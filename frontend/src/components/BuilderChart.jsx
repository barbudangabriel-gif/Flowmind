import React, { forwardRef } from 'react';

/**
 * BuilderChart - Reusable P&L Chart Component
 * 
 * SVG-based chart for displaying options strategy P&L diagrams
 * with profit/loss regions, breakevens, spot price, and optional probability bands
 * 
 * @param {Object} data - Chart data from builder API
 * @param {number} width - Chart width in pixels (default: 900)
 * @param {number} height - Chart height in pixels (default: 260)
 * @param {number} target - Optional target price to highlight
 * @param {boolean} showProbability - Show probability distribution overlay (default: true)
 * @param {React.Ref} ref - Forward ref for SVG element
 */
const BuilderChart = forwardRef(function BuilderChart(
 { data, width = 900, height = 260, target, showProbability = true },
 ref
) {
 if (!data) return null;
 
 const series = (data.chart?.series && data.chart.series[0]?.xy) 
 ? data.chart.series[0].xy 
 : [];
 
 if (!series.length) {
 return (
 <div className="bg-slate-800 rounded-lg p-6 text-slate-500">
 No chart data
 </div>
 );
 }

 // Padding configuration
 const pad = { l: 48, r: 24, t: 10, b: 28 };
 
 // Calculate data ranges
 const xs = series.map(p => p[0]);
 const ys = series.map(p => p[1]);
 const xMin = Math.min(...xs);
 const xMax = Math.max(...xs);
 const yMin = Math.min(...ys);
 const yMax = Math.max(...ys);
 
 // Coordinate transformation functions
 const X = (x) => pad.l + (x - xMin) / (xMax - xMin) * (width - pad.l - pad.r);
 const Y = (y) => height - pad.b - (y - yMin) / (yMax - yMin || 1) * (height - pad.t - pad.b);
 
 // Create P&L path
 const path = series
 .map((p, i) => `${i ? 'L' : 'M'}${X(p[0])},${Y(p[1])}`)
 .join(' ');
 
 // Create profit and loss fill paths
 const zeroY = Y(0);
 const profitPath = `M${pad.l},${zeroY}` + 
 series
 .filter(p => p[1] >= 0)
 .map(p => `L${X(p[0])},${Y(p[1])}`)
 .join(' ') + 
 `L${width - pad.r},${zeroY}Z`;
 
 const lossPath = `M${pad.l},${zeroY}` + 
 series
 .filter(p => p[1] < 0)
 .map(p => `L${X(p[0])},${Y(p[1])}`)
 .join(' ') + 
 `L${width - pad.r},${zeroY}Z`;
 
 // Probability path (optional)
 const prob = showProbability && data.chart.prob 
 ? data.chart.prob
 .map(p => `${p === data.chart.prob[0] ? 'M' : 'L'}${X(p.x)},${Y(yMin + (yMax - yMin) * p.y)}`)
 .join(' ')
 : '';
 
 // Calculate marker positions
 const spotX = X(data.meta?.spot || 0);
 const targetX = target ? X(target) : null;
 const breakevens = data.meta?.breakevens || [];
 
 return (
 <div className="bg-slate-800 rounded-lg overflow-hidden" data-testid="builder-chart">
 <svg ref={ref} width={width} height={height} className="w-full">
 {/* Probability band (back layer) */}
 {showProbability && prob && (
 <path 
 d={prob} 
 fill="var(--pl-prob-fill, rgba(59, 130, 246, 0.16))" 
 stroke="var(--pl-prob-line, #60a5fa)" 
 strokeWidth={1}
 opacity={0.7}
 />
 )}
 
 {/* Loss region fill */}
 {yMin < 0 && (
 <path 
 d={lossPath} 
 fill="var(--pl-loss-fill, rgba(239, 68, 68, 0.22))" 
 opacity={0.8}
 />
 )}
 
 {/* Profit region fill */}
 {yMax > 0 && (
 <path 
 d={profitPath} 
 fill="var(--pl-profit-fill, rgba(34, 197, 94, 0.22))" 
 opacity={0.8}
 />
 )}
 
 {/* Axes */}
 <line 
 x1={pad.l} 
 y1={height - pad.b} 
 x2={width - pad.r} 
 y2={height - pad.b} 
 stroke="#cbd5e1"
 />
 <line 
 x1={pad.l} 
 y1={pad.t} 
 x2={pad.l} 
 y2={height - pad.b} 
 stroke="#cbd5e1"
 />
 
 {/* Zero line with unified styling */}
 {0 >= yMin && 0 <= yMax && (
 <line 
 x1={pad.l} 
 y1={Y(0)} 
 x2={width - pad.r} 
 y2={Y(0)} 
 stroke="var(--pl-zero-axis, #94a3b8)" 
 strokeDasharray="4 4"
 strokeWidth={1}
 />
 )}
 
 {/* P&L payoff line */}
 <path 
 d={path} 
 fill="none" 
 stroke="var(--pl-profit-line, #22c55e)" 
 strokeWidth={2.5}
 />
 
 {/* Spot price marker */}
 <line 
 x1={spotX} 
 x2={spotX} 
 y1={pad.t} 
 y2={height - pad.b} 
 stroke="var(--pl-spot-line, #6ee7b7)" 
 strokeWidth={2}
 />
 
 {/* Target price marker */}
 {targetX != null && (
 <line 
 x1={targetX} 
 x2={targetX} 
 y1={pad.t} 
 y2={height - pad.b} 
 stroke="var(--pl-atm-line, #a78bfa)" 
 strokeDasharray="3 3"
 strokeWidth={1.5}
 />
 )}
 
 {/* Breakeven markers */}
 {breakevens.map((be, i) => (
 <line 
 key={i}
 x1={X(be)} 
 x2={X(be)} 
 y1={pad.t} 
 y2={height - pad.b} 
 stroke="var(--pl-breakeven-line, #fbbf24)" 
 strokeDasharray="6 4"
 strokeWidth={1.5}
 />
 ))}
 
 {/* Labels */}
 <text x={pad.l} y={14} fontSize={12} fill="#94a3b8">
 P/L
 </text>
 <text x={width - pad.r - 60} y={height - 6} fontSize={12} fill="#94a3b8">
 Price
 </text>
 
 {/* Spot label */}
 <text 
 x={spotX + 4} 
 y={pad.t + 15} 
 fontSize={10} 
 fill="var(--pl-spot-line, #6ee7b7)"
 >
 Spot
 </text>
 
 {/* Breakeven labels */}
 {breakevens.map((be, i) => (
 <text 
 key={i}
 x={X(be) + 4} 
 y={pad.t + 30 + (i % 2) * 15} 
 fontSize={10} 
 fill="var(--pl-breakeven-line, #fbbf24)"
 >
 BE
 </text>
 ))}
 </svg>
 </div>
 );
});

BuilderChart.displayName = 'BuilderChart';

export default BuilderChart;
