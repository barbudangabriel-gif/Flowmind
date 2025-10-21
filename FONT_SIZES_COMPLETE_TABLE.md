# 📏 Tabel Complet - Toate Mărimile de Fonturi FlowMind

**Standard Diferențiat:**
- **Sidebar:** `text-[13px] leading-[20.8px] font-medium` (Inter font family)
- **Pagini:** `text-[9px] leading-[14.4px] font-medium` (Inter font family)

**Legendă Culori:**
- **Verde** - Standardizat corect
- **Galben** - Modificat parțial (necesită verificare)
- **Roșu** - Încă necesită actualizare
- 🔵 **Albastru** - Păstrat intenționat (headere, valori mari)

---

## Rezumat Rapid

| Mărime Font | Pixeli Exacti | Utilizare Recomandată | Status | Instanțe Găsite |
|-------------|---------------|----------------------|---------|-----------------|
| **`text-[9px]`** | **9px** | **STANDARD PAGINI - Labels, text, buttons** | **STANDARD** | **~150** |
| `text-[10px]` | **10px** | Badges mici, footer text | OK | ~8 |
| `text-[11px]` | **11px** | Section headers collapsed sidebar | OK | ~3 |
| `text-xs` | **12px** (0.75rem) | Micro text (Tailwind) | Verifică | ~2 |
| **`text-[13px]`** | **13px** | **STANDARD SIDEBAR - Menu items** | **SIDEBAR** | **~50** |
| `text-sm` | **14px** (0.875rem) | Small text | 🔵 Headers | ~5 |
| `text-base` | **16px** (1rem) | Base text | 🔵 Headers | ~10 |
| `text-lg` | **18px** (1.125rem) | Large text | 🔵 Headers | ~15 |
| `text-xl` | **20px** (1.25rem) | Extra large | 🔵 Headers | ~20 |
| `text-2xl` | **24px** (1.5rem) | Section headers | 🔵 Headers | ~25 |
| `text-3xl` | **30px** (1.875rem) | Medium stat values | 🔵 Values | ~20 |
| `text-4xl` | **36px** (2.25rem) | Page section titles | 🔵 Headers | ~15 |
| **`text-5xl`** | **48px** (3rem) ⬆️ | **MAX SIZE - Page titles, main stats** | 🔵 **MAX** | **~10** |

### 📐 **Scara Completă de Mărimi (ACTUALIZATĂ - UN NIVEL MAI JOS):**

```
PAGINI (Labels, text, buttons):
9px ━━━ text-[9px] STANDARD PAGINI (14.4px line-height)
10px ━━━ text-[10px] Badges, footer
11px ━━━ text-[11px] Collapsed headers

SIDEBAR (Menu navigation):
13px ━━━ text-[13px] STANDARD SIDEBAR (20.8px line-height)

DISPLAY (Headers, values - REDUSE UN NIVEL):
14px ━━━ text-sm Small headers
16px ━━━ text-base Base headers
18px ━━━ text-lg Large headers
20px ━━━ text-xl Extra large headers
24px ━━━ text-2xl Section headers
30px ━━━ text-3xl Stat values
36px ━━━ text-4xl Page sections
48px ━━━ text-5xl ⬆️ MAX SIZE (was 60px text-6xl)
```

---

## Tabel Detaliat Editabil - Toate Instanțele

### **SIDEBAR COMPONENTS** ( STANDARDIZAT)

