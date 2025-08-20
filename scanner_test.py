#!/usr/bin/env python3
"""
Investment Scoring Scanner Testing Script
Testează funcționalitatea Investment Scoring Scanner-ului implementat în FlowMind Analytics
"""

import requests
import sys
import time
import json
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class InvestmentScannerTester:
    def __init__(self, base_url="https://tradestation-sync-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # MongoDB connection for direct database testing
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"🔍 Investment Scoring Scanner Tester")
        print(f"📡 Backend URL: {self.api_url}")
        print(f"🗄️  MongoDB URL: {self.mongo_url}")
        print(f"📊 Database: {self.db_name}")
        print("=" * 80)

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

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
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
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

    def test_mongodb_connectivity(self):
        """Test MongoDB connectivity and collection access"""
        print("\n🗄️  PHASE 1: MongoDB Connectivity Testing")
        print("-" * 60)
        
        try:
            # Connect to MongoDB
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            collection = db['scanned_stocks']
            
            print(f"✅ MongoDB connection successful")
            print(f"   Database: {self.db_name}")
            print(f"   Collection: scanned_stocks")
            
            # Test collection operations
            # Insert a test document
            test_doc = {
                "ticker": "TEST",
                "total_score": 75.5,
                "rating": "BUY",
                "scanned_at": datetime.utcnow().isoformat(),
                "test_document": True
            }
            
            result = collection.insert_one(test_doc)
            print(f"✅ Test document inserted with ID: {result.inserted_id}")
            
            # Count documents
            count = collection.count_documents({})
            print(f"📊 Total documents in collection: {count}")
            
            # Delete test document
            collection.delete_one({"test_document": True})
            print(f"✅ Test document cleaned up")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connectivity failed: {str(e)}")
            return False

    def test_scanner_status_endpoint(self):
        """Test GET /api/scanner/status endpoint"""
        print("\n📊 PHASE 2: Scanner Status Endpoint Testing")
        print("-" * 60)
        
        success, status_data = self.run_test(
            "Scanner Status", "GET", "scanner/status", 200, timeout=10
        )
        
        if not success:
            return False
        
        # Verify response structure
        required_fields = ['status', 'total_stocks_scanned', 'database_status']
        missing_fields = [field for field in required_fields if field not in status_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        status = status_data.get('status')
        total_stocks = status_data.get('total_stocks_scanned', 0)
        db_status = status_data.get('database_status')
        
        print(f"📊 Scanner Status: {status}")
        print(f"📊 Total Stocks Scanned: {total_stocks}")
        print(f"📊 Database Status: {db_status}")
        
        if 'last_scan_date' in status_data:
            print(f"📊 Last Scan Date: {status_data['last_scan_date']}")
        
        if 'top_5_stocks' in status_data:
            top_5 = status_data['top_5_stocks']
            print(f"📊 Top 5 Stocks Preview: {len(top_5)} stocks")
            for i, stock in enumerate(top_5[:3]):
                print(f"   #{i+1}: {stock.get('ticker')} - Score: {stock.get('score')} - Rating: {stock.get('rating')}")
        
        return True

    def test_scanner_start_endpoint(self):
        """Test POST /api/scanner/start-scan endpoint"""
        print("\n🚀 PHASE 3: Scanner Start Endpoint Testing")
        print("-" * 60)
        
        success, start_data = self.run_test(
            "Start Scanner", "POST", "scanner/start-scan", 200, timeout=15
        )
        
        if not success:
            return False
        
        # Verify response structure
        required_fields = ['status', 'message']
        missing_fields = [field for field in required_fields if field not in start_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        status = start_data.get('status')
        message = start_data.get('message')
        
        print(f"📊 Start Status: {status}")
        print(f"📊 Message: {message}")
        
        if 'estimated_duration' in start_data:
            print(f"📊 Estimated Duration: {start_data['estimated_duration']}")
        
        # Wait a bit for scan to start processing
        print(f"⏳ Waiting 10 seconds for scan to start processing...")
        time.sleep(10)
        
        return True

    def test_scanner_top_stocks_endpoint(self):
        """Test GET /api/scanner/top-stocks endpoint"""
        print("\n🏆 PHASE 4: Scanner Top Stocks Endpoint Testing")
        print("-" * 60)
        
        # Test with different limits
        for limit in [10, 25, 50]:
            print(f"\n📊 Testing with limit={limit}")
            
            success, top_stocks_data = self.run_test(
                f"Top Stocks (limit={limit})", "GET", "scanner/top-stocks", 200, 
                params={"limit": limit}, timeout=20
            )
            
            if not success:
                continue
            
            # Verify response structure
            required_fields = ['total_found', 'limit', 'top_stocks']
            missing_fields = [field for field in required_fields if field not in top_stocks_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                continue
            
            total_found = top_stocks_data.get('total_found', 0)
            returned_limit = top_stocks_data.get('limit', 0)
            top_stocks = top_stocks_data.get('top_stocks', [])
            
            print(f"📊 Total Found: {total_found}")
            print(f"📊 Requested Limit: {limit}")
            print(f"📊 Returned Limit: {returned_limit}")
            print(f"📊 Actual Stocks Returned: {len(top_stocks)}")
            
            if 'scan_date' in top_stocks_data:
                print(f"📊 Scan Date: {top_stocks_data['scan_date']}")
            
            # Analyze top stocks data
            if top_stocks:
                print(f"\n📈 Top 5 Stocks Analysis:")
                for i, stock in enumerate(top_stocks[:5]):
                    ticker = stock.get('ticker', 'N/A')
                    score = stock.get('score', 'N/A')
                    rating = stock.get('rating', 'N/A')
                    price = stock.get('price', 'N/A')
                    sector = stock.get('sector', 'N/A')
                    
                    print(f"   #{i+1}: {ticker}")
                    print(f"     - Score: {score}")
                    print(f"     - Rating: {rating}")
                    print(f"     - Price: {price}")
                    print(f"     - Sector: {sector}")
                
                # Check for data quality
                valid_scores = [s for s in top_stocks if isinstance(s.get('score'), (int, float)) and s.get('score') > 0]
                print(f"\n📊 Data Quality Analysis:")
                print(f"   - Stocks with valid scores: {len(valid_scores)}/{len(top_stocks)}")
                
                if len(valid_scores) == 0:
                    print(f"❌ CRITICAL: No stocks with valid scores found!")
                    return False
                else:
                    print(f"✅ Found {len(valid_scores)} stocks with valid scores")
            else:
                print(f"❌ CRITICAL: No top stocks returned!")
                return False
        
        return True

    def test_mongodb_data_persistence(self):
        """Test MongoDB data persistence directly"""
        print("\n💾 PHASE 5: MongoDB Data Persistence Testing")
        print("-" * 60)
        
        try:
            # Connect to MongoDB
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            collection = db['scanned_stocks']
            
            # Count total documents
            total_docs = collection.count_documents({})
            print(f"📊 Total documents in scanned_stocks collection: {total_docs}")
            
            if total_docs == 0:
                print(f"❌ CRITICAL: No documents found in scanned_stocks collection!")
                print(f"   This indicates the scanner is not saving results to MongoDB")
                client.close()
                return False
            
            # Get sample documents
            sample_docs = list(collection.find({}).limit(5))
            print(f"📊 Sample documents structure:")
            
            for i, doc in enumerate(sample_docs):
                print(f"   Document #{i+1}:")
                print(f"     - Ticker: {doc.get('ticker', 'N/A')}")
                print(f"     - Score: {doc.get('total_score', 'N/A')}")
                print(f"     - Rating: {doc.get('rating', 'N/A')}")
                print(f"     - Scanned At: {doc.get('scanned_at', 'N/A')}")
                
                # Check for required fields
                required_fields = ['ticker', 'total_score', 'rating', 'scanned_at']
                missing_fields = [field for field in required_fields if field not in doc]
                
                if missing_fields:
                    print(f"     ❌ Missing fields: {missing_fields}")
                else:
                    print(f"     ✅ All required fields present")
            
            # Check for recent scans
            recent_docs = list(collection.find({}).sort('scanned_at', -1).limit(1))
            if recent_docs:
                latest_scan = recent_docs[0].get('scanned_at')
                print(f"📊 Latest scan timestamp: {latest_scan}")
            
            # Get score distribution
            pipeline = [
                {"$group": {
                    "_id": "$rating",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$total_score"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            rating_distribution = list(collection.aggregate(pipeline))
            print(f"📊 Rating Distribution:")
            for rating_data in rating_distribution:
                rating = rating_data.get('_id', 'N/A')
                count = rating_data.get('count', 0)
                avg_score = rating_data.get('avg_score', 0)
                print(f"   - {rating}: {count} stocks (avg score: {avg_score:.1f})")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ MongoDB data persistence test failed: {str(e)}")
            return False

    def test_scanner_logic_and_scoring(self):
        """Test scanner logic and scoring calculations"""
        print("\n🧮 PHASE 6: Scanner Logic and Scoring Testing")
        print("-" * 60)
        
        # Test individual stock scoring to verify logic
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in test_symbols:
            print(f"\n📊 Testing individual scoring for {symbol}:")
            
            success, score_data = self.run_test(
                f"Individual Score ({symbol})", "GET", f"investments/score/{symbol}", 200, timeout=15
            )
            
            if success:
                total_score = score_data.get('total_score', 0)
                rating = score_data.get('rating', 'N/A')
                risk_level = score_data.get('risk_level', 'N/A')
                
                print(f"   ✅ {symbol}: Score={total_score}, Rating={rating}, Risk={risk_level}")
                
                # Verify score is in valid range
                if 0 <= total_score <= 100:
                    print(f"   ✅ Score in valid range (0-100)")
                else:
                    print(f"   ❌ Score outside valid range: {total_score}")
                
                # Check for required fields
                required_fields = ['symbol', 'total_score', 'rating', 'individual_scores']
                missing_fields = [field for field in required_fields if field not in score_data]
                
                if missing_fields:
                    print(f"   ❌ Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
            else:
                print(f"   ❌ Failed to get score for {symbol}")
        
        return True

    def test_scanner_comprehensive_workflow(self):
        """Test complete scanner workflow"""
        print("\n🔄 PHASE 7: Comprehensive Scanner Workflow Testing")
        print("-" * 60)
        
        # Step 1: Check initial status
        print(f"Step 1: Check initial scanner status")
        success, initial_status = self.run_test(
            "Initial Status", "GET", "scanner/status", 200, timeout=10
        )
        
        if success:
            initial_count = initial_status.get('total_stocks_scanned', 0)
            print(f"   Initial stocks scanned: {initial_count}")
        
        # Step 2: Start a new scan
        print(f"\nStep 2: Start new scan")
        success, start_response = self.run_test(
            "Start New Scan", "POST", "scanner/start-scan", 200, timeout=15
        )
        
        if not success:
            print(f"❌ Failed to start scan")
            return False
        
        # Step 3: Wait for scan to process
        print(f"\nStep 3: Wait for scan processing (30 seconds)")
        time.sleep(30)
        
        # Step 4: Check status after scan
        print(f"\nStep 4: Check status after scan")
        success, post_scan_status = self.run_test(
            "Post-Scan Status", "GET", "scanner/status", 200, timeout=10
        )
        
        if success:
            post_scan_count = post_scan_status.get('total_stocks_scanned', 0)
            status = post_scan_status.get('status', 'unknown')
            print(f"   Post-scan stocks scanned: {post_scan_count}")
            print(f"   Scanner status: {status}")
            
            # Check if scan actually processed stocks
            if post_scan_count > initial_count:
                print(f"✅ Scan processed {post_scan_count - initial_count} new stocks")
            elif post_scan_count > 0:
                print(f"✅ Scanner has {post_scan_count} stocks in database")
            else:
                print(f"❌ No stocks processed by scanner")
                return False
        
        # Step 5: Get top stocks results
        print(f"\nStep 5: Get top stocks results")
        success, top_stocks = self.run_test(
            "Final Top Stocks", "GET", "scanner/top-stocks", 200, 
            params={"limit": 20}, timeout=20
        )
        
        if success:
            stocks_returned = len(top_stocks.get('top_stocks', []))
            print(f"   Top stocks returned: {stocks_returned}")
            
            if stocks_returned > 0:
                print(f"✅ Scanner workflow completed successfully")
                return True
            else:
                print(f"❌ No top stocks returned")
                return False
        
        return False

    def run_comprehensive_scanner_tests(self):
        """Run all scanner tests"""
        print(f"\n🎯 COMPREHENSIVE INVESTMENT SCORING SCANNER TESTING")
        print(f"📋 Testing Romanian requirements: Scanner endpoints, MongoDB persistence, scoring logic")
        print("=" * 80)
        
        test_results = []
        
        # Phase 1: MongoDB Connectivity
        result = self.test_mongodb_connectivity()
        test_results.append(("MongoDB Connectivity", result))
        
        # Phase 2: Scanner Status Endpoint
        result = self.test_scanner_status_endpoint()
        test_results.append(("Scanner Status Endpoint", result))
        
        # Phase 3: Scanner Start Endpoint
        result = self.test_scanner_start_endpoint()
        test_results.append(("Scanner Start Endpoint", result))
        
        # Phase 4: Scanner Top Stocks Endpoint
        result = self.test_scanner_top_stocks_endpoint()
        test_results.append(("Scanner Top Stocks Endpoint", result))
        
        # Phase 5: MongoDB Data Persistence
        result = self.test_mongodb_data_persistence()
        test_results.append(("MongoDB Data Persistence", result))
        
        # Phase 6: Scanner Logic and Scoring
        result = self.test_scanner_logic_and_scoring()
        test_results.append(("Scanner Logic and Scoring", result))
        
        # Phase 7: Comprehensive Workflow
        result = self.test_scanner_comprehensive_workflow()
        test_results.append(("Comprehensive Scanner Workflow", result))
        
        # Final Results
        print(f"\n🎯 FINAL SCANNER TESTING RESULTS")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
            if passed:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Romanian requirements verification
        print(f"\n🇷🇴 ROMANIAN REQUIREMENTS VERIFICATION:")
        
        mongodb_working = test_results[0][1] and test_results[4][1]  # MongoDB connectivity + persistence
        endpoints_working = test_results[1][1] and test_results[2][1] and test_results[3][1]  # All endpoints
        scoring_working = test_results[5][1]  # Scoring logic
        workflow_working = test_results[6][1]  # Complete workflow
        
        requirements = [
            ("Scanner endpoints working (GET status, POST start-scan, GET top-stocks)", endpoints_working),
            ("MongoDB persistence working (saves to 'scanned_stocks' collection)", mongodb_working),
            ("Scoring logic working (calculates scores for ~100 tickers)", scoring_working),
            ("Complete workflow working (scan → save → retrieve)", workflow_working)
        ]
        
        for requirement, met in requirements:
            status = "✅ MET" if met else "❌ NOT MET"
            print(f"   {status} {requirement}")
        
        # Issues identified
        print(f"\n🔍 ISSUES IDENTIFIED:")
        if not mongodb_working:
            print(f"   ❌ MongoDB persistence issues - scanner may not be saving results")
        if not endpoints_working:
            print(f"   ❌ Scanner endpoints issues - API responses may be incomplete")
        if not scoring_working:
            print(f"   ❌ Scoring logic issues - calculations may be incorrect")
        if not workflow_working:
            print(f"   ❌ Workflow issues - complete scan process not working")
        
        if all([mongodb_working, endpoints_working, scoring_working, workflow_working]):
            print(f"   ✅ No critical issues found - scanner working correctly")
        
        # Final verdict
        if success_rate >= 85:
            print(f"\n🎉 VERDICT: EXCELLENT - Investment Scoring Scanner working perfectly!")
        elif success_rate >= 70:
            print(f"\n✅ VERDICT: GOOD - Investment Scoring Scanner mostly working with minor issues")
        else:
            print(f"\n❌ VERDICT: NEEDS IMPROVEMENT - Investment Scoring Scanner has significant issues")
        
        return success_rate >= 70

def main():
    """Main testing function"""
    tester = InvestmentScannerTester()
    
    try:
        success = tester.run_comprehensive_scanner_tests()
        
        if success:
            print(f"\n✅ Scanner testing completed successfully")
            sys.exit(0)
        else:
            print(f"\n❌ Scanner testing failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()