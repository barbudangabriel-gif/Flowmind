import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query, Request

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/options/flow", tags=["options-flow"])

DEFAULT_PROXY = "SPY"  # For symbol=ALL


@router.get("/summary")
async def flow_summary(
    request: Request,
    symbol: str = Query("ALL", description="Ticker or ALL"),
    days: int = Query(7, ge=1, le=30, description="Window for historical data"),
):
    """
    Get flow summary data:
    - live: trades in last 24h (from UW)
    - historical: trades in last `days` days (from UW)
    - news/congress/insiders: 0 (not using UW for these)
    """
    now = datetime.now(timezone.utc)
    d1 = now - timedelta(days=1)
    dN = now - timedelta(days=days)

    # Get UW client from app state
    uw = request.app.state.uw
    sym = None if symbol == "ALL" else symbol.upper()
    sym_or_proxy = sym or DEFAULT_PROXY

    try:
        # Get trades data from UW
        trades_live = await uw.trades(sym_or_proxy, d1, now)
        trades_hist = await uw.trades(sym_or_proxy, dN, now)

        logger.info(
            f"UW flow summary for {sym_or_proxy}: live={len(trades_live)}, hist={
                len(trades_hist)
            }"
        )

        return {
            "live": len(trades_live),
            "historical": len(trades_hist),
            "news": 0,  # Not using UW for news
            "congress": 0,  # Not using UW for congress
            "insiders": 0,  # Not using UW for insiders
            "source": {"trades": "uw", "symbolUsed": sym_or_proxy},
        }
    except Exception as e:
        logger.error(f"Flow summary error for {symbol}: {e}")
        # Return zeros on error to prevent UI crashes
        return {
            "live": 0,
            "historical": 0,
            "news": 0,
            "congress": 0,
            "insiders": 0,
            "source": {"trades": "error", "error": str(e)},
        }
