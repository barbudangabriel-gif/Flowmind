# 🧪 Test Unusual Whales CORRECT Endpoints
# Based on: Official email from Dan (UW API Support)
# Date: 21 October 2025

import requests
import json

TOKEN = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE_URL = "https://api.unusualwhales.com/api"

print("=" * 70)
print("🧪 Testing CORRECT Unusual Whales API Endpoints")
print("=" * 70)

# Test 1: Flow Alerts (CORRECT ENDPOINT)
print("\n1️⃣ Testing Flow Alerts...")
try:
    response = requests.get(
        f"{BASE_URL}/flow-alerts",
        headers=HEADERS,
        params={"ticker": "TSLA", "min_premium": 25000},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ SUCCESS! Got {len(response.json())} alerts")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 2: Stock Last State (CORRECT ENDPOINT)
print("\n2️⃣ Testing Stock Last State...")
try:
    response = requests.get(
        f"{BASE_URL}/stock/TSLA/last-state",
        headers=HEADERS,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS! TSLA price: ${data.get('last_price', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 3: GEX Exposures (CORRECT ENDPOINT)
print("\n3️⃣ Testing Spot GEX Exposures...")
try:
    response = requests.get(
        f"{BASE_URL}/stock/TSLA/spot-exposures-by-strike-expiry",
        headers=HEADERS,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS! Got GEX data")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 4: Market Tide (CORRECT ENDPOINT)
print("\n4️⃣ Testing Market Tide...")
try:
    response = requests.get(
        f"{BASE_URL}/market/tide",
        headers=HEADERS,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS! Market sentiment: {data.get('sentiment', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 70)
print("✅ Testing Complete!")
print("=" * 70)
