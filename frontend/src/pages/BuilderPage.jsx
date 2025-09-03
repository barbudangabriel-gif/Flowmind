import React, { useEffect, useMemo, useState, useRef, forwardRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FLAT_BUILD_LIST, toSlug } from '../lib/buildStrategies';
import BuildHoverMegaMenu from '../components/nav/BuildHoverMegaMenu';
import { SpreadQualityMeter } from '../components/SpreadQualityMeter';
import { StrategyPicker } from '../components/StrategyPicker';
import BuilderHeaderV2 from '../components/build/BuilderHeaderV2';
import RailsBar from '../components/build/RailsBar';
import StatsRow from '../components/build/StatsRow';
import ControlsBar from '../components/build/ControlsBar';
import GreeksStrip from '../components/build/GreeksStrip';
import BuilderTable from '../components/build/BuilderTable';
import { StrikeRailPro } from '../components/StrikeRailPro';
import { GhostPagerOverlay } from '../components/GhostPagerOverlay';
import { GraphPaneSR2 } from '../components/GraphPaneSR2';
import ExpiryRail from '../components/ExpiryRail';
import TradeButton from '../components/builder/TradeButton';
import HistoryModal from '../components/builder/HistoryModal';
import QualityBadge from '../components/common/QualityBadge';
import CatalogModal from '../components/build/CatalogModal';
import { SQMBadge, ModeBadge, PerfBadge } from '../components/StatusBadges';
import { useChain } from '../options/api/useChain';
import { useExpirations } from '../hooks/useExpirations';
import { useQuality } from '../hooks/useQuality';
import { withRetry } from '../utils/withRetry';

// ==========================
// Utils
// ==========================

// Find strategy by slug from buildStrategies.js
function findStrategyBySlug(slug) {
  return FLAT_BUILD_LIST.find(s => s.slug === slug);
}

// Basic strategy definitions with legs  
function getStrategyLegs(strategyName) {
  const spot = 250; // Default spot price for TSLA
  
  switch(strategyName.toLowerCase().replace(/\s+/g, '_')) {
    case 'long_call':
      return [{ type: 'CALL', side: 'BUY', strike: spot + 5, qty: 1, active: true }];
    case 'long_put':
      return [{ type: 'PUT', side: 'BUY', strike: spot - 5, qty: 1, active: true }];
    case 'bull_call_spread':
      return [
        { type: 'CALL', side: 'BUY', strike: spot, qty: 1, active: true },
        { type: 'CALL', side: 'SELL', strike: spot + 10, qty: 1, active: false }
      ];
    case 'bear_put_spread':
      return [
        { type: 'PUT', side: 'BUY', strike: spot, qty: 1, active: true },
        { type: 'PUT', side: 'SELL', strike: spot - 10, qty: 1, active: false }
      ];
    case 'iron_condor':
      return [
        { type: 'PUT', side: 'SELL', strike: spot - 20, qty: 1, active: false },
        { type: 'PUT', side: 'BUY', strike: spot - 30, qty: 1, active: false },
        { type: 'CALL', side: 'SELL', strike: spot + 20, qty: 1, active: false },
        { type: 'CALL', side: 'BUY', strike: spot + 30, qty: 1, active: false }
      ];
    default:
      return [{ type: 'CALL', side: 'BUY', strike: spot + 5, qty: 1, active: true }];
  }
}

function inferStanceFromDelta(deltaSum) {
  if (typeof deltaSum !== 'number') return 'neutral';
  if (Math.abs(deltaSum) < 0.1) return 'neutral';
  if (deltaSum > 0.1) return 'bullish';
  if (deltaSum < -0.1) return 'bearish';
  return 'neutral';
}

