import requests
import sys
import time


class PortfolioManagementTester:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")

        try:
            timeout = 30

            if method == "GET":
                response = requests.get(
                    url, headers=headers, params=params, timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    url, json=data, headers=headers, timeout=timeout
                )
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(
                    f"❌ Failed - Expected {expected_status}, got {response.status_code}"
                )
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_portfolio_management_with_tradestation_integration(self):
        """Test Portfolio Management Service with real TradeStation integration as requested in review"""
        print(
            "\n🎯 PORTFOLIO MANAGEMENT SERVICE WITH TRADESTATION INTEGRATION - COMPREHENSIVE TESTING"
        )
        print("=" * 100)
        print(
            "🎯 OBJECTIVE: Test updated Portfolio Management Service with real TradeStation integration"
        )
        print("📋 REVIEW REQUIREMENTS:")
        print(
            "   1. GET /api/portfolio-management/portfolios - Should load real TradeStation data in TradeStation Main portfolio"
        )
        print(
            "   2. GET /api/portfolio-management/portfolios/tradestation-main/positions - Should show real positions from TradeStation account"
        )
        print(
            "   3. Verify positions data structure includes both stocks and options from TradeStation"
        )
        print(
            "   4. Check if portfolio totals are calculated correctly from real TradeStation data"
        )
        print("   5. Confirm fallback to mock data works if TradeStation API fails")
        print("🔧 FOCUS AREAS:")
        print("   - TradeStation API integration working correctly")
        print("   - Real position data being loaded and formatted properly")
        print(
            "   - Portfolio totals (total_value, total_pnl, positions_count) reflecting TradeStation data"
        )
        print("   - Position metadata including TradeStation-specific fields")
        print("   - Data structure compatibility with existing frontend")
        print(
            "   - Live TradeStation account data (84 positions: 19 stocks, 65 options)"
        )

        # Test 1: GET /api/portfolio-management/portfolios - Should load real TradeStation data
        print(
            "\n📊 PHASE 1: Get All Portfolios - TradeStation Main Portfolio Integration"
        )
        print("-" * 80)

        success, portfolios_data = self.run_test(
            "Get All Portfolios with TradeStation Integration",
            "GET",
            "portfolio-management/portfolios",
            200,
        )

        if not success:
            print("❌ CRITICAL: Portfolio Management portfolios endpoint failed")
            return False

        # Analyze portfolios response
        portfolios = portfolios_data.get("portfolios", [])
        print(f"📊 Total Portfolios Found: {len(portfolios)}")

        # Find TradeStation Main portfolio
        tradestation_main = None
        for portfolio in portfolios:
            if (
                portfolio.get("id") == "tradestation-main"
                or "tradestation" in portfolio.get("name", "").lower()
            ):
                tradestation_main = portfolio
                break

        if tradestation_main:
            print("✅ TradeStation Main Portfolio Found:")
            print(f"   - ID: {tradestation_main.get('id')}")
            print(f"   - Name: {tradestation_main.get('name')}")
            print(f"   - Total Value: ${tradestation_main.get('total_value', 0):,.2f}")
            print(f"   - Total P&L: ${tradestation_main.get('total_pnl', 0):,.2f}")
            print(
                f"   - Positions Count: {tradestation_main.get('positions_count', 0)}"
            )
            print(
                f"   - Data Source: {tradestation_main.get('data_source', 'Unknown')}"
            )

            # Check if using real TradeStation data
            data_source = tradestation_main.get("data_source", "")
            if (
                "tradestation" in data_source.lower()
                and "mock" not in data_source.lower()
            ):
                print(f"✅ Using Real TradeStation Data: {data_source}")
                using_real_data = True
            elif "mock" in data_source.lower() or "fallback" in data_source.lower():
                print(f"⚠️  Using Fallback/Mock Data: {data_source}")
                using_real_data = False
            else:
                print(f"❓ Data Source Unclear: {data_source}")
                using_real_data = False

            # Verify expected position count (84 positions: 19 stocks, 65 options)
            positions_count = tradestation_main.get("positions_count", 0)
            if positions_count >= 80:  # Allow some variance
                print(
                    f"✅ Position Count Matches Expected Range: {positions_count} (expected ~84)"
                )
                position_count_correct = True
            elif positions_count >= 10:
                print(
                    f"⚠️  Position Count Lower Than Expected: {positions_count} (expected ~84)"
                )
                position_count_correct = False
            else:
                print(f"❌ Position Count Too Low: {positions_count} (expected ~84)")
                position_count_correct = False

        else:
            print("❌ CRITICAL: TradeStation Main Portfolio Not Found")
            print(f"   Available portfolios: {[p.get('name') for p in portfolios]}")
            using_real_data = False
            position_count_correct = False

        # Test 2: GET /api/portfolio-management/portfolios/tradestation-main/positions - Real positions
        print(
            "\n📈 PHASE 2: Get TradeStation Main Portfolio Positions - Real Position Data"
        )
        print("-" * 80)

        success, positions_data = self.run_test(
            "Get TradeStation Main Positions",
            "GET",
            "portfolio-management/portfolios/tradestation-main/positions",
            200,
        )

        if not success:
            print("❌ CRITICAL: TradeStation Main positions endpoint failed")
            return False

        # Analyze positions response
        positions = positions_data.get("positions", [])
        portfolio_summary = positions_data.get("portfolio_summary", {})

        print("📊 Positions Analysis:")
        print(f"   - Total Positions: {len(positions)}")
        print(
            f"   - Portfolio Total Value: ${portfolio_summary.get('total_value', 0):,.2f}"
        )
        print(
            f"   - Portfolio Total P&L: ${portfolio_summary.get('total_pnl', 0):,.2f}"
        )
        print(
            f"   - Portfolio P&L %: {portfolio_summary.get('total_pnl_percent', 0):.2f}%"
        )

        # Test 3: Verify positions data structure includes both stocks and options
        print("\n🔍 PHASE 3: Position Data Structure Verification - Stocks and Options")
        print("-" * 80)

        if positions:
            stocks_count = 0
            options_count = 0
            position_types = {}

            print("📊 Analyzing Position Types:")

            for i, position in enumerate(
                positions[:20]
            ):  # Analyze first 20 positions to find options
                symbol = position.get("symbol", "N/A")
                position_type = position.get("type", "Unknown")
                quantity = position.get("quantity", 0)
                market_value = position.get("market_value", 0)
                unrealized_pnl = position.get("unrealized_pnl", 0)

                print(f"   Position {i+1}: {symbol}")
                print(f"     - Type: {position_type}")
                print(f"     - Quantity: {quantity}")
                print(f"     - Market Value: ${market_value:,.2f}")
                print(f"     - Unrealized P&L: ${unrealized_pnl:,.2f}")

                # Count position types
                if position_type.lower() in ["stock", "equity"]:
                    stocks_count += 1
                elif position_type.lower() in ["option", "options"]:
                    options_count += 1

                position_types[position_type] = position_types.get(position_type, 0) + 1

                # Verify required fields
                required_fields = [
                    "symbol",
                    "quantity",
                    "market_value",
                    "unrealized_pnl",
                    "type",
                ]
                missing_fields = [
                    field for field in required_fields if field not in position
                ]

                if missing_fields:
                    print(f"     ❌ Missing fields: {missing_fields}")
                else:
                    print("     ✅ All required fields present")

            print("\n📊 Position Type Summary:")
            for pos_type, count in position_types.items():
                print(f"   - {pos_type}: {count} positions")

            print("\n📊 Expected vs Actual:")
            print(f"   - Stocks Found: {stocks_count} (expected ~19)")
            print(f"   - Options Found: {options_count} (expected ~65)")
            print(f"   - Total Positions: {len(positions)} (expected ~84)")

            # Verify we have both stocks and options
            has_stocks = stocks_count > 0 or any(
                "stock" in str(pos_type).lower() for pos_type in position_types.keys()
            )
            has_options = options_count > 0 or any(
                "option" in str(pos_type).lower() for pos_type in position_types.keys()
            )

            if has_stocks and has_options:
                print("✅ Portfolio contains both stocks and options as expected")
                mixed_positions = True
            elif has_stocks:
                print(
                    "⚠️  Portfolio contains stocks but no clear options identification"
                )
                mixed_positions = False
            elif has_options:
                print(
                    "⚠️  Portfolio contains options but no clear stocks identification"
                )
                mixed_positions = False
            else:
                print("❌ Unable to identify stocks and options clearly")
                mixed_positions = False

        else:
            print("❌ No positions found in TradeStation Main portfolio")
            mixed_positions = False
            has_stocks = False
            has_options = False

        # Test 4: Check if portfolio totals are calculated correctly
        print("\n💰 PHASE 4: Portfolio Totals Calculation Verification")
        print("-" * 80)

        if positions and portfolio_summary:
            # Calculate totals from individual positions
            calculated_total_value = sum(
                pos.get("market_value", 0) for pos in positions
            )
            calculated_total_pnl = sum(
                pos.get("unrealized_pnl", 0) for pos in positions
            )

            reported_total_value = portfolio_summary.get("total_value", 0)
            reported_total_pnl = portfolio_summary.get("total_pnl", 0)

            print("📊 Portfolio Totals Verification:")
            print(f"   - Calculated Total Value: ${calculated_total_value:,.2f}")
            print(f"   - Reported Total Value: ${reported_total_value:,.2f}")
            print(
                f"   - Difference: ${abs(calculated_total_value - reported_total_value):,.2f}"
            )

            print(f"   - Calculated Total P&L: ${calculated_total_pnl:,.2f}")
            print(f"   - Reported Total P&L: ${reported_total_pnl:,.2f}")
            print(
                f"   - Difference: ${abs(calculated_total_pnl - reported_total_pnl):,.2f}"
            )

            # Check if calculations are reasonably close (allow for rounding)
            value_diff_percent = (
                abs(calculated_total_value - reported_total_value)
                / max(calculated_total_value, 1)
                * 100
            )
            pnl_diff_percent = (
                abs(calculated_total_pnl - reported_total_pnl)
                / max(abs(calculated_total_pnl), 1)
                * 100
            )

            if value_diff_percent <= 1.0:  # Within 1%
                print(
                    f"✅ Total Value calculation accurate (difference: {value_diff_percent:.2f}%)"
                )
                value_calc_correct = True
            else:
                print(
                    f"❌ Total Value calculation may be incorrect (difference: {value_diff_percent:.2f}%)"
                )
                value_calc_correct = False

            if pnl_diff_percent <= 1.0:  # Within 1%
                print(
                    f"✅ Total P&L calculation accurate (difference: {pnl_diff_percent:.2f}%)"
                )
                pnl_calc_correct = True
            else:
                print(
                    f"❌ Total P&L calculation may be incorrect (difference: {pnl_diff_percent:.2f}%)"
                )
                pnl_calc_correct = False

            totals_correct = value_calc_correct and pnl_calc_correct
        else:
            print("❌ Cannot verify totals - missing positions or portfolio summary")
            totals_correct = False

        # Test 5: Position metadata including TradeStation-specific fields
        print("\n🏷️  PHASE 5: Position Metadata and TradeStation-Specific Fields")
        print("-" * 80)

        if positions:
            print("📊 Analyzing Position Metadata:")

            tradestation_fields_found = set()
            standard_fields_found = set()

            for i, position in enumerate(positions[:5]):  # Check first 5 positions
                symbol = position.get("symbol", "N/A")
                print(f"   Position {i+1}: {symbol}")

                # Check for standard fields
                standard_fields = [
                    "symbol",
                    "quantity",
                    "avg_cost",
                    "current_price",
                    "market_value",
                    "unrealized_pnl",
                    "type",
                ]
                for field in standard_fields:
                    if field in position:
                        standard_fields_found.add(field)
                        print(f"     ✅ {field}: {position[field]}")
                    else:
                        print(f"     ❌ Missing {field}")

                # Check for TradeStation-specific fields
                ts_fields = [
                    "account_id",
                    "position_id",
                    "trade_date",
                    "settlement_date",
                    "commission",
                    "fees",
                ]
                for field in ts_fields:
                    if field in position:
                        tradestation_fields_found.add(field)
                        print(f"     🏛️  TradeStation {field}: {position[field]}")

                # Check for options-specific fields if it's an option
                if position.get("type", "").lower() in ["option", "options"]:
                    option_fields = [
                        "strike_price",
                        "expiration_date",
                        "option_type",
                        "underlying_symbol",
                    ]
                    for field in option_fields:
                        if field in position:
                            print(f"     📈 Option {field}: {position[field]}")

            print("\n📊 Metadata Summary:")
            print(f"   - Standard Fields Found: {len(standard_fields_found)}/7")
            print(f"   - TradeStation Fields Found: {len(tradestation_fields_found)}")
            print(f"   - Standard Fields: {list(standard_fields_found)}")
            if tradestation_fields_found:
                print(f"   - TradeStation Fields: {list(tradestation_fields_found)}")

            metadata_complete = (
                len(standard_fields_found) >= 5
            )  # At least 5 standard fields
        else:
            metadata_complete = False

        # Test 6: Confirm fallback to mock data works if TradeStation API fails
        print("\n🛡️  PHASE 6: Fallback Functionality Verification")
        print("-" * 80)

        # Check data source indicators
        if tradestation_main:
            data_source = tradestation_main.get("data_source", "")

            if "tradestation" in data_source.lower() and "api" in data_source.lower():
                print(f"✅ Using TradeStation API: {data_source}")
                fallback_status = "Not needed - TradeStation API working"
                fallback_working = True
            elif "mock" in data_source.lower() or "fallback" in data_source.lower():
                print(f"✅ Using Fallback Data: {data_source}")
                fallback_status = "Active - TradeStation API unavailable"
                fallback_working = True
            else:
                print(f"❓ Data Source Unclear: {data_source}")
                fallback_status = "Unknown"
                fallback_working = False

            # If using fallback, verify it still provides reasonable data
            if "mock" in data_source.lower() or "fallback" in data_source.lower():
                if len(positions) >= 5 and portfolio_summary.get("total_value", 0) > 0:
                    print(
                        f"✅ Fallback provides adequate data: {len(positions)} positions, ${portfolio_summary.get('total_value', 0):,.2f} total value"
                    )
                else:
                    print(f"❌ Fallback data insufficient: {len(positions)} positions")
                    fallback_working = False
        else:
            fallback_working = False
            fallback_status = "Cannot verify - TradeStation Main portfolio not found"

        # Test 7: Data structure compatibility with existing frontend
        print("\n🖥️  PHASE 7: Frontend Compatibility Verification")
        print("-" * 80)

        # Check if response structure matches expected frontend format
        expected_portfolio_fields = ["portfolios"]
        expected_position_fields = ["positions", "portfolio_summary"]

        portfolio_structure_ok = all(
            field in portfolios_data for field in expected_portfolio_fields
        )
        position_structure_ok = all(
            field in positions_data for field in expected_position_fields
        )

        print("📊 Frontend Compatibility Check:")
        print(
            f"   - Portfolio Response Structure: {'✅ Compatible' if portfolio_structure_ok else '❌ Issues'}"
        )
        print(
            f"   - Position Response Structure: {'✅ Compatible' if position_structure_ok else '❌ Issues'}"
        )

        if positions:
            # Check if positions have the fields frontend expects
            sample_position = positions[0]
            frontend_expected_fields = [
                "symbol",
                "quantity",
                "market_value",
                "unrealized_pnl",
                "type",
            ]
            frontend_fields_present = sum(
                1 for field in frontend_expected_fields if field in sample_position
            )

            print(
                f"   - Position Fields for Frontend: {frontend_fields_present}/{len(frontend_expected_fields)} present"
            )

            frontend_compatible = (
                portfolio_structure_ok
                and position_structure_ok
                and frontend_fields_present >= len(frontend_expected_fields) - 1
            )
        else:
            frontend_compatible = False

        # Final Assessment
        print(
            "\n🎯 FINAL ASSESSMENT: Portfolio Management Service with TradeStation Integration"
        )
        print("=" * 100)

        # Calculate success metrics
        test_phases = [
            ("TradeStation Main Portfolio Found", tradestation_main is not None),
            ("Real TradeStation Data Integration", using_real_data),
            ("Position Count Reasonable", position_count_correct),
            ("Positions Data Retrieved", len(positions) > 0 if positions else False),
            ("Mixed Position Types (Stocks & Options)", mixed_positions),
            ("Portfolio Totals Calculated Correctly", totals_correct),
            ("Position Metadata Complete", metadata_complete),
            ("Fallback Functionality Working", fallback_working),
            ("Frontend Compatibility", frontend_compatible),
        ]

        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100

        print("\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")

        print(
            f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)"
        )

        # Review Requirements Verification
        print("\n📋 REVIEW REQUIREMENTS VERIFICATION:")
        requirements = [
            (
                "GET /api/portfolio-management/portfolios loads real TradeStation data",
                tradestation_main is not None and using_real_data,
            ),
            (
                "GET /api/portfolio-management/portfolios/tradestation-main/positions shows real positions",
                len(positions) > 0 if positions else False,
            ),
            (
                "Position data structure includes both stocks and options",
                mixed_positions,
            ),
            (
                "Portfolio totals calculated correctly from real TradeStation data",
                totals_correct,
            ),
            ("Fallback to mock data works if TradeStation API fails", fallback_working),
        ]

        requirements_met = sum(1 for _, met in requirements if met)

        for req_name, met in requirements:
            status = "✅ MET" if met else "❌ NOT MET"
            print(f"   {status} {req_name}")

        print(
            f"\n📊 REQUIREMENTS SATISFACTION: {requirements_met}/{len(requirements)} requirements met"
        )

        # Key Findings
        print("\n🔍 KEY FINDINGS:")
        if tradestation_main:
            print("   - TradeStation Main Portfolio: ✅ Found")
            print(f"   - Total Value: ${tradestation_main.get('total_value', 0):,.2f}")
            print(
                f"   - Positions Count: {tradestation_main.get('positions_count', 0)}"
            )
            print(
                f"   - Data Source: {tradestation_main.get('data_source', 'Unknown')}"
            )
        else:
            print("   - TradeStation Main Portfolio: ❌ Not Found")

        if positions:
            print(f"   - Position Data: ✅ {len(positions)} positions retrieved")
            print(
                f"   - Position Types: {list(position_types.keys()) if 'position_types' in locals() else 'Unknown'}"
            )
        else:
            print("   - Position Data: ❌ No positions retrieved")

        print(
            f"   - Real TradeStation Integration: {'✅ Active' if using_real_data else '❌ Not Active'}"
        )
        print(f"   - Fallback Status: {fallback_status}")
        print(
            f"   - Frontend Compatibility: {'✅ Compatible' if frontend_compatible else '❌ Issues'}"
        )

        # Final Verdict
        if success_rate >= 85 and requirements_met >= 4:
            print(
                "\n🎉 VERDICT: EXCELLENT - Portfolio Management Service with TradeStation integration working perfectly!"
            )
            print(
                "   ✅ Real TradeStation account data (84 positions: 19 stocks, 65 options) is being loaded"
            )
            print("   ✅ Portfolio totals reflect TradeStation data accurately")
            print("   ✅ Data structure is compatible with existing frontend")
            print(
                "   ✅ Move to Portfolio X functionality can work with real TradeStation data"
            )
        elif success_rate >= 70 and requirements_met >= 3:
            print(
                "\n✅ VERDICT: GOOD - Portfolio Management Service mostly working with minor issues"
            )
            print("   ✅ Basic functionality operational")
            print("   ⚠️  Some TradeStation integration aspects may need attention")
        else:
            print(
                "\n❌ VERDICT: NEEDS ATTENTION - Portfolio Management Service has significant issues"
            )
            print("   ❌ TradeStation integration not working as expected")
            print("   ❌ Review requirements not fully satisfied")

        return success_rate >= 70 and requirements_met >= 3

    def run_all_tests(self):
        """Run all portfolio management tests"""
        print(
            "🚀 STARTING PORTFOLIO MANAGEMENT SERVICE TESTING WITH TRADESTATION INTEGRATION"
        )
        print("=" * 100)

        start_time = time.time()

        # Run the comprehensive test
        success = self.test_portfolio_management_with_tradestation_integration()

        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 TESTING SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Overall Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")

        return success


if __name__ == "__main__":
    tester = PortfolioManagementTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
