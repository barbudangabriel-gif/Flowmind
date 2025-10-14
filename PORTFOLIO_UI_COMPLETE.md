# 🎨 FlowMind Portfolio UI - Complete Guide

## 📋 Overview

FlowMind oferă un UI complet pentru management portofoliu cu:
- ✅ Multi-portfolio support
- ✅ TradeStation live integration
- ✅ Real-time P&L tracking
- ✅ Transaction history
- ✅ CSV import/export
- ✅ Analytics & charts
- ✅ Buckets organization
- ✅ Dark theme optimized

## 🗺️ Navigation Structure

### Sidebar Menu
```
📊 Account
  └── 💼 Portfolios (expandable)
      ├── Portfolio 1
      ├── Portfolio 2
      └── + Create Portfolio
```

**Location:** `/portfolios`
**Icon:** Briefcase (💼)
**Dynamic:** Shows all user portfolios + "Create" button

## 📱 Pages & Components

### 1. **Portfolios List** (`/portfolios`)
**File:** `frontend/src/pages/PortfoliosList.jsx`

**Features:**
- Grid layout (responsive: 1 col mobile, 2 tablet, 3 desktop)
- Portfolio cards showing:
  - Name
  - NAV (Net Asset Value)
  - Status (ACTIVE/PAUSED/CLOSED)
  - Module allocations
- "+ Create Portfolio" button (top-right)
- Empty state with call-to-action

**API Call:** `GET /api/portfolios`

**UI Elements:**
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Link to={`/portfolios/${id}`}>
    <div className="border rounded-xl p-4 hover:bg-gray-50">
      <h3>{name}</h3>
      <div>NAV: ${cash_balance}</div>
      <div>Status: {status}</div>
      <div>Modules: {modules.join(", ")}</div>
    </div>
  </Link>
</div>
```

---

### 2. **Portfolio Detail** (`/portfolios/:id`)
**File:** `frontend/src/pages/PortfolioDetail.jsx`

**Layout:**
```
┌─────────────────────────────────────────┐
│ Header: Portfolio Name + NAV + Status  │
├─────────────────────────────────────────┤
│ Stats Cards (4-column grid):           │
│ [Realized P&L] [Total Trades] [Open]  │
│ [Cash Balance]                          │
├─────────────────────────────────────────┤
│ Tab Navigation:                         │
│ [Overview] [Analytics] [Positions]      │
│ [Transactions] [Import CSV]             │
├─────────────────────────────────────────┤
│ Tab Content (dynamic)                   │
└─────────────────────────────────────────┘
```

**Tabs:**

#### Tab 1: Overview 📊
- Portfolio summary
- Recent transactions (last 10)
- Quick actions:
  - Add/Remove funds
  - Add transaction
  - Module allocation

#### Tab 2: Analytics & Buckets 📈
**Component:** `AnalyticsPanel`
- Equity curve chart
- P&L breakdown
- Buckets management
  - Create/edit buckets
  - Assign symbols to buckets
  - Color coding

#### Tab 3: Positions & P&L 💼
**Component:** `PositionsTable`
- Current open positions
- Columns:
  - Symbol
  - Quantity
  - Avg Cost
  - Cost Basis
  - Market Value (requires live price)
  - Unrealized P&L
  - P&L %
- FIFO-based calculation
- Real-time updates (if connected to TS)

#### Tab 4: Transactions 📋
**Component:** `TransactionsTable`
- Full transaction history
- Filters:
  - Symbol
  - Date range
  - Side (BUY/SELL)
- Pagination
- Export to CSV button
- Columns:
  - Date/Time
  - Symbol
  - Side
  - Quantity
  - Price
  - Fee
  - Total
  - Notes

#### Tab 5: Import CSV 📤
**Component:** `CSVImport`
- Drag & drop file upload
- CSV format validation
- Preview imported data
- Bulk transaction import
- Error handling with detailed feedback

**CSV Format:**
```csv
datetime,symbol,side,qty,price,fee,notes,account_id
2025-10-01T10:00:00Z,AAPL,BUY,100,150.00,1.00,Opening,account1
```

---

### 3. **Create Portfolio** (`/portfolios/new`)
**File:** `frontend/src/pages/PortfolioCreate.jsx`

**Form Fields:**
1. **Name** (required)
   - Text input
   - Validation: 3-50 characters

2. **Starting Balance** (required)
   - Number input
   - Default: $10,000
   - Validation: > 0

3. **Module Allocations** (optional)
   - Multi-module selector
   - Per module:
     - Module type (dropdown)
     - Budget allocation
     - Max risk per trade
     - Daily loss limit
     - Auto-trade toggle

**Module Types:**
- IV_SERVICE (Implied Volatility)
- SELL_PUTS (Cash-secured puts)
- COVERED_CALLS
- IRON_CONDOR
- CUSTOM

**UI Flow:**
```
1. Enter name → 2. Set balance → 3. Add modules → 4. Review → 5. Create
```

**API Call:** `POST /api/portfolios`

---

### 4. **TradeStation Live Portfolio**
**Component:** `TradeStationMainPortfolio.js`

**Features:**
- Multi-account aggregation
- Real-time positions from TradeStation API
- Weighted average calculations
- Position grouping by symbol
- Account breakdown per symbol
- Auto-refresh (30s interval)
- OAuth2 integration

**Position Card:**
```jsx
<div className="position-card">
  <div className="symbol">{symbol}</div>
  <div className="accounts-grid">
    {accounts.map(acc => (
      <div key={acc.id}>
        {acc.name}: {acc.qty} @ ${acc.avg}
      </div>
    ))}
  </div>
  <div className="totals">
    Total: {totalQty} @ ${weightedAvg}
    P&L: ${unrealized} ({pct}%)
  </div>
