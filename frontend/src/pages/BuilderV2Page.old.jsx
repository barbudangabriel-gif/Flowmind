// =============================================
// FlowMind — Builder V2 (Next.js Style)
// =============================================
import React, { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

// Diagonal Call Spread Component
function DiagonalCallSpread() {
  const [rangeValue, setRangeValue] = useState(12);
  const [activeTab, setActiveTab] = useState('table');

  // Strike prices from $249 down to $195
  const strikes = [
    249, 247, 244, 242, 239, 237, 234, 232, 229, 227, 224, 222, 220, 217, 215, 212, 210, 207, 205, 202, 200, 197, 195,
  ];

  // Dates for columns (Oct through Nov)
  const dates = [
    { month: 'Oct', day: '22', label: 'W' },
    { month: '', day: '24', label: 'F' },
    { month: '', day: '27', label: 'M' },
    { month: '', day: '29', label: 'W' },
    { month: '', day: '30', label: 'Th' },
    { month: '', day: '31', label: '' },
    { month: '', day: '3', label: 'M' },
    { month: '', day: '4', label: 'T' },
    { month: '', day: '6', label: 'Th' },
    { month: '', day: '7', label: 'F' },
    { month: '', day: '10', label: 'M' },
    { month: '', day: '11', label: 'T' },
    { month: 'Nov', day: '13', label: 'Th' },
    { month: '', day: '14', label: 'F' },
    { month: '', day: '17', label: 'M' },
    { month: '', day: '18', label: 'T' },
    { month: '', day: '20', label: 'Th' },
    { month: '', day: '21', label: 'F' },
    { month: '', day: '21', label: 'F' },
  ];

  // Sample data matrix (profit/loss values)
  const dataMatrix = [
    [27, 35, 46, 54, 59, 61, 72, 76, 82, 84, 90, 92, 92, 90, 80, 74, 59, 52, 50],
    [30, 38, 51, 60, 64, 68, 81, 85, 93, 96, 103, 108, 110, 110, 102, 96, 81, 73, 71],
    [33, 43, 57, 68, 73, 78, 94, 99, 109, 114, 128, 132, 139, 141, 139, 135, 119, 110, 108],
    [35, 45, 61, 72, 78, 83, 101, 107, 119, 125, 143, 148, 158, 162, 166, 164, 149, 139, 137],
    [35, 47, 64, 77, 83, 90, 111, 118, 133, 140, 163, 171, 186, 193, 209, 211, 201, 190, 187],
    [35, 47, 66, 79, 86, 93, 116, 124, 140, 148, 175, 185, 204, 213, 238, 243, 241, 230, 227],
    [33, 45, 65, 80, 87, 95, 120, 129, 148, 158, 190, 202, 226, 239, 280, 297, 306, 298, 295],
    [30, 43, 64, 79, 87, 95, 122, 131, 151, 162, 197, 210, 238, 254, 304, 322, 353, 350, 346],
    [24, 37, 59, 75, 83, 92, 120, 130, 152, 163, 202, 217, 250, 268, 333, 359, 419, 438, 435],
    [19, 32, 54, 70, 78, 87, 116, 126, 149, 161, 202, 217, 252, 271, 344, 374, 454, 501, 501],
    [8, 22, 44, 60, 68, 77, 106, 117, 140, 152, 194, 210, 246, 267, 345, 380, 479, 573, 612],
    [0, 13, 35, 51, 59, 68, 97, 108, 130, 142, 184, 200, 236, 256, 335, 370, 471, 572, 645],
    [-9, 4, 25, 41, 49, 57, 86, 96, 118, 130, 170, 185, 220, 240, 315, 348, 440, 518, 535],
    [-26, -13, 7, 22, 29, 37, 64, 73, 94, 105, 142, 156, 187, 205, 269, 295, 359, 386, 382],
    [-38, -26, -7, 7, 14, 22, 47, 56, 75, 85, 119, 131, 159, 175, 228, 249, 290, 294, 290],
    [-58, -47, -30, -17, -11, -4, 18, 25, 42, 50, 78, 88, 110, 121, 157, 168, 179, 169, 165],
    [-72, -62, -47, -35, -29, -23, -4, 3, 17, 25, 48, 56, 73, 82, 105, 110, 107, 94, 90],
    [-86, -87, -74, -64, -59, -54, -39, -33, -23, -17, -1, 5, 15, 19, 26, 24, 8, -5, -9],
    [-112, -104, -93, -84, -80, -76, -63, -59, -50, -46, -34, -31, -25, -24, -26, -31, -50, -63, -67],
    [-137, -131, -122, -116, -118, -110, -101, -98, -93, -91, -85, -85, -85, -86, -98, -106, -127, -139, -142],
    [-155, -150, -142, -137, -135, -132, -126, -124, -121, -120, -118, -119, -123, -126, -142, -150, -171, -181, -184],
    [-181, -177, -172, -169, -168, -166, -164, -163, -163, -163, -167, -169, -176, -180, -200, -208, -226, -236, -238],
    [-198, -195, -192, -190, -189, -189, -188, -188, -189, -191, -197, -200, -208, -213, -233, -241, -257, -265, -268],
  ];

  const getColorForValue = (value) => {
    if (value > 0) {
      const intensity = Math.min(value / 600, 1);
      const green = Math.floor(50 + intensity * 100);
      const opacity = 0.3 + intensity * 0.7;
      return `rgba(34, ${green}, 34, ${opacity})`;
    } else {
      const intensity = Math.min(Math.abs(value) / 300, 1);
      const red = Math.floor(100 + intensity * 100);
      const opacity = 0.3 + intensity * 0.7;
      return `rgba(${red}, 30, 30, ${opacity})`;
    }
  };

  return (
    <div className="w-full max-w-[1400px] mx-auto bg-[#0a0e27] text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-medium text-white">Diagonal Call Spread</h1>
          <button className="w-5 h-5 rounded-full border border-white/30 flex items-center justify-center text-xs">
            ?
          </button>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-cyan-500 text-white text-sm font-medium rounded">Add +</button>
          <button className="px-4 py-2 bg-cyan-500 text-white text-sm font-medium rounded">Positions (2) ☰</button>
          <button className="px-4 py-2 bg-cyan-500 text-white text-sm font-medium rounded">Save Trade ⎘</button>
          <button className="px-4 py-2 bg-cyan-500 text-white text-sm font-medium rounded">Historical Chart ↻</button>
        </div>
      </div>

      {/* Ticker Info */}
      <div className="p-4 flex items-center gap-4">
        <div className="px-3 py-1 bg-white/10 text-white text-sm font-medium">AMZN</div>
        <div className="text-2xl font-medium">$222.13</div>
        <div className="text-green-400 text-sm">+0.04%</div>
        <div className="text-green-400 text-sm">+$0.10</div>
        <div className="text-sm text-white/60 flex items-center gap-1">
          Real-time{' '}
          <button className="w-4 h-4 rounded-full border border-white/30 flex items-center justify-center text-xs">
            ?
          </button>
        </div>
      </div>

      {/* Expirations */}
      <div className="px-4 pb-2">
        <div className="text-sm text-white/80 mb-2">
          EXPIRATIONS: <span className="font-medium">30d, 58d</span>
        </div>
        <div className="flex gap-2 text-xs">
          <div className="flex flex-col items-center">
            <div className="text-white/60">Oct</div>
            <div className="text-white">24</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60"></div>
            <div className="text-white">31</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60">Nov</div>
            <div className="text-white">7</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60"></div>
            <div className="text-white">14</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60"></div>
            <div className="px-2 py-1 bg-cyan-500 text-white rounded">21</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60"></div>
            <div className="text-white">28</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-white/60">Dec</div>
            <div className="px-2 py-1 bg-fuchsia-500 text-white rounded">19</div>
          </div>
        </div>
      </div>

      {/* Strikes Chart */}
      <div className="px-4 py-4">
        <div className="text-sm text-white/80 mb-2">STRIKES:</div>
        <div className="relative h-32 bg-[#0d1230] rounded">
          {/* Strike scale */}
          <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-white/40 px-2">
            {[200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300].map((strike) => (
              <div key={strike}>{strike}</div>
            ))}
          </div>

          {/* Volume bars */}
          <div className="absolute bottom-6 left-[60%] flex gap-1">
            <div className="w-2 h-12 bg-green-500"></div>
            <div className="w-2 h-16 bg-green-500"></div>
            <div className="w-2 h-20 bg-green-500"></div>
            <div className="w-2 h-16 bg-green-500"></div>
            <div className="w-2 h-12 bg-green-500"></div>
            <div className="w-2 h-8 bg-green-500"></div>
          </div>

          {/* Price labels */}
          <div className="absolute top-4 left-[58%]">
            <div className="bg-fuchsia-600 text-white text-xs px-2 py-1 rounded">12/19</div>
            <div className="bg-green-500 text-white text-sm px-2 py-1 rounded mt-1">220C</div>
          </div>
          <div className="absolute bottom-8 left-[62%]">
            <div className="bg-cyan-500 text-white text-sm px-2 py-1 rounded">222.5C</div>
            <div className="bg-cyan-600 text-white text-xs px-2 py-1 rounded mt-1">11/21</div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="px-4 py-4 flex justify-between items-center text-sm border-y border-white/10">
        <div className="text-center">
          <div className="text-white/60">NET DEBIT:</div>
          <div className="text-lg font-medium">-$400</div>
        </div>
        <div className="text-center">
          <div className="text-white/60">MAX LOSS:</div>
          <div className="text-lg font-medium">$400</div>
        </div>
        <div className="text-center">
          <div className="text-white/60">MAX PROFIT:</div>
          <div className="text-lg font-medium text-green-400">$673.76</div>
        </div>
        <div className="text-center">
          <div className="text-white/60">CHANCE OF PROFIT:</div>
          <div className="text-lg font-medium">59%</div>
        </div>
        <div className="text-center">
          <div className="text-white/60">BREAKEVENS:</div>
          <div className="text-sm">
            → Between <span className="font-medium">$207.30 - $255.38</span>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="p-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-left text-white/60 pb-2"></th>
              {dates.map((date, i) => (
                <th key={i} className="text-center text-white/60 pb-2 px-1">
                  {date.month && <div className="text-white/80">{date.month}</div>}
                  <div className="flex items-center justify-center gap-1">
                    <span>{date.day}</span>
                    {date.label && <span className="text-[10px] text-white/40">{date.label}</span>}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {strikes.map((strike, rowIndex) => (
              <tr key={strike}>
                <td className="text-left py-1 pr-2 text-white/80">${strike}</td>
                {dataMatrix[rowIndex].map((value, colIndex) => (
                  <td
                    key={colIndex}
                    className="text-center py-1 px-1"
                    style={{ backgroundColor: getColorForValue(value) }}
                  >
                    {value > 0 ? value : value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Range Control */}
      <div className="px-4 py-3 border-t border-white/10">
        <div className="flex items-center gap-4">
          <div className="text-sm">RANGE: ±{rangeValue}%</div>
          <input
            type="range"
            min="0"
            max="50"
            value={rangeValue}
            onChange={(e) => setRangeValue(Number(e.target.value))}
            className="flex-1 h-2 bg-white/10 rounded-lg"
          />
          <button className="w-6 h-6 rounded-full border border-white/30 flex items-center justify-center">↻</button>
          <div className="text-sm">AVERAGE ▼</div>
          <div className="text-sm">
            IMPLIED VOLATILITY: <span className="font-medium">39.4%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            defaultValue="39"
            className="w-32 h-2 bg-white/10 rounded-lg"
          />
          <div className="text-xs text-white/40">×2</div>
          <div className="text-xs text-white/40">×3</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-t border-white/10">
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'table' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('table')}
        >
          ▦ Table
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'graph' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('graph')}
        >
          📊 Graph
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'profit-loss-dollar' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('profit-loss-dollar')}
        >
          Profit / Loss $
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'profit-loss-percent' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('profit-loss-percent')}
        >
          Profit / Loss %
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'contract-value' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('contract-value')}
        >
          Contract Value
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'max-risk' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('max-risk')}
        >
          % of Max Risk
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${
            activeTab === 'more' ? 'bg-cyan-500 text-white' : 'bg-white/5 text-white/60'
          }`}
          onClick={() => setActiveTab('more')}
        >
          ▼ More
        </button>
      </div>
    </div>
  );
}

// Options Flow Dashboard Component
function OptionsFlowDashboard() {
  const flowData = [
    { ticker: '/GF', count: 42, amount: '$8.67m', opposingTicker: 'MSTX', opposingCount: 25, opposingAmount: '$9.87m' },
    { ticker: 'PNR', count: 19, amount: '$727k', opposingTicker: 'PLTR', opposingCount: 118, opposingAmount: '$72.16m' },
    { ticker: 'SMH', count: 20, amount: '$8.05m', opposingTicker: 'GDX', opposingCount: 27, opposingAmount: '$16.00m' },
    { ticker: 'FHN', count: 23, amount: '$2.38m', opposingTicker: 'SE', opposingCount: 29, opposingAmount: '$3.40m' },
    { ticker: 'CVNA', count: 29, amount: '$39.80m', opposingTicker: 'SPX', opposingCount: 164, opposingAmount: '$1111.02m' },
    { ticker: 'VRT', count: 19, amount: '$36.90m', opposingTicker: 'GLXY', opposingCount: 20, opposingAmount: '$4.53m' },
    { ticker: 'TSM', count: 20, amount: '$10.55m', opposingTicker: 'QUBT', opposingCount: 17, opposingAmount: '$3.34m' },
    { ticker: 'MSFT', count: 33, amount: '$31.91m', opposingTicker: '/ZN', opposingCount: 26, opposingAmount: '$6.33m' },
    { ticker: 'BULL', count: 23, amount: '$2.14m', opposingTicker: 'LAZR', opposingCount: 29, opposingAmount: '$1.50m' },
    { ticker: 'DIS', count: 17, amount: '$1.69m', opposingTicker: 'RGTI', opposingCount: 32, opposingAmount: '$11.65m' },
    { ticker: 'PTON', count: 21, amount: '$694k', opposingTicker: 'HOOD', opposingCount: 27, opposingAmount: '$10.64m' },
    { ticker: 'CMG', count: 16, amount: '$820k', opposingTicker: 'CRML', opposingCount: 11, opposingAmount: '$1.11m' },
    { ticker: 'T', count: 39, amount: '$1.63m', opposingTicker: 'BBAI', opposingCount: 31, opposingAmount: '$839k' },
    { ticker: 'JD', count: 16, amount: '$3.60m', opposingTicker: 'GDXJ', opposingCount: 7, opposingAmount: '$4.30m' },
    { ticker: 'SOUN', count: 16, amount: '$1.50m', opposingTicker: 'SOFI', opposingCount: 29, opposingAmount: '$3.85m' },
    { ticker: 'CRCL', count: 38, amount: '$8.01m', opposingTicker: 'ACHR', opposingCount: 15, opposingAmount: '$743k' },
    { ticker: 'NKE', count: 13, amount: '$1.71m', opposingTicker: 'CORZ', opposingCount: 15, opposingAmount: '$4.99m' },
    { ticker: 'MU', count: 23, amount: '$10.61m', opposingTicker: 'IONQ', opposingCount: 11, opposingAmount: '$6.23m' },
  ];

  return (
    <div className="mx-auto max-w-[1400px] px-6">
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-600 shadow-lg">
            <TrendingUp className="h-6 w-6 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-2xl font-medium text-white">Bullish Flow</h1>
        </div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-medium text-white">Bearish Flow</h1>
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-600 shadow-lg">
            <TrendingDown className="h-6 w-6 text-white" strokeWidth={2.5} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        {/* Bullish Column */}
        <div className="space-y-1.5">
          {flowData.map((flow, index) => (
            <div
              key={`bullish-${index}`}
              className="relative flex items-center justify-between px-4 py-3 bg-gradient-to-r from-green-900/40 via-green-900/20 to-transparent"
              style={{ boxShadow: '0 0 20px rgba(34, 197, 94, 0.15)' }}
            >
              <div className="flex items-center gap-3">
                <span className="min-w-[60px] text-sm font-medium text-white">{flow.ticker}</span>
                <span className="text-sm font-normal text-white/80">{flow.count}</span>
              </div>
              <span className="text-base font-medium text-green-400">{flow.amount}</span>
            </div>
          ))}
        </div>

        {/* Bearish Column */}
        <div className="space-y-1.5">
          {flowData.map((flow, index) => (
            <div
              key={`bearish-${index}`}
              className="relative flex items-center justify-between px-4 py-3 bg-gradient-to-l from-red-900/40 via-red-900/20 to-transparent"
              style={{ boxShadow: '0 0 20px rgba(239, 68, 68, 0.15)' }}
            >
              <span className="text-base font-medium text-red-400">{flow.opposingAmount}</span>
              <div className="flex items-center gap-3">
                <span className="text-sm font-normal text-white/80">{flow.opposingCount}</span>
                <span className="min-w-[60px] text-right text-sm font-medium text-white">{flow.opposingTicker}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Main Builder V2 Page
export default function BuilderV2Page() {
  const [activeView, setActiveView] = useState('spread');

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a] p-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-white mb-2">
            Options <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">Builder V2</span>
          </h1>
          <p className="text-slate-300">Advanced options strategy builder with real-time analysis</p>
        </div>

        {/* View Toggle */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setActiveView('spread')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeView === 'spread'
                ? 'bg-cyan-500 text-white shadow-lg'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Diagonal Call Spread
          </button>
          <button
            onClick={() => setActiveView('flow')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeView === 'flow'
                ? 'bg-cyan-500 text-white shadow-lg'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Options Flow
          </button>
        </div>

        {/* Content */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl backdrop-blur-sm overflow-hidden">
          {activeView === 'spread' && <DiagonalCallSpread />}
          {activeView === 'flow' && <OptionsFlowDashboard />}
        </div>
      </div>
    </div>
  );
}
