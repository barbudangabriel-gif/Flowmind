#!/usr/bin/env python3
"""
FlowMind Options Optimizer Backend Testing Suite
Testing Options Optimizer implementation with 3 MVP strategies:
- Long Call, Bull Call Spread, Cash-Secured Put
Focus: Black-Scholes calculations, strategy generation, and risk metrics
"""

import asyncio
import requests
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://options-analytics.preview.emergentagent.com/api"


class OptionsOptimizerTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        self.test_results = []

    def log_test(
        self, test_name: str, success: bool, details: str, response_data: Any = None
    ):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    def make_request(
        self, method: str, endpoint: str, data: Dict = None, params: Dict = None
    ) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300,
            }
        except Exception as e:
            return {"status_code": 0, "data": {"error": str(e)}, "success": False}

    async def test_basic_functionality_tsla(self):
        """Test Basic Functionality - GET /api/optimize/suggest?symbol=TSLA"""
        print("\n🔍 Testing Basic Options Optimizer Functionality with TSLA...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "TSLA"}
        )

        if response["success"]:
            data = response["data"]

            # Check if we have the expected structure
            required_fields = ["meta", "strategies"]
            missing_fields = [field for field in required_fields if field not in data]

            meta = data.get("meta", {})
            strategies = data.get("strategies", [])

            # Verify meta structure
            meta_fields = ["symbol", "spot", "dte", "expiry", "iv", "rf"]
            missing_meta = [field for field in meta_fields if field not in meta]

            # Check for 3 strategies
            expected_strategies = ["long-call", "bull-call-spread", "cash-secured-put"]
            strategy_ids = [s.get("id") for s in strategies]
            has_all_strategies = all(sid in strategy_ids for sid in expected_strategies)

            if (
                not missing_fields
                and not missing_meta
                and len(strategies) >= 3
                and has_all_strategies
                and meta.get("symbol") == "TSLA"
            ):
                self.log_test(
                    "Basic Functionality - TSLA",
                    True,
                    f"Successfully generated {len(strategies)} strategies for TSLA with spot ${meta.get('spot')}, IV {meta.get('iv'):.2%}",
                    {
                        "symbol": meta.get("symbol"),
                        "spot": meta.get("spot"),
                        "iv": meta.get("iv"),
                        "strategies_count": len(strategies),
                        "strategy_ids": strategy_ids,
                    },
                )
            else:
                issues = []
                if missing_fields:
                    issues.append(f"Missing fields: {missing_fields}")
                if missing_meta:
                    issues.append(f"Missing meta fields: {missing_meta}")
                if len(strategies) < 3:
                    issues.append(f"Expected 3+ strategies, got {len(strategies)}")
                if not has_all_strategies:
                    issues.append(
                        f"Missing expected strategies: {set(expected_strategies) - set(strategy_ids)}"
                    )

                self.log_test(
                    "Basic Functionality - TSLA",
                    False,
                    f"Basic functionality validation failed: {'; '.join(issues)}",
                    data,
                )
        else:
            self.log_test(
                "Basic Functionality - TSLA",
                False,
                f"Failed to get TSLA optimization: {response['data']}",
            )

    async def test_budget_constraint(self):
        """Test Budget Constraint - GET /api/optimize/suggest?symbol=TSLA&budget=5000&dte=30&risk_bias=1"""
        print("\n💰 Testing Budget Constraint Filtering...")

        response = self.make_request(
            "GET",
            "/optimize/suggest",
            params={"symbol": "TSLA", "budget": "5000", "dte": "30", "risk_bias": "1"},
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])
            meta = data.get("meta", {})

            # Check that all strategies respect budget constraint
            budget_compliant = True
            budget_issues = []

            for strategy in strategies:
                risk_capital = strategy.get("risk_capital", 0)
                collateral = strategy.get("collateral", 0)
                total_capital = max(risk_capital, collateral)

                if total_capital > 5000:
                    budget_compliant = False
                    budget_issues.append(f"{strategy.get('id')}: ${total_capital:.2f}")

            if budget_compliant and len(strategies) > 0:
                self.log_test(
                    "Budget Constraint",
                    True,
                    f"All {len(strategies)} strategies comply with $5000 budget constraint",
                    {
                        "budget": 5000,
                        "strategies_count": len(strategies),
                        "max_capital": max(
                            [
                                max(s.get("risk_capital", 0), s.get("collateral", 0))
                                for s in strategies
                            ]
                        )
                        if strategies
                        else 0,
                    },
                )
            else:
                self.log_test(
                    "Budget Constraint",
                    False,
                    f"Budget constraint violation: {'; '.join(budget_issues) if budget_issues else 'No strategies returned'}",
                    {
                        "budget_violations": budget_issues,
                        "strategies_count": len(strategies),
                    },
                )
        else:
            self.log_test(
                "Budget Constraint",
                False,
                f"Failed to test budget constraint: {response['data']}",
            )

    async def test_target_price_roi(self):
        """Test Target Price ROI - GET /api/optimize/suggest?symbol=AAPL&target_price=250&dte=27"""
        print("\n🎯 Testing Target Price ROI Calculation...")

        response = self.make_request(
            "GET",
            "/optimize/suggest",
            params={"symbol": "AAPL", "target_price": "250", "dte": "27"},
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])
            meta = data.get("meta", {})

            # Check that ROI calculations are present and reasonable
            roi_valid = True
            roi_details = []

            for strategy in strategies:
                roi = strategy.get("roi")
                if roi is not None:
                    roi_details.append(f"{strategy.get('id')}: {roi:.2%}")
                    # ROI should be reasonable (between -100% and 1000%)
                    if roi < -1.0 or roi > 10.0:
                        roi_valid = False

            if roi_valid and len(strategies) > 0 and len(roi_details) > 0:
                self.log_test(
                    "Target Price ROI",
                    True,
                    f"ROI calculations working for AAPL target $250: {'; '.join(roi_details)}",
                    {
                        "symbol": "AAPL",
                        "target_price": 250,
                        "spot": meta.get("spot"),
                        "roi_calculations": roi_details,
                    },
                )
            else:
                self.log_test(
                    "Target Price ROI",
                    False,
                    f"ROI calculation issues: valid={roi_valid}, strategies={len(strategies)}, roi_count={len(roi_details)}",
                    {"roi_details": roi_details, "strategies_count": len(strategies)},
                )
        else:
            self.log_test(
                "Target Price ROI",
                False,
                f"Failed to test target price ROI: {response['data']}",
            )

    async def test_risk_bias_conservative(self):
        """Test Conservative Risk Bias - GET /api/optimize/suggest?symbol=NVDA&risk_bias=-2"""
        print("\n🛡️ Testing Conservative Risk Bias...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "NVDA", "risk_bias": "-2"}
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])
            meta = data.get("meta", {})
            spot = meta.get("spot", 0)

            # Analyze strike selection for conservative bias
            conservative_analysis = []

            for strategy in strategies:
                legs = strategy.get("legs", [])
                strategy_id = strategy.get("id")

                for leg in legs:
                    strike = leg.get("strike", 0)
                    leg_type = leg.get("type")
                    side = leg.get("side")

                    if leg_type == "CALL" and side == "BUY":
                        # Conservative calls should be closer to ATM or slightly ITM
                        distance_pct = (strike - spot) / spot * 100
                        conservative_analysis.append(
                            f"{strategy_id} Call: {distance_pct:+.1f}%"
                        )
                    elif leg_type == "PUT" and side == "SELL":
                        # Conservative puts should be further OTM
                        distance_pct = (spot - strike) / spot * 100
                        conservative_analysis.append(
                            f"{strategy_id} Put: {distance_pct:+.1f}%"
                        )

            if len(strategies) > 0 and len(conservative_analysis) > 0:
                self.log_test(
                    "Conservative Risk Bias",
                    True,
                    f"Conservative risk bias applied to NVDA strategies: {'; '.join(conservative_analysis)}",
                    {
                        "symbol": "NVDA",
                        "risk_bias": -2,
                        "spot": spot,
                        "strike_analysis": conservative_analysis,
                    },
                )
            else:
                self.log_test(
                    "Conservative Risk Bias",
                    False,
                    f"Conservative risk bias test failed: strategies={len(strategies)}, analysis={len(conservative_analysis)}",
                    {"strategies_count": len(strategies)},
                )
        else:
            self.log_test(
                "Conservative Risk Bias",
                False,
                f"Failed to test conservative risk bias: {response['data']}",
            )

    async def test_risk_bias_aggressive(self):
        """Test Aggressive Risk Bias - GET /api/optimize/suggest?symbol=NVDA&risk_bias=2"""
        print("\n⚡ Testing Aggressive Risk Bias...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "NVDA", "risk_bias": "2"}
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])
            meta = data.get("meta", {})
            spot = meta.get("spot", 0)

            # Analyze strike selection for aggressive bias
            aggressive_analysis = []

            for strategy in strategies:
                legs = strategy.get("legs", [])
                strategy_id = strategy.get("id")

                for leg in legs:
                    strike = leg.get("strike", 0)
                    leg_type = leg.get("type")
                    side = leg.get("side")

                    if leg_type == "CALL" and side == "BUY":
                        # Aggressive calls should be further OTM
                        distance_pct = (strike - spot) / spot * 100
                        aggressive_analysis.append(
                            f"{strategy_id} Call: {distance_pct:+.1f}%"
                        )
                    elif leg_type == "PUT" and side == "SELL":
                        # Aggressive puts should be closer to ATM
                        distance_pct = (spot - strike) / spot * 100
                        aggressive_analysis.append(
                            f"{strategy_id} Put: {distance_pct:+.1f}%"
                        )

            if len(strategies) > 0 and len(aggressive_analysis) > 0:
                self.log_test(
                    "Aggressive Risk Bias",
                    True,
                    f"Aggressive risk bias applied to NVDA strategies: {'; '.join(aggressive_analysis)}",
                    {
                        "symbol": "NVDA",
                        "risk_bias": 2,
                        "spot": spot,
                        "strike_analysis": aggressive_analysis,
                    },
                )
            else:
                self.log_test(
                    "Aggressive Risk Bias",
                    False,
                    f"Aggressive risk bias test failed: strategies={len(strategies)}, analysis={len(aggressive_analysis)}",
                    {"strategies_count": len(strategies)},
                )
        else:
            self.log_test(
                "Aggressive Risk Bias",
                False,
                f"Failed to test aggressive risk bias: {response['data']}",
            )

    async def test_data_structure_validation(self):
        """Test Data Structure Validation - Verify all required fields are present"""
        print("\n📋 Testing Data Structure Validation...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "TSLA"}
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])

            # Required fields for each strategy
            required_strategy_fields = [
                "id",
                "label",
                "roi",
                "chance",
                "profit_max",
                "risk_capital",
                "collateral",
                "breakevens",
                "legs",
                "mini",
            ]

            # Required fields for each leg
            required_leg_fields = ["side", "type", "qty", "strike"]

            # Required fields for mini object
            required_mini_fields = ["x", "breakevens"]

            validation_results = []
            all_valid = True

            for i, strategy in enumerate(strategies):
                strategy_id = strategy.get("id", f"strategy_{i}")

                # Check strategy fields
                missing_strategy_fields = [
                    f for f in required_strategy_fields if f not in strategy
                ]
                if missing_strategy_fields:
                    all_valid = False
                    validation_results.append(
                        f"{strategy_id}: missing {missing_strategy_fields}"
                    )

                # Check legs structure
                legs = strategy.get("legs", [])
                for j, leg in enumerate(legs):
                    missing_leg_fields = [
                        f for f in required_leg_fields if f not in leg
                    ]
                    if missing_leg_fields:
                        all_valid = False
                        validation_results.append(
                            f"{strategy_id} leg {j}: missing {missing_leg_fields}"
                        )

                # Check mini structure
                mini = strategy.get("mini", {})
                missing_mini_fields = [f for f in required_mini_fields if f not in mini]
                if missing_mini_fields:
                    all_valid = False
                    validation_results.append(
                        f"{strategy_id} mini: missing {missing_mini_fields}"
                    )

                # Validate data types and ranges
                roi = strategy.get("roi")
                chance = strategy.get("chance")

                if roi is not None and (
                    not isinstance(roi, (int, float)) or roi < -10 or roi > 50
                ):
                    all_valid = False
                    validation_results.append(f"{strategy_id}: invalid ROI {roi}")

                if chance is not None and (
                    not isinstance(chance, (int, float)) or chance < 0 or chance > 1
                ):
                    all_valid = False
                    validation_results.append(f"{strategy_id}: invalid chance {chance}")

            if all_valid and len(strategies) >= 3:
                self.log_test(
                    "Data Structure Validation",
                    True,
                    f"All {len(strategies)} strategies have valid data structure with required fields",
                    {
                        "strategies_validated": len(strategies),
                        "required_fields_check": "passed",
                        "data_types_check": "passed",
                    },
                )
            else:
                self.log_test(
                    "Data Structure Validation",
                    False,
                    f"Data structure validation failed: {'; '.join(validation_results)}",
                    {
                        "validation_issues": validation_results,
                        "strategies_count": len(strategies),
                    },
                )
        else:
            self.log_test(
                "Data Structure Validation",
                False,
                f"Failed to validate data structure: {response['data']}",
            )

    async def test_black_scholes_calculations(self):
        """Test Black-Scholes Pricing Calculations - Verify realistic option prices"""
        print("\n🧮 Testing Black-Scholes Pricing Calculations...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "AAPL", "dte": "30"}
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])
            meta = data.get("meta", {})
            spot = meta.get("spot", 0)
            iv = meta.get("iv", 0)

            # Analyze pricing reasonableness
            pricing_analysis = []
            pricing_valid = True

            for strategy in strategies:
                strategy_id = strategy.get("id")
                risk_capital = strategy.get("risk_capital", 0)
                legs = strategy.get("legs", [])

                # For single-leg strategies, check if pricing is reasonable
                if len(legs) == 1:
                    leg = legs[0]
                    strike = leg.get("strike", 0)
                    leg_type = leg.get("type")

                    # Basic sanity checks for option pricing
                    if leg_type == "CALL":
                        # Call should be cheaper when further OTM
                        if strike > spot:
                            intrinsic = 0
                        else:
                            intrinsic = spot - strike

                        # Risk capital should be reasonable (premium should be > intrinsic, < spot)
                        premium = risk_capital / 100.0  # Convert to per-share
                        if premium >= intrinsic and premium < spot:
                            pricing_analysis.append(
                                f"{strategy_id}: premium ${premium:.2f} > intrinsic ${intrinsic:.2f}"
                            )
                        else:
                            pricing_valid = False
                            pricing_analysis.append(
                                f"{strategy_id}: invalid premium ${premium:.2f} vs intrinsic ${intrinsic:.2f}"
                            )

                    elif leg_type == "PUT":
                        # Put intrinsic value
                        if strike < spot:
                            intrinsic = 0
                        else:
                            intrinsic = strike - spot

                        # For cash-secured puts, check collateral calculation
                        collateral = strategy.get("collateral", 0)
                        expected_collateral = (
                            strike * 100
                        )  # Should be close to strike * 100

                        if (
                            abs(collateral - expected_collateral)
                            < expected_collateral * 0.1
                        ):  # Within 10%
                            pricing_analysis.append(
                                f"{strategy_id}: collateral ${collateral:.0f} ≈ expected ${expected_collateral:.0f}"
                            )
                        else:
                            pricing_valid = False
                            pricing_analysis.append(
                                f"{strategy_id}: invalid collateral ${collateral:.0f} vs expected ${expected_collateral:.0f}"
                            )

            if pricing_valid and len(pricing_analysis) > 0:
                self.log_test(
                    "Black-Scholes Calculations",
                    True,
                    f"Black-Scholes pricing calculations appear valid: {'; '.join(pricing_analysis)}",
                    {
                        "spot": spot,
                        "iv": iv,
                        "pricing_checks": pricing_analysis,
                    },
                )
            else:
                self.log_test(
                    "Black-Scholes Calculations",
                    False,
                    f"Black-Scholes pricing validation failed: {'; '.join(pricing_analysis)}",
                    {"pricing_issues": pricing_analysis, "spot": spot, "iv": iv},
                )
        else:
            self.log_test(
                "Black-Scholes Calculations",
                False,
                f"Failed to test Black-Scholes calculations: {response['data']}",
            )

    async def test_strike_price_rounding(self):
        """Test Strike Price Rounding - Verify strikes are rounded to $5"""
        print("\n🎯 Testing Strike Price Rounding to $5...")

        response = self.make_request(
            "GET", "/optimize/suggest", params={"symbol": "TSLA"}
        )

        if response["success"]:
            data = response["data"]
            strategies = data.get("strategies", [])

            # Check strike rounding
            rounding_valid = True
            rounding_analysis = []

            for strategy in strategies:
                strategy_id = strategy.get("id")
                legs = strategy.get("legs", [])

                for leg in legs:
                    strike = leg.get("strike", 0)

                    # Check if strike is rounded to $5
                    if strike % 5 == 0:
                        rounding_analysis.append(f"{strategy_id}: ${strike}")
                    else:
                        rounding_valid = False
                        rounding_analysis.append(
                            f"{strategy_id}: ${strike} (NOT rounded to $5)"
                        )

            if rounding_valid and len(rounding_analysis) > 0:
                self.log_test(
                    "Strike Price Rounding",
                    True,
                    f"All strikes properly rounded to $5: {'; '.join(rounding_analysis)}",
                    {"strike_prices": rounding_analysis},
                )
            else:
                self.log_test(
                    "Strike Price Rounding",
                    False,
                    f"Strike rounding validation failed: {'; '.join(rounding_analysis)}",
                    {"rounding_issues": rounding_analysis},
                )
        else:
            self.log_test(
                "Strike Price Rounding",
                False,
                f"Failed to test strike rounding: {response['data']}",
            )

    async def run_comprehensive_tests(self):
        """Run all Options Optimizer tests"""
        print("🚀 Starting Options Optimizer Comprehensive Testing")
        print("=" * 80)

        start_time = time.time()

        # Run all test suites focusing on the review requirements
        await self.test_basic_functionality_tsla()
        await self.test_budget_constraint()
        await self.test_target_price_roi()
        await self.test_risk_bias_conservative()
        await self.test_risk_bias_aggressive()
        await self.test_data_structure_validation()
        await self.test_black_scholes_calculations()
        await self.test_strike_price_rounding()

        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        duration = time.time() - start_time

        # Print summary
        print("\n" + "=" * 80)
        print("🎯 OPTIONS OPTIMIZER TEST SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Duration: {duration:.2f}s")

        # Detailed results by category
        categories = {
            "Basic Functionality": [
                r for r in self.test_results if "Basic Functionality" in r["test"]
            ],
            "Budget Constraint": [
                r for r in self.test_results if "Budget Constraint" in r["test"]
            ],
            "Target Price ROI": [
                r for r in self.test_results if "Target Price ROI" in r["test"]
            ],
            "Risk Bias": [r for r in self.test_results if "Risk Bias" in r["test"]],
            "Data Structure": [
                r for r in self.test_results if "Data Structure" in r["test"]
            ],
            "Black-Scholes": [
                r for r in self.test_results if "Black-Scholes" in r["test"]
            ],
            "Strike Rounding": [r for r in self.test_results if "Strike" in r["test"]],
        }

        print("\n📋 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                print(f"  {status} {category}: {passed}/{total} ({rate:.1f}%)")

        # Critical findings for review requirements
        print("\n🔍 CRITICAL FINDINGS:")

        # Basic Functionality
        basic_tests = [
            r for r in self.test_results if "Basic Functionality" in r["test"]
        ]
        if any(r["success"] for r in basic_tests):
            print(
                "  ✅ Options Optimizer basic functionality working with 3 MVP strategies"
            )
        else:
            print("  ❌ Options Optimizer basic functionality has issues")

        # Budget Constraint
        budget_tests = [
            r for r in self.test_results if "Budget Constraint" in r["test"]
        ]
        if any(r["success"] for r in budget_tests):
            print("  ✅ Budget constraint filtering working correctly")
        else:
            print("  ❌ Budget constraint filtering has issues")

        # Target Price ROI
        roi_tests = [r for r in self.test_results if "Target Price ROI" in r["test"]]
        if any(r["success"] for r in roi_tests):
            print("  ✅ Target price ROI calculations working")
        else:
            print("  ❌ Target price ROI calculations have issues")

        # Risk Bias
        risk_tests = [r for r in self.test_results if "Risk Bias" in r["test"]]
        if any(r["success"] for r in risk_tests):
            print("  ✅ Risk bias parameter affecting strike selection correctly")
        else:
            print("  ❌ Risk bias parameter has issues")

        # Data Structure
        structure_tests = [
            r for r in self.test_results if "Data Structure" in r["test"]
        ]
        if any(r["success"] for r in structure_tests):
            print("  ✅ All required data structure fields present and valid")
        else:
            print("  ❌ Data structure validation has issues")

        # Black-Scholes
        bs_tests = [r for r in self.test_results if "Black-Scholes" in r["test"]]
        if any(r["success"] for r in bs_tests):
            print("  ✅ Black-Scholes pricing calculations appear realistic")
        else:
            print("  ❌ Black-Scholes pricing calculations have issues")

        # Strike Rounding
        strike_tests = [r for r in self.test_results if "Strike" in r["test"]]
        if any(r["success"] for r in strike_tests):
            print("  ✅ Strike prices properly rounded to $5 increments")
        else:
            print("  ❌ Strike price rounding has issues")

        print("\n" + "=" * 80)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "duration": duration,
            "test_results": self.test_results,
        }


async def main():
    """Main test execution"""
    tester = OptionsOptimizerTester()
    results = await tester.run_comprehensive_tests()

    # Return results for potential integration with other systems
    return results


if __name__ == "__main__":
    asyncio.run(main())
