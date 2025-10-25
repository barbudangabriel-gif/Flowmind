#!/usr/bin/env python3
"""Test TradeStation LIVE OAuth and API integration."""

import asyncio
import json
import os
import sys

import httpx
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from services.tradestation import get_cached_token, get_valid_token

load_dotenv()


async def test_token_status():
    """Test token retrieval and validation."""
    print("\n" + "=" * 60)
    print("🔐 TradeStation Token Status Test")
    print("=" * 60)

    user_id = "default"
    token = await get_cached_token(user_id)

    if not token:
        print(f"❌ No token found for user_id: {user_id}")
        print("\nRun OAuth flow: http://localhost:8000/api/ts/login")
        return False

    print(f"\n✅ Token found for user_id: {user_id}")
    print(f"   Access Token: {token['access_token'][:20]}...{token['access_token'][-20:]}")
    print(f"   Token Type: {token.get('token_type', 'Bearer')}")
    print(f"   Expires At: {token.get('expires_at', 'unknown')}")
    print(f"   Scope: {token.get('scope', 'unknown')}")

    # Check if token has refresh_token
    if token.get("refresh_token"):
        print(f"   Refresh Token: {token['refresh_token'][:20]}...{token['refresh_token'][-20:]}")
    else:
        print("   ⚠️  No refresh token available")

    return True


async def test_api_call():
    """Test actual API call to TradeStation."""
    print("\n" + "=" * 60)
    print("📊 TradeStation API Call Test")
    print("=" * 60)

    user_id = "default"
    token = await get_valid_token(user_id)

    if not token:
        print(f"❌ Cannot get valid token for user_id: {user_id}")
        return False

    # Test /brokerage/accounts endpoint
    url = "https://api.tradestation.com/v3/brokerage/accounts"
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json",
    }

    print(f"\n🔗 GET {url}")
    print(f"   Authorization: Bearer {token['access_token'][:20]}...")

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, headers=headers)
            print(f"\n✅ Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                accounts = data.get("Accounts", [])
                print(f"\n📈 Found {len(accounts)} account(s):")
                for acc in accounts:
                    print(f"   - {acc['AccountID']} ({acc['AccountType']}) - {acc['Status']}")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False

        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False


async def test_token_persistence():
    """Test if token survives cache reads."""
    print("\n" + "=" * 60)
    print("💾 Token Persistence Test")
    print("=" * 60)

    user_id = "default"

    # Read token multiple times
    for i in range(3):
        token = await get_cached_token(user_id)
        if token:
            print(f"   Read {i+1}: ✅ Token retrieved (expires_at={token.get('expires_at')})")
        else:
            print(f"   Read {i+1}: ❌ Token not found")
            return False

    print("\n✅ Token persistence working!")
    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 TradeStation LIVE Integration Test Suite")
    print("=" * 60)

    results = {
        "Token Status": await test_token_status(),
        "API Call": await test_api_call(),
        "Token Persistence": await test_token_persistence(),
    }

    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:.<40} {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
