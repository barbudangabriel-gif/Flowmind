#!/usr/bin/env python3
"""
Performance & Load Testing for Health Endpoints
Tests response times, concurrent load, and bottlenecks
"""
import asyncio
import time
import statistics
import httpx
from typing import List, Dict, Any
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
ENDPOINTS = [
 "/health",
 "/healthz", 
 "/readyz",
 "/api/health/redis"
]

# Test parameters
WARMUP_REQUESTS = 10
LOAD_TEST_CONCURRENT = 100
LOAD_TEST_TOTAL = 1000
TIMEOUT = 5.0

class HealthEndpointTester:
 def __init__(self, base_url: str):
 self.base_url = base_url
 self.results = {}
 
 async def single_request(self, endpoint: str, client: httpx.AsyncClient) -> Dict[str, Any]:
 """Make single request and measure performance"""
 start = time.perf_counter()
 try:
 response = await client.get(f"{self.base_url}{endpoint}", timeout=TIMEOUT)
 elapsed = (time.perf_counter() - start) * 1000 # ms
 
 return {
 "success": True,
 "status": response.status_code,
 "elapsed_ms": elapsed,
 "size_bytes": len(response.content)
 }
 except Exception as e:
 elapsed = (time.perf_counter() - start) * 1000
 return {
 "success": False,
 "error": str(e),
 "elapsed_ms": elapsed
 }
 
 async def warmup(self, endpoint: str):
 """Warmup requests to establish connections"""
 print(f" Warming up {endpoint}...")
 async with httpx.AsyncClient() as client:
 tasks = [self.single_request(endpoint, client) for _ in range(WARMUP_REQUESTS)]
 await asyncio.gather(*tasks)
 
 async def measure_sequential(self, endpoint: str, count: int = 100) -> Dict[str, Any]:
 """Measure sequential request performance"""
 print(f" Sequential test ({count} requests)...")
 
 async with httpx.AsyncClient() as client:
 results = []
 for _ in range(count):
 result = await self.single_request(endpoint, client)
 results.append(result)
 
 return self._analyze_results(results)
 
 async def measure_concurrent(self, endpoint: str, concurrent: int, total: int) -> Dict[str, Any]:
 """Measure concurrent request performance"""
 print(f" Concurrent test ({total} requests, {concurrent} concurrent)...")
 
 async with httpx.AsyncClient(limits=httpx.Limits(max_connections=concurrent)) as client:
 all_results = []
 
 # Run in batches
 for batch_start in range(0, total, concurrent):
 batch_size = min(concurrent, total - batch_start)
 tasks = [self.single_request(endpoint, client) for _ in range(batch_size)]
 batch_results = await asyncio.gather(*tasks)
 all_results.extend(batch_results)
 
 return self._analyze_results(all_results)
 
 def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
 """Analyze performance metrics"""
 success_results = [r for r in results if r["success"]]
 failed_results = [r for r in results if not r["success"]]
 
 if not success_results:
 return {
 "total": len(results),
 "success": 0,
 "failed": len(failed_results),
 "success_rate": 0.0,
 "error": "All requests failed"
 }
 
 elapsed_times = [r["elapsed_ms"] for r in success_results]
 
 return {
 "total": len(results),
 "success": len(success_results),
 "failed": len(failed_results),
 "success_rate": len(success_results) / len(results) * 100,
 "response_time": {
 "min": round(min(elapsed_times), 2),
 "max": round(max(elapsed_times), 2),
 "mean": round(statistics.mean(elapsed_times), 2),
 "median": round(statistics.median(elapsed_times), 2),
 "p95": round(statistics.quantiles(elapsed_times, n=20)[18], 2) if len(elapsed_times) > 20 else round(max(elapsed_times), 2),
 "p99": round(statistics.quantiles(elapsed_times, n=100)[98], 2) if len(elapsed_times) > 100 else round(max(elapsed_times), 2),
 },
 "throughput_rps": round(len(success_results) / (sum(elapsed_times) / 1000), 2) if elapsed_times else 0
 }
 
 async def test_endpoint(self, endpoint: str):
 """Full test suite for endpoint"""
 print(f"\n{'='*70}")
 print(f" Testing: {endpoint}")
 print(f"{'='*70}")
 
 # Warmup
 await self.warmup(endpoint)
 
 # Sequential baseline
 seq_results = await self.measure_sequential(endpoint, count=50)
 
 # Concurrent load test
 concurrent_results = await self.measure_concurrent(
 endpoint, 
 concurrent=LOAD_TEST_CONCURRENT,
 total=LOAD_TEST_TOTAL
 )
 
 self.results[endpoint] = {
 "sequential": seq_results,
 "concurrent": concurrent_results
 }
 
 # Display results
 self._display_endpoint_results(endpoint)
 
 def _display_endpoint_results(self, endpoint: str):
 """Display formatted results"""
 data = self.results[endpoint]
 
 print(f"\n SEQUENTIAL PERFORMANCE:")
 seq = data["sequential"]
 print(f" Total Requests: {seq['total']}")
 print(f" Success Rate: {seq['success_rate']:.1f}%")
 print(f" Response Time:")
 print(f" Min: {seq['response_time']['min']}ms")
 print(f" Mean: {seq['response_time']['mean']}ms")
 print(f" Median: {seq['response_time']['median']}ms")
 print(f" P95: {seq['response_time']['p95']}ms")
 print(f" Max: {seq['response_time']['max']}ms")
 
 print(f"\n CONCURRENT PERFORMANCE:")
 conc = data["concurrent"]
 print(f" Total Requests: {conc['total']}")
 print(f" Success Rate: {conc['success_rate']:.1f}%")
 print(f" Failed: {conc['failed']}")
 print(f" Response Time:")
 print(f" Min: {conc['response_time']['min']}ms")
 print(f" Mean: {conc['response_time']['mean']}ms")
 print(f" Median: {conc['response_time']['median']}ms")
 print(f" P95: {conc['response_time']['p95']}ms")
 print(f" P99: {conc['response_time']['p99']}ms")
 print(f" Max: {conc['response_time']['max']}ms")
 print(f" Throughput: {conc['throughput_rps']} req/s")
 
 # Performance assessment
 self._assess_performance(endpoint, conc)
 
 def _assess_performance(self, endpoint: str, results: Dict[str, Any]):
 """Assess if performance meets SLA"""
 print(f"\n PERFORMANCE ASSESSMENT:")
 
 checks = []
 
 # Success rate > 99%
 if results["success_rate"] >= 99:
 checks.append(("", "Success Rate", f"{results['success_rate']:.1f}% (Target: ≥99%)"))
 else:
 checks.append(("", "Success Rate", f"{results['success_rate']:.1f}% (Target: ≥99%)"))
 
 # P95 < 100ms
 p95 = results["response_time"]["p95"]
 if p95 < 100:
 checks.append(("", "P95 Latency", f"{p95}ms (Target: <100ms)"))
 elif p95 < 200:
 checks.append(("", "P95 Latency", f"{p95}ms (Target: <100ms, Acceptable: <200ms)"))
 else:
 checks.append(("", "P95 Latency", f"{p95}ms (Target: <100ms)"))
 
 # P99 < 200ms
 p99 = results["response_time"]["p99"]
 if p99 < 200:
 checks.append(("", "P99 Latency", f"{p99}ms (Target: <200ms)"))
 elif p99 < 500:
 checks.append(("", "P99 Latency", f"{p99}ms (Target: <200ms, Acceptable: <500ms)"))
 else:
 checks.append(("", "P99 Latency", f"{p99}ms (Target: <200ms)"))
 
 for icon, metric, status in checks:
 print(f" {icon} {metric}: {status}")
 
 def generate_summary(self):
 """Generate overall performance summary"""
 print(f"\n{'='*70}")
 print(f" OVERALL SUMMARY")
 print(f"{'='*70}\n")
 
 print(f"{'Endpoint':<30} {'Mean (ms)':<12} {'P95 (ms)':<12} {'Success %':<12}")
 print(f"{'-'*70}")
 
 for endpoint, data in self.results.items():
 conc = data["concurrent"]
 print(f"{endpoint:<30} "
 f"{conc['response_time']['mean']:<12} "
 f"{conc['response_time']['p95']:<12} "
 f"{conc['success_rate']:.1f}%")
 
 print(f"\n RECOMMENDATIONS:")
 
 # Check if all endpoints meet SLA
 all_good = True
 issues = []
 
 for endpoint, data in self.results.items():
 conc = data["concurrent"]
 if conc["success_rate"] < 99:
 all_good = False
 issues.append(f" {endpoint}: Success rate below 99%")
 if conc["response_time"]["p95"] > 200:
 all_good = False
 issues.append(f" {endpoint}: P95 latency above 200ms")
 
 if all_good:
 print(" All endpoints meet performance SLA!")
 print(" Ready for production deployment")
 else:
 print(" Some endpoints need optimization:")
 for issue in issues:
 print(issue)
 print("\n Recommended actions:")
 print(" - Add caching for expensive operations")
 print(" - Optimize database queries")
 print(" - Consider connection pooling")
 print(" - Add CDN for static content")

