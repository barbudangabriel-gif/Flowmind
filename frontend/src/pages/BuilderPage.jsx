import React, { useEffect, useMemo, useState } from 'react';
import Plot from 'react-plotly.js';
import useDebouncedEffect from '../lib/useDebouncedEffect';
import { priceStrategy, getExpirations, getOptionsChain } from '../lib/builderApi';

// ===== UI helpers (neutru, fără culori) =====
const Card = (p) => <div {...p} className={'rounded-xl border border-gray-300 bg-white ' + (p.className||'')} />;
const SectionTitle = ({ title, right }) => (
  <div className="flex items-center justify-between py-2">
    <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
    {right}
  </div>
);
const Button = ({ className='', ...p }) => (
  <button {...p} className={'h-9 px-3 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-60 ' + className} />
);
const Segmented = ({ value, items, onChange }) => (
  <div role="tablist" className="inline-flex overflow-hidden rounded-lg border border-gray-300">
    {items.map(x => (
      <button key={x} role="tab" aria-selected={value===x}
        onClick={()=>onChange(x)}
        className={'px-3 py-1 text-sm ' + (value===x?'bg-gray-200':'bg-white hover:bg-gray-50')}>
        {x}
      </button>
    ))}
  </div>
);

// ===== Helper functions =====
function formatExpiration(dateStr) {
  // Convert "2025-10-25" to "Oct 25"
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

async function fetchExpirationsFromAPI(symbol) {
  try {
    const response = await getExpirations(symbol);
    if (response.status === 'success' && response.data?.expirations) {
      return response.data.expirations.map(date => ({
        label: formatExpiration(date),
        date: date
      }));
    }
    // Fallback to mock data if API fails
    return [
      { label:'Oct 25', date:'2025-10-25' },
      { label:'Nov 25', date:'2025-11-25' },
      { label:'Dec 25', date:'2025-12-25' },
    ];
  } catch (err) {
    console.error('Failed to fetch expirations:', err);
    // Return mock data on error
    return [
      { label:'Oct 25', date:'2025-10-25' },
      { label:'Nov 25', date:'2025-11-25' },
      { label:'Dec 25', date:'2025-12-25' },
    ];
  }
}

async function fetchChainFromAPI(symbol, expiry) {
  if (!expiry) return { strikes: [], hasData: false };
  
  try {
    const response = await getOptionsChain(symbol, expiry);
    if (response.status === 'success' && response.data?.strikes) {
      const strikes = response.data.strikes.map(s => s.strike).sort((a,b) => a-b);
      return { strikes, hasData: strikes.length > 0, fullData: response.data };
    }
    // Fallback to mock
    return { strikes: [80,85,90,95,100,105,110], hasData: true };
  } catch (err) {
    console.error('Failed to fetch options chain:', err);
    return { strikes: [80,85,90,95,100,105,110], hasData: true };
  }
}

// ===== Header =====
function HeaderBar({ symbol, onSymbol, error }) {
  return (
    <div className="sticky top-0 z-10 border-b border-gray-200 bg-gray-50/60 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Segmented value={'Build'} items={['Build','Optimize','Flow']} onChange={()=>{}} />
            <div className="h-6 w-px bg-gray-300" />
            <input
              aria-label="Symbol"
              value={symbol}
              onChange={(e)=>onSymbol(e.target.value.toUpperCase())}
              className="h-9 w-32 rounded-md border border-gray-300 bg-white px-3"
              placeholder="Symbol"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button>Demo</Button>
            <Segmented value={'SQM'} items={['SQM','RAW']} onChange={()=>{}} />
          </div>
        </div>

        {error && (
          <div className="mt-3 rounded-md border border-gray-300 bg-white p-2 text-sm text-gray-700">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

// ===== Panels =====
function ExpirationsPanel({ items, value, onChange }) {
  return (
    <Card className="p-3">
      <SectionTitle title="Expirations" />
      {items.length===0 ? (
        <div className="py-6 text-sm text-gray-500">No expirations available</div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {items.map(x=>(
            <button key={x.date}
              onClick={()=>onChange(x.date)}
              className={'h-9 rounded-lg border border-gray-300 bg-white px-3 text-sm hover:bg-gray-50 ' + (value===x.date?'outline outline-2 outline-gray-400':'')}>
              {x.label}
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}

function StrikesPanel({ summary, value, onChange }) {
  return (
    <Card className="p-3">
      <SectionTitle title="Strike Prices" />
      {summary.hasData ? (
        <div className="flex flex-wrap gap-2">
          {summary.strikes.map(s=>(
            <button key={s}
              onClick={()=>onChange(s)}
              className={'h-9 rounded-md border border-gray-300 bg-white px-3 text-sm hover:bg-gray-50 ' + (value===s?'outline outline-2 outline-gray-400':'')}>
              {s}
            </button>
          ))}
        </div>
      ) : (
        <div className="py-8 text-center text-sm text-gray-500">No options chain available</div>
      )}
    </Card>
  );
}

function MetricsBar({ data, loading }) {
  const items = useMemo(()=>[
    { k:'Net Debit', v: data?.netDebit ?? '$0' },
    { k:'Max Loss', v: data?.maxLoss ?? '$0' },
    { k:'Max Profit', v: data?.maxProfit ?? '$0' },
    { k:'Chance of Profit', v: data?.prob ?? '—' },
    { k:'Breakeven', v: data?.breakeven ?? '—' },
  ], [data]);
  return (
    <Card className="p-0 overflow-hidden">
      <div className="grid grid-cols-2 gap-px md:grid-cols-5">
        {items.map(x=>(
          <div key={x.k} className="p-3">
            <div className="text-xs text-gray-500">{x.k}</div>
            <div className="text-base font-medium text-gray-900">
              {loading ? '…' : x.v}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function GreeksPanel({ data, loading }) {
  const items = [
    { k:'Delta', v: data?.delta ?? '0.0000' },
    { k:'Gamma', v: data?.gamma ?? '—' },
    { k:'Vega',  v: data?.vega  ?? '—' },
    { k:'Rho',   v: data?.rho   ?? '—' },
  ];
  return (
    <Card className="p-3">
      <SectionTitle title="Greeks" />
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {items.map(x=>(
          <div key={x.k} className="rounded-lg border border-gray-200 p-3">
            <div className="text-xs text-gray-500">{x.k}</div>
            <div className="text-sm font-medium text-gray-900">{loading ? '…' : x.v}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function SliderRow({ label, value, onChange, min=0, max=100, step=1 }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="w-56 text-sm text-gray-700">{label}</div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e)=>onChange(Number(e.target.value))}
        className="flex-1" aria-label={label} />
      <div className="w-16 text-right text-sm tabular-nums text-gray-700">{value}%</div>
    </div>
  );
}

function StrategyPanel({ legs, onAddLeg, onRemoveLeg, onUpdateLeg }) {
  const [type, setType] = useState('CALL');
  const [side, setSide] = useState('BUY');
  const [strike, setStrike] = useState('');
  const [qty, setQty] = useState(1);

  const handleAdd = () => {
    if (!strike) return;
    onAddLeg({ 
      type, 
      side, 
      strike: Number(strike), 
      qty: Number(qty),
      id: Date.now() // Simple unique ID
    });
    setStrike('');
  };

  return (
    <Card className="p-3">
      <SectionTitle 
        title="Strategy" 
        right={<span className="text-xs text-gray-500">{legs.length} leg{legs.length !== 1 ? 's' : ''}</span>} 
      />
      
      {/* Existing legs */}
      {legs.length > 0 && (
        <div className="mb-3 space-y-2">
          {legs.map((leg, idx) => (
            <div key={leg.id || idx} className="flex items-center justify-between rounded-lg border border-gray-200 p-2">
              <div className="flex-1 text-sm">
                <span className={leg.side === 'BUY' ? 'text-green-600' : 'text-red-600'}>
                  {leg.side}
                </span>
                {' '}
                {leg.qty}x {leg.type} @ ${leg.strike}
              </div>
              <button 
                onClick={() => onRemoveLeg(leg.id || idx)}
                className="text-xs text-gray-500 hover:text-red-600"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new leg */}
      <div className="space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <select 
            value={type} 
            onChange={(e) => setType(e.target.value)}
            className="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm"
          >
            <option value="CALL">Call</option>
            <option value="PUT">Put</option>
          </select>
          <select 
            value={side} 
            onChange={(e) => setSide(e.target.value)}
            className="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm"
          >
            <option value="BUY">Buy</option>
            <option value="SELL">Sell</option>
          </select>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            placeholder="Strike"
            value={strike}
            onChange={(e) => setStrike(e.target.value)}
            className="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm"
          />
          <input
            type="number"
            placeholder="Qty"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
            min="1"
            className="h-9 rounded-md border border-gray-300 bg-white px-2 text-sm"
          />
        </div>
        
        <Button onClick={handleAdd} className="w-full">
          Add Leg
        </Button>
      </div>
    </Card>
  );
}

function PnLChart({ data, loading }) {
  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12 text-sm text-gray-500">
          Loading P&L chart...
        </div>
      </Card>
    );
  }

  if (!data?.pnlData || data.pnlData.length === 0) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12 text-sm text-gray-500">
          Add legs to see P&L chart
        </div>
      </Card>
    );
  }

  // Prepare Plotly data
  const spotPrices = data.pnlData.map(point => point[0]);
  const pnlValues = data.pnlData.map(point => point[1]);

  const plotData = [{
    x: spotPrices,
    y: pnlValues,
    type: 'scatter',
    mode: 'lines',
    line: { 
      color: '#3b82f6', 
      width: 2 
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(59, 130, 246, 0.1)',
    name: 'P&L'
  }];

  // Add breakeven lines
  if (data.breakevens && data.breakevens.length > 0) {
    data.breakevens.forEach((be, idx) => {
      plotData.push({
        x: [be, be],
        y: [Math.min(...pnlValues), Math.max(...pnlValues)],
        type: 'scatter',
        mode: 'lines',
        line: { 
          color: '#10b981', 
          width: 1, 
          dash: 'dash' 
        },
        showlegend: idx === 0,
        name: 'Breakeven'
      });
    });
  }

  const layout = {
    autosize: true,
    margin: { l: 60, r: 20, t: 20, b: 50 },
    xaxis: { 
      title: 'Spot Price ($)',
      gridcolor: '#e5e7eb'
    },
    yaxis: { 
      title: 'Profit/Loss ($)',
      gridcolor: '#e5e7eb',
      zeroline: true,
      zerolinecolor: '#9ca3af',
      zerolinewidth: 2
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif', size: 12 },
    hovermode: 'x unified',
    showlegend: true,
    legend: { 
      x: 0.02, 
      y: 0.98, 
      bgcolor: 'rgba(255,255,255,0.8)',
      bordercolor: '#e5e7eb',
      borderwidth: 1
    }
  };

  const config = {
    responsive: true,
    displayModeBar: false
  };

  return (
    <Card className="p-3">
      <SectionTitle title="Profit/Loss Chart" />
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '400px' }}
        useResizeHandler={true}
      />
    </Card>
  );
}

// ===== Page =====
export default function BuilderPage() {
  const [symbol, setSymbol] = useState('TSLA');

  const [expirations, setExpirations] = useState([]);
  const [expiry, setExpiry] = useState();
  const [summary, setSummary] = useState({ strikes: [], hasData:false });
  const [strike, setStrike] = useState();

  const [legs, setLegs] = useState([]);
  const [rangePct, setRangePct] = useState(15);
  const [ivPct, setIvPct] = useState(25);

  const [price, setPrice] = useState(null);
  const [pLoading, setPLoading] = useState(false);
  const [error, setError] = useState('');

  // Strategy management handlers
  const handleAddLeg = (leg) => {
    setLegs(prev => [...prev, leg]);
  };

  const handleRemoveLeg = (legId) => {
    setLegs(prev => prev.filter((l, idx) => (l.id || idx) !== legId));
  };

  const handleUpdateLeg = (legId, updates) => {
    setLegs(prev => prev.map((l, idx) => 
      (l.id || idx) === legId ? { ...l, ...updates } : l
    ));
  };

  // expirations
  useEffect(()=>{
    let alive = true;
    setError('');
    fetchExpirationsFromAPI(symbol)
      .then(r=> alive && setExpirations(r))
      .catch(e=> alive && setError(String(e?.message||e)));
    return ()=>{ alive=false; };
  }, [symbol]);

  // chain summary
  useEffect(()=>{
    let alive = true;
    setError('');
    fetchChainFromAPI(symbol, expiry)
      .then(r=> alive && setSummary(r))
      .catch(e=> alive && setError(String(e?.message||e)));
    return ()=>{ alive=false; };
  }, [symbol, expiry]);

  // pricing: debounce pentru a nu spama backend-ul
  useDebouncedEffect(()=>{
    if (!symbol || !expiry || legs.length === 0) {
      setPrice(null);
      return;
    }
    const payload = {
      symbol,
      expiry,
      legs: legs.map(l => ({ type: l.type, side: l.side, strike: l.strike, qty: l.qty || 1 })),
      rangePct,
      ivPct,
    };
    setPLoading(true);
    setError('');
    priceStrategy(payload)
      .then(data => setPrice(data))
      .catch(e  => setError(String(e?.message||e)))
      .finally(()=> setPLoading(false));
  }, [symbol, expiry, legs, rangePct, ivPct], 350);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <HeaderBar symbol={symbol} onSymbol={setSymbol} error={error} />

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-12">
        {/* stânga */}
        <div className="lg:col-span-8 space-y-6">
          <ExpirationsPanel items={expirations} value={expiry} onChange={setExpiry} />
          <StrikesPanel summary={summary} value={strike} onChange={setStrike} />
          <MetricsBar data={price?.metrics} loading={pLoading} />
          <PnLChart data={price} loading={pLoading} />
        </div>

        {/* dreapta */}
        <div className="lg:col-span-4 space-y-6">
          <StrategyPanel 
            legs={legs}
            onAddLeg={handleAddLeg}
            onRemoveLeg={handleRemoveLeg}
            onUpdateLeg={handleUpdateLeg}
          />

          <GreeksPanel data={price?.greeks} loading={pLoading} />

          <Card className="p-3">
            <SectionTitle title="Parameters" />
            <SliderRow label="Range" value={rangePct} onChange={setRangePct} min={0} max={100} />
            <SliderRow label="Implied Volatility" value={ivPct} onChange={setIvPct} min={0} max={300} />
          </Card>

          <Card className="p-3">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium">Actions</div>
              <div className="flex gap-2">
                <Button>Graph</Button>
                <Button>Table</Button>
                <Button>More</Button>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
