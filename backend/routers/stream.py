"""
WebSocket Streaming API Endpoints
Real-time data streaming from Unusual Whales to frontend clients.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ws_connection_manager import ws_manager
from integrations.uw_websocket_client import UWWebSocketClient
import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stream", tags=["stream"])

# Global UW WebSocket client (singleton)
uw_client: Optional[UWWebSocketClient] = None
uw_listen_task: Optional[asyncio.Task] = None
_initialized = False

# ============================================================================
# Initialization Function (call from main app lifespan)
# ============================================================================

async def initialize_websocket():
 """
 Initialize UW WebSocket client.
 Call this from your main app's lifespan context manager.
 """
 global uw_client, uw_listen_task, _initialized
 
 if _initialized:
 return
 
 logger.info(" Initializing WebSocket streaming service...")
 
 # Get API token from environment
 uw_api_token = (
 os.getenv("UW_API_TOKEN") or 
 os.getenv("UW_KEY") or 
 os.getenv("UNUSUAL_WHALES_API_KEY")
 )
 
 if not uw_api_token:
 logger.warning(
 " UW_API_TOKEN not set - WebSocket streaming DISABLED"
 )
 logger.warning(
 " Set UW_API_TOKEN environment variable to enable real-time streaming"
 )
 _initialized = True
 return
 
 # Create WebSocket client
 uw_client = UWWebSocketClient(uw_api_token)
 
 # Connect to UW
 success = await uw_client.connect()
 
 if success:
 logger.info(" Connected to Unusual Whales WebSocket")
 
 # Start listening in background
 uw_listen_task = asyncio.create_task(uw_client.listen())
 logger.info(" WebSocket listen task started")
 
 else:
 logger.error(" Failed to connect to Unusual Whales WebSocket")
 logger.error(" Streaming features will not be available")
 uw_client = None
 
 _initialized = True

async def shutdown_websocket():
 """
 Cleanup WebSocket connections.
 Call this from your main app's lifespan context manager.
 """
 global uw_client, uw_listen_task
 
 logger.info("🛑 Shutting down WebSocket streaming service...")
 
 # Cancel listen task
 if uw_listen_task:
 uw_listen_task.cancel()
 try:
 await uw_listen_task
 except asyncio.CancelledError:
 pass
 
 # Disconnect from UW
 if uw_client:
 await uw_client.disconnect()
 
 logger.info(" WebSocket streaming service stopped")

# Remove old event handlers - they don't work reliably
# Use lifespan context manager in main app instead

# ============================================================================
# WebSocket Endpoints - Real-time Streaming
# ============================================================================

@router.websocket("/ws/flow")
async def stream_flow_alerts(websocket: WebSocket):
 """
 Stream real-time options flow alerts from Unusual Whales.
 
 **Connection:** wss://your-backend.com/api/stream/ws/flow
 
 **Message Format:**
 ```json
 {
 "channel": "flow-alerts",
 "timestamp": "2025-10-14T12:34:56.789Z",
 "data": {
 "ticker_symbol": "TSLA",
 "put_call": "CALL",
 "strike": 250.0,
 "expiration_date": "2025-11-15",
 "ask_side_premium": 265000,
 ...
 }
 }
 ```
 """
 channel = "flow-alerts"
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 # Connect frontend client
 await ws_manager.connect(websocket, channel)
 logger.info(f"🔌 Frontend client connected to {channel}")
 
 # Define handler that broadcasts to all clients
 async def flow_handler(ch: str, payload: dict):
 """Broadcast flow alerts to all subscribed frontend clients"""
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 # Subscribe to UW channel if not already subscribed
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 First subscriber - subscribing to UW {channel}")
 await uw_client.subscribe(channel, flow_handler)
 else:
 # Already subscribed, just register callback
 uw_client.message_handlers[channel] = flow_handler
 
 try:
 # Keep connection alive - just wait for client messages (e.g., pings)
 while True:
 try:
 # Receive messages from client (if any)
 data = await websocket.receive_text()
 # Could handle client messages here (e.g., filters)
 logger.debug(f"Received from client: {data}")
 except WebSocketDisconnect:
 break
 
 except Exception as e:
 logger.error(f"Error in flow stream: {e}")
 
 finally:
 # Cleanup
 await ws_manager.disconnect(websocket, channel)
 
 # Unsubscribe from UW if no more clients
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 Last subscriber - unsubscribing from UW {channel}")
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/gex/{ticker}")
async def stream_gamma_exposure(websocket: WebSocket, ticker: str):
 """
 Stream real-time gamma exposure (GEX) updates for a specific ticker.
 
 ** VERIFIED CHANNEL** - Confirmed working with UW API
 
 **Connection:** wss://your-backend.com/api/stream/ws/gex/SPY
 
 **Parameters:**
 - `ticker`: Stock symbol (e.g., SPY, TSLA, AAPL, NVDA)
 
 **Message Format:**
 ```json
 {
 "channel": "gex:SPY",
 "timestamp": "2025-10-14T12:34:56.789Z",
 "data": {
 "ticker": "SPY",
 "total_gex": 125000000,
 "call_gex": 85000000,
 "put_gex": 40000000,
 "zero_gamma_level": 445.5,
 "strikes": [
 {"strike": 440, "gex": 5000000},
 {"strike": 445, "gex": 25000000}
 ]
 }
 }
 ```
 """
 ticker = ticker.upper()
 channel = f"gex:{ticker}"
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 # Connect frontend client
 await ws_manager.connect(websocket, channel)
 logger.info(f"🔌 Frontend client connected to {channel}")
 
 # Define handler that broadcasts to all clients
 async def gex_handler(ch: str, payload: dict):
 """Broadcast GEX updates to all subscribed frontend clients"""
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 # Subscribe to UW channel if not already subscribed
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 First subscriber - subscribing to UW {channel}")
 await uw_client.subscribe(channel, gex_handler)
 else:
 # Already subscribed, just register callback
 uw_client.message_handlers[channel] = gex_handler
 
 try:
 # Keep connection alive
 while True:
 try:
 data = await websocket.receive_text()
 logger.debug(f"Received from client on {channel}: {data}")
 except WebSocketDisconnect:
 break
 
 except Exception as e:
 logger.error(f"Error in GEX stream for {ticker}: {e}")
 
 finally:
 # Cleanup
 await ws_manager.disconnect(websocket, channel)
 
 # Unsubscribe from UW if no more clients
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 Last subscriber - unsubscribing from UW {channel}")
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/option-trades/{ticker}")
async def stream_option_trades(websocket: WebSocket, ticker: str):
 """
 Stream real-time option trades for a specific ticker.
 
 ** VERIFIED CHANNEL** - Confirmed from UW official examples
 
 **Connection:** wss://your-backend.com/api/stream/ws/option-trades/TSLA
 
 **Parameters:**
 - `ticker`: Stock symbol (e.g., TSLA, AAPL, NVDA, SPY)
 
 **Message Format:**
 ```json
 {
 "channel": "option_trades:TSLA",
 "timestamp": "2025-10-14T12:34:56.789Z",
 "data": {
 "ticker": "TSLA",
 "strike": 250,
 "expiry": "2025-11-15",
 "type": "CALL",
 "side": "BUY",
 "price": 5.30,
 "quantity": 100,
 "premium": 53000,
 "timestamp": "2025-10-14T12:34:56Z"
 }
 }
 ```
 
 **Use Cases:**
 - Monitor all option trades for a specific ticker
 - Track large trades (whales) in real-time
 - Analyze trade patterns and flow direction
 - Build trade volume heatmaps
 """
 ticker = ticker.upper()
 channel = f"option_trades:{ticker}"
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 # Connect frontend client
 await ws_manager.connect(websocket, channel)
 logger.info(f"🔌 Frontend client connected to {channel}")
 
 # Define handler that broadcasts to all clients
 async def trades_handler(ch: str, payload: dict):
 """Broadcast option trades to all subscribed frontend clients"""
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 # Subscribe to UW channel if not already subscribed
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 First subscriber - subscribing to UW {channel}")
 await uw_client.subscribe(channel, trades_handler)
 else:
 # Already subscribed, just register callback
 uw_client.message_handlers[channel] = trades_handler
 
 try:
 # Keep connection alive
 while True:
 try:
 data = await websocket.receive_text()
 logger.debug(f"Received from client on {channel}: {data}")
 except WebSocketDisconnect:
 break
 
 except Exception as e:
 logger.error(f"Error in option trades stream for {ticker}: {e}")
 
 finally:
 # Cleanup
 await ws_manager.disconnect(websocket, channel)
 
 # Unsubscribe from UW if no more clients
 if not ws_manager.has_subscribers(channel):
 logger.info(f"📡 Last subscriber - unsubscribing from UW {channel}")
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/market-movers")
async def stream_market_movers(websocket: WebSocket):
 """
 Stream real-time market movers data.
 
 ** EXPERIMENTAL CHANNEL** - Not officially verified by UW API
 This channel may not receive updates or could have a different name.
 
 **Note:** Channel name might vary - check UW docs for exact channel name.
 This is a placeholder implementation.
 """
 channel = "market_movers" # TODO: Verify actual UW channel name
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 await ws_manager.connect(websocket, channel)
 logger.info(f"🔌 Frontend client connected to {channel}")
 
 async def movers_handler(ch: str, payload: dict):
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 if not ws_manager.has_subscribers(channel):
 try:
 await uw_client.subscribe(channel, movers_handler)
 except Exception as e:
 logger.warning(f"Could not subscribe to {channel}: {e}")
 # Channel might not exist - close connection
 await websocket.close(code=1011, reason=f"Channel {channel} not available")
 return
 else:
 uw_client.message_handlers[channel] = movers_handler
 
 try:
 while True:
 await websocket.receive_text()
 except WebSocketDisconnect:
 pass
 finally:
 await ws_manager.disconnect(websocket, channel)
 if not ws_manager.has_subscribers(channel):
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/dark-pool")
async def stream_dark_pool(websocket: WebSocket):
 """
 Stream real-time dark pool activity.
 
 ** EXPERIMENTAL CHANNEL** - Not officially verified by UW API
 This channel may not receive updates or could have a different name.
 
 **Note:** Channel name might vary - check UW docs for exact channel name.
 """
 channel = "dark_pool" # TODO: Verify actual UW channel name
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 await ws_manager.connect(websocket, channel)
 
 async def darkpool_handler(ch: str, payload: dict):
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 if not ws_manager.has_subscribers(channel):
 try:
 await uw_client.subscribe(channel, darkpool_handler)
 except Exception as e:
 logger.warning(f"Could not subscribe to {channel}: {e}")
 await websocket.close(code=1011, reason=f"Channel {channel} not available")
 return
 else:
 uw_client.message_handlers[channel] = darkpool_handler
 
 try:
 while True:
 await websocket.receive_text()
 except WebSocketDisconnect:
 pass
 finally:
 await ws_manager.disconnect(websocket, channel)
 if not ws_manager.has_subscribers(channel):
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/congress")
async def stream_congress_trades(websocket: WebSocket):
 """
 Stream real-time congress trade filings.
 
 ** EXPERIMENTAL CHANNEL** - Not officially verified by UW API
 This channel may not receive updates or could have a different name.
 
 **Note:** Channel name might vary - check UW docs for exact channel name.
 """
 channel = "congress_trades" # TODO: Verify actual UW channel name
 
 if not uw_client:
 await websocket.close(code=1011, reason="WebSocket streaming not available")
 return
 
 await ws_manager.connect(websocket, channel)
 
 async def congress_handler(ch: str, payload: dict):
 message = {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 }
 await ws_manager.broadcast(channel, message)
 
 if not ws_manager.has_subscribers(channel):
 try:
 await uw_client.subscribe(channel, congress_handler)
 except Exception as e:
 logger.warning(f"Could not subscribe to {channel}: {e}")
 await websocket.close(code=1011, reason=f"Channel {channel} not available")
 return
 else:
 uw_client.message_handlers[channel] = congress_handler
 
 try:
 while True:
 await websocket.receive_text()
 except WebSocketDisconnect:
 pass
 finally:
 await ws_manager.disconnect(websocket, channel)
 if not ws_manager.has_subscribers(channel):
 await uw_client.unsubscribe(channel)

# ============================================================================
# HTTP Endpoints - Status & Health
# ============================================================================

@router.get("/status")
async def websocket_status():
 """
 Get WebSocket connection status and statistics.
 
 **Response:**
 ```json
 {
 "status": "connected",
 "uw_connection": {...},
 "client_connections": {...},
 "total_clients": 5
 }
 ```
 """
 if not uw_client:
 return {
 "status": "disabled",
 "message": "WebSocket streaming not initialized (UW_API_TOKEN not set)",
 "enabled": False
 }
 
 uw_stats = uw_client.get_stats()
 manager_stats = ws_manager.get_stats()
 
 return {
 "status": "connected" if uw_stats["connected"] else "disconnected",
 "enabled": True,
 "uw_connection": uw_stats,
 "client_connections": manager_stats,
 "total_clients": ws_manager.get_connection_count()
 }

@router.get("/channels")
async def list_channels():
 """
 List available streaming channels.
 
 **Response:**
 ```json
 {
 "channels": [
 {
 "id": "flow-alerts",
 "name": "Options Flow Alerts",
 "endpoint": "ws://backend/api/stream/ws/flow",
 "active_subscribers": 3
 },
 ...
 ]
 }
 ```
 """
 channels = [
 {
 "id": "flow-alerts",
 "name": "Options Flow Alerts",
 "endpoint": "/api/stream/ws/flow",
 "description": "Real-time options flow activity and unusual trades",
 "active_subscribers": ws_manager.get_connection_count("flow-alerts"),
 "verified": True # We know this channel exists
 },
 {
 "id": "market-movers",
 "name": "Market Movers",
 "endpoint": "/api/stream/ws/market-movers",
 "description": "Real-time market movers and top gainers/losers",
 "active_subscribers": ws_manager.get_connection_count("market_movers"),
 "verified": False # Need to verify channel name with UW
 },
 {
 "id": "dark-pool",
 "name": "Dark Pool",
 "endpoint": "/api/stream/ws/dark-pool",
 "description": "Real-time dark pool activity and volume",
 "active_subscribers": ws_manager.get_connection_count("dark_pool"),
 "verified": False
 },
 {
 "id": "congress",
 "name": "Congress Trades",
 "endpoint": "/api/stream/ws/congress",
 "description": "Real-time congressional trade filings",
 "active_subscribers": ws_manager.get_connection_count("congress_trades"),
 "verified": False
 }
 ]
 
 return {
 "channels": channels,
 "total_channels": len(channels),
 "enabled": uw_client is not None
 }

@router.get("/health")
async def health_check():
 """
 Health check endpoint for WebSocket service.
 
 Returns:
 200 if service is healthy
 503 if service is unavailable
 """
 if not uw_client:
 raise HTTPException(
 status_code=503,
 detail="WebSocket streaming service not available"
 )
 
 stats = uw_client.get_stats()
 
 if not stats["connected"]:
 raise HTTPException(
 status_code=503,
 detail="Not connected to Unusual Whales WebSocket"
 )
 
 return {
 "status": "healthy",
 "connected": True,
 "uptime_seconds": stats.get("last_message_seconds_ago", 0)
 }

@router.post("/reconnect")
async def force_reconnect():
 """
 Force reconnection to UW WebSocket.
 Useful for debugging or recovering from errors.
 
 **Admin endpoint** - should be protected in production.
 """
 if not uw_client:
 raise HTTPException(
 status_code=503,
 detail="WebSocket client not initialized"
 )
 
 logger.info("🔄 Forcing WebSocket reconnection...")
 
 try:
 # Disconnect
 await uw_client.disconnect()
 
 # Wait a bit
 await asyncio.sleep(2)
 
 # Reconnect
 success = await uw_client.connect()
 
 if success:
 # Restart listen task
 global uw_listen_task
 if uw_listen_task:
 uw_listen_task.cancel()
 uw_listen_task = asyncio.create_task(uw_client.listen())
 
 return {
 "status": "success",
 "message": "Reconnected to Unusual Whales WebSocket"
 }
 else:
 raise HTTPException(
 status_code=500,
 detail="Failed to reconnect"
 )
 
 except Exception as e:
 logger.error(f"Reconnection failed: {e}")
 raise HTTPException(
 status_code=500,
 detail=f"Reconnection error: {str(e)}"
 )
