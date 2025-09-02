#!/usr/bin/env python3
"""
Backend API Testing for Review Request
Focus: IndividualPortfolio and Portfolio Management Service endpoints
"""

import requests
from datetime import datetime


class ReviewBackendTester:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, details):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1

        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

    def make_request(
        self, method, endpoint, expected_status=200, params=None, data=None
    ):
        """Make HTTP request and return response"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response

        except requests.exceptions.Timeout:
            return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def test_tradestation_accounts(self):
        """Test 1: GET /api/tradestation/accounts"""
        print("\n🔍 Test 1: TradeStation Accounts Endpoint")
        print("-" * 50)

        response = self.make_request("GET", "tradestation/accounts")

        if not response:
            self.log_result(
                "TradeStation Accounts - Request", False, "Request failed or timed out"
            )
            return None

        if response.status_code != 200:
            self.log_result(
                "TradeStation Accounts - Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return None

        try:
            data = response.json()
        except:
            self.log_result(
                "TradeStation Accounts - JSON", False, "Response is not valid JSON"
            )
            return None

        # Check response structure
        if "status" in data and data["status"] == "success":
            self.log_result(
                "TradeStation Accounts - Status Field",
                True,
                f"Status: {data['status']}",
            )
        else:
            self.log_result(
                "TradeStation Accounts - Status Field",
                False,
                "Missing or invalid status field",
            )

        if "accounts" in data and isinstance(data["accounts"], list):
            accounts = data["accounts"]
            self.log_result(
                "TradeStation Accounts - Accounts Array",
                True,
                f"Found {len(accounts)} accounts",
            )

            # Find first margin account
            margin_account = None
            for account in accounts:
                if account.get("type", "").lower() == "margin":
                    margin_account = account
                    break

            if margin_account:
                account_id = margin_account.get("account_id") or margin_account.get(
                    "id"
                )
                self.log_result(
                    "TradeStation Accounts - Margin Account",
                    True,
                    f"Found margin account: {account_id}",
                )
                return account_id
            else:
                self.log_result(
                    "TradeStation Accounts - Margin Account",
                    False,
                    "No margin account found",
                )
                # Return first account if available
                if accounts:
                    account_id = accounts[0].get("account_id") or accounts[0].get("id")
                    return account_id
                return None
        else:
            self.log_result(
                "TradeStation Accounts - Accounts Array",
                False,
                "Missing or invalid accounts array",
            )
            return None

    def test_tradestation_positions(self, account_id):
        """Test 2: GET /api/tradestation/accounts/{account_id}/positions"""
        print(f"\n🔍 Test 2: TradeStation Positions for Account {account_id}")
        print("-" * 50)

        if not account_id:
            self.log_result(
                "TradeStation Positions - Account ID", False, "No account ID provided"
            )
            return

        response = self.make_request(
            "GET", f"tradestation/accounts/{account_id}/positions"
        )

        if not response:
            self.log_result(
                "TradeStation Positions - Request", False, "Request failed or timed out"
            )
            return

        if response.status_code != 200:
            self.log_result(
                "TradeStation Positions - Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return

        try:
            data = response.json()
        except:
            self.log_result(
                "TradeStation Positions - JSON", False, "Response is not valid JSON"
            )
            return

        # Check for positions data
        if "positions" in data:
            positions = data["positions"]
            self.log_result(
                "TradeStation Positions - Data Structure",
                True,
                f"Found {len(positions)} positions",
            )

            # Sample a few positions to check structure
            if positions:
                sample_position = positions[0]
                required_fields = ["symbol", "quantity", "market_value"]
                missing_fields = [
                    field for field in required_fields if field not in sample_position
                ]

                if not missing_fields:
                    self.log_result(
                        "TradeStation Positions - Position Structure",
                        True,
                        "Position fields complete",
                    )
                else:
                    self.log_result(
                        "TradeStation Positions - Position Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                    )

                # Count symbols for dropdown verification
                symbols = list(set([pos.get("symbol", "") for pos in positions]))
                self.log_result(
                    "TradeStation Positions - Symbol Count",
                    True,
                    f"Found {len(symbols)} unique symbols",
                )

        elif "data" in data and "positions" in data["data"]:
            # Handle nested data structure
            positions = data["data"]["positions"]
            self.log_result(
                "TradeStation Positions - Nested Data Structure",
                True,
                f"Found {len(positions)} positions in data.positions",
            )
        else:
            self.log_result(
                "TradeStation Positions - Data Structure",
                False,
                "No positions array found in response",
            )

    def test_tradestation_balances(self, account_id):
        """Test 3: GET /api/tradestation/accounts/{account_id}/balances"""
        print(f"\n🔍 Test 3: TradeStation Balances for Account {account_id}")
        print("-" * 50)

        if not account_id:
            self.log_result(
                "TradeStation Balances - Account ID", False, "No account ID provided"
            )
            return

        response = self.make_request(
            "GET", f"tradestation/accounts/{account_id}/balances"
        )

        if not response:
            self.log_result(
                "TradeStation Balances - Request", False, "Request failed or timed out"
            )
            return

        if response.status_code != 200:
            self.log_result(
                "TradeStation Balances - Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return

        try:
            data = response.json()
        except:
            self.log_result(
                "TradeStation Balances - JSON", False, "Response is not valid JSON"
            )
            return

        # Check for balance data
        if "balances" in data or "data" in data:
            self.log_result(
                "TradeStation Balances - Data Structure",
                True,
                "Balance data structure found",
            )

            # Look for common balance fields
            balance_data = data.get("balances") or data.get("data", {})
            balance_fields = ["cash_balance", "buying_power", "total_value", "equity"]
            found_fields = [
                field for field in balance_fields if field in str(balance_data).lower()
            ]

            if found_fields:
                self.log_result(
                    "TradeStation Balances - Balance Fields",
                    True,
                    f"Found balance fields: {found_fields}",
                )
            else:
                self.log_result(
                    "TradeStation Balances - Balance Fields",
                    False,
                    "No standard balance fields found",
                )
        else:
            self.log_result(
                "TradeStation Balances - Data Structure",
                False,
                "No balance data found in response",
            )

    def test_portfolio_management_portfolios(self):
        """Test 4: GET /api/portfolio-management/portfolios"""
        print("\n🔍 Test 4: Portfolio Management Portfolios")
        print("-" * 50)

        response = self.make_request("GET", "portfolio-management/portfolios")

        if not response:
            self.log_result(
                "Portfolio Management Portfolios - Request",
                False,
                "Request failed or timed out",
            )
            return False

        if response.status_code != 200:
            self.log_result(
                "Portfolio Management Portfolios - Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return False

        try:
            data = response.json()
        except:
            self.log_result(
                "Portfolio Management Portfolios - JSON",
                False,
                "Response is not valid JSON",
            )
            return False

        # Check response structure
        if "status" in data and data["status"] == "success":
            self.log_result(
                "Portfolio Management Portfolios - Status Field",
                True,
                f"Status: {data['status']}",
            )
        else:
            self.log_result(
                "Portfolio Management Portfolios - Status Field",
                False,
                "Missing or invalid status field",
            )

        if "portfolios" in data and isinstance(data["portfolios"], list):
            portfolios = data["portfolios"]
            self.log_result(
                "Portfolio Management Portfolios - Portfolios Array",
                True,
                f"Found {len(portfolios)} portfolios",
            )

            # Check for tradestation-main portfolio
            tradestation_main_found = False
            for portfolio in portfolios:
                portfolio_id = portfolio.get("id", "").lower()
                if "tradestation" in portfolio_id and "main" in portfolio_id:
                    tradestation_main_found = True
                    break

            if tradestation_main_found:
                self.log_result(
                    "Portfolio Management Portfolios - TradeStation Main",
                    True,
                    "tradestation-main portfolio found",
                )
                return True
            else:
                self.log_result(
                    "Portfolio Management Portfolios - TradeStation Main",
                    False,
                    "tradestation-main portfolio not found",
                )
                return False
        else:
            self.log_result(
                "Portfolio Management Portfolios - Portfolios Array",
                False,
                "Missing or invalid portfolios array",
            )
            return False

    def test_portfolio_management_positions(self):
        """Test 5: GET /api/portfolio-management/portfolios/tradestation-main/positions"""
        print("\n🔍 Test 5: Portfolio Management TradeStation Main Positions")
        print("-" * 50)

        response = self.make_request(
            "GET", "portfolio-management/portfolios/tradestation-main/positions"
        )

        if not response:
            self.log_result(
                "Portfolio Management Positions - Request",
                False,
                "Request failed or timed out",
            )
            return

        if response.status_code != 200:
            self.log_result(
                "Portfolio Management Positions - Status",
                False,
                f"Expected 200, got {response.status_code}",
            )
            return

        try:
            data = response.json()
        except:
            self.log_result(
                "Portfolio Management Positions - JSON",
                False,
                "Response is not valid JSON",
            )
            return

        # Check response structure
        if "status" in data and data["status"] == "success":
            self.log_result(
                "Portfolio Management Positions - Status Field",
                True,
                f"Status: {data['status']}",
            )
        else:
            self.log_result(
                "Portfolio Management Positions - Status Field",
                False,
                "Missing or invalid status field",
            )

        if "positions" in data and isinstance(data["positions"], list):
            positions = data["positions"]
            self.log_result(
                "Portfolio Management Positions - Positions Array",
                True,
                f"Found {len(positions)} positions",
            )

            # Check position structure
            if positions:
                sample_position = positions[0]
                required_fields = ["symbol", "position_type"]
                found_fields = []

                for field in required_fields:
                    if field in sample_position:
                        found_fields.append(field)
                    elif field == "position_type" and "type" in sample_position:
                        found_fields.append("type (equivalent)")

                if len(found_fields) >= 1:  # At least symbol should be present
                    self.log_result(
                        "Portfolio Management Positions - Position Structure",
                        True,
                        f"Found fields: {found_fields}",
                    )
                else:
                    self.log_result(
                        "Portfolio Management Positions - Position Structure",
                        False,
                        f"Missing required fields: {required_fields}",
                    )
        else:
            self.log_result(
                "Portfolio Management Positions - Positions Array",
                False,
                "Missing or invalid positions array",
            )

    def test_api_accessibility(self):
        """Test 6: Verify all routes are accessible via base URL with /api prefix"""
        print("\n🔍 Test 6: API Route Accessibility")
        print("-" * 50)

        # Test base API endpoint
        response = self.make_request("GET", "")

        if response and response.status_code == 200:
            self.log_result(
                "API Base Route - Accessibility",
                True,
                f"Base API route accessible at {self.api_url}",
            )

            try:
                data = response.json()
                if "tradestation_endpoints" in data:
                    self.log_result(
                        "API Base Route - TradeStation Endpoints",
                        True,
                        "TradeStation endpoints documented",
                    )
                else:
                    self.log_result(
                        "API Base Route - TradeStation Endpoints",
                        False,
                        "TradeStation endpoints not documented",
                    )

                if "version" in data:
                    version = data["version"]
                    self.log_result(
                        "API Base Route - Version", True, f"API version: {version}"
                    )
                else:
                    self.log_result(
                        "API Base Route - Version", False, "API version not found"
                    )

            except:
                self.log_result(
                    "API Base Route - JSON Response",
                    False,
                    "Base route response is not valid JSON",
                )
        else:
            self.log_result(
                "API Base Route - Accessibility", False, "Base API route not accessible"
            )

        # Verify no hardcoded localhost dependencies
        test_endpoints = ["tradestation/accounts", "portfolio-management/portfolios"]

        localhost_issues = 0
        for endpoint in test_endpoints:
            response = self.make_request("GET", endpoint)
            if response:
                try:
                    response_text = response.text
                    if "localhost" in response_text.lower():
                        localhost_issues += 1
                except:
                    pass

        if localhost_issues == 0:
            self.log_result(
                "API Routes - No Localhost Dependencies",
                True,
                "No hardcoded localhost found in responses",
            )
        else:
            self.log_result(
                "API Routes - No Localhost Dependencies",
                False,
                f"Found {localhost_issues} endpoints with localhost references",
            )

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Backend API Testing for Review Request")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print()

        # Test 1: TradeStation Accounts
        account_id = self.test_tradestation_accounts()

        # Test 2 & 3: TradeStation Positions and Balances (if we have an account)
        if account_id:
            self.test_tradestation_positions(account_id)
            self.test_tradestation_balances(account_id)
        else:
            print(
                "\n⚠️  Skipping positions and balances tests - no account ID available"
            )

        # Test 4: Portfolio Management Portfolios
        portfolio_found = self.test_portfolio_management_portfolios()

        # Test 5: Portfolio Management Positions
        self.test_portfolio_management_positions()

        # Test 6: API Accessibility
        self.test_api_accessibility()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary and findings"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        success_rate = (
            (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        )

        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")

        print("\n📋 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")

        print("\n🔍 SCHEMA NOTES AND MISMATCHES:")

        # Analyze results for schema issues
        schema_notes = []

        # Check for data nesting issues
        tradestation_tests = [r for r in self.results if "TradeStation" in r["test"]]
        portfolio_tests = [
            r for r in self.results if "Portfolio Management" in r["test"]
        ]

        if any(
            "Nested Data Structure" in r["details"]
            for r in tradestation_tests
            if r["details"]
        ):
            schema_notes.append(
                "⚠️  TradeStation API returns data nested under 'data' field - frontend may need to access response.data.* instead of response.*"
            )

        if any(
            "Missing" in r["details"]
            for r in self.results
            if r["details"] and not r["success"]
        ):
            schema_notes.append(
                "⚠️  Some expected fields may be missing or named differently than expected"
            )

        if any(
            "position_type" in r["details"] for r in portfolio_tests if r["details"]
        ):
            schema_notes.append(
                "ℹ️  Portfolio positions may use 'type' field instead of 'position_type'"
            )

        if schema_notes:
            for note in schema_notes:
                print(note)
        else:
            print("✅ No major schema mismatches detected")

        print("\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 80:
            print(
                "🎉 EXCELLENT - Backend APIs are working well for IndividualPortfolio and Portfolio Management"
            )
        elif success_rate >= 60:
            print("✅ GOOD - Most backend APIs are working with minor issues")
        elif success_rate >= 40:
            print("⚠️  MODERATE - Some backend APIs have issues that need attention")
        else:
            print("❌ POOR - Significant backend API issues detected")

        print(f"\nTimestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    tester = ReviewBackendTester()
    tester.run_all_tests()
