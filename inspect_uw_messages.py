#!/usr/bin/env python3
"""
Raw message inspection - see what UW actually sends
"""
import asyncio
import websockets

async def inspect():
    token = '5809ee6a-bcb6-48ce-a16d-9f3bd634fd50'
    uri = f'wss://api.unusualwhales.com/socket?token={token}'
    
    print("Connecting to UW...")
    async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as ws:
        print("✅ Connected!\n")
        
        # Subscribe to lit_trades:SPY
        import json
        await ws.send(json.dumps({'channel': 'lit_trades:SPY', 'msg_type': 'join'}))
        print("📡 Subscribed to lit_trades:SPY\n")
        
        print("Raw messages (10 seconds):")
        print("="*70)
        
        for i in range(20):  # Max 20 messages
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                print(f"\nMessage {i+1}:")
                print(f"  Type: {type(msg)}")
                print(f"  Length: {len(msg)}")
                print(f"  Raw: {repr(msg[:200])}")
                
                # Try to parse
                try:
                    data = json.loads(msg)
                    print(f"  Parsed: {data}")
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON Error: {e}")
                    print(f"  Content: {msg[:500]}")
                
            except asyncio.TimeoutError:
                print(".", end="", flush=True)
        
        print("\n\nDone!")

asyncio.run(inspect())
