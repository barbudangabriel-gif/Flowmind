# 🚀 FlowMind Deployment Files

Complete deployment solution for Hetzner Cloud VPS.

---

## 📁 Files Overview

| File | Purpose | When to use |
|------|---------|-------------|
| `DEPLOYMENT_GUIDE.md` | **Complete setup guide** | First time deployment |
| `CHECKLIST.md` | **Step-by-step checklist** | During deployment |
| `TROUBLESHOOTING.md` | **Problem solving** | When issues occur |
| `hetzner-setup.sh` | Initial server setup | Run once on new server |
| `production-deploy.sh` | Full deployment | First deploy or major updates |
| `quick-update.sh` | Quick code updates | After git changes |
| `backup.sh` | Backup Redis + mindfolios | Daily cron job |
| `docker-compose.production.yml` | Production stack | Used by deploy scripts |
| `Caddyfile` | Reverse proxy + SSL | Copied to `/etc/caddy/` |
| `.env.production.example` | Environment template | Copy to `.env.production` |

---

## 🚀 Quick Start

### 1. First Time Setup (On Hetzner Server)

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Run setup script
curl -o setup.sh https://raw.githubusercontent.com/barbudangabriel-gif/Flowmind/main/deploy/hetzner-setup.sh
chmod +x setup.sh
./setup.sh

# Clone repository
cd /opt/flowmind
git clone https://github.com/barbudangabriel-gif/Flowmind.git .

# Configure environment
cp deploy/.env.production.example deploy/.env.production
nano deploy/.env.production  # Fill in your values

# Update Caddyfile with your domain
nano deploy/Caddyfile

# Deploy
./deploy/production-deploy.sh
```

### 2. Updates After Code Changes

```bash
cd /opt/flowmind
git pull
./deploy/quick-update.sh
```

### 3. Full Rebuild

```bash
cd /opt/flowmind
./deploy/production-deploy.sh
```

---

## 📚 Documentation Order

**For first deployment:**
1. Read `DEPLOYMENT_GUIDE.md` (comprehensive guide)
2. Follow `CHECKLIST.md` (step-by-step)
3. Keep `TROUBLESHOOTING.md` handy

**For updates:**
1. Use `quick-update.sh` for code changes
2. Use `production-deploy.sh` for major changes

**For problems:**
1. Check `TROUBLESHOOTING.md` first
2. Run diagnostic script
3. Check Docker logs

---

## 🔧 Configuration Files

### `.env.production` (You create this)
```bash
TS_CLIENT_ID=your_id
TS_CLIENT_SECRET=your_secret
TS_REDIRECT_URI=https://your-domain.com/api/oauth/tradestation/callback
UW_API_TOKEN=your_token
DOMAIN=your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### `Caddyfile` (Edit domain)
```
your-domain.com, www.your-domain.com {
    root * /opt/flowmind/frontend/build
    # ... rest is pre-configured
}
```

---

## 🐳 Docker Stack

```
┌─────────────────────────────────────┐
│         Caddy (Ports 80/443)        │
│    - Auto HTTPS (Let's Encrypt)     │
│    - Reverse proxy                  │
└────────────┬────────────────────────┘
             │
             ├─→ Frontend (static files in /build)
             │
             └─→ Backend (port 8000)
                     │
                     └─→ Redis (port 6379)
```

---

## 📊 Server Requirements

### Minimum (CPX21)
- 3 vCPU
- 4GB RAM
- 80GB SSD
- **Cost:** ~€7/month

### Recommended (CPX31)
- 4 vCPU
- 8GB RAM
- 160GB SSD
- **Cost:** ~€13/month

---

## 🔒 Security Features

✅ Auto HTTPS via Let's Encrypt  
✅ Firewall configured (UFW)  
✅ Non-root Docker containers  
✅ Redis only accessible from localhost  
✅ Backend only accessible via Caddy  
✅ Security headers enabled  
✅ CORS properly configured  

---

## 📈 Monitoring

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Redis
docker exec flowmind-redis redis-cli ping

# Frontend
curl -I https://your-domain.com
```

### Logs
```bash
# All logs
docker-compose -f deploy/docker-compose.production.yml logs -f

# Backend only
docker-compose -f deploy/docker-compose.production.yml logs -f backend

# Caddy
sudo journalctl -u caddy -f
```

### Resource Usage
```bash
docker stats flowmind-backend flowmind-redis
```

---

## 🗄️ Backups

### Manual Backup
```bash
/opt/flowmind/deploy/backup.sh
```

### Automated (Daily at 2 AM)
```bash
crontab -e
# Add:
0 2 * * * /opt/flowmind/deploy/backup.sh >> /opt/flowmind/logs/backup.log 2>&1
```

### Restore from Backup
See `TROUBLESHOOTING.md` → Emergency Recovery

---

## 🔄 Update Workflow

### Code Changes Only
```bash
cd /opt/flowmind
git pull
./deploy/quick-update.sh
```

### Dependency Changes
```bash
cd /opt/flowmind
git pull
./deploy/production-deploy.sh  # Full rebuild
```

### Environment Variable Changes
```bash
nano /opt/flowmind/deploy/.env.production
docker-compose -f deploy/docker-compose.production.yml restart backend
```

---

## 🆘 Emergency Contacts

- **Documentation:** `deploy/TROUBLESHOOTING.md`
- **GitHub Issues:** https://github.com/barbudangabriel-gif/Flowmind/issues
- **Project Instructions:** `.github/copilot-instructions.md`

---

## 📞 Support

For deployment issues:
1. Check `TROUBLESHOOTING.md`
2. Run diagnostic script
3. Check Docker logs
4. Create GitHub issue with logs

---

**Last Updated:** November 1, 2025  
**Tested On:** Hetzner CPX21 (Ubuntu 24.04 LTS)  
**Stack:** FastAPI + React 19 + Redis + Caddy
