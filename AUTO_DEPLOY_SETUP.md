# Auto-Deploy Setup Guide

**Purpose:** Automatically pull and deploy latest changes from `origin/main` every 60 seconds.  
**Method:** systemd user timer (more robust than cron)  
**Platform:** WSL2, Linux, macOS (with systemd support)

---

## 📋 Prerequisites

- Git repository cloned to `~/projects/Flowmind`
- `main` branch tracking `origin/main`
- systemd user services enabled (standard on Ubuntu 20.04+)

---

## 🚀 Installation

### Step 1: Setup Main Branch Tracking

```bash
cd ~/projects/Flowmind
git checkout main
git branch --set-upstream-to=origin/main main
git pull
```

**Verify:**
```bash
git status
# Should show: Your branch is up to date with 'origin/main'.
```

### Step 2: Install Systemd Units

```bash
# Create systemd user directory
mkdir -p ~/.config/systemd/user

# Copy service and timer files
cp ~/projects/Flowmind/.ci/flowmind-autopull.service ~/.config/systemd/user/
cp ~/projects/Flowmind/.ci/flowmind-autopull.timer ~/.config/systemd/user/

# Reload systemd to recognize new units
systemctl --user daemon-reload
```

### Step 3: Enable and Start Timer

```bash
# Enable timer (starts on boot)
systemctl --user enable flowmind-autopull.timer

# Start timer immediately
systemctl --user start flowmind-autopull.timer
```

**Verify:**
```bash
systemctl --user status flowmind-autopull.timer
# Should show: active (waiting)
```

---

## 🔍 Verification

### Check Timer Status

```bash
# List all timers (find flowmind-autopull)
systemctl --user list-timers

# Expected output:
# NEXT                        LEFT     LAST                        PASSED  UNIT                        ACTIVATES
# Thu 2025-10-17 22:30:00 UTC 45s left Thu 2025-10-17 22:29:00 UTC 15s ago flowmind-autopull.timer     flowmind-autopull.service
```

### View Logs (Real-time)

```bash
# Follow logs in real-time
journalctl --user -u flowmind-autopull.service -f

# Expected output:
# Oct 17 22:29:15 hostname bash[12345]: [autopull] Starting at 2025-10-17 22:29:15
# Oct 17 22:29:16 hostname bash[12345]: [autopull] No changes detected (6a9284a)
# Oct 17 22:29:16 hostname bash[12345]: [autopull] Done at 2025-10-17 22:29:16
```

### View Last 50 Log Lines

```bash
journalctl --user -u flowmind-autopull.service -n 50
```

### Test Manual Run

```bash
# Trigger service manually (doesn't wait for timer)
systemctl --user start flowmind-autopull.service

# Check if it ran
systemctl --user status flowmind-autopull.service
```

---

## 🛠️ How It Works

### Timer Schedule

- **Interval:** Every 60 seconds after last run completes
- **First Run:** 10 seconds after timer starts
- **Accuracy:** ±5 seconds (optimized for performance)

### Auto-Pull Logic

1. **Fetch:** `git fetch origin main`
2. **Compare:** Check if local commit differs from remote
3. **Update:** If different, `git reset --hard origin/main`
4. **Dependencies:**
   - If `frontend/pnpm-lock.yaml` changed → `pnpm install`
   - If `backend/requirements.txt` changed → `pip install`
5. **Reload:** uvicorn `--reload` auto-restarts backend

### Example Logs (When Changes Detected)

```
[autopull] Starting at 2025-10-17 22:30:00
[autopull] Changes detected on origin/main
[autopull]   Local:  6a9284a
[autopull]   Remote: abc1234
[autopull] Updating to origin/main...
HEAD is now at abc1234 feat: new feature
[autopull] ✅ Code updated
[autopull] Frontend lockfile changed -> reinstalling dependencies
Lockfile is up to date, resolution step is skipped
Already up to date
[autopull] 🚀 Deployment complete
[autopull] Done at 2025-10-17 22:30:05
```

### Example Logs (No Changes)

```
[autopull] Starting at 2025-10-17 22:31:00
[autopull] No changes detected (abc1234)
[autopull] Done at 2025-10-17 22:31:01
```

---

## 🎛️ Configuration

### Change Update Interval

Edit `~/.config/systemd/user/flowmind-autopull.timer`:

```ini
[Timer]
# Every 60 seconds (default)
OnUnitActiveSec=60

# Every 5 minutes (300 seconds)
# OnUnitActiveSec=300

# Every 30 seconds
# OnUnitActiveSec=30
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart flowmind-autopull.timer
```

### Enable Production Build

Edit `.ci/auto-pull.sh` and uncomment:

```bash
# Uncomment these lines:
if git diff --name-only HEAD@{1}...HEAD 2>/dev/null | grep -qE "^frontend/(src|public)/"; then
  echo "[autopull] Frontend code changed -> rebuilding"
  (cd frontend && pnpm build) || {
    echo "[autopull] ⚠️  Frontend build failed"
  }
fi
```

### Restart Backend Service (Production)

If using Gunicorn instead of uvicorn `--reload`, add to `.ci/auto-pull.sh`:

```bash
# After git reset --hard origin/main
systemctl --user restart flowmind-backend.service
```

---

## 🔧 Management Commands

### Stop Auto-Deploy

```bash
# Stop timer (keeps configuration)
systemctl --user stop flowmind-autopull.timer
```

### Start Auto-Deploy

```bash
systemctl --user start flowmind-autopull.timer
```

### Disable Auto-Deploy (Permanent)

