#!/usr/bin/env python3
"""
Performance Testing for FlowMind Health Endpoints
Tests response times under concurrent load
"""
import asyncio
import httpx
import time
from statistics import mean, median, stdev
from typing import List, Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_REQUESTS = 100 # Start with 100, can scale to 1000
ENDPOINTS = [
 "/health",
 "/healthz",
 "/readyz",
 "/api/health/redis",
]

class HealthEndpointPerformanceTester:
 def __init__(self, base_url: str = BASE_URL):
 self.base_url = base_url
 self.results: Dict[str, List[float]] = {ep: [] for ep in ENDPOINTS}
 
 async def test_endpoint(self, client: httpx.AsyncClient, endpoint: str) -> float:
 """Test single endpoint and return response time in ms"""
 start = time.perf_counter()
 try:
 response = await client.get(f"{self.base_url}{endpoint}", timeout=10.0)
 end = time.perf_counter()
 
 if response.status_code == 200:
 return (end - start) * 1000 # Convert to ms
 else:
 print(f" {endpoint} returned {response.status_code}")
 return -1
 except Exception as e:
 print(f" {endpoint} error: {e}")
 return -1
 
 async def run_concurrent_tests(self, endpoint: str, count: int = CONCURRENT_REQUESTS):
 """Run multiple concurrent requests to single endpoint"""
 async with httpx.AsyncClient() as client:
 tasks = [self.test_endpoint(client, endpoint) for _ in range(count)]
 response_times = await asyncio.gather(*tasks)
 
 # Filter out errors
 valid_times = [t for t in response_times if t > 0]
 self.results[endpoint] = valid_times
 
 return valid_times
 
 async def test_all_endpoints(self):
 """Test all endpoints concurrently"""
 print(f" Starting performance tests...")
 print(f" Base URL: {self.base_url}")
 print(f" Concurrent requests per endpoint: {CONCURRENT_REQUESTS}")
 print(f" Endpoints: {len(ENDPOINTS)}")
 print()
 
 for endpoint in ENDPOINTS:
 print(f" Testing {endpoint}...")
 times = await self.run_concurrent_tests(endpoint)
 
 if times:
 print(f" Success: {len(times)}/{CONCURRENT_REQUESTS} requests")
 print(f" Mean: {mean(times):.2f}ms")
 print(f" Median: {median(times):.2f}ms")
 if len(times) > 1:
 print(f" StdDev: {stdev(times):.2f}ms")
 print(f" Min: {min(times):.2f}ms")
 print(f" Max: {max(times):.2f}ms")
 print(f" P95: {sorted(times)[int(len(times) * 0.95)]:.2f}ms")
 print(f" P99: {sorted(times)[int(len(times) * 0.99)]:.2f}ms")
 else:
 print(f" All requests failed")
 print()
 
 def generate_report(self) -> str:
 """Generate performance report"""
 report = ["=" * 80]
 report.append("🏁 PERFORMANCE TEST RESULTS SUMMARY")
 report.append("=" * 80)
 report.append("")
 
 for endpoint, times in self.results.items():
 if not times:
 report.append(f" {endpoint}: NO DATA")
 continue
 
 report.append(f"📍 {endpoint}")
 report.append(f" Requests: {len(times)}/{CONCURRENT_REQUESTS} successful")
 report.append(f" Mean Response Time: {mean(times):.2f}ms")
 report.append(f" Median Response Time: {median(times):.2f}ms")
 report.append(f" 95th Percentile: {sorted(times)[int(len(times) * 0.95)]:.2f}ms")
 report.append(f" 99th Percentile: {sorted(times)[int(len(times) * 0.99)]:.2f}ms")
 report.append("")
 
 # Overall assessment
 all_times = [t for times in self.results.values() for t in times if t > 0]
 if all_times:
 report.append(" OVERALL STATISTICS")
 report.append(f" Total Successful Requests: {len(all_times)}")
 report.append(f" Average Response Time: {mean(all_times):.2f}ms")
 report.append(f" Median Response Time: {median(all_times):.2f}ms")
 report.append("")
 
 # Performance thresholds
 report.append(" PERFORMANCE ASSESSMENT")
 avg_time = mean(all_times)
 if avg_time < 50:
 report.append(" EXCELLENT - Response times under 50ms")
 elif avg_time < 100:
 report.append(" GOOD - Response times under 100ms")
 elif avg_time < 200:
 report.append(" ACCEPTABLE - Response times under 200ms")
 else:
 report.append(" POOR - Response times over 200ms")
 
 report.append("=" * 80)
 return "\n".join(report)

async def main():
 """Main test execution"""
 print("=" * 80)
 print("🏥 FlowMind Health Endpoints Performance Test")
 print("=" * 80)
 print()
 
 tester = HealthEndpointPerformanceTester()
 
 try:
 await tester.test_all_endpoints()
 print(tester.generate_report())
 
 # Save report
 with open("/workspaces/Flowmind/health_performance_report.txt", "w") as f:
 f.write(tester.generate_report())
 print("\n Report saved to: health_performance_report.txt")
 
 except Exception as e:
 print(f" Test failed: {e}")
 return 1
 
 return 0

if __name__ == "__main__":
 exit_code = asyncio.run(main())
 exit(exit_code)
