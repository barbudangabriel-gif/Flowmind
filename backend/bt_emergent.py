"""
FlowMind - Emergent Status (SELL_PUTS) v0.1
Status endpoint pentru module diagnostics
"""

import json
import os
import time
from typing import List

from fastapi import APIRouter, Query

from redis_fallback import get_kv

emergent_router = APIRouter(prefix="/_emergent", tags=["emergent"])

# Add Redis diagnostics endpoint
redis_diag_router = APIRouter(prefix="/_redis", tags=["redis"])


@redis_diag_router.get("/health")
async def redis_health():
    """
    Redis health check endpoint - simple status for monitoring
    Returns: connected (Redis), fallback (in-memory), or error
    """
    try:
        kv = await get_kv()
        impl_name = type(kv).__name__

        # Test connection with ping
        try:
            ping_result = await kv.ping()
            is_connected = bool(ping_result)
        except Exception:
            is_connected = False

        # Determine status
        if impl_name == "AsyncTTLDict":
            status = "fallback"
            mode = "in-memory"
            message = "Using in-memory fallback storage (Redis not available)"
        elif is_connected:
            status = "connected"
            mode = "redis"
            message = "Redis connection healthy"
        else:
            status = "error"
            mode = "unknown"
            message = "Redis connection failed"

        return {
            "status": status,
            "mode": mode,
            "implementation": impl_name,
            "connected": is_connected,
            "message": message,
            "redis_url": os.getenv("REDIS_URL", "not_set"),
            "force_fallback": os.getenv("FM_FORCE_FALLBACK") == "1",
            "redis_required": os.getenv("FM_REDIS_REQUIRED") == "1",
        }
    except Exception as e:
        return {
            "status": "error",
            "mode": "error",
            "implementation": "unknown",
            "connected": False,
            "message": f"Health check failed: {str(e)}",
            "error": str(e),
        }


@redis_diag_router.get("/diag")
async def redis_diag_endpoint():
    """Redis diagnostics endpoint"""
    return await _redis_diag()


# Also add redis diag to emergent router for easier access
@emergent_router.get("/redis/diag")
async def emergent_redis_diag():
    """Redis diagnostics endpoint via emergent router"""
    return await _redis_diag()


async def _redis_diag():
    """Redis diagnostics"""
    from urllib.parse import urlparse

    rds = get_kv()
    url = os.getenv("REDIS_URL", "")
    db = None
    try:
        p = urlparse(url)
        db = p.path or "/0"
    except (ValueError, AttributeError):
        pass

    try:
        pong = await rds.ping()
        impl = type(rds).__name__
        return {"ok": bool(pong), "impl": impl, "url": url, "db": db}
    except Exception as e:
        return {
            "ok": False,
            "impl": type(rds).__name__,
            "url": url,
            "db": db,
            "error": str(e),
        }


async def _scan_sell_put_keys():
    """Scan cache keys for sell puts strategies"""
    rds = get_kv()
    total = proxy = verified = 0

    try:
        if hasattr(rds, "keys"):
            keys = await rds.keys("bt:sum:*")
        elif hasattr(rds, "_store"):
            keys = [k for k in rds._store.keys() if k.startswith("bt:sum:")]
        else:
            return 0, 0, 0

        for key in keys:
            try:
                cached = await rds.get(key)
                if cached:
                    data = json.loads(cached)
                    total += 1
                    if data.get("kind") == "proxy/eod":
                        proxy += 1
                    elif data.get("kind") == "verified/chain":
                        verified += 1
            except Exception:
                continue

    except Exception:
        pass

    return total, proxy, verified


async def _metrics_bt():
    """Backtest cache metrics"""
    # Import metrics tracking from bt_ops if available
    try:
        from bt_ops import _metrics

        runtime_min = (time.time() - _metrics["start_time"]) / 60
        hit_rate = (
            _metrics["cache_hits"] / max(_metrics["total_requests"], 1)
            if _metrics["total_requests"] > 0
            else None
        )

        return {
            "runtime_min": round(runtime_min, 1),
            "total_requests": _metrics["total_requests"],
            "cache_hits": _metrics["cache_hits"],
            "cache_misses": _metrics["cache_misses"],
            "hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        }
    except Exception:
        return {"available": False}


async def _warmup_info():
    """Warmup process info"""
    return {
        "last_run": None,  # Would track actual warmup runs
        "next_scheduled": "16:00 Bucharest weekdays",
        "enabled": True,
    }


async def _sample_screener(limit: int = 5):
    """Sample from IV screener"""
    try:
        # Would call actual screener endpoint
        sample_data = [
            {
                "symbol": "TSLA",
                "dte": 21,
                "strike": 250,
                "delta": 0.18,
                "credit": 2.50,
                "decision": "ALLOW",
                "kind": "proxy/eod",
                "wr": 0.62,
                "exp": 0.18,
                "n": 184,
            }
        ]
        return {"available": True, "count": len(sample_data), "items": sample_data}
    except Exception:
        return {"available": False}


@emergent_router.get("/status")
async def emergent_status(
    module: str = Query(
        "sell_puts", description="Modul vizat: sell_puts / builder / gates / all"
    ),
    include_sample: bool = Query(
        True, description="Include mostre din screener dacă sunt disponibile"
    ),
):
    """Emergent status pentru SELL_PUTS module"""
    red = await _redis_diag()
    total, proxy, verified = await _scan_sell_put_keys()
    metrics = await _metrics_bt()
    warmup = await _warmup_info()
    sample = await _sample_screener(limit=5) if include_sample else {"available": False}

    alerts: List[str] = []
    if not red.get("ping"):
        alerts.append("redis_offline")
    if metrics.get("hit_rate") is not None and metrics["hit_rate"] < 0.7:
        alerts.append("low_cache_hit_rate")
    if total >= 25:
        vr = verified / max(1, total)
        if vr < 0.2:
            alerts.append("low_verified_ratio")

    return {
        "ok": True,
        "module": module,
        "redis": red,
        "cache": {
            "keys_total": total,
            "keys_proxy": proxy,
            "keys_verified": verified,
            "verified_ratio": (verified / max(1, total)) if total else None,
        },
        "metrics": metrics,
        "warmup": warmup,
        "screener_sample": sample,
        "alerts": alerts,
    }
