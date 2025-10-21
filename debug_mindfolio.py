#!/usr/bin/env python3
"""
Debug script to test mindfolio service data processing
"""

import asyncio
import json
import sys
import os
sys.path.append('/app/backend')

from mindfolio_service import MindfolioService, MindfolioMetrics
from tradestation_client import Position

def simulate_tradestation_response():
 """Simulate a TradeStation API response based on expected format"""
 return {
 "account_id": "123456789",
 "balances": {
 "TotalEquity": 50000.00,
 "CashBalance": 10000.00,
 "MarketValue": 40000.00,
 "BuyingPower": 80000.00
 },
 "positions": [
 {
 "account_id": "123456789",
 "symbol": "AAPL",
 "asset_type": "EQ",
 "quantity": 100,
 "average_price": 150.00,
 "current_price": 160.00,
 "market_value": 16000.00,
 "unrealized_pnl": 1000.00,
 "unrealized_pnl_percent": 6.67
 },
 {
 "account_id": "123456789", 
 "symbol": "MSFT",
 "asset_type": "EQ",
 "quantity": 50,
 "average_price": 300.00,
 "current_price": 320.00,
 "market_value": 16000.00,
 "unrealized_pnl": 1000.00,
 "unrealized_pnl_percent": 6.67
 }
 ],
 "recent_orders": [],
 "summary_timestamp": "2025-08-14T21:25:36.769361",
 "totals": {
 "position_count": 2,
 "recent_order_count": 0,
 "total_market_value": 32000.00,
 "total_unrealized_pnl": 2000.00
 }
 }

def test_position_creation():
 """Test creating Position objects from data"""
 print("Testing Position object creation...")
 
 # Test data
 pos_data = {
 "account_id": "123456789",
 "symbol": "AAPL", 
 "asset_type": "EQ",
 "quantity": 100,
 "average_price": 150.00,
 "current_price": 160.00,
 "market_value": 16000.00,
 "unrealized_pnl": 1000.00,
 "unrealized_pnl_percent": 6.67
 }
 
 try:
 position = Position(
 account_id=pos_data.get("account_id", ""),
 symbol=pos_data.get("symbol", ""),
 asset_type=pos_data.get("asset_type", "EQ"),
 quantity=pos_data.get("quantity", 0),
 average_price=pos_data.get("average_price", 0.0),
 current_price=pos_data.get("current_price", 0.0),
 market_value=pos_data.get("market_value", 0.0),
 unrealized_pnl=pos_data.get("unrealized_pnl", 0.0),
 unrealized_pnl_percent=pos_data.get("unrealized_pnl_percent", 0.0)
 )
 print(f" Position created successfully: {position}")
 return position
 except Exception as e:
 print(f" Error creating position: {e}")
 return None

def test_mindfolio_processing():
 """Test the mindfolio processing logic"""
 print("\nTesting mindfolio processing logic...")
 
 # Simulate account summary data
 account_summary = simulate_tradestation_response()
 print(f"Simulated account summary: {json.dumps(account_summary, indent=2)}")
 
 # Test position parsing
 positions = []
 for pos_data in account_summary.get("positions", []):
 if isinstance(pos_data, dict):
 print(f"\nProcessing position data: {pos_data}")
 position = Position(
 account_id=pos_data.get("account_id", account_summary["account_id"]),
 symbol=pos_data.get("symbol", ""),
 asset_type=pos_data.get("asset_type", "EQ"),
 quantity=pos_data.get("quantity", 0),
 average_price=pos_data.get("average_price", 0.0),
 current_price=pos_data.get("current_price", 0.0),
 market_value=pos_data.get("market_value", 0.0),
 unrealized_pnl=pos_data.get("unrealized_pnl", 0.0),
 unrealized_pnl_percent=pos_data.get("unrealized_pnl_percent", 0.0)
 )
 positions.append(position)
 print(f" Created position: {position}")
 
 print(f"\nTotal positions created: {len(positions)}")
 
 # Test metrics calculation 
 metrics = MindfolioMetrics.calculate_total_return(positions)
 print(f"Mindfolio metrics: {json.dumps(metrics, indent=2)}")
 
 return positions, metrics

if __name__ == "__main__":
 print(" Debug Mindfolio Service Data Processing")
 print("=" * 50)
 
 # Test individual position creation
 test_position = test_position_creation()
 
 # Test full mindfolio processing
 positions, metrics = test_mindfolio_processing()
 
 print(f"\n Final Results:")
 print(f"Positions: {len(positions)}")
 print(f"Total Market Value: ${metrics['total_market_value']:,.2f}")
 print(f"Total P&L: ${metrics['total_unrealized_pnl']:,.2f}")
 print(f"Return: {metrics['total_return_percent']:.2f}%")