# Strategy Engine - Universal System for 69 Strategies

**Date:** October 24, 2025  
**Context:** BuilderV2Page Build tab chart complete, need scalable approach for 69 strategies

---

## 🎯 Problem Statement

**Manual approach = nightmare:**
- 69 strategies × manual implementation = months of work
- Each strategy needs: chart rendering, P&L calculation, Greeks, metrics
- StrategyCard (360x180px) → Build Tab (1000x400px) resize logic
- "Open in Builder" button requires state transfer between tabs
- Maintenance: color change → update 69 components

**User quote:** "cum crezi ca vom reusi noi sa facem cardurile pentru toate 69 de strategii si functionalitatea de open in builder sa vina in builder cu alte dimensiuni? una cate una ca imbatranim?"

---

## 🚀 Solution: Generative Strategy Engine

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Strategy Config (strategies.json)                      │
│  69 strategies defined declaratively                    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Strategy Engine (StrategyEngine.js)                    │
│  - Parse strategy definition                            │
│  - Calculate P&L curve (universal formula)              │
│  - Compute Greeks (Delta, Gamma, Theta, Vega)           │
│  - Generate breakeven, max profit/loss                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Universal Chart Component (StrategyChart.jsx)          │
│  - Accepts strategy data + size prop                    │
│  - Renders: card (360x180) OR full (1000x400)           │
│  - Same colors, gradients, tooltip logic                │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Component 1: Strategy Configuration

**File:** `frontend/src/config/strategies.json`

```json
{
  "long_call": {
    "id": "long_call",
    "name": "Long Call",
    "category": "bullish",
    "complexity": "beginner",
    "legs": [
      { 
        "type": "call", 
        "action": "buy", 
        "quantity": 1,
        "strike_offset": 0  // relative to current price
      }
    ],
    "pnl_formula": {
      "below_strike": "-premium",
      "above_strike": "(price - strike) * 100 * quantity - premium"
    },
    "breakeven": "strike + (premium / 100)",
    "max_profit": "unlimited",
    "max_loss": "premium",
    "description": "Bullish strategy with unlimited profit potential"
  },
  
  "bull_call_spread": {
    "id": "bull_call_spread",
    "name": "Bull Call Spread",
    "category": "bullish",
    "complexity": "intermediate",
    "legs": [
      { "type": "call", "action": "buy", "quantity": 1, "strike_label": "lower" },
      { "type": "call", "action": "sell", "quantity": 1, "strike_label": "higher" }
    ],
    "pnl_formula": {
      "below_lower": "net_debit",
      "between_strikes": "(price - lower_strike) * 100 - net_debit",
      "above_higher": "(higher_strike - lower_strike) * 100 - net_debit"
    },
    "breakeven": "lower_strike + (net_debit / 100)",
    "max_profit": "(higher_strike - lower_strike) * 100 - net_debit",
    "max_loss": "net_debit",
    "description": "Limited risk bullish spread"
  },
  
  "iron_condor": {
    "id": "iron_condor",
    "name": "Iron Condor",
    "category": "neutral",
    "complexity": "advanced",
    "legs": [
      { "type": "put", "action": "sell", "quantity": 1, "strike_label": "put_sell" },
      { "type": "put", "action": "buy", "quantity": 1, "strike_label": "put_buy" },
      { "type": "call", "action": "sell", "quantity": 1, "strike_label": "call_sell" },
      { "type": "call", "action": "buy", "quantity": 1, "strike_label": "call_buy" }
    ],
    "pnl_formula": {
      "segments": [
        { "range": "below_put_buy", "formula": "-(put_sell - put_buy) * 100 + net_credit" },
        { "range": "put_buy_to_put_sell", "formula": "(price - put_buy) * 100 + net_credit" },
        { "range": "put_sell_to_call_sell", "formula": "net_credit" },
        { "range": "call_sell_to_call_buy", "formula": "net_credit - (price - call_sell) * 100" },
        { "range": "above_call_buy", "formula": "-(call_buy - call_sell) * 100 + net_credit" }
      ]
    },
    "breakeven": ["put_sell - (net_credit / 100)", "call_sell + (net_credit / 100)"],
    "max_profit": "net_credit",
    "max_loss": "max(put_width, call_width) * 100 - net_credit",
    "description": "Neutral income strategy with defined risk"
  }
  
  // ... 66 more strategies
}
```

---

## ⚙️ Component 2: Strategy Engine

