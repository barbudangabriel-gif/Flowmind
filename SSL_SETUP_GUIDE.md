# 🔒 SSL Setup Guide - FlowMind Production

**Data:** November 5, 2025  
**Domain:** flowmindanalytics.ai  
**SSH Key Fingerprint:** `62:be:3c:43:8c:bb:c3:10:81:ae:ac:41:c3:a7:2d:4a`

---

## 📋 Ce Face SSL-ul Automat

**Caddy** instalat pe server obține automat certificate SSL de la **Let's Encrypt** (GRATUIT).

**Nu trebuie să:**
- Plătești pentru certificate SSL
- Configurezi manual nginx/Apache
- Reînnoiești manual certificatele (Caddy face automat la 60 zile)

**Trebuie doar să:**
1. DNS-ul să fie configurat corect (A record → IP server)
2. Portul 443 (HTTPS) să fie deschis
3. Caddy să fie configurat cu domeniul tău

---

## 🚀 Pași de Configurare SSL

### Pas 1: Conectare la Server

**Deschide Terminal/CMD și conectează-te:**

```bash
ssh root@YOUR_SERVER_IP
```

**Exemplu cu IP-ul tău:**
```bash
ssh root@91.107.206.64
# SAU dacă DNS e setat:
ssh root@flowmindanalytics.ai
```

Când întreabă despre fingerprint, verifică că este:
```
62:be:3c:43:8c:bb:c3:10:81:ae:ac:41:c3:a7:2d:4a
```

---

### Pas 2: Verifică că Caddy Este Instalat

```bash
caddy version
```

**Dacă NU este instalat, rulează:**
```bash
# Adaugă Caddy repository
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

# Instalează Caddy
apt update
apt install -y caddy

# Verifică instalarea
caddy version
systemctl enable caddy
```

---

### Pas 3: Verifică DNS (FOARTE IMPORTANT!)

**SSL nu va funcționa dacă DNS nu este configurat corect!**

```bash
# Verifică că domeniul tău rezolvă la IP-ul serverului
dig flowmindanalytics.ai +short
# SAU
nslookup flowmindanalytics.ai
```

**Trebuie să vezi IP-ul serverului tău!**

**Dacă NU vezi IP-ul corect:**
1. Intră în Cloudflare/DNS provider
2. Adaugă A record:
   - **Type:** A
   - **Name:** @ (pentru flowmindanalytics.ai)
   - **IPv4:** YOUR_SERVER_IP
   - **Proxy:** OFF (gray cloud, NU orange!)
   - **TTL:** Auto

3. Adaugă A record pentru www:
   - **Type:** A
   - **Name:** www
   - **IPv4:** YOUR_SERVER_IP
   - **Proxy:** OFF
   - **TTL:** Auto

**Așteaptă 2-5 minute și verifică din nou DNS-ul.**

---

### Pas 4: Deploy FlowMind pe Server

```bash
# Navighează în directorul FlowMind
cd /opt/flowmind

# Pull ultimele modificări
git pull origin main

# Build frontend pentru producție
cd frontend
npm install
echo 'REACT_APP_BACKEND_URL=http://localhost:8080' > .env.production
npm run build
cd ..

# Configurare backend .env
cd backend
cp .env.example .env
nano .env
# Adaugă TS_CLIENT_ID, TS_CLIENT_SECRET, UW_API_TOKEN
cd ..

# Start Docker containers (backend + Redis)
docker-compose up -d

# Verifică că backend rulează
curl http://localhost:8000/health
# Trebuie să vezi: {"status":"healthy"}
```

---

### Pas 5: Configurează Caddy pentru SSL

```bash
# Creează director pentru log-uri
mkdir -p /var/log/caddy
chown -R caddy:caddy /var/log/caddy

# Copiază Caddyfile cu autentificare și SSL
cp /opt/flowmind/Caddyfile.with-auth /etc/caddy/Caddyfile

# Verifică configurația
caddy validate --config /etc/caddy/Caddyfile
```

**Dacă `caddy validate` dă erori, verifică că:**
- Domeniul din Caddyfile este corect (flowmindanalytics.ai)
- Frontend build directory există: `/opt/flowmind/frontend/build`
- Backend rulează pe localhost:8000

---

### Pas 6: Pornește Caddy (SSL Se Configurează Automat!)

```bash
# Restart Caddy
systemctl restart caddy

# Verifică status
systemctl status caddy
```

**Caddy va:**
1. Detecta domeniul din Caddyfile (flowmindanalytics.ai)
2. Contacta Let's Encrypt
3. Obține certificat SSL (durează 30-60 secunde)
4. Configura automat HTTPS

**Vezi log-urile în timp real:**
```bash
journalctl -u caddy -f
```

**Cauți în log-uri:**
```
✅ "certificate obtained successfully"
✅ "serving https"
✅ "automatic https enabled"
```

**Dacă vezi erori:**
- `DNS: no such host` → DNS nu este configurat corect
- `timeout` → Portul 443 este blocat în firewall
- `rate limit` → Prea multe cereri, așteaptă 1 oră

---

### Pas 7: Verifică SSL

**Din browser:**
```
https://flowmindanalytics.ai
```

