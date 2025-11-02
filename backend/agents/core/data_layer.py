"""
FlowMind CORE ENGINE - Data Layer (Redis Streams + TimeSeries)

EXTENDS redis_fallback.py with:
- Redis Streams: Event streaming for signals and news
- Redis TimeSeries: Historical news tracking
- 100% compatible with existing redis_fallback.get_kv()

Architecture:
- Reuses existing Redis connection from redis_fallback.py
- Adds Streams methods: publish_signal(), consume_signals(), create_stream()
- Adds TimeSeries methods: add_news_event(), query_news_history()
- Fallback: Streams → in-memory queues, TimeSeries → in-memory lists

Streams:
- signals:universe - Scanner signals (167 workers)
- signals:validated:{team_lead_id} - Team Lead validated signals (20 leads)
- signals:approved:{sector_head_id} - Sector Head approved signals (10 heads)
- signals:final - Master Director final decisions (1 director)
- news:realtime - Real-time news events (<1s latency)
- news:macro - Macro news events (5-15min latency)

TimeSeries Keys:
- news:history:{ticker} - Per-ticker news history (7 days retention)
- news:sentiment:{ticker} - Sentiment scores over time
- signals:performance:{agent_id} - Agent performance tracking (30 days)

Author: FlowMind Team
Created: November 2, 2025
Based on: redis_fallback.py (115 lines, existing)
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

# CRITICAL: Import from existing redis_fallback.py (no duplication!)
from redis_fallback import get_kv

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY FALLBACKS (when Redis unavailable)
# ═══════════════════════════════════════════════════════════════════════════


class InMemoryStream:
    """In-memory fallback for Redis Streams (FIFO queue with consumer groups)"""

    def __init__(self, maxlen: int = 10000):
        self.messages: deque = deque(maxlen=maxlen)
        self.consumer_groups: Dict[str, int] = {}  # {group_name: last_index}
        self.message_id_counter = 0

    async def add(self, data: Dict[str, Any]) -> str:
        """Add message to stream (like XADD)"""
        self.message_id_counter += 1
        msg_id = f"{int(time.time() * 1000)}-{self.message_id_counter}"
        self.messages.append((msg_id, data))
        return msg_id

    async def read(
        self, group: str, consumer: str, count: int = 10, block: int = 0
    ) -> List[Tuple[str, Dict]]:
        """Read messages from stream (like XREADGROUP)"""
        if group not in self.consumer_groups:
            self.consumer_groups[group] = 0

        last_index = self.consumer_groups[group]
        messages = list(self.messages)[last_index : last_index + count]

        if messages:
            self.consumer_groups[group] = last_index + len(messages)

        # Simulate blocking
        if not messages and block > 0:
            await asyncio.sleep(min(block / 1000, 1))

        return messages

    async def create_group(self, group: str) -> bool:
        """Create consumer group (like XGROUP CREATE)"""
        if group not in self.consumer_groups:
            self.consumer_groups[group] = 0
            return True
        return False


class InMemoryTimeSeries:
    """In-memory fallback for Redis TimeSeries (time-sorted list with retention)"""

    def __init__(self, retention_seconds: int = 604800):  # 7 days default
        self.data: deque = deque()
        self.retention = retention_seconds

    async def add(self, timestamp: int, value: float) -> bool:
        """Add data point (like TS.ADD)"""
        self.data.append((timestamp, value))
        await self._purge_old()
        return True

    async def range(
        self, from_ts: int, to_ts: int
    ) -> List[Tuple[int, float]]:
        """Query time range (like TS.RANGE)"""
        await self._purge_old()
        return [(ts, val) for ts, val in self.data if from_ts <= ts <= to_ts]

    async def _purge_old(self):
        """Remove data older than retention period"""
        cutoff = int(time.time()) - self.retention
        while self.data and self.data[0][0] < cutoff:
            self.data.popleft()


# ═══════════════════════════════════════════════════════════════════════════
# REDIS STREAMS MANAGER
# ═══════════════════════════════════════════════════════════════════════════


class RedisStreamsManager:
    """
    Redis Streams wrapper for event streaming.

    Features:
    - Publisher: publish_signal(), publish_news()
    - Consumer: consume_signals() with consumer groups
    - Stream management: create_stream(), get_stream_length()
    - Fallback: In-memory queues when Redis unavailable
    """

    def __init__(self):
        self.fallback_streams: Dict[str, InMemoryStream] = defaultdict(
            InMemoryStream
        )
        self.use_fallback = False

    async def _get_client(self):
        """Get Redis client or fallback to in-memory"""
        try:
            client = await get_kv()
            # Test connection
            await client.ping()
            # Check if real Redis (has execute_command method)
            if not hasattr(client, "execute_command"):
                logger.warning(
                    "Redis client is AsyncTTLDict (fallback), using in-memory"
                )
                self.use_fallback = True
                return None
            self.use_fallback = False
            return client
        except Exception as e:
            logger.warning(
                f"Redis Streams unavailable, using in-memory fallback: {e}"
            )
            self.use_fallback = True
            return None

    async def publish_signal(
        self, stream: str, signal_data: Dict[str, Any]
    ) -> str:
        """
        Publish signal to Redis Stream.

        Args:
            stream: Stream name (e.g., 'signals:universe')
            signal_data: Signal payload (dict)

        Returns:
            Message ID (e.g., '1698765432000-0')
        """
        client = await self._get_client()

        if self.use_fallback:
            msg_id = await self.fallback_streams[stream].add(signal_data)
            logger.debug(f"Published to in-memory stream {stream}: {msg_id}")
            return msg_id

        try:
            # Redis XADD: Add to stream with auto-generated ID
            # MAXLEN ~1000: Keep last ~1000 messages (approximate trimming)
            msg_id = await client.execute_command(
                "XADD",
                stream,
                "MAXLEN",
                "~",
                "1000",
                "*",
                "data",
                json.dumps(signal_data),
            )
            logger.debug(f"Published to Redis stream {stream}: {msg_id}")
            return msg_id.decode() if isinstance(msg_id, bytes) else msg_id
        except Exception as e:
            logger.error(f"Failed to publish to stream {stream}: {e}")
            # Fallback to in-memory
            self.use_fallback = True
            return await self.fallback_streams[stream].add(signal_data)

    async def consume_signals(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block: int = 5000,
    ) -> List[Dict[str, Any]]:
        """
        Consume signals from Redis Stream (consumer group pattern).

        Args:
            stream: Stream name (e.g., 'signals:universe')
            group: Consumer group name (e.g., 'team_leads')
            consumer: Consumer name (e.g., 'team_lead_1')
            count: Max messages to read
            block: Block for N milliseconds if no messages (0 = non-blocking)

        Returns:
            List of signal dicts
        """
        client = await self._get_client()

        if self.use_fallback:
            messages = await self.fallback_streams[stream].read(
                group, consumer, count, block
            )
            return [msg[1] for msg in messages]

        try:
            # Create consumer group if not exists
            await self._ensure_consumer_group(stream, group)

            # Redis XREADGROUP: Read from stream with consumer group
            # > means "only new messages not yet delivered to this group"
            result = await client.execute_command(
                "XREADGROUP",
                "GROUP",
                group,
                consumer,
                "COUNT",
                str(count),
                "BLOCK",
                str(block),
                "STREAMS",
                stream,
                ">",
            )

            if not result:
                return []

            # Parse result: [[stream_name, [[msg_id, [field, value, ...]], ...]]]
            messages = []
            for stream_data in result:
                for msg_id, fields in stream_data[1]:
                    # fields = [b'data', b'{...}', ...]
                    data_idx = fields.index(b"data") if b"data" in fields else -1
                    if data_idx >= 0 and data_idx + 1 < len(fields):
                        signal_json = fields[data_idx + 1]
                        signal = json.loads(signal_json)
                        messages.append(signal)

            logger.debug(
                f"Consumed {len(messages)} signals from {stream} (group={group})"
            )
            return messages

        except Exception as e:
            logger.error(f"Failed to consume from stream {stream}: {e}")
            # Fallback
            self.use_fallback = True
            messages = await self.fallback_streams[stream].read(
                group, consumer, count, block
            )
            return [msg[1] for msg in messages]

    async def _ensure_consumer_group(self, stream: str, group: str):
        """Create consumer group if not exists (XGROUP CREATE)"""
        client = await self._get_client()
        if self.use_fallback:
            await self.fallback_streams[stream].create_group(group)
            return

        try:
            # MKSTREAM: Create stream if not exists
            await client.execute_command(
                "XGROUP", "CREATE", stream, group, "0", "MKSTREAM"
            )
            logger.info(f"Created consumer group {group} for stream {stream}")
        except Exception as e:
            # BUSYGROUP error is OK (group already exists)
            if "BUSYGROUP" not in str(e):
                logger.warning(
                    f"Could not create consumer group {group}: {e}"
                )

    async def get_stream_length(self, stream: str) -> int:
        """Get number of messages in stream (XLEN)"""
        client = await self._get_client()

        if self.use_fallback:
            return len(self.fallback_streams[stream].messages)

        try:
            length = await client.execute_command("XLEN", stream)
            return int(length)
        except Exception as e:
            logger.error(f"Failed to get stream length {stream}: {e}")
            return 0


# ═══════════════════════════════════════════════════════════════════════════
# REDIS TIMESERIES MANAGER
# ═══════════════════════════════════════════════════════════════════════════


class RedisTimeSeriesManager:
    """
    Redis TimeSeries wrapper for historical data tracking.

    Features:
    - Add data points: add_news_event(), add_sentiment_score()
    - Query time ranges: query_news_history(), query_sentiment()
    - Automatic retention: 7 days default
    - Fallback: In-memory time-sorted lists

    Note: Requires RedisTimeSeries module installed on Redis server.
    If unavailable, falls back to in-memory storage.
    """

    def __init__(self, default_retention: int = 604800):  # 7 days
        self.default_retention = default_retention
        self.fallback_series: Dict[str, InMemoryTimeSeries] = defaultdict(
            lambda: InMemoryTimeSeries(self.default_retention)
        )
        self.use_fallback = False

    async def _get_client(self):
        """Get Redis client or fallback to in-memory"""
        try:
            client = await get_kv()
            await client.ping()
            # Check if real Redis (has execute_command method)
            if not hasattr(client, "execute_command"):
                logger.warning(
                    "Redis client is AsyncTTLDict (fallback), using in-memory"
                )
                self.use_fallback = True
                return None
            self.use_fallback = False
            return client
        except Exception as e:
            logger.warning(
                f"Redis TimeSeries unavailable, using in-memory fallback: {e}"
            )
            self.use_fallback = True
            return None

    async def add_news_event(
        self, ticker: str, timestamp: Optional[int] = None, sentiment: float = 0.0
    ) -> bool:
        """
        Add news event to ticker's history.

        Args:
            ticker: Stock symbol (e.g., 'TSLA')
            timestamp: Unix timestamp (default: now)
            sentiment: Sentiment score -1.0 to 1.0

        Returns:
            True if added successfully
        """
        ts = timestamp or int(time.time())
        key = f"news:history:{ticker}"
        return await self._add_datapoint(key, ts, sentiment)

    async def add_sentiment_score(
        self, ticker: str, score: float, timestamp: Optional[int] = None
    ) -> bool:
        """Add sentiment score for ticker"""
        ts = timestamp or int(time.time())
        key = f"news:sentiment:{ticker}"
        return await self._add_datapoint(key, ts, score)

    async def add_agent_performance(
        self, agent_id: str, win_rate: float, timestamp: Optional[int] = None
    ) -> bool:
        """Add agent performance metric"""
        ts = timestamp or int(time.time())
        key = f"signals:performance:{agent_id}"
        return await self._add_datapoint(key, ts, win_rate)

    async def _add_datapoint(
        self, key: str, timestamp: int, value: float
    ) -> bool:
        """Generic datapoint addition"""
        client = await self._get_client()

        if self.use_fallback:
            return await self.fallback_series[key].add(timestamp, value)

        try:
            # TS.ADD key timestamp value [RETENTION retention] [LABELS ...]
            await client.execute_command(
                "TS.ADD",
                key,
                str(timestamp),
                str(value),
                "RETENTION",
                str(self.default_retention),
            )
            return True
        except Exception as e:
            # If RedisTimeSeries not installed, fallback
            logger.warning(f"RedisTimeSeries command failed, using fallback: {e}")
            self.use_fallback = True
            return await self.fallback_series[key].add(timestamp, value)

    async def query_news_history(
        self, ticker: str, from_ts: int, to_ts: int
    ) -> List[Tuple[int, float]]:
        """Query news sentiment history for ticker"""
        key = f"news:history:{ticker}"
        return await self._query_range(key, from_ts, to_ts)

    async def query_sentiment(
        self, ticker: str, from_ts: int, to_ts: int
    ) -> List[Tuple[int, float]]:
        """Query sentiment scores for ticker"""
        key = f"news:sentiment:{ticker}"
        return await self._query_range(key, from_ts, to_ts)

    async def query_agent_performance(
        self, agent_id: str, from_ts: int, to_ts: int
    ) -> List[Tuple[int, float]]:
        """Query agent performance history"""
        key = f"signals:performance:{agent_id}"
        return await self._query_range(key, from_ts, to_ts)

    async def _query_range(
        self, key: str, from_ts: int, to_ts: int
    ) -> List[Tuple[int, float]]:
        """Generic time range query"""
        client = await self._get_client()

        if self.use_fallback:
            return await self.fallback_series[key].range(from_ts, to_ts)

        try:
            # TS.RANGE key from_timestamp to_timestamp
            result = await client.execute_command(
                "TS.RANGE", key, str(from_ts), str(to_ts)
            )
            # Result: [[timestamp, value], ...]
            return [(int(ts), float(val)) for ts, val in result]
        except Exception as e:
            logger.warning(f"RedisTimeSeries query failed, using fallback: {e}")
            self.use_fallback = True
            return await self.fallback_series[key].range(from_ts, to_ts)


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON FACTORY
# ═══════════════════════════════════════════════════════════════════════════

_streams_manager: Optional[RedisStreamsManager] = None
_timeseries_manager: Optional[RedisTimeSeriesManager] = None


async def get_data_layer() -> Tuple[RedisStreamsManager, RedisTimeSeriesManager]:
    """
    Get singleton instances of Streams and TimeSeries managers.

    Returns:
        (streams_manager, timeseries_manager)

    Usage:
        streams, timeseries = await get_data_layer()
        await streams.publish_signal('signals:universe', signal_data)
        await timeseries.add_news_event('TSLA', sentiment=0.75)
    """
    global _streams_manager, _timeseries_manager

    if _streams_manager is None:
        _streams_manager = RedisStreamsManager()
        logger.info("Initialized RedisStreamsManager (singleton)")

    if _timeseries_manager is None:
        _timeseries_manager = RedisTimeSeriesManager()
        logger.info("Initialized RedisTimeSeriesManager (singleton)")

    return _streams_manager, _timeseries_manager
