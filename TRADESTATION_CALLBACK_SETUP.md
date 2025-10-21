# 🔐 TradeStation SIMULATOR - Configurare Callback

**Data:** 21 Octombrie 2025  
**Mode:** SIMULATOR (Development)  
**Status:** ✅ Backend configurat și pornit

---

## 📋 Ce trebuie să faci în TradeStation

### **Pasul 1: Accesează TradeStation Developer Portal**
🔗 **Link:** https://sim.tradestation.com/developers

### **Pasul 2: Creează sau editează aplicația ta**

1. **Apasă pe "My Apps"** sau **"Create New App"**
2. **Completează detaliile aplicației:**
   - **App Name:** FlowMind Analytics (sau cum vrei tu)
   - **Description:** Options analytics and portfolio management platform

### **Pasul 3: Configurează Redirect URI (IMPORTANT!)**

📍 **Adaugă acest URL EXACT în câmpul "Redirect URIs":**

```
https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback
```

⚠️ **ATENȚIE:** Trebuie să fie EXACT așa - inclusiv `/api/oauth/tradestation/callback` la final!

### **Pasul 4: Selectează Scopes (Permisiuni)**

✅ Bifează următoarele:
- ✅ `openid` - Required pentru autentificare
- ✅ `offline_access` - Token refresh (important!)
- ✅ `MarketData` - Pentru options chains și spot prices
- ✅ `ReadAccount` - Pentru balance și positions
- ✅ `Trade` - (Optional) Dacă vrei să execuți tranzacții

### **Pasul 5: Salvează și copiază credențialele**

După ce salvezi aplicația, TradeStation îți va arăta:
- **Client ID** (deja ai: `XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj`)
- **Client Secret** (deja ai: `NsAIyb...`)

---

## ✅ Verificare că totul funcționează

### **Test 1: Verifică că backend-ul rulează**
```bash
curl https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/health
```

Răspuns așteptat: `{"status":"ok"}` sau similar

### **Test 2: Testează OAuth Flow**

1. **Deschide browser și accesează:**
   ```
   https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/login
   ```

2. **Ce ar trebui să se întâmple:**
   - Browser-ul te redirectează la TradeStation login
   - Te loghezi cu contul tău de SIMULATOR
   - TradeStation te redirectează înapoi la FlowMind
   - Vezi mesaj de succes: ✅ "Successfully authenticated!"

### **Test 3: Verifică dacă token-ul e salvat**
```bash
curl https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/token
```

Răspuns așteptat: `{"has_token": true}` sau detalii despre token

---

## 🔧 Configurația ta actuală (backend/.env)

```bash
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback
TS_MODE=SIMULATION

# URLs configurate automat
TS_BASE_URL=https://sim-api.tradestation.com
TS_AUTH_URL=https://sim-signin.tradestation.com/authorize
TS_TOKEN_URL=https://sim-signin.tradestation.com/oauth/token
```

---

## 🚨 Troubleshooting

### **Problemă: "Redirect URI mismatch"**
**Soluție:** Verifică că ai copiat EXACT URL-ul din acest document în TradeStation. Include tot până la `/callback`.

### **Problemă: "Invalid client credentials"**
**Soluție:** Verifică că `TS_CLIENT_ID` și `TS_CLIENT_SECRET` din `.env` match-uiesc cu cele din TradeStation dashboard.

### **Problemă: Backend nu răspunde**
**Soluție:** Restart backend:
```bash
cd /workspaces/Flowmind/backend
pkill -f uvicorn
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### **Problemă: Codespace URL s-a schimbat**
Dacă restartezi Codespace-ul, URL-ul poate fi diferit. Verifică noul URL și updatează:
1. `backend/.env` - `TS_REDIRECT_URI`
2. TradeStation dashboard - Redirect URI

---

## 📞 Next Steps după ce configurezi

1. ✅ Adaugă callback URL în TradeStation → **TU FACI ASTA ACUM**
2. ✅ Testezi OAuth flow (click pe link-ul de mai sus)
3. ✅ Verifici că primești date de la TradeStation API
4. 🚀 Începi să construiești strategii în FlowMind!

---

## 🎯 Link-uri rapide

| Descriere | URL |
|-----------|-----|
| **TradeStation SIM Portal** | https://sim.tradestation.com/developers |
| **Login endpoint (test)** | https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/login |
| **Health check** | https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/health |
| **Frontend (dacă pornit)** | https://sturdy-system-wvrqjjp49wg29qxx-3000.app.github.dev |

---

**✅ Callback configurat și gata de folosit!**

Îmi spui când ai terminat în TradeStation dashboard și testăm împreună OAuth flow-ul! 🚀
