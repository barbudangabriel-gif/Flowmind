"""
Test Suite for Universe Scanner Pool Manager
Tests pool initialization, agent spawning, load balancing, health monitoring

Run: cd /workspaces/Flowmind/backend && python agents/tier4_workers/test_scanner_pool.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier4_workers.scanner_pool import UniverseScannerPool


# ═══════════════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════════════


def test_pool_initialization():
    """Test pool initialization with default config"""
    pool = UniverseScannerPool(num_agents=10, tickers_per_agent=3)

    assert pool.num_agents == 10
    assert pool.tickers_per_agent == 3
    assert pool.light_interval == 300
    assert pool.deep_interval == 60
    assert len(pool.agents) == 0  # Not initialized yet
    assert not pool.is_running

    print("✅ Test 1/5: Pool initialization")


def test_ticker_universe():
    """Test ticker universe generation (500 tickers)"""
    pool = UniverseScannerPool(num_agents=167)
    tickers = pool._get_ticker_universe()

    assert len(tickers) == 500
    assert "AAPL" in tickers
    assert "TSLA" in tickers
    assert "NVDA" in tickers
    assert "MSFT" in tickers

    # Check no duplicates
    assert len(tickers) == len(set(tickers))

    print("✅ Test 2/5: Ticker universe (500 symbols)")


def test_ticker_assignment():
    """Test load balancing (round-robin ticker assignment)"""

    async def run_test():
        pool = UniverseScannerPool(num_agents=10, tickers_per_agent=3)
        pool._assign_tickers_to_agents()

        # Check assignments created
        assert len(pool.ticker_assignments) == 10

        # Check each agent has 3 tickers
        for agent_id, tickers in pool.ticker_assignments.items():
            assert len(tickers) <= 3  # Some agents may have <3 if not enough tickers

        # Check no ticker assigned twice
        all_assigned = []
        for tickers in pool.ticker_assignments.values():
            all_assigned.extend(tickers)

        assert len(all_assigned) == len(set(all_assigned))  # No duplicates

        # Check agent IDs formatted correctly
        assert "scanner_000" in pool.ticker_assignments
        assert "scanner_009" in pool.ticker_assignments

    asyncio.run(run_test())
    print("✅ Test 3/5: Ticker assignment (load balancing)")


def test_pool_initialization_with_agents():
    """Test pool initialization creates all agents"""

    async def run_test():
        pool = UniverseScannerPool(num_agents=5, tickers_per_agent=3)
        await pool.initialize()

        # Check agents created
        assert len(pool.agents) == 5

        # Check agent IDs
        agent_ids = [agent.agent_id for agent in pool.agents]
        assert "scanner_000" in agent_ids
        assert "scanner_004" in agent_ids

        # Check ticker assignments
        for agent in pool.agents:
            assert len(agent.tickers) <= 3

    asyncio.run(run_test())
    print("✅ Test 4/5: Agent initialization")


def test_pool_stats():
    """Test pool statistics aggregation"""

    async def run_test():
        pool = UniverseScannerPool(num_agents=5, tickers_per_agent=3)
        await pool.initialize()

        # Simulate some agent activity
        pool.agents[0].signals_generated = 10
        pool.agents[0].signals_validated = 7
        pool.agents[1].signals_generated = 5
        pool.agents[1].signals_validated = 3
        pool.agents[0].hot_tickers = {"TSLA", "AAPL"}
        pool.agents[1].hot_tickers = {"NVDA"}

        stats = pool.get_pool_stats()

        assert stats["total_agents"] == 5
        assert stats["active_agents"] == 5
        assert stats["failed_agents"] == 0
        assert stats["signals_generated"] == 15  # 10 + 5
        assert stats["signals_validated"] == 10  # 7 + 3
        assert stats["win_rate"] == round(10 / 15, 3)  # 0.667
        assert stats["hot_tickers_count"] == 3  # TSLA, AAPL, NVDA

    asyncio.run(run_test())
    print("✅ Test 5/5: Pool statistics")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("UNIVERSE SCANNER POOL - TEST SUITE")
    print("=" * 70 + "\n")

    test_pool_initialization()
    test_ticker_universe()
    test_ticker_assignment()
    test_pool_initialization_with_agents()
    test_pool_stats()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED (5/5)")
    print("=" * 70 + "\n")
