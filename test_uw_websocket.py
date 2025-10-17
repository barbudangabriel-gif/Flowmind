#!/usr/bin/env python3
"""
Quick test script to verify Unusual Whales WebSocket connection.
Based on official UW examples.

Usage:
 export UW_API_TOKEN=your_token_here
 python test_uw_websocket.py
"""

import asyncio
import websockets
import json
import os
import sys
from datetime import datetime

# Configuration
UW_API_TOKEN = os.getenv("UW_API_TOKEN") or os.getenv("UW_KEY") or os.getenv("UNUSUAL_WHALES_API_KEY")
TIMEOUT = 30 # seconds

def log(message: str):
 """Print timestamped log message"""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
 print(f"[{timestamp}] {message}")

async def test_websocket_connection():
 """
 Test basic WebSocket connection to Unusual Whales API
 """
 if not UW_API_TOKEN:
 log(" ERROR: UW_API_TOKEN not set!")
 log("Please set one of these environment variables:")
 log(" - UW_API_TOKEN")
 log(" - UW_KEY")
 log(" - UNUSUAL_WHALES_API_KEY")
 sys.exit(1)
 
 # Mask token for security (show first 8 chars only)
 masked_token = f"{UW_API_TOKEN[:8]}...{UW_API_TOKEN[-4:]}" if len(UW_API_TOKEN) > 12 else "***"
 log(f"🔑 Using API token: {masked_token}")
 
 # Build WebSocket URI
 uri = f"wss://api.unusualwhales.com/socket?token={UW_API_TOKEN}"
 log(f" Connecting to: wss://api.unusualwhales.com/socket")
 
 try:
 # Connect to WebSocket
 async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as ws:
 log(" WebSocket connected!")
 
 # Test 1: Subscribe to flow-alerts channel
 log("\n📡 Test 1: Subscribing to 'flow-alerts' channel...")
 subscribe_msg = {
 "channel": "flow-alerts",
 "msg_type": "join"
 }
 await ws.send(json.dumps(subscribe_msg))
 log(f" Sent: {subscribe_msg}")
 
 # Test 2: Subscribe to gex:SPY channel
 log("\n📡 Test 2: Subscribing to 'gex:SPY' channel...")
 subscribe_msg = {
 "channel": "gex:SPY",
 "msg_type": "join"
 }
 await ws.send(json.dumps(subscribe_msg))
 log(f" Sent: {subscribe_msg}")
 
 # Test 3: Receive messages for 30 seconds
 log(f"\n📨 Test 3: Listening for messages ({TIMEOUT} seconds)...")
 log(" Press Ctrl+C to stop early\n")
 
 message_count = 0
 channels_seen = set()
 start_time = datetime.now()
 
 try:
 while True:
 # Wait for message with timeout
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=TIMEOUT)
 message_count += 1
 
 # Parse message
 data = json.loads(message)
 
 # UW format: [channel, payload]
 if isinstance(data, list) and len(data) >= 2:
 channel, payload = data[0], data[1]
 channels_seen.add(channel)
 
 # Pretty print first few messages
 if message_count <= 5:
 log(f"📬 Message #{message_count}:")
 log(f" Channel: {channel}")
 log(f" Payload: {json.dumps(payload, indent=2)[:200]}...")
 log("")
 elif message_count % 10 == 0:
 # Show progress every 10 messages
 elapsed = (datetime.now() - start_time).total_seconds()
 rate = message_count / elapsed if elapsed > 0 else 0
 log(f" Progress: {message_count} messages received ({rate:.1f} msg/s)")
 else:
 log(f" Unexpected message format: {data}")
 
 except asyncio.TimeoutError:
 log(f"⏱️ No messages received for {TIMEOUT} seconds")
 break
 
 except KeyboardInterrupt:
 log("\n Interrupted by user (Ctrl+C)")
 
 # Summary
 elapsed = (datetime.now() - start_time).total_seconds()
 log("\n" + "="*60)
 log(" TEST SUMMARY:")
 log("="*60)
 log(f" Connection: SUCCESS")
 log(f"📬 Messages received: {message_count}")
 log(f"📡 Channels seen: {', '.join(channels_seen) if channels_seen else 'None'}")
 log(f"⏱️ Duration: {elapsed:.1f} seconds")
 log(f" Average rate: {message_count/elapsed:.2f} messages/second" if elapsed > 0 else "N/A")
 log("="*60)
 
 if message_count > 0:
 log("\n SUCCESS! WebSocket is working perfectly!")
 log(" Ready to implement full streaming features!")
 else:
 log("\n WARNING: No messages received")
 log("This could mean:")
 log(" - Market is closed (check trading hours)")
 log(" - No activity on subscribed channels")
 log(" - Subscription format might be incorrect")
 
 # Test 4: Graceful disconnect
 log("\n🔌 Test 4: Disconnecting gracefully...")
 await ws.close()
 log(" Disconnected cleanly")
 
 except websockets.exceptions.InvalidStatusCode as e:
 log(f"\n Connection failed with status code: {e.status_code}")
 if e.status_code == 401:
 log(" ERROR: Invalid API token (401 Unauthorized)")
 log(" Please check your UW_API_TOKEN")
 elif e.status_code == 403:
 log(" ERROR: Access forbidden (403)")
 log(" Your API plan may not have WebSocket access")
 else:
 log(f" HTTP Error: {e}")
 sys.exit(1)
 
 except websockets.exceptions.WebSocketException as e:
 log(f"\n WebSocket error: {e}")
 sys.exit(1)
 
 except Exception as e:
 log(f"\n Unexpected error: {type(e).__name__}: {e}")
 import traceback
 traceback.print_exc()
 sys.exit(1)

async def main():
 """Main entry point"""
 log("="*60)
 log("🧪 UNUSUAL WHALES WEBSOCKET TEST")
 log("="*60)
 log("")
 
 await test_websocket_connection()
 
 log("\n All tests completed!")
 log("Next step: Run full implementation with 'A' option")

if __name__ == "__main__":
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 log("\n Test interrupted by user")
 sys.exit(0)
