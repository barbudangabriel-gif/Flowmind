#!/usr/bin/env python3
"""
BSR1 (Strike Rail PRO) Backend Integration Testing
Testing Builder pricing engine and options chain endpoints for BSR1 support
"""

import requests
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "http://localhost:8000/api"


def test_builder_price_endpoint():
    """Test POST /api/builder/price endpoint with sample TSLA strategy data"""
    print("🎯 TESTING POST /api/builder/price - BSR1 Integration")
    print("=" * 60)

    # Test 1: Long Call TSLA Strategy
    print("\n✅ TEST 1: Long Call TSLA Strategy for BSR1")
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
            print("✅ Builder Price Endpoint Working")

            # Verify required sections for BSR1
            required_sections = ["pricing", "chart", "meta", "greeks"]
            for section in required_sections:
                if section in data:
                    print(f"✅ {section.upper()} section present")
                else:
                    print(f"❌ {section.upper()} section missing")

            # Check pricing data
            if "pricing" in data:
                pricing = data["pricing"]
                print(f"Net Debit: ${pricing.get('net_debit', 'N/A')}")
                print(f"Chance of Profit: {pricing.get('chance_profit', 'N/A')}%")
                print(f"Max Profit: ${pricing.get('max_profit', 'N/A')}")
                print(f"Max Loss: ${pricing.get('max_loss', 'N/A')}")

            # Check Greeks for BSR1 tooltips
            if "greeks" in data:
                greeks = data["greeks"]
                print(f"Delta: {greeks.get('delta', 'N/A')}")
                print(f"Gamma: {greeks.get('gamma', 'N/A')}")
                print(f"Theta: {greeks.get('theta', 'N/A')}")
                print(f"Vega: {greeks.get('vega', 'N/A')}")

            # Check chart data for P&L visualization
            if "chart" in data:
                chart = data["chart"]
                if "series" in chart and len(chart["series"]) > 0:
                    series_data = chart["series"][0].get("xy", [])
                    print(f"Chart Data Points: {len(series_data)}")
                    if series_data:
                        print(f"Sample Chart Point: {series_data[0]}")
                else:
                    print("❌ No chart series data found")

            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

    # Test 2: Bull Call Spread for multi-leg BSR1 support
    print("\n✅ TEST 2: Bull Call Spread TSLA Strategy for BSR1")
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
            f"{BACKEND_URL}/builder/price", json=bull_call_payload, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Multi-leg Strategy Pricing Working")

            if "pricing" in data:
                pricing = data["pricing"]
                print(f"Net Debit: ${pricing.get('net_debit', 'N/A')}")
                print(f"Max Profit: ${pricing.get('max_profit', 'N/A')}")
                print(f"Chance of Profit: {pricing.get('chance_profit', 'N/A')}%")

            return True
        else:
            print(f"❌ Multi-leg Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Multi-leg Exception: {str(e)}")
        return False


