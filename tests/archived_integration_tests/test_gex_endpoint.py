#!/usr/bin/env python3
"""
Test WebSocket Endpoint: gex:SPY
Verify that new gamma exposure endpoint works correctly
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_gex_endpoint():
 """Test /api/stream/ws/gex/SPY endpoint"""
 
 print("=" * 80)
 print("🧪 TESTING NEW GEX ENDPOINT")
 print("=" * 80)
 print(f"Timestamp: {datetime.now().isoformat()}")
 print(f"Endpoint: ws://localhost:8000/api/stream/ws/gex/SPY")
 print("=" * 80)
 print()
 
 uri = "ws://localhost:8000/api/stream/ws/gex/SPY"
 
 try:
 async with websockets.connect(uri, timeout=10) as ws:
 print(" Connected to gex/SPY endpoint")
 print("⏳ Waiting for messages (10 seconds)...")
 print()
 
 message_count = 0
 start_time = asyncio.get_event_loop().time()
 
 while (asyncio.get_event_loop().time() - start_time) < 10:
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=2.0)
 message_count += 1
 
 # Parse message
 try:
 data = json.loads(message)
 print(f"📨 Message {message_count}:")
 print(f" Channel: {data.get('channel', 'N/A')}")
 print(f" Timestamp: {data.get('timestamp', 'N/A')}")
 
 if 'data' in data:
 payload = data['data']
 print(f" Data keys: {list(payload.keys())}")
 if isinstance(payload, str):
 print(f" Payload: {payload}")
 else:
 print(f" Raw: {message[:200]}")
 print()
 
 except json.JSONDecodeError:
 print(f"📨 Raw message {message_count}: {message[:100]}")
 print()
 
 except asyncio.TimeoutError:
 print(".", end="", flush=True)
 continue
 except websockets.exceptions.ConnectionClosed:
 print("\n Connection closed by server")
 break
 
 print()
 print("=" * 80)
 print(f" Test complete: Received {message_count} messages in 10 seconds")
 print("=" * 80)
 
 except Exception as e:
 print(f" Error: {e}")

async def test_all_endpoints():
 """Test all WebSocket endpoints"""
 
 endpoints = [
 ("flow-alerts", "ws://localhost:8000/api/stream/ws/flow"),
 ("gex:SPY", "ws://localhost:8000/api/stream/ws/gex/SPY"),
 ("gex:TSLA", "ws://localhost:8000/api/stream/ws/gex/TSLA"),
 ]
 
 print("\n")
 print("=" * 80)
 print("🧪 TESTING ALL VERIFIED ENDPOINTS")
 print("=" * 80)
 print()
 
 results = {}
 
 for name, uri in endpoints:
 print(f"Testing: {name}...", end=" ", flush=True)
 
 try:
 async with websockets.connect(uri, timeout=5) as ws:
 # Wait for first message (or timeout)
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=3.0)
 print(f" CONNECTED")
 results[name] = {"status": "success", "message": message[:100]}
 except asyncio.TimeoutError:
 print(f"⏱️ CONNECTED (no data yet)")
 results[name] = {"status": "timeout", "message": "No data within 3s"}
 except Exception as e:
 print(f" ERROR: {str(e)[:50]}")
 results[name] = {"status": "error", "message": str(e)}
 
 await asyncio.sleep(0.5)
 
 print()
 print("=" * 80)
 print(" RESULTS SUMMARY")
 print("=" * 80)
 for name, result in results.items():
 status_emoji = {
 "success": "",
 "timeout": "⏱️ ",
 "error": ""
 }.get(result["status"], "❓")
 
 print(f"{status_emoji} {name:<20} {result['status'].upper()}")
 
 print()

if __name__ == "__main__":
 print("\n Starting WebSocket endpoint tests...\n")
 
 # Test specific endpoint
 asyncio.run(test_gex_endpoint())
 
 # Test all endpoints
 asyncio.run(test_all_endpoints())
 
 print("\n All tests complete!")
