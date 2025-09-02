import os
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from utils.redis_client import get_redis


def _redis():
    # lazy, cu fallback in-memory
    return get_redis()


WINDOW = int(os.getenv("RL_WINDOW_SECONDS", "5"))  # secunde
LIMIT_DEFAULT = int(os.getenv("RL_LIMIT_DEFAULT", "120"))
LIMIT_PRICES = int(os.getenv("RL_LIMIT_PRICES", "60"))
LIMIT_TS = int(os.getenv("RL_LIMIT_TS", "30"))

SAFE_PREFIXES = {"/health", "/readyz", "/healthz"}


def _limit_for(path: str) -> int:
    if (
        path.startswith("/api/ts/")
        or path.startswith("/api/portfolios")
        and "/ts/" in path
    ):
        return LIMIT_TS
    if path.startswith("/api/prices"):
        return LIMIT_PRICES
    return LIMIT_DEFAULT


async def rate_limit(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in SAFE_PREFIXES):
        return await call_next(request)
    try:
        ip = request.client.host if request.client else "unknown"
        now = int(time.time())
        bucket = now // WINDOW
        limit = _limit_for(path)
        key = f"rl:{path}:{ip}:{bucket}"
        r = _redis()
        cur = r.incr(key)
        if cur == 1:
            r.expire(key, WINDOW + 1)
        if cur > limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
    except Exception:
        # fail-open dacă Redis nu răspunde
        pass
    return await call_next(request)