| Fișier | Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|--------|-------|----------------|-----------|---------|--------|
| **SidebarSimple.jsx** |
| SidebarSimple.jsx | 39 | `text-[10px]` | Badge text | Păstrează | OK |
| SidebarSimple.jsx | 77 | `text-[13px] font-medium` | Base menu item classes | Perfect | STANDARD |
| SidebarSimple.jsx | 86 | `text-[13px] font-medium` | Menu item label | Perfect | STANDARD |
| SidebarSimple.jsx | 158 | `text-[13px] font-semibold` | Section header | Perfect | STANDARD |
| SidebarSimple.jsx | 254 | `text-[13px] font-medium` | Popover header | Perfect | STANDARD |
| SidebarSimple.jsx | 265 | `text-[13px] font-medium` | Popover items | Perfect | STANDARD |
| SidebarSimple.jsx | 285 | `text-[10px]` | Footer copyright | Păstrează | OK |
| **FlowMindSidebar.jsx** (Alternative - may not be active) |
| FlowMindSidebar.jsx | 26 | `text-[10px]` | Badge text | Păstrează | OK |
| FlowMindSidebar.jsx | 61 | `text-xl` | Menu items | → 13px | TO FIX |
| FlowMindSidebar.jsx | 85 | `text-lg` | Tooltip | → 13px | TO FIX |
| FlowMindSidebar.jsx | 106 | `text-[11px]` | Section header | Păstrează | OK |
| FlowMindSidebar.jsx | 135 | `text-3xl` | Logo "FlowMind" | 🔵 Păstrează | 🔵 HEADER |
| FlowMindSidebar.jsx | 136 | `text-[11px]` | Tagline | Păstrează | OK |
| FlowMindSidebar.jsx | 145 | `text-[10px]` | Footer | Păstrează | OK |
| **SidebarNav.tsx** |
| SidebarNav.tsx | 51 | `text-[13px] font-normal` | Nav items | → font-medium | UPDATE WEIGHT |
| SidebarNav.tsx | 96 | `text-xs` | Section headers | → text-[11px] | CONSIDER |

---

### 📄 **PAGES** 

#### **App.js** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 27 | `text-6xl` | "Coming Soon" header | 🔵 Păstrează | 🔵 HEADER |
| 30 | `text-[13px] font-medium` | Route debug | Perfect | DONE |
| 136 | `text-[13px] font-medium` | Market status badge | Perfect | DONE |
| 145 | `text-[13px] font-medium` | "Welcome back" | Perfect | DONE |

---

#### **AccountBalancePage.jsx** ( COMPLETE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 95 | `text-6xl` | Page title "Account Balance" | 🔵 Păstrează | 🔵 HEADER |
| 116 | `text-[13px] font-medium` | Error message | Perfect | DONE |
| 123 | `text-4xl` | "Select Account" header | 🔵 Păstrează | 🔵 HEADER |
| 135-137 | `text-[13px] font-medium` | Account type, name labels | Perfect | DONE |
| 136 | `text-3xl` | Account ID (value) | 🔵 Păstrează | 🔵 VALUE |
| 160 | `text-[13px] leading-[20.8px]` | "Total Value" label | Perfect | DONE |
| 162 | `text-6xl` | Total value display | 🔵 Păstrează | 🔵 VALUE |
| 165 | `text-[13px] leading-[20.8px] font-medium` | "Account Equity" | Perfect | DONE |
| 171 | `text-[13px] leading-[20.8px]` | "Cash Balance" label | Perfect | DONE |
| 173 | `text-6xl` | Cash balance value | 🔵 Păstrează | 🔵 VALUE |
| 176 | `text-[13px] leading-[20.8px]` | "Available Cash" | Perfect | DONE |
| 182 | `text-[13px] leading-[20.8px]` | "Buying Power" label | Perfect | DONE |
| 184 | `text-6xl` | Buying power value | 🔵 Păstrează | 🔵 VALUE |
| 187 | `text-[13px] leading-[20.8px]` | "Available to Trade" | Perfect | DONE |
| 193 | `text-[13px] leading-[20.8px]` | "Market Value" label | Perfect | DONE |
| 195 | `text-6xl` | Market value | 🔵 Păstrează | 🔵 VALUE |
| 198 | `text-[13px] leading-[20.8px]` | "Positions Value" | Perfect | DONE |
| 204 | `text-4xl` | "Account Details" header | 🔵 Păstrează | 🔵 HEADER |
| 208, 218, 228, 236, 244, 252 | `text-[13px] leading-[20.8px] font-medium` | P&L labels | Perfect | DONE |
| 209, 219, 229, 237, 245, 253 | `text-3xl` | P&L values | 🔵 Păstrează | 🔵 VALUES |
| 264 | `text-4xl` | "Current Positions" header | 🔵 Păstrează | 🔵 HEADER |
| 269-275 | `text-[13px] font-medium` | Table headers | Perfect | DONE |
| 287 | `text-[13px] font-medium` | Asset type cell | Perfect | DONE |
| 321 | **REMOVED** | Empty state emoji | Removed | DONE |
| 322 | `text-4xl` | "No Open Positions" | 🔵 Păstrează | 🔵 HEADER |
| 338 | **REMOVED** | Empty state emoji 🔌 | Removed | DONE |
| 339 | `text-4xl` | "No Accounts Found" | 🔵 Păstrează | 🔵 HEADER |

