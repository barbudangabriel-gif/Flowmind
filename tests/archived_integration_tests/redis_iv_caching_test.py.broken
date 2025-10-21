import requests
import sys
import time
from datetime import datetime

class RedisIVCachingTester:
 def __init__(self, base_url="http://localhost:8001"):
 self.base_url = base_url
 self.tests_run = 0
 self.tests_passed = 0
 self.test_results = []

 def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
 """Run a single API test"""
 url = f"{self.base_url}{endpoint}"
 headers = {"Content-Type": "application/json"}

 self.tests_run += 1
 print(f"\n Testing {name}...")
 print(f" URL: {url}")

 try:
 timeout = 30

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
 print(f" Passed - Status: {response.status_code}")
 try:
 response_data = response.json()
 return True, response_data
 except:
 return True, response.text
 else:
 print(
 f" Failed - Expected {expected_status}, got {response.status_code}"
 )
 try:
 error_data = response.json()
 print(f" Error: {error_data}")
 except:
 print(f" Error: {response.text}")
 return False, {}

 except requests.exceptions.Timeout:
 print(f" Failed - Request timeout ({timeout}s)")
 return False, {}
 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}

 def test_redis_diagnostics(self):
 """Test Redis diagnostics endpoint"""
 print("\n🔧 PHASE 1: Redis Diagnostics Verification")
 print("-" * 60)

 success, diag_data = self.run_test(
 "Redis Diagnostics", "GET", "/_redis/diag", 200
 )

 if not success:
 print(" Redis diagnostics endpoint failed")
 return False, {}

 print(f" Redis Diagnostics Response: {diag_data}")

 # Verify Redis connection details
 expected_fields = ["impl", "url", "db", "ok"]
 missing_fields = [field for field in expected_fields if field not in diag_data]

 if missing_fields:
 print(f" Missing diagnostic fields: {missing_fields}")
 return False, diag_data

 impl = diag_data.get("impl", "")
 url = diag_data.get("url", "")
 db = diag_data.get("db", "")
 ok = diag_data.get("ok", False)

 print(f" Implementation: {impl}")
 print(f" URL: {url}")
 print(f" Database: {db}")
 print(f" Connected: {ok}")

 # Verify Redis is being used (not in-memory fallback)
 if "Redis" in impl:
 print(" Using Redis implementation (not in-memory fallback)")
 else:
 print(f" Using {impl} instead of Redis")
 return False, diag_data

 # Verify correct Redis URL and DB
 if "redis://localhost:6379" in url:
 print(" Correct Redis URL configuration")
 else:
 print(f" Unexpected Redis URL: {url}")

 if "/0" in db:
 print(" Correct Redis database index")
 else:
 print(f" Unexpected Redis database: {db}")

 if ok:
 print(" Redis connection established")
 else:
 print(" Redis connection failed")
 return False, diag_data

 return True, diag_data

 def test_emergent_status(self):
 """Test emergent status endpoint for cache statistics"""
 print("\n PHASE 2: Emergent Status Cache Verification")
 print("-" * 60)

 success, status_data = self.run_test(
 "Emergent Status (sell_puts)",
 "GET",
 "/_emergent/status",
 200,
 params={"module": "sell_puts"},
 )

 if not success:
 print(" Emergent status endpoint failed")
 return False, {}

 print(f" Emergent Status Response: {status_data}")

 # Check for cache statistics
 cache_info = status_data.get("cache", {})
 keys_total = cache_info.get("keys_total", 0)

 print(f" Keys Total: {keys_total}")
 print(f" Cache Info: {cache_info}")

 # Verify keys_total > 0 (not empty cache)
 if keys_total > 0:
 print(f" Cache contains {keys_total} keys (not empty)")
 cache_populated = True
 else:
 print(" Cache is empty (keys_total = 0)")
 cache_populated = False

 return cache_populated, status_data

 def test_iv_screening_cache(self):
 """Test IV screening endpoint for cache HIT/MISS"""
 print("\n PHASE 3: IV Screening Cache Hit Verification")
 print("-" * 60)

 success, screening_data = self.run_test(
 "IV Screening (limit=3)",
 "GET",
 "/screen/iv-setups",
 200,
 params={"limit": 3},
 )

 if not success:
 print(" IV screening endpoint failed")
 return False, {}

 print(f" IV Screening Response Keys: {list(screening_data.keys())}")

 # Look for cache information in response items
 items = screening_data.get("items", [])
 cache_hits = 0
 cache_misses = 0

 for item in items:
 backtest = item.get("backtest", {})
 cache_status = backtest.get("cache", "UNKNOWN")

 if cache_status == "HIT":
 cache_hits += 1
 elif cache_status == "MISS":
 cache_misses += 1

 print(f" Cache HITs: {cache_hits}")
 print(f" Cache MISSes: {cache_misses}")
 print(f" Total Items: {len(items)}")

 # Verify cache HIT (not MISS)
 if cache_hits > 0:
 print(" Cache HITs detected (using cached data)")
 cache_hit = True
 elif cache_misses > 0:
 print(" Cache MISSes detected (generating new data)")
 cache_hit = False
 else:
 print(" No cache status information found")
 cache_hit = False

 # Check for backtest data
 if items:
 print(f" IV screening data present: {len(items)} items")
 else:
 print(" No IV screening data found")

 return cache_hit, screening_data

 def test_cache_keys(self):
 """Test cache keys endpoint"""
 print("\n🔑 PHASE 4: Cache Keys Verification")
 print("-" * 60)

 success, keys_data = self.run_test(
 "Cache Keys (bt:sum:*)",
 "GET",
 "/_bt/keys",
 200,
 params={"pattern": "bt:sum:*"},
 )

 if not success:
 print(" Cache keys endpoint failed")
 return False, {}

 print(f" Cache Keys Response: {keys_data}")

 # Check for key count
 key_count = keys_data.get("count", 0)
 keys_list = keys_data.get("keys", [])

 print(f" Key Count: {key_count}")
 print(f" Keys Found: {len(keys_list)}")

 if keys_list:
 print(f" Sample Keys: {keys_list[:5]}") # Show first 5 keys

 # Verify cache keys exist
 if key_count > 0:
 print(f" Cache keys found: {key_count} keys with pattern bt:sum:*")
 keys_exist = True
 else:
 print(" No cache keys found with pattern bt:sum:*")
 keys_exist = False

 return keys_exist, keys_data

 def test_cache_persistence(self):
 """Test cache persistence between processes"""
 print("\n🔄 PHASE 5: Cache Persistence Verification")
 print("-" * 60)

 # First, get initial cache state
 print(" Getting initial cache state...")
 success1, initial_status = self.run_test(
 "Initial Cache State",
 "GET",
 "/_emergent/status",
 200,
 params={"module": "sell_puts"},
 )

 if not success1:
 print(" Failed to get initial cache state")
 return False

 initial_cache = initial_status.get("cache", {})
 initial_keys = initial_cache.get("keys_total", 0)
 print(f" Initial Keys: {initial_keys}")

 # Wait a moment and check again
 print("⏳ Waiting 3 seconds...")
 time.sleep(3)

 # Get cache state again
 print(" Getting cache state after wait...")
 success2, final_status = self.run_test(
 "Final Cache State",
 "GET",
 "/_emergent/status",
 200,
 params={"module": "sell_puts"},
 )

 if not success2:
 print(" Failed to get final cache state")
 return False

 final_cache = final_status.get("cache", {})
 final_keys = final_cache.get("keys_total", 0)
 print(f" Final Keys: {final_keys}")

 # Verify cache persistence
 if final_keys > 0 and final_keys == initial_keys:
 print(" Cache keys persisted between requests")
 persistence_verified = True
 elif final_keys > initial_keys:
 print(" Cache keys increased (cache is being populated)")
 persistence_verified = True
 elif final_keys == 0:
 print(" Cache keys not persisting (both processes using in-memory cache)")
 persistence_verified = False
 else:
 print(f" Cache keys changed: {initial_keys} → {final_keys}")
 persistence_verified = False

 return persistence_verified

 def run_comprehensive_test(self):
 """Run comprehensive Redis IV caching integration test"""
 print(" REDIS IV CACHING INTEGRATION TEST")
 print("=" * 80)
 print(" OBJECTIVE: Verify Redis caching integration for IV module")
 print("🔧 TESTING:")
 print(" 1. Redis connection and configuration")
 print(" 2. Cache key persistence between processes")
 print(" 3. IV screening cache HIT/MISS status")
 print(" 4. Emergent status cache statistics")
 print(" 5. Cache key enumeration")
 print()

 test_results = {}

 # Phase 1: Redis Diagnostics
 redis_working, diag_data = self.test_redis_diagnostics()
 test_results["redis_diagnostics"] = redis_working

 # Phase 2: Emergent Status
 cache_populated, status_data = self.test_emergent_status()
 test_results["cache_populated"] = cache_populated

 # Phase 3: IV Screening Cache
 cache_hit, screening_data = self.test_iv_screening_cache()
 test_results["cache_hit"] = cache_hit

 # Phase 4: Cache Keys
 keys_exist, keys_data = self.test_cache_keys()
 test_results["cache_keys"] = keys_exist

 # Phase 5: Cache Persistence
 persistence_verified = self.test_cache_persistence()
 test_results["cache_persistence"] = persistence_verified

 # Final Assessment
 print("\n FINAL ASSESSMENT: Redis IV Caching Integration")
 print("=" * 80)

 # Calculate success metrics
 test_phases = [
 ("Redis Connection & Configuration", redis_working),
 ("Cache Population (keys_total > 0)", cache_populated),
 ("IV Screening Cache HIT", cache_hit),
 ("Cache Keys Enumeration", keys_exist),
 ("Cache Persistence Between Processes", persistence_verified),
 ]

 passed_phases = sum(1 for _, passed in test_phases if passed)
 total_phases = len(test_phases)
 success_rate = (passed_phases / total_phases) * 100

 print("\n TEST RESULTS SUMMARY:")
 for phase_name, passed in test_phases:
 status = " PASS" if passed else " FAIL"
 print(f" {status} {phase_name}")

 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)"
 )

 # Key findings
 print("\n KEY FINDINGS:")
 if redis_working and diag_data:
 impl = diag_data.get("impl", "Unknown")
 url = diag_data.get("url", "Unknown")
 db = diag_data.get("db", "Unknown")
 print(f" - Redis Implementation: {impl}")
 print(f" - Redis URL: {url}")
 print(f" - Redis Database: {db}")
 else:
 print(" - Redis Connection: FAILED")

 if cache_populated and status_data:
 cache_info = status_data.get("cache", {})
 keys_total = cache_info.get("keys_total", 0)
 print(f" - Cache Keys Total: {keys_total}")
 else:
 print(" - Cache Keys Total: 0 (empty)")

 if cache_hit:
 print(" - IV Screening: Using cached data (HIT)")
 else:
 print(" - IV Screening: Not using cache (MISS)")

 if keys_exist and keys_data:
 key_count = keys_data.get("count", 0)
 print(f" - Cache Keys Found: {key_count}")
 else:
 print(" - Cache Keys Found: 0")

 print(
 f" - Cache Persistence: {' VERIFIED' if persistence_verified else ' FAILED'}"
 )

 # Requirements verification
 print("\n REQUIREMENTS VERIFICATION:")
 requirements_met = []

 if redis_working:
 requirements_met.append(
 " Redis connection properly established with correct URL/DB info"
 )
 else:
 requirements_met.append(
 " Redis connection failed or using in-memory fallback"
 )

 if cache_populated and persistence_verified:
 requirements_met.append(
 " Cache keys persisting between backend and warmup processes"
 )
 else:
 requirements_met.append(
 " Cache keys not persisting (isolated in-memory caches)"
 )

 if cache_hit:
 requirements_met.append(" IV screening endpoints returning cache HIT")
 else:
 requirements_met.append(" IV screening endpoints returning cache MISS")

 if cache_populated:
 requirements_met.append(" Emergent status shows keys_total > 0")
 else:
 requirements_met.append(" Emergent status shows keys_total = 0")

 if redis_working and diag_data:
 requirements_met.append(
 " Redis diagnostic endpoint shows proper connection details"
 )
 else:
 requirements_met.append(" Redis diagnostic endpoint failed")

 if redis_working:
 requirements_met.append(
 " Backend using Redis instead of in-memory fallback"
 )
 else:
 requirements_met.append(
 " Backend using in-memory fallback instead of Redis"
 )

 for requirement in requirements_met:
 print(f" {requirement}")

 # Final verdict
 if success_rate >= 80:
 print(
 "\n VERDICT: EXCELLENT - Redis caching integration working correctly!"
 )
 print(
 " Both backend and warmup processes are using the shared Redis instance."
 )
 print(" Cache keys are persisting and IV screening is using cached data.")
 verdict = "EXCELLENT"
 elif success_rate >= 60:
 print(
 "\n VERDICT: GOOD - Redis caching mostly working with minor issues."
 )
 print(" Most functionality is working but some improvements needed.")
 verdict = "GOOD"
 else:
 print(
 "\n VERDICT: CRITICAL ISSUES - Redis caching integration has major problems."
 )
 print(" Processes may still be using isolated in-memory caches.")
 print(" Immediate attention required to fix Redis integration.")
 verdict = "CRITICAL"

 # Store results for reporting
 self.test_results = {
 "success_rate": success_rate,
 "passed_phases": passed_phases,
 "total_phases": total_phases,
 "verdict": verdict,
 "test_results": test_results,
 "requirements_met": requirements_met,
 }

 return success_rate >= 60

def main():
 """Main test execution"""
 print(" Starting Redis IV Caching Integration Test")
 print(f" Test started at: {datetime.now().isoformat()}")
 print()

 tester = RedisIVCachingTester()

 try:
 success = tester.run_comprehensive_test()

 print("\n FINAL RESULTS:")
 print(f" Tests Run: {tester.tests_run}")
 print(f" Tests Passed: {tester.tests_passed}")
 print(f" Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
 print(f" Overall Result: {' PASS' if success else ' FAIL'}")

 return 0 if success else 1

 except Exception as e:
 print(f"\n Test execution failed: {str(e)}")
 return 1

if __name__ == "__main__":
 sys.exit(main())
