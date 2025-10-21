"""
Expert Options Trading System with Machine Learning
Implements 3 expert strategies with auto-optimization and learning capabilities
"""

import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    WHEEL = "wheel"
    IRON_CONDOR = "iron_condor"
    VOLATILITY_PLAY = "volatility_play"


class TradeStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"
    ASSIGNED = "assigned"


@dataclass
class OptionLeg:
    symbol: str
    option_type: str  # 'call' or 'put'
    strike: float
    expiration: str
    action: str  # 'buy' or 'sell'
    quantity: int
    premium: float
    iv: float
    delta: float
    gamma: float
    theta: float
    vega: float


@dataclass
class ExpertTrade:
    id: str
    strategy_type: StrategyType
    underlying: str
    legs: List[OptionLeg]
    entry_date: datetime
    exit_date: Optional[datetime]
    status: TradeStatus
    entry_iv: float
    exit_iv: Optional[float]
    max_profit: float
    max_loss: float
    current_pnl: float
    target_profit: float
    stop_loss: float
    parameters: Dict[str, Any]
    learning_score: float = 0.0


class ExpertOptionsSystem:
    """
    Expert Options Trading System with Machine Learning Capabilities
    """

    def __init__(self):
        self.trade_history: List[ExpertTrade] = []
        self.active_trades: List[ExpertTrade] = []
        self.strategy_performance: Dict[StrategyType, Dict] = {}
        self.learning_parameters: Dict[StrategyType, Dict] = {}
        self.market_conditions: Dict[str, Any] = {}

        # Initialize learning parameters for each strategy
        self._initialize_learning_parameters()

    def _initialize_learning_parameters(self):
        """Initialize optimal parameters for each strategy based on research"""

        self.learning_parameters[StrategyType.WHEEL] = {
            "put_delta_target": 0.30,  # Start conservative
            "call_delta_target": 0.30,
            "min_premium_pct": 1.0,  # 1% of stock price minimum
            "max_dte": 45,  # Days to expiration
            "iv_percentile_min": 25,  # Only trade when IV > 25th percentile
            "profit_target_pct": 50,  # Take profit at 50% of premium
            "adjustment_triggers": {"delta_breach": 0.50, "days_to_expiration": 21},
            "learning_weights": {
                "win_rate": 0.4,
                "profit_factor": 0.3,
                "sharpe_ratio": 0.3,
            },
        }

        self.learning_parameters[StrategyType.IRON_CONDOR] = {
            "wing_width": 10,  # Strike spacing
            "target_delta": 0.16,  # Delta for short strikes
            "min_credit": 2.0,  # Minimum credit to receive
            "max_dte": 30,
            "profit_target_pct": 25,  # Take profit at 25% of credit
            "loss_limit_pct": 200,  # Stop loss at -200% of credit
            "iv_rank_min": 30,  # Only trade high IV
            "manage_at_dte": 7,  # Manage positions at 7 DTE
            "learning_weights": {
                "win_rate": 0.5,
                "max_drawdown": 0.3,
                "consistency": 0.2,
            },
        }

        self.learning_parameters[StrategyType.VOLATILITY_PLAY] = {
            "straddle_delta": 0.50,  # ATM straddles
            "strangle_delta": 0.25,  # OTM strangles
            "iv_expansion_threshold": 20,  # IV percentile for entry
            "profit_target_pct": 100,  # 100% profit target
            "loss_limit_pct": 50,  # 50% loss limit
            "max_dte": 14,  # Short-term plays
            "earnings_buffer_days": 2,  # Days before earnings
            "vega_threshold": 0.10,  # Minimum vega per contract
            "learning_weights": {
                "profit_factor": 0.5,
                "volatility_timing": 0.3,
                "risk_adjusted_return": 0.2,
            },
        }

    async def analyze_market_conditions(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze current market conditions for optimal strategy selection
        """
        try:
            # Mock market analysis - in production, integrate with real data
            conditions = {
                "symbol": symbol,
                "current_price": 450.0,  # Mock price
                "iv_percentile": np.random.uniform(20, 80),
                "iv_rank": np.random.uniform(0, 100),
                "hv_30": np.random.uniform(15, 45),
                "trend": np.random.choice(["bullish", "bearish", "neutral"]),
                "support": 440.0,
                "resistance": 460.0,
                "days_to_earnings": np.random.randint(0, 90),
                "volume_ratio": np.random.uniform(0.8, 2.0),
                "options_volume": np.random.randint(1000, 10000),
            }

            # Calculate optimal strategy based on conditions
            conditions["optimal_strategy"] = self._determine_optimal_strategy(
                conditions
            )

            return conditions

        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return {}

    def _determine_optimal_strategy(self, conditions: Dict[str, Any]) -> str:
        """
        Determine optimal strategy based on market conditions using ML
        """
        iv_percentile = conditions.get("iv_percentile", 50)
        trend = conditions.get("trend", "neutral")
        days_to_earnings = conditions.get("days_to_earnings", 30)

        # Strategy selection logic based on conditions
        if days_to_earnings <= 7 and iv_percentile < 30:
            return StrategyType.VOLATILITY_PLAY.value
        elif iv_percentile > 60 and trend == "neutral":
            return StrategyType.IRON_CONDOR.value
        elif iv_percentile > 40:
            return StrategyType.WHEEL.value
        else:
            return StrategyType.WHEEL.value  # Default to wheel

    async def generate_wheel_strategy(
        self, symbol: str, conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized Wheel strategy trade
        """
        try:
            params = self.learning_parameters[StrategyType.WHEEL]
            current_price = conditions.get("current_price", 450.0)

            # Phase 1: Cash-Secured Put
            put_strike = current_price * (1 - params["put_delta_target"])
            put_premium = current_price * params["min_premium_pct"] / 100

            # Calculate Greeks (mock values - in production use real options data)
            put_delta = -params["put_delta_target"]
            put_theta = -put_premium / params["max_dte"]
            put_vega = put_premium * 0.1  # Mock vega

            strategy = {
                "strategy_type": StrategyType.WHEEL.value,
                "phase": "cash_secured_put",
                "underlying": symbol,
                "current_price": current_price,
                "legs": [
                    {
                        "option_type": "put",
                        "action": "sell",
                        "strike": round(put_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(put_premium, 2),
                        "delta": round(put_delta, 3),
                        "theta": round(put_theta, 3),
                        "vega": round(put_vega, 3),
                    }
                ],
                "max_profit": round(put_premium * 100, 2),  # Per contract
                "max_loss": round((put_strike - put_premium) * 100, 2),
                "profit_target": round(
                    put_premium * params["profit_target_pct"] / 100 * 100, 2
                ),
                "capital_required": round(put_strike * 100, 2),
                "roi_potential": round(put_premium / put_strike * 100, 2),
                "parameters_used": params,
                "market_conditions": conditions,
                "confidence_score": self._calculate_confidence_score(
                    StrategyType.WHEEL, conditions
                ),
            }

            return strategy

        except Exception as e:
            logger.error(f"Error generating wheel strategy: {str(e)}")
            return {}

    async def generate_iron_condor_strategy(
        self, symbol: str, conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized Iron Condor strategy
        """
        try:
            params = self.learning_parameters[StrategyType.IRON_CONDOR]
            current_price = conditions.get("current_price", 450.0)
            wing_width = params["wing_width"]

            # Calculate strikes based on delta targets
            call_short_strike = current_price * (1 + params["target_delta"])
            call_long_strike = call_short_strike + wing_width
            put_short_strike = current_price * (1 - params["target_delta"])
            put_long_strike = put_short_strike - wing_width

            # Mock premium calculations
            call_short_premium = current_price * 0.02
            call_long_premium = current_price * 0.01
            put_short_premium = current_price * 0.02
            put_long_premium = current_price * 0.01

            net_credit = (call_short_premium + put_short_premium) - (
                call_long_premium + put_long_premium
            )

            strategy = {
                "strategy_type": StrategyType.IRON_CONDOR.value,
                "underlying": symbol,
                "current_price": current_price,
                "legs": [
                    {
                        "option_type": "call",
                        "action": "sell",
                        "strike": round(call_short_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(call_short_premium, 2),
                        "delta": round(params["target_delta"], 3),
                    },
                    {
                        "option_type": "call",
                        "action": "buy",
                        "strike": round(call_long_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(call_long_premium, 2),
                        "delta": round(params["target_delta"] * 0.5, 3),
                    },
                    {
                        "option_type": "put",
                        "action": "sell",
                        "strike": round(put_short_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(put_short_premium, 2),
                        "delta": round(-params["target_delta"], 3),
                    },
                    {
                        "option_type": "put",
                        "action": "buy",
                        "strike": round(put_long_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(put_long_premium, 2),
                        "delta": round(-params["target_delta"] * 0.5, 3),
                    },
                ],
                "net_credit": round(net_credit * 100, 2),
                "max_profit": round(net_credit * 100, 2),
                "max_loss": round((wing_width - net_credit) * 100, 2),
                "profit_target": round(
                    net_credit * params["profit_target_pct"] / 100 * 100, 2
                ),
                "breakeven_high": round(call_short_strike + net_credit, 2),
                "breakeven_low": round(put_short_strike - net_credit, 2),
                "parameters_used": params,
                "market_conditions": conditions,
                "confidence_score": self._calculate_confidence_score(
                    StrategyType.IRON_CONDOR, conditions
                ),
            }

            return strategy

        except Exception as e:
            logger.error(f"Error generating iron condor strategy: {str(e)}")
            return {}

    async def generate_volatility_play_strategy(
        self, symbol: str, conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized Volatility Play strategy (Straddle/Strangle)
        """
        try:
            params = self.learning_parameters[StrategyType.VOLATILITY_PLAY]
            current_price = conditions.get("current_price", 450.0)
            days_to_earnings = conditions.get("days_to_earnings", 30)

            # Choose between straddle and strangle based on conditions
            if days_to_earnings <= 7:
                # Use straddle for earnings plays
                strategy_name = "Long Straddle"
                call_strike = current_price
                put_strike = current_price
                call_premium = current_price * 0.03
                put_premium = current_price * 0.03
            else:
                # Use strangle for general volatility
                strategy_name = "Long Strangle"
                call_strike = current_price * (1 + params["strangle_delta"])
                put_strike = current_price * (1 - params["strangle_delta"])
                call_premium = current_price * 0.02
                put_premium = current_price * 0.02

            total_premium = call_premium + put_premium

            strategy = {
                "strategy_type": StrategyType.VOLATILITY_PLAY.value,
                "strategy_name": strategy_name,
                "underlying": symbol,
                "current_price": current_price,
                "legs": [
                    {
                        "option_type": "call",
                        "action": "buy",
                        "strike": round(call_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(call_premium, 2),
                        "delta": round(
                            (
                                params["straddle_delta"]
                                if strategy_name == "Long Straddle"
                                else params["strangle_delta"]
                            ),
                            3,
                        ),
                        "vega": round(params["vega_threshold"], 3),
                    },
                    {
                        "option_type": "put",
                        "action": "buy",
                        "strike": round(put_strike, 2),
                        "expiration": (
                            datetime.now() + timedelta(days=params["max_dte"])
                        ).strftime("%Y-%m-%d"),
                        "quantity": 1,
                        "premium": round(put_premium, 2),
                        "delta": round(
                            (
                                -params["straddle_delta"]
                                if strategy_name == "Long Straddle"
                                else -params["strangle_delta"]
                            ),
                            3,
                        ),
                        "vega": round(params["vega_threshold"], 3),
                    },
                ],
                "total_cost": round(total_premium * 100, 2),
                "max_loss": round(total_premium * 100, 2),
                "max_profit": "Unlimited",
                "profit_target": round(
                    total_premium * params["profit_target_pct"] / 100 * 100, 2
                ),
                "breakeven_high": round(call_strike + total_premium, 2),
                "breakeven_low": round(put_strike - total_premium, 2),
                "iv_expansion_needed": round(total_premium / current_price * 100, 1),
                "parameters_used": params,
                "market_conditions": conditions,
                "confidence_score": self._calculate_confidence_score(
                    StrategyType.VOLATILITY_PLAY, conditions
                ),
            }

            return strategy

        except Exception as e:
            logger.error(f"Error generating volatility play strategy: {str(e)}")
            return {}

    def _calculate_confidence_score(
        self, strategy_type: StrategyType, conditions: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for strategy based on market conditions and historical performance
        """
        try:
            base_score = 0.5  # Start with neutral confidence

            iv_percentile = conditions.get("iv_percentile", 50)
            trend = conditions.get("trend", "neutral")
            days_to_earnings = conditions.get("days_to_earnings", 30)

            if strategy_type == StrategyType.WHEEL:
                # Higher confidence when IV is elevated
                if iv_percentile > 50:
                    base_score += 0.2
                # Prefer bullish or neutral trends
                if trend in ["bullish", "neutral"]:
                    base_score += 0.1

            elif strategy_type == StrategyType.IRON_CONDOR:
                # Higher confidence in high IV, neutral trends
                if iv_percentile > 60:
                    base_score += 0.3
                if trend == "neutral":
                    base_score += 0.2
                # Avoid near earnings
                if days_to_earnings > 14:
                    base_score += 0.1

            elif strategy_type == StrategyType.VOLATILITY_PLAY:
                # Higher confidence near earnings
                if days_to_earnings <= 7:
                    base_score += 0.3
                # Low IV is good for buying volatility
                if iv_percentile < 40:
                    base_score += 0.2

            # Factor in historical performance
            if strategy_type in self.strategy_performance:
                perf = self.strategy_performance[strategy_type]
                win_rate = perf.get("win_rate", 50)
                if win_rate > 60:
                    base_score += 0.1
                elif win_rate < 40:
                    base_score -= 0.1

            return min(max(base_score, 0.0), 1.0)  # Clamp between 0 and 1

        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5

    async def optimize_parameters(self, strategy_type: StrategyType):
        """
        Use machine learning to optimize strategy parameters based on historical performance
        """
        try:
            if not self.trade_history:
                logger.info("No trade history available for optimization")
                return

            # Filter trades by strategy type
            strategy_trades = [
                t for t in self.trade_history if t.strategy_type == strategy_type
            ]

            if len(strategy_trades) < 10:  # Need minimum trades for optimization
                logger.info(f"Not enough trades for {strategy_type.value} optimization")
                return

            # Analyze performance metrics
            performance_data = self._analyze_strategy_performance(strategy_trades)

            # Optimize parameters based on performance
            optimized_params = self._genetic_algorithm_optimization(
                strategy_type, strategy_trades
            )

            # Update learning parameters if improvement is significant
            current_performance = performance_data.get("sharpe_ratio", 0)
            if current_performance > 0.5:  # Only update if performance is decent
                self.learning_parameters[strategy_type].update(optimized_params)
                logger.info(f"Updated parameters for {strategy_type.value} strategy")

        except Exception as e:
            logger.error(f"Error optimizing parameters: {str(e)}")

    def _analyze_strategy_performance(
        self, trades: List[ExpertTrade]
    ) -> Dict[str, float]:
        """
        Analyze performance metrics for a strategy
        """
        if not trades:
            return {}

        pnls = [t.current_pnl for t in trades if t.status == TradeStatus.CLOSED]

        if not pnls:
            return {}

        total_return = sum(pnls)
        win_rate = len([p for p in pnls if p > 0]) / len(pnls) * 100

        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        avg_win = statistics.mean(wins) if wins else 0
        avg_loss = statistics.mean(losses) if losses else 0
        profit_factor = (
            abs(sum(wins) / sum(losses))
            if losses and sum(losses) != 0
            else float("inf")
        )

        # Calculate Sharpe ratio (simplified)
        if len(pnls) > 1:
            returns_std = statistics.stdev(pnls)
            sharpe_ratio = statistics.mean(pnls) / returns_std if returns_std > 0 else 0
        else:
            sharpe_ratio = 0

        return {
            "total_return": total_return,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": len(trades),
            "max_drawdown": min(pnls) if pnls else 0,
        }

    def _genetic_algorithm_optimization(
        self, strategy_type: StrategyType, trades: List[ExpertTrade]
    ) -> Dict[str, Any]:
        """
        Use genetic algorithm to optimize strategy parameters
        """
        # Simplified genetic algorithm for parameter optimization
        current_params = self.learning_parameters[strategy_type].copy()

        # Define parameter ranges for optimization
        if strategy_type == StrategyType.WHEEL:
            param_ranges = {
                "put_delta_target": (0.15, 0.40),
                "profit_target_pct": (25, 75),
                "max_dte": (21, 60),
            }
        elif strategy_type == StrategyType.IRON_CONDOR:
            param_ranges = {
                "target_delta": (0.10, 0.25),
                "profit_target_pct": (15, 40),
                "wing_width": (5, 20),
            }
        else:  # VOLATILITY_PLAY
            param_ranges = {
                "profit_target_pct": (50, 150),
                "loss_limit_pct": (25, 75),
                "max_dte": (7, 21),
            }

        # Simple optimization: try random variations and keep best performers
        best_params = current_params.copy()
        best_score = 0

        for _ in range(50):  # 50 iterations
            test_params = current_params.copy()

            # Randomly modify parameters within ranges
            for param, (min_val, max_val) in param_ranges.items():
                if param in test_params:
                    test_params[param] = np.random.uniform(min_val, max_val)

            # Calculate score for these parameters (simplified)
            score = self._evaluate_parameters(strategy_type, test_params, trades)

            if score > best_score:
                best_score = score
                best_params.update(
                    {k: v for k, v in test_params.items() if k in param_ranges}
                )

        return best_params

    def _evaluate_parameters(
        self,
        strategy_type: StrategyType,
        params: Dict[str, Any],
        trades: List[ExpertTrade],
    ) -> float:
        """
        Evaluate parameter set based on historical performance
        """
        # Simplified evaluation - in production would backtest with new parameters
        weights = params.get(
            "learning_weights",
            {"win_rate": 0.5, "profit_factor": 0.3, "sharpe_ratio": 0.2},
        )

        performance = self._analyze_strategy_performance(trades)

        score = 0
        if "win_rate" in performance:
            score += (performance["win_rate"] / 100) * weights.get("win_rate", 0)
        if "profit_factor" in performance:
            score += min(performance["profit_factor"] / 2, 1) * weights.get(
                "profit_factor", 0
            )
        if "sharpe_ratio" in performance:
            score += max(min(performance["sharpe_ratio"], 1), 0) * weights.get(
                "sharpe_ratio", 0
            )

        return score

    async def get_strategy_recommendations(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get AI-powered strategy recommendations based on market conditions
        """
        try:
            conditions = await self.analyze_market_conditions(symbol)
            recommendations = []

            # Generate all three strategies
            wheel_strategy = await self.generate_wheel_strategy(symbol, conditions)
            iron_condor_strategy = await self.generate_iron_condor_strategy(
                symbol, conditions
            )
            volatility_strategy = await self.generate_volatility_play_strategy(
                symbol, conditions
            )

            # Add to recommendations with scores
            strategies = [
                ("Wheel Strategy", wheel_strategy),
                ("Iron Condor", iron_condor_strategy),
                ("Volatility Play", volatility_strategy),
            ]

            for name, strategy in strategies:
                if strategy:
                    strategy["strategy_name"] = name
                    recommendations.append(strategy)

            # Sort by confidence score
            recommendations.sort(
                key=lambda x: x.get("confidence_score", 0), reverse=True
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting strategy recommendations: {str(e)}")
            return []

    async def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights from the learning system
        """
        try:
            insights = {
                "total_trades": len(self.trade_history),
                "active_trades": len(self.active_trades),
                "strategy_performance": {},
                "market_insights": {},
                "optimization_status": {},
            }

            # Calculate performance for each strategy
            for strategy_type in StrategyType:
                strategy_trades = [
                    t for t in self.trade_history if t.strategy_type == strategy_type
                ]
                if strategy_trades:
                    perf = self._analyze_strategy_performance(strategy_trades)
                    insights["strategy_performance"][strategy_type.value] = perf

            # Add optimization status
            insights["optimization_status"][strategy_type.value] = {
                "optimized": len(strategy_trades) >= 10,
                "last_optimization": datetime.now().isoformat(),
                "parameter_version": "1.0",
            }

            # Market insights
            insights["market_insights"] = {
                "preferred_strategy": (
                    "wheel" if len(self.trade_history) == 0 else "data_driven"
                ),
                "current_conditions": "neutral",
                "iv_environment": "moderate",
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting learning insights: {str(e)}")
            return {}


# Global instance
expert_system = ExpertOptionsSystem()