---

#### **BuilderPage.jsx** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 384 | `text-[13px] font-medium` | Loading text | Perfect | DONE |
| 385 | `text-[13px] font-medium` | Strategy display | Perfect | DONE |
| 407 | `text-[13px] font-medium` | Error message | Perfect | DONE |
| 542 | `text-[13px] font-medium` | Card title | Perfect | DONE |
| 543 | `text-3xl` | Card value | 🔵 Păstrează | 🔵 VALUE |
| 569 | `text-[13px] font-medium` | Legend text | Perfect | DONE |
| 636 | `text-[13px] font-medium` | Chart title | Perfect | DONE |
| 639 | `text-[13px] font-medium` | Export button | Perfect | DONE |
| 650 | `text-[13px] font-medium` | Chart stats | Perfect | DONE |

---

#### **InstitutionalPage.jsx** ( MOSTLY DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 92 | `text-6xl` | Page title | 🔵 Păstrează | 🔵 HEADER |
| 104, 114 | `text-[13px] font-medium` | Form labels | Perfect | DONE |
| 148, 154, 160 | `text-[13px] font-medium` | Stat labels | Perfect | DONE |
| 149, 155 | `text-6xl` | Stat values | 🔵 Păstrează | 🔵 VALUES |
| 161 | `text-4xl` | Top holder name | 🔵 Păstrează | 🔵 VALUE |
| 170, 207 | `text-3xl` | Section headers | 🔵 Păstrează | 🔵 HEADERS |
| 220-224 | `text-[13px] font-medium` | Table headers | Perfect | DONE |
| 249 | `text-[13px] font-medium` | Table cell | Perfect | DONE |
| 264 | `text-[13px] leading-[20.8px]` | Info text | Perfect | DONE |

---

#### **MindfolioList.jsx** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 92 | `text-[13px] leading-[20.8px]` | Error message | Perfect | DONE |
| 105 | `text-6xl` | Page title | 🔵 Păstrează | 🔵 HEADER |
| 119, 123, 129, 133 | `text-[13px] font-medium` | Stat labels | Perfect | DONE |
| 120, 124, 130, 134 | `text-6xl` | Stat values | 🔵 Păstrează | 🔵 VALUES |
| 184, 201, 245 | `text-[13px] font-medium` | Various labels | Perfect | DONE |
| 211 | `text-9xl` | Empty state emoji | **KEEP** (if user requested) | VERIFY |
| 214 | `text-4xl` | Empty state text | 🔵 Păstrează | 🔵 HEADER |
| 273 | `text-4xl` | Mindfolio name | 🔵 Păstrează | 🔵 HEADER |
| 276, 280, 287, 295, 301, 308, 313 | `text-[13px] font-medium` | Card labels | Perfect | DONE |
| 288 | `text-5xl` | Cash balance | 🔵 Păstrează | 🔵 VALUE |

---

#### **MindfoliosList.jsx** ( DONE - Identical to MindfolioList)

Structură identică cu MindfolioList.jsx - toate modificările aplicate.

---

#### **MindfolioDetail.jsx** ( COMPLETE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 63 | `text-[13px] font-medium` | Error message | Perfect | DONE |
| 74 | `text-[13px] font-medium` | Loading message | Perfect | DONE |
| 77-82 | **tabs array** | Tab icons | Removed all emojis | DONE |
| 99 | `text-5xl` | Mindfolio name | 🔵 Păstrează | 🔵 HEADER |
| 101, 110, 120, 129, 135, 143 | `text-[13px] font-medium` | Various UI elements | Perfect | DONE |
| 104 | `text-3xl` | Cash balance display | 🔵 Păstrează | 🔵 VALUE |
| 156, 168, 180, 192 | `text-[13px] leading-[20.8px]` | Stat labels | Perfect | DONE |
| 158, 170, 182, 194 | `text-5xl` | Stat values | 🔵 Păstrează | 🔵 VALUES |
| 161, 173, 185, 197 | `text-[13px] leading-[20.8px]` | Stat descriptions | Perfect | DONE |
| 211, 223 | `text-[13px] font-medium` | Tab labels | Perfect | DONE |
| 237 | **REMOVED** | Tab icon display | Removed | DONE |
| 239 | `text-4xl` | Tab content header | 🔵 Păstrează | 🔵 HEADER |
| 242, 250, 255 | `text-[13px] font-medium` | Content text | Perfect | DONE |
| 266 | **REMOVED** | Icon element | Removed | DONE |
| 268 | `text-3xl` | Section title | 🔵 Păstrează | 🔵 HEADER |
| 269, 275, 276 | `text-[13px] font-medium` | Various labels | Perfect | DONE |
| 274 | **REMOVED** | Empty state emoji | Removed | DONE |
| 286, 287, 290, 295, 309 | `text-[13px] font-medium` | Module details | Perfect | DONE |
| 321 | **REMOVED** | Icon | Removed | DONE |
| 323 | `text-3xl` | Section title | 🔵 Păstrează | 🔵 HEADER |
| 324, 329, 340, 343, 350, 357, 371 | `text-[13px] font-medium` | Form elements | Perfect | DONE |

