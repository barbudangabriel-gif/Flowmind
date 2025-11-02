// Sidebar config (FlowMind)
// — single source of truth —
// Dynamic menu generation via buildNav(ctx) using system diagnostics.

// ——— Helpers for badge/visible/disable ———
const ivBadge = (ctx) => ctx.metrics.ivOnline
 ? { text: "IV", tone: "success" }
 : { text: "OFF", tone: "warn" };

const verifiedBadge = (ctx) =>
 (ctx.metrics.verifiedRatio ?? 0) >= 0.2
 ? { text: "verified", tone: "verified" }
 : { text: "low", tone: "warn" };

const tsLiveBadge = (ctx) =>
 ctx.flags.TS_LIVE ? { text: "LIVE", tone: "live" } : { text: "OFF", tone: "warn" };

const ivDependentDisabled = (ctx) => !ctx.metrics.ivOnline;
const ivDisabledReason = (_) => "IV service offline";

// ——— Builder principal ———
export function buildNav(ctx) {
 return [
 // OVERVIEW
 {
 title: "Overview",
 items: [
 { label: "Dashboard", to: "/dashboard", icon: "LayoutDashboard" },
 ],
 },

 // ACCOUNT & MINDFOLIOS
 {
 title: "Account",
 items: [
 {
 label: "Mindfolios", icon: "Briefcase",
 children: [
 // ramificare dinamică: toate portofoliile
 ...ctx.mindfolios.map(p => ({
 label: p.name,
 to: `/mindfolios/${p.id}`,
 icon: "FolderKanban",
 badge: p.nav != null ? { text: `$${Math.round(p.nav/1000)}k`, tone: "default" } : undefined,
 })),
 // separator logic: + create
 { label: "+ Create Mindfolio", to: "/mindfolios/new", icon: "PlusCircle" },
 ],
 },
 ],
 },

 // STOCKS
 {
 title: "Stocks",
 items: [
 { label: "Investment Scoring", to: "/stocks/scoring", icon: "Target" },
 { label: "Scoring Scanner", to: "/stocks/scanner", icon: "Search" },
 // (opțional) Buy Signals / Ideas
 // { label: "Buy Signals", to: "/stocks/signals", icon: "TrendingUp" },
 ],
 },

 // OPTIONS
 {
 title: "Options",
 items: [
 { 
 label: "IV Setups (Auto)", 
 to: "/screener/iv", 
 icon: "Activity"
 },
 { 
 label: "Sell Puts (Auto)", 
 to: "/screener/sell-puts", 
 icon: "ArrowDownCircle"
 },
 { 
 label: "Analytics", 
 to: "/options/analytics", 
 icon: "BarChart2", 
 badge: { text: "NEW", tone: "success" } 
 },
 { 
 label: "Workbench", 
 to: "/options/workbench", 
 icon: "Wrench", 
 badge: { text: "β", tone: "beta" } 
 },
 ],
 },

 // TRADES
 {
 title: "Trades",
 items: [
 { label: "Preview Queue", to: "/trades/preview", icon: "ClipboardList" },
 { label: "Orders (SIM)", to: "/trades/orders/sim", icon: "ReceiptText" },
 { 
 label: "Orders (Live)", 
 to: "/trades/orders/live", 
 icon: "CreditCard",
 visible: (c) => !!c.flags.ORDERS_LIVE 
 },
 ],
 },

 // ANALYTICS
 {
 title: "Analytics",
 items: [
 { label: "Backtests", to: "/analytics/backtests", icon: "BarChart3" },
 { label: "Verified Chains", to: "/analytics/verified", icon: "ShieldCheck", badge: verifiedBadge },
 ],
 },

 // DATA PROVIDERS
 {
 title: "Data Providers",
 items: [
 { label: "TradeStation", to: "/providers/ts", icon: "Building2" },
 { 
 label: "Quotes (TS)", 
 to: "/md/quotes", 
 icon: "Sparkle",
 visible: (c) => !!c.flags.TS_LIVE, 
 badge: tsLiveBadge 
 },
 { 
 label: "Option Chain (TS)", 
 to: "/md/chain", 
 icon: "Grid3X3",
 visible: (c) => !!c.flags.TS_LIVE 
 },
 { label: "Unusual Whales", to: "/providers/uw", icon: "Fish" },
 ],
 },

 // OPS / DIAGNOSTICS (admin only)
 {
 title: "Ops / Diagnostics",
 items: [
 { 
 label: "Redis Diag", 
 to: "/ops/redis", 
 icon: "ServerCog", 
 visible: (c) => c.role === "admin" 
 },
 { 
 label: "Backtest Ops", 
 to: "/ops/bt", 
 icon: "DatabaseZap", 
 visible: (c) => c.role === "admin" 
 },
 { 
 label: "System Diagnostics", 
 to: "/ops/diagnostics", 
 icon: "Heartbeat", 
 visible: (c) => c.role === "admin" 
 },
 { 
 label: "Warm-up", 
 to: "/ops/warmup", 
 icon: "Timer", 
 visible: (c) => c.role === "admin" 
 },
 { 
 label: "Rate Limits", 
 to: "/ops/ratelimits", 
 icon: "Gauge", 
 visible: (c) => c.role === "admin" 
 },
 ],
 },

 // SETTINGS
 {
 title: "Settings",
 items: [
 { label: "Risk & Gates", to: "/settings/gates", icon: "Shield" },
 { label: "Accounts", to: "/settings/accounts", icon: "UserCog" },
 { label: "API Keys", to: "/settings/keys", icon: "KeyRound" },
 ],
 },

 // HELP
 {
 title: "Help",
 items: [
 { label: "Docs", to: "/help/docs", icon: "BookOpenCheck" },
 ],
 },
 ];
}