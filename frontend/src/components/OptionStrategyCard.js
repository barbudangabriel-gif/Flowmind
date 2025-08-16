import React from 'react';
import InteractiveOptionsChart from './InteractiveOptionsChart';

const OptionStrategyCard = ({ 
  strategy = {
    name: "Long Call",
    strikes: "18C",
    returnOnRisk: "113%",
    chance: "43%",
    profit: "$1016.22",
    risk: "$900",
    category: "Novice",
    breakeven: "$27.30",
    probProfit: "43%",
    expiration: "Dec 20",
    chartData: {
      x: [10, 15, 20, 25, 30, 35, 40],
      y: [-900, -900, -500, 0, 500, 1000, 1500]
    }
  },
  onOpenInBuilder = () => {},
  compact = false
}) => {
  
  const getCategoryColor = (category) => {
    switch(category) {
      case 'Novice': return 'bg-green-900/50 text-green-300 border-green-700';
      case 'Intermediate': return 'bg-blue-900/50 text-blue-300 border-blue-700';
      case 'Advanced': return 'bg-purple-900/50 text-purple-300 border-purple-700';
      case 'Expert': return 'bg-red-900/50 text-red-300 border-red-700';
      default: return 'bg-gray-900/50 text-gray-300 border-gray-700';
    }
  };

  const getChanceColor = (chance) => {
    const numChance = parseInt(chance);
    if (numChance >= 70) return 'text-green-400';
    if (numChance >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getReturnColor = (returnOnRisk) => {
    const numReturn = parseInt(returnOnRisk);
    if (numReturn >= 100) return 'text-green-400';
    if (numReturn >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-all duration-200 shadow-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div>
              <h4 className="text-lg font-bold text-white">{strategy.name}</h4>
              <div className="text-sm text-gray-400">{strategy.strikes}</div>
            </div>
            <div className={`px-2 py-1 rounded text-xs font-medium border ${getCategoryColor(strategy.category)}`}>
              {strategy.category}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className={`text-xl font-bold ${getReturnColor(strategy.returnOnRisk)}`}>
                {strategy.returnOnRisk}
              </div>
              <div className="text-xs text-gray-400">Return on Risk</div>
            </div>
            <div className="text-center">
              <div className={`text-xl font-bold ${getChanceColor(strategy.chance)}`}>
                {strategy.chance}
              </div>
              <div className="text-xs text-gray-400">Chance</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-sm">
          <div>
            <div className="text-gray-400">Max Profit</div>
            <div className="text-green-400 font-semibold">{strategy.profit}</div>
          </div>
          <div>
            <div className="text-gray-400">Max Risk</div>
            <div className="text-red-400 font-semibold">{strategy.risk}</div>
          </div>
          <div>
            <div className="text-gray-400">Breakeven</div>
            <div className="text-yellow-400 font-semibold">{strategy.breakeven}</div>
          </div>
        </div>

        <button 
          onClick={onOpenInBuilder}
          className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded font-semibold transition-colors text-sm"
        >
          Open in Builder
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-all duration-200 shadow-lg overflow-hidden">
      
      {/* Header Section - Exact OptionStrat Style */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <h4 className="text-xl font-bold text-white">{strategy.name}</h4>
              <div className="text-sm text-gray-400">
                Buy {strategy.strikes}
              </div>
            </div>
            <div className={`px-3 py-1 rounded text-xs font-medium border ${getCategoryColor(strategy.category)}`}>
              {strategy.category}
            </div>
          </div>
          
          {/* Key Metrics Header - OptionStrat Style */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className={`text-2xl font-bold ${getReturnColor(strategy.returnOnRisk)}`}>
                {strategy.returnOnRisk}
              </div>
              <div className="text-xs text-gray-400">Return on Risk</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${getChanceColor(strategy.chance)}`}>
                {strategy.chance}
              </div>
              <div className="text-xs text-gray-400">Chance</div>
            </div>
            <button 
              onClick={onOpenInBuilder}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-semibold transition-colors"
            >
              Open in Builder
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - Chart & Details */}
      <div className="grid grid-cols-12 gap-6 p-6">
        
        {/* Left: Interactive P&L Chart - 8 columns */}
        <div className="col-span-8">
          <div className="h-64">
            <InteractiveOptionsChart
              chartData={strategy.chartData}
              strategyName={strategy.name}
              stockPrice={25} // Example current price
              height={250}
            />
          </div>
        </div>

        {/* Right: Strategy Details - 4 columns */}
        <div className="col-span-4 space-y-4">
          
          {/* Risk & Reward Metrics */}
          <div className="space-y-3">
            <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-300">Max Profit</span>
                <span className="font-bold text-green-400 text-base">{strategy.profit}</span>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-300">Max Risk</span>
                <span className="font-bold text-red-400 text-base">{strategy.risk}</span>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-300">Return on Risk</span>
                <span className={`font-bold text-base ${getReturnColor(strategy.returnOnRisk)}`}>
                  {strategy.returnOnRisk}
                </span>
              </div>
            </div>
          </div>

          {/* Strategy Legs */}
          <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
            <h6 className="text-sm font-semibold text-white mb-3">Strategy Legs</h6>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between py-1">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 bg-green-500 rounded-full"></div>
                  <span className="text-gray-300">Buy Call</span>
                </div>
                <span className="text-white font-mono text-xs">{strategy.strikes}</span>
              </div>
            </div>
          </div>

          {/* Key Statistics */}
          <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
            <h6 className="text-sm font-semibold text-white mb-3">Key Statistics</h6>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Breakeven</span>
                <span className="text-yellow-400 font-semibold">{strategy.breakeven}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Expiration</span>
                <span className="text-white font-semibold">{strategy.expiration}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Prob. of Profit</span>
                <span className={`font-semibold ${getChanceColor(strategy.probProfit)}`}>
                  {strategy.probProfit}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptionStrategyCard;