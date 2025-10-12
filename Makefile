.PHONY: test perf
BASE?=http://localhost:8000

test:
	pytest -q tests/test_gex_endpoint.py

perf:
	FLOWMIND_BASE_URL=$(BASE) k6 run perf/k6_gex_smoke.js
