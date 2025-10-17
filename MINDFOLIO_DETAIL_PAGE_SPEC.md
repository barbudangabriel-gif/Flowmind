# Mindfolio Detail Page - Design Specification

## Overview

The Mindfolio Detail Page is the **central hub** for viewing and managing a single Mindfolio. It provides:
- **Aggregate performance chart** showing cash, stocks, and options over time
- **Tab navigation** for different asset classes (Summary, Stocks, Options, Dividend)
- **Time range filters** (1M, 6M, YTD, ALL)
- **Real-time allocation breakdown** with percentages
- **Drawdown indicators** to show current performance vs initial value

---

## UI Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ 📄 Header │
│ ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ Aggressive Growth │ │ [Edit] [+ Add Position] │ │
│ │ Mindfolio ID: mf_abc123 │ │ │ │
│ └──────────────────────────────┘ └─────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│ 📑 Tab Navigation │
│ [SUMMARY] [STOCKS] [OPTIONS] [DIVIDEND] │
├──────────────────────────────────────────────────────────────────────┤
│ SUMMARY TAB │
│ │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ AGGREGATE CHART CARD │ │
│ │ │ │
│ │ ┌─ Top Section ──────────────────────────────────────────┐ │ │
│ │ │ LEFT: Current Allocation RIGHT: Total Value │ │ │
│ │ │ • Cash $25.0k (27.8%) $89,700 │ │ │
│ │ │ • Stocks $48.5k (54.1%) +5.53% ↑ │ │ │
│ │ │ • Options $16.2k (18.1%) │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │ │ │
│ │ ┌─ Time Range Selector ─────────────────────────────────┐ │ │
│ │ │ [1M] [6M] [YTD] [ALL] │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │ │ │
│ │ ┌─ Chart (h-96) ──────────────────────────────────────┐ │ │
│ │ │ │ │ │
│ │ │ Stacked Area Chart │ │ │
│ │ │ │ │ │
│ │ │ 90k ─────────────────── Purple (Options) │ │ │
│ │ │ ──── Blue (Stocks) │ │ │
│ │ │ 60k ───── │ │ │
│ │ │ ──── │ │ │
│ │ │ 30k ──── │ │ │
│ │ │ ────── Green (Cash) │ │ │
│ │ │ 0k │ │ │
│ │ │ Jan Feb Mar Apr May Jun Jul Aug Sep │ │ │
│ │ │ │ │ │
│ │ │ Legend: ● Cash ● Stocks ● Options │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─ Summary Stats Grid (3 columns) ──────────────────────────────┐ │
│ │ ┌─ Cash ─────┐ ┌─ Stocks ───┐ ┌─ Options ──┐ │ │
│ │ │ │ │ │ │ │ │ │
│ │ │ $25.0k │ │ $48.5k │ │ $16.2k │ │ │
│ │ │ 27.8% │ │ 54.1% │ │ 18.1% │ │ │
│ │ │ Available │ │ 8 positions│ │ 12 contracts│ │ │
│ │ └────────────┘ └────────────┘ └────────────┘ │ │
│ └────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─ Module Allocation ────────────────────────────────────────────┐ │
│ │ 🤖 IV SERVICE $30.0k (33.5% allocated) │ │
│ │ Max Risk: $1,000 • Daily Limit: $2,000 │ │
│ │ │ │
│ │ SELL PUTS ENGINE $40.0k (44.6% allocated) │ │
│ │ Max Risk: $2,000 • Daily Limit: $3,000 │ │
│ │ │ │
│ │ ⚖️ SMART REBALANCER $15.0k (16.7% allocated) │ │
│ │ Max Risk: $500 • Daily Limit: $1,000 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📐 Component Structure

### **MindfolioDetailNew.jsx**

