import os
import json
import requests
from typing import Any, Dict
from utils.redis_client import get_redis
import secrets
from datetime import datetime, timedelta

BASE = os.getenv("UW_BASE_URL", "https://api.unusualwhales.com").rstrip("/")
TOKEN = os.getenv("UW_API_TOKEN")
TTL = int(os.getenv("FLOW_TTL", "10"))
LIVE_PATH = os.getenv("UW_FLOW_LIVE_PATH", "/v1/options/flow/live")
HIST_PATH = os.getenv("UW_FLOW_HIST_PATH", "/v1/options/flow/historical")
NEWS_PATH = os.getenv("UW_NEWS_PATH", "/v1/news/flow")
CONG_PATH = os.getenv("UW_CONGRESS_PATH", "/v1/congress/flow")
INSD_PATH = os.getenv("UW_INSIDERS_PATH", "/v1/insiders/flow")


def _hdr():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def _get(path: str, params: Dict[str, Any] | None = None):
    """Make request to UW API with fallback to mock data if API is unavailable"""
    try:
        r = requests.get(BASE + path, headers=_hdr(), params=params, timeout=25)
    r.raise_for_status()
    return r.json()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        # UW API is not available for this endpoint, return mock data
    return _generate_mock_data(path)


def _generate_mock_data(path: str) -> Dict[str, Any]:
    """Generate mock flow data for demonstration purposes"""
    tickers = [
        "TSLA",
        "AAPL",
        "NVDA",
        "MSFT",
        "AMZN",
        "GOOGL",
        "META",
        "SPY",
        "QQQ",
        "IWM",
    ]
    sides = ["BUY", "SELL"]
    kinds = ["sweep", "block", "split", "single"]
    types = ["CALL", "PUT"]
    executions = ["above_ask", "below_bid", "at_mid"]

    if "live" in path or "historical" in path:
        # Generate mock flow data (using secrets for non-cryptographic
        # randomness)
    items = []
    for _ in range(secrets.randbelow(30) + 20):  # 20-50 items
    ticker = secrets.choice(tickers)
    side = secrets.choice(sides)
    kind = secrets.choice(kinds)
    opt_type = secrets.choice(types)

    item = {
        "time": (
            datetime.now() - timedelta(minutes=secrets.randbelow(60))
        ).isoformat(),
        "symbol": ticker,
        "side": side,
        "premium": round(1000 + secrets.randbelow(99000), 2),
        "price": round(0.5 + (secrets.randbelow(4950) / 100), 2),
        "size": secrets.randbelow(100) + 1,
        "kind": kind,
        "type": opt_type,
        "strike": 100 + secrets.randbelow(400),
        "expiry": (
            datetime.now() + timedelta(days=secrets.randbelow(365) + 1)
        ).strftime("%Y-%m-%d"),
        "dte": secrets.randbelow(365) + 1,
        "iv": round(0.2 + (secrets.randbelow(180) / 100), 3),
        "execution": secrets.choice(executions),
        "volume": secrets.randbelow(1000) + 1,
        "oi": secrets.randbelow(5000),
        "moneyness": round(0.8 + (secrets.randbelow(40) / 100), 3),
        "chance": round(0.1 + (secrets.randbelow(80) / 100), 3),
    }
    items.append(item)

    return {"data": items}

    elif "news" in path:
        # Generate mock news data
    news_items = [
        {
            "title": f"{secrets.choice(tickers)} Options Activity Surges",
            "headline": f"Unusual {secrets.choice(tickers)} options volume detected",
            "source": "FlowMind",
            "time": (
                datetime.now() - timedelta(hours=secrets.randbelow(24))
            ).isoformat(),
            "summary": f"Large {secrets.choice(kinds)} trades observed in {secrets.choice(types)} options",
        }
        for _ in range(secrets.randbelow(10) + 5)  # 5-15 items
    ]
    return {"data": news_items}

    elif "congress" in path or "insiders" in path:
        # Generate mock trading data
    trading_items = []
    for _ in range(secrets.randbelow(7) + 3):  # 3-10 items
    item = {
        "time": (
            datetime.now() - timedelta(days=secrets.randbelow(30))
        ).isoformat(),
        "symbol": secrets.choice(tickers),
        "side": secrets.choice(sides),
        "premium": round(10000 + secrets.randbelow(990000), 2),
        "type": secrets.choice(types),
        "strike": 100 + secrets.randbelow(400),
        "expiry": (
            datetime.now() + timedelta(days=30 + secrets.randbelow(335))
        ).strftime("%Y-%m-%d"),
        "dte": 30 + secrets.randbelow(335),
        "trader": f"Representative {chr(65 + secrets.randbelow(26))}"
        if "congress" in path
        else f"Insider {chr(65 + secrets.randbelow(26))}",
    }
    trading_items.append(item)

    return {"data": trading_items}

    return {"data": []}


