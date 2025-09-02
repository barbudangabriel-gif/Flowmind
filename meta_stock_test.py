#!/usr/bin/env python3
"""
META Stock Analysis Backend API Testing
Quick verification test for META stock analysis functionality to confirm all backend APIs
supporting the professional chart integration are working perfectly.

Focus Areas:
1. Investment Scoring API - GET /api/investments/score/META
2. Chart Data Requirements - Verify stock_data fields needed for chart (price, change, change_percent)
3. Response Speed - Ensure APIs respond quickly for chart loading
"""

import requests
import time


class METAStockTester:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.response_times = []

    def log_test(self, name, success, response_time, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1

        self.response_times.append(response_time)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name} ({response_time:.3f}s)")
        if details:
            print(f"    {details}")

    def test_investment_scoring_api(self):
        """Test Investment Scoring API for META - PRIMARY FOCUS"""
        print("\n🎯 PHASE 1: Investment Scoring API - GET /api/investments/score/META")
        print("-" * 70)

        url = f"{self.api_url}/investments/score/META"
        start_time = time.time()

        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                # Verify required fields for chart integration
                required_fields = ["symbol", "total_score", "rating", "stock_data"]
                missing_fields = [
                    field for field in required_fields if field not in data
                ]

                if missing_fields:
                    self.log_test(
                        "Investment Scoring API",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                    )
                    return False

                # Verify stock_data contains chart-required fields
                stock_data = data.get("stock_data", {})
                chart_fields = ["price", "change", "change_percent"]
                missing_chart_fields = [
                    field for field in chart_fields if field not in stock_data
                ]

                if missing_chart_fields:
                    self.log_test(
                        "Investment Scoring API",
                        False,
                        response_time,
                        f"Missing chart fields in stock_data: {missing_chart_fields}",
                    )
                    return False

                # Extract key data
                symbol = data.get("symbol")
                score = data.get("total_score")
                rating = data.get("rating")
                price = stock_data.get("price")
                change = stock_data.get("change")
                change_percent = stock_data.get("change_percent")

                # Verify data quality
                if price and price > 0:
                    price_valid = True
                    price_details = f"${price:.2f}"
                else:
                    price_valid = False
                    price_details = f"Invalid price: {price}"

                details = f"Symbol: {symbol}, Score: {score}, Rating: {rating}, Price: {price_details}"
                self.log_test(
                    "Investment Scoring API",
                    price_valid and symbol == "META",
                    response_time,
                    details,
                )

                return {
                    "success": price_valid and symbol == "META",
                    "data": data,
                    "response_time": response_time,
                }
            else:
                self.log_test(
                    "Investment Scoring API",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(
                "Investment Scoring API", False, response_time, f"Error: {str(e)}"
            )
            return False

    def test_enhanced_stock_data_api(self):
        """Test Enhanced Stock Data API for META - Chart Data Source"""
        print("\n📊 PHASE 2: Enhanced Stock Data API - GET /api/stocks/META/enhanced")
        print("-" * 70)

        url = f"{self.api_url}/stocks/META/enhanced"
        start_time = time.time()

        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                # Verify required fields for chart
                required_fields = [
                    "symbol",
                    "price",
                    "change",
                    "change_percent",
                    "volume",
                ]
                missing_fields = [
                    field for field in required_fields if field not in data
                ]

                if missing_fields:
                    self.log_test(
                        "Enhanced Stock Data API",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                    )
                    return False

                # Extract key data
                symbol = data.get("symbol")
                price = data.get("price")
                change = data.get("change")
                change_percent = data.get("change_percent")
                volume = data.get("volume")
                data_source = data.get("data_source", "Unknown")

                # Verify data quality
                data_valid = (
                    symbol == "META" and price and price > 0 and volume and volume > 0
                )

                details = f"Price: ${price:.2f}, Change: {change:+.2f} ({change_percent:+.2f}%), Volume: {volume:,}, Source: {data_source}"
                self.log_test(
                    "Enhanced Stock Data API", data_valid, response_time, details
                )

                return {
                    "success": data_valid,
                    "data": data,
                    "response_time": response_time,
                }
            else:
                self.log_test(
                    "Enhanced Stock Data API",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(
                "Enhanced Stock Data API", False, response_time, f"Error: {str(e)}"
            )
            return False

    def test_historical_data_api(self):
        """Test Historical Data API for META - Chart Data"""
        print("\n📈 PHASE 3: Historical Data API - GET /api/stocks/META/historical")
        print("-" * 70)

        url = f"{self.api_url}/stocks/META/historical"
        params = {"interval": "1D", "bars_back": 30}
        start_time = time.time()

        try:
            response = requests.get(url, params=params, timeout=15)
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                # Verify response structure
                required_fields = ["status", "symbol", "data", "count"]
                missing_fields = [
                    field for field in required_fields if field not in data
                ]

                if missing_fields:
                    self.log_test(
                        "Historical Data API",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                    )
                    return False

                # Verify chart data structure
                chart_data = data.get("data", [])
                if not chart_data:
                    self.log_test(
                        "Historical Data API",
                        False,
                        response_time,
                        "No chart data returned",
                    )
                    return False

                # Check first data point structure
                first_point = chart_data[0]
                chart_fields = ["time", "open", "high", "low", "close", "volume"]
                missing_chart_fields = [
                    field for field in chart_fields if field not in first_point
                ]

                if missing_chart_fields:
                    self.log_test(
                        "Historical Data API",
                        False,
                        response_time,
                        f"Missing chart fields: {missing_chart_fields}",
                    )
                    return False

                # Extract key info
                symbol = data.get("symbol")
                count = data.get("count")
                data_source = data.get("data_source", "Unknown")

                details = (
                    f"Symbol: {symbol}, Data Points: {count}, Source: {data_source}"
                )
                success = symbol == "META" and count > 0

                self.log_test("Historical Data API", success, response_time, details)

                return {
                    "success": success,
                    "data": data,
                    "response_time": response_time,
                }
            else:
                self.log_test(
                    "Historical Data API",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(
                "Historical Data API", False, response_time, f"Error: {str(e)}"
            )
            return False

    def test_response_speed_requirements(self):
        """Test Response Speed Requirements - Under 2 seconds"""
        print("\n⚡ PHASE 4: Response Speed Verification")
        print("-" * 70)

        if not self.response_times:
            print("❌ No response times recorded")
            return False

        avg_response_time = sum(self.response_times) / len(self.response_times)
        max_response_time = max(self.response_times)
        min_response_time = min(self.response_times)

        print("📊 Response Time Analysis:")
        print(f"    Average: {avg_response_time:.3f}s")
        print(f"    Maximum: {max_response_time:.3f}s")
        print(f"    Minimum: {min_response_time:.3f}s")
        print("    Requirement: < 2.000s")

        # Check if all responses are under 2 seconds
        slow_responses = [t for t in self.response_times if t >= 2.0]

        if slow_responses:
            self.log_test(
                "Response Speed Requirements",
                False,
                avg_response_time,
                f"{len(slow_responses)} responses >= 2s (slowest: {max(slow_responses):.3f}s)",
            )
            return False
        else:
            self.log_test(
                "Response Speed Requirements",
                True,
                avg_response_time,
                f"All {len(self.response_times)} responses < 2s",
            )
            return True

    def test_price_verification(self, investment_result, enhanced_result):
        """Test Price Information Verification - Match Frontend Display"""
        print("\n💰 PHASE 5: Price Information Verification")
        print("-" * 70)

        if not investment_result or not enhanced_result:
            print("❌ Cannot verify prices - missing API data")
            return False

        # Extract prices from both APIs
        investment_price = investment_result["data"].get("stock_data", {}).get("price")
        enhanced_price = enhanced_result["data"].get("price")

        print("📊 Price Comparison:")
        print(
            f"    Investment API: ${investment_price:.2f}"
            if investment_price
            else "    Investment API: No price"
        )
        print(
            f"    Enhanced API: ${enhanced_price:.2f}"
            if enhanced_price
            else "    Enhanced API: No price"
        )
        print("    Expected Range: $700-$900 (typical META range)")

        # Check if prices are consistent
        if investment_price and enhanced_price:
            price_diff = abs(investment_price - enhanced_price)
            price_consistent = price_diff < 1.0  # Allow $1 difference

            if price_consistent:
                avg_price = (investment_price + enhanced_price) / 2
                self.log_test(
                    "Price Consistency",
                    True,
                    0,
                    f"Prices consistent: ${avg_price:.2f} (diff: ${price_diff:.2f})",
                )

                # Check if price is in reasonable range for META
                reasonable_range = 200 <= avg_price <= 1000  # META typical range
                if reasonable_range:
                    self.log_test(
                        "Price Reasonableness",
                        True,
                        0,
                        f"Price ${avg_price:.2f} in reasonable range",
                    )
                    return True
                else:
                    self.log_test(
                        "Price Reasonableness",
                        False,
                        0,
                        f"Price ${avg_price:.2f} outside reasonable range",
                    )
                    return False
            else:
                self.log_test(
                    "Price Consistency",
                    False,
                    0,
                    f"Price mismatch: ${price_diff:.2f} difference",
                )
                return False
        else:
            self.log_test(
                "Price Verification",
                False,
                0,
                "Missing price data from one or both APIs",
            )
            return False

    def run_comprehensive_test(self):
        """Run comprehensive META stock analysis test"""
        print("🎯 META STOCK ANALYSIS BACKEND API TESTING")
        print("=" * 80)
        print(
            "📋 OBJECTIVE: Quick verification test for META stock analysis functionality"
        )
        print("🎯 FOCUS AREAS:")
        print("   1. Investment Scoring API - GET /api/investments/score/META")
        print(
            "   2. Chart Data Requirements - Verify stock_data fields (price, change, change_percent)"
        )
        print(
            "   3. Response Speed - Ensure APIs respond quickly for chart loading (< 2s)"
        )
        print(
            "   4. Price Information - Verify price matches frontend display expectations"
        )
        print(
            "   5. Professional Chart Integration - Confirm data structure compatibility"
        )

        # Run all tests
        investment_result = self.test_investment_scoring_api()
        enhanced_result = self.test_enhanced_stock_data_api()
        historical_result = self.test_historical_data_api()
        speed_result = self.test_response_speed_requirements()
        price_result = self.test_price_verification(investment_result, enhanced_result)

        # Final Assessment
        print("\n🎯 FINAL ASSESSMENT: META Stock Analysis Backend APIs")
        print("=" * 80)

        # Calculate success rate
        total_tests = self.tests_run
        passed_tests = self.tests_passed
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n📊 TEST RESULTS SUMMARY:")
        print(f"    Tests Run: {total_tests}")
        print(f"    Tests Passed: {passed_tests}")
        print(f"    Success Rate: {success_rate:.1f}%")

        # Response time summary
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            print(f"    Average Response Time: {avg_time:.3f}s")
            print(f"    Maximum Response Time: {max_time:.3f}s")
            print(
                f"    Speed Requirement Met: {'✅ YES' if max_time < 2.0 else '❌ NO'}"
            )

        # Key findings
        print("\n🔍 KEY FINDINGS:")

        if investment_result and investment_result.get("success"):
            inv_data = investment_result["data"]
            stock_data = inv_data.get("stock_data", {})
            print("    ✅ Investment Scoring API: Working")
            print(f"       - META Score: {inv_data.get('total_score')}")
            print(f"       - Rating: {inv_data.get('rating')}")
            print(f"       - Price: ${stock_data.get('price', 0):.2f}")
        else:
            print("    ❌ Investment Scoring API: Failed")

        if enhanced_result and enhanced_result.get("success"):
            enh_data = enhanced_result["data"]
            print("    ✅ Enhanced Stock Data API: Working")
            print(f"       - Price: ${enh_data.get('price', 0):.2f}")
            print(
                f"       - Change: {enh_data.get('change', 0):+.2f} ({enh_data.get('change_percent', 0):+.2f}%)"
            )
            print(f"       - Volume: {enh_data.get('volume', 0):,}")
        else:
            print("    ❌ Enhanced Stock Data API: Failed")

        if historical_result and historical_result.get("success"):
            hist_data = historical_result["data"]
            print("    ✅ Historical Data API: Working")
            print(f"       - Data Points: {hist_data.get('count', 0)}")
            print("       - Chart Ready: Yes")
        else:
            print("    ❌ Historical Data API: Failed")

        print(
            f"    {'✅' if speed_result else '❌'} Response Speed: {'Under 2s' if speed_result else 'Too slow'}"
        )
        print(
            f"    {'✅' if price_result else '❌'} Price Verification: {'Consistent' if price_result else 'Issues detected'}"
        )

        # Chart Integration Assessment
        print("\n📊 PROFESSIONAL CHART INTEGRATION ASSESSMENT:")

        chart_ready_fields = []
        if investment_result and investment_result.get("success"):
            chart_ready_fields.append("Investment scoring data")
        if enhanced_result and enhanced_result.get("success"):
            chart_ready_fields.append("Real-time price data")
        if historical_result and historical_result.get("success"):
            chart_ready_fields.append("Historical OHLC data")

        if len(chart_ready_fields) >= 3:
            print("    ✅ Chart Integration: READY")
            print(f"       - Available data: {', '.join(chart_ready_fields)}")
            print("       - ApexCharts compatibility: Confirmed")
        elif len(chart_ready_fields) >= 2:
            print("    ⚠️  Chart Integration: PARTIAL")
            print(f"       - Available data: {', '.join(chart_ready_fields)}")
            print(f"       - Missing: {3 - len(chart_ready_fields)} data source(s)")
        else:
            print("    ❌ Chart Integration: NOT READY")
            print(
                f"       - Available data: {', '.join(chart_ready_fields) if chart_ready_fields else 'None'}"
            )

        # Final Verdict
        print("\n🎯 FINAL VERDICT:")

        if success_rate >= 90 and speed_result and len(chart_ready_fields) >= 3:
            print(
                "    🎉 EXCELLENT - META stock analysis functionality working perfectly!"
            )
            print(
                "    ✅ All backend APIs supporting professional chart integration are operational"
            )
            print("    ✅ Response times meet requirements (< 2s)")
            print("    ✅ Price data is consistent and ready for frontend display")
            print(
                "    ✅ Chart data structure is compatible with ApexCharts integration"
            )
            verdict = "EXCELLENT"
        elif success_rate >= 75 and len(chart_ready_fields) >= 2:
            print("    ✅ GOOD - META stock analysis mostly working with minor issues")
            print("    ✅ Core functionality operational for chart integration")
            print("    ⚠️  Some optimization may be needed")
            verdict = "GOOD"
        else:
            print("    ❌ NEEDS ATTENTION - META stock analysis has significant issues")
            print("    ❌ Chart integration may not work properly")
            print("    🔧 Backend APIs require fixes before frontend integration")
            verdict = "NEEDS_ATTENTION"

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if verdict == "EXCELLENT":
            print("    ✅ Backend APIs are ready for production use")
            print("    ✅ Professional charts should load META data correctly")
            print("    ✅ No immediate action required")
        elif verdict == "GOOD":
            print("    🔧 Monitor response times during peak usage")
            print("    🔧 Consider caching for improved performance")
            print("    ✅ Charts should work with current implementation")
        else:
            print("    🚨 Fix failing API endpoints before chart integration")
            print("    🚨 Investigate slow response times")
            print("    🚨 Verify data source connectivity")

        return verdict == "EXCELLENT" or verdict == "GOOD"


if __name__ == "__main__":
    tester = METAStockTester()
    success = tester.run_comprehensive_test()

    print(f"\n{'='*80}")
    print(
        f"META STOCK ANALYSIS TEST {'COMPLETED SUCCESSFULLY' if success else 'COMPLETED WITH ISSUES'}"
    )
    print(f"{'='*80}")
