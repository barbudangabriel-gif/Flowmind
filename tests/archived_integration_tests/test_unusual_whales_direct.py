#!/usr/bin/env python3
"""
Direct test of Unusual Whales API to diagnose ETF data issues
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

async def test_unusual_whales_api():
 api_token = os.getenv("UW_API_TOKEN")
 base_url = os.getenv("UW_BASE_URL", "https://api.unusualwhales.com")
 
 print(f"API Token: {api_token}")
 print(f"Base URL: {base_url}")
 
 headers = {
 "Authorization": f"Bearer {api_token}",
 "Content-Type": "application/json",
 "User-Agent": "FlowMind-Analytics/1.0"
 }
 
 # Test different endpoints to find ETF data
 test_endpoints = [
 "/api/stocks/screener",
 "/api/stocks/quote?symbol=SPY",
 "/api/stock/SPY",
 "/api/screener",
 "/api/etf/SPY",
 "/api/stocks/SPY"
 ]
 
 async with httpx.AsyncClient(timeout=30.0) as client:
 for endpoint in test_endpoints:
 try:
 print(f"\n Testing endpoint: {endpoint}")
 url = f"{base_url}{endpoint}"
 response = await client.get(url, headers=headers)
 
 print(f" Status: {response.status_code}")
 
 if response.status_code == 200:
 try:
 data = response.json()
 print(f" Response: {str(data)[:200]}...")
 
 # Look for SPY data specifically
 if isinstance(data, dict):
 if 'data' in data and isinstance(data['data'], list):
 spy_found = any(item.get('symbol') == 'SPY' for item in data['data'] if isinstance(item, dict))
 if spy_found:
 print(f" Found SPY in response!")
 elif data.get('symbol') == 'SPY':
 print(f" Direct SPY data found!")
 elif isinstance(data, list):
 spy_found = any(item.get('symbol') == 'SPY' for item in data if isinstance(item, dict))
 if spy_found:
 print(f" Found SPY in list response!")
 
 except Exception as e:
 print(f" JSON parse error: {e}")
 print(f" Raw response: {response.text[:200]}...")
 
 elif response.status_code == 401:
 print(f" Unauthorized - API token may be invalid")
 elif response.status_code == 404:
 print(f" Not Found - Endpoint doesn't exist")
 elif response.status_code == 429:
 print(f" Rate Limited")
 else:
 print(f" Error: {response.text[:100]}...")
 
 except Exception as e:
 print(f" Request failed: {e}")
 
 # Test the specific method used in the service
 print(f"\n🐋 Testing UnusualWhalesService method directly:")
 try:
 from backend.unusual_whales_service import UnusualWhalesService
 
 service = UnusualWhalesService()
 print(f"Service API token: {service.api_token}")
 
 # Test ETF data method
 etf_symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
 etf_data = await service.get_etf_data_for_futures(etf_symbols)
 
 print(f"ETF data results: {len(etf_data)} ETFs found")
 for symbol, data in etf_data.items():
 price = data.get('price', 0)
 print(f" {symbol}: ${price:.2f}")
 
 except Exception as e:
 print(f" Service test failed: {e}")

if __name__ == "__main__":
 asyncio.run(test_unusual_whales_api())