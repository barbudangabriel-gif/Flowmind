"""
Universe Scanner Agent - Tier 4 Worker
EXTENDS StockScanner from investment_scoring.py
NEW FEATURES: 500 tickers, two-tier scanning, news integration, Redis Streams

Architecture:
- 167 agents × 3 tickers = 501 capacity (500 used)
- Light scan: 5-minute interval (quick checks)
- Deep scan: 1-minute interval (full analysis for hot tickers)
- Publishes to: signals:universe stream
- Cost: $0/month (FREE data sources)
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.core.data_layer import get_data_layer
from agents.core.news_aggregator import get_news_aggregator
from enhanced_ticker_data import enhanced_ticker_manager
from market_sentiment_analyzer import (
    market_sentiment_analyzer,
    sentiment_to_investment_score,
)
from technical_analysis_enhanced import technical_analyzer
from unusual_whales_service_clean import UnusualWhalesService

logger = logging.getLogger(__name__)


class UniverseScannerAgent:
    """
    Single scanner agent instance - scans 3 assigned tickers
    
    Features:
    - Two-tier scanning (light 5min, deep 1min)
    - News integration (NewsAggregator)
    - Options flow + dark pool (Unusual Whales)
    - Technical + sentiment analysis
    - Redis Streams publishing (signals:universe)
    - Performance tracking (Redis TimeSeries)
    """

    def __init__(
        self,
        agent_id: str,
        assigned_tickers: List[str],
        light_interval: int = 300,  # 5 minutes
        deep_interval: int = 60,  # 1 minute
    ):
        """
        Initialize scanner agent
        
        Args:
            agent_id: Unique identifier (e.g., "scanner_001")
            assigned_tickers: List of 3 tickers to scan
            light_interval: Seconds between light scans (default: 300 = 5min)
            deep_interval: Seconds between deep scans (default: 60 = 1min)
        """
        self.agent_id = agent_id
        self.tickers = assigned_tickers[:3]  # Max 3 tickers per agent
        self.light_interval = light_interval
        self.deep_interval = deep_interval

        # Initialize services
        self.news_aggregator = None
        self.uw_service = UnusualWhalesService()
        self.streams_manager = None
        self.timeseries_manager = None

        # Performance tracking
        self.signals_generated = 0
        self.signals_validated = 0  # Confirmed by Team Leads
        self.false_positives = 0
        self.start_time = None

        # Hot tickers (upgrade to deep scan)
        self.hot_tickers = set()  # Tickers with recent signals

        logger.info(
            f"[{self.agent_id}] Initialized with tickers: {', '.join(self.tickers)}"
        )

    async def initialize(self):
        """Async initialization (services require async setup)"""
        self.news_aggregator = await get_news_aggregator()
        self.streams_manager, self.timeseries_manager = await get_data_layer()
        self.start_time = datetime.utcnow()
        logger.info(f"[{self.agent_id}] Services initialized")

    async def scan_light(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Light scan (5-minute interval)
        Quick checks: price, volume, basic indicators
        
        Returns signal dict if opportunity found, else None
        """
        try:
            # Get real-time quote
            quote = await enhanced_ticker_manager.get_real_time_quote(ticker)
            if not quote:
                logger.warning(f"[{self.agent_id}] {ticker}: No quote data")
                return None

            current_price = quote.get("Last", 0)
            volume = quote.get("Volume", 0)
            prev_close = quote.get("PreviousClose", current_price)

            # Calculate price change percentage
            price_change_pct = (
                ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            )

            # LIGHT SCAN FILTERS (fast decision)
            # 1. Minimum price: $5 (avoid penny stocks)
            if current_price < 5.0:
                return None

            # 2. Minimum volume: 100k shares (ensure liquidity)
            if volume < 100_000:
                return None

            # 3. Price movement threshold: ±2% (skip flat stocks)
            if abs(price_change_pct) < 2.0:
                return None

            # Quick technical indicators (no full analysis)
            # RSI check (basic momentum)
            technical_data = await technical_analyzer.analyze_stock_technical(ticker)
            if not technical_data:
                return None

            rsi = technical_data.get("indicators", {}).get("rsi", {}).get("value", 50)

            # SIGNAL GENERATION (light scan passed)
            signal = {
                "agent_id": self.agent_id,
                "agent_tier": "tier4_worker",
                "ticker": ticker,
                "scan_type": "light",
                "timestamp": datetime.utcnow().isoformat(),
                "price": current_price,
                "volume": volume,
                "price_change_pct": round(price_change_pct, 2),
                "rsi": round(rsi, 2),
                "reason": f"Light scan: {price_change_pct:+.2f}% move, RSI {rsi:.0f}",
                "confidence": 0.3,  # Low confidence (needs deep scan)
                "upgrade_to_deep": True,  # Flag for deep scan
            }

            logger.info(
                f"[{self.agent_id}] {ticker}: Light signal - "
                f"{price_change_pct:+.2f}% move, RSI {rsi:.0f}"
            )

            # Mark as hot ticker (upgrade to deep scan)
            self.hot_tickers.add(ticker)

            return signal

        except Exception as e:
            logger.error(f"[{self.agent_id}] Light scan error ({ticker}): {e}")
            return None

    async def scan_deep(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Deep scan (1-minute interval for hot tickers)
        Full analysis: technical, sentiment, news, options flow, dark pool
        
        Returns enriched signal dict if strong opportunity, else None
        """
        try:
            # Get all data sources concurrently
            quote_task = enhanced_ticker_manager.get_real_time_quote(ticker)
            technical_task = technical_analyzer.analyze_stock_technical(ticker)
            sentiment_task = market_sentiment_analyzer.analyze_market_sentiment(ticker)
            news_task = self.news_aggregator.get_ticker_news(
                ticker, sources=["alpha_vantage", "reddit"]
            )
            options_task = self._get_options_flow(ticker)
            darkpool_task = self._get_dark_pool_activity(ticker)

            # Wait for all tasks
            quote, technical, sentiment, news, options_flow, darkpool = await asyncio.gather(
                quote_task,
                technical_task,
                sentiment_task,
                news_task,
                options_task,
                darkpool_task,
                return_exceptions=True,
            )

            # Handle exceptions
            if isinstance(quote, Exception):
                logger.error(f"[{self.agent_id}] {ticker}: Quote fetch failed - {quote}")
                return None

            if not quote:
                return None

            # Extract core data
            current_price = quote.get("Last", 0)
            volume = quote.get("Volume", 0)
            prev_close = quote.get("PreviousClose", current_price)
            price_change_pct = (
                ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            )

            # Technical analysis score
            tech_score = 0
            if not isinstance(technical, Exception) and technical:
                trend = technical.get("overall_trend", {})
                indicators = technical.get("indicators", {})

                trend_score = trend.get("score", 0)
                rsi = indicators.get("rsi", {}).get("value", 50)
                macd_signal = indicators.get("macd", {}).get("signal", "neutral")

                # Trend scoring
                if trend.get("direction") == "bullish" and trend_score > 70:
                    tech_score += 30
                elif trend.get("direction") == "bearish" and trend_score < 30:
                    tech_score += 30  # Short opportunity
                else:
                    tech_score += 10

                # RSI scoring (oversold/overbought)
                if rsi < 30:
                    tech_score += 20  # Oversold (buy signal)
                elif rsi > 70:
                    tech_score += 20  # Overbought (short signal)
                else:
                    tech_score += 5

                # MACD scoring
                if macd_signal == "buy":
                    tech_score += 15
                elif macd_signal == "sell":
                    tech_score += 15  # Short signal
                else:
                    tech_score += 5

            # Sentiment analysis score
            sentiment_score = 0
            news_sentiment = 0.0
            if not isinstance(sentiment, Exception) and sentiment:
                overall_score = sentiment.get("overall_sentiment", 0)
                sentiment_score = sentiment_to_investment_score(overall_score) * 20

            # News sentiment
            if not isinstance(news, Exception) and news:
                # Average sentiment from recent news
                recent_news = [n for n in news if n.get("sentiment_score")][:5]
                if recent_news:
                    news_sentiment = sum(n.get("sentiment_score", 0) for n in recent_news) / len(recent_news)
                    sentiment_score += abs(news_sentiment) * 15  # Strong sentiment (bull or bear)

            # Options flow score
            options_score = 0
            call_put_ratio = 0
            if not isinstance(options_flow, Exception) and options_flow:
                call_volume = options_flow.get("call_volume", 0)
                put_volume = options_flow.get("put_volume", 0)
                total_premium = options_flow.get("total_premium", 0)

                if put_volume > 0:
                    call_put_ratio = call_volume / put_volume

                # Heavy call buying (bullish)
                if call_put_ratio > 2.0 and total_premium > 1_000_000:
                    options_score += 25
                # Heavy put buying (bearish)
                elif call_put_ratio < 0.5 and total_premium > 1_000_000:
                    options_score += 25
                else:
                    options_score += 5

            # Dark pool score
            darkpool_score = 0
            if not isinstance(darkpool, Exception) and darkpool:
                trade_count = darkpool.get("trade_count", 0)
                avg_trade_size = darkpool.get("avg_trade_size", 0)

                # Large dark pool activity (institutional interest)
                if trade_count > 50 and avg_trade_size > 10_000:
                    darkpool_score += 15

            # TOTAL SCORE (0-100)
            total_score = tech_score + sentiment_score + options_score + darkpool_score

            # CONFIDENCE LEVEL (0.0-1.0)
            confidence = min(total_score / 100, 1.0)

            # DEEP SCAN THRESHOLD: 60+ score
            if total_score < 60:
                logger.debug(
                    f"[{self.agent_id}] {ticker}: Deep scan below threshold "
                    f"(score: {total_score})"
                )
                return None

            # GENERATE ENRICHED SIGNAL
            signal = {
                "agent_id": self.agent_id,
                "agent_tier": "tier4_worker",
                "ticker": ticker,
                "scan_type": "deep",
                "timestamp": datetime.utcnow().isoformat(),
                # Price data
                "price": current_price,
                "volume": volume,
                "price_change_pct": round(price_change_pct, 2),
                # Scores
                "total_score": round(total_score, 1),
                "confidence": round(confidence, 2),
                "tech_score": tech_score,
                "sentiment_score": round(sentiment_score, 1),
                "options_score": options_score,
                "darkpool_score": darkpool_score,
                # Details
                "trend_direction": (
                    technical.get("overall_trend", {}).get("direction")
                    if not isinstance(technical, Exception) and technical
                    else "neutral"
                ),
                "rsi": (
                    round(technical.get("indicators", {}).get("rsi", {}).get("value", 50), 2)
                    if not isinstance(technical, Exception) and technical
                    else 50
                ),
                "news_sentiment": round(news_sentiment, 2),
                "call_put_ratio": round(call_put_ratio, 2),
                "news_count": len(news) if not isinstance(news, Exception) and news else 0,
                "reason": self._generate_signal_reason(
                    total_score, tech_score, sentiment_score, options_score, darkpool_score
                ),
                "upgrade_to_deep": False,  # Already deep scan
            }

            logger.info(
                f"[{self.agent_id}] {ticker}: DEEP SIGNAL - "
                f"Score {total_score:.0f}, Confidence {confidence:.0%}"
            )

            self.signals_generated += 1
            return signal

        except Exception as e:
            logger.error(f"[{self.agent_id}] Deep scan error ({ticker}): {e}")
            return None

    def _generate_signal_reason(
        self, total: float, tech: float, sentiment: float, options: float, darkpool: float
    ) -> str:
        """Generate human-readable reason for signal"""
        reasons = []

        if tech >= 50:
            reasons.append(f"Strong technicals ({tech:.0f})")
        if sentiment >= 20:
            reasons.append(f"Positive sentiment ({sentiment:.0f})")
        if options >= 20:
            reasons.append(f"Options flow ({options:.0f})")
        if darkpool >= 10:
            reasons.append(f"Dark pool activity ({darkpool:.0f})")

        return ", ".join(reasons) if reasons else f"Score: {total:.0f}"

    async def _get_options_flow(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch options flow data from Unusual Whales"""
        try:
            # Get options volume data
            volume_data = await self.uw_service.get_ticker_options_volume(ticker)
            if not volume_data:
                return None

            return {
                "call_volume": volume_data.get("call_volume", 0),
                "put_volume": volume_data.get("put_volume", 0),
                "total_premium": volume_data.get("total_premium", 0),
                "call_put_ratio": volume_data.get("put_call_ratio", 0),
            }
        except Exception as e:
            logger.debug(f"[{self.agent_id}] {ticker}: Options flow unavailable - {e}")
            return None

    async def _get_dark_pool_activity(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch dark pool data from Unusual Whales"""
        try:
            # Get dark pool trades (limit to 50 for speed)
            darkpool_data = await self.uw_service.get_ticker_darkpool(ticker, limit=50)
            if not darkpool_data or "data" not in darkpool_data:
                return None

            trades = darkpool_data["data"]
            if not trades:
                return None

            # Calculate metrics
            trade_count = len(trades)
            total_volume = sum(t.get("size", 0) for t in trades)
            avg_trade_size = total_volume / trade_count if trade_count else 0

            return {
                "trade_count": trade_count,
                "total_volume": total_volume,
                "avg_trade_size": avg_trade_size,
            }
        except Exception as e:
            logger.debug(f"[{self.agent_id}] {ticker}: Dark pool unavailable - {e}")
            return None

    async def publish_signal(self, signal: Dict[str, Any]):
        """Publish signal to Redis Streams"""
        try:
            stream_name = "signals:universe"
            await self.streams_manager.publish_signal(stream_name, signal)

            # Track performance in TimeSeries
            await self.timeseries_manager.add_news_event(
                f"signals:performance:{self.agent_id}",
                {
                    "ticker": signal["ticker"],
                    "score": signal["total_score"],
                    "confidence": signal["confidence"],
                },
            )

            logger.debug(
                f"[{self.agent_id}] Published signal for {signal['ticker']} "
                f"to {stream_name}"
            )

        except Exception as e:
            logger.error(f"[{self.agent_id}] Publish signal error: {e}")

    async def run_light_scan_loop(self):
        """Background task: Light scan loop (5-minute interval)"""
        logger.info(
            f"[{self.agent_id}] Starting light scan loop "
            f"({self.light_interval}s interval)"
        )

        while True:
            try:
                for ticker in self.tickers:
                    # Skip if already hot (being scanned deeply)
                    if ticker in self.hot_tickers:
                        continue

                    signal = await self.scan_light(ticker)
                    if signal:
                        await self.publish_signal(signal)

                    # Small delay between tickers
                    await asyncio.sleep(0.5)

                # Wait before next light scan cycle
                await asyncio.sleep(self.light_interval)

            except Exception as e:
                logger.error(f"[{self.agent_id}] Light scan loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def run_deep_scan_loop(self):
        """Background task: Deep scan loop (1-minute interval for hot tickers)"""
        logger.info(
            f"[{self.agent_id}] Starting deep scan loop "
            f"({self.deep_interval}s interval)"
        )

        while True:
            try:
                if not self.hot_tickers:
                    # No hot tickers, wait
                    await asyncio.sleep(self.deep_interval)
                    continue

                # Scan all hot tickers
                hot_list = list(self.hot_tickers)
                for ticker in hot_list:
                    signal = await self.scan_deep(ticker)
                    if signal:
                        await self.publish_signal(signal)
                    else:
                        # No longer hot (remove from hot list)
                        self.hot_tickers.discard(ticker)

                    # Small delay between tickers
                    await asyncio.sleep(0.5)

                # Wait before next deep scan cycle
                await asyncio.sleep(self.deep_interval)

            except Exception as e:
                logger.error(f"[{self.agent_id}] Deep scan loop error: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error

    async def start(self):
        """Start scanner agent (both light and deep scan loops)"""
        await self.initialize()

        # Start both scan loops concurrently
        light_task = asyncio.create_task(self.run_light_scan_loop())
        deep_task = asyncio.create_task(self.run_deep_scan_loop())

        logger.info(f"[{self.agent_id}] Scanner agent started")

        # Wait for both tasks (run forever)
        await asyncio.gather(light_task, deep_task)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        uptime = (
            (datetime.utcnow() - self.start_time).total_seconds()
            if self.start_time
            else 0
        )

        return {
            "agent_id": self.agent_id,
            "tickers": self.tickers,
            "hot_tickers": list(self.hot_tickers),
            "signals_generated": self.signals_generated,
            "signals_validated": self.signals_validated,
            "false_positives": self.false_positives,
            "win_rate": (
                self.signals_validated / self.signals_generated
                if self.signals_generated
                else 0
            ),
            "uptime_seconds": round(uptime, 1),
            "uptime_hours": round(uptime / 3600, 2),
        }
