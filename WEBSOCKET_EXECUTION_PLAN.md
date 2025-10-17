# WebSocket Implementation - PLAN EXECUȚIE

**Data:** 2025-10-14 
**Status:** READY TO START 
**Metodă:** 3+2 (Backend 3 părți → Frontend 2 părți)

---

## 📚 CE AM ÎNVĂȚAT din UW Examples:

### **Python Implementation (`ws_demo_multi_channel_and_multi_outfiles.py`):**
 Connection string: `wss://api.unusualwhales.com/socket?token={UW_API_TOKEN}` 
 Subscribe message format: `{"channel": "flow-alerts", "msg_type": "join"}` 
 Message format: `[channel, payload]` (array with 2 elements) 
 Channels available:
- `flow-alerts` - Real-time options flow
- `option_trades:TSLA` - Specific ticker option trades
- `gex:SPY` - Gamma exposure for ticker

 Reconnection logic:
- Exponential backoff: `RECONNECT_DELAY * (2 ** attempt)`
- Max delay: 60 seconds
- Jitter: ±10% random to avoid storms

 Health monitoring:
- Timeout: 30 seconds without message
- Ping/pong to check connection
- Auto-reconnect on failure

---

## IMPLEMENTARE - 4 Features + 1 Manager:

### **Backend - Partea 1: WebSocket Client** 
**File:** `/backend/integrations/uw_websocket_client.py`

```python
import websockets
import asyncio
import json
import logging
from typing import Callable, List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
TIMEOUT_LENGTH = 30
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_DELAY = 5
RECONNECT_DELAY_MAX = 60

class UWWebSocketClient:
 """
 WebSocket client pentru Unusual Whales streaming.
 Based on official UW examples.
 """
 
 def __init__(self, api_token: str):
 self.api_token = api_token
 self.uri = f"wss://api.unusualwhales.com/socket?token={api_token}"
 self.ws = None
 self.running = False
 self.reconnect_attempt = 0
 self.message_handlers = {} # channel -> callback
 
 async def connect(self):
 """Establish WebSocket connection"""
 try:
 self.ws = await websockets.connect(self.uri)
 self.running = True
 logger.info("WebSocket connected to Unusual Whales")
 return True
 except Exception as e:
 logger.error(f"Failed to connect: {e}")
 return False
 
 async def subscribe(self, channel: str, callback: Callable):
 """
 Subscribe to a channel and register callback
 
 Args:
 channel: Channel name (e.g., "flow-alerts", "gex:SPY")
 callback: Function to call when message received
 """
 if not self.ws:
 raise RuntimeError("Not connected")
 
 # Register callback
 self.message_handlers[channel] = callback
 
 # Send subscription message
 subscribe_msg = {
 "channel": channel,
 "msg_type": "join"
 }
 await self.ws.send(json.dumps(subscribe_msg))
 logger.info(f"Subscribed to channel: {channel}")
 
 async def unsubscribe(self, channel: str):
 """Unsubscribe from a channel"""
 if not self.ws:
 return
 
 unsubscribe_msg = {
 "channel": channel,
 "msg_type": "leave"
 }
 await self.ws.send(json.dumps(unsubscribe_msg))
 
 if channel in self.message_handlers:
 del self.message_handlers[channel]
 
 logger.info(f"Unsubscribed from channel: {channel}")
 
 async def listen(self):
 """
 Main message loop - receive and dispatch messages
 """
 try:
 while self.running:
 try:
 # Wait for message with timeout
 message = await asyncio.wait_for(
 self.ws.recv(), 
 timeout=TIMEOUT_LENGTH
 )
 
 # Parse message: [channel, payload]
 data = json.loads(message)
 if isinstance(data, list) and len(data) == 2:
 channel, payload = data
 
 # Dispatch to registered handler
 if channel in self.message_handlers:
 callback = self.message_handlers[channel]
 await callback(channel, payload)
 else:
 logger.warning(f"No handler for channel: {channel}")
 
 except asyncio.TimeoutError:
 # No message in 30s, check connection health
 logger.debug("No message received, checking connection...")
 try:
 pong = await self.ws.ping()
 await asyncio.wait_for(pong, timeout=10)
 logger.debug("Connection is alive (pong received)")
 except:
 logger.warning("Connection appears dead, reconnecting...")
 raise websockets.exceptions.ConnectionClosed(
 1006, "Connection timed out"
 )
 
 except websockets.exceptions.ConnectionClosed as e:
 logger.warning(f"Connection closed: {e}")
 if self.running:
 await self.reconnect()
 
 except Exception as e:
 logger.error(f"Error in listen loop: {e}")
 if self.running:
 await self.reconnect()
 
 async def reconnect(self):
 """Reconnect with exponential backoff"""
 self.reconnect_attempt += 1
 
 if self.reconnect_attempt > MAX_RECONNECT_ATTEMPTS:
 logger.error("Max reconnection attempts reached, giving up")
 self.running = False
 return
 
 # Calculate backoff delay
 delay = min(
 RECONNECT_DELAY * (2 ** (self.reconnect_attempt - 1)),
 RECONNECT_DELAY_MAX
 )
 
 logger.info(f"Reconnecting in {delay}s (attempt {self.reconnect_attempt}/{MAX_RECONNECT_ATTEMPTS})")
 await asyncio.sleep(delay)
 
 # Attempt reconnection
 success = await self.connect()
 if success:
 # Resubscribe to all channels
 for channel in list(self.message_handlers.keys()):
 subscribe_msg = {
 "channel": channel,
 "msg_type": "join"
 }
 await self.ws.send(json.dumps(subscribe_msg))
 logger.info(f"Resubscribed to: {channel}")
 
 # Reset reconnect counter on success
 self.reconnect_attempt = 0
 
 # Resume listening
 await self.listen()
 
 async def disconnect(self):
 """Gracefully disconnect"""
 self.running = False
 if self.ws:
 await self.ws.close()
 logger.info("WebSocket disconnected")
 
 def get_stats(self) -> Dict[str, Any]:
 """Get connection statistics"""
 return {
 "connected": self.ws is not None and self.ws.open,
 "running": self.running,
 "reconnect_attempts": self.reconnect_attempt,
 "subscribed_channels": list(self.message_handlers.keys()),
 "channel_count": len(self.message_handlers)
 }
```

