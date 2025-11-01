# FlowMind Production Deployment Guide

**Complete step-by-step guide for deploying FlowMind to Hetzner VPS**

Last Updated: November 1, 2025
Production URL: https://flowmindanalytics.ai

---

## 📋 Prerequisites

### Required Accounts & Credentials
- ✅ Hetzner Cloud account
- ✅ Domain name (e.g., flowmindanalytics.ai)
- ✅ Cloudflare account (for DNS management)
- ✅ GitHub account with repository access
- ✅ TradeStation API credentials (Client ID, Secret)
- ✅ Unusual Whales API token

### Local Requirements
- SSH client (Windows CMD/PowerShell, Linux/Mac Terminal)
- Git installed locally
- Text editor for configuration files

---

## 🚀 Part 1: Server Setup on Hetzner

### Step 1: Create Server

1. **Login to Hetzner Cloud Console**
   - Go to: https://console.hetzner.cloud/

2. **Create New Project**
   - Name: `FlowMind Production`

3. **Add Server**
   - **Location:** Falkenstein, Germany (or nearest to your users)
   - **Image:** Ubuntu 24.04 LTS
   - **Type:** CPX31 (4 vCPU, 8GB RAM, 80GB SSD)
   - **Cost:** €12.90/month
   - **Networking:** 
     - IPv4: ✅ Enabled
     - IPv6: ⬜ Optional
   - **SSH Key:** Add your public key (or create new one - see below)
   - **Server Name:** `Flowmind-prod`

4. **Note Server IP Address**
   - Example: `91.107.206.64`
   - Save this IP for DNS configuration

### Step 2: Generate SSH Key (if needed)

**Windows (PowerShell):**
```powershell
ssh-keygen -t ed25519 -C "flowmind-production" -f %USERPROFILE%\.ssh\flowmind_key
```

**Linux/Mac:**
```bash
ssh-keygen -t ed25519 -C "flowmind-production" -f ~/.ssh/flowmind_key
```

**Add Public Key to Hetzner:**
- Copy content of `flowmind_key.pub`
- Paste in Hetzner → SSH Keys section

### Step 3: Initial Connection

**Windows:**
```cmd
ssh -i %USERPROFILE%\.ssh\flowmind_key root@YOUR_SERVER_IP
```

**Linux/Mac:**
```bash
ssh -i ~/.ssh/flowmind_key root@YOUR_SERVER_IP
```

---

## 🌐 Part 2: DNS Configuration

### Cloudflare Setup

1. **Login to Cloudflare Dashboard**
   - Go to: https://dash.cloudflare.com/

2. **Select Your Domain**
   - Example: `flowmindanalytics.ai`

3. **Add DNS Records**

**A Record (Root Domain):**
```
Type: A
Name: @
IPv4: YOUR_SERVER_IP (e.g., 91.107.206.64)
Proxy status: DNS only (gray cloud)
TTL: Auto
```

**CNAME Record (www subdomain):**
```
Type: CNAME
Name: www
Target: flowmindanalytics.ai
Proxy status: DNS only (gray cloud)
TTL: Auto
```

4. **Verify DNS Propagation**
```bash
# Test from local machine
nslookup flowmindanalytics.ai
ping flowmindanalytics.ai
```

**Note:** DNS propagation can take 5-30 minutes

---

## 🔧 Part 3: Server Software Installation

**Connect to server and execute these commands:**

### Update System
```bash
apt-get update && apt-get upgrade -y
```

### Install Docker
```bash
# Add Docker's official GPG key
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Install Caddy (Web Server + Automatic HTTPS)
```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy

# Verify installation
caddy version
systemctl status caddy
```

### Install Git
```bash
apt-get install -y git

# Verify installation
git --version
```

### Configure Firewall (UFW)
```bash
# Install UFW
apt-get install -y ufw

# Allow SSH (port 22)
ufw allow 22/tcp

# Allow HTTP (port 80)
ufw allow 80/tcp

# Allow HTTPS (port 443)
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Verify rules
ufw status
```

### Install Node.js (for frontend build)
```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

# Install Node.js
apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

---

## 📦 Part 4: Clone and Configure Application

### Clone Repository
```bash
# Create application directory
mkdir -p /opt/flowmind
cd /opt/flowmind

# Clone FlowMind repository
git clone https://github.com/barbudangabriel-gif/Flowmind.git .

# Verify clone
ls -la
```

