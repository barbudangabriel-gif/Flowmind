#!/usr/bin/env python3
"""
Enhanced Trading Strategies Chart Integration Test
Focus on testing the new interactive charts functionality
"""

import requests
import json
import sys
from datetime import datetime

class ChartIntegrationTester:
    def __init__(self, base_url="https://put-selling-dash.preview.emergentagent.com"):
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

    def test_enhanced_trading_strategies_with_charts(self):
        """Test Enhanced Trading Strategies API with Interactive Charts Integration"""
        print("\n🎯 TESTING ENHANCED TRADING STRATEGIES WITH INTERACTIVE CHARTS")
        print("=" * 80)
        
        success, strategies_data = self.run_test(
            "Enhanced Trading Strategies with Charts", 
            "GET", 
            "unusual-whales/trading-strategies", 
            200
        )
        
        if not success:
            print("❌ CRITICAL: Trading strategies endpoint failed")
            return False
            
        # Test 1: Verify response structure
        print(f"\n📊 RESPONSE STRUCTURE VALIDATION:")
        required_top_level_fields = ['status', 'trading_strategies', 'charts_included', 'tradestation_ready']
        missing_fields = [field for field in required_top_level_fields if field not in strategies_data]
        
        if missing_fields:
            print(f"❌ Missing top-level fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required top-level fields present")
        
        # Test 2: Verify charts_included flag
        charts_included = strategies_data.get('charts_included', False)
        print(f"📈 Charts Included Flag: {'✅ TRUE' if charts_included else '❌ FALSE'}")
        
        if not charts_included:
            print("❌ CRITICAL: charts_included flag is False")
            return False
        
        # Test 3: Analyze strategies and their charts
        strategies = strategies_data.get('trading_strategies', [])
        print(f"📋 Total Strategies Generated: {len(strategies)}")
        
        if not strategies:
            print("⚠️  No strategies generated - this may be expected if no unusual activity")
            return True
        
        # Detailed chart analysis
        chart_analysis = {
            'total_strategies': len(strategies),
            'strategies_with_charts': 0,
            'valid_plotly_charts': 0,
            'chart_types_found': set(),
            'strategy_chart_mapping': {},
            'chart_metrics_found': 0,
            'chart_errors': []
        }
        
        print(f"\n🎨 DETAILED CHART INTEGRATION ANALYSIS:")
        print("-" * 60)
        
        for i, strategy in enumerate(strategies):
            strategy_name = strategy.get('strategy_name', f'Strategy {i+1}')
            ticker = strategy.get('ticker', 'N/A')
            strategy_type = strategy.get('strategy_type', 'unknown')
            
            print(f"\n📋 Strategy {i+1}: {strategy_name} ({ticker})")
            print(f"   Strategy Type: {strategy_type}")
            
            # Test 4: Verify chart field exists
            if 'chart' not in strategy:
                print(f"   ❌ CRITICAL: Missing 'chart' field")
                chart_analysis['chart_errors'].append(f"{strategy_name}: Missing chart field")
                continue
                
            chart_analysis['strategies_with_charts'] += 1
            chart_data = strategy['chart']
            
            # Test 5: Verify chart_type
            chart_type = chart_data.get('chart_type', 'unknown')
            chart_analysis['chart_types_found'].add(chart_type)
            chart_analysis['strategy_chart_mapping'][strategy_name] = chart_type
            
            print(f"   📊 Chart Type: {chart_type}")
            
            # Test 6: Verify strategy-specific chart type mapping
            expected_chart_types = {
                'bull call spread': 'vertical_spread',
                'bear put spread': 'vertical_spread',
                'bear call spread': 'vertical_spread',
                'bull put spread': 'vertical_spread',
                'long call': 'directional',
                'long put': 'directional',
                'short call': 'directional',
                'short put': 'directional',
                'long straddle': 'volatility',
                'long strangle': 'volatility',
                'short straddle': 'volatility',
                'short strangle': 'volatility',
                'iron condor': 'iron_condor',
                'iron butterfly': 'iron_condor',
                'cash-secured put': 'income',
                'covered call': 'income',
                'protective put': 'income',
                'collar': 'income'
            }
            
            strategy_name_lower = strategy_name.lower()
            expected_type = None
            for name_pattern, expected_chart_type in expected_chart_types.items():
                if name_pattern in strategy_name_lower:
                    expected_type = expected_chart_type
                    break
            
            if expected_type:
                if chart_type == expected_type:
                    print(f"   ✅ Chart Type Mapping: Correct ({chart_type})")
                else:
                    print(f"   ⚠️  Chart Type Mapping: Expected {expected_type}, got {chart_type}")
            else:
                print(f"   ℹ️  Chart Type Mapping: Unknown strategy pattern, got {chart_type}")
            
            # Test 7: Verify plotly_chart JSON
            if 'plotly_chart' not in chart_data:
                print(f"   ❌ CRITICAL: Missing 'plotly_chart' field")
                chart_analysis['chart_errors'].append(f"{strategy_name}: Missing plotly_chart")
                continue
            
            try:
                plotly_json_str = chart_data['plotly_chart']
                if not isinstance(plotly_json_str, str):
                    print(f"   ❌ plotly_chart is not a string: {type(plotly_json_str)}")
                    continue
                
                # Parse the JSON
                plotly_chart = json.loads(plotly_json_str)
                
                # Verify essential plotly structure
                if 'data' not in plotly_chart or 'layout' not in plotly_chart:
                    print(f"   ❌ Invalid plotly structure: missing data or layout")
                    continue
                
                chart_analysis['valid_plotly_charts'] += 1
                print(f"   ✅ Plotly Chart: Valid JSON structure")
                
                # Test 8: Verify chart data points
                chart_data_traces = plotly_chart.get('data', [])
                if chart_data_traces and len(chart_data_traces) > 0:
                    first_trace = chart_data_traces[0]
                    x_data = first_trace.get('x', [])
                    y_data = first_trace.get('y', [])
                    
                    if x_data and y_data and len(x_data) > 0 and len(y_data) > 0:
                        print(f"   ✅ P&L Data Points: {len(x_data)} price points")
                        
                        # Verify data is realistic
                        if isinstance(x_data[0], (int, float)) and isinstance(y_data[0], (int, float)):
                            print(f"   ✅ Data Types: Numeric price/P&L data")
                        else:
                            print(f"   ⚠️  Data Types: Non-numeric data detected")
                    else:
                        print(f"   ❌ P&L Data Points: Empty or missing x/y data")
                else:
                    print(f"   ❌ P&L Data Points: No chart traces found")
                
                # Test 9: Verify chart layout and styling
                layout = plotly_chart.get('layout', {})
                if 'title' in layout and 'xaxis' in layout and 'yaxis' in layout:
                    print(f"   ✅ Chart Layout: Complete with title and axes")
                    
                    # Check for dark theme
                    template = layout.get('template', '')
                    if 'dark' in str(template).lower():
                        print(f"   ✅ Chart Theme: Dark theme applied")
                    else:
                        print(f"   ℹ️  Chart Theme: {template or 'default'}")
                else:
                    print(f"   ⚠️  Chart Layout: Incomplete layout structure")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Plotly Chart JSON Error: {str(e)}")
                chart_analysis['chart_errors'].append(f"{strategy_name}: JSON decode error")
                continue
            except Exception as e:
                print(f"   ❌ Plotly Chart Error: {str(e)}")
                chart_analysis['chart_errors'].append(f"{strategy_name}: {str(e)}")
                continue
            
            # Test 10: Verify chart metrics
            metrics_found = []
            if 'max_profit' in chart_data:
                max_profit = chart_data['max_profit']
                if isinstance(max_profit, (int, float)) and max_profit > 0:
                    metrics_found.append(f"Max Profit: ${max_profit:.0f}")
            
            if 'max_loss' in chart_data:
                max_loss = chart_data['max_loss']
                if isinstance(max_loss, (int, float)) and max_loss > 0:
                    metrics_found.append(f"Max Loss: ${max_loss:.0f}")
            
            # Check for breakeven points (different field names possible)
            breakeven_fields = ['breakeven_points', 'breakeven', 'breakeven_upper', 'breakeven_lower']
            for be_field in breakeven_fields:
                if be_field in chart_data:
                    be_value = chart_data[be_field]
                    if isinstance(be_value, list) and be_value:
                        metrics_found.append(f"Breakeven: ${be_value[0]:.2f}")
                        break
                    elif isinstance(be_value, (int, float)):
                        metrics_found.append(f"Breakeven: ${be_value:.2f}")
                        break
            
            if metrics_found:
                chart_analysis['chart_metrics_found'] += 1
                print(f"   ✅ Chart Metrics: {', '.join(metrics_found)}")
            else:
                print(f"   ⚠️  Chart Metrics: No financial metrics found")
        
        # Test 11: Print comprehensive analysis summary
        print(f"\n📊 COMPREHENSIVE CHART INTEGRATION SUMMARY:")
        print("=" * 60)
        print(f"Total Strategies: {chart_analysis['total_strategies']}")
        print(f"Strategies with Charts: {chart_analysis['strategies_with_charts']}")
        print(f"Valid Plotly Charts: {chart_analysis['valid_plotly_charts']}")
        print(f"Strategies with Metrics: {chart_analysis['chart_metrics_found']}")
        print(f"Chart Types Found: {', '.join(sorted(chart_analysis['chart_types_found']))}")
        
        if chart_analysis['chart_errors']:
            print(f"\n❌ Chart Errors ({len(chart_analysis['chart_errors'])}):")
            for error in chart_analysis['chart_errors']:
                print(f"   - {error}")
        
        # Calculate success rates
        if chart_analysis['total_strategies'] > 0:
            chart_coverage = (chart_analysis['strategies_with_charts'] / chart_analysis['total_strategies']) * 100
            chart_validity = (chart_analysis['valid_plotly_charts'] / chart_analysis['total_strategies']) * 100
            metrics_coverage = (chart_analysis['chart_metrics_found'] / chart_analysis['total_strategies']) * 100
            
            print(f"\n📈 SUCCESS METRICS:")
            print(f"Chart Coverage: {chart_coverage:.1f}%")
            print(f"Chart Validity: {chart_validity:.1f}%")
            print(f"Metrics Coverage: {metrics_coverage:.1f}%")
            
            # Overall success criteria
            overall_success = (
                chart_coverage >= 90 and  # At least 90% of strategies have charts
                chart_validity >= 80 and  # At least 80% have valid plotly charts
                len(chart_analysis['chart_types_found']) >= 2  # At least 2 different chart types
            )
            
            print(f"\n🎯 OVERALL CHART INTEGRATION: {'✅ SUCCESS' if overall_success else '⚠️  NEEDS IMPROVEMENT'}")
            
            return overall_success
        else:
            print(f"\n⚠️  No strategies to analyze - may be expected behavior")
            return True

def main():
    print("🚀 Enhanced Trading Strategies Chart Integration Test")
    print("=" * 80)
    print("Testing the new interactive charts functionality for options strategies")
    print("Focus: Plotly chart generation, chart types, P&L calculations, and metrics")
    print("=" * 80)
    
    tester = ChartIntegrationTester()
    
    # Run the comprehensive chart integration test
    success = tester.test_enhanced_trading_strategies_with_charts()
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if success:
        print("🎉 Chart Integration Test: SUCCESS!")
        print("✅ Enhanced Trading Strategies endpoint with interactive charts is working correctly")
        return 0
    else:
        print("⚠️  Chart Integration Test: NEEDS ATTENTION")
        print("❌ Some chart integration features may need fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())