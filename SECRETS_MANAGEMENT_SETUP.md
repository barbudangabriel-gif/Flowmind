# Secrets Management - Production Vault Setup

**Date:** November 6, 2025  
**Issue:** API tokens exposed in git → had to rotate UW_API_TOKEN  
**Solution:** Implement proper secrets management for production

---

## 🚨 Problem Summary

**What Happened:**
1. `UW_API_TOKEN` was committed to git in `backend/.env`
2. Token was exposed publicly → security risk
3. Had to rotate/change the token
4. Need proper secrets management to prevent this in future

**Critical Lesson:** NEVER commit API tokens to git, even in private repos!

---

## ✅ Solution: Multi-Layer Secrets Management

### Layer 1: Git Protection (.gitignore)

**File:** `.gitignore` (should already contain)
```gitignore
# Environment variables with secrets
.env
.env.local
.env.production
.env.development
backend/.env
frontend/.env.local

# Backup/config files that might contain secrets
*.env.backup
secrets.json
vault.json
```

**Verification:**
```bash
# Check .gitignore includes .env files
cat .gitignore | grep "\.env"

# Verify .env is not tracked
git status --ignored | grep "\.env"
```

---

### Layer 2: Production Secrets Vault

**Option A: Environment Variables Only (Simplest)**

Store secrets directly on server as environment variables, NOT in files:

```bash
# SSH to production
ssh root@flowmindanalytics.ai

# Create secrets directory (NOT in git repo)
mkdir -p /opt/flowmind/secrets
chmod 700 /opt/flowmind/secrets

# Create encrypted secrets file
nano /opt/flowmind/secrets/api_keys.env

# Add secrets (replace with your NEW tokens):
UW_API_TOKEN=your_new_token_here_after_rotation
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=your_new_ts_secret_if_rotated

# Set strict permissions
chmod 600 /opt/flowmind/secrets/api_keys.env
chown root:root /opt/flowmind/secrets/api_keys.env
```

**Load secrets in Docker:**

Update `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env.template  # Non-sensitive config only
      - /opt/flowmind/secrets/api_keys.env  # Secrets from vault
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
```

---

**Option B: HashiCorp Vault (Enterprise Grade)**

For production-grade secrets management:

```bash
# Install Vault
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
apt update && apt install vault

# Start Vault in dev mode (for testing)
vault server -dev

# Store secrets
vault kv put secret/flowmind/api \
  uw_token="your_new_uw_token" \
  ts_client_id="XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj" \
  ts_client_secret="your_ts_secret"

# Retrieve in application
vault kv get -field=uw_token secret/flowmind/api
```

---

**Option C: Docker Secrets (Docker Swarm)**

```bash
# Create secrets
echo "your_new_uw_token" | docker secret create uw_api_token -
echo "your_ts_secret" | docker secret create ts_client_secret -

# Reference in docker-compose.yml
version: '3.8'
services:
  backend:
    secrets:
      - uw_api_token
      - ts_client_secret
    environment:
      - UW_API_TOKEN_FILE=/run/secrets/uw_api_token
      
secrets:
  uw_api_token:
    external: true
  ts_client_secret:
    external: true
```

---

### Layer 3: Development Environment Protection

**For Codespaces/Local Development:**

```bash
# Create .env.local (never commit!)
cat > backend/.env.local << 'EOF'
# Development secrets - DO NOT COMMIT
UW_API_TOKEN=dev_token_here
TS_CLIENT_SECRET=dev_secret_here
EOF

# Load in application
python-dotenv loads .env.local automatically (higher priority than .env)
```

**Backend code to load secrets:**

```python
# backend/config.py or server.py
import os
from pathlib import Path

def load_secrets():
    """Load secrets from vault or env files"""
    # Priority: Environment variables > .env.local > .env > vault file
    
    # Check for secrets vault first
    vault_path = Path("/opt/flowmind/secrets/api_keys.env")
    if vault_path.exists():
        from dotenv import load_dotenv
        load_dotenv(vault_path)
        print("✅ Loaded secrets from vault")
    
    # Fallback to environment variables
    uw_token = os.getenv("UW_API_TOKEN")
    if not uw_token:
        print("⚠️  UW_API_TOKEN not found in environment")
    
    return {
        "uw_token": uw_token,
        "ts_client_id": os.getenv("TS_CLIENT_ID"),
        "ts_client_secret": os.getenv("TS_CLIENT_SECRET"),
    }
```

---

## 🔒 Recommended Setup (Simplest & Secure)

**For FlowMind Production:**

1. **Create secrets vault on server:**
```bash
ssh root@flowmindanalytics.ai

# Create vault directory
mkdir -p /opt/flowmind/secrets
chmod 700 /opt/flowmind/secrets

# Create secrets file
cat > /opt/flowmind/secrets/api_keys.env << 'EOF'
# API Secrets - Production Only
UW_API_TOKEN=your_new_rotated_token_here
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback
EOF

chmod 600 /opt/flowmind/secrets/api_keys.env
```

2. **Update docker-compose.yml:**
```yaml
services:
  backend:
    env_file:
      - ./backend/.env.template  # Non-sensitive config
      - /opt/flowmind/secrets/api_keys.env  # Secrets vault
```

