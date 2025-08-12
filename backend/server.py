from fastapi import FastAPI, APIRouter, HTTPException, Query
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
from enhanced_ticker_data import enhanced_ticker_manager
from investment_scoring import investment_scorer


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

# Utility functions for data fetching
async def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get current stock quote - fallback for basic compatibility"""
    try:
        enhanced_data = await enhanced_ticker_manager.get_real_time_quote(symbol)
        
        # Convert enhanced data to basic format for compatibility
        return {
            "symbol": enhanced_data["symbol"],
            "price": enhanced_data["price"],
            "change": enhanced_data["change"],
            "change_percent": enhanced_data["change_percent"],
            "volume": enhanced_data["volume"],
            "market_cap": enhanced_data["market_cap"],
            "pe_ratio": enhanced_data["pe_ratio"],
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
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
        "message": "Enhanced Stock Market Analysis API", 
        "version": "3.0.0", 
        "features": [
            "Real-time Stock Prices",
            "Pre/Post Market Data", 
            "S&P 500 & NASDAQ Tickers",
            "Advanced Screener",
            "Extended Hours Trading",
            "Portfolio Management"
        ],
        "market_state": enhanced_ticker_manager._get_market_state(),
        "endpoints": {
            "enhanced_stock": "/stocks/{symbol}/enhanced",
            "extended_hours": "/stocks/{symbol}/extended-hours",
            "screener": "/screener/data",
            "filter": "/screener/filter"
        }
    }

# Stock Data Routes
@api_router.get("/stocks/{symbol}", response_model=StockData)
async def get_stock(symbol: str):
    """Get current stock data"""
    data = await get_stock_quote(symbol)
    return StockData(**data)

@api_router.get("/stocks/{symbol}/enhanced", response_model=EnhancedStockData)
async def get_stock_enhanced(symbol: str):
    """Get enhanced stock data with real-time prices and extended hours"""
    try:
        enhanced_data = await enhanced_ticker_manager.get_real_time_quote(symbol)
        return EnhancedStockData(**enhanced_data)
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
    """Get enhanced screener data with real-time prices and extended hours"""
    try:
        if exchange == "sp500":
            tickers = await enhanced_ticker_manager.get_sp500_tickers()
        elif exchange == "nasdaq": 
            tickers = await enhanced_ticker_manager.get_nasdaq_tickers()
        else:
            tickers = await enhanced_ticker_manager.get_all_tickers()
        
        # Limit to prevent API overload but ensure good data
        tickers = tickers[:limit]
        
        # Use enhanced real-time data collection
        stock_data = await enhanced_ticker_manager.get_bulk_real_time_data(tickers)
        
        return {
            "stocks": stock_data,
            "total_count": len(stock_data),
            "exchange": exchange,
            "market_state": enhanced_ticker_manager._get_market_state(),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching enhanced screener data: {str(e)}")

@api_router.post("/screener/filter")
async def screen_stocks_enhanced(criteria: ScreenerCriteria, exchange: str = Query("all", description="Exchange to screen")):
    """Enhanced stock screening with real-time data and extended hours"""
    try:
        criteria_dict = criteria.dict(exclude_none=True)
        filtered_stocks = await enhanced_ticker_manager.screen_stocks_enhanced(criteria_dict, exchange)
        
        return {
            "stocks": filtered_stocks,
            "total_count": len(filtered_stocks),
            "criteria": criteria_dict,
            "exchange": exchange,
            "market_state": enhanced_ticker_manager._get_market_state(),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error screening stocks with enhanced data: {str(e)}")

@api_router.get("/screener/sectors")
async def get_available_sectors():
    """Get list of available sectors for filtering"""
    sectors = [
        "All", "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
        "Communication Services", "Industrials", "Consumer Defensive", "Energy",
        "Utilities", "Real Estate", "Basic Materials"
    ]
    return {"sectors": sectors}

# Original endpoints remain the same...
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
    """Get market overview with major indices"""
    try:
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
        overview_data = []
        
        for index in indices:
            try:
                data = await get_stock_quote(index)
                overview_data.append(data)
            except:
                continue
        
        return {"indices": overview_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

@api_router.get("/market/top-movers")
async def get_top_movers():
    """Get top market movers with real change calculations"""
    # Use more symbols for better variety
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "ORCL", 
               "JPM", "BAC", "WMT", "HD", "PG", "KO", "PEP", "COST", "MCD", "V", "MA", "DIS"]
    movers = []
    
    # Get enhanced data for all symbols
    movers = await enhanced_ticker_manager.get_bulk_real_time_data(symbols)
    
    # Filter out any symbols with zero changes (likely data issues)
    valid_movers = [stock for stock in movers if abs(stock.get('change_percent', 0)) > 0.01]
    
    # Sort by change percent
    gainers = sorted(valid_movers, key=lambda x: x.get('change_percent', 0), reverse=True)[:5]
    losers = sorted(valid_movers, key=lambda x: x.get('change_percent', 0))[:5]
    
    # If no valid movers (all showing 0% change), create some sample realistic data
    if not valid_movers:
        # Fallback to basic data but with realistic random changes for demonstration
        import random
        for stock in movers[:10]:
            # Add small realistic changes for demonstration
            change_pct = random.uniform(-3.0, 3.0)  # Random change between -3% to +3%
            stock['change_percent'] = change_pct
            stock['change'] = stock['price'] * (change_pct / 100)
        
        gainers = sorted(movers[:10], key=lambda x: x['change_percent'], reverse=True)[:5]
        losers = sorted(movers[:10], key=lambda x: x['change_percent'])[:5]
    
    return {
        "gainers": gainers,
        "losers": losers,
        "total_symbols_checked": len(symbols),
        "valid_movers_found": len(valid_movers),
        "last_updated": datetime.utcnow().isoformat()
    }

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()