from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timezone
import os
from services.uw_flow import (
    live_flow,
    historical_flow,
    summary_from_live,
    news_flow,
    congress_flow,
    insiders_flow,
)

router = APIRouter(prefix="/flow", tags=["flow"])

# Environment flags
UW_LIVE = os.getenv("UW_LIVE", "0") == "1"
UW_MIN_PREMIUM = int(os.getenv("UW_MIN_PREMIUM", "25000"))


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_builder_link(row):
    """Generate deep-link to Builder for a flow row"""
    try:
        symbol = row.get("symbol", "")
        strike = row.get("strike", "")
        expiry = row.get("expiry", "")
        kind = row.get("kind", "").lower()

        if all([symbol, strike, expiry, kind]):
            return (
                f"/builder?symbol={symbol}&strike={strike}&expiry={expiry}&type={kind}"
            )
        return "/builder"
    except:
        return "/builder"


# ---------- DEMO DATA ----------
def demo_summary(limit=24):
    syms = [
        "AAPL",
        "TSLA",
        "NVDA",
        "QQQ",
        "SPY",
        "META",
        "AMZN",
        "GOOGL",
        "IWM",
        "MSFT",
        "AMD",
        "NFLX",
        "SHOP",
        "BA",
        "PLTR",
        "COIN",
        "SMCI",
        "AVGO",
        "MU",
        "CRM",
        "DIS",
        "UBER",
        "JPM",
        "CVX",
    ]
    out = []
    for i, s in enumerate(syms[:limit]):
        bull = 180_000 + 9_000 * i
        bear = 95_000 + 6_000 * i
        out.append(
            {
                "symbol": s,
                "bull_premium": bull,
                "bear_premium": bear,
                "net_premium": bull - bear,
                "trades": 1 + (i % 4),
                "sweeps_pct": 0.35 + (i % 3) * 0.1,
                "blocks_pct": 0.10 + (i % 2) * 0.05,
            }
        )
    return out


def demo_live(symbol: str, min_premium: int):
    """Demo live flow data to prevent UI blocking"""
    base = 260 if symbol == "TSLA" else 100
    rows = []
    for k in range(13):
        kind = "CALL" if k % 2 == 0 else "PUT"
        side = "BUY" if k % 3 != 0 else "SELL"
        qty = 100 * (1 + k % 4)
        price = round(0.85 + 0.15 * k, 2)
        premium = qty * price
        if premium < min_premium:
            premium = min_premium + 1000 * k
        rows.append(
            {
                "ts": now_iso(),
                "symbol": symbol,
                "side": side,
                "kind": kind,
                "expiry": "2025-09-19",
                "strike": base + (k - 6) * 5,
                "qty": qty,
                "price": price,
                "premium": premium,
                "isSweep": k % 2 == 0,
                "isBlock": k % 5 == 0,
                "venue": "CBOE",
                "odte": False,
                "note": "DEMO",
            }
        )
    return rows


def _filters(
    tickers: Optional[str] = None,
    side: Optional[str] = None,
    kinds: Optional[str] = None,
    opt_types: Optional[str] = None,
    otm: Optional[bool] = None,
    vol_gt_oi: Optional[bool] = None,
    above_ask_below_bid: Optional[bool] = None,
    price_op: Optional[str] = None,
    price_val: Optional[float] = None,
    chance_op: Optional[str] = None,
    chance_val: Optional[float] = None,
    min_dte: Optional[int] = None,
    max_dte: Optional[int] = None,
):
    csv = lambda x: [s.strip() for s in x.split(",") if s.strip()] if x else None
    d = {
        "tickers": csv(tickers),
        "side": csv(side),
        "kinds": csv(kinds),
        "opt_types": csv(opt_types),
        "otm": otm,
        "vol_gt_oi": vol_gt_oi,
        "above_ask_below_bid": above_ask_below_bid,
        "price_op": price_op,
        "price_val": price_val,
        "chance_op": chance_op,
        "chance_val": chance_val,
        "min_dte": min_dte,
        "max_dte": max_dte,
    }
    return d


