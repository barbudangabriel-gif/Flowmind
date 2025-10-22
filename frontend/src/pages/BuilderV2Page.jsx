// =============================================
// FlowMind — Builder V2 (Unified Tabs)
// =============================================
import React, { useState, useEffect } from 'react';
import { Hammer, Target, BookOpen, TrendingUp, TrendingDown, ChevronDown, Search, RefreshCw, ArrowUp, ArrowDown, Minus, ArrowUpDown, ArrowUpCircle, ArrowDownCircle, ChevronLeft, ChevronRight, ArrowLeft, ArrowRight } from 'lucide-react';
import StrategyCard from '../components/StrategyCard';

// Custom slider styles
const sliderStyles = `
  /* Hide number input arrows */
  input[type=number]::-webkit-inner-spin-button,
  input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type=number] {
    -moz-appearance: textfield;
  }
  
  .slider-cyan::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    background: #06b6d4;
    cursor: pointer;
    border-radius: 50%;
    border: 2px solid #0e7490;
  }
  .slider-cyan::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #06b6d4;
    cursor: pointer;
    border-radius: 50%;
    border: 2px solid #0e7490;
  }
  .slider-green::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    background: #22c55e;
    cursor: pointer;
    border-radius: 50%;
    border: 2px solid #16a34a;
  }
  .slider-green::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #22c55e;
    cursor: pointer;
    border-radius: 50%;
    border: 2px solid #16a34a;
  }
`;

/**
 * BuilderV2Page - Unified builder interface with 4 tabs
 * - Builder: Strategy construction tool
 * - Optimize: AI-suggested strategies for ticker
 * - Strategy: Library of 69 strategies
 * - Flow: Options flow data with 6 sub-views
 */