</div>
```

**API Calls:**
- `GET /api/portfolios/positions-ts` (every 30s)
- `GET /api/auth/tradestation/status` (every 5min)

---

## 🎨 Design System

### Colors (Dark Theme Only)

**Background:**
- Primary: `#0a0e1a` (dark navy)
- Secondary: `#0f1419` (slightly lighter)
- Cards: `#1e293b` (slate-800)

**Text:**
- Primary: `#ffffff` (white)
- Secondary: `#94a3b8` (slate-400)
- Muted: `#64748b` (slate-500)

**Accents:**
- Success: `#10b981` (green-500) - Profits, ACTIVE status
- Danger: `#ef4444` (red-500) - Losses, errors
- Warning: `#f59e0b` (amber-500) - Warnings
- Info: `#3b82f6` (blue-500) - Links, CTAs

**Borders:**
- Default: `#1e293b` (slate-800)
- Hover: `#334155` (slate-700)

### Typography

**Headers:**
- H1: `text-xl font-semibold` (20px)
- H2: `text-lg font-semibold` (18px)
- H3: `text-base font-medium` (16px)

**Body:**
- Regular: `text-sm` (14px)
- Small: `text-xs` (12px)
- Mono (numbers): `font-mono`

### Components

**Card:**
```jsx
<div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
  {/* Content */}
</div>
```

**Button Primary:**
```jsx
<button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
  Click Me
</button>
```

**Button Secondary:**
```jsx
<button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors">
  Cancel
</button>
```

**Input:**
```jsx
<input 
  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
  type="text"
/>
```

**Badge (Status):**
```jsx
<span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
  ACTIVE
</span>
```

---

## 🔧 Components Breakdown

### Core Components

#### 1. **PositionsTable**
**File:** `frontend/src/components/PositionsTable.jsx`

**Props:**
```typescript
interface PositionsTableProps {
  portfolioId: string;
  positions: Position[];
  onRefresh: () => void;
}
```

**Features:**
- Sortable columns
- Market value calculation (requires live price)
- P&L color coding (green/red)
- Symbol links to detail view

---

#### 2. **TransactionsTable**
**File:** `frontend/src/components/TransactionsTable.jsx`

**Props:**
```typescript
interface TransactionsTableProps {
  portfolioId: string;
  transactions: Transaction[];
  filters?: {
    symbol?: string;
    startDate?: string;
    endDate?: string;
  };
}
```

**Features:**
- Date/time formatting
- Side badges (BUY=green, SELL=red)
- Total calculation with fees
- Notes column (truncated with tooltip)

---

#### 3. **CSVImport**
**File:** `frontend/src/components/CSVImport.jsx`

