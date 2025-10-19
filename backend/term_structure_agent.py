"""
Term Structure Volatility Arbitrage Agent

This agent scans upcoming earnings announcements and identifies calendar spread
opportunities based on forward volatility factor mispricing.

Key Strategy:
- Identify stocks with earnings in next 30 days
- Calculate forward vol factor = IV_front_month / IV_back_month
- Higher factors (>1.5) indicate term structure mispricing
- Execute calendar spreads: SELL expensive front-month, BUY cheap back-month
- Profit from IV crush post-earnings

Author: FlowMind AI Team
Date: October 15, 2025
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

logger = logging.getLogger(__name__)

class TermStructureAgent:
    """
    AI Agent for Term Structure Volatility Arbitrage
    
    Capabilities:
    - Scan earnings calendar for upcoming announcements
    - Calculate forward volatility factors
    - Rank opportunities by mispricing severity
    - Generate calendar spread trade recommendations
    - Integrate with ML IV crush predictor
    - Pre-trade backtest validation
    """
    
    def __init__(self, uw_client=None, ts_client=None, ml_predictor=None):
        """
        Initialize Term Structure Agent
        
        Args:
        uw_client: Unusual Whales client for earnings calendar
        ts_client: TradeStation client for options chains
        ml_predictor: ML model for IV crush prediction
        """
        self.uw_client = uw_client
        self.ts_client = ts_client
        self.ml_predictor = ml_predictor
        
        # Configuration
        self.min_fwd_vol_factor = 1.3 # Minimum factor to consider
        self.optimal_fwd_vol_factor = 1.5 # Ideal mispricing
        self.min_dte_front = 5 # Minimum DTE for front month
        self.max_dte_front = 15 # Maximum DTE for front month
        self.min_dte_back = 25 # Minimum DTE for back month
        self.max_dte_back = 50 # Maximum DTE for back month
        
        logger.info("TermStructureAgent initialized")
 
    async def scan_earnings_calendar(self, days_ahead: int = 30) -> List[Dict]:
        """
        Scan upcoming earnings and calculate term structure opportunities
        
        Args:
        days_ahead: How many days to look ahead for earnings
        
        Returns:
        List of opportunities ranked by quality score
        """
        logger.info(f"Scanning earnings calendar for next {days_ahead} days")
        
        # Get earnings calendar (demo data for now)
        earnings_calendar = await self._get_earnings_calendar(days_ahead)
        
        opportunities = []
        
        for stock in earnings_calendar:
            try:
                # Get options chain
                chain_data = await self._get_options_chain(stock["symbol"])
                
                if not chain_data:
                    logger.warning(f"No options chain for {stock['symbol']}")
                    continue
                
                # Find optimal expirations (pre-earnings and post-earnings)
                front_exp, back_exp = self._find_optimal_expirations(
                    chain_data["expirations"],
                    stock["earnings_date"]
                )
                
                if not front_exp or not back_exp:
                    logger.debug(f"No suitable expirations for {stock['symbol']}")
                    continue
                
                # Calculate ATM strike
                current_price = stock["current_price"]
                atm_strike = self._round_to_nearest_strike(current_price)
                
                # Get IV for front and back month at ATM
                front_iv = self._get_iv_for_strike(
                    chain_data, front_exp, atm_strike, "call"
                )
                back_iv = self._get_iv_for_strike(
                    chain_data, back_exp, atm_strike, "call"
                )
                
                if not front_iv or not back_iv or back_iv == 0:
                    continue
                
                # Calculate forward volatility factor
                fwd_vol_factor = front_iv / back_iv
                
                # Skip if factor too low (no mispricing)
                if fwd_vol_factor < self.min_fwd_vol_factor:
                    logger.debug(f"{stock['symbol']} factor {fwd_vol_factor:.2f} too low")
                    continue
                
                # Get historical IV crush data
                historical_crush = await self._get_historical_iv_crush(stock["symbol"])
                
                # ML prediction for IV crush
                ml_predicted_crush = None
                if self.ml_predictor:
                    ml_predicted_crush = await self.ml_predictor.predict_iv_crush(
                        symbol=stock["symbol"],
                        current_iv=front_iv,
                        sector=stock.get("sector", "Unknown"),
                        market_cap=stock.get("market_cap", 0)
                    )
                
                # Calculate calendar spread pricing
                front_call = self._get_option_price(
                    chain_data, front_exp, atm_strike, "call"
                )
                back_call = self._get_option_price(
                    chain_data, back_exp, atm_strike, "call"
                )
                
                if not front_call or not back_call:
                    continue
                
                spread_cost = back_call - front_call # Net debit
                
                # Estimate profit potential
                # After earnings, front month IV should drop by crush %
                estimated_crush = ml_predicted_crush or historical_crush
                expected_front_value_post_er = front_call * (1 - estimated_crush)
                expected_profit = front_call - expected_front_value_post_er - (spread_cost * 0.1) # 10% slippage
                
                roi = (expected_profit / spread_cost * 100) if spread_cost > 0 else 0
                
                # Calculate opportunity score
                # Factors: fwd_vol_factor, historical_crush, ML confidence, liquidity
                opportunity_score = self._calculate_opportunity_score(
                    fwd_vol_factor=fwd_vol_factor,
                    historical_crush=historical_crush,
                    ml_predicted_crush=ml_predicted_crush,
                    volume=stock.get("avg_volume", 0)
                )
                
                # Backtest this strategy on historical data
                backtest_results = await self._backtest_calendar_spread(
                    symbol=stock["symbol"],
                    lookback_quarters=8
                )
                
                opportunity = {
                    "symbol": stock["symbol"],
                    "company_name": stock.get("company_name", stock["symbol"]),
                    "earnings_date": stock["earnings_date"],
                    "days_to_earnings": stock["days_to_earnings"],
                    "current_price": current_price,
                    "sector": stock.get("sector", "Unknown"),
                    "market_cap": stock.get("market_cap", 0),
                    
                    "atm_strike": atm_strike,
                    
                    "front_month": {
                        "expiration": front_exp,
                        "dte": self._calculate_dte(front_exp),
                        "iv": front_iv,
                        "call_price": front_call
                    },
                    
                    "back_month": {
                        "expiration": back_exp,
                        "dte": self._calculate_dte(back_exp),
                        "iv": back_iv,
                        "call_price": back_call
                    },
                    
                    "forward_vol_factor": fwd_vol_factor,
                    "spread_cost": spread_cost,
                    "expected_profit": expected_profit,
                    "expected_roi": roi,
                    
                    "iv_crush": {
                        "historical_avg": historical_crush,
                        "ml_predicted": ml_predicted_crush,
                        "confidence": 0.85 if ml_predicted_crush else 0.60
                    },
                    
                    "backtest": backtest_results,
                    
                    "opportunity_score": opportunity_score,
                    "risk_rating": self._calculate_risk_rating(fwd_vol_factor, backtest_results),
                    
                    "trade_recommendation": {
                        "action": "BUY_CALENDAR_SPREAD",
                        "entry_timing": f"{stock['days_to_earnings'] - 7} days before ER",
                        "exit_timing": "1 day after ER announcement",
                        "position_size": self._recommend_position_size(
                            opportunity_score, backtest_results
                        ),
                        "max_risk_per_contract": spread_cost,
                        "target_profit_per_contract": expected_profit
                    }
                }
                
                opportunities.append(opportunity)
            
            except Exception as e:
                logger.error(f"Error processing {stock['symbol']}: {e}")
                continue
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        logger.info(f"Found {len(opportunities)} term structure opportunities")
        
        return opportunities
 
    async def _get_earnings_calendar(self, days_ahead: int) -> List[Dict]:
        """Get earnings calendar (demo data for now)"""
        today = datetime.now()
        
        # Demo earnings calendar
        demo_earnings = [
            {
                "symbol": "TSLA",
                "company_name": "Tesla Inc",
                "earnings_date": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
                "days_to_earnings": 12,
                "current_price": 250.50,
                "sector": "Automotive",
                "market_cap": 800_000_000_000,
                "avg_volume": 125_000_000
            },
            {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corp",
                "earnings_date": (today + timedelta(days=8)).strftime("%Y-%m-%d"),
                "days_to_earnings": 8,
                "current_price": 450.20,
                "sector": "Technology",
                "market_cap": 1_100_000_000_000,
                "avg_volume": 45_000_000
            },
            {
                "symbol": "AAPL",
                "company_name": "Apple Inc",
                "earnings_date": (today + timedelta(days=18)).strftime("%Y-%m-%d"),
                "days_to_earnings": 18,
                "current_price": 175.80,
                "sector": "Technology",
                "market_cap": 2_800_000_000_000,
                "avg_volume": 55_000_000
            },
            {
                "symbol": "META",
                "company_name": "Meta Platforms",
                "earnings_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
                "days_to_earnings": 10,
                "current_price": 320.15,
                "sector": "Technology",
                "market_cap": 850_000_000_000,
                "avg_volume": 18_000_000
            },
            {
                "symbol": "AMZN",
                "company_name": "Amazon.com Inc",
                "earnings_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
                "days_to_earnings": 15,
                "current_price": 135.90,
                "sector": "Consumer Cyclical",
                "market_cap": 1_400_000_000_000,
                "avg_volume": 52_000_000
            }
        ]
        
        return demo_earnings
    
    async def _get_options_chain(self, symbol: str) -> Optional[Dict]:
        """Get options chain for symbol (demo data for now)"""
        # Demo options chain data
        today = datetime.now()
        
        expirations = [
            (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            (today + timedelta(days=21)).strftime("%Y-%m-%d"),
            (today + timedelta(days=35)).strftime("%Y-%m-%d"),
            (today + timedelta(days=49)).strftime("%Y-%m-%d")
        ]
        
        return {
            "symbol": symbol,
            "expirations": expirations,
            "chains": {} # Simplified for demo
        }
    
    def _find_optimal_expirations(
        self, 
        expirations: List[str], 
        earnings_date: str
    ) -> tuple:
        """
        Find optimal front-month (pre-ER) and back-month (post-ER) expirations
        """
        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
        
        front_month = None
        back_month = None
        
        for exp_str in expirations:
            exp_dt = datetime.strptime(exp_str, "%Y-%m-%d")
            dte = (exp_dt - datetime.now()).days
            
            # Front month: expires 2-7 days before earnings
            if exp_dt < earnings_dt:
                days_before_er = (earnings_dt - exp_dt).days
                if 2 <= days_before_er <= 7:
                    if not front_month or abs(days_before_er - 3) < abs(
                        (earnings_dt - datetime.strptime(front_month, "%Y-%m-%d")).days - 3
                    ):
                        front_month = exp_str
            
            # Back month: expires 20-40 days after earnings
            elif exp_dt > earnings_dt:
                days_after_er = (exp_dt - earnings_dt).days
                if 20 <= days_after_er <= 40:
                    if not back_month or abs(days_after_er - 30) < abs(
                        (datetime.strptime(back_month, "%Y-%m-%d") - earnings_dt).days - 30
                    ):
                        back_month = exp_str
        
        return front_month, back_month
    
    def _round_to_nearest_strike(self, price: float) -> float:
        """Round price to nearest standard strike"""
        if price < 25:
            return round(price * 2) / 2 # $0.50 increments
        elif price < 200:
            return round(price) # $1 increments
        else:
            return round(price / 5) * 5 # $5 increments
    
    def _get_iv_for_strike(
        self, 
        chain_data: Dict, 
        expiration: str, 
        strike: float, 
        option_type: str
    ) -> Optional[float]:
        """Get IV for specific strike (demo data)"""
        # Demo: Front-month has elevated IV (80%), back-month normal (45%)
        if self._calculate_dte(expiration) < 20:
            return 0.82 # 82% IV for front month (pre-earnings)
        else:
            return 0.45 # 45% IV for back month (post-earnings)
    
    def _get_option_price(
        self, 
        chain_data: Dict, 
        expiration: str, 
        strike: float, 
        option_type: str
    ) -> Optional[float]:
        """Get option price for specific strike (demo data)"""
        dte = self._calculate_dte(expiration)
        
        # Simplified Black-Scholes approximation for demo
        if dte < 20:
            return 14.50 # Front month call
        else:
            return 18.20 # Back month call
    
    def _calculate_dte(self, expiration: str) -> int:
        """Calculate days to expiration"""
        exp_dt = datetime.strptime(expiration, "%Y-%m-%d")
        return (exp_dt - datetime.now()).days
    
    async def _get_historical_iv_crush(self, symbol: str) -> float:
        """
        Get historical average IV crush for this symbol
        Returns: Average IV crush percentage (0.0 to 1.0)
        """
        # Demo data: typical IV crush percentages
        historical_crushes = {
            "TSLA": 0.48, # 48% average IV drop post-ER
            "NVDA": 0.52, # 52% average IV drop
            "AAPL": 0.35, # 35% average IV drop (less volatile)
            "META": 0.45, # 45% average IV drop
            "AMZN": 0.42 # 42% average IV drop
        }
        
        return historical_crushes.get(symbol, 0.40) # Default 40%
 
    async def _backtest_calendar_spread(
        self, 
        symbol: str, 
        lookback_quarters: int = 8
    ) -> Dict:
        """
        Backtest calendar spread strategy over past N earnings
        Returns: Win rate, avg profit, max drawdown, Sharpe ratio
        """
        # Demo backtest results
        backtest_data = {
            "TSLA": {
                "trades": 8,
                "wins": 6,
                "losses": 2,
                "win_rate": 0.75,
                "avg_profit": 285.0,
                "avg_loss": -125.0,
                "max_drawdown": -250.0,
                "sharpe_ratio": 1.85,
                "total_return": 1425.0
            },
            "NVDA": {
                "trades": 8,
                "wins": 7,
                "losses": 1,
                "win_rate": 0.875,
                "avg_profit": 320.0,
                "avg_loss": -95.0,
                "max_drawdown": -95.0,
                "sharpe_ratio": 2.15,
                "total_return": 2145.0
            },
            "AAPL": {
                "trades": 8,
                "wins": 5,
                "losses": 3,
                "win_rate": 0.625,
                "avg_profit": 180.0,
                "avg_loss": -110.0,
                "max_drawdown": -220.0,
                "sharpe_ratio": 1.20,
                "total_return": 570.0
            },
            "META": {
                "trades": 8,
                "wins": 6,
                "losses": 2,
                "win_rate": 0.75,
                "avg_profit": 250.0,
                "avg_loss": -140.0,
                "max_drawdown": -280.0,
                "sharpe_ratio": 1.65,
                "total_return": 1220.0
            },
            "AMZN": {
                "trades": 8,
                "wins": 5,
                "losses": 3,
                "win_rate": 0.625,
                "avg_profit": 210.0,
                "avg_loss": -105.0,
                "max_drawdown": -210.0,
                "sharpe_ratio": 1.45,
                "total_return": 735.0
            }
        }
        
        return backtest_data.get(symbol, {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "total_return": 0.0
        })
    
    def _calculate_opportunity_score(
        self,
        fwd_vol_factor: float,
        historical_crush: float,
        ml_predicted_crush: Optional[float],
        volume: int
    ) -> float:
        """
        Calculate composite opportunity score (0-100)
        
        Factors:
        - Forward vol factor (40% weight)
        - Historical IV crush (30% weight)
        - ML prediction confidence (20% weight)
        - Liquidity (10% weight)
        """
        # Factor 1: Forward vol factor (normalized to 0-100)
        # 1.5 = 75, 2.0 = 100
        factor_score = min(100, (fwd_vol_factor - 1.0) * 100)
        
        # Factor 2: Historical crush
        crush_score = historical_crush * 100
        
        # Factor 3: ML prediction
        ml_score = 0
        if ml_predicted_crush:
            ml_score = ml_predicted_crush * 100
        
        # Factor 4: Liquidity
        liquidity_score = min(100, volume / 1_000_000) # Normalize by 1M volume
        
        # Weighted average
        score = (
            factor_score * 0.40 +
            crush_score * 0.30 +
            ml_score * 0.20 +
            liquidity_score * 0.10
        )
        
        return round(score, 2)
    
    def _calculate_risk_rating(
        self, 
        fwd_vol_factor: float, 
        backtest_results: Dict
    ) -> str:
        """Calculate risk rating based on factor and backtest"""
        win_rate = backtest_results.get("win_rate", 0)
        sharpe = backtest_results.get("sharpe_ratio", 0)
        
        if fwd_vol_factor >= 1.8 and win_rate >= 0.75 and sharpe >= 1.5:
            return "LOW"
        elif fwd_vol_factor >= 1.5 and win_rate >= 0.65 and sharpe >= 1.2:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _recommend_position_size(
        self, 
        opportunity_score: float, 
        backtest_results: Dict
    ) -> int:
        """
        Recommend number of contracts based on opportunity quality
        """
        win_rate = backtest_results.get("win_rate", 0)
        
        if opportunity_score >= 80 and win_rate >= 0.75:
            return 5 # Aggressive
        elif opportunity_score >= 60 and win_rate >= 0.65:
            return 3 # Moderate
        else:
            return 1 # Conservative
