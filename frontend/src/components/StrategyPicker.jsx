import React, { useState, useMemo } from 'react';

// S1-S3 - Comprehensive Options Strategy Catalog
const STRATEGY_CATALOG = [
 // Directional Bullish
 {
 id: 'long-call', name: 'Long Call', category: 'Directional', bias: 'Bullish', nature: 'Debit',
 explain: 'Buy a call option to profit from upward price movement.',
 notes: 'Unlimited profit potential, limited risk to premium paid.',
 legs: [{side: 'BUY', type: 'CALL', strike_offset: 0}]
 },
 {
 id: 'bull-call-spread', name: 'Bull Call Spread', category: 'Directional', bias: 'Bullish', nature: 'Debit',
 explain: 'Buy ATM call, sell OTM call to reduce cost and cap profit.',
 notes: 'Lower cost than long call, but limited profit potential.',
 legs: [{side: 'BUY', type: 'CALL', strike_offset: 0}, {side: 'SELL', type: 'CALL', strike_offset: 1}]
 },
 {
 id: 'bull-put-spread', name: 'Bull Put Spread', category: 'Directional', bias: 'Bullish', nature: 'Credit',
 explain: 'Sell ITM put, buy OTM put to profit from upward movement.',
 notes: 'Net credit received, profit if stock stays above short strike.',
 legs: [{side: 'SELL', type: 'PUT', strike_offset: 0}, {side: 'BUY', type: 'PUT', strike_offset: -1}]
 },

 // Directional Bearish
 {
 id: 'long-put', name: 'Long Put', category: 'Directional', bias: 'Bearish', nature: 'Debit',
 explain: 'Buy a put option to profit from downward price movement.',
 notes: 'High profit potential on downside, limited risk to premium.',
 legs: [{side: 'BUY', type: 'PUT', strike_offset: 0}]
 },
 {
 id: 'bear-put-spread', name: 'Bear Put Spread', category: 'Directional', bias: 'Bearish', nature: 'Debit',
 explain: 'Buy ITM put, sell OTM put to reduce cost.',
 notes: 'Lower cost than long put, but capped profit potential.',
 legs: [{side: 'BUY', type: 'PUT', strike_offset: 0}, {side: 'SELL', type: 'PUT', strike_offset: -1}]
 },
 {
 id: 'bear-call-spread', name: 'Bear Call Spread', category: 'Directional', bias: 'Bearish', nature: 'Credit',
 explain: 'Sell ITM call, buy OTM call to profit from downward movement.',
 notes: 'Net credit received, profit if stock stays below short strike.',
 legs: [{side: 'SELL', type: 'CALL', strike_offset: 0}, {side: 'BUY', type: 'CALL', strike_offset: 1}]
 },

 // Income Strategies
 {
 id: 'covered-call', name: 'Covered Call', category: 'Income', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell call against stock position to generate income.',
 notes: 'Requires 100 shares per contract. Caps upside potential.',
 legs: [{side: 'SELL', type: 'CALL', strike_offset: 1}]
 },
 {
 id: 'cash-secured-put', name: 'Cash-Secured Put', category: 'Income', bias: 'Bullish', nature: 'Credit',
 explain: 'Sell put with cash to secure assignment if needed.',
 notes: 'Generate income while potentially acquiring stock at discount.',
 legs: [{side: 'SELL', type: 'PUT', strike_offset: -1}]
 },
 {
 id: 'wheel-strategy', name: 'Wheel Strategy', category: 'Income', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell puts, if assigned sell calls against shares.',
 notes: 'Combination of CSP and covered call for income generation.',
 legs: [{side: 'SELL', type: 'PUT', strike_offset: -1}]
 },

 // Volatility Strategies
 {
 id: 'long-straddle', name: 'Long Straddle', category: 'Volatility', bias: 'Neutral', nature: 'Debit',
 explain: 'Buy call and put at same strike to profit from big moves.',
 notes: 'Profits from high volatility in either direction.',
 legs: [{side: 'BUY', type: 'CALL', strike_offset: 0}, {side: 'BUY', type: 'PUT', strike_offset: 0}]
 },
 {
 id: 'short-straddle', name: 'Short Straddle', category: 'Volatility', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell call and put at same strike to profit from low volatility.',
 notes: 'Profits if stock stays near strike price. High risk strategy.',
 legs: [{side: 'SELL', type: 'CALL', strike_offset: 0}, {side: 'SELL', type: 'PUT', strike_offset: 0}]
 },
 {
 id: 'long-strangle', name: 'Long Strangle', category: 'Volatility', bias: 'Neutral', nature: 'Debit',
 explain: 'Buy OTM call and put to profit from large moves.',
 notes: 'Cheaper than straddle, needs bigger move to profit.',
 legs: [{side: 'BUY', type: 'CALL', strike_offset: 1}, {side: 'BUY', type: 'PUT', strike_offset: -1}]
 },
 {
 id: 'short-strangle', name: 'Short Strangle', category: 'Volatility', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell OTM call and put to profit from low volatility.',
 notes: 'Profit if stock stays between strikes. Undefined risk.',
 legs: [{side: 'SELL', type: 'CALL', strike_offset: 1}, {side: 'SELL', type: 'PUT', strike_offset: -1}]
 },

 // Advanced/Neutral Strategies
 {
 id: 'iron-condor', name: 'Iron Condor', category: 'Neutral', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell strangle, buy wider strangle for defined risk.',
 notes: 'Profit from low volatility with limited risk and reward.',
 legs: [
 {side: 'SELL', type: 'PUT', strike_offset: -1}, {side: 'BUY', type: 'PUT', strike_offset: -2},
 {side: 'SELL', type: 'CALL', strike_offset: 1}, {side: 'BUY', type: 'CALL', strike_offset: 2}
 ]
 },
 {
 id: 'iron-butterfly', name: 'Iron Butterfly', category: 'Neutral', bias: 'Neutral', nature: 'Credit',
 explain: 'Sell ATM straddle, buy OTM strangle for protection.',
 notes: 'Maximum profit if stock closes exactly at middle strike.',
 legs: [
 {side: 'SELL', type: 'PUT', strike_offset: 0}, {side: 'BUY', type: 'PUT', strike_offset: -2},
 {side: 'SELL', type: 'CALL', strike_offset: 0}, {side: 'BUY', type: 'CALL', strike_offset: 2}
 ]
 },

 // Hedge Strategies
 {
 id: 'protective-put', name: 'Protective Put', category: 'Hedge', bias: 'Neutral', nature: 'Debit',
 explain: 'Buy put to protect long stock position from downside.',
 notes: 'Insurance for stock holdings. Limits downside risk.',
 legs: [{side: 'BUY', type: 'PUT', strike_offset: -1}]
 },
 {
 id: 'collar', name: 'Collar', category: 'Hedge', bias: 'Neutral', nature: 'Credit',
 explain: 'Buy protective put, sell covered call to reduce cost.',
 notes: 'Caps both upside and downside. Often net credit or zero cost.',
 legs: [{side: 'BUY', type: 'PUT', strike_offset: -1}, {side: 'SELL', type: 'CALL', strike_offset: 1}]
 }
];

