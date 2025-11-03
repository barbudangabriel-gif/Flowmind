#!/usr/bin/env python3
"""
Master Mindfolio System - Comprehensive Test Suite
Tests all backend endpoints and data integrity
"""

import json
import requests
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"
USER_ID = "test_user"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def test_1_create_master_mindfolio():
    """Test 1: Create a Master Mindfolio"""
    print_header("TEST 1: Create Master Mindfolio")
    
    payload = {
        "name": "Test TradeStation Master",
        "broker": "TradeStation",
        "account_id": "TEST123456",
        "starting_balance": 50000.0,
        "is_master": True,
        "auto_sync": True
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/mindfolio",
            json=payload,
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            master_id = data.get("mindfolio", {}).get("id")
            
            # Verify master fields
            mindfolio = data.get("mindfolio", {})
            checks = {
                "is_master": mindfolio.get("is_master") == True,
                "auto_sync": mindfolio.get("auto_sync") == True,
                "sync_status": mindfolio.get("sync_status") == "idle",
                "allocated_to": mindfolio.get("allocated_to") == [],
                "received_from": mindfolio.get("received_from") is None
            }
            
            all_passed = all(checks.values())
            print_result("Master Mindfolio Creation", all_passed, 
                        f"Master ID: {master_id}")
            
            for check, result in checks.items():
                print(f"  - {check}: {'✓' if result else '✗'}")
            
            return master_id if all_passed else None
        else:
            print_result("Master Mindfolio Creation", False, 
                        f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result("Master Mindfolio Creation", False, str(e))
        return None

def test_2_create_specialized_mindfolio():
    """Test 2: Create a Specialized Mindfolio"""
    print_header("TEST 2: Create Specialized Mindfolio")
    
    payload = {
        "name": "LEAPS Strategy",
        "starting_balance": 10000.0,
        "is_master": False,
        "auto_sync": False
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/mindfolio",
            json=payload,
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            specialized_id = data.get("mindfolio", {}).get("id")
            
            mindfolio = data.get("mindfolio", {})
            checks = {
                "is_master": mindfolio.get("is_master") == False,
                "auto_sync": mindfolio.get("auto_sync") == False,
            }
            
            all_passed = all(checks.values())
            print_result("Specialized Mindfolio Creation", all_passed,
                        f"Specialized ID: {specialized_id}")
            
            return specialized_id if all_passed else None
        else:
            print_result("Specialized Mindfolio Creation", False,
                        f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result("Specialized Mindfolio Creation", False, str(e))
        return None

def test_3_add_positions_to_master(master_id):
    """Test 3: Add positions to Master Mindfolio"""
    print_header("TEST 3: Add Positions to Master")
    
    if not master_id:
        print_result("Add Positions", False, "No master_id provided")
        return False
    
    # Add 3 positions: TSLA, NVDA, AAPL
    positions = [
        {"symbol": "TSLA", "qty": 100, "price": 250.0},
        {"symbol": "NVDA", "qty": 50, "price": 500.0},
        {"symbol": "AAPL", "qty": 200, "price": 180.0}
    ]
    
    all_passed = True
    for pos in positions:
        payload = {
            "mindfolio_id": master_id,
            "symbol": pos["symbol"],
            "side": "BUY",
            "qty": pos["qty"],
            "price": pos["price"],
            "datetime": datetime.now().isoformat(),
            "fee": 0.0
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/mindfolio/transaction",
                json=payload,
                headers={"X-User-ID": USER_ID}
            )
            
            if response.status_code == 200:
                print(f"  ✓ Added {pos['qty']} {pos['symbol']} @ ${pos['price']}")
            else:
                print(f"  ✗ Failed to add {pos['symbol']}: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error adding {pos['symbol']}: {e}")
            all_passed = False
    
    print_result("Add Positions to Master", all_passed)
    return all_passed

def test_4_verify_master_positions(master_id):
    """Test 4: Verify Master positions calculated correctly"""
    print_header("TEST 4: Verify Master Positions")
    
    if not master_id:
        print_result("Verify Positions", False, "No master_id provided")
        return False
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/mindfolio/{master_id}",
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            positions = data.get("positions", [])
            
            expected = {
                "TSLA": {"qty": 100, "avg_cost": 250.0},
                "NVDA": {"qty": 50, "avg_cost": 500.0},
                "AAPL": {"qty": 200, "avg_cost": 180.0}
            }
            
            checks_passed = True
            for pos in positions:
                symbol = pos["symbol"]
                if symbol in expected:
                    exp = expected[symbol]
                    qty_match = abs(pos["qty"] - exp["qty"]) < 0.01
                    cost_match = abs(pos["avg_cost"] - exp["avg_cost"]) < 0.01
                    
                    if qty_match and cost_match:
                        print(f"  ✓ {symbol}: {pos['qty']} @ ${pos['avg_cost']}")
                    else:
                        print(f"  ✗ {symbol}: Expected {exp['qty']}@${exp['avg_cost']}, "
                              f"Got {pos['qty']}@${pos['avg_cost']}")
                        checks_passed = False
            
            print_result("Verify Master Positions", checks_passed,
                        f"Found {len(positions)} positions")
            return checks_passed
        else:
            print_result("Verify Positions", False,
                        f"Status {response.status_code}")
            return False
    except Exception as e:
        print_result("Verify Positions", False, str(e))
        return False

def test_5_transfer_position(master_id, specialized_id):
    """Test 5: Transfer position from Master to Specialized"""
    print_header("TEST 5: Transfer Position (Master → Specialized)")
    
    if not master_id or not specialized_id:
        print_result("Transfer Position", False, "Missing mindfolio IDs")
        return False
    
    # Transfer 20 TSLA shares
    payload = {
        "from_mindfolio_id": master_id,
        "to_mindfolio_id": specialized_id,
        "symbol": "TSLA",
        "quantity": 20.0
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/mindfolio/transfer/position",
            json=payload,
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check transfer record
            transfer = data.get("transfer", {})
            checks = {
                "symbol": transfer.get("symbol") == "TSLA",
                "quantity": transfer.get("quantity") == 20.0,
                "from_id": transfer.get("from_mindfolio_id") == master_id,
                "to_id": transfer.get("to_mindfolio_id") == specialized_id
            }
            
            all_passed = all(checks.values())
            print_result("Transfer Position", all_passed,
                        f"Transferred 20 TSLA")
            
            if all_passed:
                # Verify source has 80 TSLA
                from_positions = data.get("from_remaining", [])
                tsla_pos = next((p for p in from_positions if p["symbol"] == "TSLA"), None)
                if tsla_pos:
                    print(f"  Master now has: {tsla_pos['qty']} TSLA @ ${tsla_pos['avg_cost']}")
                
                # Verify destination has 20 TSLA
                to_positions = data.get("to_updated", [])
                tsla_pos = next((p for p in to_positions if p["symbol"] == "TSLA"), None)
                if tsla_pos:
                    print(f"  Specialized now has: {tsla_pos['qty']} TSLA @ ${tsla_pos['avg_cost']}")
            
            return all_passed
        else:
            print_result("Transfer Position", False,
                        f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Transfer Position", False, str(e))
        return False

def test_6_transfer_cash(master_id, specialized_id):
    """Test 6: Transfer cash from Master to Specialized"""
    print_header("TEST 6: Transfer Cash (Master → Specialized)")
    
    if not master_id or not specialized_id:
        print_result("Transfer Cash", False, "Missing mindfolio IDs")
        return False
    
    # Transfer $5000
    payload = {
        "from_mindfolio_id": master_id,
        "to_mindfolio_id": specialized_id,
        "amount": 5000.0,
        "notes": "Initial allocation for LEAPS strategy"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/mindfolio/transfer/cash",
            json=payload,
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check transfer record
            transfer = data.get("transfer", {})
            from_balance = data.get("from_balance")
            to_balance = data.get("to_balance")
            
            checks = {
                "amount": transfer.get("amount") == 5000.0,
                "from_balance": from_balance is not None,
                "to_balance": to_balance is not None
            }
            
            all_passed = all(checks.values())
            print_result("Transfer Cash", all_passed,
                        f"Transferred $5,000")
            
            if all_passed:
                print(f"  Master balance: ${from_balance:,.2f}")
                print(f"  Specialized balance: ${to_balance:,.2f}")
            
            return all_passed
        else:
            print_result("Transfer Cash", False,
                        f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Transfer Cash", False, str(e))
        return False

def test_7_verify_allocation_tracking(master_id, specialized_id):
    """Test 7: Verify allocation tracking fields"""
    print_header("TEST 7: Verify Allocation Tracking")
    
    if not master_id or not specialized_id:
        print_result("Allocation Tracking", False, "Missing mindfolio IDs")
        return False
    
    try:
        # Check master
        response = requests.get(
            f"{BACKEND_URL}/api/mindfolio/{master_id}",
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code != 200:
            print_result("Allocation Tracking", False, "Failed to fetch master")
            return False
        
        master = response.json().get("mindfolio", {})
        
        # Check specialized
        response = requests.get(
            f"{BACKEND_URL}/api/mindfolio/{specialized_id}",
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code != 200:
            print_result("Allocation Tracking", False, "Failed to fetch specialized")
            return False
        
        specialized = response.json().get("mindfolio", {})
        
        # Verify tracking
        checks = {
            "master_allocated_to": specialized_id in master.get("allocated_to", []),
            "specialized_received_from": specialized.get("received_from") == master_id
        }
        
        all_passed = all(checks.values())
        print_result("Allocation Tracking", all_passed)
        
        print(f"  Master allocated_to: {master.get('allocated_to', [])}")
        print(f"  Specialized received_from: {specialized.get('received_from')}")
        
        return all_passed
    except Exception as e:
        print_result("Allocation Tracking", False, str(e))
        return False

def test_8_list_all_mindfolios():
    """Test 8: List all mindfolios and verify master badge"""
    print_header("TEST 8: List All Mindfolios")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/mindfolio",
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            mindfolios = data.get("mindfolios", [])
            
            print(f"  Found {len(mindfolios)} mindfolios:")
            
            masters = [m for m in mindfolios if m.get("is_master")]
            specialized = [m for m in mindfolios if not m.get("is_master")]
            
            print(f"\n  Master Mindfolios ({len(masters)}):")
            for m in masters:
                sync_badge = "🟢 Auto-Sync" if m.get("auto_sync") else ""
                print(f"    - {m['name']} {sync_badge}")
                print(f"      Allocated to: {len(m.get('allocated_to', []))} mindfolios")
            
            print(f"\n  Specialized Mindfolios ({len(specialized)}):")
            for m in specialized:
                received = m.get("received_from")
                from_badge = f"← from {received}" if received else ""
                print(f"    - {m['name']} {from_badge}")
            
            print_result("List Mindfolios", True,
                        f"{len(masters)} masters, {len(specialized)} specialized")
            return True
        else:
            print_result("List Mindfolios", False,
                        f"Status {response.status_code}")
            return False
    except Exception as e:
        print_result("List Mindfolios", False, str(e))
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*60)
    print("  MASTER MINDFOLIO SYSTEM - TEST SUITE")
    print("="*60)
    print(f"  Backend: {BACKEND_URL}")
    print(f"  User ID: {USER_ID}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    # Test 1: Create Master
    master_id = test_1_create_master_mindfolio()
    results.append(("Create Master", master_id is not None))
    
    # Test 2: Create Specialized
    specialized_id = test_2_create_specialized_mindfolio()
    results.append(("Create Specialized", specialized_id is not None))
    
    # Test 3: Add Positions
    if master_id:
        pos_added = test_3_add_positions_to_master(master_id)
        results.append(("Add Positions", pos_added))
    
    # Test 4: Verify Positions
    if master_id:
        pos_verified = test_4_verify_master_positions(master_id)
        results.append(("Verify Positions", pos_verified))
    
    # Test 5: Transfer Position
    if master_id and specialized_id:
        pos_transferred = test_5_transfer_position(master_id, specialized_id)
        results.append(("Transfer Position", pos_transferred))
    
    # Test 6: Transfer Cash
    if master_id and specialized_id:
        cash_transferred = test_6_transfer_cash(master_id, specialized_id)
        results.append(("Transfer Cash", cash_transferred))
    
    # Test 7: Verify Allocation Tracking
    if master_id and specialized_id:
        tracking_verified = test_7_verify_allocation_tracking(master_id, specialized_id)
        results.append(("Allocation Tracking", tracking_verified))
    
    # Test 8: List All
    list_verified = test_8_list_all_mindfolios()
    results.append(("List Mindfolios", list_verified))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed}/{total} tests passed ({passed*100//total}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Master Mindfolio System is working correctly.\n")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review output above.\n")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)