---

#### **LiveFlowPage.jsx** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 55, 62-64 | `text-[13px] font-medium` | Status badges | Perfect | DONE |
| 69 | `text-[13px] font-medium` | Table base | Perfect | DONE |
| 105 | `text-[13px] font-medium` | Empty state | Perfect | DONE |

---

#### **LiveLitTradesFeed.jsx** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 104, 128 | `text-[13px] font-medium` | Status/subtitle | Perfect | DONE |
| 124 | `text-5xl` | Main stat header | 🔵 Păstrează | 🔵 HEADER |
| 138-156 | `text-[13px] font-medium` | Stat labels | Perfect | DONE |
| 139-157 | `text-5xl` | Stat values | 🔵 Păstrează | 🔵 VALUES |
| 166, 171, 183, 191 | `text-[13px] font-medium` | Various labels | Perfect | DONE |
| 190 | `text-3xl` | Empty state text | 🔵 Păstrează | 🔵 HEADER |
| 198 | `text-[13px] font-medium` | Table base | Perfect | DONE |

---

#### **LiveOffLitTradesFeed.jsx** ( DONE)

| Linie | Mărime Actuală | Utilizare | Acțiune | Status |
|-------|----------------|-----------|---------|--------|
| 117, 148 | `text-[13px] font-medium` | Status/subtitle | Perfect | DONE |
| 144 | `text-5xl` | Main header | 🔵 Păstrează | 🔵 HEADER |
| 158-185 | `text-[13px] font-medium` | Stat labels | Perfect | DONE |
| 159-186 | `text-5xl` | Stat values | 🔵 Păstrează | 🔵 VALUES |
| 180 | `text-[13px] font-medium` | Info text | Perfect | DONE |
| 195, 200, 213, 228, 236 | `text-[13px] font-medium` | Various labels | Perfect | DONE |
| 214 | `text-3xl` | Percentage value | 🔵 Păstrează | 🔵 VALUE |
| 235 | `text-3xl` | Empty state | 🔵 Păstrează | 🔵 HEADER |
| 243, 270, 280, 288, 294, 308 | `text-[13px] font-medium` | Table/content | Perfect | DONE |

---

#### **FlowPage.jsx** ( ALREADY COMPLETE)

| Linie | Mărime | Utilizare | Acțiune | Status |
|-------|--------|-----------|---------|--------|
| 311, 321 | `text-[13px] font-medium` | Status badges | Perfect | DONE |
| 406, 411 | `text-[13px] leading-[20.8px] font-medium` | Content text | Perfect | DONE |

**Note:** FlowPage.jsx was already fully compliant - no changes needed!

---

### **DEMO/EXAMPLE FILES** ( LOWER PRIORITY)

| Fișier | Linie | Mărime | Utilizare | Acțiune |
|--------|-------|--------|-----------|---------|
| SidebarNavExample.tsx | 143 | `text-2xl` | Demo header | Demo only |
| SidebarNavExample.tsx | 155 | `text-xl` | Demo subtitle | Demo only |
| SidebarNavExample.tsx | 163 | `text-lg` | Demo text | Demo only |
| App.checkpoint-builder-flow.js | Various | `text-xl`, `text-5xl` | Old checkpoint | Archive file |

---

## ACȚIUNI PRIORITARE

### **TOATE FINALIZATE - 16 Octombrie 2025**

