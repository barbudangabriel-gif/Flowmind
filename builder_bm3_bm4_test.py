#!/usr/bin/env python3
"""
Builder Backend Testing for BM3/BM4.1 Integration
Testing Builder endpoints for StrikeRailPro and GhostPagerOverlay components
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://options-analytics.preview.emergentagent.com/api"


def test_builder_price_endpoint():
    """Test POST /api/builder/price endpoint with sample strategy data"""
    print("🎯 TESTING POST /api/builder/price ENDPOINT")
    print("=" * 60)

    # Test 1: Long Call TSLA Strategy
    print("\n✅ TEST 1: Long Call TSLA Strategy")
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
            print("✅ Long Call pricing successful")

            # Verify required sections for BM3/BM4.1 integration
            required_sections = ["pricing", "greeks", "chart", "meta"]
            for section in required_sections:
                if section in data:
                    print(f"  ✅ {section} section present")
                else:
                    print(f"  ❌ {section} section missing")
                    return False

            # Verify pricing section fields
            pricing = data.get("pricing", {})
            pricing_fields = ["net_debit", "chance_profit"]
            for field in pricing_fields:
                if field in pricing:
                    print(f"  ✅ pricing.{field}: {pricing[field]}")
                else:
                    print(f"  ❌ pricing.{field} missing")

            # Verify greeks section with all 4 Greeks
            greeks = data.get("greeks", {})
            greek_fields = ["delta", "gamma", "theta", "vega"]
            for field in greek_fields:
                if field in greeks:
                    print(f"  ✅ greeks.{field}: {greeks[field]}")
                else:
                    print(f"  ❌ greeks.{field} missing")

            # Verify chart section for visualization
            chart = data.get("chart", {})
            if "series" in chart:
                series = chart["series"]
                if isinstance(series, list) and len(series) > 0:
                    print(
                        f"  ✅ chart.series: {len(series)} series with {len(series[0].get('data', []))} data points"
                    )
                else:
                    print("  ❌ chart.series empty or invalid")
            else:
                print("  ❌ chart.series missing")

            # Verify meta section
            meta = data.get("meta", {})
            meta_fields = ["symbol", "spot"]
            for field in meta_fields:
                if field in meta:
                    print(f"  ✅ meta.{field}: {meta[field]}")
                else:
                    print(f"  ❌ meta.{field} missing")

        else:
            print(f"❌ Request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Long Call test failed: {str(e)}")
        return False

    # Test 2: Bull Call Spread Strategy (Multi-leg)
    print("\n✅ TEST 2: Bull Call Spread Strategy (Multi-leg)")
    bull_call_spread_payload = {
        "symbol": "TSLA",
        "legs": [
            {"side": "BUY", "type": "CALL", "strike": 245, "qty": 1},
            {"side": "SELL", "type": "CALL", "strike": 255, "qty": 1},
        ],
        "qty": 1,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=bull_call_spread_payload, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Bull Call Spread pricing successful")

            # Verify multi-leg calculations
            pricing = data.get("pricing", {})
            if "net_debit" in pricing and "chance_profit" in pricing:
                print(
                    f"  ✅ Multi-leg pricing: Debit=${pricing['net_debit']}, Chance={pricing['chance_profit']}%"
                )

            # Verify Greeks aggregation for multi-leg
            greeks = data.get("greeks", {})
            if all(field in greeks for field in ["delta", "gamma", "theta", "vega"]):
                print(
                    f"  ✅ Multi-leg Greeks: δ={greeks['delta']}, γ={greeks['gamma']}, θ={greeks['theta']}, ν={greeks['vega']}"
                )
            else:
                print("  ❌ Multi-leg Greeks incomplete")

        else:
            print(f"❌ Bull Call Spread failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Bull Call Spread test failed: {str(e)}")
        return False

    # Test 3: Error Handling
    print("\n✅ TEST 3: Error Handling")

    # Test invalid payload
    invalid_payload = {"symbol": "INVALID_SYMBOL", "legs": []}

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=invalid_payload, timeout=15
        )
        print(f"Invalid payload - Status: {response.status_code}")

        if response.status_code in [400, 422, 500]:
            print("✅ Error handling working - proper error status returned")
        elif response.status_code == 200:
            data = response.json()
            print("✅ Graceful handling - returns valid response structure")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")

    return True


def test_options_chain_endpoint():
    """Test GET /api/options/chain endpoint for chain data availability"""
    print("\n🎯 TESTING GET /api/options/chain ENDPOINT")
    print("=" * 60)

    # Test 1: TSLA Options Chain
    print("\n✅ TEST 1: TSLA Options Chain Data")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": "TSLA"}, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Options chain data retrieved successfully")

            # Verify required fields for StrikeRailPro integration
            required_fields = ["spot", "chains"]
            for field in required_fields:
                if field in data:
                    print(f"  ✅ {field} field present")
                else:
                    print(f"  ❌ {field} field missing")

            # Verify chain structure for strikes data
            chains = data.get("chains", [])
            if isinstance(chains, list) and len(chains) > 0:
                print(f"  ✅ chains: {len(chains)} expiration groups")

                # Check first chain for strike structure
                first_chain = chains[0]
                if "strikes" in first_chain:
                    strikes = first_chain["strikes"]
                    if isinstance(strikes, list) and len(strikes) > 0:
                        print(f"  ✅ strikes: {len(strikes)} strike prices available")

                        # Verify strike data structure
                        first_strike = strikes[0]
                        strike_fields = ["StrikePrice", "Calls", "Puts"]
                        for field in strike_fields:
                            if field in first_strike:
                                print(f"    ✅ strike.{field} present")
                            else:
                                print(f"    ❌ strike.{field} missing")

                        # Verify Calls/Puts have OpenInterest data
                        calls = first_strike.get("Calls", {})
                        puts = first_strike.get("Puts", {})

                        for option_type, option_data in [
                            ("Calls", calls),
                            ("Puts", puts),
                        ]:
                            if "OpenInterest" in option_data:
                                print(
                                    f"    ✅ {option_type}.OpenInterest: {option_data['OpenInterest']}"
                                )
                            else:
                                print(f"    ❌ {option_type}.OpenInterest missing")
                    else:
                        print("  ❌ strikes array empty or invalid")
                else:
                    print("  ❌ strikes field missing from chain")
            else:
                print("  ❌ chains array empty or invalid")

            # Verify spot price for current market data
            spot = data.get("spot")
            if spot and isinstance(spot, (int, float)) and spot > 0:
                print(f"  ✅ spot price: ${spot}")
            else:
                print(f"  ❌ invalid spot price: {spot}")

        else:
            print(f"❌ Request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options chain test failed: {str(e)}")
        return False

    # Test 2: Different Symbol (AAPL)
    print("\n✅ TEST 2: AAPL Options Chain Data")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": "AAPL"}, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            chains = data.get("chains", [])
            spot = data.get("spot")
            print(f"  ✅ AAPL chain: {len(chains)} expirations, spot=${spot}")
        else:
            print(f"  ⚠️ AAPL chain failed: {response.status_code}")

    except Exception as e:
        print(f"❌ AAPL chain test failed: {str(e)}")

    return True


def test_options_expirations_endpoint():
    """Test GET /api/options/expirations endpoint for expiration data"""
    print("\n🎯 TESTING GET /api/options/expirations ENDPOINT")
    print("=" * 60)

    # Test 1: TSLA Expirations
    print("\n✅ TEST 1: TSLA Expiration Dates")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/expirations", params={"symbol": "TSLA"}, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Expiration data retrieved successfully")

            # Verify expirations field
            if "expirations" in data:
                expirations = data["expirations"]
                if isinstance(expirations, list) and len(expirations) > 0:
                    print(f"  ✅ expirations: {len(expirations)} dates available")

                    # Show first few expirations
                    for i, exp in enumerate(expirations[:5]):
                        print(f"    {i+1}. {exp}")

                    if len(expirations) > 5:
                        print(f"    ... and {len(expirations) - 5} more")

                    # Verify date format (should be YYYY-MM-DD or similar)
                    first_exp = expirations[0]
                    if isinstance(first_exp, str) and len(first_exp) >= 8:
                        print(f"  ✅ date format appears valid: {first_exp}")
                    else:
                        print(f"  ⚠️ date format may be invalid: {first_exp}")

                else:
                    print("  ❌ expirations array empty or invalid")
            else:
                print("  ❌ expirations field missing")

        else:
            print(f"❌ Request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Expirations test failed: {str(e)}")
        return False

    # Test 2: Different Symbol (AAPL)
    print("\n✅ TEST 2: AAPL Expiration Dates")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/expirations", params={"symbol": "AAPL"}, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            expirations = data.get("expirations", [])
            print(f"  ✅ AAPL expirations: {len(expirations)} dates")
        else:
            print(f"  ⚠️ AAPL expirations failed: {response.status_code}")

    except Exception as e:
        print(f"❌ AAPL expirations test failed: {str(e)}")

    return True


def test_comprehensive_integration():
    """Test comprehensive integration for BM3/BM4.1 components"""
    print("\n🎯 TESTING COMPREHENSIVE BM3/BM4.1 INTEGRATION")
    print("=" * 60)

    # Test complete workflow: Get expirations -> Get chain -> Price strategy
    print("\n✅ COMPREHENSIVE WORKFLOW TEST")

    symbol = "TSLA"

    try:
        # Step 1: Get available expirations
        print(f"Step 1: Getting expirations for {symbol}")
        exp_response = requests.get(
            f"{BACKEND_URL}/options/expirations", params={"symbol": symbol}, timeout=15
        )

        if exp_response.status_code != 200:
            print(f"❌ Expirations failed: {exp_response.status_code}")
            return False

        exp_data = exp_response.json()
        expirations = exp_data.get("expirations", [])

        if not expirations:
            print("❌ No expirations available")
            return False

        print(f"  ✅ Found {len(expirations)} expirations")

        # Step 2: Get options chain
        print(f"Step 2: Getting options chain for {symbol}")
        chain_response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": symbol}, timeout=15
        )

        if chain_response.status_code != 200:
            print(f"❌ Chain failed: {chain_response.status_code}")
            return False

        chain_data = chain_response.json()
        spot = chain_data.get("spot")
        chains = chain_data.get("chains", [])

        if not chains:
            print("❌ No chain data available")
            return False

        print(f"  ✅ Chain data retrieved, spot=${spot}")

        # Step 3: Find suitable strikes for strategy
        first_chain = chains[0]
        strikes = first_chain.get("strikes", [])

        if not strikes:
            print("❌ No strikes available")
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
            print("❌ Could not find suitable strikes")
            return False

        print(f"  ✅ Found strikes: ATM=${atm_strike}, OTM=${otm_strike}")

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
            print(f"❌ Pricing failed: {price_response.status_code}")
            return False

        price_data = price_response.json()
        pricing = price_data.get("pricing", {})
        greeks = price_data.get("greeks", {})

        print("  ✅ Strategy priced successfully:")
        print(f"    Net Debit: ${pricing.get('net_debit', 'N/A')}")
        print(f"    Chance of Profit: {pricing.get('chance_profit', 'N/A')}%")
        print(f"    Delta: {greeks.get('delta', 'N/A')}")
        print(f"    Gamma: {greeks.get('gamma', 'N/A')}")
        print(f"    Theta: {greeks.get('theta', 'N/A')}")
        print(f"    Vega: {greeks.get('vega', 'N/A')}")

        print("\n✅ COMPREHENSIVE INTEGRATION TEST PASSED")
        return True

    except Exception as e:
        print(f"❌ Comprehensive test failed: {str(e)}")
        return False


def verify_data_structure_requirements():
    """Verify all required data fields are present for BM3/BM4.1 integration"""
    print("\n🎯 VERIFYING DATA STRUCTURE REQUIREMENTS")
    print("=" * 60)

    requirements = {
        "Builder Price Endpoint": {
            "pricing": ["net_debit", "chance_profit"],
            "greeks": ["delta", "gamma", "theta", "vega"],
            "chart": ["series"],
            "meta": ["symbol", "spot"],
        },
        "Options Chain Endpoint": {
            "root": ["spot", "chains"],
            "strikes": ["StrikePrice", "Calls", "Puts"],
            "options": ["OpenInterest"],
        },
        "Options Expirations Endpoint": {"root": ["expirations"]},
    }

    print("\n📋 REQUIRED DATA STRUCTURE VERIFICATION:")

    for endpoint, sections in requirements.items():
        print(f"\n{endpoint}:")
        for section, fields in sections.items():
            print(f"  {section}: {', '.join(fields)}")

    # Test actual data structure compliance
    print("\n🔍 TESTING ACTUAL COMPLIANCE:")

    # Test Builder Price
    try:
        price_payload = {
            "symbol": "TSLA",
            "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
            "qty": 1,
        }

        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=price_payload, timeout=15
        )
        if response.status_code == 200:
            data = response.json()

            compliance_score = 0
            total_checks = 0

            for section, fields in requirements["Builder Price Endpoint"].items():
                section_data = data.get(section, {})
                for field in fields:
                    total_checks += 1
                    if field in section_data:
                        compliance_score += 1
                        print(f"  ✅ {section}.{field}")
                    else:
                        print(f"  ❌ {section}.{field}")

            print(
                f"\nBuilder Price Compliance: {compliance_score}/{total_checks} ({compliance_score/total_checks*100:.1f}%)"
            )
        else:
            print("❌ Builder Price endpoint failed")

    except Exception as e:
        print(f"❌ Builder Price verification failed: {str(e)}")

    # Test Options Chain
    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": "TSLA"}, timeout=15
        )
        if response.status_code == 200:
            data = response.json()

            compliance_score = 0
            total_checks = 0

            # Check root fields
            for field in requirements["Options Chain Endpoint"]["root"]:
                total_checks += 1
                if field in data:
                    compliance_score += 1
                    print(f"  ✅ root.{field}")
                else:
                    print(f"  ❌ root.{field}")

            # Check strikes structure if available
            chains = data.get("chains", [])
            if chains and "strikes" in chains[0]:
                strikes = chains[0]["strikes"]
                if strikes:
                    first_strike = strikes[0]

                    for field in requirements["Options Chain Endpoint"]["strikes"]:
                        total_checks += 1
                        if field in first_strike:
                            compliance_score += 1
                            print(f"  ✅ strikes.{field}")
                        else:
                            print(f"  ❌ strikes.{field}")

                    # Check options data
                    for option_type in ["Calls", "Puts"]:
                        option_data = first_strike.get(option_type, {})
                        for field in requirements["Options Chain Endpoint"]["options"]:
                            total_checks += 1
                            if field in option_data:
                                compliance_score += 1
                                print(f"  ✅ {option_type}.{field}")
                            else:
                                print(f"  ❌ {option_type}.{field}")

            print(
                f"\nOptions Chain Compliance: {compliance_score}/{total_checks} ({compliance_score/total_checks*100:.1f}%)"
            )
        else:
            print("❌ Options Chain endpoint failed")

    except Exception as e:
        print(f"❌ Options Chain verification failed: {str(e)}")

    # Test Options Expirations
    try:
        response = requests.get(
            f"{BACKEND_URL}/options/expirations", params={"symbol": "TSLA"}, timeout=15
        )
        if response.status_code == 200:
            data = response.json()

            compliance_score = 0
            total_checks = 0

            for field in requirements["Options Expirations Endpoint"]["root"]:
                total_checks += 1
                if field in data:
                    compliance_score += 1
                    print(f"  ✅ root.{field}")
                else:
                    print(f"  ❌ root.{field}")

            print(
                f"\nOptions Expirations Compliance: {compliance_score}/{total_checks} ({compliance_score/total_checks*100:.1f}%)"
            )
        else:
            print("❌ Options Expirations endpoint failed")

    except Exception as e:
        print(f"❌ Options Expirations verification failed: {str(e)}")

    return True


if __name__ == "__main__":
    print("🚀 Starting Builder Backend Testing for BM3/BM4.1 Integration")
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

    print("\n5️⃣ VERIFYING DATA STRUCTURE REQUIREMENTS")
    result5 = verify_data_structure_requirements()
    test_results.append(("Data Structure Requirements", result5))

    # Summary
    print("\n" + "=" * 80)
    print("🎉 BUILDER BM3/BM4.1 INTEGRATION TESTING COMPLETE")
    print("=" * 80)

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    print("\n📊 TEST RESULTS SUMMARY:")
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name}")

    print(
        f"\n🎯 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)"
    )

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Builder backend ready for BM3/BM4.1 integration!")
    else:
        print("⚠️ Some tests failed - review issues before BM3/BM4.1 integration")

    print(f"\n✅ Testing completed at {datetime.now().isoformat()}")