async def main():
 """Main test execution"""
 print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║ FlowMind Health Endpoints Performance Test ║
║ ║
║ Backend: {BACKEND_URL:<56}║
║ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<59}║
╚══════════════════════════════════════════════════════════════════════╝
 """)
 
 print(f"\n Test Configuration:")
 print(f" Warmup Requests: {WARMUP_REQUESTS}")
 print(f" Sequential Test: 50 requests")
 print(f" Concurrent Test: {LOAD_TEST_TOTAL} total, {LOAD_TEST_CONCURRENT} concurrent")
 print(f" Timeout: {TIMEOUT}s")
 
 # Check if server is running
 print(f"\n Checking server availability...")
 try:
 async with httpx.AsyncClient() as client:
 response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
 if response.status_code == 200:
 print(f" Server is running")
 else:
 print(f" Server returned status {response.status_code}")
 except Exception as e:
 print(f" Server not available: {e}")
 print(f"\n Start server with:")
 print(f" cd backend && python -m uvicorn server:app --port 8000")
 return
 
 # Run tests
 tester = HealthEndpointTester(BACKEND_URL)
 
 for endpoint in ENDPOINTS:
 await tester.test_endpoint(endpoint)
 
 # Generate summary
 tester.generate_summary()
 
 print(f"\n{'='*70}")
 print(f" Performance testing complete!")
 print(f"{'='*70}\n")

if __name__ == "__main__":
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 print("\n\n Test interrupted by user")
 except Exception as e:
 print(f"\n\n Test failed: {e}")
 raise
