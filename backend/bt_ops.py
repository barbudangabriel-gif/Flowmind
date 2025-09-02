import time
import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from redis_fallback import get_kv

log = logging.getLogger("bt-ops")
rds = get_kv()

# Metrics tracking
_metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "start_time": time.time(),
}

router = APIRouter(prefix="/_bt", tags=["backtest-ops"])


@router.get("/status")
async def bt_status(key: Optional[str] = None):
    """Check backtest cache status"""
    if not key:
        # Global stats
        runtime_min = (time.time() - _metrics["start_time"]) / 60
        hit_rate = _metrics["cache_hits"] / max(_metrics["total_requests"], 1)

        return {
            "ok": True,
            "runtime_min": round(runtime_min, 1),
            "total_requests": _metrics["total_requests"],
            "cache_hits": _metrics["cache_hits"],
            "cache_misses": _metrics["cache_misses"],
            "hit_rate": round(hit_rate, 3),
            "impl": type(rds).__name__,
        }

    # Specific key status
    try:
        cached = await rds.get(key)
        if not cached:
            raise HTTPException(404, f"Key not found: {key}")

        data = json.loads(cached) if isinstance(cached, str) else cached
        ttl = await rds.ttl(key)

        return {
            "ok": True,
            "key": key,
            "kind": data.get("kind", "unknown"),
            "n": data.get("n", 0),
            "ttl": ttl,
            "size_bytes": len(str(cached)),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Status check failed: {e}")


@router.post("/purge")
async def bt_purge(body: dict):
    """Purge cache key for debugging"""
    key = body.get("key")
    if not key:
        raise HTTPException(400, "Key required")

    try:
        # Delete key
        if hasattr(rds, "delete"):
            await rds.delete(key)
        elif hasattr(rds, "_store"):
            # AsyncTTLDict fallback
            rds._store.pop(key, None)

        log.info("bt.purged key=%s", key)
        return {"ok": True, "purged": key}

    except Exception as e:
        log.error("bt.purge failed key=%s err=%s", key, e)
        raise HTTPException(500, f"Purge failed: {e}")


@router.get("/keys")
async def bt_keys(pattern: str = "bt:sum:*", limit: int = 100):
    """List cache keys (debug)"""
    try:
        if hasattr(rds, "keys"):
            # Real Redis
            keys = await rds.keys(pattern)
            return {"ok": True, "keys": keys[:limit], "count": len(keys)}
        elif hasattr(rds, "_store"):
            # AsyncTTLDict fallback
            all_keys = list(rds._store.keys())
            matched = [k for k in all_keys if pattern.replace("*", "") in k]
            return {"ok": True, "keys": matched[:limit], "count": len(matched)}
        else:
            return {"ok": False, "error": "Keys operation not supported"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def track_cache_hit():
    """Track cache hit"""
    _metrics["total_requests"] += 1
    _metrics["cache_hits"] += 1


def track_cache_miss():
    """Track cache miss"""
    _metrics["total_requests"] += 1
    _metrics["cache_misses"] += 1


def log_bt_operation(
    key: str, cache_status: str, n: int, win_rate: float, took_ms: int
):
    """Log backtest operation pentru metrics"""
    log.info(
        "bt.op key=%s cache=%s n=%d wr=%.3f took_ms=%d",
        key[:16],
        cache_status,
        n,
        win_rate,
        took_ms,
    )
