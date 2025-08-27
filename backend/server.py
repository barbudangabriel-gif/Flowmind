from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from unusual_whales_service import UnusualWhalesService

# TradeStation Integration
from tradestation_auth_service import tradestation_auth_service as ts_auth
from tradestation_client import TradeStationClient
from portfolio_service import PortfolioService
from trading_service import TradingService

# AI Agents
from investment_scoring_agent import InvestmentScoringAgent
from technical_analysis_agent import TechnicalAnalysisAgent

# Options Calculator

# Portfolio Charts and Smart Rebalancing
from portfolio_charts_service import PortfolioChartsService
from smart_rebalancing_service import SmartRebalancingService

# Portfolio Management
from portfolio_management_service import PortfolioManagementService

# NEW: Option Selling compute + monitor service + analysis
from options_selling_service import (
    ComputeRequest,
    compute_selling,
    MonitorStartRequest,
    monitor_start,
    monitor_stop,
    monitor_status,
    AnalysisQuery,
    options_analysis,
)

# Logger setup
logger = logging.getLogger("server")
logger.setLevel(logging.INFO)

# NEW: Robust TradeStation Token Management
try:
    from app.routers.tradestation_auth import router as ts_auth_router

    ROBUST_TS_AVAILABLE = True
except ImportError:
    ROBUST_TS_AVAILABLE = False
    logger.warning("Robust TradeStation auth not available - using legacy system")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
ts = (
    TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format="pandas")
    if ALPHA_VANTAGE_API_KEY
    else None
)
ti = (
    TechIndicators(key=ALPHA_VANTAGE_API_KEY, output_format="pandas")
    if ALPHA_VANTAGE_API_KEY
    else None
)

# Initialize Unusual Whales Service
uw_service = UnusualWhalesService()

# Initialize AI Agents
investment_scoring_agent = InvestmentScoringAgent()
technical_analysis_agent = TechnicalAnalysisAgent()

# Initialize TradeStation Services
ts_client = TradeStationClient(ts_auth)
portfolio_service = PortfolioService(ts_client)
trading_service = TradingService(ts_client)

# Initialize new services
portfolio_charts_service = PortfolioChartsService()
smart_rebalancing_service = SmartRebalancingService()
portfolio_management_service = PortfolioManagementService(ts_auth)

# Global flag to track initialization
portfolio_service_initialized = False


async def initialize_portfolio_service():
    """Initialize portfolio management service with TradeStation data"""
    global portfolio_service_initialized
    if not portfolio_service_initialized:
        try:
            await portfolio_management_service.initialize()
            portfolio_service_initialized = True
            logger.info("Portfolio management service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize portfolio management service: {str(e)}")
            portfolio_service_initialized = False


# Create the main app without a prefix
app = FastAPI(title="Enhanced Stock Market Analysis API", version="3.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# NEW: Option Selling compute endpoint
@api_router.post("/options/selling/compute")
async def options_selling_compute(req: ComputeRequest):
    try:
        result = await compute_selling(req)
        return {"status": "success", "data": result.dict()}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Options selling compute failed: {str(e)}"
        )


# NEW: Option Selling Monitor endpoints
@api_router.post("/options/selling/monitor/start")
async def options_selling_monitor_start(req: MonitorStartRequest):
    try:
        res = await monitor_start(req)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Monitor start failed: {str(e)}")


@api_router.post("/options/selling/monitor/stop")
async def options_selling_monitor_stop():
    try:
        res = await monitor_stop()
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Monitor stop failed: {str(e)}")


@api_router.get("/options/selling/monitor/status")
async def options_selling_monitor_status():
    try:
        res = await monitor_status()
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Monitor status failed: {str(e)}")


# NEW: Options Selling Analysis endpoint (simulated from monitor logs)
@api_router.get("/options/selling/analysis")
async def options_selling_analysis(
    range: str = Query(default="3M"),
    strategies: Optional[str] = Query(
        default=None, description="Comma separated list of signals to include"
    ),
    ticker: Optional[str] = Query(default=None),
    fill: str = Query(default="mid"),
    slippage: float = Query(default=0.05),
    commission: float = Query(default=0.65),
):
    try:
        q = AnalysisQuery(
            range=range,
            strategies=[s.strip() for s in strategies.split(",")]
            if strategies
            else None,
            ticker=ticker,
            fill=fill,
            slippage=slippage,
            commission=commission,
        )
        res = await options_analysis(q)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Options analysis failed: {str(e)}"
        )


# TradeStation Authentication Endpoints
@api_router.get("/auth/tradestation/status")
async def tradestation_auth_status():
    """Get TradeStation authentication status"""
    try:
        status = ts_auth.get_status()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get auth status: {str(e)}"
        )


@api_router.get("/auth/tradestation/login")
async def tradestation_auth_login():
    """Get TradeStation login URL"""
    try:
        auth_info = ts_auth.generate_auth_url()
        return auth_info
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate login URL: {str(e)}"
        )


