"""
CORE ENGINE API Router
FastAPI endpoints for 198-agent hierarchical trading system control.

Endpoints:
  GET  /api/core-engine/status     - Get orchestrator status
  GET  /api/core-engine/stats      - Get detailed statistics
  POST /api/core-engine/start      - Start all agents
  POST /api/core-engine/stop       - Stop all agents gracefully
  GET  /api/core-engine/signals    - Get recent final signals
  GET  /api/core-engine/health     - Get per-tier health status
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.agents.orchestrator import get_orchestrator
from backend.redis_fallback import get_kv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/core-engine", tags=["core-engine"])


class OrchestratorStatusResponse(BaseModel):
    """Orchestrator status response model."""

    is_running: bool
    uptime_seconds: int
    agents_running: int
    agents_total: int
    health_percentage: float


class OrchestratorStatsResponse(BaseModel):
    """Detailed orchestrator statistics."""

    orchestrator_id: str
    is_running: bool
    start_time: Optional[str]
    uptime_seconds: int
    agents: Dict[str, Any]
    tiers: Dict[str, Dict[str, int]]
    signal_flow: Dict[str, int]
    performance: Dict[str, float]


class SignalResponse(BaseModel):
    """Final execution signal response."""

    signal_id: str
    ticker: str
    action: str
    position_size: float
    max_loss: float
    confidence: float
    reasoning: str
    approved_at: str


@router.get("/status", response_model=OrchestratorStatusResponse)
async def get_status():
    """
    Get current orchestrator status.
    
    Returns basic health information:
    - is_running: Whether CORE ENGINE is active
    - uptime_seconds: Time since startup
    - agents_running: Number of operational agents
    - health_percentage: Overall system health
    """
    try:
        orchestrator = await get_orchestrator()
        stats = orchestrator.get_orchestrator_stats()

        return OrchestratorStatusResponse(
            is_running=stats["is_running"],
            uptime_seconds=stats["uptime_seconds"],
            agents_running=stats["agents"]["running"],
            agents_total=stats["agents"]["total"],
            health_percentage=stats["agents"]["health_percentage"],
        )
    except Exception as e:
        logger.error(f"Error getting orchestrator status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/stats", response_model=OrchestratorStatsResponse)
async def get_stats():
    """
    Get detailed orchestrator statistics.
    
    Returns comprehensive metrics:
    - Agent counts per tier (Tier 1-4)
    - Signal flow metrics (universe, validated, approved, final)
    - Performance metrics (signals/sec, win rate)
    - Health status per tier
    """
    try:
        orchestrator = await get_orchestrator()
        stats = orchestrator.get_orchestrator_stats()

        return OrchestratorStatsResponse(
            orchestrator_id=stats["orchestrator_id"],
            is_running=stats["is_running"],
            start_time=stats["start_time"],
            uptime_seconds=stats["uptime_seconds"],
            agents=stats["agents"],
            tiers=stats["tiers"],
            signal_flow=stats["signal_flow"],
            performance=stats["performance"],
        )
    except Exception as e:
        logger.error(f"Error getting orchestrator stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/start")
async def start_core_engine():
    """
    Start CORE ENGINE (198 agents).
    
    Initiates hierarchical startup:
    1. Tier 4 Scanner Agents (167)
    2. Tier 3 Team Lead Supervisors (20)
    3. Tier 2 Sector Head Validators (10)
    4. Tier 1 Master Director (1)
    5. Background tasks (health monitoring, stats aggregation)
    
    Returns:
      - status: "started" or "already_running"
      - message: Startup confirmation
      - agents_running: Number of operational agents
    """
    try:
        orchestrator = await get_orchestrator()

        if orchestrator.is_running:
            stats = orchestrator.get_orchestrator_stats()
            return {
                "status": "already_running",
                "message": "CORE ENGINE is already operational",
                "agents_running": stats["agents"]["running"],
                "uptime_seconds": stats["uptime_seconds"],
            }

        # Start all agents
        await orchestrator.start()

        stats = orchestrator.get_orchestrator_stats()

        return {
            "status": "started",
            "message": f"CORE ENGINE started successfully ({stats['agents']['running']}/198 agents operational)",
            "agents_running": stats["agents"]["running"],
            "health_percentage": stats["agents"]["health_percentage"],
        }

    except Exception as e:
        logger.error(f"Error starting CORE ENGINE: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to start CORE ENGINE: {str(e)}"
        )


@router.post("/stop")
async def stop_core_engine():
    """
    Stop CORE ENGINE gracefully.
    
    Initiates reverse-order shutdown:
    1. Stop background tasks
    2. Stop Master Director (Tier 1)
    3. Stop Sector Head Validators (Tier 2)
    4. Stop Team Lead Supervisors (Tier 3)
    5. Stop Scanner Agents (Tier 4)
    
    Returns:
      - status: "stopped" or "not_running"
      - message: Shutdown confirmation
    """
    try:
        orchestrator = await get_orchestrator()

        if not orchestrator.is_running:
            return {
                "status": "not_running",
                "message": "CORE ENGINE is not currently running",
            }

        # Stop all agents
        await orchestrator.stop()

        return {
            "status": "stopped",
            "message": "CORE ENGINE stopped gracefully (all 198 agents halted)",
        }

    except Exception as e:
        logger.error(f"Error stopping CORE ENGINE: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to stop CORE ENGINE: {str(e)}"
        )


@router.get("/signals", response_model=List[SignalResponse])
async def get_recent_signals(limit: int = Query(default=20, ge=1, le=100)):
    """
    Get recent final execution signals.
    
    Query Parameters:
      - limit: Number of signals to retrieve (1-100, default 20)
    
    Returns list of final signals approved by Master Director.
    Each signal includes:
      - ticker, action, position_size, max_loss
      - confidence, reasoning
      - approved_at timestamp
    """
    try:
        cli = await get_kv()

        # Query signals:final stream (last N entries)
        # Redis XREVRANGE signals:final + - COUNT limit
        signals_raw = await cli.xrevrange("signals:final", count=limit)

        signals = []
        for signal_id, fields in signals_raw:
            # Parse signal fields
            signal_data = {
                key.decode() if isinstance(key, bytes) else key: (
                    val.decode() if isinstance(val, bytes) else val
                )
                for key, val in fields.items()
            }

            signals.append(
                SignalResponse(
                    signal_id=signal_id.decode()
                    if isinstance(signal_id, bytes)
                    else signal_id,
                    ticker=signal_data.get("ticker", "UNKNOWN"),
                    action=signal_data.get("action", "UNKNOWN"),
                    position_size=float(signal_data.get("position_size", 0)),
                    max_loss=float(signal_data.get("max_loss", 0)),
                    confidence=float(signal_data.get("director_confidence", 0)),
                    reasoning=signal_data.get("director_reasoning", ""),
                    approved_at=signal_data.get("approved_at", ""),
                )
            )

        return signals

    except Exception as e:
        logger.error(f"Error fetching signals: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch signals: {str(e)}"
        )


@router.get("/health")
async def get_health_status():
    """
    Get per-tier health status.
    
    Returns detailed health breakdown:
    - Tier 4 Scanners: 167 agents
    - Tier 3 Team Leads: 20 agents
    - Tier 2 Sector Heads: 10 agents
    - Tier 1 Director: 1 agent
    
    Each tier includes:
      - running: Number of operational agents
      - total: Total agents in tier
      - health_percentage: Tier health (running/total * 100)
    """
    try:
        orchestrator = await get_orchestrator()
        stats = orchestrator.get_orchestrator_stats()

        tiers = stats["tiers"]

        health_data = {}
        for tier_name, tier_info in tiers.items():
            running = tier_info["running"]
            total = tier_info["total"]
            health_pct = (running / total * 100) if total > 0 else 0

            health_data[tier_name] = {
                "running": running,
                "total": total,
                "health_percentage": round(health_pct, 2),
                "status": (
                    "healthy"
                    if health_pct >= 95
                    else "degraded"
                    if health_pct >= 80
                    else "critical"
                ),
            }

        return {
            "overall_health": stats["agents"]["health_percentage"],
            "overall_status": (
                "healthy"
                if stats["agents"]["health_percentage"] >= 95
                else "degraded"
                if stats["agents"]["health_percentage"] >= 80
                else "critical"
            ),
            "is_running": stats["is_running"],
            "uptime_seconds": stats["uptime_seconds"],
            "tiers": health_data,
        }

    except Exception as e:
        logger.error(f"Error getting health status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get health status: {str(e)}"
        )