export default function BuilderV2Page() {
  const [activeTab, setActiveTab] = useState('optimize');
  const [symbol, setSymbol] = useState('TSLA');
  const [price, setPrice] = useState(217.26);
  const [change, setChange] = useState(2.34);
  const [changePercent, setChangePercent] = useState(1.09);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedDirection, setSelectedDirection] = useState(null);
  const [targetPrice, setTargetPrice] = useState(270.00);
  const [budget, setBudget] = useState('');
  const [selectedExpiryIndex, setSelectedExpiryIndex] = useState(0);
  const [sliderPosition, setSliderPosition] = useState(5); // 0-10 scale
  
  // Calculate Max Return and Max Chance based on slider position
  // Position 0 = Max Chance (0% return, 100% chance)
  // Position 10 = Max Return (500% return, 0% chance)
  const maxReturn = Math.round((sliderPosition / 10) * 500);
  const maxChance = Math.round(((10 - sliderPosition) / 10) * 100);
  
  // Mock expiration dates (will be fetched from options chain API)
  const expirationDates = [
    '2025-10-24', '2025-10-31', '2025-11-07', '2025-11-14', '2025-11-21',
    '2025-11-28', '2025-12-05', '2025-12-12', '2025-12-19', '2025-12-26',
    '2026-01-02', '2026-01-17', '2026-02-21'
  ];
  
  // Group dates by month
  const groupedDates = expirationDates.reduce((acc, date) => {
    const monthYear = new Date(date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    if (!acc[monthYear]) acc[monthYear] = [];
    acc[monthYear].push(date);
    return acc;
  }, {});
  
  // Inject slider styles
  useEffect(() => {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = sliderStyles;
    document.head.appendChild(styleSheet);
    return () => document.head.removeChild(styleSheet);
  }, []);
  
  console.log('BuilderV2Page rendering, activeTab:', activeTab);

  const handleRefresh = () => {
    setIsRefreshing(true);
    // TODO: Fetch real-time data
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  // Calculate growth percentage
  const growthPercent = ((targetPrice - price) / price * 100).toFixed(2);

  const handlePrevExpiry = () => {
    setSelectedExpiryIndex((prev) => Math.max(0, prev - 1));
  };

  const handleNextExpiry = () => {
    setSelectedExpiryIndex((prev) => Math.min(expirationDates.length - 1, prev + 1));
  };

  const directionConfig = [
    { id: 'very-bearish', label: 'Very Bearish', icon: TrendingDown, color: 'text-rose-500' },
    { id: 'bearish', label: 'Bearish', icon: ArrowDown, color: 'text-red-400' },
    { id: 'directional', label: 'Directional', icon: ArrowUpDown, color: 'text-cyan-400' },
    { id: 'neutral', label: 'Neutral', icon: Minus, color: 'text-slate-400' },
    { id: 'bullish', label: 'Bullish', icon: ArrowUp, color: 'text-green-400' },
    { id: 'very-bullish', label: 'Very Bullish', icon: TrendingUp, color: 'text-emerald-400' },
  ];

  const tabs = [
    { id: 'builder', label: 'Build', icon: Hammer },
    { id: 'optimize', label: 'Optimize', icon: Target },
    { id: 'strategy', label: 'Strategy', icon: BookOpen },
    { id: 'flow', label: 'Flow', icon: TrendingUp },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a]">
      {/* Tab Navigation */}
      <div className="border-b border-slate-700/30">
        <div className="px-8 py-4 flex justify-center">
          <div className="w-3/5 flex gap-1 justify-center">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-8 py-5 text-base font-semibold transition-all border-b-2 hover:bg-transparent ${
                    activeTab === tab.id
                      ? 'border-cyan-500 text-cyan-400'
                      : 'border-transparent text-white hover:text-cyan-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Ticker Header Bar */}
      <div className="border-b border-slate-700/30 bg-slate-900/40 backdrop-blur-sm">
        <div className="px-8 py-4 flex justify-center">
          <div className="w-3/5 flex items-center justify-center gap-6">
            {/* Symbol Search */}
            <div className="flex items-center gap-2">
              <label className="text-white text-sm font-medium">Symbol:</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="TSLA"
                className="w-20 px-3 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white text-sm font-semibold placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all text-center"
              />
            </div>

            {/* Price Display */}
            <div className="flex items-center gap-4">
              <div className="text-white font-semibold text-2xl">
                ${price.toFixed(2)}
              </div>
              <div className="flex flex-col gap-0.5">
                <div className={`text-sm font-semibold ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {change >= 0 ? '+' : ''}{change.toFixed(2)}
                </div>
                <div className={`text-xs font-medium ${change >= 0 ? 'text-green-500/70' : 'text-red-500/70'}`}>
                  {change >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* Real-time State */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-full">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              <span className="text-emerald-400 text-xs font-semibold">REAL-TIME</span>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg text-white hover:text-white text-sm font-semibold transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Direction Filter */}
      <div className="border-b border-slate-700/30 bg-slate-900/20">
        <div className="px-8 py-4 flex justify-center">
          <div className="w-3/4 flex items-center justify-center gap-3">
            {directionConfig.map((direction) => {
              const Icon = direction.icon;
              const isActive = selectedDirection === direction.id;
              
              return (
                <button
                  key={direction.id}
                  onClick={() => setSelectedDirection(direction.id)}
                  className={`flex flex-col items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    isActive
                      ? 'border-2 border-cyan-500'
                      : 'border-2 border-transparent hover:bg-transparent'
                  }`}
                >
                  {/* Icon with Circle Border */}
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center border-2 ${
                    isActive 
                      ? 'bg-cyan-500 border-cyan-500' 
                      : `border-current ${direction.color}`
                  }`}>
                    <Icon className={`w-8 h-8 ${isActive ? 'text-white' : direction.color}`} />
                  </div>
                  
                  {/* Label */}
                  <span className={`text-base font-semibold ${
                    isActive ? 'text-cyan-400' : 'text-white'
                  }`}>
                    {direction.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Target Price & Budget */}
      <div className="border-b border-slate-700/30 bg-slate-900/20">
        <div className="px-8 py-4 flex justify-center">
          <div className="w-3/5 flex flex-col items-center gap-4">
            {/* Target Price */}
            <div className="flex items-center gap-3">
              <label className="text-white text-sm font-medium w-24 text-right">Target Price:</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(parseFloat(e.target.value) || 0)}
                  className="w-24 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white text-sm font-semibold focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                  step="0.007"
                />
                <span className={`text-sm font-semibold ${growthPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ({growthPercent >= 0 ? '+' : ''}{growthPercent}%)
                </span>
              </div>
            </div>

            {/* Budget */}
            <div className="flex items-center gap-3" style={{ marginLeft: '-70px' }}>
              <label className="text-white text-sm font-medium w-24 text-right">Budget:</label>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white text-sm font-semibold">$</span>
                  <input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    placeholder="Budget..."
                    step="0.7"
                    className="w-24 pl-7 pr-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white text-sm font-semibold placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                  />
                </div>
              </div>
              {budget && (
                <span className="text-xs text-slate-500">
                  (Strategies filtered by budget)
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Expiration Carousel & Sliders */}
      <div className="border-b border-slate-700/30 bg-slate-900/20">
        <div className="px-8 py-4">
          {/* Container at 60% width, centered */}
          <div className="w-3/5 mx-auto flex flex-col items-center">
            {/* Expiration Carousel */}
            <div className="w-1/2 mb-4">
              {/* Horizontal Display by Month */}
              <div className="flex items-start gap-4 justify-center">
              {Object.entries(groupedDates).map(([monthYear, dates]) => (
                <div key={monthYear} className="flex flex-col gap-2">
                  {/* Month Header */}
                  <div className="text-white text-xs font-semibold uppercase tracking-wide text-center">
                    {monthYear}
                  </div>
                  
                  {/* Dates for this month */}
                  <div className="flex items-center gap-1.5">
                    {dates.map((date) => {
                      const dateIndex = expirationDates.indexOf(date);
                      const isSelected = dateIndex === selectedExpiryIndex;
                      const dayNum = new Date(date).getDate();
                      
                      return (
                        <button
                          key={date}
                          onClick={() => setSelectedExpiryIndex(dateIndex)}
                          className={`w-10 h-10 rounded-lg text-sm font-bold transition-all ${
                            isSelected
                              ? 'bg-cyan-500 text-white'
                              : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 hover:text-white'
                          }`}
                        >
                          {dayNum}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
            </div>

            {/* Single Slider with 10 positions */}
            <div className="w-1/2">
              {/* Single Axis with 10 clickable positions */}
              <div className="relative">
                {/* Horizontal track */}
                <div className="relative h-2 bg-slate-700 rounded-full mb-2"></div>
                
                {/* 10 clickable positions */}
                <div className="flex justify-between items-center absolute top-0 left-0 right-0">
                  {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((position) => {
                    const isSelected = position === sliderPosition;
                    
                    return (
                      <button
                        key={position}
                        onClick={() => setSliderPosition(position)}
                        className="relative cursor-pointer group flex items-center"
                        style={{ height: '8px' }}
                      >
                        {/* Active indicator (small gray rectangle) */}
                        {isSelected && (
                          <div className="w-1.5 h-6 bg-slate-400 rounded-sm"></div>
                        )}
                        {!isSelected && (
                          <div className="w-px h-full bg-slate-600 group-hover:bg-slate-400"></div>
                        )}
                      </button>
                    );
                  })}
                </div>
                
                {/* Helper text with arrows - below slider */}
                <div className="flex justify-between items-center text-xs text-white mt-2">
                  <div className="flex items-center gap-1">
                    <ArrowLeft className="w-3 h-3" />
                    <span>Max Return</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>Max Chance</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-8">
        {activeTab === 'builder' && <BuilderTab />}
        {activeTab === 'optimize' && <OptimizeTab symbol={symbol} selectedDirection={selectedDirection} />}
        {activeTab === 'strategy' && <StrategyTab />}
        {activeTab === 'flow' && <FlowTab />}
      </div>
    </div>
  );
}

/**
 * BuilderTab - Strategy construction tool
 */
function BuilderTab() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-semibold text-white mb-4">Strategy Builder</h2>
        <p className="text-slate-400 mb-6">
          Build custom options strategies with live pricing and Greeks analysis
        </p>
        <div className="text-sm text-slate-600">
          TODO: Import BuilderPage content here
        </div>
      </div>
    </div>
  );
}

/**
 * OptimizeTab - AI-suggested strategies for a ticker
 */
function OptimizeTab({ symbol, selectedDirection }) {
  const mockStrategies = [
    { 
      name: 'Bull Call Spread',
      legs: [
        { side: 'BUY', kind: 'CALL', strike: '195', qty: 1 },
        { side: 'SELL', kind: 'CALL', strike: '210', qty: 1 }
      ],
      returnPercent: 85,
      chancePercent: 65,
      profit: 1500,
      risk: 500,
      collateral: 0
    },
    {
      name: 'Long Call',
      legs: [{ side: 'BUY', kind: 'CALL', strike: '195', qty: 1 }],
      returnPercent: 120,
      chancePercent: 45,
      profit: 3000,
      risk: 2500,
      collateral: 0
    },
    {
      name: 'Iron Condor',
      legs: [
        { side: 'SELL', kind: 'PUT', strike: '185', qty: 1 },
        { side: 'BUY', kind: 'PUT', strike: '180', qty: 1 },
        { side: 'SELL', kind: 'CALL', strike: '215', qty: 1 },
        { side: 'BUY', kind: 'CALL', strike: '220', qty: 1 }
      ],
      returnPercent: 25,
      chancePercent: 70,
      profit: 750,
      risk: 3000,
      collateral: 0
    },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Suggested Strategies */}
      {symbol && selectedDirection && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">
            Recommended Strategies for <span className="text-cyan-400">{symbol}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockStrategies.map((strategy, idx) => (
              <StrategyCard
                key={idx}
                strategy={strategy}
                onClick={() => console.log(`Open ${strategy.name} in Builder`)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!symbol || !selectedDirection) && (
        <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
          <div className="text-slate-400 text-lg mb-2">Select a direction to see strategies</div>
          <p className="text-slate-600 text-sm">Choose a market direction above to view recommended strategies</p>
        </div>
      )}
    </div>
  );
}

/**
 * StrategyTab - Library of 69 strategies
 */
function StrategyTab() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-semibold text-white mb-4">Strategy Library</h2>
        <p className="text-slate-400 mb-6">
          Browse 69 options strategies across all experience levels
        </p>
        <div className="text-sm text-slate-600">
          TODO: Import StrategyLibraryPage content here
        </div>
      </div>
    </div>
  );
}

/**
 * FlowTab - Options flow data with 6 sub-views
 */
function FlowTab() {
  const [selectedFlow, setSelectedFlow] = useState('summary');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const flowOptions = [
    { id: 'summary', label: 'Flow Summary' },
    { id: 'live', label: 'Live Flow' },
    { id: 'historical', label: 'Historical Flow' },
    { id: 'news', label: 'News Flow' },
    { id: 'congress', label: 'Congress Flow' },
    { id: 'insiders', label: 'Insiders Flow' },
  ];

  const selectedOption = flowOptions.find(opt => opt.id === selectedFlow);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Flow Type Dropdown */}
      <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-4">
        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full md:w-64 flex items-center justify-between px-4 py-2.5 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white hover:border-cyan-500/50 transition-all"
          >
            <span className="font-semibold">{selectedOption.label}</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute top-full left-0 mt-2 w-full md:w-64 bg-slate-800 border border-slate-700/50 rounded-lg shadow-xl z-10 overflow-hidden">
              {flowOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    setSelectedFlow(option.id);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full px-4 py-2.5 text-left transition-all ${
                    selectedFlow === option.id
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'text-slate-300 hover:bg-slate-700/50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Flow Content */}
      <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-8">
        {selectedFlow === 'summary' && <FlowSummaryView />}
        {selectedFlow === 'live' && <LiveFlowView />}
        {selectedFlow === 'historical' && <HistoricalFlowView />}
        {selectedFlow === 'news' && <NewsFlowView />}
        {selectedFlow === 'congress' && <CongressFlowView />}
        {selectedFlow === 'insiders' && <InsidersFlowView />}
      </div>
    </div>
  );
}

// Flow sub-views
function FlowSummaryView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">Flow Summary</h3>
      <p className="text-slate-400">Aggregated options flow data for the day</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage summary content</div>
    </div>
  );
}

function LiveFlowView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">Live Flow</h3>
      <p className="text-slate-400">Real-time options flow updates</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage live content</div>
    </div>
  );
}

function HistoricalFlowView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">Historical Flow</h3>
      <p className="text-slate-400">Past options flow data and trends</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage historical content</div>
    </div>
  );
}

function NewsFlowView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">News Flow</h3>
      <p className="text-slate-400">Market news affecting options activity</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage news content</div>
    </div>
  );
}

function CongressFlowView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">Congress Flow</h3>
      <p className="text-slate-400">Congressional trading activity</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage congress content</div>
    </div>
  );
}

function InsidersFlowView() {
  return (
    <div className="text-center">
      <h3 className="text-xl font-semibold text-white mb-4">Insiders Flow</h3>
      <p className="text-slate-400">Corporate insider trading activity</p>
      <div className="text-sm text-slate-600 mt-4">TODO: Import FlowPage insiders content</div>
    </div>
  );
}
