"""
Sector Head Validator - Tier 2 Validator
Validates signals from Tier 3 Team Leads (20 total)

Architecture:
- 10 Sector Head instances
- Each supervises 2 team leads
- Sector-specific validation: exposure limits, correlation checks, risk scoring
- Consumes from: signals:validated:{team_lead_id} streams
- Publishes to: signals:approved:{sector_head_id} stream
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


# ═══════════════════════════════════════════════════════════════════════════
# SECTOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

SECTORS = {
    "technology": {
        "name": "Technology",
        "exposure_limit": 0.30,  # Max 30% portfolio exposure
        "tickers": [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "NVDA",
            "TSM",
            "AVGO",
            "ORCL",
            "CSCO",
        ],
    },
    "financials": {
        "name": "Financials",
        "exposure_limit": 0.30,
        "tickers": ["JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SCHW", "USB"],
    },
    "healthcare": {
        "name": "Healthcare",
        "exposure_limit": 0.30,
        "tickers": [
            "UNH",
            "JNJ",
            "LLY",
            "ABBV",
            "MRK",
            "TMO",
            "ABT",
            "PFE",
            "DHR",
            "BMY",
        ],
    },
    "consumer": {
        "name": "Consumer",
        "exposure_limit": 0.30,
        "tickers": [
            "TSLA",
            "HD",
            "WMT",
            "MCD",
            "NKE",
            "SBUX",
            "TGT",
            "LOW",
            "COST",
            "DIS",
        ],
    },
    "energy": {
        "name": "Energy",
        "exposure_limit": 0.25,  # Lower limit (more volatile)
        "tickers": [
            "XOM",
            "CVX",
            "COP",
            "SLB",
            "EOG",
            "MPC",
            "PSX",
            "VLO",
            "OXY",
            "HAL",
        ],
    },
    "industrials": {
        "name": "Industrials",
        "exposure_limit": 0.30,
        "tickers": [
            "BA",
            "CAT",
            "HON",
            "UPS",
            "RTX",
            "LMT",
            "DE",
            "GE",
            "MMM",
            "FDX",
        ],
    },
    "materials": {
        "name": "Materials",
        "exposure_limit": 0.25,
        "tickers": [
            "LIN",
            "APD",
            "SHW",
            "FCX",
            "NEM",
            "DD",
            "ECL",
            "NUE",
            "DOW",
            "PPG",
        ],
    },
    "utilities": {
        "name": "Utilities",
        "exposure_limit": 0.20,  # Lower limit (defensive)
        "tickers": [
            "NEE",
            "DUK",
            "SO",
            "D",
            "EXC",
            "AEP",
            "SRE",
            "XEL",
            "ED",
            "PEG",
        ],
    },
    "real_estate": {
        "name": "Real Estate",
        "exposure_limit": 0.20,
        "tickers": [
            "AMT",
            "PLD",
            "CCI",
            "EQIX",
            "PSA",
            "SPG",
            "O",
            "WELL",
            "DLR",
            "AVB",
        ],
    },
    "communications": {
        "name": "Communications",
        "exposure_limit": 0.30,
        "tickers": [
            "GOOGL",
            "META",
            "DIS",
            "CMCSA",
            "NFLX",
            "T",
            "VZ",
            "TMUS",
            "CHTR",
            "EA",
        ],
    },
}


class SectorHead:
    """
    Sector Head Validator - Validates signals with sector-specific rules
    
    Features:
    - Sector exposure limits (max 30% per sector)
    - Correlation checks (avoid correlated positions)
    - Sector risk scoring
    - Portfolio-level validation
    """

    def __init__(
        self,
        sector_head_id: str,
        sector_name: str,
        supervised_team_leads: List[str],
        exposure_limit: float = 0.30,
    ):
        """
        Initialize Sector Head validator
        
        Args:
            sector_head_id: Unique identifier (e.g., "sector_head_technology")
            sector_name: Sector name (e.g., "technology")
            supervised_team_leads: List of team lead IDs to supervise
            exposure_limit: Max portfolio exposure for this sector (default: 0.30)
        """
        self.sector_head_id = sector_head_id
        self.sector_name = sector_name
        self.supervised_team_leads = supervised_team_leads
        self.exposure_limit = exposure_limit

        # Get sector configuration
        self.sector_config = SECTORS.get(
            sector_name, {"name": sector_name, "exposure_limit": 0.30, "tickers": []}
        )

        # Initialize services
        self.streams_manager = None
        self.timeseries_manager = None

        # Portfolio tracking (simulated - in production, fetch from Redis)
        self.current_portfolio: Dict[str, float] = {}  # {ticker: position_value}
        self.sector_exposures: Dict[str, float] = {}  # {sector: exposure_pct}

        # Validation statistics
        self.signals_processed = 0
        self.signals_approved = 0
        self.signals_rejected = 0
        self.rejection_reasons = defaultdict(int)  # {reason: count}

        # Performance tracking
        self.start_time: Optional[datetime] = None

        logger.info(
            f"[{self.sector_head_id}] Initialized for sector '{sector_name}' "
            f"supervising {len(supervised_team_leads)} team leads"
        )

    async def initialize(self):
        """Async initialization (services require async setup)"""
        self.streams_manager, self.timeseries_manager = await get_data_layer()
        self.start_time = datetime.utcnow()
        logger.info(f"[{self.sector_head_id}] Services initialized")

    def _get_ticker_sector(self, ticker: str) -> Optional[str]:
        """
        Determine which sector a ticker belongs to
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Sector name or None if unknown
        """
        for sector_name, config in SECTORS.items():
            if ticker in config["tickers"]:
                return sector_name
        return None

    async def validate_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Sector-specific validation process
        
        Checks:
        1. Sector exposure limits (max 30% per sector)
        2. Correlation with existing positions (avoid overconcentration)
        3. Sector risk scoring (volatility, correlation)
        
        Args:
            signal: Validated signal from Team Lead
        
        Returns:
            Approved signal dict if passed, None if rejected
        """
        self.signals_processed += 1

        ticker = signal.get("ticker")
        score = signal.get("total_score", 0)
        confidence = signal.get("validation_confidence", 0)

        # Determine ticker sector
        ticker_sector = self._get_ticker_sector(ticker)

        if ticker_sector is None:
            # Unknown sector - reject
            self._reject_signal(
                ticker,
                "unknown_sector",
                f"Ticker {ticker} not found in sector definitions",
            )
            return None

        # CHECK 1: Sector Exposure Limit
        if not await self._check_exposure_limit(ticker, ticker_sector):
            return None

        # CHECK 2: Correlation Check
        if not await self._check_correlation(ticker, ticker_sector):
            return None

        # CHECK 3: Sector Risk Scoring
        sector_risk_score = await self._calculate_sector_risk(ticker, ticker_sector)
        if sector_risk_score > 80:  # High risk threshold
            self._reject_signal(
                ticker,
                "high_sector_risk",
                f"Sector risk score {sector_risk_score:.0f} exceeds threshold 80",
            )
            return None

        # ALL CHECKS PASSED - Approve signal
        approved_signal = self._create_approved_signal(signal, sector_risk_score)

        self.signals_approved += 1

        logger.info(
            f"[{self.sector_head_id}] ✅ APPROVED: {ticker} "
            f"(sector: {ticker_sector}, risk: {sector_risk_score:.0f})"
        )

        return approved_signal

    def _reject_signal(self, ticker: str, reason: str, message: str):
        """Track rejected signal"""
        self.signals_rejected += 1
        self.rejection_reasons[reason] += 1

        logger.debug(f"[{self.sector_head_id}] ❌ REJECTED: {ticker} - {message}")

    async def _check_exposure_limit(self, ticker: str, ticker_sector: str) -> bool:
        """
        Check if adding this position would exceed sector exposure limit
        
        Args:
            ticker: Stock ticker
            ticker_sector: Sector name
        
        Returns:
            True if within limit, False if rejected
        """
        # Get current sector exposure (simulated)
        current_exposure = self.sector_exposures.get(ticker_sector, 0.0)

        # Estimate new position size (assume $10k position)
        position_size = 10000.0  # TODO: Get from signal or portfolio manager

        # Calculate total portfolio value (simulated)
        total_portfolio = sum(self.current_portfolio.values()) or 100000.0

        # Calculate new exposure
        new_exposure = (
            sum(
                v
                for t, v in self.current_portfolio.items()
                if self._get_ticker_sector(t) == ticker_sector
            )
            + position_size
        ) / total_portfolio

        # Get sector limit
        sector_limit = self.sector_config.get("exposure_limit", 0.30)

        if new_exposure > sector_limit:
            self._reject_signal(
                ticker,
                "exposure_limit",
                f"Sector exposure {new_exposure:.1%} exceeds limit {sector_limit:.0%}",
            )
            return False

        return True

    async def _check_correlation(self, ticker: str, ticker_sector: str) -> bool:
        """
        Check correlation with existing positions in same sector
        
        Rejects if:
        - Already have 3+ positions in same sector
        - High correlation with existing positions (>0.7)
        
        Args:
            ticker: Stock ticker
            ticker_sector: Sector name
        
        Returns:
            True if acceptable, False if rejected
        """
        # Count positions in same sector
        sector_positions = [
            t
            for t in self.current_portfolio.keys()
            if self._get_ticker_sector(t) == ticker_sector
        ]

        if len(sector_positions) >= 3:
            self._reject_signal(
                ticker,
                "sector_concentration",
                f"Already have {len(sector_positions)} positions in {ticker_sector}",
            )
            return False

        # TODO: Add correlation calculation with historical prices
        # For now, accept if below position limit

        return True

    async def _calculate_sector_risk(self, ticker: str, ticker_sector: str) -> float:
        """
        Calculate sector risk score (0-100)
        
        Factors:
        - Sector volatility (historical)
        - Current sector exposure
        - Market regime (bull/bear)
        - Sector momentum
        
        Args:
            ticker: Stock ticker
            ticker_sector: Sector name
        
        Returns:
            Risk score (0-100, higher = riskier)
        """
        risk_score = 0.0

        # Factor 1: Sector volatility (0-30 points)
        # TODO: Fetch historical sector volatility
        sector_volatility = 0.25  # Placeholder
        risk_score += sector_volatility * 100  # 0.25 → 25 points

        # Factor 2: Current exposure (0-30 points)
        current_exposure = self.sector_exposures.get(ticker_sector, 0.0)
        risk_score += current_exposure * 100  # 0.20 → 20 points

        # Factor 3: Sector momentum (0-20 points)
        # TODO: Calculate sector momentum
        sector_momentum = 0.10  # Placeholder (positive momentum = lower risk)
        risk_score += (1 - sector_momentum) * 20  # Inverse relationship

        # Factor 4: Market regime (0-20 points)
        # TODO: Detect market regime (bull/bear)
        market_regime_risk = 0.15  # Placeholder
        risk_score += market_regime_risk * 20

        return min(risk_score, 100.0)

    def _create_approved_signal(
        self, original_signal: Dict[str, Any], sector_risk_score: float
    ) -> Dict[str, Any]:
        """
        Create approved signal with sector validation metadata
        
        Args:
            original_signal: Validated signal from Team Lead
            sector_risk_score: Calculated sector risk score
        
        Returns:
            Enhanced signal dict
        """
        approved_signal = original_signal.copy()

        ticker = original_signal.get("ticker")
        ticker_sector = self._get_ticker_sector(ticker)

        # Add Sector Head validation metadata
        approved_signal.update(
            {
                "approved_by": self.sector_head_id,
                "approved_at": datetime.utcnow().isoformat(),
                "validation_tier": "tier2_validator",
                "sector": ticker_sector,
                "sector_risk_score": round(sector_risk_score, 1),
                "sector_exposure": round(
                    self.sector_exposures.get(ticker_sector, 0.0), 3
                ),
            }
        )

        return approved_signal

    async def publish_approved_signal(self, approved_signal: Dict[str, Any]):
        """
        Publish approved signal to Sector Head's stream
        
        Stream: signals:approved:{sector_head_id}
        Next tier: Master Director (Tier 1)
        """
        try:
            stream_name = f"signals:approved:{self.sector_head_id}"
            await self.streams_manager.publish_signal(stream_name, approved_signal)

            # Track in TimeSeries
            await self.timeseries_manager.add_news_event(
                f"sector_head:performance:{self.sector_head_id}",
                {
                    "ticker": approved_signal["ticker"],
                    "score": approved_signal["total_score"],
                    "approved": True,
                },
            )

            logger.debug(
                f"[{self.sector_head_id}] Published approved signal for "
                f"{approved_signal['ticker']} to {stream_name}"
            )

        except Exception as e:
            logger.error(f"[{self.sector_head_id}] Publish approved signal error: {e}")

    async def consume_signals_loop(self):
        """
        Background task: Consume signals from supervised team leads
        
        Consumer group: sector_heads
        Consumer name: {sector_head_id}
        Streams: signals:validated:{team_lead_id} (2 streams per sector head)
        """
        logger.info(
            f"[{self.sector_head_id}] Starting signal consumption loop "
            f"(supervising {len(self.supervised_team_leads)} team leads)"
        )

        consumer_group = "sector_heads"
        consumer_name = self.sector_head_id

        while True:
            try:
                # Consume from each supervised team lead's stream
                for team_lead_id in self.supervised_team_leads:
                    stream_name = f"signals:validated:{team_lead_id}"

                    signals = await self.streams_manager.consume_signals(
                        stream_name=stream_name,
                        group_name=consumer_group,
                        consumer_name=consumer_name,
                        count=5,  # Batch of 5 signals
                        block=1000,  # Block 1 second if no signals
                    )

                    for signal in signals:
                        # Validate signal
                        approved_signal = await self.validate_signal(signal)

                        if approved_signal:
                            # Publish to next tier
                            await self.publish_approved_signal(approved_signal)

                # Small delay between stream checks
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"[{self.sector_head_id}] Consume signals error: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds on error

    async def start(self):
        """Start Sector Head validator (consume signals loop)"""
        await self.initialize()

        # Start signal consumption loop
        await self.consume_signals_loop()

    def get_sector_stats(self) -> Dict[str, Any]:
        """
        Get Sector Head performance statistics
        
        Returns:
            Dict with sector-level metrics
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
            "sector_head_id": self.sector_head_id,
            "sector_name": self.sector_name,
            "supervised_team_leads": len(self.supervised_team_leads),
            "signals_processed": self.signals_processed,
            "signals_approved": self.signals_approved,
            "signals_rejected": self.signals_rejected,
            "approval_rate": round(approval_rate, 3),
            "rejection_reasons": dict(self.rejection_reasons),
            "sector_exposure": round(
                self.sector_exposures.get(self.sector_name, 0.0), 3
            ),
            "exposure_limit": self.exposure_limit,
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SECTOR HEAD POOL
# ═══════════════════════════════════════════════════════════════════════════


class SectorHeadPool:
    """
    Manages pool of 10 Sector Head validators
    
    Features:
    - Auto-assign team leads to sector heads (20 leads / 10 sectors = 2 each)
    - Start all sector heads concurrently
    - Performance aggregation
    - Graceful shutdown
    """

    def __init__(self, num_sector_heads: int = 10, num_team_leads: int = 20):
        """
        Initialize Sector Head pool
        
        Args:
            num_sector_heads: Number of Sector Head instances (default: 10)
            num_team_leads: Total team leads to supervise (default: 20)
        """
        self.num_sector_heads = num_sector_heads
        self.num_team_leads = num_team_leads

        # Sector Head instances
        self.sector_heads: List[SectorHead] = []
        self.sector_head_tasks: Dict[str, asyncio.Task] = {}

        # Pool state
        self.is_running = False
        self.start_time: Optional[datetime] = None

        logger.info(
            f"[SectorHeadPool] Initialized: {num_sector_heads} sector heads "
            f"supervising {num_team_leads} team leads"
        )

    def _assign_team_leads_to_sectors(self) -> Dict[str, List[str]]:
        """
        Assign team leads to sector heads (round-robin)
        
        Returns:
            Dict {sector_head_id: [team_lead_ids]}
        """
        assignments = defaultdict(list)

        # Get sector names (first 10 sectors)
        sector_names = list(SECTORS.keys())[: self.num_sector_heads]

        # Round-robin assignment
        for team_lead_idx in range(self.num_team_leads):
            team_lead_id = f"team_lead_{team_lead_idx:02d}"
            sector_idx = team_lead_idx % self.num_sector_heads
            sector_name = sector_names[sector_idx]
            sector_head_id = f"sector_head_{sector_name}"
            assignments[sector_head_id].append(team_lead_id)

        logger.info(
            f"[SectorHeadPool] Assigned {self.num_team_leads} team leads to "
            f"{self.num_sector_heads} sector heads"
        )

        return dict(assignments)

    async def initialize(self):
        """Initialize all Sector Head instances"""
        if self.sector_heads:
            logger.warning("[SectorHeadPool] Already initialized")
            return

        # Generate assignments
        assignments = self._assign_team_leads_to_sectors()

        # Get sector names
        sector_names = list(SECTORS.keys())[: self.num_sector_heads]

        # Create Sector Head instances
        for sector_name in sector_names:
            sector_head_id = f"sector_head_{sector_name}"
            team_leads = assignments.get(sector_head_id, [])
            sector_config = SECTORS[sector_name]

            sector_head = SectorHead(
                sector_head_id=sector_head_id,
                sector_name=sector_name,
                supervised_team_leads=team_leads,
                exposure_limit=sector_config.get("exposure_limit", 0.30),
            )
            self.sector_heads.append(sector_head)

        logger.info(
            f"[SectorHeadPool] Initialized {len(self.sector_heads)} sector heads"
        )

    async def start_all(self):
        """Start all Sector Head validators concurrently"""
        if self.is_running:
            logger.warning("[SectorHeadPool] Already running")
            return

        if not self.sector_heads:
            await self.initialize()

        self.is_running = True
        self.start_time = datetime.utcnow()

        logger.info(
            f"[SectorHeadPool] Starting {len(self.sector_heads)} sector heads..."
        )

        # Start all sector heads concurrently
        for sector_head in self.sector_heads:
            task = asyncio.create_task(sector_head.start())
            self.sector_head_tasks[sector_head.sector_head_id] = task

        logger.info(f"[SectorHeadPool] All {len(self.sector_heads)} sector heads started")

    async def shutdown(self):
        """Gracefully stop all Sector Head validators"""
        logger.info("[SectorHeadPool] Shutting down...")

        self.is_running = False

        # Cancel all tasks
        for sector_head_id, task in self.sector_head_tasks.items():
            if not task.done():
                logger.info(f"[SectorHeadPool] Cancelling {sector_head_id}")
                task.cancel()

        # Wait for all tasks
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    *self.sector_head_tasks.values(), return_exceptions=True
                ),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            logger.warning("[SectorHeadPool] Shutdown timeout")

        logger.info("[SectorHeadPool] Shutdown complete")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get aggregated pool statistics"""
        total_processed = 0
        total_approved = 0
        total_rejected = 0

        for sector_head in self.sector_heads:
            stats = sector_head.get_sector_stats()
            total_processed += stats["signals_processed"]
            total_approved += stats["signals_approved"]
            total_rejected += stats["signals_rejected"]

        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        approval_rate = total_approved / total_processed if total_processed else 0

        return {
            "pool_status": "running" if self.is_running else "stopped",
            "total_sector_heads": len(self.sector_heads),
            "signals_processed": total_processed,
            "signals_approved": total_approved,
            "signals_rejected": total_rejected,
            "approval_rate": round(approval_rate, 3),
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_global_sector_head_pool: Optional[SectorHeadPool] = None


async def get_sector_head_pool(
    num_sector_heads: int = 10, num_team_leads: int = 20
) -> SectorHeadPool:
    """
    Get global Sector Head pool instance (singleton)
    
    Args:
        num_sector_heads: Number of Sector Head instances (default: 10)
        num_team_leads: Total team leads (default: 20)
    
    Returns:
        SectorHeadPool instance
    """
    global _global_sector_head_pool

    if _global_sector_head_pool is None:
        _global_sector_head_pool = SectorHeadPool(
            num_sector_heads=num_sector_heads, num_team_leads=num_team_leads
        )
        await _global_sector_head_pool.initialize()

    return _global_sector_head_pool
