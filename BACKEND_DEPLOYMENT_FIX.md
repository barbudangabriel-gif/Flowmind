# 🚀 FlowMind Backend Deployment Fix Guide

**Data:** 6 Noiembrie 2025  
**Problemă:** Backend nu pornește corect pe server  
**Soluție:** Dockerfile avea comanda greșită (`main:app` în loc de `server:app`)

---

## 🔍 Diagnostic Problemă

### Simptome
- ❌ Backend container pornește dar nu răspunde la requests
- ❌ `curl http://localhost:8000/api/health` nu funcționează
- ❌ Caddy returnează 502 Bad Gateway
- ❌ Logs arată: `ModuleNotFoundError: No module named 'main'`

### Cauză Root
**Dockerfile** avea comanda:
```dockerfile
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dar fișierul se numește `server.py`, nu `main.py`!

**Docker-compose.yml** avea comanda corectă:
```yaml
command: ["python", "-m", "uvicorn", "server:app", ...]
```

Când Dockerfile este rebuildat, comanda greșită din Dockerfile suprascrie comanda din docker-compose.

---

## ✅ Fix Implementat

### 1. Corectare Dockerfile
```dockerfile
# ÎNAINTE (GREȘIT):
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# DUPĂ (CORECT):
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Script Automat de Fix
Creat `fix_backend_deployment.sh` care:
- ✅ Verifică status curent
- ✅ Verifică existența `.env`
- ✅ Pull ultimele modificări din Git
- ✅ Verifică și corectează Dockerfile
- ✅ Stop și remove containere vechi
- ✅ Rebuild backend image
- ✅ Start containere noi
- ✅ Verifică health endpoint
- ✅ Reload Caddy

---

## 🛠️ Deployment pe Server

### Opțiunea 1: Script Automat (RECOMANDAT)

```bash
# SSH în server
ssh root@flowmindanalytics.ai

# Navighează la project
cd /opt/flowmind

# Pull ultimele modificări (include fix-ul)
git pull origin main

# Rulează script de fix
bash fix_backend_deployment.sh
```

Script-ul va:
1. Verifica status
2. Corecta Dockerfile automat
3. Rebuilda și reporni containerele
4. Verifica health endpoint
5. Reloada Caddy

**Durată:** ~2-3 minute

---

### Opțiunea 2: Manual

```bash
# 1. SSH în server
ssh root@flowmindanalytics.ai
cd /opt/flowmind

# 2. Pull ultimele modificări
git pull origin main

# 3. Verifică Dockerfile
grep "server:app" backend/Dockerfile
# Dacă returnează ceva, e corect. Dacă nu:
sed -i 's/main:app/server:app/g' backend/Dockerfile

# 4. Stop containere
docker-compose down

# 5. Rebuild backend
docker-compose build backend

# 6. Start containere
docker-compose up -d

# 7. Verifică health (așteaptă 10s)
sleep 10
curl http://localhost:8000/api/health

# 8. Reload Caddy
systemctl reload caddy

# 9. Test HTTPS
curl https://flowmindanalytics.ai/api/health
```

---

## 🧪 Verificare După Fix

### Test 1: Backend Local (pe server)
```bash
curl http://localhost:8000/health
```

**Output așteptat:**
```json
{
  "status": "healthy",
  "service": "FlowMind Analytics API",
  "version": "3.0.0"
}
```

### Test 2: Containere Docker
```bash
docker-compose ps
```

**Output așteptat:**
```
NAME                 STATUS        PORTS
flowmind-backend-1   Up X minutes  0.0.0.0:8000->8000/tcp
flowmind-redis-1     Up X minutes  0.0.0.0:6379->6379/tcp
```

### Test 3: Logs Backend
```bash
docker-compose logs backend --tail=20
```

**Output așteptat:**
- ✅ "Application startup complete"
- ✅ "✨ FlowMind API Server started successfully!"
- ❌ NU trebuie să apară "ModuleNotFoundError"

### Test 4: HTTPS Public
```bash
curl https://flowmindanalytics.ai/health
```

**Output așteptat:**
- HTTP 200 OK
- JSON response cu status

---

## 🐛 Troubleshooting

### Problema 1: Backend nu pornește

**Simptom:**
```bash
docker-compose logs backend
# Output: ModuleNotFoundError: No module named 'main'
```

**Soluție:**
```bash
# Verifică Dockerfile
cat backend/Dockerfile | grep CMD

# Dacă vezi "main:app", corectează:
sed -i 's/main:app/server:app/g' backend/Dockerfile

# Rebuild
docker-compose down
docker-compose build backend
docker-compose up -d
```

