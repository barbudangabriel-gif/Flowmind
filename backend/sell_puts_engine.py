from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Literal, Optional, Tuple
import math, json
from datetime import datetime

Status = Literal["Active", "Closed", "Assigned"]
Signal = Literal["SELL PUT", "ROLL", "COVERED CALL", ""]

@dataclass
class Config:
    # Praguri "sweet spot"
    delta_min: float = 0.25
    delta_max: float = 0.30
    dte_min: int = 20
    dte_max: int = 40
    iv_rank_min: float = 40.0
    vix_min: float = 15.0
    vix_max: float = 25.0

    # Praguri ROLL
    roll_delta_threshold: float = 0.35
    roll_dte_threshold: int = 10

    # Capital de bază
    capital_base: float = 500_000.0

    # Modul de alocare: True = delta-adjusted, False = cash-secured
    dynamic_risk: bool = True

@dataclass
class Position:
    ticker: str
    price: float
    strike: float
    delta: float
    dte: int
    premium: float # per contract (USD)
    iv_rank: float
    vix: float
    selected: bool = True
    assigned: bool = False
    status: Status = "Active"
    contracts: int = 0
    premium_paid_to_close: float = 0.0 # când roluiești/închizi
    notes: str = ""

    # ------- Derived metrics --------
    def capital_per_contract(self) -> float:
        return self.strike * 100.0

    def capital_blocked(self) -> float:
        """Capital blocat cash-secured pentru această poziție (numai Active)."""
        if self.status != "Active":
            return 0.0
        return self.contracts * self.capital_per_contract()

    def monthly_yield_pct(self) -> float:
        """Randament %/lună (numeric, 0..100), pe contract, scalat la DTE."""
        if self.dte <= 0 or self.capital_per_contract() <= 0:
            return 0.0
        return (self.premium / self.capital_per_contract()) * (30.0 / self.dte) * 100.0

    def risk_per_contract_delta_adjusted(self) -> float:
        """Risk economic per contract ajustat cu delta (proxy probabilitate assignment)."""
        return self.capital_per_contract() * max(0.0, min(1.0, self.delta))

    def eligible(self, cfg: Config) -> bool:
        return (
            (cfg.delta_min <= self.delta <= cfg.delta_max) and
            (cfg.dte_min <= self.dte <= cfg.dte_max) and
            (self.iv_rank >= cfg.iv_rank_min) and
            (cfg.vix_min <= self.vix <= cfg.vix_max)
        )

    def signal(self, cfg: Config) -> Signal:
        """PRIORITATE: COVERED CALL > ROLL > SELL PUT > ''"""
        if self.assigned:
            return "COVERED CALL"
        if (self.delta > cfg.roll_delta_threshold) or (self.dte < cfg.roll_dte_threshold):
            return "ROLL"
        if self.selected and self.eligible(cfg):
            return "SELL PUT"
        return ""

# ---------- Sumar portofoliu ----------
def summarize(positions: List[Position], cfg: Config) -> Dict[str, float]:
    active = [p for p in positions if p.status == "Active"]
    closed = [p for p in positions if p.status == "Closed"]
    assigned = [p for p in positions if p.status == "Assigned" or p.assigned]

    capital_active = sum(p.capital_blocked() for p in active)
    capital_released = sum(p.contracts * p.capital_per_contract() for p in closed)
    capital_in_equity = sum(p.contracts * p.capital_per_contract() for p in assigned)

    risk_economic = sum(p.risk_per_contract_delta_adjusted() * p.contracts for p in active)

    signals_count = {
        "SELL PUT": sum(1 for p in positions if p.signal(cfg) == "SELL PUT"),
        "ROLL": sum(1 for p in positions if p.signal(cfg) == "ROLL"),
        "COVERED CALL": sum(1 for p in positions if p.signal(cfg) == "COVERED CALL"),
    }

    return {
        "capital_base": cfg.capital_base,
        "capital_active_blocked": capital_active,
        "capital_released": capital_released,
        "capital_in_equity": capital_in_equity,
        "capital_available_cash_secured": max(0.0, cfg.capital_base - capital_active),
        "risk_economic_active": risk_economic,
        "risk_budget": cfg.capital_base,
        "risk_headroom": max(0.0, cfg.capital_base - risk_economic),
        "count_active": len(active),
        "count_closed": len(closed),
        "count_assigned": len(assigned),
        **{f"signals_{k}": v for k, v in signals_count.items()}
    }

# ---------- Alocare ----------
def allocate_contracts_equal(
    candidates: List[Position],
    cfg: Config,
    per_symbol_cap: Optional[float] = None
) -> List[Position]:
    """
    Alocă contracte per simbol folosind fie delta-adjusted (dynamic_risk=True),
    fie cash-secured. per_symbol_cap default = capital_base / nr. simboluri.
    Returnează o listă nouă cu 'contracts' setat.
    """
    if not candidates:
        return []

    n = len(candidates)
    per_cap = per_symbol_cap if per_symbol_cap is not None else cfg.capital_base / n

    result: List[Position] = []
    for p in candidates:
        pc = Position(**asdict(p)) # clone
        cap_per_contract = pc.capital_per_contract()

        if cfg.dynamic_risk:
            risk_per_contract = pc.risk_per_contract_delta_adjusted()
            pc.contracts = 0 if risk_per_contract <= 0 else max(0, math.floor(per_cap / risk_per_contract))
        else:
            pc.contracts = 0 if cap_per_contract <= 0 else max(0, math.floor(per_cap / cap_per_contract))

        result.append(pc)
    return result

