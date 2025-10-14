#!/usr/bin/env python3
"""
END-TO-END Test: UW → Backend Handler → Frontend WebSocket
Debug de ce nu ajung datele la frontend
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from integrations.uw_websocket_client import UWWebSocketClient
from datetime import datetime

messages_received = []

async def test_full_flow():
    print("="*70)
    print("🔬 END-TO-END DATA FLOW TEST")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S EST')}\n")
    
    token = '5809ee6a-bcb6-48ce-a16d-9f3bd634fd50'
    client = UWWebSocketClient(token)
    
    print("Step 1: Connect to UW WebSocket...")
    success = await client.connect()
    if not success:
        print("❌ Connection failed!")
        return
    print("✅ Connected!\n")
    
    print("Step 2: Define message handler...")
    async def lit_trades_handler(channel, payload):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        messages_received.append((timestamp, channel, payload))
        print(f"📨 [{timestamp}] {channel}: {str(payload)[:150]}")
    
    print("Step 3: Subscribe to lit_trades:SPY...")
    await client.subscribe('lit_trades:SPY', lit_trades_handler)
    print("✅ Subscribed!\n")
    
    print("Step 4: Start listening...")
    listen_task = asyncio.create_task(client.listen())
    print("✅ Listen task started\n")
    
    print(f"⏳ Waiting for messages (30 seconds)...")
    print(f"   Market: US market is OPEN (12:50 EST)")
    print(f"   Expected: Real-time SPY trades")
    print("-"*70)
    
    # Wait 30 seconds
    await asyncio.sleep(30)
    
    # Stop
    print("\n" + "-"*70)
    client.running = False
    
    # Results
    print(f"\n📊 RESULTS:")
    print(f"   Messages received: {len(messages_received)}")
    
    if messages_received:
        print(f"\n✅ SUCCESS - Data is flowing from UW!")
        print(f"\nFirst 3 messages:")
        for i, (ts, ch, payload) in enumerate(messages_received[:3], 1):
            print(f"   {i}. [{ts}] {ch}")
            print(f"      {str(payload)[:200]}")
    else:
        print(f"\n❌ NO DATA RECEIVED")
        print(f"\n🔍 Possible causes:")
        print(f"   1. Channel exists but no active trades for SPY")
        print(f"   2. UW API rate limiting or throttling")
        print(f"   3. Handler not being called")
        print(f"   4. Message format changed")
        
        print(f"\n💡 Let's try flow-alerts (always active)...")
        
        # Try flow-alerts
        flow_msgs = []
        async def flow_handler(ch, p):
            flow_msgs.append(p)
            print(f"📨 FLOW: {str(p)[:100]}")
        
        await client.subscribe('flow-alerts', flow_handler)
        print("Listening to flow-alerts for 15 seconds...")
        await asyncio.sleep(15)
        
        if flow_msgs:
            print(f"✅ flow-alerts working! Received {len(flow_msgs)} messages")
            print(f"   → lit_trades:SPY might just be quiet right now")
        else:
            print(f"❌ No flow-alerts either - handler issue or API problem")
    
    await client.disconnect()
    print(f"\n✅ Test complete!")

if __name__ == '__main__':
    print("Testing if UW data reaches our handlers...\n")
    asyncio.run(test_full_flow())