3. **Create .env.template (safe to commit):**
```bash
# backend/.env.template - Safe to commit (no secrets!)
REDIS_HOST=redis
REDIS_PORT=6379
FM_FORCE_FALLBACK=0
LOG_LEVEL=INFO

# API URLs (public, safe to commit)
UW_BASE_URL=https://api.unusualwhales.com
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://signin.tradestation.com/authorize
TS_TOKEN_URL=https://signin.tradestation.com/oauth/token
TS_MODE=LIVE
```

4. **Update .gitignore:**
```gitignore
# CRITICAL: Never commit these files
.env
.env.local
.env.production
backend/.env
backend/.env.local
secrets/
api_keys.env
vault.json
```

---

## 📋 Implementation Checklist

**Immediate Actions (Production Server):**
- [ ] SSH to `root@flowmindanalytics.ai`
- [ ] Create `/opt/flowmind/secrets/` directory
- [ ] Create `api_keys.env` with NEW rotated tokens
- [ ] Set permissions: `chmod 600 api_keys.env`
- [ ] Verify permissions: `ls -la /opt/flowmind/secrets/`
- [ ] Update `docker-compose.yml` to load secrets vault
- [ ] Restart backend: `docker-compose restart backend`
- [ ] Test API calls work with new tokens
- [ ] Delete old .env file: `rm /opt/flowmind/backend/.env` (if it contains secrets)

**Git Repository Cleanup:**
- [ ] Remove `backend/.env` from git history (if committed)
- [ ] Update `.gitignore` to prevent future commits
- [ ] Create `backend/.env.template` (safe template without secrets)
- [ ] Commit .gitignore + .env.template
- [ ] Verify: `git status --ignored` shows .env files ignored

**Development Environment:**
- [ ] Create `backend/.env.local` (not committed) with dev tokens
- [ ] Update `backend/.env.example` with placeholder values
- [ ] Document secrets setup in README.md
- [ ] Test dev environment works with .env.local

---

## 🔐 Token Rotation Process

**When you need to rotate tokens:**

1. **Get new token from provider:**
   - Unusual Whales: Login → Account → API Keys → Regenerate
   - TradeStation: Developer portal → Regenerate Client Secret

2. **Update production vault:**
```bash
ssh root@flowmindanalytics.ai
nano /opt/flowmind/secrets/api_keys.env
# Update token value
docker-compose restart backend
```

3. **Update development environment:**
```bash
# In Codespaces
nano backend/.env.local
# Update token value
docker-compose restart backend
```

4. **Test both environments:**
```bash
# Production
curl https://flowmindanalytics.ai/api/health

# Development  
curl http://localhost:8000/health
```

---

## 📊 Current Status

**Exposed Tokens (NEED ROTATION):**
- ❌ `UW_API_TOKEN=5809ee6a-bcb6-48ce-a16d-9f3bd634fd50` - **EXPOSED IN GIT**
- ⚠️ `TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk` - **CHECK IF EXPOSED**

**Action Required:**
1. ✅ Rotate UW_API_TOKEN (get new token from Unusual Whales dashboard)
2. ✅ Verify TS_CLIENT_SECRET not exposed (check git history)
3. ✅ Implement secrets vault on production server
4. ✅ Remove secrets from git repository
5. ✅ Update documentation

---

## 🚀 Quick Setup Commands

**Copy-paste these commands on production server:**

```bash
# SSH to server
ssh root@flowmindanalytics.ai

# Create secrets vault
mkdir -p /opt/flowmind/secrets
chmod 700 /opt/flowmind/secrets

# Create secrets file (REPLACE TOKENS WITH NEW ONES!)
cat > /opt/flowmind/secrets/api_keys.env << 'EOFVAULT'
# FlowMind API Secrets - Production
UW_API_TOKEN=GET_NEW_TOKEN_FROM_UNUSUALWHALES_DASHBOARD
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback
TS_MODE=LIVE
TRADESTATION_MODE=LIVE
EOFVAULT

# Secure the file
chmod 600 /opt/flowmind/secrets/api_keys.env
chown root:root /opt/flowmind/secrets/api_keys.env

# Verify
ls -la /opt/flowmind/secrets/
cat /opt/flowmind/secrets/api_keys.env

# Update docker-compose.yml to load secrets
cd /opt/flowmind
nano docker-compose.yml
# Add under backend service:
#   env_file:
#     - /opt/flowmind/secrets/api_keys.env

# Restart
docker-compose restart backend

# Test
docker logs flowmind-backend-1 --tail 20
curl http://localhost:8000/health
```

---

## 📞 Where to Get New Tokens

**Unusual Whales:**
- Dashboard: https://unusualwhales.com/account
- API Keys section → Regenerate Token
- Copy new token to `/opt/flowmind/secrets/api_keys.env`

**TradeStation:**
- Developer Portal: https://developer.tradestation.com
- My Apps → FlowMind Analytics → Regenerate Secret
- Update `TS_CLIENT_SECRET` in vault

---

**Next Steps:**
1. Rotate UW_API_TOKEN NOW (it's exposed)
2. Implement secrets vault on production
3. Remove .env from git history (optional but recommended)
4. Test everything still works

**Priority:** HIGH - exposed tokens are a security risk!
