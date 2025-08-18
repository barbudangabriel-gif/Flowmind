from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import aiohttp
import asyncio
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import numpy as np
from collections import Counter
from enhanced_ticker_data import enhanced_ticker_manager
from investment_scoring import investment_scorer, StockScanner
from smart_money_analysis import smart_money_analyzer
from market_sentiment_analyzer import market_sentiment_analyzer
from unusual_whales_service import UnusualWhalesService
from expert_options_system import expert_system, StrategyType
from options_strategy_charts import chart_generator

# TradeStation Integration
from tradestation_auth_service import tradestation_auth_service as ts_auth
from tradestation_client import TradeStationClient
from portfolio_service import PortfolioService
from trading_service import TradingService, OrderRequest, OrderModification, RiskLimits
from token_manager import get_token_manager

# AI Agents
from investment_scoring_agent import InvestmentScoringAgent
from technical_analysis_agent import TechnicalAnalysisAgent

# Options Calculator
from options_calculator import options_engine, StrategyConfig, StrategyAnalysis


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas') if ALPHA_VANTAGE_API_KEY else None
ti = TechIndicators(key=ALPHA_VANTAGE_API_KEY, output_format='pandas') if ALPHA_VANTAGE_API_KEY else None

# Initialize Unusual Whales Service
uw_service = UnusualWhalesService()

# Initialize AI Agents
investment_scoring_agent = InvestmentScoringAgent()
technical_analysis_agent = TechnicalAnalysisAgent()

# Initialize TradeStation Services
ts_client = TradeStationClient(ts_auth)
portfolio_service = PortfolioService(ts_client)
trading_service = TradingService(ts_client)

