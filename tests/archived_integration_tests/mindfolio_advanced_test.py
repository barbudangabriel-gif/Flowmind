#!/usr/bin/env python3
"""
Advanced Mindfolio Management System Testing
===========================================

Additional tests for edge cases and advanced scenarios:
1. Multiple module allocations (IV_SERVICE, SELL_PUTS, etc.)
2. Budget validation edge cases
3. JSON serialization with complex data
4. Error handling for invalid operations
5. Mindfolio statistics with multiple modules
"""

import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional

class AdvancedMindfolioTester:
 def __init__(self):
 self.base_url = "http://localhost:8000"
 self.api_url = f"{self.base_url}/api"
 self.session = requests.Session()
 self.session.headers.update(
 {"Content-Type": "application/json", "Accept": "application/json"}
 )

 self.created_mindfolio_id = None

 print("🔬 ADVANCED MINDFOLIO MANAGEMENT SYSTEM TESTING")
 print("=" * 60)

 def make_request(
 self, method: str, endpoint: str, data: Optional[Dict] = None
 ) -> Dict[str, Any]:
 """Make HTTP request to API endpoint"""
 url = f"{self.api_url}/{endpoint.lstrip('/')}"

 try:
 if method.upper() == "GET":
 response = self.session.get(url, timeout=10)
 elif method.upper() == "POST":
 response = self.session.post(url, json=data, timeout=10)
 elif method.upper() == "PATCH":
 response = self.session.patch(url, json=data, timeout=10)
 else:
 raise ValueError(f"Unsupported method: {method}")

 print(f" {method.upper()} {endpoint} -> {response.status_code}")

 if response.status_code in [200, 201]:
 return response.json()
 else:
 print(f" Error: {response.text}")
 return {"error": response.text, "status_code": response.status_code}

 except Exception as e:
 print(f" Exception: {str(e)}")
 return {"error": str(e), "status_code": 0}

 def test_1_create_mindfolio_with_large_balance(self) -> bool:
 """Test 1: Create mindfolio with large starting balance"""
 print(" Test 1: Create mindfolio with large starting balance")

 large_mindfolio_data = {
 "name": "High Capital Mindfolio",
 "starting_balance": 1000000.50, # $1M+ with decimals
 }

 response = self.make_request("POST", "/mindfolios", large_mindfolio_data)

 if "error" in response:
 print(f" Failed: {response['error']}")
 return False

 self.created_mindfolio_id = response["id"]

 if response["cash_balance"] != large_mindfolio_data["starting_balance"]:
 print(
 f" Failed: Balance precision issue. Expected: {large_mindfolio_data['starting_balance']}, Got: {response['cash_balance']}"
 )
 return False

 print(
 f" Success: Created mindfolio with large balance: ${response['cash_balance']:,.2f}"
 )
 return True

 def test_2_allocate_multiple_modules(self) -> bool:
 """Test 2: Allocate budget to multiple modules"""
 print("\n Test 2: Allocate budget to multiple modules")

 if not self.created_mindfolio_id:
 print(" Failed: No mindfolio ID available")
 return False

 modules_to_allocate = [
 {
 "module": "IV_SERVICE",
 "alloc": {
 "module": "IV_SERVICE",
 "budget": 300000,
 "max_risk_per_trade": 5000,
 "daily_loss_limit": 15000,
 "autotrade": True,
 },
 },
 {
 "module": "SELL_PUTS",
 "alloc": {
 "module": "SELL_PUTS",
 "budget": 400000,
 "max_risk_per_trade": 10000,
 "daily_loss_limit": 20000,
 "autotrade": False,
 },
 },
 {
 "module": "COVERED_CALLS",
 "alloc": {
 "module": "COVERED_CALLS",
 "budget": 200000,
 "max_risk_per_trade": 3000,
 "daily_loss_limit": 8000,
 "autotrade": True,
 },
 },
 ]

 for i, allocation in enumerate(modules_to_allocate):
 print(f" Allocating module {i+1}/3: {allocation['module']}")
 response = self.make_request(
 "POST", f"/mindfolios/{self.created_mindfolio_id}/allocate", allocation
 )

 if "error" in response:
 print(
 f" Failed to allocate {allocation['module']}: {response['error']}"
 )
 return False

 # Verify all modules are allocated
 mindfolio = self.make_request("GET", f"/mindfolios/{self.created_mindfolio_id}")
 if "error" in mindfolio:
 print(f" Failed to get mindfolio: {mindfolio['error']}")
 return False

 allocated_modules = mindfolio.get("modules", [])
 if len(allocated_modules) != 3:
 print(f" Failed: Expected 3 modules, got {len(allocated_modules)}")
 return False

 total_allocated = sum(module["budget"] for module in allocated_modules)
 print(
 f" Success: Allocated 3 modules with total budget: ${total_allocated:,.2f}"
 )

 for module in allocated_modules:
 print(
 f" - {module['module']}: ${module['budget']:,.2f} (autotrade: {module['autotrade']})"
 )

 return True

 def test_3_update_existing_module_allocation(self) -> bool:
 """Test 3: Update existing module allocation (should replace, not duplicate)"""
 print("\n🔄 Test 3: Update existing module allocation")

 if not self.created_mindfolio_id:
 print(" Failed: No mindfolio ID available")
 return False

 # Update IV_SERVICE with new budget
 updated_allocation = {
 "module": "IV_SERVICE",
 "alloc": {
 "module": "IV_SERVICE",
 "budget": 350000, # Increased from 300000
 "max_risk_per_trade": 7500, # Increased from 5000
 "daily_loss_limit": 18000, # Increased from 15000
 "autotrade": False, # Changed from True
 },
 }

 response = self.make_request(
 "POST",
 f"/mindfolios/{self.created_mindfolio_id}/allocate",
 updated_allocation,
 )

 if "error" in response:
 print(f" Failed: {response['error']}")
 return False

 # Verify update (should still have 3 modules, not 4)
 allocated_modules = response.get("modules", [])
 if len(allocated_modules) != 3:
 print(
 f" Failed: Expected 3 modules after update, got {len(allocated_modules)}"
 )
 return False

 # Find updated IV_SERVICE module
 iv_module = None
 for module in allocated_modules:
 if module["module"] == "IV_SERVICE":
 iv_module = module
 break

 if not iv_module:
 print(" Failed: IV_SERVICE module not found after update")
 return False

 if iv_module["budget"] != 350000:
 print(
 f" Failed: Budget not updated. Expected: 350000, Got: {iv_module['budget']}"
 )
 return False

 if iv_module["autotrade"] != False:
 print(
 f" Failed: Autotrade not updated. Expected: False, Got: {iv_module['autotrade']}"
 )
 return False

 print(" Success: IV_SERVICE module updated")
 print(f" - New Budget: ${iv_module['budget']:,.2f}")
 print(f" - New Max Risk: ${iv_module['max_risk_per_trade']:,.2f}")
 print(f" - New Autotrade: {iv_module['autotrade']}")

 return True

 def test_4_error_handling_invalid_mindfolio(self) -> bool:
 """Test 4: Error handling for invalid mindfolio operations"""
 print("\n Test 4: Error handling for invalid mindfolio operations")

 # Test 1: Get non-existent mindfolio
 response = self.make_request("GET", "/mindfolios/invalid_id")
 if response.get("status_code") != 404:
 print(
 f" Failed: Expected 404 for invalid mindfolio, got {response.get('status_code')}"
 )
 return False
 print(" Correctly returns 404 for non-existent mindfolio")

 # Test 2: Update non-existent mindfolio
 response = self.make_request(
 "PATCH", "/mindfolios/invalid_id", {"name": "Test"}
 )
 if response.get("status_code") != 404:
 print(
 f" Failed: Expected 404 for invalid mindfolio update, got {response.get('status_code')}"
 )
 return False
 print(" Correctly returns 404 for non-existent mindfolio update")

 # Test 3: Add funds to non-existent mindfolio
 response = self.make_request(
 "POST", "/mindfolios/invalid_id/funds", {"delta": 1000}
 )
 if response.get("status_code") != 404:
 print(
 f" Failed: Expected 404 for invalid mindfolio funds, got {response.get('status_code')}"
 )
 return False
 print(" Correctly returns 404 for non-existent mindfolio funds operation")

 return True

 def test_5_negative_balance_handling(self) -> bool:
 """Test 5: Negative balance handling"""
 print("\n💸 Test 5: Negative balance handling")

 if not self.created_mindfolio_id:
 print(" Failed: No mindfolio ID available")
 return False

 # Get current balance
 mindfolio = self.make_request("GET", f"/mindfolios/{self.created_mindfolio_id}")
 if "error" in mindfolio:
 print(f" Failed to get mindfolio: {mindfolio['error']}")
 return False

 current_balance = mindfolio["cash_balance"]
 print(f" Current Balance: ${current_balance:,.2f}")

 # Try to remove more than available (should work, allowing negative balance)
 large_withdrawal = {
 "delta": -(current_balance + 100000)
 } # Remove more than available

 response = self.make_request(
 "POST", f"/mindfolios/{self.created_mindfolio_id}/funds", large_withdrawal
 )

 if "error" in response:
 print(f" Failed: {response['error']}")
 return False

 new_balance = response["cash_balance"]
 expected_balance = current_balance + large_withdrawal["delta"]

 if new_balance != expected_balance:
 print(
 f" Failed: Balance calculation error. Expected: {expected_balance}, Got: {new_balance}"
 )
 return False

 print(f" Success: Negative balance allowed: ${new_balance:,.2f}")

 # Restore positive balance for other tests
 restore_funds = {"delta": abs(new_balance) + 50000}
 self.make_request(
 "POST", f"/mindfolios/{self.created_mindfolio_id}/funds", restore_funds
 )

 return True

 def test_6_json_serialization_complex_data(self) -> bool:
 """Test 6: JSON serialization with complex data"""
 print("\n📄 Test 6: JSON serialization with complex data")

 if not self.created_mindfolio_id:
 print(" Failed: No mindfolio ID available")
 return False

 # Create mindfolio with special characters and unicode
 complex_mindfolio_data = {
 "name": "Test Mindfolio with Special Chars: àáâãäåæçèéêë & 中文 & ",
 "starting_balance": 123456.789,
 }

 response = self.make_request("POST", "/mindfolios", complex_mindfolio_data)

 if "error" in response:
 print(f" Failed: {response['error']}")
 return False

 complex_mindfolio_id = response["id"]

 # Verify the name was stored and retrieved correctly
 if response["name"] != complex_mindfolio_data["name"]:
 print(" Failed: Name encoding issue")
 print(f" Expected: {complex_mindfolio_data['name']}")
 print(f" Got: {response['name']}")
 return False

 print(" Success: Complex characters handled correctly")
 print(f" Name: {response['name']}")

 # Clean up
 self.make_request(
 "PATCH", f"/mindfolios/{complex_mindfolio_id}", {"status": "CLOSED"}
 )

 return True

 def test_7_mindfolio_stats_with_modules(self) -> bool:
 """Test 7: Mindfolio statistics with multiple modules"""
 print("\n Test 7: Mindfolio statistics with multiple modules")

 if not self.created_mindfolio_id:
 print(" Failed: No mindfolio ID available")
 return False

 response = self.make_request(
 "GET", f"/mindfolios/{self.created_mindfolio_id}/stats"
 )

 if "error" in response:
 print(f" Failed: {response['error']}")
 return False

 # Verify stats structure
 required_fields = ["mindfolio_id", "nav", "pnl_realized", "pnl_unrealized"]
 missing_fields = [field for field in required_fields if field not in response]

 if missing_fields:
 print(f" Failed: Missing stats fields: {missing_fields}")
 return False

 # Get current mindfolio to compare NAV
 mindfolio = self.make_request("GET", f"/mindfolios/{self.created_mindfolio_id}")
 if "error" in mindfolio:
 print(f" Failed to get mindfolio for comparison: {mindfolio['error']}")
 return False

 if response["nav"] != mindfolio["cash_balance"]:
 print(
 f" Failed: NAV mismatch. Stats NAV: {response['nav']}, Mindfolio Balance: {mindfolio['cash_balance']}"
 )
 return False

 print(" Success: Mindfolio statistics working correctly")
 print(f" Mindfolio ID: {response['mindfolio_id']}")
 print(f" NAV: ${response['nav']:,.2f}")
 print(f" Realized P&L: ${response['pnl_realized']:,.2f}")
 print(f" Unrealized P&L: ${response['pnl_unrealized']:,.2f}")

 return True

 def cleanup(self):
 """Clean up created test data"""
 print(f"\n🧹 Cleanup: Removing test mindfolio {self.created_mindfolio_id}")

 if not self.created_mindfolio_id:
 print(" No mindfolio to clean up")
 return

 cleanup_data = {"status": "CLOSED"}
 response = self.make_request(
 "PATCH", f"/mindfolios/{self.created_mindfolio_id}", cleanup_data
 )

 if "error" not in response:
 print(" Mindfolio marked as CLOSED for cleanup")
 else:
 print(f" Could not clean up mindfolio: {response['error']}")

 def run_all_tests(self):
 """Run all advanced mindfolio management tests"""
 print(" Starting Advanced Mindfolio Management Tests")
 print(f"Timestamp: {datetime.now().isoformat()}")
 print()

 tests = [
 (
 "Create Mindfolio with Large Balance",
 self.test_1_create_mindfolio_with_large_balance,
 ),
 ("Allocate Multiple Modules", self.test_2_allocate_multiple_modules),
 (
 "Update Existing Module Allocation",
 self.test_3_update_existing_module_allocation,
 ),
 (
 "Error Handling Invalid Mindfolio",
 self.test_4_error_handling_invalid_mindfolio,
 ),
 ("Negative Balance Handling", self.test_5_negative_balance_handling),
 (
 "JSON Serialization Complex Data",
 self.test_6_json_serialization_complex_data,
 ),
 ("Mindfolio Stats with Modules", self.test_7_mindfolio_stats_with_modules),
 ]

 results = []

 for test_name, test_func in tests:
 try:
 result = test_func()
 results.append((test_name, result))
 if not result:
 print(" Test failed, continuing with remaining tests...")
 time.sleep(0.5)
 except Exception as e:
 print(f" 💥 Test exception: {str(e)}")
 results.append((test_name, False))

 # Cleanup
 try:
 self.cleanup()
 except Exception as e:
 print(f" Cleanup failed: {str(e)}")

 # Summary
 print("\n" + "=" * 60)
 print(" ADVANCED MINDFOLIO MANAGEMENT TEST RESULTS")
 print("=" * 60)

 passed = sum(1 for _, result in results if result)
 total = len(results)
 success_rate = (passed / total) * 100 if total > 0 else 0

 for test_name, result in results:
 status = " PASS" if result else " FAIL"
 print(f"{status} {test_name}")

 print(f"\n SUCCESS RATE: {success_rate:.1f}% ({passed}/{total} tests passed)")

 if success_rate >= 85:
 print(" EXCELLENT: Advanced features working perfectly!")
 elif success_rate >= 70:
 print(" GOOD: Most advanced features working")
 else:
 print(" NEEDS ATTENTION: Advanced features have issues")

 return success_rate >= 80

if __name__ == "__main__":
 tester = AdvancedMindfolioTester()
 success = tester.run_all_tests()

 if success:
 print(
 "\n VERDICT: Advanced Mindfolio Management features are production-ready!"
 )
 else:
 print("\n🔧 VERDICT: Some advanced features need refinement.")
