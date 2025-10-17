# FlowMind Font Sizes - Editable Reference

## Current Standard (Pages Only - Excluding Sidebar)

### Main Page Headers
- **text-2xl** - Page titles (Dashboard, Portfolios, etc.)
- Font weight: font-bold
- Color: text-white

### Section Headers  
- **text-xl** - Section titles (Mindfolio Overview, Options Analytics, etc.)
- Font weight: font-semibold
- Color: text-white

### Stat Values (Large Numbers)
- **text-3xl** - Primary stat values ($89.7k, 87, etc.)
- Font weight: font-bold or font-semibold
- Color: varies (text-green-400, text-white, text-yellow-400)

### Card Values (Medium Numbers)
- **text-2xl** - Secondary values in cards
- Font weight: font-bold
- Color: varies

### Body Text
- **text-base** - Standard paragraph text, labels
- Font weight: font-medium or normal
- Color: text-gray-400, text-slate-400

### Small Text
- **text-sm** - Labels, secondary info, timestamps
- Font weight: font-medium
- Color: text-gray-400, text-slate-500

### Extra Small Text
- **text-xs** - Tiny labels, badges, metadata
- Font weight: font-medium
- Color: text-gray-500

---

## Edit This Section to Change Sizes

Change the values below, save, and tell me to apply them:

```
PAGE_HEADER = text-2xl font-bold
SECTION_HEADER = text-xl font-semibold  
STAT_VALUE = text-3xl font-bold
CARD_VALUE = text-2xl font-bold
BODY_TEXT = text-base font-medium
LABEL_TEXT = text-sm font-medium
TINY_TEXT = text-xs font-medium
```

---

## Current Font Family (All Pages)
```
font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

---

## Pages Using These Standards

1. **Dashboard.jsx** - text-2xl header, text-xl sections, text-3xl values
2. **MindfolioList.jsx** - text-xl header, text-base content
3. **MindfolioDetailNew.jsx** - text-3xl header, text-2xl/text-3xl values
4. **StatCard.jsx** - text-3xl values, text-sm labels
5. **TopScoredStocks.jsx** - text-base symbols, text-sm sectors, text-xl scores
6. **QuickActionButton.jsx** - text-base labels

---

## How to Use This File

1. Edit the values in "Edit This Section" above
2. Save the file
3. Tell me: "aplica fonturile din FONT_SIZES_EDITABLE.md"
4. I will update all pages to match your changes

---

## Notes

- Sidebar fonts are SEPARATE (text-[13px] leading-[20.8px])
- All sizes use Tailwind CSS classes
- Dark theme only - colors must be light (white, gray-400, etc.)
- NO EMOJI allowed anywhere in UI
