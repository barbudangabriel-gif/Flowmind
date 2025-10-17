// src/components/build/BuildPopup.jsx
import React, { useMemo, useRef, useState, useEffect } from "react";
import { ALL_STRATEGIES } from "../../data/strategies";
import { renderMiniPayoff, getPreviewType } from "../../utils/payoffPreview";

const LEVELS = ["Novice", "Intermediate", "Advanced", "Expert"];

function byLevel(items, level) {
 return items.filter(s => (s.level || "").toLowerCase() === level.toLowerCase());
}

function byGroup(items) {
 // Grupează strategiile pe categorii
 return items.reduce((acc, s) => {
 const g = s.group || getGroupFromTags(s.tags) || "Other";
 (acc[g] ||= []).push(s);
 return acc;
 }, {});
}

// Helper pentru a deduce grupa din tags când nu e specificată
function getGroupFromTags(tags = []) {
 if (tags.includes('income') || tags.includes('covered')) return 'Income';
 if (tags.includes('credit') && tags.includes('vertical')) return 'Spreads';
 if (tags.includes('debit') && tags.includes('vertical')) return 'Spreads';
 if (tags.includes('neutral')) return 'Multi-Leg';
 if (tags.includes('hedge')) return 'Protection';
 if (tags.includes('vol') || tags.includes('vega+')) return 'Volatility';
 if (tags.includes('time')) return 'Time Decay';
 if (tags.includes('ratio')) return 'Ratio';
 if (tags.includes('arbitrage')) return 'Arbitrage';
 return 'Basic';
}

