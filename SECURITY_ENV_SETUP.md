# FlowMind Security - Environment Variables Setup

**Date:** November 5, 2025  
**Purpose:** Set up authentication credentials securely (NO passwords in Git!)

---

## ⚠️ GitGuardian Alert - Nov 5, 2025

**Issue:** Default password was committed to Git history (commits before 86e1836).

**Status:** Code fixed (commit 86e1836) - all hardcoded passwords removed.

**Action Required:** Set new credentials via environment variables on production server.

---

## Required Environment Variables

Authentication now requires these environment variables:

```bash
ADMIN_EMAIL=gabriel@flowmind.ai          # User email
ADMIN_PASSWORD=<your-secure-password>    # Plain text password (will be validated)
JWT_SECRET_KEY=<random-32-char-string>   # Token signing key
```

**⚠️ CRITICAL:**
- NEVER commit `.env` files to Git
- NEVER run SSH commands with passwords in them (they appear in shell history)
- Generate strong passwords (24+ characters, random)

---

## Production Server Setup (SECURE METHOD)

### Step 1: SSH to Server

```bash
ssh root@flowmindanalytics.ai
cd /opt/flowmind
```

### Step 2: Create .env File Manually

**DO NOT** copy-paste commands with passwords! Instead:

```bash
# Open editor
nano backend/.env
```

**Type manually** (do NOT paste into terminal):

```env
ADMIN_EMAIL=gabriel@flowmind.ai
ADMIN_PASSWORD=<generate-secure-password-here>
JWT_SECRET_KEY=<generate-random-key-here>
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 3: Generate Secure Values

**For JWT_SECRET_KEY:**
```bash
openssl rand -base64 32
```
Copy output, paste into `.env` file (use nano/vim, not terminal commands).

**For ADMIN_PASSWORD:**
- Use password manager to generate 24+ character password
- Type manually into `.env` file
- Save password in password manager (NOT in terminal history)

### Step 4: Verify File Permissions

```bash
chmod 600 backend/.env
ls -la backend/.env
# Should show: -rw------- (only root can read)
```

### Step 5: Restart Backend

```bash
cd /opt/flowmind
docker compose restart backend
docker compose logs backend --tail 50
# Look for "Application startup complete" (no errors)
```

### Step 6: Test Login

**From your local machine** (NOT on server):

```bash
curl -X POST https://flowmindanalytics.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gabriel@flowmind.ai","password":"YOUR_NEW_PASSWORD"}'
```

**Expected response:**
```json
{
  "token": "eyJhbGci...",
  "user": {
    "email": "gabriel@flowmind.ai",
    "name": "Gabriel",
    "role": "admin"
  }
}
```

**If 401 error:** Password incorrect, check `.env` file for typos.

---

## Security Best Practices

### ✅ DO:
- Generate passwords with password manager (24+ chars)
- Store passwords in secure password manager
- Use `nano` or `vim` to edit `.env` files
- Set file permissions: `chmod 600 .env`
- Test login after setup
- Rotate JWT_SECRET_KEY every 90 days

### ❌ DON'T:
- Commit `.env` files to Git
- Run commands with passwords in them: `echo "password=123" > .env` ❌
- Share passwords via chat/email
- Use weak passwords (<16 chars)
- Store passwords in shell history
- Copy-paste passwords into terminal commands

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
docker compose logs backend --tail 100
```

**Common issues:**
- `.env` file missing → Backend uses defaults ("CHANGE_ME_IN_PRODUCTION")
- `.env` file syntax error → Check for quotes, newlines
- Permission denied → Run `chmod 600 backend/.env`

### Login Returns 401

**Possible causes:**
1. Wrong password in curl command
2. `.env` file not loaded by backend
3. Backend not restarted after `.env` change

**Debug:**
```bash
# Verify .env file exists
ls -la /opt/flowmind/backend/.env

# Check backend loaded env vars (DO NOT print password!)
docker compose exec backend env | grep ADMIN_EMAIL
# Should show: ADMIN_EMAIL=gabriel@flowmind.ai

# Restart backend
docker compose restart backend
```

### Login Returns 500

**Cause:** `ADMIN_PASSWORD` not set in `.env`

**Fix:**
1. Edit `/opt/flowmind/backend/.env`
2. Add: `ADMIN_PASSWORD=<your-password>`
3. Restart: `docker compose restart backend`

---

## Password Reset Procedure

If you forget the password:

1. SSH to server
2. Edit `.env`: `nano /opt/flowmind/backend/.env`
3. Change `ADMIN_PASSWORD=<new-password>`
4. Restart: `docker compose restart backend`
5. Test login with new password

**Note:** No database involved - password stored only in `.env` file.

---

## .gitignore Verification

Ensure these patterns are in `.gitignore`:

```gitignore
# Environment variables (NEVER commit)
.env
.env.*
*.env
backend/.env
frontend/.env
**/.env

# Secrets
secrets/
*.key
*.pem
```

**Verify:**
```bash
git status
# .env files should NOT appear in "Changes to be committed"
```

---

## Audit & Compliance

**GitGuardian Scan:** Detected exposed password (Nov 5, 2025)

**Remediation:**
- ✅ Code fixed (commit 86e1836)
- ✅ All hardcoded passwords removed
- ✅ Environment variables enforced
- ⚠️ Production server needs `.env` update
- ❌ Git history still contains exposed password (cannot remove without force push)

**Risk Assessment:**
- **Previous password:** Exposed in public Git history → MUST change
- **New password:** Only in `.env` file (gitignored) → Safe if properly managed
- **JWT tokens:** Signed with new secret key → Old tokens invalid after key change

---

## Additional Security Measures (Future)

### Priority 1: Rate Limiting
```python
# backend/routers/auth.py
from slowapi import Limiter

limiter = Limiter(key_func=lambda: "global")

@router.post("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: LoginRequest):
    ...
```

### Priority 2: Password Strength Validation
```python
import re

def validate_password(password: str) -> bool:
    if len(password) < 16:
        return False
    if not re.search(r'[A-Z]', password):  # Uppercase
        return False
    if not re.search(r'[a-z]', password):  # Lowercase
        return False
    if not re.search(r'[0-9]', password):  # Digit
        return False
    if not re.search(r'[!@#$%^&*]', password):  # Special char
        return False
    return True
```

### Priority 3: Two-Factor Authentication (2FA)
- Use PyOTP for TOTP generation
- Store secret in user profile
- Require 6-digit code after password

---

## Contact

**Admin:** Gabriel (gabriel@flowmind.ai)  
**Production URL:** https://flowmindanalytics.ai  
**Server:** Hetzner VPS (91.107.206.64)

**For password reset requests:** SSH to server and manually edit `.env` file.

---

**Remember:** Security is only as strong as your weakest password. Use a password manager!
