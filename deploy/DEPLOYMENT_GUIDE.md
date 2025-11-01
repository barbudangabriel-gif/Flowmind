# 🚀 FlowMind Hetzner Deployment Guide

**Date:** November 1, 2025  
**Target:** Hetzner Cloud VPS  
**Stack:** Docker + Caddy + Redis

---

## 📋 Prerequisites

1. **Hetzner Account** - Sign up at https://www.hetzner.com/cloud
2. **Domain** - Point your domain to server IP (A record)
3. **API Keys Ready:**
   - TradeStation OAuth credentials
   - Unusual Whales API token

---

## 💰 Server Recommendation

### CPX21 (Recommended for start)
- **Specs:** 3 vCPU, 4GB RAM, 80GB SSD
- **Price:** ~€7/month
- **Location:** Falkenstein or Nuremberg (EU)
- **OS:** Ubuntu 24.04 LTS

### CPX31 (For scaling)
- **Specs:** 4 vCPU, 8GB RAM, 160GB SSD
- **Price:** ~€13/month

---

## 🛠️ Setup Steps

### 1. Create Hetzner Server

```bash
# On Hetzner Cloud Console:
1. Create new project "FlowMind"
2. Add Server → CPX21
3. Location: Falkenstein (Germany)
4. Image: Ubuntu 24.04
5. Add SSH key
6. Name: flowmind-prod
7. Create & Start
```

### 2. Initial Server Setup

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Download and run setup script
apt-get update && apt-get install -y curl
curl -o setup.sh https://raw.githubusercontent.com/barbudangabriel-gif/Flowmind/main/deploy/hetzner-setup.sh
chmod +x setup.sh
./setup.sh

# After setup completes, log out and back in for docker group to take effect
exit
ssh root@YOUR_SERVER_IP
```

### 3. Deploy Application

```bash
# Clone repository
cd /opt/flowmind
git clone https://github.com/barbudangabriel-gif/Flowmind.git .

# Configure environment
cp deploy/.env.production.example deploy/.env.production
nano deploy/.env.production  # Fill in your values:
  # TS_CLIENT_ID=...
  # TS_CLIENT_SECRET=...
  # TS_REDIRECT_URI=https://your-domain.com/api/oauth/tradestation/callback
  # UW_API_TOKEN=...
  # DOMAIN=your-domain.com

# Update Caddyfile with your domain
nano deploy/Caddyfile  # Replace "your-domain.com" with actual domain

# Make deploy script executable
chmod +x deploy/production-deploy.sh
chmod +x deploy/quick-update.sh

# Run deployment
./deploy/production-deploy.sh
```

### 4. DNS Configuration

Point your domain to the server:

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

Wait 5-15 minutes for DNS propagation.

---

## 🔍 Verification

### Check Services
```bash
# Backend health
curl http://localhost:8000/health

# Frontend (after DNS propagates)
curl https://your-domain.com

# Docker containers
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml ps

# Logs
docker-compose -f deploy/docker-compose.production.yml logs -f backend
docker-compose -f deploy/docker-compose.production.yml logs -f redis
sudo journalctl -u caddy -f
```

---

## 🔄 Updates & Maintenance

### Quick Update (after code changes)
```bash
cd /opt/flowmind
./deploy/quick-update.sh
```

### Full Rebuild
```bash
cd /opt/flowmind
./deploy/production-deploy.sh
```

### View Logs
```bash
cd /opt/flowmind

# Backend logs
docker-compose -f deploy/docker-compose.production.yml logs -f backend

# Redis logs
docker-compose -f deploy/docker-compose.production.yml logs -f redis

# Caddy logs
sudo journalctl -u caddy -f

# Access logs
sudo tail -f /var/log/caddy/flowmind-access.log
```

### Backup Redis Data
```bash
# Redis data is in Docker volume
docker exec flowmind-redis redis-cli SAVE

