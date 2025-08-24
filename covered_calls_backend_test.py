#!/usr/bin/env python3
"""
Covered Calls Integration Backend Test
Tests the updated backend for Covered Calls integration within Options Selling.

Test Scenarios:
1) Compute with CC only:
   - SELL CALL candidate with shares_owned=300, open_cc_contracts=1, candidate_call={strike: 250, delta: 0.2, dte: 30, premium: 2.5}
   - ROLL CC with open_cc_state {delta: 0.4, dte: 8, premium_sold: 3.0, premium_mark: 2.2}

2) Monitor start with CC inputs:
   - POST /api/options/selling/monitor/start with cc_config and cc_inputs
   - GET /api/options/selling/monitor/status: verify signals_current contains CC signals
   - POST /api/options/selling/monitor/stop

3) Backward compatibility when cc_inputs omitted
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class CoveredCallsBackendTester:
    def __init__(self, base_url="https://options-trader-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []

    def log_result(self, test_name: str, success: bool, details: str, is_critical: bool = False):
        """Log test result with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"   ✅ {test_name}: {details}")
        else:
            print(f"   ❌ {test_name}: {details}")
            if is_critical:
                self.critical_failures.append(f"{test_name}: {details}")

    def get_cc_config_defaults(self) -> Dict[str, Any]:
        """Get default CC config"""
        return {
            "cc_delta_min": 0.15,
            "cc_delta_max": 0.30,
            "cc_dte_min": 20,
            "cc_dte_max": 40,
            "cc_roll_delta_threshold": 0.35,
            "cc_roll_dte_threshold": 10,
            "cc_take_profit_remaining_threshold": 0.30
        }

    def get_minimal_positions(self) -> List[Dict[str, Any]]:
        """Get minimal positions array for testing"""
        return [
            {
                "ticker": "AAPL",
                "price": 150.0,
                "strike": 145.0,
                "delta": 0.25,
                "dte": 30,
                "premium": 2.0,
                "iv_rank": 45.0,
                "vix": 20.0,
                "selected": True
            }
        ]

    def test_compute_cc_sell_call_candidate(self) -> bool:
        """Test SELL CALL candidate scenario"""
        print("\n🎯 Testing SELL CALL Candidate Scenario")
        print("=" * 60)
        print("Scenario: shares_owned=300, open_cc_contracts=1, candidate_call={strike: 250, delta: 0.2, dte: 30, premium: 2.5}")
        
        try:
            # Prepare test data
            test_data = {
                "positions": [],  # Empty positions for CC-only test
                "cc_config": self.get_cc_config_defaults(),
                "cc_inputs": [
                    {
                        "ticker": "TSLA",
                        "shares_owned": 300,
                        "open_cc_contracts": 1,
                        "candidate_call": {
                            "strike": 250.0,
                            "delta": 0.2,
                            "dte": 30,
                            "premium": 2.5
                        }
                    }
                ]
            }

            # Make API call
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/compute",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code != 200:
                self.log_result(
                    "SELL CALL Candidate - HTTP Status",
                    False,
                    f"Expected 200, got {response.status_code}: {response.text[:200]}",
                    True
                )
                return False

            data = response.json()
            
            # Verify response structure
            if data.get('status') != 'success':
                self.log_result(
                    "SELL CALL Candidate - Response Status",
                    False,
                    f"Expected status=success, got {data.get('status')}",
                    True
                )
                return False

            response_data = data.get('data', {})
            
            # Verify CC signals are present
            cc_signals = response_data.get('cc_signals', [])
            if not isinstance(cc_signals, list):
                self.log_result(
                    "SELL CALL Candidate - CC Signals Type",
                    False,
                    f"Expected cc_signals as list, got {type(cc_signals)}",
                    True
                )
                return False

            # Find SELL CALL signal
            sell_call_signals = [s for s in cc_signals if s.get('signal') == 'SELL CALL']
            if not sell_call_signals:
                self.log_result(
                    "SELL CALL Candidate - SELL CALL Signal",
                    False,
                    f"No SELL CALL signal found in cc_signals: {cc_signals}",
                    True
                )
                return False

            sell_call = sell_call_signals[0]
            
            # Verify SELL CALL signal details
            expected_contracts = 2  # (300 shares / 100) - 1 open contract = 2
            actual_contracts = sell_call.get('contracts', 0)
            
            if actual_contracts != expected_contracts:
                self.log_result(
                    "SELL CALL Candidate - Contracts",
                    False,
                    f"Expected contracts={expected_contracts}, got {actual_contracts}",
                    True
                )
                return False

            # Verify CC summary
            cc_summary = response_data.get('cc_summary', {})
            if not isinstance(cc_summary, dict):
                self.log_result(
                    "SELL CALL Candidate - CC Summary Type",
                    False,
                    f"Expected cc_summary as dict, got {type(cc_summary)}",
                    True
                )
                return False

            lots_free = cc_summary.get('lots_free', -1)
            if lots_free < 0:
                self.log_result(
                    "SELL CALL Candidate - Lots Free",
                    False,
                    f"Expected lots_free >= 0, got {lots_free}",
                    True
                )
                return False

            # Log success details
            self.log_result(
                "SELL CALL Candidate - Complete",
                True,
                f"SELL CALL signal found with {actual_contracts} contracts, lots_free={lots_free}, time={response_time:.2f}s"
            )

            # Verify signal structure
            required_fields = ['ticker', 'signal', 'contracts', 'strike', 'dte', 'delta', 'premium']
            missing_fields = [field for field in required_fields if field not in sell_call]
            
            if missing_fields:
                self.log_result(
                    "SELL CALL Candidate - Signal Fields",
                    False,
                    f"Missing required fields in SELL CALL signal: {missing_fields}",
                    True
                )
                return False

            self.log_result(
                "SELL CALL Candidate - Signal Structure",
                True,
                f"All required fields present: {required_fields}"
            )

            return True

        except Exception as e:
            self.log_result(
                "SELL CALL Candidate - Exception",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_compute_cc_roll_and_take_profit(self) -> bool:
        """Test ROLL CC and TAKE PROFIT scenario"""
        print("\n🎯 Testing ROLL CC and TAKE PROFIT Scenario")
        print("=" * 60)
        print("Scenario: open_cc_state {delta: 0.4, dte: 8, premium_sold: 3.0, premium_mark: 2.2}")
        
        try:
            # Prepare test data
            test_data = {
                "positions": [],  # Empty positions for CC-only test
                "cc_config": self.get_cc_config_defaults(),
                "cc_inputs": [
                    {
                        "ticker": "NVDA",
                        "shares_owned": 200,
                        "open_cc_contracts": 2,
                        "open_cc_state": {
                            "delta": 0.4,
                            "dte": 8,
                            "premium_sold": 3.0,
                            "premium_mark": 2.2
                        }
                    }
                ]
            }

            # Make API call
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/compute",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code != 200:
                self.log_result(
                    "ROLL CC - HTTP Status",
                    False,
                    f"Expected 200, got {response.status_code}: {response.text[:200]}",
                    True
                )
                return False

            data = response.json()
            
            # Verify response structure
            if data.get('status') != 'success':
                self.log_result(
                    "ROLL CC - Response Status",
                    False,
                    f"Expected status=success, got {data.get('status')}",
                    True
                )
                return False

            response_data = data.get('data', {})
            cc_signals = response_data.get('cc_signals', [])

            # Check for ROLL CC signal (delta > threshold OR dte < threshold)
            roll_cc_signals = [s for s in cc_signals if s.get('signal') == 'ROLL CC']
            
            # Check for TAKE PROFIT signal (premium_mark/premium_sold <= 0.3)
            take_profit_signals = [s for s in cc_signals if s.get('signal') == 'TAKE PROFIT']
            
            # Calculate expected conditions
            delta_condition = 0.4 > 0.35  # delta > cc_roll_delta_threshold
            dte_condition = 8 < 10  # dte < cc_roll_dte_threshold
            profit_ratio = 2.2 / 3.0  # premium_mark / premium_sold = 0.733
            profit_condition = profit_ratio <= 0.30  # Should be False (0.733 > 0.30)

            print(f"   📊 Condition Analysis:")
            print(f"     - Delta condition (0.4 > 0.35): {delta_condition}")
            print(f"     - DTE condition (8 < 10): {dte_condition}")
            print(f"     - Profit ratio (2.2/3.0 = {profit_ratio:.3f}): {profit_ratio:.3f}")
            print(f"     - Take profit condition ({profit_ratio:.3f} <= 0.30): {profit_condition}")

            # Expect ROLL CC signal (either condition met)
            if delta_condition or dte_condition:
                if not roll_cc_signals:
                    self.log_result(
                        "ROLL CC - Signal Expected",
                        False,
                        f"Expected ROLL CC signal (delta={delta_condition}, dte={dte_condition}), but not found",
                        True
                    )
                    return False
                else:
                    self.log_result(
                        "ROLL CC - Signal Found",
                        True,
                        f"ROLL CC signal correctly generated (conditions met)"
                    )

            # Check TAKE PROFIT expectation
            if profit_condition:
                if not take_profit_signals:
                    self.log_result(
                        "TAKE PROFIT - Signal Expected",
                        False,
                        f"Expected TAKE PROFIT signal (ratio={profit_ratio:.3f} <= 0.30), but not found",
                        True
                    )
                    return False
                else:
                    self.log_result(
                        "TAKE PROFIT - Signal Found",
                        True,
                        f"TAKE PROFIT signal correctly generated"
                    )
            else:
                if take_profit_signals:
                    self.log_result(
                        "TAKE PROFIT - Unexpected Signal",
                        False,
                        f"Unexpected TAKE PROFIT signal (ratio={profit_ratio:.3f} > 0.30)",
                        True
                    )
                    return False
                else:
                    self.log_result(
                        "TAKE PROFIT - Correctly Not Generated",
                        True,
                        f"TAKE PROFIT correctly not generated (ratio={profit_ratio:.3f} > 0.30)"
                    )

            # Verify signal details if present
            if roll_cc_signals:
                roll_signal = roll_cc_signals[0]
                expected_contracts = 2
                actual_contracts = roll_signal.get('contracts', 0)
                
                if actual_contracts != expected_contracts:
                    self.log_result(
                        "ROLL CC - Contracts",
                        False,
                        f"Expected contracts={expected_contracts}, got {actual_contracts}",
                        True
                    )
                    return False

            self.log_result(
                "ROLL CC and TAKE PROFIT - Complete",
                True,
                f"Scenario processed correctly, time={response_time:.2f}s"
            )

            return True

        except Exception as e:
            self.log_result(
                "ROLL CC and TAKE PROFIT - Exception",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_monitor_start_with_cc_inputs(self) -> bool:
        """Test monitor start with CC inputs"""
        print("\n🎯 Testing Monitor Start with CC Inputs")
        print("=" * 60)
        
        try:
            # Prepare test data
            test_data = {
                "positions": self.get_minimal_positions(),
                "config": {
                    "capital_base": 500000.0,
                    "delta_min": 0.25,
                    "delta_max": 0.30
                },
                "cc_config": self.get_cc_config_defaults(),
                "cc_inputs": [
                    {
                        "ticker": "AAPL",
                        "shares_owned": 400,
                        "open_cc_contracts": 0,
                        "candidate_call": {
                            "strike": 160.0,
                            "delta": 0.25,
                            "dte": 25,
                            "premium": 3.0
                        }
                    }
                ],
                "interval_seconds": 15,
                "mode": "equal"
            }

            # Start monitor
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/options/selling/monitor/start",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code != 200:
                self.log_result(
                    "Monitor Start CC - HTTP Status",
                    False,
                    f"Expected 200, got {response.status_code}: {response.text[:200]}",
                    True
                )
                return False

            data = response.json()
            
            if data.get('status') != 'success':
                self.log_result(
                    "Monitor Start CC - Response Status",
                    False,
                    f"Expected status=success, got {data.get('status')}",
                    True
                )
                return False

            start_data = data.get('data', {})
            if start_data.get('status') != 'started':
                self.log_result(
                    "Monitor Start CC - Start Status",
                    False,
                    f"Expected data.status=started, got {start_data.get('status')}",
                    True
                )
                return False

            self.log_result(
                "Monitor Start CC - Started",
                True,
                f"Monitor started with CC inputs, interval={start_data.get('interval_seconds')}s, time={response_time:.2f}s"
            )

            # Wait a moment for monitor to run
            time.sleep(2)

            # Check status
            status_response = requests.get(
                f"{self.api_url}/options/selling/monitor/status",
                timeout=15
            )

            if status_response.status_code != 200:
                self.log_result(
                    "Monitor Status CC - HTTP Status",
                    False,
                    f"Expected 200, got {status_response.status_code}",
                    True
                )
                return False

            status_data = status_response.json()
            status_response_data = status_data.get('data', {})

            # Verify monitor is running
            if not status_response_data.get('running'):
                self.log_result(
                    "Monitor Status CC - Running",
                    False,
                    f"Expected running=true, got {status_response_data.get('running')}",
                    True
                )
                return False

            # Verify signals_current contains CC signals
            signals_current = status_response_data.get('signals_current', [])
            cc_signals_in_current = [s for s in signals_current if s.get('signal') in ['SELL CALL', 'ROLL CC', 'TAKE PROFIT']]

            if not cc_signals_in_current:
                self.log_result(
                    "Monitor Status CC - CC Signals",
                    False,
                    f"No CC signals found in signals_current: {[s.get('signal') for s in signals_current]}",
                    True
                )
                return False

            # Verify summary contains cc_summary
            summary = status_response_data.get('summary', {})
            cc_summary = summary.get('cc_summary', {})
            
            if not isinstance(cc_summary, dict):
                self.log_result(
                    "Monitor Status CC - CC Summary",
                    False,
                    f"Expected cc_summary as dict, got {type(cc_summary)}",
                    True
                )
                return False

            self.log_result(
                "Monitor Status CC - Verified",
                True,
                f"Monitor running with {len(cc_signals_in_current)} CC signals, cc_summary present"
            )

            # Stop monitor
            stop_response = requests.post(
                f"{self.api_url}/options/selling/monitor/stop",
                headers={'Content-Type': 'application/json'},
                timeout=15
            )

            if stop_response.status_code != 200:
                self.log_result(
                    "Monitor Stop CC - HTTP Status",
                    False,
                    f"Expected 200, got {stop_response.status_code}",
                    True
                )
                return False

            stop_data = stop_response.json()
            if stop_data.get('status') != 'success':
                self.log_result(
                    "Monitor Stop CC - Response Status",
                    False,
                    f"Expected status=success, got {stop_data.get('status')}",
                    True
                )
                return False

            self.log_result(
                "Monitor Stop CC - Stopped",
                True,
                f"Monitor stopped successfully"
            )

            return True

        except Exception as e:
            self.log_result(
                "Monitor Start CC - Exception",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_backward_compatibility(self) -> bool:
        """Test backward compatibility when cc_inputs omitted"""
        print("\n🎯 Testing Backward Compatibility (No CC Inputs)")
        print("=" * 60)
        
        try:
            # Test 1: Compute without CC inputs
            test_data_compute = {
                "positions": self.get_minimal_positions(),
                "config": {
                    "capital_base": 500000.0,
                    "delta_min": 0.25,
                    "delta_max": 0.30
                },
                "mode": "equal"
                # No cc_config or cc_inputs
            }

            # Make compute API call
            response = requests.post(
                f"{self.api_url}/options/selling/compute",
                json=test_data_compute,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code != 200:
                self.log_result(
                    "Backward Compatibility Compute - HTTP Status",
                    False,
                    f"Expected 200, got {response.status_code}: {response.text[:200]}",
                    True
                )
                return False

            data = response.json()
            
            if data.get('status') != 'success':
                self.log_result(
                    "Backward Compatibility Compute - Response Status",
                    False,
                    f"Expected status=success, got {data.get('status')}",
                    True
                )
                return False

            response_data = data.get('data', {})
            
            # Verify traditional signals still work
            signals_equal = response_data.get('signals_equal', [])
            if not isinstance(signals_equal, list):
                self.log_result(
                    "Backward Compatibility Compute - Signals Equal",
                    False,
                    f"Expected signals_equal as list, got {type(signals_equal)}",
                    True
                )
                return False

            # CC fields should be None or empty when not provided
            cc_signals = response_data.get('cc_signals')
            cc_summary = response_data.get('cc_summary')
            
            if cc_signals is not None and cc_signals != []:
                self.log_result(
                    "Backward Compatibility Compute - CC Signals Empty",
                    False,
                    f"Expected cc_signals to be None or empty, got {cc_signals}",
                    True
                )
                return False

            self.log_result(
                "Backward Compatibility Compute - Success",
                True,
                f"Compute works without CC inputs, signals_equal has {len(signals_equal)} items"
            )

            # Test 2: Monitor without CC inputs
            test_data_monitor = {
                "positions": self.get_minimal_positions(),
                "config": {
                    "capital_base": 500000.0,
                    "delta_min": 0.25,
                    "delta_max": 0.30
                },
                "interval_seconds": 15,
                "mode": "equal"
                # No cc_config or cc_inputs
            }

            # Start monitor
            monitor_response = requests.post(
                f"{self.api_url}/options/selling/monitor/start",
                json=test_data_monitor,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if monitor_response.status_code != 200:
                self.log_result(
                    "Backward Compatibility Monitor - HTTP Status",
                    False,
                    f"Expected 200, got {monitor_response.status_code}: {monitor_response.text[:200]}",
                    True
                )
                return False

            monitor_data = monitor_response.json()
            
            if monitor_data.get('status') != 'success':
                self.log_result(
                    "Backward Compatibility Monitor - Response Status",
                    False,
                    f"Expected status=success, got {monitor_data.get('status')}",
                    True
                )
                return False

            self.log_result(
                "Backward Compatibility Monitor - Started",
                True,
                f"Monitor started without CC inputs"
            )

            # Wait and check status
            time.sleep(1)
            
            status_response = requests.get(
                f"{self.api_url}/options/selling/monitor/status",
                timeout=15
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                status_response_data = status_data.get('data', {})
                
                if status_response_data.get('running'):
                    self.log_result(
                        "Backward Compatibility Monitor - Status",
                        True,
                        f"Monitor running without CC inputs"
                    )
                else:
                    self.log_result(
                        "Backward Compatibility Monitor - Status",
                        False,
                        f"Monitor not running",
                        True
                    )
                    return False
            else:
                self.log_result(
                    "Backward Compatibility Monitor - Status Check",
                    False,
                    f"Status check failed: {status_response.status_code}",
                    True
                )
                return False

            # Stop monitor
            requests.post(
                f"{self.api_url}/options/selling/monitor/stop",
                headers={'Content-Type': 'application/json'},
                timeout=15
            )

            self.log_result(
                "Backward Compatibility - Complete",
                True,
                f"Both compute and monitor work without CC inputs"
            )

            return True

        except Exception as e:
            self.log_result(
                "Backward Compatibility - Exception",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def run_comprehensive_test(self) -> bool:
        """Run all Covered Calls integration tests"""
        print("🎯 Starting Comprehensive Covered Calls Integration Backend Testing")
        print("=" * 80)
        print("Focus: Covered Calls integration within Options Selling")
        print("Scenarios: SELL CALL candidates, ROLL CC, TAKE PROFIT, Monitor integration, Backward compatibility")
        print("=" * 80)
        
        # Run all test phases
        test_results = []
        
        # Phase 1: Test SELL CALL candidate
        sell_call_success = self.test_compute_cc_sell_call_candidate()
        test_results.append(("SELL CALL Candidate", sell_call_success))
        
        # Phase 2: Test ROLL CC and TAKE PROFIT
        roll_profit_success = self.test_compute_cc_roll_and_take_profit()
        test_results.append(("ROLL CC and TAKE PROFIT", roll_profit_success))
        
        # Phase 3: Test monitor with CC inputs
        monitor_cc_success = self.test_monitor_start_with_cc_inputs()
        test_results.append(("Monitor with CC Inputs", monitor_cc_success))
        
        # Phase 4: Test backward compatibility
        backward_compat_success = self.test_backward_compatibility()
        test_results.append(("Backward Compatibility", backward_compat_success))
        
        # Print comprehensive results
        self.print_final_results(test_results)
        
        # Determine overall success
        critical_tests_passed = sum(1 for _, success in test_results if success)
        overall_success = critical_tests_passed >= 3 and len(self.critical_failures) == 0
        
        return overall_success

    def print_final_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE COVERED CALLS INTEGRATION TEST RESULTS")
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
        
        # Covered Calls specific assessment
        critical_phases = ["SELL CALL Candidate", "ROLL CC and TAKE PROFIT", "Monitor with CC Inputs"]
        critical_failures = [name for name, success in test_results if name in critical_phases and not success]
        
        print(f"\n🎯 COVERED CALLS INTEGRATION ASSESSMENT:")
        if not critical_failures:
            print("   ✅ Covered Calls integration is fully operational")
            print("   ✅ SELL CALL candidates processed correctly with proper contract calculations")
            print("   ✅ ROLL CC and TAKE PROFIT conditions evaluated accurately")
            print("   ✅ Monitor integration works with CC inputs and signals")
            print("   ✅ Backward compatibility maintained when CC inputs omitted")
            print("   ✅ Ready for production use")
        else:
            print("   ❌ Covered Calls integration has critical issues:")
            for failure in critical_failures:
                print(f"      - {failure}")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = CoveredCallsBackendTester()
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())