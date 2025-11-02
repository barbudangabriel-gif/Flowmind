"""
Universe Scanner Pool Manager - Tier 4 Workers Coordinator
Spawns and manages 167 UniverseScannerAgent instances (500 tickers total)

Architecture:
- 167 agents × 3 tickers = 501 capacity (500 used)
- Load balancing: Distribute tickers evenly across agents
- Health monitoring: Track agent status, auto-restart failures
- Performance aggregation: Pool-level statistics
- Graceful shutdown: Stop all agents cleanly

Usage:
    pool = UniverseScannerPool(num_agents=167)
    await pool.initialize()
    await pool.start_all()
    # ... pool runs in background ...
    stats = pool.get_pool_stats()
    await pool.shutdown()
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier4_workers.scanner_agent import UniverseScannerAgent

logger = logging.getLogger(__name__)


class UniverseScannerPool:
    """
    Manages pool of 167 UniverseScannerAgent instances
    
    Features:
    - Auto-spawn agents with ticker assignments
    - Load balancing (3 tickers per agent)
    - Health monitoring and auto-restart
    - Performance aggregation (pool-level stats)
    - Graceful shutdown
    """

    def __init__(
        self,
        num_agents: int = 167,
        tickers_per_agent: int = 3,
        light_interval: int = 300,  # 5 minutes
        deep_interval: int = 60,  # 1 minute
    ):
        """
        Initialize scanner pool
        
        Args:
            num_agents: Number of scanner agents (default: 167)
            tickers_per_agent: Tickers per agent (default: 3)
            light_interval: Light scan interval in seconds (default: 300)
            deep_interval: Deep scan interval in seconds (default: 60)
        """
        self.num_agents = num_agents
        self.tickers_per_agent = tickers_per_agent
        self.light_interval = light_interval
        self.deep_interval = deep_interval

        # Agent instances
        self.agents: List[UniverseScannerAgent] = []
        self.agent_tasks: Dict[str, asyncio.Task] = {}  # {agent_id: task}

        # Ticker assignments
        self.ticker_assignments: Dict[str, List[str]] = {}  # {agent_id: [tickers]}
        self.ticker_universe: List[str] = []

        # Pool state
        self.is_running = False
        self.start_time: Optional[datetime] = None

        # Performance tracking
        self.total_signals_generated = 0
        self.total_signals_validated = 0
        self.failed_agents: List[str] = []

        logger.info(
            f"[ScannerPool] Initialized pool: {num_agents} agents, "
            f"{tickers_per_agent} tickers/agent"
        )

    def _get_ticker_universe(self) -> List[str]:
        """
        Get universe of 500 tickers to scan
        
        Extends the 100-ticker list from StockScanner to 500 tickers
        (S&P 500 + NASDAQ 100 + Russell 2000 top picks)
        
        Returns:
            List of 500 ticker symbols
        """
        # Base: S&P 500 major tickers (from investment_scoring.py)
        sp500_major = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK.B",
            "V", "JNJ", "WMT", "JPM", "PG", "UNH", "DIS", "HD", "MA", "PFE",
            "BAC", "ABBV", "ADBE", "CRM", "KO", "PEP", "TMO", "COST", "AVGO",
            "DHR", "NEE", "ABT", "CMCSA", "XOM", "LLY", "VZ", "ORCL", "INTC",
            "AMD", "COP", "PM", "HON", "LIN", "CVX", "NOW", "IBM", "QCOM",
            "UBER", "TXN", "SPGI", "LOW", "CAT", "GS", "NFLX", "INTU", "AMGN",
            "RTX", "ISRG", "MDT", "BA", "SBUX", "DE", "AMAT", "GILD", "AXP",
            "BKNG", "LRCX", "TJX", "SYK", "BLK", "MU", "TMUS", "REGN", "PYPL",
            "SCHW", "PANW", "C", "PGR", "VRTX", "MMC", "CB", "MDLZ", "SO",
            "FI", "BSX", "EOG", "KLAC", "WM", "EL", "SNPS", "ITW", "ADI",
            "MSI", "CSX", "CME", "ZTS", "HCA", "SHW", "APD", "CDNS", "MO", "USB"
        ]

        # Additional S&P 500 (mid-cap)
        sp500_additional = [
            "CI", "PLD", "CL", "DUK", "ICE", "TT", "MCK", "AON", "SLB", "GD",
            "TGT", "MMM", "BDX", "EMR", "NSC", "GM", "USB", "ADP", "WMB",
            "NOC", "MPC", "HUM", "APH", "CCI", "PSA", "FIS", "EQIX", "EW",
            "F", "ADSK", "AIG", "TFC", "ROP", "LHX", "COF", "SRE", "ORLY",
            "KMB", "D", "TEL", "AFL", "AEP", "PSX", "IQV", "WELL", "AZO",
            "PPG", "ECL", "DLR", "CMI", "ILMN", "JCI", "ROST", "PAYX", "CTAS",
            "CTVA", "KMI", "A", "MSCI", "AMP", "CHTR", "NEM", "PCG", "HPQ",
            "GIS", "EA", "LVS", "PRU", "ALL", "SPG", "YUM", "DOW", "O", "CARR",
            "ODFL", "PCAR", "DD", "IFF", "GPN", "FTV", "ED", "KHC", "OTIS",
            "CPRT", "VMC", "HLT", "BIIB", "AWK", "WEC", "VRSK", "FRC", "FAST",
            "ALB", "APTV", "GWW", "ES", "ROK", "KEYS", "CBRE", "MTD", "DHI"
        ]

        # NASDAQ 100 (tech-heavy)
        nasdaq100 = [
            "ABNB", "AEP", "ALGN", "AMAT", "AMD", "ANSS", "ASML", "AVGO",
            "AZN", "BIDU", "BKNG", "CDNS", "CEG", "CHTR", "CMCSA", "COST",
            "CPRT", "CRWD", "CSCO", "CSGP", "CSX", "CTAS", "CTSH", "DDOG",
            "DLTR", "DXCM", "EA", "EBAY", "EXC", "FANG", "FAST", "FTNT",
            "GILD", "HON", "IDXX", "ILMN", "INTC", "INTU", "ISRG", "KDP",
            "KHC", "KLAC", "LCID", "LRCX", "LULU", "MAR", "MCHP", "MDLZ",
            "MELI", "MNST", "MRNA", "MRVL", "MU", "NFLX", "NTES", "NVDA",
            "NXPI", "ODFL", "ON", "ORLY", "PANW", "PAYX", "PCAR", "PDD",
            "PEP", "PYPL", "QCOM", "REGN", "RIVN", "ROST", "SBUX", "SGEN",
            "SIRI", "SNPS", "TEAM", "TMUS", "TXN", "VRSK", "VRTX", "WBA",
            "WBD", "WDAY", "XEL", "ZM", "ZS"
        ]

        # Popular retail/meme stocks
        retail_favorites = [
            "AMC", "GME", "PLTR", "SOFI", "RBLX", "COIN", "HOOD", "DKNG",
            "LCID", "RIVN", "NIO", "XPEV", "LI", "BABA", "JD", "PDD", "TSM",
            "ASML", "ARM", "SHOP", "SQ", "ROKU", "ZM", "DOCU", "SNOW", "NET",
            "DDOG", "CRWD", "ZS", "OKTA", "TWLO", "DASH", "ABNB", "UBER",
            "LYFT", "MRNA", "BNTX", "PFE", "JNJ", "LLY", "ABBV", "BMY", "MRK"
        ]

        # Energy sector (high volatility)
        energy = [
            "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY",
            "HAL", "DVN", "FANG", "BKR", "HES", "MRO", "APA", "CNQ", "SU",
            "IMO", "CVE", "TRP", "ENB", "EPD", "ET", "WMB", "KMI", "OKE"
        ]

        # Financial sector
        financials = [
            "JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW", "USB", "PNC",
            "TFC", "COF", "AXP", "BX", "KKR", "APO", "SPGI", "MCO", "CME",
            "ICE", "MSCI", "FIS", "FISV", "V", "MA", "PYPL", "SQ", "ADP"
        ]

        # Healthcare sector
        healthcare = [
            "UNH", "JNJ", "PFE", "ABBV", "LLY", "TMO", "ABT", "DHR", "BMY",
            "AMGN", "GILD", "VRTX", "REGN", "BIIB", "MRNA", "BNTX", "ISRG",
            "BSX", "MDT", "SYK", "EW", "ZBH", "ALGN", "DXCM", "HOLX", "IDXX"
        ]

        # Combine all sources
        all_tickers = set()
        all_tickers.update(sp500_major)
        all_tickers.update(sp500_additional)
        all_tickers.update(nasdaq100)
        all_tickers.update(retail_favorites)
        all_tickers.update(energy)
        all_tickers.update(financials)
        all_tickers.update(healthcare)

        # Convert to sorted list and take first 500
        ticker_list = sorted(list(all_tickers))[:500]

        logger.info(f"[ScannerPool] Ticker universe: {len(ticker_list)} symbols")
        return ticker_list

    def _assign_tickers_to_agents(self):
        """
        Distribute tickers evenly across agents (load balancing)
        
        Algorithm: Round-robin assignment
        - Agent 0: tickers[0], tickers[167], tickers[334]
        - Agent 1: tickers[1], tickers[168], tickers[335]
        - ...
        - Agent 166: tickers[166], tickers[333], tickers[499]
        """
        self.ticker_universe = self._get_ticker_universe()
        total_tickers = len(self.ticker_universe)

        # Round-robin assignment
        for agent_idx in range(self.num_agents):
            agent_id = f"scanner_{agent_idx:03d}"
            assigned_tickers = []

            # Assign every Nth ticker where N = num_agents
            for offset in range(self.tickers_per_agent):
                ticker_idx = agent_idx + (offset * self.num_agents)
                if ticker_idx < total_tickers:
                    assigned_tickers.append(self.ticker_universe[ticker_idx])

            self.ticker_assignments[agent_id] = assigned_tickers

        logger.info(
            f"[ScannerPool] Assigned {total_tickers} tickers to {self.num_agents} agents"
        )

    async def initialize(self):
        """Initialize all scanner agents with ticker assignments"""
        if self.agents:
            logger.warning("[ScannerPool] Already initialized")
            return

        # Generate ticker assignments
        self._assign_tickers_to_agents()

        # Create agent instances
        for agent_id, tickers in self.ticker_assignments.items():
            if not tickers:
                continue

            agent = UniverseScannerAgent(
                agent_id=agent_id,
                assigned_tickers=tickers,
                light_interval=self.light_interval,
                deep_interval=self.deep_interval,
            )

            # Initialize agent services
            await agent.initialize()

            self.agents.append(agent)

        logger.info(f"[ScannerPool] Initialized {len(self.agents)} scanner agents")

    async def start_all(self):
        """Start all scanner agents concurrently"""
        if self.is_running:
            logger.warning("[ScannerPool] Already running")
            return

        if not self.agents:
            await self.initialize()

        self.is_running = True
        self.start_time = datetime.utcnow()

        # Start all agents concurrently
        logger.info(f"[ScannerPool] Starting {len(self.agents)} agents...")

        for agent in self.agents:
            # Create background task for each agent
            task = asyncio.create_task(agent.start())
            self.agent_tasks[agent.agent_id] = task

        logger.info(f"[ScannerPool] All {len(self.agents)} agents started")

        # Start health monitor in background
        monitor_task = asyncio.create_task(self._monitor_health_loop())
        self.agent_tasks["health_monitor"] = monitor_task

    async def _monitor_health_loop(self):
        """Background task: Monitor agent health and restart failures"""
        logger.info("[ScannerPool] Health monitor started")

        while self.is_running:
            try:
                # Check each agent's task
                for agent in self.agents:
                    agent_id = agent.agent_id
                    task = self.agent_tasks.get(agent_id)

                    if not task or task.done():
                        # Agent crashed or stopped
                        if agent_id not in self.failed_agents:
                            logger.error(f"[ScannerPool] Agent {agent_id} FAILED")
                            self.failed_agents.append(agent_id)

                            # Get exception if available
                            if task and task.done():
                                try:
                                    exc = task.exception()
                                    if exc:
                                        logger.error(
                                            f"[ScannerPool] Agent {agent_id} exception: {exc}"
                                        )
                                except Exception as e:
                                    logger.error(
                                        f"[ScannerPool] Could not get exception: {e}"
                                    )

                            # Restart agent
                            logger.info(f"[ScannerPool] Restarting agent {agent_id}...")
                            new_task = asyncio.create_task(agent.start())
                            self.agent_tasks[agent_id] = new_task

                # Sleep before next health check
                await asyncio.sleep(60)  # Check every 60 seconds

            except Exception as e:
                logger.error(f"[ScannerPool] Health monitor error: {e}")
                await asyncio.sleep(60)

    async def shutdown(self):
        """Gracefully stop all scanner agents"""
        logger.info("[ScannerPool] Shutting down...")

        self.is_running = False

        # Cancel all agent tasks
        for agent_id, task in self.agent_tasks.items():
            if not task.done():
                logger.info(f"[ScannerPool] Cancelling {agent_id}")
                task.cancel()

        # Wait for all tasks to finish (with timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.agent_tasks.values(), return_exceptions=True),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            logger.warning("[ScannerPool] Shutdown timeout (some tasks may be hanging)")

        logger.info("[ScannerPool] Shutdown complete")

    def get_pool_stats(self) -> Dict[str, Any]:
        """
        Get aggregated pool statistics
        
        Returns:
            Dict with pool-level metrics
        """
        # Aggregate agent stats
        total_signals = 0
        total_validated = 0
        total_false_positives = 0
        hot_tickers = set()

        for agent in self.agents:
            stats = agent.get_stats()
            total_signals += stats["signals_generated"]
            total_validated += stats["signals_validated"]
            total_false_positives += stats["false_positives"]
            hot_tickers.update(stats["hot_tickers"])

        # Calculate pool metrics
        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        active_agents = len(self.agents) - len(self.failed_agents)

        win_rate = total_validated / total_signals if total_signals else 0

        return {
            "pool_status": "running" if self.is_running else "stopped",
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "failed_agents": len(self.failed_agents),
            "failed_agent_ids": self.failed_agents,
            "ticker_universe_size": len(self.ticker_universe),
            "hot_tickers": list(hot_tickers),
            "hot_tickers_count": len(hot_tickers),
            "signals_generated": total_signals,
            "signals_validated": total_validated,
            "false_positives": total_false_positives,
            "win_rate": round(win_rate, 3),
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific agent"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent.get_stats()
        return None

    def get_ticker_assignment(self, ticker: str) -> Optional[str]:
        """Find which agent is assigned to a ticker"""
        for agent_id, tickers in self.ticker_assignments.items():
            if ticker in tickers:
                return agent_id
        return None


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_global_scanner_pool: Optional[UniverseScannerPool] = None


async def get_scanner_pool(
    num_agents: int = 167,
    tickers_per_agent: int = 3,
    light_interval: int = 300,
    deep_interval: int = 60,
) -> UniverseScannerPool:
    """
    Get global scanner pool instance (singleton)
    
    Args:
        num_agents: Number of scanner agents (default: 167)
        tickers_per_agent: Tickers per agent (default: 3)
        light_interval: Light scan interval (default: 300s = 5min)
        deep_interval: Deep scan interval (default: 60s = 1min)
    
    Returns:
        UniverseScannerPool instance
    """
    global _global_scanner_pool

    if _global_scanner_pool is None:
        _global_scanner_pool = UniverseScannerPool(
            num_agents=num_agents,
            tickers_per_agent=tickers_per_agent,
            light_interval=light_interval,
            deep_interval=deep_interval,
        )
        await _global_scanner_pool.initialize()

    return _global_scanner_pool
