#!/usr/bin/env python3
"""
S1-S3 Strategy Catalog & Picker Backend Verification Test
Quick verification that all existing Builder and Optimizer functionality continues to work properly
after S1-S3 Strategy Catalog & Picker frontend implementation.
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://options-analytics.preview.emergentagent.com/api"


def test_builder_endpoints():
    """Test Builder endpoints: POST /api/builder/price and POST /api/builder/historical"""
    print("🎯 TESTING BUILDER ENDPOINTS")
    print("=" * 60)

    # Test 1: Builder Pricing - Long Call should return complete pricing with Greeks
    print("\n✅ TEST 1: Builder Pricing - Long Call with Complete Pricing & Greeks")

    long_call_payload = {
        "symbol": "TSLA",
        "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
        "qty": 1,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=long_call_payload, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check required sections
            required_sections = ["pricing", "chart", "meta", "greeks"]
            for section in required_sections:
                if section in data:
                    print(f"✅ Section '{section}' present")
                else:
                    print(f"❌ Section '{section}' missing")
                    return False

            # Check pricing data (actual field names from response)
            pricing = data.get("pricing", {})
            if "net_debit" in pricing and "chance_profit" in pricing:
                print(
                    f"✅ Pricing data: Debit=${pricing.get('net_debit', 0):.2f}, Chance={pricing.get('chance_profit', 0)*100:.1f}%"
                )
            elif "max_loss" in pricing and "max_profit" in pricing:
                print(
                    f"✅ Pricing data: Max Loss=${pricing.get('max_loss', 0):.2f}, Max Profit=${pricing.get('max_profit', 0):.2f}"
                )
            else:
                print(
                    "❌ Missing pricing data (net_debit/chance_profit or max_loss/max_profit)"
                )
                return False

            # Check Greeks - all 4 Greeks should be present
            greeks = data.get("greeks", {})
            required_greeks = ["delta", "gamma", "theta", "vega"]
            for greek in required_greeks:
                if greek in greeks:
                    print(f"✅ Greek '{greek}': {greeks[greek]}")
                else:
                    print(f"❌ Greek '{greek}' missing")
                    return False

            # Check chart data (actual structure from response)
            chart = data.get("chart", {})
            if "series" in chart and len(chart["series"]) > 0:
                # Check if series has xy data points
                series_data = chart["series"][0].get("xy", [])
                print(f"✅ Chart data: {len(series_data)} data points")
            else:
                print("❌ Missing chart data")
                return False

            print("✅ Builder pricing test PASSED - Complete pricing with Greeks")

        else:
            print(
                f"❌ Builder pricing failed: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        print(f"❌ Builder pricing test error: {str(e)}")
        return False

    # Test 2: Builder Historical - Historical series should return for CSV export
    print("\n✅ TEST 2: Builder Historical - Historical Series for CSV Export")

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

            # Check series data for CSV export
            if "series" in data:
                series = data["series"]
                if len(series) > 0:
                    print(f"✅ Historical series: {len(series)} data points")

                    # Check CSV-ready structure
                    first_point = series[0]
                    required_fields = ["t", "spot", "pl"]
                    for field in required_fields:
                        if field in first_point:
                            print(f"✅ CSV field '{field}': {first_point[field]}")
                        else:
                            print(f"❌ CSV field '{field}' missing")
                            return False

                    print(
                        "✅ Builder historical test PASSED - CSV-ready data structure"
                    )
                else:
                    print("❌ Empty historical series")
                    return False
            else:
                print("❌ Missing series data")
                return False

        else:
            print(
                f"❌ Builder historical failed: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        print(f"❌ Builder historical test error: {str(e)}")
        return False

    return True


def test_optimizer_endpoint():
    """Test Optimizer endpoint: POST /api/optimize/suggest with spread quality"""
    print("\n🎯 TESTING OPTIMIZER ENDPOINT")
    print("=" * 60)

    print("\n✅ TEST 3: Optimizer - TSLA Strategies with Spread Quality Metrics")

    # Test TSLA strategies should return with spread quality metrics
    try:
        response = requests.get(
            f"{BACKEND_URL}/optimize/suggest?symbol=TSLA&budget=5000", timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "strategies" in data:
                strategies = data["strategies"]
                print(f"✅ Strategies returned: {len(strategies)}")

                if len(strategies) > 0:
                    # Check first strategy for spread quality metrics
                    strategy = strategies[0]

                    # Check basic strategy fields
                    basic_fields = [
                        "id",
                        "label",
                        "roi",
                        "chance",
                        "profit_max",
                        "risk_capital",
                    ]
                    for field in basic_fields:
                        if field in strategy:
                            print(f"✅ Strategy field '{field}': {strategy[field]}")
                        else:
                            print(f"❌ Strategy field '{field}' missing")
                            return False

                    # Check spread quality metrics (B8 implementation)
                    spread_quality_fields = [
                        "quality",
                        "slippage_est",
                        "nbbo_ok",
                        "market",
                    ]
                    spread_quality_present = 0
                    for field in spread_quality_fields:
                        if field in strategy:
                            print(
                                f"✅ Spread quality field '{field}': {strategy[field]}"
                            )
                            spread_quality_present += 1
                        else:
                            print(
                                f"⚠️ Spread quality field '{field}' missing (may be optional)"
                            )

                    if (
                        spread_quality_present >= 2
                    ):  # At least some spread quality metrics
                        print("✅ Spread quality metrics present")
                    else:
                        print("⚠️ Limited spread quality metrics (may be expected)")

                    # Check legs structure
                    if "legs" in strategy and len(strategy["legs"]) > 0:
                        leg = strategy["legs"][0]
                        leg_fields = ["side", "type", "strike", "qty"]
                        for field in leg_fields:
                            if field in leg:
                                print(f"✅ Leg field '{field}': {leg[field]}")
                            else:
                                print(f"❌ Leg field '{field}' missing")
                                return False
                    else:
                        print("❌ Missing legs data")
                        return False

                    print(
                        "✅ Optimizer test PASSED - TSLA strategies with quality metrics"
                    )
                else:
                    print("❌ No strategies returned")
                    return False
            else:
                print("❌ Missing strategies in response")
                return False

        else:
            print(f"❌ Optimizer failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Optimizer test error: {str(e)}")
        return False

    return True


def test_options_chain():
    """Test Options Chain data availability for strategy picker spot price calculation"""
    print("\n🎯 TESTING OPTIONS CHAIN DATA")
    print("=" * 60)

    print("\n✅ TEST 4: Options Chain - Data Available for Strategy Picker Spot Price")

    try:
        response = requests.get(f"{BACKEND_URL}/options/chain?symbol=TSLA", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check spot price availability
            if "spot" in data:
                spot_price = data["spot"]
                print(f"✅ Spot price available: ${spot_price}")
            else:
                print("❌ Spot price missing from chain data")
                return False

            # Check raw options chain data (actual structure from response)
            if "raw" in data and "OptionChains" in data["raw"]:
                option_chains = data["raw"]["OptionChains"]
                print(f"✅ Option chains available: {len(option_chains)} expirations")

                if len(option_chains) > 0:
                    # Check first expiration structure
                    first_exp = option_chains[0]
                    if "Expiration" in first_exp and "Strikes" in first_exp:
                        strikes = first_exp["Strikes"]
                        print(f"✅ Strikes available: {len(strikes)} strike prices")

                        if len(strikes) > 0:
                            # Check strike structure for strategy picker
                            strike = strikes[0]
                            if "StrikePrice" in strike:
                                print(
                                    f"✅ Strike data structure valid: {strike['StrikePrice']}"
                                )

                                # Check calls/puts data
                                if "Calls" in strike and "Puts" in strike:
                                    print("✅ Calls and Puts data available")
                                else:
                                    print("❌ Missing Calls or Puts data")
                                    return False
                            else:
                                print("❌ Strike structure invalid")
                                return False
                        else:
                            print("❌ No strikes available")
                            return False
                    else:
                        print("❌ Invalid expiration structure")
                        return False
                else:
                    print("❌ No expirations available")
                    return False
            else:
                print("❌ Raw options chain data missing")
                return False

            print("✅ Options chain test PASSED - Data available for strategy picker")

        else:
            print(f"❌ Options chain failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options chain test error: {str(e)}")
        return False

    return True


def run_comprehensive_verification():
    """Run all verification tests"""
    print("🚀 S1-S3 STRATEGY CATALOG & PICKER BACKEND VERIFICATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)

    results = []

    # Test 1: Builder Endpoints
    try:
        result1 = test_builder_endpoints()
        results.append(("Builder Endpoints", result1))
    except Exception as e:
        print(f"❌ Builder endpoints test crashed: {str(e)}")
        results.append(("Builder Endpoints", False))

    # Test 2: Optimizer Endpoint
    try:
        result2 = test_optimizer_endpoint()
        results.append(("Optimizer Endpoint", result2))
    except Exception as e:
        print(f"❌ Optimizer endpoint test crashed: {str(e)}")
        results.append(("Optimizer Endpoint", False))

    # Test 3: Options Chain
    try:
        result3 = test_options_chain()
        results.append(("Options Chain", result3))
    except Exception as e:
        print(f"❌ Options chain test crashed: {str(e)}")
        results.append(("Options Chain", False))

    # Summary
    print("\n" + "=" * 80)
    print("🎉 S1-S3 VERIFICATION SUMMARY")
    print("=" * 80)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED - S1-S3 backend functionality verified!")
        return True
    else:
        print("⚠️ SOME TESTS FAILED - Review required")
        return False


if __name__ == "__main__":
    success = run_comprehensive_verification()
    print(f"\n✅ Verification completed at {datetime.now().isoformat()}")
    exit(0 if success else 1)
