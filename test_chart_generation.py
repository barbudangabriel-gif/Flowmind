#!/usr/bin/env python3
"""
Test chart generation directly
"""

import sys
import os
sys.path.append('/app/backend')

from options_strategy_charts import chart_generator

def test_chart_generation():
    """Test chart generation with sample strategy"""
    
    # Test Long Put strategy
    long_put_strategy = {
        'strategy_name': 'Long Put',
        'ticker': 'MSFT',
        'strategy_type': 'directional',
        'entry_logic': {
            'underlying_price': 313.0
        }
    }
    
    print("🎯 Testing Long Put Chart Generation")
    try:
        chart_data = chart_generator.generate_strategy_chart(long_put_strategy)
        print(f"✅ Chart generated successfully")
        print(f"   Chart Type: {chart_data.get('chart_type')}")
        print(f"   Max Loss: {chart_data.get('max_loss')}")
        print(f"   Breakeven: {chart_data.get('breakeven')}")
        
        # Check plotly data
        import json
        plotly_json = chart_data.get('plotly_chart')
        if plotly_json:
            plotly_data = json.loads(plotly_json)
            if 'data' in plotly_data and plotly_data['data']:
                trace = plotly_data['data'][0]
                x_data = trace.get('x', [])
                y_data = trace.get('y', [])
                print(f"   X data points: {len(x_data)}")
                print(f"   Y data points: {len(y_data)}")
                if x_data and y_data:
                    print(f"   X range: ${min(x_data):.2f} - ${max(x_data):.2f}")
                    print(f"   Y range: ${min(y_data):.2f} - ${max(y_data):.2f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test Bull Call Spread
    print("\n🎯 Testing Bull Call Spread Chart Generation")
    bull_call_strategy = {
        'strategy_name': 'Bull Call Spread',
        'ticker': 'AAPL',
        'strategy_type': 'vertical_spread',
        'entry_logic': {
            'underlying_price': 229.0
        }
    }
    
    try:
        chart_data = chart_generator.generate_strategy_chart(bull_call_strategy)
        print(f"✅ Chart generated successfully")
        print(f"   Chart Type: {chart_data.get('chart_type')}")
        print(f"   Max Profit: {chart_data.get('max_profit')}")
        print(f"   Max Loss: {chart_data.get('max_loss')}")
        print(f"   Breakeven Points: {chart_data.get('breakeven_points')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chart_generation()