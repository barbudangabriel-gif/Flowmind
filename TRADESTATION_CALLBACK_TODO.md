# TradeStation Callback URL - Action Items

**Email Sent:** November 6, 2025  
**Status:** ⏳ Waiting for TradeStation approval

---

## ⏳ Current Status

✅ Email sent to apisupport@tradestation.com requesting:
- **ADD** production URL: `https://flowmindanalytics.ai/api/oauth/tradestation/callback`
- **KEEP** development URL: `https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback`

Expected response: 1-2 business days

---

## 📝 When TradeStation Approves - DO THIS:

### Step 1: Update Production Server

```bash
# SSH to server
ssh root@flowmindanalytics.ai

# Edit backend .env
nano /opt/flowmind/backend/.env

# Change line 18 to:
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback

# Save and restart
cd /opt/flowmind
docker-compose restart backend

# Verify backend is running
docker ps
curl http://localhost:8000/health
```

### Step 2: Test Production OAuth Flow

```bash
# Visit in browser:
https://flowmindanalytics.ai/api/ts/login

# Should redirect to TradeStation
# After login, should return to:
https://flowmindanalytics.ai/api/oauth/tradestation/callback?code=...

# Check backend logs for token
docker logs flowmind-backend-1 --tail 50 | grep -i token
```

### Step 3: Verify Frontend Config

```bash
curl https://flowmindanalytics.ai/api/oauth/tradestation/config | jq

# Should show production callback URL
```

### Step 4: Test API Calls

```bash
# After OAuth login, test these endpoints:
curl https://flowmindanalytics.ai/api/tradestation/accounts -H "X-User-ID: default"
curl https://flowmindanalytics.ai/api/tradestation/accounts/ACCOUNT_ID/balances -H "X-User-ID: default"
```

---

## 📌 Important Notes

- **Development URL stays unchanged** - Keep using Codespaces URL in dev
- **No changes needed in Codespaces** - backend/.env stays as is
- **Two separate OAuth tokens** - One for prod, one for dev
- **Test in production first** - Before announcing to users

---

## ✅ Post-Approval Checklist

- [ ] TradeStation confirmation email received
- [ ] Production .env updated with new callback URL
- [ ] Backend restarted on production server
- [ ] Production OAuth flow tested successfully
- [ ] Token received and stored in Redis
- [ ] API calls working with new token
- [ ] Frontend displays correct OAuth config
- [ ] Documentation updated (copilot-instructions.md)
- [ ] PROJECT_TASKS.md updated with completion

---

## 🔗 Related Files

- Production .env: `/opt/flowmind/backend/.env`
- Development .env: `/workspaces/Flowmind/backend/.env` (NO CHANGES)
- Email draft: `EMAIL_TRADESTATION_CALLBACK_CHANGE.md`
- Instructions: `.github/copilot-instructions.md`

---

**Quick Command Reference:**

```bash
# Check production backend status
ssh root@flowmindanalytics.ai 'docker ps && docker logs flowmind-backend-1 --tail 20'

# View production .env
ssh root@flowmindanalytics.ai 'cat /opt/flowmind/backend/.env | grep TS_REDIRECT_URI'

# Restart production backend
ssh root@flowmindanalytics.ai 'cd /opt/flowmind && docker-compose restart backend'
```
