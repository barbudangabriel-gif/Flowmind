"""
Options Calculator Engine
Black-Scholes implementation pentru FlowMind Options Module
Supports all Greeks calculations și multi-leg strategies
"""

import numpy as np
import math
from scipy.stats import norm
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OptionType(Enum):
 CALL = "call"
 PUT = "put"

class ActionType(Enum):
 BUY = "buy" 
 SELL = "sell"

@dataclass
class OptionLeg:
 """Single option leg configuration"""
 option_type: OptionType
 action: ActionType
 strike: float
 quantity: int
 premium: float = 0.0
 
@dataclass 
class StrategyConfig:
 """Complete strategy configuration"""
 name: str
 description: str
 legs: List[OptionLeg]
 stock_price: float
 risk_free_rate: float = 0.05 # 5% default
 volatility: float = 0.25 # 25% default
 days_to_expiry: int = 30 # 30 days default

@dataclass
class Greeks:
 """All Greeks for an option"""
 delta: float
 gamma: float 
 theta: float
 vega: float
 rho: float

@dataclass
class StrategyAnalysis:
 """Complete strategy analysis results"""
 max_profit: float
 max_loss: float
 breakeven_points: List[float]
 probability_of_profit: float
 strategy_greeks: Greeks
 price_array: List[float]
 pnl_array: List[float]

