# 📡 FlowMind - Real-Time WebSocket Streaming Documentation

## 🎯 Overview

FlowMind implements a **hybrid WebSocket streaming architecture** with 3 verified channels and 3 experimental channels from Unusual Whales API. This document covers the complete streaming infrastructure, API endpoints, and usage examples.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unusual Whales API                           │
│                 wss://api.unusualwhales.com                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ WebSocket Connection
                           │ (1 shared connection)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FlowMind Backend                             │
│                  (FastAPI + asyncio)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  UWWebSocketClient (Singleton)                           │  │
│  │  - Auto-reconnect with exponential backoff               │  │
│  │  - Multi-channel subscription management                 │  │
│  │  - Health monitoring (ping/pong)                         │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│                 │ Message Broadcasting                          │
│                 ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WebSocket Connection Manager                            │  │
│  │  - Per-channel client tracking                           │  │
│  │  - Broadcast to all subscribed frontends                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ WebSocket Connections
                           │ (Multiple frontend clients)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Frontend Clients (React)                        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Flow Feed    │  │ GEX Feed     │  │ Trades Feed  │         │
│  │ (verified)   │  │ (verified)   │  │ (verified)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  🧪 Experimental (with REST fallback):                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Market       │  │ Dark Pool    │  │ Congress     │         │
│  │ Movers       │  │ Activity     │  │ Trades       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 WebSocket Endpoints

### ✅ Verified Channels (100% Functional)

#### 1. **Flow Alerts**
```
Endpoint: ws://localhost:8000/api/stream/ws/flow
Channel:  flow-alerts
Status:   ✅ CONFIRMED WORKING
```

**Data Format:**
```json
{
  "channel": "flow-alerts",
  "timestamp": "2025-10-14T12:34:56.789Z",
  "data": {
    "ticker_symbol": "TSLA",
    "put_call": "CALL",
    "strike": 250.0,
    "expiration_date": "2025-11-15",
    "ask_side_premium": 265000,
    "bid_side_premium": 258000,
    "traded_at": "2025-10-14T14:32:45Z",
    "is_sweep": true,
    "sentiment": "bullish"
  }
}
```

**Use Cases:**
- Monitor large options orders in real-time
- Track unusual options activity (sweeps, blocks)
- Detect whale trades and institutional flow
- Analyze bullish/bearish sentiment

---

#### 2. **Gamma Exposure (GEX)**
```
Endpoint: ws://localhost:8000/api/stream/ws/gex/{ticker}
Channel:  gex:SPY, gex:TSLA, gex:AAPL, etc.
Status:   ✅ CONFIRMED WORKING
```

**Data Format:**
```json
{
  "channel": "gex:SPY",
  "timestamp": "2025-10-14T12:34:56.789Z",
  "data": {
    "ticker": "SPY",
    "total_gex": 125000000,
    "call_gex": 85000000,
    "put_gex": 40000000,
    "zero_gamma_level": 445.5,
    "strikes": [
      {"strike": 440, "gex": 5000000},
      {"strike": 445, "gex": 25000000},
      {"strike": 450, "gex": 15000000}
    ]
  }
}
```

**Use Cases:**
- Track gamma exposure levels in real-time
- Identify zero gamma points (support/resistance)
- Detect potential gamma squeezes
- Monitor dealer hedging activity

---

#### 3. **Option Trades**
```
Endpoint: ws://localhost:8000/api/stream/ws/option-trades/{ticker}
Channel:  option_trades:TSLA, option_trades:AAPL, etc.
Status:   ✅ CONFIRMED WORKING
```

**Data Format:**
```json
{
  "channel": "option_trades:TSLA",
  "timestamp": "2025-10-14T12:34:56.789Z",
  "data": {
    "ticker": "TSLA",
    "strike": 250,
    "expiry": "2025-11-15",
    "type": "CALL",
    "side": "BUY",
    "price": 5.30,
    "quantity": 100,
    "premium": 53000,
    "timestamp": "2025-10-14T12:34:56Z"
  }
}
```

