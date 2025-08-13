#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get("http://localhost:8001/api/market/overview", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Market Overview Response:")
        print(json.dumps(data, indent=2))
        
        # Check if we have indices data
        if 'indices' in data and len(data['indices']) > 0:
            print(f"\nFound {len(data['indices'])} indices:")
            for index in data['indices']:
                print(f"  {index.get('symbol', 'N/A')}: {index.get('name', 'N/A')} - ${index.get('price', 0):.2f} ({index.get('change_percent', 0):+.2f}%)")
        else:
            print("No indices data found")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error testing endpoint: {e}")