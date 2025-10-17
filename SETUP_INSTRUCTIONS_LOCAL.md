# FlowMind - Instrucțiuni Setup LOCAL

**Data**: 17 Octombrie 2025  
**Status**: Configurat pentru localhost, gata pentru rulare locală

---

## ⚠️ DE CE LOCAL?

După 5 ore de încercări în Codespaces:
- ❌ `sim-signin.tradestation.com` NU este accesibil din Codespaces (restricții DNS/rețea)
- ❌ TradeStation NU a aprobat callback URL pentru Codespaces
- ✅ TradeStation A APROBAT `http://localhost:8000/api/oauth/tradestation/callback`

**CONCLUZIE**: Trebuie rulat LOCAL pentru OAuth TradeStation!

---

## 📋 CERINȚE

Înainte de setup, asigură-te că ai:
- ✅ Python 3.8+ instalat
- ✅ Node.js 16+ și npm instalat
- ✅ Git instalat
- ✅ Cont TradeStation SIMULATION (ai deja!)
- ✅ Conexiune la internet

Verifică versiunile:
```bash
python --version   # sau python3 --version
node --version
npm --version
git --version
```

---

## 🚀 PAȘI SETUP (10-15 minute)

### **1. Clonează Repository**

```bash
# Deschide Terminal/Command Prompt
# Navighează unde vrei să salvezi proiectul (ex: Desktop)
cd Desktop

# Clonează repo
git clone https://github.com/barbudangabriel-gif/Flowmind.git
cd Flowmind
```

### **2. Pornește Backend**

**Deschide Terminal 1:**
```bash
cd backend

# Instalează dependențele
pip install -r requirements.txt
# SAU dacă ai probleme: pip3 install -r requirements.txt

# Pornește server-ul
python -m uvicorn app.main:app --reload --port 8000
# SAU: python3 -m uvicorn app.main:app --reload --port 8000
```

**Aștepți să vezi:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### **3. Pornește Frontend**

**Deschide Terminal 2 NOU (lasă primul pornit!):**
```bash
cd frontend

# Instalează dependențele
npm install

# Pornește aplicația
npm start
```

**Aștepți să vezi:**
```
Compiled successfully!
You can now view flowmind in the browser.
  Local:            http://localhost:3000
```

**Browser-ul se va deschide AUTOMAT!** 🎉

---

## 🔐 CONECTARE TRADESTATION

### **Pas 1: Navighează la pagina de login**

În browser, du-te la:
```
http://localhost:3000/tradestation/login
```

### **Pas 2: Click "Connect with TradeStation"**

Vei vedea:
- Mode: **SIMULATION** (paper trading, bani virtuali)
- Buton albastru: **"Connect with TradeStation"**

### **Pas 3: Autentificare**

- Vei fi redirecționat la `sim-signin.tradestation.com` ✅
- Introdu credențialele contului tău **TradeStation SIMULATION**
- Aprobează accesul FlowMind

### **Pas 4: Success!**

- Vei fi redirecționat înapoi la `http://localhost:8000/api/oauth/tradestation/callback`
- Backend-ul salvează token-ul
- Ești conectat! ✅

### **Pas 5: Vezi Account Balance**

Navighează la:
```
http://localhost:3000/account/balance
```

**Vei vedea:**
- Account ID (SIMULATION)
- Cash Balance (~$100,000+ bani virtuali)
- Buying Power
- Current Positions (dacă ai)
- Market Value
- Unrealized P&L

---

## 🎯 CE POȚI FACE ACUM

### **1. Options Flow (Unusual Whales - LIVE)**
```
http://localhost:3000/flow
```
- Real-time options flow
- Bull/Bear premium tracking
- Sweeps & blocks detection
- Congress trades, insider activity

### **2. Options Chain (TradeStation - LIVE)**
```
http://localhost:3000/options/chain
```
- Live options prices
- Greeks (Delta, Gamma, Theta, Vega)
- Open Interest & Volume
- Bid/Ask spreads

### **3. GEX - Gamma Exposure**
```
http://localhost:3000/options/gex
```
- Gamma exposure by strike
- Zero-gamma level
- Support/resistance zones
- Market maker positioning

### **4. Strategy Builder**
```
http://localhost:3000/builder
```
- Build multi-leg strategies
- P&L visualization
- Greeks calculation
- Backtest historical performance

