import requests
import sys


class ComprehensiveTradeStationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.warnings = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")

        try:
            timeout = 30

            if method == "GET":
                response = requests.get(
                    url, headers=headers, params=params, timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    url, json=data, headers=headers, timeout=timeout
                )

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
                print(
                    f"❌ Failed - Expected {expected_status}, got {response.status_code}"
                )
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_tradestation_authentication_comprehensive(self):
        """Comprehensive TradeStation authentication testing"""
        print("\n🔐 COMPREHENSIVE TRADESTATION AUTHENTICATION TESTING")
        print("=" * 80)

        # Test 1: Authentication Status
        success, auth_data = self.run_test(
            "TradeStation Auth Status", "GET", "auth/tradestation/status", 200
        )

        if success:
            authenticated = auth_data.get("authenticated", False)
            environment = auth_data.get("environment", "UNKNOWN")
            has_access_token = auth_data.get("has_access_token", False)

            print(f"📊 Authentication Status: {authenticated}")
            print(f"📊 Environment: {environment}")
            print(f"📊 Has Access Token: {has_access_token}")

            if not authenticated:
                self.warnings.append("User not authenticated to TradeStation")
                print("⚠️ WARNING: User not authenticated - this may limit data access")
            else:
                print("✅ User is authenticated to TradeStation")

        # Test 2: Login URL Generation
        success, login_data = self.run_test(
            "TradeStation Login URL", "GET", "auth/tradestation/login", 200
        )

        if success:
            auth_url = login_data.get("auth_url", "")
            if auth_url:
                print("✅ OAuth login URL generated successfully")
                print(f"   URL length: {len(auth_url)} characters")
            else:
                self.critical_issues.append("OAuth login URL not generated")

        return success

    def test_tradestation_accounts_comprehensive(self):
        """Comprehensive TradeStation accounts testing"""
        print("\n🏛️ COMPREHENSIVE TRADESTATION ACCOUNTS TESTING")
        print("=" * 80)

        success, accounts_data = self.run_test(
            "TradeStation Accounts", "GET", "tradestation/accounts", 200
        )

        if not success:
            self.critical_issues.append("TradeStation accounts endpoint failed")
            return False, {}

        accounts = accounts_data.get("accounts", [])
        count = accounts_data.get("count", 0)

        print(f"📊 Accounts Found: {count}")

        if count == 0:
            self.critical_issues.append("No TradeStation accounts available")
            return False, {}

        # Analyze each account
        active_accounts = []
        for i, account in enumerate(accounts):
            account_id = account.get("AccountID", "N/A")
            account_type = account.get("AccountType", "N/A")
            status = account.get("Status", "N/A")
            currency = account.get("Currency", "N/A")

            print(f"   Account {i+1}: {account_id}")
            print(f"     - Type: {account_type}")
            print(f"     - Status: {status}")
            print(f"     - Currency: {currency}")

            if status == "Active":
                active_accounts.append(account_id)
                print("     ✅ Active account suitable for testing")

        if not active_accounts:
            self.critical_issues.append("No active TradeStation accounts found")
            return False, {}

        print(f"✅ Found {len(active_accounts)} active accounts")
        return True, {
            "active_accounts": active_accounts,
            "target_account": active_accounts[0],
        }

    def test_tradestation_positions_comprehensive(self, account_id):
        """Comprehensive TradeStation positions testing"""
        print(
            f"\n📊 COMPREHENSIVE TRADESTATION POSITIONS TESTING - Account {account_id}"
        )
        print("=" * 80)

        success, positions_data = self.run_test(
            "TradeStation Positions",
            "GET",
            f"tradestation/accounts/{account_id}/positions",
            200,
        )

        if not success:
            self.critical_issues.append(
                f"TradeStation positions endpoint failed for account {account_id}"
            )
            return False, {}

        # Analyze response structure
        print("📋 Response Structure Analysis:")
        print(f"   Response Type: {type(positions_data)}")
        print(f"   Response Keys: {list(positions_data.keys())}")

        positions = positions_data.get("positions", [])
        status = positions_data.get("status", "unknown")

        print(f"📊 Status: {status}")
        print(f"📊 Positions Count: {len(positions)}")

        if len(positions) == 0:
            self.warnings.append(f"No positions found in account {account_id}")
            return True, {"positions_count": 0, "total_value": 0}

        # Analyze position data quality
        total_value = 0
        stocks_count = 0
        options_count = 0

        print("\n📊 Position Analysis (showing first 5):")
        for i, position in enumerate(positions[:5]):
            symbol = position.get("symbol", "N/A")
            asset_type = position.get("asset_type", "N/A")
            quantity = position.get("quantity", 0)
            current_price = position.get("current_price", 0)
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)

            print(f"   Position {i+1}: {symbol}")
            print(f"     - Asset Type: {asset_type}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Current Price: ${current_price:.2f}")
            print(f"     - Market Value: ${market_value:,.2f}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:,.2f}")

            total_value += market_value

            if asset_type == "STOCK":
                stocks_count += 1
            elif asset_type == "OPTION":
                options_count += 1

        # Calculate total portfolio value
        total_portfolio_value = sum(pos.get("market_value", 0) for pos in positions)
        total_unrealized_pnl = sum(pos.get("unrealized_pnl", 0) for pos in positions)

        print("\n💰 Portfolio Summary:")
        print(f"   Total Positions: {len(positions)}")
        print(f"   Stocks: {stocks_count}")
        print(f"   Options: {options_count}")
        print(f"   Total Market Value: ${total_portfolio_value:,.2f}")
        print(f"   Total Unrealized P&L: ${total_unrealized_pnl:,.2f}")

        # Check data quality
        required_fields = [
            "symbol",
            "asset_type",
            "quantity",
            "current_price",
            "market_value",
        ]
        positions_with_all_fields = 0

        for position in positions:
            if all(
                field in position and position[field] is not None
                for field in required_fields
            ):
                positions_with_all_fields += 1

        data_quality = (positions_with_all_fields / len(positions)) * 100
        print(
            f"📊 Data Quality: {data_quality:.1f}% ({positions_with_all_fields}/{len(positions)} positions complete)"
        )

        if data_quality < 90:
            self.warnings.append(
                f"Some positions missing required fields ({data_quality:.1f}% complete)"
            )

        return True, {
            "positions_count": len(positions),
            "total_value": total_portfolio_value,
            "total_pnl": total_unrealized_pnl,
            "stocks_count": stocks_count,
            "options_count": options_count,
            "data_quality": data_quality,
        }

    def test_portfolio_management_integration(self):
        """Test Portfolio Management Service integration"""
        print("\n🔄 PORTFOLIO MANAGEMENT SERVICE INTEGRATION TESTING")
        print("=" * 80)

        success, portfolio_data = self.run_test(
            "Portfolio Management - TradeStation Main",
            "GET",
            "portfolio-management/portfolios/tradestation-main/positions",
            200,
        )

        if not success:
            self.critical_issues.append("Portfolio Management Service not accessible")
            return False, {}

        positions = portfolio_data.get("positions", [])
        portfolio_summary = portfolio_data.get("portfolio_summary", {})

        print(f"📊 Portfolio Management Positions: {len(positions)}")

        # Check data source
        using_mock_data = False
        real_tradestation_symbols = ["CRM", "TSLA", "AAPL", "NVO"]  # From direct API
        mock_symbols = ["AMZN", "QQQ", "GOOGL"]  # Typical mock data

        found_symbols = [pos.get("symbol", "") for pos in positions[:10]]
        print(f"📊 Found Symbols: {found_symbols}")

        # Check if using mock data
        mock_symbols_found = [sym for sym in found_symbols if sym in mock_symbols]
        real_symbols_found = [
            sym for sym in found_symbols if sym in real_tradestation_symbols
        ]

        print(f"📊 Mock Symbols Found: {mock_symbols_found}")
        print(f"📊 Real TradeStation Symbols Found: {real_symbols_found}")

        # Check metadata for source information
        if positions:
            first_position = positions[0]
            metadata = first_position.get("metadata", {})
            source = metadata.get("source", "unknown")

            print(f"📊 Data Source: {source}")

            if "mock" in source.lower() or "fallback" in source.lower():
                using_mock_data = True
                self.critical_issues.append(
                    "Portfolio Management using mock data instead of TradeStation"
                )
                print(
                    "🚨 CRITICAL: Portfolio Management Service using mock/fallback data"
                )
                print(
                    "   This explains why user sees fake positions instead of real TradeStation data"
                )
            else:
                print("✅ Portfolio Management Service using real data")

        return True, {
            "positions_count": len(positions),
            "using_mock_data": using_mock_data,
            "found_symbols": found_symbols,
        }

    def test_frontend_data_compatibility(self):
        """Test frontend data structure compatibility"""
        print("\n🔧 FRONTEND DATA STRUCTURE COMPATIBILITY TESTING")
        print("=" * 80)

        # Test the specific endpoint that IndividualPortfolio component uses
        success, response_data = self.run_test(
            "Frontend Portfolio Data",
            "GET",
            "portfolio-management/portfolios/tradestation-main/positions",
            200,
        )

        if not success:
            self.critical_issues.append("Frontend portfolio endpoint not accessible")
            return False

        # Check response structure for frontend compatibility
        print("📋 Frontend Data Structure Analysis:")
        print(f"   Response Keys: {list(response_data.keys())}")

        # Check if positions are at root level or nested
        if "positions" in response_data:
            positions = response_data["positions"]
            print(f"   ✅ Positions found in 'positions' field: {len(positions)} items")

            if positions:
                first_position = positions[0]
                print(f"   Position Fields: {list(first_position.keys())}")

                # Check for required frontend fields
                required_frontend_fields = [
                    "symbol",
                    "quantity",
                    "current_price",
                    "market_value",
                    "type",
                ]
                missing_fields = [
                    field
                    for field in required_frontend_fields
                    if field not in first_position
                ]

                if missing_fields:
                    self.warnings.append(
                        f"Some required frontend fields missing: {missing_fields}"
                    )
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                else:
                    print("   ✅ All required frontend fields present")
        else:
            self.critical_issues.append(
                "Positions data not found in expected structure"
            )
            print("   ❌ Positions data not found in expected structure")

        return True

    def run_comprehensive_diagnostic(self):
        """Run comprehensive diagnostic test"""
        print("🚀 COMPREHENSIVE TRADESTATION DIAGNOSTIC TEST")
        print("=" * 100)
        print(
            "🎯 OBJECTIVE: Complete diagnosis of TradeStation integration and IndividualPortfolio loading issues"
        )
        print("📋 TESTING SCOPE:")
        print("   1. TradeStation Authentication Status")
        print("   2. TradeStation Accounts Access")
        print("   3. TradeStation Positions Data Quality")
        print("   4. Portfolio Management Service Integration")
        print("   5. Frontend Data Structure Compatibility")

        # Phase 1: Authentication
        auth_success = self.test_tradestation_authentication_comprehensive()

        # Phase 2: Accounts
        accounts_success, accounts_data = (
            self.test_tradestation_accounts_comprehensive()
        )

        if not accounts_success:
            return self.generate_final_report("Accounts Access Failed")

        target_account = accounts_data["target_account"]

        # Phase 3: Positions
        positions_success, positions_data = (
            self.test_tradestation_positions_comprehensive(target_account)
        )

        # Phase 4: Portfolio Management Integration
        portfolio_mgmt_success, portfolio_data = (
            self.test_portfolio_management_integration()
        )

        # Phase 5: Frontend Compatibility
        frontend_success = self.test_frontend_data_compatibility()

        # Generate comprehensive report
        return self.generate_final_report(
            "Complete Diagnostic",
            {
                "auth_success": auth_success,
                "accounts_success": accounts_success,
                "positions_success": positions_success,
                "portfolio_mgmt_success": portfolio_mgmt_success,
                "frontend_success": frontend_success,
                "positions_data": positions_data,
                "portfolio_data": portfolio_data,
                "target_account": target_account,
            },
        )

    def generate_final_report(self, analysis_type, results=None):
        """Generate comprehensive diagnostic report"""
        print(f"\n📋 COMPREHENSIVE DIAGNOSTIC REPORT: {analysis_type}")
        print("=" * 100)

        print("\n📊 TEST EXECUTION SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")

        if self.critical_issues:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        if results:
            print("\n📈 DETAILED TEST RESULTS:")
            print(
                f"   Authentication: {'✅ Working' if results.get('auth_success') else '❌ Failed'}"
            )
            print(
                f"   Accounts Access: {'✅ Working' if results.get('accounts_success') else '❌ Failed'}"
            )
            print(
                f"   Positions Access: {'✅ Working' if results.get('positions_success') else '❌ Failed'}"
            )
            print(
                f"   Portfolio Management: {'✅ Working' if results.get('portfolio_mgmt_success') else '❌ Failed'}"
            )
            print(
                f"   Frontend Compatibility: {'✅ Working' if results.get('frontend_success') else '❌ Failed'}"
            )

            if results.get("positions_data"):
                pos_data = results["positions_data"]
                print(
                    f"   TradeStation Positions: {pos_data.get('positions_count', 0)}"
                )
                print(f"   Portfolio Value: ${pos_data.get('total_value', 0):,.2f}")
                print(f"   Data Quality: {pos_data.get('data_quality', 0):.1f}%")

            if results.get("portfolio_data"):
                port_data = results["portfolio_data"]
                print(
                    f"   Portfolio Mgmt Positions: {port_data.get('positions_count', 0)}"
                )
                print(
                    f"   Using Mock Data: {'❌ Yes' if port_data.get('using_mock_data') else '✅ No'}"
                )

        print("\n🎯 ROOT CAUSE ANALYSIS FOR INDIVIDUALPORTFOLIO LOADING ISSUE:")

        if not results:
            print(f"   ❌ {analysis_type} - Cannot complete full analysis")
        elif self.critical_issues:
            print("   🚨 CRITICAL ISSUES FOUND:")
            for issue in self.critical_issues:
                if "mock data" in issue.lower():
                    print(f"     🔧 DATA SOURCE ISSUE: {issue}")
                    print(
                        "        - User sees fake positions (AMZN, QQQ, GOOGL) instead of real ones"
                    )
                    print(
                        "        - Portfolio Management Service not properly integrated with TradeStation"
                    )
                elif "authentication" in issue.lower():
                    print(f"     🔐 AUTHENTICATION ISSUE: {issue}")
                    print(
                        "        - User needs to complete OAuth flow at /auth/tradestation/login"
                    )
                else:
                    print(f"     ❌ {issue}")
        else:
            print("   ✅ All TradeStation APIs are working correctly")
            print("   🤔 Loading issue may be frontend-specific:")
            print("     - Network connectivity issues")
            print("     - JavaScript errors in browser console")
            print("     - Frontend API URL configuration")
            print("     - Component state management issues")

        print("\n💡 SPECIFIC RECOMMENDATIONS FOR MAIN AGENT:")

        if any("mock data" in issue.lower() for issue in self.critical_issues):
            print("   🔧 IMMEDIATE ACTION REQUIRED:")
            print(
                "   1. Fix Portfolio Management Service to use real TradeStation data"
            )
            print("   2. Ensure TradeStation API integration is properly connected")
            print(
                "   3. Remove mock/fallback data usage when TradeStation is available"
            )
            print("   4. Verify data source field shows 'TradeStation API Integration'")
        elif any("authentication" in issue.lower() for issue in self.critical_issues):
            print("   🔐 AUTHENTICATION REQUIRED:")
            print("   1. User must complete TradeStation OAuth authentication")
            print("   2. Navigate to /auth/tradestation/login")
            print("   3. Accept required permissions (MarketData, ReadAccount, Trade)")
            print("   4. Verify authentication status shows authenticated: true")
        else:
            print("   🔍 FRONTEND INVESTIGATION NEEDED:")
            print("   1. Check browser console for JavaScript errors")
            print("   2. Verify network requests in browser DevTools")
            print("   3. Check if frontend is using correct API endpoints")
            print("   4. Verify component error handling and loading states")
            print("   5. Test with different browsers/devices")

        print("\n📊 TRADESTATION API STATUS SUMMARY:")
        if results and results.get("positions_data"):
            pos_data = results["positions_data"]
            print("   ✅ TradeStation Direct API: WORKING")
            print(f"   ✅ Account Access: {results.get('target_account', 'N/A')}")
            print(f"   ✅ Positions Available: {pos_data.get('positions_count', 0)}")
            print(f"   ✅ Portfolio Value: ${pos_data.get('total_value', 0):,.2f}")
            print("   ✅ Real-time Data: Available")
        else:
            print("   ❌ TradeStation API: Issues detected")

        if results and results.get("portfolio_data"):
            port_data = results["portfolio_data"]
            if port_data.get("using_mock_data"):
                print("   ❌ Portfolio Management: Using MOCK data")
                print(
                    "   🚨 USER IMPACT: Sees fake positions instead of real portfolio"
                )
            else:
                print("   ✅ Portfolio Management: Using real TradeStation data")

        success_rate = (
            (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        )
        has_critical_issues = len(self.critical_issues) > 0

        print("\n🎯 FINAL VERDICT:")
        if has_critical_issues:
            print("   🚨 CRITICAL ISSUES FOUND - Immediate attention required")
            print("   📝 IndividualPortfolio loading issue has identifiable root cause")
            print("   🔧 Solutions provided for resolution")
        elif success_rate >= 90:
            print("   ✅ EXCELLENT - All TradeStation APIs working correctly")
            print("   🤔 Loading issue likely frontend-specific")
        else:
            print("   ⚠️ MIXED RESULTS - Some issues detected")

        return success_rate >= 70 and not has_critical_issues


if __name__ == "__main__":
    print("🚀 Starting Comprehensive TradeStation Diagnostic")
    print("🎯 Focus: Complete analysis of IndividualPortfolio loading issues")

    tester = ComprehensiveTradeStationTester()
    success = tester.run_comprehensive_diagnostic()

    if success:
        print("\n🎉 DIAGNOSTIC COMPLETE: Comprehensive analysis finished")
    else:
        print(
            "\n🚨 DIAGNOSTIC COMPLETE: Critical issues identified requiring immediate action"
        )

    sys.exit(0 if success else 1)
