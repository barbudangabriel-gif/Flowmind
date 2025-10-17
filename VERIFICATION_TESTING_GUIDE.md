# Verificări și Testare - FlowMind Backend
**Data:** 17 octombrie 2025  
**Scop:** Verificări manuale + teste automate pentru backend și TradeStation OAuth

---

## ✅ 1. Verificări Manuale

### A. Health & Status Checks

**Pornește backend-ul:**
```bash
# Activate venv (dacă folosești)
cd /workspaces/Flowmind/backend
source .venv/bin/activate 2>/dev/null || true

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Testează endpoints:**
```bash
# 1. Health check
curl -s http://localhost:8000/health
# Expected: {"ok": true}

# 2. Flow health
curl -s http://localhost:8000/api/flow/health
# Expected: {"ok": true, "scope": "flow"}

# 3. TradeStation status (unauthenticated)
curl -s http://localhost:8000/api/ts/status
# Expected: {"authenticated": false, "user_id": "demo"}
```

---

### B. OAuth Flow Complete

**1. Inițiază login:**
```bash
# În browser, deschide:
http://localhost:8000/api/ts/login

# Vei fi redirectat la TradeStation OAuth page
# Login cu SIMULATION credentials
```

**2. Verifică callback:**
După login, vei fi redirectat la:
```
http://localhost:8000/api/ts/callback?code=AUTH_CODE&state=RANDOM_STATE
```

**Expected response:**
```json
{
  "ok": true,
  "user_id": "demo",
  "expires_at": 1729200000,
  "message": "Authentication successful! You can close this window."
}
```

**3. Verifică authentication status:**
```bash
curl -s http://localhost:8000/api/ts/status
```

**Expected (după login):**
```json
{
  "authenticated": true,
  "user_id": "demo",
  "expires_at": 1729200000,
  "has_refresh_token": true
}
```

---

### C. Token Refresh Automat (Simulare Expirare)

**1. Simulează token expirat:**
```python
# În Python REPL (în terminal separat):
from app.services.tradestation import _TOKENS

# Forțează expirarea token-ului
t = _TOKENS.get("demo") or {}
t["expires_at"] = 0  # Expired
_TOKENS["demo"] = t

print("✅ Token marcat ca expirat")
```

**2. Test auto-refresh:**
```bash
# Lovește un endpoint care folosește get_valid_token()
curl -s http://localhost:8000/api/ts/status

# Check backend logs pentru:
# INFO: TS refresh ok; expires_at=...
tail -20 /tmp/backend_ts.log | grep "refresh"
```

**Expected în logs:**
```
INFO: Token expiring for user demo, refreshing...
INFO: TS refresh ok; expires_at=1729203600
```

---

### D. CORS Verification

**Frontend → Backend:**
```javascript
// În browser console (http://localhost:5173):
fetch('http://localhost:8000/api/flow/health')
  .then(r => r.json())
  .then(d => console.log('✅ CORS OK:', d))
  .catch(e => console.error('❌ CORS Error:', e));

// Expected output:
// ✅ CORS OK: {ok: true, scope: "flow"}
```

**Codespaces CORS:**
```bash
# Verifică .env conține ambele URL-uri:
grep ALLOWED_ORIGINS backend/.env

# Expected:
# ALLOWED_ORIGINS=https://sturdy-system-wvrqjjp49wg29qxx-5173.app.github.dev,https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev
```

---

## 🧪 2. Teste Automate (pytest + httpx mock)

### A. Setup Dependencies

**Install test dependencies:**
```bash
cd /workspaces/Flowmind/backend

# Install pytest, httpx, respx
pip install pytest httpx pytest-asyncio respx

# Verify installation
pytest --version
```

---

### B. Test Suite - TradeStation Auth

**Create `tests/test_ts_auth.py`:**
```python
# tests/test_ts_auth.py
import asyncio
import time
import respx
import httpx
import pytest
from app.services import tradestation as ts