Trebuie să vezi:
- 🔒 Lacăt verde în browser
- HTTP Basic Auth prompt (Username: gabriel, Password: FlowMind2025!)
- FlowMind dashboard după autentificare

**Din terminal (pe server):**
```bash
# Test HTTPS
curl -I https://flowmindanalytics.ai

# Verifică certificatul
echo | openssl s_client -connect flowmindanalytics.ai:443 -servername flowmindanalytics.ai 2>/dev/null | openssl x509 -noout -dates

# Trebuie să vezi:
# notBefore: Nov 5 XX:XX:XX 2025 GMT
# notAfter: Feb 3 XX:XX:XX 2026 GMT (90 zile validitate)
```

---

## 🔧 Troubleshooting

### Problema: "Connection Refused" pe port 443

**Verifică că portul 443 este deschis:**
```bash
# Verifică firewall
ufw status

# Dacă 443 nu este listat, deschide-l:
ufw allow 443/tcp
ufw reload
```

**Verifică că Caddy ascultă pe 443:**
```bash
ss -tulpn | grep :443
# Trebuie să vezi caddy
```

---

### Problema: "DNS Resolution Failed"

**Verifică DNS din mai multe locații:**
```bash
# De pe server
dig flowmindanalytics.ai +short

# De pe alt computer
# Windows CMD:
nslookup flowmindanalytics.ai

# Trebuie să vezi IP-ul serverului (ex: 91.107.206.64)
```

**Dacă DNS nu este corect:**
- Așteaptă 5-15 minute (propagare DNS)
- Verifică Cloudflare că A record există
- Asigură-te că Proxy este OFF (gray cloud)

---

### Problema: "Rate Limit Exceeded" (Let's Encrypt)

Let's Encrypt are limite:
- **50 certificate/săptămână** per domeniu
- **5 duplicate certificate/săptămână**

**Soluție:**
```bash
# Folosește staging environment pentru teste
# Editează /etc/caddy/Caddyfile și adaugă la început:
{
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}

# Restart Caddy
systemctl restart caddy

# După ce funcționează, elimină liniile de staging și restart
```

---

### Problema: Certificat expirat sau invalid

**Caddy reînnoiește automat la 60 zile, dar dacă vrei forțat:**
```bash
# Șterge certificatul vechi
rm -rf /var/lib/caddy/.local/share/caddy/certificates/acme-v02.api.letsencrypt.org-directory/*

# Restart Caddy (va obține certificat nou)
systemctl restart caddy
```

---

## 📊 Verificare Finală - Checklist

După configurare, verifică toate acestea:

```bash
# 1. DNS rezolvă corect
dig flowmindanalytics.ai +short
# ✅ Trebuie să vezi IP-ul serverului

# 2. Backend rulează
curl http://localhost:8000/health
# ✅ Trebuie: {"status":"healthy"}

# 3. Caddy rulează
systemctl status caddy
# ✅ Trebuie: active (running)

# 4. Caddy ascultă pe 443
ss -tulpn | grep :443
# ✅ Trebuie să vezi caddy

# 5. HTTPS funcționează
curl -I https://flowmindanalytics.ai
# ✅ Trebuie: HTTP/2 200

# 6. Certificat valid
echo | openssl s_client -connect flowmindanalytics.ai:443 -servername flowmindanalytics.ai 2>/dev/null | openssl x509 -noout -dates
# ✅ Trebuie: notAfter în viitor (90 zile)

# 7. Redirect HTTP → HTTPS
curl -I http://flowmindanalytics.ai
# ✅ Trebuie: 301 sau 308 redirect la https://
```

---

## 🔄 Update Site (După Setup Inițial)

**Când faci modificări în cod și vrei să le publici:**

```bash
# 1. Conectează-te la server
ssh root@flowmindanalytics.ai

# 2. Pull ultimele modificări
cd /opt/flowmind
git pull origin main

# 3. Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# 4. Restart backend (dacă ai modificat Python)
docker-compose restart backend

# 5. Reload Caddy (dacă ai modificat Caddyfile)
systemctl reload caddy

# 6. Verifică că totul funcționează
curl https://flowmindanalytics.ai/api/health
```

**Gata! Site-ul este actualizat cu SSL activ!** 🎉

---

## 📞 Support

**Dacă întâmpini probleme:**

1. **Verifică log-urile Caddy:**
   ```bash
   journalctl -u caddy -n 100 --no-pager
   ```

2. **Verifică log-urile backend:**
   ```bash
   docker-compose logs backend --tail=50
   ```

3. **Test manual SSL:**
   ```bash
   curl -v https://flowmindanalytics.ai 2>&1 | grep -i ssl
   ```

---

## 🎯 Rezumat Rapid

**Pentru a activa SSL:**

```bash
# Pe server (ca root)
cd /opt/flowmind
git pull origin main
cd frontend && npm install && npm run build && cd ..
docker-compose up -d
cp Caddyfile.with-auth /etc/caddy/Caddyfile
systemctl restart caddy

# Verifică
curl -I https://flowmindanalytics.ai
```

**Asta e tot! SSL se configurează automat!** ✅
