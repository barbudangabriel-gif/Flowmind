import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

# Import observability and config (optional for security audit)
try:
    from config import get_settings

    # TODO: Wire observability when needed
    # from observability import configure_logging, wire_observability

    OBSERVABILITY_AVAILABLE = True
except ImportError:
    # Observability modules not available - continue without them
    OBSERVABILITY_AVAILABLE = False

# Import services (temporarily disabled for security audit)
# from unusual_whales_service import UnusualWhalesService
# from tradestation_auth_service import tradestation_auth_service as ts_auth
# from tradestation_client import TradeStationClient
# from mindfolio_service import MindfolioService
# from trading_service import TradingService

# AI Agents
from investment_scoring_agent import InvestmentScoringAgent

# Options Calculator
# Mindfolio Charts and Smart Rebalancing
from mindfolio_charts_service import MindfolioChartsService

# Mindfolio Management
# NEW: Option Selling compute + monitor service + analysis
from options_selling_service import (
    AnalysisQuery,
    ComputeRequest,
    MonitorStartRequest,
    compute_selling,
    monitor_start,
    monitor_status,
    monitor_stop,
    options_analysis,
)
from smart_rebalancing_service import SmartRebalancingService
from technical_analysis_agent import TechnicalAnalysisAgent

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

# NEW: OAuth Callback Router
try:
    from app.routers.oauth import router as oauth_router

    OAUTH_ROUTER_AVAILABLE = True
except ImportError:
    OAUTH_ROUTER_AVAILABLE = False
    logger.warning("OAuth callback router not available")

# NEW: TradeStation Data Endpoints (accounts, balances, positions)
try:
    from app.routers.tradestation import router as ts_data_router

    TS_DATA_ROUTER_AVAILABLE = True
except ImportError:
    TS_DATA_ROUTER_AVAILABLE = False
    logger.warning("TradeStation data router not available")

# NEW: Mock Broker Endpoints (for UI testing without auth)
try:
    from app.routers.brokers_mock import router as brokers_mock_router

    BROKERS_MOCK_ROUTER_AVAILABLE = True
    logger.warning("🔓 Mock broker endpoints ENABLED (DEV ONLY!)")
except ImportError:
    BROKERS_MOCK_ROUTER_AVAILABLE = False
    logger.info("Mock broker endpoints not available")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# Alpha Vantage API
# Alpha Vantage removed - not used in this application

# Initialize services (temporarily disabled for security audit)
# uw_service = UnusualWhalesService()
# ts_client = TradeStationClient(ts_auth)
# mindfolio_service = MindfolioService(ts_client)
# trading_service = TradingService(ts_client)
# mindfolio_management_service = MindfolioManagementService(ts_auth)

# Initialize AI Agents
investment_scoring_agent = InvestmentScoringAgent()
technical_analysis_agent = TechnicalAnalysisAgent()

# Initialize new services
mindfolio_charts_service = MindfolioChartsService()
smart_rebalancing_service = SmartRebalancingService()

# Placeholder services for disabled functionality
uw_service = None
ts_client = None
mindfolio_service = None
trading_service = None
mindfolio_management_service = None
ts_auth = None

# Integration clients
try:
    from integrations.ts_client import TSClient
    from integrations.uw_client import UWClient

    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Integration clients not available: {e}")
    INTEGRATIONS_AVAILABLE = False
    UWClient = None
    TSClient = None

# Global flag to track initialization
mindfolio_service_initialized = False


async def initialize_mindfolio_service():
    """Initialize mindfolio management service with TradeStation data"""
    global mindfolio_service_initialized
    if not mindfolio_service_initialized:
        try:
            if mindfolio_management_service is not None:
                await mindfolio_management_service.initialize()
                mindfolio_service_initialized = True
                logger.info("Mindfolio management service initialized successfully")
            else:
                logger.warning(
                    "Mindfolio management service is disabled for security audit"
                )
                mindfolio_service_initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize mindfolio management service: {str(e)}")
            mindfolio_service_initialized = False


# Create the main app without a prefix
app = FastAPI(title="Enhanced Stock Market Analysis API", version="3.0.0")


