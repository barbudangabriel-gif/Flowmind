// =============================================
// FlowMind — Builder V2 (Unified Tabs)
// =============================================
/**
 * TODO: Strategy Card → Build Tab Integration
 * 
 * FEATURE REQUEST (Oct 23, 2025):
 * When user clicks "Open in Builder" button on a StrategyCard (in Optimize tab),
 * the strategy should transfer to Build tab with full chart visualization.
 * 
 * Flow:
 * 1. User in Optimize tab sees StrategyCard (e.g., Long Call) with small chart
 * 2. User clicks "Open in Builder" button
 * 3. App switches activeTab to 'build'
 * 4. Build tab loads with:
 *    - Strategy name (Long Call)
 *    - Strategy legs (Buy 220C)
 *    - Metrics (Net Debit, Max Loss, Max Profit, etc.)
 *    - Full-size P&L chart with same data
 * 
 * Implementation:
 * - Add state to store selected strategy data
 * - Pass onClick handler to StrategyCard that:
 *   a) Sets selectedStrategy state
 *   b) Changes activeTab to 'build'
 * - BuilderTab reads selectedStrategy and displays full chart
 * 
 * Chart specs:
 * - Small chart in StrategyCard: 360x180px
 * - Large chart in Build tab: 1000x400px (full width of container)
 * - Same P&L curve, colors, axes, but scaled up
 */
import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Hammer, Target, BookOpen, TrendingUp, TrendingDown, ChevronDown, Search, RefreshCw, ArrowUp, ArrowDown, Minus, ArrowUpDown, ArrowUpCircle, ArrowDownCircle, ChevronLeft, ChevronRight, ArrowLeft, ArrowRight, Plus } from 'lucide-react';
import StrategyCard from '../components/StrategyCard';
import StrategyChart from '../components/StrategyChart';
import StrategyLibraryPage from './StrategyLibraryPage';
import BuilderPage from './BuilderPage';
import FlowPage from './FlowPage';
import FlowFilters from '../components/FlowFilters';
import FlowSummary from '../components/FlowSummary';
import FlowTable from '../components/FlowTable';
import LiveFlow from './Flow/LiveFlow';
import LiveLitTradesFeed from './LiveLitTradesFeed';
import LiveOffLitTradesFeed from './LiveOffLitTradesFeed';
import { FiltersPanel } from '../components/FiltersPanel';
import StrategyEngine from '../services/StrategyEngine';

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
  
  /* Custom Scrollbar - Rectangular Cyan */
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px !important;
    height: 8px !important;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3) !important;
    border-radius: 0 !important;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #0e7490 !important;
    border-radius: 0 !important;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #0891b2 !important;
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
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('builder');
  const [layerTab, setLayerTab] = useState('graph'); // table, graph view in Build tab
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
  const [selectedStrategy, setSelectedStrategy] = useState(null); // For strategy transfer from Optimize tab
  
  // Receive strategy from navigation state (from UniversalStrategyCardTestPage)
  useEffect(() => {
    if (location.state?.selectedStrategy) {
      console.log('Received strategy from navigation:', location.state.selectedStrategy);
      setSelectedStrategy(location.state.selectedStrategy);
      if (location.state.openBuildTab) {
        setActiveTab('builder');
      }
      if (location.state.openGraphView) {
        setLayerTab('graph');
      }
    }
  }, [location.state]);
  
  console.log('BuilderV2Page rendering, activeTab:', activeTab);
  
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
    { id: 'neutral', label: 'Neutral', icon: Minus, color: 'text-slate-400' },
    { id: 'directional', label: 'Directional', icon: ArrowUpDown, color: 'text-cyan-400' },
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
          <div className="w-[52%] flex gap-1 justify-center">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    console.log('Switching to tab:', tab.id);
                    setActiveTab(tab.id);
                  }}
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

      {/* Tab Content */}
      <div className="p-8">
        {console.log('Current activeTab:', activeTab)}
        {activeTab === 'builder' && <BuilderTab selectedStrategy={selectedStrategy} />}
        {activeTab === 'optimize' && <OptimizeTab 
          symbol={symbol} 
          setSymbol={setSymbol}
          price={price}
          change={change}
          changePercent={changePercent}
          isRefreshing={isRefreshing}
          handleRefresh={handleRefresh}
          selectedDirection={selectedDirection}
          setSelectedDirection={setSelectedDirection}
          directionConfig={directionConfig}
          expirationDates={expirationDates}
          selectedExpiryIndex={selectedExpiryIndex}
          setSelectedExpiryIndex={setSelectedExpiryIndex}
          targetPrice={targetPrice}
          setTargetPrice={setTargetPrice}
          budget={budget}
          setBudget={setBudget}
          sliderPosition={sliderPosition}
          setSliderPosition={setSliderPosition}
          maxReturn={maxReturn}
          maxChance={maxChance}
          groupedDates={groupedDates}
          growthPercent={growthPercent}
        />}
        {activeTab === 'strategy' && <StrategyTab />}
        {activeTab === 'flow' && <FlowTab />}
      </div>
    </div>
  );
}

/**
 * OptionsTable - Profit/Loss Grid Component
 * Shows profit/loss percentages across 23 strikes and 21 expiration dates
 * Values calculated dynamically based on range and IV using Black-Scholes
 */
