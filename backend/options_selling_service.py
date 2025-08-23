from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import os

from sell_puts_engine import (
    Config, Position, allocate_contracts_equal, greedy_fill_by_risk,
    summarize, to_table, collect_signals
)

# Optional Mongo logging (simulated analysis source)
try:
    from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
except Exception:  # pragma: no cover
    AsyncIOMotorClient = None  # type: ignore

_MONGO_URL = os.environ.get("MONGO_URL")
_DB_NAME = os.environ.get("DB_NAME")
_mongo_client = None
_db = None
if AsyncIOMotorClient and _MONGO_URL and _DB_NAME:
    try:
        _mongo_client = AsyncIOMotorClient(_MONGO_URL)
        _db = _mongo_client[_DB_NAME]
    except Exception:
        _db = None

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

# --------------- Covered Calls ---------------
class CCConfigIn(BaseModel):
    cc_delta_min: float = 0.15
    cc_delta_max: float = 0.30
    cc_dte_min: int = 20
    cc_dte_max: int = 40
    cc_roll_delta_threshold: float = 0.35
    cc_roll_dte_threshold: int = 10
    cc_take_profit_remaining_threshold: float = 0.30  # 30% remaining => 70% captured

class CCCandidateCall(BaseModel):
    strike: float
    delta: float
    dte: int
    premium: float

class CCOpenState(BaseModel):
    delta: float
    dte: int
    premium_sold: float
    premium_mark: float

class CCInput(BaseModel):
    ticker: str
    shares_owned: int
    open_cc_contracts: int = 0
    candidate_call: Optional[CCCandidateCall] = None
    open_cc_state: Optional[CCOpenState] = None

class ComputeRequest(BaseModel):
    positions: List[PositionIn]
    config: Optional[ConfigIn] = None
    mode: Optional[str] = Field(default="both", description="equal|greedy|both")
    watchlist: Optional[List[str]] = None
    # New: Covered Calls
    cc_config: Optional[CCConfigIn] = None
    cc_inputs: Optional[List[CCInput]] = None

