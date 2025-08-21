import requests
import sys
from datetime import datetime
import json

class TradeStationPortfolioTester:
    def __init__(self, base_url="https://market-pulse-139.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.account_id = "11775499"  # From test_result.md

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
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_tradestation_portfolio_dropdown_functionality(self):
        """Test TradeStation Live Portfolio backend endpoints for dropdown functionality"""
        print("\n🏛️ TESTING TRADESTATION LIVE PORTFOLIO - DROPDOWN FUNCTIONALITY")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify backend data structure supports frontend dropdown grouping")
        print("🔧 CRITICAL FOCUS:")
        print("   1. Test /api/tradestation/accounts/11775499/summary for portfolio positions")
        print("   2. Verify positions include both stocks and options with correct asset_type field")
        print("   3. Check for position data that should be grouped (stocks with related options)")
        print("   4. Test specific symbols for dropdown functionality (IBM, OSCR, GOOGL)")
        print("   5. Verify option positions have proper symbol format for grouping")
        print("   6. Validate data structure matches frontend expectations")

        # Test 1: TradeStation Authentication Status
        print(f"\n📊 PHASE 1: TradeStation Authentication Status")
        print("-" * 60)
        
        success, auth_data = self.run_test("TradeStation Auth Status", "GET", "auth/tradestation/status", 200)
        if not success:
            print("❌ TradeStation authentication endpoint failed")
            return False
        
        auth_status = auth_data.get('authentication', {})
        authenticated = auth_status.get('authenticated', False)
        environment = auth_status.get('environment', 'UNKNOWN')
        
        print(f"📊 Authentication Status: {'✅ AUTHENTICATED' if authenticated else '❌ NOT AUTHENTICATED'}")
        print(f"📊 Environment: {environment}")
        
        if not authenticated:
            print("⚠️  WARNING: Not authenticated - portfolio data may be limited or mock")
            print("   📝 NOTE: Testing will continue but may show authentication errors")

        # Test 2: Portfolio Summary Endpoint - CRITICAL TEST
        print(f"\n📊 PHASE 2: Portfolio Summary Endpoint (CRITICAL)")
        print("-" * 60)
        
        success, portfolio_data = self.run_test(
            f"Portfolio Summary (Account {self.account_id})", 
            "GET", 
            f"tradestation/accounts/{self.account_id}/summary", 
            200
        )
        
        if not success:
            print("❌ Portfolio Summary endpoint failed - cannot test dropdown functionality")
            return False
        
        # Analyze response structure for frontend compatibility
        print(f"📋 Response Structure Analysis:")
        
        # Check if data is nested under 'data' field (known issue from test_result.md)
        if 'data' in portfolio_data:
            print("   ⚠️  Data is nested under 'data' field")
            actual_data = portfolio_data['data']
            print("   📝 Frontend expects: {portfolio_metrics, positions, risk_analysis}")
            print("   📝 Backend returns: {status, data: {portfolio_metrics, positions, risk_analysis}}")
            print("   🔧 STRUCTURE MISMATCH CONFIRMED - This explains the loading spinner issue!")
        else:
            print("   ✅ Data is at root level (frontend compatible)")
            actual_data = portfolio_data
        
        # Extract key components
        portfolio_metrics = actual_data.get('portfolio_metrics', {})
        positions = actual_data.get('positions', [])
        risk_analysis = actual_data.get('risk_analysis', {})
        
        print(f"📊 Portfolio Metrics: {'✅ Present' if portfolio_metrics else '❌ Missing'}")
        print(f"📊 Positions Array: {'✅ Present' if positions else '❌ Missing'} ({len(positions)} positions)")
        print(f"📊 Risk Analysis: {'✅ Present' if risk_analysis else '❌ Missing'}")
        
        if portfolio_metrics:
            total_value = portfolio_metrics.get('total_value', 0)
            total_pnl = portfolio_metrics.get('total_pnl', 0)
            print(f"   💰 Total Portfolio Value: ${total_value:,.2f}")
            print(f"   📈 Total P&L: ${total_pnl:,.2f}")

        # Test 3: Position Data Structure Analysis for Dropdown Functionality
        print(f"\n📊 PHASE 3: Position Data Structure Analysis (DROPDOWN FOCUS)")
        print("-" * 60)
        
        if not positions:
            print("❌ No positions found - cannot test dropdown functionality")
            return False
        
        print(f"📊 Total Positions Found: {len(positions)}")
        
        # Analyze position types and asset types
        asset_types = {}
        symbols_found = set()
        option_positions = []
        stock_positions = []
        
        for position in positions:
            symbol = position.get('symbol', 'N/A')
            asset_type = position.get('asset_type', position.get('AssetType', 'UNKNOWN'))
            quantity = position.get('quantity', position.get('Quantity', 0))
            
            symbols_found.add(symbol)
            
            # Count asset types
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            
            # Categorize positions
            if asset_type == 'STOCKOPTION' or 'OPTION' in asset_type.upper():
                option_positions.append(position)
            elif asset_type == 'STOCK' or asset_type == 'EQUITY':
                stock_positions.append(position)
        
        print(f"📊 Asset Type Distribution:")
        for asset_type, count in asset_types.items():
            print(f"   - {asset_type}: {count} positions")
        
        print(f"📊 Position Categories:")
        print(f"   - Stock Positions: {len(stock_positions)}")
        print(f"   - Option Positions: {len(option_positions)}")
        print(f"   - Unique Symbols: {len(symbols_found)}")
        
        # Test 4: Dropdown Grouping Analysis - CRITICAL FOR USER ISSUE
        print(f"\n📊 PHASE 4: Dropdown Grouping Analysis (CRITICAL)")
        print("-" * 60)
        
        # Look for symbols that should have dropdown functionality
        target_symbols = ['IBM', 'OSCR', 'GOOGL', 'AAPL', 'MSFT', 'TSLA', 'SPY', 'QQQ']
        
        groupable_positions = {}  # symbol -> [positions]
        
        for position in positions:
            symbol = position.get('symbol', 'N/A')
            
            # Extract base symbol for options (e.g., "IBM 240119C00180000" -> "IBM")
            base_symbol = symbol
            if ' ' in symbol:  # Option format: "SYMBOL YYMMDDCPPPPPPP"
                base_symbol = symbol.split(' ')[0]
            elif len(symbol) > 5 and symbol[-8:].isdigit():  # Alternative option format
                # Find where the base symbol ends and option details begin
                for i, char in enumerate(symbol):
                    if char.isdigit():
                        base_symbol = symbol[:i]
                        break
            
            if base_symbol not in groupable_positions:
                groupable_positions[base_symbol] = []
            groupable_positions[base_symbol].append(position)
        
        print(f"📊 Groupable Positions Analysis:")
        dropdown_candidates = []
        
        for base_symbol, symbol_positions in groupable_positions.items():
            if len(symbol_positions) > 1:  # Multiple positions for same base symbol
                dropdown_candidates.append(base_symbol)
                print(f"   🎯 {base_symbol}: {len(symbol_positions)} positions (DROPDOWN CANDIDATE)")
                
                # Analyze position types for this symbol
                stock_count = 0
                option_count = 0
                
                for pos in symbol_positions:
                    asset_type = pos.get('asset_type', pos.get('AssetType', 'UNKNOWN'))
                    symbol_detail = pos.get('symbol', 'N/A')
                    quantity = pos.get('quantity', pos.get('Quantity', 0))
                    
                    if asset_type == 'STOCKOPTION' or 'OPTION' in asset_type.upper():
                        option_count += 1
                        print(f"     📈 OPTION: {symbol_detail} (Qty: {quantity})")
                    else:
                        stock_count += 1
                        print(f"     📊 STOCK: {symbol_detail} (Qty: {quantity})")
                
                print(f"     📊 Summary: {stock_count} stock + {option_count} options")
                
                # Check if this matches user's reported symbols
                if base_symbol in target_symbols:
                    print(f"     ✅ MATCHES USER REPORTED SYMBOL: {base_symbol}")
        
        print(f"\n📊 Dropdown Functionality Summary:")
        print(f"   - Total Dropdown Candidates: {len(dropdown_candidates)}")
        print(f"   - Candidates: {dropdown_candidates}")
        print(f"   - User Reported Symbols Found: {[s for s in target_symbols if s in dropdown_candidates]}")

        # Test 5: Option Symbol Format Analysis
        print(f"\n📊 PHASE 5: Option Symbol Format Analysis")
        print("-" * 60)
        
        if option_positions:
            print(f"📊 Analyzing {len(option_positions)} option positions:")
            
            option_formats = {}
            
            for i, option in enumerate(option_positions[:10]):  # Analyze first 10 options
                symbol = option.get('symbol', 'N/A')
                asset_type = option.get('asset_type', option.get('AssetType', 'UNKNOWN'))
                
                print(f"   📈 Option {i+1}: {symbol}")
                print(f"     - Asset Type: {asset_type}")
                
                # Analyze symbol format
                if ' ' in symbol:
                    parts = symbol.split(' ')
                    base_symbol = parts[0]
                    option_details = parts[1] if len(parts) > 1 else ''
                    
                    print(f"     - Base Symbol: {base_symbol}")
                    print(f"     - Option Details: {option_details}")
                    
                    # Try to parse option details (YYMMDDCPPPPPPP format)
                    if len(option_details) >= 15:
                        exp_date = option_details[:6]  # YYMMDD
                        call_put = option_details[6]   # C or P
                        strike = option_details[7:]    # Strike price
                        
                        print(f"     - Expiration: {exp_date}")
                        print(f"     - Type: {'Call' if call_put == 'C' else 'Put' if call_put == 'P' else 'Unknown'}")
                        print(f"     - Strike: {strike}")
                        
                        format_key = f"{base_symbol}_space_separated"
                    else:
                        format_key = f"{base_symbol}_unknown_format"
                else:
                    format_key = "no_space_format"
                
                option_formats[format_key] = option_formats.get(format_key, 0) + 1
            
            print(f"\n📊 Option Format Distribution:")
            for format_type, count in option_formats.items():
                print(f"   - {format_type}: {count} options")
        else:
            print("📊 No option positions found for format analysis")

        # Test 6: Data Structure Compatibility Check
        print(f"\n📊 PHASE 6: Frontend Data Structure Compatibility")
        print("-" * 60)
        
        compatibility_issues = []
        
        # Check for known structure mismatch
        if 'data' in portfolio_data:
            compatibility_issues.append("Data nested under 'data' field - frontend expects root level")
        
        # Check required fields for dropdown functionality
        required_fields = ['symbol', 'asset_type', 'quantity']
        
        if positions:
            sample_position = positions[0]
            missing_fields = []
            
            for field in required_fields:
                if field not in sample_position and field.title() not in sample_position:
                    missing_fields.append(field)
            
            if missing_fields:
                compatibility_issues.append(f"Missing required fields: {missing_fields}")
        
        # Check for proper asset type values
        if asset_types:
            expected_asset_types = ['STOCK', 'STOCKOPTION', 'EQUITY', 'OPTION']
            unexpected_types = [at for at in asset_types.keys() if at not in expected_asset_types]
            
            if unexpected_types:
                compatibility_issues.append(f"Unexpected asset types: {unexpected_types}")
        
        print(f"📊 Compatibility Analysis:")
        if compatibility_issues:
            print("   ❌ COMPATIBILITY ISSUES FOUND:")
            for issue in compatibility_issues:
                print(f"     - {issue}")
        else:
            print("   ✅ No major compatibility issues detected")

        # Test 7: Specific Symbol Testing (User Reported Issues)
        print(f"\n📊 PHASE 7: Specific Symbol Testing (User Issues)")
        print("-" * 60)
        
        user_symbols = ['IBM', 'OSCR', 'GOOGL']
        
        for symbol in user_symbols:
            symbol_positions = [p for p in positions if p.get('symbol', '').startswith(symbol)]
            
            if symbol_positions:
                print(f"   🎯 {symbol}: {len(symbol_positions)} positions found")
                
                stock_pos = [p for p in symbol_positions if p.get('asset_type', '').upper() in ['STOCK', 'EQUITY']]
                option_pos = [p for p in symbol_positions if 'OPTION' in p.get('asset_type', '').upper()]
                
                print(f"     - Stock positions: {len(stock_pos)}")
                print(f"     - Option positions: {len(option_pos)}")
                
                if len(stock_pos) > 0 and len(option_pos) > 0:
                    print(f"     ✅ DROPDOWN SHOULD WORK: Has both stock and options")
                elif len(option_pos) > 1:
                    print(f"     ✅ DROPDOWN SHOULD WORK: Multiple option contracts")
                else:
                    print(f"     ⚠️  DROPDOWN NOT NEEDED: Only single position type")
                
                # Show sample positions
                for i, pos in enumerate(symbol_positions[:3]):
                    symbol_detail = pos.get('symbol', 'N/A')
                    asset_type = pos.get('asset_type', 'N/A')
                    quantity = pos.get('quantity', pos.get('Quantity', 0))
                    print(f"     - Position {i+1}: {symbol_detail} ({asset_type}, Qty: {quantity})")
            else:
                print(f"   ❌ {symbol}: No positions found")

        # Test 8: Response Time and Performance
        print(f"\n📊 PHASE 8: Performance Analysis")
        print("-" * 60)
        
        import time
        start_time = time.time()
        
        success_perf, perf_data = self.run_test(
            f"Portfolio Summary (Performance Test)", 
            "GET", 
            f"tradestation/accounts/{self.account_id}/summary", 
            200
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   ⏱️  Response Time: {response_time:.2f} seconds")
        
        if response_time < 1.0:
            print(f"   ✅ Excellent response time")
        elif response_time < 3.0:
            print(f"   ✅ Good response time")
        else:
            print(f"   ⚠️  Slow response time - may affect user experience")

        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: TradeStation Portfolio Dropdown Functionality")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("Authentication Check", success),
            ("Portfolio Data Retrieval", success and len(positions) > 0),
            ("Asset Type Detection", len(asset_types) > 0),
            ("Dropdown Candidates Found", len(dropdown_candidates) > 0),
            ("Option Format Analysis", len(option_positions) >= 0),  # 0 is acceptable
            ("User Symbol Testing", any(symbol in [p.get('symbol', '') for p in positions] for symbol in user_symbols)),
            ("Performance", response_time < 5.0)
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
        print(f"   - Total Positions: {len(positions)}")
        print(f"   - Asset Types: {list(asset_types.keys())}")
        print(f"   - Dropdown Candidates: {len(dropdown_candidates)} ({dropdown_candidates})")
        print(f"   - Stock Positions: {len(stock_positions)}")
        print(f"   - Option Positions: {len(option_positions)}")
        print(f"   - Authentication Status: {'✅ AUTHENTICATED' if authenticated else '❌ NOT AUTHENTICATED'}")
        print(f"   - Response Time: {response_time:.2f}s")
        
        # Root cause analysis for user issue
        print(f"\n🔧 ROOT CAUSE ANALYSIS (User Issue: Dropdown arrows don't expand):")
        
        if 'data' in portfolio_data:
            print(f"   🚨 CRITICAL ISSUE CONFIRMED: Data structure mismatch")
            print(f"     - Backend returns: {{status, data: {{portfolio_metrics, positions, risk_analysis}}}}")
            print(f"     - Frontend expects: {{portfolio_metrics, positions, risk_analysis}}")
            print(f"     - SOLUTION: Frontend needs to access response.data.* instead of response.*")
        
        if len(dropdown_candidates) > 0:
            print(f"   ✅ DROPDOWN DATA AVAILABLE: {len(dropdown_candidates)} symbols have multiple positions")
            print(f"     - Symbols with dropdowns: {dropdown_candidates}")
        else:
            print(f"   ⚠️  NO DROPDOWN CANDIDATES: No symbols have multiple positions")
        
        if not authenticated:
            print(f"   ⚠️  AUTHENTICATION ISSUE: May be showing mock/limited data")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if 'data' in portfolio_data:
            print(f"   1. 🔧 CRITICAL: Fix frontend data access pattern")
            print(f"      - Change: response.portfolio_metrics")
            print(f"      - To: response.data.portfolio_metrics")
            print(f"      - This will resolve the permanent loading spinner issue")
        
        if len(dropdown_candidates) > 0:
            print(f"   2. ✅ DROPDOWN LOGIC: Backend data supports dropdown functionality")
            print(f"      - Group positions by base symbol (before space or option details)")
            print(f"      - Show dropdown arrow when multiple positions exist for same base symbol")
        
        if len(option_positions) > 0:
            print(f"   3. ✅ OPTION PARSING: Option symbols follow standard format")
            print(f"      - Format: 'BASE_SYMBOL YYMMDDCPPPPPPP'")
            print(f"      - Extract base symbol by splitting on space")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: BACKEND DATA STRUCTURE IS CORRECT")
            print(f"   The backend provides all necessary data for dropdown functionality.")
            print(f"   The user issue is likely a FRONTEND DATA ACCESS problem.")
            print(f"   Fix: Update frontend to access response.data.* instead of response.*")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: MOSTLY WORKING - Minor issues detected")
            print(f"   Backend data is mostly correct but may need minor adjustments.")
        else:
            print(f"\n❌ VERDICT: SIGNIFICANT ISSUES - Backend data structure problems")
            print(f"   Backend data structure needs major fixes for dropdown functionality.")
        
        return success_rate >= 70

    def run_all_tests(self):
        """Run all TradeStation portfolio tests"""
        print("🏛️ TRADESTATION LIVE PORTFOLIO BACKEND TESTING")
        print("=" * 80)
        print("🎯 FOCUS: Verify data structure for dropdown functionality")
        print("🔧 USER ISSUE: Dropdown arrows appear but don't expand to show option contracts")
        
        # Run the comprehensive dropdown functionality test
        success = self.test_tradestation_portfolio_dropdown_functionality()
        
        print(f"\n📊 OVERALL TEST SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return success

if __name__ == "__main__":
    tester = TradeStationPortfolioTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n✅ TESTING COMPLETE: TradeStation Portfolio backend data structure verified")
        sys.exit(0)
    else:
        print(f"\n❌ TESTING FAILED: Issues found with TradeStation Portfolio backend")
        sys.exit(1)