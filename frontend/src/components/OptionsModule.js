import React, { useState } from 'react';
import { ComposedChart, Line, Area, XAxis, YAxis, ResponsiveContainer, ReferenceLine, CartesianGrid } from 'recharts';

// Generate P&L data for each strategy
function generatePnLData(strategy) {
  const prices = [];
  for (let i = 50; i <= 350; i += 10) {
    prices.push(i);
  }
  
  let data = [];
  
  switch(strategy) {
    case 'longCall':
      data = prices.map(price => {
        const pnl = Math.max(0, price - 95) * 100 - 6455;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
    case 'coveredCall':
      data = prices.map(price => {
        const pnl = (price - 149.53) * 100 + Math.min(0, 210 - price) * 100 + 1285;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
    case 'cashSecuredPut':
      data = prices.map(price => {
        const pnl = -Math.max(0, 125 - price) * 100 + 2615;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
    case 'shortPut':
      data = prices.map(price => {
        const pnl = -Math.max(0, 115 - price) * 100 + 2405;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
    case 'bullCallSpread':
      data = prices.map(price => {
        const pnl = Math.min(Math.max(0, price - 95), 170) * 100 - 5025;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
    case 'bullPutSpread':
      data = prices.map(price => {
        const pnl = 1810 - Math.min(Math.max(0, 185 - price), 95) * 100;
        return { price, pnl, profit: pnl > 0 ? pnl : 0, loss: pnl < 0 ? pnl : 0 };
      });
      break;
  }
  
  return data;
}

// Strategy Card Component - Pixel-Perfect OptionStrat.com Replica
function StrategyCard({ title, subtitle, returnOnRisk, chance, profit, risk, riskLabel, strategyType }) {
  const data = generatePnLData(strategyType);
  
  return (
    <div className="bg-[#2c3e50] border border-[#34495e] rounded-none" style={{minHeight: '420px'}}>
      {/* Header Section */}
      <div className="px-4 pt-4 pb-3 border-b border-[#34495e]">
        <h3 className="text-white text-base font-bold leading-tight mb-1">{title}</h3>
        <p className="text-[#7f8c8d] text-xs leading-tight">{subtitle}</p>
      </div>
      
      {/* Metrics Section */}
      <div className="px-4 py-3">
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="text-left">
            <div className="text-[#f39c12] text-xl font-bold leading-none">{returnOnRisk}</div>
            <div className="text-[#7f8c8d] text-xs mt-1">Return on Risk</div>
          </div>
          <div className="text-left">
            <div className="text-[#27ae60] text-xl font-bold leading-none">{chance}</div>
            <div className="text-[#7f8c8d] text-xs mt-1">Chance</div>
          </div>
        </div>
        
        {/* Profit/Risk Row */}
        <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
          <div className="text-left">
            <span className="text-[#27ae60] font-semibold">{profit}</span>
            <span className="text-[#7f8c8d]"> Profit</span>
          </div>
          <div className="text-left">
            <span className="text-[#e74c3c] font-semibold">{risk}</span>
            <span className="text-[#7f8c8d]"> {riskLabel}</span>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="px-3 pb-3">
        <div className="h-36 bg-[#34495e] rounded-none border border-[#4a5f7a]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <defs>
                <linearGradient id={`profit-gradient-${strategyType}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#27ae60" stopOpacity={0.6} />
                  <stop offset="100%" stopColor="#27ae60" stopOpacity={0.2} />
                </linearGradient>
                <linearGradient id={`loss-gradient-${strategyType}`} x1="0" y1="1" x2="0" y2="0">
                  <stop offset="0%" stopColor="#e74c3c" stopOpacity={0.6} />
                  <stop offset="100%" stopColor="#e74c3c" stopOpacity={0.2} />
                </linearGradient>
              </defs>
              
              {/* Grid - Exact OptionStrat Style */}
              <CartesianGrid 
                stroke="#4a5f7a" 
                strokeDasharray="1 1" 
                strokeOpacity={0.6}
                horizontal={true}
                vertical={true}
              />
              
              {/* Axes */}
              <XAxis 
                dataKey="price" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: "#7f8c8d", fontSize: 9 }}
                tickCount={6}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: "#7f8c8d", fontSize: 9 }}
                tickCount={5}
              />
              
              {/* Gradient fill areas - PRIMUL LAYER */}
              <Area 
                dataKey="profit" 
                fill={`url(#profit-gradient-${strategyType})`} 
                stroke="none" 
                fillOpacity={1}
              />
              <Area 
                dataKey="loss" 
                fill={`url(#loss-gradient-${strategyType})`} 
                stroke="none" 
                fillOpacity={1}
              />
              
              {/* P&L Lines in gradient colors - AL DOILEA LAYER */}
              <Line 
                dataKey="profit" 
                stroke="#27ae60" 
                strokeWidth={1.5} 
                dot={false} 
                connectNulls={false} 
              />
              <Line 
                dataKey="loss" 
                stroke="#e74c3c" 
                strokeWidth={1.5} 
                dot={false} 
                connectNulls={false} 
              />
              
              {/* WHITE ZERO LINE - ULTIMUL LAYER (DEASUPRA TUTUROR) */}
              <ReferenceLine 
                y={0} 
                stroke="#ffffff" 
                strokeOpacity={0.8} 
                strokeWidth={2}
              />
              
              {/* VERTICAL LINES - ULTIMUL LAYER */}
              <ReferenceLine 
                x={150} 
                stroke="#3498db" 
                strokeDasharray="2 2" 
                strokeOpacity={0.9} 
                strokeWidth={1}
              />
              
              <ReferenceLine 
                x={strategyType === 'longCall' ? 95 : 
                   strategyType === 'coveredCall' ? 210 :
                   strategyType === 'cashSecuredPut' ? 125 :
                   strategyType === 'shortPut' ? 115 :
                   strategyType === 'bullCallSpread' ? 180 :
                   strategyType === 'bullPutSpread' ? 185 : 200} 
                stroke="#f39c12" 
                strokeDasharray="2 2" 
                strokeOpacity={0.9} 
                strokeWidth={1}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Button Section */}
      <div className="px-4 pb-4">
        <button className="w-full bg-[#3498db] hover:bg-[#2980b9] text-white py-2.5 px-4 text-sm font-semibold transition-colors rounded-none border-0">
          Open in Builder
        </button>
      </div>
    </div>
  );
}

// Sentiment Button Component - Sharp Corners OptionStrat Style
function SentimentButton({ icon, label, active, onClick }) {
  const getColor = () => {
    if (label.includes('Bearish')) return active ? 'bg-[#e74c3c] border-[#e74c3c]' : 'bg-[#2c3e50] border-[#e74c3c]';
    if (label.includes('Bullish')) return active ? 'bg-[#27ae60] border-[#27ae60]' : 'bg-[#2c3e50] border-[#27ae60]';
    if (label === 'Directional') return active ? 'bg-[#9b59b6] border-[#9b59b6]' : 'bg-[#2c3e50] border-[#9b59b6]';
    return active ? 'bg-[#3498db] border-[#3498db]' : 'bg-[#2c3e50] border-[#3498db]';
  };

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={onClick}
        className={`w-16 h-16 border-2 flex items-center justify-center text-2xl transition-all rounded-none ${getColor()}`}
      >
        {icon}
      </button>
      <span className="text-white text-xs mt-2 text-center leading-tight">{label}</span>
    </div>
  );
}

export default function OptionsModule() {
  const [symbol] = useState("CRCL");
  const [spotPrice] = useState(149.53);
  const [targetPrice, setTargetPrice] = useState(263.91);
  const [sentiment, setSentiment] = useState("Bullish");

  const sentiments = [
    { icon: "📉", label: "Very Bearish" },
    { icon: "📈", label: "Bearish" },
    { icon: "➡️", label: "Neutral" },
    { icon: "⚡", label: "Directional" },
    { icon: "📈", label: "Bullish" },
    { icon: "📊", label: "Very Bullish" }
  ];

  const months = ["Sep", "Oct", "Nov", "Dec", "Jan '26", "Feb", "Mar", "Apr", "Jun", "Dec", "Jan '27"];

  return (
    <div className="min-h-screen bg-[#1a252f] text-white">
      {/* Header */}
      <div className="bg-[#2c3e50] px-6 py-4 border-b border-[#34495e]">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-[#3498db] rounded-none"></div>
              <span className="text-xl font-bold">OptionStrat</span>
            </div>
            <nav className="hidden md:flex space-x-6">
              <button className="text-[#bdc3c7] hover:text-white transition-colors">Build ▼</button>
              <button className="text-[#bdc3c7] hover:text-white transition-colors">Optimize</button>
              <button className="text-[#bdc3c7] hover:text-white transition-colors">Flow ▼</button>
            </nav>
          </div>
          
          <div className="flex items-center space-x-6 text-sm">
            <span className="text-[#bdc3c7] hover:text-white transition-colors cursor-pointer">Tutorials</span>
            <span className="text-[#bdc3c7] hover:text-white transition-colors cursor-pointer">Blog</span>
            <button className="text-[#bdc3c7] hover:text-white transition-colors">My Account ▼</button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        
        {/* Symbol and Price */}
        <div className="flex items-center justify-center space-x-4 mb-6">
          <span className="text-[#7f8c8d]">Symbol:</span>
          <input 
            value={symbol}
            readOnly
            className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-white w-20 text-center rounded-none focus:outline-none focus:border-[#3498db]"
          />
          <span className="text-2xl font-bold">${spotPrice.toFixed(2)}</span>
          <span className="text-[#27ae60]">+7.40%</span>
          <span className="text-[#27ae60]">+$10.30</span>
          <span className="text-[#7f8c8d] text-sm">🔄 Real-time</span>
        </div>

        {/* News Banner */}
        <div className="bg-[#3498db] p-4 mb-6 text-center rounded-none">
          <span className="text-white">
            📊 Circle Internet Group shares are trading higher. The company announced a 
            public offering of 10 million shares at $130 per share. 
            <em className="text-[#ecf0f1] ml-2">updated 8/15/25, 8:06 PM</em>
          </span>
          <button className="ml-4 text-[#ecf0f1] hover:text-white transition-colors">✕</button>
        </div>

        {/* Sentiment Buttons */}
        <div className="flex justify-center space-x-8 mb-8">
          {sentiments.map((s) => (
            <SentimentButton
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
            <span className="text-[#7f8c8d]">Target Price: $</span>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(parseFloat(e.target.value))}
              className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-white w-24 rounded-none focus:outline-none focus:border-[#3498db]"
            />
            <span className="text-[#7f8c8d]">(+76%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-[#7f8c8d]">Budget: $</span>
            <input
              placeholder="None"
              className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-[#7f8c8d] w-24 rounded-none focus:outline-none focus:border-[#3498db]"
            />
          </div>
        </div>

        {/* Month Tabs - Sharp Corners */}
        <div className="flex justify-center space-x-2 mb-8">
          {months.map((month, i) => (
            <button
              key={i}
              className={`px-3 py-1 text-sm border rounded-none transition-colors ${
                month === "Dec" 
                  ? "bg-[#3498db] text-white border-[#3498db]" 
                  : "bg-[#34495e] text-[#bdc3c7] border-[#4a5f7a] hover:border-[#3498db]"
              }`}
            >
              {month}
            </button>
          ))}
        </div>

        {/* Max Return/Max Chance Slider */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-[#7f8c8d] mb-2">
            <span>← Max Return</span>
            <span>Max Chance →</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="100" 
            defaultValue="50"
            className="w-full h-2 bg-[#34495e] appearance-none cursor-pointer rounded-none"
            style={{
              background: 'linear-gradient(to right, #3498db 0%, #3498db 50%, #34495e 50%, #34495e 100%)'
            }}
          />
        </div>

        {/* Strategy Cards Grid - 3x2 Layout */}
        <div className="grid grid-cols-3 gap-4 max-w-6xl mx-auto">
          <StrategyCard
            title="Long Call"
            subtitle="Buy 95C"
            returnOnRisk="162%"
            chance="47%"
            profit="$10,435.59"
            risk="$6,455"
            riskLabel="Risk"
            strategyType="longCall"
          />
          
          <StrategyCard
            title="Covered Call"
            subtitle="Own the underlying, Sell 210C"
            returnOnRisk="63%"
            chance="58%"
            profit="$8,147"
            risk="$12,853"
            riskLabel="Risk"
            strategyType="coveredCall"
          />
          
          <StrategyCard
            title="Cash-Secured Put"
            subtitle="Sell 125P, Have cash to buy shares if assigned"
            returnOnRisk=""
            chance="74%"
            profit="$3,315"
            risk="$12,500"
            riskLabel="Collateral"
            strategyType="cashSecuredPut"
          />
          
          <StrategyCard
            title="Short Put"
            subtitle="Sell 115P"
            returnOnRisk="209%"
            chance="74%"
            profit="$2,405"
            risk="$1,150"
            riskLabel="Collateral"
            strategyType="shortPut"
          />
          
          <StrategyCard
            title="Bull Call Spread"
            subtitle="Buy 95C, Sell 265C"
            returnOnRisk="236%"
            chance="52%"
            profit="$11,865.59"
            risk="$5,025"
            riskLabel="Risk"
            strategyType="bullCallSpread"
          />
          
          <StrategyCard
            title="Bull Put Spread"
            subtitle="Buy 90P, Sell 185P"
            returnOnRisk="124%"
            chance="58%"
            profit="$5,805"
            risk="$4,695"
            riskLabel="Risk"
            strategyType="bullPutSpread"
          />
        </div>
      </div>
    </div>
  );
}