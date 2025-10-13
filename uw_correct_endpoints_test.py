#!/usr/bin/env python3
"""
UW API Correct Endpoints Integration Test
Tests the FIXED Unusual Whales API endpoints after hallucination corrections
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from integrations.uw_client import UWClient
from unusual_whales_service import UnusualWhalesService

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with color"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {test_name}")
    if details:
        print(f"     {details}")


async def test_uw_client():
    """Test UWClient with correct endpoints"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Testing UWClient (integrations/uw_client.py){RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    client = UWClient()
    
    # Test 1: Flow Alerts
    try:
        print(f"{YELLOW}Test 1: Flow Alerts (Correct Endpoint){RESET}")
        alerts = await client.flow_alerts(ticker="TSLA", min_premium=100000, limit=5)
        
        if isinstance(alerts, list):
            print_result(
                "Flow Alerts endpoint", 
                True,
                f"Returned {len(alerts)} alerts (empty list is OK for demo mode)"
            )
        else:
            print_result("Flow Alerts endpoint", False, f"Expected list, got {type(alerts)}")
    except Exception as e:
        print_result("Flow Alerts endpoint", False, f"Error: {e}")
    
    # Test 2: Stock State (Current Price)
    try:
        print(f"\n{YELLOW}Test 2: Stock State (Current Price){RESET}")
        state = await client.stock_state("TSLA")
        
        if isinstance(state, dict):
            print_result(
                "Stock State endpoint",
                True,
                f"Returned: {state.get('ticker', 'N/A')} @ ${state.get('price', 'N/A')}"
            )
        else:
            print_result("Stock State endpoint", False, f"Expected dict, got {type(state)}")
    except Exception as e:
        print_result("Stock State endpoint", False, f"Error: {e}")
    
    # Test 3: Stock OHLC (Historical Data)
    try:
        print(f"\n{YELLOW}Test 3: Stock OHLC (Historical Data){RESET}")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        ohlc = await client.stock_ohlc("TSLA", interval="1d", start_date=start_date, end_date=end_date)
        
        if isinstance(ohlc, list):
            print_result(
                "Stock OHLC endpoint",
                True,
                f"Returned {len(ohlc)} bars (empty list is OK for demo mode)"
            )
        else:
            print_result("Stock OHLC endpoint", False, f"Expected list, got {type(ohlc)}")
    except Exception as e:
        print_result("Stock OHLC endpoint", False, f"Error: {e}")
    
    # Test 4: Spot GEX Exposures (Gamma)
    try:
        print(f"\n{YELLOW}Test 4: Spot GEX Exposures (Gamma){RESET}")
        gex = await client.spot_gex_exposures("TSLA")
        
        if isinstance(gex, dict):
            print_result(
                "Spot GEX endpoint",
                True,
                f"Returned: {gex.get('ticker', 'N/A')} GEX data"
            )
        else:
            print_result("Spot GEX endpoint", False, f"Expected dict, got {type(gex)}")
    except Exception as e:
        print_result("Spot GEX endpoint", False, f"Error: {e}")
    
    # Test 5: Market Tide (Market Overview)
    try:
        print(f"\n{YELLOW}Test 5: Market Tide (Market Overview){RESET}")
        tide = await client.market_tide()
        
        if isinstance(tide, dict):
            print_result(
                "Market Tide endpoint",
                True,
                f"Returned market overview data"
            )
        else:
            print_result("Market Tide endpoint", False, f"Expected dict, got {type(tide)}")
    except Exception as e:
        print_result("Market Tide endpoint", False, f"Error: {e}")
    
    # Test 6: Market Movers (NEW)
    try:
        print(f"\n{YELLOW}Test 6: Market Movers (NEW){RESET}")
        movers = await client.market_movers()
        
        if isinstance(movers, dict):
            has_keys = all(k in movers for k in ['gainers', 'losers', 'most_active'])
            print_result(
                "Market Movers endpoint",
                has_keys,
                f"Keys present: gainers, losers, most_active" if has_keys else f"Missing keys: {movers.keys()}"
            )
        else:
            print_result("Market Movers endpoint", False, f"Expected dict, got {type(movers)}")
    except Exception as e:
        print_result("Market Movers endpoint", False, f"Error: {e}")
    
    # Test 7: Congress Trades (NEW)
    try:
        print(f"\n{YELLOW}Test 7: Congress Trades (NEW){RESET}")
        trades = await client.congress_trades(ticker="TSLA", party="D", limit=10)
        
        if isinstance(trades, list):
            print_result(
                "Congress Trades endpoint",
                True,
                f"Returned {len(trades)} congress trades for TSLA (party=D)"
            )
        else:
            print_result("Congress Trades endpoint", False, f"Expected list, got {type(trades)}")
    except Exception as e:
        print_result("Congress Trades endpoint", False, f"Error: {e}")
    
    # Test 8: Dark Pool (NEW)
    try:
        print(f"\n{YELLOW}Test 8: Dark Pool (NEW){RESET}")
        prints = await client.dark_pool(ticker="SPY", min_volume=100000, limit=10)
        
        if isinstance(prints, list):
            print_result(
                "Dark Pool endpoint",
                True,
                f"Returned {len(prints)} dark pool prints for SPY (min_volume=100k)"
            )
        else:
            print_result("Dark Pool endpoint", False, f"Expected list, got {type(prints)}")
    except Exception as e:
        print_result("Dark Pool endpoint", False, f"Error: {e}")
    
    # Test 9: Institutional Holdings (NEW)
    try:
        print(f"\n{YELLOW}Test 9: Institutional Holdings (NEW){RESET}")
        holdings = await client.institutional_holdings(ticker="TSLA")
        
        if isinstance(holdings, dict):
            has_ticker = 'ticker' in holdings
            has_holdings = 'holdings' in holdings
            print_result(
                "Institutional Holdings endpoint",
                has_ticker and has_holdings,
                f"Keys: ticker={has_ticker}, holdings={has_holdings}"
            )
        else:
            print_result("Institutional Holdings endpoint", False, f"Expected dict, got {type(holdings)}")
    except Exception as e:
        print_result("Institutional Holdings endpoint", False, f"Error: {e}")
    
    # Test 10: Legacy methods (should warn but not crash)
    try:
        print(f"\n{YELLOW}Test 10: Legacy Methods (Deprecated){RESET}")
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        
        # These should log warnings but return data via fallback
        trades = await client.trades("TSLA", start, end)
        news = await client.news("TSLA", start, end)
        congress = await client.congress("TSLA", start, end)
        insiders = await client.insiders("TSLA", start, end)
        
        print_result(
            "Legacy methods (trades, news, congress, insiders)",
            True,
            "All deprecated methods returned without crashing (expected)"
        )
    except Exception as e:
        print_result("Legacy methods", False, f"Error: {e}")
    
    await client.aclose()


