// =============================================
// FlowMind — Sidebar Config (Safe Minimal)
// =============================================

// Helpers pentru badge/gating
const ivBadge = (ctx) => ctx.metrics?.ivOnline ? { text: "IV", tone: "success" } : { text: "OFF", tone: "warn" };
const verifiedBadge = (ctx) => (ctx.metrics?.verifiedRatio ?? 0) >= 0.2 ? { text: "verified", tone: "verified" } : { text: "low", tone: "warn" };
const tsLiveBadge = (ctx) => ctx.flags?.TS_LIVE ? { text: "LIVE", tone: "live" } : { text: "OFF", tone: "warn" };

const ivDependentDisabled = (ctx) => !ctx.metrics?.ivOnline;
const ivDisabledReason = () => "IV service offline";

export function buildNav(ctx) {
  return [
    // OVERVIEW
    {
      title: "Overview",
      items: [
        { label: "Dashboard", to: "/dashboard", icon: "LayoutDashboard" },
      ],
    },

    // ACCOUNT & PORTFOLIOS
    {
      title: "Account",
      items: [
        { label: "Account Balance", to: "/account/balance", icon: "Wallet" },
        {
          label: "Portfolio Manager", 
          to: "/portfolios",  // Direct link to portfolios list
          icon: "Briefcase",
          children: [
            // View all portfolios
            { label: "View All Portfolios", to: "/portfolios", icon: "List" },
            // Dynamic portfolios
            ...((ctx.portfolios || []).map(p => ({
              label: p.name,
              to: `/portfolios/${p.id}`,
              icon: "FolderKanban",
              badge: p.nav ? { text: `$${Math.round(p.nav/1000)}k`, tone: "default" } : undefined,
            }))),
            // Create new
            { label: "+ Create Portfolio", to: "/portfolios/new", icon: "PlusCircle" },
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
          icon: "Droplet",
          badge: { text: "NEW", tone: "success" }
        },
        { 
          label: "Market Movers", 
          to: "/market-movers", 
          icon: "Activity",
          badge: { text: "NEW", tone: "success" }
        },
        { 
          label: "Congress Trades", 
          to: "/congress-trades", 
          icon: "Building",
          badge: { text: "NEW", tone: "success" }
        },
        { 
          label: "Institutional", 
          to: "/institutional", 
          icon: "Building2",
          badge: { text: "NEW", tone: "success" }
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
          visible: (c) => !!c.flags?.ORDERS_LIVE 
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
          visible: (c) => !!c.flags?.TS_LIVE, 
          badge: tsLiveBadge 
        },
        { 
          label: "Option Chain (TS)", 
          to: "/md/chain", 
          icon: "Grid3X3",
          visible: (c) => !!c.flags?.TS_LIVE 
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
          label: "Emergent Status", 
          to: "/ops/emergent", 
          icon: "Heartbeat", 
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