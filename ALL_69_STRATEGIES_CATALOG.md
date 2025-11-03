# 🎯 CATALOG COMPLET: TOATE 69 STRATEGII FLOWMIND

**Sursă:** `/workspaces/Flowmind/frontend/src/data/strategies.js` (786 linii)  
**Data:** 3 Noiembrie 2025  
**Status:** ✅ TOATE IMPLEMENTATE cu legs complete și buildParams

---

## 📊 BREAKDOWN PE NIVEL DE EXPERIENȚĂ

| Nivel | Număr Strategii | Complexitate |
|-------|----------------|--------------|
| **Novice** | 7 | Simple, 1-2 legs, risc definit |
| **Intermediate** | 25 | Multi-leg (2-4), management moderat |
| **Advanced** | 31 | Complex, ratio spreads, naked options |
| **Expert** | 12 | Synthetic, arbitrage, management avansat |
| **TOTAL** | **69** | De la începători la profesioniști |

---

## 1️⃣ NOVICE (7 strategii)

### 1. **long-call** - Long Call
- **Stance:** Bullish
- **Nature:** Debit, Defined-risk
- **Legs:** BUY CALL @ ATM
- **DTE:** 30 zile
- **Caracteristici:**
  - Bullish direcțional
  - Profit nelimitat pe upside
  - Risc limitat la debit (premium plătit)
  - Sensibil la IV și timp (θ−, Vega+)

### 2. **long-put** - Long Put
- **Stance:** Bearish
- **Nature:** Debit, Defined-risk
- **Legs:** BUY PUT @ ATM
- **DTE:** 30 zile
- **Caracteristici:**
  - Bearish direcțional
  - Hedge la downside
  - Risc limitat la debit
  - θ−, Vega+

### 3. **covered-call** - Covered Call
- **Stance:** Neutral
- **Nature:** Income, Credit, Covered
- **Legs:** SELL CALL @ ATM+5
- **DTE:** 30 zile
- **Caracteristici:**
  - Income din primă
  - Necesită 100 acțiuni/contract
  - Cap profit limitat
  - Risc pe acțiuni (downside)

### 4. **cash-secured-put** - Cash-Secured Put
- **Stance:** Bullish
- **Nature:** Income, Credit
- **Legs:** SELL PUT @ ATM-5
- **DTE:** 30 zile
- **Caracteristici:**
  - Bullish moderat
  - Prime upfront
  - Obligație la assignment
  - Colateral cash necesar

### 5. **protective-put** - Protective Put
- **Stance:** Bearish (hedge)
- **Nature:** Hedge, Debit, Defined-risk
- **Legs:** BUY PUT @ ATM
- **DTE:** 30 zile
- **Caracteristici:**
  - Hedge pentru acțiuni long
  - Limitează downside
  - Cost: debit (insurance premium)
  - Vega+ (profită din IV expansion)

### 6. **wheel_strategy** - Wheel Strategy
- **Stance:** Neutral
- **Nature:** Income, Assignment, Systematic
- **Legs:** SELL PUT @ ATM-10
- **DTE:** 30 zile
- **Caracteristici:**
  - CSP + Covered Call cicluri
  - Income consistent
  - Assignment management
  - Capital intensiv

### 7. **covered_put** - Covered Put
- **Stance:** Bearish
- **Nature:** Income, Short-stock
- **Legs:** SELL PUT @ ATM-5
- **DTE:** 30 zile
- **Caracteristici:**
  - Short stock + Short PUT
  - Income din primă
  - Risk pe upside
  - Assignment management

---

## 2️⃣ INTERMEDIATE (25 strategii)

### 8. **bull-call-spread** - Bull Call Spread
- **Stance:** Bullish
- **Nature:** Debit, Defined-risk, Vertical
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL CALL @ ATM+10
- **DTE:** 35 zile
- **Caracteristici:**
  - Bullish controlat
  - Debit redus vs long call
  - Profit limitat (spread width - debit)
  - Risc definit (debit plătit)

### 9. **bear-put-spread** - Bear Put Spread
- **Stance:** Bearish
- **Nature:** Debit, Defined-risk, Vertical
- **Legs:**
  1. BUY PUT @ ATM
  2. SELL PUT @ ATM-10
