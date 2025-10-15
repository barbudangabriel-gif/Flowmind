import React from "react";
import StatCard from "../components/dashboard/StatCard";
import TopPortfolios from "../components/dashboard/TopPortfolios";
import QuickActionButton from "../components/dashboard/QuickActionButton";
import SignalCard from "../components/dashboard/SignalCard";
import ActiveStrategies from "../components/dashboard/ActiveStrategies";
import FlowSummaryWidget from "../components/dashboard/FlowSummaryWidget";
import DarkPoolWidget from "../components/dashboard/DarkPoolWidget";
import NewsTickerWidget from "../components/dashboard/NewsTickerWidget";
import TopScoredStocks from "../components/dashboard/TopScoredStocks";
import SystemHealthWidget from "../components/dashboard/SystemHealthWidget";
import AlertsWidget from "../components/dashboard/AlertsWidget";

export default function Dashboard() {
  // TODO: Replace with real API calls
  const totalNAV = 125000.5;
  const dailyChange = 2450.25;
  const dailyPnL = 2450.25;
  const dailyPnLPct = 1.96;
  const totalCash = 35000.0;
  const portfolioCount = 3;

  // Mock data - replace with API calls
  const ivSignals = [
    { symbol: "TSLA", strategy: "Iron Condor", edge: "8.5%", confidence: "82%" },
    { symbol: "AAPL", strategy: "Calendar Spread", edge: "6.2%", confidence: "75%" }
  ];

  const sellPutsSignals = [
    { symbol: "NVDA", strike: "$450", premium: "$850", probability: "71%" },
    { symbol: "MSFT", strike: "$380", premium: "$620", probability: "68%" }
  ];

  const flowSummary = [
    { symbol: "TSLA", net_premium: 5200000, sentiment: "bullish" },
    { symbol: "AAPL", net_premium: 3800000, sentiment: "neutral" },
    { symbol: "NVDA", net_premium: 2900000, sentiment: "bullish" }
  ];

  const darkPoolActivity = [
    { symbol: "MSFT", volume: 2500000, premium: 1250000 },
    { symbol: "GOOGL", volume: 1800000, premium: 900000 }
  ];

  const systemServices = [
    { name: "TradeStation", status: "connected", mode: "live" },
    { name: "Unusual Whales", status: "connected", rateLimit: 450 },
    { name: "MongoDB", status: "connected" },
    { name: "Redis", status: "fallback", fallback: true }
  ];

  const recentAlerts = [
    { timestamp: "2025-10-15T09:15:00Z", type: "position_threshold", message: "TSLA position exceeded 10% of portfolio", severity: "warning" },
    { timestamp: "2025-10-15T08:30:00Z", type: "module_stop_loss", message: "IV Service daily loss limit approaching", severity: "warning" }
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">📊 FlowMind Dashboard</h1>
        <p className="text-gray-400">Real-time overview of your trading activity and market intelligence</p>
      </div>

      {/* Section 1: Portfolio Overview */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">💼 Portfolio Overview</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <StatCard title="Total Portfolio Value" value={totalNAV} change={dailyChange} icon="💼" gradient="from-blue-500/20 to-blue-600/20" />
          <StatCard title="Today's P&L" value={dailyPnL} percentage={dailyPnLPct} icon="📈" gradient="from-green-500/20 to-green-600/20" />
          <StatCard title="Available Cash" value={totalCash} subtitle={`Across ${portfolioCount} portfolios`} icon="💵" gradient="from-purple-500/20 to-purple-600/20" />
        </div>
        <TopPortfolios limit={3} />
      </div>

      {/* Section 2: Options Analytics Highlights */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">📊 Options Analytics</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SignalCard
            title="🎯 IV Service Signals"
            data={ivSignals}
            fields={['symbol', 'strategy', 'edge', 'confidence']}
            emptyText="No high-confidence setups today"
            ctaLink="/options/iv-service"
          />
          <SignalCard
            title="💰 Sell Puts Opportunities"
            data={sellPutsSignals}
            fields={['symbol', 'strike', 'premium', 'probability']}
            emptyText="No quality CSP setups found"
            ctaLink="/options/sell-puts"
          />
        </div>
        <ActiveStrategies totalStrategies={12} totalPremium={15250} expiringThisWeek={3} />
      </div>

      {/* Section 3: Market Intelligence */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">🔍 Market Intelligence</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FlowSummaryWidget
            title="📊 Options Flow (Top 5)"
            data={flowSummary}
            showSentiment={true}
            ctaLink="/flow"
          />
          <DarkPoolWidget
            title="🌊 Dark Pool Highlights"
            data={darkPoolActivity}
            threshold={1000000}
          />
        </div>
        <NewsTickerWidget sources={['congress', 'insiders', 'news']} limit={10} />
      </div>

      {/* Section 4: Stock Scoring Insights */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">🎓 Investment Scoring - Today's Top Picks</h2>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <TopScoredStocks limit={5} ctaText="Run Full Scan" ctaLink="/stocks/scoring" />
        </div>
      </div>

      {/* Section 5: Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">⚡ Quick Actions</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickActionButton icon="➕" label="Create Portfolio" href="/portfolios/new" gradient="from-blue-600 to-blue-700" />
          <QuickActionButton icon="🔨" label="Open Builder" href="/builder" gradient="from-green-600 to-green-700" />
          <QuickActionButton icon="🔍" label="Run IV Scan" href="/options/iv-service" gradient="from-purple-600 to-purple-700" />
          <QuickActionButton icon="📈" label="View Flow" href="/flow" gradient="from-orange-600 to-orange-700" />
        </div>
      </div>

      {/* Section 6: System Health & Alerts */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">🔧 System Status</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SystemHealthWidget services={systemServices} />
          <AlertsWidget alerts={recentAlerts} types={['position_threshold', 'module_stop_loss', 'api_error']} limit={5} />
        </div>
      </div>
    </div>
  );
}
