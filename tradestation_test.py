import requests
import sys
from datetime import datetime, timedelta
import json
import time

class TradeStationAPITester:
    def __init__(self, base_url="https://flowmind-live.preview.emergentagent.com"):
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
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            end_time = time.time()
            response_time = end_time - start_time

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} ({response_time:.2f}s)")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 1000:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response: Dict with keys: {list(response_data.keys())}")
                    
                    self.test_results.append({
                        "name": name,
                        "status": "PASS",
                        "response_time": response_time,
                        "data": response_data
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        "name": name,
                        "status": "PASS",
                        "response_time": response_time,
                        "data": {}
                    })
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({
                        "name": name,
                        "status": "FAIL",
                        "response_time": response_time,
                        "error": error_data
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        "name": name,
                        "status": "FAIL",
                        "response_time": response_time,
                        "error": response.text
                    })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            self.test_results.append({
                "name": name,
                "status": "TIMEOUT",
                "response_time": 30.0,
                "error": "Request timeout"
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "response_time": 0,
                "error": str(e)
            })
            return False, {}

    def test_tradestation_authentication(self):
        """Test TradeStation OAuth Authentication System"""
        print("\n🔐 TESTING TRADESTATION AUTHENTICATION SYSTEM")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test OAuth authentication endpoints and configuration")
        
        # Test 1: Authentication Status
        print(f"\n📊 PHASE 1: Authentication Status Check")
        print("-" * 60)
        
        success, auth_status = self.run_test(
            "TradeStation Auth Status", 
            "GET", 
            "auth/tradestation/status", 
            200
        )
        
        if success:
            auth_data = auth_status.get('authentication', {})
            config_data = auth_status.get('api_configuration', {})
            
            print(f"   🔐 Authenticated: {auth_data.get('authenticated', False)}")
            print(f"   🌐 Environment: {config_data.get('environment', 'unknown')}")
            print(f"   🔧 Credentials Configured: {config_data.get('credentials_configured', False)}")
            print(f"   🔗 Base URL: {config_data.get('base_url', 'unknown')}")
            
            if auth_data.get('authenticated'):
                print(f"   ✅ TradeStation authentication is active")
                if 'connection_test' in auth_status:
                    conn_test = auth_status['connection_test']
                    print(f"   🔗 Connection Test: {conn_test}")
            else:
                print(f"   ⚠️  TradeStation not authenticated (expected for testing)")
        
        # Test 2: OAuth Login URL Generation
        print(f"\n🔗 PHASE 2: OAuth Login URL Generation")
        print("-" * 60)
        
        success, login_data = self.run_test(
            "TradeStation OAuth Login", 
            "GET", 
            "auth/tradestation/login", 
            200
        )
        
        if success:
            auth_url = login_data.get('auth_url', '')
            instructions = login_data.get('instructions', [])
            
            print(f"   🔗 Auth URL Generated: {'✅ YES' if auth_url else '❌ NO'}")
            if auth_url:
                print(f"   🌐 URL Length: {len(auth_url)} characters")
                print(f"   🔧 Contains OAuth params: {'✅ YES' if 'oauth' in auth_url.lower() or 'authorize' in auth_url.lower() else '❌ NO'}")
            
            print(f"   📋 Instructions Provided: {len(instructions)}")
            for i, instruction in enumerate(instructions, 1):
                print(f"     {i}. {instruction}")
        
        return success

    def test_tradestation_portfolio_endpoints(self):
        """Test TradeStation Portfolio Management Endpoints"""
        print("\n📊 TESTING TRADESTATION PORTFOLIO ENDPOINTS")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test portfolio data retrieval and account management")
        
        # Test 1: Get Accounts
        print(f"\n👤 PHASE 1: Account Retrieval")
        print("-" * 60)
        
        success, accounts_data = self.run_test(
            "TradeStation Accounts", 
            "GET", 
            "tradestation/accounts", 
            200
        )
        
        account_id = None
        if success:
            accounts = accounts_data.get('accounts', [])
            count = accounts_data.get('count', 0)
            
            print(f"   👤 Accounts Found: {count}")
            
            if accounts:
                account_id = accounts[0].get('account_id') or accounts[0].get('AccountID') or 'test_account'
                print(f"   🔑 Using Account ID: {account_id}")
                
                # Show account details
                first_account = accounts[0]
                print(f"   📊 Account Details:")
                for key, value in first_account.items():
                    print(f"     - {key}: {value}")
            else:
                print(f"   ⚠️  No accounts found - using test account ID")
                account_id = "test_account_123"
        
        if not account_id:
            account_id = "test_account_123"
        
        # Test 2: Account Summary
        print(f"\n📈 PHASE 2: Account Summary")
        print("-" * 60)
        
        success, summary_data = self.run_test(
            "TradeStation Account Summary", 
            "GET", 
            f"tradestation/accounts/{account_id}/summary", 
            200
        )
        
        if success:
            data = summary_data.get('data', {})
            
            # Check for portfolio analysis components
            portfolio_summary = data.get('portfolio_summary', {})
            performance_metrics = data.get('performance_metrics', {})
            risk_analysis = data.get('risk_analysis', {})
            
            print(f"   📊 Portfolio Summary: {'✅ Present' if portfolio_summary else '❌ Missing'}")
            print(f"   📈 Performance Metrics: {'✅ Present' if performance_metrics else '❌ Missing'}")
            print(f"   ⚖️  Risk Analysis: {'✅ Present' if risk_analysis else '❌ Missing'}")
            
            if portfolio_summary:
                total_value = portfolio_summary.get('total_market_value', 0)
                total_cost = portfolio_summary.get('total_cost_basis', 0)
                unrealized_pnl = portfolio_summary.get('unrealized_pnl', 0)
                
                print(f"   💰 Total Market Value: ${total_value:,.2f}")
                print(f"   💸 Total Cost Basis: ${total_cost:,.2f}")
                print(f"   📊 Unrealized P&L: ${unrealized_pnl:,.2f}")
        
        # Test 3: Positions
        print(f"\n📋 PHASE 3: Position Retrieval")
        print("-" * 60)
        
        success, positions_data = self.run_test(
            "TradeStation Positions", 
            "GET", 
            f"tradestation/accounts/{account_id}/positions", 
            200
        )
        
        if success:
            positions = positions_data.get('positions', [])
            summary = positions_data.get('summary', {})
            
            print(f"   📋 Positions Found: {len(positions)}")
            print(f"   📊 Summary: {summary}")
            
            if positions:
                # Show first position details
                first_pos = positions[0]
                print(f"   📊 Sample Position:")
                print(f"     - Symbol: {first_pos.get('symbol', 'N/A')}")
                print(f"     - Quantity: {first_pos.get('quantity', 0)}")
                print(f"     - Market Value: ${first_pos.get('market_value', 0):,.2f}")
                print(f"     - Asset Type: {first_pos.get('asset_type', 'N/A')}")
        
        # Test 4: Positions with Filters
        print(f"\n🔍 PHASE 4: Position Filtering")
        print("-" * 60)
        
        # Test equity positions filter
        success, eq_positions = self.run_test(
            "TradeStation Positions (Equity Filter)", 
            "GET", 
            f"tradestation/accounts/{account_id}/positions", 
            200,
            params={"asset_type": "EQ", "min_value": 1000}
        )
        
        if success:
            eq_pos = eq_positions.get('positions', [])
            print(f"   📊 Equity Positions (>$1000): {len(eq_pos)}")
        
        # Test 5: Account Balances
        print(f"\n💰 PHASE 5: Account Balances")
        print("-" * 60)
        
        success, balances_data = self.run_test(
            "TradeStation Account Balances", 
            "GET", 
            f"tradestation/accounts/{account_id}/balances", 
            200
        )
        
        if success:
            balances = balances_data.get('balances', {})
            
            print(f"   💰 Account Balances:")
            for key, value in balances.items():
                if isinstance(value, (int, float)):
                    print(f"     - {key}: ${value:,.2f}")
                else:
                    print(f"     - {key}: {value}")
        
        return success

    def test_tradestation_trading_endpoints(self):
        """Test TradeStation Trading and Order Management Endpoints"""
        print("\n⚡ TESTING TRADESTATION TRADING ENDPOINTS")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test order validation, placement, and management")
        
        account_id = "test_account_123"
        
        # Test 1: Order Validation
        print(f"\n✅ PHASE 1: Order Validation")
        print("-" * 60)
        
        test_order = {
            "symbol": "AAPL",
            "quantity": 10,
            "order_type": "Market",
            "time_in_force": "Day",
            "trade_action": "Buy"
        }
        
        success, validation_data = self.run_test(
            "TradeStation Order Validation", 
            "POST", 
            f"tradestation/accounts/{account_id}/orders/validate", 
            200,
            data=test_order
        )
        
        if success:
            validation = validation_data.get('validation', {})
            risk_checks = validation_data.get('risk_checks', {})
            
            print(f"   ✅ Order Valid: {validation.get('is_valid', False)}")
            print(f"   💰 Estimated Cost: ${validation.get('estimated_cost', 0):,.2f}")
            print(f"   ⚖️  Risk Checks Passed: {risk_checks.get('all_passed', False)}")
            
            if 'warnings' in validation:
                warnings = validation['warnings']
                print(f"   ⚠️  Warnings: {len(warnings)}")
                for warning in warnings:
                    print(f"     - {warning}")
        
        # Test 2: Get Orders History
        print(f"\n📋 PHASE 2: Orders History")
        print("-" * 60)
        
        success, orders_data = self.run_test(
            "TradeStation Orders History", 
            "GET", 
            f"tradestation/accounts/{account_id}/orders", 
            200
        )
        
        if success:
            orders = orders_data.get('orders', [])
            summary = orders_data.get('summary', {})
            
            print(f"   📋 Orders Found: {len(orders)}")
            print(f"   📊 Summary: {summary}")
            
            if orders:
                # Show first order details
                first_order = orders[0]
                print(f"   📊 Sample Order:")
                print(f"     - Symbol: {first_order.get('symbol', 'N/A')}")
                print(f"     - Quantity: {first_order.get('quantity', 0)}")
                print(f"     - Status: {first_order.get('status', 'N/A')}")
                print(f"     - Order Type: {first_order.get('order_type', 'N/A')}")
        
        # Test 3: Trading Summary
        print(f"\n📈 PHASE 3: Trading Summary")
        print("-" * 60)
        
        success, trading_summary = self.run_test(
            "TradeStation Trading Summary", 
            "GET", 
            f"tradestation/accounts/{account_id}/trading-summary", 
            200
        )
        
        if success:
            summary = trading_summary.get('summary', {})
            
            print(f"   📊 Trading Summary:")
            for key, value in summary.items():
                if isinstance(value, (int, float)):
                    if 'amount' in key.lower() or 'value' in key.lower() or 'pnl' in key.lower():
                        print(f"     - {key}: ${value:,.2f}")
                    else:
                        print(f"     - {key}: {value}")
                else:
                    print(f"     - {key}: {value}")
        
        # Test 4: Order Status Check (with test order ID)
        print(f"\n🔍 PHASE 4: Order Status Check")
        print("-" * 60)
        
        test_order_id = "test_order_123"
        
        success, order_status = self.run_test(
            "TradeStation Order Status", 
            "GET", 
            f"tradestation/accounts/{account_id}/orders/{test_order_id}/status", 
            200
        )
        
        if success:
            status_data = order_status.get('status', {})
            
            print(f"   📊 Order Status:")
            if isinstance(status_data, dict):
                for key, value in status_data.items():
                    print(f"     - {key}: {value}")
            else:
                print(f"     - Status: {status_data}")
        
        return success

    def test_tradestation_market_data_endpoints(self):
        """Test TradeStation Market Data Endpoints"""
        print("\n📊 TESTING TRADESTATION MARKET DATA ENDPOINTS")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test real-time quotes and historical data")
        
        # Test 1: Real-time Quotes (Single Symbol)
        print(f"\n💹 PHASE 1: Real-time Quotes (Single Symbol)")
        print("-" * 60)
        
        success, quote_data = self.run_test(
            "TradeStation Quote (AAPL)", 
            "GET", 
            "tradestation/quotes/AAPL", 
            200
        )
        
        if success:
            quotes = quote_data.get('quotes', [])
            
            if quotes:
                aapl_quote = quotes[0]
                print(f"   📊 AAPL Quote:")
                print(f"     - Symbol: {aapl_quote.get('symbol', 'N/A')}")
                print(f"     - Last Price: ${aapl_quote.get('last_price', 0):.2f}")
                print(f"     - Bid: ${aapl_quote.get('bid', 0):.2f}")
                print(f"     - Ask: ${aapl_quote.get('ask', 0):.2f}")
                print(f"     - Volume: {aapl_quote.get('volume', 0):,}")
                print(f"     - Change: {aapl_quote.get('change', 0):+.2f}")
                print(f"     - Change %: {aapl_quote.get('change_percent', 0):+.2f}%")
        
        # Test 2: Real-time Quotes (Multiple Symbols)
        print(f"\n💹 PHASE 2: Real-time Quotes (Multiple Symbols)")
        print("-" * 60)
        
        success, multi_quotes = self.run_test(
            "TradeStation Quotes (Multiple)", 
            "GET", 
            "tradestation/quotes/AAPL,MSFT,GOOGL", 
            200
        )
        
        if success:
            quotes = multi_quotes.get('quotes', [])
            
            print(f"   📊 Multiple Quotes: {len(quotes)} symbols")
            for quote in quotes:
                symbol = quote.get('symbol', 'N/A')
                price = quote.get('last_price', 0)
                change_pct = quote.get('change_percent', 0)
                print(f"     - {symbol}: ${price:.2f} ({change_pct:+.2f}%)")
        
        # Test 3: Historical Data
        print(f"\n📈 PHASE 3: Historical Data")
        print("-" * 60)
        
        success, hist_data = self.run_test(
            "TradeStation Historical (AAPL)", 
            "GET", 
            "tradestation/historical/AAPL", 
            200,
            params={"interval": "Daily", "period": "1M"}
        )
        
        if success:
            bars = hist_data.get('bars', [])
            
            print(f"   📈 Historical Bars: {len(bars)}")
            
            if bars:
                # Show first and last bar
                first_bar = bars[0]
                last_bar = bars[-1]
                
                print(f"   📊 First Bar:")
                print(f"     - Date: {first_bar.get('date', 'N/A')}")
                print(f"     - Open: ${first_bar.get('open', 0):.2f}")
                print(f"     - High: ${first_bar.get('high', 0):.2f}")
                print(f"     - Low: ${first_bar.get('low', 0):.2f}")
                print(f"     - Close: ${first_bar.get('close', 0):.2f}")
                print(f"     - Volume: {first_bar.get('volume', 0):,}")
                
                print(f"   📊 Last Bar:")
                print(f"     - Date: {last_bar.get('date', 'N/A')}")
                print(f"     - Close: ${last_bar.get('close', 0):.2f}")
        
        return success

    def test_tradestation_risk_management(self):
        """Test TradeStation Risk Management System"""
        print("\n⚖️  TESTING TRADESTATION RISK MANAGEMENT")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test risk limits configuration and enforcement")
        
        # Test 1: Get Current Risk Limits
        print(f"\n📋 PHASE 1: Current Risk Limits")
        print("-" * 60)
        
        success, risk_limits = self.run_test(
            "TradeStation Risk Limits (GET)", 
            "GET", 
            "tradestation/risk-limits", 
            200
        )
        
        if success:
            limits = risk_limits.get('risk_limits', {})
            
            print(f"   ⚖️  Risk Limits Configuration:")
            for key, value in limits.items():
                if isinstance(value, (int, float)):
                    if 'amount' in key.lower() or 'value' in key.lower():
                        print(f"     - {key}: ${value:,.2f}")
                    elif 'percent' in key.lower():
                        print(f"     - {key}: {value:.2f}%")
                    else:
                        print(f"     - {key}: {value}")
                else:
                    print(f"     - {key}: {value}")
        
        # Test 2: Update Risk Limits
        print(f"\n🔧 PHASE 2: Update Risk Limits")
        print("-" * 60)
        
        new_limits = {
            "max_order_value": 50000.0,
            "daily_loss_limit": 10000.0,
            "max_position_size": 1000,
            "sector_concentration_limit": 25.0,
            "minimum_account_balance": 25000.0
        }
        
        success, update_response = self.run_test(
            "TradeStation Risk Limits (PUT)", 
            "PUT", 
            "tradestation/risk-limits", 
            200,
            data=new_limits
        )
        
        if success:
            updated_limits = update_response.get('updated_limits', {})
            
            print(f"   ✅ Risk Limits Updated:")
            for key, value in updated_limits.items():
                if isinstance(value, (int, float)):
                    if 'amount' in key.lower() or 'value' in key.lower():
                        print(f"     - {key}: ${value:,.2f}")
                    elif 'percent' in key.lower():
                        print(f"     - {key}: {value:.2f}%")
                    else:
                        print(f"     - {key}: {value}")
                else:
                    print(f"     - {key}: {value}")
        
        return success

    def test_api_root_with_tradestation(self):
        """Test Updated API Root Endpoint with TradeStation Features"""
        print("\n🏠 TESTING UPDATED API ROOT ENDPOINT")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify API version 5.0.0 and TradeStation endpoint documentation")
        
        success, root_data = self.run_test(
            "API Root with TradeStation", 
            "GET", 
            "", 
            200
        )
        
        if success:
            version = root_data.get('version', 'unknown')
            features = root_data.get('features', [])
            ts_endpoints = root_data.get('tradestation_endpoints', {})
            
            print(f"   📊 API Version: {version}")
            print(f"   ✅ Expected Version 5.0.0: {'✅ YES' if version == '5.0.0' else '❌ NO'}")
            
            print(f"\n   🎯 TradeStation Features:")
            ts_features = [f for f in features if 'tradestation' in f.lower() or '🏛️' in f or '📊' in f or '⚡' in f or '🛡️' in f]
            for feature in ts_features:
                print(f"     - {feature}")
            
            print(f"\n   🔗 TradeStation Endpoints:")
            for category, endpoint in ts_endpoints.items():
                print(f"     - {category}: {endpoint}")
            
            # Verify all expected TradeStation endpoints are documented
            expected_endpoints = [
                'authentication', 'auth_status', 'accounts', 'portfolio_summary',
                'positions', 'balances', 'place_order', 'orders_history', 'trading_summary'
            ]
            
            missing_endpoints = [ep for ep in expected_endpoints if ep not in ts_endpoints]
            if missing_endpoints:
                print(f"   ⚠️  Missing endpoint documentation: {missing_endpoints}")
            else:
                print(f"   ✅ All TradeStation endpoints documented")
        
        return success

    def run_comprehensive_tradestation_tests(self):
        """Run all TradeStation API tests"""
        print("\n🏛️  COMPREHENSIVE TRADESTATION API INTEGRATION TESTING")
        print("=" * 100)
        print("🎯 TESTING SCOPE: Complete TradeStation API integration as requested")
        print("📋 TEST CATEGORIES:")
        print("   1. 🔐 Authentication Testing")
        print("   2. 📊 Portfolio Endpoints Testing") 
        print("   3. ⚡ Trading Endpoints Testing")
        print("   4. 💹 Market Data Endpoints Testing")
        print("   5. ⚖️  Risk Management Testing")
        print("   6. 🏠 Root Endpoint Testing")
        print("   7. 🔧 Error Handling & Integration Testing")
        
        # Run all test categories
        test_results = {}
        
        # 1. Authentication Testing
        test_results['authentication'] = self.test_tradestation_authentication()
        
        # 2. Portfolio Endpoints Testing
        test_results['portfolio'] = self.test_tradestation_portfolio_endpoints()
        
        # 3. Trading Endpoints Testing
        test_results['trading'] = self.test_tradestation_trading_endpoints()
        
        # 4. Market Data Endpoints Testing
        test_results['market_data'] = self.test_tradestation_market_data_endpoints()
        
        # 5. Risk Management Testing
        test_results['risk_management'] = self.test_tradestation_risk_management()
        
        # 6. Root Endpoint Testing
        test_results['root_endpoint'] = self.test_api_root_with_tradestation()
        
        # Generate comprehensive summary
        self.generate_tradestation_test_summary(test_results)
        
        return test_results

    def generate_tradestation_test_summary(self, test_results):
        """Generate comprehensive test summary"""
        print("\n🎯 COMPREHENSIVE TRADESTATION API TEST SUMMARY")
        print("=" * 100)
        
        # Calculate overall statistics
        total_categories = len(test_results)
        passed_categories = sum(1 for result in test_results.values() if result)
        success_rate = (passed_categories / total_categories) * 100
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   - Total Test Categories: {total_categories}")
        print(f"   - Categories Passed: {passed_categories}")
        print(f"   - Overall Success Rate: {success_rate:.1f}%")
        print(f"   - Individual Tests Run: {self.tests_run}")
        print(f"   - Individual Tests Passed: {self.tests_passed}")
        print(f"   - Individual Test Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n📋 CATEGORY RESULTS:")
        category_names = {
            'authentication': '🔐 Authentication System',
            'portfolio': '📊 Portfolio Endpoints',
            'trading': '⚡ Trading Endpoints',
            'market_data': '💹 Market Data Endpoints',
            'risk_management': '⚖️  Risk Management',
            'root_endpoint': '🏠 Root Endpoint'
        }
        
        for category, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            name = category_names.get(category, category)
            print(f"   {status} {name}")
        
        # Detailed findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Authentication findings
        auth_tests = [t for t in self.test_results if 'auth' in t['name'].lower() or 'oauth' in t['name'].lower()]
        auth_passed = sum(1 for t in auth_tests if t['status'] == 'PASS')
        print(f"   - Authentication Tests: {auth_passed}/{len(auth_tests)} passed")
        
        # Portfolio findings
        portfolio_tests = [t for t in self.test_results if 'account' in t['name'].lower() or 'position' in t['name'].lower() or 'balance' in t['name'].lower()]
        portfolio_passed = sum(1 for t in portfolio_tests if t['status'] == 'PASS')
        print(f"   - Portfolio Tests: {portfolio_passed}/{len(portfolio_tests)} passed")
        
        # Trading findings
        trading_tests = [t for t in self.test_results if 'order' in t['name'].lower() or 'trading' in t['name'].lower()]
        trading_passed = sum(1 for t in trading_tests if t['status'] == 'PASS')
        print(f"   - Trading Tests: {trading_passed}/{len(trading_tests)} passed")
        
        # Market data findings
        market_tests = [t for t in self.test_results if 'quote' in t['name'].lower() or 'historical' in t['name'].lower()]
        market_passed = sum(1 for t in market_tests if t['status'] == 'PASS')
        print(f"   - Market Data Tests: {market_passed}/{len(market_tests)} passed")
        
        # Risk management findings
        risk_tests = [t for t in self.test_results if 'risk' in t['name'].lower()]
        risk_passed = sum(1 for t in risk_tests if t['status'] == 'PASS')
        print(f"   - Risk Management Tests: {risk_passed}/{len(risk_tests)} passed")
        
        # Performance analysis
        response_times = [t['response_time'] for t in self.test_results if 'response_time' in t]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"   - Average Response Time: {avg_response_time:.2f}s")
            print(f"   - Maximum Response Time: {max_response_time:.2f}s")
        
        # Error analysis
        failed_tests = [t for t in self.test_results if t['status'] in ['FAIL', 'ERROR', 'TIMEOUT']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   - {test['name']}: {test['status']}")
                if 'error' in test:
                    error_msg = str(test['error'])[:100] + "..." if len(str(test['error'])) > 100 else str(test['error'])
                    print(f"     Error: {error_msg}")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if success_rate >= 85:
            print(f"🎉 EXCELLENT: TradeStation API integration is working excellently!")
            print(f"   All major components are functional and ready for production use.")
            print(f"   Authentication, portfolio management, trading, and risk controls are operational.")
        elif success_rate >= 70:
            print(f"✅ GOOD: TradeStation API integration is mostly working with minor issues.")
            print(f"   Core functionality is available but some endpoints may need attention.")
        elif success_rate >= 50:
            print(f"⚠️  PARTIAL: TradeStation API integration has significant issues.")
            print(f"   Some components are working but major functionality may be impaired.")
        else:
            print(f"❌ CRITICAL: TradeStation API integration has major problems.")
            print(f"   Most endpoints are failing and require immediate attention.")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not test_results.get('authentication', False):
            print(f"   🔐 Authentication: Check TradeStation API credentials and OAuth configuration")
        
        if not test_results.get('portfolio', False):
            print(f"   📊 Portfolio: Verify account access and portfolio service initialization")
        
        if not test_results.get('trading', False):
            print(f"   ⚡ Trading: Check trading service and order management functionality")
        
        if not test_results.get('market_data', False):
            print(f"   💹 Market Data: Verify market data feed and quote service")
        
        if not test_results.get('risk_management', False):
            print(f"   ⚖️  Risk Management: Check risk limit configuration and enforcement")
        
        if success_rate >= 70:
            print(f"   ✅ TradeStation integration is ready for comprehensive testing")
        else:
            print(f"   🔧 Focus on fixing failed endpoints before proceeding")

if __name__ == "__main__":
    print("🏛️  TradeStation API Integration Tester")
    print("=" * 50)
    
    tester = TradeStationAPITester()
    results = tester.run_comprehensive_tradestation_tests()
    
    print(f"\n✅ Testing completed!")
    print(f"📊 Results: {tester.tests_passed}/{tester.tests_run} tests passed")