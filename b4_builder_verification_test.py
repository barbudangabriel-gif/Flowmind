#!/usr/bin/env python3
"""
B4/6 Builder Backend Verification Test
Quick verification that Builder backend continues to work properly after frontend Save Trade implementation.

Test Scope:
1. Builder Price Endpoint: Confirm POST /api/builder/price returns complete data structure for save payload
2. Greeks Data: Verify all 4 Greeks (delta, gamma, theta, vega) are included in response
3. Chart Data: Confirm chart.series with xy data is provided for PNG export
4. Meta Data: Verify meta section includes spot price and IV data

Test Cases:
- Long Call TSLA $250: Should return complete response with pricing, greeks, chart, meta
- Verify response structure matches canonical save payload requirements
"""

import asyncio
import requests
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000/api"


class B4BuilderVerificationTester:
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

    async def test_builder_price_endpoint_long_call_tsla_250(self):
        """Test Builder Price Endpoint - Long Call TSLA $250"""
        print("\n🎯 Testing Builder Price Endpoint - Long Call TSLA $250...")

        # Long Call TSLA $250 strategy payload as specified in review
        payload = {
            "symbol": "TSLA",
            "expiry": "2025-02-21",
            "dte": 30,
            "spot_override": 333.87,  # Use realistic TSLA price
            "iv_atm": 0.40,  # 40% IV
            "legs": [
                {
                    "type": "CALL",
                    "strike": 250.0,  # $250 strike as specified
                    "side": "BUY",
                    "qty": 1,
                }
            ],
            "qty": 1,
            "range_pct": 0.15,
            "iv_mult": 1.0,
        }

        response = self.make_request("POST", "/builder/price", data=payload)

        if response["success"]:
            data = response["data"]

            # Verify complete data structure for save payload
            required_sections = ["pricing", "greeks", "chart", "meta"]
            missing_sections = [
                section for section in required_sections if section not in data
            ]

            # Verify pricing section (for save payload)
            pricing = data.get("pricing", {})
            pricing_fields = [
                "net_debit",
                "net_credit",
                "max_loss",
                "max_profit",
                "chance_profit",
                "breakevens",
            ]
            missing_pricing = [
                field for field in pricing_fields if field not in pricing
            ]

            # Verify Greeks data (all 4 Greeks required)
            greeks = data.get("greeks", {})
            required_greeks = ["delta", "gamma", "theta", "vega"]
            missing_greeks = [greek for greek in required_greeks if greek not in greeks]

            # Verify chart data (for PNG export)
            chart = data.get("chart", {})
            chart_fields = ["series", "x_min", "x_max"]
            missing_chart = [field for field in chart_fields if field not in chart]

            # Verify chart.series with xy data
            series = chart.get("series", [])
            has_xy_data = (
                len(series) > 0
                and "xy" in series[0]
                and len(series[0]["xy"]) > 200  # Sufficient data points for PNG export
            )

            # Verify meta data (spot price and IV data)
            meta = data.get("meta", {})
            meta_fields = ["symbol", "spot", "iv_atm", "iv_eff"]
            missing_meta = [field for field in meta_fields if field not in meta]

            # Validate data quality for Long Call TSLA $250
            spot_price = meta.get("spot", 0)
            net_debit = pricing.get("net_debit", 0)
            chance_profit = pricing.get("chance_profit", 0)
            delta = greeks.get("delta", 0)
            gamma = greeks.get("gamma", 0)
            theta = greeks.get("theta", 0)
            vega = greeks.get("vega", 0)

            # Quality checks for Long Call TSLA $250
            spot_reasonable = 300.0 <= spot_price <= 400.0  # TSLA price range
            debit_positive = net_debit > 0  # Long call should cost premium
            chance_valid = 0 <= chance_profit <= 1  # Probability range
            delta_valid = 0.5 <= delta <= 1.0  # Deep ITM call should have high delta
            gamma_positive = gamma > 0  # Long options have positive gamma
            theta_negative = theta < 0  # Long options lose time value
            vega_positive = vega > 0  # Long options benefit from IV increase

            complete_structure = (
                not missing_sections
                and not missing_pricing
                and not missing_greeks
                and not missing_chart
                and not missing_meta
                and has_xy_data
            )

            data_quality_valid = (
                spot_reasonable
                and debit_positive
                and chance_valid
                and delta_valid
                and gamma_positive
                and theta_negative
                and vega_positive
            )

            if complete_structure and data_quality_valid:
                self.log_test(
                    "Builder Price Endpoint - Long Call TSLA $250",
                    True,
                    f"Complete save payload structure: ${net_debit:.2f} debit, {chance_profit:.2%} chance, δ={delta:.3f}, γ={gamma:.6f}, θ={theta:.4f}, ν={vega:.4f}",
                    {
                        "symbol": meta.get("symbol"),
                        "spot": spot_price,
                        "net_debit": net_debit,
                        "chance_profit": chance_profit,
                        "greeks": {
                            "delta": delta,
                            "gamma": gamma,
                            "theta": theta,
                            "vega": vega,
                        },
                        "chart_points": len(series[0]["xy"]) if series else 0,
                        "complete_structure": True,
                    },
                )
            else:
                issues = []
                if missing_sections:
                    issues.append(f"Missing sections: {missing_sections}")
                if missing_pricing:
                    issues.append(f"Missing pricing fields: {missing_pricing}")
                if missing_greeks:
                    issues.append(f"Missing Greeks: {missing_greeks}")
                if missing_chart:
                    issues.append(f"Missing chart fields: {missing_chart}")
                if missing_meta:
                    issues.append(f"Missing meta fields: {missing_meta}")
                if not has_xy_data:
                    issues.append("Insufficient chart xy data for PNG export")
                if not spot_reasonable:
                    issues.append(f"Unreasonable spot price: {spot_price}")
                if not debit_positive:
                    issues.append(f"Expected positive debit: {net_debit}")
                if not chance_valid:
                    issues.append(f"Invalid chance of profit: {chance_profit}")
                if not delta_valid:
                    issues.append(f"Invalid delta for deep ITM call: {delta}")
                if not gamma_positive:
                    issues.append(f"Expected positive gamma: {gamma}")
                if not theta_negative:
                    issues.append(f"Expected negative theta: {theta}")
                if not vega_positive:
                    issues.append(f"Expected positive vega: {vega}")

                self.log_test(
                    "Builder Price Endpoint - Long Call TSLA $250",
                    False,
                    f"Save payload structure validation failed: {'; '.join(issues)}",
                    data,
                )
        else:
            self.log_test(
                "Builder Price Endpoint - Long Call TSLA $250",
                False,
                f"Failed to get Builder price response: {response['data']}",
            )

    async def test_greeks_data_verification(self):
        """Test Greeks Data - Verify all 4 Greeks (delta, gamma, theta, vega) are included"""
        print("\n📊 Testing Greeks Data Verification - All 4 Greeks...")

        # Test with Bull Call Spread to verify Greeks aggregation
        payload = {
            "symbol": "TSLA",
            "expiry": "2025-02-21",
            "dte": 30,
            "spot_override": 333.87,
            "iv_atm": 0.40,
            "legs": [
                {"type": "CALL", "strike": 330.0, "side": "BUY", "qty": 1},
                {"type": "CALL", "strike": 350.0, "side": "SELL", "qty": 1},
            ],
            "qty": 1,
        }

        response = self.make_request("POST", "/builder/price", data=payload)

        if response["success"]:
            data = response["data"]
            greeks = data.get("greeks", {})

            # Verify all 4 Greeks are present
            required_greeks = ["delta", "gamma", "theta", "vega"]
            present_greeks = [greek for greek in required_greeks if greek in greeks]
            missing_greeks = [greek for greek in required_greeks if greek not in greeks]

            # Verify Greeks values are numeric and reasonable
            delta = greeks.get("delta", 0)
            gamma = greeks.get("gamma", 0)
            theta = greeks.get("theta", 0)
            vega = greeks.get("vega", 0)

            # Greeks validation for Bull Call Spread
            delta_reasonable = -1.0 <= delta <= 1.0  # Delta range
            gamma_reasonable = -0.1 <= gamma <= 0.1  # Gamma can be negative for spreads
            theta_reasonable = -10.0 <= theta <= 10.0  # Theta range
            vega_reasonable = -100.0 <= vega <= 100.0  # Vega range

            all_greeks_present = len(missing_greeks) == 0
            all_greeks_reasonable = (
                delta_reasonable
                and gamma_reasonable
                and theta_reasonable
                and vega_reasonable
            )

            if all_greeks_present and all_greeks_reasonable:
                self.log_test(
                    "Greeks Data Verification",
                    True,
                    f"All 4 Greeks present and valid: δ={delta:.4f}, γ={gamma:.6f}, θ={theta:.4f}, ν={vega:.4f}",
                    {
                        "greeks_present": present_greeks,
                        "delta": delta,
                        "gamma": gamma,
                        "theta": theta,
                        "vega": vega,
                        "all_reasonable": True,
                    },
                )
            else:
                issues = []
                if missing_greeks:
                    issues.append(f"Missing Greeks: {missing_greeks}")
                if not delta_reasonable:
                    issues.append(f"Delta out of range: {delta}")
                if not gamma_reasonable:
                    issues.append(f"Gamma out of range: {gamma}")
                if not theta_reasonable:
                    issues.append(f"Theta out of range: {theta}")
                if not vega_reasonable:
                    issues.append(f"Vega out of range: {vega}")

                self.log_test(
                    "Greeks Data Verification",
                    False,
                    f"Greeks validation failed: {'; '.join(issues)}",
                    {"greeks": greeks, "issues": issues},
                )
        else:
            self.log_test(
                "Greeks Data Verification",
                False,
                f"Failed to get Greeks data: {response['data']}",
            )

    async def test_chart_data_png_export(self):
        """Test Chart Data - Confirm chart.series with xy data for PNG export"""
        print("\n📈 Testing Chart Data for PNG Export...")

        # Test with simple Long Put to verify chart data structure
        payload = {
            "symbol": "TSLA",
            "expiry": "2025-02-21",
            "dte": 30,
            "spot_override": 333.87,
            "iv_atm": 0.40,
            "legs": [
                {
                    "type": "PUT",
                    "strike": 320.0,
                    "side": "BUY",
                    "qty": 1,
                }
            ],
            "qty": 1,
        }

        response = self.make_request("POST", "/builder/price", data=payload)

        if response["success"]:
            data = response["data"]
            chart = data.get("chart", {})

            # Verify chart structure for PNG export
            required_chart_fields = ["series", "x_min", "x_max"]
            missing_chart_fields = [
                field for field in required_chart_fields if field not in chart
            ]

            series = chart.get("series", [])
            x_min = chart.get("x_min", 0)
            x_max = chart.get("x_max", 0)

            # Verify series structure
            has_series = len(series) > 0
            has_xy_data = False
            xy_data_points = 0

            if has_series:
                first_series = series[0]
                if "xy" in first_series and isinstance(first_series["xy"], list):
                    xy_data = first_series["xy"]
                    xy_data_points = len(xy_data)
                    has_xy_data = xy_data_points >= 200  # Sufficient for PNG export

                    # Verify xy data format [[x, y], [x, y], ...]
                    valid_xy_format = all(
                        isinstance(point, list) and len(point) == 2
                        for point in xy_data[:5]  # Check first 5 points
                    )
                else:
                    valid_xy_format = False
            else:
                valid_xy_format = False

            # Verify x_min and x_max are reasonable
            x_range_valid = x_min > 0 and x_max > x_min and (x_max - x_min) > 50

            chart_ready_for_png = (
                not missing_chart_fields
                and has_series
                and has_xy_data
                and valid_xy_format
                and x_range_valid
            )

            if chart_ready_for_png:
                self.log_test(
                    "Chart Data PNG Export",
                    True,
                    f"Chart data ready for PNG export: {xy_data_points} points, range ${x_min:.2f}-${x_max:.2f}",
                    {
                        "series_count": len(series),
                        "xy_data_points": xy_data_points,
                        "x_min": x_min,
                        "x_max": x_max,
                        "valid_format": valid_xy_format,
                        "png_ready": True,
                    },
                )
            else:
                issues = []
                if missing_chart_fields:
                    issues.append(f"Missing chart fields: {missing_chart_fields}")
                if not has_series:
                    issues.append("No series data found")
                if not has_xy_data:
                    issues.append(f"Insufficient xy data points: {xy_data_points}")
                if not valid_xy_format:
                    issues.append("Invalid xy data format")
                if not x_range_valid:
                    issues.append(f"Invalid x range: {x_min} to {x_max}")

                self.log_test(
                    "Chart Data PNG Export",
                    False,
                    f"Chart data not ready for PNG export: {'; '.join(issues)}",
                    {"chart": chart, "issues": issues},
                )
        else:
            self.log_test(
                "Chart Data PNG Export",
                False,
                f"Failed to get chart data: {response['data']}",
            )

    async def test_meta_data_verification(self):
        """Test Meta Data - Verify meta section includes spot price and IV data"""
        print("\n📋 Testing Meta Data Verification...")

        # Test with Cash-Secured Put to verify meta data
        payload = {
            "symbol": "TSLA",
            "expiry": "2025-02-21",
            "dte": 30,
            "spot_override": 333.87,
            "iv_atm": 0.40,
            "legs": [
                {
                    "type": "PUT",
                    "strike": 300.0,
                    "side": "SELL",
                    "qty": 1,
                }
            ],
            "qty": 1,
        }

        response = self.make_request("POST", "/builder/price", data=payload)

        if response["success"]:
            data = response["data"]
            meta = data.get("meta", {})

            # Verify required meta fields for save payload
            required_meta_fields = [
                "symbol",
                "spot",
                "expiry",
                "dte",
                "iv_atm",
                "iv_eff",
                "rf",
            ]
            missing_meta_fields = [
                field for field in required_meta_fields if field not in meta
            ]

            # Verify meta data values
            symbol = meta.get("symbol", "")
            spot = meta.get("spot", 0)
            expiry = meta.get("expiry", "")
            dte = meta.get("dte", 0)
            iv_atm = meta.get("iv_atm", 0)
            iv_eff = meta.get("iv_eff", 0)
            rf = meta.get("rf", 0)

            # Validate meta data quality
            symbol_correct = symbol == "TSLA"
            spot_reasonable = 300.0 <= spot <= 400.0  # TSLA price range
            expiry_valid = "2025" in str(expiry)  # Should contain 2025
            dte_reasonable = 20 <= dte <= 40  # Around 30 days
            iv_atm_reasonable = 0.3 <= iv_atm <= 0.5  # 30-50% IV
            iv_eff_reasonable = 0.3 <= iv_eff <= 0.5  # Effective IV
            rf_reasonable = 0.03 <= rf <= 0.06  # Risk-free rate 3-6%

            meta_complete = not missing_meta_fields
            meta_valid = (
                symbol_correct
                and spot_reasonable
                and expiry_valid
                and dte_reasonable
                and iv_atm_reasonable
                and iv_eff_reasonable
                and rf_reasonable
            )

            if meta_complete and meta_valid:
                self.log_test(
                    "Meta Data Verification",
                    True,
                    f"Meta data complete and valid: {symbol} @ ${spot:.2f}, IV {iv_atm:.1%}/{iv_eff:.1%}, {dte}D, RF {rf:.1%}",
                    {
                        "symbol": symbol,
                        "spot": spot,
                        "expiry": expiry,
                        "dte": dte,
                        "iv_atm": iv_atm,
                        "iv_eff": iv_eff,
                        "rf": rf,
                        "complete": True,
                    },
                )
            else:
                issues = []
                if missing_meta_fields:
                    issues.append(f"Missing meta fields: {missing_meta_fields}")
                if not symbol_correct:
                    issues.append(f"Wrong symbol: {symbol}")
                if not spot_reasonable:
                    issues.append(f"Unreasonable spot: {spot}")
                if not expiry_valid:
                    issues.append(f"Invalid expiry: {expiry}")
                if not dte_reasonable:
                    issues.append(f"Unreasonable DTE: {dte}")
                if not iv_atm_reasonable:
                    issues.append(f"Unreasonable IV ATM: {iv_atm}")
                if not iv_eff_reasonable:
                    issues.append(f"Unreasonable IV effective: {iv_eff}")
                if not rf_reasonable:
                    issues.append(f"Unreasonable risk-free rate: {rf}")

                self.log_test(
                    "Meta Data Verification",
                    False,
                    f"Meta data validation failed: {'; '.join(issues)}",
                    {"meta": meta, "issues": issues},
                )
        else:
            self.log_test(
                "Meta Data Verification",
                False,
                f"Failed to get meta data: {response['data']}",
            )

    async def test_canonical_save_payload_structure(self):
        """Test Canonical Save Payload Structure - Verify response matches save requirements"""
        print("\n💾 Testing Canonical Save Payload Structure...")

        # Test with the exact Long Call TSLA $250 from review requirements
        payload = {
            "symbol": "TSLA",
            "expiry": "2025-02-21",
            "dte": 30,
            "spot_override": 333.87,
            "iv_atm": 0.40,
            "legs": [
                {
                    "type": "CALL",
                    "strike": 250.0,  # $250 strike as specified in review
                    "side": "BUY",
                    "qty": 1,
                }
            ],
            "qty": 1,
        }

        response = self.make_request("POST", "/builder/price", data=payload)

        if response["success"]:
            data = response["data"]

            # Verify canonical save payload structure
            canonical_sections = ["meta", "pricing", "greeks", "chart"]
            all_sections_present = all(
                section in data for section in canonical_sections
            )

            # Verify each section has required fields for save functionality
            meta_complete = all(
                field in data.get("meta", {})
                for field in ["symbol", "spot", "expiry", "dte", "iv_atm", "iv_eff"]
            )

            pricing_complete = all(
                field in data.get("pricing", {})
                for field in [
                    "net_debit",
                    "net_credit",
                    "max_loss",
                    "max_profit",
                    "chance_profit",
                    "breakevens",
                ]
            )

            greeks_complete = all(
                field in data.get("greeks", {})
                for field in ["delta", "gamma", "theta", "vega"]
            )

            chart_complete = (
                "series" in data.get("chart", {})
                and len(data.get("chart", {}).get("series", [])) > 0
                and "xy" in data.get("chart", {}).get("series", [{}])[0]
            )

            # Verify data types are JSON serializable (important for save)
            try:
                import json

                json_serializable = True
                json.dumps(data)  # Test serialization
            except (TypeError, ValueError):
                json_serializable = False

            canonical_structure_valid = (
                all_sections_present
                and meta_complete
                and pricing_complete
                and greeks_complete
                and chart_complete
                and json_serializable
            )

            if canonical_structure_valid:
                # Extract key metrics for verification
                meta = data.get("meta", {})
                pricing = data.get("pricing", {})
                greeks = data.get("greeks", {})
                chart = data.get("chart", {})

                self.log_test(
                    "Canonical Save Payload Structure",
                    True,
                    f"Save payload structure complete: Long Call TSLA $250 @ ${meta.get('spot', 0):.2f}, ${pricing.get('net_debit', 0):.2f} debit, {len(chart.get('series', [{}])[0].get('xy', []))} chart points",
                    {
                        "structure_complete": True,
                        "json_serializable": json_serializable,
                        "sections": canonical_sections,
                        "meta_fields": list(data.get("meta", {}).keys()),
                        "pricing_fields": list(data.get("pricing", {}).keys()),
                        "greeks_fields": list(data.get("greeks", {}).keys()),
                        "chart_points": len(chart.get("series", [{}])[0].get("xy", [])),
                    },
                )
            else:
                issues = []
                if not all_sections_present:
                    missing = [s for s in canonical_sections if s not in data]
                    issues.append(f"Missing sections: {missing}")
                if not meta_complete:
                    issues.append("Incomplete meta section")
                if not pricing_complete:
                    issues.append("Incomplete pricing section")
                if not greeks_complete:
                    issues.append("Incomplete greeks section")
                if not chart_complete:
                    issues.append("Incomplete chart section")
                if not json_serializable:
                    issues.append("Response not JSON serializable")

                self.log_test(
                    "Canonical Save Payload Structure",
                    False,
                    f"Save payload structure incomplete: {'; '.join(issues)}",
                    {"data_keys": list(data.keys()), "issues": issues},
                )
        else:
            self.log_test(
                "Canonical Save Payload Structure",
                False,
                f"Failed to get save payload structure: {response['data']}",
            )

    async def run_b4_verification_tests(self):
        """Run all B4/6 Builder Backend Verification tests"""
        print("🚀 Starting B4/6 Builder Backend Verification Testing")
        print("=" * 80)
        print("Quick verification that Builder backend continues to work properly")
        print("after frontend Save Trade implementation.")
        print("=" * 80)

        start_time = time.time()

        # Run all verification tests as specified in review
        await self.test_builder_price_endpoint_long_call_tsla_250()
        await self.test_greeks_data_verification()
        await self.test_chart_data_png_export()
        await self.test_meta_data_verification()
        await self.test_canonical_save_payload_structure()

        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        duration = time.time() - start_time

        # Print summary
        print("\n" + "=" * 80)
        print("🎯 B4/6 BUILDER BACKEND VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Duration: {duration:.2f}s")

        # Detailed results by verification area
        verification_areas = {
            "Builder Price Endpoint": [
                r for r in self.test_results if "Builder Price Endpoint" in r["test"]
            ],
            "Greeks Data": [r for r in self.test_results if "Greeks Data" in r["test"]],
            "Chart Data PNG Export": [
                r for r in self.test_results if "Chart Data PNG" in r["test"]
            ],
            "Meta Data": [r for r in self.test_results if "Meta Data" in r["test"]],
            "Save Payload Structure": [
                r for r in self.test_results if "Save Payload" in r["test"]
            ],
        }

        print("\n📋 VERIFICATION RESULTS BY AREA:")
        for area, results in verification_areas.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate >= 100 else "⚠️" if rate >= 75 else "❌"
                print(f"  {status} {area}: {passed}/{total} ({rate:.1f}%)")

        # Critical findings for B4/6 verification
        print("\n🔍 B4/6 VERIFICATION FINDINGS:")

        # Builder Price Endpoint
        price_tests = [
            r for r in self.test_results if "Builder Price Endpoint" in r["test"]
        ]
        if any(r["success"] for r in price_tests):
            print(
                "  ✅ POST /api/builder/price returns complete data structure for save payload"
            )
        else:
            print("  ❌ Builder price endpoint has issues with save payload structure")

        # Greeks Data
        greeks_tests = [r for r in self.test_results if "Greeks Data" in r["test"]]
        if any(r["success"] for r in greeks_tests):
            print("  ✅ All 4 Greeks (delta, gamma, theta, vega) included in response")
        else:
            print("  ❌ Greeks data incomplete or missing")

        # Chart Data
        chart_tests = [r for r in self.test_results if "Chart Data PNG" in r["test"]]
        if any(r["success"] for r in chart_tests):
            print("  ✅ Chart.series with xy data provided for PNG export")
        else:
            print("  ❌ Chart data insufficient for PNG export")

        # Meta Data
        meta_tests = [r for r in self.test_results if "Meta Data" in r["test"]]
        if any(r["success"] for r in meta_tests):
            print("  ✅ Meta section includes spot price and IV data")
        else:
            print("  ❌ Meta data incomplete or missing")

        # Save Payload Structure
        save_tests = [r for r in self.test_results if "Save Payload" in r["test"]]
        if any(r["success"] for r in save_tests):
            print("  ✅ Response structure matches canonical save payload requirements")
        else:
            print("  ❌ Save payload structure does not meet requirements")

        # Overall verdict
        print("\n🎯 OVERALL VERDICT:")
        if success_rate >= 100:
            print(
                "  🎉 EXCELLENT - B4/6 Builder backend fully supports Save Trade functionality"
            )
        elif success_rate >= 80:
            print(
                "  ✅ GOOD - B4/6 Builder backend mostly supports Save Trade functionality"
            )
        elif success_rate >= 60:
            print(
                "  ⚠️ PARTIAL - B4/6 Builder backend has some issues with Save Trade support"
            )
        else:
            print(
                "  ❌ CRITICAL - B4/6 Builder backend has significant issues with Save Trade support"
            )

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
    tester = B4BuilderVerificationTester()
    results = await tester.run_b4_verification_tests()

    # Return results for potential integration with other systems
    return results


if __name__ == "__main__":
    asyncio.run(main())
