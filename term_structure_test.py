"""
Term Structure Volatility Arbitrage Module - Integration Test

Tests all backend endpoints and validates functionality:
- Earnings calendar scanning
- Forward vol factor calculation
- ML IV crush predictions
- Backtest engine
- Module supervision
- Position tracking

Author: FlowMind AI Team
Date: October 15, 2025
"""

import os
import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8000")

def print_header(title):
 """Print formatted test header"""
 print("\n" + "=" * 80)
 print(f" {title}")
 print("=" * 80)

def print_success(message):
 """Print success message"""
 print(f" {message}")

def print_error(message):
 """Print error message"""
 print(f" {message}")

def print_info(message):
 """Print info message"""
 print(f" {message}")

def test_health_check():
 """Test 1: Health check endpoint"""
 print_header("TEST 1: Health Check")
 
 try:
 response = requests.get(f"{BACKEND_URL}/api/term-structure/health")
 data = response.json()
 
 if response.status_code == 200:
 print_success(f"Health check passed: {data['status']}")
 print_info(f"Service: {data.get('service', 'N/A')}")
 print_info(f"Components: {json.dumps(data.get('components', {}), indent=2)}")
 return True
 else:
 print_error(f"Health check failed: {response.status_code}")
 return False
 
 except Exception as e:
 print_error(f"Health check exception: {e}")
 return False