def test_options_chain_endpoint():
    """Test GET /api/options/chain endpoint for BSR1 data requirements"""
    print("\n🎯 TESTING GET /api/options/chain - BSR1 Data Requirements")
    print("=" * 60)

    # Test with TSLA and specific expiry
    print("\n✅ TEST 1: TSLA Options Chain for BSR1")

    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain",
            params={"symbol": "TSLA", "expiry": "2025-02-21"},
            timeout=15,
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Options Chain Endpoint Working")

            # Check for spot price (can be "spot_price" or "spot")
            spot_price = data.get("spot_price") or data.get("spot")
            if spot_price:
                print(f"✅ Spot Price: ${spot_price}")
            else:
                print("❌ No spot price found")

            # Check for raw options chain data
            raw_data = data.get("raw")
            if raw_data and "OptionChains" in raw_data:
                chains = raw_data["OptionChains"]
                if chains and len(chains) > 0:
                    chain = chains[0]
                    print("✅ Options Chain Found")

                    # Check for strikes data (required for BSR1)
                    strikes = chain.get("Strikes", [])
                    print(f"✅ Number of Strikes: {len(strikes)}")

                    if strikes:
                        # Examine first strike for BSR1 requirements
                        first_strike = strikes[0]
                        strike_price = first_strike.get("StrikePrice")
                        print(f"✅ Sample Strike Price: ${strike_price}")

                        # Check Calls data for BSR1 requirements
                        calls = first_strike.get("Calls", [])
                        if calls:
                            call = calls[0]
                            print("✅ CALLS DATA STRUCTURE:")

                            # BSR1 Required Fields
                            bsr1_fields = ["Bid", "Ask", "OpenInterest", "Volume"]
                            for field in bsr1_fields:
                                value = call.get(field)
                                if value is not None:
                                    print(f"  ✅ {field}: {value}")
                                else:
                                    print(f"  ❌ {field}: Missing")

                            # Check IV field specifically (can be "IV" or "ImpliedVolatility")
                            iv_value = call.get("IV") or call.get("ImpliedVolatility")
                            if iv_value is not None:
                                print(f"  ✅ ImpliedVolatility (IV): {iv_value}")
                            else:
                                print("  ❌ ImpliedVolatility (IV): Missing")

                        # Check Puts data for BSR1 requirements
                        puts = first_strike.get("Puts", [])
                        if puts:
                            put = puts[0]
                            print("✅ PUTS DATA STRUCTURE:")

                            # BSR1 Required Fields
                            for field in bsr1_fields:
                                value = put.get(field)
                                if value is not None:
                                    print(f"  ✅ {field}: {value}")
                                else:
                                    print(f"  ❌ {field}: Missing")

                            # Check IV field specifically (can be "IV" or "ImpliedVolatility")
                            iv_value = put.get("IV") or put.get("ImpliedVolatility")
                            if iv_value is not None:
                                print(f"  ✅ ImpliedVolatility (IV): {iv_value}")
                            else:
                                print("  ❌ ImpliedVolatility (IV): Missing")

                    return True
                else:
                    print("❌ No strikes found in options chain")
                    return False
            else:
                print("❌ No raw options chain data found")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_bsr1_data_structure_compliance():
    """Test that response structures support BSR1 component requirements"""
    print("\n🎯 TESTING BSR1 DATA STRUCTURE COMPLIANCE")
    print("=" * 60)

    print("\n✅ TEST 1: Verifying BSR1 Requirements Compliance")

    # Test options chain for BSR1 strike rail data
    try:
        response = requests.get(
            f"{BACKEND_URL}/options/chain", params={"symbol": "TSLA"}, timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            # BSR1 Requirements Checklist
            bsr1_requirements = {
                "StrikePrice for strikes": False,
                "Calls array with required fields": False,
                "Puts array with required fields": False,
                "Bid/Ask prices for spread calculations": False,
                "OpenInterest and Volume for bar charts": False,
                "ImpliedVolatility for IV visualization": False,
            }

            raw_data = data.get("raw", {})
            chains = raw_data.get("OptionChains", [])

            if chains:
                chain = chains[0]
                strikes = chain.get("Strikes", [])

                if strikes:
                    strike = strikes[0]

                    # Check StrikePrice
                    if strike.get("StrikePrice"):
                        bsr1_requirements["StrikePrice for strikes"] = True

                    # Check Calls array
                    calls = strike.get("Calls", [])
                    if calls:
                        call = calls[0]
                        required_fields = ["Bid", "Ask", "OpenInterest", "Volume"]

                        # Check basic required fields
                        basic_fields_present = all(
                            field in call for field in required_fields
                        )

                        # Check IV field (can be "IV" or "ImpliedVolatility")
                        iv_present = "IV" in call or "ImpliedVolatility" in call

                        if basic_fields_present and iv_present:
                            bsr1_requirements["Calls array with required fields"] = True

                            if (
                                call.get("Bid") is not None
                                and call.get("Ask") is not None
                            ):
                                bsr1_requirements[
                                    "Bid/Ask prices for spread calculations"
                                ] = True

                            if (
                                call.get("OpenInterest") is not None
                                and call.get("Volume") is not None
                            ):
                                bsr1_requirements[
                                    "OpenInterest and Volume for bar charts"
                                ] = True

                            if (
                                call.get("IV") is not None
                                or call.get("ImpliedVolatility") is not None
                            ):
                                bsr1_requirements[
                                    "ImpliedVolatility for IV visualization"
                                ] = True

                    # Check Puts array
                    puts = strike.get("Puts", [])
                    if puts:
                        put = puts[0]
                        # Check basic required fields for puts
                        basic_fields_present = all(
                            field in put for field in required_fields
                        )
                        # Check IV field (can be "IV" or "ImpliedVolatility")
                        iv_present = "IV" in put or "ImpliedVolatility" in put

                        if basic_fields_present and iv_present:
                            bsr1_requirements["Puts array with required fields"] = True

            # Report BSR1 compliance
            print("BSR1 REQUIREMENTS COMPLIANCE:")
            total_requirements = len(bsr1_requirements)
            met_requirements = sum(bsr1_requirements.values())

            for requirement, met in bsr1_requirements.items():
                status = "✅" if met else "❌"
                print(f"  {status} {requirement}")

            compliance_percentage = (met_requirements / total_requirements) * 100
            print(
                f"\nBSR1 Compliance: {met_requirements}/{total_requirements} ({compliance_percentage:.1f}%)"
            )

            return compliance_percentage >= 80  # 80% compliance threshold
        else:
            print(f"❌ Options chain request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ BSR1 compliance test exception: {str(e)}")
        return False


def main():
    """Run all BSR1 backend integration tests"""
    print("🚀 BSR1 (Strike Rail PRO) Backend Integration Testing")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 70)

    test_results = []

    # Test 1: Builder Price Endpoint
    print("\n" + "=" * 50)
    result1 = test_builder_price_endpoint()
    test_results.append(("Builder Price Endpoint", result1))

    # Test 2: Options Chain Endpoint
    print("\n" + "=" * 50)
    result2 = test_options_chain_endpoint()
    test_results.append(("Options Chain Endpoint", result2))

    # Test 3: BSR1 Data Structure Compliance
    print("\n" + "=" * 50)
    result3 = test_bsr1_data_structure_compliance()
    test_results.append(("BSR1 Data Structure Compliance", result3))

    # Summary
    print("\n" + "=" * 70)
    print("🎯 BSR1 BACKEND INTEGRATION TEST SUMMARY")
    print("=" * 70)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(f"\nSUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 BSR1 BACKEND INTEGRATION: READY FOR PRODUCTION")
    else:
        print("⚠️  BSR1 BACKEND INTEGRATION: NEEDS ATTENTION")

    print("=" * 70)


if __name__ == "__main__":
    main()
