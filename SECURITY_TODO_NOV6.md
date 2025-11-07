# Security Action Items - November 6, 2025

**Issue:** UW_API_TOKEN exposed in git (had to rotate)  
**Priority:** 🔴 HIGH - Need to secure production secrets

---

## ✅ Already Done

- [x] `.gitignore` configured to block `.env` files
- [x] Security commit `9ad2ff0` removed exposed secrets
- [x] Created `SECRETS_MANAGEMENT_SETUP.md` documentation
- [x] Created `setup_secrets_vault.sh` automated setup script

---

## 🔴 TODO: Production Server Setup

### Step 1: Get New API Tokens

**Unusual Whales (REQUIRED - old token exposed):**
1. Visit: https://unusualwhales.com/account
2. Go to API Keys section
3. Click "Regenerate Token"
4. Save new token securely (you'll need it in Step 2)

**TradeStation (Check if needed):**
- Verify if `TS_CLIENT_SECRET` was exposed in git
- If yes: https://developer.tradestation.com → Regenerate
- If no: Keep existing secret

### Step 2: Run Setup Script on Production

```bash
# Copy script to production server
scp setup_secrets_vault.sh root@flowmindanalytics.ai:/tmp/

# SSH to server
ssh root@flowmindanalytics.ai

# Run setup script
bash /tmp/setup_secrets_vault.sh

# Follow the on-screen instructions
```

### Step 3: Create Secrets File Manually

```bash
# On production server
nano /opt/flowmind/secrets/api_keys.env

# Add (replace with REAL values):
UW_API_TOKEN=your_NEW_rotated_token_from_step1
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback
TS_MODE=LIVE
TRADESTATION_MODE=LIVE

# Secure the file
chmod 600 /opt/flowmind/secrets/api_keys.env
```

### Step 4: Update docker-compose.yml

```bash
cd /opt/flowmind
nano docker-compose.yml

# Find 'backend:' service and add:
services:
  backend:
    build: ./backend
    env_file:
      - /opt/flowmind/secrets/api_keys.env  # <-- ADD THIS LINE
    ports:
      - "8000:8000"
    ...
```

### Step 5: Restart and Verify

```bash
# Restart backend
docker-compose restart backend

# Check logs
docker logs flowmind-backend-1 --tail 30

# Verify health
curl http://localhost:8000/health | jq

# Test UW API (should work with new token)
curl "http://localhost:8000/api/flow/summary?limit=1" -H "X-User-ID: default"
```

---

## 📋 Quick Checklist

**On Production Server (flowmindanalytics.ai):**
- [ ] Get NEW UW_API_TOKEN from Unusual Whales dashboard
- [ ] Run `setup_secrets_vault.sh` script
- [ ] Create `/opt/flowmind/secrets/api_keys.env` with real tokens
- [ ] Set permissions: `chmod 600 api_keys.env`
- [ ] Update `docker-compose.yml` to load secrets
- [ ] Restart backend: `docker-compose restart backend`
- [ ] Verify backend starts without errors
- [ ] Test API calls work with new tokens
- [ ] Delete old `.env` if it exists: `rm /opt/flowmind/backend/.env`

**In Git Repository:**
- [ ] Verify `.gitignore` blocks `.env` files (already done ✅)
- [ ] Verify no secrets in `backend/.env` (should be git-ignored)
- [ ] Update documentation with vault setup instructions
- [ ] Commit security docs (this file + setup script)

---

## 🚨 CRITICAL: Token Rotation Required

**Old UW_API_TOKEN (EXPOSED in git):**
```
5809ee6a-bcb6-48ce-a16d-9f3bd634fd50
```
❌ This token MUST be rotated - it was committed to git history!

**Action:** Get new token from Unusual Whales dashboard ASAP

---

## 📁 Files Created

1. `SECRETS_MANAGEMENT_SETUP.md` - Complete documentation
2. `setup_secrets_vault.sh` - Automated setup script
3. `SECURITY_TODO_NOV6.md` - This checklist (you are here)

---

## ⏱️ Time Estimate

- Get new UW token: 2 minutes
- Run setup script: 1 minute
- Create secrets file: 3 minutes
- Update docker-compose: 2 minutes
- Test: 2 minutes
- **Total: ~10 minutes**

---

## 🔗 Quick Links

- Unusual Whales Dashboard: https://unusualwhales.com/account
- TradeStation Dev Portal: https://developer.tradestation.com
- Setup Script: `setup_secrets_vault.sh`
- Full Docs: `SECRETS_MANAGEMENT_SETUP.md`

---

**Status:** ⏳ PENDING - Waiting for you to rotate UW token and run setup  
**Next Action:** Get new UW_API_TOKEN from dashboard, then run setup script on server