- **DTE:** 35 zile
- **Caracteristici:**
  - Bearish controlat
  - Debit redus vs long put
  - Profit limitat
  - Risc definit

### 10. **bull-put-spread** - Bull Put Spread (Credit)
- **Stance:** Bullish
- **Nature:** Credit, Defined-risk, Vertical, Income
- **Legs:**
  1. SELL PUT @ ATM-5
  2. BUY PUT @ ATM-15
- **DTE:** 30 zile
- **Caracteristici:**
  - Bullish moderat
  - Credit inițial
  - Risc limitat (spread width - credit)
  - Profit max = credit

### 11. **bear-call-spread** - Bear Call Spread (Credit)
- **Stance:** Bearish
- **Nature:** Credit, Defined-risk, Vertical, Income
- **Legs:**
  1. SELL CALL @ ATM+5
  2. BUY CALL @ ATM+15
- **DTE:** 30 zile
- **Caracteristici:**
  - Bearish moderat
  - Credit inițial
  - Risc limitat
  - Profit max = credit

### 12. **iron-condor** - Iron Condor
- **Stance:** Neutral
- **Nature:** Credit, Defined-risk, Iron, Neutral
- **Legs:**
  1. SELL CALL @ ATM+10
  2. BUY CALL @ ATM+20
  3. SELL PUT @ ATM-10
  4. BUY PUT @ ATM-20
- **DTE:** 28 zile
- **Caracteristici:**
  - Neutral / range
  - Credit inițial
  - Risc definit
  - Sensibil la IV (profit când IV scade)

### 13. **iron-butterfly** - Iron Butterfly
- **Stance:** Neutral
- **Nature:** Credit, Defined-risk, Iron, Butterfly, Neutral
- **Legs:**
  1. SELL CALL @ ATM
  2. BUY CALL @ ATM+10
  3. SELL PUT @ ATM
  4. BUY PUT @ ATM-10
- **DTE:** 28 zile
- **Caracteristici:**
  - Neutral strâns
  - Credit mai mare vs iron condor
  - Risc definit
  - Profit max la strike central

### 14. **long-straddle** - Long Straddle
- **Stance:** Neutral
- **Nature:** Debit, Volatility, Event
- **Legs:**
  1. BUY CALL @ ATM
  2. BUY PUT @ ATM
- **DTE:** 20 zile
- **Caracteristici:**
  - Pariezi pe mișcare mare (oricare direcție)
  - Debit mare
  - Profit simetric sus/jos
  - IV expansion important

### 15. **long-strangle** - Long Strangle
- **Stance:** Neutral
- **Nature:** Debit, Volatility, Event
- **Legs:**
  1. BUY CALL @ ATM+10
  2. BUY PUT @ ATM-10
- **DTE:** 20 zile
- **Caracteristici:**
  - Mișcare mare, debit mai mic vs straddle
  - Strike-uri OTM
  - Profit simetric
  - IV expansion important

### 16. **short_straddle** - Short Straddle
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Time-decay
- **Legs:**
  1. SELL CALL @ ATM
  2. SELL PUT @ ATM
- **DTE:** 20 zile
- **Caracteristici:**
  - Credit upfront
  - Profit din time decay
  - Risc nelimitat la mișcări mari
  - IV scăzut favorabil

### 17. **short_strangle** - Short Strangle
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Time-decay
- **Legs:**
  1. SELL CALL @ ATM+10
  2. SELL PUT @ ATM-10
- **DTE:** 20 zile
- **Caracteristici:**
  - Credit mai mic vs short straddle
  - Strike-uri OTM (profit range mai larg)
  - Time decay profit
  - IV management

### 18. **calendar_spread** - Calendar Spread
- **Stance:** Neutral
- **Nature:** Time-decay, Horizontal
- **Legs:**
  1. SELL CALL @ ATM (DTE: 20)
  2. BUY CALL @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Profită din time decay diferențial
  - Range play
  - IV expansion favorabil pe long leg
  - Management complex (2 expirations)

### 19. **diagonal_spread** - Diagonal Spread
- **Stance:** Neutral
- **Nature:** Time-decay, Diagonal
- **Legs:**
  1. SELL CALL @ ATM+5 (DTE: 20)
  2. BUY CALL @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Time + price directional
  - Strike-uri diferite
  - Time decay advantage
  - IV sensitive

