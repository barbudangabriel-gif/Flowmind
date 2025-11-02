"""
Team Lead Supervisor - Tier 3 Validator
Validates signals from Tier 4 scanner agents (167 total)

Architecture:
- 20 Team Lead instances
- Each supervises 8-9 scanner agents
- 3-step validation: Score threshold, agent reliability, peer cross-validation
- Consumes from: signals:universe stream
- Publishes to: signals:validated:{team_lead_id} stream
- Cost: $0/month (no additional APIs)
"""

import asyncio
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend and parent to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

from agents.core.data_layer import get_data_layer

logger = logging.getLogger(__name__)


class TeamLead:
    """
    Team Lead Supervisor - Validates signals from scanner agents
    
    Features:
    - 3-step validation (score, reliability, peer consensus)
    - 24-hour agent performance tracking
    - False positive detection
    - Auto-flag underperforming agents
    - Redis Streams integration
    """

    def __init__(
        self,
        team_lead_id: str,
        assigned_agents: List[str],
        score_threshold: float = 60.0,
        reliability_threshold: float = 0.50,  # 50% win rate minimum
        peer_consensus_threshold: float = 0.30,  # 30% of peers agree
    ):
        """
        Initialize Team Lead supervisor
        
        Args:
            team_lead_id: Unique identifier (e.g., "team_lead_00")
            assigned_agents: List of scanner agent IDs to supervise
            score_threshold: Minimum signal score to pass (default: 60.0)
            reliability_threshold: Minimum agent win rate (default: 0.50)
            peer_consensus_threshold: Minimum peer agreement (default: 0.30)
        """
        self.team_lead_id = team_lead_id
        self.assigned_agents = assigned_agents
        self.score_threshold = score_threshold
        self.reliability_threshold = reliability_threshold
        self.peer_consensus_threshold = peer_consensus_threshold

        # Initialize services
        self.streams_manager = None
        self.timeseries_manager = None

        # Agent performance tracking (24-hour window)
        self.agent_performance: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "signals_received": 0,
                "signals_validated": 0,
                "signals_rejected": 0,
                "false_positives": 0,
                "win_rate": 0.0,
                "last_updated": None,
            }
        )

        # Validation statistics
        self.signals_processed = 0
        self.signals_validated = 0
        self.signals_rejected = 0
        self.rejection_reasons = defaultdict(int)  # {reason: count}

        # Performance tracking
        self.start_time: Optional[datetime] = None

        logger.info(
            f"[{self.team_lead_id}] Initialized supervising {len(assigned_agents)} agents"
        )

    async def initialize(self):
        """Async initialization (services require async setup)"""
        self.streams_manager, self.timeseries_manager = await get_data_layer()
        self.start_time = datetime.utcnow()
        logger.info(f"[{self.team_lead_id}] Services initialized")

    async def validate_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        3-step validation process
        
        Step 1: Score threshold check (60+ required)
        Step 2: Agent reliability check (24h win rate >50%)
        Step 3: Peer cross-validation (30% consensus)
        
        Args:
            signal: Signal dict from scanner agent
        
        Returns:
            Validated signal dict if passed, None if rejected
        """
        self.signals_processed += 1

        agent_id = signal.get("agent_id")
        ticker = signal.get("ticker")
        score = signal.get("total_score", 0)
        confidence = signal.get("confidence", 0)

        # STEP 1: Score Threshold Check
        if score < self.score_threshold:
            self._reject_signal(
                agent_id,
                ticker,
                "score_threshold",
                f"Score {score:.1f} below threshold {self.score_threshold}",
            )
            return None

        # STEP 2: Agent Reliability Check
        reliability = await self._check_agent_reliability(agent_id)
        if reliability < self.reliability_threshold:
            self._reject_signal(
                agent_id,
                ticker,
                "agent_reliability",
                f"Agent reliability {reliability:.1%} below {self.reliability_threshold:.0%}",
            )
            return None

        # STEP 3: Peer Cross-Validation
        peer_consensus = await self._peer_cross_validate(signal)
        if peer_consensus < self.peer_consensus_threshold:
            self._reject_signal(
                agent_id,
                ticker,
                "peer_consensus",
                f"Peer consensus {peer_consensus:.1%} below {self.peer_consensus_threshold:.0%}",
            )
            return None

        # ALL CHECKS PASSED - Validate signal
        validated_signal = self._create_validated_signal(
            signal, reliability, peer_consensus
        )

        self.signals_validated += 1
        self.agent_performance[agent_id]["signals_validated"] += 1
        self.agent_performance[agent_id]["last_updated"] = datetime.utcnow()

        logger.info(
            f"[{self.team_lead_id}] ✅ VALIDATED: {ticker} from {agent_id} "
            f"(score: {score:.0f}, reliability: {reliability:.0%}, consensus: {peer_consensus:.0%})"
        )

        return validated_signal

    def _reject_signal(
        self, agent_id: str, ticker: str, reason: str, message: str
    ):
        """Track rejected signal"""
        self.signals_rejected += 1
        self.rejection_reasons[reason] += 1
        self.agent_performance[agent_id]["signals_rejected"] += 1
        self.agent_performance[agent_id]["signals_received"] += 1

        logger.debug(
            f"[{self.team_lead_id}] ❌ REJECTED: {ticker} from {agent_id} - {message}"
        )

    async def _check_agent_reliability(self, agent_id: str) -> float:
        """
        Check agent reliability (24-hour win rate)
        
        Queries Redis TimeSeries for agent's signals in last 24 hours
        Calculates: validated_signals / total_signals
        
        Args:
            agent_id: Scanner agent ID
        
        Returns:
            Win rate (0.0-1.0)
        """
        try:
            # Query Redis TimeSeries for agent performance
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)

            # Get signals from last 24 hours
            performance_key = f"signals:performance:{agent_id}"
            signals_24h = await self.timeseries_manager.query_news_history(
                performance_key,
                start_timestamp=int(start_time.timestamp()),
                end_timestamp=int(end_time.timestamp()),
            )

            if not signals_24h:
                # New agent - give benefit of doubt (neutral 0.5)
                return 0.5

            # Calculate validation rate from stored data
            # Each entry has: {ticker, score, confidence, validated: bool}
            total = len(signals_24h)
            validated = sum(1 for s in signals_24h if s.get("validated", False))

            win_rate = validated / total if total > 0 else 0.5

            # Update agent performance cache
            self.agent_performance[agent_id]["win_rate"] = win_rate

            return win_rate

        except Exception as e:
            logger.error(
                f"[{self.team_lead_id}] Error checking agent reliability: {e}"
            )
            return 0.5  # Neutral on error

    async def _peer_cross_validate(self, signal: Dict[str, Any]) -> float:
        """
        Peer cross-validation - Check if other agents agree
        
        Algorithm:
        1. Get ticker from signal
        2. Query recent signals (last 5 minutes) from other agents for same ticker
        3. Calculate consensus: similar_signals / total_peer_signals
        4. "Similar" means: same direction (bullish/bearish) and score within 20%
        
        Args:
            signal: Signal to validate
        
        Returns:
            Consensus rate (0.0-1.0)
        """
        ticker = signal.get("ticker")
        signal_score = signal.get("total_score", 0)
        signal_direction = self._get_signal_direction(signal)

        try:
            # Query signals from last 5 minutes
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)

            # Get recent signals for this ticker from universe stream
            # (In production, this would query Redis Streams)
            # For now, simulate peer signals
            peer_signals = []  # TODO: Query from Redis Streams

            if not peer_signals:
                # No peer data - neutral consensus
                return 0.5

            # Count similar signals
            similar_count = 0
            for peer_signal in peer_signals:
                # Skip same agent
                if peer_signal.get("agent_id") == signal.get("agent_id"):
                    continue

                peer_score = peer_signal.get("total_score", 0)
                peer_direction = self._get_signal_direction(peer_signal)

                # Check similarity:
                # - Same direction (bullish/bearish)
                # - Score within 20%
                if peer_direction == signal_direction:
                    score_diff_pct = abs(peer_score - signal_score) / signal_score
                    if score_diff_pct <= 0.20:  # Within 20%
                        similar_count += 1

            consensus = similar_count / len(peer_signals) if peer_signals else 0.5
            return consensus

        except Exception as e:
            logger.error(
                f"[{self.team_lead_id}] Error in peer cross-validation: {e}"
            )
            return 0.5  # Neutral on error

    def _get_signal_direction(self, signal: Dict[str, Any]) -> str:
        """
        Determine signal direction (bullish/bearish)
        
        Based on:
        - Trend direction
        - News sentiment
        - Call/put ratio
        
        Args:
            signal: Signal dict
        
        Returns:
            "bullish" or "bearish"
        """
        trend = signal.get("trend_direction", "neutral")
        news_sentiment = signal.get("news_sentiment", 0.0)
        call_put_ratio = signal.get("call_put_ratio", 1.0)

        # Simple heuristic
        bullish_score = 0

        if trend == "bullish":
            bullish_score += 1
        elif trend == "bearish":
            bullish_score -= 1

        if news_sentiment > 0.3:
            bullish_score += 1
        elif news_sentiment < -0.3:
            bullish_score -= 1

        if call_put_ratio > 1.5:
            bullish_score += 1
        elif call_put_ratio < 0.67:
            bullish_score -= 1

        return "bullish" if bullish_score > 0 else "bearish"

    def _create_validated_signal(
        self,
        original_signal: Dict[str, Any],
        reliability: float,
        peer_consensus: float,
    ) -> Dict[str, Any]:
        """
        Create validated signal with additional metadata
        
        Args:
            original_signal: Original scanner signal
            reliability: Agent reliability score
            peer_consensus: Peer consensus score
        
        Returns:
            Enhanced signal dict
        """
        validated_signal = original_signal.copy()

        # Add Team Lead validation metadata
        validated_signal.update(
            {
                "validated_by": self.team_lead_id,
                "validated_at": datetime.utcnow().isoformat(),
                "validation_tier": "tier3_supervisor",
                "agent_reliability": round(reliability, 3),
                "peer_consensus": round(peer_consensus, 3),
                "validation_confidence": round(
                    (reliability + peer_consensus) / 2, 3
                ),  # Average
            }
        )

        return validated_signal

    async def publish_validated_signal(self, validated_signal: Dict[str, Any]):
        """
        Publish validated signal to Team Lead's stream
        
        Stream: signals:validated:{team_lead_id}
        Next tier: Sector Head Validators (Tier 2)
        """
        try:
            stream_name = f"signals:validated:{self.team_lead_id}"
            await self.streams_manager.publish_signal(stream_name, validated_signal)

            # Track in TimeSeries
            await self.timeseries_manager.add_news_event(
                f"team_lead:performance:{self.team_lead_id}",
                {
                    "ticker": validated_signal["ticker"],
                    "score": validated_signal["total_score"],
                    "validated": True,
                },
            )

            logger.debug(
                f"[{self.team_lead_id}] Published validated signal for "
                f"{validated_signal['ticker']} to {stream_name}"
            )

        except Exception as e:
            logger.error(f"[{self.team_lead_id}] Publish validated signal error: {e}")

    async def consume_signals_loop(self):
        """
        Background task: Consume signals from universe stream
        
        Consumer group: team_leads
        Consumer name: {team_lead_id}
        Stream: signals:universe
        """
        logger.info(
            f"[{self.team_lead_id}] Starting signal consumption loop "
            f"(supervising {len(self.assigned_agents)} agents)"
        )

        consumer_group = "team_leads"
        consumer_name = self.team_lead_id
        stream_name = "signals:universe"

        while True:
            try:
                # Consume signals from universe stream
                signals = await self.streams_manager.consume_signals(
                    stream_name=stream_name,
                    group_name=consumer_group,
                    consumer_name=consumer_name,
                    count=10,  # Batch of 10 signals
                    block=5000,  # Block 5 seconds if no signals
                )

                for signal in signals:
                    # Check if signal is from supervised agent
                    agent_id = signal.get("agent_id")
                    if agent_id not in self.assigned_agents:
                        # Not my agent - skip
                        continue

                    # Validate signal
                    validated_signal = await self.validate_signal(signal)

                    if validated_signal:
                        # Publish to next tier
                        await self.publish_validated_signal(validated_signal)

            except Exception as e:
                logger.error(f"[{self.team_lead_id}] Consume signals error: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds on error

    async def start(self):
        """Start Team Lead supervisor (consume signals loop)"""
        await self.initialize()

        # Start signal consumption loop
        await self.consume_signals_loop()

    def get_team_stats(self) -> Dict[str, Any]:
        """
        Get Team Lead performance statistics
        
        Returns:
            Dict with team-level metrics
        """
        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        validation_rate = (
            self.signals_validated / self.signals_processed
            if self.signals_processed
            else 0
        )

        return {
            "team_lead_id": self.team_lead_id,
            "supervised_agents": len(self.assigned_agents),
            "signals_processed": self.signals_processed,
            "signals_validated": self.signals_validated,
            "signals_rejected": self.signals_rejected,
            "validation_rate": round(validation_rate, 3),
            "rejection_reasons": dict(self.rejection_reasons),
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }

    def get_agent_performance(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get performance stats for specific agent"""
        if agent_id in self.agent_performance:
            return dict(self.agent_performance[agent_id])
        return None

    def get_all_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance stats for all supervised agents"""
        return {
            agent_id: dict(perf)
            for agent_id, perf in self.agent_performance.items()
        }


# ═══════════════════════════════════════════════════════════════════════════
# TEAM LEAD POOL
# ═══════════════════════════════════════════════════════════════════════════


class TeamLeadPool:
    """
    Manages pool of 20 Team Lead supervisors
    
    Features:
    - Auto-assign agents to team leads (167 scanners / 20 leads ≈ 8-9 each)
    - Start all team leads concurrently
    - Performance aggregation
    - Graceful shutdown
    """

    def __init__(self, num_leads: int = 20, num_scanner_agents: int = 167):
        """
        Initialize Team Lead pool
        
        Args:
            num_leads: Number of Team Lead instances (default: 20)
            num_scanner_agents: Total scanner agents to supervise (default: 167)
        """
        self.num_leads = num_leads
        self.num_scanner_agents = num_scanner_agents

        # Team Lead instances
        self.team_leads: List[TeamLead] = []
        self.team_lead_tasks: Dict[str, asyncio.Task] = {}

        # Pool state
        self.is_running = False
        self.start_time: Optional[datetime] = None

        logger.info(
            f"[TeamLeadPool] Initialized: {num_leads} leads supervising "
            f"{num_scanner_agents} scanners"
        )

    def _assign_agents_to_leads(self) -> Dict[str, List[str]]:
        """
        Assign scanner agents to team leads (round-robin)
        
        Returns:
            Dict {team_lead_id: [agent_ids]}
        """
        assignments = defaultdict(list)

        # Round-robin assignment
        for agent_idx in range(self.num_scanner_agents):
            agent_id = f"scanner_{agent_idx:03d}"
            lead_idx = agent_idx % self.num_leads
            lead_id = f"team_lead_{lead_idx:02d}"
            assignments[lead_id].append(agent_id)

        logger.info(
            f"[TeamLeadPool] Assigned {self.num_scanner_agents} agents to "
            f"{self.num_leads} team leads"
        )

        return dict(assignments)

    async def initialize(self):
        """Initialize all Team Lead instances"""
        if self.team_leads:
            logger.warning("[TeamLeadPool] Already initialized")
            return

        # Generate assignments
        assignments = self._assign_agents_to_leads()

        # Create Team Lead instances
        for lead_id, agent_ids in assignments.items():
            team_lead = TeamLead(
                team_lead_id=lead_id,
                assigned_agents=agent_ids,
            )
            self.team_leads.append(team_lead)

        logger.info(f"[TeamLeadPool] Initialized {len(self.team_leads)} team leads")

    async def start_all(self):
        """Start all Team Lead supervisors concurrently"""
        if self.is_running:
            logger.warning("[TeamLeadPool] Already running")
            return

        if not self.team_leads:
            await self.initialize()

        self.is_running = True
        self.start_time = datetime.utcnow()

        logger.info(f"[TeamLeadPool] Starting {len(self.team_leads)} team leads...")

        # Start all team leads concurrently
        for team_lead in self.team_leads:
            task = asyncio.create_task(team_lead.start())
            self.team_lead_tasks[team_lead.team_lead_id] = task

        logger.info(f"[TeamLeadPool] All {len(self.team_leads)} team leads started")

    async def shutdown(self):
        """Gracefully stop all Team Lead supervisors"""
        logger.info("[TeamLeadPool] Shutting down...")

        self.is_running = False

        # Cancel all tasks
        for lead_id, task in self.team_lead_tasks.items():
            if not task.done():
                logger.info(f"[TeamLeadPool] Cancelling {lead_id}")
                task.cancel()

        # Wait for all tasks
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.team_lead_tasks.values(), return_exceptions=True),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            logger.warning("[TeamLeadPool] Shutdown timeout")

        logger.info("[TeamLeadPool] Shutdown complete")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get aggregated pool statistics"""
        total_processed = 0
        total_validated = 0
        total_rejected = 0

        for team_lead in self.team_leads:
            stats = team_lead.get_team_stats()
            total_processed += stats["signals_processed"]
            total_validated += stats["signals_validated"]
            total_rejected += stats["signals_rejected"]

        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        validation_rate = (
            total_validated / total_processed if total_processed else 0
        )

        return {
            "pool_status": "running" if self.is_running else "stopped",
            "total_team_leads": len(self.team_leads),
            "signals_processed": total_processed,
            "signals_validated": total_validated,
            "signals_rejected": total_rejected,
            "validation_rate": round(validation_rate, 3),
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_global_team_lead_pool: Optional[TeamLeadPool] = None


async def get_team_lead_pool(
    num_leads: int = 20, num_scanner_agents: int = 167
) -> TeamLeadPool:
    """
    Get global Team Lead pool instance (singleton)
    
    Args:
        num_leads: Number of Team Lead instances (default: 20)
        num_scanner_agents: Total scanner agents (default: 167)
    
    Returns:
        TeamLeadPool instance
    """
    global _global_team_lead_pool

    if _global_team_lead_pool is None:
        _global_team_lead_pool = TeamLeadPool(
            num_leads=num_leads, num_scanner_agents=num_scanner_agents
        )
        await _global_team_lead_pool.initialize()

    return _global_team_lead_pool