### Create Environment Variables
```bash
# Copy environment template
cp deploy/.env.production.example .env

# Edit environment file (use nano or cat)
nano .env
```

**Environment Variables Configuration:**
```bash
# FlowMind Production Environment Variables

# TradeStation OAuth Credentials
TS_CLIENT_ID=YOUR_TRADESTATION_CLIENT_ID
TS_CLIENT_SECRET=YOUR_TRADESTATION_CLIENT_SECRET
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback
TS_MODE=LIVE

# Unusual Whales API
UW_API_TOKEN=YOUR_UNUSUAL_WHALES_TOKEN

# Domain Configuration
DOMAIN=flowmindanalytics.ai
CORS_ORIGINS=https://flowmindanalytics.ai,https://www.flowmindanalytics.ai

# Backend Configuration
UVICORN_WORKERS=4
REDIS_URL=redis://redis:6379/0
```

**Save and exit:**
- Nano: `Ctrl+X`, then `Y`, then `Enter`
- Or use heredoc method (see Troubleshooting section)

### Create Caddyfile
```bash
cat > deploy/Caddyfile << 'EOF'
flowmindanalytics.ai, www.flowmindanalytics.ai {
    root * /opt/flowmind/frontend/build
    try_files {path} /index.html

    handle /api/* {
        reverse_proxy localhost:8000
    }

    handle /ws/* {
        reverse_proxy localhost:8000
    }

    encode gzip zstd

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }

    @static {
        path *.js *.css *.png *.jpg *.jpeg *.gif *.ico *.woff *.woff2 *.svg
    }
    header @static Cache-Control "public, max-age=31536000, immutable"

    log {
        output file /var/log/caddy/flowmind-access.log
        format json
    }

    file_server
}
EOF
```

---

## 🏗️ Part 5: Build and Deploy

### Build Frontend
```bash
cd /opt/flowmind/frontend

# Install dependencies (takes 2-3 minutes)
npm install

# Build production frontend (takes 1-2 minutes)
REACT_APP_BACKEND_URL="" npm run build

# Verify build
ls -lh build/
```

### Start Docker Containers
```bash
cd /opt/flowmind

# Start backend + Redis
docker compose up -d

# Verify containers are running
docker ps

# Check backend logs
docker logs flowmind-backend-1 --tail 20
```

**Expected output:**
```
✨ FlowMind API Server started successfully!
Application startup complete.
```

### Configure and Start Caddy
```bash
# Create log directory
mkdir -p /var/log/caddy
chown -R caddy:caddy /var/log/caddy

# Copy Caddyfile to Caddy config directory
cp /opt/flowmind/deploy/Caddyfile /etc/caddy/Caddyfile

# Validate configuration
caddy validate --config /etc/caddy/Caddyfile

# Start Caddy
systemctl start caddy

# Check status
systemctl status caddy

# Verify Caddy is listening
ss -tulpn | grep :443
```

**Wait 1-2 minutes for Let's Encrypt SSL certificate generation**

---

## ✅ Part 6: Verification

### Test Backend Health
```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"healthy"}`

### Test HTTPS
```bash
curl -I https://flowmindanalytics.ai
```

**Expected:** `HTTP/2 200`

### Check SSL Certificate
```bash
journalctl -u caddy -n 50 --no-pager | grep -i "certificate"
```

**Expected:**
```
certificate obtained successfully for flowmindanalytics.ai
certificate obtained successfully for www.flowmindanalytics.ai
```

### Open in Browser
Navigate to: **https://flowmindanalytics.ai**

**Verify:**
- ✅ Green padlock (SSL valid)
- ✅ FlowMind frontend loads
- ✅ No console errors
- ✅ API calls working

---

## 🔄 Part 7: Updates and Maintenance

### Update Application Code
```bash
cd /opt/flowmind

# Pull latest changes
git pull origin main

# Rebuild backend
docker compose up -d --build backend

# Rebuild frontend (if needed)
cd frontend
npm install
REACT_APP_BACKEND_URL="" npm run build

# Reload Caddy (if Caddyfile changed)
systemctl reload caddy
```

### View Logs
```bash
# Backend logs
docker logs flowmind-backend-1 -f

# Caddy logs
journalctl -u caddy -f

# System logs
journalctl -xe
```

### Restart Services
```bash
# Restart Docker containers
docker compose restart

# Restart Caddy
systemctl restart caddy

# Restart all
docker compose restart && systemctl restart caddy
```

### Monitor Resources
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top

