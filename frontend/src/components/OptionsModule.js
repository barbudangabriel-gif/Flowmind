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
              
              {/* Grid */}
              <CartesianGrid stroke="#4a5f7a" strokeDasharray="1 1" strokeOpacity={0.3} />
              
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
              
              {/* Faded white zero line - CRITICAL FEATURE */}
              <ReferenceLine 
                y={0} 
                stroke="#ffffff" 
                strokeDasharray="3 3" 
                strokeOpacity={0.4} 
                strokeWidth={1}
              />
              
              {/* Current price line */}
              <ReferenceLine 
                x={149.53} 
                stroke="#3498db" 
                strokeDasharray="2 2" 
                strokeOpacity={0.7} 
                strokeWidth={1}
              />
              
              {/* Gradient fill areas */}
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
              
              {/* P&L Lines matching gradient colors */}
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

// Sentiment Button Component  
function SentimentButton({ icon, label, active, onClick }) {
  const getColor = () => {
    if (label.includes('Bearish')) return active ? 'bg-red-500' : 'bg-gray-700 border-red-500';
    if (label.includes('Bullish')) return active ? 'bg-green-500' : 'bg-gray-700 border-green-500';
    if (label === 'Directional') return active ? 'bg-purple-500' : 'bg-gray-700 border-purple-500';
    return active ? 'bg-blue-500' : 'bg-gray-700 border-blue-500';
  };

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={onClick}
        className={`w-16 h-16 border-2 flex items-center justify-center text-2xl transition-all ${getColor()}`}
      >
        {icon}
      </button>
      <span className="text-white text-xs mt-2 text-center">{label}</span>
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
              <div className="w-8 h-8 bg-blue-500"></div>
              <span className="text-xl font-bold">OptionStrat</span>
            </div>
            <nav className="hidden md:flex space-x-6">
              <button className="text-gray-300 hover:text-white">Build ▼</button>
              <button className="text-gray-300 hover:text-white">Optimize</button>
              <button className="text-gray-300 hover:text-white">Flow ▼</button>
            </nav>
          </div>
          
          <div className="flex items-center space-x-6 text-sm">
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
            readOnly
            className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-white w-20 text-center"
          />
          <span className="text-2xl font-bold">${spotPrice.toFixed(2)}</span>
          <span className="text-green-400">+7.40%</span>
          <span className="text-green-400">+$10.30</span>
          <span className="text-gray-400 text-sm">🔄 Real-time</span>
        </div>

        {/* News Banner */}
        <div className="bg-[#3498db] p-4 mb-6 text-center">
          <span className="text-white">
            📊 Circle Internet Group shares are trading higher. The company announced a 
            public offering of 10 million shares at $130 per share. 
            <em className="text-blue-200 ml-2">updated 8/15/25, 8:06 PM</em>
          </span>
          <button className="ml-4 text-blue-200 hover:text-white">✕</button>
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
            <span className="text-gray-400">Target Price: $</span>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(parseFloat(e.target.value))}
              className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-white w-24"
            />
            <span className="text-gray-400">(+76%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Budget: $</span>
            <input
              placeholder="None"
              className="bg-[#34495e] border border-[#4a5f7a] px-2 py-1 text-gray-400 w-24"
            />
          </div>
        </div>

        {/* Month Tabs */}
        <div className="flex justify-center space-x-2 mb-8">
          {months.map((month, i) => (
            <button
              key={i}
              className={`px-3 py-1 text-sm border ${
                month === "Dec" ? "bg-[#3498db] text-white border-[#3498db]" : "bg-[#34495e] text-gray-300 border-[#4a5f7a]"
              }`}
            >
              {month}
            </button>
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
            className="w-full h-2 bg-[#34495e] appearance-none cursor-pointer"
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