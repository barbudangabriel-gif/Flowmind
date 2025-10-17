import React from 'react';

// Utils
const fmtPct = (x) => (x == null || Number.isNaN(x) ? "-" : (x * 100).toFixed(1) + "%");
const fmtNum = (x, decimals = 2) => (x == null || Number.isNaN(x) ? "-" : x.toFixed(decimals));

function Metric({ label, value }) {
 return (
 <div className="flex flex-col">
 <div className="text-[11px] uppercase tracking-wide text-gray-400">{label}</div>
 <div className="text-2xl font-medium text-gray-900">{value}</div>
 </div>
 );
}

function Badge({ children, kind = "neutral" }) {
 const map = {
 neutral: "bg-gray-200 text-gray-700",
 warning: "bg-amber-200 text-amber-900",
 success: "bg-emerald-200 text-emerald-900",
 };
 return (
 <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-lg font-medium ${map[kind]}`}>
 {children}
 </span>
 );
}

export default function BacktestCard({ backtest, className = "", sampleMin = 30 }) {
 if (!backtest) {
 return (
 <div className={`rounded-2xl border border-gray-200 bg-white p-3 text-xl text-gray-500 ${className}`}>
 <div className="flex items-center gap-2">
 <Badge kind="neutral">no backtest</Badge>
 <span>Nu există backtest pentru această strategie.</span>
 </div>
 </div>
 );
 }

 const n = backtest.n ?? 0;
 const lowSample = n < sampleMin;
 const isVerified = backtest.kind === "verified/chain";
 const badgeText = isVerified ? "verified" : "proxy";
 const badgeClass = isVerified ? "bg-emerald-600" : "bg-amber-600";

 return (
 <div className={`rounded-2xl border border-gray-200 bg-white p-4 shadow-sm ${className}`}>
 <div className="flex items-center justify-between mb-2">
 <div className="flex items-center gap-2">
 <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-lg font-medium text-[rgb(252, 251, 255)] ${badgeClass}`}>
 {badgeText}
 </span>
 {backtest.cache && (
 <span className="text-[11px] text-gray-400">cache: {backtest.cache}</span>
 )}
 </div>
 <div className="text-lg text-gray-500">N = {n}</div>
 </div>

 {lowSample ? (
 <div className="text-xl text-gray-600 flex items-center gap-2">
 <Badge kind="warning">low sample</Badge>
 <span>Metricele sunt orientative (N &lt; {sampleMin}).</span>
 </div>
 ) : (
 <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xl">
 <Metric label="WinRate" value={fmtPct(backtest.win_rate)} />
 <Metric label="Expectancy" value={fmtNum(backtest.expectancy)} />
 <Metric label="PF" value={fmtNum(backtest.pf)} />
 <Metric label="MaxDD" value={fmtNum(backtest.max_dd)} />
 <Metric label="Med. Hold" value={`${fmtNum(backtest.hold_med_days, 0)}d`} />
 </div>
 )}

 {backtest.notes && backtest.notes.length > 0 && (
 <div className="mt-3 flex flex-wrap gap-1">
 {backtest.notes.slice(0, 4).map((n, i) => (
 <span key={i} className="text-[11px] rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">
 {n}
 </span>
 ))}
 </div>
 )}
 </div>
 );
}