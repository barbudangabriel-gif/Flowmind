# 🆘 FlowMind Production Troubleshooting

Quick reference for common issues on Hetzner deployment.

---

## 🔴 Backend Not Starting

### Check logs
```bash
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml logs backend
```

### Common issues:
1. **Missing environment variables**
   ```bash
   # Verify .env.production exists and has all values
   cat deploy/.env.production | grep TS_CLIENT_ID
   ```

2. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

3. **Redis not accessible**
   ```bash
   docker exec flowmind-redis redis-cli ping
   # Should return: PONG
   ```

---

## 🔴 SSL Certificate Not Generating

### Check Caddy status
```bash
sudo systemctl status caddy
sudo journalctl -u caddy -n 50
```

### Common issues:
1. **DNS not propagated**
   ```bash
   # Check DNS from external server
   nslookup your-domain.com 8.8.8.8
   ```

2. **Port 80/443 blocked**
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Caddyfile syntax error**
   ```bash
   sudo caddy validate --config /etc/caddy/Caddyfile
   ```

---

## 🔴 Frontend Shows White Screen

### Check build
```bash
ls -la /opt/flowmind/frontend/build
# Should contain index.html, static/, etc.
```

### Rebuild frontend
```bash
cd /opt/flowmind/frontend
rm -rf build node_modules
npm install
REACT_APP_BACKEND_URL="" npm run build
sudo systemctl reload caddy
```

---

## 🔴 TradeStation OAuth Not Working

### Check redirect URI
```bash
# Verify it matches TradeStation Developer Portal
cat /opt/flowmind/deploy/.env.production | grep TS_REDIRECT_URI
# Should be: https://your-domain.com/api/oauth/tradestation/callback
```

### Test OAuth flow
```bash
# Check backend logs during OAuth
docker-compose -f deploy/docker-compose.production.yml logs -f backend
```

---

## 🔴 Redis Data Lost After Restart

### Check persistence
```bash
# Verify AOF is enabled
docker exec flowmind-redis redis-cli CONFIG GET appendonly
# Should return: 1. appendonly 2. yes

# Check AOF file
docker exec flowmind-redis ls -lh /data/
```

### Restore from backup
```bash
# Stop Redis
docker-compose -f deploy/docker-compose.production.yml stop redis

# Copy backup
LATEST_BACKUP=$(ls -t /opt/flowmind/backups/redis-*.rdb | head -1)
docker cp $LATEST_BACKUP flowmind-redis:/data/dump.rdb

# Start Redis
docker-compose -f deploy/docker-compose.production.yml start redis
```

---

## 🔴 High Memory Usage

### Check container stats
```bash
docker stats flowmind-backend flowmind-redis
```

### Reduce Uvicorn workers
```bash
nano /opt/flowmind/deploy/.env.production
# Change: UVICORN_WORKERS=2 (from 4)

docker-compose -f deploy/docker-compose.production.yml restart backend
```

### Clear Redis cache
```bash
docker exec flowmind-redis redis-cli FLUSHALL
# WARNING: This will delete all cached data!
```

---

## 🔴 Slow Response Times

### Check backend health
```bash
curl -w "@-" -o /dev/null -s http://localhost:8000/health <<'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
   time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
         time_total:  %{time_total}\n
EOF
```

### Enable debug logging
```bash
# Edit docker-compose
nano /opt/flowmind/deploy/docker-compose.production.yml
# Add under backend environment:
#   LOG_LEVEL: DEBUG

docker-compose -f deploy/docker-compose.production.yml restart backend
```

---

## 🔴 Disk Space Full

### Check usage
```bash
df -h
docker system df
```

### Clean up
```bash
# Remove old Docker images
docker image prune -a -f

# Remove old logs
find /opt/flowmind/logs -type f -mtime +7 -delete

# Remove old backups
find /opt/flowmind/backups -type f -mtime +14 -delete
```

---

## 🟢 Monitoring Commands

### Quick health check
```bash
# All services
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml ps

# Backend health
curl http://localhost:8000/health

# Redis
docker exec flowmind-redis redis-cli ping
```

### View logs (real-time)
```bash
# Backend
docker-compose -f deploy/docker-compose.production.yml logs -f backend

# Redis
docker-compose -f deploy/docker-compose.production.yml logs -f redis

# Caddy
sudo journalctl -u caddy -f
```

### Check resource usage
```bash
# CPU & Memory
htop

# Docker containers
docker stats

# Disk
df -h
```

---

## 🔧 Emergency Recovery

### Complete restart
```bash
cd /opt/flowmind
docker-compose -f deploy/docker-compose.production.yml down
docker-compose -f deploy/docker-compose.production.yml up -d
```

### Restore from backup
```bash
# Stop services
docker-compose -f deploy/docker-compose.production.yml down

# Restore Redis
LATEST_REDIS=$(ls -t /opt/flowmind/backups/redis-*.rdb | head -1)
docker volume rm flowmind_redis-data
docker volume create flowmind_redis-data
docker run --rm -v flowmind_redis-data:/data -v /opt/flowmind/backups:/backup alpine sh -c "cp /backup/$(basename $LATEST_REDIS) /data/dump.rdb"

# Restore Mindfolios
LATEST_MINDFOLIOS=$(ls -t /opt/flowmind/backups/mindfolios-*.tar.gz | head -1)
tar -xzf $LATEST_MINDFOLIOS -C /

# Start services
docker-compose -f deploy/docker-compose.production.yml up -d
```

---

## 📞 Getting Help

1. **Check logs first** - Most issues show up in logs
2. **Search GitHub Issues** - Someone may have had the same problem
3. **Check documentation** - `.github/copilot-instructions.md`
4. **Create issue** - https://github.com/barbudangabriel-gif/Flowmind/issues

---

## 🔍 Diagnostic Script

Save this as `/opt/flowmind/diagnose.sh`:

```bash
#!/bin/bash
echo "🔍 FlowMind Diagnostic Report"
echo "=============================="
echo ""
echo "📅 Date: $(date)"
echo "🖥️  Server: $(hostname)"
echo ""
echo "🐳 Docker Containers:"
docker-compose -f /opt/flowmind/deploy/docker-compose.production.yml ps
echo ""
echo "💾 Disk Space:"
df -h | grep -E 'Filesystem|/dev/sda'
echo ""
echo "🧠 Memory:"
free -h
echo ""
echo "🔥 CPU Load:"
uptime
echo ""
echo "✅ Backend Health:"
curl -s http://localhost:8000/health || echo "❌ Backend not responding"
echo ""
echo "✅ Redis:"
docker exec flowmind-redis redis-cli ping 2>/dev/null || echo "❌ Redis not responding"
echo ""
echo "🌐 Caddy Status:"
sudo systemctl is-active caddy
echo ""
```

Run with: `bash /opt/flowmind/diagnose.sh`
