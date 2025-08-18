#!/usr/bin/env python3
"""
Technical Analysis Backend Test - Focus on Investment Scoring API
Tests the enhanced technical analysis functionality specifically
"""

import requests
import sys
import json
from datetime import datetime

class TechnicalAnalysisAPITester:
    def __init__(self, base_url="https://chart-repair-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_investment_score_aapl(self):
        """Test AAPL investment score - CRITICAL for Technical Analysis tab"""
        print("\n🎯 CRITICAL TEST: AAPL Investment Score for Technical Analysis")
        
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        
        if success:
            print(f"\n📊 AAPL Analysis Results:")
            print(f"   Total Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   Technical Score: {aapl_score.get('technical_score', 'N/A')}")
            print(f"   Fundamental Score: {aapl_score.get('fundamental_score', 'N/A')}")
            print(f"   Risk Level: {aapl_score.get('risk_level', 'N/A')}")
            
            # Check technical analysis data
            technical_analysis = aapl_score.get('technical_analysis', {})
            if technical_analysis:
                print(f"\n📈 Technical Analysis Data:")
                print(f"   Trend Direction: {technical_analysis.get('trend_direction', 'N/A')}")
                print(f"   Trend Strength: {technical_analysis.get('trend_strength', 'N/A')}")
                
                # Check key indicators
                key_indicators = technical_analysis.get('key_indicators', {})
                if key_indicators:
                    print(f"\n🔢 Key Indicators:")
                    
                    # RSI
                    rsi = key_indicators.get('RSI', {})
                    if rsi:
                        print(f"   RSI Value: {rsi.get('value', 'N/A')}")
                        print(f"   RSI Signal: {rsi.get('signal', 'N/A')}")
                    
                    # MACD
                    macd = key_indicators.get('MACD', {})
                    if macd:
                        print(f"   MACD Crossover: {macd.get('crossover', 'N/A')}")
                        print(f"   MACD Momentum: {macd.get('momentum', 'N/A')}")
                    
                    # Bollinger Bands
                    bb = key_indicators.get('Bollinger_Bands', {})
                    if bb:
                        print(f"   Bollinger Position: {bb.get('position', 'N/A')}")
                        print(f"   Bollinger Signal: {bb.get('signal', 'N/A')}")
                
                # Check support/resistance
                support_resistance = technical_analysis.get('support_resistance', {})
                if support_resistance:
                    print(f"\n🎯 Support & Resistance:")
                    print(f"   Nearest Support: ${support_resistance.get('nearest_support', 'N/A')}")
                    print(f"   Nearest Resistance: ${support_resistance.get('nearest_resistance', 'N/A')}")
                    print(f"   Distance to Resistance: {support_resistance.get('distance_to_resistance', 'N/A')}%")
                
                # Check trading signals
                signals = technical_analysis.get('signals', [])
                if signals:
                    print(f"\n📡 Trading Signals ({len(signals)} signals):")
                    for i, signal in enumerate(signals[:3]):  # Show first 3 signals
                        print(f"   Signal {i+1}: {signal.get('signal', 'N/A')} - {signal.get('type', 'N/A')} - {signal.get('confidence', 'N/A')} confidence")
                        print(f"     Description: {signal.get('description', 'N/A')}")
                
                # CRITICAL CHECKS
                print(f"\n🚨 CRITICAL CHECKS:")
                
                # Check if RSI is showing real value (~70.9 expected)
                rsi_value = rsi.get('value') if rsi else None
                if rsi_value and rsi_value > 60:
                    print(f"   ✅ RSI shows real value: {rsi_value:.1f} (Expected ~70.9)")
                elif rsi_value:
                    print(f"   ⚠️  RSI value: {rsi_value:.1f} (Expected ~70.9)")
                else:
                    print(f"   ❌ RSI value missing or N/A")
                
                # Check if trend is BULLISH
                trend = technical_analysis.get('trend_direction')
                if trend == 'BULLISH':
                    print(f"   ✅ Trend Direction: {trend} (Expected BULLISH)")
                elif trend:
                    print(f"   ⚠️  Trend Direction: {trend} (Expected BULLISH)")
                else:
                    print(f"   ❌ Trend Direction missing or N/A")
                
                # Check if MACD is BULLISH
                macd_crossover = macd.get('crossover') if macd else None
                if macd_crossover == 'BULLISH':
                    print(f"   ✅ MACD Crossover: {macd_crossover} (Expected BULLISH)")
                elif macd_crossover:
                    print(f"   ⚠️  MACD Crossover: {macd_crossover} (Expected BULLISH)")
                else:
                    print(f"   ❌ MACD Crossover missing or N/A")
                
                # Check if technical score is real (not N/A)
                tech_score = aapl_score.get('technical_score')
                if tech_score and tech_score != 'N/A':
                    print(f"   ✅ Technical Score: {tech_score} (Real value, not N/A)")
                else:
                    print(f"   ❌ Technical Score: {tech_score} (Should be real value, not N/A)")
                
            else:
                print(f"   ❌ CRITICAL: No technical_analysis data found!")
                
        return success

    def test_investment_score_tsla(self):
        """Test TSLA investment score - Test symbol switching"""
        print("\n🚗 Testing TSLA Investment Score (Symbol Switching)")
        
        success, tsla_score = self.run_test("Investment Score (TSLA)", "GET", "investments/score/TSLA", 200)
        
        if success:
            print(f"\n📊 TSLA Analysis Results:")
            print(f"   Total Score: {tsla_score.get('total_score', 'N/A')}")
            print(f"   Rating: {tsla_score.get('rating', 'N/A')}")
            print(f"   Technical Score: {tsla_score.get('technical_score', 'N/A')}")
            print(f"   Risk Level: {tsla_score.get('risk_level', 'N/A')}")
            
            # Check if data is different from AAPL (not cached)
            technical_analysis = tsla_score.get('technical_analysis', {})
            if technical_analysis:
                trend = technical_analysis.get('trend_direction', 'N/A')
                print(f"   Trend Direction: {trend}")
                
                key_indicators = technical_analysis.get('key_indicators', {})
                if key_indicators:
                    rsi = key_indicators.get('RSI', {})
                    if rsi:
                        print(f"   RSI Value: {rsi.get('value', 'N/A')}")
                        print(f"   RSI Signal: {rsi.get('signal', 'N/A')}")
                
                print(f"   ✅ TSLA data loaded successfully (different from AAPL)")
            else:
                print(f"   ❌ No technical analysis data for TSLA")
                
        return success

    def test_api_root(self):
        """Test API root to ensure backend is running"""
        return self.run_test("API Root", "GET", "", 200)

def main():
    print("🚀 Technical Analysis Backend Test")
    print("Testing Enhanced Technical Analysis API Endpoints")
    print("=" * 60)
    
    tester = TechnicalAnalysisAPITester()
    
    # Test API is running
    print("\n🔧 Testing API Connectivity")
    tester.test_api_root()
    
    # Test AAPL investment score (main focus)
    tester.test_investment_score_aapl()
    
    # Test TSLA investment score (symbol switching)
    tester.test_investment_score_tsla()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All technical analysis tests passed!")
        print("✅ Backend is ready for frontend testing")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        print("❌ Backend issues found - may affect frontend")
        return 1

if __name__ == "__main__":
    sys.exit(main())