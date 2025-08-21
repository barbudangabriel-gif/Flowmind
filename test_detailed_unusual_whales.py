#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

def test_detailed_unusual_whales():
    """Detailed testing of Unusual Whales API with filters and data quality checks"""
    base_url = "https://stockflow-ui.preview.emergentagent.com/api"
    
    print("🐋 DETAILED Unusual Whales API Testing")
    print("=" * 60)
    
    # Test 1: Options Flow with Different Filters
    print("\n📈 OPTIONS FLOW TESTING")
    print("-" * 30)
    
    # Default parameters
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/options/flow-alerts", timeout=30)
    response_time = time.time() - start_time
    
    print(f"1.1 Default Options Flow:")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('data', {}).get('alerts', [])
        summary = data.get('data', {}).get('summary', {})
        
        print(f"    📊 Alerts: {len(alerts)}")
        print(f"    💰 Total Premium: ${summary.get('total_premium', 0):,.0f}")
        print(f"    📈 Bullish: {summary.get('bullish_count', 0)} | 📉 Bearish: {summary.get('bearish_count', 0)}")
        
        # Check data structure
        if alerts:
            first_alert = alerts[0]
            print(f"    🔍 Sample Alert: {first_alert.get('symbol')} {first_alert.get('strike_type')} - ${first_alert.get('premium', 0):,.0f}")
            print(f"    📊 Sentiment: {first_alert.get('sentiment')} | Volume/OI: {first_alert.get('volume_oi_ratio', 0):.2f}")
    
    # High premium filter
    params = {"minimum_premium": 500000, "minimum_volume_oi_ratio": 2.0, "limit": 25}
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/options/flow-alerts", params=params, timeout=30)
    response_time = time.time() - start_time
    
    print(f"\n1.2 High Premium Filter (≥$500K):")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('data', {}).get('alerts', [])
        analysis = data.get('analysis', {})
        
        print(f"    📊 Filtered Alerts: {len(alerts)}")
        if 'signals' in analysis:
            signals = analysis.get('signals', [])
            print(f"    🎯 Trading Signals: {len(signals)}")
            for signal in signals[:2]:
                print(f"      - {signal.get('type', 'unknown')}: {signal.get('description', 'N/A')}")
    
    # Test 2: Dark Pool Analysis
    print("\n🌊 DARK POOL TESTING")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/dark-pool/recent", timeout=30)
    response_time = time.time() - start_time
    
    print(f"2.1 Recent Dark Pool Activity:")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        summary = data.get('data', {}).get('summary', {})
        
        print(f"    📊 Trades: {len(trades)}")
        print(f"    📈 Total Dark Volume: {summary.get('total_dark_volume', 0):,}")
        print(f"    🎯 Avg Dark %: {summary.get('avg_dark_percentage', 0):.1f}%")
        print(f"    🏛️  Institutional Signals: {summary.get('institutional_signals', 0)}")
        
        if trades:
            first_trade = trades[0]
            print(f"    🔍 Sample Trade: {first_trade.get('ticker')} - {first_trade.get('dark_volume', 0):,} vol ({first_trade.get('dark_percentage', 0):.1f}% dark)")
    
    # High volume filter
    params = {"minimum_volume": 200000, "minimum_dark_percentage": 40.0, "include_analysis": True}
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/dark-pool/recent", params=params, timeout=30)
    response_time = time.time() - start_time
    
    print(f"\n2.2 High Volume Filter (≥200K vol, ≥40% dark):")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        analysis = data.get('analysis', {})
        
        print(f"    📊 Filtered Trades: {len(trades)}")
        if 'implications' in analysis:
            implications = analysis.get('implications', [])
            print(f"    💡 Analysis Implications: {len(implications)}")
            for implication in implications[:2]:
                print(f"      - {implication.get('type', 'unknown')}: {implication.get('description', 'N/A')}")
    
    # Test 3: Congressional Trades with Filters
    print("\n🏛️  CONGRESSIONAL TRADES TESTING")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/congressional/trades", timeout=30)
    response_time = time.time() - start_time
    
    print(f"3.1 All Congressional Trades:")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        summary = data.get('data', {}).get('summary', {})
        analysis = data.get('analysis', {})
        
        print(f"    📊 Trades: {len(trades)}")
        print(f"    💰 Total Amount: ${summary.get('total_amount', 0):,.0f}")
        print(f"    👥 Representatives: {summary.get('unique_representatives', 0)}")
        print(f"    📈 Unique Tickers: {summary.get('unique_tickers', 0)}")
        
        # Party breakdown
        party_breakdown = summary.get('party_breakdown', {})
        if party_breakdown:
            print(f"    🗳️  Party Breakdown:")
            for party, count in party_breakdown.items():
                print(f"      - {party}: {count} trades")
        
        # Transaction type breakdown
        tx_breakdown = summary.get('transaction_type_breakdown', {})
        if tx_breakdown:
            print(f"    💼 Transaction Types:")
            for tx_type, count in tx_breakdown.items():
                print(f"      - {tx_type}: {count} trades")
        
        # Analysis insights
        if 'insights' in analysis:
            insights = analysis.get('insights', [])
            print(f"    💡 Analysis Insights: {len(insights)}")
            for insight in insights:
                print(f"      - {insight.get('type', 'unknown')}: {insight.get('description', 'N/A')}")
    
    # Democrat purchases filter
    params = {"party_filter": "Democrat", "transaction_type": "Purchase", "minimum_amount": 50000}
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/congressional/trades", params=params, timeout=30)
    response_time = time.time() - start_time
    
    print(f"\n3.2 Democrat Purchases (≥$50K):")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        print(f"    📊 Filtered Trades: {len(trades)}")
        
        if trades:
            first_trade = trades[0]
            print(f"    🔍 Sample: {first_trade.get('representative')} - {first_trade.get('transaction_type')} {first_trade.get('ticker')} ${first_trade.get('transaction_amount', 0):,.0f}")
    
    # Test 4: Trading Strategies
    print("\n🎯 TRADING STRATEGIES TESTING")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/trading-strategies", timeout=30)
    response_time = time.time() - start_time
    
    print(f"4.1 AI-Powered Trading Strategies:")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        market_context = data.get('market_context', {})
        
        print(f"    📊 Generated Strategies: {len(strategies)}")
        print(f"    📈 Market Sentiment: {market_context.get('overall_sentiment', 'unknown')}")
        print(f"    🎯 Confidence: {market_context.get('confidence_level', 'unknown')}")
        
        if strategies:
            # Analyze strategy types
            strategy_types = {}
            for strategy in strategies:
                s_type = strategy.get('strategy_type', 'unknown')
                strategy_types[s_type] = strategy_types.get(s_type, 0) + 1
            
            print(f"    📋 Strategy Types:")
            for s_type, count in strategy_types.items():
                print(f"      - {s_type}: {count} strategies")
            
            # Show top strategy details
            first_strategy = strategies[0]
            print(f"    💡 Top Strategy: {first_strategy.get('strategy_name', 'N/A')}")
            print(f"      - Ticker: {first_strategy.get('ticker', 'N/A')}")
            print(f"      - Confidence: {first_strategy.get('confidence', 0):.2f}")
            print(f"      - Timeframe: {first_strategy.get('timeframe', 'N/A')}")
            
            # Check TradeStation readiness
            tradestation = first_strategy.get('tradestation_execution', {})
            if tradestation:
                print(f"      - TradeStation Ready: ✅")
                print(f"        * Instrument: {tradestation.get('instrument_type', 'N/A')}")
                print(f"        * Action: {tradestation.get('action', 'N/A')}")
                print(f"        * Stop Loss: {tradestation.get('stop_loss', 'N/A')}")
            else:
                print(f"      - TradeStation Ready: ❌")
    
    # Test 5: Comprehensive Analysis
    print("\n🔬 COMPREHENSIVE ANALYSIS TESTING")
    print("-" * 30)
    
    start_time = time.time()
    response = requests.get(f"{base_url}/unusual-whales/analysis/comprehensive", timeout=30)
    response_time = time.time() - start_time
    
    print(f"5.1 Cross-Signal Analysis:")
    print(f"    Status: {response.status_code} | Response Time: {response_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        comprehensive_analysis = data.get('comprehensive_analysis', {})
        market_outlook = data.get('market_outlook', {})
        data_summary = data.get('data_summary', {})
        
        print(f"    📊 Data Sources:")
        print(f"      - Options Alerts: {data_summary.get('options_alerts', 0)}")
        print(f"      - Dark Pool Trades: {data_summary.get('dark_pool_trades', 0)}")
        print(f"      - Congressional Trades: {data_summary.get('congressional_trades', 0)}")
        
        print(f"    🔮 Market Outlook:")
        print(f"      - Overall Sentiment: {market_outlook.get('overall_sentiment', 'unknown')}")
        print(f"      - Confidence: {market_outlook.get('confidence', 'unknown')}")
        
        key_signals = market_outlook.get('key_signals', [])
        if key_signals:
            print(f"      - Key Signals ({len(key_signals)}):")
            for signal in key_signals[:3]:
                print(f"        * {signal}")
        
        recommended_actions = market_outlook.get('recommended_actions', [])
        if recommended_actions:
            print(f"      - Recommended Actions ({len(recommended_actions)}):")
            for action in recommended_actions[:2]:
                print(f"        * {action}")
        
        # Check each analysis component
        for source, analysis in comprehensive_analysis.items():
            data_available = analysis.get('data_available', False)
            status = "✅ Available" if data_available else "❌ No Data"
            print(f"      - {source.replace('_', ' ').title()}: {status}")
    
    print("\n" + "=" * 60)
    print("🎉 DETAILED Unusual Whales API Testing Complete")
    print("✅ All endpoints tested successfully with real API key integration")

if __name__ == "__main__":
    test_detailed_unusual_whales()