#!/usr/bin/env python3
"""
PROPER UW Channel Investigation - Tests REAL channels
"""
import asyncio
import websockets
import json
from datetime import datetime

TOKEN = '5809ee6a-bcb6-48ce-a16d-9f3bd634fd50'
URI = f'wss://api.unusualwhales.com/socket?token={TOKEN}'

# Channels to test
CHANNELS = [
    # Base channels (no ticker)
    'flow-alerts',
    'lit_trades',
    'off_lit_trades',
    'dark_pool',
    'news',
    'market-movers',
    
    # Ticker-specific
    'lit_trades:SPY',
    'off_lit_trades:SPY',
    'option_trades:SPY',
    'gex:SPY',
    'gex_strike_expiry:SPY',
    'price:SPY',
]

async def test_channels():
    print("="*70)
    print("🔬 REAL UW API Channel Test")
    print("="*70)
    print(f"Time: {datetime.now().isoformat()}\n")
    
    results = {'exists': [], 'unknown': [], 'has_data': []}
    
    async with websockets.connect(URI, ping_interval=20, ping_timeout=10) as ws:
        print("✅ Connected to UW WebSocket\n")
        
        for channel in CHANNELS:
            print(f"Testing: {channel:<30}", end=" ")
            
            # Send join
            await ws.send(json.dumps({'channel': channel, 'msg_type': 'join'}))
            
            # Collect all responses for 2 seconds
            responses = []
            start = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start < 2.0:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    responses.append(msg)
                except asyncio.TimeoutError:
                    break
            
            if not responses:
                print("❌ No response")
                results['unknown'].append(channel)
                continue
            
            # Check first response for "ok" status
            try:
                first = json.loads(responses[0])
                if isinstance(first, list) and len(first) >= 2:
                    ch_name, payload = first[0], first[1]
                    if payload.get('status') == 'ok':
                        print(f"✅ EXISTS", end="")
                        results['exists'].append(channel)
                        
                        # Check if we got data messages
                        if len(responses) > 1:
                            print(f" + {len(responses)-1} data messages")
                            results['has_data'].append(channel)
                        else:
                            print(" (no data yet)")
                    else:
                        print(f"⚠️  Status: {payload.get('status', 'unknown')}")
                        results['unknown'].append(channel)
                else:
                    print(f"⚠️  Unexpected format")
                    results['unknown'].append(channel)
            except json.JSONDecodeError:
                # Might be raw data
                print(f"✅ EXISTS (binary/raw data)")
                results['exists'].append(channel)
                results['has_data'].append(channel)
            except Exception as e:
                print(f"❌ Error: {e}")
                results['unknown'].append(channel)
            
            await asyncio.sleep(0.3)
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"\n✅ CONFIRMED CHANNELS ({len(results['exists'])}):")
    for ch in results['exists']:
        has_data = " [📨 HAS DATA]" if ch in results['has_data'] else ""
        print(f"   • {ch}{has_data}")
    
    print(f"\n❌ UNCONFIRMED ({len(results['unknown'])}):")
    for ch in results['unknown']:
        print(f"   • {ch}")
    
    # Save results
    with open('uw_confirmed_channels.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'confirmed': results['exists'],
            'with_data': results['has_data'],
            'unknown': results['unknown']
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: uw_confirmed_channels.json")
    
    return results

if __name__ == '__main__':
    print("Testing UW WebSocket channels...\n")
    results = asyncio.run(test_channels())
    print("\n✅ Investigation complete!")
