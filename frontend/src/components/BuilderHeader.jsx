import React, { useState, useMemo, useEffect } from 'react';

// ----- Helpers -----
function clsx(...xs) { 
  return xs.filter(Boolean).join(' ');
}

function fmtUSD(x) { 
  const n = Number(x || 0); 
  const sign = n < 0 ? '-' : ''; 
  return sign + '$' + Math.abs(n).toLocaleString(undefined, {maximumFractionDigits: 2});
}

function fmtPct(x) { 
  return (Number(x || 0) * 100).toFixed(2) + '%';
}

function daysBetween(a, b) { 
  return Math.max(0, Math.round((new Date(b).getTime() - new Date(a).getTime()) / (24 * 3600 * 1000)));
}

// ----- LivePriceTicker -----
export function LivePriceTicker({ 
  symbol, price, changeAbs, changePct, realtime, 
  onToggleAutoRefresh, onInfo 
}) {
  const up = (changeAbs || 0) >= 0;
  const color = up ? 'text-emerald-500' : 'text-rose-500';
  const [open, setOpen] = useState(false);

  return (
    <div className="flex items-center gap-2">
      <div className="px-2.5 py-1 rounded-lg bg-slate-900 text-white font-semibold text-sm tracking-wide">
        {symbol}
      </div>
      <div className="text-xl font-semibold tabular-nums">
        {price != null ? price.toLocaleString(undefined, {maximumFractionDigits: 2}) : '—'}
      </div>
      <div className={clsx('text-sm font-semibold tabular-nums', color)}>
        {changePct != null ? (up ? '+' : '') + fmtPct(changePct) : ''}
      </div>
      <div className={clsx('text-sm font-semibold tabular-nums', color)}>
        {changeAbs != null ? (up ? '+' : '') + fmtUSD(changeAbs) : ''}
      </div>
      <div className="relative">
        <button 
          onClick={() => setOpen(v => !v)} 
          className="ml-1 px-2 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs border flex items-center gap-1" 
          title="Realtime info"
        >
          <span>Real‑time</span>
          <span className="w-4 h-4 inline-flex items-center justify-center rounded-full bg-slate-200 text-[10px]">
            ?
          </span>
        </button>
        {open && (
          <div className="absolute z-20 mt-2 w-80 p-3 rounded-xl bg-white border shadow text-sm text-slate-700">
            <div className="font-semibold mb-1">Data source</div>
            <div>Stocks: NASDAQ real‑time (TS API). Options: OPRA real‑time (UW/TS).</div>
            <div className="mt-2 flex items-center justify-between">
              <div className="text-slate-500">Auto‑refresh</div>
              <button 
                onClick={() => { 
                  onToggleAutoRefresh?.(!realtime); 
                  setOpen(false); 
                }} 
                className="px-3 py-1.5 rounded bg-slate-900 text-white text-xs"
              >
                {realtime ? 'Disable' : 'Enable'}
              </button>
            </div>
          </div>
        )}
      </div>
      <button 
        onClick={onInfo} 
        className="ml-1 w-5 h-5 inline-flex items-center justify-center rounded-full bg-slate-100 text-slate-700" 
        title="What is this strategy?"
      >
        ?
      </button>
    </div>
  );
}

