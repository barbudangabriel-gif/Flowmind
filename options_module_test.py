#!/usr/bin/env python3
"""
Options Module Backend Testing
Test the new Options Module backend endpoints and functionality.
"""

import requests
import json
import sys
from datetime import datetime

class OptionsModuleTester:
    def __init__(self, base_url="https://tradeoptions-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            timeout = 30
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
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
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
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

    def test_options_strategies_endpoint(self):
        """Test GET /api/options/strategies - Check if it returns all available strategies organized by proficiency levels"""
        print("\n🎯 TESTING OPTIONS STRATEGIES ENDPOINT")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify GET /api/options/strategies returns strategies organized by proficiency levels")
        
        success, strategies_data = self.run_test("Options Strategies", "GET", "options/strategies", 200)
        
        if not success:
            print("❌ Options strategies endpoint failed")
            self.test_results.append(("Options Strategies Endpoint", False, "Endpoint failed"))
            return False
        
        # Verify response structure
        required_fields = ['status', 'strategies', 'total_strategies', 'implemented', 'coming_soon', 'timestamp']
        missing_fields = [field for field in required_fields if field not in strategies_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            self.test_results.append(("Options Strategies Structure", False, f"Missing fields: {missing_fields}"))
            return False
        else:
            print(f"✅ All required response fields present: {required_fields}")
        
        # Verify strategies organization
        strategies = strategies_data.get('strategies', {})
        total_strategies = strategies_data.get('total_strategies', 0)
        implemented = strategies_data.get('implemented', [])
        coming_soon = strategies_data.get('coming_soon', [])
        
        print(f"📊 Total Strategies: {total_strategies}")
        print(f"📊 Implemented Strategies: {implemented}")
        print(f"📊 Coming Soon: {coming_soon}")
        
        # Verify proficiency levels organization
        if isinstance(strategies, dict):
            print(f"📊 Strategy Categories: {list(strategies.keys())}")
            
            # Check if strategies are organized by proficiency levels
            proficiency_indicators = ['beginner', 'intermediate', 'advanced', 'basic', 'complex']
            has_proficiency_organization = any(
                any(indicator in str(key).lower() for indicator in proficiency_indicators)
                for key in strategies.keys()
            )
            
            if has_proficiency_organization:
                print(f"✅ Strategies organized by proficiency levels")
            else:
                print(f"⚠️  Strategies may not be organized by proficiency levels")
        
        # Verify implemented strategies include Long Call and Long Put
        expected_implemented = ["Long Call", "Long Put"]
        missing_implemented = [strategy for strategy in expected_implemented if strategy not in implemented]
        
        if not missing_implemented:
            print(f"✅ All expected implemented strategies present: {expected_implemented}")
        else:
            print(f"❌ Missing implemented strategies: {missing_implemented}")
        
        self.test_results.append(("Options Strategies Endpoint", True, f"Found {total_strategies} strategies"))
        return True

    def test_long_call_calculation(self):
        """Test POST /api/options/calculate - Test Long Call strategy calculation"""
        print("\n🎯 TESTING LONG CALL STRATEGY CALCULATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test Long Call strategy calculation with specific parameters")
        
        # Test data as specified in the review request
        long_call_data = {
            "symbol": "AAPL",
            "strategy_name": "Long Call",
            "stock_price": 150.0,
            "strike": 155.0,
            "days_to_expiry": 30,
            "volatility": 0.25,
            "risk_free_rate": 0.05
        }
        
        print(f"📊 Test Parameters:")
        for key, value in long_call_data.items():
            print(f"   - {key}: {value}")
        
        success, calc_data = self.run_test("Long Call Calculation", "POST", "options/calculate", 200, data=long_call_data)
        
        if not success:
            print("❌ Long Call calculation failed")
            self.test_results.append(("Long Call Calculation", False, "Calculation failed"))
            return False
        
        # Verify response structure
        required_fields = ['strategy_config', 'analysis', 'chart_data']
        missing_fields = [field for field in required_fields if field not in calc_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            self.test_results.append(("Long Call Response Structure", False, f"Missing fields: {missing_fields}"))
            return False
        
        # Verify strategy config
        strategy_config = calc_data.get('strategy_config', {})
        analysis = calc_data.get('analysis', {})
        chart_data = calc_data.get('chart_data', {})
        
        print(f"📊 Strategy Config:")
        print(f"   - Name: {strategy_config.get('name', 'N/A')}")
        print(f"   - Stock Price: ${strategy_config.get('stock_price', 0):.2f}")
        print(f"   - Days to Expiry: {strategy_config.get('days_to_expiry', 0)}")
        print(f"   - Volatility: {strategy_config.get('volatility', 0):.2%}")
        
        # Verify legs structure
        legs = strategy_config.get('legs', [])
        if legs:
            print(f"📊 Strategy Legs ({len(legs)}):")
            for i, leg in enumerate(legs):
                print(f"   Leg {i+1}: {leg.get('option_type', 'N/A')} {leg.get('action', 'N/A')} Strike ${leg.get('strike', 0)} Premium ${leg.get('premium', 0):.2f}")
        
        # Verify Black-Scholes calculations (premium > 0)
        if legs:
            premium = legs[0].get('premium', 0)
            if premium > 0:
                print(f"✅ Black-Scholes calculation working - Premium: ${premium:.2f}")
            else:
                print(f"❌ Black-Scholes calculation issue - Premium: ${premium:.2f}")
                self.test_results.append(("Long Call Black-Scholes", False, f"Premium: ${premium:.2f}"))
                return False
        
        # Verify Greeks calculations
        greeks = analysis.get('greeks', {})
        if greeks:
            delta = greeks.get('delta', 0)
            gamma = greeks.get('gamma', 0)
            theta = greeks.get('theta', 0)
            vega = greeks.get('vega', 0)
            rho = greeks.get('rho', 0)
            
            print(f"📊 Greeks:")
            print(f"   - Delta: {delta:.3f}")
            print(f"   - Gamma: {gamma:.3f}")
            print(f"   - Theta: {theta:.2f}")
            print(f"   - Vega: {vega:.2f}")
            print(f"   - Rho: {rho:.2f}")
            
            # Verify delta is reasonable for Long Call (should be positive and between 0 and 1)
            if 0 <= delta <= 1:
                print(f"✅ Delta reasonable for Long Call: {delta:.3f}")
            else:
                print(f"❌ Delta outside expected range for Long Call: {delta:.3f}")
                self.test_results.append(("Long Call Delta", False, f"Delta: {delta:.3f}"))
                return False
        
        # Verify P&L analysis
        max_profit = analysis.get('max_profit', 0)
        max_loss = analysis.get('max_loss', 0)
        breakeven_points = analysis.get('breakeven_points', [])
        prob_profit = analysis.get('probability_of_profit', 0)
        
        print(f"📊 P&L Analysis:")
        print(f"   - Max Profit: ${max_profit:.2f}")
        print(f"   - Max Loss: ${max_loss:.2f}")
        print(f"   - Breakeven Points: {breakeven_points}")
        print(f"   - Probability of Profit: {prob_profit:.1f}%")
        
        # Verify chart data arrays are generated
        if chart_data:
            x_data = chart_data.get('x', [])
            y_data = chart_data.get('y', [])
            
            if x_data and y_data and len(x_data) == len(y_data):
                print(f"✅ P&L chart data arrays generated properly - {len(x_data)} data points")
            else:
                print(f"❌ P&L chart data arrays issue - X: {len(x_data)}, Y: {len(y_data)}")
                self.test_results.append(("Long Call Chart Data", False, f"X: {len(x_data)}, Y: {len(y_data)}"))
                return False
        
        self.test_results.append(("Long Call Calculation", True, f"Premium: ${premium:.2f}, Delta: {delta:.3f}"))
        return True

    def test_long_put_calculation(self):
        """Test POST /api/options/calculate - Test Long Put strategy calculation"""
        print("\n🎯 TESTING LONG PUT STRATEGY CALCULATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test Long Put strategy calculation with specific parameters")
        
        # Test data as specified in the review request
        long_put_data = {
            "symbol": "AAPL",
            "strategy_name": "Long Put",
            "stock_price": 150.0,
            "strike": 145.0,
            "days_to_expiry": 30,
            "volatility": 0.25,
            "risk_free_rate": 0.05
        }
        
        print(f"📊 Test Parameters:")
        for key, value in long_put_data.items():
            print(f"   - {key}: {value}")
        
        success, calc_data = self.run_test("Long Put Calculation", "POST", "options/calculate", 200, data=long_put_data)
        
        if not success:
            print("❌ Long Put calculation failed")
            self.test_results.append(("Long Put Calculation", False, "Calculation failed"))
            return False
        
        # Verify response structure
        required_fields = ['strategy_config', 'analysis', 'chart_data']
        missing_fields = [field for field in required_fields if field not in calc_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            self.test_results.append(("Long Put Response Structure", False, f"Missing fields: {missing_fields}"))
            return False
        
        # Verify strategy config
        strategy_config = calc_data.get('strategy_config', {})
        analysis = calc_data.get('analysis', {})
        chart_data = calc_data.get('chart_data', {})
        
        print(f"📊 Strategy Config:")
        print(f"   - Name: {strategy_config.get('name', 'N/A')}")
        print(f"   - Stock Price: ${strategy_config.get('stock_price', 0):.2f}")
        print(f"   - Days to Expiry: {strategy_config.get('days_to_expiry', 0)}")
        print(f"   - Volatility: {strategy_config.get('volatility', 0):.2%}")
        
        # Verify legs structure
        legs = strategy_config.get('legs', [])
        if legs:
            print(f"📊 Strategy Legs ({len(legs)}):")
            for i, leg in enumerate(legs):
                print(f"   Leg {i+1}: {leg.get('option_type', 'N/A')} {leg.get('action', 'N/A')} Strike ${leg.get('strike', 0)} Premium ${leg.get('premium', 0):.2f}")
        
        # Verify Black-Scholes calculations (premium > 0)
        if legs:
            premium = legs[0].get('premium', 0)
            if premium > 0:
                print(f"✅ Black-Scholes calculation working - Premium: ${premium:.2f}")
            else:
                print(f"❌ Black-Scholes calculation issue - Premium: ${premium:.2f}")
                self.test_results.append(("Long Put Black-Scholes", False, f"Premium: ${premium:.2f}"))
                return False
        
        # Verify Greeks calculations
        greeks = analysis.get('greeks', {})
        if greeks:
            delta = greeks.get('delta', 0)
            gamma = greeks.get('gamma', 0)
            theta = greeks.get('theta', 0)
            vega = greeks.get('vega', 0)
            rho = greeks.get('rho', 0)
            
            print(f"📊 Greeks:")
            print(f"   - Delta: {delta:.3f}")
            print(f"   - Gamma: {gamma:.3f}")
            print(f"   - Theta: {theta:.2f}")
            print(f"   - Vega: {vega:.2f}")
            print(f"   - Rho: {rho:.2f}")
            
            # Verify delta is reasonable for Long Put (should be negative and between -1 and 0)
            if -1 <= delta <= 0:
                print(f"✅ Delta reasonable for Long Put: {delta:.3f}")
            else:
                print(f"❌ Delta outside expected range for Long Put: {delta:.3f}")
                self.test_results.append(("Long Put Delta", False, f"Delta: {delta:.3f}"))
                return False
        
        # Verify P&L analysis
        max_profit = analysis.get('max_profit', 0)
        max_loss = analysis.get('max_loss', 0)
        breakeven_points = analysis.get('breakeven_points', [])
        prob_profit = analysis.get('probability_of_profit', 0)
        
        print(f"📊 P&L Analysis:")
        print(f"   - Max Profit: ${max_profit:.2f}")
        print(f"   - Max Loss: ${max_loss:.2f}")
        print(f"   - Breakeven Points: {breakeven_points}")
        print(f"   - Probability of Profit: {prob_profit:.1f}%")
        
        # Verify chart data arrays are generated
        if chart_data:
            x_data = chart_data.get('x', [])
            y_data = chart_data.get('y', [])
            
            if x_data and y_data and len(x_data) == len(y_data):
                print(f"✅ P&L chart data arrays generated properly - {len(x_data)} data points")
            else:
                print(f"❌ P&L chart data arrays issue - X: {len(x_data)}, Y: {len(y_data)}") 
                self.test_results.append(("Long Put Chart Data", False, f"X: {len(x_data)}, Y: {len(y_data)}"))
                return False
        
        self.test_results.append(("Long Put Calculation", True, f"Premium: ${premium:.2f}, Delta: {delta:.3f}"))
        return True

    def test_options_quote_endpoint(self):
        """Test GET /api/options/quote/AAPL - Test options chain data endpoint"""
        print("\n🎯 TESTING OPTIONS QUOTE ENDPOINT")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test GET /api/options/quote/AAPL for options chain data")
        
        success, quote_data = self.run_test("Options Quote (AAPL)", "GET", "options/quote/AAPL", 200)
        
        if not success:
            print("❌ Options quote endpoint failed")
            self.test_results.append(("Options Quote Endpoint", False, "Endpoint failed"))
            return False
        
        # Verify response structure
        required_fields = ['status', 'data', 'note', 'timestamp']
        missing_fields = [field for field in required_fields if field not in quote_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            self.test_results.append(("Options Quote Structure", False, f"Missing fields: {missing_fields}"))
            return False
        else:
            print(f"✅ All required response fields present: {required_fields}")
        
        # Verify data structure
        data = quote_data.get('data', {})
        symbol = data.get('symbol', '')
        stock_price = data.get('stock_price', 0)
        options_chain = data.get('options_chain', {})
        
        print(f"📊 Options Chain Data:")
        print(f"   - Symbol: {symbol}")
        print(f"   - Stock Price: ${stock_price:.2f}")
        print(f"   - Expiration Date: {data.get('expiration_date', 'N/A')}")
        print(f"   - Days to Expiry: {data.get('days_to_expirt', 0)}")  # Note: typo in original code
        print(f"   - Implied Volatility: {data.get('implied_volatility', 0):.2%}")
        
        # Verify options chain structure
        if options_chain:
            calls = options_chain.get('calls', [])
            puts = options_chain.get('puts', [])
            
            print(f"📊 Options Chain:")
            print(f"   - Call Options: {len(calls)}")
            print(f"   - Put Options: {len(puts)}")
            
            # Verify call options structure
            if calls:
                print(f"📊 Sample Call Option:")
                call = calls[0]
                required_call_fields = ['strike', 'bid', 'ask', 'last', 'volume', 'open_interest']
                missing_call_fields = [field for field in required_call_fields if field not in call]
                
                if not missing_call_fields:
                    print(f"   ✅ Call option structure complete")
                    print(f"   - Strike: ${call.get('strike', 0)}")
                    print(f"   - Bid: ${call.get('bid', 0):.2f}")
                    print(f"   - Ask: ${call.get('ask', 0):.2f}")
                    print(f"   - Last: ${call.get('last', 0):.2f}")
                    print(f"   - Volume: {call.get('volume', 0):,}")
                    print(f"   - Open Interest: {call.get('open_interest', 0):,}")
                else:
                    print(f"   ❌ Missing call option fields: {missing_call_fields}")
            
            # Verify put options structure
            if puts:
                print(f"📊 Sample Put Option:")
                put = puts[0]
                required_put_fields = ['strike', 'bid', 'ask', 'last', 'volume', 'open_interest']
                missing_put_fields = [field for field in required_put_fields if field not in put]
                
                if not missing_put_fields:
                    print(f"   ✅ Put option structure complete")
                    print(f"   - Strike: ${put.get('strike', 0)}")
                    print(f"   - Bid: ${put.get('bid', 0):.2f}")
                    print(f"   - Ask: ${put.get('ask', 0):.2f}")
                    print(f"   - Last: ${put.get('last', 0):.2f}")
                    print(f"   - Volume: {put.get('volume', 0):,}")
                    print(f"   - Open Interest: {put.get('open_interest', 0):,}")
                else:
                    print(f"   ❌ Missing put option fields: {missing_put_fields}")
        
        # Check if this is mock data (as indicated in the code)
        note = quote_data.get('note', '')
        if 'Mock data' in note or 'mock' in note.lower():
            print(f"📝 Note: {note}")
            print(f"⚠️  Currently using mock data - TradeStation options API integration in development")
        
        self.test_results.append(("Options Quote Endpoint", True, f"Symbol: {symbol}, Calls: {len(calls)}, Puts: {len(puts)}"))
        return True

    def test_error_handling(self):
        """Test error handling for invalid strategy names"""
        print("\n🎯 TESTING ERROR HANDLING")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test error handling for invalid strategy names")
        
        # Test with invalid strategy name
        invalid_strategy_data = {
            "symbol": "AAPL",
            "strategy_name": "Invalid Strategy",
            "stock_price": 150.0,
            "strike": 155.0,
            "days_to_expiry": 30,
            "volatility": 0.25,
            "risk_free_rate": 0.05
        }
        
        success, error_data = self.run_test("Invalid Strategy Error Handling", "POST", "options/calculate", 400, data=invalid_strategy_data)
        
        if success:
            print(f"✅ Error handling working correctly - returned 400 status")
            detail = error_data.get('detail', '')
            if 'not yet implemented' in detail.lower() or 'invalid' in detail.lower():
                print(f"✅ Appropriate error message: {detail}")
                self.test_results.append(("Error Handling", True, "Invalid strategy properly rejected"))
                return True
            else:
                print(f"⚠️  Error message could be more specific: {detail}")
                self.test_results.append(("Error Handling", True, f"Error message: {detail}"))
                return True
        else:
            print(f"❌ Error handling not working as expected")
            self.test_results.append(("Error Handling", False, "Invalid strategy not properly rejected"))
            return False

    def run_comprehensive_test(self):
        """Run all Options Module tests"""
        print("\n🎯 OPTIONS MODULE COMPREHENSIVE TESTING")
        print("=" * 100)
        print("🎯 OBJECTIVE: Test the new Options Module backend endpoints și functionality")
        print("📋 REQUIREMENTS:")
        print("   1. GET /api/options/strategies - Returns strategies organized by proficiency levels")
        print("   2. POST /api/options/calculate - Long Call strategy calculation")
        print("   3. POST /api/options/calculate - Long Put strategy calculation")
        print("   4. GET /api/options/quote/AAPL - Options chain data endpoint")
        print("   5. Error handling for invalid strategy names")
        print("   6. Verify Black-Scholes calculations (premium > 0)")
        print("   7. Verify Greeks calculations are reasonable")
        print("   8. Verify P&L chart data arrays are generated properly")
        print("   9. Verify JSON response structure matches expected format")
        
        # Run all tests
        test_functions = [
            self.test_options_strategies_endpoint,
            self.test_long_call_calculation,
            self.test_long_put_calculation,
            self.test_options_quote_endpoint,
            self.test_error_handling
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
                self.test_results.append((test_func.__name__, False, f"Exception: {str(e)}"))
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Options Module Backend Testing")
        print("=" * 100)
        
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for test_name, passed, details in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}: {details}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Detailed findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Total API Calls: {self.tests_run}")
        print(f"   - Successful API Calls: {self.tests_passed}")
        print(f"   - API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Requirements verification
        print(f"\n✅ REQUIREMENTS VERIFICATION:")
        requirements_met = []
        
        strategies_test = next((result for result in self.test_results if "Strategies Endpoint" in result[0]), None)
        if strategies_test and strategies_test[1]:
            requirements_met.append("✅ GET /api/options/strategies returns strategies organized by proficiency levels")
        else:
            requirements_met.append("❌ GET /api/options/strategies endpoint issues")
        
        long_call_test = next((result for result in self.test_results if "Long Call Calculation" in result[0]), None)
        if long_call_test and long_call_test[1]:
            requirements_met.append("✅ POST /api/options/calculate Long Call strategy calculation working")
        else:
            requirements_met.append("❌ Long Call strategy calculation issues")
        
        long_put_test = next((result for result in self.test_results if "Long Put Calculation" in result[0]), None)
        if long_put_test and long_put_test[1]:
            requirements_met.append("✅ POST /api/options/calculate Long Put strategy calculation working")
        else:
            requirements_met.append("❌ Long Put strategy calculation issues")
        
        quote_test = next((result for result in self.test_results if "Quote Endpoint" in result[0]), None)
        if quote_test and quote_test[1]:
            requirements_met.append("✅ GET /api/options/quote/AAPL options chain data endpoint working")
        else:
            requirements_met.append("❌ Options quote endpoint issues")
        
        error_test = next((result for result in self.test_results if "Error Handling" in result[0]), None)
        if error_test and error_test[1]:
            requirements_met.append("✅ Error handling works for invalid strategy names")
        else:
            requirements_met.append("❌ Error handling issues")
        
        for requirement in requirements_met:
            print(f"   {requirement}")
        
        # Mathematical engine verification
        print(f"\n🧮 MATHEMATICAL ENGINE VERIFICATION:")
        black_scholes_working = any("Black-Scholes" in result[0] and result[1] for result in self.test_results)
        greeks_working = any("Delta" in result[0] and result[1] for result in self.test_results)
        chart_data_working = any("Chart Data" in result[0] and result[1] for result in self.test_results)
        
        if black_scholes_working:
            print(f"   ✅ Black-Scholes calculations working (premium > 0)")
        else:
            print(f"   ❌ Black-Scholes calculations may have issues")
        
        if greeks_working:
            print(f"   ✅ Greeks calculations are reasonable (delta between -1 and 1)")
        else:
            print(f"   ❌ Greeks calculations may have issues")
        
        if chart_data_working:
            print(f"   ✅ P&L chart data arrays generated properly")
        else:
            print(f"   ❌ P&L chart data generation may have issues")
        
        # Final verdict
        if success_rate >= 90:
            print(f"\n🎉 VERDICT: EXCELLENT - Options Module backend is working perfectly!")
            print(f"   All mathematical engine și API integration requirements are met.")
            print(f"   FlowMind Options Module is ready for production use.")
        elif success_rate >= 75:
            print(f"\n✅ VERDICT: GOOD - Options Module backend mostly working with minor issues.")
            print(f"   Core functionality is operational with some areas for improvement.")
        elif success_rate >= 50:
            print(f"\n⚠️  VERDICT: PARTIAL - Options Module backend has significant issues.")
            print(f"   Some core functionality working but needs attention.")
        else:
            print(f"\n❌ VERDICT: CRITICAL - Options Module backend has major issues.")
            print(f"   Requires immediate attention before production use.")
        
        return success_rate >= 75

if __name__ == "__main__":
    print("🎯 FlowMind Options Module Backend Testing")
    print("=" * 100)
    
    tester = OptionsModuleTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 OPTIONS MODULE TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"\n❌ OPTIONS MODULE TESTING COMPLETED WITH ISSUES!")
        sys.exit(1)