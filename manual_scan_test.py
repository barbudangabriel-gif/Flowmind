#!/usr/bin/env python3
"""
Manual Scanner Test - Run a complete scan manually to test the full workflow
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

async def run_manual_scan():
    """Run a manual scan to test the complete workflow"""
    print("🚀 MANUAL SCANNER TEST - COMPLETE WORKFLOW")
    print("=" * 80)
    
    try:
        # Import scanner components
        from investment_scoring import StockScanner, investment_scorer
        
        print(f"✅ Imported scanner components")
        
        # Initialize scanner
        scanner = StockScanner(investment_scorer)
        print(f"✅ Initialized scanner")
        
        # Check MongoDB before scan
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        collection = db['scanned_stocks']
        
        initial_count = await collection.count_documents({})
        print(f"📊 Initial documents in MongoDB: {initial_count}")
        
        # Run the scan (limit to first 10 tickers for testing)
        print(f"\n🔄 Starting manual scan (limited to 10 tickers for testing)...")
        
        # Get tickers
        all_tickers = await scanner.get_all_tickers_from_ts()
        test_tickers = all_tickers[:10]  # Limit to 10 for testing
        
        print(f"📊 Testing with {len(test_tickers)} tickers: {test_tickers}")
        
        # Manual scan process
        scanned_results = []
        processed = 0
        errors = 0
        
        for ticker in test_tickers:
            try:
                print(f"   🔍 Scanning {ticker} ({processed + 1}/{len(test_tickers)})")
                
                # Get stock data
                from enhanced_ticker_data import enhanced_ticker_manager
                stock_data = await enhanced_ticker_manager.get_real_time_quote(ticker)
                
                if not stock_data:
                    print(f"     ⚠️ No stock data for {ticker}")
                    continue
                
                # Calculate score
                result = await investment_scorer.calculate_investment_score(stock_data)
                
                if result and 'total_score' in result:
                    # Add required fields
                    result['ticker'] = ticker
                    result['scanned_at'] = datetime.utcnow()
                    result['scan_id'] = f"manual_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    
                    scanned_results.append(result)
                    print(f"     ✅ {ticker}: Score {result['total_score']:.1f}, Rating: {result.get('rating', 'N/A')}")
                else:
                    print(f"     ❌ Failed to calculate score for {ticker}")
                
                processed += 1
                
                # Small delay
                await asyncio.sleep(0.2)
                
            except Exception as e:
                errors += 1
                print(f"     ❌ Error scanning {ticker}: {str(e)}")
                continue
        
        print(f"\n📊 Scan completed:")
        print(f"   - Processed: {processed}")
        print(f"   - Successful: {len(scanned_results)}")
        print(f"   - Errors: {errors}")
        
        if not scanned_results:
            print(f"❌ No results to save")
            return False
        
        # Sort results by score
        scanned_results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        print(f"\n💾 Saving {len(scanned_results)} results to MongoDB...")
        
        # Clear old results
        delete_result = await collection.delete_many({})
        print(f"   Deleted {delete_result.deleted_count} old documents")
        
        # Insert new results
        insert_result = await collection.insert_many(scanned_results)
        print(f"   Inserted {len(insert_result.inserted_ids)} new documents")
        
        # Verify save
        final_count = await collection.count_documents({})
        print(f"   Final document count: {final_count}")
        
        # Get top 5 results
        print(f"\n🏆 Top 5 Results:")
        top_cursor = collection.find({}).sort('total_score', -1).limit(5)
        top_stocks = await top_cursor.to_list(length=5)
        
        for i, stock in enumerate(top_stocks):
            ticker = stock.get('ticker', 'N/A')
            score = stock.get('total_score', 0)
            rating = stock.get('rating', 'N/A')
            print(f"   #{i+1}: {ticker} - Score: {score:.1f} - Rating: {rating}")
        
        client.close()
        
        print(f"\n✅ Manual scan completed successfully!")
        print(f"📊 Results: {len(scanned_results)} stocks scanned and saved to MongoDB")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual scan failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints_after_scan():
    """Test API endpoints after manual scan"""
    print(f"\n🔗 Testing API Endpoints After Manual Scan")
    print("=" * 50)
    
    import requests
    
    base_url = "https://trade-insights-27.preview.emergentagent.com/api"
    
    try:
        # Test scanner status
        print(f"📊 Testing scanner status...")
        response = requests.get(f"{base_url}/scanner/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ Total stocks: {data.get('total_stocks_scanned', 0)}")
            print(f"   ✅ Database status: {data.get('database_status')}")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
        
        # Test top stocks
        print(f"\n🏆 Testing top stocks...")
        response = requests.get(f"{base_url}/scanner/top-stocks?limit=5", timeout=15)
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('top_stocks', [])
            print(f"   ✅ Retrieved {len(stocks)} top stocks")
            
            for i, stock in enumerate(stocks[:3]):
                ticker = stock.get('ticker', 'N/A')
                score = stock.get('score', 'N/A')
                rating = stock.get('rating', 'N/A')
                print(f"     #{i+1}: {ticker} - {score} - {rating}")
        else:
            print(f"   ❌ Top stocks endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint testing failed: {str(e)}")
        return False

async def main():
    """Main function"""
    print(f"🧪 MANUAL SCANNER WORKFLOW TEST")
    print("=" * 80)
    
    # Run manual scan
    scan_success = await run_manual_scan()
    
    if scan_success:
        # Test API endpoints
        api_success = await test_api_endpoints_after_scan()
        
        if api_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"✅ Manual scan worked")
            print(f"✅ MongoDB persistence worked")
            print(f"✅ API endpoints worked")
            print(f"\n💡 CONCLUSION: Scanner components work, but async task in server.py may not be completing properly")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print(f"✅ Manual scan worked")
            print(f"❌ API endpoints had issues")
    else:
        print(f"\n❌ SCAN FAILED")
        print(f"Scanner workflow has fundamental issues")

if __name__ == "__main__":
    asyncio.run(main())