# ---------- Routes ----------
@router.get("/summary")
async def flow_summary(limit: int = Query(24), minPremium: int = Query(UW_MIN_PREMIUM)):
    """Flow summary with guaranteed fallback and mode detection"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            data = summary_from_live()
            if not data or not isinstance(data, list):
                data = demo_summary(limit)
                mode = "DEMO"
        else:
            data = demo_summary(limit)
    except Exception as e:
        print(f"Flow summary error (using demo): {e}")
        data = demo_summary(limit)
        mode = "DEMO"

    items = data[:limit] if isinstance(data, list) else demo_summary(limit)
    return {"mode": mode, "items": items, "ts": now_iso()}


@router.get("/live")
async def flow_live(
    symbol: str = Query("TSLA"),
    minPremium: int = Query(UW_MIN_PREMIUM),
    cursor: Optional[str] = Query(None),
):
    """Live flow with guaranteed fallback, mode detection, and deep-linking"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            rows = live_flow(
                _filters(
                    tickers=symbol,
                    side=None,
                    kinds=None,
                    opt_types=None,
                    otm=None,
                    vol_gt_oi=None,
                    above_ask_below_bid=None,
                    price_op=None,
                    price_val=None,
                    chance_op=None,
                    chance_val=None,
                    min_dte=None,
                    max_dte=None,
                )
            )
            if not rows or not isinstance(rows, list):
                rows = demo_live(symbol, minPremium)
                mode = "DEMO"
        else:
            rows = demo_live(symbol, minPremium)
    except Exception as e:
        print(f"Live flow error for {symbol} (using demo): {e}")
        rows = demo_live(symbol, minPremium)
        mode = "DEMO"

    # Add deep-link to Builder for each row
    items = rows if isinstance(rows, list) else demo_live(symbol, minPremium)
    for r in items:
        r["linkBuilder"] = make_builder_link(r)

    return {"mode": mode, "items": items, "next": None, "ts": now_iso()}


@router.get("/historical")
async def flow_historical(
    symbol: str = Query("TSLA"),
    days: int = Query(7),
    minPremium: int = Query(UW_MIN_PREMIUM),
):
    """Historical flow with fallback"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            data = historical_flow({})
            if not data:
                data = demo_live(symbol, minPremium)[:10]  # Smaller historical set
                mode = "DEMO"
        else:
            data = demo_live(symbol, minPremium)[:10]
    except Exception:
        data = demo_live(symbol, minPremium)[:10]
        mode = "DEMO"

    return {"mode": mode, "items": data, "ts": now_iso()}


@router.get("/news")
async def flow_news(tickers: Optional[str] = Query(None)):
    """News flow with fallback"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            data = news_flow(tickers.split(",") if tickers else [])
            if not data:
                data = []
                mode = "DEMO"
        else:
            data = []
    except Exception:
        data = []
        mode = "DEMO"

    return {"mode": mode, "items": data, "ts": now_iso()}


@router.get("/congress")
async def flow_congress(tickers: Optional[str] = Query(None)):
    """Congress flow with fallback"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            data = congress_flow(tickers.split(",") if tickers else [])
            if not data:
                data = []
                mode = "DEMO"
        else:
            data = []
    except Exception:
        data = []
        mode = "DEMO"

    return {"mode": mode, "items": data, "ts": now_iso()}


@router.get("/insiders")
async def flow_insiders(tickers: Optional[str] = Query(None)):
    """Insiders flow with fallback"""
    mode = "LIVE" if UW_LIVE else "DEMO"
    try:
        if UW_LIVE:
            data = insiders_flow(tickers.split(",") if tickers else [])
            if not data:
                data = []
                mode = "DEMO"
        else:
            data = []
    except Exception:
        data = []
        mode = "DEMO"

    return {"mode": mode, "items": data, "ts": now_iso()}
