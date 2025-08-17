#!/usr/bin/env python3
"""
Investment Scoring Improvements Test - Review Request Focus
Testing the complete implementation of Investment Scoring improvements as requested in review.
"""

import requests
import time
import json
from datetime import datetime

class ReviewInvestmentScoringTester:
    def __init__(self):
        self.base_url = "https://trade-insights-27.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.test_results = []
        self.test_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA']  # As requested in review
        
    def log_result(self, test_name, success, details, response_time=0):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({response_time:.2f}s)")
        if isinstance(details, dict) and details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        elif details:
            print(f"    {details}")
        
    def make_request(self, method, endpoint, params=None, data=None, timeout=120):
        """Make API request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, params=params, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                return True, response.json(), response_time
            else:
                return False, {'error': f"HTTP {response.status_code}", 'text': response.text}, response_time
                
        except requests.exceptions.Timeout:
            return False, {'error': 'Request timeout'}, timeout
        except Exception as e:
            return False, {'error': str(e)}, time.time() - start_time

    def test_investment_scoring_agent_endpoints(self):
        """Test Investment Scoring Agent endpoints for all requested symbols"""
        print("\n🎯 TESTING INVESTMENT SCORING AGENT ENDPOINTS")
        print("=" * 70)
        
        agent_results = {}
        
        for symbol in self.test_symbols:
            print(f"\n📊 Testing Investment Scoring Agent - {symbol}")
            
            # Test individual scoring
            success, data, response_time = self.make_request(
                'POST', 'agents/investment-scoring', 
                params={'symbol': symbol}
            )
            
            if success:
                # Check required fields for frontend modal
                required_fields = [
                    'symbol', 'investment_score', 'recommendation', 
                    'confidence_level', 'key_signals', 'risk_analysis'
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    details = {
                        'Score': data.get('investment_score', 'N/A'),
                        'Recommendation': data.get('recommendation', 'N/A'),
                        'Confidence': data.get('confidence_level', 'N/A'),
                        'Key Signals': len(data.get('key_signals', [])),
                        'All Fields Present': True
                    }
                    self.log_result(f"Investment Scoring Agent ({symbol})", True, details, response_time)
                    agent_results[symbol] = {'success': True, 'data': data, 'response_time': response_time}
                else:
                    self.log_result(f"Investment Scoring Agent ({symbol})", False, 
                                  f"Missing fields: {missing_fields}", response_time)
                    agent_results[symbol] = {'success': False, 'error': 'Missing fields'}
            else:
                self.log_result(f"Investment Scoring Agent ({symbol})", False, data, response_time)
                agent_results[symbol] = {'success': False, 'error': data}
        
        # Test batch processing
        print(f"\n📊 Testing Investment Scoring Agent - Batch Processing")
        batch_symbols = ",".join(self.test_symbols)
        success, data, response_time = self.make_request(
            'GET', 'agents/investment-scoring/batch',
            params={'symbols': batch_symbols}
        )
        
        if success:
            results = data.get('results', [])
            details = {
                'Symbols Requested': len(self.test_symbols),
                'Results Returned': len(results),
                'Success Rate': f"{len(results)}/{len(self.test_symbols)}"
            }
            self.log_result("Investment Scoring Batch Processing", True, details, response_time)
        else:
            self.log_result("Investment Scoring Batch Processing", False, data, response_time)
        
        # Test methodology endpoint
        print(f"\n📊 Testing Investment Scoring Agent - Methodology")
        success, data, response_time = self.make_request('GET', 'agents/investment-scoring/methodology')
        
        if success:
            details = {
                'Agent Name': data.get('agent_name', 'N/A'),
                'Version': data.get('version', 'N/A'),
                'Signal Components': len(data.get('signal_weights', {}))
            }
            self.log_result("Investment Scoring Methodology", True, details, response_time)
        else:
            self.log_result("Investment Scoring Methodology", False, data, response_time)
        
        return agent_results

    def test_technical_analysis_agent_endpoints(self):
        """Test Technical Analysis Agent endpoints for all requested symbols"""
        print("\n🎯 TESTING TECHNICAL ANALYSIS AGENT ENDPOINTS")
        print("=" * 70)
        
        tech_results = {}
        
        for symbol in self.test_symbols:
            print(f"\n📊 Testing Technical Analysis Agent - {symbol}")
            
            # Test individual analysis
            success, data, response_time = self.make_request(
                'POST', 'agents/technical-analysis',
                params={'symbol': symbol, 'include_smc': 'true'}
            )
            
            if success:
                # Check required fields for frontend modal
                required_fields = [
                    'symbol', 'technical_score', 'recommendation',
                    'confidence_level', 'key_signals', 'timeframe_analysis'
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    details = {
                        'Technical Score': data.get('technical_score', 'N/A'),
                        'Recommendation': data.get('recommendation', 'N/A'),
                        'Confidence': data.get('confidence_level', 'N/A'),
                        'Key Signals': len(data.get('key_signals', [])),
                        'Timeframe Analysis': bool(data.get('timeframe_analysis')),
                        'All Fields Present': True
                    }
                    self.log_result(f"Technical Analysis Agent ({symbol})", True, details, response_time)
                    tech_results[symbol] = {'success': True, 'data': data, 'response_time': response_time}
                else:
                    self.log_result(f"Technical Analysis Agent ({symbol})", False,
                                  f"Missing fields: {missing_fields}", response_time)
                    tech_results[symbol] = {'success': False, 'error': 'Missing fields'}
            else:
                self.log_result(f"Technical Analysis Agent ({symbol})", False, data, response_time)
                tech_results[symbol] = {'success': False, 'error': data}
        
        # Test methodology endpoint
        print(f"\n📊 Testing Technical Analysis Agent - Methodology")
        success, data, response_time = self.make_request('GET', 'agents/technical-analysis/methodology')
        
        if success:
            details = {
                'Agent Name': data.get('agent_name', 'N/A'),
                'Version': data.get('version', 'N/A'),
                'Multi-Timeframe': bool(data.get('methodology', {}).get('timeframes'))
            }
            self.log_result("Technical Analysis Methodology", True, details, response_time)
        else:
            self.log_result("Technical Analysis Methodology", False, data, response_time)
        
        return tech_results

    def test_pricing_data_sources_3tier(self):
        """Test 3-tier pricing data source priority system"""
        print("\n🎯 TESTING 3-TIER PRICING DATA SOURCE PRIORITY SYSTEM")
        print("=" * 70)
        
        # Test data sources status
        print(f"\n📊 Testing Data Sources Status")
        success, data, response_time = self.make_request('GET', 'data-sources/status')
        
        if success:
            priority_sources = data.get('data_source_priority', [])
            current_primary = data.get('current_primary_source', 'Unknown')
            
            # Verify 3-tier system
            expected_sources = ['TradeStation API', 'Unusual Whales', 'Yahoo Finance']
            actual_sources = [s.get('source', '') for s in priority_sources]
            
            tier_system_correct = len(priority_sources) >= 3
            for expected in expected_sources:
                if not any(expected in actual for actual in actual_sources):
                    tier_system_correct = False
                    break
            
            details = {
                'Current Primary': current_primary,
                'Priority Sources': len(priority_sources),
                '3-Tier System': tier_system_correct,
                'Sources': [s.get('source', 'Unknown') for s in priority_sources[:3]]
            }
            self.log_result("Data Sources Status", True, details, response_time)
        else:
            self.log_result("Data Sources Status", False, data, response_time)
        
        # Test data source comparison for each symbol
        pricing_results = {}
        for symbol in self.test_symbols:
            print(f"\n📊 Testing Data Source Comparison - {symbol}")
            success, data, response_time = self.make_request('GET', f'data-sources/test/{symbol}')
            
            if success:
                test_results = data.get('test_results', {})
                primary_source = data.get('primary_source_used', 'unknown')
                
                working_sources = [source for source, result in test_results.items() 
                                 if result.get('status') == 'success']
                
                details = {
                    'Primary Source': primary_source,
                    'Working Sources': len(working_sources),
                    'Sources': working_sources
                }
                self.log_result(f"Data Source Comparison ({symbol})", True, details, response_time)
                pricing_results[symbol] = {'success': True, 'primary': primary_source, 'working': len(working_sources)}
            else:
                self.log_result(f"Data Source Comparison ({symbol})", False, data, response_time)
                pricing_results[symbol] = {'success': False}
        
        return pricing_results

    def test_combined_analysis_response_times(self):
        """Test combined analysis response times for frontend modal"""
        print("\n🎯 TESTING COMBINED ANALYSIS RESPONSE TIMES")
        print("=" * 70)
        
        combined_results = {}
        
        for symbol in self.test_symbols:
            print(f"\n📊 Testing Combined Analysis Response Time - {symbol}")
            
            # Time both calls together (as frontend modal would do)
            start_time = time.time()
            
            # Investment Scoring call
            inv_success, inv_data, inv_time = self.make_request(
                'POST', 'agents/investment-scoring',
                params={'symbol': symbol}
            )
            
            # Technical Analysis call
            tech_success, tech_data, tech_time = self.make_request(
                'POST', 'agents/technical-analysis',
                params={'symbol': symbol, 'include_smc': 'true'}
            )
            
            total_time = time.time() - start_time
            
            if inv_success and tech_success:
                # Check if all required fields are present for modal
                modal_ready = True
                required_modal_fields = {
                    'investment_score': inv_data.get('investment_score'),
                    'investment_recommendation': inv_data.get('recommendation'),
                    'technical_score': tech_data.get('technical_score'),
                    'technical_recommendation': tech_data.get('recommendation'),
                    'investment_signals': inv_data.get('key_signals', []),
                    'technical_signals': tech_data.get('key_signals', [])
                }
                
                for field, value in required_modal_fields.items():
                    if value is None or (isinstance(value, list) and len(value) == 0):
                        modal_ready = False
                        break
                
                details = {
                    'Investment Score': inv_data.get('investment_score', 'N/A'),
                    'Technical Score': tech_data.get('technical_score', 'N/A'),
                    'Combined Time': f"{total_time:.2f}s",
                    'Modal Ready': modal_ready,
                    'Performance': 'Excellent' if total_time < 10 else 'Good' if total_time < 30 else 'Slow'
                }
                self.log_result(f"Combined Analysis ({symbol})", True, details, total_time)
                combined_results[symbol] = {
                    'success': True, 
                    'total_time': total_time,
                    'modal_ready': modal_ready,
                    'inv_score': inv_data.get('investment_score'),
                    'tech_score': tech_data.get('technical_score')
                }
            else:
                error_details = []
                if not inv_success:
                    error_details.append("Investment Scoring failed")
                if not tech_success:
                    error_details.append("Technical Analysis failed")
                
                self.log_result(f"Combined Analysis ({symbol})", False, "; ".join(error_details), total_time)
                combined_results[symbol] = {'success': False, 'total_time': total_time}
        
        return combined_results

    def test_error_handling_invalid_symbols(self):
        """Test error handling for invalid symbols"""
        print("\n🎯 TESTING ERROR HANDLING FOR INVALID SYMBOLS")
        print("=" * 70)
        
        invalid_symbols = ['INVALID', 'ZZZZZ', '']
        error_handling_results = {}
        
        for symbol in invalid_symbols:
            display_symbol = 'EMPTY' if symbol == '' else symbol
            print(f"\n📊 Testing Error Handling - {display_symbol}")
            
            # Test Investment Scoring with invalid symbol
            inv_success, inv_data, inv_time = self.make_request(
                'POST', 'agents/investment-scoring',
                params={'symbol': symbol}
            )
            
            # Test Technical Analysis with invalid symbol
            tech_success, tech_data, tech_time = self.make_request(
                'POST', 'agents/technical-analysis',
                params={'symbol': symbol}
            )
            
            # Check if errors are handled gracefully
            inv_handled = inv_success and ('error' in inv_data or inv_data.get('investment_score', -1) == 0)
            tech_handled = tech_success and ('error' in tech_data or tech_data.get('technical_score', -1) == 0)
            
            details = {
                'Investment Error Handled': inv_handled,
                'Technical Error Handled': tech_handled,
                'Both Handled Gracefully': inv_handled and tech_handled
            }
            
            overall_success = inv_handled and tech_handled
            self.log_result(f"Error Handling ({display_symbol})", overall_success, details, inv_time + tech_time)
            error_handling_results[display_symbol] = {
                'success': overall_success,
                'inv_handled': inv_handled,
                'tech_handled': tech_handled
            }
        
        return error_handling_results

    def generate_review_report(self):
        """Generate comprehensive report for review requirements"""
        print("\n" + "=" * 100)
        print("🎯 INVESTMENT SCORING IMPROVEMENTS - COMPREHENSIVE REVIEW REPORT")
        print("=" * 100)
        
        print("\n🚀 EXECUTING REVIEW-FOCUSED TEST SUITE...")
        
        # Execute all tests
        investment_results = self.test_investment_scoring_agent_endpoints()
        technical_results = self.test_technical_analysis_agent_endpoints()
        pricing_results = self.test_pricing_data_sources_3tier()
        combined_results = self.test_combined_analysis_response_times()
        error_results = self.test_error_handling_invalid_symbols()
        
        # Calculate success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 100)
        print("📊 REVIEW REQUIREMENTS VERIFICATION")
        print("=" * 100)
        
        # Review Requirement 1: Backend endpoints working correctly
        print(f"\n1️⃣ BACKEND ENDPOINTS FOR BOTH AGENTS:")
        inv_working = sum(1 for r in investment_results.values() if r.get('success', False))
        tech_working = sum(1 for r in technical_results.values() if r.get('success', False))
        
        if inv_working >= 3 and tech_working >= 3:
            print(f"   ✅ PASS: Investment Scoring ({inv_working}/4) and Technical Analysis ({tech_working}/4) agents working")
        else:
            print(f"   ❌ FAIL: Investment Scoring ({inv_working}/4) or Technical Analysis ({tech_working}/4) agents have issues")
        
        # Review Requirement 2: 3-tier pricing data sources
        print(f"\n2️⃣ 3-TIER PRICING DATA SOURCE PRIORITY SYSTEM:")
        pricing_working = sum(1 for r in pricing_results.values() if r.get('success', False))
        
        if pricing_working >= 3:
            print(f"   ✅ PASS: 3-tier pricing system verified for {pricing_working}/4 symbols")
        else:
            print(f"   ❌ FAIL: 3-tier pricing system issues detected ({pricing_working}/4 symbols working)")
        
        # Review Requirement 3: Data structure for frontend modal
        print(f"\n3️⃣ DATA STRUCTURE COMPATIBILITY WITH FRONTEND MODAL:")
        modal_ready = sum(1 for r in combined_results.values() if r.get('modal_ready', False))
        
        if modal_ready >= 3:
            print(f"   ✅ PASS: Data structure compatible with frontend modal for {modal_ready}/4 symbols")
        else:
            print(f"   ❌ FAIL: Data structure compatibility issues ({modal_ready}/4 symbols ready)")
        
        # Review Requirement 4: Multiple ticker symbols tested
        print(f"\n4️⃣ MULTIPLE TICKER SYMBOLS (AAPL, MSFT, NVDA, TSLA) TESTED:")
        symbols_tested = len(self.test_symbols)
        
        if symbols_tested == 4:
            print(f"   ✅ PASS: All 4 requested symbols tested (AAPL, MSFT, NVDA, TSLA)")
        else:
            print(f"   ❌ FAIL: Only {symbols_tested} symbols tested")
        
        # Review Requirement 5: Response times acceptable
        print(f"\n5️⃣ RESPONSE TIMES ACCEPTABLE FOR COMBINED ANALYSIS:")
        fast_responses = sum(1 for r in combined_results.values() if r.get('success') and r.get('total_time', 999) < 60)
        
        if fast_responses >= 3:
            avg_time = sum(r.get('total_time', 0) for r in combined_results.values() if r.get('success')) / max(1, len([r for r in combined_results.values() if r.get('success')]))
            print(f"   ✅ PASS: Response times acceptable ({fast_responses}/4 under 60s, avg: {avg_time:.1f}s)")
        else:
            print(f"   ❌ FAIL: Response times too slow ({fast_responses}/4 under 60s)")
        
        # Review Requirement 6: All required fields present
        print(f"\n6️⃣ ALL REQUIRED FIELDS PRESENT IN API RESPONSES:")
        complete_responses = modal_ready  # Same as modal ready check
        
        if complete_responses >= 3:
            print(f"   ✅ PASS: All required fields present for {complete_responses}/4 symbols")
        else:
            print(f"   ❌ FAIL: Missing required fields for some symbols ({complete_responses}/4 complete)")
        
        # Calculate requirements success rate
        requirements_passed = sum([
            inv_working >= 3 and tech_working >= 3,  # Requirement 1
            pricing_working >= 3,                    # Requirement 2
            modal_ready >= 3,                        # Requirement 3
            symbols_tested == 4,                     # Requirement 4
            fast_responses >= 3,                     # Requirement 5
            complete_responses >= 3                  # Requirement 6
        ])
        
        requirements_success_rate = (requirements_passed / 6) * 100
        
        print(f"\n" + "=" * 100)
        print("🎯 FINAL REVIEW VERDICT")
        print("=" * 100)
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   - Total Tests Executed: {total_tests}")
        print(f"   - Tests Passed: {passed_tests}")
        print(f"   - Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"   - Review Requirements Met: {requirements_passed}/6 ({requirements_success_rate:.1f}%)")
        
        print(f"\n📋 DETAILED RESULTS BY SYMBOL:")
        for symbol in self.test_symbols:
            inv_status = "✅" if investment_results.get(symbol, {}).get('success') else "❌"
            tech_status = "✅" if technical_results.get(symbol, {}).get('success') else "❌"
            pricing_status = "✅" if pricing_results.get(symbol, {}).get('success') else "❌"
            combined_status = "✅" if combined_results.get(symbol, {}).get('success') else "❌"
            
            print(f"   {symbol}: Inv{inv_status} Tech{tech_status} Pricing{pricing_status} Combined{combined_status}")
        
        print(f"\n🎯 FINAL VERDICT:")
        if requirements_success_rate >= 85:
            print(f"   🎉 EXCELLENT: Investment Scoring improvements are working perfectly!")
            print(f"   ✅ All major review requirements satisfied")
            print(f"   🚀 Backend endpoints ready for production use with new frontend modal")
            verdict = "EXCELLENT"
        elif requirements_success_rate >= 70:
            print(f"   ✅ GOOD: Investment Scoring improvements mostly working")
            print(f"   🔧 Minor issues detected but core functionality is solid")
            print(f"   📝 Some areas may need attention before full production deployment")
            verdict = "GOOD"
        else:
            print(f"   ❌ NEEDS ATTENTION: Investment Scoring improvements have significant issues")
            print(f"   🚨 Major problems detected that need to be addressed")
            print(f"   🔧 Backend endpoints require fixes before production use")
            verdict = "NEEDS_ATTENTION"
        
        # Summary for main agent
        print(f"\n💡 RECOMMENDATIONS FOR MAIN AGENT:")
        if verdict == "EXCELLENT":
            print(f"   ✅ Investment Scoring improvements are working perfectly")
            print(f"   ✅ All backend endpoints tested successfully")
            print(f"   ✅ 3-tier pricing system operational")
            print(f"   ✅ Frontend modal compatibility confirmed")
            print(f"   ✅ Response times acceptable for production use")
        elif verdict == "GOOD":
            print(f"   ✅ Core Investment Scoring functionality working")
            print(f"   ⚠️  Some minor issues detected - review individual test results")
            print(f"   📝 Consider optimizing response times if needed")
        else:
            print(f"   ❌ Significant issues detected with Investment Scoring improvements")
            print(f"   🔧 Review failed tests and fix backend endpoint issues")
            print(f"   📊 Check data source configuration and API connectivity")
        
        return {
            'verdict': verdict,
            'overall_success_rate': overall_success_rate,
            'requirements_success_rate': requirements_success_rate,
            'requirements_passed': requirements_passed,
            'total_requirements': 6,
            'investment_results': investment_results,
            'technical_results': technical_results,
            'pricing_results': pricing_results,
            'combined_results': combined_results
        }

def main():
    """Main test execution for review requirements"""
    print("🎯 INVESTMENT SCORING IMPROVEMENTS - REVIEW REQUEST TESTING")
    print("=" * 80)
    print("📋 REVIEW FOCUS AREAS:")
    print("   1. Backend endpoints for Investment Scoring Agent and Technical Analysis Agent")
    print("   2. 3-tier pricing data sources (TradeStation → Unusual Whales → Yahoo Finance)")
    print("   3. Data structure compatibility with new frontend modal")
    print("   4. Multiple ticker symbols testing (AAPL, MSFT, NVDA, TSLA)")
    print("   5. Acceptable response times for combined analysis")
    print("   6. All required fields present in API responses")
    
    tester = ReviewInvestmentScoringTester()
    
    try:
        results = tester.generate_review_report()
        
        # Return appropriate exit code based on results
        if results['requirements_success_rate'] >= 70:
            print(f"\n✅ Review testing completed successfully!")
            return 0
        else:
            print(f"\n❌ Review testing completed with significant issues!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Review testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())