#!/usr/bin/env python3
"""
Test script specifically for Portfolio Charts and Smart Rebalancing Agent endpoints
"""

import sys
import os
sys.path.append('/app')

from backend_test import StockMarketAPITester

def main():
    print("🚀 Testing Portfolio Charts and Smart Rebalancing Agent Endpoints")
    print("=" * 80)
    
    # Initialize tester
    tester = StockMarketAPITester()
    
    # Test Portfolio Charts endpoints
    print("\n📊 TESTING PORTFOLIO CHARTS ENDPOINTS")
    print("=" * 60)
    portfolio_charts_success = tester.test_portfolio_charts_endpoints()
    
    # Test Smart Rebalancing Agent endpoints
    print("\n🤖 TESTING SMART REBALANCING AGENT ENDPOINTS")
    print("=" * 60)
    smart_rebalancing_success = tester.test_smart_rebalancing_agent_endpoints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 FINAL RESULTS")
    print("=" * 80)
    
    results = [
        ("Portfolio Charts Endpoints", portfolio_charts_success),
        ("Smart Rebalancing Agent Endpoints", smart_rebalancing_success)
    ]
    
    passed_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} test suites passed)")
    
    if success_rate >= 85:
        print("\n🎉 EXCELLENT: Portfolio Charts and Smart Rebalancing Agent endpoints working perfectly!")
        print("   Both services are ready for frontend integration.")
    elif success_rate >= 70:
        print("\n✅ GOOD: Most endpoints working with minor issues.")
    else:
        print("\n❌ NEEDS ATTENTION: Significant issues detected in endpoints.")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)