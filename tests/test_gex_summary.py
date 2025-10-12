
import os, requests
BASE = os.getenv("FLOWMIND_BASE_URL", "http://localhost:8000")

def test_summary_contract_multiple():
    url = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSLA&expiries=2025-11-01,2025-11-08,2025-11-22&source=mock"
    r = requests.get(url, timeout=15)
    assert r.status_code == 200
    js = r.json()
    assert js.get("symbol") == "TSLA"
    assert isinstance(js.get("items"), list) and len(js["items"]) >= 1
    for it in js["items"]:
        assert "expiry" in it and "netGex" in it

def test_summary_invalid_symbol_422():
    url = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSL@&expiries=2025-11-01&source=mock"
    r = requests.get(url, timeout=10)
    assert r.status_code in (400, 422)

def test_summary_empty_or_bad_expiries_400():
    url = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSLA&expiries=&source=mock"
    r = requests.get(url, timeout=10)
    assert r.status_code in (400, 422)

def test_summary_dedups_duplicate_expiries():
    url = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSLA&expiries=2025-11-01,2025-11-01,2025-11-08&source=mock"
    r = requests.get(url, timeout=10)
    assert r.status_code == 200
    js = r.json(); seen = set()
    for it in js["items"]:
        assert it["expiry"] not in seen
        seen.add(it["expiry"])

def test_summary_partial_no_data_allows_206_or_200():
    url = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSLA&expiries=1999-01-01,1999-01-08&source=mock"
    r = requests.get(url, timeout=10)
    assert r.status_code in (200, 206)
    js = r.json()
    if js.get("items"):
        assert all(it.get("status") in ("NO_DATA", None) for it in js["items"])

def test_summary_dealer_sign_inverts_each_item():
    base = f"{BASE}/api/v1/analytics/gex/summary?symbol=TSLA&expiries=2025-11-01,2025-11-08&source=mock"
    r1 = requests.get(base + "&dealer_sign=mm_short", timeout=10)
    r2 = requests.get(base + "&dealer_sign=mm_long", timeout=10)
    assert r1.status_code == 200 and r2.status_code == 200
    a, b = r1.json()["items"], r2.json()["items"]
    assert len(a) == len(b) >= 1
    d = {it["expiry"]: float(it["netGex"]) for it in a}
    for it in b:
        exp = it["expiry"]; n2 = float(it["netGex"])
        import math
        assert math.isclose(d[exp], -n2, rel_tol=1e-3, abs_tol=1.0)
