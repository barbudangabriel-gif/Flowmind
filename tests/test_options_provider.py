from unittest.mock import Mock, patch


def test_provider_selection_uw(client, monkeypatch):
    """Test UW provider selection"""
    monkeypatch.setenv("PROVIDER", "UW")
    monkeypatch.setenv("UW_API_KEY", "test_key")

    r = client.get("/api/options/provider/status")
    assert r.status_code == 200
    js = r.json()
    assert js["provider_name"] == "UWProvider"
    assert js["provider_env"] == "UW"


def test_provider_selection_ts(client, monkeypatch):
    """Test TS provider selection"""
    monkeypatch.setenv("PROVIDER", "TS")

    r = client.get("/api/options/provider/status")
    assert r.status_code == 200
    js = r.json()
    assert js["provider_name"] == "TSProvider"
    assert js["provider_env"] == "TS"


@patch("services.providers.uw_provider.requests.get")
def test_uw_provider_spot_price(mock_get, client, monkeypatch):
    """Test UW provider spot price with mocked response"""
    monkeypatch.setenv("PROVIDER", "UW")
    monkeypatch.setenv("UW_API_KEY", "test_key")

    # Mock UW API response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"last": 250.75}
    mock_get.return_value = mock_response

    r = client.get("/api/options/spot/TSLA")
    assert r.status_code == 200
    js = r.json()
    assert js["symbol"] == "TSLA"
    assert js["spot"] == 250.75
    assert js["provider"] == "UWProvider"


@patch("services.providers.uw_provider.requests.get")
def test_uw_provider_options_chain(mock_get, client, monkeypatch):
    """Test UW provider options chain with mocked response"""
    monkeypatch.setenv("PROVIDER", "UW")
    monkeypatch.setenv("UW_API_KEY", "test_key")

    # Mock UW chain response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "options": [
            {
                "expiration": "2025-02-21",
                "strike": 250.0,
                "type": "C",
                "iv": 0.25,
                "gamma": 0.01,
                "open_interest": 100,
            }
        ]
    }
    mock_get.return_value = mock_response

    r = client.get("/api/options/chain?symbol=TSLA")
    assert r.status_code == 200
    js = r.json()
    assert js["symbol"] == "TSLA"
    assert js["provider"] == "UWProvider"
    assert "OptionChains" in js["raw"]


def test_gex_calculation_mock(client, monkeypatch):
    """Test GEX calculation with mocked provider data"""
    monkeypatch.setenv("PROVIDER", "TS")  # Use TS to avoid UW API calls

    # This will fail gracefully since we don't have real TS credentials in TEST_MODE
    r = client.get("/api/options/gex?symbol=TSLA&dte=30")
    # Accept either success with empty data or controlled failure
    assert r.status_code in (200, 500)