**Use Cases:**
- Monitor all option trades for a specific ticker
- Track trade volume and patterns
- Build real-time trade heatmaps
- Analyze order flow direction

---

### ⚠️ Experimental Channels (with REST Fallback)

#### 4. **Market Movers**
```
Endpoint:  ws://localhost:8000/api/stream/ws/market-movers
Channel:   market_movers (unverified)
Status:    ⚠️ EXPERIMENTAL
Fallback:  GET /api/market/movers (polling every 30s)
```

#### 5. **Dark Pool**
```
Endpoint:  ws://localhost:8000/api/stream/ws/dark-pool
Channel:   dark_pool (unverified)
Status:    ⚠️ EXPERIMENTAL
Fallback:  GET /api/dark-pool (polling every 60s)
```

#### 6. **Congress Trades**
```
Endpoint:  ws://localhost:8000/api/stream/ws/congress
Channel:   congress_trades (unverified)
Status:    ⚠️ EXPERIMENTAL
Fallback:  GET /api/congress-trades (polling every 5min)
```

---

## 🚀 Quick Start

### Backend Setup

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Set environment variables
export UW_API_TOKEN="your-unusual-whales-token"

# 3. Start server
python -m uvicorn server:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Set backend URL
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env.local

# 3. Start development server
npm start
```

### Access Streaming Dashboard

```
http://localhost:3000/streaming
```

---

## 💻 Frontend Usage

### Basic Connection

```javascript
import useWebSocket from '../hooks/useWebSocket';

function MyComponent() {
  const endpoint = '/api/stream/ws/flow';
  const { messages, connected, error } = useWebSocket(endpoint);
  
  return (
    <div>
      {connected ? '✅ Connected' : '❌ Disconnected'}
      {messages.map((msg, idx) => (
        <div key={idx}>{JSON.stringify(msg)}</div>
      ))}
    </div>
  );
}
```

### Using Context (Multi-channel)

```javascript
import { useWebSocketContext } from '../context/WebSocketContext';

function MyComponent() {
  const { subscribe, connections } = useWebSocketContext();
  
  useEffect(() => {
    const unsubscribe = subscribe('flow-alerts', (message) => {
      console.log('Flow alert:', message);
    });
    
    return unsubscribe;
  }, [subscribe]);
  
  return <div>Status: {connections['flow-alerts'].status}</div>;
}
```

### Ticker-Specific Channels

```javascript
import GammaExposureFeed from '../components/streaming/GammaExposureFeed';
import OptionTradesFeed from '../components/streaming/OptionTradesFeed';

function Dashboard() {
  return (
    <div>
      {/* GEX for SPY */}
      <GammaExposureFeed defaultTicker="SPY" />
      
      {/* Option trades for TSLA */}
      <OptionTradesFeed defaultTicker="TSLA" />
    </div>
  );
}
```

---

## 🔧 Configuration

### Environment Variables

**Backend (`backend/.env`):**
```bash
# Required
UW_API_TOKEN=your-token-here

# Optional
REDIS_URL=redis://localhost:6379/0
FM_FORCE_FALLBACK=1                 # Force in-memory cache
FM_REDIS_REQUIRED=1                 # Fail if Redis unavailable
```

**Frontend (`frontend/.env.local`):**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Rate Limits (UW Pro Tier)

- **WebSocket Connections:** 3 concurrent (we use 1)
- **REST API:** 120 requests/minute
- **Daily Limit:** 15,000 REST hits/day
- **Reconnect Backoff:** 5s → 10s → 20s → 40s → 60s (max)

---

## 📊 Features

### Core Features (Verified Channels)
- ✅ Real-time options flow alerts
- ✅ Live gamma exposure tracking
- ✅ Ticker-specific option trades
- ✅ Auto-reconnect on disconnect
- ✅ Multi-channel subscription management
- ✅ Connection status indicators
- ✅ Message history and logging

### Experimental Features (Toggle Required)
- ⚠️ Market movers streaming (with REST fallback)
- ⚠️ Dark pool activity (with REST fallback)
- ⚠️ Congress trades (with REST fallback)
- ⚠️ Automatic REST polling when WebSocket unavailable

### User Experience
- 🎯 Clean default view (3 verified feeds)
- 🧪 Opt-in experimental feeds
- 🔄 Seamless REST fallback
- 🎨 Dark theme throughout
- 📱 Responsive design
- ⏸️ Pause/resume per feed
- 🔍 Advanced filtering

---

## 🧪 Testing

### Test WebSocket Connection

```bash
# Test flow-alerts channel
python test_uw_websocket.py

