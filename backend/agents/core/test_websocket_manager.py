"""
Test suite for WebSocket Manager

Tests:
1. Connection management: connect, disconnect, multiple clients
2. Subscriptions: subscribe, unsubscribe, broadcast to subscribers
3. Stream consumer: consume from Redis Streams → broadcast
4. Message types: signals, news, status

Run: pytest backend/agents/core/test_websocket_manager.py -v
"""

import asyncio
import json
from typing import List

import pytest

from backend.agents.core.websocket_manager import (
    ConnectionManager,
    StreamConsumerTask,
    get_connection_manager,
)


# ═══════════════════════════════════════════════════════════════════════════
# MOCK WEBSOCKET
# ═══════════════════════════════════════════════════════════════════════════


class MockWebSocket:
    """Mock WebSocket for testing"""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.messages: List[dict] = []
        self.closed = False

    async def accept(self):
        """Accept connection"""
        pass

    async def send_json(self, data: dict):
        """Send JSON message"""
        if not self.closed:
            self.messages.append(data)

    async def receive_json(self):
        """Receive JSON message (not used in tests)"""
        raise NotImplementedError

    async def close(self):
        """Close connection"""
        self.closed = True


# ═══════════════════════════════════════════════════════════════════════════
# TEST: CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_connection_manager_connect_disconnect():
    """Test connecting and disconnecting clients"""
    manager = ConnectionManager()

    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")

    # Connect clients
    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")

    assert len(manager.active_connections) == 2
    print(f"✅ Connected 2 clients: {manager.get_stats()}")

    # Disconnect client 1
    await manager.disconnect(ws1)
    assert len(manager.active_connections) == 1
    print(f"✅ Disconnected client_1: {manager.get_stats()}")

    # Disconnect client 2
    await manager.disconnect(ws2)
    assert len(manager.active_connections) == 0
    print(f"✅ All clients disconnected: {manager.get_stats()}")


@pytest.mark.asyncio
async def test_connection_manager_subscriptions():
    """Test stream subscriptions"""
    manager = ConnectionManager()

    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")

    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")

    # Subscribe client 1 to signals:universe
    await manager.subscribe(ws1, "signals:universe")
    assert "signals:universe" in manager.subscriptions
    assert ws1 in manager.subscriptions["signals:universe"]
    print(f"✅ Client 1 subscribed to signals:universe")

    # Subscribe client 2 to signals:universe and news:realtime
    await manager.subscribe(ws2, "signals:universe")
    await manager.subscribe(ws2, "news:realtime")
    assert len(manager.subscriptions["signals:universe"]) == 2
    assert ws2 in manager.subscriptions["news:realtime"]
    print(f"✅ Client 2 subscribed to 2 streams: {manager.get_stats()}")

    # Unsubscribe client 1
    await manager.unsubscribe(ws1, "signals:universe")
    assert len(manager.subscriptions["signals:universe"]) == 1
    print(f"✅ Client 1 unsubscribed: {manager.get_stats()}")

    # Disconnect clients
    await manager.disconnect(ws1)
    await manager.disconnect(ws2)
    assert len(manager.subscriptions) == 0
    print(f"✅ All subscriptions cleaned up")


@pytest.mark.asyncio
async def test_connection_manager_broadcast_all():
    """Test broadcasting to all clients"""
    manager = ConnectionManager()

    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")
    ws3 = MockWebSocket("client_3")

    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")
    await manager.connect(ws3, "client_3")

    # Broadcast message
    message = {
        "type": "signal",
        "stream": "signals:universe",
        "data": {"symbol": "TSLA", "action": "BUY", "score": 88},
        "timestamp": 1698765432,
    }

    await manager.broadcast(message)

    # Verify all clients received message
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 1
    assert len(ws3.messages) == 1
    assert ws1.messages[0] == message
    print(f"✅ Broadcast to all 3 clients: {message}")

    await manager.disconnect(ws1)
    await manager.disconnect(ws2)
    await manager.disconnect(ws3)


