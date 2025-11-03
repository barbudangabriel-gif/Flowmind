#!/usr/bin/env python3
"""
Manual test for options strategy recommendations.
Tests different score scenarios to see complete strategy output.
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from investment_scoring_agent import InvestmentScoringAgent


async def test_manual_strategies():
    """Test options strategy recommendations with manual score scenarios."""
    
    print("=" * 80)
    print("✨ Testing Options Strategy Recommendations (Manual Scenarios)")
    print("=" * 80)
    
    agent = InvestmentScoringAgent()
    
    # Mock UW data with realistic options flow
    mock_uw_data = {
        "options_flow": [
            {"strike": 220, "iv": 0.58, "premium": 450, "underlying_price": 245.0},
            {"strike": 230, "iv": 0.55, "premium": 600, "underlying_price": 245.0},
            {"strike": 250, "iv": 0.60, "premium": 800, "underlying_price": 245.0},
        ],
        "dark_pool": [
            {"volume": 150000, "dark_percentage": 0.42},
        ],
        "congressional": [
            {"type": "buy", "amount": 50000},
        ],
    }
    
    mock_signal_scores = {
        "discount_opportunity": 45,
        "options_flow": 65,
        "dark_pool": 58,
        "congressional": 70,
    }
    
    test_scenarios = [
        {
            "name": "Strong Buy + High IV → Sell Cash-Secured Put",
            "score": 85,
            "avg_iv": 0.58,
            "discount": 45,
        },
        {
            "name": "Strong Buy + Low IV → Buy Long Call",
            "score": 82,
            "avg_iv": 0.25,
            "discount": 50,
        },
        {
            "name": "Neutral + High IV → Iron Condor",
            "score": 60,
            "avg_iv": 0.52,
            "discount": 48,
        },
        {
            "name": "Moderate Buy + Discount → Bull Call Spread",
            "score": 75,
            "avg_iv": 0.35,
            "discount": 68,
        },
        {
            "name": "Low Score → Protective Put",
            "score": 42,
            "avg_iv": 0.40,
            "discount": 30,
        },
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'=' * 80}")
        print(f"📊 Scenario: {scenario['name']}")
        print(f"{'=' * 80}")
        print(f"   Score: {scenario['score']}/100")
        print(f"   Avg IV: {scenario['avg_iv']*100:.0f}%")
        print(f"   Discount Score: {scenario['discount']}/100")
        
        # Update mock data for this scenario
        for opt in mock_uw_data["options_flow"]:
            opt["iv"] = scenario["avg_iv"]
        
        mock_signal_scores["discount_opportunity"] = scenario["discount"]
        
        # Get strategy recommendations
        strategies = agent._recommend_options_strategies(
            "TSLA",
            scenario["score"],
            mock_uw_data,
            mock_signal_scores
        )
        
        print(f"\n✨ STRATEGIES RECOMMENDED: {len(strategies)}")
        
        if not strategies:
            print("   ❌ No strategies triggered (check threshold logic)")
            continue
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n   [{i}] {strategy['strategy_type']}")
            print(f"       Priority: {strategy['priority']}")
            print(f"       Risk: {strategy['risk_level']}")
            print(f"       Rationale: {strategy['rationale']}")
            
            # Trade details
            trade = strategy.get('trade_details', {})
            if trade.get('action') == 'MULTI_LEG':
                print(f"\n       Multi-leg Trade:")
                for leg in trade.get('legs', []):
                    print(f"          • {leg['action']} {leg['type']} @ ${leg['strike']}")
                if 'net_credit' in trade:
                    print(f"       💰 Net Credit: ${trade['net_credit']:.2f}")
                if 'net_debit' in trade:
                    print(f"       💸 Net Debit: ${trade['net_debit']:.2f}")
            else:
                print(f"\n       Single-leg Trade:")
                print(f"          Action: {trade.get('action')}")
                print(f"          Strike: ${trade.get('strike', 0):.2f}")
                if 'premium_per_share' in trade:
                    print(f"          Premium: ${trade.get('premium_per_share', 0):.2f}/share")
                    print(f"          💰 Total: ${trade.get('total_premium', 0):.2f}")
                if 'total_cost' in trade:
                    print(f"          💸 Cost: ${trade.get('total_cost', 0):.2f}")
                print(f"          DTE: {trade.get('dte', 0)} days")
            
            # Expected outcomes
            outcomes = strategy.get('expected_outcomes', {})
            print(f"\n       Expected Outcomes:")
            for key, value in outcomes.items():
                if isinstance(value, (int, float)):
                    print(f"          {key.replace('_', ' ').title()}: ${value:.2f}")
                else:
                    print(f"          {key.replace('_', ' ').title()}: {value}")
            
            # Management
            if 'next_phase' in strategy:
                print(f"\n       📈 Next Phase: {strategy['next_phase']}")
            if 'exit_plan' in strategy:
                print(f"       🚪 Exit Plan: {strategy['exit_plan']}")
            if 'management' in strategy:
                print(f"       🔧 Management: {strategy['management']}")
            
            # Market context
            context = strategy.get('market_context', {})
            if context:
                print(f"\n       📊 Market Context:")
                print(f"          Current Price: ${context.get('current_price', 0):.2f}")
                print(f"          Avg IV: {context.get('avg_iv', 0):.1f}%")
                print(f"          IV Percentile: {context.get('iv_percentile', 'N/A')}")
                print(f"          Flow Sentiment: {context.get('options_flow_sentiment', 'N/A')}")
    
    print(f"\n{'=' * 80}")
    print("✅ Manual Strategy Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_manual_strategies())
