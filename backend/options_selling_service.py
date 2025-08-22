from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

from sell_puts_engine import (
    Config, Position, allocate_contracts_equal, greedy_fill_by_risk,
    summarize, to_table, collect_signals
)

# -----------------------------
# Core compute request/response
# -----------------------------
class PositionIn(BaseModel):
    ticker: str
    price: float
    strike: float
    delta: float
    dte: int
    premium: float
    iv_rank: float
    vix: float
    selected: Optional[bool] = True
    assigned: Optional[bool] = False
    status: Optional[str] = "Active"
    contracts: Optional[int] = 0
    notes: Optional[str] = ""

class ConfigIn(BaseModel):
    delta_min: float = 0.25
    delta_max: float = 0.30
    dte_min: int = 20
    dte_max: int = 40
    iv_rank_min: float = 40.0
    vix_min: float = 15.0
    vix_max: float = 25.0
    roll_delta_threshold: float = 0.35
    roll_dte_threshold: int = 10
    capital_base: float = 500_000.0
    dynamic_risk: bool = True

class ComputeRequest(BaseModel):
    positions: List[PositionIn]
    config: Optional[ConfigIn] = None
    mode: Optional[str] = Field(default="both", description="equal|greedy|both")
    watchlist: Optional[List[str]] = None

class ComputeResponse(BaseModel):
    summary_equal: Optional[Dict[str, Any]] = None
    table_equal: Optional[List[Dict[str, Any]]] = None
    signals_equal: Optional[List[Dict[str, Any]]] = None
    summary_greedy: Optional[Dict[str, Any]] = None
    table_greedy: Optional[List[Dict[str, Any]]] = None
    signals_greedy: Optional[List[Dict[str, Any]]] = None

async def compute_selling(req: ComputeRequest) -> ComputeResponse:
    cfg = Config(**(req.config.dict() if req.config else {}))

    # Build Position list
    pos_list: List[Position] = []
    for p in req.positions:
        pos_list.append(Position(
            ticker=p.ticker.upper(),
            price=p.price,
            strike=p.strike,
            delta=p.delta,
            dte=p.dte,
            premium=p.premium,
            iv_rank=p.iv_rank,
            vix=p.vix,
            selected=p.selected if p.selected is not None else True,
            assigned=p.assigned if p.assigned is not None else False,
            status=p.status or "Active",
            contracts=p.contracts or 0,
            notes=p.notes or ""
        ))

    # Optional watchlist filter
    if req.watchlist:
        wl = set([s.upper() for s in req.watchlist])
        pos_list = [p for p in pos_list if p.ticker.upper() in wl]

    resp = ComputeResponse()

    if req.mode in ("equal", "both", None):
        eq = allocate_contracts_equal(pos_list, cfg)
        resp.summary_equal = summarize(eq, cfg)
        resp.table_equal = to_table(eq, cfg)
        resp.signals_equal = collect_signals(eq, cfg)

    if req.mode in ("greedy", "both", None):
        gr = greedy_fill_by_risk(pos_list, cfg)
        resp.summary_greedy = summarize(gr, cfg)
        resp.table_greedy = to_table(gr, cfg)
        resp.signals_greedy = collect_signals(gr, cfg)

    return resp

# -----------------------------
# Monitor service (in-memory)
# -----------------------------
class MonitorStartRequest(BaseModel):
    positions: List[PositionIn]
    config: Optional[ConfigIn] = None
    mode: Optional[str] = Field(default="equal", description="equal|greedy|both")
    watchlist: Optional[List[str]] = None
    interval_seconds: int = 15

class MonitorDiffs(BaseModel):
    added: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []
    changed: List[Dict[str, Any]] = []

class MonitorSnapshot(BaseModel):
    running: bool
    last_run_at: Optional[str] = None
    interval_seconds: int = 15
    mode: str = "equal"
    summary: Optional[Dict[str, Any]] = None
    signals_current: List[Dict[str, Any]] = []
    signals_previous: List[Dict[str, Any]] = []
    diffs: MonitorDiffs = MonitorDiffs()
    cycles: int = 0

