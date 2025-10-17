# Guard-Rails Deployment Checklist

**Date:** 2025-10-17  
**PR:** [#2 - Comprehensive Guard-Rails System](https://github.com/barbudangabriel-gif/Flowmind/pull/2)  
**Status:** Ready for deployment

---

## 🎯 Pre-Deployment

### ✅ Prerequisites Checklist

- [ ] PR #2 created and open
- [ ] All commits pushed to `chore/guardrails`
- [ ] Documentation reviewed (~4,000 lines)
- [ ] Auto-deploy system configured (.ci/ files)

**Current Status:**
```bash
# Check PR status
gh pr view 2

# Verify branch
git status
# Should show: On branch chore/guardrails, nothing to commit, working tree clean
```

---

## 📋 Deployment Steps (In Order)

### Step 1: Review PR #2 (Visual Check)

**GitHub UI:** https://github.com/barbudangabriel-gif/Flowmind/pull/2

**Critical Files to Review:**

1. **`.github/workflows/ci.yml`**
   - [ ] Frontend job: `pnpm lint`
   - [ ] Backend job: `black --check`, `isort --check-only`
   - [ ] Triggers: `push`, `pull_request`

2. **`.github/workflows/tests.yml`**
   - [ ] Frontend tests: `pnpm test --if-present`
   - [ ] Backend tests: `pytest -q --maxfail=1`
   - [ ] Graceful fallback if no tests

3. **`CODEOWNERS`**
   - [ ] Default owner: `@barbudangabriel-gif`
   - [ ] Frontend/* requires review
   - [ ] Backend/* requires review
   - [ ] Config files protected

4. **`.ci/auto-pull.sh`**
   - [ ] Executable permissions (`chmod +x`)
   - [ ] Safe `git reset --hard` logic
   - [ ] Dependency detection (lockfiles)

5. **`.github/pull_request_template.md`**
   - [ ] Pre-submission checklist
   - [ ] Scope validation (<80 lines)
   - [ ] Testing steps template

**Quick Review Command:**
```bash
# View files in PR
gh pr view 2 --json files --jq '.files[].path'

# View specific file
gh pr diff 2 --name-only | grep -E "(ci.yml|CODEOWNERS|auto-pull.sh)"
```

---

### Step 2: Fix Backend Formatting (BLOCKER)

**Current Issue:** 97 backend files have indentation/parsing errors blocking CI.

**Create Formatting Fix PR:**

```bash
# 1. Switch to main
cd ~/projects/Flowmind  # or /workspaces/Flowmind in Codespaces
git checkout main
git pull origin main

# 2. Create fix branch
git checkout -b fix/backend-formatting

# 3. Run Black formatter (fixes indentation)
cd backend
black .

# 4. Verify fixes
black --check .
isort --check-only .

# 5. Check what changed
git diff --stat

# 6. Commit
git add -A
git commit -m "fix: resolve backend formatting and indentation errors

Fixes 97 files with mixed tabs/spaces and parsing issues.
Required for guard-rails PR #2 CI to pass.

Changes:
- Applied Black formatter to all Python files
- Fixed indentation errors preventing Black parsing
- Ensured consistent 4-space indentation

Resolves CI failures in PR #2."

# 7. Push
git push origin fix/backend-formatting

# 8. Create PR
gh pr create \
  --base main \
  --head fix/backend-formatting \
  --title "fix: Backend Formatting & Indentation Errors (Unblocks Guard-Rails)" \
  --body "## Problem

97 backend files have indentation/parsing errors blocking guard-rails PR #2.

## Solution

Applied Black formatter to resolve:
- Mixed tabs/spaces
- Invalid indentation
- Parsing errors

## Testing

\`\`\`bash
cd backend
black --check .  # Should pass
isort --check-only .  # Should pass
python -m py_compile **/*.py  # Should pass
\`\`\`

## Impact

- Unblocks PR #2 (guard-rails system)
- No functional changes (formatting only)
- Safe to merge

## Related

Blocks: #2"

# 9. Wait for CI to pass, then merge
gh pr status
```

**Expected CI Result:**
- ✅ `ci/backend` - Should PASS (formatting now correct)
- ✅ `ci/frontend` - Should PASS (no frontend changes)
- ✅ `tests/backend-tests` - Should PASS
- ✅ `tests/frontend-tests` - Should PASS

**Merge Formatting PR:**
```bash
# After CI passes
gh pr merge fix/backend-formatting --squash --delete-branch
```

---

### Step 3: Rebase Guard-Rails PR

**After formatting PR merged to main:**

```bash
# 1. Switch to guard-rails branch
git checkout chore/guardrails

# 2. Fetch latest main
git fetch origin main

# 3. Rebase onto updated main
git rebase origin/main

# If conflicts (unlikely):
# git status
# (resolve conflicts)
# git add -A
# git rebase --continue

# 4. Force push (rebase rewrites history)
git push origin chore/guardrails --force-with-lease

# 5. Verify CI now passes
gh pr checks 2
```

**Expected CI Result After Rebase:**
- ✅ All 9 checks should PASS (formatting fixed in main)

---

### Step 4: Enable Branch Protection

**GitHub UI Method:**

1. Go to: https://github.com/barbudangabriel-gif/Flowmind/settings/branches
2. Click: **Add branch protection rule**
3. Branch name pattern: `main`
4. Enable settings:

**Required:**
- [x] **Require a pull request before merging**
  - [x] Require approvals: **1** (yourself)
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Search and add:
    - `ci / frontend`
    - `ci / backend`
    - `tests / Frontend tests`
    - `tests / Backend tests`

- [x] **Require conversation resolution before merging**

- [x] **Do not allow bypassing the above settings**

**Optional (Recommended):**
- [x] Require signed commits
- [x] Require linear history
- [x] Include administrators (enforces rules on you too)

5. Click: **Create** (or **Save changes**)

**CLI Method (Alternative):**

```bash
# Install GitHub CLI extension (if not installed)
gh extension install mislav/gh-branch

# Create protection rule
gh api repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field required_pull_request_reviews[require_code_owner_reviews]=true \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=ci%20/%20frontend \
  --field required_status_checks[contexts][]=ci%20/%20backend \
  --field required_status_checks[contexts][]=tests%20/%20Frontend%20tests \
  --field required_status_checks[contexts][]=tests%20/%20Backend%20tests \
  --field enforce_admins=true \
  --field required_conversation_resolution=true
```

**Verify Protection:**
```bash
# Check protection status
gh api repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  --jq '{
    required_status_checks: .required_status_checks.contexts,
    required_reviews: .required_pull_request_reviews.required_approving_review_count,
    enforce_admins: .enforce_admins.enabled
  }'
```

---

### Step 5: Merge PR #2

**Pre-Merge Checklist:**
- [ ] All CI checks passing (9/9 green)
- [ ] Backend formatting fixed and merged
- [ ] Branch protection enabled
- [ ] Code review completed (self-review OK for now)

**Merge Command:**
```bash
# Check final status
gh pr checks 2

# Approve PR (if you're the reviewer)
gh pr review 2 --approve --body "Guard-rails system looks good. All checks passing. Ready to merge."

# Merge PR
gh pr merge 2 --squash --delete-branch --body "Merging guard-rails system.

Delivered:
- 11 documents (~4,000 lines)
- 4-layer architecture (Editor → Pre-commit → CI → Branch Protection)
- Auto-deploy system (systemd timer)
- Complete testing & verification guides

Next: Install guard-rails locally and setup auto-deploy."

# Verify merge
git checkout main
git pull origin main
git log --oneline -5
# Should show squashed guard-rails commit
```

---

### Step 6: Install Guard-Rails Locally

#### A. Frontend (Codespaces or Local)

```bash
cd ~/projects/Flowmind/frontend  # or /workspaces/Flowmind/frontend

# 1. Install dependencies
pnpm install

# 2. Initialize Husky (if not already)
pnpm dlx husky init

# If already exists, just verify:
ls -la .husky/
# Should see: pre-commit file

# 3. Test pre-commit hook
echo "const bad={a:1}" > test-bad-format.ts
git add test-bad-format.ts
git commit -m "test: bad formatting"

# Expected output:
# ✖ eslint --max-warnings=0 test-bad-format.ts
# husky - pre-commit hook exited with code 1 (error)

# 4. Clean up test
rm test-bad-format.ts
git reset HEAD

# 5. Verify lint works
pnpm lint
# Should pass with no errors
```

#### B. Backend (WSL or Local Linux)

```bash
cd ~/projects/Flowmind/backend

# 1. Upgrade pip
pip install -U pip

# 2. Install formatting tools
pip install black isort pre-commit

# 3. Install pre-commit hooks
pre-commit install

# Output should show:
# pre-commit installed at .git/hooks/pre-commit

# 4. Test pre-commit hook
echo "def bad( ):\n pass" > test_bad_format.py
git add test_bad_format.py
git commit -m "test: bad formatting"

# Expected output:
# black....................................................................Failed
# isort....................................................................Failed

# 5. Clean up test
rm test_bad_format.py
git reset HEAD

# 6. Verify formatting works
black --check .
isort --check-only .
# Both should pass
```

---

### Step 7: Setup Auto-Deploy (Optional - WSL Only)

**Only if you want automatic deployment from GitHub to local WSL server.**

```bash
# 1. Ensure on main branch with tracking
cd ~/projects/Flowmind
git checkout main
git branch --set-upstream-to=origin/main main
git pull

# 2. Create systemd user directory
mkdir -p ~/.config/systemd/user

# 3. Copy service units
cp .ci/flowmind-autopull.service ~/.config/systemd/user/
cp .ci/flowmind-autopull.timer ~/.config/systemd/user/

# 4. Reload systemd
systemctl --user daemon-reload

# 5. Enable and start timer
systemctl --user enable flowmind-autopull.timer
systemctl --user start flowmind-autopull.timer

# 6. Verify timer is active
systemctl --user list-timers | grep flowmind

# Expected output:
# NEXT                        LEFT     LAST  PASSED  UNIT                       ACTIVATES
# Thu 2025-10-17 23:00:00 UTC 45s left n/a   n/a     flowmind-autopull.timer    flowmind-autopull.service

# 7. Watch logs (Ctrl+C to exit)
journalctl --user -u flowmind-autopull.service -f

# Expected output every 60s:
# [autopull] Starting at 2025-10-17 23:00:00
# [autopull] No changes detected (cec98a5)
# [autopull] Done at 2025-10-17 23:00:01
```

**Enable Lingering (keeps timer running after logout):**
```bash
loginctl enable-linger $USER

# Verify
loginctl show-user $USER | grep Linger
# Should show: Linger=yes
```

---

## ✅ Verification Tests

### Test 1: CI Pipeline Works

```bash
# Create test branch
git checkout -b test/ci-check
echo "# Test change" >> README.md
git add README.md
git commit -m "test: verify CI pipeline"
git push origin test/ci-check

# Create PR
gh pr create --base main --head test/ci-check --title "test: CI verification" --body "Testing CI pipeline"

# Wait 2-3 minutes, check status
gh pr checks

# Expected:
# ✓ ci / frontend
# ✓ ci / backend
# ✓ tests / Frontend tests
# ✓ tests / Backend tests

# Close and delete test PR
gh pr close --delete-branch
```

### Test 2: Pre-Commit Hooks Block Bad Code

**Frontend Test:**
```bash
cd frontend
echo "const bad={a:1}" > test.ts
git add test.ts
git commit -m "test"

# Should FAIL with:
# ✖ Problems found in test.ts
# husky - pre-commit hook exited with code 1

rm test.ts
git reset HEAD
```

**Backend Test:**
```bash
cd backend
echo "def bad( ):\n    pass" > test.py
git add test.py
git commit -m "test"

# Should FAIL with:
# black....................................................................Failed
# isort....................................................................Failed

rm test.py
git reset HEAD
```

### Test 3: Branch Protection Blocks Direct Push

```bash
# Try to push directly to main (should fail)
git checkout main
echo "# Direct change" >> README.md
git add README.md
git commit -m "test: direct push"
git push origin main

# Expected error:
# remote: error: GH006: Protected branch update failed for refs/heads/main.
# remote: error: Changes must be made through a pull request.
```

### Test 4: Auto-Deploy Detects Changes

**If auto-deploy enabled:**

```bash
# 1. Make a change and merge to main via PR
git checkout -b test/auto-deploy
echo "# Test auto-deploy" >> README.md
git add README.md
git commit -m "test: auto-deploy detection"
git push origin test/auto-deploy
gh pr create --base main --head test/auto-deploy --title "test: auto-deploy" --body "Test"
gh pr merge test/auto-deploy --squash --delete-branch

# 2. Wait 60 seconds, check auto-deploy logs
journalctl --user -u flowmind-autopull.service -n 20

# Expected output:
# [autopull] Changes detected on origin/main
# [autopull]   Local:  cec98a5
# [autopull]   Remote: abc1234
# [autopull] Updating to origin/main...
# HEAD is now at abc1234 test: auto-deploy detection
# [autopull] ✅ Code updated
# [autopull] 🚀 Deployment complete
```

---

## 📊 Success Criteria

### ✅ All Systems Operational

- [ ] **PR #2 merged** to main
- [ ] **Branch protection** enabled (requires PR + CI)
- [ ] **Frontend pre-commit** blocks bad formatting
- [ ] **Backend pre-commit** blocks bad formatting
- [ ] **CI pipeline** runs on all PRs
- [ ] **Auto-deploy** pulls changes every 60s (optional)
- [ ] **Direct push to main** blocked

### 🎯 Guard-Rails Active

**Test Matrix:**

| Test | Expected Result | Status |
|------|-----------------|--------|
| Create PR with bad formatting | CI fails ❌ | [ ] |
| Pre-commit with bad code | Hook blocks commit ❌ | [ ] |
| Direct push to main | GitHub blocks push ❌ | [ ] |
| Valid PR with CI passing | Merge allowed ✅ | [ ] |
| Auto-deploy after merge | Pulls within 60s ✅ | [ ] |

---

## 🐛 Troubleshooting

### Issue: CI Checks Not Running

**Solution:**
```bash
# Check workflow files exist
ls -la .github/workflows/

# Verify workflow syntax
cat .github/workflows/ci.yml

# Re-trigger CI
gh pr close 2 && gh pr reopen 2
```

### Issue: Pre-Commit Hook Not Working

**Frontend:**
```bash
cd frontend
pnpm dlx husky init
cat .husky/pre-commit  # Should show: pnpm lint-staged
```

**Backend:**
```bash
cd backend
pre-commit install --install-hooks
pre-commit run --all-files  # Test on all files
```

### Issue: Branch Protection Not Enforcing

**Check Settings:**
```bash
gh api repos/barbudangabriel-gif/Flowmind/branches/main/protection

# Verify Include Administrators is checked
```

### Issue: Auto-Deploy Not Running

**Debug:**
```bash
# Check timer status
systemctl --user status flowmind-autopull.timer

# Check service status
systemctl --user status flowmind-autopull.service

# Check logs
journalctl --user -u flowmind-autopull.service -n 50

# Manual trigger
systemctl --user start flowmind-autopull.service
```

---

## 📝 Post-Deployment

### Update COPILOT_COMMIT_CONTRACT.md

**Every future Copilot session MUST start with:**
```
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.
```

### Daily Workflow

**Before coding:**
```bash
git checkout main
git pull
git checkout -b feature/my-feature
```

**Before committing:**
```bash
# Frontend
cd frontend
pnpm format
pnpm lint

# Backend
cd backend
black .
isort .
```

**Commit (pre-commit runs automatically):**
```bash
git add <files>
git commit -m "feat: description"
```

**Create PR:**
```bash
git push origin feature/my-feature
gh pr create --base main --head feature/my-feature
```

**CI will:**
1. Run lint/format checks
2. Run tests
3. Block merge if any fail

**After approval:**
```bash
gh pr merge --squash --delete-branch
```

**Auto-deploy (if enabled):**
- Changes appear in WSL within 60 seconds
- Check logs: `journalctl --user -u flowmind-autopull.service -f`

---

## 🎓 Summary

**What We Built:**
- 4-layer guard-rails (Editor → Pre-commit → CI → Branch Protection)
- Auto-deploy system (GitHub → WSL in 60s)
- Complete documentation (~4,000 lines)
- Testing & verification guides

**What It Prevents:**
- Mass reformatting (164 files → NEVER)
- IndentationError (mixed tabs/spaces)
- Import errors
- CORS misconfigurations
- Bad commits to main
- Code chaos

**Result:**
- ✅ Professional development workflow
- ✅ Automated quality enforcement
- ✅ Continuous deployment
- ✅ Zero tolerance for bad code in main

---

**Created:** 2025-10-17 by GitHub Copilot  
**Purpose:** Complete deployment guide for guard-rails system  
**Status:** Ready for execution

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Fix backend formatting (separate PR)
git checkout main && git checkout -b fix/backend-formatting
cd backend && black . && git add -A
git commit -m "fix: backend formatting (97 files)"
git push origin fix/backend-formatting
gh pr create && gh pr merge --squash

# 2. Rebase guard-rails PR
git checkout chore/guardrails
git rebase origin/main
git push origin chore/guardrails --force-with-lease

# 3. Enable branch protection (GitHub UI)
# Settings → Branches → Add rule → main

# 4. Merge guard-rails PR
gh pr merge 2 --squash --delete-branch

# 5. Install locally
git checkout main && git pull
cd frontend && pnpm install && pnpm dlx husky init
cd ../backend && pip install black isort pre-commit && pre-commit install

# 6. Setup auto-deploy (optional)
cp .ci/flowmind-autopull.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now flowmind-autopull.timer
journalctl --user -u flowmind-autopull.service -f

# ✅ DONE!
```
