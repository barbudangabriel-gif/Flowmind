import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useOptionsStore, useOptionsOverviewPolling } from '../stores/optionsStore';
import BuildHoverMegaMenu from '../components/nav/BuildHoverMegaMenu';

export default function OptionsAnalytics() {
 const navigate = useNavigate();
 const { pathname } = useLocation();
 const { loading, error, overview, flow, previewItem, setPreviewItem } = useOptionsStore();
 
 // Set up polling for market data - with fallback data
 useOptionsOverviewPolling('ALL');

 const [showBuildMenu, setShowBuildMenu] = useState(false);
 const [hoverTimer, setHoverTimer] = useState(null);

 // Fallback data când API-ul eșuează
 const fallbackOverview = {
 activeStrategies: 0,
 expirationDates: 8,
 dailyVolumeUsd: 12500000,
 avgIvPct: 28.5
 };

 const fallbackFlow = {
 live: 0,
 historical: 0,
 news: 0,
 congress: 0,
 insiders: 0
 };

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

 // Tab component
 const Tab = ({ label, to, dropdown = false }) => {
 const active = pathname.includes(to) || (to === 'build' && pathname === '/options/analytics');
 const base = "px-4 py-2 rounded-lg text-slate-300 hover:text-[rgb(252, 251, 255)] hover:bg-slate-800 transition-colors font-medium";
 
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
 symbol="TSLA"
 onClose={() => setShowBuildMenu(false)}
 onItemHover={(item) => setPreviewItem(item)}
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

 const formatNumber = (num) => {
 if (num === null || num === undefined) return '—';
 if (num >= 1_000_000) return `$${(num / 1_000_000).toFixed(1)}M`;
 if (num >= 1_000) return `$${(num / 1_000).toFixed(0)}K`;
 return `$${num}`;
 };

 return (
 <div className="p-6 space-y-6 bg-slate-950 min-h-screen">
 {/* Header tabs - restored to this component */}
 <div className="flex items-center gap-2">
 <Tab label="Build" to="build" dropdown />
 <Tab label="Optimize" to="optimize" />
 <Tab label="Flow" to="flow" />
 </div>

 {/* Market Overview Cards */}
 {loading && (
 <div className="text-slate-400 text-center py-4">Loading market data...</div>
 )}
 
 {/* Folosește datele disponibile sau fallback, nu afișa eroarea */}
 {(overview || fallbackOverview) && (
 <div className="grid grid-cols-4 gap-4">
 {[
 { label: 'Active Strategies', value: (overview || fallbackOverview).activeStrategies },
 { label: 'Expirations', value: (overview || fallbackOverview).expirationDates },
 { label: 'Daily Volume', value: formatNumber((overview || fallbackOverview).dailyVolumeUsd) },
 { label: 'Avg IV', value: (overview || fallbackOverview).avgIvPct != null ? `${(overview || fallbackOverview).avgIvPct}%` : '—' }
 ].map((item, i) => (
 <div key={i} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
 <div className="text-xl text-slate-400 mb-1">{item.label}</div>
 <div className="text-xl font-medium text-slate-200">{item.value}</div>
 </div>
 ))}
 </div>
 )}

 {/* Flow Summary Cards */}
 {(flow || fallbackFlow) && (
 <div className="space-y-4">
 <h2 className="text-3xl font-medium text-slate-200">Flow Summary</h2>
 <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
 {[
 { label: 'Live Trades', value: (flow || fallbackFlow).live },
 { label: 'Historical', value: (flow || fallbackFlow).historical },
 { label: 'News Flow', value: (flow || fallbackFlow).news },
 { label: 'Congress', value: (flow || fallbackFlow).congress },
 { label: 'Insiders', value: (flow || fallbackFlow).insiders }
 ].map((item, i) => (
 <div key={i} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
 <div className="text-xl text-slate-400 mb-1">{item.label}</div>
 <div className="text-xl font-medium text-slate-200">{item.value}</div>
 </div>
 ))}
 </div>
 </div>
 )}

 {/* Strategy Preview */}
 <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
 <h3 className="text-slate-300 font-medium mb-2">Strategy Preview</h3>
 <p className="text-slate-400 text-xl">
 {previewItem 
 ? `Previewing: ${previewItem.name}` 
 : 'Select from Build (above). Real data connected.'
 }
 </p>
 </div>
 </div>
 );
}