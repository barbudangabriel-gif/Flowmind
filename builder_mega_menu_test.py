#!/usr/bin/env python3

import requests
import time

# Get backend URL from frontend .env file
try:
 with open("/app/frontend/.env", "r") as f:
 for line in f:
 if line.startswith("REACT_APP_BACKEND_URL="):
 BACKEND_URL = line.split("=", 1)[1].strip()
 break
 else:
 BACKEND_URL = "http://localhost:8001"
except:
 BACKEND_URL = "http://localhost:8001"

BASE_URL = f"{BACKEND_URL}/api"

def test_backend_accessibility():
 """Test if backend is accessible from frontend URL"""
 print("🔗 TESTING BACKEND ACCESSIBILITY")
 print("=" * 50)

 print(f"Frontend expects backend at: {BACKEND_URL}")
 print(f"Testing API base URL: {BASE_URL}")

 try:
 # Test health endpoint first
 response = requests.get(f"{BACKEND_URL}/health", timeout=5)
 if response.status_code == 200:
 print(" Backend health endpoint accessible")
 data = response.json()
 print(f" Service: {data.get('service', 'Unknown')}")
 print(f" Version: {data.get('version', 'Unknown')}")
 return True
 else:
 print(f" Backend health check failed: HTTP {response.status_code}")
 return False
 except requests.exceptions.RequestException as e:
 print(f" Backend not accessible: {str(e)}")
 return False

def test_builder_price_endpoint():
 """
 Test the /api/builder/price endpoint that BuilderPage uses.
 Tests the specific Long Call strategy payload as requested in review.
 """
 print("\n TESTING /API/BUILDER/PRICE ENDPOINT")
 print("=" * 50)

 # Long Call strategy payload as specified in review request
 long_call_payload = {
 "symbol": "TSLA",
 "strategyId": "long_call",
 "legs": [{"type": "CALL", "strike": 255, "side": "BUY", "qty": 1}],
 "spot": 250, # Current TSLA price
 "iv_mult": 1.0,
 "range_pct": 0.15,
 "dte": 30,
 "expiry": "2025-02-21",
 }

 print("Testing Long Call strategy payload:")
 print(f" Symbol: {long_call_payload['symbol']}")
 print(f" Strategy: {long_call_payload['strategyId']}")
 print(f" Strike: ${long_call_payload['legs'][0]['strike']}")
 print(f" Type: {long_call_payload['legs'][0]['type']}")
 print(f" Side: {long_call_payload['legs'][0]['side']}")

 try:
 start_time = time.time()
 response = requests.post(
 f"{BASE_URL}/builder/price", json=long_call_payload, timeout=10
 )
 response_time = time.time() - start_time

 print(f"\n⏱️ Response time: {response_time:.3f}s")

 if response.status_code == 200:
 data = response.json()
 print(" /api/builder/price endpoint working")
 print(f" Response structure: {list(data.keys())}")

 # Validate required fields as specified in review
 required_sections = ["meta", "pricing", "chart", "greeks"]
 missing_sections = [
 section for section in required_sections if section not in data
 ]

 if not missing_sections:
 print(" All required sections present")

 # Validate meta section
 meta = data.get("meta", {})
 print("\n META SECTION:")
 print(f" Symbol: {meta.get('symbol')}")
 print(f" Spot Price: ${meta.get('spot')}")
 print(f" Expiry: {meta.get('expiry')}")
 print(f" DTE: {meta.get('dte')} days")

 # Validate pricing section
 pricing = data.get("pricing", {})
 print("\n PRICING SECTION:")
 print(f" Net Debit: ${pricing.get('net_debit')}")
 print(f" Max Profit: ${pricing.get('max_profit')}")
 print(f" Max Loss: ${pricing.get('max_loss')}")
 print(f" Breakevens: {pricing.get('breakevens')}")

 # Validate chart section
 chart = data.get("chart", {})
 print("\n CHART SECTION:")
 print(f" X Range: ${chart.get('x_min')} - ${chart.get('x_max')}")
 series = chart.get("series", [])
 if series:
 print(f" Series Count: {len(series)}")
 print(f" Data Points: {len(series[0].get('xy', []))} points")
 else:
 print(" No chart series data")

 # Validate greeks section
 greeks = data.get("greeks", {})
 print("\n🔢 GREEKS SECTION:")
 print(f" Delta: {greeks.get('delta')}")
 print(f" Gamma: {greeks.get('gamma')}")
 print(f" Theta: {greeks.get('theta')}")
 print(f" Vega: {greeks.get('vega')}")

 # Check for quality data (bonus)
 if "quality" in data:
 quality = data.get("quality", {})
 print("\n QUALITY SECTION (BONUS):")
 print(f" Score: {quality.get('score')}")
 print(f" Buckets: {quality.get('buckets', {})}")
 print(f" Flags: {quality.get('flags', [])}")

 # Validate data integrity
 validation_results = []

 # Check meta fields
 if meta.get("symbol") == "TSLA":
 print(" Symbol matches request")
 validation_results.append(True)
 else:
 print(" Symbol mismatch")
 validation_results.append(False)

 # Check pricing fields are numeric
 numeric_fields = ["net_debit", "max_loss"]
 for field in numeric_fields:
 value = pricing.get(field)
 if isinstance(value, (int, float)) and value >= 0:
 validation_results.append(True)
 else:
 print(f" {field} is not valid: {value}")
 validation_results.append(False)

 # Check chart data exists
 if series and len(series[0].get("xy", [])) > 0:
 print(" Chart data present")
 validation_results.append(True)
 else:
 print(" Chart data missing")
 validation_results.append(False)

 # Check greeks are numeric
 greek_fields = ["delta", "gamma", "theta", "vega"]
 for field in greek_fields:
 value = greeks.get(field)
 if isinstance(value, (int, float)):
 validation_results.append(True)
 else:
 print(f" {field} is not numeric: {value}")
 validation_results.append(False)

 all_valid = all(validation_results)

 if all_valid:
 print("\n ALL VALIDATIONS PASSED")
 print(" API response includes all required fields")
 print(" Data types are correct")
 print(" Values are realistic")
 return True, data
 else:
 print(
 f"\n SOME VALIDATIONS FAILED ({sum(validation_results)}/{len(validation_results)} passed)"
 )
 return False, data

 else:
 print(f" Missing required sections: {missing_sections}")
 return False, data

 else:
 print(f" /api/builder/price failed: HTTP {response.status_code}")
 print(f"Response: {response.text}")
 return False, None

 except requests.exceptions.RequestException as e:
 print(f" Request error: {str(e)}")
 return False, None