function deepLink(strategy, symbol = "TSLA") {
 // Folosește buildParams dacă există, altfel fallback generic
 let payload;
 
 if (strategy.buildParams) {
 payload = {
 symbol,
 ...strategy.buildParams(symbol),
 meta: { from: "popup", stance: strategy.stance || "neutral", level: strategy.level }
 };
 } else {
 payload = {
 symbol,
 strategyId: strategy.id,
 legs: [],
 params: { iv_mult: 1.0, range_pct: 0.15 },
 meta: { from: "popup", stance: strategy.stance || "neutral", level: strategy.level }
 };
 }
 
 try {
 const b64 = btoa(JSON.stringify(payload)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
 return `/build/${strategy.id}?s=${b64}`;
 } catch (error) {
 console.warn('Deep link encoding failed:', error);
 return `/build/${strategy.id}`;
 }
}

export default function BuildPopup({ open, onClose, symbol = "TSLA" }) {
 const [hover, setHover] = useState(null);
 const popupRef = useRef(null);

 // închidere cu ESC / click în afara
 useEffect(() => {
 if (!open) return;
 const onKey = (e) => { if (e.key === "Escape") onClose?.(); };
 const onClickAway = (e) => { 
 if (popupRef.current && !popupRef.current.contains(e.target)) onClose?.(); 
 };
 window.addEventListener("keydown", onKey);
 window.addEventListener("mousedown", onClickAway);
 return () => { 
 window.removeEventListener("keydown", onKey); 
 window.removeEventListener("mousedown", onClickAway); 
 };
 }, [open, onClose]);

 const cols = useMemo(() => {
 const map = {};
 LEVELS.forEach(level => {
 const items = byLevel(ALL_STRATEGIES, level);
 const grouped = byGroup(items);
 map[level] = Object.entries(grouped) // [["Basic",[..]], ...]
 .sort((a, b) => a[0].localeCompare(b[0]));
 });
 return map;
 }, []);

 if (!open) return null;

 return (
 <div className="fixed inset-0 z-[70] bg-black/40 backdrop-blur-sm">
 <div
 className="mx-auto mt-12 w-[980px] max-w-[98vw] rounded-2xl bg-slate-900/95 ring-1 ring-white/10 shadow-2xl border border-slate-800"
 ref={popupRef}
 >
 {/* Header */}
 <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
 <div className="text-3xl font-medium text-white">Build — Strategy Catalog</div>
 <button
 onClick={onClose}
 className="px-3 py-1.5 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
 >
 Close ✕
 </button>
 </div>

 {/* Grid pe 4 coloane */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 px-6 py-5">
 {LEVELS.map((lvl) => (
 <div key={lvl}>
 <div className={`font-medium mb-3 text-xl ${
 lvl === 'Novice' ? 'text-blue-400' :
 lvl === 'Intermediate' ? 'text-yellow-400' :
 lvl === 'Advanced' ? 'text-orange-400' : 'text-red-400'
 }`}>
 {lvl}
 <span className="ml-2 text-lg px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
 {byLevel(ALL_STRATEGIES, lvl).length}
 </span>
 </div>
 
 {cols[lvl].map(([group, items]) => (
 <div key={group} className="mb-4">
 <div className="text-sky-300 text-lg font-medium uppercase tracking-wide mb-2">
 {group}
 </div>
 <ul className="space-y-1">
 {items.map((s) => (
 <li key={s.id}>
 <a
 href={deepLink(s, symbol)}
 onMouseEnter={() => setHover(s)}
 onFocus={() => setHover(s)}
 onMouseLeave={() => {}} // Keep hover until new strategy
 className="block text-xl text-sky-300 hover:text-emerald-300 hover:underline transition-colors py-0.5 px-1 -mx-1 rounded hover:bg-slate-800/50"
 title={`${s.name} - ${s.stance} strategy`}
 onClick={(e) => {
 // Shift+Click → deschide în tab nou
 if (e.shiftKey) {
 e.preventDefault();
 window.open(deepLink(s, symbol), "_blank", "noopener,noreferrer");
 }
 }}
 >
 {s.name}
 </a>
 </li>
 ))}
 </ul>
 </div>
 ))}
 </div>
 ))}
 </div>

 {/* Preview la hover */}
 <div className="border-t border-white/10 px-6 py-4 bg-slate-900/50">
 {!hover ? (
 <div className="text-white/60 text-xl flex items-center justify-center py-8">
 <div className="text-center">
 <div className="text-2xl mb-2">👆 Hover over a strategy above</div>
 <div>to see description and payoff preview</div>
 </div>
 </div>
 ) : (
 <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
 {/* Diagrama mini (2 coloane) */}
 <div className="lg:col-span-2">
 {renderMiniPayoff({
 ...hover,
 preview: hover.preview || getPreviewType(hover.id)
 }, 280, 140)}
 </div>
 
 {/* Text info (3 coloane) */}
 <div className="lg:col-span-3">
 <div className="flex items-center gap-3 mb-3">
 <h3 className="text-white font-medium text-3xl">{hover.name}</h3>
 <span className={`px-2 py-1 rounded text-lg font-medium ${
 hover.stance === 'bullish' ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-400/30' :
 hover.stance === 'bearish' ? 'bg-rose-500/15 text-rose-300 border border-rose-400/30' :
 hover.stance === 'neutral' ? 'bg-slate-500/15 text-slate-300 border border-slate-400/30' :
 'bg-fuchsia-500/15 text-fuchsia-300 border border-fuchsia-400/30'
 }`}>
 {hover.stance?.toUpperCase() || "NEUTRAL"}
 </span>
 </div>
 
 {/* Bullets */}
 {hover.bullets && hover.bullets.length > 0 && (
 <div className="mb-4">
 <ul className="text-white/80 text-xl space-y-1">
 {hover.bullets.slice(0, 4).map((bullet, i) => (
 <li key={i} className="flex items-start gap-2">
 <span className="text-emerald-400 mt-1">•</span>
 <span>{bullet}</span>
 </li>
 ))}
 </ul>
 </div>
 )}
 
 {/* Tags */}
 {hover.tags && hover.tags.length > 0 && (
 <div className="flex flex-wrap gap-2 mb-4">
 {hover.tags.slice(0, 6).map(tag => (
 <span key={tag} className="px-2 py-1 rounded text-lg bg-white/10 border border-white/15 text-white/80">
 {tag}
 </span>
 ))}
 </div>
 )}
 
 {/* Action button */}
 <a
 className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
 hover.stance === 'bullish' ? 'bg-emerald-600 hover:bg-emerald-500 text-white' :
 hover.stance === 'bearish' ? 'bg-rose-600 hover:bg-rose-500 text-white' :
 hover.stance === 'neutral' ? 'bg-slate-600 hover:bg-slate-500 text-white' :
 'bg-fuchsia-600 hover:bg-fuchsia-500 text-white'
 }`}
 href={deepLink(hover, symbol)}
 onClick={onClose}
 >
 Open in Builder →
 </a>
 </div>
 </div>
 )}
 </div>
 
 {/* Footer hint */}
 <div className="border-t border-white/10 px-6 py-3 bg-slate-900/30">
 <div className="flex items-center justify-between text-lg text-slate-400">
 <div className="flex items-center gap-4">
 <span>Symbol: <span className="text-slate-300 font-mono">{symbol}</span></span>
 <span>Total: <span className="text-slate-300">{ALL_STRATEGIES.length} strategies</span></span>
 </div>
 <div>
 Hint: Hold <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">Shift</kbd> to open in new tab
 </div>
 </div>
 </div>
 </div>
 </div>
 );
}