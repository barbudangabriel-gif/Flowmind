"""
Unusual Whales WebSocket Client
Based on official UW examples and tested with Pro tier API.

Features:
- Real-time streaming from UW API
- Auto-reconnect with exponential backoff
- Multi-channel subscriptions
- Health monitoring with ping/pong
- Message buffering and callbacks
"""

import websockets
import asyncio
import json
import logging
import os
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime
import secrets

logger = logging.getLogger(__name__)

# Configuration (from official UW examples)
TIMEOUT_LENGTH = 30  # seconds
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_DELAY = 5  # seconds
RECONNECT_DELAY_MAX = 60  # seconds


class UWWebSocketClient:
    """
    WebSocket client for Unusual Whales streaming API.

    Example usage:
        client = UWWebSocketClient(api_token="your_token")
        await client.connect()

        async def flow_handler(channel, payload):
            print(f"Flow alert: {payload}")

        await client.subscribe("flow-alerts", flow_handler)
        await client.listen()
    """

    def __init__(self, api_token: str):
        """
        Initialize WebSocket client.

        Args:
            api_token: Unusual Whales API token (Pro tier required for WebSocket)
        """
        self.api_token = api_token
        self.uri = f"wss://api.unusualwhales.com/socket?token={api_token}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.reconnect_attempt = 0
        self.message_handlers: Dict[str, Callable] = {}
        self.last_message_time = datetime.now()

    async def connect(self) -> bool:
        """
        Establish WebSocket connection to UW API.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to Unusual Whales WebSocket...")
            self.ws = await websockets.connect(
                self.uri,
                ping_interval=20,  # Send ping every 20s
                ping_timeout=10,  # Wait 10s for pong response
            )
            self.running = True
            self.last_message_time = datetime.now()
            logger.info(" WebSocket connected to Unusual Whales")
            return True

        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"Connection failed with status {e.status_code}")
            if e.status_code == 401:
                logger.error("Invalid API token (401 Unauthorized)")
            elif e.status_code == 403:
                logger.error("Access forbidden - WebSocket not available on your plan")
            return False

        except Exception as e:
            logger.error(f"Failed to connect: {type(e).__name__}: {e}")
            return False

    async def subscribe(self, channel: str, callback: Callable[[str, Dict], Any]):
        """
        Subscribe to a channel and register message callback.

        Args:
            channel: Channel name (e.g., "flow-alerts", "gex:SPY", "option_trades:TSLA")
            callback: Async function called with (channel, payload) on each message

        Raises:
            RuntimeError: If not connected to WebSocket
        """
        if not self.ws:
            raise RuntimeError("Not connected to WebSocket")

        # Register callback for this channel
        self.message_handlers[channel] = callback

        # Send subscription message to UW
        subscribe_msg = {"channel": channel, "msg_type": "join"}
        await self.ws.send(json.dumps(subscribe_msg))
        logger.info(f"📡 Subscribed to channel: {channel}")

    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from a channel.

        Args:
            channel: Channel name to unsubscribe from
        """
        if not self.ws:
            return

        # Send unsubscribe message
        unsubscribe_msg = {"channel": channel, "msg_type": "leave"}

        try:
            await self.ws.send(json.dumps(unsubscribe_msg))
        except Exception as e:
            logger.warning(f"Failed to send unsubscribe for {channel}: {e}")

        # Remove callback
        if channel in self.message_handlers:
            del self.message_handlers[channel]
        logger.info(f"📡 Unsubscribed from channel: {channel}")

    async def listen(self):
        """
        Main message loop - receive and dispatch messages to callbacks.
        Handles reconnection on connection loss.
        """
        while self.running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.ws.recv(), timeout=TIMEOUT_LENGTH)

                self.last_message_time = datetime.now()

                # Parse message: UW format is [channel, payload]
                data = json.loads(message)

                if isinstance(data, list) and len(data) >= 2:
                    channel, payload = data[0], data[1]

                    # Log first few messages for debugging
                    if len(self.message_handlers) <= 3:
                        logger.debug(
                            f"📬 Received on {channel}: {str(payload)[:100]}..."
                        )

                    # Dispatch to registered handler
                    if channel in self.message_handlers:
                        try:
                            callback = self.message_handlers[channel]
                            # Call callback (could be sync or async)
                            if asyncio.iscoroutinefunction(callback):
                                await callback(channel, payload)
                            else:
                                callback(channel, payload)
                        except Exception as e:
                            logger.error(f"Error in callback for {channel}: {e}")
                    else:
                        logger.debug(f"No handler registered for channel: {channel}")
                else:
                    logger.warning(f"Unexpected message format: {data}")

            except asyncio.TimeoutError:
                # No message received in TIMEOUT_LENGTH seconds
                logger.debug(
                    f"No messages for {TIMEOUT_LENGTH}s, checking connection..."
                )

                # Send ping to verify connection is alive
                try:
                    pong_waiter = await self.ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                    logger.debug(" Connection alive (pong received)")
                except Exception:
                    logger.warning("Connection appears dead, triggering reconnect...")
                    raise websockets.exceptions.ConnectionClosed(1006, "Timeout")

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: {e}")
                if self.running:
                    await self._reconnect()
                break

            except asyncio.CancelledError:
                logger.info("Listen task cancelled")
                raise

            except Exception as e:
                logger.error(f"Error in listen loop: {type(e).__name__}: {e}")
                if self.running:
                    await self._reconnect()

    async def _reconnect(self):
        """
        Reconnect with exponential backoff (internal method).
        """
        self.reconnect_attempt += 1

        if self.reconnect_attempt > MAX_RECONNECT_ATTEMPTS:
            logger.error(
                f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached, giving up"
            )
            self.running = False
            return

        # Calculate exponential backoff with jitter
        delay = min(
            RECONNECT_DELAY * (2 ** (self.reconnect_attempt - 1)), RECONNECT_DELAY_MAX
        )
        # Use secrets for cryptographically secure random jitter
        jitter = delay * 0.1 * (secrets.randbelow(1000) / 1000.0)
        reconnect_delay = delay + jitter

        logger.info(
            f"Reconnecting in {reconnect_delay:.1f}s "
            f"(attempt {self.reconnect_attempt}/{MAX_RECONNECT_ATTEMPTS})"
        )
        await asyncio.sleep(reconnect_delay)

        # Attempt reconnection
        success = await self.connect()

        if success:
            # Resubscribe to all channels
            channels = list(self.message_handlers.keys())
            logger.info(f"Resubscribing to {len(channels)} channels...")

            for channel in channels:
                try:
                    subscribe_msg = {"channel": channel, "msg_type": "join"}
                    await self.ws.send(json.dumps(subscribe_msg))
                    logger.info(f" Resubscribed to: {channel}")
                except Exception as e:
                    logger.error(f"Failed to resubscribe to {channel}: {e}")

            # Reset reconnect counter on success
            self.reconnect_attempt = 0

            # Resume listening
            await self.listen()
        else:
            # Connection failed, try again
            await self._reconnect()

    async def disconnect(self):
        """
        Gracefully disconnect from WebSocket.
        """
        logger.info("Disconnecting from WebSocket...")
        self.running = False

        if self.ws:
            try:
                await self.ws.close()
                logger.info(" WebSocket disconnected")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")

        self.ws = None
        self.message_handlers.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.

        Returns:
            Dict with connection status, subscribed channels, etc.
        """
        time_since_message = (datetime.now() - self.last_message_time).total_seconds()

        return {
            "connected": self.ws is not None,
            "running": self.running,
            "reconnect_attempts": self.reconnect_attempt,
            "subscribed_channels": list(self.message_handlers.keys()),
            "channel_count": len(self.message_handlers),
            "last_message_seconds_ago": round(time_since_message, 1),
            "connection_uri": "wss://api.unusualwhales.com/socket",
        }

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is currently connected."""
        return self.ws is not None