### **5. ALGOS - Paper Trading**
```
http://localhost:3000/account/balance
```
- Connected to TradeStation SIMULATION
- Run trading algorithms
- Test strategies with virtual money
- Execute automated trades
- Track performance

---

## 🔧 TROUBLESHOOTING

### **Backend nu pornește:**
```bash
# Verifică că ești în directorul corect
pwd  # Trebuie să fie: .../Flowmind/backend

# Încearcă cu python3
python3 -m uvicorn app.main:app --reload --port 8000

# Verifică dacă portul 8000 e ocupat
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### **Frontend nu pornește:**
```bash
# Șterge node_modules și reinstalează
rm -rf node_modules package-lock.json
npm install
npm start
```

### **Port 3000 ocupat:**
```bash
# Specifică alt port
PORT=3001 npm start
```

### **OAuth Error - "redirect_uri mismatch":**
- Verifică că rulezi pe `localhost:8000` (NU Codespaces URL!)
- Verifică că backend-ul rulează pe port 8000
- Asigură-te că ai codul LATEST de pe GitHub (cu localhost configurat)

### **MongoDB Connection Refused:**
- Nu e blocker! Backend folosește in-memory cache
- Token-urile funcționează, dar nu persistă după restart
- Optional: Pornește MongoDB pentru persistență

---

## 📊 VERIFICARE RAPIDĂ

### **Backend Health Check:**
```bash
curl http://localhost:8000/health
```

Răspuns așteptat:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "unusual_whales": "connected",
    "tradestation": "ready",
    "redis": "fallback_in_memory"
  }
}
```

### **Frontend Loaded:**
Deschide browser la `http://localhost:3000` - ar trebui să vezi homepage FlowMind

### **TradeStation Auth Status:**
```bash
curl http://localhost:8000/api/tradestation/auth/status
```

Înainte de login:
```json
{
  "status": "success",
  "data": {
    "authenticated": false,
    "expires_in": 0
  }
}
```

După login:
```json
{
  "status": "success",
  "data": {
    "authenticated": true,
    "expires_in": 1199
  }
}
```

---

## 🎉 SUCCESS CRITERIA

Știi că totul funcționează când:
1. ✅ Backend rulează pe `http://localhost:8000`
2. ✅ Frontend rulează pe `http://localhost:3000`
3. ✅ Vezi homepage FlowMind în browser
4. ✅ TradeStation OAuth te redirectează și se conectează
5. ✅ Vezi balanța SIMULATION în Account Balance
6. ✅ Flow page arată date LIVE de la Unusual Whales
7. ✅ Options chain arată prețuri LIVE de la TradeStation

---

## 📝 CONFIGURAȚIE

Toate configurările sunt deja setate pentru localhost:

### **Backend: `/backend/.env`**
```bash
TS_REDIRECT_URI=http://localhost:8000/api/oauth/tradestation/callback
TS_MODE=SIMULATION
```

### **Frontend: `/frontend/.env.local`**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### **TradeStationLogin.jsx**
```javascript
const REDIRECT_URI = 'http://localhost:8000/api/oauth/tradestation/callback';
const MODE = 'SIMULATION';
```

**TOATE configurate corect pentru localhost! Nu trebuie modificat nimic!** ✅

---

## 🆘 DACĂ AI PROBLEME

1. Verifică că backend-ul și frontend-ul rulează (ambele terminale active)
2. Verifică că folosești `localhost` (NU Codespaces URL!)
3. Verifică că ai ultimul cod de pe GitHub (`git pull origin main`)
4. Încearcă să oprești și să repornești ambele servicii
5. Verifică logs-urile în terminalele unde rulează serviciile

---

## 🚀 NEXT STEPS (după conectare)

1. **Explorează Flow Scanner** - vezi ce tranzacționează big money
2. **Testează Builder** - construiește strategii options
3. **Analizează GEX** - găsește support/resistance zones
4. **Rulează ALGOS** - testează algoritmi pe paper trading
5. **Monitorizează performance** - tracking P&L în timp real

---

**Configurat de**: GitHub Copilot  
**Pentru**: Gabriel (@barbudangabriel-gif)  
**Data**: 17 Octombrie 2025  
**Status**: ✅ READY TO RUN

**Tot codul e salvat pe GitHub! Mâine clonezi și rulezi local! 🎯**
