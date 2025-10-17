from datetime import datetime, timezone

def get_ivx(symbol: str, window: int) -> dict:
    base = (hash(symbol + str(window)) % 40) / 100 # 0.00 .. 0.39
    rank = (hash("rank" + symbol) % 101) # 0 .. 100
    return {
    "symbol": symbol,
    "window": window,
    "ivx": round(0.15 + base, 4),
    "rank": float(rank),
    "ts": datetime.now(timezone.utc),
    "source": "mock",
    "note": "stub; replace with UW+MCP computation",
    }
