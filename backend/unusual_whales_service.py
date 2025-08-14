import os
import asyncio
import logging
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
        
        self.rate_limit_delay = 1.0  # Delay between requests to avoid rate limiting
    
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
    
    # OPTIONS FLOW METHODS
    async def get_options_flow_alerts(
        self,
        minimum_premium: Optional[int] = 200000,
        minimum_volume_oi_ratio: Optional[float] = 1.0,
        limit: Optional[int] = 100
    ) -> List[Dict[str, Any]]:
        """Fetch options flow alerts with filtering"""
        try:
            params = {
                "limit": limit,
                "premium_gte": minimum_premium,
                "volume_oi_ratio_gte": minimum_volume_oi_ratio
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await self._make_request("/api/option-trades/flow-alerts", params)
            
            if not response.get('data'):
                return []
            
            processed_alerts = []
            for alert in response['data']:
                processed_alert = self._process_flow_alert(alert)
                processed_alerts.append(processed_alert)
            
            return processed_alerts
            
        except Exception as e:
            logger.error(f"Error fetching options flow alerts: {str(e)}")
            # Return mock data if API fails for development/testing
            return await self._get_mock_options_flow()
    
    def _process_flow_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance individual flow alert data"""
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
                lit_volume = dark_volume * 2  # Rough estimate
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
                "institutional_signal": dark_percentage > 15 and dark_volume > 50000  # Adjusted thresholds
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
            return 25000  # Default estimate
    
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
        """Generate mock options flow data for development"""
        mock_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "META", "AMZN", "SPY", "QQQ"]
        mock_alerts = []
        
        for i, ticker in enumerate(mock_tickers[:5]):  # Limit to 5 for demo
            mock_alerts.append({
                "symbol": ticker,
                "strike_type": f"{300 + i * 20}C" if i % 2 == 0 else f"{280 + i * 15}P",
                "expiration": (datetime.now() + timedelta(days=7 + i)).strftime("%Y-%m-%d"),
                "dte": 7 + i,
                "volume": 1000 + i * 500,
                "open_interest": 500 + i * 200,
                "volume_oi_ratio": 2.0 + i * 0.5,
                "premium": 250000 + i * 100000,
                "underlying_price": 300 + i * 20,
                "is_opener": i % 2 == 0,
                "timestamp": datetime.now().isoformat(),
                "trade_size": "large" if i < 2 else "medium",
                "sentiment": "bullish" if i % 2 == 0 else "bearish",
                "unusual_activity": True
            })
        
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
        """Get specific ETF data for futures display from Unusual Whales API"""
        try:
            # Try direct API calls for individual ETF data
            etf_results = {}
            
            for symbol in etf_symbols:
                try:
                    # First try to get from stock screener data
                    screener_data = await self.get_stock_screener_data(limit=500, exchange="all")
                    
                    # Look for the ETF in screener data
                    etf_found = None
                    for stock in screener_data:
                        if stock.get('symbol', '').upper() == symbol.upper():
                            etf_found = stock
                            break
                    
                    if etf_found:
                        etf_results[symbol] = etf_found
                        logger.info(f"Found {symbol} in Unusual Whales screener data: ${etf_found.get('price', 0):.2f}")
                        continue
                    
                    # If not found in screener, try individual stock lookup
                    try:
                        # Try to make direct API call for individual stock
                        individual_data = await self._make_request(f"/api/stock/{symbol}")
                        
                        if individual_data and individual_data.get('price', 0) > 0:
                            processed_data = self._process_stock_data(individual_data)
                            etf_results[symbol] = processed_data
                            logger.info(f"Found {symbol} via individual API call: ${processed_data.get('price', 0):.2f}")
                            continue
                    except:
                        pass
                    
                    # Try alternative API endpoints for stock data
                    try:
                        params = {"symbol": symbol}
                        stock_response = await self._make_request("/api/stocks/quote", params)
                        
                        if stock_response and stock_response.get('data'):
                            stock_data = stock_response['data']
                            processed_data = self._process_stock_data(stock_data)
                            etf_results[symbol] = processed_data
                            logger.info(f"Found {symbol} via quote endpoint: ${processed_data.get('price', 0):.2f}")
                            continue
                    except:
                        pass
                    
                    logger.warning(f"Could not find {symbol} in Unusual Whales API")
                    
                except Exception as e:
                    logger.error(f"Error fetching {symbol} from Unusual Whales: {str(e)}")
                    continue
            
            return etf_results
            
        except Exception as e:
            logger.error(f"Error fetching ETF data from Unusual Whales: {str(e)}")
            return {}
    
    async def get_stock_screener_data(
        self,
        limit: Optional[int] = 100,
        exchange: Optional[str] = "all"
    ) -> List[Dict[str, Any]]:
        """Fetch stock screener data from Unusual Whales API"""
        try:
            params = {
                "limit": limit
            }
            
            # Add exchange filter if specified
            if exchange and exchange != "all":
                params["exchange"] = exchange
            
            # Try to fetch from Unusual Whales API
            response = await self._make_request("/api/stocks/screener", params)
            
            if not response.get('data'):
                logger.warning("No stock screener data from Unusual Whales, using mock data")
                return await self._get_mock_stock_screener_data(limit, exchange)
            
            processed_stocks = []
            for stock in response['data']:
                processed_stock = self._process_stock_data(stock)
                processed_stocks.append(processed_stock)
            
            return processed_stocks
            
        except Exception as e:
            logger.error(f"Error fetching stock screener data: {str(e)}")
            # Return mock data if API fails
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
                **criteria  # Merge criteria into params
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
        import random
        
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
            base_price = random.uniform(50, 500)
            change = random.uniform(-10, 10)
            
            mock_stock = {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "price": round(base_price, 2),
                "change": round(change, 2),
                "change_percent": round((change / base_price) * 100, 2),
                "volume": random.randint(1000000, 50000000),
                "market_cap": random.randint(10000000000, 3000000000000),  # 10B to 3T
                "pe_ratio": round(random.uniform(10, 50), 2) if random.random() > 0.2 else None,
                "sector": stock["sector"],
                "exchange": "NYSE" if exchange == "sp500" else "NASDAQ" if exchange == "nasdaq" else random.choice(["NYSE", "NASDAQ"]),
                "dividend_yield": round(random.uniform(0, 5), 2) if random.random() > 0.4 else None,
                "unusual_activity": random.random() > 0.8,  # 20% chance of unusual activity
                "options_flow_signal": random.choice(["bullish", "bearish", "neutral", "neutral", "neutral"])  # Mostly neutral
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
        
        return filtered_stocks[:50]  # Limit results