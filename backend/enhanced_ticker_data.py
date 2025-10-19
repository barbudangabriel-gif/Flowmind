"""
Enhanced module for collecting real-time stock data with pre/post market information
"""
import requests
import pandas as pd
import yfinance as yf
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import aiohttp
import json

logger = logging.getLogger(__name__)

# S&P 500 tickers list (most liquid ones for real-time data)
SP500_TICKERS = [
 # Technology Giants
 "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "NVDA", "META", "NFLX", "ADBE",
 "CRM", "ORCL", "INTC", "AMD", "CSCO", "AVGO", "QCOM", "IBM", "NOW", "INTU",
 
 # Healthcare & Pharma
 "UNH", "JNJ", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "DHR", "BMY",
 "AMGN", "GILD", "VRTX", "CVS", "CI", "HUM", "ZTS", "REGN", "BIIB",
 
 # Financial Services
 "BRK-B", "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "USB", "PNC",
 "TFC", "COF", "SCHW", "CME", "ICE", "SPGI", "MCO", "BLK", "CB",
 
 # Consumer & Retail
 "WMT", "HD", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX",
 "TGT", "LOW", "TJX", "DIS", "CMCSA", "VZ", "T", "CL", "KMB",
 
 # Industrial & Energy
 "BA", "CAT", "MMM", "GE", "HON", "UNP", "LMT", "RTX", "UPS", "FDX",
 "XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC", "OXY"
]

# NASDAQ 100 tickers
NASDAQ_TICKERS = [
 # Tech Leaders
 "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "NVDA", "META", "NFLX", "ADBE",
 "PYPL", "INTC", "CSCO", "CMCSA", "AVGO", "TXN", "QCOM", "INTU", "AMD", "MU",
 "ISRG", "AMAT", "LRCX", "KLAC", "ADI", "MCHP", "CDNS", "SNPS", "MRVL", "NXPI",
 
 # Biotech & Healthcare
 "AMGN", "GILD", "VRTX", "BIIB", "REGN", "ILMN", "BMRN", "INCY",
 
 # Consumer & Services 
    "COST", "SBUX", "MAR", "BKNG", "EBAY", "FAST", "PAYX", "FISV", "ADP", "ROST"
]

