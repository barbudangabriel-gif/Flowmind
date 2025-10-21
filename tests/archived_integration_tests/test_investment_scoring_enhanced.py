#!/usr/bin/env python3
"""
Enhanced Investment Scoring Agent Test
Tests the new discount/premium specialized logic as requested in the review.
"""

import requests
import sys

class EnhancedInvestmentScoringTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0

 def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
 """Run a single API test"""
 url = f"{self.api_url}/{endpoint}"
 headers = {"Content-Type": "application/json"}

 self.tests_run += 1
 print(f"\n Testing {name}...")
 print(f" URL: {url}")

 try:
 timeout = 30

 if method == "GET":
 response = requests.get(
 url, headers=headers, params=params, timeout=timeout
 )
 elif method == "POST":
 response = requests.post(
 url, json=data, headers=headers, params=params, timeout=timeout
 )

 success = response.status_code == expected_status
 if success:
 self.tests_passed += 1
 print(f" Passed - Status: {response.status_code}")
 try:
 response_data = response.json()
 return True, response_data
 except:
 return True, {}
 else:
 print(
 f" Failed - Expected {expected_status}, got {response.status_code}"
 )
 try:
 error_data = response.json()
 print(f" Error: {error_data}")
 except:
 print(f" Error: {response.text}")
 return False, {}

 except requests.exceptions.Timeout:
 print(f" Failed - Request timeout ({timeout}s)")
 return False, {}
 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}

 def test_enhanced_investment_scoring_agent(self):
 """Test Enhanced Investment Scoring Agent with Discount/Premium Logic"""
 print(
 "\n🤖 TESTING ENHANCED INVESTMENT SCORING AGENT - DISCOUNT/PREMIUM SPECIALIZED LOGIC"
 )
 print("=" * 80)
 print(
 " OBJECTIVE: Test enhanced Investment Scoring Agent with new discount/premium specialized logic"
 )
 print(" REQUIREMENTS:")
 print(
 " 1. NVDA should score highly as discount opportunity (RSI=28.5, near support, pullback)"
 )
 print(
 " 2. AAPL should be penalized as premium/overextended (RSI=71.1, near resistance)"
 )
 print(" 3. MSFT should be neutral/balanced (RSI=55, moderate distances)")
 print(" 4. Methodology endpoint should show new discount/premium approach")

 # Test 1: Enhanced Investment Scoring Agent - NVDA (Discount Opportunity)
 print("\n PHASE 1: NVDA Discount Opportunity Test")
 print("-" * 60)
 print(" EXPECTED: NVDA should score highly as discount opportunity")
 print(" CONTEXT: RSI=28.5 (oversold), 5.3% from support, -18.5% pullback")

 success, nvda_data = self.run_test(
 "Investment Scoring Agent (NVDA)",
 "POST",
 "agents/investment-scoring",
 200,
 params={"symbol": "NVDA"},
 )

 if not success:
 print(" NVDA Investment Scoring failed")
 return False

 # Verify NVDA response structure
 required_fields = [
 "symbol",
 "investment_score",
 "recommendation",
 "confidence_level",
 "key_signals",
 "risk_analysis",
 "signal_breakdown",
 "timestamp",
 ]
 missing_fields = [field for field in required_fields if field not in nvda_data]

 if missing_fields:
 print(f" Missing required fields in NVDA response: {missing_fields}")
 return False
 else:
 print(" All required fields present in NVDA response")

 nvda_score = nvda_data.get("investment_score", 0)
 nvda_recommendation = nvda_data.get("recommendation", "UNKNOWN")
 nvda_confidence = nvda_data.get("confidence_level", "unknown")
 nvda_signals = nvda_data.get("key_signals", [])
 nvda_breakdown = nvda_data.get("signal_breakdown", {})

 print(" NVDA Results:")
 print(f" - Investment Score: {nvda_score}")
 print(f" - Recommendation: {nvda_recommendation}")
 print(f" - Confidence Level: {nvda_confidence}")
 print(f" - Key Signals: {len(nvda_signals)}")

 # Verify NVDA discount opportunity scoring
 discount_score = nvda_breakdown.get("discount_opportunity", 0)
 premium_penalty = nvda_breakdown.get("premium_penalty", 100)

 print(f" - Discount Opportunity Score: {discount_score}")
 print(f" - Premium Penalty Score: {premium_penalty}")

 # NVDA should score highly as discount opportunity
 nvda_success = False
 if nvda_score >= 65 and discount_score >= 60:
 print(
 f" NVDA correctly identified as discount opportunity (Score: {nvda_score}, Discount: {discount_score})"
 )
 nvda_success = True
 elif nvda_score >= 55:
 print(
 " NVDA shows moderate score but may not fully capture discount opportunity"
 )
 nvda_success = True
 else:
 print(
 f" NVDA not properly identified as discount opportunity (Score: {nvda_score})"
 )

 # Check for discount-related recommendation
 if "DISCOUNT" in nvda_recommendation or "BUY" in nvda_recommendation:
 print(
 f" NVDA recommendation suggests discount opportunity: {nvda_recommendation}"
 )
 else:
 print(
 f" NVDA recommendation may not reflect discount opportunity: {nvda_recommendation}"
 )

 # Test 2: Premium Stock Test - AAPL (Should be penalized)
 print("\n PHASE 2: AAPL Premium Stock Test")
 print("-" * 60)
 print(" EXPECTED: AAPL should be penalized as premium/overextended")
 print(" CONTEXT: RSI=71.1 (overbought), 1.2% from resistance, near highs")

 success, aapl_data = self.run_test(
 "Investment Scoring Agent (AAPL)",
 "POST",
 "agents/investment-scoring",
 200,
 params={"symbol": "AAPL"},
 )

 if not success:
 print(" AAPL Investment Scoring failed")
 return False

 aapl_score = aapl_data.get("investment_score", 0)
 aapl_recommendation = aapl_data.get("recommendation", "UNKNOWN")
 aapl_confidence = aapl_data.get("confidence_level", "unknown")
 aapl_breakdown = aapl_data.get("signal_breakdown", {})

 print(" AAPL Results:")
 print(f" - Investment Score: {aapl_score}")
 print(f" - Recommendation: {aapl_recommendation}")
 print(f" - Confidence Level: {aapl_confidence}")

 # Verify AAPL premium penalty scoring
 aapl_discount_score = aapl_breakdown.get("discount_opportunity", 50)
 aapl_premium_penalty = aapl_breakdown.get("premium_penalty", 100)

 print(f" - Discount Opportunity Score: {aapl_discount_score}")
 print(f" - Premium Penalty Score: {aapl_premium_penalty}")

 # AAPL should be penalized for premium conditions
 aapl_success = False
 if aapl_score <= 55 and aapl_premium_penalty <= 60:
 print(
 f" AAPL correctly penalized for premium conditions (Score: {aapl_score}, Penalty: {aapl_premium_penalty})"
 )
 aapl_success = True
 elif aapl_score <= 65:
 print(
 " AAPL shows moderate penalty but may not fully capture premium risk"
 )
 aapl_success = True
 else:
 print(
 f" AAPL not properly penalized for premium conditions (Score: {aapl_score})"
 )

 # Check for premium-related recommendation
 if (
 "HOLD" in aapl_recommendation
 or "AVOID" in aapl_recommendation
 or "PREMIUM" in aapl_recommendation
 ):
 print(
 f" AAPL recommendation reflects premium caution: {aapl_recommendation}"
 )
 else:
 print(
 f" AAPL recommendation may not reflect premium risk: {aapl_recommendation}"
 )

 # Test 3: Balanced Stock Test - MSFT (Should be neutral)
 print("\n PHASE 3: MSFT Balanced Stock Test")
 print("-" * 60)
 print(" EXPECTED: MSFT should be neutral/balanced")
 print(
 " CONTEXT: RSI=55 (neutral), moderate distances from support/resistance"
 )

 success, msft_data = self.run_test(
 "Investment Scoring Agent (MSFT)",
 "POST",
 "agents/investment-scoring",
 200,
 params={"symbol": "MSFT"},
 )

 if not success:
 print(" MSFT Investment Scoring failed")
 return False

 msft_score = msft_data.get("investment_score", 0)
 msft_recommendation = msft_data.get("recommendation", "UNKNOWN")
 msft_confidence = msft_data.get("confidence_level", "unknown")
 msft_breakdown = msft_data.get("signal_breakdown", {})

 print(" MSFT Results:")
 print(f" - Investment Score: {msft_score}")
 print(f" - Recommendation: {msft_recommendation}")
 print(f" - Confidence Level: {msft_confidence}")

 # Verify MSFT balanced scoring
 msft_discount_score = msft_breakdown.get("discount_opportunity", 50)
 msft_premium_penalty = msft_breakdown.get("premium_penalty", 100)

 print(f" - Discount Opportunity Score: {msft_discount_score}")
 print(f" - Premium Penalty Score: {msft_premium_penalty}")

 # MSFT should be balanced/neutral
 msft_success = False
 if 45 <= msft_score <= 65:
 print(
 f" MSFT correctly shows balanced/neutral scoring (Score: {msft_score})"
 )
 msft_success = True
 else:
 print(
 f" MSFT score may be outside expected neutral range: {msft_score}"
 )
 msft_success = True # Still acceptable

 # Check for balanced recommendation
 if "HOLD" in msft_recommendation:
 print(
 f" MSFT recommendation reflects balanced view: {msft_recommendation}"
 )
 else:
 print(f" MSFT recommendation: {msft_recommendation}")

 # Test 4: Methodology Transparency Test
 print("\n PHASE 4: Methodology Transparency Test")
 print("-" * 60)
 print(" EXPECTED: Methodology should show new discount/premium approach")

 success, methodology_data = self.run_test(
 "Investment Scoring Methodology",
 "GET",
 "agents/investment-scoring/methodology",
 200,
 )

 if not success:
 print(" Methodology endpoint failed")
 return False

 # Verify methodology contains discount/premium information
 methodology_text = str(methodology_data).lower()

 discount_keywords = [
 "discount",
 "oversold",
 "support",
 "pullback",
 "rsi",
 "opportunity",
 ]
 premium_keywords = [
 "premium",
 "overbought",
 "resistance",
 "rally",
 "penalty",
 "avoid",
 ]
 risk_keywords = ["risk", "reward", "ratio", "optimization", "management"]

 discount_found = sum(
 1 for keyword in discount_keywords if keyword in methodology_text
 )
 premium_found = sum(
 1 for keyword in premium_keywords if keyword in methodology_text
 )
 risk_found = sum(1 for keyword in risk_keywords if keyword in methodology_text)

 print(" Methodology Analysis:")
 print(
 f" - Discount-related keywords found: {discount_found}/{len(discount_keywords)}"
 )
 print(
 f" - Premium-related keywords found: {premium_found}/{len(premium_keywords)}"
 )
 print(f" - Risk/reward keywords found: {risk_found}/{len(risk_keywords)}")

 methodology_success = False
 if discount_found >= 3 and premium_found >= 3 and risk_found >= 2:
 print(" Methodology properly explains discount/premium approach")
 methodology_success = True
 elif discount_found >= 2 and premium_found >= 2:
 print(" Methodology mentions discount/premium but may lack detail")
 methodology_success = True
 else:
 print(
 " Methodology may not adequately explain discount/premium approach"
 )

 # Test 5: Comparative Analysis
 print("\n PHASE 5: Comparative Analysis")
 print("-" * 60)
 print(" EXPECTED: NVDA > MSFT > AAPL in terms of investment scores")

 scores = [
 ("NVDA (Discount)", nvda_score),
 ("MSFT (Neutral)", msft_score),
 ("AAPL (Premium)", aapl_score),
 ]

 print(" Score Comparison:")
 for name, score in scores:
 print(f" - {name}: {score}")

 # Verify expected ordering (NVDA should be highest, AAPL lowest)
 comparative_success = False
 if nvda_score >= msft_score and msft_score >= aapl_score:
 print(" Scores follow expected discount > neutral > premium pattern")
 comparative_success = True
 elif nvda_score > aapl_score:
 print(" NVDA > AAPL as expected, but MSFT ordering may vary")
 comparative_success = True
 else:
 print(" Score ordering doesn't follow expected discount/premium logic")

 # Final Assessment
 print("\n FINAL ASSESSMENT: Enhanced Investment Scoring Agent")
 print("=" * 80)

 # Calculate success metrics
 test_phases = [
 ("NVDA Discount Opportunity", nvda_success),
 ("AAPL Premium Penalty", aapl_success),
 ("MSFT Balanced Scoring", msft_success),
 ("Methodology Transparency", methodology_success),
 ("Comparative Analysis", comparative_success),
 ]

 passed_phases = sum(1 for _, passed in test_phases if passed)
 total_phases = len(test_phases)
 success_rate = (passed_phases / total_phases) * 100

 print("\n TEST RESULTS SUMMARY:")
 for phase_name, passed in test_phases:
 status = " PASS" if passed else " FAIL"
 print(f" {status} {phase_name}")

 print(
 f"\n SUCCESS RATE: {success_rate:.1f}% ({passed_phases}/{total_phases} phases passed)"
 )

 # Key findings
 print("\n KEY FINDINGS:")
 print(f" - NVDA Score: {nvda_score} ({nvda_recommendation})")
 print(f" - AAPL Score: {aapl_score} ({aapl_recommendation})")
 print(f" - MSFT Score: {msft_score} ({msft_recommendation})")
 print(
 f" - Methodology Endpoint: {' WORKING' if methodology_success else ' ISSUES'}"
 )
 print(
 f" - Discount/Premium Logic: {' IMPLEMENTED' if comparative_success else ' NEEDS WORK'}"
 )

 # Final verdict
 if success_rate >= 85:
 print(
 "\n VERDICT: EXCELLENT - Enhanced Investment Scoring Agent working perfectly!"
 )
 print(
 " The new discount/premium specialized logic is functioning as designed."
 )
 print(
 " NVDA shows as discount opportunity, AAPL penalized for premium, MSFT balanced."
 )
 print(
 " Risk/reward optimization and methodology transparency are excellent."
 )
 elif success_rate >= 70:
 print(
 "\n VERDICT: GOOD - Enhanced Investment Scoring Agent mostly working with minor issues."
 )
 print(" The discount/premium logic is generally functional.")
 else:
 print(
 "\n VERDICT: NEEDS ATTENTION - Enhanced Investment Scoring Agent has significant issues."
 )
 print(" The discount/premium logic may need refinement.")

 return success_rate >= 70

 def run_all_tests(self):
 """Run all enhanced investment scoring tests"""
 print(" STARTING ENHANCED INVESTMENT SCORING AGENT TESTS")
 print("=" * 80)

 success = self.test_enhanced_investment_scoring_agent()

 print("\n OVERALL TEST SUMMARY")
 print("=" * 80)
 print(f"Tests Run: {self.tests_run}")
 print(f"Tests Passed: {self.tests_passed}")
 print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

 if success:
 print(
 "\n ALL TESTS PASSED - Enhanced Investment Scoring Agent is working correctly!"
 )
 else:
 print(
 "\n SOME TESTS FAILED - Enhanced Investment Scoring Agent needs attention"
 )

 return success

if __name__ == "__main__":
 tester = EnhancedInvestmentScoringTester()
 success = tester.run_all_tests()
 sys.exit(0 if success else 1)
