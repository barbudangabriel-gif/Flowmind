#!/usr/bin/env python3
"""
Test Script for gex_strike_expiry:TICKER WebSocket Channel

Tests the newly implemented gex_strike_expiry channel against:
1. Backend WebSocket endpoint (/ws/gex-strike-expiry/{ticker})
2. UW API WebSocket connection (wss://api.unusualwhales.com/socket)
3. Data format validation
4. Real-time message broadcasting

Usage:
 python gex_strike_expiry_test.py [--ticker SPY] [--duration 30]
"""

import asyncio
import websockets
import json
import os
import sys
from datetime import datetime
from typing import Optional

# Configuration
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8000")
WS_URL = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")
UW_API_TOKEN = os.getenv("UW_API_TOKEN") or os.getenv("UNUSUAL_WHALES_API_KEY")

class Colors:
 GREEN = '\033[92m'
 RED = '\033[91m'
 YELLOW = '\033[93m'
 BLUE = '\033[94m'
 MAGENTA = '\033[95m'
 CYAN = '\033[96m'
 RESET = '\033[0m'
 BOLD = '\033[1m'

def log(message: str, color: str = Colors.RESET):
 timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
 print(f"{color}[{timestamp}] {message}{Colors.RESET}")

def format_gex(value: float) -> str:
 """Format GEX value with color coding"""
 abs_value = abs(value)
 if abs_value >= 1e9:
 formatted = f"${value/1e9:.2f}B"
 elif abs_value >= 1e6:
 formatted = f"${value/1e6:.2f}M"
 elif abs_value >= 1e3:
 formatted = f"${value/1e3:.2f}K"
 else:
 formatted = f"${value:.0f}"
 
 color = Colors.GREEN if value > 0 else Colors.RED if value < 0 else Colors.RESET
 return f"{color}{formatted}{Colors.RESET}"

async def test_backend_endpoint(ticker: str, duration: int = 30):
 """Test backend WebSocket endpoint"""
 log(f"\n{'='*70}", Colors.BOLD)
 log(f"TEST 1: Backend WebSocket Endpoint", Colors.CYAN + Colors.BOLD)
 log(f"{'='*70}\n", Colors.BOLD)
 
 endpoint = f"{WS_URL}/api/stream/ws/gex-strike-expiry/{ticker.upper()}"
 log(f"Connecting to: {endpoint}", Colors.BLUE)
 
 try:
 async with websockets.connect(endpoint) as ws:
 log(" WebSocket connection established", Colors.GREEN)
 log(f"Listening for {duration} seconds...\n", Colors.YELLOW)
 
 message_count = 0
 start_time = asyncio.get_event_loop().time()
 gex_by_strike_expiry = {}
 
 try:
 while asyncio.get_event_loop().time() - start_time < duration:
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=5.0)
 data = json.loads(message)
 message_count += 1
 
 # Validate message structure
 assert "channel" in data, "Missing 'channel' field"
 assert "timestamp" in data, "Missing 'timestamp' field"
 assert "ticker" in data, "Missing 'ticker' field"
 assert "data" in data, "Missing 'data' field"
 
 # Extract GEX data
 payload = data["data"]
 strike = payload.get("strike")
 expiry = payload.get("expiry")
 net_gex = payload.get("net_gex", 0)
 call_gex = payload.get("call_gex", 0)
 put_gex = payload.get("put_gex", 0)
 
 # Store for matrix display
 key = (strike, expiry)
 gex_by_strike_expiry[key] = {
 "net_gex": net_gex,
 "call_gex": call_gex,
 "put_gex": put_gex
 }
 
 # Display message
 log(f"Message #{message_count}: Strike ${strike} | Expiry {expiry}", Colors.MAGENTA)
 log(f" Net GEX: {format_gex(net_gex)} | Calls: {format_gex(call_gex)} | Puts: {format_gex(put_gex)}")
 
 except asyncio.TimeoutError:
 log("⏱️ Waiting for data...", Colors.YELLOW)
 continue
 
 except KeyboardInterrupt:
 log("\n Test interrupted by user", Colors.YELLOW)
 
 # Summary
 log(f"\n{'─'*70}", Colors.BOLD)
 log(f" SUMMARY", Colors.CYAN + Colors.BOLD)
 log(f"{'─'*70}", Colors.BOLD)
 log(f"Total messages received: {message_count}", Colors.GREEN)
 log(f"Unique strike/expiry combinations: {len(gex_by_strike_expiry)}", Colors.GREEN)
 
 if gex_by_strike_expiry:
 log(f"\n GEX Matrix Preview (Top 10):", Colors.CYAN)
 sorted_gex = sorted(
 gex_by_strike_expiry.items(), 
 key=lambda x: abs(x[1]["net_gex"]), 
 reverse=True
 )[:10]
 
 for (strike, expiry), gex_data in sorted_gex:
 log(f" ${strike} @ {expiry}: {format_gex(gex_data['net_gex'])}")
 
 log(f"\n Backend endpoint test PASSED", Colors.GREEN + Colors.BOLD)
 return True
 
 except websockets.exceptions.WebSocketException as e:
 log(f" WebSocket error: {e}", Colors.RED)
 return False
 except Exception as e:
 log(f" Unexpected error: {e}", Colors.RED)
 import traceback
 traceback.print_exc()
 return False