# Docker stats
docker stats
```

---

## 🐛 Troubleshooting

### Issue: Nano editor arrow keys not working

**Solution:** Use heredoc method instead:
```bash
cat > filename << 'EOF'
[paste content here]
EOF
```

### Issue: Port 8000 refused connection

**Check backend logs:**
```bash
docker logs flowmind-backend-1 --tail 50
```

**Restart backend:**
```bash
docker compose restart backend
```

### Issue: Caddy fails to start

**Common causes:**
1. Log directory doesn't exist
```bash
mkdir -p /var/log/caddy
chown -R caddy:caddy /var/log/caddy
```

2. Port 80/443 already in use
```bash
netstat -tulpn | grep -E ':(80|443)'
```

3. Invalid Caddyfile syntax
```bash
caddy validate --config /etc/caddy/Caddyfile
```

### Issue: SSL certificate not generated

**Verify DNS points to server:**
```bash
nslookup flowmindanalytics.ai
```

**Check Caddy logs:**
```bash
journalctl -u caddy -n 100 --no-pager | grep -i "acme"
```

**Ensure DNS is not proxied through Cloudflare:**
- Go to Cloudflare DNS settings
- Set Proxy status to "DNS only" (gray cloud)

### Issue: Git pull fails with local changes

**Reset to remote version:**
```bash
git fetch origin
git reset --hard origin/main
```

### Issue: Frontend shows "Failed to fetch"

**Check CORS configuration in .env:**
```bash
cat .env | grep CORS
```

**Verify backend is accessible:**
```bash
curl http://localhost:8000/health
```

### Issue: Python syntax errors on startup

**Known fix:** Multi-line f-strings must be on single line
```python
# ❌ Wrong
logger.info(
    f"Message {
        variable
    }"
)

# ✅ Correct
logger.info(
    f"Message {variable}"
)
```

---

## 📊 Monitoring and Alerts

### Setup Automatic Restarts
```bash
# Docker containers restart automatically (default policy)
docker inspect flowmind-backend-1 | grep -A 5 RestartPolicy

# Caddy restarts on failure (systemd default)
systemctl show caddy | grep Restart
```

### Disk Space Monitoring
```bash
# Check Docker disk usage
docker system df

# Clean up unused Docker resources
docker system prune -a
```

### Log Rotation
Caddy logs are automatically rotated. For Docker logs:
```bash
# Edit Docker daemon config
nano /etc/docker/daemon.json
```

Add:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
systemctl restart docker
docker compose up -d
```

---

## 🔒 Security Best Practices

### 1. Keep System Updated
```bash
# Run weekly
apt-get update && apt-get upgrade -y
```

### 2. Configure Fail2Ban (SSH protection)
```bash
apt-get install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Disable Root Password Login
```bash
nano /etc/ssh/sshd_config
```

Set:
```
PermitRootLogin prohibit-password
PasswordAuthentication no
```

Restart SSH:
```bash
systemctl restart sshd
```

### 4. Setup Automatic Security Updates
```bash
apt-get install -y unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

### 5. Backup Environment Variables
Store `.env` file securely offline (encrypted)

---

## 💾 Backup and Recovery

### Manual Backup
```bash
# Create backup directory
mkdir -p /root/backups

# Backup environment
cp /opt/flowmind/.env /root/backups/env-$(date +%Y%m%d).bak

# Backup Caddyfile
cp /etc/caddy/Caddyfile /root/backups/Caddyfile-$(date +%Y%m%d).bak

# Backup Redis data (if persistent)
docker exec flowmind-redis-1 redis-cli SAVE
cp /var/lib/docker/volumes/flowmind_redis-data/_data/dump.rdb /root/backups/
```

### Automated Backup Script
```bash
cat > /root/backup-flowmind.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d-%H%M)

mkdir -p $BACKUP_DIR

# Backup configs
cp /opt/flowmind/.env $BACKUP_DIR/env-$DATE.bak
cp /etc/caddy/Caddyfile $BACKUP_DIR/Caddyfile-$DATE.bak

# Backup Redis
docker exec flowmind-redis-1 redis-cli SAVE
cp /var/lib/docker/volumes/flowmind_redis-data/_data/dump.rdb $BACKUP_DIR/redis-$DATE.rdb

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup-flowmind.sh

# Add to cron (daily at 2 AM)
crontab -e
```

Add line:
```
0 2 * * * /root/backup-flowmind.sh >> /var/log/flowmind-backup.log 2>&1
```