class EnhancedTickerDataManager:
    def __init__(self, alpha_vantage_key: str = None):
        self.alpha_vantage_key = alpha_vantage_key
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote with pre/post market data using multiple sources"""
        try:
            # Primary source: Yahoo Finance with extended hours
            ticker = yf.Ticker(symbol)
            
            # Get current info and recent history for proper change calculation
            info = ticker.info
            
            # Get last 5 trading days to ensure we have previous close data
            history = ticker.history(period="5d", interval="1d", prepost=True)
            
            if history.empty:
                raise Exception(f"No data available for {symbol}")
            
            # Current price (most recent close)
            current_price = float(history['Close'].iloc[-1])
            current_volume = int(history['Volume'].iloc[-1])
            
            # Calculate change from previous trading day
            price_change = 0.0
            percent_change = 0.0
            
            if len(history) > 1:
                # Find the previous trading day's close
                previous_close = float(history['Close'].iloc[-2])
                price_change = current_price - previous_close
                percent_change = (price_change / previous_close) * 100
            else:
                # Fallback: use info data if available
                prev_close = info.get('previousClose')
                if prev_close:
                    price_change = current_price - float(prev_close)
                    percent_change = (price_change / float(prev_close)) * 100
            
            # Try to get live/current price if available
            current_live_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_live_price and current_live_price != current_price:
                # Use live price for more accurate change calculation
                if len(history) > 1:
                    previous_close = float(history['Close'].iloc[-2])
                elif info.get('previousClose'):
                    previous_close = float(info.get('previousClose'))
                else:
                    previous_close = current_price
                
                current_price = float(current_live_price)
                price_change = current_price - previous_close
                percent_change = (price_change / previous_close) * 100
            
            # Get volume - prefer live volume if available
            current_volume = info.get('regularMarketVolume') or info.get('volume')
            if not current_volume and not history.empty:
                current_volume = int(history['Volume'].iloc[-1])
            elif not current_volume:
                current_volume = 0
            else:
                current_volume = int(current_volume)
            
            # Try to get extended hours data
            extended_hours_data = await self._get_extended_hours_data(symbol)
            
            result = {
                "symbol": symbol.upper(),
                "name": info.get('longName', symbol),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "price": current_price,
                "change": price_change,
                "change_percent": percent_change,
                "volume": current_volume,
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('forwardPE') or info.get('trailingPE'),
                "dividend_yield": info.get('dividendYield'),
                "week_52_high": info.get('fiftyTwoWeekHigh'),
                "week_52_low": info.get('fiftyTwoWeekLow'),
                "beta": info.get('beta'),
                "avg_volume": info.get('averageVolume'),
                "exchange": info.get('exchange', 'Unknown'),
                "market_state": self._get_market_state(),
                "extended_hours": extended_hours_data,
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "Yahoo Finance Enhanced"
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching real-time data for {symbol}: {str(e)}")
            # Fallback with basic data
            return {
                "symbol": symbol.upper(),
                "name": symbol,
                "sector": "Unknown",
                "industry": "Unknown",
                "price": 0.0,
                "change": 0.0,
                "change_percent": 0.0,
                "volume": 0,
                "market_cap": None,
                "pe_ratio": None,
                "dividend_yield": None,
                "week_52_high": None,
                "week_52_low": None,
                "beta": None,
                "avg_volume": None,
                "exchange": "Unknown",
                "market_state": "UNKNOWN",
                "extended_hours": {},
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "Fallback"
            }

    async def _get_extended_hours_data(self, symbol: str) -> Dict[str, Any]:
        """Get pre-market and post-market data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get intraday data with pre/post market
            today_data = ticker.history(period="1d", interval="1m", prepost=True)
            
            if today_data.empty:
                return {}
            
            # Find pre-market data (before 9:30 AM ET)
            premarket_data = today_data.between_time('04:00', '09:29')
            postmarket_data = today_data.between_time('16:01', '19:59')
            
            result = {}
            
            if not premarket_data.empty:
                premarket_price = float(premarket_data['Close'].iloc[-1])
                premarket_volume = int(premarket_data['Volume'].sum())
                result['premarket'] = {
                    'price': premarket_price,
                    'change': premarket_price - float(today_data['Close'].iloc[0]) if len(today_data) > 0 else 0,
                    'volume': premarket_volume,
                    'time': premarket_data.index[-1].isoformat()
                }
            
            if not postmarket_data.empty:
                postmarket_price = float(postmarket_data['Close'].iloc[-1])
                postmarket_volume = int(postmarket_data['Volume'].sum())
                # Calculate change from regular market close
                regular_close = float(today_data.between_time('09:30', '16:00')['Close'].iloc[-1]) if len(today_data.between_time('09:30', '16:00')) > 0 else postmarket_price
                result['postmarket'] = {
                    'price': postmarket_price,
                    'change': postmarket_price - regular_close,
                    'volume': postmarket_volume,
                    'time': postmarket_data.index[-1].isoformat()
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching extended hours data for {symbol}: {str(e)}")
            return {}

    def _get_market_state(self) -> str:
        """Determine current market state"""
        import pytz
        et_tz = pytz.timezone('US/Eastern')
        et_time = datetime.now(et_tz)
        
        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = et_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = et_time.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Pre-market: 4:00 AM - 9:30 AM ET
        premarket_open = et_time.replace(hour=4, minute=0, second=0, microsecond=0)
        
        # Post-market: 4:00 PM - 8:00 PM ET
        postmarket_close = et_time.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Weekend check
        if et_time.weekday() >= 5: # Saturday = 5, Sunday = 6
            return "CLOSED"
        
        if premarket_open <= et_time < market_open:
            return "PREMARKET"
        elif market_open <= et_time < market_close:
            return "OPEN"
        elif market_close <= et_time < postmarket_close:
            return "POSTMARKET"
        else:
            return "CLOSED"

    async def get_bulk_real_time_data(self, symbols: List[str], max_batch_size: int = 10) -> List[Dict[str, Any]]:
        """Get real-time data for multiple symbols efficiently"""
        results = []
        
        for i in range(0, len(symbols), max_batch_size):
            batch = symbols[i:i + max_batch_size]
            batch_tasks = [self.get_real_time_quote(symbol) for symbol in batch]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Error in batch processing: {result}")
                        continue
                    results.append(result)
            
            except Exception as e:
                logger.error(f"Error processing batch {i}-{i+max_batch_size}: {str(e)}")
                continue
            
            # Small delay between batches to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return results

    async def get_sp500_tickers(self) -> List[str]:
        """Get S&P 500 ticker list"""
        return SP500_TICKERS
    
    async def get_nasdaq_tickers(self) -> List[str]:
        """Get NASDAQ ticker list"""
        return NASDAQ_TICKERS
    
    async def get_all_tickers(self) -> List[str]:
        """Get combined ticker list"""
        all_tickers = list(set(SP500_TICKERS + NASDAQ_TICKERS))
        return sorted(all_tickers)

    async def screen_stocks_enhanced(self, criteria: Dict[str, Any], exchange: str = "all") -> List[Dict[str, Any]]:
        """Enhanced stock screening with real-time data"""
        try:
            # Get ticker list based on exchange
            if exchange == "sp500":
                tickers = await self.get_sp500_tickers()
            elif exchange == "nasdaq":
                tickers = await self.get_nasdaq_tickers() 
            else:
                tickers = await self.get_all_tickers()
            
            # Limit for performance - focus on most liquid stocks
            tickers = tickers[:50]
            
            # Get real-time data for all tickers
            stock_data = await self.get_bulk_real_time_data(tickers)
            
            # Apply filtering criteria
            filtered_stocks = []
            for stock in stock_data:
                if self._meets_criteria_enhanced(stock, criteria):
                    filtered_stocks.append(stock)
            
            return filtered_stocks
        
        except Exception as e:
            logger.error(f"Error in enhanced stock screening: {str(e)}")
            return []

    def _meets_criteria_enhanced(self, stock: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Enhanced criteria matching with real-time data"""
        try:
            # Price range
            if 'min_price' in criteria and criteria['min_price']:
                if stock['price'] < float(criteria['min_price']):
                    return False
            
            if 'max_price' in criteria and criteria['max_price']:
                if stock['price'] > float(criteria['max_price']):
                    return False
            
            # Market cap range 
            if 'min_market_cap' in criteria and criteria['min_market_cap'] and stock['market_cap']:
                if stock['market_cap'] < float(criteria['min_market_cap']) * 1000000:
                    return False
            
            if 'max_market_cap' in criteria and criteria['max_market_cap'] and stock['market_cap']:
                if stock['market_cap'] > float(criteria['max_market_cap']) * 1000000:
                    return False
            
            # P/E ratio range
            if 'min_pe' in criteria and criteria['min_pe'] and stock['pe_ratio']:
                if stock['pe_ratio'] < float(criteria['min_pe']):
                    return False
            
            if 'max_pe' in criteria and criteria['max_pe'] and stock['pe_ratio']:
                if stock['pe_ratio'] > float(criteria['max_pe']):
                    return False
            
            # Volume filter
            if 'min_volume' in criteria and criteria['min_volume']:
                if stock['volume'] < int(criteria['min_volume']):
                    return False
            
            # Sector filter
            if 'sector' in criteria and criteria['sector'] and criteria['sector'] != 'All':
                if stock['sector'] != criteria['sector']:
                    return False
            
            # Change percent range - now using real calculated changes
            if 'min_change' in criteria and criteria['min_change']:
                if stock['change_percent'] < float(criteria['min_change']):
                    return False
            
            if 'max_change' in criteria and criteria['max_change']:
                if stock['change_percent'] > float(criteria['max_change']):
                    return False
            
            return True
        
        except (TypeError, ValueError) as e:
            logger.error(f"Error in criteria matching for {stock.get('symbol', 'unknown')}: {str(e)}")
            return False

# Global enhanced instance
enhanced_ticker_manager = EnhancedTickerDataManager()