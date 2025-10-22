# Strategy Card Final Design Specification

**Date:** October 22, 2025  
**Component:** `frontend/src/components/StrategyCard.jsx`  
**Backup:** `StrategyCard.backup.20251022_*.jsx`

## Visual Design Completed ✅

### Card Structure
- **Background:** `#282841` (dark purple)
- **Border:** `2px solid #4a4a6a` (medium gray)
- **Box Shadow:** `0 0 0 1px rgba(74, 74, 106, 0.3)` (subtle glow)
- **Padding:** `p-4` (16px)
- **Border Radius:** `rounded-lg`

### Typography (All Bold - fontWeight: 700)
- **Title:** "Long Call" - 1.125rem, rgba(255,255,255,0.95)
- **Description:** "Buy 195C" - 0.875rem, rgba(203,213,225,0.9)
- **Metrics:** 0.875rem with dynamic colors
- **Axis Labels:** fontSize 11, fontWeight 700, opacity 0.85

### Dynamic Color System
**Return % (Orange Gradient):**
- Formula: `getReturnColor(returnPercent)`
- 0-30%: #d97706 (dark orange)
- 30-70%: #f97316 (medium orange)
- 70-100%: #fb923c (bright orange)

**Chance % (Green Gradient):**
- Formula: `getChanceColor(chancePercent)`
- 0-40%: #86efac (light green)
- 40-70%: #4ade80 (medium green)
- 70-100%: #22c55e (dark green)

### Spacing (Compact Layout)
- Title → Legs: `mb-0.5` (2px)
- Legs → Metrics: `mb-1.5` (6px)
- Metrics Row: `mb-1.5` (6px)
- Profit/Risk: `mb-2.5` (10px)
- Chart → Button: `mb-3` (12px)

### Chart Specifications
**Dimensions:**
- Width: 360px, Height: 180px
- Padding: `{top: 10, right: -8, bottom: 45, left: 33}` (18px right shift)

**Colors:**
- Chart BG: `#1e1e35` (darker purple)
- Loss Line: `#ef4444` (red) with gradient fill
- Profit Line: `#22c55e` (green) with gradient fill
- Zero Line: white, 0.3 opacity, 1.5px solid
- Grid: white, 0.12 opacity
- Axes Frame: white, 0.25 opacity, 2px

**Gradients (45% opacity at zero line):**
- Red: Top 0% → Bottom 45% (intense at zero, fade down)
- Green: Top 45% → Bottom 0% (intense at zero, fade up)

**Vertical Lines:**
1. **Spot Price (White Dashed):** $217.26
   - Color: rgba(255,255,255,0.5)
   - Style: strokeDasharray="4 4"
   - No label

2. **Breakeven (Cyan Solid):** $220.80
   - Color: rgba(6,182,212,0.6)
   - Label: "$220.80" (cyan, top)

3. **Chance Line (Orange Solid):** In profit zone
   - Color: rgba(251,146,60,0.6)
   - Position: breakeven + (maxPrice - breakeven) * (chancePercent / 100)
   - No label

**Tick Marks:**
- Y-axis: 5px horizontal, stroke rgba(255,255,255,0.7), 2px
- X-axis: 5px vertical, stroke rgba(255,255,255,0.7), 2px

### "Open in Builder" Button
- **Background:** `#06b6d4` (cyan solid)
- **Text:** White, fontWeight 700, 0.875rem
- **Padding:** `4px 12px` (compact height)
- **Border Radius:** `rounded`
- **Display:** `inline-block` (centered)
- **Hover:** opacity 80%

## Implementation Status

### Completed Features
- ✅ P&L curve with RED/GREEN color split
- ✅ Smooth intersection at zero line
- ✅ Gradient fills (intense at zero, fading away)
- ✅ Three vertical lines (spot, breakeven, chance)
- ✅ Tick marks on both axes
- ✅ Dynamic color system for Return/Chance
- ✅ Compact spacing layout
- ✅ Bold typography (fontWeight 700)
- ✅ High contrast text (0.85-0.95 opacity)
- ✅ Cyan "Open in Builder" button
- ✅ Card border with subtle glow

### Next Steps
1. Apply this card to all 69 strategies in StrategyLibraryPage
2. Connect real P&L calculations from builder_engine.py
3. Pass dynamic data: spot price, breakeven, chance line position
4. Create Optimize tab using same card layout
5. Implement click-through to Builder with pre-filled parameters

## Testing
- **Test Page:** http://localhost:3000/card-test
- **Strategy:** Long Call (Buy 195C)
- **Metrics:** 90% Return, 45% Chance, $2,315 Profit, $2,580 Risk