# Create the main app without a prefix
app = FastAPI(title="Enhanced Stock Market Analysis API", version="3.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Enhanced Models
class ExtendedHoursData(BaseModel):
    premarket: Optional[Dict[str, Any]] = None
    postmarket: Optional[Dict[str, Any]] = None

class EnhancedStockData(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    beta: Optional[float] = None
    avg_volume: Optional[int] = None
    exchange: str
    market_state: str = "UNKNOWN"
    extended_hours: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    data_source: str = "Enhanced"

class StockData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ScreenerCriteria(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_market_cap: Optional[float] = None  # in millions
    max_market_cap: Optional[float] = None  # in millions  
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_volume: Optional[int] = None
    sector: Optional[str] = None
    min_change: Optional[float] = None
    max_change: Optional[float] = None

class PortfolioItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    
class PortfolioItemCreate(BaseModel):
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime

class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_profit_loss: float
    total_profit_loss_percent: float
    items: List[PortfolioItem]

class TechnicalIndicatorData(BaseModel):
    symbol: str
    rsi: Optional[Dict[str, float]] = None
    macd: Optional[Dict[str, float]] = None
    sma: Optional[Dict[str, float]] = None
    ema: Optional[Dict[str, float]] = None
    bollinger_bands: Optional[Dict[str, float]] = None

class WatchlistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    added_date: datetime = Field(default_factory=datetime.utcnow)
    target_price: Optional[float] = None
    notes: Optional[str] = None

class WatchlistItemCreate(BaseModel):
    symbol: str
    target_price: Optional[float] = None
    notes: Optional[str] = None

class InvestmentScore(BaseModel):
    symbol: str
    total_score: float
    rating: str
    individual_scores: Dict[str, float]
    fundamental_score: Optional[float] = None
    technical_score: Optional[float] = None
    explanation: str
    risk_level: str
    investment_horizon: str
    key_strengths: List[str]
    key_risks: List[str]
    stock_data: Optional[Dict[str, Any]] = None  # FIXED: Add stock_data field
    technical_analysis: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None  # FIXED: Add sentiment_analysis field
    analysis_type: Optional[str] = None
    last_updated: str

class SmartMoneyAnalysis(BaseModel):
    symbol: str
    analysis_timestamp: str
    current_price: float
    timeframe: str
    smart_money_verdict: Dict[str, Any]
    order_blocks: List[Dict[str, Any]]
    fair_value_gaps: List[Dict[str, Any]]
    liquidity_sweeps: List[Dict[str, Any]]
    market_structure: Dict[str, Any]
    premium_discount: Dict[str, Any]
    imbalances: List[Dict[str, Any]]
    price_action: Dict[str, Any]
    trading_signals: List[Dict[str, Any]]

class TopInvestments(BaseModel):
    recommendations: List[InvestmentScore]
    total_analyzed: int
    criteria: str
    last_updated: str

# Utility functions for data fetching
async def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get current stock quote with TradeStation primary, Unusual Whales fallback"""
    
    # First, try TradeStation if authenticated
    try:
        if ts_auth.is_authenticated():
            logger.info(f"Using TradeStation API for {symbol} pricing (primary source)")
            
            async with ts_client:
                quotes = await ts_client.get_quote([symbol])
                
                if quotes and len(quotes) > 0:
                    ts_quote = quotes[0]
                    
                    return {
                        "symbol": ts_quote.symbol,
                        "price": ts_quote.last,
                        "change": ts_quote.change,
                        "change_percent": ts_quote.change_percent,
                        "volume": ts_quote.volume,
                        "market_cap": None,  # Not available in TradeStation
                        "pe_ratio": None,   # Not available in TradeStation
                        "timestamp": datetime.utcnow(),
                        "data_source": "TradeStation API (Primary)"
                    }
                else:
                    logger.warning(f"No TradeStation quote data for {symbol}, falling back to Unusual Whales")
        
    except Exception as e:
        logger.warning(f"TradeStation quote failed for {symbol}: {str(e)}, falling back to Unusual Whales")
    
    # Fallback to Unusual Whales
    try:
        logger.info(f"Using Unusual Whales for {symbol} pricing (fallback)")
        
        # Get stock data from Unusual Whales screener
        uw_stocks = await uw_service.get_stock_screener_data(limit=500, exchange="all")
        
        # Find the specific symbol
        uw_stock_data = None
        for stock in uw_stocks:
            if stock.get('symbol', '').upper() == symbol.upper():
                uw_stock_data = stock
                break
        
        if uw_stock_data:
            return {
                "symbol": uw_stock_data.get("symbol", symbol),
                "price": float(uw_stock_data.get("price", 0)),
                "change": float(uw_stock_data.get("change", 0)),
                "change_percent": float(uw_stock_data.get("change_percent", 0)),
                "volume": int(uw_stock_data.get("volume", 0)),
                "market_cap": uw_stock_data.get("market_cap"),
                "pe_ratio": uw_stock_data.get("pe_ratio"),
                "timestamp": datetime.utcnow(),
                "data_source": "Unusual Whales (Fallback)"
            }
        else:
            logger.error(f"Symbol {symbol} not found in Unusual Whales data")
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found in any data source")
            
    except Exception as e:
        logger.error(f"Unusual Whales fallback also failed for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data for {symbol}: {str(e)}")

async def get_historical_data(symbol: str, period: str = "1y") -> List[Dict[str, Any]]:
    """Get historical stock data"""
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        
        data = []
        for date, row in history.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data for {symbol}: {str(e)}")

async def get_technical_indicators(symbol: str) -> Dict[str, Any]:
    """Get technical indicators for a stock"""
    try:
        # Get RSI
        rsi_data, rsi_meta = ti.get_rsi(symbol=symbol, interval='daily', time_period=14, series_type='close')
        latest_rsi = rsi_data.iloc[0]['RSI'] if not rsi_data.empty else None
        
        # Get MACD
        macd_data, macd_meta = ti.get_macd(symbol=symbol, interval='daily', series_type='close')
        latest_macd = {
            'macd': macd_data.iloc[0]['MACD'] if not macd_data.empty else None,
            'signal': macd_data.iloc[0]['MACD_Signal'] if not macd_data.empty else None,
            'histogram': macd_data.iloc[0]['MACD_Hist'] if not macd_data.empty else None
        }
        
        # Get SMA
        sma20_data, sma20_meta = ti.get_sma(symbol=symbol, interval='daily', time_period=20, series_type='close')
        sma50_data, sma50_meta = ti.get_sma(symbol=symbol, interval='daily', time_period=50, series_type='close')
        
        return {
            "symbol": symbol.upper(),
            "rsi": {"value": float(latest_rsi) if latest_rsi else None},
            "macd": latest_macd,
            "sma": {
                "sma20": float(sma20_data.iloc[0]['SMA']) if not sma20_data.empty else None,
                "sma50": float(sma50_data.iloc[0]['SMA']) if not sma50_data.empty else None
            }
        }
    except Exception as e:
        # Fallback to basic calculations if Alpha Vantage fails
        return {"symbol": symbol.upper(), "rsi": None, "macd": None, "sma": None}

# API Routes
@api_router.get("/")
async def root():
    return {
        "message": "Enhanced Stock Market Analysis API with TradeStation Integration", 
        "version": "5.0.0", 
        "features": [
            "Real-time Stock Prices",
            "Pre/Post Market Data", 
            "S&P 500 & NASDAQ Tickers",
            "Advanced Screener",
            "Extended Hours Trading",
            "Portfolio Management",
            "🎯 Investment Scoring System",
            "📊 Top Investment Picks",
            "⚖️ Risk Analysis",
            "🐋 Unusual Whales Integration",
            "📈 Options Flow Alerts",
            "🌊 Dark Pool Analysis",
            "🏛️ Congressional Trades Tracking",
            "🎯 AI-Powered Trading Strategies",
            "🏛️ TradeStation Integration",
            "📊 Live Portfolio Management",
            "⚡ Real-Time Trading",
            "🛡️ Risk Management Controls"
        ],
        "market_state": enhanced_ticker_manager._get_market_state(),
        "tradestation_endpoints": {
            "authentication": "/auth/tradestation/login",
            "auth_status": "/auth/tradestation/status",
            "accounts": "/tradestation/accounts",
            "portfolio_summary": "/tradestation/accounts/{account_id}/summary",
            "positions": "/tradestation/accounts/{account_id}/positions",
            "balances": "/tradestation/accounts/{account_id}/balances",
            "place_order": "/tradestation/accounts/{account_id}/orders",
            "orders_history": "/tradestation/accounts/{account_id}/orders",
            "trading_summary": "/tradestation/accounts/{account_id}/trading-summary"
        },
        "unusual_whales_endpoints": {
            "options_flow": "/unusual-whales/options/flow-alerts",
            "dark_pool": "/unusual-whales/dark-pool/recent", 
            "congressional": "/unusual-whales/congressional/trades",
            "comprehensive_analysis": "/unusual-whales/analysis/comprehensive",
            "trading_strategies": "/unusual-whales/trading-strategies"
        },
        "investment_endpoints": {
            "investment_score": "/investments/score/{symbol}",
            "top_picks": "/investments/top-picks",
            "sector_leaders": "/investments/sector-leaders",
            "risk_analysis": "/investments/risk-analysis"
        },
        "core_endpoints": {
            "enhanced_stock": "/stocks/{symbol}/enhanced",
            "extended_hours": "/stocks/{symbol}/extended-hours",
            "screener": "/screener/data",
            "filter": "/screener/filter",
            "data_sources_status": "/data-sources/status",
            "test_data_source": "/data-sources/test/{symbol}",
            "tradestation_quotes": "/tradestation/quotes/{symbols}"
        }
    }

# Stock Data Routes
@api_router.get("/stocks/{symbol}", response_model=StockData)
async def get_stock(symbol: str):
    """Get current stock data"""
    data = await get_stock_quote(symbol)
    return StockData(**data)

@api_router.get("/stocks/{symbol}/historical")
async def get_stock_historical_data(
    symbol: str, 
    interval: str = "1D",  # 1m, 5m, 15m, 30m, 1H, 1D
    bars_back: int = 100
):
    """Get historical OHLC data for charts"""
    try:
        # Try TradeStation first if authenticated
        if ts_auth.is_authenticated():
            try:
                async with ts_client:
                    # Map interval to TradeStation format
                    interval_map = {
                        "1m": (1, "Minute"),
                        "5m": (5, "Minute"), 
                        "15m": (15, "Minute"),
                        "30m": (30, "Minute"),
                        "1H": (1, "Hour"),
                        "1D": (1, "Daily")
                    }
                    
                    if interval in interval_map:
                        interval_val, unit = interval_map[interval]
                        bars = await ts_client.get_historical_bars(
                            symbol=symbol.upper(),
                            interval=interval_val,
                            unit=unit,
                            bars_back=bars_back
                        )
                        
                        # Format for lightweight-charts
                        chart_data = []
                        for bar in bars:
                            chart_data.append({
                                "time": bar.get("TimeStamp", "").split("T")[0],  # YYYY-MM-DD format
                                "open": float(bar.get("Open", 0)),
                                "high": float(bar.get("High", 0)),
                                "low": float(bar.get("Low", 0)),
                                "close": float(bar.get("Close", 0)),
                                "volume": int(bar.get("TotalVolume", 0))
                            })
                        
                        return {
                            "status": "success",
                            "symbol": symbol.upper(),
                            "interval": interval,
                            "data": sorted(chart_data, key=lambda x: x["time"]),
                            "count": len(chart_data),
                            "data_source": "TradeStation API",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
            except Exception as e:
                logger.warning(f"TradeStation historical data failed for {symbol}: {str(e)}")
        
        # Fallback to mock data for demo
        logger.info(f"Using mock historical data for {symbol}")
        
        # Generate realistic mock OHLC data with more data points
        from datetime import timedelta
        import random
        
        mock_data = []
        base_price = random.uniform(80, 150)  # Random starting price
        current_date = datetime.utcnow() - timedelta(days=bars_back)
        
        for i in range(bars_back):
            # Simulate realistic price movement with trends
            trend_factor = 0.0001 * i  # Slight upward trend
            volatility = random.uniform(0.01, 0.04)  # 1-4% daily volatility
            price_change = random.gauss(trend_factor, volatility)  # Normal distribution
            
            base_price *= (1 + price_change)
            base_price = max(1.0, base_price)  # Ensure positive price
            
            # Generate realistic OHLC with intraday movement
            open_price = base_price
            intraday_volatility = random.uniform(0.005, 0.025)  # 0.5-2.5% intraday
            
            # Create realistic high/low based on open/close
            close_change = random.gauss(0, intraday_volatility)
            close_price = open_price * (1 + close_change)
            
            # High and low with realistic wicks
            high_wick = random.uniform(0, 0.015)  # Up to 1.5% wick
            low_wick = random.uniform(0, 0.015)   # Up to 1.5% wick
            
            high_price = max(open_price, close_price) * (1 + high_wick)
            low_price = min(open_price, close_price) * (1 - low_wick)
            
            # Volume with realistic patterns (higher on big moves)
            price_move = abs(close_price - open_price) / open_price
            base_volume = random.randint(500000, 2000000)
            volume_multiplier = 1 + (price_move * 10)  # Higher volume on big moves
            volume = int(base_volume * volume_multiplier)
            
            mock_data.append({
                "time": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            base_price = close_price
            
            # Adjust date increment based on interval
            if interval == "1D":
                current_date += timedelta(days=1)
            elif interval == "4H":
                current_date += timedelta(hours=4)
            elif interval == "1H":
                current_date += timedelta(hours=1)
            elif interval == "15m":
                current_date += timedelta(minutes=15)
            elif interval == "5m":
                current_date += timedelta(minutes=5)
            else:
                current_date += timedelta(days=1)
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "interval": interval,
            "data": mock_data,
            "count": len(mock_data),
            "data_source": "Mock Data (Demo)",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")

@api_router.get("/stocks/{symbol}/enhanced", response_model=EnhancedStockData)
async def get_stock_enhanced(symbol: str):
    """Get enhanced stock data with TradeStation primary, Unusual Whales fallback"""
    try:
        # Try TradeStation first if authenticated
        if ts_auth.is_authenticated():
            try:
                async with ts_client:
                    quotes = await ts_client.get_quote([symbol])
                    
                if quotes and len(quotes) > 0:
                    ts_quote = quotes[0]
                    
                    # Return TradeStation data with basic enhanced structure
                    return EnhancedStockData(
                        symbol=ts_quote.symbol,
                        name=ts_quote.symbol,  # Limited data from TradeStation
                        sector="Unknown",
                        industry="Unknown", 
                        price=ts_quote.last,
                        change=ts_quote.change,
                        change_percent=ts_quote.change_percent,
                        volume=ts_quote.volume,
                        market_cap=None,
                        pe_ratio=None,
                        exchange="Unknown",
                        timestamp=datetime.utcnow().isoformat(),
                        data_source="TradeStation API (Primary)"
                    )
                        
            except Exception as e:
                logger.warning(f"TradeStation enhanced quote failed for {symbol}: {str(e)}")
        
        # Fallback to Unusual Whales
        try:
            logger.info(f"Using Unusual Whales for enhanced {symbol} (fallback)")
            
            # Get stock data from Unusual Whales
            uw_stocks = await uw_service.get_stock_screener_data(limit=500, exchange="all")
            
            # Find the specific symbol
            uw_stock_data = None
            for stock in uw_stocks:
                if stock.get('symbol', '').upper() == symbol.upper():
                    uw_stock_data = stock
                    break
            
            if uw_stock_data:
                return EnhancedStockData(
                    symbol=uw_stock_data.get("symbol", symbol),
                    name=uw_stock_data.get("name", symbol),
                    sector=uw_stock_data.get("sector", "Unknown"),
                    industry="Unknown",
                    price=float(uw_stock_data.get("price", 0)),
                    change=float(uw_stock_data.get("change", 0)),
                    change_percent=float(uw_stock_data.get("change_percent", 0)),
                    volume=int(uw_stock_data.get("volume", 0)),
                    market_cap=uw_stock_data.get("market_cap"),
                    pe_ratio=uw_stock_data.get("pe_ratio"),
                    exchange=uw_stock_data.get("exchange", "Unknown"),
                    timestamp=datetime.utcnow().isoformat(),
                    data_source="Unusual Whales (Fallback)"
                )
            else:
                logger.error(f"Symbol {symbol} not found in Unusual Whales data")
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found in any data source")
                
        except Exception as e:
            logger.error(f"Unusual Whales enhanced fallback also failed for {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching enhanced data for {symbol}: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching enhanced data for {symbol}: {str(e)}")

@api_router.get("/stocks/{symbol}/extended-hours")
async def get_extended_hours_data(symbol: str):
    """Get pre-market and post-market data for a stock"""
    try:
        enhanced_data = await enhanced_ticker_manager.get_real_time_quote(symbol)
        return {
            "symbol": symbol.upper(),
            "market_state": enhanced_data.get("market_state", "UNKNOWN"),
            "extended_hours": enhanced_data.get("extended_hours", {}),
            "regular_price": enhanced_data.get("price", 0.0),
            "timestamp": enhanced_data.get("timestamp", datetime.utcnow().isoformat())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching extended hours data for {symbol}: {str(e)}")

@api_router.get("/stocks/{symbol}/history")
async def get_stock_history(symbol: str, period: str = Query("1y", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical stock data"""
    return await get_historical_data(symbol, period)

@api_router.get("/stocks/{symbol}/indicators", response_model=TechnicalIndicatorData)
async def get_stock_indicators(symbol: str):
    """Get technical indicators for a stock"""
    data = await get_technical_indicators(symbol)
    return TechnicalIndicatorData(**data)

# NEW: Extended ticker and screener endpoints
@api_router.get("/tickers/sp500")
async def get_sp500_tickers():
    """Get S&P 500 ticker list"""
    tickers = await enhanced_ticker_manager.get_sp500_tickers()
    return {"tickers": tickers, "count": len(tickers)}

@api_router.get("/tickers/nasdaq")
async def get_nasdaq_tickers():
    """Get NASDAQ ticker list"""
    tickers = await enhanced_ticker_manager.get_nasdaq_tickers()
    return {"tickers": tickers, "count": len(tickers)}

@api_router.get("/tickers/all")
async def get_all_tickers():
    """Get all available tickers"""
    tickers = await enhanced_ticker_manager.get_all_tickers()
    return {"tickers": tickers, "count": len(tickers)}

@api_router.get("/screener/data")
async def get_screener_data(
    limit: int = Query(50, description="Maximum number of stocks to return"),
    exchange: str = Query("all", description="Exchange filter: sp500, nasdaq, or all")
):
    """Get screener data using Unusual Whales API - ENHANCED VERSION"""
    try:
        # Use Unusual Whales service for stock screener data
        uw_service = UnusualWhalesService()
        stock_data = await uw_service.get_stock_screener_data(limit=limit, exchange=exchange)
        
        # Add market state and timestamp
        return {
            "stocks": stock_data,
            "total_count": len(stock_data),
            "exchange": exchange,
            "data_source": "Unusual Whales API" if uw_service.api_token else "Mock Data",
            "last_updated": datetime.utcnow().isoformat(),
            "note": "Real-time data from Unusual Whales with options flow signals"
        }
    except Exception as e:
        logger.error(f"Error fetching Unusual Whales screener data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching screener data: {str(e)}")

@api_router.post("/screener/filter")
async def screen_stocks_enhanced(criteria: ScreenerCriteria, exchange: str = Query("all", description="Exchange to screen")):
    """Enhanced stock screening using Unusual Whales API with advanced filtering"""
    try:
        criteria_dict = criteria.dict(exclude_none=True)
        
        # Use Unusual Whales service for filtering
        uw_service = UnusualWhalesService()
        filtered_stocks = await uw_service.filter_stocks_by_criteria(criteria_dict, exchange)
        
        return {
            "stocks": filtered_stocks,
            "total_count": len(filtered_stocks),
            "criteria": criteria_dict,
            "exchange": exchange,
            "data_source": "Unusual Whales API" if uw_service.api_token else "Mock Data",
            "last_updated": datetime.utcnow().isoformat(),
            "note": "Filtered results with unusual activity indicators"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error screening stocks with enhanced data: {str(e)}")

@api_router.get("/investments/score/{symbol}", response_model=InvestmentScore)
async def get_investment_score(symbol: str):
    """Get comprehensive investment score for a specific stock"""
    try:
        # Get enhanced stock data
        stock_data = await enhanced_ticker_manager.get_real_time_quote(symbol)
        
        # Calculate investment score
        score_data = await investment_scorer.calculate_investment_score(stock_data)
        
        return InvestmentScore(**score_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating investment score for {symbol}: {str(e)}")

@api_router.get("/investments/smart-money/{symbol}", response_model=SmartMoneyAnalysis)
async def get_smart_money_analysis(symbol: str, timeframe: str = Query("3mo", description="Timeframe for analysis")):
    """Get comprehensive Smart Money Concepts and Price Action analysis for a specific stock"""
    try:
        # Perform smart money analysis
        analysis_data = await smart_money_analyzer.analyze_smart_money_concepts(symbol, timeframe)
        
        return SmartMoneyAnalysis(**analysis_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing smart money analysis for {symbol}: {str(e)}")

@api_router.get("/market/sentiment/{symbol}")
async def get_market_sentiment_analysis(symbol: str):
    """Get comprehensive market sentiment analysis for a stock"""
    try:
        sentiment_data = await market_sentiment_analyzer.analyze_market_sentiment(symbol)
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing market sentiment for {symbol}: {str(e)}")

@api_router.get("/analysis/comprehensive/{symbol}")
async def get_comprehensive_stock_analysis(symbol: str):
    """Get comprehensive analysis including fundamentals, technicals, smart money, and sentiment"""
    try:
        # Get enhanced stock data
        stock_data = await enhanced_ticker_manager.get_real_time_quote(symbol)
        
        # Run all analyses concurrently
        investment_task = investment_scorer.calculate_investment_score(stock_data)
        smart_money_task = smart_money_analyzer.analyze_smart_money_concepts(symbol)
        sentiment_task = market_sentiment_analyzer.analyze_market_sentiment(symbol)
        
        investment_score, smart_money_analysis, sentiment_analysis = await asyncio.gather(
            investment_task, smart_money_task, sentiment_task
        )
        
        return {
            "symbol": symbol.upper(),
            "current_price": stock_data.get('price', 0),
            "last_updated": datetime.utcnow().isoformat(),
            "investment_score": investment_score,
            "smart_money_analysis": smart_money_analysis,
            "sentiment_analysis": sentiment_analysis,
            "comprehensive_rating": _generate_comprehensive_rating(investment_score, smart_money_analysis, sentiment_analysis)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive analysis for {symbol}: {str(e)}")

def _generate_comprehensive_rating(investment_score: Dict, smart_money: Dict, sentiment: Dict) -> Dict[str, Any]:
    """Generate overall comprehensive rating from all analyses"""
    try:
        # Get individual ratings
        investment_rating = investment_score.get('rating', 'HOLD')
        smart_money_verdict = smart_money.get('smart_money_verdict', {}).get('verdict', 'NEUTRAL')
        sentiment_direction = sentiment.get('insights', {}).get('direction', 'UNKNOWN')
        
        # Score components
        total_score = investment_score.get('total_score', 50)
        sentiment_score = sentiment.get('composite_sentiment', {}).get('score', 0.0)  # -1 to +1
        
        # Calculate confidence based on agreement
        bullish_signals = 0
        bearish_signals = 0
        
        if investment_rating in ['BUY', 'BUY STRONG']:
            bullish_signals += 1
        elif investment_rating.startswith('HOLD'):
            pass  # neutral
        else:
            bearish_signals += 1
            
        if smart_money_verdict == 'BULLISH':
            bullish_signals += 1
        elif smart_money_verdict == 'BEARISH':
            bearish_signals += 1
            
        if sentiment_direction == 'BULLISH':
            bullish_signals += 1
        elif sentiment_direction == 'BEARISH':
            bearish_signals += 1
        
        # Overall verdict
        if bullish_signals >= 2 and bearish_signals == 0:
            overall_verdict = "STRONG BUY"
            confidence = "HIGH"
        elif bullish_signals > bearish_signals:
            overall_verdict = "BUY"  
            confidence = "MEDIUM" if bullish_signals >= 2 else "LOW"
        elif bearish_signals > bullish_signals:
            overall_verdict = "SELL"
            confidence = "MEDIUM" if bearish_signals >= 2 else "LOW"
        elif bearish_signals >= 2 and bullish_signals == 0:
            overall_verdict = "STRONG SELL"
            confidence = "HIGH"
        else:
            overall_verdict = "HOLD"
            confidence = "LOW"
        
        return {
            "overall_verdict": overall_verdict,
            "confidence": confidence,
            "agreement_score": abs(bullish_signals - bearish_signals),
            "supporting_analyses": {
                "investment_score": investment_rating,
                "smart_money": smart_money_verdict,
                "sentiment": sentiment_direction
            },
            "summary": f"Comprehensive analysis shows {overall_verdict} recommendation with {confidence.lower()} confidence based on {bullish_signals + bearish_signals} analytical approaches."
        }
        
    except Exception as e:
        logger.error(f"Error generating comprehensive rating: {str(e)}")
        return {
            "overall_verdict": "HOLD",
            "confidence": "LOW", 
            "agreement_score": 0,
            "supporting_analyses": {},
            "summary": "Unable to generate comprehensive rating due to analysis errors."
        }
# ===========================================
# STOCK SCANNER ENDPOINTS 🔍
# ===========================================

# Instanță globală de scanner
global_scanner = None

@api_router.post("/scanner/start-scan")
async def start_stock_scan():
    """Pornește scanarea completă a tuturor tickerelor"""
    try:
        global global_scanner
        
        # Inițializează scanner-ul dacă nu există
        if global_scanner is None:
            global_scanner = StockScanner(investment_scorer)
            
        logger.info("🚀 Pornire scanare completă...")
        
        # Pornește scanarea (asincron)
        scan_task = asyncio.create_task(global_scanner.scan_all_stocks())
        
        return {
            "status": "started",
            "message": "Scanarea a început. Verifică progresul cu /scanner/status",
            "estimated_duration": "15-30 minute pentru ~100 tickere"
        }
        
    except Exception as e:
        logger.error(f"Eroare la pornirea scanării: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la pornirea scanării: {str(e)}")

@api_router.get("/scanner/top-stocks")
async def get_scanner_top_stocks(limit: int = Query(50, description="Numărul de acțiuni top")):
    """Obține top acțiuni din ultimul scan"""
    try:
        global global_scanner
        
        if global_scanner is None:
            global_scanner = StockScanner(investment_scorer)
            
        top_stocks = await global_scanner.get_top_stocks(limit)
        
        # ENHANCED: Get fresh price data for each stock
        enhanced_stocks = []
        for stock in top_stocks:
            ticker = stock.get('ticker')
            
            # Try to get fresh price data
            try:
                from enhanced_ticker_data import enhanced_ticker_manager
                fresh_data = await enhanced_ticker_manager.get_real_time_quote(ticker)
                
                enhanced_stock = {
                    "ticker": ticker,
                    "score": round(stock.get('total_score', 0), 1),
                    "rating": stock.get('rating'),
                    "price": fresh_data.get('price') if fresh_data else stock.get('stock_data', {}).get('price', 'N/A'),
                    "sector": fresh_data.get('sector') if fresh_data else stock.get('stock_data', {}).get('sector', 'N/A'),
                    "explanation": stock.get('explanation', '')[:100] + "..." if len(stock.get('explanation', '')) > 100 else stock.get('explanation', '')
                }
            except Exception as e:
                # Fallback to original data structure
                enhanced_stock = {
                    "ticker": ticker,
                    "score": round(stock.get('total_score', 0), 1),
                    "rating": stock.get('rating'),
                    "price": stock.get('stock_data', {}).get('price', 'N/A'),
                    "sector": stock.get('stock_data', {}).get('sector', 'N/A'),
                    "explanation": stock.get('explanation', '')[:100] + "..." if len(stock.get('explanation', '')) > 100 else stock.get('explanation', '')
                }
            
            enhanced_stocks.append(enhanced_stock)
        
        return {
            "total_found": len(enhanced_stocks),
            "limit": limit,
            "scan_date": top_stocks[0].get('scanned_at') if top_stocks else None,
            "top_stocks": enhanced_stocks
        }
        
    except Exception as e:
        logger.error(f"Eroare la obținerea top acțiuni: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea top acțiuni: {str(e)}")

@api_router.get("/scanner/status")
async def get_scanner_status():
    """Obține statusul scanărilor și statistici"""
    try:
        # Verifică dacă există rezultate în MongoDB
        from investment_scoring import scanned_stocks_collection
        
        total_stocks = await scanned_stocks_collection.count_documents({})
        
        if total_stocks > 0:
            # Găsește cel mai recent scan
            latest_scan = await scanned_stocks_collection.find_one(
                {}, sort=[('scanned_at', -1)]
            )
            
            # Top 5 acțiuni
            top_5 = []
            async for stock in scanned_stocks_collection.find({}).sort('total_score', -1).limit(5):
                top_5.append({
                    'ticker': stock.get('ticker'),
                    'score': round(stock.get('total_score', 0), 1),
                    'rating': stock.get('rating')
                })
            
            return {
                "status": "completed" if total_stocks > 0 else "no_scans",
                "total_stocks_scanned": total_stocks,
                "last_scan_date": latest_scan.get('scanned_at') if latest_scan else None,
                "scan_id": latest_scan.get('scan_id') if latest_scan else None,
                "top_5_stocks": top_5,
                "database_status": "active"
            }
        else:
            return {
                "status": "no_scans",
                "message": "Nu există scanări în baza de date. Pornește o scanare cu /scanner/start-scan",
                "total_stocks_scanned": 0,
                "database_status": "empty"
            }
            
    except Exception as e:
        logger.error(f"Eroare la obținerea statusului: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la obținerea statusului: {str(e)}")

# ===========================================

@api_router.get("/investments/top-picks", response_model=TopInvestments)
async def get_top_investment_picks(
    limit: int = Query(10, description="Number of top picks to return"),
    min_market_cap: float = Query(1000, description="Minimum market cap in millions"),
    exchange: str = Query("sp500", description="Exchange filter: sp500, nasdaq, or all")
):
    """Get top investment picks based on comprehensive scoring - OPTIMIZED VERSION"""
    try:
        # Use a curated list of high-quality stocks for faster processing
        if exchange == "sp500":
            # Top 20 S&P 500 stocks by market cap for fast processing
            tickers = ["AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", 
                      "BRK.B", "UNH", "JNJ", "JPM", "V", "PG", "XOM", "HD", "CVX", "MA", "ABBV", "PFE"]
        elif exchange == "nasdaq":
            # Top NASDAQ stocks
            tickers = ["AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", 
                      "NFLX", "ADBE", "CRM", "PYPL", "INTC", "CMCSA", "CSCO", "AVGO", "TXN", "QCOM", "COST", "AMD"]
        else:
            # Mixed high-quality stocks from both exchanges
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", 
                      "UNH", "JNJ", "JPM", "V", "PG", "HD", "MA", "NFLX", "ADBE", "CRM", "PYPL", "WMT"]
        
        # Get enhanced data for selected stocks (much faster with curated list)
        stocks_data = await enhanced_ticker_manager.get_bulk_real_time_data(tickers)
        
        # Filter by market cap if specified
        filtered_stocks = []
        for stock in stocks_data:
            market_cap = stock.get('market_cap', 0)
            if market_cap and market_cap >= (min_market_cap * 1e6):
                filtered_stocks.append(stock)
        
        # Calculate investment scores for filtered stocks
        scored_stocks = []
        for stock_data in filtered_stocks[:15]:  # Process max 15 for speed
            try:
                score_data = await investment_scorer.calculate_investment_score(stock_data)
                scored_stocks.append(score_data)
            except Exception as e:
                logger.error(f"Error scoring {stock_data.get('symbol', 'unknown')}: {str(e)}")
                continue
        
        # Sort by total score (descending)
        scored_stocks.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Get top picks
        top_picks = scored_stocks[:limit]
        
        return TopInvestments(
            recommendations=[InvestmentScore(**pick) for pick in top_picks],
            total_analyzed=len(scored_stocks),
            criteria=f"Min Market Cap: ${min_market_cap}M, Exchange: {exchange}, Curated High-Quality Stocks",
            last_updated=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating top investment picks: {str(e)}")

@api_router.get("/investments/sector-leaders")
async def get_sector_leaders(sector: str = Query("Technology", description="Sector to analyze")):
    """Get top investment picks within a specific sector"""
    try:
        # Get all tickers and filter by sector
        all_tickers = await enhanced_ticker_manager.get_all_tickers()
        stocks_data = await enhanced_ticker_manager.get_bulk_real_time_data(all_tickers[:30])
        
        # Filter by sector
        sector_stocks = [stock for stock in stocks_data if stock.get('sector') == sector]
        
        if not sector_stocks:
            return {
                "sector": sector,
                "leaders": [],
                "message": f"No stocks found in {sector} sector or data unavailable"
            }
        
        # Calculate scores for sector stocks
        scored_stocks = []
        for stock_data in sector_stocks:
            try:
                score_data = await investment_scorer.calculate_investment_score(stock_data)
                scored_stocks.append(score_data)
            except Exception as e:
                continue
        
        # Sort by score
        scored_stocks.sort(key=lambda x: x['total_score'], reverse=True)
        
        return {
            "sector": sector,
            "leaders": [InvestmentScore(**stock) for stock in scored_stocks[:5]],
            "total_analyzed": len(scored_stocks),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sector leaders: {str(e)}")

@api_router.get("/investments/risk-analysis")
async def get_risk_analysis():
    """Get investment recommendations categorized by risk level"""
    try:
        # Get top stocks for analysis
        tickers = await enhanced_ticker_manager.get_sp500_tickers()
        stocks_data = await enhanced_ticker_manager.get_bulk_real_time_data(tickers[:25])
        
        # Calculate scores and categorize by risk
        risk_categories = {"LOW": [], "MODERATE": [], "HIGH": []}
        
        for stock_data in stocks_data:
            try:
                score_data = await investment_scorer.calculate_investment_score(stock_data)
                risk_level = score_data['risk_level']
                
                if risk_level in risk_categories and len(risk_categories[risk_level]) < 5:
                    risk_categories[risk_level].append(InvestmentScore(**score_data))
                    
            except Exception as e:
                continue
        
        # Sort each category by score
        for risk_level in risk_categories:
            risk_categories[risk_level].sort(key=lambda x: x.total_score, reverse=True)
        
        return {
            "risk_categories": risk_categories,
            "total_analyzed": len(stocks_data),
            "methodology": "Risk assessed based on beta, market cap, volatility, and financial stability",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing risk analysis: {str(e)}")

@api_router.get("/screener/sectors")
async def get_available_sectors():
    """Get list of available sectors for filtering"""
    sectors = [
        "All", "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
        "Communication Services", "Industrials", "Consumer Defensive", "Energy",
        "Utilities", "Real Estate", "Basic Materials"
    ]
    return {"sectors": sectors}

@api_router.get("/data-sources/status")
async def get_data_sources_status():
    """Get current data sources status and priority"""
    try:
        # Check TradeStation authentication
        ts_authenticated = ts_auth.is_authenticated()
        ts_status = "Available" if ts_authenticated else "Not Authenticated"
        
        # Test connection if authenticated
        ts_connection_test = None
        if ts_authenticated:
            try:
                async with ts_client:
                    ts_connection_test = await ts_client.test_connection()
            except Exception as e:
                ts_connection_test = {"status": "error", "message": str(e)}
        
        return {
            "data_source_priority": [
                {
                    "rank": 1,
                    "source": "TradeStation API",
                    "status": ts_status,
                    "authenticated": ts_authenticated,
                    "connection_test": ts_connection_test,
                    "usage": "Primary data source when authenticated",
                    "reliability": "High (User's Brokerage Data)"
                },
                {
                    "rank": 2, 
                    "source": "Unusual Whales",
                    "status": "Available",
                    "usage": "Fallback data source",
                    "reliability": "High (Professional Market Data)"
                }
            ],
            "current_primary_source": "TradeStation API" if ts_authenticated else "Unusual Whales",
            "recommendation": "Authenticate with TradeStation for most accurate pricing data" if not ts_authenticated else "Using TradeStation for accurate pricing ✅",
            "yahoo_finance_status": "❌ REMOVED - No longer used as data source",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Error checking data sources: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.get("/data-sources/test/{symbol}")
async def test_data_sources(symbol: str):
    """Test different data sources for a specific symbol"""
    results = {}
    
    # Test TradeStation
    try:
        if ts_auth.is_authenticated():
            async with ts_client:
                quotes = await ts_client.get_quote([symbol])
                if quotes:
                    ts_quote = quotes[0]
                    results["tradestation"] = {
                        "status": "success",
                        "price": ts_quote.last,
                        "change": ts_quote.change,
                        "change_percent": ts_quote.change_percent,
                        "volume": ts_quote.volume,
                        "timestamp": ts_quote.timestamp.isoformat()
                    }
                else:
                    results["tradestation"] = {"status": "no_data", "message": "No quote data returned"}
        else:
            results["tradestation"] = {"status": "not_authenticated", "message": "TradeStation not authenticated"}
    except Exception as e:
        results["tradestation"] = {"status": "error", "message": str(e)}
    
    # Test Unusual Whales
    try:
        uw_stocks = await uw_service.get_stock_screener_data(limit=500, exchange="all")
        uw_stock_data = None
        
        for stock in uw_stocks:
            if stock.get('symbol', '').upper() == symbol.upper():
                uw_stock_data = stock
                break
        
        if uw_stock_data:
            results["unusual_whales"] = {
                "status": "success",
                "price": float(uw_stock_data.get("price", 0)),
                "change": float(uw_stock_data.get("change", 0)),
                "change_percent": float(uw_stock_data.get("change_percent", 0)),
                "volume": int(uw_stock_data.get("volume", 0)),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            results["unusual_whales"] = {"status": "symbol_not_found", "message": f"Symbol {symbol} not found in UW data"}
            
    except Exception as e:
        results["unusual_whales"] = {"status": "error", "message": str(e)}
    
    # Show which source would be used (2-tier priority)
    if ts_auth.is_authenticated() and results.get("tradestation", {}).get("status") == "success":
        primary_source = "tradestation"
    elif results.get("unusual_whales", {}).get("status") == "success":
        primary_source = "unusual_whales"
    else:
        primary_source = "none_available"
    
    return {
        "symbol": symbol.upper(),
        "test_results": results,
        "primary_source_used": primary_source,
        "price_comparison": {
            "tradestation_price": results.get("tradestation", {}).get("price"),
            "unusual_whales_price": results.get("unusual_whales", {}).get("price"),
            "price_difference": None if not (results.get("tradestation", {}).get("price") and results.get("unusual_whales", {}).get("price")) 
                        else round(results["tradestation"]["price"] - results["unusual_whales"]["price"], 2)
        },
        "yahoo_finance_status": "❌ REMOVED - No longer tested as data source",
        "timestamp": datetime.utcnow().isoformat()
    }
@api_router.get("/stocks/search/{query}")
async def search_stocks(query: str):
    """Search for stocks by symbol or company name"""
    try:
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        
        if not info.get('symbol'):
            return {"results": []}
        
        return {
            "results": [{
                "symbol": info.get('symbol', query.upper()),
                "name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A')
            }]
        }
    except:
        return {"results": []}

# Portfolio Routes (unchanged)
@api_router.post("/portfolio", response_model=PortfolioItem)
async def add_portfolio_item(item: PortfolioItemCreate):
    """Add item to portfolio"""
    current_data = await get_stock_quote(item.symbol)
    
    portfolio_item = PortfolioItem(
        **item.dict(),
        current_price=current_data['price'],
        current_value=current_data['price'] * item.shares,
        profit_loss=(current_data['price'] - item.purchase_price) * item.shares,
        profit_loss_percent=((current_data['price'] - item.purchase_price) / item.purchase_price) * 100
    )
    
    await db.portfolio.insert_one(portfolio_item.dict())
    return portfolio_item

@api_router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio():
    """Get complete portfolio with current values"""
    items = await db.portfolio.find().to_list(1000)
    portfolio_items = []
    
    total_value = 0
    total_cost = 0
    
    for item_data in items:
        try:
            current_data = await get_stock_quote(item_data['symbol'])
            item_data['current_price'] = current_data['price']
            item_data['current_value'] = current_data['price'] * item_data['shares']
            item_data['profit_loss'] = (current_data['price'] - item_data['purchase_price']) * item_data['shares']
            item_data['profit_loss_percent'] = ((current_data['price'] - item_data['purchase_price']) / item_data['purchase_price']) * 100
            
            total_value += item_data['current_value']
            total_cost += item_data['purchase_price'] * item_data['shares']
        except:
            item_data['current_price'] = item_data.get('current_price', item_data['purchase_price'])
            item_data['current_value'] = item_data.get('current_value', item_data['purchase_price'] * item_data['shares'])
            
        portfolio_items.append(PortfolioItem(**item_data))
    
    total_profit_loss = total_value - total_cost
    total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
    
    return PortfolioSummary(
        total_value=total_value,
        total_cost=total_cost,
        total_profit_loss=total_profit_loss,
        total_profit_loss_percent=total_profit_loss_percent,
        items=portfolio_items
    )

@api_router.delete("/portfolio/{item_id}")
async def delete_portfolio_item(item_id: str):
    """Delete item from portfolio"""
    result = await db.portfolio.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return {"message": "Portfolio item deleted successfully"}

# Watchlist Routes (unchanged)
@api_router.post("/watchlist", response_model=WatchlistItem)
async def add_watchlist_item(item: WatchlistItemCreate):
    """Add stock to watchlist"""
    watchlist_item = WatchlistItem(**item.dict())
    await db.watchlist.insert_one(watchlist_item.dict())
    return watchlist_item

@api_router.get("/watchlist", response_model=List[WatchlistItem])
async def get_watchlist():
    """Get user's watchlist"""
    items = await db.watchlist.find().to_list(1000)
    return [WatchlistItem(**item) for item in items]

@api_router.delete("/watchlist/{item_id}")
async def delete_watchlist_item(item_id: str):
    """Delete item from watchlist"""
    result = await db.watchlist.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    return {"message": "Watchlist item deleted successfully"}

# Market Overview Routes (unchanged)
@api_router.get("/market/overview")
async def get_market_overview():
    """Get market overview with ETF symbols for direct trading - UPDATED TO SHOW ETF SYMBOLS"""
    try:
        # Use tradeable ETF symbols directly for display
        etf_symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
        
        # Display names for ETFs
        etf_display_names = [
            'SPY (SPDR S&P 500 ETF)',
            'QQQ (Invesco QQQ Trust)',
            'DIA (SPDR Dow Jones ETF)',
            'IWM (iShares Russell 2000 ETF)'
        ]
        
        indices_data = []
        
        # Get ETF data from Unusual Whales API first
        uw_service = UnusualWhalesService()
        etf_data_dict = await uw_service.get_etf_data_for_futures(etf_symbols)
        
        logger.info(f"Unusual Whales returned data for {len(etf_data_dict)} ETFs: {list(etf_data_dict.keys())}")
        
        for i, symbol in enumerate(etf_symbols):
            try:
                # Use ETF symbol directly for display (no futures mapping)
                display_symbol = symbol  # SPY, QQQ, DIA, IWM
                
                # Check if we have live data from Unusual Whales
                if symbol in etf_data_dict:
                    etf_data = etf_data_dict[symbol]
                    
                    indices_data.append({
                        "symbol": display_symbol,  # Display ETF symbol directly
                        "name": etf_display_names[i],
                        "price": round(etf_data.get('price', 0), 2),
                        "change": round(etf_data.get('change', 0), 2),
                        "change_percent": round(etf_data.get('change_percent', 0), 2),
                        "underlying_symbol": symbol,  # Same as display symbol for ETFs
                        "data_source": "Unusual Whales API (Live ETF Data)",
                        "unusual_activity": etf_data.get('unusual_activity', False),
                        "options_flow_signal": etf_data.get('options_flow_signal', 'neutral'),
                        "volume": etf_data.get('volume', 0),
                        "market_cap": etf_data.get('market_cap', 0)
                    })
                    logger.info(f"Using live Unusual Whales data for {symbol}: ${etf_data.get('price', 0):.2f}")
                    continue
                
                # Fallback to yfinance if Unusual Whales doesn't have the ETF
                logger.warning(f"No Unusual Whales data for {symbol}, using yfinance fallback")
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty and 'regularMarketPrice' in info:
                    current_price = info.get('regularMarketPrice', hist['Close'].iloc[-1])
                    previous_close = info.get('regularMarketPreviousClose', hist['Close'].iloc[0])
                    
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                    
                    indices_data.append({
                        "symbol": display_symbol,  # Display ETF symbol directly
                        "name": etf_display_names[i],
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "underlying_symbol": symbol,  # Same as display symbol for ETFs
                        "data_source": "Yahoo Finance (ETF Live Data)",
                        "unusual_activity": False,  # Not available from yfinance
                        "options_flow_signal": "neutral",  # Not available from yfinance
                        "volume": info.get('regularMarketVolume', 0),
                        "market_cap": info.get('marketCap', 0)
                    })
                    logger.info(f"Using yfinance data for {symbol}: ${current_price:.2f}")
                else:
                    # Use fallback data if yfinance also fails
                    logger.error(f"Both Unusual Whales and yfinance failed for {symbol}")
                    fallback_data = get_fallback_etf_data(symbol, display_symbol, etf_display_names[i])
                    indices_data.append(fallback_data)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                # Use fallback data for this ETF
                fallback_data = get_fallback_etf_data(symbol, symbol, etf_display_names[i])
                indices_data.append(fallback_data)
        
        # Determine primary data source with better messaging
        uw_count = sum(1 for index in indices_data if "Unusual Whales" in index.get('data_source', ''))
        yf_count = sum(1 for index in indices_data if "Yahoo Finance" in index.get('data_source', ''))
        mock_count = sum(1 for index in indices_data if "Mock Data" in index.get('data_source', ''))
        
        if uw_count >= 2:
            primary_source = f"Unusual Whales API (Live Data for {uw_count}/4 ETFs)"
            note_text = f"Live ETF data from Unusual Whales API. {uw_count} ETFs with UW data, {yf_count} with real-time market data."
        elif yf_count >= 2:
            primary_source = f"Live Market Data (Real-time ETF prices for {yf_count}/4 ETFs)"
            note_text = f"Live ETF market data with real-time prices. Showing actual tradeable ETF symbols."
        else:
            primary_source = f"Fallback Data ({mock_count}/4 using mock data)"
            note_text = f"Using mock data due to API issues. {mock_count} ETFs with simulated data."
        
        return {
            "indices": indices_data,
            "data_source": primary_source,
            "note": note_text,
            "last_updated": datetime.utcnow().isoformat(),
            "unusual_whales_coverage": f"{uw_count}/4 ETFs",
            "live_data_status": "Live ETF prices available" if yf_count >= 2 else "Limited live data"
        }
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {str(e)}")
        # Return complete fallback with ETF symbols
        fallback_indices = []
        etf_symbols_fallback = ['SPY', 'QQQ', 'DIA', 'IWM']
        display_names_fallback = [
            'SPY (SPDR S&P 500 ETF)',
            'QQQ (Invesco QQQ Trust)',
            'DIA (SPDR Dow Jones ETF)',
            'IWM (iShares Russell 2000 ETF)'
        ]
        
        for i, (etf_sym, display_name) in enumerate(zip(etf_symbols_fallback, display_names_fallback)):
            fallback_data = get_fallback_etf_data(etf_sym, etf_sym, display_name)
            fallback_indices.append(fallback_data)
        
        return {
            "indices": fallback_indices,
            "data_source": "Fallback Data (ETF Symbols)",
            "note": "Using mock ETF data due to API failures - ETF symbols provide tradeable instruments",
            "last_updated": datetime.utcnow().isoformat(),
            "unusual_whales_coverage": "0/4 ETFs",
            "live_data_status": "Mock data only"
        }

def get_fallback_market_data(symbol):
    """Generate realistic fallback market data based on symbol"""
    import random
    
    fallback_mapping = {
        '^GSPC': {'name': 'S&P 500', 'base_price': 6420, 'volatility': 50},
        '^DJI': {'name': 'Dow Jones', 'base_price': 44400, 'volatility': 200},
        '^IXIC': {'name': 'NASDAQ', 'base_price': 21600, 'volatility': 100},
        '^RUT': {'name': 'Russell 2000', 'base_price': 2280, 'volatility': 30}
    }
    
    if symbol not in fallback_mapping:
        return None
    
    data = fallback_mapping[symbol]
    
    # Generate realistic price movements (small daily changes)
    price_change = random.uniform(-data['volatility'], data['volatility'])
    current_price = data['base_price'] + price_change
    change_percent = random.uniform(-2.5, 2.5)  # Realistic daily change
    change = (change_percent / 100) * current_price
    
    return {
        "symbol": symbol,
        "name": data['name'],
        "price": round(current_price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2)
    }

def get_fallback_etf_data(etf_symbol, futures_symbol, display_name):
    """Generate realistic fallback ETF data for futures-style display"""
    import random
    
    etf_mapping = {
        'SPY': {'name': 'SPDR S&P 500 ETF', 'base_price': 642, 'volatility': 5},
        'QQQ': {'name': 'Invesco QQQ Trust', 'base_price': 216, 'volatility': 10},
        'DIA': {'name': 'SPDR Dow Jones Industrial Average ETF', 'base_price': 444, 'volatility': 8},
        'IWM': {'name': 'iShares Russell 2000 ETF', 'base_price': 228, 'volatility': 3}
    }
    
    if etf_symbol not in etf_mapping:
        # Default fallback
        data = {'name': display_name, 'base_price': 100, 'volatility': 5}
    else:
        data = etf_mapping[etf_symbol]
    
    # Generate realistic price movements (small daily changes)
    price_change = random.uniform(-data['volatility'], data['volatility'])
    current_price = data['base_price'] + price_change
    change_percent = random.uniform(-2.5, 2.5)  # Realistic daily change
    change = (change_percent / 100) * current_price
    
    return {
        "symbol": futures_symbol,  # Display as futures symbol
        "name": display_name,
        "price": round(current_price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "underlying_symbol": etf_symbol,  # Track the ETF symbol used
        "data_source": "Mock Data (ETF Futures Style)",
        "unusual_activity": False,
        "options_flow_signal": "neutral"
    }

def get_fallback_etf_data(etf_symbol, futures_symbol, display_name):
    """Generate realistic fallback ETF data for futures-style display"""
    import random
    
    etf_mapping = {
        'SPY': {'name': 'SPDR S&P 500 ETF', 'base_price': 642, 'volatility': 5},
        'QQQ': {'name': 'Invesco QQQ Trust', 'base_price': 580, 'volatility': 10},
        'DIA': {'name': 'SPDR Dow Jones Industrial Average ETF', 'base_price': 449, 'volatility': 8},
        'IWM': {'name': 'iShares Russell 2000 ETF', 'base_price': 231, 'volatility': 3}
    }
    
    if etf_symbol not in etf_mapping:
        # Default fallback
        data = {'name': display_name, 'base_price': 100, 'volatility': 5}
    else:
        data = etf_mapping[etf_symbol]
    
    # Generate realistic price movement
    current_price = data['base_price'] + random.uniform(-data['volatility'], data['volatility'])
    previous_close = current_price + random.uniform(-2, 2)
    change = current_price - previous_close
    change_percent = (change / previous_close) * 100
    
    # Generate unusual activity with lower probability for ETFs
    unusual_activity = random.random() < 0.15  # 15% chance
    options_signals = ['bullish', 'bearish', 'neutral', 'neutral', 'neutral']  # Mostly neutral
    
    return {
        "symbol": futures_symbol,  # Display as futures symbol (SPX, NQ, YM, RTY)
        "name": display_name,
        "price": round(current_price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "underlying_symbol": etf_symbol,  # Track the ETF symbol used
        "data_source": "Mock Data (ETF Futures Style)",
        "unusual_activity": unusual_activity,
        "options_flow_signal": random.choice(options_signals)
    }

def get_complete_fallback_dataset():
    """Generate complete fallback dataset for all ETF equivalents"""
    return [
        get_fallback_etf_data('SPY', 'SPX', 'SPX (via SPY ETF)'),
        get_fallback_etf_data('QQQ', 'NQ', 'NQ (via QQQ ETF)'), 
        get_fallback_etf_data('DIA', 'YM', 'YM (via DIA ETF)'),
        get_fallback_etf_data('IWM', 'RTY', 'RTY (via IWM ETF)')
    ]

@api_router.get("/market/top-movers")
async def get_top_movers():
    """Get top gainers and losers with fallback for API failures"""
    try:
        # Sample of popular stocks for fallback
        stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'WMT',
                        'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX']
        
        gainers = []
        losers = []
        
        # Try to get real data first
        for symbol in stock_symbols[:12]:  # Limit to avoid timeout
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2 and 'regularMarketPrice' in info:
                    current_price = info.get('regularMarketPrice', hist['Close'].iloc[-1])
                    previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
                    
                    stock_data = {
                        "symbol": symbol,
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2)
                    }
                    
                    if change_percent > 0:
                        gainers.append(stock_data)
                    else:
                        losers.append(stock_data)
                
                # Break early if we have enough data
                if len(gainers) >= 5 and len(losers) >= 5:
                    break
                    
            except Exception as e:
                logging.warning(f"Failed to get data for {symbol}: {e}")
                continue
        
        # If we don't have enough real data, use fallback
        if len(gainers) < 3 or len(losers) < 3:
            logging.warning("Insufficient real market data. Using fallback top movers.")
            fallback_data = get_fallback_top_movers()
            gainers = fallback_data['gainers']
            losers = fallback_data['losers']
        
        # Sort and limit results
        gainers = sorted(gainers, key=lambda x: x['change_percent'], reverse=True)[:5]
        losers = sorted(losers, key=lambda x: x['change_percent'])[:5]
        
        return {
            "gainers": gainers,
            "losers": losers,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Top movers error: {e}")
        # Always return fallback data
        fallback_data = get_fallback_top_movers()
        return {
            "gainers": fallback_data['gainers'],
            "losers": fallback_data['losers'], 
            "last_updated": datetime.now().isoformat(),
            "note": "Using simulated data due to market data provider issues"
        }

def get_fallback_top_movers():
    """Generate realistic fallback top movers data"""
    import random
    
    # Common stock symbols with realistic base prices
    stocks_data = {
        'META': 650, 'BAC': 47, 'HD': 396, 'DIS': 103, 'JPM': 242,
        'MCD': 301, 'TSLA': 334, 'KO': 70, 'ORCL': 184, 'COST': 1036,
        'NVDA': 515, 'AAPL': 229, 'MSFT': 528, 'GOOGL': 203, 'AMZN': 220
    }
    
    gainers = []
    losers = []
    
    # Generate realistic gainers (positive changes)
    for symbol, base_price in list(stocks_data.items())[:8]:
        change_percent = random.uniform(0.5, 4.5)  # Realistic daily gains
        change = (change_percent / 100) * base_price
        current_price = base_price + random.uniform(-10, 10)  # Small price variation
        
        if len(gainers) < 5:
            gainers.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2)
            })
        else:
            # Make these losers with negative changes
            change_percent = -random.uniform(0.3, 3.2)
            change = (change_percent / 100) * base_price
            losers.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2)
            })
    
    return {"gainers": gainers, "losers": losers}

# ==================== UNUSUAL WHALES API ENDPOINTS ====================

@api_router.get("/unusual-whales/options/flow-alerts")
async def get_unusual_whales_options_flow(
    minimum_premium: Optional[int] = Query(200000, description="Minimum premium in dollars"),
    minimum_volume_oi_ratio: Optional[float] = Query(1.0, description="Minimum volume to OI ratio"),
    limit: Optional[int] = Query(100, description="Maximum number of alerts to return"),
    include_analysis: Optional[bool] = Query(True, description="Include pattern analysis")
):
    """Get options flow alerts from Unusual Whales with analysis"""
    try:
        # Get options flow alerts
        alerts = await uw_service.get_options_flow_alerts(
            minimum_premium=minimum_premium,
            minimum_volume_oi_ratio=minimum_volume_oi_ratio,
            limit=limit
        )
        
        response_data = {
            "status": "success",
            "data": {
                "alerts": alerts,
                "summary": {
                    "total_alerts": len(alerts),
                    "total_premium": sum(alert.get('premium', 0) for alert in alerts),
                    "avg_premium": sum(alert.get('premium', 0) for alert in alerts) / len(alerts) if alerts else 0,
                    "bullish_count": len([a for a in alerts if a.get('sentiment') == 'bullish']),
                    "bearish_count": len([a for a in alerts if a.get('sentiment') == 'bearish']),
                    "opening_trades": len([a for a in alerts if a.get('is_opener', False)]),
                    "unusual_activity": len([a for a in alerts if a.get('unusual_activity', False)])
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add analysis if requested
        if include_analysis and alerts:
            analysis = await uw_service.analyze_options_flow_patterns(alerts)
            response_data["analysis"] = analysis
            
        return response_data
        
    except Exception as e:
        logger.error(f"Error in options flow endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching options flow: {str(e)}")
@api_router.get("/unusual-whales/options/flow-alerts/debug")
async def debug_options_flow():
    """Debug endpoint for options flow data"""
    try:
        # Test direct API call
        import httpx
        api_token = os.getenv("UW_API_TOKEN")
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Try different possible endpoints
        endpoints_to_test = [
            "https://api.unusualwhales.com/api/options/flow-alerts",
            "https://api.unusualwhales.com/api/options/flow",
            "https://api.unusualwhales.com/api/flow",
            "https://api.unusualwhales.com/api/options"
        ]
        
        results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints_to_test:
                try:
                    response = await client.get(f"{endpoint}?limit=2", headers=headers)
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "response": response.text[:200] if response.text else "No response"
                    }
                except Exception as e:
                    results[endpoint] = {"error": str(e)}
        
        # Also test our mock data generation
        mock_data = await uw_service._get_mock_options_flow()
        
        return {
            "api_test_results": results,
            "mock_data_sample": mock_data[:2] if mock_data else [],
            "using_mock_data": True,
            "note": "Options flow endpoints not available - using mock data"
        }
            
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/unusual-whales/dark-pool/recent")
async def get_unusual_whales_dark_pool(
    limit: Optional[int] = Query(100, description="Maximum number of trades to return"),
    minimum_volume: Optional[int] = Query(100000, description="Minimum dark volume"),
    minimum_dark_percentage: Optional[float] = Query(0.01, description="Minimum dark pool percentage"),
    include_analysis: Optional[bool] = Query(True, description="Include pattern analysis")
):
    """Get recent dark pool activity from Unusual Whales"""
    try:
        # Get dark pool trades
        trades = await uw_service.get_recent_dark_pool_activity(
            limit=limit,
            minimum_volume=minimum_volume
        )
        
        # Filter by dark percentage
        filtered_trades = [
            trade for trade in trades 
            if trade.get('dark_percentage', 0) >= minimum_dark_percentage
        ]
        
        # Sort by significance and volume
        sorted_trades = sorted(
            filtered_trades,
            key=lambda x: (
                {"very_high": 4, "high": 3, "medium": 2, "low": 1}.get(x.get('significance', 'low'), 1),
                x.get('dark_volume', 0)
            ),
            reverse=True
        )
        
        response_data = {
            "status": "success", 
            "data": {
                "trades": sorted_trades,
                "summary": {
                    "total_trades": len(sorted_trades),
                    "total_dark_volume": sum(trade.get('dark_volume', 0) for trade in sorted_trades),
                    "avg_dark_percentage": sum(trade.get('dark_percentage', 0) for trade in sorted_trades) / len(sorted_trades) if sorted_trades else 0,
                    "institutional_signals": len([t for t in sorted_trades if t.get('institutional_signal', False)]),
                    "high_significance": len([t for t in sorted_trades if t.get('significance') in ['high', 'very_high']])
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add analysis if requested
        if include_analysis and sorted_trades:
            analysis = await uw_service.analyze_dark_pool_patterns(sorted_trades)
            response_data["analysis"] = analysis
            
        return response_data
        
    except Exception as e:
        logger.error(f"Error in dark pool endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching dark pool data: {str(e)}")

@api_router.get("/unusual-whales/dark-pool/debug")
async def debug_dark_pool():
    """Debug endpoint for dark pool data"""
    try:
        # Test direct API call
        import httpx
        api_token = os.getenv("UW_API_TOKEN")
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.unusualwhales.com/api/darkpool/recent?limit=3", 
                headers=headers
            )
            
            raw_data = response.json()
            
            # Test processing
            processed_trades = []
            if raw_data.get('data'):
                for trade in raw_data['data'][:2]:  # Just test first 2
                    processed = uw_service._process_dark_pool_trade(trade)
                    processed_trades.append(processed)
            
            return {
                "raw_api_response": raw_data,
                "processed_trades": processed_trades,
                "api_status": response.status_code
            }
            
    except Exception as e:
        return {"error": str(e)}

# ==================== TRADESTATION API ENDPOINTS ====================

@api_router.get("/auth/tradestation/status")
async def get_tradestation_auth_status():
    """Get comprehensive TradeStation authentication status"""
    try:
        status = ts_auth.get_status()
        
        # Test connection if authenticated
        connection_test = None
        if status["authenticated"]:
            try:
                async with ts_client:
                    connection_test = await ts_client.test_connection()
            except Exception as e:
                connection_test = {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "authentication": status,
            "connection_test": connection_test,
            "api_configuration": {
                "environment": ts_auth.environment,
                "base_url": ts_auth.api_base,
                "credentials_configured": bool(ts_auth.client_id and ts_auth.client_secret)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking TradeStation auth status: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to check authentication status: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.get("/auth/tradestation/login")
async def initiate_tradestation_login():
    """Initiate TradeStation OAuth login process"""
    try:
        auth_info = ts_auth.generate_auth_url()
        
        return {
            "status": "success",
            "message": "OAuth URL generated. Complete authentication by visiting the auth_url.",
            **auth_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating TradeStation auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@api_router.get("/auth/tradestation/callback")
async def handle_tradestation_callback(code: str = Query(...), state: str = Query(...)):
    """Handle TradeStation OAuth callback"""
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Exchange code for tokens
        token_data = await ts_auth.exchange_code_for_tokens(code)
        
        # Start token monitoring after successful authentication
        if token_manager and not token_manager.running:
            await token_manager.start_monitoring()
            logger.info("🔄 Started token monitoring after successful authentication")
        
        # Test the connection
        async with ts_client:
            connection_test = await ts_client.test_connection()
        
        # Return HTML page that closes the popup and notifies parent
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TradeStation Authentication</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                }}
                .success {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    margin: 0 0 10px 0;
                }}
                p {{
                    margin: 0;
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅</div>
                <h1>Authentication Successful!</h1>
                <p>TradeStation connection established.</p>
                <p>This window will close automatically...</p>
            </div>
            
            <script>
                // Notify parent window of successful authentication
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'TRADESTATION_AUTH_SUCCESS',
                        data: {token_data}
                    }}, '*');
                }}
                
                // Close window after 2 seconds
                setTimeout(() => {{
                    window.close();
                }}, 2000);
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        
        # Return error HTML page
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TradeStation Authentication Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                    color: white;
                }}
                .container {{
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                }}
                .error {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌</div>
                <h1>Authentication Failed</h1>
                <p>Error: {str(e)}</p>
                <p>Please close this window and try again.</p>
            </div>
            
            <script>
                // Notify parent window of authentication failure
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'TRADESTATION_AUTH_ERROR',
                        error: '{str(e)}'
                    }}, '*');
                }}
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html)