def greedy_fill_by_risk(candidates: List[Position], cfg: Config) -> List[Position]:
    """
    Umple bugetul (risk sau capital) în stil greedy, alegând pe rând 1 contract
    pe simbol, maximizând premium / unitate_risc (delta-adjusted) sau / capital (cash-secured).
    """
    pool = [Position(**asdict(p)) for p in candidates]
    for p in pool:
        p.contracts = 0

    budget = cfg.capital_base

    def unit(p: Position) -> float:
        return p.risk_per_contract_delta_adjusted() if cfg.dynamic_risk else p.capital_per_contract()

    def efficiency(p: Position) -> float:
        denom = unit(p)
        return (p.premium / denom) if denom > 0 else 0.0

    while True:
        pool_sorted = sorted(pool, key=efficiency, reverse=True)
        placed = False
        for p in pool_sorted:
            u = unit(p)
            if u <= 0:
                continue
            current = sum(x.contracts * unit(x) for x in pool)
            if current + u <= budget:
                p.contracts += 1
                placed = True
                break
        if not placed:
            break

    return pool

# ---------- Tabele / JSON ----------
def to_table(positions: List[Position], cfg: Config) -> List[Dict]:
    """Tablou JSON-friendly, cu semnale și metrici principale."""
    rows = []
    for p in positions:
        rows.append({
            "ticker": p.ticker,
            "price": p.price,
            "strike": p.strike,
            "delta": p.delta,
            "dte": p.dte,
            "premium": p.premium,
            "iv_rank": p.iv_rank,
            "vix": p.vix,
            "selected": p.selected,
            "assigned": p.assigned,
            "status": p.status,
            "contracts": p.contracts,
            "eligible": p.eligible(cfg),
            "signal": p.signal(cfg),
            "capital_per_contract": p.capital_per_contract(),
            "capital_blocked": p.capital_blocked(),
            "risk_per_contract": p.risk_per_contract_delta_adjusted(),
            "monthly_yield_pct": p.monthly_yield_pct(),
            "notes": p.notes,
        })
    return rows

# ---------- PnL & lifecycle ----------
def pnl_sell_put(premium_received_per_contract: float, contracts: int) -> float:
    """PnL realizat la vânzarea inițială (cash in)."""
    return premium_received_per_contract * 100.0 * contracts

def pnl_close_put(premium_paid_to_close_per_contract: float, contracts: int) -> float:
    """PnL realizat la închiderea prin buy-to-close (cash out, negativ)."""
    return - premium_paid_to_close_per_contract * 100.0 * contracts

def close_position(p: Position, premium_paid_to_close_per_contract: float) -> float:
    """
    Închide poziția (status=Closed). Returnează PnL realizat al închiderii (cash out).
    Notă: PnL net al ciclului = +premium inițial (cash in) + acest close (cash out).
    """
    p.premium_paid_to_close = premium_paid_to_close_per_contract
    realized = pnl_close_put(premium_paid_to_close_per_contract, p.contracts)
    p.status = "Closed"
    return realized

def roll_position(old: Position,
                  new_strike: float,
                  new_dte: int,
                  new_delta: float,
                  new_premium: float) -> Tuple[Position, float]:
    """
    ROLL: închide vechea poziție (buy-to-close) și deschide una nouă (same ticker).
    Returnează (new_position, realized_pnl_from_close).
    Notă: PnL net pe roll = premium vechi + (-cost BTC) + premium nou.
    """
    realized_close = close_position(old, premium_paid_to_close_per_contract=old.premium)
    new_pos = Position(
        ticker=old.ticker,
        price=old.price, # actualizează cu live dacă ai
        strike=new_strike,
        delta=new_delta,
        dte=new_dte,
        premium=new_premium,
        iv_rank=old.iv_rank,
        vix=old.vix,
        selected=old.selected,
        assigned=False,
        status="Active",
        contracts=old.contracts,
        notes=f"roll from {old.strike} -> {new_strike}"
    )
    return new_pos, realized_close

def assign_position(p: Position) -> None:
    """Marchează poziția ca Assigned (ai primit acțiunile)."""
    p.assigned = True
    p.status = "Assigned"

# ---------- Export semnale ----------
def collect_signals(positions: List[Position], cfg: Config) -> List[Dict]:
    """Listă cu semnale active (pentru export / orchestrare)."""
    out = []
    for p in positions:
        s = p.signal(cfg)
        if not s:
            continue
        out.append({
            "ticker": p.ticker,
            "signal": s,
            "contracts": p.contracts,
            "strike": p.strike,
            "dte": p.dte,
            "delta": p.delta,
            "premium": p.premium,
            "notes": p.notes
        })
    return out

def export_signals_json(positions: List[Position], cfg: Config, path: str = "signals.json") -> None:
    signals = collect_signals(positions, cfg)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "signals": signals
        }, f, indent=2)