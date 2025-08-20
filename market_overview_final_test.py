import requests
import sys
import time
from datetime import datetime
import json

class MarketOverviewFinalTester:
    def __init__(self, base_url="https://tradestation-sync-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} - Response Time: {response_time:.3f}s")
                try:
                    response_data = response.json()
                    return True, response_data, response_time
                except:
                    return True, {}, response_time
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}, response_time

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}, 30.0
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}, 0.0

    def test_market_overview_final_messaging(self):
        """Test the final Market Overview endpoint with improved messaging - COMPREHENSIVE FINAL TEST"""
        print("\n" + "="*100)
        print("🎯 FINAL MARKET OVERVIEW ENDPOINT TEST - IMPROVED MESSAGING VERIFICATION")
        print("="*100)
        print("📋 TESTING REQUIREMENTS:")
        print("   1. Live ETF Data Status - Check response indicates live ETF data even with yfinance fallback")
        print("   2. Improved Messaging - Verify data_source and note fields show user-friendly messages")
        print("   3. New Status Fields - Test 'live_data_status' field shows appropriate status")
        print("   4. Accurate Coverage - Confirm unusual_whales_coverage shows correct ETF coverage")
        print("   5. ETF Price Quality - Verify all 4 ETFs (SPY, QQQ, DIA, IWM) show realistic live prices")
        print("   6. Response Performance - Check response times are good with optimized approach")
        print("="*100)
        
        # Execute the test
        success, overview_data, response_time = self.run_test(
            "Market Overview - Final Messaging Test", 
            "GET", 
            "market/overview", 
            200
        )
        
        if not success:
            print("❌ CRITICAL FAILURE: Market Overview endpoint failed")
            return False
        
        # Initialize test results tracking
        test_results = {
            'live_etf_data_status': False,
            'improved_messaging': False,
            'new_status_fields': False,
            'accurate_coverage': False,
            'etf_price_quality': False,
            'response_performance': False
        }
        
        detailed_results = {}
        
        # REQUIREMENT 1: Live ETF Data Status
        print(f"\n📊 REQUIREMENT 1: Live ETF Data Status Verification")
        print("-" * 80)
        
        indices = overview_data.get('indices', [])
        data_source = overview_data.get('data_source', '')
        note = overview_data.get('note', '')
        
        print(f"   📈 Found {len(indices)} market indices")
        print(f"   🔗 Primary Data Source: {data_source}")
        print(f"   📝 Note Message: {note}")
        
        # Check if response correctly indicates live ETF data
        live_data_indicators = [
            'live etf data' in note.lower(),
            'etf data' in note.lower(),
            'live' in data_source.lower() or 'real-time' in data_source.lower(),
            any('etf' in idx.get('name', '').lower() for idx in indices)
        ]
        
        live_data_count = sum(live_data_indicators)
        if live_data_count >= 2:
            test_results['live_etf_data_status'] = True
            print(f"   ✅ PASS: Response correctly indicates live ETF data ({live_data_count}/4 indicators)")
        else:
            print(f"   ❌ FAIL: Response doesn't clearly indicate live ETF data ({live_data_count}/4 indicators)")
        
        detailed_results['live_data_indicators'] = {
            'note_mentions_live_etf': 'live etf data' in note.lower(),
            'note_mentions_etf': 'etf data' in note.lower(),
            'data_source_indicates_live': 'live' in data_source.lower() or 'real-time' in data_source.lower(),
            'indices_show_etf_names': any('etf' in idx.get('name', '').lower() for idx in indices)
        }
        
        # REQUIREMENT 2: Improved Messaging
        print(f"\n💬 REQUIREMENT 2: Improved Messaging Verification")
        print("-" * 80)
        
        # Check for user-friendly messaging
        user_friendly_keywords = [
            'live', 'real-time', 'etf', 'trading', 'market data', 
            'futures', 'tradeable', 'alternatives', 'liquid'
        ]
        
        note_keywords_found = [kw for kw in user_friendly_keywords if kw.lower() in note.lower()]
        source_keywords_found = [kw for kw in user_friendly_keywords if kw.lower() in data_source.lower()]
        
        print(f"   📝 Note Keywords Found: {note_keywords_found}")
        print(f"   🔗 Data Source Keywords Found: {source_keywords_found}")
        
        total_keywords = len(note_keywords_found) + len(source_keywords_found)
        if total_keywords >= 3:
            test_results['improved_messaging'] = True
            print(f"   ✅ PASS: Improved user-friendly messaging detected ({total_keywords} relevant keywords)")
        else:
            print(f"   ❌ FAIL: Messaging could be more user-friendly ({total_keywords} relevant keywords)")
        
        detailed_results['messaging_analysis'] = {
            'note_keywords': note_keywords_found,
            'source_keywords': source_keywords_found,
            'total_keywords': total_keywords,
            'note_length': len(note),
            'source_length': len(data_source)
        }
        
        # REQUIREMENT 3: New Status Fields
        print(f"\n🆕 REQUIREMENT 3: New Status Fields Verification")
        print("-" * 80)
        
        # Check for new status fields
        new_fields = {
            'live_data_status': overview_data.get('live_data_status'),
            'unusual_whales_coverage': overview_data.get('unusual_whales_coverage'),
            'data_source': overview_data.get('data_source'),
            'note': overview_data.get('note')
        }
        
        print(f"   🔍 New Fields Found:")
        for field_name, field_value in new_fields.items():
            if field_value is not None:
                print(f"     ✅ {field_name}: {field_value}")
            else:
                print(f"     ❌ {field_name}: Missing")
        
        # Check specifically for live_data_status field
        live_data_status = overview_data.get('live_data_status')
        if live_data_status:
            test_results['new_status_fields'] = True
            print(f"   ✅ PASS: 'live_data_status' field present: {live_data_status}")
        else:
            print(f"   ❌ FAIL: 'live_data_status' field missing")
        
        detailed_results['new_fields'] = new_fields
        
        # REQUIREMENT 4: Accurate Coverage
        print(f"\n📊 REQUIREMENT 4: Accurate Coverage Verification")
        print("-" * 80)
        
        unusual_whales_coverage = overview_data.get('unusual_whales_coverage')
        print(f"   🐋 Unusual Whales Coverage: {unusual_whales_coverage}")
        
        # Parse coverage (expected format: "X/4 ETFs")
        if unusual_whales_coverage:
            if '/4' in str(unusual_whales_coverage):
                test_results['accurate_coverage'] = True
                print(f"   ✅ PASS: Coverage shows correct ETF count format: {unusual_whales_coverage}")
                
                # Extract the number
                try:
                    coverage_num = int(str(unusual_whales_coverage).split('/')[0])
                    print(f"   📈 Coverage Analysis: {coverage_num}/4 ETFs covered by Unusual Whales")
                    if coverage_num == 0:
                        print(f"   💡 INFO: Currently using fallback data (expected when UW API unavailable)")
                    elif coverage_num > 0:
                        print(f"   🎉 INFO: Partial Unusual Whales coverage active")
                except:
                    print(f"   ⚠️  WARNING: Could not parse coverage number")
            else:
                print(f"   ❌ FAIL: Coverage format unexpected: {unusual_whales_coverage}")
        else:
            print(f"   ❌ FAIL: unusual_whales_coverage field missing")
        
        detailed_results['coverage_analysis'] = {
            'coverage_field': unusual_whales_coverage,
            'expected_format': 'X/4 ETFs',
            'format_correct': '/4' in str(unusual_whales_coverage) if unusual_whales_coverage else False
        }
        
        # REQUIREMENT 5: ETF Price Quality
        print(f"\n💰 REQUIREMENT 5: ETF Price Quality Verification")
        print("-" * 80)
        
        expected_etfs = ['SPY', 'QQQ', 'DIA', 'IWM']
        expected_futures_display = ['SPX', 'NQ', 'YM', 'RTY']
        
        etf_price_analysis = {
            'total_indices': len(indices),
            'realistic_prices': 0,
            'zero_prices': 0,
            'etf_symbols_found': [],
            'futures_symbols_found': [],
            'price_ranges_valid': 0
        }
        
        # Expected price ranges for validation
        price_ranges = {
            'SPX': (600, 700),    # SPY ETF range
            'NQ': (500, 650),     # QQQ ETF range  
            'YM': (400, 500),     # DIA ETF range
            'RTY': (200, 250)     # IWM ETF range
        }
        
        print(f"   📊 Analyzing {len(indices)} indices for ETF price quality:")
        
        for i, index in enumerate(indices):
            symbol = index.get('symbol', 'N/A')
            underlying_symbol = index.get('underlying_symbol', 'N/A')
            price = index.get('price', 0)
            name = index.get('name', 'N/A')
            
            print(f"\n     📈 Index {i+1}: {symbol}")
            print(f"       - Display Symbol: {symbol}")
            print(f"       - Underlying Symbol: {underlying_symbol}")
            print(f"       - Price: ${price:.2f}")
            print(f"       - Name: {name}")
            
            # Track ETF symbols found
            if underlying_symbol in expected_etfs:
                etf_price_analysis['etf_symbols_found'].append(underlying_symbol)
            
            # Track futures display symbols
            if symbol in expected_futures_display:
                etf_price_analysis['futures_symbols_found'].append(symbol)
            
            # Validate price realism
            if price > 0:
                etf_price_analysis['realistic_prices'] += 1
                print(f"       ✅ Price is realistic (not zero)")
                
                # Check if price is in expected range
                if symbol in price_ranges:
                    min_price, max_price = price_ranges[symbol]
                    if min_price <= price <= max_price:
                        etf_price_analysis['price_ranges_valid'] += 1
                        print(f"       ✅ Price in expected range: ${min_price}-${max_price}")
                    else:
                        print(f"       ⚠️  Price outside expected range: ${min_price}-${max_price}")
            else:
                etf_price_analysis['zero_prices'] += 1
                print(f"       ❌ Price is zero or invalid")
        
        # Evaluate ETF price quality
        if (etf_price_analysis['realistic_prices'] == 4 and 
            etf_price_analysis['zero_prices'] == 0 and
            len(etf_price_analysis['etf_symbols_found']) >= 3):
            test_results['etf_price_quality'] = True
            print(f"\n   ✅ PASS: All 4 ETFs show realistic live prices")
        else:
            print(f"\n   ❌ FAIL: ETF price quality issues detected")
        
        print(f"\n   📊 ETF Price Quality Summary:")
        print(f"     - Realistic Prices: {etf_price_analysis['realistic_prices']}/4")
        print(f"     - Zero Prices: {etf_price_analysis['zero_prices']}/4")
        print(f"     - ETF Symbols Found: {etf_price_analysis['etf_symbols_found']}")
        print(f"     - Futures Display: {etf_price_analysis['futures_symbols_found']}")
        print(f"     - Valid Price Ranges: {etf_price_analysis['price_ranges_valid']}/4")
        
        detailed_results['etf_price_analysis'] = etf_price_analysis
        
        # REQUIREMENT 6: Response Performance
        print(f"\n⚡ REQUIREMENT 6: Response Performance Verification")
        print("-" * 80)
        
        print(f"   ⏱️  Response Time: {response_time:.3f} seconds")
        
        # Performance thresholds
        if response_time <= 3.0:
            test_results['response_performance'] = True
            print(f"   ✅ PASS: Excellent response time (≤3.0s)")
        elif response_time <= 5.0:
            test_results['response_performance'] = True
            print(f"   ✅ PASS: Good response time (≤5.0s)")
        elif response_time <= 10.0:
            print(f"   ⚠️  ACCEPTABLE: Moderate response time (≤10.0s)")
        else:
            print(f"   ❌ FAIL: Slow response time (>10.0s)")
        
        detailed_results['performance'] = {
            'response_time': response_time,
            'performance_rating': 'excellent' if response_time <= 3.0 else 
                                'good' if response_time <= 5.0 else
                                'acceptable' if response_time <= 10.0 else 'slow'
        }
        
        # FINAL ASSESSMENT
        print(f"\n" + "="*100)
        print("🎯 FINAL ASSESSMENT - MARKET OVERVIEW IMPROVED MESSAGING")
        print("="*100)
        
        passed_requirements = sum(test_results.values())
        total_requirements = len(test_results)
        success_rate = (passed_requirements / total_requirements) * 100
        
        print(f"\n📊 REQUIREMENT RESULTS:")
        requirement_names = {
            'live_etf_data_status': '1. Live ETF Data Status',
            'improved_messaging': '2. Improved Messaging',
            'new_status_fields': '3. New Status Fields',
            'accurate_coverage': '4. Accurate Coverage',
            'etf_price_quality': '5. ETF Price Quality',
            'response_performance': '6. Response Performance'
        }
        
        for key, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {requirement_names[key]}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_requirements}/{total_requirements} requirements met)")
        
        # Detailed findings
        print(f"\n📋 DETAILED FINDINGS:")
        print(f"   🔗 Data Source: {data_source}")
        print(f"   📝 Note: {note}")
        print(f"   🐋 UW Coverage: {unusual_whales_coverage}")
        print(f"   📊 Live Data Status: {overview_data.get('live_data_status', 'Not specified')}")
        print(f"   ⏱️  Response Time: {response_time:.3f}s")
        print(f"   💰 Price Quality: {etf_price_analysis['realistic_prices']}/4 realistic prices")
        
        # Professional assessment
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT")
            print(f"   The Market Overview endpoint successfully implements improved messaging")
            print(f"   for live ETF data. Users will clearly understand they are receiving")
            print(f"   live ETF data for futures-style trading, even when using fallback sources.")
            print(f"   The professional Market Dashboard backend is ready for production.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD")
            print(f"   The Market Overview endpoint mostly meets requirements with minor issues.")
            print(f"   The improved messaging is functional and users should understand")
            print(f"   they are receiving live ETF data for trading purposes.")
        else:
            print(f"\n❌ VERDICT: NEEDS IMPROVEMENT")
            print(f"   The Market Overview endpoint has significant issues with the improved")
            print(f"   messaging requirements. Users may not clearly understand the live")
            print(f"   ETF data status or trading implications.")
        
        # Store detailed results for potential debugging
        self.detailed_test_results = detailed_results
        
        return success_rate >= 70

    def run_comprehensive_test(self):
        """Run the comprehensive final test"""
        print("🚀 Starting Market Overview Final Test - Improved Messaging")
        print(f"🌐 Testing against: {self.base_url}")
        print(f"📅 Test Time: {datetime.now().isoformat()}")
        
        # Run the main test
        success = self.test_market_overview_final_messaging()
        
        # Summary
        print(f"\n" + "="*100)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*100)
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Overall Success: {'✅ PASS' if success else '❌ FAIL'}")
        print(f"   Test Duration: {datetime.now().isoformat()}")
        
        return success

if __name__ == "__main__":
    tester = MarketOverviewFinalTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)