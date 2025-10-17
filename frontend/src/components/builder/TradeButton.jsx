// components/builder/TradeButton.jsx
import React from 'react';

function inferStanceFromGreeks(deltaSum) {
 if (Math.abs(deltaSum) < 0.1) return "neutral";
 return deltaSum > 0 ? "bullish" : "bearish";
}

export default function TradeButton({
 stance,
 deltaSum,
 disabled = false,
 onClick,
}) {
 const s = stance ?? inferStanceFromGreeks(deltaSum ?? 0);
 const colorMap = {
 bullish: "bg-emerald-500 hover:bg-emerald-600",
 bearish: "bg-rose-500 hover:bg-rose-600", 
 neutral: "bg-zinc-500 hover:bg-zinc-600",
 directional: "bg-fuchsia-500 hover:bg-fuchsia-600",
 };
 
 const color = colorMap[s];

 return (
 <button
 className={`px-3 py-2 rounded-xl text-[rgb(252, 251, 255)] font-medium shadow transition-colors ${color} ${
 disabled ? 'opacity-60 cursor-not-allowed' : ''
 }`}
 disabled={disabled}
 onClick={onClick}
 title={`Trade via TradeStation (${s})`}
 >
 TRADE
 </button>
 );
}