**File:** `frontend/src/services/StrategyEngine.js`

```javascript
/**
 * StrategyEngine - Universal P&L calculator for all strategies
 */
class StrategyEngine {
  constructor(strategyConfig) {
    this.config = strategyConfig;
    this.strikePrice = null;
    this.premium = null;
    this.legs = [];
  }

  /**
   * Initialize strategy with market data
   */
  initialize(currentPrice, optionsChain, expiryDate) {
    // Fetch strikes and premiums from options chain
    this.legs = this.config.legs.map(leg => ({
      ...leg,
      strike: this.calculateStrike(currentPrice, leg),
      premium: this.fetchPremium(optionsChain, leg)
    }));
    
    // Calculate net debit/credit
    this.netCost = this.calculateNetCost();
  }

  /**
   * Generate P&L curve across price range
   */
  generatePnLCurve(priceMin, priceMax, step = 1) {
    const points = [];
    
    for (let price = priceMin; price <= priceMax; price += step) {
      const pnl = this.calculatePnL(price);
      points.push({ price, pnl });
    }
    
    return points;
  }

  /**
   * Calculate P&L at specific price (universal formula parser)
   */
  calculatePnL(price) {
    const formula = this.getFormulaForPrice(price);
    return this.evaluateFormula(formula, price);
  }

  /**
   * Determine which formula segment applies to current price
   */
  getFormulaForPrice(price) {
    const { pnl_formula } = this.config;
    
    if (pnl_formula.segments) {
      // Multi-segment strategy (e.g., Iron Condor)
      for (const segment of pnl_formula.segments) {
        if (this.isPriceInRange(price, segment.range)) {
          return segment.formula;
        }
      }
    } else {
      // Simple strategy (e.g., Long Call)
      const strike = this.legs[0].strike;
      return price < strike ? pnl_formula.below_strike : pnl_formula.above_strike;
    }
  }

  /**
   * Evaluate formula string with variable substitution
   */
  evaluateFormula(formula, price) {
    const vars = {
      price,
      premium: this.netCost,
      strike: this.legs[0]?.strike,
      quantity: this.legs[0]?.quantity || 1,
      // ... all strike labels from legs
    };
    
    // Replace variables and eval safely (or use math.js)
    return this.safeEval(formula, vars);
  }

  /**
   * Calculate Greeks (universal for all strategies)
   */
  calculateGreeks(currentPrice, volatility, daysToExpiry) {
    // Black-Scholes for each leg, sum results
    return this.legs.reduce((acc, leg) => {
      const legGreeks = this.blackScholes(leg, currentPrice, volatility, daysToExpiry);
      return {
        delta: acc.delta + legGreeks.delta * leg.quantity * (leg.action === 'buy' ? 1 : -1),
        gamma: acc.gamma + legGreeks.gamma * leg.quantity * (leg.action === 'buy' ? 1 : -1),
        theta: acc.theta + legGreeks.theta * leg.quantity * (leg.action === 'buy' ? 1 : -1),
        vega: acc.vega + legGreeks.vega * leg.quantity * (leg.action === 'buy' ? 1 : -1),
      };
    }, { delta: 0, gamma: 0, theta: 0, vega: 0 });
  }

  /**
   * Calculate breakeven price(s)
   */
  calculateBreakeven() {
    const { breakeven } = this.config;
    
    if (Array.isArray(breakeven)) {
      // Multiple breakevens (e.g., Iron Condor)
      return breakeven.map(formula => this.evaluateFormula(formula, null));
    } else {
      // Single breakeven
      return [this.evaluateFormula(breakeven, null)];
    }
  }

  /**
   * Get strategy metrics
   */
  getMetrics() {
    return {
      name: this.config.name,
      category: this.config.category,
      maxProfit: this.evaluateFormula(this.config.max_profit, null),
      maxLoss: this.evaluateFormula(this.config.max_loss, null),
      breakeven: this.calculateBreakeven(),
      netCost: this.netCost,
      collateral: this.calculateCollateral(),
      legs: this.legs
    };
  }
}

export default StrategyEngine;
```

---

## 🎨 Component 3: Universal Chart Component

**File:** `frontend/src/components/StrategyChart.jsx`

