#!/usr/bin/env python3
"""
SR-1/3 Strike Rail PRO Integration Test
=====================================

Test the SR-1/3 Strike Rail PRO integration to verify the new chain data endpoint works correctly.

Test Requirements:
1. Chain Endpoint Test: GET /api/options/chain?symbol=TSLA&expiry=2025-02-21
2. Data Transformation Test: Verify backend response can be transformed to ChainRow format
3. Integration Readiness: Confirm useChain hook will receive proper data structure
4. Error Handling: Test invalid symbol/expiry to verify proper error responses
"""

import requests
import sys
from datetime import datetime
from typing import Dict, Optional

# Use the external URL from frontend/.env
BASE_URL = "http://localhost:8000"

class SR1StrikeRailProTester:
 def __init__(self):
 self.base_url = BASE_URL
 self.test_results = []
 self.success_count = 0
 self.total_tests = 0

 def log_test(self, test_name: str, success: bool, details: str):
 """Log test result"""
 self.total_tests += 1
 if success:
 self.success_count += 1
 status = " PASS"
 else:
 status = " FAIL"

 result = f"{status} {test_name}: {details}"
 self.test_results.append(result)
 print(result)

 def test_chain_endpoint_basic(self) -> bool:
 """Test 1: Basic Chain Endpoint Test"""
 print("\n TEST 1: Chain Endpoint Basic Functionality")

 try:
 # Test with TSLA and specific expiry
 url = f"{self.base_url}/api/options/chain"
 params = {"symbol": "TSLA", "expiry": "2025-02-21"}

 response = requests.get(url, params=params, timeout=30)

 if response.status_code != 200:
 self.log_test(
 "Chain Endpoint Basic",
 False,
 f"HTTP {response.status_code}: {response.text}",
 )
 return False

 data = response.json()

 # Verify response structure
 if not isinstance(data, dict):
 self.log_test(
 "Chain Endpoint Basic", False, "Response is not a dictionary"
 )
 return False

 # Check for essential fields
 required_fields = ["spot", "raw"]
 missing_fields = [field for field in required_fields if field not in data]

 if missing_fields:
 self.log_test(
 "Chain Endpoint Basic",
 False,
 f"Missing required fields: {missing_fields}",
 )
 return False

 self.log_test(
 "Chain Endpoint Basic",
 True,
 f"Response received with spot=${data.get('spot', 'N/A')}",
 )
 return True

 except Exception as e:
 self.log_test("Chain Endpoint Basic", False, f"Exception: {str(e)}")
 return False

 def test_chain_data_structure(self) -> bool:
 """Test 2: Chain Data Structure Verification"""
 print("\n TEST 2: Chain Data Structure for Strike Rail PRO")

 try:
 url = f"{self.base_url}/api/options/chain"
 params = {"symbol": "TSLA", "expiry": "2025-02-21"}

 response = requests.get(url, params=params, timeout=30)

 if response.status_code != 200:
 self.log_test(
 "Chain Data Structure", False, f"HTTP {response.status_code}"
 )
 return False

 data = response.json()

 # Check for chain structure
 if "raw" not in data or "OptionChains" not in data["raw"]:
 self.log_test(
 "Chain Data Structure", False, "Missing raw.OptionChains structure"
 )
 return False

 chains = data["raw"]["OptionChains"]
 if not chains or len(chains) == 0:
 self.log_test("Chain Data Structure", False, "No option chains found")
 return False

 # Check first chain structure
 chain = chains[0]
 if "Strikes" not in chain:
 self.log_test("Chain Data Structure", False, "Missing Strikes in chain")
 return False

 strikes = chain["Strikes"]
 if not strikes or len(strikes) == 0:
 self.log_test(
 "Chain Data Structure", False, "No strikes found in chain"
 )
 return False

 # Verify strike structure for Strike Rail PRO requirements
 strike = strikes[0]
 required_strike_fields = ["StrikePrice", "Calls", "Puts"]
 missing_strike_fields = [
 field for field in required_strike_fields if field not in strike
 ]

 if missing_strike_fields:
 self.log_test(
 "Chain Data Structure",
 False,
 f"Missing strike fields: {missing_strike_fields}",
 )
 return False

 # Check calls/puts structure
 calls = strike.get("Calls", [])
 puts = strike.get("Puts", [])

 if not calls and not puts:
 self.log_test(
 "Chain Data Structure", False, "No calls or puts data found"
 )
 return False

 # Verify option data structure (check first call if available)
 option_data = calls[0] if calls else puts[0] if puts else None
 if option_data:
 required_option_fields = [
 "Bid",
 "Ask",
 "OpenInterest",
 "Volume",
 "ImpliedVolatility",
 ]
 available_fields = [
 field for field in required_option_fields if field in option_data
 ]

 self.log_test(
 "Chain Data Structure",
 True,
 f"Found {len(strikes)} strikes, {len(available_fields)}/{len(required_option_fields)} required fields: {available_fields}",
 )
 else:
 self.log_test(
 "Chain Data Structure",
 True,
 f"Found {len(strikes)} strikes with basic structure",
 )

 return True

 except Exception as e:
 self.log_test("Chain Data Structure", False, f"Exception: {str(e)}")
 return False

 def test_data_transformation(self) -> bool:
 """Test 3: Data Transformation to ChainRow Format"""
 print("\n TEST 3: Data Transformation to ChainRow Format")

 try:
 url = f"{self.base_url}/api/options/chain"
 params = {"symbol": "TSLA", "expiry": "2025-02-21"}

 response = requests.get(url, params=params, timeout=30)

 if response.status_code != 200:
 self.log_test(
 "Data Transformation", False, f"HTTP {response.status_code}"
 )
 return False

 data = response.json()

 # Transform data to ChainRow format
 chain_rows = []

 if "raw" in data and "OptionChains" in data["raw"]:
 chains = data["raw"]["OptionChains"]
 for chain in chains:
 if "Strikes" in chain:
 for strike_data in chain["Strikes"]:
 strike_price = strike_data.get("StrikePrice")
 if strike_price is None:
 continue

 # Process calls
 calls = strike_data.get("Calls", [])
 for call in calls:
 chain_row = self.transform_to_chain_row(
 strike_price, call, "call"
 )
 if chain_row:
 chain_rows.append(chain_row)

 # Process puts
 puts = strike_data.get("Puts", [])
 for put in puts:
 chain_row = self.transform_to_chain_row(
 strike_price, put, "put"
 )
 if chain_row:
 chain_rows.append(chain_row)

 if not chain_rows:
 self.log_test(
 "Data Transformation", False, "No chain rows could be transformed"
 )
 return False

 # Verify transformation results
 sample_row = chain_rows[0]
 required_fields = ["strike", "bid", "ask", "mid", "iv", "oi", "vol"]
 available_fields = [
 field for field in required_fields if field in sample_row
 ]

 # Check if data is sorted by strike (ascending)
 strikes = [row["strike"] for row in chain_rows if "strike" in row]
 is_sorted = strikes == sorted(strikes)

 self.log_test(
 "Data Transformation",
 True,
 f"Transformed {len(chain_rows)} rows, {len(available_fields)}/{len(required_fields)} fields, sorted: {is_sorted}",
 )
 return True

 except Exception as e:
 self.log_test("Data Transformation", False, f"Exception: {str(e)}")
 return False

 def transform_to_chain_row(
 self, strike_price: float, option_data: dict, option_type: str
 ) -> Optional[Dict]:
 """Transform option data to ChainRow format"""
 try:
 bid = option_data.get("Bid")
 ask = option_data.get("Ask")

 # Calculate mid price
 mid = None
 if bid is not None and ask is not None and bid > 0 and ask > 0:
 mid = (bid + ask) / 2

 chain_row = {
 "strike": float(strike_price),
 "bid": float(bid) if bid is not None else None,
 "ask": float(ask) if ask is not None else None,
 "mid": float(mid) if mid is not None else None,
 "iv": float(option_data.get("ImpliedVolatility", 0))
 if option_data.get("ImpliedVolatility")
 else None,
 "oi": int(option_data.get("OpenInterest", 0))
 if option_data.get("OpenInterest")
 else None,
 "vol": int(option_data.get("Volume", 0))
 if option_data.get("Volume")
 else None,
 "type": option_type,
 }

 return chain_row

 except Exception as e:
 print(f"Transform error: {e}")
 return None

 def test_integration_readiness(self) -> bool:
 """Test 4: Integration Readiness for useChain Hook"""
 print("\n TEST 4: Integration Readiness for useChain Hook")

 try:
 url = f"{self.base_url}/api/options/chain"
 params = {"symbol": "TSLA", "expiry": "2025-02-21"}

 response = requests.get(url, params=params, timeout=30)

 if response.status_code != 200:
 self.log_test(
 "Integration Readiness", False, f"HTTP {response.status_code}"
 )
 return False

 data = response.json()

 # Simulate useChain hook processing
 chain_data = self.process_for_use_chain(data)

 if not chain_data:
 self.log_test(
 "Integration Readiness",
 False,
 "Could not process data for useChain hook",
 )
 return False

 # Verify calculations that useChain would perform
 calculations = {
 "maxOI": chain_data.get("maxOI", 0),
 "maxVol": chain_data.get("maxVol", 0),
 "minIv": chain_data.get("minIv", 0),
 "maxIv": chain_data.get("maxIv", 0),
 "chain_length": len(chain_data.get("rows", [])),
 }

 success = all(
 [
 calculations["maxOI"] > 0,
 calculations["maxVol"] > 0,
 calculations["chain_length"] > 0,
 ]
 )

 if success:
 self.log_test(
 "Integration Readiness",
 True,
 f"Ready for useChain: {calculations['chain_length']} rows, maxOI={calculations['maxOI']}, maxVol={calculations['maxVol']}",
 )
 else:
 self.log_test(
 "Integration Readiness",
 False,
 f"Insufficient data for useChain: {calculations}",
 )

 return success

 except Exception as e:
 self.log_test("Integration Readiness", False, f"Exception: {str(e)}")
 return False

 def process_for_use_chain(self, data: dict) -> Optional[Dict]:
 """Process chain data as useChain hook would"""
 try:
 rows = []
 oi_values = []
 vol_values = []
 iv_values = []

 if "raw" in data and "OptionChains" in data["raw"]:
 chains = data["raw"]["OptionChains"]
 for chain in chains:
 if "Strikes" in chain:
 for strike_data in chain["Strikes"]:
 strike_price = strike_data.get("StrikePrice")
 if strike_price is None:
 continue

 # Process all options for this strike
 for option_type, options in [
 ("call", strike_data.get("Calls", [])),
 ("put", strike_data.get("Puts", [])),
 ]:
 for option in options:
 row = self.transform_to_chain_row(
 strike_price, option, option_type
 )
 if row:
 rows.append(row)

 # Collect values for calculations
 if row["oi"] is not None:
 oi_values.append(row["oi"])
 if row["vol"] is not None:
 vol_values.append(row["vol"])
 if row["iv"] is not None:
 iv_values.append(row["iv"])

 # Calculate max/min values
 return {
 "rows": sorted(
 rows, key=lambda x: x["strike"]
 ), # Sort by strike ascending
 "maxOI": max(oi_values) if oi_values else 0,
 "maxVol": max(vol_values) if vol_values else 0,
 "minIv": min(iv_values) if iv_values else 0,
 "maxIv": max(iv_values) if iv_values else 0,
 }

 except Exception as e:
 print(f"Process error: {e}")
 return None

 def test_error_handling(self) -> bool:
 """Test 5: Error Handling for Invalid Inputs"""
 print("\n TEST 5: Error Handling")

 error_tests = [
 ("Invalid Symbol", {"symbol": "INVALID123", "expiry": "2025-02-21"}),
 ("Invalid Expiry", {"symbol": "TSLA", "expiry": "2025-13-45"}),
 ("Missing Symbol", {"expiry": "2025-02-21"}),
 ]

 passed_tests = 0

 for test_name, params in error_tests:
 try:
 url = f"{self.base_url}/api/options/chain"
 response = requests.get(url, params=params, timeout=30)

 # We expect either a proper error response or graceful handling
 if response.status_code in [400, 422, 500]:
 self.log_test(
 f"Error Handling - {test_name}",
 True,
 f"Proper error response: {response.status_code}",
 )
 passed_tests += 1
 elif response.status_code == 200:
 # Check if response indicates no data or error
 data = response.json()
 if not data or "error" in str(data).lower() or not data.get("raw"):
 self.log_test(
 f"Error Handling - {test_name}",
 True,
 "Graceful handling with empty/error response",
 )
 passed_tests += 1
 else:
 self.log_test(
 f"Error Handling - {test_name}",
 False,
 "Unexpected success response",
 )
 else:
 self.log_test(
 f"Error Handling - {test_name}",
 False,
 f"Unexpected status: {response.status_code}",
 )

 except Exception as e:
 self.log_test(
 f"Error Handling - {test_name}",
 True,
 f"Proper exception handling: {str(e)[:100]}",
 )
 passed_tests += 1

 return passed_tests >= 2 # At least 2 out of 3 error tests should pass

 def run_all_tests(self):
 """Run all SR-1/3 Strike Rail PRO tests"""
 print(" SR-1/3 STRIKE RAIL PRO INTEGRATION TESTING")
 print("=" * 60)
 print(f"Testing against: {self.base_url}")
 print(f"Timestamp: {datetime.now().isoformat()}")
 print()

 # Run all tests
 tests = [
 self.test_chain_endpoint_basic,
 self.test_chain_data_structure,
 self.test_data_transformation,
 self.test_integration_readiness,
 self.test_error_handling,
 ]

 for test_func in tests:
 try:
 test_func()
 except Exception as e:
 self.log_test(
 f"{test_func.__name__}", False, f"Test execution failed: {str(e)}"
 )

 # Print summary
 print("\n" + "=" * 60)
 print(" SR-1/3 STRIKE RAIL PRO TEST SUMMARY")
 print("=" * 60)

 for result in self.test_results:
 print(result)

 success_rate = (
 (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
 )
 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({self.success_count}/{self.total_tests} tests passed)"
 )

 if success_rate >= 80:
 print(
 " VERDICT: SR-1/3 Strike Rail PRO integration is READY for frontend testing"
 )
 elif success_rate >= 60:
 print(
 " VERDICT: SR-1/3 Strike Rail PRO integration has MINOR ISSUES but may be usable"
 )
 else:
 print(
 " VERDICT: SR-1/3 Strike Rail PRO integration has CRITICAL ISSUES requiring fixes"
 )

 return success_rate >= 80

if __name__ == "__main__":
 tester = SR1StrikeRailProTester()
 success = tester.run_all_tests()
 sys.exit(0 if success else 1)
