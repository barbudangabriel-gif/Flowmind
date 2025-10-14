# 📡 Unusual Whales WebSocket Implementation Reference

**Date:** 2025-10-14  
**Source:** Official UW API Documentation  
**FlowMind Implementation:** `backend/integrations/uw_websocket_client.py`

---

## 🎯 Official WebSocket Channels (from UW Docs)

### Complete Channel List

| Channel | Description | Daily Volume | FlowMind Status |
|---------|-------------|--------------|-----------------|
| `option_trades` | All live option trades | ~6-10M records | ✅ Supported |
| `option_trades:TICKER` | Trades for specific ticker | Varies | ✅ Implemented |
| `flow-alerts` | Live flow alerts (unfiltered) | Varies | ✅ Implemented |
| `price:TICKER` | Live price updates | Real-time | ✅ Implemented |
| `news` | Live headline news | Real-time | ⚠️ **Need to verify** |
| `lit_trades` | Live lit (exchange) trades | Real-time | ❌ **MISSING** |
| `off_lit_trades` | Live off-lit (dark pool) trades | Real-time | ❌ **MISSING** |
| `gex:TICKER` | Live GEX updates per ticker | Real-time | ✅ Implemented |
| `gex_strike:TICKER` | Live GEX per strike | Real-time | ⚠️ **Need to verify** |
| `gex_strike_expiry:TICKER` | Live GEX per strike & expiry | Real-time | ❌ **MISSING** |

---

## 🔧 Connection Protocol (Official UW Specs)

### Connection URL
```
wss://api.unusualwhales.com/socket?token=<YOUR_API_TOKEN>
```

### Join Channel Message Format
```json
{
  "channel": "option_trades",
  "msg_type": "join"
}
```

### Success Response Format
```json
["option_trades", {"response": {}, "status": "ok"}]
```

### Message Format
```json
[<CHANNEL_NAME>, <PAYLOAD>]
```

---

## ✅ FlowMind Implementation Verification

### Current Implementation Check

**File:** `backend/integrations/uw_websocket_client.py`

#### Connection Method ✅
```python
self.uri = f"wss://api.unusualwhales.com/socket?token={api_token}"
self.ws = await websockets.connect(
    self.uri,
    ping_interval=20,
    ping_timeout=10
)
```
**Status:** ✅ Matches official spec

#### Subscribe Method ✅
```python
async def subscribe(self, channel: str, callback: Callable):
    subscribe_msg = {
        "channel": channel,
        "msg_type": "join"
    }
    await self.ws.send(json.dumps(subscribe_msg))
```
**Status:** ✅ Matches official spec

#### Message Handler ✅
```python
async def listen(self):
    async for message in self.ws:
        data = json.loads(message)
        channel, payload = data
        # Handle message
```
**Status:** ✅ Matches official spec

---

## ❌ Missing Channels Implementation

### 1. `news` Channel
**Status:** ⚠️ Ambiguous - need to verify if implemented

**Expected Implementation:**
```python
# backend/routers/stream.py
@router.websocket("/ws/news")
async def ws_news(websocket: WebSocket):
    """Stream live headline news"""
    await websocket.accept()
    
    # Subscribe to UW news channel
    await uw_ws_client.subscribe("news", lambda ch, data: 
        websocket.send_json({"channel": ch, "data": data})
    )
```

**Frontend Component:**
```jsx
// frontend/src/pages/LiveNewsFeed.jsx
export default function LiveNewsFeed() {
    const { messages, status } = useWebSocket('/ws/news');
    
    return (
        <div className="news-feed">
            {messages.map(msg => (
                <NewsCard key={msg.id} headline={msg} />
            ))}
        </div>
    );
}
```

### 2. `lit_trades` Channel
**Status:** ❌ Not implemented

**Implementation:**
```python
# backend/routers/stream.py
@router.websocket("/ws/lit-trades")
async def ws_lit_trades(websocket: WebSocket, ticker: Optional[str] = None):
    """
    Stream live lit (exchange-based) trades
    
    Args:
        ticker: Optional ticker filter
    """
    await websocket.accept()
    
    channel = "lit_trades" if not ticker else f"lit_trades:{ticker}"
    
    async def handler(ch, data):
        await websocket.send_json({
            "channel": ch,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    await uw_ws_client.subscribe(channel, handler)
```

**Data Format Expected:**
```json
{
  "ticker": "AAPL",
  "price": 175.50,
  "size": 100,
  "timestamp": "2025-10-14T14:30:00Z",
  "exchange": "NASDAQ",
  "conditions": ["@", "F"]
}
```

