import requests
import sys
from datetime import datetime
import json

class PricingInvestigationTester:
    def __init__(self, base_url="https://tradeoptions-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Expected price ranges for investigation
        self.expected_prices = {
            "CRM": {"min": 280, "max": 290, "name": "Salesforce"},
            "AAPL": {"min": 220, "max": 240, "name": "Apple"},
            "MSFT": {"min": 410, "max": 430, "name": "Microsoft"},
            "NVDA": {"min": 110, "max": 130, "name": "Nvidia"}
        }

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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}, Time: {response.elapsed.total_seconds():.2f}s")
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

    def investigate_pricing_issues(self):
        """Main investigation function for pricing issues"""
        print("\n" + "="*80)
        print("🔍 PRICING INVESTIGATION - COMPREHENSIVE ANALYSIS")
        print("="*80)
        print("🎯 OBJECTIVE: Investigate why prices are not correct in application")
        print("📋 FOCUS SYMBOLS:")
        for symbol, info in self.expected_prices.items():
            print(f"   - {symbol} ({info['name']}): Expected ~${info['min']}-${info['max']}")
        
        print("\n📊 INVESTIGATION PHASES:")
        print("   1. Data Sources Status & Authentication")
        print("   2. Individual Symbol Price Testing")
        print("   3. Data Source Comparison Analysis")
        print("   4. Root Cause Analysis")
        print("   5. Recommendations")
        
        # Phase 1: Data Sources Status
        self.phase_1_data_sources_status()
        
        # Phase 2: Individual Symbol Testing
        self.phase_2_individual_symbol_testing()
        
        # Phase 3: Data Source Comparison
        self.phase_3_data_source_comparison()
        
        # Phase 4: Root Cause Analysis
        self.phase_4_root_cause_analysis()
        
        # Phase 5: Recommendations
        self.phase_5_recommendations()

    def phase_1_data_sources_status(self):
        """Phase 1: Check data sources status and authentication"""
        print("\n" + "="*60)
        print("📊 PHASE 1: DATA SOURCES STATUS & AUTHENTICATION")
        print("="*60)
        
        success, status_data = self.run_test("Data Sources Status", "GET", "data-sources/status", 200)
        
        if not success:
            print("❌ CRITICAL: Cannot check data sources status")
            return
        
        # Analyze data source priority
        data_source_priority = status_data.get('data_source_priority', [])
        current_primary = status_data.get('current_primary_source', 'Unknown')
        
        print(f"\n🎯 CURRENT PRIMARY SOURCE: {current_primary}")
        print(f"📊 AVAILABLE DATA SOURCES: {len(data_source_priority)}")
        
        self.tradestation_authenticated = False
        self.unusual_whales_available = False
        
        for i, source in enumerate(data_source_priority, 1):
            source_name = source.get('source', 'Unknown')
            status = source.get('status', 'Unknown')
            authenticated = source.get('authenticated', False)
            reliability = source.get('reliability', 'Unknown')
            
            print(f"\n   {i}. {source_name}")
            print(f"      Status: {status}")
            print(f"      Authenticated: {authenticated}")
            print(f"      Reliability: {reliability}")
            
            if source_name == "TradeStation API":
                self.tradestation_authenticated = authenticated
                if authenticated:
                    connection_test = source.get('connection_test', {})
                    if connection_test:
                        print(f"      Connection Test: {connection_test.get('status', 'Unknown')}")
                        if 'accounts' in connection_test:
                            print(f"      Accounts Found: {len(connection_test.get('accounts', []))}")
                        if 'environment' in connection_test:
                            print(f"      Environment: {connection_test.get('environment', 'Unknown')}")
            
            elif source_name == "Unusual Whales":
                self.unusual_whales_available = True
        
        # Summary of authentication status
        print(f"\n📋 AUTHENTICATION SUMMARY:")
        print(f"   TradeStation: {'✅ Authenticated' if self.tradestation_authenticated else '❌ Not Authenticated'}")
        print(f"   Unusual Whales: {'✅ Available' if self.unusual_whales_available else '❌ Not Available'}")
        
        if not self.tradestation_authenticated and not self.unusual_whales_available:
            print(f"   🚨 CRITICAL: No data sources are properly configured!")
        elif not self.tradestation_authenticated:
            print(f"   ⚠️  WARNING: Primary source (TradeStation) not authenticated, using fallback")

    def phase_2_individual_symbol_testing(self):
        """Phase 2: Test individual symbols for pricing accuracy"""
        print("\n" + "="*60)
        print("📊 PHASE 2: INDIVIDUAL SYMBOL PRICE TESTING")
        print("="*60)
        
        self.symbol_results = {}
        
        for symbol, expected in self.expected_prices.items():
            print(f"\n🔍 TESTING {symbol} ({expected['name']})")
            print(f"   Expected Range: ${expected['min']}-${expected['max']}")
            print("-" * 40)
            
            symbol_data = {
                'symbol': symbol,
                'expected_min': expected['min'],
                'expected_max': expected['max'],
                'basic_quote': None,
                'enhanced_quote': None,
                'issues': []
            }
            
            # Test 1: Basic Quote
            success, basic_data = self.run_test(f"Basic Quote ({symbol})", "GET", f"stocks/{symbol}", 200)
            if success:
                price = basic_data.get('price', 0)
                data_source = basic_data.get('data_source', 'Unknown')
                timestamp = basic_data.get('timestamp', 'Unknown')
                
                symbol_data['basic_quote'] = {
                    'price': price,
                    'data_source': data_source,
                    'timestamp': timestamp,
                    'full_data': basic_data
                }
                
                print(f"   📊 Basic Quote: ${price:.2f}")
                print(f"   📡 Data Source: {data_source}")
                print(f"   🕒 Timestamp: {timestamp}")
                
                # Check if price is in expected range
                if expected['min'] <= price <= expected['max']:
                    print(f"   ✅ Price is within expected range")
                elif price == 0:
                    print(f"   ❌ CRITICAL: Price is $0.00 - no data retrieved")
                    symbol_data['issues'].append("Zero price - no data")
                elif price < expected['min'] * 0.5:
                    print(f"   ❌ CRITICAL: Price significantly below expected range (${price:.2f} vs ${expected['min']}-${expected['max']})")
                    symbol_data['issues'].append(f"Price too low: ${price:.2f}")
                elif price > expected['max'] * 2:
                    print(f"   ❌ CRITICAL: Price significantly above expected range (${price:.2f} vs ${expected['min']}-${expected['max']})")
                    symbol_data['issues'].append(f"Price too high: ${price:.2f}")
                else:
                    print(f"   ⚠️  Price outside expected range but reasonable (${price:.2f} vs ${expected['min']}-${expected['max']})")
                    symbol_data['issues'].append(f"Price outside expected range: ${price:.2f}")
            else:
                symbol_data['issues'].append("Basic quote API failed")
            
            # Test 2: Enhanced Quote
            success, enhanced_data = self.run_test(f"Enhanced Quote ({symbol})", "GET", f"stocks/{symbol}/enhanced", 200)
            if success:
                price = enhanced_data.get('price', 0)
                data_source = enhanced_data.get('data_source', 'Unknown')
                timestamp = enhanced_data.get('timestamp', 'Unknown')
                
                symbol_data['enhanced_quote'] = {
                    'price': price,
                    'data_source': data_source,
                    'timestamp': timestamp,
                    'full_data': enhanced_data
                }
                
                print(f"   📊 Enhanced Quote: ${price:.2f}")
                print(f"   📡 Data Source: {data_source}")
                print(f"   🕒 Timestamp: {timestamp}")
                
                # Compare with basic quote
                if symbol_data['basic_quote']:
                    basic_price = symbol_data['basic_quote']['price']
                    if abs(price - basic_price) > 0.01:
                        print(f"   ⚠️  Price difference between basic and enhanced: ${abs(price - basic_price):.2f}")
                        symbol_data['issues'].append(f"Price inconsistency: Basic ${basic_price:.2f} vs Enhanced ${price:.2f}")
                    else:
                        print(f"   ✅ Consistent pricing between basic and enhanced quotes")
            else:
                symbol_data['issues'].append("Enhanced quote API failed")
            
            self.symbol_results[symbol] = symbol_data
            
            # Summary for this symbol
            print(f"\n   📋 {symbol} SUMMARY:")
            if symbol_data['issues']:
                print(f"   ❌ Issues Found: {len(symbol_data['issues'])}")
                for issue in symbol_data['issues']:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ No major issues detected")

    def phase_3_data_source_comparison(self):
        """Phase 3: Compare data sources for each symbol"""
        print("\n" + "="*60)
        print("📊 PHASE 3: DATA SOURCE COMPARISON ANALYSIS")
        print("="*60)
        
        self.comparison_results = {}
        
        for symbol in self.expected_prices.keys():
            print(f"\n🔍 DATA SOURCE COMPARISON FOR {symbol}")
            print("-" * 40)
            
            success, comparison_data = self.run_test(f"Data Source Comparison ({symbol})", "GET", f"data-sources/test/{symbol}", 200)
            
            if not success:
                print(f"   ❌ Data source comparison failed for {symbol}")
                self.comparison_results[symbol] = {'error': 'API failed'}
                continue
            
            test_results = comparison_data.get('test_results', {})
            primary_source_used = comparison_data.get('primary_source_used', 'Unknown')
            price_comparison = comparison_data.get('price_comparison', {})
            
            print(f"   🎯 Primary Source Used: {primary_source_used}")
            
            comparison_info = {
                'primary_source': primary_source_used,
                'sources_tested': list(test_results.keys()),
                'price_comparison': price_comparison,
                'source_details': test_results
            }
            
            # Analyze each data source
            for source_name, source_data in test_results.items():
                status = source_data.get('status', 'unknown')
                print(f"\n   📡 {source_name.upper()}:")
                print(f"      Status: {status}")
                
                if status == 'success':
                    price = source_data.get('price', 0)
                    timestamp = source_data.get('timestamp', 'Unknown')
                    print(f"      Price: ${price:.2f}")
                    print(f"      Timestamp: {timestamp}")
                    
                    # Check if price is reasonable
                    expected = self.expected_prices[symbol]
                    if expected['min'] <= price <= expected['max']:
                        print(f"      ✅ Price within expected range")
                    elif price == 0:
                        print(f"      ❌ Zero price returned")
                    else:
                        print(f"      ⚠️  Price outside expected range (${expected['min']}-${expected['max']})")
                
                elif status == 'not_authenticated':
                    print(f"      ⚠️  Not authenticated - expected for TradeStation if not logged in")
                elif status == 'error':
                    message = source_data.get('message', 'Unknown error')
                    print(f"      ❌ Error: {message}")
                else:
                    print(f"      ❓ Unknown status: {status}")
            
            # Price comparison analysis
            if price_comparison:
                ts_price = price_comparison.get('tradestation_price')
                uw_price = price_comparison.get('unusual_whales_price')
                price_diff = price_comparison.get('price_difference')
                
                print(f"\n   💰 PRICE COMPARISON:")
                if ts_price:
                    print(f"      TradeStation: ${ts_price:.2f}")
                if uw_price:
                    print(f"      Unusual Whales: ${uw_price:.2f}")
                if price_diff is not None:
                    print(f"      Difference: ${price_diff:.2f}")
                    
                    if abs(price_diff) > 5:
                        print(f"      ⚠️  Large price difference detected!")
                        comparison_info['large_price_difference'] = True
                    else:
                        print(f"      ✅ Price difference is reasonable")
            
            self.comparison_results[symbol] = comparison_info

    def phase_4_root_cause_analysis(self):
        """Phase 4: Analyze root causes of pricing issues"""
        print("\n" + "="*60)
        print("📊 PHASE 4: ROOT CAUSE ANALYSIS")
        print("="*60)
        
        self.root_causes = []
        
        print(f"\n🔍 ANALYZING PRICING ISSUES ACROSS ALL SYMBOLS")
        print("-" * 50)
        
        # Issue 1: Authentication Problems
        if not self.tradestation_authenticated:
            print(f"\n❌ ISSUE 1: TradeStation Not Authenticated")
            print(f"   Impact: Primary data source unavailable")
            print(f"   Symptoms: Falling back to secondary sources")
            print(f"   Affected: All symbols")
            self.root_causes.append({
                'issue': 'TradeStation Authentication',
                'severity': 'High',
                'impact': 'All symbols',
                'description': 'TradeStation API not authenticated, causing fallback to less reliable sources'
            })
        
        # Issue 2: Data Source Quality
        zero_price_symbols = []
        wrong_range_symbols = []
        inconsistent_symbols = []
        
        for symbol, data in self.symbol_results.items():
            # Check for zero prices
            if data.get('basic_quote', {}).get('price', 0) == 0:
                zero_price_symbols.append(symbol)
            
            # Check for wrong price ranges
            basic_price = data.get('basic_quote', {}).get('price', 0)
            expected = self.expected_prices[symbol]
            if basic_price > 0 and not (expected['min'] <= basic_price <= expected['max']):
                wrong_range_symbols.append(symbol)
            
            # Check for inconsistencies
            if 'Price inconsistency' in str(data.get('issues', [])):
                inconsistent_symbols.append(symbol)
        
        if zero_price_symbols:
            print(f"\n❌ ISSUE 2: Zero Prices Detected")
            print(f"   Affected Symbols: {zero_price_symbols}")
            print(f"   Possible Causes: API failures, authentication issues, symbol not found")
            self.root_causes.append({
                'issue': 'Zero Prices',
                'severity': 'Critical',
                'impact': f'{len(zero_price_symbols)} symbols',
                'description': f'Symbols returning $0.00: {zero_price_symbols}'
            })
        
        if wrong_range_symbols:
            print(f"\n⚠️  ISSUE 3: Prices Outside Expected Ranges")
            print(f"   Affected Symbols: {wrong_range_symbols}")
            print(f"   Possible Causes: Outdated data, wrong market, currency issues, cached data")
            self.root_causes.append({
                'issue': 'Incorrect Price Ranges',
                'severity': 'Medium',
                'impact': f'{len(wrong_range_symbols)} symbols',
                'description': f'Symbols with unexpected prices: {wrong_range_symbols}'
            })
        
        if inconsistent_symbols:
            print(f"\n⚠️  ISSUE 4: Price Inconsistencies")
            print(f"   Affected Symbols: {inconsistent_symbols}")
            print(f"   Possible Causes: Different data sources, timing issues, caching problems")
            self.root_causes.append({
                'issue': 'Price Inconsistencies',
                'severity': 'Medium',
                'impact': f'{len(inconsistent_symbols)} symbols',
                'description': f'Inconsistent prices between endpoints: {inconsistent_symbols}'
            })
        
        # Issue 5: Data Source Reliability
        source_issues = {}
        for symbol, comparison in self.comparison_results.items():
            if 'error' in comparison:
                continue
            
            for source_name, details in comparison.get('source_details', {}).items():
                if details.get('status') != 'success':
                    if source_name not in source_issues:
                        source_issues[source_name] = []
                    source_issues[source_name].append(symbol)
        
        for source, failed_symbols in source_issues.items():
            print(f"\n⚠️  ISSUE 5: {source.upper()} Data Source Problems")
            print(f"   Failed Symbols: {failed_symbols}")
            print(f"   Impact: Reduced data reliability")
            self.root_causes.append({
                'issue': f'{source} Source Failures',
                'severity': 'Medium',
                'impact': f'{len(failed_symbols)} symbols',
                'description': f'{source} failed for: {failed_symbols}'
            })
        
        # Issue 6: Large Price Differences Between Sources
        large_diff_symbols = []
        for symbol, comparison in self.comparison_results.items():
            if comparison.get('large_price_difference'):
                large_diff_symbols.append(symbol)
        
        if large_diff_symbols:
            print(f"\n⚠️  ISSUE 6: Large Price Differences Between Sources")
            print(f"   Affected Symbols: {large_diff_symbols}")
            print(f"   Possible Causes: Different markets, timing, data quality")
            self.root_causes.append({
                'issue': 'Large Price Differences',
                'severity': 'Medium',
                'impact': f'{len(large_diff_symbols)} symbols',
                'description': f'Large differences between data sources: {large_diff_symbols}'
            })
        
        # Summary
        print(f"\n📋 ROOT CAUSE SUMMARY:")
        print(f"   Total Issues Identified: {len(self.root_causes)}")
        critical_issues = [rc for rc in self.root_causes if rc['severity'] == 'Critical']
        high_issues = [rc for rc in self.root_causes if rc['severity'] == 'High']
        medium_issues = [rc for rc in self.root_causes if rc['severity'] == 'Medium']
        
        print(f"   Critical Issues: {len(critical_issues)}")
        print(f"   High Priority Issues: {len(high_issues)}")
        print(f"   Medium Priority Issues: {len(medium_issues)}")

    def phase_5_recommendations(self):
        """Phase 5: Provide recommendations for fixing pricing issues"""
        print("\n" + "="*60)
        print("📊 PHASE 5: RECOMMENDATIONS & NEXT STEPS")
        print("="*60)
        
        print(f"\n🎯 IMMEDIATE ACTIONS REQUIRED:")
        
        # Priority 1: Authentication Issues
        if not self.tradestation_authenticated:
            print(f"\n1. 🔐 FIX TRADESTATION AUTHENTICATION (CRITICAL)")
            print(f"   Problem: Primary data source not authenticated")
            print(f"   Solution: Complete TradeStation OAuth authentication flow")
            print(f"   Steps:")
            print(f"      - Visit /api/auth/tradestation/login")
            print(f"      - Complete OAuth authorization")
            print(f"      - Verify authentication at /api/auth/tradestation/status")
            print(f"   Impact: Will provide most accurate real-time pricing")
        
        # Priority 2: Zero Price Issues
        zero_price_symbols = [s for s, d in self.symbol_results.items() 
                             if d.get('basic_quote', {}).get('price', 0) == 0]
        if zero_price_symbols:
            print(f"\n2. 💰 FIX ZERO PRICE ISSUES (CRITICAL)")
            print(f"   Problem: {len(zero_price_symbols)} symbols returning $0.00")
            print(f"   Affected: {zero_price_symbols}")
            print(f"   Solutions:")
            print(f"      - Check Unusual Whales API key validity")
            print(f"      - Verify symbol mappings in data sources")
            print(f"      - Implement better error handling and fallbacks")
            print(f"      - Add data validation before returning prices")
        
        # Priority 3: Data Source Configuration
        print(f"\n3. 🔧 OPTIMIZE DATA SOURCE CONFIGURATION")
        print(f"   Current Status:")
        print(f"      - TradeStation: {'✅ Authenticated' if self.tradestation_authenticated else '❌ Not Authenticated'}")
        print(f"      - Unusual Whales: {'✅ Available' if self.unusual_whales_available else '❌ Not Available'}")
        print(f"   Recommendations:")
        print(f"      - Ensure Unusual Whales API key is valid and has sufficient quota")
        print(f"      - Implement health checks for all data sources")
        print(f"      - Add monitoring for data source failures")
        
        # Priority 4: Price Validation
        print(f"\n4. ✅ IMPLEMENT PRICE VALIDATION")
        print(f"   Problem: Prices outside expected ranges not caught")
        print(f"   Solutions:")
        print(f"      - Add price range validation for known symbols")
        print(f"      - Implement sanity checks (e.g., price > 0, reasonable ranges)")
        print(f"      - Add alerts for unusual price movements")
        print(f"      - Cache last known good prices as fallback")
        
        # Priority 5: Monitoring and Alerting
        print(f"\n5. 📊 ADD MONITORING AND ALERTING")
        print(f"   Implement:")
        print(f"      - Real-time price accuracy monitoring")
        print(f"      - Data source health dashboards")
        print(f"      - Automated alerts for pricing anomalies")
        print(f"      - Performance metrics for API response times")
        
        print(f"\n🔍 SPECIFIC SYMBOL ISSUES:")
        for symbol, data in self.symbol_results.items():
            if data.get('issues'):
                expected = self.expected_prices[symbol]
                current_price = data.get('basic_quote', {}).get('price', 0)
                print(f"\n   {symbol} ({expected['name']}):")
                print(f"      Expected: ${expected['min']}-${expected['max']}")
                print(f"      Current: ${current_price:.2f}")
                print(f"      Issues: {len(data['issues'])}")
                for issue in data['issues']:
                    print(f"         - {issue}")
        
        print(f"\n📋 TESTING RECOMMENDATIONS:")
        print(f"   1. Re-run this test after TradeStation authentication")
        print(f"   2. Monitor prices during market hours for real-time accuracy")
        print(f"   3. Test with additional symbols to verify fixes")
        print(f"   4. Implement automated price accuracy testing")
        
        print(f"\n🎯 SUCCESS CRITERIA:")
        print(f"   ✅ All symbols return non-zero prices")
        print(f"   ✅ Prices within expected ranges (±10% tolerance)")
        print(f"   ✅ Consistent prices across different endpoints")
        print(f"   ✅ TradeStation authenticated and working")
        print(f"   ✅ Fast response times (<2 seconds)")

    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*80)
        print("📋 PRICING INVESTIGATION SUMMARY REPORT")
        print("="*80)
        
        print(f"\n🔍 INVESTIGATION OVERVIEW:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"   Symbols Tested: {len(self.expected_prices)}")
        print(f"   Issues Identified: {len(self.root_causes)}")
        
        print(f"\n💰 PRICE ACCURACY RESULTS:")
        accurate_count = 0
        for symbol, data in self.symbol_results.items():
            expected = self.expected_prices[symbol]
            current_price = data.get('basic_quote', {}).get('price', 0)
            
            if expected['min'] <= current_price <= expected['max']:
                status = "✅ ACCURATE"
                accurate_count += 1
            elif current_price == 0:
                status = "❌ NO DATA"
            else:
                status = "⚠️  INACCURATE"
            
            print(f"   {symbol}: ${current_price:.2f} (Expected: ${expected['min']}-${expected['max']}) {status}")
        
        print(f"\n📊 ACCURACY SUMMARY:")
        print(f"   Accurate Prices: {accurate_count}/{len(self.expected_prices)} ({accurate_count/len(self.expected_prices)*100:.1f}%)")
        
        print(f"\n🚨 CRITICAL ISSUES:")
        critical_issues = [rc for rc in self.root_causes if rc['severity'] == 'Critical']
        if critical_issues:
            for issue in critical_issues:
                print(f"   - {issue['issue']}: {issue['description']}")
        else:
            print(f"   No critical issues identified")
        
        print(f"\n⚠️  HIGH PRIORITY ISSUES:")
        high_issues = [rc for rc in self.root_causes if rc['severity'] == 'High']
        if high_issues:
            for issue in high_issues:
                print(f"   - {issue['issue']}: {issue['description']}")
        else:
            print(f"   No high priority issues identified")
        
        print(f"\n🔧 NEXT STEPS:")
        if not self.tradestation_authenticated:
            print(f"   1. URGENT: Authenticate TradeStation API for accurate pricing")
        if accurate_count < len(self.expected_prices):
            print(f"   2. Fix pricing issues for {len(self.expected_prices) - accurate_count} symbols")
        print(f"   3. Implement price validation and monitoring")
        print(f"   4. Re-test after fixes are applied")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': self.tests_passed/self.tests_run*100,
            'accurate_prices': accurate_count,
            'total_symbols': len(self.expected_prices),
            'critical_issues': len(critical_issues),
            'high_issues': len(high_issues),
            'root_causes': self.root_causes
        }

def main():
    """Main function to run the pricing investigation"""
    print("🔍 Starting Pricing Investigation...")
    
    tester = PricingInvestigationTester()
    
    # Run the comprehensive investigation
    tester.investigate_pricing_issues()
    
    # Generate summary report
    summary = tester.generate_summary_report()
    
    print(f"\n🎯 INVESTIGATION COMPLETE")
    print(f"   Overall Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Price Accuracy: {summary['accurate_prices']}/{summary['total_symbols']} symbols")
    
    if summary['critical_issues'] > 0 or summary['accurate_prices'] < summary['total_symbols']:
        print(f"   🚨 ACTION REQUIRED: Critical pricing issues detected")
        return False
    else:
        print(f"   ✅ All pricing appears to be working correctly")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)