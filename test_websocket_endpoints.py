#!/usr/bin/env python3
"""
Test WebSocket streaming endpoints.
Quick verification that all endpoints are accessible.
"""

import asyncio
import websockets
import httpx
import json
import os

BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_http_endpoints():
 """Test HTTP status endpoints"""
 print("=" * 60)
 print("🧪 Testing HTTP Endpoints")
 print("=" * 60)
 
 async with httpx.AsyncClient() as client:
 # Test 1: Status endpoint
 print("\n📡 Test 1: GET /api/stream/status")
 try:
 r = await client.get(f"{BACKEND_URL}/api/stream/status")
 print(f" Status: {r.status_code}")
 print(f" Response: {json.dumps(r.json(), indent=2)}")
 except Exception as e:
 print(f" Error: {e}")
 
 # Test 2: Channels endpoint
 print("\n📡 Test 2: GET /api/stream/channels")
 try:
 r = await client.get(f"{BACKEND_URL}/api/stream/channels")
 print(f" Status: {r.status_code}")
 data = r.json()
 print(f" Channels: {len(data.get('channels', []))}")
 for ch in data.get('channels', []):
 print(f" - {ch['name']}: {ch['endpoint']}")
 except Exception as e:
 print(f" Error: {e}")
 
 # Test 3: Health endpoint
 print("\n📡 Test 3: GET /api/stream/health")
 try:
 r = await client.get(f"{BACKEND_URL}/api/stream/health")
 print(f" Status: {r.status_code}")
 print(f" Response: {json.dumps(r.json(), indent=2)}")
 except Exception as e:
 print(f" Error: {e}")

async def test_websocket_connection():
 """Test WebSocket connection"""
 print("\n" + "=" * 60)
 print("🧪 Testing WebSocket Connection")
 print("=" * 60)
 
 print("\n🔌 Test 4: WebSocket /api/stream/ws/flow")
 try:
 uri = f"{WS_URL}/api/stream/ws/flow"
 print(f" Connecting to: {uri}")
 
 async with websockets.connect(uri) as ws:
 print(" Connected!")
 
 # Listen for messages for 5 seconds
 print(" 📨 Listening for messages (5 seconds)...")
 message_count = 0
 
 try:
 for _ in range(5):
 message = await asyncio.wait_for(ws.recv(), timeout=1.0)
 message_count += 1
 data = json.loads(message)
 print(f" 📬 Message #{message_count}: {data.get('channel', 'unknown')}")
 except asyncio.TimeoutError:
 print(f" ⏱️ Timeout after {message_count} messages")
 
 print(f" Total messages: {message_count}")
 
 except websockets.exceptions.InvalidStatusCode as e:
 print(f" Connection rejected: HTTP {e.status_code}")
 except Exception as e:
 print(f" Error: {type(e).__name__}: {e}")

async def main():
 print("=" * 60)
 print(" FlowMind WebSocket Streaming Tests")
 print("=" * 60)
 print(f"\nBackend URL: {BACKEND_URL}")
 print(f"WebSocket URL: {WS_URL}")
 print("")
 
 # Test HTTP endpoints first
 await test_http_endpoints()
 
 # Then test WebSocket
 await test_websocket_connection()
 
 print("\n" + "=" * 60)
 print(" Tests completed!")
 print("=" * 60)

if __name__ == "__main__":
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 print("\n Tests interrupted")