**Features:**
- Drag & drop zone
- File validation (CSV only)
- Preview table (first 10 rows)
- Column mapping
- Error reporting with row numbers
- Progress indicator

**CSV Validation:**
- Required columns: datetime, symbol, side, qty, price
- Optional: fee, notes, account_id
- Date format: ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
- Side: BUY or SELL (case-insensitive)

---

#### 4. **AnalyticsPanel**
**File:** `frontend/src/components/AnalyticsPanel.jsx`

**Sections:**

**Equity Curve:**
- Line chart (Chart.js or Recharts)
- Date range selector
- Interval selector (daily/weekly/monthly)
- Export to CSV button

**P&L Breakdown:**
- Realized vs Unrealized
- Per-symbol breakdown
- Top winners/losers

**Buckets Management:**
- Create bucket form
- Assign symbols to buckets
- Color picker for visual organization
- Bucket performance summary

---

#### 5. **BucketForm**
**File:** `frontend/src/components/BucketForm.jsx`

**Form Fields:**
- Name (required)
- Description (optional)
- Color (color picker)
- Initial symbols (multi-select)

**UI:**
```jsx
<form>
  <input type="text" placeholder="Bucket name" />
  <textarea placeholder="Description" />
  <input type="color" defaultValue="#4CAF50" />
  <SymbolMultiSelect />
  <button>Create Bucket</button>
</form>
```

---

## 📊 Data Flow

### Loading Portfolio Data

```javascript
// 1. Load portfolio details
const portfolio = await pfClient.get(portfolioId);

// 2. Load statistics in parallel
const stats = await pfClient.stats(portfolioId);

// 3. Load positions (optional, for Positions tab)
const positions = await pfClient.positions(portfolioId);

// 4. Load transactions (optional, for Transactions tab)
const transactions = await pfClient.transactions(portfolioId);

// 5. Combine and display
setState({ portfolio, stats, positions, transactions });
```

### Real-time Updates (TradeStation)

```javascript
// Poll TradeStation positions every 30s
useEffect(() => {
  const fetchTSPositions = async () => {
    const data = await fetch('/api/portfolios/positions-ts');
    setPositions(data.positions_grid);
  };
  
  fetchTSPositions(); // Initial load
  const interval = setInterval(fetchTSPositions, 30000); // 30s
  
  return () => clearInterval(interval);
}, []);
```

---

## 🔐 Authentication Flow (TradeStation)

### OAuth2 Integration

**Step 1: Get Auth URL**
```javascript
const { auth_url, state } = await fetch('/api/portfolios/ts/auth-url');
window.location.href = auth_url; // Redirect to TradeStation
```

**Step 2: Handle Callback**
```javascript
// URL: /auth/callback?code=ABC123&state=XYZ789
const params = new URLSearchParams(window.location.search);
const code = params.get('code');
const state = params.get('state');

await fetch('/api/portfolios/ts/callback', {
  method: 'POST',
  body: JSON.stringify({ code, state })
});
```

**Step 3: Store Tokens**
Backend automatically stores tokens in MongoDB + memory cache.

**Step 4: Auto-refresh**
Backend auto-refreshes tokens 60s before expiry.

---

## 🎯 User Flows

### Flow 1: Create First Portfolio

1. User lands on `/portfolios` (empty state)
2. Clicks "+ Create Portfolio"
3. Enters name: "My Trading Account"
4. Sets balance: $50,000
5. (Optional) Adds module allocation
6. Clicks "Create Portfolio"
7. Redirected to `/portfolios/:id`

---

### Flow 2: Import CSV Transactions

1. User opens portfolio detail (`/portfolios/:id`)
2. Clicks "Import CSV" tab
3. Drags CSV file into dropzone
4. System validates format
5. Preview shows first 10 rows
6. User clicks "Import"
7. System processes transactions
8. Success: Shows "Imported 50 transactions"
9. Transactions tab auto-refreshes

---

### Flow 3: Connect TradeStation

1. User clicks "Connect TradeStation" in sidebar
2. System requests auth URL
3. User redirected to TradeStation OAuth
4. User approves access
5. TradeStation redirects to `/auth/callback`
6. Tokens stored automatically
7. User sees "Connected ✅" status
8. Real-time positions load automatically

---

### Flow 4: View P&L

