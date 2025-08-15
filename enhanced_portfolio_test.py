import requests
import json
from datetime import datetime, timedelta

class EnhancedPortfolioTester:
    def __init__(self, base_url="https://flowmind-live.preview.emergentagent.com"):
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
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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
            print(f"❌ Failed - Request timeout (15s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_enhanced_portfolio_features(self):
        """Test enhanced portfolio features with TradeStation-inspired functionality"""
        print("🎯 Testing Enhanced Portfolio Management API")
        
        # Test 1: Get empty portfolio
        success, portfolio_data = self.run_test("Get Portfolio (Empty)", "GET", "portfolio", 200)
        if success:
            print(f"   Portfolio structure: {list(portfolio_data.keys())}")
            
            # Check for enhanced portfolio summary structure
            required_fields = ['total_value', 'total_cost', 'total_profit_loss', 'total_profit_loss_percent', 'items']
            missing_fields = [field for field in required_fields if field not in portfolio_data]
            if missing_fields:
                print(f"   ⚠️  Missing portfolio summary fields: {missing_fields}")
            else:
                print(f"   ✅ All required portfolio summary fields present")

        # Test 2: Add AAPL position
        aapl_position = {
            "symbol": "AAPL",
            "shares": 100.0,
            "purchase_price": 220.0,
            "purchase_date": (datetime.now() - timedelta(days=15)).isoformat()
        }
        
        success, add_response = self.run_test("Add AAPL Position", "POST", "portfolio", 200, data=aapl_position)
        aapl_id = None
        if success and 'id' in add_response:
            aapl_id = add_response['id']
            print(f"   Added AAPL position with ID: {aapl_id}")
            
            # Check enhanced position fields
            enhanced_fields = ['current_price', 'current_value', 'profit_loss', 'profit_loss_percent']
            missing_enhanced = [field for field in enhanced_fields if field not in add_response]
            if missing_enhanced:
                print(f"   ⚠️  Missing enhanced position fields: {missing_enhanced}")
            else:
                print(f"   ✅ All enhanced position fields present")
                print(f"   Current Price: ${add_response.get('current_price', 0):.2f}")
                print(f"   Current Value: ${add_response.get('current_value', 0):.2f}")
                print(f"   P&L: ${add_response.get('profit_loss', 0):.2f} ({add_response.get('profit_loss_percent', 0):.2f}%)")

        # Test 3: Add MSFT position
        msft_position = {
            "symbol": "MSFT",
            "shares": 50.0,
            "purchase_price": 400.0,
            "purchase_date": (datetime.now() - timedelta(days=30)).isoformat()
        }
        
        success, msft_response = self.run_test("Add MSFT Position", "POST", "portfolio", 200, data=msft_position)
        msft_id = None
        if success and 'id' in msft_response:
            msft_id = msft_response['id']
            print(f"   Added MSFT position with ID: {msft_id}")

        # Test 4: Get portfolio with positions and enhanced calculations
        success, full_portfolio = self.run_test("Get Portfolio (With Positions)", "GET", "portfolio", 200)
        if success:
            print(f"   Portfolio Items: {len(full_portfolio.get('items', []))}")
            print(f"   Total Value: ${full_portfolio.get('total_value', 0):.2f}")
            print(f"   Total Cost: ${full_portfolio.get('total_cost', 0):.2f}")
            print(f"   Total P&L: ${full_portfolio.get('total_profit_loss', 0):.2f} ({full_portfolio.get('total_profit_loss_percent', 0):.2f}%)")
            
            # Verify each position has real-time data
            for item in full_portfolio.get('items', []):
                symbol = item.get('symbol', 'Unknown')
                current_price = item.get('current_price', 0)
                if current_price > 0:
                    print(f"   ✅ {symbol}: Real-time price ${current_price:.2f}")
                else:
                    print(f"   ❌ {symbol}: No real-time price data")

        # Test 5: Delete positions
        if aapl_id:
            self.run_test("Delete AAPL Position", "DELETE", f"portfolio/{aapl_id}", 200)
        
        if msft_id:
            self.run_test("Delete MSFT Position", "DELETE", f"portfolio/{msft_id}", 200)

        # Test 6: Verify portfolio is empty again
        self.run_test("Get Portfolio (After Cleanup)", "GET", "portfolio", 200)

    def test_market_data_apis(self):
        """Test market data APIs essential for dashboard"""
        print("\n📊 Testing Market Data APIs")
        
        # Test market overview
        success, overview_data = self.run_test("Market Overview", "GET", "market/overview", 200)
        if success and 'indices' in overview_data:
            indices = overview_data['indices']
            print(f"   Found {len(indices)} market indices")
            for index in indices:
                symbol = index.get('symbol', 'Unknown')
                price = index.get('price', 0)
                change_pct = index.get('change_percent', 0)
                print(f"   {symbol}: ${price:.2f} ({change_pct:+.2f}%)")

        # Test top movers
        success, movers_data = self.run_test("Top Movers", "GET", "market/top-movers", 200)
        if success:
            gainers = movers_data.get('gainers', [])
            losers = movers_data.get('losers', [])
            print(f"   Top Gainers: {len(gainers)} stocks")
            print(f"   Top Losers: {len(losers)} stocks")
            
            if gainers:
                top_gainer = gainers[0]
                print(f"   #1 Gainer: {top_gainer.get('symbol', 'N/A')} (+{top_gainer.get('change_percent', 0):.2f}%)")
            
            if losers:
                top_loser = losers[0]
                print(f"   #1 Loser: {top_loser.get('symbol', 'N/A')} ({top_loser.get('change_percent', 0):.2f}%)")

    def test_investment_scoring_system(self):
        """Test investment scoring system APIs"""
        print("\n🎯 Testing Investment Scoring System")
        
        # Test individual stock scoring for AAPL
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   Risk Level: {aapl_score.get('risk_level', 'N/A')}")

        # Test individual stock scoring for MSFT
        success, msft_score = self.run_test("Investment Score (MSFT)", "GET", "investments/score/MSFT", 200)
        if success:
            print(f"   MSFT Score: {msft_score.get('total_score', 'N/A')}")
            print(f"   MSFT Rating: {msft_score.get('rating', 'N/A')}")

        # Test top picks (with timeout handling)
        try:
            success, top_picks = self.run_test("Top Investment Picks", "GET", "investments/top-picks", 200, params={"limit": 5})
            if success and 'recommendations' in top_picks:
                recommendations = top_picks['recommendations']
                print(f"   Found {len(recommendations)} top picks")
                if recommendations:
                    top_pick = recommendations[0]
                    print(f"   #1 Pick: {top_pick.get('symbol', 'N/A')} - Score: {top_pick.get('total_score', 'N/A')}")
        except:
            print("   ⚠️  Top picks endpoint may have timeout issues")

        # Test sector leaders
        success, sector_leaders = self.run_test("Sector Leaders", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"})
        if success and 'leaders' in sector_leaders:
            leaders = sector_leaders['leaders']
            print(f"   Found {len(leaders)} Technology sector leaders")

    def test_enhanced_stock_data(self):
        """Test enhanced stock data APIs"""
        print("\n🚀 Testing Enhanced Stock Data APIs")
        
        # Test enhanced stock data for AAPL
        success, aapl_enhanced = self.run_test("Enhanced Stock Data (AAPL)", "GET", "stocks/AAPL/enhanced", 200)
        if success:
            print(f"   AAPL Price: ${aapl_enhanced.get('price', 0):.2f}")
            print(f"   Market State: {aapl_enhanced.get('market_state', 'UNKNOWN')}")
            print(f"   Exchange: {aapl_enhanced.get('exchange', 'N/A')}")

        # Test screener data
        success, screener_data = self.run_test("Screener Data", "GET", "screener/data", 200, params={"limit": 10, "exchange": "sp500"})
        if success and 'stocks' in screener_data:
            stocks = screener_data['stocks']
            print(f"   Found {len(stocks)} stocks in screener")
            if stocks:
                sample_stock = stocks[0]
                print(f"   Sample: {sample_stock.get('symbol', 'N/A')} - ${sample_stock.get('price', 0):.2f}")

def main():
    print("🚀 Enhanced Portfolio & Market Data API Tests")
    print("=" * 60)
    
    tester = EnhancedPortfolioTester()
    
    # Test enhanced portfolio features (main focus)
    tester.test_enhanced_portfolio_features()
    
    # Test supporting APIs
    tester.test_market_data_apis()
    tester.test_investment_scoring_system()
    tester.test_enhanced_stock_data()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        return 1

if __name__ == "__main__":
    main()