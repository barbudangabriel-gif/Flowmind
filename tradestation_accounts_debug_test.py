#!/usr/bin/env python3
"""
TradeStation Accounts Endpoint Debug Test
=========================================

This test specifically debugs the TradeStation accounts endpoint to understand
why Portfolio Management Service can't access accounts and falls back to mock data.

Review Request Focus:
1. GET `/api/tradestation/accounts` - Test direct accounts endpoint and verify response structure
2. Check if the accounts response includes account 11775499 in the correct format
3. Verify the response structure matches what Portfolio Management Service expects

Based on test_result.md findings:
- TradeStation authentication works (authenticated=true, has_access_token=true)
- But accounts endpoint returns 0 accounts
- This causes Portfolio Management Service to fall back to mock data
- User sees fake positions instead of real TradeStation positions
"""

import requests
import json
import sys

class TradeStationAccountsDebugger:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.target_account = "11775499" # The account that should be present

 def debug_print(self, title, data, level="INFO"):
 """Enhanced debug printing with structure analysis"""
 print(f"\n{'='*60}")
 print(f" {level}: {title}")
 print(f"{'='*60}")

 if isinstance(data, dict):
 print(f" Response Type: Dictionary with {len(data)} keys")
 print(f" Keys: {list(data.keys())}")

 # Pretty print the JSON with proper formatting
 try:
 formatted_json = json.dumps(data, indent=2, default=str)
 print(" Full Response Structure:")
 print(formatted_json)
 except Exception as e:
 print(f" JSON formatting error: {e}")
 print(f" Raw Data: {data}")

 elif isinstance(data, list):
 print(f" Response Type: List with {len(data)} items")
 if data:
 print(f" First item type: {type(data[0])}")
 if isinstance(data[0], dict):
 print(f" First item keys: {list(data[0].keys())}")

 # Print each item
 for i, item in enumerate(data):
 print(f" Item {i+1}:")
 try:
 formatted_item = json.dumps(item, indent=2, default=str)
 print(formatted_item)
 except:
 print(f" {item}")
 else:
 print(f" Response Type: {type(data)}")
 print(f" Data: {data}")

 def test_tradestation_auth_status(self):
 """Test TradeStation authentication status first"""
 print("\n🔐 PHASE 1: TradeStation Authentication Status Check")
 print("-" * 60)

 try:
 url = f"{self.api_url}/auth/tradestation/status"
 print(f" Testing URL: {url}")

 response = requests.get(url, timeout=30)
 print(f" Status Code: {response.status_code}")

 if response.status_code == 200:
 auth_data = response.json()
 self.debug_print("TradeStation Authentication Status", auth_data)

 # Extract key authentication info
 authenticated = auth_data.get("authenticated", False)
 has_access_token = auth_data.get("has_access_token", False)
 environment = auth_data.get("environment", "UNKNOWN")

 print("\n AUTHENTICATION ANALYSIS:")
 print(f" Authenticated: {authenticated}")
 print(f" 🔑 Has Access Token: {has_access_token}")
 print(f" 🌍 Environment: {environment}")

 if authenticated and has_access_token:
 print(" AUTHENTICATION STATUS: GOOD - Ready for API calls")
 return True, auth_data
 else:
 print(
 " AUTHENTICATION STATUS: FAILED - Not ready for API calls"
 )
 return False, auth_data

 else:
 print(f" Authentication status check failed: {response.status_code}")
 try:
 error_data = response.json()
 self.debug_print("Authentication Error", error_data, "ERROR")
 except:
 print(f" Error response: {response.text}")
 return False, {}

 except Exception as e:
 print(f" Authentication status check exception: {str(e)}")
 return False, {}

 def test_tradestation_accounts_endpoint(self):
 """Test the main TradeStation accounts endpoint - THE CORE ISSUE"""
 print("\n🏛️ PHASE 2: TradeStation Accounts Endpoint Debug")
 print("-" * 60)

 try:
 url = f"{self.api_url}/tradestation/accounts"
 print(f" Testing URL: {url}")
 print(f" Looking for account: {self.target_account}")

 response = requests.get(url, timeout=30)
 print(f" Status Code: {response.status_code}")

 if response.status_code == 200:
 accounts_data = response.json()
 self.debug_print("TradeStation Accounts Response", accounts_data)

 # Analyze the response structure
 print("\n ACCOUNTS RESPONSE ANALYSIS:")

 # Check if it's a direct list or wrapped in a data field
 if isinstance(accounts_data, list):
 accounts_list = accounts_data
 print(" Response Format: Direct list")
 elif isinstance(accounts_data, dict):
 if "data" in accounts_data:
 accounts_list = accounts_data["data"]
 print(" Response Format: Wrapped in 'data' field")
 elif "accounts" in accounts_data:
 accounts_list = accounts_data["accounts"]
 print(" Response Format: Wrapped in 'accounts' field")
 else:
 # Check if the dict itself contains account info
 if (
 "account_id" in accounts_data
 or "AccountID" in accounts_data
 ):
 accounts_list = [accounts_data]
 print(" Response Format: Single account object")
 else:
 accounts_list = []
 print(" Response Format: Unknown structure")
 print(f" Available keys: {list(accounts_data.keys())}")
 else:
 accounts_list = []
 print(
 f" Response Format: Unexpected type {type(accounts_data)}"
 )

 print(f" Total Accounts Found: {len(accounts_list)}")

 # Analyze each account
 target_account_found = False
 for i, account in enumerate(accounts_list):
 print(f"\n Account {i+1}:")

 if isinstance(account, dict):
 # Look for account ID in various possible field names
 account_id_fields = [
 "account_id",
 "AccountID",
 "account",
 "id",
 "Account",
 ]
 account_id = None

 for field in account_id_fields:
 if field in account:
 account_id = str(account[field])
 print(f" 🆔 Account ID ({field}): {account_id}")
 break

 if not account_id:
 print(
 f" No account ID found in fields: {list(account.keys())}"
 )

 # Check other important fields
 important_fields = [
 "account_type",
 "AccountType",
 "type",
 "status",
 "Status",
 "currency",
 "Currency",
 ]
 for field in important_fields:
 if field in account:
 print(f" {field}: {account[field]}")

 # Check if this is our target account
 if account_id == self.target_account:
 target_account_found = True
 print(
 f" TARGET ACCOUNT FOUND: {self.target_account}"
 )
 self.debug_print(
 f"Target Account {self.target_account} Details", account
 )

 # Show all fields for debugging
 print(f" All fields: {list(account.keys())}")
 else:
 print(
 f" Account {i+1} is not a dictionary: {type(account)}"
 )
 print(f" Value: {account}")

 # Summary of findings
 print("\n ACCOUNTS ENDPOINT ANALYSIS SUMMARY:")
 print(f" Total Accounts: {len(accounts_list)}")
 print(
 f" Target Account ({self.target_account}): {' FOUND' if target_account_found else ' NOT FOUND'}"
 )

 if len(accounts_list) == 0:
 print(
 " 🚨 CRITICAL ISSUE: No accounts returned - This explains Portfolio Management fallback!"
 )
 print(
 " 🔧 DIAGNOSIS: TradeStation API integration issue at account retrieval level"
 )
 elif not target_account_found:
 print(
 f" 🚨 CRITICAL ISSUE: Target account {self.target_account} not found in {len(accounts_list)} accounts"
 )
 print(" 🔧 DIAGNOSIS: Account filtering or ID mismatch issue")
 else:
 print(
 " SUCCESS: Target account found - Portfolio Management should work"
 )

 return True, accounts_data, target_account_found

 else:
 print(f" Accounts endpoint failed: {response.status_code}")
 try:
 error_data = response.json()
 self.debug_print("Accounts Endpoint Error", error_data, "ERROR")
 except:
 print(f" Error response: {response.text}")
 return False, {}, False

 except Exception as e:
 print(f" Accounts endpoint exception: {str(e)}")
 return False, {}, False

 def test_portfolio_management_service_integration(self):
 """Test how Portfolio Management Service accesses accounts"""
 print("\n🔄 PHASE 3: Portfolio Management Service Integration Debug")
 print("-" * 60)

 try:
 # Test the Portfolio Management Service endpoint that should use TradeStation data
 url = f"{self.api_url}/portfolio-management/portfolios"
 print(f" Testing URL: {url}")

 response = requests.get(url, timeout=30)
 print(f" Status Code: {response.status_code}")

 if response.status_code == 200:
 portfolios_data = response.json()
 self.debug_print("Portfolio Management Portfolios", portfolios_data)

 # Look for TradeStation Main portfolio
 portfolios = portfolios_data.get("portfolios", [])
 tradestation_portfolio = None

 for portfolio in portfolios:
 if isinstance(portfolio, dict):
 portfolio_id = portfolio.get("id", "")
 portfolio_name = portfolio.get("name", "")

 if (
 "tradestation" in portfolio_id.lower()
 or "tradestation" in portfolio_name.lower()
 ):
 tradestation_portfolio = portfolio
 print(
 f" Found TradeStation portfolio: {portfolio_name} (ID: {portfolio_id})"
 )
 break

 if tradestation_portfolio:
 # Check the data source
 data_source = tradestation_portfolio.get("data_source", "unknown")
 integration_status = tradestation_portfolio.get(
 "integration_status", "unknown"
 )
 total_value = tradestation_portfolio.get("total_value", 0)
 positions_count = tradestation_portfolio.get("positions_count", 0)

 print("\n TRADESTATION PORTFOLIO ANALYSIS:")
 print(f" Data Source: {data_source}")
 print(f" 🔗 Integration Status: {integration_status}")
 print(f" Total Value: ${total_value:,.2f}")
 print(f" Positions Count: {positions_count}")

 # Check if it's using mock data
 if (
 "mock" in data_source.lower()
 or "fallback" in data_source.lower()
 ):
 print(" 🚨 CRITICAL: Portfolio Management is using MOCK DATA")
 print(
 " 🔧 DIAGNOSIS: TradeStation integration failed, fallback activated"
 )
 return False, portfolios_data
 elif "tradestation" in data_source.lower():
 print(
 " SUCCESS: Portfolio Management using TradeStation data"
 )
 return True, portfolios_data
 else:
 print(f" UNCLEAR: Data source unclear - {data_source}")
 return False, portfolios_data
 else:
 print(
 " No TradeStation portfolio found in Portfolio Management"
 )
 return False, portfolios_data

 else:
 print(
 f" Portfolio Management endpoint failed: {response.status_code}"
 )
 return False, {}

 except Exception as e:
 print(f" Portfolio Management integration test exception: {str(e)}")
 return False, {}

 def test_tradestation_positions_endpoint(self):
 """Test TradeStation positions endpoint for the target account"""
 print("\n PHASE 4: TradeStation Positions Endpoint Debug")
 print("-" * 60)

 try:
 url = (
 f"{self.api_url}/tradestation/accounts/{self.target_account}/positions"
 )
 print(f" Testing URL: {url}")

 response = requests.get(url, timeout=30)
 print(f" Status Code: {response.status_code}")

 if response.status_code == 200:
 positions_data = response.json()
 self.debug_print("TradeStation Positions Response", positions_data)

 # Analyze positions structure
 if isinstance(positions_data, dict):
 if "data" in positions_data:
 positions_list = positions_data["data"]
 print(" Positions Format: Wrapped in 'data' field")
 elif "positions" in positions_data:
 positions_list = positions_data["positions"]
 print(" Positions Format: Wrapped in 'positions' field")
 else:
 positions_list = []
 print(" Positions Format: Unknown structure")
 print(f" Available keys: {list(positions_data.keys())}")
 elif isinstance(positions_data, list):
 positions_list = positions_data
 print(" Positions Format: Direct list")
 else:
 positions_list = []
 print(
 f" Positions Format: Unexpected type {type(positions_data)}"
 )

 print(f" Total Positions: {len(positions_list)}")

 # Analyze first few positions
 if positions_list:
 print("\n Sample Positions Analysis:")
 for i, position in enumerate(positions_list[:3]):
 if isinstance(position, dict):
 symbol = position.get(
 "symbol", position.get("Symbol", "N/A")
 )
 quantity = position.get(
 "quantity", position.get("Quantity", 0)
 )
 market_value = position.get(
 "market_value", position.get("MarketValue", 0)
 )

 print(f" Position {i+1}: {symbol}")
 print(f" - Quantity: {quantity}")
 print(f" - Market Value: ${market_value:,.2f}")
 print(f" - Fields: {list(position.keys())}")

 return True, positions_data

 else:
 print(f" Positions endpoint failed: {response.status_code}")
 try:
 error_data = response.json()
 self.debug_print("Positions Endpoint Error", error_data, "ERROR")
 except:
 print(f" Error response: {response.text}")
 return False, {}

 except Exception as e:
 print(f" Positions endpoint exception: {str(e)}")
 return False, {}

 def run_comprehensive_debug(self):
 """Run comprehensive debugging of TradeStation accounts integration"""
 print("🚨 TRADESTATION ACCOUNTS ENDPOINT COMPREHENSIVE DEBUG")
 print("=" * 80)
 print(
 " OBJECTIVE: Debug why Portfolio Management Service can't access accounts"
 )
 print(" FOCUS AREAS:")
 print(" 1. TradeStation authentication status")
 print(" 2. TradeStation accounts endpoint response structure")
 print(" 3. Account 11775499 presence and format")
 print(" 4. Portfolio Management Service integration")
 print(" 5. Data flow from TradeStation to Portfolio Management")

 # Phase 1: Authentication Status
 auth_success, auth_data = self.test_tradestation_auth_status()

 # Phase 2: Accounts Endpoint
 accounts_success, accounts_data, target_found = (
 self.test_tradestation_accounts_endpoint()
 )

 # Phase 3: Portfolio Management Integration
 pm_success, pm_data = self.test_portfolio_management_service_integration()

 # Phase 4: Positions Endpoint (if account found)
 positions_success = False
 if target_found:
 positions_success, positions_data = (
 self.test_tradestation_positions_endpoint()
 )

 # Final Analysis
 print("\n COMPREHENSIVE DEBUG ANALYSIS")
 print("=" * 80)

 print("\n TEST RESULTS SUMMARY:")
 print(
 f" 🔐 Authentication Status: {' PASS' if auth_success else ' FAIL'}"
 )
 print(f" 🏛️ Accounts Endpoint: {' PASS' if accounts_success else ' FAIL'}")
 print(f" Target Account Found: {' YES' if target_found else ' NO'}")
 print(
 f" 🔄 Portfolio Management: {' USING TRADESTATION' if pm_success else ' USING MOCK DATA'}"
 )
 print(
 f" Positions Accessible: {' YES' if positions_success else ' NO'}"
 )

 # Root Cause Analysis
 print("\n ROOT CAUSE ANALYSIS:")

 if not auth_success:
 print(" 🚨 PRIMARY ISSUE: TradeStation authentication failed")
 print(" 🔧 SOLUTION: Fix TradeStation OAuth authentication")
 elif not accounts_success:
 print(" 🚨 PRIMARY ISSUE: TradeStation accounts endpoint failed")
 print(" 🔧 SOLUTION: Fix TradeStation accounts API integration")
 elif not target_found:
 print(
 f" 🚨 PRIMARY ISSUE: Target account {self.target_account} not found in accounts response"
 )
 print(" 🔧 SOLUTION: Verify account ID format and API response structure")
 elif not pm_success:
 print(
 " 🚨 PRIMARY ISSUE: Portfolio Management Service not using TradeStation data"
 )
 print(
 " 🔧 SOLUTION: Fix Portfolio Management Service integration with TradeStation accounts"
 )
 else:
 print(" SUCCESS: All components working correctly")

 # Specific Recommendations
 print("\n🔧 SPECIFIC RECOMMENDATIONS:")

 if auth_success and accounts_success and not target_found:
 print(" 1. Check TradeStation API account filtering")
 print(
 f" 2. Verify account {self.target_account} is accessible with current credentials"
 )
 print(" 3. Check account status (active/inactive)")
 print(" 4. Verify account permissions in TradeStation API")

 if auth_success and not accounts_success:
 print(" 1. Check TradeStation accounts API endpoint implementation")
 print(" 2. Verify API credentials have account access permissions")
 print(" 3. Check TradeStation API rate limits")
 print(" 4. Verify network connectivity to TradeStation API")

 if target_found and not pm_success:
 print(" 1. Check Portfolio Management Service account data parsing")
 print(" 2. Verify Portfolio Management Service TradeStation integration")
 print(" 3. Check error handling in Portfolio Management Service")
 print(
 " 4. Verify data format compatibility between TradeStation and Portfolio Management"
 )

 # Expected vs Actual
 print("\n EXPECTED VS ACTUAL:")
 print(
 f" EXPECTED: TradeStation accounts endpoint returns account {self.target_account}"
 )
 print(f" ACTUAL: {'Account found' if target_found else 'Account NOT found'}")
 print(" ")
 print(" EXPECTED: Portfolio Management Service uses TradeStation data")
 print(
 f" ACTUAL: {'Using TradeStation data' if pm_success else 'Using MOCK data (fallback)'}"
 )
 print(" ")
 print(" EXPECTED: User sees real portfolio positions")
 print(
 f" ACTUAL: {'Real positions' if pm_success else 'FAKE positions (mock data)'}"
 )

 # User Impact
 print("\n👤 USER IMPACT:")
 if not pm_success:
 print(
 " 🚨 CRITICAL: User sees FAKE portfolio data instead of real TradeStation positions"
 )
 print(
 " Portfolio value shown: Mock data (~$790K) instead of real data (~$969K)"
 )
 print(
 " Positions shown: Fake symbols (AMZN, QQQ, GOOGL) instead of real (CRM, TSLA, AAPL, NVO)"
 )
 print(
 " 🔧 User complaint: 100% VALID - they are not seeing their real portfolio"
 )
 else:
 print(" SUCCESS: User should see real TradeStation portfolio data")

 # Next Steps
 print("\n IMMEDIATE NEXT STEPS:")
 if not target_found:
 print(
 f" 1. INVESTIGATE: Why account {self.target_account} is not in TradeStation accounts response"
 )
 print(
 " 2. 🔧 FIX: TradeStation accounts API integration to return all user accounts"
 )
 print(
 f" 3. VERIFY: Account {self.target_account} appears in accounts list"
 )
 print(
 " 4. 🔄 TEST: Portfolio Management Service picks up real account data"
 )
 elif not pm_success:
 print(
 " 1. INVESTIGATE: Why Portfolio Management Service ignores TradeStation account data"
 )
 print(
 " 2. 🔧 FIX: Portfolio Management Service integration with TradeStation accounts"
 )
 print(
 " 3. VERIFY: Portfolio Management Service uses real TradeStation data"
 )
 print(" 4. 👤 CONFIRM: User sees real portfolio positions")

 return {
 "auth_success": auth_success,
 "accounts_success": accounts_success,
 "target_found": target_found,
 "pm_success": pm_success,
 "positions_success": positions_success,
 "overall_success": auth_success
 and accounts_success
 and target_found
 and pm_success,
 }

if __name__ == "__main__":
 print("🚨 TradeStation Accounts Endpoint Debug Test")
 print("=" * 60)
 print(" Debugging why Portfolio Management Service falls back to mock data")
 print(" Focus: Account 11775499 accessibility and data structure")

 debugger = TradeStationAccountsDebugger()
 results = debugger.run_comprehensive_debug()

 # Exit with appropriate code
 if results["overall_success"]:
 print("\n DEBUG COMPLETE: All systems working correctly")
 sys.exit(0)
 else:
 print("\n DEBUG COMPLETE: Issues found that need immediate attention")
 sys.exit(1)