@api_router.post("/auth/tradestation/refresh")
async def tradestation_token_refresh():
    """Refresh TradeStation access token"""
    try:
        success = await ts_auth.refresh_access_token()
        if success:
            return {
                "status": "success",
                "message": "Token refreshed successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "status": "error",
                "message": "Token refresh failed",
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@api_router.post("/auth/tradestation/callback")
async def tradestation_auth_callback(
    code: Optional[str] = Query(None), state: Optional[str] = Query(None)
):
    """Handle TradeStation OAuth callback"""
    try:
        if not code:
            raise HTTPException(
                status_code=422, detail="Authorization code is required"
            )
        if not state:
            raise HTTPException(status_code=422, detail="State parameter is required")

        result = await ts_auth.exchange_code_for_tokens(code)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Callback processing failed: {str(e)}"
        )


# TradeStation API Endpoints
@api_router.get("/tradestation/accounts")
async def get_tradestation_accounts():
    """Get TradeStation accounts"""
    try:
        accounts = await ts_client.get_accounts()
        return {
            "status": "success",
            "accounts": accounts,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")


@api_router.get("/tradestation/accounts/{account_id}/positions")
async def get_tradestation_positions(account_id: str):
    """Get positions for a TradeStation account"""
    try:
        positions = await ts_client.get_positions(account_id)

        # Convert Position objects to dictionaries
        positions_data = []
        for pos in positions:
            positions_data.append(
                {
                    "account_id": pos.account_id,
                    "symbol": pos.symbol,
                    "asset_type": pos.asset_type,
                    "quantity": pos.quantity,
                    "average_price": pos.average_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                    "position_type": "LONG" if pos.quantity > 0 else "SHORT",
                }
            )

        return {
            "status": "success",
            "data": positions_data,
            "count": len(positions_data),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get positions: {str(e)}"
        )


@api_router.get("/tradestation/positions/{account_id}")
async def get_tradestation_positions_alt(account_id: str):
    """Alternative endpoint for TradeStation positions (for compatibility)"""
    return await get_tradestation_positions(account_id)


@api_router.get("/tradestation/accounts/{account_id}/balances")
async def get_tradestation_balances(account_id: str):
    """Get balances for a TradeStation account"""
    try:
        balances = await ts_client.get_account_balances(account_id)
        return {
            "status": "success",
            "data": balances,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balances: {str(e)}")


@api_router.get("/tradestation/balances/{account_id}")
async def get_tradestation_balances_alt(account_id: str):
    """Alternative endpoint for TradeStation balances (for compatibility)"""
    return await get_tradestation_balances(account_id)


@api_router.get("/tradestation/connection/test")
async def test_tradestation_connection():
    """Test TradeStation API connection"""
    try:
        result = await ts_client.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


# NEW: Mount robust TradeStation authentication router FIRST (higher priority)
if ROBUST_TS_AVAILABLE:
    app.include_router(ts_auth_router, prefix="/api")
    logger.info("✅ Robust TradeStation authentication system mounted")
else:
    logger.warning("⚠️  Using legacy TradeStation authentication system")


# NEW: TradeStation streaming endpoint
@api_router.get("/tradestation/stream/{symbol}")
async def tradestation_stream(
    symbol: str,
    tf: str = Query(default="D", description="Timeframe"),
    limit: int = Query(default=500, description="Number of bars"),
):
    """Stream real-time OHLCV data from TradeStation"""
    try:
        # This would integrate with TradeStation streaming API
        # For now, return demo data structure
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": tf,
            "limit": limit,
            "stream_available": False,
            "message": "TradeStation streaming integration ready for implementation",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"TradeStation streaming failed: {str(e)}"
        )


# NEW: Chart data endpoint
@api_router.get("/market/chart/{symbol}")
async def get_chart_data(
    symbol: str,
    timeframe: str = Query(
        default="D", description="Timeframe: 1m, 5m, 15m, 1h, 4h, D, W"
    ),
    limit: int = Query(default=300, description="Number of bars"),
):
    """Get OHLCV chart data for a symbol"""
    try:
        # Generate demo OHLCV data
        import time
        import random

        # Timeframe mapping to seconds
        tf_seconds = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "D": 86400,
            "W": 604800,
        }

        seconds = tf_seconds.get(timeframe, 86400)
        now = int(time.time())
        price = 150 + random.random() * 50

        data = []
        for i in range(limit, 0, -1):
            timestamp = now - (i * seconds)
            change = (random.random() - 0.5) * 4
            open_price = price
            close_price = price + change
            high_price = max(open_price, close_price) + random.random() * 2
            low_price = min(open_price, close_price) - random.random() * 2
            volume = random.randint(100000, 2000000)

            data.append(
                {
                    "time": timestamp,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                }
            )

            price = close_price

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "limit": limit,
            "data": data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Chart data generation failed: {str(e)}"
        )


# Watchlist module
from watchlist.routes import router as watchlist_router

# Mount main API router (includes legacy endpoints)
app.include_router(api_router)
app.include_router(watchlist_router, prefix="/api/watchlists")


# Health check endpoint
@app.get("/health")
def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "FlowMind Analytics API",
        "version": "3.0.0",
        "tradestation_robust": ROBUST_TS_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }


# CORS (kept at end to apply globally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
