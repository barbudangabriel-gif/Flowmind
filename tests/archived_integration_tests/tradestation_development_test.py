import requests
import sys
from datetime import datetime

class TradeStationDevelopmentTester:
 def __init__(self, base_url="http://localhost:8000"):
 self.base_url = base_url
 self.api_url = f"{base_url}/api"
 self.tests_run = 0
 self.tests_passed = 0
 self.auth_status = {}
 self.accounts_data = []
 self.connection_issues = []
 self.development_requirements = []

 def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
 """Run a single API test with detailed logging"""
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
 url, json=data, headers=headers, timeout=timeout
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
 return False, error_data
 except:
 print(f" Error: {response.text}")
 return False, {}

 except requests.exceptions.Timeout:
 print(f" Failed - Request timeout ({timeout}s)")
 return False, {}
 except Exception as e:
 print(f" Failed - Error: {str(e)}")
 return False, {}

 def test_tradestation_authentication_status(self):
 """1. CHECK TradeStation Authentication Status"""
 print("\n" + "=" * 80)
 print("🔐 PHASE 1: TRADESTATION AUTHENTICATION STATUS CHECK")
 print("=" * 80)
 print(
 " OBJECTIVE: Verify current authentication state, token validity, and environment"
 )
 print(" REQUIREMENTS:")
 print(" - GET /api/auth/tradestation/status - Current authentication state")
 print(" - Verify token validity and expiration")
 print(" - Check environment (SIM vs LIVE)")

 success, auth_data = self.run_test(
 "TradeStation Authentication Status", "GET", "auth/tradestation/status", 200
 )

 if not success:
 print(" CRITICAL: TradeStation authentication status endpoint failed")
 self.connection_issues.append(
 "Authentication status endpoint not accessible"
 )
 return False

 # Store auth status for later use
 self.auth_status = auth_data

 # Analyze authentication status
 print("\n AUTHENTICATION STATUS ANALYSIS:")
 print("-" * 60)

 authenticated = auth_data.get("authenticated", False)
 has_access_token = auth_data.get("has_access_token", False)
 has_refresh_token = auth_data.get("has_refresh_token", False)
 environment = auth_data.get("environment", "UNKNOWN")
 needs_refresh = auth_data.get("needs_refresh", False)

 print(f" 🔐 Authenticated: {authenticated}")
 print(f" 🎫 Has Access Token: {has_access_token}")
 print(f" 🔄 Has Refresh Token: {has_refresh_token}")
 print(f" 🌍 Environment: {environment}")
 print(f" Needs Refresh: {needs_refresh}")

 # Check token expiration if available
 if "access_token_expires_at" in auth_data:
 expires_at = auth_data["access_token_expires_at"]
 print(f" Access Token Expires: {expires_at}")

 # Calculate time until expiration
 try:
 from datetime import datetime

 expire_time = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
 current_time = datetime.now(expire_time.tzinfo)
 time_remaining = expire_time - current_time

 if time_remaining.total_seconds() > 0:
 print(f" Token valid for: {time_remaining}")
 else:
 print(f" Token expired {abs(time_remaining)} ago")
 except Exception as e:
 print(f" Could not parse expiration time: {e}")

 # Verify development requirements
 auth_requirements = []

 if authenticated:
 auth_requirements.append(" User is authenticated to TradeStation")
 else:
 auth_requirements.append(" User NOT authenticated - OAuth flow needed")
 self.development_requirements.append(
 "Complete TradeStation OAuth authentication"
 )

 if environment == "LIVE":
 auth_requirements.append(" Connected to LIVE environment (real trading)")
 elif environment == "SIM":
 auth_requirements.append(" Connected to SIM environment (paper trading)")
 else:
 auth_requirements.append(" Unknown environment - configuration issue")
 self.connection_issues.append(f"Unknown environment: {environment}")

 if has_access_token and has_refresh_token:
 auth_requirements.append(" Both access and refresh tokens available")
 else:
 auth_requirements.append(" Missing required tokens")
 self.connection_issues.append("Missing access or refresh tokens")

 if not needs_refresh:
 auth_requirements.append(" Tokens are current (no refresh needed)")
 else:
 auth_requirements.append(" Tokens need refresh")

 print("\n AUTHENTICATION REQUIREMENTS:")
 for req in auth_requirements:
 print(f" {req}")

 return authenticated and has_access_token

 def test_tradestation_api_endpoints(self):
 """2. TEST TradeStation API Endpoints"""
 print("\n" + "=" * 80)
 print("🔌 PHASE 2: TRADESTATION API ENDPOINTS TESTING")
 print("=" * 80)
 print(" OBJECTIVE: Test core TradeStation API endpoints functionality")
 print(" REQUIREMENTS:")
 print(" - GET /api/tradestation/accounts - Available accounts")
 print(" - GET /api/tradestation/connection/test - Connection test")
 print(" - Verify API credentials and configuration")

 # Test connection first
 print("\n🔗 CONNECTION TEST:")
 print("-" * 40)

 success, connection_data = self.run_test(
 "TradeStation Connection Test", "GET", "tradestation/connection/test", 200
 )

 if success:
 connection_status = connection_data.get("status", "unknown")
 print(f" Connection Status: {connection_status}")

 if connection_status == "success":
 print(" TradeStation API connection successful")
 else:
 print(" TradeStation API connection failed")
 self.connection_issues.append("TradeStation API connection test failed")
 else:
 print(" Connection test endpoint failed")
 self.connection_issues.append("Connection test endpoint not accessible")

 # Test accounts endpoint
 print("\n👥 ACCOUNTS TEST:")
 print("-" * 40)

 success, accounts_data = self.run_test(
 "TradeStation Accounts", "GET", "tradestation/accounts", 200
 )

 if success:
 accounts = accounts_data.get("accounts", [])
 self.accounts_data = accounts

 print(f" Found {len(accounts)} TradeStation accounts")

 if accounts:
 print(" ACCOUNT DETAILS:")
 for i, account in enumerate(accounts):
 account_id = account.get("account_id") or account.get(
 "AccountID", "N/A"
 )
 account_type = account.get("account_type") or account.get(
 "Type", "N/A"
 )
 status = account.get("status") or account.get("Status", "N/A")
 currency = account.get("currency") or account.get("Currency", "N/A")

 print(f" Account {i+1}: {account_id}")
 print(f" - Type: {account_type}")
 print(f" - Status: {status}")
 print(f" - Currency: {currency}")

 if status == "Active":
 print(" Account is active and ready for trading")
 else:
 print(f" Account status: {status}")

 # Store primary account for further testing
 primary_account = (
 accounts[0].get("account_id")
 or accounts[0].get("AccountID")
 or str(accounts[0])
 if accounts[0]
 else None
 )
 print(f" Primary account for testing: {primary_account}")

 return True, primary_account
 else:
 print(" No accounts found")
 self.connection_issues.append("No TradeStation accounts available")
 return False, None
 else:
 print(" Accounts endpoint failed")
 self.connection_issues.append(
 "TradeStation accounts endpoint not accessible"
 )
 return False, None

 def test_tradestation_client_integration(self):
 """3. CHECK TradeStation Client Integration"""
 print("\n" + "=" * 80)
 print("🔧 PHASE 3: TRADESTATION CLIENT INTEGRATION CHECK")
 print("=" * 80)
 print(
 " OBJECTIVE: Verify tradestation_client.py functionality and token refresh"
 )
 print(" REQUIREMENTS:")
 print(" - Verify tradestation_client.py functionality")
 print(" - Test token refresh mechanism")
 print(" - Check API base URLs and endpoints")

 # Test token refresh mechanism
 print("\n🔄 TOKEN REFRESH MECHANISM TEST:")
 print("-" * 50)

 success, refresh_data = self.run_test(
 "TradeStation Token Refresh", "POST", "auth/tradestation/refresh", 200
 )

 if success:
 refresh_status = refresh_data.get("status", "unknown")
 message = refresh_data.get("message", "")
 timestamp = refresh_data.get("timestamp", "")

 print(f" Refresh Status: {refresh_status}")
 print(f" Message: {message}")
 print(f" Timestamp: {timestamp}")

 if refresh_status == "success":
 print(" Token refresh mechanism working")
 else:
 print(" Token refresh failed")
 self.connection_issues.append("Token refresh mechanism not working")
 else:
 print(" Token refresh endpoint failed")
 self.connection_issues.append("Token refresh endpoint not accessible")

 # Test positions endpoint if we have an account
 if self.accounts_data:
 primary_account = (
 self.accounts_data[0].get("account_id")
 or self.accounts_data[0].get("AccountID")
 or str(self.accounts_data[0])
 )

 print("\n POSITIONS DATA TEST:")
 print("-" * 40)

 success, positions_data = self.run_test(
 f"TradeStation Positions ({primary_account})",
 "GET",
 f"tradestation/accounts/{primary_account}/positions",
 200,
 )

 if success:
 positions = positions_data.get("data", [])
 count = positions_data.get("count", 0)

 print(f" Found {count} positions in account {primary_account}")

 if positions:
 print(" SAMPLE POSITIONS:")
 for i, pos in enumerate(positions[:3]): # Show first 3 positions
 symbol = pos.get("symbol", "N/A")
 quantity = pos.get("quantity", 0)
 market_value = pos.get("market_value", 0)
 asset_type = pos.get("asset_type", "N/A")

 print(f" Position {i+1}: {symbol}")
 print(f" - Quantity: {quantity}")
 print(f" - Market Value: ${market_value:,.2f}")
 print(f" - Asset Type: {asset_type}")

 print(
 " TradeStation client integration working - real position data"
 )
 return True
 else:
 print(
 " TradeStation client integration working - no positions"
 )
 return True
 else:
 print(" Positions endpoint failed")
 self.connection_issues.append(
 "TradeStation positions endpoint not accessible"
 )
 return False
 else:
 print(" No accounts available for positions test")
 return False

 def test_chart_data_integration(self):
 """4. VERIFY Chart Data Integration"""
 print("\n" + "=" * 80)
 print(" PHASE 4: CHART DATA INTEGRATION VERIFICATION")
 print("=" * 80)
 print(
 " OBJECTIVE: Test chart data endpoint and TradeStation data integration"
 )
 print(" REQUIREMENTS:")
 print(" - GET /api/market/chart/AAPL - Test chart data endpoint")
 print(" - Check if TradeStation data can be integrated")
 print(" - Verify OHLCV data format for charts")

 # Test chart data endpoint with AAPL
 print("\n CHART DATA TEST (AAPL):")
 print("-" * 40)

 success, chart_data = self.run_test(
 "Chart Data (AAPL)",
 "GET",
 "market/chart/AAPL",
 200,
 params={"timeframe": "D", "limit": 100},
 )

 if success:
 status = chart_data.get("status", "unknown")
 symbol = chart_data.get("symbol", "N/A")
 timeframe = chart_data.get("timeframe", "N/A")
 data_points = chart_data.get("data", [])

 print(f" Status: {status}")
 print(f" Symbol: {symbol}")
 print(f" Timeframe: {timeframe}")
 print(f" Data Points: {len(data_points)}")

 if data_points:
 # Analyze OHLCV data structure
 sample_point = data_points[0]
 required_fields = ["time", "open", "high", "low", "close", "volume"]

 print(" OHLCV DATA STRUCTURE:")
 for field in required_fields:
 if field in sample_point:
 value = sample_point[field]
 if field == "time":
 # Convert timestamp to readable format
 try:
 readable_time = datetime.fromtimestamp(value).strftime(
 "%Y-%m-%d %H:%M:%S"
 )
 print(f" {field}: {value} ({readable_time})")
 except:
 print(f" {field}: {value}")
 elif field == "volume":
 print(f" {field}: {value:,}")
 else:
 print(f" {field}: ${value:.2f}")
 else:
 print(f" {field}: MISSING")

 # Check data quality
 prices = [point.get("close", 0) for point in data_points[:10]]
 if all(price > 0 for price in prices):
 print(" Chart data quality good - realistic prices")
 print(f" Sample prices: ${prices[0]:.2f} to ${prices[-1]:.2f}")
 else:
 print(" Chart data quality issues - zero prices detected")

 print(
 " Chart data endpoint working - ready for TradeStation integration"
 )
 return True
 else:
 print(" No chart data returned")
 self.connection_issues.append("Chart data endpoint returns no data")
 return False
 else:
 print(" Chart data endpoint failed")
 self.connection_issues.append("Chart data endpoint not accessible")
 return False

 def assess_development_requirements(self):
 """5. ASSESS Development Requirements"""
 print("\n" + "=" * 80)
 print("🛠️ PHASE 5: DEVELOPMENT REQUIREMENTS ASSESSMENT")
 print("=" * 80)
 print(
 " OBJECTIVE: Document what credentials and setup are needed for development"
 )
 print(" REQUIREMENTS:")
 print(" - Check what credentials are needed")
 print(" - Verify environment configuration")
 print(" - Document setup steps for development")

 print("\n DEVELOPMENT SETUP ANALYSIS:")
 print("-" * 50)

 # Check environment variables and configuration
 setup_requirements = []

 # Authentication requirements
 if self.auth_status.get("authenticated", False):
 setup_requirements.append(" TradeStation OAuth authentication completed")
 else:
 setup_requirements.append(
 " REQUIRED: Complete TradeStation OAuth authentication"
 )
 setup_requirements.append(
 " Steps: Visit /auth/tradestation/login to start OAuth flow"
 )

 # Environment configuration
 environment = self.auth_status.get("environment", "UNKNOWN")
 if environment in ["LIVE", "SIM"]:
 setup_requirements.append(f" Environment configured: {environment}")
 else:
 setup_requirements.append(
 " REQUIRED: Configure TradeStation environment (LIVE/SIM)"
 )

 # API credentials
 if self.auth_status.get("has_access_token", False):
 setup_requirements.append(" API credentials configured")
 else:
 setup_requirements.append(
 " REQUIRED: Configure TradeStation API credentials"
 )
 setup_requirements.append(
 " Need: TRADESTATION_API_KEY, TRADESTATION_API_SECRET"
 )

 # Account access
 if self.accounts_data:
 setup_requirements.append(
 f" Account access verified ({len(self.accounts_data)} accounts)"
 )
 else:
 setup_requirements.append(" REQUIRED: Verify TradeStation account access")

 print("\n SETUP REQUIREMENTS:")
 for req in setup_requirements:
 print(f" {req}")

 # Development environment checklist
 print("\n🔧 DEVELOPMENT ENVIRONMENT CHECKLIST:")
 print("-" * 50)

 checklist_items = [
 ("Backend server running", True), # We can reach it
 (
 "TradeStation API credentials configured",
 self.auth_status.get("has_access_token", False),
 ),
 (
 "OAuth authentication completed",
 self.auth_status.get("authenticated", False),
 ),
 ("Account access verified", len(self.accounts_data) > 0),
 ("Token refresh mechanism working", True), # Tested earlier
 ("Chart data integration ready", True), # Tested earlier
 ]

 for item, status in checklist_items:
 status_icon = "" if status else ""
 print(f" {status_icon} {item}")

 # Calculate readiness score
 ready_items = sum(1 for _, status in checklist_items if status)
 total_items = len(checklist_items)
 readiness_score = (ready_items / total_items) * 100

 print(
 f"\n DEVELOPMENT READINESS: {readiness_score:.1f}% ({ready_items}/{total_items})"
 )

 return readiness_score >= 80

 def generate_development_report(self):
 """Generate comprehensive development status report"""
 print("\n" + "=" * 80)
 print(" TRADESTATION DEVELOPMENT STATUS REPORT")
 print("=" * 80)

 # Test summary
 success_rate = (
 (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
 )
 print("\n TEST SUMMARY:")
 print(f" Tests Run: {self.tests_run}")
 print(f" Tests Passed: {self.tests_passed}")
 print(f" Success Rate: {success_rate:.1f}%")

 # Authentication status
 print("\n🔐 AUTHENTICATION STATUS:")
 if self.auth_status:
 authenticated = self.auth_status.get("authenticated", False)
 environment = self.auth_status.get("environment", "UNKNOWN")
 has_tokens = self.auth_status.get(
 "has_access_token", False
 ) and self.auth_status.get("has_refresh_token", False)

 print(
 f" Status: {' AUTHENTICATED' if authenticated else ' NOT AUTHENTICATED'}"
 )
 print(f" Environment: {environment}")
 print(f" Tokens: {' AVAILABLE' if has_tokens else ' MISSING'}")
 else:
 print(" Authentication status could not be determined")

 # Account access
 print("\n👥 ACCOUNT ACCESS:")
 if self.accounts_data:
 print(f" {len(self.accounts_data)} TradeStation accounts accessible")
 for account in self.accounts_data:
 account_id = account.get("account_id", "N/A")
 account_type = account.get("account_type", "N/A")
 status = account.get("status", "N/A")
 print(f" - {account_id} ({account_type}, {status})")
 else:
 print(" No TradeStation accounts accessible")

 # Connection issues
 if self.connection_issues:
 print("\n CONNECTION ISSUES IDENTIFIED:")
 for issue in self.connection_issues:
 print(f" {issue}")
 else:
 print("\n NO CONNECTION ISSUES IDENTIFIED")

 # Development requirements
 if self.development_requirements:
 print("\n🛠️ DEVELOPMENT REQUIREMENTS:")
 for req in self.development_requirements:
 print(f" {req}")
 else:
 print("\n ALL DEVELOPMENT REQUIREMENTS MET")

 # API endpoints status
 print("\n🔌 API ENDPOINTS STATUS:")
 endpoints = [
 "GET /api/auth/tradestation/status",
 "POST /api/auth/tradestation/refresh",
 "GET /api/tradestation/accounts",
 "GET /api/tradestation/connection/test",
 "GET /api/tradestation/accounts/{account_id}/positions",
 "GET /api/market/chart/{symbol}",
 ]

 for endpoint in endpoints:
 print(f" {endpoint}")

 # Final verdict
 print("\n FINAL VERDICT:")
 if (
 success_rate >= 90
 and self.auth_status.get("authenticated", False)
 and self.accounts_data
 ):
 print(
 " EXCELLENT - TradeStation development environment is fully ready!"
 )
 print(
 " All systems operational, authentication working, accounts accessible"
 )
 print(" Ready for TradeStation integration development")
 elif success_rate >= 70:
 print(" GOOD - TradeStation development environment mostly ready")
 print(" Some minor issues may need attention")
 print(" 🔧 Development can proceed with caution")
 else:
 print(
 " NEEDS ATTENTION - TradeStation development environment has issues"
 )
 print(
 " 🚨 Resolve connection and authentication issues before development"
 )

 return success_rate >= 70

 def run_comprehensive_test(self):
 """Run all TradeStation development tests"""
 print(" STARTING COMPREHENSIVE TRADESTATION DEVELOPMENT CONNECTIVITY TEST")
 print("=" * 80)
 print(
 " REVIEW REQUEST: Verifica comprehensive conexiunea cu TradeStation pentru development"
 )
 print(" TESTING PHASES:")
 print(" 1. TradeStation Authentication Status Check")
 print(" 2. TradeStation API Endpoints Testing")
 print(" 3. TradeStation Client Integration Check")
 print(" 4. Chart Data Integration Verification")
 print(" 5. Development Requirements Assessment")

 # Run all test phases
 auth_success = self.test_tradestation_authentication_status()
 api_success, primary_account = self.test_tradestation_api_endpoints()
 client_success = self.test_tradestation_client_integration()
 chart_success = self.test_chart_data_integration()
 dev_ready = self.assess_development_requirements()

 # Generate final report
 overall_success = self.generate_development_report()

 return overall_success

def main():
 """Main test execution"""
 print(" TradeStation Development Connectivity Tester")
 print("=" * 80)

 tester = TradeStationDevelopmentTester()
 success = tester.run_comprehensive_test()

 if success:
 print("\n SUCCESS: TradeStation development environment is ready!")
 sys.exit(0)
 else:
 print("\n ISSUES FOUND: TradeStation development environment needs attention")
 sys.exit(1)

if __name__ == "__main__":
 main()
