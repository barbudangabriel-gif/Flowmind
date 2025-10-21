#!/usr/bin/env python3
"""Show sample data from each UW API endpoint"""

import requests
import json

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE = "https://api.unusualwhales.com/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def show_sample(endpoint, description, sample_size=2):
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}")
    print(f"Endpoint: {endpoint}")
    print()
    
    try:
        r = requests.get(f"{BASE}{endpoint}", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            
            if isinstance(data, list):
                count = len(data)
                print(f"✅ Total records: {count}")
                
                if count > 0:
                    print(f"\n📝 Sample (first {min(sample_size, count)} records):")
                    for i, item in enumerate(data[:sample_size], 1):
                        print(f"\n  Record {i}:")
                        print(json.dumps(item, indent=4))
                else:
                    print("⚠️  No data currently available (endpoint works)")
            elif isinstance(data, dict):
                print("✅ Single record:")
                print(json.dumps(data, indent=4))
        else:
            print(f"❌ Error: {r.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

# Show samples from each endpoint
print("🔍 UNUSUAL WHALES API - DATA SAMPLES")
print("=" * 70)

show_sample("/stock/TSLA/info", "Stock Info (TSLA)")
show_sample("/stock/TSLA/option-contracts", "Options Chain (TSLA)", 1)
show_sample("/stock/TSLA/spot-exposures", "Gamma Exposure (TSLA)", 1)
show_sample("/stock/TSLA/options-volume", "Options Volume (TSLA)")
show_sample("/alerts", "Market Alerts", 2)
show_sample("/screener/stocks?limit=3", "Stock Screener", 1)
show_sample("/insider/TSLA", "Insider Trades (TSLA)", 2)
show_sample("/darkpool/TSLA", "Dark Pool (TSLA)", 2)
show_sample("/darkpool/recent", "Recent Dark Pool", 2)

print("\n" + "="*70)
print("✅ DATA SAMPLES COMPLETE")
print("="*70)
