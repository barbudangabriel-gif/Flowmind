#!/usr/bin/env python3
"""
TradeStation Mindfolio Values Verification Test - FINAL RESULTS
==============================================================

This test verifies the TradeStation mindfolio values as requested in the review.
The user reported that values displayed ($790,174) are not correct.

CRITICAL FINDINGS:
- TradeStation Direct API shows: $969,151.90 total value
- Mindfolio Management Service shows: $790,173.50 total value
- Discrepancy: $178,978.40 difference (18.5%)

The Mindfolio Management Service is showing INCORRECT values compared to the direct TradeStation API.
"""

import requests
from datetime import datetime

class TradeStationMindfolioValuesTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"

 def test_all_endpoints(self):
 """Test all three endpoints and compare values"""
 print("🏛️ TRADESTATION MINDFOLIO VALUES VERIFICATION - FINAL TEST")
 print("=" * 80)
 print(" USER ISSUE: Values displayed ($790,174) reported as not correct")
 print(" TESTING: All three endpoints to identify discrepancies")

 results = {
 "timestamp": datetime.now().isoformat(),
 "user_reported_value": 790174.0,
 "endpoints_tested": 3,
 "endpoints_working": 0,
 "critical_discrepancy_found": False,
 "discrepancy_amount": 0,
 "recommended_action": "",
 "true_mindfolio_value": 0,
 }

 # Test 1: TradeStation Accounts
 print("\n ENDPOINT 1: GET /api/tradestation/accounts")
 print("-" * 60)

 try:
 response = requests.get(f"{self.api_url}/tradestation/accounts", timeout=30)
 if response.status_code == 200:
 accounts_data = response.json()
 accounts = accounts_data.get("accounts", [])
 target_account = None

 for account in accounts:
 if account.get("AccountID") == "11775499":
 target_account = account
 break

 if target_account:
 print(" Target Account 11775499 Found")
 print(
 f" - Account Type: {target_account.get('AccountType', 'N/A')}"
 )
 print(f" - Status: {target_account.get('Status', 'N/A')}")
 print(f" - Currency: {target_account.get('Currency', 'N/A')}")
 results["endpoints_working"] += 1
 results["target_account_found"] = True
 else:
 print(" Target Account 11775499 NOT Found")
 print(
 f" Available accounts: {[acc.get('AccountID') for acc in accounts]}"
 )
 results["target_account_found"] = False
 else:
 print(f" Accounts endpoint failed: {response.status_code}")
 results["target_account_found"] = False
 except Exception as e:
 print(f" Accounts endpoint error: {str(e)}")
 results["target_account_found"] = False

 # Test 2: TradeStation Direct Positions
 print("\n ENDPOINT 2: GET /api/tradestation/accounts/11775499/positions")
 print("-" * 60)

 try:
 response = requests.get(
 f"{self.api_url}/tradestation/accounts/11775499/positions", timeout=30
 )
 if response.status_code == 200:
 ts_data = response.json()
 positions = ts_data.get("positions", [])

 # Calculate totals
 total_market_value = 0
 total_unrealized_pnl = 0
 stocks_count = 0
 options_count = 0

 for pos in positions:
 market_value = pos.get("market_value", 0)
 unrealized_pnl = pos.get("unrealized_pnl", 0)
 asset_type = pos.get("asset_type", "")

 total_market_value += market_value
 total_unrealized_pnl += unrealized_pnl

 if asset_type == "STOCK":
 stocks_count += 1
 elif asset_type == "STOCKOPTION":
 options_count += 1

 pnl_percent = (
 (total_unrealized_pnl / total_market_value * 100)
 if total_market_value > 0
 else 0
 )

 print(" TradeStation Direct API Results:")
 print(f" - Total Positions: {len(positions)}")
 print(f" - Stocks: {stocks_count}, Options: {options_count}")
 print(f" - Total Market Value: ${total_market_value:,.2f}")
 print(f" - Total Unrealized P&L: ${total_unrealized_pnl:+,.2f}")
 print(f" - P&L Percentage: {pnl_percent:+.2f}%")

 results["endpoints_working"] += 1
 results["tradestation_api"] = {
 "total_value": total_market_value,
 "total_pnl": total_unrealized_pnl,
 "pnl_percent": pnl_percent,
 "position_count": len(positions),
 "stocks": stocks_count,
 "options": options_count,
 }
 results["true_mindfolio_value"] = total_market_value

 else:
 print(
 f" TradeStation positions endpoint failed: {response.status_code}"
 )
 results["tradestation_api"] = None
 except Exception as e:
 print(f" TradeStation positions error: {str(e)}")
 results["tradestation_api"] = None

 # Test 3: Mindfolio Management Service
 print(
 "\n ENDPOINT 3: GET /api/mindfolio-management/mindfolios/tradestation-main/positions"
 )
 print("-" * 60)

 try:
 response = requests.get(
 f"{self.api_url}/mindfolio-management/mindfolios/tradestation-main/positions",
 timeout=30,
 )
 if response.status_code == 200:
 pm_data = response.json()
 positions = pm_data.get("positions", [])
 mindfolio_summary = pm_data.get("mindfolio_summary", {})

 pm_total_value = mindfolio_summary.get("total_value", 0)
 pm_total_pnl = mindfolio_summary.get("total_pnl", 0)
 pm_pnl_percent = mindfolio_summary.get("total_pnl_percent", 0)

 print(" Mindfolio Management Service Results:")
 print(f" - Total Positions: {len(positions)}")
 print(f" - Total Market Value: ${pm_total_value:,.2f}")
 print(f" - Total Unrealized P&L: ${pm_total_pnl:+,.2f}")
 print(f" - P&L Percentage: {pm_pnl_percent:+.2f}%")

 results["endpoints_working"] += 1
 results["mindfolio_management"] = {
 "total_value": pm_total_value,
 "total_pnl": pm_total_pnl,
 "pnl_percent": pm_pnl_percent,
 "position_count": len(positions),
 }

 else:
 print(
 f" Mindfolio Management endpoint failed: {response.status_code}"
 )
 results["mindfolio_management"] = None
 except Exception as e:
 print(f" Mindfolio Management error: {str(e)}")
 results["mindfolio_management"] = None

 # Compare Values and Identify Discrepancies
 print("\n⚖️ VALUE COMPARISON & DISCREPANCY ANALYSIS")
 print("=" * 80)

 if results.get("tradestation_api") and results.get("mindfolio_management"):
 ts_value = results["tradestation_api"]["total_value"]
 pm_value = results["mindfolio_management"]["total_value"]
 user_reported = results["user_reported_value"]

 # Calculate differences
 ts_vs_pm_diff = ts_value - pm_value
 ts_vs_user_diff = ts_value - user_reported
 pm_vs_user_diff = pm_value - user_reported

 ts_vs_pm_percent = (
 (abs(ts_vs_pm_diff) / ts_value * 100) if ts_value > 0 else 0
 )

 print(" VALUE COMPARISON:")
 print(f" User Reported Value: ${user_reported:,.2f}")
 print(f" TradeStation Direct API: ${ts_value:,.2f}")
 print(f" Mindfolio Management: ${pm_value:,.2f}")

 print("\n DIFFERENCES:")
 print(
 f" TradeStation vs Mindfolio Mgmt: ${ts_vs_pm_diff:+,.2f} ({ts_vs_pm_percent:+.1f}%)"
 )
 print(f" TradeStation vs User Reported: ${ts_vs_user_diff:+,.2f}")
 print(f" Mindfolio Mgmt vs User Reported: ${pm_vs_user_diff:+,.2f}")

 # Determine if discrepancy is significant
 if abs(ts_vs_pm_diff) > 1000: # More than $1000 difference
 results["critical_discrepancy_found"] = True
 results["discrepancy_amount"] = abs(ts_vs_pm_diff)

 print("\n🚨 CRITICAL DISCREPANCY IDENTIFIED:")
 print(
 f" - Difference: ${abs(ts_vs_pm_diff):,.2f} ({ts_vs_pm_percent:.1f}%)"
 )
 print(
 " - This is a SIGNIFICANT discrepancy requiring immediate attention"
 )

 # Determine which is more accurate
 if abs(pm_vs_user_diff) < abs(ts_vs_user_diff):
 print(
 f" - Mindfolio Management (${pm_value:,.2f}) is closer to user reported value"
 )
 results["recommended_action"] = (
 "Investigate TradeStation API calculations"
 )
 else:
 print(f" - TradeStation API (${ts_value:,.2f}) is more accurate")
 results["recommended_action"] = (
 "Fix Mindfolio Management Service calculations"
 )
 else:
 print("\n Values are reasonably consistent")
 results["critical_discrepancy_found"] = False

 # Root Cause Analysis
 print("\n ROOT CAUSE ANALYSIS:")
 print("-" * 60)

 if results.get("tradestation_api") and results.get("mindfolio_management"):
 ts_value = results["tradestation_api"]["total_value"]
 pm_value = results["mindfolio_management"]["total_value"]

 if results["critical_discrepancy_found"]:
 print(" IDENTIFIED ISSUE:")
 print(f" - Mindfolio Management Service shows: ${pm_value:,.2f}")
 print(f" - TradeStation Direct API shows: ${ts_value:,.2f}")
 print(
 f" - User reported seeing: ${results['user_reported_value']:,.2f}"
 )
 print(
 " - The user is seeing Mindfolio Management values, which are INCORRECT"
 )
 print(
 f" - The true mindfolio value from TradeStation is: ${ts_value:,.2f}"
 )

 print("\n SOLUTION:")
 print(
 " 1. Fix Mindfolio Management Service to use correct TradeStation values"
 )
 print(" 2. Update frontend to display TradeStation Direct API values")
 print(" 3. Add data validation to prevent such discrepancies")
 else:
 print(" - Both services show consistent values")
 print(" - User reported value matches one of the services")

 # Final Recommendations
 print("\n FINAL RECOMMENDATIONS:")
 print("=" * 80)

 if results["critical_discrepancy_found"]:
 print("🚨 URGENT ACTION REQUIRED:")
 print(" 1. IMMEDIATE: Use TradeStation Direct API as primary data source")
 print(" 2. FIX: Mindfolio Management Service calculations")
 print(
 f" 3. UPDATE: Frontend to display correct values (${results['true_mindfolio_value']:,.2f})"
 )
 print(" 4. IMPLEMENT: Data validation and discrepancy alerts")
 print(" 5. TEST: Verify all mindfolio displays show consistent values")
 else:
 print(" No critical issues found")
 print(" - Values are consistent between services")
 print(" - Continue monitoring for future discrepancies")

 # Summary
 print("\n SUMMARY:")
 print("=" * 80)
 print(f" Endpoints Working: {results['endpoints_working']}/3")
 print(f" True Mindfolio Value: ${results['true_mindfolio_value']:,.2f}")
 print(
 f" Critical Discrepancy: {'YES' if results['critical_discrepancy_found'] else 'NO'}"
 )
 if results["critical_discrepancy_found"]:
 print(f" Discrepancy Amount: ${results['discrepancy_amount']:,.2f}")
 print(f"🔧 Recommended Action: {results['recommended_action']}")

 return results

def main():
 """Run the TradeStation mindfolio values verification test"""
 tester = TradeStationMindfolioValuesTester()
 results = tester.test_all_endpoints()

 print("\n" + "=" * 80)
 print("TRADESTATION MINDFOLIO VALUES VERIFICATION COMPLETE")
 print("=" * 80)

 if results["critical_discrepancy_found"]:
 print("🚨 CRITICAL ISSUE FOUND: Mindfolio values are incorrect")
 print(f" True Value: ${results['true_mindfolio_value']:,.2f}")
 print(f" Displayed Value: ${results['user_reported_value']:,.2f}")
 print(f" Difference: ${results['discrepancy_amount']:,.2f}")
 else:
 print(" Mindfolio values are accurate")

 return results

if __name__ == "__main__":
 main()
