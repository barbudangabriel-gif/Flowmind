import requests
import sys
from datetime import datetime
import json

class TradeStationAPITester:
    def __init__(self, base_url="https://put-selling-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []

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
                    self.issues_found.append(f"{name}: Status {response.status_code} - {error_data}")
                except:
                    print(f"   Error: {response.text}")
                    self.issues_found.append(f"{name}: Status {response.status_code} - {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            self.issues_found.append(f"{name}: Request timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.issues_found.append(f"{name}: {str(e)}")
            return False, {}

    def test_tradestation_authentication_status(self):
        """Test TradeStation authentication status - CRITICAL FOR LOADING ISSUE"""
        print("\n🔐 PHASE 1: TradeStation Authentication Status Check")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation authentication is working")
        print("📋 REQUIREMENT: Check if user is authenticated to access portfolio data")
        
        success, auth_data = self.run_test("TradeStation Auth Status", "GET", "auth/tradestation/status", 200)
        
        if not success:
            print("❌ CRITICAL: TradeStation authentication status endpoint failed")
            return False, {}
        
        # Analyze authentication data
        authenticated = auth_data.get('authenticated', False)
        environment = auth_data.get('environment', 'UNKNOWN')
        has_access_token = auth_data.get('has_access_token', False)
        
        print(f"📊 Authentication Status: {authenticated}")
        print(f"📊 Environment: {environment}")
        print(f"📊 Has Access Token: {has_access_token}")
        
        if authenticated and has_access_token:
            print("✅ TradeStation authentication is working correctly")
            auth_working = True
        else:
            print("❌ CRITICAL: TradeStation authentication issues detected")
            print("   This could explain why IndividualPortfolio is stuck in loading state")
            self.issues_found.append("TradeStation not authenticated - portfolio data unavailable")
            auth_working = False
        
        return auth_working, auth_data

    def test_tradestation_accounts(self):
        """Test TradeStation accounts endpoint - CRITICAL FOR PORTFOLIO ACCESS"""
        print("\n🏛️ PHASE 2: TradeStation Accounts Access")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation accounts can be fetched")
        print("📋 REQUIREMENT: GET /api/tradestation/accounts should return account data")
        
        success, accounts_data = self.run_test("TradeStation Accounts", "GET", "tradestation/accounts", 200)
        
        if not success:
            print("❌ CRITICAL: TradeStation accounts endpoint failed")
            print("   This is likely why IndividualPortfolio is stuck loading")
            return False, {}
        
        # Analyze accounts data
        accounts = accounts_data.get('accounts', [])
        if isinstance(accounts_data, list):
            accounts = accounts_data
        
        print(f"📊 Accounts Found: {len(accounts)}")
        
        if len(accounts) == 0:
            print("❌ CRITICAL: No TradeStation accounts found")
            print("   This explains the loading issue - no account data to display")
            self.issues_found.append("No TradeStation accounts available")
            return False, {}
        
        # Display account information
        target_account_id = None
        for i, account in enumerate(accounts):
            account_id = account.get('account_id', 'N/A')
            account_type = account.get('account_type', 'N/A')
            status = account.get('status', 'N/A')
            
            print(f"   Account {i+1}: {account_id}")
            print(f"     - Type: {account_type}")
            print(f"     - Status: {status}")
            
            if status == 'Active' and target_account_id is None:
                target_account_id = account_id
                print(f"     ✅ Will use this account for position testing")
        
        if target_account_id:
            print(f"✅ TradeStation accounts accessible - Target Account: {target_account_id}")
            return True, {'target_account_id': target_account_id, 'accounts': accounts}
        else:
            print("❌ CRITICAL: No active TradeStation accounts found")
            self.issues_found.append("No active TradeStation accounts")
            return False, {}

    def test_tradestation_positions(self, account_id):
        """Test TradeStation positions endpoint - CORE ISSUE INVESTIGATION"""
        print(f"\n📊 PHASE 3: TradeStation Positions Data for Account {account_id}")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify position data can be fetched from TradeStation")
        print("📋 REQUIREMENT: GET /api/tradestation/accounts/{account_id}/positions")
        
        success, positions_data = self.run_test(
            f"TradeStation Positions (Account {account_id})", 
            "GET", 
            f"tradestation/accounts/{account_id}/positions", 
            200
        )
        
        if not success:
            print("❌ CRITICAL: TradeStation positions endpoint failed")
            print("   This is the ROOT CAUSE of IndividualPortfolio loading issue")
            return False, {}
        
        # Analyze positions data structure
        print(f"\n📋 Analyzing Positions Data Structure:")
        print(f"   Response Type: {type(positions_data)}")
        print(f"   Response Keys: {list(positions_data.keys()) if isinstance(positions_data, dict) else 'Not a dict'}")
        
        # Check for nested data structure
        positions = []
        if 'data' in positions_data:
            positions = positions_data['data']
            print(f"   ✅ Found positions in 'data' field: {len(positions)} positions")
            print(f"   🚨 FRONTEND ISSUE IDENTIFIED: Frontend may need to access response.data instead of response")
        elif isinstance(positions_data, list):
            positions = positions_data
            print(f"   ✅ Positions at root level: {len(positions)} positions")
        elif 'positions' in positions_data:
            positions = positions_data['positions']
            print(f"   ✅ Found positions in 'positions' field: {len(positions)} positions")
        else:
            print(f"   ❌ CRITICAL: Cannot find positions data in response")
            self.issues_found.append("Positions data structure unclear")
            return False, {}
        
        if len(positions) == 0:
            print("❌ CRITICAL: No positions found in TradeStation account")
            print("   This could explain empty portfolio display")
            self.issues_found.append("No positions in TradeStation account")
            return False, {}
        
        # Analyze position data structure
        print(f"\n📊 Position Data Analysis:")
        print(f"   Total Positions: {len(positions)}")
        
        # Check first few positions for data quality
        for i, position in enumerate(positions[:3]):
            symbol = position.get('symbol', 'N/A')
            quantity = position.get('quantity', 0)
            market_value = position.get('market_value', 0)
            asset_type = position.get('asset_type', 'N/A')
            
            print(f"   Position {i+1}: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Market Value: ${market_value:,.2f}")
            print(f"     - Asset Type: {asset_type}")
        
        # Calculate total portfolio value
        total_value = sum(pos.get('market_value', 0) for pos in positions)
        print(f"\n💰 Portfolio Summary:")
        print(f"   Total Positions: {len(positions)}")
        print(f"   Total Market Value: ${total_value:,.2f}")
        
        # Check for required fields that frontend needs
        required_fields = ['symbol', 'quantity', 'market_value', 'current_price']
        missing_fields_count = 0
        
        for position in positions[:5]:  # Check first 5 positions
            missing = [field for field in required_fields if field not in position]
            if missing:
                missing_fields_count += 1
        
        if missing_fields_count > 0:
            print(f"⚠️ WARNING: {missing_fields_count}/5 positions missing some required fields")
            print(f"   This could cause frontend display issues")
        else:
            print(f"✅ All positions have required fields for frontend display")
        
        return True, {
            'positions_count': len(positions),
            'total_value': total_value,
            'data_structure': 'nested' if 'data' in positions_data else 'direct',
            'positions': positions[:5]  # Sample positions
        }

    def test_data_structure_compatibility(self, positions_response):
        """Test if data structure matches frontend expectations"""
        print(f"\n🔧 PHASE 4: Frontend Data Structure Compatibility")
        print("=" * 80)
        print("🎯 OBJECTIVE: Identify data structure issues causing loading problems")
        
        # Check if response has nested structure
        if 'data' in positions_response:
            print("🚨 CRITICAL FINDING: Response uses nested 'data' structure")
            print("   Backend Response: { data: [...positions...] }")
            print("   Frontend Expectation: [...positions...] or { positions: [...] }")
            print("   SOLUTION: Frontend needs to access response.data instead of response")
            
            self.issues_found.append("Data structure mismatch - frontend needs response.data access")
            return False
        else:
            print("✅ Data structure appears compatible with frontend expectations")
            return True

    def test_portfolio_management_integration(self):
        """Test Portfolio Management Service integration with TradeStation"""
        print(f"\n🔄 PHASE 5: Portfolio Management Service Integration")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test if Portfolio Management Service can access TradeStation data")
        
        success, portfolio_data = self.run_test(
            "Portfolio Management - TradeStation Main", 
            "GET", 
            "portfolio-management/portfolios/tradestation-main/positions", 
            200
        )
        
        if not success:
            print("❌ Portfolio Management Service cannot access TradeStation data")
            return False, {}
        
        # Check if using real TradeStation data
        data_source = portfolio_data.get('data_source', 'unknown')
        positions = portfolio_data.get('positions', [])
        
        print(f"📊 Data Source: {data_source}")
        print(f"📊 Positions Count: {len(positions)}")
        
        if 'mock' in data_source.lower() or 'fallback' in data_source.lower():
            print("⚠️ WARNING: Portfolio Management using mock/fallback data")
            print("   This suggests TradeStation integration issues")
            self.issues_found.append("Portfolio Management using mock data instead of TradeStation")
            return False, portfolio_data
        else:
            print("✅ Portfolio Management successfully using TradeStation data")
            return True, portfolio_data

    def run_comprehensive_test(self):
        """Run comprehensive TradeStation API test to diagnose loading issues"""
        print("🚀 TRADESTATION API COMPREHENSIVE DIAGNOSTIC TEST")
        print("=" * 100)
        print("🎯 OBJECTIVE: Diagnose why IndividualPortfolio component is stuck in loading state")
        print("📋 FOCUS AREAS:")
        print("   1. TradeStation Authentication Status")
        print("   2. TradeStation Accounts Access")
        print("   3. TradeStation Positions Data Retrieval")
        print("   4. Data Structure Compatibility")
        print("   5. Portfolio Management Integration")
        print("🔍 EXPECTED OUTCOME: Identify root cause of loading issue")
        
        # Phase 1: Authentication
        auth_working, auth_data = self.test_tradestation_authentication_status()
        
        if not auth_working:
            print("\n🚨 CRITICAL ISSUE IDENTIFIED: TradeStation Authentication Failed")
            print("   RECOMMENDATION: User needs to authenticate with TradeStation")
            print("   ACTION: Navigate to /auth/tradestation/login")
            return self.generate_final_report("Authentication Failure")
        
        # Phase 2: Accounts
        accounts_working, accounts_data = self.test_tradestation_accounts()
        
        if not accounts_working:
            print("\n🚨 CRITICAL ISSUE IDENTIFIED: TradeStation Accounts Not Accessible")
            print("   RECOMMENDATION: Check TradeStation API integration")
            return self.generate_final_report("Accounts Access Failure")
        
        target_account_id = accounts_data.get('target_account_id')
        
        # Phase 3: Positions
        positions_working, positions_data = self.test_tradestation_positions(target_account_id)
        
        if not positions_working:
            print("\n🚨 CRITICAL ISSUE IDENTIFIED: TradeStation Positions Not Accessible")
            print("   RECOMMENDATION: Check TradeStation positions API endpoint")
            return self.generate_final_report("Positions Access Failure")
        
        # Phase 4: Data Structure
        structure_compatible = self.test_data_structure_compatibility(positions_data)
        
        # Phase 5: Portfolio Management
        portfolio_mgmt_working, portfolio_data = self.test_portfolio_management_integration()
        
        # Generate comprehensive report
        return self.generate_final_report("Complete Analysis", {
            'auth_working': auth_working,
            'accounts_working': accounts_working,
            'positions_working': positions_working,
            'structure_compatible': structure_compatible,
            'portfolio_mgmt_working': portfolio_mgmt_working,
            'positions_count': positions_data.get('positions_count', 0),
            'total_value': positions_data.get('total_value', 0),
            'data_structure': positions_data.get('data_structure', 'unknown')
        })

    def generate_final_report(self, analysis_type, results=None):
        """Generate comprehensive diagnostic report"""
        print(f"\n📋 FINAL DIAGNOSTIC REPORT: {analysis_type}")
        print("=" * 100)
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.issues_found:
            print(f"\n🚨 ISSUES IDENTIFIED:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        if results:
            print(f"\n📈 DETAILED RESULTS:")
            print(f"   Authentication Working: {'✅' if results.get('auth_working') else '❌'}")
            print(f"   Accounts Accessible: {'✅' if results.get('accounts_working') else '❌'}")
            print(f"   Positions Accessible: {'✅' if results.get('positions_working') else '❌'}")
            print(f"   Data Structure Compatible: {'✅' if results.get('structure_compatible') else '❌'}")
            print(f"   Portfolio Management Working: {'✅' if results.get('portfolio_mgmt_working') else '❌'}")
            
            if results.get('positions_count'):
                print(f"   Positions Found: {results['positions_count']}")
                print(f"   Total Portfolio Value: ${results['total_value']:,.2f}")
                print(f"   Data Structure: {results['data_structure']}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        if not results:
            print(f"   ❌ {analysis_type} - Cannot proceed with further testing")
        elif not results.get('auth_working'):
            print(f"   🔐 Authentication Issue - User not logged into TradeStation")
            print(f"   📝 SOLUTION: User needs to authenticate at /auth/tradestation/login")
        elif not results.get('accounts_working'):
            print(f"   🏛️ Accounts Access Issue - TradeStation accounts not accessible")
            print(f"   📝 SOLUTION: Check TradeStation API integration and credentials")
        elif not results.get('positions_working'):
            print(f"   📊 Positions Access Issue - Cannot fetch position data")
            print(f"   📝 SOLUTION: Check TradeStation positions API endpoint")
        elif not results.get('structure_compatible'):
            print(f"   🔧 Data Structure Issue - Frontend/Backend data format mismatch")
            print(f"   📝 SOLUTION: Frontend needs to access response.data instead of response")
        elif not results.get('portfolio_mgmt_working'):
            print(f"   🔄 Integration Issue - Portfolio Management not using TradeStation data")
            print(f"   📝 SOLUTION: Fix Portfolio Management Service TradeStation integration")
        else:
            print(f"   ✅ All TradeStation APIs working correctly")
            print(f"   🤔 Loading issue may be frontend-specific (network, parsing, etc.)")
        
        print(f"\n💡 RECOMMENDATIONS FOR MAIN AGENT:")
        
        if not results or not results.get('auth_working'):
            print(f"   1. 🔐 Ensure user completes TradeStation OAuth authentication")
            print(f"   2. 🔗 Verify TradeStation API credentials are correct")
            print(f"   3. 🌐 Check TradeStation environment (LIVE vs PAPER)")
        elif not results.get('structure_compatible'):
            print(f"   1. 🔧 Update frontend to access response.data for positions")
            print(f"   2. 📝 Modify IndividualPortfolio component data parsing")
            print(f"   3. 🧪 Test frontend with corrected data access pattern")
        elif results.get('positions_count', 0) > 0:
            print(f"   1. ✅ TradeStation API is working correctly")
            print(f"   2. 🔍 Investigate frontend network requests and error handling")
            print(f"   3. 🐛 Check browser console for JavaScript errors")
            print(f"   4. 📱 Verify frontend API URL configuration")
        else:
            print(f"   1. 🔄 Restart TradeStation services")
            print(f"   2. 🔍 Check TradeStation API rate limits")
            print(f"   3. 📞 Contact TradeStation API support if issues persist")
        
        success_rate = (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0
        return success_rate >= 70

if __name__ == "__main__":
    print("🚀 Starting TradeStation API Diagnostic Test")
    print("🎯 Focus: Diagnosing IndividualPortfolio loading issues")
    
    tester = TradeStationAPITester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 DIAGNOSTIC COMPLETE: Issues identified and solutions provided")
    else:
        print(f"\n🚨 DIAGNOSTIC COMPLETE: Critical issues found requiring immediate attention")
    
    sys.exit(0 if success else 1)