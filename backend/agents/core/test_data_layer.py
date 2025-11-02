"""
Test suite for CORE ENGINE Data Layer (Redis Streams + TimeSeries)

Tests:
1. Streams: publish_signal(), consume_signals(), consumer groups
2. TimeSeries: add_news_event(), query_news_history()
3. Fallback: In-memory when Redis unavailable
4. End-to-end: Signal flow through streams

Run: pytest backend/agents/core/test_data_layer.py -v
"""

import asyncio
import time
from typing import List

import pytest

from agents.core.data_layer import (
    RedisStreamsManager,
    RedisTimeSeriesManager,
    get_data_layer,
)


# ═══════════════════════════════════════════════════════════════════════════
# TEST: REDIS STREAMS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_streams_publish_and_consume():
    """Test signal publishing and consuming with consumer groups"""
    streams, _ = await get_data_layer()

    stream_name = "signals:test"
    group_name = "test_consumers"
    consumer_name = "consumer_1"

    # Publish 3 signals
    signal_1 = {"symbol": "TSLA", "action": "BUY", "score": 85, "agent": "scanner_1"}
    signal_2 = {"symbol": "AAPL", "action": "SELL", "score": 78, "agent": "scanner_2"}
    signal_3 = {"symbol": "NVDA", "action": "BUY", "score": 92, "agent": "scanner_3"}

    msg_id_1 = await streams.publish_signal(stream_name, signal_1)
    msg_id_2 = await streams.publish_signal(stream_name, signal_2)
    msg_id_3 = await streams.publish_signal(stream_name, signal_3)

    assert msg_id_1
    assert msg_id_2
    assert msg_id_3

    print(f"✅ Published 3 signals: {msg_id_1}, {msg_id_2}, {msg_id_3}")

    # Consume signals
    messages = await streams.consume_signals(
        stream_name, group_name, consumer_name, count=10, block=1000
    )

    assert len(messages) == 3
    assert messages[0]["symbol"] == "TSLA"
    assert messages[1]["symbol"] == "AAPL"
    assert messages[2]["symbol"] == "NVDA"

    print(f"✅ Consumed {len(messages)} signals: {messages}")

    # Verify stream length
    length = await streams.get_stream_length(stream_name)
    assert length >= 3

    print(f"✅ Stream length: {length}")


@pytest.mark.asyncio
async def test_streams_multiple_consumers():
    """Test multiple consumers in same group (each message delivered once)"""
    streams, _ = await get_data_layer()

    stream_name = "signals:multi_consumer_test"
    group_name = "team_leads"

    # Publish 10 signals
    for i in range(10):
        signal = {
            "symbol": f"TICK{i}",
            "action": "BUY",
            "score": 80 + i,
            "agent": f"scanner_{i}",
        }
        await streams.publish_signal(stream_name, signal)

    # Consumer 1 reads 5 messages
    messages_c1 = await streams.consume_signals(
        stream_name, group_name, "consumer_1", count=5, block=1000
    )
    assert len(messages_c1) == 5

    # Consumer 2 reads remaining 5 messages
    messages_c2 = await streams.consume_signals(
        stream_name, group_name, "consumer_2", count=5, block=1000
    )
    assert len(messages_c2) == 5

    # Total should be 10, no duplicates
    all_symbols = [m["symbol"] for m in messages_c1 + messages_c2]
    assert len(all_symbols) == 10
    assert len(set(all_symbols)) == 10  # No duplicates

    print(f"✅ Consumer 1: {len(messages_c1)} signals")
    print(f"✅ Consumer 2: {len(messages_c2)} signals")
    print(f"✅ No duplicates: {all_symbols}")


# ═══════════════════════════════════════════════════════════════════════════
# TEST: REDIS TIMESERIES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_timeseries_news_events():
    """Test adding and querying news events"""
    _, timeseries = await get_data_layer()

    ticker = "TSLA"
    now = int(time.time())

    # Add 5 news events over 60 seconds
    for i in range(5):
        sentiment = 0.2 * i - 0.4  # -0.4, -0.2, 0.0, 0.2, 0.4
        timestamp = now + (i * 12)  # 12 seconds apart
        success = await timeseries.add_news_event(ticker, timestamp, sentiment)
        assert success

    print(f"✅ Added 5 news events for {ticker}")

    # Query news history
    from_ts = now - 10
    to_ts = now + 100
    history = await timeseries.query_news_history(ticker, from_ts, to_ts)

    assert len(history) >= 5
    print(f"✅ Queried news history: {len(history)} events")

    # Verify sentiment values
    sentiments = [val for ts, val in history]
    assert min(sentiments) >= -0.5
    assert max(sentiments) <= 0.5

    print(f"✅ Sentiment range: {min(sentiments):.2f} to {max(sentiments):.2f}")


