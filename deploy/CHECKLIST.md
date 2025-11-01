# ✅ FlowMind Deployment Checklist

Use this checklist when deploying to Hetzner production.

---

## 📋 Pre-Deployment

### Hetzner Setup
- [ ] Hetzner account created
- [ ] Server created (CPX21 or CPX31)
- [ ] SSH key added to server
- [ ] Server IP noted: `___.___.___.___`

### Domain Setup
- [ ] Domain purchased/available
- [ ] DNS A record added: `@` → Server IP
- [ ] DNS A record added: `www` → Server IP
- [ ] DNS propagation verified (15 min wait)
  ```bash
  nslookup your-domain.com 8.8.8.8
  ```

### API Keys Ready
- [ ] TradeStation Client ID
- [ ] TradeStation Client Secret
- [ ] Unusual Whales API Token
- [ ] TradeStation redirect URI prepared: `https://your-domain.com/api/oauth/tradestation/callback`

---

## 🛠️ Server Setup (First Time Only)

- [ ] SSH into server
  ```bash
  ssh root@YOUR_SERVER_IP
  ```

- [ ] Download setup script
  ```bash
  apt-get update && apt-get install -y curl
  curl -o setup.sh https://raw.githubusercontent.com/barbudangabriel-gif/Flowmind/main/deploy/hetzner-setup.sh
  chmod +x setup.sh
  ./setup.sh
  ```

- [ ] Wait for setup to complete (~10 minutes)
- [ ] Log out and back in
  ```bash
  exit
  ssh root@YOUR_SERVER_IP
  ```

---

## 📦 Application Deployment

- [ ] Clone repository
  ```bash
  cd /opt/flowmind
  git clone https://github.com/barbudangabriel-gif/Flowmind.git .
  ```

- [ ] Create production environment file
  ```bash
  cp deploy/.env.production.example deploy/.env.production
  nano deploy/.env.production
  ```

- [ ] Fill in environment variables:
  - [ ] `TS_CLIENT_ID=___`
  - [ ] `TS_CLIENT_SECRET=___`
  - [ ] `TS_REDIRECT_URI=https://your-domain.com/api/oauth/tradestation/callback`
  - [ ] `UW_API_TOKEN=___`
  - [ ] `DOMAIN=your-domain.com`
  - [ ] `CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com`

- [ ] Update Caddyfile
  ```bash
  nano deploy/Caddyfile
  # Replace "your-domain.com" with actual domain (2 places)
  ```

- [ ] Run deployment
  ```bash
  chmod +x deploy/*.sh
  ./deploy/production-deploy.sh
  ```

- [ ] Wait for deployment (~5-10 minutes)

---

## 🔍 Verification

### Backend Health
- [ ] Test health endpoint
  ```bash
  curl http://localhost:8000/health
  ```
  **Expected:** `{"status":"ok","timestamp":"..."}`

### Redis
- [ ] Test Redis connection
  ```bash
  docker exec flowmind-redis redis-cli ping
  ```
  **Expected:** `PONG`

### Docker Containers
- [ ] Check all containers running
  ```bash
  cd /opt/flowmind
  docker-compose -f deploy/docker-compose.production.yml ps
  ```
  **Expected:** Both `flowmind-backend` and `flowmind-redis` in "Up" state

### SSL Certificate
- [ ] Check Caddy status
  ```bash
  sudo systemctl status caddy
  ```
  **Expected:** `active (running)`

- [ ] Test HTTPS (wait 2-5 min for cert)
  ```bash
  curl -I https://your-domain.com
  ```
  **Expected:** `HTTP/2 200` with valid SSL

### Frontend
- [ ] Open browser: `https://your-domain.com`
  **Expected:** FlowMind homepage loads

- [ ] Check browser console (F12)
  **Expected:** No errors

### Backend API
- [ ] Test API endpoint
  ```bash
  curl https://your-domain.com/api/health
  ```
  **Expected:** `{"status":"ok",...}`

### TradeStation OAuth
- [ ] Navigate to `https://your-domain.com/builder`
- [ ] Click TradeStation login
- [ ] Complete OAuth flow
  **Expected:** Successful redirect back to app

---

## 🔄 Post-Deployment

### Setup Backups
- [ ] Test backup script
  ```bash
  /opt/flowmind/deploy/backup.sh
  ```

- [ ] Add to crontab (daily at 2 AM)
  ```bash
  crontab -e
  # Add line:
  0 2 * * * /opt/flowmind/deploy/backup.sh >> /opt/flowmind/logs/backup.log 2>&1
  ```

### Setup Monitoring (Optional)
- [ ] Create monitoring script
  ```bash
  cat > /opt/flowmind/monitor.sh << 'EOF'
  #!/bin/bash
  if ! curl -sf http://localhost:8000/health > /dev/null; then
      echo "Backend down! Restarting..."
      cd /opt/flowmind
      docker-compose -f deploy/docker-compose.production.yml restart backend
  fi
  EOF
  chmod +x /opt/flowmind/monitor.sh
  ```

- [ ] Add to crontab (every 5 minutes)
  ```bash
  crontab -e
  # Add line:
  */5 * * * * /opt/flowmind/monitor.sh >> /opt/flowmind/logs/monitor.log 2>&1
  ```

### Security Hardening
- [ ] Disable password SSH authentication
  ```bash
  sudo nano /etc/ssh/sshd_config
  # Set: PasswordAuthentication no
  sudo systemctl restart sshd
  ```

- [ ] Enable automatic security updates
  ```bash
  sudo apt-get install -y unattended-upgrades
  sudo dpkg-reconfigure -plow unattended-upgrades
  ```

---

## 📊 Performance Check

- [ ] Test load time: `curl -w "Time: %{time_total}s\n" -o /dev/null -s https://your-domain.com`
  **Expected:** < 2 seconds

- [ ] Check memory usage: `free -h`
  **Expected:** < 50% used (on CPX21)

- [ ] Check disk usage: `df -h`
  **Expected:** < 20% used

---

## 📝 Documentation

- [ ] Update TradeStation Developer Portal with production redirect URI
- [ ] Document server IP in password manager
- [ ] Save SSH key securely
- [ ] Share production URL with team

---

## 🎉 Launch!

- [ ] Announce to users
- [ ] Monitor logs for first 24 hours
  ```bash
  docker-compose -f deploy/docker-compose.production.yml logs -f
  ```

---

## 🆘 If Something Goes Wrong

1. Check logs: `docker-compose -f /opt/flowmind/deploy/docker-compose.production.yml logs`
2. Run diagnostic: `bash /opt/flowmind/diagnose.sh`
3. Consult troubleshooting guide: `deploy/TROUBLESHOOTING.md`
4. Restore from backup if needed

---

**Estimated Total Time:** 45-60 minutes (excluding DNS propagation)

**Cost:** ~€7-13/month (depending on server size)

**Support:** https://github.com/barbudangabriel-gif/Flowmind/issues