1. User opens portfolio detail
2. Clicks "Positions & P&L" tab
3. Table loads with current positions
4. System fetches live prices (if TS connected)
5. Unrealized P&L calculated and displayed
6. Color-coded (green=profit, red=loss)
7. User can click symbol for drill-down

---

## 🚀 Performance Optimizations

### 1. **Lazy Loading**
```javascript
// Load positions only when tab is active
useEffect(() => {
  if (activeTab === 'positions') {
    loadPositions();
  }
}, [activeTab]);
```

### 2. **Memoization**
```javascript
// Memoize expensive calculations
const totalPnL = useMemo(() => 
  positions.reduce((sum, p) => sum + p.unrealized_pnl, 0),
  [positions]
);
```

### 3. **Debounced Search**
```javascript
// Debounce transaction search
const debouncedSearch = useMemo(
  () => debounce(searchTransactions, 300),
  []
);
```

### 4. **Virtual Scrolling** (Future)
For large transaction lists (1000+), implement virtual scrolling via `react-window`.

---

## 📱 Responsive Design

### Breakpoints
- Mobile: `< 640px` (1 column)
- Tablet: `640px - 1024px` (2 columns)
- Desktop: `> 1024px` (3 columns)

### Mobile Optimizations
- Collapsible sidebar
- Stacked cards instead of grid
- Bottom navigation for tabs
- Simplified transaction table (hide less important columns)

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Portfolio list rendering
- [ ] Transaction form validation
- [ ] FIFO calculation logic
- [ ] CSV parser

### Integration Tests
- [ ] Create portfolio flow
- [ ] Import CSV flow
- [ ] TradeStation OAuth flow
- [ ] Real-time position updates

### E2E Tests
- [ ] Complete user journey (Cypress)
- [ ] Multi-browser compatibility
- [ ] Mobile responsiveness

---

## 🔮 Future Enhancements

### Phase 1 (Q1 2026)
- [ ] Portfolio comparison view
- [ ] Benchmark overlay (SPY, QQQ)
- [ ] Mobile app (React Native)

### Phase 2 (Q2 2026)
- [ ] Social features (share portfolio performance)
- [ ] Alerts & notifications
- [ ] Tax reporting (Form 8949 export)

### Phase 3 (Q3 2026)
- [ ] AI-powered insights
- [ ] Automated rebalancing suggestions
- [ ] Risk scoring & recommendations

---

## 📁 File Structure

```
frontend/src/
├── pages/
│   ├── PortfoliosList.jsx          # Main list view
│   ├── PortfolioDetail.jsx         # Detail page with tabs
│   └── PortfolioCreate.jsx         # Creation form
├── components/
│   ├── PositionsTable.jsx          # Positions grid
│   ├── TransactionsTable.jsx       # Transaction history
│   ├── CSVImport.jsx               # CSV import UI
│   ├── AnalyticsPanel.jsx          # Charts & analytics
│   ├── BucketForm.jsx              # Bucket management
│   ├── TradeStationMainPortfolio.js # TS integration
│   └── AllPortfolios.js            # Portfolio overview
├── services/
│   └── portfolioClient.js          # API client
├── hooks/
│   └── usePortfolioManagement.js   # Custom hooks
└── lib/
    ├── portfolioAPI.js             # API helpers
    └── nav.simple.js               # Navigation structure
```

---

## 🎓 Developer Guide

### Adding a New Tab

1. **Define tab in PortfolioDetail.jsx:**
```javascript
const tabs = [
  // ...existing tabs
  { id: 'new-feature', label: 'New Feature', icon: '🚀' }
];
```

2. **Add tab content:**
```javascript
{activeTab === 'new-feature' && (
  <NewFeatureComponent portfolioId={id} />
)}
```

3. **Create component:**
```javascript
// components/NewFeatureComponent.jsx
export default function NewFeatureComponent({ portfolioId }) {
  // Component logic
  return <div>New Feature Content</div>;
}
```

### Adding a New API Endpoint

1. **Backend:** Add route in `backend/portfolios.py`
2. **Frontend:** Add method in `services/portfolioClient.js`
3. **Use in component:** Call the new API method

---

**Last Updated:** October 14, 2025  
**UI Framework:** React + Tailwind CSS  
**Status:** Production Ready ✅  
**Dark Theme:** Enforced (no light mode)
