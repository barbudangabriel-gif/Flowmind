# Quick Start Guide - Testing Lit Trades & Dark Pool Feeds

**Purpose:** Test the newly integrated Lit Trades and Dark Pool real-time feeds 
**Date:** October 14, 2025 
**Prerequisites:** Backend running on port 8000, Frontend running on port 3000

---

## Quick Test (5 minutes)

### 1. Start Backend
```bash
cd /workspaces/Flowmind/backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd /workspaces/Flowmind/frontend
npm start
```

### 3. Test Navigation

#### A. Access Lit Trades Feed
1. Open browser: `http://localhost:3000/flow`
2. Click **" Lit Trades"** tab
3. Verify URL changes to `/flow/lit-trades`
4. Confirm component loads with SPY ticker

**Expected Behavior:**
- Feed connects via WebSocket to `ws://localhost:8000/ws/lit-trades/SPY`
- Real-time trades display with exchange information
- Stats panel shows: Total Trades, Total Volume, Total Value
- Exchange distribution chart displays
- Tape classification (A/B/C) visible

#### B. Access Dark Pool Feed
1. On Flow page, click **"🕶️ Dark Pool"** tab
2. Verify URL changes to `/flow/dark-pool`
3. Confirm component loads with SPY ticker

**Expected Behavior:**
- Feed connects via WebSocket to `ws://localhost:8000/ws/off-lit-trades/SPY`
- Dark pool trades display with venue information
- Block trades (10K+ shares) highlighted
- Size categories (MEGA/HUGE/BLOCK/LARGE) shown
- Venue distribution stats visible

---

## Detailed Verification

### Backend Health Check
```bash
# Check WebSocket endpoints exist
curl http://localhost:8000/health

# Verify endpoints in documentation
curl http://localhost:8000/docs
```

Look for:
- `/ws/lit-trades/{ticker}` - Lit Trades WebSocket
- `/ws/off-lit-trades/{ticker}` - Dark Pool WebSocket

### Frontend Component Check
```bash
cd /workspaces/Flowmind/frontend/src/pages

# Verify component files exist
ls -lh LiveLitTradesFeed.jsx
ls -lh LiveOffLitTradesFeed.jsx
```

Expected:
- `LiveLitTradesFeed.jsx` - ~280 lines
- `LiveOffLitTradesFeed.jsx` - ~320 lines

### Browser DevTools Test

#### 1. Open DevTools (F12)

#### 2. Network Tab
- Filter: `WS` (WebSocket)
- Navigate to `/flow/lit-trades`
- Look for WebSocket connection to `ws://localhost:8000/ws/lit-trades/SPY`
- Status should be: **101 Switching Protocols**

#### 3. Console Tab
Look for logs:
```
[LiveLitTradesFeed] Connecting to WebSocket: ws://localhost:8000/ws/lit-trades/SPY
[WebSocket] Connected
[LiveLitTradesFeed] Received trade: {...}
```

#### 4. React DevTools
- Locate `LiveLitTradesFeed` component
- Check props: `ticker: "SPY"`
- Check state: `trades: [...]`, `stats: {...}`, `connected: true`

---

## 🧪 Test Scenarios

### Scenario 1: Tab Navigation
**Steps:**
1. Navigate to `/flow`
2. Click each tab: Summary → Live → Hist → Lit Trades → Dark Pool → News
3. Verify each tab highlights correctly
4. Verify URL updates for each tab
5. Use browser back/forward buttons

**Expected:** Smooth navigation, correct URL changes, no errors

### Scenario 2: Direct URL Access
**Steps:**
1. Open `http://localhost:3000/flow/lit-trades` directly
2. Verify component loads
3. Open `http://localhost:3000/flow/dark-pool` directly
4. Verify component loads

**Expected:** Components render without requiring tab click

### Scenario 3: WebSocket Reconnection
**Steps:**
1. Open Lit Trades feed
2. Stop backend server
3. Observe disconnection indicator
4. Restart backend server
5. Observe automatic reconnection

**Expected:** Graceful degradation, automatic recovery

### Scenario 4: Multiple Tabs
**Steps:**
1. Open Lit Trades in one browser tab
2. Open Dark Pool in another browser tab
3. Verify both feeds work simultaneously

**Expected:** Independent WebSocket connections, no conflicts

### Scenario 5: Data Validation
**Steps:**
1. Open Lit Trades feed
2. Observe incoming trades
3. Verify fields present:
 - Timestamp
 - Exchange (NASDAQ, NYSE, ARCA, etc.)
 - Price
 - Size
 - Tape (A/B/C)
 - Condition codes

**Expected:** All fields populated, data makes sense

---

## 🐛 Troubleshooting

### Issue: Tab not rendering
**Symptoms:** Blank page or "Loading..." forever 
**Check:**
1. Browser console for errors
2. Component import in FlowPage.jsx
3. Route registered in App.js
4. Backend server running

**Fix:**
```bash
cd /workspaces/Flowmind/frontend
npm install
npm start
```

