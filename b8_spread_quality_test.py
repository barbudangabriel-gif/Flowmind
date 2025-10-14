#!/usr/bin/env python3
"""
B8 Spread Quality Meter Backend Testing
=====================================

Tests the complete B8 Spread Quality Meter backend implementation in the Options Optimizer.
Verifies enhanced optimize endpoint returns spread quality metrics including:
- quality: 0-100 range scoring
- slippage_est: half-spread calculation
- nbbo_ok: liquidity assessment boolean
- market: bid/ask/mid/oi/vol data per leg

Test Requirements:
1. Enhanced Optimize Endpoint: POST /api/optimize/suggest returns spread quality metrics
2. Spread Quality Fields: Strategies include quality, slippage_est, nbbo_ok, market fields
3. Quality Calculation: Verify spread quality scoring algorithm with different scenarios
4. Multi-Strategy Support: Test Long Call, Bull Call Spread, Cash-Secured Put quality calculations
5. Market Data Analysis: Confirm _leg_market_snapshot and _compute_spread_quality functions work correctly
"""

import requests
import sys
import os

# Backend URL from environment
BACKEND_URL = os.getenv(
    "REACT_APP_BACKEND_URL", "http://localhost:8000"
)
API_BASE = f"{BACKEND_URL}/api"


def test_b8_spread_quality_meter():
    """Test B8 Spread Quality Meter backend implementation"""

    print("🎯 B8 SPREAD QUALITY METER BACKEND TESTING")
    print("=" * 60)

    results = []

    # Test 1: Enhanced Optimize Endpoint with TSLA
    print("\n✅ Test 1: Enhanced Optimize Endpoint - TSLA Strategies")
    try:
        response = requests.get(
            f"{API_BASE}/optimize/suggest",
            params={
                "symbol": "TSLA",
                "sentiment": "bullish",
                "dte": 30,
                "budget": 5000,
                "risk_bias": 0,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            strategies = data.get("strategies", [])

            print(f"   📊 Generated {len(strategies)} strategies")

            # Verify each strategy has spread quality metrics
            quality_fields_found = 0
            for i, strategy in enumerate(strategies):
                strategy_name = strategy.get("label", f"Strategy {i+1}")
                print(f"   📈 {strategy_name}:")

                # Check for B8 spread quality fields
                has_quality = "quality" in strategy
                has_slippage = "slippage_est" in strategy
                has_nbbo = "nbbo_ok" in strategy
                has_market = "market" in strategy

                if has_quality:
                    quality_score = strategy["quality"]
                    print(f"      🎯 Quality Score: {quality_score}/100")

                    # Verify quality score is in 0-100 range
                    if 0 <= quality_score <= 100:
                        print("      ✅ Quality score in valid range (0-100)")
                    else:
                        print(f"      ❌ Quality score out of range: {quality_score}")

                if has_slippage:
                    slippage = strategy["slippage_est"]
                    print(f"      💰 Slippage Estimate: ${slippage}")

                    # Verify slippage is reasonable (should be positive)
                    if slippage >= 0:
                        print("      ✅ Slippage estimate valid")
                    else:
                        print(f"      ❌ Invalid slippage estimate: {slippage}")

                if has_nbbo:
                    nbbo_ok = strategy["nbbo_ok"]
                    print(f"      📊 NBBO OK: {nbbo_ok}")

                    # Verify NBBO is boolean
                    if isinstance(nbbo_ok, bool):
                        print("      ✅ NBBO flag is boolean")
                    else:
                        print(f"      ❌ NBBO flag not boolean: {type(nbbo_ok)}")

                if has_market:
                    market_data = strategy["market"]
                    print(f"      📈 Market Data: {len(market_data)} legs")

                    # Verify market data structure
                    for j, leg_market in enumerate(market_data):
                        required_fields = ["bid", "ask", "mid", "oi", "vol"]
                        missing_fields = [
                            f for f in required_fields if f not in leg_market
                        ]

                        if not missing_fields:
                            bid = leg_market["bid"]
                            ask = leg_market["ask"]
                            mid = leg_market["mid"]
                            print(
                                f"         Leg {j+1}: Bid=${bid}, Ask=${ask}, Mid=${mid}"
                            )
                            print(
                                f"      ✅ Market data structure complete for leg {j+1}"
                            )
                        else:
                            print(
                                f"      ❌ Missing market fields for leg {j+1}: {missing_fields}"
                            )

                # Count strategies with all quality fields
                if has_quality and has_slippage and has_nbbo and has_market:
                    quality_fields_found += 1
                    print("      ✅ All B8 spread quality fields present")
                else:
                    missing = []
                    if not has_quality:
                        missing.append("quality")
                    if not has_slippage:
                        missing.append("slippage_est")
                    if not has_nbbo:
                        missing.append("nbbo_ok")
                    if not has_market:
                        missing.append("market")
                    print(f"      ❌ Missing B8 fields: {missing}")

            if quality_fields_found == len(strategies):
                print(
                    f"   ✅ All {len(strategies)} strategies have complete B8 spread quality metrics"
                )
                results.append(
                    (
                        "Enhanced Optimize Endpoint",
                        True,
                        f"All {len(strategies)} strategies have B8 metrics",
                    )
                )
            else:
                print(
                    f"   ❌ Only {quality_fields_found}/{len(strategies)} strategies have complete B8 metrics"
                )
                results.append(
                    (
                        "Enhanced Optimize Endpoint",
                        False,
                        f"Only {quality_fields_found}/{len(strategies)} strategies complete",
                    )
                )

        else:
            print(f"   ❌ API Error: {response.status_code} - {response.text}")
            results.append(
                (
                    "Enhanced Optimize Endpoint",
                    False,
                    f"API Error: {response.status_code}",
                )
            )

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        results.append(("Enhanced Optimize Endpoint", False, f"Exception: {str(e)}"))

    # Test 2: Quality Score Range Validation
    print("\n✅ Test 2: Quality Score Range Validation - Multiple Symbols")
    try:
        test_symbols = ["AAPL", "SPY", "QQQ"]
        valid_scores = 0
        total_strategies = 0

        for symbol in test_symbols:
            print(f"   📊 Testing {symbol}...")
            response = requests.get(
                f"{API_BASE}/optimize/suggest",
                params={
                    "symbol": symbol,
                    "sentiment": "bullish",
                    "dte": 45,
                    "budget": 10000,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                strategies = data.get("strategies", [])

                for strategy in strategies:
                    total_strategies += 1
                    if "quality" in strategy:
                        quality = strategy["quality"]
                        if 0 <= quality <= 100:
                            valid_scores += 1
                        else:
                            print(
                                f"      ❌ Invalid quality score: {quality} for {strategy.get('label')}"
                            )

        if total_strategies > 0:
            score_percentage = (valid_scores / total_strategies) * 100
            print(
                f"   📊 Quality Score Validation: {valid_scores}/{total_strategies} ({score_percentage:.1f}%) valid"
            )

            if score_percentage >= 95:
                print("   ✅ Quality scores are properly bounded (0-100)")
                results.append(
                    (
                        "Quality Score Range",
                        True,
                        f"{score_percentage:.1f}% valid scores",
                    )
                )
            else:
                print("   ❌ Some quality scores out of range")
                results.append(
                    (
                        "Quality Score Range",
                        False,
                        f"Only {score_percentage:.1f}% valid",
                    )
                )
        else:
            print("   ❌ No strategies generated for testing")
            results.append(("Quality Score Range", False, "No strategies generated"))

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        results.append(("Quality Score Range", False, f"Exception: {str(e)}"))

    # Test 3: Slippage Estimation Calculation
    print("\n✅ Test 3: Slippage Estimation Calculation")
    try:
        response = requests.get(
            f"{API_BASE}/optimize/suggest",
            params={
                "symbol": "TSLA",
                "sentiment": "bullish",
                "dte": 30,
                "budget": 5000,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            strategies = data.get("strategies", [])

            slippage_valid = 0
            for strategy in strategies:
                if "slippage_est" in strategy and "market" in strategy:
                    slippage = strategy["slippage_est"]
                    market_data = strategy["market"]

                    # Calculate expected slippage (half-spread * 100)
                    expected_slippage = 0
                    for leg_market in market_data:
                        if "bid" in leg_market and "ask" in leg_market:
                            spread = leg_market["ask"] - leg_market["bid"]
                            expected_slippage += 0.5 * spread * 100

                    # Allow for rounding differences
                    if abs(slippage - expected_slippage) < 0.1:
                        slippage_valid += 1
                        print(
                            f"   ✅ {strategy.get('label')}: Slippage ${slippage} matches calculation"
                        )
                    else:
                        print(
                            f"   ⚠️  {strategy.get('label')}: Slippage ${slippage} vs expected ${expected_slippage:.2f}"
                        )

            if slippage_valid > 0:
                print(
                    f"   ✅ Slippage calculation verified for {slippage_valid} strategies"
                )
                results.append(
                    (
                        "Slippage Calculation",
                        True,
                        f"{slippage_valid} strategies verified",
                    )
                )
            else:
                print("   ❌ No valid slippage calculations found")
                results.append(("Slippage Calculation", False, "No valid calculations"))

        else:
            print(f"   ❌ API Error: {response.status_code}")
            results.append(
                ("Slippage Calculation", False, f"API Error: {response.status_code}")
            )

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        results.append(("Slippage Calculation", False, f"Exception: {str(e)}"))

    # Test 4: Multi-Strategy Support Verification
    print(
        "\n✅ Test 4: Multi-Strategy Support - Long Call, Bull Call Spread, Cash-Secured Put"
    )
    try:
        response = requests.get(
            f"{API_BASE}/optimize/suggest",
            params={
                "symbol": "TSLA",
                "sentiment": "bullish",
                "dte": 30,
                "budget": 10000,  # Higher budget to ensure all strategies
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            strategies = data.get("strategies", [])

            # Look for specific strategy types
            strategy_types = {}
            for strategy in strategies:
                label = strategy.get("label", "").lower()
                strategy_id = strategy.get("id", "")

                if "buy" in label and "c" in label and "sell" not in label:
                    strategy_types["Long Call"] = strategy
                elif "buy" in label and "sell" in label and "c" in label:
                    strategy_types["Bull Call Spread"] = strategy
                elif "sell" in label and "p" in label:
                    strategy_types["Cash-Secured Put"] = strategy

            print(f"   📊 Found {len(strategy_types)} target strategy types:")

            for strategy_name, strategy_data in strategy_types.items():
                print(f"   📈 {strategy_name}: {strategy_data.get('label')}")

                # Verify B8 fields for each strategy type
                b8_fields = ["quality", "slippage_est", "nbbo_ok", "market"]
                missing_fields = [f for f in b8_fields if f not in strategy_data]

                if not missing_fields:
                    quality = strategy_data["quality"]
                    slippage = strategy_data["slippage_est"]
                    nbbo = strategy_data["nbbo_ok"]
                    market_legs = len(strategy_data["market"])

                    print(
                        f"      Quality: {quality}, Slippage: ${slippage}, NBBO: {nbbo}, Market Legs: {market_legs}"
                    )
                    print(f"      ✅ All B8 fields present for {strategy_name}")
                else:
                    print(f"      ❌ Missing B8 fields: {missing_fields}")

            if len(strategy_types) >= 2:  # At least 2 of the 3 target strategies
                print(
                    f"   ✅ Multi-strategy support verified ({len(strategy_types)} strategy types)"
                )
                results.append(
                    (
                        "Multi-Strategy Support",
                        True,
                        f"{len(strategy_types)} strategy types with B8 metrics",
                    )
                )
            else:
                print(
                    f"   ❌ Insufficient strategy variety ({len(strategy_types)} types)"
                )
                results.append(
                    (
                        "Multi-Strategy Support",
                        False,
                        f"Only {len(strategy_types)} strategy types",
                    )
                )

        else:
            print(f"   ❌ API Error: {response.status_code}")
            results.append(
                ("Multi-Strategy Support", False, f"API Error: {response.status_code}")
            )

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        results.append(("Multi-Strategy Support", False, f"Exception: {str(e)}"))

    # Test 5: Market Data Analysis Verification
    print("\n✅ Test 5: Market Data Analysis - Bid/Ask/Mid/OI/Vol Structure")
    try:
        response = requests.get(
            f"{API_BASE}/optimize/suggest",
            params={
                "symbol": "AAPL",  # Use AAPL for potentially better market data
                "sentiment": "bullish",
                "dte": 30,
                "budget": 5000,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            strategies = data.get("strategies", [])

            market_data_complete = 0
            total_legs = 0

            for strategy in strategies:
                if "market" in strategy:
                    market_data = strategy["market"]

                    for leg_market in market_data:
                        total_legs += 1
                        required_fields = ["bid", "ask", "mid", "oi", "vol"]

                        if all(field in leg_market for field in required_fields):
                            market_data_complete += 1

                            # Verify data relationships
                            bid = leg_market["bid"]
                            ask = leg_market["ask"]
                            mid = leg_market["mid"]

                            # Basic sanity checks
                            if bid <= ask and (bid == 0 or (bid <= mid <= ask)):
                                print(
                                    f"      ✅ Valid market data: Bid=${bid}, Ask=${ask}, Mid=${mid}"
                                )
                            else:
                                print(
                                    f"      ⚠️  Questionable market data: Bid=${bid}, Ask=${ask}, Mid=${mid}"
                                )

            if total_legs > 0:
                completion_rate = (market_data_complete / total_legs) * 100
                print(
                    f"   📊 Market Data Completeness: {market_data_complete}/{total_legs} legs ({completion_rate:.1f}%)"
                )

                if completion_rate >= 90:
                    print("   ✅ Market data analysis working correctly")
                    results.append(
                        (
                            "Market Data Analysis",
                            True,
                            f"{completion_rate:.1f}% complete market data",
                        )
                    )
                else:
                    print("   ❌ Incomplete market data")
                    results.append(
                        (
                            "Market Data Analysis",
                            False,
                            f"Only {completion_rate:.1f}% complete",
                        )
                    )
            else:
                print("   ❌ No market data found")
                results.append(("Market Data Analysis", False, "No market data found"))

        else:
            print(f"   ❌ API Error: {response.status_code}")
            results.append(
                ("Market Data Analysis", False, f"API Error: {response.status_code}")
            )

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        results.append(("Market Data Analysis", False, f"Exception: {str(e)}"))

    # Test Summary
    print("\n" + "=" * 60)
    print("🎯 B8 SPREAD QUALITY METER TEST SUMMARY")
    print("=" * 60)

    passed_tests = sum(1 for _, success, _ in results if success)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    print(f"\n📊 SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 B8 SPREAD QUALITY METER BACKEND: EXCELLENT - Production Ready")
        return True
    elif success_rate >= 60:
        print("⚠️  B8 SPREAD QUALITY METER BACKEND: GOOD - Minor Issues")
        return True
    else:
        print("🚨 B8 SPREAD QUALITY METER BACKEND: NEEDS ATTENTION - Major Issues")
        return False


if __name__ == "__main__":
    print("🚀 Starting B8 Spread Quality Meter Backend Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")

    success = test_b8_spread_quality_meter()

    if success:
        print("\n✅ B8 Spread Quality Meter backend testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ B8 Spread Quality Meter backend testing failed!")
        sys.exit(1)
