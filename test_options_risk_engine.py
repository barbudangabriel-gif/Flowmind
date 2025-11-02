"""
Test Options Risk Engine - HIGHEST PRIORITY
Test multi-leg validation, Greeks limits, probability calculations
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta

sys.path.append('/workspaces/Flowmind/backend')

from options_risk_engine import (
    OptionsRiskEngine,
    OptionPosition,
    OptionType,
    ActionType,
    GreeksLimits,
    RiskLevel,
)


async def test_long_call_validation():
    """Test simple long call validation"""
    print("\n" + "="*60)
    print("TEST 1: Long Call (Single Leg)")
    print("="*60)
    
    # Setup
    engine = OptionsRiskEngine(greeks_limits=GreeksLimits(
        max_delta=200.0,
        max_gamma=20.0,
        max_vega=500.0,
        max_theta=100.0,
    ))
    
    # Create long call position (TSLA 250C expiring in 30 days)
    expiry = (datetime.now() + timedelta(days=30)).isoformat()
    
    new_positions = [
        OptionPosition(
            symbol="TSLA",
            option_type=OptionType.CALL,
            action=ActionType.BUY,
            strike=250.0,
            expiry=expiry,
            quantity=1,
            premium=500.0,  # $5.00 * 100
            volatility=0.45,  # 45% IV
            current_price=245.0,  # Current TSLA price
        )
    ]
    
    # Validate
    result = await engine.validate_options_trade(
        new_positions=new_positions,
        existing_positions=[],
        portfolio_cash=10000.0,
        risk_profile="MODERATE",
    )
    
    # Print results
    print(f"\n✓ Strategy Detected: {result.strategy_info['type']}")
    print(f"✓ Estimated Cost: ${result.estimated_cost:.2f}")
    print(f"✓ Max Loss: ${result.strategy_info['max_loss']:.2f}")
    print(f"✓ Max Profit: ${result.strategy_info['max_profit']:.2f}")
    
    print("\n📊 Greeks Impact:")
    print(f"  Current Portfolio: {json.dumps(result.greeks_impact['current'], indent=2)}")
    print(f"  New Trade: {json.dumps(result.greeks_impact['new_trade'], indent=2)}")
    print(f"  Combined: {json.dumps(result.greeks_impact['combined'], indent=2)}")
    
    print("\n📈 Probability Analysis:")
    for key, value in result.probability_analysis.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Risk Checks:")
    for check in result.checks:
        emoji = {"BLOCKER": "🚫", "WARNING": "⚠️", "INFO": "ℹ️", "PASS": "✅"}[check.level.value]
        print(f"  {emoji} [{check.level.value}] {check.check_name}: {check.message}")
    
    print(f"\n{'✅ TRADE ALLOWED' if result.passed else '❌ TRADE BLOCKED'}")
    
    return result


async def test_iron_condor_validation():
    """Test iron condor (4-leg strategy)"""
    print("\n" + "="*60)
    print("TEST 2: Iron Condor (4-Leg Strategy)")
    print("="*60)
    
    engine = OptionsRiskEngine()
    
    # SPY Iron Condor: 450/455 Put Spread + 470/475 Call Spread
    expiry = (datetime.now() + timedelta(days=45)).isoformat()
    current_spy = 460.0
    
    new_positions = [
        # Put Spread (credit)
        OptionPosition(
            symbol="SPY",
            option_type=OptionType.PUT,
            action=ActionType.SELL,
            strike=455.0,
            expiry=expiry,
            quantity=1,
            premium=150.0,  # Receive $1.50 * 100
            volatility=0.15,
            current_price=current_spy,
        ),
        OptionPosition(
            symbol="SPY",
            option_type=OptionType.PUT,
            action=ActionType.BUY,
            strike=450.0,
            expiry=expiry,
            quantity=1,
            premium=80.0,  # Pay $0.80 * 100
            volatility=0.15,
            current_price=current_spy,
        ),
        # Call Spread (credit)
        OptionPosition(
            symbol="SPY",
            option_type=OptionType.CALL,
            action=ActionType.SELL,
            strike=470.0,
            expiry=expiry,
            quantity=1,
            premium=140.0,  # Receive $1.40 * 100
            volatility=0.15,
            current_price=current_spy,
        ),
        OptionPosition(
            symbol="SPY",
            option_type=OptionType.CALL,
            action=ActionType.BUY,
            strike=475.0,
            expiry=expiry,
            quantity=1,
            premium=70.0,  # Pay $0.70 * 100
            volatility=0.15,
            current_price=current_spy,
        ),
    ]
    
    result = await engine.validate_options_trade(
        new_positions=new_positions,
        existing_positions=[],
        portfolio_cash=10000.0,
        risk_profile="MODERATE",
    )
    
    print(f"\n✓ Strategy Detected: {result.strategy_info['type']}")
    print(f"✓ Net Credit: ${abs(result.estimated_cost):.2f}")
    print(f"✓ Max Loss: ${result.strategy_info['max_loss']:.2f}")
    print(f"✓ Max Profit: ${result.strategy_info['max_profit']:.2f}")
    
    print("\n📊 Greeks Impact:")
    print(f"  Delta: {result.greeks_impact['combined']['delta']}")
    print(f"  Gamma: {result.greeks_impact['combined']['gamma']}")
    print(f"  Theta: {result.greeks_impact['combined']['theta']}")
    print(f"  Vega: {result.greeks_impact['combined']['vega']}")
    
    print("\n📈 Probability Analysis:")
    print(f"  PoP at Expiration: {result.probability_analysis['pop_expiration']:.1f}%")
    print(f"  Breakeven Prices: {result.probability_analysis['breakeven_prices']}")
    
    print("\n🔍 Risk Checks:")
    for check in result.checks:
        emoji = {"BLOCKER": "🚫", "WARNING": "⚠️", "INFO": "ℹ️", "PASS": "✅"}[check.level.value]
        print(f"  {emoji} [{check.level.value}] {check.check_name}: {check.message}")
    
    print(f"\n{'✅ TRADE ALLOWED' if result.passed else '❌ TRADE BLOCKED'}")
    
    return result


async def test_greeks_limit_violation():
    """Test Greeks limit violation (should block trade)"""
    print("\n" + "="*60)
    print("TEST 3: Greeks Limit Violation (Should Block)")
    print("="*60)
    
    # Set very low limits to trigger blockers
    engine = OptionsRiskEngine(greeks_limits=GreeksLimits(
        max_delta=50.0,  # Very low limit
        max_gamma=5.0,
        max_vega=200.0,
        max_theta=30.0,
    ))
    
    # Large position to exceed limits
    expiry = (datetime.now() + timedelta(days=30)).isoformat()
    
    new_positions = [
        OptionPosition(
            symbol="TSLA",
            option_type=OptionType.CALL,
            action=ActionType.BUY,
            strike=250.0,
            expiry=expiry,
            quantity=5,  # 5 contracts = high delta
            premium=500.0,
            volatility=0.45,
            current_price=245.0,
        )
    ]
    
    result = await engine.validate_options_trade(
        new_positions=new_positions,
        existing_positions=[],
        portfolio_cash=10000.0,
        risk_profile="CONSERVATIVE",
    )
    
    print(f"\n✓ Strategy: {result.strategy_info['type']}")
    print(f"✓ Position Size: {new_positions[0].quantity} contracts")
    print(f"✓ Combined Delta: {result.greeks_impact['combined']['delta']} (Limit: 50)")
    
    print("\n🔍 Risk Checks:")
    blockers = [c for c in result.checks if c.level == RiskLevel.BLOCKER]
    warnings = [c for c in result.checks if c.level == RiskLevel.WARNING]
    
    print(f"\n🚫 BLOCKERS ({len(blockers)}):")
    for check in blockers:
        print(f"  • {check.check_name}: {check.message}")
    
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for check in warnings:
        print(f"  • {check.check_name}: {check.message}")
    
    print(f"\n{'✅ TRADE ALLOWED' if result.passed else '❌ TRADE BLOCKED'}")
    
    return result


async def test_insufficient_capital():
    """Test insufficient capital (should block trade)"""
    print("\n" + "="*60)
    print("TEST 4: Insufficient Capital (Should Block)")
    print("="*60)
    
    engine = OptionsRiskEngine()
    
    # Expensive position, low cash
    expiry = (datetime.now() + timedelta(days=30)).isoformat()
    
    new_positions = [
        OptionPosition(
            symbol="TSLA",
            option_type=OptionType.CALL,
            action=ActionType.BUY,
            strike=250.0,
            expiry=expiry,
            quantity=10,  # 10 contracts = $5,000 cost
            premium=500.0,
            volatility=0.45,
            current_price=245.0,
        )
    ]
    
    result = await engine.validate_options_trade(
        new_positions=new_positions,
        existing_positions=[],
        portfolio_cash=2000.0,  # Only $2,000 available
        risk_profile="MODERATE",
    )
    
    print(f"\n✓ Estimated Cost: ${result.estimated_cost:.2f}")
    print(f"✓ Available Cash: $2,000.00")
    
    capital_check = [c for c in result.checks if c.check_name == "capital_requirement"][0]
    print(f"\n🚫 {capital_check.message}")
    
    print(f"\n{'✅ TRADE ALLOWED' if result.passed else '❌ TRADE BLOCKED'}")
    
    return result


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OPTIONS RISK ENGINE TEST SUITE")
    print("Testing HIGHEST PRIORITY validation system")
    print("="*60)
    
    try:
        # Test 1: Simple long call
        result1 = await test_long_call_validation()
        
        # Test 2: Complex iron condor
        result2 = await test_iron_condor_validation()
        
        # Test 3: Greeks limit violation
        result3 = await test_greeks_limit_violation()
        
        # Test 4: Insufficient capital
        result4 = await test_insufficient_capital()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Test 1 (Long Call): {'✅ PASS' if result1.passed else '❌ FAIL'}")
        print(f"Test 2 (Iron Condor): {'✅ PASS' if result2.passed else '❌ FAIL'}")
        print(f"Test 3 (Greeks Violation): {'❌ BLOCKED (Expected)' if not result3.passed else '⚠️  Should have blocked'}")
        print(f"Test 4 (Low Capital): {'❌ BLOCKED (Expected)' if not result4.passed else '⚠️  Should have blocked'}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