async function fetchPricing(builder) {
  const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";
  
  const payload = {
    symbol: builder.symbol,
    expiry: builder.expiry || '2025-02-21',
    dte: Math.max(1, builder.dte || 30),
    legs: Array.isArray(builder.legs) ? builder.legs : [],
    qty: Math.max(1, builder.qty || 1),
    iv_mult: Math.min(2, Math.max(0.8, builder.params.iv_mult || 1)),
    range_pct: Math.min(0.3, Math.max(0.05, builder.params.range_pct || 0.15)),
    mode: 'pl_usd',
    strategyId: builder.strategyId || 'long_call'
  };

  const response = await withRetry(() => 
    fetch(`${API}/api/builder/price`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => { 
      if (!r.ok) throw new Error(`price ${r.status}`); 
      return r.json(); 
    })
  );
  
  return response;
}

const BuilderChart = forwardRef(function BuilderChart(
  { data, width=900, height=260, target, showProbability = true },
  ref
){
  if (!data) return null;
  const series = (data.chart?.series && data.chart.series[0]?.xy) ? data.chart.series[0].xy : [];
  if (!series.length) return <div className="bg-slate-800 rounded-lg p-6 text-slate-500">No chart data</div>;

  const pad = {l:48,r:24,t:10,b:28};
  const xs = series.map(p=>p[0]);
  const ys = series.map(p=>p[1]);
  const xMin = Math.min(...xs), xMax = Math.max(...xs);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const X = (x)=> pad.l + (x - xMin) / (xMax-xMin) * (width - pad.l - pad.r);
  const Y = (y)=> height - pad.b - (y - yMin) / (yMax-yMin || 1) * (height - pad.t - pad.b);
  
  // Create P&L path
  const path = series.map((p,i)=> `${i? 'L':'M'}${X(p[0])},${Y(p[1])}`).join(' ');
  
  // Create profit and loss fill paths
  const zeroY = Y(0);
  const profitPath = `M${pad.l},${zeroY}` + 
    series.filter(p => p[1] >= 0).map(p => `L${X(p[0])},${Y(p[1])}`).join(' ') + 
    `L${width-pad.r},${zeroY}Z`;
  const lossPath = `M${pad.l},${zeroY}` + 
    series.filter(p => p[1] < 0).map(p => `L${X(p[0])},${Y(p[1])}`).join(' ') + 
    `L${width-pad.r},${zeroY}Z`;
  
  // Probability path (optional)
  const prob = showProbability && data.chart.prob ? 
    data.chart.prob.map(p=> `${p===data.chart.prob[0]?'M':'L'}${X(p.x)},${Y(yMin + (yMax-yMin)*p.y)}`).join(' ') : '';
  
  const spotX = X(data.meta?.spot || 0);
  const targetX = target ? X(target) : null;
  const breakevens = data.meta?.breakevens || [];
  
  return (
    <div className="bg-slate-800 rounded-lg overflow-hidden" data-testid="builder-chart">
      <svg ref={ref} width={width} height={height} className="w-full">
        {/* Probability band (back layer) */}
        {showProbability && prob && (
          <path 
            d={prob} 
            fill="var(--pl-prob-fill, rgba(59, 130, 246, 0.16))" 
            stroke="var(--pl-prob-line, #60a5fa)" 
            strokeWidth={1}
            opacity={0.7}
          />
        )}
        
        {/* Loss region fill */}
        {yMin < 0 && (
          <path 
            d={lossPath} 
            fill="var(--pl-loss-fill, rgba(239, 68, 68, 0.22))" 
            opacity={0.8}
          />
        )}
        
        {/* Profit region fill */}
        {yMax > 0 && (
          <path 
            d={profitPath} 
            fill="var(--pl-profit-fill, rgba(34, 197, 94, 0.22))" 
            opacity={0.8}
          />
        )}
        
        {/* Axes */}
        <line x1={pad.l} y1={height-pad.b} x2={width-pad.r} y2={height-pad.b} stroke="#cbd5e1"/>
        <line x1={pad.l} y1={pad.t} x2={pad.l} y2={height-pad.b} stroke="#cbd5e1"/>
        
        {/* Zero line with unified styling */}
        {0>=yMin && 0<=yMax && (
          <line 
            x1={pad.l} 
            y1={Y(0)} 
            x2={width-pad.r} 
            y2={Y(0)} 
            stroke="var(--pl-zero-axis, #94a3b8)" 
            strokeDasharray="4 4"
            strokeWidth={1}
          />
        )}
        
        {/* P&L payoff line */}
        <path 
          d={path} 
          fill="none" 
          stroke="var(--pl-profit-line, #22c55e)" 
          strokeWidth={2.5}
        />
        
        {/* Spot price marker */}
        <line 
          x1={spotX} 
          x2={spotX} 
          y1={pad.t} 
          y2={height-pad.b} 
          stroke="var(--pl-spot-line, #6ee7b7)" 
          strokeWidth={2}
        />
        
        {/* Target price marker */}
        {targetX != null && (
          <line 
            x1={targetX} 
            x2={targetX} 
            y1={pad.t} 
            y2={height-pad.b} 
            stroke="var(--pl-atm-line, #a78bfa)" 
            strokeDasharray="3 3"
            strokeWidth={1.5}
          />
        )}
        
        {/* Breakeven markers */}
        {breakevens.map((be, i) => (
          <line 
            key={i}
            x1={X(be)} 
            x2={X(be)} 
            y1={pad.t} 
            y2={height-pad.b} 
            stroke="var(--pl-breakeven-line, #fbbf24)" 
            strokeDasharray="6 4"
            strokeWidth={1.5}
          />
        ))}
        
        {/* Labels */}
        <text x={pad.l} y={14} fontSize={12} fill="#94a3b8">P/L</text>
        <text x={width-pad.r-60} y={height-6} fontSize={12} fill="#94a3b8">Price</text>
        
        {/* Spot label */}
        <text x={spotX + 4} y={pad.t + 15} fontSize={10} fill="var(--pl-spot-line, #6ee7b7)">
          Spot
        </text>
        
        {/* Breakeven labels */}
        {breakevens.map((be, i) => (
          <text 
            key={i}
            x={X(be) + 4} 
            y={pad.t + 30 + (i % 2) * 15} 
            fontSize={10} 
            fill="var(--pl-breakeven-line, #fbbf24)"
          >
            BE
          </text>
        ))}
      </svg>
    </div>
  );
});

