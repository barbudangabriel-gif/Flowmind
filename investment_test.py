import requests
import sys
from datetime import datetime

class InvestmentScoringTester:
    def __init__(self, base_url="https://stockpulse-9.preview.emergentagent.com"):
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

    def test_investment_scoring_endpoints(self):
        """Test Investment Scoring System endpoints"""
        print("\n🎯 Testing Investment Scoring System")
        
        # Test top investment picks - MAIN FOCUS
        success, top_picks_data = self.run_test("Investment Top Picks", "GET", "investments/top-picks", 200, params={"limit": 10})
        if success and 'recommendations' in top_picks_data:
            recommendations = top_picks_data['recommendations']
            print(f"   📊 Found {len(recommendations)} top investment picks")
            
            if recommendations:
                first_pick = recommendations[0]
                print(f"   🥇 #1 Pick: {first_pick.get('symbol', 'N/A')} - Score: {first_pick.get('total_score', 'N/A')} - Rating: {first_pick.get('rating', 'N/A')}")
                print(f"   🛡️  Risk Level: {first_pick.get('risk_level', 'N/A')}")
                
                # Check required fields
                required_fields = ['symbol', 'total_score', 'rating', 'risk_level', 'key_strengths', 'key_risks']
                missing_fields = [field for field in required_fields if field not in first_pick]
                if missing_fields:
                    print(f"   ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
            else:
                print(f"   ⚠️  No recommendations found in response")
        else:
            print(f"   ❌ Failed to get top picks or missing 'recommendations' field")
        
        # Test individual stock scoring - AAPL
        success, aapl_score = self.run_test("Investment Score (AAPL)", "GET", "investments/score/AAPL", 200)
        if success:
            print(f"   📈 AAPL Score: {aapl_score.get('total_score', 'N/A')}")
            print(f"   📊 AAPL Rating: {aapl_score.get('rating', 'N/A')}")
            print(f"   🛡️  AAPL Risk: {aapl_score.get('risk_level', 'N/A')}")
            
            individual_scores = aapl_score.get('individual_scores', {})
            if individual_scores:
                print(f"   📋 Score Breakdown: {len(individual_scores)} metrics")
        
        # Test sector leaders
        success, sector_data = self.run_test("Sector Leaders (Technology)", "GET", "investments/sector-leaders", 200, params={"sector": "Technology"})
        if success and 'leaders' in sector_data:
            leaders = sector_data['leaders']
            print(f"   🏢 Found {len(leaders)} Technology sector leaders")
            if leaders:
                top_leader = leaders[0]
                print(f"   🥇 Top Tech Leader: {top_leader.get('symbol', 'N/A')} - Score: {top_leader.get('total_score', 'N/A')}")
        
        # Test risk analysis
        success, risk_data = self.run_test("Risk Analysis", "GET", "investments/risk-analysis", 200)
        if success and 'risk_categories' in risk_data:
            risk_categories = risk_data['risk_categories']
            print(f"   📊 Risk Categories: {list(risk_categories.keys())}")
            
            for risk_level, stocks in risk_categories.items():
                print(f"   {risk_level} Risk: {len(stocks)} stocks")
        
        return success

def main():
    print("🚀 Starting Investment Scoring API Tests")
    print("=" * 50)
    
    tester = InvestmentScoringTester()
    
    # Test Investment Scoring System
    tester.test_investment_scoring_endpoints()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Investment Scoring tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())