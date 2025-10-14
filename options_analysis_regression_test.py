#!/usr/bin/env python3
"""
Options Selling Analysis Regression Test
Backend-only regression test of updated /api/options/selling/analysis endpoint
"""

import requests
import sys


class OptionsAnalysisRegressionTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   {details}")
        else:
            self.failures.append(f"{test_name}: {details}")
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, params=None, data=None):
        """Make HTTP request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)

            return response
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

    def test_analysis_default_params(self):
        """Test 1: Call GET /api/options/selling/analysis with default params"""
        print("\n🔍 TEST 1: Analysis with default parameters")
        print("-" * 50)

        response = self.make_request("GET", "options/selling/analysis")

        if not response:
            self.log_result("Analysis Default Request", False, "Request failed")
            return False

        if response.status_code != 200:
            self.log_result(
                "Analysis Default Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return False

        try:
            data = response.json()
        except:
            self.log_result(
                "Analysis Default JSON", False, "Response is not valid JSON"
            )
            return False

        # Check response structure
        if "status" not in data:
            self.log_result(
                "Analysis Default Structure", False, "Missing 'status' field"
            )
            return False

        if data["status"] != "success":
            self.log_result(
                "Analysis Default Status Field",
                False,
                f"Status is '{data['status']}', expected 'success'",
            )
            return False

        if "data" not in data:
            self.log_result(
                "Analysis Default Data Field", False, "Missing 'data' field"
            )
            return False

        analysis_data = data["data"]

        # Check for data.series
        if "series" not in analysis_data:
            self.log_result(
                "Analysis Default Series", False, "Missing 'series' field in data"
            )
            return False

        series = analysis_data["series"]
        if not isinstance(series, list):
            self.log_result(
                "Analysis Default Series Type", False, "Series is not an array"
            )
            return False

        self.log_result(
            "Analysis Default Request", True, f"Got {len(series)} series items"
        )

        # Check series structure if not empty
        if len(series) > 0:
            return self.validate_series_structure(series, "Default")
        else:
            self.log_result(
                "Analysis Default Series Content", True, "Series is empty (acceptable)"
            )
            return True

    def test_analysis_specific_params(self):
        """Test 2: Call with ticker=TSLA&strategies=SELL%20CALL,ROLL%20CC range=1M"""
        print("\n🔍 TEST 2: Analysis with specific parameters")
        print("-" * 50)

        params = {"ticker": "TSLA", "strategies": "SELL CALL,ROLL CC", "range": "1M"}

        response = self.make_request("GET", "options/selling/analysis", params=params)

        if not response:
            self.log_result("Analysis Specific Request", False, "Request failed")
            return False

        if response.status_code != 200:
            self.log_result(
                "Analysis Specific Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return False

        try:
            data = response.json()
        except:
            self.log_result(
                "Analysis Specific JSON", False, "Response is not valid JSON"
            )
            return False

        # Check response structure
        if "status" not in data or data["status"] != "success":
            self.log_result(
                "Analysis Specific Status Field",
                False,
                f"Status is '{data.get('status')}', expected 'success'",
            )
            return False

        if "data" not in data:
            self.log_result(
                "Analysis Specific Data Field", False, "Missing 'data' field"
            )
            return False

        analysis_data = data["data"]

        # Check for data.series
        if "series" not in analysis_data:
            self.log_result(
                "Analysis Specific Series", False, "Missing 'series' field in data"
            )
            return False

        series = analysis_data["series"]
        if not isinstance(series, list):
            self.log_result(
                "Analysis Specific Series Type", False, "Series is not an array"
            )
            return False

        self.log_result(
            "Analysis Specific Request",
            True,
            f"Got {len(series)} series items for TSLA",
        )

        # Check series structure if not empty
        if len(series) > 0:
            return self.validate_series_structure(series, "Specific")
        else:
            self.log_result(
                "Analysis Specific Series Content", True, "Series is empty (acceptable)"
            )
            return True

    def validate_series_structure(self, series, test_type):
        """Validate series structure and xIndex field"""
        print(f"   📊 Validating {len(series)} series items...")

        # Check each series item has required fields
        required_fields = ["ts", "xIndex", "cum_closed_pl"]

        for i, item in enumerate(series):
            if not isinstance(item, dict):
                self.log_result(
                    f"Analysis {test_type} Series Item Type",
                    False,
                    f"Item {i} is not a dict",
                )
                return False

            # Check required fields
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                self.log_result(
                    f"Analysis {test_type} Series Fields",
                    False,
                    f"Item {i} missing fields: {missing_fields}",
                )
                return False

            # Check field types
            ts = item["ts"]
            x_index = item["xIndex"]
            cum_closed_pl = item["cum_closed_pl"]

            if not isinstance(ts, str):
                self.log_result(
                    f"Analysis {test_type} Series TS Type",
                    False,
                    f"Item {i} 'ts' is not string: {type(ts)}",
                )
                return False

            if not isinstance(x_index, (int, float)):
                self.log_result(
                    f"Analysis {test_type} Series xIndex Type",
                    False,
                    f"Item {i} 'xIndex' is not number: {type(x_index)}",
                )
                return False

            if not isinstance(cum_closed_pl, (int, float)):
                self.log_result(
                    f"Analysis {test_type} Series P&L Type",
                    False,
                    f"Item {i} 'cum_closed_pl' is not number: {type(cum_closed_pl)}",
                )
                return False

        self.log_result(
            f"Analysis {test_type} Series Fields",
            True,
            "All items have required fields with correct types",
        )

        # Check xIndex values are increasing integers
        x_indices = [item["xIndex"] for item in series]

        # Check if they are integers (or can be converted to integers)
        try:
            int_indices = [int(x) for x in x_indices]
        except:
            self.log_result(
                f"Analysis {test_type} xIndex Integers",
                False,
                "xIndex values cannot be converted to integers",
            )
            return False

        # Check if they are increasing
        is_increasing = all(
            int_indices[i] <= int_indices[i + 1] for i in range(len(int_indices) - 1)
        )

        if not is_increasing:
            self.log_result(
                f"Analysis {test_type} xIndex Increasing",
                False,
                f"xIndex values not increasing: {int_indices[:5]}...",
            )
            return False

        self.log_result(
            f"Analysis {test_type} xIndex Increasing",
            True,
            f"xIndex values are increasing integers: {int_indices[0]} to {int_indices[-1]}",
        )

        # Show sample data
        print("   📋 Sample series data:")
        for i, item in enumerate(series[:3]):
            print(
                f"     [{i}] ts: {item['ts']}, xIndex: {item['xIndex']}, cum_closed_pl: {item['cum_closed_pl']}"
            )
        if len(series) > 3:
            print(f"     ... and {len(series) - 3} more items")

        return True

    def test_compute_monitor_endpoints(self):
        """Test 3: Ensure no 500 errors on compute/monitor endpoints after this change"""
        print("\n🔍 TEST 3: Verify compute/monitor endpoints still work")
        print("-" * 50)

        # Test compute endpoint
        compute_data = {
            "positions": [
                {
                    "ticker": "AAPL",
                    "shares": 100,
                    "avg_cost": 150.0,
                    "price": 150.0,
                    "strike": 145.0,
                    "delta": 0.25,
                    "dte": 30,
                    "premium": 2.5,
                    "iv_rank": 50.0,
                    "vix": 20.0,
                }
            ],
            "config": {"capital_base": 50000, "mode": "equal"},
        }

        response = self.make_request(
            "POST", "options/selling/compute", data=compute_data
        )

        if not response:
            self.log_result("Compute Endpoint Request", False, "Request failed")
            return False

        if response.status_code == 500:
            self.log_result(
                "Compute Endpoint 500 Error", False, "Got 500 Internal Server Error"
            )
            return False

        if response.status_code != 200:
            self.log_result(
                "Compute Endpoint Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return False

        self.log_result("Compute Endpoint", True, "No 500 error, endpoint working")

        # Test monitor status endpoint
        response = self.make_request("GET", "options/selling/monitor/status")

        if not response:
            self.log_result("Monitor Status Request", False, "Request failed")
            return False

        if response.status_code == 500:
            self.log_result(
                "Monitor Status 500 Error", False, "Got 500 Internal Server Error"
            )
            return False

        if response.status_code != 200:
            self.log_result(
                "Monitor Status", False, f"Expected 200, got {response.status_code}"
            )
            return False

        self.log_result(
            "Monitor Status Endpoint", True, "No 500 error, endpoint working"
        )

        return True

    def run_all_tests(self):
        """Run all regression tests"""
        print("🎯 OPTIONS SELLING ANALYSIS REGRESSION TEST")
        print("=" * 60)
        print("📋 Testing updated /api/options/selling/analysis endpoint")
        print(
            "🔍 Verifying response includes data.series with xIndex field integers increasing"
        )
        print("✅ Ensuring original fields are preserved")
        print()

        # Run tests
        test1_passed = self.test_analysis_default_params()
        test2_passed = self.test_analysis_specific_params()
        test3_passed = self.test_compute_monitor_endpoints()

        # Summary
        print("\n" + "=" * 60)
        print("📊 REGRESSION TEST SUMMARY")
        print("-" * 30)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

        if self.failures:
            print("\n❌ FAILURES:")
            for failure in self.failures:
                print(f"   - {failure}")

        print("\n🎯 REGRESSION TEST RESULTS:")
        print(f"   ✅ Default params test: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"   ✅ Specific params test: {'PASSED' if test2_passed else 'FAILED'}")
        print(f"   ✅ No 500 errors test: {'PASSED' if test3_passed else 'FAILED'}")

        all_passed = test1_passed and test2_passed and test3_passed

        if all_passed:
            print("\n🎉 VERDICT: ALL REGRESSION TESTS PASSED")
            print("   ✅ /api/options/selling/analysis endpoint working correctly")
            print("   ✅ data.series includes xIndex field with increasing integers")
            print("   ✅ Original fields preserved (ts, cum_closed_pl)")
            print("   ✅ No 500 errors on compute/monitor endpoints")
        else:
            print("\n🚨 VERDICT: REGRESSION TESTS FAILED")
            print("   ❌ Issues detected with /api/options/selling/analysis endpoint")

        return all_passed


if __name__ == "__main__":
    tester = OptionsAnalysisRegressionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
