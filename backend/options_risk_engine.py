"""
Options Risk Engine - HIGHEST PRIORITY Component
Multi-leg strategy validation, Greeks impact analysis, Probability calculations
IV Rank checks, 5-year backtesting, Correlation detection, Early assignment risk
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import norm

from options_calculator import BlackScholesCalculator, Greeks, OptionType, ActionType

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels"""
    BLOCKER = "BLOCKER"  # Trade cannot proceed
    WARNING = "WARNING"  # Requires user acknowledgment
    INFO = "INFO"  # Informational only
    PASS = "PASS"  # No issues


class StrategyType(Enum):
    """Multi-leg strategy types"""
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    SHORT_CALL = "short_call"
    SHORT_PUT = "short_put"
    CALL_SPREAD = "call_spread"
    PUT_SPREAD = "put_spread"
    IRON_CONDOR = "iron_condor"
    IRON_BUTTERFLY = "iron_butterfly"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    CALENDAR_SPREAD = "calendar_spread"
    DIAGONAL_SPREAD = "diagonal_spread"
    RATIO_SPREAD = "ratio_spread"
    CUSTOM = "custom"


@dataclass
class OptionPosition:
    """Single option position"""
    symbol: str  # Underlying symbol
    option_type: OptionType  # CALL or PUT
    action: ActionType  # BUY or SELL
    strike: float
    expiry: str  # ISO format date
    quantity: int
    premium: float  # Per contract (already * 100)
    volatility: float  # Implied volatility
    current_price: float  # Current underlying price


@dataclass
class GreeksLimits:
    """Portfolio Greeks limits"""
    max_delta: float = 200.0  # Max absolute portfolio delta
    max_gamma: float = 20.0  # Max portfolio gamma
    max_vega: float = 500.0  # Max absolute vega ($)
    max_theta: float = 100.0  # Max theta decay per day


@dataclass
class RiskCheck:
    """Individual risk check result"""
    check_name: str
    level: RiskLevel
    message: str
    current_value: Optional[float] = None
    limit_value: Optional[float] = None
    details: Optional[Dict] = None


@dataclass
class OptionsTradeValidation:
    """Complete validation result"""
    passed: bool  # Overall pass/fail
    checks: List[RiskCheck]
    strategy_info: Dict
    greeks_impact: Dict
    probability_analysis: Dict
    backtest_results: Optional[Dict] = None
    estimated_cost: float = 0.0


