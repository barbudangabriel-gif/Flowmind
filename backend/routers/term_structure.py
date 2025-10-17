"""
Term Structure API Router

REST API endpoints for term structure volatility arbitrage module.

Endpoints:
- GET /api/term-structure/scan - Scan earnings calendar for opportunities
- GET /api/term-structure/opportunities - Get ranked opportunities
- GET /api/term-structure/backtest/{symbol} - Backtest symbol
- POST /api/term-structure/execute - Execute calendar spread
- GET /api/term-structure/positions - Get active positions
- GET /api/term-structure/module-stats - Get module statistics

Author: FlowMind AI Team 
Date: October 15, 2025
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

# Import our components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_structure_agent import TermStructureAgent
from term_structure_supervisor import TermStructureSupervisor
from ml.iv_crush_predictor import IVCrushPredictor
from services.calendar_backtest import CalendarBacktest

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/term-structure", tags=["term-structure"])

# Initialize components (singletons for demo)
ml_predictor = IVCrushPredictor()
calendar_backtest = CalendarBacktest()
term_structure_agent = TermStructureAgent(ml_predictor=ml_predictor)

# Store active supervisors per mindfolio
active_supervisors = {}

@router.get("/scan")
async def scan_earnings_calendar(
 days_ahead: int = Query(30, ge=1, le=90, description="Days ahead to scan"),
 min_fwd_vol_factor: float = Query(1.3, ge=1.0, le=3.0, description="Minimum forward vol factor")
):
 """
 Scan upcoming earnings calendar for term structure opportunities
 
 Returns top opportunities ranked by forward volatility factor and ML predictions.
 """
 try:
 logger.info(f"Scanning earnings calendar: {days_ahead} days ahead, min factor {min_fwd_vol_factor}")
 
 # Scan for opportunities
 opportunities = await term_structure_agent.scan_earnings_calendar(days_ahead=days_ahead)
 
 # Filter by minimum factor
 filtered = [
 opp for opp in opportunities 
 if opp["forward_vol_factor"] >= min_fwd_vol_factor
 ]
 
 logger.info(f"Found {len(filtered)} opportunities (filtered from {len(opportunities)})")
 
 return {
 "status": "success",
 "data": {
 "opportunities": filtered,
 "total_scanned": len(opportunities),
 "total_filtered": len(filtered),
 "min_fwd_vol_factor": min_fwd_vol_factor,
 "scan_date": datetime.now().isoformat()
 }
 }
 
 except Exception as e:
 logger.error(f"Error scanning earnings calendar: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/opportunities")
async def get_top_opportunities(
 limit: int = Query(20, ge=1, le=100, description="Number of opportunities to return"),
 min_backtest_win_rate: float = Query(0.65, ge=0.0, le=1.0, description="Minimum backtest win rate")
):
 """
 Get top-ranked term structure opportunities
 
 Returns opportunities sorted by opportunity_score with backtest validation.
 """
 try:
 # Scan all opportunities
 opportunities = await term_structure_agent.scan_earnings_calendar(days_ahead=30)
 
 # Filter by backtest win rate
 filtered = [
 opp for opp in opportunities
 if opp.get("backtest", {}).get("win_rate", 0) >= min_backtest_win_rate
 ]
 
 # Limit to top N
 top_opportunities = filtered[:limit]
 
 return {
 "status": "success",
 "data": {
 "opportunities": top_opportunities,
 "total_available": len(filtered),
 "filters": {
 "min_backtest_win_rate": min_backtest_win_rate,
 "limit": limit
 },
 "timestamp": datetime.now().isoformat()
 }
 }
 
 except Exception as e:
 logger.error(f"Error getting opportunities: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtest/{symbol}")
async def backtest_symbol(
 symbol: str,
 lookback_quarters: int = Query(8, ge=1, le=20, description="Number of quarters to backtest"),
 position_size: int = Query(1, ge=1, le=10, description="Position size per trade")
):
 """
 Backtest calendar spread strategy for a specific symbol
 
 Returns historical performance metrics over past N earnings.
 """
 try:
 logger.info(f"Backtesting {symbol} over {lookback_quarters} quarters")
 
 # Run backtest
 results = await calendar_backtest.backtest_symbol(
 symbol=symbol,
 lookback_quarters=lookback_quarters,
 position_size=position_size
 )
 
 return {
 "status": "success",
 "data": {
 "symbol": symbol,
 "backtest_results": results,
 "parameters": {
 "lookback_quarters": lookback_quarters,
 "position_size": position_size
 },
 "timestamp": datetime.now().isoformat()
 }
 }
 
 except Exception as e:
 logger.error(f"Error backtesting {symbol}: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml-prediction/{symbol}")
async def get_ml_prediction(
 symbol: str,
 current_iv: float = Query(..., ge=0.0, le=3.0, description="Current IV"),
 sector: str = Query("Unknown", description="Company sector"),
 market_cap: float = Query(0, ge=0, description="Market cap"),
 iv_rank: Optional[float] = Query(None, ge=0, le=100, description="IV rank")
):
 """
 Get ML prediction for IV crush after earnings
 """
 try:
 logger.info(f"Getting ML prediction for {symbol}")
 
 # Get prediction with full metadata
 prediction = await ml_predictor.get_prediction_with_metadata(
 symbol=symbol,
 current_iv=current_iv,
 sector=sector,
 market_cap=market_cap,
 iv_rank=iv_rank
 )
 
 return {
 "status": "success",
 "data": prediction
 }
 
 except Exception as e:
 logger.error(f"Error getting ML prediction for {symbol}: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_calendar_spread(
 mindfolio_id: str,
 symbol: str,
 strike: float,
 front_expiration: str,
 back_expiration: str,
 position_size: int = 1,
 auto_execute: bool = False
):
 """
 Execute calendar spread trade
 
 Validates trade through supervisor, executes if approved.
 """
 try:
 logger.info(f"Execute calendar spread: {symbol} {strike} {position_size}x")
 
 # Get or create supervisor for this mindfolio
 if mindfolio_id not in active_supervisors:
 # Demo config
 module_config = {
 "budget": 10000,
 "max_risk_per_trade": 500,
 "daily_loss_limit": 1000,
 "autotrade": auto_execute
 }
 active_supervisors[mindfolio_id] = TermStructureSupervisor(
 mindfolio_id=mindfolio_id,
 module_config=module_config
 )
 
 supervisor = active_supervisors[mindfolio_id]
 
 # Build opportunity for validation
 opportunity = {
 "symbol": symbol,
 "spread_cost": 3.70, # Demo value
 "trade_recommendation": {
 "position_size": position_size
 },
 "backtest": {
 "win_rate": 0.75 # Demo value
 }
 }
 
 # Validate trade
 validation = await supervisor.validate_trade(opportunity)
 
 if not validation.approved:
 return {
 "status": "rejected",
 "reason": validation.reason,
 "timestamp": datetime.now().isoformat()
 }
 
 # If auto-execute and approved, execute via TradeStation
 if auto_execute:
 # TODO: Integrate with TradeStation execution
 order_id = f"TS_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
 
 logger.info(f"Executing order: {order_id}")
 
 return {
 "status": "executed",
 "order_id": order_id,
 "symbol": symbol,
 "strike": strike,
 "position_size": position_size,
 "validation": {
 "approved": True,
 "warnings": validation.warnings
 },
 "timestamp": datetime.now().isoformat()
 }
 else:
 # Manual approval required
 return {
 "status": "pending_approval",
 "symbol": symbol,
 "strike": strike,
 "position_size": position_size,
 "validation": {
 "approved": True,
 "reason": validation.reason,
 "warnings": validation.warnings
 },
 "message": "Trade validated, waiting for user approval",
 "timestamp": datetime.now().isoformat()
 }
 
 except Exception as e:
 logger.error(f"Error executing calendar spread: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/{mindfolio_id}")
async def get_active_positions(mindfolio_id: str):
 """
 Get active calendar spread positions for a mindfolio
 """
 try:
 if mindfolio_id not in active_supervisors:
 return {
 "status": "success",
 "data": {
 "positions": [],
 "count": 0,
 "message": "No active module for this mindfolio"
 }
 }
 
 supervisor = active_supervisors[mindfolio_id]
 
 # Get positions from supervisor
 status = await supervisor.monitor_positions()
 
 return {
 "status": "success",
 "data": status
 }
 
 except Exception as e:
 logger.error(f"Error getting positions for {mindfolio_id}: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/module-stats/{mindfolio_id}")
async def get_module_stats(mindfolio_id: str):
 """
 Get module statistics and performance metrics
 """
 try:
 if mindfolio_id not in active_supervisors:
 return {
 "status": "success",
 "data": {
 "message": "No active module for this mindfolio",
 "module_active": False
 }
 }
 
 supervisor = active_supervisors[mindfolio_id]
 stats = supervisor.get_module_stats()
 
 return {
 "status": "success",
 "data": {
 **stats,
 "module_active": True
 }
 }
 
 except Exception as e:
 logger.error(f"Error getting module stats for {mindfolio_id}: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.post("/module/{mindfolio_id}/pause")
async def pause_module(mindfolio_id: str, reason: str = "Manual pause"):
 """
 Pause term structure module
 """
 try:
 if mindfolio_id not in active_supervisors:
 raise HTTPException(status_code=404, detail="Module not found")
 
 supervisor = active_supervisors[mindfolio_id]
 await supervisor.pause_module(reason=reason)
 
 return {
 "status": "success",
 "message": f"Module paused: {reason}",
 "timestamp": datetime.now().isoformat()
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Error pausing module: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.post("/module/{mindfolio_id}/resume")
async def resume_module(mindfolio_id: str):
 """
 Resume term structure module
 """
 try:
 if mindfolio_id not in active_supervisors:
 raise HTTPException(status_code=404, detail="Module not found")
 
 supervisor = active_supervisors[mindfolio_id]
 success = await supervisor.resume_module()
 
 if not success:
 raise HTTPException(status_code=400, detail="Cannot resume from EMERGENCY_STOP")
 
 return {
 "status": "success",
 "message": "Module resumed",
 "timestamp": datetime.now().isoformat()
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Error resuming module: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.post("/module/{mindfolio_id}/emergency-stop")
async def emergency_stop(mindfolio_id: str, reason: str = "Manual emergency stop"):
 """
 Emergency stop - pause module and close all positions
 """
 try:
 if mindfolio_id not in active_supervisors:
 raise HTTPException(status_code=404, detail="Module not found")
 
 supervisor = active_supervisors[mindfolio_id]
 result = await supervisor.emergency_stop(reason=reason)
 
 return {
 "status": "success",
 "data": result
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f"Error in emergency stop: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
 """
 Health check endpoint
 """
 return {
 "status": "healthy",
 "service": "term-structure-api",
 "timestamp": datetime.now().isoformat(),
 "components": {
 "agent": "operational",
 "supervisor": "operational",
 "ml_predictor": ml_predictor.get_model_info(),
 "backtest_engine": "operational"
 }
 }
