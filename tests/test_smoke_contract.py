import os
import pytest

PID = "pf_test123"  # din seed-ul conftest


def test_mindfolios_list(client):
    """Test basic mindfolio listing"""
    r = client.get("/api/mindfolios")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, list)
    # In TEST_MODE, mindfolio list might be empty initially (Redis in-memory)
    # This is expected behavior and validates the endpoint works


def test_health_endpoints(client):
    """Test health and readiness endpoints"""
    r = client.get("/health")
    assert r.status_code == 200
    js = r.json()
    assert js["status"] == "healthy"
    assert "service" in js

    r = client.get("/readyz")
    assert r.status_code == 200
    js = r.json()
    assert js["status"] == "ready"


def test_eod_workflow(client):
    """Test EOD snapshot creation and retrieval"""
    # First create a mindfolio for testing
    mindfolio_data = {
        "name": "Test EOD Mindfolio",
        "cash_balance": 10000.0,
        "status": "ACTIVE",
    }
    r = client.post("/api/mindfolios", json=mindfolio_data)
    assert r.status_code in (200, 201)
    created_mindfolio = r.json()
    test_mindfolio_id = created_mindfolio["id"]

    # Create snapshot
    r = client.post(f"/api/mindfolios/{test_mindfolio_id}/analytics/eod/snapshot")
    assert r.status_code == 200
    js = r.json()
    assert js["status"] == "success"
    assert "snapshot" in js
    snapshot = js["snapshot"]
    assert "date" in snapshot
    assert "total" in snapshot

    # Retrieve EOD series
    r = client.get(f"/api/mindfolios/{test_mindfolio_id}/analytics/eod")
    assert r.status_code == 200
    js = r.json()
    assert "series" in js
    assert isinstance(js["series"], list)


@pytest.mark.skipif(not os.getenv("TRADESTATION_API_KEY"), reason="TS creds absent")
def test_ts_integration_optional(client):
    """Test TradeStation integration (optional)"""
    r = client.get("/api/ts/status")
    assert r.status_code in (200, 404)  # May not be implemented yet
