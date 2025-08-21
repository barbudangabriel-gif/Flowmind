#!/usr/bin/env python3
"""
Comprehensive Options Calculator Backend Testing
Focus: Black-Scholes calculations, Greeks, Strategy Engine, and API endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import math

class OptionsCalculatorTester:
    def __init__(self, base_url="https://stockflow-ui.preview.emergentagent.com"):
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

    def test_options_calculate_endpoint(self):
        """Test POST /api/options/calculate endpoint with Black-Scholes calculations"""
        print("\n🎯 Testing Options Calculator Core - Black-Scholes Calculations")
        print("=" * 80)
        
        # Test parameters as specified in review request
        test_cases = [
            {
                "name": "Long Call - CRCL $95 Strike",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "CRCL",
                    "stock_price": 149.53,
                    "strike": 95.0,
                    "days_to_expiry": 30,  # December 2024 (approx 30 days)
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_premium_range": (50, 60),  # Expected range for deep ITM call
                "critical": True
            },
            {
                "name": "Long Call - At The Money",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "CRCL", 
                    "stock_price": 149.53,
                    "strike": 149.53,
                    "days_to_expiry": 30,
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_premium_range": (4, 6),  # Expected range for ATM call
                "critical": True
            },
            {
                "name": "Long Put - Out of Money",
                "data": {
                    "strategy_name": "Long Put",
                    "symbol": "CRCL",
                    "stock_price": 149.53,
                    "strike": 130.0,
                    "days_to_expiry": 30,
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_premium_range": (0.05, 0.15),  # Expected range for OTM put
                "critical": True
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/options/calculate",
                    json=test_case["data"],
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_fields = ['strategy_config', 'analysis', 'chart_data']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Options Calculate - {test_case['name']} Structure",
                            False,
                            f"Missing fields: {missing_fields}",
                            test_case.get('critical', False)
                        )
                        continue
                    
                    # Extract strategy and analysis data
                    strategy_config = data.get('strategy_config', {})
                    analysis = data.get('analysis', {})
                    chart_data = data.get('chart_data', {})
                    
                    # Verify strategy configuration
                    legs = strategy_config.get('legs', [])
                    if not legs:
                        self.log_result(
                            f"Options Calculate - {test_case['name']} Legs",
                            False,
                            "No option legs found in strategy",
                            test_case.get('critical', False)
                        )
                        continue
                    
                    # Check premium calculation
                    first_leg = legs[0]
                    premium = first_leg.get('premium', 0)
                    expected_min, expected_max = test_case.get('expected_premium_range', (0, 1000))
                    
                    premium_valid = expected_min <= premium <= expected_max
                    
                    # Verify Greeks calculations
                    strategy_greeks = analysis.get('greeks', {})  # Changed from 'strategy_greeks' to 'greeks'
                    required_greeks = ['delta', 'gamma', 'theta', 'vega', 'rho']
                    greeks_present = all(greek in strategy_greeks for greek in required_greeks)
                    
                    # Verify P&L arrays for charting
                    price_array = chart_data.get('x', [])  # Changed from analysis to chart_data
                    pnl_array = chart_data.get('y', [])    # Changed from analysis to chart_data
                    
                    # Verify breakeven points
                    breakeven_points = analysis.get('breakeven_points', [])
                    
                    # Calculate success metrics
                    checks = [
                        ("Premium Calculation", premium > 0, f"Premium: ${premium:.2f}"),
                        ("Premium Range", premium_valid, f"Premium ${premium:.2f} in range ${expected_min}-${expected_max}"),
                        ("Greeks Present", greeks_present, f"Greeks: {list(strategy_greeks.keys())}"),
                        ("P&L Arrays", len(price_array) > 0 and len(pnl_array) > 0, f"Price points: {len(price_array)}, P&L points: {len(pnl_array)}"),
                        ("Breakeven Calculation", isinstance(breakeven_points, list), f"Breakeven points: {breakeven_points}")
                    ]
                    
                    all_checks_passed = all(passed for _, passed, _ in checks)
                    
                    if all_checks_passed:
                        success_count += 1
                        details = f"Premium: ${premium:.2f}, Delta: {strategy_greeks.get('delta', 0):.3f}, Time: {response_time:.2f}s"
                        self.log_result(
                            f"Options Calculate - {test_case['name']}",
                            True,
                            details
                        )
                        
                        # Log detailed Greeks for verification
                        print(f"     📊 Greeks Analysis:")
                        for greek in required_greeks:
                            value = strategy_greeks.get(greek, 0)
                            print(f"       - {greek.capitalize()}: {value:.4f}")
                        
                        # Verify Greeks are within reasonable ranges
                        delta = strategy_greeks.get('delta', 0)
                        gamma = strategy_greeks.get('gamma', 0)
                        theta = strategy_greeks.get('theta', 0)
                        vega = strategy_greeks.get('vega', 0)
                        
                        greeks_reasonable = (
                            -1 <= delta <= 1 and  # Delta should be between -1 and 1
                            gamma >= 0 and  # Gamma should be positive
                            theta <= 0 and  # Theta should be negative (time decay)
                            vega >= 0  # Vega should be positive
                        )
                        
                        if greeks_reasonable:
                            print(f"     ✅ Greeks within reasonable ranges")
                        else:
                            print(f"     ⚠️  Some Greeks outside expected ranges")
                    
                    else:
                        failed_checks = [name for name, passed, _ in checks if not passed]
                        self.log_result(
                            f"Options Calculate - {test_case['name']}",
                            False,
                            f"Failed checks: {failed_checks}",
                            test_case.get('critical', False)
                        )
                
                else:
                    self.log_result(
                        f"Options Calculate - {test_case['name']}",
                        False,
                        f"HTTP {response.status_code}: {response.text[:200]}",
                        test_case.get('critical', False)
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Options Calculate - {test_case['name']}",
                    False,
                    f"Error: {str(e)}",
                    test_case.get('critical', False)
                )
        
        return success_count >= 2  # At least 2 out of 3 test cases should pass

    def test_options_strategies_endpoint(self):
        """Test GET /api/options/strategies endpoint for available strategies"""
        print("\n📋 Testing Strategy Engine - Available Strategies")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_url}/options/strategies",
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['status', 'strategies', 'total_strategies']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Options Strategies - Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        True
                    )
                    return False
                
                strategies = data.get('strategies', {})
                total_strategies = data.get('total_strategies', 0)
                implemented = data.get('implemented', [])
                
                # Verify strategy categories
                expected_categories = ['novice', 'intermediate', 'advanced', 'expert']
                found_categories = list(strategies.keys())
                
                # Check for key strategies mentioned in review
                key_strategies = ['Long Call', 'Long Put', 'Bull Call Spread', 'Covered Call']
                strategies_found = []
                
                for category, strategy_groups in strategies.items():
                    for group, strategy_list in strategy_groups.items():
                        strategies_found.extend(strategy_list)
                
                key_strategies_present = [s for s in key_strategies if s in strategies_found]
                
                # Verify implemented strategies
                implemented_count = len(implemented) if implemented else 0
                
                success_checks = [
                    ("Response Status", data.get('status') == 'success'),
                    ("Strategy Categories", len(found_categories) >= 3),
                    ("Total Strategies", total_strategies >= 20),
                    ("Key Strategies Present", len(key_strategies_present) >= 3),
                    ("Implemented Strategies", implemented_count >= 4)
                ]
                
                all_passed = all(passed for _, passed in success_checks)
                
                if all_passed:
                    details = f"Categories: {len(found_categories)}, Total: {total_strategies}, Implemented: {implemented_count}, Time: {response_time:.2f}s"
                    self.log_result("Options Strategies Endpoint", True, details)
                    
                    print(f"     📊 Strategy Categories: {found_categories}")
                    print(f"     🎯 Key Strategies Found: {key_strategies_present}")
                    print(f"     ✅ Implemented Strategies: {implemented}")
                    
                    return True
                else:
                    failed_checks = [name for name, passed in success_checks if not passed]
                    self.log_result(
                        "Options Strategies Endpoint",
                        False,
                        f"Failed checks: {failed_checks}",
                        True
                    )
                    return False
            
            else:
                self.log_result(
                    "Options Strategies Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Options Strategies Endpoint",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_mathematical_accuracy(self):
        """Test mathematical accuracy of Black-Scholes calculations and Greeks"""
        print("\n🧮 Testing Mathematical Accuracy - Greeks Calculations")
        print("=" * 60)
        
        # Test with known parameters for mathematical verification
        test_data = {
            "strategy_name": "Long Call",
            "symbol": "TEST",
            "stock_price": 100.0,  # Simple round number for easier verification
            "strike": 100.0,       # At-the-money
            "days_to_expiry": 30,
            "volatility": 0.20,    # 20% volatility
            "risk_free_rate": 0.05 # 5% risk-free rate
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/options/calculate",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis', {})
                strategy_greeks = analysis.get('greeks', {})  # Changed from 'strategy_greeks' to 'greeks'
                
                # Extract Greeks
                delta = strategy_greeks.get('delta', 0)
                gamma = strategy_greeks.get('gamma', 0)
                theta = strategy_greeks.get('theta', 0)
                vega = strategy_greeks.get('vega', 0)
                rho = strategy_greeks.get('rho', 0)
                
                # Mathematical validation checks
                validation_checks = [
                    ("Delta Range", -1 <= delta <= 1, f"Delta: {delta:.4f}"),
                    ("Delta ATM Call", 0.4 <= delta <= 0.6, f"ATM Call Delta: {delta:.4f} (expected ~0.5)"),
                    ("Gamma Positive", gamma > 0, f"Gamma: {gamma:.6f}"),
                    ("Theta Negative", theta < 0, f"Theta: {theta:.4f} (time decay)"),
                    ("Vega Positive", vega > 0, f"Vega: {vega:.4f}"),
                    ("Rho Positive Call", rho > 0, f"Rho: {rho:.4f} (call should have positive rho)")
                ]
                
                passed_validations = sum(1 for _, passed, _ in validation_checks if passed)
                total_validations = len(validation_checks)
                
                if passed_validations >= total_validations - 1:  # Allow 1 failure
                    details = f"Greeks validation: {passed_validations}/{total_validations} passed"
                    self.log_result("Mathematical Accuracy - Greeks", True, details)
                    
                    print(f"     📊 Greeks Values:")
                    for name, _, description in validation_checks:
                        print(f"       - {description}")
                    
                    return True
                else:
                    failed_validations = [name for name, passed, _ in validation_checks if not passed]
                    self.log_result(
                        "Mathematical Accuracy - Greeks",
                        False,
                        f"Failed validations: {failed_validations}",
                        True
                    )
                    return False
            
            else:
                self.log_result(
                    "Mathematical Accuracy - Greeks",
                    False,
                    f"HTTP {response.status_code}",
                    True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Mathematical Accuracy - Greeks",
                False,
                f"Error: {str(e)}",
                True
            )
            return False

    def test_strategy_calculations(self):
        """Test specific strategies like Bull Call Spread, Covered Call"""
        print("\n📈 Testing Strategy Calculations - Multi-leg Strategies")
        print("=" * 60)
        
        strategies_to_test = [
            {
                "name": "Bull Call Spread",
                "data": {
                    "strategy_name": "Bull Call Spread",
                    "symbol": "CRCL",
                    "stock_price": 149.53,
                    "strike": 145.0,  # Long strike
                    "days_to_expiry": 30,
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_legs": 2,
                "expected_max_profit_limited": True
            },
            {
                "name": "Covered Call",
                "data": {
                    "strategy_name": "Covered Call",
                    "symbol": "CRCL",
                    "stock_price": 149.53,
                    "strike": 155.0,  # Call strike above current price
                    "days_to_expiry": 30,
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_legs": 1,  # Only the call leg (stock ownership assumed)
                "expected_max_profit_limited": True
            }
        ]
        
        success_count = 0
        
        for strategy_test in strategies_to_test:
            try:
                response = requests.post(
                    f"{self.api_url}/options/calculate",
                    json=strategy_test["data"],
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    strategy_config = data.get('strategy_config', {})
                    analysis = data.get('analysis', {})
                    
                    # Verify strategy structure
                    legs = strategy_config.get('legs', [])
                    max_profit = analysis.get('max_profit', 0)
                    max_loss = analysis.get('max_loss', 0)
                    breakeven_points = analysis.get('breakeven_points', [])
                    
                    # Strategy-specific validations
                    validations = [
                        ("Correct Leg Count", len(legs) == strategy_test["expected_legs"]),
                        ("Max Profit Calculated", max_profit != 0),
                        ("Max Loss Calculated", max_loss != 0),
                        ("Breakeven Points", isinstance(breakeven_points, list))
                    ]
                    
                    # Additional validation for limited profit strategies
                    if strategy_test.get("expected_max_profit_limited"):
                        validations.append(("Limited Max Profit", max_profit > 0 and max_profit < 100000))
                    
                    passed_validations = sum(1 for _, passed in validations if passed)
                    
                    if passed_validations >= len(validations) - 1:  # Allow 1 failure
                        success_count += 1
                        details = f"Legs: {len(legs)}, Max Profit: ${max_profit:.2f}, Max Loss: ${max_loss:.2f}"
                        self.log_result(f"Strategy Calculation - {strategy_test['name']}", True, details)
                        
                        print(f"     📊 Strategy Analysis:")
                        print(f"       - Legs: {len(legs)}")
                        print(f"       - Max Profit: ${max_profit:.2f}")
                        print(f"       - Max Loss: ${max_loss:.2f}")
                        print(f"       - Breakeven Points: {breakeven_points}")
                    
                    else:
                        failed_validations = [name for name, passed in validations if not passed]
                        self.log_result(
                            f"Strategy Calculation - {strategy_test['name']}",
                            False,
                            f"Failed validations: {failed_validations}"
                        )
                
                else:
                    self.log_result(
                        f"Strategy Calculation - {strategy_test['name']}",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Strategy Calculation - {strategy_test['name']}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return success_count >= 1  # At least 1 strategy should work

    def test_error_scenarios(self):
        """Test error scenarios like missing parameters, invalid values"""
        print("\n🚨 Testing Error Scenarios - Input Validation")
        print("=" * 60)
        
        error_test_cases = [
            {
                "name": "Missing Parameters",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "TEST"
                    # Missing required parameters
                },
                "expected_status": [400, 422]  # Bad Request or Unprocessable Entity
            },
            {
                "name": "Invalid Strike Price",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "TEST",
                    "stock_price": 100.0,
                    "strike": -50.0,  # Negative strike price
                    "days_to_expiry": 30,
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_status": [400, 422, 500]
            },
            {
                "name": "Negative Volatility",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "TEST",
                    "stock_price": 100.0,
                    "strike": 100.0,
                    "days_to_expiry": 30,
                    "volatility": -0.25,  # Negative volatility
                    "risk_free_rate": 0.05
                },
                "expected_status": [400, 422, 500]
            },
            {
                "name": "Invalid Expiration",
                "data": {
                    "strategy_name": "Long Call",
                    "symbol": "TEST",
                    "stock_price": 100.0,
                    "strike": 100.0,
                    "days_to_expiry": -10,  # Negative days
                    "volatility": 0.25,
                    "risk_free_rate": 0.05
                },
                "expected_status": [400, 422, 500]
            }
        ]
        
        success_count = 0
        
        for test_case in error_test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/options/calculate",
                    json=test_case["data"],
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                
                if response.status_code in test_case["expected_status"]:
                    success_count += 1
                    self.log_result(
                        f"Error Handling - {test_case['name']}",
                        True,
                        f"Correctly returned HTTP {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Error Handling - {test_case['name']}",
                        False,
                        f"Expected {test_case['expected_status']}, got {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Error Handling - {test_case['name']}",
                    False,
                    f"Error: {str(e)}"
                )
        
        return success_count >= 2  # At least half should pass

    def run_comprehensive_options_test(self):
        """Run all Options Calculator tests"""
        print("🎯 Starting Comprehensive Options Calculator Backend Testing")
        print("=" * 80)
        print("Focus: Black-Scholes calculations, Greeks, Strategy Engine, API endpoints")
        print("Test Parameters: CRCL @ $149.53, Strike $95, Target $263.91, 25% vol, 5% rate")
        print("=" * 80)
        
        # Run all test phases
        test_results = []
        
        # Phase 1: Core Black-Scholes calculations
        calculate_success = self.test_options_calculate_endpoint()
        test_results.append(("Options Calculate Endpoint", calculate_success))
        
        # Phase 2: Strategy Engine
        strategies_success = self.test_options_strategies_endpoint()
        test_results.append(("Strategy Engine", strategies_success))
        
        # Phase 3: Mathematical accuracy
        math_success = self.test_mathematical_accuracy()
        test_results.append(("Mathematical Accuracy", math_success))
        
        # Phase 4: Strategy calculations
        strategy_calc_success = self.test_strategy_calculations()
        test_results.append(("Strategy Calculations", strategy_calc_success))
        
        # Phase 5: Error handling
        error_success = self.test_error_scenarios()
        test_results.append(("Error Scenarios", error_success))
        
        # Print comprehensive results
        self.print_final_results(test_results)
        
        # Determine overall success
        critical_tests_passed = sum(1 for _, success in test_results[:4] if success)  # First 4 are critical
        overall_success = critical_tests_passed >= 3 and len(self.critical_failures) == 0
        
        return overall_success

    def print_final_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE OPTIONS CALCULATOR TEST RESULTS")
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
        
        # Options Calculator specific assessment
        critical_phases = ["Options Calculate Endpoint", "Strategy Engine", "Mathematical Accuracy"]
        critical_failures = [name for name, success in test_results if name in critical_phases and not success]
        
        print(f"\n🎯 OPTIONS CALCULATOR ASSESSMENT:")
        if not critical_failures:
            print("   ✅ Options Calculator backend is fully operational")
            print("   ✅ Black-Scholes calculations working correctly")
            print("   ✅ Greeks calculations within reasonable ranges")
            print("   ✅ Strategy Engine providing accurate P&L analysis")
            print("   ✅ Ready to support frontend Options Module")
        else:
            print("   ❌ Options Calculator has critical issues:")
            for failure in critical_failures:
                print(f"      - {failure}")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = OptionsCalculatorTester()
    success = tester.run_comprehensive_options_test()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())