```bash
# Disable timer (won't start on boot)
systemctl --user disable flowmind-autopull.timer

# Stop timer
systemctl --user stop flowmind-autopull.timer
```

### Re-enable Auto-Deploy

```bash
systemctl --user enable --now flowmind-autopull.timer
```

### View Service Configuration

```bash
systemctl --user cat flowmind-autopull.service
systemctl --user cat flowmind-autopull.timer
```

### Edit Service Configuration

```bash
# Edit service
systemctl --user edit --full flowmind-autopull.service

# Edit timer
systemctl --user edit --full flowmind-autopull.timer

# After editing, reload
systemctl --user daemon-reload
systemctl --user restart flowmind-autopull.timer
```

---

## 🐛 Troubleshooting

### Timer Not Running

**Check status:**
```bash
systemctl --user status flowmind-autopull.timer
```

**Common issues:**
- Timer not enabled: `systemctl --user enable flowmind-autopull.timer`
- systemd user instance not running: `loginctl enable-linger $USER`
- Wrong file permissions: `.ci/auto-pull.sh` should be executable

### Script Errors

**Check logs:**
```bash
journalctl --user -u flowmind-autopull.service -n 100
```

**Common errors:**
- `git fetch` fails: Check network/SSH keys
- `git reset --hard` fails: Check file permissions
- `pnpm install` fails: Check Node.js version
- Path not found: Verify repository is at `~/projects/Flowmind`

### Manual Script Test

```bash
# Run script directly
cd ~/projects/Flowmind
./.ci/auto-pull.sh

# Should output:
# [autopull] Starting at ...
# [autopull] No changes detected (...)
# [autopull] Done at ...
```

### systemd User Instance Not Persistent

If timer stops when you log out:

```bash
# Enable user lingering (keeps systemd running after logout)
loginctl enable-linger $USER

# Verify
loginctl show-user $USER | grep Linger
# Should show: Linger=yes
```

### Reset Everything

```bash
# Stop and disable timer
systemctl --user stop flowmind-autopull.timer
systemctl --user disable flowmind-autopull.timer

# Remove units
rm ~/.config/systemd/user/flowmind-autopull.{service,timer}

# Reload systemd
systemctl --user daemon-reload

# Start fresh from Step 2 in Installation
```

---

## 📊 Monitoring

### Dashboard View

```bash
# Watch timer and service status
watch -n 5 'systemctl --user list-timers | grep flowmind && echo "" && systemctl --user status flowmind-autopull.service | head -15'
```

### Log Summary

```bash
# Count successful vs failed runs today
journalctl --user -u flowmind-autopull.service --since today | grep -c "Done at"
journalctl --user -u flowmind-autopull.service --since today | grep -c "failed"
```

### Alert on Failures

Add to `.ci/auto-pull.sh`:

```bash
# At the top
NOTIFY_EMAIL="your@email.com"

# On error
if [ $? -ne 0 ]; then
  echo "Auto-pull failed at $(date)" | mail -s "Flowmind Auto-Deploy Failed" "$NOTIFY_EMAIL"
fi
```

---

## 🔒 Security Considerations

1. **Destructive Updates:** `git reset --hard` **discards all local changes**. Only use if you never commit directly on the server.

2. **Branch Protection:** Ensure `main` branch has protection rules enabled (see `GITHUB_PROTECTION_SETUP.md`).

3. **Service Hardening:** The systemd service includes:
   - `PrivateTmp=true` - Isolates /tmp directory
   - `NoNewPrivileges=true` - Prevents privilege escalation

4. **Logs:** Service logs may contain repository paths. Review with:
   ```bash
   journalctl --user -u flowmind-autopull.service --since today
   ```

5. **SSH Keys:** If using SSH for git, ensure keys are in `~/.ssh/` and added to ssh-agent.

---

## 🎯 Integration with Guard-Rails

Auto-deploy works seamlessly with guard-rails system:

1. **Branch Protection** (GitHub) blocks bad code from reaching `main`
2. **CI Checks** verify all code before merge
3. **Auto-Deploy** pulls only validated code from `main`
4. **Pre-commit Hooks** (local) prevent bad commits on server

**Workflow:**
```
Developer PR → CI Checks → Code Review → Merge to main → Auto-Deploy (60s) → Production
```

See `GITHUB_PROTECTION_SETUP.md` for branch protection setup.

---

## 📝 Files Reference

| File | Purpose |
|------|---------|
| `.ci/auto-pull.sh` | Main deployment script |
| `.ci/flowmind-autopull.service` | systemd service unit |
| `.ci/flowmind-autopull.timer` | systemd timer unit |
| `~/.config/systemd/user/flowmind-autopull.service` | Installed service |
| `~/.config/systemd/user/flowmind-autopull.timer` | Installed timer |

---

## 🚀 Quick Start (Copy-Paste)

```bash
# 1. Setup branch tracking
cd ~/projects/Flowmind
git checkout main
git branch --set-upstream-to=origin/main main

# 2. Install systemd units
mkdir -p ~/.config/systemd/user
cp .ci/flowmind-autopull.service ~/.config/systemd/user/
cp .ci/flowmind-autopull.timer ~/.config/systemd/user/
systemctl --user daemon-reload

# 3. Enable and start
systemctl --user enable --now flowmind-autopull.timer

# 4. Verify
systemctl --user list-timers | grep flowmind
journalctl --user -u flowmind-autopull.service -f
```

---

**Created:** 2025-10-17 by GitHub Copilot  
**Purpose:** Automated continuous deployment from GitHub to production server
