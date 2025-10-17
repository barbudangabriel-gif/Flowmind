# Manual Testing Guide - Lit Trades & Dark Pool

**Quick Reference for Live Testing**

---

## Quick Start (5 Minutes)

### Step 1: Open FlowMind
```
URL: http://localhost:3000
```

### Step 2: Navigate to Flow Page
```
Click: Flow (in navigation)
OR
Direct URL: http://localhost:3000/flow
```

### Step 3: Test Lit Trades Tab
```
1. Click: " Lit Trades" tab
2. Wait 2-3 seconds for connection
3. Observe: Real-time trades appearing
```

### Step 4: Test Dark Pool Tab
```
1. Click: "🕶️ Dark Pool" tab
2. Wait 2-3 seconds for connection
3. Observe: Dark pool trades appearing
```

---

## What to Look For

### Lit Trades Feed ()
**Good Signs:**
- Trades appear in real-time
- Exchange names visible (NASDAQ, NYSE, ARCA)
- Stats panel shows: Total Trades, Volume, Value
- Exchange distribution chart updates
- Tape classification shows (A/B/C)

**Warning Signs:**
- "Connecting..." message persists > 5s
- No trades appear after 10s
- Console errors in DevTools

**Critical Issues:**
- Component doesn't render
- "WebSocket connection failed" error
- Blank page or React error

### Dark Pool Feed (🕶️)
**Good Signs:**
- Trades appear in real-time
- Venue names visible (UBS ATS, MS Pool, Citadel)
- Block trades highlighted (💎 indicator)
- Size categories shown (MEGA/HUGE/BLOCK/LARGE)
- Stats panel shows: Total Trades, Volume, Notional

**Warning Signs:**
- "Connecting..." message persists > 5s
- No trades appear after 15s (dark pool trades are less frequent)
- Console warnings

**Critical Issues:**
- Component doesn't render
- "WebSocket connection failed" error
- Blank page or React error

---

## Browser DevTools Check

### Open DevTools
```
Press: F12 (or Ctrl+Shift+I / Cmd+Opt+I)
```

### Check Console Tab
**Expected:**
```
 No red errors
 May see blue info logs
 WebSocket connection messages OK
```

**Investigate if you see:**
```
 Red errors
 CORS errors
 Failed to fetch errors
 WebSocket connection refused
```

### Check Network Tab → WS Filter
**Expected:**
```
 ws://localhost:8000/ws/lit-trades/SPY
 Status: 101 Switching Protocols
 Type: websocket
 
 ws://localhost:8000/ws/off-lit-trades/SPY
 Status: 101 Switching Protocols
 Type: websocket
```

**Investigate if you see:**
```
 Status: 403 Forbidden
 Status: 500 Internal Server Error
 Connection attempts but failures
```

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Flow page with all tabs visible
2. Lit Trades tab active with data
3. Dark Pool tab active with data
4. DevTools showing WebSocket connections
5. Stats panels with metrics

Save to: `/workspaces/Flowmind/screenshots/`

---

## 🎬 Video Recording (Optional)

Record:
1. Tab navigation (Summary → Lit Trades → Dark Pool)
2. Real-time data streaming (30 seconds)
3. Stats panel updates

Use: Browser screen recorder or external tool

---

## 🐛 Troubleshooting

### Issue: Frontend won't load
**Fix:**
```bash
cd /workspaces/Flowmind/frontend
npm install
npm start
```

### Issue: Backend not responding
**Fix:**
```bash
cd /workspaces/Flowmind/backend
python -m uvicorn server:app --reload --port 8000
```

### Issue: WebSocket 403 errors
**Check:**
- Backend CORS settings allow localhost:3000
- Using correct WebSocket URL (ws:// not wss://)
- Origin header present

### Issue: No data appearing
**Possible Causes:**
1. UW API token not configured (demo mode active)
2. Market closed (after hours)
3. Backend not connected to UW WebSocket
4. Network issues

**Check Backend Logs:**
```bash
# Look for:
INFO:routers.stream: Connected to Unusual Whales WebSocket
INFO:integrations.uw_websocket_client: WebSocket connected
```

---

## Quick Validation Checklist

```
□ Backend running (port 8000)
□ Frontend compiled (port 3000)
□ Flow page loads
□ All tabs visible
□ Lit Trades tab works
□ 🕶️ Dark Pool tab works
□ WebSocket connections active
□ No console errors
□ Data streaming in real-time
```

---

## Test Results Template

```
Date: October 14, 2025
Time: [HH:MM]
Tester: Gabriel Barbudan

Backend Status: / / 
Frontend Status: / / 

Lit Trades Test:
- Component renders: / 
- WebSocket connects: / 
- Data displays: / 
- Stats accurate: / 
Notes: _______________________

Dark Pool Test:
- Component renders: / 
- WebSocket connects: / 
- Data displays: / 
- Stats accurate: / 
Notes: _______________________

Overall Result: PASS / FAIL / PARTIAL
```

---

## Success Criteria

**PASS:**
- All components render
- WebSocket connections established
- Real-time data streaming
- No critical errors

**PARTIAL:**
- Components render but data delayed
- Minor console warnings
- Some features not working

**FAIL:**
- Components don't render
- WebSocket connections fail
- Critical errors in console

---

*Manual Testing Guide* 
*Created: October 14, 2025* 
*For: FlowMind Lit Trades & Dark Pool Integration*