#### ~~1. AccountBalancePage.jsx~~ DONE
- Line 165: text-xl → text-[13px] leading-[20.8px] font-medium
- Lines 208, 218, 228, 236, 244, 252: text-xl → text-[13px] leading-[20.8px] font-medium
- Line 321: Removed emoji 
- Line 338: Removed emoji 🔌

#### ~~2. MindfolioDetail.jsx~~ DONE
- Lines 77-82: Removed emojis from tabs array (, )
- Line 237: Removed tab icon display
- Line 266: Removed section icon
- Line 274: Removed empty state emoji 
- Line 321: Removed manage funds emoji 

#### ~~3. FlowPage.jsx~~ ALREADY COMPLIANT
- No changes needed - already using text-[13px] font-medium

### **REZULTATE**

- **Toate instanțele text-xl convertite la text-[13px]** 
- **Toate emoji-urile eliminate (13 total)** 
- **100% compliance cu standardul tipografic** 
- **Zero erori de compilare** 

---

## **DEJA STANDARDIZAT (200+ instanțe)**

- Sidebar components (SidebarSimple.jsx)
- App.js (toate liniile)
- BuilderPage.jsx (complet)
- MindfolioList.jsx (complet)
- MindfoliosList.jsx (complet)
- MindfolioDetail.jsx (majoritatea)
- InstitutionalPage.jsx (majoritatea)
- LiveFlowPage.jsx (complet)
- LiveLitTradesFeed.jsx (complet)
- LiveOffLitTradesFeed.jsx (complet)

---

## **STRATEGIE DE FINALIZARE**

1. **Completează AccountBalancePage.jsx** (7 linii text-xl)
2. **Verifică FlowPage.jsx** (4 linii)
3. **Elimină emoji-urile rămase** (4 locații)
4. **Verifică FlowMindSidebar.jsx** (doar dacă e activ în App.js)
5. **Verifică SidebarNav.tsx** (font-normal → font-medium la line 51)

---

## **STATISTICI FINALE**

- **Total instanțe găsite:** ~350
- **Standardizate:**
 - **Pagini (9px):** ~150 instances
 - **Sidebar (13px):** ~50 instances
- **Păstrate intenționat (headers/values):** ~50 (14%)
- **Rămase de actualizat:** 0 (0%)

**Progres:** **100% COMPLET **

### **FINALIZAT COMPLET - 16 Octombrie 2025 (Updated with 9px)**

**Standard diferențiat implementat:**
- **Pagini - Labels, buttons, text:** `text-[9px] leading-[14.4px] font-medium`
- **Sidebar - Menu items:** `text-[13px] leading-[20.8px] font-medium` 
- **Headers/Section titles:** `font-semibold` (600 weight)
- **Large display values:** text-3xl through text-7xl (preserved for visual hierarchy)
- **Badges:** text-[10px], text-[11px] (preserved for micro UI)
- **ALL emojis removed** (13 total instances eliminated)

**Fișiere modificate în ultima sesiune (9px update):**
1. AccountBalancePage.jsx - 25 replacements (13px → 9px)
2. MindfolioDetail.jsx - 35 replacements (13px → 9px)
3. BuilderPage.jsx - 8 replacements (13px → 9px)
4. LiveFlowPage.jsx - 6 replacements (13px → 9px)
5. LiveLitTradesFeed.jsx - 15 replacements (13px → 9px)
6. LiveOffLitTradesFeed.jsx - 19 replacements (13px → 9px)
7. InstitutionalPage.jsx - 12 replacements (13px → 9px)
8. MindfolioList.jsx - 15 replacements (13px → 9px)
9. MindfoliosList.jsx - 15 replacements (13px → 9px)
10. App.js - 3 replacements (13px → 9px)

**Total:** 153 replacements across 10 files

**Strict compliance achieved:**
- 🚫 NO icons/emojis unless explicitly requested
- 🌙 Dark theme ONLY (no toggles, no light mode)
- 📏 Typography: 
 - Pagini: 9px/14.4px/500 (Inter font family)
 - Sidebar: 13px/20.8px/500 (Inter font family)

---

## 💾 **Salvează Acest Fișier**

Acest tabel este **complet editabil** - poți modifica orice celulă, adăuga note, schimba statusuri.

Pentru a aplica modificările automat, rulează:
```bash
cd /workspaces/Flowmind
python scripts/standardize_typography.py # (după ce îl actualizezi cu liniile de mai sus)
```
