def get_gex_summary(symbol: str, expiries: list, range: str = None, source: str = None):
    # Deterministic mock: generate netGex and walls for each expiry
    import hashlib, random, datetime
    items = []
    for expiry in expiries:
        h = int(hashlib.sha256((symbol+expiry).encode()).hexdigest()[:8], 16)
        rnd = random.Random(h)
        netGex = round(rnd.uniform(-200, 200), 2) * 1_000_000
        call_wall = rnd.randint(200, 300)
        put_wall = rnd.randint(100, 200)
        dte = None
        try:
            dte = (datetime.datetime.strptime(expiry, "%Y-%m-%d").date() - datetime.date.today()).days
        except Exception:
            pass
        items.append({
            "expiry": expiry,
            "dte": dte,
            "netGex": netGex,
            "walls": {"call": call_wall, "put": put_wall}
        })
    return items
from datetime import datetime, timezone

def get_ivx(symbol: str, window: int) -> dict:
    base = (hash(symbol + str(window)) % 40) / 100  # 0.00 .. 0.39
    rank = (hash("rank" + symbol) % 101)            # 0 .. 100
    return {
        "symbol": symbol,
        "window": window,
        "ivx": round(0.15 + base, 4),
        "rank": float(rank),
        "ts": datetime.now(timezone.utc),
        "source": "mock",
        "note": "stub; replace with UW+MCP computation",
    }


def get_gex(symbol: str) -> dict:
    """
    Return a deterministic mock GEX for a given symbol.
    """
    import hashlib, random, datetime
    h = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
    rnd = random.Random(h)
    gex = round(rnd.uniform(-50, 50), 2) * 1_000_000  # +/- up to ~50M USD
    flip_level = round(rnd.uniform(50, 500), 2)
    return {
        "symbol": symbol,
        "gex": gex,
        "unit": "USD",
        "flip_level": flip_level if rnd.random() > 0.2 else None,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "source": "mock",
        "note": "stub; replace with UW computation"
    }