```jsx
export default function MindfolioDetailNew() {
 // State management
 const [mindfolio, setMindfolio] = useState(null);
 const [activeTab, setActiveTab] = useState("SUMMARY");
 const [timeRange, setTimeRange] = useState("1M");
 const [chartData, setChartData] = useState(null);

 // Sections:
 // 1. Header (name, ID, actions)
 // 2. Tab Navigation
 // 3. Tab Content (conditional rendering)
 // - SUMMARY: Chart + Stats + Modules
 // - STOCKS: Position table
 // - OPTIONS: Options table with Greeks
 // - DIVIDEND: Income tracking
}
```

---

## Design Specifications

### **Colors**

```javascript
{
 // Chart layers
 cash: {
 border: "rgb(34, 197, 94)", // Green-500
 background: "rgba(34, 197, 94, 0.1)"
 },
 stocks: {
 border: "rgb(59, 130, 246)", // Blue-500
 background: "rgba(59, 130, 246, 0.1)"
 },
 options: {
 border: "rgb(168, 85, 247)", // Purple-500
 background: "rgba(168, 85, 247, 0.1)"
 },

 // UI elements
 background: "bg-slate-800/50",
 border: "border-slate-700",
 text: {
 primary: "text-white",
 secondary: "text-gray-400",
 success: "text-green-400",
 error: "text-red-400"
 },
 
 // Buttons
 tab: {
 active: "text-white border-b-2 border-blue-500",
 inactive: "text-gray-400 hover:text-gray-300"
 },
 timeRange: {
 active: "bg-blue-600 text-white",
 inactive: "bg-slate-700/50 text-gray-400 hover:bg-slate-700"
 }
}
```

### **Typography**

```javascript
{
 header: {
 title: "text-3xl font-bold text-white",
 subtitle: "text-gray-400 text-sm"
 },
 allocation: {
 label: "text-sm text-gray-400 font-medium",
 value: "text-white font-medium",
 percentage: "text-gray-400 text-sm"
 },
 totalValue: {
 label: "text-sm text-gray-400 font-medium",
 value: "text-3xl font-bold text-white",
 change: "text-sm font-medium text-green-400/text-red-400"
 }
}
```

### **Spacing**

```javascript
{
 page: "p-8 space-y-6",
 card: "p-6",
 cardGrid: "grid grid-cols-1 md:grid-cols-3 gap-6",
 chartHeight: "h-96",
 gap: {
 small: "gap-2",
 medium: "gap-4",
 large: "gap-6"
 }
}
```

---

## Chart Configuration

### **Chart.js Settings**

```javascript
const chartOptions = {
 responsive: true,
 maintainAspectRatio: false,
 interaction: {
 mode: 'index', // Show all datasets at same X position
 intersect: false // Trigger on hover anywhere in column
 },
 plugins: {
 legend: {
 position: 'bottom',
 labels: {
 color: '#94a3b8', // slate-400
 padding: 15,
 font: { size: 12 }
 }
 },
 tooltip: {
 backgroundColor: 'rgba(15, 23, 42, 0.9)', // slate-900
 titleColor: '#f1f5f9', // slate-100
 bodyColor: '#cbd5e1', // slate-300
 callbacks: {
 label: (context) => `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`,
 footer: (tooltipItems) => {
 const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
 return `Total: $${total.toLocaleString()}`;
 }
 }
 }
 },
 scales: {
 x: {
 grid: { color: '#1e293b' }, // slate-800
 ticks: { color: '#64748b' } // slate-500
 },
 y: {
 grid: { color: '#1e293b' },
 ticks: {
 color: '#64748b',
 callback: (value) => '$' + (value / 1000).toFixed(0) + 'k'
 }
 }
 }
};
```

### **Data Structure**

