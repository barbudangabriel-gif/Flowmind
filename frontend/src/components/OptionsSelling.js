import React, { useEffect, useMemo, useState } from "react";
import { ChevronDown, Settings, RefreshCw, AlertTriangle, ToggleRight, Database, Zap } from "lucide-react";

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
  capital_base: 500000, // buget teoretic
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
  // Header controls
  const [source, setSource] = useState("TS"); // TS Budget active | Tasty skeleton
  const [activeTab, setActiveTab] = useState("candidates"); // candidates | tradelist | live

  // Engine config & inputs
  const [config, setConfig] = useState(defaultConfig);
  const [mode, setMode] = useState("equal");
  const [positionsText, setPositionsText] = useState(JSON.stringify({ positions: demoPositions }, null, 2));
  const [watchlist, setWatchlist] = useState(["AAPL","TSLA","NVDA","AMZN","SPY","QQQ","PLTR"]);

  // Compute request/response state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  // Trade list grouping
  const [groupBy, setGroupBy] = useState("signal"); // signal | ticker
  const [expanded, setExpanded] = useState({});

  // TS live options
  const [loadingLive, setLoadingLive] = useState(false);
  const [errorLive, setErrorLive] = useState("");
  const [accountId, setAccountId] = useState("");
  const [cashTS, setCashTS] = useState(0);
  const [positionsLive, setPositionsLive] = useState([]);
  const [expandedLive, setExpandedLive] = useState({});

  // Build table for engine output
  const table = useMemo(() => {
    if (!data) return [];
    let src = [];
    if (mode === "greedy") src = data?.table_greedy || [];
    else if (mode === "equal") src = data?.table_equal || [];
    else src = [...(data?.table_equal || []), ...(data?.table_greedy || [])];
    return Array.isArray(src) ? src : [];
  }, [data, mode]);

  const summary = useMemo(() => {
    if (!data) return null;
    if (mode === "greedy") return data?.summary_greedy;
    if (mode === "equal") return data?.summary_equal;
    // both -> prefer equal summary
    return data?.summary_equal || data?.summary_greedy;
  }, [data, mode]);

  const groupedTrade = useMemo(() => {
    const g = {};
    const keyField = groupBy === "signal" ? "signal" : "ticker";
    table.forEach((row) => {
      const key = (row[keyField] || "").toUpperCase();
      if (!g[key]) g[key] = [];
      g[key].push(row);
    });
    return g;
  }, [table, groupBy]);

  const toggle = (sym) => setExpanded((prev) => ({ ...prev, [sym]: !prev[sym] }));
  const expandAll = () => setExpanded(Object.keys(groupedTrade).reduce((acc, s) => ({ ...acc, [s]: true }), {}));
  const collapseAll = () => setExpanded({});

  // Compute using backend
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

  // TS Live fetcher (options only)
  const parseIsOption = (rawSymbol, assetType) => {
    const asset = (assetType || "").toUpperCase();
    if (asset.includes("OP")) return true;
    const base = (rawSymbol || '').trim();
    const parts = base.split(' ');
    if (parts.length > 1) {
      const tail = parts[1];
      return /^(\d{6})([CP])([0-9]+(?:\.[0-9]+)?)$/i.test(tail);
    }
    return false;
  };

  const normalizeLive = (positions) => {
    return (positions || [])
      .filter((p) => parseIsOption(p.symbol, p.asset_type))
      .map((pos) => {
        const raw = (pos.symbol || '').trim();
        const baseSym = (raw.split(' ')[0] || raw).split('_')[0];
        // Try option fields
        let option_type = pos.option_type || pos.right || pos.optionRight || pos.put_call || pos.CallPut;
        let strike_price = pos.strike || pos.strikePrice || pos.strike_price;
        let expiration_date = pos.expiration || pos.expirationDate || pos.Expiry || pos.expiration_date;
        if (!option_type || !strike_price || !expiration_date) {
          // parse from symbol tail
          const parts = raw.split(' ');
          if (parts.length > 1) {
            const tail = parts[1];
            const m = tail.match(/^(\d{6})([CP])([0-9]+(?:\.[0-9]+)?)$/i);
            if (m) {
              const [, yymmdd, cp, strikeStr] = m;
              const yy = parseInt(yymmdd.slice(0,2),10);
              const mm = yymmdd.slice(2,4);
              const dd = yymmdd.slice(4,6);
              const fullYear = yy >= 70 ? 1900+yy : 2000+yy;
              expiration_date = `${fullYear}-${mm}-${dd}`;
              option_type = (cp || '').toUpperCase() === 'P' ? 'PUT' : 'CALL';
              strike_price = parseFloat(strikeStr);
            }
          }
        }
        const price = pos.mark_price || pos.current_price || pos.last_price || pos.market_price || pos.price || 0;
        const mv = pos.market_value || Math.abs((pos.quantity || 0) * price);
        return {
          id: `opt-${raw}-${Math.random()}`,
          symbol: baseSym.toUpperCase(),
          quantity: pos.quantity || 0,
          current_price: price,
          market_value: mv,
          metadata: { option_type, strike_price, expiration_date, contract_symbol: raw },
        };
      });
  };

  const loadTSLive = async () => {
    try {
      setLoadingLive(true); setErrorLive("");
      const accResp = await fetch(`${backendUrl}/api/tradestation/accounts`);
      const accJson = await accResp.json();
      const accounts = accJson.accounts || accJson || [];
      const main = Array.isArray(accounts) ? (accounts.find(a=>a.Type==='Margin') || accounts[0]) : accounts;
      if (!main || !main.AccountID) throw new Error('No TS account');
      setAccountId(main.AccountID);
      const posResp = await fetch(`${backendUrl}/api/tradestation/accounts/${main.AccountID}/positions`);
      const posJson = await posResp.json();
      const positions = posJson.positions || posJson.data || posJson || [];
      const live = normalizeLive(positions);
      setPositionsLive(live);
      // balances for cash
      try {
        const balResp = await fetch(`${backendUrl}/api/tradestation/accounts/${main.AccountID}/balances`);
        const balJson = await balResp.json();
        const cb = balJson?.balances?.Balances?.[0]?.CashBalance || balJson?.balances?.CashBalance || 0;
        setCashTS(parseFloat(cb)||0);
      } catch { setCashTS(0); }
    } catch (e) {
      setErrorLive(e.message);
      setPositionsLive([]);
    } finally {
      setLoadingLive(false);
    }
  };

  // Auto compute once on mount with demo
  useEffect(() => {
    compute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load TS live when switching to tab
  useEffect(() => {
    if (source === 'TS' && activeTab === 'live') {
      loadTSLive();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source, activeTab]);

  // Header bar with source & tabs
  const HeaderBar = () => (
    <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Puts Options Selling</h1>
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-sm mr-2">Source:</span>
          <button className={`px-3 py-1 rounded ${source==='TS' ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-200'}`} onClick={()=>setSource('TS')}>
            <Database size={14} className="inline mr-1"/> TradeStation Budget
          </button>
          <button className="px-3 py-1 rounded bg-slate-800 text-slate-500 cursor-not-allowed" title="Coming soon">
            <Zap size={14} className="inline mr-1"/> Tastytrade (soon)
          </button>
          <button onClick={compute} disabled={loading} className="ml-4 px-3 py-2 bg-blue-600 rounded hover:bg-blue-700 flex items-center gap-2">
            <RefreshCw className={loading ? 'animate-spin' : ''} size={16} /> Compute
          </button>
        </div>
      </div>
      {/* Tabs */}
      <div className="mt-3 flex items-center gap-6 text-sm">
        {['candidates','tradelist','live'].map(tab => (
          <button key={tab} onClick={()=>setActiveTab(tab)} className={`pb-2 border-b-2 ${activeTab===tab ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}>
            {tab === 'candidates' ? 'Candidates' : tab === 'tradelist' ? 'Trade List' : 'Live Positions'}
          </button>
        ))}
        {source==='TS' && (
          <div className="ml-auto text-slate-300 text-sm">
            Cash (TS): <span className="font-semibold">${cashTS.toLocaleString()}</span> • Budget (theoretical): <input type="number" value={config.capital_base} onChange={(e)=>setConfig({...config, capital_base: parseFloat(e.target.value||0)})} className="ml-2 w-32 bg-slate-800 border border-slate-700 rounded px-2 py-0.5"/>
          </div>
        )}
      </div>
      {error && (
        <div className="mt-3 bg-red-900/60 border border-red-700 text-red-200 px-3 py-2 rounded">
          <AlertTriangle size={16} className="inline mr-2" /> {error}
        </div>
      )}
    </div>
  );

  // Candidates tab content
  const Candidates = () => (
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
          <label className="flex flex-col">Budget (theoretical)<input type="number" value={config.capital_base} onChange={e=>setConfig({...config, capital_base: parseFloat(e.target.value||0)})} className="bg-slate-700 rounded px-2 py-1"/></label>
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
          {['equal','greedy','both'].map(m => (
            <label key={m} className="flex items-center gap-1"><input type="radio" name="mode" value={m} checked={mode===m} onChange={()=>setMode(m)}/> {m}</label>
          ))}
        </div>
        <div className="mt-3 text-sm">
          <div className="mb-1">Watchlist (comma separated)</div>
          <input value={watchlist.join(',')} onChange={e=>setWatchlist(e.target.value.split(',').map(s=>s.trim()).filter(Boolean))} className="w-full bg-slate-700 rounded px-2 py-1"/>
        </div>
      </div>
    </div>
  );

  // Trade list tab
  const TradeList = () => (
    <div className="p-6">
      {!summary && (
        <div className="text-slate-400">Run Compute to generate trade list.</div>
      )}
      {summary && (
        <>
          <div className="flex items-center justify-between mb-3">
            <div className="text-slate-300 text-sm">Grouping: 
              <button onClick={()=>setGroupBy('signal')} className={`ml-2 px-2 py-1 rounded ${groupBy==='signal'?'bg-blue-600':'bg-slate-700'}`}>by Signal</button>
              <button onClick={()=>setGroupBy('ticker')} className={`ml-2 px-2 py-1 rounded ${groupBy==='ticker'?'bg-blue-600':'bg-slate-700'}`}>by Ticker</button>
            </div>
            <div className="flex gap-2">
              <button onClick={expandAll} className="px-3 py-1 bg-slate-700 rounded">Expand All</button>
              <button onClick={collapseAll} className="px-3 py-1 bg-slate-700 rounded">Collapse All</button>
              <button disabled className="px-3 py-1 bg-slate-800 text-slate-500 rounded" title="Coming soon">Export JSON</button>
              <button disabled className="px-3 py-1 bg-slate-800 text-slate-500 rounded" title="Coming soon">Export CSV</button>
            </div>
          </div>
          <table className="w-full text-sm bg-slate-800 rounded">
            <thead>
              <tr className="border-b border-slate-700 text-slate-300">
                <th className="text-left py-2 px-2">Group</th>
                <th className="text-right py-2 px-2">Items</th>
                <th className="text-right py-2 px-2">Contracts</th>
                <th className="text-right py-2 px-2">Cap (sum)</th>
                <th className="text-right py-2 px-2">Risk (sum)</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(groupedTrade).sort().map((key) => {
                const rows = groupedTrade[key];
                const isExpanded = !!expanded[key];
                const totalContracts = rows.reduce((s,r)=> s + (r.contracts||0), 0);
                const capSum = rows.reduce((s,r)=> s + (r.capital_per_contract||0), 0);
                const riskSum = rows.reduce((s,r)=> s + (r.risk_per_contract||0), 0);
                return (
                  <React.Fragment key={key}>
                    <tr className="border-b border-slate-700 bg-slate-800 hover:bg-slate-700 cursor-pointer" onClick={()=>toggle(key)}>
                      <td className="py-3 px-2"><div className="flex items-center"><ChevronDown className={`w-4 h-4 text-slate-400 mr-2 transition-transform ${isExpanded ? 'rotate-180':'rotate-0'}`}/><span className="text-blue-300 font-bold">{key}</span></div></td>
                      <td className="text-right py-3 px-2 text-slate-300">{rows.length}</td>
                      <td className="text-right py-3 px-2 text-slate-300">{totalContracts}</td>
                      <td className="text-right py-3 px-2 text-slate-300">${capSum.toLocaleString()}</td>
                      <td className="text-right py-3 px-2 text-slate-300">${riskSum.toLocaleString()}</td>
                    </tr>
                    {isExpanded && rows.map((r, idx) => (
                      <tr key={`${key}-${idx}`} className="border-b border-slate-800">
                        <td className="py-2 px-2 text-slate-200">└ {r.ticker} • {r.signal}</td>
                        <td className="text-right py-2 px-2">Δ {Number(r.delta).toFixed(2)} • DTE {r.dte} • Strike {r.strike} • Prem {r.premium}</td>
                        <td className="text-right py-2 px-2">{r.contracts}</td>
                        <td className="text-right py-2 px-2">${(r.capital_per_contract||0).toLocaleString()}</td>
                        <td className="text-right py-2 px-2">${(r.risk_per_contract||0).toLocaleString()}</td>
                      </tr>
                    ))}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </div>
  );

  // Live positions tab (TS)
  const LivePositions = () => {
    const grouped = useMemo(() => {
      const g = {};
      positionsLive.forEach((p) => {
        const key = (p.symbol || '').toUpperCase();
        if (!g[key]) g[key] = [];
        g[key].push(p);
      });
      return g;
    }, [positionsLive]);

    const toggleLive = (sym) => setExpandedLive((prev)=> ({ ...prev, [sym]: !prev[sym] }));
    const expandAllLive = () => setExpandedLive(Object.keys(grouped).reduce((acc, s) => ({ ...acc, [s]: true }), {}));
    const collapseAllLive = () => setExpandedLive({});

    const totalMV = positionsLive.reduce((s,p)=> s + (p.market_value||0), 0);

    return (
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <div className="text-slate-300 text-sm">Account: <span className="font-semibold">{accountId || '-'}</span> • Cash: <span className="font-semibold">${cashTS.toLocaleString()}</span> • Options MV: <span className="font-semibold">${totalMV.toLocaleString()}</span></div>
          <div className="flex gap-2">
            <button onClick={expandAllLive} className="px-3 py-1 bg-slate-700 rounded">Expand All</button>
            <button onClick={collapseAllLive} className="px-3 py-1 bg-slate-700 rounded">Collapse All</button>
          </div>
        </div>
        {loadingLive && (<div className="text-slate-400">Loading live options...</div>)}
        {errorLive && (<div className="bg-red-900/60 border border-red-700 text-red-200 px-3 py-2 rounded mb-3"><AlertTriangle size={16} className="inline mr-2"/>{errorLive}</div>)}
        {!loadingLive && positionsLive.length === 0 && !errorLive && (<div className="text-slate-400">No live options found.</div>)}

        {positionsLive.length > 0 && (
          <table className="w-full text-sm bg-slate-800 rounded">
            <thead>
              <tr className="border-b border-slate-700 text-slate-300">
                <th className="text-left py-2 px-2">Symbol</th>
                <th className="text-right py-2 px-2">Qty</th>
                <th className="text-right py-2 px-2">Last</th>
                <th className="text-right py-2 px-2">Market Value</th>
                <th className="text-left py-2 px-2">Description</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(grouped).sort().map((sym)=> {
                const rows = grouped[sym];
                const isExpanded = !!expandedLive[sym];
                const qtySum = rows.reduce((s,p)=> s + Math.abs(p.quantity||0), 0);
                const mvSum = rows.reduce((s,p)=> s + (p.market_value||0), 0);
                const last = rows.reduce((s,p)=> s + (p.current_price||0), 0) / rows.length;
                return (
                  <React.Fragment key={sym}>
                    <tr className="border-b border-slate-700 bg-slate-800 hover:bg-slate-700 cursor-pointer" onClick={()=>toggleLive(sym)}>
                      <td className="py-3 px-2"><div className="flex items-center"><ChevronDown className={`w-4 h-4 text-slate-400 mr-2 transition-transform ${isExpanded ? 'rotate-180':'rotate-0'}`}/><span className="text-blue-300 font-bold">{sym}</span></div></td>
                      <td className="text-right py-3 px-2 text-slate-300">{qtySum}</td>
                      <td className="text-right py-3 px-2 text-slate-300">{last.toFixed(2)}</td>
                      <td className="text-right py-3 px-2 text-slate-300">${mvSum.toLocaleString()}</td>
                      <td className="text-left py-3 px-2 text-slate-300">-</td>
                    </tr>
                    {isExpanded && rows.map((p, idx)=> (
                      <tr key={`${sym}-${idx}`} className="border-b border-slate-800">
                        <td className="py-2 px-2 text-slate-200">└ {p.metadata?.contract_symbol}</td>
                        <td className="text-right py-2 px-2">{p.quantity}</td>
                        <td className="text-right py-2 px-2">{p.current_price.toFixed(2)}</td>
                        <td className="text-right py-2 px-2">${(p.market_value||0).toLocaleString()}</td>
                        <td className="text-left py-2 px-2">{p.metadata?.expiration_date} {p.metadata?.strike_price} {p.metadata?.option_type}</td>
                      </tr>
                    ))}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <HeaderBar />
      {activeTab === 'candidates' && <Candidates />}
      {activeTab === 'tradelist' && <TradeList />}
      {activeTab === 'live' && <LivePositions />}
    </div>
  );
}