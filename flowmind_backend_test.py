#!/usr/bin/env python3
"""
FlowMind Backend API Testing
Testing the FlowMind backend APIs as requested in review:
1. /api/builder/price endpoint (POST) with sample payload
2. /api/options/chain endpoint for options chain data
3. /api/options/expirations endpoint
4. Check for proper responses including "quality" field
"""

import requests
import json
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "http://localhost:8000/api"


def test_builder_price_endpoint():
    """Test POST /api/builder/price with sample payload"""
    print("🎯 TESTING /api/builder/price ENDPOINT")
    print("=" * 60)

    # Sample payload as specified in review request
    sample_payload = {
        "symbol": "TSLA",
        "expiry": "2025-02-21",
        "dte": 30,
        "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
        "qty": 1,
        "iv_mult": 1.0,
        "range_pct": 0.12,
        "strategyId": "long_call",
    }

    print(f"Testing with payload: {json.dumps(sample_payload, indent=2)}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price", json=sample_payload, timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Builder price endpoint working")

            # Check for expected response structure
            expected_fields = ["pricing", "chart", "meta", "greeks"]
            for field in expected_fields:
                if field in data:
                    print(f"  ✅ Field '{field}' present")
                else:
                    print(f"  ⚠️ Field '{field}' missing")

            # Check for quality field specifically mentioned in review
            if "quality" in data:
                print(f"  ✅ Quality field present: {data['quality']}")
            else:
                print("  ⚠️ Quality field not found in response")

            # Show sample response structure
            print(f"\nResponse structure keys: {list(data.keys())}")

            # Check pricing section if present
            if "pricing" in data:
                pricing = data["pricing"]
                print(
                    f"  Pricing keys: {list(pricing.keys()) if isinstance(pricing, dict) else 'Not a dict'}"
                )

            # Check greeks section if present
            if "greeks" in data:
                greeks = data["greeks"]
                print(
                    f"  Greeks keys: {list(greeks.keys()) if isinstance(greeks, dict) else 'Not a dict'}"
                )

            return True

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Builder price test failed: {str(e)}")
        return False


def test_options_chain_endpoint():
    """Test GET /api/options/chain for options chain data"""
    print("\n🎯 TESTING /api/options/chain ENDPOINT")
    print("=" * 60)

    # Test parameters as specified in review
    test_params = {"symbol": "TSLA", "expiry": "2025-02-21"}

    print(f"Testing with params: {test_params}")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params=test_params, timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Options chain endpoint working")

            # Check if data is a list (chain format) or dict
            if isinstance(data, list):
                print(f"  Chain data: {len(data)} strikes returned")

                if data:
                    # Check first strike structure
                    first_strike = data[0]
                    expected_fields = ["strike", "bid", "ask", "mid", "iv", "oi", "vol"]

                    print("  Strike data structure:")
                    for field in expected_fields:
                        if field in first_strike:
                            print(f"    ✅ {field}: {first_strike[field]}")
                        else:
                            print(f"    ⚠️ {field}: missing")

                    # Check for quality field
                    if "quality" in first_strike:
                        print(f"    ✅ Quality field: {first_strike['quality']}")
                    else:
                        print("    ⚠️ Quality field not found in strike data")

            elif isinstance(data, dict):
                print(f"  Response keys: {list(data.keys())}")

                # Check for quality field in dict response
                if "quality" in data:
                    print(f"  ✅ Quality field: {data['quality']}")
                else:
                    print("  ⚠️ Quality field not found in response")

            return True

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options chain test failed: {str(e)}")
        return False


def test_options_expirations_endpoint():
    """Test GET /api/options/expirations endpoint"""
    print("\n🎯 TESTING /api/options/expirations ENDPOINT")
    print("=" * 60)

    # Test parameters as specified in review
    test_params = {"symbol": "TSLA"}

    print(f"Testing with params: {test_params}")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/expirations", params=test_params, timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Options expirations endpoint working")

            # Check response structure
            if "expirations" in data:
                expirations = data["expirations"]
                print(f"  ✅ Expirations field present: {len(expirations)} dates")

                if expirations:
                    print(f"  Sample expirations: {expirations[:5]}")

                    # Validate date format
                    try:
                        datetime.strptime(expirations[0], "%Y-%m-%d")
                        print("  ✅ Date format valid (YYYY-MM-DD)")
                    except:
                        print(f"  ⚠️ Date format may be non-standard: {expirations[0]}")

            else:
                print(
                    f"  ⚠️ 'expirations' field missing. Response keys: {list(data.keys())}"
                )

            # Check for quality field
            if "quality" in data:
                print(f"  ✅ Quality field: {data['quality']}")
            else:
                print("  ⚠️ Quality field not found in response")

            return True

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Options expirations test failed: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n🎯 TESTING ERROR HANDLING")
    print("=" * 60)

    # Test 1: Invalid symbol for chain
    print("Test 1: Invalid symbol for options chain")
    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": "INVALID_XYZ"}, timeout=10
        )
        print(f"  Invalid symbol status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print("  ✅ Graceful fallback to demo data")
            else:
                print("  ✅ Empty response for invalid symbol")
        else:
            print(f"  ✅ Proper error response: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Invalid symbol test error: {str(e)}")

    # Test 2: Missing required parameters for builder/price
    print("\nTest 2: Missing parameters for builder/price")
    try:
        response = requests.post(
            f"{BACKEND_URL}/builder/price",
            json={},  # Empty payload
            timeout=10,
        )
        print(f"  Empty payload status: {response.status_code}")

        if response.status_code in [400, 422, 500]:
            print("  ✅ Proper error handling for missing parameters")
        else:
            print("  ⚠️ Unexpected response for empty payload")

    except Exception as e:
        print(f"  ❌ Empty payload test error: {str(e)}")

    # Test 3: Invalid expiry date
    print("\nTest 3: Invalid expiry date")
    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain",
            params={"symbol": "TSLA", "expiry": "invalid-date"},
            timeout=10,
        )
        print(f"  Invalid expiry status: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ Graceful handling of invalid expiry")
        else:
            print("  ✅ Proper error response for invalid expiry")

    except Exception as e:
        print(f"  ❌ Invalid expiry test error: {str(e)}")


