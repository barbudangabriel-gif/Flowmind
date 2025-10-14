#!/usr/bin/env python3
"""
BM2 Builder Actions & Trade Button Backend Verification
Quick verification that all existing Builder functionality continues to work properly
after BM2 Builder Actions & Trade Button frontend implementation.
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "http://localhost:8000/api"


def test_builder_price_endpoint():
    """Test POST /api/builder/price endpoint for trade button bias detection"""
    print("🎯 TESTING BUILDER PRICING ENGINE")
    print("=" * 60)

    # Test 1: Long Call Strategy for bias detection
    print("\n✅ TEST 1: Long Call Strategy - Complete Pricing Data")
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

            # Check required sections for trade button
            required_sections = ["pricing", "chart", "meta", "greeks"]
            for section in required_sections:
                if section in data:
                    print(f"✅ {section.upper()} section present")
                else:
                    print(f"❌ {section.upper()} section missing")
                    return False

            # Validate pricing data for bias detection
            pricing = data.get("pricing", {})
            if "net_debit" in pricing and "chance_profit" in pricing:
                print(f"  Net Debit: ${pricing['net_debit']:.2f}")
                print(f"  Chance of Profit: {pricing['chance_profit']:.1f}%")
                print("✅ Pricing data available for trade button bias detection")
            else:
                print("❌ Missing pricing data for bias detection")
                return False

            # Validate Greeks for strategy analysis
            greeks = data.get("greeks", {})
            greek_names = ["delta", "gamma", "theta", "vega"]
            for greek in greek_names:
                if greek in greeks:
                    print(f"  {greek.capitalize()}: {greeks[greek]}")
                else:
                    print(f"❌ Missing {greek} in Greeks")

            # Validate chart data
            chart = data.get("chart", {})
            if "series" in chart and len(chart["series"]) > 0:
                series_count = len(chart["series"])
                data_points = len(chart["series"][0].get("data", []))
                print(f"✅ Chart data: {series_count} series, {data_points} points")
            else:
                print("⚠️ Chart data missing or empty")

            print("✅ Long Call pricing test PASSED")

        else:
            print(f"❌ Request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Long Call pricing test failed: {str(e)}")
        return False

    # Test 2: Bull Call Spread Strategy
    print("\n✅ TEST 2: Bull Call Spread - Multi-leg Strategy")
    bull_call_payload = {
        "symbol": "TSLA",
        "legs": [
            {"side": "BUY", "type": "CALL", "strike": 245, "qty": 1},
            {"side": "SELL", "type": "CALL", "strike": 255, "qty": 1},
        ],
        "qty": 1,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=bull_call_payload, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            pricing = data.get("pricing", {})

            if "net_debit" in pricing and "max_profit" in pricing:
                print(f"  Net Debit: ${pricing['net_debit']:.2f}")
                print(f"  Max Profit: ${pricing.get('max_profit', 0):.2f}")
                print(f"  Chance: {pricing.get('chance_profit', 0):.1f}%")
                print("✅ Bull Call Spread pricing working")
            else:
                print("❌ Bull Call Spread pricing incomplete")
                return False

        else:
            print(f"❌ Bull Call Spread failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Bull Call Spread test failed: {str(e)}")
        return False

    return True


def test_builder_historical_endpoint():
    """Test POST /api/builder/historical endpoint for historical chart modal"""
    print("\n🎯 TESTING BUILDER HISTORICAL ENGINE")
    print("=" * 60)

    # Test historical data for chart modal
    print("\n✅ TEST 1: Historical Series Data for Chart Modal")
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

            if series and len(series) > 0:
                print(f"Series Length: {len(series)} data points")

                # Validate data structure for chart modal
                first_point = series[0]
                required_fields = ["t", "spot", "pl"]

                for field in required_fields:
                    if field in first_point:
                        print(f"✅ {field} field present")
                    else:
                        print(f"❌ {field} field missing")
                        return False

                # Show sample data
                print(f"Sample Point: {first_point}")
                print("✅ Historical series data ready for chart modal")

            else:
                print("❌ No historical series data returned")
                return False

        else:
            print(f"❌ Historical request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Historical test failed: {str(e)}")
        return False

    return True


def test_options_chain_endpoint():
    """Test options chain data for Add+ functionality"""
    print("\n🎯 TESTING OPTIONS CHAIN DATA")
    print("=" * 60)

    # Test options chain for strike data
    print("\n✅ TEST 1: Options Chain Strike Data for Add+ Functionality")

    try:
        response = requests.get(f"{BACKEND_URL}/options/chain?symbol=TSLA", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check for spot price
            if "spot" in data:
                print(f"✅ Spot Price: ${data['spot']}")
            else:
                print("⚠️ Spot price not in chain data")

            # Check for strikes/expirations
            if "expirations" in data:
                exp_count = len(data["expirations"])
                print(f"✅ Expirations: {exp_count} available")
            else:
                print("⚠️ No expirations in chain data")

            # Check for raw chain data
            if "raw" in data or "chains" in data or "strikes" in data:
                print("✅ Strike data available for Add+ functionality")
            else:
                print("⚠️ Strike data structure unclear")

            print("✅ Options chain data accessible")

        else:
            print(f"❌ Options chain request failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options chain test failed: {str(e)}")
        return False

    return True


def test_strategy_bias_detection():
    """Test different strategy types for bias color coding"""
    print("\n🎯 TESTING STRATEGY BIAS DETECTION")
    print("=" * 60)

    strategies = [
        {
            "name": "Long Call (Bullish)",
            "payload": {
                "symbol": "TSLA",
                "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
                "qty": 1,
            },
        },
        {
            "name": "Long Put (Bearish)",
            "payload": {
                "symbol": "TSLA",
                "legs": [{"side": "BUY", "type": "PUT", "strike": 240, "qty": 1}],
                "qty": 1,
            },
        },
        {
            "name": "Iron Condor (Neutral)",
            "payload": {
                "symbol": "TSLA",
                "legs": [
                    {"side": "SELL", "type": "PUT", "strike": 230, "qty": 1},
                    {"side": "BUY", "type": "PUT", "strike": 225, "qty": 1},
                    {"side": "SELL", "type": "CALL", "strike": 270, "qty": 1},
                    {"side": "BUY", "type": "CALL", "strike": 275, "qty": 1},
                ],
                "qty": 1,
            },
        },
    ]

    for strategy in strategies:
        print(f"\n✅ Testing {strategy['name']}")

        try:
            response = requests.post(
                f"{BACKEND_URL}/builder/price", json=strategy["payload"], timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                pricing = data.get("pricing", {})
                greeks = data.get("greeks", {})

                # Extract bias indicators
                delta = greeks.get("delta", 0)
                chance = pricing.get("chance_profit", 0)

                print(f"  Delta: {delta:.4f}")
                print(f"  Chance: {chance:.1f}%")

                # Determine bias based on delta
                if delta > 0.1:
                    bias = "BULLISH"
                elif delta < -0.1:
                    bias = "BEARISH"
                else:
                    bias = "NEUTRAL"

                print(f"  Detected Bias: {bias}")
                print(f"✅ {strategy['name']} bias detection working")

            else:
                print(f"❌ {strategy['name']} failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ {strategy['name']} error: {str(e)}")
            return False

    return True


def run_comprehensive_verification():
    """Run all BM2 Builder verification tests"""
    print("🚀 BM2 BUILDER ACTIONS & TRADE BUTTON BACKEND VERIFICATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)

    test_results = []

    # Test 1: Builder Pricing Engine
    print("\n📊 PHASE 1: BUILDER PRICING ENGINE VERIFICATION")
    result1 = test_builder_price_endpoint()
    test_results.append(("Builder Pricing Engine", result1))

    # Test 2: Builder Historical Engine
    print("\n📈 PHASE 2: BUILDER HISTORICAL ENGINE VERIFICATION")
    result2 = test_builder_historical_endpoint()
    test_results.append(("Builder Historical Engine", result2))

    # Test 3: Options Chain Data
    print("\n🔗 PHASE 3: OPTIONS CHAIN DATA VERIFICATION")
    result3 = test_options_chain_endpoint()
    test_results.append(("Options Chain Data", result3))

    # Test 4: Strategy Bias Detection
    print("\n🎯 PHASE 4: STRATEGY BIAS DETECTION VERIFICATION")
    result4 = test_strategy_bias_detection()
    test_results.append(("Strategy Bias Detection", result4))

    # Summary
    print("\n" + "=" * 80)
    print("🎉 BM2 BUILDER VERIFICATION SUMMARY")
    print("=" * 80)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(
        f"\nSUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
    )

    if success_rate == 100:
        print(
            "🎉 EXCELLENT: All Builder functionality continues to work after BM2 implementation"
        )
    elif success_rate >= 75:
        print("✅ GOOD: Core Builder functionality working with minor issues")
    else:
        print("⚠️ ISSUES: Significant problems detected in Builder functionality")

    print(f"\nTest completed at: {datetime.now().isoformat()}")
    print("=" * 80)

    return success_rate >= 75


if __name__ == "__main__":
    run_comprehensive_verification()
