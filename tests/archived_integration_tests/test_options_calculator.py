#!/usr/bin/env python3
"""
Options Calculator Testing Script
Test the expanded Options Calculator with new strategies and optimization endpoint
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import StockMarketAPITester

def main():
 print(" OPTIONS CALCULATOR COMPREHENSIVE TESTING")
 print("=" * 80)
 print("🔑 Testing expanded Options Calculator with new strategies")
 print(" Backend URL: http://localhost:8000")

 tester = StockMarketAPITester()

 # Run the Options Calculator comprehensive test
 success = tester.test_options_calculator_comprehensive()

 # Summary
 print("\n" + "=" * 80)
 print(" OPTIONS CALCULATOR TEST SUMMARY")
 print("=" * 80)
 print(f"Total Tests Run: {tester.tests_run}")
 print(f"Tests Passed: {tester.tests_passed}")
 print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")

 if success:
 print(" OPTIONS CALCULATOR TESTING PASSED!")
 print(" All new strategies and optimization endpoints working correctly")
 return 0
 else:
 print(" OPTIONS CALCULATOR TESTING NEEDS ATTENTION")
 print(" Some strategies or endpoints may have issues")
 return 1

if __name__ == "__main__":
 sys.exit(main())
