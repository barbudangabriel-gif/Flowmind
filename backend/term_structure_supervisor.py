"""
Term Structure Supervisor - Risk Management & Trade Validation

This supervisor monitors calendar spread positions, enforces budget limits,
validates ML predictions, and implements emergency stop controls.

Key Responsibilities:
- Pre-trade validation (budget, risk limits, ML confidence)
- Position monitoring (P&L, Greeks, time decay)
- Auto-pause on daily loss limit
- Emergency stop on portfolio drawdown
- Trade approval workflow for manual mode

Author: FlowMind AI Team
Date: October 15, 2025
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class ModuleStatus(Enum):
 """Module operational status"""
 ACTIVE = "ACTIVE"
 PAUSED = "PAUSED"
 STOPPED = "STOPPED"
 EMERGENCY_STOP = "EMERGENCY_STOP"

class TradeValidationResult:
 """Result of pre-trade validation"""
 def __init__(self, approved: bool, reason: str = "", warnings: List[str] = None):
 self.approved = approved
 self.reason = reason
 self.warnings = warnings or []

class TermStructureSupervisor:
 """
 Supervisor for Term Structure Arbitrage Module
 
 Monitors and controls all calendar spread trading activity with:
 - Budget enforcement
 - Risk limit validation
 - ML prediction confidence checks
 - Daily loss limits
 - Portfolio-level emergency stops
 """
 
 def __init__(self, mindfolio_id: str, module_config: Dict):
 """
 Initialize supervisor
 
 Args:
 mindfolio_id: ID of parent Mindfolio
 module_config: Module configuration with budget and risk limits
 """
 self.mindfolio_id = mindfolio_id
 self.config = module_config
 
 # Extract config
 self.budget = module_config.get("budget", 10000)
 self.max_risk_per_trade = module_config.get("max_risk_per_trade", 500)
 self.daily_loss_limit = module_config.get("daily_loss_limit", 1000)
 self.autotrade = module_config.get("autotrade", False)
 
 # State tracking
 self.status = ModuleStatus.ACTIVE
 self.budget_used = 0.0
 self.daily_pnl = 0.0
 self.total_pnl = 0.0
 self.positions = []
 self.trade_history = []
 
 # Risk metrics
 self.max_positions = module_config.get("max_positions", 10)
 self.min_ml_confidence = module_config.get("min_ml_confidence", 0.70)
 self.min_backtest_win_rate = module_config.get("min_backtest_win_rate", 0.65)
 self.max_correlation = module_config.get("max_correlation", 0.70)
 
 # Emergency thresholds
 self.emergency_drawdown_pct = 0.20 # 20% drawdown triggers emergency stop
 self.emergency_daily_loss_pct = 0.15 # 15% daily loss triggers emergency stop
 
 logger.info(
 f"TermStructureSupervisor initialized for Mindfolio {mindfolio_id} "
 f"with budget ${self.budget:,.2f}"
 )
 
 async def validate_trade(
 self, 
 opportunity: Dict,
 ml_prediction: Optional[Dict] = None
 ) -> TradeValidationResult:
 """
 Validate trade before execution
 
 Checks:
 1. Module status (not paused/stopped)
 2. Budget availability
 3. Risk limits
 4. ML prediction confidence
 5. Backtest performance
 6. Position concentration
 7. Correlation risk
 
 Args:
 opportunity: Trade opportunity from agent
 ml_prediction: ML model prediction (optional)
 
 Returns:
 TradeValidationResult with approval status and reason
 """
 warnings = []
 
 # Check 1: Module status
 if self.status != ModuleStatus.ACTIVE:
 return TradeValidationResult(
 approved=False,
 reason=f"Module status is {self.status.value}, not accepting new trades"
 )
 
 # Check 2: Budget availability
 spread_cost = opportunity.get("spread_cost", 0)
 position_size = opportunity["trade_recommendation"].get("position_size", 1)
 total_cost = spread_cost * position_size * 100 # Per contract
 
 available_budget = self.budget - self.budget_used
 
 if total_cost > available_budget:
 return TradeValidationResult(
 approved=False,
 reason=f"Insufficient budget: Need ${total_cost:,.2f}, have ${available_budget:,.2f}"
 )
 
 # Check 3: Risk limit per trade
 max_risk = spread_cost * position_size * 100
 
 if max_risk > self.max_risk_per_trade:
 return TradeValidationResult(
 approved=False,
 reason=f"Risk ${max_risk:,.2f} exceeds max_risk_per_trade ${self.max_risk_per_trade:,.2f}"
 )
 
 # Check 4: Daily loss limit
 if self.daily_pnl < -self.daily_loss_limit:
 return TradeValidationResult(
 approved=False,
 reason=f"Daily loss limit hit: ${self.daily_pnl:,.2f} / ${-self.daily_loss_limit:,.2f}"
 )
 
 # Check 5: ML prediction confidence
 if ml_prediction:
 confidence = ml_prediction.get("confidence", 0)
 if confidence < self.min_ml_confidence:
 warnings.append(
 f"ML confidence {confidence:.2%} below minimum {self.min_ml_confidence:.2%}"
 )
 
 # Check 6: Backtest performance
 backtest = opportunity.get("backtest", {})
 win_rate = backtest.get("win_rate", 0)
 
 if win_rate < self.min_backtest_win_rate:
 return TradeValidationResult(
 approved=False,
 reason=f"Backtest win rate {win_rate:.2%} below minimum {self.min_backtest_win_rate:.2%}"
 )
 
 # Check 7: Position limit
 if len(self.positions) >= self.max_positions:
 return TradeValidationResult(
 approved=False,
 reason=f"Max positions ({self.max_positions}) reached"
 )
 
 # Check 8: Concentration risk
 symbol = opportunity.get("symbol")
 symbol_exposure = self._calculate_symbol_exposure(symbol)
 
 if symbol_exposure + total_cost > self.budget * 0.30: # Max 30% in one symbol
 warnings.append(
 f"High concentration in {symbol}: {((symbol_exposure + total_cost) / self.budget * 100):.1f}%"
 )
 
 # Check 9: Correlation risk
 sector = opportunity.get("sector", "Unknown")
 sector_exposure = self._calculate_sector_exposure(sector)
 
 if sector_exposure + total_cost > self.budget * 0.50: # Max 50% in one sector
 warnings.append(
 f"High sector exposure in {sector}: {((sector_exposure + total_cost) / self.budget * 100):.1f}%"
 )
 
 # Check 10: Risk/Reward ratio
 expected_profit = opportunity.get("expected_profit", 0) * position_size * 100
 risk_reward_ratio = expected_profit / max_risk if max_risk > 0 else 0
 
 if risk_reward_ratio < 1.0:
 warnings.append(
 f"Low risk/reward ratio: {risk_reward_ratio:.2f}:1 (expected)"
 )
 
 # All checks passed
 approval_msg = f"Trade validated: {symbol} calendar spread, ${total_cost:,.2f} cost"
 
 if warnings:
 approval_msg += f" (with {len(warnings)} warnings)"
 
 return TradeValidationResult(
 approved=True,
 reason=approval_msg,
 warnings=warnings
 )
 
 async def monitor_positions(self) -> Dict:
 """
 Monitor all active positions
 
 Checks:
 - P&L status
 - Time decay (theta)
 - Exit conditions
 - Risk alerts
 
 Returns:
 Status summary with alerts
 """
 alerts = []
 position_summaries = []
 
 for position in self.positions:
 # Calculate current P&L
 current_pnl = await self._calculate_position_pnl(position)
 
 # Update position P&L
 position["current_pnl"] = current_pnl
 position["current_pnl_pct"] = (current_pnl / position["cost"]) * 100
 
 # Check exit conditions
 exit_signals = self._check_exit_conditions(position)
 
 if exit_signals:
 alerts.append({
 "type": "EXIT_SIGNAL",
 "symbol": position["symbol"],
 "signals": exit_signals,
 "current_pnl": current_pnl
 })
 
 # Check risk alerts
 risk_alerts = self._check_risk_alerts(position)
 
 if risk_alerts:
 alerts.extend(risk_alerts)
 
 position_summaries.append({
 "symbol": position["symbol"],
 "entry_date": position["entry_date"],
 "dte_front": position["dte_front"],
 "cost": position["cost"],
 "current_pnl": current_pnl,
 "current_pnl_pct": position["current_pnl_pct"],
 "status": position["status"]
 })
 
 # Calculate aggregate metrics
 total_position_pnl = sum(p["current_pnl"] for p in self.positions)
 
 # Check emergency conditions
 emergency_alerts = self._check_emergency_conditions(total_position_pnl)
 
 if emergency_alerts:
 alerts.extend(emergency_alerts)
 
 return {
 "status": self.status.value,
 "positions_count": len(self.positions),
 "budget_used": self.budget_used,
 "budget_available": self.budget - self.budget_used,
 "daily_pnl": self.daily_pnl,
 "total_pnl": self.total_pnl,
 "positions": position_summaries,
 "alerts": alerts,
 "timestamp": datetime.now().isoformat()
 }
 
 async def _calculate_position_pnl(self, position: Dict) -> float:
 """
 Calculate current P&L for a position
 
 For calendar spread:
 P&L = (current_front_value - entry_front_value) - 
 (current_back_value - entry_back_value)
 """
 # Demo: Simulate P&L based on time decay and IV changes
 days_held = (datetime.now() - datetime.fromisoformat(position["entry_date"])).days
 
 # Front month decays faster (benefit to us since we sold it)
 front_decay = position["front_premium"] * (days_held / position["dte_front"]) * 0.7
 
 # Back month decays slower (slight loss since we bought it)
 back_decay = position["back_premium"] * (days_held / position["dte_back"]) * 0.3
 
 # Net P&L
 pnl = front_decay - back_decay - (position["cost"] * 0.05) # 5% slippage
 
 return pnl * position["quantity"] * 100
 
 def _check_exit_conditions(self, position: Dict) -> List[str]:
 """Check if position should be exited"""
 signals = []
 
 # Exit 1: Earnings passed (primary exit)
 if datetime.now() > datetime.fromisoformat(position["earnings_date"]):
 signals.append("EARNINGS_PASSED")
 
 # Exit 2: Profit target hit (e.g., 80% of max profit)
 target_profit = position.get("target_profit", 0)
 if position.get("current_pnl", 0) >= target_profit * 0.80:
 signals.append("PROFIT_TARGET")
 
 # Exit 3: Stop loss hit (e.g., -50% of cost)
 stop_loss = -position["cost"] * 0.50
 if position.get("current_pnl", 0) <= stop_loss:
 signals.append("STOP_LOSS")
 
 # Exit 4: Front month expiration approaching (3 days)
 if position["dte_front"] <= 3:
 signals.append("EXPIRATION_NEAR")
 
 return signals
 
 def _check_risk_alerts(self, position: Dict) -> List[Dict]:
 """Check for risk alerts on position"""
 alerts = []
 
 # Alert 1: Large unrealized loss
 if position.get("current_pnl", 0) < -position["cost"] * 0.30:
 alerts.append({
 "type": "LARGE_LOSS",
 "symbol": position["symbol"],
 "severity": "HIGH",
 "message": f"Position down {position.get('current_pnl_pct', 0):.1f}%",
 "current_pnl": position.get("current_pnl", 0)
 })
 
 # Alert 2: Earnings date approaching but IV not elevated
 days_to_earnings = (
 datetime.fromisoformat(position["earnings_date"]) - datetime.now()
 ).days
 
 if days_to_earnings <= 5 and position.get("current_iv_front", 0) < position["entry_iv_front"] * 0.90:
 alerts.append({
 "type": "LOW_IV_WARNING",
 "symbol": position["symbol"],
 "severity": "MEDIUM",
 "message": "IV lower than expected near earnings",
 "days_to_earnings": days_to_earnings
 })
 
 return alerts
 
 def _check_emergency_conditions(self, total_position_pnl: float) -> List[Dict]:
 """Check for emergency stop conditions"""
 alerts = []
 
 # Emergency 1: Daily loss exceeds emergency threshold
 emergency_daily_loss = self.budget * self.emergency_daily_loss_pct
 
 if self.daily_pnl < -emergency_daily_loss:
 alerts.append({
 "type": "EMERGENCY_DAILY_LOSS",
 "severity": "CRITICAL",
 "message": f"Daily loss ${self.daily_pnl:,.2f} exceeds emergency threshold ${-emergency_daily_loss:,.2f}",
 "action": "EMERGENCY_STOP_TRIGGERED"
 })
 
 # Trigger emergency stop
 self.status = ModuleStatus.EMERGENCY_STOP
 logger.critical(f"EMERGENCY STOP: Daily loss ${self.daily_pnl:,.2f}")
 
 # Emergency 2: Total drawdown exceeds threshold
 emergency_drawdown = self.budget * self.emergency_drawdown_pct
 
 if self.total_pnl < -emergency_drawdown:
 alerts.append({
 "type": "EMERGENCY_DRAWDOWN",
 "severity": "CRITICAL",
 "message": f"Total drawdown ${self.total_pnl:,.2f} exceeds threshold ${-emergency_drawdown:,.2f}",
 "action": "EMERGENCY_STOP_TRIGGERED"
 })
 
 # Trigger emergency stop
 self.status = ModuleStatus.EMERGENCY_STOP
 logger.critical(f"EMERGENCY STOP: Drawdown ${self.total_pnl:,.2f}")
 
 return alerts
 
 def _calculate_symbol_exposure(self, symbol: str) -> float:
 """Calculate total exposure to a specific symbol"""
 exposure = 0.0
 
 for position in self.positions:
 if position["symbol"] == symbol:
 exposure += position["cost"]
 
 return exposure
 
 def _calculate_sector_exposure(self, sector: str) -> float:
 """Calculate total exposure to a specific sector"""
 exposure = 0.0
 
 for position in self.positions:
 if position.get("sector") == sector:
 exposure += position["cost"]
 
 return exposure
 
 async def pause_module(self, reason: str = "Manual pause"):
 """Pause module (stop new trades, keep monitoring existing)"""
 self.status = ModuleStatus.PAUSED
 logger.warning(f"Module paused: {reason}")
 
 async def resume_module(self):
 """Resume module operations"""
 if self.status == ModuleStatus.EMERGENCY_STOP:
 logger.error("Cannot resume from EMERGENCY_STOP, requires manual intervention")
 return False
 
 self.status = ModuleStatus.ACTIVE
 logger.info("Module resumed")
 return True
 
 async def emergency_stop(self, reason: str = "Manual emergency stop"):
 """
 Emergency stop - pause module and close all positions
 """
 self.status = ModuleStatus.EMERGENCY_STOP
 logger.critical(f"EMERGENCY STOP: {reason}")
 
 # Close all positions (would integrate with TradeStation here)
 for position in self.positions:
 logger.info(f"Closing position: {position['symbol']}")
 # await self._close_position(position)
 
 return {
 "status": "EMERGENCY_STOP",
 "reason": reason,
 "positions_closed": len(self.positions),
 "timestamp": datetime.now().isoformat()
 }
 
 def get_module_stats(self) -> Dict:
 """Get module statistics"""
 return {
 "mindfolio_id": self.mindfolio_id,
 "status": self.status.value,
 "budget": self.budget,
 "budget_used": self.budget_used,
 "budget_available": self.budget - self.budget_used,
 "budget_utilization_pct": (self.budget_used / self.budget * 100) if self.budget > 0 else 0,
 "daily_pnl": self.daily_pnl,
 "total_pnl": self.total_pnl,
 "total_pnl_pct": (self.total_pnl / self.budget * 100) if self.budget > 0 else 0,
 "positions_count": len(self.positions),
 "trades_count": len(self.trade_history),
 "max_risk_per_trade": self.max_risk_per_trade,
 "daily_loss_limit": self.daily_loss_limit,
 "autotrade": self.autotrade
 }
