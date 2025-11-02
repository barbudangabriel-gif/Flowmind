"""
CORE ENGINE Orchestrator
Coordinates 200-agent hierarchical trading system.

Architecture:
  - 1 Master Director (Tier 1)
  - 10 Sector Heads (Tier 2)
  - 20 Team Leads (Tier 3)
  - 167 Scanner Agents (Tier 4)
  - 2 Specialists (News Aggregator, Data Layer)

Signal Flow:
  scanners → signals:universe → team_leads → signals:validated:{id}
  → sector_heads → signals:approved:{id} → master_director → signals:final
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from backend.agents.tier4_workers import get_scanner_pool
from backend.agents.tier3_supervisors import get_team_lead_pool
from backend.agents.tier2_validators import get_sector_head_pool
from backend.agents.tier1_director import get_master_director

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central coordinator for CORE ENGINE.
    Manages lifecycle, health monitoring, and statistics aggregation.
    """

    def __init__(self):
        self.orchestrator_id = "core_engine_orchestrator"
        self.is_running = False
        self.start_time: Optional[datetime] = None

        # Component references (initialized on start)
        self.scanner_pool = None
        self.team_lead_pool = None
        self.sector_head_pool = None
        self.master_director = None

        # Background tasks
        self.tasks: List[asyncio.Task] = []

        # Health tracking
        self.health_checks_enabled = True
        self.health_check_interval = 60  # 60s

        # Statistics
        self.stats = {
            "uptime_seconds": 0,
            "agents_running": 0,
            "total_agents": 198,
            "tiers": {
                "tier4_scanners": {"running": 0, "total": 167},
                "tier3_team_leads": {"running": 0, "total": 20},
                "tier2_sector_heads": {"running": 0, "total": 10},
                "tier1_director": {"running": 0, "total": 1},
            },
            "signal_flow": {
                "universe_published": 0,
                "validated_published": 0,
                "approved_published": 0,
                "final_published": 0,
            },
            "performance": {
                "signals_per_second": 0.0,
                "avg_latency_seconds": 0.0,
                "win_rate_percent": 0.0,
            },
        }

        logger.info(f"Orchestrator initialized: {self.orchestrator_id}")

    async def start(self):
        """Start all 200 agents in hierarchical order."""
        if self.is_running:
            logger.warning("Orchestrator already running")
            return

        logger.info("=" * 80)
        logger.info("STARTING CORE ENGINE (200 AGENTS)")
        logger.info("=" * 80)

        self.start_time = datetime.utcnow()
        self.is_running = True

        try:
            # STEP 1: Initialize Tier 4 - Scanner Agents
            logger.info("\n[STEP 1] Starting Tier 4 - Scanner Agents (167)...")
            self.scanner_pool = await get_scanner_pool()
            await self.scanner_pool.start_all_scanners()
            running_scanners = sum(
                1 for s in self.scanner_pool.scanners if s.is_running
            )
            self.stats["tiers"]["tier4_scanners"]["running"] = running_scanners
            logger.info(
                f"✅ {running_scanners}/167 scanners running (Universe → signals:universe)"
            )

            # STEP 2: Initialize Tier 3 - Team Lead Supervisors
            logger.info("\n[STEP 2] Starting Tier 3 - Team Lead Supervisors (20)...")
            self.team_lead_pool = await get_team_lead_pool()
            await self.team_lead_pool.start_all_leads()
            running_leads = sum(1 for tl in self.team_lead_pool.team_leads if tl.is_running)
            self.stats["tiers"]["tier3_team_leads"]["running"] = running_leads
            logger.info(
                f"✅ {running_leads}/20 team leads running (Validate → signals:validated:{{id}})"
            )

            # STEP 3: Initialize Tier 2 - Sector Head Validators
            logger.info("\n[STEP 3] Starting Tier 2 - Sector Head Validators (10)...")
            self.sector_head_pool = await get_sector_head_pool()
            await self.sector_head_pool.start_all_heads()
            running_heads = sum(
                1 for sh in self.sector_head_pool.sector_heads if sh.is_running
            )
            self.stats["tiers"]["tier2_sector_heads"]["running"] = running_heads
            logger.info(
                f"✅ {running_heads}/10 sector heads running (Approve → signals:approved:{{id}})"
            )

            # STEP 4: Initialize Tier 1 - Master Director
            logger.info("\n[STEP 4] Starting Tier 1 - Master Director (1)...")
            self.master_director = await get_master_director()
            await self.master_director.start()
            self.stats["tiers"]["tier1_director"]["running"] = (
                1 if self.master_director.is_running else 0
            )
            logger.info(
                f"✅ Master Director running (GPT-4o + fallback → signals:final)"
            )

            # STEP 5: Start background tasks
            logger.info("\n[STEP 5] Starting Background Tasks...")
            self.tasks.append(asyncio.create_task(self._health_monitor_loop()))
            self.tasks.append(asyncio.create_task(self._stats_aggregation_loop()))
            logger.info("✅ 2 background tasks started (health monitoring, stats)")

            # Summary
            total_running = (
                self.stats["tiers"]["tier4_scanners"]["running"]
                + self.stats["tiers"]["tier3_team_leads"]["running"]
                + self.stats["tiers"]["tier2_sector_heads"]["running"]
                + self.stats["tiers"]["tier1_director"]["running"]
            )
            self.stats["agents_running"] = total_running

            logger.info("\n" + "=" * 80)
            logger.info(
                f"🎉 CORE ENGINE STARTED: {total_running}/198 agents operational"
            )
            logger.info("=" * 80)
            logger.info(f"Signal Flow: scanners → universe → leads → validated")
            logger.info(f"             → sectors → approved → director → final")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Failed to start CORE ENGINE: {e}", exc_info=True)
            await self.stop()
            raise

    async def stop(self):
        """Stop all agents gracefully."""
        if not self.is_running:
            logger.warning("Orchestrator not running")
            return

        logger.info("=" * 80)
        logger.info("STOPPING CORE ENGINE")
        logger.info("=" * 80)

        self.is_running = False

        try:
            # Stop background tasks
            logger.info("[1/5] Stopping background tasks...")
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()

            # Stop Tier 1 (Director)
            if self.master_director:
                logger.info("[2/5] Stopping Master Director...")
                # Director doesn't have stop() yet, just flag
                self.master_director.is_running = False

            # Stop Tier 2 (Sector Heads)
            if self.sector_head_pool:
                logger.info("[3/5] Stopping Sector Heads...")
                await self.sector_head_pool.stop_all_heads()

            # Stop Tier 3 (Team Leads)
            if self.team_lead_pool:
                logger.info("[4/5] Stopping Team Leads...")
                await self.team_lead_pool.stop_all_leads()

            # Stop Tier 4 (Scanners)
            if self.scanner_pool:
                logger.info("[2/5] Stopping Scanner Agents...")
                await self.scanner_pool.stop_all_scanners()

            logger.info("=" * 80)
            logger.info("✅ CORE ENGINE STOPPED")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

    async def _health_monitor_loop(self):
        """Periodically check agent health and restart if needed."""
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)

                if not self.health_checks_enabled:
                    continue

                logger.info("Running health checks...")

                # Check scanner pool
                if self.scanner_pool:
                    dead_scanners = [
                        s for s in self.scanner_pool.scanners if not s.is_running
                    ]
                    if dead_scanners:
                        logger.warning(
                            f"⚠️  {len(dead_scanners)} scanners down, restarting..."
                        )
                        for scanner in dead_scanners[:10]:  # Restart up to 10 at once
                            try:
                                await scanner.start()
                            except Exception as e:
                                logger.error(
                                    f"Failed to restart scanner {scanner.agent_id}: {e}"
                                )

                # Check team leads
                if self.team_lead_pool:
                    dead_leads = [
                        tl for tl in self.team_lead_pool.team_leads if not tl.is_running
                    ]
                    if dead_leads:
                        logger.warning(
                            f"⚠️  {len(dead_leads)} team leads down, restarting..."
                        )
                        for lead in dead_leads:
                            try:
                                await lead.start()
                            except Exception as e:
                                logger.error(
                                    f"Failed to restart team lead {lead.lead_id}: {e}"
                                )

                # Check sector heads
                if self.sector_head_pool:
                    dead_heads = [
                        sh
                        for sh in self.sector_head_pool.sector_heads
                        if not sh.is_running
                    ]
                    if dead_heads:
                        logger.warning(
                            f"⚠️  {len(dead_heads)} sector heads down, restarting..."
                        )
                        for head in dead_heads:
                            try:
                                await head.start()
                            except Exception as e:
                                logger.error(
                                    f"Failed to restart sector head {head.head_id}: {e}"
                                )

                # Check master director
                if self.master_director and not self.master_director.is_running:
                    logger.warning("⚠️  Master Director down, restarting...")
                    try:
                        await self.master_director.start()
                    except Exception as e:
                        logger.error(f"Failed to restart Master Director: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}", exc_info=True)

    async def _stats_aggregation_loop(self):
        """Aggregate statistics from all agents."""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Update every 30s

                # Update uptime
                if self.start_time:
                    uptime = (datetime.utcnow() - self.start_time).total_seconds()
                    self.stats["uptime_seconds"] = int(uptime)

                # Update running counts
                if self.scanner_pool:
                    self.stats["tiers"]["tier4_scanners"]["running"] = sum(
                        1 for s in self.scanner_pool.scanners if s.is_running
                    )

                if self.team_lead_pool:
                    self.stats["tiers"]["tier3_team_leads"]["running"] = sum(
                        1 for tl in self.team_lead_pool.team_leads if tl.is_running
                    )

                if self.sector_head_pool:
                    self.stats["tiers"]["tier2_sector_heads"]["running"] = sum(
                        1 for sh in self.sector_head_pool.sector_heads if sh.is_running
                    )

                if self.master_director:
                    self.stats["tiers"]["tier1_director"]["running"] = (
                        1 if self.master_director.is_running else 0
                    )

                # Total agents running
                total_running = sum(
                    tier["running"] for tier in self.stats["tiers"].values()
                )
                self.stats["agents_running"] = total_running

                # Aggregate signal flow stats
                total_universe = 0
                total_validated = 0
                total_approved = 0

                if self.scanner_pool:
                    pool_stats = self.scanner_pool.get_pool_stats()
                    total_universe = pool_stats.get("signals_published", 0)

                if self.team_lead_pool:
                    for lead in self.team_lead_pool.team_leads:
                        lead_stats = lead.get_lead_stats()
                        total_validated += lead_stats.get("signals_validated", 0)

                if self.sector_head_pool:
                    for head in self.sector_head_pool.sector_heads:
                        head_stats = head.get_head_stats()
                        total_approved += head_stats.get("signals_approved", 0)

                if self.master_director:
                    director_stats = self.master_director.get_director_stats()
                    total_final = director_stats.get("signals_approved", 0)
                    self.stats["signal_flow"]["final_published"] = total_final

                self.stats["signal_flow"]["universe_published"] = total_universe
                self.stats["signal_flow"]["validated_published"] = total_validated
                self.stats["signal_flow"]["approved_published"] = total_approved

                # Calculate performance metrics
                if self.stats["uptime_seconds"] > 0:
                    self.stats["performance"]["signals_per_second"] = round(
                        total_universe / self.stats["uptime_seconds"], 2
                    )

                # Calculate win rate (approved / universe)
                if total_universe > 0:
                    final_approved = self.stats["signal_flow"]["final_published"]
                    self.stats["performance"]["win_rate_percent"] = round(
                        (final_approved / total_universe) * 100, 2
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stats aggregation: {e}", exc_info=True)

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get current orchestrator statistics."""
        return {
            "orchestrator_id": self.orchestrator_id,
            "is_running": self.is_running,
            "start_time": (
                self.start_time.isoformat() if self.start_time else None
            ),
            "uptime_seconds": self.stats["uptime_seconds"],
            "agents": {
                "total": self.stats["total_agents"],
                "running": self.stats["agents_running"],
                "health_percentage": round(
                    (self.stats["agents_running"] / self.stats["total_agents"]) * 100,
                    2,
                ),
            },
            "tiers": self.stats["tiers"],
            "signal_flow": self.stats["signal_flow"],
            "performance": self.stats["performance"],
        }


# Singleton instance
_orchestrator_instance: Optional[Orchestrator] = None


async def get_orchestrator() -> Orchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
