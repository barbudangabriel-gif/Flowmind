// src/utils/payoffPreview.js
import React from "react";

/**
 * Generează o mini-diagramă SVG pentru preview bazată pe forma generică a strategiei
 */

// Helper pentru forme de payoff standard
const generatePayoffShape = (preview, width = 280, height = 120) => {
 const pad = { l: 20, r: 20, t: 10, b: 20 };
 const w = width - pad.l - pad.r;
 const h = height - pad.t - pad.b;
 
 let path = '';
 let color = '#60a5fa'; // blue default
 
 switch (preview) {
 case 'up': // Long Call
 path = `M${pad.l},${pad.t + h} L${pad.l + w * 0.4},${pad.t + h} L${pad.l + w},${pad.t}`;
 color = '#22c55e'; // green
 break;
 
 case 'down': // Long Put 
 path = `M${pad.l},${pad.t} L${pad.l + w * 0.6},${pad.t + h} L${pad.l + w},${pad.t + h}`;
 color = '#ef4444'; // red
 break;
 
 case 'range': // Covered Call - flat then decline
 path = `M${pad.l},${pad.t + h * 0.3} L${pad.l + w * 0.6},${pad.t + h * 0.3} L${pad.l + w},${pad.t + h}`;
 color = '#8b5cf6'; // purple
 break;
 
 case 'skew': // Cash Secured Put - decline then flat
 path = `M${pad.l},${pad.t} L${pad.l + w * 0.4},${pad.t + h * 0.7} L${pad.l + w},${pad.t + h * 0.7}`;
 color = '#06b6d4'; // cyan
 break;
 
 case 'tent': // Long Straddle/Strangle - V shape
 path = `M${pad.l},${pad.t + h} L${pad.l + w * 0.5},${pad.t} L${pad.l + w},${pad.t + h}`;
 color = '#f59e0b'; // amber
 break;
 
 case 'smile': // Short Straddle - inverted V
 path = `M${pad.l},${pad.t} L${pad.l + w * 0.5},${pad.t + h} L${pad.l + w},${pad.t}`;
 color = '#ec4899'; // pink
 break;
 
 case 'butterfly': // Butterfly - peak in middle
 path = `M${pad.l},${pad.t + h} L${pad.l + w * 0.25},${pad.t + h * 0.7} L${pad.l + w * 0.5},${pad.t} L${pad.l + w * 0.75},${pad.t + h * 0.7} L${pad.l + w},${pad.t + h}`;
 color = '#10b981'; // emerald
 break;
 
 case 'condor': // Iron Condor - flat middle
 path = `M${pad.l},${pad.t + h} L${pad.l + w * 0.2},${pad.t + h * 0.3} L${pad.l + w * 0.8},${pad.t + h * 0.3} L${pad.l + w},${pad.t + h}`;
 color = '#6366f1'; // indigo
 break;
 
 default:
 // Generic payoff line
 path = `M${pad.l},${pad.t + h * 0.6} Q${pad.l + w * 0.3},${pad.t + h * 0.2} ${pad.l + w * 0.5},${pad.t + h * 0.4} Q${pad.l + w * 0.7},${pad.t + h * 0.6} ${pad.l + w},${pad.t + h * 0.3}`;
 break;
 }
 
 return { path, color };
};

export function renderMiniPayoff(strategy, width = 280, height = 120) {
 if (!strategy) {
 return (
 <div 
 className="rounded-lg bg-slate-900/60 border border-slate-700 flex items-center justify-center"
 style={{ width, height }}
 >
 <div className="text-lg text-slate-500">No preview</div>
 </div>
 );
 }

 const { path, color } = generatePayoffShape(strategy.preview, width, height);
 const pad = { l: 20, r: 20, t: 10, b: 20 };
 const zeroY = height - pad.b - (height - pad.t - pad.b) * 0.5;

 return (
 <div className="rounded-lg bg-slate-900/60 border border-slate-700 overflow-hidden">
 <svg width={width} height={height} className="w-full">
 {/* Grid background */}
 <defs>
 <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
 <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1"/>
 </pattern>
 </defs>
 <rect width="100%" height="100%" fill="url(#grid)" />
 
 {/* Zero line */}
 <line 
 x1={pad.l} 
 y1={zeroY} 
 x2={width - pad.r} 
 y2={zeroY} 
 stroke="var(--pl-zero-axis, #94a3b8)" 
 strokeDasharray="3 3" 
 strokeWidth="1"
 />
 
 {/* Payoff path */}
 <path 
 d={path} 
 fill="none" 
 stroke={color}
 strokeWidth="2.5" 
 strokeLinecap="round"
 strokeLinejoin="round"
 />
 
 {/* Labels */}
 <text x={pad.l} y={height - 5} fontSize="10" fill="#94a3b8" className="text-lg">
 P&L
 </text>
 <text x={width - pad.r - 30} y={height - 5} fontSize="10" fill="#94a3b8" className="text-lg">
 Price
 </text>
 </svg>
 </div>
 );
}

// Mapare preview pentru strategii existente
export const getPreviewType = (strategyId) => {
 const previewMap = {
 'long-call': 'up',
 'long-put': 'down', 
 'covered-call': 'range',
 'cash-secured-put': 'skew',
 'bull-call-spread': 'up',
 'bear-put-spread': 'down',
 'bull-put-spread': 'up',
 'bear-call-spread': 'down',
 'iron-butterfly': 'butterfly',
 'iron-condor': 'condor',
 'long-straddle': 'tent',
 'long-strangle': 'tent',
 'short-straddle': 'smile',
 'short-strangle': 'smile',
 'protective-put': 'down',
 'collar': 'range',
 };
 
 return previewMap[strategyId] || 'default';
};