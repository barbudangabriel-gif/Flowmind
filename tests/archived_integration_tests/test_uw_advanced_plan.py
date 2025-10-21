#!/usr/bin/env python3
"""
Test Unusual Whales API endpoints with Advanced plan
Token: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50
Plan: API - Advanced ($375/month)
"""
import requests
import json

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE_URL = "https://api.unusualwhales.com/api"

# Test both authentication methods
AUTH_METHODS = {
    "header": {"Authorization": f"Bearer {TOKEN}"},
    "query_param": {}  # Will add token to URL
}

# Endpoints to test (from documentation)
ENDPOINTS = [
    {
        "name": "Flow Alerts",
        "path": "/flow-alerts",
        "params": {"ticker": "TSLA"}
    },
    {
        "name": "Custom Alerts",
        "path": "/alerts",
        "params": {}
    },
    {
        "name": "Stock Last State",
        "path": "/stock/TSLA/last-state",
        "params": {}
    },
    {
        "name": "Stock OHLC",
        "path": "/stock/TSLA/ohlc",
        "params": {"start_date": "2025-10-01", "end_date": "2025-10-21"}
    },
    {
        "name": "Market Tide",
        "path": "/market/tide",
        "params": {}
    },
    {
        "name": "Spot GEX Exposures",
        "path": "/stock/TSLA/spot-exposures-by-strike-expiry",
        "params": {}
    },
    {
        "name": "Options Chain",
        "path": "/stock/TSLA/options-chain",
        "params": {}
    },
    {
        "name": "Greeks Flow Expiry",
        "path": "/stock/TSLA/greeks-flow-expiry",
        "params": {}
    }
]

def test_endpoint(endpoint, auth_method, headers, use_query_param=False):
    """Test a single endpoint with specified auth method"""
    url = f"{BASE_URL}{endpoint['path']}"
    params = endpoint['params'].copy()
    
    if use_query_param:
        params['token'] = TOKEN
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        result = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "content_type": response.headers.get("Content-Type", ""),
        }
        
        try:
            result["response"] = response.json()
        except:
            result["response"] = response.text[:200]  # First 200 chars
        
        return result
    
    except Exception as e:
        return {
            "status_code": None,
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("UNUSUAL WHALES API - ADVANCED PLAN TEST")
    print("=" * 80)
    print(f"Token: {TOKEN}")
    print(f"Plan: API - Advanced ($375/month)")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    print()
    
    results = []
    
    for endpoint in ENDPOINTS:
        print(f"Testing: {endpoint['name']}")
        print(f"Path: {endpoint['path']}")
        print("-" * 80)
        
        # Test with Bearer token in header
        print("  Auth Method: Bearer token in header...")
        result_header = test_endpoint(
            endpoint, 
            "header", 
            AUTH_METHODS["header"],
            use_query_param=False
        )
        
        print(f"    Status: {result_header['status_code']}")
        print(f"    Success: {result_header['success']}")
        if not result_header['success']:
            print(f"    Response: {result_header.get('response', result_header.get('error', 'Unknown'))}")
        
        # Test with token in query param
        print("  Auth Method: Token in query param...")
        result_query = test_endpoint(
            endpoint,
            "query_param",
            {},
            use_query_param=True
        )
        
        print(f"    Status: {result_query['status_code']}")
        print(f"    Success: {result_query['success']}")
        if not result_query['success']:
            print(f"    Response: {result_query.get('response', result_query.get('error', 'Unknown'))}")
        
        results.append({
            "endpoint": endpoint['name'],
            "path": endpoint['path'],
            "header_auth": result_header,
            "query_auth": result_query
        })
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    working_endpoints = []
    for result in results:
        header_works = result['header_auth']['success']
        query_works = result['query_auth']['success']
        
        if header_works or query_works:
            auth_method = "header" if header_works else "query"
            working_endpoints.append({
                "name": result['endpoint'],
                "path": result['path'],
                "auth": auth_method
            })
            print(f"✅ {result['endpoint']}: WORKS (auth: {auth_method})")
        else:
            print(f"❌ {result['endpoint']}: FAILED")
    
    print()
    print("=" * 80)
    
    if working_endpoints:
        print(f"\n✅ WORKING ENDPOINTS: {len(working_endpoints)}/{len(ENDPOINTS)}")
        print("\nSave this configuration:")
        print(json.dumps(working_endpoints, indent=2))
    else:
        print("\n❌ NO ENDPOINTS WORKING - Possible issues:")
        print("   1. Token expired or invalid")
        print("   2. Plan doesn't include API access")
        print("   3. Wrong base URL")
        print("   4. Authentication method incorrect")
        print("\nNext step: Contact support@unusualwhales.com")

if __name__ == "__main__":
    main()
