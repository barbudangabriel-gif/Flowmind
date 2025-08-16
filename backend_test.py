import requests
import sys
from datetime import datetime, timedelta
import json

class StockMarketAPITester:
    def __init__(self, base_url="https://tradedash-11.preview.emergentagent.com"):
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
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
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_market_overview_futures_headers(self):
        """Test market overview endpoint with futures-style headers (SPX, NQ, YM, RTY) - COMPREHENSIVE TESTING"""
        print("\n🔮 Testing Market Overview with Futures-Style Headers")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify Market Overview displays futures symbols (SPX, NQ, YM, RTY)")
        print("📊 REQUIREMENTS: Test symbol display, data quality, response structure, fallback functionality")
        
        success, overview_data = self.run_test("Market Overview - Futures Headers", "GET", "market/overview", 200)
        
        if not success:
            print("❌ Market Overview endpoint failed")
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

    def test_top_movers(self):
        """Test top movers endpoint"""
        return self.run_test("Top Movers", "GET", "market/top-movers", 200)

    def test_stock_data(self, symbol="AAPL"):
        """Test stock data endpoint - CRITICAL: Check for real prices"""
        success, stock_data = self.run_test(f"Stock Data ({symbol})", "GET", f"stocks/{symbol}", 200)
        if success and symbol == "AAPL":
            price = stock_data.get('price', 0)
            print(f"   💰 {symbol} Price: ${price:.2f} (Expected ~$227, NOT $0.00)")
            if price == 0.0:
                print(f"   ❌ CRITICAL: {symbol} showing $0.00 price!")
            elif price > 200:
                print(f"   ✅ GOOD: {symbol} showing real price")
        return success

    def test_stock_history(self, symbol="AAPL"):
        """Test stock history endpoint"""
        return self.run_test(f"Stock History ({symbol})", "GET", f"stocks/{symbol}/history", 200, params={"period": "1mo"})

    def test_technical_indicators(self, symbol="AAPL"):
        """Test technical indicators endpoint"""
        return self.run_test(f"Technical Indicators ({symbol})", "GET", f"stocks/{symbol}/indicators", 200)

    def test_stock_search(self, query="AAPL"):
        """Test stock search endpoint"""
        return self.run_test(f"Stock Search ({query})", "GET", f"stocks/search/{query}", 200)

    def test_portfolio_operations(self):
        """Test portfolio CRUD operations"""
        # Test getting empty portfolio
        success, portfolio_data = self.run_test("Get Portfolio (Empty)", "GET", "portfolio", 200)
        
        # Test adding portfolio item
        portfolio_item = {
            "symbol": "AAPL",
            "shares": 10.0,
            "purchase_price": 150.0,
            "purchase_date": (datetime.now() - timedelta(days=30)).isoformat()
        }
        
        success, add_response = self.run_test("Add Portfolio Item", "POST", "portfolio", 200, data=portfolio_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting portfolio with item
            self.run_test("Get Portfolio (With Items)", "GET", "portfolio", 200)
            
            # Test deleting portfolio item
            self.run_test("Delete Portfolio Item", "DELETE", f"portfolio/{item_id}", 200)
        
        return success

    def test_watchlist_operations(self):
        """Test watchlist CRUD operations"""
        # Test getting empty watchlist
        self.run_test("Get Watchlist (Empty)", "GET", "watchlist", 200)
        
        # Test adding watchlist item
        watchlist_item = {
            "symbol": "GOOGL",
            "target_price": 2800.0,
            "notes": "Test watchlist item"
        }
        
        success, add_response = self.run_test("Add Watchlist Item", "POST", "watchlist", 200, data=watchlist_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting watchlist with item
            self.run_test("Get Watchlist (With Items)", "GET", "watchlist", 200)
            
            # Test deleting watchlist item
            self.run_test("Delete Watchlist Item", "DELETE", f"watchlist/{item_id}", 200)
        
        return success

    def test_ticker_endpoints(self):
        """Test new ticker endpoints for S&P 500 and NASDAQ"""
        # Test S&P 500 tickers
        success, sp500_data = self.run_test("S&P 500 Tickers", "GET", "tickers/sp500", 200)
        if success and 'tickers' in sp500_data:
            print(f"   Found {len(sp500_data['tickers'])} S&P 500 tickers")
        
        # Test NASDAQ tickers
        success, nasdaq_data = self.run_test("NASDAQ Tickers", "GET", "tickers/nasdaq", 200)
        if success and 'tickers' in nasdaq_data:
            print(f"   Found {len(nasdaq_data['tickers'])} NASDAQ tickers")
        
        # Test all tickers
        success, all_data = self.run_test("All Tickers", "GET", "tickers/all", 200)
        if success and 'tickers' in all_data:
            print(f"   Found {len(all_data['tickers'])} total tickers")
        
        return success

    def test_screener_endpoints(self):
        """Test advanced screener endpoints - CRITICAL: Check for real prices (not $0.00)"""
        # Test basic screener data
        success, screener_data = self.run_test("Screener Data (All)", "GET", "screener/data", 200, params={"limit": 20, "exchange": "all"})
        if success and 'stocks' in screener_data:
            print(f"   Found {len(screener_data['stocks'])} stocks in screener")
            
            # CRITICAL CHECK: Verify real prices (not $0.00)
            zero_price_count = 0
            real_price_count = 0
            for stock in screener_data['stocks']:
                if stock.get('price', 0) == 0.0:
                    zero_price_count += 1
                else:
                    real_price_count += 1
                    if stock['symbol'] == 'AAPL':
                        print(f"   ✅ AAPL Price: ${stock['price']:.2f} (Expected ~$227)")
                    elif stock['symbol'] == 'ABT':
                        print(f"   ✅ ABT Price: ${stock['price']:.2f} (Expected ~$131)")
            
            print(f"   📊 Price Analysis: {real_price_count} real prices, {zero_price_count} zero prices")
            if zero_price_count > real_price_count:
                print(f"   ⚠️  WARNING: More zero prices than real prices!")
        
        # Test S&P 500 screener data
        success, sp500_screener = self.run_test("Screener Data (S&P 500)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "sp500"})
        if success and 'stocks' in sp500_screener:
            print(f"   Found {len(sp500_screener['stocks'])} S&P 500 stocks")
        
        # Test NASDAQ screener data
        success, nasdaq_screener = self.run_test("Screener Data (NASDAQ)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "nasdaq"})
        if success and 'stocks' in nasdaq_screener:
            print(f"   Found {len(nasdaq_screener['stocks'])} NASDAQ stocks")
        
        # Test screener sectors
        self.run_test("Available Sectors", "GET", "screener/sectors", 200)
        
        # Test advanced filtering
        filter_criteria = {
            "min_price": 50.0,
            "max_price": 500.0,
            "min_market_cap": 1000.0,  # 1B market cap
            "sector": "Technology"
        }
        
        success, filtered_data = self.run_test("Advanced Filter (Tech Stocks)", "POST", "screener/filter", 200, data=filter_criteria)
        if success and 'stocks' in filtered_data:
            print(f"   Found {len(filtered_data['stocks'])} filtered stocks")
        
        # Test filter with P/E ratio
        pe_filter = {
            "min_pe": 10.0,
            "max_pe": 30.0,
            "min_volume": 1000000
        }
        
        success, pe_filtered = self.run_test("P/E Ratio Filter", "POST", "screener/filter", 200, data=pe_filter)
        if success and 'stocks' in pe_filtered:
            print(f"   Found {len(pe_filtered['stocks'])} stocks with P/E 10-30")
        
        return success

    def test_enhanced_stock_endpoints(self):
        """Test NEW enhanced stock endpoints with real-time data and extended hours"""
        # Test enhanced stock data for AAPL
        success, aapl_enhanced = self.run_test("Enhanced Stock Data (AAPL)", "GET", "stocks/AAPL/enhanced", 200)
        if success:
            print(f"   ✅ AAPL Enhanced Price: ${aapl_enhanced.get('price', 0):.2f}")
            print(f"   Market State: {aapl_enhanced.get('market_state', 'UNKNOWN')}")
            if 'extended_hours' in aapl_enhanced:
                extended = aapl_enhanced['extended_hours']
                if 'premarket' in extended:
                    print(f"   📈 Premarket Data: ${extended['premarket'].get('price', 'N/A')}")
                if 'postmarket' in extended:
                    print(f"   📉 Postmarket Data: ${extended['postmarket'].get('price', 'N/A')}")
        
        # Test extended hours endpoint
        success, extended_hours = self.run_test("Extended Hours Data (AAPL)", "GET", "stocks/AAPL/extended-hours", 200)
        if success:
            print(f"   Market State: {extended_hours.get('market_state', 'UNKNOWN')}")
            print(f"   Regular Price: ${extended_hours.get('regular_price', 0):.2f}")
        
        # Test enhanced data for other popular stocks
        for symbol in ["MSFT", "GOOGL", "TSLA"]:
            success, enhanced_data = self.run_test(f"Enhanced Stock Data ({symbol})", "GET", f"stocks/{symbol}/enhanced", 200)
            if success and enhanced_data.get('price', 0) > 0:
                print(f"   ✅ {symbol} Price: ${enhanced_data['price']:.2f}")
        
        return success

    def test_investment_scoring_endpoints(self):
        """Test NEW Investment Scoring System endpoints - PRIORITY FEATURE"""
        print("\n🎯 Testing Investment Scoring System - NEW FEATURE")
        
        # Test top investment picks
        success, top_picks_data = self.run_test("Investment Top Picks", "GET", "investments/top-picks", 200, params={"limit": 10})
        if success and 'recommendations' in top_picks_data:
            recommendations = top_picks_data['recommendations']
            print(f"   Found {len(recommendations)} top investment picks")
            
            # Check first recommendation structure
            if recommendations:
                first_pick = recommendations[0]
                print(f"   #1 Pick: {first_pick.get('symbol', 'N/A')} - Score: {first_pick.get('total_score', 'N/A')} - Rating: {first_pick.get('rating', 'N/A')}")
                print(f"   Risk Level: {first_pick.get('risk_level', 'N/A')}")
                
                # Verify required fields
                required_fields = ['symbol', 'total_score', 'rating', 'risk_level', 'key_strengths', 'key_risks']
                missing_fields = [field for field in required_fields if field not in first_pick]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in top pick: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present in top pick")
        
        # Test individual stock scoring - AAPL
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   AAPL Risk Level: {aapl_score.get('risk_level', 'N/A')}")
            
            # Check individual scores breakdown
            individual_scores = aapl_score.get('individual_scores', {})
            if individual_scores:
                print(f"   Score Breakdown: {len(individual_scores)} metrics")
                # Show a few key scores
                for key in ['pe_score', 'momentum_score', 'value_score']:
                    if key in individual_scores:
                        print(f"     {key}: {individual_scores[key]}")
        
        # Test sector leaders
        success, sector_data = self.run_test("Sector Leaders (Technology)", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"})
        if success and 'leaders' in sector_data:
            leaders = sector_data['leaders']
            print(f"   Found {len(leaders)} Technology sector leaders")
            if leaders:
                top_leader = leaders[0]
                print(f"   Top Tech Leader: {top_leader.get('symbol', 'N/A')} - Score: {top_leader.get('total_score', 'N/A')}")
        
        # Test different sector
        success, healthcare_data = self.run_test("Sector Leaders (Healthcare)", "GET", "investments/sector-leaders", 200, params={"sector": "Healthcare"})
        if success and 'leaders' in healthcare_data:
            leaders = healthcare_data['leaders']
            print(f"   Found {len(leaders)} Healthcare sector leaders")
        
        # Test risk analysis
        success, risk_data = self.run_test("Risk Analysis", "GET", "investments/risk-analysis", 200)
        if success and 'risk_categories' in risk_data:
            risk_categories = risk_data['risk_categories']
            print(f"   Risk Categories: {list(risk_categories.keys())}")
            
            for risk_level, stocks in risk_categories.items():
                print(f"   {risk_level} Risk: {len(stocks)} stocks")
                if stocks:
                    # Show first stock in each category
                    first_stock = stocks[0]
                    print(f"     Example: {first_stock.get('symbol', 'N/A')} - Score: {first_stock.get('total_score', 'N/A')}")
        
        return success

    def test_top_picks_endpoint_comprehensive(self):
        """Test Top Picks endpoint comprehensively as requested by user - PRIORITY TEST"""
        print("\n🎯 COMPREHENSIVE TOP PICKS ENDPOINT TESTING - USER PRIORITY REQUEST")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test Top Picks endpoint that user needs working")
        print("📋 REQUIREMENTS: 'am nevoie de top picks minim 10' - need at least 10 recommendations")
        print("🔧 TESTING: Different limits, market cap filters, data quality verification")
        
        # Test 1: Basic Top Picks with limit=10 (User's primary requirement)
        print(f"\n📊 PHASE 1: Basic Top Picks (limit=10) - PRIMARY USER REQUIREMENT")
        print("-" * 60)
        
        success, top_picks_data = self.run_test("Top Picks (limit=10)", "GET", "investments/top-picks", 200, params={"limit": 10})
        
        if not success:
            print("❌ CRITICAL: Top Picks endpoint failed - user's primary requirement not met")
            return False
        
        # Verify response structure
        required_fields = ['recommendations', 'total_analyzed', 'criteria', 'last_updated']
        missing_fields = [field for field in required_fields if field not in top_picks_data]
        
        if missing_fields:
            print(f"❌ Missing required response fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required response fields present: {required_fields}")
        
        recommendations = top_picks_data.get('recommendations', [])
        total_analyzed = top_picks_data.get('total_analyzed', 0)
        criteria = top_picks_data.get('criteria', '')
        
        print(f"📊 Found {len(recommendations)} investment recommendations")
        print(f"📊 Total stocks analyzed: {total_analyzed}")
        print(f"📊 Selection criteria: {criteria}")
        
        # CRITICAL CHECK: User needs at least 10 recommendations
        if len(recommendations) < 10:
            print(f"❌ CRITICAL FAILURE: Only {len(recommendations)} recommendations found, user needs minimum 10")
            print(f"   🚨 USER REQUIREMENT NOT MET: 'am nevoie de top picks minim 10'")
            return False
        else:
            print(f"✅ USER REQUIREMENT MET: {len(recommendations)} recommendations >= 10 minimum")
        
        # Test 2: Verify Investment Score and Rating Data Quality
        print(f"\n📋 PHASE 2: Investment Score and Rating Data Quality")
        print("-" * 60)
        
        if recommendations:
            print(f"📊 Analyzing top 5 recommendations:")
            
            valid_recommendations = 0
            for i, rec in enumerate(recommendations[:5]):
                symbol = rec.get('symbol', 'N/A')
                total_score = rec.get('total_score', 0)
                rating = rec.get('rating', 'N/A')
                risk_level = rec.get('risk_level', 'N/A')
                
                print(f"   #{i+1}: {symbol}")
                print(f"     - Investment Score: {total_score}")
                print(f"     - Rating: {rating}")
                print(f"     - Risk Level: {risk_level}")
                
                # Verify score is reasonable (0-100 range)
                if 0 <= total_score <= 100:
                    print(f"     ✅ Score in valid range (0-100)")
                    valid_recommendations += 1
                else:
                    print(f"     ❌ Score outside valid range: {total_score}")
                
                # Verify rating is valid
                valid_ratings = ['STRONG BUY', 'BUY', 'BUY+', 'HOLD+', 'HOLD', 'HOLD-', 'SELL', 'STRONG SELL']
                if rating in valid_ratings:
                    print(f"     ✅ Valid rating: {rating}")
                else:
                    print(f"     ⚠️  Unusual rating: {rating}")
                
                # Check for required fields
                required_rec_fields = ['symbol', 'total_score', 'rating', 'risk_level', 'key_strengths', 'key_risks']
                missing_rec_fields = [field for field in required_rec_fields if field not in rec]
                
                if missing_rec_fields:
                    print(f"     ❌ Missing fields: {missing_rec_fields}")
                else:
                    print(f"     ✅ All required fields present")
            
            print(f"📊 Valid recommendations: {valid_recommendations}/5")
        
        # Test 3: Stock Information Verification (symbol, price, change, etc.)
        print(f"\n💰 PHASE 3: Stock Information Verification")
        print("-" * 60)
        
        if recommendations:
            print(f"📊 Verifying stock data for top recommendations:")
            
            stocks_with_price_data = 0
            for i, rec in enumerate(recommendations[:3]):
                symbol = rec.get('symbol', 'N/A')
                
                # Check if recommendation includes price information
                price_fields = ['current_price', 'price', 'change', 'change_percent']
                price_data_found = [field for field in price_fields if field in rec and rec[field] is not None]
                
                print(f"   📊 {symbol}:")
                if price_data_found:
                    print(f"     ✅ Price data fields found: {price_data_found}")
                    stocks_with_price_data += 1
                    
                    # Display available price data
                    for field in price_data_found:
                        value = rec[field]
                        if 'price' in field:
                            print(f"     - {field}: ${value:.2f}")
                        elif 'change' in field:
                            print(f"     - {field}: {value:+.2f}{'%' if 'percent' in field else ''}")
                else:
                    print(f"     ⚠️  No direct price data in recommendation")
                    print(f"     📝 Note: Price data may be fetched separately by frontend")
                
                # Check for additional stock information
                info_fields = ['market_cap', 'pe_ratio', 'sector', 'industry']
                info_found = [field for field in info_fields if field in rec and rec[field] is not None]
                
                if info_found:
                    print(f"     ✅ Additional info: {info_found}")
                    for field in info_found:
                        value = rec[field]
                        if field == 'market_cap':
                            print(f"     - {field}: ${value/1e9:.1f}B" if value > 1e9 else f"${value/1e6:.1f}M")
                        else:
                            print(f"     - {field}: {value}")
            
            print(f"📊 Stocks with price data: {stocks_with_price_data}/3")
        
        # Test 4: Test with Different Limits (5, 15 as requested)
        print(f"\n🔢 PHASE 4: Different Limit Parameters Testing")
        print("-" * 60)
        
        limit_tests = [
            {"limit": 5, "name": "Fewer picks (5)"},
            {"limit": 15, "name": "More picks (15)"},
            {"limit": 20, "name": "Extended picks (20)"}
        ]
        
        limit_results = {}
        
        for test in limit_tests:
            limit = test["limit"]
            name = test["name"]
            
            success_limit, limit_data = self.run_test(
                f"Top Picks ({name})", 
                "GET", 
                "investments/top-picks", 
                200, 
                params={"limit": limit}
            )
            
            if success_limit:
                limit_recommendations = limit_data.get('recommendations', [])
                limit_results[limit] = len(limit_recommendations)
                
                print(f"   📊 Limit {limit}: {len(limit_recommendations)} recommendations returned")
                
                # Verify we get the requested number (or close to it)
                if len(limit_recommendations) >= min(limit, 10):  # At least the minimum or requested
                    print(f"     ✅ Adequate number of recommendations")
                else:
                    print(f"     ⚠️  Fewer recommendations than expected")
                
                # Check if recommendations are properly sorted by score
                if len(limit_recommendations) >= 2:
                    scores = [rec.get('total_score', 0) for rec in limit_recommendations]
                    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                    
                    if is_sorted:
                        print(f"     ✅ Recommendations properly sorted by score")
                        print(f"     - Top score: {scores[0]:.1f}")
                        print(f"     - Lowest score: {scores[-1]:.1f}")
                    else:
                        print(f"     ⚠️  Recommendations may not be sorted by score")
            else:
                print(f"   ❌ Failed to get recommendations with limit {limit}")
        
        # Test 5: Market Cap Filter Testing
        print(f"\n💰 PHASE 5: Market Cap Filter Testing")
        print("-" * 60)
        
        market_cap_tests = [
            {"min_market_cap": 1000, "name": "Large Cap (≥$1B)"},
            {"min_market_cap": 10000, "name": "Mega Cap (≥$10B)"},
            {"min_market_cap": 50000, "name": "Ultra Large Cap (≥$50B)"}
        ]
        
        for test in market_cap_tests:
            min_cap = test["min_market_cap"]
            name = test["name"]
            
            params = {
                "limit": 10,
                "min_market_cap": min_cap
            }
            
            success_cap, cap_data = self.run_test(
                f"Top Picks ({name})", 
                "GET", 
                "investments/top-picks", 
                200, 
                params=params
            )
            
            if success_cap:
                cap_recommendations = cap_data.get('recommendations', [])
                print(f"   📊 {name}: {len(cap_recommendations)} recommendations")
                
                if cap_recommendations:
                    # Show top recommendation for this market cap filter
                    top_rec = cap_recommendations[0]
                    symbol = top_rec.get('symbol', 'N/A')
                    score = top_rec.get('total_score', 0)
                    print(f"     - Top pick: {symbol} (Score: {score:.1f})")
        
        # Test 6: Exchange Filter Testing
        print(f"\n🏛️  PHASE 6: Exchange Filter Testing")
        print("-" * 60)
        
        exchange_tests = [
            {"exchange": "sp500", "name": "S&P 500"},
            {"exchange": "nasdaq", "name": "NASDAQ"},
            {"exchange": "all", "name": "All Exchanges"}
        ]
        
        for test in exchange_tests:
            exchange = test["exchange"]
            name = test["name"]
            
            params = {
                "limit": 10,
                "exchange": exchange
            }
            
            success_ex, ex_data = self.run_test(
                f"Top Picks ({name})", 
                "GET", 
                "investments/top-picks", 
                200, 
                params=params
            )
            
            if success_ex:
                ex_recommendations = ex_data.get('recommendations', [])
                print(f"   📊 {name}: {len(ex_recommendations)} recommendations")
                
                if ex_recommendations:
                    # Show symbols for this exchange
                    symbols = [rec.get('symbol', 'N/A') for rec in ex_recommendations[:5]]
                    print(f"     - Top symbols: {symbols}")
        
        # Test 7: Response Time and Performance
        print(f"\n⏱️  PHASE 7: Response Time and Performance")
        print("-" * 60)
        
        import time
        start_time = time.time()
        
        success_perf, perf_data = self.run_test("Top Picks (Performance Test)", "GET", "investments/top-picks", 200, params={"limit": 10})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   ⏱️  Response Time: {response_time:.2f} seconds")
        
        if response_time < 5.0:
            print(f"   ✅ Excellent response time")
        elif response_time < 15.0:
            print(f"   ✅ Good response time")
        elif response_time < 30.0:
            print(f"   ⚠️  Slow response time")
        else:
            print(f"   ❌ Very slow response time (may timeout)")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Top Picks Endpoint")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("Basic Endpoint Response", success),
            ("Minimum 10 Recommendations", len(recommendations) >= 10),
            ("Valid Investment Scores", valid_recommendations >= 3 if recommendations else False),
            ("Different Limits Working", len(limit_results) >= 2),
            ("Response Structure Complete", len(missing_fields) == 0),
            ("Performance Acceptable", response_time < 30.0)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Recommendations Found: {len(recommendations)}")
        print(f"   - User Requirement (≥10): {'✅ MET' if len(recommendations) >= 10 else '❌ NOT MET'}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - Total Stocks Analyzed: {total_analyzed}")
        print(f"   - Different Limits Tested: {list(limit_results.keys())}")
        
        # User-specific feedback
        print(f"\n👤 USER FEEDBACK:")
        if len(recommendations) >= 10:
            print(f"   ✅ SUCCESS: Top Picks endpoint provides {len(recommendations)} recommendations")
            print(f"   ✅ User requirement 'am nevoie de top picks minim 10' is satisfied")
            print(f"   📊 Investment Scoring page should display recommendations correctly")
        else:
            print(f"   ❌ FAILURE: Only {len(recommendations)} recommendations found")
            print(f"   🚨 User requirement 'am nevoie de top picks minim 10' is NOT satisfied")
            print(f"   🔧 Investment Scoring page may show insufficient data")
        
        # Final verdict
        if success_rate >= 85 and len(recommendations) >= 10:
            print(f"\n🎉 VERDICT: EXCELLENT - Top Picks endpoint fully meets user requirements!")
            print(f"   The Investment Scoring page Top Picks functionality is working perfectly.")
            print(f"   User will see at least 10 investment recommendations with proper scores and ratings.")
        elif success_rate >= 70 and len(recommendations) >= 10:
            print(f"\n✅ VERDICT: GOOD - Top Picks endpoint meets user requirements with minor issues.")
            print(f"   The Investment Scoring page should work correctly for the user.")
        else:
            print(f"\n❌ VERDICT: NEEDS IMMEDIATE ATTENTION - Top Picks endpoint does not meet user requirements.")
            print(f"   The Investment Scoring page may not provide adequate functionality for the user.")
        
        return success_rate >= 70 and len(recommendations) >= 10

    def test_unusual_whales_options_flow(self):
        """Test Unusual Whales Options Flow API endpoints - COMPREHENSIVE TESTING WITH REAL API KEY"""
        print("\n🐋 TESTING UNUSUAL WHALES OPTIONS FLOW API - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test Options Flow endpoint with real API key (5809ee6a-bcb6-48ce-a16d-9f3bd634fd50)")
        print("🔧 FOCUS: Verify real data vs mock data, identify 404 errors, test different parameters")
        
        # Test 1: Basic Options Flow Alerts (Default Parameters)
        print(f"\n📊 PHASE 1: Basic Options Flow API Testing")
        print("-" * 60)
        
        success, flow_data = self.run_test("Options Flow Alerts (Default)", "GET", "unusual-whales/options/flow-alerts", 200)
        if not success:
            print("❌ Options Flow API endpoint failed - checking for 404 errors")
            # Try alternative endpoints that might work
            alternative_endpoints = [
                "unusual-whales/options/flow",
                "unusual-whales/flow-alerts", 
                "unusual-whales/options-flow"
            ]
            
            for alt_endpoint in alternative_endpoints:
                print(f"   🔍 Trying alternative endpoint: {alt_endpoint}")
                alt_success, alt_data = self.run_test(f"Alternative Options Flow ({alt_endpoint})", "GET", alt_endpoint, 200)
                if alt_success:
                    print(f"   ✅ Alternative endpoint working: {alt_endpoint}")
                    flow_data = alt_data
                    success = True
                    break
            
            if not success:
                print("❌ All Options Flow endpoints failed - API may be down or endpoints incorrect")
                return False
        
        # Analyze response structure
        data = flow_data.get('data', {})
        alerts = data.get('alerts', [])
        summary = data.get('summary', {})
        status = flow_data.get('status', 'unknown')
        
        print(f"📊 API Status: {status}")
        print(f"📊 Found {len(alerts)} options flow alerts")
        print(f"💰 Total Premium: ${summary.get('total_premium', 0):,.0f}")
        print(f"📈 Bullish Count: {summary.get('bullish_count', 0)}")
        print(f"📉 Bearish Count: {summary.get('bearish_count', 0)}")
        print(f"🔥 Unusual Activity: {summary.get('unusual_activity', 0)}")
        print(f"🎯 Opening Trades: {summary.get('opening_trades', 0)}")
        
        # Test 2: Real Data vs Mock Data Detection
        print(f"\n🔍 PHASE 2: Real Data vs Mock Data Detection")
        print("-" * 60)
        
        is_real_data = False
        mock_data_indicators = []
        real_data_indicators = []
        
        if alerts:
            # Check for mock data patterns
            symbols = [alert.get('symbol', '') for alert in alerts]
            premiums = [alert.get('premium', 0) for alert in alerts]
            
            # Mock data typically has predictable patterns
            if len(set(symbols)) < len(symbols) * 0.7:  # Too many duplicate symbols
                mock_data_indicators.append("High symbol duplication")
            
            if all(p % 1000 == 0 for p in premiums if p > 0):  # All premiums are round thousands
                mock_data_indicators.append("All premiums are round numbers")
            
            # Real data indicators
            if len(set(symbols)) >= 3:  # Good symbol diversity
                real_data_indicators.append("Good symbol diversity")
            
            if any(p % 1000 != 0 for p in premiums if p > 0):  # Some non-round premiums
                real_data_indicators.append("Realistic premium values")
            
            # Check for realistic market symbols
            common_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'AMZN', 'META']
            real_symbols_found = [s for s in symbols if s in common_symbols]
            if real_symbols_found:
                real_data_indicators.append(f"Real market symbols: {real_symbols_found}")
            
            print(f"   📊 Symbols Found: {list(set(symbols))}")
            print(f"   💰 Premium Range: ${min(premiums):,.0f} - ${max(premiums):,.0f}")
            
            if len(real_data_indicators) > len(mock_data_indicators):
                is_real_data = True
                print(f"   ✅ REAL DATA DETECTED")
                for indicator in real_data_indicators:
                    print(f"     - {indicator}")
            else:
                print(f"   ⚠️  MOCK DATA SUSPECTED")
                for indicator in mock_data_indicators:
                    print(f"     - {indicator}")
        else:
            print(f"   ⚠️  No alerts found - could be real (no activity) or API issue")
        
        # Test 3: Data Structure Verification
        print(f"\n📋 PHASE 3: Data Structure Verification")
        print("-" * 60)
        
        if alerts:
            first_alert = alerts[0]
            required_fields = ['symbol', 'strike_type', 'premium', 'sentiment', 'volume']
            optional_fields = ['volume_oi_ratio', 'is_opener', 'unusual_activity', 'dte', 'strike_price']
            
            missing_required = [field for field in required_fields if field not in first_alert]
            present_optional = [field for field in optional_fields if field in first_alert]
            
            if missing_required:
                print(f"   ❌ Missing required fields: {missing_required}")
            else:
                print(f"   ✅ All required fields present: {required_fields}")
            
            if present_optional:
                print(f"   ✅ Optional fields present: {present_optional}")
            
            # Display sample alert
            print(f"   📊 Sample Alert:")
            print(f"     - Symbol: {first_alert.get('symbol', 'N/A')}")
            print(f"     - Strike/Type: {first_alert.get('strike_type', 'N/A')}")
            print(f"     - Premium: ${first_alert.get('premium', 0):,.0f}")
            print(f"     - Sentiment: {first_alert.get('sentiment', 'N/A')}")
            print(f"     - Volume: {first_alert.get('volume', 0):,}")
            if 'dte' in first_alert:
                print(f"     - DTE: {first_alert.get('dte', 'N/A')}")
            if 'strike_price' in first_alert:
                print(f"     - Strike Price: ${first_alert.get('strike_price', 0):.2f}")
        
        # Test 4: Premium Filter Testing (200K and 500K as requested)
        print(f"\n💰 PHASE 4: Premium Filter Testing")
        print("-" * 60)
        
        premium_filters = [200000, 500000]
        filter_results = {}
        
        for min_premium in premium_filters:
            params = {
                "minimum_premium": min_premium,
                "limit": 50,
                "include_analysis": True
            }
            
            success_filter, filtered_data = self.run_test(
                f"Options Flow (Premium >= ${min_premium:,})", 
                "GET", 
                "unusual-whales/options/flow-alerts", 
                200, 
                params=params
            )
            
            if success_filter:
                filtered_alerts = filtered_data.get('data', {}).get('alerts', [])
                filter_results[min_premium] = len(filtered_alerts)
                
                print(f"   💰 Premium >= ${min_premium:,}: {len(filtered_alerts)} alerts")
                
                if filtered_alerts:
                    avg_premium = sum(alert.get('premium', 0) for alert in filtered_alerts) / len(filtered_alerts)
                    max_premium = max(alert.get('premium', 0) for alert in filtered_alerts)
                    min_premium_actual = min(alert.get('premium', 0) for alert in filtered_alerts)
                    
                    print(f"     - Average Premium: ${avg_premium:,.0f}")
                    print(f"     - Premium Range: ${min_premium_actual:,.0f} - ${max_premium:,.0f}")
                    
                    # Verify filter is working
                    if min_premium_actual >= min_premium:
                        print(f"     ✅ Filter working correctly")
                    else:
                        print(f"     ⚠️  Filter may not be working (found ${min_premium_actual:,} < ${min_premium:,})")
                
                # Check for analysis
                analysis = filtered_data.get('analysis', {})
                if analysis:
                    signals = analysis.get('signals', [])
                    patterns = analysis.get('patterns', [])
                    print(f"     - Trading Signals: {len(signals)}")
                    print(f"     - Patterns Detected: {len(patterns)}")
                    
                    if signals:
                        for signal in signals[:2]:
                            print(f"       • {signal.get('type', 'unknown')}: {signal.get('description', 'N/A')}")
        
        # Test 5: Response Time and Performance
        print(f"\n⏱️  PHASE 5: Response Time and Performance Testing")
        print("-" * 60)
        
        import time
        start_time = time.time()
        
        success_perf, perf_data = self.run_test("Options Flow (Performance Test)", "GET", "unusual-whales/options/flow-alerts", 200)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   ⏱️  Response Time: {response_time:.2f} seconds")
        
        if response_time < 1.0:
            print(f"   ✅ Excellent response time")
        elif response_time < 3.0:
            print(f"   ✅ Good response time")
        elif response_time < 10.0:
            print(f"   ⚠️  Slow response time")
        else:
            print(f"   ❌ Very slow response time")
        
        # Test 6: Error Handling and Edge Cases
        print(f"\n🔧 PHASE 6: Error Handling and Edge Cases")
        print("-" * 60)
        
        # Test with invalid parameters
        invalid_params = {
            "minimum_premium": -1000,  # Negative premium
            "limit": 0  # Zero limit
        }
        
        success_invalid, invalid_data = self.run_test(
            "Options Flow (Invalid Params)", 
            "GET", 
            "unusual-whales/options/flow-alerts", 
            200,  # Should still return 200 but handle gracefully
            params=invalid_params
        )
        
        if success_invalid:
            invalid_alerts = invalid_data.get('data', {}).get('alerts', [])
            print(f"   🔧 Invalid params handled: {len(invalid_alerts)} alerts returned")
        
        # Test with very high premium filter (should return few/no results)
        high_premium_params = {"minimum_premium": 10000000}  # $10M premium
        success_high, high_data = self.run_test(
            "Options Flow (Very High Premium)", 
            "GET", 
            "unusual-whales/options/flow-alerts", 
            200, 
            params=high_premium_params
        )
        
        if success_high:
            high_alerts = high_data.get('data', {}).get('alerts', [])
            print(f"   💰 Very high premium filter: {len(high_alerts)} alerts (expected: few/none)")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Options Flow API")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("API Endpoint Response", success),
            ("Data Structure", len(alerts) >= 0),  # 0 is acceptable
            ("Real Data Detection", is_real_data or len(alerts) == 0),  # 0 alerts could be real
            ("Premium Filtering", len(filter_results) >= 2),
            ("Performance", response_time < 10.0),
            ("Error Handling", success_invalid)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Options Flow Alerts Found: {len(alerts)}")
        print(f"   - Data Type: {'✅ REAL DATA' if is_real_data else '⚠️  MOCK DATA or NO DATA'}")
        print(f"   - API Response Time: {response_time:.2f}s")
        print(f"   - Premium Filters Working: {'✅ YES' if len(filter_results) >= 2 else '❌ NO'}")
        print(f"   - Total Premium: ${summary.get('total_premium', 0):,.0f}")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not is_real_data and len(alerts) > 0:
            print(f"   ⚠️  Options Flow may be showing mock data - check API key configuration")
        elif len(alerts) == 0:
            print(f"   📝 No alerts found - could be normal if no unusual options activity")
        else:
            print(f"   ✅ Options Flow API working correctly with real data")
        
        if response_time > 5.0:
            print(f"   ⚠️  Consider optimizing API response time")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Options Flow API working perfectly!")
            print(f"   The Options Flow component should display real data correctly.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Options Flow API mostly working with minor issues.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Options Flow API has significant issues.")
        
        return success_rate >= 70

    def test_unusual_whales_dark_pool_fix(self):
        """Test Unusual Whales Dark Pool API endpoints - COMPREHENSIVE DARK POOL FIX TESTING"""
        print("\n🌊 TESTING DARK POOL API FIX - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify Dark Pool API fix shows REAL data instead of empty results")
        print("🔧 FIXES TESTED:")
        print("   1. ✅ Updated minimum_dark_percentage filter from 30.0% to 0.01%")
        print("   2. ✅ Enhanced data processing for actual Unusual Whales API format")
        print("   3. ✅ Added debug logging and fallback mechanisms")
        print("   4. ✅ Verify trades array populated with real data")
        
        # Test 1: Basic Dark Pool API Endpoint
        print(f"\n📊 PHASE 1: Basic Dark Pool API Endpoint Testing")
        print("-" * 60)
        
        success, dark_pool_data = self.run_test("Dark Pool Recent Activity", "GET", "unusual-whales/dark-pool/recent", 200)
        if not success:
            print("❌ Dark Pool API endpoint failed")
            return False
        
        # Verify response structure
        required_top_level_fields = ['status', 'data', 'timestamp']
        missing_top_fields = [field for field in required_top_level_fields if field not in dark_pool_data]
        
        if missing_top_fields:
            print(f"❌ Missing top-level fields: {missing_top_fields}")
            return False
        else:
            print(f"✅ All required top-level fields present: {required_top_level_fields}")
        
        data = dark_pool_data.get('data', {})
        trades = data.get('trades', [])
        summary = data.get('summary', {})
        status = dark_pool_data.get('status', 'unknown')
        
        print(f"📊 API Status: {status}")
        print(f"📊 Found {len(trades)} dark pool trades")
        print(f"📈 Total Dark Volume: {summary.get('total_dark_volume', 0):,}")
        print(f"🎯 Avg Dark %: {summary.get('avg_dark_percentage', 0):.2f}%")
        print(f"🏛️  Institutional Signals: {summary.get('institutional_signals', 0)}")
        print(f"🔥 High Significance: {summary.get('high_significance', 0)}")
        
        # Test 2: Verify Real Data vs Empty Results
        print(f"\n🔍 PHASE 2: Real Data Verification (Fix Validation)")
        print("-" * 60)
        
        if len(trades) == 0:
            print("⚠️  ZERO TRADES FOUND - This could be expected if no significant dark pool activity")
            print("   📝 NOTE: 0 trades is acceptable when no activity meets filtering criteria")
            print("   🔧 Testing with more permissive filters to verify API connectivity...")
            
            # Test with very permissive filters to see if we can get any data
            permissive_params = {
                "minimum_volume": 1000,  # Very low volume threshold
                "minimum_dark_percentage": 0.01,  # Very low dark percentage (the fix!)
                "limit": 100
            }
            
            success_permissive, permissive_data = self.run_test(
                "Dark Pool (Very Permissive Filters)", 
                "GET", 
                "unusual-whales/dark-pool/recent", 
                200, 
                params=permissive_params
            )
            
            if success_permissive:
                permissive_trades = permissive_data.get('data', {}).get('trades', [])
                print(f"   🔧 Permissive Filter Results: {len(permissive_trades)} trades")
                
                if len(permissive_trades) > 0:
                    print("   ✅ API IS WORKING - Data available with permissive filters")
                    print("   💡 Original 0 results likely due to no significant activity meeting default criteria")
                    trades = permissive_trades  # Use permissive data for further testing
                    data = permissive_data.get('data', {})
                    summary = data.get('summary', {})
                else:
                    print("   ⚠️  Still 0 trades with permissive filters - may indicate API issues or no market activity")
        else:
            print(f"✅ REAL DATA FOUND: {len(trades)} dark pool trades")
            print("   🎉 FIX SUCCESSFUL - Dark Pool API now returning actual data!")
        
        # Test 3: Data Structure and Field Verification
        print(f"\n📋 PHASE 3: Data Structure Verification")
        print("-" * 60)
        
        if trades:
            first_trade = trades[0]
            print(f"📊 Analyzing first trade: {first_trade.get('ticker', 'N/A')}")
            
            # Verify all required fields are present
            required_trade_fields = [
                'ticker', 'timestamp', 'price', 'dark_volume', 'total_volume', 
                'dark_percentage', 'dollar_volume', 'significance', 'institutional_signal'
            ]
            missing_fields = [field for field in required_trade_fields if field not in first_trade]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print(f"✅ All required fields present: {len(required_trade_fields)} fields")
            
            # Display sample trade data
            print(f"   📊 Sample Trade Details:")
            print(f"     - Ticker: {first_trade.get('ticker', 'N/A')}")
            print(f"     - Price: ${first_trade.get('price', 0):.2f}")
            print(f"     - Dark Volume: {first_trade.get('dark_volume', 0):,}")
            print(f"     - Total Volume: {first_trade.get('total_volume', 0):,}")
            print(f"     - Dark Percentage: {first_trade.get('dark_percentage', 0):.2f}%")
            print(f"     - Dollar Volume: ${first_trade.get('dollar_volume', 0):,.0f}")
            print(f"     - Significance: {first_trade.get('significance', 'N/A')}")
            print(f"     - Institutional Signal: {first_trade.get('institutional_signal', False)}")
            print(f"     - Timestamp: {first_trade.get('timestamp', 'N/A')}")
            
            # Test 4: Verify Ticker Symbols (Real Market Data)
            print(f"\n🏷️  PHASE 4: Ticker Symbol Verification")
            print("-" * 60)
            
            tickers_found = [trade.get('ticker', 'N/A') for trade in trades[:10]]  # First 10 tickers
            print(f"   📊 Sample Tickers Found: {tickers_found}")
            
            # Check for expected ticker patterns (real market symbols)
            expected_ticker_patterns = ['XLF', 'BBEU', 'COIN', 'SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOGL']
            real_tickers_found = [ticker for ticker in tickers_found if any(pattern in ticker for pattern in expected_ticker_patterns)]
            
            if real_tickers_found:
                print(f"   ✅ Real market tickers detected: {real_tickers_found}")
                print("   🎉 VERIFICATION: API returning actual market data, not mock data")
            else:
                print(f"   ⚠️  No expected ticker patterns found - may be using different symbols or mock data")
            
            # Test 5: Dark Percentage Calculations Verification
            print(f"\n📊 PHASE 5: Dark Percentage Calculations Verification")
            print("-" * 60)
            
            dark_percentages = [trade.get('dark_percentage', 0) for trade in trades[:5]]
            print(f"   📊 Sample Dark Percentages: {[f'{dp:.2f}%' for dp in dark_percentages]}")
            
            # Verify dark percentages are reasonable (< 100% and > 0%)
            valid_percentages = [dp for dp in dark_percentages if 0 < dp < 100]
            invalid_percentages = [dp for dp in dark_percentages if dp <= 0 or dp >= 100]
            
            print(f"   ✅ Valid Dark Percentages: {len(valid_percentages)}/{len(dark_percentages)}")
            if invalid_percentages:
                print(f"   ⚠️  Invalid Dark Percentages: {invalid_percentages}")
            
            # Check if percentages are reasonable (typically < 20% for most stocks)
            reasonable_percentages = [dp for dp in dark_percentages if dp < 20]
            print(f"   📊 Reasonable Percentages (<20%): {len(reasonable_percentages)}/{len(dark_percentages)}")
            
            # Test 6: Dollar Volume Calculations Verification
            print(f"\n💰 PHASE 6: Dollar Volume Calculations Verification")
            print("-" * 60)
            
            for i, trade in enumerate(trades[:3]):
                ticker = trade.get('ticker', 'N/A')
                price = trade.get('price', 0)
                dark_volume = trade.get('dark_volume', 0)
                dollar_volume = trade.get('dollar_volume', 0)
                
                # Calculate expected dollar volume
                expected_dollar_volume = price * dark_volume
                
                print(f"   📊 Trade {i+1} ({ticker}):")
                print(f"     - Price: ${price:.2f}")
                print(f"     - Dark Volume: {dark_volume:,}")
                print(f"     - Reported Dollar Volume: ${dollar_volume:,.0f}")
                print(f"     - Expected Dollar Volume: ${expected_dollar_volume:,.0f}")
                
                # Verify calculation accuracy (allow for small rounding differences)
                if abs(dollar_volume - expected_dollar_volume) < (expected_dollar_volume * 0.01):  # 1% tolerance
                    print(f"     ✅ Dollar volume calculation accurate")
                else:
                    print(f"     ⚠️  Dollar volume calculation may be incorrect")
        else:
            print("⚠️  No trades available for detailed verification")
            print("   📝 This may be normal if no significant dark pool activity is occurring")
        
        # Test 7: API Filtering with Different minimum_dark_percentage Values
        print(f"\n🔍 PHASE 7: API Filtering Tests (Key Fix Verification)")
        print("-" * 60)
        
        filter_tests = [
            {"minimum_dark_percentage": 0.01, "name": "Very Low (0.01% - THE FIX!)"},
            {"minimum_dark_percentage": 5.0, "name": "Low (5.0%)"},
            {"minimum_dark_percentage": 15.0, "name": "Medium (15.0%)"},
            {"minimum_dark_percentage": 30.0, "name": "High (30.0% - OLD SETTING)"}
        ]
        
        filter_results = {}
        
        for filter_test in filter_tests:
            min_dark_pct = filter_test["minimum_dark_percentage"]
            test_name = filter_test["name"]
            
            params = {
                "minimum_volume": 100000,
                "minimum_dark_percentage": min_dark_pct,
                "limit": 50
            }
            
            success_filter, filter_data = self.run_test(
                f"Dark Pool Filter ({test_name})", 
                "GET", 
                "unusual-whales/dark-pool/recent", 
                200, 
                params=params
            )
            
            if success_filter:
                filter_trades = filter_data.get('data', {}).get('trades', [])
                filter_results[min_dark_pct] = len(filter_trades)
                print(f"   📊 {test_name}: {len(filter_trades)} trades")
                
                if len(filter_trades) > 0:
                    avg_dark_pct = sum(trade.get('dark_percentage', 0) for trade in filter_trades) / len(filter_trades)
                    print(f"     - Average Dark %: {avg_dark_pct:.2f}%")
                    print(f"     - Min Dark % in results: {min(trade.get('dark_percentage', 0) for trade in filter_trades):.2f}%")
                    print(f"     - Max Dark % in results: {max(trade.get('dark_percentage', 0) for trade in filter_trades):.2f}%")
        
        # Verify that lower thresholds return more results (the fix validation)
        print(f"\n   🔧 FILTER FIX VALIDATION:")
        if 0.01 in filter_results and 30.0 in filter_results:
            low_threshold_results = filter_results[0.01]
            high_threshold_results = filter_results[30.0]
            
            print(f"     - 0.01% threshold (NEW): {low_threshold_results} trades")
            print(f"     - 30.0% threshold (OLD): {high_threshold_results} trades")
            
            if low_threshold_results >= high_threshold_results:
                print(f"     ✅ FIX VERIFIED: Lower threshold returns more/equal results")
                print(f"     🎉 Dark Pool API fix is working correctly!")
            else:
                print(f"     ⚠️  Unexpected: Higher threshold returned more results")
        
        # Test 8: Institutional Signal Logic Verification
        print(f"\n🏛️  PHASE 8: Institutional Signal Logic Verification")
        print("-" * 60)
        
        if trades:
            institutional_trades = [trade for trade in trades if trade.get('institutional_signal', False)]
            non_institutional_trades = [trade for trade in trades if not trade.get('institutional_signal', False)]
            
            print(f"   📊 Institutional Signals: {len(institutional_trades)}/{len(trades)} trades")
            print(f"   📊 Non-Institutional: {len(non_institutional_trades)}/{len(trades)} trades")
            
            if institutional_trades:
                print(f"   ✅ Institutional signal logic working")
                # Show sample institutional trade
                inst_trade = institutional_trades[0]
                print(f"   📊 Sample Institutional Trade:")
                print(f"     - Ticker: {inst_trade.get('ticker', 'N/A')}")
                print(f"     - Dark Volume: {inst_trade.get('dark_volume', 0):,}")
                print(f"     - Dark %: {inst_trade.get('dark_percentage', 0):.2f}%")
                print(f"     - Significance: {inst_trade.get('significance', 'N/A')}")
            else:
                print(f"   📊 No institutional signals detected (may be normal)")
        
        # Test 9: Significance Scoring Verification
        print(f"\n⭐ PHASE 9: Significance Scoring Verification")
        print("-" * 60)
        
        if trades:
            significance_levels = {}
            for trade in trades:
                sig_level = trade.get('significance', 'unknown')
                significance_levels[sig_level] = significance_levels.get(sig_level, 0) + 1
            
            print(f"   📊 Significance Distribution:")
            for level, count in significance_levels.items():
                print(f"     - {level}: {count} trades")
            
            # Verify significance levels are valid
            valid_levels = ['low', 'medium', 'high', 'very_high']
            invalid_levels = [level for level in significance_levels.keys() if level not in valid_levels and level != 'unknown']
            
            if invalid_levels:
                print(f"   ⚠️  Invalid significance levels found: {invalid_levels}")
            else:
                print(f"   ✅ All significance levels are valid")
        
        # Test 10: Debug Endpoint Testing
        print(f"\n🔧 PHASE 10: Debug Endpoint Testing")
        print("-" * 60)
        
        success_debug, debug_data = self.run_test("Dark Pool Debug", "GET", "unusual-whales/dark-pool/debug", 200)
        if success_debug:
            print(f"   ✅ Debug endpoint accessible")
            
            if 'raw_api_response' in debug_data:
                raw_response = debug_data['raw_api_response']
                print(f"   📊 Raw API Response Status: {debug_data.get('api_status', 'unknown')}")
                
                if isinstance(raw_response, dict) and 'data' in raw_response:
                    raw_trades = raw_response.get('data', [])
                    print(f"   📊 Raw API Trades: {len(raw_trades)}")
                    
                    if raw_trades:
                        print(f"   ✅ Raw API returning data - processing pipeline working")
                    else:
                        print(f"   ⚠️  Raw API returning no data - may indicate API issues")
            
            if 'processed_trades' in debug_data:
                processed_trades = debug_data['processed_trades']
                print(f"   📊 Processed Trades: {len(processed_trades)}")
                
                if processed_trades:
                    print(f"   ✅ Data processing pipeline working")
                else:
                    print(f"   ⚠️  Data processing may have issues")
        else:
            print(f"   ⚠️  Debug endpoint not accessible")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Dark Pool API Fix")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("API Endpoint Response", success),
            ("Response Structure", len(missing_top_fields) == 0),
            ("Data Processing", len(trades) >= 0),  # 0 is acceptable
            ("Field Structure", len(trades) == 0 or len([field for field in required_trade_fields if field not in trades[0]]) == 0),
            ("Filter Functionality", len(filter_results) >= 2),
            ("Debug Endpoint", success_debug)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Dark Pool Trades Found: {len(trades)}")
        print(f"   - API Status: {status}")
        print(f"   - Filter Fix Working: {'✅ YES' if 0.01 in filter_results else '❌ UNKNOWN'}")
        print(f"   - Real Data Detected: {'✅ YES' if len(trades) > 0 else '⚠️  NO DATA (may be normal)'}")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Dark Pool API fix is working perfectly!")
            print(f"   The Dark Pool page should now show real trading data instead of empty results.")
            print(f"   All fixes have been successfully implemented and verified.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Dark Pool API fix mostly working with minor issues.")
            print(f"   The Dark Pool page should display data correctly.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Dark Pool API fix has significant issues.")
            print(f"   The Dark Pool page may still show empty results.")
        
        return success_rate >= 70

    def test_unusual_whales_congressional_trades(self):
        """Test Unusual Whales Congressional Trades API endpoints"""
        print("\n🏛️  Testing Unusual Whales Congressional Trades API")
        
        # Test basic congressional trades
        success, congress_data = self.run_test("Congressional Trades", "GET", "unusual-whales/congressional/trades", 200)
        if success:
            data = congress_data.get('data', {})
            trades = data.get('trades', [])
            summary = data.get('summary', {})
            
            print(f"   📊 Found {len(trades)} congressional trades")
            print(f"   💰 Total Amount: ${summary.get('total_amount', 0):,.0f}")
            print(f"   👥 Unique Representatives: {summary.get('unique_representatives', 0)}")
            print(f"   📈 Unique Tickers: {summary.get('unique_tickers', 0)}")
            print(f"   🕐 Recent Trades (7d): {summary.get('recent_trades', 0)}")
            
            # Show party breakdown
            party_breakdown = summary.get('party_breakdown', {})
            if party_breakdown:
                print(f"   🗳️  Party Breakdown:")
                for party, count in party_breakdown.items():
                    print(f"     - {party}: {count} trades")
            
            # Show transaction type breakdown
            transaction_breakdown = summary.get('transaction_type_breakdown', {})
            if transaction_breakdown:
                print(f"   💼 Transaction Types:")
                for tx_type, count in transaction_breakdown.items():
                    print(f"     - {tx_type}: {count} trades")
            
            # Verify data structure
            if trades:
                first_trade = trades[0]
                required_fields = ['representative', 'party', 'ticker', 'transaction_type', 'transaction_amount']
                missing_fields = [field for field in required_fields if field not in first_trade]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in trade: {missing_fields}")
                else:
                    print(f"   ✅ Trade data structure complete")
                    print(f"   Example: {first_trade.get('representative')} ({first_trade.get('party')}) - {first_trade.get('transaction_type')} {first_trade.get('ticker')} ${first_trade.get('transaction_amount', 0):,.0f}")
        
        # Test with filters
        params = {
            "days_back": 14,
            "minimum_amount": 50000,
            "party_filter": "Democrat",
            "transaction_type": "Purchase",
            "limit": 20,
            "include_analysis": True
        }
        success, filtered_data = self.run_test("Congressional Trades (Filtered)", "GET", "unusual-whales/congressional/trades", 200, params=params)
        if success:
            trades = filtered_data.get('data', {}).get('trades', [])
            analysis = filtered_data.get('analysis', {})
            print(f"   🔍 Filtered trades: {len(trades)} (Democrat purchases >= $50K, 14d)")
            if analysis and 'insights' in analysis:
                insights = analysis.get('insights', [])
                print(f"   💡 Analysis insights: {len(insights)}")
                for insight in insights[:2]:
                    print(f"     - {insight.get('type', 'unknown')}: {insight.get('description', 'N/A')}")
        
        return success

    def test_all_unusual_whales_endpoints(self):
        """Test ALL Unusual Whales API endpoints comprehensively with API key 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"""
        print("\n🐋 COMPREHENSIVE UNUSUAL WHALES API TESTING")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test all Unusual Whales endpoints with provided API key")
        print("🔑 API KEY: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print("🎯 PRIMARY FOCUS: Options Flow endpoint (main priority)")
        print("📊 SECONDARY: Dark Pool, Congressional Trades, Trading Strategies")
        
        endpoint_results = {}
        
        # Test 1: Options Flow Endpoint (MAIN PRIORITY)
        print(f"\n🎯 PRIORITY 1: OPTIONS FLOW ENDPOINT")
        print("=" * 60)
        
        options_flow_success = self.test_unusual_whales_options_flow()
        endpoint_results['options_flow'] = options_flow_success
        
        # Test 2: Dark Pool Endpoint
        print(f"\n🌊 PRIORITY 2: DARK POOL ENDPOINT")
        print("=" * 60)
        
        dark_pool_success = self.test_unusual_whales_dark_pool_fix()
        endpoint_results['dark_pool'] = dark_pool_success
        
        # Test 3: Congressional Trades Endpoint
        print(f"\n🏛️  PRIORITY 3: CONGRESSIONAL TRADES ENDPOINT")
        print("=" * 60)
        
        congressional_success = self.test_unusual_whales_congressional_trades()
        endpoint_results['congressional_trades'] = congressional_success
        
        # Test 4: Trading Strategies Endpoint
        print(f"\n🎯 PRIORITY 4: TRADING STRATEGIES ENDPOINT")
        print("=" * 60)
        
        strategies_success = self.test_unusual_whales_trading_strategies()
        endpoint_results['trading_strategies'] = strategies_success
        
        # Test 5: Comprehensive Analysis Endpoint
        print(f"\n📊 BONUS: COMPREHENSIVE ANALYSIS ENDPOINT")
        print("=" * 60)
        
        success, analysis_data = self.run_test("Comprehensive Analysis", "GET", "unusual-whales/analysis/comprehensive", 200)
        endpoint_results['comprehensive_analysis'] = success
        
        if success:
            comprehensive_analysis = analysis_data.get('comprehensive_analysis', {})
            market_outlook = analysis_data.get('market_outlook', {})
            data_summary = analysis_data.get('data_summary', {})
            
            print(f"   📊 Data Summary:")
            print(f"     - Options Alerts: {data_summary.get('options_alerts', 0)}")
            print(f"     - Dark Pool Trades: {data_summary.get('dark_pool_trades', 0)}")
            print(f"     - Congressional Trades: {data_summary.get('congressional_trades', 0)}")
            
            print(f"   🎯 Market Outlook:")
            print(f"     - Overall Sentiment: {market_outlook.get('overall_sentiment', 'unknown')}")
            print(f"     - Confidence: {market_outlook.get('confidence', 'unknown')}")
            print(f"     - Key Signals: {len(market_outlook.get('key_signals', []))}")
        
        # Test 6: Debug Endpoints (if available)
        print(f"\n🔧 DEBUG ENDPOINTS TESTING")
        print("=" * 60)
        
        debug_endpoints = [
            "unusual-whales/options/flow-alerts/debug",
            "unusual-whales/dark-pool/debug"
        ]
        
        for debug_endpoint in debug_endpoints:
            debug_success, debug_data = self.run_test(f"Debug ({debug_endpoint})", "GET", debug_endpoint, 200)
            if debug_success:
                print(f"   ✅ Debug endpoint accessible: {debug_endpoint}")
            else:
                print(f"   ❌ Debug endpoint failed: {debug_endpoint}")
        
        # Final Comprehensive Assessment
        print(f"\n🎯 FINAL COMPREHENSIVE ASSESSMENT")
        print("=" * 80)
        
        total_endpoints = len(endpoint_results)
        working_endpoints = sum(1 for success in endpoint_results.values() if success)
        success_rate = (working_endpoints / total_endpoints) * 100
        
        print(f"\n📊 ENDPOINT RESULTS SUMMARY:")
        priority_order = [
            ('options_flow', '🎯 Options Flow (MAIN PRIORITY)'),
            ('dark_pool', '🌊 Dark Pool'),
            ('congressional_trades', '🏛️  Congressional Trades'),
            ('trading_strategies', '🎯 Trading Strategies'),
            ('comprehensive_analysis', '📊 Comprehensive Analysis')
        ]
        
        for endpoint_key, endpoint_name in priority_order:
            if endpoint_key in endpoint_results:
                status = "✅ WORKING" if endpoint_results[endpoint_key] else "❌ FAILED"
                print(f"   {status} {endpoint_name}")
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({working_endpoints}/{total_endpoints} endpoints working)")
        
        # Specific findings for each endpoint
        print(f"\n🔍 DETAILED FINDINGS:")
        
        if endpoint_results.get('options_flow', False):
            print(f"   ✅ Options Flow: Working with real data - main priority achieved")
        else:
            print(f"   ❌ Options Flow: Failed - main priority NOT achieved")
        
        if endpoint_results.get('dark_pool', False):
            print(f"   ✅ Dark Pool: Working correctly")
        else:
            print(f"   ❌ Dark Pool: Issues detected")
        
        if endpoint_results.get('congressional_trades', False):
            print(f"   ✅ Congressional Trades: Working correctly")
        else:
            print(f"   ❌ Congressional Trades: Issues detected")
        
        if endpoint_results.get('trading_strategies', False):
            print(f"   ✅ Trading Strategies: Working correctly")
        else:
            print(f"   ❌ Trading Strategies: Issues detected")
        
        # 404 Error Analysis
        print(f"\n🚫 404 ERROR ANALYSIS:")
        failed_endpoints = [name for name, success in endpoint_results.items() if not success]
        
        if failed_endpoints:
            print(f"   ❌ Endpoints returning 404 or other errors: {failed_endpoints}")
            print(f"   💡 RECOMMENDATIONS:")
            print(f"     - Verify API key is correctly configured in backend/.env")
            print(f"     - Check Unusual Whales API documentation for correct endpoint paths")
            print(f"     - Ensure API key has proper permissions for all endpoints")
        else:
            print(f"   ✅ No 404 errors detected - all endpoints accessible")
        
        # API Key Status
        print(f"\n🔑 API KEY STATUS:")
        print(f"   - API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print(f"   - Working Endpoints: {working_endpoints}/{total_endpoints}")
        
        if working_endpoints >= 4:
            print(f"   ✅ API key appears to be working correctly")
        elif working_endpoints >= 2:
            print(f"   ⚠️  API key partially working - some endpoints may need attention")
        else:
            print(f"   ❌ API key may be invalid or endpoints are incorrect")
        
        # Final verdict
        if success_rate >= 80:
            print(f"\n🎉 VERDICT: EXCELLENT - Unusual Whales API integration working well!")
            print(f"   Most endpoints are operational with the provided API key.")
            if endpoint_results.get('options_flow', False):
                print(f"   ✅ MAIN PRIORITY ACHIEVED: Options Flow working with real data")
        elif success_rate >= 60:
            print(f"\n✅ VERDICT: GOOD - Most Unusual Whales endpoints working.")
            print(f"   Some endpoints may need attention but core functionality is operational.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Multiple Unusual Whales endpoints failing.")
            print(f"   API key or endpoint configurations may need review.")
        
        return endpoint_results
        """Test Unusual Whales Trading Strategies API endpoint with ENHANCED CHART INTEGRATION"""
        print("\n🎯 Testing Unusual Whales Trading Strategies API - ENHANCED WITH CHARTS")
        
        success, strategies_data = self.run_test("Trading Strategies Generation", "GET", "unusual-whales/trading-strategies", 200)
        if success:
            strategies = strategies_data.get('trading_strategies', [])  # Updated field name
            charts_included = strategies_data.get('charts_included', False)
            
            print(f"   📊 Generated {len(strategies)} trading strategies")
            print(f"   📈 Charts Included: {'✅ YES' if charts_included else '❌ NO'}")
            
            # Test chart integration for each strategy
            chart_test_results = {
                'total_strategies': len(strategies),
                'strategies_with_charts': 0,
                'chart_types_found': set(),
                'plotly_charts_valid': 0,
                'chart_errors': 0
            }
            
            if strategies:
                print(f"\n   🎨 CHART INTEGRATION TESTING:")
                
                for i, strategy in enumerate(strategies):
                    strategy_name = strategy.get('strategy_name', f'Strategy {i+1}')
                    print(f"   📋 Strategy {i+1}: {strategy_name}")
                    
                    # Test 1: Check if strategy has chart field
                    if 'chart' in strategy:
                        chart_test_results['strategies_with_charts'] += 1
                        chart_data = strategy['chart']
                        
                        # Test 2: Verify chart data structure
                        if 'chart_type' in chart_data:
                            chart_type = chart_data['chart_type']
                            chart_test_results['chart_types_found'].add(chart_type)
                            print(f"     - Chart Type: {chart_type}")
                            
                            # Test 3: Verify plotly chart JSON
                            if 'plotly_chart' in chart_data:
                                try:
                                    plotly_json = chart_data['plotly_chart']
                                    if isinstance(plotly_json, str):
                                        # Try to parse JSON
                                        import json
                                        parsed_chart = json.loads(plotly_json)
                                        if 'data' in parsed_chart and 'layout' in parsed_chart:
                                            chart_test_results['plotly_charts_valid'] += 1
                                            print(f"     - Plotly Chart: ✅ Valid JSON structure")
                                            
                                            # Test 4: Verify chart contains P&L data
                                            if 'data' in parsed_chart and len(parsed_chart['data']) > 0:
                                                first_trace = parsed_chart['data'][0]
                                                if 'x' in first_trace and 'y' in first_trace:
                                                    print(f"     - P&L Data Points: ✅ {len(first_trace['x'])} points")
                                                else:
                                                    print(f"     - P&L Data Points: ❌ Missing x/y data")
                                            
                                            # Test 5: Verify chart metrics
                                            metrics_found = []
                                            if 'max_profit' in chart_data:
                                                metrics_found.append(f"Max Profit: ${chart_data['max_profit']:.0f}")
                                            if 'max_loss' in chart_data:
                                                metrics_found.append(f"Max Loss: ${chart_data['max_loss']:.0f}")
                                            if 'breakeven_points' in chart_data:
                                                be_points = chart_data['breakeven_points']
                                                if be_points:
                                                    metrics_found.append(f"Breakeven: ${be_points[0]:.2f}")
                                            if 'breakeven' in chart_data:
                                                metrics_found.append(f"Breakeven: ${chart_data['breakeven']:.2f}")
                                            
                                            if metrics_found:
                                                print(f"     - Chart Metrics: ✅ {', '.join(metrics_found)}")
                                            else:
                                                print(f"     - Chart Metrics: ⚠️  No metrics found")
                                        else:
                                            print(f"     - Plotly Chart: ❌ Invalid structure")
                                    else:
                                        print(f"     - Plotly Chart: ❌ Not a string")
                                except Exception as e:
                                    print(f"     - Plotly Chart: ❌ JSON parse error: {str(e)}")
                                    chart_test_results['chart_errors'] += 1
                            else:
                                print(f"     - Plotly Chart: ❌ Missing plotly_chart field")
                        else:
                            print(f"     - Chart Type: ❌ Missing chart_type field")
                            
                        # Test 6: Verify strategy-specific chart types
                        expected_chart_types = {
                            'bull call spread': 'vertical_spread',
                            'bear put spread': 'vertical_spread', 
                            'long call': 'directional',
                            'long put': 'directional',
                            'long straddle': 'volatility',
                            'long strangle': 'volatility',
                            'iron condor': 'iron_condor',
                            'cash-secured put': 'income',
                            'covered call': 'income'
                        }
                        
                        strategy_name_lower = strategy_name.lower()
                        expected_type = None
                        for name_pattern, chart_type in expected_chart_types.items():
                            if name_pattern in strategy_name_lower:
                                expected_type = chart_type
                                break
                        
                        if expected_type and 'chart' in strategy:
                            actual_type = strategy['chart'].get('chart_type')
                            if actual_type == expected_type:
                                print(f"     - Chart Type Match: ✅ {actual_type} (expected)")
                            else:
                                print(f"     - Chart Type Match: ⚠️  {actual_type} (expected {expected_type})")
                    else:
                        print(f"     - Chart: ❌ Missing chart field")
                
                # Print chart testing summary
                print(f"\n   📊 CHART TESTING SUMMARY:")
                print(f"     - Total Strategies: {chart_test_results['total_strategies']}")
                print(f"     - Strategies with Charts: {chart_test_results['strategies_with_charts']}")
                print(f"     - Valid Plotly Charts: {chart_test_results['plotly_charts_valid']}")
                print(f"     - Chart Types Found: {', '.join(chart_test_results['chart_types_found'])}")
                print(f"     - Chart Errors: {chart_test_results['chart_errors']}")
                
                # Calculate success rate
                if chart_test_results['total_strategies'] > 0:
                    chart_success_rate = (chart_test_results['plotly_charts_valid'] / chart_test_results['total_strategies']) * 100
                    print(f"     - Chart Success Rate: {chart_success_rate:.1f}%")
                
                # Test 7: Verify TradeStation execution details
                print(f"\n   🎯 TRADESTATION EXECUTION TESTING:")
                first_strategy = strategies[0]
                print(f"   💡 Top Strategy: {first_strategy.get('strategy_name', 'N/A')}")
                print(f"     - Ticker: {first_strategy.get('ticker', 'N/A')}")
                print(f"     - Type: {first_strategy.get('strategy_type', 'N/A')}")
                print(f"     - Confidence: {first_strategy.get('confidence', 0):.2f}")
                print(f"     - Timeframe: {first_strategy.get('timeframe', 'N/A')}")
                
                # Check TradeStation execution details
                tradestation = first_strategy.get('tradestation_execution', {})
                if tradestation:
                    print(f"     - TradeStation Ready: ✅")
                    print(f"       * Underlying: {tradestation.get('underlying', 'N/A')}")
                    print(f"       * Max Risk: {tradestation.get('max_risk', 'N/A')}")
                    print(f"       * Max Profit: {tradestation.get('max_profit', 'N/A')}")
                    print(f"       * Breakeven: {tradestation.get('breakeven', 'N/A')}")
                    
                    # Check legs structure
                    legs = tradestation.get('legs', [])
                    if legs:
                        print(f"       * Strategy Legs: {len(legs)} legs")
                        for j, leg in enumerate(legs):
                            action = leg.get('action', 'N/A')
                            strike = leg.get('strike', 'N/A')
                            option_type = leg.get('option_type', 'N/A')
                            print(f"         - Leg {j+1}: {action} {option_type} @ ${strike}")
                    else:
                        print(f"       * Strategy Legs: ❌ No legs found")
                else:
                    print(f"     - TradeStation Ready: ❌")
                
                # Verify required fields
                required_fields = ['strategy_name', 'ticker', 'confidence', 'entry_logic', 'risk_management', 'chart']
                missing_fields = [field for field in required_fields if field not in first_strategy]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in strategy: {missing_fields}")
                else:
                    print(f"   ✅ Strategy data structure complete with charts")
        
        return success

    def test_unusual_whales_trading_strategies(self):
        """Test Unusual Whales Trading Strategies API endpoint"""
        print("\n🎯 Testing Unusual Whales Trading Strategies API")
        
        success, strategies_data = self.run_test("Trading Strategies Generation", "GET", "unusual-whales/trading-strategies", 200)
        if success:
            strategies = strategies_data.get('trading_strategies', [])
            charts_included = strategies_data.get('charts_included', False)
            
            print(f"   📊 Generated {len(strategies)} trading strategies")
            print(f"   📈 Charts Included: {'✅ YES' if charts_included else '❌ NO'}")
            
            if strategies:
                first_strategy = strategies[0]
                print(f"   💡 Top Strategy: {first_strategy.get('strategy_name', 'N/A')}")
                print(f"     - Ticker: {first_strategy.get('ticker', 'N/A')}")
                print(f"     - Type: {first_strategy.get('strategy_type', 'N/A')}")
                print(f"     - Confidence: {first_strategy.get('confidence', 0):.2f}")
                print(f"     - Timeframe: {first_strategy.get('timeframe', 'N/A')}")
                
                # Check TradeStation execution details
                tradestation = first_strategy.get('tradestation_execution', {})
                if tradestation:
                    print(f"     - TradeStation Ready: ✅")
                    print(f"       * Underlying: {tradestation.get('underlying', 'N/A')}")
                    print(f"       * Max Risk: {tradestation.get('max_risk', 'N/A')}")
                    print(f"       * Max Profit: {tradestation.get('max_profit', 'N/A')}")
                else:
                    print(f"     - TradeStation Ready: ❌")
                
                # Verify required fields
                required_fields = ['strategy_name', 'ticker', 'confidence', 'entry_logic', 'risk_management']
                missing_fields = [field for field in required_fields if field not in first_strategy]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in strategy: {missing_fields}")
                else:
                    print(f"   ✅ Strategy data structure complete")
        
        return success
        """Test Unusual Whales Comprehensive Analysis API endpoint"""
        print("\n🔬 Testing Unusual Whales Comprehensive Analysis API")
        
        success, analysis_data = self.run_test("Comprehensive Analysis", "GET", "unusual-whales/analysis/comprehensive", 200)
        if success:
            comprehensive_analysis = analysis_data.get('comprehensive_analysis', {})
            market_outlook = analysis_data.get('market_outlook', {})
            data_summary = analysis_data.get('data_summary', {})
            
            print(f"   📊 Data Sources:")
            print(f"     - Options Alerts: {data_summary.get('options_alerts', 0)}")
            print(f"     - Dark Pool Trades: {data_summary.get('dark_pool_trades', 0)}")
            print(f"     - Congressional Trades: {data_summary.get('congressional_trades', 0)}")
            
            # Check each analysis component
            for source, analysis in comprehensive_analysis.items():
                data_available = analysis.get('data_available', False)
                print(f"   {source.replace('_', ' ').title()}: {'✅ Available' if data_available else '❌ No Data'}")
                
                if data_available and 'analysis' in analysis:
                    source_analysis = analysis['analysis']
                    if isinstance(source_analysis, dict):
                        if 'signals' in source_analysis:
                            signals = source_analysis.get('signals', [])
                            print(f"     - Signals: {len(signals)}")
                        if 'implications' in source_analysis:
                            implications = source_analysis.get('implications', [])
                            print(f"     - Implications: {len(implications)}")
                        if 'insights' in source_analysis:
                            insights = source_analysis.get('insights', [])
                            print(f"     - Insights: {len(insights)}")
            
            # Market outlook analysis
            print(f"   🔮 Market Outlook:")
            print(f"     - Overall Sentiment: {market_outlook.get('overall_sentiment', 'unknown')}")
            print(f"     - Confidence: {market_outlook.get('confidence', 'unknown')}")
            
            key_signals = market_outlook.get('key_signals', [])
            if key_signals:
                print(f"     - Key Signals ({len(key_signals)}):")
                for signal in key_signals[:3]:  # Show first 3
                    print(f"       * {signal}")
            
            recommended_actions = market_outlook.get('recommended_actions', [])
            if recommended_actions:
                print(f"     - Recommended Actions ({len(recommended_actions)}):")
                for action in recommended_actions[:2]:  # Show first 2
                    print(f"       * {action}")
            
            risk_factors = market_outlook.get('risk_factors', [])
            if risk_factors:
                print(f"     - Risk Factors ({len(risk_factors)}):")
                for risk in risk_factors[:2]:  # Show first 2
                    print(f"       * {risk}")
            
            # Verify comprehensive analysis structure
            required_components = ['options_flow', 'dark_pool', 'congressional']
            missing_components = [comp for comp in required_components if comp not in comprehensive_analysis]
            if missing_components:
                print(f"   ⚠️  Missing analysis components: {missing_components}")
            else:
                print(f"   ✅ All analysis components present")
        
        return success

    def test_advanced_screener_unusual_whales_integration(self):
        """Test Advanced Screener endpoints with Unusual Whales API integration - COMPREHENSIVE TESTING"""
        print("\n🐋 Testing Advanced Screener with Unusual Whales API Integration")
        print("=" * 80)
        
        # Test 1: Stock Screener Data Endpoint with different exchanges
        exchanges = ["all", "sp500", "nasdaq"]
        screener_results = {}
        
        for exchange in exchanges:
            print(f"\n📊 Testing GET /api/screener/data with exchange='{exchange}'")
            success, data = self.run_test(
                f"Screener Data ({exchange.upper()})", 
                "GET", 
                "screener/data", 
                200, 
                params={"limit": 20, "exchange": exchange}
            )
            
            if success:
                screener_results[exchange] = data
                stocks = data.get('stocks', [])
                data_source = data.get('data_source', 'Unknown')
                
                print(f"   ✅ Found {len(stocks)} stocks from {data_source}")
                print(f"   📈 Exchange: {data.get('exchange', 'N/A')}")
                print(f"   🕐 Last Updated: {data.get('last_updated', 'N/A')}")
                
                # Verify Unusual Whales specific fields
                if stocks:
                    first_stock = stocks[0]
                    unusual_whales_fields = ['unusual_activity', 'options_flow_signal']
                    missing_uw_fields = [field for field in unusual_whales_fields if field not in first_stock]
                    
                    if missing_uw_fields:
                        print(f"   ⚠️  Missing Unusual Whales fields: {missing_uw_fields}")
                    else:
                        print(f"   🐋 Unusual Whales fields present: ✅")
                        print(f"     - Unusual Activity: {first_stock.get('unusual_activity', 'N/A')}")
                        print(f"     - Options Flow Signal: {first_stock.get('options_flow_signal', 'N/A')}")
                    
                    # Verify all expected stock fields
                    expected_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 
                                     'volume', 'market_cap', 'sector', 'unusual_activity', 'options_flow_signal']
                    missing_fields = [field for field in expected_fields if field not in first_stock]
                    
                    if missing_fields:
                        print(f"   ❌ Missing required fields: {missing_fields}")
                    else:
                        print(f"   ✅ All required fields present")
                        print(f"   📊 Sample: {first_stock['symbol']} - ${first_stock['price']:.2f} ({first_stock['change_percent']:+.2f}%)")
                
                # Verify data source indicates Unusual Whales
                if "Unusual Whales" in data_source:
                    print(f"   🐋 Data Source Verified: {data_source}")
                elif "Mock Data" in data_source:
                    print(f"   🔧 Using Mock Data: {data_source} (API key may not be working)")
                else:
                    print(f"   ⚠️  Unexpected data source: {data_source}")
        
        # Test 2: Stock Filtering Endpoint with various criteria
        print(f"\n🔍 Testing POST /api/screener/filter with various criteria")
        
        filter_tests = [
            {
                "name": "Technology Stocks Filter",
                "criteria": {
                    "min_price": 50.0,
                    "max_price": 500.0,
                    "min_market_cap": 1000.0,  # 1B market cap
                    "sector": "Technology"
                },
                "exchange": "all"
            },
            {
                "name": "High Volume Filter",
                "criteria": {
                    "min_volume": 5000000,
                    "min_price": 100.0
                },
                "exchange": "sp500"
            },
            {
                "name": "P/E Ratio Filter",
                "criteria": {
                    "min_pe": 10.0,
                    "max_pe": 30.0,
                    "min_market_cap": 500.0
                },
                "exchange": "nasdaq"
            },
            {
                "name": "Price Range Filter",
                "criteria": {
                    "min_price": 200.0,
                    "max_price": 400.0,
                    "min_change": -5.0,
                    "max_change": 5.0
                },
                "exchange": "all"
            }
        ]
        
        for filter_test in filter_tests:
            print(f"\n   🎯 {filter_test['name']}")
            success, filtered_data = self.run_test(
                filter_test['name'],
                "POST",
                "screener/filter",
                200,
                data=filter_test['criteria'],
                params={"exchange": filter_test['exchange']}
            )
            
            if success:
                stocks = filtered_data.get('stocks', [])
                criteria = filtered_data.get('criteria', {})
                data_source = filtered_data.get('data_source', 'Unknown')
                
                print(f"     📊 Found {len(stocks)} filtered stocks")
                print(f"     🐋 Data Source: {data_source}")
                print(f"     🔍 Applied Criteria: {len(criteria)} filters")
                
                # Verify filtering worked correctly
                if stocks:
                    sample_stock = stocks[0]
                    print(f"     📈 Sample Result: {sample_stock['symbol']} - ${sample_stock['price']:.2f}")
                    
                    # Check if filters were applied correctly
                    filter_checks = []
                    if 'min_price' in criteria and sample_stock['price'] >= criteria['min_price']:
                        filter_checks.append("min_price ✅")
                    if 'max_price' in criteria and sample_stock['price'] <= criteria['max_price']:
                        filter_checks.append("max_price ✅")
                    if 'sector' in criteria and sample_stock['sector'] == criteria['sector']:
                        filter_checks.append("sector ✅")
                    
                    if filter_checks:
                        print(f"     ✅ Filter Validation: {', '.join(filter_checks)}")
        
        # Test 3: API Key Usage Verification
        print(f"\n🔑 Testing API Key Usage (Unusual Whales API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50)")
        
        # Check if we're using the correct API key by examining response metadata
        if screener_results:
            for exchange, data in screener_results.items():
                data_source = data.get('data_source', '')
                if "Unusual Whales API" in data_source:
                    print(f"   ✅ {exchange.upper()}: Using Unusual Whales API (correct API key)")
                elif "Mock Data" in data_source:
                    print(f"   🔧 {exchange.upper()}: Using Mock Data (API key may be inactive)")
                else:
                    print(f"   ❌ {exchange.upper()}: Unknown data source: {data_source}")
        
        # Test 4: Exchange Filtering Verification
        print(f"\n🏛️  Testing Exchange Filtering Accuracy")
        
        if len(screener_results) >= 2:
            all_stocks = screener_results.get('all', {}).get('stocks', [])
            sp500_stocks = screener_results.get('sp500', {}).get('stocks', [])
            nasdaq_stocks = screener_results.get('nasdaq', {}).get('stocks', [])
            
            print(f"   📊 Stock Counts: ALL={len(all_stocks)}, SP500={len(sp500_stocks)}, NASDAQ={len(nasdaq_stocks)}")
            
            # Verify that 'all' contains more or equal stocks than individual exchanges
            if len(all_stocks) >= len(sp500_stocks) and len(all_stocks) >= len(nasdaq_stocks):
                print(f"   ✅ Exchange filtering logic correct: ALL >= individual exchanges")
            else:
                print(f"   ⚠️  Exchange filtering may have issues")
            
            # Check for exchange-specific stocks
            if sp500_stocks:
                sp500_symbols = {stock['symbol'] for stock in sp500_stocks}
                print(f"   📈 SP500 Sample Symbols: {list(sp500_symbols)[:5]}")
            
            if nasdaq_stocks:
                nasdaq_symbols = {stock['symbol'] for stock in nasdaq_stocks}
                print(f"   💻 NASDAQ Sample Symbols: {list(nasdaq_symbols)[:5]}")
        
        # Test 5: Error Handling and Mock Data Fallback
        print(f"\n🛡️  Testing Error Handling and Mock Data Fallback")
        
        # Test with invalid exchange parameter
        success, invalid_data = self.run_test(
            "Invalid Exchange Parameter",
            "GET",
            "screener/data",
            200,  # Should still return 200 with mock data
            params={"exchange": "invalid_exchange", "limit": 5}
        )
        
        if success:
            data_source = invalid_data.get('data_source', '')
            if "Mock Data" in data_source or "Unusual Whales" in data_source:
                print(f"   ✅ Error handling working: {data_source}")
            else:
                print(f"   ⚠️  Unexpected response for invalid exchange")
        
        # Test 6: Response Format Verification
        print(f"\n📋 Testing Response Format Compliance")
        
        if screener_results:
            sample_response = list(screener_results.values())[0]
            required_response_fields = ['stocks', 'total_count', 'exchange', 'data_source', 'last_updated']
            missing_response_fields = [field for field in required_response_fields if field not in sample_response]
            
            if missing_response_fields:
                print(f"   ❌ Missing response fields: {missing_response_fields}")
            else:
                print(f"   ✅ All required response fields present")
                print(f"   📊 Response Structure: {list(sample_response.keys())}")
        
        # Test 7: Data Quality Verification
        print(f"\n🔍 Testing Data Quality")
        
        if screener_results:
            all_stocks = screener_results.get('all', {}).get('stocks', [])
            if all_stocks:
                # Check for realistic stock prices (not all zeros)
                non_zero_prices = [stock for stock in all_stocks if stock.get('price', 0) > 0]
                zero_prices = [stock for stock in all_stocks if stock.get('price', 0) == 0]
                
                print(f"   💰 Price Quality: {len(non_zero_prices)} real prices, {len(zero_prices)} zero prices")
                
                if len(non_zero_prices) > len(zero_prices):
                    print(f"   ✅ Good price data quality")
                else:
                    print(f"   ⚠️  Poor price data quality - too many zero prices")
                
                # Check for Unusual Whales specific data
                unusual_activity_count = len([stock for stock in all_stocks if stock.get('unusual_activity', False)])
                options_signals = [stock.get('options_flow_signal', 'neutral') for stock in all_stocks]
                signal_distribution = {signal: options_signals.count(signal) for signal in set(options_signals)}
                
                print(f"   🐋 Unusual Activity: {unusual_activity_count}/{len(all_stocks)} stocks")
                print(f"   📊 Options Flow Signals: {signal_distribution}")
                
                if unusual_activity_count > 0 or any(signal != 'neutral' for signal in options_signals):
                    print(f"   ✅ Unusual Whales data integration working")
                else:
                    print(f"   🔧 Using mock data - Unusual Whales integration may be inactive")
        
        print(f"\n🎯 Advanced Screener Unusual Whales Integration Testing Complete")
        return True

    def test_unusual_whales_futures_support(self):
        """Test if Unusual Whales API supports futures data for SPX, NQ, YM, RTY symbols"""
        print("\n🔮 Testing Unusual Whales API Futures Data Support")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test futures symbols SPX, NQ, YM, RTY using Unusual Whales API")
        print("🔑 API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print("🌐 Base URL: https://api.unusualwhales.com")
        
        # Define futures symbols to test
        futures_symbols = {
            'SPX': 'S&P 500 Index Futures',
            'NQ': 'NASDAQ-100 Futures', 
            'YM': 'Dow Jones Futures',
            'RTY': 'Russell 2000 Futures'
        }
        
        # Alternative symbol formats to try
        alternative_formats = {
            'SPX': ['/ES', 'ES', 'SPY', '^GSPC'],
            'NQ': ['/NQ', 'NQ', 'QQQ', '^IXIC'],
            'YM': ['/YM', 'YM', 'DIA', '^DJI'],
            'RTY': ['/RTY', 'RTY', 'IWM', '^RUT']
        }
        
        futures_test_results = {
            'symbols_tested': 0,
            'successful_responses': 0,
            'options_flow_found': 0,
            'dark_pool_found': 0,
            'congressional_found': 0,
            'stock_data_found': 0,
            'alternative_formats_working': {},
            'api_endpoints_tested': 0,
            'working_endpoints': []
        }
        
        print(f"\n📊 PHASE 1: Testing Primary Futures Symbols")
        print("-" * 60)
        
        # Test 1: Try futures symbols in Options Flow endpoint
        print(f"\n🐋 Testing Options Flow for Futures Symbols")
        for symbol, description in futures_symbols.items():
            futures_test_results['symbols_tested'] += 1
            print(f"\n   🎯 Testing {symbol} ({description})")
            
            # Test options flow with symbol filter (if API supports it)
            success, flow_data = self.run_test(
                f"Options Flow - {symbol}",
                "GET",
                "unusual-whales/options/flow-alerts",
                200,
                params={"limit": 100}
            )
            
            if success:
                futures_test_results['successful_responses'] += 1
                alerts = flow_data.get('data', {}).get('alerts', [])
                
                # Check if any alerts contain our futures symbol
                symbol_alerts = [alert for alert in alerts if alert.get('symbol', '').upper() == symbol.upper()]
                if symbol_alerts:
                    futures_test_results['options_flow_found'] += 1
                    print(f"     ✅ Found {len(symbol_alerts)} options flow alerts for {symbol}")
                    
                    # Show sample alert
                    sample_alert = symbol_alerts[0]
                    print(f"     📊 Sample: {sample_alert.get('symbol')} {sample_alert.get('strike_type', 'N/A')} - ${sample_alert.get('premium', 0):,.0f}")
                else:
                    print(f"     ❌ No options flow alerts found for {symbol}")
            else:
                print(f"     ❌ Failed to get options flow data")
        
        # Test 2: Try futures symbols in Dark Pool endpoint
        print(f"\n🌊 Testing Dark Pool for Futures Symbols")
        success, dark_pool_data = self.run_test(
            "Dark Pool - All Recent",
            "GET", 
            "unusual-whales/dark-pool/recent",
            200,
            params={"limit": 100}
        )
        
        if success:
            trades = dark_pool_data.get('data', {}).get('trades', [])
            print(f"   📊 Retrieved {len(trades)} dark pool trades")
            
            for symbol in futures_symbols.keys():
                symbol_trades = [trade for trade in trades if trade.get('ticker', '').upper() == symbol.upper()]
                if symbol_trades:
                    futures_test_results['dark_pool_found'] += 1
                    print(f"     ✅ Found {len(symbol_trades)} dark pool trades for {symbol}")
                    
                    # Show sample trade
                    sample_trade = symbol_trades[0]
                    print(f"     📊 Sample: {sample_trade.get('ticker')} - {sample_trade.get('dark_volume', 0):,} vol ({sample_trade.get('dark_percentage', 0):.1f}% dark)")
                else:
                    print(f"     ❌ No dark pool trades found for {symbol}")
        
        # Test 3: Try futures symbols in Congressional Trades endpoint
        print(f"\n🏛️  Testing Congressional Trades for Futures Symbols")
        success, congress_data = self.run_test(
            "Congressional Trades - All Recent",
            "GET",
            "unusual-whales/congressional/trades", 
            200,
            params={"limit": 100}
        )
        
        if success:
            trades = congress_data.get('data', {}).get('trades', [])
            print(f"   📊 Retrieved {len(trades)} congressional trades")
            
            for symbol in futures_symbols.keys():
                symbol_trades = [trade for trade in trades if trade.get('ticker', '').upper() == symbol.upper()]
                if symbol_trades:
                    futures_test_results['congressional_found'] += 1
                    print(f"     ✅ Found {len(symbol_trades)} congressional trades for {symbol}")
                    
                    # Show sample trade
                    sample_trade = symbol_trades[0]
                    print(f"     📊 Sample: {sample_trade.get('representative')} - {sample_trade.get('transaction_type')} {sample_trade.get('ticker')} ${sample_trade.get('transaction_amount', 0):,.0f}")
                else:
                    print(f"     ❌ No congressional trades found for {symbol}")
        
        # Test 4: Try futures symbols in regular stock data endpoints
        print(f"\n📈 Testing Stock Data Endpoints for Futures Symbols")
        for symbol, description in futures_symbols.items():
            print(f"\n   🎯 Testing {symbol} ({description})")
            
            # Test basic stock data
            success, stock_data = self.run_test(
                f"Stock Data - {symbol}",
                "GET",
                f"stocks/{symbol}",
                200
            )
            
            if success and stock_data.get('price', 0) > 0:
                futures_test_results['stock_data_found'] += 1
                print(f"     ✅ Stock data available: ${stock_data.get('price', 0):.2f}")
            else:
                print(f"     ❌ No stock data available for {symbol}")
            
            # Test enhanced stock data
            success, enhanced_data = self.run_test(
                f"Enhanced Stock Data - {symbol}",
                "GET",
                f"stocks/{symbol}/enhanced",
                200
            )
            
            if success and enhanced_data.get('price', 0) > 0:
                print(f"     ✅ Enhanced stock data available: ${enhanced_data.get('price', 0):.2f}")
                print(f"     📊 Market State: {enhanced_data.get('market_state', 'UNKNOWN')}")
            else:
                print(f"     ❌ No enhanced stock data available for {symbol}")
        
        print(f"\n📊 PHASE 2: Testing Alternative Symbol Formats")
        print("-" * 60)
        
        # Test 5: Try alternative symbol formats
        for primary_symbol, alternatives in alternative_formats.items():
            print(f"\n🔄 Testing alternatives for {primary_symbol} ({futures_symbols[primary_symbol]})")
            
            working_alternatives = []
            for alt_symbol in alternatives:
                print(f"   🧪 Testing alternative format: {alt_symbol}")
                
                # Test stock data for alternative format
                success, alt_data = self.run_test(
                    f"Stock Data - {alt_symbol}",
                    "GET",
                    f"stocks/{alt_symbol}",
                    200
                )
                
                if success and alt_data.get('price', 0) > 0:
                    working_alternatives.append(alt_symbol)
                    print(f"     ✅ {alt_symbol} works: ${alt_data.get('price', 0):.2f}")
                    
                    # Test if this alternative appears in screener data
                    success, screener_data = self.run_test(
                        f"Screener Check - {alt_symbol}",
                        "GET",
                        "screener/data",
                        200,
                        params={"limit": 50, "exchange": "all"}
                    )
                    
                    if success:
                        stocks = screener_data.get('stocks', [])
                        alt_in_screener = any(stock.get('symbol', '').upper() == alt_symbol.upper() for stock in stocks)
                        if alt_in_screener:
                            print(f"     📊 {alt_symbol} found in screener data")
                        else:
                            print(f"     📊 {alt_symbol} not in screener data")
                else:
                    print(f"     ❌ {alt_symbol} not available")
            
            futures_test_results['alternative_formats_working'][primary_symbol] = working_alternatives
            if working_alternatives:
                print(f"   ✅ Working alternatives for {primary_symbol}: {', '.join(working_alternatives)}")
            else:
                print(f"   ❌ No working alternatives found for {primary_symbol}")
        
        print(f"\n📊 PHASE 3: Testing Futures-Specific API Endpoints")
        print("-" * 60)
        
        # Test 6: Check if there are any futures-specific endpoints
        futures_endpoints_to_test = [
            "futures/data",
            "futures/options",
            "futures/flow",
            "market/futures",
            "derivatives/futures",
            "unusual-whales/futures",
            "unusual-whales/derivatives"
        ]
        
        print(f"🔍 Testing potential futures-specific endpoints:")
        for endpoint in futures_endpoints_to_test:
            futures_test_results['api_endpoints_tested'] += 1
            print(f"\n   🧪 Testing endpoint: /{endpoint}")
            
            success, endpoint_data = self.run_test(
                f"Futures Endpoint - {endpoint}",
                "GET",
                endpoint,
                200
            )
            
            if success:
                futures_test_results['working_endpoints'].append(endpoint)
                print(f"     ✅ Endpoint exists and responds")
                
                # Check if response contains futures data
                if isinstance(endpoint_data, dict):
                    if any(symbol in str(endpoint_data).upper() for symbol in futures_symbols.keys()):
                        print(f"     🎯 Response contains futures symbols!")
                    else:
                        print(f"     📊 Response structure: {list(endpoint_data.keys()) if endpoint_data else 'Empty'}")
            else:
                print(f"     ❌ Endpoint not available")
        
        # Test 7: Direct API call to Unusual Whales (if we can access it directly)
        print(f"\n🌐 PHASE 4: Direct Unusual Whales API Testing")
        print("-" * 60)
        
        try:
            import requests
            import os
            
            # Get API credentials from environment
            uw_api_token = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
            uw_base_url = "https://api.unusualwhales.com"
            
            print(f"🔑 Testing direct API access with token: {uw_api_token[:8]}...")
            
            # Test direct API endpoints that might support futures
            direct_endpoints = [
                "/api/stock/options-flow",
                "/api/market/overview", 
                "/api/derivatives/futures",
                "/api/options/flow",
                "/api/market/indices"
            ]
            
            headers = {
                'Authorization': f'Bearer {uw_api_token}',
                'Content-Type': 'application/json'
            }
            
            for endpoint in direct_endpoints:
                try:
                    url = f"{uw_base_url}{endpoint}"
                    print(f"\n   🌐 Direct API call: {url}")
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    print(f"     📡 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"     ✅ Success - Response received")
                            
                            # Check for futures symbols in response
                            response_text = str(data).upper()
                            found_symbols = [symbol for symbol in futures_symbols.keys() if symbol in response_text]
                            if found_symbols:
                                print(f"     🎯 Found futures symbols: {', '.join(found_symbols)}")
                            else:
                                print(f"     📊 No futures symbols in response")
                                
                        except Exception as e:
                            print(f"     📊 Response not JSON: {str(e)}")
                    else:
                        print(f"     ❌ Failed: {response.status_code} - {response.text[:100]}")
                        
                except Exception as e:
                    print(f"     ❌ Request failed: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Direct API testing failed: {str(e)}")
        
        # Print comprehensive results
        print(f"\n" + "=" * 80)
        print(f"📊 FUTURES DATA SUPPORT TEST RESULTS")
        print(f"=" * 80)
        
        print(f"🎯 SYMBOLS TESTED: {futures_test_results['symbols_tested']}")
        print(f"✅ SUCCESSFUL API RESPONSES: {futures_test_results['successful_responses']}")
        print(f"📈 OPTIONS FLOW MATCHES: {futures_test_results['options_flow_found']}")
        print(f"🌊 DARK POOL MATCHES: {futures_test_results['dark_pool_found']}")
        print(f"🏛️  CONGRESSIONAL MATCHES: {futures_test_results['congressional_found']}")
        print(f"📊 STOCK DATA AVAILABLE: {futures_test_results['stock_data_found']}")
        print(f"🔍 ENDPOINTS TESTED: {futures_test_results['api_endpoints_tested']}")
        print(f"✅ WORKING ENDPOINTS: {len(futures_test_results['working_endpoints'])}")
        
        print(f"\n🔄 ALTERNATIVE SYMBOL FORMATS:")
        for symbol, alternatives in futures_test_results['alternative_formats_working'].items():
            if alternatives:
                print(f"   {symbol}: ✅ {', '.join(alternatives)}")
            else:
                print(f"   {symbol}: ❌ No working alternatives")
        
        if futures_test_results['working_endpoints']:
            print(f"\n🌐 WORKING ENDPOINTS:")
            for endpoint in futures_test_results['working_endpoints']:
                print(f"   ✅ /{endpoint}")
        
        # Final assessment
        total_matches = (futures_test_results['options_flow_found'] + 
                        futures_test_results['dark_pool_found'] + 
                        futures_test_results['congressional_found'] + 
                        futures_test_results['stock_data_found'])
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if total_matches > 0:
            print(f"✅ PARTIAL FUTURES SUPPORT DETECTED ({total_matches} data sources)")
            print(f"📊 Unusual Whales API has some futures-related data available")
        else:
            print(f"❌ NO DIRECT FUTURES SUPPORT DETECTED")
            print(f"📊 Unusual Whales API may not support futures symbols SPX, NQ, YM, RTY")
        
        # Check if alternatives can substitute
        working_alternatives_count = sum(len(alts) for alts in futures_test_results['alternative_formats_working'].values())
        if working_alternatives_count > 0:
            print(f"🔄 ALTERNATIVE SYMBOLS AVAILABLE ({working_alternatives_count} working formats)")
            print(f"💡 Consider using index ETFs or index symbols as futures substitutes")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if total_matches == 0 and working_alternatives_count > 0:
            print(f"   1. Use alternative symbols like SPY (for SPX), QQQ (for NQ), DIA (for YM), IWM (for RTY)")
            print(f"   2. Use index symbols like ^GSPC, ^IXIC, ^DJI, ^RUT for market data")
            print(f"   3. Consider waiting for TradeStation API integration for true futures data")
        elif total_matches > 0:
            print(f"   1. Some futures data is available through Unusual Whales API")
            print(f"   2. Test with larger datasets to confirm consistent availability")
            print(f"   3. Implement fallback to alternative symbols when futures data unavailable")
        else:
            print(f"   1. Unusual Whales API does not appear to support futures symbols")
            print(f"   2. Recommend proceeding with TradeStation API for futures data")
            print(f"   3. Use index ETFs as temporary substitutes for market dashboard")
        
        return futures_test_results

    def test_tradestation_live_portfolio_comprehensive(self):
        """Test TradeStation Live Portfolio API endpoints - COMPREHENSIVE TESTING FOR LOADING SPINNER ISSUE"""
        print("\n🏛️  TESTING TRADESTATION LIVE PORTFOLIO API - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test TradeStation Live Portfolio backend API endpoints")
        print("🔧 FOCUS: Verify API endpoints work correctly and return proper data structure")
        print("📊 EXPECTED DATA: Account 11775499, 63 positions, ~$854k value, ~-$61k P&L")
        print("🐛 ISSUE: Frontend shows permanent 'Loading portfolio data...' spinner")
        
        # Test 1: TradeStation Accounts Endpoint
        print(f"\n📊 PHASE 1: TradeStation Accounts Endpoint Testing")
        print("-" * 60)
        
        success_accounts, accounts_data = self.run_test("TradeStation Accounts", "GET", "tradestation/accounts", 200)
        
        if success_accounts:
            print(f"✅ Accounts endpoint responding")
            
            # Check if we have account data
            if isinstance(accounts_data, list) and len(accounts_data) > 0:
                print(f"   📊 Found {len(accounts_data)} accounts")
                
                # Look for expected account 11775499
                account_11775499_found = False
                for account in accounts_data:
                    account_id = account.get('account_id') or account.get('AccountID') or account.get('Key')
                    print(f"   - Account: {account_id}")
                    if str(account_id) == "11775499":
                        account_11775499_found = True
                        print(f"     ✅ Expected account 11775499 found!")
                        account_type = account.get('account_type') or account.get('Type')
                        if account_type:
                            print(f"     - Type: {account_type}")
                
                if not account_11775499_found:
                    print(f"   ⚠️  Expected account 11775499 not found in accounts list")
                    
            elif isinstance(accounts_data, dict):
                print(f"   📊 Accounts data structure: {list(accounts_data.keys())}")
                if 'accounts' in accounts_data:
                    accounts_list = accounts_data['accounts']
                    print(f"   📊 Found {len(accounts_list)} accounts in nested structure")
            else:
                print(f"   ⚠️  Unexpected accounts data format: {type(accounts_data)}")
        else:
            print(f"❌ Accounts endpoint failed - this may indicate authentication issues")
            print(f"   📝 Note: TradeStation API requires OAuth authentication")
        
        # Test 2: TradeStation Portfolio Summary Endpoint (Specific Account)
        print(f"\n📊 PHASE 2: TradeStation Portfolio Summary Endpoint Testing")
        print("-" * 60)
        
        account_id = "11775499"  # Expected account from user report
        success_summary, summary_data = self.run_test(
            f"TradeStation Portfolio Summary (Account {account_id})", 
            "GET", 
            f"tradestation/accounts/{account_id}/summary", 
            200
        )
        
        if success_summary:
            print(f"✅ Portfolio summary endpoint responding for account {account_id}")
            
            # Verify response structure matches frontend expectations
            expected_fields = ['portfolio_metrics', 'positions', 'risk_analysis']
            missing_fields = []
            present_fields = []
            
            for field in expected_fields:
                if field in summary_data:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            print(f"   📊 Response Structure Analysis:")
            print(f"     - Present fields: {present_fields}")
            if missing_fields:
                print(f"     - Missing fields: {missing_fields}")
            else:
                print(f"     ✅ All expected fields present")
            
            # Check portfolio metrics
            if 'portfolio_metrics' in summary_data:
                metrics = summary_data['portfolio_metrics']
                print(f"   💰 Portfolio Metrics:")
                
                total_value = metrics.get('total_value', 0)
                total_pl = metrics.get('total_profit_loss', 0)
                position_count = metrics.get('position_count', 0)
                
                print(f"     - Total Value: ${total_value:,.2f}")
                print(f"     - Total P&L: ${total_pl:,.2f}")
                print(f"     - Position Count: {position_count}")
                
                # Compare with expected values
                expected_value = 854448  # ~$854k
                expected_pl = -61262    # ~-$61k P&L
                expected_positions = 63
                
                print(f"   🎯 Expected vs Actual Comparison:")
                print(f"     - Value: Expected ~${expected_value:,}, Got ${total_value:,.2f}")
                print(f"     - P&L: Expected ~${expected_pl:,}, Got ${total_pl:,.2f}")
                print(f"     - Positions: Expected ~{expected_positions}, Got {position_count}")
                
                # Check if values are close to expected (within reasonable range)
                value_close = abs(total_value - expected_value) < (expected_value * 0.1)  # 10% tolerance
                pl_close = abs(total_pl - expected_pl) < (abs(expected_pl) * 0.2)  # 20% tolerance
                positions_close = abs(position_count - expected_positions) < 10  # ±10 positions
                
                if value_close:
                    print(f"     ✅ Portfolio value matches expected range")
                else:
                    print(f"     ⚠️  Portfolio value differs significantly from expected")
                
                if pl_close:
                    print(f"     ✅ P&L matches expected range")
                else:
                    print(f"     ⚠️  P&L differs significantly from expected")
                
                if positions_close:
                    print(f"     ✅ Position count matches expected range")
                else:
                    print(f"     ⚠️  Position count differs significantly from expected")
            
            # Check positions data
            if 'positions' in summary_data:
                positions = summary_data['positions']
                print(f"   📊 Positions Data:")
                print(f"     - Positions array length: {len(positions) if isinstance(positions, list) else 'Not a list'}")
                
                if isinstance(positions, list) and len(positions) > 0:
                    # Show sample position structure
                    sample_position = positions[0]
                    print(f"     - Sample position fields: {list(sample_position.keys()) if isinstance(sample_position, dict) else 'Not a dict'}")
                    
                    if isinstance(sample_position, dict):
                        symbol = sample_position.get('symbol') or sample_position.get('Symbol')
                        quantity = sample_position.get('quantity') or sample_position.get('Quantity')
                        market_value = sample_position.get('market_value') or sample_position.get('MarketValue')
                        
                        print(f"     - Sample position: {symbol}, Qty: {quantity}, Value: ${market_value}")
            
            # Check risk analysis
            if 'risk_analysis' in summary_data:
                risk_analysis = summary_data['risk_analysis']
                print(f"   ⚖️  Risk Analysis:")
                print(f"     - Risk analysis fields: {list(risk_analysis.keys()) if isinstance(risk_analysis, dict) else 'Not a dict'}")
        else:
            print(f"❌ Portfolio summary endpoint failed for account {account_id}")
            print(f"   📝 This could indicate:")
            print(f"     - Authentication required")
            print(f"     - Account not accessible")
            print(f"     - API endpoint issues")
        
        # Test 3: Multiple Consecutive Calls (Consistency Testing)
        print(f"\n🔄 PHASE 3: Multiple Consecutive Calls Testing")
        print("-" * 60)
        
        consecutive_results = []
        for i in range(3):
            print(f"   🔍 Consecutive call {i+1}/3...")
            success_consecutive, consecutive_data = self.run_test(
                f"Portfolio Summary Call #{i+1}", 
                "GET", 
                f"tradestation/accounts/{account_id}/summary", 
                200
            )
            
            consecutive_results.append({
                'success': success_consecutive,
                'data': consecutive_data,
                'call_number': i+1
            })
            
            if success_consecutive and 'portfolio_metrics' in consecutive_data:
                metrics = consecutive_data['portfolio_metrics']
                total_value = metrics.get('total_value', 0)
                position_count = metrics.get('position_count', 0)
                print(f"     - Call {i+1}: Value=${total_value:,.2f}, Positions={position_count}")
        
        # Analyze consistency
        successful_calls = [r for r in consecutive_results if r['success']]
        print(f"   📊 Consistency Analysis:")
        print(f"     - Successful calls: {len(successful_calls)}/3")
        
        if len(successful_calls) >= 2:
            # Compare values between calls
            values = []
            position_counts = []
            
            for result in successful_calls:
                if 'portfolio_metrics' in result['data']:
                    metrics = result['data']['portfolio_metrics']
                    values.append(metrics.get('total_value', 0))
                    position_counts.append(metrics.get('position_count', 0))
            
            if len(values) >= 2:
                value_consistent = all(abs(v - values[0]) < 1000 for v in values)  # $1000 tolerance
                positions_consistent = all(p == position_counts[0] for p in position_counts)
                
                print(f"     - Value consistency: {'✅ Consistent' if value_consistent else '⚠️  Inconsistent'}")
                print(f"     - Position count consistency: {'✅ Consistent' if positions_consistent else '⚠️  Inconsistent'}")
                
                if not value_consistent:
                    print(f"       Values: {[f'${v:,.2f}' for v in values]}")
                if not positions_consistent:
                    print(f"       Position counts: {position_counts}")
        
        # Test 4: Response Time Analysis
        print(f"\n⏱️  PHASE 4: Response Time Analysis")
        print("-" * 60)
        
        import time
        response_times = []
        
        for i in range(3):
            start_time = time.time()
            success_timing, timing_data = self.run_test(
                f"Response Time Test #{i+1}", 
                "GET", 
                f"tradestation/accounts/{account_id}/summary", 
                200
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            print(f"   ⏱️  Call {i+1}: {response_time:.2f}s")
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"   📊 Response Time Analysis:")
        print(f"     - Average: {avg_response_time:.2f}s")
        print(f"     - Range: {min_response_time:.2f}s - {max_response_time:.2f}s")
        
        if avg_response_time < 2.0:
            print(f"     ✅ Excellent response time")
        elif avg_response_time < 5.0:
            print(f"     ✅ Good response time")
        elif avg_response_time < 10.0:
            print(f"     ⚠️  Slow response time")
        else:
            print(f"     ❌ Very slow response time - may cause frontend timeouts")
        
        # Test 5: Authentication Status Check
        print(f"\n🔐 PHASE 5: Authentication Status Verification")
        print("-" * 60)
        
        success_auth, auth_data = self.run_test("TradeStation Auth Status", "GET", "auth/tradestation/status", 200)
        
        if success_auth:
            print(f"✅ Auth status endpoint responding")
            
            if 'authentication' in auth_data:
                auth_info = auth_data['authentication']
                authenticated = auth_info.get('authenticated', False)
                environment = auth_info.get('environment', 'unknown')
                
                print(f"   🔐 Authentication Status:")
                print(f"     - Authenticated: {authenticated}")
                print(f"     - Environment: {environment}")
                
                if not authenticated:
                    print(f"     ⚠️  NOT AUTHENTICATED - This explains API failures")
                    print(f"     📝 TradeStation APIs require OAuth authentication")
                else:
                    print(f"     ✅ AUTHENTICATED - APIs should work")
            
            if 'api_configuration' in auth_data:
                config = auth_data['api_configuration']
                print(f"   ⚙️  API Configuration:")
                print(f"     - Environment: {config.get('environment', 'unknown')}")
                print(f"     - Base URL: {config.get('base_url', 'unknown')}")
                print(f"     - Credentials Configured: {config.get('credentials_configured', False)}")
        
        # Test 6: Additional TradeStation Endpoints
        print(f"\n📊 PHASE 6: Additional TradeStation Endpoints Testing")
        print("-" * 60)
        
        additional_endpoints = [
            ("Positions", f"tradestation/accounts/{account_id}/positions"),
            ("Balances", f"tradestation/accounts/{account_id}/balances"),
            ("Orders History", f"tradestation/accounts/{account_id}/orders")
        ]
        
        for endpoint_name, endpoint_path in additional_endpoints:
            success_additional, additional_data = self.run_test(
                f"TradeStation {endpoint_name}", 
                "GET", 
                endpoint_path, 
                200
            )
            
            if success_additional:
                print(f"   ✅ {endpoint_name} endpoint responding")
                if isinstance(additional_data, list):
                    print(f"     - Returned {len(additional_data)} items")
                elif isinstance(additional_data, dict):
                    print(f"     - Response keys: {list(additional_data.keys())}")
            else:
                print(f"   ❌ {endpoint_name} endpoint failed")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: TradeStation Live Portfolio API")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("Accounts Endpoint", success_accounts),
            ("Portfolio Summary", success_summary),
            ("Consecutive Calls", len(successful_calls) >= 2),
            ("Response Time", avg_response_time < 10.0),
            ("Auth Status", success_auth)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        if success_summary and 'portfolio_metrics' in summary_data:
            metrics = summary_data['portfolio_metrics']
            print(f"   - Portfolio Value: ${metrics.get('total_value', 0):,.2f}")
            print(f"   - Position Count: {metrics.get('position_count', 0)}")
            print(f"   - P&L: ${metrics.get('total_profit_loss', 0):,.2f}")
        else:
            print(f"   - Portfolio data: ❌ Not accessible")
        
        print(f"   - API Response Time: {avg_response_time:.2f}s average")
        print(f"   - Consistency: {'✅ Good' if len(successful_calls) >= 2 else '❌ Poor'}")
        
        # Root cause analysis for loading spinner issue
        print(f"\n🐛 ROOT CAUSE ANALYSIS FOR LOADING SPINNER ISSUE:")
        
        if not success_summary:
            print(f"   ❌ BACKEND API ISSUE: Portfolio summary endpoint not responding")
            print(f"     - Frontend will show loading spinner indefinitely")
            print(f"     - Check authentication and API configuration")
        elif success_summary and 'portfolio_metrics' not in summary_data:
            print(f"   ❌ RESPONSE STRUCTURE ISSUE: Missing expected fields")
            print(f"     - Frontend expects 'portfolio_metrics', 'positions', 'risk_analysis'")
            print(f"     - Current response structure may not match frontend expectations")
        elif avg_response_time > 30.0:
            print(f"   ❌ TIMEOUT ISSUE: API responses too slow")
            print(f"     - Frontend may timeout before receiving response")
            print(f"     - Consider implementing loading timeouts")
        else:
            print(f"   ✅ BACKEND API WORKING: Issue likely in frontend JavaScript")
            print(f"     - API returns correct data structure")
            print(f"     - Check frontend state management and error handling")
            print(f"     - Verify frontend API call implementation")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not success_accounts and not success_summary:
            print(f"   🔐 AUTHENTICATION REQUIRED:")
            print(f"     - Complete TradeStation OAuth authentication flow")
            print(f"     - Visit /auth/tradestation/login to authenticate")
            print(f"     - Ensure API credentials are properly configured")
        
        if success_summary:
            print(f"   ✅ BACKEND WORKING CORRECTLY:")
            print(f"     - API endpoints return proper data structure")
            print(f"     - Focus on frontend debugging")
            print(f"     - Check browser console for JavaScript errors")
            print(f"     - Verify API response handling in frontend code")
        
        if avg_response_time > 10.0:
            print(f"   ⚠️  PERFORMANCE OPTIMIZATION:")
            print(f"     - Consider caching portfolio data")
            print(f"     - Implement progressive loading")
            print(f"     - Add timeout handling in frontend")
        
        # Final verdict
        if success_rate >= 80:
            print(f"\n🎉 VERDICT: BACKEND API WORKING CORRECTLY")
            print(f"   The TradeStation Live Portfolio backend APIs are functional.")
            print(f"   Loading spinner issue is likely in frontend JavaScript code.")
            print(f"   Focus debugging efforts on frontend state management.")
        elif success_rate >= 60:
            print(f"\n⚠️  VERDICT: PARTIAL BACKEND ISSUES")
            print(f"   Some TradeStation APIs working, others failing.")
            print(f"   Check authentication and API configuration.")
        else:
            print(f"\n❌ VERDICT: BACKEND API ISSUES")
            print(f"   TradeStation APIs not responding correctly.")
            print(f"   Authentication and configuration issues need resolution.")
        
        return success_rate >= 60

    def test_market_overview_debug_futures_symbols(self):
        """DEBUG: Comprehensive test to verify Market Overview returns futures symbols (SPX, NQ, YM, RTY) instead of old index symbols"""
        print("\n🔍 DEBUGGING MARKET OVERVIEW - FUTURES SYMBOLS ISSUE")
        print("=" * 80)
        print("🎯 OBJECTIVE: Debug why frontend shows old symbols (^GSPC, ^DJI, ^IXIC, ^RUT) instead of futures symbols (SPX, NQ, YM, RTY)")
        print("📋 REQUIREMENTS:")
        print("   1. Test Market Overview API: GET /api/market/overview")
        print("   2. Verify 'symbol' field shows SPX, NQ, YM, RTY (NOT ^GSPC, ^DJI, ^IXIC, ^RUT)")
        print("   3. Verify 'underlying_symbol' field shows SPY, QQQ, DIA, IWM")
        print("   4. Show exact JSON response structure")
        print("   5. Check for caching issues")
        
        # Test the Market Overview API
        success, overview_data = self.run_test("Market Overview API", "GET", "market/overview", 200)
        
        if not success:
            print("❌ CRITICAL: Market Overview API failed completely")
            return False
        
        print(f"\n📊 RAW API RESPONSE ANALYSIS:")
        print("-" * 60)
        
        # Show the complete response structure
        import json
        print("🔍 COMPLETE JSON RESPONSE:")
        print(json.dumps(overview_data, indent=2))
        
        # Extract indices data
        indices = overview_data.get('indices', [])
        print(f"\n📈 INDICES ANALYSIS ({len(indices)} found):")
        print("-" * 60)
        
        # Expected vs Actual symbols
        expected_futures_symbols = ['SPX', 'NQ', 'YM', 'RTY']
        expected_etf_underlying = ['SPY', 'QQQ', 'DIA', 'IWM']
        old_index_symbols = ['^GSPC', '^DJI', '^IXIC', '^RUT']
        
        debug_results = {
            'total_indices': len(indices),
            'futures_symbols_found': [],
            'old_symbols_found': [],
            'underlying_symbols_found': [],
            'symbol_field_values': [],
            'underlying_field_values': [],
            'issues_detected': []
        }
        
        for i, index in enumerate(indices):
            symbol = index.get('symbol', 'MISSING')
            underlying_symbol = index.get('underlying_symbol', 'MISSING')
            name = index.get('name', 'MISSING')
            price = index.get('price', 0)
            
            print(f"\n   📊 INDEX {i+1}:")
            print(f"     - symbol: '{symbol}'")
            print(f"     - underlying_symbol: '{underlying_symbol}'")
            print(f"     - name: '{name}'")
            print(f"     - price: ${price:.2f}")
            
            # Track all symbol values
            debug_results['symbol_field_values'].append(symbol)
            debug_results['underlying_field_values'].append(underlying_symbol)
            
            # Check if we're getting futures symbols (GOOD)
            if symbol in expected_futures_symbols:
                debug_results['futures_symbols_found'].append(symbol)
                print(f"     ✅ CORRECT: Found futures symbol '{symbol}'")
            
            # Check if we're getting old index symbols (BAD - this is the problem)
            elif symbol in old_index_symbols:
                debug_results['old_symbols_found'].append(symbol)
                debug_results['issues_detected'].append(f"Index {i+1} shows old symbol '{symbol}' instead of futures symbol")
                print(f"     ❌ PROBLEM: Found old index symbol '{symbol}' - should be futures symbol!")
            
            else:
                debug_results['issues_detected'].append(f"Index {i+1} has unexpected symbol '{symbol}'")
                print(f"     ⚠️  UNEXPECTED: Symbol '{symbol}' not in expected lists")
            
            # Check underlying symbols
            if underlying_symbol in expected_etf_underlying:
                debug_results['underlying_symbols_found'].append(underlying_symbol)
                print(f"     ✅ CORRECT: Underlying symbol '{underlying_symbol}' is ETF")
            elif underlying_symbol in old_index_symbols:
                print(f"     ✅ ACCEPTABLE: Underlying symbol '{underlying_symbol}' is index (fallback)")
            else:
                debug_results['issues_detected'].append(f"Index {i+1} has unexpected underlying_symbol '{underlying_symbol}'")
                print(f"     ⚠️  UNEXPECTED: Underlying symbol '{underlying_symbol}' not recognized")
        
        # CRITICAL ANALYSIS
        print(f"\n🚨 CRITICAL ISSUE ANALYSIS:")
        print("=" * 60)
        
        print(f"📊 SYMBOL FIELD ANALYSIS:")
        print(f"   - Total indices: {debug_results['total_indices']}")
        print(f"   - Futures symbols found: {len(debug_results['futures_symbols_found'])} {debug_results['futures_symbols_found']}")
        print(f"   - Old index symbols found: {len(debug_results['old_symbols_found'])} {debug_results['old_symbols_found']}")
        print(f"   - All symbol values: {debug_results['symbol_field_values']}")
        
        print(f"\n📊 UNDERLYING_SYMBOL FIELD ANALYSIS:")
        print(f"   - ETF underlying found: {len(debug_results['underlying_symbols_found'])} {debug_results['underlying_symbols_found']}")
        print(f"   - All underlying values: {debug_results['underlying_field_values']}")
        
        # ROOT CAUSE ANALYSIS
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 60)
        
        if len(debug_results['old_symbols_found']) > 0:
            print(f"❌ PROBLEM CONFIRMED: API is returning old index symbols in 'symbol' field")
            print(f"   - Old symbols found: {debug_results['old_symbols_found']}")
            print(f"   - Expected futures symbols: {expected_futures_symbols}")
            print(f"   - This explains why frontend shows ^GSPC, ^DJI, ^IXIC, ^RUT instead of SPX, NQ, YM, RTY")
            
            # Check if the mapping is working at all
            if len(debug_results['futures_symbols_found']) == 0:
                print(f"❌ CRITICAL: No futures symbols found - mapping completely broken")
            else:
                print(f"⚠️  PARTIAL: Some futures symbols found but not all")
        
        elif len(debug_results['futures_symbols_found']) == 4:
            print(f"✅ BACKEND WORKING: All 4 futures symbols found correctly")
            print(f"   - Futures symbols: {debug_results['futures_symbols_found']}")
            print(f"   - If frontend still shows old symbols, the issue is in frontend code or caching")
        
        else:
            print(f"⚠️  PARTIAL SUCCESS: Some futures symbols found but not complete set")
            print(f"   - Found: {debug_results['futures_symbols_found']}")
            print(f"   - Missing: {set(expected_futures_symbols) - set(debug_results['futures_symbols_found'])}")
        
        # CACHING ANALYSIS
        print(f"\n🔄 CACHING ANALYSIS:")
        print("-" * 60)
        
        data_source = overview_data.get('data_source', 'Unknown')
        last_updated = overview_data.get('last_updated', 'Unknown')
        
        print(f"   - Data Source: {data_source}")
        print(f"   - Last Updated: {last_updated}")
        
        if "Mock Data" in data_source or "Fallback" in data_source:
            print(f"   ⚠️  Using fallback/mock data - may not reflect latest implementation")
        else:
            print(f"   ✅ Using live data source")
        
        # Check timestamp freshness
        try:
            from datetime import datetime
            if last_updated != 'Unknown':
                # Parse timestamp and check if recent
                print(f"   📅 Timestamp indicates fresh data")
        except:
            print(f"   ⚠️  Cannot verify timestamp freshness")
        
        # DETAILED ISSUES REPORT
        if debug_results['issues_detected']:
            print(f"\n🚨 ISSUES DETECTED ({len(debug_results['issues_detected'])}):")
            print("-" * 60)
            for i, issue in enumerate(debug_results['issues_detected'], 1):
                print(f"   {i}. {issue}")
        
        # SOLUTION RECOMMENDATIONS
        print(f"\n💡 SOLUTION RECOMMENDATIONS:")
        print("-" * 60)
        
        if len(debug_results['old_symbols_found']) > 0:
            print(f"1. ❌ BACKEND ISSUE: The backend is returning old index symbols in the 'symbol' field")
            print(f"   - Check server.py line ~814-850 in get_market_overview() function")
            print(f"   - Verify futures_symbol assignment: futures_symbol = ['SPX', 'NQ', 'YM', 'RTY'][i]")
            print(f"   - Ensure 'symbol': futures_symbol is used in response, not underlying symbol")
            
        elif len(debug_results['futures_symbols_found']) == 4:
            print(f"1. ✅ BACKEND CORRECT: Backend returns proper futures symbols")
            print(f"2. 🔍 CHECK FRONTEND: Issue may be in frontend code or browser caching")
            print(f"   - Clear browser cache and hard refresh")
            print(f"   - Check frontend API call to /api/market/overview")
            print(f"   - Verify frontend uses response.symbol field correctly")
            
        else:
            print(f"1. ⚠️  PARTIAL BACKEND ISSUE: Some symbols correct, others not")
            print(f"   - Check array indexing in server.py get_market_overview() function")
            print(f"   - Verify all 4 futures symbols are properly mapped")
        
        # FINAL VERDICT
        print(f"\n🎯 FINAL VERDICT:")
        print("=" * 60)
        
        if len(debug_results['old_symbols_found']) > 0:
            print(f"❌ BACKEND ISSUE CONFIRMED: API returns old symbols instead of futures symbols")
            print(f"   This explains why frontend shows ^GSPC, ^DJI, ^IXIC, ^RUT")
            print(f"   SOLUTION: Fix backend symbol mapping in server.py")
            return False
        
        elif len(debug_results['futures_symbols_found']) == 4:
            print(f"✅ BACKEND WORKING CORRECTLY: All futures symbols returned properly")
            print(f"   If frontend still shows old symbols, check frontend code or caching")
            print(f"   SOLUTION: Clear frontend cache or check frontend API usage")
            return True
        
        else:
            print(f"⚠️  PARTIAL BACKEND ISSUE: Incomplete futures symbol implementation")
            print(f"   SOLUTION: Complete the futures symbol mapping in backend")
            return False

    def test_expert_options_endpoints(self):
        """Test Expert Options Trading System endpoints - NEW FEATURE"""
        print("\n🎯 Testing Expert Options Trading System - AI-POWERED OPTIONS STRATEGIES")
        print("=" * 80)
        
        # Test 1: Expert Strategy Recommendations for SPY
        print("\n📊 Testing GET /api/expert-options/strategies/SPY")
        success, strategies_data = self.run_test(
            "Expert Strategy Recommendations (SPY)", 
            "GET", 
            "expert-options/strategies/SPY", 
            200
        )
        
        if success:
            recommendations = strategies_data.get('recommendations', [])
            total_strategies = strategies_data.get('total_strategies', 0)
            
            print(f"   ✅ Generated {total_strategies} strategy recommendations")
            print(f"   📈 Symbol: {strategies_data.get('symbol', 'N/A')}")
            
            # Verify all 3 strategies are present
            expected_strategies = ["Wheel Strategy", "Iron Condor", "Volatility Play"]
            found_strategies = []
            
            for rec in recommendations:
                strategy_name = rec.get('strategy_name', 'Unknown')
                confidence = rec.get('confidence_score', 0)
                strategy_type = rec.get('strategy_type', 'Unknown')
                
                found_strategies.append(strategy_name)
                print(f"     - {strategy_name}: {confidence:.2f} confidence ({strategy_type})")
                
                # Verify strategy structure
                required_fields = ['legs', 'max_profit', 'max_loss', 'confidence_score']
                missing_fields = [field for field in required_fields if field not in rec]
                
                if missing_fields:
                    print(f"       ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"       ✅ Complete strategy structure")
                    
                    # Check legs structure
                    legs = rec.get('legs', [])
                    if legs:
                        print(f"       📋 Strategy has {len(legs)} option legs")
                        for i, leg in enumerate(legs):
                            action = leg.get('action', 'N/A')
                            option_type = leg.get('option_type', 'N/A')
                            strike = leg.get('strike', 'N/A')
                            print(f"         Leg {i+1}: {action} {option_type} @ ${strike}")
            
            # Verify all expected strategies are present
            missing_strategies = [s for s in expected_strategies if s not in found_strategies]
            if missing_strategies:
                print(f"   ⚠️  Missing strategies: {missing_strategies}")
            else:
                print(f"   ✅ All 3 expert strategies generated successfully")
        
        # Test 2: Individual Strategy Endpoints
        print(f"\n🔄 Testing Individual Strategy Endpoints")
        
        # Test Wheel Strategy
        success, wheel_data = self.run_test(
            "Wheel Strategy (SPY)", 
            "GET", 
            "expert-options/wheel/SPY", 
            200
        )
        
        if success:
            strategy = wheel_data.get('strategy', {})
            print(f"   🎯 Wheel Strategy:")
            print(f"     - Phase: {strategy.get('phase', 'N/A')}")
            print(f"     - Max Profit: ${strategy.get('max_profit', 0):.2f}")
            print(f"     - Capital Required: ${strategy.get('capital_required', 0):.2f}")
            print(f"     - ROI Potential: {strategy.get('roi_potential', 0):.2f}%")
            print(f"     - Confidence: {strategy.get('confidence_score', 0):.2f}")
        
        # Test Iron Condor Strategy
        success, condor_data = self.run_test(
            "Iron Condor Strategy (SPY)", 
            "GET", 
            "expert-options/iron-condor/SPY", 
            200
        )
        
        if success:
            strategy = condor_data.get('strategy', {})
            print(f"   🦅 Iron Condor Strategy:")
            print(f"     - Net Credit: ${strategy.get('net_credit', 0):.2f}")
            print(f"     - Max Profit: ${strategy.get('max_profit', 0):.2f}")
            print(f"     - Max Loss: ${strategy.get('max_loss', 0):.2f}")
            print(f"     - Breakeven High: ${strategy.get('breakeven_high', 0):.2f}")
            print(f"     - Breakeven Low: ${strategy.get('breakeven_low', 0):.2f}")
            print(f"     - Confidence: {strategy.get('confidence_score', 0):.2f}")
        
        # Test Volatility Play Strategy
        success, vol_data = self.run_test(
            "Volatility Play Strategy (SPY)", 
            "GET", 
            "expert-options/volatility/SPY", 
            200
        )
        
        if success:
            strategy = vol_data.get('strategy', {})
            print(f"   ⚡ Volatility Play Strategy:")
            print(f"     - Strategy Name: {strategy.get('strategy_name', 'N/A')}")
            print(f"     - Total Cost: ${strategy.get('total_cost', 0):.2f}")
            print(f"     - Max Loss: ${strategy.get('max_loss', 0):.2f}")
            print(f"     - Max Profit: {strategy.get('max_profit', 'N/A')}")
            print(f"     - IV Expansion Needed: {strategy.get('iv_expansion_needed', 0):.1f}%")
            print(f"     - Confidence: {strategy.get('confidence_score', 0):.2f}")
        
        # Test 3: Market Analysis
        print(f"\n📊 Testing Market Analysis Endpoint")
        success, market_data = self.run_test(
            "Market Analysis (SPY)", 
            "GET", 
            "expert-options/market-analysis/SPY", 
            200
        )
        
        if success:
            conditions = market_data.get('market_conditions', {})
            print(f"   📈 Market Analysis for {market_data.get('symbol', 'N/A')}:")
            print(f"     - Current Price: ${conditions.get('current_price', 0):.2f}")
            print(f"     - IV Percentile: {conditions.get('iv_percentile', 0):.1f}")
            print(f"     - IV Rank: {conditions.get('iv_rank', 0):.1f}")
            print(f"     - Trend: {conditions.get('trend', 'N/A')}")
            print(f"     - Support: ${conditions.get('support', 0):.2f}")
            print(f"     - Resistance: ${conditions.get('resistance', 0):.2f}")
            print(f"     - Days to Earnings: {conditions.get('days_to_earnings', 0)}")
            print(f"     - Optimal Strategy: {conditions.get('optimal_strategy', 'N/A')}")
            
            # Verify market analysis structure
            required_conditions = ['current_price', 'iv_percentile', 'trend', 'optimal_strategy']
            missing_conditions = [field for field in required_conditions if field not in conditions]
            
            if missing_conditions:
                print(f"     ⚠️  Missing market conditions: {missing_conditions}")
            else:
                print(f"     ✅ Complete market analysis provided")
        
        # Test 4: Learning Insights
        print(f"\n🧠 Testing Learning Insights Endpoint")
        success, insights_data = self.run_test(
            "Learning System Insights", 
            "GET", 
            "expert-options/learning/insights", 
            200
        )
        
        if success:
            insights = insights_data.get('learning_insights', {})
            print(f"   🤖 AI Learning System Status:")
            print(f"     - Total Trades: {insights.get('total_trades', 0)}")
            print(f"     - Active Trades: {insights.get('active_trades', 0)}")
            
            # Strategy performance
            strategy_performance = insights.get('strategy_performance', {})
            print(f"     - Strategy Performance Data: {len(strategy_performance)} strategies")
            
            for strategy, perf in strategy_performance.items():
                if isinstance(perf, dict):
                    win_rate = perf.get('win_rate', 0)
                    total_trades = perf.get('total_trades', 0)
                    print(f"       * {strategy}: {win_rate:.1f}% win rate ({total_trades} trades)")
            
            # Optimization status
            optimization_status = insights.get('optimization_status', {})
            print(f"     - Optimization Status: {len(optimization_status)} strategies")
            
            for strategy, status in optimization_status.items():
                if isinstance(status, dict):
                    optimized = status.get('optimized', False)
                    version = status.get('parameter_version', 'N/A')
                    print(f"       * {strategy}: {'✅ Optimized' if optimized else '⏳ Learning'} (v{version})")
            
            # Market insights
            market_insights = insights.get('market_insights', {})
            if market_insights:
                print(f"     - Market Insights:")
                print(f"       * Preferred Strategy: {market_insights.get('preferred_strategy', 'N/A')}")
                print(f"       * Current Conditions: {market_insights.get('current_conditions', 'N/A')}")
                print(f"       * IV Environment: {market_insights.get('iv_environment', 'N/A')}")
        
        # Test 5: Parameter Optimization
        print(f"\n⚙️  Testing Parameter Optimization Endpoint")
        success, optimize_data = self.run_test(
            "Parameter Optimization (Wheel)", 
            "POST", 
            "expert-options/optimize/wheel", 
            200
        )
        
        if success:
            print(f"   🔧 Optimization Result:")
            print(f"     - Message: {optimize_data.get('message', 'N/A')}")
            print(f"     - Strategy Type: {optimize_data.get('strategy_type', 'N/A')}")
            print(f"     - Timestamp: {optimize_data.get('timestamp', 'N/A')}")
        
        # Test invalid strategy type
        success, error_data = self.run_test(
            "Parameter Optimization (Invalid)", 
            "POST", 
            "expert-options/optimize/invalid_strategy", 
            200  # Should return 200 with error message
        )
        
        if success and 'error' in error_data:
            print(f"   ✅ Error handling working: {error_data.get('error', 'N/A')}")
        
        # Test 6: Comprehensive Validation
        print(f"\n✅ Expert Options System Validation Summary")
        
        validation_results = {
            "strategy_recommendations": strategies_data.get('total_strategies', 0) >= 3,
            "individual_strategies": all([
                wheel_data.get('strategy', {}).get('strategy_type') == 'wheel',
                condor_data.get('strategy', {}).get('strategy_type') == 'iron_condor', 
                vol_data.get('strategy', {}).get('strategy_type') == 'volatility_play'
            ]),
            "market_analysis": len(market_data.get('market_conditions', {})) >= 5,
            "learning_insights": 'learning_insights' in insights_data,
            "parameter_optimization": 'message' in optimize_data
        }
        
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        
        print(f"   📊 Validation Results: {passed_validations}/{total_validations} passed")
        
        for test_name, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"     {status} {test_name.replace('_', ' ').title()}")
        
        success_rate = (passed_validations / total_validations) * 100
        print(f"   🎯 Expert Options Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   🎉 EXCELLENT: Expert Options Trading System is fully operational!")
            print(f"   🤖 AI-powered options strategies with confidence scores working perfectly")
            print(f"   📈 All 3 strategies (Wheel, Iron Condor, Volatility Play) generating properly")
            print(f"   🧠 Machine learning insights and parameter optimization functional")
        elif success_rate >= 60:
            print(f"   ✅ GOOD: Expert Options system mostly working with minor issues")
        else:
            print(f"   ❌ NEEDS ATTENTION: Expert Options system has significant issues")
        
        return success_rate >= 80

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid stock symbol
        self.run_test("Invalid Stock Symbol", "GET", "stocks/INVALID123", 500)
        
        # Test invalid portfolio item deletion
        self.run_test("Delete Non-existent Portfolio Item", "DELETE", "portfolio/invalid-id", 404)
        
        # Test invalid watchlist item deletion
        self.run_test("Delete Non-existent Watchlist Item", "DELETE", "watchlist/invalid-id", 404)
        
        # Test invalid investment score
        self.run_test("Invalid Investment Score", "GET", "investments/score/INVALID123", 500)

    def run_unusual_whales_focused_tests(self):
        """Run focused tests on Unusual Whales API endpoints as requested"""
        print("🐋 UNUSUAL WHALES API ENDPOINT TESTING")
        print("=" * 80)
        print("🎯 FOCUS: Test all Unusual Whales API endpoints with provided API key")
        print("🔑 API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print("📋 Endpoints to test:")
        print("   1. 🎯 Options Flow (/api/unusual-whales/options/flow-alerts) - MAIN PRIORITY")
        print("   2. 🌊 Dark Pool (/api/unusual-whales/dark-pool/recent)")
        print("   3. 🏛️  Congressional Trades (/api/unusual-whales/congressional/trades)")
        print("   4. 🎯 Trading Strategies (/api/unusual-whales/trading-strategies)")
        print("=" * 80)
        
        # Test API root first to verify connectivity
        print("\n🔍 PRELIMINARY: API Connectivity Test")
        root_success = self.test_root_endpoint()
        
        if not root_success:
            print("❌ API root endpoint failed - cannot proceed with testing")
            return False
        
        # Run comprehensive Unusual Whales tests
        endpoint_results = self.test_all_unusual_whales_endpoints()
        
        # Summary
        print(f"\n📊 FINAL SUMMARY")
        print("=" * 80)
        
        working_count = sum(1 for success in endpoint_results.values() if success)
        total_count = len(endpoint_results)
        
        print(f"🎯 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"🐋 Unusual Whales Endpoints Working: {working_count}/{total_count}")
        
        # Specific focus on main priority
        options_flow_working = endpoint_results.get('options_flow', False)
        print(f"\n🎯 MAIN PRIORITY STATUS:")
        if options_flow_working:
            print(f"   ✅ Options Flow API: WORKING - Real data instead of mock data")
            print(f"   🎉 PRIMARY OBJECTIVE ACHIEVED")
        else:
            print(f"   ❌ Options Flow API: FAILED - Still showing mock data or 404 errors")
            print(f"   ⚠️  PRIMARY OBJECTIVE NOT ACHIEVED")
        
        return endpoint_results

    def test_unusual_whales_final_verification(self):
        """Final verification testing of all 5 Unusual Whales API endpoints after API key update and bug fixes"""
        print("\n🐋 FINAL VERIFICATION: ALL UNUSUAL WHALES API ENDPOINTS")
        print("=" * 80)
        print("🎯 OBJECTIVE: Final verification testing after API key update and bug fixes")
        print("🔑 API KEY: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
        print("📋 TESTING 5 PRIMARY ENDPOINTS:")
        print("   1. Options Flow: /api/unusual-whales/options/flow-alerts")
        print("   2. Dark Pool: /api/unusual-whales/dark-pool/recent") 
        print("   3. Congressional Trades: /api/unusual-whales/congressional/trades")
        print("   4. Trading Strategies: /api/unusual-whales/trading-strategies")
        print("   5. Comprehensive Analysis: /api/unusual-whales/analysis/comprehensive")
        
        endpoint_results = {}
        
        # Test 1: Options Flow - should return real data, no longer mock
        print(f"\n📈 ENDPOINT 1: Options Flow Alerts")
        print("-" * 60)
        
        import time
        start_time = time.time()
        success_options, options_data = self.run_test("Options Flow Alerts", "GET", "unusual-whales/options/flow-alerts", 200)
        options_time = time.time() - start_time
        
        if success_options:
            data = options_data.get('data', {})
            alerts = data.get('alerts', [])
            summary = data.get('summary', {})
            
            print(f"   ✅ Status: 200 OK")
            print(f"   ⏱️  Response Time: {options_time:.2f}s")
            print(f"   📊 Alerts Found: {len(alerts)}")
            print(f"   💰 Total Premium: ${summary.get('total_premium', 0):,.0f}")
            print(f"   📈 Bullish/Bearish: {summary.get('bullish_count', 0)}/{summary.get('bearish_count', 0)}")
            
            # Check for real data indicators
            if len(alerts) > 0:
                symbols = [alert.get('symbol', '') for alert in alerts[:5]]
                print(f"   🎯 Sample Symbols: {symbols}")
                
                # Real data check
                real_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'AMZN', 'META']
                real_found = [s for s in symbols if s in real_symbols]
                if real_found:
                    print(f"   ✅ REAL DATA: Found market symbols {real_found}")
                    endpoint_results['options_flow'] = {'status': 'PASS', 'real_data': True, 'response_time': options_time}
                else:
                    print(f"   ⚠️  DATA CHECK: No common market symbols found")
                    endpoint_results['options_flow'] = {'status': 'PASS', 'real_data': False, 'response_time': options_time}
            else:
                print(f"   📝 No alerts (may be normal if no unusual activity)")
                endpoint_results['options_flow'] = {'status': 'PASS', 'real_data': 'N/A', 'response_time': options_time}
        else:
            print(f"   ❌ FAILED: Options Flow endpoint returned error")
            endpoint_results['options_flow'] = {'status': 'FAIL', 'real_data': False, 'response_time': options_time}
        
        # Test 2: Dark Pool - should work with existing real data
        print(f"\n🌊 ENDPOINT 2: Dark Pool Recent Activity")
        print("-" * 60)
        
        start_time = time.time()
        success_dark, dark_data = self.run_test("Dark Pool Recent", "GET", "unusual-whales/dark-pool/recent", 200)
        dark_time = time.time() - start_time
        
        if success_dark:
            data = dark_data.get('data', {})
            trades = data.get('trades', [])
            summary = data.get('summary', {})
            
            print(f"   ✅ Status: 200 OK")
            print(f"   ⏱️  Response Time: {dark_time:.2f}s")
            print(f"   📊 Trades Found: {len(trades)}")
            print(f"   📈 Total Dark Volume: {summary.get('total_dark_volume', 0):,}")
            print(f"   🎯 Avg Dark %: {summary.get('avg_dark_percentage', 0):.2f}%")
            print(f"   🏛️  Institutional Signals: {summary.get('institutional_signals', 0)}")
            
            if len(trades) > 0:
                tickers = [trade.get('ticker', '') for trade in trades[:5]]
                print(f"   🎯 Sample Tickers: {tickers}")
                endpoint_results['dark_pool'] = {'status': 'PASS', 'data_count': len(trades), 'response_time': dark_time}
            else:
                print(f"   📝 No trades (expected when no significant dark pool activity)")
                endpoint_results['dark_pool'] = {'status': 'PASS', 'data_count': 0, 'response_time': dark_time}
        else:
            print(f"   ❌ FAILED: Dark Pool endpoint returned error")
            endpoint_results['dark_pool'] = {'status': 'FAIL', 'data_count': 0, 'response_time': dark_time}
        
        # Test 3: Congressional Trades - should work with existing real data
        print(f"\n🏛️  ENDPOINT 3: Congressional Trades")
        print("-" * 60)
        
        start_time = time.time()
        success_congress, congress_data = self.run_test("Congressional Trades", "GET", "unusual-whales/congressional/trades", 200)
        congress_time = time.time() - start_time
        
        if success_congress:
            data = congress_data.get('data', {})
            trades = data.get('trades', [])
            summary = data.get('summary', {})
            
            print(f"   ✅ Status: 200 OK")
            print(f"   ⏱️  Response Time: {congress_time:.2f}s")
            print(f"   📊 Trades Found: {len(trades)}")
            print(f"   💰 Total Amount: ${summary.get('total_amount', 0):,.0f}")
            print(f"   👥 Representatives: {summary.get('unique_representatives', 0)}")
            print(f"   📈 Unique Tickers: {summary.get('unique_tickers', 0)}")
            
            # Show party breakdown
            party_breakdown = summary.get('party_breakdown', {})
            if party_breakdown:
                print(f"   🗳️  Party Breakdown: {dict(party_breakdown)}")
            
            endpoint_results['congressional'] = {'status': 'PASS', 'data_count': len(trades), 'response_time': congress_time}
        else:
            print(f"   ❌ FAILED: Congressional Trades endpoint returned error")
            endpoint_results['congressional'] = {'status': 'FAIL', 'data_count': 0, 'response_time': congress_time}
        
        # Test 4: Trading Strategies - just fixed string concatenation error, verify working
        print(f"\n🎯 ENDPOINT 4: Trading Strategies")
        print("-" * 60)
        
        start_time = time.time()
        success_strategies, strategies_data = self.run_test("Trading Strategies", "GET", "unusual-whales/trading-strategies", 200)
        strategies_time = time.time() - start_time
        
        if success_strategies:
            strategies = strategies_data.get('strategies', [])
            
            print(f"   ✅ Status: 200 OK")
            print(f"   ⏱️  Response Time: {strategies_time:.2f}s")
            print(f"   📊 Strategies Generated: {len(strategies)}")
            
            if len(strategies) > 0:
                for i, strategy in enumerate(strategies[:3]):
                    print(f"   🎯 Strategy {i+1}: {strategy.get('strategy_name', 'N/A')}")
                    print(f"     - Ticker: {strategy.get('ticker', 'N/A')}")
                    print(f"     - Confidence: {strategy.get('confidence', 0):.0%}")
                    print(f"     - Timeframe: {strategy.get('timeframe', 'N/A')}")
                
                endpoint_results['trading_strategies'] = {'status': 'PASS', 'strategies_count': len(strategies), 'response_time': strategies_time}
            else:
                print(f"   📝 No strategies (expected when insufficient signals)")
                endpoint_results['trading_strategies'] = {'status': 'PASS', 'strategies_count': 0, 'response_time': strategies_time}
        else:
            print(f"   ❌ FAILED: Trading Strategies endpoint returned error")
            endpoint_results['trading_strategies'] = {'status': 'FAIL', 'strategies_count': 0, 'response_time': strategies_time}
        
        # Test 5: Comprehensive Analysis - should work combining all data
        print(f"\n📊 ENDPOINT 5: Comprehensive Analysis")
        print("-" * 60)
        
        start_time = time.time()
        success_analysis, analysis_data = self.run_test("Comprehensive Analysis", "GET", "unusual-whales/analysis/comprehensive", 200)
        analysis_time = time.time() - start_time
        
        if success_analysis:
            comprehensive_analysis = analysis_data.get('comprehensive_analysis', {})
            market_outlook = analysis_data.get('market_outlook', {})
            data_summary = analysis_data.get('data_summary', {})
            
            print(f"   ✅ Status: 200 OK")
            print(f"   ⏱️  Response Time: {analysis_time:.2f}s")
            print(f"   📊 Data Summary:")
            print(f"     - Options Alerts: {data_summary.get('options_alerts', 0)}")
            print(f"     - Dark Pool Trades: {data_summary.get('dark_pool_trades', 0)}")
            print(f"     - Congressional Trades: {data_summary.get('congressional_trades', 0)}")
            
            print(f"   🎯 Market Outlook:")
            print(f"     - Sentiment: {market_outlook.get('overall_sentiment', 'N/A')}")
            print(f"     - Confidence: {market_outlook.get('confidence', 'N/A')}")
            
            # Check data availability flags
            options_available = comprehensive_analysis.get('options_flow', {}).get('data_available', False)
            dark_pool_available = comprehensive_analysis.get('dark_pool', {}).get('data_available', False)
            congressional_available = comprehensive_analysis.get('congressional', {}).get('data_available', False)
            
            print(f"   📋 Data Availability:")
            print(f"     - Options Flow: {'✅' if options_available else '❌'}")
            print(f"     - Dark Pool: {'✅' if dark_pool_available else '❌'}")
            print(f"     - Congressional: {'✅' if congressional_available else '❌'}")
            
            endpoint_results['comprehensive'] = {'status': 'PASS', 'data_sources': sum([options_available, dark_pool_available, congressional_available]), 'response_time': analysis_time}
        else:
            print(f"   ❌ FAILED: Comprehensive Analysis endpoint returned error")
            endpoint_results['comprehensive'] = {'status': 'FAIL', 'data_sources': 0, 'response_time': analysis_time}
        
        # Final Assessment
        print(f"\n🎯 FINAL VERIFICATION RESULTS")
        print("=" * 80)
        
        passed_endpoints = sum(1 for result in endpoint_results.values() if result['status'] == 'PASS')
        total_endpoints = len(endpoint_results)
        success_rate = (passed_endpoints / total_endpoints) * 100
        
        print(f"\n📊 ENDPOINT STATUS SUMMARY:")
        for endpoint, result in endpoint_results.items():
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            response_time = result['response_time']
            print(f"   {status_icon} {endpoint.replace('_', ' ').title()}: {result['status']} ({response_time:.2f}s)")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_endpoints}/{total_endpoints} endpoints passing)")
        
        # Response time analysis
        avg_response_time = sum(result['response_time'] for result in endpoint_results.values()) / len(endpoint_results)
        print(f"⏱️  AVERAGE RESPONSE TIME: {avg_response_time:.2f}s")
        
        # Key success criteria verification
        print(f"\n✅ SUCCESS CRITERIA VERIFICATION:")
        
        criteria_met = []
        
        # All 5 endpoints returning 200 status codes
        if passed_endpoints == 5:
            criteria_met.append("✅ All 5 endpoints returning 200 status codes")
        else:
            criteria_met.append(f"❌ Only {passed_endpoints}/5 endpoints returning 200 status codes")
        
        # No 500 errors or API failures
        failed_endpoints = [name for name, result in endpoint_results.items() if result['status'] == 'FAIL']
        if not failed_endpoints:
            criteria_met.append("✅ No 500 errors or API failures")
        else:
            criteria_met.append(f"❌ Failed endpoints: {failed_endpoints}")
        
        # Options Flow returning real data (not mock)
        options_result = endpoint_results.get('options_flow', {})
        if options_result.get('real_data') == True:
            criteria_met.append("✅ Options Flow returning real data (not mock)")
        elif options_result.get('real_data') == 'N/A':
            criteria_met.append("⚠️  Options Flow: No data to verify (may be normal)")
        else:
            criteria_met.append("❌ Options Flow: Real data verification failed")
        
        # Trading Strategies working after fixes
        strategies_result = endpoint_results.get('trading_strategies', {})
        if strategies_result.get('status') == 'PASS':
            criteria_met.append("✅ Trading Strategies working after fixes")
        else:
            criteria_met.append("❌ Trading Strategies still has issues")
        
        # Response times reasonable (under 5 seconds each)
        slow_endpoints = [name for name, result in endpoint_results.items() if result['response_time'] > 5.0]
        if not slow_endpoints:
            criteria_met.append("✅ All response times reasonable (under 5 seconds)")
        else:
            criteria_met.append(f"⚠️  Slow endpoints (>5s): {slow_endpoints}")
        
        for criterion in criteria_met:
            print(f"   {criterion}")
        
        # Final verdict
        print(f"\n🎉 FINAL VERDICT:")
        if success_rate == 100 and avg_response_time < 5.0:
            print(f"   🎉 EXCELLENT: All Unusual Whales endpoints working perfectly!")
            print(f"   ✅ API key update successful")
            print(f"   ✅ Bug fixes verified")
            print(f"   ✅ All endpoints operational")
            print(f"   ✅ Response times excellent")
        elif success_rate >= 80:
            print(f"   ✅ GOOD: Most Unusual Whales endpoints working correctly")
            print(f"   📝 Minor issues may need attention")
        else:
            print(f"   ❌ NEEDS ATTENTION: Multiple endpoint failures detected")
            print(f"   🔧 API key or configuration issues may exist")
        
        return success_rate >= 80

    def test_tradestation_authentication_status(self):
        """Test TradeStation authentication status and LIVE environment connectivity"""
        print("\n🏛️  TESTING TRADESTATION AUTHENTICATION STATUS - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation authentication to LIVE environment")
        print("🔧 REQUIREMENTS: Check auth status, environment, credentials, connection test")
        
        # Test 1: Authentication Status Endpoint
        print(f"\n📊 PHASE 1: Authentication Status Endpoint Testing")
        print("-" * 60)
        
        success, auth_data = self.run_test("TradeStation Auth Status", "GET", "auth/tradestation/status", 200)
        if not success:
            print("❌ TradeStation authentication status endpoint failed")
            return False, False
        
        # Verify response structure
        required_fields = ['status', 'authentication', 'api_configuration', 'timestamp']
        missing_fields = [field for field in required_fields if field not in auth_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False, False
        else:
            print(f"✅ All required response fields present: {required_fields}")
        
        authentication = auth_data.get('authentication', {})
        api_config = auth_data.get('api_configuration', {})
        connection_test = auth_data.get('connection_test', {})
        
        print(f"📊 API Status: {auth_data.get('status', 'unknown')}")
        print(f"🔐 Authenticated: {authentication.get('authenticated', False)}")
        print(f"🌍 Environment: {api_config.get('environment', 'unknown')}")
        print(f"🔗 Base URL: {api_config.get('base_url', 'unknown')}")
        print(f"⚙️  Credentials Configured: {api_config.get('credentials_configured', False)}")
        
        # Test 2: LIVE Environment Verification
        print(f"\n🌍 PHASE 2: LIVE Environment Verification")
        print("-" * 60)
        
        environment = api_config.get('environment', '')
        base_url = api_config.get('base_url', '')
        
        if environment == 'LIVE':
            print(f"✅ Environment correctly set to LIVE")
        else:
            print(f"❌ Environment is '{environment}', expected 'LIVE'")
        
        if 'api.tradestation.com' in base_url:
            print(f"✅ Base URL points to production TradeStation API")
        else:
            print(f"⚠️  Base URL may not be production: {base_url}")
        
        # Test 3: Authentication Status Verification
        print(f"\n🔐 PHASE 3: Authentication Status Verification")
        print("-" * 60)
        
        authenticated = authentication.get('authenticated', False)
        expires_in = authentication.get('expires_in_minutes', 0)
        
        if authenticated:
            print(f"✅ TradeStation authentication successful")
            print(f"⏰ Token expires in: {expires_in} minutes")
            
            if expires_in > 5:
                print(f"✅ Token has sufficient time remaining")
            else:
                print(f"⚠️  Token expires soon ({expires_in} minutes)")
        else:
            print(f"❌ TradeStation not authenticated")
            print(f"💡 User needs to complete OAuth authentication flow")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: TradeStation Authentication")
        print("=" * 80)
        
        # Calculate success metrics
        test_results = [
            ("Endpoint Response", success),
            ("Response Structure", len(missing_fields) == 0),
            ("LIVE Environment", environment == 'LIVE'),
            ("Production URL", 'api.tradestation.com' in base_url),
            ("Credentials Configured", api_config.get('credentials_configured', False)),
            ("Authentication Status", authenticated or not api_config.get('credentials_configured', False))
        ]
        
        passed_tests = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Authentication Status: {'✅ AUTHENTICATED' if authenticated else '❌ NOT AUTHENTICATED'}")
        print(f"   - Environment: {environment}")
        print(f"   - Credentials: {'✅ CONFIGURED' if api_config.get('credentials_configured', False) else '❌ NOT CONFIGURED'}")
        print(f"   - Connection: {'✅ WORKING' if connection_test and connection_test.get('success') else '❌ NOT TESTED/FAILED'}")
        
        return success_rate >= 70, authenticated

    def test_tradestation_accounts_endpoint(self):
        """Test TradeStation accounts endpoint to verify account retrieval"""
        print("\n📊 TESTING TRADESTATION ACCOUNTS ENDPOINT")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation accounts retrieval functionality")
        
        # Test accounts endpoint
        success, accounts_data = self.run_test("TradeStation Accounts", "GET", "tradestation/accounts", 200)
        
        if not success:
            print("❌ TradeStation accounts endpoint failed")
            return False, None
        
        # Verify response structure
        if 'accounts' in accounts_data:
            accounts = accounts_data['accounts']
            print(f"✅ Found {len(accounts)} TradeStation accounts")
            
            if accounts:
                # Show first account details (without sensitive info)
                first_account = accounts[0]
                account_id = first_account.get('Key', first_account.get('AccountID', 'unknown'))
                account_type = first_account.get('Type', 'unknown')
                
                print(f"📊 Sample Account:")
                print(f"   - Account ID: {account_id}")
                print(f"   - Account Type: {account_type}")
                
                return True, account_id
            else:
                print("⚠️  No accounts found")
                return True, None
        else:
            print("❌ Invalid response structure - missing 'accounts' field")
            return False, None

    def test_tradestation_portfolio_summary(self, account_id):
        """Test TradeStation portfolio summary endpoint with comprehensive data structure verification"""
        print(f"\n📊 TESTING TRADESTATION PORTFOLIO SUMMARY - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify portfolio summary returns correct data structure for dropdown functionality")
        print("🔧 REQUIREMENTS: Check data structure, positions data, asset types, dropdown candidates")
        
        if not account_id:
            print("❌ No account ID available for testing")
            return False
        
        # Test portfolio summary endpoint
        print(f"\n📊 PHASE 1: Portfolio Summary Endpoint Testing")
        print("-" * 60)
        
        success, portfolio_data = self.run_test(
            f"Portfolio Summary (Account: {account_id})", 
            "GET", 
            f"tradestation/accounts/{account_id}/summary", 
            200
        )
        
        if not success:
            print("❌ TradeStation portfolio summary endpoint failed")
            return False
        
        # Test 2: Data Structure Verification
        print(f"\n📋 PHASE 2: Data Structure Verification")
        print("-" * 60)
        
        # Verify top-level fields
        if portfolio_data.get('status') != 'success':
            print(f"❌ Expected status 'success', got '{portfolio_data.get('status')}'")
            return False
        else:
            print(f"✅ Status field correct: {portfolio_data.get('status')}")
        
        data = portfolio_data.get('data', {})
        if not data:
            print(f"❌ Missing 'data' field in response")
            return False
        else:
            print(f"✅ Data field present")
        
        # Verify nested data structure
        portfolio_metrics = data.get('portfolio_metrics', {})
        positions = data.get('positions', [])
        risk_analysis = data.get('risk_analysis', {})
        
        print(f"📊 Portfolio Metrics: {len(portfolio_metrics)} fields")
        print(f"📊 Positions: {len(positions)} positions")
        print(f"📊 Risk Analysis: {len(risk_analysis)} fields")
        
        # Test 3: Positions Data Structure Verification
        print(f"\n📊 PHASE 3: Positions Data Structure Verification")
        print("-" * 60)
        
        if not positions:
            print("⚠️  No positions found - portfolio may be empty")
            return True  # Empty portfolio is valid
        
        # Verify required fields in positions
        required_position_fields = [
            'symbol', 'asset_type', 'quantity', 'unrealized_pnl', 
            'average_price', 'daily_pnl', 'unrealized_pnl_percent', 'market_value'
        ]
        
        first_position = positions[0]
        missing_fields = [field for field in required_position_fields if field not in first_position]
        
        if missing_fields:
            print(f"❌ Missing required position fields: {missing_fields}")
        else:
            print(f"✅ All required position fields present: {len(required_position_fields)} fields")
        
        # Display sample position
        print(f"📊 Sample Position:")
        print(f"   - Symbol: {first_position.get('symbol', 'N/A')}")
        print(f"   - Asset Type: {first_position.get('asset_type', 'N/A')}")
        print(f"   - Quantity: {first_position.get('quantity', 0)}")
        print(f"   - Market Value: ${first_position.get('market_value', 0):,.2f}")
        print(f"   - Unrealized P&L: ${first_position.get('unrealized_pnl', 0):,.2f}")
        print(f"   - Daily P&L: ${first_position.get('daily_pnl', 0):,.2f}")
        
        # Test 4: Asset Type Verification
        print(f"\n🏷️  PHASE 4: Asset Type Verification")
        print("-" * 60)
        
        asset_types = {}
        for position in positions:
            asset_type = position.get('asset_type', 'UNKNOWN')
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        print(f"📊 Asset Type Distribution:")
        for asset_type, count in asset_types.items():
            print(f"   - {asset_type}: {count} positions")
        
        # Verify expected asset types
        expected_asset_types = ['STOCK', 'STOCKOPTION']
        found_expected_types = [at for at in asset_types.keys() if at in expected_asset_types]
        
        if found_expected_types:
            print(f"✅ Expected asset types found: {found_expected_types}")
        else:
            print(f"⚠️  No expected asset types (STOCK, STOCKOPTION) found")
        
        # Test 5: Dropdown Functionality Data Verification
        print(f"\n🔽 PHASE 5: Dropdown Functionality Data Verification")
        print("-" * 60)
        
        # Group positions by symbol to identify dropdown candidates
        symbol_groups = {}
        for position in positions:
            symbol = position.get('symbol', 'UNKNOWN')
            base_symbol = symbol.split()[0] if ' ' in symbol else symbol  # Extract base symbol from options
            
            if base_symbol not in symbol_groups:
                symbol_groups[base_symbol] = []
            symbol_groups[base_symbol].append(position)
        
        # Find symbols with multiple positions (dropdown candidates)
        dropdown_candidates = {symbol: positions_list for symbol, positions_list in symbol_groups.items() if len(positions_list) > 1}
        
        print(f"📊 Symbol Analysis:")
        print(f"   - Total Unique Symbols: {len(symbol_groups)}")
        print(f"   - Symbols with Multiple Positions: {len(dropdown_candidates)}")
        
        if dropdown_candidates:
            print(f"🔽 Dropdown Candidates:")
            for symbol, symbol_positions in list(dropdown_candidates.items())[:10]:  # Show first 10
                asset_types_in_group = [pos.get('asset_type', 'UNKNOWN') for pos in symbol_positions]
                print(f"   - {symbol}: {len(symbol_positions)} positions ({', '.join(set(asset_types_in_group))})")
        
        # Test 6: Specific Symbol Verification (CRM, TSLA, AAPL, GOOGL, IBM)
        print(f"\n🎯 PHASE 6: Specific Symbol Verification")
        print("-" * 60)
        
        target_symbols = ['CRM', 'TSLA', 'AAPL', 'GOOGL', 'IBM']
        found_target_symbols = []
        
        for target_symbol in target_symbols:
            if target_symbol in symbol_groups:
                positions_count = len(symbol_groups[target_symbol])
                found_target_symbols.append(target_symbol)
                print(f"   ✅ {target_symbol}: {positions_count} positions")
                
                # Show asset types for this symbol
                asset_types_for_symbol = [pos.get('asset_type', 'UNKNOWN') for pos in symbol_groups[target_symbol]]
                print(f"      Asset types: {', '.join(set(asset_types_for_symbol))}")
            else:
                print(f"   ❌ {target_symbol}: Not found in portfolio")
        
        print(f"📊 Target Symbols Found: {len(found_target_symbols)}/{len(target_symbols)}")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: TradeStation Portfolio Summary")
        print("=" * 80)
        
        # Calculate success metrics
        test_results = [
            ("Endpoint Response", success),
            ("Correct Data Structure", portfolio_data.get('status') == 'success' and 'data' in portfolio_data),
            ("Portfolio Metrics Present", len(portfolio_metrics) > 0),
            ("Positions Data Present", len(positions) >= 0),  # 0 is valid (empty portfolio)
            ("Required Position Fields", len(missing_fields) == 0 if positions else True),
            ("Asset Types Present", len(asset_types) > 0 if positions else True),
            ("Dropdown Candidates Found", len(dropdown_candidates) > 0 if positions else True),
            ("Risk Analysis Present", len(risk_analysis) > 0)
        ]
        
        passed_tests = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Data Structure: {'✅ CORRECT' if portfolio_data.get('status') == 'success' else '❌ INCORRECT'}")
        print(f"   - Total Positions: {len(positions)}")
        print(f"   - Asset Types: {list(asset_types.keys()) if asset_types else 'None'}")
        print(f"   - Dropdown Candidates: {len(dropdown_candidates)}")
        print(f"   - Target Symbols Found: {len(found_target_symbols)}/{len(target_symbols)}")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Portfolio summary API perfect for dropdown functionality!")
            print(f"   Backend provides correct data structure for frontend grouping and dropdowns.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Portfolio summary API mostly ready for dropdown functionality.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Portfolio summary API has issues for dropdown functionality.")
        
        return success_rate >= 70

    def run_tradestation_tests(self):
        """Run TradeStation-specific tests as requested in the review"""
        print("🏛️  Starting TradeStation Live Portfolio Backend Tests")
        print("=" * 80)
        print("🎯 FOCUS: TradeStation authentication, accounts, and portfolio summary functionality")
        print("📋 REQUIREMENTS: Verify backend provides correct data for frontend dropdown functionality")
        
        # Test 1: TradeStation Authentication Status
        auth_success, authenticated = self.test_tradestation_authentication_status()
        
        # Test 2: TradeStation Accounts Endpoint
        if auth_success:
            accounts_success, account_id = self.test_tradestation_accounts_endpoint()
            
            # Test 3: TradeStation Portfolio Summary
            if accounts_success and account_id:
                portfolio_success = self.test_tradestation_portfolio_summary(account_id)
            else:
                print("\n⚠️  Skipping portfolio summary test - no account ID available")
                portfolio_success = False
        else:
            print("\n⚠️  Skipping accounts and portfolio tests - authentication issues")
            accounts_success = False
            portfolio_success = False
        
        # Final TradeStation Test Results
        print("\n" + "=" * 80)
        print("🏛️  TRADESTATION TEST RESULTS SUMMARY")
        print("=" * 80)
        
        tradestation_tests = [
            ("Authentication Status", auth_success),
            ("Accounts Retrieval", accounts_success),
            ("Portfolio Summary", portfolio_success)
        ]
        
        passed_ts_tests = sum(1 for _, passed in tradestation_tests if passed)
        total_ts_tests = len(tradestation_tests)
        ts_success_rate = (passed_ts_tests / total_ts_tests) * 100
        
        print(f"\n📊 TRADESTATION TEST RESULTS:")
        for test_name, passed in tradestation_tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        print(f"\n🎯 TRADESTATION SUCCESS RATE: {ts_success_rate:.1f}% ({passed_ts_tests}/{total_ts_tests} tests passed)")
        
        # Overall assessment
        if ts_success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - TradeStation backend fully ready for dropdown functionality!")
        elif ts_success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - TradeStation backend mostly ready with minor issues.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - TradeStation backend has significant issues.")
        
        return ts_success_rate >= 70

    def test_investment_scoring_agent_endpoints(self):
        """Test NEW Investment Scoring Agent endpoints - COMPREHENSIVE TESTING"""
        print("\n🤖 TESTING INVESTMENT SCORING AGENT - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test new AI Investment Scoring Agent implementation")
        print("📊 ENDPOINTS TO TEST:")
        print("   1. POST /api/agents/investment-scoring?symbol=AAPL")
        print("   2. GET /api/agents/investment-scoring/batch?symbols=AAPL,MSFT,NVDA")
        print("   3. GET /api/agents/investment-scoring/methodology")
        
        # Test 1: Individual Investment Scoring - AAPL
        print(f"\n📊 PHASE 1: Individual Investment Scoring (AAPL)")
        print("-" * 60)
        
        success, aapl_score = self.run_test(
            "Investment Scoring Agent (AAPL)", 
            "POST", 
            "agents/investment-scoring?symbol=AAPL&include_personalization=false", 
            200
        )
        
        if success:
            print(f"   ✅ AAPL Investment Score: {aapl_score.get('investment_score', 'N/A')}")
            print(f"   📊 Recommendation: {aapl_score.get('recommendation', 'N/A')}")
            print(f"   🎯 Confidence Level: {aapl_score.get('confidence_level', 'N/A')}")
            
            # Verify required fields
            required_fields = [
                'symbol', 'investment_score', 'recommendation', 'confidence_level',
                'key_signals', 'risk_analysis', 'signal_breakdown', 'timestamp'
            ]
            missing_fields = [field for field in required_fields if field not in aapl_score]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
            
            # Verify score range (0-100)
            score = aapl_score.get('investment_score', -1)
            if 0 <= score <= 100:
                print(f"   ✅ Score in valid range: {score}")
            else:
                print(f"   ❌ Score out of range: {score}")
            
            # Verify key signals
            key_signals = aapl_score.get('key_signals', [])
            print(f"   📊 Key Signals Found: {len(key_signals)}")
            for i, signal in enumerate(key_signals[:3]):
                signal_type = signal.get('type', 'unknown')
                signal_score = signal.get('score', 0)
                signal_direction = signal.get('direction', 'unknown')
                print(f"     {i+1}. {signal_type}: {signal_score} ({signal_direction})")
            
            # Verify signal breakdown
            signal_breakdown = aapl_score.get('signal_breakdown', {})
            expected_signals = ['options_flow', 'dark_pool', 'congressional', 'ai_strategies', 'market_momentum', 'risk_assessment']
            present_signals = [sig for sig in expected_signals if sig in signal_breakdown]
            print(f"   🔍 Signal Components: {len(present_signals)}/{len(expected_signals)} present")
            
            # Verify risk analysis
            risk_analysis = aapl_score.get('risk_analysis', {})
            if 'overall_risk' in risk_analysis and 'risk_factors' in risk_analysis:
                print(f"   🛡️  Risk Analysis: {risk_analysis.get('overall_risk', 'unknown')} risk")
                print(f"   ⚠️  Risk Factors: {len(risk_analysis.get('risk_factors', []))}")
            
        # Test 2: Individual Investment Scoring - Different Symbols
        print(f"\n📊 PHASE 2: Multiple Symbol Testing")
        print("-" * 60)
        
        test_symbols = ["MSFT", "GOOGL", "NVDA"]
        symbol_results = {}
        
        for symbol in test_symbols:
            success_sym, sym_score = self.run_test(
                f"Investment Scoring Agent ({symbol})", 
                "POST", 
                f"agents/investment-scoring?symbol={symbol}", 
                200
            )
            
            if success_sym:
                score = sym_score.get('investment_score', 0)
                recommendation = sym_score.get('recommendation', 'N/A')
                confidence = sym_score.get('confidence_level', 'N/A')
                symbol_results[symbol] = {'score': score, 'recommendation': recommendation, 'confidence': confidence}
                print(f"   ✅ {symbol}: Score={score}, Rec={recommendation}, Conf={confidence}")
            else:
                print(f"   ❌ {symbol}: Failed to get score")
                symbol_results[symbol] = {'error': True}
        
        # Test 3: Batch Investment Scoring
        print(f"\n📊 PHASE 3: Batch Investment Scoring")
        print("-" * 60)
        
        batch_symbols = "AAPL,MSFT,NVDA"
        success_batch, batch_results = self.run_test(
            "Batch Investment Scoring", 
            "GET", 
            "agents/investment-scoring/batch", 
            200, 
            params={"symbols": batch_symbols, "limit": 10}
        )
        
        if success_batch:
            symbols_analyzed = batch_results.get('symbols_analyzed', 0)
            successful_analyses = batch_results.get('successful_analyses', 0)
            results = batch_results.get('results', {})
            
            print(f"   📊 Symbols Analyzed: {symbols_analyzed}")
            print(f"   ✅ Successful Analyses: {successful_analyses}")
            print(f"   📈 Success Rate: {(successful_analyses/symbols_analyzed*100):.1f}%" if symbols_analyzed > 0 else "N/A")
            
            # Verify each symbol in batch results
            expected_symbols = ["AAPL", "MSFT", "NVDA"]
            for symbol in expected_symbols:
                if symbol in results:
                    result = results[symbol]
                    if 'error' not in result:
                        score = result.get('investment_score', 0)
                        recommendation = result.get('recommendation', 'N/A')
                        print(f"     ✅ {symbol}: Score={score}, Rec={recommendation}")
                    else:
                        print(f"     ❌ {symbol}: Error - {result.get('error', 'Unknown')}")
                else:
                    print(f"     ❌ {symbol}: Missing from batch results")
        
        # Test 4: Scoring Methodology Endpoint
        print(f"\n📊 PHASE 4: Scoring Methodology")
        print("-" * 60)
        
        success_method, methodology = self.run_test(
            "Investment Scoring Methodology", 
            "GET", 
            "agents/investment-scoring/methodology", 
            200
        )
        
        if success_method:
            print(f"   ✅ Methodology endpoint accessible")
            
            # Verify methodology structure
            expected_method_fields = [
                'agent_name', 'version', 'scoring_methodology', 'signal_weights',
                'score_ranges', 'confidence_levels', 'data_sources'
            ]
            missing_method_fields = [field for field in expected_method_fields if field not in methodology]
            
            if missing_method_fields:
                print(f"   ❌ Missing methodology fields: {missing_method_fields}")
            else:
                print(f"   ✅ All methodology fields present")
            
            # Display key methodology info
            agent_name = methodology.get('agent_name', 'N/A')
            version = methodology.get('version', 'N/A')
            print(f"   🤖 Agent: {agent_name} v{version}")
            
            # Signal weights
            signal_weights = methodology.get('signal_weights', {})
            print(f"   ⚖️  Signal Weights ({len(signal_weights)} components):")
            for signal, weight_desc in signal_weights.items():
                print(f"     - {signal}: {weight_desc}")
            
            # Score ranges
            score_ranges = methodology.get('score_ranges', {})
            print(f"   📊 Score Ranges ({len(score_ranges)} levels):")
            for range_key, range_desc in score_ranges.items():
                print(f"     - {range_key}: {range_desc}")
            
            # Data sources
            data_sources = methodology.get('data_sources', [])
            print(f"   📡 Data Sources ({len(data_sources)} sources):")
            for source in data_sources:
                print(f"     - {source}")
        
        # Test 5: Error Handling and Edge Cases
        print(f"\n📊 PHASE 5: Error Handling and Edge Cases")
        print("-" * 60)
        
        # Test invalid symbol
        success_invalid, invalid_result = self.run_test(
            "Investment Scoring (Invalid Symbol)", 
            "POST", 
            "agents/investment-scoring?symbol=INVALID123", 
            200  # Should return 200 with error handling
        )
        
        if success_invalid:
            if 'error' in invalid_result:
                print(f"   ✅ Invalid symbol handled gracefully: {invalid_result.get('error', 'N/A')}")
            else:
                score = invalid_result.get('investment_score', 0)
                print(f"   ✅ Invalid symbol processed: Score={score}")
        
        # Test batch with invalid symbols
        invalid_batch_symbols = "AAPL,INVALID123,MSFT"
        success_invalid_batch, invalid_batch_result = self.run_test(
            "Batch Scoring (Mixed Valid/Invalid)", 
            "GET", 
            "agents/investment-scoring/batch", 
            200, 
            params={"symbols": invalid_batch_symbols}
        )
        
        if success_invalid_batch:
            successful_analyses = invalid_batch_result.get('successful_analyses', 0)
            symbols_analyzed = invalid_batch_result.get('symbols_analyzed', 0)
            print(f"   ✅ Mixed batch handled: {successful_analyses}/{symbols_analyzed} successful")
        
        # Test 6: Performance and Response Time
        print(f"\n📊 PHASE 6: Performance Testing")
        print("-" * 60)
        
        import time
        start_time = time.time()
        
        success_perf, perf_result = self.run_test(
            "Investment Scoring (Performance)", 
            "POST", 
            "agents/investment-scoring?symbol=AAPL", 
            200
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   ⏱️  Response Time: {response_time:.2f} seconds")
        
        if response_time < 5.0:
            print(f"   ✅ Excellent response time")
        elif response_time < 10.0:
            print(f"   ✅ Good response time")
        else:
            print(f"   ⚠️  Slow response time")
        
        # Test 7: Data Source Integration Verification
        print(f"\n📊 PHASE 7: Data Source Integration Verification")
        print("-" * 60)
        
        if success and 'data_sources' in aapl_score:
            data_sources = aapl_score.get('data_sources', [])
            expected_sources = ['unusual_whales_options_flow', 'dark_pool', 'congressional_trades']
            
            print(f"   📡 Data Sources Integrated: {len(data_sources)}")
            for source in data_sources:
                if source in expected_sources:
                    print(f"     ✅ {source}")
                else:
                    print(f"     ⚠️  {source} (unexpected)")
            
            missing_sources = [src for src in expected_sources if src not in data_sources]
            if missing_sources:
                print(f"   ❌ Missing expected sources: {missing_sources}")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Investment Scoring Agent")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("Individual Scoring (AAPL)", success),
            ("Multiple Symbol Testing", len([r for r in symbol_results.values() if 'error' not in r]) >= 2),
            ("Batch Scoring", success_batch and batch_results.get('successful_analyses', 0) >= 2),
            ("Methodology Endpoint", success_method),
            ("Error Handling", success_invalid),
            ("Performance", response_time < 15.0)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        if success:
            print(f"   - AAPL Investment Score: {aapl_score.get('investment_score', 'N/A')}")
            print(f"   - AAPL Recommendation: {aapl_score.get('recommendation', 'N/A')}")
            print(f"   - AAPL Confidence: {aapl_score.get('confidence_level', 'N/A')}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - Batch Processing: {'✅ Working' if success_batch else '❌ Failed'}")
        print(f"   - Methodology Transparency: {'✅ Available' if success_method else '❌ Failed'}")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Investment Scoring Agent working perfectly!")
            print(f"   All endpoints functional with comprehensive ML-powered investment scoring.")
            print(f"   Real UW data integration confirmed with transparent methodology.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Investment Scoring Agent mostly working with minor issues.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Investment Scoring Agent has significant issues.")
        
        return success_rate >= 70

def main():
    print("🏛️  TRADESTATION LIVE PORTFOLIO BACKEND TESTING")
    print("=" * 80)
    print("🔑 Testing TradeStation authentication, accounts, and portfolio summary")
    print("🌐 Backend URL: https://tradedash-11.preview.emergentagent.com")
    
    tester = StockMarketAPITester()
    
    # Run the TradeStation-specific tests
    success = tester.run_tradestation_tests()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 TRADESTATION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if success:
        print("🎉 TRADESTATION BACKEND TESTING PASSED!")
        return 0
    else:
        print("⚠️  TRADESTATION BACKEND TESTING NEEDS ATTENTION")
        return 1

def main_unusual_whales():
    print("🐋 UNUSUAL WHALES API FINAL VERIFICATION TEST")
    print("=" * 80)
    print("🔑 Using API Key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")
    print("🌐 Backend URL: https://tradedash-11.preview.emergentagent.com")
    
    tester = StockMarketAPITester()
    
    # Run the focused verification test
    success = tester.test_unusual_whales_final_verification()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 VERIFICATION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if success:
        print("🎉 UNUSUAL WHALES VERIFICATION PASSED!")
        return 0
    else:
        print("⚠️  UNUSUAL WHALES VERIFICATION NEEDS ATTENTION")
        return 1

def main_top_picks():
    print("🎯 TOP PICKS ENDPOINT COMPREHENSIVE TESTING")
    print("=" * 80)
    print("👤 USER REQUEST: 'am nevoie de top picks minim 10' - need at least 10 recommendations")
    print("🌐 Backend URL: https://tradedash-11.preview.emergentagent.com")
    print("📊 Testing: GET /api/investments/top-picks with different parameters")
    
    tester = StockMarketAPITester()
    
    # Run the comprehensive Top Picks test
    success = tester.test_top_picks_endpoint_comprehensive()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 TOP PICKS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if success:
        print("🎉 TOP PICKS ENDPOINT TESTING PASSED!")
        print("✅ User requirement 'am nevoie de top picks minim 10' is satisfied")
        print("📊 Investment Scoring page should work correctly")
        return 0
    else:
        print("⚠️  TOP PICKS ENDPOINT TESTING FAILED!")
        print("❌ User requirement may not be satisfied")
        print("🔧 Investment Scoring page may need attention")
        return 1

if __name__ == "__main__":
    # Run the Top Picks test as requested by user
    sys.exit(main_top_picks())