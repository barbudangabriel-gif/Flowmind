import requests
import sys
from datetime import datetime
import json

class ETFDataTester:
    def __init__(self, base_url="https://chart-repair-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.etf_symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
        self.etf_names = {
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust',
            'DIA': 'SPDR Dow Jones Industrial Average ETF Trust',
            'IWM': 'iShares Russell 2000 ETF'
        }
        self.findings = {
            'options_flow': {},
            'dark_pool': {},
            'congressional_trades': {},
            'market_overview': {},
            'screener_data': {}
        }

    def make_request(self, method, endpoint, params=None, data=None):
        """Make API request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Status {response.status_code}", "detail": response.text}
                
        except Exception as e:
            return False, {"error": str(e)}

    def test_options_flow_for_etfs(self):
        """Test if ETFs appear in options flow alerts"""
        print("\n🐋 TESTING OPTIONS FLOW FOR ETFs")
        print("=" * 60)
        
        success, data = self.make_request('GET', 'unusual-whales/options/flow-alerts', 
                                        params={'limit': 100, 'minimum_premium': 50000})
        
        if not success:
            print(f"❌ Options Flow API failed: {data.get('error', 'Unknown error')}")
            return
        
        alerts = data.get('data', {}).get('alerts', [])
        print(f"📊 Total Options Flow Alerts: {len(alerts)}")
        
        etf_alerts = {}
        for alert in alerts:
            symbol = alert.get('symbol', '').upper()
            if symbol in self.etf_symbols:
                if symbol not in etf_alerts:
                    etf_alerts[symbol] = []
                etf_alerts[symbol].append(alert)
        
        print(f"\n🎯 ETF FINDINGS IN OPTIONS FLOW:")
        for etf in self.etf_symbols:
            if etf in etf_alerts:
                alerts_count = len(etf_alerts[etf])
                print(f"✅ {etf} ({self.etf_names[etf]}): {alerts_count} alerts found")
                
                # Show sample alert details
                sample_alert = etf_alerts[etf][0]
                print(f"   📈 Sample Alert: {sample_alert.get('strike_type', 'N/A')} - Premium: ${sample_alert.get('premium', 0):,.0f}")
                print(f"   📊 Sentiment: {sample_alert.get('sentiment', 'N/A')} | Volume: {sample_alert.get('volume', 0):,}")
                
                # Store findings
                self.findings['options_flow'][etf] = {
                    'found': True,
                    'count': alerts_count,
                    'sample_data': {
                        'premium': sample_alert.get('premium', 0),
                        'sentiment': sample_alert.get('sentiment', 'N/A'),
                        'volume': sample_alert.get('volume', 0),
                        'strike_type': sample_alert.get('strike_type', 'N/A')
                    }
                }
            else:
                print(f"❌ {etf} ({self.etf_names[etf]}): No alerts found")
                self.findings['options_flow'][etf] = {'found': False, 'count': 0}
        
        # Summary statistics
        total_etf_alerts = sum(len(alerts) for alerts in etf_alerts.values())
        total_premium = sum(alert.get('premium', 0) for alerts in etf_alerts.values() for alert in alerts)
        
        print(f"\n📊 OPTIONS FLOW ETF SUMMARY:")
        print(f"   - ETFs with alerts: {len(etf_alerts)}/4")
        print(f"   - Total ETF alerts: {total_etf_alerts}")
        print(f"   - Total ETF premium: ${total_premium:,.0f}")

    def test_dark_pool_for_etfs(self):
        """Test if ETFs appear in dark pool data"""
        print("\n🌊 TESTING DARK POOL FOR ETFs")
        print("=" * 60)
        
        success, data = self.make_request('GET', 'unusual-whales/dark-pool/recent',
                                        params={'limit': 100, 'minimum_volume': 50000})
        
        if not success:
            print(f"❌ Dark Pool API failed: {data.get('error', 'Unknown error')}")
            return
        
        trades = data.get('data', {}).get('trades', [])
        print(f"📊 Total Dark Pool Trades: {len(trades)}")
        
        etf_trades = {}
        for trade in trades:
            ticker = trade.get('ticker', '').upper()
            if ticker in self.etf_symbols:
                if ticker not in etf_trades:
                    etf_trades[ticker] = []
                etf_trades[ticker].append(trade)
        
        print(f"\n🎯 ETF FINDINGS IN DARK POOL:")
        for etf in self.etf_symbols:
            if etf in etf_trades:
                trades_count = len(etf_trades[etf])
                print(f"✅ {etf} ({self.etf_names[etf]}): {trades_count} trades found")
                
                # Show sample trade details
                sample_trade = etf_trades[etf][0]
                print(f"   📊 Sample Trade: Dark Volume: {sample_trade.get('dark_volume', 0):,}")
                print(f"   📈 Dark %: {sample_trade.get('dark_percentage', 0):.1f}% | Significance: {sample_trade.get('significance', 'N/A')}")
                
                # Store findings
                self.findings['dark_pool'][etf] = {
                    'found': True,
                    'count': trades_count,
                    'sample_data': {
                        'dark_volume': sample_trade.get('dark_volume', 0),
                        'dark_percentage': sample_trade.get('dark_percentage', 0),
                        'significance': sample_trade.get('significance', 'N/A'),
                        'institutional_signal': sample_trade.get('institutional_signal', False)
                    }
                }
            else:
                print(f"❌ {etf} ({self.etf_names[etf]}): No trades found")
                self.findings['dark_pool'][etf] = {'found': False, 'count': 0}
        
        # Summary statistics
        total_etf_trades = sum(len(trades) for trades in etf_trades.values())
        total_dark_volume = sum(trade.get('dark_volume', 0) for trades in etf_trades.values() for trade in trades)
        
        print(f"\n📊 DARK POOL ETF SUMMARY:")
        print(f"   - ETFs with trades: {len(etf_trades)}/4")
        print(f"   - Total ETF trades: {total_etf_trades}")
        print(f"   - Total dark volume: {total_dark_volume:,}")

    def test_congressional_trades_for_etfs(self):
        """Test if ETFs appear in congressional trades"""
        print("\n🏛️ TESTING CONGRESSIONAL TRADES FOR ETFs")
        print("=" * 60)
        
        success, data = self.make_request('GET', 'unusual-whales/congressional/trades',
                                        params={'days_back': 90, 'minimum_amount': 1000, 'limit': 200})
        
        if not success:
            print(f"❌ Congressional Trades API failed: {data.get('error', 'Unknown error')}")
            return
        
        trades = data.get('data', {}).get('trades', [])
        print(f"📊 Total Congressional Trades: {len(trades)}")
        
        etf_trades = {}
        for trade in trades:
            ticker = trade.get('ticker', '').upper()
            if ticker in self.etf_symbols:
                if ticker not in etf_trades:
                    etf_trades[ticker] = []
                etf_trades[ticker].append(trade)
        
        print(f"\n🎯 ETF FINDINGS IN CONGRESSIONAL TRADES:")
        for etf in self.etf_symbols:
            if etf in etf_trades:
                trades_count = len(etf_trades[etf])
                print(f"✅ {etf} ({self.etf_names[etf]}): {trades_count} trades found")
                
                # Show sample trade details
                sample_trade = etf_trades[etf][0]
                print(f"   👤 Sample Trade: {sample_trade.get('representative', 'N/A')} ({sample_trade.get('party', 'N/A')})")
                print(f"   💰 Amount: ${sample_trade.get('transaction_amount', 0):,.0f} | Type: {sample_trade.get('transaction_type', 'N/A')}")
                print(f"   📅 Date: {sample_trade.get('transaction_date', 'N/A')}")
                
                # Store findings
                self.findings['congressional_trades'][etf] = {
                    'found': True,
                    'count': trades_count,
                    'sample_data': {
                        'representative': sample_trade.get('representative', 'N/A'),
                        'party': sample_trade.get('party', 'N/A'),
                        'transaction_amount': sample_trade.get('transaction_amount', 0),
                        'transaction_type': sample_trade.get('transaction_type', 'N/A'),
                        'transaction_date': sample_trade.get('transaction_date', 'N/A')
                    }
                }
            else:
                print(f"❌ {etf} ({self.etf_names[etf]}): No trades found")
                self.findings['congressional_trades'][etf] = {'found': False, 'count': 0}
        
        # Summary statistics
        total_etf_trades = sum(len(trades) for trades in etf_trades.values())
        total_amount = sum(trade.get('transaction_amount', 0) for trades in etf_trades.values() for trade in trades)
        
        print(f"\n📊 CONGRESSIONAL TRADES ETF SUMMARY:")
        print(f"   - ETFs with trades: {len(etf_trades)}/4")
        print(f"   - Total ETF trades: {total_etf_trades}")
        print(f"   - Total trade amount: ${total_amount:,.0f}")

    def test_market_overview_etf_data(self):
        """Test if ETF data is available in market overview (already uses ETFs)"""
        print("\n📊 TESTING MARKET OVERVIEW ETF DATA")
        print("=" * 60)
        
        success, data = self.make_request('GET', 'market/overview')
        
        if not success:
            print(f"❌ Market Overview API failed: {data.get('error', 'Unknown error')}")
            return
        
        indices = data.get('indices', [])
        print(f"📊 Market Overview Indices: {len(indices)}")
        
        etf_data = {}
        for index in indices:
            underlying_symbol = index.get('underlying_symbol', '').upper()
            if underlying_symbol in self.etf_symbols:
                etf_data[underlying_symbol] = index
        
        print(f"\n🎯 ETF DATA IN MARKET OVERVIEW:")
        for etf in self.etf_symbols:
            if etf in etf_data:
                index_data = etf_data[etf]
                print(f"✅ {etf} ({self.etf_names[etf]}): Available")
                print(f"   💰 Price: ${index_data.get('price', 0):.2f}")
                print(f"   📈 Change: {index_data.get('change', 0):+.2f} ({index_data.get('change_percent', 0):+.2f}%)")
                print(f"   🐋 Unusual Activity: {index_data.get('unusual_activity', False)}")
                print(f"   📊 Options Flow Signal: {index_data.get('options_flow_signal', 'N/A')}")
                print(f"   📺 Display Symbol: {index_data.get('symbol', 'N/A')}")
                
                # Store findings
                self.findings['market_overview'][etf] = {
                    'found': True,
                    'price': index_data.get('price', 0),
                    'change': index_data.get('change', 0),
                    'change_percent': index_data.get('change_percent', 0),
                    'unusual_activity': index_data.get('unusual_activity', False),
                    'options_flow_signal': index_data.get('options_flow_signal', 'N/A'),
                    'display_symbol': index_data.get('symbol', 'N/A')
                }
            else:
                print(f"❌ {etf} ({self.etf_names[etf]}): Not found")
                self.findings['market_overview'][etf] = {'found': False}
        
        print(f"\n📊 MARKET OVERVIEW ETF SUMMARY:")
        print(f"   - ETFs available: {len(etf_data)}/4")
        print(f"   - Data source: {data.get('data_source', 'Unknown')}")
        print(f"   - Unusual Whales coverage: {data.get('unusual_whales_coverage', 'N/A')}")

    def test_screener_data_for_etfs(self):
        """Test if ETFs appear in screener data"""
        print("\n🔍 TESTING SCREENER DATA FOR ETFs")
        print("=" * 60)
        
        success, data = self.make_request('GET', 'screener/data', 
                                        params={'limit': 100, 'exchange': 'all'})
        
        if not success:
            print(f"❌ Screener Data API failed: {data.get('error', 'Unknown error')}")
            return
        
        stocks = data.get('stocks', [])
        print(f"📊 Total Screener Stocks: {len(stocks)}")
        
        etf_stocks = {}
        for stock in stocks:
            symbol = stock.get('symbol', '').upper()
            if symbol in self.etf_symbols:
                etf_stocks[symbol] = stock
        
        print(f"\n🎯 ETF FINDINGS IN SCREENER DATA:")
        for etf in self.etf_symbols:
            if etf in etf_stocks:
                stock_data = etf_stocks[etf]
                print(f"✅ {etf} ({self.etf_names[etf]}): Found in screener")
                print(f"   💰 Price: ${stock_data.get('price', 0):.2f}")
                print(f"   📈 Change: {stock_data.get('change_percent', 0):+.2f}%")
                print(f"   📊 Volume: {stock_data.get('volume', 0):,}")
                print(f"   🐋 Unusual Activity: {stock_data.get('unusual_activity', False)}")
                print(f"   📊 Options Flow Signal: {stock_data.get('options_flow_signal', 'N/A')}")
                
                # Store findings
                self.findings['screener_data'][etf] = {
                    'found': True,
                    'price': stock_data.get('price', 0),
                    'change_percent': stock_data.get('change_percent', 0),
                    'volume': stock_data.get('volume', 0),
                    'unusual_activity': stock_data.get('unusual_activity', False),
                    'options_flow_signal': stock_data.get('options_flow_signal', 'N/A'),
                    'market_cap': stock_data.get('market_cap', 0)
                }
            else:
                print(f"❌ {etf} ({self.etf_names[etf]}): Not found in screener")
                self.findings['screener_data'][etf] = {'found': False}
        
        print(f"\n📊 SCREENER DATA ETF SUMMARY:")
        print(f"   - ETFs found: {len(etf_stocks)}/4")
        print(f"   - Data source: {data.get('data_source', 'Unknown')}")

    def generate_comprehensive_report(self):
        """Generate comprehensive report of ETF data findings"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE ETF DATA EXTRACTION REPORT")
        print("=" * 80)
        
        # Summary table
        print(f"\n📊 ETF AVAILABILITY ACROSS ENDPOINTS:")
        print(f"{'ETF':<6} {'Options Flow':<13} {'Dark Pool':<11} {'Congressional':<13} {'Market Overview':<15} {'Screener':<10}")
        print("-" * 80)
        
        for etf in self.etf_symbols:
            options_status = "✅ YES" if self.findings['options_flow'].get(etf, {}).get('found', False) else "❌ NO"
            dark_pool_status = "✅ YES" if self.findings['dark_pool'].get(etf, {}).get('found', False) else "❌ NO"
            congress_status = "✅ YES" if self.findings['congressional_trades'].get(etf, {}).get('found', False) else "❌ NO"
            market_status = "✅ YES" if self.findings['market_overview'].get(etf, {}).get('found', False) else "❌ NO"
            screener_status = "✅ YES" if self.findings['screener_data'].get(etf, {}).get('found', False) else "❌ NO"
            
            print(f"{etf:<6} {options_status:<13} {dark_pool_status:<11} {congress_status:<13} {market_status:<15} {screener_status:<10}")
        
        # Best data sources for each ETF
        print(f"\n🏆 BEST DATA SOURCES FOR EACH ETF:")
        for etf in self.etf_symbols:
            print(f"\n📈 {etf} ({self.etf_names[etf]}):")
            
            available_sources = []
            
            # Check each endpoint
            if self.findings['market_overview'].get(etf, {}).get('found', False):
                price = self.findings['market_overview'][etf]['price']
                available_sources.append(f"Market Overview (Price: ${price:.2f})")
            
            if self.findings['screener_data'].get(etf, {}).get('found', False):
                price = self.findings['screener_data'][etf]['price']
                volume = self.findings['screener_data'][etf]['volume']
                available_sources.append(f"Screener Data (Price: ${price:.2f}, Volume: {volume:,})")
            
            if self.findings['options_flow'].get(etf, {}).get('found', False):
                count = self.findings['options_flow'][etf]['count']
                available_sources.append(f"Options Flow ({count} alerts)")
            
            if self.findings['dark_pool'].get(etf, {}).get('found', False):
                count = self.findings['dark_pool'][etf]['count']
                available_sources.append(f"Dark Pool ({count} trades)")
            
            if self.findings['congressional_trades'].get(etf, {}).get('found', False):
                count = self.findings['congressional_trades'][etf]['count']
                available_sources.append(f"Congressional Trades ({count} trades)")
            
            if available_sources:
                for source in available_sources:
                    print(f"   ✅ {source}")
            else:
                print(f"   ❌ No data sources available")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR ETF DATA EXTRACTION:")
        
        # Count available sources per ETF
        etf_source_counts = {}
        for etf in self.etf_symbols:
            count = 0
            if self.findings['options_flow'].get(etf, {}).get('found', False): count += 1
            if self.findings['dark_pool'].get(etf, {}).get('found', False): count += 1
            if self.findings['congressional_trades'].get(etf, {}).get('found', False): count += 1
            if self.findings['market_overview'].get(etf, {}).get('found', False): count += 1
            if self.findings['screener_data'].get(etf, {}).get('found', False): count += 1
            etf_source_counts[etf] = count
        
        # Primary recommendation
        best_etf = max(etf_source_counts, key=etf_source_counts.get)
        best_count = etf_source_counts[best_etf]
        
        print(f"\n🎯 PRIMARY RECOMMENDATION:")
        print(f"   - Best ETF for data extraction: {best_etf} ({best_count}/5 endpoints)")
        
        # Endpoint recommendations
        market_overview_count = sum(1 for etf in self.etf_symbols if self.findings['market_overview'].get(etf, {}).get('found', False))
        screener_count = sum(1 for etf in self.etf_symbols if self.findings['screener_data'].get(etf, {}).get('found', False))
        options_count = sum(1 for etf in self.etf_symbols if self.findings['options_flow'].get(etf, {}).get('found', False))
        
        print(f"\n📊 ENDPOINT RECOMMENDATIONS:")
        if market_overview_count >= 3:
            print(f"   ✅ Use Market Overview endpoint for ETF prices ({market_overview_count}/4 ETFs available)")
        if screener_count >= 3:
            print(f"   ✅ Use Screener Data endpoint for ETF details ({screener_count}/4 ETFs available)")
        if options_count >= 2:
            print(f"   ✅ Use Options Flow endpoint for ETF activity ({options_count}/4 ETFs available)")
        
        # Implementation strategy
        print(f"\n🛠️ IMPLEMENTATION STRATEGY:")
        print(f"   1. Primary: Use Market Overview endpoint for real-time ETF prices")
        print(f"   2. Secondary: Use Screener Data endpoint for detailed ETF information")
        print(f"   3. Activity: Monitor Options Flow and Dark Pool for ETF unusual activity")
        print(f"   4. Sentiment: Check Congressional Trades for ETF insider activity")
        
        # API endpoints summary
        print(f"\n🔗 RECOMMENDED API ENDPOINTS FOR ETF DATA:")
        print(f"   - Real-time Prices: GET /api/market/overview")
        print(f"   - Detailed Data: GET /api/screener/data?exchange=all")
        print(f"   - Options Activity: GET /api/unusual-whales/options/flow-alerts")
        print(f"   - Dark Pool Activity: GET /api/unusual-whales/dark-pool/recent")
        print(f"   - Congressional Activity: GET /api/unusual-whales/congressional/trades")

    def run_all_tests(self):
        """Run all ETF data extraction tests"""
        print("🐋 UNUSUAL WHALES ETF DATA EXTRACTION TESTING")
        print("=" * 80)
        print("Testing ETF data availability in Unusual Whales endpoints")
        print(f"Target ETFs: {', '.join(self.etf_symbols)}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_options_flow_for_etfs()
        self.test_dark_pool_for_etfs()
        self.test_congressional_trades_for_etfs()
        self.test_market_overview_etf_data()
        self.test_screener_data_for_etfs()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

if __name__ == "__main__":
    tester = ETFDataTester()
    tester.run_all_tests()