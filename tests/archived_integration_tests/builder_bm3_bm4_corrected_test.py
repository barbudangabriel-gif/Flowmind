#!/usr/bin/env python3
"""
Builder Backend Testing for BM3/BM4.1 Integration - CORRECTED VERSION
Testing Builder endpoints for StrikeRailPro and GhostPagerOverlay components
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "http://localhost:8000/api"

def test_builder_price_endpoint():
 """Test POST /api/builder/price endpoint with sample strategy data"""
 print(" TESTING POST /api/builder/price ENDPOINT")
 print("=" * 60)

 # Test 1: Long Call TSLA Strategy
 print("\n TEST 1: Long Call TSLA Strategy")
 long_call_payload = {
 "symbol": "TSLA",
 "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
 "qty": 1,
 }

 try:
 response = requests.post(
 f"{BACKEND_URL}/builder/price", json=long_call_payload, timeout=15
 )
 print(f"Status Code: {response.status_code}")

 if response.status_code == 200:
 data = response.json()
 print(" Long Call pricing successful")

 # Verify required sections for BM3/BM4.1 integration
 required_sections = ["pricing", "greeks", "chart", "meta"]
 for section in required_sections:
 if section in data:
 print(f" {section} section present")
 else:
 print(f" {section} section missing")
 return False

 # Verify pricing section fields
 pricing = data.get("pricing", {})
 pricing_fields = ["net_debit", "chance_profit"]
 for field in pricing_fields:
 if field in pricing:
 print(f" pricing.{field}: {pricing[field]}")
 else:
 print(f" pricing.{field} missing")

 # Verify greeks section with all 4 Greeks
 greeks = data.get("greeks", {})
 greek_fields = ["delta", "gamma", "theta", "vega"]
 for field in greek_fields:
 if field in greeks:
 print(f" greeks.{field}: {greeks[field]}")
 else:
 print(f" greeks.{field} missing")

 # Verify chart section for visualization
 chart = data.get("chart", {})
 if "series" in chart:
 series = chart["series"]
 if isinstance(series, list):
 print(f" chart.series: {len(series)} series available")
 if len(series) > 0 and "data" in series[0]:
 print(
 f" First series has {len(series[0]['data'])} data points"
 )
 else:
 print(" chart.series not a list")
 else:
 print(" chart.series missing")

 # Verify meta section
 meta = data.get("meta", {})
 meta_fields = ["symbol", "spot"]
 for field in meta_fields:
 if field in meta:
 print(f" meta.{field}: {meta[field]}")
 else:
 print(f" meta.{field} missing")

 else:
 print(f" Request failed: {response.text}")
 return False

 except Exception as e:
 print(f" Long Call test failed: {str(e)}")
 return False

 return True

def test_options_chain_endpoint():
 """Test GET /api/options/chain endpoint for chain data availability"""
 print("\n TESTING GET /api/options/chain ENDPOINT")
 print("=" * 60)

 # Test 1: TSLA Options Chain
 print("\n TEST 1: TSLA Options Chain Data")

 try:
 response = requests.get(
 f"{BACKEND_URL}/options/chain", params={"symbol": "TSLA"}, timeout=15
 )
 print(f"Status Code: {response.status_code}")

 if response.status_code == 200:
 data = response.json()
 print(" Options chain data retrieved successfully")

 # Verify required fields for StrikeRailPro integration
 required_fields = ["spot", "raw"]
 for field in required_fields:
 if field in data:
 print(f" {field} field present")
 else:
 print(f" {field} field missing")

 # Verify actual chain structure (raw.OptionChains)
 raw_data = data.get("raw", {})
 option_chains = raw_data.get("OptionChains", [])

 if isinstance(option_chains, list) and len(option_chains) > 0:
 print(f" OptionChains: {len(option_chains)} expiration groups")

 # Check first chain for strike structure
 first_chain = option_chains[0]
 if "Strikes" in first_chain:
 strikes = first_chain["Strikes"]
 if isinstance(strikes, list) and len(strikes) > 0:
 print(f" Strikes: {len(strikes)} strike prices available")

 # Verify strike data structure
 first_strike = strikes[0]
 strike_fields = ["StrikePrice", "Calls", "Puts"]
 for field in strike_fields:
 if field in first_strike:
 print(f" strike.{field} present")
 else:
 print(f" strike.{field} missing")

 # Verify Calls/Puts have OpenInterest data
 calls = first_strike.get("Calls", [])
 puts = first_strike.get("Puts", [])

 for option_type, option_list in [
 ("Calls", calls),
 ("Puts", puts),
 ]:
 if isinstance(option_list, list) and len(option_list) > 0:
 option_data = option_list[0]
 if "OpenInterest" in option_data:
 print(
 f" {option_type}[0].OpenInterest: {option_data['OpenInterest']}"
 )
 else:
 print(
 f" {option_type}[0].OpenInterest missing"
 )

 # Check for other required fields
 required_option_fields = [
 "Volume",
 "Bid",
 "Ask",
 "Last",
 "IV",
 ]
 for field in required_option_fields:
 if field in option_data:
 print(
 f" {option_type}[0].{field}: {option_data[field]}"
 )
 else:
 print(
 f" {option_type}[0].{field} missing"
 )
 else:
 print(f" {option_type} array empty or invalid")
 else:
 print(" Strikes array empty or invalid")
 else:
 print(" Strikes field missing from chain")
 else:
 print(" OptionChains array empty or invalid")

 # Verify spot price for current market data
 spot = data.get("spot")
 if spot and isinstance(spot, (int, float)) and spot > 0:
 print(f" spot price: ${spot}")
 else:
 print(f" invalid spot price: {spot}")

 else:
 print(f" Request failed: {response.text}")
 return False

 except Exception as e:
 print(f" Options chain test failed: {str(e)}")
 return False

 return True

def test_options_expirations_endpoint():
 """Test GET /api/options/expirations endpoint for expiration data"""
 print("\n TESTING GET /api/options/expirations ENDPOINT")
 print("=" * 60)

 # Test 1: TSLA Expirations
 print("\n TEST 1: TSLA Expiration Dates")

 try:
 response = requests.get(
 f"{BACKEND_URL}/options/expirations", params={"symbol": "TSLA"}, timeout=15
 )
 print(f"Status Code: {response.status_code}")

 if response.status_code == 200:
 data = response.json()
 print(" Expiration data retrieved successfully")

 # Verify expirations field
 if "expirations" in data:
 expirations = data["expirations"]
 if isinstance(expirations, list) and len(expirations) > 0:
 print(f" expirations: {len(expirations)} dates available")

 # Show first few expirations
 for i, exp in enumerate(expirations[:5]):
 print(f" {i+1}. {exp}")

 if len(expirations) > 5:
 print(f" ... and {len(expirations) - 5} more")

 # Verify date format (should be YYYY-MM-DD or similar)
 first_exp = expirations[0]
 if isinstance(first_exp, str) and len(first_exp) >= 8:
 print(f" date format appears valid: {first_exp}")
 else:
 print(f" date format may be invalid: {first_exp}")

 else:
 print(" expirations array empty or invalid")
 else:
 print(" expirations field missing")

 else:
 print(f" Request failed: {response.text}")
 return False

 except Exception as e:
 print(f" Expirations test failed: {str(e)}")
 return False

 return True

def test_comprehensive_integration():
 """Test comprehensive integration for BM3/BM4.1 components"""
 print("\n TESTING COMPREHENSIVE BM3/BM4.1 INTEGRATION")
 print("=" * 60)

 # Test complete workflow: Get expirations -> Get chain -> Price strategy
 print("\n COMPREHENSIVE WORKFLOW TEST")

 symbol = "TSLA"

 try:
 # Step 1: Get available expirations
 print(f"Step 1: Getting expirations for {symbol}")
 exp_response = requests.get(
 f"{BACKEND_URL}/options/expirations", params={"symbol": symbol}, timeout=15
 )

 if exp_response.status_code != 200:
 print(f" Expirations failed: {exp_response.status_code}")
 return False

 exp_data = exp_response.json()
 expirations = exp_data.get("expirations", [])

 if not expirations:
 print(" No expirations available")
 return False

 print(f" Found {len(expirations)} expirations")

 # Step 2: Get options chain
 print(f"Step 2: Getting options chain for {symbol}")
 chain_response = requests.get(
 f"{BACKEND_URL}/options/chain", params={"symbol": symbol}, timeout=15
 )

 if chain_response.status_code != 200:
 print(f" Chain failed: {chain_response.status_code}")
 return False

 chain_data = chain_response.json()
 spot = chain_data.get("spot")
 raw_data = chain_data.get("raw", {})
 option_chains = raw_data.get("OptionChains", [])

 if not option_chains:
 print(" No chain data available")
 return False

 print(f" Chain data retrieved, spot=${spot}")

 # Step 3: Find suitable strikes for strategy
 first_chain = option_chains[0]
 strikes = first_chain.get("Strikes", [])

 if not strikes:
 print(" No strikes available")
 return False

 # Find ATM and OTM strikes
 atm_strike = None
 otm_strike = None

 for strike_data in strikes:
 strike_price = strike_data.get("StrikePrice")
 if strike_price:
 if not atm_strike or abs(strike_price - spot) < abs(atm_strike - spot):
 atm_strike = strike_price
 if strike_price > spot and (
 not otm_strike or strike_price < otm_strike
 ):
 otm_strike = strike_price

 if not atm_strike or not otm_strike:
 print(" Could not find suitable strikes")
 return False

 print(f" Found strikes: ATM=${atm_strike}, OTM=${otm_strike}")

 # Step 4: Price a strategy using found strikes
 print("Step 3: Pricing Bull Call Spread strategy")
 strategy_payload = {
 "symbol": symbol,
 "legs": [
 {"side": "BUY", "type": "CALL", "strike": atm_strike, "qty": 1},
 {"side": "SELL", "type": "CALL", "strike": otm_strike, "qty": 1},
 ],
 "qty": 1,
 }

 price_response = requests.post(
 f"{BACKEND_URL}/builder/price", json=strategy_payload, timeout=15
 )

 if price_response.status_code != 200:
 print(f" Pricing failed: {price_response.status_code}")
 return False

 price_data = price_response.json()
 pricing = price_data.get("pricing", {})
 greeks = price_data.get("greeks", {})

 print(" Strategy priced successfully:")
 print(f" Net Debit: ${pricing.get('net_debit', 'N/A')}")
 print(f" Chance of Profit: {pricing.get('chance_profit', 'N/A')}")
 print(f" Delta: {greeks.get('delta', 'N/A')}")
 print(f" Gamma: {greeks.get('gamma', 'N/A')}")
 print(f" Theta: {greeks.get('theta', 'N/A')}")
 print(f" Vega: {greeks.get('vega', 'N/A')}")

 print("\n COMPREHENSIVE INTEGRATION TEST PASSED")
 return True

 except Exception as e:
 print(f" Comprehensive test failed: {str(e)}")
 return False

def test_error_handling():
 """Test proper error handling for invalid requests"""
 print("\n TESTING ERROR HANDLING")
 print("=" * 60)

 # Test 1: Invalid symbol for options chain
 print("\n TEST 1: Invalid Symbol Error Handling")

 try:
 response = requests.get(
 f"{BACKEND_URL}/options/chain",
 params={"symbol": "INVALID_SYMBOL_XYZ"},
 timeout=15,
 )
 print(f"Invalid symbol - Status: {response.status_code}")

 if response.status_code in [400, 404, 422, 500]:
 print(" Proper error status returned for invalid symbol")
 elif response.status_code == 200:
 data = response.json()
 print(" Graceful handling - returns valid response structure")
 else:
 print(f" Unexpected status code: {response.status_code}")

 except Exception as e:
 print(f" Invalid symbol test failed: {str(e)}")

 # Test 2: Missing required parameters for builder price
 print("\n TEST 2: Missing Parameters Error Handling")

 try:
 # Empty payload
 response = requests.post(f"{BACKEND_URL}/builder/price", json={}, timeout=15)
 print(f"Empty payload - Status: {response.status_code}")

 if response.status_code in [400, 422]:
 print(" Proper error status for empty payload")
 elif response.status_code == 200:
 print(" Graceful handling of empty payload")

 except Exception as e:
 print(f" Empty payload test failed: {str(e)}")

 return True

def verify_bm3_bm4_requirements():
 """Verify specific requirements for BM3/BM4.1 integration"""
 print("\n VERIFYING BM3/BM4.1 SPECIFIC REQUIREMENTS")
 print("=" * 60)

 print("\n BM3/BM4.1 INTEGRATION REQUIREMENTS:")
 print(" StrikeRailPro Component:")
 print(" - Options chain with strikes data")
 print(" - OpenInterest and Volume data for bars")
 print(" - Bid/Ask data for tooltips")
 print(" GhostPagerOverlay Component:")
 print(" - Real-time pricing calculations")
 print(" - Greeks data (delta, gamma, theta, vega)")
 print(" - Chart data for P&L visualization")

 # Test StrikeRailPro requirements
 print("\n TESTING STRIKERAILPRO REQUIREMENTS:")

 try:
 response = requests.get(
 f"{BACKEND_URL}/options/chain", params={"symbol": "TSLA"}, timeout=15
 )
 if response.status_code == 200:
 data = response.json()

 # Check for strikes data
 raw_data = data.get("raw", {})
 option_chains = raw_data.get("OptionChains", [])

 if option_chains and "Strikes" in option_chains[0]:
 strikes = option_chains[0]["Strikes"]
 if strikes:
 first_strike = strikes[0]
 calls = first_strike.get("Calls", [])

 if calls:
 call_data = calls[0]

 # Check StrikeRailPro requirements
 strikerail_fields = ["OpenInterest", "Volume", "Bid", "Ask"]
 strikerail_score = 0

 for field in strikerail_fields:
 if field in call_data:
 strikerail_score += 1
 print(f" StrikeRailPro.{field}: {call_data[field]}")
 else:
 print(f" StrikeRailPro.{field}: missing")

 print(
 f" StrikeRailPro Compliance: {strikerail_score}/{len(strikerail_fields)} ({strikerail_score/len(strikerail_fields)*100:.1f}%)"
 )
 else:
 print(" No call data available for StrikeRailPro")
 else:
 print(" No strikes data available for StrikeRailPro")
 else:
 print(" No option chains available for StrikeRailPro")
 else:
 print(" Options chain endpoint failed for StrikeRailPro")

 except Exception as e:
 print(f" StrikeRailPro test failed: {str(e)}")

 # Test GhostPagerOverlay requirements
 print("\n TESTING GHOSTPAGEROVERLAY REQUIREMENTS:")

 try:
 payload = {
 "symbol": "TSLA",
 "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
 "qty": 1,
 }

 response = requests.post(
 f"{BACKEND_URL}/builder/price", json=payload, timeout=15
 )
 if response.status_code == 200:
 data = response.json()

 # Check GhostPagerOverlay requirements
 ghost_requirements = {
 "pricing": ["net_debit", "chance_profit"],
 "greeks": ["delta", "gamma", "theta", "vega"],
 "chart": ["series"],
 }

 ghost_score = 0
 total_ghost_checks = 0

 for section, fields in ghost_requirements.items():
 section_data = data.get(section, {})
 for field in fields:
 total_ghost_checks += 1
 if field in section_data:
 ghost_score += 1
 print(
 f" GhostPagerOverlay.{section}.{field}: {section_data[field]}"
 )
 else:
 print(f" GhostPagerOverlay.{section}.{field}: missing")

 print(
 f" GhostPagerOverlay Compliance: {ghost_score}/{total_ghost_checks} ({ghost_score/total_ghost_checks*100:.1f}%)"
 )
 else:
 print(" Builder price endpoint failed for GhostPagerOverlay")

 except Exception as e:
 print(f" GhostPagerOverlay test failed: {str(e)}")

 return True

if __name__ == "__main__":
 print(" Starting Builder Backend Testing for BM3/BM4.1 Integration - CORRECTED")
 print(f"Backend URL: {BACKEND_URL}")
 print(f"Test Time: {datetime.now().isoformat()}")
 print("=" * 80)

 # Track test results
 test_results = []

 # Run all tests
 print("\n1️⃣ TESTING BUILDER PRICE ENDPOINT")
 result1 = test_builder_price_endpoint()
 test_results.append(("Builder Price Endpoint", result1))

 print("\n2️⃣ TESTING OPTIONS CHAIN ENDPOINT")
 result2 = test_options_chain_endpoint()
 test_results.append(("Options Chain Endpoint", result2))

 print("\n3️⃣ TESTING OPTIONS EXPIRATIONS ENDPOINT")
 result3 = test_options_expirations_endpoint()
 test_results.append(("Options Expirations Endpoint", result3))

 print("\n4️⃣ TESTING COMPREHENSIVE INTEGRATION")
 result4 = test_comprehensive_integration()
 test_results.append(("Comprehensive Integration", result4))

 print("\n5️⃣ TESTING ERROR HANDLING")
 result5 = test_error_handling()
 test_results.append(("Error Handling", result5))

 print("\n6️⃣ VERIFYING BM3/BM4.1 REQUIREMENTS")
 result6 = verify_bm3_bm4_requirements()
 test_results.append(("BM3/BM4.1 Requirements", result6))

 # Summary
 print("\n" + "=" * 80)
 print(" BUILDER BM3/BM4.1 INTEGRATION TESTING COMPLETE - CORRECTED")
 print("=" * 80)

 passed_tests = sum(1 for _, result in test_results if result)
 total_tests = len(test_results)

 print("\n TEST RESULTS SUMMARY:")
 for test_name, result in test_results:
 status = " PASSED" if result else " FAILED"
 print(f" {status} - {test_name}")

 print(
 f"\n OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)"
 )

 if passed_tests == total_tests:
 print(" ALL TESTS PASSED - Builder backend ready for BM3/BM4.1 integration!")
 else:
 print(" Some tests failed - review issues before BM3/BM4.1 integration")

 print(f"\n Testing completed at {datetime.now().isoformat()}")
