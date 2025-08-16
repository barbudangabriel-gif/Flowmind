#!/usr/bin/env python3
"""
Market Overview Unusual Whales ETF Data Integration Test
========================================================

This test specifically validates the optimized Market Overview endpoint to verify:
1. Live Unusual Whales Data: ETF data (SPY, QQQ, DIA, IWM) from Unusual Whales API
2. Data Source Verification: "Unusual Whales API (Live ETF Data)" as data source
3. Coverage Analysis: "unusual_whales_coverage" field showing ETF coverage
4. Enhanced Fields: unusual_activity and options_flow_signal populated
5. Fallback Behavior: Proper fallback to yfinance with clear source indication
6. Performance: Response times with optimized ETF data fetching
7. Real Price Validation: Current and realistic ETF prices
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

class MarketOverviewUnusualWhalesTest:
    def __init__(self, base_url="https://stockai-platform-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Expected ETF data for validation
        self.expected_etfs = ['SPY', 'QQQ', 'DIA', 'IWM']
        self.expected_futures_symbols = ['SPX', 'NQ', 'YM', 'RTY']
        self.etf_price_ranges = {
            'SPY': (600, 700),    # SPDR S&P 500 ETF typical range
            'QQQ': (550, 650),    # Invesco QQQ Trust typical range
            'DIA': (400, 500),    # SPDR Dow Jones Industrial Average ETF typical range
            'IWM': (200, 250)     # iShares Russell 2000 ETF typical range
        }
        
    def log_test(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ FAIL"
            
        self.test_results['test_details'].append({
            'test_name': test_name,
            'status': status,
            'passed': passed,
            'details': details,
            'response_time': response_time
        })
        
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    Response Time: {response_time:.3f}s")
    
    def make_api_request(self, endpoint: str, method: str = "GET", params: Dict = None) -> Tuple[bool, Dict, float]:
        """Make API request and return success, data, response_time"""
        url = f"{self.api_url}/{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            else:
                response = requests.post(url, json=params, timeout=30)
                
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, response_time
                except json.JSONDecodeError:
                    return False, {"error": "Invalid JSON response"}, response_time
            else:
                return False, {"error": f"HTTP {response.status_code}", "text": response.text}, response_time
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return False, {"error": "Request timeout (30s)"}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return False, {"error": str(e)}, response_time
    
    def test_market_overview_basic_functionality(self) -> bool:
        """Test 1: Basic Market Overview endpoint functionality"""
        print("\n🔍 TEST 1: Basic Market Overview Endpoint Functionality")
        print("-" * 60)
        
        success, data, response_time = self.make_api_request("market/overview")
        
        if not success:
            self.log_test("Market Overview Basic Request", False, 
                         f"API request failed: {data.get('error', 'Unknown error')}", response_time)
            return False
        
        # Check basic response structure
        required_fields = ['indices', 'data_source', 'note', 'last_updated']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            self.log_test("Market Overview Response Structure", False,
                         f"Missing required fields: {missing_fields}", response_time)
            return False
        
        self.log_test("Market Overview Basic Request", True,
                     f"Successfully retrieved market overview with {len(data.get('indices', []))} indices", response_time)
        return True
    
    def test_unusual_whales_etf_data_integration(self) -> Tuple[bool, Dict]:
        """Test 2: Unusual Whales ETF Data Integration"""
        print("\n🐋 TEST 2: Unusual Whales ETF Data Integration")
        print("-" * 60)
        
        success, data, response_time = self.make_api_request("market/overview")
        
        if not success:
            self.log_test("Unusual Whales ETF Data Request", False,
                         f"API request failed: {data.get('error', 'Unknown error')}", response_time)
            return False, {}
        
        indices = data.get('indices', [])
        data_source = data.get('data_source', '')
        
        # Test 2.1: Verify ETF symbols are used as underlying symbols
        underlying_symbols = [index.get('underlying_symbol', '') for index in indices]
        etf_symbols_found = [symbol for symbol in underlying_symbols if symbol in self.expected_etfs]
        
        etf_integration_success = len(etf_symbols_found) >= 3  # At least 3 out of 4 ETFs
        
        self.log_test("ETF Underlying Symbols", etf_integration_success,
                     f"Found {len(etf_symbols_found)}/4 expected ETF symbols: {etf_symbols_found}", response_time)
        
        # Test 2.2: Verify futures-style display symbols
        display_symbols = [index.get('symbol', '') for index in indices]
        futures_symbols_found = [symbol for symbol in display_symbols if symbol in self.expected_futures_symbols]
        
        futures_display_success = len(futures_symbols_found) >= 3
        
        self.log_test("Futures Display Symbols", futures_display_success,
                     f"Found {len(futures_symbols_found)}/4 expected futures symbols: {futures_symbols_found}")
        
        return etf_integration_success and futures_display_success, data
    
    def test_unusual_whales_data_source_verification(self, market_data: Dict) -> bool:
        """Test 3: Data Source Verification"""
        print("\n📊 TEST 3: Data Source Verification")
        print("-" * 60)
        
        data_source = market_data.get('data_source', '')
        note = market_data.get('note', '')
        unusual_whales_coverage = market_data.get('unusual_whales_coverage', '')
        
        # Test 3.1: Check if data source indicates Unusual Whales usage
        uw_data_source = "Unusual Whales" in data_source
        
        self.log_test("Unusual Whales Data Source", uw_data_source,
                     f"Data source: {data_source}")
        
        # Test 3.2: Check for coverage analysis field
        coverage_present = bool(unusual_whales_coverage)
        
        self.log_test("Coverage Analysis Field", coverage_present,
                     f"Coverage field: {unusual_whales_coverage}")
        
        # Test 3.3: Verify note contains relevant information
        note_relevant = any(keyword in note.lower() for keyword in ['etf', 'unusual whales', 'live data', 'api'])
        
        self.log_test("Relevant Note Information", note_relevant,
                     f"Note: {note[:100]}...")
        
        return uw_data_source and coverage_present and note_relevant
    
    def test_enhanced_fields_population(self, market_data: Dict) -> bool:
        """Test 4: Enhanced Fields Population"""
        print("\n🔥 TEST 4: Enhanced Fields Population")
        print("-" * 60)
        
        indices = market_data.get('indices', [])
        enhanced_fields_results = {
            'indices_with_unusual_activity': 0,
            'indices_with_options_flow_signal': 0,
            'total_indices': len(indices)
        }
        
        for index in indices:
            symbol = index.get('symbol', 'N/A')
            unusual_activity = index.get('unusual_activity')
            options_flow_signal = index.get('options_flow_signal')
            
            print(f"    {symbol}: unusual_activity={unusual_activity}, options_flow_signal={options_flow_signal}")
            
            if unusual_activity is not None:
                enhanced_fields_results['indices_with_unusual_activity'] += 1
            
            if options_flow_signal is not None:
                enhanced_fields_results['indices_with_options_flow_signal'] += 1
        
        # Test success if at least 75% of indices have enhanced fields
        unusual_activity_success = enhanced_fields_results['indices_with_unusual_activity'] >= (len(indices) * 0.75)
        options_flow_success = enhanced_fields_results['indices_with_options_flow_signal'] >= (len(indices) * 0.75)
        
        self.log_test("Unusual Activity Fields", unusual_activity_success,
                     f"{enhanced_fields_results['indices_with_unusual_activity']}/{len(indices)} indices have unusual_activity field")
        
        self.log_test("Options Flow Signal Fields", options_flow_success,
                     f"{enhanced_fields_results['indices_with_options_flow_signal']}/{len(indices)} indices have options_flow_signal field")
        
        return unusual_activity_success and options_flow_success
    
    def test_real_price_validation(self, market_data: Dict) -> bool:
        """Test 5: Real Price Validation"""
        print("\n💰 TEST 5: Real Price Validation")
        print("-" * 60)
        
        indices = market_data.get('indices', [])
        price_validation_results = {
            'realistic_prices': 0,
            'zero_prices': 0,
            'out_of_range_prices': 0,
            'total_indices': len(indices)
        }
        
        for index in indices:
            symbol = index.get('symbol', 'N/A')
            underlying_symbol = index.get('underlying_symbol', 'N/A')
            price = index.get('price', 0)
            change = index.get('change', 0)
            change_percent = index.get('change_percent', 0)
            
            print(f"    {symbol} (via {underlying_symbol}): ${price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")
            
            if price == 0:
                price_validation_results['zero_prices'] += 1
                continue
            
            # Check if price is within realistic range for the underlying ETF
            if underlying_symbol in self.etf_price_ranges:
                min_price, max_price = self.etf_price_ranges[underlying_symbol]
                if min_price <= price <= max_price:
                    price_validation_results['realistic_prices'] += 1
                    print(f"      ✅ Price realistic for {underlying_symbol}: ${price:.2f} (range: ${min_price}-${max_price})")
                else:
                    price_validation_results['out_of_range_prices'] += 1
                    print(f"      ⚠️  Price outside expected range for {underlying_symbol}: ${price:.2f} (expected: ${min_price}-${max_price})")
            else:
                # For non-ETF underlying symbols, just check if price is reasonable (> 0 and < 10000)
                if 0 < price < 10000:
                    price_validation_results['realistic_prices'] += 1
                else:
                    price_validation_results['out_of_range_prices'] += 1
        
        # Test success if at least 75% of prices are realistic
        realistic_price_success = price_validation_results['realistic_prices'] >= (len(indices) * 0.75)
        no_zero_prices = price_validation_results['zero_prices'] == 0
        
        self.log_test("Realistic Price Validation", realistic_price_success,
                     f"{price_validation_results['realistic_prices']}/{len(indices)} indices have realistic prices")
        
        self.log_test("No Zero Prices", no_zero_prices,
                     f"{price_validation_results['zero_prices']} indices have zero prices")
        
        return realistic_price_success and no_zero_prices
    
    def test_performance_metrics(self) -> bool:
        """Test 6: Performance Metrics"""
        print("\n⚡ TEST 6: Performance Metrics")
        print("-" * 60)
        
        # Test multiple requests to get average response time
        response_times = []
        successful_requests = 0
        
        for i in range(3):
            success, data, response_time = self.make_api_request("market/overview")
            if success:
                response_times.append(response_time)
                successful_requests += 1
            print(f"    Request {i+1}: {'✅' if success else '❌'} {response_time:.3f}s")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance criteria: average < 5s, max < 10s
            avg_performance_good = avg_response_time < 5.0
            max_performance_acceptable = max_response_time < 10.0
            
            self.log_test("Average Response Time", avg_performance_good,
                         f"Average: {avg_response_time:.3f}s (target: <5s)")
            
            self.log_test("Maximum Response Time", max_performance_acceptable,
                         f"Max: {max_response_time:.3f}s, Min: {min_response_time:.3f}s (max target: <10s)")
            
            return avg_performance_good and max_performance_acceptable
        else:
            self.log_test("Performance Test", False, "No successful requests for performance testing")
            return False
    
    def test_fallback_behavior_analysis(self, market_data: Dict) -> bool:
        """Test 7: Fallback Behavior Analysis"""
        print("\n🛡️  TEST 7: Fallback Behavior Analysis")
        print("-" * 60)
        
        data_source = market_data.get('data_source', '')
        note = market_data.get('note', '')
        indices = market_data.get('indices', [])
        
        # Analyze data sources used
        individual_sources = []
        for index in indices:
            index_source = index.get('data_source', 'Unknown')
            individual_sources.append(index_source)
        
        # Count different data sources
        from collections import Counter
        source_counts = Counter(individual_sources)
        
        print(f"    Overall Data Source: {data_source}")
        print(f"    Individual Index Sources:")
        for source, count in source_counts.items():
            print(f"      - {source}: {count} indices")
        
        # Test fallback behavior
        has_unusual_whales = any("Unusual Whales" in source for source in individual_sources)
        has_fallback = any("Yahoo Finance" in source or "Mock Data" in source for source in individual_sources)
        
        if has_unusual_whales and has_fallback:
            fallback_behavior = "Mixed sources (partial Unusual Whales with fallback)"
            fallback_success = True
        elif has_unusual_whales and not has_fallback:
            fallback_behavior = "Full Unusual Whales coverage"
            fallback_success = True
        elif not has_unusual_whales and has_fallback:
            fallback_behavior = "Full fallback mode (no Unusual Whales data)"
            fallback_success = True
        else:
            fallback_behavior = "Unknown data source configuration"
            fallback_success = False
        
        # Verify that futures symbols are maintained even in fallback
        display_symbols = [index.get('symbol', '') for index in indices]
        futures_maintained = all(symbol in self.expected_futures_symbols for symbol in display_symbols)
        
        self.log_test("Fallback Data Source Analysis", fallback_success,
                     f"Behavior: {fallback_behavior}")
        
        self.log_test("Futures Symbols Maintained in Fallback", futures_maintained,
                     f"Display symbols: {display_symbols}")
        
        return fallback_success and futures_maintained
    
    def run_comprehensive_test(self) -> Dict:
        """Run all tests and return comprehensive results"""
        print("🐋 MARKET OVERVIEW UNUSUAL WHALES ETF DATA INTEGRATION TEST")
        print("=" * 80)
        print("Testing optimized Market Overview endpoint with live ETF data from Unusual Whales API")
        print(f"Target URL: {self.api_url}/market/overview")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run all tests
        test_1_success = self.test_market_overview_basic_functionality()
        
        if test_1_success:
            test_2_success, market_data = self.test_unusual_whales_etf_data_integration()
            
            if test_2_success and market_data:
                test_3_success = self.test_unusual_whales_data_source_verification(market_data)
                test_4_success = self.test_enhanced_fields_population(market_data)
                test_5_success = self.test_real_price_validation(market_data)
                test_6_success = self.test_performance_metrics()
                test_7_success = self.test_fallback_behavior_analysis(market_data)
            else:
                # If ETF integration failed, still run basic tests
                test_3_success = test_4_success = test_5_success = test_6_success = test_7_success = False
        else:
            test_2_success = test_3_success = test_4_success = test_5_success = test_6_success = test_7_success = False
            market_data = {}
        
        # Calculate overall results
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for test_detail in self.test_results['test_details']:
            print(f"{test_detail['status']} {test_detail['test_name']}")
            if test_detail['details']:
                print(f"    {test_detail['details']}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.test_results['total_tests']}")
        print(f"   Passed: {self.test_results['passed_tests']}")
        print(f"   Failed: {self.test_results['failed_tests']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Determine overall verdict
        if success_rate >= 90:
            verdict = "🎉 EXCELLENT - Market Overview with Unusual Whales ETF data is working perfectly!"
            verdict_details = "All requirements met. Live ETF data integration successful."
        elif success_rate >= 75:
            verdict = "✅ GOOD - Market Overview mostly working with minor issues"
            verdict_details = "Most requirements met. Some minor issues detected."
        elif success_rate >= 50:
            verdict = "⚠️  PARTIAL - Market Overview working but significant issues detected"
            verdict_details = "Basic functionality works but ETF integration has problems."
        else:
            verdict = "❌ CRITICAL - Market Overview has major issues"
            verdict_details = "Significant problems detected. Requires immediate attention."
        
        print(f"\n🏆 FINAL VERDICT: {verdict}")
        print(f"   {verdict_details}")
        
        # Specific requirement verification
        print(f"\n✅ REQUIREMENT VERIFICATION:")
        requirements_met = []
        
        if any("ETF Underlying Symbols" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Live Unusual Whales Data: ETF data (SPY, QQQ, DIA, IWM) successfully fetched")
        else:
            requirements_met.append("❌ Live Unusual Whales Data: ETF data integration failed")
        
        if any("Unusual Whales Data Source" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Data Source Verification: Shows 'Unusual Whales API (Live ETF Data)'")
        else:
            requirements_met.append("❌ Data Source Verification: Does not show Unusual Whales as source")
        
        if any("Coverage Analysis Field" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Coverage Analysis: 'unusual_whales_coverage' field present")
        else:
            requirements_met.append("❌ Coverage Analysis: Coverage field missing")
        
        if any("Enhanced Fields" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Enhanced Fields: unusual_activity and options_flow_signal populated")
        else:
            requirements_met.append("❌ Enhanced Fields: Enhanced fields not properly populated")
        
        if any("Fallback" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Fallback Behavior: Proper fallback with clear source indication")
        else:
            requirements_met.append("❌ Fallback Behavior: Fallback behavior issues detected")
        
        if any("Performance" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Performance: Response times acceptable with optimized fetching")
        else:
            requirements_met.append("❌ Performance: Response time issues detected")
        
        if any("Price Validation" in test['test_name'] and test['passed'] for test in self.test_results['test_details']):
            requirements_met.append("✅ Real Price Validation: Current and realistic ETF prices confirmed")
        else:
            requirements_met.append("❌ Real Price Validation: Price validation failed")
        
        for requirement in requirements_met:
            print(f"   {requirement}")
        
        return {
            'success_rate': success_rate,
            'verdict': verdict,
            'verdict_details': verdict_details,
            'requirements_met': requirements_met,
            'test_results': self.test_results,
            'market_data': market_data
        }

def main():
    """Main test execution"""
    tester = MarketOverviewUnusualWhalesTest()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on success rate
    if results['success_rate'] >= 75:
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    main()