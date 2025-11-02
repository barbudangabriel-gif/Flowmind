import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services.options_gex import compute_gex, fetch_chain

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/options", tags=["options"])


@router.get("/gex")
def get_gex(
    symbol: str = Query(..., description="Stock symbol (e.g., TSLA)"),
    expiry: Optional[str] = Query(None, description="Expiration date (YYYY-MM-DD)"),
    dte: Optional[int] = Query(None, description="Days to expiration"),
):
    """Calculate Gamma Exposure (GEX) for a symbol"""
    try:
        result = compute_gex(symbol.upper(), expiry=expiry, dte=dte)
        return result
    except Exception as e:
        logger.error(f"GEX calculation failed for {symbol}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate GEX: {str(e)}"
        )


@router.get("/expirations")
def get_options_expirations(
    symbol: str = Query(..., description="Stock symbol"),
):
    """Get available expiration dates for a symbol"""
    try:
        from services.providers import get_provider

        provider = get_provider()
        if hasattr(provider, "get_expirations"):
            expirations = provider.get_expirations(symbol.upper())
            return {"expirations": expirations}
        else:
            # Fallback: get expirations from chain data
            result = fetch_chain(None, symbol.upper())
            expirations = result.get("expirations", [])
            return {"expirations": expirations}
    except Exception as e:
        logger.warning(f"Options expirations fetch failed for {symbol}: {e}, using fallback")
        # Return mock expirations when provider fails
        from datetime import datetime, timedelta
        today = datetime.now()
        mock_expirations = []
        for weeks in [1, 2, 4, 8, 13, 26, 52]:
            exp_date = today + timedelta(weeks=weeks)
            mock_expirations.append(exp_date.strftime("%Y-%m-%d"))
        return {
            "expirations": mock_expirations,
            "source": "mock",
            "symbol": symbol.upper()
        }


@router.get("/chain")
def get_options_chain(
    symbol: str = Query(..., description="Stock symbol"),
    expiry: Optional[str] = Query(None, description="Expiration date"),
    dte: Optional[int] = Query(None, description="Days to expiration"),
    dev: int = Query(0, description="Force demo data (1=enabled)"),
):
    """Get options chain data with demo fallback"""
    import os
    import secrets

    def _round5(x):
        return int(round(x / 5.0) * 5)

    def demo_chain(symbol: str, expiry: str, spot: float | None = None):
        """Generează 13 strikes (±6 * 5$) cu Bid/Ask/Mid, IV, OI, Vol – determinist."""
        if spot is None:
            # Fallback spot prices for common symbols
            spot_map = {
                "TSLA": 250.0,
                "AAPL": 175.0,
                "MSFT": 300.0,
                "NVDA": 450.0,
                "SPY": 425.0,
                "QQQ": 350.0,
            }
            spot = spot_map.get(symbol.upper(), 250.0)

        step = 5
        atm = _round5(spot)
        strikes = [atm + i * step for i in range(-6, 7)]
        total_oi = 0
        rows = []
        base_iv = 0.42  # la ATM

        for k in strikes:
            moneyness = abs(k - spot) / (spot if spot else 1.0)
            iv = max(0.18, base_iv * (1 + 0.25 * moneyness))  # IV mai mare OTM
            mid = max(0.05, (max(spot - k, 0) + 2.0) * 0.2)  # mid simplificat
            spread = max(0.03, mid * (0.06 + 0.12 * moneyness))
            bid = round(max(0.01, mid - spread / 2), 2)
            ask = round(mid + spread / 2, 2)
            mid = round((bid + ask) / 2, 2)
            oi = int(800 + (1 - min(moneyness, 1)) * 4500)  # OI mai mare aproape de ATM
            vol = int(
                50
                + 600
                * max(0, 1 - moneyness)
                * (0.6 + 0.4 * secrets.randbelow(100) / 100)
            )
            total_oi += oi
            rows.append(
                {
                    "strike": k,
                    "bid": bid,
                    "ask": ask,
                    "mid": mid,
                    "iv": round(iv, 3),
                    "oi": oi,
                    "vol": vol,
                }
            )

        # calc OI% (față de total expirare)
        for r in rows:
            r["oi_pct"] = round(r["oi"] / total_oi, 4) if total_oi > 0 else 0

        return rows

    use_dev = dev == 1 or os.getenv("CHAIN_DEV", "0") == "1"
    if use_dev:
        return demo_chain(symbol, expiry or "2025-02-21")

    # 1) încearcă providerul real
    try:
        result = fetch_chain(None, symbol.upper(), expiry=expiry, dte=dte)
        if result and result.get("raw", {}).get("OptionChains"):
            chains = result["raw"]["OptionChains"]
            if chains and len(chains[0].get("Strikes", [])) >= 6:
                # Transform to simple format
                strikes_data = chains[0]["Strikes"]
                chain_rows = []
                for strike in strikes_data:
                    call = strike.get("Calls", [{}])[0]
                    put = strike.get("Puts", [{}])[0]

                    chain_rows.append(
                        {
                            "strike": strike["StrikePrice"],
                            "bid": call.get("Bid") or put.get("Bid"),
                            "ask": call.get("Ask") or put.get("Ask"),
                            "mid": (
                                ((call.get("Bid", 0) + call.get("Ask", 0)) / 2)
                                if call.get("Bid") and call.get("Ask")
                                else None
                            ),
                            "iv": call.get("IV") or put.get("IV"),
                            "oi": (
                                call.get("OpenInterest", 0) + put.get("OpenInterest", 0)
                            ),
                            "vol": (call.get("Volume", 0) + put.get("Volume", 0)),
                        }
                    )

                return sorted(chain_rows, key=lambda x: x["strike"])

            # If not enough data, fallback to original response for backward compatibility
            return result
    except Exception as e:
        logger.error(f"Options chain fetch failed for {symbol}: {e}")
        pass

    # 2) fallback elegant pentru dev/test
    return demo_chain(symbol, expiry or "2025-02-21")


@router.get("/spot/{symbol}")
def get_spot_price(symbol: str):
    """Get current spot price for symbol"""
    try:
        from services.providers import get_provider

        provider = get_provider()
        spot = provider.get_spot(symbol.upper())
        return {
            "symbol": symbol.upper(),
            "spot": spot,
            "provider": provider.__class__.__name__,
        }
    except Exception as e:
        logger.warning(f"Spot price fetch failed for {symbol}: {e}, using fallback")
        # Return mock spot price when provider fails
        mock_prices = {
            "TSLA": 250.00,
            "AAPL": 175.50,
            "MSFT": 300.25,
            "NVDA": 450.75,
            "SPY": 425.00,
            "QQQ": 350.00,
            "GOOGL": 125.00,
            "AMZN": 140.00,
            "META": 320.00,
            "AMD": 110.00,
        }
        spot = mock_prices.get(symbol.upper(), 200.00)
        return {
            "symbol": symbol.upper(),
            "spot": spot,
            "provider": "MockProvider",
            "source": "fallback"
        }


@router.get("/provider/status")
def get_provider_status():
    """Get current options provider configuration and status"""
    try:
        import os

        from services.providers import get_provider

        provider = get_provider()

        return {
            "provider_name": provider.__class__.__name__,
            "provider_env": os.getenv("PROVIDER", "TS"),
            "cache_ttl": os.getenv("OPT_CHAIN_TTL", "10"),
            "status": "ready",
        }
    except Exception as e:
        logger.error(f"Provider status check failed: {e}")
        return {"provider_name": "unknown", "status": "error", "error": str(e)}