```javascript
import React, { useState } from 'react';

/**
 * StrategyChart - Renders P&L chart for ANY strategy
 * Supports two sizes: "card" (360x180) and "full" (1000x400)
 */
export default function StrategyChart({ 
  strategyId, 
  currentPrice, 
  optionsChain, 
  expiryDate,
  size = 'card' // 'card' | 'full'
}) {
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, price: 0, pnl: 0 });

  // Load strategy config and initialize engine
  const strategyConfig = STRATEGIES[strategyId]; // from strategies.json
  const engine = new StrategyEngine(strategyConfig);
  engine.initialize(currentPrice, optionsChain, expiryDate);

  // Generate P&L curve
  const priceRange = { min: currentPrice * 0.5, max: currentPrice * 1.5 };
  const pnlData = engine.generatePnLCurve(priceRange.min, priceRange.max, 2);

  // Get metrics
  const metrics = engine.getMetrics();

  // Chart dimensions based on size
  const dimensions = size === 'card' 
    ? { width: 360, height: 180, padding: { top: 10, right: 5, bottom: 30, left: 35 } }
    : { width: 1000, height: 400, padding: { top: 20, right: 1, bottom: 40, left: 70 } };

  // Calculate Y-axis range (auto-scale based on P&L data)
  const yMin = Math.min(...pnlData.map(d => d.pnl)) * 1.2;
  const yMax = Math.max(...pnlData.map(d => d.pnl)) * 1.2;

  // Split into profit/loss sections (same logic as BuilderV2Page)
  const { lossPoints, profitPoints } = splitPnLData(pnlData);

  return (
    <div className={`relative bg-[#0d1230] rounded-lg ${size === 'card' ? 'h-[180px]' : 'h-[400px]'}`}>
      <svg 
        width="100%" 
        height={dimensions.height}
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        preserveAspectRatio="none"
        onMouseMove={(e) => handleMouseMove(e, dimensions, priceRange, engine)}
        onMouseLeave={() => setTooltip({ show: false })}
      >
        {/* Gradients (cyan profit, red loss) */}
        <defs>
          <linearGradient id="cyanGradient">
            <stop offset="0%" stopColor="rgba(6, 182, 212, 0.85)" />
            <stop offset="100%" stopColor="rgba(6, 182, 212, 0)" />
          </linearGradient>
          <linearGradient id="redGradient">
            <stop offset="0%" stopColor="rgba(220, 38, 38, 0.85)" />
            <stop offset="100%" stopColor="rgba(220, 38, 38, 0)" />
          </linearGradient>
        </defs>

        {/* Y-axis grid and labels */}
        {renderYAxis(dimensions, yMin, yMax)}

        {/* X-axis grid and labels */}
        {renderXAxis(dimensions, priceRange)}

        {/* Zero line */}
        <line 
          x1={dimensions.padding.left} 
          y1={scaleY(0, dimensions, yMin, yMax)}
          x2={dimensions.width - dimensions.padding.right} 
          y2={scaleY(0, dimensions, yMin, yMax)}
          stroke="white" 
          strokeWidth="1.5" 
        />

        {/* Current price line (dashed white) */}
        <line 
          x1={scaleX(currentPrice, dimensions, priceRange)}
          y1={dimensions.padding.top}
          x2={scaleX(currentPrice, dimensions, priceRange)}
          y2={dimensions.height - dimensions.padding.bottom}
          stroke="rgba(255, 255, 255, 0.5)"
          strokeDasharray="3 3"
          strokeWidth="2"
        />

        {/* Breakeven line(s) (cyan) */}
        {metrics.breakeven.map((be, idx) => (
          <line 
            key={idx}
            x1={scaleX(be, dimensions, priceRange)}
            y1={dimensions.padding.top}
            x2={scaleX(be, dimensions, priceRange)}
            y2={dimensions.height - dimensions.padding.bottom}
            stroke="rgba(6, 182, 212, 0.6)"
            strokeWidth="1.5"
          />
        ))}

        {/* Loss section (red) */}
        {lossPoints.length > 0 && (
          <>
            <path d={generatePath(lossPoints, dimensions, priceRange, yMin, yMax)} 
                  stroke="#dc2626" strokeWidth="2.5" fill="none" />
            <path d={generatePath(lossPoints, dimensions, priceRange, yMin, yMax) + closePath} 
                  fill="url(#redGradient)" />
          </>
        )}

        {/* Profit section (cyan) */}
        {profitPoints.length > 0 && (
          <>
            <path d={generatePath(profitPoints, dimensions, priceRange, yMin, yMax)} 
                  stroke="#06b6d4" strokeWidth="2.5" fill="none" />
            <path d={generatePath(profitPoints, dimensions, priceRange, yMin, yMax) + closePath} 
                  fill="url(#cyanGradient)" />
          </>
        )}

        {/* Mouse tracking line and dot */}
        {tooltip.show && (
          <>
            <line x1={tooltip.viewBoxX} y1={dimensions.padding.top} 
                  x2={tooltip.viewBoxX} y2={dimensions.height - dimensions.padding.bottom}
                  stroke="white" strokeWidth="1.5" />
            <text x={tooltip.viewBoxX} y={dimensions.padding.top - 5} 
                  fill="white" fontSize="11" textAnchor="middle">
              ${tooltip.price.toFixed(2)}
            </text>
            <circle cx={tooltip.viewBoxX} 
                    cy={scaleY(tooltip.pnl, dimensions, yMin, yMax)}
                    r="5" 
                    fill={tooltip.pnl >= 0 ? "#06b6d4" : "#dc2626"}
                    stroke="white" strokeWidth="2" />
          </>
        )}
      </svg>

      {/* Tooltip for P&L */}
      {tooltip.show && (
        <div 
          className="absolute z-50 pointer-events-none"
          style={{
            left: `${((tooltip.viewBoxX) / dimensions.width) * 100}%`,
            top: `${(scaleY(tooltip.pnl, dimensions, yMin, yMax) / dimensions.height) * 100}%`,
            transform: 'translate(10px, -50%)',
          }}
        >
          <div className={`rounded-lg px-2 py-1 shadow-xl ${tooltip.pnl >= 0 ? 'bg-cyan-600' : 'bg-red-600'}`}>
            <div className="text-white text-xs font-bold whitespace-nowrap">
              {tooltip.pnl >= 0 ? '+' : ''}${tooltip.pnl.toFixed(0)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🔗 Component 4: Integration Layer

**File:** `frontend/src/components/UniversalStrategyCard.jsx`

```javascript
/**
 * UniversalStrategyCard - Reusable card for ANY strategy
 * Used in: Optimize tab, Strategy Library, Search results
 */
export default function UniversalStrategyCard({ 
  strategyId, 
  currentPrice, 
  optionsChain, 
  expiryDate,
  onOpenInBuilder 
}) {
  const strategyConfig = STRATEGIES[strategyId];
  const engine = new StrategyEngine(strategyConfig);
  engine.initialize(currentPrice, optionsChain, expiryDate);
  const metrics = engine.getMetrics();

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-4">
      {/* Strategy Name */}
      <h3 className="text-lg font-semibold text-white mb-2">{metrics.name}</h3>

      {/* Chart (360x180 card size) */}
      <StrategyChart 
        strategyId={strategyId}
        currentPrice={currentPrice}
        optionsChain={optionsChain}
        expiryDate={expiryDate}
        size="card"
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
        <div>
          <div className="text-gray-400">Max Profit</div>
          <div className="text-white font-semibold">
            {metrics.maxProfit === 'unlimited' ? 'Unlimited' : `$${metrics.maxProfit.toFixed(0)}`}
          </div>
        </div>
        <div>
          <div className="text-gray-400">Max Loss</div>
          <div className="text-white font-semibold">-${metrics.maxLoss.toFixed(0)}</div>
        </div>
        <div>
          <div className="text-gray-400">Net Cost</div>
          <div className="text-white font-semibold">${metrics.netCost.toFixed(0)}</div>
        </div>
        <div>
          <div className="text-gray-400">Breakeven</div>
          <div className="text-white font-semibold">
            ${metrics.breakeven[0].toFixed(2)}
          </div>
        </div>
      </div>

      {/* Legs Display */}
      <div className="mt-3 space-y-1">
        {metrics.legs.map((leg, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs">
            <span className={leg.action === 'buy' ? 'text-green-400' : 'text-red-400'}>
              {leg.action.toUpperCase()}
            </span>
            <span className="text-white">{leg.quantity}x</span>
            <span className="text-white">{leg.type.toUpperCase()}</span>
            <span className="text-cyan-400">${leg.strike.toFixed(2)}</span>
          </div>
        ))}
      </div>

      {/* Open in Builder Button */}
      <button
        onClick={() => onOpenInBuilder(strategyId, metrics)}
        className="w-full mt-4 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-semibold transition-colors"
      >
        Open in Builder
      </button>
    </div>
  );
}
```

**State Transfer (Optimize → Build):**

```javascript
// In BuilderV2Page.jsx
const [buildTabStrategy, setBuildTabStrategy] = useState(null);

const handleOpenInBuilder = (strategyId, metrics) => {
  // Transfer strategy to Build tab
  setBuildTabStrategy({
    id: strategyId,
    metrics,
    timestamp: Date.now()
  });
  
  // Switch to Build tab
  setActiveTab('builder');
};

// In BuilderTab
function BuilderTab({ strategy }) {
  if (strategy) {
    // Render StrategyChart with size="full" (1000x400)
    return (
      <div>
        <StrategyChart 
          strategyId={strategy.id}
          size="full"
          {...otherProps}
        />
        {/* Position management UI */}
      </div>
    );
  }
  
  // Default: manual strategy builder
  return <BuilderPage />;
}
```

---

## 📊 Benefits Summary

### ✅ **Scalability**
- **69 strategies** → defined in ~1000 lines JSON config (not 69 × 500 = 34,500 lines code)
- **Add new strategy:** 30 lines JSON, zero new components
- **Backend reusable:** Same `StrategyEngine.js` can run in Node.js for API

### ✅ **Maintainability**
- **Color change:** Update `StrategyChart.jsx` → all 69 strategies updated instantly
- **Gradient tweak:** One place (`<linearGradient>`) → propagates to all charts
- **Bug fix:** Fix once in engine → 69 strategies fixed

### ✅ **Consistency**
- **Same visual style** across card/full views (360x180 → 1000x400 auto-scaling)
- **Unified P&L calculation** (no formula drift between components)
- **Standardized tooltip** behavior (follows curve, cyan/red, percentage positioning)

### ✅ **Performance**
- **Lazy loading:** Only load strategy configs as needed
- **Memoization:** Cache P&L curves per price/expiry combination
- **Shared gradients:** SVG `<defs>` reused across multiple charts

### ✅ **Developer Experience**
- **Add strategy workflow:**
  1. Define JSON entry (30 lines)
  2. Test in Storybook with `<UniversalStrategyCard strategyId="new_strategy" />`
  3. Done ✅
- **No manual chart coding**
- **No leg-by-leg P&L debugging**

---

## 🛠️ Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create `strategies.json` with 10 core strategies (Long Call/Put, Spreads, Straddle/Strangle)
2. Build `StrategyEngine.js` core (P&L calculator, formula parser)
3. Implement `StrategyChart.jsx` with card/full size support
4. Test with existing BuilderV2Page Build tab chart

### Phase 2: Library Expansion (Week 2)
5. Add remaining 59 strategies to `strategies.json`
6. Implement Greeks calculation (Black-Scholes)
7. Add breakeven, max profit/loss auto-calculation
8. Build `UniversalStrategyCard.jsx`

### Phase 3: Integration (Week 3)
9. Replace Optimize tab mock cards with `UniversalStrategyCard`
10. Implement "Open in Builder" state transfer
11. Add Strategy Library filtering (category, complexity, risk)
12. Connect to TradeStation API for real options chain data

### Phase 4: Polish (Week 4)
13. Add chart animations (curve draw-in, tooltip transitions)
14. Implement strategy comparison (overlay multiple charts)
15. Add probability cone visualization
16. Performance optimization (memoization, virtualization for large lists)

---

## 📝 File Structure

```
frontend/src/
├── config/
│   └── strategies.json              (69 strategy definitions, ~1500 lines)
├── services/
│   └── StrategyEngine.js            (Universal P&L calculator, ~500 lines)
├── components/
│   ├── StrategyChart.jsx            (Universal chart component, ~400 lines)
│   └── UniversalStrategyCard.jsx    (Reusable card wrapper, ~150 lines)
├── pages/
│   └── BuilderV2Page.jsx            (Tab orchestration, state management)
└── hooks/
    └── useStrategyData.js           (Options chain fetching, caching)
```

**Total code:** ~2,550 lines (vs. 69 × 500 = 34,500 lines manual approach)  
**Reduction:** **93% less code** 🎉

---

## 🎯 Next Steps

1. **Approve architecture:** User confirms generative approach vs. manual
2. **Start with Phase 1:** 10 strategies + engine core
3. **Validate with Build tab:** Ensure StrategyChart matches current chart quality
4. **Iterate based on feedback:** Adjust formula parser, chart rendering

**Estimated timeline:** 4 weeks full implementation (vs. 6 months manual)

---

**AI Agent Ready:** Aștept confirmarea pentru a începe implementarea! 🚀
