import React, { useEffect, useMemo, useState } from 'react';
import useDebouncedEffect from '../lib/useDebouncedEffect';
import { priceStrategy } from '../lib/builderApi';

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

// ===== mock data (în Sprint 2 le înlocuim cu API-urile reale pentru expirations/chain) =====
async function fetchExpirations(symbol) {
  await new Promise(r=>setTimeout(r,150));
  return [
    { label:'Oct 25', date:'2025-10-25' },
    { label:'Nov 25', date:'2025-11-25' },
    { label:'Dec 25', date:'2025-12-25' },
  ];
}
async function fetchChainSummary(symbol, expiry) {
  await new Promise(r=>setTimeout(r,150));
  if (!expiry) return { strikes: [], hasData:false };
  return { strikes:[80,85,90,95,100,105,110], hasData:true };
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

// ===== Page =====
export default function BuilderPage() {
  const [symbol, setSymbol] = useState('TSLA');

  const [expirations, setExpirations] = useState([]);
  const [expiry, setExpiry] = useState();
  const [summary, setSummary] = useState({ strikes: [], hasData:false });
  const [strike, setStrike] = useState();

  const [rangePct, setRangePct] = useState(15);
  const [ivPct, setIvPct] = useState(25);

  const [price, setPrice] = useState(null);
  const [pLoading, setPLoading] = useState(false);
  const [error, setError] = useState('');

  // expirations
  useEffect(()=>{
    let alive = true;
    setError('');
    fetchExpirations(symbol)
      .then(r=> alive && setExpirations(r))
      .catch(e=> alive && setError(String(e?.message||e)));
    return ()=>{ alive=false; };
  }, [symbol]);

  // chain summary
  useEffect(()=>{
    let alive = true;
    setError('');
    fetchChainSummary(symbol, expiry)
      .then(r=> alive && setSummary(r))
      .catch(e=> alive && setError(String(e?.message||e)));
    return ()=>{ alive=false; };
  }, [symbol, expiry]);

  // pricing: debounce pentru a nu spama backend-ul
  useDebouncedEffect(()=>{
    if (!symbol || !expiry || !strike) {
      setPrice(null);
      return;
    }
    const payload = {
      symbol,
      expiry,
      legs: [{ type:'CALL', side:'BUY', strike }],   // simplu, 1 leg; extindem ulterior
      rangePct,
      ivPct,
    };
    setPLoading(true);
    setError('');
    priceStrategy(payload)
      .then(data => setPrice(data))
      .catch(e  => setError(String(e?.message||e)))
      .finally(()=> setPLoading(false));
  }, [symbol, expiry, strike, rangePct, ivPct], 350);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <HeaderBar symbol={symbol} onSymbol={setSymbol} error={error} />

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-12">
        {/* stânga */}
        <div className="lg:col-span-8 space-y-6">
          <ExpirationsPanel items={expirations} value={expiry} onChange={setExpiry} />
          <StrikesPanel summary={summary} value={strike} onChange={setStrike} />
          <MetricsBar data={price?.metrics} loading={pLoading} />
          <Card className="p-6 text-center text-sm text-gray-500">Chain area (tabel/grafice) – Sprint 2</Card>
        </div>

        {/* dreapta */}
        <div className="lg:col-span-4 space-y-6">
          <Card className="p-3">
            <SectionTitle title="Strategy" right={<span className="text-xs text-gray-500">0 legs</span>} />
            <div className="text-sm text-gray-700">Long Call</div>
          </Card>

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
