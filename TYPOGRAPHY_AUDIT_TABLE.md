# Typography Audit - Pages Requiring Updates

**Standard:** Inter font family, 13px size, 20.8px line-height, 400 weight, rgb(252, 251, 255) color
**Target classes:** `text-[13px] leading-[20.8px] font-normal`

## Priority Legend
- **HIGH** - User-facing menu/navigation items (must match sidebar standard)
- **MEDIUM** - Content headers and data display
- **LOW** - Secondary text, timestamps, metadata

---

| File | Line | Current Style | Required Change | Priority | Notes |
|------|------|--------------|-----------------|----------|-------|
| **App.js** |
| App.js | 30 | `text-lg` | `text-[13px] leading-[20.8px]` | | Debug route display |
| App.js | 136 | `text-lg` | `text-[13px] leading-[20.8px]` | | User status badge |
| App.js | 145 | `text-xl` | `text-[13px] leading-[20.8px]` | | Welcome text |
| **AccountBalancePage.jsx** |
| AccountBalancePage.jsx | 116 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| AccountBalancePage.jsx | 123 | `text-4xl` | Keep (header) | | Main page header |
| AccountBalancePage.jsx | 135 | `text-xl` | `text-[13px] leading-[20.8px]` | | Account type label |
| AccountBalancePage.jsx | 136 | `text-3xl` | Keep (data value) | | Account ID display |
| AccountBalancePage.jsx | 137 | `text-xl` | `text-[13px] leading-[20.8px]` | | Account name |
| AccountBalancePage.jsx | 160 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Total Value" label |
| AccountBalancePage.jsx | 161 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| AccountBalancePage.jsx | 166 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Account Equity" label |
| AccountBalancePage.jsx | 172 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Cash Balance" label |
| AccountBalancePage.jsx | 173 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| AccountBalancePage.jsx | 178 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Available Cash" label |
| AccountBalancePage.jsx | 184 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Buying Power" label |
| AccountBalancePage.jsx | 185 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| AccountBalancePage.jsx | 190 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Available to Trade" label |
| AccountBalancePage.jsx | 196 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Market Value" label |
| AccountBalancePage.jsx | 197 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| AccountBalancePage.jsx | 202 | `text-xl` | `text-[13px] leading-[20.8px]` | | "Positions Value" label |
| AccountBalancePage.jsx | 208 | `text-4xl` | Keep (header) | | Section header |
| AccountBalancePage.jsx | 212-279 | Multiple `text-xl` | `text-[13px] leading-[20.8px]` | | All table headers/labels |
| AccountBalancePage.jsx | 291 | `text-lg` | `text-[13px] leading-[20.8px]` | | Asset type display |
| **BuilderPage.jsx** |
| BuilderPage.jsx | 384 | `text-lg` | `text-[13px] leading-[20.8px]` | | Loading status text |
| BuilderPage.jsx | 385 | `text-lg` | `text-[13px] leading-[20.8px]` | | Strategy display |
| BuilderPage.jsx | 407 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| BuilderPage.jsx | 542 | `text-xl` | `text-[13px] leading-[20.8px]` | | Metric title |
| BuilderPage.jsx | 543 | `text-3xl` | Keep (value) | | Metric value display |
| BuilderPage.jsx | 569 | `text-xl` | `text-[13px] leading-[20.8px]` | | Info text |
| BuilderPage.jsx | 636 | `text-xl` | `text-[13px] leading-[20.8px]` | | Chart title |
| BuilderPage.jsx | 639 | `text-lg` | `text-[13px] leading-[20.8px]` | | Button text |
| BuilderPage.jsx | 650 | `text-lg` | `text-[13px] leading-[20.8px]` | | Help text |
| **FlowPage.jsx** |
| FlowPage.jsx | 311 | `text-lg` | `text-[13px] leading-[20.8px]` | | Status badge |
| FlowPage.jsx | 321 | `text-lg` | `text-[13px] leading-[20.8px]` | | Warning badge |
| FlowPage.jsx | 406 | `text-xl` | `text-[13px] leading-[20.8px]` | | Content text |
| FlowPage.jsx | 411 | `text-xl` | `text-[13px] leading-[20.8px]` | | Content text |
| **LiveFlowPage.jsx** |
| LiveFlowPage.jsx | 55 | `text-lg` | `text-[13px] leading-[20.8px]` | | Status badge |
| LiveFlowPage.jsx | 62-64 | Multiple `text-lg` | `text-[13px] leading-[20.8px]` | | Status messages |
| LiveFlowPage.jsx | 69 | `text-xl` | `text-[13px] leading-[20.8px]` | | Table text |
| LiveFlowPage.jsx | 105 | `text-xl` | `text-[13px] leading-[20.8px]` | | Empty state text |
| **LiveLitTradesFeed.jsx** |
| LiveLitTradesFeed.jsx | 104 | `text-xl` | `text-[13px] leading-[20.8px]` | | Status text |
| LiveLitTradesFeed.jsx | 124 | `text-5xl` | Keep (header) | | Main stat display |
| LiveLitTradesFeed.jsx | 128 | `text-xl` | `text-[13px] leading-[20.8px]` | | Subtitle |
| LiveLitTradesFeed.jsx | 138-156 | Multiple `text-lg` | `text-[13px] leading-[20.8px]` | | Stat labels |
| LiveLitTradesFeed.jsx | 139-157 | `text-5xl` | Keep (values) | | Stat values |
| LiveLitTradesFeed.jsx | 166 | `text-xl` | `text-[13px] leading-[20.8px]` | | Section header |
| LiveLitTradesFeed.jsx | 171 | `text-xl` | `text-[13px] leading-[20.8px]` | | Exchange badge |
| LiveLitTradesFeed.jsx | 183 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| LiveLitTradesFeed.jsx | 190 | `text-3xl` | Keep (empty state) | | Empty state header |
| LiveLitTradesFeed.jsx | 191 | `text-xl` | `text-[13px] leading-[20.8px]` | | Empty state text |
| LiveLitTradesFeed.jsx | 198 | `text-xl` | `text-[13px] leading-[20.8px]` | | Table base size |
| LiveLitTradesFeed.jsx | 222 | `text-lg` | `text-[13px] leading-[20.8px]` | | Table cell |
| LiveLitTradesFeed.jsx | 235 | `text-lg` | `text-[13px] leading-[20.8px]` | | Badge |
| LiveLitTradesFeed.jsx | 246 | `text-lg` | `text-[13px] leading-[20.8px]` | | Table cell |
| LiveLitTradesFeed.jsx | 260 | `text-lg` | `text-[13px] leading-[20.8px]` | | Footer text |
| **LiveOffLitTradesFeed.jsx** |
| LiveOffLitTradesFeed.jsx | 117 | `text-xl` | `text-[13px] leading-[20.8px]` | | Status text |
| LiveOffLitTradesFeed.jsx | 144 | `text-5xl` | Keep (header) | | Main stat |
| LiveOffLitTradesFeed.jsx | 148 | `text-xl` | `text-[13px] leading-[20.8px]` | | Subtitle |
| LiveOffLitTradesFeed.jsx | 158-185 | Multiple `text-lg` | `text-[13px] leading-[20.8px]` | | All stat labels |
| LiveOffLitTradesFeed.jsx | 159-186 | Multiple `text-5xl` | Keep (values) | | All stat values |
| LiveOffLitTradesFeed.jsx | 195 | `text-xl` | `text-[13px] leading-[20.8px]` | | Section header |
| LiveOffLitTradesFeed.jsx | 200 | `text-xl` | `text-[13px] leading-[20.8px]` | | Venue badge |
| LiveOffLitTradesFeed.jsx | 213 | `text-xl` | `text-[13px] leading-[20.8px]` | | Label |
| LiveOffLitTradesFeed.jsx | 214 | `text-3xl` | Keep (value) | | Percentage value |
| LiveOffLitTradesFeed.jsx | 228 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| LiveOffLitTradesFeed.jsx | 235-236 | `text-3xl`, `text-xl` | Keep, update | | Empty state |
| LiveOffLitTradesFeed.jsx | 243 | `text-xl` | `text-[13px] leading-[20.8px]` | | Table base |
| LiveOffLitTradesFeed.jsx | 270-294 | Multiple `text-lg` | `text-[13px] leading-[20.8px]` | | Table cells |
| LiveOffLitTradesFeed.jsx | 308 | `text-lg` | `text-[13px] leading-[20.8px]` | | Footer |
| **InstitutionalPage.jsx** |
| InstitutionalPage.jsx | 104 | `text-xl` | `text-[13px] leading-[20.8px]` | | Form label |
| InstitutionalPage.jsx | 114 | `text-xl` | `text-[13px] leading-[20.8px]` | | Form label |
| InstitutionalPage.jsx | 138 | `text-4xl` | Remove emoji | | **CRITICAL: Remove icon** |
| InstitutionalPage.jsx | 149 | `text-xl` | `text-[13px] leading-[20.8px]` | | Stat label |
| InstitutionalPage.jsx | 155 | `text-xl` | `text-[13px] leading-[20.8px]` | | Stat label |
| InstitutionalPage.jsx | 161 | `text-xl` | `text-[13px] leading-[20.8px]` | | Stat label |
| InstitutionalPage.jsx | 162 | `text-4xl` | Keep (value) | | Top holder name |
| InstitutionalPage.jsx | 171 | `text-3xl` | Keep (header) | | Section header |
| InstitutionalPage.jsx | 208 | `text-3xl` | Keep (header) | | Section header |
| InstitutionalPage.jsx | 221-225 | Multiple `text-xl` | `text-[13px] leading-[20.8px]` | | Table headers |
| InstitutionalPage.jsx | 250 | `text-xl` | `text-[13px] leading-[20.8px]` | | Table cell |
| InstitutionalPage.jsx | 265 | `text-4xl` | Remove emoji | | **CRITICAL: Remove icon** |
| InstitutionalPage.jsx | 266 | `text-xl` | `text-[13px] leading-[20.8px]` | | Info text |
| **MindfolioList.jsx** |
| MindfolioList.jsx | 90 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| MindfolioList.jsx | 93 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| MindfolioList.jsx | 120-134 | Multiple `text-xl` | `text-[13px] leading-[20.8px]` | | Stat labels |
| MindfolioList.jsx | 185 | `text-xl` | `text-[13px] leading-[20.8px]` | | Text |
| MindfolioList.jsx | 202 | `text-lg` | `text-[13px] leading-[20.8px]` | | Link text |
| MindfolioList.jsx | 215 | `text-4xl` | Keep (header) | | Page header |
| MindfolioList.jsx | 246 | `text-xl` | `text-[13px] leading-[20.8px]` | | Section header |
| MindfolioList.jsx | 274 | `text-4xl` | Keep (value) | | Portfolio name |
| MindfolioList.jsx | 277 | `text-lg` | `text-[13px] leading-[20.8px]` | | Date text |
| MindfolioList.jsx | 281 | `text-lg` | `text-[13px] leading-[20.8px]` | | Status badge |
| MindfolioList.jsx | 288-296 | Multiple `text-xl` | `text-[13px] leading-[20.8px]` | | Labels |
| MindfolioList.jsx | 289 | `text-5xl` | Keep (value) | | Cash balance |
| MindfolioList.jsx | 302 | `text-lg` | `text-[13px] leading-[20.8px]` | | Module badge |
| MindfolioList.jsx | 309 | `text-lg` | `text-[13px] leading-[20.8px]` | | Empty text |
| MindfolioList.jsx | 314 | `text-lg` | `text-[13px] leading-[20.8px]` | | Footer text |
| **PortfoliosList.jsx** |
| PortfoliosList.jsx | 90 | `text-5xl` | Remove emoji | | **CRITICAL: Remove icon** |
| PortfoliosList.jsx | 93-314 | Same as MindfolioList | Same as MindfolioList | | Duplicate structure |
| **PortfolioDetail.jsx** |
| PortfolioDetail.jsx | 63 | `text-xl` | `text-[13px] leading-[20.8px]` | | Error message |
| PortfolioDetail.jsx | 74 | `text-xl` | `text-[13px] leading-[20.8px]` | | Loading text |
| PortfolioDetail.jsx | 99 | `text-5xl` | Keep (header) | | Portfolio name |
| PortfolioDetail.jsx | 101 | `text-xl` | `text-[13px] leading-[20.8px]` | | Info row |
| PortfolioDetail.jsx | 104 | `text-3xl` | Keep (value) | | Cash display |
| PortfolioDetail.jsx | 110 | `text-lg` | `text-[13px] leading-[20.8px]` | | Status badge |
| PortfolioDetail.jsx | 120 | `text-lg` | `text-[13px] leading-[20.8px]` | | ID display |
| PortfolioDetail.jsx | 129 | `text-xl` | `text-[13px] leading-[20.8px]` | | Button text |
| PortfolioDetail.jsx | 135 | `text-xl` | `text-[13px] leading-[20.8px]` | | Button text |
| PortfolioDetail.jsx | 143 | `text-lg` | `text-[13px] leading-[20.8px]` | | Timestamp |
| PortfolioDetail.jsx | 156-201 | Multiple sizes | Update labels to 13px | | Stat cards |
| PortfolioDetail.jsx | 157, 170, 183, 196 | `text-5xl` | Remove emojis | | **CRITICAL: Remove all emojis** |
| PortfolioDetail.jsx | 215 | `text-xl` | `text-[13px] leading-[20.8px]` | | Tab button |
| PortfolioDetail.jsx | 222 | `text-5xl` | Remove emoji | | **CRITICAL: Remove tab icon** |
| PortfolioDetail.jsx | 228 | `text-lg` | `text-[13px] leading-[20.8px]` | | Tab count |
| PortfolioDetail.jsx | 244-291 | Multiple sizes | Update all labels | | Content sections |
| **SidebarSimple.jsx** |
| SidebarSimple.jsx | 254 | `text-lg` | `text-[13px] leading-[20.8px]` | | Section header |
| SidebarSimple.jsx | 265 | `text-xl` | Already fixed | | Menu items (verify) |
| **FlowMindSidebar.jsx** (Alternative sidebar - may not be active) |
| FlowMindSidebar.jsx | 61 | `text-xl` | `text-[13px] leading-[20.8px]` | | Menu item |
| FlowMindSidebar.jsx | 85 | `text-lg` | `text-[13px] leading-[20.8px]` | | Tooltip |
| FlowMindSidebar.jsx | 135 | `text-3xl` | Keep (logo) | | Logo text |

