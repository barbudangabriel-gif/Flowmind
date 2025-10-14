#!/usr/bin/env python3
"""
Quick test for Redis health check endpoint
Tests the new /_redis/health endpoint
"""

import requests
import os

BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8000")

def test_redis_health():
    """Test Redis health check endpoint"""
    print("🧪 Testing Redis Health Check Endpoint")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    try:
        response = requests.get(f"{BACKEND_URL}/_redis/health", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Endpoint Response:")
            print(f"   Status: {data.get('status')}")
            print(f"   Mode: {data.get('mode')}")
            print(f"   Implementation: {data.get('implementation')}")
            print(f"   Connected: {data.get('connected')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Redis URL: {data.get('redis_url')}")
            print(f"   Force Fallback: {data.get('force_fallback')}")
            print(f"   Redis Required: {data.get('redis_required')}")
            
            if data.get('error'):
                print(f"   Error: {data.get('error')}")
            
            # Validation
            print("\n📊 Validation:")
            required_fields = ['status', 'mode', 'implementation', 'connected', 'message']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {', '.join(missing_fields)}")
                return False
            else:
                print("   ✅ All required fields present")
            
            # Check status values
            valid_statuses = ['connected', 'fallback', 'error']
            if data.get('status') in valid_statuses:
                print(f"   ✅ Valid status: {data.get('status')}")
            else:
                print(f"   ❌ Invalid status: {data.get('status')}")
                return False
            
            print("\n🎉 Redis Health Check Endpoint Working!")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        print("💡 Make sure the backend server is running:")
        print("   cd backend && uvicorn server:app --reload")
        return False

if __name__ == "__main__":
    success = test_redis_health()
    exit(0 if success else 1)