@pytest.mark.asyncio
async def test_timeseries_agent_performance():
    """Test tracking agent performance over time"""
    _, timeseries = await get_data_layer()

    agent_id = "scanner_42"
    now = int(time.time())

    # Simulate 24-hour performance tracking (1 data point per hour)
    for hour in range(24):
        win_rate = 0.70 + (0.05 * (hour % 5))  # Varies 0.70-0.75
        timestamp = now - ((24 - hour) * 3600)  # Go back 24 hours
        success = await timeseries.add_agent_performance(
            agent_id, win_rate, timestamp
        )
        assert success

    print(f"✅ Added 24h performance data for {agent_id}")

    # Query last 24 hours
    from_ts = now - (24 * 3600)
    to_ts = now
    performance = await timeseries.query_agent_performance(
        agent_id, from_ts, to_ts
    )

    assert len(performance) >= 24
    print(f"✅ Queried performance: {len(performance)} data points")

    # Verify win rate range
    win_rates = [val for ts, val in performance]
    assert all(0.65 <= wr <= 0.80 for wr in win_rates)

    print(
        f"✅ Win rate range: {min(win_rates):.2%} to {max(win_rates):.2%}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# TEST: END-TO-END SIGNAL FLOW
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_end_to_end_signal_flow():
    """
    Test complete signal flow:
    Scanner → signals:universe → Team Lead → signals:validated:1 → Sector Head
    """
    streams, timeseries = await get_data_layer()

    # STEP 1: Scanner publishes signal
    scanner_signal = {
        "symbol": "NVDA",
        "action": "BUY",
        "score": 88,
        "agent_id": "scanner_1",
        "timestamp": int(time.time()),
        "reasons": ["technical_breakout", "options_flow_bullish"],
    }

    msg_id = await streams.publish_signal("signals:universe", scanner_signal)
    assert msg_id
    print(f"✅ Scanner published signal: {msg_id}")

    # STEP 2: Team Lead consumes signal
    team_lead_signals = await streams.consume_signals(
        stream="signals:universe",
        group="team_leads",
        consumer="team_lead_1",
        count=1,
        block=1000,
    )

    assert len(team_lead_signals) == 1
    signal = team_lead_signals[0]
    assert signal["symbol"] == "NVDA"
    print(f"✅ Team Lead consumed signal: {signal['symbol']}")

    # STEP 3: Team Lead validates and publishes to validated stream
    validated_signal = {
        **signal,
        "validated_by": "team_lead_1",
        "validation_score": 85,
        "peer_confirmation": True,
    }

    msg_id_validated = await streams.publish_signal(
        "signals:validated:1", validated_signal
    )
    assert msg_id_validated
    print(f"✅ Team Lead validated signal: {msg_id_validated}")

    # STEP 4: Sector Head consumes validated signal
    sector_head_signals = await streams.consume_signals(
        stream="signals:validated:1",
        group="sector_heads",
        consumer="sector_head_tech",
        count=1,
        block=1000,
    )

    assert len(sector_head_signals) == 1
    validated = sector_head_signals[0]
    assert validated["symbol"] == "NVDA"
    assert validated["validated_by"] == "team_lead_1"
    print(f"✅ Sector Head consumed validated signal: {validated['symbol']}")

    # STEP 5: Track agent performance
    await timeseries.add_agent_performance("scanner_1", win_rate=0.75)
    print(f"✅ Tracked agent performance")

    print("\n✅ END-TO-END SIGNAL FLOW COMPLETE!")


# ═══════════════════════════════════════════════════════════════════════════
# TEST: FALLBACK MODE
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_fallback_mode():
    """Test in-memory fallback when Redis unavailable"""
    streams = RedisStreamsManager()
    timeseries = RedisTimeSeriesManager()

    # Force fallback mode
    streams.use_fallback = True
    timeseries.use_fallback = True

    # Publish signal (in-memory)
    signal = {"symbol": "TSLA", "action": "BUY", "score": 85}
    msg_id = await streams.publish_signal("signals:test_fallback", signal)
    assert msg_id
    print(f"✅ Fallback publish: {msg_id}")

    # Consume signal (in-memory)
    messages = await streams.consume_signals(
        "signals:test_fallback",
        "test_group",
        "consumer_1",
        count=1,
        block=100,
    )
    assert len(messages) == 1
    assert messages[0]["symbol"] == "TSLA"
    print(f"✅ Fallback consume: {messages[0]}")

    # Add timeseries data (in-memory)
    now = int(time.time())
    success = await timeseries.add_news_event("TSLA", now, sentiment=0.5)
    assert success
    print(f"✅ Fallback timeseries add")

    # Query timeseries (in-memory)
    history = await timeseries.query_news_history("TSLA", now - 10, now + 10)
    assert len(history) >= 1
    print(f"✅ Fallback timeseries query: {len(history)} events")

    print("\n✅ FALLBACK MODE WORKING!")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CORE ENGINE - Data Layer Test Suite")
    print("=" * 80 + "\n")

    # Run all tests
    async def run_all_tests():
        await test_streams_publish_and_consume()
        print()
        await test_streams_multiple_consumers()
        print()
        await test_timeseries_news_events()
        print()
        await test_timeseries_agent_performance()
        print()
        await test_end_to_end_signal_flow()
        print()
        await test_fallback_mode()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80 + "\n")

    asyncio.run(run_all_tests())
