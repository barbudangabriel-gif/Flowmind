"""
Cache Warmup Service for FlowMind

Pre-populates cache with frequently accessed data at startup
Reduces first-request latency for popular symbols
"""

import asyncio
import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

# Popular symbols to warm up (ordered by typical volume)
DEFAULT_WARMUP_SYMBOLS = [
    "SPY",  # S&P 500 ETF (most traded)
    "QQQ",  # Nasdaq ETF
    "TSLA",  # Tesla
    "AAPL",  # Apple
    "NVDA",  # Nvidia
    "MSFT",  # Microsoft
    "AMD",  # AMD
    "AMZN",  # Amazon
    "META",  # Meta
    "GOOGL",  # Google
]


async def warmup_options_chain(symbol: str) -> bool:
    """
    Warm up options chain cache for a symbol

    Args:
        symbol: Stock ticker symbol

    Returns:
        True if successful, False otherwise
    """
    try:
        # Import here to avoid circular dependencies
        from services.options_gex import fetch_chain

        logger.debug(f" Warming up options chain for {symbol}...")

        # Fetch chain (will be cached automatically)
        result = fetch_chain(None, symbol.upper())

        if result and result.get("raw"):
            logger.info(f" Warmed up {symbol} options chain")
            return True
        else:
            logger.warning(f" No data for {symbol}")
            return False

    except Exception as e:
        logger.warning(f" Warmup failed for {symbol}: {e}")
        return False


async def warmup_spot_prices(symbols: List[str]) -> int:
    """
    Warm up spot price cache for multiple symbols

    Args:
        symbols: List of ticker symbols

    Returns:
        Number of successful warmups
    """
    success_count = 0

    try:
        from services.providers import get_provider

        provider = get_provider()

        for symbol in symbols:
            try:
                logger.debug(f" Warming up spot price for {symbol}...")

                if hasattr(provider, "get_quote"):
                    quote = provider.get_quote(symbol.upper())
                    if quote:
                        success_count += 1
                        logger.info(f" Warmed up {symbol} spot price")
                else:
                    logger.debug(f" Provider doesn't support get_quote")

            except Exception as e:
                logger.warning(f" Spot price warmup failed for {symbol}: {e}")

    except Exception as e:
        logger.error(f" Spot price warmup error: {e}")

    return success_count