### Issue: WebSocket not connecting
**Symptoms:** "Connecting..." message persists 
**Check:**
1. Backend logs for WebSocket endpoint
2. Network tab for connection attempt
3. CORS configuration
4. Backend port (should be 8000)

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Restart backend
cd /workspaces/Flowmind/backend
python -m uvicorn app.main:app --reload --port 8000
```

### Issue: No data appearing
**Symptoms:** Connected but no trades shown 
**Check:**
1. UW API token configured in backend/.env
2. Ticker is valid (default: SPY)
3. Market hours (9:30 AM - 4:00 PM EST)
4. Backend logs for UW API errors

**Fix:**
```bash
# Check backend environment
cd /workspaces/Flowmind/backend
cat .env | grep UW_API_TOKEN

# Test UW API connection manually
# (Check backend logs for detailed errors)
```

### Issue: Build errors
**Symptoms:** Frontend won't compile 
**Check:**
1. Missing imports
2. Syntax errors in new components
3. Missing dependencies

**Fix:**
```bash
cd /workspaces/Flowmind/frontend
npm run lint
npm run build
```

---

## Verification Checklist

### Backend 
- [ ] Server running on port 8000
- [ ] `/health` endpoint returns 200
- [ ] WebSocket endpoints visible in `/docs`
- [ ] UW API token configured
- [ ] No errors in backend logs

### Frontend 
- [ ] Dev server running on port 3000
- [ ] No compilation errors
- [ ] Components render without errors
- [ ] No console errors in browser
- [ ] WebSocket connections established

### Navigation 
- [ ] Tab buttons visible and clickable
- [ ] Active tab highlights correctly
- [ ] URL changes on tab click
- [ ] Direct URL access works
- [ ] Browser back/forward functional

### Data Flow 
- [ ] Lit Trades feed shows data
- [ ] Dark Pool feed shows data
- [ ] Exchange information visible
- [ ] Venue information visible
- [ ] Stats panels update
- [ ] Real-time updates work

### UX 
- [ ] Emoji indicators display ( 🕶️)
- [ ] Loading states show correctly
- [ ] Error states handled gracefully
- [ ] Reconnection works automatically
- [ ] Performance is smooth

---

## Success Criteria

**Test PASSES if:**
1. Both tabs accessible from FlowPage
2. Components render without errors
3. WebSocket connections establish successfully
4. Real-time data displays correctly
5. Navigation works smoothly
6. No console errors
7. Performance is acceptable
8. Mobile responsive (bonus)

**Test FAILS if:**
1. Components don't render
2. WebSocket connections fail
3. Navigation broken
4. Console errors present
5. Data doesn't update
6. Performance issues
7. Styling broken

---

## 📸 Expected Screenshots

### Lit Trades Feed
```
┌─────────────────────────────────────────────────────┐
│ Options Flow > Lit Trades (SPY) │
├─────────────────────────────────────────────────────┤
│ Stats: Total: 1,234 Volume: 145K Value: $36.2M │
├─────────────────────────────────────────────────────┤
│ Exchange Distribution: │
│ ████████ NASDAQ (45%) │
│ ██████ NYSE (30%) │
│ ████ ARCA (15%) │
├─────────────────────────────────────────────────────┤
│ Recent Trades: │
│ 14:32:15 NASDAQ $422.50 500 Tape C @ │
│ 14:32:14 NYSE $422.48 250 Tape C @ │
│ 14:32:13 ARCA $422.52 100 Tape C @ │
└─────────────────────────────────────────────────────┘
```

### Dark Pool Feed
```
┌─────────────────────────────────────────────────────┐
│ Options Flow > 🕶️ Dark Pool (SPY) │
├─────────────────────────────────────────────────────┤
│ Stats: Total: 456 Volume: 2.3M Notional: $972M │
├─────────────────────────────────────────────────────┤
│ Venue Distribution: │
│ ████████ UBS ATS (35%) │
│ ██████ MS Pool (25%) │
│ ████ Citadel (20%) │
├─────────────────────────────────────────────────────┤
│ Recent Trades: │
│ 14:32:15 UBS ATS $422.50 25,000 BLOCK 💎 │
│ 14:32:12 MS Pool $422.48 50,000 HUGE │
│ 14:32:10 Citadel $422.52 15,000 BLOCK 💎 │
└─────────────────────────────────────────────────────┘
```

---

## 🔗 Related Documentation

- **Implementation:** `100_PERCENT_COMPLIANCE_ACHIEVEMENT.md`
- **Backend:** `UW_WEBSOCKET_SPECIFICATION.md`
- **Components:** `LiveLitTradesFeed.jsx`, `LiveOffLitTradesFeed.jsx`
- **Integration:** `UI_INTEGRATION_COMPLETE.md`
- **API Status:** `UW_CONNECTION_STATUS.md`

---

## Pro Tips

1. **Testing with Real Data:** Connect during market hours (9:30 AM - 4:00 PM EST) for best results
2. **Testing After Hours:** Backend will use demo/simulated data automatically
3. **Multiple Tickers:** Modify component prop to test different tickers (e.g., `ticker="AAPL"`)
4. **Performance:** Monitor WebSocket message frequency in DevTools
5. **Debugging:** Enable verbose logging in browser console: `localStorage.setItem('debug', 'flowmind:*')`

---

## Test Complete

After completing all tests, you should have:
- Verified both feeds work correctly
- Confirmed navigation is functional
- Validated real-time data updates
- Documented any issues found
- Captured screenshots (optional)

**Next:** Ready for production deployment! 

---

*Test Guide Version: 1.0* 
*Last Updated: October 14, 2025* 
*Author: Gabriel Barbudan*
