import React, { useMemo, useState } from "react";
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid } from "recharts";

// Helper functions
function range(start, end, step = 10) {
  const out = [];
  for (let x = start; x <= end; x += step) out.push(x);
  return out;
}

function buildChartData({ xMin = 0, xMax = 400, step = 10, payoffFn }) {
  const xs = range(xMin, xMax, step);
  const raw = xs.map((x) => {
    const y = payoffFn(x);
    return { x, y, pos: y > 0 ? y : 0, neg: y < 0 ? y : 0 };
  });
  return raw;
}

function formatUSD(n, showSign = true) {
  const sign = n < 0 ? "-" : (showSign && n > 0 ? "+" : "");
  const v = Math.abs(n);
  return `${sign}$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

// Strategy Cards Component
function StrategyCard({ 
  title, 
  subtitle, 
  returnOnRisk, 
  returnLabel = "Return on Risk",
  chance, 
  profit, 
  risk, 
  riskLabel = "Risk",
  chartData, 
  idSuffix,
  spotPrice = 149.53,
  targetPrice = 263.91 
}) {
  return (
    <div className="bg-[#2c3e50] rounded-none p-4 border border-[#34495e] shadow-lg">
      {/* Header */}
      <div className="mb-3">
        <h3 className="text-white text-lg font-bold">{title}</h3>
        <p className="text-gray-400 text-xs">{subtitle}</p>
      </div>
      
      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <div className="text-yellow-400 text-lg font-bold">{returnOnRisk}</div>
          <div className="text-gray-400 text-xs">{returnLabel}</div>
        </div>
        <div>
          <div className="text-green-400 text-lg font-bold">{chance}</div>
          <div className="text-gray-400 text-xs">Chance</div>
        </div>
      </div>
      
      {/* Profit/Risk Row */}
      <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
        <div>
          <span className="text-green-400 font-semibold">{profit}</span>
          <span className="text-gray-400"> Profit</span>
        </div>
        <div>
          <span className="text-red-400 font-semibold">{risk}</span>
          <span className="text-gray-400"> {riskLabel}</span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-40 mb-3">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <defs>
              <linearGradient id={`greenGrad-${idSuffix}`} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#2ecc71" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#2ecc71" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id={`redGrad-${idSuffix}`} x1="0" x2="0" y1="1" y2="0">
                <stop offset="0%" stopColor="#e74c3c" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#e74c3c" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            
            <CartesianGrid stroke="#34495e" strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#7f8c8d", fontSize: 10 }}
              tickFormatter={(v) => `$${v}`}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#7f8c8d", fontSize: 10 }}
              tickFormatter={(v) => v >= 0 ? `$${Math.abs(v)}` : `-$${Math.abs(v)}`}
            />
            
            {/* Zero line */}
            <ReferenceLine y={0} stroke="#7f8c8d" strokeDasharray="2 2" />
            
            {/* Spot price line */}
            <ReferenceLine x={spotPrice} stroke="#3498db" strokeDasharray="2 2" strokeWidth={1} />
            
            {/* Target price line */}
            <ReferenceLine x={targetPrice} stroke="#f39c12" strokeDasharray="2 2" strokeWidth={1} />
            
            {/* Fill areas */}
            <Area 
              type="monotone" 
              dataKey="pos" 
              stroke="none" 
              fill={`url(#greenGrad-${idSuffix})`} 
            />
            <Area 
              type="monotone" 
              dataKey="neg" 
              stroke="none" 
              fill={`url(#redGrad-${idSuffix})`} 
            />
            
            {/* P&L Lines - Green for profit, Red for loss */}
            <Line 
              type="monotone" 
              dataKey="pos" 
              stroke="#2ecc71" 
              strokeWidth={2.5} 
              dot={false} 
              connectNulls={false}
            />
            <Line 
              type="monotone" 
              dataKey="neg" 
              stroke="#e74c3c" 
              strokeWidth={2.5} 
              dot={false} 
              connectNulls={false}
            />
            
            <Tooltip
              formatter={(value) => [formatUSD(value), "P&L"]}
              labelFormatter={(label) => `Price: $${label}`}
              contentStyle={{ 
                background: "#2c3e50", 
                border: "1px solid #34495e", 
                borderRadius: "8px",
                color: "#ecf0f1"
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Open in Builder Button */}
      <button className="w-full bg-[#3498db] hover:bg-[#2980b9] text-white py-2 px-4 rounded-lg font-semibold transition-colors">
        Open in Builder
      </button>
    </div>
  );
}

// Sentiment Circle Component
function SentimentCircle({ icon, label, active, onClick }) {
  const getColors = () => {
    if (label.includes('Bearish')) return active ? 'bg-red-500' : 'bg-gray-700 border-red-500';
    if (label.includes('Bullish')) return active ? 'bg-green-500' : 'bg-gray-700 border-green-500';
    if (label === 'Directional') return active ? 'bg-purple-500' : 'bg-gray-700 border-purple-500';
    return active ? 'bg-blue-500' : 'bg-gray-700 border-blue-500';
  };

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={onClick}
        className={`w-16 h-16 rounded-full border-2 flex items-center justify-center text-2xl transition-all ${getColors()}`}
      >
        {icon}
      </button>
      <span className="text-white text-xs mt-2 text-center">{label}</span>
    </div>
  );
}

