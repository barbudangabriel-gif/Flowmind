#!/usr/bin/env python3
"""
Comprehensive Backend API Test for Stock Market Analysis
Focus on high-priority endpoints causing dashboard loading issues
"""
import requests
import json
import time
from datetime import datetime
import sys

class ComprehensiveAPITester:
    def __init__(self, base_url="https://tradesmartview.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.test_results = {}

    def log_result(self, test_name, success, details=None, is_critical=False):
        """Log test result with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if is_critical:
                self.critical_failures.append(test_name)
        
        if details:
            print(f"   {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'critical': is_critical,
            'timestamp': datetime.utcnow().isoformat()
        }

    def test_api_connectivity(self):
        """Test basic API connectivity"""
        print("\n🔌 Testing API Connectivity")
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                features = len(data.get('features', []))
                self.log_result("API Root Endpoint", True, f"Version: {version}, Features: {features}")
                return True
            else:
                self.log_result("API Root Endpoint", False, f"Status: {response.status_code}", True)
                return False
        except Exception as e:
            self.log_result("API Root Endpoint", False, f"Error: {str(e)}", True)
            return False

    def test_market_overview_api(self):
        """Test Market Overview API - CRITICAL for dashboard"""
        print("\n📊 Testing Market Overview API (CRITICAL)")
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/market/overview", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                indices = data.get('indices', [])
                
                if len(indices) >= 4:  # Should have S&P 500, Dow, NASDAQ, Russell
                    # Check for expected indices
                    symbols = [idx.get('symbol') for idx in indices]
                    expected_symbols = ['^GSPC', '^DJI', '^IXIC', '^RUT']
                    found_symbols = [s for s in expected_symbols if s in symbols]
                    
                    # Verify real price data (not zeros)
                    real_prices = [idx for idx in indices if idx.get('price', 0) > 0]
                    
                    if len(found_symbols) >= 3 and len(real_prices) >= 3:
                        details = f"Found {len(indices)} indices, {len(real_prices)} with real prices, Response time: {response_time:.2f}s"
                        self.log_result("Market Overview - Data Quality", True, details)
                        
                        # Test specific index data
                        for idx in indices[:2]:  # Check first 2 indices
                            symbol = idx.get('symbol', 'Unknown')
                            price = idx.get('price', 0)
                            change_pct = idx.get('change_percent', 0)
                            if price > 0:
                                self.log_result(f"Market Overview - {symbol}", True, f"Price: ${price:.2f}, Change: {change_pct:.2f}%")
                            else:
                                self.log_result(f"Market Overview - {symbol}", False, "Zero price detected", True)
                        
                        return True
                    else:
                        self.log_result("Market Overview - Data Quality", False, f"Missing indices or zero prices. Found: {found_symbols}", True)
                        return False
                else:
                    self.log_result("Market Overview - Data Count", False, f"Expected 4+ indices, got {len(indices)}", True)
                    return False
            else:
                self.log_result("Market Overview API", False, f"HTTP {response.status_code}", True)
                return False
                
        except Exception as e:
            self.log_result("Market Overview API", False, f"Error: {str(e)}", True)
            return False

    def test_top_movers_api(self):
        """Test Top Movers API - CRITICAL for dashboard"""
        print("\n📈 Testing Top Movers API (CRITICAL)")
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/market/top-movers", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                gainers = data.get('gainers', [])
                losers = data.get('losers', [])
                
                if len(gainers) >= 3 and len(losers) >= 3:
                    # Check for real price changes (not all zeros)
                    real_gainers = [g for g in gainers if abs(g.get('change_percent', 0)) > 0.01]
                    real_losers = [l for l in losers if abs(l.get('change_percent', 0)) > 0.01]
                    
                    if len(real_gainers) >= 2 and len(real_losers) >= 2:
                        details = f"Gainers: {len(real_gainers)}, Losers: {len(real_losers)}, Response time: {response_time:.2f}s"
                        self.log_result("Top Movers - Data Quality", True, details)
                        
                        # Test specific movers
                        top_gainer = gainers[0]
                        top_loser = losers[0]
                        
                        gainer_symbol = top_gainer.get('symbol', 'Unknown')
                        gainer_change = top_gainer.get('change_percent', 0)
                        self.log_result(f"Top Gainer - {gainer_symbol}", True, f"Change: +{gainer_change:.2f}%")
                        
                        loser_symbol = top_loser.get('symbol', 'Unknown')
                        loser_change = top_loser.get('change_percent', 0)
                        self.log_result(f"Top Loser - {loser_symbol}", True, f"Change: {loser_change:.2f}%")
                        
                        return True
                    else:
                        self.log_result("Top Movers - Real Changes", False, "Most stocks showing 0% change", True)
                        return False
                else:
                    self.log_result("Top Movers - Data Count", False, f"Insufficient movers: {len(gainers)} gainers, {len(losers)} losers", True)
                    return False
            else:
                self.log_result("Top Movers API", False, f"HTTP {response.status_code}", True)
                return False
                
        except Exception as e:
            self.log_result("Top Movers API", False, f"Error: {str(e)}", True)
            return False

    def test_investment_scoring_apis(self):
        """Test Investment Scoring APIs - HIGH PRIORITY"""
        print("\n🎯 Testing Investment Scoring APIs (HIGH PRIORITY)")
        
        # Test individual stock scoring
        test_symbols = ['AAPL', 'GOOGL', 'MSFT']
        scoring_success = True
        
        for symbol in test_symbols:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}/investments/score/{symbol}", timeout=20)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    score = data.get('total_score', 0)
                    rating = data.get('rating', 'Unknown')
                    risk_level = data.get('risk_level', 'Unknown')
                    
                    if score > 0 and rating != 'Unknown':
                        details = f"Score: {score}, Rating: {rating}, Risk: {risk_level}, Time: {response_time:.2f}s"
                        self.log_result(f"Investment Score - {symbol}", True, details)
                    else:
                        self.log_result(f"Investment Score - {symbol}", False, "Invalid score data")
                        scoring_success = False
                else:
                    self.log_result(f"Investment Score - {symbol}", False, f"HTTP {response.status_code}")
                    scoring_success = False
                    
            except Exception as e:
                self.log_result(f"Investment Score - {symbol}", False, f"Error: {str(e)}")
                scoring_success = False
        
        # Test top picks API
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/investments/top-picks?limit=5", timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommendations', [])
                
                if len(recommendations) >= 3:
                    details = f"Found {len(recommendations)} recommendations, Time: {response_time:.2f}s"
                    self.log_result("Investment Top Picks", True, details)
                    
                    # Check first recommendation structure
                    first_pick = recommendations[0]
                    required_fields = ['symbol', 'total_score', 'rating', 'risk_level']
                    missing_fields = [f for f in required_fields if f not in first_pick]
                    
                    if not missing_fields:
                        symbol = first_pick.get('symbol')
                        score = first_pick.get('total_score')
                        self.log_result("Top Pick Structure", True, f"#{1} Pick: {symbol} (Score: {score})")
                    else:
                        self.log_result("Top Pick Structure", False, f"Missing fields: {missing_fields}")
                        scoring_success = False
                else:
                    self.log_result("Investment Top Picks", False, f"Only {len(recommendations)} recommendations")
                    scoring_success = False
            else:
                self.log_result("Investment Top Picks", False, f"HTTP {response.status_code}")
                scoring_success = False
                
        except Exception as e:
            self.log_result("Investment Top Picks", False, f"Error: {str(e)}")
            scoring_success = False
        
        return scoring_success

    def test_enhanced_stock_data_apis(self):
        """Test Enhanced Stock Data APIs"""
        print("\n🚀 Testing Enhanced Stock Data APIs")
        
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        enhanced_success = True
        
        for symbol in test_symbols:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}/stocks/{symbol}/enhanced", timeout=15)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    price = data.get('price', 0)
                    change_pct = data.get('change_percent', 0)
                    market_state = data.get('market_state', 'Unknown')
                    
                    if price > 0:
                        details = f"Price: ${price:.2f}, Change: {change_pct:.2f}%, Market: {market_state}, Time: {response_time:.2f}s"
                        self.log_result(f"Enhanced Stock - {symbol}", True, details)
                        
                        # Check for extended hours data
                        extended_hours = data.get('extended_hours', {})
                        if extended_hours:
                            self.log_result(f"Extended Hours - {symbol}", True, "Pre/post market data available")
                        else:
                            self.log_result(f"Extended Hours - {symbol}", True, "No extended hours data (normal)")
                    else:
                        self.log_result(f"Enhanced Stock - {symbol}", False, "Zero price detected")
                        enhanced_success = False
                else:
                    self.log_result(f"Enhanced Stock - {symbol}", False, f"HTTP {response.status_code}")
                    enhanced_success = False
                    
            except Exception as e:
                self.log_result(f"Enhanced Stock - {symbol}", False, f"Error: {str(e)}")
                enhanced_success = False
        
        # Test screener data API
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/screener/data?limit=10", timeout=20)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                stocks = data.get('stocks', [])
                
                if len(stocks) >= 5:
                    real_prices = [s for s in stocks if s.get('price', 0) > 0]
                    details = f"Found {len(stocks)} stocks, {len(real_prices)} with real prices, Time: {response_time:.2f}s"
                    self.log_result("Screener Data API", True, details)
                else:
                    self.log_result("Screener Data API", False, f"Only {len(stocks)} stocks returned")
                    enhanced_success = False
            else:
                self.log_result("Screener Data API", False, f"HTTP {response.status_code}")
                enhanced_success = False
                
        except Exception as e:
            self.log_result("Screener Data API", False, f"Error: {str(e)}")
            enhanced_success = False
        
        return enhanced_success

    def test_error_handling(self):
        """Test API error handling"""
        print("\n🚨 Testing Error Handling")
        
        # Test invalid stock symbol
        try:
            response = requests.get(f"{self.api_url}/stocks/INVALID123", timeout=10)
            if response.status_code in [404, 500]:
                self.log_result("Error Handling - Invalid Symbol", True, f"Proper error response: {response.status_code}")
            else:
                self.log_result("Error Handling - Invalid Symbol", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Symbol", False, f"Error: {str(e)}")
        
        # Test invalid investment score
        try:
            response = requests.get(f"{self.api_url}/investments/score/INVALID123", timeout=10)
            if response.status_code in [404, 500]:
                self.log_result("Error Handling - Invalid Investment Score", True, f"Proper error response: {response.status_code}")
            else:
                self.log_result("Error Handling - Invalid Investment Score", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Investment Score", False, f"Error: {str(e)}")

    def test_response_times(self):
        """Test API response times"""
        print("\n⏱️  Testing Response Times")
        
        critical_endpoints = [
            ("/market/overview", "Market Overview", 5.0),
            ("/market/top-movers", "Top Movers", 5.0),
            ("/investments/score/AAPL", "Investment Score", 10.0),
            ("/stocks/AAPL/enhanced", "Enhanced Stock", 5.0)
        ]
        
        for endpoint, name, max_time in critical_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}{endpoint}", timeout=max_time + 5)
                response_time = time.time() - start_time
                
                if response.status_code == 200 and response_time <= max_time:
                    self.log_result(f"Response Time - {name}", True, f"{response_time:.2f}s (target: <{max_time}s)")
                elif response.status_code == 200:
                    self.log_result(f"Response Time - {name}", False, f"{response_time:.2f}s (too slow, target: <{max_time}s)")
                else:
                    self.log_result(f"Response Time - {name}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Response Time - {name}", False, f"Error: {str(e)}")

    def run_comprehensive_test(self):
        """Run all tests in priority order"""
        print("🚀 Starting Comprehensive Backend API Tests")
        print("=" * 60)
        print("Focus: Dashboard Loading Issue & High-Priority Endpoints")
        print("=" * 60)
        
        # Test in priority order
        connectivity_ok = self.test_api_connectivity()
        
        if connectivity_ok:
            # Critical dashboard APIs first
            market_overview_ok = self.test_market_overview_api()
            top_movers_ok = self.test_top_movers_api()
            
            # High priority features
            investment_scoring_ok = self.test_investment_scoring_apis()
            enhanced_stock_ok = self.test_enhanced_stock_data_apis()
            
            # Additional tests
            self.test_error_handling()
            self.test_response_times()
        
        # Print comprehensive results
        self.print_final_results()
        
        return len(self.critical_failures) == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        else:
            print(f"\n✅ NO CRITICAL FAILURES")
        
        # Dashboard readiness assessment
        dashboard_critical = ['Market Overview API', 'Top Movers API', 'Market Overview - Data Quality', 'Top Movers - Data Quality']
        dashboard_failures = [f for f in self.critical_failures if any(dc in f for dc in dashboard_critical)]
        
        print(f"\n📊 DASHBOARD READINESS:")
        if not dashboard_failures:
            print("   ✅ Dashboard APIs are working - loading issue should be resolved")
        else:
            print("   ❌ Dashboard APIs have issues - loading problem persists")
            for failure in dashboard_failures:
                print(f"      - {failure}")
        
        # Investment scoring assessment
        investment_failures = [f for f in self.critical_failures if 'Investment' in f]
        print(f"\n🎯 INVESTMENT SCORING SYSTEM:")
        if not investment_failures:
            print("   ✅ Investment scoring system is operational")
        else:
            print("   ❌ Investment scoring system has issues")
        
        print("\n" + "=" * 60)

def main():
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())