```javascript
{
 labels: ["2025-01-01", "2025-01-02", ...], // ISO date strings
 datasets: [
 {
 label: "Cash",
 data: [25000, 25100, 25200, ...],
 borderColor: "rgb(34, 197, 94)",
 backgroundColor: "rgba(34, 197, 94, 0.1)",
 fill: true,
 tension: 0.4 // Smooth curves
 },
 {
 label: "Stocks",
 data: [45000, 45800, 46200, ...],
 borderColor: "rgb(59, 130, 246)",
 backgroundColor: "rgba(59, 130, 246, 0.1)",
 fill: true,
 tension: 0.4
 },
 {
 label: "Options",
 data: [15000, 15300, 15600, ...],
 borderColor: "rgb(168, 85, 247)",
 backgroundColor: "rgba(168, 85, 247, 0.1)",
 fill: true,
 tension: 0.4
 }
 ]
}
```

---

## 🔌 API Integration

### **Endpoints Needed**

#### **1. Get Mindfolio Performance Data**
```javascript
GET /api/mindfolio/:id/performance?range=1M

Response:
{
 "mindfolio_id": "mf_abc123",
 "range": "1M",
 "data_points": 30,
 "series": [
 {
 "date": "2025-09-15",
 "timestamp": "2025-09-15T16:00:00Z",
 "cash": 25000,
 "stocks": 45000,
 "options": 15000,
 "total": 85000
 },
 ...
 ],
 "current": {
 "cash": 25000,
 "stocks": 48500,
 "options": 16200,
 "total": 89700
 },
 "initial_value": 85000,
 "drawdown_pct": 5.53
}
```

#### **2. Get Stock Positions (for STOCKS tab)**
```javascript
GET /api/mindfolio/:id/positions/stocks

Response:
{
 "positions": [
 {
 "symbol": "TSLA",
 "qty": 100,
 "avg_cost": 250.50,
 "current_price": 265.30,
 "cost_basis": 25050,
 "market_value": 26530,
 "unrealized_pnl": 1480,
 "unrealized_pnl_pct": 5.91,
 "day_change": 250,
 "day_change_pct": 0.95
 },
 ...
 ],
 "total_cost_basis": 48000,
 "total_market_value": 48500,
 "total_unrealized_pnl": 500
}
```

#### **3. Get Options Positions (for OPTIONS tab)**
```javascript
GET /api/mindfolio/:id/positions/options

Response:
{
 "positions": [
 {
 "symbol": "TSLA",
 "strategy": "Iron Condor",
 "legs": [
 {
 "type": "CALL",
 "strike": 270,
 "expiration": "2025-11-15",
 "side": "SELL",
 "qty": 1,
 "premium_collected": 250
 },
 ...
 ],
 "dte": 31,
 "entry_date": "2025-10-01",
 "credit_received": 250,
 "current_value": 125,
 "unrealized_pnl": 125,
 "max_profit": 250,
 "max_loss": 750,
 "greeks": {
 "delta": 0.05,
 "gamma": 0.02,
 "theta": -2.5,
 "vega": 5.2
 }
 },
 ...
 ],
 "total_credit_received": 3200,
 "total_current_value": 2850,
 "total_unrealized_pnl": 350,
 "aggregate_greeks": {
 "delta": 12.5,
 "gamma": 3.2,
 "theta": -45.8,
 "vega": 125.3
 }
}
```

#### **4. Get Dividend Income (for DIVIDEND tab)**
```javascript
GET /api/mindfolio/:id/dividends

Response:
{
 "history": [
 {
 "symbol": "AAPL",
 "ex_date": "2025-08-15",
 "pay_date": "2025-08-22",
 "amount_per_share": 0.24,
 "shares_held": 100,
 "total_amount": 24.00,
 "status": "paid"
 },
 ...
 ],
 "upcoming": [
 {
 "symbol": "MSFT",
 "ex_date": "2025-11-15",
 "estimated_amount": 32.00
 },
 ...
 ],
 "summary": {
 "ytd_total": 850.50,
 "monthly_avg": 94.50,
 "annual_projected": 1200.00,
 "yield_on_cost": 2.85
 }
}
```

---

## Time Range Logic

### **Range Calculation**

