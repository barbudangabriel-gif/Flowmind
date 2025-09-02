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

    async def trades(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """Get options trades data"""
        params = {"start": start.isoformat(), "end": end.isoformat()}
        if symbol:
            params["symbol"] = symbol

        try:
            result = await self._get("/v1/options/trades", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW trades API error for {symbol}: {e}")
            return []

    async def news(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """Get news data"""
        params = {"start": start.isoformat(), "end": end.isoformat()}
        if symbol:
            params["symbol"] = symbol

        try:
            result = await self._get("/v1/news", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW news API error for {symbol}: {e}")
            return []

    async def congress(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """Get congress trades data"""
        params = {"start": start.isoformat(), "end": end.isoformat()}
        if symbol:
            params["symbol"] = symbol

        try:
            result = await self._get("/v1/congress/trades", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW congress API error for {symbol}: {e}")
            return []

    async def insiders(
        self, symbol: Optional[str], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """Get insider trades data"""
        params = {"start": start.isoformat(), "end": end.isoformat()}
        if symbol:
            params["symbol"] = symbol

        try:
            result = await self._get("/v1/insiders/trades", params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"UW insiders API error for {symbol}: {e}")
            return []