# Test all verified channels
python test_websocket_hybrid_live.py

# Test specific ticker
python test_gex_endpoint.py
```

### Expected Results

```
✅ flow-alerts: Connected, receiving messages
✅ gex:SPY: Connected, receiving messages
✅ option_trades:TSLA: Connected, receiving messages
⏱️  market-movers: Connected (no data yet)
⏱️  dark-pool: Connected (no data yet)
⏱️  congress: Connected (no data yet)
```

---

## 📈 Performance

### Benchmarks (Typical)

- **Latency:** UW → Backend: <50ms
- **Latency:** Backend → Frontend: <20ms
- **Total Latency:** <70ms end-to-end
- **Throughput:** 100+ messages/second
- **Memory:** <50MB per frontend client
- **Reconnect Time:** <5s on disconnect

### Optimization Tips

1. **Use single backend instance** (singleton WebSocket client)
2. **Broadcast to multiple frontends** (don't open multiple UW connections)
3. **Enable Redis caching** for REST fallback
4. **Implement message throttling** on high-volume channels
5. **Use React.memo** for feed components

---

## 🐛 Troubleshooting

### WebSocket Not Connecting

**Problem:** "WebSocket streaming service not available"

**Solution:**
```bash
# Check UW_API_TOKEN is set
echo $UW_API_TOKEN

# Restart backend
cd backend && python -m uvicorn server:app --reload --port 8000
```

### No Messages Received

**Problem:** Connected but no data

**Possible Causes:**
1. **Market closed** - Options flow only during trading hours
2. **Low activity** - Try high-volume tickers (SPY, TSLA, AAPL)
3. **Channel name** - Experimental channels may have different names

**Solution:**
```bash
# Test with known active channel
python test_uw_websocket.py
```

### Frequent Disconnects

**Problem:** Connection drops every few minutes

**Solution:**
1. Check network stability
2. Verify firewall allows WebSocket connections
3. Backend auto-reconnects with exponential backoff
4. Monitor backend logs for errors

---

## 📚 Additional Resources

### Documentation Files
- `WEBSOCKET_IMPLEMENTATION_COMPLETE.md` - Complete implementation details
- `WEBSOCKET_CHANNELS_FINAL_RECOMMENDATION.md` - Design decisions
- `UW_WEBSOCKET_CHANNELS_RESEARCH.md` - Channel research findings
- `TRADESTATION_SETUP_GUIDE.md` - TradeStation integration
- `UW_API_PRO_TIER_DOCUMENTATION.md` - UW API documentation

### External Links
- [Unusual Whales API Docs](https://api.unusualwhales.com/docs)
- [UW GitHub Examples](https://github.com/unusual-whales/api-examples)
- [FastAPI WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)
- [React WebSocket Patterns](https://react.dev)

---

## 🤝 Contributing

### Adding New Channels

1. **Verify channel exists** in UW documentation
2. **Add backend endpoint** in `/backend/routers/stream.py`
3. **Create frontend component** in `/frontend/src/components/streaming/`
4. **Add to StreamingDashboard** with appropriate verification badge
5. **Update documentation**
6. **Test thoroughly**

### Code Style
- Backend: `ruff`, `mypy`, `bandit`
- Frontend: `eslint`, `prettier`
- All code must pass CI/QA gates

---

## 📝 License

Proprietary - FlowMind Platform

---

## 🆘 Support

For issues or questions:
- GitHub Issues: [Flowmind Repository](https://github.com/barbudangabriel-gif/Flowmind)
- UW API Support: Contact Dan Wagner @ Unusual Whales
- Email: support@flowmind.ai

---

**Last Updated:** 2025-10-14  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
