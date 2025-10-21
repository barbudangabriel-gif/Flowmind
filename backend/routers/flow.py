import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query

from services.uw_flow import (
    congress_flow,
    historical_flow,
    insiders_flow,
    live_flow,
    news_flow,
    summary_from_live,
)

logger = logging.getLogger(__name__)

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
    except (KeyError, AttributeError, TypeError) as e:
        logger.warning(f"Failed to build link from row: {e}")
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
    def csv(x):
        return [s.strip() for s in x.split(",") if s.strip()] if x else None

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


# ============================================================================
# NEW ENDPOINTS - 2025-10-13 Extension
# ============================================================================


@router.get("/market-movers")
async def market_movers():
    """
    Get market movers (top gainers, losers, most active)

    Returns:
    {
        "gainers": [...],
        "losers": [...],
        "most_active": [...]
    }
    """
    from unusual_whales_service import UnusualWhalesService

    try:
        service = UnusualWhalesService()
        data = await service.get_market_movers()
        return {"status": "success", "data": data, "timestamp": now_iso()}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": {"gainers": [], "losers": [], "most_active": []},
            "timestamp": now_iso(),
        }


@router.get("/congress-trades")
async def congress_trades(
    ticker: Optional[str] = Query(None),
    politician: Optional[str] = Query(None),
    party: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get congressional trading activity

    Query params:
    - ticker: Filter by stock symbol
    - politician: Filter by politician name
    - party: Filter by party (D, R, I)
    - transaction_type: BUY, SELL, or EXCHANGE
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - limit: Max results (1-500, default 100)
    """
    from unusual_whales_service import UnusualWhalesService

    try:
        service = UnusualWhalesService()

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        data = await service.get_congress_trades(
            ticker=ticker,
            politician=politician,
            party=party,
            transaction_type=transaction_type,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
        )

        return {
            "status": "success",
            "data": data,
            "count": len(data),
            "timestamp": now_iso(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "data": [], "timestamp": now_iso()}


@router.get("/dark-pool")
async def dark_pool(
    ticker: Optional[str] = Query(None),
    min_volume: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get dark pool activity (off-exchange trades)

    Query params:
    - ticker: Filter by symbol
    - min_volume: Minimum share volume threshold
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - limit: Max results (1-500, default 100)
    """
    from unusual_whales_service import UnusualWhalesService

    try:
        service = UnusualWhalesService()

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        data = await service.get_dark_pool(
            ticker=ticker,
            min_volume=min_volume,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
        )

        return {
            "status": "success",
            "data": data,
            "count": len(data),
            "timestamp": now_iso(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "data": [], "timestamp": now_iso()}


@router.get("/institutional/{ticker}")
async def institutional_holdings(
    ticker: str,
    quarter: Optional[str] = Query(None, description="Quarter (e.g., 2025Q3)"),
):
    """
    Get institutional holdings (13F filings) for a ticker

    Path params:
    - ticker: Stock symbol (required)

    Query params:
    - quarter: Quarter filter (e.g., "2025Q3", defaults to latest)
    """
    from unusual_whales_service import UnusualWhalesService

    try:
        service = UnusualWhalesService()
        data = await service.get_institutional_holdings(ticker=ticker, quarter=quarter)

        return {"status": "success", "data": data, "timestamp": now_iso()}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": {"ticker": ticker, "holdings": []},
            "timestamp": now_iso(),
        }
