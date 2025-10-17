# GitHub Branch Protection & Security Setup

**Date:** October 17, 2025  
**Purpose:** Enable branch protection, code security, and automated dependency management

---

## 🔒 1. Enable Branch Protection (UI Method - RECOMMENDED)

### Step-by-Step:

1. **Navigate to Settings:**
   ```
   https://github.com/barbudangabriel-gif/Flowmind/settings/branches
   ```

2. **Add Branch Protection Rule:**
   - Click **"Add rule"** or **"Add branch protection rule"**
   - Branch name pattern: `main`

3. **Configure Protection Rules:**

   ✅ **Require a pull request before merging**
   - ✅ Require approvals: **1** (or more if team grows)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (CODEOWNERS file)

   ✅ **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - Search and select status checks:
     - `frontend` (from .github/workflows/ci.yml)
     - `backend` (from .github/workflows/ci.yml)

   ✅ **Require conversation resolution before merging**
   - All comments must be resolved

   ✅ **Require signed commits** (optional but recommended)

   ✅ **Require linear history** (optional - prevents merge commits)

   ✅ **Do not allow bypassing the above settings**
   - Even admins must follow rules (recommended)

   ❌ **Allow force pushes** - Keep DISABLED
   ❌ **Allow deletions** - Keep DISABLED

4. **Save Changes:**
   - Click **"Create"** or **"Save changes"**

---

## 🔒 2. Enable Branch Protection (CLI Method - Alternative)

### Using GitHub CLI:

```bash
# Install GitHub CLI (if not already installed)
# https://cli.github.com/

# Authenticate
gh auth login

# Enable branch protection
gh api -X PUT repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["frontend", "backend"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

---

## 🛡️ 3. Enable Code Security & Analysis

### Step-by-Step:

1. **Navigate to Security Settings:**
   ```
   https://github.com/barbudangabriel-gif/Flowmind/settings/security_analysis
   ```

2. **Enable Dependabot:**
   - ✅ **Dependabot alerts** - Get notified of vulnerabilities
   - ✅ **Dependabot security updates** - Auto-create PRs for security fixes
   - ✅ **Grouped security updates** - Combine related updates

3. **Enable Code Scanning:**
   - ✅ **CodeQL analysis** - Scan for security vulnerabilities
   - Click **"Set up"** → Choose **"Default"** setup

4. **Enable Secret Scanning:**
   - ✅ **Secret scanning** - Detect exposed API keys, tokens
   - ✅ **Push protection** - Block commits with secrets

5. **Enable Dependency Review:**
   - ✅ **Dependency review** - Review dependency changes in PRs

---

## 📦 4. Verify Dependabot Configuration

### Check Dependabot File:

File: `.github/dependabot.yml` ✅ (already created)

```yaml
version: 2
updates:
  - package-ecosystem: "npm"       # Frontend dependencies
  - package-ecosystem: "pip"       # Backend dependencies
  - package-ecosystem: "github-actions"  # CI/CD workflows
```

### Expected Behavior:

- **Weekly updates** (Monday 09:00)
- **Max 2 PRs per ecosystem** (prevents spam)
- **Auto-labels:** `dependencies`, `frontend`/`backend`/`ci`
- **Semantic commits:** `chore(deps): update package-name`

---

## ✅ 5. Verify CODEOWNERS

File: `CODEOWNERS` ✅ (already created)

```
# Default owner
* @barbudangabriel-gif

