#!/usr/bin/env python3
"""
TradeStation Portfolio Values Verification Test
==============================================

This test verifies the correct TradeStation portfolio values by testing specific endpoints
to check if the values are accurate as requested in the review.

Focus Areas:
1. GET `/api/tradestation/accounts` - Check accounts and their balance information
2. GET `/api/tradestation/accounts/11775499/positions` - Get exact position values and total portfolio value
3. GET `/api/portfolio-management/portfolios/tradestation-main/positions` - Compare portfolio management service values with direct TradeStation API

The user reports that values displayed ($790,174) are not correct, so we need to identify
where the error is coming from and get the true correct values from TradeStation API.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


class TradeStationPortfolioVerificationTester:
    def __init__(self, base_url="https://options-analytics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.portfolio_data = {}
        self.discrepancies = []

    def log_test(self, name: str, status: str, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if status == "PASS":
            self.tests_passed += 1
            print(f"✅ {name}: {details}")
        elif status == "FAIL":
            print(f"❌ {name}: {details}")
        elif status == "WARNING":
            print(f"⚠️  {name}: {details}")
        else:
            print(f"ℹ️  {name}: {details}")

    def make_request(
        self, method: str, endpoint: str, params: Dict = None, data: Dict = None
    ) -> tuple:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            if response.status_code == 200:
                try:
                    return True, response.json()
                except json.JSONDecodeError:
                    return False, {
                        "error": "Invalid JSON response",
                        "text": response.text,
                    }
            else:
                try:
                    error_data = response.json()
                    return False, {
                        "status_code": response.status_code,
                        "error": error_data,
                    }
                except:
                    return False, {
                        "status_code": response.status_code,
                        "error": response.text,
                    }

        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}
        except Exception as e:
            return False, {"error": str(e)}

    def test_tradestation_accounts(self) -> Dict[str, Any]:
        """Test GET /api/tradestation/accounts - Check accounts and their balance information"""
        print("\n" + "=" * 80)
        print("🏛️  PHASE 1: TradeStation Accounts Verification")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation accounts and balance information")
        print("📊 ENDPOINT: GET /api/tradestation/accounts")
        print("🔍 FOCUS: Account balances, account types, authentication status")

        success, response_data = self.make_request("GET", "tradestation/accounts")

        if not success:
            self.log_test(
                "TradeStation Accounts API",
                "FAIL",
                f"Failed to fetch accounts: {response_data.get('error', 'Unknown error')}",
            )
            return {"success": False, "accounts": [], "error": response_data}

        # Store accounts data for later comparison
        accounts_data = response_data
        self.portfolio_data["accounts"] = accounts_data

        # Verify response structure
        if not isinstance(accounts_data, dict):
            self.log_test(
                "Accounts Response Structure",
                "FAIL",
                f"Expected dict, got {type(accounts_data)}",
            )
            return {
                "success": False,
                "accounts": [],
                "error": "Invalid response structure",
            }

        # Check for accounts list
        accounts = accounts_data.get("accounts", [])
        if not accounts:
            self.log_test("Accounts List", "FAIL", "No accounts found in response")
            return {"success": False, "accounts": [], "error": "No accounts found"}

        self.log_test(
            "TradeStation Accounts API",
            "PASS",
            f"Successfully retrieved {len(accounts)} accounts",
        )

        # Analyze each account
        print("\n📊 ACCOUNT ANALYSIS:")
        print("-" * 60)

        target_account_found = False
        account_balances = {}

        for i, account in enumerate(accounts):
            account_id = account.get("account_id", "N/A")
            account_type = account.get("account_type", "N/A")
            account_name = account.get("name", "N/A")

            print(f"\n   Account #{i+1}: {account_id}")
            print(f"     - Type: {account_type}")
            print(f"     - Name: {account_name}")

            # Check if this is the target account (11775499)
            if account_id == "11775499":
                target_account_found = True
                print("     🎯 TARGET ACCOUNT FOUND!")

            # Look for balance information
            balance_fields = [
                "balance",
                "total_balance",
                "account_value",
                "equity",
                "cash_balance",
            ]
            balance_info = {}

            for field in balance_fields:
                if field in account:
                    balance_info[field] = account[field]
                    print(f"     - {field}: ${account[field]:,.2f}")

            if balance_info:
                account_balances[account_id] = balance_info
                self.log_test(
                    f"Account {account_id} Balance Info",
                    "PASS",
                    f"Found {len(balance_info)} balance fields",
                )
            else:
                self.log_test(
                    f"Account {account_id} Balance Info",
                    "WARNING",
                    "No balance information found in account data",
                )

            # Check for additional account details
            additional_fields = [
                "status",
                "currency",
                "margin_enabled",
                "day_trading_buying_power",
            ]
            additional_info = {}

            for field in additional_fields:
                if field in account:
                    additional_info[field] = account[field]
                    print(f"     - {field}: {account[field]}")

            if additional_info:
                print(
                    f"     ✅ Additional account details: {len(additional_info)} fields"
                )

        # Verify target account
        if target_account_found:
            self.log_test(
                "Target Account 11775499",
                "PASS",
                "Target account found in accounts list",
            )
        else:
            self.log_test(
                "Target Account 11775499",
                "FAIL",
                f"Target account not found. Available accounts: {[acc.get('account_id') for acc in accounts]}",
            )

        # Summary
        print("\n📊 ACCOUNTS SUMMARY:")
        print(f"   - Total Accounts: {len(accounts)}")
        print(
            f"   - Target Account Found: {'✅ Yes' if target_account_found else '❌ No'}"
        )
        print(f"   - Accounts with Balance Info: {len(account_balances)}")

        return {
            "success": True,
            "accounts": accounts,
            "target_account_found": target_account_found,
            "account_balances": account_balances,
            "total_accounts": len(accounts),
        }

    def test_tradestation_positions(
        self, account_id: str = "11775499"
    ) -> Dict[str, Any]:
        """Test GET /api/tradestation/accounts/{account_id}/positions - Get exact position values"""
        print("\n" + "=" * 80)
        print("🎯 PHASE 2: TradeStation Direct Positions Verification")
        print("=" * 80)
        print("🎯 OBJECTIVE: Get exact position values from TradeStation API directly")
        print(f"📊 ENDPOINT: GET /api/tradestation/accounts/{account_id}/positions")
        print(
            "🔍 FOCUS: Individual position values, total portfolio calculation, P&L accuracy"
        )

        success, response_data = self.make_request(
            "GET", f"tradestation/accounts/{account_id}/positions"
        )

        if not success:
            self.log_test(
                "TradeStation Positions API",
                "FAIL",
                f"Failed to fetch positions: {response_data.get('error', 'Unknown error')}",
            )
            return {"success": False, "positions": [], "error": response_data}

        # Store positions data for later comparison
        positions_data = response_data
        self.portfolio_data["tradestation_positions"] = positions_data

        # Verify response structure
        if not isinstance(positions_data, dict):
            self.log_test(
                "Positions Response Structure",
                "FAIL",
                f"Expected dict, got {type(positions_data)}",
            )
            return {
                "success": False,
                "positions": [],
                "error": "Invalid response structure",
            }

        # Extract positions list
        positions = positions_data.get("positions", [])
        if not positions:
            # Try alternative structure
            if "data" in positions_data:
                positions = positions_data["data"]
            else:
                self.log_test(
                    "Positions List", "FAIL", "No positions found in response"
                )
                return {
                    "success": False,
                    "positions": [],
                    "error": "No positions found",
                }

        self.log_test(
            "TradeStation Positions API",
            "PASS",
            f"Successfully retrieved {len(positions)} positions",
        )

        # Analyze positions
        print("\n📊 POSITIONS ANALYSIS:")
        print("-" * 60)

        total_market_value = 0
        total_unrealized_pnl = 0
        stocks_count = 0
        options_count = 0
        position_details = []

        print(f"   Found {len(positions)} total positions")

        # Analyze first 10 positions in detail
        for i, position in enumerate(positions[:10]):
            symbol = position.get("symbol", "N/A")
            quantity = position.get("quantity", 0)
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)
            avg_cost = position.get("avg_cost", 0)
            current_price = position.get("current_price", 0)
            position_type = position.get("type", "unknown")

            print(f"\n   Position #{i+1}: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Current Price: ${current_price:.2f}")
            print(f"     - Average Cost: ${avg_cost:.2f}")
            print(f"     - Market Value: ${market_value:,.2f}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:+,.2f}")
            print(f"     - Type: {position_type}")

            # Accumulate totals
            if isinstance(market_value, (int, float)):
                total_market_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                total_unrealized_pnl += unrealized_pnl

            # Count position types
            if position_type.lower() == "stock":
                stocks_count += 1
            elif position_type.lower() == "option":
                options_count += 1

            # Store position details
            position_details.append(
                {
                    "symbol": symbol,
                    "quantity": quantity,
                    "market_value": market_value,
                    "unrealized_pnl": unrealized_pnl,
                    "current_price": current_price,
                    "avg_cost": avg_cost,
                    "type": position_type,
                }
            )

        # Calculate totals for all positions
        print(f"\n📊 CALCULATING TOTALS FOR ALL {len(positions)} POSITIONS:")
        print("-" * 60)

        all_positions_market_value = 0
        all_positions_unrealized_pnl = 0

        for position in positions:
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)

            if isinstance(market_value, (int, float)):
                all_positions_market_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                all_positions_unrealized_pnl += unrealized_pnl

        print(
            f"   📊 Total Market Value (All Positions): ${all_positions_market_value:,.2f}"
        )
        print(
            f"   📊 Total Unrealized P&L (All Positions): ${all_positions_unrealized_pnl:+,.2f}"
        )
        print(
            f"   📊 Total P&L Percentage: {(all_positions_unrealized_pnl/all_positions_market_value*100):+.2f}%"
        )

        # Check for portfolio summary in response
        portfolio_summary = positions_data.get("portfolio_summary", {})
        if portfolio_summary:
            print("\n📊 PORTFOLIO SUMMARY FROM API:")
            print("-" * 60)

            summary_total_value = portfolio_summary.get("total_value", 0)
            summary_total_pnl = portfolio_summary.get("total_pnl", 0)
            summary_pnl_percent = portfolio_summary.get("total_pnl_percent", 0)

            print(f"   📊 API Total Value: ${summary_total_value:,.2f}")
            print(f"   📊 API Total P&L: ${summary_total_pnl:+,.2f}")
            print(f"   📊 API P&L Percentage: {summary_pnl_percent:+.2f}%")

            # Compare calculated vs API summary
            value_difference = abs(all_positions_market_value - summary_total_value)
            pnl_difference = abs(all_positions_unrealized_pnl - summary_total_pnl)

            if value_difference < 0.01:  # Within 1 cent
                self.log_test(
                    "Portfolio Value Calculation",
                    "PASS",
                    f"Calculated value matches API summary: ${summary_total_value:,.2f}",
                )
            else:
                self.log_test(
                    "Portfolio Value Calculation",
                    "WARNING",
                    f"Value difference: ${value_difference:,.2f} (Calculated: ${all_positions_market_value:,.2f}, API: ${summary_total_value:,.2f})",
                )
                self.discrepancies.append(
                    {
                        "type": "value_calculation",
                        "calculated": all_positions_market_value,
                        "api_summary": summary_total_value,
                        "difference": value_difference,
                    }
                )

        # Position type breakdown
        print("\n📊 POSITION TYPE BREAKDOWN:")
        print("-" * 60)

        type_counts = {}
        type_values = {}

        for position in positions:
            pos_type = position.get("type", "unknown").lower()
            market_value = position.get("market_value", 0)

            type_counts[pos_type] = type_counts.get(pos_type, 0) + 1
            type_values[pos_type] = type_values.get(pos_type, 0) + market_value

        for pos_type, count in type_counts.items():
            value = type_values.get(pos_type, 0)
            percentage = (
                (value / all_positions_market_value * 100)
                if all_positions_market_value > 0
                else 0
            )
            print(
                f"   📊 {pos_type.title()}: {count} positions, ${value:,.2f} ({percentage:.1f}%)"
            )

        # Summary
        print("\n📊 TRADESTATION POSITIONS SUMMARY:")
        print(f"   - Total Positions: {len(positions)}")
        print(f"   - Total Market Value: ${all_positions_market_value:,.2f}")
        print(f"   - Total Unrealized P&L: ${all_positions_unrealized_pnl:+,.2f}")
        print(f"   - Position Types: {list(type_counts.keys())}")

        return {
            "success": True,
            "positions": positions,
            "total_positions": len(positions),
            "total_market_value": all_positions_market_value,
            "total_unrealized_pnl": all_positions_unrealized_pnl,
            "position_types": type_counts,
            "position_values": type_values,
            "portfolio_summary": portfolio_summary,
            "sample_positions": position_details[:10],
        }

    def test_portfolio_management_positions(self) -> Dict[str, Any]:
        """Test GET /api/portfolio-management/portfolios/tradestation-main/positions"""
        print("\n" + "=" * 80)
        print("🔄 PHASE 3: Portfolio Management Service Verification")
        print("=" * 80)
        print(
            "🎯 OBJECTIVE: Compare Portfolio Management Service values with direct TradeStation API"
        )
        print(
            "📊 ENDPOINT: GET /api/portfolio-management/portfolios/tradestation-main/positions"
        )
        print("🔍 FOCUS: Value comparison, data consistency, integration accuracy")

        success, response_data = self.make_request(
            "GET", "portfolio-management/portfolios/tradestation-main/positions"
        )

        if not success:
            self.log_test(
                "Portfolio Management API",
                "FAIL",
                f"Failed to fetch portfolio management data: {response_data.get('error', 'Unknown error')}",
            )
            return {"success": False, "positions": [], "error": response_data}

        # Store portfolio management data
        pm_data = response_data
        self.portfolio_data["portfolio_management"] = pm_data

        # Verify response structure
        if not isinstance(pm_data, dict):
            self.log_test(
                "Portfolio Management Response Structure",
                "FAIL",
                f"Expected dict, got {type(pm_data)}",
            )
            return {
                "success": False,
                "positions": [],
                "error": "Invalid response structure",
            }

        # Extract positions and summary
        pm_positions = pm_data.get("positions", [])
        pm_summary = pm_data.get("portfolio_summary", {})

        if not pm_positions:
            self.log_test(
                "Portfolio Management Positions",
                "FAIL",
                "No positions found in response",
            )
            return {"success": False, "positions": [], "error": "No positions found"}

        self.log_test(
            "Portfolio Management API",
            "PASS",
            f"Successfully retrieved {len(pm_positions)} positions",
        )

        # Analyze Portfolio Management data
        print("\n📊 PORTFOLIO MANAGEMENT ANALYSIS:")
        print("-" * 60)

        pm_total_value = pm_summary.get("total_value", 0)
        pm_total_pnl = pm_summary.get("total_pnl", 0)
        pm_total_pnl_percent = pm_summary.get("total_pnl_percent", 0)

        print(f"   📊 PM Total Value: ${pm_total_value:,.2f}")
        print(f"   📊 PM Total P&L: ${pm_total_pnl:+,.2f}")
        print(f"   📊 PM P&L Percentage: {pm_total_pnl_percent:+.2f}%")
        print(f"   📊 PM Position Count: {len(pm_positions)}")

        # Calculate totals from individual positions
        pm_calculated_value = 0
        pm_calculated_pnl = 0

        print("\n📊 SAMPLE PORTFOLIO MANAGEMENT POSITIONS:")
        print("-" * 60)

        for i, position in enumerate(pm_positions[:10]):
            symbol = position.get("symbol", "N/A")
            quantity = position.get("quantity", 0)
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)
            current_price = position.get("current_price", 0)
            avg_cost = position.get("avg_cost", 0)

            print(f"   Position #{i+1}: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Market Value: ${market_value:,.2f}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:+,.2f}")

            if isinstance(market_value, (int, float)):
                pm_calculated_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                pm_calculated_pnl += unrealized_pnl

        # Calculate for all positions
        for position in pm_positions:
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)

            if isinstance(market_value, (int, float)):
                pm_calculated_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                pm_calculated_pnl += unrealized_pnl

        print("\n📊 PORTFOLIO MANAGEMENT CALCULATED TOTALS:")
        print(f"   📊 Calculated Total Value: ${pm_calculated_value:,.2f}")
        print(f"   📊 Calculated Total P&L: ${pm_calculated_pnl:+,.2f}")

        return {
            "success": True,
            "positions": pm_positions,
            "portfolio_summary": pm_summary,
            "total_positions": len(pm_positions),
            "summary_total_value": pm_total_value,
            "summary_total_pnl": pm_total_pnl,
            "calculated_total_value": pm_calculated_value,
            "calculated_total_pnl": pm_calculated_pnl,
        }

    def compare_portfolio_values(self, ts_data: Dict, pm_data: Dict) -> Dict[str, Any]:
        """Compare values between TradeStation direct API and Portfolio Management Service"""
        print("\n" + "=" * 80)
        print("⚖️  PHASE 4: Portfolio Values Comparison & Discrepancy Analysis")
        print("=" * 80)
        print(
            "🎯 OBJECTIVE: Identify discrepancies between TradeStation API and Portfolio Management Service"
        )
        print("🔍 FOCUS: Value differences, data source accuracy, error identification")

        if not ts_data.get("success") or not pm_data.get("success"):
            self.log_test(
                "Data Availability",
                "FAIL",
                "Cannot compare - missing data from one or both sources",
            )
            return {"success": False, "error": "Missing data for comparison"}

        # Extract values for comparison
        ts_total_value = ts_data.get("total_market_value", 0)
        ts_total_pnl = ts_data.get("total_unrealized_pnl", 0)
        ts_position_count = ts_data.get("total_positions", 0)

        pm_total_value = pm_data.get("summary_total_value", 0)
        pm_total_pnl = pm_data.get("summary_total_pnl", 0)
        pm_position_count = pm_data.get("total_positions", 0)

        print("\n📊 VALUE COMPARISON:")
        print("-" * 60)
        print("   TradeStation Direct API:")
        print(f"     - Total Value: ${ts_total_value:,.2f}")
        print(f"     - Total P&L: ${ts_total_pnl:+,.2f}")
        print(f"     - Position Count: {ts_position_count}")

        print("\n   Portfolio Management Service:")
        print(f"     - Total Value: ${pm_total_value:,.2f}")
        print(f"     - Total P&L: ${pm_total_pnl:+,.2f}")
        print(f"     - Position Count: {pm_position_count}")

        # Calculate differences
        value_difference = pm_total_value - ts_total_value
        pnl_difference = pm_total_pnl - ts_total_pnl
        position_count_difference = pm_position_count - ts_position_count

        print("\n📊 DIFFERENCES:")
        print("-" * 60)
        print(f"   Value Difference: ${value_difference:+,.2f}")
        print(f"   P&L Difference: ${pnl_difference:+,.2f}")
        print(f"   Position Count Difference: {position_count_difference:+d}")

        # Analyze significance of differences
        value_difference_percent = (
            (abs(value_difference) / ts_total_value * 100) if ts_total_value > 0 else 0
        )
        pnl_difference_percent = (
            (abs(pnl_difference) / abs(ts_total_pnl) * 100) if ts_total_pnl != 0 else 0
        )

        print(f"   Value Difference %: {value_difference_percent:.2f}%")
        print(f"   P&L Difference %: {pnl_difference_percent:.2f}%")

        # Determine if differences are significant
        significant_value_diff = value_difference_percent > 0.1  # More than 0.1%
        significant_pnl_diff = pnl_difference_percent > 1.0  # More than 1%
        significant_count_diff = abs(position_count_difference) > 0

        # Check against reported issue ($790,174)
        reported_value = 790174.0
        print("\n📊 REPORTED VALUE ANALYSIS:")
        print("-" * 60)
        print(f"   User Reported Value: ${reported_value:,.2f}")
        print(f"   TradeStation API Value: ${ts_total_value:,.2f}")
        print(f"   Portfolio Management Value: ${pm_total_value:,.2f}")

        ts_vs_reported = abs(ts_total_value - reported_value)
        pm_vs_reported = abs(pm_total_value - reported_value)

        print(f"   TradeStation vs Reported: ${ts_vs_reported:+,.2f}")
        print(f"   Portfolio Mgmt vs Reported: ${pm_vs_reported:+,.2f}")

        # Determine which is closer to reported value
        if ts_vs_reported < pm_vs_reported:
            closer_to_reported = "TradeStation API"
            self.log_test(
                "Accuracy vs Reported Value",
                "INFO",
                f"TradeStation API (${ts_total_value:,.2f}) is closer to reported value",
            )
        elif pm_vs_reported < ts_vs_reported:
            closer_to_reported = "Portfolio Management"
            self.log_test(
                "Accuracy vs Reported Value",
                "INFO",
                f"Portfolio Management (${pm_total_value:,.2f}) is closer to reported value",
            )
        else:
            closer_to_reported = "Equal"
            self.log_test(
                "Accuracy vs Reported Value",
                "INFO",
                "Both sources equally close to reported value",
            )

        # Issue analysis
        print("\n🔍 ISSUE ANALYSIS:")
        print("-" * 60)

        issues_found = []

        if significant_value_diff:
            issues_found.append(
                f"Significant value difference: ${value_difference:+,.2f} ({value_difference_percent:.2f}%)"
            )
            self.log_test(
                "Value Consistency",
                "FAIL",
                f"Significant difference: ${value_difference:+,.2f}",
            )
        else:
            self.log_test(
                "Value Consistency",
                "PASS",
                f"Values are consistent (difference: ${value_difference:+,.2f})",
            )

        if significant_pnl_diff:
            issues_found.append(
                f"Significant P&L difference: ${pnl_difference:+,.2f} ({pnl_difference_percent:.2f}%)"
            )
            self.log_test(
                "P&L Consistency",
                "FAIL",
                f"Significant difference: ${pnl_difference:+,.2f}",
            )
        else:
            self.log_test(
                "P&L Consistency",
                "PASS",
                f"P&L values are consistent (difference: ${pnl_difference:+,.2f})",
            )

        if significant_count_diff:
            issues_found.append(
                f"Position count mismatch: {position_count_difference:+d} positions"
            )
            self.log_test(
                "Position Count Consistency",
                "FAIL",
                f"Count difference: {position_count_difference:+d}",
            )
        else:
            self.log_test("Position Count Consistency", "PASS", "Position counts match")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 60)

        if not issues_found:
            print("   ✅ No significant discrepancies found between data sources")
            print(
                "   ✅ Both TradeStation API and Portfolio Management Service show consistent values"
            )
            if ts_vs_reported > 1000:  # More than $1000 difference
                print(
                    f"   ⚠️  However, both differ significantly from user reported value (${reported_value:,.2f})"
                )
                print(
                    "   🔍 Investigate if user is looking at different account or time period"
                )
        else:
            print("   🚨 Discrepancies found between data sources:")
            for issue in issues_found:
                print(f"     - {issue}")

            if closer_to_reported == "TradeStation API":
                print(
                    "   💡 Recommendation: Use TradeStation API as primary source (closer to reported value)"
                )
                print(
                    "   🔧 Fix Portfolio Management Service to match TradeStation API values"
                )
            elif closer_to_reported == "Portfolio Management":
                print("   💡 Recommendation: Verify Portfolio Management calculations")
                print("   🔧 Check if Portfolio Management has more recent data")

            print("   🔍 Additional investigation needed:")
            print("     - Check data refresh timestamps")
            print("     - Verify position filtering (active vs all positions)")
            print("     - Confirm account ID consistency")
            print("     - Check for currency conversion issues")

        return {
            "success": True,
            "ts_total_value": ts_total_value,
            "pm_total_value": pm_total_value,
            "value_difference": value_difference,
            "value_difference_percent": value_difference_percent,
            "pnl_difference": pnl_difference,
            "position_count_difference": position_count_difference,
            "significant_differences": significant_value_diff
            or significant_pnl_diff
            or significant_count_diff,
            "issues_found": issues_found,
            "closer_to_reported": closer_to_reported,
            "reported_value": reported_value,
            "ts_vs_reported": ts_vs_reported,
            "pm_vs_reported": pm_vs_reported,
        }

    def generate_final_report(
        self,
        accounts_result: Dict,
        ts_result: Dict,
        pm_result: Dict,
        comparison_result: Dict,
    ):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📋 FINAL VERIFICATION REPORT")
        print("=" * 80)
        print("🎯 OBJECTIVE: TradeStation Portfolio Values Verification")
        print(f"📅 TEST DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔍 USER ISSUE: Values displayed ($790,174) reported as incorrect")

        # Test Summary
        print("\n📊 TEST EXECUTION SUMMARY:")
        print("-" * 60)
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")

        # Data Sources Summary
        print("\n📊 DATA SOURCES VERIFICATION:")
        print("-" * 60)

        if accounts_result.get("success"):
            print(
                f"   ✅ TradeStation Accounts API: {accounts_result.get('total_accounts', 0)} accounts"
            )
            print(
                f"     - Target Account (11775499): {'✅ Found' if accounts_result.get('target_account_found') else '❌ Not Found'}"
            )
        else:
            print("   ❌ TradeStation Accounts API: Failed")

        if ts_result.get("success"):
            print(
                f"   ✅ TradeStation Positions API: {ts_result.get('total_positions', 0)} positions"
            )
            print(f"     - Total Value: ${ts_result.get('total_market_value', 0):,.2f}")
            print(
                f"     - Total P&L: ${ts_result.get('total_unrealized_pnl', 0):+,.2f}"
            )
        else:
            print("   ❌ TradeStation Positions API: Failed")

        if pm_result.get("success"):
            print(
                f"   ✅ Portfolio Management API: {pm_result.get('total_positions', 0)} positions"
            )
            print(
                f"     - Total Value: ${pm_result.get('summary_total_value', 0):,.2f}"
            )
            print(f"     - Total P&L: ${pm_result.get('summary_total_pnl', 0):+,.2f}")
        else:
            print("   ❌ Portfolio Management API: Failed")

        # Value Analysis
        print("\n💰 VALUE ANALYSIS:")
        print("-" * 60)

        if comparison_result.get("success"):
            reported_value = comparison_result.get("reported_value", 790174)
            ts_value = comparison_result.get("ts_total_value", 0)
            pm_value = comparison_result.get("pm_total_value", 0)

            print(f"   User Reported Value: ${reported_value:,.2f}")
            print(f"   TradeStation API Value: ${ts_value:,.2f}")
            print(f"   Portfolio Management Value: ${pm_value:,.2f}")

            print("\n   Differences from Reported Value:")
            print(
                f"     - TradeStation API: ${comparison_result.get('ts_vs_reported', 0):+,.2f}"
            )
            print(
                f"     - Portfolio Management: ${comparison_result.get('pm_vs_reported', 0):+,.2f}"
            )

            print("\n   Inter-Service Difference:")
            print(
                f"     - Value Difference: ${comparison_result.get('value_difference', 0):+,.2f}"
            )
            print(
                f"     - Percentage Difference: {comparison_result.get('value_difference_percent', 0):.2f}%"
            )

        # Issue Identification
        print("\n🔍 ISSUE IDENTIFICATION:")
        print("-" * 60)

        if comparison_result.get("success"):
            issues = comparison_result.get("issues_found", [])
            if issues:
                print("   🚨 Issues Found:")
                for issue in issues:
                    print(f"     - {issue}")
            else:
                print("   ✅ No significant discrepancies between data sources")

            # Determine root cause
            ts_vs_reported = comparison_result.get("ts_vs_reported", 0)
            pm_vs_reported = comparison_result.get("pm_vs_reported", 0)

            if ts_vs_reported > 1000 and pm_vs_reported > 1000:
                print("\n   🎯 ROOT CAUSE ANALYSIS:")
                print(
                    f"     - Both APIs show values significantly different from reported ${reported_value:,.2f}"
                )
                print("     - This suggests the user may be looking at:")
                print("       • Different account ID")
                print("       • Different time period")
                print("       • Cached/stale data")
                print("       • Different portfolio view (e.g., including cash)")
            elif abs(comparison_result.get("value_difference", 0)) > 1000:
                print("\n   🎯 ROOT CAUSE ANALYSIS:")
                print(
                    "     - Significant difference between TradeStation API and Portfolio Management"
                )
                print("     - Portfolio Management Service may have calculation errors")
                print("     - Data synchronization issues possible")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 60)

        if comparison_result.get("success"):
            closer_source = comparison_result.get("closer_to_reported", "Unknown")

            if closer_source == "TradeStation API":
                print("   1. ✅ Use TradeStation API as the primary data source")
                print("   2. 🔧 Fix Portfolio Management Service calculations")
                print("   3. 📊 Display TradeStation API values in the frontend")
            elif closer_source == "Portfolio Management":
                print("   1. 🔍 Verify Portfolio Management calculations are correct")
                print("   2. ⚠️  Investigate why TradeStation API differs")
                print("   3. 📊 Consider using Portfolio Management values if verified")
            else:
                print("   1. 🔍 Both sources need investigation")
                print(
                    "   2. 📞 Contact user to verify expected value and account details"
                )
                print("   3. 🕐 Check if timing/market hours affect the values")

            print("\n   Additional Actions:")
            print("   4. 🔄 Implement real-time data refresh")
            print("   5. 📝 Add data source indicators in UI")
            print("   6. ⚠️  Add discrepancy alerts for large differences")
            print("   7. 🧪 Add automated testing for value consistency")

        # Final Verdict
        print("\n🎯 FINAL VERDICT:")
        print("-" * 60)

        if self.tests_passed / self.tests_run >= 0.8:
            if comparison_result.get("significant_differences"):
                print(
                    "   ⚠️  PARTIAL SUCCESS: APIs are working but show different values"
                )
                print("   🔧 Action Required: Fix data consistency issues")
            else:
                print("   ✅ SUCCESS: All APIs working and values are consistent")
                print(
                    "   🔍 Investigation: User reported value may be from different source"
                )
        else:
            print("   ❌ FAILURE: Critical API issues prevent proper verification")
            print(
                "   🚨 Urgent: Fix API connectivity before addressing value discrepancies"
            )

        # True Values Summary
        print("\n📊 TRUE PORTFOLIO VALUES (Best Available):")
        print("-" * 60)

        if ts_result.get("success") and pm_result.get("success"):
            if (
                abs(comparison_result.get("value_difference", 0)) < 100
            ):  # Less than $100 difference
                print(
                    f"   💰 Verified Portfolio Value: ${ts_result.get('total_market_value', 0):,.2f}"
                )
                print(
                    f"   📈 Verified P&L: ${ts_result.get('total_unrealized_pnl', 0):+,.2f}"
                )
                print("   ✅ Confidence: High (both sources agree)")
            else:
                print(
                    f"   💰 TradeStation API Value: ${ts_result.get('total_market_value', 0):,.2f}"
                )
                print(
                    f"   💰 Portfolio Mgmt Value: ${pm_result.get('summary_total_value', 0):,.2f}"
                )
                print("   ⚠️  Confidence: Medium (sources disagree)")
        elif ts_result.get("success"):
            print(
                f"   💰 TradeStation API Value: ${ts_result.get('total_market_value', 0):,.2f}"
            )
            print(
                f"   📈 TradeStation API P&L: ${ts_result.get('total_unrealized_pnl', 0):+,.2f}"
            )
            print("   ✅ Confidence: Medium (single source)")
        elif pm_result.get("success"):
            print(
                f"   💰 Portfolio Mgmt Value: ${pm_result.get('summary_total_value', 0):,.2f}"
            )
            print(
                f"   📈 Portfolio Mgmt P&L: ${pm_result.get('summary_total_pnl', 0):+,.2f}"
            )
            print("   ⚠️  Confidence: Low (fallback source only)")
        else:
            print("   ❌ Unable to determine true portfolio values")
            print("   🚨 Critical: All data sources failed")

    def run_comprehensive_test(self):
        """Run the complete TradeStation portfolio verification test"""
        print("🏛️  TRADESTATION PORTFOLIO VALUES VERIFICATION TEST")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify correct TradeStation portfolio values")
        print("📊 USER ISSUE: Values displayed ($790,174) reported as not correct")
        print("🔍 TESTING: Direct TradeStation API vs Portfolio Management Service")
        print("⚖️  GOAL: Identify discrepancies and determine true correct values")

        # Phase 1: Test TradeStation Accounts
        accounts_result = self.test_tradestation_accounts()

        # Phase 2: Test TradeStation Positions (only if accounts successful)
        if accounts_result.get("success") and accounts_result.get(
            "target_account_found"
        ):
            ts_result = self.test_tradestation_positions("11775499")
        else:
            print(
                "\n⚠️  Skipping TradeStation positions test - account verification failed"
            )
            ts_result = {"success": False, "error": "Account verification failed"}

        # Phase 3: Test Portfolio Management Service
        pm_result = self.test_portfolio_management_positions()

        # Phase 4: Compare Values
        if ts_result.get("success") and pm_result.get("success"):
            comparison_result = self.compare_portfolio_values(ts_result, pm_result)
        else:
            print("\n⚠️  Skipping comparison - insufficient data from APIs")
            comparison_result = {
                "success": False,
                "error": "Insufficient data for comparison",
            }

        # Generate Final Report
        self.generate_final_report(
            accounts_result, ts_result, pm_result, comparison_result
        )

        return {
            "accounts": accounts_result,
            "tradestation_positions": ts_result,
            "portfolio_management": pm_result,
            "comparison": comparison_result,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100)
            if self.tests_run > 0
            else 0,
        }


def main():
    """Main function to run the TradeStation portfolio verification test"""
    print("Starting TradeStation Portfolio Values Verification Test...")

    tester = TradeStationPortfolioVerificationTester()
    results = tester.run_comprehensive_test()

    print("\n" + "=" * 80)
    print("TEST EXECUTION COMPLETED")
    print("=" * 80)
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Tests Passed: {results['tests_passed']}")

    return results


if __name__ == "__main__":
    main()