export default function BuilderPage() {
  // Extract strategyId from URL parameters  
  const { strategyId } = useParams();
  const navigate = useNavigate();
  
  // State for persistent header Build menu
  const [showBuildMenu, setShowBuildMenu] = useState(false);
  const [hoverTimer, setHoverTimer] = useState(null);
  
  // Build menu hover handlers
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
  
  // Central state management
  const [builder, setBuilder] = useState({
    symbol: 'TSLA',
    expiry: '',
    legs: [],
    qty: 1,
    dte: 30,
    strategyId: strategyId || 'long_call',
    params: { 
      iv_mult: 1.0, 
      range_pct: 0.15 
    }
  });

  const [pricing, setPricing] = useState(null);
  const [mode, setMode] = useState("graph"); // "table" | "pl$" | "pl%" | "contract" | "%risk"
  const [dataMode, setDataMode] = useState('DEMO');
  
  // Chart options state
  const [showProbability, setShowProbability] = useState(true);
  const [highContrast, setHighContrast] = useState(false);
  
  // Core page state
  const [pageReady, setPageReady] = useState(true); // Force ready for debugging
  const [coreError, setCoreError] = useState(null);
  const [perfMetrics, setPerfMetrics] = useState({});
  
  // UI state
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const chartRef = useRef(null);

  // Initialize strategy from URL parameter
  useEffect(() => {
    console.log('Strategy initialization effect running, strategyId:', strategyId);
    if (strategyId) {
      const strategy = findStrategyBySlug(strategyId);
      console.log('Found strategy:', strategy);
      if (strategy) {
        const legs = getStrategyLegs(strategy.name);
        console.log('Generated legs:', legs);
        setBuilder(prev => ({
          ...prev,
          strategyId: strategyId,
          legs: legs
        }));
      }
    }
    // Set page ready after strategy initialization
    console.log('Setting pageReady to true');
    setPageReady(true);
  }, [strategyId]);

  // Parse deep-link fail-safe (doesn't throw)
  useEffect(() => {
    try {
      const url = new URL(window.location.href);
      const s = url.searchParams.get('s');
      if (s) {
        const json = JSON.parse(decodeURIComponent(escape(atob(s))));
        setBuilder(prev => ({
          ...prev,
          symbol: json.symbol || prev.symbol,
          expiry: json.expiry || prev.expiry,
          legs: Array.isArray(json.legs) && json.legs.length ? json.legs : prev.legs,
          strategyId: json.strategyId || prev.strategyId,
          dte: json.dte || prev.dte,
          qty: json.qty || prev.qty
        }));
      }
    } catch (e) {
      console.warn('Deep-link parse error:', e);
      // Builder has fallback - ignore error
    }
  }, []);

  // Debounced pricing fetch
  useEffect(() => {
    let alive = true;
    
    console.log('Pricing fetch effect triggered, builder state:', builder);
    
    const timeoutId = setTimeout(async () => {
      try {
        setCoreError(null);
        console.log('Starting pricing fetch...');
        
        const t0 = performance.now();
        const data = await fetchPricing(builder);
        const dt = performance.now() - t0;
        
        console.log('Pricing fetch completed in', dt, 'ms');
        setPerfMetrics(prev => ({ ...prev, priceMs: dt }));
        
        // Log slow operations
        if (dt > 1200) {
          console.warn('price slow', Math.round(dt), 'ms');
        }
        
        if (!alive) return;
        
        // Detect data mode from response
        setDataMode(data?.meta?.mode || (data?.demo ? 'DEMO' : 'LIVE'));
        setPricing(data);
        console.log('Pricing data set:', data);
        
      } catch (e) {
        console.warn('Builder core error:', e);
        if (!alive) return;
        setCoreError(e?.message ?? 'builder-core-error');
        setDataMode('DEMO'); // Always demo on error
        // Set fallback pricing so UI can still render
        setPricing({
          net_price: 0,
          max_profit: 0,
          max_loss: 0,
          breakevens: [],
          greeks: { delta: 0 },
          chart_data: []
        });
      }
    }, 200); // 200ms debounce

    return () => { 
      alive = false; 
      clearTimeout(timeoutId);
    };
  }, [builder]); // Re-run when builder state changes

  // External data hooks
  const { list: expirations } = useExpirations(builder.symbol);
  const { data: chain } = useChain({ symbol: builder.symbol, expiry: builder.expiry });

  // Patch D - SQM/Quality - live connected to IV/Range
  const { score: sqm, mode: sqmMode } = useQuality(
    { 
      legs: builder.legs, 
      spot: pricing?.meta?.spot || 250, 
      ivMult: builder.params.iv_mult, 
      rangePct: builder.params.range_pct, 
      dte: builder.dte, 
      symbol: builder.symbol 
    },
    { enabled: pageReady }
  );

  // Handlers
  const handleParamsChange = (patch) => {
    setBuilder(prev => ({
      ...prev,
      params: { ...prev.params, ...patch }
    }));
  };

  const handleStrike = (strike) => {
    setBuilder(prev => ({
      ...prev,
      legs: prev.legs.map(leg => 
        leg.active ? { ...leg, strike } : leg
      )
    }));
  };

  const handleTrade = () => {
    console.log('Trade button clicked', {
      builder,
      deltaSum: pricing?.greeks?.delta
    });
  };

  // Loading state - only for core essentials
  console.log('BuilderPage render - pageReady:', pageReady, 'strategyId:', strategyId);
  
  if (!pageReady) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-slate-300">Loading Options Builder...</div>
          <div className="text-xs text-slate-500 mt-1">Preparing advanced features</div>
          <div className="text-xs text-slate-400 mt-2">Strategy: {strategyId || 'none'}</div>
        </div>
      </div>
    );
  }

  const stance = inferStanceFromDelta(pricing?.greeks?.delta);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-4">
        
        {/* Core Error Display */}
        {coreError && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 mb-4">
            <div className="text-sm text-red-300">Core error: {String(coreError)}</div>
          </div>
        )}

        {/* Header */}
        <BuilderHeaderV2
          symbol={builder.symbol}
          meta={{ 
            price: pricing?.meta?.spot, 
            change: 2.45, // Mock data - you can get from pricing
            changePct: 1.2,
            mode: dataMode 
          }}
          sqm={{ score: sqm, degraded: sqmMode === 'degraded' }}
          stance={stance}
          legs={builder.legs}
          strategyId={builder.strategyId}
          onCatalog={() => setCatalogOpen(true)}
          onHistorical={() => setHistoryModalOpen(true)}
          onTrade={handleTrade}
        />

        {/* Rails */}
        <RailsBar
          symbol={builder.symbol}
          expiry={builder.expiry}
          onExpiry={(e) => setBuilder(prev => ({ ...prev, expiry: e }))}
          chain={chain}
          onStrike={handleStrike}
          expirations={expirations}
        />

        {/* Stats Row */}
        <StatsRow p={pricing} />

        {/* Chart & Content */}
        <div className="space-y-4">
          {mode === 'graph' && (
            <div>
              <BuilderChart 
                ref={chartRef} 
                data={pricing} 
                showProbability={showProbability}
              />
              <GreeksStrip greeks={pricing?.greeks} />
            </div>
          )}
          
          {mode !== 'graph' && (
            <BuilderTable 
              pricing={pricing} 
              builder={builder} 
              variant={mode}
            />
          )}
        </div>

        {/* Controls */}
        <ControlsBar
          builder={builder}
          pricing={pricing}
          mode={mode}
          setMode={setMode}
          onParams={handleParamsChange}
          showProbability={showProbability}
          setShowProbability={setShowProbability}
          highContrast={highContrast}
          setHighContrast={setHighContrast}
        />

        {/* Modals */}
        <HistoryModal 
          open={historyModalOpen} 
          onClose={() => setHistoryModalOpen(false)} 
          symbol={builder.symbol}
          legs={builder.legs}
          expiry={builder.expiry}
          dte={builder.dte}
        />

        <CatalogModal 
          open={catalogOpen} 
          onOpenChange={setCatalogOpen} 
          symbol={builder.symbol}
        />
      </div>
    </div>
  );
}
function qs() {
  const p = new URLSearchParams(window.location.search);
  return Object.fromEntries(p.entries());
}
function safeJson(s) {
  try { return s ? JSON.parse(s) : null; } catch { return null; }
}
function b64urlDecode(s) {
  if (!s) return null;
  try {
    const pad = '='.repeat((4 - (s.length % 4)) % 4);
    const norm = (s + pad).replace(/-/g, '+').replace(/_/g, '/');
    const json = atob(norm);
    const data = safeJson(json);
    
    // Robust validation with safe fallback
    if (!data || typeof data !== 'object') {
      return { strategyId: 'long_call', legs: [], params: { iv_mult: 1, range_pct: 0.15 } };
    }
    
    // Validate required fields
    if (!Array.isArray(data.legs) || !data.strategyId) {
      return { strategyId: 'long_call', legs: [], params: { iv_mult: 1, range_pct: 0.15 } };
    }
    
    return data;
  } catch (error) {
    console.warn('Deep-link decode failed, using fallback:', error);
    return { strategyId: 'long_call', legs: [], params: { iv_mult: 1, range_pct: 0.15 } };
  }
}
const API = (window).API_BASE || process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "";
const jfetch = async (url, opts) => {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  // tolerăm atât {expirations:[...]} cât și [...]
  const body = await r.json().catch(()=> ({}));
  return body;
};