# Application lifecycle events
@app.on_event("startup")
async def startup():
    """Initialize integration clients on startup"""
    logger.info("🚀 Starting FlowMind API Server...")

    # Validate critical environment variables
    logger.info("🔍 Validating environment configuration...")

    required_vars = {
        "MONGO_URL": os.getenv("MONGO_URL"),
    }

    optional_vars = {
        "TS_CLIENT_ID": os.getenv("TS_CLIENT_ID"),
        "TS_CLIENT_SECRET": os.getenv("TS_CLIENT_SECRET"),
        "UW_API_TOKEN": os.getenv("UW_API_TOKEN")
        or os.getenv("UNUSUAL_WHALES_API_KEY"),
        "REDIS_URL": os.getenv("REDIS_URL"),
    }

    # Check required variables
    missing_required = [key for key, val in required_vars.items() if not val]
    if missing_required:
        logger.error(
            f"❌ Missing required environment variables: {', '.join(missing_required)}"
        )
        logger.error("❌ Check your .env file or environment configuration")
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_required)}"
        )
    else:
        logger.info("✅ All required environment variables present")

    # Check optional variables (warnings only)
    missing_optional = [key for key, val in optional_vars.items() if not val]
    if missing_optional:
        logger.warning(f"⚠️  Missing optional variables: {', '.join(missing_optional)}")
        logger.warning("⚠️  Some features may be limited or use fallback mode")

    # Log configuration summary
    logger.info(
        f"📊 Redis: {'Configured' if optional_vars['REDIS_URL'] else 'Using fallback (in-memory)'}"
    )
    logger.info(
        f"📊 TradeStation: {'Available' if optional_vars['TS_CLIENT_ID'] else 'Not configured'}"
    )
    logger.info(
        f"📊 Unusual Whales: {'Available' if optional_vars['UW_API_TOKEN'] else 'Not configured'}"
    )

    # Start CORE ENGINE WebSocket stream consumer
    try:
        from backend.agents.core.websocket_manager import start_stream_consumer

        await start_stream_consumer()
        logger.info("✅ CORE ENGINE WebSocket stream consumer started")
    except Exception as e:
        logger.warning(f"⚠️  Failed to start WebSocket stream consumer: {e}")
        logger.warning("⚠️  Real-time streaming disabled")

    # Initialize integrations
    if INTEGRATIONS_AVAILABLE:
        uw_token = optional_vars["UW_API_TOKEN"]
        ts_credentials = {
            "client_id": optional_vars["TS_CLIENT_ID"],
            "client_secret": optional_vars["TS_CLIENT_SECRET"],
        }
        if uw_token and UWClient:
            try:
                app.state.uw = UWClient(uw_token)
                logger.info("✅ Unusual Whales client initialized")
            except Exception as e:
                logger.error(f"❌ UW client initialization failed: {e}")

        if ts_credentials["client_id"] and TSClient:
            try:
                app.state.ts = TSClient(
                    ts_credentials["client_id"], ts_credentials["client_secret"]
                )
                logger.info("✅ TradeStation client initialized")
            except Exception as e:
                logger.error(f"❌ TS client initialization failed: {e}")

    logger.info("✨ FlowMind API Server started successfully!")
    logger.info(
        f"🔑 TradeStation: {'Configured' if optional_vars['TS_CLIENT_ID'] else 'Demo mode'}"
    )
    logger.info(
        f"🐋 Unusual Whales: {'Configured' if optional_vars['UW_API_TOKEN'] else 'Demo mode'}"
    )

    if INTEGRATIONS_AVAILABLE:
        try:
            # Initialize UW client for trades data
            app.state.uw = UWClient()
            logger.info(" UW client initialized for trades data")

            # Initialize TS client for options chain data
            app.state.ts = TSClient()
            logger.info(" TS client initialized for options chain data")

        except Exception as e:
            logger.error(f" Failed to initialize integration clients: {e}")
            # Set None to prevent crashes if clients fail to initialize
            app.state.uw = None
            app.state.ts = None
    else:
        logger.warning(" Integration clients not available - using fallback mode")
        app.state.uw = None
        app.state.ts = None

    # Initialize Prometheus metrics
    try:
        from observability.metrics import initialize_metrics

        initialize_metrics()
        logger.info(" Prometheus metrics initialized")
    except Exception as e:
        logger.warning(f" Metrics initialization failed: {e}")

    # Run cache warmup if enabled
    warmup_enabled = os.getenv("WARMUP_ENABLED", "1") == "1"
    if warmup_enabled:
        try:
            from services.warmup import get_warmup_config, warmup_cache

            config = get_warmup_config()
            logger.info(
                f" Starting cache warmup (symbols: {len(config['symbols'])})..."
            )

            # Run warmup in background (don't block startup)
            import asyncio

            asyncio.create_task(
                warmup_cache(
                    symbols=config["symbols"],
                    include_flow=config["include_flow"],
                    parallel=config["parallel"],
                )
            )

        except Exception as e:
            logger.warning(f" Cache warmup failed: {e}")

    # Initialize WebSocket streaming
    try:
        from routers.stream import initialize_websocket

        await initialize_websocket()
    except Exception as e:
        logger.error(f" WebSocket initialization failed: {e}")

    # Auto-restore mindfolios from disk backups (in case Redis was cleared)
    try:
        from mindfolio import restore_all_mindfolios_from_backup

        restored_count = await restore_all_mindfolios_from_backup()
        if restored_count > 0:
            logger.info(f"✅ Auto-restored {restored_count} mindfolios from backup")
        else:
            logger.info("ℹ️  No mindfolios to restore from backup")
    except Exception as e:
        logger.warning(f"⚠️  Failed to auto-restore mindfolios from backup: {e}")

    logger.info("✨ FlowMind API Server started successfully!")