async def test_uw_service():
    """Test UnusualWhalesService with correct endpoints"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Testing UnusualWhalesService (unusual_whales_service.py){RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    service = UnusualWhalesService()
    
    # Test 1: Flow Alerts (Fixed endpoint)
    try:
        print(f"{YELLOW}Test 1: Flow Alerts (Service Layer){RESET}")
        alerts = await service.get_options_flow_alerts(minimum_premium=100000, ticker="TSLA", limit=5)
        
        if isinstance(alerts, list):
            print_result(
                "Service Flow Alerts",
                True,
                f"Returned {len(alerts)} alerts (mock data OK for demo mode)"
            )
            if alerts:
                first = alerts[0]
                print(f"     Sample: {first.get('symbol', 'N/A')} {first.get('strike_type', 'N/A')}")
        else:
            print_result("Service Flow Alerts", False, f"Expected list, got {type(alerts)}")
    except Exception as e:
        print_result("Service Flow Alerts", False, f"Error: {e}")
    
    # Test 2: Stock State
    try:
        print(f"\n{YELLOW}Test 2: Stock State (Service Layer){RESET}")
        state = await service.get_stock_state("TSLA")
        
        if isinstance(state, dict):
            print_result(
                "Service Stock State",
                True,
                f"Returned: {state.get('ticker', 'N/A')} @ ${state.get('price', 'N/A')}"
            )
        else:
            print_result("Service Stock State", False, f"Expected dict, got {type(state)}")
    except Exception as e:
        print_result("Service Stock State", False, f"Error: {e}")
    
    # Test 3: Stock OHLC
    try:
        print(f"\n{YELLOW}Test 3: Stock OHLC (Service Layer){RESET}")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        ohlc = await service.get_stock_ohlc("TSLA", interval="1d", start_date=start_date, end_date=end_date)
        
        if isinstance(ohlc, list):
            print_result(
                "Service Stock OHLC",
                True,
                f"Returned {len(ohlc)} bars"
            )
        else:
            print_result("Service Stock OHLC", False, f"Expected list, got {type(ohlc)}")
    except Exception as e:
        print_result("Service Stock OHLC", False, f"Error: {e}")
    
    # Test 4: Gamma Exposure
    try:
        print(f"\n{YELLOW}Test 4: Gamma Exposure (Service Layer){RESET}")
        gex = await service.get_gamma_exposure("TSLA")
        
        if isinstance(gex, dict):
            print_result(
                "Service Gamma Exposure",
                True,
                f"Returned GEX data for {gex.get('ticker', 'N/A')}"
            )
        else:
            print_result("Service Gamma Exposure", False, f"Expected dict, got {type(gex)}")
    except Exception as e:
        print_result("Service Gamma Exposure", False, f"Error: {e}")
    
    # Test 5: Market Tide
    try:
        print(f"\n{YELLOW}Test 5: Market Tide (Service Layer){RESET}")
        tide = await service.get_market_tide()
        
        if isinstance(tide, dict):
            print_result(
                "Service Market Tide",
                True,
                f"Returned market overview data"
            )
        else:
            print_result("Service Market Tide", False, f"Expected dict, got {type(tide)}")
    except Exception as e:
        print_result("Service Market Tide", False, f"Error: {e}")
    
    # Test 6: Market Movers (NEW)
    try:
        print(f"\n{YELLOW}Test 6: Market Movers (Service Layer - NEW){RESET}")
        movers = await service.get_market_movers()
        
        if isinstance(movers, dict):
            has_keys = all(k in movers for k in ['gainers', 'losers', 'most_active'])
            print_result(
                "Service Market Movers",
                has_keys,
                f"Returned market movers data (mock: {len(movers.get('gainers', []))} gainers)"
            )
        else:
            print_result("Service Market Movers", False, f"Expected dict, got {type(movers)}")
    except Exception as e:
        print_result("Service Market Movers", False, f"Error: {e}")
    
    # Test 7: Congress Trades (NEW)
    try:
        print(f"\n{YELLOW}Test 7: Congress Trades (Service Layer - NEW){RESET}")
        trades = await service.get_congress_trades(ticker="TSLA", party="D", limit=10)
        
        if isinstance(trades, list):
            print_result(
                "Service Congress Trades",
                True,
                f"Returned {len(trades)} congress trades (mock: {trades[0].get('politician_name', 'N/A') if trades else 'empty'})"
            )
        else:
            print_result("Service Congress Trades", False, f"Expected list, got {type(trades)}")
    except Exception as e:
        print_result("Service Congress Trades", False, f"Error: {e}")
    
    # Test 8: Dark Pool (NEW)
    try:
        print(f"\n{YELLOW}Test 8: Dark Pool (Service Layer - NEW){RESET}")
        prints = await service.get_dark_pool(ticker="SPY", min_volume=100000, limit=10)
        
        if isinstance(prints, list):
            print_result(
                "Service Dark Pool",
                True,
                f"Returned {len(prints)} dark pool prints (mock: ${prints[0].get('notional', 0)/1e6:.1f}M notional if prints else 'empty')"
            )
        else:
            print_result("Service Dark Pool", False, f"Expected list, got {type(prints)}")
    except Exception as e:
        print_result("Service Dark Pool", False, f"Error: {e}")
    
    # Test 9: Institutional Holdings (NEW)
    try:
        print(f"\n{YELLOW}Test 9: Institutional Holdings (Service Layer - NEW){RESET}")
        holdings = await service.get_institutional_holdings(ticker="TSLA")
        
        if isinstance(holdings, dict):
            has_holdings = 'holdings' in holdings
            count = len(holdings.get('holdings', []))
            print_result(
                "Service Institutional Holdings",
                has_holdings,
                f"Returned institutional data (mock: {count} holders, top: {holdings.get('top_holder', 'N/A')})"
            )
        else:
            print_result("Service Institutional Holdings", False, f"Expected dict, got {type(holdings)}")
    except Exception as e:
        print_result("Service Institutional Holdings", False, f"Error: {e}")


async def main():
    """Run all tests"""
    print(f"\n{GREEN}{'='*80}{RESET}")
    print(f"{GREEN}UW API CORRECT ENDPOINTS INTEGRATION TEST{RESET}")
    print(f"{GREEN}Fixed: Replaced hallucinated endpoints with real UW API routes{RESET}")
    print(f"{GREEN}{'='*80}{RESET}")
    
    # Check API key
    uw_key = os.getenv("UW_API_TOKEN") or os.getenv("UNUSUAL_WHALES_API_KEY") or os.getenv("UW_KEY")
    
    if not uw_key:
        print(f"\n{YELLOW}⚠️  WARNING: No UW API key found in environment{RESET}")
        print(f"{YELLOW}   Tests will run in DEMO MODE (fallback data){RESET}")
        print(f"{YELLOW}   Set UW_API_TOKEN or UW_KEY to test with real API{RESET}\n")
    else:
        print(f"\n{GREEN}✓ UW API key found: {uw_key[:8]}...{RESET}\n")
    
    # Run tests
    await test_uw_client()
    await test_uw_service()
    
    print(f"\n{GREEN}{'='*80}{RESET}")
    print(f"{GREEN}TESTS COMPLETED{RESET}")
    print(f"{GREEN}{'='*80}{RESET}\n")
    
    print(f"{BLUE}Next Steps:{RESET}")
    print(f"  1. Review UW_API_CORRECT_ENDPOINTS.md for full documentation")
    print(f"  2. Set UW_API_TOKEN env var to test with real API")
    print(f"  3. Update frontend API client if needed")
    print(f"  4. Run full backend test: python backend_test.py")
    print(f"  5. Deploy to staging and verify\n")


if __name__ == "__main__":
    asyncio.run(main())
