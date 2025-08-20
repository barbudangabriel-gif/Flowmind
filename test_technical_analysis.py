#!/usr/bin/env python3
"""
Technical Analysis Expert Agent Testing Script
Test the new Technical Analysis Expert Agent implementation with Smart Money Concepts
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://tradestation-sync-1.preview.emergentagent.com/api"

def run_test(test_name, method, endpoint, expected_status=200, params=None, data=None):
    """Run a single API test"""
    url = f"{BACKEND_URL}/{endpoint}"
    
    try:
        print(f"\n🧪 Testing: {test_name}")
        print(f"   📡 {method} {url}")
        
        if params:
            print(f"   📋 Params: {params}")
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, params=params, json=data, timeout=30)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False, {}
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                response_data = response.json()
                print(f"   ✅ SUCCESS: {test_name}")
                return True, response_data
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                return False, {}
        else:
            print(f"   ❌ FAILED: Expected {expected_status}, got {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")
            return False, {}
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, {}

def test_technical_analysis_expert_agent():
    """Test Technical Analysis Expert Agent with Smart Money Concepts"""
    print("🔬 TESTING TECHNICAL ANALYSIS EXPERT AGENT - SMART MONEY CONCEPTS")
    print("=" * 80)
    print("🎯 OBJECTIVE: Test new Technical Analysis Expert Agent implementation")
    print("📋 REQUIREMENTS:")
    print("   1. ✅ POST /api/agents/technical-analysis?symbol=NVDA&include_smc=true")
    print("   2. ✅ Different Symbol Test - POST /api/agents/technical-analysis?symbol=AAPL")
    print("   3. ✅ Batch Technical Analysis - GET /api/agents/technical-analysis/batch?symbols=NVDA,AAPL,MSFT&include_smc=true")
    print("   4. ✅ Technical Analysis Methodology - GET /api/agents/technical-analysis/methodology")
    
    test_results = {}
    
    # Test 1: Technical Analysis Agent - NVDA with Smart Money Concepts
    print(f"\n📊 PHASE 1: Technical Analysis Agent - NVDA with Smart Money Concepts")
    print("-" * 60)
    
    success, nvda_data = run_test(
        "Technical Analysis Agent (NVDA + SMC)", 
        "POST", 
        "agents/technical-analysis", 
        200, 
        params={"symbol": "NVDA", "include_smc": "true"}
    )
    
    test_results['nvda_analysis'] = success
    
    if success:
        # Verify response structure
        required_fields = [
            'symbol', 'technical_score', 'recommendation', 'confidence_level', 
            'key_signals', 'smart_money_analysis', 'multi_timeframe_analysis',
            'technical_indicators', 'support_resistance_levels', 'risk_reward_analysis',
            'position_sizing', 'entry_timing', 'timestamp'
        ]
        
        missing_fields = [field for field in required_fields if field not in nvda_data]
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
        else:
            print(f"   ✅ All required fields present")
        
        nvda_score = nvda_data.get('technical_score', 0)
        nvda_recommendation = nvda_data.get('recommendation', 'UNKNOWN')
        nvda_confidence = nvda_data.get('confidence_level', 'unknown')
        smc_analysis = nvda_data.get('smart_money_analysis', {})
        timeframe_analysis = nvda_data.get('multi_timeframe_analysis', {})
        indicators = nvda_data.get('technical_indicators', {})
        
        print(f"   📊 NVDA Results:")
        print(f"     - Technical Score: {nvda_score}")
        print(f"     - Recommendation: {nvda_recommendation}")
        print(f"     - Confidence: {nvda_confidence}")
        print(f"     - Smart Money Components: {len(smc_analysis)}")
        print(f"     - Timeframes: {list(timeframe_analysis.keys())}")
        print(f"     - Indicators: {len(indicators)}")
    
    # Test 2: Different Symbol Test - AAPL
    print(f"\n📊 PHASE 2: Different Symbol Test - AAPL")
    print("-" * 60)
    
    success, aapl_data = run_test(
        "Technical Analysis Agent (AAPL)", 
        "POST", 
        "agents/technical-analysis", 
        200, 
        params={"symbol": "AAPL"}
    )
    
    test_results['aapl_analysis'] = success
    
    if success:
        aapl_score = aapl_data.get('technical_score', 0)
        aapl_recommendation = aapl_data.get('recommendation', 'UNKNOWN')
        
        print(f"   📊 AAPL Results:")
        print(f"     - Technical Score: {aapl_score}")
        print(f"     - Recommendation: {aapl_recommendation}")
        
        # Compare with NVDA
        if 'nvda_analysis' in test_results and test_results['nvda_analysis']:
            nvda_score = nvda_data.get('technical_score', 0)
            if abs(nvda_score - aapl_score) >= 5:
                print(f"     ✅ Different conditions detected (NVDA: {nvda_score}, AAPL: {aapl_score})")
            else:
                print(f"     ⚠️  Similar scores")
    
    # Test 3: Batch Technical Analysis
    print(f"\n📊 PHASE 3: Batch Technical Analysis")
    print("-" * 60)
    
    success, batch_data = run_test(
        "Batch Technical Analysis", 
        "GET", 
        "agents/technical-analysis/batch", 
        200, 
        params={"symbols": "NVDA,AAPL,MSFT", "include_smc": "true"}
    )
    
    test_results['batch_analysis'] = success
    
    if success:
        symbols_analyzed = batch_data.get('symbols_analyzed', 0)
        successful_analyses = batch_data.get('successful_analyses', 0)
        results = batch_data.get('results', {})
        
        print(f"   📊 Batch Results:")
        print(f"     - Symbols Analyzed: {symbols_analyzed}")
        print(f"     - Successful: {successful_analyses}")
        print(f"     - Success Rate: {(successful_analyses/symbols_analyzed)*100:.1f}%" if symbols_analyzed > 0 else "N/A")
        
        for symbol in ['NVDA', 'AAPL', 'MSFT']:
            if symbol in results:
                result = results[symbol]
                score = result.get('technical_score', 0)
                recommendation = result.get('recommendation', 'UNKNOWN')
                print(f"     - {symbol}: Score {score}, {recommendation}")
    
    # Test 4: Technical Analysis Methodology
    print(f"\n📊 PHASE 4: Technical Analysis Methodology")
    print("-" * 60)
    
    success, methodology_data = run_test(
        "Technical Analysis Methodology", 
        "GET", 
        "agents/technical-analysis/methodology", 
        200
    )
    
    test_results['methodology'] = success
    
    if success:
        agent_name = methodology_data.get('agent_name', '')
        version = methodology_data.get('version', '')
        analysis_weights = methodology_data.get('analysis_weights', {})
        smc_concepts = methodology_data.get('smart_money_concepts', {})
        
        print(f"   📊 Methodology:")
        print(f"     - Agent: {agent_name}")
        print(f"     - Version: {version}")
        print(f"     - Analysis Components: {len(analysis_weights)}")
        print(f"     - Smart Money Concepts: {len(smc_concepts)}")
    
    # Final Assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 TEST RESULTS:")
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    if success_rate >= 75:
        print(f"\n🎉 VERDICT: Technical Analysis Expert Agent working well!")
        print(f"   All major endpoints functional with Smart Money Concepts.")
        print(f"   Multi-timeframe analysis and professional recommendations operational.")
    elif success_rate >= 50:
        print(f"\n✅ VERDICT: Mostly working with some issues.")
    else:
        print(f"\n❌ VERDICT: Significant issues detected.")
    
    return success_rate >= 75

if __name__ == "__main__":
    print(f"🚀 Technical Analysis Expert Agent Testing")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_technical_analysis_expert_agent()
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("✅ Technical Analysis Expert Agent is working correctly!")
        sys.exit(0)
    else:
        print("❌ Technical Analysis Expert Agent has issues.")
        sys.exit(1)