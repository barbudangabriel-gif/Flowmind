#!/usr/bin/env python3
"""
Investment Scoring Scanner Price Investigation Test
Investigates the missing prices issue in Investment Scoring Scanner
"""

import requests
import json
import time
from datetime import datetime
import sys


class InvestmentScoringPriceInvestigator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []

    def log_issue(self, issue_type, description, data=None):
        """Log an issue found during testing"""
        issue = {
            "type": issue_type,
            "description": description,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.issues_found.append(issue)
        print(f"🚨 ISSUE FOUND: {issue_type} - {description}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")

        try:
            timeout = 120 if "scanner" in endpoint else 30

            if method == "GET":
                response = requests.get(
                    url, headers=headers, params=params, timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    url, json=data, headers=headers, timeout=timeout
                )

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(
                    f"❌ Failed - Expected {expected_status}, got {response.status_code}"
                )
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_scanner_top_stocks_price_structure(self):
        """Test 1: Investigate /api/scanner/top-stocks price structure"""
        print("\n" + "=" * 80)
        print("🔍 TEST 1: SCANNER TOP STOCKS PRICE STRUCTURE INVESTIGATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Check if price field exists and has valid values")

        success, data = self.run_test(
            "Scanner Top Stocks", "GET", "scanner/top-stocks", 200, params={"limit": 10}
        )

        if not success:
            self.log_issue("API_FAILURE", "Scanner top-stocks endpoint failed")
            return False

        # Check response structure
        top_stocks = data.get("top_stocks", [])
        print(f"\n📊 Found {len(top_stocks)} stocks in response")

        if not top_stocks:
            self.log_issue("NO_DATA", "No stocks returned from scanner")
            return False

        # Analyze price data in each stock
        stocks_with_prices = 0
        stocks_with_na_prices = 0
        stocks_with_zero_prices = 0
        stocks_missing_price_field = 0

        print("\n📋 ANALYZING PRICE DATA FOR EACH STOCK:")
        print("-" * 60)

        for i, stock in enumerate(top_stocks[:10]):  # Check first 10
            ticker = stock.get("ticker", "N/A")
            price = stock.get("price", "MISSING")

            print(f"\n   📊 Stock #{i+1}: {ticker}")
            print(f"     - Price field: {price}")
            print(f"     - Price type: {type(price)}")

            # Check all fields in stock data
            all_fields = list(stock.keys())
            print(f"     - All fields: {all_fields}")

            # Analyze price field
            if "price" not in stock:
                stocks_missing_price_field += 1
                print("     ❌ MISSING: No 'price' field")
                self.log_issue(
                    "MISSING_PRICE_FIELD", f"Stock {ticker} missing price field", stock
                )
            elif price == "N/A" or price == "N/A":
                stocks_with_na_prices += 1
                print("     ❌ N/A: Price shows 'N/A'")
                self.log_issue("NA_PRICE", f"Stock {ticker} has N/A price", stock)
            elif price == 0 or price == 0.0:
                stocks_with_zero_prices += 1
                print("     ❌ ZERO: Price is zero")
                self.log_issue("ZERO_PRICE", f"Stock {ticker} has zero price", stock)
            elif isinstance(price, (int, float)) and price > 0:
                stocks_with_prices += 1
                print(f"     ✅ VALID: Price is ${price:.2f}")
            else:
                print("     ⚠️  UNKNOWN: Unexpected price format")
                self.log_issue(
                    "INVALID_PRICE_FORMAT",
                    f"Stock {ticker} has invalid price format",
                    {"price": price, "type": type(price)},
                )

        # Summary
        print("\n📊 PRICE DATA SUMMARY:")
        print(f"   - Stocks with valid prices: {stocks_with_prices}")
        print(f"   - Stocks with N/A prices: {stocks_with_na_prices}")
        print(f"   - Stocks with zero prices: {stocks_with_zero_prices}")
        print(f"   - Stocks missing price field: {stocks_missing_price_field}")

        # Check if this is the main issue
        if stocks_with_na_prices > 0:
            print(
                f"\n🚨 MAIN ISSUE IDENTIFIED: {stocks_with_na_prices} stocks showing 'N/A' prices"
            )
            return False
        elif stocks_missing_price_field > 0:
            print(
                f"\n🚨 MAIN ISSUE IDENTIFIED: {stocks_missing_price_field} stocks missing price field"
            )
            return False
        else:
            print(
                f"\n✅ PRICE DATA LOOKS GOOD: {stocks_with_prices} stocks have valid prices"
            )
            return True

    def test_scanner_status_top5_prices(self):
        """Test 2: Check /api/scanner/status top_5_stocks prices"""
        print("\n" + "=" * 80)
        print("🔍 TEST 2: SCANNER STATUS TOP 5 STOCKS PRICE CHECK")
        print("=" * 80)
        print("🎯 OBJECTIVE: Check if top_5_stocks in status have prices")

        success, data = self.run_test("Scanner Status", "GET", "scanner/status", 200)

        if not success:
            self.log_issue("API_FAILURE", "Scanner status endpoint failed")
            return False

        top_5_stocks = data.get("top_5_stocks", [])
        print(f"\n📊 Found {len(top_5_stocks)} stocks in top_5_stocks")

        if not top_5_stocks:
            self.log_issue("NO_TOP5_DATA", "No top_5_stocks in status response")
            return False

        print("\n📋 ANALYZING TOP 5 STOCKS PRICE DATA:")
        print("-" * 60)

        valid_prices = 0
        for i, stock in enumerate(top_5_stocks):
            ticker = stock.get("ticker", "N/A")
            score = stock.get("score", "N/A")
            rating = stock.get("rating", "N/A")

            print(f"\n   📊 Top Stock #{i+1}: {ticker}")
            print(f"     - Score: {score}")
            print(f"     - Rating: {rating}")

            # Check if price field exists in top_5_stocks
            if "price" in stock:
                price = stock["price"]
                print(f"     - Price: {price}")
                if isinstance(price, (int, float)) and price > 0:
                    valid_prices += 1
                    print(f"     ✅ Valid price: ${price:.2f}")
                else:
                    print(f"     ❌ Invalid price: {price}")
                    self.log_issue(
                        "INVALID_TOP5_PRICE",
                        f"Top 5 stock {ticker} has invalid price",
                        stock,
                    )
            else:
                print("     ⚠️  No price field in top_5_stocks")
                # This might be expected - top_5_stocks might not include prices

        print("\n📊 TOP 5 STOCKS PRICE SUMMARY:")
        print(f"   - Stocks with valid prices: {valid_prices}")
        print(f"   - Total top 5 stocks: {len(top_5_stocks)}")

        return valid_prices > 0

    def test_individual_stock_scoring_price(self):
        """Test 3: Test individual stock scoring for AAPL to check price handling"""
        print("\n" + "=" * 80)
        print("🔍 TEST 3: INDIVIDUAL STOCK SCORING PRICE CHECK (AAPL)")
        print("=" * 80)
        print(
            "🎯 OBJECTIVE: Test calculate_investment_score for AAPL and check price data"
        )

        # Test investment scoring for AAPL
        success, data = self.run_test(
            "Investment Score AAPL", "GET", "investments/score/AAPL", 200
        )

        if not success:
            self.log_issue("API_FAILURE", "Investment score endpoint failed for AAPL")
            return False

        print("\n📊 AAPL Investment Score Response Analysis:")
        print("-" * 60)

        symbol = data.get("symbol", "N/A")
        total_score = data.get("total_score", "N/A")
        rating = data.get("rating", "N/A")

        print(f"   - Symbol: {symbol}")
        print(f"   - Total Score: {total_score}")
        print(f"   - Rating: {rating}")

        # Check if there's any price-related data in the response
        price_related_fields = ["price", "current_price", "stock_price"]
        found_price_fields = []

        for field in price_related_fields:
            if field in data:
                found_price_fields.append(field)
                print(f"   - {field}: {data[field]}")

        if not found_price_fields:
            print("   ⚠️  No direct price fields found in investment score response")
            print(
                "   📝 Note: Price data might be fetched separately by the scoring system"
            )

        # Check if we can get enhanced stock data for AAPL
        success2, stock_data = self.run_test(
            "Enhanced Stock Data AAPL", "GET", "stocks/AAPL/enhanced", 200
        )

        if success2:
            aapl_price = stock_data.get("price", "N/A")
            print("\n📊 AAPL Enhanced Stock Data:")
            print(
                f"   - Price from enhanced endpoint: ${aapl_price:.2f}"
                if isinstance(aapl_price, (int, float))
                else f"   - Price: {aapl_price}"
            )

            if isinstance(aapl_price, (int, float)) and aapl_price > 0:
                print("   ✅ Enhanced stock data has valid price")
                return True
            else:
                print("   ❌ Enhanced stock data has invalid price")
                self.log_issue(
                    "INVALID_ENHANCED_PRICE",
                    "AAPL enhanced stock data has invalid price",
                    stock_data,
                )
                return False
        else:
            self.log_issue(
                "API_FAILURE", "Enhanced stock data endpoint failed for AAPL"
            )
            return False

    def test_mongodb_data_structure(self):
        """Test 4: Investigate MongoDB data structure indirectly"""
        print("\n" + "=" * 80)
        print("🔍 TEST 4: MONGODB DATA STRUCTURE INVESTIGATION (INDIRECT)")
        print("=" * 80)
        print(
            "🎯 OBJECTIVE: Analyze scanner data to understand what's saved in MongoDB"
        )

        # Get scanner status to understand data structure
        success, status_data = self.run_test(
            "Scanner Status for MongoDB Analysis", "GET", "scanner/status", 200
        )

        if not success:
            return False

        # Get top stocks to see full data structure
        success2, top_stocks_data = self.run_test(
            "Top Stocks for MongoDB Analysis",
            "GET",
            "scanner/top-stocks",
            200,
            params={"limit": 5},
        )

        if not success2:
            return False

        print("\n📊 MONGODB DATA STRUCTURE ANALYSIS:")
        print("-" * 60)

        # Analyze what fields are being saved
        top_stocks = top_stocks_data.get("top_stocks", [])
        if top_stocks:
            sample_stock = top_stocks[0]
            print("\n📋 Sample Stock Data Structure (First Stock):")
            print(f"   Ticker: {sample_stock.get('ticker', 'N/A')}")

            all_fields = list(sample_stock.keys())
            print("\n   📊 All Fields in MongoDB Document:")
            for field in sorted(all_fields):
                value = sample_stock.get(field)
                if isinstance(value, dict):
                    print(
                        f"     - {field}: {type(value).__name__} with {len(value)} keys"
                    )
                    if field == "stock_data":  # This might contain the price
                        print(f"       stock_data keys: {list(value.keys())}")
                        if "price" in value:
                            print(f"       stock_data.price: {value['price']}")
                elif isinstance(value, list):
                    print(
                        f"     - {field}: {type(value).__name__} with {len(value)} items"
                    )
                else:
                    print(f"     - {field}: {value}")

            # Check specifically for price-related fields
            price_fields = ["price", "current_price", "stock_price"]
            stock_data_price_fields = []

            if "stock_data" in sample_stock and isinstance(
                sample_stock["stock_data"], dict
            ):
                stock_data = sample_stock["stock_data"]
                for field in price_fields:
                    if field in stock_data:
                        stock_data_price_fields.append(field)
                        print(
                            f"\n   💰 PRICE FOUND in stock_data.{field}: {stock_data[field]}"
                        )

            if not stock_data_price_fields:
                print("\n   ❌ NO PRICE FIELDS FOUND in stock_data")
                self.log_issue(
                    "NO_PRICE_IN_STOCK_DATA",
                    "No price fields found in stock_data",
                    sample_stock,
                )

                # Check if price is at root level
                root_price_fields = []
                for field in price_fields:
                    if field in sample_stock:
                        root_price_fields.append(field)
                        print(
                            f"   💰 PRICE FOUND at root level.{field}: {sample_stock[field]}"
                        )

                if not root_price_fields:
                    print("   ❌ NO PRICE FIELDS FOUND at root level either")
                    self.log_issue(
                        "NO_PRICE_ANYWHERE",
                        "No price fields found anywhere in document",
                        sample_stock,
                    )
                    return False

            return True
        else:
            print("   ❌ No sample stock data available for analysis")
            return False

    def test_new_scan_price_saving(self):
        """Test 5: Start a new scan and verify price saving"""
        print("\n" + "=" * 80)
        print("🔍 TEST 5: NEW SCAN PRICE SAVING VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Start new scan and verify prices are saved correctly")

        # Start a new scan
        success, scan_data = self.run_test(
            "Start New Scan", "POST", "scanner/start-scan", 200
        )

        if not success:
            self.log_issue("API_FAILURE", "Failed to start new scan")
            return False

        print("\n📊 Scan Started Successfully:")
        print(f"   Status: {scan_data.get('status', 'N/A')}")
        print(f"   Message: {scan_data.get('message', 'N/A')}")

        # Wait for scan to process some stocks
        print("\n⏳ Waiting 30 seconds for scan to process...")
        time.sleep(30)

        # Check status after scan
        success2, status_data = self.run_test(
            "Scanner Status After New Scan", "GET", "scanner/status", 200
        )

        if not success2:
            return False

        total_scanned = status_data.get("total_stocks_scanned", 0)
        print("\n📊 Scan Progress:")
        print(f"   Total stocks scanned: {total_scanned}")

        if total_scanned > 0:
            # Get fresh top stocks data
            success3, fresh_data = self.run_test(
                "Fresh Top Stocks After Scan",
                "GET",
                "scanner/top-stocks",
                200,
                params={"limit": 3},
            )

            if success3:
                fresh_stocks = fresh_data.get("top_stocks", [])
                print("\n📊 Fresh Scan Results Analysis:")

                for i, stock in enumerate(fresh_stocks[:3]):
                    ticker = stock.get("ticker", "N/A")
                    price = stock.get("price", "MISSING")

                    print(f"\n   📊 Fresh Stock #{i+1}: {ticker}")
                    print(f"     - Price: {price}")

                    if "stock_data" in stock:
                        stock_data = stock["stock_data"]
                        stock_data_price = stock_data.get("price", "MISSING")
                        print(f"     - stock_data.price: {stock_data_price}")

                        if (
                            isinstance(stock_data_price, (int, float))
                            and stock_data_price > 0
                        ):
                            print("     ✅ Fresh scan has valid price in stock_data")
                        else:
                            print("     ❌ Fresh scan has invalid price in stock_data")
                            self.log_issue(
                                "FRESH_SCAN_INVALID_PRICE",
                                f"Fresh scan stock {ticker} has invalid price",
                                stock,
                            )

                return True
            else:
                return False
        else:
            print("   ⚠️  No stocks processed yet, scan might still be running")
            return False

    def test_enhanced_ticker_manager_prices(self):
        """Test 6: Test enhanced_ticker_manager price fetching directly"""
        print("\n" + "=" * 80)
        print("🔍 TEST 6: ENHANCED TICKER MANAGER PRICE VERIFICATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Test if enhanced_ticker_manager returns prices correctly")

        # Test enhanced stock data for a few major stocks
        test_symbols = ["AAPL", "MSFT", "GOOGL"]

        for symbol in test_symbols:
            success, stock_data = self.run_test(
                f"Enhanced Stock Data {symbol}", "GET", f"stocks/{symbol}/enhanced", 200
            )

            if success:
                price = stock_data.get("price", "N/A")
                data_source = stock_data.get("data_source", "Unknown")

                print(f"\n📊 {symbol} Enhanced Data:")
                print(
                    f"   - Price: ${price:.2f}"
                    if isinstance(price, (int, float))
                    else f"   - Price: {price}"
                )
                print(f"   - Data Source: {data_source}")

                if isinstance(price, (int, float)) and price > 0:
                    print(
                        f"   ✅ {symbol} has valid price from enhanced ticker manager"
                    )
                else:
                    print(
                        f"   ❌ {symbol} has invalid price from enhanced ticker manager"
                    )
                    self.log_issue(
                        "ENHANCED_TICKER_INVALID_PRICE",
                        f"{symbol} enhanced ticker data has invalid price",
                        stock_data,
                    )
            else:
                self.log_issue(
                    "API_FAILURE", f"Enhanced stock data failed for {symbol}"
                )

        return True

    def run_comprehensive_investigation(self):
        """Run all tests to investigate the missing prices issue"""
        print("\n" + "=" * 100)
        print("🔍 INVESTMENT SCORING SCANNER PRICE INVESTIGATION")
        print("=" * 100)
        print(
            "🎯 INVESTIGATING: Missing prices issue - all prices show 'N/A' in frontend table"
        )
        print("📋 TESTING PLAN:")
        print("   1. Check /api/scanner/top-stocks price structure")
        print("   2. Check /api/scanner/status top_5_stocks prices")
        print("   3. Test individual stock scoring price handling")
        print("   4. Investigate MongoDB data structure (indirect)")
        print("   5. Start new scan and verify price saving")
        print("   6. Test enhanced_ticker_manager price fetching")

        # Run all tests
        test_results = []

        test_results.append(
            (
                "Scanner Top Stocks Price Structure",
                self.test_scanner_top_stocks_price_structure(),
            )
        )
        test_results.append(
            ("Scanner Status Top 5 Prices", self.test_scanner_status_top5_prices())
        )
        test_results.append(
            (
                "Individual Stock Scoring Price",
                self.test_individual_stock_scoring_price(),
            )
        )
        test_results.append(
            ("MongoDB Data Structure", self.test_mongodb_data_structure())
        )
        test_results.append(
            ("New Scan Price Saving", self.test_new_scan_price_saving())
        )
        test_results.append(
            (
                "Enhanced Ticker Manager Prices",
                self.test_enhanced_ticker_manager_prices(),
            )
        )

        # Final Analysis
        print("\n" + "=" * 100)
        print("🎯 FINAL INVESTIGATION RESULTS")
        print("=" * 100)

        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)

        print("\n📊 TEST RESULTS SUMMARY:")
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")

        print(
            f"\n🎯 SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}% ({passed_tests}/{total_tests} tests passed)"
        )

        # Issues Summary
        if self.issues_found:
            print(f"\n🚨 ISSUES FOUND ({len(self.issues_found)} total):")
            issue_types = {}
            for issue in self.issues_found:
                issue_type = issue["type"]
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)

            for issue_type, issues in issue_types.items():
                print(f"\n   🔴 {issue_type} ({len(issues)} occurrences):")
                for issue in issues[:3]:  # Show first 3 of each type
                    print(f"     - {issue['description']}")
                if len(issues) > 3:
                    print(f"     - ... and {len(issues) - 3} more")

        # Root Cause Analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")

        if any("NA_PRICE" in issue["type"] for issue in self.issues_found):
            print(
                "   🎯 PRIMARY ISSUE: Prices are being set to 'N/A' in the data pipeline"
            )
            print(
                "   🔧 LIKELY CAUSE: enhanced_ticker_manager.get_real_time_quote() returning invalid prices"
            )
            print("   💡 SOLUTION: Check enhanced_ticker_data.py price fetching logic")

        elif any("MISSING_PRICE_FIELD" in issue["type"] for issue in self.issues_found):
            print("   🎯 PRIMARY ISSUE: Price field is missing from scanner results")
            print(
                "   🔧 LIKELY CAUSE: investment_scoring.py not including price in response structure"
            )
            print("   💡 SOLUTION: Modify scanner response to include price field")

        elif any(
            "NO_PRICE_IN_STOCK_DATA" in issue["type"] for issue in self.issues_found
        ):
            print(
                "   🎯 PRIMARY ISSUE: Prices not being saved in stock_data during scanning"
            )
            print(
                "   🔧 LIKELY CAUSE: StockScanner.scan_all_stocks() not preserving price data"
            )
            print(
                "   💡 SOLUTION: Ensure stock_data includes price when saving to MongoDB"
            )

        else:
            print("   🤔 UNCLEAR: Multiple potential issues detected")
            print(
                "   🔧 RECOMMENDATION: Check the entire data pipeline from enhanced_ticker_manager to frontend"
            )

        # Specific Recommendations
        print("\n💡 SPECIFIC RECOMMENDATIONS:")
        print("   1. Check enhanced_ticker_data.py get_real_time_quote() method")
        print("   2. Verify investment_scoring.py includes price in scanner response")
        print("   3. Ensure MongoDB documents include stock_data.price field")
        print(
            "   4. Test the complete pipeline: enhanced_ticker_manager → investment_scorer → MongoDB → API response"
        )

        return passed_tests >= total_tests * 0.5  # At least 50% tests should pass


if __name__ == "__main__":
    print("🔍 Starting Investment Scoring Scanner Price Investigation...")

    investigator = InvestmentScoringPriceInvestigator()
    success = investigator.run_comprehensive_investigation()

    if success:
        print("\n✅ Investigation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Investigation found critical issues")
        sys.exit(1)
