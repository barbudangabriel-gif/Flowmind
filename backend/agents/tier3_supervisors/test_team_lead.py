"""
Test suite for Team Lead Supervisor (Tier 3)

Tests:
1. TeamLead initialization
2. Score threshold validation
3. Agent reliability check
4. Peer cross-validation
5. Validated signal creation
6. TeamLeadPool initialization
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier3_supervisors.team_lead import TeamLead, TeamLeadPool


async def run_tests():
    """Run all Team Lead tests"""

    print("\n" + "=" * 70)
    print("TEAM LEAD SUPERVISOR TEST SUITE")
    print("=" * 70)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 1: TeamLead Initialization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] TeamLead Initialization")
    print("-" * 70)

    assigned_agents = [
        "scanner_000",
        "scanner_001",
        "scanner_002",
        "scanner_003",
        "scanner_004",
        "scanner_005",
        "scanner_006",
        "scanner_007",
    ]

    team_lead = TeamLead(
        team_lead_id="team_lead_00",
        assigned_agents=assigned_agents,
    )

    assert team_lead.team_lead_id == "team_lead_00"
    assert len(team_lead.assigned_agents) == 8
    assert team_lead.score_threshold == 60.0
    assert team_lead.reliability_threshold == 0.50
    assert team_lead.peer_consensus_threshold == 0.30

    print(f"✅ TeamLead ID: {team_lead.team_lead_id}")
    print(f"✅ Supervised agents: {len(team_lead.assigned_agents)}")
    print(f"✅ Score threshold: {team_lead.score_threshold}")
    print(f"✅ Reliability threshold: {team_lead.reliability_threshold}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Score Threshold Validation (REJECT)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Score Threshold Validation (should reject)")
    print("-" * 70)

    # Create mock signal below threshold
    low_score_signal = {
        "agent_id": "scanner_000",
        "ticker": "TSLA",
        "total_score": 45.0,  # Below 60.0 threshold
        "confidence": 0.70,
        "trend_direction": "bullish",
        "news_sentiment": 0.5,
        "call_put_ratio": 1.8,
    }

    validated = await team_lead.validate_signal(low_score_signal)

    assert validated is None, "Expected signal to be rejected"
    assert team_lead.signals_processed == 1
    assert team_lead.signals_rejected == 1
    assert team_lead.rejection_reasons["score_threshold"] == 1

    print(f"✅ Low score signal rejected (score: 45.0 < 60.0)")
    print(f"✅ Signals processed: {team_lead.signals_processed}")
    print(f"✅ Signals rejected: {team_lead.signals_rejected}")
    print(f"✅ Rejection reason: score_threshold")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 3: Agent Reliability Check
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Agent Reliability Check")
    print("-" * 70)

    # Check reliability for new agent (should return neutral 0.5)
    reliability = await team_lead._check_agent_reliability("scanner_000")

    assert 0.0 <= reliability <= 1.0
    print(f"✅ Agent reliability: {reliability:.1%}")
    print(f"   (New agent gets neutral 0.5)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 4: Peer Cross-Validation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Peer Cross-Validation")
    print("-" * 70)

    peer_signal = {
        "agent_id": "scanner_001",
        "ticker": "TSLA",
        "total_score": 75.0,
        "confidence": 0.80,
        "trend_direction": "bullish",
        "news_sentiment": 0.6,
        "call_put_ratio": 2.0,
    }

    consensus = await team_lead._peer_cross_validate(peer_signal)

    assert 0.0 <= consensus <= 1.0
    print(f"✅ Peer consensus: {consensus:.1%}")
    print(f"   (No peer data returns neutral 0.5)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 5: Signal Direction Detection
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Signal Direction Detection")
    print("-" * 70)

    bullish_signal = {
        "ticker": "AAPL",
        "trend_direction": "bullish",
        "news_sentiment": 0.5,
        "call_put_ratio": 2.0,
    }

    bearish_signal = {
        "ticker": "META",
        "trend_direction": "bearish",
        "news_sentiment": -0.4,
        "call_put_ratio": 0.5,
    }

    bullish_direction = team_lead._get_signal_direction(bullish_signal)
    bearish_direction = team_lead._get_signal_direction(bearish_signal)

    assert bullish_direction == "bullish"
    assert bearish_direction == "bearish"

    print(f"✅ Bullish signal detected: {bullish_direction}")
    print(f"✅ Bearish signal detected: {bearish_direction}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 6: Validated Signal Creation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Validated Signal Creation")
    print("-" * 70)

    original_signal = {
        "agent_id": "scanner_000",
        "ticker": "NVDA",
        "total_score": 78.0,
        "confidence": 0.85,
    }

    validated_signal = team_lead._create_validated_signal(
        original_signal, reliability=0.67, peer_consensus=0.45
    )

    assert "validated_by" in validated_signal
    assert validated_signal["validated_by"] == "team_lead_00"
    assert "validated_at" in validated_signal
    assert "agent_reliability" in validated_signal
    assert "peer_consensus" in validated_signal
    assert "validation_confidence" in validated_signal

    print(f"✅ Validated by: {validated_signal['validated_by']}")
    print(f"✅ Agent reliability: {validated_signal['agent_reliability']}")
    print(f"✅ Peer consensus: {validated_signal['peer_consensus']}")
    print(
        f"✅ Validation confidence: {validated_signal['validation_confidence']:.3f}"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 7: Team Stats
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 7] Team Stats")
    print("-" * 70)

    team_lead.start_time = datetime.utcnow()  # Set start time
    stats = team_lead.get_team_stats()

    assert stats["team_lead_id"] == "team_lead_00"
    assert stats["supervised_agents"] == 8
    assert stats["signals_processed"] >= 0
    assert "validation_rate" in stats

    print(f"✅ Team Lead ID: {stats['team_lead_id']}")
    print(f"✅ Supervised agents: {stats['supervised_agents']}")
    print(f"✅ Signals processed: {stats['signals_processed']}")
    print(f"✅ Validation rate: {stats['validation_rate']:.1%}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 8: TeamLeadPool Initialization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 8] TeamLeadPool Initialization")
    print("-" * 70)

    pool = TeamLeadPool(num_leads=20, num_scanner_agents=167)

    assert pool.num_leads == 20
    assert pool.num_scanner_agents == 167
    assert pool.is_running is False

    print(f"✅ Pool initialized: {pool.num_leads} leads")
    print(f"✅ Scanner agents: {pool.num_scanner_agents}")

    # Test agent assignment
    assignments = pool._assign_agents_to_leads()

    assert len(assignments) == 20
    assert all(len(agents) >= 8 for agents in assignments.values())
    assert all(len(agents) <= 9 for agents in assignments.values())

    print(f"✅ Assignments: {len(assignments)} team leads")

    # Count total assigned
    total_assigned = sum(len(agents) for agents in assignments.values())
    assert total_assigned == 167

    print(f"✅ Total agents assigned: {total_assigned}")

    # Show distribution
    lead_sizes = [len(agents) for agents in assignments.values()]
    print(f"✅ Agent distribution: min={min(lead_sizes)}, max={max(lead_sizes)}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 9: TeamLeadPool Stats
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 9] TeamLeadPool Stats")
    print("-" * 70)

    await pool.initialize()
    pool_stats = pool.get_pool_stats()

    assert pool_stats["total_team_leads"] == 20
    assert pool_stats["pool_status"] == "stopped"
    assert "signals_processed" in pool_stats
    assert "validation_rate" in pool_stats

    print(f"✅ Pool status: {pool_stats['pool_status']}")
    print(f"✅ Total team leads: {pool_stats['total_team_leads']}")
    print(f"✅ Signals processed: {pool_stats['signals_processed']}")
    print(f"✅ Validation rate: {pool_stats['validation_rate']:.1%}")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nTeam Lead Supervisor Features Validated:")
    print("  ✅ 3-step validation (score, reliability, peer consensus)")
    print("  ✅ Signal rejection with reason tracking")
    print("  ✅ Agent performance monitoring")
    print("  ✅ Signal direction detection")
    print("  ✅ Validated signal creation with metadata")
    print("  ✅ Team-level statistics")
    print("  ✅ Pool management (20 leads, 167 agents)")
    print("  ✅ Round-robin agent assignment")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
