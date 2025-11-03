#!/usr/bin/env python3
"""
Test script for integrated Options + Scoring system.
Tests the new _recommend_options_strategies() function.
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from investment_scoring_agent import InvestmentScoringAgent


async def test_integrated_scoring():
    """Test the integrated scoring system with options recommendations."""
    
    print("=" * 80)
    print("🚀 Testing Integrated Options + Scoring System")
    print("=" * 80)
    
    agent = InvestmentScoringAgent()
    
    # Test scenarios
    test_symbols = [
        ("TSLA", "High growth tech - likely strong buy"),
        ("AAPL", "Mega cap tech - moderate buy"),
        ("NFLX", "Streaming - neutral to bullish"),
        ("XOM", "Energy - defensive play"),
    ]
    
    for symbol, description in test_symbols:
        print(f"\n{'=' * 80}")
        print(f"📊 Testing: {symbol} ({description})")
        print(f"{'=' * 80}")
        
        try:
            # Generate comprehensive score with options strategies
            result = await agent.generate_investment_score(symbol)
            
            # Display main score
            print(f"\n🎯 Investment Score: {result['investment_score']:.1f}/100")
            print(f"📈 Recommendation: {result['recommendation']}")
            print(f"🎲 Confidence: {result['confidence_level'].upper()}")
            
            # Display risk analysis
            print(f"\n⚠️  Risk Analysis:")
            risk = result.get("risk_analysis", {})
            print(f"   Overall Risk: {risk.get('overall_risk_level', 'unknown').upper()}")
            print(f"   Risk Factors: {len(risk.get('risk_factors', []))}")
            print(f"   Mitigating Factors: {len(risk.get('mitigating_factors', []))}")
            
            # Display key signals
            print(f"\n📡 Key Signals:")
            for signal in result.get("key_signals", [])[:5]:
                print(f"   • {signal}")
            
            # ✨ NEW: Display options strategies
            strategies = result.get("options_strategies", [])
            print(f"\n✨ OPTIONS STRATEGIES RECOMMENDED: {len(strategies)}")
            
            for i, strategy in enumerate(strategies, 1):
                print(f"\n   [{i}] {strategy['strategy_type']}")
                print(f"       Priority: {strategy['priority']}")
                print(f"       Risk: {strategy['risk_level']}")
                print(f"       Rationale: {strategy['rationale']}")
                
                # Trade details
                trade = strategy.get('trade_details', {})
                if trade.get('action') == 'MULTI_LEG':
                    print(f"\n       Trade: {len(trade.get('legs', []))} legs")
                    for leg in trade.get('legs', []):
                        print(f"          • {leg['action']} {leg['type']} @ ${leg['strike']}")
                    if 'net_credit' in trade:
                        print(f"       Net Credit: ${trade['net_credit']:.2f}")
                    if 'net_debit' in trade:
                        print(f"       Net Debit: ${trade['net_debit']:.2f}")
                else:
                    print(f"       Action: {trade.get('action')}")
                    print(f"       Strike: ${trade.get('strike', 0):.2f}")
                    if 'premium_per_share' in trade:
                        print(f"       Premium: ${trade.get('premium_per_share', 0):.2f}/share (${trade.get('total_premium', 0):.2f} total)")
                    if 'total_cost' in trade:
                        print(f"       Cost: ${trade.get('total_cost', 0):.2f}")
                    print(f"       DTE: {trade.get('dte', 0)} days")
                
                # Expected outcomes
                outcomes = strategy.get('expected_outcomes', {})
                print(f"\n       Expected Outcomes:")
                if 'max_profit' in outcomes:
                    profit_val = outcomes['max_profit']
                    if isinstance(profit_val, str):
                        print(f"          Max Profit: {profit_val}")
                    else:
                        print(f"          Max Profit: ${profit_val:.2f}")
                if 'max_loss' in outcomes:
                    loss_val = outcomes['max_loss']
                    if isinstance(loss_val, str):
                        print(f"          Max Loss: {loss_val}")
                    else:
                        print(f"          Max Loss: ${loss_val:.2f}")
                if 'breakeven' in outcomes:
                    print(f"          Breakeven: ${outcomes['breakeven']:.2f}")
                if 'profit_range' in outcomes:
                    print(f"          Profit Range: {outcomes['profit_range']}")
                if 'pop' in outcomes:
                    print(f"          Probability of Profit: {outcomes['pop']}")
                
                # Management/exit plan
                if 'next_phase' in strategy:
                    print(f"\n       Next Phase: {strategy['next_phase']}")
                if 'exit_plan' in strategy:
                    print(f"       Exit Plan: {strategy['exit_plan']}")
                if 'management' in strategy:
                    print(f"       Management: {strategy['management']}")
                
                # Market context
                context = strategy.get('market_context', {})
                if context:
                    print(f"\n       Market Context:")
                    print(f"          Current Price: ${context.get('current_price', 0):.2f}")
                    print(f"          Avg IV: {context.get('avg_iv', 0):.1f}%")
                    print(f"          IV Percentile: {context.get('iv_percentile', 'N/A')}")
                    print(f"          Flow Sentiment: {context.get('options_flow_sentiment', 'N/A')}")
            
            print(f"\n{'=' * 80}")
            print(f"✅ Successfully tested {symbol}")
            
        except Exception as e:
            print(f"\n❌ Error testing {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("🎉 Integration Test Complete!")
    print("=" * 80)
    print("\n✨ KEY INNOVATION: Score → Options Strategy → Trade Plan")
    print("   Now you see exactly HOW to trade based on the score!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_integrated_scoring())
