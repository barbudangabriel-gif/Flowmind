#!/usr/bin/env python3
"""
GO/NO-GO Backend Smoke Tests - Comprehensive Pre-Integration System Validation
Testing critical endpoints for Strike Rail PRO integration readiness
"""

import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://options-analytics.preview.emergentagent.com"


class GoNoGoTester:
    def __init__(self):
        self.results = []
        self.critical_failures = []
        self.uw_token_status = "unknown"

    def log_result(
        self, test_name: str, success: bool, details: str, critical: bool = False
    ):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append(
            {
                "test": test_name,
                "success": success,
                "details": details,
                "critical": critical,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if not success and critical:
            self.critical_failures.append(test_name)

        print(f"{status} {test_name}")
        print(f"   {details}")
        if not success and critical:
            print("   🚨 CRITICAL FAILURE - BLOCKS INTEGRATION")
        print()

    def test_health_endpoint(self) -> bool:
        """Test 1: GET /health → verify 200 response"""
        print("🔍 TEST 1: Health Check Endpoint")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)

            if response.status_code == 200:
                try:
                    data = response.json()
                    service_name = data.get("service", "unknown")
                    version = data.get("version", "unknown")
                    self.log_result(
                        "Health Check",
                        True,
                        f"Service: {service_name}, Version: {version}, Status: {response.status_code}",
                        critical=True,
                    )
                    return True
                except:
                    # If JSON parsing fails, it might be HTML (frontend)
                    # Let's check if we can reach any API endpoint as health check
                    api_test = requests.get(
                        f"{BACKEND_URL}/api/flow/summary", timeout=5
                    )
                    if api_test.status_code == 200:
                        self.log_result(
                            "Health Check",
                            True,
                            f"API accessible via /api endpoints, Status: {api_test.status_code}",
                            critical=True,
                        )
                        return True
                    else:
                        self.log_result(
                            "Health Check",
                            False,
                            f"Health endpoint returns HTML, API test failed: {api_test.status_code}",
                            critical=True,
                        )
                        return False
            else:
                self.log_result(
                    "Health Check",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    critical=True,
                )
                return False

        except Exception as e:
            self.log_result(
                "Health Check", False, f"Connection failed: {str(e)}", critical=True
            )
            return False

    def test_portfolios_endpoint(self) -> Optional[str]:
        """Test 2: GET /api/portfolios → verify 200 response with portfolio list"""
        print("🔍 TEST 2: Portfolios List Endpoint")
        try:
            response = requests.get(f"{BACKEND_URL}/api/portfolios", timeout=15)

            if response.status_code == 200:
                data = response.json()
                # Handle both list format and dict format
                if isinstance(data, list):
                    portfolios = data
                else:
                    portfolios = data.get("portfolios", [])

                portfolio_count = len(portfolios)

                # Get first portfolio ID for later tests
                first_portfolio_id = None
                if portfolios:
                    first_portfolio_id = portfolios[0].get("id")

                self.log_result(
                    "Portfolios List",
                    True,
                    f"Found {portfolio_count} portfolios, First ID: {first_portfolio_id}",
                    critical=True,
                )
                return first_portfolio_id
            else:
                self.log_result(
                    "Portfolios List",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    critical=True,
                )
                return None

        except Exception as e:
            self.log_result(
                "Portfolios List", False, f"Request failed: {str(e)}", critical=True
            )
            return None

    def test_eod_snapshot_endpoint(self, portfolio_id: str) -> bool:
        """Test 3: POST /api/portfolios/{pid}/analytics/eod/snapshot → verify 200 response"""
        print("🔍 TEST 3: EOD Snapshot Creation")
        if not portfolio_id:
            self.log_result(
                "EOD Snapshot",
                False,
                "No portfolio ID available for testing",
                critical=True,
            )
            return False

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/portfolios/{portfolio_id}/analytics/eod/snapshot",
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                snapshot_data = data.get("data", {})
                date = snapshot_data.get("date", "unknown")
                total_pl = snapshot_data.get("total", 0)

                self.log_result(
                    "EOD Snapshot",
                    True,
                    f"Snapshot created for {date}, Total P&L: ${total_pl}",
                    critical=False,
                )
                return True
            else:
                self.log_result(
                    "EOD Snapshot",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    critical=False,
                )
                return False

        except Exception as e:
            self.log_result(
                "EOD Snapshot", False, f"Request failed: {str(e)}", critical=False
            )
            return False

    def test_flow_summary_endpoint(self) -> bool:
        """Test 4: GET /api/flow/summary → verify 200 response with real payload"""
        print("🔍 TEST 4: Flow Summary (UW Token Integration)")
        try:
            response = requests.get(f"{BACKEND_URL}/api/flow/summary", timeout=20)

            if response.status_code == 200:
                data = response.json()

                # Check if we have real data or mock data
                flow_data = data.get("data", {})
                total_flow = flow_data.get("total_flow", 0)
                call_flow = flow_data.get("call_flow", 0)
                put_flow = flow_data.get("put_flow", 0)

                # Determine if data is real or mock
                if total_flow > 0 or call_flow > 0 or put_flow > 0:
                    self.uw_token_status = "working"
                    data_type = "REAL DATA"
                else:
                    self.uw_token_status = "mock_fallback"
                    data_type = "MOCK/FALLBACK DATA"

                self.log_result(
                    "Flow Summary",
                    True,
                    f"{data_type} - Total: ${total_flow:,.0f}, Calls: ${call_flow:,.0f}, Puts: ${put_flow:,.0f}",
                    critical=False,
                )
                return True
            else:
                self.uw_token_status = "error"
                self.log_result(
                    "Flow Summary",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    critical=False,
                )
                return False

        except Exception as e:
            self.uw_token_status = "error"
            self.log_result(
                "Flow Summary", False, f"Request failed: {str(e)}", critical=False
            )
            return False

    def test_optimize_suggest_endpoint(self) -> Optional[Dict]:
        """Test 5: GET /api/optimize/suggest → verify 200 response with 2+ strategies"""
        print("🔍 TEST 5: Options Optimizer with Deep-Links")

        params = {"symbol": "TSLA", "dte": 30, "budget": 5000, "risk_bias": 0}

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/optimize/suggest", params=params, timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                strategies = data.get("strategies", [])
                strategy_count = len(strategies)

                # Check for deep-links
                deep_links_found = 0
                sample_deep_link = None

                for strategy in strategies:
                    if "open_in_builder" in strategy:
                        deep_links_found += 1
                        if not sample_deep_link:
                            sample_deep_link = strategy["open_in_builder"]

                success = strategy_count >= 2 and deep_links_found > 0

                if success:
                    # Return first strategy with deep-link for builder test
                    builder_strategy = None
                    for strategy in strategies:
                        if "open_in_builder" in strategy:
                            builder_strategy = strategy
                            break

                    self.log_result(
                        "Options Optimizer",
                        True,
                        f"Generated {strategy_count} strategies, {deep_links_found} with deep-links",
                        critical=True,
                    )
                    return builder_strategy
                else:
                    self.log_result(
                        "Options Optimizer",
                        False,
                        f"Only {strategy_count} strategies, {deep_links_found} deep-links (need 2+ strategies with deep-links)",
                        critical=True,
                    )
                    return None
            else:
                self.log_result(
                    "Options Optimizer",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    critical=True,
                )
                return None

        except Exception as e:
            self.log_result(
                "Options Optimizer", False, f"Request failed: {str(e)}", critical=True
            )
            return None

    def test_builder_pricing_endpoint(self, strategy_data: Dict) -> bool:
        """Test 6: POST /api/builder/price → verify 200 response with complete pricing + greeks"""
        print("🔍 TEST 6: Builder Pricing Engine with Deep-Link Data")

        if not strategy_data or "open_in_builder" not in strategy_data:
            self.log_result(
                "Builder Pricing",
                False,
                "No strategy data with deep-link available for testing",
                critical=True,
            )
            return False

        try:
            # Extract deep-link data
            deep_link = strategy_data["open_in_builder"]

            # Parse deep-link to extract parameters
            # Format: /build/{strategy}?symbol=X&expiry=Y&s=base64data
            if "?s=" in deep_link:
                encoded_data = deep_link.split("?s=")[-1]
                try:
                    # Decode base64URL data
                    decoded_bytes = base64.urlsafe_b64decode(encoded_data + "==")
                    strategy_params = json.loads(decoded_bytes.decode("utf-8"))
                except Exception as decode_error:
                    self.log_result(
                        "Builder Pricing",
                        False,
                        f"Failed to decode deep-link data: {str(decode_error)}",
                        critical=True,
                    )
                    return False
            else:
                # Fallback: create test payload from strategy data
                strategy_params = {
                    "symbol": "TSLA",
                    "legs": strategy_data.get(
                        "legs",
                        [{"side": "BUY", "type": "CALL", "strike": 250, "qty": 1}],
                    ),
                }

            # Make builder pricing request
            response = requests.post(
                f"{BACKEND_URL}/api/builder/price", json=strategy_params, timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                # Check for required sections
                required_sections = ["pricing", "chart", "meta", "greeks"]
                missing_sections = []

                for section in required_sections:
                    if section not in data:
                        missing_sections.append(section)

                if not missing_sections:
                    # Extract key metrics
                    pricing = data.get("pricing", {})
                    greeks = data.get("greeks", {})
                    meta = data.get("meta", {})

                    net_debit = pricing.get("net_debit", 0)
                    chance_profit = pricing.get("chance_profit", 0)
                    delta = greeks.get("delta", 0)
                    symbol = meta.get("symbol", "unknown")

                    self.log_result(
                        "Builder Pricing",
                        True,
                        f"{symbol} - Debit: ${net_debit:.2f}, Chance: {chance_profit:.1f}%, Delta: {delta:.4f}",
                        critical=True,
                    )
                    return True
                else:
                    self.log_result(
                        "Builder Pricing",
                        False,
                        f"Missing required sections: {missing_sections}",
                        critical=True,
                    )
                    return False
            else:
                self.log_result(
                    "Builder Pricing",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    critical=True,
                )
                return False

        except Exception as e:
            self.log_result(
                "Builder Pricing", False, f"Request failed: {str(e)}", critical=True
            )
            return False

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all GO/NO-GO tests and return results"""
        print("🚀 STARTING GO/NO-GO BACKEND SMOKE TESTS")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()

        # Test 1: Health Check
        health_ok = self.test_health_endpoint()

        # Test 2: Portfolios List
        portfolio_id = self.test_portfolios_endpoint()

        # Test 3: EOD Snapshot (if portfolio available)
        eod_ok = False
        if portfolio_id:
            eod_ok = self.test_eod_snapshot_endpoint(portfolio_id)

        # Test 4: Flow Summary (UW Token Test)
        flow_ok = self.test_flow_summary_endpoint()

        # Test 5: Options Optimizer
        strategy_data = self.test_optimize_suggest_endpoint()

        # Test 6: Builder Pricing (if strategy available)
        builder_ok = False
        if strategy_data:
            builder_ok = self.test_builder_pricing_endpoint(strategy_data)

        # Generate final assessment
        return self.generate_assessment()

    def generate_assessment(self) -> Dict[str, Any]:
        """Generate GO/NO-GO assessment"""
        print("=" * 70)
        print("🎯 GO/NO-GO ASSESSMENT RESULTS")
        print("=" * 70)

        # Count results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        critical_tests = sum(1 for r in self.results if r["critical"])
        critical_passed = sum(1 for r in self.results if r["critical"] and r["success"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        critical_success_rate = (
            (critical_passed / critical_tests * 100) if critical_tests > 0 else 0
        )

        print("📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Critical Tests: {critical_tests}")
        print(f"   Critical Passed: {critical_passed}")
        print(f"   Critical Success Rate: {critical_success_rate:.1f}%")
        print()

        # UW Token Status
        print(f"🔗 UW TOKEN STATUS: {self.uw_token_status.upper()}")
        if self.uw_token_status == "working":
            print("   ✅ Real data integration working")
        elif self.uw_token_status == "mock_fallback":
            print("   ⚠️  Using mock/fallback data")
        else:
            print("   ❌ Token integration issues")
        print()

        # Critical Failures
        if self.critical_failures:
            print("🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
            print()

        # GO/NO-GO Decision
        go_decision = len(self.critical_failures) == 0 and critical_success_rate >= 80

        print("🎯 GO/NO-GO DECISION:")
        if go_decision:
            print("   ✅ GO - System ready for Strike Rail PRO integration")
            print("   ✅ GO - Trade button (TS) color-coded implementation")
            print("   ✅ GO - Final polish phase")
        else:
            print("   ❌ NO-GO - Critical issues must be resolved before integration")
            print("   ❌ Block Strike Rail PRO integration")
            print("   ❌ Block Trade button implementation")

        print()
        print("📋 DETAILED TEST RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            critical_marker = " [CRITICAL]" if result["critical"] else ""
            print(f"   {status} {result['test']}{critical_marker}")
            print(f"      {result['details']}")

        print("=" * 70)

        return {
            "go_decision": go_decision,
            "success_rate": success_rate,
            "critical_success_rate": critical_success_rate,
            "uw_token_status": self.uw_token_status,
            "critical_failures": self.critical_failures,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "results": self.results,
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    tester = GoNoGoTester()
    assessment = tester.run_comprehensive_tests()

    # Save results to file
    with open("/app/go_no_go_results.json", "w") as f:
        json.dump(assessment, f, indent=2)

    print("\n📁 Results saved to: /app/go_no_go_results.json")
    print(f"✅ Testing completed at {datetime.now().isoformat()}")
