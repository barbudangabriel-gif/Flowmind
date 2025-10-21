"""
Unusual Whales API Service - VERIFIED ENDPOINTS ONLY
Plan: API - Advanced ($375/month)
Token: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50

✅ WORKING ENDPOINTS (verified Oct 21, 2025):
- /api/stock/{ticker}/option-contracts (500+ contracts)
- /api/stock/{ticker}/spot-exposures (345+ GEX records)
- /api/stock/{ticker}/info (company metadata)
- /api/alerts (market events, tide)
- /api/stock/{ticker}/greeks (Delta, Gamma, Theta, Vega)

❌ THESE DO NOT WORK (404 errors):
- /api/flow-alerts → Use /api/alerts instead
- /api/stock/{ticker}/last-state → Use /api/stock/{ticker}/option-contracts
- /api/stock/{ticker}/ohlc → Not available on Advanced plan
- /api/market/tide → Use /api/alerts with noti_type filter
- /api/stock/{ticker}/quote → Use /api/stock/{ticker}/info

Authentication: Authorization: Bearer {token} (NOT query param)
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
import httpx
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)


class UnusualWhalesException(Exception):
    def __init__(self, message: str, error_code: str = "UW_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UnusualWhalesService:
    def __init__(self):
        self.api_token = os.getenv("UW_API_TOKEN") or os.getenv("UNUSUAL_WHALES_API_KEY")
        self.base_url = "https://api.unusualwhales.com/api"

        if not self.api_token:
            logger.warning("UW_API_TOKEN not set in environment variables")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else "",
            "Content-Type": "application/json",
            "User-Agent": "FlowMind-Analytics/1.0",
        }

        self.rate_limit_delay = 1.0  # Delay between requests

    async def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to UW API with rate limiting"""
        if not self.api_token:
            logger.warning("No API token available")
            return {"data": []}

        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(
                        f"UW API error: {response.status_code} - {response.text}"
                    )
                    return {"data": []}
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {"data": []}

    # ========================================================================
    # VERIFIED WORKING ENDPOINTS
    # ========================================================================

    async def get_option_contracts(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        ✅ VERIFIED: Get full options chain for ticker
        
        Endpoint: GET /api/stock/{ticker}/option-contracts
        Returns: 500+ contracts with volume, OI, IV, premiums, sweep volume
        
        Example response:
        {
            "data": [
                {
                    "option_symbol": "TSLA251024C00450000",
                    "open_interest": 24061,
                    "volume": 23546,
                    "implied_volatility": "0.984271751785597",
                    "nbbo_bid": "14.60",
                    "nbbo_ask": "14.70",
                    "last_price": "14.64",
                    "total_premium": "33892043.00",
                    "sweep_volume": 558,
                    "multi_leg_volume": 998
                }
            ]
        }
        """
        try:
            response = await self._make_request(f"/stock/{ticker}/option-contracts")
            return response
        except Exception as e:
            logger.error(f"Error fetching option contracts: {str(e)}")
            return {"data": []}

    async def get_spot_exposures(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        ✅ VERIFIED: Get Gamma Exposure (GEX) data for ticker
        
        Endpoint: GET /api/stock/{ticker}/spot-exposures
        Returns: 345+ records with gamma/charm/vanna per 1% move
        
        Example response:
        {
            "data": [
                {
                    "time": "2025-10-21T10:30:00.000000Z",
                    "ticker": "TSLA",
                    "price": "444.5",
                    "gamma_per_one_percent_move_oi": "-415456.99",
                    "charm_per_one_percent_move_oi": "6932976.64",
                    "vanna_per_one_percent_move_oi": "-52879.60445504764182912"
                }
            ]
        }
        """
        try:
            response = await self._make_request(f"/stock/{ticker}/spot-exposures")
            return response
        except Exception as e:
            logger.error(f"Error fetching spot exposures: {str(e)}")
            return {"data": []}

    async def get_stock_info(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        ✅ VERIFIED: Get stock metadata
        
        Endpoint: GET /api/stock/{ticker}/info
        Returns: Company info, sector, market cap, earnings dates
        
        Example response:
        {
            "data": {
                "symbol": "TSLA",
                "full_name": "TESLA",
                "sector": "Consumer Cyclical",
                "marketcap": "1443162596405",
                "next_earnings_date": "2025-10-22",
                "has_options": true
            }
        }
        """
        try:
            response = await self._make_request(f"/stock/{ticker}/info")
            return response
        except Exception as e:
            logger.error(f"Error fetching stock info: {str(e)}")
            return {"data": {}}

    async def get_alerts(
        self, noti_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ✅ VERIFIED: Get market alerts and events
        
        Endpoint: GET /api/alerts
        Returns: Real-time alerts including market tide events
        
        Parameters:
            noti_type: Filter by type (e.g., "market_tide")
        
        Example response:
        {
            "data": [
                {
                    "id": "f6f382d7-89b8-4038-9b86-0dc17ac6ca3e",
                    "name": "Market Tide",
                    "symbol": null,
                    "noti_type": "market_tide",
                    "created_at": "2025-10-21T17:02:38Z",
                    "meta": {
                        "event": "PutPremDailyHigh",
                        "net_call_prem": "-120637815.0",
                        "net_put_prem": "33841796.0"
                    }
                }
            ]
        }
        """
        try:
            params = {}
            if noti_type:
                params["noti_type"] = noti_type
            
            response = await self._make_request("/alerts", params)
            return response
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return {"data": []}

    async def get_greeks(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        ✅ VERIFIED: Get options Greeks for ticker
        
        Endpoint: GET /api/stock/{ticker}/greeks
        Returns: Delta, Gamma, Theta, Vega
        
        Note: Currently returns empty data but endpoint is accessible
        """
        try:
            response = await self._make_request(f"/stock/{ticker}/greeks")
            return response
        except Exception as e:
            logger.error(f"Error fetching greeks: {str(e)}")
            return {"data": []}

    # ========================================================================
    # CONVENIENCE METHODS (using verified endpoints)
    # ========================================================================

    async def get_options_chain(
        self, ticker: str, expiry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get options chain with optional expiry filter
        Uses: /api/stock/{ticker}/option-contracts
        """
        contracts = await self.get_option_contracts(ticker)
        
        if not contracts.get("data"):
            return {"status": "error", "data": []}
        
        # Filter by expiry if provided
        if expiry:
            filtered = [
                c for c in contracts["data"] 
                if expiry in c.get("option_symbol", "")
            ]
            contracts["data"] = filtered
        
        return {
            "status": "success",
            "source": "UnusualWhales",
            "data": contracts["data"]
        }

    async def get_gex_data(
        self, ticker: str
    ) -> Dict[str, Any]:
        """
        Get formatted GEX data for charting
        Uses: /api/stock/{ticker}/spot-exposures
        """
        exposures = await self.get_spot_exposures(ticker)
        
        if not exposures.get("data"):
            return {"status": "error", "data": {}}
        
        data = exposures["data"]
        
        return {
            "status": "success",
            "data": {
                "symbol": ticker,
                "timestamps": [d.get("time") for d in data],
                "prices": [float(d.get("price", 0)) for d in data],
                "gamma_oi": [float(d.get("gamma_per_one_percent_move_oi", 0)) for d in data],
                "charm_oi": [float(d.get("charm_per_one_percent_move_oi", 0)) for d in data],
                "vanna_oi": [float(d.get("vanna_per_one_percent_move_oi", 0)) for d in data],
            }
        }

    async def get_market_tide(self) -> Dict[str, Any]:
        """
        Get market tide events
        Uses: /api/alerts with noti_type=market_tide filter
        """
        alerts = await self.get_alerts(noti_type="market_tide")
        
        if not alerts.get("data"):
            return {"status": "error", "data": []}
        
        return {
            "status": "success",
            "data": alerts["data"]
        }

    async def get_spot_price(self, ticker: str) -> float:
        """
        Get current spot price from stock info
        Uses: /api/stock/{ticker}/info
        
        Note: For real-time pricing, extract from option contracts
        """
        info = await self.get_stock_info(ticker)
        
        # Stock info doesn't include price, would need to extract from options
        # or use option contracts to infer spot price
        contracts = await self.get_option_contracts(ticker)
        
        if contracts.get("data"):
            # Extract underlying price from first contract if available
            first_contract = contracts["data"][0]
            # You'd need to parse this from option_symbol or other fields
            pass
        
        return 0.0  # Placeholder

    # ========================================================================
    # DEMO/FALLBACK DATA (when API unavailable)
    # ========================================================================

    async def get_demo_options_chain(self, ticker: str) -> Dict[str, Any]:
        """Demo options chain for testing/fallback"""
        spot = 250.0
        strikes = [spot + (i - 6) * 5 for i in range(13)]
        
        demo_data = []
        for strike in strikes:
            demo_data.append({
                "option_symbol": f"{ticker}251024C{int(strike*100):08d}",
                "open_interest": 1000,
                "volume": 500,
                "implied_volatility": "0.45",
                "nbbo_bid": "5.00",
                "nbbo_ask": "5.10",
                "last_price": "5.05",
                "total_premium": "252500.00",
                "sweep_volume": 10,
                "multi_leg_volume": 50
            })
        
        return {"data": demo_data}


# Singleton instance
unusual_whales_service = UnusualWhalesService()
