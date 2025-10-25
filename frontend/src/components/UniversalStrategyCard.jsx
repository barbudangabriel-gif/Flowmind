/**
 * UniversalStrategyCard - Reusable Strategy Card Component
 * 
 * Universal card that works for ALL 69 strategies defined in strategies.json
 * Used in: Optimize tab, Strategy Library, Search results
 * 
 * Features:
 * - StrategyChart component (360x180) with P&L visualization
 * - Strategy name, category badge, complexity indicator
 * - Key metrics: Max Profit, Max Loss, Net Cost, Breakeven
 * - Legs display with color coding (BUY green, SELL red)
 * - "Open in Builder" button with state transfer
 * - Hover effects and animations
 */

import React from 'react';
import StrategyChart from './StrategyChart';
import StrategyEngine from '../services/StrategyEngine';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function UniversalStrategyCard({ 
  strategyId,
  currentPrice,
  strikes = {},
  premiums = {},
  volatility = 0.30,
  daysToExpiry = 30,
  onOpenInBuilder,
  showChart = true,
  className = ''
}) {
  // Initialize StrategyEngine
  const engine = new StrategyEngine(strategyId, currentPrice);
  engine.initialize({ strikes, premiums });
  const metrics = engine.getMetrics();

  // Category badge color
  const categoryColors = {
    bullish: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    bearish: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    neutral: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    volatility: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
  };

  // Complexity indicator
  const complexityColors = {
    beginner: 'bg-green-500',
    intermediate: 'bg-yellow-500',
    advanced: 'bg-orange-500',
    expert: 'bg-red-500'
  };

  // Category icon
  const getCategoryIcon = () => {
    switch (metrics.category) {
      case 'bullish':
        return <TrendingUp className="w-3 h-3" />;
      case 'bearish':
        return <TrendingDown className="w-3 h-3" />;
      case 'neutral':
        return <Minus className="w-3 h-3" />;
      default:
        return null;
    }
  };

  const handleOpenInBuilder = () => {
    if (onOpenInBuilder) {
      onOpenInBuilder({
        strategyId: metrics.id,
        strategyName: metrics.name,
        currentPrice,
        strikes,
        premiums,
        metrics,
        volatility,
        daysToExpiry
      });
    }
  };

  return (
    <div className={`bg-slate-800 rounded-lg border border-slate-700 hover:border-slate-600 transition-all duration-200 p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">{metrics.name}</h3>
          <div className="flex items-center gap-2">
            {/* Category Badge */}
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${categoryColors[metrics.category] || categoryColors.neutral}`}>
              {getCategoryIcon()}
              {metrics.category}
            </span>
            {/* Complexity Dots */}
            <div className="flex items-center gap-1">
              {[1, 2, 3].map((dot) => (
                <div 
                  key={dot}
                  className={`w-1.5 h-1.5 rounded-full ${
                    dot <= (metrics.complexity === 'beginner' ? 1 : metrics.complexity === 'intermediate' ? 2 : 3)
                      ? complexityColors[metrics.complexity]
                      : 'bg-slate-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      {showChart && (
        <div className="mb-3">
          <StrategyChart 
            strategyId={strategyId}
            currentPrice={currentPrice}
            strikes={strikes}
            premiums={premiums}
            volatility={volatility}
            daysToExpiry={daysToExpiry}
            size="card"
            showProbability={false}
          />
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div>
          <div className="text-gray-400 mb-0.5">Max Profit</div>
          <div className="text-white font-semibold">
            {metrics.maxProfit === 'unlimited' 
              ? 'Unlimited' 
              : `$${typeof metrics.maxProfit === 'number' ? metrics.maxProfit.toFixed(0) : '0'}`
            }
          </div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Max Loss</div>
          <div className="text-white font-semibold">
            -${typeof metrics.maxLoss === 'number' ? metrics.maxLoss.toFixed(0) : '0'}
          </div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Net Cost</div>
          <div className="text-white font-semibold">
            ${Math.abs(metrics.netCost).toFixed(0)}
          </div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Breakeven</div>
          <div className="text-white font-semibold">
            ${metrics.breakeven[0]?.toFixed(2) || '0.00'}
          </div>
        </div>
      </div>

      {/* Legs Display */}
      <div className="mb-3 space-y-1">
        {metrics.legs.map((leg, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs">
            <span className={`font-semibold ${leg.action === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
              {leg.action.toUpperCase()}
            </span>
            <span className="text-white">{leg.quantity}x</span>
            <span className="text-white uppercase">{leg.type}</span>
            <span className="text-cyan-400">
              ${typeof leg.strike === 'number' ? leg.strike.toFixed(2) : leg.strike}
            </span>
            {leg.premium > 0 && (
              <span className="text-gray-400">
                @${(leg.premium / 100).toFixed(2)}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Description (if short enough) */}
      {metrics.description && metrics.description.length < 100 && (
        <p className="text-xs text-gray-400 mb-3 line-clamp-2">
          {metrics.description}
        </p>
      )}

      {/* Open in Builder Button */}
      <button
        onClick={handleOpenInBuilder}
        className="w-full px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-semibold transition-colors text-sm"
      >
        Open in Builder
      </button>
    </div>
  );
}

/**
 * UniversalStrategyCard.Skeleton - Loading state
 */
UniversalStrategyCard.Skeleton = function StrategyCardSkeleton() {
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 animate-pulse">
      <div className="h-6 bg-slate-700 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-slate-700 rounded w-1/2 mb-3"></div>
      <div className="h-[180px] bg-slate-700 rounded mb-3"></div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-10 bg-slate-700 rounded"></div>
        ))}
      </div>
      <div className="h-10 bg-slate-700 rounded"></div>
    </div>
  );
};

/**
 * UniversalStrategyCard.Empty - Empty state
 */
UniversalStrategyCard.Empty = function StrategyCardEmpty({ message = 'No strategies found' }) {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-12 text-gray-400">
      <svg className="w-16 h-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p className="text-lg font-medium">{message}</p>
    </div>
  );
};
