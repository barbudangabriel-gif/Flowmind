import os
import time
from typing import Any, Optional, Tuple

try:
    from redis.asyncio import from_url as redis_from_url
except ImportError:
    redis_from_url = None


class AsyncTTLDict:
    """In-memory TTL store (fallback pentru Redis)"""

    def __init__(self):
        self._store: dict[str, Tuple[Optional[float], Any]] = {}

    def _purge(self):
        """Curăță intrările expirate"""
        now = time.time()
        expired = [k for k, (exp, _) in self._store.items() if exp and exp < now]
        for k in expired:
            del self._store[k]

    async def get(self, key: str) -> Optional[str]:
        self._purge()
        rec = self._store.get(key)
        return rec[1] if rec else None

    async def set(
        self, key: str, value: str, ex: Optional[int] = None, ttl: Optional[int] = None
    ) -> bool:
        # Support both ex and ttl parameters (ttl is alias for ex)
        expiry_seconds = ex or ttl
        exp = (time.time() + expiry_seconds) if expiry_seconds else None
        self._store[key] = (exp, value)
        return True

    async def setex(self, key: str, time_seconds: int, value: str) -> bool:
        exp = time.time() + time_seconds
        self._store[key] = (exp, value)
        return True

    async def ttl(self, key: str) -> int:
        self._purge()
        rec = self._store.get(key)
        if not rec:
            return -2  # no such key
        exp, _ = rec
        if exp is None:
            return -1  # no expiry
        return max(0, int(exp - time.time()))

    async def delete(self, key: str) -> int:
        """Delete key from store, return 1 if deleted, 0 if not found"""
        if key in self._store:
            del self._store[key]
            return 1
        return 0

    async def ping(self) -> bool:
        return True


# Shared instance for consistent storage (test mode AND fallback mode)
_shared_kv_instance = None


async def get_kv():
    """Returnează Redis client sau fallback in-memory"""
    global _shared_kv_instance

    # Force in-memory store during tests (shared instance)
    if os.environ.get("TEST_MODE") == "1":
        if _shared_kv_instance is None:
            _shared_kv_instance = AsyncTTLDict()
        return _shared_kv_instance

    if os.getenv("FM_FORCE_FALLBACK") == "1":
        if _shared_kv_instance is None:
            _shared_kv_instance = AsyncTTLDict()
        return _shared_kv_instance

    url = os.getenv("REDIS_URL")
    required = os.getenv("FM_REDIS_REQUIRED") == "1"

    if redis_from_url and url:
        try:
            return redis_from_url(url, decode_responses=True)
        except Exception as e:
            if required:
                raise RuntimeError(f"Redis connection required but failed: {e}")
            pass

    if required:
        raise RuntimeError(
            "Redis connection required but REDIS_URL not set or redis not available"
        )

    # Fallback to shared singleton instance when Redis not available
    if _shared_kv_instance is None:
        _shared_kv_instance = AsyncTTLDict()
    return _shared_kv_instance
