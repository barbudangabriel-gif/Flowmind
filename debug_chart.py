#!/usr/bin/env python3
"""
Debug chart generation
"""

import numpy as np
import sys
import os
sys.path.append('/app/backend')

def debug_directional_chart():
 """Debug the directional chart generation"""
 
 # Simulate the directional chart logic
 underlying_price = 313.0
 strategy_name = 'Long Put'
 
 is_call = 'call' in strategy_name.lower()
 strike = underlying_price * (1.02 if is_call else 0.98)
 premium = 3 # Assumed premium
 
 print(f"Strategy: {strategy_name}")
 print(f"Underlying Price: ${underlying_price}")
 print(f"Is Call: {is_call}")
 print(f"Strike: ${strike}")
 print(f"Premium: ${premium}")
 
 # Generate price range
 price_range = np.linspace(underlying_price * 0.8, underlying_price * 1.2, 100)
 print(f"Price Range: {len(price_range)} points from ${price_range[0]:.2f} to ${price_range[-1]:.2f}")
 
 # Calculate P&L
 if is_call:
 total_pl = np.maximum(price_range - strike, 0) - premium
 else:
 total_pl = np.maximum(strike - price_range, 0) - premium
 
 print(f"P&L Array: {len(total_pl)} points")
 print(f"P&L Range: ${min(total_pl):.2f} to ${max(total_pl):.2f}")
 
 # Check for breakeven
 breakeven = strike + premium if is_call else strike - premium
 print(f"Calculated Breakeven: ${breakeven:.2f}")
 
 # Check what happens when we convert to lists for JSON
 price_list = price_range.tolist()
 pl_list = (total_pl * 100).tolist()
 
 print(f"Price List Length: {len(price_list)}")
 print(f"P&L List Length: {len(pl_list)}")
 print(f"First few prices: {price_list[:5]}")
 print(f"First few P&L: {pl_list[:5]}")

if __name__ == "__main__":
 debug_directional_chart()