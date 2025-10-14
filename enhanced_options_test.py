#!/usr/bin/env python3
"""
Enhanced Options Optimizer (OZ2/6) and Builder Backend (B1/6) Testing
Testing the enhanced Options Optimizer with EV scoring, liquidity checks, deep-linking,
and the Builder pricing engine with Black-Scholes calculations.
"""

import requests
import json
import time

# Use the external URL from frontend/.env
BASE_URL = "http://localhost:8000/api"


def test_enhanced_optimize_endpoint():
    """Test the enhanced optimize endpoint with EV scoring and deep-links"""
    print("🎯 Testing Enhanced Optimize Endpoint...")

    # Test 1: Basic TSLA optimization with enhanced features
    url = f"{BASE_URL}/optimize/suggest"
    params = {"symbol": "TSLA", "dte": 30, "budget": 5000, "risk_bias": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Validate response structure
            assert "meta" in data, "Missing meta section"
            assert "strategies" in data, "Missing strategies section"

            meta = data["meta"]
            strategies = data["strategies"]

            print(f"   ✅ Symbol: {meta.get('symbol')}")
            print(f"   ✅ Spot Price: ${meta.get('spot')}")
            print(f"   ✅ IV: {meta.get('iv', 0)*100:.1f}%")
            print(f"   ✅ Strategies Count: {len(strategies)}")

            # Test enhanced features in each strategy
            for i, strategy in enumerate(strategies):
                print(f"\n   Strategy {i+1}: {strategy.get('label')}")

                # Check for deep-link field
                assert (
                    "open_in_builder" in strategy
                ), f"Missing open_in_builder field in strategy {i+1}"
                deep_link = strategy["open_in_builder"]
                print(f"   ✅ Deep-link: {deep_link}")

                # Validate deep-link format (should be base64-encoded)
                assert deep_link.startswith(
                    "/build/"
                ), "Deep-link should start with /build/"
                assert (
                    "s=" in deep_link
                ), "Deep-link should contain base64 strategy data"

                # Check EV-based ROI calculations
                roi = strategy.get("roi", 0)
                chance = strategy.get("chance", 0)
                print(f"   ✅ ROI (EV-based): {roi*100:.2f}%")
                print(f"   ✅ Chance of Profit: {chance*100:.2f}%")

                # Validate required fields
                required_fields = ["id", "label", "roi", "chance", "legs", "mini"]
                for field in required_fields:
                    assert field in strategy, f"Missing {field} in strategy {i+1}"

                # Check legs structure
                legs = strategy["legs"]
                assert isinstance(legs, list), "Legs should be a list"
                for leg in legs:
                    assert "side" in leg, "Leg missing side"
                    assert "type" in leg, "Leg missing type"
                    assert "strike" in leg, "Leg missing strike"
                    assert leg["side"] in [
                        "BUY",
                        "SELL",
                    ], f"Invalid side: {leg['side']}"
                    assert leg["type"] in [
                        "CALL",
                        "PUT",
                    ], f"Invalid type: {leg['type']}"

            print("   ✅ Enhanced Optimize Endpoint: PASSED")
            return True

        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_builder_pricing_engine():
    """Test the Builder pricing engine with Black-Scholes calculations"""
    print("\n🏗️ Testing Builder Pricing Engine...")

    # Test 1: Long Call pricing
    print("\n   Test 1: Long Call Pricing")
    url = f"{BASE_URL}/builder/price"
    payload = {
        "symbol": "TSLA",
        "expiry": "2025-09-26",
        "dte": 27,
        "legs": [{"side": "BUY", "type": "CALL", "qty": 1, "strike": 240}],
        "iv_mult": 1,
        "range_pct": 0.12,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Validate response structure
            required_sections = ["meta", "pricing", "chart", "greeks"]
            for section in required_sections:
                assert section in data, f"Missing {section} section"

            meta = data["meta"]
            pricing = data["pricing"]
            chart = data["chart"]
            greeks = data["greeks"]

            print(f"   ✅ Symbol: {meta.get('symbol')}")
            print(f"   ✅ Spot: ${meta.get('spot')}")
            print(f"   ✅ IV Effective: {meta.get('iv_eff', 0)*100:.1f}%")
            print(f"   ✅ DTE: {meta.get('dte')}")

            # Check pricing calculations
            print(f"   ✅ Net Debit: ${pricing.get('net_debit')}")
            print(f"   ✅ Max Loss: ${pricing.get('max_loss')}")
            print(f"   ✅ Chance of Profit: {pricing.get('chance_profit', 0)*100:.2f}%")

            # Validate breakevens
            breakevens = pricing.get("breakevens", [])
            print(f"   ✅ Breakevens: {breakevens}")
            assert isinstance(breakevens, list), "Breakevens should be a list"

            # Check chart data
            assert "series" in chart, "Missing chart series"
            assert "prob" in chart, "Missing probability data"
            series = chart["series"][0]
            assert "xy" in series, "Missing XY data in chart"
            print(f"   ✅ Chart points: {len(series['xy'])}")

            # Check Greeks
            delta = greeks.get("delta", 0)
            print(f"   ✅ Delta: {delta:.4f}")
            assert -1 <= delta <= 1, f"Delta out of range: {delta}"

            print("   ✅ Long Call Pricing: PASSED")

        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

    # Test 2: Bull Call Spread pricing
    print("\n   Test 2: Bull Call Spread Pricing")
    payload2 = {
        "symbol": "TSLA",
        "expiry": "2025-09-26",
        "dte": 27,
        "legs": [
            {"side": "BUY", "type": "CALL", "qty": 1, "strike": 250},
            {"side": "SELL", "type": "CALL", "qty": 1, "strike": 285},
        ],
        "iv_mult": 1.2,
        "range_pct": 0.15,
    }

    try:
        response = requests.post(url, json=payload2, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            pricing = data["pricing"]
            meta = data["meta"]

            print(f"   ✅ Net Debit: ${pricing.get('net_debit')}")
            print(f"   ✅ Max Profit: ${pricing.get('max_profit')}")
            print(f"   ✅ Max Loss: ${pricing.get('max_loss')}")
            print(f"   ✅ Chance of Profit: {pricing.get('chance_profit', 0)*100:.2f}%")

            # Validate spread characteristics
            net_debit = pricing.get("net_debit", 0)
            max_profit = pricing.get("max_profit")

            # For bull call spread, max profit should be limited
            if max_profit is not None:
                assert (
                    max_profit > 0
                ), "Bull call spread should have positive max profit"
                print(f"   ✅ Limited max profit confirmed: ${max_profit}")

            # Check that we have 2 breakevens or 1 (depending on spread)
            breakevens = pricing.get("breakevens", [])
            print(f"   ✅ Breakevens: {breakevens}")

            print("   ✅ Bull Call Spread Pricing: PASSED")
            return True

        else:
            print(f"   ❌ Request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_deep_link_integration():
    """Test deep-link integration between Optimize and Builder"""
    print("\n🔗 Testing Deep-Link Integration...")

    # Step 1: Get strategies from Optimize
    optimize_url = f"{BASE_URL}/optimize/suggest"
    params = {"symbol": "TSLA", "dte": 30, "budget": 5000, "risk_bias": 0}

    try:
        response = requests.get(optimize_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            strategies = data["strategies"]

            if strategies:
                # Take the first strategy and extract deep-link data
                strategy = strategies[0]
                deep_link = strategy["open_in_builder"]

                print(f"   ✅ Got deep-link: {deep_link}")

                # Parse the deep-link to extract strategy data
                import urllib.parse
                import base64

                # Extract query parameters
                if "?" in deep_link:
                    query_part = deep_link.split("?")[1]
                    params = urllib.parse.parse_qs(query_part)

                    symbol = params.get("symbol", [""])[0]
                    expiry = params.get("expiry", [""])[0]
                    s_param = params.get("s", [""])[0]

                    print(f"   ✅ Parsed symbol: {symbol}")
                    print(f"   ✅ Parsed expiry: {expiry}")

                    # Decode base64 strategy data
                    if s_param:
                        # Add padding if needed
                        padding = "=" * (-len(s_param) % 4)
                        decoded_bytes = base64.urlsafe_b64decode(
                            (s_param + padding).encode()
                        )
                        strategy_data = json.loads(decoded_bytes.decode())

                        print(f"   ✅ Decoded strategy data: {strategy_data}")

                        # Step 2: Use decoded data to price in Builder
                        builder_payload = {
                            "symbol": symbol,
                            "expiry": expiry,
                            "dte": 30,
                            "legs": strategy_data["legs"],
                            "qty": strategy_data.get("qty", 1),
                            "iv_mult": 1,
                            "range_pct": 0.12,
                        }

                        builder_url = f"{BASE_URL}/builder/price"
                        builder_response = requests.post(
                            builder_url, json=builder_payload, timeout=10
                        )

                        if builder_response.status_code == 200:
                            builder_data = builder_response.json()
                            print("   ✅ Builder successfully priced the strategy")
                            print(
                                f"   ✅ Net Debit: ${builder_data['pricing'].get('net_debit')}"
                            )
                            print(
                                f"   ✅ Chance of Profit: {builder_data['pricing'].get('chance_profit', 0)*100:.2f}%"
                            )

                            print("   ✅ Deep-Link Integration: PASSED")
                            return True
                        else:
                            print(
                                f"   ❌ Builder pricing failed: {builder_response.status_code}"
                            )
                            return False
                    else:
                        print("   ❌ No strategy data in deep-link")
                        return False
                else:
                    print("   ❌ Invalid deep-link format")
                    return False
            else:
                print("   ❌ No strategies returned from optimize")
                return False
        else:
            print(f"   ❌ Optimize request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_data_structure_validation():
    """Test data structure validation for both endpoints"""
    print("\n📊 Testing Data Structure Validation...")

    # Test Optimize data structure
    print("\n   Testing Optimize Data Structure...")
    optimize_url = f"{BASE_URL}/optimize/suggest"
    params = {"symbol": "AAPL", "dte": 45, "budget": 10000}

    try:
        response = requests.get(optimize_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Validate meta section
            meta = data["meta"]
            required_meta = ["symbol", "spot", "dte", "expiry", "iv", "rf"]
            for field in required_meta:
                assert field in meta, f"Missing {field} in meta"

            # Validate strategies
            strategies = data["strategies"]
            for strategy in strategies:
                # Check for open_in_builder field
                assert "open_in_builder" in strategy, "Missing open_in_builder field"

                # Validate numeric fields are in reasonable ranges
                roi = strategy.get("roi", 0)
                chance = strategy.get("chance", 0)

                assert -5 <= roi <= 20, f"ROI out of reasonable range: {roi}"
                assert 0 <= chance <= 1, f"Chance out of range [0,1]: {chance}"

                # Check breakevens are realistic price levels
                breakevens = strategy.get("breakevens", [])
                spot = meta["spot"]
                for be in breakevens:
                    assert (
                        0.5 * spot <= be <= 2 * spot
                    ), f"Breakeven {be} unrealistic for spot {spot}"

            print("   ✅ Optimize data structure validation: PASSED")

        else:
            print(f"   ❌ Optimize request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Optimize validation error: {str(e)}")
        return False

    # Test Builder data structure
    print("\n   Testing Builder Data Structure...")
    builder_url = f"{BASE_URL}/builder/price"
    payload = {
        "symbol": "AAPL",
        "expiry": "2025-10-17",
        "dte": 30,
        "legs": [{"side": "BUY", "type": "CALL", "qty": 1, "strike": 200}],
        "iv_mult": 1,
        "range_pct": 0.12,
    }

    try:
        response = requests.post(builder_url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Validate all required sections
            required_sections = ["meta", "pricing", "chart", "greeks"]
            for section in required_sections:
                assert section in data, f"Missing {section} section"

            # Validate pricing section
            pricing = data["pricing"]
            chance_profit = pricing.get("chance_profit", 0)
            assert (
                0 <= chance_profit <= 1
            ), f"Chance of profit out of range: {chance_profit}"

            # Validate chart section
            chart = data["chart"]
            assert "series" in chart, "Missing chart series"
            assert "prob" in chart, "Missing probability data"

            series = chart["series"][0]
            xy_data = series["xy"]
            assert len(xy_data) > 100, "Chart should have sufficient data points"

            # Validate Greeks
            greeks = data["greeks"]
            delta = greeks.get("delta", 0)
            assert -10 <= delta <= 10, f"Delta out of reasonable range: {delta}"

            print("   ✅ Builder data structure validation: PASSED")
            return True

        else:
            print(f"   ❌ Builder request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Builder validation error: {str(e)}")
        return False


def main():
    """Run all enhanced Options Optimizer and Builder tests"""
    print("🚀 Enhanced Options Optimizer (OZ2/6) and Builder Backend (B1/6) Testing")
    print("=" * 80)

    start_time = time.time()
    tests_passed = 0
    total_tests = 4

    # Run all tests
    if test_enhanced_optimize_endpoint():
        tests_passed += 1

    if test_builder_pricing_engine():
        tests_passed += 1

    if test_deep_link_integration():
        tests_passed += 1

    if test_data_structure_validation():
        tests_passed += 1

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("🎯 ENHANCED OPTIONS TESTING SUMMARY")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {tests_passed/total_tests*100:.1f}%")
    print(f"Execution Time: {elapsed:.2f}s")

    if tests_passed == total_tests:
        print(
            "✅ ALL TESTS PASSED - Enhanced Options system ready for frontend integration!"
        )
    else:
        print("❌ SOME TESTS FAILED - Review issues above")

    return tests_passed == total_tests


if __name__ == "__main__":
    main()