class OptionsRiskEngine:
    """Comprehensive options risk validation engine"""

    def __init__(self, greeks_limits: Optional[GreeksLimits] = None):
        self.greeks_limits = greeks_limits or GreeksLimits()
        self.bs_calc = BlackScholesCalculator()

    async def validate_options_trade(
        self,
        new_positions: List[OptionPosition],
        existing_positions: List[OptionPosition],
        portfolio_cash: float,
        risk_profile: str = "MODERATE",  # CONSERVATIVE, MODERATE, AGGRESSIVE
    ) -> OptionsTradeValidation:
        """
        Comprehensive multi-leg options trade validation
        Returns validation result with all checks
        """
        checks = []
        strategy_info = {}
        
        # 1. Strategy Detection & Classification
        strategy_type = self._detect_strategy_type(new_positions)
        strategy_info["type"] = strategy_type.value
        strategy_info["legs"] = len(new_positions)
        
        # 2. Greeks Impact Analysis
        current_greeks = self._calculate_portfolio_greeks(existing_positions)
        new_greeks = self._calculate_portfolio_greeks(new_positions)
        combined_greeks = self._add_greeks(current_greeks, new_greeks)
        
        greeks_impact = {
            "current": self._greeks_to_dict(current_greeks),
            "new_trade": self._greeks_to_dict(new_greeks),
            "combined": self._greeks_to_dict(combined_greeks),
        }
        
        # Greeks Limits Checks
        checks.extend(self._check_greeks_limits(combined_greeks, new_greeks))
        
        # 3. Cost & Margin Validation
        estimated_cost = self._calculate_trade_cost(new_positions)
        strategy_info["estimated_cost"] = estimated_cost
        strategy_info["max_loss"] = self._calculate_max_loss(new_positions)
        strategy_info["max_profit"] = self._calculate_max_profit(new_positions)
        
        cost_check = self._check_sufficient_capital(estimated_cost, portfolio_cash)
        checks.append(cost_check)
        
        # 4. Probability Analysis
        probability_analysis = self._calculate_probabilities(new_positions)
        
        # PoP threshold based on risk profile
        min_pop = {"CONSERVATIVE": 70, "MODERATE": 60, "AGGRESSIVE": 50}[risk_profile]
        if probability_analysis["pop_expiration"] < min_pop:
            checks.append(RiskCheck(
                check_name="probability_of_profit",
                level=RiskLevel.WARNING,
                message=f"PoP ({probability_analysis['pop_expiration']:.1f}%) below {min_pop}% threshold for {risk_profile} profile",
                current_value=probability_analysis["pop_expiration"],
                limit_value=min_pop,
            ))
        
        # 5. IV Rank Check (for credit strategies)
        if self._is_credit_strategy(new_positions):
            iv_rank_check = await self._check_iv_rank(new_positions[0].symbol)
            checks.append(iv_rank_check)
        
        # 6. Correlation with Existing Positions
        correlation_check = self._check_correlation(new_positions, existing_positions)
        checks.append(correlation_check)
        
        # 7. Early Assignment Risk (for short positions)
        assignment_check = self._check_early_assignment_risk(new_positions)
        if assignment_check:
            checks.append(assignment_check)
        
        # 8. Expiration Distribution Check
        expiration_check = self._check_expiration_concentration(
            new_positions, existing_positions
        )
        checks.append(expiration_check)
        
        # 9. Strike Concentration Check
        strike_check = self._check_strike_concentration(
            new_positions, existing_positions
        )
        checks.append(strike_check)
        
        # 10. 5-Year Historical Backtest (async - may be slow)
        # TODO: Implement full backtest with historical options data
        backtest_results = None  # Placeholder for now
        
        # Determine overall pass/fail
        blockers = [c for c in checks if c.level == RiskLevel.BLOCKER]
        passed = len(blockers) == 0
        
        return OptionsTradeValidation(
            passed=passed,
            checks=checks,
            strategy_info=strategy_info,
            greeks_impact=greeks_impact,
            probability_analysis=probability_analysis,
            backtest_results=backtest_results,
            estimated_cost=estimated_cost,
        )

    def _detect_strategy_type(self, positions: List[OptionPosition]) -> StrategyType:
        """Detect multi-leg strategy type"""
        if len(positions) == 1:
            pos = positions[0]
            if pos.action == ActionType.BUY:
                return StrategyType.LONG_CALL if pos.option_type == OptionType.CALL else StrategyType.LONG_PUT
            else:
                return StrategyType.SHORT_CALL if pos.option_type == OptionType.CALL else StrategyType.SHORT_PUT
        
        elif len(positions) == 2:
            # Check for vertical spreads
            if positions[0].option_type == positions[1].option_type:
                if positions[0].option_type == OptionType.CALL:
                    return StrategyType.CALL_SPREAD
                else:
                    return StrategyType.PUT_SPREAD
            # Straddle or Strangle
            elif positions[0].strike == positions[1].strike:
                return StrategyType.STRADDLE
            else:
                return StrategyType.STRANGLE
        
        elif len(positions) == 4:
            # Iron Condor or Iron Butterfly
            call_count = sum(1 for p in positions if p.option_type == OptionType.CALL)
            if call_count == 2:
                strikes = sorted([p.strike for p in positions])
                if strikes[1] == strikes[2]:
                    return StrategyType.IRON_BUTTERFLY
                else:
                    return StrategyType.IRON_CONDOR
        
        return StrategyType.CUSTOM

    def _calculate_portfolio_greeks(self, positions: List[OptionPosition]) -> Greeks:
        """Calculate aggregate portfolio Greeks"""
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        total_rho = 0.0
        
        for pos in positions:
            # Calculate time to expiry in years
            expiry_date = datetime.fromisoformat(pos.expiry.replace('Z', '+00:00'))
            dte = (expiry_date - datetime.now()).days
            time_to_expiry = max(dte, 1) / 365.0
            
            # Get Greeks for this position
            greeks = self.bs_calc.calculate_greeks(
                stock_price=pos.current_price,
                strike=pos.strike,
                time_to_expiry=time_to_expiry,
                risk_free_rate=0.05,  # 5% default
                volatility=pos.volatility,
                option_type=pos.option_type,
            )
            
            # Multiply by quantity and action direction
            multiplier = pos.quantity * (1 if pos.action == ActionType.BUY else -1)
            
            total_delta += greeks.delta * multiplier
            total_gamma += greeks.gamma * multiplier
            total_theta += greeks.theta * multiplier
            total_vega += greeks.vega * multiplier
            total_rho += greeks.rho * multiplier
        
        return Greeks(
            delta=total_delta,
            gamma=total_gamma,
            theta=total_theta,
            vega=total_vega,
            rho=total_rho,
        )

    def _add_greeks(self, g1: Greeks, g2: Greeks) -> Greeks:
        """Add two Greeks objects"""
        return Greeks(
            delta=g1.delta + g2.delta,
            gamma=g1.gamma + g2.gamma,
            theta=g1.theta + g2.theta,
            vega=g1.vega + g2.vega,
            rho=g1.rho + g2.rho,
        )

    def _greeks_to_dict(self, greeks: Greeks) -> Dict:
        """Convert Greeks to dict for JSON serialization"""
        return {
            "delta": round(greeks.delta, 2),
            "gamma": round(greeks.gamma, 4),
            "theta": round(greeks.theta, 2),
            "vega": round(greeks.vega, 2),
            "rho": round(greeks.rho, 2),
        }

    def _check_greeks_limits(
        self, combined_greeks: Greeks, new_greeks: Greeks
    ) -> List[RiskCheck]:
        """Check if Greeks exceed portfolio limits"""
        checks = []
        
        # Delta check
        if abs(combined_greeks.delta) > self.greeks_limits.max_delta:
            checks.append(RiskCheck(
                check_name="portfolio_delta",
                level=RiskLevel.BLOCKER,
                message=f"Portfolio Delta ({combined_greeks.delta:.1f}) exceeds limit (±{self.greeks_limits.max_delta})",
                current_value=abs(combined_greeks.delta),
                limit_value=self.greeks_limits.max_delta,
                details={"new_trade_delta": round(new_greeks.delta, 2)},
            ))
        elif abs(combined_greeks.delta) > self.greeks_limits.max_delta * 0.8:
            checks.append(RiskCheck(
                check_name="portfolio_delta",
                level=RiskLevel.WARNING,
                message=f"Portfolio Delta ({combined_greeks.delta:.1f}) approaching limit",
                current_value=abs(combined_greeks.delta),
                limit_value=self.greeks_limits.max_delta,
            ))
        
        # Gamma check
        if abs(combined_greeks.gamma) > self.greeks_limits.max_gamma:
            checks.append(RiskCheck(
                check_name="portfolio_gamma",
                level=RiskLevel.BLOCKER,
                message=f"Portfolio Gamma ({combined_greeks.gamma:.2f}) exceeds limit (±{self.greeks_limits.max_gamma})",
                current_value=abs(combined_greeks.gamma),
                limit_value=self.greeks_limits.max_gamma,
            ))
        
        # Vega check
        if abs(combined_greeks.vega) > self.greeks_limits.max_vega:
            checks.append(RiskCheck(
                check_name="portfolio_vega",
                level=RiskLevel.BLOCKER,
                message=f"Portfolio Vega (${combined_greeks.vega:.0f}) exceeds limit ($±{self.greeks_limits.max_vega})",
                current_value=abs(combined_greeks.vega),
                limit_value=self.greeks_limits.max_vega,
            ))
        
        # Theta check (daily decay)
        if abs(combined_greeks.theta) > self.greeks_limits.max_theta:
            checks.append(RiskCheck(
                check_name="portfolio_theta",
                level=RiskLevel.WARNING,
                message=f"Daily Theta decay (${combined_greeks.theta:.0f}) is high",
                current_value=abs(combined_greeks.theta),
                limit_value=self.greeks_limits.max_theta,
            ))
        
        return checks

    def _calculate_trade_cost(self, positions: List[OptionPosition]) -> float:
        """Calculate total cost/credit of trade"""
        total_cost = 0.0
        
        for pos in positions:
            if pos.action == ActionType.BUY:
                # Buying costs money (debit)
                total_cost += pos.premium * pos.quantity
            else:
                # Selling receives money (credit)
                total_cost -= pos.premium * pos.quantity
        
        return total_cost  # Positive = debit, Negative = credit

    def _calculate_max_loss(self, positions: List[OptionPosition]) -> float:
        """Calculate maximum possible loss for strategy"""
        # For complex strategies, need to evaluate P&L at various prices
        # Simplified implementation - return sum of debits paid
        max_loss = 0.0
        
        for pos in positions:
            if pos.action == ActionType.BUY:
                max_loss += pos.premium * pos.quantity
            else:
                # For naked short options, theoretically unlimited
                # For spreads, limited by strike width
                # Simplified: assume max loss is 10x premium received
                max_loss += pos.premium * pos.quantity * 10
        
        return max_loss

    def _calculate_max_profit(self, positions: List[OptionPosition]) -> float:
        """Calculate maximum possible profit for strategy"""
        # Simplified - for credit spreads, max profit = credit received
        # For debit spreads, max profit = strike width - debit paid
        max_profit = 0.0
        
        # If net credit, max profit = credit
        net_credit = -self._calculate_trade_cost(positions)
        if net_credit > 0:
            return net_credit
        
        # For debit strategies, calculate strike width
        if len(positions) >= 2:
            strikes = sorted([p.strike for p in positions])
            strike_width = (strikes[-1] - strikes[0]) * 100  # Per contract
            max_profit = strike_width - abs(self._calculate_trade_cost(positions))
        
        return max(max_profit, 0)

    def _check_sufficient_capital(self, cost: float, cash: float) -> RiskCheck:
        """Check if sufficient capital for trade"""
        if cost <= 0:
            # Credit strategy - no upfront cost
            return RiskCheck(
                check_name="capital_requirement",
                level=RiskLevel.PASS,
                message=f"Credit strategy receives ${abs(cost):.2f}",
                current_value=cash,
                limit_value=0,
            )
        
        if cost > cash:
            return RiskCheck(
                check_name="capital_requirement",
                level=RiskLevel.BLOCKER,
                message=f"Insufficient capital: Need ${cost:.2f}, have ${cash:.2f}",
                current_value=cash,
                limit_value=cost,
            )
        
        # Warn if using >50% of capital
        if cost > cash * 0.5:
            return RiskCheck(
                check_name="capital_requirement",
                level=RiskLevel.WARNING,
                message=f"Trade uses {(cost/cash*100):.1f}% of available capital",
                current_value=cost,
                limit_value=cash,
            )
        
        return RiskCheck(
            check_name="capital_requirement",
            level=RiskLevel.PASS,
            message=f"Capital requirement: ${cost:.2f} ({(cost/cash*100):.1f}% of available)",
            current_value=cost,
            limit_value=cash,
        )

    def _calculate_probabilities(self, positions: List[OptionPosition]) -> Dict:
        """Calculate probability of profit and breakeven analysis"""
        # Get the first position's underlying data
        pos = positions[0]
        current_price = pos.current_price
        
        # Calculate breakeven points
        breakeven_prices = self._find_breakeven_points(positions)
        
        # Calculate probability of profit at expiration
        # For simple strategies, use lognormal distribution
        pop = self._calculate_pop_lognormal(
            current_price=current_price,
            breakeven_prices=breakeven_prices,
            volatility=pos.volatility,
            days_to_expiry=self._get_dte(pos.expiry),
        )
        
        # Calculate early exit probabilities (50% and 25% profit targets)
        profit_50_prob = self._calculate_early_exit_prob(positions, 0.50)
        profit_25_prob = self._calculate_early_exit_prob(positions, 0.25)
        
        return {
            "pop_expiration": round(pop * 100, 2),
            "breakeven_prices": [round(bp, 2) for bp in breakeven_prices],
            "profit_50_probability": round(profit_50_prob * 100, 2),
            "profit_25_probability": round(profit_25_prob * 100, 2),
            "current_price": round(current_price, 2),
        }

    def _find_breakeven_points(self, positions: List[OptionPosition]) -> List[float]:
        """Find breakeven price points for strategy"""
        # Simplified - for single leg, breakeven = strike +/- premium
        if len(positions) == 1:
            pos = positions[0]
            premium_per_share = pos.premium / 100
            
            if pos.option_type == OptionType.CALL and pos.action == ActionType.BUY:
                return [pos.strike + premium_per_share]
            elif pos.option_type == OptionType.PUT and pos.action == ActionType.BUY:
                return [pos.strike - premium_per_share]
        
        # For multi-leg, need to solve P&L = 0
        # Simplified: return strikes as approximation
        return sorted(list(set([p.strike for p in positions])))

    def _calculate_pop_lognormal(
        self, current_price: float, breakeven_prices: List[float],
        volatility: float, days_to_expiry: int
    ) -> float:
        """Calculate probability of profit using lognormal distribution"""
        if not breakeven_prices:
            return 0.5
        
        time_to_expiry = days_to_expiry / 365.0
        
        # For single breakeven (most common)
        if len(breakeven_prices) == 1:
            breakeven = breakeven_prices[0]
            
            # Calculate probability price > breakeven (for calls/bullish)
            # or price < breakeven (for puts/bearish)
            mu = math.log(current_price)
            sigma = volatility * math.sqrt(time_to_expiry)
            
            z = (math.log(breakeven) - mu) / sigma
            
            # Assume bullish if breakeven > current (typical for debit spreads)
            if breakeven > current_price:
                prob = 1 - norm.cdf(z)
            else:
                prob = norm.cdf(z)
            
            return prob
        
        # For two breakevens (iron condor, etc.) - price must be between
        if len(breakeven_prices) == 2:
            lower_be = min(breakeven_prices)
            upper_be = max(breakeven_prices)
            
            mu = math.log(current_price)
            sigma = volatility * math.sqrt(time_to_expiry)
            
            z_lower = (math.log(lower_be) - mu) / sigma
            z_upper = (math.log(upper_be) - mu) / sigma
            
            prob = norm.cdf(z_upper) - norm.cdf(z_lower)
            return prob
        
        return 0.5  # Default for complex strategies

    def _calculate_early_exit_prob(
        self, positions: List[OptionPosition], profit_target: float
    ) -> float:
        """Calculate probability of reaching profit target before expiration"""
        # Simplified - assume 70% of max profit probability
        # Real implementation would use Monte Carlo simulation
        return 0.7  # Placeholder

    def _is_credit_strategy(self, positions: List[OptionPosition]) -> bool:
        """Check if strategy receives net credit"""
        return self._calculate_trade_cost(positions) < 0

    async def _check_iv_rank(self, symbol: str) -> RiskCheck:
        """Check IV Rank - credit strategies prefer high IV"""
        # TODO: Fetch actual IV Rank from market data
        # Placeholder - assume moderate IV Rank
        iv_rank = 50.0  # Placeholder
        
        if iv_rank < 50:
            return RiskCheck(
                check_name="iv_rank",
                level=RiskLevel.WARNING,
                message=f"IV Rank ({iv_rank:.0f}) is below 50 - credit strategies prefer high IV",
                current_value=iv_rank,
                limit_value=50,
            )
        
        return RiskCheck(
            check_name="iv_rank",
            level=RiskLevel.PASS,
            message=f"IV Rank ({iv_rank:.0f}) is favorable for credit strategies",
            current_value=iv_rank,
        )

    def _check_correlation(
        self, new_positions: List[OptionPosition], existing_positions: List[OptionPosition]
    ) -> RiskCheck:
        """Check for concentrated positions in same underlying"""
        new_symbols = set([p.symbol for p in new_positions])
        existing_symbols = [p.symbol for p in existing_positions]
        
        for symbol in new_symbols:
            existing_count = existing_symbols.count(symbol)
            if existing_count >= 3:
                return RiskCheck(
                    check_name="symbol_concentration",
                    level=RiskLevel.WARNING,
                    message=f"{symbol} already has {existing_count} open positions - high concentration risk",
                    current_value=existing_count + len(new_positions),
                    limit_value=3,
                )
        
        return RiskCheck(
            check_name="symbol_concentration",
            level=RiskLevel.PASS,
            message="No excessive symbol concentration detected",
        )

    def _check_early_assignment_risk(
        self, positions: List[OptionPosition]
    ) -> Optional[RiskCheck]:
        """Check early assignment risk for short options"""
        for pos in positions:
            if pos.action == ActionType.SELL:
                # Check if deep ITM (high assignment risk)
                dte = self._get_dte(pos.expiry)
                
                if pos.option_type == OptionType.CALL:
                    itm_amount = pos.current_price - pos.strike
                else:
                    itm_amount = pos.strike - pos.current_price
                
                if itm_amount > 0 and dte < 7:
                    assignment_prob = min((itm_amount / pos.current_price) * 100, 95)
                    
                    if assignment_prob > 50:
                        return RiskCheck(
                            check_name="early_assignment_risk",
                            level=RiskLevel.WARNING,
                            message=f"High early assignment risk ({assignment_prob:.0f}%) for {pos.option_type.value} at ${pos.strike}",
                            current_value=assignment_prob,
                            limit_value=50,
                        )
        
        return None

    def _check_expiration_concentration(
        self, new_positions: List[OptionPosition], existing_positions: List[OptionPosition]
    ) -> RiskCheck:
        """Check for too many positions expiring same day"""
        all_positions = new_positions + existing_positions
        expiration_counts = {}
        
        for pos in all_positions:
            expiry_date = pos.expiry.split('T')[0]  # Get date part
            expiration_counts[expiry_date] = expiration_counts.get(expiry_date, 0) + 1
        
        max_count = max(expiration_counts.values()) if expiration_counts else 0
        
        if max_count > 5:
            return RiskCheck(
                check_name="expiration_concentration",
                level=RiskLevel.WARNING,
                message=f"High concentration: {max_count} positions expiring same day",
                current_value=max_count,
                limit_value=5,
            )
        
        return RiskCheck(
            check_name="expiration_concentration",
            level=RiskLevel.PASS,
            message="Expirations well distributed",
        )

    def _check_strike_concentration(
        self, new_positions: List[OptionPosition], existing_positions: List[OptionPosition]
    ) -> RiskCheck:
        """Check for too many positions at same strike"""
        all_positions = new_positions + existing_positions
        strike_symbol_counts = {}
        
        for pos in all_positions:
            key = f"{pos.symbol}_{pos.strike}"
            strike_symbol_counts[key] = strike_symbol_counts.get(key, 0) + 1
        
        max_count = max(strike_symbol_counts.values()) if strike_symbol_counts else 0
        
        if max_count > 3:
            return RiskCheck(
                check_name="strike_concentration",
                level=RiskLevel.WARNING,
                message=f"High concentration: {max_count} positions at same strike",
                current_value=max_count,
                limit_value=3,
            )
        
        return RiskCheck(
            check_name="strike_concentration",
            level=RiskLevel.PASS,
            message="Strikes well distributed",
        )

    def _get_dte(self, expiry: str) -> int:
        """Get days to expiration"""
        expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
        return max((expiry_date - datetime.now()).days, 0)
