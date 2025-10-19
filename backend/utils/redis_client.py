import os
import time
import threading
from typing import Optional


class InMemoryRedis:
    def __init__(self):
        self._d = {}
        self._lock = threading.Lock()

    def _purge(self, k):
        v = self._d.get(k)
        if not v:
            return
        val, exp = v
        if exp is not None and time.time() >= exp:
            self._d.pop(k, None)

    def incr(self, k: str) -> int:
        with self._lock:
            self._purge(k)
            cur = int(self._d.get(k, (0, None))[0] or 0)
            cur += 1
            self._d[k] = (cur, self._d.get(k, (None, None))[1])
            return cur

    def expire(self, k: str, seconds: int) -> int:
        with self._lock:
            self._purge(k)
            if k not in self._d:
                return 0
            val, _ = self._d[k]
            self._d[k] = (val, time.time() + max(0, seconds))
            return 1

    def set(self, k: str, v, ex: Optional[int] = None):
        with self._lock:
            self._d[k] = (v, time.time() + ex if ex else None)
        return True

    def get(self, k: str):
        with self._lock:
            self._purge(k)
            v = self._d.get(k)
            return None if v is None else v[0]

    def delete(self, k: str):
        with self._lock:
            self._d.pop(k, None)

    def flushdb(self):
        with self._lock:
            self._d.clear()


_client = None
_test_instance = None


def get_redis():
    """Returnează un client Redis real, sau InMemory dacă suntem în TEST/absent."""
    global _client, _test_instance
    if _client is not None:
        return _client
    # TEST_MODE true => in-memory (shared instance for tests)
    if os.getenv("TEST_MODE") == "1":
        if _test_instance is None:
            _test_instance = InMemoryRedis()
        _client = _test_instance
        return _client
    # încearcă redis real
    try:
        import redis

        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _client = redis.from_url(url, decode_responses=True)
        # ping "soft" – dacă nu răspunde, cădem pe in-memory
        try:
            _client.ping()
        except Exception:
            _client = InMemoryRedis()
    except Exception:
        _client = InMemoryRedis()
    return _client
