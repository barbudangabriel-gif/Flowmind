"""
Cache Decorators for FlowMind API
Provides response caching functionality using Redis with fallback support
"""

import json
import hashlib
import inspect
from functools import wraps
from typing import Any, Callable, Optional, Union
import logging

from redis_fallback import get_kv

logger = logging.getLogger(__name__)


def _generate_cache_key(
    prefix: str,
    func_name: str,
    args: tuple,
    kwargs: dict
) -> str:
    """
    Generate unique cache key from function signature
    
    Args:
        prefix: Cache key prefix (e.g., "chain", "flow")
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
    
    Returns:
        Cache key string like "chain:get_options_chain:abc123"
    """
    # Create stable hash from args + kwargs
    cache_data = {
        'args': [str(arg) for arg in args],
        'kwargs': {k: str(v) for k, v in sorted(kwargs.items())}
    }
    
    data_str = json.dumps(cache_data, sort_keys=True)
    key_hash = hashlib.md5(data_str.encode()).hexdigest()[:12]
    
    return f"{prefix}:{func_name}:{key_hash}"


def cached_response(
    ttl: int = 60,
    key_prefix: str = "api",
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching API responses in Redis (with fallback)
    
    Usage:
        @cached_response(ttl=60, key_prefix="chain")
        async def get_options_chain(symbol: str, expiry: str):
            # ... expensive API call
            return data
    
    Args:
        ttl: Cache time-to-live in seconds (default: 60)
        key_prefix: Prefix for cache keys (default: "api")
        key_builder: Optional custom function to generate cache key
                    Signature: (func_name, args, kwargs) -> str
    
    Features:
        - Automatic cache key generation from function args
        - Redis fallback to in-memory AsyncTTLDict
        - JSON serialization/deserialization
        - Cache hit/miss logging
        - Graceful error handling (cache failures don't break API)
    
    Example:
        # Cache options chain for 60 seconds
        @cached_response(ttl=60, key_prefix="chain")
        async def get_chain(symbol: str):
            return await expensive_api_call(symbol)
        
        # Custom cache key
        def my_key_builder(func_name, args, kwargs):
            return f"custom:{kwargs['symbol']}"
        
        @cached_response(ttl=120, key_builder=my_key_builder)
        async def get_custom(symbol: str):
            return data
    """
    def decorator(func: Callable) -> Callable:
        # Determine if function is async
        is_async = inspect.iscoroutinefunction(func)
        
        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                if key_builder:
                    cache_key = key_builder(func.__name__, args, kwargs)
                else:
                    cache_key = _generate_cache_key(
                        key_prefix,
                        func.__name__,
                        args,
                        kwargs
                    )
                
                try:
                    # Get KV store (Redis or fallback)
                    kv = await get_kv()
                    
                    # Try to get from cache
                    cached_value = await kv.get(cache_key)
                    
                    if cached_value:
                        logger.debug(f"✅ Cache HIT: {cache_key}")
                        try:
                            return json.loads(cached_value)
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Invalid JSON in cache for {cache_key}, refreshing")
                    else:
                        logger.debug(f"❌ Cache MISS: {cache_key}")
                    
                    # Cache miss - execute function
                    result = await func(*args, **kwargs)
                    
                    # Store in cache
                    try:
                        serialized = json.dumps(result)
                        await kv.set(cache_key, serialized, ex=ttl)
                        logger.debug(f"💾 Cached: {cache_key} (TTL: {ttl}s)")
                    except (TypeError, json.JSONEncodeError) as e:
                        logger.warning(f"⚠️ Cannot cache result for {cache_key}: {e}")
                    
                    return result
                    
                except Exception as e:
                    # Cache errors should not break API
                    logger.error(f"❌ Cache error for {cache_key}: {e}")
                    logger.info("⚠️ Executing function without cache")
                    return await func(*args, **kwargs)
            
            return async_wrapper
        
        else:
            # Sync function wrapper
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                # For sync functions, we can't use async get_kv()
                # This is a limitation - sync functions need different handling
                logger.warning(
                    f"⚠️ cached_response decorator used on sync function {func.__name__}. "
                    "Caching disabled for sync functions."
                )
                return func(*args, **kwargs)
            
            return sync_wrapper
    
    return decorator


def invalidate_cache(
    key_prefix: str,
    func_name: Optional[str] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None
):
    """
    Manually invalidate cache entries
    
    Usage:
        # Invalidate all "chain" entries
        await invalidate_cache("chain")
        
        # Invalidate specific function cache
        await invalidate_cache("chain", func_name="get_options_chain")
        
        # Invalidate specific call
        await invalidate_cache(
            "chain",
            func_name="get_options_chain",
            args=("TSLA",),
            kwargs={"expiry": "2025-11-15"}
        )
    
    Args:
        key_prefix: Cache key prefix to invalidate
        func_name: Optional specific function name
        args: Optional function arguments
        kwargs: Optional function keyword arguments
    
    Returns:
        Number of keys invalidated
    """
    async def _invalidate():
        try:
            kv = await get_kv()
            
            if args is not None and kwargs is not None and func_name:
                # Invalidate specific cache entry
                cache_key = _generate_cache_key(
                    key_prefix,
                    func_name,
                    args,
                    kwargs
                )
                deleted = await kv.delete(cache_key)
                logger.info(f"🗑️ Invalidated cache: {cache_key}")
                return deleted
            else:
                # Invalidate pattern (requires Redis SCAN)
                pattern = f"{key_prefix}:{func_name}:*" if func_name else f"{key_prefix}:*"
                
                # This is simplified - full implementation would use SCAN
                logger.warning(
                    f"⚠️ Pattern-based cache invalidation not fully implemented. "
                    f"Pattern: {pattern}"
                )
                return 0
                
        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e}")
            return 0
    
    return _invalidate()


# Convenience decorators for common endpoints

def cache_chain(ttl: int = 60):
    """Cache options chain data"""
    return cached_response(ttl=ttl, key_prefix="chain")


def cache_flow(ttl: int = 30):
    """Cache flow data (shorter TTL for real-time data)"""
    return cached_response(ttl=ttl, key_prefix="flow")


def cache_builder(ttl: int = 300):
    """Cache builder pricing results"""
    return cached_response(ttl=ttl, key_prefix="builder")


def cache_backtest(ttl: int = 3600):
    """Cache backtest results (longer TTL for historical data)"""
    return cached_response(ttl=ttl, key_prefix="backtest")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    @cached_response(ttl=10, key_prefix="test")
    async def example_api_call(symbol: str, param: int = 1):
        print(f"Executing expensive API call for {symbol}, param={param}")
        await asyncio.sleep(0.5)  # Simulate delay
        return {"symbol": symbol, "data": [1, 2, 3], "param": param}
    
    async def test_cache():
        print("Test 1: First call (cache MISS)")
        result1 = await example_api_call("TSLA", param=1)
        print(f"Result: {result1}\n")
        
        print("Test 2: Second call with same args (cache HIT)")
        result2 = await example_api_call("TSLA", param=1)
        print(f"Result: {result2}\n")
        
        print("Test 3: Different args (cache MISS)")
        result3 = await example_api_call("AAPL", param=2)
        print(f"Result: {result3}\n")
        
        print("Test 4: Wait for TTL expiry (11 seconds)")
        await asyncio.sleep(11)
        result4 = await example_api_call("TSLA", param=1)
        print(f"Result: {result4}\n")
    
    asyncio.run(test_cache())