function OptionsTable({ rangeValue, ivValue, currentPrice, strike, premium, displayMode }) {
  // Strike prices (23 values calculated from current price and range)
  const numStrikes = 23;
  const strikes = Array.from({ length: numStrikes }, (_, i) => {
    const minPrice = currentPrice * (1 - rangeValue / 100);
    const maxPrice = currentPrice * (1 + rangeValue / 100);
    const step = (maxPrice - minPrice) / (numStrikes - 1);
    return Math.round(minPrice + i * step);
  }).reverse(); // Reverse: highest price at top, lowest at bottom
  
  // Expiration dates (21 dates - mock data for visual only)
  const dates = [
    { month: "Oct", day: 24, dte: 0 },
    { month: "Oct", day: 31, dte: 7 },
    { month: "Nov", day: 7, dte: 14 },
    { month: "Nov", day: 14, dte: 21 },
    { month: "Nov", day: 21, dte: 28 },
    { month: "Dec", day: 5, dte: 42 },
    { month: "Dec", day: 12, dte: 49 },
    { month: "Dec", day: 19, dte: 56 },
    { month: "Dec", day: 26, dte: 63 },
    { month: "Jan", day: 2, dte: 70 },
    { month: "Jan", day: 9, dte: 77 },
    { month: "Jan", day: 16, dte: 84 },
    { month: "Jan", day: 23, dte: 91 },
    { month: "Jan", day: 30, dte: 98 },
    { month: "Feb", day: 6, dte: 105 },
    { month: "Feb", day: 13, dte: 112 },
    { month: "Feb", day: 20, dte: 119 },
    { month: "Feb", day: 27, dte: 126 },
    { month: "Mar", day: 6, dte: 133 },
    { month: "Mar", day: 13, dte: 140 },
    { month: "Dec", day: 18, dte: 420 }
  ];

  // Black-Scholes helper functions
  const normalCDF = (x) => {
    // Approximation of cumulative normal distribution
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989423 * Math.exp(-x * x / 2);
    const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - prob : prob;
  };

  const blackScholesCall = (S, K, tau, r, sigma, q = 0) => {
    if (tau <= 0) {
      // At expiration
      return Math.max(S - K, 0);
    }
    
    const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * tau) / (sigma * Math.sqrt(tau));
    const d2 = d1 - sigma * Math.sqrt(tau);
    
    const callPrice = S * Math.exp(-q * tau) * normalCDF(d1) - K * Math.exp(-r * tau) * normalCDF(d2);
    return callPrice;
  };

  // Calculate P&L for each cell
  const calculatePnL = (stockPrice, dte) => {
    const tau = dte / 365; // Convert DTE to years
    const r = 0.05; // Risk-free rate (5%)
    const sigma = ivValue / 100; // Convert IV% to decimal
    const K = 220; // Strike price (fixed)
    
    // Calculate theoretical option price
    const optionPrice = blackScholesCall(stockPrice, K, tau, r, sigma);
    
    // Contract value (1 contract = 100 shares)
    const contractValue = 100 * optionPrice;
    
    // Initial cost (premium per share * 100)
    const initialCost = 100 * 37.075; // Cost per contract
    
    // P&L in dollars
    const pnlDollar = contractValue - initialCost;
    
    // P&L as % of initial cost
    const pnlPercent = (pnlDollar / initialCost) * 100;
    
    // % of Max Risk (for Long Call, max risk = initial cost)
    const maxRiskPercent = pnlPercent; // Same as pnlPercent, capped at -100%
    
    return {
      pnlDollar,
      pnlPercent,
      contractValue,
      maxRiskPercent: Math.max(maxRiskPercent, -100) // Cap at -100%
    };
  };

  // Generate profit/loss data dynamically
  const profitLossData = {};
  strikes.forEach(strikePrice => {
    profitLossData[strikePrice] = dates.map(date => calculatePnL(strikePrice, date.dte));
  });

  // Extract values based on display mode
  const getDisplayValue = (cellData) => {
    switch(displayMode) {
      case 'pnl_dollar': return cellData.pnlDollar;
      case 'pnl_percent': return cellData.pnlPercent;
      case 'contract_value': return cellData.contractValue / 100; // Per share, not per contract
      case 'max_risk_percent': return cellData.maxRiskPercent;
      default: return cellData.pnlPercent;
    }
  };

  // Find min/max for normalization across entire grid (based on display mode)
  const allValues = Object.values(profitLossData).flat().map(cellData => getDisplayValue(cellData));
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  
  // Heatmap color function - diverging red → neutral → cyan
  const getCellColor = (value) => {
    // Normalize value to [-1, 1] range
    let normalized;
    if (value >= 0) {
      // Profit: map [0, maxValue] to [0, 1]
      normalized = maxValue > 0 ? value / maxValue : 0;
    } else {
      // Loss: map [minValue, 0] to [-1, 0]
      normalized = minValue < 0 ? value / Math.abs(minValue) : 0;
    }
    
    // Clamp to [-1, 1]
    normalized = Math.max(-1, Math.min(1, normalized));
    
    if (normalized > 0) {
      // Profit: cyan gradient (0 → +1)
      const intensity = normalized;
      if (intensity >= 0.9) return "bg-cyan-400 text-gray-900";
      if (intensity >= 0.7) return "bg-cyan-500/90 text-white";
      if (intensity >= 0.5) return "bg-cyan-500/70 text-white";
      if (intensity >= 0.3) return "bg-cyan-600/50 text-white";
      if (intensity >= 0.1) return "bg-cyan-700/30 text-white";
      return "bg-cyan-800/20 text-gray-300";
    } else if (normalized < 0) {
      // Loss: red gradient (-1 → 0)
      const intensity = Math.abs(normalized);
      if (intensity >= 0.9) return "bg-red-500 text-white";
      if (intensity >= 0.7) return "bg-red-600/90 text-white";
      if (intensity >= 0.5) return "bg-red-600/70 text-white";
      if (intensity >= 0.3) return "bg-red-700/50 text-white";
      if (intensity >= 0.1) return "bg-red-800/30 text-white";
      return "bg-red-900/20 text-gray-300";
    } else {
      // Neutral: near zero
      return "bg-gray-700/30 text-gray-300";
    }
  };

  return (
    <div className="w-full max-w-[1400px] mx-auto mb-6">
      {/* Profit/Loss Table */}
      <div className="rounded-lg border border-gray-700 shadow-2xl shadow-black/50 bg-gray-900/50">
        <table className="w-full text-xs -my-0.5">
          <thead>
            {/* Row 1: Months */}
            <tr className="bg-gray-800">
              <th rowSpan="2" className="sticky left-0 z-20 bg-gray-800 px-1 py-0 text-left font-semibold text-white border-r border-gray-700 leading-tight">
              </th>
              <th rowSpan="2" className="sticky left-[50px] z-20 bg-gray-800 px-0.5 py-0 text-center font-semibold text-white border-r border-gray-700 leading-tight">
                %
              </th>
              {/* Group dates by month */}
              <th colSpan="2" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Oct</th>
              <th colSpan="3" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Nov</th>
              <th colSpan="4" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Dec</th>
              <th colSpan="5" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Jan</th>
              <th colSpan="4" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Feb</th>
              <th colSpan="2" className="px-0.5 py-0 text-center font-semibold text-gray-300 border-r border-gray-700 leading-tight">Mar</th>
              <th colSpan="1" className="px-0.5 py-0 text-center font-semibold text-gray-300 leading-tight">Dec</th>
            </tr>
            {/* Row 2: Days */}
            <tr className="bg-gray-800 border-b border-gray-700">
              {dates.map((date, idx) => (
                <th key={idx} className="px-0.5 py-0 text-center font-semibold text-gray-400 whitespace-nowrap leading-tight">
                  {date.day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(() => {
              // Find the strike closest to 220 (once, outside the map)
              const closestStrike = strikes.reduce((prev, curr) => 
                Math.abs(curr - 220) < Math.abs(prev - 220) ? curr : prev
              );
              
              return strikes.map((strike, strikeIdx) => {
                const isStrikeLine = strike === closestStrike;
                return (
                  <tr key={strike} className={`border-t border-gray-700 hover:bg-gray-800/30 transition-colors ${isStrikeLine ? 'border-b border-dashed border-white' : ''}`}>
                  <td className="sticky left-0 z-10 px-1 py-0 text-left font-bold text-white border-r border-gray-700 leading-tight">
                    ${strike}
                  </td>
                  <td className="sticky left-[50px] z-10 px-0.5 py-0 text-center font-bold text-gray-400 border-r border-gray-700 leading-tight">
                    {(() => {
                      const maxValue = Math.max(...profitLossData[strike].map(cellData => getDisplayValue(cellData)));
                      
                      if (displayMode === 'pnl_dollar') {
                        const roundedMax = Math.round(maxValue);
                        return roundedMax > 0 ? `+$${roundedMax}` : `-$${Math.abs(roundedMax)}`;
                      } else if (displayMode === 'contract_value') {
                        return `$${maxValue.toFixed(2)}`;
                      } else {
                        const roundedMax = Math.round(maxValue);
                        return roundedMax > 0 ? `+${roundedMax}%` : `${roundedMax}%`;
                      }
                    })()}
                  </td>
                  {profitLossData[strike]?.map((cellData, dateIdx) => {
                    const value = getDisplayValue(cellData);
                    let displayText;
                    
                    if (displayMode === 'pnl_dollar') {
                      const roundedValue = Math.round(value);
                      displayText = roundedValue > 0 ? `+$${roundedValue}` : `-$${Math.abs(roundedValue)}`;
                    } else if (displayMode === 'contract_value') {
                      displayText = `$${value.toFixed(2)}`;
                    } else {
                      const roundedValue = Math.round(value);
                      displayText = roundedValue > 0 ? `+${roundedValue}%` : `${roundedValue}%`;
                    }
                    
                    return (
                      <td
                        key={dateIdx}
                        className={`px-0.5 py-0 text-center font-semibold leading-tight ${getCellColor(value)}`}
                      >
                        {displayText}
                      </td>
                    );
                  })}
                </tr>
              );
              });
            })()}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * BuilderTab - Options Trading Builder
 * Full strategy construction interface with strike selection, expiration timeline, P&L chart
 */
function BuilderTab({ selectedStrategy }) {
  const [selectedDate, setSelectedDate] = useState("18");
  const [selectedMonth, setSelectedMonth] = useState("Dec");
  const [monthWidths, setMonthWidths] = useState({});
  const monthRefs = useRef({});
  const [rangeValue, setRangeValue] = useState(37);
  const [ivValue, setIvValue] = useState(34.8);
  const [dteValue, setDteValue] = useState(420); // Start at expiration (420 DTE)
  const [layerTab, setLayerTab] = useState('graph'); // table, graph, pnl_dollar, pnl_percent, contract_value, max_risk
  const [displayMode, setDisplayMode] = useState('pnl_percent'); // 'pnl_dollar', 'pnl_percent', 'contract_value', 'max_risk_percent'
  
  // Use selectedStrategy data if available, otherwise default to AMZN Long Call
  const strategyData = selectedStrategy || {
    strategyId: 'long_call',
    strategyName: 'Long Call',
    currentPrice: 221.09,
    strikes: { strike: 220 },
    premiums: { premium: 3787.50 },
    volatility: 0.348,
    daysToExpiry: 420
  };
  
  const [symbol] = useState(selectedStrategy?.symbol || "AMZN");
  const [currentPrice] = useState(strategyData.currentPrice);
  const [priceChange] = useState(3.14);
  const [priceChangePercent] = useState(1.44);
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, price: 0, pnl: 0 });

  // Initialize StrategyEngine with selected strategy
  const engine = new StrategyEngine(strategyData.strategyId, strategyData.currentPrice);
  engine.initialize({ strikes: strategyData.strikes, premiums: strategyData.premiums });
  const metrics = engine.getMetrics();

  const months = [
    { name: "Oct", dates: ["24", "31"] },
    { name: "Nov", dates: ["7", "14", "21", "28"] },
    { name: "Dec", dates: ["5", "19"] },
    { name: "Jan '26", dates: ["16"] },
    { name: "Feb", dates: ["20"] },
    { name: "Mar", dates: ["20"] },
    { name: "Apr", dates: ["17"] },
    { name: "May", dates: ["15"] },
    { name: "Jun", dates: ["18"] },
    { name: "Aug", dates: ["21"] },
    { name: "Sep", dates: ["18"] },
    { name: "Dec", dates: ["18"] },
    { name: "Jan '27", dates: ["15"] },
    { name: "Jun", dates: ["17"] },
    { name: "Dec", dates: ["17"] },
    { name: "Jan '28", dates: ["21"] },
  ];

  const strikes = Array.from({ length: 56 }, (_, i) => 85 + i * 5);

  // Measure month card widths after render
  useEffect(() => {
    const newWidths = {};
    Object.keys(monthRefs.current).forEach((monthName) => {
      const el = monthRefs.current[monthName];
      if (el) {
        newWidths[monthName] = el.offsetWidth;
      }
    });
    setMonthWidths(newWidths);
  }, []);

  return (
    <div className="h-full bg-gradient-to-b from-[#0a0e27] via-[#0a0e1a] to-[#0a0e27] text-white p-6 overflow-y-auto">
      {/* Header with Action Buttons - aligned with 60% container */}
      <div className="w-[52%] mx-auto mb-2">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold">{strategyData.strategyName}</h1>
            <button className="text-gray-400 hover:text-gray-300">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <Plus className="w-4 h-4" />
              Add
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              Positions (1)
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              Save Trade
            </button>
            <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm">
              <RefreshCw className="w-4 h-4" />
              Historical Chart
            </button>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-2 py-1 border border-gray-600 rounded text-sm">{symbol}</div>
          <div className="text-2xl font-semibold text-white">${currentPrice}</div>
          <div className={`text-sm ${priceChange >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            <div>{priceChange >= 0 ? '+' : ''}{priceChangePercent}%</div>
            <div>{priceChange >= 0 ? '+' : ''}${priceChange}</div>
          </div>
          <div className="text-gray-400 text-sm flex items-center gap-1">
            Real-time
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Chart Section - 60% width centered */}
      <div className="w-[52%] mx-auto">
        {/* Expiration Timeline */}
        <div className="mb-2">
          <div className="text-sm mb-2">EXPIRATION: 1.2y</div>
          <div className="relative h-20 bg-gray-900/50 rounded overflow-x-auto custom-scrollbar">
            <div className="flex items-center justify-between px-2 h-full">
              {months.map((month, idx) => (
                <div key={idx} className="flex flex-col items-center justify-center min-w-fit">
                  <div 
                    ref={(el) => monthRefs.current[month.name] = el}
                    className="text-xs text-white mb-1 px-4 py-1 bg-gray-600 rounded text-center w-full h-6"
                  >
                    {month.name}
                  </div>
                  <div className="flex gap-1.5">
                    {month.dates.map((date) => (
                      <button
                        key={date}
                        onClick={() => {
                          setSelectedDate(date);
                          setSelectedMonth(month.name);
                        }}
                        style={
                          selectedDate === date && selectedMonth === month.name
                            ? { width: monthWidths[month.name] ? `${monthWidths[month.name]}px` : 'auto' }
                            : {}
                        }
                        className={`px-4 py-1 rounded text-sm transition-colors h-6 ${
                          selectedDate === date && selectedMonth === month.name
                            ? "bg-cyan-700 text-white"
                            : "text-white hover:text-cyan-400"
                        }`}
                      >
                        {date}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Strike Price Scale */}
        <div className="mb-4">
          <div className="text-sm mb-2">STRIKE:</div>
          <div className="relative h-12 bg-gray-900/50 rounded">
            <div className="absolute inset-0 flex items-center justify-between px-2">
              {strikes.map((strike, idx) => (
                <div key={idx} className="relative flex flex-col items-center">
                  <div className="h-2 w-px bg-gray-600"></div>
                  {idx % 2 === 0 && <div className="text-[10px] text-white mt-1">{strike}</div>}
                  {strike === 220 && (
                    <div className="absolute -top-8 bg-emerald-500 text-white px-2 py-1 rounded text-xs font-semibold">
                      220C
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Metrics Row - Compact Layout */}
        <div className="flex items-center gap-4 mb-6">
          <button className="text-gray-500 hover:text-gray-300 flex-shrink-0">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex-1 grid grid-cols-5 gap-3">
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">NET COST:</div>
              <div className="text-sm font-semibold text-white">
                {typeof metrics.maxLoss === 'number' ? `-$${metrics.maxLoss.toFixed(2)}` : '-'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">MAX LOSS:</div>
              <div className="text-sm font-semibold text-white">
                {metrics.maxLoss === 'unlimited' ? 'Unlimited' : 
                 typeof metrics.maxLoss === 'number' ? `-$${metrics.maxLoss.toFixed(2)}` : 
                 metrics.maxLoss}
              </div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">MAX PROFIT:</div>
              <div className="text-sm font-semibold text-white">
                {metrics.maxProfit === 'unlimited' ? 'Unlimited' : 
                 typeof metrics.maxProfit === 'number' ? `$${metrics.maxProfit.toFixed(2)}` : 
                 metrics.maxProfit}
              </div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">CHANCE:</div>
              <div className="text-sm font-semibold text-white">
                {metrics.chanceOfProfit ? `${metrics.chanceOfProfit.toFixed(0)}%` : '-'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-gray-400 mb-0.5">BREAKEVEN:</div>
              <div className="text-sm font-semibold text-white">
                {Array.isArray(metrics.breakeven) && metrics.breakeven.length > 0 
                  ? `$${metrics.breakeven[0].toFixed(2)}` 
                  : '-'}
              </div>
            </div>
          </div>
          <button className="text-gray-500 hover:text-gray-300 flex-shrink-0">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Chart / Table Toggle */}
        {layerTab === 'graph' ? (
          <div className="relative h-[400px] bg-[#0d1230] rounded-lg mb-6">
            <svg 
              width="100%" 
              height="400" 
              viewBox="0 0 1000 400" 
              className="w-full" 
              preserveAspectRatio="none"
              onMouseMove={(e) => {
                const svg = e.currentTarget;
                const rect = svg.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Scale to viewBox coordinates
                const scaleXFactor = 1000 / rect.width;
                const scaleYFactor = 400 / rect.height;
                const viewBoxX = x * scaleXFactor;
                const viewBoxY = y * scaleYFactor;
                
                // Chart bounds
                const padding = { top: 20, right: 10, bottom: 60, left: 70 };
                const xMin = 100, xMax = 330, yMin = -5000, yMax = 12000;
                
                // Check if inside chart area
                if (viewBoxX >= padding.left && viewBoxX <= 1000 - padding.right && 
                    viewBoxY >= padding.top && viewBoxY <= 400 - padding.bottom) {
                  
                  // Calculate price from X position
                  const price = xMin + ((viewBoxX - padding.left) / (1000 - padding.left - padding.right)) * (xMax - xMin);
                  
                  // Calculate P&L using StrategyEngine
                  const pnl = engine.calculatePnL(price);
                  
                  setTooltip({ 
                    show: true, 
                    x: e.clientX, 
                    y: e.clientY, 
                    viewBoxX: viewBoxX,
                    price: price, 
                    pnl: pnl 
                  });
                } else {
                  setTooltip({ show: false, x: 0, y: 0, viewBoxX: 0, price: 0, pnl: 0 });
                }
              }}
              onMouseLeave={() => setTooltip({ show: false, x: 0, y: 0, viewBoxX: 0, price: 0, pnl: 0 })}
            >
              {/* Gradient definitions */}
              <defs>
                <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="rgba(220, 38, 38, 0)" stopOpacity="0" />
                  <stop offset="100%" stopColor="rgba(220, 38, 38, 0.85)" stopOpacity="1" />
                </linearGradient>
                <linearGradient id="cyanGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="rgba(6, 182, 212, 0.85)" stopOpacity="1" />
                  <stop offset="100%" stopColor="rgba(6, 182, 212, 0)" stopOpacity="0" />
                </linearGradient>
              </defs>

              {(() => {
                // Chart dimensions and padding
                const width = 1000;
                const height = 400;
                const padding = { top: 20, right: 1, bottom: 40, left: 70 };
                
                // Dynamic X-axis range based on strategy type
                let xMin, xMax;
                if (strategyData.strategyId === 'long_put') {
                  xMin = 100;
                  xMax = 275;
                } else if (strategyData.strategyId === 'bull_call_spread' || strategyData.strategyId === 'bear_call_spread') {
                  xMin = 155;
                  xMax = 305;
                } else {
                  // Long Call default
                  xMin = 175;
                  xMax = 325;
                }
                
                // Generate P&L curve using StrategyEngine
                const generatePnL = () => {
                  const points = [];
                  
                  // Use StrategyEngine to generate P&L curve
                  const pnlCurve = engine.generatePnLCurve(xMin, xMax, 2);
                  
                  // Convert to [price, pnl] pairs
                  for (const point of pnlCurve) {
                    points.push([point.price, point.pnl]);
                  }
                  
                  return points;
                };
                
                const data = generatePnL();
                
                // Calculate dynamic Y-axis range from actual P&L data
                const pnlValues = data.map(point => point[1]);
                const minPnL = Math.min(...pnlValues);
                const maxPnL = Math.max(...pnlValues);
                
                // Add 20% padding to Y-range for better visualization
                const pnlRange = maxPnL - minPnL;
                const yPadding = pnlRange * 0.2;
                const yMin = Math.floor((minPnL - yPadding) / 100) * 100; // Round to nearest 100
                const yMax = Math.ceil((maxPnL + yPadding) / 100) * 100;
                const yRange = yMax - yMin;
                
                const xRange = xMax - xMin;
                
                // Scale functions
                const scaleX = (price) => {
                  return padding.left + ((price - xMin) / xRange) * (width - padding.left - padding.right);
                };
                
                const scaleY = (pnl) => {
                  return height - padding.bottom - ((pnl - yMin) / yRange) * (height - padding.top - padding.bottom);
                };
                
                const zeroY = scaleY(0);
                
                // Split data into loss and profit segments
                let lossPoints = [];
                let profitPoints = [];
                let intersectionPoint = null;
                
                for (let i = 0; i < data.length - 1; i++) {
                  if ((data[i][1] <= 0 && data[i + 1][1] > 0) || (data[i][1] > 0 && data[i + 1][1] <= 0)) {
                    const x1 = data[i][0], y1 = data[i][1];
                    const x2 = data[i + 1][0], y2 = data[i + 1][1];
                    const t = -y1 / (y2 - y1);
                    const xIntersect = x1 + t * (x2 - x1);
                    intersectionPoint = [xIntersect, 0];
                    lossPoints = data.slice(0, i + 1);
                    lossPoints.push(intersectionPoint);
                    profitPoints = [intersectionPoint, ...data.slice(i + 1)];
                    break;
                  }
                }
                
                if (!intersectionPoint) {
                  if (data[0][1] <= 0) lossPoints = data;
                  else profitPoints = data;
                }
                
                // Build paths
                const lossPath = lossPoints.map((point, i) => {
                  const x = scaleX(point[0]);
                  const y = scaleY(point[1]);
                  return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                }).join(' ');
                
                const profitPath = profitPoints.map((point, i) => {
                  const x = scaleX(point[0]);
                  const y = scaleY(point[1]);
                  return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
                }).join(' ');
                
                // Y-axis labels: dynamic based on yMin/yMax
                const yLabelCount = 6;
                const yStep = Math.ceil(yRange / (yLabelCount - 1) / 100) * 100; // Round to nearest 100
                const yLabels = [];
                for (let i = 0; i < yLabelCount; i++) {
                  yLabels.push(yMin + (i * yStep));
                }
                
                // X-axis labels: dynamic based on xMin/xMax
                const xLabelCount = 8;
                const xStep = Math.ceil(xRange / (xLabelCount - 1) / 5) * 5; // Round to nearest 5
                const xLabels = [];
                for (let i = 0; i < xLabelCount; i++) {
                  xLabels.push(Math.round(xMin + (i * xStep)));
                }
                
                return (
                  <>
                    {/* Y-axis grid lines and labels */}
                    {yLabels.map((value, i) => {
                      const y = scaleY(value);
                      return (
                        <g key={`y-${i}`}>
                          <line
                            x1={padding.left}
                            y1={y}
                            x2={width - padding.right}
                            y2={y}
                            stroke="rgba(255, 255, 255, 0.12)"
                            strokeWidth="1"
                          />
                          <line
                            x1={padding.left - 5}
                            y1={y}
                            x2={padding.left}
                            y2={y}
                            stroke="rgba(255, 255, 255, 0.7)"
                            strokeWidth="2"
                          />
                          <text
                            x={padding.left - 10}
                            y={y + 4}
                            textAnchor="end"
                            fill="rgba(255, 255, 255, 0.9)"
                            fontSize="12"
                            fontWeight="700"
                          >
                            ${value >= 0 ? value.toLocaleString() : value.toLocaleString()}
                          </text>
                        </g>
                      );
                    })}
                    
                    {/* Zero line */}
                    <line
                      x1={padding.left}
                      y1={zeroY}
                      x2={width - padding.right}
                      y2={zeroY}
                      stroke="rgba(255, 255, 255, 0.3)"
                      strokeWidth="1.5"
                    />
                    
                    {/* Current price line (white dashed) */}
                    <line
                      x1={scaleX(currentPrice)}
                      y1={padding.top}
                      x2={scaleX(currentPrice)}
                      y2={height - padding.bottom}
                      stroke="rgba(255, 255, 255, 0.5)"
                      strokeWidth="1.5"
                      strokeDasharray="4 4"
                    />
                    
                    {/* Breakeven line (cyan) - Only show if breakeven exists */}
                    {Array.isArray(metrics.breakeven) && metrics.breakeven.length > 0 && (
                      <>
                        <line
                          x1={scaleX(metrics.breakeven[0])}
                          y1={padding.top}
                          x2={scaleX(metrics.breakeven[0])}
                          y2={height - padding.bottom}
                          stroke="rgba(6, 182, 212, 0.6)"
                          strokeWidth="1.5"
                        />
                        <text
                          x={scaleX(metrics.breakeven[0])}
                          y={padding.top - 5}
                          textAnchor="middle"
                          fill="#06b6d4"
                          fontSize="12"
                          fontWeight="600"
                        >
                          ${metrics.breakeven[0].toFixed(2)}
                        </text>
                      </>
                    )}
                    
                    {/* Loss line (red) and fill */}
                    {lossPath && lossPoints.length > 0 && (
                      <>
                        <path
                          d={lossPath}
                          fill="none"
                          stroke="#dc2626"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        <path
                          d={`${lossPath} L ${scaleX(lossPoints[lossPoints.length - 1][0])} ${zeroY} L ${scaleX(lossPoints[0][0])} ${zeroY} Z`}
                          fill="url(#redGradient)"
                        />
                      </>
                    )}
                    
                    {/* Profit line (cyan) and fill */}
                    {profitPath && profitPoints.length > 0 && (
                      <>
                        <path
                          d={profitPath}
                          fill="none"
                          stroke="#06b6d4"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        <path
                          d={`${profitPath} L ${scaleX(profitPoints[profitPoints.length - 1][0])} ${zeroY} L ${scaleX(profitPoints[0][0])} ${zeroY} Z`}
                          fill="url(#cyanGradient)"
                        />
                      </>
                    )}
                    
                    {/* Chart frame (axes) */}
                    <line
                      x1={padding.left}
                      y1={height - padding.bottom}
                      x2={width - padding.right}
                      y2={height - padding.bottom}
                      stroke="rgba(255, 255, 255, 0.25)"
                      strokeWidth="2"
                    />
                    <line
                      x1={padding.left}
                      y1={padding.top}
                      x2={padding.left}
                      y2={height - padding.bottom}
                      stroke="rgba(255, 255, 255, 0.25)"
                      strokeWidth="2"
                    />
                    
                    {/* X-axis labels and ticks */}
                    {xLabels.map((value, i) => {
                      const x = scaleX(value);
                      return (
                        <g key={`x-${i}`}>
                          <line
                            x1={x}
                            y1={height - padding.bottom}
                            x2={x}
                            y2={height - padding.bottom + 5}
                            stroke="rgba(255, 255, 255, 0.7)"
                            strokeWidth="2"
                          />
                          <text
                            x={x}
                            y={height - padding.bottom + 20}
                            textAnchor="middle"
                            fill="rgba(255, 255, 255, 0.9)"
                            fontSize="12"
                            fontWeight="700"
                          >
                            ${value}
                          </text>
                        </g>
                      );
                    })}
                    
                    {/* Mouse tracking vertical line */}
                    {tooltip.show && (
                      <>
                        <line
                          x1={tooltip.viewBoxX}
                          y1={padding.top}
                          x2={tooltip.viewBoxX}
                          y2={height - padding.bottom}
                          stroke="rgba(255, 255, 255, 0.5)"
                          strokeWidth="1.5"
                        />
                        
                        {/* Price label at top */}
                        <text
                          x={tooltip.viewBoxX}
                          y={padding.top - 5}
                          textAnchor="middle"
                          fill="white"
                          fontSize="12"
                          fontWeight="700"
                          className="pointer-events-none"
                        >
                          ${tooltip.price.toFixed(2)}
                        </text>
                        
                        {/* P&L dot on curve */}
                        <circle
                          cx={tooltip.viewBoxX}
                          cy={(() => {
                            const yPos = height - padding.bottom - ((tooltip.pnl - yMin) / yRange) * (height - padding.top - padding.bottom);
                            return yPos;
                          })()}
                          r="5"
                          fill={tooltip.pnl >= 0 ? "#06b6d4" : "#dc2626"}
                          stroke="white"
                          strokeWidth="2"
                        />
                      </>
                    )}
                  </>
                );
              })()}
            </svg>
            
            {/* Tooltip for P&L following the curve */}
            {tooltip.show && (
              <div
                className="absolute z-50 pointer-events-none"
                style={{
                  left: `${((tooltip.viewBoxX) / 1000) * 100}%`,
                  top: (() => {
                    const padding = { top: 20, right: 1, bottom: 40, left: 70 };
                    const yMin = -5000, yMax = 12000, yRange = yMax - yMin;
                    const height = 400;
                    const yPos = height - padding.bottom - ((tooltip.pnl - yMin) / yRange) * (height - padding.top - padding.bottom);
                    return `${(yPos / 400) * 100}%`;
                  })(),
                  transform: 'translate(10px, -50%)',
                }}
              >
                <div className={`rounded-lg px-2 py-1 shadow-xl ${tooltip.pnl >= 0 ? 'bg-cyan-600' : 'bg-red-600'}`}>
                  <div className="text-white text-xs font-bold whitespace-nowrap">
                    {tooltip.pnl >= 0 ? '+' : ''}${tooltip.pnl.toFixed(0)}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : layerTab === 'table' ? (
          <OptionsTable 
            rangeValue={rangeValue}
            ivValue={ivValue}
            currentPrice={currentPrice}
            strike={220}
            premium={37.075}
            displayMode={displayMode}
          />
        ) : (
          <div className="text-center text-gray-400 py-8">
            {layerTab === 'pnl_dollar' && 'P&L Dollar View (Coming Soon)'}
            {layerTab === 'pnl_percent' && 'P&L Percent View (Coming Soon)'}
            {layerTab === 'contract_value' && 'Contract Value View (Coming Soon)'}
            {layerTab === 'max_risk' && 'Max Risk View (Coming Soon)'}
          </div>
        )}

        {/* Expiration Date Slider - Only show for Graph view */}
        {layerTab === 'graph' && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-white font-bold">
                {(() => {
                  const today = new Date();
                  const expDate = new Date(today);
                  // dteValue directly = days from today
                  // dteValue=420 → 420 days from now (expiration)
                  // dteValue=0 → today
                  expDate.setDate(expDate.getDate() + dteValue);
                  const years = (dteValue / 365).toFixed(1);
                  const dayName = expDate.toLocaleDateString('en-US', { weekday: 'short' });
                  const monthName = expDate.toLocaleDateString('en-US', { month: 'short' });
                  const day = expDate.getDate();
                  const daySuffix = day === 1 || day === 21 || day === 31 ? 'st' : day === 2 || day === 22 ? 'nd' : day === 3 || day === 23 ? 'rd' : 'th';
                  const year = expDate.getFullYear();
                  return `${dayName} ${monthName} ${day}${daySuffix} ${year} 11:00pm (${years}y)`;
                })()}
              </span>
              <span className="text-xs text-white font-bold">{dteValue === 420 ? '(At expiration)' : '(Before expiration)'}</span>
            </div>
            <div className="relative">
              <input
                type="range"
                min="0"
                max="420"
                step="1"
                value={dteValue}
                onChange={(e) => setDteValue(parseInt(e.target.value))}
                className="w-full cursor-pointer range-slider-cyan"
                style={{
                  background: `linear-gradient(to right, #374151 0%, #374151 ${(dteValue / 420) * 100}%, #06b6d4 ${(dteValue / 420) * 100}%, #06b6d4 100%)`
                }}
              />
              <div className="flex justify-between mt-1 text-[10px] text-gray-500">
                <span>0 DTE (Today)</span>
                <span>100 DTE</span>
                <span>200 DTE</span>
                <span>300 DTE</span>
                <span>420 DTE (Expiration)</span>
              </div>
            </div>
          </div>
        )}

        {/* Spacer for Table view to match Graph view height */}
        {layerTab === 'table' && (
          <div className="mb-6"></div>
        )}

        {/* Sliders - Show for both Graph and Table views */}
        {(layerTab === 'graph' || layerTab === 'table') && (
          <div className="grid grid-cols-2 gap-8 mb-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-white">RANGE: ±{rangeValue}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={rangeValue}
                onChange={(e) => setRangeValue(parseInt(e.target.value))}
                className="range-slider-cyan w-full cursor-pointer"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-semibold text-white">IMPLIED VOLATILITY: {ivValue}%</span>
                </div>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="0.1"
                value={ivValue}
                onChange={(e) => setIvValue(parseFloat(e.target.value))}
                className="range-slider-cyan w-full cursor-pointer"
              />
            </div>
          </div>
        )}

        {/* Bottom Tabs */}
        <div className="flex gap-1 border-t border-gray-700 pt-2">
          <button 
            onClick={() => setLayerTab('table')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              layerTab === 'table'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            Table
          </button>
          <button 
            onClick={() => setLayerTab('graph')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              layerTab === 'graph'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            Graph
          </button>
          <button 
            onClick={() => setDisplayMode('pnl_dollar')}
            className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
              displayMode === 'pnl_dollar'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            Profit / Loss $
          </button>
          <button 
            onClick={() => setDisplayMode('pnl_percent')}
            className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
              displayMode === 'pnl_percent'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            Profit / Loss %
          </button>
          <button 
            onClick={() => setDisplayMode('contract_value')}
            className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
              displayMode === 'contract_value'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            Contract Value
          </button>
          <button 
            onClick={() => setDisplayMode('max_risk_percent')}
            className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
              displayMode === 'max_risk_percent'
                ? 'bg-cyan-700 text-white'
                : 'bg-transparent border border-gray-600 text-white hover:bg-gray-800'
            }`}
          >
            % of Max Risk
          </button>
          <button className="flex-1 px-4 py-2 bg-transparent border border-gray-600 text-white hover:bg-gray-800 rounded-lg transition-colors">
            More
          </button>
        </div>

        {/* Multiplier indicators */}
        <div className="flex justify-end gap-4 mt-2 text-xs text-gray-500">
          <span>×2</span>
          <span>×3</span>
        </div>
      </div>
    </div>
  );
}

/**
 * OptimizeTab - Strategy recommendations
 */

/**
 * OptimizeTab - AI-suggested strategies with full UI controls
 */
function OptimizeTab({ 
  symbol, setSymbol, price, change, changePercent, isRefreshing, handleRefresh,
  selectedDirection, setSelectedDirection, directionConfig, expirationDates,
  selectedExpiryIndex, setSelectedExpiryIndex, targetPrice, setTargetPrice,
  budget, setBudget, sliderPosition, setSliderPosition, maxReturn, maxChance,
  groupedDates, growthPercent
}) {
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
    <div>
      {/* Ticker Header Bar */}
      <div className="border-b border-slate-700/30 bg-slate-900/40 backdrop-blur-sm">
        <div className="px-8 py-4 flex justify-center">
          <div className="w-[52%] flex items-center justify-center gap-6">
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
              className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg text-white hover:text-white text-sm font-medium transition-all disabled:opacity-50"
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
          <div className="w-[52%] flex flex-col items-center gap-4">
            {/* Target Price */}
            <div className="flex items-center gap-3">
              <label className="text-white text-sm font-medium w-24 text-right">Target Price:</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(parseFloat(e.target.value) || 0)}
                  className="w-24 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white text-sm font-semibold focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                  step="0.01"
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
                    step="100"
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
          <div className="w-[52%] mx-auto flex flex-col items-center">
            {/* Expiration Carousel */}
            <div className="w-[52%] mb-4">
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
            <div className="w-[52%]">
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

      {/* Suggested Strategies */}
      <div className="max-w-7xl mx-auto space-y-6 mt-8">
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
    </div>
  );
}

/**
 * StrategyTab - Strategy library with 69 strategies
 */
function StrategyTab() {
  return <StrategyLibraryPage />;
}

/**
 * FlowTab - Options flow with 6 sub-pages
 */
function FlowTab() {
  const [activeFlowTab, setActiveFlowTab] = useState('Summary');
  
  const flowTabs = [
    'Summary',
    'Live Flow', 
    'Historical Flow',
    'News Flow',
    'Congress Flow',
    'Insider Flow'
  ];

  const flowData = [
    { bullish: { ticker: "SLV", count: 20, amount: "$13.26m" }, bearish: { ticker: "DIA", count: 20, amount: "$6.13m" } },
    { bullish: { ticker: "INTC", count: 37, amount: "$8.86m" }, bearish: { ticker: "TSLA", count: 93, amount: "$447.47m" } },
    { bullish: { ticker: "ORCL", count: 27, amount: "$10.49m" }, bearish: { ticker: "ANET", count: 29, amount: "$5.73m" } },
    { bullish: { ticker: "XSP", count: 16, amount: "$1.63m" }, bearish: { ticker: "TSLL", count: 43, amount: "$5.93m" } },
    { bullish: { ticker: "META", count: 20, amount: "$15.67m" }, bearish: { ticker: "MRNA", count: 10, amount: "$39.53m" } },
    { bullish: { ticker: "AMD", count: 20, amount: "$13.54m" }, bearish: { ticker: "IBM", count: 32, amount: "$5.50m" } },
    { bullish: { ticker: "SOXL", count: 16, amount: "$2.41m" }, bearish: { ticker: "XLE", count: 8, amount: "$7.77m" } },
    { bullish: { ticker: "LULU", count: 8, amount: "$204.67m" }, bearish: { ticker: "LVS", count: 9, amount: "$1.76m" } },
    { bullish: { ticker: "UUUU", count: 39, amount: "$7.84m" }, bearish: { ticker: "VRT", count: 20, amount: "$7.40m" } },
    { bullish: { ticker: "TXN", count: 17, amount: "$3.15m" }, bearish: { ticker: "TMUS", count: 7, amount: "$3.90m" } },
    { bullish: { ticker: "NOK", count: 11, amount: "$356k" }, bearish: { ticker: "AVDL", count: 7, amount: "$2.98m" } },
    { bullish: { ticker: "GOOGL", count: 14, amount: "$4.26m" }, bearish: { ticker: "GME", count: 24, amount: "$3.10m" } },
    { bullish: { ticker: "HD", count: 10, amount: "$2.89m" }, bearish: { ticker: "F", count: 18, amount: "$609k" } },
    { bullish: { ticker: "OKLO", count: 17, amount: "$7.34m" }, bearish: { ticker: "RIG", count: 13, amount: "$945k" } },
    { bullish: { ticker: "AMAT", count: 8, amount: "$1.10m" }, bearish: { ticker: "IWM", count: 72, amount: "$16.48m" } },
    { bullish: { ticker: "GE", count: 7, amount: "$679k" }, bearish: { ticker: "SPY", count: 329, amount: "$82.74m" } },
    { bullish: { ticker: "CVNA", count: 6, amount: "$6.95m" }, bearish: { ticker: "TSM", count: 5, amount: "$18.64m" } },
    { bullish: { ticker: "MSFT", count: 22, amount: "$11.13m" }, bearish: { ticker: "SBUX", count: 7, amount: "$1.07m" } },
    { bullish: { ticker: "AAPL", count: 25, amount: "$7.46m" }, bearish: { ticker: "USO", count: 14, amount: "$2.13m" } },
    { bullish: { ticker: "GLD", count: 46, amount: "$34.04m" }, bearish: { ticker: "SOFI", count: 16, amount: "$2.15m" } },
    { bullish: { ticker: "ADBE", count: 6, amount: "$20.75m" }, bearish: { ticker: "DECK", count: 21, amount: "$2.48m" } },
    { bullish: { ticker: "SPOT", count: 5, amount: "$4.32m" }, bearish: { ticker: "APLD", count: 5, amount: "$1.13m" } },
    { bullish: { ticker: "SMH", count: 5, amount: "$43.26m" }, bearish: { ticker: "DAL", count: 6, amount: "$365k" } },
    { bullish: { ticker: "OXY", count: 12, amount: "$2.54m" }, bearish: { ticker: "GFI", count: 5, amount: "$449k" } },
    { bullish: { ticker: "PG", count: 9, amount: "$851k" }, bearish: { ticker: "VOO", count: 5, amount: "$443k" } },
    { bullish: { ticker: "MU", count: 11, amount: "$6.58m" }, bearish: { ticker: "/CL", count: 72, amount: "$13.49m" } },
    { bullish: { ticker: "FE", count: 6, amount: "$146k" }, bearish: { ticker: "AA", count: 14, amount: "$2.19m" } },
    { bullish: { ticker: "PLTR", count: 26, amount: "$9.17m" }, bearish: { ticker: "WMT", count: 6, amount: "$654k" } },
    { bullish: { ticker: "PEP", count: 5, amount: "$3.20m" }, bearish: { ticker: "IBIT", count: 9, amount: "$4.51m" } },
    { bullish: { ticker: "MOH", count: 5, amount: "$2.90m" }, bearish: { ticker: "/ES", count: 12, amount: "$3.01m" } },
    { bullish: { ticker: "/LE", count: 34, amount: "$6.98m" }, bearish: { ticker: "GDX", count: 12, amount: "$2.02m" } },
    { bullish: { ticker: "SPX", count: 65, amount: "$253.66m" }, bearish: { ticker: "CNC", count: 5, amount: "$472k" } },
    { bullish: { ticker: "HON", count: 6, amount: "$3.45m" }, bearish: { ticker: "UNH", count: 11, amount: "$33.59m" } },
    { bullish: { ticker: "CRWV", count: 15, amount: "$3.43m" }, bearish: { ticker: "AVGO", count: 8, amount: "$16.24m" } },
    { bullish: { ticker: "COIN", count: 11, amount: "$9.24m" }, bearish: { ticker: "C", count: 4, amount: "$1.26m" } },
    { bullish: { ticker: "CDZI", count: 7, amount: "$132k" }, bearish: { ticker: "SFM", count: 5, amount: "$734k" } },
  ];

  const liveFlowData = [
    { time: "10/23 11:56pm", symbol: "/CL", strategy: "Sell 60 Put", expiration: "Feb 17 '26", premium: "$106k", type: "", isBullish: true },
    { time: "10/23 11:56pm", symbol: "/CL", strategy: "Sell 60 Put", expiration: "Feb 17 '26", premium: "$264k", type: "", isBullish: true },
    { time: "10/23 11:38pm", symbol: "/ZB", strategy: "Buy 116.5 Put To Open", expiration: "Oct 29", premium: "$250k", type: "SPLIT", isBullish: false },
    { time: "10/23 11:33pm", symbol: "MOH", strategy: "Sell 145 Put", expiration: "Jan 21 '28", premium: "$1.65m", type: "", isBullish: true },
    { time: "10/23 11:31pm", symbol: "/ZN", strategy: "Buy 113 Call", expiration: "Nov 21", premium: "$702k", type: "SPLIT", isBullish: true },
    { time: "10/23 11:23pm", symbol: "/SI", strategy: "Sell 41 Call", expiration: "Oct 28", premium: "$750k", type: "", isBullish: false },
    { time: "10/23 11:21pm", symbol: "/ZN", strategy: "Sell 113.5 Put", expiration: "Oct 27", premium: "$139k", type: "SPLIT", isBullish: true },
    { time: "10/23 11:14pm", symbol: "IWM", strategy: "Buy 234 Put", expiration: "Nov 21", premium: "$208k", type: "SWEEP", isBullish: false },
    { time: "10/23 11:14pm", symbol: "QQQ", strategy: "Buy 611 Put", expiration: "Oct 28", premium: "$56k", type: "SWEEP", isBullish: false },
    { time: "10/23 11:14pm", symbol: "QQQ", strategy: "Buy 611 Put", expiration: "Oct 28", premium: "$139k", type: "SWEEP", isBullish: false },
    { time: "10/23 11:14pm", symbol: "SPY", strategy: "Sell 672 Put", expiration: "Oct 28", premium: "$207k", type: "SWEEP", isBullish: true },
    { time: "10/23 11:14pm", symbol: "SPY", strategy: "Sell 673 Call", expiration: "Oct 28", premium: "$197k", type: "SWEEP", isBullish: false },
    { time: "10/23 11:13pm", symbol: "QQQ", strategy: "Buy 611 Call", expiration: "Oct 28", premium: "$432k", type: "SWEEP", isBullish: true },
    { time: "10/23 11:13pm", symbol: "/ZN", strategy: "Buy 112.5 Put", expiration: "Dec 26", premium: "$178k", type: "SPLIT", isBullish: false },
    { time: "10/23 11:12pm", symbol: "IWM", strategy: "Sell 247 Call", expiration: "Oct 27", premium: "$41k", type: "SPLIT", isBullish: false },
    { time: "10/23 11:12pm", symbol: "QQQ", strategy: "Sell 606 Put", expiration: "Oct 27", premium: "$56k", type: "SWEEP", isBullish: true },
    { time: "10/23 11:11pm", symbol: "XSP", strategy: "Sell 686/688 Puts", expiration: "Oct 27", premium: "$103k", type: "SPLIT", isBullish: true },
    { time: "10/23 11:10pm", symbol: "XSP", strategy: "Sell 686/688 Puts", expiration: "Oct 27", premium: "$128k", type: "SPLIT", isBullish: true },
    { time: "10/23 11:10pm", symbol: "SPY", strategy: "Buy 915 Put", expiration: "Dec 17 '27", premium: "$8.31m", type: "BLOCK", isBullish: false },
    { time: "10/23 11:10pm", symbol: "SPY", strategy: "Sell 720 Put", expiration: "Nov 28", premium: "$2.43m", type: "BLOCK", isBullish: true },
    { time: "10/23 11:10pm", symbol: "SPY", strategy: "Sell 700 Put", expiration: "Nov 14", premium: "$5.60m", type: "BLOCK", isBullish: true },
    { time: "10/23 11:10pm", symbol: "SPY", strategy: "Buy 700 Put", expiration: "Oct 31", premium: "$5.96m", type: "BLOCK", isBullish: false },
    { time: "10/23 11:09pm", symbol: "XSP", strategy: "Buy 673/676 Calls", expiration: "Oct 27", premium: "$29k", type: "", isBullish: true },
    { time: "10/23 11:09pm", symbol: "SPX", strategy: "6600/6700 Bull Put Spread", expiration: "Oct 31", premium: "$1.51m", type: "", isBullish: true },
    { time: "10/23 11:09pm", symbol: "SPX", strategy: "Sell 6750/6790/6800/6840 Calls", expiration: "Oct 24 - Oct 27", premium: "$530k", type: "BLOCK", isBullish: false },
    { time: "10/23 11:08pm", symbol: "SMR", strategy: "Sell 40 Call", expiration: "Dec 19", premium: "$355k", type: "", isBullish: false },
    { time: "10/23 11:07pm", symbol: "QQQ", strategy: "Buy 620 Put", expiration: "Oct 24", premium: "$137k", type: "", isBullish: false },
    { time: "10/23 11:07pm", symbol: "IWM", strategy: "Sell 234 Put", expiration: "Nov 21", premium: "$206k", type: "SWEEP", isBullish: true },
    { time: "10/23 11:07pm", symbol: "QQQ", strategy: "Sell 607 Call", expiration: "Oct 24", premium: "$81k", type: "SWEEP", isBullish: false },
    { time: "10/23 11:06pm", symbol: "SPX", strategy: "Sell 6745 Call To Open", expiration: "Nov 10", premium: "$724k", type: "", isBullish: false },
    { time: "10/23 11:05pm", symbol: "SPY", strategy: "Buy 639 Put", expiration: "Nov 21", premium: "$1.36m", type: "", isBullish: false },
    { time: "10/23 11:05pm", symbol: "TLT", strategy: "Buy 90.5 Put", expiration: "Oct 24", premium: "$30k", type: "SWEEP", isBullish: false },
  ];

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a]">
      <div className="flex-1">
        {/* Flow Content */}
        <div className="p-6 max-w-7xl mx-auto h-[calc(100vh-4rem)]">
          {activeFlowTab === 'Summary' && (
            <div className="flex gap-4 h-full">
              {/* Bullish/Bearish Columns */}
              <div className="flex-1 flex flex-col gap-4">
                {/* Flow Sub-Navigation */}
                <div className="flex items-center justify-between gap-6 border-b border-slate-700/30 pb-3">
                  <div className="flex items-center gap-6">
                    {flowTabs.map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveFlowTab(tab)}
                        className={`relative py-2 text-base font-semibold transition-all ${
                          activeFlowTab === tab ? 'text-cyan-400' : 'text-white hover:text-cyan-300'
                        }`}
                      >
                        {tab}
                        {activeFlowTab === tab && (
                          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-500" />
                        )}
                      </button>
                    ))}
                  </div>
                  {/* Market Bias Indicator */}
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600" />
                </div>
                
                {/* Columns */}
                <div className="flex-1 grid grid-cols-2 gap-4 overflow-y-auto pr-2 custom-scrollbar">
                  {/* Bullish Flow Column */}
                  <div>
                    <div className="mb-4 flex items-center gap-2 text-base font-semibold text-white">
                      <TrendingUp className="h-5 w-5 text-cyan-500" />
                      <span>Bullish Flow</span>
                    </div>
                    <div className="space-y-1">
                      {flowData.map((item, index) => (
                        <div
                          key={`bullish-${index}`}
                          className="group relative flex items-center justify-between overflow-hidden rounded-md bg-gradient-to-r from-cyan-600/50 to-transparent px-3 py-1.5 transition-all hover:from-cyan-500/70"
                        >
                          <div className="flex items-center gap-3">
                            <span className="min-w-[60px] text-lg font-bold text-white">
                              {item.bullish.ticker}
                            </span>
                            <span className="text-lg text-white">{item.bullish.count}</span>
                          </div>
                          <span className="text-lg font-semibold text-white">{item.bullish.amount}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Bearish Flow Column */}
                  <div>
                    <div className="mb-4 flex items-center justify-end gap-2 text-base font-semibold text-white">
                      <span>Bearish Flow</span>
                      <TrendingDown className="h-5 w-5 text-orange-500" />
                    </div>
                    <div className="space-y-1">
                      {flowData.map((item, index) => (
                        <div
                          key={`bearish-${index}`}
                          className="group relative flex items-center justify-between overflow-hidden rounded-md bg-gradient-to-l from-orange-600/50 to-transparent px-3 py-1.5 transition-all hover:from-orange-500/70"
                        >
                          <span className="text-lg font-semibold text-white">{item.bearish.amount}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-lg text-white">{item.bearish.count}</span>
                            <span className="min-w-[60px] text-right text-lg font-bold text-white">
                              {item.bearish.ticker}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* FiltersPanel */}
              <div className="w-80 flex-shrink-0 overflow-y-auto custom-scrollbar">
                <FiltersPanel />
              </div>
            </div>
          )}

          {activeFlowTab === 'Live Flow' && (
            <div className="flex gap-4 h-full">
              {/* Live Flow Table */}
              <div className="flex-1 flex flex-col gap-4">
                {/* Flow Sub-Navigation */}
                <div className="flex items-center justify-between gap-6 border-b border-slate-700/30 pb-3">
                  <div className="flex items-center gap-6">
                    {flowTabs.map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveFlowTab(tab)}
                        className={`relative py-2 text-base font-semibold transition-all ${
                          activeFlowTab === tab ? 'text-cyan-400' : 'text-white hover:text-cyan-300'
                        }`}
                      >
                        {tab}
                        {activeFlowTab === tab && (
                          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-500" />
                        )}
                      </button>
                    ))}
                  </div>
                  {/* Market Bias Indicator */}
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600" />
                </div>

                {/* Table */}
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                  <div className="overflow-hidden rounded-lg border border-slate-700/30">
                    {/* Table Header */}
                    <div className="grid grid-cols-[120px_80px_1fr_120px_100px_80px] gap-4 border-b border-slate-700/30 bg-slate-900/40 px-4 py-3 text-sm font-semibold text-white">
                      <div>Time</div>
                      <div>Symbol</div>
                      <div>Strategy</div>
                      <div>Expiration</div>
                      <div>Premium</div>
                      <div>Type</div>
                    </div>

                    {/* Table Body */}
                    <div className="divide-y divide-slate-700/30">
                      {liveFlowData.map((row, index) => (
                        <div
                          key={index}
                          className="grid grid-cols-[120px_80px_1fr_120px_100px_80px] gap-4 px-4 py-2 text-sm transition-colors hover:bg-slate-900/20"
                        >
                          <div className="text-white/60 text-sm">{row.time}</div>
                          <div className={`font-bold text-base ${row.isBullish ? "text-cyan-500" : "text-orange-500"}`}>
                            {row.symbol}
                          </div>
                          <div className="text-white text-sm">{row.strategy}</div>
                          <div className="text-white text-sm">{row.expiration}</div>
                          <div className={`font-semibold text-base ${row.isBullish ? "text-cyan-500" : "text-orange-500"}`}>
                            {row.premium}
                          </div>
                          <div>
                            {row.type && (
                              <span
                                className={`inline-block rounded px-2 py-0.5 text-xs font-bold ${
                                  row.type === "SPLIT"
                                    ? "bg-cyan-500/20 text-cyan-400"
                                    : row.type === "SWEEP"
                                      ? "bg-orange-500/20 text-orange-400"
                                      : "bg-purple-500/20 text-purple-400"
                                }`}
                              >
                                {row.type}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* FiltersPanel */}
              <div className="w-80 flex-shrink-0 overflow-y-auto custom-scrollbar">
                <FiltersPanel />
              </div>
            </div>
          )}

          {activeFlowTab === 'Historical Flow' && (
            <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
              <div className="text-white text-lg mb-2">Historical Flow</div>
              <p className="text-white/60 text-sm">Historical options flow data (coming soon)</p>
            </div>
          )}

          {activeFlowTab === 'News Flow' && (
            <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
              <div className="text-white text-lg mb-2">News Flow</div>
              <p className="text-white/60 text-sm">Market-moving news feed (coming soon)</p>
            </div>
          )}

          {activeFlowTab === 'Congress Flow' && (
            <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
              <div className="text-white text-lg mb-2">Congress Flow</div>
              <p className="text-white/60 text-sm">Congressional trades tracking (coming soon)</p>
            </div>
          )}

          {activeFlowTab === 'Insider Flow' && (
            <div className="text-center py-16 bg-slate-800/20 border border-slate-700/30 rounded-lg">
              <div className="text-white text-lg mb-2">Insider Flow</div>
              <p className="text-white/60 text-sm">Corporate insider trades (coming soon)</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