**Tasks:**
- [ ] Create file `/backend/integrations/uw_websocket_client.py`
- [ ] Copy implementation above
- [ ] Test basic connection with real UW token
- [ ] Test subscribe/unsubscribe
- [ ] Test reconnection logic
- [ ] Add unit tests

---

### **Backend - Partea 2: Connection Manager** 🎛️
**File:** `/backend/services/ws_connection_manager.py`

```python
from typing import Dict, List, Set
from fastapi import WebSocket
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebSocketConnectionManager:
 """
 Manages multiple client WebSocket connections.
 Broadcasts messages from UW to connected frontend clients.
 """
 
 def __init__(self):
 # Map: channel -> set of WebSocket connections
 self.active_connections: Dict[str, Set[WebSocket]] = {}
 self.lock = asyncio.Lock()
 
 async def connect(self, websocket: WebSocket, channel: str):
 """Register new client connection"""
 await websocket.accept()
 
 async with self.lock:
 if channel not in self.active_connections:
 self.active_connections[channel] = set()
 
 self.active_connections[channel].add(websocket)
 logger.info(f"Client connected to {channel}. Total: {len(self.active_connections[channel])}")
 
 async def disconnect(self, websocket: WebSocket, channel: str):
 """Remove client connection"""
 async with self.lock:
 if channel in self.active_connections:
 self.active_connections[channel].discard(websocket)
 
 # Clean up empty channels
 if len(self.active_connections[channel]) == 0:
 del self.active_connections[channel]
 
 logger.info(f"Client disconnected from {channel}")
 
 async def broadcast(self, channel: str, message: dict):
 """
 Broadcast message to all clients subscribed to channel
 """
 if channel not in self.active_connections:
 return
 
 # Create list to avoid modification during iteration
 connections = list(self.active_connections[channel])
 
 # Send to all clients
 for connection in connections:
 try:
 await connection.send_json(message)
 except Exception as e:
 logger.error(f"Failed to send to client: {e}")
 # Remove dead connection
 await self.disconnect(connection, channel)
 
 def get_connection_count(self, channel: str = None) -> int:
 """Get number of active connections"""
 if channel:
 return len(self.active_connections.get(channel, set()))
 else:
 return sum(len(conns) for conns in self.active_connections.values())
 
 def get_stats(self) -> Dict[str, int]:
 """Get statistics for all channels"""
 return {
 channel: len(connections)
 for channel, connections in self.active_connections.items()
 }

# Global singleton instance
ws_manager = WebSocketConnectionManager()
```

**Tasks:**
- [ ] Create file `/backend/services/ws_connection_manager.py`
- [ ] Copy implementation above
- [ ] Test with mock WebSocket connections
- [ ] Add stress test (100+ connections)

---

