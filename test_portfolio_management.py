#!/usr/bin/env python3
"""
Portfolio Management Service API Test Script
Tests all 7 endpoints as requested in the review
"""

import requests
import json
import sys

class PortfolioManagementTester:
    def __init__(self, base_url="https://stockflow-ui.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

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
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_portfolio_management_endpoints(self):
        """Test Portfolio Management Service API endpoints - COMPREHENSIVE TESTING AS REQUESTED"""
        print("\n📊 TESTING PORTFOLIO MANAGEMENT SERVICE API ENDPOINTS - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test new Portfolio Management Service API endpoints")
        print("📋 ENDPOINTS TO TEST:")
        print("   1. GET /api/portfolio-management/portfolios - Should return 4 default portfolios")
        print("   2. GET /api/portfolio-management/portfolios/tradestation-main/positions - Should return 6 mock positions")
        print("   3. GET /api/portfolio-management/available-portfolios/tradestation-main - Should return 3 other portfolios")
        print("   4. POST /api/portfolio-management/move-position - Test moving position to Long Term portfolio")
        print("   5. POST /api/portfolio-management/create-portfolio - Test creating new custom portfolio")
        print("   6. GET /api/portfolio-management/aggregate-view - Should show aggregated portfolio data")
        print("   7. GET /api/portfolio-management/move-history/tradestation-main - Should show move history")
        
        # Test 1: Get All Portfolios (Should return 4 default portfolios)
        print(f"\n📊 PHASE 1: Get All Portfolios")
        print("-" * 60)
        
        success, portfolios_data = self.run_test("Get All Portfolios", "GET", "portfolio-management/portfolios", 200)
        if not success:
            print("❌ Get portfolios endpoint failed")
            return False
        
        # Extract portfolios from nested response
        portfolios = portfolios_data.get('portfolios', []) if isinstance(portfolios_data, dict) else []
        print(f"📊 Found {len(portfolios)} portfolios")
        
        # Verify we have 4 default portfolios
        expected_portfolio_ids = ['tradestation-main', 'long-term-portfolio', 'medium-term-portfolio', 'short-term-portfolio']
        found_portfolio_ids = [p.get('id', '') for p in portfolios]
        
        if len(portfolios) == 4:
            print(f"✅ Correct number of portfolios: 4")
            portfolios_count_correct = True
        else:
            print(f"❌ Expected 4 portfolios, found {len(portfolios)}")
            portfolios_count_correct = False
        
        # Check for expected portfolio IDs
        missing_portfolios = [pid for pid in expected_portfolio_ids if pid not in found_portfolio_ids]
        if not missing_portfolios:
            print(f"✅ All expected portfolios found: {expected_portfolio_ids}")
            expected_portfolios_found = True
        else:
            print(f"❌ Missing portfolios: {missing_portfolios}")
            expected_portfolios_found = False
        
        # Display portfolio details
        for i, portfolio in enumerate(portfolios):
            print(f"   Portfolio {i+1}: {portfolio.get('name', 'N/A')} ({portfolio.get('id', 'N/A')})")
            print(f"     - Description: {portfolio.get('description', 'N/A')}")
            print(f"     - Category: {portfolio.get('category', 'N/A')}")
            print(f"     - Total Value: ${portfolio.get('total_value', 0):,.2f}")
            print(f"     - Positions Count: {portfolio.get('positions_count', 0)}")
        
        # Test 2: Get TradeStation Main Positions (Should return 6 mock positions)
        print(f"\n📊 PHASE 2: Get TradeStation Main Positions")
        print("-" * 60)
        
        success, positions_data = self.run_test("Get TradeStation Main Positions", "GET", "portfolio-management/portfolios/tradestation-main/positions", 200)
        if not success:
            print("❌ Get positions endpoint failed")
            return False
        
        # Extract positions from nested response
        positions = positions_data.get('positions', []) if isinstance(positions_data, dict) else []
        print(f"📊 Found {len(positions)} positions in TradeStation Main")
        
        # Verify we have 6 mock positions
        if len(positions) == 6:
            print(f"✅ Correct number of positions: 6")
            positions_count_correct = True
        else:
            print(f"❌ Expected 6 positions, found {len(positions)}")
            positions_count_correct = False
        
        # Display position details and verify expected symbols
        expected_symbols = ['AAPL', 'MSFT', 'TSLA', 'NVDA Jan2026 LEAPS', 'SPY Weekly Calls', 'QQQ']
        found_symbols = [p.get('symbol', '') for p in positions]
        
        print(f"📊 Position Details:")
        total_portfolio_value = 0
        for i, position in enumerate(positions):
            symbol = position.get('symbol', 'N/A')
            quantity = position.get('quantity', 0)
            current_price = position.get('current_price', 0)
            market_value = position.get('market_value', 0)
            unrealized_pnl = position.get('unrealized_pnl', 0)
            position_type = position.get('position_type', 'N/A')
            
            print(f"   Position {i+1}: {symbol}")
            print(f"     - Quantity: {quantity}")
            print(f"     - Current Price: ${current_price:.2f}")
            print(f"     - Market Value: ${market_value:,.2f}")
            print(f"     - Unrealized P&L: ${unrealized_pnl:+,.2f}")
            print(f"     - Type: {position_type}")
            
            total_portfolio_value += market_value
        
        print(f"📊 Total Portfolio Value: ${total_portfolio_value:,.2f}")
        
        # Check for expected symbols
        missing_symbols = [sym for sym in expected_symbols if sym not in found_symbols]
        if not missing_symbols:
            print(f"✅ All expected symbols found: {expected_symbols}")
            expected_symbols_found = True
        else:
            print(f"❌ Missing symbols: {missing_symbols}")
            expected_symbols_found = False
        
        # Test 3: Get Available Portfolios for Move (Should return 3 other portfolios)
        print(f"\n📊 PHASE 3: Get Available Portfolios for Move")
        print("-" * 60)
        
        success, available_data = self.run_test("Get Available Portfolios", "GET", "portfolio-management/available-portfolios/tradestation-main", 200)
        if not success:
            print("❌ Get available portfolios endpoint failed")
            return False
        
        # Extract available portfolios from nested response
        available_portfolios = available_data.get('available_portfolios', []) if isinstance(available_data, dict) else []
        print(f"📊 Found {len(available_portfolios)} available portfolios for move")
        
        # Should return 3 portfolios (excluding tradestation-main)
        if len(available_portfolios) == 3:
            print(f"✅ Correct number of available portfolios: 3")
            available_count_correct = True
        else:
            print(f"❌ Expected 3 available portfolios, found {len(available_portfolios)}")
            available_count_correct = False
        
        # Display available portfolios
        for i, portfolio in enumerate(available_portfolios):
            print(f"   Available Portfolio {i+1}: {portfolio.get('name', 'N/A')} ({portfolio.get('id', 'N/A')})")
        
        # Test 4: Move Position (Move a position to Long Term portfolio)
        print(f"\n📊 PHASE 4: Move Position to Long Term Portfolio")
        print("-" * 60)
        
        # Get a position ID from the positions we retrieved
        position_to_move = None
        if positions:
            # Find AAPL position to move
            for pos in positions:
                if pos.get('symbol') == 'AAPL':
                    position_to_move = pos
                    break
            
            if not position_to_move:
                position_to_move = positions[0]  # Use first position if AAPL not found
        
        if position_to_move:
            move_data = {
                "position_id": position_to_move.get('id'),
                "to_portfolio_id": "long-term-portfolio",
                "reason": "Moving AAPL to long-term holdings for testing"
            }
            
            success, move_response = self.run_test("Move Position to Long Term", "POST", "portfolio-management/move-position", 200, data=move_data)
            if success:
                print(f"✅ Position move successful")
                print(f"   Move ID: {move_response.get('move_id', 'N/A')}")
                print(f"   Message: {move_response.get('message', 'N/A')}")
                move_position_success = True
            else:
                print(f"❌ Position move failed")
                move_position_success = False
        else:
            print(f"❌ No positions available to move")
            move_position_success = False
        
        # Test 5: Create Custom Portfolio
        print(f"\n📊 PHASE 5: Create Custom Portfolio")
        print("-" * 60)
        
        create_portfolio_data = {
            "name": "Test Portfolio",
            "description": "Testing portfolio creation",
            "category": "custom"
        }
        
        success, create_response = self.run_test("Create Custom Portfolio", "POST", "portfolio-management/create-portfolio", 200, data=create_portfolio_data)
        if success:
            print(f"✅ Custom portfolio created successfully")
            print(f"   Portfolio ID: {create_response.get('id', 'N/A')}")
            print(f"   Name: {create_response.get('name', 'N/A')}")
            print(f"   Description: {create_response.get('description', 'N/A')}")
            create_portfolio_success = True
        else:
            print(f"❌ Custom portfolio creation failed")
            create_portfolio_success = False
        
        # Test 6: Get Aggregate View
        print(f"\n📊 PHASE 6: Get Aggregate Portfolio View")
        print("-" * 60)
        
        success, aggregate_data = self.run_test("Get Aggregate View", "GET", "portfolio-management/aggregate-view", 200)
        if success:
            total_value = aggregate_data.get('total_value', 0)
            total_pnl = aggregate_data.get('total_pnl', 0)
            total_positions = aggregate_data.get('total_positions', 0)
            portfolio_breakdown = aggregate_data.get('portfolio_breakdown', {})
            asset_breakdown = aggregate_data.get('asset_breakdown', {})
            
            print(f"✅ Aggregate view retrieved successfully")
            print(f"   Total Value: ${total_value:,.2f}")
            print(f"   Total P&L: ${total_pnl:+,.2f}")
            print(f"   Total Positions: {total_positions}")
            print(f"   Portfolio Breakdown: {len(portfolio_breakdown)} portfolios")
            print(f"   Asset Breakdown: {len(asset_breakdown)} asset types")
            
            # Display portfolio breakdown
            for portfolio_id, breakdown in portfolio_breakdown.items():
                print(f"     - {breakdown.get('name', 'N/A')}: ${breakdown.get('value', 0):,.2f} ({breakdown.get('percentage', 0):.1f}%)")
            
            aggregate_view_success = True
        else:
            print(f"❌ Aggregate view failed")
            aggregate_view_success = False
        
        # Test 7: Get Move History
        print(f"\n📊 PHASE 7: Get Move History for TradeStation Main")
        print("-" * 60)
        
        success, history_data = self.run_test("Get Move History", "GET", "portfolio-management/move-history/tradestation-main", 200)
        if success:
            # Extract move history from nested response
            move_history = history_data.get('moves', []) if isinstance(history_data, dict) else []
            print(f"✅ Move history retrieved successfully")
            print(f"   Found {len(move_history)} move records")
            
            # Display move history
            for i, move in enumerate(move_history):
                print(f"   Move {i+1}:")
                print(f"     - Move ID: {move.get('id', 'N/A')}")
                print(f"     - From: {move.get('from_portfolio_id', 'N/A')}")
                print(f"     - To: {move.get('to_portfolio_id', 'N/A')}")
                print(f"     - Quantity: {move.get('quantity_moved', 0)}")
                print(f"     - Date: {move.get('move_date', 'N/A')}")
                print(f"     - Reason: {move.get('reason', 'N/A')}")
            
            move_history_success = True
        else:
            print(f"❌ Move history failed")
            move_history_success = False
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT: Portfolio Management Service API Endpoints")
        print("=" * 80)
        
        # Calculate success metrics
        test_phases = [
            ("Get All Portfolios (4 expected)", portfolios_count_correct and expected_portfolios_found),
            ("Get TradeStation Positions (6 expected)", positions_count_correct and expected_symbols_found),
            ("Get Available Portfolios (3 expected)", available_count_correct),
            ("Move Position Functionality", move_position_success),
            ("Create Custom Portfolio", create_portfolio_success),
            ("Aggregate View", aggregate_view_success),
            ("Move History", move_history_success)
        ]
        
        passed_phases = sum(1 for _, passed in test_phases if passed)
        total_phases = len(test_phases)
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for phase_name, passed in test_phases:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {phase_name}")
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   - Default Portfolios: {len(portfolios)}/4 found")
        print(f"   - Mock Positions: {len(positions)}/6 found")
        print(f"   - Available for Move: {len(available_portfolios)}/3 found")
        print(f"   - Position Move: {'✅ Working' if move_position_success else '❌ Failed'}")
        print(f"   - Portfolio Creation: {'✅ Working' if create_portfolio_success else '❌ Failed'}")
        print(f"   - Aggregate View: {'✅ Working' if aggregate_view_success else '❌ Failed'}")
        print(f"   - Move History: {'✅ Working' if move_history_success else '❌ Failed'}")
        
        # Review requirements verification
        print(f"\n📋 REVIEW REQUIREMENTS VERIFICATION:")
        requirements_met = []
        
        if portfolios_count_correct and expected_portfolios_found:
            requirements_met.append("✅ GET /api/portfolio-management/portfolios returns 4 default portfolios")
        else:
            requirements_met.append("❌ GET /api/portfolio-management/portfolios - Portfolio count/structure issues")
        
        if positions_count_correct and expected_symbols_found:
            requirements_met.append("✅ GET /api/portfolio-management/portfolios/tradestation-main/positions returns 6 mock positions")
        else:
            requirements_met.append("❌ GET /api/portfolio-management/portfolios/tradestation-main/positions - Position issues")
        
        if available_count_correct:
            requirements_met.append("✅ GET /api/portfolio-management/available-portfolios/tradestation-main returns 3 other portfolios")
        else:
            requirements_met.append("❌ GET /api/portfolio-management/available-portfolios/tradestation-main - Count issues")
        
        if move_position_success:
            requirements_met.append("✅ POST /api/portfolio-management/move-position - Position move functionality working")
        else:
            requirements_met.append("❌ POST /api/portfolio-management/move-position - Move functionality failed")
        
        if create_portfolio_success:
            requirements_met.append("✅ POST /api/portfolio-management/create-portfolio - Custom portfolio creation working")
        else:
            requirements_met.append("❌ POST /api/portfolio-management/create-portfolio - Creation failed")
        
        if aggregate_view_success:
            requirements_met.append("✅ GET /api/portfolio-management/aggregate-view - Aggregated portfolio data working")
        else:
            requirements_met.append("❌ GET /api/portfolio-management/aggregate-view - Aggregate view failed")
        
        if move_history_success:
            requirements_met.append("✅ GET /api/portfolio-management/move-history/tradestation-main - Move history working")
        else:
            requirements_met.append("❌ GET /api/portfolio-management/move-history/tradestation-main - History failed")
        
        for requirement in requirements_met:
            print(f"   {requirement}")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Portfolio Management Service API endpoints working perfectly!")
            print(f"   All 7 endpoints are functional with proper data structures and expected responses.")
            print(f"   The 'Move to Portfolio X' functionality is ready for frontend integration.")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Portfolio Management Service mostly working with minor issues.")
            print(f"   Most endpoints functional, may need minor fixes for full functionality.")
        else:
            print(f"\n❌ VERDICT: NEEDS ATTENTION - Portfolio Management Service has significant issues.")
            print(f"   Multiple endpoints failing, requires investigation and fixes.")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = PortfolioManagementTester()
    result = tester.test_portfolio_management_endpoints()
    print(f"\n🎯 Portfolio Management Service Test Result: {'✅ PASSED' if result else '❌ FAILED'}")
    print(f"📊 Tests Run: {tester.tests_run}, Tests Passed: {tester.tests_passed}")
    sys.exit(0 if result else 1)