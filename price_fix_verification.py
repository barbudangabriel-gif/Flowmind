#!/usr/bin/env python3
"""
Quick verification test for the price fix
"""

import requests
import json
import time

def test_price_fix():
    base_url = "https://chart-repair-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 TESTING PRICE FIX...")
    print("="*60)
    
    # Test 1: Start a new scan to get fresh data with the fix
    print("\n1. Starting new scan...")
    try:
        response = requests.post(f"{api_url}/scanner/start-scan", timeout=30)
        if response.status_code == 200:
            print("✅ New scan started successfully")
        else:
            print(f"❌ Failed to start scan: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting scan: {e}")
        return False
    
    # Wait for scan to process
    print("\n2. Waiting 20 seconds for scan to process...")
    time.sleep(20)
    
    # Test 2: Check top stocks for prices
    print("\n3. Checking top stocks for prices...")
    try:
        response = requests.get(f"{api_url}/scanner/top-stocks?limit=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            top_stocks = data.get('top_stocks', [])
            
            print(f"📊 Found {len(top_stocks)} stocks")
            
            valid_prices = 0
            na_prices = 0
            
            for i, stock in enumerate(top_stocks[:5]):
                ticker = stock.get('ticker', 'N/A')
                price = stock.get('price', 'MISSING')
                score = stock.get('score', 'N/A')
                
                print(f"\n   Stock #{i+1}: {ticker}")
                print(f"   - Score: {score}")
                print(f"   - Price: {price}")
                
                if price == 'N/A':
                    na_prices += 1
                    print(f"   ❌ Still showing N/A")
                elif isinstance(price, (int, float)) and price > 0:
                    valid_prices += 1
                    print(f"   ✅ Valid price: ${price:.2f}")
                else:
                    print(f"   ⚠️  Unexpected price format: {price}")
            
            print(f"\n📊 RESULTS:")
            print(f"   - Valid prices: {valid_prices}")
            print(f"   - N/A prices: {na_prices}")
            
            if valid_prices > 0:
                print(f"\n🎉 SUCCESS: Price fix is working! {valid_prices} stocks now have valid prices")
                return True
            else:
                print(f"\n❌ ISSUE: All prices still showing N/A")
                return False
                
        else:
            print(f"❌ Failed to get top stocks: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting top stocks: {e}")
        return False

if __name__ == "__main__":
    success = test_price_fix()
    if success:
        print(f"\n✅ Price fix verification PASSED")
    else:
        print(f"\n❌ Price fix verification FAILED")