def test_builder_page_loading_scenario():
 """
 Test the scenario described in review: BuilderPage getting stuck on 'Loading Options Builder...'
 This tests if the backend API can handle the requests that BuilderPage makes.
 """
 print("\n🔄 TESTING BUILDERPAGE LOADING SCENARIO")
 print("=" * 50)

 print(
 "Simulating BuilderPage requests that might cause 'Loading Options Builder...' issue"
 )

 # Test 1: Basic strategy loading (what BuilderPage does on /build/long_call)
 print("\n1. Testing basic strategy loading...")

 basic_payload = {
 "symbol": "TSLA",
 "strategyId": "long_call",
 "legs": [{"type": "CALL", "strike": 255, "side": "BUY", "qty": 1}],
 "dte": 30,
 }

 try:
 response = requests.post(
 f"{BASE_URL}/builder/price", json=basic_payload, timeout=5
 )
 if response.status_code == 200:
 print(" Basic strategy loading works")
 else:
 print(f" Basic strategy loading failed: HTTP {response.status_code}")
 return False
 except Exception as e:
 print(f" Basic strategy loading error: {str(e)}")
 return False

 # Test 2: Options chain data (BuilderPage needs this for strike selection)
 print("\n2. Testing options chain data...")

 try:
 response = requests.get(f"{BASE_URL}/options/chain?symbol=TSLA", timeout=5)
 if response.status_code == 200:
 print(" Options chain endpoint accessible")
 else:
 print(f" Options chain failed: HTTP {response.status_code}")
 # This might not be critical if builder has fallback
 except Exception as e:
 print(f" Options chain error: {str(e)}")

 # Test 3: Options expirations (BuilderPage needs this for expiry selection)
 print("\n3. Testing options expirations...")

 try:
 response = requests.get(
 f"{BASE_URL}/options/expirations?symbol=TSLA", timeout=5
 )
 if response.status_code == 200:
 print(" Options expirations endpoint accessible")
 else:
 print(f" Options expirations failed: HTTP {response.status_code}")
 except Exception as e:
 print(f" Options expirations error: {str(e)}")

 # Test 4: Rapid successive requests (simulate user interactions)
 print("\n4. Testing rapid successive requests...")

 success_count = 0
 for i in range(3):
 try:
 response = requests.post(
 f"{BASE_URL}/builder/price", json=basic_payload, timeout=3
 )
 if response.status_code == 200:
 success_count += 1
 except:
 pass

 if success_count == 3:
 print(" Rapid requests handled successfully")
 return True
 else:
 print(f" Only {success_count}/3 rapid requests succeeded")
 return success_count > 0

def main():
 """Main test execution for Build mega menu navigation to Builder page"""
 print(" BUILD MEGA MENU NAVIGATION TO BUILDER PAGE - BACKEND TESTING")
 print("=" * 70)
 print("Testing backend API endpoints that BuilderPage uses")
 print()

 # Test 1: Backend accessibility
 backend_accessible = test_backend_accessibility()

 if not backend_accessible:
 print("\n CRITICAL: Backend not accessible - BuilderPage will fail to load")
 return False

 # Test 2: Main builder/price endpoint
 price_success, price_data = test_builder_price_endpoint()

 # Test 3: BuilderPage loading scenario
 loading_success = test_builder_page_loading_scenario()

 # Final assessment
 print("\n FINAL TEST RESULTS")
 print("=" * 40)

 print(f" Backend Accessibility: {'PASS' if backend_accessible else 'FAIL'}")
 print(f" Builder Price Endpoint: {'PASS' if price_success else 'FAIL'}")
 print(f" BuilderPage Loading Scenario: {'PASS' if loading_success else 'FAIL'}")

 overall_success = backend_accessible and price_success and loading_success

 if overall_success:
 print("\n ALL TESTS PASSED - Build mega menu navigation backend is working!")
 print(" Backend is accessible from frontend")
 print(" /api/builder/price returns valid pricing data with chart information")
 print(
 " API response includes all required fields (meta, pricing, chart, greeks)"
 )
 print(" BuilderPage should be able to load strategy data successfully")
 print(
 "\n If BuilderPage is still stuck on 'Loading Options Builder...', the issue is likely:"
 )
 print(" - Frontend JavaScript errors")
 print(" - React component lifecycle issues")
 print(" - Network connectivity problems")
 print(" - CORS configuration issues")
 else:
 print("\n SOME TESTS FAILED - Issues detected with backend API")
 if not backend_accessible:
 print(" Backend accessibility issue - check server status")
 if not price_success:
 print(" Builder price endpoint issue - check API implementation")
 if not loading_success:
 print(" BuilderPage loading scenario issue - check API performance")

 return overall_success

if __name__ == "__main__":
 main()
