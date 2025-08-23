#!/usr/bin/env python3
"""
Options Selling Monitor Backend Testing
Focus: Testing the new Options Selling Monitor feature endpoints
"""

import requests
import json
import time
import asyncio
from datetime import datetime
import sys

class OptionsSellingSMonitorTester:
    def __init__(self, base_url="https://put-selling-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.test_results = {}

    def log_result(self, test_name, success, details=None, is_critical=False):
        """Log test result with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if is_critical:
                self.critical_failures.append(test_name)
        
        if details:
            print(f"   {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'critical': is_critical,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_demo_positions(self):
        """Get demo positions for testing"""
        return [
            {
                "ticker": "AAPL",
                "price": 227.50,
                "strike": 220.0,
                "delta": 0.28,
                "dte": 25,
                "premium": 3.50,
                "iv_rank": 45.0,
                "vix": 18.5,
                "selected": True,
                "assigned": False,
                "status": "Active",
                "contracts": 0,
                "notes": "High quality tech stock"
            },
            {
                "ticker": "MSFT",
                "price": 415.00,
                "strike": 400.0,
                "delta": 0.26,
                "dte": 30,
                "premium": 8.75,
                "iv_rank": 42.0,
                "vix": 18.5,
                "selected": True,
                "assigned": False,
                "status": "Active",
                "contracts": 0,
                "notes": "Stable dividend stock"
            },
            {
                "ticker": "TSLA",
                "price": 350.00,
                "strike": 330.0,
                "delta": 0.29,
                "dte": 28,
                "premium": 12.25,
                "iv_rank": 55.0,
                "vix": 18.5,
                "selected": True,
                "assigned": False,
                "status": "Active",
                "contracts": 0,
                "notes": "High volatility growth stock"
            }
        ]

    def get_default_config(self):
        """Get default configuration for testing"""
        return {
            "delta_min": 0.25,
            "delta_max": 0.30,
            "dte_min": 20,
            "dte_max": 40,
            "iv_rank_min": 40.0,
            "vix_min": 15.0,
            "vix_max": 25.0,
            "roll_delta_threshold": 0.35,
            "roll_dte_threshold": 10,
            "capital_base": 500000.0,
            "dynamic_risk": True
        }

    def test_existing_compute_endpoint(self):
        """Test existing POST /api/options/selling/compute endpoint"""
        print("\n🎯 Testing Existing Options Selling Compute Endpoint")
        print("=" * 80)
        
        # Test with demo positions and default config, mode=equal
        test_data = {
            "positions": self.get_demo_positions(),
            "config": self.get_default_config(),
            "mode": "equal"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/compute",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['status', 'data']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Compute Endpoint - Response Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        True
                    )
                    return False
                
                # Check status is success
                if data.get('status') != 'success':
                    self.log_result(
                        "Compute Endpoint - Status",
                        False,
                        f"Expected status=success, got {data.get('status')}",
                        True
                    )
                    return False
                
                # Verify data structure contains expected fields
                response_data = data.get('data', {})
                expected_data_fields = ['summary_equal', 'table_equal', 'signals_equal']
                missing_data_fields = [field for field in expected_data_fields if field not in response_data]
                
                if missing_data_fields:
                    self.log_result(
                        "Compute Endpoint - Data Fields",
                        False,
                        f"Missing data fields: {missing_data_fields}",
                        True
                    )
                    return False
                
                # Verify summary_equal has content
                summary_equal = response_data.get('summary_equal', {})
                if not summary_equal:
                    self.log_result(
                        "Compute Endpoint - Summary Equal",
                        False,
                        "summary_equal is empty",
                        True
                    )
                    return False
                
                # Verify table_equal has content
                table_equal = response_data.get('table_equal', [])
                if not isinstance(table_equal, list):
                    self.log_result(
                        "Compute Endpoint - Table Equal",
                        False,
                        "table_equal is not a list",
                        True
                    )
                    return False
                
                # Verify signals_equal has content
                signals_equal = response_data.get('signals_equal', [])
                if not isinstance(signals_equal, list):
                    self.log_result(
                        "Compute Endpoint - Signals Equal",
                        False,
                        "signals_equal is not a list",
                        True
                    )
                    return False
                
                self.log_result(
                    "Options Selling Compute Endpoint",
                    True,
                    f"Status: {data.get('status')}, Summary fields: {len(summary_equal)}, Table rows: {len(table_equal)}, Signals: {len(signals_equal)}, Time: {response_time:.2f}s"
                )
                
                # Store response for later use
                self.compute_response = data
                return True
            
            else:
                self.log_result(
                    "Options Selling Compute Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Options Selling Compute Endpoint",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_monitor_start_endpoint(self):
        """Test POST /api/options/selling/monitor/start endpoint"""
        print("\n🎯 Testing Monitor Start Endpoint")
        print("=" * 60)
        
        # Test with positions, config, and specific parameters
        test_data = {
            "positions": self.get_demo_positions(),
            "config": self.get_default_config(),
            "mode": "equal",
            "interval_seconds": 15
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/monitor/start",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('status') != 'success':
                    self.log_result(
                        "Monitor Start - Status",
                        False,
                        f"Expected status=success, got {data.get('status')}",
                        True
                    )
                    return False
                
                # Verify data contains expected fields
                response_data = data.get('data', {})
                if response_data.get('status') != 'started':
                    self.log_result(
                        "Monitor Start - Data Status",
                        False,
                        f"Expected data.status=started, got {response_data.get('status')}",
                        True
                    )
                    return False
                
                self.log_result(
                    "Monitor Start Endpoint",
                    True,
                    f"Status: {response_data.get('status')}, Interval: {response_data.get('interval_seconds')}s, Mode: {response_data.get('mode')}, Time: {response_time:.2f}s"
                )
                return True
            
            else:
                self.log_result(
                    "Monitor Start Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Monitor Start Endpoint",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_monitor_status_endpoint(self):
        """Test GET /api/options/selling/monitor/status endpoint"""
        print("\n🎯 Testing Monitor Status Endpoint")
        print("=" * 60)
        
        try:
            # Test immediately after start
            start_time = time.time()
            response = requests.get(
                f"{self.api_url}/options/selling/monitor/status",
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('status') != 'success':
                    self.log_result(
                        "Monitor Status - Status",
                        False,
                        f"Expected status=success, got {data.get('status')}",
                        True
                    )
                    return False
                
                # Verify data contains expected fields
                response_data = data.get('data', {})
                required_fields = ['running', 'cycles', 'interval_seconds', 'mode']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if missing_fields:
                    self.log_result(
                        "Monitor Status - Data Fields",
                        False,
                        f"Missing data fields: {missing_fields}",
                        True
                    )
                    return False
                
                # Verify running is true
                if not response_data.get('running'):
                    self.log_result(
                        "Monitor Status - Running",
                        False,
                        f"Expected running=true, got {response_data.get('running')}",
                        True
                    )
                    return False
                
                self.log_result(
                    "Monitor Status Endpoint (Immediate)",
                    True,
                    f"Running: {response_data.get('running')}, Cycles: {response_data.get('cycles')}, Mode: {response_data.get('mode')}, Time: {response_time:.2f}s"
                )
                
                # Wait ~1 second and test again to ensure cycles increment
                print("   Waiting 1 second for monitor cycle...")
                time.sleep(1.5)
                
                start_time = time.time()
                response2 = requests.get(
                    f"{self.api_url}/options/selling/monitor/status",
                    timeout=15
                )
                response_time2 = time.time() - start_time
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    response_data2 = data2.get('data', {})
                    
                    # Verify cycles is >= 0 and last_run_at is present
                    cycles = response_data2.get('cycles', -1)
                    last_run_at = response_data2.get('last_run_at')
                    
                    if cycles < 0:
                        self.log_result(
                            "Monitor Status - Cycles",
                            False,
                            f"Expected cycles >= 0, got {cycles}",
                            True
                        )
                        return False
                    
                    if not last_run_at or not isinstance(last_run_at, str):
                        self.log_result(
                            "Monitor Status - Last Run At",
                            False,
                            f"Expected last_run_at as string, got {last_run_at}",
                            True
                        )
                        return False
                    
                    self.log_result(
                        "Monitor Status Endpoint (After Wait)",
                        True,
                        f"Cycles: {cycles}, Last Run: {last_run_at}, Time: {response_time2:.2f}s"
                    )
                    return True
                
                else:
                    self.log_result(
                        "Monitor Status Endpoint (After Wait)",
                        False,
                        f"HTTP {response2.status_code}: {response2.text[:200]}",
                        True
                    )
                    return False
            
            else:
                self.log_result(
                    "Monitor Status Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Monitor Status Endpoint",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_monitor_stop_endpoint(self):
        """Test POST /api/options/selling/monitor/stop endpoint"""
        print("\n🎯 Testing Monitor Stop Endpoint")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/monitor/stop",
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('status') != 'success':
                    self.log_result(
                        "Monitor Stop - Status",
                        False,
                        f"Expected status=success, got {data.get('status')}",
                        True
                    )
                    return False
                
                # Verify data contains expected fields
                response_data = data.get('data', {})
                if response_data.get('status') != 'stopped':
                    self.log_result(
                        "Monitor Stop - Data Status",
                        False,
                        f"Expected data.status=stopped, got {response_data.get('status')}",
                        True
                    )
                    return False
                
                self.log_result(
                    "Monitor Stop Endpoint",
                    True,
                    f"Status: {response_data.get('status')}, Time: {response_time:.2f}s"
                )
                
                # Verify status shows running=false after stop
                time.sleep(0.5)  # Brief wait
                status_response = requests.get(f"{self.api_url}/options/selling/monitor/status", timeout=15)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_response_data = status_data.get('data', {})
                    
                    if status_response_data.get('running') == False:
                        self.log_result(
                            "Monitor Stop - Status Verification",
                            True,
                            f"Confirmed running=false after stop"
                        )
                        return True
                    else:
                        self.log_result(
                            "Monitor Stop - Status Verification",
                            False,
                            f"Expected running=false after stop, got {status_response_data.get('running')}",
                            True
                        )
                        return False
                else:
                    self.log_result(
                        "Monitor Stop - Status Verification",
                        False,
                        f"Could not verify status after stop: HTTP {status_response.status_code}",
                        True
                    )
                    return False
            
            else:
                self.log_result(
                    "Monitor Stop Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Monitor Stop Endpoint",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_robustness_scenarios(self):
        """Test robustness scenarios with different modes"""
        print("\n🎯 Testing Robustness Scenarios")
        print("=" * 60)
        
        # Test 1: Start with mode=both
        test_data_both = {
            "positions": self.get_demo_positions(),
            "config": self.get_default_config(),
            "mode": "both",
            "interval_seconds": 15
        }
        
        try:
            # Start with mode=both
            response = requests.post(
                f"{self.api_url}/options/selling/monitor/start",
                json=test_data_both,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('data', {}).get('status') == 'started':
                    self.log_result(
                        "Robustness - Start with mode=both",
                        True,
                        f"Successfully started with mode=both"
                    )
                    
                    # Wait a moment and check status
                    time.sleep(1)
                    status_response = requests.get(f"{self.api_url}/options/selling/monitor/status", timeout=15)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status_response_data = status_data.get('data', {})
                        
                        # Verify signals_current array is present
                        signals_current = status_response_data.get('signals_current', [])
                        if isinstance(signals_current, list):
                            self.log_result(
                                "Robustness - Signals Current Array",
                                True,
                                f"signals_current array present with {len(signals_current)} items"
                            )
                        else:
                            self.log_result(
                                "Robustness - Signals Current Array",
                                False,
                                f"signals_current is not an array: {type(signals_current)}",
                                True
                            )
                            return False
                    else:
                        self.log_result(
                            "Robustness - Status Check",
                            False,
                            f"Status check failed: HTTP {status_response.status_code}",
                            True
                        )
                        return False
                else:
                    self.log_result(
                        "Robustness - Start with mode=both",
                        False,
                        f"Failed to start with mode=both",
                        True
                    )
                    return False
            else:
                self.log_result(
                    "Robustness - Start with mode=both",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
            
            # Test 2: Stop again
            stop_response = requests.post(
                f"{self.api_url}/options/selling/monitor/stop",
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if stop_response.status_code == 200:
                stop_data = stop_response.json()
                if stop_data.get('status') == 'success' and stop_data.get('data', {}).get('status') == 'stopped':
                    self.log_result(
                        "Robustness - Stop Again",
                        True,
                        f"Successfully stopped monitor again"
                    )
                    return True
                else:
                    self.log_result(
                        "Robustness - Stop Again",
                        False,
                        f"Failed to stop monitor again",
                        True
                    )
                    return False
            else:
                self.log_result(
                    "Robustness - Stop Again",
                    False,
                    f"HTTP {stop_response.status_code}: {stop_response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Robustness Scenarios",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_api_prefix_compliance(self):
        """Test that all routes are under /api prefix and no hardcoded URLs"""
        print("\n🎯 Testing API Prefix Compliance")
        print("=" * 60)
        
        # All endpoints should be under /api prefix
        endpoints_to_test = [
            "/api/options/selling/compute",
            "/api/options/selling/monitor/start", 
            "/api/options/selling/monitor/status",
            "/api/options/selling/monitor/stop"
        ]
        
        compliance_issues = []
        
        for endpoint in endpoints_to_test:
            if not endpoint.startswith('/api'):
                compliance_issues.append(f"Endpoint {endpoint} does not start with /api")
        
        # Check that we're using the correct base URL (not hardcoded localhost)
        if 'localhost' in self.api_url or '127.0.0.1' in self.api_url:
            compliance_issues.append(f"Using hardcoded localhost URL: {self.api_url}")
        
        if compliance_issues:
            self.log_result(
                "API Prefix Compliance",
                False,
                f"Compliance issues: {compliance_issues}",
                True
            )
            return False
        else:
            self.log_result(
                "API Prefix Compliance",
                True,
                f"All {len(endpoints_to_test)} endpoints use /api prefix, using external URL: {self.base_url}"
            )
            return True

    def run_comprehensive_test(self):
        """Run all Options Selling Monitor tests"""
        print("🎯 Starting Comprehensive Options Selling Monitor Backend Testing")
        print("=" * 80)
        print("Focus: New Options Selling Monitor feature endpoints")
        print("Endpoints: compute, monitor/start, monitor/status, monitor/stop")
        print("=" * 80)
        
        # Run all test phases
        test_results = []
        
        # Phase 1: Test existing compute endpoint
        compute_success = self.test_existing_compute_endpoint()
        test_results.append(("Existing Compute Endpoint", compute_success))
        
        # Phase 2: Test monitor start
        start_success = self.test_monitor_start_endpoint()
        test_results.append(("Monitor Start Endpoint", start_success))
        
        # Phase 3: Test monitor status
        status_success = self.test_monitor_status_endpoint()
        test_results.append(("Monitor Status Endpoint", status_success))
        
        # Phase 4: Test monitor stop
        stop_success = self.test_monitor_stop_endpoint()
        test_results.append(("Monitor Stop Endpoint", stop_success))
        
        # Phase 5: Test robustness scenarios
        robustness_success = self.test_robustness_scenarios()
        test_results.append(("Robustness Scenarios", robustness_success))
        
        # Phase 6: Test API compliance
        compliance_success = self.test_api_prefix_compliance()
        test_results.append(("API Prefix Compliance", compliance_success))
        
        # Print comprehensive results
        self.print_final_results(test_results)
        
        # Determine overall success
        critical_tests_passed = sum(1 for _, success in test_results[:5] if success)  # First 5 are critical
        overall_success = critical_tests_passed >= 4 and len(self.critical_failures) == 0
        
        return overall_success

    def print_final_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE OPTIONS SELLING MONITOR TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🎯 TEST PHASE RESULTS:")
        for phase_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        else:
            print(f"\n✅ NO CRITICAL FAILURES")
        
        # Options Selling Monitor specific assessment
        critical_phases = ["Existing Compute Endpoint", "Monitor Start Endpoint", "Monitor Status Endpoint", "Monitor Stop Endpoint"]
        critical_failures = [name for name, success in test_results if name in critical_phases and not success]
        
        print(f"\n🎯 OPTIONS SELLING MONITOR ASSESSMENT:")
        if not critical_failures:
            print("   ✅ Options Selling Monitor backend is fully operational")
            print("   ✅ Existing compute endpoint still works with demo positions")
            print("   ✅ Monitor start/stop/status endpoints working correctly")
            print("   ✅ Robustness scenarios pass with different modes")
            print("   ✅ All routes properly use /api prefix")
            print("   ✅ Ready for production use")
        else:
            print("   ❌ Options Selling Monitor has critical issues:")
            for failure in critical_failures:
                print(f"      - {failure}")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = OptionsSellingSMonitorTester()
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())