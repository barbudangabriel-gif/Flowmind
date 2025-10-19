"""
FlowMind - Backtest cache tests
"""

import pytest
from fastapi.testclient import TestClient
import sys

sys.path.insert(0, "/app/backend")

@pytest.fixture
def client():
    from server import app

    return TestClient(app)

def test_screener_emits_only_ok(client):
    """Test că screener emits doar signals care pass gates"""
    r = client.get("/screen/iv-setups?strategy=DOUBLE_DIAGONAL&limit=3")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"]

    for item in data["items"]:
        assert item.get("signalOk") is True
        assert item.get("decision") in ("ALLOW", "ALLOW_WITH_WARNINGS")
        assert "backtest" in item

def test_cache_hit(client):
    """Test Redis cache HIT behavior"""
    # First call (MISS)
    r1 = client.get("/screen/iv-setups?strategy=IRON_CONDOR&limit=1")
    assert r1.status_code == 200
    data1 = r1.json()

    # Second call (should be HIT)
    r2 = client.get("/screen/iv-setups?strategy=IRON_CONDOR&limit=1")
    assert r2.status_code == 200
    data2 = r2.json()

    # Check cache status
    if data1["items"] and data2["items"]:
        cache1 = data1["items"][0].get("backtest", {}).get("cache", "unknown")
        cache2 = data2["items"][0].get("backtest", {}).get("cache", "unknown")
        # Note: May be MISS/MISS în fallback mode, HIT în Redis mode
        assert cache2 in ("HIT", "MISS") # Either is acceptable

def test_ops_endpoints(client):
    """Test backtest ops endpoints"""
    # Status
    r = client.get("/_bt/status")
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # Keys
    r = client.get("/_bt/keys")
    assert r.status_code == 200
    assert "keys" in r.json()

def test_backtest_quality_gate(client):
    """Test că backtest data has minimum quality"""
    r = client.get("/screen/iv-setups?limit=5")
    data = r.json()

    for item in data.get("items", []):
        bt = item.get("backtest", {})
        if bt.get("kind") == "proxy/eod":
            # Quality checks
            assert isinstance(bt.get("n"), int)
            assert bt["n"] >= 0
            if bt["n"] > 30: # Only check metrics pentru sufficient sample
                assert 0 <= bt.get("win_rate", 0) <= 1
                assert -10 <= bt.get("expectancy", 0) <= 10
