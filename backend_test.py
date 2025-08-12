import requests
import sys
from datetime import datetime, timedelta
import json

class StockMarketAPITester:
    def __init__(self, base_url="https://market-insight-25.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_market_overview(self):
        """Test market overview endpoint"""
        return self.run_test("Market Overview", "GET", "market/overview", 200)

    def test_top_movers(self):
        """Test top movers endpoint"""
        return self.run_test("Top Movers", "GET", "market/top-movers", 200)

    def test_stock_data(self, symbol="AAPL"):
        """Test stock data endpoint - CRITICAL: Check for real prices"""
        success, stock_data = self.run_test(f"Stock Data ({symbol})", "GET", f"stocks/{symbol}", 200)
        if success and symbol == "AAPL":
            price = stock_data.get('price', 0)
            print(f"   💰 {symbol} Price: ${price:.2f} (Expected ~$227, NOT $0.00)")
            if price == 0.0:
                print(f"   ❌ CRITICAL: {symbol} showing $0.00 price!")
            elif price > 200:
                print(f"   ✅ GOOD: {symbol} showing real price")
        return success

    def test_stock_history(self, symbol="AAPL"):
        """Test stock history endpoint"""
        return self.run_test(f"Stock History ({symbol})", "GET", f"stocks/{symbol}/history", 200, params={"period": "1mo"})

    def test_technical_indicators(self, symbol="AAPL"):
        """Test technical indicators endpoint"""
        return self.run_test(f"Technical Indicators ({symbol})", "GET", f"stocks/{symbol}/indicators", 200)

    def test_stock_search(self, query="AAPL"):
        """Test stock search endpoint"""
        return self.run_test(f"Stock Search ({query})", "GET", f"stocks/search/{query}", 200)

    def test_portfolio_operations(self):
        """Test portfolio CRUD operations"""
        # Test getting empty portfolio
        success, portfolio_data = self.run_test("Get Portfolio (Empty)", "GET", "portfolio", 200)
        
        # Test adding portfolio item
        portfolio_item = {
            "symbol": "AAPL",
            "shares": 10.0,
            "purchase_price": 150.0,
            "purchase_date": (datetime.now() - timedelta(days=30)).isoformat()
        }
        
        success, add_response = self.run_test("Add Portfolio Item", "POST", "portfolio", 200, data=portfolio_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting portfolio with item
            self.run_test("Get Portfolio (With Items)", "GET", "portfolio", 200)
            
            # Test deleting portfolio item
            self.run_test("Delete Portfolio Item", "DELETE", f"portfolio/{item_id}", 200)
        
        return success

    def test_watchlist_operations(self):
        """Test watchlist CRUD operations"""
        # Test getting empty watchlist
        self.run_test("Get Watchlist (Empty)", "GET", "watchlist", 200)
        
        # Test adding watchlist item
        watchlist_item = {
            "symbol": "GOOGL",
            "target_price": 2800.0,
            "notes": "Test watchlist item"
        }
        
        success, add_response = self.run_test("Add Watchlist Item", "POST", "watchlist", 200, data=watchlist_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting watchlist with item
            self.run_test("Get Watchlist (With Items)", "GET", "watchlist", 200)
            
            # Test deleting watchlist item
            self.run_test("Delete Watchlist Item", "DELETE", f"watchlist/{item_id}", 200)
        
        return success

    def test_ticker_endpoints(self):
        """Test new ticker endpoints for S&P 500 and NASDAQ"""
        # Test S&P 500 tickers
        success, sp500_data = self.run_test("S&P 500 Tickers", "GET", "tickers/sp500", 200)
        if success and 'tickers' in sp500_data:
            print(f"   Found {len(sp500_data['tickers'])} S&P 500 tickers")
        
        # Test NASDAQ tickers
        success, nasdaq_data = self.run_test("NASDAQ Tickers", "GET", "tickers/nasdaq", 200)
        if success and 'tickers' in nasdaq_data:
            print(f"   Found {len(nasdaq_data['tickers'])} NASDAQ tickers")
        
        # Test all tickers
        success, all_data = self.run_test("All Tickers", "GET", "tickers/all", 200)
        if success and 'tickers' in all_data:
            print(f"   Found {len(all_data['tickers'])} total tickers")
        
        return success

    def test_screener_endpoints(self):
        """Test advanced screener endpoints - CRITICAL: Check for real prices (not $0.00)"""
        # Test basic screener data
        success, screener_data = self.run_test("Screener Data (All)", "GET", "screener/data", 200, params={"limit": 20, "exchange": "all"})
        if success and 'stocks' in screener_data:
            print(f"   Found {len(screener_data['stocks'])} stocks in screener")
            
            # CRITICAL CHECK: Verify real prices (not $0.00)
            zero_price_count = 0
            real_price_count = 0
            for stock in screener_data['stocks']:
                if stock.get('price', 0) == 0.0:
                    zero_price_count += 1
                else:
                    real_price_count += 1
                    if stock['symbol'] == 'AAPL':
                        print(f"   ✅ AAPL Price: ${stock['price']:.2f} (Expected ~$227)")
                    elif stock['symbol'] == 'ABT':
                        print(f"   ✅ ABT Price: ${stock['price']:.2f} (Expected ~$131)")
            
            print(f"   📊 Price Analysis: {real_price_count} real prices, {zero_price_count} zero prices")
            if zero_price_count > real_price_count:
                print(f"   ⚠️  WARNING: More zero prices than real prices!")
        
        # Test S&P 500 screener data
        success, sp500_screener = self.run_test("Screener Data (S&P 500)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "sp500"})
        if success and 'stocks' in sp500_screener:
            print(f"   Found {len(sp500_screener['stocks'])} S&P 500 stocks")
        
        # Test NASDAQ screener data
        success, nasdaq_screener = self.run_test("Screener Data (NASDAQ)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "nasdaq"})
        if success and 'stocks' in nasdaq_screener:
            print(f"   Found {len(nasdaq_screener['stocks'])} NASDAQ stocks")
        
        # Test screener sectors
        self.run_test("Available Sectors", "GET", "screener/sectors", 200)
        
        # Test advanced filtering
        filter_criteria = {
            "min_price": 50.0,
            "max_price": 500.0,
            "min_market_cap": 1000.0,  # 1B market cap
            "sector": "Technology"
        }
        
        success, filtered_data = self.run_test("Advanced Filter (Tech Stocks)", "POST", "screener/filter", 200, data=filter_criteria)
        if success and 'stocks' in filtered_data:
            print(f"   Found {len(filtered_data['stocks'])} filtered stocks")
        
        # Test filter with P/E ratio
        pe_filter = {
            "min_pe": 10.0,
            "max_pe": 30.0,
            "min_volume": 1000000
        }
        
        success, pe_filtered = self.run_test("P/E Ratio Filter", "POST", "screener/filter", 200, data=pe_filter)
        if success and 'stocks' in pe_filtered:
            print(f"   Found {len(pe_filtered['stocks'])} stocks with P/E 10-30")
        
        return success

    def test_enhanced_stock_endpoints(self):
        """Test NEW enhanced stock endpoints with real-time data and extended hours"""
        # Test enhanced stock data for AAPL
        success, aapl_enhanced = self.run_test("Enhanced Stock Data (AAPL)", "GET", "stocks/AAPL/enhanced", 200)
        if success:
            print(f"   ✅ AAPL Enhanced Price: ${aapl_enhanced.get('price', 0):.2f}")
            print(f"   Market State: {aapl_enhanced.get('market_state', 'UNKNOWN')}")
            if 'extended_hours' in aapl_enhanced:
                extended = aapl_enhanced['extended_hours']
                if 'premarket' in extended:
                    print(f"   📈 Premarket Data: ${extended['premarket'].get('price', 'N/A')}")
                if 'postmarket' in extended:
                    print(f"   📉 Postmarket Data: ${extended['postmarket'].get('price', 'N/A')}")
        
        # Test extended hours endpoint
        success, extended_hours = self.run_test("Extended Hours Data (AAPL)", "GET", "stocks/AAPL/extended-hours", 200)
        if success:
            print(f"   Market State: {extended_hours.get('market_state', 'UNKNOWN')}")
            print(f"   Regular Price: ${extended_hours.get('regular_price', 0):.2f}")
        
        # Test enhanced data for other popular stocks
        for symbol in ["MSFT", "GOOGL", "TSLA"]:
            success, enhanced_data = self.run_test(f"Enhanced Stock Data ({symbol})", "GET", f"stocks/{symbol}/enhanced", 200)
            if success and enhanced_data.get('price', 0) > 0:
                print(f"   ✅ {symbol} Price: ${enhanced_data['price']:.2f}")
        
        return success

    def test_investment_scoring_endpoints(self):
        """Test NEW Investment Scoring System endpoints - PRIORITY FEATURE"""
        print("\n🎯 Testing Investment Scoring System - NEW FEATURE")
        
        # Test top investment picks
        success, top_picks_data = self.run_test("Investment Top Picks", "GET", "investments/top-picks", 200, params={"limit": 10})
        if success and 'recommendations' in top_picks_data:
            recommendations = top_picks_data['recommendations']
            print(f"   Found {len(recommendations)} top investment picks")
            
            # Check first recommendation structure
            if recommendations:
                first_pick = recommendations[0]
                print(f"   #1 Pick: {first_pick.get('symbol', 'N/A')} - Score: {first_pick.get('total_score', 'N/A')} - Rating: {first_pick.get('rating', 'N/A')}")
                print(f"   Risk Level: {first_pick.get('risk_level', 'N/A')}")
                
                # Verify required fields
                required_fields = ['symbol', 'total_score', 'rating', 'risk_level', 'key_strengths', 'key_risks']
                missing_fields = [field for field in required_fields if field not in first_pick]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in top pick: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present in top pick")
        
        # Test individual stock scoring - AAPL
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   AAPL Risk Level: {aapl_score.get('risk_level', 'N/A')}")
            
            # Check individual scores breakdown
            individual_scores = aapl_score.get('individual_scores', {})
            if individual_scores:
                print(f"   Score Breakdown: {len(individual_scores)} metrics")
                # Show a few key scores
                for key in ['pe_score', 'momentum_score', 'value_score']:
                    if key in individual_scores:
                        print(f"     {key}: {individual_scores[key]}")
        
        # Test sector leaders
        success, sector_data = self.run_test("Sector Leaders (Technology)", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"})
        if success and 'leaders' in sector_data:
            leaders = sector_data['leaders']
            print(f"   Found {len(leaders)} Technology sector leaders")
            if leaders:
                top_leader = leaders[0]
                print(f"   Top Tech Leader: {top_leader.get('symbol', 'N/A')} - Score: {top_leader.get('total_score', 'N/A')}")
        
        # Test different sector
        success, healthcare_data = self.run_test("Sector Leaders (Healthcare)", "GET", "investments/sector-leaders", 200, params={"sector": "Healthcare"})
        if success and 'leaders' in healthcare_data:
            leaders = healthcare_data['leaders']
            print(f"   Found {len(leaders)} Healthcare sector leaders")
        
        # Test risk analysis
        success, risk_data = self.run_test("Risk Analysis", "GET", "investments/risk-analysis", 200)
        if success and 'risk_categories' in risk_data:
            risk_categories = risk_data['risk_categories']
            print(f"   Risk Categories: {list(risk_categories.keys())}")
            
            for risk_level, stocks in risk_categories.items():
                print(f"   {risk_level} Risk: {len(stocks)} stocks")
                if stocks:
                    # Show first stock in each category
                    first_stock = stocks[0]
                    print(f"     Example: {first_stock.get('symbol', 'N/A')} - Score: {first_stock.get('total_score', 'N/A')}")
        
        return success

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid stock symbol
        self.run_test("Invalid Stock Symbol", "GET", "stocks/INVALID123", 500)
        
        # Test invalid portfolio item deletion
        self.run_test("Delete Non-existent Portfolio Item", "DELETE", "portfolio/invalid-id", 404)
        
        # Test invalid watchlist item deletion
        self.run_test("Delete Non-existent Watchlist Item", "DELETE", "watchlist/invalid-id", 404)
        
        # Test invalid investment score
        self.run_test("Invalid Investment Score", "GET", "investments/score/INVALID123", 500)

def main():
    print("🚀 Starting Stock Market API Tests")
    print("=" * 50)
    
    tester = StockMarketAPITester()
    
    # Test basic endpoints
    print("\n📊 Testing Basic Endpoints")
    tester.test_root_endpoint()
    tester.test_market_overview()
    tester.test_top_movers()
    
    # Test NEW ticker endpoints
    print("\n🎯 Testing NEW Ticker Endpoints")
    tester.test_ticker_endpoints()
    
    # Test NEW screener endpoints
    print("\n🔍 Testing NEW Advanced Screener Endpoints")
    tester.test_screener_endpoints()
    
    # Test NEW enhanced endpoints
    print("\n🚀 Testing NEW Enhanced Stock Endpoints")
    tester.test_enhanced_stock_endpoints()
    
    # Test stock data endpoints
    print("\n📈 Testing Stock Data Endpoints")
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    for stock in popular_stocks:
        tester.test_stock_data(stock)
        tester.test_stock_history(stock)
        # Only test technical indicators for AAPL to avoid API rate limits
        if stock == "AAPL":
            tester.test_technical_indicators(stock)
        tester.test_stock_search(stock)
    
    # Test portfolio operations
    print("\n💼 Testing Portfolio Operations")
    tester.test_portfolio_operations()
    
    # Test watchlist operations
    print("\n⭐ Testing Watchlist Operations")
    tester.test_watchlist_operations()
    
    # Test error handling
    print("\n🚨 Testing Error Handling")
    tester.test_error_handling()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())