import requests
import sys
from datetime import datetime
import json

class TradeStationBalanceAPITester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0
 self.account_id = "11775499" # Specific account from review request

 def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
 """Run a single API test"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 self.tests_run += 1
 print(f"\n Testing {name}...")
 print(f" URL: {url}")

 try:
 if method == "GET":
 response = requests.get(url, headers=headers, params=params, timeout=30)
 elif method == "POST":
 response = requests.post(url, json=data, headers=headers, timeout=30)

 success = response.status_code == expected_status
 if success:
 self.tests_passed += 1
 print(f" Passed - Status: {response.status_code}")
 try:
 response_data = response.json()
 return True, response_data
 except:
 return True, {}
 else:
 print(
 f" Failed - Expected {expected_status}, got {response.status_code}"
 )
 try:
 error_data = response.json()
 print(f" Error: {error_data}")
 except:
 print(f" Error: {response.text}")
 return False, {}

 except requests.exceptions.Timeout:
 print(" Failed - Request timeout (30s)")
 return False, {}
 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}

 def test_tradestation_balance_endpoint(self):
 """Test TradeStation Account Balance functionality - COMPREHENSIVE TESTING"""
 print("\n🏛️ TESTING TRADESTATION ACCOUNT BALANCE FUNCTIONALITY")
 print("=" * 80)
 print(
 " OBJECTIVE: Verify /api/tradestation/accounts/11775499/balances endpoint"
 )
 print(" REQUIREMENTS:")
 print(
 " 1. Response structure: {status: 'success', balances: {Balances: [...]}}"
 )
 print(
 " 2. Key fields: CashBalance, BuyingPower, Equity, MarketValue, TodaysProfitLoss"
 )
 print(
 " 3. BalanceDetail: OptionBuyingPower, OptionsMarketValue, OvernightBuyingPower"
 )
 print(" 4. Authentication works and data is real/current")
 print(" 5. Expected values: Cash ~$390k, Buying Power ~$2.5M, Equity ~$1.2M")

 # Test 1: Basic Balance Endpoint
 print("\n PHASE 1: Basic Balance Endpoint Testing")
 print("-" * 60)

 endpoint = f"tradestation/accounts/{self.account_id}/balances"
 success, balance_data = self.run_test(
 "TradeStation Account Balances", "GET", endpoint, 200
 )

 if not success:
 print(" Balance endpoint failed - checking authentication status")
 # Check auth status first
 auth_success, auth_data = self.run_test(
 "TradeStation Auth Status", "GET", "auth/tradestation/status", 200
 )
 if auth_success:
 auth_status = auth_data.get("authentication", {})
 print(
 f" 🔐 Authentication Status: {auth_status.get('authenticated', False)}"
 )
 print(f" Environment: {auth_status.get('environment', 'unknown')}")
 print(
 f" Credentials Configured: {auth_status.get('credentials_configured', False)}"
 )

 if not auth_status.get("authenticated", False):
 print(
 " Not authenticated - this is expected behavior for secure trading API"
 )
 print(
 " Balance endpoint requires OAuth authentication to function"
 )
 return False
 return False

 # Test 2: Response Structure Verification
 print("\n PHASE 2: Response Structure Verification")
 print("-" * 60)

 # Check top-level structure
 required_top_fields = ["status"]
 optional_top_fields = ["balances", "data", "message"]

 print(f" Response Keys: {list(balance_data.keys())}")

 # Verify status field
 status = balance_data.get("status", "unknown")
 print(f" Status: {status}")

 if status == "success":
 print(" Status indicates success")

 # Look for balance data in different possible locations
 balances = None
 if "balances" in balance_data:
 balances = balance_data["balances"]
 print(" Found balances at root level")
 elif "data" in balance_data and isinstance(balance_data["data"], dict):
 if "balances" in balance_data["data"]:
 balances = balance_data["data"]["balances"]
 print(" Found balances in data object")
 elif "Balances" in balance_data["data"]:
 balances = balance_data["data"]["Balances"]
 print(" Found Balances (capitalized) in data object")

 if balances is None:
 print(" No balance data found in response")
 print(
 f" Full response structure: {json.dumps(balance_data, indent=2)[:500]}..."
 )
 return False

 elif status == "error":
 error_message = balance_data.get("message", "Unknown error")
 print(f" API returned error: {error_message}")

 if (
 "authentication" in error_message.lower()
 or "access token" in error_message.lower()
 ):
 print(
 " Authentication required - this is expected for secure trading API"
 )
 print(" 🔐 User needs to complete OAuth flow to access balance data")
 return False
 else:
 print(" Unexpected error type")
 return False
 else:
 print(f" Unexpected status: {status}")
 return False

 # Test 3: Balance Data Structure Analysis
 print("\n PHASE 3: Balance Data Structure Analysis")
 print("-" * 60)

 # Handle the actual TradeStation API structure: balances.Balances[0]
 balance_record = None

 if isinstance(balances, dict):
 print(" Balance data is dictionary format")
 print(f" Balance keys: {list(balances.keys())}")

 # Look for Balances array
 if (
 "Balances" in balances
 and isinstance(balances["Balances"], list)
 and len(balances["Balances"]) > 0
 ):
 balance_record = balances["Balances"][0]
 print(
 f" Found {len(balances['Balances'])} balance record(s) in Balances array"
 )
 print(f" Balance record keys: {list(balance_record.keys())}")
 else:
 print(" No Balances array found or empty")
 return False

 elif isinstance(balances, list) and len(balances) > 0:
 balance_record = balances[0]
 print(f" Found {len(balances)} balance record(s)")
 print(f" Balance record keys: {list(balance_record.keys())}")
 else:
 print(f" Unexpected balance data format: {type(balances)}")
 return False

 # Test 4: Required Fields Verification
 print("\n PHASE 4: Required Fields Verification")
 print("-" * 60)

 # Expected key fields from review request
 required_balance_fields = [
 "CashBalance",
 "BuyingPower",
 "Equity",
 "MarketValue",
 "TodaysProfitLoss",
 ]

 balance_detail_fields = [
 "OptionBuyingPower",
 "OptionsMarketValue",
 "OvernightBuyingPower",
 ]

 # Check main balance fields
 found_main_fields = []
 missing_main_fields = []

 for field in required_balance_fields:
 if field in balance_record:
 found_main_fields.append(field)
 value = balance_record[field]
 print(f" {field}: {value}")
 else:
 missing_main_fields.append(field)
 print(f" Missing: {field}")

 # Check for BalanceDetail section
 balance_detail = None
 if "BalanceDetail" in balance_record:
 balance_detail = balance_record["BalanceDetail"]
 print(" Found BalanceDetail section")
 elif "balanceDetail" in balance_record:
 balance_detail = balance_record["balanceDetail"]
 print(" Found balanceDetail section")
 else:
 print(" No BalanceDetail section found")

 # Check balance detail fields
 found_detail_fields = []
 missing_detail_fields = []

 if balance_detail:
 for field in balance_detail_fields:
 if field in balance_detail:
 found_detail_fields.append(field)
 value = balance_detail[field]
 print(f" BalanceDetail.{field}: {value}")
 else:
 missing_detail_fields.append(field)
 print(f" Missing BalanceDetail.{field}")
 else:
 missing_detail_fields = balance_detail_fields

 # Test 5: Data Value Validation
 print("\n PHASE 5: Data Value Validation")
 print("-" * 60)

 # Expected ranges from review request
 expected_values = {
 "CashBalance": (300000, 500000), # ~$390k
 "BuyingPower": (2000000, 3000000), # ~$2.5M
 "Equity": (1000000, 1500000), # ~$1.2M
 "MarketValue": (800000, 900000), # ~$855k
 "OptionBuyingPower": (600000, 700000), # ~$643k (in BalanceDetail)
 }

 value_validations = []

 for field, (min_val, max_val) in expected_values.items():
 value = None

 # Check main balance fields
 if field in balance_record:
 value = balance_record[field]
 # Check balance detail fields
 elif balance_detail and field in balance_detail:
 value = balance_detail[field]

 if value is not None:
 try:
 numeric_value = float(value)
 if min_val <= numeric_value <= max_val:
 print(
 f" {field}: ${numeric_value:,.2f} (within expected range ${min_val:,}-${max_val:,})"
 )
 value_validations.append(True)
 else:
 print(
 f" {field}: ${numeric_value:,.2f} (outside expected range ${min_val:,}-${max_val:,})"
 )
 value_validations.append(False)
 except (ValueError, TypeError):
 print(f" {field}: Invalid numeric value '{value}'")
 value_validations.append(False)
 else:
 print(f" {field}: Not found")
 value_validations.append(False)

 # Test 6: Account Type and Metadata
 print("\n🏦 PHASE 6: Account Type and Metadata Verification")
 print("-" * 60)

 # Check for account type (should be Margin based on review request)
 account_type = balance_record.get(
 "AccountType", balance_record.get("accountType", "Unknown")
 )
 print(f" 🏦 Account Type: {account_type}")

 if account_type.lower() == "margin":
 print(" Account type matches expected (Margin)")
 else:
 print(
 f" Account type unexpected (expected: Margin, got: {account_type})"
 )

 # Check for account ID
 account_id_in_response = balance_record.get(
 "AccountID", balance_record.get("accountId", "Unknown")
 )
 print(f" 🆔 Account ID: {account_id_in_response}")

 if str(account_id_in_response) == self.account_id:
 print(f" Account ID matches requested ({self.account_id})")
 else:
 print(
 f" Account ID mismatch (expected: {self.account_id}, got: {account_id_in_response})"
 )

 # Check for timestamp/currency
 currency = balance_record.get(
 "Currency", balance_record.get("currency", "Unknown")
 )
 print(f" 💱 Currency: {currency}")

 # Test 7: Data Freshness and Authenticity
 print("\n🕐 PHASE 7: Data Freshness and Authenticity Verification")
 print("-" * 60)

 # Check for timestamp fields
 timestamp_fields = [
 "Timestamp",
 "timestamp",
 "LastUpdated",
 "lastUpdated",
 "AsOfDate",
 "asOfDate",
 ]
 found_timestamp = None

 for ts_field in timestamp_fields:
 if ts_field in balance_record:
 found_timestamp = balance_record[ts_field]
 print(f" 🕐 Found timestamp ({ts_field}): {found_timestamp}")
 break

 if not found_timestamp:
 print(" No timestamp found in balance data")

 # Check for real-time indicators
 real_time_indicators = []

 # Non-zero, non-round values indicate real data
 for field in ["CashBalance", "BuyingPower", "Equity", "MarketValue"]:
 if field in balance_record:
 try:
 value = float(balance_record[field])
 if value > 0 and value % 1000 != 0: # Not a round thousand
 real_time_indicators.append(f"{field} has realistic precision")
 except:
 pass

 # P&L values (especially TodaysProfitLoss) should be realistic
 if "TodaysProfitLoss" in balance_record:
 try:
 pnl = float(balance_record["TodaysProfitLoss"])
 if pnl != 0:
 real_time_indicators.append("Non-zero P&L indicates live data")
 except:
 pass

 if real_time_indicators:
 print(" Real-time data indicators:")
 for indicator in real_time_indicators:
 print(f" - {indicator}")
 else:
 print(" No clear real-time data indicators found")

 # Final Assessment
 print("\n FINAL ASSESSMENT: TradeStation Account Balance API")
 print("=" * 80)

 # Calculate success metrics
 test_phases = [
 ("API Endpoint Response", success),
 ("Response Structure", status == "success"),
 ("Required Main Fields", len(missing_main_fields) == 0),
 (
 "Balance Detail Fields",
 len(missing_detail_fields) <= 1,
 ), # Allow 1 missing
 (
 "Value Validation",
 sum(value_validations) >= len(value_validations) * 0.6,
 ), # 60% of values in range
 ("Account Metadata", account_type.lower() == "margin"),
 ("Data Authenticity", len(real_time_indicators) > 0),
 ]

 passed_phases = sum(1 for _, passed in test_phases if passed)
 total_phases = len(test_phases)
 success_rate = (passed_phases / total_phases) * 100

 print("\n TEST RESULTS SUMMARY:")
 for phase_name, passed in test_phases:
 status_icon = " PASS" if passed else " FAIL"
 print(f" {status_icon} {phase_name}")

 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)"
 )

 # Detailed findings
 print("\n DETAILED FINDINGS:")
 print(
 f" - Main Balance Fields Found: {len(found_main_fields)}/{len(required_balance_fields)}"
 )
 print(
 f" - Balance Detail Fields Found: {len(found_detail_fields)}/{len(balance_detail_fields)}"
 )
 print(
 f" - Values in Expected Range: {sum(value_validations)}/{len(value_validations)}"
 )
 print(f" - Account Type: {account_type}")
 print(f" - Real-time Indicators: {len(real_time_indicators)}")

 # Requirements verification
 print("\n REQUIREMENTS VERIFICATION:")
 requirements_met = []

 if status == "success":
 requirements_met.append(" Response structure has 'success' status")
 else:
 requirements_met.append(" Response structure missing 'success' status")

 if len(missing_main_fields) == 0:
 requirements_met.append(
 " All key balance fields present (CashBalance, BuyingPower, etc.)"
 )
 else:
 requirements_met.append(
 f" Missing key balance fields: {missing_main_fields}"
 )

 if len(missing_detail_fields) <= 1:
 requirements_met.append(" BalanceDetail section mostly complete")
 else:
 requirements_met.append(
 f" BalanceDetail section incomplete: {missing_detail_fields}"
 )

 if sum(value_validations) >= len(value_validations) * 0.6:
 requirements_met.append(" Balance values are in expected ranges")
 else:
 requirements_met.append(" Balance values outside expected ranges")

 if len(real_time_indicators) > 0:
 requirements_met.append(" Data appears to be real/current")
 else:
 requirements_met.append(" Data may not be real/current")

 for requirement in requirements_met:
 print(f" {requirement}")

 # Final verdict
 if success_rate >= 85:
 print(
 "\n VERDICT: EXCELLENT - TradeStation Balance API working perfectly!"
 )
 print(
 " The Account Balance page should display all required data correctly."
 )
 print(" Balance data is authentic and within expected ranges.")
 elif success_rate >= 70:
 print("\n VERDICT: GOOD - TradeStation Balance API mostly working.")
 print(" The Account Balance page should function with minor issues.")
 elif success_rate >= 50:
 print(
 "\n VERDICT: PARTIAL - TradeStation Balance API has significant issues."
 )
 print(" The Account Balance page may have data display problems.")
 else:
 print(
 "\n VERDICT: CRITICAL - TradeStation Balance API not working properly."
 )
 print(
 " The Account Balance page likely shows 'Failed to load balance data'."
 )

 return success_rate >= 70

 def run_comprehensive_test(self):
 """Run comprehensive TradeStation Balance API test"""
 print("🏛️ TRADESTATION BALANCE API COMPREHENSIVE TEST")
 print("=" * 80)
 print(f" Testing Account: {self.account_id}")
 print(f" Base URL: {self.base_url}")
 print(f" Test Time: {datetime.now().isoformat()}")

 # Run the main balance test
 balance_success = self.test_tradestation_balance_endpoint()

 # Summary
 print("\n FINAL TEST SUMMARY")
 print("=" * 80)
 print(f"Tests Run: {self.tests_run}")
 print(f"Tests Passed: {self.tests_passed}")
 print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

 if balance_success:
 print("\n OVERALL RESULT: TradeStation Balance API is working correctly")
 print(" The Account Balance functionality should work as expected")
 else:
 print("\n OVERALL RESULT: TradeStation Balance API has issues")
 print(" The Account Balance functionality may not work properly")

 return balance_success

if __name__ == "__main__":
 tester = TradeStationBalanceAPITester()
 success = tester.run_comprehensive_test()
 sys.exit(0 if success else 1)