async def test_direct_uw_api(ticker: str, duration: int = 15):
 """Test direct connection to UW API"""
 log(f"\n{'='*70}", Colors.BOLD)
 log(f"TEST 2: Direct UW API Connection", Colors.CYAN + Colors.BOLD)
 log(f"{'='*70}\n", Colors.BOLD)
 
 if not UW_API_TOKEN:
 log(" UW_API_TOKEN not found in environment", Colors.YELLOW)
 log("Set UW_API_TOKEN or UNUSUAL_WHALES_API_KEY to test direct connection", Colors.YELLOW)
 log("Skipping direct UW API test\n", Colors.YELLOW)
 return None
 
 uri = f"wss://api.unusualwhales.com/socket?token={UW_API_TOKEN}"
 channel = f"gex_strike_expiry:{ticker.upper()}"
 
 log(f"Connecting to: wss://api.unusualwhales.com/socket", Colors.BLUE)
 log(f"Channel: {channel}", Colors.BLUE)
 
 try:
 async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as ws:
 log(" Connected to UW API", Colors.GREEN)
 
 # Subscribe to channel
 subscribe_msg = {
 "channel": channel,
 "msg_type": "join"
 }
 await ws.send(json.dumps(subscribe_msg))
 log(f" Sent join request: {channel}", Colors.BLUE)
 
 # Wait for confirmation
 response = await asyncio.wait_for(ws.recv(), timeout=10.0)
 response_data = json.loads(response)
 log(f"📥 Received: {response_data}", Colors.GREEN)
 
 if isinstance(response_data, list) and len(response_data) >= 2:
 ch, payload = response_data[0], response_data[1]
 if payload.get("status") == "ok":
 log(f" Successfully subscribed to {ch}", Colors.GREEN)
 else:
 log(f" Unexpected response: {payload}", Colors.YELLOW)
 
 # Listen for messages
 log(f"Listening for {duration} seconds...\n", Colors.YELLOW)
 message_count = 0
 start_time = asyncio.get_event_loop().time()
 
 while asyncio.get_event_loop().time() - start_time < duration:
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=5.0)
 data = json.loads(message)
 message_count += 1
 
 if isinstance(data, list) and len(data) >= 2:
 ch, payload = data[0], data[1]
 log(f"Message #{message_count}: {ch}", Colors.MAGENTA)
 log(f" Payload: {json.dumps(payload, indent=2)[:200]}...")
 
 except asyncio.TimeoutError:
 log("⏱️ Waiting for UW data...", Colors.YELLOW)
 continue
 
 log(f"\n Direct UW API test PASSED ({message_count} messages)", Colors.GREEN + Colors.BOLD)
 return True
 
 except websockets.exceptions.InvalidStatusCode as e:
 log(f" Invalid status code: {e}", Colors.RED)
 log("Check your UW_API_TOKEN is valid", Colors.YELLOW)
 return False
 except asyncio.TimeoutError:
 log(f" Timeout waiting for UW response", Colors.RED)
 return False
 except Exception as e:
 log(f" Error: {e}", Colors.RED)
 import traceback
 traceback.print_exc()
 return False

