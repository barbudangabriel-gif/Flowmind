import requests
import json
from datetime import datetime, timedelta

class ComprehensiveAPITester:
    def __init__(self, base_url="https://options-builder.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=10):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    self.test_results.append({"name": name, "status": "PASSED", "data": response_data})
                    return True, response_data
                except:
                    self.test_results.append({"name": name, "status": "PASSED", "data": {}})
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({"name": name, "status": "FAILED", "error": error_data})
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({"name": name, "status": "FAILED", "error": response.text})
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout ({timeout}s)")
            self.test_results.append({"name": name, "status": "TIMEOUT", "error": f"Timeout after {timeout}s"})
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.test_results.append({"name": name, "status": "ERROR", "error": str(e)})
            return False, {}

    def test_portfolio_management_crud(self):
        """Test Portfolio Management API - All CRUD operations"""
        print("\n💼 TESTING PORTFOLIO MANAGEMENT API - CRUD OPERATIONS")
        print("=" * 60)
        
        # Test GET /api/portfolio - retrieve portfolio data
        success, portfolio_data = self.run_test("GET /api/portfolio", "GET", "portfolio", 200)
        if success:
            print(f"   ✅ Portfolio structure: {list(portfolio_data.keys())}")
            print(f"   ✅ Total Value: ${portfolio_data.get('total_value', 0):.2f}")
            print(f"   ✅ Items Count: {len(portfolio_data.get('items', []))}")

        # Test POST /api/portfolio - add new stock positions (AAPL)
        aapl_position = {
            "symbol": "AAPL",
            "shares": 100.0,
            "purchase_price": 225.0,
            "purchase_date": (datetime.now() - timedelta(days=10)).isoformat()
        }
        
        success, aapl_response = self.run_test("POST /api/portfolio (AAPL)", "POST", "portfolio", 200, data=aapl_position)
        aapl_id = None
        if success:
            aapl_id = aapl_response.get('id')
            print(f"   ✅ Added AAPL - ID: {aapl_id}")
            print(f"   ✅ Current Price: ${aapl_response.get('current_price', 0):.2f}")
            print(f"   ✅ Current Value: ${aapl_response.get('current_value', 0):.2f}")
            print(f"   ✅ P&L: ${aapl_response.get('profit_loss', 0):.2f} ({aapl_response.get('profit_loss_percent', 0):.2f}%)")

        # Test POST /api/portfolio - add new stock positions (MSFT)
        msft_position = {
            "symbol": "MSFT",
            "shares": 50.0,
            "purchase_price": 420.0,
            "purchase_date": (datetime.now() - timedelta(days=20)).isoformat()
        }
        
        success, msft_response = self.run_test("POST /api/portfolio (MSFT)", "POST", "portfolio", 200, data=msft_position)
        msft_id = None
        if success:
            msft_id = msft_response.get('id')
            print(f"   ✅ Added MSFT - ID: {msft_id}")
            print(f"   ✅ Current Price: ${msft_response.get('current_price', 0):.2f}")
            print(f"   ✅ P&L: ${msft_response.get('profit_loss', 0):.2f} ({msft_response.get('profit_loss_percent', 0):.2f}%)")

        # Verify portfolio summary with P&L calculations
        success, updated_portfolio = self.run_test("GET /api/portfolio (With Positions)", "GET", "portfolio", 200)
        if success:
            print(f"   ✅ Portfolio Items: {len(updated_portfolio.get('items', []))}")
            print(f"   ✅ Total Value: ${updated_portfolio.get('total_value', 0):.2f}")
            print(f"   ✅ Total Cost: ${updated_portfolio.get('total_cost', 0):.2f}")
            print(f"   ✅ Total P&L: ${updated_portfolio.get('total_profit_loss', 0):.2f} ({updated_portfolio.get('total_profit_loss_percent', 0):.2f}%)")

        # Test DELETE /api/portfolio/{id} - remove positions
        if aapl_id:
            self.run_test(f"DELETE /api/portfolio/{aapl_id}", "DELETE", f"portfolio/{aapl_id}", 200)
        
        if msft_id:
            self.run_test(f"DELETE /api/portfolio/{msft_id}", "DELETE", f"portfolio/{msft_id}", 200)

        return True

    def test_market_data_apis(self):
        """Test Market Data APIs - Essential for dashboard"""
        print("\n📊 TESTING MARKET DATA APIS")
        print("=" * 60)
        
        # Test GET /api/market/overview - market indices data
        success, overview_data = self.run_test("GET /api/market/overview", "GET", "market/overview", 200)
        if success and 'indices' in overview_data:
            indices = overview_data['indices']
            print(f"   ✅ Found {len(indices)} market indices")
            for index in indices:
                symbol = index.get('symbol', 'Unknown')
                price = index.get('price', 0)
                change_pct = index.get('change_percent', 0)
                print(f"   ✅ {symbol}: ${price:.2f} ({change_pct:+.2f}%)")

        # Test GET /api/market/top-movers - gainers and losers
        success, movers_data = self.run_test("GET /api/market/top-movers", "GET", "market/top-movers", 200)
        if success:
            gainers = movers_data.get('gainers', [])
            losers = movers_data.get('losers', [])
            print(f"   ✅ Top Gainers: {len(gainers)} stocks")
            print(f"   ✅ Top Losers: {len(losers)} stocks")
            
            if gainers:
                top_gainer = gainers[0]
                print(f"   ✅ #1 Gainer: {top_gainer.get('symbol', 'N/A')} (+{top_gainer.get('change_percent', 0):.2f}%)")
            
            if losers:
                top_loser = losers[0]
                print(f"   ✅ #1 Loser: {top_loser.get('symbol', 'N/A')} ({top_loser.get('change_percent', 0):.2f}%)")

        return True

    def test_investment_scoring_system(self):
        """Test Investment Scoring System"""
        print("\n🎯 TESTING INVESTMENT SCORING SYSTEM")
        print("=" * 60)
        
        # Test GET /api/investments/score/{symbol} - individual stock scoring (AAPL)
        success, aapl_score = self.run_test("GET /api/investments/score/AAPL", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   ✅ AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   ✅ AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   ✅ Risk Level: {aapl_score.get('risk_level', 'N/A')}")
            print(f"   ✅ Investment Horizon: {aapl_score.get('investment_horizon', 'N/A')}")

        # Test GET /api/investments/score/{symbol} - individual stock scoring (MSFT)
        success, msft_score = self.run_test("GET /api/investments/score/MSFT", "GET", "investments/score/MSFT", 200)
        if success:
            print(f"   ✅ MSFT Score: {msft_score.get('total_score', 'N/A')}")
            print(f"   ✅ MSFT Rating: {msft_score.get('rating', 'N/A')}")
            print(f"   ✅ Risk Level: {msft_score.get('risk_level', 'N/A')}")

        # Test GET /api/investments/top-picks - top recommended stocks (with shorter timeout)
        success, top_picks = self.run_test("GET /api/investments/top-picks", "GET", "investments/top-picks", 200, params={"limit": 5}, timeout=20)
        if success and 'recommendations' in top_picks:
            recommendations = top_picks['recommendations']
            print(f"   ✅ Found {len(recommendations)} top investment picks")
            if recommendations:
                top_pick = recommendations[0]
                print(f"   ✅ #1 Pick: {top_pick.get('symbol', 'N/A')} - Score: {top_pick.get('total_score', 'N/A')}")

        # Test GET /api/investments/sector-leaders - sector analysis
        success, sector_leaders = self.run_test("GET /api/investments/sector-leaders", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"}, timeout=15)
        if success and 'leaders' in sector_leaders:
            leaders = sector_leaders['leaders']
            print(f"   ✅ Found {len(leaders)} Technology sector leaders")
            if leaders:
                top_leader = leaders[0]
                print(f"   ✅ Top Tech Leader: {top_leader.get('symbol', 'N/A')} - Score: {top_leader.get('total_score', 'N/A')}")

        return True

    def test_enhanced_stock_data(self):
        """Test Enhanced Stock Data"""
        print("\n🚀 TESTING ENHANCED STOCK DATA")
        print("=" * 60)
        
        # Test GET /api/stocks/{symbol}/enhanced - detailed stock info (AAPL)
        success, aapl_enhanced = self.run_test("GET /api/stocks/AAPL/enhanced", "GET", "stocks/AAPL/enhanced", 200)
        if success:
            print(f"   ✅ AAPL Price: ${aapl_enhanced.get('price', 0):.2f}")
            print(f"   ✅ Market State: {aapl_enhanced.get('market_state', 'UNKNOWN')}")
            print(f"   ✅ Exchange: {aapl_enhanced.get('exchange', 'N/A')}")
            print(f"   ✅ Sector: {aapl_enhanced.get('sector', 'N/A')}")
            print(f"   ✅ Market Cap: ${aapl_enhanced.get('market_cap', 0):,.0f}")

        # Test GET /api/stocks/{symbol}/enhanced - detailed stock info (MSFT)
        success, msft_enhanced = self.run_test("GET /api/stocks/MSFT/enhanced", "GET", "stocks/MSFT/enhanced", 200)
        if success:
            print(f"   ✅ MSFT Price: ${msft_enhanced.get('price', 0):.2f}")
            print(f"   ✅ Market State: {msft_enhanced.get('market_state', 'UNKNOWN')}")

        # Test GET /api/screener/data - stock screening data
        success, screener_data = self.run_test("GET /api/screener/data", "GET", "screener/data", 200, params={"limit": 10, "exchange": "sp500"})
        if success and 'stocks' in screener_data:
            stocks = screener_data['stocks']
            print(f"   ✅ Found {len(stocks)} stocks in screener")
            print(f"   ✅ Market State: {screener_data.get('market_state', 'UNKNOWN')}")
            
            # Check for real prices
            real_price_count = 0
            for stock in stocks:
                if stock.get('price', 0) > 0:
                    real_price_count += 1
            print(f"   ✅ Stocks with real prices: {real_price_count}/{len(stocks)}")

        return True

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [test for test in self.test_results if test["status"] == "PASSED"]
        failed_tests = [test for test in self.test_results if test["status"] in ["FAILED", "TIMEOUT", "ERROR"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 TOTAL: {self.tests_run}")
        print(f"📈 SUCCESS RATE: {(len(passed_tests)/self.tests_run)*100:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['name']} - {test['status']}")
        
        print("\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['name']}")

def main():
    print("🚀 COMPREHENSIVE FLOWMIND ANALYTICS API TESTING")
    print("Testing Enhanced Portfolio Management with TradeStation-inspired features")
    print("=" * 80)
    
    tester = ComprehensiveAPITester()
    
    # Test all required APIs from review request
    tester.test_portfolio_management_crud()
    tester.test_market_data_apis()
    tester.test_investment_scoring_system()
    tester.test_enhanced_stock_data()
    
    # Generate comprehensive summary
    tester.generate_summary()
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()