# Convenience function for quick testing
async def test_connection(
    api_token: str, channels: List[str] = None, duration: int = 30
):
    """
    Quick test of WebSocket connection.

    Args:
        api_token: UW API token
        channels: List of channels to subscribe to (default: ["flow-alerts"])
        duration: How long to listen in seconds (default: 30)
    """
    if channels is None:
        channels = ["flow-alerts"]

    client = UWWebSocketClient(api_token)

    # Connect
    success = await client.connect()
    if not success:
        logger.error("Failed to connect")
        return

    # Message counter
    message_count = 0

    # Generic message handler
    async def message_handler(channel: str, payload: Dict):
        nonlocal message_count
        message_count += 1
        logger.info(f"📬 [{message_count}] {channel}: {str(payload)[:100]}...")

    # Subscribe to channels
    for channel in channels:
        await client.subscribe(channel, message_handler)

    # Listen for specified duration
    try:
        await asyncio.wait_for(client.listen(), timeout=duration)
    except asyncio.TimeoutError:
        logger.info(f"Test completed after {duration}s")
    finally:
        await client.disconnect()

    logger.info(
        f" Test summary: {message_count} messages received from {len(channels)} channels"
    )


if __name__ == "__main__":
    # Quick test when run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

    token = os.getenv("UW_API_TOKEN")
    if not token:
        print(" Error: UW_API_TOKEN not set")
        print("Usage: export UW_API_TOKEN=your_token && python uw_websocket_client.py")
    else:
        asyncio.run(test_connection(token, ["flow-alerts", "gex:SPY"], duration=30))
