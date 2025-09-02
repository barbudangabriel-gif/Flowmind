#!/usr/bin/env python3
"""
TradeStation Positions Route Stability Test
Re-testing after session handling fix as requested in review.

Test Requirements:
1. GET /api/tradestation/accounts -> pick first margin account ID
2. GET /api/tradestation/accounts/{id}/positions -> expect 200 and JSON with positions[] (not 500)
3. GET /api/tradestation/accounts/{id}/balances -> expect 200
4. Report any errors, especially if 500 persists
5. Include sample of returned positions payload shape for UI mapping
"""

import requests
import json
import sys
from datetime import datetime


class TradeStationPositionsTest:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_results = []
        self.margin_account_id = None

    def log_result(
        self, test_name, success, status_code, response_data=None, error_msg=None
    ):
        """Log test result for final summary"""
        result = {
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error_msg": error_msg,
        }
        self.test_results.append(result)
        return result

    def make_request(self, method, endpoint, timeout=30):
        """Make HTTP request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            print(f"🔍 {method} {url}")

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code}")

            # Try to parse JSON response
            try:
                response_data = response.json()
                return response.status_code, response_data, None
            except json.JSONDecodeError as e:
                return (
                    response.status_code,
                    response.text,
                    f"JSON decode error: {str(e)}",
                )

        except requests.exceptions.Timeout:
            return None, None, f"Request timeout ({timeout}s)"
        except requests.exceptions.RequestException as e:
            return None, None, f"Request error: {str(e)}"
        except Exception as e:
            return None, None, f"Unexpected error: {str(e)}"

    def test_accounts_endpoint(self):
        """Test 1: GET /api/tradestation/accounts -> pick first margin account ID"""
        print("\n" + "=" * 80)
        print("TEST 1: TradeStation Accounts Endpoint")
        print("=" * 80)
        print("🎯 OBJECTIVE: Get accounts and identify first margin account ID")

        status_code, response_data, error_msg = self.make_request(
            "GET", "tradestation/accounts"
        )

        if error_msg:
            print(f"❌ FAILED: {error_msg}")
            self.log_result("TradeStation Accounts", False, None, None, error_msg)
            return False

        if status_code != 200:
            print(f"❌ FAILED: Expected 200, got {status_code}")
            print(f"   Response: {response_data}")
            self.log_result(
                "TradeStation Accounts",
                False,
                status_code,
                response_data,
                "Non-200 status code",
            )
            return False

        print("✅ SUCCESS: Status 200")

        # Analyze response structure
        if isinstance(response_data, dict):
            print(f"📊 Response structure: {list(response_data.keys())}")

            # Look for accounts in different possible structures
            accounts = None
            if "accounts" in response_data:
                accounts = response_data["accounts"]
            elif isinstance(response_data, list):
                accounts = response_data
            elif "data" in response_data and isinstance(response_data["data"], list):
                accounts = response_data["data"]

            if accounts and isinstance(accounts, list):
                print(f"📊 Found {len(accounts)} accounts")

                # Look for margin account
                margin_accounts = []
                for account in accounts:
                    account_type = account.get("AccountType", "").upper()
                    account_id = account.get("AccountID", account.get("account_id", ""))

                    print(f"   Account: {account_id} - Type: {account_type}")

                    if "MARGIN" in account_type:
                        margin_accounts.append(account_id)

                if margin_accounts:
                    self.margin_account_id = margin_accounts[0]
                    print(f"✅ MARGIN ACCOUNT FOUND: {self.margin_account_id}")
                    self.log_result(
                        "TradeStation Accounts",
                        True,
                        status_code,
                        {
                            "accounts_count": len(accounts),
                            "margin_account_id": self.margin_account_id,
                        },
                    )
                    return True
                else:
                    print("❌ NO MARGIN ACCOUNT FOUND")
                    print(
                        f"   Available account types: {[acc.get('AccountType', 'Unknown') for acc in accounts]}"
                    )
                    self.log_result(
                        "TradeStation Accounts",
                        False,
                        status_code,
                        response_data,
                        "No margin account found",
                    )
                    return False
            else:
                print("❌ INVALID RESPONSE: No accounts array found")
                print(
                    f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}"
                )
                self.log_result(
                    "TradeStation Accounts",
                    False,
                    status_code,
                    response_data,
                    "No accounts array in response",
                )
                return False
        else:
            print(f"❌ INVALID RESPONSE: Expected dict, got {type(response_data)}")
            self.log_result(
                "TradeStation Accounts",
                False,
                status_code,
                response_data,
                "Invalid response format",
            )
            return False

    def test_positions_endpoint(self):
        """Test 2: GET /api/tradestation/accounts/{id}/positions -> expect 200 and JSON with positions[]"""
        print("\n" + "=" * 80)
        print("TEST 2: TradeStation Positions Endpoint")
        print("=" * 80)
        print("🎯 OBJECTIVE: Get positions for margin account, expect 200 (not 500)")

        if not self.margin_account_id:
            print("❌ SKIPPED: No margin account ID available from previous test")
            self.log_result(
                "TradeStation Positions", False, None, None, "No margin account ID"
            )
            return False

        print(f"📊 Testing with account ID: {self.margin_account_id}")

        status_code, response_data, error_msg = self.make_request(
            "GET", f"tradestation/accounts/{self.margin_account_id}/positions"
        )

        if error_msg:
            print(f"❌ FAILED: {error_msg}")
            self.log_result("TradeStation Positions", False, None, None, error_msg)
            return False

        # Check for 500 error specifically (main concern from review)
        if status_code == 500:
            print("🚨 CRITICAL: 500 Internal Server Error persists!")
            print("   This indicates the session handling fix may not be working")
            print(f"   Response: {response_data}")
            self.log_result(
                "TradeStation Positions",
                False,
                status_code,
                response_data,
                "500 Internal Server Error - session handling issue",
            )
            return False

        if status_code != 200:
            print(f"❌ FAILED: Expected 200, got {status_code}")
            print(f"   Response: {response_data}")
            self.log_result(
                "TradeStation Positions",
                False,
                status_code,
                response_data,
                f"Non-200 status code: {status_code}",
            )
            return False

        print("✅ SUCCESS: Status 200 (no 500 error)")

        # Analyze response structure for UI mapping
        if isinstance(response_data, dict):
            print(f"📊 Response structure: {list(response_data.keys())}")

            # Look for positions in different possible structures
            positions = None
            if "positions" in response_data:
                positions = response_data["positions"]
            elif "data" in response_data:
                positions = response_data["data"]
            elif isinstance(response_data, list):
                positions = response_data

            if positions and isinstance(positions, list):
                print(f"📊 Found {len(positions)} positions")

                if len(positions) > 0:
                    print("✅ At least one position found")

                    # Analyze first position for UI mapping
                    first_position = positions[0]
                    print("\n📋 SAMPLE POSITION PAYLOAD SHAPE (for UI mapping):")
                    print(f"   Position fields: {list(first_position.keys())}")

                    # Show key fields that UI would need
                    key_fields = [
                        "symbol",
                        "Symbol",
                        "quantity",
                        "Quantity",
                        "market_value",
                        "MarketValue",
                        "unrealized_pnl",
                        "UnrealizedPnL",
                        "position_type",
                        "PositionType",
                        "asset_type",
                        "AssetType",
                    ]

                    print("\n📊 KEY FIELDS FOR UI MAPPING:")
                    for field in key_fields:
                        if field in first_position:
                            value = first_position[field]
                            print(f"   ✅ {field}: {value} ({type(value).__name__})")

                    # Show sample of actual data structure
                    print("\n📄 SAMPLE POSITION DATA:")
                    sample_data = {}
                    for key, value in first_position.items():
                        if isinstance(value, (str, int, float, bool)):
                            sample_data[key] = value
                        else:
                            sample_data[key] = f"<{type(value).__name__}>"

                    print(json.dumps(sample_data, indent=2))

                    # Check for different asset types
                    asset_types = set()
                    symbols = set()
                    for pos in positions[:10]:  # Check first 10
                        if "asset_type" in pos:
                            asset_types.add(pos["asset_type"])
                        elif "AssetType" in pos:
                            asset_types.add(pos["AssetType"])

                        if "symbol" in pos:
                            symbols.add(pos["symbol"])
                        elif "Symbol" in pos:
                            symbols.add(pos["Symbol"])

                    print("\n📊 PORTFOLIO COMPOSITION:")
                    print(f"   Asset types: {list(asset_types)}")
                    print(f"   Sample symbols: {list(symbols)[:10]}")

                    self.log_result(
                        "TradeStation Positions",
                        True,
                        status_code,
                        {
                            "positions_count": len(positions),
                            "sample_fields": list(first_position.keys()),
                            "asset_types": list(asset_types),
                            "sample_symbols": list(symbols)[:5],
                        },
                    )
                    return True
                else:
                    print("⚠️  WARNING: No positions found in account")
                    self.log_result(
                        "TradeStation Positions",
                        True,
                        status_code,
                        {"positions_count": 0},
                        "No positions in account",
                    )
                    return True
            else:
                print("❌ INVALID RESPONSE: No positions array found")
                print(f"   Response structure: {response_data}")
                self.log_result(
                    "TradeStation Positions",
                    False,
                    status_code,
                    response_data,
                    "No positions array in response",
                )
                return False
        else:
            print(f"❌ INVALID RESPONSE: Expected dict, got {type(response_data)}")
            self.log_result(
                "TradeStation Positions",
                False,
                status_code,
                response_data,
                "Invalid response format",
            )
            return False

    def test_balances_endpoint(self):
        """Test 3: GET /api/tradestation/accounts/{id}/balances -> expect 200"""
        print("\n" + "=" * 80)
        print("TEST 3: TradeStation Balances Endpoint")
        print("=" * 80)
        print("🎯 OBJECTIVE: Get balances for margin account, expect 200")

        if not self.margin_account_id:
            print("❌ SKIPPED: No margin account ID available from previous test")
            self.log_result(
                "TradeStation Balances", False, None, None, "No margin account ID"
            )
            return False

        print(f"📊 Testing with account ID: {self.margin_account_id}")

        status_code, response_data, error_msg = self.make_request(
            "GET", f"tradestation/accounts/{self.margin_account_id}/balances"
        )

        if error_msg:
            print(f"❌ FAILED: {error_msg}")
            self.log_result("TradeStation Balances", False, None, None, error_msg)
            return False

        if status_code != 200:
            print(f"❌ FAILED: Expected 200, got {status_code}")
            print(f"   Response: {response_data}")
            self.log_result(
                "TradeStation Balances",
                False,
                status_code,
                response_data,
                f"Non-200 status code: {status_code}",
            )
            return False

        print("✅ SUCCESS: Status 200")

        # Analyze balance data
        if isinstance(response_data, dict):
            print(f"📊 Response structure: {list(response_data.keys())}")

            # Look for balance information
            balance_fields = [
                "CashBalance",
                "BuyingPower",
                "Equity",
                "MarketValue",
                "balances",
                "Balances",
            ]
            found_fields = []

            for field in balance_fields:
                if field in response_data:
                    found_fields.append(field)
                    value = response_data[field]
                    if isinstance(value, (int, float)):
                        print(f"   ✅ {field}: ${value:,.2f}")
                    else:
                        print(f"   ✅ {field}: {type(value).__name__}")

            if found_fields:
                print(f"✅ Balance data available: {found_fields}")
                self.log_result(
                    "TradeStation Balances",
                    True,
                    status_code,
                    {"balance_fields": found_fields},
                )
                return True
            else:
                print("⚠️  WARNING: No recognized balance fields found")
                print(f"   Available fields: {list(response_data.keys())}")
                self.log_result(
                    "TradeStation Balances",
                    True,
                    status_code,
                    response_data,
                    "No recognized balance fields",
                )
                return True
        else:
            print(f"❌ INVALID RESPONSE: Expected dict, got {type(response_data)}")
            self.log_result(
                "TradeStation Balances",
                False,
                status_code,
                response_data,
                "Invalid response format",
            )
            return False

    def run_all_tests(self):
        """Run all TradeStation position stability tests"""
        print("🚀 TRADESTATION POSITIONS ROUTE STABILITY TEST")
        print("=" * 80)
        print(
            "📋 REVIEW REQUEST: Re-test backend TradeStation positions route stability after session handling fix"
        )
        print(
            "🎯 FOCUS: Verify no 500 errors, proper JSON responses, positions data structure"
        )
        print(f"⏰ Test started: {datetime.now().isoformat()}")

        # Run tests in sequence
        test1_success = self.test_accounts_endpoint()
        test2_success = self.test_positions_endpoint()
        test3_success = self.test_balances_endpoint()

        # Generate final report
        self.generate_final_report()

        return test1_success and test2_success and test3_success

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 FINAL REPORT: TradeStation Positions Route Stability")
        print("=" * 80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(
            f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)"
        )

        # Test by test breakdown
        print("\n📋 TEST BREAKDOWN:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} Test {i}: {result['test_name']}")
            if result["status_code"]:
                print(f"      Status Code: {result['status_code']}")
            if result["error_msg"]:
                print(f"      Error: {result['error_msg']}")

        # Critical findings
        print("\n🔍 CRITICAL FINDINGS:")

        # Check for 500 errors specifically
        has_500_error = any(
            result.get("status_code") == 500 for result in self.test_results
        )
        if has_500_error:
            print(
                "   🚨 500 INTERNAL SERVER ERROR DETECTED - Session handling fix may not be working"
            )
        else:
            print("   ✅ No 500 errors detected - Session handling appears stable")

        # Check positions endpoint specifically
        positions_test = next(
            (r for r in self.test_results if "Positions" in r["test_name"]), None
        )
        if positions_test:
            if positions_test["success"]:
                print(
                    "   ✅ Positions endpoint working - Returns JSON with positions[]"
                )
                if (
                    positions_test["response_data"]
                    and "positions_count" in positions_test["response_data"]
                ):
                    count = positions_test["response_data"]["positions_count"]
                    print(f"   📊 Found {count} positions in account")
            else:
                print(
                    f"   ❌ Positions endpoint failed - {positions_test.get('error_msg', 'Unknown error')}"
                )

        # Account identification
        if self.margin_account_id:
            print(f"   ✅ Margin account identified: {self.margin_account_id}")
        else:
            print("   ❌ No margin account identified")

        # Sample payload information
        positions_test = next(
            (
                r
                for r in self.test_results
                if "Positions" in r["test_name"] and r["success"]
            ),
            None,
        )
        if positions_test and positions_test.get("response_data"):
            data = positions_test["response_data"]
            if "sample_fields" in data:
                print("\n📄 POSITIONS PAYLOAD SHAPE FOR UI MAPPING:")
                print(f"   Available fields: {data['sample_fields']}")
            if "asset_types" in data:
                print(f"   Asset types found: {data['asset_types']}")
            if "sample_symbols" in data:
                print(f"   Sample symbols: {data['sample_symbols']}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if success_rate >= 100:
            print(
                "   🎉 EXCELLENT: All TradeStation endpoints working perfectly after session handling fix"
            )
            print("   ✅ No further action needed - positions route is stable")
        elif success_rate >= 66:
            print("   ✅ GOOD: Most endpoints working, minor issues detected")
            print("   🔧 Review failed tests and address specific issues")
        else:
            print("   ❌ CRITICAL: Multiple endpoint failures detected")
            print("   🚨 Session handling fix may not be complete")
            print("   🔧 Immediate investigation required")

        # Session handling assessment
        if has_500_error:
            print(
                "   🚨 SESSION HANDLING: 500 errors indicate session management issues persist"
            )
            print("   🔧 Review authentication token refresh logic")
            print("   🔧 Check TradeStation API session timeout handling")
        else:
            print(
                "   ✅ SESSION HANDLING: No 500 errors suggest session handling fix is working"
            )

        print(f"\n⏰ Test completed: {datetime.now().isoformat()}")
        print("=" * 80)


def main():
    """Main test execution"""
    tester = TradeStationPositionsTest()
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