### Disaster Recovery
```bash
# Stop services
docker compose down
systemctl stop caddy

# Restore environment
cp /root/backups/env-YYYYMMDD.bak /opt/flowmind/.env

# Restore Caddyfile
cp /root/backups/Caddyfile-YYYYMMDD.bak /etc/caddy/Caddyfile

# Restore Redis data
cp /root/backups/redis-YYYYMMDD.rdb /var/lib/docker/volumes/flowmind_redis-data/_data/dump.rdb

# Restart services
docker compose up -d
systemctl start caddy
```

---

## 📈 Performance Optimization

### 1. Enable Redis Persistence
Edit `docker-compose.yml`:
```yaml
redis:
  command: redis-server --appendonly yes
```

### 2. Increase Docker Resources
Edit `/etc/docker/daemon.json`:
```json
{
  "default-ulimits": {
    "nofile": {
      "Hard": 64000,
      "Name": "nofile",
      "Soft": 64000
    }
  }
}
```

### 3. Caddy Optimizations
Already configured in Caddyfile:
- ✅ Gzip/Zstd compression
- ✅ Static file caching (1 year)
- ✅ HTTP/2 enabled by default

### 4. Backend Workers
In `.env`:
```
UVICORN_WORKERS=4  # Set to number of CPU cores
```

---

## 📞 Support and Resources

### Documentation
- FlowMind Repo: https://github.com/barbudangabriel-gif/Flowmind
- Docker Docs: https://docs.docker.com/
- Caddy Docs: https://caddyserver.com/docs/
- Hetzner Docs: https://docs.hetzner.com/

### Useful Commands Cheat Sheet
```bash
# Quick status check
docker ps && systemctl status caddy

# View all logs
docker logs flowmind-backend-1 -f & journalctl -u caddy -f

# Full restart
docker compose restart && systemctl restart caddy

# Check resource usage
docker stats --no-stream

# Test backend health
curl http://localhost:8000/health

# Test HTTPS
curl -I https://flowmindanalytics.ai

# Update everything
cd /opt/flowmind && git pull && docker compose up -d --build && systemctl reload caddy
```

---

## ✅ Deployment Checklist

Use this checklist for each deployment:

**Pre-Deployment:**
- [ ] Server created on Hetzner
- [ ] DNS configured in Cloudflare
- [ ] SSH key generated and tested
- [ ] API credentials ready (TradeStation, Unusual Whales)

**Installation:**
- [ ] System updated
- [ ] Docker installed and running
- [ ] Caddy installed and running
- [ ] Git installed
- [ ] Node.js installed
- [ ] Firewall configured (ports 22, 80, 443)

**Configuration:**
- [ ] Repository cloned to `/opt/flowmind`
- [ ] `.env` file created with correct credentials
- [ ] `Caddyfile` created with correct domain
- [ ] Log directory created (`/var/log/caddy`)

**Build:**
- [ ] Frontend built (`npm install && npm run build`)
- [ ] Backend containers started (`docker compose up -d`)
- [ ] Backend logs show "Application startup complete"

**Caddy Setup:**
- [ ] Caddyfile copied to `/etc/caddy/`
- [ ] Configuration validated (`caddy validate`)
- [ ] Caddy started (`systemctl start caddy`)
- [ ] SSL certificates obtained (check logs)

**Verification:**
- [ ] Backend health check returns 200 (`curl localhost:8000/health`)
- [ ] HTTPS returns 200 (`curl -I https://domain.com`)
- [ ] Website loads in browser
- [ ] SSL certificate valid (green padlock)
- [ ] API calls working (check browser console)

**Post-Deployment:**
- [ ] Backup script configured
- [ ] Monitoring setup
- [ ] Documentation updated
- [ ] Team notified

---

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ `https://flowmindanalytics.ai` loads in browser
2. ✅ SSL certificate is valid (green padlock)
3. ✅ No console errors in browser DevTools
4. ✅ Backend responds to `/health` endpoint
5. ✅ WebSocket connections work (live data updates)
6. ✅ All Docker containers running (`docker ps`)
7. ✅ Caddy service active (`systemctl status caddy`)

**Congratulations! FlowMind is now live in production! 🚀**

---

## 📝 Changelog

### 2025-11-01
- Initial production deployment
- Hetzner CPX31 server (91.107.206.64)
- Domain: flowmindanalytics.ai
- SSL: Let's Encrypt automatic certificates
- Fixed Python f-string syntax errors
- All services operational

---

**For questions or issues, refer to the Troubleshooting section or check repository issues.**
