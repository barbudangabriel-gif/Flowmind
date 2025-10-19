# Branch Protection Rules Setup

**Date:** October 19, 2025  
**Branch:** main  
**Status:** Ready to enable

---

## 🎯 Purpose

Enable branch protection rules on `main` branch to:
- Require status checks before merge
- Prevent force pushes
- Maintain code quality standards
- Automate compliance verification

---

## 📋 Manual Setup Instructions

### Option 1: GitHub UI (Recommended for Visual Confirmation)

1. Go to: https://github.com/barbudangabriel-gif/Flowmind/settings/branches
2. Click **"Add rule"** or edit existing rule for `main`
3. Configure as follows:

**Branch name pattern:** `main`

**Protection Rules:**
- ✅ **Require a pull request before merging**
  - Required approvals: 0 (optional, set to 1 for team workflows)
  - Dismiss stale reviews: NO
  - Require review from Code Owners: NO
  
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **Required checks (add these):**
    - `Validate Python 3.12 Compilation` (from Python Indent Validation workflow)
    - `Python Quality Checks` (from Python Code Quality workflow)
    - `Unit Tests` (from Backend Testing workflow)
    - `Backend import sanity` (from build-only workflow)
  
- ✅ **Require conversation resolution before merging**
  
- ❌ **Require signed commits** (optional, enable if needed)
  
- ❌ **Require linear history** (optional, depends on workflow)
  
- ❌ **Include administrators** (disable to allow admin override)
  
- ✅ **Restrict who can push** (optional, for team management)
  
- ✅ **Allow force pushes** (DISABLE)
  
- ✅ **Allow deletions** (DISABLE)

4. Click **"Create"** or **"Save changes"**

---

### Option 2: GitHub CLI (Fastest Method)

```bash
# Requires: gh CLI with admin permissions
# Run from project root

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["Validate Python 3.12 Compilation","Python Quality Checks","Unit Tests","Backend import sanity"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"required_approving_review_count":0}' \
  -f restrictions=null \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f required_conversation_resolution=true
```

---

### Option 3: Terraform/IaC (For Advanced Users)

```hcl
resource "github_branch_protection" "main" {
  repository_id = "barbudangabriel-gif/Flowmind"
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = [
      "Validate Python 3.12 Compilation",
      "Python Quality Checks",
      "Unit Tests",
      "Backend import sanity"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 0
  }

  enforce_admins              = false
  allows_force_pushes         = false
  allows_deletions            = false
  require_conversation_resolution = true
}
```

---

## ✅ Verification Steps

After enabling protection rules:

1. **Verify rules are active:**
   ```bash
   gh api /repos/barbudangabriel-gif/Flowmind/branches/main/protection
   ```

2. **Test with a test PR:**
   - Create test branch: `git checkout -b test/branch-protection`
   - Make small change: `echo "test" >> README.md`
   - Push and create PR
   - Verify status checks run
   - Verify merge is blocked until checks pass

3. **Check required checks:**
   - Go to PR → "Checks" tab
   - Confirm all 4 workflows run:
     - Python Indent Validation ✅
     - Python Code Quality ✅
     - Backend Testing ✅
     - build-only ✅

---

## 📊 Required Status Checks Details

### 1. Python Indent Validation
- **Workflow:** `.github/workflows/python-indent-validation.yml`
- **Check Name:** `Validate Python 3.12 Compilation`
- **Purpose:** Ensure all Python files compile with Python 3.12
- **Runtime:** ~10-15 seconds

### 2. Python Code Quality
- **Workflow:** `.github/workflows/python-quality.yml`
- **Check Name:** `Python Quality Checks`
- **Purpose:** Black formatting, Ruff linting, MyPy types, Bandit security
- **Runtime:** ~30-45 seconds

### 3. Backend Testing
- **Workflow:** `.github/workflows/backend-testing.yml`
- **Check Names:**
  - `Unit Tests` (blocking)
  - `Integration Tests` (informational)
  - `Performance Tests` (informational)
- **Purpose:** Run pytest suite, verify service health
- **Runtime:** ~60-90 seconds

### 4. Build-Only Verification
- **Workflow:** `.github/workflows/build-only.yml`
- **Check Names:**
  - `Frontend build` (optional)
  - `Backend import sanity` (blocking)
- **Purpose:** Verify builds complete without errors
- **Runtime:** ~120-180 seconds

---

## 🚨 Important Notes

### For Administrators:
- Branch protection does NOT apply to admins by default
- To enforce on admins: Enable **"Include administrators"** (not recommended for sole maintainer)
- Emergency override: Use `--admin` flag with `gh pr merge`

### For Contributors:
- All PRs must pass status checks before merge
- Force push to `main` is BLOCKED
- Deleting `main` branch is BLOCKED
- Commit directly to `main` is BLOCKED (use PRs)

### For CI/CD:
- GitHub Actions token has write access
- Workflows can push to `main` after status checks pass
- Use `GITHUB_TOKEN` for authentication (already configured)

---

## 🔄 Update Protection Rules

To modify protection rules later:

```bash
# Add new required check
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/barbudangabriel-gif/Flowmind/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["Validate Python 3.12 Compilation","Python Quality Checks","Unit Tests","Backend import sanity","NEW_CHECK_NAME"]}'

# Disable protection temporarily (NOT RECOMMENDED)
gh api \
  --method DELETE \
  /repos/barbudangabriel-gif/Flowmind/branches/main/protection
```

---

## 📚 Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [GitHub API Reference](https://docs.github.com/en/rest/branches/branch-protection)

---

## ✅ Checklist

Before enabling protection rules, ensure:

- [x] All 4 workflows exist in `.github/workflows/`
- [x] Workflows have been tested on at least one PR
- [x] Required checks are named correctly
- [x] Team members understand the process
- [x] Emergency override process is documented

After enabling:

- [ ] Verify rules are active (check repo settings)
- [ ] Test with a test PR
- [ ] Communicate to team (if applicable)
- [ ] Update team documentation

---

**Setup Status:** ⏳ MANUAL ACTION REQUIRED  
**Next Step:** Follow Option 1 (GitHub UI) or Option 2 (GitHub CLI)  
**ETA:** 2-3 minutes

Once enabled, branch protection ensures code quality and prevents accidental breakage! 🛡️