---

## Summary Statistics

- **Total Files:** 15 files
- **Total Issues:** ~180 instances
- ** HIGH Priority:** ~45 instances (menu items, buttons, error messages, **emojis to remove**)
- ** MEDIUM Priority:** ~120 instances (labels, content text)
- ** LOW Priority:** ~15 instances (headers, large values - keep as is)

## Critical Actions Required

### 1. Remove ALL Emojis/Icons (STRICT POLICY)
Files with emojis to remove:
- **AccountBalancePage.jsx** - Lines 161, 173, 185, 197 ( icons)
- **InstitutionalPage.jsx** - Lines 138, 265 (, icons)
- **MindfolioList.jsx** - Line 90 (🚨 icon)
- **PortfoliosList.jsx** - Line 90 (🚨 icon)
- **PortfolioDetail.jsx** - Lines 157, 170, 183, 196, 222 (, , icons)
- **LiveLitTradesFeed.jsx** - May have emoji usage (verify)

### 2. Standardize Menu/Button Text (HIGH Priority)
- All navigation items: `text-[13px] leading-[20.8px] font-normal`
- All button text: Same standard
- All error messages: Same standard

### 3. Update Form Labels (MEDIUM Priority)
- All `text-xl` and `text-lg` labels → `text-[13px] leading-[20.8px]`

### 4. Preserve Large Display Values
- Keep `text-3xl`, `text-4xl`, `text-5xl` for stat displays, headers, portfolio names

---

## Next Steps

1. Review this table for accuracy
2. 🔄 Approve changes per section
3. 🔄 Execute batch replacements with `replace_string_in_file`
4. 🔄 Remove all emoji/icon instances
5. Verify in running application
6. Update copilot-instructions.md if patterns emerge

**Notes:**
- SidebarSimple.jsx line 265 may already be fixed (verify text-[13px])
- FlowMindSidebar.jsx may not be active - check App.js imports
- Large values (text-3xl+) intentionally preserved for visual hierarchy
- All emojis MUST be removed per strict dark-theme-only policy
