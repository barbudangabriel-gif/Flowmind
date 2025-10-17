"""
Dashboard API - Aggregate data endpoint
Provides unified dashboard data from all FlowMind modules
"""
from fastapi import APIRouter
from typing import Dict, Any
import logging

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

@router.get("/summary")
async def get_dashboard_summary() -> Dict[str, Any]:
 """
 Unified dashboard summary - aggregates data from all modules
 Returns mock data for now - TODO: integrate real data sources
 """
 try:
 # TODO: Replace with real data from:
 # - Mindfolio service
 # - IV Service
 # - Sell Puts service
 # - Flow service
 # - Investment scoring
 
 return {
 "mindfolio_summary": {
 "total_nav": 125000.50,
 "daily_pnl": 2450.25,
 "daily_pnl_pct": 1.96,
 "total_cash": 35000.00,
 "mindfolio_count": 3,
 "top_mindfolios": [
 {
 "id": "pf_abc",
 "name": "Main Trading",
 "value": 75000,
 "pnl_today": 1500,
 },
 {
 "id": "pf_def",
 "name": "Income Strategy",
 "value": 45000,
 "pnl_today": 850,
 },
 {
 "id": "pf_ghi",
 "name": "Experimental",
 "value": 5000,
 "pnl_today": 100,
 },
 ],
 },
 "options_highlights": {
 "iv_signals": [
 {
 "symbol": "TSLA",
 "strategy": "Iron Condor",
 "edge": "8.5%",
 "confidence": "82%",
 },
 {
 "symbol": "AAPL",
 "strategy": "Calendar Spread",
 "edge": "6.2%",
 "confidence": "75%",
 },
 ],
 "sell_puts_signals": [
 {
 "symbol": "NVDA",
 "strike": "$450",
 "premium": "$850",
 "probability": "71%",
 },
 {
 "symbol": "MSFT",
 "strike": "$380",
 "premium": "$620",
 "probability": "68%",
 },
 ],
 "active_strategies": 12,
 "total_premium_collected": 15250.00,
 "expiring_this_week": 3,
 },
 "market_intelligence": {
 "flow_summary": [
 {"symbol": "TSLA", "net_premium": 5200000, "sentiment": "bullish"},
 {"symbol": "AAPL", "net_premium": 3800000, "sentiment": "neutral"},
 {"symbol": "NVDA", "net_premium": 2900000, "sentiment": "bullish"},
 {"symbol": "MSFT", "net_premium": 2100000, "sentiment": "bearish"},
 {"symbol": "GOOGL", "net_premium": 1850000, "sentiment": "neutral"},
 ],
 "dark_pool": [
 {"symbol": "MSFT", "volume": 2500000, "premium": 1250000},
 {"symbol": "GOOGL", "volume": 1800000, "premium": 900000},
 ],
 "latest_news": [
 {
 "timestamp": "2025-10-15T10:30:00Z",
 "headline": "Tesla Q3 earnings beat expectations",
 "sentiment": "positive",
 "source": "news",
 },
 {
 "timestamp": "2025-10-15T09:15:00Z",
 "headline": "Pelosi bought NVDA calls worth $2M",
 "sentiment": "bullish",
 "source": "congress",
 },
 {
 "timestamp": "2025-10-15T08:45:00Z",
 "headline": "Apple insider sold 50k shares",
 "sentiment": "bearish",
 "source": "insiders",
 },
 ],
 },
 "stock_scoring": {
 "top_scored": [
 {
 "symbol": "NVDA",
 "score": 92,
 "sector": "Technology",
 "momentum": 0.85,
 "value": 0.78,
 },
 {
 "symbol": "MSFT",
 "score": 88,
 "sector": "Technology",
 "momentum": 0.82,
 "value": 0.81,
 },
 {
 "symbol": "AAPL",
 "score": 85,
 "sector": "Technology",
 "momentum": 0.79,
 "value": 0.83,
 },
 {
 "symbol": "TSLA",
 "score": 82,
 "sector": "Automotive",
 "momentum": 0.88,
 "value": 0.65,
 },
 {
 "symbol": "GOOGL",
 "score": 80,
 "sector": "Technology",
 "momentum": 0.75,
 "value": 0.80,
 },
 ],
 },
 "system_health": {
 "tradestation": {"status": "connected", "mode": "live"},
 "unusual_whales": {"status": "connected", "rate_limit_remaining": 450},
 "mongodb": {"status": "connected"},
 "redis": {"status": "fallback", "using_in_memory": True},
 },
 "recent_alerts": [
 {
 "timestamp": "2025-10-15T09:15:00Z",
 "type": "position_threshold",
 "message": "TSLA position exceeded 10% of mindfolio",
 "severity": "warning",
 },
 {
 "timestamp": "2025-10-15T08:30:00Z",
 "type": "module_stop_loss",
 "message": "IV Service daily loss limit approaching",
 "severity": "warning",
 },
 ],
 }
 except Exception as e:
 logger.error(f"Dashboard summary error: {e}")
 raise
