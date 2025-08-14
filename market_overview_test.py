#!/usr/bin/env python3
"""
Market Overview Futures Headers Test
Test the updated Market Overview endpoint to verify futures-style headers (SPX, NQ, YM, RTY)
"""

import requests
import sys
from datetime import datetime
import json

class MarketOverviewTester:
    def __init__(self, base_url="https://7a773a8a-2f25-4f93-af2e-50c73530caf1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def test_market_overview_futures_headers(self):
        """Test market overview endpoint with futures-style headers (SPX, NQ, YM, RTY) - COMPREHENSIVE TESTING"""
        print("\n🔮 Testing Market Overview with Futures-Style Headers")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify Market Overview displays futures symbols (SPX, NQ, YM, RTY)")
        print("📊 REQUIREMENTS: Test symbol display, data quality, response structure, fallback functionality")
        
        url = f"{self.api_url}/market/overview"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"\n📡 API Call: {url}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Market Overview endpoint failed with status {response.status_code}")
                return False
            
            overview_data = response.json()
            print(f"✅ Response received successfully")
            
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False
        
        # Test 1: Verify Response Structure
        print(f"\n📋 PHASE 1: Response Structure Verification")
        print("-" * 60)
        
        required_fields = ['indices', 'data_source', 'note', 'last_updated']
        missing_fields = [field for field in required_fields if field not in overview_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required response fields present: {required_fields}")
        
        indices = overview_data.get('indices', [])
        data_source = overview_data.get('data_source', '')
        note = overview_data.get('note', '')
        
        print(f"📊 Found {len(indices)} market indices")
        print(f"🔗 Data Source: {data_source}")
        print(f"📝 Note: {note}")
        
        # Test 2: Verify Futures Symbol Display
        print(f"\n🎯 PHASE 2: Futures Symbol Display Verification")
        print("-" * 60)
        
        expected_futures_symbols = ['SPX', 'NQ', 'YM', 'RTY']
        expected_underlying_symbols = ['^GSPC', '^IXIC', '^DJI', '^RUT']
        expected_names = [
            'SPX (S&P 500)',
            'NQ (NASDAQ-100)', 
            'YM (Dow Jones)',
            'RTY (Russell 2000)'
        ]
        
        futures_test_results = {
            'total_indices': len(indices),
            'futures_symbols_found': 0,
            'underlying_symbols_verified': 0,
            'names_verified': 0,
            'prices_realistic': 0,
            'new_fields_present': 0
        }
        
        if len(indices) != 4:
            print(f"⚠️  Expected 4 indices, found {len(indices)}")
        
        for i, index in enumerate(indices):
            symbol = index.get('symbol', 'N/A')
            name = index.get('name', 'N/A')
            price = index.get('price', 0)
            underlying_symbol = index.get('underlying_symbol', 'N/A')
            data_source_field = index.get('data_source', 'N/A')
            
            print(f"\n   📊 Index {i+1}: {symbol}")
            print(f"     - Display Name: {name}")
            print(f"     - Price: ${price:.2f}")
            print(f"     - Underlying Symbol: {underlying_symbol}")
            print(f"     - Data Source: {data_source_field}")
            
            # Verify futures symbol display
            if symbol in expected_futures_symbols:
                futures_test_results['futures_symbols_found'] += 1
                print(f"     ✅ Futures symbol correct: {symbol}")
            else:
                print(f"     ❌ Unexpected symbol: {symbol} (expected one of {expected_futures_symbols})")
            
            # Verify underlying symbol mapping
            if underlying_symbol in expected_underlying_symbols:
                futures_test_results['underlying_symbols_verified'] += 1
                print(f"     ✅ Underlying symbol correct: {underlying_symbol}")
            else:
                print(f"     ❌ Unexpected underlying symbol: {underlying_symbol}")
            
            # Verify name format
            if any(expected_name in name for expected_name in expected_names):
                futures_test_results['names_verified'] += 1
                print(f"     ✅ Name format correct: {name}")
            else:
                print(f"     ⚠️  Name format unexpected: {name}")
            
            # Verify price realism
            price_ranges = {
                'SPX': (6000, 7000),    # S&P 500 typical range
                'NQ': (20000, 23000),   # NASDAQ typical range  
                'YM': (43000, 46000),   # Dow Jones typical range
                'RTY': (2200, 2400)     # Russell 2000 typical range
            }
            
            if symbol in price_ranges:
                min_price, max_price = price_ranges[symbol]
                if min_price <= price <= max_price:
                    futures_test_results['prices_realistic'] += 1
                    print(f"     ✅ Price realistic: ${price:.2f} (range: ${min_price}-${max_price})")
                else:
                    print(f"     ⚠️  Price outside expected range: ${price:.2f} (expected: ${min_price}-${max_price})")
            
            # Verify new required fields
            required_index_fields = ['underlying_symbol', 'data_source']
            missing_index_fields = [field for field in required_index_fields if field not in index]
            
            if not missing_index_fields:
                futures_test_results['new_fields_present'] += 1
                print(f"     ✅ All new fields present: {required_index_fields}")
            else:
                print(f"     ❌ Missing new fields: {missing_index_fields}")
        
        # Test 3: Symbol Mapping Verification
        print(f"\n🔄 PHASE 3: Symbol Mapping Verification")
        print("-" * 60)
        
        expected_mappings = {
            'SPX': '^GSPC',
            'NQ': '^IXIC', 
            'YM': '^DJI',
            'RTY': '^RUT'
        }
        
        mapping_correct = 0
        for index in indices:
            symbol = index.get('symbol')
            underlying = index.get('underlying_symbol')
            
            if symbol in expected_mappings:
                expected_underlying = expected_mappings[symbol]
                if underlying == expected_underlying:
                    mapping_correct += 1
                    print(f"   ✅ {symbol} → {underlying} (correct mapping)")
                else:
                    print(f"   ❌ {symbol} → {underlying} (expected {expected_underlying})")
        
        print(f"   📊 Mapping Accuracy: {mapping_correct}/{len(expected_mappings)} correct")
        
        # Test 4: Data Quality Verification
        print(f"\n💰 PHASE 4: Data Quality Verification")
        print("-" * 60)
        
        for index in indices:
            symbol = index.get('symbol')
            price = index.get('price', 0)
            change = index.get('change', 0)
            change_percent = index.get('change_percent', 0)
            
            print(f"   📊 {symbol}: ${price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")
            
            # Verify price is not zero
            if price > 0:
                print(f"     ✅ Price is realistic (not zero)")
            else:
                print(f"     ❌ Price is zero or invalid")
            
            # Verify change values are reasonable
            if abs(change_percent) <= 10:  # Daily changes typically < 10%
                print(f"     ✅ Change percentage reasonable: {change_percent:+.2f}%")
            else:
                print(f"     ⚠️  Change percentage high: {change_percent:+.2f}%")
        
        # Test 5: Futures Display Note Verification
        print(f"\n📝 PHASE 5: Futures Display Note Verification")
        print("-" * 60)
        
        futures_keywords = ['futures', 'SPX', 'NQ', 'YM', 'RTY', 'TradeStation', 'index equivalents']
        note_keywords_found = [keyword for keyword in futures_keywords if keyword.lower() in note.lower()]
        
        if note_keywords_found:
            print(f"   ✅ Note contains futures-related keywords: {note_keywords_found}")
        else:
            print(f"   ⚠️  Note may not clearly indicate futures display")
        
        print(f"   📝 Full Note: {note}")
        
        # Test 6: Fallback Functionality Test
        print(f"\n🛡️  PHASE 6: Fallback Functionality Verification")
        print("-" * 60)
        
        # Check if we're using fallback data
        if "Mock Data" in data_source or "Fallback" in data_source:
            print(f"   🔧 Using fallback data: {data_source}")
            
            # Verify fallback still shows futures symbols
            fallback_symbols = [index.get('symbol') for index in indices]
            futures_in_fallback = [symbol for symbol in fallback_symbols if symbol in expected_futures_symbols]
            
            if len(futures_in_fallback) == 4:
                print(f"   ✅ Fallback maintains futures symbols: {futures_in_fallback}")
            else:
                print(f"   ❌ Fallback doesn't maintain futures symbols: {fallback_symbols}")
        else:
            print(f"   📊 Using live data: {data_source}")
        
        # Test 7: Enhanced Metadata Verification
        print(f"\n📋 PHASE 7: Enhanced Metadata Verification")
        print("-" * 60)
        
        metadata_checks = []
        
        # Check for enhanced metadata fields
        if 'data_source' in overview_data:
            metadata_checks.append("✅ data_source field present")
        else:
            metadata_checks.append("❌ data_source field missing")
        
        if 'note' in overview_data and 'futures' in overview_data['note'].lower():
            metadata_checks.append("✅ futures display note present")
        else:
            metadata_checks.append("❌ futures display note missing")
        
        if 'last_updated' in overview_data:
            metadata_checks.append("✅ last_updated timestamp present")
        else:
            metadata_checks.append("❌ last_updated timestamp missing")
        
        # Check individual index metadata
        for index in indices:
            if 'underlying_symbol' in index and 'data_source' in index:
                metadata_checks.append(f"✅ {index.get('symbol')} has enhanced metadata")
            else:
                metadata_checks.append(f"❌ {index.get('symbol')} missing enhanced metadata")
        
        for check in metadata_checks:
            print(f"   {check}")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Market Overview Futures Headers")
        print("=" * 80)
        
        total_tests = 7
        passed_tests = 0
        
        # Test results summary
        test_results = [
            ("Response Structure", len(missing_fields) == 0),
            ("Futures Symbols", futures_test_results['futures_symbols_found'] == 4),
            ("Symbol Mapping", mapping_correct == 4),
            ("Data Quality", futures_test_results['prices_realistic'] >= 3),
            ("Futures Note", len(note_keywords_found) >= 2),
            ("Enhanced Metadata", futures_test_results['new_fields_present'] >= 3),
            ("Overall Functionality", len(indices) == 4 and futures_test_results['futures_symbols_found'] >= 3)
        ]
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")
            if passed:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Detailed metrics
        print(f"\n📈 DETAILED METRICS:")
        print(f"   - Futures Symbols Found: {futures_test_results['futures_symbols_found']}/4")
        print(f"   - Underlying Symbols Verified: {futures_test_results['underlying_symbols_verified']}/4")
        print(f"   - Names Verified: {futures_test_results['names_verified']}/4")
        print(f"   - Realistic Prices: {futures_test_results['prices_realistic']}/4")
        print(f"   - Enhanced Metadata: {futures_test_results['new_fields_present']}/4")
        print(f"   - Symbol Mapping Accuracy: {mapping_correct}/4")
        
        # Requirements verification
        print(f"\n✅ REQUIREMENTS VERIFICATION:")
        requirements_met = []
        
        if futures_test_results['futures_symbols_found'] >= 3:
            requirements_met.append("✅ Market Overview displays futures symbols (SPX, NQ, YM, RTY)")
        else:
            requirements_met.append("❌ Market Overview does not display futures symbols properly")
        
        if futures_test_results['underlying_symbols_verified'] >= 3:
            requirements_met.append("✅ Response shows underlying symbols (^GSPC, ^IXIC, ^DJI, ^RUT)")
        else:
            requirements_met.append("❌ Underlying symbols not properly mapped")
        
        if futures_test_results['prices_realistic'] >= 3:
            requirements_met.append("✅ Real price data is being fetched from underlying indices")
        else:
            requirements_met.append("❌ Price data quality issues detected")
        
        if futures_test_results['new_fields_present'] >= 3:
            requirements_met.append("✅ New fields present (underlying_symbol, data_source)")
        else:
            requirements_met.append("❌ New required fields missing")
        
        if len(note_keywords_found) >= 2:
            requirements_met.append("✅ Enhanced metadata with futures display note")
        else:
            requirements_met.append("❌ Futures display note insufficient")
        
        if "Mock Data" in data_source or "Fallback" in data_source:
            if futures_test_results['futures_symbols_found'] >= 3:
                requirements_met.append("✅ Fallback functionality maintains futures-style symbols")
            else:
                requirements_met.append("❌ Fallback functionality doesn't maintain futures symbols")
        else:
            requirements_met.append("✅ Using live data (fallback not needed)")
        
        for requirement in requirements_met:
            print(f"   {requirement}")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Market Overview futures headers implementation is working perfectly!")
            print(f"   The Market Dashboard will now show SPX, NQ, YM, RTY as requested by the user.")
            print(f"   Data accuracy is maintained through underlying index equivalents.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Market Overview futures headers mostly working with minor issues.")
            print(f"   The Market Dashboard should display futures symbols correctly.")
        else:
            print(f"\n❌ VERDICT: NEEDS IMPROVEMENT - Market Overview futures headers have significant issues.")
            print(f"   The Market Dashboard may not display futures symbols as expected.")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = MarketOverviewTester()
    success = tester.test_market_overview_futures_headers()
    
    if success:
        print(f"\n🎉 Market Overview Futures Headers Test: PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ Market Overview Futures Headers Test: FAILED")
        sys.exit(1)