@pytest.mark.asyncio
async def test_connection_manager_broadcast_subscribers_only():
    """Test broadcasting to subscribed clients only"""
    manager = ConnectionManager()

    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")
    ws3 = MockWebSocket("client_3")

    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")
    await manager.connect(ws3, "client_3")

    # Only client 1 and 2 subscribe to signals:final
    await manager.subscribe(ws1, "signals:final")
    await manager.subscribe(ws2, "signals:final")
    # Client 3 subscribes to news:realtime
    await manager.subscribe(ws3, "news:realtime")

    # Broadcast to signals:final subscribers
    signal_message = {
        "type": "signal",
        "stream": "signals:final",
        "data": {"symbol": "NVDA", "decision": "APPROVED"},
        "timestamp": 1698765432,
    }

    await manager.broadcast(signal_message, stream="signals:final")

    # Verify only subscribed clients received message
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 1
    assert len(ws3.messages) == 0  # Not subscribed to signals:final
    print(f"✅ Broadcast to 2 subscribers only (client 3 not subscribed)")

    # Broadcast to news:realtime subscribers
    news_message = {
        "type": "news",
        "stream": "news:realtime",
        "data": {"ticker": "TSLA", "headline": "Earnings beat"},
        "timestamp": 1698765433,
    }

    await manager.broadcast(news_message, stream="news:realtime")

    # Verify only client 3 received news
    assert len(ws1.messages) == 1  # Still 1 (only signal)
    assert len(ws2.messages) == 1  # Still 1 (only signal)
    assert len(ws3.messages) == 1  # Got news
    assert ws3.messages[0] == news_message
    print(f"✅ Broadcast news to 1 subscriber only (client 3)")

    await manager.disconnect(ws1)
    await manager.disconnect(ws2)
    await manager.disconnect(ws3)


@pytest.mark.asyncio
async def test_connection_manager_stats():
    """Test connection statistics"""
    manager = ConnectionManager()

    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")

    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")

    await manager.subscribe(ws1, "signals:universe")
    await manager.subscribe(ws1, "news:realtime")
    await manager.subscribe(ws2, "signals:final")

    stats = manager.get_stats()

    assert stats["total_connections"] == 2
    assert stats["total_subscriptions"] == 3
    assert stats["streams"]["signals:universe"] == 1
    assert stats["streams"]["news:realtime"] == 1
    assert stats["streams"]["signals:final"] == 1

    print(f"✅ Stats: {stats}")

    await manager.disconnect(ws1)
    await manager.disconnect(ws2)


# ═══════════════════════════════════════════════════════════════════════════
# TEST: STREAM CONSUMER (Mock)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_stream_consumer_broadcast():
    """Test StreamConsumerTask broadcasting (with mock data)"""
    from backend.agents.core.data_layer import get_data_layer

    manager = ConnectionManager()
    ws1 = MockWebSocket("client_1")
    ws2 = MockWebSocket("client_2")

    await manager.connect(ws1, "client_1")
    await manager.connect(ws2, "client_2")

    # Subscribe to signals:universe
    await manager.subscribe(ws1, "signals:universe")
    await manager.subscribe(ws2, "signals:universe")

    # Publish test signal to Redis Stream
    streams, _ = await get_data_layer()
    test_signal = {
        "symbol": "AAPL",
        "action": "BUY",
        "score": 82,
        "agent": "scanner_test",
    }
    await streams.publish_signal("signals:universe", test_signal)

    # Create consumer task (but don't start it - manual consume for test)
    consumer = StreamConsumerTask(
        connection_manager=manager,
        streams=["signals:universe"],
        group_name="test_group",
        consumer_name="test_consumer",
    )

    # Manually consume and broadcast
    signals = await streams.consume_signals(
        stream="signals:universe",
        group="test_group",
        consumer="test_consumer",
        count=1,
        block=1000,
    )

    assert len(signals) == 1
    print(f"✅ Consumed 1 signal from stream: {signals[0]}")

    # Manually broadcast
    await consumer._broadcast_message("signals:universe", signals[0])

    # Verify both clients received message
    assert len(ws1.messages) >= 1
    assert len(ws2.messages) >= 1
    assert ws1.messages[-1]["type"] == "signal"
    assert ws1.messages[-1]["data"] == test_signal
    print(f"✅ Broadcast signal to 2 clients: {ws1.messages[-1]}")

    await manager.disconnect(ws1)
    await manager.disconnect(ws2)


# ═══════════════════════════════════════════════════════════════════════════
# TEST: SINGLETON
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_singleton_manager():
    """Test singleton ConnectionManager"""
    manager1 = get_connection_manager()
    manager2 = get_connection_manager()

    assert manager1 is manager2
    print(f"✅ Singleton working: {id(manager1)} == {id(manager2)}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CORE ENGINE - WebSocket Manager Test Suite")
    print("=" * 80 + "\n")

    async def run_all_tests():
        await test_connection_manager_connect_disconnect()
        print()
        await test_connection_manager_subscriptions()
        print()
        await test_connection_manager_broadcast_all()
        print()
        await test_connection_manager_broadcast_subscribers_only()
        print()
        await test_connection_manager_stats()
        print()
        await test_stream_consumer_broadcast()
        print()
        await test_singleton_manager()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80 + "\n")

    asyncio.run(run_all_tests())
