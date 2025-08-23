#!/usr/bin/env python3
"""
TradeStation Balances API Test
Focus: Test TradeStation balances API to find "Cash available to withdraw" field
"""

import requests
import json
import sys
from datetime import datetime

class TradeStationBalancesAPITester:
    def __init__(self, base_url="https://put-selling-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.account_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            timeout = 30
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

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
            print(f"❌ Failed - Request timeout ({timeout}s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_tradestation_accounts(self):
        """Test GET /api/tradestation/accounts - get account ID"""
        print("\n🏛️ PHASE 1: GET TRADESTATION ACCOUNTS")
        print("=" * 60)
        print("🎯 OBJECTIVE: Get account ID for balances testing")
        
        success, accounts_data = self.run_test(
            "TradeStation Accounts", 
            "GET", 
            "tradestation/accounts", 
            200
        )
        
        if not success:
            print("❌ CRITICAL: Cannot get TradeStation accounts")
            return False, None
        
        # Analyze accounts response
        print(f"\n📊 ACCOUNTS RESPONSE ANALYSIS:")
        print(f"   Response Type: {type(accounts_data)}")
        print(f"   Response Keys: {list(accounts_data.keys()) if isinstance(accounts_data, dict) else 'Not a dict'}")
        
        # Look for accounts in different possible structures
        accounts = None
        if isinstance(accounts_data, dict):
            if 'accounts' in accounts_data:
                accounts = accounts_data['accounts']
                print(f"   ✅ Found 'accounts' field with {len(accounts)} accounts")
            elif 'data' in accounts_data and isinstance(accounts_data['data'], list):
                accounts = accounts_data['data']
                print(f"   ✅ Found 'data' field with {len(accounts)} accounts")
            elif isinstance(accounts_data, dict) and 'account' in str(accounts_data).lower():
                # Try to find account-like data
                for key, value in accounts_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        accounts = value
                        print(f"   ✅ Found accounts in '{key}' field with {len(accounts)} accounts")
                        break
        elif isinstance(accounts_data, list):
            accounts = accounts_data
            print(f"   ✅ Response is direct list with {len(accounts)} accounts")
        
        if not accounts or len(accounts) == 0:
            print("❌ CRITICAL: No accounts found in response")
            print(f"   Full Response: {json.dumps(accounts_data, indent=2)}")
            return False, None
        
        # Find suitable account for testing
        target_account = None
        print(f"\n📋 ACCOUNT ANALYSIS:")
        
        for i, account in enumerate(accounts):
            if isinstance(account, dict):
                account_id = account.get('AccountID') or account.get('account_id') or account.get('id')
                account_type = account.get('TypeDescription') or account.get('type') or account.get('account_type')
                status = account.get('Status') or account.get('status')
                
                print(f"   Account {i+1}:")
                print(f"     - ID: {account_id}")
                print(f"     - Type: {account_type}")
                print(f"     - Status: {status}")
                
                # Prefer Margin accounts for balances testing
                if account_id and (not target_account or 'margin' in str(account_type).lower()):
                    target_account = account_id
                    print(f"     ✅ Selected for balances testing")
                else:
                    print(f"     - Available for testing")
        
        if target_account:
            print(f"\n🎯 SELECTED ACCOUNT: {target_account}")
            self.account_id = target_account
            return True, target_account
        else:
            print("❌ CRITICAL: No suitable account found for balances testing")
            return False, None

    def test_tradestation_balances(self, account_id):
        """Test GET /api/tradestation/accounts/{account_id}/balances - check exact balance fields"""
        print(f"\n💰 PHASE 2: GET TRADESTATION ACCOUNT BALANCES")
        print("=" * 60)
        print(f"🎯 OBJECTIVE: Check exact balance fields for account {account_id}")
        print(f"🔍 FOCUS: Find 'Cash available to withdraw' field or equivalent")
        
        success, balances_data = self.run_test(
            f"TradeStation Balances (Account: {account_id})", 
            "GET", 
            f"tradestation/accounts/{account_id}/balances", 
            200
        )
        
        if not success:
            print(f"❌ CRITICAL: Cannot get balances for account {account_id}")
            return False
        
        # Comprehensive balance field analysis
        print(f"\n📊 BALANCES RESPONSE ANALYSIS:")
        print(f"   Response Type: {type(balances_data)}")
        
        # Pretty print the full response for analysis
        print(f"\n📋 FULL BALANCES RESPONSE:")
        print("=" * 40)
        print(json.dumps(balances_data, indent=2))
        print("=" * 40)
        
        # Extract balance fields
        balance_fields = {}
        cash_fields = {}
        
        def extract_fields(data, prefix=""):
            """Recursively extract all fields from the response"""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    # Check if this looks like a cash/balance field
                    key_lower = key.lower()
                    if any(term in key_lower for term in ['cash', 'available', 'withdraw', 'balance', 'buying', 'power']):
                        cash_fields[full_key] = value
                    
                    balance_fields[full_key] = value
                    
                    # Recurse into nested objects
                    if isinstance(value, dict):
                        extract_fields(value, full_key)
                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        for i, item in enumerate(value):
                            extract_fields(item, f"{full_key}[{i}]")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    extract_fields(item, f"{prefix}[{i}]" if prefix else f"[{i}]")
        
        extract_fields(balances_data)
        
        print(f"\n🔍 BALANCE FIELD ANALYSIS:")
        print(f"   Total Fields Found: {len(balance_fields)}")
        print(f"   Cash-Related Fields: {len(cash_fields)}")
        
        # Display all fields
        print(f"\n📋 ALL BALANCE FIELDS:")
        for field, value in balance_fields.items():
            field_type = type(value).__name__
            if isinstance(value, (int, float)):
                print(f"   {field}: {value} ({field_type})")
            elif isinstance(value, str):
                print(f"   {field}: '{value}' ({field_type})")
            else:
                print(f"   {field}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''} ({field_type})")
        
        # Focus on cash-related fields
        print(f"\n💰 CASH-RELATED FIELDS ANALYSIS:")
        if cash_fields:
            for field, value in cash_fields.items():
                print(f"   🔍 {field}: {value}")
                
                # Check if this could be "Cash available to withdraw"
                field_lower = field.lower()
                if 'available' in field_lower and ('cash' in field_lower or 'withdraw' in field_lower):
                    print(f"     ⭐ POTENTIAL MATCH: This could be 'Cash available to withdraw'")
                elif 'cash' in field_lower and 'available' in field_lower:
                    print(f"     ⭐ POTENTIAL MATCH: This could be 'Cash available to withdraw'")
                elif 'buying' in field_lower and 'power' in field_lower:
                    print(f"     💡 RELATED: This is buying power (may include cash available)")
                elif 'cash' in field_lower and 'balance' in field_lower:
                    print(f"     💡 RELATED: This is cash balance")
        else:
            print("   ❌ No cash-related fields found")
        
        # Look for specific patterns
        print(f"\n🎯 SPECIFIC FIELD PATTERN SEARCH:")
        
        # Common field names for cash available to withdraw
        target_patterns = [
            'cash_available_to_withdraw',
            'cashAvailableToWithdraw',
            'CashAvailableToWithdraw',
            'available_cash',
            'availableCash',
            'AvailableCash',
            'cash_available',
            'cashAvailable',
            'CashAvailable',
            'withdrawable_cash',
            'withdrawableCash',
            'WithdrawableCash'
        ]
        
        found_patterns = []
        for pattern in target_patterns:
            for field in balance_fields.keys():
                if pattern.lower() in field.lower():
                    found_patterns.append((pattern, field, balance_fields[field]))
        
        if found_patterns:
            print("   ✅ FOUND MATCHING PATTERNS:")
            for pattern, field, value in found_patterns:
                print(f"     - Pattern '{pattern}' matches field '{field}': {value}")
        else:
            print("   ❌ No exact pattern matches found")
        
        # Check for nested balance objects
        print(f"\n🔍 NESTED BALANCE OBJECT ANALYSIS:")
        nested_balance_objects = []
        
        for field, value in balance_fields.items():
            if isinstance(value, dict) and len(value) > 3:  # Likely a balance object
                nested_balance_objects.append((field, value))
        
        if nested_balance_objects:
            print("   ✅ FOUND NESTED BALANCE OBJECTS:")
            for field, obj in nested_balance_objects:
                print(f"     - {field}: {len(obj)} properties")
                for key, val in obj.items():
                    if isinstance(val, (int, float)):
                        print(f"       • {key}: {val}")
        else:
            print("   ❌ No nested balance objects found")
        
        # Summary and recommendations
        print(f"\n📊 SUMMARY AND RECOMMENDATIONS:")
        
        if cash_fields:
            print(f"   ✅ Found {len(cash_fields)} cash-related fields")
            
            # Recommend the most likely field
            best_candidates = []
            for field, value in cash_fields.items():
                score = 0
                field_lower = field.lower()
                
                if 'available' in field_lower:
                    score += 3
                if 'cash' in field_lower:
                    score += 2
                if 'withdraw' in field_lower:
                    score += 3
                if isinstance(value, (int, float)) and value > 0:
                    score += 1
                
                best_candidates.append((score, field, value))
            
            best_candidates.sort(reverse=True)
            
            if best_candidates:
                print(f"\n🏆 BEST CANDIDATES FOR 'Cash available to withdraw':")
                for i, (score, field, value) in enumerate(best_candidates[:3]):
                    print(f"   #{i+1} (Score: {score}): {field} = {value}")
                    if i == 0:
                        print(f"        ⭐ RECOMMENDED: Use this field for 'Cash available to withdraw'")
        else:
            print(f"   ❌ No cash-related fields found - API may not provide balance details")
        
        return len(cash_fields) > 0

    def run_comprehensive_test(self):
        """Run comprehensive TradeStation balances API test"""
        print("🏛️ TRADESTATION BALANCES API COMPREHENSIVE TEST")
        print("=" * 80)
        print("🎯 OBJECTIVE: Find 'Cash available to withdraw' field in TradeStation balances API")
        print("📋 TEST PLAN:")
        print("   1. GET /api/tradestation/accounts - get account ID")
        print("   2. GET /api/tradestation/accounts/{account_id}/balances - check exact balance fields")
        print("🔍 FOCUS: Identify exact field names for cash available to withdraw")
        
        # Phase 1: Get accounts
        accounts_success, account_id = self.test_tradestation_accounts()
        
        if not accounts_success or not account_id:
            print("\n❌ CRITICAL FAILURE: Cannot proceed without account ID")
            return False
        
        # Phase 2: Get balances
        balances_success = self.test_tradestation_balances(account_id)
        
        # Final summary
        print(f"\n🎯 FINAL TEST SUMMARY:")
        print("=" * 60)
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   Account ID Found: {'✅ Yes' if account_id else '❌ No'}")
        print(f"   Balances API Working: {'✅ Yes' if balances_success else '❌ No'}")
        
        if accounts_success and balances_success:
            print(f"\n🎉 SUCCESS: TradeStation balances API is accessible")
            print(f"   ✅ Account ID: {account_id}")
            print(f"   ✅ Balances endpoint responds with data")
            print(f"   📊 Check the detailed field analysis above to identify the correct field name")
            print(f"   💡 Look for fields containing 'available', 'cash', or 'withdraw' in the name")
        else:
            print(f"\n❌ FAILURE: TradeStation balances API test failed")
            if not accounts_success:
                print(f"   ❌ Cannot get account information")
            if not balances_success:
                print(f"   ❌ Cannot get balance information")
        
        return accounts_success and balances_success

if __name__ == "__main__":
    print("🚀 Starting TradeStation Balances API Test...")
    
    tester = TradeStationBalancesAPITester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)