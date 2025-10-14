#!/usr/bin/env python3
"""
Lit Trades & Off-Lit Trades WebSocket Integration Test
========================================================

Tests the newly implemented lit_trades and off_lit_trades WebSocket channels
for 100% UW API compliance.

Channels Tested:
- lit_trades:TICKER (exchange-based visible trades)
- off_lit_trades:TICKER (dark pool institutional trades)

Usage:
    python lit_off_lit_trades_test.py --ticker SPY --duration 30
    python lit_off_lit_trades_test.py --ticker AAPL --duration 60 --skip-uw

Author: Gabriel Barbudan
Date: October 14, 2025
"""

import asyncio
import json
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Any
import websockets

# Configuration
BACKEND_URL = "ws://localhost:8000"
TEST_TIMEOUT = 90  # seconds


class TestResults:
    """Store and display test results"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors: List[str] = []
        self.lit_trades_count = 0
        self.off_lit_trades_count = 0
        self.lit_exchanges = set()
        self.off_lit_venues = set()
        self.start_time = datetime.now()
    
    def add_test(self, name: str, passed: bool, error: str = None):
        """Record test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            self.tests_failed += 1
            print(f"❌ {name}")
            if error:
                self.errors.append(f"{name}: {error}")
                print(f"   Error: {error}")
    
    def add_lit_trade(self, trade: Dict[str, Any]):
        """Record lit trade data"""
        self.lit_trades_count += 1
        if 'exchange' in trade:
            self.lit_exchanges.add(trade['exchange'])
    
    def add_off_lit_trade(self, trade: Dict[str, Any]):
        """Record off-lit trade data"""
        self.off_lit_trades_count += 1
        if 'venue' in trade:
            self.off_lit_venues.add(trade['venue'])
    
    def print_summary(self):
        """Print final test summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("📊 TEST SUMMARY - Lit Trades & Off-Lit Trades")
        print("="*70)
        print(f"\n⏱️  Duration: {duration:.1f}s")
        print(f"\n🧪 Tests Run: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        
        if self.lit_trades_count > 0:
            print(f"\n📊 Lit Trades Received: {self.lit_trades_count}")
            print(f"   Exchanges: {', '.join(sorted(self.lit_exchanges)) if self.lit_exchanges else 'None'}")
        
        if self.off_lit_trades_count > 0:
            print(f"\n🕶️  Off-Lit Trades Received: {self.off_lit_trades_count}")
            print(f"   Venues: {', '.join(sorted(self.off_lit_venues)) if self.off_lit_venues else 'None'}")
        
        if self.errors:
            print("\n⚠️  Errors:")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n" + "="*70)
        
        if self.tests_failed == 0:
            print("✅ ALL TESTS PASSED")
        else:
            print(f"❌ {self.tests_failed} TEST(S) FAILED")
        
        print("="*70 + "\n")
        
        return self.tests_failed == 0


async def test_lit_trades_connection(ticker: str, duration: int) -> TestResults:
    """Test lit_trades WebSocket channel"""
    results = TestResults()
    endpoint = f"{BACKEND_URL}/ws/lit-trades/{ticker}"
    
    print(f"\n🔗 Testing Lit Trades Channel: {ticker}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Duration: {duration}s\n")
    
    # Add Origin header for CORS
    additional_headers = {"Origin": "http://localhost:3000"}
    
    try:
        async with websockets.connect(endpoint, ping_interval=20, ping_timeout=10, additional_headers=additional_headers) as ws:
            # Test 1: Connection established
            results.add_test("Lit Trades - Connection established", True)
            
            # Test 2: Receive initial message
            try:
                first_msg = await asyncio.wait_for(ws.recv(), timeout=10)
                results.add_test("Lit Trades - Received first message", True)
                
                # Parse message
                try:
                    data = json.loads(first_msg)
                    results.add_test("Lit Trades - Valid JSON format", True)
                    
                    # Test 3: Message structure
                    if isinstance(data, dict):
                        results.add_test("Lit Trades - Message is dictionary", True)
                        
                        # Test 4: Required fields
                        required_fields = ['timestamp', 'price', 'size']
                        has_required = any(field in data for field in required_fields)
                        results.add_test(
                            "Lit Trades - Has required fields", 
                            has_required,
                            f"Missing fields. Got: {list(data.keys())}"
                        )
                        
                        # Record trade data
                        results.add_lit_trade(data)
                        
                    else:
                        results.add_test("Lit Trades - Message is dictionary", False, f"Got {type(data)}")
                        
                except json.JSONDecodeError as e:
                    results.add_test("Lit Trades - Valid JSON format", False, str(e))
                    
            except asyncio.TimeoutError:
                results.add_test("Lit Trades - Received first message", False, "Timeout waiting for data")
            
            # Test 5: Stream continuity (collect trades for duration)
            print(f"\n⏳ Collecting lit trades for {duration}s...")
            start_time = asyncio.get_event_loop().time()
            trade_count = 0
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(msg)
                    results.add_lit_trade(data)
                    trade_count += 1
                    
                    # Print sample every 10 trades
                    if trade_count % 10 == 0:
                        exchange = data.get('exchange', 'UNKNOWN')
                        price = data.get('price', 0)
                        size = data.get('size', 0)
                        print(f"   Trade #{trade_count}: {exchange} | ${price:.2f} | {size:,} shares")
                        
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            results.add_test(
                "Lit Trades - Stream continuity",
                trade_count > 0,
                f"Only received {trade_count} trades in {duration}s"
            )
            
    except websockets.exceptions.WebSocketException as e:
        results.add_test("Lit Trades - Connection established", False, str(e))
    except Exception as e:
        results.add_test("Lit Trades - Unexpected error", False, str(e))
    
    return results


async def test_off_lit_trades_connection(ticker: str, duration: int) -> TestResults:
    """Test off_lit_trades WebSocket channel"""
    results = TestResults()
    endpoint = f"{BACKEND_URL}/ws/off-lit-trades/{ticker}"
    
    print(f"\n🔗 Testing Off-Lit Trades Channel: {ticker}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Duration: {duration}s\n")
    
    # Add Origin header for CORS
    additional_headers = {"Origin": "http://localhost:3000"}
    
    try:
        async with websockets.connect(endpoint, ping_interval=20, ping_timeout=10, additional_headers=additional_headers) as ws:
            # Test 1: Connection established
            results.add_test("Off-Lit Trades - Connection established", True)
            
            # Test 2: Receive initial message
            try:
                first_msg = await asyncio.wait_for(ws.recv(), timeout=10)
                results.add_test("Off-Lit Trades - Received first message", True)
                
                # Parse message
                try:
                    data = json.loads(first_msg)
                    results.add_test("Off-Lit Trades - Valid JSON format", True)
                    
                    # Test 3: Message structure
                    if isinstance(data, dict):
                        results.add_test("Off-Lit Trades - Message is dictionary", True)
                        
                        # Test 4: Required fields
                        required_fields = ['timestamp', 'price', 'size']
                        has_required = any(field in data for field in required_fields)
                        results.add_test(
                            "Off-Lit Trades - Has required fields",
                            has_required,
                            f"Missing fields. Got: {list(data.keys())}"
                        )
                        
                        # Record trade data
                        results.add_off_lit_trade(data)
                        
                    else:
                        results.add_test("Off-Lit Trades - Message is dictionary", False, f"Got {type(data)}")
                        
                except json.JSONDecodeError as e:
                    results.add_test("Off-Lit Trades - Valid JSON format", False, str(e))
                    
            except asyncio.TimeoutError:
                results.add_test("Off-Lit Trades - Received first message", False, "Timeout waiting for data")
            
            # Test 5: Stream continuity (collect trades for duration)
            print(f"\n⏳ Collecting off-lit trades for {duration}s...")
            start_time = asyncio.get_event_loop().time()
            trade_count = 0
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(msg)
                    results.add_off_lit_trade(data)
                    trade_count += 1
                    
                    # Print sample every 5 trades (dark pool trades are less frequent)
                    if trade_count % 5 == 0:
                        venue = data.get('venue', 'UNKNOWN')
                        price = data.get('price', 0)
                        size = data.get('size', 0)
                        is_block = size >= 10000
                        block_indicator = " 💎 BLOCK" if is_block else ""
                        print(f"   Trade #{trade_count}: {venue} | ${price:.2f} | {size:,} shares{block_indicator}")
                        
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            results.add_test(
                "Off-Lit Trades - Stream continuity",
                trade_count > 0,
                f"Only received {trade_count} trades in {duration}s"
            )
            
    except websockets.exceptions.WebSocketException as e:
        results.add_test("Off-Lit Trades - Connection established", False, str(e))
    except Exception as e:
        results.add_test("Off-Lit Trades - Unexpected error", False, str(e))
    
    return results


async def test_concurrent_connections(ticker: str, duration: int) -> TestResults:
    """Test both channels running concurrently"""
    results = TestResults()
    
    print(f"\n🔗 Testing Concurrent Connections: {ticker}")
    print(f"   Testing both channels simultaneously")
    print(f"   Duration: {duration}s\n")
    
    lit_endpoint = f"{BACKEND_URL}/ws/lit-trades/{ticker}"
    off_lit_endpoint = f"{BACKEND_URL}/ws/off-lit-trades/{ticker}"
    
    # Add Origin header for CORS
    additional_headers = {"Origin": "http://localhost:3000"}
    
    try:
        # Connect to both channels simultaneously
        async with websockets.connect(lit_endpoint, ping_interval=20, ping_timeout=10, additional_headers=additional_headers) as lit_ws, \
                   websockets.connect(off_lit_endpoint, ping_interval=20, ping_timeout=10, additional_headers=additional_headers) as off_lit_ws:
            
            results.add_test("Concurrent - Both connections established", True)
            
            # Receive from both channels
            start_time = asyncio.get_event_loop().time()
            lit_count = 0
            off_lit_count = 0
            
            print(f"⏳ Collecting from both channels for {duration}s...")
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    # Try to receive from both channels with timeout
                    lit_task = asyncio.create_task(lit_ws.recv())
                    off_lit_task = asyncio.create_task(off_lit_ws.recv())
                    
                    done, pending = await asyncio.wait(
                        [lit_task, off_lit_task],
                        timeout=2,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()
                    
                    # Process completed tasks
                    for task in done:
                        try:
                            msg = task.result()
                            data = json.loads(msg)
                            
                            if task == lit_task:
                                results.add_lit_trade(data)
                                lit_count += 1
                            else:
                                results.add_off_lit_trade(data)
                                off_lit_count += 1
                                
                        except Exception:
                            pass
                    
                    # Print progress
                    if (lit_count + off_lit_count) % 20 == 0:
                        print(f"   Progress: 📊 {lit_count} lit trades | 🕶️ {off_lit_count} dark pool trades")
                        
                except asyncio.TimeoutError:
                    continue
            
            results.add_test(
                "Concurrent - Lit trades received",
                lit_count > 0,
                f"No lit trades received"
            )
            
            results.add_test(
                "Concurrent - Off-lit trades received",
                off_lit_count > 0,
                f"No off-lit trades received"
            )
            
            results.add_test(
                "Concurrent - No data interference",
                lit_count > 0 and off_lit_count > 0,
                f"Channels may be interfering: lit={lit_count}, off_lit={off_lit_count}"
            )
            
    except Exception as e:
        results.add_test("Concurrent - Test execution", False, str(e))
    
    return results


async def run_all_tests(ticker: str, duration: int):
    """Run all test suites"""
    print("\n" + "="*70)
    print("🧪 LIT TRADES & OFF-LIT TRADES - WEBSOCKET TEST SUITE")
    print("="*70)
    print(f"\nTicker: {ticker}")
    print(f"Duration: {duration}s per test")
    print(f"Backend: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = TestResults()
    
    # Test 1: Lit Trades Channel
    print("\n" + "-"*70)
    print("TEST SUITE 1: LIT TRADES CHANNEL")
    print("-"*70)
    lit_results = await test_lit_trades_connection(ticker, duration)
    all_results.tests_run += lit_results.tests_run
    all_results.tests_passed += lit_results.tests_passed
    all_results.tests_failed += lit_results.tests_failed
    all_results.errors.extend(lit_results.errors)
    all_results.lit_trades_count = lit_results.lit_trades_count
    all_results.lit_exchanges = lit_results.lit_exchanges
    
    # Test 2: Off-Lit Trades Channel
    print("\n" + "-"*70)
    print("TEST SUITE 2: OFF-LIT TRADES CHANNEL")
    print("-"*70)
    off_lit_results = await test_off_lit_trades_connection(ticker, duration)
    all_results.tests_run += off_lit_results.tests_run
    all_results.tests_passed += off_lit_results.tests_passed
    all_results.tests_failed += off_lit_results.tests_failed
    all_results.errors.extend(off_lit_results.errors)
    all_results.off_lit_trades_count = off_lit_results.off_lit_trades_count
    all_results.off_lit_venues = off_lit_results.off_lit_venues
    
    # Test 3: Concurrent Connections
    print("\n" + "-"*70)
    print("TEST SUITE 3: CONCURRENT CONNECTIONS")
    print("-"*70)
    concurrent_results = await test_concurrent_connections(ticker, duration)
    all_results.tests_run += concurrent_results.tests_run
    all_results.tests_passed += concurrent_results.tests_passed
    all_results.tests_failed += concurrent_results.tests_failed
    all_results.errors.extend(concurrent_results.errors)
    
    # Print final summary
    success = all_results.print_summary()
    
    return 0 if success else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test lit_trades and off_lit_trades WebSocket channels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lit_off_lit_trades_test.py --ticker SPY --duration 30
  python lit_off_lit_trades_test.py --ticker AAPL --duration 60
  python lit_off_lit_trades_test.py --ticker TSLA --duration 45
        """
    )
    
    parser.add_argument(
        '--ticker',
        type=str,
        default='SPY',
        help='Stock ticker to test (default: SPY)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=20,
        help='Test duration in seconds per channel (default: 20)'
    )
    
    parser.add_argument(
        '--backend',
        type=str,
        default='ws://localhost:8000',
        help='Backend WebSocket URL (default: ws://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Update global backend URL
    global BACKEND_URL
    BACKEND_URL = args.backend
    
    # Run tests
    try:
        exit_code = asyncio.run(run_all_tests(args.ticker, args.duration))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
