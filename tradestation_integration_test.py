#!/usr/bin/env python3
"""
TradeStation Integration and Token Refresh Testing
Comprehensive test suite for TradeStation authentication and API endpoints
"""

import requests
import sys
import json
import time
from typing import Dict, Any, Optional

class TradeStationIntegrationTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0
 self.test_results = []

 print("🔧 TradeStation Integration Tester initialized")
 print(f"📡 Base URL: {self.base_url}")
 print(f"🔗 API URL: {self.api_url}")
 print("=" * 80)

 def run_test(
 self,
 name: str,
 method: str,
 endpoint: str,
 expected_status: int,
 data: Optional[Dict] = None,
 params: Optional[Dict] = None,
 ) -> tuple[bool, Dict]:
 """Run a single API test with comprehensive error handling"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 self.tests_run += 1
 print(f"\n Test {self.tests_run}: {name}")
 print(f" 📡 URL: {url}")
 print(f" Method: {method}")
 if params:
 print(f" Params: {params}")
 if data:
 print(f" Data: {json.dumps(data, indent=2)}")

 try:
 start_time = time.time()

 if method == "GET":
 response = requests.get(url, headers=headers, params=params, timeout=30)
 elif method == "POST":
 response = requests.post(url, json=data, headers=headers, timeout=30)
 elif method == "DELETE":
 response = requests.delete(url, headers=headers, timeout=30)
 else:
 raise ValueError(f"Unsupported HTTP method: {method}")

 end_time = time.time()
 response_time = end_time - start_time

 success = response.status_code == expected_status

 if success:
 self.tests_passed += 1
 print(
 f" PASSED - Status: {response.status_code} (Expected: {expected_status})"
 )
 print(f" ⏱️ Response Time: {response_time:.3f}s")

 try:
 response_data = response.json()
 if isinstance(response_data, dict):
 # Show key fields for readability
 if len(str(response_data)) < 500:
 print(
 f" 📄 Response: {json.dumps(response_data, indent=2)}"
 )
 else:
 # Show summary for large responses
 keys = (
 list(response_data.keys())
 if isinstance(response_data, dict)
 else []
 )
 print(f" 📄 Response Keys: {keys}")
 if "data" in response_data:
 data_keys = (
 list(response_data["data"].keys())
 if isinstance(response_data["data"], dict)
 else []
 )
 print(f" 📄 Data Keys: {data_keys}")
 elif isinstance(response_data, list):
 print(f" 📄 Response: List with {len(response_data)} items")

 self.test_results.append(
 {
 "name": name,
 "status": "PASSED",
 "response_time": response_time,
 "response_data": response_data,
 }
 )
 return True, response_data
 except json.JSONDecodeError:
 print(" 📄 Response: Non-JSON response")
 self.test_results.append(
 {
 "name": name,
 "status": "PASSED",
 "response_time": response_time,
 "response_data": {},
 }
 )
 return True, {}
 else:
 print(
 f" FAILED - Status: {response.status_code} (Expected: {expected_status})"
 )
 print(f" ⏱️ Response Time: {response_time:.3f}s")
 try:
 error_data = response.json()
 print(f" 🚨 Error Response: {json.dumps(error_data, indent=2)}")
 except:
 print(f" 🚨 Error Text: {response.text}")

 self.test_results.append(
 {
 "name": name,
 "status": "FAILED",
 "response_time": response_time,
 "expected_status": expected_status,
 "actual_status": response.status_code,
 "error": response.text,
 }
 )
 return False, {}

 except requests.exceptions.Timeout:
 print(" FAILED - Request timeout (30s)")
 self.test_results.append(
 {
 "name": name,
 "status": "TIMEOUT",
 "error": "Request timeout after 30 seconds",
 }
 )
 return False, {}
 except Exception as e:
 print(f" FAILED - Error: {str(e)}")
 self.test_results.append({"name": name, "status": "ERROR", "error": str(e)})
 return False, {}

 def test_tradestation_auth_status(self) -> bool:
 """Test TradeStation authentication status endpoint"""
 print("\n🔐 PHASE 1: TradeStation Authentication Status Check")
 print("-" * 60)

 success, status_data = self.run_test(
 "TradeStation Auth Status", "GET", "auth/tradestation/status", 200
 )

 if success:
 # Analyze authentication status
 authenticated = status_data.get("authenticated", False)
 has_access_token = status_data.get("has_access_token", False)
 has_refresh_token = status_data.get("has_refresh_token", False)
 environment = status_data.get("environment", "UNKNOWN")
 needs_refresh = status_data.get("needs_refresh", False)

 print(" Authentication Status Analysis:")
 print(f" - Authenticated: {authenticated}")
 print(f" - Has Access Token: {has_access_token}")
 print(f" - Has Refresh Token: {has_refresh_token}")
 print(f" - Environment: {environment}")
 print(f" - Needs Refresh: {needs_refresh}")

 if authenticated:
 print(" TradeStation is authenticated and ready")
 elif has_refresh_token:
 print(" 🔄 TradeStation has refresh token but needs refresh")
 else:
 print(" TradeStation not authenticated - login required")

 return success

 def test_tradestation_login_url(self) -> bool:
 """Test TradeStation login URL generation"""
 print("\n🔗 PHASE 2: TradeStation Login URL Generation")
 print("-" * 60)

 success, login_data = self.run_test(
 "TradeStation Login URL", "GET", "auth/tradestation/login", 200
 )

 if success:
 # Analyze login URL response
 auth_url = login_data.get("auth_url", "")
 state = login_data.get("state", "")
 instructions = login_data.get("instructions", [])
 permissions = login_data.get("permissions", [])

 print(" Login URL Analysis:")
 print(f" - Auth URL Present: {bool(auth_url)}")
 print(f" - State Parameter: {bool(state)}")
 print(f" - Instructions Count: {len(instructions)}")
 print(f" - Permissions Count: {len(permissions)}")

 if auth_url:
 print(" Login URL generated successfully")
 if "tradestation.com" in auth_url:
 print(" URL points to TradeStation domain")
 else:
 print(" URL may not point to TradeStation")

 if instructions:
 print(" Instructions provided:")
 for i, instruction in enumerate(instructions[:3], 1):
 print(f" {i}. {instruction}")

 return success

 def test_tradestation_token_refresh(self) -> bool:
 """Test TradeStation token refresh functionality"""
 print("\n🔄 PHASE 3: TradeStation Token Refresh")
 print("-" * 60)

 success, refresh_data = self.run_test(
 "TradeStation Token Refresh", "POST", "auth/tradestation/refresh", 200
 )

 if success:
 # Analyze refresh response
 status = refresh_data.get("status", "")
 message = refresh_data.get("message", "")
 token_info = refresh_data.get("token_info", {})

 print(" Token Refresh Analysis:")
 print(f" - Status: {status}")
 print(f" - Message: {message}")
 print(f" - Token Info Present: {bool(token_info)}")

 if status == "success":
 print(" Token refresh successful")
 if token_info:
 expires_in = token_info.get("expires_in", 0)
 print(f" - New token expires in: {expires_in}s")
 else:
 print(f" Token refresh status: {status}")

 return success

 def test_tradestation_accounts(self) -> bool:
 """Test TradeStation accounts endpoint"""
 print("\n🏦 PHASE 4: TradeStation Accounts")
 print("-" * 60)

 success, accounts_data = self.run_test(
 "TradeStation Accounts", "GET", "tradestation/accounts", 200
 )

 if success:
 # Analyze accounts response
 if isinstance(accounts_data, dict):
 accounts = accounts_data.get("accounts", [])
 if not accounts:
 # Try direct list format
 accounts = accounts_data if isinstance(accounts_data, list) else []
 else:
 accounts = accounts_data if isinstance(accounts_data, list) else []

 print(" Accounts Analysis:")
 print(f" - Accounts Found: {len(accounts)}")

 if accounts:
 print(" TradeStation accounts retrieved successfully")
 for i, account in enumerate(accounts[:3], 1):
 account_id = account.get(
 "AccountID", account.get("account_id", "N/A")
 )
 account_type = account.get("Type", account.get("type", "N/A"))
 status = account.get("Status", account.get("status", "N/A"))
 print(f" Account {i}: {account_id} ({account_type}) - {status}")
 else:
 print(" No accounts found - may need authentication")

 return success

 def test_tradestation_positions(self, account_id: str = None) -> bool:
 """Test TradeStation positions endpoint"""
 print("\n PHASE 5: TradeStation Positions")
 print("-" * 60)

 # If no account_id provided, try to get it from accounts first
 if not account_id:
 print(" No account ID provided, attempting to get from accounts...")
 accounts_success, accounts_data = self.run_test(
 "Get Account for Positions", "GET", "tradestation/accounts", 200
 )

 if accounts_success:
 if isinstance(accounts_data, dict):
 accounts = accounts_data.get("accounts", [])
 if not accounts:
 accounts = (
 accounts_data if isinstance(accounts_data, list) else []
 )
 else:
 accounts = accounts_data if isinstance(accounts_data, list) else []

 if accounts:
 account_id = accounts[0].get(
 "AccountID", accounts[0].get("account_id")
 )
 print(f" Using account ID: {account_id}")
 else:
 print(" No accounts available for positions test")
 return False
 else:
 print(" Could not retrieve accounts for positions test")
 return False

 if not account_id:
 print(" No valid account ID available")
 return False

 success, positions_data = self.run_test(
 f"TradeStation Positions ({account_id})",
 "GET",
 f"tradestation/positions/{account_id}",
 200,
 )

 if success:
 # Analyze positions response
 positions = []
 if isinstance(positions_data, dict):
 positions = positions_data.get(
 "positions", positions_data.get("data", [])
 )
 elif isinstance(positions_data, list):
 positions = positions_data

 print(" Positions Analysis:")
 print(f" - Positions Found: {len(positions)}")

 if positions:
 print(" TradeStation positions retrieved successfully")

 # Analyze position types
 stocks = [
 p
 for p in positions
 if p.get("asset_type", "").upper() in ["STOCK", "EQ"]
 ]
 options = [
 p
 for p in positions
 if p.get("asset_type", "").upper() in ["OPTION", "OP"]
 ]

 print(f" - Stock Positions: {len(stocks)}")
 print(f" - Option Positions: {len(options)}")

 # Show sample positions
 for i, position in enumerate(positions[:3], 1):
 symbol = position.get("symbol", "N/A")
 quantity = position.get("quantity", 0)
 market_value = position.get("market_value", 0)
 print(
 f" Position {i}: {symbol} - {quantity} shares - ${market_value:.2f}"
 )
 else:
 print(" No positions found in account")

 return success

 def test_tradestation_balances(self, account_id: str = None) -> bool:
 """Test TradeStation balances endpoint"""
 print("\n PHASE 6: TradeStation Balances")
 print("-" * 60)

 # If no account_id provided, try to get it from accounts first
 if not account_id:
 print(" No account ID provided, attempting to get from accounts...")
 accounts_success, accounts_data = self.run_test(
 "Get Account for Balances", "GET", "tradestation/accounts", 200
 )

 if accounts_success:
 if isinstance(accounts_data, dict):
 accounts = accounts_data.get("accounts", [])
 if not accounts:
 accounts = (
 accounts_data if isinstance(accounts_data, list) else []
 )
 else:
 accounts = accounts_data if isinstance(accounts_data, list) else []

 if accounts:
 account_id = accounts[0].get(
 "AccountID", accounts[0].get("account_id")
 )
 print(f" Using account ID: {account_id}")
 else:
 print(" No accounts available for balances test")
 return False
 else:
 print(" Could not retrieve accounts for balances test")
 return False

 if not account_id:
 print(" No valid account ID available")
 return False

 success, balances_data = self.run_test(
 f"TradeStation Balances ({account_id})",
 "GET",
 f"tradestation/balances/{account_id}",
 200,
 )

 if success:
 # Analyze balances response
 print(" Balances Analysis:")

 if isinstance(balances_data, dict):
 # Look for common balance fields
 balance_fields = [
 "total_value",
 "cash_balance",
 "buying_power",
 "equity",
 "market_value",
 ]
 found_fields = []

 for field in balance_fields:
 if field in balances_data:
 value = balances_data[field]
 found_fields.append(field)
 print(
 f" - {field.replace('_', ' ').title()}: ${value:,.2f}"
 if isinstance(value, (int, float))
 else f" - {field.replace('_', ' ').title()}: {value}"
 )

 if found_fields:
 print(" TradeStation balances retrieved successfully")
 print(f" - Balance fields found: {len(found_fields)}")
 else:
 print(" Balance data structure may be different than expected")
 print(f" - Available keys: {list(balances_data.keys())}")
 else:
 print(" Unexpected balances response format")

 return success

 def test_token_auto_refresh_mechanism(self) -> bool:
 """Test token auto-refresh mechanism by checking status before and after operations"""
 print("\n🔄 PHASE 7: Token Auto-Refresh Mechanism")
 print("-" * 60)

 # Get initial auth status
 print(" Step 1: Check initial authentication status")
 initial_success, initial_status = self.run_test(
 "Initial Auth Status", "GET", "auth/tradestation/status", 200
 )

 if not initial_success:
 print(" Could not get initial auth status")
 return False

 initial_authenticated = initial_status.get("authenticated", False)
 initial_needs_refresh = initial_status.get("needs_refresh", False)

 print(f" - Initial Authenticated: {initial_authenticated}")
 print(f" - Initial Needs Refresh: {initial_needs_refresh}")

 # Perform multiple API calls to test auto-refresh
 print(" Step 2: Perform multiple API calls to test auto-refresh")

 api_calls = [
 ("accounts", "GET", "tradestation/accounts"),
 ("auth status", "GET", "auth/tradestation/status"),
 ]

 auto_refresh_working = True
 for call_name, method, endpoint in api_calls:
 print(f" Testing {call_name}...")
 success, _ = self.run_test(
 f"Auto-refresh test: {call_name}", method, endpoint, 200
 )

 if not success:
 print(f" {call_name} failed - auto-refresh may not be working")
 auto_refresh_working = False
 else:
 print(f" {call_name} succeeded")

 # Check final auth status
 print(" Step 3: Check final authentication status")
 final_success, final_status = self.run_test(
 "Final Auth Status", "GET", "auth/tradestation/status", 200
 )

 if final_success:
 final_authenticated = final_status.get("authenticated", False)
 final_needs_refresh = final_status.get("needs_refresh", False)

 print(f" - Final Authenticated: {final_authenticated}")
 print(f" - Final Needs Refresh: {final_needs_refresh}")

 if final_authenticated and auto_refresh_working:
 print(" Token auto-refresh mechanism appears to be working")
 return True
 else:
 print(" Token auto-refresh mechanism may have issues")
 return False
 else:
 print(" Could not get final auth status")
 return False

 def run_comprehensive_test(self) -> Dict[str, Any]:
 """Run comprehensive TradeStation integration test suite"""
 print(" STARTING COMPREHENSIVE TRADESTATION INTEGRATION TEST")
 print("=" * 80)
 print(
 " OBJECTIVE: Test TradeStation integration and token refresh functionality"
 )
 print(" TEST PHASES:")
 print(" 1. Authentication Status Check")
 print(" 2. Login URL Generation")
 print(" 3. Token Refresh")
 print(" 4. Accounts Retrieval")
 print(" 5. Positions Retrieval")
 print(" 6. Balances Retrieval")
 print(" 7. Token Auto-Refresh Mechanism")
 print("=" * 80)

 start_time = time.time()

 # Run all test phases
 test_phases = [
 ("Authentication Status", self.test_tradestation_auth_status),
 ("Login URL Generation", self.test_tradestation_login_url),
 ("Token Refresh", self.test_tradestation_token_refresh),
 ("Accounts Retrieval", self.test_tradestation_accounts),
 ("Positions Retrieval", self.test_tradestation_positions),
 ("Balances Retrieval", self.test_tradestation_balances),
 ("Token Auto-Refresh", self.test_token_auto_refresh_mechanism),
 ]

 phase_results = {}
 passed_phases = 0

 for phase_name, test_function in test_phases:
 try:
 result = test_function()
 phase_results[phase_name] = result
 if result:
 passed_phases += 1
 except Exception as e:
 print(f"\n PHASE FAILED: {phase_name} - {str(e)}")
 phase_results[phase_name] = False

 end_time = time.time()
 total_time = end_time - start_time

 # Generate comprehensive report
 print("\n" + "=" * 80)
 print(" COMPREHENSIVE TEST RESULTS")
 print("=" * 80)

 print("\n OVERALL STATISTICS:")
 print(f" - Total Tests Run: {self.tests_run}")
 print(f" - Tests Passed: {self.tests_passed}")
 print(f" - Tests Failed: {self.tests_run - self.tests_passed}")
 print(f" - Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
 print(f" - Total Time: {total_time:.2f}s")

 print("\n PHASE RESULTS:")
 for phase_name, result in phase_results.items():
 status = " PASSED" if result else " FAILED"
 print(f" {status} {phase_name}")

 phase_success_rate = (passed_phases / len(test_phases)) * 100
 print(
 f"\n PHASE SUCCESS RATE: {phase_success_rate:.1f}% ({passed_phases}/{len(test_phases)} phases passed)"
 )

 # Critical issues analysis
 print("\n CRITICAL ISSUES ANALYSIS:")
 critical_issues = []

 if not phase_results.get("Authentication Status", False):
 critical_issues.append(" Authentication status endpoint not working")

 if not phase_results.get("Token Refresh", False):
 critical_issues.append(" Token refresh functionality not working")

 if not phase_results.get("Accounts Retrieval", False):
 critical_issues.append(" Accounts endpoint not accessible")

 if not phase_results.get("Token Auto-Refresh", False):
 critical_issues.append(" Auto-refresh mechanism not functioning")

 if critical_issues:
 print(" 🚨 CRITICAL ISSUES FOUND:")
 for issue in critical_issues:
 print(f" {issue}")
 else:
 print(" No critical issues detected")

 # Recommendations
 print("\n RECOMMENDATIONS:")
 if phase_success_rate >= 85:
 print(" EXCELLENT: TradeStation integration is working well")
 print(" Token refresh functionality is stable")
 print(" All major endpoints are accessible")
 elif phase_success_rate >= 70:
 print(" GOOD: TradeStation integration mostly working")
 print(" Some minor issues detected - review failed phases")
 elif phase_success_rate >= 50:
 print(" MODERATE: TradeStation integration has significant issues")
 print(" 🔧 Focus on fixing authentication and token refresh")
 else:
 print(" 🚨 CRITICAL: TradeStation integration is not working properly")
 print(" 🔧 Major fixes needed for authentication system")
 print(" 🔧 Check API endpoint implementations")

 # Final verdict
 print("\n FINAL VERDICT:")
 if phase_success_rate >= 85 and self.tests_passed >= (self.tests_run * 0.8):
 print(
 " EXCELLENT - TradeStation integration and token refresh working perfectly!"
 )
 verdict = "EXCELLENT"
 elif phase_success_rate >= 70 and self.tests_passed >= (self.tests_run * 0.7):
 print(" GOOD - TradeStation integration working with minor issues")
 verdict = "GOOD"
 elif phase_success_rate >= 50:
 print(" MODERATE - TradeStation integration needs attention")
 verdict = "MODERATE"
 else:
 print(" 🚨 CRITICAL - TradeStation integration requires immediate fixes")
 verdict = "CRITICAL"

 return {
 "verdict": verdict,
 "phase_success_rate": phase_success_rate,
 "overall_success_rate": (self.tests_passed / self.tests_run * 100)
 if self.tests_run > 0
 else 0,
 "tests_run": self.tests_run,
 "tests_passed": self.tests_passed,
 "phase_results": phase_results,
 "critical_issues": critical_issues,
 "total_time": total_time,
 "test_results": self.test_results,
 }

def main():
 """Main function to run TradeStation integration tests"""
 print("🔧 TradeStation Integration and Token Refresh Testing")
 print("=" * 80)

 tester = TradeStationIntegrationTester()
 results = tester.run_comprehensive_test()

 # Exit with appropriate code
 if results["verdict"] in ["EXCELLENT", "GOOD"]:
 sys.exit(0)
 else:
 sys.exit(1)

if __name__ == "__main__":
 main()
