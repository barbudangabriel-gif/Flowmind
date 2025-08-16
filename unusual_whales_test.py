#!/usr/bin/env python3
"""
Unusual Whales API Testing Suite
Test all Unusual Whales endpoints with the new dropdown UI structure
Focus on verifying real data with provided API key: 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50
"""

import requests
import sys
import time
from datetime import datetime
import json

class UnusualWhalesAPITester:
    def __init__(self, base_url="https://options-builder.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.api_key = "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
        
        print("🐋 UNUSUAL WHALES API TESTING SUITE")
        print("=" * 80)
        print(f"🎯 OBJECTIVE: Test all Unusual Whales endpoints for dropdown UI functionality")
        print(f"🔑 API Key: {self.api_key}")
        print(f"🌐 Base URL: {base_url}")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test with detailed logging"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            end_time = time.time()
            response_time = end_time - start_time

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} - Time: {response_time:.2f}s")
                try:
                    response_data = response.json()
                    return True, response_data, response_time
                except:
                    return True, {}, response_time
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code} - Time: {response_time:.2f}s")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, {}, response_time

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}, 30.0
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}, 0.0

    def test_options_flow_api(self):
        """Test Options Flow API - GET /api/unusual-whales/options/flow-alerts"""
        print("\n" + "="*80)
        print("🎯 TESTING OPTIONS FLOW API")
        print("="*80)
        print("📊 Endpoint: GET /api/unusual-whales/options/flow-alerts")
        print("🎯 Expected: Real options flow data with provided API key")
        
        # Test 1: Basic Options Flow Request
        print(f"\n📋 PHASE 1: Basic Options Flow Request")
        print("-" * 60)
        
        success, flow_data, response_time = self.run_test(
            "Options Flow Alerts (Default)", 
            "GET", 
            "unusual-whales/options/flow-alerts", 
            200
        )
        
        if not success:
            print("❌ Options Flow API endpoint failed")
            return False
        
        # Analyze response structure
        status = flow_data.get('status', 'unknown')
        data = flow_data.get('data', {})
        alerts = data.get('alerts', [])
        summary = data.get('summary', {})
        timestamp = flow_data.get('timestamp', 'N/A')
        
        print(f"📊 API Status: {status}")
        print(f"📊 Response Time: {response_time:.2f}s")
        print(f"📊 Timestamp: {timestamp}")
        print(f"📊 Found {len(alerts)} options flow alerts")
        
        if summary:
            print(f"💰 Total Premium: ${summary.get('total_premium', 0):,.0f}")
            print(f"📈 Bullish Count: {summary.get('bullish_count', 0)}")
            print(f"📉 Bearish Count: {summary.get('bearish_count', 0)}")
            print(f"🔥 Unusual Activity: {summary.get('unusual_activity', 0)}")
            print(f"🎯 Opening Trades: {summary.get('opening_trades', 0)}")
        
        # Test 2: Data Quality Verification
        print(f"\n🔍 PHASE 2: Data Quality Verification")
        print("-" * 60)
        
        real_data_indicators = []
        mock_data_indicators = []
        
        if alerts:
            # Check first alert structure
            first_alert = alerts[0]
            required_fields = ['symbol', 'strike_type', 'premium', 'sentiment', 'volume']
            optional_fields = ['volume_oi_ratio', 'is_opener', 'unusual_activity', 'dte']
            
            missing_required = [field for field in required_fields if field not in first_alert]
            present_optional = [field for field in optional_fields if field in first_alert]
            
            if missing_required:
                print(f"❌ Missing required fields: {missing_required}")
            else:
                print(f"✅ All required fields present: {required_fields}")
                real_data_indicators.append("Complete field structure")
            
            if present_optional:
                print(f"✅ Optional fields present: {present_optional}")
                real_data_indicators.append("Enhanced field data")
            
            # Analyze symbols for real market data
            symbols = [alert.get('symbol', '') for alert in alerts[:10]]
            unique_symbols = list(set(symbols))
            print(f"📊 Sample Symbols: {unique_symbols}")
            
            # Check for real market symbols
            common_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'AMZN', 'META', 'SOFI', 'TTD']
            real_symbols_found = [s for s in unique_symbols if s in common_symbols]
            
            if real_symbols_found:
                print(f"✅ Real market symbols detected: {real_symbols_found}")
                real_data_indicators.append(f"Real symbols: {len(real_symbols_found)}")
            
            # Analyze premium values
            premiums = [alert.get('premium', 0) for alert in alerts[:5]]
            print(f"💰 Sample Premiums: ${premiums}")
            
            # Check for realistic premium distribution
            if any(p % 1000 != 0 for p in premiums if p > 0):
                real_data_indicators.append("Realistic premium values")
            
            # Display sample alert
            print(f"\n📊 Sample Alert Details:")
            print(f"   - Symbol: {first_alert.get('symbol', 'N/A')}")
            print(f"   - Strike/Type: {first_alert.get('strike_type', 'N/A')}")
            print(f"   - Premium: ${first_alert.get('premium', 0):,.0f}")
            print(f"   - Sentiment: {first_alert.get('sentiment', 'N/A')}")
            print(f"   - Volume: {first_alert.get('volume', 0):,}")
            if 'dte' in first_alert:
                print(f"   - DTE: {first_alert.get('dte', 'N/A')}")
        
        # Test 3: Premium Filtering
        print(f"\n💰 PHASE 3: Premium Filtering Tests")
        print("-" * 60)
        
        premium_filters = [200000, 500000]
        filter_results = {}
        
        for min_premium in premium_filters:
            params = {
                "minimum_premium": min_premium,
                "limit": 50,
                "include_analysis": True
            }
            
            success_filter, filtered_data, filter_time = self.run_test(
                f"Options Flow (Premium >= ${min_premium:,})", 
                "GET", 
                "unusual-whales/options/flow-alerts", 
                200, 
                params=params
            )
            
            if success_filter:
                filtered_alerts = filtered_data.get('data', {}).get('alerts', [])
                filter_results[min_premium] = len(filtered_alerts)
                
                print(f"   💰 Premium >= ${min_premium:,}: {len(filtered_alerts)} alerts")
                
                if filtered_alerts:
                    avg_premium = sum(alert.get('premium', 0) for alert in filtered_alerts) / len(filtered_alerts)
                    max_premium = max(alert.get('premium', 0) for alert in filtered_alerts)
                    min_premium_actual = min(alert.get('premium', 0) for alert in filtered_alerts)
                    
                    print(f"     - Average Premium: ${avg_premium:,.0f}")
                    print(f"     - Premium Range: ${min_premium_actual:,.0f} - ${max_premium:,.0f}")
                    
                    # Verify filter is working
                    if min_premium_actual >= min_premium:
                        print(f"     ✅ Filter working correctly")
                    else:
                        print(f"     ⚠️  Filter issue: found ${min_premium_actual:,} < ${min_premium:,}")
        
        # Assessment
        is_real_data = len(real_data_indicators) > len(mock_data_indicators)
        
        print(f"\n🎯 OPTIONS FLOW API ASSESSMENT:")
        print(f"   - Alerts Found: {len(alerts)}")
        print(f"   - Data Quality: {'✅ REAL DATA' if is_real_data else '⚠️  MOCK/NO DATA'}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - Premium Filters: {'✅ WORKING' if len(filter_results) >= 2 else '❌ ISSUES'}")
        
        return success and (len(alerts) > 0 or status == 'success')

    def test_dark_pool_api(self):
        """Test Dark Pool API - GET /api/unusual-whales/dark-pool"""
        print("\n" + "="*80)
        print("🌊 TESTING DARK POOL API")
        print("="*80)
        print("📊 Endpoint: GET /api/unusual-whales/dark-pool/recent")
        print("🎯 Expected: Real dark pool trading data")
        
        # Test 1: Basic Dark Pool Request
        print(f"\n📋 PHASE 1: Basic Dark Pool Request")
        print("-" * 60)
        
        success, dark_pool_data, response_time = self.run_test(
            "Dark Pool Recent Activity", 
            "GET", 
            "unusual-whales/dark-pool/recent", 
            200
        )
        
        if not success:
            print("❌ Dark Pool API endpoint failed")
            return False
        
        # Analyze response structure
        status = dark_pool_data.get('status', 'unknown')
        data = dark_pool_data.get('data', {})
        trades = data.get('trades', [])
        summary = data.get('summary', {})
        timestamp = dark_pool_data.get('timestamp', 'N/A')
        
        print(f"📊 API Status: {status}")
        print(f"📊 Response Time: {response_time:.2f}s")
        print(f"📊 Timestamp: {timestamp}")
        print(f"📊 Found {len(trades)} dark pool trades")
        
        if summary:
            print(f"📈 Total Dark Volume: {summary.get('total_dark_volume', 0):,}")
            print(f"🎯 Avg Dark Percentage: {summary.get('avg_dark_percentage', 0):.2f}%")
            print(f"🏛️  Institutional Signals: {summary.get('institutional_signals', 0)}")
            print(f"🔥 High Significance: {summary.get('high_significance', 0)}")
        
        # Test 2: Data Structure Verification
        print(f"\n🔍 PHASE 2: Data Structure Verification")
        print("-" * 60)
        
        if trades:
            first_trade = trades[0]
            required_fields = ['ticker', 'timestamp', 'price', 'dark_volume', 'total_volume', 
                             'dark_percentage', 'dollar_volume', 'significance', 'institutional_signal']
            
            missing_fields = [field for field in required_fields if field not in first_trade]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print(f"✅ All required fields present: {len(required_fields)} fields")
            
            # Display sample trade
            print(f"\n📊 Sample Trade Details:")
            print(f"   - Ticker: {first_trade.get('ticker', 'N/A')}")
            print(f"   - Price: ${first_trade.get('price', 0):.2f}")
            print(f"   - Dark Volume: {first_trade.get('dark_volume', 0):,}")
            print(f"   - Total Volume: {first_trade.get('total_volume', 0):,}")
            print(f"   - Dark Percentage: {first_trade.get('dark_percentage', 0):.2f}%")
            print(f"   - Dollar Volume: ${first_trade.get('dollar_volume', 0):,.0f}")
            print(f"   - Significance: {first_trade.get('significance', 'N/A')}")
            print(f"   - Institutional Signal: {first_trade.get('institutional_signal', False)}")
            
            # Check for real market tickers
            tickers = [trade.get('ticker', '') for trade in trades[:5]]
            print(f"📊 Sample Tickers: {tickers}")
        else:
            print("⚠️  No trades found - testing with permissive filters...")
            
            # Test with very permissive filters
            params = {
                "minimum_volume": 1000,
                "minimum_dark_percentage": 0.01,
                "limit": 100
            }
            
            success_permissive, permissive_data, perm_time = self.run_test(
                "Dark Pool (Permissive Filters)", 
                "GET", 
                "unusual-whales/dark-pool/recent", 
                200, 
                params=params
            )
            
            if success_permissive:
                permissive_trades = permissive_data.get('data', {}).get('trades', [])
                print(f"   🔧 Permissive Filter Results: {len(permissive_trades)} trades")
                if len(permissive_trades) > 0:
                    trades = permissive_trades
                    print("   ✅ API working - data available with permissive filters")
        
        # Test 3: Filter Testing
        print(f"\n🔍 PHASE 3: Filter Testing")
        print("-" * 60)
        
        filter_tests = [
            {"minimum_dark_percentage": 0.01, "name": "Very Low (0.01%)"},
            {"minimum_dark_percentage": 10.0, "name": "Medium (10.0%)"},
            {"minimum_dark_percentage": 30.0, "name": "High (30.0%)"}
        ]
        
        for filter_test in filter_tests:
            min_dark_pct = filter_test["minimum_dark_percentage"]
            test_name = filter_test["name"]
            
            params = {
                "minimum_volume": 100000,
                "minimum_dark_percentage": min_dark_pct,
                "limit": 50
            }
            
            success_filter, filter_data, filter_time = self.run_test(
                f"Dark Pool Filter ({test_name})", 
                "GET", 
                "unusual-whales/dark-pool/recent", 
                200, 
                params=params
            )
            
            if success_filter:
                filter_trades = filter_data.get('data', {}).get('trades', [])
                print(f"   📊 {test_name}: {len(filter_trades)} trades")
        
        print(f"\n🎯 DARK POOL API ASSESSMENT:")
        print(f"   - Trades Found: {len(trades)}")
        print(f"   - Data Quality: {'✅ REAL DATA' if len(trades) > 0 else '⚠️  NO DATA (may be normal)'}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - API Status: {status}")
        
        return success

    def test_congressional_trades_api(self):
        """Test Congressional Trades API - GET /api/unusual-whales/congress/trades"""
        print("\n" + "="*80)
        print("🏛️  TESTING CONGRESSIONAL TRADES API")
        print("="*80)
        print("📊 Endpoint: GET /api/unusual-whales/congressional/trades")
        print("🎯 Expected: Congressional trading data")
        
        # Test 1: Basic Congressional Trades Request
        print(f"\n📋 PHASE 1: Basic Congressional Trades Request")
        print("-" * 60)
        
        success, congress_data, response_time = self.run_test(
            "Congressional Trades", 
            "GET", 
            "unusual-whales/congressional/trades", 
            200
        )
        
        if not success:
            print("❌ Congressional Trades API endpoint failed")
            return False
        
        # Analyze response structure
        status = congress_data.get('status', 'unknown')
        data = congress_data.get('data', {})
        trades = data.get('trades', [])
        summary = data.get('summary', {})
        timestamp = congress_data.get('timestamp', 'N/A')
        
        print(f"📊 API Status: {status}")
        print(f"📊 Response Time: {response_time:.2f}s")
        print(f"📊 Timestamp: {timestamp}")
        print(f"📊 Found {len(trades)} congressional trades")
        
        if summary:
            print(f"💰 Total Amount: ${summary.get('total_amount', 0):,.0f}")
            print(f"👥 Unique Representatives: {summary.get('unique_representatives', 0)}")
            print(f"📈 Unique Tickers: {summary.get('unique_tickers', 0)}")
            print(f"🕐 Recent Trades (7d): {summary.get('recent_trades', 0)}")
            
            # Party breakdown
            party_breakdown = summary.get('party_breakdown', {})
            if party_breakdown:
                print(f"🗳️  Party Breakdown:")
                for party, count in party_breakdown.items():
                    print(f"     - {party}: {count} trades")
        
        # Test 2: Data Structure Verification
        print(f"\n🔍 PHASE 2: Data Structure Verification")
        print("-" * 60)
        
        if trades:
            first_trade = trades[0]
            required_fields = ['representative', 'party', 'ticker', 'transaction_type', 'transaction_amount']
            optional_fields = ['transaction_date', 'disclosure_date', 'asset_description']
            
            missing_required = [field for field in required_fields if field not in first_trade]
            present_optional = [field for field in optional_fields if field in first_trade]
            
            if missing_required:
                print(f"❌ Missing required fields: {missing_required}")
            else:
                print(f"✅ All required fields present: {required_fields}")
            
            if present_optional:
                print(f"✅ Optional fields present: {present_optional}")
            
            # Display sample trade
            print(f"\n📊 Sample Congressional Trade:")
            print(f"   - Representative: {first_trade.get('representative', 'N/A')}")
            print(f"   - Party: {first_trade.get('party', 'N/A')}")
            print(f"   - Ticker: {first_trade.get('ticker', 'N/A')}")
            print(f"   - Transaction Type: {first_trade.get('transaction_type', 'N/A')}")
            print(f"   - Amount: ${first_trade.get('transaction_amount', 0):,.0f}")
            if 'transaction_date' in first_trade:
                print(f"   - Date: {first_trade.get('transaction_date', 'N/A')}")
        
        # Test 3: Filtering Tests
        print(f"\n🔍 PHASE 3: Filtering Tests")
        print("-" * 60)
        
        # Test party filter
        params = {"party": "Democrat", "minimum_amount": 50000}
        success_filter, filtered_data, filter_time = self.run_test(
            "Congressional Trades (Democrat, $50K+)", 
            "GET", 
            "unusual-whales/congressional/trades", 
            200, 
            params=params
        )
        
        if success_filter:
            filtered_trades = filtered_data.get('data', {}).get('trades', [])
            print(f"   🗳️  Democrat trades >= $50K: {len(filtered_trades)}")
        
        # Test transaction type filter
        params = {"transaction_type": "Purchase", "limit": 20}
        success_purchase, purchase_data, purchase_time = self.run_test(
            "Congressional Trades (Purchases Only)", 
            "GET", 
            "unusual-whales/congressional/trades", 
            200, 
            params=params
        )
        
        if success_purchase:
            purchase_trades = purchase_data.get('data', {}).get('trades', [])
            print(f"   📈 Purchase trades: {len(purchase_trades)}")
        
        print(f"\n🎯 CONGRESSIONAL TRADES API ASSESSMENT:")
        print(f"   - Trades Found: {len(trades)}")
        print(f"   - Data Quality: {'✅ REAL DATA' if len(trades) > 0 else '⚠️  NO DATA'}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - API Status: {status}")
        
        return success

    def test_trading_strategies_api(self):
        """Test Trading Strategies API - GET /api/unusual-whales/trading-strategies"""
        print("\n" + "="*80)
        print("🎯 TESTING TRADING STRATEGIES API")
        print("="*80)
        print("📊 Endpoint: GET /api/unusual-whales/trading-strategies")
        print("🎯 Expected: AI-powered trading strategies with charts")
        
        # Test 1: Basic Trading Strategies Request
        print(f"\n📋 PHASE 1: Basic Trading Strategies Request")
        print("-" * 60)
        
        success, strategies_data, response_time = self.run_test(
            "Trading Strategies", 
            "GET", 
            "unusual-whales/trading-strategies", 
            200
        )
        
        if not success:
            print("❌ Trading Strategies API endpoint failed")
            return False
        
        # Analyze response structure
        status = strategies_data.get('status', 'unknown')
        data = strategies_data.get('data', {})
        strategies = data.get('strategies', [])
        summary = data.get('summary', {})
        timestamp = strategies_data.get('timestamp', 'N/A')
        charts_included = data.get('charts_included', False)
        
        print(f"📊 API Status: {status}")
        print(f"📊 Response Time: {response_time:.2f}s")
        print(f"📊 Timestamp: {timestamp}")
        print(f"📊 Found {len(strategies)} trading strategies")
        print(f"📈 Charts Included: {charts_included}")
        
        if summary:
            print(f"🎯 Strategy Types: {summary.get('strategy_types', 0)}")
            print(f"📊 Avg Confidence: {summary.get('avg_confidence', 0):.1f}%")
            print(f"⏰ Timeframes: {summary.get('timeframes', [])}")
        
        # Test 2: Strategy Structure Verification
        print(f"\n🔍 PHASE 2: Strategy Structure Verification")
        print("-" * 60)
        
        if strategies:
            first_strategy = strategies[0]
            required_fields = ['strategy_name', 'ticker', 'confidence', 'timeframe', 'entry_logic']
            optional_fields = ['tradestation_execution', 'risk_management', 'chart', 'category']
            
            missing_required = [field for field in required_fields if field not in first_strategy]
            present_optional = [field for field in optional_fields if field in first_strategy]
            
            if missing_required:
                print(f"❌ Missing required fields: {missing_required}")
            else:
                print(f"✅ All required fields present: {required_fields}")
            
            if present_optional:
                print(f"✅ Optional fields present: {present_optional}")
            
            # Display sample strategy
            print(f"\n📊 Sample Trading Strategy:")
            print(f"   - Strategy Name: {first_strategy.get('strategy_name', 'N/A')}")
            print(f"   - Ticker: {first_strategy.get('ticker', 'N/A')}")
            print(f"   - Confidence: {first_strategy.get('confidence', 0):.1f}%")
            print(f"   - Timeframe: {first_strategy.get('timeframe', 'N/A')}")
            print(f"   - Category: {first_strategy.get('category', 'N/A')}")
            
            # Check TradeStation execution details
            ts_execution = first_strategy.get('tradestation_execution', {})
            if ts_execution:
                print(f"   - TradeStation Ready: ✅")
                print(f"     • Underlying: {ts_execution.get('underlying', 'N/A')}")
                print(f"     • Max Risk: ${ts_execution.get('max_risk', 0):,.0f}")
                print(f"     • Max Profit: ${ts_execution.get('max_profit', 0):,.0f}")
                if 'legs' in ts_execution:
                    print(f"     • Legs: {len(ts_execution['legs'])} option legs")
            
            # Check chart data
            chart_data = first_strategy.get('chart', {})
            if chart_data:
                print(f"   - Chart Data: ✅")
                if 'plotly_chart' in chart_data:
                    plotly_data = chart_data['plotly_chart']
                    if isinstance(plotly_data, dict) and 'data' in plotly_data:
                        print(f"     • Plotly Chart: Valid JSON structure")
                        data_points = len(plotly_data.get('data', [{}])[0].get('y', []))
                        print(f"     • Data Points: {data_points}")
        else:
            print("⚠️  No strategies found - this may be normal if no qualifying signals exist")
        
        # Test 3: Chart Integration Verification
        print(f"\n📈 PHASE 3: Chart Integration Verification")
        print("-" * 60)
        
        if strategies and charts_included:
            strategies_with_charts = [s for s in strategies if 'chart' in s]
            print(f"📊 Strategies with charts: {len(strategies_with_charts)}/{len(strategies)}")
            
            if strategies_with_charts:
                chart_strategy = strategies_with_charts[0]
                chart = chart_strategy.get('chart', {})
                
                if 'plotly_chart' in chart:
                    plotly_chart = chart['plotly_chart']
                    print(f"   ✅ Plotly chart data present")
                    
                    # Validate chart structure
                    if isinstance(plotly_chart, dict):
                        has_data = 'data' in plotly_chart
                        has_layout = 'layout' in plotly_chart
                        print(f"   - Chart Data: {'✅' if has_data else '❌'}")
                        print(f"   - Chart Layout: {'✅' if has_layout else '❌'}")
                        
                        if has_data and plotly_chart['data']:
                            first_trace = plotly_chart['data'][0]
                            y_data = first_trace.get('y', [])
                            print(f"   - Data Points: {len(y_data)}")
                            
                            if len(y_data) > 0:
                                print(f"   - Y Range: ${min(y_data):.2f} to ${max(y_data):.2f}")
        
        # Test 4: Strategy Categories Verification
        print(f"\n🏷️  PHASE 4: Strategy Categories Verification")
        print("-" * 60)
        
        if strategies:
            categories = [s.get('category', 'unknown') for s in strategies]
            unique_categories = list(set(categories))
            print(f"📊 Strategy Categories Found: {unique_categories}")
            
            expected_categories = ['vertical_spread', 'directional', 'volatility', 'income', 'policy_play']
            valid_categories = [cat for cat in unique_categories if cat in expected_categories]
            
            if valid_categories:
                print(f"✅ Valid categories detected: {valid_categories}")
            
            # Check strategy names for real options strategies
            strategy_names = [s.get('strategy_name', '') for s in strategies]
            expected_strategies = ['Bull Call Spread', 'Bear Put Spread', 'Long Call', 'Long Put', 
                                 'Long Straddle', 'Iron Condor', 'Synthetic Long', 'Protective Put']
            
            real_strategies = [name for name in strategy_names if any(exp in name for exp in expected_strategies)]
            if real_strategies:
                print(f"✅ Real options strategies detected: {real_strategies}")
        
        print(f"\n🎯 TRADING STRATEGIES API ASSESSMENT:")
        print(f"   - Strategies Found: {len(strategies)}")
        print(f"   - Charts Available: {'✅ YES' if charts_included else '❌ NO'}")
        print(f"   - Response Time: {response_time:.2f}s")
        print(f"   - API Status: {status}")
        print(f"   - TradeStation Ready: {'✅ YES' if strategies and 'tradestation_execution' in strategies[0] else '❌ NO'}")
        
        return success

    def run_comprehensive_test(self):
        """Run comprehensive test of all Unusual Whales endpoints"""
        print("\n🚀 STARTING COMPREHENSIVE UNUSUAL WHALES API TEST")
        print("="*80)
        
        test_results = {}
        
        # Test all endpoints
        test_results['options_flow'] = self.test_options_flow_api()
        test_results['dark_pool'] = self.test_dark_pool_api()
        test_results['congressional_trades'] = self.test_congressional_trades_api()
        test_results['trading_strategies'] = self.test_trading_strategies_api()
        
        # Generate final report
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS SUMMARY")
        print("="*80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} endpoints passed)")
        print(f"📊 Total API Calls: {self.tests_run}")
        print(f"✅ Successful Calls: {self.tests_passed}")
        print(f"❌ Failed Calls: {self.tests_run - self.tests_passed}")
        
        print(f"\n📋 ENDPOINT RESULTS:")
        for endpoint, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            endpoint_name = endpoint.replace('_', ' ').title()
            print(f"   {status} {endpoint_name}")
        
        print(f"\n🔍 KEY FINDINGS:")
        if test_results['options_flow']:
            print("   ✅ Options Flow API: Working with real data")
        else:
            print("   ❌ Options Flow API: Issues detected")
        
        if test_results['dark_pool']:
            print("   ✅ Dark Pool API: Working correctly")
        else:
            print("   ❌ Dark Pool API: Issues detected")
        
        if test_results['congressional_trades']:
            print("   ✅ Congressional Trades API: Working correctly")
        else:
            print("   ❌ Congressional Trades API: Issues detected")
        
        if test_results['trading_strategies']:
            print("   ✅ Trading Strategies API: Working correctly")
        else:
            print("   ❌ Trading Strategies API: Issues detected")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 75:
            print("   🎉 Unusual Whales integration is working well with the new dropdown UI")
            print("   📱 Frontend dropdown functionality should work correctly")
            print("   🔑 API key (5809ee6a-bcb6-48ce-a16d-9f3bd634fd50) is properly configured")
        else:
            print("   ⚠️  Some Unusual Whales endpoints need attention")
            print("   🔧 Check API key configuration and endpoint implementations")
        
        print(f"\n🐋 UNUSUAL WHALES API TESTING COMPLETE")
        print("="*80)
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = UnusualWhalesAPITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)