@app.on_event("shutdown")
async def shutdown():
    """Clean up integration clients on shutdown"""
    # Stop CORE ENGINE WebSocket stream consumer
    try:
        from backend.agents.core.websocket_manager import stop_stream_consumer

        await stop_stream_consumer()
        logger.info("✅ CORE ENGINE WebSocket stream consumer stopped")
    except Exception as e:
        logger.warning(f"⚠️  WebSocket stream consumer shutdown failed: {e}")

    # Shutdown WebSocket streaming
    try:
        from routers.stream import shutdown_websocket

        await shutdown_websocket()
    except Exception as e:
        logger.error(f"❌ WebSocket shutdown failed: {e}")

    try:
        if hasattr(app.state, "uw") and app.state.uw:
            await app.state.uw.aclose()
            logger.info(" UW client closed")

        if hasattr(app.state, "ts") and app.state.ts:
            await app.state.ts.aclose()
            logger.info(" TS client closed")

    except Exception as e:
        logger.error(f" Error closing integration clients: {e}")


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
            strategies=(
                [s.strip() for s in strategies.split(",")] if strategies else None
            ),
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


# TradeStation Authentication Endpoints (disabled for security audit)
@api_router.get("/auth/tradestation/status")
async def tradestation_auth_status():
    """Get TradeStation authentication status"""
    try:
        if ts_auth is None:
            return {
                "status": "disabled",
                "message": "TradeStation authentication is disabled for security audit",
                "timestamp": datetime.now().isoformat(),
            }
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
        if ts_auth is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation authentication is disabled for security audit",
            )
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
        if ts_auth is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation authentication is disabled for security audit",
            )
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
        if ts_auth is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation authentication is disabled for security audit",
            )
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


# TradeStation API Endpoints (disabled for security audit)
@api_router.get("/tradestation/accounts")
async def get_tradestation_accounts():
    """Get TradeStation accounts"""
    try:
        if ts_client is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation client is disabled for security audit",
            )
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
        if ts_client is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation client is disabled for security audit",
            )
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
        if ts_client is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation client is disabled for security audit",
            )
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
        if ts_client is None:
            raise HTTPException(
                status_code=503,
                detail="TradeStation client is disabled for security audit",
            )
        result = await ts_client.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


# NEW: Mount robust TradeStation authentication router FIRST (higher priority)
if ROBUST_TS_AVAILABLE:
    app.include_router(ts_auth_router, prefix="/api")
    logger.info(" Robust TradeStation authentication system mounted")
else:
    logger.warning(" Using legacy TradeStation authentication system")

# NEW: Mount OAuth callback router
if OAUTH_ROUTER_AVAILABLE:
    app.include_router(oauth_router, prefix="/api")
    logger.info(" OAuth callback router mounted at /api/oauth/tradestation/callback")
else:
    logger.warning(" OAuth callback router not available")

# NEW: Mount TradeStation data endpoints (accounts, balances, positions)
if TS_DATA_ROUTER_AVAILABLE:
    app.include_router(ts_data_router, prefix="/api")
    logger.info(" TradeStation data router mounted at /api/tradestation/*")
else:
    logger.warning(" TradeStation data router not available")
    logger.warning(" OAuth callback router not available")

# NEW: Mount Mock Broker Endpoints (for UI testing without auth)
if BROKERS_MOCK_ROUTER_AVAILABLE:
    app.include_router(brokers_mock_router, prefix="/api")
    logger.warning("🔓 Mock broker endpoints mounted at /api/{broker}/mock/* (DEV ONLY!)")