# Copy backup
docker cp flowmind-redis:/data/dump.rdb /opt/flowmind/backups/redis-$(date +%Y%m%d).rdb

# Mindfolios backup (automatic to disk)
tar -czf /opt/flowmind/backups/mindfolios-$(date +%Y%m%d).tar.gz /opt/flowmind/data/mindfolios
```

---

## 🔐 Security Checklist

- [x] Firewall enabled (UFW)
- [x] SSH key authentication
- [x] Auto HTTPS (Let's Encrypt via Caddy)
- [x] Docker containers run as non-root
- [x] Redis only accessible from localhost
- [x] Backend only accessible from localhost (via Caddy)
- [ ] **TODO:** Set up SSH key-only auth (disable password)
  ```bash
  nano /etc/ssh/sshd_config
  # Set: PasswordAuthentication no
  systemctl restart sshd
  ```
- [ ] **TODO:** Enable automatic security updates
  ```bash
  apt-get install -y unattended-upgrades
  dpkg-reconfigure -plow unattended-upgrades
  ```

---

## 📊 Monitoring (Optional)

### Simple Health Check Script
```bash
# Create monitoring script
cat > /opt/flowmind/monitor.sh << 'EOF'
#!/bin/bash
if ! curl -sf http://localhost:8000/health > /dev/null; then
    echo "Backend down! Restarting..."
    cd /opt/flowmind
    docker-compose -f deploy/docker-compose.production.yml restart backend
fi
EOF

chmod +x /opt/flowmind/monitor.sh

# Add to cron (every 5 minutes)
crontab -e
# Add line:
# */5 * * * * /opt/flowmind/monitor.sh >> /opt/flowmind/logs/monitor.log 2>&1
```

---

## 🆘 Troubleshooting

### Backend won't start
```bash
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml logs backend

# Check environment variables
docker-compose -f deploy/docker-compose.production.yml exec backend env | grep TS_
```

### Caddy SSL issues
```bash
# Check Caddy status
sudo systemctl status caddy

# Validate Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile

# Check Caddy logs
sudo journalctl -u caddy -n 100
```

### Redis connection issues
```bash
# Check Redis is running
docker exec flowmind-redis redis-cli ping
# Should return: PONG

# Check Redis logs
docker-compose -f deploy/docker-compose.production.yml logs redis
```

### Port already in use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Or port 80/443
sudo lsof -i :80
sudo lsof -i :443
```

---

## 💡 Performance Tuning

### Increase Uvicorn workers (if needed)
```bash
# Edit .env.production
nano /opt/flowmind/deploy/.env.production
# Set: UVICORN_WORKERS=8 (for CPX31 with 4 vCPU)

# Restart
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml restart backend
```

### Redis persistence tuning
```bash
# Edit docker-compose
nano /opt/flowmind/deploy/docker-compose.production.yml

# Redis command options:
# --appendonly yes --appendfsync everysec  # Current (balanced)
# --appendfsync always                      # Safer, slower
# --appendfsync no                          # Faster, less safe
```

---

## 📞 Support

- **Repository:** https://github.com/barbudangabriel-gif/Flowmind
- **Issues:** https://github.com/barbudangabriel-gif/Flowmind/issues
- **Documentation:** `.github/copilot-instructions.md`

---

## ✅ Post-Deployment Checklist

- [ ] Server created on Hetzner
- [ ] DNS configured (A records)
- [ ] SSL certificate issued (automatic via Caddy)
- [ ] Backend health check passes
- [ ] Frontend loads on domain
- [ ] TradeStation OAuth works (test login flow)
- [ ] Unusual Whales API connected (test flow data)
- [ ] Redis persistence confirmed
- [ ] Backups scheduled
- [ ] Monitoring enabled
- [ ] Security hardening complete

---

**Estimated Setup Time:** 30-45 minutes (excluding DNS propagation)

**Monthly Cost:** ~€7-13 (depending on server size)