# Frontend requires review
/frontend/* @barbudangabriel-gif

# Backend requires review
/backend/* @barbudangabriel-gif

# Dependencies require review
/frontend/package.json @barbudangabriel-gif
/backend/requirements.txt @barbudangabriel-gif
```

### Expected Behavior:

- All PRs touching these files auto-request review from @barbudangabriel-gif
- Cannot merge without approval (if "Require review from Code Owners" enabled)

---

## ✅ 6. Verify PR Template

File: `.github/pull_request_template.md` ✅ (already created)

### Expected Behavior:

- All new PRs auto-populate with checklist template
- Ensures:
  - Scope limited (diff <80 lines)
  - No dependency changes without reason
  - Formatting verified (Prettier/Black)
  - Testing steps documented
  - Breaking changes flagged

---

## 🧪 7. Test Branch Protection

### Test 1: Direct Push to Main (Should FAIL)

```bash
git checkout main
git pull
echo "test" >> README.md
git add README.md
git commit -m "test: direct push"
git push origin main
# Expected: ❌ remote rejected (branch protection)
```

### Test 2: PR Without CI Pass (Should BLOCK)

```bash
git checkout -b test/broken-code
echo "bad code" >> backend/test.py
git add backend/test.py
git commit -m "test: bad code"
git push origin test/broken-code
# Create PR via GitHub
# Expected: ❌ Cannot merge until CI passes
```

### Test 3: PR Without Review (Should BLOCK)

```bash
git checkout -b test/no-review
echo "good code" >> backend/test_good.py
git add backend/test_good.py
git commit -m "test: good code"
git push origin test/no-review
# Create PR via GitHub
# Expected: ❌ Cannot merge until approval
```

### Test 4: Valid PR (Should SUCCEED)

```bash
git checkout -b fix/valid-change
# Make minimal change (1-3 files, <80 lines)
black backend/
git add backend/
git commit -m "fix: proper change"
git push origin fix/valid-change
# Create PR via GitHub
# Wait for CI ✅
# Get approval ✅
# Expected: ✅ Can merge
```

---

## 🎯 8. Success Criteria

After setup complete, verify:

- [ ] Branch protection active on `main`
- [ ] Cannot push directly to `main`
- [ ] Cannot merge PR without CI pass
- [ ] Cannot merge PR without approval
- [ ] CODEOWNERS auto-requests review
- [ ] PR template auto-populates
- [ ] Dependabot alerts enabled
- [ ] Secret scanning enabled
- [ ] CodeQL analysis enabled
- [ ] First Dependabot PR created (within 1 week)

---

## 📊 9. Monitoring & Maintenance

### Weekly Tasks:

- [ ] Review Dependabot PRs (Monday mornings)
- [ ] Check security alerts (Dependabot/CodeQL)
- [ ] Review failed CI runs (GitHub Actions)

### Monthly Tasks:

- [ ] Update branch protection rules if needed
- [ ] Review CODEOWNERS accuracy
- [ ] Update PR template based on common issues

### Commands:

```bash
# Check branch protection status
gh api repos/barbudangabriel-gif/Flowmind/branches/main/protection

# List open Dependabot PRs
gh pr list --label dependencies

# View security alerts
gh api repos/barbudangabriel-gif/Flowmind/dependabot/alerts

# Check CI runs
gh run list --workflow=ci.yml
```

---

## 🆘 10. Troubleshooting

### Issue: "Branch protection not enforced for admin"

**Solution:** Enable "Do not allow bypassing the above settings"

```bash
gh api -X PUT repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  -f enforce_admins=true
```

---

### Issue: "CI status checks not appearing"

**Solution:** CI must run at least once for checks to be selectable

```bash
# Push to branch to trigger CI
git push origin chore/guardrails

# Wait for CI to complete
gh run watch

# Then add checks to branch protection
```

---

### Issue: "CODEOWNERS not requesting review"

**Solution:** Enable "Require review from Code Owners" in branch protection

Settings → Branches → Edit rule → ✅ Require review from Code Owners

---

### Issue: "Dependabot not creating PRs"

**Solution:** Check Dependabot logs

```bash
# View Dependabot alerts/logs
https://github.com/barbudangabriel-gif/Flowmind/security/dependabot

# Manually trigger Dependabot
# Settings → Code security → Dependabot → Check for updates
```

---

## 🚀 Quick Setup Checklist

```bash
# 1. Merge guard-rails PR
gh pr merge 2 --squash

# 2. Enable branch protection (UI method - see section 1)
# https://github.com/barbudangabriel-gif/Flowmind/settings/branches

# 3. Enable code security (UI method - see section 3)
# https://github.com/barbudangabriel-gif/Flowmind/settings/security_analysis

# 4. Test branch protection
git checkout -b test/protection
echo "test" >> README.md
git add README.md
git commit -m "test: branch protection"
git push origin test/protection
gh pr create --title "test: branch protection" --body "Testing"
# Try to merge → should require approval + CI

# 5. Cleanup test
gh pr close --delete-branch
```

---

**🔒 Protection Active - Repository Secured!**

**Next:** Start using guard-rails daily workflow:
```
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.
```
