# pytest -q tests/test_gex_endpoint.py
import os
import json
import math
from pathlib import Path
from typing import Dict, Any
import requests

BASE_URL = os.getenv("FLOWMIND_BASE_URL", "http://localhost:8000")
GEX_PATH = "/api/v1/analytics/gex"
FIXTURE = Path("fixtures/tsla_2025-11-21.json")

def _url(params: Dict[str, Any]) -> str:
    from urllib.parse import urlencode
    return f"{BASE_URL}{GEX_PATH}?{urlencode(params)}"


def test_contract_ok_symbol_expiry():
    params = {"symbol": "SPY", "expiry": "2025-11-21"}
    r = requests.get(_url(params), headers={"Accept": "application/json"}, timeout=10)
    assert r.status_code == 200, r.text
    body = r.json()
    for k in ("symbol","spot","expiry","strikes","gex","walls","netGex"):
        assert k in body
    assert isinstance(body["strikes"], list) and isinstance(body["gex"], list)
    assert len(body["strikes"]) == len(body["gex"]) >= 3


def test_invalid_params_400():
    # expiry greșit
    r = requests.get(_url({"symbol":"SPY","expiry":"21-11-2025"}), timeout=10)
    assert r.status_code in (400,422)


def test_etag_cache_304():
    params = {"symbol": "SPY", "expiry": "2025-11-21"}
    r1 = requests.get(_url(params), headers={"Accept":"application/json"}, timeout=10)
    assert r1.status_code == 200
    etag = r1.headers.get("ETag")
    if not etag:
        # dacă nu e implementat încă, marchează xfail
        import pytest
        pytest.xfail("ETag absent — implementați cache pentru 304")
    r2 = requests.get(_url(params), headers={"If-None-Match": etag}, timeout=10)
    assert r2.status_code == 304


def test_fixture_correctness_mock_oracle():
    if not FIXTURE.exists():
        import pytest
        pytest.skip("fixture absent")
    fx = json.loads(FIXTURE.read_text())
    params = {"symbol": fx["symbol"], "expiry": fx["expiry"], "source": "mock"}
    r = requests.get(_url(params), headers={"Accept":"application/json"}, timeout=10)
    assert r.status_code == 200
    body = r.json()
    # compara netGex și walls cu oracle-ul din fixture
    def rel_err(x,y):
        x = float(x); y = float(y)
        return abs(x-y)/max(1.0, abs(y))
    assert rel_err(body["netGex"], fx["netGex_ref"]) <= 0.02
    assert body["walls"] == fx["walls_ref"], body["walls"]


def test_range_atm10_lengths():
    params = {"symbol": "TSLA", "expiry": "2025-11-21", "range": "ATM10", "source": "mock"}
    r = requests.get(_url(params), timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert len(body["strikes"]) >= 5
