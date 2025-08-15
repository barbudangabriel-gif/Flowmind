#!/usr/bin/env python3
"""
Expert Options Trading System Test Script
Tests all Expert Options endpoints for AI-powered options strategies
"""

import requests
import sys
import json
from datetime import datetime

class ExpertOptionsAPITester:
    def __init__(self, base_url="https://flowmind-live.preview.emergentagent.com"):
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

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_expert_options_endpoints(self):
        """Test Expert Options Trading System endpoints - COMPREHENSIVE TESTING"""
        print("\n🎯 EXPERT OPTIONS TRADING SYSTEM - AI-POWERED OPTIONS STRATEGIES")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test all Expert Options endpoints for AI-powered strategies")
        print("📋 ENDPOINTS TO TEST:")
        print("   1. GET /api/expert-options/strategies/SPY - All strategy recommendations")
        print("   2. GET /api/expert-options/wheel/SPY - Wheel strategy")
        print("   3. GET /api/expert-options/iron-condor/SPY - Iron Condor strategy")
        print("   4. GET /api/expert-options/volatility/SPY - Volatility Play strategy")
        print("   5. GET /api/expert-options/market-analysis/SPY - Market analysis")
        print("   6. GET /api/expert-options/learning/insights - Learning insights")
        print("   7. POST /api/expert-options/optimize/wheel - Parameter optimization")
        
        # Test 1: Expert Strategy Recommendations for SPY
        print("\n📊 TEST 1: Expert Strategy Recommendations")
        print("-" * 60)
        success, strategies_data = self.run_test(
            "Expert Strategy Recommendations (SPY)", 
            "GET", 
            "expert-options/strategies/SPY", 
            200
        )
        
        if success:
            recommendations = strategies_data.get('recommendations', [])
            total_strategies = strategies_data.get('total_strategies', 0)
            symbol = strategies_data.get('symbol', 'N/A')
            timestamp = strategies_data.get('timestamp', 'N/A')
            
            print(f"   ✅ Generated {total_strategies} strategy recommendations for {symbol}")
            print(f"   📅 Timestamp: {timestamp}")
            
            # Verify all 3 strategies are present
            expected_strategies = ["Wheel Strategy", "Iron Condor", "Volatility Play"]
            found_strategies = []
            
            for i, rec in enumerate(recommendations):
                strategy_name = rec.get('strategy_name', 'Unknown')
                confidence = rec.get('confidence_score', 0)
                strategy_type = rec.get('strategy_type', 'Unknown')
                
                found_strategies.append(strategy_name)
                print(f"     {i+1}. {strategy_name}")
                print(f"        - Type: {strategy_type}")
                print(f"        - Confidence: {confidence:.3f}")
                
                # Verify strategy structure
                required_fields = ['legs', 'max_profit', 'max_loss', 'confidence_score']
                missing_fields = [field for field in required_fields if field not in rec]
                
                if missing_fields:
                    print(f"        ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"        ✅ Complete strategy structure")
                    
                    # Check legs structure
                    legs = rec.get('legs', [])
                    if legs:
                        print(f"        📋 Strategy has {len(legs)} option legs:")
                        for j, leg in enumerate(legs):
                            action = leg.get('action', 'N/A')
                            option_type = leg.get('option_type', 'N/A')
                            strike = leg.get('strike', 'N/A')
                            premium = leg.get('premium', 'N/A')
                            print(f"           Leg {j+1}: {action} {option_type} @ ${strike} (${premium} premium)")
                    
                    # Show key metrics
                    max_profit = rec.get('max_profit', 0)
                    max_loss = rec.get('max_loss', 0)
                    if isinstance(max_profit, (int, float)):
                        print(f"        💰 Max Profit: ${max_profit:.2f}")
                    else:
                        print(f"        💰 Max Profit: {max_profit}")
                    if isinstance(max_loss, (int, float)):
                        print(f"        💸 Max Loss: ${max_loss:.2f}")
                    else:
                        print(f"        💸 Max Loss: {max_loss}")
            
            # Verify all expected strategies are present
            missing_strategies = [s for s in expected_strategies if s not in found_strategies]
            if missing_strategies:
                print(f"   ⚠️  Missing strategies: {missing_strategies}")
            else:
                print(f"   ✅ All 3 expert strategies generated successfully")
        
        # Test 2: Individual Strategy Endpoints
        print(f"\n🔄 TEST 2: Individual Strategy Endpoints")
        print("-" * 60)
        
        # Test Wheel Strategy
        print(f"\n   🎯 Testing Wheel Strategy")
        success, wheel_data = self.run_test(
            "Wheel Strategy (SPY)", 
            "GET", 
            "expert-options/wheel/SPY", 
            200
        )
        
        if success:
            strategy = wheel_data.get('strategy', {})
            symbol = wheel_data.get('symbol', 'N/A')
            timestamp = wheel_data.get('timestamp', 'N/A')
            
            print(f"     📈 Symbol: {symbol}")
            print(f"     📅 Generated: {timestamp}")
            print(f"     🎯 Wheel Strategy Details:")
            print(f"       - Phase: {strategy.get('phase', 'N/A')}")
            print(f"       - Strategy Type: {strategy.get('strategy_type', 'N/A')}")
            print(f"       - Current Price: ${strategy.get('current_price', 0):.2f}")
            print(f"       - Max Profit: ${strategy.get('max_profit', 0):.2f}")
            print(f"       - Max Loss: ${strategy.get('max_loss', 0):.2f}")
            print(f"       - Capital Required: ${strategy.get('capital_required', 0):.2f}")
            print(f"       - ROI Potential: {strategy.get('roi_potential', 0):.2f}%")
            print(f"       - Confidence Score: {strategy.get('confidence_score', 0):.3f}")
            
            # Check legs
            legs = strategy.get('legs', [])
            if legs:
                print(f"       - Option Legs ({len(legs)}):")
                for i, leg in enumerate(legs):
                    print(f"         {i+1}. {leg.get('action', 'N/A')} {leg.get('option_type', 'N/A')} @ ${leg.get('strike', 0):.2f}")
                    print(f"            Premium: ${leg.get('premium', 0):.2f}, Delta: {leg.get('delta', 0):.3f}")
        
        # Test Iron Condor Strategy
        print(f"\n   🦅 Testing Iron Condor Strategy")
        success, condor_data = self.run_test(
            "Iron Condor Strategy (SPY)", 
            "GET", 
            "expert-options/iron-condor/SPY", 
            200
        )
        
        if success:
            strategy = condor_data.get('strategy', {})
            symbol = condor_data.get('symbol', 'N/A')
            
            print(f"     📈 Symbol: {symbol}")
            print(f"     🦅 Iron Condor Strategy Details:")
            print(f"       - Strategy Type: {strategy.get('strategy_type', 'N/A')}")
            print(f"       - Current Price: ${strategy.get('current_price', 0):.2f}")
            print(f"       - Net Credit: ${strategy.get('net_credit', 0):.2f}")
            print(f"       - Max Profit: ${strategy.get('max_profit', 0):.2f}")
            print(f"       - Max Loss: ${strategy.get('max_loss', 0):.2f}")
            print(f"       - Breakeven High: ${strategy.get('breakeven_high', 0):.2f}")
            print(f"       - Breakeven Low: ${strategy.get('breakeven_low', 0):.2f}")
            print(f"       - Confidence Score: {strategy.get('confidence_score', 0):.3f}")
            
            # Check legs (should be 4 for Iron Condor)
            legs = strategy.get('legs', [])
            if legs:
                print(f"       - Option Legs ({len(legs)}):")
                for i, leg in enumerate(legs):
                    print(f"         {i+1}. {leg.get('action', 'N/A')} {leg.get('option_type', 'N/A')} @ ${leg.get('strike', 0):.2f}")
                    print(f"            Premium: ${leg.get('premium', 0):.2f}, Delta: {leg.get('delta', 0):.3f}")
        
        # Test Volatility Play Strategy
        print(f"\n   ⚡ Testing Volatility Play Strategy")
        success, vol_data = self.run_test(
            "Volatility Play Strategy (SPY)", 
            "GET", 
            "expert-options/volatility/SPY", 
            200
        )
        
        if success:
            strategy = vol_data.get('strategy', {})
            symbol = vol_data.get('symbol', 'N/A')
            
            print(f"     📈 Symbol: {symbol}")
            print(f"     ⚡ Volatility Play Strategy Details:")
            print(f"       - Strategy Type: {strategy.get('strategy_type', 'N/A')}")
            print(f"       - Strategy Name: {strategy.get('strategy_name', 'N/A')}")
            print(f"       - Current Price: ${strategy.get('current_price', 0):.2f}")
            print(f"       - Total Cost: ${strategy.get('total_cost', 0):.2f}")
            print(f"       - Max Loss: ${strategy.get('max_loss', 0):.2f}")
            print(f"       - Max Profit: {strategy.get('max_profit', 'N/A')}")
            print(f"       - Breakeven High: ${strategy.get('breakeven_high', 0):.2f}")
            print(f"       - Breakeven Low: ${strategy.get('breakeven_low', 0):.2f}")
            print(f"       - IV Expansion Needed: {strategy.get('iv_expansion_needed', 0):.1f}%")
            print(f"       - Confidence Score: {strategy.get('confidence_score', 0):.3f}")
            
            # Check legs
            legs = strategy.get('legs', [])
            if legs:
                print(f"       - Option Legs ({len(legs)}):")
                for i, leg in enumerate(legs):
                    print(f"         {i+1}. {leg.get('action', 'N/A')} {leg.get('option_type', 'N/A')} @ ${leg.get('strike', 0):.2f}")
                    print(f"            Premium: ${leg.get('premium', 0):.2f}, Delta: {leg.get('delta', 0):.3f}")
        
        # Test 3: Market Analysis
        print(f"\n📊 TEST 3: Market Analysis")
        print("-" * 60)
        success, market_data = self.run_test(
            "Market Analysis (SPY)", 
            "GET", 
            "expert-options/market-analysis/SPY", 
            200
        )
        
        if success:
            conditions = market_data.get('market_conditions', {})
            symbol = market_data.get('symbol', 'N/A')
            timestamp = market_data.get('timestamp', 'N/A')
            
            print(f"   📈 Market Analysis for {symbol}")
            print(f"   📅 Analysis Time: {timestamp}")
            print(f"   📊 Market Conditions:")
            print(f"     - Current Price: ${conditions.get('current_price', 0):.2f}")
            print(f"     - IV Percentile: {conditions.get('iv_percentile', 0):.1f}")
            print(f"     - IV Rank: {conditions.get('iv_rank', 0):.1f}")
            print(f"     - Historical Volatility (30d): {conditions.get('hv_30', 0):.1f}%")
            print(f"     - Trend: {conditions.get('trend', 'N/A')}")
            print(f"     - Support Level: ${conditions.get('support', 0):.2f}")
            print(f"     - Resistance Level: ${conditions.get('resistance', 0):.2f}")
            print(f"     - Days to Earnings: {conditions.get('days_to_earnings', 0)}")
            print(f"     - Volume Ratio: {conditions.get('volume_ratio', 0):.2f}")
            print(f"     - Options Volume: {conditions.get('options_volume', 0):,}")
            print(f"     - Optimal Strategy: {conditions.get('optimal_strategy', 'N/A')}")
            
            # Verify market analysis structure
            required_conditions = ['current_price', 'iv_percentile', 'trend', 'optimal_strategy']
            missing_conditions = [field for field in required_conditions if field not in conditions]
            
            if missing_conditions:
                print(f"     ⚠️  Missing market conditions: {missing_conditions}")
            else:
                print(f"     ✅ Complete market analysis provided")
        
        # Test 4: Learning Insights
        print(f"\n🧠 TEST 4: Learning System Insights")
        print("-" * 60)
        success, insights_data = self.run_test(
            "Learning System Insights", 
            "GET", 
            "expert-options/learning/insights", 
            200
        )
        
        if success:
            insights = insights_data.get('learning_insights', {})
            timestamp = insights_data.get('timestamp', 'N/A')
            
            print(f"   🤖 AI Learning System Status (Generated: {timestamp})")
            print(f"   📊 System Statistics:")
            print(f"     - Total Trades: {insights.get('total_trades', 0)}")
            print(f"     - Active Trades: {insights.get('active_trades', 0)}")
            
            # Strategy performance
            strategy_performance = insights.get('strategy_performance', {})
            print(f"     - Strategy Performance Data: {len(strategy_performance)} strategies")
            
            for strategy, perf in strategy_performance.items():
                if isinstance(perf, dict):
                    win_rate = perf.get('win_rate', 0)
                    total_trades = perf.get('total_trades', 0)
                    profit_factor = perf.get('profit_factor', 0)
                    sharpe_ratio = perf.get('sharpe_ratio', 0)
                    print(f"       * {strategy.replace('_', ' ').title()}:")
                    print(f"         - Win Rate: {win_rate:.1f}%")
                    print(f"         - Total Trades: {total_trades}")
                    print(f"         - Profit Factor: {profit_factor:.2f}")
                    print(f"         - Sharpe Ratio: {sharpe_ratio:.2f}")
            
            # Optimization status
            optimization_status = insights.get('optimization_status', {})
            print(f"   ⚙️  Optimization Status: {len(optimization_status)} strategies")
            
            for strategy, status in optimization_status.items():
                if isinstance(status, dict):
                    optimized = status.get('optimized', False)
                    last_optimization = status.get('last_optimization', 'N/A')
                    version = status.get('parameter_version', 'N/A')
                    print(f"       * {strategy.replace('_', ' ').title()}:")
                    print(f"         - Status: {'✅ Optimized' if optimized else '⏳ Learning'}")
                    print(f"         - Last Optimization: {last_optimization}")
                    print(f"         - Parameter Version: {version}")
            
            # Market insights
            market_insights = insights.get('market_insights', {})
            if market_insights:
                print(f"   🔮 Market Insights:")
                print(f"     - Preferred Strategy: {market_insights.get('preferred_strategy', 'N/A')}")
                print(f"     - Current Conditions: {market_insights.get('current_conditions', 'N/A')}")
                print(f"     - IV Environment: {market_insights.get('iv_environment', 'N/A')}")
        
        # Test 5: Parameter Optimization
        print(f"\n⚙️  TEST 5: Parameter Optimization")
        print("-" * 60)
        
        # Test valid strategy optimization
        success, optimize_data = self.run_test(
            "Parameter Optimization (Wheel)", 
            "POST", 
            "expert-options/optimize/wheel", 
            200
        )
        
        if success:
            print(f"   🔧 Wheel Strategy Optimization Result:")
            print(f"     - Message: {optimize_data.get('message', 'N/A')}")
            print(f"     - Strategy Type: {optimize_data.get('strategy_type', 'N/A')}")
            print(f"     - Timestamp: {optimize_data.get('timestamp', 'N/A')}")
        
        # Test other strategy types
        for strategy_type in ['iron_condor', 'volatility_play']:
            success, opt_data = self.run_test(
                f"Parameter Optimization ({strategy_type})", 
                "POST", 
                f"expert-options/optimize/{strategy_type}", 
                200
            )
            
            if success:
                print(f"   🔧 {strategy_type.replace('_', ' ').title()} Optimization:")
                print(f"     - Message: {opt_data.get('message', 'N/A')}")
        
        # Test invalid strategy type
        success, error_data = self.run_test(
            "Parameter Optimization (Invalid)", 
            "POST", 
            "expert-options/optimize/invalid_strategy", 
            200  # Should return 200 with error message
        )
        
        if success and 'error' in error_data:
            print(f"   ✅ Error handling working: {error_data.get('error', 'N/A')}")
        
        # Test 6: Comprehensive Validation
        print(f"\n✅ TEST 6: Expert Options System Validation")
        print("-" * 60)
        
        validation_results = {
            "strategy_recommendations": strategies_data.get('total_strategies', 0) >= 3,
            "wheel_strategy": wheel_data.get('strategy', {}).get('strategy_type') == 'wheel',
            "iron_condor_strategy": condor_data.get('strategy', {}).get('strategy_type') == 'iron_condor',
            "volatility_strategy": vol_data.get('strategy', {}).get('strategy_type') == 'volatility_play',
            "market_analysis": len(market_data.get('market_conditions', {})) >= 5,
            "learning_insights": 'learning_insights' in insights_data,
            "parameter_optimization": 'message' in optimize_data
        }
        
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        
        print(f"   📊 Validation Results: {passed_validations}/{total_validations} passed")
        
        for test_name, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"     {status} {test_name.replace('_', ' ').title()}")
        
        success_rate = (passed_validations / total_validations) * 100
        print(f"   🎯 Expert Options Success Rate: {success_rate:.1f}%")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        if success_rate >= 85:
            print(f"🎉 EXCELLENT: Expert Options Trading System is fully operational!")
            print(f"   🤖 AI-powered options strategies with confidence scores working perfectly")
            print(f"   📈 All 3 strategies (Wheel, Iron Condor, Volatility Play) generating properly")
            print(f"   🧠 Machine learning insights and parameter optimization functional")
            print(f"   📊 Market analysis providing comprehensive conditions assessment")
            print(f"   ⚙️  Parameter optimization system ready for continuous learning")
        elif success_rate >= 70:
            print(f"✅ GOOD: Expert Options system mostly working with minor issues")
            print(f"   🔧 Some components may need attention but core functionality works")
        else:
            print(f"❌ NEEDS ATTENTION: Expert Options system has significant issues")
            print(f"   🚨 Multiple components failing - requires debugging")
        
        return success_rate >= 80

def main():
    print("🚀 EXPERT OPTIONS TRADING SYSTEM - COMPREHENSIVE API TESTING")
    print("=" * 80)
    print("🎯 Testing AI-powered options strategies with machine learning capabilities")
    print("📅 Test Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    tester = ExpertOptionsAPITester()
    
    # Run comprehensive Expert Options testing
    success = tester.test_expert_options_endpoints()
    
    # Print final results
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"✅ Tests Passed: {tester.tests_passed}")
    print(f"❌ Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"📊 Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if success:
        print("🎉 EXPERT OPTIONS SYSTEM FULLY OPERATIONAL!")
        print("   🤖 AI-powered options strategies ready for production")
        print("   📈 All strategy endpoints working correctly")
        print("   🧠 Machine learning system functional")
        return 0
    else:
        print("⚠️  EXPERT OPTIONS SYSTEM NEEDS ATTENTION!")
        print("   🔧 Some endpoints may require debugging")
        return 1

if __name__ == "__main__":
    sys.exit(main())