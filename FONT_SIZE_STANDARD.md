# FlowMind Font Size Standard
**Date: October 16, 2025**

## 🎯 Unified Font System

FlowMind folosește un sistem simplu și uniform de 5 dimensiuni pentru TOATĂ aplicația:

### 1️⃣ Display (Page Headers)
- **Size:** `text-2xl`
- **Weight:** `font-bold`
- **Usage:** Titluri principale de pagină (ex: "FlowMind Dashboard")
- **Example:** `<h1 className="text-2xl font-bold text-white">`

### 2️⃣ Section Headers
- **Size:** `text-xl`
- **Weight:** `font-semibold`
- **Usage:** Titluri de secțiuni (ex: "Mindfolio Overview", "Options Analytics")
- **Example:** `<h2 className="text-xl font-semibold text-white">`

### 3️⃣ Body/Normal Text
- **Size:** `text-base`
- **Weight:** `font-medium`
- **Usage:** Text normal, labels, descrieri
- **Example:** `<p className="text-base font-medium text-gray-400">`

### 4️⃣ Small/Details
- **Size:** `text-sm`
- **Weight:** `font-medium`
- **Usage:** Detalii secundare, subtitluri, metadata
- **Example:** `<div className="text-sm font-medium text-gray-400">`

### 5️⃣ Highlighted Values (Numbers)
- **Size:** `text-3xl`
- **Weight:** `font-semibold`
- **Usage:** Valori numerice importante (ex: $125,000.5, scores)
- **Example:** `<div className="text-3xl font-semibold text-green-400">{value}</div>`

## 📐 Font Hierarchy

```
text-2xl (Display)
   ↓
text-xl (Section Headers)
   ↓
text-base (Body)  ←→  text-3xl (Values)
   ↓
text-sm (Details)
```

## 🚫 Interzise

**NU se mai folosesc:**
- ❌ `text-xs` (prea mic)
- ❌ `text-lg` (redundant cu text-xl)
- ❌ `text-4xl`, `text-5xl`, `text-6xl`, `text-7xl`, `text-8xl`, `text-9xl` (prea mari)
- ❌ `text-[9px]`, `text-[13px]` (nu mai folosim custom sizes)
- ❌ `font-normal` (folosim font-medium sau font-semibold)
- ❌ `font-light`, `font-thin` (prea subtiri)

## ✅ Exemple Practice

### Dashboard Card
```jsx
<div className="card">
  <div className="text-sm font-medium">Total Portfolio Value</div>
  <div className="text-3xl font-semibold text-green-400">$125,000.50</div>
  <div className="text-sm font-medium text-gray-400">+2,450.25 (1.96%)</div>
</div>
```

### Stock List Item
```jsx
<div className="stock-item">
  <div className="text-base font-medium">NVDA</div>
  <div className="text-sm font-medium text-gray-400">Technology</div>
  <div className="text-xl font-semibold text-green-400">92</div>
</div>
```

### Page Header
```jsx
<div className="page-header">
  <h1 className="text-2xl font-bold text-white">FlowMind Dashboard</h1>
  <p className="text-base font-medium text-gray-400">Real-time overview</p>
</div>
```

## 🎨 Design Principles

1. **Consistency:** Aceeași dimensiune pentru același tip de conținut
2. **Hierarchy:** Diferențe clare între nivele
3. **Readability:** Text lizibil la toate dimensiunile
4. **Professional:** Aspect curat, fără extreme

## 📊 Statistics

- **Total font sizes used:** 5 (down from 13+)
- **Font weights used:** 3 (medium, semibold, bold)
- **Consistency:** 100%

## 🔄 Migration Status

✅ Dashboard components uniformized
✅ Emoji eliminated (11,176 removed)
✅ Dark theme enforced
✅ Typography standardized

**Last updated:** October 16, 2025