### **Backend - Partea 3: API Endpoints** 
**File:** `/backend/routers/stream.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from backend.services.ws_connection_manager import ws_manager
from backend.integrations.uw_websocket_client import UWWebSocketClient
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stream", tags=["stream"])

# Global UW WebSocket client (singleton)
uw_client: UWWebSocketClient = None

@router.on_event("startup")
async def startup_websocket():
 """Initialize UW WebSocket client on app startup"""
 global uw_client
 
 uw_api_token = os.getenv("UW_API_TOKEN") or os.getenv("UW_KEY")
 if not uw_api_token:
 logger.warning("UW_API_TOKEN not set, WebSocket streaming disabled")
 return
 
 uw_client = UWWebSocketClient(uw_api_token)
 success = await uw_client.connect()
 
 if success:
 # Start listening in background
 asyncio.create_task(uw_client.listen())
 logger.info("UW WebSocket client started")
 else:
 logger.error("Failed to start UW WebSocket client")

@router.on_event("shutdown")
async def shutdown_websocket():
 """Cleanup on app shutdown"""
 global uw_client
 if uw_client:
 await uw_client.disconnect()

# ============================================================================
# WebSocket Endpoints - Each channel gets its own endpoint
# ============================================================================

@router.websocket("/ws/flow")
async def stream_flow_alerts(websocket: WebSocket):
 """
 Stream real-time options flow alerts
 
 Client receives messages in format:
 {
 "channel": "flow-alerts",
 "timestamp": "2025-10-14T12:34:56",
 "data": {...}
 }
 """
 channel = "flow-alerts"
 
 # Connect client
 await ws_manager.connect(websocket, channel)
 
 # Define message handler
 async def flow_handler(ch: str, payload: dict):
 await ws_manager.broadcast(channel, {
 "channel": ch,
 "timestamp": datetime.now().isoformat(),
 "data": payload
 })
 
 # Subscribe to UW channel
 if uw_client:
 await uw_client.subscribe(channel, flow_handler)
 
 try:
 # Keep connection alive
 while True:
 await websocket.receive_text()
 except WebSocketDisconnect:
 await ws_manager.disconnect(websocket, channel)
 if uw_client and ws_manager.get_connection_count(channel) == 0:
 # Unsubscribe if no more clients
 await uw_client.unsubscribe(channel)

@router.websocket("/ws/market-movers")
async def stream_market_movers(websocket: WebSocket):
 """Stream real-time market movers data"""
 # Similar implementation to flow-alerts
 # Channel might be "market_movers" or similar (check UW docs)
 pass

@router.websocket("/ws/dark-pool")
async def stream_dark_pool(websocket: WebSocket):
 """Stream real-time dark pool activity"""
 pass

@router.websocket("/ws/congress")
async def stream_congress_trades(websocket: WebSocket):
 """Stream real-time congress trades"""
 pass

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@router.get("/status")
async def websocket_status():
 """Get WebSocket connection status"""
 if not uw_client:
 return {
 "status": "disabled",
 "message": "WebSocket client not initialized"
 }
 
 stats = uw_client.get_stats()
 connection_stats = ws_manager.get_stats()
 
 return {
 "status": "connected" if stats["connected"] else "disconnected",
 "uw_connection": stats,
 "client_connections": connection_stats,
 "total_clients": ws_manager.get_connection_count()
 }

@router.get("/channels")
async def list_channels():
 """List available channels"""
 return {
 "channels": [
 {
 "id": "flow-alerts",
 "name": "Options Flow Alerts",
 "endpoint": "/api/stream/ws/flow",
 "description": "Real-time options flow activity"
 },
 {
 "id": "market-movers",
 "name": "Market Movers",
 "endpoint": "/api/stream/ws/market-movers",
 "description": "Real-time market movers data"
 },
 {
 "id": "dark-pool",
 "name": "Dark Pool",
 "endpoint": "/api/stream/ws/dark-pool",
 "description": "Real-time dark pool activity"
 },
 {
 "id": "congress",
 "name": "Congress Trades",
 "endpoint": "/api/stream/ws/congress",
 "description": "Real-time congress trade filings"
 }
 ]
 }
```

**Tasks:**
- [ ] Create file `/backend/routers/stream.py`
- [ ] Implement all 4 WebSocket endpoints
- [ ] Add to `server.py` router includes
- [ ] Test each endpoint with real connections
- [ ] Add error handling and logging

---

## FRONTEND PARTS TO COME...

Confirmă că vrei să continui și îți fac și părțile frontend! 

**Următorii pași:**
- Frontend Partea 1: Hooks & Context
- Frontend Partea 2: Live UI Components
- Testing
- Documentation

**Ready to start?** 😊
