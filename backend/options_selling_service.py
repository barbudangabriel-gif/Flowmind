from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sell_puts_engine import (
    Config, Position, allocate_contracts_equal, greedy_fill_by_risk,
    summarize, to_table, collect_signals
)

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