class ComputeResponse(BaseModel):
    summary_equal: Optional[Dict[str, Any]] = None
    table_equal: Optional[List[Dict[str, Any]]] = None
    signals_equal: Optional[List[Dict[str, Any]]] = None
    summary_greedy: Optional[Dict[str, Any]] = None
    table_greedy: Optional[List[Dict[str, Any]]] = None
    signals_greedy: Optional[List[Dict[str, Any]]] = None
    # CC outputs
    cc_summary: Optional[Dict[str, Any]] = None
    cc_table: Optional[List[Dict[str, Any]]] = None
    cc_signals: Optional[List[Dict[str, Any]]] = None

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

    # ------- Covered Calls logic (independent of engine) -------
    cc_cfg = req.cc_config or CCConfigIn()
    cc_inputs = req.cc_inputs or []
    if cc_inputs:
        cc_signals: List[Dict[str, Any]] = []
        cc_rows: List[Dict[str, Any]] = []
        lots_total = 0
        lots_used = 0
        yields: List[float] = []

        for item in cc_inputs:
            sym = (item.ticker or "").upper()
            lots_avail = max(0, (item.shares_owned // 100) - int(item.open_cc_contracts or 0))
            lots_total += (item.shares_owned // 100)

            # SELL CALL candidate
            if item.candidate_call and lots_avail > 0:
                c = item.candidate_call
                if (cc_cfg.cc_delta_min <= c.delta <= cc_cfg.cc_delta_max) and (cc_cfg.cc_dte_min <= c.dte <= cc_cfg.cc_dte_max):
                    monthly_y = 0.0
                    if c.dte > 0 and c.strike > 0:
                        monthly_y = (c.premium / (c.strike * 100.0)) * (30.0 / c.dte) * 100.0
                    contracts = lots_avail
                    lots_used += contracts
                    yields.append(monthly_y)
                    sig = {
                        "ticker": sym,
                        "signal": "SELL CALL",
                        "contracts": contracts,
                        "strike": c.strike,
                        "dte": c.dte,
                        "delta": c.delta,
                        "premium": c.premium,
                        "notes": f"lots_avail={lots_avail}",
                    }
                    cc_signals.append(sig)
                    cc_rows.append({**sig, "monthly_yield_pct": monthly_y})

            # ROLL CC / TAKE PROFIT on existing
            if item.open_cc_state and (item.open_cc_contracts or 0) > 0:
                s = item.open_cc_state
                # ROLL CC condition
                if (s.delta > cc_cfg.cc_roll_delta_threshold) or (s.dte < cc_cfg.cc_roll_dte_threshold):
                    sig = {
                        "ticker": sym,
                        "signal": "ROLL CC",
                        "contracts": int(item.open_cc_contracts or 0),
                        "strike": None,
                        "dte": s.dte,
                        "delta": s.delta,
                        "premium": s.premium_mark,
                        "notes": "roll conditions met",
                    }
                    cc_signals.append(sig)
                    cc_rows.append({**sig, "monthly_yield_pct": None})
                # TAKE PROFIT condition
                if s.premium_sold > 0:
                    rem_ratio = (s.premium_mark or 0.0) / float(s.premium_sold)
                    if rem_ratio <= cc_cfg.cc_take_profit_remaining_threshold:
                        sig = {
                            "ticker": sym,
                            "signal": "TAKE PROFIT",
                            "contracts": int(item.open_cc_contracts or 0),
                            "strike": None,
                            "dte": s.dte,
                            "delta": s.delta,
                            "premium": s.premium_mark,
                            "notes": f"remaining={rem_ratio:.2f}",
                        }
                        cc_signals.append(sig)
                        cc_rows.append({**sig, "monthly_yield_pct": None})

        cc_summary = {
            "lots_total": lots_total,
            "lots_used": lots_used,
            "lots_free": max(0, lots_total - lots_used),
            "monthly_yield_avg": (sum(yields) / len(yields)) if yields else 0.0,
            "signals_count": {
                "SELL CALL": sum(1 for s in cc_signals if s["signal"] == "SELL CALL"),
                "ROLL CC": sum(1 for s in cc_signals if s["signal"] == "ROLL CC"),
                "TAKE PROFIT": sum(1 for s in cc_signals if s["signal"] == "TAKE PROFIT"),
            },
        }
        resp.cc_summary = cc_summary
        resp.cc_table = cc_rows
        resp.cc_signals = cc_signals

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
    # Covered Calls
    cc_config: Optional[CCConfigIn] = None
    cc_inputs: Optional[List[CCInput]] = None

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

async def _log_snapshot_to_mongo(snap: MonitorSnapshot, cfg: Optional[ConfigIn]):
    if _db is None:
        return
    try:
        doc = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "mode": snap.mode,
            "interval_seconds": snap.interval_seconds,
            "summary": snap.summary or {},
            "signals": snap.signals_current or [],
            "diffs": {
                "added": snap.diffs.added if snap.diffs else [],
                "removed": snap.diffs.removed if snap.diffs else [],
                "changed": snap.diffs.changed if snap.diffs else [],
            },
            "cycles": snap.cycles,
            "config": cfg.dict() if cfg else {},
        }
        await _db["options_monitor_snapshots"].insert_one(doc)
    except Exception:
        # Best effort logging; do not break monitor
        pass

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
                    cc_config=self._req.cc_config,
                    cc_inputs=self._req.cc_inputs,
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

                # Merge CC signals into signal stream
                if res.cc_signals:
                    signals = list(signals) + list(res.cc_signals)

                diffs = self._diff(self._prev_signals, signals)
                self._prev_signals = signals
                self._cycles += 1

                snap = MonitorSnapshot(
                    running=True,
                    last_run_at=datetime.utcnow().isoformat() + "Z",
                    interval_seconds=interval,
                    mode=mode,
                    summary={**(summary or {}), "cc_summary": res.cc_summary or {}},
                    signals_current=signals,
                    signals_previous=self._snapshot.signals_current if self._snapshot.signals_current else [],
                    diffs=diffs,
                    cycles=self._cycles,
                )
                async with self._lock:
                    self._snapshot = snap

                # Async log to Mongo (best effort)
                await _log_snapshot_to_mongo(snap, self._req.config)
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
            except asyncio.CancelledError:
                # This is expected when cancelling a task
                pass
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

# --------- Analysis (simulated from monitor logs) ---------
class AnalysisQuery(BaseModel):
    range: Optional[str] = Field(default="3M", description="1M|3M|6M|1Y|ALL")
    strategies: Optional[List[str]] = None  # e.g., ["SELL PUT","ROLL","SELL CALL","ROLL CC","TAKE PROFIT","COVERED CALL"]
    ticker: Optional[str] = None
    fill: Optional[str] = Field(default="mid", description="mid|bid|last (informational)")
    slippage: float = 0.05  # $ per contract per side
    commission: float = 0.65  # $ per contract per side

async def options_analysis(q: AnalysisQuery) -> Dict[str, Any]:
    if _db is None:
        return {"kpi": {}, "series": [], "metrics": {}, "notes": "analysis disabled: no Mongo connection"}

    # Time window
    now = datetime.utcnow()
    ranges = {
        "1M": now - timedelta(days=30),
        "3M": now - timedelta(days=90),
        "6M": now - timedelta(days=180),
        "1Y": now - timedelta(days=365),
        "ALL": datetime(1970,1,1),
    }
    start = ranges.get((q.range or "3M").upper(), ranges["3M"])

    # Fetch snapshots
    cur = _db["options_monitor_snapshots"].find({"ts": {"$gte": start.isoformat() + "Z"}}).sort("ts", 1)
    snaps: List[Dict[str, Any]] = [s async for s in cur]

    # Trade simulation stores
    open_cc: Dict[str, List[Dict[str, Any]]] = {}  # per ticker list of open calls
    open_put: Dict[str, List[Dict[str, Any]]] = {} # per ticker list of short puts
    closed_trades: List[Dict[str, Any]] = []

    def record_open(sym: str, book: Dict[str, List[Dict[str, Any]]], sig: Dict[str, Any]):
        book.setdefault(sym, [])
        book[sym].append({
            "opened_at": sig.get("_ts"),
            "contracts": int(sig.get("contracts") or 0),
            "premium_sold": float(sig.get("premium") or 0.0),
            "strike": sig.get("strike"),
            "dte": sig.get("dte"),
            "delta": sig.get("delta"),
        })

    def close_from_open(sym: str, book: Dict[str, List[Dict[str, Any]]], close_sig: Dict[str, Any], reason: str):
        lst = book.get(sym, [])
        if not lst:
            return
        # FIFO close
        op = lst.pop(0)
        btc = float(close_sig.get("premium") or 0.0)
        contracts = int(close_sig.get("contracts") or op.get("contracts") or 0)
        # Costs (per contract, both sides)
        costs = 2.0 * (q.commission + q.slippage)
        pnl_per_contract = (op["premium_sold"] - btc) - costs
        pnl_total = pnl_per_contract * contracts
        ror = 0.0
        try:
            if op.get("strike"):
                ror = (op["premium_sold"] / (float(op["strike"]) * 100.0)) * 100.0
        except Exception:
            ror = 0.0
        closed_trades.append({
            "ticker": sym,
            "strategy": reason,
            "opened_at": op["opened_at"],
            "closed_at": close_sig.get("_ts"),
            "contracts": contracts,
            "pnl": pnl_total,
            "ror_pct": ror,
        })

    # Iterate snapshots and build events using diffs.added
    ticker_filter = (q.ticker or "").upper().strip() if q.ticker else None
    strategy_set = set([st.upper() for st in (q.strategies or [])]) if q.strategies else None

    for s in snaps:
        ts = s.get("ts")
        diffs = (s.get("diffs") or {})
        added = diffs.get("added") or []
        for sig in added:
            sig["_ts"] = ts
            sig_type = (sig.get("signal") or "").upper()
            sym = (sig.get("ticker") or "").upper()
            if ticker_filter and sym != ticker_filter:
                continue
            if strategy_set and sig_type not in strategy_set:
                continue
            if sig_type == "SELL CALL":
                record_open(sym, open_cc, sig)
            elif sig_type in ("TAKE PROFIT", "ROLL CC"):
                close_from_open(sym, open_cc, sig, sig_type)
            elif sig_type == "SELL PUT":
                record_open(sym, open_put, sig)
            elif sig_type == "ROLL":
                close_from_open(sym, open_put, sig, sig_type)
            # Optionally: handle COVERED CALL elsewhere

    # KPI & metrics
    wins = sum(1 for t in closed_trades if t["pnl"] > 0)
    losses = sum(1 for t in closed_trades if t["pnl"] <= 0)
    closed_pl = sum(t["pnl"] for t in closed_trades)
    ror_avg = (sum(t.get("ror_pct", 0.0) for t in closed_trades) / len(closed_trades)) if closed_trades else 0.0
    profit_factor = (sum(t["pnl"] for t in closed_trades if t["pnl"] > 0) / max(1e-9, abs(sum(t["pnl"] for t in closed_trades if t["pnl"] &lt; 0)))) if closed_trades else 0.0

    # Series cumulative
    series = []
    cum = 0.0
    for t in sorted(closed_trades, key=lambda x: x["closed_at"] or ""):
        cum += t["pnl"]
        series.append({"ts": t["closed_at"], "xIndex": len(series), "cum_closed_pl": cum})

    result = {
        "kpi": {
            "closed_pl": closed_pl,
            "positions_closed": len(closed_trades),
            "win_rate": (wins / len(closed_trades) * 100.0) if closed_trades else 0.0,
            "return_on_risk_avg": ror_avg,
        },
        "metrics": {
            "profit_factor": profit_factor,
            "wins": wins,
            "losses": losses,
            "avg_pnl": (closed_pl / len(closed_trades)) if closed_trades else 0.0,
            "avg_ror": ror_avg,
        },
        "series": series,
        "closed_trades": closed_trades[-200:],
        "assumptions": {
            "fill": q.fill,
            "slippage": q.slippage,
            "commission": q.commission,
            "range": q.range,
            "ticker": q.ticker,
            "strategies": list(strategy_set) if strategy_set else None,
        }
    }
    return result

# Facade functions for server.py
async def monitor_start(req: MonitorStartRequest) -> Dict[str, Any]:
    return await monitor_service.start(req)

async def monitor_stop() -> Dict[str, Any]:
    return await monitor_service.stop()

async def monitor_status() -> Dict[str, Any]:
    return await monitor_service.status()