```javascript
const getTimeRangeParams = (range) => {
 const today = new Date();
 let startDate;
 let dataPoints;

 switch (range) {
 case "1M":
 startDate = new Date(today);
 startDate.setMonth(startDate.getMonth() - 1);
 dataPoints = 30; // Daily data
 break;

 case "6M":
 startDate = new Date(today);
 startDate.setMonth(startDate.getMonth() - 6);
 dataPoints = 180; // Daily data
 break;

 case "YTD":
 startDate = new Date(today.getFullYear(), 0, 1);
 dataPoints = Math.ceil((today - startDate) / (1000 * 60 * 60 * 24));
 break;

 case "ALL":
 // From mindfolio creation date
 startDate = new Date(mindfolio.created_at);
 dataPoints = Math.ceil((today - startDate) / (1000 * 60 * 60 * 24));
 break;

 default:
 startDate = new Date(today);
 startDate.setMonth(startDate.getMonth() - 1);
 dataPoints = 30;
 }

 return {
 startDate: startDate.toISOString().split('T')[0],
 endDate: today.toISOString().split('T')[0],
 dataPoints
 };
};
```

---

## Responsive Design

### **Breakpoints**

```javascript
{
 // Grid adjustments
 "grid-cols-1": "Mobile (< 768px)",
 "md:grid-cols-3": "Tablet+ (≥ 768px)",
 "lg:grid-cols-4": "Desktop (≥ 1024px)",

 // Tab layout
 "Mobile": "Scrollable tabs",
 "Desktop": "Inline tabs with gap",

 // Chart height
 "h-64": "Mobile (256px)",
 "md:h-80": "Tablet (320px)",
 "lg:h-96": "Desktop (384px)"
}
```

---

## Implementation Checklist

### **Phase 1: Core Structure** 
- [x] Create MindfolioDetailNew.jsx component
- [x] Add tab navigation (SUMMARY, STOCKS, OPTIONS, DIVIDEND)
- [x] Add time range selector (1M, 6M, YTD, ALL)
- [x] Install Chart.js dependencies

### **Phase 2: Chart Integration** 
- [x] Configure Chart.js with dark theme
- [x] Create stacked area chart with 3 layers
- [x] Add custom tooltips with totals
- [x] Format Y-axis as $Xk
- [x] Add smooth curves (tension: 0.4)

### **Phase 3: Summary Tab** 
- [x] Allocation breakdown (top-left)
- [x] Total value with drawdown (top-right)
- [x] Summary stats grid (3 cards)
- [x] Module allocation cards

### **Phase 4: Data Integration** 🔄
- [ ] Connect to /api/mindfolio/:id/performance
- [ ] Replace mock data with real time-series
- [ ] Add loading states
- [ ] Add error handling

### **Phase 5: Additional Tabs** 
- [ ] STOCKS tab: Position table with P&L
- [ ] OPTIONS tab: Options table with Greeks
- [ ] DIVIDEND tab: Income tracking
- [ ] Add tab-specific filters/sorting

### **Phase 6: Polish** 
- [ ] Add skeleton loaders
- [ ] Add empty states
- [ ] Add export to CSV functionality
- [ ] Add print-friendly view
- [ ] Optimize performance for large datasets

---

## Future Enhancements

1. **Interactive Chart Features**
 - Click on data point to see transactions on that date
 - Zoom/pan functionality
 - Compare against benchmark (SPY, QQQ)

2. **Advanced Filtering**
 - Filter by module (show only IV Service positions)
 - Filter by asset type (stocks only, options only)
 - Custom date range picker

3. **Performance Metrics**
 - Sharpe ratio over selected range
 - Max drawdown visualization
 - Win rate by time period

4. **Annotations**
 - Mark significant events (module added, large trade, etc.)
 - Show earnings dates for held stocks
 - Highlight dividend payment dates

5. **Export & Sharing**
 - Export chart as PNG
 - Share performance snapshot
 - Generate PDF report

---

**Status:** Phase 1-3 Complete 
**Next:** Connect real API data 🔄