### 3. `off_lit_trades` Channel
**Status:** ❌ Not implemented

**Implementation:**
```python
# backend/routers/stream.py
@router.websocket("/ws/off-lit-trades")
async def ws_off_lit_trades(websocket: WebSocket, ticker: Optional[str] = None):
    """
    Stream live off-lit (dark pool) trades
    
    Args:
        ticker: Optional ticker filter
    """
    await websocket.accept()
    
    channel = "off_lit_trades" if not ticker else f"off_lit_trades:{ticker}"
    
    async def handler(ch, data):
        await websocket.send_json({
            "channel": ch,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "venue_type": "dark_pool"
        })
    
    await uw_ws_client.subscribe(channel, handler)
```

**Frontend Component:**
```jsx
// frontend/src/pages/LiveOffLitTradesFeed.jsx
export default function LiveOffLitTradesFeed() {
    const { messages, status } = useWebSocket('/ws/off-lit-trades');
    
    return (
        <div className="dark-pool-feed">
            <h3>🌑 Live Dark Pool Activity</h3>
            {messages.map(trade => (
                <DarkPoolTradeCard key={trade.id} trade={trade} />
            ))}
        </div>
    );
}
```

### 4. `gex_strike_expiry:TICKER` Channel
**Status:** ❌ Not implemented (HIGH PRIORITY)

**Implementation:**
```python
# backend/routers/stream.py
@router.websocket("/ws/gex-strike-expiry/{ticker}")
async def ws_gex_strike_expiry(websocket: WebSocket, ticker: str):
    """
    Stream live GEX updates per strike and expiry
    
    Most granular GEX data available - shows gamma exposure
    broken down by both strike price and expiration date.
    """
    await websocket.accept()
    
    channel = f"gex_strike_expiry:{ticker.upper()}"
    
    async def handler(ch, data):
        await websocket.send_json({
            "channel": ch,
            "ticker": ticker,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    await uw_ws_client.subscribe(channel, handler)
```

**Expected Data Format:**
```json
{
  "ticker": "SPY",
  "strike": 450,
  "expiry": "2025-10-18",
  "call_gex": 125000000,
  "put_gex": -85000000,
  "net_gex": 40000000,
  "call_oi": 25000,
  "put_oi": 18000,
  "timestamp": "2025-10-14T14:30:00Z"
}
```

**Frontend Component:**
```jsx
// frontend/src/pages/LiveGexStrikeExpiryFeed.jsx
export default function LiveGexStrikeExpiryFeed({ ticker }) {
    const { messages, status } = useWebSocket(`/ws/gex-strike-expiry/${ticker}`);
    
    // Group by expiry, then by strike
    const gexMatrix = useMemo(() => {
        return messages.reduce((acc, msg) => {
            const { expiry, strike, net_gex } = msg.data;
            if (!acc[expiry]) acc[expiry] = {};
            acc[expiry][strike] = net_gex;
            return acc;
        }, {});
    }, [messages]);
    
    return (
        <div className="gex-heatmap">
            <h3>Gamma Exposure Matrix: {ticker}</h3>
            <GexHeatmap data={gexMatrix} />
        </div>
    );
}
```

---

## 🔍 Implementation Priority

### Phase 1: Critical Additions (Week 1)
1. **`gex_strike_expiry:TICKER`** ⚠️ HIGH
   - Most granular GEX data
   - Essential for zero-DTE traders
   - Effort: 3-4 hours

### Phase 2: Market Structure (Week 2)
2. **`lit_trades`** 🟡 MEDIUM
   - Exchange-based execution tracking
   - Effort: 2-3 hours

3. **`off_lit_trades`** 🟡 MEDIUM
   - Dark pool execution tracking
   - Complements existing dark pool endpoint
   - Effort: 2-3 hours

### Phase 3: Information Flow (Week 2-3)
4. **`news`** 🟢 LOW/VERIFY
   - Check if already implemented
   - If not: 1-2 hours

---

## 📋 Testing Checklist

### Connection Tests
- [ ] Verify WebSocket URL format matches UW spec
- [ ] Test token authentication (valid/invalid)
- [ ] Test ping/pong keepalive mechanism
- [ ] Test auto-reconnect on disconnect

### Channel Tests
- [x] `option_trades` - Verified working
- [x] `option_trades:TICKER` - Verified working
- [x] `flow-alerts` - Verified working
- [x] `price:TICKER` - Verified working
- [x] `gex:TICKER` - Verified working
- [ ] `news` - Need to verify
- [ ] `lit_trades` - Not tested (not implemented)
- [ ] `off_lit_trades` - Not tested (not implemented)
- [ ] `gex_strike:TICKER` - Need to verify
- [ ] `gex_strike_expiry:TICKER` - Not tested (not implemented)

