#!/usr/bin/env python3
"""
Quick test for all 12 UW API endpoints
Run: python test_uw_12_endpoints.py
"""

import requests
import time

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE = "https://api.unusualwhales.com/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

ENDPOINTS = [
    ("/stock/TSLA/info", "Stock info"),
    ("/stock/TSLA/greeks", "Options Greeks"),
    ("/stock/TSLA/option-contracts", "Options chain"),
    ("/stock/TSLA/spot-exposures", "Gamma exposure"),
    ("/stock/TSLA/options-volume", "Options volume"),
    ("/alerts", "Market alerts"),
    ("/screener/stocks?limit=5", "Stock screener"),
    ("/insider/trades", "All insider trades"),
    ("/insider/TSLA", "Insider trades (TSLA)"),
    ("/insider/recent", "Recent insider trades"),
    ("/darkpool/TSLA", "Dark pool (TSLA)"),
    ("/darkpool/recent", "Recent dark pool"),
]

print("🧪 TESTING ALL 12 VERIFIED UW API ENDPOINTS")
print("=" * 60)
print()

results = []
for i, (endpoint, description) in enumerate(ENDPOINTS, 1):
    print(f"{i:2d}. {description:25s} ", end="", flush=True)
    
    try:
        r = requests.get(f"{BASE}{endpoint}", headers=HEADERS, timeout=10)
        
        if r.status_code == 200:
            data = r.json().get("data", [])
            count = len(data) if isinstance(data, list) else (1 if data else 0)
            print(f"✅ OK ({count} records)")
            results.append((description, True, count))
        else:
            print(f"❌ FAILED ({r.status_code})")
            results.append((description, False, 0))
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:40]}")
        results.append((description, False, 0))
    
    time.sleep(1.0)  # Rate limiting

print()
print("=" * 60)

working = sum(1 for _, ok, _ in results if ok)
print(f"📊 RESULTS: {working}/12 endpoints working")
print()

if working == 12:
    print("✅ ALL 12 ENDPOINTS VERIFIED!")
    print()
    print("🎉 HIGHLIGHTS:")
    for desc, ok, count in results:
        if ok and count > 0:
            print(f"  • {desc}: {count} records")
else:
    print("⚠️ WARNING: Some endpoints failed!")
    for desc, ok, count in results:
        if not ok:
            print(f"  ❌ {desc}")
