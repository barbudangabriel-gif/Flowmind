"""
Master Director - Tier 1 Final Authority
Single instance with GPT-4o LLM reasoning for final trade decisions

Architecture:
- 1 MasterDirector instance (top of hierarchy)
- Supervises 10 Sector Heads
- GPT-4o integration for context-aware reasoning
- Multi-factor analysis: portfolio, risk, regime, news
- Consumes from: signals:approved:{sector_head_id} streams
- Publishes to: signals:final stream (for execution)
- Cost: ~$10-20/month (OpenAI GPT-4o API)
"""

import asyncio
import json
import logging
import os
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

# OpenAI API configuration
try:
    import openai

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        GPT4O_AVAILABLE = True
    else:
        GPT4O_AVAILABLE = False
        logger.warning("OPENAI_API_KEY not set - Master Director will use fallback logic")
except ImportError:
    GPT4O_AVAILABLE = False
    logger.warning("openai package not installed - Master Director will use fallback logic")


class MasterDirector:
    """
    Master Director - Final decision authority with GPT-4o reasoning
    
    Features:
    - GPT-4o LLM integration for context-aware decisions
    - Multi-factor analysis (portfolio, risk, regime, news)
    - Decision tracking with explanations
    - Confidence scoring (0-100)
    - Execution signal generation
    """

    def __init__(
        self,
        director_id: str = "master_director",
        supervised_sector_heads: Optional[List[str]] = None,
        use_llm: bool = True,
        confidence_threshold: float = 70.0,
    ):
        """
        Initialize Master Director
        
        Args:
            director_id: Unique identifier (default: "master_director")
            supervised_sector_heads: List of sector head IDs (default: all 10)
            use_llm: Use GPT-4o for reasoning (default: True, fallback if unavailable)
            confidence_threshold: Minimum confidence to execute (default: 70.0)
        """
        self.director_id = director_id
        self.supervised_sector_heads = supervised_sector_heads or [
            f"sector_head_{sector}"
            for sector in [
                "technology",
                "financials",
                "healthcare",
                "consumer",
                "energy",
                "industrials",
                "materials",
                "utilities",
                "real_estate",
                "communications",
            ]
        ]
        self.use_llm = use_llm and GPT4O_AVAILABLE
        self.confidence_threshold = confidence_threshold

        # Initialize services
        self.streams_manager = None
        self.timeseries_manager = None

        # Portfolio state (simulated - in production, fetch from Redis)
        self.current_portfolio: Dict[str, Dict[str, Any]] = {}  # {ticker: {value, sector, ...}}
        self.total_portfolio_value = 100000.0  # Starting capital
        self.available_cash = 100000.0

        # Market regime tracking
        self.market_regime = "neutral"  # "bull", "bear", "neutral"
        self.market_volatility = 0.20  # VIX equivalent

        # Decision statistics
        self.signals_processed = 0
        self.signals_approved = 0
        self.signals_rejected = 0
        self.rejection_reasons = defaultdict(int)  # {reason: count}
        self.decisions: List[Dict[str, Any]] = []  # Decision history

        # Performance tracking
        self.start_time: Optional[datetime] = None

        logger.info(
            f"[{self.director_id}] Initialized with {'GPT-4o' if self.use_llm else 'fallback logic'} "
            f"supervising {len(self.supervised_sector_heads)} sector heads"
        )

    async def initialize(self):
        """Async initialization (services require async setup)"""
        self.streams_manager, self.timeseries_manager = await get_data_layer()
        self.start_time = datetime.utcnow()
        logger.info(f"[{self.director_id}] Services initialized")

    async def make_decision(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Final decision with GPT-4o reasoning
        
        Process:
        1. Gather full context (portfolio, news, market regime)
        2. Call GPT-4o with structured prompt
        3. Parse LLM response (approve/reject + reasoning)
        4. Validate decision (confidence threshold)
        5. Generate execution signal if approved
        
        Args:
            signal: Approved signal from Sector Head
        
        Returns:
            Execution signal dict if approved, None if rejected
        """
        self.signals_processed += 1

        ticker = signal.get("ticker")
        sector = signal.get("sector")
        score = signal.get("total_score", 0)
        sector_risk = signal.get("sector_risk_score", 0)

        # STEP 1: Gather context
        context = await self._gather_decision_context(signal)

        # STEP 2: Make decision (LLM or fallback)
        if self.use_llm:
            decision_result = await self._llm_decision(signal, context)
        else:
            decision_result = await self._fallback_decision(signal, context)

        # STEP 3: Validate confidence
        confidence = decision_result.get("confidence", 0)
        approved = decision_result.get("approved", False)
        reasoning = decision_result.get("reasoning", "")

        if not approved or confidence < self.confidence_threshold:
            self._reject_signal(
                ticker,
                "director_rejection",
                f"Director rejected (confidence: {confidence:.0f}%, threshold: {self.confidence_threshold:.0f}%)",
            )
            
            # Store decision
            self.decisions.append({
                "timestamp": datetime.utcnow().isoformat(),
                "ticker": ticker,
                "approved": False,
                "confidence": confidence,
                "reasoning": reasoning,
            })
            
            return None

        # STEP 4: Generate execution signal
        execution_signal = self._create_execution_signal(signal, decision_result)

        self.signals_approved += 1

        # Store decision
        self.decisions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "ticker": ticker,
            "approved": True,
            "confidence": confidence,
            "reasoning": reasoning,
        })

        logger.info(
            f"[{self.director_id}] ✅ APPROVED: {ticker} "
            f"(confidence: {confidence:.0f}%, sector: {sector})"
        )

        return execution_signal

    def _reject_signal(self, ticker: str, reason: str, message: str):
        """Track rejected signal"""
        self.signals_rejected += 1
        self.rejection_reasons[reason] += 1

        logger.debug(f"[{self.director_id}] ❌ REJECTED: {ticker} - {message}")

    async def _gather_decision_context(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather full context for decision making
        
        Returns:
            Dict with portfolio, market regime, news, risk metrics
        """
        ticker = signal.get("ticker")
        sector = signal.get("sector")

        # Portfolio context
        portfolio_exposure = sum(
            pos.get("value", 0) for pos in self.current_portfolio.values()
        ) / self.total_portfolio_value if self.current_portfolio else 0.0

        sector_positions = [
            t for t, pos in self.current_portfolio.items()
            if pos.get("sector") == sector
        ]

        # Risk metrics
        portfolio_risk = await self._calculate_portfolio_risk()

        # News context (fetch recent news for ticker)
        recent_news = await self._fetch_recent_news(ticker)

        return {
            "portfolio": {
                "total_value": self.total_portfolio_value,
                "cash_available": self.available_cash,
                "positions_count": len(self.current_portfolio),
                "portfolio_exposure": portfolio_exposure,
                "sector_positions": sector_positions,
            },
            "market": {
                "regime": self.market_regime,
                "volatility": self.market_volatility,
            },
            "risk": {
                "portfolio_risk": portfolio_risk,
                "max_position_size": self.total_portfolio_value * 0.10,  # 10% max
            },
            "news": recent_news,
        }

    async def _llm_decision(
        self, signal: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use GPT-4o for decision making
        
        Prompt structure:
        - Signal details (ticker, score, sector, risk)
        - Portfolio context (positions, exposure, cash)
        - Market regime (bull/bear/neutral, volatility)
        - Recent news (sentiment, impact)
        - Risk metrics (portfolio risk, position sizing)
        
        Args:
            signal: Approved signal from Sector Head
            context: Full decision context
        
        Returns:
            Dict with approved (bool), confidence (0-100), reasoning (str)
        """
        ticker = signal.get("ticker")
        sector = signal.get("sector")
        score = signal.get("total_score", 0)
        sector_risk = signal.get("sector_risk_score", 0)

        # Build LLM prompt
        prompt = self._build_llm_prompt(signal, context)

        try:
            # Call GPT-4o
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading director making final decisions on trade execution. "
                        "Analyze all provided context and decide whether to execute the trade. "
                        "Respond in JSON format: {\"approved\": bool, \"confidence\": 0-100, \"reasoning\": str}"
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for consistent decisions
                max_tokens=300,
            )

            # Parse response
            llm_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if llm_text.startswith("```json"):
                llm_text = llm_text.split("```json")[1].split("```")[0].strip()
            elif llm_text.startswith("```"):
                llm_text = llm_text.split("```")[1].split("```")[0].strip()

            decision = json.loads(llm_text)

            return {
                "approved": decision.get("approved", False),
                "confidence": float(decision.get("confidence", 0)),
                "reasoning": decision.get("reasoning", "No reasoning provided"),
                "llm_model": "gpt-4o",
            }

        except Exception as e:
            logger.error(f"[{self.director_id}] GPT-4o error: {e}, falling back to rule-based")
            return await self._fallback_decision(signal, context)

    def _build_llm_prompt(self, signal: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build structured prompt for GPT-4o"""
        ticker = signal.get("ticker")
        sector = signal.get("sector")
        score = signal.get("total_score", 0)
        sector_risk = signal.get("sector_risk_score", 0)
        validation_confidence = signal.get("validation_confidence", 0)

        prompt = f"""Trade Decision Analysis

SIGNAL DETAILS:
- Ticker: {ticker}
- Sector: {sector}
- Signal Score: {score:.0f}/100
- Sector Risk: {sector_risk:.0f}/100
- Validation Confidence: {validation_confidence:.0%}

PORTFOLIO CONTEXT:
- Total Value: ${context['portfolio']['total_value']:,.0f}
- Cash Available: ${context['portfolio']['cash_available']:,.0f}
- Positions: {context['portfolio']['positions_count']}
- Portfolio Exposure: {context['portfolio']['portfolio_exposure']:.0%}
- Sector Positions: {len(context['portfolio']['sector_positions'])} in {sector}

MARKET REGIME:
- Regime: {context['market']['regime']}
- Volatility: {context['market']['volatility']:.1%}

RISK METRICS:
- Portfolio Risk: {context['risk']['portfolio_risk']:.1f}/100
- Max Position Size: ${context['risk']['max_position_size']:,.0f}

RECENT NEWS:
{self._format_news_for_prompt(context['news'])}

DECISION REQUIRED:
Should we execute this trade? Consider:
1. Signal quality (score, validation confidence)
2. Portfolio diversification (sector exposure)
3. Market regime (favorable conditions?)
4. Risk management (portfolio risk, position sizing)
5. News impact (positive/negative sentiment)

Respond in JSON format:
{{
  "approved": true/false,
  "confidence": 0-100,
  "reasoning": "Brief explanation (1-2 sentences)"
}}
"""
        return prompt

    def _format_news_for_prompt(self, news: List[Dict[str, Any]]) -> str:
        """Format news items for LLM prompt"""
        if not news:
            return "No recent news available"

        formatted = []
        for item in news[:3]:  # Top 3 news items
            formatted.append(
                f"- {item.get('title', 'N/A')} (sentiment: {item.get('sentiment', 0):.2f})"
            )

        return "\n".join(formatted)

    async def _fallback_decision(
        self, signal: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rule-based fallback decision (when GPT-4o unavailable)
        
        Rules:
        1. Score >= 70 → High confidence
        2. Score 60-69 → Medium confidence (check portfolio)
        3. Score < 60 → Reject
        4. Portfolio exposure > 80% → Reject (fully invested)
        5. Sector has 3+ positions → Reduce confidence
        6. High portfolio risk (>70) → Reduce confidence
        
        Args:
            signal: Approved signal
            context: Decision context
        
        Returns:
            Dict with approved, confidence, reasoning
        """
        ticker = signal.get("ticker")
        sector = signal.get("sector")
        score = signal.get("total_score", 0)
        sector_risk = signal.get("sector_risk_score", 0)

        confidence = 0.0
        reasoning = ""
        approved = False

        # Rule 1: Base confidence from signal score
        if score >= 70:
            confidence = 85.0
            reasoning = "High signal score"
        elif score >= 60:
            confidence = 70.0
            reasoning = "Medium signal score"
        else:
            confidence = 50.0
            reasoning = "Low signal score"

        # Rule 2: Portfolio exposure check
        portfolio_exposure = context["portfolio"]["portfolio_exposure"]
        if portfolio_exposure > 0.80:
            confidence -= 20
            reasoning += ", high portfolio exposure"

        # Rule 3: Sector concentration
        sector_positions = len(context["portfolio"]["sector_positions"])
        if sector_positions >= 3:
            confidence -= 15
            reasoning += ", sector overconcentrated"

        # Rule 4: Portfolio risk
        portfolio_risk = context["risk"]["portfolio_risk"]
        if portfolio_risk > 70:
            confidence -= 10
            reasoning += ", high portfolio risk"

        # Rule 5: Market regime
        if context["market"]["regime"] == "bear" and confidence < 75:
            confidence -= 10
            reasoning += ", bearish regime"
        elif context["market"]["regime"] == "bull":
            confidence += 5
            reasoning += ", bullish regime"

        # Final decision
        confidence = max(0, min(100, confidence))  # Clamp 0-100
        approved = confidence >= self.confidence_threshold

        return {
            "approved": approved,
            "confidence": confidence,
            "reasoning": reasoning.strip(", "),
            "llm_model": "fallback",
        }

    async def _calculate_portfolio_risk(self) -> float:
        """
        Calculate overall portfolio risk (0-100)
        
        Factors:
        - Concentration (single position > 15%)
        - Sector correlation
        - Volatility
        - Leverage
        
        Returns:
            Risk score (0-100, higher = riskier)
        """
        if not self.current_portfolio:
            return 0.0

        risk_score = 0.0

        # Factor 1: Concentration (0-40 points)
        max_position_pct = max(
            (pos.get("value", 0) / self.total_portfolio_value)
            for pos in self.current_portfolio.values()
        )
        if max_position_pct > 0.15:
            risk_score += (max_position_pct - 0.15) * 200  # Penalty for large positions

        # Factor 2: Sector correlation (0-30 points)
        sector_counts = defaultdict(int)
        for pos in self.current_portfolio.values():
            sector_counts[pos.get("sector")] += 1

        max_sector_count = max(sector_counts.values()) if sector_counts else 0
        if max_sector_count > 3:
            risk_score += (max_sector_count - 3) * 10

        # Factor 3: Market volatility (0-30 points)
        risk_score += self.market_volatility * 100  # 0.20 → 20 points

        return min(risk_score, 100.0)

    async def _fetch_recent_news(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetch recent news for ticker (last 24h)
        
        Args:
            ticker: Stock ticker
        
        Returns:
            List of news items with sentiment
        """
        try:
            # Query TimeSeries for recent news
            # In production, this would fetch from NewsAggregator
            # For now, return placeholder
            return [
                {
                    "title": f"{ticker} quarterly earnings beat expectations",
                    "sentiment": 0.65,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ]
        except Exception as e:
            logger.error(f"[{self.director_id}] Fetch news error: {e}")
            return []

    def _create_execution_signal(
        self, original_signal: Dict[str, Any], decision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create final execution signal with director approval
        
        Args:
            original_signal: Approved signal from Sector Head
            decision_result: Director decision with reasoning
        
        Returns:
            Execution signal dict
        """
        execution_signal = original_signal.copy()

        # Add Director decision metadata
        execution_signal.update({
            "director_approved": True,
            "director_id": self.director_id,
            "director_confidence": round(decision_result["confidence"], 1),
            "director_reasoning": decision_result["reasoning"],
            "llm_model": decision_result.get("llm_model", "fallback"),
            "approved_at": datetime.utcnow().isoformat(),
            "execution_tier": "tier1_director",
            
            # Position sizing (10% of portfolio)
            "position_size": round(self.total_portfolio_value * 0.10, 2),
            "max_loss": round(self.total_portfolio_value * 0.02, 2),  # 2% risk per trade
        })

        return execution_signal

    async def publish_execution_signal(self, execution_signal: Dict[str, Any]):
        """
        Publish final execution signal
        
        Stream: signals:final (single stream for execution engine)
        """
        try:
            stream_name = "signals:final"
            await self.streams_manager.publish_signal(stream_name, execution_signal)

            # Track in TimeSeries
            await self.timeseries_manager.add_news_event(
                f"director:performance:{self.director_id}",
                {
                    "ticker": execution_signal["ticker"],
                    "confidence": execution_signal["director_confidence"],
                    "executed": True,
                },
            )

            logger.info(
                f"[{self.director_id}] Published execution signal for "
                f"{execution_signal['ticker']} to {stream_name}"
            )

        except Exception as e:
            logger.error(f"[{self.director_id}] Publish execution signal error: {e}")

    async def consume_signals_loop(self):
        """
        Background task: Consume signals from all sector heads
        
        Consumer group: master_director
        Consumer name: master_director
        Streams: signals:approved:{sector_head_id} (10 streams)
        """
        logger.info(
            f"[{self.director_id}] Starting signal consumption loop "
            f"(supervising {len(self.supervised_sector_heads)} sector heads)"
        )

        consumer_group = "master_director"
        consumer_name = self.director_id

        while True:
            try:
                # Consume from each sector head's stream
                for sector_head_id in self.supervised_sector_heads:
                    stream_name = f"signals:approved:{sector_head_id}"

                    signals = await self.streams_manager.consume_signals(
                        stream_name=stream_name,
                        group_name=consumer_group,
                        consumer_name=consumer_name,
                        count=3,  # Batch of 3 signals
                        block=1000,  # Block 1 second if no signals
                    )

                    for signal in signals:
                        # Make final decision
                        execution_signal = await self.make_decision(signal)

                        if execution_signal:
                            # Publish to execution engine
                            await self.publish_execution_signal(execution_signal)

                # Small delay between stream checks
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"[{self.director_id}] Consume signals error: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds on error

    async def start(self):
        """Start Master Director (consume signals loop)"""
        await self.initialize()

        # Start signal consumption loop
        await self.consume_signals_loop()

    def get_director_stats(self) -> Dict[str, Any]:
        """
        Get Master Director performance statistics
        
        Returns:
            Dict with director-level metrics
        """
        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        approval_rate = (
            self.signals_approved / self.signals_processed
            if self.signals_processed
            else 0
        )

        return {
            "director_id": self.director_id,
            "llm_enabled": self.use_llm,
            "llm_model": "gpt-4o" if self.use_llm else "fallback",
            "supervised_sector_heads": len(self.supervised_sector_heads),
            "signals_processed": self.signals_processed,
            "signals_approved": self.signals_approved,
            "signals_rejected": self.signals_rejected,
            "approval_rate": round(approval_rate, 3),
            "confidence_threshold": self.confidence_threshold,
            "rejection_reasons": dict(self.rejection_reasons),
            "recent_decisions": self.decisions[-10:],  # Last 10 decisions
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_global_master_director: Optional[MasterDirector] = None


async def get_master_director(
    use_llm: bool = True, confidence_threshold: float = 70.0
) -> MasterDirector:
    """
    Get global Master Director instance (singleton)
    
    Args:
        use_llm: Use GPT-4o for reasoning (default: True)
        confidence_threshold: Minimum confidence to execute (default: 70.0)
    
    Returns:
        MasterDirector instance
    """
    global _global_master_director

    if _global_master_director is None:
        _global_master_director = MasterDirector(
            use_llm=use_llm, confidence_threshold=confidence_threshold
        )
        await _global_master_director.initialize()

    return _global_master_director
