export default function BuilderHeaderV2({
 symbol, 
 meta, 
 sqm, 
 stance, 
 legs = [],
 strategyId = "",
 onCatalog, 
 onHistorical, 
 onTrade
}) {
 const tradeColor = stance === 'bullish' ? 'bg-emerald-600 hover:bg-emerald-700' :
 stance === 'bearish' ? 'bg-rose-600 hover:bg-rose-700' :
 stance === 'directional' ? 'bg-fuchsia-600 hover:bg-fuchsia-700' : 
 'bg-slate-600 hover:bg-slate-700';

 const priceColor = meta?.change >= 0 ? 'text-emerald-400' : 'text-rose-400';
 const changeText = meta?.change >= 0 ? `+$${Math.abs(meta.change).toFixed(2)}` : `-$${Math.abs(meta.change).toFixed(2)}`;
 const changePct = meta?.changePct >= 0 ? `+${meta.changePct.toFixed(1)}%` : `${meta.changePct.toFixed(1)}%`;

 return (
 <div className="flex items-center justify-between py-3 border-b border-slate-800" data-testid="builder-header">
 {/* Left - Symbol + Price */}
 <div className="flex items-center gap-4">
 <div className="text-xl font-medium text-slate-100">
 {symbol}
 {meta?.price && (
 <span className={`ml-3 ${priceColor}`}>
 ${meta.price.toFixed(2)}
 </span>
 )}
 </div>
 {meta?.change && (
 <div className="flex items-center gap-2 text-xl">
 <span className={priceColor}>{changeText}</span>
 <span className={`px-1.5 py-0.5 rounded text-lg ${priceColor} bg-current bg-opacity-10`}>
 {changePct}
 </span>
 <span className="text-lg px-2 py-0.5 rounded bg-slate-700 text-slate-300">
 Real-time
 </span>
 </div>
 )}
 </div>

 {/* Center - Breadcrumbs */}
 <div className="text-xl text-slate-400">
 <span>{legs.length} leg{legs.length !== 1 ? 's' : ''}</span>
 {strategyId && (
 <>
 <span className="mx-2">•</span>
 <span>Strategy: {strategyId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
 </>
 )}
 </div>

 {/* Right - Badges & Buttons */}
 <div className="flex items-center gap-2">
 {/* Mode Badge */}
 <span 
 className={`px-2 py-1 text-lg rounded ${
 meta?.mode === 'LIVE' 
 ? 'bg-emerald-600/20 text-emerald-300' 
 : 'bg-amber-600/20 text-amber-300'
 }`}
 data-badge-mode={meta?.mode || 'DEMO'}
 >
 {meta?.mode ?? 'DEMO'}
 </span>

 {/* SQM Badge */}
 <span 
 className={`px-2 py-1 text-lg rounded border ${
 sqm?.score >= 75 ? 'border-emerald-700 text-emerald-300' :
 sqm?.score >= 50 ? 'border-amber-700 text-amber-300' :
 sqm?.score ? 'border-rose-700 text-rose-300' : 'border-slate-700 text-slate-300'
 }`}
 data-badge-sqm={sqm?.score || 0}
 >
 SQM: {sqm?.score ?? '—'}{sqm?.degraded ? ' (degraded)' : ''}
 </span>

 {/* Action Buttons */}
 <button 
 className="px-3 py-1.5 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 transition-colors text-xl"
 onClick={onCatalog}
 >
 Catalog
 </button>
 
 <button 
 className="px-3 py-1.5 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 transition-colors text-xl"
 onClick={onHistorical}
 >
 Historical
 </button>
 
 <button 
 className={`px-4 py-1.5 rounded text-white font-medium transition-colors text-xl ${tradeColor}`}
 onClick={onTrade}
 data-testid="trade-button"
 data-stance={stance}
 >
 TRADE
 </button>
 </div>
 </div>
 );
}