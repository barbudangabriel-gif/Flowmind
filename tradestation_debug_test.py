#!/usr/bin/env python3
"""
TradeStation Debug Test - Examine actual response data
"""

import requests
import json
from datetime import datetime

def debug_tradestation_endpoints():
    base_url = "https://options-trader-6.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 TRADESTATION DEBUG TEST")
    print("=" * 60)
    
    # Test 1: Accounts endpoint
    print("\n📊 Testing /api/tradestation/accounts")
    try:
        response = requests.get(f"{api_url}/tradestation/accounts", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Response Sample: {json.dumps(data, indent=2)[:1000]}...")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Positions endpoint
    print(f"\n📊 Testing /api/tradestation/accounts/11775499/positions")
    try:
        response = requests.get(f"{api_url}/tradestation/accounts/11775499/positions", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Response Sample: {json.dumps(data, indent=2)[:1000]}...")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Auth status
    print(f"\n🔐 Testing /api/auth/tradestation/status")
    try:
        response = requests.get(f"{api_url}/auth/tradestation/status", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Full Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_tradestation_endpoints()