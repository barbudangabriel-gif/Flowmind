#!/usr/bin/env python3
"""
Test API MongoDB Connection - Check if API is using the same MongoDB as our manual tests
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

async def test_api_mongodb_connection():
    """Test the exact MongoDB connection used by the API"""
    print("🔍 TESTING API MONGODB CONNECTION")
    print("=" * 80)
    
    try:
        # Import the exact same way as server.py
        print("📡 Importing server.py MongoDB connection...")
        
        # Replicate server.py imports and connection
        from pathlib import Path
        from motor.motor_asyncio import AsyncIOMotorClient
        
        ROOT_DIR = Path('/app/backend')
        load_dotenv(ROOT_DIR / '.env')
        
        # MongoDB connection (same as server.py)
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print(f"✅ Connected using server.py method")
        print(f"   MONGO_URL: {mongo_url}")
        print(f"   DB_NAME: {os.environ['DB_NAME']}")
        
        # Test the scanned_stocks collection
        collection = db['scanned_stocks']
        
        # Count documents
        count = await collection.count_documents({})
        print(f"📊 Documents in scanned_stocks collection: {count}")
        
        if count > 0:
            print(f"✅ Found {count} documents - API should see them")
            
            # Get sample documents
            cursor = collection.find({}).limit(3)
            docs = await cursor.to_list(length=3)
            
            print(f"📋 Sample documents:")
            for i, doc in enumerate(docs):
                print(f"   #{i+1}: {doc.get('ticker')} - Score: {doc.get('total_score')} - Rating: {doc.get('rating')}")
                print(f"        Scanned at: {doc.get('scanned_at')}")
                print(f"        Scan ID: {doc.get('scan_id')}")
        else:
            print(f"❌ No documents found - API will show empty")
        
        # Test the exact same query as server.py status endpoint
        print(f"\n🔍 Testing server.py status endpoint queries...")
        
        # Query 1: Count documents (line 899)
        total_stocks = await collection.count_documents({})
        print(f"   total_stocks query result: {total_stocks}")
        
        if total_stocks > 0:
            # Query 2: Latest scan (lines 903-905)
            latest_scan = await collection.find_one(
                {}, sort=[('scanned_at', -1)]
            )
            print(f"   latest_scan found: {bool(latest_scan)}")
            if latest_scan:
                print(f"     scanned_at: {latest_scan.get('scanned_at')}")
                print(f"     scan_id: {latest_scan.get('scan_id')}")
            
            # Query 3: Top 5 stocks (lines 909-914)
            top_5 = []
            async for stock in collection.find({}).sort('total_score', -1).limit(5):
                top_5.append({
                    'ticker': stock.get('ticker'),
                    'score': round(stock.get('total_score', 0), 1),
                    'rating': stock.get('rating')
                })
            
            print(f"   top_5 query result: {len(top_5)} stocks")
            for stock in top_5:
                print(f"     {stock['ticker']}: {stock['score']} - {stock['rating']}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ API MongoDB connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_import_scanned_stocks_collection():
    """Test importing scanned_stocks_collection directly from investment_scoring"""
    print(f"\n🔍 Testing Direct Import of scanned_stocks_collection")
    print("=" * 50)
    
    try:
        # Import exactly as server.py does
        from investment_scoring import scanned_stocks_collection
        
        print(f"✅ Successfully imported scanned_stocks_collection")
        
        # Test count
        count = await scanned_stocks_collection.count_documents({})
        print(f"📊 Documents via direct import: {count}")
        
        if count > 0:
            # Get sample
            cursor = scanned_stocks_collection.find({}).limit(2)
            docs = await cursor.to_list(length=2)
            
            print(f"📋 Sample via direct import:")
            for doc in docs:
                print(f"   {doc.get('ticker')}: {doc.get('total_score')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_call_simulation():
    """Simulate the exact API call logic"""
    print(f"\n🔍 Simulating API Call Logic")
    print("=" * 50)
    
    try:
        # Replicate the exact logic from get_scanner_status()
        from investment_scoring import scanned_stocks_collection
        
        total_stocks = await scanned_stocks_collection.count_documents({})
        print(f"📊 total_stocks: {total_stocks}")
        
        if total_stocks > 0:
            # Găsește cel mai recent scan
            latest_scan = await scanned_stocks_collection.find_one(
                {}, sort=[('scanned_at', -1)]
            )
            
            # Top 5 acțiuni
            top_5 = []
            async for stock in scanned_stocks_collection.find({}).sort('total_score', -1).limit(5):
                top_5.append({
                    'ticker': stock.get('ticker'),
                    'score': round(stock.get('total_score', 0), 1),
                    'rating': stock.get('rating')
                })
            
            result = {
                "status": "completed" if total_stocks > 0 else "no_scans",
                "total_stocks_scanned": total_stocks,
                "last_scan_date": latest_scan.get('scanned_at') if latest_scan else None,
                "scan_id": latest_scan.get('scan_id') if latest_scan else None,
                "top_5_stocks": top_5,
                "database_status": "active"
            }
        else:
            result = {
                "status": "no_scans",
                "message": "Nu există scanări în baza de date. Pornește o scanare cu /scanner/start-scan",
                "total_stocks_scanned": 0,
                "database_status": "empty"
            }
        
        print(f"📋 Simulated API response:")
        print(f"   Status: {result.get('status')}")
        print(f"   Total stocks: {result.get('total_stocks_scanned')}")
        print(f"   Database status: {result.get('database_status')}")
        print(f"   Top 5 stocks: {len(result.get('top_5_stocks', []))}")
        
        return result
        
    except Exception as e:
        print(f"❌ API simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function"""
    print(f"🧪 API MONGODB CONNECTION TESTING")
    print("=" * 80)
    
    tests = [
        ("API MongoDB Connection", test_api_mongodb_connection()),
        ("Direct Import Test", test_import_scanned_stocks_collection()),
        ("API Call Simulation", test_api_call_simulation())
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
    print(f"\n🎯 API MONGODB TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results:
        if test_name == "API Call Simulation":
            if result and result.get('total_stocks_scanned', 0) > 0:
                print(f"✅ PASS {test_name} - Found {result['total_stocks_scanned']} stocks")
            else:
                print(f"❌ FAIL {test_name} - No stocks found")
        else:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")

if __name__ == "__main__":
    asyncio.run(main())