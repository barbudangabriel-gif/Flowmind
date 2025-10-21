#!/usr/bin/env python3
"""
Test alternative UW API endpoint structures
The /api/alerts works, so let's try different path patterns
"""
import requests
import json

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Different base URL patterns to test
BASE_URLS = [
    "https://api.unusualwhales.com/api",
    "https://api.unusualwhales.com",
    "https://api.unusualwhales.com/v2",
]

# Endpoints to test with different patterns
TEST_CASES = [
    # Options Flow
    {"name": "Flow Alerts v1", "path": "/flow-alerts", "params": {"ticker": "TSLA"}},
    {"name": "Options Flow", "path": "/options-flow", "params": {"ticker": "TSLA"}},
    {"name": "Flow", "path": "/flow", "params": {"ticker": "TSLA"}},
    
    # Stock Data
    {"name": "Stock Quote", "path": "/stock/TSLA/quote", "params": {}},
    {"name": "Stock Last State", "path": "/stock/TSLA/last-state", "params": {}},
    {"name": "Stock Info", "path": "/stock/TSLA", "params": {}},
    {"name": "Quote TSLA", "path": "/quote/TSLA", "params": {}},
    
    # Market Data
    {"name": "Market Tide", "path": "/market/tide", "params": {}},
    {"name": "Market Overview", "path": "/market/overview", "params": {}},
    {"name": "Tide", "path": "/tide", "params": {}},
    
    # Options specific
    {"name": "Options Chain", "path": "/options-chain/TSLA", "params": {}},
    {"name": "Chain TSLA", "path": "/chain/TSLA", "params": {}},
    {"name": "GEX", "path": "/stock/TSLA/gex", "params": {}},
    {"name": "Greeks", "path": "/stock/TSLA/greeks", "params": {}},
]

def test_url(base_url, endpoint, params):
    """Test a single URL"""
    url = f"{base_url}{endpoint['path']}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=5)
        return {
            "status": response.status_code,
            "success": response.status_code == 200,
            "url": url,
            "response": response.text[:100] if response.status_code != 200 else "OK"
        }
    except Exception as e:
        return {"status": None, "success": False, "url": url, "error": str(e)}

def main():
    print("=" * 80)
    print("TESTING ALTERNATIVE UW API ENDPOINT PATTERNS")
    print("=" * 80)
    print()
    
    working = []
    
    for base_url in BASE_URLS:
        print(f"\n{'=' * 80}")
        print(f"BASE URL: {base_url}")
        print('=' * 80)
        
        for test_case in TEST_CASES:
            result = test_url(base_url, test_case, test_case['params'])
            
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {test_case['name']:<25} [{result['status']}] {test_case['path']}")
            
            if result['success']:
                working.append({
                    "name": test_case['name'],
                    "base_url": base_url,
                    "path": test_case['path'],
                    "full_url": result['url']
                })
    
    print("\n" + "=" * 80)
    print("WORKING ENDPOINTS")
    print("=" * 80)
    
    if working:
        for w in working:
            print(f"✅ {w['name']}")
            print(f"   {w['full_url']}")
            print()
        
        print(f"\nTotal working: {len(working)}")
        
        # Save configuration
        with open('/workspaces/Flowmind/uw_working_endpoints.json', 'w') as f:
            json.dump(working, f, indent=2)
        print("\n✅ Saved to: uw_working_endpoints.json")
    else:
        print("❌ No working endpoints found")
        print("\nRecommendation: Check UW API documentation for correct endpoint structure")

if __name__ == "__main__":
    main()
