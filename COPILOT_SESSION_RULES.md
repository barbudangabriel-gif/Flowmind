# Copilot Session Rules - FlowMind

**📌 PASTE THIS AT START OF EVERY COPILOT SESSION:**
```
@workspace Read COPILOT_SESSION_RULES.md and follow strictly.
```

---

## ROLE
You are a **minimal-change code fixer**. Your goal is **surgical precision**, not wholesale rewrites.

---

## DO ✅ (Allowed Actions)

### Files You CAN Modify:
- `backend/app/main.py` (imports, CORS, router registration)
- `backend/app/routers/flow.py` (flow endpoints)
- `backend/app/services/tradestation.py` (TS OAuth service)
- `backend/app/routers/tradestation_auth.py` (TS OAuth routes)
- `backend/app/deps/tradestation.py` (TS dependencies)
- `frontend/.env.local` (backend URL configuration)
- `backend/.env` (CORS origins, TS credentials)

### Allowed Operations:
- ✅ Fix indentation errors with `black app/routers/flow.py`
- ✅ Add missing imports
- ✅ Update environment variables
- ✅ Fix type annotations
- ✅ Add logging statements
- ✅ Fix syntax errors (SyntaxError, IndentationError)
- ✅ Update CORS configuration
- ✅ Add new endpoints to existing routers

---

## DON'T ❌ (Forbidden Actions)

### Files You CANNOT Modify (Unless Explicitly Requested):
- ❌ `requirements.txt` / `package.json` (dependency files)
- ❌ `package-lock.json` / `yarn.lock` (lockfiles - NEVER touch)
- ❌ Other routers: `backend/app/routers/tradestation.py`, `options.py`, etc.
- ❌ Database models: `backend/app/models/*`
- ❌ Migrations: `backend/alembic/*`
- ❌ Git configuration: `.git/*`, `.gitignore`
- ❌ CI/CD: `.gitlab-ci.yml`, `.github/workflows/*`

### Forbidden Operations:
- ❌ DO NOT reindent entire files (only fix syntax errors in specific functions)
- ❌ DO NOT add new dependencies without explicit approval
- ❌ DO NOT rewrite working code ("refactoring" for "cleanliness")
- ❌ DO NOT modify files outside the scope of the current task
- ❌ DO NOT change database schemas without migration plan
- ❌ DO NOT remove existing functionality without confirmation

---

## CHECK ✔️ (Before Committing)

### Backend Checks:
```bash
cd backend

# 1. Format check (don't auto-fix unless approved)
black --check app/main.py app/routers/flow.py app/services/tradestation.py

# 2. Type check
mypy app/main.py --ignore-missing-imports

# 3. Syntax check
python -m py_compile app/routers/flow.py
python -m py_compile app/services/tradestation.py

# 4. Import check
python -c "from app.main import app; print('✅ Imports OK')"

# 5. Smoke test
curl http://localhost:8000/health
curl http://localhost:8000/api/flow/health
curl http://localhost:8000/api/ts/status
```

### Frontend Checks (if modified):
```bash
cd frontend

# 1. TypeScript check (if applicable)
npm run typecheck 2>/dev/null || echo "No typecheck script"

# 2. ESLint
npm run lint 2>/dev/null || echo "No lint script"

# 3. Build test
npm run build
```

---

## CONFIRM ✅ (After Changes)

### Mandatory Verifications:
- [ ] **Backend starts without errors:**
  ```bash
  uvicorn app.main:app --reload --port 8000
  # Should show: "Application startup complete"
  ```

- [ ] **All smoke tests pass:**
  ```bash
  curl http://localhost:8000/health
  # Should return: {"ok": true}
  
  curl http://localhost:8000/api/flow/health
  # Should return: {"ok": true, "scope": "flow"}
  ```

- [ ] **No new dependencies added:**
  ```bash
  git diff requirements.txt package.json
  # Should be empty unless explicitly approved
  ```

- [ ] **Git diff shows ONLY intended changes:**
  ```bash
  git diff --stat
  # Review each file - no accidental mass reformatting
  ```

- [ ] **No breaking changes:**
  - Existing endpoints still work
  - Frontend can still connect
  - Tests still pass (if test suite exists)

---

## WORKFLOW 🔄

### For Bug Fixes:
1. **Identify** the exact error (file, line number, error message)
2. **Isolate** the minimal code change needed
3. **Apply** fix to ONLY that code block
4. **Test** the specific endpoint/function that was broken
5. **Verify** no side effects (run smoke tests)
6. **Commit** with clear message describing fix

