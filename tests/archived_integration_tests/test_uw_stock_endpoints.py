#!/usr/bin/env python3
"""
Deep dive into stock-related endpoints that might work
We found /api/stock/TSLA/greeks works, so test similar patterns
"""
import requests
import json

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE_URL = "https://api.unusualwhales.com/api"

# Comprehensive stock endpoint tests
STOCK_ENDPOINTS = [
    # Greeks variations
    {"path": "/stock/TSLA/greeks", "params": {}},
    {"path": "/stock/TSLA/greeks-flow", "params": {}},
    {"path": "/stock/TSLA/greeks-flow-expiry", "params": {}},
    
    # Options data
    {"path": "/stock/TSLA/options", "params": {}},
    {"path": "/stock/TSLA/option-contracts", "params": {}},
    {"path": "/stock/TSLA/option-chain", "params": {}},
    
    # Flow data
    {"path": "/stock/TSLA/flow", "params": {}},
    {"path": "/stock/TSLA/options-flow", "params": {}},
    {"path": "/stock/TSLA/flow-summary", "params": {}},
    
    # Volume and activity
    {"path": "/stock/TSLA/volume", "params": {}},
    {"path": "/stock/TSLA/activity", "params": {}},
    {"path": "/stock/TSLA/unusual-activity", "params": {}},
    
    # Greeks and exposures
    {"path": "/stock/TSLA/gamma", "params": {}},
    {"path": "/stock/TSLA/gamma-exposure", "params": {}},
    {"path": "/stock/TSLA/spot-gamma", "params": {}},
    {"path": "/stock/TSLA/spot-exposures", "params": {}},
    
    # Market data
    {"path": "/stock/TSLA/price", "params": {}},
    {"path": "/stock/TSLA/snapshot", "params": {}},
    {"path": "/stock/TSLA/real-time", "params": {}},
    
    # Historical
    {"path": "/stock/TSLA/historical", "params": {}},
    {"path": "/stock/TSLA/history", "params": {}},
    
    # Info
    {"path": "/stock/TSLA/info", "params": {}},
    {"path": "/stock/TSLA/details", "params": {}},
]

# Non-stock endpoints that might work
OTHER_ENDPOINTS = [
    # Market
    {"path": "/market", "params": {}},
    {"path": "/market/summary", "params": {}},
    {"path": "/market/status", "params": {}},
    
    # General flow
    {"path": "/flow", "params": {}},
    {"path": "/activity", "params": {}},
    {"path": "/unusual", "params": {}},
    
    # Tickers list
    {"path": "/tickers", "params": {}},
    {"path": "/stocks", "params": {}},
    {"path": "/symbols", "params": {}},
]

def test_endpoint(path, params):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=5)
        has_data = False
        data_preview = ""
        
        if response.status_code == 200:
            try:
                data = response.json()
                has_data = bool(data.get('data') or data)
                data_preview = str(data)[:100]
            except:
                pass
        
        return {
            "status": response.status_code,
            "success": response.status_code == 200,
            "has_data": has_data,
            "preview": data_preview if has_data else response.text[:80]
        }
    except Exception as e:
        return {"status": None, "success": False, "has_data": False, "error": str(e)[:80]}

def main():
    print("=" * 80)
    print("DEEP DIVE: UW API STOCK ENDPOINTS")
    print("=" * 80)
    print(f"Testing {len(STOCK_ENDPOINTS)} stock endpoints + {len(OTHER_ENDPOINTS)} other...")
    print()
    
    working = []
    working_with_data = []
    
    print("\n📊 STOCK ENDPOINTS:")
    print("-" * 80)
    for ep in STOCK_ENDPOINTS:
        result = test_endpoint(ep['path'], ep['params'])
        
        icon = "✅" if result['success'] else "❌"
        data_icon = "📦" if result.get('has_data') else "  "
        
        print(f"{icon}{data_icon} [{result['status'] or 'ERR'}] {ep['path']}")
        
        if result['success']:
            working.append(ep['path'])
            if result.get('has_data'):
                working_with_data.append(ep['path'])
                print(f"      → {result.get('preview', '')}")
    
    print("\n\n🌐 OTHER ENDPOINTS:")
    print("-" * 80)
    for ep in OTHER_ENDPOINTS:
        result = test_endpoint(ep['path'], ep['params'])
        
        icon = "✅" if result['success'] else "❌"
        data_icon = "📦" if result.get('has_data') else "  "
        
        print(f"{icon}{data_icon} [{result['status'] or 'ERR'}] {ep['path']}")
        
        if result['success']:
            working.append(ep['path'])
            if result.get('has_data'):
                working_with_data.append(ep['path'])
                print(f"      → {result.get('preview', '')}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Working endpoints: {len(working)}")
    print(f"📦 Endpoints with data: {len(working_with_data)}")
    
    if working:
        print("\n✅ ALL WORKING ENDPOINTS:")
        for path in working:
            data_mark = "📦" if path in working_with_data else "  "
            print(f"  {data_mark} {BASE_URL}{path}")
        
        # Save
        result = {
            "working_endpoints": working,
            "endpoints_with_data": working_with_data,
            "base_url": BASE_URL,
            "auth": "Bearer token in Authorization header"
        }
        
        with open('/workspaces/Flowmind/uw_discovered_endpoints.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Saved to: uw_discovered_endpoints.json")

if __name__ == "__main__":
    main()
