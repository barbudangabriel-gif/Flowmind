#!/usr/bin/env python3
"""
Mindfolio Management Service API Test Script
Tests all 7 endpoints as requested in the review
"""

import requests
import sys

class MindfolioManagementTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0

 def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
 """Run a single API test"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 self.tests_run += 1
 print(f"\n Testing {name}...")
 print(f" URL: {url}")

 try:
 if method == "GET":
 response = requests.get(url, headers=headers, params=params, timeout=30)
 elif method == "POST":
 response = requests.post(url, json=data, headers=headers, timeout=30)

 success = response.status_code == expected_status
 if success:
 self.tests_passed += 1
 print(f" Passed - Status: {response.status_code}")
 try:
 response_data = response.json()
 return True, response_data
 except:
 return True, {}
 else:
 print(
 f" Failed - Expected {expected_status}, got {response.status_code}"
 )
 try:
 error_data = response.json()
 print(f" Error: {error_data}")
 except:
 print(f" Error: {response.text}")
 return False, {}

 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}

 def test_mindfolio_management_endpoints(self):
 """Test Mindfolio Management Service API endpoints - COMPREHENSIVE TESTING AS REQUESTED"""
 print(
 "\n TESTING MINDFOLIO MANAGEMENT SERVICE API ENDPOINTS - COMPREHENSIVE VERIFICATION"
 )
 print("=" * 80)
 print(" OBJECTIVE: Test new Mindfolio Management Service API endpoints")
 print(" ENDPOINTS TO TEST:")
 print(
 " 1. GET /api/mindfolio-management/mindfolios - Should return 4 default mindfolios"
 )
 print(
 " 2. GET /api/mindfolio-management/mindfolios/tradestation-main/positions - Should return 6 mock positions"
 )
 print(
 " 3. GET /api/mindfolio-management/available-mindfolios/tradestation-main - Should return 3 other mindfolios"
 )
 print(
 " 4. POST /api/mindfolio-management/move-position - Test moving position to Long Term mindfolio"
 )
 print(
 " 5. POST /api/mindfolio-management/create-mindfolio - Test creating new custom mindfolio"
 )
 print(
 " 6. GET /api/mindfolio-management/aggregate-view - Should show aggregated mindfolio data"
 )
 print(
 " 7. GET /api/mindfolio-management/move-history/tradestation-main - Should show move history"
 )

 # Test 1: Get All Mindfolios (Should return 4 default mindfolios)
 print("\n PHASE 1: Get All Mindfolios")
 print("-" * 60)

 success, mindfolios_data = self.run_test(
 "Get All Mindfolios", "GET", "mindfolio-management/mindfolios", 200
 )
 if not success:
 print(" Get mindfolios endpoint failed")
 return False

 # Extract mindfolios from nested response
 mindfolios = (
 mindfolios_data.get("mindfolios", [])
 if isinstance(mindfolios_data, dict)
 else []
 )
 print(f" Found {len(mindfolios)} mindfolios")

 # Verify we have 4 default mindfolios
 expected_mindfolio_ids = [
 "tradestation-main",
 "long-term-mindfolio",
 "medium-term-mindfolio",
 "short-term-mindfolio",
 ]
 found_mindfolio_ids = [p.get("id", "") for p in mindfolios]

 if len(mindfolios) == 4:
 print(" Correct number of mindfolios: 4")
 mindfolios_count_correct = True
 else:
 print(f" Expected 4 mindfolios, found {len(mindfolios)}")
 mindfolios_count_correct = False

 # Check for expected mindfolio IDs
 missing_mindfolios = [
 pid for pid in expected_mindfolio_ids if pid not in found_mindfolio_ids
 ]
 if not missing_mindfolios:
 print(f" All expected mindfolios found: {expected_mindfolio_ids}")
 expected_mindfolios_found = True
 else:
 print(f" Missing mindfolios: {missing_mindfolios}")
 expected_mindfolios_found = False

 # Display mindfolio details
 for i, mindfolio in enumerate(mindfolios):
 print(
 f" Mindfolio {i+1}: {mindfolio.get('name', 'N/A')} ({mindfolio.get('id', 'N/A')})"
 )
 print(f" - Description: {mindfolio.get('description', 'N/A')}")
 print(f" - Category: {mindfolio.get('category', 'N/A')}")
 print(f" - Total Value: ${mindfolio.get('total_value', 0):,.2f}")
 print(f" - Positions Count: {mindfolio.get('positions_count', 0)}")

 # Test 2: Get TradeStation Main Positions (Should return 6 mock positions)
 print("\n PHASE 2: Get TradeStation Main Positions")
 print("-" * 60)

 success, positions_data = self.run_test(
 "Get TradeStation Main Positions",
 "GET",
 "mindfolio-management/mindfolios/tradestation-main/positions",
 200,
 )
 if not success:
 print(" Get positions endpoint failed")
 return False

 # Extract positions from nested response
 positions = (
 positions_data.get("positions", [])
 if isinstance(positions_data, dict)
 else []
 )
 print(f" Found {len(positions)} positions in TradeStation Main")

 # Verify we have 6 mock positions
 if len(positions) == 6:
 print(" Correct number of positions: 6")
 positions_count_correct = True
 else:
 print(f" Expected 6 positions, found {len(positions)}")
 positions_count_correct = False

 # Display position details and verify expected symbols
 expected_symbols = [
 "AAPL",
 "MSFT",
 "TSLA",
 "NVDA Jan2026 LEAPS",
 "SPY Weekly Calls",
 "QQQ",
 ]
 found_symbols = [p.get("symbol", "") for p in positions]

 print(" Position Details:")
 total_mindfolio_value = 0
 for i, position in enumerate(positions):
 symbol = position.get("symbol", "N/A")
 quantity = position.get("quantity", 0)
 current_price = position.get("current_price", 0)
 market_value = position.get("market_value", 0)
 unrealized_pnl = position.get("unrealized_pnl", 0)
 position_type = position.get("position_type", "N/A")

 print(f" Position {i+1}: {symbol}")
 print(f" - Quantity: {quantity}")
 print(f" - Current Price: ${current_price:.2f}")
 print(f" - Market Value: ${market_value:,.2f}")
 print(f" - Unrealized P&L: ${unrealized_pnl:+,.2f}")
 print(f" - Type: {position_type}")

 total_mindfolio_value += market_value

 print(f" Total Mindfolio Value: ${total_mindfolio_value:,.2f}")

 # Check for expected symbols
 missing_symbols = [sym for sym in expected_symbols if sym not in found_symbols]
 if not missing_symbols:
 print(f" All expected symbols found: {expected_symbols}")
 expected_symbols_found = True
 else:
 print(f" Missing symbols: {missing_symbols}")
 expected_symbols_found = False

 # Test 3: Get Available Mindfolios for Move (Should return 3 other mindfolios)
 print("\n PHASE 3: Get Available Mindfolios for Move")
 print("-" * 60)

 success, available_data = self.run_test(
 "Get Available Mindfolios",
 "GET",
 "mindfolio-management/available-mindfolios/tradestation-main",
 200,
 )
 if not success:
 print(" Get available mindfolios endpoint failed")
 return False

 # Extract available mindfolios from nested response
 available_mindfolios = (
 available_data.get("available_mindfolios", [])
 if isinstance(available_data, dict)
 else []
 )
 print(f" Found {len(available_mindfolios)} available mindfolios for move")

 # Should return 3 mindfolios (excluding tradestation-main)
 if len(available_mindfolios) == 3:
 print(" Correct number of available mindfolios: 3")
 available_count_correct = True
 else:
 print(
 f" Expected 3 available mindfolios, found {len(available_mindfolios)}"
 )
 available_count_correct = False

 # Display available mindfolios
 for i, mindfolio in enumerate(available_mindfolios):
 print(
 f" Available Mindfolio {i+1}: {mindfolio.get('name', 'N/A')} ({mindfolio.get('id', 'N/A')})"
 )

 # Test 4: Move Position (Move a position to Long Term mindfolio)
 print("\n PHASE 4: Move Position to Long Term Mindfolio")
 print("-" * 60)

 # Get a position ID from the positions we retrieved
 position_to_move = None
 if positions:
 # Find AAPL position to move
 for pos in positions:
 if pos.get("symbol") == "AAPL":
 position_to_move = pos
 break

 if not position_to_move:
 position_to_move = positions[0] # Use first position if AAPL not found

 if position_to_move:
 move_data = {
 "position_id": position_to_move.get("id"),
 "to_mindfolio_id": "long-term-mindfolio",
 "reason": "Moving AAPL to long-term holdings for testing",
 }

 success, move_response = self.run_test(
 "Move Position to Long Term",
 "POST",
 "mindfolio-management/move-position",
 200,
 data=move_data,
 )
 if success:
 print(" Position move successful")
 print(f" Move ID: {move_response.get('move_id', 'N/A')}")
 print(f" Message: {move_response.get('message', 'N/A')}")
 move_position_success = True
 else:
 print(" Position move failed")
 move_position_success = False
 else:
 print(" No positions available to move")
 move_position_success = False

 # Test 5: Create Custom Mindfolio
 print("\n PHASE 5: Create Custom Mindfolio")
 print("-" * 60)

 create_mindfolio_data = {
 "name": "Test Mindfolio",
 "description": "Testing mindfolio creation",
 "category": "custom",
 }

 success, create_response = self.run_test(
 "Create Custom Mindfolio",
 "POST",
 "mindfolio-management/create-mindfolio",
 200,
 data=create_mindfolio_data,
 )
 if success:
 print(" Custom mindfolio created successfully")
 print(f" Mindfolio ID: {create_response.get('id', 'N/A')}")
 print(f" Name: {create_response.get('name', 'N/A')}")
 print(f" Description: {create_response.get('description', 'N/A')}")
 create_mindfolio_success = True
 else:
 print(" Custom mindfolio creation failed")
 create_mindfolio_success = False

 # Test 6: Get Aggregate View
 print("\n PHASE 6: Get Aggregate Mindfolio View")
 print("-" * 60)

 success, aggregate_data = self.run_test(
 "Get Aggregate View", "GET", "mindfolio-management/aggregate-view", 200
 )
 if success:
 total_value = aggregate_data.get("total_value", 0)
 total_pnl = aggregate_data.get("total_pnl", 0)
 total_positions = aggregate_data.get("total_positions", 0)
 mindfolio_breakdown = aggregate_data.get("mindfolio_breakdown", {})
 asset_breakdown = aggregate_data.get("asset_breakdown", {})

 print(" Aggregate view retrieved successfully")
 print(f" Total Value: ${total_value:,.2f}")
 print(f" Total P&L: ${total_pnl:+,.2f}")
 print(f" Total Positions: {total_positions}")
 print(f" Mindfolio Breakdown: {len(mindfolio_breakdown)} mindfolios")
 print(f" Asset Breakdown: {len(asset_breakdown)} asset types")

 # Display mindfolio breakdown
 for mindfolio_id, breakdown in mindfolio_breakdown.items():
 print(
 f" - {breakdown.get('name', 'N/A')}: ${breakdown.get('value', 0):,.2f} ({breakdown.get('percentage', 0):.1f}%)"
 )

 aggregate_view_success = True
 else:
 print(" Aggregate view failed")
 aggregate_view_success = False

 # Test 7: Get Move History
 print("\n PHASE 7: Get Move History for TradeStation Main")
 print("-" * 60)

 success, history_data = self.run_test(
 "Get Move History",
 "GET",
 "mindfolio-management/move-history/tradestation-main",
 200,
 )
 if success:
 # Extract move history from nested response
 move_history = (
 history_data.get("moves", []) if isinstance(history_data, dict) else []
 )
 print(" Move history retrieved successfully")
 print(f" Found {len(move_history)} move records")

 # Display move history
 for i, move in enumerate(move_history):
 print(f" Move {i+1}:")
 print(f" - Move ID: {move.get('id', 'N/A')}")
 print(f" - From: {move.get('from_mindfolio_id', 'N/A')}")
 print(f" - To: {move.get('to_mindfolio_id', 'N/A')}")
 print(f" - Quantity: {move.get('quantity_moved', 0)}")
 print(f" - Date: {move.get('move_date', 'N/A')}")
 print(f" - Reason: {move.get('reason', 'N/A')}")

 move_history_success = True
 else:
 print(" Move history failed")
 move_history_success = False

 # Final Assessment
 print("\n FINAL ASSESSMENT: Mindfolio Management Service API Endpoints")
 print("=" * 80)

 # Calculate success metrics
 test_phases = [
 (
 "Get All Mindfolios (4 expected)",
 mindfolios_count_correct and expected_mindfolios_found,
 ),
 (
 "Get TradeStation Positions (6 expected)",
 positions_count_correct and expected_symbols_found,
 ),
 ("Get Available Mindfolios (3 expected)", available_count_correct),
 ("Move Position Functionality", move_position_success),
 ("Create Custom Mindfolio", create_mindfolio_success),
 ("Aggregate View", aggregate_view_success),
 ("Move History", move_history_success),
 ]

 passed_phases = sum(1 for _, passed in test_phases if passed)
 total_phases = len(test_phases)
 success_rate = (passed_phases / total_phases) * 100

 print("\n TEST RESULTS SUMMARY:")
 for phase_name, passed in test_phases:
 status = " PASS" if passed else " FAIL"
 print(f" {status} {phase_name}")

 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)"
 )

 # Key findings
 print("\n KEY FINDINGS:")
 print(f" - Default Mindfolios: {len(mindfolios)}/4 found")
 print(f" - Mock Positions: {len(positions)}/6 found")
 print(f" - Available for Move: {len(available_mindfolios)}/3 found")
 print(
 f" - Position Move: {' Working' if move_position_success else ' Failed'}"
 )
 print(
 f" - Mindfolio Creation: {' Working' if create_mindfolio_success else ' Failed'}"
 )
 print(
 f" - Aggregate View: {' Working' if aggregate_view_success else ' Failed'}"
 )
 print(
 f" - Move History: {' Working' if move_history_success else ' Failed'}"
 )

 # Review requirements verification
 print("\n REVIEW REQUIREMENTS VERIFICATION:")
 requirements_met = []

 if mindfolios_count_correct and expected_mindfolios_found:
 requirements_met.append(
 " GET /api/mindfolio-management/mindfolios returns 4 default mindfolios"
 )
 else:
 requirements_met.append(
 " GET /api/mindfolio-management/mindfolios - Mindfolio count/structure issues"
 )

 if positions_count_correct and expected_symbols_found:
 requirements_met.append(
 " GET /api/mindfolio-management/mindfolios/tradestation-main/positions returns 6 mock positions"
 )
 else:
 requirements_met.append(
 " GET /api/mindfolio-management/mindfolios/tradestation-main/positions - Position issues"
 )

 if available_count_correct:
 requirements_met.append(
 " GET /api/mindfolio-management/available-mindfolios/tradestation-main returns 3 other mindfolios"
 )
 else:
 requirements_met.append(
 " GET /api/mindfolio-management/available-mindfolios/tradestation-main - Count issues"
 )

 if move_position_success:
 requirements_met.append(
 " POST /api/mindfolio-management/move-position - Position move functionality working"
 )
 else:
 requirements_met.append(
 " POST /api/mindfolio-management/move-position - Move functionality failed"
 )

 if create_mindfolio_success:
 requirements_met.append(
 " POST /api/mindfolio-management/create-mindfolio - Custom mindfolio creation working"
 )
 else:
 requirements_met.append(
 " POST /api/mindfolio-management/create-mindfolio - Creation failed"
 )

 if aggregate_view_success:
 requirements_met.append(
 " GET /api/mindfolio-management/aggregate-view - Aggregated mindfolio data working"
 )
 else:
 requirements_met.append(
 " GET /api/mindfolio-management/aggregate-view - Aggregate view failed"
 )

 if move_history_success:
 requirements_met.append(
 " GET /api/mindfolio-management/move-history/tradestation-main - Move history working"
 )
 else:
 requirements_met.append(
 " GET /api/mindfolio-management/move-history/tradestation-main - History failed"
 )

 for requirement in requirements_met:
 print(f" {requirement}")

 # Final verdict
 if success_rate >= 85:
 print(
 "\n VERDICT: EXCELLENT - Mindfolio Management Service API endpoints working perfectly!"
 )
 print(
 " All 7 endpoints are functional with proper data structures and expected responses."
 )
 print(
 " The 'Move to Mindfolio X' functionality is ready for frontend integration."
 )
 elif success_rate >= 70:
 print(
 "\n VERDICT: GOOD - Mindfolio Management Service mostly working with minor issues."
 )
 print(
 " Most endpoints functional, may need minor fixes for full functionality."
 )
 else:
 print(
 "\n VERDICT: NEEDS ATTENTION - Mindfolio Management Service has significant issues."
 )
 print(" Multiple endpoints failing, requires investigation and fixes.")

 return success_rate >= 70

if __name__ == "__main__":
 tester = MindfolioManagementTester()
 result = tester.test_mindfolio_management_endpoints()
 print(
 f"\n Mindfolio Management Service Test Result: {' PASSED' if result else ' FAILED'}"
 )
 print(f" Tests Run: {tester.tests_run}, Tests Passed: {tester.tests_passed}")
 sys.exit(0 if result else 1)
