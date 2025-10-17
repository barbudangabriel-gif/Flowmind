import base64
import json
import urllib.parse


def b64url(obj) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64url_decode(s: str):
    pad = "=" * (-len(s) % 4)
    return json.loads(base64.urlsafe_b64decode((s + pad).encode()))


def builder_link(strategy_id: str, symbol: str, expiry: str, legs, qty=1):
    s = b64url({"legs": legs, "qty": qty})
    q = urllib.parse.urlencode({"symbol": symbol, "expiry": expiry, "s": s})
    return f"/build/{strategy_id}?{q}"
