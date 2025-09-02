import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area,
} from 'recharts';

// =============== UTILS ====================
const clsx = (...xs) => xs.filter(Boolean).join(' ');
const fmtUSD = (x) => (x < 0 ? '-' : '') + '$' + Math.abs(x).toLocaleString(undefined, {maximumFractionDigits: 2});

// =============== TRADE BUTTON =============
export function TradeButton({ bias, onClick }) {
  const colors = bias === 'Bullish'
    ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
    : bias === 'Bearish'
      ? 'bg-rose-600 hover:bg-rose-700 text-white'
      : 'bg-amber-500 hover:bg-amber-600 text-slate-900';
  
  return (
    <button onClick={onClick} className={clsx('px-4 py-1.5 rounded font-semibold shadow-sm', colors)}>
      TRADE
    </button>
  );
}

// =============== ADD MENU =================
export function AddMenu({ onAdd }) {
  const [open, setOpen] = useState(false);
  
  return (
    <div className="relative">
      <button onClick={() => setOpen(v => !v)} className="px-3 py-1.5 rounded bg-sky-600 text-white text-sm">
        Add +
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-44 bg-white border rounded-lg shadow z-20 text-sm">
          <div className="px-3 py-1 text-slate-500">Options:</div>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('BUY_CALL'); setOpen(false);}}>
            Buy Call
          </button>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('SELL_CALL'); setOpen(false);}}>
            Sell Call
          </button>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('BUY_PUT'); setOpen(false);}}>
            Buy Put
          </button>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('SELL_PUT'); setOpen(false);}}>
            Sell Put
          </button>
          <div className="px-3 py-1 text-slate-500 border-t">Underlying:</div>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('BUY_STK'); setOpen(false);}}>
            Buy STOCK
          </button>
          <button className="w-full px-3 py-1 hover:bg-slate-50 text-left" onClick={() => {onAdd('SELL_STK'); setOpen(false);}}>
            Sell STOCK
          </button>
        </div>
      )}
    </div>
  );
}

// =============== SAVE TRADE MODAL =========
export function SaveTradeModal({ open, onClose, defaultName, onSave }) {
  const [name, setName] = useState(defaultName || '');
  const [notes, setNotes] = useState('');
  const [group, setGroup] = useState('All');
  
  useEffect(() => { 
    if (open) setName(defaultName || ''); 
  }, [open, defaultName]);
  
  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center" onClick={onClose}>
      <div className="bg-[#0b2347] text-white rounded-2xl p-5 w-[680px] max-w-[92vw]" onClick={e => e.stopPropagation()}>
        <div className="text-2xl font-semibold mb-4">Save & Share this Trade</div>
        <div className="space-y-3">
          <div>
            <div className="text-sm opacity-80 mb-1">Trade Name (optional)</div>
            <input 
              value={name} 
              onChange={e => setName(e.target.value)} 
              className="w-full rounded px-3 py-2 bg-white text-slate-900"
            />
          </div>
          <div>
            <div className="text-sm opacity-80 mb-1">Trade Description (optional)</div>
            <textarea 
              rows={4} 
              value={notes} 
              onChange={e => setNotes(e.target.value)} 
              className="w-full rounded px-3 py-2 bg-white text-slate-900"
            />
          </div>
          <div>
            <div className="text-sm opacity-80 mb-1">Group</div>
            <select 
              value={group} 
              onChange={e => setGroup(e.target.value)} 
              className="rounded px-3 py-2 bg-white text-slate-900"
            >
              <option>All</option>
              <option>Income</option>
              <option>Directional</option>
              <option>Hedge</option>
            </select>
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onClose} className="px-3 py-1.5 rounded bg-slate-100 text-slate-800">
            Cancel
          </button>
          <button 
            onClick={() => {onSave({name, notes, group}); onClose();}} 
            className="px-3 py-1.5 rounded bg-sky-600 text-white"
          >
            Save trade
          </button>
        </div>
      </div>
    </div>
  );
}

