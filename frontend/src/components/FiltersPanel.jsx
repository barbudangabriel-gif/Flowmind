import React, { useState } from 'react';
import { TrendingUp, TrendingDown, ArrowRight, ArrowUpRight, Activity } from 'lucide-react';

export function FiltersPanel() {
  const [activeFilterTab, setActiveFilterTab] = useState('current');
  const [premiumValue, setPremiumValue] = useState(50);
  const [expirationValue, setExpirationValue] = useState(50);

  const flowTypeIcons = [
    { icon: TrendingUp, color: 'text-cyan-500', bg: 'bg-cyan-500/20' },
    { icon: TrendingDown, color: 'text-orange-500', bg: 'bg-orange-500/20' },
    { icon: ArrowRight, color: 'text-gray-400', bg: 'bg-gray-500/20' },
    { icon: ArrowUpRight, color: 'text-pink-500', bg: 'bg-pink-500/20' },
    { icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-500/20' },
    { icon: Activity, color: 'text-purple-500', bg: 'bg-purple-500/20' },
  ];

  const toggleButtons = [
    { label: 'Buy Side', active: true },
    { label: 'Sell Side', active: true },
  ];

  const tradeTypes = [
    { label: 'Single', active: true },
    { label: 'Split', active: true },
    { label: 'Sweep', active: true },
    { label: 'Block', active: true },
  ];

  const assetTypes = [
    { label: 'Stocks', active: true },
    { label: 'ETFs', active: true },
  ];

  const marketCaps = [
    { label: 'Small Cap', active: true },
    { label: 'Mid Cap', active: true },
    { label: 'Large Cap', active: true },
  ];

  const optionTypes = [
    { label: 'Calls', active: true },
    { label: 'Puts', active: true },
    { label: 'Spreads', active: true },
  ];

  return (
    <div className="border-l border-slate-700/30 bg-[#0d1117] p-4">
      <h2 className="mb-4 text-base font-semibold text-white">Filters & Alerts</h2>

      {/* Filter Tabs */}
      <div className="mb-6 grid grid-cols-2 gap-2">
        <button
          onClick={() => setActiveFilterTab('current')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            activeFilterTab === 'current'
              ? 'bg-cyan-500 text-white'
              : 'border border-slate-700/30 bg-transparent text-white hover:text-white/80'
          }`}
        >
          Current Filter
        </button>
        <button
          onClick={() => setActiveFilterTab('your')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            activeFilterTab === 'your'
              ? 'bg-cyan-500 text-white'
              : 'border border-slate-700/30 bg-transparent text-white hover:text-white/80'
          }`}
        >
          Your Filters
        </button>
      </div>

      {/* Tickers Input */}
      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-white">Tickers:</label>
        <input
          type="text"
          placeholder="Add or exclude a ticker"
          className="w-full rounded border border-slate-700/30 bg-[#0a0e1a] px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
      </div>

      {/* Minimum Premium Slider */}
      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-white">
          Minimum premium: All premiums
        </label>
        <input
          type="range"
          value={premiumValue}
          onChange={(e) => setPremiumValue(e.target.value)}
          className="w-full h-2 bg-slate-700/30 rounded-lg appearance-none cursor-pointer slider-cyan"
        />
      </div>

      {/* Expiration Slider */}
      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-white">
          Expiration: All expirations
        </label>
        <input
          type="range"
          value={expirationValue}
          onChange={(e) => setExpirationValue(e.target.value)}
          className="w-full h-2 bg-slate-700/30 rounded-lg appearance-none cursor-pointer slider-cyan"
        />
      </div>

      {/* Flow Type Icons */}
      <div className="mb-6 flex gap-2">
        {flowTypeIcons.map((item, index) => {
          const Icon = item.icon;
          return (
            <button
              key={index}
              className={`flex h-10 w-10 items-center justify-center rounded ${item.bg} transition-opacity hover:opacity-80`}
            >
              <Icon className={`h-5 w-5 ${item.color}`} />
            </button>
          );
        })}
      </div>

      {/* Buy/Sell Side */}
      <div className="mb-4 grid grid-cols-2 gap-2">
        {toggleButtons.map((btn) => (
          <button
            key={btn.label}
            className="flex items-center justify-center gap-2 rounded border border-cyan-500/50 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-cyan-500/20"
          >
            <span className="text-cyan-400">✓</span>
            {btn.label}
          </button>
        ))}
      </div>

      {/* Trade Types */}
      <div className="mb-4 grid grid-cols-4 gap-2">
        {tradeTypes.map((type) => (
          <button
            key={type.label}
            className="flex items-center justify-center gap-1 rounded border border-cyan-500/50 bg-cyan-500/10 px-2 py-2 text-xs font-medium text-white transition-colors hover:bg-cyan-500/20"
          >
            <span className="text-cyan-400 text-xs">✓</span>
            {type.label}
          </button>
        ))}
      </div>

      {/* Asset Types */}
      <div className="mb-4 grid grid-cols-2 gap-2">
        {assetTypes.map((type) => (
          <button
            key={type.label}
            className="flex items-center justify-center gap-2 rounded border border-cyan-500/50 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-cyan-500/20"
          >
            <span className="text-cyan-400">✓</span>
            {type.label}
          </button>
        ))}
      </div>

      {/* Market Caps */}
      <div className="mb-4 grid grid-cols-3 gap-2">
        {marketCaps.map((cap) => (
          <button
            key={cap.label}
            className="flex items-center justify-center gap-1 rounded border border-cyan-500/50 bg-cyan-500/10 px-2 py-2 text-xs font-medium text-white transition-colors hover:bg-cyan-500/20"
          >
            <span className="text-cyan-400 text-xs">✓</span>
            {cap.label}
          </button>
        ))}
      </div>

      {/* Option Types */}
      <div className="mb-6 grid grid-cols-3 gap-2">
        {optionTypes.map((type) => (
          <button
            key={type.label}
            className="flex items-center justify-center gap-1 rounded border border-cyan-500/50 bg-cyan-500/10 px-2 py-2 text-xs font-medium text-white transition-colors hover:bg-cyan-500/20"
          >
            <span className="text-cyan-400 text-xs">✓</span>
            {type.label}
          </button>
        ))}
      </div>

      {/* Checkboxes */}
      <div className="mb-6 space-y-3">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 rounded border-cyan-500 bg-transparent checked:bg-cyan-500" />
          <span className="text-sm text-white">Out of the money</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 rounded border-cyan-500 bg-transparent checked:bg-cyan-500" />
          <span className="text-sm text-white">Volume &gt; OI</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 rounded border-cyan-500 bg-transparent checked:bg-cyan-500" />
          <span className="text-sm text-white">Upcoming earnings</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 rounded border-cyan-500 bg-transparent checked:bg-cyan-500" />
          <span className="text-sm text-white">Above ask or below bid</span>
        </label>
      </div>

      {/* Price Filter */}
      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-white">Price was</label>
        <div className="flex gap-2">
          <select className="flex-1 rounded border border-slate-700/30 bg-[#0a0e1a] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500">
            <option>Less than</option>
            <option>Greater than</option>
            <option>Equal to</option>
          </select>
          <div className="flex flex-1 items-center gap-1 rounded border border-slate-700/30 bg-[#0a0e1a] px-3">
            <span className="text-slate-400">$</span>
            <input
              type="number"
              className="w-full bg-transparent border-0 p-0 text-sm text-white focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Chance Filter */}
      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-white">Chance was</label>
        <div className="flex gap-2">
          <select className="flex-1 rounded border border-slate-700/30 bg-[#0a0e1a] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500">
            <option>Less than</option>
            <option>Greater than</option>
            <option>Equal to</option>
          </select>
          <div className="flex flex-1 items-center gap-1 rounded border border-slate-700/30 bg-[#0a0e1a] px-3">
            <input
              type="number"
              className="w-full bg-transparent border-0 p-0 text-sm text-white focus:outline-none"
            />
            <span className="text-slate-400">%</span>
          </div>
        </div>
      </div>

      {/* Help Link */}
      <div className="flex items-center gap-2 text-sm text-white cursor-pointer hover:text-white/80">
        <span className="flex h-5 w-5 items-center justify-center rounded-full border border-cyan-500 text-xs text-cyan-500">?</span>
        <span>Need help? View our flow tutorial</span>
      </div>
    </div>
  );
}
