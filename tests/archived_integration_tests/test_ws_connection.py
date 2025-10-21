#!/usr/bin/env python3
"""
Quick WebSocket test to verify lit-trades endpoint
"""
import asyncio
import websockets
import json

async def test_ws():
 uri = "ws://localhost:8000/api/stream/ws/lit-trades/SPY"
 print(f"🔌 Connecting to: {uri}")
 
 try:
 async with websockets.connect(uri) as ws:
 print(" Connected!")
 
 # Wait for messages (5 seconds)
 for i in range(5):
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=1.0)
 data = json.loads(message)
 print(f"📨 Message {i+1}: {data.get('type', 'unknown')}")
 except asyncio.TimeoutError:
 print(f"⏱️ No message after {i+1}s")
 
 print(" Test complete!")
 
 except Exception as e:
 print(f" Error: {e}")

if __name__ == "__main__":
 asyncio.run(test_ws())
