import React, { useEffect, useMemo, useState } from "react";
import { ChevronDown, Settings, RefreshCw, AlertTriangle } from "lucide-react";

const backendUrl = process.env.REACT_APP_BACKEND_URL;

const defaultConfig = {
  delta_min: 0.25,
  delta_max: 0.3,
  dte_min: 20,
  dte_max: 40,
  iv_rank_min: 40,
  vix_min: 15,
  vix_max: 25,
  roll_delta_threshold: 0.35,
  roll_dte_threshold: 10,
  capital_base: 500000,
  dynamic_risk: true,
};

const demoPositions = [
  { ticker: "TSLA", price: 329, strike: 320, delta: 0.28, dte: 30, premium: 5.5, iv_rank: 55, vix: 20, selected: true },
  { ticker: "AAPL", price: 231, strike: 230, delta: 0.27, dte: 28, premium: 2.8, iv_rank: 50, vix: 20, selected: true },
  { ticker: "NVDA", price: 175, strike: 170, delta: 0.26, dte: 25, premium: 3.4, iv_rank: 60, vix: 20, selected: true },
  { ticker: "AMZN", price: 222, strike: 220, delta: 0.25, dte: 33, premium: 2.7, iv_rank: 48, vix: 20, selected: true },
  { ticker: "SPY",  price: 636, strike: 630, delta: 0.26, dte: 26, premium: 9.0, iv_rank: 45, vix: 20, selected: true },
  { ticker: "QQQ",  price: 563, strike: 560, delta: 0.27, dte: 22, premium: 7.2, iv_rank: 52, vix: 20, selected: true },
  { ticker: "PLTR", price: 156, strike: 155, delta: 0.29, dte: 29, premium: 1.8, iv_rank: 58, vix: 20, selected: true },
];

