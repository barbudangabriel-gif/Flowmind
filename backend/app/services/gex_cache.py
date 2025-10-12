import threading
import time
from typing import Any, Dict, Optional

class CacheEntry:
    def __init__(self, value: Any, ts: float, ttl: float):
        self.value = value
        self.ts = ts
        self.ttl = ttl
        self.lock = threading.Lock()
        self.inflight = False
        self.last_access = ts

    def is_valid(self, now: float, grace: float = 0.0) -> bool:
        return (now - self.ts) < (self.ttl + grace)

class GexCache:
    def __init__(self, ttl: float = 60.0, grace: float = 30.0):
        self.ttl = ttl
        self.grace = grace
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        entry = self._cache.get(key)
        if entry and entry.is_valid(now, self.grace):
            entry.last_access = now
            return entry.value
        return None

    def set(self, key: str, value: Any):
        now = time.time()
        with self._lock:
            self._cache[key] = CacheEntry(value, now, self.ttl)

    def get_entry(self, key: str) -> Optional[CacheEntry]:
        return self._cache.get(key)

    def clear(self):
        with self._lock:
            self._cache.clear()

gex_cache = GexCache()
