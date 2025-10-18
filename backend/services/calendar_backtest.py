"""
Calendar Spread Backtest Engine

Backtests calendar spread strategies over historical earnings announcements
to validate win rate, average profit, max drawdown, and Sharpe ratio.

Strategy:
- Enter calendar spread 7-10 days before earnings
- Exit 1 day after earnings announcement
- Measure IV crush, P&L, and risk metrics

Author: FlowMind AI Team
Date: October 15, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

logger = logging.getLogger(__name__)


class CalendarBacktest:
    """
    Backtesting engine for calendar spread strategies

    Simulates historical calendar spreads around earnings to evaluate:
    - Win rate
    - Average profit/loss
    - Max drawdown
    - Sharpe ratio
    - Profit factor
    """

    def __init__(self, data_provider=None):
    """
                Initialize backtest engine

                Args:
                data_provider: Historical options data provider (optional)
                """
    self.data_provider = data_provider

    # Backtest configuration
    self.entry_days_before_earnings = 7
    self.exit_days_after_earnings = 1
    self.atm_strike_tolerance = 0.05  # 5% from spot

    # Historical earnings data (demo)
    self.historical_earnings = self._load_demo_earnings_data()

    logger.info("CalendarBacktest engine initialized")

    async def backtest_symbol(
        self,
        symbol: str,
        lookback_quarters: int = 8,
        position_size: int = 1
    ) -> Dict:
    """
                Backtest calendar spread strategy for a symbol

                Args:
                symbol: Stock ticker
                lookback_quarters: Number of past earnings to backtest
                position_size: Number of contracts per trade

                Returns:
                Backtest results with metrics
                """
    logger.info(f"Backtesting {symbol} over {lookback_quarters} quarters")

    # Get historical earnings for this symbol
    earnings_history = self.historical_earnings.get(symbol, [])

    if not earnings_history:
    logger.warning(f"No historical data for {symbol}")
    return self._empty_backtest_result()

    # Limit to requested quarters
    earnings_history = earnings_history[:lookback_quarters]

    # Run backtest for each earnings
    trades = []

    for earnings_event in earnings_history:
    trade_result = await self._simulate_calendar_spread(
        symbol=symbol,
        earnings_event=earnings_event,
        position_size=position_size
    )

    if trade_result:
    trades.append(trade_result)

    # Calculate aggregate metrics
    if not trades:
    return self._empty_backtest_result()

    results = self._calculate_metrics(trades)
    results["symbol"] = symbol
    results["lookback_quarters"] = lookback_quarters
    results["trades"] = len(trades)

    logger.info(
        f"{symbol} backtest: {results['wins']}/{results['trades']} wins, "
        f"${results['total_profit']:.2f} profit"
    )

    return results

    async def _simulate_calendar_spread(
        self,
        symbol: str,
        earnings_event: Dict,
        position_size: int
    ) -> Optional[Dict]:
    """
                Simulate a single calendar spread trade

                Trade flow:
                1. Enter 7 days before earnings
                2. Sell front-month call, buy back-month call
                3. Exit 1 day after earnings
                4. Calculate P&L based on IV crush
                """
    earnings_date = datetime.fromisoformat(earnings_event["date"])
    entry_date = earnings_date - \
        timedelta(days=self.entry_days_before_earnings)
    exit_date = earnings_date + timedelta(days=self.exit_days_after_earnings)

    # Get options data at entry
    spot_price = earnings_event["spot_price"]
    atm_strike = self._round_to_strike(spot_price)

    # Front month (expires before ER)
    front_exp = earnings_date - timedelta(days=2)
    front_dte_entry = (front_exp - entry_date).days
    front_iv_entry = earnings_event["iv_pre_earnings"]
    front_call_entry = self._estimate_option_price(
        spot=spot_price,
        strike=atm_strike,
        dte=front_dte_entry,
        iv=front_iv_entry
    )

    # Back month (expires after ER)
    back_exp = earnings_date + timedelta(days=30)
    back_dte_entry = (back_exp - entry_date).days
    back_iv_entry = earnings_event["iv_normal"]
    back_call_entry = self._estimate_option_price(
        spot=spot_price,
        strike=atm_strike,
        dte=back_dte_entry,
        iv=back_iv_entry
    )

    # Entry cost (debit spread)
    entry_cost = (back_call_entry - front_call_entry) * position_size * 100

    # Exit values (1 day after earnings)
    # Front month: IV crushed, close to expiration
    front_dte_exit = (front_exp - exit_date).days
    front_iv_exit = front_iv_entry * (1 - earnings_event["iv_crush"])

    # Check if front expired worthless (best case)
    if front_dte_exit <= 0:
    front_call_exit = 0
    else:
    front_call_exit = self._estimate_option_price(
        spot=earnings_event["spot_price_post"],
        strike=atm_strike,
        dte=front_dte_exit,
        iv=front_iv_exit
    )

    # Back month: Also crushed but still has time value
    back_dte_exit = (back_exp - exit_date).days
    back_iv_exit = back_iv_entry * \
        (1 - earnings_event["iv_crush"] * 0.5)  # Less crush
    back_call_exit = self._estimate_option_price(
        spot=earnings_event["spot_price_post"],
        strike=atm_strike,
        dte=back_dte_exit,
        iv=back_iv_exit
    )

    # Exit value
    exit_value = (back_call_exit - front_call_exit) * position_size * 100

    # P&L
    pnl = exit_value - entry_cost

    # Trade result
    return {
        "symbol": symbol,
        "entry_date": entry_date.strftime("%Y-%m-%d"),
        "exit_date": exit_date.strftime("%Y-%m-%d"),
        "earnings_date": earnings_date.strftime("%Y-%m-%d"),
        "strike": atm_strike,
        "position_size": position_size,
        "entry_cost": entry_cost,
        "exit_value": exit_value,
        "pnl": pnl,
        "pnl_pct": (pnl / entry_cost * 100) if entry_cost > 0 else 0,
        "iv_crush": earnings_event["iv_crush"],
        "spot_move_pct": earnings_event.get("spot_move_pct", 0),
        "win": pnl > 0
    }

    def _calculate_metrics(self, trades: List[Dict]) -> Dict:
    """Calculate aggregate backtest metrics"""
    wins = [t for t in trades if t["win"]]
    losses = [t for t in trades if not t["win"]]

    total_pnl = sum(t["pnl"] for t in trades)

    # Win rate
    win_rate = len(wins) / len(trades) if trades else 0

    # Average profit/loss
    avg_profit = statistics.mean(t["pnl"] for t in wins) if wins else 0
    avg_loss = statistics.mean(t["pnl"] for t in losses) if losses else 0

    # Max drawdown
    cumulative_pnl = 0
    max_pnl = 0
    max_drawdown = 0

    for trade in trades:
    cumulative_pnl += trade["pnl"]
    max_pnl = max(max_pnl, cumulative_pnl)
    drawdown = max_pnl - cumulative_pnl
    max_drawdown = max(max_drawdown, drawdown)

    # Sharpe ratio (simplified)
    # Assume risk-free rate = 0 for simplicity
    if trades:
    returns = [t["pnl_pct"] for t in trades]
    avg_return = statistics.mean(returns)
    std_return = statistics.stdev(returns) if len(returns) > 1 else 0
    sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0
    else:
    sharpe_ratio = 0

    # Profit factor
    gross_profit = sum(t["pnl"] for t in wins)
    gross_loss = abs(sum(t["pnl"] for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

    return {
        "trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "total_profit": total_pnl,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "best_trade": max(
            trades,
            key=lambda t: t["pnl"])["pnl"] if trades else 0,
        "worst_trade": min(
            trades,
            key=lambda t: t["pnl"])["pnl"] if trades else 0,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "profit_factor": profit_factor,
        "avg_iv_crush": statistics.mean(
            t["iv_crush"] for t in trades) if trades else 0}

    def _load_demo_earnings_data(self) -> Dict:
    """
                Load demo historical earnings data

                In production, this would query historical database
                """
    return {
        "TSLA": [
            {
                "date": "2025-07-15",
                "spot_price": 245.0,
                "spot_price_post": 252.0,
                "spot_move_pct": 2.86,
                "iv_pre_earnings": 0.85,
                "iv_normal": 0.42,
                "iv_crush": 0.52
            },
            {
                "date": "2025-04-15",
                "spot_price": 238.0,
                "spot_price_post": 230.0,
                "spot_move_pct": -3.36,
                "iv_pre_earnings": 0.78,
                "iv_normal": 0.40,
                "iv_crush": 0.48
            },
            {
                "date": "2025-01-15",
                "spot_price": 255.0,
                "spot_price_post": 268.0,
                "spot_move_pct": 5.10,
                "iv_pre_earnings": 0.88,
                "iv_normal": 0.43,
                "iv_crush": 0.55
            },
            {
                "date": "2024-10-15",
                "spot_price": 248.0,
                "spot_price_post": 242.0,
                "spot_move_pct": -2.42,
                "iv_pre_earnings": 0.80,
                "iv_normal": 0.41,
                "iv_crush": 0.45
            },
            {
                "date": "2024-07-15",
                "spot_price": 240.0,
                "spot_price_post": 246.0,
                "spot_move_pct": 2.50,
                "iv_pre_earnings": 0.82,
                "iv_normal": 0.42,
                "iv_crush": 0.50
            },
            {
                "date": "2024-04-15",
                "spot_price": 232.0,
                "spot_price_post": 228.0,
                "spot_move_pct": -1.72,
                "iv_pre_earnings": 0.76,
                "iv_normal": 0.40,
                "iv_crush": 0.47
            },
            {
                "date": "2024-01-15",
                "spot_price": 250.0,
                "spot_price_post": 260.0,
                "spot_move_pct": 4.00,
                "iv_pre_earnings": 0.86,
                "iv_normal": 0.44,
                "iv_crush": 0.53
            },
            {
                "date": "2023-10-15",
                "spot_price": 245.0,
                "spot_price_post": 238.0,
                "spot_move_pct": -2.86,
                "iv_pre_earnings": 0.79,
                "iv_normal": 0.41,
                "iv_crush": 0.49
            }
        ],
        "NVDA": [
            {
                "date": "2025-08-15",
                "spot_price": 445.0,
                "spot_price_post": 465.0,
                "spot_move_pct": 4.49,
                "iv_pre_earnings": 0.90,
                "iv_normal": 0.46,
                "iv_crush": 0.58
            },
            {
                "date": "2025-05-15",
                "spot_price": 438.0,
                "spot_price_post": 452.0,
                "spot_move_pct": 3.20,
                "iv_pre_earnings": 0.88,
                "iv_normal": 0.45,
                "iv_crush": 0.55
            },
            {
                "date": "2025-02-15",
                "spot_price": 425.0,
                "spot_price_post": 418.0,
                "spot_move_pct": -1.65,
                "iv_pre_earnings": 0.85,
                "iv_normal": 0.44,
                "iv_crush": 0.52
            },
            {
                "date": "2024-11-15",
                "spot_price": 455.0,
                "spot_price_post": 475.0,
                "spot_move_pct": 4.40,
                "iv_pre_earnings": 0.92,
                "iv_normal": 0.47,
                "iv_crush": 0.60
            },
            {
                "date": "2024-08-15",
                "spot_price": 442.0,
                "spot_price_post": 435.0,
                "spot_move_pct": -1.58,
                "iv_pre_earnings": 0.87,
                "iv_normal": 0.45,
                "iv_crush": 0.48
            },
            {
                "date": "2024-05-15",
                "spot_price": 430.0,
                "spot_price_post": 448.0,
                "spot_move_pct": 4.19,
                "iv_pre_earnings": 0.89,
                "iv_normal": 0.46,
                "iv_crush": 0.54
            },
            {
                "date": "2024-02-15",
                "spot_price": 420.0,
                "spot_price_post": 438.0,
                "spot_move_pct": 4.29,
                "iv_pre_earnings": 0.91,
                "iv_normal": 0.48,
                "iv_crush": 0.57
            },
            {
                "date": "2023-11-15",
                "spot_price": 450.0,
                "spot_price_post": 442.0,
                "spot_move_pct": -1.78,
                "iv_pre_earnings": 0.86,
                "iv_normal": 0.45,
                "iv_crush": 0.53
            }
        ],
        # Add more symbols as needed...
    }

    def _estimate_option_price(
        self,
        spot: float,
        strike: float,
        dte: int,
        iv: float
    ) -> float:
    """
                Estimate option price using simplified Black-Scholes

                This is a rough approximation for demo purposes.
                Production would use full Black-Scholes or actual market prices.
                """
    # Simplified: intrinsic + time value
    intrinsic = max(0, spot - strike)

    # Time value ~ sqrt(DTE) * IV * spot * 0.4
    time_value = (dte ** 0.5) * iv * spot * 0.04

    return intrinsic + time_value

    def _round_to_strike(self, price: float) -> float:
    """Round to nearest standard strike"""
    if price < 25:
    return round(price * 2) / 2
    elif price < 200:
    return round(price)
    else:
    return round(price / 5) * 5

    def _empty_backtest_result(self) -> Dict:
    """Return empty backtest result"""
    return {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0.0,
        "total_profit": 0.0,
        "avg_profit": 0.0,
        "avg_loss": 0.0,
        "best_trade": 0.0,
        "worst_trade": 0.0,
        "max_drawdown": 0.0,
        "sharpe_ratio": 0.0,
        "profit_factor": 0.0,
        "avg_iv_crush": 0.0
    }
