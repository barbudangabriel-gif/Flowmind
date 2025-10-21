"""
Investment Scoring Agent - AI-Powered Investment Analysis
Uses Unusual Whales data to generate comprehensive investment scores with ML-enhanced insights.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from unusual_whales_service import UnusualWhalesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvestmentScoringAgent:
    """
    AI-powered investment scoring agent that combines multiple data sources
    from Unusual Whales to generate comprehensive investment recommendations.
    """

    def __init__(self):
        self.uw_service = UnusualWhalesService()

        # Enhanced scoring weights for discount/premium logic
        self.signal_weights = {
            "discount_opportunity": 0.35,  # NEW: Heavily weight discount opportunities
            "options_flow": 0.20,  # Reduced: Options sentiment (still important)
            "dark_pool": 0.15,  # Institutional activity
            "congressional": 0.10,  # Political insider information
            "risk_reward_ratio": 0.10,  # NEW: Risk/reward calculation
            "market_momentum": 0.05,  # Reduced: General market indicators
            "premium_penalty": 0.05,  # NEW: Penalty for premium positions
        }

        # Discount/Premium thresholds
        self.discount_thresholds = {
            "rsi_oversold": 30,  # RSI below 30 = oversold discount
            "support_distance": 5,  # Within 5% of major support
            "pullback_threshold": -10,  # 10%+ pullback from recent high
            "pe_discount": 0.8,  # P/E below sector average * 0.8
        }

        self.premium_thresholds = {
            "rsi_overbought": 70,  # RSI above 70 = overbought premium
            "resistance_distance": 3,  # Within 3% of major resistance
            "rally_threshold": 20,  # 20%+ rally from recent low
            "pe_premium": 1.3,  # P/E above sector average * 1.3
        }

        # Risk/Reward calculation parameters
        self.risk_reward_params = {
            "min_reward_ratio": 2.0,  # Minimum 2:1 reward:risk ratio
            "max_risk_percentage": 8,  # Maximum 8% risk from entry
            "optimal_risk_percentage": 5,  # Optimal 5% risk from entry
        }

        # Confidence thresholds
        self.confidence_thresholds = {"high": 0.75, "medium": 0.50, "low": 0.25}

    async def generate_investment_score(
        self, symbol: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive investment score for a given symbol using UW data sources.

        Args:
            symbol: Stock ticker symbol
            user_context: Optional user mindfolio/preferences for personalization

        Returns:
            Dict containing investment score, signals, and recommendations
        """
        try:
            logger.info(f"Generating investment score for {symbol}")

            # 1. Fetch all UW data sources concurrently
            uw_data = await self._fetch_uw_data(symbol)

            # 2. Analyze each signal component
            signal_scores = await self._analyze_signal_components(uw_data, symbol)

            # 3. Calculate composite investment score
            composite_score = self._calculate_composite_score(signal_scores)

            # 4. Generate recommendation and confidence
            recommendation = self._generate_recommendation(
                composite_score, signal_scores
            )
            confidence = self._calculate_confidence_level(signal_scores)

            # 5. Extract key insights
            key_signals = self._extract_key_signals(uw_data, signal_scores)

            # 6. Risk assessment
            risk_analysis = self._assess_risk_factors(uw_data, signal_scores)

            return {
                "symbol": symbol,
                "investment_score": round(composite_score, 1),
                "recommendation": recommendation,
                "confidence_level": confidence,
                "key_signals": key_signals,
                "risk_analysis": risk_analysis,
                "signal_breakdown": signal_scores,
                "timestamp": datetime.now().isoformat(),
                "agent_version": "1.0",
                "data_sources": [
                    "unusual_whales_options_flow",
                    "dark_pool",
                    "congressional_trades",
                    "discount_premium_analysis",
                    "risk_reward_optimization",
                ],
            }

        except Exception as e:
            logger.error(f"Error generating investment score for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": f"Failed to generate investment score: {str(e)}",
                "investment_score": 50.0,  # Neutral score on error
                "recommendation": "HOLD",
                "confidence_level": "low",
                "timestamp": datetime.now().isoformat(),
            }

    async def _fetch_uw_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch all relevant data from Unusual Whales API concurrently."""
        try:
            # Fetch all UW data sources in parallel for efficiency
            tasks = [
                self.uw_service.get_options_flow_alerts(
                    minimum_premium=200000, limit=100  # Focus on significant flows
                ),
                self.uw_service.get_dark_pool_recent(
                    minimum_volume=100000, minimum_dark_percentage=0.01, limit=50
                ),
                self.uw_service.get_congressional_trades(
                    days_back=90,  # Longer lookback for congressional activity
                    minimum_amount=50000,
                    limit=100,
                ),
            ]

            options_flow, dark_pool, congressional = await asyncio.gather(
                *tasks, return_exceptions=True
            )

            # Filter data for the specific symbol
            filtered_data = {
                "options_flow": self._filter_options_for_symbol(options_flow, symbol),
                "dark_pool": self._filter_dark_pool_for_symbol(dark_pool, symbol),
                "congressional": self._filter_congressional_for_symbol(
                    congressional, symbol
                ),
                "strategies": [],
            }

            logger.info(
                f"Fetched UW data for {symbol}: Options={len(filtered_data['options_flow'])}, "
                f"DarkPool={len(filtered_data['dark_pool'])}, "
                f"Congressional={len(filtered_data['congressional'])}"
            )

            return filtered_data

        except Exception as e:
            logger.error(f"Error fetching UW data for {symbol}: {str(e)}")
            return {
                "options_flow": [],
                "dark_pool": [],
                "congressional": [],
                "strategies": [],
            }

    def _filter_options_for_symbol(
        self, options_data: List[Dict], symbol: str
    ) -> List[Dict]:
        """Filter options flow data for specific symbol."""
        if isinstance(options_data, Exception) or not options_data:
            return []

        return [
            opt
            for opt in options_data
            if opt.get("symbol", "").upper() == symbol.upper()
        ]

    def _filter_dark_pool_for_symbol(
        self, dark_pool_data: List[Dict], symbol: str
    ) -> List[Dict]:
        """Filter dark pool data for specific symbol."""
        if isinstance(dark_pool_data, Exception) or not dark_pool_data:
            return []

        return [
            dp
            for dp in dark_pool_data
            if dp.get("ticker", "").upper() == symbol.upper()
        ]

    def _filter_congressional_for_symbol(
        self, congressional_data: List[Dict], symbol: str
    ) -> List[Dict]:
        """Filter congressional trades for specific symbol."""
        if isinstance(congressional_data, Exception) or not congressional_data:
            return []

        return [
            cong
            for cong in congressional_data
            if cong.get("ticker", "").upper() == symbol.upper()
        ]

    def _filter_strategies_for_symbol(
        self, strategies_data: List[Dict], symbol: str
    ) -> List[Dict]:
        """Filter trading strategies for specific symbol."""
        if isinstance(strategies_data, Exception) or not strategies_data:
            return []

        return [
            strat
            for strat in strategies_data
            if symbol.upper() in strat.get("ticker", "").upper()
        ]

    async def _analyze_signal_components(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> Dict[str, float]:
        """Analyze each signal component and return normalized scores (0-100)."""

        signal_scores = {}

        # 1. NEW: Discount Opportunity Analysis (most important)
        signal_scores["discount_opportunity"] = (
            await self._analyze_discount_opportunity(uw_data, symbol)
        )

        signal_scores["options_flow_bullish"] = self._analyze_options_flow(
            uw_data["options_flow"]
        )

        # 3. Dark Pool Activity
        signal_scores["dark_pool_strength"] = self._analyze_dark_pool(
            uw_data["dark_pool"]
        )

        # 4. Congressional Activity
        signal_scores["congressional_interest"] = self._analyze_congressional(
            uw_data["congressional"]
        )

        # 5. Risk/Reward Optimization (new component)
        signal_scores["risk_reward_favorability"] = await self._analyze_risk_reward(
            uw_data, symbol
        )

        # 6. Strategy Viability (new component)
        signal_scores["strategy_quality"] = self._analyze_strategy_quality(
            uw_data.get("strategies", [])
        )

        # 7. Multi-Timeframe Alignment (trend confirmation)
        signal_scores["timeframe_alignment"] = await self._analyze_timeframe_alignment(
            symbol
        )

        # 8. Volume Profile Analysis
        signal_scores["volume_profile"] = await self._analyze_volume_profile(
            uw_data, symbol
        )

        return signal_scores

    async def _analyze_discount_opportunity(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> float:
        """
        NEW: Analyze if stock is at a discount (pullback from recent highs).
        Returns score 0-100 (100 = strong discount opportunity).
        """
        try:
            score = 50.0  # Neutral baseline

            # Placeholder: Would fetch real-time price data and technical indicators
            # For now, use options flow sentiment as proxy

            options_flow = uw_data.get("options_flow", [])
            if not options_flow:
                return score

            # Calculate put/call ratio
            call_premium = sum(
                opt.get("premium", 0)
                for opt in options_flow
                if opt.get("option_type") == "call"
            )
            put_premium = sum(
                opt.get("premium", 0)
                for opt in options_flow
                if opt.get("option_type") == "put"
            )

            if call_premium + put_premium == 0:
                return score

            put_call_ratio = put_premium / (call_premium + 1)

            # High put activity might indicate oversold conditions (discount)
            if put_call_ratio > self.discount_thresholds["rsi_oversold"]:
                score += 20

            # Check for support levels (simplified)
            recent_trades = sorted(
                options_flow, key=lambda x: x.get("timestamp", ""), reverse=True
            )[:20]
            if recent_trades:
                avg_price = sum(
                    t.get("stock_price", 0)
                    for t in recent_trades
                    if t.get("stock_price")
                ) / len(recent_trades)
                current_price = recent_trades[0].get("stock_price", 0)

                if current_price and avg_price:
                    pullback_pct = (avg_price - current_price) / avg_price

                    # Score higher if we're at a meaningful pullback
                    if pullback_pct > self.discount_thresholds["pullback_from_high"]:
                        score += 30

            return min(100.0, max(0.0, score))

        except Exception as e:
            logger.error(f"Error analyzing discount opportunity for {symbol}: {str(e)}")
            return 50.0

    def _analyze_options_flow(self, options_flow: List[Dict]) -> float:
        """Analyze options flow sentiment and magnitude."""
        if not options_flow:
            return 50.0  # Neutral

        try:
            # Calculate bullish vs bearish premium
            bullish_premium = 0
            bearish_premium = 0

            for flow in options_flow:
                premium = flow.get("premium", 0)
                opt_type = flow.get("option_type", "").lower()
                sentiment = flow.get("sentiment", "").lower()

                # Bullish: Calls bought, Puts sold
                if (opt_type == "call" and sentiment == "bullish") or (
                    opt_type == "put" and sentiment == "bearish"
                ):
                    bullish_premium += premium
                # Bearish: Calls sold, Puts bought
                elif (opt_type == "call" and sentiment == "bearish") or (
                    opt_type == "put" and sentiment == "bullish"
                ):
                    bearish_premium += premium

            total_premium = bullish_premium + bearish_premium
            if total_premium == 0:
                return 50.0

            # Calculate bullish percentage
            bullish_pct = (bullish_premium / total_premium) * 100

            # Scale to 0-100 score (50 = neutral)
            return bullish_pct

        except Exception as e:
            logger.error(f"Error analyzing options flow: {str(e)}")
            return 50.0

    def _analyze_dark_pool(self, dark_pool: List[Dict]) -> float:
        """Analyze dark pool activity strength."""
        if not dark_pool:
            return 50.0

        try:
            # Analyze dark pool volume and price impact
            total_volume = sum(dp.get("volume", 0) for dp in dark_pool)
            dark_volume = sum(dp.get("dark_pool_volume", 0) for dp in dark_pool)

            if total_volume == 0:
                return 50.0

            dark_pool_pct = (dark_volume / total_volume) * 100

            # Higher dark pool percentage indicates institutional interest
            # Scale: 0-20% dark pool → 30-70 score, >20% → 70-100 score
            if dark_pool_pct < 20:
                score = 30 + (dark_pool_pct / 20) * 40
            else:
                score = 70 + min((dark_pool_pct - 20) / 30 * 30, 30)

            return min(100.0, score)

        except Exception as e:
            logger.error(f"Error analyzing dark pool: {str(e)}")
            return 50.0

    def _analyze_congressional(self, congressional: List[Dict]) -> float:
        """Analyze congressional trading activity."""
        if not congressional:
            return 50.0

        try:
            # Count buys vs sells
            buys = sum(
                1 for trade in congressional if trade.get("type", "").lower() == "buy"
            )
            sells = sum(
                1 for trade in congressional if trade.get("type", "").lower() == "sell"
            )

            total_trades = buys + sells
            if total_trades == 0:
                return 50.0

            # Calculate buy percentage
            buy_pct = (buys / total_trades) * 100

            # Weight by recent trades (last 30 days)
            recent_trades = [
                t for t in congressional if self._is_recent_trade(t, days=30)
            ]
            if recent_trades:
                recent_buys = sum(
                    1 for t in recent_trades if t.get("type", "").lower() == "buy"
                )
                recent_total = len(recent_trades)
                recent_buy_pct = (recent_buys / recent_total) * 100

                # Blend: 60% recent, 40% all-time
                buy_pct = recent_buy_pct * 0.6 + buy_pct * 0.4

            return buy_pct

        except Exception as e:
            logger.error(f"Error analyzing congressional trades: {str(e)}")
            return 50.0

    def _is_recent_trade(self, trade: Dict, days: int = 30) -> bool:
        """Check if trade is within the last N days."""
        try:
            trade_date_str = trade.get("transaction_date", "")
            if not trade_date_str:
                return False

            trade_date = datetime.fromisoformat(trade_date_str.replace("Z", "+00:00"))
            cutoff_date = datetime.now() - timedelta(days=days)

            return trade_date >= cutoff_date

        except Exception:
            return False

    async def _analyze_risk_reward(self, uw_data: Dict[str, Any], symbol: str) -> float:
        """
        NEW: Analyze risk/reward profile based on options strategies and market conditions.
        Returns score 0-100 (100 = excellent risk/reward).
        """
        try:
            score = 50.0

            # Analyze IV percentile (lower IV = better entry for buyers)
            options_flow = uw_data.get("options_flow", [])
            if options_flow:
                iv_values = [opt.get("iv", 0) for opt in options_flow if opt.get("iv")]
                if iv_values:
                    avg_iv = sum(iv_values) / len(iv_values)

                    # Lower IV is better for long options (buying)
                    if avg_iv < 0.30:  # Low IV
                        score += 20
                    elif avg_iv > 0.60:  # High IV (worse for buyers)
                        score -= 10

            # Check for asymmetric opportunities (large upside, limited downside)
            # This is simplified - would integrate with options chain data

            return min(100.0, max(0.0, score))

        except Exception as e:
            logger.error(f"Error analyzing risk/reward for {symbol}: {str(e)}")
            return 50.0

    def _analyze_strategy_quality(self, strategies: List[Dict]) -> float:
        """Analyze quality of available trading strategies."""
        if not strategies:
            return 50.0  # Neutral if no strategies

        try:
            # Score based on strategy characteristics
            total_score = 0
            for strategy in strategies:
                strategy_score = 50.0

                # Higher score for defined-risk strategies
                if strategy.get("max_loss") and strategy.get("max_profit"):
                    risk_reward_ratio = abs(
                        strategy.get("max_profit", 0)
                        / (strategy.get("max_loss", 1) + 1)
                    )

                    if (
                        risk_reward_ratio
                        >= self.risk_reward_params["min_risk_reward_ratio"]
                    ):
                        strategy_score += 30

                # Higher score for lower capital requirement
                capital_req = strategy.get("capital_required", float("inf"))
                if capital_req < 5000:
                    strategy_score += 20

                total_score += strategy_score

            return min(100.0, total_score / len(strategies))

        except Exception as e:
            logger.error(f"Error analyzing strategy quality: {str(e)}")
            return 50.0

    async def _analyze_timeframe_alignment(self, symbol: str) -> float:
        """Analyze if multiple timeframes are aligned."""
        try:
            # Placeholder: Would fetch multi-timeframe trend data
            # For now, return neutral
            return 50.0

        except Exception as e:
            logger.error(f"Error analyzing timeframe alignment for {symbol}: {str(e)}")
            return 50.0

    async def _analyze_volume_profile(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> float:
        """Analyze volume profile and price action."""
        try:
            # Analyze from dark pool and options flow volume
            dark_pool = uw_data.get("dark_pool", [])
            options_flow = uw_data.get("options_flow", [])

            score = 50.0

            # High dark pool activity
            if len(dark_pool) > 10:
                score += 15

            # High options flow activity
            if len(options_flow) > 20:
                score += 15

            # Volume concentration analysis
            if dark_pool:
                volumes = [dp.get("volume", 0) for dp in dark_pool]
                if volumes:
                    avg_volume = sum(volumes) / len(volumes)
                    max_volume = max(volumes)

                    # Volume concentration (high concentration = institutional interest)
                    concentration = max_volume / (avg_volume + 1)
                    if concentration > 3:
                        score += 20

            return min(100.0, score)

        except Exception as e:
            logger.error(f"Error analyzing volume profile for {symbol}: {str(e)}")
            return 50.0

    def _calculate_composite_score(self, signal_scores: Dict[str, float]) -> float:
        """Calculate weighted composite investment score."""
        try:
            composite = 0.0

            for signal_name, weight in self.signal_weights.items():
                score = signal_scores.get(signal_name, 50.0)  # Default to neutral
                composite += score * weight

            return composite

        except Exception as e:
            logger.error(f"Error calculating composite score: {str(e)}")
            return 50.0

    def _generate_recommendation(
        self, composite_score: float, signal_scores: Dict[str, float]
    ) -> str:
        """Generate BUY/HOLD/SELL recommendation based on composite score."""
        try:
            # Thresholds for recommendations
            if composite_score >= 70:
                return "STRONG_BUY"
            elif composite_score >= 60:
                return "BUY"
            elif composite_score >= 40:
                return "HOLD"
            elif composite_score >= 30:
                return "SELL"
            else:
                return "STRONG_SELL"

        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            return "HOLD"

    def _calculate_confidence_level(self, signal_scores: Dict[str, float]) -> str:
        """Calculate confidence level based on signal agreement."""
        try:
            # Calculate standard deviation of signal scores
            scores = list(signal_scores.values())
            if not scores:
                return "low"

            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = variance**0.5

            # Lower std_dev = higher agreement = higher confidence
            if std_dev < self.confidence_thresholds["high_confidence_threshold"]:
                return "high"
            elif std_dev < self.confidence_thresholds["medium_confidence_threshold"]:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Error calculating confidence level: {str(e)}")
            return "low"

    def _extract_key_signals(
        self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]
    ) -> List[str]:
        """Extract the most important signals driving the investment score."""
        try:
            key_signals = []

            # Find top 3 signals by score
            sorted_signals = sorted(
                signal_scores.items(), key=lambda x: abs(x[1] - 50), reverse=True
            )[:3]

            for signal_name, score in sorted_signals:
                if score >= 70:
                    key_signals.append(
                        f"Strong {signal_name.replace('_', ' ')}: {score:.1f}/100"
                    )
                elif score >= 60:
                    key_signals.append(
                        f"Moderate {signal_name.replace('_', ' ')}: {score:.1f}/100"
                    )
                elif score <= 30:
                    key_signals.append(
                        f"Weak {signal_name.replace('_', ' ')}: {score:.1f}/100"
                    )

            # Add data-driven insights
            options_flow = uw_data.get("options_flow", [])
            if options_flow:
                total_premium = sum(opt.get("premium", 0) for opt in options_flow)
                key_signals.append(f"Options flow: ${total_premium:,.0f} premium")

            dark_pool = uw_data.get("dark_pool", [])
            if dark_pool:
                total_dark_volume = sum(
                    dp.get("dark_pool_volume", 0) for dp in dark_pool
                )
                key_signals.append(f"Dark pool: {total_dark_volume:,.0f} shares")

            congressional = uw_data.get("congressional", [])
            if congressional:
                buys = sum(
                    1 for t in congressional if t.get("type", "").lower() == "buy"
                )
                sells = sum(
                    1 for t in congressional if t.get("type", "").lower() == "sell"
                )
                key_signals.append(f"Congressional: {buys} buys, {sells} sells")

            return key_signals

        except Exception as e:
            logger.error(f"Error extracting key signals: {str(e)}")
            return []

    def _assess_risk_factors(
        self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Assess key risk factors for the investment."""
        try:
            risk_analysis = {
                "overall_risk_level": "moderate",
                "risk_factors": [],
                "mitigating_factors": [],
            }

            # Calculate overall risk
            risk_score = 50.0  # Baseline

            # High options flow volatility = higher risk
            options_flow = uw_data.get("options_flow", [])
            if options_flow:
                iv_values = [opt.get("iv", 0) for opt in options_flow if opt.get("iv")]
                if iv_values:
                    avg_iv = sum(iv_values) / len(iv_values)
                    if avg_iv > 0.60:
                        risk_score += 20
                        risk_analysis["risk_factors"].append(
                            "High implied volatility (IV > 60%)"
                        )

            # Low liquidity = higher risk
            if len(options_flow) < 5:
                risk_score += 15
                risk_analysis["risk_factors"].append("Limited options flow data")

            # Congressional selling = potential risk
            congressional = uw_data.get("congressional", [])
            if congressional:
                sells = sum(
                    1 for t in congressional if t.get("type", "").lower() == "sell"
                )
                if sells > len(congressional) * 0.6:
                    risk_score += 10
                    risk_analysis["risk_factors"].append(
                        "Majority of congressional trades are sells"
                    )

            # Mitigating factors
            if signal_scores.get("dark_pool_strength", 0) > 70:
                risk_score -= 10
                risk_analysis["mitigating_factors"].append(
                    "Strong institutional interest (dark pool)"
                )

            if signal_scores.get("discount_opportunity", 0) > 70:
                risk_score -= 15
                risk_analysis["mitigating_factors"].append(
                    "Stock at significant discount"
                )

            # Determine overall risk level
            if risk_score > 70:
                risk_analysis["overall_risk_level"] = "high"
            elif risk_score > 50:
                risk_analysis["overall_risk_level"] = "moderate"
            else:
                risk_analysis["overall_risk_level"] = "low"

            return risk_analysis

        except Exception as e:
            logger.error(f"Error assessing risk factors: {str(e)}")
            return {
                "overall_risk_level": "unknown",
                "risk_factors": [f"Error: {str(e)}"],
                "mitigating_factors": [],
            }

    def _analyze_options_sentiment(self, options_data: List[Dict]) -> float:
        """Analyze options flow to determine bullish/bearish sentiment."""
        if not options_data:
            return 50.0  # Neutral score

        bullish_count = sum(
            1 for opt in options_data if opt.get("sentiment", "").lower() == "bullish"
        )
        bearish_count = sum(
            1 for opt in options_data if opt.get("sentiment", "").lower() == "bearish"
        )
        total_premium = sum(opt.get("premium", 0) for opt in options_data)

        if bullish_count + bearish_count == 0:
            return 50.0

        # Weight by premium volume - larger premiums have more significance
        bullish_premium = sum(
            opt.get("premium", 0)
            for opt in options_data
            if opt.get("sentiment", "").lower() == "bullish"
        )

        # Sentiment ratio weighted by premium
        sentiment_ratio = bullish_count / (bullish_count + bearish_count)
        premium_ratio = (
            bullish_premium / max(total_premium, 1) if total_premium > 0 else 0.5
        )

        # Combine count and premium weighting
        combined_sentiment = sentiment_ratio * 0.4 + premium_ratio * 0.6

        # Scale to 0-100 with premium volume boost
        base_score = combined_sentiment * 100

        # Boost for high premium volume (institutional interest)
        if total_premium > 5000000:  # $5M+ total premium
            base_score = min(100, base_score * 1.1)

        return round(base_score, 1)

    def _analyze_dark_pool_sentiment(self, dark_pool_data: List[Dict]) -> float:
        """Analyze dark pool activity for institutional sentiment."""
        if not dark_pool_data:
            return 50.0  # Neutral

        # High dark pool percentage suggests institutional accumulation
        avg_dark_percentage = statistics.mean(
            [dp.get("dark_percentage", 0) for dp in dark_pool_data]
        )
        total_dark_volume = sum(dp.get("dark_volume", 0) for dp in dark_pool_data)

        # Score based on dark pool percentage (higher = more bullish institutional activity)
        percentage_score = min(
            100, avg_dark_percentage * 1.5
        )  # Scale up since 60%+ is high

        # Volume significance boost
        volume_multiplier = 1.0
        if total_dark_volume > 1000000:  # 1M+ shares
            volume_multiplier = 1.2
        elif total_dark_volume > 5000000:  # 5M+ shares
            volume_multiplier = 1.4

        return round(min(100, percentage_score * volume_multiplier), 1)

    def _analyze_congressional_sentiment(self, congressional_data: List[Dict]) -> float:
        """Analyze congressional trading activity for insider sentiment."""
        if not congressional_data:
            return 50.0  # Neutral

        purchases = [
            trade
            for trade in congressional_data
            if "purchase" in trade.get("transaction_type", "").lower()
        ]
        sales = [
            trade
            for trade in congressional_data
            if "sale" in trade.get("transaction_type", "").lower()
        ]

        if not purchases and not sales:
            return 50.0

        # Weight by transaction amounts
        purchase_amount = sum(trade.get("transaction_amount", 0) for trade in purchases)
        sale_amount = sum(trade.get("transaction_amount", 0) for trade in sales)
        total_amount = purchase_amount + sale_amount

        if total_amount == 0:
            return 50.0

        # Calculate purchase ratio
        purchase_ratio = purchase_amount / total_amount

        # Recent activity boost (last 30 days gets higher weight)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_trades = [
            trade
            for trade in congressional_data
            if self._parse_date(trade.get("transaction_date", "")) > recent_cutoff
        ]

        recency_boost = 1.0
        if len(recent_trades) > 0:
            recency_boost = 1.3

        # Scale to 0-100
        base_score = purchase_ratio * 100 * recency_boost

        return round(min(100, base_score), 1)

    def _analyze_ai_strategies_confidence(self, strategies_data: List[Dict]) -> float:
        """Analyze AI-generated trading strategies confidence."""
        if not strategies_data:
            return 50.0  # Neutral when no strategies

        # Extract confidence levels from strategies
        confidences = []
        bullish_strategies = 0

        for strategy in strategies_data:
            confidence = strategy.get("confidence", 0.5)
            confidences.append(confidence)

            # Check if strategy is bullish (calls, long positions, etc.)
            strategy_type = strategy.get("strategy_name", "").lower()
            if any(
                bullish_term in strategy_type
                for bullish_term in ["long", "call", "bull"]
            ):
                bullish_strategies += 1

        if not confidences:
            return 50.0

        # Average confidence scaled to 0-100
        avg_confidence = statistics.mean(confidences)
        confidence_score = avg_confidence * 100

        # Boost for predominantly bullish strategies
        if len(strategies_data) > 0:
            bullish_ratio = bullish_strategies / len(strategies_data)
            if bullish_ratio > 0.6:  # 60%+ bullish strategies
                confidence_score *= 1.2

        return round(min(100, confidence_score), 1)

    def _analyze_market_momentum(self, options_data: List[Dict]) -> float:
        """Analyze market momentum from options flow patterns."""
        if not options_data:
            return 50.0

        # Look for momentum indicators in options data
        short_term_dte = [
            opt for opt in options_data if opt.get("dte", 365) <= 7
        ]  # Weekly options
        high_volume = [opt for opt in options_data if opt.get("volume", 0) > 1000]

        momentum_score = 50.0  # Base neutral

        # Short-term options activity suggests momentum
        if len(short_term_dte) > len(options_data) * 0.3:  # 30%+ short-term
            momentum_score += 15

            # High volume suggests strong momentum
        if len(high_volume) > len(options_data) * 0.4:  # 40%+ high volume
            momentum_score += 15

        # Opening vs closing positions (opening suggests new momentum)
        opening_positions = sum(
            1 for opt in options_data if opt.get("is_opener", False)
        )
        if opening_positions > len(options_data) * 0.5:  # 50%+ opening
            momentum_score += 10

        return round(min(100, momentum_score), 1)

    async def _analyze_discount_opportunity_old(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> float:
        """
        Analyze if stock is in discount phase vs premium phase.
        Higher score = better discount opportunity (near support, oversold, etc.)
        """
        discount_score = 50.0  # Start neutral

        # Get mock technical data (in real implementation, fetch from API)
        technical_data = self._get_mock_technical_data(symbol)

        discount_factors = []

        # 1. RSI Analysis (30% weight)
        rsi = technical_data.get("rsi", 50)
        if rsi <= self.discount_thresholds["rsi_oversold"]:
            rsi_score = 100 - rsi  # Lower RSI = higher discount score
            discount_factors.append(("rsi_oversold", rsi_score, 0.3))
        elif rsi >= self.premium_thresholds["rsi_overbought"]:
            rsi_score = max(0, 100 - rsi)  # Heavily penalize overbought
            discount_factors.append(("rsi_overbought", rsi_score, 0.3))
        else:
            # Neutral zone - slight preference for lower RSI
            rsi_score = 50 + (50 - rsi) * 0.5
            discount_factors.append(("rsi_neutral", rsi_score, 0.3))

        # 2. Support/Resistance Distance Analysis (25% weight)
        support_distance = technical_data.get("support_distance_pct", 10)
        resistance_distance = technical_data.get("resistance_distance_pct", 10)

        if support_distance <= self.discount_thresholds["support_distance"]:
            # Near support = discount opportunity
            support_score = 100 - (support_distance * 10)  # Closer = higher score
            discount_factors.append(("near_support", support_score, 0.25))
        elif resistance_distance <= self.premium_thresholds["resistance_distance"]:
            # Near resistance = premium/risky
            resistance_score = max(
                0, 30 - resistance_distance * 5
            )  # Penalty for near resistance
            discount_factors.append(("near_resistance", resistance_score, 0.25))
        else:
            # Middle range - neutral
            mid_score = 50
            discount_factors.append(("mid_range", mid_score, 0.25))

        # 3. Recent Price Action Analysis (25% weight)
        recent_change = technical_data.get("recent_30d_change_pct", 0)
        if recent_change <= self.discount_thresholds["pullback_threshold"]:
            # Significant pullback = discount opportunity
            pullback_score = min(
                100, 70 + abs(recent_change) * 2
            )  # Bigger pullback = better discount
            discount_factors.append(("pullback_discount", pullback_score, 0.25))
        elif recent_change >= self.premium_thresholds["rally_threshold"]:
            # Strong rally = premium/extended
            rally_score = max(
                0, 50 - recent_change * 1.5
            )  # Penalty for extended rallies
            discount_factors.append(("rally_premium", rally_score, 0.25))
        else:
            # Moderate movement - neutral to positive
            moderate_score = 55
            discount_factors.append(("moderate_move", moderate_score, 0.25))

        # 4. Options Flow Confirmation (20% weight)
        options_data = uw_data["options_flow"]
        if options_data:
            # Look for contrarian opportunities
            put_call_ratio = self._calculate_put_call_ratio(options_data)
            if put_call_ratio > 1.5:  # High fear = discount opportunity
                fear_score = min(100, 60 + put_call_ratio * 15)
                discount_factors.append(("fear_discount", fear_score, 0.2))
            elif put_call_ratio < 0.5:  # Excessive optimism = premium warning
                greed_score = max(0, 40 - (1 - put_call_ratio) * 30)
                discount_factors.append(("greed_premium", greed_score, 0.2))
            else:
                balanced_score = 50
                discount_factors.append(("balanced_sentiment", balanced_score, 0.2))

        # Calculate weighted discount score
        if discount_factors:
            weighted_score = sum(
                score * weight for _, score, weight in discount_factors
            )
            discount_score = weighted_score

        # Log the analysis for transparency
        logger.info(
            f"Discount analysis for {symbol}: Score={discount_score:.1f}, Factors={len(discount_factors)}"
        )

        return round(min(100, max(0, discount_score)), 1)

    async def _calculate_risk_reward_score(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> float:
        """
        Calculate risk/reward ratio score for optimal entries.
        Higher score = better risk/reward setup.
        """
        technical_data = self._get_mock_technical_data(symbol)

        current_price = technical_data.get("current_price", 100)
        support_level = technical_data.get("support_level", current_price * 0.9)
        resistance_level = technical_data.get("resistance_level", current_price * 1.1)

        # Calculate risk and reward
        risk = max(0.01, current_price - support_level)  # Risk to support
        reward = max(0.01, resistance_level - current_price)  # Reward to resistance

        risk_reward_ratio = reward / risk

        # Score based on risk/reward ratio
        if risk_reward_ratio >= self.risk_reward_params["min_reward_ratio"]:
            # Good risk/reward ratio
            ratio_score = min(100, 50 + (risk_reward_ratio - 2) * 15)
        else:
            # Poor risk/reward ratio
            ratio_score = max(0, 50 - (2 - risk_reward_ratio) * 20)

        # Penalty for excessive risk percentage
        risk_percentage = (risk / current_price) * 100
        if risk_percentage > self.risk_reward_params["max_risk_percentage"]:
            risk_penalty = (risk_percentage - 8) * 5
            ratio_score = max(0, ratio_score - risk_penalty)

        logger.info(
            f"Risk/Reward for {symbol}: Ratio={risk_reward_ratio:.2f}, Score={ratio_score:.1f}"
        )

        return round(ratio_score, 1)

    async def _calculate_premium_penalty(
        self, uw_data: Dict[str, Any], symbol: str
    ) -> float:
        """
        Calculate penalty score for premium/overextended stocks.
        Lower score = higher penalty for premium stocks.
        """
        technical_data = self._get_mock_technical_data(symbol)

        penalty_score = 100.0  # Start with no penalty

        penalties = []

        # 1. Overbought RSI penalty
        rsi = technical_data.get("rsi", 50)
        if rsi >= self.premium_thresholds["rsi_overbought"]:
            overbought_penalty = (rsi - 70) * 2  # Escalating penalty
            penalties.append(("overbought_rsi", overbought_penalty))

        # 2. Near resistance penalty
        resistance_distance = technical_data.get("resistance_distance_pct", 10)
        if resistance_distance <= self.premium_thresholds["resistance_distance"]:
            resistance_penalty = (3 - resistance_distance) * 10
            penalties.append(("near_resistance", resistance_penalty))

        # 3. Extended rally penalty
        recent_change = technical_data.get("recent_30d_change_pct", 0)
        if recent_change >= self.premium_thresholds["rally_threshold"]:
            rally_penalty = (recent_change - 20) * 1.5
            penalties.append(("extended_rally", rally_penalty))

        # 4. High volume at resistance penalty (distribution signs)
        if technical_data.get("volume_at_resistance", False):
            volume_penalty = 15
            penalties.append(("distribution_volume", volume_penalty))

        # Apply penalties
        total_penalty = sum(penalty for _, penalty in penalties)
        penalty_score = max(0, 100 - total_penalty)

        logger.info(
            f"Premium penalty for {symbol}: Penalties={len(penalties)}, Score={penalty_score:.1f}"
        )

        return round(penalty_score, 1)

    def _get_mock_technical_data(self, symbol: str) -> Dict[str, Any]:
        """
        Mock technical data for different symbols.
        In production, this would fetch real technical analysis data.
        """
        # Mock data simulating different market conditions
        mock_data = {
            "AAPL": {
                "current_price": 231.59,
                "rsi": 71.1,  # Overbought
                "support_level": 196.64,
                "resistance_level": 234.28,
                "support_distance_pct": 15.1,
                "resistance_distance_pct": 1.2,  # Near resistance - premium
                "recent_30d_change_pct": 12.5,
                "volume_at_resistance": True,
            },
            "MSFT": {
                "current_price": 520.17,
                "rsi": 55.0,  # Neutral
                "support_level": 469.66,
                "resistance_level": 532.70,
                "support_distance_pct": 9.7,
                "resistance_distance_pct": 2.4,
                "recent_30d_change_pct": 8.2,
                "volume_at_resistance": False,
            },
            "NVDA": {
                "current_price": 142.50,
                "rsi": 28.5,  # Oversold - discount opportunity
                "support_level": 135.00,
                "resistance_level": 165.00,
                "support_distance_pct": 5.3,  # Near support - discount
                "resistance_distance_pct": 15.8,
                "recent_30d_change_pct": -18.5,  # Pullback - discount
                "volume_at_resistance": False,
            },
            "TSLA": {
                "current_price": 330.56,
                "rsi": 54.2,  # Neutral
                "support_level": 293.21,
                "resistance_level": 345.26,
                "support_distance_pct": 11.3,
                "resistance_distance_pct": 4.4,
                "recent_30d_change_pct": 5.8,
                "volume_at_resistance": False,
            },
        }

        # Return specific data or default neutral data
        return mock_data.get(
            symbol,
            {
                "current_price": 100,
                "rsi": 50,
                "support_level": 90,
                "resistance_level": 110,
                "support_distance_pct": 10,
                "resistance_distance_pct": 10,
                "recent_30d_change_pct": 0,
                "volume_at_resistance": False,
            },
        )

    def _calculate_put_call_ratio(self, options_data: List[Dict]) -> float:
        """Calculate put/call ratio from options flow data."""
        if not options_data:
            return 1.0  # Neutral

        puts = sum(
            1 for opt in options_data if "put" in opt.get("option_type", "").lower()
        )
        calls = sum(
            1 for opt in options_data if "call" in opt.get("option_type", "").lower()
        )

        if calls == 0:
            return 2.0  # High fear

        return puts / calls

    def _calculate_composite_score_old(self, signal_scores: Dict[str, float]) -> float:
        """Calculate weighted composite investment score."""
        composite = 0.0

        for signal_type, score in signal_scores.items():
            weight = self.signal_weights.get(signal_type, 0.0)
            composite += score * weight

        return round(min(100, max(0, composite)), 1)

    def _generate_recommendation_old(
        self, composite_score: float, signal_scores: Dict[str, float]
    ) -> str:
        """Generate investment recommendation based on composite score and discount/premium analysis."""

        # Get key factors for context
        discount_score = signal_scores.get("discount_opportunity", 50)
        premium_penalty = signal_scores.get("premium_penalty", 100)
        risk_reward_score = signal_scores.get("risk_reward_ratio", 50)

        # Enhanced recommendation logic
        if composite_score >= 75 and discount_score >= 65:
            return "STRONG BUY - DISCOUNT OPPORTUNITY"
        elif composite_score >= 65 and discount_score >= 55:
            return "BUY - GOOD ENTRY"
        elif composite_score >= 55 and risk_reward_score >= 60:
            return "HOLD+ - DECENT SETUP"
        elif composite_score >= 45:
            return "HOLD - WAIT FOR BETTER ENTRY"
        elif composite_score >= 35 or premium_penalty < 40:
            return "HOLD- - AVOID PREMIUM LEVELS"
        elif composite_score >= 25:
            return "SELL - WEAK FUNDAMENTALS"
        else:
            return "STRONG SELL - POOR OPPORTUNITY"

    def _calculate_confidence_level_old(self, signal_scores: Dict[str, float]) -> str:
        """Calculate confidence level based on signal consistency."""
        scores = list(signal_scores.values())
        if not scores:
            return "low"

        # Check consistency of signals
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        avg_score = statistics.mean(scores)

        # High confidence: consistent signals with good average
        if score_std < 15 and (avg_score > 65 or avg_score < 35):
            return "high"
        elif score_std < 25:
            return "medium"
        else:
            return "low"

    def _extract_key_signals_old(
        self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Extract the most significant signals for display."""
        key_signals = []

        # Find top 3 signals by score
        sorted_signals = sorted(
            signal_scores.items(), key=lambda x: abs(x[1] - 50), reverse=True
        )

        for signal_type, score in sorted_signals[:3]:
            signal_info = {
                "type": signal_type,
                "score": score,
                "strength": (
                    "strong"
                    if abs(score - 50) > 20
                    else "moderate" if abs(score - 50) > 10 else "weak"
                ),
                "direction": (
                    "bullish" if score > 50 else "bearish" if score < 50 else "neutral"
                ),
            }

            # Add specific details based on signal type
            if signal_type == "options_flow":
                options_count = len(uw_data["options_flow"])
                signal_info["details"] = f"{options_count} options flow alerts analyzed"
            elif signal_type == "dark_pool":
                dp_count = len(uw_data["dark_pool"])
                signal_info["details"] = f"{dp_count} dark pool trades analyzed"
            elif signal_type == "congressional":
                cong_count = len(uw_data["congressional"])
                signal_info["details"] = f"{cong_count} congressional trades analyzed"
            elif signal_type == "ai_strategies":
                signal_info["details"] = "AI strategies analysis (placeholder)"

            key_signals.append(signal_info)

        return key_signals

    def _assess_risk_factors_old(
        self, uw_data: Dict[str, Any], signal_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Assess various risk factors."""
        risk_factors = []
        overall_risk = "medium"  # Default

        # High volatility indicators from options
        options_data = uw_data["options_flow"]
        if options_data:
            short_dte_count = sum(1 for opt in options_data if opt.get("dte", 365) <= 3)
            if short_dte_count > len(options_data) * 0.4:
                risk_factors.append(
                    "High short-term options activity suggests volatility"
                )

        # Signal inconsistency
        scores = list(signal_scores.values())
        if len(scores) > 1:
            score_range = max(scores) - min(scores)
            if score_range > 40:
                risk_factors.append("Mixed signals across data sources")

        # Determine overall risk level
        risk_score = signal_scores.get("risk_assessment", 50)
        if risk_score < 30:
            overall_risk = "high"
        elif risk_score > 70:
            overall_risk = "low"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "risk_score": risk_score,
        }

    def _parse_date(self, date_string: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except:
            return datetime.now() - timedelta(days=365)  # Default to old date

    # Additional utility methods for future enhancements
    async def get_batch_scores(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Generate investment scores for multiple symbols efficiently."""
        tasks = [self.generate_investment_score(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            symbol: (
                result if not isinstance(result, Exception) else {"error": str(result)}
            )
            for symbol, result in zip(symbols, results)
        }

    def get_scoring_explanation(self) -> Dict[str, str]:
        """Return explanation of enhanced discount/premium scoring methodology for transparency."""
        return {
            "discount_opportunity": "Identifies stocks in discount phase using RSI, support levels, pullbacks, and contrarian sentiment analysis",
            "options_flow": "Analyzes options trading sentiment and premium volume to gauge market sentiment",
            "dark_pool": "Evaluates institutional activity through dark pool trading percentages and volumes",
            "congressional": "Tracks congressional insider trading activity and timing for insider sentiment",
            "risk_reward_ratio": "Calculates optimal risk/reward setups based on support/resistance levels and position sizing",
            "market_momentum": "Assesses short-term momentum indicators from options flow patterns",
            "premium_penalty": "Applies penalties for overextended stocks near resistance or in overbought conditions",
            "discount_methodology": "Prioritizes stocks with: RSI <30 (oversold), <5% from support, recent pullbacks >10%, high put/call ratios",
            "premium_avoidance": "Penalizes stocks with: RSI >70 (overbought), <3% from resistance, rallies >20%, distribution volume",
            "risk_management": "Ensures minimum 2:1 reward/risk ratio with maximum 8% risk from entry point",
            "composite_methodology": "Weighted scoring heavily favoring discount opportunities (35%) over premium momentum plays",
        }


# Global instance
investment_scoring_agent = InvestmentScoringAgent()