def test_scan_earnings_calendar():
 """Test 2: Scan earnings calendar"""
 print_header("TEST 2: Scan Earnings Calendar")
 
 try:
 response = requests.get(
 f"{BACKEND_URL}/api/term-structure/scan",
 params={"days_ahead": 30, "min_fwd_vol_factor": 1.3}
 )
 data = response.json()
 
 if response.status_code == 200 and data.get("status") == "success":
 opportunities = data["data"]["opportunities"]
 print_success(f"Scan completed: {len(opportunities)} opportunities found")
 
 if opportunities:
 print_info(f"Total scanned: {data['data']['total_scanned']}")
 print_info(f"Filtered: {data['data']['total_filtered']}")
 
 # Show top 3 opportunities
 print("\n Top 3 Opportunities:")
 for i, opp in enumerate(opportunities[:3], 1):
 print(f"\n {i}. {opp['symbol']} - {opp['company_name']}")
 print(f" • Fwd Vol Factor: {opp['forward_vol_factor']:.2f}x")
 print(f" • Opportunity Score: {opp['opportunity_score']:.0f}/100")
 print(f" • Days to Earnings: {opp['days_to_earnings']}")
 print(f" • Expected ROI: {opp['expected_roi']:.0f}%")
 print(f" • Backtest Win Rate: {opp['backtest']['win_rate']*100:.0f}%")
 print(f" • Risk Rating: {opp['risk_rating']}")
 
 return True
 else:
 print_error(f"Scan failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"Scan exception: {e}")
 return False

def test_get_opportunities():
 """Test 3: Get top opportunities"""
 print_header("TEST 3: Get Top Opportunities")
 
 try:
 response = requests.get(
 f"{BACKEND_URL}/api/term-structure/opportunities",
 params={"limit": 10, "min_backtest_win_rate": 0.65}
 )
 data = response.json()
 
 if response.status_code == 200 and data.get("status") == "success":
 opportunities = data["data"]["opportunities"]
 print_success(f"Retrieved {len(opportunities)} top opportunities")
 
 if opportunities:
 # Show detailed view of #1 opportunity
 top = opportunities[0]
 print(f"\n🥇 #1 Opportunity: {top['symbol']}")
 print(f" Company: {top['company_name']}")
 print(f" Sector: {top.get('sector', 'N/A')}")
 print(f" Current Price: ${top['current_price']:.2f}")
 print(f" Earnings Date: {top['earnings_date']}")
 print(f" Days to Earnings: {top['days_to_earnings']}")
 print(f"\n Forward Vol Factor: {top['forward_vol_factor']:.2f}x")
 print(f" Opportunity Score: {top['opportunity_score']:.0f}/100")
 print(f"\n ATM Strike: ${top['atm_strike']:.0f}")
 print(f" Front Month: {top['front_month']['expiration']} ({top['front_month']['dte']} DTE)")
 print(f" Front IV: {top['front_month']['iv']*100:.0f}%")
 print(f" Back Month: {top['back_month']['expiration']} ({top['back_month']['dte']} DTE)")
 print(f" Back IV: {top['back_month']['iv']*100:.0f}%")
 print(f"\n Spread Cost: ${top['spread_cost']:.2f}")
 print(f" Expected Profit: ${top['expected_profit']:.2f}")
 print(f" Expected ROI: {top['expected_roi']:.0f}%")
 print(f"\n IV Crush (Historical): {top['iv_crush']['historical_avg']*100:.0f}%")
 print(f" IV Crush (ML): {top['iv_crush']['ml_predicted']*100:.0f}% (confidence: {top['iv_crush']['confidence']*100:.0f}%)")
 print(f"\n Backtest:")
 print(f" • Trades: {top['backtest']['trades']}")
 print(f" • Win Rate: {top['backtest']['win_rate']*100:.0f}%")
 print(f" • Avg Profit: ${top['backtest']['avg_profit']:.2f}")
 print(f" • Max Drawdown: ${top['backtest']['max_drawdown']:.2f}")
 print(f" • Sharpe Ratio: {top['backtest']['sharpe_ratio']:.2f}")
 print(f"\n Risk Rating: {top['risk_rating']}")
 print(f" Position Size Recommendation: {top['trade_recommendation']['position_size']} contracts")
 
 return True
 else:
 print_error(f"Get opportunities failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"Get opportunities exception: {e}")
 return False

def test_backtest_symbol():
 """Test 4: Backtest specific symbol"""
 print_header("TEST 4: Backtest Symbol (TSLA)")
 
 try:
 response = requests.get(
 f"{BACKEND_URL}/api/term-structure/backtest/TSLA",
 params={"lookback_quarters": 8, "position_size": 1}
 )
 data = response.json()
 
 if response.status_code == 200 and data.get("status") == "success":
 results = data["data"]["backtest_results"]
 print_success("Backtest completed for TSLA")
 
 print(f"\n Backtest Results (Last {results.get('lookback_quarters', 8)} Quarters):")
 print(f" Total Trades: {results['trades']}")
 print(f" Wins: {results['wins']} | Losses: {results['losses']}")
 print(f" Win Rate: {results['win_rate']*100:.1f}%")
 print(f"\n Total Profit: ${results['total_profit']:.2f}")
 print(f" Avg Profit: ${results['avg_profit']:.2f}")
 print(f" Avg Loss: ${results['avg_loss']:.2f}")
 print(f" Best Trade: ${results['best_trade']:.2f}")
 print(f" Worst Trade: ${results['worst_trade']:.2f}")
 print(f"\n Max Drawdown: ${results['max_drawdown']:.2f}")
 print(f" Sharpe Ratio: {results['sharpe_ratio']:.2f}")
 print(f" Profit Factor: {results['profit_factor']:.2f}")
 print(f" Avg IV Crush: {results['avg_iv_crush']*100:.0f}%")
 
 return True
 else:
 print_error(f"Backtest failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"Backtest exception: {e}")
 return False

def test_ml_prediction():
 """Test 5: ML IV crush prediction"""
 print_header("TEST 5: ML IV Crush Prediction (NVDA)")
 
 try:
 response = requests.get(
 f"{BACKEND_URL}/api/term-structure/ml-prediction/NVDA",
 params={
 "current_iv": 0.88,
 "sector": "Technology",
 "market_cap": 1100000000000,
 "iv_rank": 75
 }
 )
 data = response.json()
 
 if response.status_code == 200 and data.get("status") == "success":
 prediction = data["data"]
 print_success("ML prediction completed for NVDA")
 
 print(f"\n🤖 ML Prediction:")
 print(f" Symbol: {prediction['symbol']}")
 print(f" Predicted IV Crush: {prediction['prediction']*100:.0f}%")
 print(f" Confidence: {prediction['confidence']*100:.0f}%")
 print(f"\n Historical Range:")
 print(f" • Min: {prediction['historical_range']['min']*100:.0f}%")
 print(f" • Avg: {prediction['historical_range']['avg']*100:.0f}%")
 print(f" • Max: {prediction['historical_range']['max']*100:.0f}%")
 print(f"\n Explanation: {prediction['explanation']}")
 print(f" Model Version: {prediction['model_version']}")
 
 return True
 else:
 print_error(f"ML prediction failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"ML prediction exception: {e}")
 return False

def test_module_stats():
 """Test 6: Get module stats"""
 print_header("TEST 6: Module Stats")
 
 try:
 mindfolio_id = "demo_mindfolio_001"
 response = requests.get(
 f"{BACKEND_URL}/api/term-structure/module-stats/{mindfolio_id}"
 )
 data = response.json()
 
 if response.status_code == 200 and data.get("status") == "success":
 if data["data"].get("module_active"):
 stats = data["data"]
 print_success(f"Module stats retrieved for {mindfolio_id}")
 
 print(f"\n Module Statistics:")
 print(f" Status: {stats['status']}")
 print(f" Budget: ${stats['budget']:,.2f}")
 print(f" Budget Used: ${stats['budget_used']:,.2f}")
 print(f" Budget Available: ${stats['budget_available']:,.2f}")
 print(f" Utilization: {stats['budget_utilization_pct']:.1f}%")
 print(f"\n Daily P&L: ${stats['daily_pnl']:,.2f}")
 print(f" Total P&L: ${stats['total_pnl']:,.2f} ({stats['total_pnl_pct']:.2f}%)")
 print(f"\n Positions: {stats['positions_count']}")
 print(f" Total Trades: {stats['trades_count']}")
 print(f"\n Max Risk per Trade: ${stats['max_risk_per_trade']:,.2f}")
 print(f" Daily Loss Limit: ${stats['daily_loss_limit']:,.2f}")
 print(f" Autotrade: {stats['autotrade']}")
 else:
 print_info("No active module for this mindfolio")
 
 return True
 else:
 print_error(f"Module stats failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"Module stats exception: {e}")
 return False

def test_execute_trade_validation():
 """Test 7: Execute trade (validation only)"""
 print_header("TEST 7: Trade Execution Validation")
 
 try:
 response = requests.post(
 f"{BACKEND_URL}/api/term-structure/execute",
 json={
 "mindfolio_id": "demo_mindfolio_001",
 "symbol": "TSLA",
 "strike": 250,
 "front_expiration": "2025-10-25",
 "back_expiration": "2025-11-15",
 "position_size": 1,
 "auto_execute": False
 }
 )
 data = response.json()
 
 if response.status_code == 200:
 print_success(f"Trade validation: {data['status']}")
 
 if data['status'] == 'pending_approval':
 print_info(f"Symbol: {data['symbol']}")
 print_info(f"Strike: ${data['strike']}")
 print_info(f"Position Size: {data['position_size']}")
 print_info(f"Validation: {data['validation']['reason']}")
 if data['validation'].get('warnings'):
 print_info(f"Warnings: {', '.join(data['validation']['warnings'])}")
 
 return True
 else:
 print_error(f"Trade validation failed: {data.get('detail', 'Unknown error')}")
 return False
 
 except Exception as e:
 print_error(f"Trade validation exception: {e}")
 return False

def run_all_tests():
 """Run all tests"""
 print("\n")
 print("╔" + "=" * 78 + "╗")
 print("║" + " " * 15 + "TERM STRUCTURE MODULE - INTEGRATION TEST" + " " * 22 + "║")
 print("╚" + "=" * 78 + "╝")
 print(f"\nBackend URL: {BACKEND_URL}")
 print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 
 results = []
 
 # Run all tests
 results.append(("Health Check", test_health_check()))
 results.append(("Scan Earnings Calendar", test_scan_earnings_calendar()))
 results.append(("Get Top Opportunities", test_get_opportunities()))
 results.append(("Backtest Symbol", test_backtest_symbol()))
 results.append(("ML IV Crush Prediction", test_ml_prediction()))
 results.append(("Module Stats", test_module_stats()))
 results.append(("Trade Execution Validation", test_execute_trade_validation()))
 
 # Summary
 print_header("TEST SUMMARY")
 
 passed = sum(1 for _, result in results if result)
 total = len(results)
 
 for test_name, result in results:
 status = " PASS" if result else " FAIL"
 print(f"{status} - {test_name}")
 
 print(f"\n{'=' * 80}")
 print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
 
 if passed == total:
 print("\n ALL TESTS PASSED! Term Structure module is operational! ")
 else:
 print(f"\n {total - passed} test(s) failed. Check backend logs.")
 
 print("=" * 80 + "\n")

if __name__ == "__main__":
 run_all_tests()