### For New Features:
1. **Plan** where new code goes (which file, which function)
2. **Create** new functions/endpoints (don't modify existing unless necessary)
3. **Add** to router registration in `app/main.py`
4. **Test** new endpoint in isolation
5. **Document** in docstring and API docs
6. **Commit** with feature description

### For Environment Changes:
1. **Update** `.env` or `.env.local` files
2. **Document** new variables in README or setup guide
3. **Test** with both old and new values (backward compatibility)
4. **Commit** with clear explanation of what changed

---

## EXAMPLES 📝

### ✅ GOOD: Minimal Fix
```python
# File: backend/app/routers/flow.py
# Task: Fix IndentationError on line 26

# BEFORE (broken):
def make_builder_link(row):
 symbol = row.get("symbol", "")  # ❌ 1 space indent

# AFTER (fixed):
def make_builder_link(row):
    symbol = row.get("symbol", "")  # ✅ 4 spaces
```

**Git diff shows:**
```diff
- symbol = row.get("symbol", "")
+     symbol = row.get("symbol", "")
```
Only 1 line changed. Perfect! ✅

---

### ❌ BAD: Mass Reformatting
```bash
# Running black on entire codebase
black backend/

# Result:
reformatted 164 files
```

**Git diff shows:**
```diff
Changed 164 files, 2000+ lines modified
```
Too many changes! Hard to review! ❌

**Better approach:**
```bash
# Fix only the broken file
black backend/app/routers/flow.py

# Result:
reformatted 1 file
```

---

### ✅ GOOD: Adding New Endpoint
```python
# File: backend/app/routers/flow.py
# Task: Add /api/flow/summary endpoint

@router.get("/summary")
async def flow_summary(limit: int = 24) -> Dict[str, Any]:
    """Get flow summary with top symbols."""
    # New function, doesn't touch existing code
    return {"summary": "not-implemented-yet", "limit": limit}
```

**Git diff:**
```diff
+ @router.get("/summary")
+ async def flow_summary(limit: int = 24) -> Dict[str, Any]:
+     """Get flow summary with top symbols."""
+     return {"summary": "not-implemented-yet", "limit": limit}
```
Clean addition, no existing code modified. ✅

---

### ❌ BAD: "Refactoring" Working Code
```python
# File: backend/app/services/tradestation.py
# Task: "Clean up" the code

# BEFORE (working):
def get_token(user_id):
    return _TOKENS.get(user_id)

# AFTER ("improved"):
async def get_cached_token_with_validation(
    user_id: str,
    validate_expiry: bool = True,
    refresh_if_needed: bool = False
) -> Optional[TokenModel]:
    """
    Retrieves and optionally validates user token.
    
    Args:
        user_id: User identifier
        validate_expiry: Check if token is expired
        refresh_if_needed: Auto-refresh expired tokens
    
    Returns:
        Token object or None
    """
    # ... 50 more lines of "improvements"
```

**Problem:**
- Original function was 1 line, working perfectly
- "Improved" version is 50+ lines with new features not requested
- Breaks existing code that calls `get_token(user_id)`
- Not a bug fix, just unnecessary complexity

❌ Don't do this unless explicitly asked!

---

## ANTI-PATTERNS 🚫

### 1. The "While We're Here" Syndrome
```
❌ "I'm fixing flow.py, let me also reformat options.py and builder.py"
✅ Only fix flow.py, leave other files alone
```

### 2. The "Future-Proofing" Trap
```
❌ "Let me add error handling for edge cases that might happen"
✅ Fix the current error, don't anticipate future problems
```

### 3. The "Consistency" Excuse
```
❌ "File A uses async, so I'll rewrite File B to also use async"
✅ Only change async/sync if it fixes a bug or is explicitly requested
```

### 4. The "Dependency Creep"
```
❌ "I'll add this library, it makes the code cleaner"
✅ Use existing dependencies, propose new ones separately
```

---

## RESPONSE TEMPLATE 📋

When user asks for a fix, respond with:

```markdown
## Analysis
[Describe the problem in 1-2 sentences]

## Proposed Fix
[Describe the minimal change needed]

## Files to Modify
- `path/to/file.py` (lines X-Y)

## Verification Commands
```bash
[Commands to verify the fix works]
```

## Proceed?
[Wait for user confirmation before making changes]
```

---

## EMERGENCY ROLLBACK 🆘

If something breaks after your changes:

```bash
# 1. Identify what broke
tail -30 /tmp/backend_*.log

# 2. Restore from git
git checkout HEAD -- backend/app/routers/flow.py

# 3. Restart backend
pkill -9 uvicorn
uvicorn app.main:app --reload --port 8000

# 4. Verify health
curl http://localhost:8000/health
```

---

## SUCCESS METRICS 📊

### Good Session:
- ✅ 1-3 files modified
- ✅ 10-50 lines changed
- ✅ All tests pass
- ✅ Backend starts without errors
- ✅ Clear, focused git commit message

### Bad Session:
- ❌ 50+ files modified
- ❌ 1000+ lines changed
- ❌ New dependencies added
- ❌ Breaking changes without warning
- ❌ Vague commit message like "fixes" or "updates"

---

## FINAL REMINDER 🎯

**Your job is to FIX, not REFACTOR.**

When in doubt, ask:
1. Does this change fix a specific bug?
2. Was this change explicitly requested?
3. Could I do this with fewer lines?
4. Am I touching code outside the problem area?

If answer to #4 is YES → STOP and reconsider.

---

**Use this document at the start of EVERY session to prevent issues!**