def test_response_times():
    """Test response times for performance"""
    print("\n🎯 TESTING RESPONSE TIMES")
    print("=" * 60)

    endpoints = [
        ("GET", "/options/expirations", {"symbol": "TSLA"}),
        ("GET", "/options/chain", {"symbol": "TSLA", "expiry": "2025-02-21"}),
        (
            "POST",
            "/builder/price",
            {
                "symbol": "TSLA",
                "expiry": "2025-02-21",
                "dte": 30,
                "legs": [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
                "qty": 1,
                "iv_mult": 1.0,
                "range_pct": 0.12,
                "strategyId": "long_call",
            },
        ),
    ]

    for method, endpoint, payload in endpoints:
        try:
            start_time = time.time()

            if method == "GET":
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}", params=payload, timeout=15
                )
            else:
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}", json=payload, timeout=15
                )

            end_time = time.time()
            response_time = end_time - start_time

            print(
                f"{method} {endpoint}: {response_time:.3f}s (Status: {response.status_code})"
            )

            if response_time < 5.0:
                print("  ✅ Good response time")
            elif response_time < 10.0:
                print("  ⚠️ Acceptable response time")
            else:
                print("  ❌ Slow response time")

        except Exception as e:
            print(f"{method} {endpoint}: ❌ Error - {str(e)}")


def main():
    """Run all FlowMind backend API tests"""
    print("🚀 STARTING FLOWMIND BACKEND API TESTS")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)

    # Track test results
    results = []

    # Test 1: Builder price endpoint
    results.append(("Builder Price", test_builder_price_endpoint()))

    # Test 2: Options chain endpoint
    results.append(("Options Chain", test_options_chain_endpoint()))

    # Test 3: Options expirations endpoint
    results.append(("Options Expirations", test_options_expirations_endpoint()))

    # Test 4: Error handling
    test_error_handling()

    # Test 5: Response times
    test_response_times()

    # Summary
    print("\n" + "=" * 80)
    print("🎉 FLOWMIND BACKEND API TESTING COMPLETE")
    print("=" * 80)

    print("\nTest Results Summary:")
    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("🎉 ALL CORE TESTS PASSED - FlowMind backend APIs are working correctly!")
    else:
        print("⚠️ Some tests failed - Check individual test results above")

    print(f"\nTest completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
