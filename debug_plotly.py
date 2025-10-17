#!/usr/bin/env python3
"""
Debug plotly chart creation
"""

import numpy as np
import plotly.graph_objects as go
import json

def debug_plotly_creation():
 """Debug plotly chart creation"""
 
 # Generate test data
 underlying_price = 313.0
 strike = underlying_price * 0.98
 premium = 3
 
 price_range = np.linspace(underlying_price * 0.8, underlying_price * 1.2, 100)
 total_pl = np.maximum(strike - price_range, 0) - premium
 
 print(f"Input data: {len(price_range)} price points, {len(total_pl)} P&L points")
 
 # Create Plotly chart
 fig = go.Figure()
 
 fig.add_trace(go.Scatter(
 x=price_range,
 y=total_pl * 100,
 mode='lines',
 name='P&L',
 line=dict(color='#3B82F6', width=3),
 fill='tozeroy',
 fillcolor='rgba(59, 130, 246, 0.1)',
 hovertemplate='<b>Price: $%{x:.2f}</b><br>P&L: $%{y:.0f}<extra></extra>'
 ))
 
 # Check the figure data
 print(f"Figure traces: {len(fig.data)}")
 if fig.data:
 trace = fig.data[0]
 print(f"Trace x data: {len(trace.x)} points")
 print(f"Trace y data: {len(trace.y)} points")
 print(f"First few x: {list(trace.x[:5])}")
 print(f"First few y: {list(trace.y[:5])}")
 
 # Convert to JSON
 plotly_json = fig.to_json()
 
 # Parse back to check
 parsed = json.loads(plotly_json)
 if 'data' in parsed and parsed['data']:
 data_trace = parsed['data'][0]
 x_data = data_trace.get('x', [])
 y_data = data_trace.get('y', [])
 print(f"JSON x data: {len(x_data)} points")
 print(f"JSON y data: {len(y_data)} points")

if __name__ == "__main__":
 debug_plotly_creation()