class BlackScholesCalculator:
 """Black-Scholes options pricing și Greeks calculations"""
 
 @staticmethod
 def calculate_option_price(
 stock_price: float,
 strike: float,
 time_to_expiry: float, # în years
 risk_free_rate: float,
 volatility: float,
 option_type: OptionType
 ) -> float:
 """Calculate Black-Scholes option price"""
 
 if time_to_expiry <= 0:
 # At expiration - intrinsic value only
 if option_type == OptionType.CALL:
 return max(stock_price - strike, 0)
 else:
 return max(strike - stock_price, 0)
 
 # Black-Scholes formula components
 d1 = (math.log(stock_price / strike) + 
 (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (
 volatility * math.sqrt(time_to_expiry))
 
 d2 = d1 - volatility * math.sqrt(time_to_expiry)
 
 if option_type == OptionType.CALL:
 price = (stock_price * norm.cdf(d1) - 
 strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
 else: # PUT
 price = (strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - 
 stock_price * norm.cdf(-d1))
 
 return price
 
 @staticmethod
 def calculate_greeks(
 stock_price: float,
 strike: float,
 time_to_expiry: float,
 risk_free_rate: float,
 volatility: float,
 option_type: OptionType
 ) -> Greeks:
 """Calculate all Greeks for an option"""
 
 if time_to_expiry <= 0:
 # At expiration - Greeks are zero except delta
 delta = 1.0 if (option_type == OptionType.CALL and stock_price > strike) else 0.0
 if option_type == OptionType.PUT:
 delta = -1.0 if stock_price < strike else 0.0
 return Greeks(delta=delta, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)
 
 # Calculate d1 și d2
 d1 = (math.log(stock_price / strike) + 
 (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (
 volatility * math.sqrt(time_to_expiry))
 
 d2 = d1 - volatility * math.sqrt(time_to_expiry)
 
 # Standard normal probability density function
 pdf_d1 = (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * d1**2)
 
 # Calculate Greeks
 if option_type == OptionType.CALL:
 delta = norm.cdf(d1)
 theta = ((-stock_price * pdf_d1 * volatility) / (2 * math.sqrt(time_to_expiry)) - 
 risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
 rho = strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2) / 100
 else: # PUT
 delta = norm.cdf(d1) - 1
 theta = ((-stock_price * pdf_d1 * volatility) / (2 * math.sqrt(time_to_expiry)) + 
 risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365
 rho = -strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) / 100
 
 # Gamma și Vega sunt same pentru calls și puts
 gamma = pdf_d1 / (stock_price * volatility * math.sqrt(time_to_expiry))
 vega = stock_price * pdf_d1 * math.sqrt(time_to_expiry) / 100
 
 return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)

class OptionsStrategyEngine:
 """Main engine pentru options strategy analysis"""
 
 def __init__(self):
 self.calculator = BlackScholesCalculator()
 
 def create_long_call_strategy(
 self,
 symbol: str,
 stock_price: float,
 strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Long Call strategy configuration"""
 
 # Calculate premium using Black-Scholes
 time_to_expiry = days_to_expiry / 365.0
 premium = self.calculator.calculate_option_price(
 stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 
 leg = OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.BUY,
 strike=strike,
 quantity=1,
 premium=premium
 )
 
 return StrategyConfig(
 name="Long Call",
 description=f"Bullish strategy - Buy {symbol} ${strike} Call expiring în {days_to_expiry} days",
 legs=[leg],
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_long_put_strategy(
 self,
 symbol: str,
 stock_price: float,
 strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Long Put strategy configuration"""
 
 # Calculate premium using Black-Scholes
 time_to_expiry = days_to_expiry / 365.0
 premium = self.calculator.calculate_option_price(
 stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 
 leg = OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.BUY,
 strike=strike,
 quantity=1,
 premium=premium
 )
 
 return StrategyConfig(
 name="Long Put",
 description=f"Bearish strategy - Buy {symbol} ${strike} Put expiring în {days_to_expiry} days",
 legs=[leg],
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_bull_call_spread_strategy(
 self,
 symbol: str,
 stock_price: float,
 long_strike: float,
 short_strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Bull Call Spread strategy configuration"""
 
 time_to_expiry = days_to_expiry / 365.0
 
 # Long call premium
 long_premium = self.calculator.calculate_option_price(
 stock_price, long_strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 
 # Short call premium 
 short_premium = self.calculator.calculate_option_price(
 stock_price, short_strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 
 legs = [
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.BUY,
 strike=long_strike,
 quantity=1,
 premium=long_premium
 ),
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.SELL,
 strike=short_strike,
 quantity=1,
 premium=short_premium
 )
 ]
 
 return StrategyConfig(
 name="Bull Call Spread",
 description=f"Bullish strategy - Buy {symbol} ${long_strike}C, Sell ${short_strike}C expiring în {days_to_expiry} days",
 legs=legs,
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_bear_put_spread_strategy(
 self,
 symbol: str,
 stock_price: float,
 long_strike: float,
 short_strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Bear Put Spread strategy configuration"""
 
 time_to_expiry = days_to_expiry / 365.0
 
 # Long put premium (higher strike)
 long_premium = self.calculator.calculate_option_price(
 stock_price, long_strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 
 # Short put premium (lower strike)
 short_premium = self.calculator.calculate_option_price(
 stock_price, short_strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 
 legs = [
 OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.BUY,
 strike=long_strike,
 quantity=1,
 premium=long_premium
 ),
 OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.SELL,
 strike=short_strike,
 quantity=1,
 premium=short_premium
 )
 ]
 
 return StrategyConfig(
 name="Bear Put Spread",
 description=f"Bearish strategy - Buy {symbol} ${long_strike}P, Sell ${short_strike}P expiring în {days_to_expiry} days",
 legs=legs,
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_iron_condor_strategy(
 self,
 symbol: str,
 stock_price: float,
 put_short_strike: float,
 put_long_strike: float,
 call_short_strike: float,
 call_long_strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Iron Condor strategy configuration"""
 
 time_to_expiry = days_to_expiry / 365.0
 
 # Calculate premiums for all four legs
 put_long_premium = self.calculator.calculate_option_price(
 stock_price, put_long_strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 put_short_premium = self.calculator.calculate_option_price(
 stock_price, put_short_strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 call_short_premium = self.calculator.calculate_option_price(
 stock_price, call_short_strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 call_long_premium = self.calculator.calculate_option_price(
 stock_price, call_long_strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 
 legs = [
 # Put spread (bear put spread - sell lower, buy higher)
 OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.BUY,
 strike=put_long_strike,
 quantity=1,
 premium=put_long_premium
 ),
 OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.SELL,
 strike=put_short_strike,
 quantity=1,
 premium=put_short_premium
 ),
 # Call spread (bear call spread - sell lower, buy higher)
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.SELL,
 strike=call_short_strike,
 quantity=1,
 premium=call_short_premium
 ),
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.BUY,
 strike=call_long_strike,
 quantity=1,
 premium=call_long_premium
 )
 ]
 
 return StrategyConfig(
 name="Iron Condor",
 description=f"Neutral strategy - {symbol} ${put_long_strike}P/{put_short_strike}P/{call_short_strike}C/{call_long_strike}C",
 legs=legs,
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_long_straddle_strategy(
 self,
 symbol: str,
 stock_price: float,
 strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Long Straddle strategy configuration"""
 
 time_to_expiry = days_to_expiry / 365.0
 
 # Calculate premiums for both call and put at same strike
 call_premium = self.calculator.calculate_option_price(
 stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 put_premium = self.calculator.calculate_option_price(
 stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.PUT
 )
 
 legs = [
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.BUY,
 strike=strike,
 quantity=1,
 premium=call_premium
 ),
 OptionLeg(
 option_type=OptionType.PUT,
 action=ActionType.BUY,
 strike=strike,
 quantity=1,
 premium=put_premium
 )
 ]
 
 return StrategyConfig(
 name="Long Straddle",
 description=f"Volatility strategy - Buy {symbol} ${strike}C and ${strike}P expiring în {days_to_expiry} days",
 legs=legs,
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def create_covered_call_strategy(
 self,
 symbol: str,
 stock_price: float,
 call_strike: float,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create Covered Call strategy configuration"""
 
 time_to_expiry = days_to_expiry / 365.0
 
 # Calculate call premium
 call_premium = self.calculator.calculate_option_price(
 stock_price, call_strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
 )
 
 # Note: This assumes the user already owns 100 shares
 # The "stock leg" is not included in the legs array as it's assumed to be owned
 legs = [
 OptionLeg(
 option_type=OptionType.CALL,
 action=ActionType.SELL,
 strike=call_strike,
 quantity=1,
 premium=call_premium
 )
 ]
 
 return StrategyConfig(
 name="Covered Call",
 description=f"Income strategy - Own 100 shares {symbol}, Sell ${call_strike}C expiring în {days_to_expiry} days",
 legs=legs,
 stock_price=stock_price,
 risk_free_rate=risk_free_rate,
 volatility=volatility,
 days_to_expiry=days_to_expiry
 )
 
 def analyze_strategy(self, strategy: StrategyConfig) -> StrategyAnalysis:
 """Analyze complete strategy - P&L, Greeks, breakevens"""
 
 time_to_expiry = strategy.days_to_expiry / 365.0
 
 # Generate price range pentru P&L chart (±50% from current price)
 min_price = strategy.stock_price * 0.5
 max_price = strategy.stock_price * 1.5
 price_array = np.linspace(min_price, max_price, 100).tolist()
 
 pnl_array = []
 total_greeks = Greeks(0, 0, 0, 0, 0)
 
 # Calculate P&L pentru each price point
 for price in price_array:
 strategy_pnl = 0
 
 for leg in strategy.legs:
 # Calculate option value at this price
 option_value = self.calculator.calculate_option_price(
 price, leg.strike, time_to_expiry,
 strategy.risk_free_rate, strategy.volatility, leg.option_type
 )
 
 # Calculate P&L pentru this leg
 if leg.action == ActionType.BUY:
 leg_pnl = (option_value - leg.premium) * leg.quantity * 100 # $100 per contract
 else: # SELL
 leg_pnl = (leg.premium - option_value) * leg.quantity * 100
 
 strategy_pnl += leg_pnl
 
 pnl_array.append(strategy_pnl)
 
 # Calculate strategy Greeks at current stock price
 for leg in strategy.legs:
 leg_greeks = self.calculator.calculate_greeks(
 strategy.stock_price, leg.strike, time_to_expiry,
 strategy.risk_free_rate, strategy.volatility, leg.option_type
 )
 
 multiplier = leg.quantity if leg.action == ActionType.BUY else -leg.quantity
 total_greeks.delta += leg_greeks.delta * multiplier
 total_greeks.gamma += leg_greeks.gamma * multiplier
 total_greeks.theta += leg_greeks.theta * multiplier
 total_greeks.vega += leg_greeks.vega * multiplier
 total_greeks.rho += leg_greeks.rho * multiplier
 
 # Calculate max profit/loss
 max_profit = max(pnl_array) if pnl_array else 0
 max_loss = min(pnl_array) if pnl_array else 0
 
 # Find breakeven points (zero crossings)
 breakeven_points = []
 for i in range(len(pnl_array) - 1):
 if (pnl_array[i] <= 0 <= pnl_array[i + 1]) or (pnl_array[i] >= 0 >= pnl_array[i + 1]):
 # Linear interpolation pentru exact breakeven
 if pnl_array[i + 1] != pnl_array[i]:
 breakeven = price_array[i] + (price_array[i + 1] - price_array[i]) * (
 -pnl_array[i] / (pnl_array[i + 1] - pnl_array[i])
 )
 breakeven_points.append(round(breakeven, 2))
 
 # Calculate probability of profit (simple approximation)
 profitable_prices = sum(1 for pnl in pnl_array if pnl > 0)
 probability_of_profit = profitable_prices / len(pnl_array) if pnl_array else 0
 
 return StrategyAnalysis(
 max_profit=max_profit,
 max_loss=max_loss,
 breakeven_points=breakeven_points,
 probability_of_profit=probability_of_profit,
 strategy_greeks=total_greeks,
 price_array=price_array,
 pnl_array=pnl_array
 )
 
 def get_available_strategies(self) -> Dict[str, Dict]:
 """Get all available strategies organized by proficiency"""
 return {
 "novice": {
 "basic": ["Long Call", "Long Put"],
 "income": ["Covered Call", "Cash-Secured Put", "Protective Put"]
 },
 "intermediate": {
 "credit_spreads": ["Bull Put Spread", "Bear Call Spread"],
 "debit_spreads": ["Bull Call Spread", "Bear Put Spread"],
 "neutral": ["Iron Butterfly", "Iron Condor", "Long Put Butterfly", "Long Call Butterfly"],
 "directional": ["Long Straddle", "Long Strangle", "Short Put Butterfly", "Short Call Butterfly"]
 },
 "advanced": {
 "naked": ["Short Put", "Short Call"],
 "income": ["Covered Short Straddle", "Covered Short Strangle"],
 "neutral": ["Short Straddle", "Short Strangle"]
 },
 "expert": {
 "synthetic": ["Long Synthetic Future", "Short Synthetic Future"],
 "arbitrage": ["Long Combo", "Short Combo"],
 "complex": ["Strip", "Strap", "Double Diagonal"]
 }
 }
 
 def create_strategy_by_name(
 self,
 strategy_name: str,
 symbol: str,
 stock_price: float,
 parameters: Dict,
 days_to_expiry: int = 30,
 volatility: float = 0.25,
 risk_free_rate: float = 0.05
 ) -> StrategyConfig:
 """Create strategy by name with parameters"""
 
 if strategy_name == "Long Call":
 return self.create_long_call_strategy(
 symbol, stock_price, parameters.get('strike', stock_price),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Long Put":
 return self.create_long_put_strategy(
 symbol, stock_price, parameters.get('strike', stock_price),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Bull Call Spread":
 return self.create_bull_call_spread_strategy(
 symbol, stock_price, 
 parameters.get('long_strike', stock_price - 5),
 parameters.get('short_strike', stock_price + 5),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Bear Put Spread":
 return self.create_bear_put_spread_strategy(
 symbol, stock_price,
 parameters.get('long_strike', stock_price + 5),
 parameters.get('short_strike', stock_price - 5),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Iron Condor":
 return self.create_iron_condor_strategy(
 symbol, stock_price,
 parameters.get('put_short_strike', stock_price - 10),
 parameters.get('put_long_strike', stock_price - 20),
 parameters.get('call_short_strike', stock_price + 10),
 parameters.get('call_long_strike', stock_price + 20),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Long Straddle":
 return self.create_long_straddle_strategy(
 symbol, stock_price, parameters.get('strike', stock_price),
 days_to_expiry, volatility, risk_free_rate
 )
 elif strategy_name == "Covered Call":
 return self.create_covered_call_strategy(
 symbol, stock_price, parameters.get('call_strike', stock_price + 5),
 days_to_expiry, volatility, risk_free_rate
 )
 else:
 raise ValueError(f"Strategy '{strategy_name}' not implemented yet")

# Singleton instance
options_engine = OptionsStrategyEngine()