# FlowMind - UI Components Guide

## 📋 Overview

This document describes the UI components and pages added to FlowMind for the Market Intelligence features integration (October 2025).

## 🎨 Design System

All components follow FlowMind's dark-only design system:

- **Background**: `slate-900` (#0f172a)
- **Cards/Panels**: `slate-800` (#1e293b)
- **Inputs/Forms**: `slate-700` (#334155)
- **Text Primary**: `white` (#ffffff)
- **Text Secondary**: `slate-300` (#cbd5e1)
- **Borders**: `slate-600` (#475569)
- **Accents**: `blue-400`, `emerald-400`, `red-400`, `purple-400`

## 🆕 New Components

### 1. MarketMoversWidget.jsx

**Location**: `frontend/src/components/MarketMoversWidget.jsx`

**Purpose**: Dashboard widget showing top market movers in 3 columns

**Features**:
- Three columns: Top Gainers (green), Top Losers (red), Most Active (blue)
- Auto-refresh every 30 seconds
- Click ticker → Navigate to Builder
- Click "View All" → Navigate to MarketMoversPage
- Responsive: 3 columns on desktop, stacks on mobile

**API**: `GET /api/flow/market-movers`

**Props**: None (standalone widget)

**Usage**:
```jsx
import MarketMoversWidget from './components/MarketMoversWidget';

<MarketMoversWidget />
```

**State Management**:
- Local state (useState) for data, loading, error
- useEffect for polling with cleanup

### 2. MarketMoversPage.jsx

**Location**: `frontend/src/pages/MarketMoversPage.jsx`

**Purpose**: Full-page view of market movers with detailed tables

**Features**:
- Shows top 20 stocks in each category (vs 3 in widget)
- Manual refresh button + auto-refresh timer (30s)
- Real-time badge when data is fresh (<60s old)
- Tables with sortable columns: ticker, price, change %, volume
- Click ticker → Navigate to Builder
- Responsive tables with horizontal scroll on mobile

**Routes**:
- `/market-movers` - Main page

**API**: `GET /api/flow/market-movers`

### 3. CongressTradesPage.jsx

**Location**: `frontend/src/pages/CongressTradesPage.jsx`

**Purpose**: Track congressional trading activity

**Features**:
- Summary cards: Total Buy/Sell, This Week count, Most Active politician
- Filters: Politician name, Party (D/R/I), Transaction Type (BUY/SELL), Date Range
- Party badges: blue (Democrat), red (Republican), purple (Independent)
- Transaction type badges: green (BUY), red (SELL)
- Full table with politician name, party, ticker, type, amount, price
- Click ticker → Navigate to Builder
- Clear filters button

**Routes**:
- `/congress-trades` - Main page

**API**: `GET /api/flow/congress-trades?ticker=&politician=&party=&transaction_type=&limit=100`

**Query Parameters**:
- `ticker`: Filter by stock symbol (e.g., "NVDA")
- `politician`: Filter by politician name (e.g., "Pelosi")
- `party`: Filter by party (D, R, I)
- `transaction_type`: BUY, SELL, EXCHANGE
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `limit`: Max results (1-500, default 100)

### 4. DarkPoolPage.jsx

**Location**: `frontend/src/pages/DarkPoolPage.jsx`

**Purpose**: Monitor dark pool activity (off-exchange trades)

**Features**:
- Volume chart (Plotly): Stacked bar chart showing dark pool (purple) vs lit exchange (blue) volume
- Filters: Ticker symbol, Minimum volume threshold
- Recent prints table: Time, Ticker, Volume, Price, Notional value
- Large print highlights: Yellow flame icon (🔥) for prints >$10M
- Auto-refresh every 10 seconds
- Click ticker → Navigate to Builder
- Legend explaining colors and icons

**Routes**:
- `/dark-pool` - Main page

**API**: `GET /api/flow/dark-pool?ticker=&min_volume=&limit=100`

**Dependencies**:
- `react-plotly.js` for charts
- Plotly layout uses dark theme colors

**Chart Configuration**:
```javascript
{
  barmode: 'stack',
  paper_bgcolor: '#1e293b',
  plot_bgcolor: '#1e293b',
  font: { color: '#cbd5e1' }
}
```

### 5. InstitutionalPage.jsx

**Location**: `frontend/src/pages/InstitutionalPage.jsx`

**Purpose**: View institutional holdings (13F filings) per ticker

**Features**:
- Ticker search input (with quarter selector)
- Summary cards: Total Institutional Ownership %, Change QoQ %, Top Holder
- Ownership pie chart (Plotly): Top 5 holders with colorful slices
- Top holders table: Institution name, Shares (M), Value ($B), Change %, Filed date
- Change % color-coded: green (positive), red (negative)
- Info box explaining 13F filings
- Color palette: blue, purple, pink, orange, green

**Routes**:
- `/institutional` - Main page
- `/institutional?ticker=TSLA` - Pre-filled ticker

**API**: `GET /api/flow/institutional/{ticker}?quarter=`

**Path Parameters**:
- `ticker`: Stock symbol (required)

**Query Parameters**:
- `quarter`: Quarter filter (e.g., "2025Q3", optional)

## 📍 Navigation Integration

All new pages are integrated into the sidebar under a new **"Market Intelligence"** section:

```
└─ Market Intelligence
   ├─ Flow Summary (existing)
   ├─ 🌊 Dark Pool (NEW)
   ├─ 📈 Market Movers (NEW)
   ├─ 🏛️ Congress Trades (NEW)
   └─ 🏢 Institutional (NEW)
```

**File**: `frontend/src/lib/nav.simple.js`

**Route Definitions** (`frontend/src/App.js`):
```javascript
<Route path="/dark-pool" element={<DarkPoolPage />} />
<Route path="/market-movers" element={<MarketMoversPage />} />
<Route path="/congress-trades" element={<CongressTradesPage />} />
<Route path="/institutional" element={<InstitutionalPage />} />
```

## 🔌 API Integration Patterns

### Fetch Pattern
All components use the same API fetch pattern:

```javascript
const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

const fetchData = async () => {
  try {
    const response = await fetch(`${API}/api/flow/endpoint`);
    const result = await response.json();
    
    if (result.status === 'success') {
      setData(result.data);
    } else {
      setError(result.error);
    }
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### Loading States
Skeleton loaders use `animate-pulse` class:

```jsx
{loading && (
  <div className="h-8 bg-slate-700 rounded w-48 animate-pulse"></div>
)}
```

### Error Handling
Error states use red accent colors:

```jsx
{error && (
  <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-4">
    <span className="text-red-400">⚠️ {error}</span>
  </div>
)}
```

## 🎨 Component Patterns

### Card Component
All pages use slate-800 cards:

```jsx
<div className="bg-slate-800 rounded-lg p-6 shadow-lg">
  <h2 className="text-lg font-semibold text-white mb-4">Title</h2>
  {/* Content */}
</div>
```

### Summary Cards
4-column grid for metrics:

```jsx
<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
  <div className="bg-slate-800 rounded-lg p-4">
    <div className="text-slate-400 text-sm">Label</div>
    <div className="text-2xl font-bold text-blue-400">Value</div>
  </div>
</div>
```

### Tables
Hover states and alternating rows:

```jsx
<table className="w-full">
  <thead>
    <tr className="border-b border-slate-700">
      <th className="text-left py-3 px-4 text-slate-400 text-sm">Header</th>
    </tr>
  </thead>
  <tbody>
    <tr className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer">
      <td className="py-3 px-4 text-white">Data</td>
    </tr>
  </tbody>
</table>
```

### Filters
Consistent filter bar pattern:

```jsx
<div className="bg-slate-800 rounded-lg p-6">
  <h2 className="text-lg font-semibold text-white mb-4">🔍 Filters</h2>
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
    <input
      className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
    />
  </div>
</div>
```

## 📱 Responsive Design

All components are mobile-responsive:

### Breakpoints
- **Mobile**: `< 768px` (default)
- **Tablet**: `md:` prefix (`>= 768px`)
- **Desktop**: `lg:` prefix (`>= 1024px`)

### Mobile Patterns
```jsx
// Grid that stacks on mobile
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">

// Flex row that wraps on mobile
<div className="flex flex-col md:flex-row gap-4">

// Hide on mobile
<div className="hidden md:block">

// Show only on mobile
<div className="block md:hidden">
```

## 🔄 Auto-Refresh Patterns

### Polling Implementation
```javascript
useEffect(() => {
  fetchData();
  
  const interval = setInterval(fetchData, 30000); // 30s
  
  return () => clearInterval(interval); // Cleanup
}, [dependencies]);
```

### Manual Refresh
```javascript
const [refreshing, setRefreshing] = useState(false);

const handleRefresh = async () => {
  setRefreshing(true);
  await fetchData();
  setRefreshing(false);
};
```

## 🎯 Click Actions

### Navigate to Builder
All ticker clicks navigate to Builder with pre-filled symbol:

```javascript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

const handleTickerClick = (ticker) => {
  navigate(`/builder?symbol=${ticker}`);
};
```

## 📊 Chart Integration (Plotly)

### Dark Theme Configuration
All Plotly charts use dark theme:

```javascript
import Plot from 'react-plotly.js';

<Plot
  data={[{ x: [...], y: [...], type: 'bar' }]}
  layout={{
    paper_bgcolor: '#1e293b',  // slate-800
    plot_bgcolor: '#1e293b',
    font: { color: '#cbd5e1' }, // slate-300
    xaxis: { gridcolor: '#334155' }, // slate-700
    yaxis: { gridcolor: '#334155' }
  }}
  config={{ displayModeBar: false }}
  style={{ width: '100%', height: '400px' }}
/>
```

### Color Palettes
- **Market Movers**: emerald (gainers), red (losers), blue (active)
- **Dark Pool**: purple (dark pool), blue (lit exchange)
- **Institutional**: rainbow palette (blue, purple, pink, orange, green)

## 🧪 Testing

### Component Testing
Each component should be tested for:
- Loading state renders skeleton
- Error state shows error message
- Success state renders data
- Click actions navigate correctly
- Filters update query params
- Auto-refresh works

### Integration Testing
Backend tests in `/uw_correct_endpoints_test.py` cover:
- API endpoint responses
- Response structure validation
- Mock data fallback
- Error handling

## 📝 Documentation Updates

Updated files:
- ✅ `UW_API_CORRECT_ENDPOINTS.md` - Added 4 new API endpoints
- ✅ `UI_COMPONENTS_GUIDE.md` - This file
- ✅ `README.md` - (if needed) Add Market Intelligence features

## 🚀 Deployment Checklist

Before deploying:
1. ✅ Verify all routes in `App.js`
2. ✅ Verify sidebar links in `nav.simple.js`
3. ✅ Test mobile responsiveness
4. ✅ Test auto-refresh intervals
5. ✅ Test error states
6. ✅ Run `npm run build` successfully
7. ✅ Test with real UW API (set `UW_API_TOKEN`)

## 🎨 Styling Guidelines

### Colors
- Positive values: `text-emerald-400`
- Negative values: `text-red-400`
- Neutral: `text-slate-300`
- Accents: `text-blue-400`, `text-purple-400`

### Spacing
- Card padding: `p-6`
- Section margins: `mb-6` or `space-y-6`
- Grid gaps: `gap-4` or `gap-6`

### Typography
- Page titles: `text-3xl font-bold text-white`
- Section headers: `text-lg font-semibold text-white`
- Labels: `text-slate-400 text-sm`
- Values: `text-2xl font-bold text-blue-400`

## 🛠️ Development Tips

### Hot Reload
Run frontend in dev mode:
```bash
cd frontend && npm start
```

### Backend API
Run backend server:
```bash
cd backend && uvicorn server:app --reload --port 8000
```

### Environment Variables
Create `frontend/.env.local`:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Debug Mode
Check browser console for:
- Fetch errors
- API responses
- Component render logs

## 🔗 Related Documentation

- [UW API Endpoints](./UW_API_CORRECT_ENDPOINTS.md)
- [Dark Theme Guide](./DARK_THEME_ONLY_VALIDATION.md)
- [Platform Guide](./PLATFORM_GUIDE.md)

---

**Created**: October 13, 2025
**Author**: FlowMind Development Team
**Version**: 1.0.0
