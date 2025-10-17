#!/usr/bin/env python3
"""
TradeStation API Connectivity Test
Quick check of TradeStation API connectivity issues as requested in review.

Focus:
1. GET `/api/tradestation/accounts` - Check if TradeStation API is accessible
2. Verify if there are any authentication or connectivity issues
3. Check backend logs for any errors related to TradeStation API calls

The frontend is showing "Error Loading Portfolio - Failed to fetch" which suggests
the TradeStation API endpoints might be down or having connectivity issues.
"""

import requests
import sys
import json
from datetime import datetime

class TradeStationConnectivityTester:
 def __init__(self):
 # Use the correct backend URL from frontend/.env
 # Note: The frontend/.env shows "None" which might be the issue
 self.base_url = "http://localhost:8000"
 self.api_url = f"{self.base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0

 def log_test(self, name, success, details=""):
 """Log test results"""
 self.tests_run += 1
 if success:
 self.tests_passed += 1
 print(f" {name}: PASSED")
 else:
 print(f" {name}: FAILED")

 if details:
 print(f" Details: {details}")
 print()

 def make_request(self, method, endpoint, timeout=30, **kwargs):
 """Make HTTP request with error handling"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 try:
 print(f" Testing: {method} {url}")

 if method == "GET":
 response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
 elif method == "POST":
 response = requests.post(
 url, headers=headers, timeout=timeout, **kwargs
 )

 print(f" Status Code: {response.status_code}")
 print(f" Response Time: {response.elapsed.total_seconds():.2f}s")

 return response

 except requests.exceptions.Timeout:
 print(f" Request timeout after {timeout}s")
 return None
 except requests.exceptions.ConnectionError as e:
 print(f" Connection error: {str(e)}")
 return None
 except Exception as e:
 print(f" Request error: {str(e)}")
 return None

 def test_backend_connectivity(self):
 """Test basic backend connectivity"""
 print(" PHASE 1: Backend Connectivity Test")
 print("-" * 50)

 response = self.make_request("GET", "")

 if response is None:
 self.log_test("Backend Connectivity", False, "Cannot reach backend server")
 return False

 if response.status_code == 200:
 try:
 data = response.json()
 version = data.get("version", "Unknown")
 features = data.get("features", [])
 tradestation_endpoints = data.get("tradestation_endpoints", {})

 self.log_test(
 "Backend Connectivity",
 True,
 f"Backend v{version} accessible, {len(features)} features, {len(tradestation_endpoints)} TS endpoints",
 )
 return True
 except:
 self.log_test("Backend Connectivity", False, "Invalid JSON response")
 return False
 else:
 self.log_test("Backend Connectivity", False, f"HTTP {response.status_code}")
 return False

 def test_tradestation_accounts_endpoint(self):
 """Test GET /api/tradestation/accounts - Primary focus of review"""
 print("🏛️ PHASE 2: TradeStation Accounts Endpoint Test")
 print("-" * 50)

 response = self.make_request("GET", "tradestation/accounts")

 if response is None:
 self.log_test(
 "TradeStation Accounts API", False, "No response from endpoint"
 )
 return False

 print(f" Response Headers: {dict(response.headers)}")

 if response.status_code == 200:
 try:
 data = response.json()

 # Check for the correct response format: {"status": "success", "accounts": [...]}
 if (
 isinstance(data, dict)
 and "accounts" in data
 and data.get("status") == "success"
 ):
 accounts = data["accounts"]
 account_count = len(accounts)

 if account_count > 0:
 first_account = accounts[0]
 account_id = first_account.get("AccountID", "Unknown")
 account_type = first_account.get("AccountType", "Unknown")

 self.log_test(
 "TradeStation Accounts API",
 True,
 f"Found {account_count} accounts, First: {account_id} ({account_type})",
 )

 # Print account details for debugging
 print(" Account Details:")
 for i, account in enumerate(
 accounts[:2]
 ): # Show first 2 accounts
 print(f" Account {i+1}:")
 print(f" - ID: {account.get('AccountID', 'N/A')}")
 print(f" - Type: {account.get('AccountType', 'N/A')}")
 print(f" - Status: {account.get('Status', 'N/A')}")
 print(
 f" - Currency: {account.get('Currency', 'N/A')}"
 )

 return True
 else:
 self.log_test(
 "TradeStation Accounts API",
 False,
 "No accounts found in response",
 )
 return False

 elif isinstance(data, dict):
 # Check if it's an error response
 if "error" in data or "message" in data:
 error_msg = data.get(
 "error", data.get("message", "Unknown error")
 )
 self.log_test(
 "TradeStation Accounts API",
 False,
 f"API Error: {error_msg}",
 )
 return False
 else:
 self.log_test(
 "TradeStation Accounts API",
 False,
 f"Unexpected response format: {data}",
 )
 return False
 else:
 self.log_test(
 "TradeStation Accounts API", False, "Empty or invalid response"
 )
 return False

 except json.JSONDecodeError:
 # Response might be HTML (error page)
 content_type = response.headers.get("content-type", "")
 if "html" in content_type.lower():
 self.log_test(
 "TradeStation Accounts API",
 False,
 "Received HTML instead of JSON - possible routing issue",
 )
 else:
 self.log_test(
 "TradeStation Accounts API", False, "Invalid JSON response"
 )

 # Show first 200 chars of response for debugging
 print(f" Response preview: {response.text[:200]}...")
 return False

 elif response.status_code == 401:
 self.log_test(
 "TradeStation Accounts API",
 False,
 "Authentication required - not logged in",
 )
 return False
 elif response.status_code == 403:
 self.log_test(
 "TradeStation Accounts API",
 False,
 "Access forbidden - authentication issue",
 )
 return False
 elif response.status_code == 404:
 self.log_test(
 "TradeStation Accounts API", False, "Endpoint not found - routing issue"
 )
 return False
 elif response.status_code == 500:
 self.log_test("TradeStation Accounts API", False, "Internal server error")
 return False
 else:
 self.log_test(
 "TradeStation Accounts API", False, f"HTTP {response.status_code}"
 )
 return False

 def test_tradestation_authentication_status(self):
 """Test TradeStation authentication status"""
 print("🔐 PHASE 3: TradeStation Authentication Status")
 print("-" * 50)

 response = self.make_request("GET", "auth/tradestation/status")

 if response is None:
 self.log_test(
 "TradeStation Auth Status", False, "No response from auth endpoint"
 )
 return False

 if response.status_code == 200:
 try:
 data = response.json()

 authenticated = data.get("authenticated", False)
 environment = data.get("environment", "Unknown")
 has_token = data.get("has_access_token", False)
 token_expires = data.get("token_expires_at", "Unknown")

 if authenticated and has_token:
 self.log_test(
 "TradeStation Auth Status",
 True,
 f"Authenticated in {environment}, token expires: {token_expires}",
 )
 return True
 else:
 self.log_test(
 "TradeStation Auth Status",
 False,
 f"Not authenticated (auth: {authenticated}, token: {has_token})",
 )
 return False

 except json.JSONDecodeError:
 self.log_test(
 "TradeStation Auth Status", False, "Invalid JSON response"
 )
 return False
 else:
 self.log_test(
 "TradeStation Auth Status", False, f"HTTP {response.status_code}"
 )
 return False

 def test_tradestation_positions_endpoint(self):
 """Test positions endpoint if we have account access"""
 print(" PHASE 4: TradeStation Positions Test")
 print("-" * 50)

 # First get accounts to find an account ID
 accounts_response = self.make_request("GET", "tradestation/accounts")

 if accounts_response is None or accounts_response.status_code != 200:
 self.log_test(
 "TradeStation Positions", False, "Cannot get accounts for position test"
 )
 return False

 try:
 accounts_data = accounts_response.json()

 # Handle the correct response format
 if isinstance(accounts_data, dict) and "accounts" in accounts_data:
 accounts = accounts_data["accounts"]
 else:
 self.log_test(
 "TradeStation Positions", False, "Invalid accounts response format"
 )
 return False

 if not accounts or len(accounts) == 0:
 self.log_test(
 "TradeStation Positions",
 False,
 "No accounts available for position test",
 )
 return False

 # Use first account
 account_id = accounts[0].get("AccountID")
 if not account_id:
 self.log_test("TradeStation Positions", False, "No account ID found")
 return False

 print(f" Testing positions for account: {account_id}")

 # Test positions endpoint
 positions_response = self.make_request(
 "GET", f"tradestation/accounts/{account_id}/positions"
 )

 if positions_response is None:
 self.log_test(
 "TradeStation Positions",
 False,
 "No response from positions endpoint",
 )
 return False

 if positions_response.status_code == 200:
 try:
 positions_data = positions_response.json()

 if (
 isinstance(positions_data, dict)
 and "positions" in positions_data
 ):
 positions = positions_data["positions"]
 position_count = (
 len(positions) if isinstance(positions, list) else 0
 )

 self.log_test(
 "TradeStation Positions",
 True,
 f"Found {position_count} positions for account {account_id}",
 )

 # Show sample positions
 if positions and len(positions) > 0:
 print(" Sample Positions:")
 for i, pos in enumerate(positions[:3]): # Show first 3
 symbol = pos.get("symbol", "N/A")
 quantity = pos.get("quantity", 0)
 market_value = pos.get("market_value", 0)
 print(
 f" {i+1}. {symbol}: {quantity} shares, ${market_value:.2f}"
 )

 return True
 else:
 self.log_test(
 "TradeStation Positions",
 False,
 "Unexpected positions response format",
 )
 return False

 except json.JSONDecodeError:
 self.log_test(
 "TradeStation Positions",
 False,
 "Invalid JSON in positions response",
 )
 return False
 else:
 self.log_test(
 "TradeStation Positions",
 False,
 f"Positions endpoint returned HTTP {positions_response.status_code}",
 )
 return False

 except Exception as e:
 self.log_test(
 "TradeStation Positions", False, f"Error testing positions: {str(e)}"
 )
 return False

 def test_frontend_backend_url_configuration(self):
 """Check if frontend .env configuration is correct"""
 print(" PHASE 5: Frontend Backend URL Configuration")
 print("-" * 50)

 # Check the actual frontend .env file
 try:
 with open("/app/frontend/.env", "r") as f:
 env_content = f.read()

 if "REACT_APP_BACKEND_URL=" in env_content:
 # Extract the URL
 for line in env_content.split("\n"):
 if line.startswith("REACT_APP_BACKEND_URL="):
 frontend_url = line.split("=", 1)[1]
 break
 else:
 frontend_url = "NOT_FOUND"
 else:
 frontend_url = "NOT_FOUND"

 except Exception as e:
 self.log_test(
 "Frontend URL Configuration",
 False,
 f"Cannot read frontend/.env: {str(e)}",
 )
 return False

 expected_url = "http://localhost:8000"

 if "None" in frontend_url:
 self.log_test(
 "Frontend URL Configuration",
 False,
 f"Frontend .env has 'None' in URL: {frontend_url}",
 )
 print(f" Expected URL: {expected_url}")
 print(f" Actual URL in frontend/.env: {frontend_url}")
 print(
 " 🔧 RECOMMENDATION: Update frontend/.env REACT_APP_BACKEND_URL to correct URL"
 )
 return False
 elif frontend_url == expected_url:
 self.log_test(
 "Frontend URL Configuration",
 True,
 f"Frontend URL is correct: {frontend_url}",
 )
 return True
 else:
 self.log_test(
 "Frontend URL Configuration",
 False,
 f"Frontend URL mismatch - Expected: {expected_url}, Got: {frontend_url}",
 )
 return False

 def run_connectivity_test(self):
 """Run complete TradeStation connectivity test"""
 print("🏛️ TRADESTATION API CONNECTIVITY TEST")
 print("=" * 60)
 print(
 " OBJECTIVE: Diagnose 'Error Loading Portfolio - Failed to fetch' issue"
 )
 print(" FOCUS: TradeStation API endpoints and connectivity")
 print(f" Backend URL: {self.base_url}")
 print(f" Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 print()

 # Run all tests
 backend_ok = self.test_backend_connectivity()
 auth_ok = self.test_tradestation_authentication_status()
 accounts_ok = self.test_tradestation_accounts_endpoint()
 positions_ok = self.test_tradestation_positions_endpoint()
 config_ok = self.test_frontend_backend_url_configuration()

 # Summary
 print(" CONNECTIVITY TEST SUMMARY")
 print("=" * 60)
 print(f"Tests Run: {self.tests_run}")
 print(f"Tests Passed: {self.tests_passed}")
 print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
 print()

 # Diagnosis
 print(" DIAGNOSIS:")

 if not backend_ok:
 print(" CRITICAL: Backend server is not accessible")
 print(" - Check if backend service is running")
 print(" - Verify URL configuration")

 elif not config_ok:
 print(" CRITICAL: Frontend URL configuration issue detected")
 print(" - Frontend .env has 'None' in REACT_APP_BACKEND_URL")
 print(" - This explains 'Failed to fetch' errors")
 print(" - Update frontend/.env with correct backend URL")

 elif not auth_ok:
 print(" WARNING: TradeStation authentication issue")
 print(" - User needs to authenticate with TradeStation")
 print(" - Visit /auth/tradestation/login to authenticate")

 elif not accounts_ok:
 print(" ISSUE: TradeStation accounts endpoint not working")
 print(" - Authentication may be expired")
 print(" - API connectivity issues")
 print(" - Check backend logs for TradeStation API errors")

 elif not positions_ok:
 print(" WARNING: Positions endpoint has issues")
 print(" - May affect portfolio display")
 print(" - Check account permissions")

 else:
 print(" All connectivity tests passed")
 print(" - TradeStation API is accessible")
 print(" - Authentication is working")
 print(" - Issue may be frontend-specific")

 print()
 print("🔧 RECOMMENDATIONS:")

 if not config_ok:
 print("1. 🚨 HIGH PRIORITY: Fix frontend/.env REACT_APP_BACKEND_URL")
 print(
 " - Change from: http://localhost:8000"
 )
 print(" - Change to: http://localhost:8000")

 if not auth_ok:
 print("2. 🔐 Authenticate with TradeStation:")
 print(" - Visit: /auth/tradestation/login")
 print(" - Complete OAuth flow")

 if not accounts_ok:
 print("3. Check TradeStation API status:")
 print(" - Verify API credentials in backend/.env")
 print(" - Check backend logs for API errors")
 print(" - Test with /data-sources/test/AAPL endpoint")

 print("4. 🔄 After fixes, test frontend portfolio loading")
 print("5. Check browser console for additional errors")

 return (
 self.tests_passed >= 3
 ) # At least 3 tests should pass for basic functionality

if __name__ == "__main__":
 tester = TradeStationConnectivityTester()
 success = tester.run_connectivity_test()

 if success:
 print(
 "\n CONNECTIVITY TEST COMPLETED - Issues identified and recommendations provided"
 )
 sys.exit(0)
 else:
 print("\n CONNECTIVITY TEST FAILED - Critical issues found")
 sys.exit(1)
