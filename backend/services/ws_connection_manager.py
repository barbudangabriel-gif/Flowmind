"""
WebSocket Connection Manager
Manages multiple frontend client connections and broadcasts messages from UW.
"""

from typing import Dict, Set, List
from fastapi import WebSocket
import asyncio
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """
    Manages multiple WebSocket connections from frontend clients.

    Features:
    - Multi-channel subscription management
    - Broadcast messages to all subscribed clients
    - Auto-cleanup of dead connections
    - Connection statistics and health monitoring

    Example usage:
    manager = WebSocketConnectionManager()

    # Accept new client
    await manager.connect(websocket, "flow-alerts")

    # Broadcast message to all clients on channel
    await manager.broadcast("flow-alerts", {"type": "flow", "data": {...}})

    # Disconnect client
    await manager.disconnect(websocket, "flow-alerts")
    """

    def __init__(self):
    """Initialize connection manager."""
    # Map: channel -> set of WebSocket connections
    self.active_connections: Dict[str, Set[WebSocket]] = {}

    # Lock for thread-safe operations
    self.lock = asyncio.Lock()

    # Statistics
    self.total_connects = 0
    self.total_disconnects = 0
    self.total_messages_sent = 0
    self.start_time = datetime.now()

    async def connect(self, websocket: WebSocket, channel: str):
    """
                Register a new client connection for a channel.

                Args:
                websocket: FastAPI WebSocket connection
                channel: Channel name to subscribe to
                """
    # Accept the WebSocket connection
    await websocket.accept()

    async with self.lock:
        # Create channel set if doesn't exist
    if channel not in self.active_connections:
    self.active_connections[channel] = set()

    # Add websocket to channel
    self.active_connections[channel].add(websocket)
    self.total_connects += 1

    connection_count = len(self.active_connections[channel])
    logger.info(
        f" Client connected to '{channel}' "
        f"(total on channel: {connection_count})"
    )

    async def disconnect(self, websocket: WebSocket, channel: str):
    """
                Remove a client connection from a channel.

                Args:
                websocket: FastAPI WebSocket connection
                channel: Channel name to unsubscribe from
                """
    async with self.lock:
    if channel in self.active_connections:
    self.active_connections[channel].discard(websocket)
    self.total_disconnects += 1

    # Clean up empty channel sets
    if len(self.active_connections[channel]) == 0:
    del self.active_connections[channel]
    logger.info(f"🗑️ Removed empty channel: {channel}")
    else:
    connection_count = len(self.active_connections[channel])
    logger.info(
        f"👋 Client disconnected from '{channel}' "
        f"(remaining: {connection_count})"
    )

    async def broadcast(self, channel: str, message: dict):
    """
                Broadcast a message to all clients subscribed to a channel.

                Args:
                channel: Channel name
                message: Message dict to send (will be JSON serialized)
                """
    if channel not in self.active_connections:
    return  # No clients subscribed to this channel

    # Copy set to avoid modification during iteration
    connections = list(self.active_connections[channel])

    if not connections:
    return

    # Send to all clients in parallel
    tasks = []
    for connection in connections:
    tasks.append(self._send_to_client(connection, channel, message))

    # Wait for all sends to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    self.total_messages_sent += len(connections)

    async def _send_to_client(
        self,
        connection: WebSocket,
        channel: str,
        message: dict
    ):
    """
                Send message to a single client (internal method).

                Args:
                connection: WebSocket connection
                channel: Channel name (for cleanup on error)
                message: Message to send
                """
    try:
    await connection.send_json(message)
    except Exception as e:
    logger.error(f"Failed to send to client: {type(e).__name__}: {e}")
    # Remove dead connection
    await self.disconnect(connection, channel)

    async def broadcast_to_all_channels(self, message: dict):
    """
                Broadcast a message to all clients across all channels.
                Useful for system-wide announcements.

                Args:
                message: Message dict to send
                """
    for channel in list(self.active_connections.keys()):
    await self.broadcast(channel, message)

    def get_connection_count(self, channel: str = None) -> int:
    """
                Get number of active connections.

                Args:
                channel: Optional channel name. If None, returns total across all channels.

                Returns:
                int: Number of active connections
                """
    if channel:
    return len(self.active_connections.get(channel, set()))
    else:
    return sum(len(conns) for conns in self.active_connections.values())

    def get_channels(self) -> List[str]:
    """
                Get list of active channels (channels with at least one connection).

                Returns:
                List of channel names
                """
    return list(self.active_connections.keys())

    def get_stats(self) -> Dict:
    """
                Get connection statistics.

                Returns:
                Dict with statistics (total connects, disconnects, messages, etc.)
                """
    uptime = (datetime.now() - self.start_time).total_seconds()

    channel_stats = {}
    for channel, connections in self.active_connections.items():
    channel_stats[channel] = len(connections)

    return {
        "total_connections": self.get_connection_count(),
        "total_connects": self.total_connects,
        "total_disconnects": self.total_disconnects,
        "total_messages_sent": self.total_messages_sent,
        "active_channels": len(
            self.active_connections),
        "channels": channel_stats,
        "uptime_seconds": round(
            uptime,
            1),
        "messages_per_second": round(
            self.total_messages_sent /
            uptime,
            2) if uptime > 0 else 0}

    def has_subscribers(self, channel: str) -> bool:
    """
                Check if a channel has any active subscribers.

                Args:
                channel: Channel name

                Returns:
                bool: True if channel has at least one subscriber
                """
    return channel in self.active_connections and len(
        self.active_connections[channel]) > 0

    async def ping_all(self) -> Dict[str, int]:
    """
                Send ping to all connections to verify they're alive.
                Returns count of successful pings per channel.

                Returns:
                Dict mapping channel names to successful ping count
                """
    results = {}

    for channel in list(self.active_connections.keys()):
    connections = list(self.active_connections[channel])
    successful_pings = 0

    for connection in connections:
    try:
        # Send a ping message
    await connection.send_json({
        "type": "ping",
        "timestamp": datetime.now().isoformat()
    })
    successful_pings += 1
    except Exception as e:
    logger.warning(f"Ping failed for client on {channel}: {e}")
    await self.disconnect(connection, channel)

    results[channel] = successful_pings

    return results

    async def cleanup_dead_connections(self):
    """
                Remove all dead/closed connections.
                Useful for periodic cleanup.
                """
    cleaned_count = 0

    for channel in list(self.active_connections.keys()):
    connections = list(self.active_connections[channel])

    for connection in connections:
    try:
        # Try to send a small message to test connection
    await connection.send_json({"type": "health_check"})
    except Exception:
        # Connection is dead
    await self.disconnect(connection, channel)
    cleaned_count += 1

    if cleaned_count > 0:
    logger.info(f"🧹 Cleaned up {cleaned_count} dead connections")

    return cleaned_count


# Global singleton instance
ws_manager = WebSocketConnectionManager()

# Periodic cleanup task (optional - run this in background)


async def periodic_cleanup_task():
    """
    Background task to periodically clean up dead connections.
    Run this with asyncio.create_task() on app startup.
    """
    while True:
    await asyncio.sleep(60)  # Run every 60 seconds
    try:
    cleaned = await ws_manager.cleanup_dead_connections()
    if cleaned > 0:
    logger.info(f"Periodic cleanup removed {cleaned} connections")
    except Exception as e:
    logger.error(f"Error in periodic cleanup: {e}")
