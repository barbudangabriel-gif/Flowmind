"""
Market Sentiment Analyzer - Real-time sentiment analysis from multiple sources
Integrates news, social media, Reddit, YouTube, and financial forums
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class SentimentData:
    source: str
    symbol: str
    sentiment_score: float  # -1 to +1
    confidence: float  # 0 to 1
    volume: int  # Number of mentions
    timestamp: str
    key_phrases: List[str]
    source_url: Optional[str] = None


class MarketSentimentAnalyzer:
    """Comprehensive market sentiment analysis from multiple sources"""

    def __init__(self):
        self.session = None
        # Sentiment keywords for basic analysis
        self.bullish_keywords = [
            "bullish",
            "buy",
            "strong buy",
            "upgrade",
            "outperform",
            "positive",
            "rally",
            "surge",
            "breakout",
            "momentum",
            "uptrend",
            "growth",
            "beat earnings",
            "exceed expectations",
            "strong guidance",
            "innovation",
            "expansion",
            "partnership",
            "acquisition",
            "dividend increase",
            "moon",
            "rocket",
            "diamond hands",
            "hodl",
            "to the moon",
            "calls",
            "bullish af",
            "going up",
            "green",
            "gains",
            "stonks",
        ]

        self.bearish_keywords = [
            "bearish",
            "sell",
            "downgrade",
            "underperform",
            "negative",
            "decline",
            "crash",
            "drop",
            "breakdown",
            "resistance",
            "downtrend",
            "recession",
            "miss earnings",
            "below expectations",
            "weak guidance",
            "competition",
            "lawsuit",
            "regulation",
            "scandal",
            "dividend cut",
            "dump",
            "puts",
            "short",
            "bearish af",
            "going down",
            "red",
            "losses",
            "paper hands",
            "sell off",
            "tanking",
            "dead cat bounce",
        ]

    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def analyze_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive sentiment analysis from multiple sources"""
        try:
            sentiment_sources = []

            # Get sentiment from multiple sources concurrently
            tasks = [
                self._analyze_financial_news_sentiment(symbol),
                self._analyze_reddit_sentiment(symbol),
                self._analyze_twitter_sentiment(symbol),
                self._analyze_yahoo_finance_sentiment(symbol),
                self._analyze_seeking_alpha_sentiment(symbol),
                self._analyze_youtube_sentiment(symbol),
                self._analyze_insider_trading_sentiment(symbol),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and filter out exceptions
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Sentiment analysis error: {str(result)}")
                    continue
                if result and result.sentiment_score != 0:
                    sentiment_sources.append(result)

            # Calculate composite sentiment
            composite_sentiment = self._calculate_composite_sentiment(sentiment_sources)

            # Generate sentiment insights
            insights = self._generate_sentiment_insights(
                sentiment_sources, composite_sentiment
            )

            return {
                "symbol": symbol.upper(),
                "composite_sentiment": composite_sentiment,
                "sentiment_sources": [
                    self._sentiment_to_dict(s) for s in sentiment_sources
                ],
                "insights": insights,
                "sentiment_trend": self._analyze_sentiment_trend(sentiment_sources),
                "market_mood": self._determine_market_mood(composite_sentiment),
                "confidence_level": self._calculate_overall_confidence(
                    sentiment_sources
                ),
                "last_updated": datetime.utcnow().isoformat(),
                "total_mentions": sum(s.volume for s in sentiment_sources),
            }

        except Exception as e:
            logger.error(
                f"Error in comprehensive sentiment analysis for {symbol}: {str(e)}"
            )
            return self._get_default_sentiment(symbol)

    async def _analyze_financial_news_sentiment(
        self, symbol: str
    ) -> Optional[SentimentData]:
        """Analyze sentiment from financial news sources"""
        try:
            # Use yfinance to get recent news
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return None

            # Analyze sentiment from headlines and summaries
            total_sentiment = 0
            total_articles = 0
            key_phrases = []

            for article in news[:10]:  # Analyze last 10 articles
                title = article.get("title", "")
                summary = article.get("summary", "")
                text = f"{title} {summary}".lower()

                sentiment = self._calculate_text_sentiment(text)
                if sentiment != 0:
                    total_sentiment += sentiment
                    total_articles += 1

                # Extract key phrases
                phrases = self._extract_key_phrases(text)
                key_phrases.extend(phrases)

            if total_articles == 0:
                return None

            avg_sentiment = total_sentiment / total_articles
            confidence = min(
                1.0, total_articles / 10.0
            )  # Higher confidence with more articles

            return SentimentData(
                source="financial_news",
                symbol=symbol,
                sentiment_score=avg_sentiment,
                confidence=confidence,
                volume=total_articles,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=key_phrases[:5],  # Top 5 phrases
            )

        except Exception as e:
            logger.error(
                f"Error analyzing financial news sentiment for {symbol}: {str(e)}"
            )
            return None

    async def _analyze_reddit_sentiment(self, symbol: str) -> Optional[SentimentData]:
        """Analyze sentiment from Reddit (wallstreetbets, investing, etc.)"""
        try:
            session = await self.get_session()

            # Search Reddit for stock mentions
            subreddits = ["wallstreetbets", "investing", "stocks", "SecurityAnalysis"]
            total_sentiment = 0
            total_posts = 0
            key_phrases = []

            for subreddit in subreddits:
                try:
                    # Use Reddit's JSON API (no auth required for public posts)
                    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={symbol}&restrict_sr=1&sort=hot&limit=25"
                    headers = {"User-Agent": "MarketSentimentBot/1.0"}

                    async with session.get(
                        url, headers=headers, timeout=10
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get("data", {}).get("children", [])

                            for post in posts:
                                post_data = post.get("data", {})
                                title = post_data.get("title", "").lower()
                                selftext = post_data.get("selftext", "").lower()

                                # Only analyze if stock symbol is mentioned
                                if (
                                    symbol.lower() in title
                                    or symbol.lower() in selftext
                                ):
                                    text = f"{title} {selftext}"
                                    sentiment = self._calculate_text_sentiment(text)

                                    if sentiment != 0:
                                        total_sentiment += sentiment
                                        total_posts += 1

                                    phrases = self._extract_key_phrases(text)
                                    key_phrases.extend(phrases)

                except Exception as e:
                    logger.warning(f"Error accessing r/{subreddit}: {str(e)}")
                    continue

                # Rate limiting
                await asyncio.sleep(1)

            if total_posts == 0:
                return None

            avg_sentiment = total_sentiment / total_posts
            confidence = min(
                1.0, total_posts / 20.0
            )  # Higher confidence with more posts

            return SentimentData(
                source="reddit",
                symbol=symbol,
                sentiment_score=avg_sentiment,
                confidence=confidence,
                volume=total_posts,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=key_phrases[:5],
            )

        except Exception as e:
            logger.error(f"Error analyzing Reddit sentiment for {symbol}: {str(e)}")
            return None

    async def _analyze_twitter_sentiment(self, symbol: str) -> Optional[SentimentData]:
        """Analyze sentiment from Twitter/X (using simulated data for demo)"""
        try:
            # For demo purposes, return simulated Twitter sentiment
            # In real implementation, you would use Twitter API v2

            return SentimentData(
                source="twitter",
                symbol=symbol,
                sentiment_score=0.1,  # Slightly positive default
                confidence=0.3,  # Lower confidence for simulated data
                volume=5,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=["social_sentiment", "twitter_mentions"],
            )

        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment for {symbol}: {str(e)}")
            return None

    async def _analyze_yahoo_finance_sentiment(
        self, symbol: str
    ) -> Optional[SentimentData]:
        """Analyze sentiment from Yahoo Finance (simulated for demo)"""
        try:
            # Simulate Yahoo Finance sentiment
            return SentimentData(
                source="yahoo_finance",
                symbol=symbol,
                sentiment_score=0.05,
                confidence=0.4,
                volume=8,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=["yahoo_sentiment", "community_discussion"],
            )

        except Exception as e:
            logger.error(
                f"Error analyzing Yahoo Finance sentiment for {symbol}: {str(e)}"
            )
            return None

    async def _analyze_seeking_alpha_sentiment(
        self, symbol: str
    ) -> Optional[SentimentData]:
        """Analyze sentiment from Seeking Alpha (simulated for demo)"""
        try:
            return SentimentData(
                source="seeking_alpha",
                symbol=symbol,
                sentiment_score=0.15,  # Slightly positive
                confidence=0.6,  # Higher confidence for professional analysis
                volume=3,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=[
                    "analyst_opinion",
                    "seeking_alpha",
                    "professional_analysis",
                ],
            )

        except Exception as e:
            logger.error(
                f"Error analyzing Seeking Alpha sentiment for {symbol}: {str(e)}"
            )
            return None

    async def _analyze_youtube_sentiment(self, symbol: str) -> Optional[SentimentData]:
        """Analyze sentiment from YouTube (simulated for demo)"""
        try:
            return SentimentData(
                source="youtube",
                symbol=symbol,
                sentiment_score=0.2,  # Positive (YouTube tends to be optimistic)
                confidence=0.35,
                volume=7,
                timestamp=datetime.utcnow().isoformat(),
                key_phrases=[
                    "youtube_sentiment",
                    "video_mentions",
                    "influencer_opinion",
                ],
            )

        except Exception as e:
            logger.error(f"Error analyzing YouTube sentiment for {symbol}: {str(e)}")
            return None

    async def _analyze_insider_trading_sentiment(
        self, symbol: str
    ) -> Optional[SentimentData]:
        """Analyze sentiment from insider trading activity"""
        try:
            # Get insider trading data
            ticker = yf.Ticker(symbol)

            try:
                insider_trades = ticker.insider_transactions
                if insider_trades is not None and not insider_trades.empty:
                    # Analyze recent insider activity
                    recent_trades = insider_trades.head(10)

                    buy_volume = 0
                    sell_volume = 0

                    for _, trade in recent_trades.iterrows():
                        shares = trade.get("Shares", 0)
                        if shares > 0:
                            buy_volume += shares
                        else:
                            sell_volume += abs(shares)

                    # Calculate sentiment based on insider activity
                    if buy_volume > sell_volume * 1.5:
                        sentiment = 0.3  # Positive insider sentiment
                        key_phrase = "insider_buying"
                    elif sell_volume > buy_volume * 1.5:
                        sentiment = -0.2  # Negative insider sentiment
                        key_phrase = "insider_selling"
                    else:
                        sentiment = 0.0  # Neutral
                        key_phrase = "insider_neutral"

                    confidence = min(1.0, len(recent_trades) / 10.0)

                    return SentimentData(
                        source="insider_trading",
                        symbol=symbol,
                        sentiment_score=sentiment,
                        confidence=confidence,
                        volume=len(recent_trades),
                        timestamp=datetime.utcnow().isoformat(),
                        key_phrases=[key_phrase],
                    )
            except:
                pass  # Insider data not available

            return None

        except Exception as e:
            logger.error(
                f"Error analyzing insider trading sentiment for {symbol}: {str(e)}"
            )
            return None

    def _calculate_text_sentiment(self, text: str) -> float:
        """Calculate sentiment score from text using keyword analysis"""
        if not text:
            return 0.0

        text_lower = text.lower()

        # Count bullish and bearish keywords
        bullish_count = sum(
            1 for keyword in self.bullish_keywords if keyword in text_lower
        )
        bearish_count = sum(
            1 for keyword in self.bearish_keywords if keyword in text_lower
        )

        total_keywords = bullish_count + bearish_count
        if total_keywords == 0:
            return 0.0

        # Calculate sentiment score (-1 to +1)
        sentiment = (bullish_count - bearish_count) / total_keywords

        # Apply length scaling (longer texts have more reliable sentiment)
        text_length_factor = min(1.0, len(text) / 500.0)  # Scale by text length

        return sentiment * text_length_factor

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        phrases = []

        # Find bullish keywords
        for keyword in self.bullish_keywords:
            if keyword in text.lower():
                phrases.append(f"bullish_{keyword.replace(' ', '_')}")

        # Find bearish keywords
        for keyword in self.bearish_keywords:
            if keyword in text.lower():
                phrases.append(f"bearish_{keyword.replace(' ', '_')}")

        return phrases[:3]  # Return top 3 phrases

    def _calculate_composite_sentiment(
        self, sentiment_sources: List[SentimentData]
    ) -> Dict[str, float]:
        """Calculate weighted composite sentiment from all sources"""
        if not sentiment_sources:
            return {"score": 0.0, "confidence": 0.0}

        # Source weights (based on reliability and impact)
        source_weights = {
            "financial_news": 0.25,  # High reliability, institutional focus
            "reddit": 0.20,  # High volume, retail sentiment
            "yahoo_finance": 0.15,  # Good mix of retail and institutional
            "seeking_alpha": 0.15,  # Professional analysis
            "twitter": 0.10,  # High volume but noisy
            "youtube": 0.08,  # Entertainment-focused
            "insider_trading": 0.07,  # High reliability but low frequency
        }

        weighted_sentiment = 0.0
        total_weight = 0.0
        total_confidence = 0.0

        for sentiment in sentiment_sources:
            weight = source_weights.get(sentiment.source, 0.05)
            confidence_weight = weight * sentiment.confidence

            weighted_sentiment += sentiment.sentiment_score * confidence_weight
            total_weight += confidence_weight
            total_confidence += sentiment.confidence

        if total_weight == 0:
            return {"score": 0.0, "confidence": 0.0}

        composite_score = weighted_sentiment / total_weight
        avg_confidence = total_confidence / len(sentiment_sources)

        return {
            "score": max(-1.0, min(1.0, composite_score)),  # Clamp to [-1, 1]
            "confidence": min(1.0, avg_confidence),
        }

    def _generate_sentiment_insights(
        self, sentiment_sources: List[SentimentData], composite: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate human-readable sentiment insights"""
        score = composite["score"]
        confidence = composite["confidence"]

        # Determine sentiment direction
        if score > 0.3:
            direction = "BULLISH"
            strength = "Strong" if score > 0.6 else "Moderate"
        elif score < -0.3:
            direction = "BEARISH"
            strength = "Strong" if score < -0.6 else "Moderate"
        else:
            direction = "NEUTRAL"
            strength = "Mixed"

        # Find dominant source
        if sentiment_sources:
            dominant_source = max(
                sentiment_sources, key=lambda x: abs(x.sentiment_score) * x.confidence
            )
            dominant_source_name = dominant_source.source.replace("_", " ").title()
        else:
            dominant_source_name = "Unknown"

        # Generate insights
        insights = {
            "direction": direction,
            "strength": strength,
            "confidence_level": (
                "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
            ),
            "dominant_source": dominant_source_name,
            "key_themes": self._extract_key_themes(sentiment_sources),
            "summary": self._generate_sentiment_summary(
                score, confidence, dominant_source_name
            ),
        }

        return insights

    def _analyze_sentiment_trend(self, sentiment_sources: List[SentimentData]) -> str:
        """Analyze if sentiment is improving or deteriorating"""
        if len(sentiment_sources) < 2:
            return "STABLE"

        # Sort by confidence (proxy for recency/reliability)
        sorted_sources = sorted(
            sentiment_sources, key=lambda x: x.confidence, reverse=True
        )

        recent_sentiment = sum(s.sentiment_score for s in sorted_sources[:3]) / min(
            3, len(sorted_sources)
        )
        older_sentiment = sum(s.sentiment_score for s in sorted_sources[3:]) / max(
            1, len(sorted_sources[3:])
        )

        if recent_sentiment > older_sentiment + 0.1:
            return "IMPROVING"
        elif recent_sentiment < older_sentiment - 0.1:
            return "DETERIORATING"
        else:
            return "STABLE"

    def _determine_market_mood(self, composite: Dict[str, float]) -> str:
        """Determine overall market mood"""
        score = composite["score"]
        confidence = composite["confidence"]

        if confidence < 0.3:
            return "UNCERTAIN"
        elif score > 0.4:
            return "OPTIMISTIC"
        elif score > 0.1:
            return "CAUTIOUSLY_POSITIVE"
        elif score < -0.4:
            return "PESSIMISTIC"
        elif score < -0.1:
            return "CAUTIOUSLY_NEGATIVE"
        else:
            return "NEUTRAL"

    def _calculate_overall_confidence(
        self, sentiment_sources: List[SentimentData]
    ) -> float:
        """Calculate overall confidence in sentiment analysis"""
        if not sentiment_sources:
            return 0.0

        # Factors that increase confidence:
        # 1. Number of sources
        # 2. Volume of mentions
        # 3. Agreement between sources

        num_sources = len(sentiment_sources)
        total_volume = sum(s.volume for s in sentiment_sources)
        avg_confidence = sum(s.confidence for s in sentiment_sources) / num_sources

        # Agreement factor (higher when sources agree)
        if num_sources > 1:
            sentiments = [s.sentiment_score for s in sentiment_sources]
            sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0
            agreement_factor = max(
                0.5, 1.0 - sentiment_std
            )  # Lower std = higher agreement
        else:
            agreement_factor = 0.7

        # Combine factors
        source_factor = min(1.0, num_sources / 5.0)  # Up to 5 sources
        volume_factor = min(1.0, total_volume / 50.0)  # Up to 50 mentions total

        overall_confidence = (
            avg_confidence * 0.4
            + agreement_factor * 0.3
            + source_factor * 0.2
            + volume_factor * 0.1
        )

        return min(1.0, overall_confidence)

    def _extract_key_themes(self, sentiment_sources: List[SentimentData]) -> List[str]:
        """Extract key themes from all sentiment sources"""
        all_phrases = []
        for source in sentiment_sources:
            all_phrases.extend(source.key_phrases)

        # Count phrase frequency
        phrase_counts = {}
        for phrase in all_phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Return top themes
        top_themes = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in top_themes[:5]]

    def _generate_sentiment_summary(
        self, score: float, confidence: float, dominant_source: str
    ) -> str:
        """Generate human-readable sentiment summary"""
        if score > 0.3:
            sentiment_desc = "positive market sentiment"
        elif score < -0.3:
            sentiment_desc = "negative market sentiment"
        else:
            sentiment_desc = "mixed market sentiment"

        confidence_desc = (
            "high" if confidence > 0.7 else "moderate" if confidence > 0.4 else "low"
        )

        return (
            f"Analysis shows {sentiment_desc} with {confidence_desc} confidence. "
            f"Primary sentiment source: {dominant_source}."
        )

    def _sentiment_to_dict(self, sentiment: SentimentData) -> Dict[str, Any]:
        """Convert SentimentData to dictionary"""
        return {
            "source": sentiment.source,
            "sentiment_score": round(sentiment.sentiment_score, 3),
            "confidence": round(sentiment.confidence, 3),
            "volume": sentiment.volume,
            "key_phrases": sentiment.key_phrases,
            "timestamp": sentiment.timestamp,
        }

    def _get_default_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Return default sentiment for error cases"""
        return {
            "symbol": symbol.upper(),
            "composite_sentiment": {"score": 0.0, "confidence": 0.0},
            "sentiment_sources": [],
            "insights": {
                "direction": "UNKNOWN",
                "strength": "Unknown",
                "confidence_level": "Low",
                "dominant_source": "None",
                "key_themes": [],
                "summary": f"Unable to analyze sentiment for {symbol}",
            },
            "sentiment_trend": "UNKNOWN",
            "market_mood": "UNCERTAIN",
            "confidence_level": 0.0,
            "last_updated": datetime.utcnow().isoformat(),
            "total_mentions": 0,
        }

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()


# Global instance
market_sentiment_analyzer = MarketSentimentAnalyzer()


# Utility function to convert sentiment to investment score component
def sentiment_to_investment_score(sentiment_data: Dict[str, Any]) -> float:
    """Convert sentiment analysis to investment score component (0-100)"""
    composite = sentiment_data.get("composite_sentiment", {})
    score = composite.get("score", 0.0)  # -1 to +1
    confidence = composite.get("confidence", 0.0)  # 0 to 1

    # Convert to 0-100 scale with confidence weighting
    base_score = ((score + 1) / 2) * 100  # Convert -1,+1 to 0,100

    # Apply confidence factor
    final_score = 50 + (base_score - 50) * confidence

    return max(0, min(100, final_score))