class _MonitorService:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._running: bool = False
        self._req: Optional[MonitorStartRequest] = None
        self._snapshot: MonitorSnapshot = MonitorSnapshot(running=False)
        self._prev_signals: List[Dict[str, Any]] = []
        self._cycles: int = 0

    def _key(self, s: Dict[str, Any]) -> Tuple:
        # Key fields to identify a unique signal across runs
        return (
            (s.get("ticker") or "").upper(),
            s.get("signal") or "",
            float(s.get("strike") or 0.0),
            int(s.get("dte") or 0),
        )

    def _diff(self, prev: List[Dict[str, Any]], cur: List[Dict[str, Any]]) -> MonitorDiffs:
        prev_map = {self._key(s): s for s in prev}
        cur_map = {self._key(s): s for s in cur}
        added, removed, changed = [], [], []
        for k, v in cur_map.items():
            if k not in prev_map:
                added.append(v)
            else:
                # Check relevant changes (contracts, premium, delta, dte)
                p = prev_map[k]
                if any([
                    (p.get("contracts") or 0) != (v.get("contracts") or 0),
                    float(p.get("premium") or 0.0) != float(v.get("premium") or 0.0),
                    float(p.get("delta") or 0.0) != float(v.get("delta") or 0.0),
                    int(p.get("dte") or 0) != int(v.get("dte") or 0),
                ]):
                    changed.append({"from": p, "to": v})
        for k, v in prev_map.items():
            if k not in cur_map:
                removed.append(v)
        return MonitorDiffs(added=added, removed=removed, changed=changed)

    async def _loop(self):
        assert self._req is not None
        interval = max(5, int(self._req.interval_seconds or 15))
        while self._running:
            try:
                # Build compute payload from start request
                comp_req = ComputeRequest(
                    positions=self._req.positions,
                    config=self._req.config,
                    mode=self._req.mode,
                    watchlist=self._req.watchlist,
                )
                res = await compute_selling(comp_req)
                # Pick signals + summary by mode preference
                mode = (self._req.mode or "equal").lower()
                if mode == "greedy":
                    signals = res.signals_greedy or []
                    summary = res.summary_greedy
                elif mode == "both":
                    # Merge both lists, remove duplicates by key (prefer greedy values)
                    signals = (res.signals_greedy or []) + (res.signals_equal or [])
                    uniq = {}
                    for s in signals:
                        uniq[self._key(s)] = s
                    signals = list(uniq.values())
                    summary = res.summary_greedy or res.summary_equal
                else:
                    signals = res.signals_equal or []
                    summary = res.summary_equal

                diffs = self._diff(self._prev_signals, signals)
                self._prev_signals = signals
                self._cycles += 1

                snap = MonitorSnapshot(
                    running=True,
                    last_run_at=datetime.utcnow().isoformat() + "Z",
                    interval_seconds=interval,
                    mode=mode,
                    summary=summary,
                    signals_current=signals,
                    signals_previous=self._snapshot.signals_current if self._snapshot.signals_current else [],
                    diffs=diffs,
                    cycles=self._cycles,
                )
                async with self._lock:
                    self._snapshot = snap
            except Exception as e:
                # Store error details in snapshot while keeping loop alive
                err_snap = MonitorSnapshot(
                    running=self._running,
                    last_run_at=datetime.utcnow().isoformat() + "Z",
                    interval_seconds=interval,
                    mode=(self._req.mode or "equal") if self._req else "equal",
                    summary={"error": str(e)},
                    signals_current=[],
                    signals_previous=self._prev_signals or [],
                    diffs=MonitorDiffs(),
                    cycles=self._cycles,
                )
                async with self._lock:
                    self._snapshot = err_snap
            # Sleep until next cycle
            await asyncio.sleep(interval)

    async def start(self, req: MonitorStartRequest) -> Dict[str, Any]:
        # Stop existing
        await self.stop()
        # Set state and launch
        self._req = req
        self._running = True
        self._prev_signals = []
        self._cycles = 0
        self._snapshot = MonitorSnapshot(running=True, interval_seconds=req.interval_seconds, mode=req.mode or "equal")
        self._task = asyncio.create_task(self._loop())
        return {"status": "started", "interval_seconds": req.interval_seconds, "mode": req.mode or "equal"}

    async def stop(self) -> Dict[str, Any]:
        if self._task and not self._task.done():
            self._running = False
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
        self._task = None
        self._running = False
        async with self._lock:
            self._snapshot.running = False
        return {"status": "stopped"}

    async def status(self) -> Dict[str, Any]:
        async with self._lock:
            snap = self._snapshot
        return {"status": "success", "data": snap.dict()}

# Singleton instance
monitor_service = _MonitorService()

# Facade functions for server.py
async def monitor_start(req: MonitorStartRequest) -> Dict[str, Any]:
    return await monitor_service.start(req)

async def monitor_stop() -> Dict[str, Any]:
    return await monitor_service.stop()

async def monitor_status() -> Dict[str, Any]:
    return await monitor_service.status()