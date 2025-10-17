import React from 'react';

const PerfectOptionCard = ({ 
 strategyName = "Long Call",
 strikes = "18C",
 returnOnRisk = "113%",
 chance = "43%",
 profit = "$1,016.22",
 risk = "$900",
 currentPrice = 27.30,
 breakeven = 27.30
}) => {
 
 return (
 <div className="bg-gray-800 rounded-lg border border-gray-600 hover:border-blue-500 transition-colors duration-200 overflow-hidden" style={{width: '280px', height: '320px'}}>
 
 {/* Header Section - EXACT OptionStrat Style */}
 <div className="px-4 py-3 border-b border-gray-700">
 <div className="flex items-center justify-between mb-2">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)]">{strategyName}</h3>
 <div className="text-right">
 <div className="text-3xl font-medium text-green-400">{returnOnRisk}</div>
 <div className="text-lg text-gray-400">Return on Risk</div>
 </div>
 </div>
 
 <div className="flex items-center justify-between">
 <div className="text-xl text-gray-400">{strikes}</div>
 <div className="text-right">
 <div className="text-3xl font-medium text-blue-400">{chance}</div>
 <div className="text-lg text-gray-400">Chance</div>
 </div>
 </div>
 </div>

 {/* Chart Section - EXACT OptionStrat Chart */}
 <div className="px-4 py-3">
 <div className="bg-gray-900 rounded border border-gray-700 relative" style={{height: '140px'}}>
 
 {/* Grid Lines - Subtle */}
 <div className="absolute inset-0 opacity-20">
 {/* Horizontal grid lines */}
 <div className="absolute w-full border-t border-gray-600" style={{top: '25%'}}></div>
 <div className="absolute w-full border-t border-gray-600" style={{top: '50%'}}></div>
 <div className="absolute w-full border-t border-gray-600" style={{top: '75%'}}></div>
 
 {/* Vertical grid lines */}
 <div className="absolute h-full border-l border-gray-600" style={{left: '20%'}}></div>
 <div className="absolute h-full border-l border-gray-600" style={{left: '40%'}}></div>
 <div className="absolute h-full border-l border-gray-600" style={{left: '60%'}}></div>
 <div className="absolute h-full border-l border-gray-600" style={{left: '80%'}}></div>
 </div>
 
 {/* P&L Curve - EXACT Long Call Shape */}
 <svg className="absolute inset-0 w-full h-full" viewBox="0 0 260 140">
 {/* Long Call P&L Curve - EXACTLY like OptionStrat */}
 <path
 d="M 20 120 L 40 120 L 60 118 L 80 115 L 100 110 L 120 100 L 140 85 L 160 65 L 180 40 L 200 20 L 240 5"
 stroke="#22c55e"
 strokeWidth="2.5"
 fill="none"
 strokeLinecap="round"
 strokeLinejoin="round"
 />
 
 {/* Zero line (breakeven reference) */}
 <line 
 x1="0" 
 y1="90" 
 x2="260" 
 y2="90" 
 stroke="#6b7280" 
 strokeWidth="1" 
 strokeDasharray="4,4" 
 opacity="0.6" 
 />
 
 {/* Current price vertical line */}
 <line 
 x1="130" 
 y1="0" 
 x2="130" 
 y2="140" 
 stroke="#f97316" 
 strokeWidth="1.5" 
 strokeDasharray="3,3" 
 opacity="0.8" 
 />
 
 {/* Breakeven vertical line */}
 <line 
 x1="120" 
 y1="0" 
 x2="120" 
 y2="140" 
 stroke="#eab308" 
 strokeWidth="1.5" 
 strokeDasharray="3,3" 
 opacity="0.8" 
 />
 </svg>
 
 {/* Price Labels - EXACT OptionStrat Positioning */}
 <div className="absolute bottom-1 left-2 text-lg text-gray-500 font-mono">15</div>
 <div className="absolute bottom-1 right-2 text-lg text-gray-500 font-mono">35</div>
 <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-lg text-orange-400 font-medium bg-gray-900 px-1">
 {currentPrice}
 </div>
 
 {/* P&L Labels */}
 <div className="absolute top-2 left-2 text-lg text-green-400 font-medium bg-gray-900 px-1">
 {profit}
 </div>
 <div className="absolute top-2 right-2 text-lg text-red-400 font-medium bg-gray-900 px-1">
 -{risk}
 </div>
 </div>
 </div>

 {/* Stats Section - EXACT OptionStrat Format */}
 <div className="px-4 py-2 space-y-2">
 <div className="flex justify-between items-center text-xl">
 <span className="text-gray-400">Max Profit</span>
 <span className="text-green-400 font-medium">{profit}</span>
 </div>
 
 <div className="flex justify-between items-center text-xl">
 <span className="text-gray-400">Max Risk</span>
 <span className="text-red-400 font-medium">{risk}</span>
 </div>
 
 <div className="flex justify-between items-center text-xl">
 <span className="text-gray-400">Breakeven</span>
 <span className="text-yellow-400 font-medium">${breakeven}</span>
 </div>
 </div>

 {/* Button Section */}
 <div className="px-4 pb-3">
 <button className="w-full bg-blue-600 hover:bg-blue-700 text-[rgb(252, 251, 255)] py-2 px-4 rounded font-medium text-xl transition-colors">
 Open in Builder
 </button>
 </div>
 </div>
 );
};

export default PerfectOptionCard;