async def warmup_flow_data(limit: int = 10) -> bool:
    """
    Warm up options flow summary cache

    Args:
        limit: Number of flow items to fetch

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.debug(" Warming up flow data...")

        # Import here to avoid circular dependencies
        from services.uw_flow import summary_from_live

        # Fetch flow summary (will be cached automatically)
        result = await summary_from_live(limit=limit, min_premium=25000)

        if result and result.get("items"):
            logger.info(f" Warmed up flow data ({len(result['items'])} items)")
            return True
        else:
            logger.warning(" No flow data returned")
            return False

    except Exception as e:
        logger.warning(f" Flow warmup failed: {e}")
        return False


async def warmup_single_symbol(symbol: str) -> dict:
    """
    Warm up all data for a single symbol

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with success flags for each data type
    """
    result = {"symbol": symbol, "chain": False, "spot": False}

    # Warm up options chain
    result["chain"] = await warmup_options_chain(symbol)

    # Small delay to avoid rate limits
    await asyncio.sleep(0.5)

    return result


async def warmup_cache(
    symbols: Optional[List[str]] = None,
    include_flow: bool = True,
    parallel: bool = True,
) -> dict:
    """
    Main warmup function - pre-populates cache at startup

    Args:
        symbols: List of symbols to warm up (default: DEFAULT_WARMUP_SYMBOLS)
        include_flow: Whether to warm up flow data (default: True)
        parallel: Run warmups in parallel (faster but more load)

    Returns:
        Dict with warmup statistics
    """
    if symbols is None:
        symbols = DEFAULT_WARMUP_SYMBOLS

    logger.info("=" * 60)
    logger.info(" Starting cache warmup...")
    logger.info(f" Symbols: {', '.join(symbols)}")
    logger.info(f" Include flow: {include_flow}")
    logger.info(f" Parallel: {parallel}")
    logger.info("=" * 60)

    start_time = asyncio.get_event_loop().time()
    stats = {
        "symbols_processed": 0,
        "chains_warmed": 0,
        "flow_warmed": False,
        "duration_seconds": 0,
        "errors": [],
    }

    try:
        if parallel:
            # Run all warmups in parallel
            tasks = []

            # Add symbol warmup tasks
            for symbol in symbols:
                tasks.append(warmup_single_symbol(symbol))

            # Add flow warmup task
            if include_flow:
                tasks.append(warmup_flow_data())

            # Execute in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, dict):
                    if "symbol" in result:
                        # Symbol warmup result
                        stats["symbols_processed"] += 1
                        if result.get("chain"):
                            stats["chains_warmed"] += 1
                elif isinstance(result, bool):
                    # Flow warmup result
                    stats["flow_warmed"] = result
                elif isinstance(result, Exception):
                    stats["errors"].append(str(result))
        else:
            # Sequential warmup (safer for rate limits)
            for symbol in symbols:
                result = await warmup_single_symbol(symbol)
                stats["symbols_processed"] += 1
                if result.get("chain"):
                    stats["chains_warmed"] += 1

                # Rate limit delay
                await asyncio.sleep(1.0)

            # Warm up flow data
            if include_flow:
                stats["flow_warmed"] = await warmup_flow_data()

    except Exception as e:
        logger.error(f" Cache warmup error: {e}")
        stats["errors"].append(str(e))

    finally:
        end_time = asyncio.get_event_loop().time()
        stats["duration_seconds"] = round(end_time - start_time, 2)

        # Log summary
        logger.info("")
        logger.info("=" * 60)
        logger.info(" Cache warmup completed!")
        logger.info(f" Symbols processed: {stats['symbols_processed']}/{len(symbols)}")
        logger.info(f" Chains warmed: {stats['chains_warmed']}")
        logger.info(f" Flow warmed: {stats['flow_warmed']}")
        logger.info(f" Duration: {stats['duration_seconds']}s")
        if stats["errors"]:
            logger.warning(f" Errors: {len(stats['errors'])}")
        logger.info("=" * 60)
        logger.info("")

    return stats


async def scheduled_warmup(interval_minutes: int = 30):
    """
    Run warmup on a schedule (for keeping cache fresh)

    Args:
        interval_minutes: How often to run warmup
    """
    while True:
        try:
            logger.info(f"🔄 Scheduled warmup starting (interval: {interval_minutes}m)")
            await warmup_cache(parallel=True)

        except Exception as e:
            logger.error(f" Scheduled warmup error: {e}")

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


def get_warmup_config():
    """
    Get warmup configuration from environment variables

    Returns:
        Dict with warmup settings
    """
    return {
        "enabled": os.getenv("WARMUP_ENABLED", "1") == "1",
        "symbols": os.getenv("WARMUP_SYMBOLS", ",".join(DEFAULT_WARMUP_SYMBOLS)).split(
            ","
        ),
        "include_flow": os.getenv("WARMUP_INCLUDE_FLOW", "1") == "1",
        "parallel": os.getenv("WARMUP_PARALLEL", "1") == "1",
        "scheduled": os.getenv("WARMUP_SCHEDULED", "0") == "1",
        "schedule_interval": int(os.getenv("WARMUP_INTERVAL_MINUTES", "30")),
    }


# Example usage
if __name__ == "__main__":

    async def test_warmup():
        # Test with small subset
        stats = await warmup_cache(
            symbols=["SPY", "TSLA"], include_flow=True, parallel=False
        )
        print(f"\nWarmup stats: {stats}")

    asyncio.run(test_warmup())
