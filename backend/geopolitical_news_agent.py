"""
FlowMind - Geopolitical & Macro News Intelligence Agent

Aggregates news from multiple sources:
- Macro events (Fed, geopolitical, economic data)
- Ticker-specific news with AI sentiment analysis
- Integration with Investment Scoring (FIS)
- Options strategy recommendations based on news

Three-level analysis:
1. MACRO: Global market events
2. MICRO: Per-ticker news + sentiment
3. INTEGRATION: Stocks + Options + News combined insights
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class GeopoliticalNewsAgent:
    """
    Aggregates and interprets geopolitical & macro news
    Provides portfolio-level and ticker-level intelligence
    """

    def __init__(self, uw_client=None):
        """
        Initialize with Unusual Whales client for news data
        """
        self.uw_client = uw_client

    async def get_macro_news(self) -> Dict:
        """
        Get global macro events and their market impact

        Returns:
        {
        "fed_policy": {...},
        "geopolitical": {...},
        "economic_data": {...},
        "market_sentiment": float # -1 to +1
        }
        """
        try:
            # TODO: Integrate real data sources
            # For now, return structured demo data

            macro_events = {
                "fed_policy": {
                    "title": "Fed Holds Rates Steady",
                    "latest": "Fed maintains rates at 5.25-5.50%",
                    "impact": "Neutral to slightly bearish for growth stocks",
                    "affected_sectors": ["Technology", "Real Estate", "Utilities"],
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "source": "Federal Reserve",
                },
                "geopolitical": {
                    "title": "Geopolitical Tensions Monitor",
                    "latest": "Middle East tensions remain elevated",
                    "impact": "Oil prices volatile, flight to safety continues",
                    "affected_tickers": ["XLE", "USO", "GLD", "TLT"],
                    "severity": "high",
                    "timestamp": datetime.now().isoformat(),
                    "source": "Reuters",
                },
                "economic_data": {
                    "title": "Latest Economic Indicators",
                    "latest": "CPI +3.2% YoY (expected 3.0%)",
                    "impact": "Inflation concerns persist, may delay rate cuts",
                    "affected_sectors": ["All"],
                    "severity": "high",
                    "timestamp": datetime.now().isoformat(),
                    "source": "Bureau of Labor Statistics",
                },
                "market_sentiment": 0.15,  # Slightly bullish overall
                "vix_level": 18.5,
                "fear_greed_index": 52,  # Neutral
            }

            return macro_events

        except Exception as e:
            logger.error(f"Failed to fetch macro news: {e}")
            return self._get_fallback_macro_news()

    async def get_ticker_news_with_sentiment(
        self, symbol: str, include_fis: bool = True, include_options: bool = True
    ) -> Dict:
        """
        Get ticker-specific news with AI sentiment analysis
        Optionally include Investment Scoring and Options suggestions

        Args:
        symbol: Stock ticker (e.g., "TSLA")
        include_fis: Include FIS score
        include_options: Include options strategy suggestions

        Returns:
        {
        "symbol": str,
        "news_items": [...],
        "aggregate_sentiment": float, # -1 to +1
        "sentiment_label": str, # "Very Bearish" to "Very Bullish"
        "impact_level": int, # 0 to 100
        "fis_score": Optional[int],
        "options_suggestions": Optional[List],
        "trading_recommendation": str
        }
        """
        try:
            # Fetch news from Unusual Whales
            news_items = []
            if self.uw_client:
                try:
                    uw_news = await self.uw_client.get_news(symbol)
                    news_items = uw_news.get("items", [])
                except Exception as e:
                    logger.warning(f"UW news fetch failed for {symbol}: {e}")

            # If no news, use demo data
            if not news_items:
                news_items = self._get_demo_news(symbol)

            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment(news_items)
            sentiment_label = self._sentiment_to_label(sentiment_score)

            # Calculate impact level
            impact_level = self._calculate_impact_level(news_items, sentiment_score)

            result = {
                "symbol": symbol,
                "news_items": news_items[:10],  # Top 10 news items
                "aggregate_sentiment": sentiment_score,
                "sentiment_label": sentiment_label,
                "impact_level": impact_level,
                "last_updated": datetime.now().isoformat(),
            }

            # Add Investment Scoring if requested
            if include_fis:
                result["fis_score"] = await self._get_fis_score(symbol)

            # Add options suggestions if requested
            if include_options:
                result["options_suggestions"] = await self._get_options_suggestions(
                    symbol, sentiment_score
                )

            # Generate trading recommendation
            result["trading_recommendation"] = self._generate_recommendation(
                sentiment_score, result.get("fis_score"), impact_level
            )

            return result

        except Exception as e:
            logger.error(f"Failed to get ticker news for {symbol}: {e}")
            return self._get_fallback_ticker_news(symbol)

    async def get_portfolio_news_digest(
        self, mindfolio_id: str, positions: List[Dict]
    ) -> Dict:
        """
        Aggregated news intelligence for entire portfolio

        Args:
        mindfolio_id: Portfolio ID
        positions: List of positions with symbol, quantity, etc.

        Returns:
        {
        "macro_events": {...},
        "ticker_news": {...},
        "risk_alerts": [...],
        "opportunities": [...],
        "portfolio_sentiment": float,
        "news_summary": str
        }
        """
        try:
            # Get macro events
            macro_events = await self.get_macro_news()

            # Get news for each ticker in portfolio
            ticker_news = {}
            risk_alerts = []
            opportunities = []

            for position in positions:
                symbol = position.get("symbol")
                if not symbol:
                    continue

                # Get ticker news with full integration
                ticker_intel = await self.get_ticker_news_with_sentiment(
                    symbol, include_fis=True, include_options=True
                )

                ticker_news[symbol] = ticker_intel

                # Generate risk alerts for significant negative news
                if ticker_intel["aggregate_sentiment"] < -0.5:
                    risk_alerts.append(
                        {
                            "symbol": symbol,
                            "severity": (
                                "high"
                                if ticker_intel["aggregate_sentiment"] < -0.7
                                else "medium"
                            ),
                            "alert": f"Significant negative news detected for {symbol}",
                            "sentiment": ticker_intel["aggregate_sentiment"],
                            "recommendation": "Review position - consider protective puts or reduce exposure",
                            "urgency": "high",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                # Generate opportunity alerts for positive news
                if ticker_intel["aggregate_sentiment"] > 0.6:
                    opportunities.append(
                        {
                            "symbol": symbol,
                            "type": "bullish_news",
                            "alert": f"Strong positive momentum for {symbol}",
                            "sentiment": ticker_intel["aggregate_sentiment"],
                            "suggestion": ticker_intel.get("options_suggestions", []),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # Calculate portfolio-wide sentiment
            portfolio_sentiment = self._calculate_portfolio_sentiment(ticker_news)

            # Generate executive summary
            news_summary = self._generate_portfolio_summary(
                macro_events, ticker_news, risk_alerts, opportunities
            )

            return {
                "mindfolio_id": mindfolio_id,
                "macro_events": macro_events,
                "ticker_news": ticker_news,
                "risk_alerts": risk_alerts,
                "opportunities": opportunities,
                "portfolio_sentiment": portfolio_sentiment,
                "news_summary": news_summary,
                "total_news_items": sum(
                    len(t.get("news_items", [])) for t in ticker_news.values()
                ),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to generate portfolio digest: {e}")
            return self._get_fallback_portfolio_digest(mindfolio_id)

    # ========== HELPER METHODS ==========

    def _calculate_sentiment(self, news_items: List[Dict]) -> float:
        """Calculate aggregate sentiment from news items (-1 to +1)"""
        if not news_items:
            return 0.0

        # Simple sentiment scoring based on keywords
        # In production, use NLP/LLM for better accuracy
        positive_keywords = [
            "beat",
            "surge",
            "gain",
            "up",
            "profit",
            "growth",
            "strong",
            "upgrade",
        ]
        negative_keywords = [
            "miss",
            "fall",
            "down",
            "loss",
            "weak",
            "concern",
            "probe",
            "downgrade",
        ]

        total_score = 0
        for item in news_items:
            headline = item.get("headline", "").lower()

            pos_count = sum(1 for kw in positive_keywords if kw in headline)
            neg_count = sum(1 for kw in negative_keywords if kw in headline)

            total_score += pos_count - neg_count

        # Normalize to -1 to +1
        max_score = len(news_items) * 3  # Max 3 keywords per headline
        sentiment = max(-1.0, min(1.0, total_score / max_score if max_score > 0 else 0))

        return round(sentiment, 2)

    def _sentiment_to_label(self, sentiment: float) -> str:
        """Convert sentiment score to human-readable label"""
        if sentiment > 0.7:
            return "Very Bullish"
        elif sentiment > 0.3:
            return "Bullish"
        elif sentiment > -0.3:
            return "Neutral"
        elif sentiment > -0.7:
            return "Bearish"
        else:
            return "Very Bearish"

    def _calculate_impact_level(self, news_items: List[Dict], sentiment: float) -> int:
        """Calculate news impact level (0-100)"""
        # More news items = higher impact
        # Stronger sentiment = higher impact
        news_count_factor = min(100, len(news_items) * 10)
        sentiment_factor = abs(sentiment) * 100

        impact = int((news_count_factor + sentiment_factor) / 2)
        return min(100, max(0, impact))

    async def _get_fis_score(self, symbol: str) -> Optional[int]:
        """Get Investment Scoring (FIS) score for ticker"""
        try:
            # TODO: Integrate with actual Investment Scoring Agent
            # For now, return demo scores
            demo_scores = {
                "TSLA": 85,
                "AAPL": 72,
                "NVDA": 88,
                "SPY": 75,
                "MSFT": 80,
                "AMD": 70,
            }
            return demo_scores.get(symbol, 65)
        except Exception as e:
            logger.error(f"Failed to get FIS score for {symbol}: {e}")
            return None

    async def _get_options_suggestions(
        self, symbol: str, sentiment: float
    ) -> List[Dict]:
        """Get options strategy suggestions based on news sentiment"""
        suggestions = []

        if sentiment > 0.6:  # Very bullish
            suggestions.append(
                {
                    "strategy": "Sell Cash-Secured Put",
                    "rationale": "Strong positive news - enter at discount via CSP",
                    "strikes": "At-the-money or slightly OTM",
                    "dte": "30-45 days",
                }
            )
            suggestions.append(
                {
                    "strategy": "Bull Call Spread",
                    "rationale": "Capitalize on upward momentum with defined risk",
                    "strikes": "ATM long + OTM short",
                    "dte": "30-60 days",
                }
            )
        elif sentiment > 0.2:  # Moderately bullish
            suggestions.append(
                {
                    "strategy": "Covered Call (if holding stock)",
                    "rationale": "Generate income while maintaining upside exposure",
                    "strikes": "Slightly OTM (delta 0.30)",
                    "dte": "30-45 days",
                }
            )
        elif sentiment < -0.6:  # Very bearish
            suggestions.append(
                {
                    "strategy": "Protective Put",
                    "rationale": "Hedge against downside risk from negative news",
                    "strikes": "5-10% OTM",
                    "dte": "30-60 days",
                }
            )
            suggestions.append(
                {
                    "strategy": "Reduce Exposure",
                    "rationale": "Consider trimming position size",
                    "strikes": "N/A",
                    "dte": "N/A",
                }
            )
        else:  # Neutral
            suggestions.append(
                {
                    "strategy": "Iron Condor",
                    "rationale": "Profit from range-bound movement",
                    "strikes": "OTM on both sides",
                    "dte": "30-45 days",
                }
            )

        return suggestions

    def _generate_recommendation(
        self, sentiment: float, fis_score: Optional[int], impact_level: int
    ) -> str:
        """Generate trading recommendation based on all factors"""

        # High impact negative news
        if sentiment < -0.5 and impact_level > 70:
            return " High risk - Consider protective measures or reduce exposure"

        # Strong positive news + good FIS
        if sentiment > 0.6 and (fis_score or 0) > 75:
            return " Strong buy signal - Consider adding to position or selling CSP for entry"

        # Good FIS but negative news
        if (fis_score or 0) > 75 and sentiment < -0.3:
            return " Opportunity - Good fundamentals with temporary negative sentiment. Consider CSP entry."

        # Positive news but weak fundamentals
        if sentiment > 0.5 and (fis_score or 0) < 60:
            return " Momentum play - Consider short-term options, avoid long-term hold"

        # Default
        return " Hold - Monitor for clearer signals"

    def _calculate_portfolio_sentiment(self, ticker_news: Dict) -> float:
        """Calculate weighted average sentiment for entire portfolio"""
        if not ticker_news:
            return 0.0

        total_sentiment = sum(t["aggregate_sentiment"] for t in ticker_news.values())
        return round(total_sentiment / len(ticker_news), 2)

    def _generate_portfolio_summary(
        self,
        macro_events: Dict,
        ticker_news: Dict,
        risk_alerts: List,
        opportunities: List,
    ) -> str:
        """Generate executive summary of portfolio news"""

        summary_parts = []

        # Macro summary
        if macro_events.get("severity") == "high":
            summary_parts.append(f" High-impact macro events detected.")

        # Risk alerts
        if len(risk_alerts) > 0:
            summary_parts.append(
                f"🚨 {len(risk_alerts)} risk alert(s) require attention."
            )

        # Opportunities
        if len(opportunities) > 0:
            summary_parts.append(
                f" {len(opportunities)} bullish opportunity(ies) identified."
            )

        # Overall sentiment
        total_sentiment = sum(t["aggregate_sentiment"] for t in ticker_news.values())
        avg_sentiment = total_sentiment / len(ticker_news) if ticker_news else 0

        if avg_sentiment > 0.3:
            summary_parts.append(" Overall portfolio sentiment is positive.")
        elif avg_sentiment < -0.3:
            summary_parts.append(" Overall portfolio sentiment is negative.")
        else:
            summary_parts.append(" Portfolio sentiment is neutral.")

        return (
            " ".join(summary_parts) if summary_parts else "No significant news today."
        )

    # ========== FALLBACK DATA METHODS ==========

    def _get_demo_news(self, symbol: str) -> List[Dict]:
        """Get demo news for testing"""
        demo_news = {
            "TSLA": [
                {
                    "headline": "Tesla Q3 Earnings Beat Estimates by 15%",
                    "source": "Bloomberg",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "url": "#",
                    "sentiment": "positive",
                },
                {
                    "headline": "Cybertruck Production Ramp Ahead of Schedule",
                    "source": "Reuters",
                    "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                    "url": "#",
                    "sentiment": "positive",
                },
            ],
            "AAPL": [
                {
                    "headline": "Apple Faces EU Antitrust Probe Over App Store Fees",
                    "source": "Financial Times",
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "url": "#",
                    "sentiment": "negative",
                },
                {
                    "headline": "iPhone Sales Miss Analyst Estimates in China",
                    "source": "WSJ",
                    "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                    "url": "#",
                    "sentiment": "negative",
                },
            ],
        }

        return demo_news.get(
            symbol,
            [
                {
                    "headline": f"{symbol} Stock Holds Steady Amid Market Volatility",
                    "source": "MarketWatch",
                    "timestamp": datetime.now().isoformat(),
                    "url": "#",
                    "sentiment": "neutral",
                }
            ],
        )

    def _get_fallback_macro_news(self) -> Dict:
        """Fallback macro news if fetch fails"""
        return {
            "fed_policy": {
                "title": "Fed Policy Monitor",
                "latest": "Data unavailable",
                "impact": "Unknown",
                "severity": "low",
            },
            "market_sentiment": 0.0,
        }

    def _get_fallback_ticker_news(self, symbol: str) -> Dict:
        """Fallback ticker news if fetch fails"""
        return {
            "symbol": symbol,
            "news_items": [],
            "aggregate_sentiment": 0.0,
            "sentiment_label": "Unknown",
            "impact_level": 0,
            "trading_recommendation": "Data unavailable",
        }

    def _get_fallback_portfolio_digest(self, mindfolio_id: str) -> Dict:
        """Fallback portfolio digest if generation fails"""
        return {
            "mindfolio_id": mindfolio_id,
            "macro_events": self._get_fallback_macro_news(),
            "ticker_news": {},
            "risk_alerts": [],
            "opportunities": [],
            "portfolio_sentiment": 0.0,
            "news_summary": "Unable to fetch news data",
            "last_updated": datetime.now().isoformat(),
        }
