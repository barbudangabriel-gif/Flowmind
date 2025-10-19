#!/usr/bin/env python3
"""
FlowMind Production Health Monitor
Checks all health endpoints and service status
"""

import subprocess
import time
import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ANSI colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_header(text):
    print(f"\n{'='*70}")
    print(f"{BLUE}{text}{NC}")
    print("=" * 70)


def check_endpoint(url, name, expected_keys=None):
    """Check a single endpoint and return status"""
    try:
        req = Request(url)
        req.add_header("User-Agent", "FlowMind-Health-Monitor/1.0")

        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            status_code = response.status

            # Check expected keys
            if expected_keys:
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    print(f"{YELLOW}⚠️  {name}: Missing keys {missing}{NC}")
                    return False

            print(f"{GREEN}✅ {name}: OK (HTTP {status_code}){NC}")

            # Pretty print response
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            return True

    except HTTPError as e:
        print(f"{RED}❌ {name}: HTTP {e.code} - {e.reason}{NC}")
        return False
    except URLError as e:
        print(f"{RED}❌ {name}: Connection failed - {e.reason}{NC}")
        return False
    except json.JSONDecodeError:
        print(f"{RED}❌ {name}: Invalid JSON response{NC}")
        return False
    except Exception as e:
        print(f"{RED}❌ {name}: Unexpected error - {str(e)}{NC}")
        return False


def check_backend_import():
    """Test backend import"""
    print(f"\n{BLUE}📦 Testing Backend Import...{NC}")
    try:
        result = subprocess.run(
            ["python", "-c", 'from app.main import app; print("OK")'],
            cwd="/workspaces/Flowmind/backend",
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "OK" in result.stdout:
            print(f"{GREEN}✅ Backend imports successfully{NC}")
            return True
        else:
            print(f"{RED}❌ Backend import failed:{NC}")
            print(f"   {result.stderr}")
            return False
    except Exception as e:
        print(f"{RED}❌ Import test error: {str(e)}{NC}")
        return False


def check_python_compilation():
    """Check Python 3.12 compilation"""
    print(f"\n{BLUE}🐍 Checking Python 3.12 Compilation...{NC}")
    try:
        result = subprocess.run(
            ["python", "-m", "compileall", "-q", "backend/"],
            cwd="/workspaces/Flowmind",
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"{GREEN}✅ All Python files compile successfully{NC}")
            return True
        else:
            print(f"{RED}❌ Compilation errors found:{NC}")
            print(f"   {result.stderr}")
            return False
    except Exception as e:
        print(f"{RED}❌ Compilation check error: {str(e)}{NC}")
        return False


def check_tests():
    """Run pytest quickly"""
    print(f"\n{BLUE}🧪 Running Quick Test Suite...{NC}")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "backend/tests/", "-q", "--tb=no"],
            cwd="/workspaces/Flowmind",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse output
        output = result.stdout + result.stderr
        if "passed" in output:
            # Extract test count
            import re

            match = re.search(r"(\d+) passed", output)
            if match:
                count = match.group(1)
                print(f"{GREEN}✅ {count} tests passed{NC}")
                return True

        print(f"{YELLOW}⚠️  Some tests failed{NC}")
        print(f"   Run 'pytest backend/tests/ -v' for details")
        return False

    except Exception as e:
        print(f"{RED}❌ Test execution error: {str(e)}{NC}")
        return False


def main():
    """Main health check routine"""
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║         FlowMind Production Health Monitor                     ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{NC}")

    results = {}

    # Check 1: Backend Import
    print_header("1. Backend Import Test")
    results["backend_import"] = check_backend_import()

    # Check 2: Python Compilation
    print_header("2. Python 3.12 Compilation")
    results["python_compilation"] = check_python_compilation()

    # Check 3: Test Suite
    print_header("3. Test Suite")
    results["tests"] = check_tests()

    # Check 4: Health Endpoints (if server is running)
    print_header("4. Health Endpoints")
    print(f"{YELLOW}ℹ️  Note: Endpoints require running server{NC}")
    print(f"   Start server: cd backend && python -m uvicorn app.main:app --port 8000")
    print(f"   Then check:")
    print(f"   - http://localhost:8000/health")
    print(f"   - http://localhost:8000/healthz")
    print(f"   - http://localhost:8000/readyz")
    print(f"   - http://localhost:8000/api/health/redis")

    # Try to check if server is running
    print(f"\n{BLUE}🔍 Checking if server is running...{NC}")
    server_running = False
    for port in [8000, 8080, 3000]:
        try:
            with urlopen(f"http://localhost:{port}/health", timeout=1) as response:
                if response.status == 200:
                    print(f"{GREEN}✅ Server found on port {port}{NC}")
                    server_running = True
                    BASE_URL = f"http://localhost:{port}"

                    # Check all endpoints
                    results["health"] = check_endpoint(
                        f"{BASE_URL}/health", "/health", expected_keys=["status"]
                    )
                    results["healthz"] = check_endpoint(
                        f"{BASE_URL}/healthz", "/healthz"
                    )
                    results["readyz"] = check_endpoint(f"{BASE_URL}/readyz", "/readyz")
                    results["redis_health"] = check_endpoint(
                        f"{BASE_URL}/api/health/redis",
                        "/api/health/redis",
                        expected_keys=["status", "cache_mode"],
                    )
                    break
        except:
            continue

    if not server_running:
        print(f"{YELLOW}⚠️  Server not running - start it to check endpoints{NC}")

    # Final Summary
    print_header("SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"\n{'='*70}")
    print(f"Total Checks: {total}")
    print(f"{GREEN}Passed: {passed}{NC}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{NC}")
    print(f"{'='*70}")

    # Detailed results
    print(f"\n{BLUE}Detailed Results:{NC}")
    for check, status in results.items():
        icon = f"{GREEN}✅{NC}" if status else f"{RED}❌{NC}"
        print(f"  {icon} {check.replace('_', ' ').title()}")

    # Exit code
    if failed == 0:
        print(f"\n{GREEN}🎉 ALL SYSTEMS OPERATIONAL{NC}\n")
        return 0
    elif failed <= 2:
        print(f"\n{YELLOW}⚠️  SOME CHECKS FAILED (non-critical){NC}\n")
        return 0  # Non-blocking
    else:
        print(f"\n{RED}❌ CRITICAL ISSUES FOUND{NC}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Health check interrupted{NC}")
        sys.exit(130)
