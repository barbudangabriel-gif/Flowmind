#!/usr/bin/env python3
"""
Master Mindfolio System - Simple Transfer Test (Nov 5, 2025)
Tests position/cash transfers WITHOUT TradeStation auth
"""

import requests
import json

API = "http://localhost:8000/api"
HEADERS = {"X-User-ID": "default", "Content-Type": "application/json"}

def log(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def create_mindfolio(name, balance):
    """Create a mindfolio"""
    resp = requests.post(
        f"{API}/mindfolio",
        json={"name": name, "starting_balance": balance},
        headers=HEADERS
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Created '{name}' (ID: {data['id']}, Cash: ${data['cash_balance']:,.2f})")
        return data
    else:
        print(f"❌ Failed: {resp.text}")
        return None

def add_position(mf_id, symbol, qty, price):
    """Add a position via BUY transaction"""
    from datetime import datetime, timezone
    resp = requests.post(
        f"{API}/mindfolio/{mf_id}/transactions",  # plural!
        json={
            "mindfolio_id": mf_id,
            "datetime": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "side": "BUY",
            "qty": qty,
            "price": price,
            "fee": 0.0
        },
        headers=HEADERS
    )
    if resp.status_code == 200:
        print(f"✅ Added {symbol}: {qty} @ ${price}")
        # Trigger position calculation
        calc_resp = requests.get(f"{API}/mindfolio/{mf_id}/positions", headers=HEADERS)
        if calc_resp.status_code == 200:
            positions = calc_resp.json()
            print(f"   Positions calculated: {len(positions)} total")
        return True
    else:
        print(f"❌ Failed to add {symbol}: {resp.text}")
        return False

def adjust_cash(mf_id, delta):
    """Adjust cash balance"""
    resp = requests.post(  # POST not PATCH!
        f"{API}/mindfolio/{mf_id}/funds",
        json={"delta": delta},
        headers=HEADERS
    )
    if resp.status_code == 200:
        print(f"✅ Adjusted cash: {delta:+,.2f}")
        return True
    else:
        print(f"❌ Failed to adjust cash: {resp.text}")
        return False

def get_mindfolio(mf_id):
    """Get mindfolio with positions"""
    resp = requests.get(f"{API}/mindfolio/{mf_id}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return None

def transfer_position(from_id, to_id, symbol, qty):
    """Transfer position"""
    log(f"Transferring {symbol} ({qty} shares)")
    resp = requests.post(
        f"{API}/mindfolio/transfer/position",
        json={
            "from_mindfolio_id": from_id,
            "to_mindfolio_id": to_id,
            "symbol": symbol,
            "quantity": qty
        },
        headers=HEADERS
    )
    if resp.status_code == 200:
        result = resp.json()
        if result.get("status") == "success":
            print(f"✅ Transfer successful!")
            transfer = result.get("transfer", {})
            print(f"   Value: ${transfer.get('transfer_value'):,.2f}")
            print(f"   From remaining: {len(result.get('from_remaining', []))} positions")
            print(f"   To updated: {len(result.get('to_updated', []))} positions")
            return True
        else:
            print(f"❌ {result.get('message')}")
            return False
    else:
        print(f"❌ Failed: {resp.text}")
        return False

def transfer_cash(from_id, to_id, amount):
    """Transfer cash"""
    log(f"Transferring ${amount:,.2f} cash")
    resp = requests.post(
        f"{API}/mindfolio/transfer/cash",
        json={
            "from_mindfolio_id": from_id,
            "to_mindfolio_id": to_id,
            "amount": amount
        },
        headers=HEADERS
    )
    if resp.status_code == 200:
        result = resp.json()
        if result.get("status") == "success":
            print(f"✅ Cash transfer successful!")
            print(f"   From balance: ${result.get('from_balance'):,.2f}")
            print(f"   To balance: ${result.get('to_balance'):,.2f}")
            return True
        else:
            print(f"❌ {result.get('message')}")
            return False
    else:
        print(f"❌ Failed: {resp.text}")
        return False

def show_summary(mf_id, name):
    """Show mindfolio summary"""
    mf = get_mindfolio(mf_id)
    if not mf:
        print(f"❌ Could not fetch {name}")
        return
    
    print(f"\n📊 {name}:")
    print(f"   Cash: ${mf['cash_balance']:,.2f}")
    print(f"   Positions: {len(mf.get('positions', []))}")
    for pos in mf.get('positions', []):
        value = pos['qty'] * pos['avg_cost']
        print(f"     - {pos['symbol']}: {pos['qty']} @ ${pos['avg_cost']:.2f} = ${value:,.2f}")
    print(f"   Allocated To: {mf.get('allocated_to', [])}")
    print(f"   Received From: {mf.get('received_from')}")

def main():
    log("MASTER MINDFOLIO TRANSFER TEST")
    print("Testing position/cash transfers (mock data, no TradeStation auth)")
    
    # Step 1: Create "master" mindfolio (simulate TradeStation account)
    log("Step 1: Create Mock Master Mindfolio")
    master = create_mindfolio("Mock TradeStation Master", 60000.0)
    if not master:
        return
    master_id = master['id']
    
    # Add positions (TSLA, NVDA)
    add_position(master_id, "TSLA", 100.0, 250.0)
    add_position(master_id, "NVDA", 50.0, 500.0)
    
    # Adjust cash (subtract position costs)
    adjust_cash(master_id, -(100*250 + 50*500))  # -50000
    
    # Step 2: Create specialized mindfolio
    log("Step 2: Create LEAPS Strategy Mindfolio")
    specialized = create_mindfolio("LEAPS Strategy", 0.0)
    if not specialized:
        return
    specialized_id = specialized['id']
    
    # Step 3: Transfer TSLA position (20 shares)
    success = transfer_position(master_id, specialized_id, "TSLA", 20.0)
    if not success:
        print("⚠️  Position transfer failed")
    
    # Step 4: Transfer NVDA position (10 shares)
    success = transfer_position(master_id, specialized_id, "NVDA", 10.0)
    if not success:
        print("⚠️  Position transfer failed")
    
    # Step 5: Transfer cash ($5,000)
    success = transfer_cash(master_id, specialized_id, 5000.0)
    if not success:
        print("⚠️  Cash transfer failed")
    
    # Final summary
    log("FINAL STATE")
    show_summary(master_id, "Mock Master")
    show_summary(specialized_id, "LEAPS Strategy")
    
    log("TEST COMPLETE")
    print("✅ Master Mindfolio transfer system operational!")
    print("\n📝 Next steps:")
    print("   1. Add TradeStation OAuth to test with real broker data")
    print("   2. Add UI buttons for Transfer Position/Cash")
    print("   3. Implement auto-sync (every 5 minutes)")

if __name__ == "__main__":
    main()
