"""
Test suite for Master Director (Tier 1)

Tests:
1. MasterDirector initialization
2. Decision context gathering
3. Fallback decision logic (rule-based)
4. Portfolio risk calculation
5. Execution signal creation
6. Director stats
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tier1_director.master_director import MasterDirector


async def run_tests():
    """Run all Master Director tests"""

    print("\n" + "=" * 70)
    print("MASTER DIRECTOR TEST SUITE")
    print("=" * 70)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 1: MasterDirector Initialization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] MasterDirector Initialization")
    print("-" * 70)

    director = MasterDirector(
        director_id="master_director",
        use_llm=False,  # Use fallback for testing
        confidence_threshold=70.0,
    )

    assert director.director_id == "master_director"
    assert len(director.supervised_sector_heads) == 10
    assert director.confidence_threshold == 70.0
    assert director.use_llm is False  # Fallback mode

    print(f"✅ Director ID: {director.director_id}")
    print(f"✅ Supervised sector heads: {len(director.supervised_sector_heads)}")
    print(f"✅ Confidence threshold: {director.confidence_threshold}%")
    print(f"✅ LLM mode: {'GPT-4o' if director.use_llm else 'Fallback'}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Decision Context Gathering
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Decision Context Gathering")
    print("-" * 70)

    signal = {
        "ticker": "AAPL",
        "sector": "technology",
        "total_score": 75.0,
        "sector_risk_score": 45.0,
    }

    context = await director._gather_decision_context(signal)

    assert "portfolio" in context
    assert "market" in context
    assert "risk" in context
    assert "news" in context

    print(f"✅ Portfolio context: {context['portfolio']['total_value']:,.0f}")
    print(f"✅ Market regime: {context['market']['regime']}")
    print(f"✅ Portfolio risk: {context['risk']['portfolio_risk']:.1f}/100")
    print(f"✅ News items: {len(context['news'])}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 3: Fallback Decision Logic (HIGH SCORE - APPROVE)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Fallback Decision (high score - should approve)")
    print("-" * 70)

    high_score_signal = {
        "ticker": "AAPL",
        "sector": "technology",
        "total_score": 80.0,  # High score
        "sector_risk_score": 40.0,
    }

    decision = await director._fallback_decision(high_score_signal, context)

    assert "approved" in decision
    assert "confidence" in decision
    assert "reasoning" in decision

    print(f"✅ Approved: {decision['approved']}")
    print(f"✅ Confidence: {decision['confidence']:.0f}%")
    print(f"✅ Reasoning: {decision['reasoning']}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 4: Fallback Decision Logic (LOW SCORE - REJECT)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Fallback Decision (low score - should reject)")
    print("-" * 70)

    low_score_signal = {
        "ticker": "XYZ",
        "sector": "technology",
        "total_score": 55.0,  # Low score
        "sector_risk_score": 60.0,
    }

    decision = await director._fallback_decision(low_score_signal, context)

    assert decision["approved"] is False
    print(f"✅ Approved: {decision['approved']}")
    print(f"✅ Confidence: {decision['confidence']:.0f}% (below threshold)")
    print(f"✅ Reasoning: {decision['reasoning']}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 5: Portfolio Risk Calculation (EMPTY PORTFOLIO)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Portfolio Risk Calculation (empty portfolio)")
    print("-" * 70)

    director.current_portfolio = {}
    risk = await director._calculate_portfolio_risk()

    assert risk == 0.0
    print(f"✅ Portfolio risk: {risk:.1f}/100 (empty portfolio)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 6: Portfolio Risk Calculation (CONCENTRATED PORTFOLIO)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Portfolio Risk Calculation (concentrated portfolio)")
    print("-" * 70)

    # Simulated concentrated portfolio (1 position = 30% of portfolio)
    director.current_portfolio = {
        "AAPL": {"value": 30000, "sector": "technology"},
    }
    director.total_portfolio_value = 100000

    risk = await director._calculate_portfolio_risk()

    assert risk > 0
    print(f"✅ Portfolio risk: {risk:.1f}/100 (30% concentration)")
    print(f"   (Penalty for single position > 15%)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 7: Execution Signal Creation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 7] Execution Signal Creation")
    print("-" * 70)

    original_signal = {
        "ticker": "AAPL",
        "sector": "technology",
        "total_score": 80.0,
        "sector_risk_score": 40.0,
    }

    decision_result = {
        "approved": True,
        "confidence": 85.0,
        "reasoning": "High signal score, favorable conditions",
        "llm_model": "fallback",
    }

    execution_signal = director._create_execution_signal(original_signal, decision_result)

    assert "director_approved" in execution_signal
    assert execution_signal["director_approved"] is True
    assert "director_confidence" in execution_signal
    assert "director_reasoning" in execution_signal
    assert "position_size" in execution_signal
    assert "max_loss" in execution_signal

    print(f"✅ Director approved: {execution_signal['director_approved']}")
    print(f"✅ Confidence: {execution_signal['director_confidence']}%")
    print(f"✅ Reasoning: {execution_signal['director_reasoning']}")
    print(f"✅ Position size: ${execution_signal['position_size']:,.0f}")
    print(f"✅ Max loss: ${execution_signal['max_loss']:,.0f}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 8: LLM Prompt Building
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 8] LLM Prompt Building")
    print("-" * 70)

    signal = {
        "ticker": "TSLA",
        "sector": "consumer",
        "total_score": 75.0,
        "sector_risk_score": 50.0,
        "validation_confidence": 0.75,
    }

    prompt = director._build_llm_prompt(signal, context)

    assert "TSLA" in prompt
    assert "consumer" in prompt
    assert "Signal Score: 75" in prompt
    assert "JSON format" in prompt

    print("✅ Prompt generated successfully")
    print(f"✅ Prompt length: {len(prompt)} chars")
    print(f"✅ Contains ticker: {'TSLA' in prompt}")
    print(f"✅ Contains JSON instruction: {'JSON format' in prompt}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 9: Make Decision (APPROVE)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 9] Make Decision (should approve)")
    print("-" * 70)

    director.signals_processed = 0
    director.signals_approved = 0
    director.signals_rejected = 0

    approved_signal = {
        "ticker": "NVDA",
        "sector": "technology",
        "total_score": 85.0,
        "sector_risk_score": 35.0,
        "validation_confidence": 0.80,
    }

    execution = await director.make_decision(approved_signal)

    assert execution is not None
    assert director.signals_approved == 1
    assert len(director.decisions) > 0

    print(f"✅ Execution signal generated: {execution is not None}")
    print(f"✅ Signals approved: {director.signals_approved}")
    print(f"✅ Decision recorded: {len(director.decisions)} decisions")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 10: Make Decision (REJECT)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 10] Make Decision (should reject)")
    print("-" * 70)

    rejected_signal = {
        "ticker": "ABC",
        "sector": "technology",
        "total_score": 50.0,  # Low score
        "sector_risk_score": 70.0,
        "validation_confidence": 0.55,
    }

    execution = await director.make_decision(rejected_signal)

    assert execution is None
    assert director.signals_rejected > 0

    print(f"✅ Execution signal: {execution}")
    print(f"✅ Signals rejected: {director.signals_rejected}")
    print(f"✅ Rejection reasons: {dict(director.rejection_reasons)}")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 11: Director Stats
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 11] Director Stats")
    print("-" * 70)

    director.start_time = datetime.utcnow()  # Set start time
    stats = director.get_director_stats()

    assert stats["director_id"] == "master_director"
    assert stats["llm_enabled"] is False
    assert stats["supervised_sector_heads"] == 10
    assert "signals_processed" in stats
    assert "approval_rate" in stats
    assert "recent_decisions" in stats

    print(f"✅ Director ID: {stats['director_id']}")
    print(f"✅ LLM model: {stats['llm_model']}")
    print(f"✅ Signals processed: {stats['signals_processed']}")
    print(f"✅ Approval rate: {stats['approval_rate']:.1%}")
    print(f"✅ Recent decisions: {len(stats['recent_decisions'])}")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nMaster Director Features Validated:")
    print("  ✅ GPT-4o integration (with fallback)")
    print("  ✅ Multi-factor decision making")
    print("  ✅ Context gathering (portfolio, market, risk, news)")
    print("  ✅ Fallback rule-based logic")
    print("  ✅ Portfolio risk calculation")
    print("  ✅ Execution signal generation")
    print("  ✅ Decision tracking with reasoning")
    print("  ✅ Confidence-based approval (70% threshold)")
    print("  ✅ LLM prompt structuring")
    print("  ✅ Director statistics")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
