import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import BuildHoverMegaMenu from '../components/nav/BuildHoverMegaMenu';
import FlowFilters from '../components/FlowFilters';
import FlowSummary from '../components/FlowSummary';
import FlowTable from '../components/FlowTable';
import LiveFlow from './Flow/LiveFlow';
import LiveLitTradesFeed from './LiveLitTradesFeed';
import LiveOffLitTradesFeed from './LiveOffLitTradesFeed';
import { getFlowHistorical, getFlowNews, getFlowCongress, getFlowInsiders } from '../api/flow';

async function fetchJSON(url, {timeoutMs=3200, signal} = {}) {
 const t = new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), timeoutMs));
 const r = await Promise.race([fetch(url, {signal}), t]);
 if (!r.ok) throw new Error(`HTTP ${r.status}`);
 return r.json();
}

export default function FlowPage() {
 const { pathname, search } = useLocation();
 const navigate = useNavigate();
 const [showBuildMenu, setShowBuildMenu] = useState(false);
 const [hoverTimer, setHoverTimer] = useState(null);

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
 symbol="TSLA"
 onClose={() => setShowBuildMenu(false)}
 onItemHover={() => {}} // No preview on Flow page
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
 
 // Derive current tab from route
 const getCurrentTab = () => {
 if (pathname.includes('/live')) return 'LIVE';
 if (pathname.includes('/hist')) return 'HIST';
 if (pathname.includes('/lit-trades')) return 'LIT_TRADES';
 if (pathname.includes('/dark-pool')) return 'DARK_POOL';
 if (pathname.includes('/news')) return 'NEWS';
 if (pathname.includes('/congress')) return 'CONGRESS';
 if (pathname.includes('/insiders')) return 'INSIDERS';
 return 'SUMMARY';
 };
 
 const currentTab = getCurrentTab();
 
 const handleTabChange = (tab) => {
 const routes = {
 'SUMMARY': '/flow',
 'LIVE': '/flow/live',
 'HIST': '/flow/hist',
 'LIT_TRADES': '/flow/lit-trades',
 'DARK_POOL': '/flow/dark-pool',
 'NEWS': '/flow/news',
 'CONGRESS': '/flow/congress',
 'INSIDERS': '/flow/insiders'
 };
 navigate(routes[tab] + search);
 };
 
 const [summary, setSummary] = useState(null);
 const [mode, setMode] = useState('UNKNOWN');
 const [loading, setLoading] = useState(true);
 const [pageReady, setPageReady] = useState(false);
 const [error, setError] = useState(null);
 const [data, setData] = useState(null);
 const [filters, setFilters] = useState({
 tickers: [],
 side: [], 
 kinds: [],
 minPremium: 25000
 });

 const reqIdRef = useRef(0);
 const readyRef = useRef(false);
 const rafRef = useRef(undefined);
 const timeoutRef = useRef(undefined);

 // idempotent: marchează UI ready o singură dată
 const ensureReady = useCallback(() => {
 if (!readyRef.current) {
 readyRef.current = true;
 setPageReady(true);
 setLoading(false);
 } else {
 setLoading(false);
 }
 }, []);

 // HARD GATE — rulează chiar dacă fetch/abort nu se declanșează
 useLayoutEffect(() => {
 // console.debug('[Flow] watchdog mounted');

 // 2 cadre RAF ca să garantăm commitul, apoi forțăm pageReady
 const raf1 = requestAnimationFrame(() => {
 const raf2 = requestAnimationFrame(() => ensureReady());
 rafRef.current = raf2;
 });
 rafRef.current = raf1;

 // backstop după 1800ms (în caz că RAF nu ajunge)
 const t = window.setTimeout(() => ensureReady(), 1800);
 timeoutRef.current = t;

 return () => {
 if (rafRef.current !== undefined) cancelAnimationFrame(rafRef.current);
 if (timeoutRef.current !== undefined) clearTimeout(timeoutRef.current);
 };
 }, [ensureReady]);

 const load = async () => {
 let alive = true;
 const ctrl = new AbortController();
 const myReqId = ++reqIdRef.current;

 try {
 setLoading(true);
 setError(null);
 
 let result;
 
 if (currentTab === 'SUMMARY') {
 try {
 const j = await fetchJSON('/api/flow/summary?limit=24&minPremium=' + filters.minPremium, { 
 timeoutMs: 3200, 
 signal: ctrl.signal 
 });
 if (!alive || myReqId !== reqIdRef.current) return;
 
 // Transform API structure to expected format
 if (j?.items && Array.isArray(j.items)) {
 const bullish = j.items.filter(item => (item.net_premium || 0) > 0);
 const bearish = j.items.filter(item => (item.net_premium || 0) <= 0);
 result = { bullish, bearish, mode: j.mode };
 setMode(j.mode || 'DEMO');
 }
 } catch (e) {
 if (!alive) return;
 console.warn('Flow summary fallback DEMO:', e?.message || e);
 // fallback DEMO
 result = {
 bullish: [
 { symbol: 'AAPL', trades: 3, net_premium: 85000, sweeps_pct: 0.35 },
 { symbol: 'TSLA', trades: 4, net_premium: 88000, sweeps_pct: 0.45 },
 { symbol: 'NVDA', trades: 2, net_premium: 91000, sweeps_pct: 0.55 },
 { symbol: 'QQQ', trades: 5, net_premium: 94000, sweeps_pct: 0.35 },
 { symbol: 'SPY', trades: 1, net_premium: 97000, sweeps_pct: 0.45 }
 ],
 bearish: [],
 mode: 'DEMO' 
 };
 setMode('DEMO');
 setError(e instanceof Error ? e : new Error(String(e)));
 }
 }
 
 if (currentTab === 'LIVE') {
 result = { items: [], mode: 'DEMO' };
 }
 
 if (currentTab === 'HIST') {
 result = await getFlowHistorical({ symbol: 'TSLA', days: 7 });
 }
 
 if (currentTab === 'NEWS') {
 result = await getFlowNews(filters.tickers);
 }
 
 if (currentTab === 'CONGRESS') {
 result = await getFlowCongress(filters.tickers);
 }
 
 if (currentTab === 'INSIDERS') {
 result = await getFlowInsiders(filters.tickers);
 }
 
 if (alive && myReqId === reqIdRef.current) {
 setData(result);
 }
 
 // UI devine ready și pe succes
 ensureReady();
 } catch (e) {
 if (alive) {
 console.error('Flow API error:', e);
 setError(e.message || 'Load failed');
 
 if (currentTab === 'SUMMARY') {
 setData({ 
 bullish: [
 { symbol: 'AAPL', trades: 3, net_premium: 85000, sweeps_pct: 0.35 },
 { symbol: 'TSLA', trades: 4, net_premium: 88000, sweeps_pct: 0.45 }
 ], 
 bearish: [], 
 mode: 'DEMO' 
 });
 setMode('DEMO');
 }
 }
 // UI devine ready chiar și pe eșec
 ensureReady();
 }
 
 return () => { alive = false; ctrl.abort(); };
 };

 useEffect(() => {
 const cleanup = async () => {
 await load();
 };
 cleanup();
 }, [currentTab]);

 const handleFiltersChange = (newFilters) => {
 setFilters(newFilters);
 };

 const handleApplyFilters = () => {
 load();
 };

 return (
 <div className="min-h-screen bg-slate-950" data-testid="flow-page">
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
 {/* Header with Mode Badge */}
 <div className="flex items-center justify-between">
 <div>
 <h1 className="text-3xl font-bold text-slate-100">Options Flow</h1>
 <p className="text-slate-400 mt-1">Real-time and historical options flow data</p>
 </div>
 {pageReady && (
 <div className="flex items-center gap-2">
 <span className={`text-xs rounded px-2 py-1 border ${
 mode === 'LIVE' 
 ? 'border-emerald-500 bg-emerald-50 text-emerald-700' 
 : mode === 'DEMO' 
 ? 'border-amber-500 bg-amber-50 text-amber-700'
 : 'border-slate-500 bg-slate-50 text-slate-700'
 }`}>
 {mode === 'LIVE' ? 'LIVE FEED' : mode === 'DEMO' ? 'DEMO DATA' : 'UNKNOWN'}
 </span>
 {error && (
 <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded border border-amber-200">
 degraded: using fallback
 </span>
 )}
 </div>
 )}
 </div>

 {/* Tabs */}
 <div className="flex items-center gap-2 flex-wrap">
 {[
 { key: 'SUMMARY', label: 'Summary', path: '/flow' },
 { key: 'LIVE', label: 'Live', path: '/flow/live' },
 { key: 'HIST', label: 'Hist', path: '/flow/hist' },
 { key: 'LIT_TRADES', label: 'Lit Trades', path: '/flow/lit-trades' },
 { key: 'DARK_POOL', label: '🕶️ Dark Pool', path: '/flow/dark-pool' },
 { key: 'NEWS', label: 'News', path: '/flow/news' },
 { key: 'CONGRESS', label: 'Congress', path: '/flow/congress' },
 { key: 'INSIDERS', label: 'Insiders', path: '/flow/insiders' }
 ].map(tab => (
 <button
 key={tab.key}
 onClick={() => navigate(tab.path + (tab.key === 'LIVE' ? search : ''))}
 className={`px-4 py-2 rounded-full border font-medium transition-colors ${
 currentTab === tab.key
 ? 'bg-slate-800 text-slate-200 border-slate-700'
 : 'bg-slate-900/70 text-slate-300 border-slate-700 hover:bg-slate-800'
 }`}
 >
 {tab.label}
 </button>
 ))}
 </div>

 {/* Filters */}
 {['SUMMARY', 'LIVE', 'HIST'].includes(currentTab) && (
 <div className="space-y-4">
 <FlowFilters value={filters} onChange={handleFiltersChange} />
 <div className="flex justify-end">
 <button
 onClick={handleApplyFilters}
 disabled={loading}
 className="px-6 py-2 bg-slate-700 text-slate-200 rounded-lg hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50"
 >
 {loading ? 'Loading...' : 'Apply Filters'}
 </button>
 </div>
 </div>
 )}

 {/* Content - Always show if pageReady */}
 {pageReady ? (
 <>
 {currentTab === 'SUMMARY' && (
 <FlowSummary bullish={data?.bullish || []} bearish={data?.bearish || []} />
 )}
 
 {currentTab === 'LIVE' && (
 <LiveFlow />
 )}
 
 {currentTab === 'HIST' && (
 <FlowTable items={data?.items || []} />
 )}
 
 {currentTab === 'LIT_TRADES' && (
 <LiveLitTradesFeed ticker={filters.symbol || 'SPY'} />
 )}
 
 {currentTab === 'DARK_POOL' && (
 <LiveOffLitTradesFeed ticker={filters.symbol || 'SPY'} />
 )}
 
 {currentTab === 'NEWS' && (
 <div className="bg-slate-900/70 border border-slate-800 rounded-2xl divide-y divide-slate-800">
 {(data?.items || []).length === 0 ? (
 <div className="p-8 text-center text-slate-400">
 No news data available
 </div>
 ) : (
 (data?.items || []).map((n, i) => (
 <div key={i} className="p-4 hover:bg-slate-800/50">
 <div className="font-semibold text-slate-200 mb-2">
 {n.title || n.headline || 'No title'}
 </div>
 <div className="text-sm text-slate-400">
 {n.source && <span>{n.source} · </span>}
 {n.time || n.date || 'No date'}
 </div>
 {n.summary && (
 <div className="text-sm text-slate-300 mt-2">
 {n.summary}
 </div>
 )}
 </div>
 ))
 )}
 </div>
 )}
 
 {currentTab === 'CONGRESS' && (
 <FlowTable items={data?.items || []} />
 )}
 
 {currentTab === 'INSIDERS' && (
 <FlowTable items={data?.items || []} />
 )}
 </>
 ) : (
 <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-8">
 <div className="flex items-center justify-center">
 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-400"></div>
 <span className="ml-3 text-slate-400">Loading Options Flow…</span>
 </div>
 </div>
 )}

 {/* Empty State for edge cases */}
 {pageReady && !data && (
 <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-8">
 <div className="text-center text-slate-400">
 No data (demo fallback active).
 </div>
 </div>
 )}
 </div>
 </div>
 </div>
 );
}