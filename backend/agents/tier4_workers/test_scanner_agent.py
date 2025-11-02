"""
Test Suite for Universe Scanner Agent
Tests light scan, deep scan, signal generation, Redis integration

Run: cd /workspaces/Flowmind/backend && python agents/tier4_workers/test_scanner_agent.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier4_workers.scanner_agent import UniverseScannerAgent


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def get_scanner_agent():
    """Create scanner agent instance for testing"""
    return UniverseScannerAgent(
        agent_id="scanner_test_001",
        assigned_tickers=["TSLA", "AAPL", "NVDA"],
        light_interval=10,
        deep_interval=5,
    )


def get_mock_quote_data():
    """Mock stock quote data"""
    return {
        "Symbol": "TSLA",
        "Last": 250.50,
        "Volume": 1_500_000,
        "PreviousClose": 245.00,
    }


def get_mock_technical_data():
    """Mock technical analysis data"""
    return {
        "overall_trend": {"direction": "bullish", "score": 75},
        "indicators": {"rsi": {"value": 65}, "macd": {"signal": "buy"}},
    }


# ═══════════════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_scanner_initialization():
    """Test scanner agent initialization"""
    scanner = get_scanner_agent()
    assert scanner.agent_id == "scanner_test_001"
    assert scanner.tickers == ["TSLA", "AAPL", "NVDA"]
    assert scanner.signals_generated == 0
    print("✅ Test 1/6: Scanner initialization")


def test_light_scan_generates_signal():
    """Test light scan generates signal for >2% price move"""

    async def run_test():
        scanner = get_scanner_agent()
        quote = get_mock_quote_data()
        technical = get_mock_technical_data()

        with patch(
            "backend.enhanced_ticker_data.enhanced_ticker_manager.get_real_time_quote"
        ) as mock_quote, patch(
            "backend.technical_analysis_enhanced.technical_analyzer.analyze_stock_technical"
        ) as mock_tech:

            mock_quote.return_value = quote
            mock_tech.return_value = technical

            signal = await scanner.scan_light("TSLA")

            assert signal is not None
            assert signal["ticker"] == "TSLA"
            assert signal["scan_type"] == "light"
            assert signal["confidence"] == 0.3
            assert "TSLA" in scanner.hot_tickers

    asyncio.run(run_test())
    print("✅ Test 2/6: Light scan generates signal")


def test_light_scan_filters_low_price():
    """Test light scan filters penny stocks (<$5)"""

    async def run_test():
        scanner = get_scanner_agent()
        penny_quote = {
            "Symbol": "PENNY",
            "Last": 2.50,  # Below $5
            "Volume": 500_000,
            "PreviousClose": 2.00,
        }

        with patch(
            "backend.enhanced_ticker_data.enhanced_ticker_manager.get_real_time_quote"
        ) as mock_quote, patch(
            "backend.technical_analysis_enhanced.technical_analyzer.analyze_stock_technical"
        ) as mock_tech:

            mock_quote.return_value = penny_quote
            mock_tech.return_value = get_mock_technical_data()

            signal = await scanner.scan_light("PENNY")
            assert signal is None  # Filtered out

    asyncio.run(run_test())
    print("✅ Test 3/6: Light scan filters low price")


def test_deep_scan_generates_signal():
    """Test deep scan with full data sources"""

    async def run_test():
        scanner = get_scanner_agent()
        scanner.news_aggregator = AsyncMock()
        scanner.streams_manager = AsyncMock()
        scanner.timeseries_manager = AsyncMock()

        quote = get_mock_quote_data()
        technical = get_mock_technical_data()
        sentiment = {"overall_sentiment": 0.65}
        news = [
            {
                "headline": "Tesla reports strong earnings",
                "sentiment_score": 0.8,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]

        with patch(
            "enhanced_ticker_data.enhanced_ticker_manager.get_real_time_quote"
        ) as mock_quote, patch(
            "technical_analysis_enhanced.technical_analyzer.analyze_stock_technical"
        ) as mock_tech, patch(
            "market_sentiment_analyzer.market_sentiment_analyzer.analyze_market_sentiment"
        ) as mock_sentiment:

            mock_quote.return_value = quote
            mock_tech.return_value = technical
            mock_sentiment.return_value = sentiment
            scanner.news_aggregator.get_ticker_news.return_value = news
            scanner._get_options_flow = AsyncMock(
                return_value={
                    "call_volume": 5000,
                    "put_volume": 2000,
                    "total_premium": 2_000_000,
                    "call_put_ratio": 2.5,
                }
            )
            scanner._get_dark_pool_activity = AsyncMock(
                return_value={"trade_count": 75, "avg_trade_size": 6666}
            )

            signal = await scanner.scan_deep("TSLA")

            assert signal is not None
            assert signal["scan_type"] == "deep"
            assert signal["total_score"] >= 60
            assert signal["confidence"] >= 0.6
            assert scanner.signals_generated == 1

    asyncio.run(run_test())
    print("✅ Test 4/6: Deep scan generates signal")


def test_publish_signal():
    """Test signal publishing to Redis Streams"""

    async def run_test():
        scanner = get_scanner_agent()
        scanner.streams_manager = AsyncMock()
        scanner.timeseries_manager = AsyncMock()

        signal = {
            "agent_id": "scanner_test_001",
            "ticker": "TSLA",
            "total_score": 75,
            "confidence": 0.75,
        }

        await scanner.publish_signal(signal)

        scanner.streams_manager.publish_signal.assert_called_once_with(
            "signals:universe", signal
        )

    asyncio.run(run_test())
    print("✅ Test 5/6: Publish signal to Redis")


def test_get_stats():
    """Test agent statistics"""
    scanner = get_scanner_agent()
    scanner.start_time = datetime.utcnow()
    scanner.signals_generated = 10
    scanner.signals_validated = 7
    scanner.hot_tickers = {"TSLA", "AAPL"}

    stats = scanner.get_stats()

    assert stats["agent_id"] == "scanner_test_001"
    assert stats["signals_generated"] == 10
    assert stats["signals_validated"] == 7
    assert stats["win_rate"] == 0.7
    print("✅ Test 6/6: Agent statistics")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("UNIVERSE SCANNER AGENT - TEST SUITE")
    print("=" * 70 + "\n")

    test_scanner_initialization()
    test_light_scan_generates_signal()
    test_light_scan_filters_low_price()
    test_deep_scan_generates_signal()
    test_publish_signal()
    test_get_stats()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED (6/6)")
    print("=" * 70 + "\n")
