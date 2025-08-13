import requests
import sys
from datetime import datetime, timedelta
import json

class StockMarketAPITester:
    def __init__(self, base_url="https://stockflow-app-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_market_overview(self):
        """Test market overview endpoint"""
        return self.run_test("Market Overview", "GET", "market/overview", 200)

    def test_top_movers(self):
        """Test top movers endpoint"""
        return self.run_test("Top Movers", "GET", "market/top-movers", 200)

    def test_stock_data(self, symbol="AAPL"):
        """Test stock data endpoint - CRITICAL: Check for real prices"""
        success, stock_data = self.run_test(f"Stock Data ({symbol})", "GET", f"stocks/{symbol}", 200)
        if success and symbol == "AAPL":
            price = stock_data.get('price', 0)
            print(f"   💰 {symbol} Price: ${price:.2f} (Expected ~$227, NOT $0.00)")
            if price == 0.0:
                print(f"   ❌ CRITICAL: {symbol} showing $0.00 price!")
            elif price > 200:
                print(f"   ✅ GOOD: {symbol} showing real price")
        return success

    def test_stock_history(self, symbol="AAPL"):
        """Test stock history endpoint"""
        return self.run_test(f"Stock History ({symbol})", "GET", f"stocks/{symbol}/history", 200, params={"period": "1mo"})

    def test_technical_indicators(self, symbol="AAPL"):
        """Test technical indicators endpoint"""
        return self.run_test(f"Technical Indicators ({symbol})", "GET", f"stocks/{symbol}/indicators", 200)

    def test_stock_search(self, query="AAPL"):
        """Test stock search endpoint"""
        return self.run_test(f"Stock Search ({query})", "GET", f"stocks/search/{query}", 200)

    def test_portfolio_operations(self):
        """Test portfolio CRUD operations"""
        # Test getting empty portfolio
        success, portfolio_data = self.run_test("Get Portfolio (Empty)", "GET", "portfolio", 200)
        
        # Test adding portfolio item
        portfolio_item = {
            "symbol": "AAPL",
            "shares": 10.0,
            "purchase_price": 150.0,
            "purchase_date": (datetime.now() - timedelta(days=30)).isoformat()
        }
        
        success, add_response = self.run_test("Add Portfolio Item", "POST", "portfolio", 200, data=portfolio_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting portfolio with item
            self.run_test("Get Portfolio (With Items)", "GET", "portfolio", 200)
            
            # Test deleting portfolio item
            self.run_test("Delete Portfolio Item", "DELETE", f"portfolio/{item_id}", 200)
        
        return success

    def test_watchlist_operations(self):
        """Test watchlist CRUD operations"""
        # Test getting empty watchlist
        self.run_test("Get Watchlist (Empty)", "GET", "watchlist", 200)
        
        # Test adding watchlist item
        watchlist_item = {
            "symbol": "GOOGL",
            "target_price": 2800.0,
            "notes": "Test watchlist item"
        }
        
        success, add_response = self.run_test("Add Watchlist Item", "POST", "watchlist", 200, data=watchlist_item)
        
        if success and 'id' in add_response:
            item_id = add_response['id']
            
            # Test getting watchlist with item
            self.run_test("Get Watchlist (With Items)", "GET", "watchlist", 200)
            
            # Test deleting watchlist item
            self.run_test("Delete Watchlist Item", "DELETE", f"watchlist/{item_id}", 200)
        
        return success

    def test_ticker_endpoints(self):
        """Test new ticker endpoints for S&P 500 and NASDAQ"""
        # Test S&P 500 tickers
        success, sp500_data = self.run_test("S&P 500 Tickers", "GET", "tickers/sp500", 200)
        if success and 'tickers' in sp500_data:
            print(f"   Found {len(sp500_data['tickers'])} S&P 500 tickers")
        
        # Test NASDAQ tickers
        success, nasdaq_data = self.run_test("NASDAQ Tickers", "GET", "tickers/nasdaq", 200)
        if success and 'tickers' in nasdaq_data:
            print(f"   Found {len(nasdaq_data['tickers'])} NASDAQ tickers")
        
        # Test all tickers
        success, all_data = self.run_test("All Tickers", "GET", "tickers/all", 200)
        if success and 'tickers' in all_data:
            print(f"   Found {len(all_data['tickers'])} total tickers")
        
        return success

    def test_screener_endpoints(self):
        """Test advanced screener endpoints - CRITICAL: Check for real prices (not $0.00)"""
        # Test basic screener data
        success, screener_data = self.run_test("Screener Data (All)", "GET", "screener/data", 200, params={"limit": 20, "exchange": "all"})
        if success and 'stocks' in screener_data:
            print(f"   Found {len(screener_data['stocks'])} stocks in screener")
            
            # CRITICAL CHECK: Verify real prices (not $0.00)
            zero_price_count = 0
            real_price_count = 0
            for stock in screener_data['stocks']:
                if stock.get('price', 0) == 0.0:
                    zero_price_count += 1
                else:
                    real_price_count += 1
                    if stock['symbol'] == 'AAPL':
                        print(f"   ✅ AAPL Price: ${stock['price']:.2f} (Expected ~$227)")
                    elif stock['symbol'] == 'ABT':
                        print(f"   ✅ ABT Price: ${stock['price']:.2f} (Expected ~$131)")
            
            print(f"   📊 Price Analysis: {real_price_count} real prices, {zero_price_count} zero prices")
            if zero_price_count > real_price_count:
                print(f"   ⚠️  WARNING: More zero prices than real prices!")
        
        # Test S&P 500 screener data
        success, sp500_screener = self.run_test("Screener Data (S&P 500)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "sp500"})
        if success and 'stocks' in sp500_screener:
            print(f"   Found {len(sp500_screener['stocks'])} S&P 500 stocks")
        
        # Test NASDAQ screener data
        success, nasdaq_screener = self.run_test("Screener Data (NASDAQ)", "GET", "screener/data", 200, params={"limit": 15, "exchange": "nasdaq"})
        if success and 'stocks' in nasdaq_screener:
            print(f"   Found {len(nasdaq_screener['stocks'])} NASDAQ stocks")
        
        # Test screener sectors
        self.run_test("Available Sectors", "GET", "screener/sectors", 200)
        
        # Test advanced filtering
        filter_criteria = {
            "min_price": 50.0,
            "max_price": 500.0,
            "min_market_cap": 1000.0,  # 1B market cap
            "sector": "Technology"
        }
        
        success, filtered_data = self.run_test("Advanced Filter (Tech Stocks)", "POST", "screener/filter", 200, data=filter_criteria)
        if success and 'stocks' in filtered_data:
            print(f"   Found {len(filtered_data['stocks'])} filtered stocks")
        
        # Test filter with P/E ratio
        pe_filter = {
            "min_pe": 10.0,
            "max_pe": 30.0,
            "min_volume": 1000000
        }
        
        success, pe_filtered = self.run_test("P/E Ratio Filter", "POST", "screener/filter", 200, data=pe_filter)
        if success and 'stocks' in pe_filtered:
            print(f"   Found {len(pe_filtered['stocks'])} stocks with P/E 10-30")
        
        return success

    def test_enhanced_stock_endpoints(self):
        """Test NEW enhanced stock endpoints with real-time data and extended hours"""
        # Test enhanced stock data for AAPL
        success, aapl_enhanced = self.run_test("Enhanced Stock Data (AAPL)", "GET", "stocks/AAPL/enhanced", 200)
        if success:
            print(f"   ✅ AAPL Enhanced Price: ${aapl_enhanced.get('price', 0):.2f}")
            print(f"   Market State: {aapl_enhanced.get('market_state', 'UNKNOWN')}")
            if 'extended_hours' in aapl_enhanced:
                extended = aapl_enhanced['extended_hours']
                if 'premarket' in extended:
                    print(f"   📈 Premarket Data: ${extended['premarket'].get('price', 'N/A')}")
                if 'postmarket' in extended:
                    print(f"   📉 Postmarket Data: ${extended['postmarket'].get('price', 'N/A')}")
        
        # Test extended hours endpoint
        success, extended_hours = self.run_test("Extended Hours Data (AAPL)", "GET", "stocks/AAPL/extended-hours", 200)
        if success:
            print(f"   Market State: {extended_hours.get('market_state', 'UNKNOWN')}")
            print(f"   Regular Price: ${extended_hours.get('regular_price', 0):.2f}")
        
        # Test enhanced data for other popular stocks
        for symbol in ["MSFT", "GOOGL", "TSLA"]:
            success, enhanced_data = self.run_test(f"Enhanced Stock Data ({symbol})", "GET", f"stocks/{symbol}/enhanced", 200)
            if success and enhanced_data.get('price', 0) > 0:
                print(f"   ✅ {symbol} Price: ${enhanced_data['price']:.2f}")
        
        return success

    def test_investment_scoring_endpoints(self):
        """Test NEW Investment Scoring System endpoints - PRIORITY FEATURE"""
        print("\n🎯 Testing Investment Scoring System - NEW FEATURE")
        
        # Test top investment picks
        success, top_picks_data = self.run_test("Investment Top Picks", "GET", "investments/top-picks", 200, params={"limit": 10})
        if success and 'recommendations' in top_picks_data:
            recommendations = top_picks_data['recommendations']
            print(f"   Found {len(recommendations)} top investment picks")
            
            # Check first recommendation structure
            if recommendations:
                first_pick = recommendations[0]
                print(f"   #1 Pick: {first_pick.get('symbol', 'N/A')} - Score: {first_pick.get('total_score', 'N/A')} - Rating: {first_pick.get('rating', 'N/A')}")
                print(f"   Risk Level: {first_pick.get('risk_level', 'N/A')}")
                
                # Verify required fields
                required_fields = ['symbol', 'total_score', 'rating', 'risk_level', 'key_strengths', 'key_risks']
                missing_fields = [field for field in required_fields if field not in first_pick]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in top pick: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present in top pick")
        
        # Test individual stock scoring - AAPL
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   AAPL Risk Level: {aapl_score.get('risk_level', 'N/A')}")
            
            # Check individual scores breakdown
            individual_scores = aapl_score.get('individual_scores', {})
            if individual_scores:
                print(f"   Score Breakdown: {len(individual_scores)} metrics")
                # Show a few key scores
                for key in ['pe_score', 'momentum_score', 'value_score']:
                    if key in individual_scores:
                        print(f"     {key}: {individual_scores[key]}")
        
        # Test sector leaders
        success, sector_data = self.run_test("Sector Leaders (Technology)", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"})
        if success and 'leaders' in sector_data:
            leaders = sector_data['leaders']
            print(f"   Found {len(leaders)} Technology sector leaders")
            if leaders:
                top_leader = leaders[0]
                print(f"   Top Tech Leader: {top_leader.get('symbol', 'N/A')} - Score: {top_leader.get('total_score', 'N/A')}")
        
        # Test different sector
        success, healthcare_data = self.run_test("Sector Leaders (Healthcare)", "GET", "investments/sector-leaders", 200, params={"sector": "Healthcare"})
        if success and 'leaders' in healthcare_data:
            leaders = healthcare_data['leaders']
            print(f"   Found {len(leaders)} Healthcare sector leaders")
        
        # Test risk analysis
        success, risk_data = self.run_test("Risk Analysis", "GET", "investments/risk-analysis", 200)
        if success and 'risk_categories' in risk_data:
            risk_categories = risk_data['risk_categories']
            print(f"   Risk Categories: {list(risk_categories.keys())}")
            
            for risk_level, stocks in risk_categories.items():
                print(f"   {risk_level} Risk: {len(stocks)} stocks")
                if stocks:
                    # Show first stock in each category
                    first_stock = stocks[0]
                    print(f"     Example: {first_stock.get('symbol', 'N/A')} - Score: {first_stock.get('total_score', 'N/A')}")
        
        return success

    def test_unusual_whales_options_flow(self):
        """Test Unusual Whales Options Flow API endpoints"""
        print("\n🐋 Testing Unusual Whales Options Flow API")
        
        # Test basic options flow alerts
        success, flow_data = self.run_test("Options Flow Alerts (Default)", "GET", "unusual-whales/options/flow-alerts", 200)
        if success:
            data = flow_data.get('data', {})
            alerts = data.get('alerts', [])
            summary = data.get('summary', {})
            
            print(f"   📊 Found {len(alerts)} options flow alerts")
            print(f"   💰 Total Premium: ${summary.get('total_premium', 0):,.0f}")
            print(f"   📈 Bullish Count: {summary.get('bullish_count', 0)}")
            print(f"   📉 Bearish Count: {summary.get('bearish_count', 0)}")
            print(f"   🔥 Unusual Activity: {summary.get('unusual_activity', 0)}")
            
            # Verify data structure
            if alerts:
                first_alert = alerts[0]
                required_fields = ['symbol', 'strike_type', 'premium', 'sentiment', 'volume']
                missing_fields = [field for field in required_fields if field not in first_alert]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in alert: {missing_fields}")
                else:
                    print(f"   ✅ Alert data structure complete")
                    print(f"   Example: {first_alert.get('symbol')} {first_alert.get('strike_type')} - ${first_alert.get('premium', 0):,.0f}")
        
        # Test with filters
        params = {
            "minimum_premium": 500000,
            "minimum_volume_oi_ratio": 2.0,
            "limit": 50,
            "include_analysis": True
        }
        success, filtered_data = self.run_test("Options Flow (Filtered)", "GET", "unusual-whales/options/flow-alerts", 200, params=params)
        if success:
            alerts = filtered_data.get('data', {}).get('alerts', [])
            analysis = filtered_data.get('analysis', {})
            print(f"   🔍 Filtered alerts: {len(alerts)} (premium >= $500K)")
            if analysis and 'signals' in analysis:
                signals = analysis.get('signals', [])
                print(f"   🎯 Trading signals generated: {len(signals)}")
                for signal in signals[:2]:  # Show first 2 signals
                    print(f"     - {signal.get('type', 'unknown')}: {signal.get('description', 'N/A')}")
        
        return success

    def test_unusual_whales_dark_pool(self):
        """Test Unusual Whales Dark Pool API endpoints"""
        print("\n🌊 Testing Unusual Whales Dark Pool API")
        
        # Test basic dark pool data
        success, dark_pool_data = self.run_test("Dark Pool Recent Activity", "GET", "unusual-whales/dark-pool/recent", 200)
        if success:
            data = dark_pool_data.get('data', {})
            trades = data.get('trades', [])
            summary = data.get('summary', {})
            
            print(f"   📊 Found {len(trades)} dark pool trades")
            print(f"   📈 Total Dark Volume: {summary.get('total_dark_volume', 0):,}")
            print(f"   🎯 Avg Dark %: {summary.get('avg_dark_percentage', 0):.1f}%")
            print(f"   🏛️  Institutional Signals: {summary.get('institutional_signals', 0)}")
            print(f"   🔥 High Significance: {summary.get('high_significance', 0)}")
            
            # Verify data structure
            if trades:
                first_trade = trades[0]
                required_fields = ['ticker', 'dark_volume', 'dark_percentage', 'significance']
                missing_fields = [field for field in required_fields if field not in first_trade]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in trade: {missing_fields}")
                else:
                    print(f"   ✅ Trade data structure complete")
                    print(f"   Example: {first_trade.get('ticker')} - {first_trade.get('dark_volume', 0):,} vol ({first_trade.get('dark_percentage', 0):.1f}% dark)")
        
        # Test with filters
        params = {
            "minimum_volume": 200000,
            "minimum_dark_percentage": 40.0,
            "limit": 25,
            "include_analysis": True
        }
        success, filtered_data = self.run_test("Dark Pool (Filtered)", "GET", "unusual-whales/dark-pool/recent", 200, params=params)
        if success:
            trades = filtered_data.get('data', {}).get('trades', [])
            analysis = filtered_data.get('analysis', {})
            print(f"   🔍 Filtered trades: {len(trades)} (vol >= 200K, dark >= 40%)")
            if analysis and 'implications' in analysis:
                implications = analysis.get('implications', [])
                print(f"   💡 Analysis implications: {len(implications)}")
                for implication in implications[:2]:
                    print(f"     - {implication.get('type', 'unknown')}: {implication.get('description', 'N/A')}")
        
        return success

    def test_unusual_whales_congressional_trades(self):
        """Test Unusual Whales Congressional Trades API endpoints"""
        print("\n🏛️  Testing Unusual Whales Congressional Trades API")
        
        # Test basic congressional trades
        success, congress_data = self.run_test("Congressional Trades", "GET", "unusual-whales/congressional/trades", 200)
        if success:
            data = congress_data.get('data', {})
            trades = data.get('trades', [])
            summary = data.get('summary', {})
            
            print(f"   📊 Found {len(trades)} congressional trades")
            print(f"   💰 Total Amount: ${summary.get('total_amount', 0):,.0f}")
            print(f"   👥 Unique Representatives: {summary.get('unique_representatives', 0)}")
            print(f"   📈 Unique Tickers: {summary.get('unique_tickers', 0)}")
            print(f"   🕐 Recent Trades (7d): {summary.get('recent_trades', 0)}")
            
            # Show party breakdown
            party_breakdown = summary.get('party_breakdown', {})
            if party_breakdown:
                print(f"   🗳️  Party Breakdown:")
                for party, count in party_breakdown.items():
                    print(f"     - {party}: {count} trades")
            
            # Show transaction type breakdown
            transaction_breakdown = summary.get('transaction_type_breakdown', {})
            if transaction_breakdown:
                print(f"   💼 Transaction Types:")
                for tx_type, count in transaction_breakdown.items():
                    print(f"     - {tx_type}: {count} trades")
            
            # Verify data structure
            if trades:
                first_trade = trades[0]
                required_fields = ['representative', 'party', 'ticker', 'transaction_type', 'transaction_amount']
                missing_fields = [field for field in required_fields if field not in first_trade]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in trade: {missing_fields}")
                else:
                    print(f"   ✅ Trade data structure complete")
                    print(f"   Example: {first_trade.get('representative')} ({first_trade.get('party')}) - {first_trade.get('transaction_type')} {first_trade.get('ticker')} ${first_trade.get('transaction_amount', 0):,.0f}")
        
        # Test with filters
        params = {
            "days_back": 14,
            "minimum_amount": 50000,
            "party_filter": "Democrat",
            "transaction_type": "Purchase",
            "limit": 20,
            "include_analysis": True
        }
        success, filtered_data = self.run_test("Congressional Trades (Filtered)", "GET", "unusual-whales/congressional/trades", 200, params=params)
        if success:
            trades = filtered_data.get('data', {}).get('trades', [])
            analysis = filtered_data.get('analysis', {})
            print(f"   🔍 Filtered trades: {len(trades)} (Democrat purchases >= $50K, 14d)")
            if analysis and 'insights' in analysis:
                insights = analysis.get('insights', [])
                print(f"   💡 Analysis insights: {len(insights)}")
                for insight in insights[:2]:
                    print(f"     - {insight.get('type', 'unknown')}: {insight.get('description', 'N/A')}")
        
        return success

    def test_unusual_whales_trading_strategies(self):
        """Test Unusual Whales Trading Strategies API endpoint with ENHANCED CHART INTEGRATION"""
        print("\n🎯 Testing Unusual Whales Trading Strategies API - ENHANCED WITH CHARTS")
        
        success, strategies_data = self.run_test("Trading Strategies Generation", "GET", "unusual-whales/trading-strategies", 200)
        if success:
            strategies = strategies_data.get('trading_strategies', [])  # Updated field name
            charts_included = strategies_data.get('charts_included', False)
            
            print(f"   📊 Generated {len(strategies)} trading strategies")
            print(f"   📈 Charts Included: {'✅ YES' if charts_included else '❌ NO'}")
            
            # Test chart integration for each strategy
            chart_test_results = {
                'total_strategies': len(strategies),
                'strategies_with_charts': 0,
                'chart_types_found': set(),
                'plotly_charts_valid': 0,
                'chart_errors': 0
            }
            
            if strategies:
                print(f"\n   🎨 CHART INTEGRATION TESTING:")
                
                for i, strategy in enumerate(strategies):
                    strategy_name = strategy.get('strategy_name', f'Strategy {i+1}')
                    print(f"   📋 Strategy {i+1}: {strategy_name}")
                    
                    # Test 1: Check if strategy has chart field
                    if 'chart' in strategy:
                        chart_test_results['strategies_with_charts'] += 1
                        chart_data = strategy['chart']
                        
                        # Test 2: Verify chart data structure
                        if 'chart_type' in chart_data:
                            chart_type = chart_data['chart_type']
                            chart_test_results['chart_types_found'].add(chart_type)
                            print(f"     - Chart Type: {chart_type}")
                            
                            # Test 3: Verify plotly chart JSON
                            if 'plotly_chart' in chart_data:
                                try:
                                    plotly_json = chart_data['plotly_chart']
                                    if isinstance(plotly_json, str):
                                        # Try to parse JSON
                                        import json
                                        parsed_chart = json.loads(plotly_json)
                                        if 'data' in parsed_chart and 'layout' in parsed_chart:
                                            chart_test_results['plotly_charts_valid'] += 1
                                            print(f"     - Plotly Chart: ✅ Valid JSON structure")
                                            
                                            # Test 4: Verify chart contains P&L data
                                            if 'data' in parsed_chart and len(parsed_chart['data']) > 0:
                                                first_trace = parsed_chart['data'][0]
                                                if 'x' in first_trace and 'y' in first_trace:
                                                    print(f"     - P&L Data Points: ✅ {len(first_trace['x'])} points")
                                                else:
                                                    print(f"     - P&L Data Points: ❌ Missing x/y data")
                                            
                                            # Test 5: Verify chart metrics
                                            metrics_found = []
                                            if 'max_profit' in chart_data:
                                                metrics_found.append(f"Max Profit: ${chart_data['max_profit']:.0f}")
                                            if 'max_loss' in chart_data:
                                                metrics_found.append(f"Max Loss: ${chart_data['max_loss']:.0f}")
                                            if 'breakeven_points' in chart_data:
                                                be_points = chart_data['breakeven_points']
                                                if be_points:
                                                    metrics_found.append(f"Breakeven: ${be_points[0]:.2f}")
                                            if 'breakeven' in chart_data:
                                                metrics_found.append(f"Breakeven: ${chart_data['breakeven']:.2f}")
                                            
                                            if metrics_found:
                                                print(f"     - Chart Metrics: ✅ {', '.join(metrics_found)}")
                                            else:
                                                print(f"     - Chart Metrics: ⚠️  No metrics found")
                                        else:
                                            print(f"     - Plotly Chart: ❌ Invalid structure")
                                    else:
                                        print(f"     - Plotly Chart: ❌ Not a string")
                                except Exception as e:
                                    print(f"     - Plotly Chart: ❌ JSON parse error: {str(e)}")
                                    chart_test_results['chart_errors'] += 1
                            else:
                                print(f"     - Plotly Chart: ❌ Missing plotly_chart field")
                        else:
                            print(f"     - Chart Type: ❌ Missing chart_type field")
                            
                        # Test 6: Verify strategy-specific chart types
                        expected_chart_types = {
                            'bull call spread': 'vertical_spread',
                            'bear put spread': 'vertical_spread', 
                            'long call': 'directional',
                            'long put': 'directional',
                            'long straddle': 'volatility',
                            'long strangle': 'volatility',
                            'iron condor': 'iron_condor',
                            'cash-secured put': 'income',
                            'covered call': 'income'
                        }
                        
                        strategy_name_lower = strategy_name.lower()
                        expected_type = None
                        for name_pattern, chart_type in expected_chart_types.items():
                            if name_pattern in strategy_name_lower:
                                expected_type = chart_type
                                break
                        
                        if expected_type and 'chart' in strategy:
                            actual_type = strategy['chart'].get('chart_type')
                            if actual_type == expected_type:
                                print(f"     - Chart Type Match: ✅ {actual_type} (expected)")
                            else:
                                print(f"     - Chart Type Match: ⚠️  {actual_type} (expected {expected_type})")
                    else:
                        print(f"     - Chart: ❌ Missing chart field")
                
                # Print chart testing summary
                print(f"\n   📊 CHART TESTING SUMMARY:")
                print(f"     - Total Strategies: {chart_test_results['total_strategies']}")
                print(f"     - Strategies with Charts: {chart_test_results['strategies_with_charts']}")
                print(f"     - Valid Plotly Charts: {chart_test_results['plotly_charts_valid']}")
                print(f"     - Chart Types Found: {', '.join(chart_test_results['chart_types_found'])}")
                print(f"     - Chart Errors: {chart_test_results['chart_errors']}")
                
                # Calculate success rate
                if chart_test_results['total_strategies'] > 0:
                    chart_success_rate = (chart_test_results['plotly_charts_valid'] / chart_test_results['total_strategies']) * 100
                    print(f"     - Chart Success Rate: {chart_success_rate:.1f}%")
                
                # Test 7: Verify TradeStation execution details
                print(f"\n   🎯 TRADESTATION EXECUTION TESTING:")
                first_strategy = strategies[0]
                print(f"   💡 Top Strategy: {first_strategy.get('strategy_name', 'N/A')}")
                print(f"     - Ticker: {first_strategy.get('ticker', 'N/A')}")
                print(f"     - Type: {first_strategy.get('strategy_type', 'N/A')}")
                print(f"     - Confidence: {first_strategy.get('confidence', 0):.2f}")
                print(f"     - Timeframe: {first_strategy.get('timeframe', 'N/A')}")
                
                # Check TradeStation execution details
                tradestation = first_strategy.get('tradestation_execution', {})
                if tradestation:
                    print(f"     - TradeStation Ready: ✅")
                    print(f"       * Underlying: {tradestation.get('underlying', 'N/A')}")
                    print(f"       * Max Risk: {tradestation.get('max_risk', 'N/A')}")
                    print(f"       * Max Profit: {tradestation.get('max_profit', 'N/A')}")
                    print(f"       * Breakeven: {tradestation.get('breakeven', 'N/A')}")
                    
                    # Check legs structure
                    legs = tradestation.get('legs', [])
                    if legs:
                        print(f"       * Strategy Legs: {len(legs)} legs")
                        for j, leg in enumerate(legs):
                            action = leg.get('action', 'N/A')
                            strike = leg.get('strike', 'N/A')
                            option_type = leg.get('option_type', 'N/A')
                            print(f"         - Leg {j+1}: {action} {option_type} @ ${strike}")
                    else:
                        print(f"       * Strategy Legs: ❌ No legs found")
                else:
                    print(f"     - TradeStation Ready: ❌")
                
                # Verify required fields
                required_fields = ['strategy_name', 'ticker', 'confidence', 'entry_logic', 'risk_management', 'chart']
                missing_fields = [field for field in required_fields if field not in first_strategy]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in strategy: {missing_fields}")
                else:
                    print(f"   ✅ Strategy data structure complete with charts")
        
        return success

    def test_unusual_whales_comprehensive_analysis(self):
        """Test Unusual Whales Comprehensive Analysis API endpoint"""
        print("\n🔬 Testing Unusual Whales Comprehensive Analysis API")
        
        success, analysis_data = self.run_test("Comprehensive Analysis", "GET", "unusual-whales/analysis/comprehensive", 200)
        if success:
            comprehensive_analysis = analysis_data.get('comprehensive_analysis', {})
            market_outlook = analysis_data.get('market_outlook', {})
            data_summary = analysis_data.get('data_summary', {})
            
            print(f"   📊 Data Sources:")
            print(f"     - Options Alerts: {data_summary.get('options_alerts', 0)}")
            print(f"     - Dark Pool Trades: {data_summary.get('dark_pool_trades', 0)}")
            print(f"     - Congressional Trades: {data_summary.get('congressional_trades', 0)}")
            
            # Check each analysis component
            for source, analysis in comprehensive_analysis.items():
                data_available = analysis.get('data_available', False)
                print(f"   {source.replace('_', ' ').title()}: {'✅ Available' if data_available else '❌ No Data'}")
                
                if data_available and 'analysis' in analysis:
                    source_analysis = analysis['analysis']
                    if isinstance(source_analysis, dict):
                        if 'signals' in source_analysis:
                            signals = source_analysis.get('signals', [])
                            print(f"     - Signals: {len(signals)}")
                        if 'implications' in source_analysis:
                            implications = source_analysis.get('implications', [])
                            print(f"     - Implications: {len(implications)}")
                        if 'insights' in source_analysis:
                            insights = source_analysis.get('insights', [])
                            print(f"     - Insights: {len(insights)}")
            
            # Market outlook analysis
            print(f"   🔮 Market Outlook:")
            print(f"     - Overall Sentiment: {market_outlook.get('overall_sentiment', 'unknown')}")
            print(f"     - Confidence: {market_outlook.get('confidence', 'unknown')}")
            
            key_signals = market_outlook.get('key_signals', [])
            if key_signals:
                print(f"     - Key Signals ({len(key_signals)}):")
                for signal in key_signals[:3]:  # Show first 3
                    print(f"       * {signal}")
            
            recommended_actions = market_outlook.get('recommended_actions', [])
            if recommended_actions:
                print(f"     - Recommended Actions ({len(recommended_actions)}):")
                for action in recommended_actions[:2]:  # Show first 2
                    print(f"       * {action}")
            
            risk_factors = market_outlook.get('risk_factors', [])
            if risk_factors:
                print(f"     - Risk Factors ({len(risk_factors)}):")
                for risk in risk_factors[:2]:  # Show first 2
                    print(f"       * {risk}")
            
            # Verify comprehensive analysis structure
            required_components = ['options_flow', 'dark_pool', 'congressional']
            missing_components = [comp for comp in required_components if comp not in comprehensive_analysis]
            if missing_components:
                print(f"   ⚠️  Missing analysis components: {missing_components}")
            else:
                print(f"   ✅ All analysis components present")
        
        return success

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid stock symbol
        self.run_test("Invalid Stock Symbol", "GET", "stocks/INVALID123", 500)
        
        # Test invalid portfolio item deletion
        self.run_test("Delete Non-existent Portfolio Item", "DELETE", "portfolio/invalid-id", 404)
        
        # Test invalid watchlist item deletion
        self.run_test("Delete Non-existent Watchlist Item", "DELETE", "watchlist/invalid-id", 404)
        
        # Test invalid investment score
        self.run_test("Invalid Investment Score", "GET", "investments/score/INVALID123", 500)

def main():
    print("🚀 Starting Stock Market API Tests with Unusual Whales Integration")
    print("=" * 70)
    
    tester = StockMarketAPITester()
    
    # Test UNUSUAL WHALES API INTEGRATION - PRIORITY
    print("\n🐋 Testing UNUSUAL WHALES API INTEGRATION - PRIORITY FEATURE")
    print("=" * 70)
    tester.test_unusual_whales_options_flow()
    tester.test_unusual_whales_dark_pool()
    tester.test_unusual_whales_congressional_trades()
    tester.test_unusual_whales_trading_strategies()
    tester.test_unusual_whales_comprehensive_analysis()
    
    # Test NEW Investment Scoring System
    print("\n🎯 Testing Investment Scoring System")
    tester.test_investment_scoring_endpoints()
    
    # Test basic endpoints
    print("\n📊 Testing Basic Endpoints")
    tester.test_root_endpoint()
    tester.test_market_overview()
    tester.test_top_movers()
    
    # Test NEW ticker endpoints
    print("\n🎯 Testing Ticker Endpoints")
    tester.test_ticker_endpoints()
    
    # Test NEW screener endpoints
    print("\n🔍 Testing Advanced Screener Endpoints")
    tester.test_screener_endpoints()
    
    # Test NEW enhanced endpoints
    print("\n🚀 Testing Enhanced Stock Endpoints")
    tester.test_enhanced_stock_endpoints()
    
    # Test stock data endpoints
    print("\n📈 Testing Stock Data Endpoints")
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    for stock in popular_stocks:
        tester.test_stock_data(stock)
        tester.test_stock_history(stock)
        # Only test technical indicators for AAPL to avoid API rate limits
        if stock == "AAPL":
            tester.test_technical_indicators(stock)
        tester.test_stock_search(stock)
    
    # Test portfolio operations
    print("\n💼 Testing Portfolio Operations")
    tester.test_portfolio_operations()
    
    # Test watchlist operations
    print("\n⭐ Testing Watchlist Operations")
    tester.test_watchlist_operations()
    
    # Test error handling
    print("\n🚨 Testing Error Handling")
    tester.test_error_handling()
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())