async def test_data_format_validation(ticker: str, sample_size: int = 5):
 """Validate data format matches specification"""
 log(f"\n{'='*70}", Colors.BOLD)
 log(f"TEST 3: Data Format Validation", Colors.CYAN + Colors.BOLD)
 log(f"{'='*70}\n", Colors.BOLD)
 
 endpoint = f"{WS_URL}/api/stream/ws/gex-strike-expiry/{ticker.upper()}"
 
 required_fields = {
 "root": ["channel", "timestamp", "ticker", "data"],
 "data": ["strike", "expiry", "net_gex", "call_gex", "put_gex"]
 }
 
 try:
 async with websockets.connect(endpoint) as ws:
 log(f"Connected. Collecting {sample_size} messages for validation...", Colors.BLUE)
 
 messages = []
 for i in range(sample_size):
 try:
 message = await asyncio.wait_for(ws.recv(), timeout=10.0)
 data = json.loads(message)
 messages.append(data)
 log(f" Message {i+1}/{sample_size} received", Colors.GREEN)
 except asyncio.TimeoutError:
 log(f"⏱️ Timeout on message {i+1}, continuing...", Colors.YELLOW)
 break
 
 if not messages:
 log(" No messages received for validation", Colors.RED)
 return False
 
 log(f"\n Validating {len(messages)} messages...\n", Colors.CYAN)
 
 all_valid = True
 for idx, msg in enumerate(messages, 1):
 log(f"Message {idx}:", Colors.MAGENTA)
 
 # Check root fields
 for field in required_fields["root"]:
 if field in msg:
 log(f" {field}: {str(msg[field])[:50]}", Colors.GREEN)
 else:
 log(f" MISSING: {field}", Colors.RED)
 all_valid = False
 
 # Check data fields
 if "data" in msg:
 for field in required_fields["data"]:
 if field in msg["data"]:
 value = msg["data"][field]
 log(f" data.{field}: {value}", Colors.GREEN)
 else:
 log(f" MISSING: data.{field}", Colors.RED)
 all_valid = False
 
 log("") # Blank line
 
 if all_valid:
 log(f" All messages passed validation", Colors.GREEN + Colors.BOLD)
 else:
 log(f" Some validation checks failed", Colors.RED + Colors.BOLD)
 
 return all_valid
 
 except Exception as e:
 log(f" Validation error: {e}", Colors.RED)
 return False

async def main():
 import argparse
 
 parser = argparse.ArgumentParser(description="Test gex_strike_expiry WebSocket channel")
 parser.add_argument("--ticker", default="SPY", help="Stock ticker (default: SPY)")
 parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds (default: 30)")
 parser.add_argument("--skip-backend", action="store_true", help="Skip backend endpoint test")
 parser.add_argument("--skip-uw", action="store_true", help="Skip direct UW API test")
 parser.add_argument("--skip-validation", action="store_true", help="Skip data format validation")
 
 args = parser.parse_args()
 
 log(f"\n{'='*70}", Colors.BOLD)
 log(f"🧪 GEX Strike/Expiry WebSocket Channel Test Suite", Colors.CYAN + Colors.BOLD)
 log(f"{'='*70}", Colors.BOLD)
 log(f"Ticker: {args.ticker.upper()}", Colors.BLUE)
 log(f"Duration: {args.duration}s", Colors.BLUE)
 log(f"Backend URL: {BACKEND_URL}", Colors.BLUE)
 log(f"UW API Token: {' Set' if UW_API_TOKEN else ' Not set'}", Colors.BLUE)
 
 results = {}
 
 # Test 1: Backend endpoint
 if not args.skip_backend:
 results["backend"] = await test_backend_endpoint(args.ticker, args.duration)
 
 # Test 2: Direct UW API
 if not args.skip_uw:
 results["uw_api"] = await test_direct_uw_api(args.ticker, 15)
 
 # Test 3: Data format validation
 if not args.skip_validation:
 results["validation"] = await test_data_format_validation(args.ticker, 5)
 
 # Final summary
 log(f"\n{'='*70}", Colors.BOLD)
 log(f" FINAL TEST RESULTS", Colors.CYAN + Colors.BOLD)
 log(f"{'='*70}\n", Colors.BOLD)
 
 for test_name, result in results.items():
 if result is True:
 status = f"{Colors.GREEN} PASSED{Colors.RESET}"
 elif result is False:
 status = f"{Colors.RED} FAILED{Colors.RESET}"
 else:
 status = f"{Colors.YELLOW} SKIPPED{Colors.RESET}"
 
 log(f"{test_name.upper()}: {status}")
 
 # Exit code
 if all(r in [True, None] for r in results.values()):
 log(f"\n All tests completed successfully!", Colors.GREEN + Colors.BOLD)
 sys.exit(0)
 else:
 log(f"\n Some tests failed", Colors.RED + Colors.BOLD)
 sys.exit(1)

if __name__ == "__main__":
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 log("\n Tests interrupted by user", Colors.YELLOW)
 sys.exit(130)
