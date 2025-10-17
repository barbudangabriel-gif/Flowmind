// ==============================================
// SR-2/3 — Graph Pane Crosshair (prob Split + P/L Tag)
// • Crosshair pe hover: price tag, P/L tag pe curbă
// • Probability split (pBelow | pAbove) calculat BSM cu IV & DTE
// • Drop-in replacement pentru GraphPane din BTG1
// ==============================================
import React, { useState, useRef } from 'react'
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'

// Black-Scholes probability calculation
function probSplit(spot, target, iv, dte) {
 if (!spot || !target || !iv || !dte || dte <= 0) {
 return { pAbove: 0.5, pBelow: 0.5 };
 }
 
 const T = dte / 365; // Convert days to years
 const r = 0.045; // Risk-free rate (4.5%)
 
 // Black-Scholes d2 calculation
 const d2 = (Math.log(spot / target) + (r - 0.5 * iv * iv) * T) / (iv * Math.sqrt(T));
 
 // Standard normal CDF approximation
 function normalCDF(x) {
 return 0.5 * (1 + erf(x / Math.sqrt(2)));
 }
 
 // Error function approximation
 function erf(x) {
 const a1 = 0.254829592;
 const a2 = -0.284496736;
 const a3 = 1.421413741;
 const a4 = -1.453152027;
 const a5 = 1.061405429;
 const p = 0.3275911;
 
 const sign = x < 0 ? -1 : 1;
 x = Math.abs(x);
 
 const t = 1.0 / (1.0 + p * x);
 const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
 
 return sign * y;
 }
 
 const pAbove = normalCDF(d2);
 const pBelow = 1 - pAbove;
 
 return { pAbove, pBelow };
}

