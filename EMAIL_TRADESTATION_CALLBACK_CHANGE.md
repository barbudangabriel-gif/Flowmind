# TradeStation OAuth Callback URL Change Request

**Date:** November 6, 2025  
**Application:** FlowMind Analytics  
**Current Status:** Development (Codespaces) → Production Migration

---

## 📧 Email Draft for TradeStation Support

**To:** apisupport@tradestation.com  
**Subject:** OAuth Callback URL Addition Request - FlowMind Analytics - Add Production URL (Client ID: XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj)

---

Dear TradeStation API Support Team,

I am writing to request **adding a second OAuth callback URL** for my application **FlowMind Analytics**. I need both my existing development URL and a new production URL to remain active simultaneously.

### Application Details:
- **Client ID:** `XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj`
- **Application Name:** FlowMind Analytics
- **Current Environment:** LIVE mode
- **Developer Email:** barbudangabriel.gif@gmail.com (or your registered email)

### Current Callback URL (Development Only):
```
https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback
```

### Request: ADD Second Callback URL (Production):
```
https://flowmindanalytics.ai/api/oauth/tradestation/callback
```

### Important: I Need BOTH URLs Active Simultaneously

I am requesting to **add** the production URL while **keeping** the existing development URL active. I need both callback URLs registered and functional:

1. **Production (NEW):** `https://flowmindanalytics.ai/api/oauth/tradestation/callback`
   - Live production server
   - Public-facing application
   - SSL via Let's Encrypt
   
2. **Development (KEEP ACTIVE):** `https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback`
   - GitHub Codespaces environment
   - Active development and testing
   - Must remain functional

### Reason for Dual URLs:
I am running the application in two environments:
- **Production:** Deployed at flowmindanalytics.ai (Ubuntu 24.04.3 LTS, Caddy reverse proxy, Let's Encrypt SSL)
- **Development:** GitHub Codespaces for active feature development and testing

Having both callback URLs active allows me to:
- Develop and test new features in Codespaces without disrupting production
- Ensure smooth deployments and rollback capabilities
- Maintain separate OAuth tokens for dev/prod environments

### Technical Details:
- Both URLs use the same endpoint path: `/api/oauth/tradestation/callback`
- Both environments run the same codebase (different branches/configurations)
- Backend dynamically selects the correct callback URL based on `TS_REDIRECT_URI` environment variable
- No conflicts between environments (separate token storage)

### Timeline:
I would appreciate this change as soon as possible. Please let me know if you need any additional information or documentation.

Thank you for your assistance!

Best regards,  
Gabriel Barbudan  
FlowMind Analytics  
https://flowmindanalytics.ai

---

## 🔧 Post-Approval Actions (After TradeStation Confirms)

### 1. Update Backend Environment Variables

**On Production Server (`/opt/flowmind/backend/.env`):**
```bash
# SSH to production server
ssh root@flowmindanalytics.ai

# Edit .env file
nano /opt/flowmind/backend/.env

# Update this line:
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback

# Restart backend
cd /opt/flowmind
docker-compose restart backend
```

### 2. Update Development Environment

**In Codespaces (`/workspaces/Flowmind/backend/.env`):**
```bash
# Keep development URL for local testing
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback

# OR if TradeStation approves dual URLs, you can switch between them
```

### 3. Test OAuth Flow

**Production Test:**
```bash
# Visit production login URL
https://flowmindanalytics.ai/api/ts/login

# Should redirect to TradeStation with correct callback
# After authentication, should return to:
# https://flowmindanalytics.ai/api/oauth/tradestation/callback?code=...
```

**Verify Backend Logs:**
```bash
# Check if OAuth token is received
docker logs flowmind-backend-1 --tail 50 | grep -i "oauth\|token\|tradestation"
```

### 4. Frontend Configuration Check

**Frontend OAuth Config Endpoint:**
```bash
# The frontend fetches OAuth settings dynamically
curl https://flowmindanalytics.ai/api/oauth/tradestation/config | jq

# Should return:
{
  "auth_url": "https://signin.tradestation.com/authorize",
  "client_id": "XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj",
  "redirect_uri": "https://flowmindanalytics.ai/api/oauth/tradestation/callback",
  "scope": "openid offline_access MarketData ReadAccount Trade OptionSpreads Matrix"
}
```

---

## 📋 Verification Checklist

After TradeStation approves the callback URL change:

- [ ] Email confirmation received from TradeStation
- [ ] Updated `TS_REDIRECT_URI` in production `.env`
- [ ] Restarted backend with `docker-compose restart backend`
- [ ] Tested OAuth login at `https://flowmindanalytics.ai/api/ts/login`
- [ ] Verified redirect to TradeStation with correct callback
- [ ] Confirmed successful token exchange
- [ ] Tested API calls with new token (accounts, positions, balances)
- [ ] Verified frontend OAuth config endpoint returns production URL
- [ ] Updated documentation with production callback URL

---

## 🚨 Important Notes

1. **TradeStation Portal:** Check your TradeStation developer portal to see if you can update the callback URL yourself at:
   - https://developer.tradestation.com/webapi

2. **Response Time:** TradeStation API support typically responds within 1-2 business days.

3. **Backup Plan:** Keep the Codespaces URL active in `.env` for development/testing until production is fully stable.

4. **Multiple Environments:** Consider requesting multiple callback URLs:
   - Production: `https://flowmindanalytics.ai/api/oauth/tradestation/callback`
   - Development: Codespaces URL
   - Staging: If you add a staging environment later

5. **Documentation:** After change is complete, update `.github/copilot-instructions.md` with the new production callback URL.

---

## 🔗 Related Files to Update After Approval

1. `/opt/flowmind/backend/.env` (production)
2. `/workspaces/Flowmind/backend/.env` (development)
3. `.github/copilot-instructions.md` (documentation)
4. `DEPLOYMENT_GUIDE.md` (if exists)
5. Any deployment scripts that reference the callback URL

---

## 📞 TradeStation Contact Information

- **Email:** apisupport@tradestation.com
- **Developer Portal:** https://developer.tradestation.com
- **Documentation:** https://api.tradestation.com/docs/fundamentals/authentication/auth-overview
- **Support Hours:** Monday-Friday, 9 AM - 5 PM EST

---

**Status:** ✅ EMAIL SENT - November 6, 2025  
**Sent To:** apisupport@tradestation.com  
**Expected Response:** 1-2 business days  
**Next Step:** Wait for TradeStation confirmation, then update production .env
