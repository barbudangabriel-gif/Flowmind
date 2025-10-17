# Pull Request - FlowMind

## 📋 What This Changes

<!-- Clear description of what this PR does (1-2 sentences) -->

## ✅ Pre-Submission Checklist

**Code Quality:**
- [ ] Scope limited (diff <80 lines, only necessary files)
- [ ] No changes to dependencies/lockfiles (unless explicitly needed)
- [ ] Respects Prettier/Black/EditorConfig formatting
- [ ] Read and followed COPILOT_COMMIT_CONTRACT.md

**Testing:**
- [ ] Frontend: `pnpm format && pnpm lint` passes
- [ ] Backend: `black --check . && isort --check-only .` passes
- [ ] Endpoints verified: `curl http://localhost:8000/health`
- [ ] Manual testing completed (describe below)

**Documentation:**
- [ ] Updated relevant docs (if needed)
- [ ] Added comments for complex logic
- [ ] Commit message follows convention: `type: description`

## 🧪 Testing Steps

<!-- How to verify this works -->

```bash
# Commands to test this change
```

**Expected result:**
<!-- What should happen -->

**Actual result:**
<!-- What actually happened -->

## 🔗 Related Links

<!-- Links to issues, designs, or documentation -->

- Issue: #
- Design: 
- Docs: 

## 📸 Screenshots (if applicable)

<!-- Before/after screenshots for UI changes -->

## 🚨 Breaking Changes

<!-- Does this break existing functionality? -->

- [ ] No breaking changes
- [ ] Breaking changes (describe below)

**If breaking:**
<!-- Migration steps, deprecation notices, etc. -->

## 📝 Additional Notes

<!-- Anything else reviewers should know -->

---

**Review Checklist (for reviewers):**
- [ ] Code follows minimal change philosophy (<80 lines)
- [ ] No unnecessary reformatting or refactoring
- [ ] Formatting passes (Prettier/Black)
- [ ] Tests verify the fix/feature
- [ ] Documentation updated if needed
- [ ] No security issues introduced
