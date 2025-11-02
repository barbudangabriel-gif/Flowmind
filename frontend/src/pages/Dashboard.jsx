import React from "react";
import StatCard from "../components/dashboard/StatCard";
import TopMindfolios from "../components/dashboard/TopMindfolios";
import QuickActionButton from "../components/dashboard/QuickActionButton";
import SignalCard from "../components/dashboard/SignalCard";
import ActiveStrategies from "../components/dashboard/ActiveStrategies";
import FlowSummaryWidget from "../components/dashboard/FlowSummaryWidget";
import DarkPoolWidget from "../components/dashboard/DarkPoolWidget";
import NewsTickerWidget from "../components/dashboard/NewsTickerWidget";
import TopScoredStocks from "../components/dashboard/TopScoredStocks";
import SystemHealthWidget from "../components/dashboard/SystemHealthWidget";
import AlertsWidget from "../components/dashboard/AlertsWidget";
import MiniTicker from "../components/dashboard/MiniTicker";

export default function Dashboard() {
  // TODO: Replace with real API calls
  const totalNAV = 125000.5;
  const dailyChange = 2450.25;
  const dailyPnL = 2450.25;
  const dailyPnLPct = 1.96;
  const totalCash = 35000.0;
  const mindfolioCount = 3;

  // Mock sparkline data - EQUITY CURVE based (cumulative P&L from trades)
  // Simulate real trade results building up to final values
  
  // Total Mindfolio Value: equity curve (14 days of cumulative value)
  // Start: 122,550.25 → End: 125,000.5 (net +2,450.25 from dailyChange)
  const navSparkline = [
    122550.25,  // Day 1: starting value
    122550.25 + 320,   // Day 2: +$320 from trade
    122870.25 - 480,   // Day 3: -$480 losing trade
    122390.25 + 890,   // Day 4: +$890 winning trade
    123280.25 - 320,   // Day 5: -$320 small loss
    122960.25 + 1150,  // Day 6: +$1,150 big win
    124110.25 + 240,   // Day 7: +$240 small win
    124350.25 - 180,   // Day 8: -$180 loss
    124170.25 + 670,   // Day 9: +$670 win
    124840.25 - 290,   // Day 10: -$290 loss
    124550.25 + 580,   // Day 11: +$580 win
    125130.25 - 420,   // Day 12: -$420 loss
    124710.25 + 540,   // Day 13: +$540 win
    125250.25 - 249.75, // Day 14: -$249.75 adjustment → 125,000.5
  ];
  
  // Today's P&L: intraday equity curve (starting from 0, ending at +2,450.25)
  // Simulates trades throughout the day
  const pnlSparkline = [
    0,          // Market open
    0 - 180,    // First trade: -$180 loss
    -180 + 420, // Second trade: +$420 win → +$240 cumulative
    240 - 150,  // Third trade: -$150 loss → +$90
    90 + 680,   // Fourth trade: +$680 win → +$770
    770 - 320,  // Fifth trade: -$320 loss → +$450
    450 + 890,  // Sixth trade: +$890 big win → +$1,340
    1340 + 320, // Seventh trade: +$320 win → +$1,660
    1660 - 240, // Eighth trade: -$240 loss → +$1,420
    1420 + 580, // Ninth trade: +$580 win → +$2,000
    2000 + 250, // Tenth trade: +$250 win → +$2,250
    2250 + 200.25, // Final trade: +$200.25 → +$2,450.25
  ];
  
  // Available Cash: reflects deposits, withdrawals, and settled trades (14 days)
  const cashSparkline = [
    32000,  // Day 1
    32000 + 1500, // Day 2: +$1,500 deposit
    33500 - 800,  // Day 3: -$800 used for margin
    32700 + 2100, // Day 4: +$2,100 trade settlement
    34800 - 1300, // Day 5: -$1,300 withdrawal
    33500 + 1800, // Day 6: +$1,800 trade profit
    35300 - 600,  // Day 7: -$600 used for position
    34700 + 900,  // Day 8: +$900 closed position
    35600 - 1400, // Day 9: -$1,400 used for new trades
    34200 + 1200, // Day 10: +$1,200 profit
    35400 - 800,  // Day 11: -$800 margin call
    34600 + 1100, // Day 12: +$1,100 settlement
    35700 - 1000, // Day 13: -$1,000 new positions
    34700 + 300,  // Day 14: +$300 adjustment → 35,000
  ];

  // Mini ticker sparklines (intraday data for major indices)
  const spySparkline = [660.20, 660.50, 659.80, 660.10, 659.50, 659.30, 659.70, 659.20, 659.48];
  const qqqSparkline = [599.10, 599.50, 598.90, 599.20, 598.50, 598.80, 598.40, 598.90, 598.76];
  const diaSparkline = [460.20, 460.10, 459.80, 460.00, 459.40, 459.60, 459.30, 459.70, 459.56];
  const iwmSparkline = [250.10, 249.50, 248.20, 247.80, 246.50, 245.80, 245.20, 244.90, 244.72];

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
 { timestamp: "2025-10-15T09:15:00Z", type: "position_threshold", message: "TSLA position exceeded 10% of mindfolio", severity: "warning" },
 { timestamp: "2025-10-15T08:30:00Z", type: "module_stop_loss", message: "IV Service daily loss limit approaching", severity: "warning" }
 ];

  return (
    <div className="bg-[#0f1419] min-h-screen p-4">
      <div className="max-w-[1800px] mx-auto space-y-4">
        {/* Header */}
        <div>
          <h1 className="text-base text-white mb-1">Dashboard</h1>
          <p className="text-sm text-gray-400">
            Overview of your portfolio, accounts, and market activity
          </p>
        </div>

      {/* Section 1: Mindfolio Overview */}
      <div>
        <h2 className="text-base text-white mb-4">Mindfolio Overview</h2>
        
        {/* Mini Tickers Row - Above right two cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-3">
          <div></div> {/* Empty space for left card */}
          <div className="grid grid-cols-2 gap-4 px-4">
            <MiniTicker symbol="SPY" price={659.48} changePct={-0.86} sparklineData={spySparkline} />
            <MiniTicker symbol="QQQ" price={598.76} changePct={-0.57} sparklineData={qqqSparkline} />
          </div>
          <div className="grid grid-cols-2 gap-4 px-4">
            <MiniTicker symbol="DIA" price={459.56} changePct={-0.68} sparklineData={diaSparkline} />
            <MiniTicker symbol="IWM" price={244.72} changePct={-2.24} sparklineData={iwmSparkline} />
          </div>
        </div>
        
        {/* Main Stat Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <StatCard 
            title="Total Mindfolio Value" 
            value={totalNAV} 
            change={dailyChange} 
            icon="" 
            gradient="from-blue-500/20 to-blue-600/20" 
            sparklineData={navSparkline}
          />
          <StatCard 
            title="Today's P&L" 
            value={dailyPnL} 
            percentage={dailyPnLPct} 
            icon="" 
            gradient="from-green-500/20 to-green-600/20" 
            sparklineData={pnlSparkline}
          />
          <StatCard 
            title="Available Cash" 
            value={totalCash} 
            subtitle={`Across ${mindfolioCount} mindfolios`} 
            icon="" 
            gradient="from-purple-500/20 to-purple-600/20" 
            sparklineData={cashSparkline}
            isNeutralMetric={true}
          />
        </div>
        <TopMindfolios limit={3} />
      </div> {/* Section 2: Options Analytics Highlights */}
 <div>
 <h2 className="text-base text-white mb-4">Options Analytics</h2>
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
 <SignalCard
 title=" IV Service Signals"
 data={ivSignals}
 fields={['symbol', 'strategy', 'edge', 'confidence']}
 emptyText="No high-confidence setups today"
 ctaLink="/options/iv-service"
 />
 <SignalCard
 title=" Sell Puts Opportunities"
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
 <h2 className="text-base text-white mb-4">Market Intelligence</h2>
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
 <FlowSummaryWidget
 title=" Options Flow (Top 5)"
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
 <h2 className="text-base text-white mb-4">Investment Scoring - Today's Top Picks</h2>
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4">
 <TopScoredStocks limit={5} ctaText="Run Full Scan" ctaLink="/stocks/scoring" />
 </div>
 </div>

 {/* Section 5: Quick Actions */}
 <div>
 <h2 className="text-base text-white mb-4">Quick Actions</h2>
 <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
 <QuickActionButton icon="" label="Create Mindfolio" href="/mindfolio/new" gradient="from-blue-600 to-blue-700" />
 <QuickActionButton icon="" label="Open Builder" href="/builder" gradient="from-green-600 to-green-700" />
 <QuickActionButton icon="" label="Run IV Scan" href="/options/iv-service" gradient="from-purple-600 to-purple-700" />
 <QuickActionButton icon="" label="View Flow" href="/flow" gradient="from-orange-600 to-orange-700" />
 </div>
 </div>

 {/* Section 6: System Health & Alerts */}
 <div>
 <h2 className="text-base text-white mb-4">System Status</h2>
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
 <SystemHealthWidget services={systemServices} />
 <AlertsWidget alerts={recentAlerts} types={['position_threshold', 'module_stop_loss', 'api_error']} limit={5} />
 </div>
 </div>
 </div>
 </div>
 );
}
