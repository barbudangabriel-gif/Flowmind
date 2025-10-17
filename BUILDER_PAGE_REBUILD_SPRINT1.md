# Builder Page Rebuild - Sprint 1 Complete

## Overview
Complete rebuild of BuilderPage.jsx with clean, minimal architecture focused on core functionality.

## Files Created/Modified

### 1. `frontend/src/lib/useDebouncedEffect.js` (NEW)
**Purpose:** Custom React hook for debounced effects
- Prevents API spam by delaying effect execution
- Default delay: 300ms (customizable)
- Cleans up timeout on unmount
- Usage: `useDebouncedEffect(effect, deps, delay)`

### 2. `frontend/src/lib/builderApi.js` (NEW)
**Purpose:** Simplified API client for Builder endpoints
- Uses Vite env var (`VITE_API`)
- Two endpoints:
  - `priceStrategy(payload)` → POST /api/builder/price
  - `getHistorical(payload)` → POST /api/builder/historical
- Clean error handling with fetch API

### 3. `frontend/src/pages/BuilderPage.jsx` (REBUILT)
**Lines:** 276 (down from 763)
**Reduction:** 64% smaller codebase

**Architecture:**
```
BuilderPage (main component)
  ├── HeaderBar (symbol input, mode toggles)
  ├── ExpirationsPanel (select expiry date)
  ├── StrikesPanel (select strike price)
  ├── MetricsBar (Net Debit, Max Loss/Profit, PoP, Breakeven)
  ├── GreeksPanel (Delta, Gamma, Vega, Rho)
  └── Parameters (Range %, IV % sliders)
```

**Components (Internal):**
- `Card` - Tailwind card wrapper
- `SectionTitle` - Section headers with optional right content
- `Button` - Standard button component
- `Segmented` - Tab-style segmented control
- `SliderRow` - Labeled range input

**State Management:**
```javascript
const [symbol, setSymbol] = useState('TSLA');
const [expiry, setExpiry] = useState();
const [strike, setStrike] = useState();
const [rangePct, setRangePct] = useState(15);
const [ivPct, setIvPct] = useState(25);
const [price, setPrice] = useState(null);
const [pLoading, setPLoading] = useState(false);
const [error, setError] = useState('');
```

**Data Flow:**
1. User selects symbol → fetch expirations (mock)
2. User selects expiry → fetch strikes (mock)
3. User selects strike → debounced pricing call (real API)
4. Pricing updates → display metrics & greeks

## Backend Contract

### POST /api/builder/price

**Request:**
```json
{
  "symbol": "TSLA",
  "expiry": "2025-11-25",
  "legs": [{ "type": "CALL", "side": "BUY", "strike": 100 }],
  "rangePct": 15,
  "ivPct": 25
}
```

**Response (minimal):**
```json
{
  "metrics": {
    "netDebit": "$500",
    "maxLoss": "$500",
    "maxProfit": "$unlimited",
    "prob": "52%",
    "breakeven": "$105.00"
  },
  "greeks": {
    "delta": 0.55,
    "gamma": 0.03,
    "vega": 0.12,
    "rho": 0.05
  }
}
```

## Mock Data (Sprint 1)

**Expirations:**
```javascript
[
  { label:'Oct 25', date:'2025-10-25' },
  { label:'Nov 25', date:'2025-11-25' },
  { label:'Dec 25', date:'2025-12-25' }
]
```

**Strikes:**
```javascript
[80, 85, 90, 95, 100, 105, 110]
```

These will be replaced with real API calls in Sprint 2:
- `GET /api/options/expirations?symbol=TSLA`
- `GET /api/options/chain?symbol=TSLA&expiry=2025-11-25`

## Features Implemented

✅ **Symbol Input** - Uppercase auto-formatting
✅ **Expiration Selection** - Button grid with selection state
✅ **Strike Selection** - Button grid with selection state  
✅ **Debounced Pricing** - 350ms delay prevents API spam
✅ **Loading States** - "…" indicators while pricing loads
✅ **Error Display** - Banner shows API errors
✅ **Metrics Display** - 5-column grid (Net Debit, Max Loss, Max Profit, PoP, Breakeven)
✅ **Greeks Display** - 4-column grid (Delta, Gamma, Vega, Rho)
✅ **Parameters** - Range & IV sliders with live values

## Features Deferred to Sprint 2

🔲 Real expirations API
🔲 Real options chain API
🔲 Multi-leg builder (currently 1 leg)
🔲 Strategy picker (54 strategies)
🔲 P&L charts (Plotly)
🔲 Options chain table
🔲 Historical backtesting
🔲 Export/Share functionality

## UI Design

**Theme:** Neutral gray scale (Tailwind defaults)
- Background: `bg-gray-100`
- Cards: `bg-white` with `border-gray-300`
- Text: `text-gray-900` (headings), `text-gray-700` (body), `text-gray-500` (muted)
- Selected: `outline-gray-400`
- Hover: `hover:bg-gray-50`

**Layout:**
- Sticky header (top nav bar)
- 2-column grid (8/4 split on desktop)
- Left: Expirations, Strikes, Metrics, Chart placeholder
- Right: Strategy, Greeks, Parameters, Actions

**Responsive:**
- Mobile: Single column stack
- Desktop: 12-column grid with `lg:col-span-8` / `lg:col-span-4`

## Backup

Original BuilderPage backed up to:
- `frontend/src/pages/BuilderPage.NEW.jsx` (763 lines, old implementation)

Restore command if needed:
```bash
mv frontend/src/pages/BuilderPage.NEW.jsx frontend/src/pages/BuilderPage.jsx
```

## Testing

**Verify Files:**
```bash
ls -lh frontend/src/lib/{builderApi,useDebouncedEffect}.js
ls -lh frontend/src/pages/BuilderPage.jsx
```

**Check for Errors:**
```bash
cd frontend && npm run lint
```

**Run Frontend:**
```bash
cd frontend && yarn start
```

Navigate to: `http://localhost:3000/builder`

**Expected Behavior:**
1. Page loads with TSLA symbol
2. 3 expirations appear (Oct/Nov/Dec 25)
3. Clicking expiration shows 7 strikes (80-110)
4. Clicking strike triggers pricing call (will error if backend not ready)
5. Error message appears if /api/builder/price not implemented
6. Sliders adjust rangePct/ivPct and re-trigger pricing

## Next Steps (Sprint 2)

1. **Backend:** Implement minimal `/api/builder/price` mock response
2. **Frontend:** Connect to real expirations API
3. **Frontend:** Connect to real chain API
4. **Frontend:** Add multi-leg support
5. **Frontend:** Add strategy picker dropdown
6. **Frontend:** Integrate Plotly charts
7. **Frontend:** Add options chain table component

## Success Metrics

✅ File size: 276 lines (64% reduction)
✅ Imports: 3 (vs 19 before)
✅ Zero lint errors
✅ Zero compile errors
✅ Clean component hierarchy
✅ Debounced API calls (no spam)
✅ Responsive layout
✅ Accessible (ARIA labels)
✅ Loading states implemented
✅ Error handling implemented

---

**Created:** 2025-10-17
**Sprint:** 1 (Foundation)
**Status:** ✅ Complete