else:
    logger.info(" Mock broker endpoints not available")


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
        import secrets
        import time

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
        price = 150 + secrets.randbelow(5000) / 100  # 150-200

        data = []
        for i in range(limit, 0, -1):
            timestamp = now - (i * seconds)
            change = (secrets.randbelow(800) - 400) / 100  # -4 to +4
            open_price = price
            close_price = price + change
            high_price = (
                max(open_price, close_price) + secrets.randbelow(200) / 100
            )  # +0-2
            low_price = (
                min(open_price, close_price) - secrets.randbelow(200) / 100
            )  # -0 to -2
            volume = 100000 + secrets.randbelow(1900000)  # 100K-2M

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


# ============================================================================
# ROUTER IMPORTS (After App Configuration)
# ============================================================================
# NOTE: These imports must come AFTER app initialization and configuration
# to avoid circular import issues and ensure proper dependency injection.
# Suppresses E402 (module-import-not-at-top-of-file) - intentional pattern.
# ============================================================================

# Watchlist module
# Redis backtest cache
from bt_cache_integration import router as bt_router

# Mindfolios
# Diagnostics & monitoring
from bt_diagnostics import diagnostics_router, redis_diag_router
from bt_ops import router as bt_ops_router

# Mindfolio (formerly Mindfolios)
from mindfolio import router as mindfolio_router

# Trade routes
from trade_routes import router as trade_router
from watchlist.routes import router as watchlist_router

