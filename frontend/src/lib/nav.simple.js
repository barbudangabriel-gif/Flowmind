// =============================================
// FlowMind — Sidebar Config (Safe Minimal)
// =============================================

const ivDependentDisabled = (ctx) => !ctx.metrics?.ivOnline;
const ivDisabledReason = () => "IV service offline";

export function buildNav(ctx) {
 return [
 // OVERVIEW
 {
 title: "Overview",
 isComplete: true,
 items: [
 { label: "Dashboard", to: "/dashboard", icon: "LayoutDashboard" },
 ],
 },

 // ACCOUNTS
 {
 title: "Accounts",
 isComplete: true,
 items: [
 { label: "Account Balance", to: "/account/balance", icon: "Wallet" },
 ],
 },

 // MINDFOLIO MANAGER
 {
 title: "Mindfolio Manager",
 items: [
 // View all mindfolios with dynamic children
 { 
 label: "View All Mindfolios", 
 to: "/mindfolio", 
 icon: "List",
 children: [
 // Dynamic mindfolios
 ...((ctx.mindfolios || []).map(p => ({
 label: p.name,
 to: `/mindfolio/${p.id}`,
 icon: "FolderKanban",
 badge: p.nav ? { text: `$${Math.round(p.nav/1000)}k`, tone: "default" } : undefined,
 }))),
 // Placeholder if no mindfolios
 ...((ctx.mindfolios || []).length === 0 ? [
 { label: "No mindfolios yet", to: "/mindfolio/new", icon: "FileX" }
 ] : [])
 ]
 },
 // Create new
 { label: "+ Create Mindfolio", to: "/mindfolio/new", icon: "PlusCircle" },
 // Mindfolio Analytics
 { label: "Mindfolio Analytics", to: "/mindfolio/analytics", icon: "BarChart3" },
 // Smart Rebalancing
 { label: "Smart Rebalancing", to: "/mindfolio/rebalancing", icon: "Scale" },
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
	 label: "Simulator",
	 to: "/simulator",
	 icon: "BarChart2"
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
 label: "Algos", 
 to: "/screener/iv", 
 icon: "Bot",
 children: [
 { label: "IV Setups (Auto)", to: "/screener/iv", icon: "Activity" },
 { label: "Iron Condor Scanner", to: "/screener/iv?strategy=IRON_CONDOR", icon: "Target" },
 { label: "Calendar Scanner", to: "/screener/iv?strategy=CALENDAR", icon: "Calendar" },
 { label: "Diagonal Scanner", to: "/screener/iv?strategy=DIAGONAL", icon: "TrendingUp" },
 { label: "Double Diagonal", to: "/screener/iv?strategy=DOUBLE_DIAGONAL", icon: "Layers" },
 { label: "Sell Puts (Auto)", to: "/screener/sell-puts", icon: "ArrowDownCircle" },
 { label: "Put Selling Engine", to: "/screener/sell-puts", icon: "ArrowDown" },
 { label: "Covered Calls", to: "/screener/covered-calls", icon: "Shield" },
 { label: "Cash-Secured Puts", to: "/screener/csp", icon: "DollarSign" },
 { label: "Preview Queue", to: "/trades/preview", icon: "ClipboardList" },
 { label: "Orders (SIM)", to: "/trades/orders/sim", icon: "ReceiptText" },
 { label: "Orders (LIVE)", to: "/trades/orders/live", icon: "CreditCard" },
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
 label: "Data & APIs", 
 to: "/settings/keys", 
 icon: "KeyRound",
 children: [
 { label: "TradeStation", to: "/providers/ts", icon: "Building2" },
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