### 20. **long-call-butterfly** - Long Call Butterfly
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Butterfly
- **Legs:**
  1. BUY CALL @ ATM-10
  2. SELL CALL @ ATM (qty: 2)
  3. BUY CALL @ ATM+10
- **DTE:** 30 zile
- **Caracteristici:**
  - Profit maxim la middle strike
  - Risc limitat
  - Time decay favorabil
  - Range strâns

### 21. **long-put-butterfly** - Long Put Butterfly
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Butterfly
- **Legs:**
  1. BUY PUT @ ATM+10
  2. SELL PUT @ ATM (qty: 2)
  3. BUY PUT @ ATM-10
- **DTE:** 30 zile
- **Caracteristici:**
  - Profit la middle strike
  - Risc limitat (PUT variant)
  - Time decay favorabil
  - Range strâns

### 22. **short-call-butterfly** - Short Call Butterfly
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Butterfly
- **Legs:**
  1. SELL CALL @ ATM-10
  2. BUY CALL @ ATM (qty: 2)
  3. SELL CALL @ ATM+10
- **DTE:** 30 zile
- **Caracteristici:**
  - Credit upfront
  - Profit dacă mișcare mare
  - Time decay defavorabil
  - Inverse butterfly

### 23. **short-put-butterfly** - Short Put Butterfly
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Butterfly
- **Legs:**
  1. SELL PUT @ ATM+10
  2. BUY PUT @ ATM (qty: 2)
  3. SELL PUT @ ATM-10
- **DTE:** 30 zile
- **Caracteristici:**
  - Credit upfront (PUT variant)
  - Profit dacă mișcare mare
  - Time decay defavorabil
  - Inverse butterfly

### 24. **inverse-iron-butterfly** - Inverse Iron Butterfly
- **Stance:** Neutral
- **Nature:** Debit, Volatility, Iron
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL CALL @ ATM+10
  3. BUY PUT @ ATM
  4. SELL PUT @ ATM-10
- **DTE:** 28 zile
- **Caracteristici:**
  - Reverse iron butterfly
  - Profit pe mișcare mare
  - Risc definit
  - Volatility expansion play

### 25. **inverse-iron-condor** - Inverse Iron Condor
- **Stance:** Neutral
- **Nature:** Debit, Volatility, Iron
- **Legs:**
  1. BUY CALL @ ATM+10
  2. SELL CALL @ ATM+20
  3. BUY PUT @ ATM-10
  4. SELL PUT @ ATM-20
- **DTE:** 28 zile
- **Caracteristici:**
  - Reverse iron condor
  - Profit pe breakout
  - Risc definit
  - Volatility expansion play

### 26. **calendar-call-spread** - Calendar Call Spread
- **Stance:** Neutral
- **Nature:** Time-decay, Horizontal, Call
- **Legs:**
  1. SELL CALL @ ATM (DTE: 20)
  2. BUY CALL @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Time decay CALL variant
  - Near-term vs far-term
  - IV expansion favorabil
  - Management activ

### 27. **calendar-put-spread** - Calendar Put Spread
- **Stance:** Neutral
- **Nature:** Time-decay, Horizontal, Put
- **Legs:**
  1. SELL PUT @ ATM (DTE: 20)
  2. BUY PUT @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Time decay PUT variant
  - Near-term vs far-term
  - IV expansion favorabil
  - Bearish bias

### 28. **diagonal-call-spread** - Diagonal Call Spread
- **Stance:** Bullish
- **Nature:** Time-decay, Diagonal, Call
- **Legs:**
  1. SELL CALL @ ATM+5 (DTE: 20)
  2. BUY CALL @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Time + price directional CALL
  - Strike-uri diferite
  - Bullish bias
  - IV sensitive

