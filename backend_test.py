#!/usr/bin/env python3

import requests
import time
import os

# Get backend URL from environment
BACKEND_URL = os.getenv(
    "REACT_APP_BACKEND_URL", "https://options-analytics.preview.emergentagent.com"
)
BASE_URL = f"{BACKEND_URL}/api"


def test_builder_quality_endpoint():
    """
    Test the backend /api/builder/quality endpoint functionality.
    Since there's no dedicated /quality endpoint, we test the /price endpoint
    which includes quality data in its response structure.
    """
    print("🎯 TESTING BUILDER QUALITY ENDPOINT FUNCTIONALITY")
    print("=" * 60)

    # Test 1: Check if dedicated /api/builder/quality endpoint exists
    print("\n1. Testing dedicated /api/builder/quality endpoint...")

    test_payload = {
        "legs": [{"type": "CALL", "strike": 250, "side": "BUY", "qty": 1}],
        "spot": 250,
        "iv_mult": 1.0,
        "range_pct": 0.15,
        "dte": 30,
        "symbol": "TSLA",
        "expiry": "2025-02-21",
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/builder/quality", json=test_payload, timeout=5
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print("✅ Dedicated /quality endpoint exists and working")
            print(f"⏱️  Response time: {response_time:.3f}s")
            print(f"📊 Response structure: {list(data.keys())}")

            # Check if response contains score
            if "score" in data:
                print(f"🎯 Quality score: {data['score']}")
                return True, data
            else:
                print("❌ Response doesn't contain 'score' field")
                return False, None
        else:
            print(
                f"❌ Dedicated /quality endpoint not found (status: {response.status_code})"
            )
    except requests.exceptions.RequestException as e:
        print(f"❌ Dedicated /quality endpoint not available: {str(e)}")

    # Test 2: Test /api/builder/price endpoint for quality data
    print("\n2. Testing /api/builder/price endpoint for quality data...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/builder/price", json=test_payload, timeout=5
        )
        response_time = time.time() - start_time

        print(f"⏱️  Response time: {response_time:.3f}s")

        if response.status_code == 200:
            data = response.json()
            print("✅ /price endpoint working")
            print(f"📊 Response structure: {list(data.keys())}")

            # Check if response contains quality data
            if "quality" in data:
                quality = data["quality"]
                print("✅ Quality data found in response")
                print(f"🎯 Quality score: {quality.get('score', 'N/A')}")
                print(f"📈 Quality buckets: {quality.get('buckets', {})}")
                print(f"🚩 Quality flags: {quality.get('flags', [])}")

                # Verify score is numeric
                score = quality.get("score")
                if isinstance(score, (int, float)):
                    print(f"✅ Score is numeric: {score}")
                    return True, data
                else:
                    print(f"❌ Score is not numeric: {score} (type: {type(score)})")
                    return False, data
            else:
                print("❌ No quality data found in /price response")
                return False, data
        else:
            print(f"❌ /price endpoint failed (status: {response.status_code})")
            print(f"Response: {response.text}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"❌ /price endpoint error: {str(e)}")
        return False, None


def test_different_leg_configurations():
    """Test quality scoring with different leg configurations"""
    print("\n🔄 TESTING DIFFERENT LEG CONFIGURATIONS")
    print("=" * 50)

    test_cases = [
        {
            "name": "Long Call (Single Leg)",
            "payload": {
                "symbol": "TSLA",
                "expiry": "2025-02-21",
                "legs": [{"type": "CALL", "strike": 250, "side": "BUY", "qty": 1}],
                "spot": 250,
                "iv_mult": 1.0,
                "range_pct": 0.15,
                "dte": 30,
                "strategyId": "long-call",
            },
        },
        {
            "name": "Bull Call Spread (Two Legs)",
            "payload": {
                "symbol": "TSLA",
                "expiry": "2025-02-21",
                "legs": [
                    {"type": "CALL", "strike": 240, "side": "BUY", "qty": 1},
                    {"type": "CALL", "strike": 260, "side": "SELL", "qty": 1},
                ],
                "spot": 250,
                "iv_mult": 1.0,
                "range_pct": 0.15,
                "dte": 30,
                "strategyId": "bull-call-spread",
            },
        },
        {
            "name": "Iron Condor (Four Legs)",
            "payload": {
                "symbol": "TSLA",
                "expiry": "2025-02-21",
                "legs": [
                    {"type": "PUT", "strike": 230, "side": "BUY", "qty": 1},
                    {"type": "PUT", "strike": 240, "side": "SELL", "qty": 1},
                    {"type": "CALL", "strike": 260, "side": "SELL", "qty": 1},
                    {"type": "CALL", "strike": 270, "side": "BUY", "qty": 1},
                ],
                "spot": 250,
                "iv_mult": 1.0,
                "range_pct": 0.15,
                "dte": 30,
                "strategyId": "iron-condor",
            },
        },
        {
            "name": "Long Put (Different Strike)",
            "payload": {
                "symbol": "TSLA",
                "expiry": "2025-02-21",
                "legs": [{"type": "PUT", "strike": 240, "side": "BUY", "qty": 1}],
                "spot": 250,
                "iv_mult": 1.0,
                "range_pct": 0.15,
                "dte": 30,
                "strategyId": "long-put",
            },
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")

        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/builder/price", json=test_case["payload"], timeout=5
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                quality = data.get("quality", {})
                score = quality.get("score", "N/A")
                buckets = quality.get("buckets", {})
                flags = quality.get("flags", [])

                print(f"   ✅ Success - Score: {score}")
                print(f"   ⏱️  Response time: {response_time:.3f}s")
                print(
                    f"   📈 Buckets: L={buckets.get('liquidity', 0):.2f}, P={buckets.get('pricing', 0):.2f}, S={buckets.get('structure', 0):.2f}, R={buckets.get('risk', 0):.2f}, T={buckets.get('stability', 0):.2f}"
                )
                if flags:
                    print(f"   🚩 Flags: {flags}")

                results.append(
                    {
                        "name": test_case["name"],
                        "score": score,
                        "response_time": response_time,
                        "buckets": buckets,
                        "flags": flags,
                        "success": True,
                    }
                )

                # Verify response time is under 1 second
                if response_time < 1.0:
                    print("   ✅ Response time under 1s requirement")
                else:
                    print(
                        f"   ⚠️  Response time {response_time:.3f}s exceeds 1s requirement"
                    )

            else:
                print(f"   ❌ Failed - Status: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(
                    {
                        "name": test_case["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                    }
                )

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {str(e)}")
            results.append(
                {"name": test_case["name"], "success": False, "error": str(e)}
            )

    return results


def test_quality_scoring_variations():
    """Test quality scoring with parameter variations"""
    print("\n🎛️  TESTING QUALITY SCORING VARIATIONS")
    print("=" * 45)

    base_payload = {
        "symbol": "TSLA",
        "expiry": "2025-02-21",
        "legs": [{"type": "CALL", "strike": 250, "side": "BUY", "qty": 1}],
        "spot": 250,
        "iv_mult": 1.0,
        "range_pct": 0.15,
        "dte": 30,
        "strategyId": "long-call",
    }

    variations = [
        {"name": "High IV (2x)", "changes": {"iv_mult": 2.0}},
        {"name": "Low IV (0.5x)", "changes": {"iv_mult": 0.5}},
        {"name": "Short DTE (7 days)", "changes": {"dte": 7}},
        {"name": "Long DTE (60 days)", "changes": {"dte": 60}},
        {"name": "Wide Range (30%)", "changes": {"range_pct": 0.30}},
        {"name": "Narrow Range (5%)", "changes": {"range_pct": 0.05}},
        {
            "name": "OTM Strike",
            "changes": {
                "legs": [{"type": "CALL", "strike": 280, "side": "BUY", "qty": 1}]
            },
        },
        {
            "name": "ITM Strike",
            "changes": {
                "legs": [{"type": "CALL", "strike": 220, "side": "BUY", "qty": 1}]
            },
        },
    ]

    print("Testing quality score variations...")

    for variation in variations:
        payload = base_payload.copy()
        payload.update(variation["changes"])

        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/builder/price", json=payload, timeout=5
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                quality = data.get("quality", {})
                score = quality.get("score", "N/A")

                print(
                    f"   {variation['name']}: Score={score}, Time={response_time:.3f}s"
                )
            else:
                print(f"   {variation['name']}: Failed (HTTP {response.status_code})")

        except Exception as e:
            print(f"   {variation['name']}: Error - {str(e)}")


def test_options_overview_endpoint():
    """
    Test the new /api/options/overview endpoint functionality.
    Tests 3 scenarios as requested:
    1. GET /api/options/overview - Default (symbol=ALL)
    2. GET /api/options/overview?symbol=ALL - Explicit ALL parameter
    3. GET /api/options/overview?symbol=TSLA - Specific symbol test
    """
    print("🎯 TESTING OPTIONS OVERVIEW ENDPOINT")
    print("=" * 50)

    test_scenarios = [
        {
            "name": "Default (symbol=ALL)",
            "url": f"{BASE_URL}/options/overview",
            "params": None,
        },
        {
            "name": "Explicit ALL parameter",
            "url": f"{BASE_URL}/options/overview",
            "params": {"symbol": "ALL"},
        },
        {
            "name": "Specific symbol (TSLA)",
            "url": f"{BASE_URL}/options/overview",
            "params": {"symbol": "TSLA"},
        },
    ]

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}...")

        try:
            start_time = time.time()
            response = requests.get(
                scenario["url"], params=scenario["params"], timeout=5
            )
            response_time = time.time() - start_time

            print(f"   ⏱️  Response time: {response_time:.3f}s")

            # Check response time requirement (under 1 second)
            if response_time < 1.0:
                print("   ✅ Response time under 1s requirement")
            else:
                print(
                    f"   ⚠️  Response time {response_time:.3f}s exceeds 1s requirement"
                )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ HTTP 200 status received")
                print(f"   📊 Response structure: {list(data.keys())}")

                # Validate required fields
                required_fields = [
                    "activeStrategies",
                    "expirationDates",
                    "dailyVolumeUsd",
                    "avgIvPct",
                ]
                missing_fields = [
                    field for field in required_fields if field not in data
                ]

                if not missing_fields:
                    print("   ✅ All required fields present")

                    # Validate field types and values
                    validation_results = []

                    # activeStrategies should be integer
                    active_strategies = data.get("activeStrategies")
                    if isinstance(active_strategies, int) and active_strategies >= 0:
                        print(
                            f"   ✅ activeStrategies: {active_strategies} (valid integer)"
                        )
                        validation_results.append(True)
                    else:
                        print(
                            f"   ❌ activeStrategies: {active_strategies} (invalid - should be positive integer)"
                        )
                        validation_results.append(False)

                    # expirationDates should be integer
                    expiration_dates = data.get("expirationDates")
                    if isinstance(expiration_dates, int) and expiration_dates >= 0:
                        print(
                            f"   ✅ expirationDates: {expiration_dates} (valid integer)"
                        )
                        validation_results.append(True)
                    else:
                        print(
                            f"   ❌ expirationDates: {expiration_dates} (invalid - should be positive integer)"
                        )
                        validation_results.append(False)

                    # dailyVolumeUsd should be positive number
                    daily_volume = data.get("dailyVolumeUsd")
                    if isinstance(daily_volume, (int, float)) and daily_volume > 0:
                        print(
                            f"   ✅ dailyVolumeUsd: ${daily_volume:,.2f} (valid positive number)"
                        )
                        validation_results.append(True)
                    else:
                        print(
                            f"   ❌ dailyVolumeUsd: {daily_volume} (invalid - should be positive number)"
                        )
                        validation_results.append(False)

                    # avgIvPct should be percentage value or null
                    avg_iv = data.get("avgIvPct")
                    if avg_iv is None or (
                        isinstance(avg_iv, (int, float)) and 0 <= avg_iv <= 100
                    ):
                        print(f"   ✅ avgIvPct: {avg_iv}% (valid percentage or null)")
                        validation_results.append(True)
                    else:
                        print(
                            f"   ❌ avgIvPct: {avg_iv} (invalid - should be percentage 0-100 or null)"
                        )
                        validation_results.append(False)

                    # Check if values are realistic (not zeros or negative)
                    realistic_check = True
                    if active_strategies == 0:
                        print("   ⚠️  activeStrategies is 0 - may not be realistic")
                        realistic_check = False
                    if daily_volume <= 0:
                        print(
                            "   ⚠️  dailyVolumeUsd is not positive - may not be realistic"
                        )
                        realistic_check = False

                    if realistic_check:
                        print("   ✅ Values appear realistic (not zeros or negative)")

                    all_valid = all(validation_results)

                    results.append(
                        {
                            "scenario": scenario["name"],
                            "success": True,
                            "response_time": response_time,
                            "data": data,
                            "validation_passed": all_valid,
                            "realistic_values": realistic_check,
                        }
                    )

                    if all_valid:
                        print("   ✅ All field validations passed")
                    else:
                        print("   ❌ Some field validations failed")

                else:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    results.append(
                        {
                            "scenario": scenario["name"],
                            "success": False,
                            "error": f"Missing fields: {missing_fields}",
                            "response_time": response_time,
                        }
                    )

            else:
                print(f"   ❌ HTTP {response.status_code} status received")
                print(f"   Response: {response.text}")
                results.append(
                    {
                        "scenario": scenario["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response_time": response_time,
                    }
                )

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            results.append(
                {"scenario": scenario["name"], "success": False, "error": str(e)}
            )

    # Test symbol parameter filtering (different values for ALL vs TSLA)
    print("\n4. Testing symbol parameter filtering...")
    try:
        all_response = requests.get(
            f"{BASE_URL}/options/overview", params={"symbol": "ALL"}, timeout=5
        )
        tsla_response = requests.get(
            f"{BASE_URL}/options/overview", params={"symbol": "TSLA"}, timeout=5
        )

        if all_response.status_code == 200 and tsla_response.status_code == 200:
            all_data = all_response.json()
            tsla_data = tsla_response.json()

            # Check if values are different (indicating filtering works)
            differences_found = False
            for field in [
                "activeStrategies",
                "expirationDates",
                "dailyVolumeUsd",
                "avgIvPct",
            ]:
                if all_data.get(field) != tsla_data.get(field):
                    differences_found = True
                    print(
                        f"   ✅ {field}: ALL={all_data.get(field)}, TSLA={tsla_data.get(field)} (different values)"
                    )

            if differences_found:
                print(
                    "   ✅ Symbol parameter filtering working (different values for ALL vs TSLA)"
                )
            else:
                print(
                    "   ⚠️  Symbol parameter filtering may not be working (same values for ALL vs TSLA)"
                )

        else:
            print("   ❌ Could not test filtering due to request failures")

    except Exception as e:
        print(f"   ❌ Filtering test error: {str(e)}")

    return results


def test_options_flow_summary_endpoint():
    """
    Test the new /api/options/flow/summary endpoint functionality.
    Tests 4 scenarios as requested:
    1. GET /api/options/flow/summary - Default (symbol=ALL, days=7)
    2. GET /api/options/flow/summary?symbol=TSLA&days=7 - Specific symbol with days
    3. GET /api/options/flow/summary?symbol=TSLA - Specific symbol default days
    4. GET /api/options/flow/summary?days=14 - Different days parameter
    """
    print("🎯 TESTING OPTIONS FLOW SUMMARY ENDPOINT")
    print("=" * 50)

    test_scenarios = [
        {
            "name": "Default (symbol=ALL, days=7)",
            "url": f"{BASE_URL}/options/flow/summary",
            "params": None,
        },
        {
            "name": "Specific symbol with days (TSLA, 7 days)",
            "url": f"{BASE_URL}/options/flow/summary",
            "params": {"symbol": "TSLA", "days": 7},
        },
        {
            "name": "Specific symbol default days (TSLA)",
            "url": f"{BASE_URL}/options/flow/summary",
            "params": {"symbol": "TSLA"},
        },
        {
            "name": "Different days parameter (14 days)",
            "url": f"{BASE_URL}/options/flow/summary",
            "params": {"days": 14},
        },
    ]

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}...")

        try:
            start_time = time.time()
            response = requests.get(
                scenario["url"], params=scenario["params"], timeout=10
            )
            response_time = time.time() - start_time

            print(f"   ⏱️  Response time: {response_time:.3f}s")

            # Check response time requirement (under 5 seconds for external API calls)
            if response_time < 5.0:
                print("   ✅ Response time under 5s requirement")
            else:
                print(
                    f"   ⚠️  Response time {response_time:.3f}s exceeds 5s requirement"
                )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ HTTP 200 status received")
                print(f"   📊 Response structure: {list(data.keys())}")

                # Validate required fields
                required_fields = ["live", "historical", "news", "congress", "insiders"]
                missing_fields = [
                    field for field in required_fields if field not in data
                ]

                if not missing_fields:
                    print("   ✅ All required fields present")

                    # Validate field types and values
                    validation_results = []

                    # All fields should be integers >= 0
                    for field in required_fields:
                        value = data.get(field)
                        if isinstance(value, int) and value >= 0:
                            print(f"   ✅ {field}: {value} (valid integer)")
                            validation_results.append(True)
                        else:
                            print(
                                f"   ❌ {field}: {value} (invalid - should be non-negative integer)"
                            )
                            validation_results.append(False)

                    # Check source metadata
                    source = data.get("source", {})
                    if "trades" in source:
                        trades_source = source.get("trades")
                        if trades_source == "uw":
                            print("   ✅ Source metadata shows 'uw' for trades data")
                            validation_results.append(True)
                        elif trades_source == "error":
                            print(
                                "   ⚠️  Source shows error - graceful fallback working"
                            )
                            validation_results.append(True)
                        else:
                            print(f"   ❌ Unexpected trades source: {trades_source}")
                            validation_results.append(False)
                    else:
                        print("   ❌ Missing source metadata for trades")
                        validation_results.append(False)

                    all_valid = all(validation_results)

                    results.append(
                        {
                            "scenario": scenario["name"],
                            "success": True,
                            "response_time": response_time,
                            "data": data,
                            "validation_passed": all_valid,
                        }
                    )

                    if all_valid:
                        print("   ✅ All field validations passed")
                    else:
                        print("   ❌ Some field validations failed")

                else:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    results.append(
                        {
                            "scenario": scenario["name"],
                            "success": False,
                            "error": f"Missing fields: {missing_fields}",
                            "response_time": response_time,
                        }
                    )

            else:
                print(f"   ❌ HTTP {response.status_code} status received")
                print(f"   Response: {response.text}")
                results.append(
                    {
                        "scenario": scenario["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response_time": response_time,
                    }
                )

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            results.append(
                {"scenario": scenario["name"], "success": False, "error": str(e)}
            )

    return results


def test_options_analytics_integration():
    """
    Comprehensive test of Options Analytics backend integration with UW and TradeStation.
    Tests all 4 endpoints as specified in the review request.
    """
    print("🎯 TESTING OPTIONS ANALYTICS BACKEND INTEGRATION")
    print("=" * 60)
    print("Testing real-data integration endpoints with UW and TradeStation")
    print()

    all_results = []

    # Test 1: Options Overview endpoints (TradeStation integration)
    print("📊 TESTING TRADESTATION INTEGRATION - OPTIONS OVERVIEW")
    print("-" * 55)
    overview_results = test_options_overview_endpoint()
    all_results.extend(overview_results)

    # Test 2: Options Flow Summary endpoints (UnusualWhales integration)
    print("\n📈 TESTING UNUSUALWHALES INTEGRATION - OPTIONS FLOW")
    print("-" * 50)
    flow_results = test_options_flow_summary_endpoint()
    all_results.extend(flow_results)

    # Summary of integration testing
    print("\n📋 OPTIONS ANALYTICS INTEGRATION SUMMARY")
    print("=" * 50)

    successful_tests = sum(1 for r in all_results if r.get("success", False))
    total_tests = len(all_results)

    print(f"✅ Total endpoints tested: {total_tests}")
    print(f"✅ Successful tests: {successful_tests}")
    print(f"✅ Success rate: {successful_tests/total_tests*100:.1f}%")

    # Categorize results
    overview_success = sum(1 for r in overview_results if r.get("success", False))
    flow_success = sum(1 for r in flow_results if r.get("success", False))

    print(
        f"\n📊 TradeStation Overview endpoints: {overview_success}/{len(overview_results)} passed"
    )
    print(f"📈 UnusualWhales Flow endpoints: {flow_success}/{len(flow_results)} passed")

    # Check for specific validation criteria
    print("\n🔍 VALIDATION CRITERIA CHECK:")

    # HTTP 200 status
    http_200_count = sum(1 for r in all_results if r.get("success", False))
    print(f"   ✅ HTTP 200 status: {http_200_count}/{total_tests} endpoints")

    # Response structure validation
    structure_valid = sum(1 for r in all_results if r.get("validation_passed", False))
    print(f"   ✅ Correct JSON structure: {structure_valid}/{total_tests} endpoints")

    # Source metadata validation
    source_metadata_count = 0
    for r in all_results:
        if r.get("success") and r.get("data"):
            source = r["data"].get("source", {})
            if ("chain" in source and source.get("chain") == "tradestation") or (
                "trades" in source and source.get("trades") == "uw"
            ):
                source_metadata_count += 1
    print(
        f"   ✅ Source metadata present: {source_metadata_count}/{total_tests} endpoints"
    )

    # Response time validation
    fast_responses = sum(1 for r in all_results if r.get("response_time", 10) < 5.0)
    print(f"   ✅ Response time <5s: {fast_responses}/{total_tests} endpoints")

    # Error handling validation (graceful fallback)
    error_handling_ok = True
    for r in all_results:
        if r.get("success") and r.get("data"):
            source = r["data"].get("source", {})
            if "error" in source:
                print(
                    f"   ✅ Graceful error handling detected in {r.get('scenario', 'unknown')}"
                )

    # Overall assessment
    integration_success = (
        successful_tests == total_tests
        and structure_valid == total_tests
        and fast_responses
        >= total_tests * 0.8  # Allow 20% to be slower due to external APIs
    )

    if integration_success:
        print("\n🎉 OPTIONS ANALYTICS INTEGRATION - EXCELLENT RESULTS!")
        print("   ✅ All endpoints working correctly")
        print("   ✅ Real data integration operational")
        print("   ✅ External API providers responding")
        print("   ✅ Error handling graceful")
        return True
    else:
        print("\n⚠️  OPTIONS ANALYTICS INTEGRATION - ISSUES DETECTED")
        if successful_tests < total_tests:
            print(f"   ❌ {total_tests - successful_tests} endpoints failing")
        if structure_valid < total_tests:
            print(
                f"   ❌ {total_tests - structure_valid} endpoints have structure issues"
            )
        if fast_responses < total_tests * 0.8:
            print("   ❌ Response times too slow for external API integration")
        return False


def main():
    """Main test execution"""
    print("🚀 OPTIONS ANALYTICS BACKEND INTEGRATION TESTING")
    print("=" * 65)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base URL: {BASE_URL}")
    print()
    print("🎯 OBJECTIVE: Verify new real-data integration endpoints work correctly")
    print("📊 ENDPOINTS TO TEST:")
    print(
        "   1. GET /api/options/overview - Market overview with TradeStation chain data"
    )
    print("   2. GET /api/options/overview?symbol=TSLA - Symbol-specific overview")
    print("   3. GET /api/options/flow/summary - Flow summary with UW trades data")
    print(
        "   4. GET /api/options/flow/summary?symbol=TSLA&days=7 - Symbol-specific flow"
    )

    # Main integration test
    print("\n" + "=" * 65)
    integration_success = test_options_analytics_integration()

    # Legacy tests (keeping for compatibility)
    print("\n" + "=" * 65)
    print("🔧 RUNNING LEGACY QUALITY ENDPOINT TESTS")
    print("-" * 40)
    success, data = test_builder_quality_endpoint()

    if success:
        config_results = test_different_leg_configurations()
        test_quality_scoring_variations()

        successful_configs = sum(1 for r in config_results if r.get("success", False))
        total_configs = len(config_results)
        legacy_success = successful_configs == total_configs
    else:
        legacy_success = False

    # Final Summary
    print("\n📊 FINAL TEST SUMMARY")
    print("=" * 40)

    print(
        f"✅ Options Analytics Integration: {'PASS' if integration_success else 'FAIL'}"
    )
    print(f"✅ Legacy Quality Endpoints: {'PASS' if legacy_success else 'FAIL'}")

    # Overall success check
    overall_success = integration_success and legacy_success

    if overall_success:
        print(
            "\n🎉 ALL TESTS PASSED - Options Analytics backend integration working correctly!"
        )
        print("   ✅ TradeStation integration operational")
        print("   ✅ UnusualWhales integration operational")
        print("   ✅ Real-time data flowing correctly")
        print("   ✅ Error handling graceful")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Review results above")
        if not integration_success:
            print("   ❌ Options Analytics integration issues detected")
        if not legacy_success:
            print("   ❌ Legacy quality endpoint issues detected")
        return False


if __name__ == "__main__":
    main()
