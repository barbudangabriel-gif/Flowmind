import os
import logging
from typing import Any, Dict, List
from datetime import datetime, timezone

log = logging.getLogger("iv.ts")

# TEMP: default ON ca să nu mai depindem de env în etapa de debug
TS_STUB = os.getenv("TS_STUB", "1") == "1"
log.warning("TS_STUB mode=%s", TS_STUB)


class TSClient:
    def __init__(self):
        pass

    async def get_spot(self, symbol: str) -> float:
        if TS_STUB:
            return 182.0
        # LIVE – pune call-ul tău real aici:
        # return await quotes.last(symbol)
        raise NotImplementedError("Mapează get_spot() la serviciul tău")

    async def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        if TS_STUB:
            return [
                {
                    "expiration": "2025-08-29",
                    "dte": 3,
                    "strikes": [
                        {
                            "K": 175,
                            "call": {
                                "bid": 6.2,
                                "ask": 6.8,
                                "last": 6.5,
                                "volume": 1200,
                            },
                            "put": {
                                "bid": 0.9,
                                "ask": 1.2,
                                "last": 1.05,
                                "volume": 800,
                            },
                        },
                        {
                            "K": 180,
                            "call": {
                                "bid": 3.8,
                                "ask": 4.2,
                                "last": 4.0,
                                "volume": 2100,
                            },
                            "put": {
                                "bid": 1.8,
                                "ask": 2.2,
                                "last": 2.0,
                                "volume": 1700,
                            },
                        },
                        {
                            "K": 190,
                            "call": {
                                "bid": 1.1,
                                "ask": 1.4,
                                "last": 1.25,
                                "volume": 900,
                            },
                            "put": {"bid": 5.2, "ask": 5.8, "last": 5.5, "volume": 700},
                        },
                    ],
                },
                {
                    "expiration": "2025-09-26",
                    "dte": 31,
                    "strikes": [
                        {
                            "K": 175,
                            "call": {
                                "bid": 10.1,
                                "ask": 10.9,
                                "last": 10.5,
                                "volume": 600,
                            },
                            "put": {"bid": 5.0, "ask": 5.6, "last": 5.3, "volume": 500},
                        },
                        {
                            "K": 180,
                            "call": {
                                "bid": 8.2,
                                "ask": 8.8,
                                "last": 8.5,
                                "volume": 800,
                            },
                            "put": {"bid": 6.3, "ask": 6.9, "last": 6.6, "volume": 900},
                        },
                        {
                            "K": 190,
                            "call": {
                                "bid": 5.1,
                                "ask": 5.9,
                                "last": 5.5,
                                "volume": 700,
                            },
                            "put": {"bid": 8.5, "ask": 9.2, "last": 8.9, "volume": 650},
                        },
                    ],
                },
            ]
        # LIVE – normalizează aici:
        # raw = await options.chain(symbol)
        # return normalize_chain(raw)
        raise NotImplementedError("Mapează get_option_chain() la serviciul tău")


def _dte(expiration_iso: str) -> int:
    try:
        dt = datetime.fromisoformat(str(expiration_iso).replace("Z", ""))
        today = datetime.now(timezone.utc)
        return max(0, (dt.date() - today.date()).days)
    except Exception:
        return 0


# ----------------- Normalizator generic pentru chain -----------------


def _dte(expiration_iso: str) -> int:
    try:
        dt = datetime.fromisoformat(str(expiration_iso).replace("Z", ""))
        today = datetime.now(timezone.utc)
        return max(0, (dt.date() - today.date()).days)
    except Exception:
        return 0


def _mid(x):
    if not x:
        return None
    bid = x.get("bid") or x.get("Bid") or x.get("b") or 0.0
    ask = x.get("ask") or x.get("Ask") or x.get("a") or 0.0
    last = x.get("last") or x.get("Last") or x.get("l")
    try:
        bid, ask = float(bid), float(ask)
        if bid > 0 and ask > 0 and ask >= bid:
            return (bid + ask) / 2.0
    except Exception:
        pass
    try:
        return float(last) if last is not None else None
    except Exception:
        return None


def normalize_chain(raw: dict | list) -> List[Dict[str, Any]]:
    """
    Normalizează payloaduri frecvente la:
    [{ expiration, dte, strikes:[ {K, call:{bid,ask,last,volume}, put:{...}} ] }]
    """
    out: List[Dict[str, Any]] = []
    expirations = None
    if isinstance(raw, dict):
        for key in ("expirations", "chains", "data", "items"):
            if key in raw and isinstance(raw[key], list):
                expirations = raw[key]
                break
    elif isinstance(raw, list):
        expirations = raw

    if not expirations:
        return out

    for exp in expirations:
        exp_dt = (
            exp.get("expiration")
            or exp.get("expiry")
            or exp.get("expirationDate")
            or exp.get("exp")
            or exp.get("date")
            or "2099-12-31"
        )
        dte = _dte(str(exp_dt))
        options_list = (
            exp.get("options")
            or exp.get("strikes")
            or exp.get("legs")
            or exp.get("contracts")
            or []
        )
        strikes_map: Dict[float, Dict[str, Any]] = {}
        for opt in options_list:
            K = opt.get("strike") or opt.get("K") or opt.get("strikePrice")
            typ = opt.get("type") or opt.get("optionType") or opt.get("right")
            if K is None or typ is None:
                continue
            try:
                K = float(K)
            except Exception:
                continue
            t = str(typ).lower()
            is_call = t.startswith("c")
            px = {
                "bid": opt.get("bid") or opt.get("Bid") or 0.0,
                "ask": opt.get("ask") or opt.get("Ask") or 0.0,
                "last": opt.get("last") or opt.get("Last") or _mid(opt),
                "volume": opt.get("volume") or opt.get("Volume") or 0,
            }
            node = strikes_map.setdefault(K, {"K": K, "call": {}, "put": {}})
            node["call" if is_call else "put"] = px

        strikes = sorted(strikes_map.values(), key=lambda s: s["K"])
        out.append({"expiration": str(exp_dt), "dte": dte, "strikes": strikes})

    out.sort(key=lambda e: e["dte"])
    return out