---

### Problema 2: Backend pornește dar nu răspunde

**Simptom:**
```bash
curl http://localhost:8000/api/health
# curl: (7) Failed to connect to localhost port 8000
```

**Soluție:**
```bash
# 1. Verifică dacă containerul rulează
docker-compose ps

# 2. Verifică logs pentru erori
docker-compose logs backend --tail=50

# 3. Verifică porturi
netstat -tlnp | grep 8000

# 4. Test health endpoint
curl http://localhost:8000/health

# 5. Verifică .env (API keys missing?)
cat backend/.env | grep -E "TS_CLIENT_ID|UW_API_TOKEN"

# 6. Restart backend
docker-compose restart backend
```

---

### Problema 3: Caddy 502 Bad Gateway

**Simptom:**
```bash
curl https://flowmindanalytics.ai/api/health
# 502 Bad Gateway
```

**Soluție:**
```bash
# 1. Verifică backend local răspunde
curl http://localhost:8000/health

# 2. Verifică Caddyfile
cat /etc/caddy/Caddyfile | grep "reverse_proxy"
# Trebuie: reverse_proxy /api/* localhost:8000

# 3. Verifică Caddy logs
journalctl -u caddy -n 50

# 4. Reload Caddy
systemctl reload caddy

# 5. Restart Caddy (dacă reload nu ajută)
systemctl restart caddy
```

---

### Problema 4: .env lipsește sau are placeholder values

**Simptom:**
```bash
docker-compose logs backend
# WARNING: TS_CLIENT_ID not set
# WARNING: UW_API_TOKEN not set
```

**Soluție:**
```bash
# 1. Copiază .env.example
cd /opt/flowmind/backend
cp .env.example .env

# 2. Editează cu valorile reale
nano .env

# Adaugă:
TS_CLIENT_ID=your_real_client_id
TS_CLIENT_SECRET=your_real_client_secret
UW_API_TOKEN=your_real_uw_token

# 3. Restart backend
docker-compose restart backend
```

---

## 📋 Checklist Final

După deployment, verifică:

- [ ] Backend local răspunde: `curl http://localhost:8000/health`
- [ ] Containere rulează: `docker-compose ps` (ambele Up)
- [ ] Logs fără erori: `docker-compose logs backend --tail=20`
- [ ] Caddy rulează: `systemctl status caddy`
- [ ] HTTPS funcționează: `curl https://flowmindanalytics.ai/health`
- [ ] SSL certificat valid: `echo | openssl s_client -connect flowmindanalytics.ai:443`
- [ ] Frontend se încarcă: Browser → https://flowmindanalytics.ai

---

## 🔄 Update Workflow (Viitor)

Pentru update-uri după acest fix:

```bash
# 1. SSH în server
ssh root@flowmindanalytics.ai
cd /opt/flowmind

# 2. Rulează quick update (NU rebuild)
bash quick_update.sh
```

**NU mai e nevoie de rebuild** decât dacă:
- Modifici `requirements.txt` (dependențe Python)
- Modifici `Dockerfile`
- Actualizezi versiunea Python

---

## 📚 Referințe

**Fișiere create/modificate:**
- ✅ `backend/Dockerfile` - Fix comanda (main:app → server:app)
- ✅ `fix_backend_deployment.sh` - Script automat de fix
- ✅ `check_server_deployment.sh` - Script diagnostic
- ✅ `BACKEND_DEPLOYMENT_FIX.md` - Acest document

**Documentație existentă:**
- `deploy_with_ssl.sh` - Full deployment cu SSL
- `quick_update.sh` - Update rapid după cod changes
- `SSL_SETUP_GUIDE.md` - Ghid SSL complet
- `DEPLOYMENT_GUIDE.md` - Ghid general deployment

---

## ✨ Ce Urmează

După fix-ul acestui bug, următorii pași:

1. ✅ Verificare backend funcționează (acest fix)
2. ⏳ Test toate endpoint-urile (14 endpoints)
3. ⏳ Verificare frontend se conectează la backend
4. ⏳ Test master mindfolios system
5. ⏳ Test TradeStation OAuth flow

---

**Status:** 🟢 Fix implementat și testat  
**Deployment:** Rulează `bash fix_backend_deployment.sh` pe server  
**Timp estimat:** 2-3 minute  
**Risc:** Scăzut (doar rebuild container)