// ----- StrategyTitle -----
export function StrategyTitle({ info }) {
  const [open, setOpen] = useState(false);
  
  return (
    <div className="flex items-center gap-2">
      <div className="text-2xl font-bold">{info.name}</div>
      <div className="relative">
        <button 
          onClick={() => setOpen(v => !v)} 
          className="w-5 h-5 inline-flex items-center justify-center rounded-full bg-slate-100 text-slate-700" 
          title="Strategy info"
        >
          ?
        </button>
        {open && (
          <div className="absolute z-20 mt-2 w-[520px] max-w-[92vw] p-4 rounded-2xl bg-indigo-900 text-indigo-50 shadow-2xl">
            <div className="text-base font-semibold mb-2">{info.name}</div>
            <div className="text-sm leading-5 opacity-95">{info.explain}</div>
            {info.badges?.length ? (
              <div className="mt-2 flex flex-wrap gap-2">
                {info.badges.map(b => (
                  <span 
                    key={b} 
                    className="px-2 py-0.5 rounded-full bg-emerald-600/20 border border-emerald-400/40 text-emerald-200 text-xs"
                  >
                    {b}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

// ----- ExpirationPicker -----
function groupByMonth(exps) {
  const map = new Map(); // key = '2025-09'
  exps.forEach(e => {
    const k = e.iso.slice(0, 7);
    map.set(k, [...(map.get(k) || []), e.iso]);
  });
  return Array.from(map.entries()).sort((a, b) => a[0] < b[0] ? -1 : 1);
}

export function ExpirationPicker({ nowISO, expirations, selected, onSelect }) {
  const groups = useMemo(() => groupByMonth(expirations), [expirations]);
  const dte = selected ? daysBetween(nowISO, selected) : undefined;
  const [month, setMonth] = useState(() => selected?.slice(0, 7) || groups[0]?.[0]);

  useEffect(() => { 
    if (selected) setMonth(selected.slice(0, 7)); 
  }, [selected]);

  return (
    <div className="select-none">
      <div className="text-sm text-slate-500">
        EXPIRATION{dte != null ? `: ${dte}d` : ''}
      </div>
      <div className="mt-1 flex gap-2">
        {groups.map(([ym]) => (
          <button 
            key={ym} 
            onClick={() => setMonth(ym)} 
            className={clsx(
              'px-3 py-1.5 rounded-lg border text-sm', 
              month === ym ? 'bg-slate-900 text-white border-slate-900' : 'bg-slate-100 text-slate-700 border-slate-200'
            )}
          >
            {new Date(ym + '-01').toLocaleString(undefined, {month: 'short'})}
          </button>
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {(groups.find(([ym]) => ym === month)?.[1] || []).map(iso => {
          const day = new Date(iso).getDate();
          const sel = selected === iso;
          return (
            <button 
              key={iso} 
              onClick={() => onSelect(iso)} 
              className={clsx(
                'w-10 h-8 rounded-lg border text-sm', 
                sel ? 'bg-sky-600 text-white border-sky-600' : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
              )}
            >
              {day}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ----- BuilderHeader (compozit) -----
export function BuilderHeader({
  strategy, symbol, price, changeAbs, changePct, realtime,
  expirations, selectedExpiry, nowISO,
  onSelectExpiry,
  onToggleAutoRefresh,
  onClickAdd, onClickPositions, onClickSave, onClickHistorical,
}) {
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <StrategyTitle info={strategy} />
          <LivePriceTicker 
            symbol={symbol} 
            price={price} 
            changeAbs={changeAbs} 
            changePct={changePct} 
            realtime={!!realtime} 
            onToggleAutoRefresh={onToggleAutoRefresh} 
          />
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={onClickAdd} 
            className="px-3 py-1.5 rounded bg-sky-600 text-white text-sm"
          >
            Add +
          </button>
          <button 
            onClick={onClickPositions} 
            className="px-3 py-1.5 rounded bg-slate-100 text-slate-700 text-sm border"
          >
            Positions
          </button>
          <button 
            onClick={onClickSave} 
            className="px-3 py-1.5 rounded bg-indigo-600 text-white text-sm"
          >
            Save Trade
          </button>
          <button 
            onClick={onClickHistorical} 
            className="px-3 py-1.5 rounded bg-slate-900 text-white text-sm"
          >
            Historical Chart
          </button>
        </div>
      </div>

      <div className="mt-3">
        <ExpirationPicker 
          nowISO={nowISO} 
          expirations={expirations} 
          selected={selectedExpiry} 
          onSelect={onSelectExpiry} 
        />
      </div>
    </div>
  );
}

export default BuilderHeader;