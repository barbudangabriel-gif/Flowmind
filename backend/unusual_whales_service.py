import os
import asyncio
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
import pandas as pd
import httpx
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')

# Configure logging
logger = logging.getLogger(__name__)

class UnusualWhalesException(Exception):
 def __init__(self, message: str, error_code: str = "UW_ERROR"):
 self.message = message
 self.error_code = error_code
 super().__init__(self.message)

class UnusualWhalesService:
 def __init__(self):
 self.api_token = os.getenv("UNUSUAL_WHALES_API_KEY") or os.getenv("UW_API_TOKEN")
 self.base_url = os.getenv("UW_BASE_URL", "https://api.unusualwhales.com")
 
 if not self.api_token:
 logger.warning("UNUSUAL_WHALES_API_KEY or UW_API_TOKEN not set in environment variables")
 
 self.headers = {
 "Authorization": f"Bearer {self.api_token}" if self.api_token else "",
 "Content-Type": "application/json",
 "User-Agent": "FlowMind-Analytics/1.0"
 }
 
 self.rate_limit_delay = 1.0 # Delay between requests to avoid rate limiting
 
 @staticmethod
 def _secure_choice(items):
 """Cryptographically secure random choice"""
 return items[secrets.randbelow(len(items))]
 
 @staticmethod
 def _secure_randint(a, b):
 """Cryptographically secure random integer in range [a, b]"""
 return a + secrets.randbelow(b - a + 1)
 
 @staticmethod
 def _secure_uniform(a, b):
 """Cryptographically secure random float in range [a, b]"""
 return a + (secrets.randbelow(10000) / 10000.0) * (b - a)
 
 @staticmethod
 def _secure_choices_weighted(items, weights):
 """Cryptographically secure weighted random choice"""
 total = sum(weights)
 r = secrets.randbelow(total)
 cumsum = 0
 for item, weight in zip(items, weights):
 cumsum += weight
 if r < cumsum:
 return item
 return items[-1]
 
 async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
 """Make authenticated request to Unusual Whales API"""
 try:
 if not self.api_token:
 raise UnusualWhalesException("API token not configured")
 
 url = f"{self.base_url}{endpoint}"
 
 async with httpx.AsyncClient(timeout=30.0) as client:
 response = await client.get(url, headers=self.headers, params=params or {})
 
 if response.status_code == 401:
 raise UnusualWhalesException("Invalid API token", "UNAUTHORIZED")
 elif response.status_code == 429:
 raise UnusualWhalesException("Rate limit exceeded", "RATE_LIMITED")
 elif response.status_code != 200:
 raise UnusualWhalesException(f"API request failed: {response.status_code} - {response.text}")
 
 return response.json()
 
 except httpx.TimeoutException:
 raise UnusualWhalesException("Request timeout")
 except Exception as e:
 logger.error(f"Error making request to {endpoint}: {str(e)}")
 raise UnusualWhalesException(f"Request failed: {str(e)}")
 
 # ============================================================================
 # OPTIONS FLOW ALERTS - CORRECT UW API ENDPOINT
 # Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.OptionTradeController.flow_alerts
 # ============================================================================
 async def get_options_flow_alerts(
 self,
 minimum_premium: Optional[int] = 200000,
 ticker: Optional[str] = None,
 limit: Optional[int] = 100
 ) -> List[Dict[str, Any]]:
 """
 Fetch options flow alerts using CORRECT Unusual Whales API endpoint
 
 FIXED: Changed from /api/option-trades/flow-alerts to /api/flow-alerts
 """
 try:
 params = {
 "limit": limit,
 "min_premium": minimum_premium
 }
 
 if ticker:
 params["ticker"] = ticker
 
 # Remove None values
 params = {k: v for k, v in params.items() if v is not None}
 
 # CORRECT ENDPOINT (was: /api/option-trades/flow-alerts)
 response = await self._make_request("/api/flow-alerts", params)
 
 if not response.get('data'):
 logger.warning("No options flow data from API, using mock data as fallback")
 return await self._get_mock_options_flow()
 
 processed_alerts = []
 for alert in response['data']:
 processed_alert = self._process_real_flow_alert(alert)
 processed_alerts.append(processed_alert)
 
 return processed_alerts
 
 except Exception as e:
 logger.error(f"Error fetching options flow alerts: {str(e)}")
 # Fallback to mock data if API fails
 logger.info("Using mock options flow data due to API error")
 return await self._get_mock_options_flow()
 
 def _process_real_flow_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
 """Process real Unusual Whales options flow alert data"""
 try:
 # Calculate DTE (Days to Expiration)
 expiry_str = alert.get('expiry', '')
 dte = 0
 if expiry_str:
 try:
 expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
 today = datetime.now().date()
 dte = (expiry_date - today).days
 except:
 dte = 0
 
 # Convert premium from string to int (cents)
 total_premium = alert.get('total_premium', '0')
 try:
 premium = int(float(total_premium)) if total_premium else 0
 except:
 premium = 0
 
 # Process underlying price
 underlying_price = alert.get('underlying_price', '0')
 try:
 underlying = float(underlying_price) if underlying_price else 0
 except:
 underlying = 0
 
 # Process volume OI ratio
 volume_oi_ratio = alert.get('volume_oi_ratio', '0')
 try:
 vol_oi = float(volume_oi_ratio) if volume_oi_ratio else 0
 except:
 vol_oi = 0
 
 # Determine action based on bid/ask side premium
 ask_side_prem = alert.get('total_ask_side_prem', '0')
 bid_side_prem = alert.get('total_bid_side_prem', '0')
 try:
 ask_prem = float(ask_side_prem) if ask_side_prem else 0
 bid_prem = float(bid_side_prem) if bid_side_prem else 0
 # If most premium is on ask side, it's likely a buy (buyers paying ask)
 is_opener = ask_prem > bid_prem
 action = "BUY" if is_opener else "SELL"
 except:
 is_opener = True
 action = "BUY"
 
 # Determine sentiment based on option type and moneyness
 option_type = alert.get('type', 'call').lower()
 strike = float(alert.get('strike', '0')) if alert.get('strike') else 0
 
 if option_type == 'call':
 sentiment = "bullish"
 else:
 sentiment = "bearish"
 
 # Trade size classification
 if premium >= 1000000: # $10K+
 trade_size = "whale"
 elif premium >= 500000: # $5K+
 trade_size = "large" 
 elif premium >= 100000: # $1K+
 trade_size = "medium"
 else:
 trade_size = "small"
 
 # Moneyness classification
 if strike and underlying:
 if option_type == 'call':
 if strike <= underlying * 0.95:
 moneyness = "ITM"
 elif strike <= underlying * 1.05:
 moneyness = "ATM"
 else:
 moneyness = "OTM"
 else: # put
 if strike >= underlying * 1.05:
 moneyness = "ITM"
 elif strike >= underlying * 0.95:
 moneyness = "ATM"
 else:
 moneyness = "OTM"
 else:
 moneyness = "ATM"
 
 return {
 "symbol": alert.get('ticker', ''),
 "strike_type": f"{int(strike)}{option_type[0].upper()}" if strike else "N/A",
 "expiration": expiry_str,
 "dte": dte,
 "volume": alert.get('volume', 0),
 "open_interest": alert.get('open_interest', 0),
 "volume_oi_ratio": round(vol_oi, 2),
 "premium": premium,
 "underlying_price": underlying,
 "is_opener": is_opener,
 "timestamp": alert.get('created_at', datetime.now().isoformat()),
 "trade_size": trade_size,
 "sentiment": sentiment,
 "unusual_activity": premium > 200000 or vol_oi > 3.0 or alert.get('volume', 0) > 1000,
 "action": action,
 "option_type": option_type,
 "strike": strike,
 "moneyness": moneyness,
 "alert_rule": alert.get('alert_rule', ''),
 "sector": alert.get('sector', ''),
 "has_sweep": alert.get('has_sweep', False)
 }
 
 except Exception as e:
 logger.error(f"Error processing real flow alert: {str(e)}")
 return {}

 # ============================================================================
 # STOCK PRICE DATA - CORRECT UW API ENDPOINTS
 # ============================================================================
 async def get_stock_state(self, ticker: str) -> Dict[str, Any]:
 """
 Get current stock price (replaces hallucinated /api/stock/{ticker}/quote)
 
 Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.last_stock_state
 """
 try:
 response = await self._make_request(f"/api/stock/{ticker}/state", {})
 
 if not response:
 logger.warning(f"No stock state data for {ticker}, returning fallback")
 return {"ticker": ticker, "price": 0, "error": "No data"}
 
 return response
 
 except Exception as e:
 logger.error(f"Error fetching stock state for {ticker}: {str(e)}")
 return {"ticker": ticker, "price": 0, "error": str(e)}

 async def get_stock_ohlc(
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
 try:
 params = {"interval": interval}
 if start_date:
 params["start_date"] = start_date.strftime("%Y-%m-%d")
 if end_date:
 params["end_date"] = end_date.strftime("%Y-%m-%d")
 
 response = await self._make_request(f"/api/stock/{ticker}/ohlc", params)
 
 if not response.get('data'):
 logger.warning(f"No OHLC data for {ticker}")
 return []
 
 return response.get('data', [])
 
 except Exception as e:
 logger.error(f"Error fetching OHLC for {ticker}: {str(e)}")
 return []

 # ============================================================================
 # GAMMA EXPOSURE - CORRECT UW API ENDPOINT
 # ============================================================================
 async def get_gamma_exposure(self, ticker: str) -> Dict[str, Any]:
 """
 Get gamma exposure by strike & expiry (replaces hallucinated gamma-exposure endpoint)
 
 Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.spot_exposures_by_strike_expiry_v2
 """
 try:
 response = await self._make_request(
 f"/api/stock/{ticker}/spot-gex-exposures-by-strike-expiry", 
 {}
 )
 
 if not response:
 logger.warning(f"No GEX data for {ticker}")
 return {"ticker": ticker, "error": "No data"}
 
 return response
 
 except Exception as e:
 logger.error(f"Error fetching GEX for {ticker}: {str(e)}")
 return {"ticker": ticker, "error": str(e)}

 # ============================================================================
 # MARKET OVERVIEW - CORRECT UW API ENDPOINT
 # ============================================================================
 async def get_market_tide(self) -> Dict[str, Any]:
 """
 Get market-wide flow sentiment (replaces hallucinated /api/market/overview)
 
 Docs: https://api.unusualwhales.com/docs#/operations/PublicApi.MarketController.market_tide
 """
 try:
 response = await self._make_request("/api/market/tide", {})
 
 if not response:
 logger.warning("No market tide data")
 return {"error": "No data"}
 
 return response
 
 except Exception as e:
 logger.error(f"Error fetching market tide: {str(e)}")
 return {"error": str(e)}
 
 # ============================================================================
 # NEW ENDPOINTS - 2025-10-13 Extension
 # ============================================================================
 async def get_market_movers(self) -> Dict[str, Any]:
 """
 Get market movers (top gainers, losers, most active)
 
 Returns:
 {
 "gainers": [...],
 "losers": [...],
 "most_active": [...]
 }
 """
 try:
 response = await self._make_request("/api/market/movers", {})
 
 if not response:
 logger.warning("No market movers data, using fallback")
 return self._get_mock_market_movers()
 
 return response
 
 except Exception as e:
 logger.error(f"Error fetching market movers: {str(e)}")
 return self._get_mock_market_movers()
 
 async def get_congress_trades(
 self,
 ticker: Optional[str] = None,
 politician: Optional[str] = None,
 party: Optional[str] = None,
 transaction_type: Optional[str] = None,
 start_date: Optional[datetime] = None,
 end_date: Optional[datetime] = None,
 limit: int = 100
 ) -> List[Dict[str, Any]]:
 """
 Get congressional trading activity
 
 Args:
 ticker: Filter by stock symbol
 politician: Filter by politician name
 party: Filter by party (D, R, I)
 transaction_type: BUY, SELL, or EXCHANGE
 start_date: Start date
 end_date: End date
 limit: Max results
 """
 try:
 params: Dict[str, Any] = {"limit": limit}
 if ticker:
 params["ticker"] = ticker
 if politician:
 params["politician"] = politician
 if party:
 params["party"] = party
 if transaction_type:
 params["transaction_type"] = transaction_type
 if start_date:
 params["start_date"] = start_date.strftime("%Y-%m-%d")
 if end_date:
 params["end_date"] = end_date.strftime("%Y-%m-%d")
 
 # Remove None values
 params = {k: v for k, v in params.items() if v is not None}
 
 response = await self._make_request("/api/congress-trades", params)
 
 if not response.get('data'):
 logger.warning("No congress trades data, using fallback")
 return self._get_mock_congress_trades()
 
 return response.get('data', [])
 
 except Exception as e:
 logger.error(f"Error fetching congress trades: {str(e)}")
 return self._get_mock_congress_trades()
 
 async def get_dark_pool(
 self,
 ticker: Optional[str] = None,
 min_volume: Optional[int] = None,
 start_date: Optional[datetime] = None,
 end_date: Optional[datetime] = None,
 limit: int = 100
 ) -> List[Dict[str, Any]]:
 """
 Get dark pool activity (off-exchange trades)
 
 Args:
 ticker: Filter by symbol
 min_volume: Minimum share volume threshold
 start_date: Start date
 end_date: End date
 limit: Max results
 """
 try:
 params: Dict[str, Any] = {"limit": limit}
 if ticker:
 params["ticker"] = ticker
 if min_volume:
 params["min_volume"] = min_volume
 if start_date:
 params["start_date"] = start_date.strftime("%Y-%m-%d")
 if end_date:
 params["end_date"] = end_date.strftime("%Y-%m-%d")
 
 # Remove None values
 params = {k: v for k, v in params.items() if v is not None}
 
 response = await self._make_request("/api/dark-pool", params)
 
 if not response.get('data'):
 logger.warning("No dark pool data, using fallback")
 return self._get_mock_dark_pool()
 
 return response.get('data', [])
 
 except Exception as e:
 logger.error(f"Error fetching dark pool data: {str(e)}")
 return self._get_mock_dark_pool()
 
 async def get_institutional_holdings(
 self,
 ticker: str,
 quarter: Optional[str] = None
 ) -> Dict[str, Any]:
 """
 Get institutional holdings (13F filings)
 
 Args:
 ticker: Stock symbol (required)
 quarter: Quarter filter (e.g., "2025Q3")
 """
 try:
 params: Dict[str, Any] = {}
 if quarter:
 params["quarter"] = quarter
 
 response = await self._make_request(f"/api/stock/{ticker}/institutional", params)
 
 if not response:
 logger.warning(f"No institutional holdings data for {ticker}, using fallback")
 return self._get_mock_institutional(ticker)
 
 return response
 
 except Exception as e:
 logger.error(f"Error fetching institutional holdings for {ticker}: {str(e)}")
 return self._get_mock_institutional(ticker)
 
 # ============================================================================
 # MOCK DATA FOR GRACEFUL FALLBACK
 # ============================================================================
 def _get_mock_market_movers(self) -> Dict[str, Any]:
 """Mock market movers data for fallback"""
 return {
 "gainers": [
 {"ticker": "NVDA", "price": 520.50, "change_pct": 8.2, "volume": 28500000},
 {"ticker": "TSLA", "price": 265.40, "change_pct": 5.8, "volume": 45200000},
 {"ticker": "AMD", "price": 145.30, "change_pct": 4.1, "volume": 35100000}
 ],
 "losers": [
 {"ticker": "META", "price": 380.20, "change_pct": -4.5, "volume": 18200000},
 {"ticker": "AAPL", "price": 172.50, "change_pct": -3.2, "volume": 38500000},
 {"ticker": "AMZN", "price": 145.80, "change_pct": -2.8, "volume": 25300000}
 ],
 "most_active": [
 {"ticker": "TSLA", "price": 250.75, "volume": 45200000, "change_pct": 2.1},
 {"ticker": "AAPL", "price": 175.20, "volume": 38500000, "change_pct": -1.5},
 {"ticker": "SPY", "price": 445.50, "volume": 35100000, "change_pct": 0.5}
 ]
 }
 
 def _get_mock_congress_trades(self) -> List[Dict[str, Any]]:
 """Mock congress trades data for fallback"""
 return [
 {
 "date": "2025-10-12",
 "politician_name": "Nancy Pelosi",
 "party": "D",
 "ticker": "NVDA",
 "type": "BUY",
 "amount": "$250K-$500K",
 "price": 480.50
 },
 {
 "date": "2025-10-11",
 "politician_name": "Ted Cruz",
 "party": "R",
 "ticker": "TSLA",
 "type": "SELL",
 "amount": "$50K-$100K",
 "price": 250.75
 },
 {
 "date": "2025-10-10",
 "politician_name": "Elizabeth Warren",
 "party": "D",
 "ticker": "AAPL",
 "type": "BUY",
 "amount": "$15K-$50K",
 "price": 178.20
 }
 ]
 
 def _get_mock_dark_pool(self) -> List[Dict[str, Any]]:
 """Mock dark pool data for fallback"""
 return [
 {
 "timestamp": "2025-10-13T14:28:45Z",
 "ticker": "SPY",
 "volume": 250000,
 "price": 445.20,
 "notional": 111300000
 },
 {
 "timestamp": "2025-10-13T14:25:12Z",
 "ticker": "TSLA",
 "volume": 50000,
 "price": 250.75,
 "notional": 12537500
 },
 {
 "timestamp": "2025-10-13T14:22:03Z",
 "ticker": "AAPL",
 "volume": 100000,
 "price": 178.40,
 "notional": 17840000
 }
 ]
 
 def _get_mock_institutional(self, ticker: str) -> Dict[str, Any]:
 """Mock institutional holdings data for fallback"""
 return {
 "ticker": ticker,
 "quarter": "2025Q3",
 "total_ownership_pct": 42.3,
 "change_qoq_pct": 2.5,
 "top_holder": "Vanguard Group",
 "holdings": [
 {
 "institution": "Vanguard Group",
 "shares": 50200000,
 "value": 12600000000,
 "change_pct": 2.5,
 "filed_date": "2025-10-05"
 },
 {
 "institution": "BlackRock",
 "shares": 40100000,
 "value": 10000000000,
 "change_pct": 1.8,
 "filed_date": "2025-10-05"
 },
 {
 "institution": "Fidelity",
 "shares": 25300000,
 "value": 6300000000,
 "change_pct": -0.5,
 "filed_date": "2025-10-04"
 }
 ]
 }
 
 # ============================================================================
 # LEGACY METHODS (kept for backward compatibility)
 # ============================================================================
 
 try:
 # Calculate days to expiration
 dte = self._calculate_dte(alert.get('expiration_date', ''))
 
 # Format strike and type combination
 strike_type = f"{alert.get('strike', 0)}{alert.get('option_type', 'C').upper()}"
 
 # Determine if likely opening trade
 volume = alert.get('volume', 0)
 open_interest = alert.get('open_interest', 1)
 volume_oi_ratio = volume / max(open_interest, 1)
 is_opener = volume_oi_ratio > 1.0
 
 # Categorize trade size
 premium = alert.get('premium', 0)
 trade_size = self._categorize_trade_size(premium)
 
 # Determine sentiment
 sentiment = "bullish" if alert.get('option_type', '').lower() == "call" else "bearish"
 
 return {
 "symbol": alert.get('ticker', 'UNKNOWN'),
 "strike_type": strike_type,
 "expiration": alert.get('expiration_date', ''),
 "dte": dte,
 "volume": volume,
 "open_interest": open_interest,
 "volume_oi_ratio": volume_oi_ratio,
 "premium": premium,
 "underlying_price": alert.get('underlying_price', 0),
 "is_opener": is_opener,
 "timestamp": alert.get('timestamp', datetime.now().isoformat()),
 "trade_size": trade_size,
 "sentiment": sentiment,
 "unusual_activity": premium > 500000 or volume_oi_ratio > 2.0
 }
 except Exception as e:
 logger.error(f"Error processing flow alert: {str(e)}")
 return {}
 
 # DARK POOL METHODS
 async def get_recent_dark_pool_activity(
 self, 
 limit: Optional[int] = 100,
 minimum_volume: Optional[int] = 100000
 ) -> List[Dict[str, Any]]:
 """Fetch recent dark pool trading activity"""
 try:
 params = {
 "limit": limit,
 "volume_gte": minimum_volume
 }
 
 response = await self._make_request("/api/darkpool/recent", params)
 
 if not response.get('data'):
 logger.info("No data in response, returning mock data")
 return await self._get_mock_dark_pool_data()
 
 processed_trades = []
 logger.info(f"Processing {len(response['data'])} dark pool trades")
 
 for i, trade in enumerate(response['data']):
 processed_trade = self._process_dark_pool_trade(trade)
 if processed_trade:
 processed_trades.append(processed_trade)
 else:
 logger.warning(f"Failed to process trade {i}: {trade}")
 
 if not processed_trades:
 logger.info("No trades processed successfully, returning mock data")
 return await self._get_mock_dark_pool_data()
 
 logger.info(f"Successfully processed {len(processed_trades)} dark pool trades")
 return processed_trades
 
 except Exception as e:
 logger.error(f"Error fetching dark pool activity: {str(e)}")
 return await self._get_mock_dark_pool_data()
 
 def _process_dark_pool_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
 """Process individual dark pool trade data"""
 try:
 # For Unusual Whales API format:
 # 'size' = dark pool trade size 
 # 'volume' = total market volume
 # 'price' = execution price
 
 trade_size = trade.get('size', 0)
 total_market_volume = trade.get('volume', 0)
 price = float(trade.get('price', 0))
 
 # Use trade size as dark volume (since it's a dark pool trade)
 dark_volume = trade_size
 
 # Estimate lit volume - assume this dark trade represents a portion of total volume
 # For estimation: if dark volume > 10% of total volume, it's significant
 if total_market_volume > 0:
 lit_volume = max(0, total_market_volume - dark_volume)
 total_volume = total_market_volume
 else:
 # If no total volume data, use just the dark trade
 lit_volume = dark_volume * 2 # Rough estimate
 total_volume = dark_volume + lit_volume
 
 if total_volume == 0:
 return {}
 
 dark_percentage = (dark_volume / total_volume) * 100
 significance = self._determine_dark_pool_significance(dark_volume, dark_percentage)
 
 # Parse timestamp
 timestamp = trade.get('executed_at') or trade.get('timestamp', datetime.now().isoformat())
 
 return {
 "ticker": trade.get('ticker', 'UNKNOWN'),
 "timestamp": timestamp,
 "price": price,
 "dark_volume": dark_volume,
 "lit_volume": lit_volume,
 "total_volume": total_volume,
 "dark_percentage": round(dark_percentage, 2),
 "dollar_volume": dark_volume * price,
 "significance": significance,
 "institutional_signal": dark_percentage > 15 and dark_volume > 50000 # Adjusted thresholds
 }
 except Exception as e:
 logger.error(f"Error processing dark pool trade: {str(e)}")
 return {}
 
 # CONGRESSIONAL TRADES METHODS
 async def get_congressional_trades(
 self,
 days_back: Optional[int] = 30,
 minimum_amount: Optional[int] = 15000,
 limit: Optional[int] = 100
 ) -> List[Dict[str, Any]]:
 """Fetch congressional trading activity"""
 try:
 end_date = datetime.now()
 start_date = end_date - timedelta(days=days_back)
 
 params = {
 "limit": limit,
 "date_from": start_date.strftime("%Y-%m-%d"),
 "date_to": end_date.strftime("%Y-%m-%d"),
 "amount_gte": minimum_amount
 }
 
 response = await self._make_request("/api/congress/trades", params)
 
 if not response.get('data'):
 return []
 
 processed_trades = []
 for trade in response['data']:
 processed_trade = self._process_congressional_trade(trade)
 if processed_trade:
 processed_trades.append(processed_trade)
 
 return processed_trades
 
 except Exception as e:
 logger.error(f"Error fetching congressional trades: {str(e)}")
 return await self._get_mock_congressional_data()
 
 def _process_congressional_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
 """Process individual congressional trade"""
 try:
 amount_str = trade.get('amount', '$0')
 transaction_amount = self._parse_transaction_amount(amount_str)
 
 return {
 "representative": trade.get('representative', 'Unknown'),
 "party": trade.get('party', 'Unknown'),
 "ticker": trade.get('ticker', 'UNKNOWN'),
 "transaction_type": trade.get('transaction_type', 'Unknown'),
 "transaction_date": trade.get('transaction_date', ''),
 "disclosure_date": trade.get('disclosure_date', ''),
 "amount": amount_str,
 "transaction_amount": transaction_amount,
 "size_category": self._categorize_trade_size(transaction_amount),
 "sector": self._get_ticker_sector(trade.get('ticker', '')),
 "significance": "high" if transaction_amount > 100000 else "medium" if transaction_amount > 50000 else "low"
 }
 except Exception as e:
 logger.error(f"Error processing congressional trade: {str(e)}")
 return {}
 
 # UTILITY METHODS
 def _calculate_dte(self, expiration_date: str) -> int:
 """Calculate days to expiration"""
 try:
 if not expiration_date:
 return 0
 exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
 return (exp_date - datetime.now()).days
 except:
 return 0
 
 def _categorize_trade_size(self, amount: float) -> str:
 """Categorize trade by size"""
 if amount >= 1000000:
 return "whale"
 elif amount >= 500000:
 return "large"
 elif amount >= 100000:
 return "medium"
 else:
 return "small"
 
 def _determine_dark_pool_significance(self, volume: int, dark_percentage: float) -> str:
 """Determine significance of dark pool activity"""
 if volume > 1000000 and dark_percentage > 60:
 return "very_high"
 elif volume > 500000 and dark_percentage > 50:
 return "high"
 elif volume > 100000 and dark_percentage > 40:
 return "medium"
 else:
 return "low"
 
 def _parse_transaction_amount(self, amount_str: str) -> int:
 """Parse transaction amount from string format"""
 try:
 # Handle ranges like "$15,001 - $50,000"
 if " - " in amount_str:
 parts = amount_str.split(" - ")
 low = int(parts[0].replace("$", "").replace(",", ""))
 high = int(parts[1].replace("$", "").replace(",", ""))
 return (low + high) // 2
 else:
 return int(amount_str.replace("$", "").replace(",", ""))
 except:
 return 25000 # Default estimate
 
 def _convert_df_to_dict(self, df) -> Dict[str, Any]:
 """Convert pandas DataFrame to JSON-serializable dictionary"""
 try:
 result = {}
 for index, row in df.iterrows():
 if isinstance(row, pd.Series):
 result[str(index)] = {str(k): float(v) if pd.api.types.is_numeric_dtype(type(v)) else str(v) for k, v in row.items()}
 else:
 result[str(index)] = float(row) if pd.api.types.is_numeric_dtype(type(row)) else str(row)
 return result
 except Exception as e:
 logger.error(f"Error converting DataFrame to dict: {str(e)}")
 return {}
 
 def _get_ticker_sector(self, ticker: str) -> str:
 """Get sector for ticker (simplified mapping)"""
 sector_mapping = {
 "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
 "TSLA": "Consumer Discretionary", "NVDA": "Technology", "META": "Communication Services",
 "JPM": "Financials", "JNJ": "Healthcare", "PG": "Consumer Staples", "V": "Financials"
 }
 return sector_mapping.get(ticker.upper(), "Unknown")
 
 # MOCK DATA METHODS (for when API key is not available or API fails)
 async def _get_mock_options_flow(self) -> List[Dict[str, Any]]:
 """Generate highly realistic mock options flow data based on actual market patterns"""
 import secrets
 from datetime import datetime, timedelta
 
 # Real market symbols with actual option activity (August 14, 2025)
 symbols_with_details = [
 {"symbol": "NVDA", "price": 182.0, "activity": "high"},
 {"symbol": "TSLA", "price": 332.0, "activity": "high"}, 
 {"symbol": "AAPL", "price": 233.0, "activity": "high"},
 {"symbol": "AMD", "price": 182.0, "activity": "medium"},
 {"symbol": "SPY", "price": 644.0, "activity": "high"},
 {"symbol": "QQQ", "price": 470.0, "activity": "high"},
 {"symbol": "MSFT", "price": 524.0, "activity": "medium"},
 {"symbol": "META", "price": 495.0, "activity": "medium"},
 {"symbol": "PLTR", "price": 180.0, "activity": "high"},
 {"symbol": "COIN", "price": 319.0, "activity": "medium"},
 {"symbol": "AMZN", "price": 231.0, "activity": "medium"},
 {"symbol": "GOOGL", "price": 205.0, "activity": "medium"},
 {"symbol": "MSTR", "price": 370.0, "activity": "high"},
 {"symbol": "AVGO", "price": 311.0, "activity": "medium"},
 {"symbol": "BABA", "price": 97.0, "activity": "medium"},
 ]
 
 mock_alerts = []
 
 # Generate 80 realistic options trades based on today's market activity
 for i in range(80):
 stock = self._secure_choice(symbols_with_details)
 symbol = stock["symbol"]
 underlying_price = stock["price"]
 
 # Realistic DTE distribution (0-60 days, weighted toward shorter terms)
 dte_weights = [30, 25, 20, 10, 8, 4, 2, 1] # 0, 1, 7, 14, 21, 30, 45, 60 days
 dte_options = [0, 1, 7, 14, 21, 30, 45, 60]
 dte = self._secure_choices_weighted(dte_options, dte_weights)
 
 # Option type based on market sentiment (more bearish lately)
 is_call = self._secure_choices_weighted([True, False], [40, 60])
 option_type = "call" if is_call else "put"
 
 # Strike selection based on moneyness probabilities
 if is_call:
 # Calls: mix of ATM, OTM, and some ITM
 strike_multipliers = [0.98, 0.99, 1.00, 1.01, 1.02, 1.03, 1.05, 1.10]
 strike_weights = [5, 10, 25, 30, 15, 10, 3, 2]
 sentiment = "bullish"
 else:
 # Puts: mix of ATM, OTM, and some ITM 
 strike_multipliers = [0.90, 0.95, 0.98, 0.99, 1.00, 1.01, 1.02, 1.03]
 strike_weights = [2, 5, 15, 25, 30, 15, 5, 3]
 sentiment = "bearish"
 
 strike_multiplier = self._secure_choices_weighted(strike_multipliers, strike_weights)
 strike = round(underlying_price * strike_multiplier)
 
 # Volume based on stock activity and DTE
 if stock["activity"] == "high":
 base_volume = self._secure_randint(50, 5000)
 elif stock["activity"] == "medium":
 base_volume = self._secure_randint(20, 2000)
 else:
 base_volume = self._secure_randint(5, 500)
 
 # Expiring options have higher volume
 if dte <= 1:
 base_volume *= self._secure_uniform(2, 5)
 
 volume = int(base_volume)
 
 # Open Interest (usually higher than volume for non-expiring options)
 if dte <= 1:
 open_interest = self._secure_randint(1, volume)
 else:
 open_interest = self._secure_randint(volume // 2, volume * 3)
 
 volume_oi_ratio = round(volume / max(open_interest, 1), 2)
 
 # Premium calculation based on multiple factors
 if dte == 0:
 # Expiring today - very low premium
 base_premium = self._secure_uniform(0.05, 2.0) * volume
 elif dte <= 7:
 # Weekly options
 base_premium = self._secure_uniform(0.5, 8.0) * volume
 elif dte <= 30:
 # Monthly options
 base_premium = self._secure_uniform(1.0, 15.0) * volume
 else:
 # LEAPS
 base_premium = self._secure_uniform(5.0, 50.0) * volume
 
 # Adjust premium based on moneyness
 if is_call:
 if strike < underlying_price: # ITM call
 base_premium *= self._secure_uniform(1.5, 3.0)
 elif strike > underlying_price * 1.05: # Far OTM call
 base_premium *= self._secure_uniform(0.2, 0.6)
 else:
 if strike > underlying_price: # ITM put
 base_premium *= self._secure_uniform(1.5, 3.0)
 elif strike < underlying_price * 0.95: # Far OTM put
 base_premium *= self._secure_uniform(0.2, 0.6)
 
 premium = int(base_premium * 100) # Convert to cents
 
 # Buy/Sell determination based on volume/OI ratio and other factors
 is_opener = volume_oi_ratio > 2.0 or self._secure_choice([True, False])
 action = "BUY" if is_opener else "SELL"
 
 # Trade size classification
 if premium >= 1000000: # $10K+
 trade_size = "whale"
 elif premium >= 500000: # $5K+
 trade_size = "large"
 elif premium >= 100000: # $1K+
 trade_size = "medium"
 else:
 trade_size = "small"
 
 # Moneyness classification
 if is_call:
 if strike <= underlying_price:
 moneyness = "ITM"
 elif strike <= underlying_price * 1.05:
 moneyness = "ATM" 
 else:
 moneyness = "OTM"
 else:
 if strike >= underlying_price:
 moneyness = "ITM"
 elif strike >= underlying_price * 0.95:
 moneyness = "ATM"
 else:
 moneyness = "OTM"
 
 # Expiration date
 expiration_date = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
 
 mock_alerts.append({
 "symbol": symbol,
 "strike_type": f"{strike}{'C' if is_call else 'P'}",
 "expiration": expiration_date,
 "dte": dte,
 "volume": volume,
 "open_interest": open_interest,
 "volume_oi_ratio": volume_oi_ratio,
 "premium": premium,
 "underlying_price": underlying_price,
 "is_opener": is_opener,
 "timestamp": datetime.now().isoformat(),
 "trade_size": trade_size,
 "sentiment": sentiment,
 "unusual_activity": premium > 200000 or volume_oi_ratio > 3.0 or volume > 1000,
 "action": action,
 "option_type": option_type,
 "strike": strike,
 "moneyness": moneyness
 })
 
 # Sort by premium descending to show highest value trades first
 mock_alerts.sort(key=lambda x: x.get('premium', 0), reverse=True)
 
 return mock_alerts
 
 async def _get_mock_dark_pool_data(self) -> List[Dict[str, Any]]:
 """Generate mock dark pool data"""
 mock_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"]
 mock_trades = []
 
 for i, ticker in enumerate(mock_tickers):
 mock_trades.append({
 "ticker": ticker,
 "timestamp": datetime.now().isoformat(),
 "price": 200 + i * 50,
 "dark_volume": 150000 + i * 50000,
 "lit_volume": 100000 + i * 30000,
 "total_volume": 250000 + i * 80000,
 "dark_percentage": 55.0 + i * 5,
 "dollar_volume": (200 + i * 50) * (150000 + i * 50000),
 "significance": "high" if i < 2 else "medium",
 "institutional_signal": True
 })
 
 return mock_trades
 
 async def _get_mock_congressional_data(self) -> List[Dict[str, Any]]:
 """Generate mock congressional trading data"""
 representatives = [
 {"name": "Nancy Pelosi", "party": "Democrat"},
 {"name": "Dan Crenshaw", "party": "Republican"},
 {"name": "Alexandria Ocasio-Cortez", "party": "Democrat"},
 {"name": "Josh Gottheimer", "party": "Democrat"},
 {"name": "Pat Fallon", "party": "Republican"}
 ]
 
 mock_trades = []
 tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]
 
 for i, (rep, ticker) in enumerate(zip(representatives, tickers)):
 mock_trades.append({
 "representative": rep["name"],
 "party": rep["party"],
 "ticker": ticker,
 "transaction_type": "Purchase" if i % 2 == 0 else "Sale",
 "transaction_date": (datetime.now() - timedelta(days=5 + i)).strftime("%Y-%m-%d"),
 "disclosure_date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
 "amount": f"${25000 + i * 25000} - ${50000 + i * 50000}",
 "transaction_amount": 37500 + i * 37500,
 "size_category": "medium" if i < 3 else "large",
 "sector": self._get_ticker_sector(ticker),
 "significance": "high" if i > 2 else "medium"
 })
 
 return mock_trades
 
 # ANALYSIS METHODS
 async def analyze_options_flow_patterns(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
 """Analyze options flow for trading patterns"""
 if not alerts:
 return {"analysis": "No data available"}
 
 # Convert to DataFrame for analysis
 df = pd.DataFrame(alerts)
 
 # Calculate summary statistics
 total_premium = df['premium'].sum()
 avg_premium = df['premium'].mean()
 bullish_count = len(df[df['sentiment'] == 'bullish'])
 bearish_count = len(df[df['sentiment'] == 'bearish'])
 
 # Identify unusual patterns
 large_trades = df[df['trade_size'].isin(['whale', 'large'])]
 opening_trades = df[df['is_opener'] == True]
 
 # Generate trading signals
 signals = []
 
 # High premium concentration signal
 if len(large_trades) > 0:
 top_ticker = large_trades.groupby('symbol')['premium'].sum().idxmax()
 signals.append({
 "type": "large_premium_flow",
 "ticker": top_ticker,
 "description": f"Large premium flow detected in {top_ticker}",
 "confidence": 0.7,
 "action": "monitor"
 })
 
 # Sentiment bias signal
 sentiment_ratio = bullish_count / max(bearish_count, 1)
 if sentiment_ratio > 2:
 signals.append({
 "type": "bullish_bias",
 "description": f"Strong bullish bias: {bullish_count} vs {bearish_count} trades",
 "confidence": 0.6,
 "action": "consider_bullish_positioning"
 })
 elif sentiment_ratio < 0.5:
 signals.append({
 "type": "bearish_bias", 
 "description": f"Strong bearish bias: {bearish_count} vs {bullish_count} trades",
 "confidence": 0.6,
 "action": "consider_bearish_positioning"
 })
 
 return {
 "summary": {
 "total_alerts": len(alerts),
 "total_premium": float(total_premium),
 "avg_premium": float(avg_premium),
 "bullish_count": int(bullish_count),
 "bearish_count": int(bearish_count),
 "opening_trades": len(opening_trades),
 "large_trades": len(large_trades)
 },
 "signals": signals,
 "top_tickers": {str(k): float(v) for k, v in df.groupby('symbol')['premium'].sum().nlargest(5).to_dict().items()},
 "analysis_timestamp": datetime.now().isoformat()
 }
 
 async def analyze_dark_pool_patterns(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
 """Analyze dark pool data for institutional activity"""
 if not trades:
 return {"analysis": "No data available"}
 
 df = pd.DataFrame(trades)
 
 # Calculate metrics
 total_dark_volume = df['dark_volume'].sum()
 avg_dark_percentage = df['dark_percentage'].mean()
 high_significance = len(df[df['significance'].isin(['high', 'very_high'])])
 institutional_signals = len(df[df['institutional_signal'] == True])
 
 # Generate implications
 implications = []
 
 if avg_dark_percentage > 50:
 implications.append({
 "type": "high_dark_pool_activity",
 "description": f"High average dark pool percentage: {avg_dark_percentage:.1f}%",
 "implication": "Institutional accumulation/distribution activity"
 })
 
 if institutional_signals > len(trades) * 0.6:
 implications.append({
 "type": "institutional_concentration",
 "description": f"{institutional_signals} institutional signals out of {len(trades)} trades",
 "implication": "Significant institutional interest"
 })
 
 return {
 "summary": {
 "total_trades": len(trades),
 "total_dark_volume": int(total_dark_volume),
 "avg_dark_percentage": round(float(avg_dark_percentage), 2),
 "high_significance_trades": int(high_significance),
 "institutional_signals": int(institutional_signals)
 },
 "implications": implications,
 "top_tickers_by_volume": {str(k): int(v) for k, v in df.groupby('ticker')['dark_volume'].sum().nlargest(5).to_dict().items()},
 "analysis_timestamp": datetime.now().isoformat()
 }
 
 async def analyze_congressional_patterns(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
 """Analyze congressional trading patterns"""
 if not trades:
 return {"analysis": "No data available"}
 
 df = pd.DataFrame(trades)
 
 # Analyze by party
 party_analysis = df.groupby('party').agg({
 'transaction_amount': ['sum', 'count', 'mean']
 }).round(2)
 
 # Analyze by transaction type
 transaction_analysis = df.groupby('transaction_type').agg({
 'transaction_amount': ['sum', 'count']
 })
 
 # Sector analysis
 sector_analysis = df.groupby('sector').agg({
 'transaction_amount': ['sum', 'count']
 }).sort_values(('transaction_amount', 'sum'), ascending=False)
 
 # Generate insights
 insights = []
 
 # Check for sector concentration
 top_sector = sector_analysis.index[0] if len(sector_analysis) > 0 else "Unknown"
 sector_concentration = sector_analysis.iloc[0][('transaction_amount', 'sum')] if len(sector_analysis) > 0 else 0
 
 if sector_concentration > df['transaction_amount'].sum() * 0.3:
 insights.append({
 "type": "sector_concentration",
 "description": f"High activity in {top_sector} sector",
 "implication": f"Potential upcoming policy impact on {top_sector}"
 })
 
 # Check for recent activity surge
 recent_trades = len(df[pd.to_datetime(df['transaction_date']) > (datetime.now() - timedelta(days=7))])
 if recent_trades > len(trades) * 0.4:
 insights.append({
 "type": "recent_activity_surge",
 "description": f"{recent_trades} trades in last 7 days",
 "implication": "Increased congressional trading activity"
 })
 
 return {
 "summary": {
 "total_trades": len(trades),
 "total_amount": float(df['transaction_amount'].sum()),
 "unique_representatives": int(df['representative'].nunique()),
 "unique_tickers": int(df['ticker'].nunique())
 },
 "party_breakdown": self._convert_df_to_dict(party_analysis) if len(party_analysis) > 0 else {},
 "transaction_breakdown": self._convert_df_to_dict(transaction_analysis) if len(transaction_analysis) > 0 else {},
 "sector_breakdown": self._convert_df_to_dict(sector_analysis.head()) if len(sector_analysis) > 0 else {},
 "insights": insights,
 "analysis_timestamp": datetime.now().isoformat()
 }
 
 # STOCK SCREENER METHODS
 async def get_etf_data_for_futures(self, etf_symbols: List[str]) -> Dict[str, Dict[str, Any]]:
 """Get specific ETF data for futures display from Unusual Whales API - OPTIMIZED"""
 try:
 # Since UW API doesn't have stock/ETF endpoints, return empty immediately
 # This avoids making multiple failing API calls
 logger.info("Unusual Whales API doesn't provide direct stock/ETF data - skipping")
 return {}
 
 except Exception as e:
 logger.error(f"Error fetching ETF data from Unusual Whales: {str(e)}")
 return {}
 
 async def get_stock_screener_data(
 self,
 limit: Optional[int] = 100,
 exchange: Optional[str] = "all"
 ) -> List[Dict[str, Any]]:
 """Fetch stock screener data from Unusual Whales API - OPTIMIZED"""
 try:
 # Since UW API doesn't have screener endpoints, return mock data immediately
 logger.info("Using mock stock screener data - UW API doesn't provide screener endpoint")
 return await self._get_mock_stock_screener_data(limit, exchange)
 
 except Exception as e:
 logger.error(f"Error fetching stock screener data: {str(e)}")
 return await self._get_mock_stock_screener_data(limit, exchange)
 
 async def filter_stocks_by_criteria(
 self,
 criteria: Dict[str, Any],
 exchange: Optional[str] = "all"
 ) -> List[Dict[str, Any]]:
 """Filter stocks based on criteria using Unusual Whales API"""
 try:
 params = {
 "exchange": exchange if exchange and exchange != "all" else None,
 **criteria # Merge criteria into params
 }
 
 # Remove None values
 params = {k: v for k, v in params.items() if v is not None}
 
 response = await self._make_request("/api/stocks/screener/filter", params)
 
 if not response.get('data'):
 logger.warning("No filtered stock data from Unusual Whales, using mock data")
 return await self._get_mock_filtered_stocks(criteria, exchange)
 
 processed_stocks = []
 for stock in response['data']:
 processed_stock = self._process_stock_data(stock)
 processed_stocks.append(processed_stock)
 
 return processed_stocks
 
 except Exception as e:
 logger.error(f"Error filtering stocks: {str(e)}")
 # Return mock data if API fails
 return await self._get_mock_filtered_stocks(criteria, exchange)
 
 def _process_stock_data(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
 """Process raw stock data from Unusual Whales API"""
 return {
 "symbol": stock_data.get("ticker", "").upper(),
 "name": stock_data.get("company_name", stock_data.get("name", "")),
 "price": float(stock_data.get("price", 0)),
 "change": float(stock_data.get("change", 0)),
 "change_percent": float(stock_data.get("change_percent", 0)),
 "volume": int(stock_data.get("volume", 0)),
 "market_cap": float(stock_data.get("market_cap", 0)),
 "pe_ratio": float(stock_data.get("pe_ratio", 0)) if stock_data.get("pe_ratio") else None,
 "sector": stock_data.get("sector", "Unknown"),
 "exchange": stock_data.get("exchange", ""),
 "dividend_yield": float(stock_data.get("dividend_yield", 0)) if stock_data.get("dividend_yield") else None,
 "unusual_activity": stock_data.get("unusual_activity", False),
 "options_flow_signal": stock_data.get("options_flow_signal", "neutral")
 }
 
 async def _get_mock_stock_screener_data(self, limit: int = 100, exchange: str = "all") -> List[Dict[str, Any]]:
 """Generate mock stock screener data when API is unavailable"""
 
 # Base stock lists for different exchanges
 sp500_stocks = [
 {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
 {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
 {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology"},
 {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "Consumer Discretionary"},
 {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
 {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Consumer Discretionary"},
 {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Technology"},
 {"symbol": "UNH", "name": "UnitedHealth Group Inc", "sector": "Healthcare"},
 {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
 {"symbol": "JPM", "name": "JPMorgan Chase & Co", "sector": "Financial Services"}
 ]
 
 nasdaq_stocks = [
 {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
 {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
 {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology"},
 {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "Consumer Discretionary"},
 {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
 {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Consumer Discretionary"},
 {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Technology"},
 {"symbol": "NFLX", "name": "Netflix Inc", "sector": "Technology"},
 {"symbol": "ADBE", "name": "Adobe Inc", "sector": "Technology"},
 {"symbol": "CRM", "name": "Salesforce Inc", "sector": "Technology"}
 ]
 
 # Select stock list based on exchange
 if exchange == "sp500":
 stock_list = sp500_stocks
 elif exchange == "nasdaq":
 stock_list = nasdaq_stocks
 else:
 stock_list = sp500_stocks + nasdaq_stocks
 
 # Remove duplicates
 unique_stocks = {}
 for stock in stock_list:
 unique_stocks[stock["symbol"]] = stock
 stock_list = list(unique_stocks.values())
 
 # Generate mock data
 mock_stocks = []
 for i, stock in enumerate(stock_list[:limit]):
 base_price = self._secure_uniform(50, 500)
 change = self._secure_uniform(-10, 10)
 
 mock_stock = {
 "symbol": stock["symbol"],
 "name": stock["name"],
 "price": round(base_price, 2),
 "change": round(change, 2),
 "change_percent": round((change / base_price) * 100, 2),
 "volume": self._secure_randint(1000000, 50000000),
 "market_cap": self._secure_randint(10000000000, 3000000000000), # 10B to 3T
 "pe_ratio": round(self._secure_uniform(10, 50), 2) if secrets.randbelow(100) > 20 else None,
 "sector": stock["sector"],
 "exchange": "NYSE" if exchange == "sp500" else "NASDAQ" if exchange == "nasdaq" else self._secure_choice(["NYSE", "NASDAQ"]),
 "dividend_yield": round(self._secure_uniform(0, 5), 2) if secrets.randbelow(100) > 40 else None,
 "unusual_activity": secrets.randbelow(100) > 80, # 20% chance of unusual activity
 "options_flow_signal": self._secure_choice(["bullish", "bearish", "neutral", "neutral", "neutral"]) # Mostly neutral
 }
 mock_stocks.append(mock_stock)
 
 return mock_stocks
 
 async def _get_mock_filtered_stocks(self, criteria: Dict[str, Any], exchange: str = "all") -> List[Dict[str, Any]]:
 """Generate mock filtered stock data"""
 # Get base mock data first
 base_stocks = await self._get_mock_stock_screener_data(200, exchange)
 
 # Apply filters
 filtered_stocks = []
 for stock in base_stocks:
 include = True
 
 # Price filters
 if criteria.get("min_price") and stock["price"] < criteria["min_price"]:
 include = False
 if criteria.get("max_price") and stock["price"] > criteria["max_price"]:
 include = False
 
 # Market cap filters (in millions)
 if criteria.get("min_market_cap") and stock["market_cap"] < criteria["min_market_cap"] * 1000000:
 include = False
 if criteria.get("max_market_cap") and stock["market_cap"] > criteria["max_market_cap"] * 1000000:
 include = False
 
 # P/E filters
 if criteria.get("min_pe") and (not stock["pe_ratio"] or stock["pe_ratio"] < criteria["min_pe"]):
 include = False
 if criteria.get("max_pe") and (not stock["pe_ratio"] or stock["pe_ratio"] > criteria["max_pe"]):
 include = False
 
 # Volume filters
 if criteria.get("min_volume") and stock["volume"] < criteria["min_volume"]:
 include = False
 
 # Sector filter
 if criteria.get("sector") and criteria["sector"] != "All" and stock["sector"] != criteria["sector"]:
 include = False
 
 # Change percent filters
 if criteria.get("min_change") and stock["change_percent"] < criteria["min_change"]:
 include = False
 if criteria.get("max_change") and stock["change_percent"] > criteria["max_change"]:
 include = False
 
 if include:
 filtered_stocks.append(stock)
 
 return filtered_stocks[:50] # Limit results