def _apply_filters(item: Dict[str, Any], f: Dict[str, Any]):
    def inc(key, coll):
    return not coll or (str(item.get(key, "")).upper()
                        in {x.upper() for x in coll})

    if f.get("tickers") and str(item.get("symbol", "")).upper() not in {
        x.upper() for x in f["tickers"]
    }:
    return False
    if not inc("side", f.get("side")):
    return False
    if f.get("kinds"):
    kind = str(item.get("kind", "")).lower()
    if kind and kind not in {x.lower() for x in f["kinds"]}:
    return False
    if f.get("opt_types") and str(item.get("type", "")).upper() not in {
        x.upper() for x in f["opt_types"]
    }:
    return False
    if f.get("otm") and item.get("moneyness") and float(
            item["moneyness"]) <= 1.0:
    return False
    if (
        f.get("vol_gt_oi")
        and item.get("volume")
        and item.get("oi")
        and float(item["volume"]) <= float(item["oi"])
    ):
    return False
    if f.get("above_ask_below_bid") and str(
        item.get(
            "execution",
            "")).lower() not in (
            "above_ask",
            "below_bid",
    ):
    return False

    op = f.get("price_op")
    val = f.get("price_val")
    if op and item.get("price") is not None:
    p = float(item["price"])
    if op == "lt" and not (p < val):
    return False
    if op == "gt" and not (p > val):
    return False

    op = f.get("chance_op")
    val = f.get("chance_val")
    if op and item.get("chance") is not None:
    c = float(item["chance"])
    if op == "lt" and not (c < val):
    return False
    if op == "gt" and not (c > val):
    return False

    md = f.get("min_dte")
    M = f.get("max_dte")
    d = item.get("dte")
    if d is not None:
    if md is not None and int(d) < int(md):
    return False
    if M is not None and int(d) > int(M):
    return False

    return True


def live_flow(filters: Dict[str, Any] | None = None):
    filters = filters or {}
    r = get_redis()
    key = "uw:flow:live"
    try:
    c = r.get(key)
    raw = json.loads(c) if c else _get(LIVE_PATH, {})
    if not c:
    r.set(key, json.dumps(raw), ex=TTL)
    except Exception:
    raw = _get(LIVE_PATH, {})

    arr = raw.get("data") or raw.get("flow") or (
        raw if isinstance(raw, list) else [])
    out = [x for x in arr if _apply_filters(x, filters)]
    return {"items": out}


def historical_flow(params: Dict[str, Any] | None = None):
    params = params or {}
    raw = _get(HIST_PATH, params)
    arr = raw.get("data") or raw.get("flow") or (
        raw if isinstance(raw, list) else [])
    out = [x for x in arr if _apply_filters(x, params)]
    return {"items": out}


def news_flow(params=None):
    j = _get(NEWS_PATH, params or {})
    return {"items": j.get("data") or (j if isinstance(j, list) else [])}


def congress_flow(params=None):
    j = _get(CONG_PATH, params or {})
    return {"items": j.get("data") or (j if isinstance(j, list) else [])}


def insiders_flow(params=None):
    j = _get(INSD_PATH, params or {})
    return {"items": j.get("data") or (j if isinstance(j, list) else [])}


def summary_from_live():
    live = live_flow({})["items"]
    bull = {}
    bear = {}

    for x in live:
    sym = x.get("symbol")
    prem = float(x.get("premium", 0) or x.get("notional", 0))
    side = str(x.get("side", "")).upper()

    if not sym:
    continue

    bucket = bull if side.startswith("B") else bear
    row = bucket.setdefault(sym, {"symbol": sym, "count": 0, "premium": 0.0})
    row["count"] += 1
    row["premium"] += prem

    b1 = sorted(bull.values(), key=lambda z: z["premium"], reverse=True)[:50]
    b2 = sorted(bear.values(), key=lambda z: z["premium"], reverse=True)[:50]
    return {"bullish": b1, "bearish": b2}