// =============== POSITIONS MODAL ==========
export function PositionsModal({ 
  open, onClose, positions, onFlip, onResetPrices, 
  pricingMode, setPricingMode, fees, setFees 
}) {
  if (!open) return null;
  
  const unrealized = 0;
  
  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center" onClick={onClose}>
      <div className="bg-white rounded-2xl p-5 w-[640px] max-w-[92vw]" onClick={e => e.stopPropagation()}>
        <div className="text-2xl font-semibold mb-3">Positions</div>
        <div className="flex gap-2 mb-2">
          <button className="px-3 py-1.5 rounded bg-sky-600 text-white text-sm">
            Open ({positions.length})
          </button>
          <button className="px-3 py-1.5 rounded bg-slate-100 text-slate-700 text-sm">
            Closed (0)
          </button>
        </div>
        <div className="text-sm mb-3">Total unrealized gain: {fmtUSD(unrealized)} (0%)</div>
        <div className="border rounded p-2 mb-3 text-sm">
          {positions.map((p, i) => (
            <div key={i} className="py-1">{p.label}</div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
          <button onClick={onFlip} className="px-3 py-2 rounded bg-slate-900 text-white">
            Flip Positions
          </button>
          <button onClick={onResetPrices} className="px-3 py-2 rounded bg-slate-200">
            Reset Custom Prices
          </button>
        </div>
        <div className="mb-3">
          <div className="text-sm mb-1">Pricing Mode</div>
          <div className="flex gap-2">
            <button 
              onClick={() => setPricingMode('Midpoint')} 
              className={clsx('px-3 py-1.5 rounded text-sm', pricingMode === 'Midpoint' ? 'bg-sky-600 text-white' : 'bg-slate-100')}
            >
              Midpoint
            </button>
            <button 
              onClick={() => setPricingMode('BidAsk')} 
              className={clsx('px-3 py-1.5 rounded text-sm', pricingMode === 'BidAsk' ? 'bg-sky-600 text-white' : 'bg-slate-100')}
            >
              Bid / Ask
            </button>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="mb-1">Commissions ($ per trade)</div>
            <input 
              type="number" 
              value={fees.perTrade} 
              onChange={e => setFees({...fees, perTrade: Number(e.target.value)})} 
              className="w-full border rounded px-2 py-1"
            />
          </div>
          <div>
            <div className="mb-1">$ per contract</div>
            <input 
              type="number" 
              value={fees.perContract} 
              onChange={e => setFees({...fees, perContract: Number(e.target.value)})} 
              className="w-full border rounded px-2 py-1"
            />
          </div>
        </div>
        <label className="mt-3 inline-flex items-center gap-2 text-sm">
          <input 
            type="checkbox" 
            checked={fees.roundTrip} 
            onChange={e => setFees({...fees, roundTrip: e.target.checked})}
          />
          Round‑Trip
        </label>
        <div className="mt-4 text-right">
          <button onClick={onClose} className="px-3 py-1.5 rounded bg-slate-100">Close</button>
        </div>
      </div>
    </div>
  );
}

// =============== TS ORDER PAYLOAD =========
export function buildTsOrder({ symbol, expiry, legs }) {
  // Map to a simple TS-like schema
  return {
    symbol,
    expiry, // ISO or yyyymmdd (convert server-side if needed)
    legs: legs.map(L => ({
      action: L.side === 'BUY' ? 'BUY' : 'SELL',
      right: L.type, // CALL/PUT
      strike: L.strike,
      quantity: L.qty,
    })),
  };
}

// =============== HISTORICAL MODAL =========
export function HistoricalChartModal({ open, onClose, data }) {
  const [range, setRange] = useState('1W');
  const [mode, setMode] = useState('candle');
  
  if (!open) return null;

  // Filter by range (very simple)
  const now = Date.now();
  const from = range === 'ALL' ? 0 : 
               range === '3M' ? now - 90 * 864e5 : 
               range === '1M' ? now - 30 * 864e5 : 
               range === '2W' ? now - 14 * 864e5 : 
               range === '1W' ? now - 7 * 864e5 : 
               now - 864e5;
  
  const cand = (data.candles || []).filter(d => d.t >= from);
  const und = (data.underlying || []).filter(d => d.t >= from);
  const iv = (data.iv || []).filter(d => d.t >= from);

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center" onClick={onClose}>
      <div className="bg-[#0a2a4f] rounded-2xl text-white p-4 w-[1000px] max-w-[96vw]" onClick={e => e.stopPropagation()}>
        <div className="text-2xl font-semibold mb-2">Price History</div>
        <div className="h-[380px] bg-[#05203d] rounded-lg p-2">
          <ResponsiveContainer width="100%" height="100%">
            {mode === 'line' ? (
              <LineChart data={(data.strat || []).filter(d => d.t >= from)}>
                <CartesianGrid stroke="#0f2b4a" strokeDasharray="3 3"/>
                <XAxis 
                  dataKey="t" 
                  tickFormatter={(t) => new Date(t).toLocaleTimeString()} 
                  stroke="#8fb7e3"
                />
                <YAxis yAxisId="left" stroke="#8fb7e3"/>
                <YAxis yAxisId="right" orientation="right" stroke="#b48cff"/>
                <Tooltip contentStyle={{background: '#0b2347', border: '1px solid #1e3a5f', color: '#fff'}}/>
                <Line 
                  yAxisId="left" 
                  type="monotone" 
                  dataKey="p" 
                  dot={false} 
                  stroke="#4ade80" 
                  name="Strategy Price"
                />
              </LineChart>
            ) : (
              <CandleOverlay candles={cand} iv={iv}/>
            )}
          </ResponsiveContainer>
        </div>

        <div className="mt-2 text-slate-200">Underlying (symbol)</div>
        <div className="h-[120px] bg-[#05203d] rounded-lg p-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={und}>
              <XAxis dataKey="t" hide/>
              <YAxis hide/>
              <Area type="monotone" dataKey="p" stroke="#60a5fa" fill="#60a5fa22"/>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 flex items-center gap-2">
          {['1D', '1W', '2W', '1M', '3M', 'ALL'].map(r => (
            <button 
              key={r} 
              onClick={() => setRange(r)} 
              className={clsx('px-3 py-1.5 rounded', range === r ? 'bg-sky-600' : 'bg-[#0b2347]')}
            >
              {r === 'ALL' ? 'All Time' : r}
            </button>
          ))}
          <div className="ml-auto flex items-center gap-2">
            <button 
              onClick={() => setMode('line')} 
              className={clsx('px-3 py-1.5 rounded', mode === 'line' ? 'bg-slate-700' : 'bg-[#0b2347]')}
            >
              Line
            </button>
            <button 
              onClick={() => setMode('candle')} 
              className={clsx('px-3 py-1.5 rounded', mode === 'candle' ? 'bg-slate-700' : 'bg-[#0b2347]')}
            >
              Candlestick
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Minimal candlestick renderer using Recharts primitives
function CandleOverlay({ candles, iv }) {
  // Convert to a dataset with OHLC + IV
  const data = candles.map(c => ({
    ...c, 
    iv: iv.find(i => Math.abs(i.t - c.t) < 60e3)?.v
  }));
  
  return (
    <LineChart data={data}>
      <CartesianGrid stroke="#0f2b4a" strokeDasharray="3 3"/>
      <XAxis 
        dataKey="t" 
        tickFormatter={(t) => new Date(t).toLocaleDateString()} 
        stroke="#8fb7e3"
      />
      <YAxis yAxisId="left" stroke="#8fb7e3"/>
      <YAxis yAxisId="right" orientation="right" stroke="#b48cff"/>
      <Tooltip contentStyle={{background: '#0b2347', border: '1px solid #1e3a5f', color: '#fff'}}/>
      <Line yAxisId="right" type="monotone" dataKey="iv" stroke="#a78bfa" dot={false} name="IV"/>
    </LineChart>
  );
}

// =============== ACTIONS BAR ==============
export function ActionsBar({
  strategy, legs, symbol, expiry,
  onAdd, onOpenPositions, onOpenSave, onOpenHistorical, onPlaceTs
}) {
  function handleTrade() {
    const order = buildTsOrder({ symbol, expiry, legs });
    onPlaceTs(order);
  }
  
  return (
    <div className="flex items-center gap-2">
      <AddMenu onAdd={onAdd} />
      <button onClick={onOpenPositions} className="px-3 py-1.5 rounded bg-slate-100 text-slate-700 text-sm">
        Positions
      </button>
      <button onClick={onOpenSave} className="px-3 py-1.5 rounded bg-indigo-600 text-white text-sm">
        Save Trade
      </button>
      <button onClick={onOpenHistorical} className="px-3 py-1.5 rounded bg-slate-900 text-white text-sm">
        Historical Chart
      </button>
      <TradeButton bias={strategy.bias} onClick={handleTrade} />
    </div>
  );
}

export default ActionsBar;