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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
ti = TechIndicators(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Create the main app without a prefix
app = FastAPI(title="Stock Market Analysis API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StockData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

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

class StockNews(BaseModel):
    title: str
    url: str
    summary: str
    source: str
    published_date: datetime

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
    """Get current stock quote using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period="1d")
        
        if history.empty:
            raise HTTPException(status_code=404, detail=f"Stock data not found for {symbol}")
            
        latest = history.iloc[-1]
        
        return {
            "symbol": symbol.upper(),
            "price": float(latest['Close']),
            "change": float(latest['Close'] - history.iloc[-2]['Close']) if len(history) > 1 else 0.0,
            "change_percent": float(((latest['Close'] - history.iloc[-2]['Close']) / history.iloc[-2]['Close']) * 100) if len(history) > 1 else 0.0,
            "volume": int(latest['Volume']),
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('forwardPE'),
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
    return {"message": "Stock Market Analysis API", "version": "1.0.0"}

# Stock Data Routes
@api_router.get("/stocks/{symbol}", response_model=StockData)
async def get_stock(symbol: str):
    """Get current stock data"""
    data = await get_stock_quote(symbol)
    return StockData(**data)

@api_router.get("/stocks/{symbol}/history")
async def get_stock_history(symbol: str, period: str = Query("1y", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")):
    """Get historical stock data"""
    return await get_historical_data(symbol, period)

@api_router.get("/stocks/{symbol}/indicators", response_model=TechnicalIndicatorData)
async def get_stock_indicators(symbol: str):
    """Get technical indicators for a stock"""
    data = await get_technical_indicators(symbol)
    return TechnicalIndicatorData(**data)

@api_router.get("/stocks/search/{query}")
async def search_stocks(query: str):
    """Search for stocks by symbol or company name"""
    try:
        # Simple search using yfinance
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

# Portfolio Routes
@api_router.post("/portfolio", response_model=PortfolioItem)
async def add_portfolio_item(item: PortfolioItemCreate):
    """Add item to portfolio"""
    # Get current stock price
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
        # Get current price
        try:
            current_data = await get_stock_quote(item_data['symbol'])
            item_data['current_price'] = current_data['price']
            item_data['current_value'] = current_data['price'] * item_data['shares']
            item_data['profit_loss'] = (current_data['price'] - item_data['purchase_price']) * item_data['shares']
            item_data['profit_loss_percent'] = ((current_data['price'] - item_data['purchase_price']) / item_data['purchase_price']) * 100
            
            total_value += item_data['current_value']
            total_cost += item_data['purchase_price'] * item_data['shares']
        except:
            # If can't get current price, use stored values
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

# Watchlist Routes
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

# Market Overview Routes
@api_router.get("/market/overview")
async def get_market_overview():
    """Get market overview with major indices"""
    try:
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]  # S&P 500, Dow, NASDAQ, Russell 2000
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
    """Get top market movers"""
    # Popular stocks to check
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "ORCL"]
    movers = []
    
    for symbol in symbols:
        try:
            data = await get_stock_quote(symbol)
            movers.append(data)
        except:
            continue
    
    # Sort by change percent
    gainers = sorted(movers, key=lambda x: x['change_percent'], reverse=True)[:5]
    losers = sorted(movers, key=lambda x: x['change_percent'])[:5]
    
    return {
        "gainers": gainers,
        "losers": losers
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