@api_router.get("/auth/tradestation/token-status")
async def get_token_manager_status():
    """Get TradeStation token manager status"""
    try:
        if not token_manager:
            return {
                "status": "error",
                "message": "Token manager not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        status = token_manager.get_status()
        return {
            "status": "success",
            "token_manager": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting token manager status: {str(e)}")
        return {
            "status": "error", 
            "message": f"Error getting token manager status: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

# ==================== PORTFOLIO ENDPOINTS ====================

@api_router.get("/tradestation/accounts")
async def get_tradestation_accounts():
    """Get all TradeStation accounts accessible to the user"""
    try:
        async with ts_client:
            accounts = await ts_client.get_accounts()
        
        return {
            "status": "success",
            "accounts": accounts,
            "count": len(accounts),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching TradeStation accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch accounts: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/summary")
async def get_tradestation_account_summary(account_id: str):
    """Get comprehensive account summary including positions, balances, and performance metrics"""
    try:
        # Get comprehensive portfolio analysis
        analysis = await portfolio_service.get_comprehensive_portfolio_analysis(account_id)
        
        return {
            "status": "success",
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching account summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch account summary: {str(e)}")

@api_router.get("/tradestation/test")
async def test_tradestation():
    """Simple test endpoint to verify connectivity"""
    return {
        "status": "success",
        "message": "TradeStation API is working",
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/tradestation/accounts/{account_id}/positions-simple")
async def get_tradestation_positions_simple(account_id: str):
    """Get basic position information quickly for UI display"""
    try:
        async with ts_client:
            positions = await ts_client.get_positions(account_id)
        
        # Convert to simple dict format for frontend
        positions_data = []
        for pos in positions:
            positions_data.append({
                "symbol": pos.symbol,
                "asset_type": pos.asset_type,
                "quantity": pos.quantity,
                "average_price": pos.average_price,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                "daily_pnl": getattr(pos, 'daily_pnl', 0),
                "description": getattr(pos, 'description', f"{pos.symbol} Position")
            })
        
        # Simple portfolio metrics
        total_market_value = sum(pos['market_value'] for pos in positions_data)
        total_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions_data)
        total_daily_pnl = sum(pos['daily_pnl'] for pos in positions_data)
        
        return {
            "status": "success",
            "data": {
                "portfolio_metrics": {
                    "total_market_value": total_market_value,
                    "total_unrealized_pnl": total_unrealized_pnl,
                    "total_daily_pnl": total_daily_pnl,
                    "total_positions": len(positions_data)
                },
                "positions": positions_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching simple positions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch positions: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/positions")
async def get_tradestation_positions(
    account_id: str,
    asset_type: Optional[str] = Query(None, description="Filter by asset type (EQ, OP, FU)"),
    min_value: Optional[float] = Query(None, description="Minimum position value filter")
):
    """Get detailed position information with filtering options"""
    try:
        async with ts_client:
            positions = await ts_client.get_positions(account_id)
        
        # Apply filters
        filtered_positions = positions
        if asset_type:
            filtered_positions = [pos for pos in filtered_positions if pos.asset_type == asset_type]
        
        if min_value is not None:
            filtered_positions = [pos for pos in filtered_positions if abs(pos.market_value) >= min_value]
        
        # Convert to dict format and sort by market value
        positions_data = []
        for pos in filtered_positions:
            pos_dict = {
                "account_id": pos.account_id,
                "symbol": pos.symbol,
                "asset_type": pos.asset_type,
                "quantity": pos.quantity,
                "average_price": pos.average_price,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                "position_type": "Long" if pos.quantity > 0 else "Short"
            }
            positions_data.append(pos_dict)
        
        # Sort by market value descending
        positions_data.sort(key=lambda x: abs(x["market_value"]), reverse=True)
        
        return {
            "status": "success",
            "account_id": account_id,
            "positions": positions_data,
            "total_positions": len(positions_data),
            "filters_applied": {
                "asset_type": asset_type,
                "min_value": min_value
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching positions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch positions: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/balances")
async def get_tradestation_balances(account_id: str):
    """Get account balance information"""
    try:
        async with ts_client:
            balances = await ts_client.get_account_balances(account_id)
        
        return {
            "status": "success",
            "account_id": account_id,
            "balances": balances,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching account balances: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch balances: {str(e)}")

# ==================== TRADING ENDPOINTS ====================

@api_router.post("/tradestation/accounts/{account_id}/orders/validate")
async def validate_tradestation_order(account_id: str, order: OrderRequest):
    """Validate order without placing it"""
    try:
        validation_result = await trading_service.validate_order(account_id, order)
        
        return {
            "status": "success",
            "account_id": account_id,
            "order": order.dict(),
            "validation": validation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Order validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Order validation failed: {str(e)}")

@api_router.post("/tradestation/accounts/{account_id}/orders")
async def place_tradestation_order(
    account_id: str, 
    order: OrderRequest,
    force: bool = Query(False, description="Force order placement despite warnings")
):
    """Place a new trading order"""
    try:
        result = await trading_service.place_order(account_id, order, force)
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "validation_failed" if result.get("requires_confirmation") else "error",
                "message": result["message"],
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Failed to place order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/orders")
async def get_tradestation_orders(
    account_id: str,
    status: Optional[str] = Query(None, description="Filter by order status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    days_back: int = Query(7, ge=1, le=30, description="Days of order history")
):
    """Get order history with filtering options"""
    try:
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with ts_client:
            orders = await ts_client.get_orders(account_id, since_date)
        
        # Apply filters
        filtered_orders = orders
        if status:
            filtered_orders = [order for order in filtered_orders if order.status == status]
        
        if symbol:
            filtered_orders = [order for order in filtered_orders if order.symbol.upper() == symbol.upper()]
        
        # Sort by timestamp descending
        filtered_orders.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Convert to dict format
        orders_data = []
        for order in filtered_orders:
            order_dict = {
                "order_id": order.order_id,
                "account_id": order.account_id,
                "symbol": order.symbol,
                "asset_type": order.asset_type,
                "quantity": order.quantity,
                "order_type": order.order_type,
                "price": order.price,
                "status": order.status,
                "filled_quantity": order.filled_quantity,
                "remaining_quantity": order.remaining_quantity,
                "timestamp": order.timestamp.isoformat()
            }
            orders_data.append(order_dict)
        
        return {
            "status": "success",
            "account_id": account_id,
            "orders": orders_data,
            "total_orders": len(orders_data),
            "filters": {
                "status": status,
                "symbol": symbol,
                "days_back": days_back
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")

@api_router.delete("/tradestation/accounts/{account_id}/orders/{order_id}")
async def cancel_tradestation_order(account_id: str, order_id: str):
    """Cancel an existing order"""
    try:
        result = await trading_service.cancel_order(account_id, order_id)
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": result["message"],
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Failed to cancel order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/orders/{order_id}/status")
async def get_tradestation_order_status(account_id: str, order_id: str):
    """Get detailed status of a specific order"""
    try:
        result = await trading_service.get_order_status(account_id, order_id)
        
        if result["success"]:
            return {
                "status": "success",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": result["message"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Failed to get order status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get order status: {str(e)}")

@api_router.get("/tradestation/accounts/{account_id}/trading-summary")
async def get_tradestation_trading_summary(
    account_id: str,
    days_back: int = Query(7, ge=1, le=30, description="Days of trading history to analyze")
):
    """Get comprehensive trading activity summary"""
    try:
        summary = await trading_service.get_trading_summary(account_id, days_back)
        
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get trading summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trading summary: {str(e)}")

# ==================== MARKET DATA ENDPOINTS ====================

@api_router.get("/tradestation/quotes/{symbols}")
async def get_tradestation_quotes(symbols: str):
    """Get current quotes for symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        async with ts_client:
            quotes = await ts_client.get_quote(symbol_list)
        
        # Convert to dict format
        quotes_data = []
        for quote in quotes:
            quote_dict = {
                "symbol": quote.symbol,
                "bid": quote.bid,
                "ask": quote.ask,
                "last": quote.last,
                "volume": quote.volume,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "timestamp": quote.timestamp.isoformat()
            }
            quotes_data.append(quote_dict)
        
        return {
            "status": "success",
            "quotes": quotes_data,
            "symbols_requested": symbol_list,
            "quotes_found": len(quotes_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get quotes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quotes: {str(e)}")

@api_router.get("/tradestation/historical/{symbol}")
async def get_tradestation_historical_data(
    symbol: str,
    interval: int = Query(1, description="Bar interval"),
    unit: str = Query("Daily", description="Time unit (Daily, Weekly, Monthly)"),
    bars_back: int = Query(30, description="Number of bars to retrieve")
):
    """Get historical bar data for a symbol"""
    try:
        async with ts_client:
            bars = await ts_client.get_historical_bars(
                symbol=symbol.upper(),
                interval=interval,
                unit=unit,
                bars_back=bars_back
            )
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "bars": bars,
            "parameters": {
                "interval": interval,
                "unit": unit,
                "bars_back": bars_back
            },
            "bars_count": len(bars),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")

# ==================== RISK MANAGEMENT ENDPOINTS ====================

@api_router.get("/tradestation/risk-limits")
async def get_risk_limits():
    """Get current risk management limits"""
    try:
        current_limits = trading_service.risk_manager.limits
        
        return {
            "status": "success",
            "risk_limits": current_limits.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get risk limits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk limits: {str(e)}")

@api_router.put("/tradestation/risk-limits")
async def update_risk_limits(new_limits: RiskLimits):
    """Update risk management limits"""
    try:
        trading_service.update_risk_limits(new_limits)
        
        return {
            "status": "success",
            "message": "Risk limits updated successfully",
            "new_limits": new_limits.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update risk limits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update risk limits: {str(e)}")

# ==================== OPTIONS MODULE ENDPOINTS ====================

class OptionsStrategyRequest(BaseModel):
    symbol: str
    strategy_name: str
    stock_price: float
    strike: float
    days_to_expiry: int = 30
    volatility: Optional[float] = 0.25
    risk_free_rate: Optional[float] = 0.05

class OptionsCalculationResponse(BaseModel):
    strategy_config: Dict[str, Any]
    analysis: Dict[str, Any]
    chart_data: Dict[str, Any]

@api_router.post("/options/calculate", response_model=OptionsCalculationResponse)
async def calculate_options_strategy(request: OptionsStrategyRequest):
    """Calculate options strategy with P&L analysis și Greeks"""
    try:
        # Create strategy using the new create_strategy_by_name method
        parameters = {
            'strike': request.strike,
            'long_strike': getattr(request, 'long_strike', request.strike - 5),
            'short_strike': getattr(request, 'short_strike', request.strike + 5),
            'call_strike': getattr(request, 'call_strike', request.strike + 5),
            'put_short_strike': getattr(request, 'put_short_strike', request.strike - 10),
            'put_long_strike': getattr(request, 'put_long_strike', request.strike - 20),
            'call_short_strike': getattr(request, 'call_short_strike', request.strike + 10),
            'call_long_strike': getattr(request, 'call_long_strike', request.strike + 20)
        }
        
        strategy = options_engine.create_strategy_by_name(
            strategy_name=request.strategy_name,
            symbol=request.symbol.upper(),
            stock_price=request.stock_price,
            parameters=parameters,
            days_to_expiry=request.days_to_expiry,
            volatility=request.volatility,
            risk_free_rate=request.risk_free_rate
        )
        
        # Analyze strategy
        analysis = options_engine.analyze_strategy(strategy)
        
        # Convert strategy config pentru JSON response
        strategy_data = {
            "name": strategy.name,
            "description": strategy.description,
            "stock_price": strategy.stock_price,
            "days_to_expiry": strategy.days_to_expiry,
            "volatility": strategy.volatility,
            "risk_free_rate": strategy.risk_free_rate,
            "legs": [
                {
                    "option_type": leg.option_type.value,
                    "action": leg.action.value,
                    "strike": leg.strike,
                    "quantity": leg.quantity,
                    "premium": round(leg.premium, 2)
                }
                for leg in strategy.legs
            ]
        }
        
        # Convert analysis pentru JSON response
        analysis_data = {
            "max_profit": round(analysis.max_profit, 2),
            "max_loss": round(analysis.max_loss, 2),
            "breakeven_points": analysis.breakeven_points,
            "probability_of_profit": round(analysis.probability_of_profit * 100, 1),  # Percentage
            "greeks": {
                "delta": round(analysis.strategy_greeks.delta, 3),
                "gamma": round(analysis.strategy_greeks.gamma, 3),
                "theta": round(analysis.strategy_greeks.theta, 2),
                "vega": round(analysis.strategy_greeks.vega, 2),
                "rho": round(analysis.strategy_greeks.rho, 2)
            }
        }
        
        # Chart data pentru Plotly.js
        chart_data = {
            "x": analysis.price_array,
            "y": analysis.pnl_array,
            "type": "scatter",
            "mode": "lines",
            "name": f"{strategy.name} P&L",
            "line": {"color": "blue", "width": 3}
        }
        
        return OptionsCalculationResponse(
            strategy_config=strategy_data,
            analysis=analysis_data,
            chart_data=chart_data
        )
        
    except Exception as e:
        logger.error(f"Failed to calculate options strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate options strategy: {str(e)}")

@api_router.get("/options/strategies")
async def get_available_options_strategies():
    """Get all available options strategies organized by proficiency level"""
    try:
        strategies = options_engine.get_available_strategies()
        
        return {
            "status": "success",
            "strategies": strategies,
            "total_strategies": sum(
                len(strategies_list) for category in strategies.values()
                for strategies_list in category.values()
            ),
            "implemented": [
                "Long Call", "Long Put", "Bull Call Spread", "Bear Put Spread",
                "Iron Condor", "Long Straddle", "Covered Call"
            ],
            "coming_soon": [
                "Bull Put Spread", "Bear Call Spread", "Iron Butterfly", 
                "Long Strangle", "Cash-Secured Put", "Protective Put"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")

@api_router.post("/options/optimize")
async def optimize_options_strategies(
    request: dict
):
    """Optimize and rank options strategies based on parameters"""
    try:
        # Extract parameters from request body
        symbol = request.get('symbol', 'SPY')
        stock_price = request.get('stock_price', 100.0)
        target_price = request.get('target_price', 105.0)
        sentiment = request.get('sentiment', 'Neutral')
        budget = request.get('budget', 10000)
        days_to_expiry = request.get('days_to_expiry', 30)
        volatility = request.get('volatility', 0.25)
        risk_free_rate = request.get('risk_free_rate', 0.05)
        
        # List of strategies to evaluate
        strategy_names = [
            "Long Call", "Long Put", "Bull Call Spread", "Bear Put Spread",
            "Iron Condor", "Long Straddle", "Covered Call"
        ]
        
        optimized_strategies = []
        
        for strategy_name in strategy_names:
            try:
                # Create default parameters based on sentiment and target
                parameters = {}
                
                if strategy_name in ["Long Call", "Covered Call"]:
                    # Bullish strategies - strike near current price
                    parameters['strike'] = stock_price - 5 if sentiment in ['Bullish', 'Very Bullish'] else stock_price + 5
                    parameters['call_strike'] = stock_price + 10
                elif strategy_name == "Long Put":
                    # Bearish strategy
                    parameters['strike'] = stock_price + 5 if sentiment in ['Bearish', 'Very Bearish'] else stock_price - 5  
                elif strategy_name == "Bull Call Spread":
                    parameters['long_strike'] = stock_price - 5
                    parameters['short_strike'] = min(target_price, stock_price + 15)
                elif strategy_name == "Bear Put Spread":
                    parameters['long_strike'] = stock_price + 5
                    parameters['short_strike'] = max(target_price, stock_price - 15)
                elif strategy_name == "Iron Condor":
                    parameters['put_short_strike'] = stock_price - 10
                    parameters['put_long_strike'] = stock_price - 20
                    parameters['call_short_strike'] = stock_price + 10
                    parameters['call_long_strike'] = stock_price + 20
                elif strategy_name == "Long Straddle":
                    parameters['strike'] = stock_price
                
                # Create and analyze strategy
                strategy = options_engine.create_strategy_by_name(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    stock_price=stock_price,
                    parameters=parameters,
                    days_to_expiry=days_to_expiry,
                    volatility=volatility,
                    risk_free_rate=risk_free_rate
                )
                
                analysis = options_engine.analyze_strategy(strategy)
                
                # Calculate key metrics
                total_premium = sum(leg.premium * leg.quantity * (1 if leg.action.value == 'buy' else -1) 
                                  for leg in strategy.legs) * 100  # Convert to dollars
                
                if abs(total_premium) > budget:
                    continue  # Skip strategies over budget
                
                return_on_risk = (analysis.max_profit / abs(analysis.max_loss)) * 100 if analysis.max_loss != 0 else 0
                
                # Create strategy result
                strategy_result = {
                    "name": strategy_name,
                    "strikes": f"{strategy.legs[0].strike}" if len(strategy.legs) == 1 else 
                             f"{strategy.legs[0].strike}/{strategy.legs[1].strike}" if len(strategy.legs) == 2 else
                             f"{strategy.legs[0].strike}/{strategy.legs[1].strike}/{strategy.legs[2].strike}/{strategy.legs[3].strike}",
                    "category": get_strategy_category(strategy_name),
                    "max_profit": analysis.max_profit,
                    "max_loss": analysis.max_loss,
                    "return_on_risk": return_on_risk,
                    "breakeven": analysis.breakeven_points[0] if analysis.breakeven_points else stock_price,
                    "prob_profit": analysis.probability_of_profit * 100,
                    "total_cost": abs(total_premium),
                    "chart_data": {
                        "x": analysis.price_array,
                        "y": analysis.pnl_array
                    }
                }
                
                optimized_strategies.append(strategy_result)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {strategy_name}: {str(e)}")
                continue
        
        # Sort strategies by return on risk (descending)
        optimized_strategies.sort(key=lambda x: x['return_on_risk'], reverse=True)
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "sentiment": sentiment,
            "target_price": target_price,
            "strategies": optimized_strategies[:10],  # Top 10 strategies
            "parameters": {
                "stock_price": stock_price,
                "days_to_expiry": days_to_expiry,
                "volatility": volatility,
                "budget": budget
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize strategies: {str(e)}")

def get_strategy_category(strategy_name: str) -> str:
    """Get strategy proficiency category"""
    categories = {
        "Long Call": "Novice",
        "Long Put": "Novice", 
        "Covered Call": "Novice",
        "Bull Call Spread": "Intermediate",
        "Bear Put Spread": "Intermediate",
        "Iron Condor": "Intermediate",
        "Long Straddle": "Intermediate"
    }
    return categories.get(strategy_name, "Advanced")

@api_router.get("/options/quote/{symbol}")
async def get_options_chain_data(symbol: str):
    """Get options chain data from TradeStation API (placeholder pentru development)"""
    try:
        # For now, return mock data until TradeStation options API is fully integrated
        # In production, this would call TradeStation options chain API
        
        mock_options_data = {
            "symbol": symbol.upper(),
            "stock_price": 150.00,  # Mock current price
            "options_chain": {
                "calls": [
                    {"strike": 145, "bid": 7.20, "ask": 7.40, "last": 7.30, "volume": 1250, "open_interest": 5600},
                    {"strike": 150, "bid": 4.80, "ask": 5.00, "last": 4.90, "volume": 2100, "open_interest": 8900},
                    {"strike": 155, "bid": 2.90, "ask": 3.10, "last": 3.00, "volume": 1800, "open_interest": 4200}
                ],
                "puts": [
                    {"strike": 145, "bid": 2.10, "ask": 2.30, "last": 2.20, "volume": 900, "open_interest": 3400},
                    {"strike": 150, "bid": 4.20, "ask": 4.40, "last": 4.30, "volume": 1600, "open_interest": 6700},
                    {"strike": 155, "bid": 7.50, "ask": 7.70, "last": 7.60, "volume": 800, "open_interest": 2100}
                ]
            },
            "expiration_date": "2024-12-20",
            "days_to_expirt": 30,
            "implied_volatility": 0.25
        }
        
        return {
            "status": "success",
            "data": mock_options_data,
            "note": "Mock data - TradeStation options API integration în development",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get options data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get options data: {str(e)}")

# Add new imports to the root response

@api_router.get("/unusual-whales/congressional/trades")
async def get_unusual_whales_congressional_trades(
    days_back: Optional[int] = Query(30, description="Days to look back for trades"),
    minimum_amount: Optional[int] = Query(15000, description="Minimum transaction amount"),
    party_filter: Optional[str] = Query(None, description="Filter by party: Democrat or Republican"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type: Purchase or Sale"),
    limit: Optional[int] = Query(100, description="Maximum number of trades to return"),
    include_analysis: Optional[bool] = Query(True, description="Include pattern analysis")
):
    """Get congressional trading data from Unusual Whales"""
    try:
        # Get congressional trades
        trades = await uw_service.get_congressional_trades(
            days_back=days_back,
            minimum_amount=minimum_amount,
            limit=limit
        )
        
        # Apply additional filters
        if party_filter:
            trades = [t for t in trades if t.get('party', '').lower() == party_filter.lower()]
        
        if transaction_type:
            trades = [t for t in trades if t.get('transaction_type', '').lower() == transaction_type.lower()]
        
        # Sort by amount and recency
        sorted_trades = sorted(
            trades,
            key=lambda x: (x.get('transaction_amount', 0), x.get('transaction_date', '')),
            reverse=True
        )
        
        response_data = {
            "status": "success",
            "data": {
                "trades": sorted_trades,
                "summary": {
                    "total_trades": len(sorted_trades),
                    "total_amount": sum(t.get('transaction_amount', 0) for t in sorted_trades),
                    "unique_representatives": len(set(t.get('representative') for t in sorted_trades)),
                    "unique_tickers": len(set(t.get('ticker') for t in sorted_trades)),
                    "recent_trades": len([t for t in sorted_trades 
                                       if (datetime.now() - datetime.strptime(t.get('transaction_date', '1970-01-01'), '%Y-%m-%d')).days <= 7]),
                    "party_breakdown": {},
                    "transaction_type_breakdown": {}
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Calculate party breakdown
        from collections import Counter
        parties = [t.get('party') for t in sorted_trades if t.get('party')]
        response_data["data"]["summary"]["party_breakdown"] = dict(Counter(parties))
        
        # Calculate transaction type breakdown
        transaction_types = [t.get('transaction_type') for t in sorted_trades if t.get('transaction_type')]
        response_data["data"]["summary"]["transaction_type_breakdown"] = dict(Counter(transaction_types))
        
        # Add analysis if requested
        if include_analysis and sorted_trades:
            analysis = await uw_service.analyze_congressional_patterns(sorted_trades)
            response_data["analysis"] = analysis
            
        return response_data
        
    except Exception as e:
        logger.error(f"Error in congressional trades endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching congressional trades: {str(e)}")

@api_router.get("/unusual-whales/analysis/comprehensive")
async def get_unusual_whales_comprehensive_analysis():
    """Get comprehensive analysis from all Unusual Whales data sources"""
    try:
        # Fetch data from all sources concurrently
        options_task = uw_service.get_options_flow_alerts(limit=50)
        dark_pool_task = uw_service.get_recent_dark_pool_activity(limit=50)
        congressional_task = uw_service.get_congressional_trades(days_back=30, limit=50)
        
        options_data, dark_pool_data, congressional_data = await asyncio.gather(
            options_task, dark_pool_task, congressional_task, return_exceptions=True
        )
        
        # Handle potential errors
        if isinstance(options_data, Exception):
            options_data = []
        if isinstance(dark_pool_data, Exception):
            dark_pool_data = []
        if isinstance(congressional_data, Exception):
            congressional_data = []
        
        # Perform analyses
        comprehensive_analysis = {
            "options_flow": {
                "data_available": len(options_data) > 0,
                "analysis": await uw_service.analyze_options_flow_patterns(options_data) if options_data else {"analysis": "No data available"}
            },
            "dark_pool": {
                "data_available": len(dark_pool_data) > 0,
                "analysis": await uw_service.analyze_dark_pool_patterns(dark_pool_data) if dark_pool_data else {"analysis": "No data available"}
            },
            "congressional": {
                "data_available": len(congressional_data) > 0,
                "analysis": await uw_service.analyze_congressional_patterns(congressional_data) if congressional_data else {"analysis": "No data available"}
            }
        }
        
        # Generate market outlook based on all data
        market_outlook = _generate_market_outlook(options_data, dark_pool_data, congressional_data)
        
        return {
            "status": "success",
            "comprehensive_analysis": comprehensive_analysis,
            "market_outlook": market_outlook,
            "data_summary": {
                "options_alerts": len(options_data),
                "dark_pool_trades": len(dark_pool_data),
                "congressional_trades": len(congressional_data)
            },
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error performing comprehensive analysis: {str(e)}")

def _generate_market_outlook(options_data: List[Dict], dark_pool_data: List[Dict], congressional_data: List[Dict]) -> Dict[str, Any]:
    """Generate overall market outlook from all data sources"""
    try:
        outlook = {
            "overall_sentiment": "neutral",
            "confidence": "low",
            "key_signals": [],
            "recommended_actions": [],
            "risk_factors": []
        }
        
        signals_count = {"bullish": 0, "bearish": 0, "neutral": 0}
        
        # Analyze options flow sentiment
        if options_data:
            bullish_options = len([o for o in options_data if o.get('sentiment') == 'bullish'])
            bearish_options = len([o for o in options_data if o.get('sentiment') == 'bearish'])
            
            if bullish_options > bearish_options * 1.5:
                signals_count["bullish"] += 1
                outlook["key_signals"].append("Options flow shows bullish bias")
            elif bearish_options > bullish_options * 1.5:
                signals_count["bearish"] += 1
                outlook["key_signals"].append("Options flow shows bearish bias")
            else:
                signals_count["neutral"] += 1
        
        # Analyze dark pool activity
        if dark_pool_data:
            institutional_signals = len([d for d in dark_pool_data if d.get('institutional_signal', False)])
            if institutional_signals > len(dark_pool_data) * 0.6:
                signals_count["bullish"] += 1
                outlook["key_signals"].append("High institutional activity in dark pools")
                outlook["recommended_actions"].append("Monitor for potential breakouts")
        
        # Analyze congressional trading
        if congressional_data:
            recent_purchases = len([c for c in congressional_data 
                                 if c.get('transaction_type') == 'Purchase' 
                                 and (datetime.now() - datetime.strptime(c.get('transaction_date', '1970-01-01'), '%Y-%m-%d')).days <= 14])
            
            if recent_purchases > len(congressional_data) * 0.4:
                signals_count["bullish"] += 1
                outlook["key_signals"].append("Recent congressional purchasing activity")
        
        # Determine overall sentiment
        max_signals = max(signals_count.values())
        if signals_count["bullish"] == max_signals and max_signals > 0:
            outlook["overall_sentiment"] = "bullish"
            outlook["confidence"] = "high" if max_signals >= 2 else "medium"
        elif signals_count["bearish"] == max_signals and max_signals > 0:
            outlook["overall_sentiment"] = "bearish"
            outlook["confidence"] = "high" if max_signals >= 2 else "medium"
        else:
            outlook["overall_sentiment"] = "neutral"
            outlook["confidence"] = "low"
        
        # Add general recommendations
        if not outlook["recommended_actions"]:
            outlook["recommended_actions"] = [
                "Continue monitoring unusual activity",
                "Stay alert for confirmation signals",
                "Maintain risk management protocols"
            ]
        
        # Add risk factors
        outlook["risk_factors"] = [
            "Market volatility during earnings season",
            "Federal Reserve policy uncertainty",
            "Geopolitical tensions affecting markets"
        ]
        
        return outlook
        
    except Exception as e:
        logger.error(f"Error generating market outlook: {str(e)}")
        return {
            "overall_sentiment": "neutral",
            "confidence": "low",
            "key_signals": [],
            "recommended_actions": ["Monitor markets closely"],
            "risk_factors": ["Analysis unavailable due to technical issues"],
            "error": str(e)
        }

@api_router.get("/unusual-whales/trading-strategies")
async def get_trading_strategies_from_unusual_whales():
    """Generate trading strategies based on Unusual Whales data - designed for TradeStation execution"""
    try:
        # Get fresh data from all sources
        options_data = await uw_service.get_options_flow_alerts(limit=25)
        dark_pool_data = await uw_service.get_recent_dark_pool_activity(limit=25)
        congressional_data = await uw_service.get_congressional_trades(days_back=14, limit=25)
        
        strategies = []
        
        # Strategy 1: Large Premium Flow Following
        large_premium_alerts = [o for o in options_data if o.get('trade_size') in ['whale', 'large']]
        if large_premium_alerts:
            top_ticker = max(large_premium_alerts, key=lambda x: x.get('premium', 0))
            sentiment = top_ticker.get('sentiment', 'neutral')
            dte = int(top_ticker.get('dte', 0)) if top_ticker.get('dte') else 0
            underlying_price = float(top_ticker.get('underlying_price', 0)) if top_ticker.get('underlying_price') else 0
            
            # Generate specific options strategy based on sentiment and DTE
            if sentiment == 'bullish' and dte > 14:
                strategy_name = "Bull Call Spread"
                strategy_type = "vertical_spread"
                lower_strike = int(underlying_price * 0.98) if underlying_price else 100
                upper_strike = int(underlying_price * 1.05) if underlying_price else 105
            elif sentiment == 'bearish' and dte > 14:
                strategy_name = "Bear Put Spread"
                strategy_type = "vertical_spread"
                lower_strike = int(underlying_price * 0.95) if underlying_price else 95
                upper_strike = int(underlying_price * 1.02) if underlying_price else 102
            elif sentiment == 'bullish' and dte <= 14:
                strategy_name = "Long Call"
                strategy_type = "directional"
                lower_strike = int(underlying_price * 1.02) if underlying_price else 102
                upper_strike = None
            else:
                strategy_name = "Long Put"
                strategy_type = "directional"
                lower_strike = int(underlying_price * 0.98) if underlying_price else 98
                upper_strike = None
                
            strategies.append({
                "strategy_name": strategy_name,
                "ticker": top_ticker['symbol'],
                "strategy_type": strategy_type,
                "confidence": 0.8,
                "timeframe": f"{int(dte)} days to expiration",
                "entry_logic": {
                    "condition": f"Large premium flow detected in {top_ticker['symbol']} ({sentiment})",
                    "premium_threshold": top_ticker.get('premium', 0),
                    "sentiment": sentiment,
                    "underlying_price": underlying_price,
                    "volume": top_ticker.get('volume', 0),
                    "dte": dte
                },
                "tradestation_execution": {
                    "strategy_type": strategy_name.lower().replace(" ", "_"),
                    "underlying": top_ticker['symbol'],
                    "legs": [
                        {
                            "action": "buy" if strategy_name in ["Long Call", "Long Put"] else "buy",
                            "strike": lower_strike or 100,
                            "option_type": "call" if "Call" in strategy_name else "put",
                            "quantity": 1
                        }
                    ] + ([{
                        "action": "sell",
                        "strike": upper_strike or 105,
                        "option_type": "call" if "Call" in strategy_name else "put", 
                        "quantity": 1
                    }] if upper_strike else []),
                    "expiration": top_ticker.get('expiration', ''),
                    "max_risk": f"${abs((upper_strike or 0) - (lower_strike or 0)) * 100}" if upper_strike else "Premium paid",
                    "max_profit": "Premium paid" if not upper_strike else f"${((upper_strike or 0) - (lower_strike or 0)) * 100 - 200}",
                    "breakeven": f"${(lower_strike or 0) + 2}" if not upper_strike else f"${(lower_strike or 0) + 2}"
                },
                "risk_management": {
                    "max_position_size": "2% of portfolio",
                    "stop_loss_percentage": 50 if not upper_strike else 25,
                    "profit_target_percentage": 100 if not upper_strike else 50,
                    "max_loss": f"${200}" if upper_strike else "Premium paid"
                }
            })
        
        # Strategy 2: High IV Options Strategies
        high_vol_alerts = [o for o in options_data if o.get('volume_oi_ratio', 0) > 3.0]
        if high_vol_alerts and len(strategies) < 4:
            ticker_counts = {}
            for alert in high_vol_alerts:
                ticker = alert['symbol']
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
            
            if ticker_counts:
                top_ticker_name = max(ticker_counts, key=ticker_counts.get)
                ticker_alerts = [a for a in high_vol_alerts if a['symbol'] == top_ticker_name]
                
                # Check if we have both calls and puts (potential straddle/strangle)
                has_calls = any(a.get('sentiment') == 'bullish' for a in ticker_alerts)
                has_puts = any(a.get('sentiment') == 'bearish' for a in ticker_alerts)
                
                # Calculate safe average price handling string/numeric values
                def safe_float(value, default=0):
                    try:
                        return float(value) if value else default
                    except (ValueError, TypeError):
                        return default
                
                avg_dte = sum(safe_float(a.get('dte', 0)) for a in ticker_alerts) / len(ticker_alerts)
                avg_price = sum(safe_float(a.get('underlying_price', 0)) for a in ticker_alerts) / len(ticker_alerts)
                
                if has_calls and has_puts and avg_dte > 7:
                    # High volatility expected - Straddle or Strangle
                    strategy_name = "Long Straddle" if len(ticker_alerts) >= 4 else "Long Strangle"
                    atm_strike = int(avg_price) if avg_price else 100
                    
                    strategies.append({
                        "strategy_name": strategy_name,
                        "ticker": top_ticker_name,
                        "strategy_type": "volatility",
                        "confidence": 0.7,
                        "timeframe": f"{int(avg_dte)} days to expiration",
                        "entry_logic": {
                            "condition": f"High volume/OI ratio in {top_ticker_name} suggesting volatility spike",
                            "volume_oi_ratio": max(a.get('volume_oi_ratio', 0) for a in ticker_alerts),
                            "both_calls_puts": True,
                            "underlying_price": avg_price
                        },
                        "tradestation_execution": {
                            "strategy_type": strategy_name.lower().replace(" ", "_"),
                            "underlying": top_ticker_name,
                            "legs": [
                                {
                                    "action": "buy",
                                    "strike": int(atm_strike),
                                    "option_type": "call",
                                    "quantity": 1
                                },
                                {
                                    "action": "buy", 
                                    "strike": int(atm_strike) + (5 if strategy_name == "Long Strangle" else 0),
                                    "option_type": "put",
                                    "quantity": 1
                                }
                            ],
                            "expiration": ticker_alerts[0].get('expiration', ''),
                            "max_risk": "Total premium paid",
                            "max_profit": "Unlimited",
                            "breakeven_upper": f"${atm_strike + 10}",
                            "breakeven_lower": f"${atm_strike - 10}"
                        },
                        "risk_management": {
                            "max_position_size": "1.5% of portfolio",
                            "stop_loss_percentage": 50,
                            "profit_target": "200% or significant move in underlying",
                            "time_decay_risk": "High - monitor theta"
                        }
                    })
                elif avg_dte > 30:  # Longer term, consider Iron Condor for income
                    strategy_name = "Iron Condor"
                    center_strike = int(avg_price) if avg_price else 100
                    
                    strategies.append({
                        "strategy_name": strategy_name,
                        "ticker": top_ticker_name,
                        "strategy_type": "income",
                        "confidence": 0.6,
                        "timeframe": f"{int(avg_dte)} days to expiration",
                        "entry_logic": {
                            "condition": f"Range-bound movement expected in {top_ticker_name}",
                            "underlying_price": avg_price,
                            "dte": avg_dte,
                            "market_assumption": "Low volatility/sideways movement"
                        },
                        "tradestation_execution": {
                            "strategy_type": "iron_condor",
                            "underlying": top_ticker_name,
                            "legs": [
                                {"action": "sell", "strike": center_strike - 5, "option_type": "put", "quantity": 1},
                                {"action": "buy", "strike": center_strike - 15, "option_type": "put", "quantity": 1},
                                {"action": "sell", "strike": center_strike + 5, "option_type": "call", "quantity": 1},
                                {"action": "buy", "strike": center_strike + 15, "option_type": "call", "quantity": 1}
                            ],
                            "expiration": ticker_alerts[0].get('expiration', ''),
                            "max_risk": "$1000",
                            "max_profit": "Net credit received",
                            "profit_range": f"${center_strike - 5} to ${center_strike + 5}"
                        },
                        "risk_management": {
                            "max_position_size": "3% of portfolio", 
                            "stop_loss": "50% of max risk",
                            "profit_target": "25-50% of max profit",
                            "management": "Close early if 21 DTE and profitable"
                        }
                    })
        
        # Strategy 3: Congressional Insider Following with Options Overlay
        recent_purchases = [c for c in congressional_data 
                          if c.get('transaction_type') == 'Purchase' 
                          and (datetime.now() - datetime.strptime(c.get('transaction_date', '1970-01-01'), '%Y-%m-%d')).days <= 21]
        
        if recent_purchases and len(strategies) < 4:
            from collections import Counter
            ticker_purchases = Counter([c['ticker'] for c in recent_purchases])
            if ticker_purchases:
                top_congress_ticker = ticker_purchases.most_common(1)[0][0]
                purchase_count = ticker_purchases[top_congress_ticker]
                
                # Find if there's options flow on the same ticker
                matching_options = [o for o in options_data if o.get('symbol') == top_congress_ticker]
                
                if matching_options:
                    # Combine congressional and options signals
                    avg_sentiment = Counter([o.get('sentiment') for o in matching_options]).most_common(1)[0][0]
                    strategy_name = "Synthetic Long" if avg_sentiment == 'bullish' else "Protective Put"
                else:
                    # Pure congressional play
                    strategy_name = "LEAPS Call" 
                    avg_sentiment = 'bullish'
                
                strategies.append({
                    "strategy_name": strategy_name,
                    "ticker": top_congress_ticker,
                    "strategy_type": "policy_play",
                    "confidence": 0.75 if matching_options else 0.6,
                    "timeframe": "3-6 months",
                    "entry_logic": {
                        "condition": f"Congressional insider activity in {top_congress_ticker} + options confirmation",
                        "congress_purchases": purchase_count,
                        "options_confirmation": len(matching_options) > 0,
                        "sector": [c.get('sector') for c in recent_purchases if c['ticker'] == top_congress_ticker][0],
                        "policy_catalyst_expected": True
                    },
                    "tradestation_execution": {
                        "strategy_type": strategy_name.lower().replace(" ", "_"),
                        "underlying": top_congress_ticker,
                        "legs": [
                            {
                                "action": "buy",
                                "strike": "ITM or ATM",
                                "option_type": "call",
                                "quantity": 1,
                                "expiration": "6+ months out (LEAPS)"
                            }
                        ] + ([{
                            "action": "buy",
                            "strike": "OTM",
                            "option_type": "put", 
                            "quantity": 1,
                            "expiration": "3 months out"
                        }] if strategy_name == "Protective Put" else []),
                        "max_risk": "Premium paid",
                        "max_profit": "Unlimited upside potential",
                        "catalyst_dependent": True
                    },
                    "risk_management": {
                        "max_position_size": "2% of portfolio",
                        "stop_loss_percentage": 30,
                        "time_stop": "Before earnings if no catalyst",
                        "catalyst_monitoring": "Policy announcements, committee hearings"
                    }
                })
        
        # Strategy 4: Mean Reversion Play
        if dark_pool_data and len(strategies) < 4:
            high_dark_pool = [d for d in dark_pool_data if d.get('dark_percentage', 0) > 60]
            if high_dark_pool:
                top_dark_ticker = max(high_dark_pool, key=lambda x: x.get('dark_volume', 0))
                ticker_symbol = top_dark_ticker['ticker']
                
                # Look for oversold/overbought conditions
                strategy_name = "Cash-Secured Put" if top_dark_ticker.get('institutional_signal') else "Covered Call"
                
                strategies.append({
                    "strategy_name": strategy_name,
                    "ticker": ticker_symbol,
                    "strategy_type": "income_generation",
                    "confidence": 0.65,
                    "timeframe": "30-45 days",
                    "entry_logic": {
                        "condition": f"High dark pool activity suggests institutional accumulation in {ticker_symbol}",
                        "dark_percentage": top_dark_ticker.get('dark_percentage', 0),
                        "institutional_signal": top_dark_ticker.get('institutional_signal', False),
                        "mean_reversion_expected": True
                    },
                    "tradestation_execution": {
                        "strategy_type": strategy_name.lower().replace("-", "_").replace(" ", "_"),
                        "underlying": ticker_symbol,
                        "legs": [
                            {
                                "action": "sell",
                                "strike": "OTM",
                                "option_type": "put" if "Put" in strategy_name else "call",
                                "quantity": 1,
                                "expiration": "30-45 DTE"
                            }
                        ],
                        "collateral_required": "$10,000 cash" if "Put" in strategy_name else "100 shares",
                        "max_risk": "Strike price - premium" if "Put" in strategy_name else "Unlimited upside",
                        "max_profit": "Premium collected",
                        "assignment_plan": "Ready to own stock" if "Put" in strategy_name else "Ready to sell shares"
                    },
                    "risk_management": {
                        "max_position_size": "5% of portfolio",
                        "profit_target": "50% of premium in 21 days",
                        "roll_strategy": "Roll out and down/up if challenged",
                        "assignment_ready": True
                    }
                })
        
        # Generate charts for all strategies
        for strategy in strategies:
            try:
                chart_data = chart_generator.generate_strategy_chart(strategy)
                strategy['chart'] = chart_data
            except Exception as e:
                logger.error(f"Error generating chart for {strategy.get('strategy_name', 'unknown')}: {str(e)}")
                strategy['chart'] = {
                    'chart_type': 'error',
                    'error': f"Chart generation failed: {str(e)}"
                }
        
        return {
            "status": "success",
            "trading_strategies": strategies,
            "total_strategies": len(strategies),
            "data_analysis": {
                "options_alerts_analyzed": len(options_data),
                "dark_pool_trades_analyzed": len(dark_pool_data),
                "congressional_trades_analyzed": len(congressional_data)
            },
            "tradestation_ready": True,
            "charts_included": True,
            "disclaimer": "These strategies are generated from unusual market activity patterns. Always perform your own due diligence and risk assessment before executing trades.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating trading strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating trading strategies: {str(e)}")

# ==================== AI INVESTMENT SCORING AGENT ====================

@api_router.post("/agents/investment-scoring")
async def generate_investment_score(
    symbol: str = Query(..., description="Stock symbol to analyze"),
    include_personalization: Optional[bool] = Query(False, description="Include user personalization if available")
):
    """
    AI-Powered Investment Scoring Agent
    
    Generates comprehensive investment score using Unusual Whales data sources:
    - Options flow sentiment analysis
    - Dark pool institutional activity
    - Congressional trading insights  
    - AI-generated trading strategies
    - Market momentum indicators
    - Risk-adjusted scoring
    
    Returns score (0-100), recommendation, confidence level, and key signals.
    """
    try:
        logger.info(f"Investment Scoring Agent: Analyzing {symbol.upper()}")
        
        # Generate comprehensive investment score
        analysis = await investment_scoring_agent.generate_investment_score(
            symbol=symbol.upper(),
            user_context={'include_personalization': include_personalization}
        )
        
        # Add response metadata
        analysis.update({
            'agent_type': 'investment_scoring',
            'data_sources_count': len(analysis.get('data_sources', [])),
            'processing_time_ms': 'N/A',  # Could add timing if needed
            'api_version': '1.0'
        })
        
        logger.info(f"Investment Scoring Agent: Generated score {analysis.get('investment_score')} "
                   f"for {symbol.upper()} with {analysis.get('confidence_level')} confidence")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Investment Scoring Agent error for {symbol}: {str(e)}")
        return {
            'symbol': symbol.upper(),
            'error': f"Failed to generate investment score: {str(e)}",
            'investment_score': 50.0,  # Neutral score on error
            'recommendation': 'HOLD',
            'confidence_level': 'low',
            'key_signals': [],
            'risk_analysis': {'overall_risk': 'unknown', 'risk_factors': ['Analysis unavailable']},
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'investment_scoring'
        }

@api_router.get("/agents/investment-scoring/batch")
async def get_batch_investment_scores(
    symbols: str = Query(..., description="Comma-separated list of stock symbols"),
    limit: Optional[int] = Query(10, description="Maximum number of symbols to analyze")
):
    """
    Batch Investment Scoring for multiple symbols
    
    Efficiently generates investment scores for multiple stocks simultaneously.
    Useful for screening and portfolio analysis.
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')][:limit]
        
        logger.info(f"Investment Scoring Agent: Batch analysis for {len(symbol_list)} symbols")
        
        # Generate scores for all symbols
        batch_results = await investment_scoring_agent.get_batch_scores(symbol_list)
        
        return {
            'symbols_analyzed': len(batch_results),
            'successful_analyses': sum(1 for result in batch_results.values() if 'error' not in result),
            'results': batch_results,
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'investment_scoring_batch'
        }
        
    except Exception as e:
        logger.error(f"Batch investment scoring error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch investment scoring: {str(e)}")

@api_router.get("/agents/investment-scoring/methodology")
async def get_scoring_methodology():
    """
    Get detailed explanation of Investment Scoring methodology
    
    Returns transparency information about how scores are calculated,
    what data sources are used, and how weighting works.
    """
    try:
        methodology = investment_scoring_agent.get_scoring_explanation()
        
        return {
            'agent_name': 'Investment Scoring Agent',
            'version': '1.0',
            'scoring_methodology': methodology,
            'signal_weights': {
                'options_flow': '25% - Options sentiment and premium volume analysis',
                'dark_pool': '20% - Institutional activity through dark pool trading', 
                'congressional': '15% - Congressional insider trading activity',
                'ai_strategies': '20% - AI-generated trading strategy confidence',
                'market_momentum': '10% - Short-term momentum indicators',
                'risk_assessment': '10% - Risk-adjusted scoring factors'
            },
            'score_ranges': {
                '75-100': 'STRONG BUY / BUY',
                '55-74': 'HOLD+ / BUY',  
                '45-54': 'HOLD',
                '25-44': 'HOLD- / SELL',
                '0-24': 'STRONG SELL'
            },
            'confidence_levels': {
                'high': 'Consistent signals across multiple data sources',
                'medium': 'Some signal consistency with moderate agreement', 
                'low': 'Mixed or inconsistent signals across sources'
            },
            'data_sources': [
                'Unusual Whales Options Flow (real-time)',
                'Unusual Whales Dark Pool Activity',
                'Congressional Trading Data', 
                'AI-Generated Trading Strategies',
                'Technical Momentum Indicators'
            ],
            'update_frequency': 'Real-time analysis on request',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting scoring methodology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving methodology: {str(e)}")

# ==================== TECHNICAL ANALYSIS EXPERT AGENT ====================

@api_router.post("/agents/technical-analysis")
async def generate_technical_analysis(
    symbol: str = Query(..., description="Stock symbol to analyze"),
    include_smc: Optional[bool] = Query(True, description="Include Smart Money Concepts analysis")
):
    """
    Technical Analysis Expert Agent
    
    Advanced technical analysis using Smart Money Concepts and multiple indicators:
    - Smart Money Concepts (Order Blocks, Fair Value Gaps, Market Structure, Liquidity)
    - Multi-timeframe confluence analysis (Weekly, Daily, Hourly)
    - Technical indicators (RSI, MACD, EMA, Stochastic, Williams %R, ADX, Ichimoku)
    - Volume analysis (OBV, Volume trends, VWAP)
    - Support/Resistance levels with risk/reward calculations
    - Position sizing and entry timing recommendations
    
    Returns comprehensive technical score, signals, and professional trading recommendations.
    """
    try:
        logger.info(f"Technical Analysis Agent: Analyzing {symbol.upper()}")
        
        # Generate comprehensive technical analysis
        analysis = await technical_analysis_agent.generate_technical_analysis(
            symbol=symbol.upper(),
            include_smc=include_smc
        )
        
        # Add response metadata
        analysis.update({
            'agent_type': 'technical_analysis',
            'smc_included': include_smc,
            'timeframes_analyzed': ['weekly', 'daily', 'hourly'],
            'api_version': '1.0'
        })
        
        logger.info(f"Technical Analysis Agent: Generated score {analysis.get('technical_score')} "
                   f"for {symbol.upper()} with {analysis.get('confidence_level')} confidence")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Technical Analysis Agent error for {symbol}: {str(e)}")
        return {
            'symbol': symbol.upper(),
            'error': f"Failed to generate technical analysis: {str(e)}",
            'technical_score': 50.0,  # Neutral score on error
            'recommendation': 'HOLD',
            'confidence_level': 'low',
            'key_signals': [],
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'technical_analysis'
        }

@api_router.get("/agents/technical-analysis/batch")
async def get_batch_technical_analysis(
    symbols: str = Query(..., description="Comma-separated list of stock symbols"),
    limit: Optional[int] = Query(10, description="Maximum number of symbols to analyze"),
    include_smc: Optional[bool] = Query(True, description="Include Smart Money Concepts analysis")
):
    """
    Batch Technical Analysis for multiple symbols
    
    Efficiently generates technical analysis for multiple stocks simultaneously.
    Includes Smart Money Concepts, multi-timeframe analysis, and risk management.
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')][:limit]
        
        logger.info(f"Technical Analysis Agent: Batch analysis for {len(symbol_list)} symbols")
        
        # Generate technical analysis for all symbols
        batch_results = await technical_analysis_agent.get_batch_technical_analysis(symbol_list)
        
        return {
            'symbols_analyzed': len(batch_results),
            'successful_analyses': sum(1 for result in batch_results.values() if 'error' not in result),
            'results': batch_results,
            'smc_included': include_smc,
            'timestamp': datetime.now().isoformat(),
            'agent_type': 'technical_analysis_batch'
        }
        
    except Exception as e:
        logger.error(f"Batch technical analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch technical analysis: {str(e)}")

@api_router.get("/agents/technical-analysis/methodology")
async def get_technical_analysis_methodology():
    """
    Get detailed explanation of Technical Analysis methodology
    
    Returns transparency information about Smart Money Concepts, technical indicators,
    multi-timeframe analysis, and risk management approach.
    """
    try:
        methodology = technical_analysis_agent.get_technical_methodology()
        
        return {
            'agent_name': 'Technical Analysis Expert Agent',
            'version': '1.0',
            'technical_methodology': methodology,
            'analysis_weights': {
                'smart_money_concepts': '30% - Order Blocks, Fair Value Gaps, Market Structure, Liquidity analysis',
                'trend_analysis': '25% - MACD, EMA crossovers, ADX, Ichimoku Cloud systems',
                'momentum_oscillators': '20% - RSI, Stochastic, Williams %R with divergence detection',
                'support_resistance': '15% - Pivot points, weekly levels, Fibonacci retracements',
                'volume_analysis': '10% - OBV, Volume trends, VWAP for institutional flow detection'
            },
            'smart_money_concepts': {
                'order_blocks': 'Institutional accumulation/distribution zones with strong rejection',
                'fair_value_gaps': 'Price imbalances indicating institutional activity',
                'market_structure': 'Higher highs/lows analysis for trend determination',
                'liquidity_zones': 'Areas where stops are likely to be swept',
                'premium_discount': 'Price position analysis using Fibonacci levels'
            },
            'timeframe_analysis': {
                'weekly': '40% weight - Primary trend identification',
                'daily': '35% weight - Intermediate trend and structure',
                'hourly': '25% weight - Short-term confirmation signals'
            },
            'risk_management': {
                'position_sizing': 'Based on distance to support/resistance levels',
                'risk_reward_ratios': 'Minimum 2:1 reward-to-risk for entry recommendations',
                'stop_loss_placement': 'Based on technical support levels and ATR',
                'max_risk_per_trade': '2% of account per position'
            },
            'confidence_levels': {
                'high': 'Multiple timeframes aligned with consistent technical signals',
                'medium': 'Some confluence with moderate signal agreement',
                'low': 'Mixed signals or conflicting timeframe analysis'
            },
            'signal_categories': [
                'Smart Money Concepts (Order Blocks, FVG, Market Structure)',
                'Technical Indicators (RSI, MACD, EMA, Stochastic, etc.)',
                'Multi-timeframe Confluence',
                'Support/Resistance Analysis',
                'Volume Analysis and Confirmation',
                'Risk/Reward Entry Timing'
            ],
            'update_frequency': 'Real-time analysis on request with multi-timeframe data',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting technical analysis methodology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving technical methodology: {str(e)}")

# ==================== END UNUSUAL WHALES API ENDPOINTS ====================

# ==================== EXPERT OPTIONS TRADING ENDPOINTS ====================

@api_router.get("/expert-options/strategies/{symbol}")
async def get_expert_strategy_recommendations(symbol: str):
    """Get AI-powered expert options strategy recommendations"""
    try:
        recommendations = await expert_system.get_strategy_recommendations(symbol.upper())
        return {
            "symbol": symbol.upper(),
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
            "total_strategies": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error getting expert recommendations: {str(e)}")
        return {"error": "Failed to get expert recommendations", "details": str(e)}

@api_router.get("/expert-options/wheel/{symbol}")
async def get_wheel_strategy(symbol: str):
    """Get optimized Wheel strategy for symbol"""
    try:
        conditions = await expert_system.analyze_market_conditions(symbol.upper())
        wheel_strategy = await expert_system.generate_wheel_strategy(symbol.upper(), conditions)
        return {
            "strategy": wheel_strategy,
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating wheel strategy: {str(e)}")
        return {"error": "Failed to generate wheel strategy", "details": str(e)}

@api_router.get("/expert-options/iron-condor/{symbol}")
async def get_iron_condor_strategy(symbol: str):
    """Get optimized Iron Condor strategy for symbol"""
    try:
        conditions = await expert_system.analyze_market_conditions(symbol.upper())
        condor_strategy = await expert_system.generate_iron_condor_strategy(symbol.upper(), conditions)
        return {
            "strategy": condor_strategy,
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating iron condor strategy: {str(e)}")
        return {"error": "Failed to generate iron condor strategy", "details": str(e)}

@api_router.get("/expert-options/volatility/{symbol}")
async def get_volatility_strategy(symbol: str):
    """Get optimized Volatility Play strategy for symbol"""
    try:
        conditions = await expert_system.analyze_market_conditions(symbol.upper())
        volatility_strategy = await expert_system.generate_volatility_play_strategy(symbol.upper(), conditions)
        return {
            "strategy": volatility_strategy,
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating volatility strategy: {str(e)}")
        return {"error": "Failed to generate volatility strategy", "details": str(e)}

@api_router.get("/expert-options/learning/insights")
async def get_learning_insights():
    """Get insights from the machine learning system"""
    try:
        insights = await expert_system.get_learning_insights()
        return {
            "learning_insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting learning insights: {str(e)}")
        return {"error": "Failed to get learning insights", "details": str(e)}

@api_router.post("/expert-options/optimize/{strategy_type}")
async def optimize_strategy_parameters(strategy_type: str):
    """Trigger parameter optimization for a strategy"""
    try:
        # Validate strategy type
        strategy_enum = StrategyType(strategy_type.lower())
        
        await expert_system.optimize_parameters(strategy_enum)
        
        return {
            "message": f"Optimization completed for {strategy_type}",
            "strategy_type": strategy_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError:
        return {"error": f"Invalid strategy type: {strategy_type}"}
    except Exception as e:
        logger.error(f"Error optimizing strategy: {str(e)}")
        return {"error": "Failed to optimize strategy", "details": str(e)}

@api_router.get("/expert-options/market-analysis/{symbol}")
async def get_market_analysis(symbol: str):
    """Get detailed market analysis for options trading"""
    try:
        conditions = await expert_system.analyze_market_conditions(symbol.upper())
        return {
            "symbol": symbol.upper(),
            "market_conditions": conditions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing market conditions: {str(e)}")
        return {"error": "Failed to analyze market conditions", "details": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize token manager
token_manager = get_token_manager(ts_auth)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Enhanced Stock Market Analysis API")
    
    # Start token monitoring if authenticated
    if ts_auth.is_authenticated():
        await token_manager.start_monitoring()
        logger.info("✅ TradeStation token monitoring started")
    else:
        logger.info("⚠️ TradeStation not authenticated - token monitoring will start after login")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    logger.info("🛑 Shutting down Enhanced Stock Market Analysis API")
    
    # Stop token monitoring
    if token_manager:
        await token_manager.stop_monitoring()
    
    # Close database connection
    client.close()
    logger.info("✅ Shutdown complete")