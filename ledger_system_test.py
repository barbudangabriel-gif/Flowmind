#!/usr/bin/env python3
"""
FlowMind Portfolios Ledger System Backend Testing
=================================================

Test the new Ledger System endpoints for FlowMind Portfolios backend:

New Transaction Endpoints:
1. GET /portfolios/{pid}/transactions - List transactions for portfolio
2. POST /portfolios/{pid}/transactions - Create new transaction
3. GET /portfolios/{pid}/positions - Get FIFO-calculated positions
4. GET /portfolios/{pid}/realized-pnl - Get realized P&L by symbol
5. POST /portfolios/{pid}/import-csv - Import transactions from CSV
6. GET /portfolios/{pid}/stats - Enhanced stats with real P&L data

Test Scenarios:
1. Create portfolio and add sample transactions (BUY/SELL)
2. Test FIFO position calculation with multiple buys/sells
3. Test realized P&L calculation when selling positions
4. Test CSV import with sample transaction data
5. Verify enhanced stats endpoint with real data
"""

import requests
import sys
from datetime import datetime
from typing import Dict, List


class LedgerSystemTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.portfolio_id = None
        self.transaction_ids = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(
        self,
        name: str,
        method: str,
        endpoint: str,
        expected_status: int,
        data: Dict = None,
        params: Dict = None,
    ) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        self.tests_run += 1
        self.log(f"Testing {name}...")
        self.log(f"URL: {url}")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
                    if (
                        isinstance(response_data, dict)
                        and len(str(response_data)) < 1000
                    ):
                        self.log(f"Response: {response_data}")
                    elif isinstance(response_data, list):
                        self.log(f"Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                self.log(
                    f"❌ FAILED - Expected {expected_status}, got {response.status_code}",
                    "ERROR",
                )
                try:
                    error_data = response.json()
                    self.log(f"Error: {error_data}", "ERROR")
                except:
                    self.log(f"Error: {response.text}", "ERROR")
                return False, {}

        except requests.exceptions.Timeout:
            self.log("❌ FAILED - Request timeout (30s)", "ERROR")
            return False, {}
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}", "ERROR")
            return False, {}

    def test_portfolio_creation(self) -> bool:
        """Test creating a new portfolio for ledger testing"""
        self.log("\n🏦 PHASE 1: Portfolio Creation", "PHASE")
        self.log("=" * 60)

        portfolio_data = {"name": "Test Ledger Portfolio", "starting_balance": 50000.0}

        success, response = self.run_test(
            "Create Test Portfolio", "POST", "portfolios", 200, data=portfolio_data
        )

        if success and "id" in response:
            self.portfolio_id = response["id"]
            self.log(f"✅ Portfolio created with ID: {self.portfolio_id}")
            self.log(f"Starting balance: ${response.get('cash_balance', 0):,.2f}")
            return True
        else:
            self.log("❌ Failed to create portfolio", "ERROR")
            return False

    def test_transaction_creation(self) -> bool:
        """Test creating sample transactions (BUY/SELL)"""
        self.log("\n📊 PHASE 2: Transaction Creation", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        # Sample transactions for FIFO testing
        sample_transactions = [
            {
                "datetime": "2024-01-15T10:30:00Z",
                "symbol": "AAPL",
                "side": "BUY",
                "qty": 100,
                "price": 180.00,
                "fee": 1.50,
                "notes": "Initial AAPL purchase",
            },
            {
                "datetime": "2024-02-01T14:15:00Z",
                "symbol": "AAPL",
                "side": "BUY",
                "qty": 50,
                "price": 185.00,
                "fee": 0.75,
                "notes": "Additional AAPL purchase",
            },
            {
                "datetime": "2024-02-15T11:45:00Z",
                "symbol": "AAPL",
                "side": "SELL",
                "qty": 75,
                "price": 190.00,
                "fee": 1.00,
                "notes": "Partial AAPL sale",
            },
            {
                "datetime": "2024-01-20T09:30:00Z",
                "symbol": "MSFT",
                "side": "BUY",
                "qty": 50,
                "price": 350.00,
                "fee": 1.25,
                "notes": "MSFT purchase",
            },
            {
                "datetime": "2024-02-10T16:00:00Z",
                "symbol": "TSLA",
                "side": "BUY",
                "qty": 25,
                "price": 200.00,
                "fee": 0.50,
                "notes": "TSLA purchase",
            },
        ]

        transaction_results = []
        for i, tx_data in enumerate(sample_transactions, 1):
            tx_data["portfolio_id"] = self.portfolio_id

            success, response = self.run_test(
                f"Create Transaction {i} ({tx_data['symbol']} {tx_data['side']})",
                "POST",
                f"portfolios/{self.portfolio_id}/transactions",
                200,
                data=tx_data,
            )

            if success and "id" in response:
                self.transaction_ids.append(response["id"])
                transaction_results.append(True)
                self.log(
                    f"✅ Transaction created: {response['symbol']} {response['side']} {response['qty']} @ ${response['price']}"
                )
            else:
                transaction_results.append(False)
                self.log(f"❌ Failed to create transaction {i}", "ERROR")

        success_rate = sum(transaction_results) / len(transaction_results) * 100
        self.log(
            f"📊 Transaction creation success rate: {success_rate:.1f}% ({sum(transaction_results)}/{len(transaction_results)})"
        )

        return success_rate >= 80

    def test_transaction_listing(self) -> bool:
        """Test listing transactions for portfolio"""
        self.log("\n📋 PHASE 3: Transaction Listing", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        # Test getting all transactions
        success, response = self.run_test(
            "List All Transactions",
            "GET",
            f"portfolios/{self.portfolio_id}/transactions",
            200,
        )

        if not success:
            return False

        transactions = response if isinstance(response, list) else []
        self.log(f"📊 Found {len(transactions)} transactions")

        if len(transactions) == 0:
            self.log("❌ No transactions found", "ERROR")
            return False

        # Verify transaction structure
        required_fields = [
            "id",
            "portfolio_id",
            "datetime",
            "symbol",
            "side",
            "qty",
            "price",
            "fee",
        ]
        structure_valid = True

        for i, tx in enumerate(transactions[:3]):  # Check first 3 transactions
            missing_fields = [field for field in required_fields if field not in tx]
            if missing_fields:
                self.log(
                    f"❌ Transaction {i+1} missing fields: {missing_fields}", "ERROR"
                )
                structure_valid = False
            else:
                self.log(
                    f"✅ Transaction {i+1}: {tx['symbol']} {tx['side']} {tx['qty']} @ ${tx['price']}"
                )

        # Test filtering by symbol
        success_filter, filter_response = self.run_test(
            "List AAPL Transactions",
            "GET",
            f"portfolios/{self.portfolio_id}/transactions",
            200,
            params={"symbol": "AAPL"},
        )

        if success_filter:
            aapl_transactions = (
                filter_response if isinstance(filter_response, list) else []
            )
            aapl_count = len(aapl_transactions)
            self.log(f"📊 Found {aapl_count} AAPL transactions")

            # Verify all returned transactions are for AAPL
            all_aapl = all(tx.get("symbol") == "AAPL" for tx in aapl_transactions)
            if all_aapl:
                self.log("✅ Symbol filtering working correctly")
            else:
                self.log("❌ Symbol filtering not working correctly", "ERROR")
                structure_valid = False

        return structure_valid and len(transactions) >= 3

    def test_fifo_positions(self) -> bool:
        """Test FIFO position calculation"""
        self.log("\n🔄 PHASE 4: FIFO Position Calculation", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        success, response = self.run_test(
            "Get FIFO Positions",
            "GET",
            f"portfolios/{self.portfolio_id}/positions",
            200,
        )

        if not success:
            return False

        positions = response if isinstance(response, list) else []
        self.log(f"📊 Found {len(positions)} positions")

        if len(positions) == 0:
            self.log("❌ No positions found", "ERROR")
            return False

        # Verify position structure
        required_fields = ["symbol", "qty", "cost_basis", "avg_cost"]
        positions_valid = True

        expected_positions = {
            "AAPL": {"expected_qty": 75, "note": "100 + 50 - 75 = 75 shares remaining"},
            "MSFT": {"expected_qty": 50, "note": "50 shares purchased"},
            "TSLA": {"expected_qty": 25, "note": "25 shares purchased"},
        }

        for position in positions:
            symbol = position.get("symbol", "N/A")
            qty = position.get("qty", 0)
            cost_basis = position.get("cost_basis", 0)
            avg_cost = position.get("avg_cost", 0)

            self.log(
                f"📊 {symbol}: {qty} shares, Cost Basis: ${cost_basis:.2f}, Avg Cost: ${avg_cost:.2f}"
            )

            # Check required fields
            missing_fields = [
                field for field in required_fields if field not in position
            ]
            if missing_fields:
                self.log(
                    f"❌ Position {symbol} missing fields: {missing_fields}", "ERROR"
                )
                positions_valid = False
            else:
                self.log(f"✅ Position {symbol} has all required fields")

            # Verify FIFO calculations for known positions
            if symbol in expected_positions:
                expected_qty = expected_positions[symbol]["expected_qty"]
                note = expected_positions[symbol]["note"]

                if qty == expected_qty:
                    self.log(f"✅ FIFO calculation correct for {symbol}: {note}")
                else:
                    self.log(
                        f"❌ FIFO calculation incorrect for {symbol}: Expected {expected_qty}, got {qty}",
                        "ERROR",
                    )
                    self.log(f"   Note: {note}")
                    positions_valid = False

            # Verify avg_cost calculation
            if qty > 0 and cost_basis > 0:
                calculated_avg = cost_basis / qty
                if (
                    abs(calculated_avg - avg_cost) < 0.01
                ):  # Allow small rounding differences
                    self.log(f"✅ Average cost calculation correct for {symbol}")
                else:
                    self.log(
                        f"❌ Average cost calculation incorrect for {symbol}: Expected ${calculated_avg:.2f}, got ${avg_cost:.2f}",
                        "ERROR",
                    )
                    positions_valid = False

        return positions_valid and len(positions) >= 2

    def test_realized_pnl(self) -> bool:
        """Test realized P&L calculation using FIFO"""
        self.log("\n💰 PHASE 5: Realized P&L Calculation", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        success, response = self.run_test(
            "Get Realized P&L",
            "GET",
            f"portfolios/{self.portfolio_id}/realized-pnl",
            200,
        )

        if not success:
            return False

        pnl_data = response if isinstance(response, list) else []
        self.log(f"📊 Found realized P&L for {len(pnl_data)} symbols")

        # Verify P&L structure
        required_fields = ["symbol", "realized", "trades"]
        pnl_valid = True

        for pnl in pnl_data:
            symbol = pnl.get("symbol", "N/A")
            realized = pnl.get("realized", 0)
            trades = pnl.get("trades", 0)

            self.log(f"📊 {symbol}: Realized P&L: ${realized:.2f}, Trades: {trades}")

            # Check required fields
            missing_fields = [field for field in required_fields if field not in pnl]
            if missing_fields:
                self.log(f"❌ P&L {symbol} missing fields: {missing_fields}", "ERROR")
                pnl_valid = False
            else:
                self.log(f"✅ P&L {symbol} has all required fields")

        # Verify AAPL P&L calculation (we sold 75 shares)
        aapl_pnl = next((pnl for pnl in pnl_data if pnl.get("symbol") == "AAPL"), None)
        if aapl_pnl:
            realized = aapl_pnl.get("realized", 0)
            trades = aapl_pnl.get("trades", 0)

            # Expected calculation:
            # FIFO: Sell 75 shares from first lot (100 @ $180.015 including fees)
            # Sale proceeds: 75 * ($190 - $1.00/75) = 75 * $189.987 = $14,249.01
            # Cost: 75 * $180.015 = $13,501.13
            # Expected P&L: $14,249.01 - $13,501.13 = $747.88 (approximately)

            if trades == 1:
                self.log(f"✅ AAPL trade count correct: {trades}")
            else:
                self.log(
                    f"❌ AAPL trade count incorrect: Expected 1, got {trades}", "ERROR"
                )
                pnl_valid = False

            if realized > 0:
                self.log(f"✅ AAPL realized P&L positive: ${realized:.2f}")
            else:
                self.log(
                    f"❌ AAPL realized P&L should be positive, got ${realized:.2f}",
                    "ERROR",
                )
                pnl_valid = False
        else:
            self.log("❌ No AAPL P&L found (expected since we sold AAPL)", "ERROR")
            pnl_valid = False

        return pnl_valid

    def test_csv_import(self) -> bool:
        """Test CSV import functionality"""
        self.log("\n📄 PHASE 6: CSV Import", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        # Sample CSV data
        csv_data = """datetime,symbol,side,qty,price,fee,currency,notes
2024-03-01T10:00:00Z,NVDA,BUY,20,800.00,2.00,USD,NVDA purchase via CSV
2024-03-02T11:30:00Z,AMD,BUY,100,150.00,1.50,USD,AMD purchase via CSV
2024-03-03T14:45:00Z,NVDA,SELL,10,850.00,1.00,USD,Partial NVDA sale via CSV"""

        import_data = {"csv_data": csv_data}

        success, response = self.run_test(
            "Import CSV Transactions",
            "POST",
            f"portfolios/{self.portfolio_id}/import-csv",
            200,
            data=import_data,
        )

        if not success:
            return False

        imported_count = response.get("imported", 0)
        message = response.get("message", "")

        self.log(f"📊 Imported {imported_count} transactions")
        self.log(f"📊 Message: {message}")

        if imported_count == 3:
            self.log("✅ CSV import successful - all 3 transactions imported")

            # Verify imported transactions appear in transaction list
            success_verify, verify_response = self.run_test(
                "Verify CSV Import",
                "GET",
                f"portfolios/{self.portfolio_id}/transactions",
                200,
            )

            if success_verify:
                all_transactions = (
                    verify_response if isinstance(verify_response, list) else []
                )
                nvda_transactions = [
                    tx for tx in all_transactions if tx.get("symbol") == "NVDA"
                ]
                amd_transactions = [
                    tx for tx in all_transactions if tx.get("symbol") == "AMD"
                ]

                self.log(
                    f"📊 Found {len(nvda_transactions)} NVDA transactions (expected 2)"
                )
                self.log(
                    f"📊 Found {len(amd_transactions)} AMD transactions (expected 1)"
                )

                return len(nvda_transactions) == 2 and len(amd_transactions) == 1
            else:
                return False
        else:
            self.log(
                f"❌ Expected 3 imported transactions, got {imported_count}", "ERROR"
            )
            return False

    def test_enhanced_stats(self) -> bool:
        """Test enhanced stats endpoint with real P&L data"""
        self.log("\n📈 PHASE 7: Enhanced Stats", "PHASE")
        self.log("=" * 60)

        if not self.portfolio_id:
            self.log("❌ No portfolio ID available", "ERROR")
            return False

        success, response = self.run_test(
            "Get Enhanced Stats", "GET", f"portfolios/{self.portfolio_id}/stats", 200
        )

        if not success:
            return False

        # Verify stats structure
        required_fields = [
            "portfolio_id",
            "nav",
            "pnl_realized",
            "pnl_unrealized",
            "positions_count",
            "total_trades",
        ]
        missing_fields = [field for field in required_fields if field not in response]

        if missing_fields:
            self.log(f"❌ Stats missing required fields: {missing_fields}", "ERROR")
            return False

        portfolio_id = response.get("portfolio_id")
        nav = response.get("nav", 0)
        pnl_realized = response.get("pnl_realized", 0)
        pnl_unrealized = response.get("pnl_unrealized", 0)
        positions_count = response.get("positions_count", 0)
        total_trades = response.get("total_trades", 0)
        realized_pnl_by_symbol = response.get("realized_pnl_by_symbol", [])

        self.log(f"📊 Portfolio ID: {portfolio_id}")
        self.log(f"📊 NAV: ${nav:,.2f}")
        self.log(f"📊 Realized P&L: ${pnl_realized:.2f}")
        self.log(f"📊 Unrealized P&L: ${pnl_unrealized:.2f}")
        self.log(f"📊 Positions Count: {positions_count}")
        self.log(f"📊 Total Trades: {total_trades}")
        self.log(f"📊 Realized P&L by Symbol: {len(realized_pnl_by_symbol)} symbols")

        # Verify data consistency
        stats_valid = True

        if portfolio_id != self.portfolio_id:
            self.log(
                f"❌ Portfolio ID mismatch: Expected {self.portfolio_id}, got {portfolio_id}",
                "ERROR",
            )
            stats_valid = False

        if nav != 50000.0:  # Should match starting balance
            self.log(
                f"❌ NAV should be $50,000.00 (starting balance), got ${nav:,.2f}",
                "ERROR",
            )
            stats_valid = False
        else:
            self.log("✅ NAV matches starting balance")

        if positions_count < 4:  # Should have AAPL, MSFT, TSLA, NVDA, AMD positions
            self.log(
                f"❌ Expected at least 4 positions, got {positions_count}", "ERROR"
            )
            stats_valid = False
        else:
            self.log(f"✅ Positions count reasonable: {positions_count}")

        if total_trades < 2:  # Should have at least AAPL and NVDA sales
            self.log(
                f"❌ Expected at least 2 trades (sales), got {total_trades}", "ERROR"
            )
            stats_valid = False
        else:
            self.log(f"✅ Total trades reasonable: {total_trades}")

        if pnl_realized <= 0:
            self.log(
                f"❌ Expected positive realized P&L, got ${pnl_realized:.2f}", "ERROR"
            )
            stats_valid = False
        else:
            self.log(f"✅ Realized P&L positive: ${pnl_realized:.2f}")

        # Verify realized P&L by symbol structure
        if realized_pnl_by_symbol:
            for symbol_pnl in realized_pnl_by_symbol:
                symbol = symbol_pnl.get("symbol", "N/A")
                realized = symbol_pnl.get("realized", 0)
                trades = symbol_pnl.get("trades", 0)
                self.log(f"   {symbol}: ${realized:.2f} ({trades} trades)")
        else:
            self.log("❌ No realized P&L by symbol data", "ERROR")
            stats_valid = False

        return stats_valid

    def test_comprehensive_workflow(self) -> bool:
        """Test the complete ledger system workflow"""
        self.log("\n🔄 COMPREHENSIVE LEDGER SYSTEM WORKFLOW TEST", "HEADER")
        self.log("=" * 80)

        workflow_results = []

        # Phase 1: Portfolio Creation
        result1 = self.test_portfolio_creation()
        workflow_results.append(("Portfolio Creation", result1))

        # Phase 2: Transaction Creation
        result2 = self.test_transaction_creation()
        workflow_results.append(("Transaction Creation", result2))

        # Phase 3: Transaction Listing
        result3 = self.test_transaction_listing()
        workflow_results.append(("Transaction Listing", result3))

        # Phase 4: FIFO Positions
        result4 = self.test_fifo_positions()
        workflow_results.append(("FIFO Positions", result4))

        # Phase 5: Realized P&L
        result5 = self.test_realized_pnl()
        workflow_results.append(("Realized P&L", result5))

        # Phase 6: CSV Import
        result6 = self.test_csv_import()
        workflow_results.append(("CSV Import", result6))

        # Phase 7: Enhanced Stats
        result7 = self.test_enhanced_stats()
        workflow_results.append(("Enhanced Stats", result7))

        return workflow_results

    def generate_summary(self, workflow_results: List[tuple]) -> Dict:
        """Generate comprehensive test summary"""
        self.log("\n📊 LEDGER SYSTEM TEST SUMMARY", "HEADER")
        self.log("=" * 80)

        passed_tests = sum(1 for _, result in workflow_results if result)
        total_tests = len(workflow_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        self.log(
            f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})"
        )
        self.log(f"📊 Individual Tests: {self.tests_passed}/{self.tests_run} passed")

        # Detailed results
        self.log("\n📋 DETAILED RESULTS:")
        for phase_name, result in workflow_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status} {phase_name}")

        # Critical findings
        critical_issues = []
        working_features = []

        for phase_name, result in workflow_results:
            if result:
                working_features.append(phase_name)
            else:
                critical_issues.append(phase_name)

        if critical_issues:
            self.log("\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                self.log(f"   ❌ {issue}")

        if working_features:
            self.log("\n✅ WORKING FEATURES:")
            for feature in working_features:
                self.log(f"   ✅ {feature}")

        # Endpoint verification
        self.log("\n🔗 ENDPOINT VERIFICATION:")
        endpoints = [
            (
                "GET /portfolios/{pid}/transactions",
                "Transaction Listing" in working_features,
            ),
            (
                "POST /portfolios/{pid}/transactions",
                "Transaction Creation" in working_features,
            ),
            ("GET /portfolios/{pid}/positions", "FIFO Positions" in working_features),
            ("GET /portfolios/{pid}/realized-pnl", "Realized P&L" in working_features),
            ("POST /portfolios/{pid}/import-csv", "CSV Import" in working_features),
            ("GET /portfolios/{pid}/stats", "Enhanced Stats" in working_features),
        ]

        for endpoint, working in endpoints:
            status = "✅ WORKING" if working else "❌ FAILING"
            self.log(f"   {status} {endpoint}")

        # FIFO Logic Verification
        fifo_working = (
            "FIFO Positions" in working_features and "Realized P&L" in working_features
        )
        self.log(
            f"\n🔄 FIFO LOGIC: {'✅ WORKING' if fifo_working else '❌ ISSUES DETECTED'}"
        )

        # Final verdict
        if success_rate >= 85:
            verdict = "EXCELLENT - Ledger System fully functional"
            recommendation = "Ready for production use"
        elif success_rate >= 70:
            verdict = "GOOD - Ledger System mostly working"
            recommendation = "Minor issues need attention"
        else:
            verdict = "NEEDS ATTENTION - Significant issues found"
            recommendation = "Major fixes required before production"

        self.log(f"\n🎯 VERDICT: {verdict}")
        self.log(f"📋 RECOMMENDATION: {recommendation}")

        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "individual_tests": f"{self.tests_passed}/{self.tests_run}",
            "critical_issues": critical_issues,
            "working_features": working_features,
            "fifo_working": fifo_working,
            "verdict": verdict,
            "recommendation": recommendation,
            "portfolio_id": self.portfolio_id,
        }


def main():
    """Main test execution"""
    print("🚀 FlowMind Portfolios Ledger System Backend Testing")
    print("=" * 80)
    print("Testing new transaction endpoints and FIFO calculations...")
    print()

    tester = LedgerSystemTester()

    try:
        # Run comprehensive workflow test
        workflow_results = tester.test_comprehensive_workflow()

        # Generate summary
        summary = tester.generate_summary(workflow_results)

        # Return appropriate exit code
        if summary["success_rate"] >= 70:
            print("\n🎉 Ledger System testing completed successfully!")
            return 0
        else:
            print("\n🚨 Ledger System testing completed with issues!")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
