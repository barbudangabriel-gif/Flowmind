#!/usr/bin/env python3
"""
 Test All Unusual Whales WebSocket Channels
Verifică ce canale WebSocket sunt disponibile pentru UW Pro tier
"""
import asyncio
import websockets
import json
import os
from datetime import datetime
from typing import List, Dict

# UW API Token
UW_API_TOKEN = os.getenv("UW_API_TOKEN", "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
WS_URL = f"wss://api.unusualwhales.com/socket?token={UW_API_TOKEN}"

# Lista de canale de testat
CHANNELS_TO_TEST = [
 # Canale confirmate din docs:
 "flow-alerts",
 "gex:SPY",
 "option_trades:SPY",
 
 # Canale presupuse (plural/singular variations):
 "market-movers",
 "market-mover",
 "market_movers",
 "marketMovers",
 
 "dark-pool",
 "dark_pool",
 "darkPool",
 
 "congress",
 "congress-trades",
 "congress_trades",
 "congressTrades",
 
 # Alte tickere pentru pattern-urile confirmate:
 "gex:TSLA",
 "gex:AAPL",
 "gex:NVDA",
 "option_trades:TSLA",
 "option_trades:AAPL",
 
 # Canale posibile suplimentare (educated guesses):
 "stock-quotes:SPY",
 "stock_quotes:SPY",
 "market-tide",
 "market_tide",
 "institutional-flows",
 "institutional_flows",
 "earnings",
 "earnings-calendar",
 "news:SPY",
 "options-flow",
 "options_flow",
]

async def test_single_channel(channel: str, timeout: float = 5.0) -> Dict:
 """
 Testează un singur canal WebSocket
 
 Returns:
 dict: {
 "channel": str,
 "status": "success" | "timeout" | "error",
 "response": str | None,
 "error": str | None
 }
 """
 result = {
 "channel": channel,
 "status": "unknown",
 "response": None,
 "error": None
 }
 
 try:
 async with websockets.connect(WS_URL, timeout=10) as ws:
 # Subscribe to channel
 subscribe_msg = {
 "channel": channel,
 "msg_type": "join"
 }
 await ws.send(json.dumps(subscribe_msg))
 
 # Wait for response
 try:
 response = await asyncio.wait_for(ws.recv(), timeout=timeout)
 result["status"] = "success"
 result["response"] = response
 
 # Parse response to check if it's an error
 try:
 parsed = json.loads(response)
 if isinstance(parsed, list) and len(parsed) >= 2:
 response_channel = parsed[0]
 payload = parsed[1]
 
 # Check for error messages
 if payload == "ok":
 result["status"] = "success"
 elif isinstance(payload, dict) and "error" in payload:
 result["status"] = "error"
 result["error"] = payload.get("error")
 except:
 pass # Not JSON or different format
 
 except asyncio.TimeoutError:
 result["status"] = "timeout"
 result["error"] = f"No response within {timeout}s"
 
 except Exception as e:
 result["status"] = "error"
 result["error"] = str(e)
 
 return result

async def test_all_channels():
 """
 Testează toate canalele din listă
 """
 print("=" * 80)
 print("🐋 UNUSUAL WHALES WEBSOCKET CHANNEL DISCOVERY")
 print("=" * 80)
 print(f"Testing {len(CHANNELS_TO_TEST)} channels...")
 print(f"WebSocket URL: {WS_URL[:50]}...")
 print(f"Timestamp: {datetime.now().isoformat()}")
 print("=" * 80)
 print()
 
 results = {
 "success": [],
 "timeout": [],
 "error": []
 }
 
 for i, channel in enumerate(CHANNELS_TO_TEST, 1):
 print(f"[{i}/{len(CHANNELS_TO_TEST)}] Testing: {channel:<30}", end=" ", flush=True)
 
 result = await test_single_channel(channel)
 status = result["status"]
 
 if status == "success":
 print(" SUCCESS")
 results["success"].append(result)
 elif status == "timeout":
 print("⏱️ TIMEOUT")
 results["timeout"].append(result)
 else:
 print(f" ERROR: {result['error'][:40]}")
 results["error"].append(result)
 
 # Small delay between tests
 await asyncio.sleep(0.5)
 
 # Print summary
 print()
 print("=" * 80)
 print(" SUMMARY")
 print("=" * 80)
 
 print(f"\n SUCCESSFUL CHANNELS ({len(results['success'])}):")
 print("-" * 80)
 for r in results["success"]:
 response_preview = str(r["response"])[:60] if r["response"] else "N/A"
 print(f" • {r['channel']:<30} → {response_preview}")
 
 print(f"\n⏱️ TIMEOUT CHANNELS ({len(results['timeout'])}):")
 print("-" * 80)
 for r in results["timeout"]:
 print(f" • {r['channel']:<30} → No response within 5s")
 
 print(f"\n ERROR CHANNELS ({len(results['error'])}):")
 print("-" * 80)
 for r in results["error"]:
 error_msg = r["error"][:60] if r["error"] else "Unknown error"
 print(f" • {r['channel']:<30} → {error_msg}")
 
 print()
 print("=" * 80)
 print(" RECOMMENDATIONS:")
 print("=" * 80)
 
 if results["success"]:
 print("\n1️⃣ Use these channels in production (confirmed working):")
 for r in results["success"]:
 print(f" - {r['channel']}")
 
 if results["timeout"]:
 print("\n2️⃣ These channels might exist but need longer timeout or specific conditions:")
 for r in results["timeout"]:
 print(f" - {r['channel']}")
 
 if results["error"]:
 print("\n3️⃣ These channels likely don't exist or have different names:")
 error_channels = [r['channel'] for r in results['error']]
 print(f" - {', '.join(error_channels[:5])}")
 if len(error_channels) > 5:
 print(f" ... and {len(error_channels) - 5} more")
 
 print()
 print("=" * 80)
 print(" NEXT STEPS:")
 print("=" * 80)
 print("1. Update backend/routers/stream.py with confirmed channels")
 print("2. Remove endpoints for non-existent channels")
 print("3. Add new endpoints for discovered channels")
 print("4. Update frontend components accordingly")
 print("5. Update documentation (WEBSOCKET_IMPLEMENTATION_COMPLETE.md)")
 print()
 
 # Save results to JSON
 output_file = "uw_channels_test_results.json"
 with open(output_file, "w") as f:
 json.dump({
 "timestamp": datetime.now().isoformat(),
 "total_tested": len(CHANNELS_TO_TEST),
 "results": results
 }, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")
 print()

async def test_with_messages(channel: str, duration: int = 10):
 """
 Testează un canal și așteaptă mesaje reale (nu doar "ok")
 Util pentru canalele confirmate
 """
 print(f"\n Testing {channel} for {duration}s (waiting for real messages)...")
 print("-" * 80)
 
 try:
 async with websockets.connect(WS_URL, timeout=10) as ws:
 # Subscribe
 await ws.send(json.dumps({
 "channel": channel,
 "msg_type": "join"
 }))
 
 message_count = 0
 start_time = asyncio.get_event_loop().time()
 
 while (asyncio.get_event_loop().time() - start_time) < duration:
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=2.0)
 message_count += 1
 
 # Parse and display
 try:
 parsed = json.loads(message)
 if isinstance(parsed, list) and len(parsed) >= 2:
 msg_channel, payload = parsed[0], parsed[1]
 
 if payload != "ok":
 print(f"📨 Message {message_count}:")
 print(f" Channel: {msg_channel}")
 print(f" Payload: {json.dumps(payload, indent=2)[:200]}")
 print()
 except:
 print(f"📨 Raw message {message_count}: {message[:100]}")
 
 except asyncio.TimeoutError:
 print(".", end="", flush=True)
 continue
 
 print()
 print(f" Received {message_count} messages in {duration}s")
 
 except Exception as e:
 print(f" Error: {e}")

if __name__ == "__main__":
 print("\n Starting WebSocket channel discovery...\n")
 
 # Run main test
 asyncio.run(test_all_channels())
 
 # Optional: Test confirmed channels for real messages
 print("\n" + "=" * 80)
 print(" EXTENDED TEST: Waiting for real messages on confirmed channels")
 print("=" * 80)
 
 confirmed_channels = ["flow-alerts", "gex:SPY"]
 for channel in confirmed_channels:
 asyncio.run(test_with_messages(channel, duration=10))
 
 print("\n All tests complete!")