@pytest.mark.asyncio
async def test_exchange_and_refresh():
    """Test token exchange and auto-refresh with expiry simulation."""
    now = int(time.time())
    
    # Mock token endpoints
    with respx.mock(base_url="https://api.tradestation.com") as mock:
        # First call: exchange code
        # Second call: refresh token
        mock.post("/oauth/token").side_effect = [
            httpx.Response(200, json={
                "access_token": "A1",
                "refresh_token": "R1",
                "expires_in": 120,
                "token_type": "Bearer"
            }),
            httpx.Response(200, json={
                "access_token": "A2",
                "refresh_token": "R2",
                "expires_in": 120,
                "token_type": "Bearer"
            }),
        ]
        
        # Test exchange_code
        tok = await ts.exchange_code("CODE", "http://localhost/cb")
        assert tok["access_token"] == "A1"
        assert tok["refresh_token"] == "R1"
        assert tok["expires_at"] > now
        assert tok["token_type"] == "Bearer"
        
        # Set token in cache and force expiration
        ts.set_token("u1", tok)
        ts._TOKENS["u1"]["expires_at"] = 0  # Force expired
        
        # get_valid_token should trigger refresh
        new_tok = await ts.get_valid_token("u1")
        assert new_tok is not None
        assert new_tok["access_token"] == "A2"
        
        # Verify cached token was updated
        cached = ts.get_cached_token("u1")
        assert cached["access_token"] == "A2"


@pytest.mark.asyncio
async def test_call_ts_api_with_retry():
    """Test API call with 401 retry logic."""
    with respx.mock(base_url=ts.TS_BASE_URL) as mock:
        # First request: 401 (expired token)
        # Second request: 200 (after refresh)
        mock.get("/v3/whatever").mock(side_effect=[
            httpx.Response(401, json={"error": "expired"}),
            httpx.Response(200, json={"ok": True})
        ])
        
        # Mock token refresh endpoint
        mock.post("/oauth/token").respond(200, json={
            "access_token": "A2",
            "refresh_token": "R2",
            "expires_in": 120,
            "token_type": "Bearer"
        })
        
        # Set initial expired token
        ts.set_token("u2", {
            "access_token": "old_token",
            "refresh_token": "R1",
            "expires_at": 0,
            "token_type": "Bearer"
        })
        
        # Call API - should auto-retry after refresh
        r = await ts.call_ts_api("u2", "GET", "/v3/whatever")
        assert r.status_code == 200
        assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_concurrent_refresh_with_lock():
    """Test that concurrent refresh requests use lock (no race condition)."""
    with respx.mock(base_url="https://api.tradestation.com") as mock:
        refresh_count = 0
        
        def mock_refresh(request):
            nonlocal refresh_count
            refresh_count += 1
            return httpx.Response(200, json={
                "access_token": f"A{refresh_count}",
                "refresh_token": f"R{refresh_count}",
                "expires_in": 120,
                "token_type": "Bearer"
            })
        
        mock.post("/oauth/token").mock(side_effect=mock_refresh)
        
        # Set expired token
        ts.set_token("u3", {
            "access_token": "old",
            "refresh_token": "R0",
            "expires_at": 0,
            "token_type": "Bearer"
        })
        
        # Concurrent requests - should only refresh once due to lock
        results = await asyncio.gather(
            ts.get_valid_token("u3"),
            ts.get_valid_token("u3"),
            ts.get_valid_token("u3")
        )
        
        # All should get same refreshed token
        assert all(r["access_token"] == results[0]["access_token"] for r in results)
        # Refresh should only happen once
        assert refresh_count == 1


@pytest.mark.asyncio
async def test_token_expiry_buffer():
    """Test REFRESH_SKEW buffer (60s before actual expiry)."""
    now = int(time.time())
    
    # Token expires in 30s (within 60s buffer)
    ts.set_token("u4", {
        "access_token": "A1",
        "refresh_token": "R1",
        "expires_at": now + 30,  # Expires soon
        "token_type": "Bearer"
    })
    
    # Should be considered expired due to REFRESH_SKEW
    cached = ts.get_cached_token("u4")
    assert cached is None  # Within buffer, considered expired
