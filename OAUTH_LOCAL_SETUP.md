# TradeStation OAuth - Setup LOCAL (SIMULATOR Mode)

## ❌ De ce NU funcționează în Codespaces:
```
DNS_PROBE_FINISHED_NXDOMAIN: sim-signin.tradestation.com
Motivul: TradeStation SIMULATOR domain nu este accesibil din GitHub Codespaces
```

## ✅ Soluție: Testare pe LOCALHOST

---

## 📋 Pași pentru Setup Local (Windows/Mac/Linux):

### 1. Pull Latest Changes
```bash
cd /path/to/Flowmind
git pull origin main
```

### 2. Configure Backend Environment
Editează `backend/.env`:
```bash
# SCHIMBĂ această linie:
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback

# CU:
TS_REDIRECT_URI=http://localhost:8000/api/oauth/tradestation/callback
```

**IMPORTANT:** TradeStation a aprobat deja URL-ul `http://localhost:8000/api/oauth/tradestation/callback` în Developer Portal!

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Start Backend
```bash
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Output așteptat:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Test OAuth Flow
**În browser, deschide:**
```
http://localhost:8000/api/ts/login
```

**Flow așteptat:**
1. Redirect către `sim-signin.tradestation.com` (TradeStation login)
2. Autentificare pe TradeStation
3. Redirect înapoi la `http://localhost:8000/api/oauth/tradestation/callback?code=...`
4. Success page cu countdown (3s)

### 6. Verify Authentication
```bash
curl http://localhost:8000/api/ts/status
```

**Output așteptat (success):**
```json
{
  "authenticated": true,
  "user_id": "default",
  "token_expiry": "2025-10-24T..."
}
```

---

## 🔍 Debugging:

### Check Backend Logs
Caută în terminal:
```
INFO:oauth.callback:OAuth callback received - code: present, state: ..., error: None
INFO:oauth.callback:Exchanging authorization code for access token
INFO:oauth.callback:✓ OAuth flow completed successfully for user default
```

### Erori Comune:

**1. ModuleNotFoundError: No module named 'xyz'**
```bash
cd backend && pip install -r requirements.txt
```

**2. Port 8000 already in use**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**3. Token exchange failed**
- Verifică `TS_REDIRECT_URI` în `.env` (trebuie să fie `http://localhost:8000/...`)
- Verifică internet connection (trebuie acces la `sim-signin.tradestation.com`)

---

## 📝 Notes:

- **Simulator Mode:** Uses `sim-signin.tradestation.com` and `sim-api.tradestation.com`
- **Token Duration:** Access token expires after 20 minutes (1200 seconds)
- **Refresh Token:** Valid for 60 days, handled automatically by `get_valid_token()`
- **Storage:** Tokens stored in memory (`_TOKENS` dict in `tradestation.py`) - NOT persistent across restarts

---

## ✅ Success Criteria:

- [ ] Backend starts without errors
- [ ] `/api/ts/login` redirects to TradeStation
- [ ] TradeStation login completes successfully
- [ ] Callback shows success page
- [ ] `/api/ts/status` returns `{"authenticated": true}`

Dacă toate 5 checkboxuri sunt ✅ → OAuth funcționează corect!