# Mount main API router (includes legacy endpoints)
app.include_router(api_router)
app.include_router(trade_router)
app.include_router(bt_router)
app.include_router(bt_ops_router)
app.include_router(diagnostics_router)
app.include_router(redis_diag_router)
app.include_router(mindfolio_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api/watchlists")

# Options provider router
from routers.options import router as options_router

app.include_router(options_router, prefix="/api")

# Flow provider router
from routers.flow import router as flow_router

app.include_router(flow_router, prefix="/api")

# Optimize router
from routers.optimize import router as optimize_router

app.include_router(optimize_router, prefix="/api")

# Builder router
from routers.builder import router as builder_router

app.include_router(builder_router, prefix="/api")

# Options Overview router
from routers.options_overview import router as options_overview_router

app.include_router(options_overview_router, prefix="/api")

# Options Flow router
from routers.options_flow import router as options_flow_router

app.include_router(options_flow_router, prefix="/api")

# Dashboard router
from routers.dashboard import router as dashboard_router

app.include_router(dashboard_router, prefix="/api")

# Geopolitical & News Intelligence router
from routers.geopolitical import router as geopolitical_router

app.include_router(geopolitical_router)  # Already has /api/geopolitical prefix

# Term Structure Volatility Arbitrage router
from routers.term_structure import router as term_structure_router

app.include_router(term_structure_router)  # Already has /api/term-structure prefix

# WebSocket Streaming router
from routers.stream import router as stream_router

app.include_router(stream_router)  # Already has /api/stream prefix

# CORE ENGINE router (198-agent hierarchical system)
from routers.core_engine import router as core_engine_router

app.include_router(core_engine_router)  # Already has /api/core-engine prefix

# Wire observability (metrics, structured logging, request correlation)
try:
    from config import get_settings
    from observability import setup_cors, setup_rate_limit, wire

    # Get settings
    settings = get_settings()

    # Wire observability
    wire(app)

    # Setup CORS and rate limiting
    setup_cors(app, settings.allowed_origins)
    setup_rate_limit(app, settings.rate_limit)

    print(
        " Production observability enabled: /metrics, CORS, rate limiting, structured logging"
    )
except ImportError as e:
    print(f" Production observability modules not available: {e}")
except Exception as e:
    print(f" Production observability setup failed: {e}")
# Continue without enhanced observability


# Health check endpoints
@app.get("/health")
@app.get("/healthz")
def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "FlowMind Analytics API",
        "version": "3.0.0",
        "tradestation_robust": ROBUST_TS_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/readyz")
async def readiness_check():
    """Service readiness check"""
    try:
        # Check Redis connection
        from redis_fallback import get_kv

        kv = await get_kv()
        await kv.get("health_check_test")
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "status": "ready" if redis_status == "connected" else "degraded",
        "redis": redis_status,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health/redis")
async def redis_health():
    """
    Redis cache health and statistics

    Returns detailed Redis status:
    - Connection status
    - Total keys count
    - Memory usage
    - Cache mode (Redis vs in-memory fallback)
    """
    try:
        from redis_fallback import get_kv

        kv = await get_kv()

        # Determine cache mode
        is_fallback = os.getenv("FM_FORCE_FALLBACK") == "1"
        cache_mode = "in-memory" if is_fallback else "redis"

        # Get cache stats
        try:
            # Try to get keys count (works for both Redis and AsyncTTLDict)
            if hasattr(kv, "keys"):
                all_keys = await kv.keys("*") if hasattr(kv.keys, "__call__") else []
                keys_count = len(all_keys) if isinstance(all_keys, list) else 0
            else:
                keys_count = 0

            # Memory info (Redis only)
            memory_used = None
            if cache_mode == "redis" and hasattr(kv, "info"):
                try:
                    info = await kv.info("memory")
                    memory_used = info.get("used_memory_human", "N/A")
                except (ConnectionError, TimeoutError, AttributeError) as e:
                    logger.debug(f"Could not fetch Redis memory info: {e}")
                    memory_used = "N/A"

            return {
                "status": "healthy",
                "mode": cache_mode,
                "connected": True,
                "keys_total": keys_count,
                "memory_used": memory_used or "N/A (in-memory mode)",
                "fallback_active": is_fallback,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning(f"Redis stats error: {e}")
            return {
                "status": "degraded",
                "mode": cache_mode,
                "connected": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unavailable",
            "mode": "unknown",
            "connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus exposition format:
    - API request counts and latency
    - Cache hits/misses
    - External API calls
    - Business metrics (strategies priced, flow trades)

    Usage:
    curl http://localhost:8000/metrics

    Prometheus scrape config:
    scrape_configs:
    - job_name: 'flowmind'
    static_configs:
    - targets: ['localhost:8000']
    """
    try:
        from fastapi.responses import Response

        from observability.metrics import export_metrics

        metrics_data, content_type = export_metrics()

        return Response(content=metrics_data, media_type=content_type)
    except Exception as e:
        logger.error(f"❌ Metrics export failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics export failed")

    # This code appears to be unreachable due to return statement above
    # Commenting out dead code
    # return {
    #     "status": "ready",
    #     "service": "FlowMind Analytics API",
    #     "redis": redis_status,  # ← Would be undefined here
    #     "tradestation": "configured" if ROBUST_TS_AVAILABLE else "not_configured",
    #     "timestamp": datetime.now().isoformat(),
    # }


# ═══════════════════════════════════════════════════════════════════════════
# CORE ENGINE - WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@app.websocket("/ws/signals")
async def websocket_signals_endpoint(websocket):
    """
    CORE ENGINE Real-time signal/news streaming via WebSocket.

    Connect: ws://localhost:8000/ws/signals
    
    Client commands:
    - {"action": "subscribe", "stream": "signals:universe"}
    - {"action": "unsubscribe", "stream": "signals:universe"}
    - {"action": "ping"}
    - {"action": "stats"}

    Server messages:
    - {"type": "signal", "stream": "signals:universe", "data": {...}, "timestamp": ...}
    - {"type": "news", "stream": "news:realtime", "data": {...}, "timestamp": ...}
    - {"type": "status", "action": "subscribed", "stream": "...", "timestamp": ...}
    """
    from backend.agents.core.websocket_manager import websocket_endpoint

    await websocket_endpoint(websocket)


# Rate limiting middleware
from middleware.rate_limit import rate_limit

app.middleware("http")(rate_limit)

# CORS (kept at end to apply globally)
# Resolve CORS settings
_cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    # Default: local dev (both http/https) and Vite
    "http://localhost:3000,https://localhost:3000,http://localhost:5173,https://localhost:5173",
)
try:
    # In case env provided as JSON array, try to normalize; otherwise treat as CSV
    if _cors_origins_env.strip().startswith("["):
        import json as _json

        _cors_origins = [o.strip() for o in _json.loads(_cors_origins_env)]
    else:
        _cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
except Exception:
    _cors_origins = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:5173",
        "https://localhost:5173",
    ]

# Allow Codespaces/GitHub dev URLs by default via regex (can be overridden via CORS_ORIGIN_REGEX)
_cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"^https:\/\/.*\.app\.github\.dev$")

logger.info(
    "CORS configured: allow_origins=%s allow_origin_regex=%s",
    _cors_origins,
    _cors_origin_regex,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEST: mindfolios import
