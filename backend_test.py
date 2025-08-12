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
        """Test stock data endpoint"""
        return self.run_test(f"Stock Data ({symbol})", "GET", f"stocks/{symbol}", 200)

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
        """Test advanced screener endpoints"""
        # Test basic screener data
        success, screener_data = self.run_test("Screener Data (All)", "GET", "screener/data", 200, params={"limit": 20, "exchange": "all"})
        if success and 'stocks' in screener_data:
            print(f"   Found {len(screener_data['stocks'])} stocks in screener")
        
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

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid stock symbol
        self.run_test("Invalid Stock Symbol", "GET", "stocks/INVALID123", 500)
        
        # Test invalid portfolio item deletion
        self.run_test("Delete Non-existent Portfolio Item", "DELETE", "portfolio/invalid-id", 404)
        
        # Test invalid watchlist item deletion
        self.run_test("Delete Non-existent Watchlist Item", "DELETE", "watchlist/invalid-id", 404)

def main():
    print("🚀 Starting Stock Market API Tests")
    print("=" * 50)
    
    tester = StockMarketAPITester()
    
    # Test basic endpoints
    print("\n📊 Testing Basic Endpoints")
    tester.test_root_endpoint()
    tester.test_market_overview()
    tester.test_top_movers()
    
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