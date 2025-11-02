"""
FlowMind CORE ENGINE - WebSocket Manager (Real-time Frontend Updates)

Provides real-time signal/news streaming to frontend via WebSockets.

Architecture:
- FastAPI WebSocket endpoint: /ws/signals
- ConnectionManager: Tracks active connections, broadcasts messages
- Stream Consumer: Consumes from Redis Streams → broadcasts to clients
- Subscription model: Clients can subscribe to specific streams

Streams consumed:
- signals:universe - All scanner signals
- signals:validated:{team_lead_id} - Team Lead validated signals
- signals:approved:{sector_head_id} - Sector Head approved signals
- signals:final - Master Director final decisions
- news:realtime - Real-time news events

Message format:
{
    "type": "signal" | "news" | "status",
    "stream": "signals:universe",
    "data": {...},
    "timestamp": 1698765432
}

Author: FlowMind Team
Created: November 2, 2025
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from agents.core.data_layer import get_data_layer

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════════════════════


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages.

    Features:
    - Connect/disconnect handling
    - Broadcast to all clients
    - Send to specific client
    - Subscription management (clients subscribe to specific streams)
    """

    def __init__(self):
        # Active connections: {websocket: client_info}
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        # Subscriptions: {stream_name: set(websockets)}
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self, websocket: WebSocket, client_id: Optional[str] = None
    ):
        """Accept WebSocket connection and register client"""
        await websocket.accept()
        async with self._lock:
            self.active_connections[websocket] = {
                "client_id": client_id or f"client_{id(websocket)}",
                "connected_at": time.time(),
                "subscriptions": set(),
            }
        logger.info(
            f"Client connected: {self.active_connections[websocket]['client_id']} "
            f"(total: {len(self.active_connections)})"
        )

    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and cleanup subscriptions"""
        async with self._lock:
            if websocket in self.active_connections:
                client_info = self.active_connections[websocket]
                client_id = client_info["client_id"]

                # Remove from subscriptions
                for stream in client_info["subscriptions"]:
                    if stream in self.subscriptions:
                        self.subscriptions[stream].discard(websocket)
                        if not self.subscriptions[stream]:
                            del self.subscriptions[stream]

                # Remove connection
                del self.active_connections[websocket]
                logger.info(
                    f"Client disconnected: {client_id} "
                    f"(remaining: {len(self.active_connections)})"
                )

    async def subscribe(self, websocket: WebSocket, stream: str):
        """Subscribe client to specific stream"""
        async with self._lock:
            if websocket not in self.active_connections:
                return

            # Add to subscriptions
            if stream not in self.subscriptions:
                self.subscriptions[stream] = set()
            self.subscriptions[stream].add(websocket)

            # Update client info
            self.active_connections[websocket]["subscriptions"].add(stream)

            client_id = self.active_connections[websocket]["client_id"]
            logger.info(f"Client {client_id} subscribed to {stream}")

    async def unsubscribe(self, websocket: WebSocket, stream: str):
        """Unsubscribe client from specific stream"""
        async with self._lock:
            if websocket not in self.active_connections:
                return

            # Remove from subscriptions
            if stream in self.subscriptions:
                self.subscriptions[stream].discard(websocket)
                if not self.subscriptions[stream]:
                    del self.subscriptions[stream]

            # Update client info
            self.active_connections[websocket]["subscriptions"].discard(stream)

            client_id = self.active_connections[websocket]["client_id"]
            logger.info(f"Client {client_id} unsubscribed from {stream}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to client: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any], stream: Optional[str] = None):
        """
        Broadcast message to all clients (or only subscribed clients if stream specified)

        Args:
            message: Message dict to send
            stream: Optional stream name (only send to subscribers)
        """
        if stream and stream in self.subscriptions:
            # Send only to subscribers of this stream
            websockets = list(self.subscriptions[stream])
            target_count = len(websockets)
        else:
            # Send to all connected clients
            websockets = list(self.active_connections.keys())
            target_count = len(websockets)

        if not websockets:
            return

        # Broadcast concurrently
        tasks = [ws.send_json(message) for ws in websockets]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle disconnections
        failed = 0
        for ws, result in zip(websockets, results):
            if isinstance(result, Exception):
                logger.error(f"Broadcast failed for client: {result}")
                await self.disconnect(ws)
                failed += 1

        success = target_count - failed
        logger.debug(
            f"Broadcast: {success}/{target_count} clients "
            f"(stream: {stream or 'all'})"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(
                len(subs) for subs in self.subscriptions.values()
            ),
            "streams": {
                stream: len(subs) for stream, subs in self.subscriptions.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# STREAM CONSUMER (Background Task)
# ═══════════════════════════════════════════════════════════════════════════


class StreamConsumerTask:
    """
    Background task that consumes Redis Streams and broadcasts to WebSocket clients.

    Runs continuously, consuming messages from configured streams and
    broadcasting them to subscribed clients.
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        streams: List[str],
        group_name: str = "websocket_consumers",
        consumer_name: str = "ws_consumer_1",
    ):
        self.manager = connection_manager
        self.streams = streams
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background consumer task"""
        if self.running:
            logger.warning("StreamConsumerTask already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._consume_loop())
        logger.info(
            f"Started StreamConsumerTask for streams: {self.streams}"
        )

    async def stop(self):
        """Stop background consumer task"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped StreamConsumerTask")

    async def _consume_loop(self):
        """Main consumer loop (runs in background)"""
        streams_manager, _ = await get_data_layer()

        while self.running:
            try:
                # Consume from all configured streams
                for stream in self.streams:
                    messages = await streams_manager.consume_signals(
                        stream=stream,
                        group=self.group_name,
                        consumer=self.consumer_name,
                        count=10,
                        block=1000,  # Block 1 second
                    )

                    # Broadcast each message
                    for msg in messages:
                        await self._broadcast_message(stream, msg)

                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in StreamConsumerTask: {e}")
                await asyncio.sleep(1)

    async def _broadcast_message(self, stream: str, data: Dict[str, Any]):
        """Format and broadcast message to WebSocket clients"""
        message = {
            "type": self._get_message_type(stream),
            "stream": stream,
            "data": data,
            "timestamp": int(time.time()),
        }

        # Broadcast to subscribers of this stream
        await self.manager.broadcast(message, stream=stream)

    def _get_message_type(self, stream: str) -> str:
        """Determine message type from stream name"""
        if stream.startswith("signals:"):
            return "signal"
        elif stream.startswith("news:"):
            return "news"
        else:
            return "event"


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON MANAGER
# ═══════════════════════════════════════════════════════════════════════════

