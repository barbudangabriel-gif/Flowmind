#!/usr/bin/env python3
"""
Debug Scanner - Test MongoDB save functionality directly
"""

import asyncio
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add backend to path
sys.path.append('/app/backend')

# Load environment
load_dotenv('/app/backend/.env')

async def test_mongodb_save():
    """Test MongoDB save functionality directly"""
    print("🔍 Testing MongoDB Save Functionality")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"📡 Connecting to: {mongo_url}")
        print(f"📊 Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        collection = db['scanned_stocks']
        
        # Test 1: Clear collection
        print(f"\n🧹 Clearing existing data...")
        delete_result = await collection.delete_many({})
        print(f"   Deleted {delete_result.deleted_count} documents")
        
        # Test 2: Insert test data
        print(f"\n💾 Inserting test scan results...")
        test_results = [
            {
                "ticker": "AAPL",
                "total_score": 75.5,
                "rating": "BUY",
                "symbol": "AAPL",
                "scanned_at": datetime.utcnow(),
                "scan_id": "test_scan_001"
            },
            {
                "ticker": "MSFT", 
                "total_score": 72.3,
                "rating": "HOLD+",
                "symbol": "MSFT",
                "scanned_at": datetime.utcnow(),
                "scan_id": "test_scan_001"
            },
            {
                "ticker": "GOOGL",
                "total_score": 68.9,
                "rating": "HOLD",
                "symbol": "GOOGL", 
                "scanned_at": datetime.utcnow(),
                "scan_id": "test_scan_001"
            }
        ]
        
        insert_result = await collection.insert_many(test_results)
        print(f"   Inserted {len(insert_result.inserted_ids)} documents")
        print(f"   IDs: {insert_result.inserted_ids}")
        
        # Test 3: Verify data was saved
        print(f"\n🔍 Verifying saved data...")
        count = await collection.count_documents({})
        print(f"   Total documents: {count}")
        
        # Get all documents
        cursor = collection.find({}).sort('total_score', -1)
        documents = await cursor.to_list(length=10)
        
        print(f"   Retrieved documents:")
        for i, doc in enumerate(documents):
            print(f"     #{i+1}: {doc.get('ticker')} - Score: {doc.get('total_score')} - Rating: {doc.get('rating')}")
        
        # Test 4: Test the get_top_stocks equivalent
        print(f"\n🏆 Testing top stocks retrieval...")
        top_cursor = collection.find({}).sort('total_score', -1).limit(5)
        top_stocks = await top_cursor.to_list(length=5)
        
        print(f"   Top stocks:")
        for i, stock in enumerate(top_stocks):
            print(f"     #{i+1}: {stock.get('ticker')} - {stock.get('total_score')}")
        
        client.close()
        print(f"\n✅ MongoDB save functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB save test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_scanner_import():
    """Test if we can import and use the scanner"""
    print(f"\n🔍 Testing Scanner Import and Initialization")
    print("=" * 50)
    
    try:
        # Import scanner components
        from investment_scoring import StockScanner, investment_scorer
        
        print(f"✅ Successfully imported StockScanner and investment_scorer")
        
        # Initialize scanner
        scanner = StockScanner(investment_scorer)
        print(f"✅ Successfully initialized StockScanner")
        
        # Test get_all_tickers_from_ts method
        print(f"\n📊 Testing ticker retrieval...")
        tickers = await scanner.get_all_tickers_from_ts()
        print(f"   Retrieved {len(tickers)} tickers")
        
        if tickers:
            print(f"   Sample tickers: {tickers[:10]}")
        else:
            print(f"   ⚠️ No tickers retrieved")
        
        return True
        
    except Exception as e:
        print(f"❌ Scanner import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_scoring():
    """Test individual stock scoring"""
    print(f"\n🧮 Testing Individual Stock Scoring")
    print("=" * 50)
    
    try:
        from investment_scoring import investment_scorer
        from enhanced_ticker_data import enhanced_ticker_manager
        
        test_symbol = "AAPL"
        print(f"📊 Testing scoring for {test_symbol}")
        
        # Get stock data
        stock_data = await enhanced_ticker_manager.get_real_time_quote(test_symbol)
        print(f"   Stock data retrieved: {bool(stock_data)}")
        
        if stock_data:
            print(f"   Price: ${stock_data.get('price', 'N/A')}")
            print(f"   Symbol: {stock_data.get('symbol', 'N/A')}")
        
        # Calculate score
        result = await investment_scorer.calculate_investment_score(stock_data)
        print(f"   Score calculation result: {bool(result)}")
        
        if result:
            print(f"   Total Score: {result.get('total_score', 'N/A')}")
            print(f"   Rating: {result.get('rating', 'N/A')}")
            print(f"   Symbol: {result.get('symbol', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual scoring test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main debug function"""
    print(f"🔧 SCANNER DEBUG TESTING")
    print("=" * 80)
    
    tests = [
        ("MongoDB Save Functionality", test_mongodb_save()),
        ("Scanner Import and Initialization", test_scanner_import()),
        ("Individual Stock Scoring", test_individual_scoring())
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n🎯 DEBUG TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 SUCCESS RATE: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print(f"✅ All debug tests passed - scanner components working")
    else:
        print(f"❌ Some debug tests failed - scanner has issues")

if __name__ == "__main__":
    asyncio.run(main())