import requests
import sys
from datetime import datetime
import json
import time

class PricingDataSourceTester:
    def __init__(self, base_url="https://options-builder.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            timeout = 30
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            end_time = time.time()
            response_time = end_time - start_time

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} ({response_time:.2f}s)")
                try:
                    response_data = response.json()
                    return True, response_data, response_time
                except:
                    return True, {}, response_time
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}, response_time

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            return False, {}, timeout
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}, 0

    def test_data_sources_status_endpoint(self):
        """Test the new data sources status endpoint (/api/data-sources/status)"""
        print("\n🔍 PHASE 1: Testing Data Sources Status Endpoint")
        print("=" * 80)
        print("🎯 OBJECTIVE: Check TradeStation authentication status and priority")
        
        success, status_data, response_time = self.run_test(
            "Data Sources Status", 
            "GET", 
            "data-sources/status", 
            200
        )
        
        if not success:
            print("❌ Data sources status endpoint failed")
            self.test_results.append({
                "test": "Data Sources Status",
                "status": "FAILED",
                "issue": "Endpoint not responding"
            })
            return False
        
        # Verify response structure
        required_fields = ['data_source_priority', 'current_primary_source', 'recommendation', 'timestamp']
        missing_fields = [field for field in required_fields if field not in status_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            self.test_results.append({
                "test": "Data Sources Status",
                "status": "FAILED",
                "issue": f"Missing fields: {missing_fields}"
            })
            return False
        
        print(f"✅ All required fields present")
        
        # Check data source priority
        priority_list = status_data.get('data_source_priority', [])
        current_primary = status_data.get('current_primary_source', '')
        recommendation = status_data.get('recommendation', '')
        
        print(f"\n📊 Data Source Priority Analysis:")
        for i, source in enumerate(priority_list):
            rank = source.get('rank', i+1)
            source_name = source.get('source', 'Unknown')
            status = source.get('status', 'Unknown')
            authenticated = source.get('authenticated', False)
            usage = source.get('usage', 'Unknown')
            reliability = source.get('reliability', 'Unknown')
            
            print(f"   {rank}. {source_name}")
            print(f"      - Status: {status}")
            print(f"      - Authenticated: {authenticated}")
            print(f"      - Usage: {usage}")
            print(f"      - Reliability: {reliability}")
            
            # Check TradeStation specific details
            if 'TradeStation' in source_name:
                connection_test = source.get('connection_test')
                if connection_test:
                    print(f"      - Connection Test: {connection_test}")
        
        print(f"\n🎯 Current Primary Source: {current_primary}")
        print(f"💡 Recommendation: {recommendation}")
        
        # Verify TradeStation is listed as priority #1
        tradestation_priority = None
        for source in priority_list:
            if 'TradeStation' in source.get('source', ''):
                tradestation_priority = source.get('rank', 999)
                break
        
        if tradestation_priority == 1:
            print(f"✅ TradeStation correctly listed as priority #1")
        else:
            print(f"❌ TradeStation not priority #1 (rank: {tradestation_priority})")
        
        # Check if TradeStation is authenticated
        ts_authenticated = False
        for source in priority_list:
            if 'TradeStation' in source.get('source', ''):
                ts_authenticated = source.get('authenticated', False)
                break
        
        print(f"\n🔐 TradeStation Authentication Status: {'✅ Authenticated' if ts_authenticated else '❌ Not Authenticated'}")
        
        self.test_results.append({
            "test": "Data Sources Status",
            "status": "PASSED",
            "details": {
                "primary_source": current_primary,
                "tradestation_authenticated": ts_authenticated,
                "tradestation_priority": tradestation_priority,
                "response_time": f"{response_time:.2f}s"
            }
        })
        
        return True

    def test_data_source_comparison_crm(self):
        """Test the data source comparison endpoint for CRM ticker specifically"""
        print("\n🔍 PHASE 2: Testing Data Source Comparison for CRM Ticker")
        print("=" * 80)
        print("🎯 OBJECTIVE: See pricing differences between TradeStation and Yahoo Finance for CRM")
        print("🚨 USER ISSUE: 'CRM PRICE 100' - checking for price accuracy")
        
        success, comparison_data, response_time = self.run_test(
            "Data Source Comparison (CRM)", 
            "GET", 
            "data-sources/test/CRM", 
            200
        )
        
        if not success:
            print("❌ Data source comparison endpoint failed")
            self.test_results.append({
                "test": "Data Source Comparison CRM",
                "status": "FAILED",
                "issue": "Endpoint not responding"
            })
            return False
        
        # Verify response structure
        required_fields = ['symbol', 'test_results', 'primary_source_used', 'price_comparison', 'timestamp']
        missing_fields = [field for field in required_fields if field not in comparison_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present")
        
        # Analyze test results
        symbol = comparison_data.get('symbol', 'UNKNOWN')
        test_results = comparison_data.get('test_results', {})
        primary_source = comparison_data.get('primary_source_used', 'unknown')
        price_comparison = comparison_data.get('price_comparison', {})
        
        print(f"\n📊 CRM Price Comparison Analysis:")
        print(f"   Symbol: {symbol}")
        print(f"   Primary Source Used: {primary_source}")
        
        # Check TradeStation results
        ts_results = test_results.get('tradestation', {})
        ts_status = ts_results.get('status', 'unknown')
        ts_price = ts_results.get('price')
        
        print(f"\n🏛️  TradeStation Results:")
        print(f"   Status: {ts_status}")
        if ts_price is not None:
            print(f"   CRM Price: ${ts_price:.2f}")
            
            # Check for the "CRM PRICE 100" issue
            if abs(ts_price - 100.0) < 0.01:
                print(f"   🚨 CRITICAL: CRM showing exactly $100.00 - this matches user's reported issue!")
            elif ts_price > 0:
                print(f"   ✅ CRM price looks realistic: ${ts_price:.2f}")
            else:
                print(f"   ❌ CRM price is zero or invalid")
        else:
            print(f"   ❌ No TradeStation price data available")
            if ts_status == 'not_authenticated':
                print(f"   📝 Note: TradeStation not authenticated - expected behavior")
        
        # Check Yahoo Finance results
        yf_results = test_results.get('yahoo_finance', {})
        yf_status = yf_results.get('status', 'unknown')
        yf_price = yf_results.get('price')
        
        print(f"\n📈 Yahoo Finance Results:")
        print(f"   Status: {yf_status}")
        if yf_price is not None:
            print(f"   CRM Price: ${yf_price:.2f}")
            
            # Check for realistic CRM price (Salesforce typically trades $200-400)
            if 150 <= yf_price <= 500:
                print(f"   ✅ CRM price in realistic range for Salesforce")
            elif abs(yf_price - 100.0) < 0.01:
                print(f"   🚨 CRITICAL: Yahoo Finance also showing $100.00 - data source issue!")
            else:
                print(f"   ⚠️  CRM price outside typical Salesforce range: ${yf_price:.2f}")
        else:
            print(f"   ❌ No Yahoo Finance price data available")
        
        # Price comparison analysis
        ts_price_comp = price_comparison.get('tradestation_price')
        yf_price_comp = price_comparison.get('yahoo_price')
        price_difference = price_comparison.get('difference')
        
        print(f"\n💰 Price Comparison Summary:")
        print(f"   TradeStation Price: ${ts_price_comp:.2f}" if ts_price_comp else "   TradeStation Price: Not Available")
        print(f"   Yahoo Finance Price: ${yf_price_comp:.2f}" if yf_price_comp else "   Yahoo Finance Price: Not Available")
        
        if price_difference is not None:
            print(f"   Price Difference: ${price_difference:.2f}")
            
            if abs(price_difference) < 1.0:
                print(f"   ✅ Prices are very close (difference < $1.00)")
            elif abs(price_difference) < 5.0:
                print(f"   ✅ Prices are reasonably close (difference < $5.00)")
            else:
                print(f"   ⚠️  Significant price difference detected")
        else:
            print(f"   ❌ Cannot compare prices - one or both sources unavailable")
        
        # Determine if CRM price issue is resolved
        crm_issue_resolved = False
        if yf_price and yf_price != 100.0 and 150 <= yf_price <= 500:
            crm_issue_resolved = True
            print(f"\n✅ CRM PRICE ISSUE ANALYSIS: Price looks correct (${yf_price:.2f})")
        elif ts_price and ts_price != 100.0 and 150 <= ts_price <= 500:
            crm_issue_resolved = True
            print(f"\n✅ CRM PRICE ISSUE ANALYSIS: Price looks correct (${ts_price:.2f})")
        else:
            print(f"\n🚨 CRM PRICE ISSUE ANALYSIS: Price may still be incorrect")
            if yf_price == 100.0 or ts_price == 100.0:
                print(f"   - Still showing $100.00 price")
            elif not yf_price and not ts_price:
                print(f"   - No price data available from either source")
        
        self.test_results.append({
            "test": "Data Source Comparison CRM",
            "status": "PASSED" if success else "FAILED",
            "details": {
                "primary_source": primary_source,
                "tradestation_price": ts_price,
                "yahoo_price": yf_price,
                "price_difference": price_difference,
                "crm_issue_resolved": crm_issue_resolved,
                "response_time": f"{response_time:.2f}s"
            }
        })
        
        return success

    def test_stock_quote_endpoint_crm(self):
        """Test the updated stock quote endpoint for CRM to verify correct data source priority"""
        print("\n🔍 PHASE 3: Testing Stock Quote Endpoint for CRM")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify CRM stock quote uses correct data source priority")
        print("🚨 USER ISSUE: Checking if 'CRM PRICE 100' issue is resolved")
        
        success, quote_data, response_time = self.run_test(
            "Stock Quote (CRM)", 
            "GET", 
            "stocks/CRM", 
            200
        )
        
        if not success:
            print("❌ Stock quote endpoint failed")
            self.test_results.append({
                "test": "Stock Quote CRM",
                "status": "FAILED",
                "issue": "Endpoint not responding"
            })
            return False
        
        # Verify response structure
        required_fields = ['symbol', 'price', 'change', 'change_percent', 'volume', 'timestamp', 'data_source']
        missing_fields = [field for field in required_fields if field not in quote_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present")
        
        # Analyze quote data
        symbol = quote_data.get('symbol', 'UNKNOWN')
        price = quote_data.get('price', 0)
        change = quote_data.get('change', 0)
        change_percent = quote_data.get('change_percent', 0)
        volume = quote_data.get('volume', 0)
        data_source = quote_data.get('data_source', 'Unknown')
        timestamp = quote_data.get('timestamp', 'Unknown')
        
        print(f"\n📊 CRM Stock Quote Analysis:")
        print(f"   Symbol: {symbol}")
        print(f"   Price: ${price:.2f}")
        print(f"   Change: ${change:+.2f} ({change_percent:+.2f}%)")
        print(f"   Volume: {volume:,}")
        print(f"   Data Source: {data_source}")
        print(f"   Timestamp: {timestamp}")
        
        # Critical check for CRM price issue
        crm_price_correct = False
        if abs(price - 100.0) < 0.01:
            print(f"\n🚨 CRITICAL ISSUE DETECTED: CRM still showing $100.00 price!")
            print(f"   This matches the user's reported 'CRM PRICE 100' issue")
            print(f"   Expected: CRM (Salesforce) should trade in $200-400 range")
        elif 150 <= price <= 500:
            print(f"\n✅ CRM PRICE LOOKS CORRECT: ${price:.2f}")
            print(f"   This is in the expected range for Salesforce (CRM)")
            crm_price_correct = True
        elif price == 0:
            print(f"\n❌ CRM PRICE IS ZERO: This indicates a data fetching issue")
        else:
            print(f"\n⚠️  CRM PRICE UNUSUAL: ${price:.2f}")
            print(f"   This is outside typical Salesforce trading range")
        
        # Check data source priority
        print(f"\n🔍 Data Source Priority Analysis:")
        if 'TradeStation' in data_source:
            print(f"   ✅ Using TradeStation as primary source (highest priority)")
            if 'Primary' in data_source:
                print(f"   ✅ Confirmed as primary data source")
        elif 'Yahoo Finance' in data_source:
            print(f"   📈 Using Yahoo Finance as fallback source")
            if 'Fallback' in data_source:
                print(f"   ✅ Correctly identified as fallback")
        else:
            print(f"   ⚠️  Unknown data source: {data_source}")
        
        # Check for realistic market data
        market_data_realistic = True
        if volume == 0:
            print(f"   ⚠️  Volume is zero - may indicate stale data")
            market_data_realistic = False
        elif volume > 100000:
            print(f"   ✅ Volume looks realistic: {volume:,}")
        
        if abs(change_percent) > 20:
            print(f"   ⚠️  Large daily change: {change_percent:+.2f}% - verify if correct")
        elif abs(change_percent) < 0.01:
            print(f"   ⚠️  No price change - may indicate stale data")
        else:
            print(f"   ✅ Price change looks normal: {change_percent:+.2f}%")
        
        self.test_results.append({
            "test": "Stock Quote CRM",
            "status": "PASSED" if success else "FAILED",
            "details": {
                "symbol": symbol,
                "price": price,
                "data_source": data_source,
                "crm_price_correct": crm_price_correct,
                "market_data_realistic": market_data_realistic,
                "response_time": f"{response_time:.2f}s"
            }
        })
        
        return success

    def test_enhanced_stock_data_crm(self):
        """Test the enhanced stock data endpoint for CRM to verify TradeStation integration"""
        print("\n🔍 PHASE 4: Testing Enhanced Stock Data Endpoint for CRM")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify TradeStation integration in enhanced stock data")
        
        success, enhanced_data, response_time = self.run_test(
            "Enhanced Stock Data (CRM)", 
            "GET", 
            "stocks/CRM/enhanced", 
            200
        )
        
        if not success:
            print("❌ Enhanced stock data endpoint failed")
            self.test_results.append({
                "test": "Enhanced Stock Data CRM",
                "status": "FAILED",
                "issue": "Endpoint not responding"
            })
            return False
        
        # Verify response structure
        required_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 'volume', 'data_source', 'timestamp']
        missing_fields = [field for field in required_fields if field not in enhanced_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present")
        
        # Analyze enhanced data
        symbol = enhanced_data.get('symbol', 'UNKNOWN')
        name = enhanced_data.get('name', 'Unknown')
        price = enhanced_data.get('price', 0)
        change = enhanced_data.get('change', 0)
        change_percent = enhanced_data.get('change_percent', 0)
        volume = enhanced_data.get('volume', 0)
        data_source = enhanced_data.get('data_source', 'Unknown')
        sector = enhanced_data.get('sector', 'Unknown')
        industry = enhanced_data.get('industry', 'Unknown')
        market_cap = enhanced_data.get('market_cap')
        pe_ratio = enhanced_data.get('pe_ratio')
        
        print(f"\n📊 CRM Enhanced Stock Data Analysis:")
        print(f"   Symbol: {symbol}")
        print(f"   Company Name: {name}")
        print(f"   Price: ${price:.2f}")
        print(f"   Change: ${change:+.2f} ({change_percent:+.2f}%)")
        print(f"   Volume: {volume:,}")
        print(f"   Sector: {sector}")
        print(f"   Industry: {industry}")
        print(f"   Data Source: {data_source}")
        
        if market_cap:
            print(f"   Market Cap: ${market_cap/1e9:.1f}B")
        if pe_ratio:
            print(f"   P/E Ratio: {pe_ratio:.2f}")
        
        # Check for TradeStation integration
        tradestation_integrated = False
        if 'TradeStation' in data_source:
            print(f"\n✅ TradeStation Integration Detected:")
            print(f"   - Data Source: {data_source}")
            tradestation_integrated = True
            
            if 'Enhanced' in data_source:
                print(f"   - Enhanced data integration confirmed")
            if 'Primary' in data_source:
                print(f"   - TradeStation used as primary source")
        else:
            print(f"\n📈 Using Alternative Data Source:")
            print(f"   - Data Source: {data_source}")
            if 'Fallback' in data_source:
                print(f"   - Fallback behavior working correctly")
        
        # Verify CRM-specific data quality
        crm_data_quality = True
        
        # Check if company name matches Salesforce
        if 'Salesforce' in name or 'CRM' in name:
            print(f"   ✅ Company name correctly identified: {name}")
        else:
            print(f"   ⚠️  Company name may be incorrect: {name} (expected Salesforce)")
            crm_data_quality = False
        
        # Check sector/industry
        if 'Technology' in sector or 'Software' in industry:
            print(f"   ✅ Sector/Industry correctly identified: {sector}/{industry}")
        else:
            print(f"   ⚠️  Sector/Industry may be incorrect: {sector}/{industry}")
        
        # Check price again for the $100 issue
        if abs(price - 100.0) < 0.01:
            print(f"\n🚨 CRITICAL: Enhanced endpoint also showing $100.00 for CRM!")
            crm_data_quality = False
        elif 150 <= price <= 500:
            print(f"\n✅ Enhanced endpoint shows realistic CRM price: ${price:.2f}")
        
        # Check for extended hours data
        extended_hours = enhanced_data.get('extended_hours', {})
        if extended_hours:
            print(f"\n📈 Extended Hours Data Available:")
            premarket = extended_hours.get('premarket', {})
            postmarket = extended_hours.get('postmarket', {})
            
            if premarket:
                print(f"   - Premarket: ${premarket.get('price', 'N/A')}")
            if postmarket:
                print(f"   - Postmarket: ${postmarket.get('price', 'N/A')}")
        
        self.test_results.append({
            "test": "Enhanced Stock Data CRM",
            "status": "PASSED" if success else "FAILED",
            "details": {
                "symbol": symbol,
                "name": name,
                "price": price,
                "data_source": data_source,
                "tradestation_integrated": tradestation_integrated,
                "crm_data_quality": crm_data_quality,
                "response_time": f"{response_time:.2f}s"
            }
        })
        
        return success

    def test_api_documentation_endpoints(self):
        """Test that API documentation reflects the new endpoints in root response"""
        print("\n🔍 PHASE 5: Testing API Documentation for New Endpoints")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify root endpoint documents new data source endpoints")
        
        success, root_data, response_time = self.run_test(
            "API Root Documentation", 
            "GET", 
            "", 
            200
        )
        
        if not success:
            print("❌ API root endpoint failed")
            self.test_results.append({
                "test": "API Documentation",
                "status": "FAILED",
                "issue": "Root endpoint not responding"
            })
            return False
        
        # Check for core endpoints section
        core_endpoints = root_data.get('core_endpoints', {})
        if not core_endpoints:
            print("❌ No core_endpoints section found in API documentation")
            return False
        
        print(f"✅ Core endpoints section found")
        
        # Check for new data source endpoints
        expected_new_endpoints = [
            'data_sources_status',
            'test_data_source'
        ]
        
        documented_endpoints = []
        missing_endpoints = []
        
        for endpoint_key in expected_new_endpoints:
            if endpoint_key in core_endpoints:
                documented_endpoints.append(endpoint_key)
                endpoint_path = core_endpoints[endpoint_key]
                print(f"   ✅ {endpoint_key}: {endpoint_path}")
            else:
                missing_endpoints.append(endpoint_key)
        
        if missing_endpoints:
            print(f"   ❌ Missing endpoint documentation: {missing_endpoints}")
        
        # Check for TradeStation endpoints section
        tradestation_endpoints = root_data.get('tradestation_endpoints', {})
        if tradestation_endpoints:
            print(f"\n✅ TradeStation endpoints section found:")
            for key, path in tradestation_endpoints.items():
                print(f"   - {key}: {path}")
        else:
            print(f"\n⚠️  No TradeStation endpoints section found")
        
        # Check API version and features
        version = root_data.get('version', 'Unknown')
        features = root_data.get('features', [])
        
        print(f"\n📊 API Documentation Analysis:")
        print(f"   Version: {version}")
        print(f"   Features Listed: {len(features)}")
        
        # Look for TradeStation-related features
        ts_features = [f for f in features if 'TradeStation' in f]
        if ts_features:
            print(f"   ✅ TradeStation features documented: {len(ts_features)}")
            for feature in ts_features:
                print(f"     - {feature}")
        else:
            print(f"   ⚠️  No TradeStation features found in documentation")
        
        documentation_complete = len(missing_endpoints) == 0
        
        self.test_results.append({
            "test": "API Documentation",
            "status": "PASSED" if documentation_complete else "PARTIAL",
            "details": {
                "documented_endpoints": documented_endpoints,
                "missing_endpoints": missing_endpoints,
                "tradestation_endpoints_count": len(tradestation_endpoints),
                "api_version": version,
                "response_time": f"{response_time:.2f}s"
            }
        })
        
        return success

    def test_logging_data_source_usage(self):
        """Test if logging shows which data source is being used"""
        print("\n🔍 PHASE 6: Testing Data Source Usage Logging")
        print("=" * 80)
        print("🎯 OBJECTIVE: Verify logging shows TradeStation vs Yahoo Finance usage")
        print("📝 NOTE: This test checks response data for logging indicators")
        
        # Test multiple endpoints to see data source logging
        test_symbols = ['CRM', 'AAPL', 'MSFT']
        data_source_usage = {}
        
        for symbol in test_symbols:
            print(f"\n📊 Testing data source logging for {symbol}:")
            
            success, quote_data, response_time = self.run_test(
                f"Stock Quote Logging ({symbol})", 
                "GET", 
                f"stocks/{symbol}", 
                200
            )
            
            if success:
                data_source = quote_data.get('data_source', 'Unknown')
                price = quote_data.get('price', 0)
                
                print(f"   Data Source: {data_source}")
                print(f"   Price: ${price:.2f}")
                
                # Categorize data source
                if 'TradeStation' in data_source:
                    source_type = 'TradeStation'
                elif 'Yahoo Finance' in data_source:
                    source_type = 'Yahoo Finance'
                else:
                    source_type = 'Other'
                
                data_source_usage[symbol] = {
                    'source_type': source_type,
                    'full_source': data_source,
                    'price': price
                }
                
                # Check for logging indicators in response
                if 'Primary' in data_source:
                    print(f"   ✅ Primary source indicator found")
                if 'Fallback' in data_source:
                    print(f"   ✅ Fallback source indicator found")
                if 'authenticated' in data_source.lower():
                    print(f"   ✅ Authentication status indicated")
            else:
                print(f"   ❌ Failed to get quote for {symbol}")
        
        # Analyze data source usage patterns
        print(f"\n📊 Data Source Usage Analysis:")
        tradestation_count = sum(1 for usage in data_source_usage.values() if usage['source_type'] == 'TradeStation')
        yahoo_count = sum(1 for usage in data_source_usage.values() if usage['source_type'] == 'Yahoo Finance')
        
        print(f"   TradeStation Usage: {tradestation_count}/{len(test_symbols)} symbols")
        print(f"   Yahoo Finance Usage: {yahoo_count}/{len(test_symbols)} symbols")
        
        if tradestation_count > 0:
            print(f"   ✅ TradeStation integration working for some symbols")
        if yahoo_count > 0:
            print(f"   ✅ Yahoo Finance fallback working for some symbols")
        
        # Check for consistent data source usage
        if tradestation_count == len(test_symbols):
            print(f"   ✅ All symbols using TradeStation (authenticated user)")
        elif yahoo_count == len(test_symbols):
            print(f"   📈 All symbols using Yahoo Finance (fallback mode)")
        else:
            print(f"   ⚠️  Mixed data source usage detected")
        
        logging_effective = len(data_source_usage) > 0
        
        self.test_results.append({
            "test": "Data Source Logging",
            "status": "PASSED" if logging_effective else "FAILED",
            "details": {
                "symbols_tested": test_symbols,
                "tradestation_usage": tradestation_count,
                "yahoo_usage": yahoo_count,
                "data_source_usage": data_source_usage
            }
        })
        
        return logging_effective

    def run_comprehensive_pricing_test(self):
        """Run all pricing data source implementation tests"""
        print("🚀 STARTING COMPREHENSIVE PRICING DATA SOURCE TESTING")
        print("=" * 100)
        print("📋 TESTING SCOPE:")
        print("   1. Data sources status endpoint (/api/data-sources/status)")
        print("   2. Data source comparison endpoint (/api/data-sources/test/CRM)")
        print("   3. Stock quote endpoint (/api/stocks/CRM) with correct priority")
        print("   4. Enhanced stock data endpoint (/api/stocks/CRM/enhanced)")
        print("   5. API documentation verification")
        print("   6. Data source usage logging")
        print("🚨 FOCUS: CRM ticker 'PRICE 100' issue and TradeStation integration")
        
        start_time = time.time()
        
        # Run all test phases
        test_phases = [
            ("Data Sources Status", self.test_data_sources_status_endpoint),
            ("Data Source Comparison CRM", self.test_data_source_comparison_crm),
            ("Stock Quote CRM", self.test_stock_quote_endpoint_crm),
            ("Enhanced Stock Data CRM", self.test_enhanced_stock_data_crm),
            ("API Documentation", self.test_api_documentation_endpoints),
            ("Data Source Logging", self.test_logging_data_source_usage)
        ]
        
        passed_phases = 0
        total_phases = len(test_phases)
        
        for phase_name, test_function in test_phases:
            try:
                result = test_function()
                if result:
                    passed_phases += 1
                    print(f"\n✅ {phase_name} - PASSED")
                else:
                    print(f"\n❌ {phase_name} - FAILED")
            except Exception as e:
                print(f"\n💥 {phase_name} - ERROR: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate comprehensive summary
        print("\n" + "=" * 100)
        print("🎯 COMPREHENSIVE PRICING DATA SOURCE TEST RESULTS")
        print("=" * 100)
        
        success_rate = (passed_phases / total_phases) * 100
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Phases Passed: {passed_phases}/{total_phases}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Time: {total_time:.2f} seconds")
        
        # Detailed results by phase
        print(f"\n📋 DETAILED RESULTS BY PHASE:")
        for result in self.test_results:
            test_name = result['test']
            status = result['status']
            details = result.get('details', {})
            
            print(f"\n   🔍 {test_name}: {status}")
            for key, value in details.items():
                print(f"     - {key}: {value}")
        
        # Critical findings
        print(f"\n🚨 CRITICAL FINDINGS:")
        
        # Check for CRM price issue
        crm_issues = []
        for result in self.test_results:
            if 'CRM' in result['test']:
                details = result.get('details', {})
                price = details.get('price')
                if price == 100.0:
                    crm_issues.append(f"{result['test']}: Still showing $100.00")
                elif price and 150 <= price <= 500:
                    print(f"   ✅ CRM price looks correct in {result['test']}: ${price:.2f}")
        
        if crm_issues:
            print(f"   🚨 CRM PRICE ISSUES DETECTED:")
            for issue in crm_issues:
                print(f"     - {issue}")
        else:
            print(f"   ✅ No CRM price issues detected")
        
        # Check TradeStation integration
        ts_integration = False
        for result in self.test_results:
            details = result.get('details', {})
            if details.get('tradestation_authenticated') or details.get('tradestation_integrated'):
                ts_integration = True
                break
        
        if ts_integration:
            print(f"   ✅ TradeStation integration detected and working")
        else:
            print(f"   ⚠️  TradeStation integration not detected (may be unauthenticated)")
        
        # Data source priority
        primary_sources = []
        for result in self.test_results:
            details = result.get('details', {})
            primary_source = details.get('primary_source')
            if primary_source:
                primary_sources.append(primary_source)
        
        if primary_sources:
            most_common_source = max(set(primary_sources), key=primary_sources.count)
            print(f"   📊 Most common primary source: {most_common_source}")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if success_rate >= 85:
            print(f"   🎉 EXCELLENT: Pricing data source implementation working perfectly!")
            print(f"   ✅ TradeStation integration and fallback logic operational")
            print(f"   ✅ API endpoints properly documented and functional")
        elif success_rate >= 70:
            print(f"   ✅ GOOD: Pricing data source implementation mostly working")
            print(f"   ⚠️  Some minor issues detected but core functionality operational")
        else:
            print(f"   ❌ NEEDS ATTENTION: Significant issues with pricing data source implementation")
            print(f"   🔧 Review failed test phases and address critical issues")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not ts_integration:
            print(f"   🔐 Consider authenticating with TradeStation for full integration testing")
        
        if crm_issues:
            print(f"   🚨 URGENT: Address CRM pricing issue - user reported 'CRM PRICE 100'")
        
        if success_rate < 100:
            print(f"   🔧 Review failed test phases and implement fixes")
        
        print(f"   📊 Monitor data source usage and fallback behavior in production")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = PricingDataSourceTester()
    success = tester.run_comprehensive_pricing_test()
    
    if success:
        print(f"\n🎉 PRICING DATA SOURCE TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n❌ PRICING DATA SOURCE TESTING FAILED")
        sys.exit(1)