// src/components/build/BuildPopupSimple.jsx
import React, { useState, useEffect, useRef } from "react";
import { ALL_STRATEGIES } from "../../data/strategies";
import { renderMiniPayoff, getPreviewType } from "../../utils/payoffPreview";

const LEVELS = ["Novice", "Intermediate", "Advanced", "Expert"];

export default function BuildPopupSimple({ open, onClose, symbol = "TSLA" }) {
 const [hover, setHover] = useState(null);
 const popupRef = useRef(null);

 // Închidere cu ESC / click afară
 useEffect(() => {
 if (!open) return;
 const onKey = (e) => { 
 if (e.key === "Escape") onClose?.(); 
 };
 const onClickAway = (e) => {
 if (popupRef.current && !popupRef.current.contains(e.target)) {
 onClose?.();
 }
 };
 window.addEventListener("keydown", onKey);
 window.addEventListener("mousedown", onClickAway);
 return () => {
 window.removeEventListener("keydown", onKey);
 window.removeEventListener("mousedown", onClickAway);
 };
 }, [open, onClose]);

 if (!open) return null;

 // Group strategies by level
 const strategiesByLevel = {};
 LEVELS.forEach(level => {
 strategiesByLevel[level] = ALL_STRATEGIES.filter(s => 
 s.level?.toLowerCase() === level.toLowerCase()
 );
 });

 return (
 <div className="fixed inset-0 z-[9999] bg-black/40 backdrop-blur-sm" data-testid="catalog-modal">
 <div
 className="mx-auto mt-12 w-[980px] max-w-[98vw] rounded-2xl bg-slate-900/95 ring-1 ring-white/10 shadow-2xl border border-slate-800"
 ref={popupRef}
 >
 {/* Header */}
 <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
 <h2 className="text-3xl font-medium text-white">Build — Strategy Catalog</h2>
 <button
 onClick={onClose}
 className="px-3 py-1.5 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
 >
 Close ✕
 </button>
 </div>

 {/* 4-Column Grid */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 px-6 py-5">
 {LEVELS.map((level) => (
 <div key={level}>
 <h3 className={`font-medium mb-3 text-xl ${
 level === 'Novice' ? 'text-blue-400' :
 level === 'Intermediate' ? 'text-yellow-400' :
 level === 'Advanced' ? 'text-orange-400' : 'text-red-400'
 }`}>
 {level}
 <span className="ml-2 text-lg px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
 {strategiesByLevel[level]?.length || 0}
 </span>
 </h3>
 
 <ul className="space-y-1">
 {(strategiesByLevel[level] || []).map((strategy) => (
 <li key={strategy.id}>
 <a
 href={`/build/${strategy.id}`}
 onMouseEnter={() => setHover(strategy)}
 className="block text-xl text-sky-300 hover:text-emerald-300 hover:underline transition-colors py-0.5 px-1 -mx-1 rounded hover:bg-slate-800/50"
 title={`${strategy.name} - ${strategy.stance} strategy`}
 onClick={(e) => {
 if (e.shiftKey) {
 e.preventDefault();
 window.open(`/build/${strategy.id}`, "_blank", "noopener,noreferrer");
 }
 }}
 >
 {strategy.name}
 </a>
 </li>
 ))}
 </ul>
 </div>
 ))}
 </div>

 {/* Preview Section */}
 <div className="border-t border-white/10 px-6 py-4 bg-slate-900/50">
 {!hover ? (
 <div className="text-white/60 text-xl flex items-center justify-center py-8">
 <div className="text-center">
 <div className="text-2xl mb-2">👆 Hover over a strategy above</div>
 <div>to see description and preview</div>
 </div>
 </div>
 ) : (
 <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
 {/* Preview Chart - Real Payoff Diagram */}
 <div className="lg:col-span-1">
 {renderMiniPayoff({
 ...hover,
 preview: hover.preview || getPreviewType(hover.id)
 }, 240, 140)}
 </div>
 
 {/* Strategy Details */}
 <div className="lg:col-span-2">
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
 
 {/* Action Button */}
 <a
 className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
 hover.stance === 'bullish' ? 'bg-emerald-600 hover:bg-emerald-500 text-white' :
 hover.stance === 'bearish' ? 'bg-rose-600 hover:bg-rose-500 text-white' :
 hover.stance === 'neutral' ? 'bg-slate-600 hover:bg-slate-500 text-white' :
 'bg-fuchsia-600 hover:bg-fuchsia-500 text-white'
 }`}
 href={`/build/${hover.id}`}
 onClick={onClose}
 >
 Open in Builder →
 </a>
 </div>
 </div>
 )}
 </div>
 
 {/* Footer */}
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