#!/usr/bin/env python3
"""
BM1 Builder Header & Expiration Backend Verification Test
Quick verification that all existing Builder functionality continues to work properly
after BM1 Builder Header & Expiration frontend implementation.
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://options-analytics.preview.emergentagent.com/api"


def test_builder_pricing_endpoints():
    """Test Builder pricing endpoints for header price display"""
    print("🎯 TESTING BUILDER PRICING ENDPOINTS")
    print("=" * 60)

    # Test 1: POST /api/builder/price - Complete data for header display
    print("\n✅ TEST 1: Builder Pricing Engine - Complete Data Structure")

    builder_price_payload = {
        "symbol": "TSLA",
        "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
        "qty": 1,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=builder_price_payload, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Verify complete data structure for header display
            required_sections = ["pricing", "chart", "meta", "greeks"]
            for section in required_sections:
                if section in data:
                    print(f"✅ {section.upper()} section present")
                else:
                    print(f"❌ {section.upper()} section missing")
                    return False

            # Check pricing data for header display
            pricing = data.get("pricing", {})
            if "net_debit" in pricing and "chance_profit" in pricing:
                print(
                    f"✅ Pricing data: Debit=${pricing.get('net_debit', 0):.2f}, Chance={pricing.get('chance_profit', 0):.1%}"
                )
            else:
                print("❌ Missing pricing data for header display")
                return False

            # Check Greeks for header display
            greeks = data.get("greeks", {})
            if "delta" in greeks:
                print(f"✅ Greeks data: Delta={greeks.get('delta', 0):.4f}")
            else:
                print("❌ Missing Greeks data for header display")
                return False

            # Check meta data for header display
            meta = data.get("meta", {})
            if "symbol" in meta and "spot" in meta:
                print(
                    f"✅ Meta data: Symbol={meta.get('symbol')}, Spot=${meta.get('spot', 0):.2f}"
                )
            else:
                print("❌ Missing meta data for header display")
                return False

            # Check chart data for visualization
            chart = data.get("chart", {})
            if "series" in chart:
                series_count = len(chart["series"])
                print(f"✅ Chart data: {series_count} series available")
            else:
                print("❌ Missing chart data")
                return False

            print("✅ Builder pricing endpoint working perfectly for header display")

        else:
            print(f"❌ Builder pricing failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Builder pricing test failed: {str(e)}")
        return False

    # Test 2: POST /api/builder/historical - Historical data functionality
    print("\n✅ TEST 2: Builder Historical Data - Continues Working")

    historical_payload = {
        "symbol": "TSLA",
        "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
        "qty": 1,
        "days": 30,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/historical", json=historical_payload, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            series = data.get("series", [])

            if len(series) > 0:
                print(f"✅ Historical data: {len(series)} data points returned")

                # Verify data structure
                first_point = series[0]
                required_fields = ["t", "spot", "pl"]

                for field in required_fields:
                    if field in first_point:
                        print(f"✅ Historical field '{field}' present")
                    else:
                        print(f"❌ Historical field '{field}' missing")
                        return False

                print("✅ Builder historical endpoint continues working")
            else:
                print("⚠️ Historical data returned empty series")

        else:
            print(f"❌ Builder historical failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Builder historical test failed: {str(e)}")
        return False

    return True


def test_options_chain_endpoints():
    """Test Options Chain endpoints for expiration picker"""
    print("\n🎯 TESTING OPTIONS CHAIN ENDPOINTS")
    print("=" * 60)

    # Test 1: GET /api/options/expirations - Expiration dates for picker
    print("\n✅ TEST 1: Options Expirations - For Expiration Picker")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/expirations?symbol=TSLA", timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check if expirations are returned
            if "expirations" in data or isinstance(data, list):
                expirations = data.get("expirations", data)
                if len(expirations) > 0:
                    print(
                        f"✅ Expirations data: {len(expirations)} expiration dates available"
                    )
                    print(
                        f"✅ Sample expirations: {expirations[:3] if len(expirations) >= 3 else expirations}"
                    )
                else:
                    print("⚠️ No expiration dates returned")
            else:
                print("❌ Invalid expirations response structure")
                return False

        else:
            print(f"❌ Options expirations failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options expirations test failed: {str(e)}")
        return False

    # Test 2: GET /api/options/chain - Strike data for strategy building
    print("\n✅ TEST 2: Options Chain - Strike Data for Strategy Building")

    try:
        response = requests.get(f"{BACKEND_URL}/options/chain?symbol=TSLA", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check chain data structure
            if "raw" in data and "spot" in data:
                print("✅ Options chain data structure present")

                # Check for strike data in raw chain
                raw_data = data.get("raw", {})
                if "OptionChains" in raw_data:
                    option_chains = raw_data["OptionChains"]
                    if len(option_chains) > 0:
                        strikes = option_chains[0].get("Strikes", [])
                        print(f"✅ Chain strikes: {len(strikes)} strikes available")
                    else:
                        print("⚠️ No option chains in raw data")

                # Check for spot price
                if "spot" in data:
                    spot_price = data["spot"]
                    print(f"✅ Spot price available: ${spot_price}")
                else:
                    print("⚠️ No spot price in chain data")

                print("✅ Options chain endpoint provides data for strategy building")

            else:
                print("❌ Invalid options chain response structure")
                print(
                    f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
                )
                return False

        else:
            print(f"❌ Options chain failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options chain test failed: {str(e)}")
        return False

    return True


def test_optimizer_integration():
    """Test Optimizer integration for strategy selection"""
    print("\n🎯 TESTING OPTIMIZER INTEGRATION")
    print("=" * 60)

    # Test 1: GET /api/optimize/suggest - Strategy selection continues working
    print("\n✅ TEST 1: Options Optimizer - Strategy Selection")

    try:
        response = requests.get(
            f"{BACKEND_URL}/optimize/suggest?symbol=TSLA&budget=5000", timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check if strategies are returned
            if "strategies" in data and len(data["strategies"]) > 0:
                strategies = data["strategies"]
                print(f"✅ Strategy suggestions: {len(strategies)} strategies returned")

                # Check strategy structure
                first_strategy = strategies[0]
                required_fields = ["id", "label", "roi", "chance", "legs"]

                for field in required_fields:
                    if field in first_strategy:
                        print(f"✅ Strategy field '{field}' present")
                    else:
                        print(f"❌ Strategy field '{field}' missing")
                        return False

                # Show sample strategy
                sample_strategy = first_strategy
                print(
                    f"✅ Sample strategy: {sample_strategy.get('label', 'Unknown')} - ROI: {sample_strategy.get('roi', 0):.1%}"
                )

                print(
                    "✅ Optimizer integration continues working for strategy selection"
                )

            else:
                print("❌ Invalid optimizer response - no strategies returned")
                return False

        else:
            print(f"❌ Optimizer failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Optimizer test failed: {str(e)}")
        return False

    return True


def run_comprehensive_verification():
    """Run comprehensive verification of Builder functionality"""
    print("🚀 BM1 BUILDER HEADER & EXPIRATION BACKEND VERIFICATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)

    test_results = []

    # Test 1: Builder Endpoints
    print("\n📊 PHASE 1: BUILDER ENDPOINTS VERIFICATION")
    builder_result = test_builder_pricing_endpoints()
    test_results.append(("Builder Endpoints", builder_result))

    # Test 2: Options Chain Endpoints
    print("\n📊 PHASE 2: OPTIONS CHAIN ENDPOINTS VERIFICATION")
    chain_result = test_options_chain_endpoints()
    test_results.append(("Options Chain", chain_result))

    # Test 3: Optimizer Integration
    print("\n📊 PHASE 3: OPTIMIZER INTEGRATION VERIFICATION")
    optimizer_result = test_optimizer_integration()
    test_results.append(("Optimizer Integration", optimizer_result))

    # Summary
    print("\n" + "=" * 80)
    print("🎉 BM1 BUILDER VERIFICATION SUMMARY")
    print("=" * 80)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(
        f"\nSUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
    )

    if success_rate == 100:
        print(
            "🎉 EXCELLENT - All Builder functionality continues working after BM1 frontend implementation"
        )
    elif success_rate >= 80:
        print("✅ GOOD - Most Builder functionality working, minor issues detected")
    else:
        print(
            "⚠️ ISSUES DETECTED - Builder functionality may be impacted by frontend changes"
        )

    print("=" * 80)

    return success_rate >= 80


if __name__ == "__main__":
    run_comprehensive_verification()
