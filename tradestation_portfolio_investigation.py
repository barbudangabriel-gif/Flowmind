#!/usr/bin/env python3
"""
CRITICAL INVESTIGATION: TradeStation Portfolio Data Discrepancy
==============================================================

User reports displayed positions are NOT their real TradeStation positions.
This script investigates the critical discrepancy between:
- TradeStation Direct API: $969,473.90 total portfolio value
- Portfolio Management Service: $790,173.50 total portfolio value
- Difference: $179,300.40 (18.5%)

Focus Areas:
1. GET /api/tradestation/accounts - Verify which TradeStation account is being accessed
2. GET /api/tradestation/accounts/{account_id}/positions - Check if this returns REAL user positions or mock data
3. GET /api/portfolio-management/portfolios/tradestation-main/positions - Check if Portfolio Management Service is using mock data
4. Compare data sources to identify where the fake/mock positions are coming from
"""

import requests
import json
from datetime import datetime
import sys

class TradeStationPortfolioInvestigator:
    def __init__(self, base_url="https://put-selling-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.investigation_results = {}
        
    def log_finding(self, category, finding, severity="INFO"):
        """Log investigation findings"""
        if category not in self.investigation_results:
            self.investigation_results[category] = []
        
        self.investigation_results[category].append({
            "finding": finding,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
        severity_icon = {
            "CRITICAL": "🚨",
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "SUCCESS": "✅"
        }
        
        print(f"{severity_icon.get(severity, 'ℹ️')} [{category}] {finding}")

    def make_request(self, endpoint, method="GET", data=None):
        """Make API request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def investigate_tradestation_accounts(self):
        """PHASE 1: Investigate TradeStation accounts access"""
        print("\n" + "="*80)
        print("🔍 PHASE 1: TRADESTATION ACCOUNTS INVESTIGATION")
        print("="*80)
        print("🎯 OBJECTIVE: Verify which TradeStation account is being accessed")
        print("📋 CHECKING: Account details, authentication status, account types")
        
        # Test TradeStation accounts endpoint
        result = self.make_request("tradestation/accounts")
        
        if not result["success"]:
            self.log_finding("ACCOUNTS", f"Failed to access TradeStation accounts: {result['error']}", "CRITICAL")
            return None
        
        if result["status_code"] != 200:
            self.log_finding("ACCOUNTS", f"TradeStation accounts returned status {result['status_code']}", "CRITICAL")
            return None
        
        accounts_data = result["data"]
        self.log_finding("ACCOUNTS", f"Successfully retrieved TradeStation accounts data", "SUCCESS")
        
        # Analyze accounts structure
        if isinstance(accounts_data, dict) and "data" in accounts_data:
            accounts = accounts_data["data"]
        elif isinstance(accounts_data, list):
            accounts = accounts_data
        else:
            self.log_finding("ACCOUNTS", f"Unexpected accounts data structure: {type(accounts_data)}", "WARNING")
            accounts = []
        
        print(f"\n📊 ACCOUNTS ANALYSIS:")
        print(f"   Total Accounts Found: {len(accounts)}")
        
        target_account_id = None
        
        for i, account in enumerate(accounts):
            account_id = account.get("AccountID", "Unknown")
            account_type = account.get("TypeDescription", "Unknown")
            status = account.get("Status", "Unknown")
            currency = account.get("Currency", "Unknown")
            
            print(f"\n   Account #{i+1}:")
            print(f"     - Account ID: {account_id}")
            print(f"     - Type: {account_type}")
            print(f"     - Status: {status}")
            print(f"     - Currency: {currency}")
            
            # Look for the target account (11775499 from test results)
            if str(account_id) == "11775499":
                target_account_id = account_id
                self.log_finding("ACCOUNTS", f"Found target account 11775499 (Margin account)", "SUCCESS")
                print(f"     ✅ TARGET ACCOUNT IDENTIFIED")
            
            # Check for any suspicious account details
            if status != "Active":
                self.log_finding("ACCOUNTS", f"Account {account_id} has non-active status: {status}", "WARNING")
            
            if currency != "USD":
                self.log_finding("ACCOUNTS", f"Account {account_id} uses non-USD currency: {currency}", "WARNING")
        
        if not target_account_id:
            self.log_finding("ACCOUNTS", "Target account 11775499 not found in accounts list", "CRITICAL")
            # Use first available account for investigation
            if accounts:
                target_account_id = accounts[0].get("AccountID")
                self.log_finding("ACCOUNTS", f"Using first available account {target_account_id} for investigation", "WARNING")
        
        return target_account_id

    def investigate_tradestation_positions(self, account_id):
        """PHASE 2: Investigate TradeStation direct positions"""
        print("\n" + "="*80)
        print("🔍 PHASE 2: TRADESTATION DIRECT POSITIONS INVESTIGATION")
        print("="*80)
        print(f"🎯 OBJECTIVE: Check if TradeStation API returns REAL user positions")
        print(f"📋 ACCOUNT: {account_id}")
        print(f"🔍 LOOKING FOR: Real positions vs mock data indicators")
        
        # Test TradeStation positions endpoint
        result = self.make_request(f"tradestation/accounts/{account_id}/positions")
        
        if not result["success"]:
            self.log_finding("TS_POSITIONS", f"Failed to access TradeStation positions: {result['error']}", "CRITICAL")
            return None
        
        if result["status_code"] != 200:
            self.log_finding("TS_POSITIONS", f"TradeStation positions returned status {result['status_code']}", "CRITICAL")
            return None
        
        positions_data = result["data"]
        self.log_finding("TS_POSITIONS", f"Successfully retrieved TradeStation positions data", "SUCCESS")
        
        # Analyze positions structure
        if isinstance(positions_data, dict) and "data" in positions_data:
            positions = positions_data["data"]
        elif isinstance(positions_data, list):
            positions = positions_data
        else:
            self.log_finding("TS_POSITIONS", f"Unexpected positions data structure: {type(positions_data)}", "WARNING")
            positions = []
        
        print(f"\n📊 TRADESTATION POSITIONS ANALYSIS:")
        print(f"   Total Positions Found: {len(positions)}")
        
        # Calculate portfolio totals
        total_market_value = 0
        total_unrealized_pnl = 0
        stocks_count = 0
        options_count = 0
        
        # Analyze position types and values
        position_symbols = []
        suspicious_patterns = []
        
        for i, position in enumerate(positions[:10]):  # Analyze first 10 positions
            symbol = position.get("Symbol", "Unknown")
            quantity = position.get("Quantity", 0)
            market_value = position.get("MarketValue", 0)
            unrealized_pnl = position.get("UnrealizedProfitLoss", 0)
            asset_type = position.get("AssetType", "Unknown")
            
            position_symbols.append(symbol)
            
            # Add to totals
            if isinstance(market_value, (int, float)):
                total_market_value += market_value
            if isinstance(unrealized_pnl, (int, float)):
                total_unrealized_pnl += unrealized_pnl
            
            # Count asset types
            if asset_type == "Stock":
                stocks_count += 1
            elif asset_type == "Option":
                options_count += 1
            
            print(f"\n   Position #{i+1}:")
            print(f"     - Symbol: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Market Value: ${market_value:,.2f}" if isinstance(market_value, (int, float)) else f"     - Market Value: {market_value}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:,.2f}" if isinstance(unrealized_pnl, (int, float)) else f"     - Unrealized P&L: {unrealized_pnl}")
            print(f"     - Asset Type: {asset_type}")
            
            # Check for mock data patterns
            if symbol in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN", "QQQ"]:
                if quantity in [100, 200, 300, 500, 1000]:  # Common mock quantities
                    suspicious_patterns.append(f"{symbol}: {quantity} shares (common mock quantity)")
            
            # Check for unrealistic values
            if isinstance(market_value, (int, float)) and market_value == 0:
                suspicious_patterns.append(f"{symbol}: Zero market value")
        
        # Calculate total for all positions
        if len(positions) > 10:
            for position in positions[10:]:
                market_value = position.get("MarketValue", 0)
                unrealized_pnl = position.get("UnrealizedProfitLoss", 0)
                asset_type = position.get("AssetType", "Unknown")
                
                if isinstance(market_value, (int, float)):
                    total_market_value += market_value
                if isinstance(unrealized_pnl, (int, float)):
                    total_unrealized_pnl += unrealized_pnl
                
                if asset_type == "Stock":
                    stocks_count += 1
                elif asset_type == "Option":
                    options_count += 1
        
        print(f"\n📊 PORTFOLIO TOTALS (TradeStation Direct):")
        print(f"   Total Market Value: ${total_market_value:,.2f}")
        print(f"   Total Unrealized P&L: ${total_unrealized_pnl:,.2f}")
        print(f"   P&L Percentage: {(total_unrealized_pnl/total_market_value*100):+.2f}%" if total_market_value > 0 else "   P&L Percentage: N/A")
        print(f"   Stocks: {stocks_count}")
        print(f"   Options: {options_count}")
        print(f"   Total Positions: {len(positions)}")
        
        # Log key findings
        self.log_finding("TS_POSITIONS", f"TradeStation Direct API shows ${total_market_value:,.2f} total portfolio value", "INFO")
        self.log_finding("TS_POSITIONS", f"TradeStation shows {len(positions)} total positions ({stocks_count} stocks, {options_count} options)", "INFO")
        
        # Check for suspicious patterns
        if suspicious_patterns:
            self.log_finding("TS_POSITIONS", f"Suspicious mock data patterns detected: {len(suspicious_patterns)} issues", "WARNING")
            for pattern in suspicious_patterns[:5]:  # Show first 5
                self.log_finding("TS_POSITIONS", f"Mock pattern: {pattern}", "WARNING")
        else:
            self.log_finding("TS_POSITIONS", "No obvious mock data patterns detected in TradeStation positions", "SUCCESS")
        
        # Check for expected user positions (from review request)
        user_reported_symbols = ["AMZN", "QQQ", "GOOGL"]  # User said these are NOT their positions
        found_reported_symbols = [symbol for symbol in position_symbols if symbol in user_reported_symbols]
        
        if found_reported_symbols:
            self.log_finding("TS_POSITIONS", f"Found user-reported 'fake' symbols in TradeStation: {found_reported_symbols}", "CRITICAL")
        else:
            self.log_finding("TS_POSITIONS", "User-reported 'fake' symbols not found in TradeStation direct API", "INFO")
        
        return {
            "total_market_value": total_market_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "positions_count": len(positions),
            "stocks_count": stocks_count,
            "options_count": options_count,
            "position_symbols": position_symbols,
            "suspicious_patterns": suspicious_patterns
        }

    def investigate_portfolio_management_service(self):
        """PHASE 3: Investigate Portfolio Management Service"""
        print("\n" + "="*80)
        print("🔍 PHASE 3: PORTFOLIO MANAGEMENT SERVICE INVESTIGATION")
        print("="*80)
        print("🎯 OBJECTIVE: Check if Portfolio Management Service is using mock data")
        print("📋 ENDPOINT: /api/portfolio-management/portfolios/tradestation-main/positions")
        print("🔍 LOOKING FOR: Mock data vs real TradeStation integration")
        
        # Test Portfolio Management Service endpoint
        result = self.make_request("portfolio-management/portfolios/tradestation-main/positions")
        
        if not result["success"]:
            self.log_finding("PM_SERVICE", f"Failed to access Portfolio Management Service: {result['error']}", "CRITICAL")
            return None
        
        if result["status_code"] != 200:
            self.log_finding("PM_SERVICE", f"Portfolio Management Service returned status {result['status_code']}", "CRITICAL")
            return None
        
        pm_data = result["data"]
        self.log_finding("PM_SERVICE", f"Successfully retrieved Portfolio Management Service data", "SUCCESS")
        
        # Analyze Portfolio Management Service structure
        positions = pm_data.get("positions", [])
        portfolio_summary = pm_data.get("portfolio_summary", {})
        
        print(f"\n📊 PORTFOLIO MANAGEMENT SERVICE ANALYSIS:")
        print(f"   Total Positions Found: {len(positions)}")
        
        # Extract portfolio summary
        pm_total_value = portfolio_summary.get("total_value", 0)
        pm_total_pnl = portfolio_summary.get("total_pnl", 0)
        pm_pnl_percent = portfolio_summary.get("total_pnl_percent", 0)
        
        print(f"\n📊 PORTFOLIO SUMMARY (Portfolio Management Service):")
        print(f"   Total Value: ${pm_total_value:,.2f}")
        print(f"   Total P&L: ${pm_total_pnl:,.2f}")
        print(f"   P&L Percentage: {pm_pnl_percent:+.2f}%")
        
        # Analyze positions
        pm_position_symbols = []
        pm_stocks_count = 0
        pm_options_count = 0
        pm_mock_indicators = []
        
        for i, position in enumerate(positions[:10]):  # Analyze first 10 positions
            symbol = position.get("symbol", "Unknown")
            quantity = position.get("quantity", 0)
            market_value = position.get("market_value", 0)
            unrealized_pnl = position.get("unrealized_pnl", 0)
            position_type = position.get("type", "Unknown")
            
            pm_position_symbols.append(symbol)
            
            # Count types
            if position_type == "stock":
                pm_stocks_count += 1
            elif position_type == "option":
                pm_options_count += 1
            
            print(f"\n   Position #{i+1}:")
            print(f"     - Symbol: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Market Value: ${market_value:,.2f}" if isinstance(market_value, (int, float)) else f"     - Market Value: {market_value}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:,.2f}" if isinstance(unrealized_pnl, (int, float)) else f"     - Unrealized P&L: {unrealized_pnl}")
            print(f"     - Type: {position_type}")
            
            # Check for mock data indicators
            if symbol in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN", "QQQ", "SPY"]:
                if quantity in [100, 200, 300, 500, 1000, 1200]:  # Common mock quantities
                    pm_mock_indicators.append(f"{symbol}: {quantity} shares (typical mock quantity)")
            
            # Check for round numbers that suggest mock data
            if isinstance(market_value, (int, float)) and market_value > 0:
                if market_value % 1000 == 0 or market_value % 500 == 0:  # Round thousands
                    pm_mock_indicators.append(f"{symbol}: ${market_value:,.2f} (round market value)")
        
        # Log key findings
        self.log_finding("PM_SERVICE", f"Portfolio Management Service shows ${pm_total_value:,.2f} total portfolio value", "INFO")
        self.log_finding("PM_SERVICE", f"Portfolio Management shows {len(positions)} total positions", "INFO")
        
        # Check for mock data indicators
        if pm_mock_indicators:
            self.log_finding("PM_SERVICE", f"Mock data indicators detected: {len(pm_mock_indicators)} issues", "WARNING")
            for indicator in pm_mock_indicators[:5]:  # Show first 5
                self.log_finding("PM_SERVICE", f"Mock indicator: {indicator}", "WARNING")
        else:
            self.log_finding("PM_SERVICE", "No obvious mock data indicators detected in Portfolio Management Service", "SUCCESS")
        
        # Check for user-reported fake symbols
        user_reported_symbols = ["AMZN", "QQQ", "GOOGL"]
        found_fake_symbols = [symbol for symbol in pm_position_symbols if symbol in user_reported_symbols]
        
        if found_fake_symbols:
            self.log_finding("PM_SERVICE", f"Found user-reported 'fake' symbols in Portfolio Management: {found_fake_symbols}", "CRITICAL")
        else:
            self.log_finding("PM_SERVICE", "User-reported 'fake' symbols not found in Portfolio Management Service", "INFO")
        
        return {
            "total_value": pm_total_value,
            "total_pnl": pm_total_pnl,
            "positions_count": len(positions),
            "position_symbols": pm_position_symbols,
            "mock_indicators": pm_mock_indicators
        }

    def compare_data_sources(self, ts_data, pm_data):
        """PHASE 4: Compare TradeStation Direct vs Portfolio Management Service"""
        print("\n" + "="*80)
        print("🔍 PHASE 4: DATA SOURCE COMPARISON")
        print("="*80)
        print("🎯 OBJECTIVE: Identify discrepancies between data sources")
        print("📋 COMPARING: TradeStation Direct API vs Portfolio Management Service")
        
        if not ts_data or not pm_data:
            self.log_finding("COMPARISON", "Cannot compare data sources - missing data", "CRITICAL")
            return
        
        # Compare portfolio values
        ts_value = ts_data["total_market_value"]
        pm_value = pm_data["total_value"]
        value_difference = ts_value - pm_value
        value_difference_percent = (value_difference / ts_value * 100) if ts_value > 0 else 0
        
        print(f"\n💰 PORTFOLIO VALUE COMPARISON:")
        print(f"   TradeStation Direct API: ${ts_value:,.2f}")
        print(f"   Portfolio Management:    ${pm_value:,.2f}")
        print(f"   Difference:              ${value_difference:,.2f} ({value_difference_percent:+.1f}%)")
        
        if abs(value_difference) > 1000:  # More than $1000 difference
            self.log_finding("COMPARISON", f"CRITICAL VALUE DISCREPANCY: ${value_difference:,.2f} difference ({value_difference_percent:+.1f}%)", "CRITICAL")
        elif abs(value_difference) > 100:  # More than $100 difference
            self.log_finding("COMPARISON", f"Significant value discrepancy: ${value_difference:,.2f} difference", "WARNING")
        else:
            self.log_finding("COMPARISON", f"Portfolio values are consistent (difference: ${value_difference:,.2f})", "SUCCESS")
        
        # Compare position counts
        ts_positions = ts_data["positions_count"]
        pm_positions = pm_data["positions_count"]
        position_difference = ts_positions - pm_positions
        
        print(f"\n📊 POSITION COUNT COMPARISON:")
        print(f"   TradeStation Direct API: {ts_positions} positions")
        print(f"   Portfolio Management:    {pm_positions} positions")
        print(f"   Difference:              {position_difference:+d} positions")
        
        if position_difference != 0:
            self.log_finding("COMPARISON", f"Position count mismatch: {position_difference:+d} positions difference", "WARNING")
        else:
            self.log_finding("COMPARISON", "Position counts match between data sources", "SUCCESS")
        
        # Compare symbols
        ts_symbols = set(ts_data["position_symbols"])
        pm_symbols = set(pm_data["position_symbols"])
        
        common_symbols = ts_symbols.intersection(pm_symbols)
        ts_only_symbols = ts_symbols - pm_symbols
        pm_only_symbols = pm_symbols - ts_symbols
        
        print(f"\n🔤 SYMBOL COMPARISON:")
        print(f"   Common symbols:     {len(common_symbols)}")
        print(f"   TradeStation only:  {len(ts_only_symbols)}")
        print(f"   Portfolio Mgmt only: {len(pm_only_symbols)}")
        
        if ts_only_symbols:
            print(f"   TradeStation exclusive: {list(ts_only_symbols)[:10]}")  # Show first 10
            self.log_finding("COMPARISON", f"TradeStation has {len(ts_only_symbols)} symbols not in Portfolio Management", "WARNING")
        
        if pm_only_symbols:
            print(f"   Portfolio Mgmt exclusive: {list(pm_only_symbols)[:10]}")  # Show first 10
            self.log_finding("COMPARISON", f"Portfolio Management has {len(pm_only_symbols)} symbols not in TradeStation", "WARNING")
        
        # Check for mock data patterns
        ts_suspicious = len(ts_data.get("suspicious_patterns", []))
        pm_suspicious = len(pm_data.get("mock_indicators", []))
        
        print(f"\n🚨 MOCK DATA ANALYSIS:")
        print(f"   TradeStation suspicious patterns: {ts_suspicious}")
        print(f"   Portfolio Mgmt mock indicators:   {pm_suspicious}")
        
        if pm_suspicious > ts_suspicious:
            self.log_finding("COMPARISON", f"Portfolio Management Service shows more mock data indicators ({pm_suspicious} vs {ts_suspicious})", "CRITICAL")
        elif ts_suspicious > pm_suspicious:
            self.log_finding("COMPARISON", f"TradeStation Direct API shows more suspicious patterns ({ts_suspicious} vs {pm_suspicious})", "WARNING")
        else:
            self.log_finding("COMPARISON", "Both data sources show similar levels of data authenticity", "INFO")

    def generate_investigation_report(self):
        """Generate final investigation report"""
        print("\n" + "="*80)
        print("📋 FINAL INVESTIGATION REPORT")
        print("="*80)
        print("🎯 CRITICAL ISSUE: User reports displayed positions are NOT their real TradeStation positions")
        
        # Summarize findings by category
        for category, findings in self.investigation_results.items():
            print(f"\n📊 {category} FINDINGS:")
            
            critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
            warning_count = sum(1 for f in findings if f["severity"] == "WARNING")
            success_count = sum(1 for f in findings if f["severity"] == "SUCCESS")
            
            print(f"   🚨 Critical Issues: {critical_count}")
            print(f"   ⚠️  Warnings: {warning_count}")
            print(f"   ✅ Successes: {success_count}")
            
            # Show critical findings
            for finding in findings:
                if finding["severity"] == "CRITICAL":
                    print(f"   🚨 {finding['finding']}")
        
        # Generate recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        
        # Check if we found the critical discrepancy
        value_discrepancy_found = any(
            "VALUE DISCREPANCY" in finding["finding"] 
            for findings in self.investigation_results.values() 
            for finding in findings
        )
        
        if value_discrepancy_found:
            print("   1. 🚨 URGENT: Fix Portfolio Management Service to use real TradeStation data")
            print("   2. 🔍 Investigate why Portfolio Management Service shows different values")
            print("   3. 📊 Implement data validation between TradeStation API and Portfolio Management")
            print("   4. 🔄 Add real-time synchronization between data sources")
        
        # Check for mock data indicators
        mock_data_found = any(
            "mock" in finding["finding"].lower() or "fake" in finding["finding"].lower()
            for findings in self.investigation_results.values() 
            for finding in findings
            if finding["severity"] in ["CRITICAL", "WARNING"]
        )
        
        if mock_data_found:
            print("   5. 🎭 Remove or replace mock data with real TradeStation integration")
            print("   6. 🔒 Ensure Portfolio Management Service uses authenticated TradeStation data")
        
        print("   7. 🧪 Add automated tests to detect data source discrepancies")
        print("   8. 📱 Update frontend to display data source information to users")
        
        # Final verdict
        critical_issues = sum(
            sum(1 for f in findings if f["severity"] == "CRITICAL")
            for findings in self.investigation_results.values()
        )
        
        if critical_issues > 0:
            print(f"\n🚨 VERDICT: CRITICAL ISSUES FOUND ({critical_issues} critical issues)")
            print("   The user's concern about fake/mock positions appears to be VALID.")
            print("   Immediate action required to fix data source discrepancies.")
        else:
            print(f"\n✅ VERDICT: NO CRITICAL ISSUES FOUND")
            print("   Data sources appear to be consistent. User issue may be elsewhere.")

def main():
    """Run the TradeStation portfolio investigation"""
    print("🔍 TRADESTATION PORTFOLIO DATA INVESTIGATION")
    print("=" * 80)
    print("🚨 CRITICAL ISSUE: User reports displayed positions are NOT real")
    print("📋 INVESTIGATING: Data source discrepancies and mock data usage")
    print("⏰ Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    investigator = TradeStationPortfolioInvestigator()
    
    try:
        # Phase 1: Investigate TradeStation accounts
        target_account_id = investigator.investigate_tradestation_accounts()
        
        if not target_account_id:
            print("\n❌ INVESTIGATION FAILED: Cannot proceed without valid TradeStation account")
            return
        
        # Phase 2: Investigate TradeStation positions
        ts_data = investigator.investigate_tradestation_positions(target_account_id)
        
        # Phase 3: Investigate Portfolio Management Service
        pm_data = investigator.investigate_portfolio_management_service()
        
        # Phase 4: Compare data sources
        if ts_data and pm_data:
            investigator.compare_data_sources(ts_data, pm_data)
        
        # Generate final report
        investigator.generate_investigation_report()
        
    except Exception as e:
        print(f"\n❌ INVESTIGATION ERROR: {str(e)}")
        investigator.log_finding("SYSTEM", f"Investigation failed with error: {str(e)}", "CRITICAL")
    
    print(f"\n⏰ Completed:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()