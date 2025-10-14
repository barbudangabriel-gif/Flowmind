# 📋 SIDEBAR TODO - Sedință Viitoare

## 🎯 Obiectiv
Sincronizare perfectă între elementele din Sidebar și paginile existente.

## 📊 Status Current

### ✅ Pagini Active (7)
1. **BuilderPage.jsx** → Strategy Builder (54+ strategies)
2. **FlowPage.jsx** → Options Flow Monitor
3. **LiveFlowPage.jsx** → Live Flow (real-time)
4. **OptimizePage.jsx** → Strategy Optimizer
5. **PortfoliosList.jsx** → Portfolio Manager
6. **PortfolioDetail.jsx** → Portfolio Details
7. **PortfolioCreate.jsx** → Create Portfolio

### 📦 Pagini în Archive (6)
- ChartHeadlessPage.js
- ChartPage.js
- ChartProPage.js
- ChartProPlusPlusPlus.js
- OptionsWorkbench.jsx
- OptionsAnalytics.jsx

## 🔧 De Făcut în Sedință

### 1. Mapare Sidebar Items → Routes
```javascript
// SidebarSimple.jsx - Current structure
const menuItems = [
  { label: 'Dashboard', icon: LayoutDashboard, link: '/' },
  { 
    label: 'Options', 
    icon: TrendingUp,
    children: [
      { label: 'Builder', link: '/builder' },      // ✅ EXISTS
      { label: 'Flow', link: '/flow' },            // ✅ EXISTS
      { label: 'Optimizer', link: '/optimizer' },  // ❓ Check OptimizePage.jsx
      { label: 'Scanner', link: '/scanner' },      // ❌ MISSING
      { label: 'Analytics', link: '/analytics' }   // ❌ MISSING (in archive)
    ]
  },
  // ... alte secțiuni
]
```

### 2. Verificări Necesare
- [ ] Care rute din Sidebar NU au pagină?
- [ ] Care pagini NU sunt în Sidebar?
- [ ] LiveFlowPage.jsx → adăugat în submeniu Flow?
- [ ] OptimizePage.jsx → funcțional? (nu e în App.js routing)

### 3. Decizii de Luat
- [ ] Scanner page → create new sau remove from sidebar?
- [ ] Analytics → restore din archive sau remove?
- [ ] Chart pages → restore sau keep archived?
- [ ] Worflow ideal: Dashboard → Builder → Flow → Portfolio

### 4. Acțiuni Concrete
1. Audit complet: `grep -r "Route path" App.js` vs Sidebar items
2. Creează pagini lipsă SAU șterge din sidebar
3. Testează fiecare link din sidebar → 404 check
4. Actualizează iconițe conform funcționalitate
5. Organizează ordine logică (workflow user)

## 🎨 Design Considerations
- Sidebar max 2 nivele (current OK)
- Popover submenu pentru collapsed (BUG - de fixat)
- Active state highlighting (de implementat)
- Breadcrumbs în header? (nice to have)

## 📝 Notes
- Archive folder: `/frontend/src/archive` (24 files)
- Production App.js: clean, 6.1K, 10 routes
- Theme: UW dark (sidebar + header done, pages TBD)

---
**Created:** 2025-10-13  
**Priority:** HIGH (înainte de deploy)  
**Time Estimate:** 2-3 ore sedință focusată