export function GraphPaneSR2({ ctx, series, mode, range, iv, dte, showProbability = true }) {
 const [hover, setHover] = useState(null);
 const chartRef = useRef(null);
 
 // recharts expects numbers; we map labels
 const data = series.map(p => ({ x: p.price, v: p.value, prob: p.prob }));
 const yFmt = (v) => (mode === 'pl%' || mode === 'maxrisk' ? 
 (v >= 0 ? '+' : '') + (v * 100).toFixed(0) + '%' : 
 (v < 0 ? '-' : '') + '$' + Math.abs(v).toLocaleString(undefined, {maximumFractionDigits: 0}));
 
 // Create profit/loss paths for fills
 const createProfitLossPaths = () => {
 const profitData = data.filter(p => p.v >= 0);
 const lossData = data.filter(p => p.v < 0);
 return { profitData, lossData };
 };
 
 const { profitData, lossData } = createProfitLossPaths();
 
 const handleMouseMove = (e) => {
 if (!e || !e.activeLabel || !e.activePayload) {
 setHover(null);
 return;
 }
 
 const chartElement = chartRef.current;
 if (!chartElement) return;
 
 // Get proper chart coordinates from Recharts event
 const chartX = e.activeCoordinate?.x || 0;
 const chartY = e.activeCoordinate?.y || 0;
 
 setHover({
 x: parseFloat(e.activeLabel),
 v: e.activePayload[0]?.value || 0,
 chartX: chartX,
 chartY: chartY
 });
 };
 
 const handleMouseLeave = () => {
 setHover(null);
 };

 return (
 <div className="relative h-[360px]" ref={chartRef}>
 <ResponsiveContainer width="100%" height="100%">
 <AreaChart 
 data={data} 
 margin={{left:12,right:12,top:8,bottom:4}}
 onMouseMove={handleMouseMove}
 onMouseLeave={handleMouseLeave}
 >
 <CartesianGrid stroke="#19314f" strokeDasharray="3 3" />
 <XAxis 
 dataKey="x" 
 type="number" 
 domain={[range[0], range[1]]} 
 tickFormatter={(v) => '$' + v.toFixed(0)} 
 stroke="#9fb3c8"
 />
 <YAxis 
 tickFormatter={yFmt} 
 stroke="#9fb3c8"
 />
 <Tooltip 
 formatter={(val) => Array.isArray(val) ? val : yFmt(val)} 
 labelFormatter={(x) => '$' + (x).toFixed(2)} 
 contentStyle={{
 background: '#0b1c33', 
 border: '1px solid #12233f', 
 borderRadius: 12
 }}
 />
 {/* Probability band - back layer with low opacity (conditional) */}
 {showProbability && (
 <Area 
 type="monotone" 
 dataKey="prob" 
 stroke="var(--pl-prob-line, #60a5fa)" 
 fill="var(--pl-prob-fill, rgba(59, 130, 246, 0.16))" 
 opacity={0.8}
 yAxisId={0} 
 />
 )}
 
 {/* Loss region fill */}
 {lossData.length > 0 && (
 <Area 
 type="monotone" 
 data={lossData}
 dataKey="v" 
 stroke="none"
 fill="var(--pl-loss-fill, rgba(239, 68, 68, 0.22))" 
 opacity={0.8}
 />
 )}
 
 {/* Profit region fill */}
 {profitData.length > 0 && (
 <Area 
 type="monotone" 
 data={profitData}
 dataKey="v" 
 stroke="none"
 fill="var(--pl-profit-fill, rgba(34, 197, 94, 0.22))" 
 opacity={0.8}
 />
 )}
 
 {/* P/L payoff line - no fill, just stroke */}
 <Area 
 type="monotone" 
 dataKey="v" 
 stroke="var(--pl-profit-line, #22c55e)"
 fill="none"
 strokeWidth={2.5}
 />
 
 {/* Zero axis with unified styling */}
 <ReferenceLine 
 y={0} 
 stroke="var(--pl-zero-axis, #94a3b8)" 
 strokeDasharray="4 4"
 strokeWidth={1}
 />
 
 {/* Spot price marker */}
 <ReferenceLine 
 x={ctx.spot} 
 stroke="var(--pl-spot-line, #6ee7b7)" 
 strokeWidth={2}
 label={{
 position: 'top', 
 value: 'Spot', 
 fill: 'var(--pl-spot-line, #6ee7b7)'
 }}
 />
 
 {/* ATM marker if different from spot */}
 {ctx.atm && Math.abs(ctx.atm - ctx.spot) > 1 && (
 <ReferenceLine 
 x={ctx.atm} 
 stroke="var(--pl-atm-line, #a78bfa)" 
 strokeDasharray="3 3"
 strokeWidth={1.5}
 label={{
 position: 'bottom', 
 value: 'ATM', 
 fill: 'var(--pl-atm-line, #a78bfa)'
 }}
 />
 )}
 
 {/* Breakeven points */}
 {ctx.breakevens && ctx.breakevens.map((be, i) => (
 <ReferenceLine 
 key={i}
 x={be} 
 stroke="var(--pl-breakeven-line, #fbbf24)" 
 strokeDasharray="6 4"
 strokeWidth={1.5}
 label={{
 position: i % 2 === 0 ? 'top' : 'bottom', 
 value: 'BE', 
 fill: 'var(--pl-breakeven-line, #fbbf24)'
 }}
 />
 ))}
 </AreaChart>
 </ResponsiveContainer>

 {/* SR-2/3 Crosshair overlays */}
 {hover && (
 <>
 {/* vertical line */}
 <div 
 className="pointer-events-none absolute inset-0 z-10" 
 style={{
 left: 0,
 top: 0,
 width: '100%',
 height: '100%'
 }}
 >
 <div 
 className="absolute w-px bg-white/60 z-20"
 style={{
 left: hover.chartX,
 top: 8,
 bottom: 24,
 height: 'calc(100% - 32px)'
 }}
 />
 </div>

 {/* price tag */}
 <div 
 className="pointer-events-none absolute z-30" 
 style={{
 left: Math.min(hover.chartX + 8, window.innerWidth - 100), 
 top: 6
 }}
 >
 <div className="px-2 py-1 rounded-lg bg-white text-slate-900 text-lg shadow-lg border border-slate-200">
 ${hover.x.toFixed(2)}
 </div>
 </div>

 {/* P/L tag near curve */}
 <div 
 className="pointer-events-none absolute z-30" 
 style={{
 left: Math.min(hover.chartX + 8, window.innerWidth - 120), 
 top: Math.max(hover.chartY - 10, 30)
 }}
 >
 <div className="px-2 py-0.5 rounded bg-emerald-600 text-[rgb(252, 251, 255)] text-lg shadow-lg">
 {yFmt(hover.v)}
 </div>
 </div>

 {/* Probability split at bottom */}
 {Number.isFinite(iv) && Number.isFinite(dte) && iv > 0 && dte > 0 && (
 (() => {
 const {pAbove, pBelow} = probSplit(ctx.spot, hover.x, iv, dte);
 return (
 <div className="pointer-events-none absolute left-2 right-2 z-30" style={{bottom: 8}}>
 <div className="flex items-center bg-black/60 rounded px-2 py-1">
 <div className="text-lg text-[rgb(252, 251, 255)] font-medium">
 Below: {(pBelow * 100).toFixed(0)}%
 </div>
 <div className="mx-2 h-2 flex-1 bg-white/20 rounded overflow-hidden">
 <div 
 className="h-full bg-sky-400 transition-all duration-200" 
 style={{width: (pBelow * 100) + '%'}}
 />
 </div>
 <div className="text-lg text-[rgb(252, 251, 255)] font-medium">
 Above: {(pAbove * 100).toFixed(0)}%
 </div>
 </div>
 </div>
 );
 })()
 )}
 </>
 )}
 </div>
 );
}

export default GraphPaneSR2;