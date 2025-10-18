import os
import json
import logging
from typing import Any, Dict, Optional
from .providers import get_provider
from utils.redis_client import get_redis

logger = logging.getLogger(__name__)


def fetch_chain(
    db, symbol: str, expiry: Optional[str] = None, dte: Optional[int] = None
) -> Dict[str, Any]:
    """Fetch options chain data using configured provider with caching"""
    provider = get_provider()

    # Try cache first
    cache_key = f"opt:chain:{provider.__class__.__name__}:{symbol}"
    if expiry:
        cache_key += f":{expiry}"
        if dte:
            cache_key += f":dte{dte}"

    try:
    r = get_redis()
    cached = r.get(cache_key)
    if cached:
    logger.info(f"Cache hit for options chain {symbol}")
    return json.loads(cached)
    except Exception as e:
    logger.debug(f"Cache read failed: {e}")

    # Fetch fresh data
    try:
    logger.info(
        f"Fetching fresh options data for {symbol} from {
            provider.__class__.__name__}")
    spot = provider.get_spot(symbol)
    chain = provider.get_chain(symbol, expiry=expiry, dte=dte)

    result = {
        "spot": float(spot),
        "raw": chain,
        "provider": provider.__class__.__name__,
        "symbol": symbol,
    }

    # Cache the result
    try:
    r = get_redis()
    ttl = int(os.getenv("OPT_CHAIN_TTL", "10"))  # Default 10 seconds
    r.set(cache_key, json.dumps(result), ex=ttl)
    logger.debug(f"Cached options chain for {symbol} (TTL: {ttl}s)")
    except Exception as e:
    logger.debug(f"Cache write failed: {e}")

    return result

    except Exception as e:
    logger.error(f"Failed to fetch options chain for {symbol}: {e}")
    raise


def compute_gex(
    symbol: str, expiry: Optional[str] = None, dte: Optional[int] = None
) -> Dict[str, Any]:
    """Compute Gamma Exposure (GEX) from options chain data"""
    try:
        # Get chain data
    chain_data = fetch_chain(None, symbol, expiry=expiry, dte=dte)
    spot = chain_data["spot"]
    chains = chain_data["raw"].get("OptionChains", [])

    if not chains:
    return {
        "symbol": symbol,
        "spot": spot,
        "error": "No options chains available",
        "gex_profile": [],
        "walls": [],
    }

    # Calculate GEX for each strike
    gex_profile = []
    call_gex_total = 0
    put_gex_total = 0

    for chain in chains:
    expiration = chain.get("Expiration", "")
    strikes = chain.get("Strikes", [])

    for strike_data in strikes:
    strike = strike_data.get("StrikePrice", 0)
    calls = strike_data.get("Calls", [])
    puts = strike_data.get("Puts", [])

    # Calculate call GEX (market makers are short calls = negative GEX)
    call_gex = 0
    for call in calls:
    gamma = call.get("Gamma", 0) or 0
    oi = call.get("OpenInterest", 0) or 0
    call_gex += -gamma * oi * 100  # Negative because MMs are short

    # Calculate put GEX (market makers are long puts = positive GEX)
    put_gex = 0
    for put in puts:
    gamma = put.get("Gamma", 0) or 0
    oi = put.get("OpenInterest", 0) or 0
    put_gex += gamma * oi * 100  # Positive because MMs are long

    total_gex = call_gex + put_gex
    call_gex_total += call_gex
    put_gex_total += put_gex

    gex_profile.append(
        {
            "strike": strike,
            "expiration": expiration,
            "call_gex": round(call_gex, 2),
            "put_gex": round(put_gex, 2),
            "total_gex": round(total_gex, 2),
        }
    )

    # Sort by strike
    gex_profile.sort(key=lambda x: x["strike"])

    # Find GEX walls (strikes with high absolute GEX)
    walls = []
    threshold = abs(call_gex_total + put_gex_total) * 0.1  # 10% threshold

    for profile in gex_profile:
    if abs(profile["total_gex"]) > threshold:
    walls.append(
        {
            "strike": profile["strike"],
            "gex": profile["total_gex"],
            "type": "resistance" if profile["total_gex"] > 0 else "support",
        }
    )

    return {
        "symbol": symbol,
        "spot": spot,
        "provider": chain_data["provider"],
        "call_gex_total": round(call_gex_total, 2),
        "put_gex_total": round(put_gex_total, 2),
        "net_gex": round(call_gex_total + put_gex_total, 2),
        "gex_profile": gex_profile,
        "walls": walls[:10],  # Top 10 walls
        "expiry": expiry,
    }

    except Exception as e:
    logger.error(f"Failed to compute GEX for {symbol}: {e}")
    return {"symbol": symbol, "error": str(e), "gex_profile": [], "walls": []}
