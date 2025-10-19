import os

os.environ.setdefault("IV_PROVIDER", "STUB")

from fastapi.testclient import TestClient
from iv_service.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_summary_nvda():
    r = client.get("/api/iv/summary", params={"symbol": "NVDA"})
    assert r.status_code == 200
    j = r.json()
    for k in ("symbol", "spot", "iv", "em_usd", "em_pct", "front_dte", "back_dte"):
        assert k in j
    assert j["symbol"] == "NVDA"


def test_batch_calendar_default():
    # Use POST instead of GET (API contract change)
    r = client.post(
        "/api/iv/batch", json={"watchlist": "WL_MAIN", "rule": "calendar", "limit": 3}
    )
    assert r.status_code == 200
    j = r.json()
    assert "meta" in j and "rows" in j
    assert j["meta"]["ok"] >= 1
    assert any(
        "dc_low" in row and "dc_high" in row for row in j["rows"]
    )  # calendar fields


def test_batch_condor_default():
    r = client.post(
        "/api/iv/batch",
        json={"symbols": ["NVDA", "AAPL", "MSFT"], "rule": "condor", "limit": 3},
    )
    assert r.status_code == 200
    j = r.json()
    assert j["meta"]["ok"] >= 1
    assert any(
        "ic_shorts" in row and "ic_wings" in row for row in j["rows"]
    )  # condor fields