_connection_manager: Optional[ConnectionManager] = None
_stream_consumer: Optional[StreamConsumerTask] = None


def get_connection_manager() -> ConnectionManager:
    """Get singleton ConnectionManager instance"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
        logger.info("Initialized ConnectionManager (singleton)")
    return _connection_manager


async def start_stream_consumer(
    streams: Optional[List[str]] = None
) -> StreamConsumerTask:
    """
    Start background stream consumer (call on app startup).

    Args:
        streams: List of stream names to consume (default: all core streams)

    Returns:
        StreamConsumerTask instance
    """
    global _stream_consumer

    if _stream_consumer and _stream_consumer.running:
        logger.warning("StreamConsumerTask already running")
        return _stream_consumer

    # Default streams to consume
    if streams is None:
        streams = [
            "signals:universe",
            "signals:final",
            "news:realtime",
        ]

    manager = get_connection_manager()
    _stream_consumer = StreamConsumerTask(
        connection_manager=manager,
        streams=streams,
        group_name="websocket_consumers",
        consumer_name="ws_consumer_1",
    )

    await _stream_consumer.start()
    logger.info(f"Started stream consumer for: {streams}")
    return _stream_consumer


async def stop_stream_consumer():
    """Stop background stream consumer (call on app shutdown)"""
    global _stream_consumer
    if _stream_consumer:
        await _stream_consumer.stop()
        _stream_consumer = None
        logger.info("Stopped stream consumer")


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI WEBSOCKET ENDPOINT (to be mounted in server.py)
# ═══════════════════════════════════════════════════════════════════════════


async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time signal/news streaming.

    Usage in server.py:
        from backend.agents.core.websocket_manager import websocket_endpoint

        @app.websocket("/ws/signals")
        async def websocket_route(websocket: WebSocket):
            await websocket_endpoint(websocket)

    Client-side example (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/signals');
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            console.log(msg.type, msg.stream, msg.data);
        };
        // Subscribe to specific stream
        ws.send(JSON.stringify({action: 'subscribe', stream: 'signals:final'}));
    """
    manager = get_connection_manager()
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive messages from client (e.g., subscription commands)
            data = await websocket.receive_json()

            action = data.get("action")
            stream = data.get("stream")

            if action == "subscribe" and stream:
                await manager.subscribe(websocket, stream)
                await manager.send_personal_message(
                    {
                        "type": "status",
                        "action": "subscribed",
                        "stream": stream,
                        "timestamp": int(time.time()),
                    },
                    websocket,
                )

            elif action == "unsubscribe" and stream:
                await manager.unsubscribe(websocket, stream)
                await manager.send_personal_message(
                    {
                        "type": "status",
                        "action": "unsubscribed",
                        "stream": stream,
                        "timestamp": int(time.time()),
                    },
                    websocket,
                )

            elif action == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": int(time.time())},
                    websocket,
                )

            elif action == "stats":
                stats = manager.get_stats()
                await manager.send_personal_message(
                    {
                        "type": "stats",
                        "data": stats,
                        "timestamp": int(time.time()),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
