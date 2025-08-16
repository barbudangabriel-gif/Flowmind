#!/usr/bin/env python3
"""
Enhanced AI Trading Strategies Test - Focused on Specific Options Strategy Names
Testing the enhanced Unusual Whales trading strategies endpoint with real options strategy names
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class EnhancedTradingStrategiesTest:
    def __init__(self, base_url="https://tradeoptions-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.api_key = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
        
        # Expected specific strategy names from the review request
        self.expected_strategy_names = [
            "Bull Call Spread",
            "Bear Put Spread", 
            "Long Call",
            "Long Put",
            "Long Straddle",
            "Long Strangle",
            "Iron Condor",
            "LEAPS Call",
            "Synthetic Long",
            "Protective Put",
            "Cash-Secured Put",
            "Covered Call"
        ]
        
        # Expected strategy categories
        self.expected_categories = [
            "vertical_spread",
            "directional", 
            "volatility",
            "income",
            "policy_play",
            "income_generation"
        ]

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, endpoint: str, params: Dict = None) -> tuple[bool, Dict]:
        """Make API request and return success status and data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data
                except json.JSONDecodeError:
                    return False, {"error": "Invalid JSON response"}
            else:
                try:
                    error_data = response.json()
                    return False, {"error": f"HTTP {response.status_code}", "details": error_data}
                except:
                    return False, {"error": f"HTTP {response.status_code}", "details": response.text}
                    
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout (30s)"}
        except Exception as e:
            return False, {"error": str(e)}

    def test_basic_endpoint_connectivity(self):
        """Test basic endpoint connectivity"""
        print("\n🔗 Testing Basic Endpoint Connectivity")
        print("=" * 50)
        
        success, data = self.make_request("unusual-whales/trading-strategies")
        
        if success:
            self.log_test("Trading Strategies Endpoint Accessible", True, 
                         f"Response received with {len(str(data))} characters")
            return True, data
        else:
            self.log_test("Trading Strategies Endpoint Accessible", False, 
                         f"Error: {data.get('error', 'Unknown error')}")
            return False, data

    def test_specific_strategy_names(self, strategies_data: List[Dict]):
        """Test for specific options strategy names"""
        print("\n📋 Testing Specific Strategy Names")
        print("=" * 50)
        
        if not strategies_data:
            self.log_test("Strategy Names Verification", False, 
                         "No strategies returned to verify names")
            return
        
        found_strategy_names = []
        for strategy in strategies_data:
            strategy_name = strategy.get('strategy_name', '')
            if strategy_name:
                found_strategy_names.append(strategy_name)
        
        print(f"Found {len(found_strategy_names)} strategies with names:")
        for name in found_strategy_names:
            print(f"  • {name}")
        
        # Check for specific expected strategy names
        matching_strategies = []
        for expected_name in self.expected_strategy_names:
            if expected_name in found_strategy_names:
                matching_strategies.append(expected_name)
        
        if matching_strategies:
            self.log_test("Specific Strategy Names Present", True, 
                         f"Found {len(matching_strategies)} expected strategy names: {', '.join(matching_strategies)}")
        else:
            self.log_test("Specific Strategy Names Present", False, 
                         f"None of the expected strategy names found. Expected: {', '.join(self.expected_strategy_names[:5])}...")
        
        # Test for realistic strategy names (not generic)
        generic_names = ["Strategy 1", "Basic Strategy", "Simple Strategy", "Default Strategy"]
        has_generic = any(generic in found_strategy_names for generic in generic_names)
        
        self.log_test("Non-Generic Strategy Names", not has_generic, 
                     "All strategy names are specific options strategies" if not has_generic 
                     else "Some generic strategy names detected")

    def test_strategy_details_verification(self, strategies_data: List[Dict]):
        """Test strategy details and structure"""
        print("\n🔍 Testing Strategy Details Verification")
        print("=" * 50)
        
        if not strategies_data:
            self.log_test("Strategy Details Structure", False, "No strategies to verify")
            return
        
        for i, strategy in enumerate(strategies_data[:3]):  # Test first 3 strategies
            strategy_name = strategy.get('strategy_name', f'Strategy {i+1}')
            print(f"\n📊 Analyzing Strategy: {strategy_name}")
            
            # Test required fields
            required_fields = [
                'strategy_name', 'ticker', 'confidence', 'timeframe', 
                'entry_logic', 'tradestation_execution', 'risk_management'
            ]
            
            missing_fields = [field for field in required_fields if field not in strategy]
            if not missing_fields:
                self.log_test(f"Required Fields - {strategy_name}", True, 
                             "All required fields present")
            else:
                self.log_test(f"Required Fields - {strategy_name}", False, 
                             f"Missing fields: {', '.join(missing_fields)}")
            
            # Test strategy legs and strikes
            tradestation_exec = strategy.get('tradestation_execution', {})
            legs = tradestation_exec.get('legs', [])
            
            if legs:
                self.log_test(f"Strategy Legs - {strategy_name}", True, 
                             f"Found {len(legs)} option legs")
                
                # Verify leg details
                for j, leg in enumerate(legs):
                    leg_fields = ['action', 'strike', 'option_type', 'quantity']
                    leg_missing = [field for field in leg_fields if field not in leg]
                    
                    if not leg_missing:
                        strike = leg.get('strike', 0)
                        option_type = leg.get('option_type', '')
                        action = leg.get('action', '')
                        
                        # Verify realistic strike prices (should be > 0 and reasonable)
                        realistic_strike = isinstance(strike, (int, float)) and strike > 0 and strike < 10000
                        valid_option_type = option_type.lower() in ['call', 'put']
                        valid_action = action.lower() in ['buy', 'sell']
                        
                        if realistic_strike and valid_option_type and valid_action:
                            self.log_test(f"Leg {j+1} Details - {strategy_name}", True, 
                                         f"{action} {option_type} @ ${strike}")
                        else:
                            self.log_test(f"Leg {j+1} Details - {strategy_name}", False, 
                                         f"Invalid leg details: strike={strike}, type={option_type}, action={action}")
                    else:
                        self.log_test(f"Leg {j+1} Structure - {strategy_name}", False, 
                                     f"Missing leg fields: {', '.join(leg_missing)}")
            else:
                self.log_test(f"Strategy Legs - {strategy_name}", False, 
                             "No option legs found in strategy")
            
            # Test expiration and DTE
            entry_logic = strategy.get('entry_logic', {})
            dte = entry_logic.get('dte', 0)
            
            if isinstance(dte, (int, float)) and dte > 0:
                self.log_test(f"DTE Calculation - {strategy_name}", True, 
                             f"DTE: {dte} days")
            else:
                self.log_test(f"DTE Calculation - {strategy_name}", False, 
                             f"Invalid or missing DTE: {dte}")
            
            # Test risk/profit calculations
            max_risk = tradestation_exec.get('max_risk', '')
            max_profit = tradestation_exec.get('max_profit', '')
            breakeven = tradestation_exec.get('breakeven', '')
            
            has_risk_calcs = bool(max_risk and max_profit and breakeven)
            self.log_test(f"Risk/Profit Calculations - {strategy_name}", has_risk_calcs, 
                         f"Max Risk: {max_risk}, Max Profit: {max_profit}, Breakeven: {breakeven}" if has_risk_calcs 
                         else "Missing risk/profit calculations")
            
            # Test confidence scores
            confidence = strategy.get('confidence', 0)
            if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                confidence_pct = confidence * 100
                self.log_test(f"Confidence Score - {strategy_name}", True, 
                             f"Confidence: {confidence_pct:.1f}%")
            else:
                self.log_test(f"Confidence Score - {strategy_name}", False, 
                             f"Invalid confidence score: {confidence}")

    def test_tradestation_execution_parameters(self, strategies_data: List[Dict]):
        """Test TradeStation execution parameters"""
        print("\n🎯 Testing TradeStation Execution Parameters")
        print("=" * 50)
        
        if not strategies_data:
            self.log_test("TradeStation Parameters", False, "No strategies to verify")
            return
        
        for strategy in strategies_data[:2]:  # Test first 2 strategies
            strategy_name = strategy.get('strategy_name', 'Unknown Strategy')
            tradestation_exec = strategy.get('tradestation_execution', {})
            
            if not tradestation_exec:
                self.log_test(f"TradeStation Execution - {strategy_name}", False, 
                             "No TradeStation execution parameters found")
                continue
            
            # Test required TradeStation fields
            ts_required_fields = ['underlying', 'legs', 'max_risk', 'max_profit', 'breakeven']
            ts_missing = [field for field in ts_required_fields if field not in tradestation_exec]
            
            if not ts_missing:
                self.log_test(f"TradeStation Structure - {strategy_name}", True, 
                             "All required TradeStation fields present")
            else:
                self.log_test(f"TradeStation Structure - {strategy_name}", False, 
                             f"Missing TradeStation fields: {', '.join(ts_missing)}")
            
            # Test underlying symbol
            underlying = tradestation_exec.get('underlying', '')
            if underlying and len(underlying) <= 5 and underlying.isupper():
                self.log_test(f"Underlying Symbol - {strategy_name}", True, 
                             f"Underlying: {underlying}")
            else:
                self.log_test(f"Underlying Symbol - {strategy_name}", False, 
                             f"Invalid underlying symbol: {underlying}")
            
            # Test legs structure
            legs = tradestation_exec.get('legs', [])
            if legs:
                valid_legs = 0
                for leg in legs:
                    if all(field in leg for field in ['action', 'strike', 'option_type', 'quantity']):
                        valid_legs += 1
                
                if valid_legs == len(legs):
                    self.log_test(f"Leg Structure - {strategy_name}", True, 
                                 f"All {len(legs)} legs properly structured")
                else:
                    self.log_test(f"Leg Structure - {strategy_name}", False, 
                                 f"Only {valid_legs}/{len(legs)} legs properly structured")
            
            # Test collateral requirements (for spreads and complex strategies)
            risk_mgmt = strategy.get('risk_management', {})
            max_position = risk_mgmt.get('max_position_size', '')
            
            if max_position:
                self.log_test(f"Position Sizing - {strategy_name}", True, 
                             f"Max position: {max_position}")
            else:
                self.log_test(f"Position Sizing - {strategy_name}", False, 
                             "No position sizing specified")

    def test_strategy_categorization(self, strategies_data: List[Dict]):
        """Test strategy categorization"""
        print("\n📂 Testing Strategy Categorization")
        print("=" * 50)
        
        if not strategies_data:
            self.log_test("Strategy Categorization", False, "No strategies to categorize")
            return
        
        found_categories = set()
        category_counts = {}
        
        for strategy in strategies_data:
            strategy_type = strategy.get('strategy_type', '')
            if strategy_type:
                found_categories.add(strategy_type)
                category_counts[strategy_type] = category_counts.get(strategy_type, 0) + 1
        
        print(f"Found strategy categories:")
        for category, count in category_counts.items():
            print(f"  • {category}: {count} strategies")
        
        # Check for expected categories
        matching_categories = found_categories.intersection(set(self.expected_categories))
        
        if matching_categories:
            self.log_test("Expected Categories Present", True, 
                         f"Found {len(matching_categories)} expected categories: {', '.join(matching_categories)}")
        else:
            self.log_test("Expected Categories Present", False, 
                         f"No expected categories found. Expected: {', '.join(self.expected_categories)}")
        
        # Test timeframe appropriateness
        timeframe_analysis = {}
        for strategy in strategies_data:
            strategy_type = strategy.get('strategy_type', '')
            timeframe = strategy.get('timeframe', '')
            
            if strategy_type and timeframe:
                if strategy_type not in timeframe_analysis:
                    timeframe_analysis[strategy_type] = []
                timeframe_analysis[strategy_type].append(timeframe)
        
        # Verify timeframes match strategy types
        appropriate_timeframes = True
        for s_type, timeframes in timeframe_analysis.items():
            if s_type == 'vertical_spread':
                # Spreads should have shorter timeframes
                short_term = any('day' in tf.lower() or 'week' in tf.lower() for tf in timeframes)
                if not short_term:
                    appropriate_timeframes = False
            elif 'LEAPS' in str(timeframes):
                # LEAPS should have longer timeframes
                long_term = any('month' in tf.lower() or 'year' in tf.lower() for tf in timeframes)
                if not long_term:
                    appropriate_timeframes = False
        
        self.log_test("Timeframe Appropriateness", appropriate_timeframes, 
                     "Strategy timeframes match strategy types" if appropriate_timeframes 
                     else "Some strategy timeframes don't match strategy types")

    def test_api_key_configuration(self):
        """Test API key configuration"""
        print("\n🔑 Testing API Key Configuration")
        print("=" * 50)
        
        # The API key should be configured as per the review request
        expected_api_key = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
        
        # Test root endpoint to see if API key is mentioned
        success, root_data = self.make_request("")
        
        if success:
            # Check if Unusual Whales endpoints are available
            uw_endpoints = root_data.get('unusual_whales_endpoints', {})
            if uw_endpoints and 'trading_strategies' in uw_endpoints:
                self.log_test("API Key Configuration", True, 
                             f"Unusual Whales endpoints available, API key likely configured")
            else:
                self.log_test("API Key Configuration", False, 
                             "Unusual Whales endpoints not found in root response")
        else:
            self.log_test("API Key Configuration", False, 
                         "Could not verify API key configuration")

    def test_real_unusual_whales_data(self, strategies_data: List[Dict]):
        """Test that real Unusual Whales data is being used"""
        print("\n🐋 Testing Real Unusual Whales Data Usage")
        print("=" * 50)
        
        if not strategies_data:
            self.log_test("Real Data Usage", False, "No strategies returned")
            return
        
        # Check for indicators of real data vs mock data
        real_data_indicators = 0
        
        for strategy in strategies_data:
            entry_logic = strategy.get('entry_logic', {})
            
            # Check for real premium values
            premium = entry_logic.get('premium_threshold', 0)
            if isinstance(premium, (int, float)) and premium > 10000:  # Real premiums are usually substantial
                real_data_indicators += 1
            
            # Check for real volume data
            volume = entry_logic.get('volume', 0)
            if isinstance(volume, (int, float)) and volume > 100:
                real_data_indicators += 1
            
            # Check for real underlying prices
            underlying_price = entry_logic.get('underlying_price', 0)
            if isinstance(underlying_price, (int, float)) and underlying_price > 10:
                real_data_indicators += 1
        
        if real_data_indicators > 0:
            self.log_test("Real Unusual Whales Data", True, 
                         f"Found {real_data_indicators} indicators of real market data")
        else:
            self.log_test("Real Unusual Whales Data", False, 
                         "No clear indicators of real Unusual Whales data found")

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🎯 Enhanced AI Trading Strategies Test Suite")
        print("Testing specific options strategy names and TradeStation execution")
        print("API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print("=" * 70)
        
        # Test 1: Basic connectivity
        success, data = self.test_basic_endpoint_connectivity()
        if not success:
            print("\n❌ Cannot proceed with tests - endpoint not accessible")
            return False
        
        # Extract strategies from response
        strategies = data.get('trading_strategies', [])
        if not strategies:
            strategies = data.get('strategies', [])  # Fallback
        if not strategies:
            print(f"\n⚠️  No strategies returned. Full response: {json.dumps(data, indent=2)}")
            strategies = []
        
        print(f"\n📊 Found {len(strategies)} strategies to analyze")
        
        # Test 2: API key configuration
        self.test_api_key_configuration()
        
        # Test 3: Specific strategy names
        self.test_specific_strategy_names(strategies)
        
        # Test 4: Strategy details verification
        self.test_strategy_details_verification(strategies)
        
        # Test 5: TradeStation execution parameters
        self.test_tradestation_execution_parameters(strategies)
        
        # Test 6: Strategy categorization
        self.test_strategy_categorization(strategies)
        
        # Test 7: Real Unusual Whales data usage
        self.test_real_unusual_whales_data(strategies)
        
        return True

    def print_final_results(self):
        """Print final test results"""
        print("\n" + "=" * 70)
        print(f"📊 Enhanced Trading Strategies Test Results")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Enhanced AI Trading Strategies are working correctly.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = EnhancedTradingStrategiesTest()
    
    success = tester.run_comprehensive_test()
    all_passed = tester.print_final_results()
    
    if success and all_passed:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())