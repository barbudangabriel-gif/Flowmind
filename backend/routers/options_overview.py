from fastapi import APIRouter, Query, Request
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from math import inf
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/options", tags=["options"])


def _mid(opt: Dict[str, Any]) -> Optional[float]:
    """Calculate mid price from bid/ask or use last"""
    bid = opt.get("bid")
    ask = opt.get("ask")
    last = opt.get("last")
    if bid is not None and ask is not None and ask > 0:
        return (bid + ask) / 2
    return last


def _closest_30d_iv(chain: Dict[str, Any], spot: float) -> Optional[float]:
    """Find IV from ATM option closest to 30 DTE"""
    expirations = chain.get("expirations") or chain.get("chains") or []
    if not expirations or spot is None:
        return None

    # Find expiry closest to 30 days
    target = datetime.utcnow() + timedelta(days=30)
    best_exp = None
    best_diff = inf

    for e in expirations:
        dt_str = e.get("expirationDate") or e.get("expiry")
        if not dt_str:
            continue
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            continue
        d = abs((dt - target).total_seconds())
        if d < best_diff:
            best_diff = d
            best_exp = e

    if not best_exp:
        return None

    # Find strike closest to spot (ATM)
    opts = best_exp.get("options", [])
    if not opts:
        return None

    atm = min(opts, key=lambda o: abs(float(o.get("strike", inf)) - spot))
    iv = atm.get("impliedVolatility") or atm.get("iv")
    if iv is None:
        return None

    # Normalize to percentage if in fraction
    return float(iv) * (100.0 if iv <= 1 else 1.0)


async def _get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database connection from request state"""
    # For now, we'll create a mock connection since we don't have actual DB setup
    # In a real implementation, this would be request.app.state.db
    from motor.motor_asyncio import AsyncIOMotorClient

    mongo_url = os.environ.get("MONGO_URL",
                               "mongodb://localhost:27017/flowmind")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get("DB_NAME", "test_database")
    return client[db_name]


@router.get("/overview")
async def options_overview(request: Request, symbol: str = Query(
        "ALL", description="Symbol filter (ALL or specific symbol)"), ):
    """
    Get market overview from TradeStation chain data:
    - dailyVolumeUsd: sum(volume * mid_price)
    - avgIvPct: IV from ATM options ~30 DTE
    - expirationDates: unique expiration count
    - activeStrategies: from internal DB
    """
    try:
        sym = None if symbol == "ALL" else symbol.upper()
        proxy = sym or "SPY"  # Use SPY for ALL market overview

        # Get TradeStation clients
        ts = request.app.state.ts

        # Get chain and quote data
        chain = await ts.chain(proxy)
        quote = await ts.quote(proxy)

        logger.info(f"Fetching TS options overview for symbol: {proxy}")

        # Extract spot price
        spot = None
        if isinstance(quote, dict):
            quote_data = quote.get("data") or quote.get("quotes") or [None]
            if isinstance(quote_data, list):
                qd = quote_data[0] if quote_data else None
            else:
                qd = quote_data
            if qd:
                spot = (
                    float(qd.get("last") or qd.get("price") or qd.get("mark") or 0)
                    or None
                )

        # Count expirations
        exps = chain.get("expirations") or chain.get("chains") or []
        expiration_dates = len(exps)

        # Calculate daily volume USD
        daily_usd = 0.0
        for e in exps:
            for opt in e.get("options", []):
                vol = opt.get("volume") or 0
                m = _mid(opt)
                if vol and m:
                    daily_usd += float(vol) * float(m) * 100  # *100 per contract

        # Get average IV (ATM 30D)
        iv_pct = _closest_30d_iv(chain, spot)

        # Get active strategies from internal DB
        db = await _get_db(request)
        strat_filter = {"status": "active"}
        if sym:
            strat_filter["symbol"] = sym
        strat_count = await db.strategies.count_documents(strat_filter)

        result = {
            "activeStrategies": strat_count,
            "expirationDates": expiration_dates,
            "dailyVolumeUsd": round(daily_usd, 2),
            "avgIvPct": round(iv_pct, 2) if iv_pct is not None else None,
            "source": {"chain": "tradestation", "symbolUsed": proxy},
        }

        logger.info(f"TS options overview result: {result}")
        return result

    except Exception as e:
        logger.error(f"Options overview failed for {symbol}: {e}")
        # Return fallback data to prevent UI crashes
        return {
            "activeStrategies": 0,
            "expirationDates": 0,
            "dailyVolumeUsd": 0.0,
            "avgIvPct": None,
            "source": {"chain": "error", "error": str(e)},
        }
