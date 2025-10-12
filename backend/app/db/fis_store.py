import os, sqlite3, threading, time
from typing import List, Dict, Any, Optional

_DB_PATH = os.environ.get("FIS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "fis_history.db"))
os.makedirs(os.path.dirname(os.path.abspath(_DB_PATH)), exist_ok=True)

_SQL_INIT = """
CREATE TABLE IF NOT EXISTS fis_history (
  symbol TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  score REAL NOT NULL,
  tech REAL NOT NULL,
  vol_surface REAL NOT NULL,
  flow REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fis_symbol_time ON fis_history(symbol, timestamp DESC);
"""

class FISStore:
    def __init__(self, path: str = _DB_PATH):
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        with self._conn:
            for stmt in _SQL_INIT.strip().split(";"):
                if stmt.strip():
                    self._conn.execute(stmt)

    def save(self, row: Dict[str, Any]) -> None:
        """row: {symbol, score, factors{tech,vol_surface,flow}, timestamp}"""
        ts = int(row.get("timestamp") or time.time())
        f = row.get("factors") or {}
        payload = (
            (row.get("symbol") or "").upper(),
            ts,
            float(row.get("score") or 0),
            float(f.get("tech") or 0),
            float(f.get("vol_surface") or f.get("vol") or 0),
            float(f.get("flow") or 0),
        )
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO fis_history(symbol,timestamp,score,tech,vol_surface,flow) VALUES (?,?,?,?,?,?)",
                payload
            )
            # păstrează ultimele 30 înregistrări / simbol
            self._conn.execute(
                """
                DELETE FROM fis_history
                WHERE symbol = ?
                AND timestamp NOT IN (
                  SELECT timestamp FROM fis_history WHERE symbol = ? ORDER BY timestamp DESC LIMIT 30
                )
                """,
                (payload[0], payload[0]),
            )

    def history(self, symbol: str, days: int = 30, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        symbol = (symbol or "").upper()
        cutoff = int(time.time()) - int(days) * 24 * 3600
        q = "SELECT timestamp,score,tech,vol_surface,flow FROM fis_history WHERE symbol=? AND timestamp>=? ORDER BY timestamp ASC"
        params = [symbol, cutoff]
        if limit:
            q += " LIMIT ?"
            params.append(int(limit))
        with self._lock, self._conn:
            cur = self._conn.execute(q, params)
            rows = cur.fetchall()
        return [{"t": r[0], "score": r[1], "tech": r[2], "vol_surface": r[3], "flow": r[4]} for r in rows]

store = FISStore()
