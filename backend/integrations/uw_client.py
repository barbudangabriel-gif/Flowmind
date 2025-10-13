from typing import List, Dict, Any, Optional
import httpx
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

UW_BASE = os.getenv("UW_BASE", "https://api.unusualwhales.com")
UW_KEY = os.getenv("UW_KEY")


class UWClient:
    def __init__(self, key: Optional[str] = UW_KEY):
        if not key:
            logger.warning("UW_KEY not configured - using demo mode")
            self._key = "demo-fallback"  # Fallback for demo/development
        else:
            self._key = key
        self._client = httpx.AsyncClient(base_url=UW_BASE, timeout=15)

    async def aclose(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated GET request to UW API"""
        headers = {"Authorization": f"Bearer {self._key}"}
        r = await self._client.get(path, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    # ============================================================================
    # OPTIONS FLOW ALERTS - Correct UW API Endpoint
    # Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.OptionTradeController.flow_alerts
    # ============================================================================
    async def flow_alerts(
        self, 
        ticker: Optional[str] = None, 
        min_premium: Optional[int] = None,
        date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get options flow alerts (replaces hallucinated /v1/options/trades)
        
        Args:
            ticker: Filter by symbol (e.g., "TSLA")
            min_premium: Minimum premium filter (in dollars)
            date: Specific date for historical alerts
            limit: Max results to return
        """
        params: Dict[str, Any] = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if min_premium:
            params["min_premium"] = min_premium
        if date:
            params["date"] = date.strftime("%Y-%m-%d")

        try:
            result = await self._get("/api/flow-alerts", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW flow alerts API error for {ticker}: {e}")
            return []

    # ============================================================================
    # STOCK DATA - Correct UW API Endpoints
    # ============================================================================
    async def stock_state(self, ticker: str) -> Dict[str, Any]:
        """
        Get current stock price (replaces hallucinated /api/stock/{ticker}/quote)
        
        Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.last_stock_state
        """
        try:
            result = await self._get(f"/api/stock/{ticker}/state", {})
            return result
        except Exception as e:
            logger.error(f"UW stock state API error for {ticker}: {e}")
            return {}

    async def stock_ohlc(
        self, 
        ticker: str, 
        interval: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical OHLC data
        
        Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.ohlc
        
        Args:
            ticker: Stock symbol
            interval: 1m, 5m, 15m, 1h, 1d (default: 1d)
            start_date: Start date for historical data
            end_date: End date for historical data
        """
        params: Dict[str, Any] = {"interval": interval}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        try:
            result = await self._get(f"/api/stock/{ticker}/ohlc", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW OHLC API error for {ticker}: {e}")
            return []

    # ============================================================================
    # GAMMA EXPOSURE - Correct UW API Endpoint
    # ============================================================================
    async def spot_gex_exposures(self, ticker: str) -> Dict[str, Any]:
        """
        Get gamma exposure by strike & expiry (replaces hallucinated gamma-exposure endpoint)
        
        Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.spot_exposures_by_strike_expiry_v2
        """
        try:
            result = await self._get(f"/api/stock/{ticker}/spot-gex-exposures-by-strike-expiry", {})
            return result
        except Exception as e:
            logger.error(f"UW GEX API error for {ticker}: {e}")
            return {}

    # ============================================================================
    # MARKET OVERVIEW - Correct UW API Endpoint
    # ============================================================================
    async def market_tide(self) -> Dict[str, Any]:
        """
        Get market-wide flow sentiment (replaces hallucinated /api/market/overview)
        
        Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.MarketController.market_tide
        """
        try:
            result = await self._get("/api/market/tide", {})
            return result
        except Exception as e:
            logger.error(f"UW market tide API error: {e}")
            return {}

    # ============================================================================
    # LEGACY METHODS - Deprecated (kept for backward compatibility)
    # ============================================================================
    async def trades(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: Use flow_alerts() instead"""
        logger.warning("trades() is deprecated - use flow_alerts() instead")
        return await self.flow_alerts(ticker=symbol, limit=100)

    async def news(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: News endpoint not yet implemented in UW API"""
        logger.warning("news() endpoint not available in UW API")
        return []

    async def congress(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: Congress trades endpoint not yet implemented in UW API"""
        logger.warning("congress() endpoint not available in UW API")
        return []

    async def insiders(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: Insiders endpoint not yet implemented in UW API"""
        logger.warning("insiders() endpoint not available in UW API")
        return []
