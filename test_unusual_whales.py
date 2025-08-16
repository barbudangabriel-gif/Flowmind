#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_unusual_whales_endpoints():
    """Test all Unusual Whales API endpoints"""
    base_url = "https://stockai-platform-1.preview.emergentagent.com/api"
    
    print("🐋 Testing Unusual Whales API Integration")
    print("=" * 50)
    
    # Test 1: Options Flow Alerts
    print("\n1. Testing Options Flow Alerts...")
    try:
        response = requests.get(f"{base_url}/unusual-whales/options/flow-alerts", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('data', {}).get('alerts', [])
            print(f"   ✅ Found {len(alerts)} options flow alerts")
            if 'analysis' in data:
                print(f"   ✅ Analysis included")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Dark Pool Activity
    print("\n2. Testing Dark Pool Activity...")
    try:
        response = requests.get(f"{base_url}/unusual-whales/dark-pool/recent", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', {}).get('trades', [])
            print(f"   ✅ Found {len(trades)} dark pool trades")
            if 'analysis' in data:
                print(f"   ✅ Analysis included")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 3: Congressional Trades
    print("\n3. Testing Congressional Trades...")
    try:
        response = requests.get(f"{base_url}/unusual-whales/congressional/trades", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', {}).get('trades', [])
            print(f"   ✅ Found {len(trades)} congressional trades")
            if 'analysis' in data:
                print(f"   ✅ Analysis included")
                analysis = data['analysis']
                if 'summary' in analysis:
                    summary = analysis['summary']
                    print(f"   📊 Total Amount: ${summary.get('total_amount', 0):,.0f}")
                    print(f"   👥 Representatives: {summary.get('unique_representatives', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 4: Trading Strategies
    print("\n4. Testing Trading Strategies...")
    try:
        response = requests.get(f"{base_url}/unusual-whales/trading-strategies", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            strategies = data.get('strategies', [])
            print(f"   ✅ Generated {len(strategies)} trading strategies")
            if strategies:
                first_strategy = strategies[0]
                print(f"   💡 Top Strategy: {first_strategy.get('strategy_name', 'N/A')}")
                print(f"   🎯 Ticker: {first_strategy.get('ticker', 'N/A')}")
                print(f"   📈 Confidence: {first_strategy.get('confidence', 0):.2f}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 5: Comprehensive Analysis
    print("\n5. Testing Comprehensive Analysis...")
    try:
        response = requests.get(f"{base_url}/unusual-whales/analysis/comprehensive", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            comprehensive_analysis = data.get('comprehensive_analysis', {})
            market_outlook = data.get('market_outlook', {})
            print(f"   ✅ Comprehensive analysis completed")
            print(f"   📊 Data Sources: {len(comprehensive_analysis)} analyzed")
            print(f"   🔮 Market Sentiment: {market_outlook.get('overall_sentiment', 'unknown')}")
            print(f"   🎯 Confidence: {market_outlook.get('confidence', 'unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🐋 Unusual Whales API Testing Complete")

if __name__ == "__main__":
    test_unusual_whales_endpoints()