export default function OptionsModule() {
  const [symbol, setSymbol] = useState("CRCL");
  const [spotPrice, setSpotPrice] = useState(149.53);
  const [targetPrice, setTargetPrice] = useState(263.91);
  const [sentiment, setSentiment] = useState("Bullish");

  // Chart data for each strategy
  const chartData = useMemo(() => {
    const longCallData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => Math.max(0, S - 95) * 100 - 6455
    });

    const coveredCallData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => (S - spotPrice) * 100 + Math.min(0, 210 - S) * 100 + 1285
    });

    const cashSecuredPutData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => -Math.max(0, 125 - S) * 100 + 2615
    });

    const shortPutData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => -Math.max(0, 115 - S) * 100 + 2405
    });

    const bullCallSpreadData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => Math.min(Math.max(0, S - 95), 265 - 95) * 100 - 5025
    });

    const bullPutSpreadData = buildChartData({
      xMin: 0, xMax: 400, step: 20,
      payoffFn: (S) => 1810 - Math.min(Math.max(0, 185 - S), 185 - 90) * 100
    });

    return {
      longCall: longCallData,
      coveredCall: coveredCallData,
      cashSecuredPut: cashSecuredPutData,
      shortPut: shortPutData,
      bullCallSpread: bullCallSpreadData,
      bullPutSpread: bullPutSpreadData
    };
  }, [spotPrice]);

  const sentiments = [
    { icon: "📉", label: "Very Bearish" },
    { icon: "📈", label: "Bearish" },
    { icon: "➡️", label: "Neutral" },
    { icon: "⚡", label: "Directional" },
    { icon: "📈", label: "Bullish" },
    { icon: "📊", label: "Very Bullish" }
  ];

  const months = ["Sep", "Oct", "Nov", "Dec", "Jan '26", "Feb", "Mar", "Apr", "Jun", "Dec", "Jan '27"];
  const days = ["12", "19", "26", "17", "21", "19", "16", "20", "20", "17", "18", "18", "15"];

  return (
    <div className="min-h-screen bg-[#1a252f] text-white">
      {/* Header */}
      <div className="bg-[#2c3e50] px-6 py-4 border-b border-[#34495e]">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-500 rounded"></div>
              <span className="text-xl font-bold">OptionStrat</span>
            </div>
            <nav className="hidden md:flex space-x-6">
              <button className="text-gray-300 hover:text-white">Build ▼</button>
              <button className="text-gray-300 hover:text-white">Optimize</button>
              <button className="text-gray-300 hover:text-white">Flow ▼</button>
            </nav>
          </div>
          
          <div className="flex items-center space-x-6">
            <span>Tutorials</span>
            <span>Blog</span>
            <button>My Account ▼</button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        
        {/* Symbol and Price */}
        <div className="flex items-center justify-center space-x-4 mb-6">
          <span className="text-gray-400">Symbol:</span>
          <input 
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="bg-[#34495e] border border-[#4a5f7a] rounded px-2 py-1 text-white w-20"
          />
          <span className="text-2xl font-bold">${spotPrice.toFixed(2)}</span>
          <span className="text-green-400">+7.40%</span>
          <span className="text-green-400">+$10.30</span>
          <span className="text-gray-400 text-sm">🔄 Real-time</span>
        </div>

        {/* News Banner */}
        <div className="bg-[#3498db] rounded-lg p-4 mb-6 text-center">
          <span className="text-white">
            📊 Circle Internet Group shares are trading higher. The company announced a 
            public offering of 10 million shares at $130 per share. 
            <em className="text-blue-200">updated 8/15/25, 8:06 PM</em>
          </span>
          <button className="ml-4 text-blue-200 hover:text-white">✕</button>
        </div>

        {/* Sentiment Circles */}
        <div className="flex justify-center space-x-8 mb-8">
          {sentiments.map((s, i) => (
            <SentimentCircle
              key={s.label}
              icon={s.icon}
              label={s.label}
              active={sentiment === s.label}
              onClick={() => setSentiment(s.label)}
            />
          ))}
        </div>

        {/* Target Price and Budget */}
        <div className="flex items-center justify-center space-x-8 mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Target Price: $</span>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(parseFloat(e.target.value))}
              className="bg-[#34495e] border border-[#4a5f7a] rounded px-2 py-1 text-white w-24"
            />
            <span className="text-gray-400">(+76%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Budget: $</span>
            <input
              placeholder="None"
              className="bg-[#34495e] border border-[#4a5f7a] rounded px-2 py-1 text-gray-400 w-24"
            />
          </div>
        </div>

        {/* Month Tabs */}
        <div className="flex justify-center space-x-2 mb-4">
          {months.map((month, i) => (
            <div key={i} className="text-center">
              <button
                className={`px-3 py-1 rounded text-sm ${
                  month === "Dec" ? "bg-[#3498db] text-white" : "bg-[#34495e] text-gray-300"
                }`}
              >
                {month}
              </button>
              <div className="text-xs text-gray-400 mt-1">{days[i] || ""}</div>
            </div>
          ))}
        </div>

        {/* Max Return/Max Chance Slider */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>← Max Return</span>
            <span>Max Chance →</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="100" 
            defaultValue="50"
            className="w-full h-2 bg-[#34495e] rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Strategy Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StrategyCard
            title="Long Call"
            subtitle="Buy 95C"
            returnOnRisk="162%"
            chance="47%"
            profit="$10,435.59"
            risk="$6,455"
            chartData={chartData.longCall}
            idSuffix="lc"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
          
          <StrategyCard
            title="Covered Call"
            subtitle="Own the underlying, Sell 210C"
            returnOnRisk="63%"
            chance="58%"
            profit="$8,147"
            risk="$12,853"
            chartData={chartData.coveredCall}
            idSuffix="cc"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
          
          <StrategyCard
            title="Cash-Secured Put"
            subtitle="Sell 125P, Have cash to buy shares if assigned"
            returnOnRisk=""
            returnLabel="Return on collateral"
            chance="74%"
            profit="$3,315"
            risk="$12,500"
            riskLabel="Collateral"
            chartData={chartData.cashSecuredPut}
            idSuffix="csp"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
          
          <StrategyCard
            title="Short Put"
            subtitle="Sell 115P"
            returnOnRisk="209%"
            returnLabel="Return on Collateral"
            chance="74%"
            profit="$2,405"
            risk="$1,150"
            riskLabel="Collateral"
            chartData={chartData.shortPut}
            idSuffix="sp"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
          
          <StrategyCard
            title="Bull Call Spread"
            subtitle="Buy 95C, Sell 265C"
            returnOnRisk="236%"
            chance="52%"
            profit="$11,865.59"
            risk="$5,025"
            chartData={chartData.bullCallSpread}
            idSuffix="bcs"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
          
          <StrategyCard
            title="Bull Put Spread"
            subtitle="Buy 90P, Sell 185P"
            returnOnRisk="124%"
            chance="58%"
            profit="$5,805"
            risk="$4,695"
            chartData={chartData.bullPutSpread}
            idSuffix="bps"
            spotPrice={spotPrice}
            targetPrice={targetPrice}
          />
        </div>
      </div>
    </div>
  );
}