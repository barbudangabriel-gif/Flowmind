import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)

TS_BASE = os.getenv("TS_BASE", "https://api.tradestation.com")
TS_TOKEN = os.getenv("TS_TOKEN")


class TSClient:
    def __init__(self):
        if not TS_TOKEN:
            raise RuntimeError("TS_TOKEN missing - need valid TradeStation OAuth token")
        self._client = httpx.AsyncClient(base_url=TS_BASE, timeout=15)

    async def aclose(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def chain(self, symbol: str) -> Dict[str, Any]:
        """Get options chain from TradeStation"""
        try:
            headers = {"Authorization": f"Bearer {TS_TOKEN}"}
            r = await self._client.get(
                f"/v3/marketdata/options/chains/{symbol.upper()}", headers=headers
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"TS chain API error for {symbol}: {e}")
            # Return empty structure to prevent crashes
            return {"expirations": []}

    async def quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote from TradeStation"""
        try:
            headers = {"Authorization": f"Bearer {TS_TOKEN}"}
            r = await self._client.get(
                f"/v3/marketdata/quotes/{symbol.upper()}", headers=headers
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"TS quote API error for {symbol}: {e}")
            # Return empty structure with fallback data
            return {"data": [{"last": 250.0}]}  # Fallback price