export function StrategyPicker({ open, onClose, symbol = 'TSLA', expiry = null, chain = null, onDeepLink }) {
 const [q, setQ] = useState('');
 const [bias, setBias] = useState('all');
 const [cat, setCat] = useState('all');
 const [width, setWidth] = useState(5);
 const [dist, setDist] = useState(1);

 // Get spot price for strike calculations
 const spot = useMemo(() => {
 if (!chain?.OptionChains?.[0]?.Strikes?.length) return 250; // Default for TSLA
 // Find ATM strike as proxy for spot
 const strikes = chain.OptionChains[0].Strikes.map(s => s.StrikePrice);
 return strikes.reduce((prev, curr) => 
 Math.abs(curr - spot) < Math.abs(prev - spot) ? curr : prev
 );
 }, [chain]);

 // Filter strategies
 const list = useMemo(() => {
 return STRATEGY_CATALOG.filter(def => {
 if (q && !def.name.toLowerCase().includes(q.toLowerCase()) && 
 !def.explain.toLowerCase().includes(q.toLowerCase())) return false;
 if (bias !== 'all' && def.bias !== bias) return false;
 if (cat !== 'all' && def.category !== cat) return false;
 return true;
 });
 }, [q, bias, cat]);

 // Base64 URL encoding for deep links
 function b64url(obj) {
 const json = JSON.stringify(obj);
 return btoa(json).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
 }

 // Convert strategy definition to actual legs with strikes
 function buildLegs(def) {
 const baseStrike = Math.round(spot / 5) * 5; // Round to nearest $5
 return def.legs.map(legDef => ({
 side: legDef.side,
 type: legDef.type,
 qty: 1,
 strike: baseStrike + (legDef.strike_offset * width * 5) // $5 steps
 }));
 }

 // Generate deep link for strategy
 function deepLink(def) {
 const legs = buildLegs(def);
 const s = b64url({ legs, qty: 1 });
 const href = `/build/${def.id}?symbol=${encodeURIComponent(symbol)}${expiry ? `&expiry=${encodeURIComponent(expiry)}` : ''}&s=${s}`;
 return href;
 }

 if (!open) return null;

 return (
 <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center" onClick={onClose}>
 <div className="bg-white rounded-2xl shadow-2xl w-[1000px] max-w-[96vw] max-h-[90vh] overflow-hidden" onClick={e => e.stopPropagation()}>
 <div className="p-4 border-b flex items-center gap-3">
 <div className="text-3xl font-medium">Strategy Builder — Catalog</div>
 <input 
 value={q} 
 onChange={e => setQ(e.target.value)} 
 placeholder="Search strategies…" 
 className="ml-4 flex-1 border rounded px-3 py-1.5"
 />
 <select 
 value={bias} 
 onChange={e => setBias(e.target.value)} 
 className="border rounded px-2 py-1 text-xl"
 >
 <option value="all">All Biases</option>
 <option>Bullish</option>
 <option>Bearish</option>
 <option>Neutral</option>
 </select>
 <select 
 value={cat} 
 onChange={e => setCat(e.target.value)} 
 className="border rounded px-2 py-1 text-xl"
 >
 <option value="all">All Categories</option>
 <option>Directional</option>
 <option>Income</option>
 <option>Volatility</option>
 <option>Neutral</option>
 <option>Hedge</option>
 </select>
 </div>
 
 <div className="px-4 pt-3 pb-2 text-xl text-slate-600 flex items-center gap-4">
 <div className="flex items-center gap-2">
 Width (steps)
 <input 
 type="range" 
 min={1} 
 max={10} 
 value={width} 
 onChange={e => setWidth(Number(e.target.value))} 
 className="w-40"
 />
 <span className="font-medium w-6 text-right">{width}</span>
 </div>
 <div className="flex items-center gap-2">
 Distance (steps)
 <input 
 type="range" 
 min={1} 
 max={10} 
 value={dist} 
 onChange={e => setDist(Number(e.target.value))} 
 className="w-40"
 />
 <span className="font-medium w-6 text-right">{dist}</span>
 </div>
 <div className="ml-auto text-slate-500">
 Symbol <span className="font-medium">{symbol}</span>
 {expiry ? <> · Exp <span className="font-medium">{expiry.slice(0, 10)}</span></> : null}
 </div>
 </div>

 <div className="p-4 grid md:grid-cols-2 gap-3 overflow-auto max-h-[64vh]">
 {list.map(def => (
 <div key={def.id} className="border rounded-xl p-3 hover:shadow transition">
 <div className="flex items-center gap-2 flex-wrap">
 <div className="font-medium">{def.name}</div>
 <span className="text-lg px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">{def.category}</span>
 <span className={`text-lg px-2 py-0.5 rounded-full ${
 def.nature === 'Credit' ? 'bg-amber-100 text-amber-700' : 
 def.nature === 'Debit' ? 'bg-emerald-100 text-emerald-700' : 
 'bg-sky-100 text-sky-700'
 }`}>
 {def.nature}
 </span>
 <span className="text-lg px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">{def.bias}</span>
 </div>
 <div className="text-xl text-slate-600 mt-1">{def.explain}</div>
 {def.notes && <div className="text-lg text-slate-500 mt-1">{def.notes}</div>}
 <div className="mt-2 flex items-center gap-2 flex-wrap">
 <button 
 onClick={() => onDeepLink(deepLink(def))} 
 className="px-3 py-1.5 rounded bg-slate-900 text-[rgb(252, 251, 255)] text-xl"
 >
 Illustrate in Builder
 </button>
 <a 
 href={deepLink(def)} 
 className="text-xl text-slate-600 underline" 
 target="_self" 
 rel="noreferrer"
 >
 Open
 </a>
 <div className="ml-auto text-lg text-slate-500">
 Legs: {def.legs.map(L => `${L.side} ${L.type}`).join(', ')}
 </div>
 </div>
 </div>
 ))}
 </div>

 <div className="p-3 border-t text-right">
 <button onClick={onClose} className="px-3 py-1.5 rounded bg-slate-100">Close</button>
 </div>
 </div>
 </div>
 );
}

export default StrategyPicker;