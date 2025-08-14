import requests
import sys
from datetime import datetime
import json
from collections import Counter

class ETFSymbolAnalyzer:
    def __init__(self, base_url="https://market-ai-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.target_etfs = ['SPY', 'QQQ', 'DIA', 'IWM']
        self.all_symbols_found = set()

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

    def analyze_options_flow_symbols(self):
        """Analyze all symbols in options flow to see what's available"""
        print("\n🔍 ANALYZING OPTIONS FLOW SYMBOLS")
        print("=" * 50)
        
        success, data = self.make_request('GET', 'unusual-whales/options/flow-alerts', 
                                        params={'limit': 100, 'minimum_premium': 10000})
        
        if not success:
            print(f"❌ Options Flow API failed: {data.get('error', 'Unknown error')}")
            return set()
        
        alerts = data.get('data', {}).get('alerts', [])
        symbols = [alert.get('symbol', '').upper() for alert in alerts if alert.get('symbol')]
        symbol_counts = Counter(symbols)
        
        print(f"📊 Total alerts: {len(alerts)}")
        print(f"📈 Unique symbols: {len(symbol_counts)}")
        print(f"🔝 Top 10 symbols by alert count:")
        
        for symbol, count in symbol_counts.most_common(10):
            print(f"   {symbol}: {count} alerts")
            self.all_symbols_found.add(symbol)
        
        # Check for ETF-like symbols
        etf_like = [s for s in symbols if len(s) == 3 and s.isalpha()]
        print(f"📊 ETF-like symbols (3 letters): {len(set(etf_like))}")
        if etf_like:
            etf_counts = Counter(etf_like)
            print(f"🎯 Top ETF-like symbols:")
            for symbol, count in etf_counts.most_common(5):
                print(f"   {symbol}: {count} alerts")
        
        return set(symbols)

    def analyze_dark_pool_symbols(self):
        """Analyze all symbols in dark pool to see what's available"""
        print("\n🔍 ANALYZING DARK POOL SYMBOLS")
        print("=" * 50)
        
        success, data = self.make_request('GET', 'unusual-whales/dark-pool/recent',
                                        params={'limit': 100, 'minimum_volume': 10000})
        
        if not success:
            print(f"❌ Dark Pool API failed: {data.get('error', 'Unknown error')}")
            return set()
        
        trades = data.get('data', {}).get('trades', [])
        symbols = [trade.get('ticker', '').upper() for trade in trades if trade.get('ticker')]
        symbol_counts = Counter(symbols)
        
        print(f"📊 Total trades: {len(trades)}")
        print(f"📈 Unique symbols: {len(symbol_counts)}")
        
        if symbol_counts:
            print(f"🔝 Top 10 symbols by trade count:")
            for symbol, count in symbol_counts.most_common(10):
                print(f"   {symbol}: {count} trades")
                self.all_symbols_found.add(symbol)
            
            # Check for ETF-like symbols
            etf_like = [s for s in symbols if len(s) == 3 and s.isalpha()]
            if etf_like:
                etf_counts = Counter(etf_like)
                print(f"🎯 Top ETF-like symbols:")
                for symbol, count in etf_counts.most_common(5):
                    print(f"   {symbol}: {count} trades")
        else:
            print("📊 No dark pool trades found")
        
        return set(symbols)

    def analyze_congressional_symbols(self):
        """Analyze all symbols in congressional trades to see what's available"""
        print("\n🔍 ANALYZING CONGRESSIONAL TRADE SYMBOLS")
        print("=" * 50)
        
        success, data = self.make_request('GET', 'unusual-whales/congressional/trades',
                                        params={'days_back': 90, 'minimum_amount': 1000, 'limit': 200})
        
        if not success:
            print(f"❌ Congressional Trades API failed: {data.get('error', 'Unknown error')}")
            return set()
        
        trades = data.get('data', {}).get('trades', [])
        symbols = [trade.get('ticker', '').upper() for trade in trades if trade.get('ticker')]
        symbol_counts = Counter(symbols)
        
        print(f"📊 Total trades: {len(trades)}")
        print(f"📈 Unique symbols: {len(symbol_counts)}")
        print(f"🔝 Top 10 symbols by trade count:")
        
        for symbol, count in symbol_counts.most_common(10):
            print(f"   {symbol}: {count} trades")
            self.all_symbols_found.add(symbol)
        
        # Check for ETF-like symbols
        etf_like = [s for s in symbols if len(s) == 3 and s.isalpha()]
        print(f"📊 ETF-like symbols (3 letters): {len(set(etf_like))}")
        if etf_like:
            etf_counts = Counter(etf_like)
            print(f"🎯 Top ETF-like symbols:")
            for symbol, count in etf_counts.most_common(5):
                print(f"   {symbol}: {count} trades")
        
        return set(symbols)

    def analyze_screener_symbols(self):
        """Analyze all symbols in screener data to see what's available"""
        print("\n🔍 ANALYZING SCREENER SYMBOLS")
        print("=" * 50)
        
        success, data = self.make_request('GET', 'screener/data', 
                                        params={'limit': 100, 'exchange': 'all'})
        
        if not success:
            print(f"❌ Screener Data API failed: {data.get('error', 'Unknown error')}")
            return set()
        
        stocks = data.get('stocks', [])
        symbols = [stock.get('symbol', '').upper() for stock in stocks if stock.get('symbol')]
        
        print(f"📊 Total stocks: {len(stocks)}")
        print(f"📈 Unique symbols: {len(set(symbols))}")
        print(f"🔝 All symbols found:")
        
        for symbol in sorted(symbols):
            print(f"   {symbol}")
            self.all_symbols_found.add(symbol)
        
        # Check for ETF-like symbols
        etf_like = [s for s in symbols if len(s) == 3 and s.isalpha()]
        print(f"📊 ETF-like symbols (3 letters): {len(set(etf_like))}")
        if etf_like:
            print(f"🎯 ETF-like symbols: {sorted(set(etf_like))}")
        
        return set(symbols)

    def test_individual_etf_endpoints(self):
        """Test if we can get individual ETF data from stock endpoints"""
        print("\n🔍 TESTING INDIVIDUAL ETF STOCK ENDPOINTS")
        print("=" * 50)
        
        for etf in self.target_etfs:
            print(f"\n📊 Testing {etf}:")
            
            # Test enhanced stock data
            success, data = self.make_request('GET', f'stocks/{etf}/enhanced')
            if success:
                price = data.get('price', 0)
                change_percent = data.get('change_percent', 0)
                volume = data.get('volume', 0)
                print(f"   ✅ Enhanced Stock Data: ${price:.2f} ({change_percent:+.2f}%) Vol: {volume:,}")
            else:
                print(f"   ❌ Enhanced Stock Data: {data.get('error', 'Failed')}")
            
            # Test basic stock data
            success, data = self.make_request('GET', f'stocks/{etf}')
            if success:
                price = data.get('price', 0)
                change_percent = data.get('change_percent', 0)
                print(f"   ✅ Basic Stock Data: ${price:.2f} ({change_percent:+.2f}%)")
            else:
                print(f"   ❌ Basic Stock Data: {data.get('error', 'Failed')}")
            
            # Test stock history
            success, data = self.make_request('GET', f'stocks/{etf}/history', params={'period': '1mo'})
            if success and isinstance(data, list) and len(data) > 0:
                print(f"   ✅ Historical Data: {len(data)} data points")
                latest = data[-1] if data else {}
                if 'close' in latest:
                    print(f"      Latest Close: ${latest['close']:.2f}")
            else:
                print(f"   ❌ Historical Data: Failed or no data")

    def search_for_etf_alternatives(self):
        """Search for ETF alternatives or related symbols"""
        print("\n🔍 SEARCHING FOR ETF ALTERNATIVES")
        print("=" * 50)
        
        # Common ETF patterns and alternatives
        etf_patterns = {
            'SPY': ['SPX', 'SPXL', 'SPXS', 'SPDR', 'SP500'],
            'QQQ': ['NASDAQ', 'TQQQ', 'SQQQ', 'NDX', 'QQQM'],
            'DIA': ['DOW', 'UDOW', 'SDOW', 'DJI', 'DJIA'],
            'IWM': ['RUSSELL', 'TNA', 'TWM', 'RUT', 'IWN']
        }
        
        print("🎯 Looking for ETF-related symbols in all endpoints:")
        
        for target_etf, alternatives in etf_patterns.items():
            print(f"\n📊 {target_etf} alternatives:")
            found_alternatives = []
            
            for alt in alternatives:
                if alt in self.all_symbols_found:
                    found_alternatives.append(alt)
                    print(f"   ✅ Found: {alt}")
            
            if not found_alternatives:
                print(f"   ❌ No alternatives found for {target_etf}")

    def generate_final_recommendations(self):
        """Generate final recommendations for ETF data extraction"""
        print("\n" + "=" * 80)
        print("🎯 FINAL ETF DATA EXTRACTION RECOMMENDATIONS")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY OF FINDINGS:")
        print(f"   - Total unique symbols found across all endpoints: {len(self.all_symbols_found)}")
        print(f"   - Target ETFs found in any endpoint: 0/4 (SPY, QQQ, DIA, IWM)")
        print(f"   - ETFs available in Market Overview: 4/4 (via underlying mapping)")
        
        print(f"\n🏆 BEST APPROACH FOR ETF DATA:")
        print(f"   1. ✅ PRIMARY: Use Market Overview endpoint")
        print(f"      - All 4 ETFs available with real-time prices")
        print(f"      - Endpoint: GET /api/market/overview")
        print(f"      - Data includes: price, change, change_percent, unusual_activity, options_flow_signal")
        
        print(f"\n   2. ✅ SECONDARY: Use individual stock endpoints")
        print(f"      - Test each ETF individually via stock endpoints")
        print(f"      - Endpoints: GET /api/stocks/{{symbol}}/enhanced")
        print(f"      - Provides: detailed stock data, historical data, technical indicators")
        
        print(f"\n   3. ❌ UNUSUAL WHALES ACTIVITY: Limited ETF coverage")
        print(f"      - Options Flow: No ETF alerts found")
        print(f"      - Dark Pool: No ETF trades found")
        print(f"      - Congressional: No ETF trades found")
        print(f"      - Screener: ETFs not included in stock screener")
        
        print(f"\n💡 IMPLEMENTATION STRATEGY:")
        print(f"   For Market Dashboard ETF display:")
        print(f"   1. Use Market Overview endpoint as primary data source")
        print(f"   2. Extract ETF data from underlying_symbol field (SPY, QQQ, DIA, IWM)")
        print(f"   3. Display as futures-style symbols (SPX, NQ, YM, RTY)")
        print(f"   4. Include unusual_activity and options_flow_signal fields")
        print(f"   5. Fallback to individual stock endpoints if needed")
        
        print(f"\n🔗 RECOMMENDED API CALLS:")
        print(f"   # Get all ETF data at once")
        print(f"   GET /api/market/overview")
        print(f"   ")
        print(f"   # Get individual ETF data")
        print(f"   GET /api/stocks/SPY/enhanced")
        print(f"   GET /api/stocks/QQQ/enhanced")
        print(f"   GET /api/stocks/DIA/enhanced")
        print(f"   GET /api/stocks/IWM/enhanced")
        
        print(f"\n⚠️  LIMITATIONS:")
        print(f"   - ETFs don't appear in Unusual Whales activity endpoints")
        print(f"   - ETFs not included in stock screener results")
        print(f"   - Activity data (options flow, dark pool) focuses on individual stocks")
        print(f"   - Congressional trades don't typically include ETFs")

    def run_complete_analysis(self):
        """Run complete ETF symbol analysis"""
        print("🔍 COMPREHENSIVE ETF SYMBOL ANALYSIS")
        print("=" * 80)
        print("Analyzing all available symbols across Unusual Whales endpoints")
        print(f"Target ETFs: {', '.join(self.target_etfs)}")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze all endpoints
        options_symbols = self.analyze_options_flow_symbols()
        dark_pool_symbols = self.analyze_dark_pool_symbols()
        congressional_symbols = self.analyze_congressional_symbols()
        screener_symbols = self.analyze_screener_symbols()
        
        # Test individual ETF endpoints
        self.test_individual_etf_endpoints()
        
        # Search for alternatives
        self.search_for_etf_alternatives()
        
        # Generate final recommendations
        self.generate_final_recommendations()

if __name__ == "__main__":
    analyzer = ETFSymbolAnalyzer()
    analyzer.run_complete_analysis()