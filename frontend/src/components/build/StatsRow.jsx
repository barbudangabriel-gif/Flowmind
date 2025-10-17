function Stat({ label, val, className = "" }) {
 return (
 <div className={`text-center ${className}`}>
 <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">
 {label}
 </div>
 <div className="text-xl font-medium text-slate-200">
 {val}
 </div>
 </div>
 );
}

function fmt$(amount) {
 if (amount == null) return '—';
 const abs = Math.abs(amount);
 if (abs >= 1000) {
 return (amount < 0 ? '-' : '') + '$' + (abs / 1000).toFixed(1) + 'k';
 }
 return (amount < 0 ? '-' : '') + '$' + abs.toFixed(0);
}

function fmtPct(decimal) {
 if (decimal == null) return '—';
 return `${(decimal * 100).toFixed(1)}%`;
}

export default function StatsRow({ p }) {
 if (!p) return null;

 const netDebit = p.net_credit ? -p.net_credit : p.net_debit || 0;
 const maxProfit = p.max_profit === Infinity || p.max_profit === Number.POSITIVE_INFINITY 
 ? 'Infinite' 
 : fmt$(p.max_profit);

 const breakevens = p.breakevens || [];
 const breakeven = breakevens.length === 1 
 ? `$${breakevens[0].toFixed(2)}` 
 : breakevens.length > 1 
 ? `${breakevens.length} levels`
 : '—';

 return (
 <div className="grid grid-cols-5 gap-4 py-3 px-4 bg-slate-900/30 rounded-lg border border-slate-800" data-testid="metrics-row">
 <Stat 
 label="Net Debit" 
 val={fmt$(netDebit)}
 className={netDebit > 0 ? 'text-rose-300' : netDebit < 0 ? 'text-emerald-300' : ''}
 />
 <Stat 
 label="Max Loss" 
 val={fmt$(p.max_loss)} 
 className="text-rose-300"
 />
 <Stat 
 label="Max Profit" 
 val={maxProfit} 
 className="text-emerald-300"
 />
 <Stat 
 label="Chance of Profit" 
 val={fmtPct(p.chance_profit)} 
 />
 <Stat 
 label="Breakeven" 
 val={breakeven} 
 />
 </div>
 );
}