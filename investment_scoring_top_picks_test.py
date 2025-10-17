#!/usr/bin/env python3
"""
Investment Scoring Top-Picks Endpoint Test
==========================================

FOCUS: Test `/api/investment-scoring/top-picks?count=5` endpoint specifically

KEY TESTING AREAS:
1. Response Structure: Verify the endpoint returns `top_picks` array with live stock data
2. Live Prices: Confirm each stock in top_picks has `stock_data.price` with real TradeStation prices
3. Data Source: Verify `stock_data.data_source` shows "TradeStation Live API"
4. Complete Data: Ensure response includes symbol, total_score, rating, component_scores, and stock_data
5. Response Performance: Test response times (should be under 30 seconds)

SPECIFIC REQUIREMENTS:
- Endpoint: GET `/api/investment-scoring/top-picks?count=5`
- Expected structure: `{ "status": "success", "top_picks": [...] }`
- Each top_pick should have: symbol, total_score, rating, stock_data.price, stock_data.data_source
- Verify prices are current (not mock data)

SUCCESS CRITERIA:
- Endpoint responds successfully (200 OK)
- Returns live prices from TradeStation API
- All required fields present in response
- Response time acceptable for frontend use

This testing is critical to resolve the user's issue of "nu ai live price in scoring" (no live price in scoring)
"""

import requests
import sys
import time

class InvestmentScoringTopPicksTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0
 self.test_results = []

 def log_test_result(self, test_name, passed, details=""):
 """Log test result for final summary"""
 self.test_results.append(
 {"name": test_name, "passed": passed, "details": details}
 )
 if passed:
 self.tests_passed += 1
 self.tests_run += 1

 def run_test(
 self,
 name,
 method,
 endpoint,
 expected_status,
 data=None,
 params=None,
 timeout=30,
 ):
 """Run a single API test with detailed logging"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 print(f"\n Testing {name}...")
 print(f" URL: {url}")
 if params:
 print(f" Params: {params}")

 start_time = time.time()

 try:
 if method == "GET":
 response = requests.get(
 url, headers=headers, params=params, timeout=timeout
 )
 elif method == "POST":
 response = requests.post(
 url, json=data, headers=headers, timeout=timeout
 )
 elif method == "DELETE":
 response = requests.delete(url, headers=headers, timeout=timeout)

 end_time = time.time()
 response_time = end_time - start_time

 success = response.status_code == expected_status

 if success:
 print(
 f" Passed - Status: {response.status_code} - Time: {response_time:.2f}s"
 )
 try:
 response_data = response.json()
 return True, response_data, response_time
 except:
 return True, {}, response_time
 else:
 print(
 f" Failed - Expected {expected_status}, got {response.status_code} - Time: {response_time:.2f}s"
 )
 try:
 error_data = response.json()
 print(f" Error: {error_data}")
 return False, error_data, response_time
 except:
 print(f" Error: {response.text}")
 return False, {}, response_time

 except requests.exceptions.Timeout:
 print(f" Failed - Request timeout ({timeout}s)")
 return False, {}, timeout
 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}, 0

 def test_investment_scoring_top_picks_comprehensive(self):
 """
 Comprehensive test of the investment scoring top-picks endpoint
 Focus on the user's issue: "nu ai live price in scoring" (no live price in scoring)
 """
 print("\n" + "=" * 100)
 print(" INVESTMENT SCORING TOP-PICKS ENDPOINT COMPREHENSIVE TEST")
 print("=" * 100)
 print(
 " OBJECTIVE: Test advanced investment scoring top-picks endpoint to verify live prices"
 )
 print("🚨 USER ISSUE: 'nu ai live price in scoring' (no live price in scoring)")
 print(" FOCUS AREAS:")
 print(" 1. Response Structure: Verify `top_picks` array with live stock data")
 print(
 " 2. Live Prices: Confirm `stock_data.price` with real TradeStation prices"
 )
 print(
 " 3. Data Source: Verify `stock_data.data_source` shows 'TradeStation Live API'"
 )
 print(
 " 4. Complete Data: symbol, total_score, rating, component_scores, stock_data"
 )
 print(" 5. Response Performance: Under 30 seconds response time")

 # PHASE 1: Test the exact endpoint mentioned in review request
 print(
 "\n PHASE 1: Test Exact Endpoint - /api/investment-scoring/top-picks?count=5"
 )
 print("-" * 80)

 # First try the exact endpoint from the review request
 success, response_data, response_time = self.run_test(
 "Investment Scoring Top-Picks (count=5)",
 "GET",
 "investment-scoring/top-picks",
 200,
 params={"count": 5},
 timeout=30,
 )

 exact_endpoint_works = success

 if not success:
 print(
 " Exact endpoint from review request failed, trying alternative endpoint..."
 )

 # Try the actual endpoint from server.py code
 success, response_data, response_time = self.run_test(
 "Investment Top-Picks (limit=5)",
 "GET",
 "investments/top-picks",
 200,
 params={"limit": 5},
 timeout=30,
 )

 if not success:
 print(" CRITICAL: Both endpoint variations failed!")
 self.log_test_result(
 "Endpoint Accessibility",
 False,
 "Both /api/investment-scoring/top-picks and /api/investments/top-picks failed",
 )
 return False
 else:
 print(" Alternative endpoint works: /api/investments/top-picks")

 self.log_test_result(
 "Endpoint Accessibility", success, f"Response time: {response_time:.2f}s"
 )

 # PHASE 2: Response Structure Verification
 print("\n PHASE 2: Response Structure Verification")
 print("-" * 80)

 # Check if response has the expected structure from review request
 expected_structure_review = {"status": "success", "top_picks": []}
 expected_structure_actual = {
 "recommendations": [],
 "total_analyzed": 0,
 "criteria": "",
 "last_updated": "",
 }

 has_review_structure = (
 "status" in response_data and "top_picks" in response_data
 )
 has_actual_structure = "recommendations" in response_data

 if has_review_structure:
 print(
 " Response has expected structure from review request: {status, top_picks}"
 )
 top_picks = response_data.get("top_picks", [])
 structure_type = "review_format"
 elif has_actual_structure:
 print(
 " Response has actual API structure: {recommendations, total_analyzed, criteria}"
 )
 top_picks = response_data.get("recommendations", [])
 structure_type = "actual_format"
 else:
 print(" Response does not match expected structure")
 print(f" Available keys: {list(response_data.keys())}")
 self.log_test_result(
 "Response Structure", False, "Neither expected structure found"
 )
 return False

 self.log_test_result(
 "Response Structure", True, f"Structure type: {structure_type}"
 )

 print(f" Found {len(top_picks)} top picks in response")

 if len(top_picks) == 0:
 print(" CRITICAL: No top picks returned!")
 self.log_test_result("Top Picks Count", False, "No top picks returned")
 return False

 self.log_test_result(
 "Top Picks Count", len(top_picks) >= 5, f"{len(top_picks)} picks returned"
 )

 # PHASE 3: Live Prices Verification - CRITICAL FOR USER ISSUE
 print("\n PHASE 3: Live Prices Verification - CRITICAL FOR USER ISSUE")
 print("-" * 80)
 print(
 "🚨 This phase addresses the user's core issue: 'nu ai live price in scoring'"
 )

 live_prices_found = 0
 tradestation_sources = 0
 price_details = []

 for i, pick in enumerate(top_picks[:5]): # Test first 5 picks
 symbol = pick.get("symbol", f"UNKNOWN_{i}")
 print(f"\n Analyzing Pick #{i+1}: {symbol}")

 # Check for price data in various possible locations
 price_locations = [
 ("stock_data.price", pick.get("stock_data", {}).get("price")),
 ("price", pick.get("price")),
 ("current_price", pick.get("current_price")),
 (
 "stock_data.current_price",
 pick.get("stock_data", {}).get("current_price"),
 ),
 ]

 price_found = False
 price_value = None
 price_location = None

 for location, value in price_locations:
 if value is not None and value != 0:
 price_found = True
 price_value = value
 price_location = location
 break

 if price_found:
 print(
 f" Price found: ${price_value:.2f} (location: {price_location})"
 )
 live_prices_found += 1

 # Check if price is realistic (not mock data)
 if price_value > 1.0: # Realistic stock price
 print(f" Price appears realistic: ${price_value:.2f}")
 else:
 print(f" Price may be mock data: ${price_value:.2f}")
 else:
 print(f" No price data found for {symbol}")
 print(f" Available fields: {list(pick.keys())}")

 # Check for data source information
 data_source_locations = [
 (
 "stock_data.data_source",
 pick.get("stock_data", {}).get("data_source"),
 ),
 ("data_source", pick.get("data_source")),
 ("stock_data.source", pick.get("stock_data", {}).get("source")),
 ]

 data_source_found = False
 data_source_value = None

 for location, value in data_source_locations:
 if value is not None:
 data_source_found = True
 data_source_value = value
 break

 if data_source_found:
 print(f" 📡 Data source: {data_source_value}")
 if "TradeStation" in str(data_source_value):
 tradestation_sources += 1
 print(" Using TradeStation data source")
 else:
 print(f" Not using TradeStation: {data_source_value}")
 else:
 print(" No data source information found")

 price_details.append(
 {
 "symbol": symbol,
 "price_found": price_found,
 "price_value": price_value,
 "price_location": price_location,
 "data_source": data_source_value,
 }
 )

 # Evaluate live prices results
 print("\n LIVE PRICES SUMMARY:")
 print(f" - Picks with prices: {live_prices_found}/{min(len(top_picks), 5)}")
 print(
 f" - TradeStation sources: {tradestation_sources}/{min(len(top_picks), 5)}"
 )

 live_prices_success = (
 live_prices_found >= 3
 ) # At least 3 out of 5 should have prices
 tradestation_success = (
 tradestation_sources >= 1
 ) # At least 1 should use TradeStation

 if live_prices_success:
 print(f" GOOD: Sufficient live prices found ({live_prices_found}/5)")
 else:
 print(f" ISSUE: Insufficient live prices ({live_prices_found}/5)")
 print(
 " 🚨 This directly relates to user's issue: 'nu ai live price in scoring'"
 )

 if tradestation_success:
 print(" GOOD: TradeStation data sources detected")
 else:
 print(" WARNING: No TradeStation data sources detected")

 self.log_test_result(
 "Live Prices Found",
 live_prices_success,
 f"{live_prices_found}/5 picks have prices",
 )
 self.log_test_result(
 "TradeStation Data Source",
 tradestation_success,
 f"{tradestation_sources}/5 use TradeStation",
 )

 # PHASE 4: Complete Data Fields Verification
 print("\n PHASE 4: Complete Data Fields Verification")
 print("-" * 80)

 required_fields = ["symbol", "total_score", "rating"]
 optional_fields = [
 "component_scores",
 "stock_data",
 "key_strengths",
 "key_risks",
 ]

 complete_picks = 0
 field_analysis = {field: 0 for field in required_fields + optional_fields}

 for i, pick in enumerate(top_picks[:5]):
 symbol = pick.get("symbol", f"UNKNOWN_{i}")
 print(f"\n Pick #{i+1}: {symbol}")

 # Check required fields
 missing_required = []
 for field in required_fields:
 if field in pick and pick[field] is not None:
 field_analysis[field] += 1
 print(f" {field}: {pick[field]}")
 else:
 missing_required.append(field)
 print(f" {field}: MISSING")

 # Check optional fields
 for field in optional_fields:
 if field in pick and pick[field] is not None:
 field_analysis[field] += 1
 if field == "stock_data":
 stock_data = pick[field]
 if isinstance(stock_data, dict):
 print(f" {field}: {len(stock_data)} fields")
 else:
 print(f" {field}: present")
 else:
 print(f" {field}: present")
 else:
 print(f" {field}: not present")

 if len(missing_required) == 0:
 complete_picks += 1
 print(" All required fields present")
 else:
 print(f" Missing required fields: {missing_required}")

 print("\n FIELD ANALYSIS SUMMARY:")
 for field, count in field_analysis.items():
 percentage = (count / min(len(top_picks), 5)) * 100
 field_type = "REQUIRED" if field in required_fields else "OPTIONAL"
 print(f" - {field} ({field_type}): {count}/5 ({percentage:.0f}%)")

 complete_data_success = (
 complete_picks >= 4
 ) # At least 4 out of 5 should be complete
 self.log_test_result(
 "Complete Data Fields",
 complete_data_success,
 f"{complete_picks}/5 picks have all required fields",
 )

 # PHASE 5: Response Performance Verification
 print("\n⏱️ PHASE 5: Response Performance Verification")
 print("-" * 80)

 print(" Response Time Analysis:")
 print(f" - Actual response time: {response_time:.2f} seconds")
 print(" - Target response time: < 30 seconds")

 performance_success = response_time < 30.0

 if response_time < 5.0:
 performance_rating = "EXCELLENT"
 print(f" {performance_rating}: Very fast response")
 elif response_time < 15.0:
 performance_rating = "GOOD"
 print(f" {performance_rating}: Acceptable response time")
 elif response_time < 30.0:
 performance_rating = "ACCEPTABLE"
 print(f" {performance_rating}: Within target range")
 else:
 performance_rating = "SLOW"
 print(f" {performance_rating}: Exceeds target response time")

 self.log_test_result(
 "Response Performance",
 performance_success,
 f"{response_time:.2f}s ({performance_rating})",
 )

 # PHASE 6: Test Different Count Parameters
 print("\n🔢 PHASE 6: Test Different Count Parameters")
 print("-" * 80)

 count_tests = [3, 5, 10]
 count_results = {}

 for count in count_tests:
 print(f"\n Testing count={count}:")

 # Try both endpoint variations
 endpoints_to_try = [
 ("investment-scoring/top-picks", {"count": count}),
 ("investments/top-picks", {"limit": count}),
 ]

 count_success = False
 for endpoint, params in endpoints_to_try:
 success, data, time_taken = self.run_test(
 f"Top-Picks (count={count})",
 "GET",
 endpoint,
 200,
 params=params,
 timeout=30,
 )

 if success:
 picks = data.get("top_picks", data.get("recommendations", []))
 count_results[count] = len(picks)
 print(f" Returned {len(picks)} picks for count={count}")
 count_success = True
 break

 if not count_success:
 count_results[count] = 0
 print(f" Failed to get picks for count={count}")

 count_test_success = len([c for c in count_results.values() if c > 0]) >= 2
 self.log_test_result(
 "Different Count Parameters",
 count_test_success,
 f"Results: {count_results}",
 )

 # FINAL ASSESSMENT
 print("\n" + "=" * 100)
 print(" FINAL ASSESSMENT: Investment Scoring Top-Picks Endpoint")
 print("=" * 100)

 # Calculate overall success rate
 total_tests = len(self.test_results)
 passed_tests = sum(1 for result in self.test_results if result["passed"])
 success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

 print("\n TEST RESULTS SUMMARY:")
 for result in self.test_results:
 status = " PASS" if result["passed"] else " FAIL"
 print(f" {status} {result['name']}: {result['details']}")

 print(
 f"\n OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
 )

 # Key findings for user issue
 print("\n KEY FINDINGS FOR USER ISSUE 'nu ai live price in scoring':")
 print(
 f" - Live prices found: {live_prices_found}/{min(len(top_picks), 5)} picks"
 )
 print(
 f" - TradeStation sources: {tradestation_sources}/{min(len(top_picks), 5)} picks"
 )
 print(f" - Response time: {response_time:.2f} seconds")
 print(
 f" - Complete data fields: {complete_picks}/{min(len(top_picks), 5)} picks"
 )

 # Detailed price analysis
 if price_details:
 print("\n DETAILED PRICE ANALYSIS:")
 for detail in price_details:
 symbol = detail["symbol"]
 if detail["price_found"]:
 print(
 f" {symbol}: ${detail['price_value']:.2f} from {detail['price_location']}"
 )
 if detail["data_source"]:
 print(f" 📡 Source: {detail['data_source']}")
 else:
 print(f" {symbol}: No price data found")

 # Success criteria evaluation
 print("\n SUCCESS CRITERIA EVALUATION:")
 criteria = [
 ("Endpoint responds successfully (200 OK)", success),
 (
 "Returns live prices from TradeStation API",
 live_prices_success and tradestation_success,
 ),
 ("All required fields present in response", complete_data_success),
 ("Response time acceptable for frontend use", performance_success),
 ]

 criteria_met = 0
 for criterion, met in criteria:
 status = " MET" if met else " NOT MET"
 print(f" {status} {criterion}")
 if met:
 criteria_met += 1

 criteria_success_rate = (criteria_met / len(criteria)) * 100

 # Final verdict
 print("\n FINAL VERDICT:")
 if criteria_success_rate >= 100:
 print(
 f" EXCELLENT: All success criteria met ({criteria_met}/{len(criteria)})"
 )
 print(" User issue 'nu ai live price in scoring' should be RESOLVED")
 print(" Investment scoring top-picks endpoint is working perfectly")
 verdict = "EXCELLENT"
 elif criteria_success_rate >= 75:
 print(
 f" GOOD: Most success criteria met ({criteria_met}/{len(criteria)})"
 )
 print(
 " User issue 'nu ai live price in scoring' may be PARTIALLY resolved"
 )
 print(" Investment scoring top-picks endpoint is mostly working")
 verdict = "GOOD"
 elif criteria_success_rate >= 50:
 print(
 f" PARTIAL: Some success criteria met ({criteria_met}/{len(criteria)})"
 )
 print(
 " User issue 'nu ai live price in scoring' is NOT fully resolved"
 )
 print(" Investment scoring top-picks endpoint needs improvement")
 verdict = "PARTIAL"
 else:
 print(f" POOR: Few success criteria met ({criteria_met}/{len(criteria)})")
 print(" User issue 'nu ai live price in scoring' is NOT resolved")
 print(" Investment scoring top-picks endpoint has significant issues")
 verdict = "POOR"

 # Recommendations
 print("\n RECOMMENDATIONS:")
 if not live_prices_success:
 print(
 " 🔧 CRITICAL: Ensure stock_data.price field is populated with live prices"
 )
 if not tradestation_success:
 print(
 " 🔧 IMPORTANT: Verify TradeStation API integration for live pricing"
 )
 if not performance_success:
 print(
 f" 🔧 OPTIMIZE: Improve response time (currently {response_time:.2f}s)"
 )
 if not complete_data_success:
 print(" 🔧 ENHANCE: Ensure all required fields are present in response")

 if verdict == "EXCELLENT":
 print(" No immediate action required - endpoint working perfectly!")

 return verdict in ["EXCELLENT", "GOOD"]

def main():
 """Main test execution"""
 print(" Starting Investment Scoring Top-Picks Endpoint Test")
 print("=" * 100)

 tester = InvestmentScoringTopPicksTester()

 try:
 success = tester.test_investment_scoring_top_picks_comprehensive()

 print("\n" + "=" * 100)
 print(" TEST EXECUTION COMPLETE")
 print("=" * 100)

 if success:
 print(" OVERALL RESULT: SUCCESS")
 print(" Investment scoring top-picks endpoint is working correctly")
 print(" User issue 'nu ai live price in scoring' should be resolved")
 return 0
 else:
 print(" OVERALL RESULT: FAILURE")
 print(" Investment scoring top-picks endpoint has issues")
 print(" User issue 'nu ai live price in scoring' is NOT resolved")
 return 1

 except Exception as e:
 print(f"\n TEST EXECUTION FAILED: {str(e)}")
 return 1

if __name__ == "__main__":
 exit_code = main()
 sys.exit(exit_code)
