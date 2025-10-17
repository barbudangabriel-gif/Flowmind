#!/usr/bin/env python3
"""
UW WebSocket Channel Investigation
Test real channels to find what actually exists in UW API
"""
import asyncio
import websockets
import json
import os
from datetime import datetime

UW_TOKEN = os.getenv("UW_API_TOKEN", "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
UW_WS_URL = f"wss://api.unusualwhales.com/socket?token={UW_TOKEN}"

# Channels to test (based on documentation and speculation)
CHANNELS_TO_TEST = [
 # Confirmed working
 "flow-alerts",
 "gex:SPY",
 "option_trades:SPY",
 "price:SPY",
 
 # Speculation - lit/dark pool
 "lit_trades",
 "lit_trades:SPY",
 "off_lit_trades",
 "off_lit_trades:SPY",
 "dark_pool",
 "dark_pool:SPY",
 
 # Other possibilities
 "trades:SPY",
 "stock_trades:SPY",
 "exchange_trades:SPY",
 "tape_trades:SPY",
 "venue_trades:SPY",
 
 # News/data
 "news",
 "market-movers",
 "congress_trades",
 "insider_trades",
]

async def test_channel(ws, channel_name):
 """Test if a channel exists and responds"""
 print(f"\n{'='*60}")
 print(f"Testing: {channel_name}")
 print(f"{'='*60}")
 
 # Send join message
 join_msg = {
 "channel": channel_name,
 "msg_type": "join"
 }
 
 try:
 await ws.send(json.dumps(join_msg))
 print(f"✓ Sent join request")
 
 # Wait for response (with timeout)
 try:
 response = await asyncio.wait_for(ws.recv(), timeout=3.0)
 data = json.loads(response)
 
 if isinstance(data, list) and len(data) >= 2:
 channel, payload = data[0], data[1]
 status = payload.get("status", "unknown")
 
 if status == "ok":
 print(f" SUCCESS - Channel exists!")
 print(f" Response: {json.dumps(payload, indent=2)[:200]}...")
 return True, payload
 elif "error" in payload or status == "error":
 print(f" FAILED - Channel rejected")
 print(f" Error: {payload}")
 return False, payload
 else:
 print(f" UNKNOWN - Unexpected response")
 print(f" Data: {data}")
 return None, data
 else:
 print(f" UNKNOWN - Unexpected format: {response[:200]}")
 return None, response
 
 except asyncio.TimeoutError:
 print(f"⏱️ TIMEOUT - No response (channel may not exist or no data)")
 return False, None
 
 except Exception as e:
 print(f" ERROR - {e}")
 return False, str(e)

async def investigate():
 """Main investigation function"""
 print("="*60)
 print(" UW WebSocket Channel Investigation")
 print("="*60)
 print(f"Connecting to: {UW_WS_URL[:50]}...")
 print(f"Testing {len(CHANNELS_TO_TEST)} channels")
 print(f"Time: {datetime.now().isoformat()}")
 print()
 
 results = {
 "working": [],
 "failed": [],
 "unknown": []
 }
 
 try:
 async with websockets.connect(
 UW_WS_URL,
 ping_interval=20,
 ping_timeout=10
 ) as ws:
 print(" Connected to UW WebSocket!")
 print()
 
 for channel in CHANNELS_TO_TEST:
 success, response = await test_channel(ws, channel)
 
 if success is True:
 results["working"].append((channel, response))
 elif success is False:
 results["failed"].append((channel, response))
 else:
 results["unknown"].append((channel, response))
 
 # Small delay between tests
 await asyncio.sleep(0.5)
 
 except Exception as e:
 print(f"\n Connection failed: {e}")
 return None
 
 # Print summary
 print("\n" + "="*60)
 print(" INVESTIGATION RESULTS")
 print("="*60)
 
 print(f"\n WORKING CHANNELS ({len(results['working'])}):")
 for channel, response in results["working"]:
 print(f" - {channel}")
 
 print(f"\n FAILED CHANNELS ({len(results['failed'])}):")
 for channel, response in results["failed"]:
 print(f" - {channel}")
 
 print(f"\n UNKNOWN STATUS ({len(results['unknown'])}):")
 for channel, response in results["unknown"]:
 print(f" - {channel}")
 
 # Save detailed results
 with open("uw_channels_investigation_results.json", "w") as f:
 json.dump({
 "timestamp": datetime.now().isoformat(),
 "working": [(ch, str(resp)[:500]) for ch, resp in results["working"]],
 "failed": [(ch, str(resp)[:500]) for ch, resp in results["failed"]],
 "unknown": [(ch, str(resp)[:500]) for ch, resp in results["unknown"]]
 }, f, indent=2)
 
 print(f"\n💾 Detailed results saved to: uw_channels_investigation_results.json")
 
 return results

if __name__ == "__main__":
 print("Starting UW Channel Investigation...")
 print("This will test various channel names to find what actually works.\n")
 
 results = asyncio.run(investigate())
 
 if results:
 print("\n" + "="*60)
 print(" Investigation complete!")
 print("="*60)
 print("\nNext steps:")
 print("1. Review working channels above")
 print("2. Check uw_channels_investigation_results.json for details")
 print("3. Update backend implementation with REAL channels only")
 else:
 print("\n Investigation failed - check connection and token")
