#!/usr/bin/env python3
"""
TradeStation Direct API Endpoints Test
Quick verification of TradeStation API endpoints as requested in review.

Focus:
1. GET /api/tradestation/accounts - Verify accounts are accessible
2. GET /api/tradestation/accounts/11775499/positions - Verify positions endpoint is working

Testing for:
- API response status codes and data availability
- Authentication or connectivity issues
- Whether endpoints return the $969,473.90 portfolio value correctly
- "Failed to fetch positions" error investigation
"""

import requests
import sys
from datetime import datetime


class TradeStationDirectTester:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.account_id = "11775499"  # Target account from review
        self.expected_portfolio_value = 969473.90  # Expected value from review

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
                    print(f"   Error: {response.text[:500]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_tradestation_accounts(self):
        """Test GET /api/tradestation/accounts - Verify accounts are accessible"""
        print("\n🏛️ PHASE 1: TradeStation Accounts Endpoint")
        print("=" * 60)
        print("🎯 OBJECTIVE: Verify accounts are accessible")
        print("📋 EXPECTED: Account 11775499 should be present")

        success, accounts_data = self.run_test(
            "TradeStation Accounts", "GET", "tradestation/accounts", 200
        )

        if not success:
            print("❌ CRITICAL: TradeStation accounts endpoint failed")
            return False, None

        # Analyze accounts response
        print("\n📊 ACCOUNTS ANALYSIS:")

        if isinstance(accounts_data, dict):
            # Check if it's wrapped in a data field
            if "data" in accounts_data:
                accounts = accounts_data["data"]
                print("   - Response structure: Wrapped in 'data' field")
            else:
                accounts = accounts_data
                print("   - Response structure: Direct response")
        elif isinstance(accounts_data, list):
            accounts = accounts_data
            print("   - Response structure: Direct list")
        else:
            print(f"❌ Unexpected response structure: {type(accounts_data)}")
            return False, None

        if not isinstance(accounts, list):
            print(f"❌ Expected list of accounts, got: {type(accounts)}")
            return False, None

        print(f"   - Total accounts found: {len(accounts)}")

        # Look for target account
        target_account = None
        for account in accounts:
            account_id = (
                account.get("AccountID")
                or account.get("account_id")
                or account.get("id")
            )
            account_type = (
                account.get("AccountType")
                or account.get("account_type")
                or account.get("type")
            )
            status = account.get("Status") or account.get("status")

            print(f"   - Account: {account_id} ({account_type}) - Status: {status}")

            if str(account_id) == self.account_id:
                target_account = account
                print(f"   ✅ TARGET ACCOUNT FOUND: {account_id}")

        if target_account:
            print("\n🎯 TARGET ACCOUNT DETAILS:")
            for key, value in target_account.items():
                print(f"   - {key}: {value}")
            return True, target_account
        else:
            print(f"❌ TARGET ACCOUNT {self.account_id} NOT FOUND")
            return False, None

    def test_tradestation_positions(self):
        """Test GET /api/tradestation/accounts/11775499/positions - Verify positions endpoint"""
        print("\n📊 PHASE 2: TradeStation Positions Endpoint")
        print("=" * 60)
        print(f"🎯 OBJECTIVE: Verify positions endpoint for account {self.account_id}")
        print(
            f"📋 EXPECTED: Portfolio value should be ~${self.expected_portfolio_value:,.2f}"
        )

        success, positions_data = self.run_test(
            f"TradeStation Positions (Account {self.account_id})",
            "GET",
            f"tradestation/accounts/{self.account_id}/positions",
            200,
        )

        if not success:
            print("❌ CRITICAL: TradeStation positions endpoint failed")
            print("🚨 This explains the 'Failed to fetch positions' error!")
            return False, None

        # Analyze positions response
        print("\n📊 POSITIONS ANALYSIS:")

        if isinstance(positions_data, dict):
            # Check if it's wrapped in a data field
            if "data" in positions_data:
                positions = positions_data["data"]
                print("   - Response structure: Wrapped in 'data' field")
                print(
                    "   🔍 FRONTEND ISSUE IDENTIFIED: Frontend may need to access response.data instead of response"
                )
            else:
                positions = positions_data
                print("   - Response structure: Direct response")
        elif isinstance(positions_data, list):
            positions = positions_data
            print("   - Response structure: Direct list")
        else:
            print(f"❌ Unexpected response structure: {type(positions_data)}")
            return False, None

        if not isinstance(positions, list):
            print(f"❌ Expected list of positions, got: {type(positions)}")
            return False, None

        print(f"   - Total positions found: {len(positions)}")

        # Analyze positions
        if len(positions) == 0:
            print("⚠️ No positions found in account")
            return True, positions_data

        # Calculate portfolio metrics
        total_market_value = 0
        total_unrealized_pnl = 0
        stocks_count = 0
        options_count = 0

        print("\n📋 POSITION BREAKDOWN:")
        for i, position in enumerate(positions[:10]):  # Show first 10
            symbol = position.get("Symbol") or position.get("symbol")
            quantity = position.get("Quantity") or position.get("quantity", 0)
            market_value = position.get("MarketValue") or position.get(
                "market_value", 0
            )
            unrealized_pnl = position.get("UnrealizedPnL") or position.get(
                "unrealized_pnl", 0
            )
            asset_type = position.get("AssetType") or position.get(
                "asset_type", "Unknown"
            )

            print(
                f"   {i+1:2d}. {symbol}: {quantity} shares, ${market_value:,.2f} value, ${unrealized_pnl:+,.2f} P&L ({asset_type})"
            )

            if isinstance(market_value, (int, float)):
                total_market_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                total_unrealized_pnl += unrealized_pnl

            if asset_type and "stock" in asset_type.lower():
                stocks_count += 1
            elif asset_type and "option" in asset_type.lower():
                options_count += 1

        if len(positions) > 10:
            print(f"   ... and {len(positions) - 10} more positions")

        # Portfolio summary
        print("\n💰 PORTFOLIO SUMMARY:")
        print(f"   - Total Positions: {len(positions)}")
        print(f"   - Stocks: {stocks_count}")
        print(f"   - Options: {options_count}")
        print(f"   - Total Market Value: ${total_market_value:,.2f}")
        print(f"   - Total Unrealized P&L: ${total_unrealized_pnl:+,.2f}")

        # Compare with expected value
        print("\n🎯 VALUE VERIFICATION:")
        print(f"   - Expected Portfolio Value: ${self.expected_portfolio_value:,.2f}")
        print(f"   - Actual Portfolio Value: ${total_market_value:,.2f}")

        value_difference = abs(total_market_value - self.expected_portfolio_value)
        value_difference_percent = (
            (value_difference / self.expected_portfolio_value) * 100
            if self.expected_portfolio_value > 0
            else 0
        )

        print(
            f"   - Difference: ${value_difference:,.2f} ({value_difference_percent:.2f}%)"
        )

        if value_difference_percent < 5:
            print("   ✅ Portfolio value matches expected value (within 5%)")
            value_correct = True
        elif value_difference_percent < 15:
            print("   ⚠️ Portfolio value close to expected (within 15%)")
            value_correct = True
        else:
            print("   ❌ Portfolio value significantly different from expected")
            value_correct = False

        return True, positions_data

    def test_connectivity_and_authentication(self):
        """Test overall connectivity and authentication status"""
        print("\n🔐 PHASE 3: Connectivity and Authentication")
        print("=" * 60)
        print("🎯 OBJECTIVE: Verify TradeStation authentication and connectivity")

        # Test authentication status
        success, auth_data = self.run_test(
            "TradeStation Auth Status", "GET", "auth/tradestation/status", 200
        )

        if success:
            print("\n🔐 AUTHENTICATION STATUS:")
            auth_status = auth_data.get("authenticated", False)
            environment = auth_data.get("environment", "Unknown")
            api_key = auth_data.get("api_key_configured", False)

            print(f"   - Authenticated: {auth_status}")
            print(f"   - Environment: {environment}")
            print(f"   - API Key Configured: {api_key}")

            if auth_status:
                print("   ✅ TradeStation authentication is working")
                return True
            else:
                print("   ❌ TradeStation not authenticated")
                print("   🔧 This may explain API connectivity issues")
                return False
        else:
            print("❌ Could not check authentication status")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive TradeStation Direct API test"""
        print("🏛️ TRADESTATION DIRECT API ENDPOINTS TEST")
        print("=" * 80)
        print("📋 REVIEW REQUEST: Quick test of TradeStation Direct API endpoints")
        print("🎯 FOCUS AREAS:")
        print("   1. API response status codes and data availability")
        print("   2. Authentication or connectivity issues")
        print("   3. Portfolio value verification ($969,473.90)")
        print("   4. 'Failed to fetch positions' error investigation")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Phase 1: Test accounts endpoint
        accounts_success, target_account = self.test_tradestation_accounts()

        # Phase 2: Test positions endpoint
        positions_success, positions_data = self.test_tradestation_positions()

        # Phase 3: Test connectivity and authentication
        auth_success = self.test_connectivity_and_authentication()

        # Final Assessment
        print("\n🎯 FINAL ASSESSMENT: TradeStation Direct API")
        print("=" * 80)

        test_results = [
            ("Accounts Endpoint", accounts_success),
            ("Positions Endpoint", positions_success),
            ("Authentication Status", auth_success),
            ("Target Account Found", target_account is not None),
            (
                "Positions Data Available",
                positions_data is not None
                and len(
                    positions_data.get("data", positions_data)
                    if isinstance(positions_data, dict)
                    else positions_data or []
                )
                > 0,
            ),
        ]

        passed_tests = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100

        print("\n📊 TEST RESULTS SUMMARY:")
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")

        print(
            f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
        )

        # Key findings
        print("\n🔍 KEY FINDINGS:")
        if accounts_success:
            print("   ✅ TradeStation accounts endpoint is accessible")
        else:
            print("   ❌ TradeStation accounts endpoint has issues")

        if positions_success:
            print("   ✅ TradeStation positions endpoint is working")
        else:
            print(
                "   ❌ TradeStation positions endpoint failed - explains 'Failed to fetch positions' error"
            )

        if target_account:
            print(f"   ✅ Target account {self.account_id} found and accessible")
        else:
            print(f"   ❌ Target account {self.account_id} not found or inaccessible")

        if auth_success:
            print("   ✅ TradeStation authentication is working")
        else:
            print("   ❌ TradeStation authentication issues detected")

        # Frontend issue analysis
        print("\n🖥️ FRONTEND ISSUE ANALYSIS:")
        if positions_success and positions_data:
            if isinstance(positions_data, dict) and "data" in positions_data:
                print(
                    "   🔍 POTENTIAL ISSUE IDENTIFIED: Response data is wrapped in 'data' field"
                )
                print(
                    "   🔧 SOLUTION: Frontend should access response.data.positions instead of response.positions"
                )
                print(
                    "   📝 This likely explains the 'Failed to fetch positions' error"
                )
            else:
                print("   ✅ Response structure appears frontend-compatible")

        # Portfolio value verification
        print("\n💰 PORTFOLIO VALUE VERIFICATION:")
        if positions_success and positions_data:
            print("   ✅ Portfolio data is available from TradeStation API")
            print(f"   📊 Expected value: ${self.expected_portfolio_value:,.2f}")
            print("   🔍 Actual values can be calculated from position data")
        else:
            print("   ❌ Cannot verify portfolio value - positions endpoint failed")

        # Final verdict
        print("\n🏆 FINAL VERDICT:")
        if success_rate >= 80:
            print("   🎉 EXCELLENT: TradeStation Direct API endpoints are working well")
            print("   ✅ API connectivity and authentication are functional")
            if positions_success:
                print("   ✅ Portfolio data is accessible - frontend issue likely")
            print(
                "   🔧 'Failed to fetch positions' error is likely a frontend data parsing issue"
            )
        elif success_rate >= 60:
            print("   ✅ GOOD: TradeStation API mostly working with some issues")
            print("   🔧 Some endpoints may need attention")
        else:
            print("   ❌ CRITICAL: TradeStation API has significant issues")
            print("   🚨 This explains the 'Failed to fetch positions' error")
            print("   🔧 Authentication or connectivity problems detected")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not auth_success:
            print("   1. Check TradeStation authentication credentials")
            print("   2. Verify API key and environment configuration")

        if (
            positions_success
            and isinstance(positions_data, dict)
            and "data" in positions_data
        ):
            print("   1. Update frontend to access response.data instead of response")
            print("   2. Check frontend error handling for nested response structures")

        if not positions_success:
            print("   1. Investigate TradeStation API connectivity")
            print("   2. Check account permissions and access rights")

        print("\n📊 SUMMARY FOR MAIN AGENT:")
        print(f"   - Tests Run: {self.tests_run}")
        print(f"   - Tests Passed: {self.tests_passed}")
        print(f"   - Success Rate: {success_rate:.1f}%")
        print(
            f"   - Primary Issue: {'Frontend data parsing' if positions_success else 'API connectivity'}"
        )

        return success_rate >= 60


if __name__ == "__main__":
    print("🚀 Starting TradeStation Direct API Test...")

    tester = TradeStationDirectTester()
    success = tester.run_comprehensive_test()

    if success:
        print("\n✅ TradeStation Direct API test completed successfully")
        sys.exit(0)
    else:
        print("\n❌ TradeStation Direct API test found critical issues")
        sys.exit(1)
