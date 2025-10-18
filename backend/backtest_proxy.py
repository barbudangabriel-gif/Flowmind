"""
FlowMind - Backtest in Signal v0.3
Adds DOUBLE_DIAGONAL proxy support
"""

import statistics as stats
from typing import List
from dataclasses import dataclass

@dataclass
class Signal:
    strategy: str
    underlying: str
    dte: int
    width_ratio_em: float = 1.0
    ivr: float = 0.0
    term_front: int = None
    term_back: int = None
    exit_tp_pct: float = 0.5
    exit_sl_mult: float = 1.5

@dataclass
class BacktestSummary:
    key: str
    n: int
    win_rate: float
    avg_pnl: float
    median_pnl: float
    max_dd: float
    pf: float
    expectancy: float
    hold_med_days: float
    notes: List[str]

@dataclass
class HistoryBar:
    c: float # close
    iv30: float # 30-day IV

def canonical_key(sig: Signal, horizon_years: int = 2) -> str:
    """v3 - include front/back pentru calendar strategies"""
    import hashlib
    import json

    blob = {
        "v": 3, # Updated version
        "strategy": sig.strategy,
        "U": sig.underlying,
        "dte": round(sig.dte),
        "ivr_bucket": int(sig.ivr // 5 * 5),
        "front": sig.term_front,
        "back": sig.term_back,
        "tp": sig.exit_tp_pct,
        "sl": sig.exit_sl_mult,
        "horizon_y": horizon_years,
    }
    s = json.dumps(blob, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()[:16]

async def get_history(symbol: str, days: int = 504) -> List[HistoryBar]:
    """Stub history data"""
    return [HistoryBar(c=250.0 + i * 0.1, iv30=0.25) for i in range(days)]

async def proxy_backtest_double_diagonal(
    sig: Signal, horizon_years: int = 2
) -> BacktestSummary:
    """Double diagonal backtest proxy"""
    front = int(sig.term_front or 14)
    back = int(sig.term_back or 45)

    if back <= front or front <= 0:
        return BacktestSummary(
            key=canonical_key(sig, horizon_years),
            n=0,
            win_rate=0,
            avg_pnl=0,
            median_pnl=0,
            max_dd=0,
            pf=0,
            expectancy=0,
            hold_med_days=0,
            notes=["invalid term structure"],
        )

    hist = await get_history(sig.underlying, days=252 * horizon_years)
    if len(hist) < front + 5:
        return BacktestSummary(
            key=canonical_key(sig, horizon_years),
            n=0,
            win_rate=0,
            avg_pnl=0,
            median_pnl=0,
            max_dd=0,
            pf=0,
            expectancy=0,
            hold_med_days=0,
            notes=["Insufficient history"],
        )

    results = []
    holds = []
    equity = 0.0
    max_eq = 0.0
    dd = 0.0

    for i in range(len(hist) - front - 1):
        S = hist[i].c
        em = S * hist[i].iv30 * (front / 365.0) ** 0.5
        debit = max(0.5, 0.20 * em) # Higher debit than calendar
        tp = (sig.exit_tp_pct or 0.35) * debit
        sl = (sig.exit_sl_mult or 1.0) * debit

        # Tighter channel for double diagonal
        lb = S - 0.7 * em
        ub = S + 0.7 * em

        hit = False
        for j in range(1, front + 1):
            bar = hist[i + j]
            if (bar.c > lb) and (bar.c < ub): # Stay în channel
                results.append(+tp)
                holds.append(j)
                hit = True
                break
            if bar.c >= S + em or bar.c <= S - em: # Breach
                results.append(-sl)
                holds.append(j)
                hit = True
                break

        if not hit:
            # At expiration
            end_S = hist[i + front].c
            drift = abs(end_S - S)
            pnl = +0.25 * debit if drift <= 0.6 * em else -0.5 * debit
            results.append(pnl)
            holds.append(front)

        equity += results[-1]
        max_eq = max(max_eq, equity)
        dd = min(dd, equity - max_eq)

    if not results:
        return BacktestSummary(
            key=canonical_key(sig, horizon_years),
            n=0,
            win_rate=0,
            avg_pnl=0,
            median_pnl=0,
            max_dd=0,
            pf=0,
            expectancy=0,
            hold_med_days=0,
            notes=["No trades generated"],
        )

    wins = [x for x in results if x > 0]
    losses = [x for x in results if x <= 0]
    pf = (sum(wins) / max(1e-9, abs(sum(losses)))) if losses else float("inf")

    return BacktestSummary(
        key=canonical_key(sig, horizon_years),
        n=len(results),
        win_rate=len(wins) / len(results),
        avg_pnl=sum(results) / len(results),
        median_pnl=stats.median(results),
        max_dd=abs(dd),
        pf=pf,
        expectancy=sum(results) / len(results),
        hold_med_days=stats.median(holds) if holds else 0,
        notes=["proxy/eod", "double_diagonal", f"front={front} back={back}"],
    )
