#!/usr/bin/env python3
"""
TradeStation Direct API Final Test
Based on actual response structure analysis
"""

import requests
from datetime import datetime

class TradeStationFinalTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.account_id = "11775499"
 self.expected_portfolio_value = 969473.90

 def test_tradestation_endpoints(self):
 """Test TradeStation endpoints with correct data structure handling"""
 print("🏛️ TRADESTATION DIRECT API ENDPOINTS - FINAL TEST")
 print("=" * 80)
 print(" REVIEW REQUEST: Quick test of TradeStation Direct API endpoints")
 print(
 " FOCUS: API response status codes, data availability, portfolio value verification"
 )
 print(f" Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

 results = {
 "accounts_working": False,
 "positions_working": False,
 "authentication_working": False,
 "target_account_found": False,
 "portfolio_value_correct": False,
 "total_positions": 0,
 "actual_portfolio_value": 0,
 "issues_found": [],
 }

 # Test 1: Authentication Status
 print("\n🔐 PHASE 1: Authentication Status")
 print("-" * 60)

 try:
 response = requests.get(
 f"{self.api_url}/auth/tradestation/status", timeout=30
 )
 if response.status_code == 200:
 auth_data = response.json()
 auth_status = auth_data.get("authentication", {})

 authenticated = auth_status.get("authenticated", False)
 environment = auth_status.get("environment", "Unknown")
 has_access_token = auth_status.get("has_access_token", False)

 print(f" Authentication Status: {response.status_code}")
 print(f" - Authenticated: {authenticated}")
 print(f" - Environment: {environment}")
 print(f" - Has Access Token: {has_access_token}")

 if authenticated and has_access_token:
 results["authentication_working"] = True
 print(" TradeStation authentication is WORKING")
 else:
 results["issues_found"].append(
 "TradeStation not properly authenticated"
 )
 print(" TradeStation authentication issues")
 else:
 results["issues_found"].append(
 f"Auth status endpoint returned {response.status_code}"
 )
 print(f" Auth Status: {response.status_code}")
 except Exception as e:
 results["issues_found"].append(f"Auth status error: {str(e)}")
 print(f" Auth Status Error: {e}")

 # Test 2: Accounts Endpoint
 print("\n🏛️ PHASE 2: Accounts Endpoint")
 print("-" * 60)

 try:
 response = requests.get(f"{self.api_url}/tradestation/accounts", timeout=30)
 if response.status_code == 200:
 accounts_data = response.json()
 accounts = accounts_data.get("accounts", [])

 print(f" Accounts Endpoint: {response.status_code}")
 print(f" - Total Accounts: {len(accounts)}")

 # Look for target account
 target_account = None
 for account in accounts:
 account_id = account.get("AccountID")
 account_type = account.get("AccountType")
 status = account.get("Status")

 print(f" - Account: {account_id} ({account_type}) - {status}")

 if account_id == self.account_id:
 target_account = account
 results["target_account_found"] = True
 print(f" TARGET ACCOUNT FOUND: {account_id}")

 if target_account:
 results["accounts_working"] = True
 else:
 results["issues_found"].append(
 f"Target account {self.account_id} not found"
 )
 print(f" Target account {self.account_id} not found")
 else:
 results["issues_found"].append(
 f"Accounts endpoint returned {response.status_code}"
 )
 print(f" Accounts Endpoint: {response.status_code}")
 except Exception as e:
 results["issues_found"].append(f"Accounts endpoint error: {str(e)}")
 print(f" Accounts Error: {e}")

 # Test 3: Positions Endpoint
 print("\n PHASE 3: Positions Endpoint")
 print("-" * 60)

 try:
 response = requests.get(
 f"{self.api_url}/tradestation/accounts/{self.account_id}/positions",
 timeout=30,
 )
 if response.status_code == 200:
 positions_data = response.json()
 positions = positions_data.get("positions", [])

 print(f" Positions Endpoint: {response.status_code}")
 print(f" - Total Positions: {len(positions)}")

 results["total_positions"] = len(positions)

 if len(positions) > 0:
 results["positions_working"] = True

 # Calculate portfolio metrics
 total_market_value = 0
 total_unrealized_pnl = 0
 stocks_count = 0
 options_count = 0

 print("\n POSITION ANALYSIS (Top 10):")
 for i, position in enumerate(positions[:10]):
 symbol = position.get("symbol")
 quantity = position.get("quantity", 0)
 market_value = position.get("market_value", 0)
 unrealized_pnl = position.get("unrealized_pnl", 0)
 asset_type = position.get("asset_type", "Unknown")

 print(
 f" {i+1:2d}. {symbol}: {quantity} shares, ${market_value:,.2f}, ${unrealized_pnl:+,.2f} P&L ({asset_type})"
 )

 total_market_value += market_value
 total_unrealized_pnl += unrealized_pnl

 if asset_type == "STOCK":
 stocks_count += 1
 elif "OPTION" in asset_type:
 options_count += 1

 if len(positions) > 10:
 # Calculate remaining positions
 for position in positions[10:]:
 total_market_value += position.get("market_value", 0)
 total_unrealized_pnl += position.get("unrealized_pnl", 0)

 results["actual_portfolio_value"] = total_market_value

 print("\n PORTFOLIO SUMMARY:")
 print(f" - Total Positions: {len(positions)}")
 print(f" - Stocks: {stocks_count}")
 print(f" - Options: {options_count}")
 print(f" - Total Market Value: ${total_market_value:,.2f}")
 print(f" - Total Unrealized P&L: ${total_unrealized_pnl:+,.2f}")

 # Compare with expected value
 print("\n VALUE VERIFICATION:")
 print(
 f" - Expected Portfolio Value: ${self.expected_portfolio_value:,.2f}"
 )
 print(f" - Actual Portfolio Value: ${total_market_value:,.2f}")

 value_difference = abs(
 total_market_value - self.expected_portfolio_value
 )
 value_difference_percent = (
 value_difference / self.expected_portfolio_value
 ) * 100

 print(
 f" - Difference: ${value_difference:,.2f} ({value_difference_percent:.2f}%)"
 )

 if value_difference_percent < 5:
 results["portfolio_value_correct"] = True
 print(" Portfolio value matches expected (within 5%)")
 elif value_difference_percent < 15:
 results["portfolio_value_correct"] = True
 print(" Portfolio value close to expected (within 15%)")
 else:
 results["issues_found"].append(
 f"Portfolio value differs by {value_difference_percent:.1f}%"
 )
 print(
 f" Portfolio value differs significantly ({value_difference_percent:.1f}%)"
 )
 else:
 results["issues_found"].append("No positions found in account")
 print(" No positions found")
 else:
 results["issues_found"].append(
 f"Positions endpoint returned {response.status_code}"
 )
 print(f" Positions Endpoint: {response.status_code}")
 print(" 🚨 This explains the 'Failed to fetch positions' error!")
 except Exception as e:
 results["issues_found"].append(f"Positions endpoint error: {str(e)}")
 print(f" Positions Error: {e}")

 return results

 def generate_final_report(self, results):
 """Generate final test report"""
 print("\n FINAL ASSESSMENT: TradeStation Direct API")
 print("=" * 80)

 # Test results summary
 test_results = [
 ("Authentication Working", results["authentication_working"]),
 ("Accounts Endpoint Working", results["accounts_working"]),
 ("Positions Endpoint Working", results["positions_working"]),
 ("Target Account Found", results["target_account_found"]),
 ("Portfolio Value Verification", results["portfolio_value_correct"]),
 ]

 passed_tests = sum(1 for _, passed in test_results if passed)
 total_tests = len(test_results)
 success_rate = (passed_tests / total_tests) * 100

 print("\n TEST RESULTS SUMMARY:")
 for test_name, passed in test_results:
 status = " PASS" if passed else " FAIL"
 print(f" {status} {test_name}")

 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
 )

 # Key findings
 print("\n KEY FINDINGS:")
 if results["authentication_working"]:
 print(" TradeStation authentication is working correctly")
 else:
 print(" TradeStation authentication has issues")

 if results["accounts_working"]:
 print(" GET /api/tradestation/accounts is working correctly")
 else:
 print(" GET /api/tradestation/accounts has issues")

 if results["positions_working"]:
 print(
 " GET /api/tradestation/accounts/11775499/positions is working correctly"
 )
 print(f" Found {results['total_positions']} positions")
 else:
 print(" GET /api/tradestation/accounts/11775499/positions failed")
 print(" 🚨 This explains the 'Failed to fetch positions' error")

 if results["target_account_found"]:
 print(f" Target account {self.account_id} is accessible")
 else:
 print(f" Target account {self.account_id} not found")

 if results["actual_portfolio_value"] > 0:
 print(f" Portfolio value: ${results['actual_portfolio_value']:,.2f}")
 if results["portfolio_value_correct"]:
 print(
 f" Portfolio value matches expected ${self.expected_portfolio_value:,.2f}"
 )
 else:
 print(
 f" Portfolio value differs from expected ${self.expected_portfolio_value:,.2f}"
 )

 # Issues found
 if results["issues_found"]:
 print("\n ISSUES IDENTIFIED:")
 for i, issue in enumerate(results["issues_found"], 1):
 print(f" {i}. {issue}")
 else:
 print("\n NO CRITICAL ISSUES FOUND")

 # Frontend analysis
 print("\n🖥️ FRONTEND ERROR ANALYSIS:")
 if results["positions_working"]:
 print(" TradeStation positions endpoint is working correctly")
 print(
 f" Returns {results['total_positions']} positions with proper data structure"
 )
 print(" 'Failed to fetch positions' error is likely a frontend issue:")
 print(" - Check frontend error handling")
 print(" - Verify API URL configuration")
 print(" - Check for CORS or network issues")
 print(" - Verify frontend data parsing logic")
 else:
 print(" TradeStation positions endpoint is failing")
 print(" 🚨 This directly explains the 'Failed to fetch positions' error")

 # Final verdict
 print("\n FINAL VERDICT:")
 if success_rate >= 80:
 print(
 " EXCELLENT: TradeStation Direct API endpoints are working correctly"
 )
 print(" Both requested endpoints are functional:")
 print(" - GET /api/tradestation/accounts ")
 print(" - GET /api/tradestation/accounts/11775499/positions ")
 print(" Authentication and connectivity are working")
 print(
 f" Portfolio value ${results['actual_portfolio_value']:,.2f} is accessible"
 )
 if not results["portfolio_value_correct"]:
 print(" Portfolio value differs from expected, but API is working")
 print(
 " 🔧 'Failed to fetch positions' error is a frontend issue, not API"
 )
 elif success_rate >= 60:
 print(" GOOD: TradeStation API mostly working with some issues")
 print(" 🔧 Some endpoints may need attention")
 else:
 print(" CRITICAL: TradeStation API has significant issues")
 print(" 🚨 This explains the 'Failed to fetch positions' error")

 # Recommendations
 print("\n RECOMMENDATIONS:")
 if results["positions_working"]:
 print(" 1. TradeStation API is working - focus on frontend debugging")
 print(" 2. Check frontend network requests and error handling")
 print(" 3. Verify frontend API URL configuration")
 print(" 4. Test frontend with browser developer tools")
 else:
 print(" 1. Fix TradeStation API connectivity issues")
 print(" 2. Check authentication and credentials")
 print(" 3. Verify account permissions")

 return success_rate >= 60

def main():
 print(" Starting TradeStation Direct API Final Test...")

 tester = TradeStationFinalTester()
 results = tester.test_tradestation_endpoints()
 success = tester.generate_final_report(results)

 print("\n TEST COMPLETION:")
 print(f" - Authentication: {'' if results['authentication_working'] else ''}")
 print(f" - Accounts Endpoint: {'' if results['accounts_working'] else ''}")
 print(f" - Positions Endpoint: {'' if results['positions_working'] else ''}")
 print(f" - Portfolio Value: ${results['actual_portfolio_value']:,.2f}")

 return success

if __name__ == "__main__":
 success = main()
 exit(0 if success else 1)
