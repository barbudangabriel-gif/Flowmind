# TradeStation OHLCV Streaming - Configuration Guide

## 🔧 Environment Variables Setup

Create `/app/frontend/.env.local` (for Next.js) or update `/app/backend/.env`:

```env
# TradeStation API Configuration
TS_BASE_URL=https://sim-api.tradestation.com
TS_CLIENT_ID=YOUR_TS_CLIENT_ID
TS_CLIENT_SECRET=YOUR_TS_CLIENT_SECRET
TS_REFRESH_TOKEN=YOUR_TS_REFRESH_TOKEN

# Note: For LIVE trading, use:
# TS_BASE_URL=https://api.tradestation.com
```

## 📊 Required TradeStation API Scopes

Your TradeStation app must have these scopes:
- ✅ **offline_access** - For refresh token functionality
- ✅ **MarketData** - For OHLCV data access
- ✅ **Streaming** - For real-time data streaming (optional)

## 🚀 API Endpoints Implemented

### REST Endpoints:
- `GET /api/ohlcv?symbol=AAPL&tf=D&limit=500` - Snapshot OHLCV data
- `GET /api/tradestation/stream/AAPL?tf=1&limit=1000` - Stream info

### Streaming Endpoints:
- `GET /api/ohlcv/stream?symbol=AAPL&tf=1&barsBack=1000` - SSE stream

## 📈 Timeframe Mapping

| FlowMind | TradeStation | Description |
|----------|--------------|-------------|
| `1` | `1 Minute` | 1-minute bars |
| `5` | `5 Minute` | 5-minute bars |
| `15` | `15 Minute` | 15-minute bars |
| `30` | `30 Minute` | 30-minute bars |
| `60` / `1h` | `60 Minute` | 1-hour bars |
| `4h` | `240 Minute` | 4-hour bars |
| `D` | `1 Daily` | Daily bars |
| `W` | `1 Weekly` | Weekly bars |

## 🧪 Testing Commands

```bash
# Test REST endpoint
curl 'http://localhost:3000/api/ohlcv?symbol=AAPL&tf=5&limit=100'

# Test streaming endpoint (SSE)
curl 'http://localhost:3000/api/ohlcv/stream?symbol=AAPL&tf=1&barsBack=500'

# Test backend integration
curl 'http://localhost:8001/api/tradestation/stream/AAPL?tf=1&limit=100'
```

## 📱 React Integration

### Using REST Data:
```jsx
import { fetchOHLCV } from '../lib/fetchOHLCV';

// In your component
useEffect(() => {
  fetchOHLCV("AAPL", "5", 1000)
    .then(bars => setCandleData(bars))
    .catch(console.error);
}, []);
```

### Using Streaming Data:
```jsx
import { useTSStream } from '../lib/useTSStream';

// In your component
const { bars, status, isLive } = useTSStream({ 
  symbol: "AAPL", 
  tf: "1", 
  barsBack: 1000 
});

// bars updates automatically with real-time data
useEffect(() => {
  if (candleSeries && bars.length > 0) {
    candleSeries.setData(bars);
  }
}, [bars]);
```

## 🔒 Security Notes

- ✅ API credentials stored în environment variables
- ✅ Server-side token refresh pentru security
- ✅ No client-side credential exposure
- ✅ Proper error handling și rate limiting

## 📊 Data Format

All endpoints return standardized format:
```json
{
  "time": 1640995200,     // UNIX timestamp (seconds)
  "open": 152.34,         // Opening price
  "high": 154.12,         // High price  
  "low": 151.89,          // Low price
  "close": 153.45,        // Closing price
  "volume": 1234567       // Trading volume
}
```

## 🎯 Integration Benefits

- ✅ **Real-time Updates**: Live bar updates via SSE
- ✅ **Historical Data**: Complete snapshot loading
- ✅ **Professional Quality**: TradeStation institutional data
- ✅ **Performance Optimized**: Efficient streaming + caching
- ✅ **Error Resilient**: Automatic reconnection și fallbacks

## 🚀 Ready for Live Trading!

Once configured cu proper TradeStation credentials, FlowMind Analytics va avea access la:
- 📊 **Real-time market data** pentru all major symbols
- 📈 **Professional charting** cu live updates
- 🎯 **Institutional quality** data feeds
- ⚡ **Low latency** streaming pentru active trading