// ==========================
// Small components
// ==========================
function Card({title,children}){
  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <div className="text-sm text-slate-500">{title}</div>
      <div className="text-lg font-semibold mt-1">{children}</div>
    </div>
  );
}

function MetricCards({ data }){
  if (!data?.pricing) return null;
  const P = data.pricing;
  const money = (n)=> n==null? '—' : (n<0? `-$${Math.abs(n).toLocaleString()}` : `$${n.toLocaleString()}`);
  const pct = (n)=> (n==null? '—' : `${(n*100).toFixed(1)}%`);
  const debit = P.net_debit>0 ? money(P.net_debit) : '—';
  const credit = P.net_credit>0 ? money(P.net_credit) : '—';
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <Card title="Net Debit">{debit}</Card>
      <Card title="Net Credit">{credit}</Card>
      <Card title="Max Loss">{money(P.max_loss)}</Card>
      <Card title="Max Profit">{money(P.max_profit)}</Card>
      <Card title="Chance of Profit">{pct(P.chance_profit)}</Card>
      <Card title="Breakeven(s)">{P.breakevens?.map(b=>b.toFixed(2)).join(', ') || '—'}</Card>
    </div>
  );
}

function Legend({spot,target}){
  return (
    <div className="flex items-center gap-4 text-sm text-slate-600">
      <div className="flex items-center gap-1"><span className="w-4 h-0.5 bg-slate-900 inline-block"/> P/L at Expiration</div>
      <div className="flex items-center gap-1"><span className="w-4 h-0.5 bg-sky-600 inline-block"/> Probability (CDF)</div>
      <div className="ml-auto">Spot: <span className="font-semibold">{spot.toFixed(2)}</span>{target? <> · Target: <span className="font-semibold">{target.toFixed(2)}</span></>:null}</div>
    </div>
  );
}