```

---

### C. Test Suite - Flow Endpoints

**Create `tests/test_flow.py`:**
```python
# tests/test_flow.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Test main health endpoint."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_flow_health():
    """Test flow service health endpoint."""
    r = client.get("/api/flow/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["scope"] == "flow"


def test_flow_snapshot():
    """Test flow snapshot endpoint."""
    r = client.get("/api/flow/snapshot/TSLA")
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "TSLA"
    assert "snapshot" in data


def test_flow_snapshot_validation():
    """Test snapshot with invalid symbol."""
    r = client.get("/api/flow/snapshot/")
    assert r.status_code == 404  # Missing symbol


def test_ts_status_unauthenticated():
    """Test TradeStation status when not authenticated."""
    r = client.get("/api/ts/status")
    assert r.status_code == 200
    data = r.json()
    assert data["authenticated"] is False
    assert "user_id" in data


def test_cors_headers():
    """Test CORS headers are present."""
    r = client.options("/api/flow/health")
    assert r.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in r.headers
```

---

### D. Run Tests

**Execute pytest:**
```bash
cd /workspaces/Flowmind/backend

# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_ts_auth.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

**Expected output:**
```
tests/test_flow.py .....                                        [50%]
tests/test_ts_auth.py ....                                      [100%]

========== 9 passed in 2.34s ==========
```

---

## 📦 3. Environment Configuration

### Local (.env)

```bash
# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# TradeStation API URLs
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://api.tradestation.com/authorize
TS_TOKEN_URL=https://api.tradestation.com/oauth/token

# TradeStation OAuth Credentials
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=http://localhost:8000/api/ts/callback

# TradeStation Scope & Timeout
TS_SCOPE=openid offline_access MarketData ReadAccount Trade Crypto
TS_HTTP_TIMEOUT=15
TS_REFRESH_SKEW=60
```

---

### Codespaces (.env)

```bash
# CORS Configuration (Codespaces public URLs)
ALLOWED_ORIGINS=https://sturdy-system-wvrqjjp49wg29qxx-5173.app.github.dev,https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev

# TradeStation Redirect URI (Codespaces public URL)
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/callback

# All other settings same as local
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://api.tradestation.com/authorize
TS_TOKEN_URL=https://api.tradestation.com/oauth/token
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_SCOPE=openid offline_access MarketData ReadAccount Trade Crypto
TS_HTTP_TIMEOUT=15
TS_REFRESH_SKEW=60
```

**⚠️ Important:** Pentru Codespaces, redirect URI trebuie aprobat în TradeStation Developer Portal!

---

## 🔒 4. Securitate - Minimum Necesar

### A. CSRF Protection pentru OAuth

**Problem:** Fără `state` validation, OAuth flow e vulnerabil la CSRF.

**Solution:**
```python
# În app/routers/tradestation_auth.py

import secrets
from fastapi import Cookie, Response

# State storage (in-memory pentru MVP, Redis pentru production)
_oauth_states = {}

@router.get("/login")
def ts_login(request: Request, response: Response):
    state = secrets.token_urlsafe(16)
    
    # Save state în cookie/sesiune (TTL 5 min)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=300,  # 5 minutes
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax"
    )
    
    return RedirectResponse(auth_url(redirect_uri, state))


@router.get("/callback")
async def ts_callback(
    code: str | None = None,
    state: str | None = None,
    oauth_state: str | None = Cookie(None)
):
    # Verifică state
    if not state or state != oauth_state:
        raise HTTPException(400, "Invalid state - CSRF protection failed")
    
    # Continue cu exchange_code...
```

---

### B. Token Storage în Production

**❌ Nu face:**
```python
# In-memory storage (pierdut la restart)
_TOKENS: Dict[str, Dict] = {}
```

**✅ Fă:**
```python
# Salvează în DB criptat
import cryptography
from sqlalchemy.orm import Session

async def set_token(user_id: str, token: Dict) -> None:
    encrypted_token = encrypt_token(token)
    await db.tokens.upsert({
        "user_id": user_id,
        "encrypted_token": encrypted_token,
        "expires_at": token["expires_at"]
    })
    
    # Cache pentru performance
    _TOKENS[user_id] = token
```

---

### C. Rate Limiting

**Install dependencies:**
```bash
pip install slowapi
```

**Implement:**
```python
# În app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# În app/routers/tradestation_auth.py
from app.main import limiter

@router.get("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def ts_login(request: Request):
    ...

@router.get("/callback")
@limiter.limit("10/minute")  # Max 10 callbacks per minute
async def ts_callback(request: Request, ...):
    ...
```

---

### D. Logging - Redact Sensitive Data

**❌ Nu face:**
```python
log.info(f"Token response: {response.json()}")  # Expune secrets
```

**✅ Fă:**
```python
def redact_token(token: Dict) -> Dict:
    return {
        "access_token": token["access_token"][:10] + "...",
        "refresh_token": "[REDACTED]",
        "expires_at": token["expires_at"]
    }

log.info(f"Token refreshed: {redact_token(new_tok)}")
```

---

## 🛠️ 5. Operare Rapidă

### A. Pornire Backend

```bash
# Activate venv
cd /workspaces/Flowmind/backend
source .venv/bin/activate

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: cu auto-reload la schimbări
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

---

### B. Pornire Frontend

```bash
cd /workspaces/Flowmind/frontend

# Development server
npm start

# Alternative cu Vite (dacă ai)
pnpm dev

# Preview production build
pnpm build && pnpm preview --host
```

---

### C. Endpoints Utile - Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Main health check |
| GET | `/api/flow/health` | Flow service health |
| GET | `/api/flow/snapshot/{symbol}` | Flow snapshot for symbol |
| GET | `/api/ts/login` | Redirect to TradeStation OAuth |
| GET | `/api/ts/callback?code=...` | OAuth callback handler |
| GET | `/api/ts/status` | Check authentication status |
| POST | `/api/ts/logout` | Clear user tokens |
| GET | `/docs` | Swagger UI (interactive API docs) |
| GET | `/openapi.json` | OpenAPI schema |

---

### D. Debug Commands

```bash
# Check backend logs
tail -f /tmp/backend_ts.log

# Check if backend is running
ps aux | grep uvicorn

# Check port 8000
lsof -ti:8000

# Kill backend
pkill -9 -f "uvicorn.*8000"

# Test endpoint with full headers
curl -v http://localhost:8000/api/flow/health

# Test CORS
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/flow/health
```

---

## 📊 6. Success Criteria

### ✅ All Tests Pass:
```bash
pytest -q
# Expected: 9 passed in 2.34s
```

### ✅ Manual Checks:
- [ ] `/health` returns `{"ok": true}`
- [ ] `/api/flow/health` returns `{"ok": true, "scope": "flow"}`
- [ ] `/api/ts/login` redirects to TradeStation
- [ ] OAuth callback returns `{"ok": true, "expires_at": ...}`
- [ ] `/api/ts/status` shows `authenticated: true` after login
- [ ] Token auto-refresh works (logs show "TS refresh ok")
- [ ] CORS allows frontend requests (no errors in console)

### ✅ Security:
- [ ] CSRF state validation implemented
- [ ] Tokens saved in DB (not only in-memory)
- [ ] Rate limiting on auth endpoints
- [ ] Sensitive data redacted in logs

---

## 🚨 Troubleshooting

### Issue: "Cannot import name 'tradestation'"
```bash
# Fix: Ensure __init__.py files exist
ls -la backend/app/__init__.py
ls -la backend/app/services/__init__.py

# If missing:
touch backend/app/__init__.py
touch backend/app/services/__init__.py
```

### Issue: "CORS error in browser"
```bash
# Check ALLOWED_ORIGINS
grep ALLOWED_ORIGINS backend/.env

# Should include frontend URL
# Local: http://localhost:5173
# Codespaces: https://...-5173.app.github.dev
```

### Issue: "OAuth callback fails"
```bash
# Check logs
tail -30 /tmp/backend_ts.log

# Common causes:
# 1. Redirect URI not approved in TradeStation portal
# 2. Wrong TS_REDIRECT_URI in .env
# 3. STATE mismatch (CSRF protection)
```

---

**Verificări complete - Ready for production testing!**