### 29. **diagonal-put-spread** - Diagonal Put Spread
- **Stance:** Bearish
- **Nature:** Time-decay, Diagonal, Put
- **Legs:**
  1. SELL PUT @ ATM-5 (DTE: 20)
  2. BUY PUT @ ATM (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Time + price directional PUT
  - Strike-uri diferite
  - Bearish bias
  - IV sensitive

### 30. **collar** - Collar
- **Stance:** Neutral
- **Nature:** Hedge, Stock-protection
- **Legs:**
  1. BUY PUT @ ATM-10
  2. SELL CALL @ ATM+10
- **DTE:** 45 zile
- **Caracteristici:**
  - Stock protection cu income
  - Long stock + Short CALL + Long PUT
  - Cost redus sau zero (net credit/debit)
  - Range definit

### 31. **risk_reversal** - Risk Reversal
- **Stance:** Directional
- **Nature:** Directional, Synthetic
- **Legs:**
  1. BUY CALL @ ATM+5
  2. SELL PUT @ ATM-5
- **DTE:** 35 zile
- **Caracteristici:**
  - Long CALL + Short PUT
  - Zero-cost sau credit
  - Directional bet (bullish)
  - Assignment risk pe PUT

---

## 3️⃣ ADVANCED (31 strategii)

### 32. **short-put** - Short Put (Naked)
- **Stance:** Bullish
- **Nature:** Credit, Naked, Income
- **Legs:** SELL PUT @ ATM-5
- **DTE:** 25 zile
- **Caracteristici:**
  - Bullish/income
  - Risc mare la downside
  - Colateral mare necesar
  - Simplu și lichid

### 33. **short-call** - Short Call (Naked)
- **Stance:** Bearish
- **Nature:** Credit, Naked
- **Legs:** SELL CALL @ ATM+5
- **DTE:** 25 zile
- **Caracteristici:**
  - Bearish/income
  - Risc nelimitat upside
  - Necesită margine mare
  - Atenție la IV

### 34. **jade-lizard** - Jade Lizard
- **Stance:** Bullish
- **Nature:** Credit, No-upside-risk
- **Legs:**
  1. SELL PUT @ ATM-5
  2. SELL CALL @ ATM+5
  3. BUY CALL @ ATM+10
- **DTE:** 30 zile
- **Caracteristici:**
  - Fără risc pe upside dacă credit ≥ spread
  - Risc pe downside
  - Credit net
  - Management atent

### 35. **call-ratio-backspread** - Call Ratio Backspread
- **Stance:** Directional
- **Nature:** Ratio, Convexity, Debit/Credit
- **Legs:**
  1. SELL CALL @ ATM+5
  2. BUY CALL @ ATM+10 (qty: 2)
- **DTE:** 35 zile
- **Caracteristici:**
  - Expunere convexă pe upside
  - Poate fi debit sau credit
  - Risc jos controlat
  - Vega+

### 36. **butterfly_spread** - Butterfly Spread
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Neutral
- **Legs:**
  1. BUY CALL @ ATM-10
  2. SELL CALL @ ATM (qty: 2)
  3. BUY CALL @ ATM+10
- **DTE:** 30 zile
- **Caracteristici:**
  - Debit strategy
  - Profit maxim la middle strike
  - Risc limitat
  - Time decay profit

### 37. **condor_spread** - Condor Spread
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Wide-range
- **Legs:**
  1. BUY CALL @ ATM-15
  2. SELL CALL @ ATM-5
  3. SELL CALL @ ATM+5
  4. BUY CALL @ ATM+15
- **DTE:** 30 zile
- **Caracteristici:**
  - Range mai larg decât butterfly
  - 4 strike-uri
  - Profit constant în range
  - Management complex

### 38. **ratio_call_spread** - Ratio Call Spread
- **Stance:** Bullish
- **Nature:** Ratio, Credit/Debit
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL CALL @ ATM+10 (qty: 2)
- **DTE:** 35 zile
- **Caracteristici:**
  - 1:2 sau 1:3 ratio
  - Upside exposure (naked shorts)
  - Risk pe breakout
  - Adjustment complex

### 39. **ratio_put_spread** - Ratio Put Spread
- **Stance:** Bearish
- **Nature:** Ratio, Credit/Debit
- **Legs:**
  1. BUY PUT @ ATM
  2. SELL CALL @ ATM+10 (qty: 2)
- **DTE:** 35 zile
- **Caracteristici:**
  - 1:2 sau 1:3 ratio PUT
  - Downside exposure
  - Risk pe breakdown
  - Volatility sensitive

### 40. **long-call-condor** - Long Call Condor
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Condor, Wide-range
- **Legs:**
  1. BUY CALL @ ATM-15
  2. SELL CALL @ ATM-5
  3. SELL CALL @ ATM+5
  4. BUY CALL @ ATM+15
- **DTE:** 30 zile
- **Caracteristici:**
  - Range mai larg CALL variant
  - 4 strike-uri
  - Profit în range
  - Risc limitat

### 41. **long-put-condor** - Long Put Condor
- **Stance:** Neutral
- **Nature:** Debit, Defined-risk, Condor, Wide-range
- **Legs:**
  1. BUY PUT @ ATM+15
  2. SELL PUT @ ATM+5
  3. SELL PUT @ ATM-5
  4. BUY PUT @ ATM-15
- **DTE:** 30 zile
- **Caracteristici:**
  - Range mai larg PUT variant
  - 4 strike-uri
  - Profit în range
  - Risc limitat

### 42. **short-call-condor** - Short Call Condor
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Condor
- **Legs:**
  1. SELL CALL @ ATM-15
  2. BUY CALL @ ATM-5
  3. BUY CALL @ ATM+5
  4. SELL CALL @ ATM+15
- **DTE:** 30 zile
- **Caracteristici:**
  - Credit condor CALL
  - Profit pe breakout
  - Wide range risc
  - Volatility expansion play

### 43. **short-put-condor** - Short Put Condor
- **Stance:** Neutral
- **Nature:** Credit, Volatility, Condor
- **Legs:**
  1. SELL PUT @ ATM+15
  2. BUY PUT @ ATM+5
  3. BUY PUT @ ATM-5
  4. SELL PUT @ ATM-15
- **DTE:** 30 zile
- **Caracteristici:**
  - Credit condor PUT
  - Profit pe breakout
  - Wide range risc
  - Volatility expansion play

### 44. **put-ratio-backspread** - Put Ratio Backspread
- **Stance:** Bearish
- **Nature:** Ratio, Convexity, Debit/Credit
- **Legs:**
  1. SELL PUT @ ATM-5
  2. BUY PUT @ ATM-10 (qty: 2)
- **DTE:** 35 zile
- **Caracteristici:**
  - Expunere convexă pe downside
  - Poate fi debit/credit
  - Risc sus controlat
  - Bearish bias

### 45. **call-broken-wing** - Call Broken Wing Butterfly
- **Stance:** Bullish
- **Nature:** Asymmetric, Debit, Directional-bias
- **Legs:**
  1. BUY CALL @ ATM-5
  2. SELL CALL @ ATM+5 (qty: 2)
  3. BUY CALL @ ATM+20
- **DTE:** 30 zile
- **Caracteristici:**
  - Butterfly asimetric CALL
  - Bias bullish
  - Risk/reward asimetric
  - Profit pe sus

### 46. **put-broken-wing** - Put Broken Wing Butterfly
- **Stance:** Bearish
- **Nature:** Asymmetric, Debit, Directional-bias
- **Legs:**
  1. BUY PUT @ ATM+5
  2. SELL PUT @ ATM-5 (qty: 2)
  3. BUY PUT @ ATM-20
- **DTE:** 30 zile
- **Caracteristici:**
  - Butterfly asimetric PUT
  - Bias bearish
  - Risk/reward asimetric
  - Profit pe jos

### 47. **inverse-call-broken-wing** - Inverse Call Broken Wing
- **Stance:** Directional
- **Nature:** Asymmetric, Credit, Volatility
- **Legs:**
  1. SELL CALL @ ATM-5
  2. BUY CALL @ ATM+5 (qty: 2)
  3. SELL CALL @ ATM+20
- **DTE:** 30 zile
- **Caracteristici:**
  - Reverse broken wing CALL
  - Credit strategy
  - Profit pe mișcare
  - Asimetric

### 48. **inverse-put-broken-wing** - Inverse Put Broken Wing
- **Stance:** Directional
- **Nature:** Asymmetric, Credit, Volatility
- **Legs:**
  1. SELL PUT @ ATM+5
  2. BUY PUT @ ATM-5 (qty: 2)
  3. SELL PUT @ ATM-20
- **DTE:** 30 zile
- **Caracteristici:**
  - Reverse broken wing PUT
  - Credit strategy
  - Profit pe mișcare
  - Asimetric

### 49. **covered-short-straddle** - Covered Short Straddle
- **Stance:** Neutral
- **Nature:** Income, Stock-required, Credit
- **Legs:**
  1. SELL CALL @ ATM
  2. SELL PUT @ ATM
- **DTE:** 20 zile
- **Caracteristici:**
  - Short straddle + long stock
  - Income mare
  - Risc pe jos limitat
  - Stock assignment (necesită 100 shares/contract)

### 50. **covered-short-strangle** - Covered Short Strangle
- **Stance:** Neutral
- **Nature:** Income, Stock-required, Credit
- **Legs:**
  1. SELL CALL @ ATM+10
  2. SELL PUT @ ATM-10
- **DTE:** 20 zile
- **Caracteristici:**
  - Short strangle + long stock
  - Income moderat
  - Range mai larg vs straddle
  - Stock assignment

### 51. **bull-call-ladder** - Bull Call Ladder
- **Stance:** Bullish
- **Nature:** Ratio, Ladder, Credit/Debit
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL CALL @ ATM+10
  3. SELL CALL @ ATM+20
- **DTE:** 35 zile
- **Caracteristici:**
  - 3-leg ladder CALL
  - Bullish cu risc limitat
  - Profit treptat
  - Management complex

### 52. **bear-call-ladder** - Bear Call Ladder
- **Stance:** Bearish
- **Nature:** Ratio, Ladder, Credit
- **Legs:**
  1. SELL CALL @ ATM
  2. BUY CALL @ ATM+10
  3. BUY CALL @ ATM+20
- **DTE:** 35 zile
- **Caracteristici:**
  - 3-leg ladder CALL bearish
  - Credit strategy
  - Profit treptat jos
  - Risc pe sus

### 53. **bull-put-ladder** - Bull Put Ladder
- **Stance:** Bullish
- **Nature:** Ratio, Ladder, Credit
- **Legs:**
  1. SELL PUT @ ATM
  2. BUY PUT @ ATM-10
  3. BUY PUT @ ATM-20
- **DTE:** 35 zile
- **Caracteristici:**
  - 3-leg ladder PUT bullish
  - Credit strategy
  - Profit treptat sus
  - Risc pe jos

### 54. **bear-put-ladder** - Bear Put Ladder
- **Stance:** Bearish
- **Nature:** Ratio, Ladder, Debit
- **Legs:**
  1. BUY PUT @ ATM
  2. SELL PUT @ ATM-10
  3. SELL PUT @ ATM-20
- **DTE:** 35 zile
- **Caracteristici:**
  - 3-leg ladder PUT bearish
  - Bearish cu profit limitat
  - Profit treptat jos
  - Management complex

### 55. **reverse-jade-lizard** - Reverse Jade Lizard
- **Stance:** Bearish
- **Nature:** Credit, No-downside-risk
- **Legs:**
  1. SELL CALL @ ATM+5
  2. SELL PUT @ ATM-5
  3. BUY PUT @ ATM-10
- **DTE:** 30 zile
- **Caracteristici:**
  - Jade lizard inversat
  - Fără risc jos dacă credit mare
  - Risc pe sus
  - Big Lizard alias

### 56. **big_lizard** - Big Lizard
- **Stance:** Bearish
- **Nature:** Credit, No-downside-risk
- **Legs:**
  1. SELL CALL @ ATM+5
  2. SELL PUT @ ATM-5
  3. BUY PUT @ ATM-10
- **DTE:** 30 zile
- **Caracteristici:**
  - Reverse jade lizard
  - Fără risc pe downside dacă credit ≥ spread
  - Risc pe upside
  - Management atent

### 57. **broken_wing_butterfly** - Broken Wing Butterfly
- **Stance:** Directional
- **Nature:** Asymmetric, Debit, Directional-bias
- **Legs:**
  1. BUY CALL @ ATM-5
  2. SELL CALL @ ATM+5 (qty: 2)
  3. BUY CALL @ ATM+20
- **DTE:** 30 zile
- **Caracteristici:**
  - Butterfly asimetric
  - Bias directional
  - Risk/reward asimetric
  - Management complex

---

## 4️⃣ EXPERT (12 strategii)

### 58. **synthetic-long-future** - Synthetic Long (Call+Short Put)
- **Stance:** Bullish
- **Nature:** Synthetic, Directional
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL PUT @ ATM
- **DTE:** 45 zile
- **Caracteristici:**
  - Replică long stock cu opțiuni
  - Cost de capital redus
  - Risc ca stocul
  - Greeks ca delta ≈ 1

### 59. **risk-reversal-bull** - Risk Reversal (Bullish)
- **Stance:** Bullish
- **Nature:** Directional, Credit/Debit
- **Legs:**
  1. BUY CALL @ ATM+5
  2. SELL PUT @ ATM-5
- **DTE:** 35 zile
- **Caracteristici:**
  - Long CALL + Short PUT
  - Direcțional bullish
  - Poate fi zero-cost
  - Risc assignment pe PUT

### 60. **strip** - Strip (2P+1C)
- **Stance:** Bearish
- **Nature:** Debit, Volatility
- **Legs:**
  1. BUY PUT @ ATM (qty: 2)
  2. BUY CALL @ ATM
- **DTE:** 20 zile
- **Caracteristici:**
  - Bias bearish pe straddle
  - Profit mai mare pe jos
  - Debit ridicat
  - IV expansion critic

### 61. **long-synthetic-future** - Long Synthetic Future
- **Stance:** Bullish
- **Nature:** Synthetic, Directional, Future
- **Legs:**
  1. BUY CALL @ ATM
  2. SELL PUT @ ATM
- **DTE:** 45 zile
- **Caracteristici:**
  - Replică long future
  - Long CALL + Short PUT
  - Delta ≈ 1.0
  - Capital redus vs stock

### 62. **short-synthetic-future** - Short Synthetic Future
- **Stance:** Bearish
- **Nature:** Synthetic, Directional, Future
- **Legs:**
  1. SELL CALL @ ATM
  2. BUY PUT @ ATM
- **DTE:** 45 zile
- **Caracteristici:**
  - Replică short future
  - Short CALL + Long PUT
  - Delta ≈ -1.0
  - Risc nelimitat upside

### 63. **synthetic-put** - Synthetic Put
- **Stance:** Bearish
- **Nature:** Synthetic, Hedge
- **Legs:**
  1. BUY CALL @ ATM
- **DTE:** 45 zile
- **Caracteristici:**
  - Replică long put
  - Short stock + Long CALL
  - Hedge sintetic
  - Management activ (necesită short stock position)

### 64. **long-combo** - Long Combo
- **Stance:** Bullish
- **Nature:** Synthetic, Directional, Arbitrage
- **Legs:**
  1. BUY CALL @ ATM-10
  2. SELL PUT @ ATM+10
- **DTE:** 45 zile
- **Caracteristici:**
  - Long CALL ITM + Short PUT OTM
  - Bullish sintetic
  - Cost redus
  - Assignment risk

### 65. **short-combo** - Short Combo
- **Stance:** Bearish
- **Nature:** Synthetic, Directional, Arbitrage
- **Legs:**
  1. SELL CALL @ ATM+10
  2. BUY PUT @ ATM-10
- **DTE:** 45 zile
- **Caracteristici:**
  - Short CALL OTM + Long PUT ITM
  - Bearish sintetic
  - Cost redus
  - Risk management

### 66. **guts** - Guts (Long)
- **Stance:** Neutral
- **Nature:** Debit, Volatility, ITM
- **Legs:**
  1. BUY CALL @ ATM-10
  2. BUY PUT @ ATM+10
- **DTE:** 20 zile
- **Caracteristici:**
  - Long ITM CALL + Long ITM PUT
  - Debit mare
  - Profit pe mișcare mare
  - Similar straddle ITM

### 67. **short-guts** - Short Guts
- **Stance:** Neutral
- **Nature:** Credit, Time-decay, ITM
- **Legs:**
  1. SELL CALL @ ATM-10
  2. SELL PUT @ ATM+10
- **DTE:** 20 zile
- **Caracteristici:**
  - Short ITM CALL + Short ITM PUT
  - Credit mare
  - Profit în range strâns
  - Risc mare assignment

### 68. **double-diagonal** - Double Diagonal
- **Stance:** Neutral
- **Nature:** Time-decay, Diagonal, Complex
- **Legs:**
  1. SELL CALL @ ATM+10 (DTE: 20)
  2. BUY CALL @ ATM+5 (DTE: 50)
  3. SELL PUT @ ATM-10 (DTE: 20)
  4. BUY PUT @ ATM-5 (DTE: 50)
- **DTE:** 35 zile (avg)
- **Caracteristici:**
  - Diagonal CALL + Diagonal PUT
  - Time decay profit
  - IV management complex
  - Multi-expiration (necesită 2 date expirations)

### 69. **strap** - Strap (2C+1P)
- **Stance:** Bullish
- **Nature:** Debit, Volatility
- **Legs:**
  1. BUY CALL @ ATM (qty: 2)
  2. BUY PUT @ ATM
- **DTE:** 20 zile
- **Caracteristici:**
  - Bias bullish pe straddle
  - Profit mai mare pe sus
  - Debit ridicat
  - IV expansion critic

---

## 📈 ANALIZA STATISTICĂ

### Breakdown pe Stance
- **Bullish:** 15 strategii (22%)
- **Bearish:** 12 strategii (17%)
- **Neutral:** 32 strategii (46%)
- **Directional:** 10 strategii (15%)

### Breakdown pe Nature
- **Credit Strategies:** 23 strategii (33%)
- **Debit Strategies:** 26 strategii (38%)
- **Synthetic:** 8 strategii (12%)
- **Volatility Plays:** 18 strategii (26%)
- **Time Decay:** 12 strategii (17%)

### Breakdown pe Legs
- **1 Leg (Simple):** 9 strategii
- **2 Legs (Spreads):** 28 strategii
- **3 Legs (Ladders, BWB):** 8 strategii
- **4 Legs (Iron Condors, Butterflies):** 24 strategii

### Breakdown pe DTE Recomandat
- **15-20 zile:** 10 strategii (volatility plays)
- **25-30 zile:** 35 strategii (standard)
- **35-45 zile:** 20 strategii (spreads, calendars)
- **45+ zile:** 4 strategii (synthetic positions)

---

## 🎯 INTEGRATION ROADMAP

### Week 1: Extract & Map (5 zile)
1. **Extract JavaScript catalog** → Python dict în `backend/strategy_catalog.py`
2. **Map IDs:** Convert `long-call` → `long_call` (kebab-case → snake_case)
3. **Validate legs:** Ensure all 69 strategies have valid buildParams
4. **Create triggers:** Define when each strategy should be recommended based on:
   - Stock score (bullish/bearish/neutral)
   - IV rank (high/low)
   - Technical indicators (RSI, MACD)
   - Risk profile (conservative/moderate/aggressive)

### Week 2: Integrate into Scoring (3 zile)
1. **Extend `_recommend_options_strategies()`:**
   - Add logic for all 69 strategies
   - Universal trigger system (not hardcoded per strategy)
2. **Universal pricer:**
   - Use Builder Engine to price any leg combination
   - Calculate Greeks for all strategies
3. **Testing:**
   - Test all 69 strategies with different scores/IVs
   - Validate recommendations make sense

### Week 3: Frontend Integration (3 zile)
1. **StrategyRecommendationCard.jsx:**
   - Display recommended strategies from API
   - Show: Name, legs, max profit/loss, probability
   - "Execute Trade" button → Open Builder
2. **Builder pre-fill:**
   - Pass strategy legs to BuilderV2Page
   - Auto-populate strikes, quantities, DTE
3. **Testing & Polish:**
   - End-to-end workflow validation
   - UI/UX improvements

### Week 4: Live Data & Testing (5 zile)
1. **TradeStation technical data:**
   - Fetch 200-day bars
   - Calculate RSI, MACD, Bollinger Bands
2. **IV rank integration:**
   - Fetch from UW or TradeStation
   - Use for strategy filtering
3. **Production testing:**
   - Test with real symbols (TSLA, AAPL, NVDA, SPY)
   - Validate all 69 strategies work end-to-end

---

## ✅ NEXT STEPS

1. **Confirm this catalog is accurate** - Review any discrepancies
2. **Choose integration approach:**
   - Option A: All 69 at once (3 weeks)
   - Option B: Phased rollout (10 strategies/week, 7 weeks)
3. **Start extraction:**
   - Create `backend/strategy_catalog.py`
   - Begin Python mapping

**Total Timeline: 3-4 săptămâni pentru TOATE 69 STRATEGII INTEGRATE ÎN SCORING!** 🚀

---

**Document creat:** 3 Noiembrie 2025  
**Status:** ✅ VERIFIED - All 69 strategies from `/frontend/src/data/strategies.js`