// ==========================
// Utils
// ==========================

// Transform BuilderChart data to GraphPaneSR2 format
function transformToGraphSR2Series(data) {
  if (!data?.chart?.series?.[0]?.xy) return [];
  
  return data.chart.series[0].xy.map(([price, value]) => ({
    price,
    value,
    prob: null // Will be calculated by GraphPaneSR2 if needed
  }));
}

function HistoricalPanel({ payload, data }) {
  const [series, setSeries] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const API = (window).API_BASE || process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "";

  async function load() {
    setLoading(true); 
    setErr(null);
    try {
      const r = await fetch(`${API}/api/builder/historical`, {
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({...payload, days: 60})
      });
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      setSeries(j.series || []);
    } catch (e) { 
      setErr(e.message || 'load failed'); 
    } finally { 
      setLoading(false); 
    }
  }

  useEffect(() => { 
    load(); 
  }, [JSON.stringify(payload)]);

  if (loading) return <div className="text-slate-500">Loading historical…</div>;
  if (err) return <div className="text-rose-700">{err}</div>;
  if (!series?.length) return <div className="text-slate-500">No historical data</div>;

  // simple SVG area chart
  const W = 980, H = 220, p = {l: 48, r: 24, t: 10, b: 28};
  const minPL = Math.min(...series.map(s => s.pl));
  const maxPL = Math.max(...series.map(s => s.pl));
  const X = (i) => p.l + (i / (series.length - 1)) * (W - p.l - p.r);
  const Y = (y) => H - p.b - ((y - minPL) / (maxPL - minPL || 1)) * (H - p.t - p.b);
  const path = series.map((s, i) => `${i ? 'L' : 'M'}${X(i)},${Y(s.pl)}`).join(' ');

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <div className="flex items-center">
        <div className="text-sm text-slate-600">Historical P/L (mark‑to‑market, 60d)</div>
        <button 
          onClick={() => downloadCSV(`${payload.symbol}_${payload.expiry || ('dte' + payload.dte)}_historical.csv`, series)} 
          className="ml-auto px-3 py-1.5 rounded bg-slate-900 text-white text-xs"
        >
          Export CSV
        </button>
      </div>
      <svg width={W} height={H} className="mt-2">
        <line x1={p.l} y1={H - p.b} x2={W - p.r} y2={H - p.b} stroke="#cbd5e1"/>
        <line x1={p.l} y1={p.t} x2={p.l} y2={H - p.b} stroke="#cbd5e1"/>
        {0 >= minPL && 0 <= maxPL && <line x1={p.l} y1={Y(0)} x2={W - p.r} y2={Y(0)} stroke="#e2e8f0" strokeDasharray="4 4"/>}
        <path d={path} fill="none" stroke="#0f172a" strokeWidth={2}/>
      </svg>
      <div className="mt-2 text-xs text-slate-500">
        Last: {series[series.length - 1].pl.toLocaleString()} · Min: {minPL.toLocaleString()} · Max: {maxPL.toLocaleString()}
      </div>
    </div>
  );
}

