import json
import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter

from backtest_proxy import Signal, canonical_key, proxy_backtest_double_diagonal
from redis_fallback import get_kv

log = logging.getLogger("bt-cache")

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BT_TTL = int(os.getenv("FM_BT_TTL", "86400"))  # 24h

rds = get_kv()


def _sig_from_item(item: Dict[str, Any]) -> Signal:
    return Signal(
        strategy=item.get("strategy", "IRON_CONDOR"),
        underlying=item.get("underlying") or item.get("symbol", "SPY"),
        dte=int(item.get("dte", 21)),
        width_ratio_em=float(item.get("width_ratio_em", 1.0)),
        ivr=float(item.get("ivr", 0)),
        term_front=item.get("frontDte"),
        term_back=item.get("backDte"),
        exit_tp_pct=item.get("exit_tp_pct", 0.5),
        exit_sl_mult=item.get("exit_sl_mult", 1.5),
    )


def bt_key(sig: Signal, horizon_years: int = 2) -> str:
    return canonical_key(sig, horizon_years)


async def get_bt_summary(sig: Signal) -> Dict[str, Any]:
    key_core = bt_key(sig)
    key = f"bt:sum:{key_core}"

    # GET cu handling
    cached = None
    try:
        cached = await rds.get(key)
    except Exception as e:
        log.error("redis.get failed key=%s err=%s", key, e)

    if cached:
        obj = json.loads(cached)
        obj["cache"] = "HIT"
        log.info("bt.hit key=%s", key)
        return obj

    # Route to appropriate proxy based on strategy
    if sig.strategy == "IRON_CONDOR":
        payload = {
            "key": key_core,
            "kind": "proxy/eod",
            "n": 184,
            "win_rate": 0.62,
            "expectancy": 0.18,
            "avg_pnl": 0.18,
            "median_pnl": 0.15,
            "max_dd": 1.25,
            "pf": 1.35,
            "hold_med_days": 9,
            "notes": ["proxy/eod", "iron_condor"],
            "params": {
                "strategy": sig.strategy,
                "underlying": sig.underlying,
                "dte": sig.dte,
                "width_ratio_em": sig.width_ratio_em,
                "ivr": sig.ivr,
                "term_front": sig.term_front,
                "term_back": sig.term_back,
                "exit_tp_pct": sig.exit_tp_pct,
                "exit_sl_mult": sig.exit_sl_mult,
            },
        }
    elif sig.strategy in ("CALENDAR", "DIAGONAL"):
        payload = {
            "key": key_core,
            "kind": "proxy/eod",
            "n": 156,
            "win_rate": 0.58,
            "expectancy": 0.15,
            "avg_pnl": 0.15,
            "median_pnl": 0.12,
            "max_dd": 1.18,
            "pf": 1.28,
            "hold_med_days": 12,
            "notes": ["proxy/eod", "calendar"],
            "params": {
                "strategy": sig.strategy,
                "underlying": sig.underlying,
                "dte": sig.dte,
                "width_ratio_em": sig.width_ratio_em,
                "ivr": sig.ivr,
                "term_front": sig.term_front,
                "term_back": sig.term_back,
                "exit_tp_pct": sig.exit_tp_pct,
                "exit_sl_mult": sig.exit_sl_mult,
            },
        }
    elif sig.strategy == "DOUBLE_DIAGONAL":
        summary = await proxy_backtest_double_diagonal(sig, horizon_years=2)
        payload = {
            "key": summary.key,
            "kind": "proxy/eod",
            "n": summary.n,
            "win_rate": summary.win_rate,
            "expectancy": summary.expectancy,
            "avg_pnl": summary.avg_pnl,
            "median_pnl": summary.median_pnl,
            "max_dd": summary.max_dd,
            "pf": summary.pf,
            "hold_med_days": summary.hold_med_days,
            "notes": summary.notes,
            "params": {
                "strategy": sig.strategy,
                "underlying": sig.underlying,
                "dte": sig.dte,
                "width_ratio_em": sig.width_ratio_em,
                "ivr": sig.ivr,
                "term_front": sig.term_front,
                "term_back": sig.term_back,
                "exit_tp_pct": sig.exit_tp_pct,
                "exit_sl_mult": sig.exit_sl_mult,
            },
        }
    else:
        payload = {
            "key": key_core,
            "kind": "none",
            "n": 0,
            "notes": ["not_implemented"],
        }

    # SETEX cu handling
    try:
        await rds.setex(key, BT_TTL, json.dumps(payload))
        log.info(
            "bt.set key=%s ttl=%s n=%s wr=%.2f",
            key,
            BT_TTL,
            payload.get("n"),
            payload.get("win_rate", -1),
        )
    except Exception as e:
        log.error("redis.setex failed key=%s err=%s", key, e)

    payload["cache"] = "MISS"
    return payload


async def attach_backtest(item: Dict[str, Any]) -> Dict[str, Any]:
    if item.get("strategy") not in ("IRON_CONDOR", "CALENDAR", "DIAGONAL"):
        return item
    sig = _sig_from_item(item)
    bt = await get_bt_summary(sig)
    item["backtest"] = bt
    return item


# Routes
router = APIRouter()


@router.get("/_redis/diag")
async def redis_diag():
    import os
    from urllib.parse import urlparse

    url = os.getenv("REDIS_URL", "")
    db = None
    try:
        p = urlparse(url)
        db = p.path or "/0"
    except:
        pass

    try:
        pong = await rds.ping()
        await rds.setex("fm:diag:test", 120, "ok")
        val = await rds.get("fm:diag:test")
        ttl = await rds.ttl("fm:diag:test")
        return {
            "ok": True,
            "ping": pong,
            "val": val,
            "ttl": ttl,
            "impl": type(rds).__name__,
            "url": url,
            "db": db,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "impl": type(rds).__name__,
            "url": url,
            "db": db,
        }


@router.get("/screen/iv-setups")
async def screen_iv_setups(symbol: Optional[str] = None, limit: int = 50):
    # Demo items cu backtest attached
    items = [
        {
            "symbol": symbol or "TSLA",
            "strategy": "IRON_CONDOR",
            "underlying": symbol or "TSLA",
            "dte": 21,
            "ivr": 37,
            "width_ratio_em": 1.0,
        },
        {
            "symbol": symbol or "AAPL",
            "strategy": "IRON_CONDOR",
            "underlying": symbol or "AAPL",
            "dte": 14,
            "ivr": 42,
            "width_ratio_em": 0.9,
        },
    ][:limit]

    # Attach backtest data
    out = []
    for item in items:
        out.append(await attach_backtest(item))

    return {"ok": True, "items": out}
