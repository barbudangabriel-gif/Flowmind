# ⚠️ CRITICAL WARNING - Unusual Whales API Hallucinations

**IMPORTANT:** Read this BEFORE using any Unusual Whales API endpoint!

---

## 🚨 The Problem

**AI assistants (including Claude, ChatGPT, Copilot) frequently generate FAKE Unusual Whales API endpoints that DO NOT EXIST.**

This has happened **multiple times** in FlowMind development, causing:
- Wasted hours debugging 404 errors
- Confusion about plan features
- Multiple rewrites of `unusual_whales_service.py`
- False assumptions about API capabilities

---

## 📋 History of Hallucinations

### October 21, 2025 - Latest Discovery
**Hallucinated by AI:**
```python
❌ /api/flow-alerts
❌ /api/market/tide  
❌ /api/stock/{ticker}/last-state
❌ /api/stock/{ticker}/ohlc
❌ /api/stock/{ticker}/quote
❌ /api/options-flow
❌ /api/market/overview
❌ /api/stock/{ticker}/gamma-exposure
```

**ALL returned 404 errors** despite AI confidently suggesting them.

**Even UW Support (Dan) provided endpoints that didn't work** - likely for different plan tiers or deprecated.

### Previous Incidents
- **Earlier 2025:** Used hallucinated `/api/options-flow` endpoint
- **Multiple rewrites:** `unusual_whales_service.py` has been rewritten 3+ times
- **Pattern:** AI sees other people's code using fake endpoints and propagates them

---

## ✅ VERIFIED Working Endpoints (Advanced Plan $375/month)

**ONLY these 5 endpoints are confirmed working (tested Oct 21, 2025):**

```python
# 1. Options Chain
GET https://api.unusualwhales.com/api/stock/{ticker}/option-contracts

# 2. Gamma Exposure  
GET https://api.unusualwhales.com/api/stock/{ticker}/spot-exposures

# 3. Stock Info
GET https://api.unusualwhales.com/api/stock/{ticker}/info

# 4. Market Alerts
GET https://api.unusualwhales.com/api/alerts

# 5. Greeks
GET https://api.unusualwhales.com/api/stock/{ticker}/greeks
```

**Authentication:** `Authorization: Bearer {token}` (NOT query param)

---

## 🛡️ How to Protect Yourself

### Rule 1: Never Trust AI-Generated Endpoints
**If an AI suggests a UW endpoint, TEST IT FIRST!**

```bash
# Quick test template:
curl -s "https://api.unusualwhales.com/api/{ENDPOINT}" \
  -H "Authorization: Bearer 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50" | jq .
```

**Expected responses:**
- ✅ `200 OK` with `{"data": [...]}` → Endpoint works
- ❌ `404 Not Found` with `"Something went wrong"` → Hallucination!

### Rule 2: Use the Clean Service
**Always use:** `backend/unusual_whales_service_clean.py`

This file contains ONLY verified endpoints with no hallucinations.

**Never blindly copy:** `backend/unusual_whales_service.py` (contains hallucinations from earlier)

### Rule 3: Check Documentation History
**Before implementing any UW endpoint, check:**
1. `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md` - Verified list
2. `test_uw_stock_endpoints.py` - Test script to verify
3. Official UW docs: https://api.unusualwhales.com/docs

### Rule 4: Document Your Discoveries
**When you find a working endpoint:**
1. Add it to `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md`
2. Create a test in `test_uw_stock_endpoints.py`
3. Update `.github/copilot-instructions.md`
4. Add example response in comments

---

## 🔍 How Hallucinations Happen

### 1. AI Training Data Contamination
AI models were trained on:
- GitHub repos with fake/outdated UW code
- Stack Overflow posts with wrong endpoints
- Blog posts using different plan tiers
- Old API versions (v1, v2, deprecated)

### 2. Logical Inference (Wrong)
AI sees:
- `/api/stock/{ticker}/info` exists
- So assumes `/api/stock/{ticker}/quote` must exist (WRONG!)

### 3. API Pattern Matching
AI pattern-matches from other APIs:
- Polygon.io has `/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}`
- So AI generates `/api/stock/{ticker}/snapshot` for UW (DOESN'T EXIST!)

### 4. Support Confusion
Even UW support provided endpoints that don't work:
- Dan's email listed `/api/flow-alerts` → 404
- Likely for Enterprise tier or deprecated
- **Lesson:** Always test, even official suggestions

---

## 📊 Statistics

**October 21, 2025 Discovery:**
- Endpoints tested: 30+
- AI-suggested endpoints: 25+
- Actually working: 5 (20% success rate)
- Time wasted on hallucinations: ~2 hours
- Time saved by verification: Countless future hours

---

## ✅ Verification Checklist

Before using ANY UW API endpoint in code:

- [ ] Tested with `curl` command
- [ ] Got 200 OK response (not 404)
- [ ] Verified data structure matches expectations
- [ ] Tested with multiple tickers (TSLA, SPY, AAPL)
- [ ] Added to verified endpoints list
- [ ] Created test case in `test_uw_stock_endpoints.py`
- [ ] Documented in `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md`
- [ ] Updated `.github/copilot-instructions.md`

---

## 🚀 Quick Test Script

```bash
#!/bin/bash
# Test if a UW endpoint works

ENDPOINT="$1"  # e.g., "/stock/TSLA/info"
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"

echo "Testing: https://api.unusualwhales.com/api${ENDPOINT}"
curl -s "https://api.unusualwhales.com/api${ENDPOINT}" \
  -H "Authorization: Bearer ${TOKEN}" | jq .

# Usage:
# ./test_uw_endpoint.sh "/stock/TSLA/info"
```

Save as `test_uw_endpoint.sh` and run before implementing any endpoint.

---

## 📚 Resources

**Verified Documentation:**
- `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md` - Complete reference
- `UW_API_QUICK_REF.md` - Quick lookup
- `backend/unusual_whales_service_clean.py` - Clean implementation
- `test_uw_stock_endpoints.py` - Verification tests

**Official (but verify!):**
- https://api.unusualwhales.com/docs
- https://unusualwhales.com/api-dashboard

**Support:**
- Email: support@unusualwhales.com
- Mention: "Advanced plan, checking endpoint availability"

---

## 🎯 Summary

**DO:**
- ✅ Use only verified endpoints from `unusual_whales_service_clean.py`
- ✅ Test every new endpoint with curl first
- ✅ Document your findings
- ✅ Check plan tier compatibility

**DON'T:**
- ❌ Trust AI-generated endpoint suggestions
- ❌ Assume endpoint exists because it "makes sense"
- ❌ Copy code from Stack Overflow without testing
- ❌ Implement endpoints without verification

---

**Remember:** If it's not in `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md`, it probably doesn't work! 🚨

---

**Last Updated:** October 21, 2025  
**Verified By:** Systematic testing of 30+ endpoint variations  
**Casualties:** Multiple hours debugging hallucinated endpoints  
**Lesson:** Test first, implement second! 🧪