// ==========================
// Main page
// ==========================
// (This section has been completely replaced with the new non-blocking implementation above)

// ==========================
// B4/6 Download Utilities
// ==========================
function downloadJSON(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function downloadSVGAsPNG(svg, filename) {
  const s = new XMLSerializer().serializeToString(svg);
  const svg64 = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
  const img = new Image();
  const cssPixelRatio = window.devicePixelRatio || 1;
  const rect = svg.getBoundingClientRect();
  const W = Math.max(800, Math.round(rect.width * cssPixelRatio));
  const H = Math.max(400, Math.round(rect.height * cssPixelRatio));
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D missing');

  await new Promise((resolve,reject)=>{
    img.onload = ()=>{ resolve(); };
    img.onerror = reject;
    img.src = svg64;
  });
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0,0,W,H);
  // scale draw to fit
  ctx.drawImage(img, 0, 0, W, H);

  const a = document.createElement('a');
  a.href = canvas.toDataURL('image/png');
  a.download = filename;
  a.click();
}

// B8 - Live Spread Quality Calculation
function marketForLeg(chain, kind, strike) {
  const rows = chain?.OptionChains?.[0]?.Strikes || [];
  for (const r of rows) {
    if (Number(r.StrikePrice) === Number(strike)) {
      const L = kind === 'CALL' ? (r.Calls?.[0] || {}) : (r.Puts?.[0] || {});
      const bid = Number(L.Bid || 0);
      const ask = Number(L.Ask || 0);
      const mid = (bid > 0 && ask > 0) ? (bid + ask) / 2 : Number(L.Last || 0);
      const oi = Number(L.OpenInterest || 0);
      const vol = Number(L.Volume || 0);
      const spr = Math.max(0, ask - bid);
      const rel = mid > 0 ? (spr / Math.max(0.05, mid)) : 1.0;
      return { bid, ask, mid, oi, vol, spr, rel };
    }
  }
  return { bid: 0, ask: 0, mid: 0, oi: 0, vol: 0, spr: 0, rel: 1 };
}

