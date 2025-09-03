import React from 'react';
import { useNavigate } from 'react-router-dom';

const StrategyOptimizeCard = ({ 
  strategy = {
    name: "Long Call",
    action: "Buy 637C", 
    returnOnRisk: "106%",
    profit: "$1,985.32",
    risk: "$1,578.20", 
    chance: "20%",
    currentPrice: "$652.78",
    maxLoss: "-$1,578",
    breakeven: "$614.22 (-4.8%)"
  }
}) => {
  const navigate = useNavigate();

  const handleOpenBuilder = () => {
    const strategySlug = strategy.name.toLowerCase().replace(/\s+/g, '_');
    navigate(`/build/${strategySlug}`);
  };

  return (
    <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:shadow-2xl overflow-hidden">
      
      {/* Header Info */}
      <div className="mb-4">
        <div className="text-sm text-slate-400 font-medium mb-1">
          {strategy.action}
        </div>
        <div className="text-xl font-semibold text-white">
          {strategy.name}
        </div>
      </div>

      {/* Metrics Row 1 */}
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-4">
          <div>
            <div className="text-lg font-bold text-amber-400">
              {strategy.returnOnRisk}
            </div>
            <div className="text-sm text-white">
              Return on risk
            </div>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm font-medium text-white">
            {strategy.profit} Profit
          </div>
        </div>
      </div>

      {/* Metrics Row 2 */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm font-medium text-white">
          {strategy.risk} Risk
        </div>
        
        <div className="flex items-center gap-2">
          <div>
            <div className="text-sm font-bold text-yellow-400">
              {strategy.chance}
            </div>
            <div className="text-xs text-white">
              Chance
            </div>
          </div>
          <div className="w-3 h-3">
            <svg viewBox="0 0 10 12" fill="none" className="w-full h-full">
              <path 
                fillRule="evenodd" 
                clipRule="evenodd" 
                d="M1.42857 5.25V3.75C1.42857 1.67893 3.02756 0 5 0C6.97244 0 8.57143 1.67893 8.57143 3.75V5.25C9.36043 5.25 10 5.92157 10 6.75V10.5C10 11.3284 9.36043 12 8.57143 12H1.42857C0.639593 12 0 11.3284 0 10.5V6.75C0 5.92157 0.639594 5.25 1.42857 5.25ZM7.14286 3.75V5.25H2.85714V3.75C2.85714 2.50736 3.81654 1.5 5 1.5C6.18346 1.5 7.14286 2.50736 7.14286 3.75Z" 
                fill="white"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Mini P&L Chart */}
      <div className="relative h-20 mb-4 bg-slate-900/50 rounded-lg overflow-hidden">
        <div className="absolute inset-0 flex items-end justify-center">
          {/* Chart bars simulation */}
          <div className="flex items-end h-full w-full px-2 gap-1">
            {[2, 4, 8, 12, 16, 20, 18, 14, 10, 6, 3].map((height, i) => (
              <div 
                key={i}
                className={`flex-1 rounded-t ${
                  i < 5 ? 'bg-red-500/60' : i === 5 ? 'bg-blue-500' : 'bg-green-500/60'
                } transition-all duration-300`}
                style={{ height: `${height * 4}%` }}
              />
            ))}
          </div>
          
          {/* Current price indicator */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
              {strategy.currentPrice}
            </div>
          </div>
        </div>

        {/* Chart labels */}
        <div className="absolute bottom-1 left-2 text-xs text-white">
          {strategy.maxLoss}
        </div>
        <div className="absolute bottom-1 right-2 text-xs text-white">
          {strategy.breakeven}
        </div>
      </div>

      {/* Open in Builder Button */}
      <button
        onClick={handleOpenBuilder}
        className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 hover:shadow-lg border border-slate-600 hover:border-slate-500"
      >
        Open in Builder
      </button>

      {/* Background accent gradients */}
      <div className="absolute -top-10 -right-10 w-20 h-20 bg-blue-500/10 rounded-full blur-2xl" />
      <div className="absolute -bottom-10 -left-10 w-20 h-20 bg-green-500/10 rounded-full blur-2xl" />
    </div>
  );
};

export default StrategyOptimizeCard;