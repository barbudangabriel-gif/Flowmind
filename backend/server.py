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

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import numpy as np
from advanced_scoring_engine import get_scoring_engine
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

# Portfolio Charts and Smart Rebalancing
from portfolio_charts_service import PortfolioChartsService
from smart_rebalancing_service import SmartRebalancingService

# Portfolio Management
from portfolio_management_service import PortfolioManagementService

# NEW: Option Selling compute + monitor service
from options_selling_service import (
    ComputeRequest, compute_selling,
    MonitorStartRequest, monitor_start, monitor_stop, monitor_status
)

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

# ... existing routes are below (omitted for brevity in this snippet) ...

# NEW: Option Selling compute endpoint
@api_router.post("/options/selling/compute")
async def options_selling_compute(req: ComputeRequest):
    try:
        result = await compute_selling(req)
        return {"status": "success", "data": result.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Options selling compute failed: {str(e)}")

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

# Mount router
app.include_router(api_router)

# CORS (kept at end to apply globally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = logging.getLogger("server")
logger.setLevel(logging.INFO)