function spreadScore(rel) {
  if (rel <= 0) return 1;
  if (rel >= 0.2) return 0;
  if (rel <= 0.05) return 1 - 0.25 * (rel / 0.05);
  if (rel <= 0.10) return 0.75 - 0.25 * ((rel - 0.05) / 0.05);
  return 0.5 - 0.5 * ((rel - 0.10) / 0.10);
}

function computeQuality(chain, legs) {
  let wSum = 0, qSum = 0, slip = 0;
  let ok = true;
  
  for (const L of legs) {
    const mm = marketForLeg(chain, L.type, Number(L.strike));
    const q = 0.65 * spreadScore(mm.rel) + 0.35 * Math.tanh((mm.oi + mm.vol) / 1500);
    const w = Math.max(1, Math.abs(mm.mid));
    wSum += w;
    qSum += q * w;
    slip += 0.5 * mm.spr * 100;
    if (!(mm.rel <= 0.12 || mm.spr <= 0.10)) ok = false;
  }
  
  const quality = wSum ? (qSum / wSum) : 0;
  return { 
    quality: Math.round(quality * 100), 
    slippage: Math.round(slip * 100) / 100, 
    ok 
  };
}

// B7 - CSV Export Utility
function downloadCSV(filename, rows) {
  const headers = Object.keys(rows[0] || {t:'t', spot:'spot', pl:'pl'});
  const esc = (v) => typeof v === 'string' && (v.includes(',') || v.includes('"')) ? '"' + v.replace(/"/g, '""') + '"' : v;
  const body = [headers.join(',')].concat(rows.map(r => headers.map(h => esc(r[h] ?? '')).join(','))).join('\n');
  const blob = new Blob([body], {type:'text/csv;charset=utf-8;'});
  const a = document.createElement('a'); 
  a.href = URL.createObjectURL(blob); 
  a.download = filename; 
  a.click(); 
  URL.revokeObjectURL(a.href);
}