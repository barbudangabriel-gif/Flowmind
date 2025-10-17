"""
Prometheus Metrics for FlowMind Analytics Platform

Tracks API performance, business metrics, and system health.
Export endpoint: GET /metrics
"""

from prometheus_client import (
 Counter,
 Histogram,
 Gauge,
 Info,
 generate_latest,
 CONTENT_TYPE_LATEST
)
from functools import wraps
import time
import logging
from typing import Callable
import asyncio

logger = logging.getLogger(__name__)

# ============================================================================
# API Performance Metrics
# ============================================================================

api_requests_total = Counter(
 'flowmind_api_requests_total',
 'Total number of API requests',
 ['endpoint', 'method', 'status']
)

api_request_duration_seconds = Histogram(
 'flowmind_api_request_duration_seconds',
 'API request latency in seconds',
 ['endpoint', 'method'],
 buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

api_request_size_bytes = Histogram(
 'flowmind_api_request_size_bytes',
 'API request body size in bytes',
 ['endpoint'],
 buckets=[100, 1000, 10000, 100000, 1000000]
)

api_response_size_bytes = Histogram(
 'flowmind_api_response_size_bytes',
 'API response body size in bytes',
 ['endpoint'],
 buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

# ============================================================================
# Business Metrics
# ============================================================================

strategies_priced_total = Counter(
 'flowmind_strategies_priced_total',
 'Total number of options strategies priced',
 ['strategy_type', 'symbol']
)

flow_trades_processed_total = Counter(
 'flowmind_flow_trades_processed_total',
 'Total number of options flow trades processed',
 ['symbol', 'trade_type']
)

portfolios_active = Gauge(
 'flowmind_portfolios_active',
 'Number of active portfolios'
)

positions_open = Gauge(
 'flowmind_positions_open',
 'Number of open positions across all portfolios',
 ['portfolio_id']
)

portfolio_value_usd = Gauge(
 'flowmind_portfolio_value_usd',
 'Portfolio market value in USD',
 ['portfolio_id', 'portfolio_name']
)

# ============================================================================
# Cache Metrics
# ============================================================================

cache_hits_total = Counter(
 'flowmind_cache_hits_total',
 'Number of cache hits',
 ['cache_type', 'key_prefix']
)

cache_misses_total = Counter(
 'flowmind_cache_misses_total',
 'Number of cache misses',
 ['cache_type', 'key_prefix']
)

cache_size_bytes = Gauge(
 'flowmind_cache_size_bytes',
 'Approximate cache size in bytes',
 ['cache_type']
)

cache_entries = Gauge(
 'flowmind_cache_entries',
 'Number of entries in cache',
 ['cache_type']
)

# ============================================================================
# External API Metrics
# ============================================================================

external_api_requests_total = Counter(
 'flowmind_external_api_requests_total',
 'Total requests to external APIs',
 ['provider', 'endpoint', 'status']
)

external_api_duration_seconds = Histogram(
 'flowmind_external_api_duration_seconds',
 'External API request latency',
 ['provider', 'endpoint'],
 buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

external_api_errors_total = Counter(
 'flowmind_external_api_errors_total',
 'Total errors from external APIs',
 ['provider', 'error_type']
)

# ============================================================================
# Database Metrics
# ============================================================================

db_queries_total = Counter(
 'flowmind_db_queries_total',
 'Total database queries',
 ['operation', 'collection']
)

db_query_duration_seconds = Histogram(
 'flowmind_db_query_duration_seconds',
 'Database query latency',
 ['operation', 'collection'],
 buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

db_connections_active = Gauge(
 'flowmind_db_connections_active',
 'Number of active database connections',
 ['database']
)

# ============================================================================
# System Metrics
# ============================================================================

system_info = Info(
 'flowmind_system',
 'FlowMind system information'
)

uptime_seconds = Gauge(
 'flowmind_uptime_seconds',
 'Application uptime in seconds'
)

# ============================================================================
# Decorators for Easy Instrumentation
# ============================================================================

def track_endpoint_metrics(endpoint_name: str):
 """
 Decorator to automatically track API endpoint metrics
 
 Usage:
 @router.get("/api/data")
 @track_endpoint_metrics("/api/data")
 async def get_data():
 return {"data": "example"}
 """
 def decorator(func: Callable) -> Callable:
 is_async = asyncio.iscoroutinefunction(func)
 
 if is_async:
 @wraps(func)
 async def async_wrapper(*args, **kwargs):
 start_time = time.time()
 status = "success"
 
 try:
 result = await func(*args, **kwargs)
 return result
 except Exception as e:
 status = "error"
 raise
 finally:
 duration = time.time() - start_time
 
 # Record metrics
 api_requests_total.labels(
 endpoint=endpoint_name,
 method="GET", # Could be extracted from request
 status=status
 ).inc()
 
 api_request_duration_seconds.labels(
 endpoint=endpoint_name,
 method="GET"
 ).observe(duration)
 
 logger.debug(
 f" Metrics: {endpoint_name} - {duration:.3f}s - {status}"
 )
 
 return async_wrapper
 else:
 @wraps(func)
 def sync_wrapper(*args, **kwargs):
 start_time = time.time()
 status = "success"
 
 try:
 result = func(*args, **kwargs)
 return result
 except Exception as e:
 status = "error"
 raise
 finally:
 duration = time.time() - start_time
 
 api_requests_total.labels(
 endpoint=endpoint_name,
 method="GET",
 status=status
 ).inc()
 
 api_request_duration_seconds.labels(
 endpoint=endpoint_name,
 method="GET"
 ).observe(duration)
 
 return sync_wrapper
 
 return decorator

def track_external_api(provider: str, endpoint: str):
 """
 Decorator to track external API calls
 
 Usage:
 @track_external_api("TradeStation", "options_chain")
 async def get_ts_chain(symbol: str):
 return await ts_client.get_chain(symbol)
 """
 def decorator(func: Callable) -> Callable:
 is_async = asyncio.iscoroutinefunction(func)
 
 if is_async:
 @wraps(func)
 async def async_wrapper(*args, **kwargs):
 start_time = time.time()
 status = "success"
 
 try:
 result = await func(*args, **kwargs)
 return result
 except Exception as e:
 status = "error"
 external_api_errors_total.labels(
 provider=provider,
 error_type=type(e).__name__
 ).inc()
 raise
 finally:
 duration = time.time() - start_time
 
 external_api_requests_total.labels(
 provider=provider,
 endpoint=endpoint,
 status=status
 ).inc()
 
 external_api_duration_seconds.labels(
 provider=provider,
 endpoint=endpoint
 ).observe(duration)
 
 return async_wrapper
 else:
 @wraps(func)
 def sync_wrapper(*args, **kwargs):
 start_time = time.time()
 status = "success"
 
 try:
 result = func(*args, **kwargs)
 return result
 except Exception as e:
 status = "error"
 external_api_errors_total.labels(
 provider=provider,
 error_type=type(e).__name__
 ).inc()
 raise
 finally:
 duration = time.time() - start_time
 
 external_api_requests_total.labels(
 provider=provider,
 endpoint=endpoint,
 status=status
 ).inc()
 
 external_api_duration_seconds.labels(
 provider=provider,
 endpoint=endpoint
 ).observe(duration)
 
 return sync_wrapper
 
 return decorator

# ============================================================================
# Metrics Collection Functions
# ============================================================================

async def collect_cache_metrics():
 """Collect current cache metrics"""
 try:
 from redis_fallback import get_kv
 
 kv = await get_kv()
 cache_type = type(kv).__name__
 
 # For AsyncTTLDict, we can count keys
 if hasattr(kv, '__len__'):
 cache_entries.labels(cache_type=cache_type).set(len(kv))
 
 logger.debug(f" Collected cache metrics for {cache_type}")
 
 except Exception as e:
 logger.warning(f" Failed to collect cache metrics: {e}")

async def collect_portfolio_metrics():
 """Collect portfolio metrics"""
 try:
 # Import here to avoid circular dependencies
 from mindfolio import list_portfolios
 
 portfolios = await list_portfolios()
 portfolios_active.set(len(portfolios))
 
 logger.debug(f" Collected portfolio metrics: {len(portfolios)} active")
 
 except Exception as e:
 logger.warning(f" Failed to collect portfolio metrics: {e}")

def export_metrics() -> tuple[bytes, str]:
 """
 Export metrics in Prometheus format
 
 Returns:
 Tuple of (metrics_data, content_type)
 """
 return generate_latest(), CONTENT_TYPE_LATEST

# ============================================================================
# Initialization
# ============================================================================

def initialize_metrics():
 """Initialize system metrics at startup"""
 import os
 import platform
 
 system_info.info({
 'version': os.getenv('APP_VERSION', '1.0.0'),
 'environment': os.getenv('ENVIRONMENT', 'development'),
 'python_version': platform.python_version(),
 'platform': platform.system()
 })
 
 logger.info(" Prometheus metrics initialized")

# Example usage
if __name__ == "__main__":
 # Test metrics
 initialize_metrics()
 
 # Simulate some metrics
 api_requests_total.labels(
 endpoint="/api/builder/price",
 method="POST",
 status="success"
 ).inc()
 
 api_request_duration_seconds.labels(
 endpoint="/api/builder/price",
 method="POST"
 ).observe(0.254)
 
 strategies_priced_total.labels(
 strategy_type="iron_condor",
 symbol="TSLA"
 ).inc()
 
 # Export metrics
 metrics_data, content_type = export_metrics()
 print(f"\nMetrics ({content_type}):")
 print(metrics_data.decode('utf-8')[:1000]) # First 1000 chars
 print("...")