export default function OptionsSelling() {
  const [config, setConfig] = useState(defaultConfig);
  const [mode, setMode] = useState("equal");
  const [positionsText, setPositionsText] = useState(JSON.stringify({ positions: demoPositions }, null, 2));
  const [watchlist, setWatchlist] = useState(["AAPL","TSLA","NVDA","AMZN","SPY","QQQ","PLTR"]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const [expanded, setExpanded] = useState({}); // map like sidebar

  const table = useMemo(() => {
    if (!data) return [];
    const src = mode === "greedy" ? data?.table_greedy : data?.table_equal;
    return Array.isArray(src) ? src : [];
  }, [data, mode]);

  const summary = useMemo(() => {
    if (!data) return null;
    return mode === "greedy" ? data?.summary_greedy : data?.summary_equal;
  }, [data, mode]);

  const grouped = useMemo(() => {
    const g = {};
    table.forEach((row) => {
      const key = (row.ticker || "").toUpperCase();
      if (!g[key]) g[key] = [];
      g[key].push(row);
    });
    return g;
  }, [table]);

  const toggle = (sym) => setExpanded((prev) => ({ ...prev, [sym]: !prev[sym] }));
  const expandAll = () => setExpanded(Object.keys(grouped).reduce((acc, s) => ({ ...acc, [s]: true }), {}));
  const collapseAll = () => setExpanded({});

  const compute = async () => {
    try {
      setLoading(true); setError("");
      let payloadPositions = [];
      try {
        const parsed = JSON.parse(positionsText);
        payloadPositions = parsed.positions || parsed || [];
      } catch (e) {
        throw new Error("Positions JSON invalid");
      }
      const body = {
        positions: payloadPositions,
        config,
        mode,
        watchlist,
      };
      const resp = await fetch(`${backendUrl}/api/options/selling/compute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!resp.ok) throw new Error(`Request failed: ${resp.status}`);
      const json = await resp.json();
      if (json.status !== "success") throw new Error(json.detail || "Compute failed");
      setData(json.data);
    } catch (e) {
      setError(e.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // auto compute on first mount with demo
    compute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="px-6 py-4 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Puts Options Selling</h1>
          <div className="flex items-center gap-2">
            <button onClick={compute} disabled={loading} className="px-3 py-2 bg-blue-600 rounded hover:bg-blue-700 flex items-center gap-2">
              <RefreshCw className={loading ? 'animate-spin' : ''} size={16} /> Compute
            </button>
          </div>
        </div>
        {error && (
          <div className="mt-3 bg-red-900/60 border border-red-700 text-red-200 px-3 py-2 rounded">
            <AlertTriangle size={16} className="inline mr-2" /> {error}
          </div>
        )}
      </div>

      {/* Config Panel */}
      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex items-center gap-2 mb-3 text-slate-200"><Settings size={16}/> Config</div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <label className="flex flex-col">Delta min<input type="number" step="0.01" value={config.delta_min} onChange={e=>setConfig({...config, delta_min: parseFloat(e.target.value)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">Delta max<input type="number" step="0.01" value={config.delta_max} onChange={e=>setConfig({...config, delta_max: parseFloat(e.target.value)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">DTE min<input type="number" value={config.dte_min} onChange={e=>setConfig({...config, dte_min: parseInt(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">DTE max<input type="number" value={config.dte_max} onChange={e=>setConfig({...config, dte_max: parseInt(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">IV Rank min<input type="number" value={config.iv_rank_min} onChange={e=>setConfig({...config, iv_rank_min: parseFloat(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">VIX min<input type="number" value={config.vix_min} onChange={e=>setConfig({...config, vix_min: parseFloat(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">VIX max<input type="number" value={config.vix_max} onChange={e=>setConfig({...config, vix_max: parseFloat(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">Roll Δ<input type="number" step="0.01" value={config.roll_delta_threshold} onChange={e=>setConfig({...config, roll_delta_threshold: parseFloat(e.target.value)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">Roll DTE<input type="number" value={config.roll_dte_threshold} onChange={e=>setConfig({...config, roll_dte_threshold: parseInt(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex flex-col">Capital<input type="number" value={config.capital_base} onChange={e=>setConfig({...config, capital_base: parseFloat(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
            <label className="flex items-center gap-2 mt-1"><input type="checkbox" checked={config.dynamic_risk} onChange={e=>setConfig({...config, dynamic_risk: e.target.checked})}/> Dynamic Risk</label>
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="mb-2 text-slate-200">Positions JSON</div>
          <textarea value={positionsText} onChange={e=>setPositionsText(e.target.value)} className="w-full h-56 bg-slate-900 border border-slate-700 rounded p-2 text-xs"></textarea>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="mb-2 text-slate-200">Mode & Watchlist</div>
          <div className="flex items-center gap-3 text-sm">
            <label className="flex items-center gap-1"><input type="radio" name="mode" value="equal" checked={mode==='equal'} onChange={()=>setMode('equal')}/> Equal</label>
            <label className="flex items-center gap-1"><input type="radio" name="mode" value="greedy" checked={mode==='greedy'} onChange={()=>setMode('greedy')}/> Greedy</label>
            <label className="flex items-center gap-1"><input type="radio" name="mode" value="both" checked={mode==='both'} onChange={()=>setMode('both')}/> Both</label>
          </div>
          <div className="mt-3 text-sm">
            <div className="mb-1">Watchlist (comma separated)</div>
            <input value={watchlist.join(',')} onChange={e=>setWatchlist(e.target.value.split(',').map(s=>s.trim()).filter(Boolean))} className="w-full bg-slate-700 rounded px-2 py-1"/>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="px-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <div className="text-slate-300 text-sm">Capital Blocked</div>
            <div className="text-2xl font-bold">${(summary.capital_active_blocked||0).toLocaleString()}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <div className="text-slate-300 text-sm">Risk (Delta-adjusted)</div>
            <div className="text-2xl font-bold">${(summary.risk_economic_active||0).toLocaleString()}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <div className="text-slate-300 text-sm">Signals</div>
            <div className="text-2xl font-bold">SELL PUT: {summary.signals_SELL PUT ?? 0} • ROLL: {summary.signals_ROLL ?? 0} • CC: {summary.signals_COVERED CALL ?? 0}</div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="text-slate-300">Rows: {table.length}</div>
          <div className="flex gap-2">
            <button onClick={expandAll} className="px-3 py-1 bg-slate-700 rounded">Expand All</button>
            <button onClick={collapseAll} className="px-3 py-1 bg-slate-700 rounded">Collapse All</button>
          </div>
        </div>
        <table className="w-full text-sm bg-slate-800 rounded">
          <thead>
            <tr className="border-b border-slate-700 text-slate-300">
              <th className="text-left py-2 px-2">Ticker</th>
              <th className="text-right py-2 px-2">Δ</th>
              <th className="text-right py-2 px-2">DTE</th>
              <th className="text-right py-2 px-2">Strike</th>
              <th className="text-right py-2 px-2">Premium</th>
              <th className="text-right py-2 px-2">Eligible</th>
              <th className="text-right py-2 px-2">Signal</th>
              <th className="text-right py-2 px-2">Contracts</th>
              <th className="text-right py-2 px-2">Cap/ct</th>
              <th className="text-right py-2 px-2">Risk/ct</th>
              <th className="text-right py-2 px-2">Monthly %</th>
              <th className="text-left py-2 px-2">Notes</th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(grouped).sort().map((sym) => {
              const rows = grouped[sym];
              const isExpanded = !!expanded[sym];
              const cap = rows.reduce((s,r)=> s + (r.capital_per_contract||0), 0);
              const eff = rows.reduce((s,r)=> s + (r.risk_per_contract||0), 0);
              return (
                <React.Fragment key={sym}>
                  <tr className="border-b border-slate-700 bg-slate-800 hover:bg-slate-700 cursor-pointer" onClick={()=>toggle(sym)}>
                    <td className="py-3 px-2"><div className="flex items-center"><ChevronDown className={`w-4 h-4 text-slate-400 mr-2 transition-transform ${isExpanded ? 'rotate-180':'rotate-0'}`}/><span className="text-blue-300 font-bold">{sym}</span></div></td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-right py-3 px-2 text-slate-300">{rows.reduce((s,r)=> s + (r.contracts||0), 0)}</td>
                    <td className="text-right py-3 px-2 text-slate-300">${cap.toLocaleString()}</td>
                    <td className="text-right py-3 px-2 text-slate-300">${eff.toLocaleString()}</td>
                    <td className="text-right py-3 px-2 text-slate-300">-</td>
                    <td className="text-left py-3 px-2 text-slate-300">{rows.find(r=>r.notes)?.notes || ''}</td>
                  </tr>
                  {isExpanded && rows.map((r, idx) => (
                    <tr key={`${sym}-${idx}`} className="border-b border-slate-800">
                      <td className="py-2 px-2 text-slate-200">└ {r.ticker}</td>
                      <td className="text-right py-2 px-2">{Number(r.delta).toFixed(2)}</td>
                      <td className="text-right py-2 px-2">{r.dte}</td>
                      <td className="text-right py-2 px-2">{r.strike}</td>
                      <td className="text-right py-2 px-2">{r.premium}</td>
                      <td className="text-right py-2 px-2">{String(r.eligible)}</td>
                      <td className="text-right py-2 px-2">{r.signal}</td>
                      <td className="text-right py-2 px-2">{r.contracts}</td>
                      <td className="text-right py-2 px-2">${(r.capital_per_contract||0).toLocaleString()}</td>
                      <td className="text-right py-2 px-2">${(r.risk_per_contract||0).toLocaleString()}</td>
                      <td className="text-right py-2 px-2">{Number(r.monthly_yield_pct||0).toFixed(2)}%</td>
                      <td className="text-left py-2 px-2">{r.notes}</td>
                    </tr>
                  ))}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}