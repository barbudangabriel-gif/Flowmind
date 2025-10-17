import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BuildHoverMegaMenu from '../components/nav/BuildHoverMegaMenu';
import { SpreadQualityMeter } from '../components/SpreadQualityMeter';
import { StrategyPicker } from '../components/StrategyPicker';
import ExpiryRail from '../components/ExpiryRail';
import StrategyCard from '../components/optimize/StrategyCard';
import { useExpirations } from '../hooks/useExpirations';
import { stanceFromStrategy, strengthFromNetDelta } from '../logic/stanceFromStrategy';
import { STANCE_THEME, intensify } from '../ui/stance';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "";

async function jfetch(url, opts) {
 const r = await fetch(url, opts);
 if (!r.ok) throw new Error(await r.text());
 return r.json();
}

export default function OptimizePage() {
 const navigate = useNavigate();
 const { pathname } = useLocation();
 const [showBuildMenu, setShowBuildMenu] = useState(false);
 const [hoverTimer, setHoverTimer] = useState(null);
 
 const [symbol, setSymbol] = useState('TSLA');

 const handleBuildEnter = () => {
 if (hoverTimer) clearTimeout(hoverTimer);
 setShowBuildMenu(true);
 };

 const handleBuildLeave = () => {
 const timer = setTimeout(() => setShowBuildMenu(false), 300);
 setHoverTimer(timer);
 };

 const handleMenuEnter = () => {
 if (hoverTimer) clearTimeout(hoverTimer);
 };

 const handleMenuLeave = () => {
 const timer = setTimeout(() => setShowBuildMenu(false), 100);
 setHoverTimer(timer);
 };
 const [sentiment, setSentiment] = useState('bullish');
 const [targetPrice, setTargetPrice] = useState('');
 const [budget, setBudget] = useState('');
 const [dte, setDte] = useState(30);
 const [riskBias, setRiskBias] = useState(0);
 
 // SR-3/3 - New state for enhanced features
 const [chanceBias, setChanceBias] = useState(0.5); // 0 = Max Return, 1 = Max Chance
 const [sortMode, setSortMode] = useState("balanced"); // balanced | return | chance
 const [expiry, setExpiry] = useState('');
 const [strategies, setStrategies] = useState([]);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);
 
 // S1-S3 - Strategy Picker state
 const [pickerOpen, setPickerOpen] = useState(false);
 
 // SR-3/3 - Expirations hook
 const { list: expirations } = useExpirations(symbol);
 
 // Sync expiry selection when list loads
 useEffect(() => {
 if (expirations.length && !expiry) setExpiry(expirations[0]);
 }, [expirations, expiry]);
 
 // Patch C - Scoring functions for different sort modes
 const scoreBalanced = (strategy) => {
 const norm = {
 roi_ev: Math.max(0, Math.min(1, (strategy.roi || 0) / 2)),
 chance: Math.max(0, Math.min(1, strategy.chance || 0)),
 liq: Math.max(0, Math.min(1, (strategy.quality || 0) / 100))
 };
 return 0.35 * norm.roi_ev + 0.45 * norm.chance + 0.20 * norm.liq;
 };

 const scoreReturn = (strategy) => {
 const norm = {
 roi_ev: Math.max(0, Math.min(1, (strategy.roi || 0) / 2)),
 chance: Math.max(0, Math.min(1, strategy.chance || 0)),
 liq: Math.max(0, Math.min(1, (strategy.quality || 0) / 100))
 };
 return 0.70 * norm.roi_ev + 0.20 * norm.chance + 0.10 * norm.liq;
 };

 const scoreChance = (strategy) => {
 const norm = {
 roi_ev: Math.max(0, Math.min(1, (strategy.roi || 0) / 2)),
 chance: Math.max(0, Math.min(1, strategy.chance || 0)),
 liq: Math.max(0, Math.min(1, (strategy.quality || 0) / 100))
 };
 return 0.70 * norm.chance + 0.20 * norm.roi_ev + 0.10 * norm.liq;
 };

 const sorters = {
 balanced: scoreBalanced,
 return: scoreReturn,
 chance: scoreChance,
 };
 
 // SR-3/3 - Ranked strategies with dynamic scoring
 const rankedStrategies = useMemo(() => {
 return strategies
 .map(s => ({ ...s, score: sorters[sortMode](s) }))
 .sort((a, b) => b.score - a.score);
 }, [strategies, sortMode]);
 
 // SR-3/3 - Console control for expiry
 useEffect(() => {
 window.OZ = window.OZ || {};
 window.OZ.expiry = {
 get list() { return expirations; },
 get i() { return Math.max(0, expirations.indexOf(expiry)); },
 get value() { return expiry; },
 select: (i) => setExpiry(expirations[Math.max(0, Math.min(expirations.length - 1, i))]),
 next: () => setExpiry(expirations[Math.min(expirations.length - 1, window.OZ.expiry.i + 1)]),
 prev: () => setExpiry(expirations[Math.max(0, window.OZ.expiry.i - 1)]),
 to: (iso) => {
 const found = expirations.indexOf(iso.slice(0, 10));
 if (found >= 0) setExpiry(expirations[found]);
 else console.warn("Expiry not found in list:", iso);
 },
 };
 
 // Debug console
 window.OZ.debug = {
 get chanceBias() { return chanceBias; },
 set chanceBias(v) { setChanceBias(Math.max(0, Math.min(1, v))); },
 get sortMode() { return sortMode; },
 set sortMode(v) { setSortMode(['balanced', 'return', 'chance'].includes(v) ? v : 'balanced'); },
 get strategies() { return rankedStrategies; },
 rescore: () => console.table(rankedStrategies.map(s => ({ 
 id: s.id, 
 score: (s.score * 100).toFixed(1) + '%',
 roi: ((s.roi || 0) * 100).toFixed(1) + '%',
 chance: ((s.chance || 0) * 100).toFixed(1) + '%'
 })))
 };
 }, [expirations, expiry, setExpiry, chanceBias, sortMode, rankedStrategies]);

 const handleOptimize = async () => {
 setLoading(true);
 setError(null);
 
 try {
 const params = new URLSearchParams({
 symbol,
 sentiment,
 dte: dte.toString(),
 risk_bias: riskBias.toString(),
 });
 
 if (targetPrice) params.set('target_price', targetPrice);
 if (budget) params.set('budget', budget);
 
 const response = await jfetch(`${API}/api/optimize/suggest?${params}`);
 setStrategies(response.strategies || []);
 } catch (e) {
 setError(e.message || 'Failed to fetch strategies');
 } finally {
 setLoading(false);
 }
 };
 
 // SR-3/3 - Handler for opening Builder
 const handleOpenBuilder = (builderUrl) => {
 window.open(builderUrl, '_blank');
 };

 // Header Tab component for persistent navigation
 const Tab = ({ label, to, dropdown = false }) => {
 let active = false;
 
 if (to === 'build' && pathname === '/options/analytics') active = true;
 else if (to === 'optimize' && pathname === '/optimize') active = true;
 else if (to === 'flow' && pathname === '/flow') active = true;
 
 const base = 'px-3 py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition-colors text-slate-200';
 
 // Special handling for Build tab with dropdown menu
 if (to === 'build' && dropdown) {
 return (
 <div className="relative">
 <button
 onClick={() => navigate('/options/analytics')}
 onMouseEnter={handleBuildEnter}
 onMouseLeave={handleBuildLeave}
 className={`${base} ${active ? 'bg-slate-800' : ''}`}
 title={label}
 >
 {label} ▾
 </button>
 
 {showBuildMenu && (
 <div 
 onMouseEnter={handleMenuEnter}
 onMouseLeave={handleMenuLeave}
 >
 <BuildHoverMegaMenu
 symbol={symbol}
 onClose={() => setShowBuildMenu(false)}
 onItemHover={() => {}} // No preview on Optimize page
 />
 </div>
 )}
 </div>
 );
 }
 
 return (
 <button
 onClick={() => {
 if (to === 'build') navigate('/options/analytics');
 else if (to === 'optimize') navigate('/optimize');
 else if (to === 'flow') navigate('/flow');
 }}
 className={`${base} ${active ? 'bg-slate-800' : ''}`}
 title={label}
 >
 {label}{dropdown ? ' ▾' : ''}
 </button>
 );
 };

 return (
 <div className="min-h-screen bg-slate-950">
 {/* Persistent Options Header */}
 <div className="bg-slate-950 border-b border-slate-800 px-6 py-4">
 <div className="max-w-7xl mx-auto">
 <div className="flex items-center gap-2">
 <Tab label="Build" to="build" dropdown />
 <Tab label="Optimize" to="optimize" />
 <Tab label="Flow" to="flow" />
 </div>
 </div>
 </div>
 
 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
 <div className="space-y-6">
 {/* Header */}
 <div>
 <h1 className="text-3xl font-bold text-slate-100">Options Optimizer</h1>
 <p className="text-slate-400 mt-1">Find the best options strategies for your market view</p>
 </div>

 {/* Controls */}
 <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Symbol</label>
 <input
 type="text"
 value={symbol}
 onChange={(e) => setSymbol(e.target.value.toUpperCase())}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 placeholder="TSLA"
 />
 </div>
 
 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Sentiment</label>
 <select
 value={sentiment}
 onChange={(e) => setSentiment(e.target.value)}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 >
 <option value="bullish">Bullish</option>
 <option value="bearish">Bearish</option>
 <option value="neutral">Neutral</option>
 </select>
 </div>

 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Target Price</label>
 <input
 type="number"
 value={targetPrice}
 onChange={(e) => setTargetPrice(e.target.value)}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 placeholder="Optional"
 />
 </div>

 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Budget ($)</label>
 <input
 type="number"
 value={budget}
 onChange={(e) => setBudget(e.target.value)}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 placeholder="Optional"
 />
 </div>

 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Days to Expiration</label>
 <input
 type="number"
 value={dte}
 onChange={(e) => setDte(Number(e.target.value))}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 min="1"
 />
 </div>

 <div>
 <label className="block text-sm font-medium text-slate-300 mb-1">Risk Bias</label>
 <select
 value={riskBias}
 onChange={(e) => setRiskBias(Number(e.target.value))}
 className="w-full px-3 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
 >
 <option value={-2}>Very Conservative</option>
 <option value={-1}>Conservative</option>
 <option value={0}>Balanced</option>
 <option value={1}>Aggressive</option>
 <option value={2}>Very Aggressive</option>
 </select>
 </div>
 </div>
 
 {/* Patch C - Max Return / Max Chance Buttons */}
 <div className="mt-6 border-t pt-4">
 <div className="flex items-center justify-between mb-2">
 <div className="text-sm text-slate-600">Sort Priority:</div>
 <div className="flex items-center gap-2">
 <button 
 className={`px-3 py-1.5 rounded text-sm transition-colors ${
 sortMode === 'return' 
 ? 'bg-emerald-800 text-emerald-200' 
 : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
 }`}
 onClick={() => setSortMode('return')}
 >
 Max Return
 </button>
 <button 
 className={`px-3 py-1.5 rounded text-sm transition-colors ${
 sortMode === 'chance' 
 ? 'bg-emerald-800 text-emerald-200' 
 : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
 }`}
 onClick={() => setSortMode('chance')}
 >
 Max Chance
 </button>
 <button 
 className={`px-3 py-1.5 rounded text-sm transition-colors ${
 sortMode === 'balanced' 
 ? 'bg-emerald-800 text-emerald-200' 
 : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
 }`}
 onClick={() => setSortMode('balanced')}
 >
 Balanced
 </button>
 </div>
 </div>
 <div className="text-xs text-slate-500">
 {sortMode === 'return' && 'Prioritizing maximum profit potential (70% return, 20% chance, 10% liquidity)'}
 {sortMode === 'chance' && 'Prioritizing probability of profit (70% chance, 20% return, 10% liquidity)'}
 {sortMode === 'balanced' && 'Balanced approach (35% return, 45% chance, 20% liquidity)'}
 </div>
 </div>

 {/* SR-3/3 - Return vs Chance Slider */}
 <div className="mt-6 border-t pt-4">
 <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
 <span>← Max Return</span>
 <span className="font-medium text-slate-600">
 Return {Math.round((1 - chanceBias) * 80)}% • Chance {Math.round(chanceBias * 80)}% • Liquidity 20%
 </span>
 <span>Max Chance →</span>
 </div>
 <input
 type="range" 
 min={0} 
 max={100} 
 value={Math.round(chanceBias * 100)}
 onChange={(e) => {
 const v = Number(e.target.value) / 100;
 setChanceBias(v);
 console.log('[Optimize] chanceBias=', v.toFixed(2));
 }}
 className="w-full accent-sky-400"
 />
 </div>

 {/* SR-3/3 - Expiry Rail */}
 <div className="mt-6 border-t pt-4">
 <ExpiryRail 
 expirations={expirations} 
 value={expiry} 
 onChange={setExpiry} 
 />
 </div>

 <div className="mt-4">
 <div className="flex gap-2">
 <button
 onClick={handleOptimize}
 disabled={loading}
 className="flex-1 bg-slate-700 text-slate-200 py-2 px-4 rounded-lg hover:bg-slate-600 disabled:opacity-50 transition-colors"
 >
 {loading ? 'Optimizing...' : 'Find Strategies'}
 </button>
 {/* S1-S3 - Strategy Catalog Button */}
 <button 
 onClick={() => setPickerOpen(true)} 
 className="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
 >
 Build…
 </button>
 </div>
 </div>
 </div>

 {/* Error */}
 {error && (
 <div className="bg-rose-900/20 border border-rose-800 rounded-2xl p-4">
 <div className="text-rose-400">{error}</div>
 </div>
 )}

 {/* Results */}
 {rankedStrategies.length > 0 && (
 <div>
 <div className="flex items-center justify-between mb-4">
 <h2 className="text-xl font-semibold text-slate-100">Recommended Strategies</h2>
 <div className="text-sm text-slate-500">
 Sorted by dynamic scoring • {rankedStrategies.length} strategies
 </div>
 </div>
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
 {rankedStrategies.map((strategy, index) => (
 <StrategyCard 
 key={index} 
 strategy={{
 ...strategy,
 name: strategy.label || strategy.id,
 stance: stanceFromStrategy(strategy.id, strategy.legs || []).stance,
 score_ev: strategy.roi || 0,
 sqm: strategy.quality,
 brief: strategy.id
 }}
 onOpenBuilder={() => handleOpenBuilder(strategy.open_in_builder)}
 />
 ))}
 </div>
 </div>
 )}

 {/* Empty State */}
 {!loading && !error && strategies.length === 0 && (
 <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-8">
 <div className="text-center text-slate-400">
 Click "Find Strategies" to get optimized options strategies for your market view
 </div>
 </div>
 )}
 </div>

 {/* S1-S3 - Strategy Picker Modal */}
 <StrategyPicker 
 open={pickerOpen} 
 onClose={() => setPickerOpen(false)} 
 symbol={symbol} 
 expiry={null} 
 chain={null}
 onDeepLink={(href) => { 
 setPickerOpen(false); 
 window.location.href = href; 
 }} 
 />
 </div>
 </div>
 );
}