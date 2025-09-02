import time
import math
from typing import Dict, Any
from .config import DEFAULT_FRONT_DTE, DEFAULT_BACK_DTE, CACHE_TTL_SECONDS, IV_PROVIDER
from .provider_base import round_to_tick
from .provider_stub import StubProvider

try:
    from .provider_ts import TradeStationProvider
except Exception:
    TradeStationProvider = None

# Provider factory
if IV_PROVIDER == "TS" and TradeStationProvider:
    _provider = TradeStationProvider()
else:
    _provider = StubProvider()

# TTL cache
_cache: Dict[str, Any] = {}


def cache_get(key: str):
    v = _cache.get(key)
    if not v:
        return None
    if time.time() - v["ts"] > CACHE_TTL_SECONDS:
        return None
    return v["data"]


def cache_put(key: str, data: Any):
    _cache[key] = {"ts": time.time(), "data": data}


def expected_move_usd(spot: float, iv: float, dte: int) -> float:
    return float(spot * iv * math.sqrt(max(dte, 0) / 365.0))


async def summary(
    symbol: str, front_dte: int = DEFAULT_FRONT_DTE, back_dte: int = DEFAULT_BACK_DTE
):
    key = f"sum:{symbol}:{front_dte}"
    c = cache_get(key)
    if c:
        return c
    spot = await _provider.get_spot(symbol)
    iv = await _provider.get_atm_iv(symbol, front_dte)
    em = expected_move_usd(spot, iv, front_dte)
    out = {
        "symbol": symbol.upper(),
        "spot": round(spot, 2),
        "iv": round(iv, 4),
        "em_usd": round(em, 2),
        "em_pct": round(em / spot if spot else 0.0, 4),
        "front_dte": int(front_dte),
        "back_dte": int(back_dte),
    }
    cache_put(key, out)
    return out


async def terms(symbol: str):
    key = f"terms:{symbol}"
    c = cache_get(key)
    if c:
        return c
    data = await _provider.list_terms(symbol)
    cache_put(key, data)
    return data


async def strikes(symbol: str, front_dte: int, back_dte: int):
    fs = await _provider.list_strikes(symbol, front_dte)
    bs = await _provider.list_strikes(symbol, back_dte)
    return {
        "symbol": symbol.upper(),
        "front": {"dte": front_dte, "strikes": fs},
        "back": {"dte": back_dte, "strikes": bs},
    }


def pick_calendar(spot: float, em_usd: float, mult: float):
    low = round_to_tick(spot - mult * em_usd, spot)
    high = round_to_tick(spot + mult * em_usd, spot)
    return int(low), int(high)


def pick_condor(spot: float, em_usd: float):
    shorts = (
        int(round_to_tick(spot - em_usd, spot)),
        int(round_to_tick(spot + em_usd, spot)),
    )
    wings = (
        int(round_to_tick(spot - 1.5 * em_usd, spot)),
        int(round_to_tick(spot + 1.5 * em_usd, spot)),
    )
    return shorts, wings