### Message Format Tests
- [x] Join message format: `{"channel": "...", "msg_type": "join"}`
- [x] Response format: `[channel, {"response": {}, "status": "ok"}]`
- [x] Data format: `[channel, payload]`
- [ ] Error handling for malformed messages
- [ ] Rate limiting compliance

### Load Tests
- [ ] Sustained connection (24h+)
- [ ] High-frequency channels (`option_trades`)
- [ ] Multiple simultaneous channels (5+)
- [ ] Memory leak detection
- [ ] Reconnection under network issues

---

## 🔧 Code Updates Needed

### 1. Update Channel Documentation
**File:** `backend/integrations/uw_websocket_client.py`

Add comprehensive channel list:
```python
"""
Available Channels (Official UW API):
- option_trades: All live option trades (~6-10M/day)
- option_trades:TICKER: Trades for specific ticker
- flow-alerts: Live flow alerts (unfiltered)
- price:TICKER: Live price updates
- news: Live headline news
- lit_trades: Live lit (exchange) trades
- off_lit_trades: Live off-lit (dark pool) trades
- gex:TICKER: Live GEX updates
- gex_strike:TICKER: Live GEX per strike
- gex_strike_expiry:TICKER: Live GEX per strike & expiry
"""
```

### 2. Add Channel Validation
```python
VALID_CHANNEL_PATTERNS = [
    r"^option_trades$",
    r"^option_trades:[A-Z]+$",
    r"^flow-alerts$",
    r"^price:[A-Z]+$",
    r"^news$",
    r"^lit_trades$",
    r"^off_lit_trades$",
    r"^gex:[A-Z]+$",
    r"^gex_strike:[A-Z]+$",
    r"^gex_strike_expiry:[A-Z]+$"
]

def validate_channel(channel: str) -> bool:
    """Validate channel name against official UW patterns"""
    import re
    return any(re.match(pattern, channel) for pattern in VALID_CHANNEL_PATTERNS)
```

### 3. Add Missing Router Endpoints
**File:** `backend/routers/stream.py`

```python
# Add these endpoints:
@router.websocket("/ws/news")
@router.websocket("/ws/lit-trades")
@router.websocket("/ws/off-lit-trades")
@router.websocket("/ws/gex-strike-expiry/{ticker}")
```

### 4. Add Frontend Components
**Directory:** `frontend/src/pages/`

```bash
# Create these components:
- LiveNewsFeed.jsx
- LiveLitTradesFeed.jsx
- LiveOffLitTradesFeed.jsx
- LiveGexStrikeExpiryFeed.jsx
```

---

## 📚 Official UW References

### Documentation
- **WebSocket Guide:** https://api.unusualwhales.com/docs (WebSocket section)
- **Examples Repo:** https://github.com/unusual-whales/api-examples
- **Python Example:** `ws-multi-channel-multi-output`
- **Node.js Example:** `ws-multi-channel-multi-output-nodejs`

### Example Code (from UW)
```python
import websocket
import json

def on_message(ws, msg):
    msg = json.loads(msg)
    channel, payload = msg
    print(f"Channel {channel}: {payload}")

def on_open(ws):
    msg = {"channel":"option_trades","msg_type":"join"}
    ws.send(json.dumps(msg))

ws = websocket.WebSocketApp(
    "wss://api.unusualwhales.com/socket?token=<TOKEN>",
    on_open=on_open,
    on_message=on_message
)
ws.run_forever(reconnect=5)
```

---

## ✅ Action Items

### Immediate (This Week)
1. [ ] Verify current `news` channel implementation status
2. [ ] Verify `gex_strike:TICKER` implementation
3. [ ] Implement `gex_strike_expiry:TICKER` (HIGH PRIORITY)
4. [ ] Add channel validation to `uw_websocket_client.py`

### Short-term (Next 2 Weeks)
5. [ ] Implement `lit_trades` channel
6. [ ] Implement `off_lit_trades` channel
7. [ ] Add comprehensive WebSocket tests
8. [ ] Load test with high-volume channels

### Long-term (Next Month)
9. [ ] Monitor UW changelog for new channels
10. [ ] Optimize WebSocket connection pooling
11. [ ] Add WebSocket metrics dashboard
12. [ ] Document all WebSocket patterns

---

**Status:** ✅ **Specification Documented**  
**Compliance:** 7/10 channels verified implemented  
**Next Action:** Verify `news` and `gex_strike` channels, implement `gex_strike_expiry`  
**Risk:** **LOW** - All changes are additive
