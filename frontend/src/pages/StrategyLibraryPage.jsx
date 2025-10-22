import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { STRATEGIES, ALL_STRATEGIES } from '../data/strategies';
import { TrendingUp, TrendingDown, Activity, Target, ChevronRight, List, LayoutGrid } from 'lucide-react';
import StrategyCard from '../components/StrategyCard';

// Icon mapping pentru stance
const stanceIcons = {
  bullish: TrendingUp,
  bearish: TrendingDown,
  neutral: Activity,
  directional: Target,
};

const stanceColors = {
  bullish: 'text-green-400 bg-green-500/10 border-green-500/30',
  bearish: 'text-red-400 bg-red-500/10 border-red-500/30',
  neutral: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  directional: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
};

const levelColors = {
  Novice: 'text-emerald-400',
  Intermediate: 'text-blue-400',
  Advanced: 'text-orange-400',
  Expert: 'text-red-400',
};

function StrategyRow({ strategy, level, index }) {
  const navigate = useNavigate();
  const StanceIcon = stanceIcons[strategy.stance] || Activity;

  const handleClick = () => {
    navigate(`/builder/${strategy.id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="flex items-center gap-3 py-2.5 px-3 hover:bg-slate-800/30 transition-colors cursor-pointer group border-b border-slate-700/30"
    >
      {/* Index */}
      <div className="text-slate-600 text-sm font-medium w-6">
        {index}
      </div>

      {/* Strategy Name */}
      <div className="flex-1 min-w-0">
        <div className="text-white text-base font-medium group-hover:text-cyan-400 transition-colors truncate">
          {strategy.name}
        </div>
      </div>

      {/* Level */}
      <div className={`text-sm font-semibold w-24 ${levelColors[level]}`}>
        {level}
      </div>

      {/* Stance */}
      <div className="flex items-center gap-1.5 w-24">
        <StanceIcon className={`w-4 h-4 ${stanceColors[strategy.stance].split(' ')[0]}`} />
        <span className="text-sm text-slate-400 capitalize">{strategy.stance}</span>
      </div>

      {/* Tags */}
      <div className="flex gap-1.5 w-56">
        {strategy.tags && strategy.tags.slice(0, 3).map((tag, idx) => (
          <span key={idx} className="px-2 py-0.5 bg-slate-800/30 text-slate-500 text-xs rounded border border-slate-700/30">
            {tag}
          </span>
        ))}
      </div>

      {/* Arrow */}
      <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-cyan-400 transition-colors flex-shrink-0" />
    </div>
  );
}

export default function StrategyLibraryPage() {
  const [selectedLevel, setSelectedLevel] = useState('Novice');
  const [selectedStance, setSelectedStance] = useState('all');
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'card'
  const [optimizeSymbol, setOptimizeSymbol] = useState(''); // For Optimize tab

  const levels = ['Novice', 'Intermediate', 'Advanced', 'Expert'];
  const stances = ['bullish', 'bearish', 'neutral', 'directional', 'optimize'];

  // Filter strategies
  const getFilteredStrategies = () => {
    let filtered = {};

    if (selectedLevel === 'all') {
      // Copy all strategies
      filtered = { ...STRATEGIES };
    } else {
      // Copy only selected level
      filtered = { [selectedLevel]: [...STRATEGIES[selectedLevel]] };
    }

    // Apply stance filter
    if (selectedStance !== 'all') {
      const result = {};
      Object.keys(filtered).forEach((level) => {
        const filteredByStance = filtered[level].filter((s) => s.stance === selectedStance);
        if (filteredByStance.length > 0) {
          result[level] = filteredByStance;
        }
      });
      return result;
    }

    return filtered;
  };

  const filteredStrategies = getFilteredStrategies();
  const totalStrategies = Object.values(filteredStrategies).reduce((sum, arr) => sum + arr.length, 0);

  // Calculate strategy counts by level
  const allStrategies = STRATEGIES;
  const noviceCount = allStrategies.Novice?.length || 0;
  const intermediateCount = allStrategies.Intermediate?.length || 0;
  const advancedCount = allStrategies.Advanced?.length || 0;
  const expertCount = allStrategies.Expert?.length || 0;
  const totalCount = noviceCount + intermediateCount + advancedCount + expertCount;

  // Calculate global index for strategies
  let globalIndex = 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a] p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-white mb-2">
            Strategy <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">Library</span>
          </h1>
          <p className="text-slate-400 text-sm mb-2">
            Explore {totalStrategies} options strategies across all experience levels
          </p>
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="text-emerald-400 font-semibold">{noviceCount}</span> Novice
            </span>
            <span className="text-slate-700">•</span>
            <span className="flex items-center gap-1.5">
              <span className="text-blue-400 font-bold">{intermediateCount}</span> <span className="font-bold">Intermediate</span>
            </span>
            <span className="text-slate-700">•</span>
            <span className="flex items-center gap-1.5">
              <span className="text-orange-400 font-semibold">{advancedCount}</span> Advanced
            </span>
            <span className="text-slate-700">•</span>
            <span className="flex items-center gap-1.5">
              <span className="text-red-400 font-semibold">{expertCount}</span> Expert
            </span>
            <span className="text-slate-700">•</span>
            <span className="flex items-center gap-1.5">
              <span className="text-slate-300 font-bold">{totalCount}</span> Total
            </span>
          </div>
        </div>

        {/* Stats - Removed cards, now just filters */}

        {/* Filters */}
        <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-6">
            {/* View Mode Toggle */}
            <div>
              <label className="text-sm text-slate-500 mb-2 block font-medium">View</label>
              <div className="flex gap-1">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-all ${
                    viewMode === 'list'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                  }`}
                  title="List View"
                >
                  <List className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('card')}
                  className={`p-2 rounded-md transition-all ${
                    viewMode === 'card'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                  }`}
                  title="Card View"
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Level Filter */}
            <div className="flex-1">
              <label className="text-sm text-slate-500 mb-2 block font-medium">Experience Level</label>
              <div className="flex gap-1.5">
                <button
                  onClick={() => setSelectedLevel('all')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    selectedLevel === 'all'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                  }`}
                >
                  All
                </button>
                {levels.map((level) => (
                  <button
                    key={level}
                    onClick={() => setSelectedLevel(level)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                      selectedLevel === level
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                        : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Stance Filter */}
            <div className="flex-1">
              <label className="text-sm text-slate-500 mb-2 block font-medium">Market Outlook</label>
              <div className="flex gap-1.5">
                <button
                  onClick={() => setSelectedStance('all')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    selectedStance === 'all'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                  }`}
                >
                  All
                </button>
                {stances.map((stance) => (
                  <button
                    key={stance}
                    onClick={() => setSelectedStance(stance)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-all capitalize ${
                      selectedStance === stance
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                        : 'bg-slate-700/30 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                    }`}
                  >
                    {stance}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Optimize Tab - Special Layout */}
        {selectedStance === 'optimize' && (
          <div className="space-y-6">
            {/* Ticker Input */}
            <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Find Optimal Strategy</h2>
              <div className="max-w-md">
                <label className="text-sm text-slate-400 mb-2 block">Enter Ticker Symbol</label>
                <input
                  type="text"
                  value={optimizeSymbol}
                  onChange={(e) => setOptimizeSymbol(e.target.value.toUpperCase())}
                  placeholder="TSLA"
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
                <p className="text-xs text-slate-500 mt-2">
                  We'll analyze market conditions and suggest the best strategies for this ticker
                </p>
              </div>
            </div>

            {/* Suggested Strategies */}
            {optimizeSymbol && (
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">
                  Recommended Strategies for <span className="text-cyan-400">{optimizeSymbol}</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* Mock suggested strategies - will be replaced with real data */}
                  {[
                    { name: 'Bull Call Spread', returnPercent: 85, chancePercent: 65, profit: 1500, risk: 500 },
                    { name: 'Long Call', returnPercent: 120, chancePercent: 45, profit: 3000, risk: 2500 },
                    { name: 'Iron Condor', returnPercent: 25, chancePercent: 70, profit: 750, risk: 3000 },
                  ].map((strategy, idx) => (
                    <StrategyCard
                      key={idx}
                      strategy={{
                        ...strategy,
                        legs: [],
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!optimizeSymbol && (
              <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
                <div className="text-slate-400 text-lg mb-2">Enter a ticker to get started</div>
                <p className="text-slate-600 text-sm">We'll analyze market data and recommend optimal strategies</p>
              </div>
            )}
          </div>
        )}

        {/* List View */}
        {viewMode === 'list' && selectedStance !== 'optimize' && (
          <>
            {/* Table Header */}
            <div className="bg-slate-800/20 border border-slate-700/30 rounded-t-lg">
              <div className="flex items-center gap-3 py-2.5 px-3 text-sm font-semibold text-slate-400 border-b border-slate-700/30">
                <div className="w-6">#</div>
                <div className="flex-1">Strategy Name</div>
                <div className="w-24">Level</div>
                <div className="w-24">Stance</div>
                <div className="w-56">Tags</div>
                <div className="w-4"></div>
              </div>
            </div>

            {/* Strategy List */}
            <div className="bg-slate-800/10 border-x border-b border-slate-700/30 rounded-b-lg">
              {Object.entries(filteredStrategies).map(([level, strategies]) => {
                if (strategies.length === 0) return null;

                return strategies.map((strategy) => {
                  const currentIndex = globalIndex++;
                  return (
                    <StrategyRow
                      key={strategy.id}
                      strategy={strategy}
                      level={level}
                      index={currentIndex}
                    />
                  );
                });
              })}
            </div>
          </>
        )}

        {/* Card View */}
        {viewMode === 'card' && selectedStance !== 'optimize' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(filteredStrategies).map(([level, strategies]) => {
              if (strategies.length === 0) return null;

              return strategies.map((strategy) => (
                <StrategyCard
                  key={strategy.id}
                  strategy={{
                    name: strategy.name,
                    legs: strategy.buildParams ? strategy.buildParams().legs : [],
                    returnPercent: Math.floor(Math.random() * 100) + 50, // Mock data
                    chancePercent: Math.floor(Math.random() * 50) + 30, // Mock data
                    profit: Math.floor(Math.random() * 5000) + 500, // Mock data
                    risk: Math.floor(Math.random() * 3000) + 200, // Mock data
                  }}
                />
              ));
            })}
          </div>
        )}

        {/* No Results */}
        {totalStrategies === 0 && selectedStance !== 'optimize' && (
          <div className="text-center py-16">
            <div className="text-slate-500 text-lg mb-2">No strategies found</div>
            <p className="text-slate-600 text-sm">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}
