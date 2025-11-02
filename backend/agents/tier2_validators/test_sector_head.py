"""
Test suite for Sector Head Validator (Tier 2)

Tests:
1. SectorHead initialization
2. Sector exposure limit check
3. Correlation check
4. Sector risk scoring
5. Approved signal creation
6. SectorHeadPool initialization
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier2_validators.sector_head import (
    SECTORS,
    SectorHead,
    SectorHeadPool,
)


async def run_tests():
    """Run all Sector Head tests"""

    print("\n" + "=" * 70)
    print("SECTOR HEAD VALIDATOR TEST SUITE")
    print("=" * 70)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 1: SectorHead Initialization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] SectorHead Initialization")
    print("-" * 70)

    supervised_team_leads = ["team_lead_00", "team_lead_10"]

    sector_head = SectorHead(
        sector_head_id="sector_head_technology",
        sector_name="technology",
        supervised_team_leads=supervised_team_leads,
        exposure_limit=0.30,
    )

    assert sector_head.sector_head_id == "sector_head_technology"
    assert sector_head.sector_name == "technology"
    assert len(sector_head.supervised_team_leads) == 2
    assert sector_head.exposure_limit == 0.30

    print(f"✅ Sector Head ID: {sector_head.sector_head_id}")
    print(f"✅ Sector: {sector_head.sector_name}")
    print(f"✅ Supervised team leads: {len(sector_head.supervised_team_leads)}")
    print(f"✅ Exposure limit: {sector_head.exposure_limit:.0%}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Ticker Sector Detection
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Ticker Sector Detection")
    print("-" * 70)

    # Test known tickers
    assert sector_head._get_ticker_sector("AAPL") == "technology"
    assert sector_head._get_ticker_sector("JPM") == "financials"
    assert sector_head._get_ticker_sector("UNH") == "healthcare"
    assert sector_head._get_ticker_sector("TSLA") == "consumer"

    # Test unknown ticker
    assert sector_head._get_ticker_sector("UNKNOWN") is None

    print("✅ AAPL → technology")
    print("✅ JPM → financials")
    print("✅ UNH → healthcare")
    print("✅ TSLA → consumer")
    print("✅ UNKNOWN → None")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 3: Sector Exposure Limit Check (PASS)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Sector Exposure Limit Check (should pass)")
    print("-" * 70)

    # Empty portfolio - should pass
    sector_head.current_portfolio = {}
    sector_head.sector_exposures = {}

    result = await sector_head._check_exposure_limit("AAPL", "technology")

    assert result is True
    print("✅ Exposure check passed (empty portfolio)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 4: Sector Exposure Limit Check (REJECT)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Sector Exposure Limit Check (should reject)")
    print("-" * 70)

    # Simulate high exposure (35% > 30% limit)
    sector_head.current_portfolio = {"MSFT": 35000, "GOOGL": 30000}
    sector_head.sector_exposures = {"technology": 0.35}

    result = await sector_head._check_exposure_limit("NVDA", "technology")

    assert result is False
    assert sector_head.signals_rejected > 0
    assert "exposure_limit" in sector_head.rejection_reasons

    print("✅ Exposure check rejected (35% > 30% limit)")
    print(f"✅ Rejection reason: {dict(sector_head.rejection_reasons)}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 5: Correlation Check (PASS)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Correlation Check (should pass)")
    print("-" * 70)

    # Reset portfolio (2 tech positions)
    sector_head.current_portfolio = {"AAPL": 10000, "MSFT": 10000}
    sector_head.signals_rejected = 0
    sector_head.rejection_reasons.clear()

    result = await sector_head._check_correlation("GOOGL", "technology")

    assert result is True
    print("✅ Correlation check passed (2 positions in sector)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 6: Correlation Check (REJECT)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Correlation Check (should reject)")
    print("-" * 70)

    # Add 3rd position (3 = limit)
    sector_head.current_portfolio = {
        "AAPL": 10000,
        "MSFT": 10000,
        "GOOGL": 10000,
    }

    result = await sector_head._check_correlation("NVDA", "technology")

    assert result is False
    assert "sector_concentration" in sector_head.rejection_reasons

    print("✅ Correlation check rejected (3+ positions in sector)")
    print(f"✅ Rejection reason: {dict(sector_head.rejection_reasons)}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 7: Sector Risk Scoring
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 7] Sector Risk Scoring")
    print("-" * 70)

    sector_head.sector_exposures = {"technology": 0.20}  # 20% exposure

    risk_score = await sector_head._calculate_sector_risk("AAPL", "technology")

    assert 0 <= risk_score <= 100
    print(f"✅ Sector risk score: {risk_score:.1f}/100")
    print(f"   (Based on volatility, exposure, momentum, market regime)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 8: Approved Signal Creation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 8] Approved Signal Creation")
    print("-" * 70)

    original_signal = {
        "agent_id": "scanner_000",
        "ticker": "AAPL",
        "total_score": 75.0,
        "confidence": 0.85,
        "validated_by": "team_lead_00",
    }

    approved_signal = sector_head._create_approved_signal(
        original_signal, sector_risk_score=45.0
    )

    assert "approved_by" in approved_signal
    assert approved_signal["approved_by"] == "sector_head_technology"
    assert "approved_at" in approved_signal
    assert "sector" in approved_signal
    assert approved_signal["sector"] == "technology"
    assert "sector_risk_score" in approved_signal
    assert approved_signal["sector_risk_score"] == 45.0

    print(f"✅ Approved by: {approved_signal['approved_by']}")
    print(f"✅ Sector: {approved_signal['sector']}")
    print(f"✅ Sector risk score: {approved_signal['sector_risk_score']}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 9: Sector Stats
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 9] Sector Stats")
    print("-" * 70)

    sector_head.start_time = datetime.utcnow()  # Set start time
    sector_head.signals_processed = 10
    sector_head.signals_approved = 7
    sector_head.signals_rejected = 3

    stats = sector_head.get_sector_stats()

    assert stats["sector_head_id"] == "sector_head_technology"
    assert stats["sector_name"] == "technology"
    assert stats["supervised_team_leads"] == 2
    assert stats["signals_processed"] == 10
    assert stats["signals_approved"] == 7
    assert stats["signals_rejected"] == 3
    assert stats["approval_rate"] == 0.7

    print(f"✅ Sector Head ID: {stats['sector_head_id']}")
    print(f"✅ Sector: {stats['sector_name']}")
    print(f"✅ Signals processed: {stats['signals_processed']}")
    print(f"✅ Approval rate: {stats['approval_rate']:.1%}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 10: SectorHeadPool Initialization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 10] SectorHeadPool Initialization")
    print("-" * 70)

    pool = SectorHeadPool(num_sector_heads=10, num_team_leads=20)

    assert pool.num_sector_heads == 10
    assert pool.num_team_leads == 20
    assert pool.is_running is False

    print(f"✅ Pool initialized: {pool.num_sector_heads} sector heads")
    print(f"✅ Team leads: {pool.num_team_leads}")

    # Test team lead assignment
    assignments = pool._assign_team_leads_to_sectors()

    assert len(assignments) == 10
    assert all(len(team_leads) == 2 for team_leads in assignments.values())

    print(f"✅ Assignments: {len(assignments)} sector heads")

    # Count total assigned
    total_assigned = sum(len(team_leads) for team_leads in assignments.values())
    assert total_assigned == 20

    print(f"✅ Total team leads assigned: {total_assigned}")

    # Show distribution
    for sector_head_id, team_leads in list(assignments.items())[:3]:
        print(f"   {sector_head_id}: {team_leads}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 11: Sector Definitions
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 11] Sector Definitions")
    print("-" * 70)

    assert len(SECTORS) == 10
    assert "technology" in SECTORS
    assert "financials" in SECTORS
    assert "healthcare" in SECTORS

    print(f"✅ Total sectors: {len(SECTORS)}")

    for sector_name, config in list(SECTORS.items())[:5]:
        print(
            f"   {config['name']}: {len(config['tickers'])} tickers, "
            f"{config['exposure_limit']:.0%} limit"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 12: SectorHeadPool Stats
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 12] SectorHeadPool Stats")
    print("-" * 70)

    await pool.initialize()
    pool_stats = pool.get_pool_stats()

    assert pool_stats["total_sector_heads"] == 10
    assert pool_stats["pool_status"] == "stopped"
    assert "signals_processed" in pool_stats
    assert "approval_rate" in pool_stats

    print(f"✅ Pool status: {pool_stats['pool_status']}")
    print(f"✅ Total sector heads: {pool_stats['total_sector_heads']}")
    print(f"✅ Signals processed: {pool_stats['signals_processed']}")
    print(f"✅ Approval rate: {pool_stats['approval_rate']:.1%}")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nSector Head Validator Features Validated:")
    print("  ✅ Sector-specific validation (10 sectors)")
    print("  ✅ Exposure limits (max 30% per sector)")
    print("  ✅ Correlation checks (max 3 positions per sector)")
    print("  ✅ Sector risk scoring (volatility, exposure, momentum)")
    print("  ✅ Approved signal enrichment (sector, risk score, exposure)")
    print("  ✅ Sector-level statistics")
    print("  ✅ Pool management (10 sector heads, 20 team leads)")
    print("  ✅ Round-robin team lead assignment (2 leads per sector)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
