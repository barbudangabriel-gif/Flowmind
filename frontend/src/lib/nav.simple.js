// =============================================
// FlowMind — Sidebar Config (Safe Minimal)
// =============================================

const ivDependentDisabled = (ctx) => !ctx.metrics?.ivOnline;
const ivDisabledReason = () => "IV service offline";

export function buildNav(ctx) {
 console.log('[nav.simple.js] Building nav with ctx.mindfolios:', ctx.mindfolios);
 return [
 // OVERVIEW
 {
 title: "Overview",
 isComplete: true,
 items: [
 { label: "Home (Dev)", to: "/", icon: "Home" },
 { label: "Dashboard", to: "/dashboard", icon: "LayoutDashboard" },
 ],
 },

 // ACCOUNTS
 {
 title: "Accounts",
 isComplete: true,
 items: [
 { 
 label: "Aggregate View", 
 to: "/account/aggregate", 
 icon: "Layers",
 description: "Unified view across all brokers"
 },
 { 
 label: "TradeStation", 
 to: "/account/tradestation", 
 icon: "Wallet",
 children: [
 { label: "MF Master Equity", to: "/mindfolio/mf_909a45e4a3d7/legacy", icon: "TrendingUp" },
 { label: "MF Master Futures", to: "/mindfolio/mf_909a45e4a3d7/legacy", icon: "Zap" },
 ]
 },
 { 
 label: "Tastytrade", 
 to: "/account/tastytrade", 
 icon: "Wallet",
 children: [
 { label: "MF Master Equity", to: "/mindfolio/mf_207943a4e6a8/legacy", icon: "TrendingUp" },
 { label: "MF Master Futures", to: "/mindfolio/mf_207943a4e6a8/legacy", icon: "Zap" },
 { label: "Crypto", to: "/account/tastytrade/crypto", icon: "Bitcoin" },
 ]
 },
 { 
 label: "Interactive Brokers", 
 to: "/account/ibkr", 
 icon: "Globe",
 children: [
 { label: "MF Master Equity", to: "/mindfolio/mf_2c171f1be938/legacy", icon: "TrendingUp" },
 { label: "MF Master Futures", to: "/mindfolio/mf_2c171f1be938/legacy", icon: "Zap" },
 { label: "Forex", to: "/account/ibkr/forex", icon: "DollarSign" },
 ]
 },
 ],
 },

 // MINDFOLIO MANAGER
 {
 title: "Mindfolio Manager",
 items: [
 // Main manager page
 { 
 label: "Manager Dashboard", 
 to: "/mindfolio", 
 icon: "LayoutDashboard"
 },
 // View all mindfolios with dynamic children
 { 
 label: "My Mindfolios", 
 to: "/mindfolio", 
 icon: "FolderKanban",
 children: [
 // Filter out master mindfolios from sidebar
 ...((ctx.mindfolios || [])
 .filter(p => !p.is_master)
 .map(p => ({
 label: p.name,
 to: `/mindfolio/${p.id}`,
 icon: "FolderKanban",
 badge: (p.nav || p.cash_balance) ? { text: `$${Math.round((p.nav || p.cash_balance)/1000)}k`, tone: "default" } : undefined,
 }))),
 // Placeholder if no regular mindfolios (show master mindfolios separately)
 ...((ctx.mindfolios || []).filter(p => !p.is_master).length === 0 ? [
 { label: "Create your first mindfolio", to: "/mindfolio", icon: "Plus" }
 ] : [])
 ]
 },
 // Broker Master Mindfolios (separate section)
 ...((ctx.mindfolios || []).filter(p => p.is_master).length > 0 ? [{
 label: "Broker Masters", 
 to: "/mindfolio", 
 icon: "Building2",
 badge: { text: "Auto-sync", tone: "success" },
 children: [
 ...((ctx.mindfolios || [])
 .filter(p => p.is_master)
 .map(p => ({
 label: p.name || `${p.broker} Master`,
 to: `/mindfolio/${p.id}`,
 icon: "Building2",
 badge: p.broker ? { text: p.broker, tone: "default" } : undefined,
 })))
 ]
 }] : []),
 ],
 },

 // STOCKS
 {
 title: "Stocks Data",
 items: [
 { label: "Investment Scoring", to: "/stocks/scoring", icon: "Target" },
 { label: "Scoring Scanner", to: "/stocks/scanner", icon: "Search" },
 { label: "Top Picks", to: "/stocks/top-picks", icon: "TrendingUp" },
 ],
 },

 // OPTIONS (Quick Tools)
 {
 title: "Options Data",
 isComplete: true,
 items: [
 { 
 label: "Builder", 
 to: "/builder", 
 icon: "Sparkles"
 },
 { 
 label: "Strategy Library", 
 to: "/strategies", 
 icon: "Library"
 },
 { 
 label: "Analytics", 
 to: "/options/analytics", 
 icon: "BarChart2",
 children: [
 { label: "Backtests", to: "/analytics/backtests", icon: "BarChart3" },
 { label: "Verified Chains", to: "/analytics/verified", icon: "ShieldCheck" },
 ]
 },
 { 
 label: "Algos Module", 
 to: "/screener/iv", 
 icon: "Bot",
 children: [
 { label: "IV Setups (Auto)", to: "/screener/iv", icon: "Activity" },
 { label: "Put Selling Engine", to: "/screener/sell-puts", icon: "ArrowDown" },
 { label: "SPY Hedge", to: "/screener/spy-hedge", icon: "Shield" },
 ]
 },
 { 
 label: "Option Chain (TS)", 
 to: "/md/chain", 
 icon: "Grid3X3",
 visible: (c) => !!c.flags?.TS_LIVE 
 },
 ],
 },

 // MARKET INTELLIGENCE
 {
 title: "Market Intelligence",
 items: [
 { 
 label: "Flow Summary", 
 to: "/flow", 
 icon: "TrendingUp" 
 },
 { 
 label: "Dark Pool", 
 to: "/dark-pool", 
 icon: "Droplet"
 },
 { 
 label: "Market Movers", 
 to: "/market-movers", 
 icon: "Activity"
 },
 { 
 label: "Congress Trades", 
 to: "/congress-trades", 
 icon: "Building"
 },
 { 
 label: "Institutional", 
 to: "/institutional", 
 icon: "Building2"
 },
 ],
 },

 // SETTINGS
 {
 title: "Settings",
 isComplete: true,
 items: [
 { label: "Risk & Gates", to: "/settings/gates", icon: "Shield" },
 { label: "Screensaver", to: "/settings/screensaver", icon: "Monitor" },
 { 
 label: "Trading Tools", 
 to: "/simulator", 
 icon: "Wrench",
 children: [
 { label: "Trade Simulator", to: "/simulator", icon: "PlayCircle" },
 { label: "Iron Condor Scanner", to: "/screener/iv?strategy=IRON_CONDOR", icon: "Target" },
 { label: "Calendar Scanner", to: "/screener/iv?strategy=CALENDAR", icon: "Calendar" },
 { label: "Diagonal Scanner", to: "/screener/iv?strategy=DIAGONAL", icon: "TrendingUp" },
 { label: "Double Diagonal", to: "/screener/iv?strategy=DOUBLE_DIAGONAL", icon: "Layers" },
 { label: "Covered Calls", to: "/screener/covered-calls", icon: "Shield" },
 { label: "Cash-Secured Puts", to: "/screener/csp", icon: "DollarSign" },
 { label: "Preview Queue", to: "/trades/preview", icon: "ClipboardList" },
 { label: "Orders (SIM)", to: "/trades/orders/sim", icon: "ReceiptText" },
 { label: "Orders (LIVE)", to: "/trades/orders/live", icon: "CreditCard" },
 ]
 },
 { 
 label: "Data & APIs", 
 to: "/settings/keys", 
 icon: "KeyRound",
 children: [
 { label: "TradeStation", to: "/tradestation/login", icon: "Building2" },
 { label: "Unusual Whales", to: "/providers/uw", icon: "Fish" },
 { label: "API Keys", to: "/settings/keys", icon: "Key" },
 ]
 },
 { 
 label: "System Diagnostics", 
 to: "/ops/redis", 
 icon: "ServerCog",
 children: [
 { label: "Redis Cache", to: "/ops/redis", icon: "Database" },
 { label: "Backtest Ops", to: "/ops/bt", icon: "DatabaseZap" },
 ]
 },
 ],
 },

 // HELP
 {
 title: "Help",
 isComplete: true,
 items: [
 { label: "Docs", to: "/help/docs", icon: "BookOpenCheck" },
 ],
 },
 ];
}