#!/usr/bin/env python3
"""Simple WebSocket test for Unusual Whales"""

import asyncio
import websockets
import json
import os
from datetime import datetime

UW_API_TOKEN = os.getenv("UW_API_TOKEN", "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")

async def test_connection():
    print("=" * 70)
    print("🧪 Testing Unusual Whales WebSocket Connection")
    print("=" * 70)
    print(f"🔑 Token: {UW_API_TOKEN[:15]}...")
    
    uri = f"wss://api.unusualwhales.com/socket?token={UW_API_TOKEN}"
    
    try:
        print("\n📡 Connecting to Unusual Whales WebSocket...")
        async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as ws:
            print("✅ Connected successfully!")
            
            # Subscribe to flow-alerts
            print("\n📨 Subscribing to 'flow-alerts' channel...")
            await ws.send(json.dumps({"channel": "flow-alerts", "msg_type": "join"}))
            print("✅ Subscription sent")
            
            # Listen for 15 seconds
            print("\n👂 Listening for messages (15 seconds)...")
            print("   Press Ctrl+C to stop\n")
            
            message_count = 0
            try:
                while True:
                    message = await asyncio.wait_for(ws.recv(), timeout=15)
                    message_count += 1
                    data = json.loads(message)
                    
                    if isinstance(data, list) and len(data) >= 2:
                        channel, payload = data[0], data[1]
                        print(f"📬 Message #{message_count} on {channel}")
                        print(f"   {json.dumps(payload)[:150]}...")
                    
                    if message_count >= 10:
                        break
                        
            except asyncio.TimeoutError:
                print("\n⏱️  15 seconds elapsed")
            
            print(f"\n📊 Total messages received: {message_count}")
            print("\n✅ WebSocket test complete!")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ Connection failed with status {e.status_code}")
        if e.status_code == 401:
            print("   → Invalid API token")
        elif e.status_code == 403:
            print("   → WebSocket not available on your plan")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
