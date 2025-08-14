#!/usr/bin/env python3
"""
Debug actual TradeStation API response format vs expected format
"""

import json
import sys
import os
sys.path.append('/app/backend')

def simulate_real_tradestation_response():
    """Simulate what TradeStation API actually returns based on their documentation"""
    # This is based on TradeStation API documentation format
    return {
        "Accounts": [
            {
                "Key": "123456789",
                "Name": "Test Account",
                "TypeDescription": "Individual"
            }
        ]
    }

def simulate_real_balance_response():
    """Simulate actual TradeStation balance response"""
    return {
        "Key": "123456789",
        "TotalEquity": 50000.00,
        "CashBalance": 10000.00,
        "UnclearedDeposit": 0.00,
        "BuyingPower": 80000.00
    }

def simulate_real_positions_response():
    """Simulate actual TradeStation positions response"""
    return {
        "Positions": [
            {
                "Symbol": "AAPL",
                "AssetType": "EQ", 
                "Quantity": 100,
                "AveragePrice": 150.00,
                "Last": 160.00,
                "MarketValue": 16000.00,
                "UnrealizedProfitLoss": 1000.00,
                "UnrealizedProfitLossPercent": 6.67
            },
            {
                "Symbol": "MSFT",
                "AssetType": "EQ",
                "Quantity": 50, 
                "AveragePrice": 300.00,
                "Last": 320.00,
                "MarketValue": 16000.00,
                "UnrealizedProfitLoss": 1000.00,
                "UnrealizedProfitLossPercent": 6.67
            }
        ]
    }

def test_data_processing():
    """Test if our processing matches expected vs actual TradeStation format"""
    print("🔍 Testing TradeStation API Data Processing")
    print("=" * 50)
    
    # Simulate the responses
    accounts_response = simulate_real_tradestation_response()
    balance_response = simulate_real_balance_response()
    positions_response = simulate_real_positions_response()
    
    print("📡 Simulated TradeStation API Responses:")
    print(f"Accounts: {json.dumps(accounts_response, indent=2)}")
    print(f"Balance: {json.dumps(balance_response, indent=2)}")
    print(f"Positions: {json.dumps(positions_response, indent=2)}")
    
    # Test position processing like in tradestation_client.py
    print("\n🔄 Processing positions like TradeStation client...")
    positions = []
    
    for pos_data in positions_response.get("Positions", []):
        try:
            # This is exactly what tradestation_client.py does
            position_dict = {
                "account_id": "123456789",  # account_id parameter
                "symbol": pos_data.get("Symbol", ""),
                "asset_type": pos_data.get("AssetType", ""), 
                "quantity": int(pos_data.get("Quantity", 0)),
                "average_price": float(pos_data.get("AveragePrice", 0.0)),
                "current_price": float(pos_data.get("Last", 0.0)),
                "market_value": float(pos_data.get("MarketValue", 0.0)),
                "unrealized_pnl": float(pos_data.get("UnrealizedProfitLoss", 0.0)),
                "unrealized_pnl_percent": float(pos_data.get("UnrealizedProfitLossPercent", 0.0))
            }
            positions.append(position_dict)
            print(f"✅ Processed position: {position_dict}")
        except Exception as e:
            print(f"❌ Error processing position: {e}")
    
    # Test account summary structure
    print("\n📊 Creating account summary structure...")
    account_summary = {
        "account_id": "123456789",
        "balances": balance_response,
        "positions": positions,
        "recent_orders": [],
        "summary_timestamp": "2025-08-14T21:25:36.769361",
        "totals": {
            "position_count": len(positions),
            "recent_order_count": 0,
            "total_market_value": sum(pos.get("market_value", 0) for pos in positions),
            "total_unrealized_pnl": sum(pos.get("unrealized_pnl", 0) for pos in positions)
        }
    }
    
    print(f"Account Summary: {json.dumps(account_summary, indent=2)}")
    
    # Test portfolio service processing
    print("\n⚙️ Testing portfolio service processing...")
    
    from portfolio_service import PortfolioService, PortfolioMetrics
    from tradestation_client import Position
    
    # Simulate what portfolio_service.py does
    positions_objects = []
    for pos_data in account_summary.get("positions", []):
        if isinstance(pos_data, dict):
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
            positions_objects.append(position)
            print(f"✅ Created Position object: {position}")
    
    # Calculate metrics
    metrics = PortfolioMetrics.calculate_total_return(positions_objects)
    print(f"\n📈 Portfolio Metrics: {json.dumps(metrics, indent=2)}")
    
    return account_summary, metrics

if __name__ == "__main__":
    account_summary, metrics = test_data_processing()
    
    print(f"\n🎯 Final Summary:")
    print(f"Positions processed: {len(account_summary['positions'])}")
    print(f"Total Market Value: ${metrics['total_market_value']:,.2f}")
    print(f"Total P&L: ${metrics['total_unrealized_pnl']:,.2f}")
    print(f"Return: {metrics['total_return_percent']:.2f}%")
    
    # Check for potential issues
    print(f"\n🔍 Diagnostic Information:")
    print(f"Are positions empty? {len(account_summary['positions']) == 0}")
    print(f"Are balances empty? {not account_summary['balances']}")
    print(f"Market value is zero? {metrics['total_market_value'] == 0}")
    print(f"P&L is zero? {metrics['total_unrealized_pnl'] == 0}")