// components/QualityBadge.jsx
import React from 'react';

export default function QualityBadge({ quality, delta, loading, className = "" }) {
  if (!quality || typeof quality.score !== 'number') return null;
  
  const score = quality.score;
  const buckets = quality.buckets || {};
  const flags = quality.flags || [];
  
  // Score-based color
  const getScoreColor = (score) => {
    if (score >= 75) return "bg-emerald-500 text-white";
    if (score >= 50) return "bg-amber-500 text-white";
    return "bg-rose-500 text-white";
  };
  
  const scoreColor = getScoreColor(score);
  
  // Format bucket percentages
  const formatBucket = (value) => Math.round((value || 0) * 100);
  
  const tooltipText = [
    `Quality ${score}`,
    `L:${formatBucket(buckets.liquidity)} P:${formatBucket(buckets.pricing)} `,
    `S:${formatBucket(buckets.structure)} R:${formatBucket(buckets.risk)} `,
    `T:${formatBucket(buckets.stability)}`,
    flags.length ? `\nFlags: ${flags.join(", ")}` : ""
  ].join("");

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Main quality score */}
      <div 
        className={`px-2 py-1 rounded text-xs font-medium ${scoreColor}`} 
        title={tooltipText}
      >
        Quality • {loading ? "…" : score}
        {typeof delta === "number" && (
          <span className={delta >= 0 ? "text-emerald-100" : "text-rose-100"}>
            {" "}({delta >= 0 ? "+" : ""}{delta})
          </span>
        )}
      </div>
      
      {/* Bucket breakdown */}
      <div className="text-[11px] text-slate-600 space-x-2">
        <span title="Liquidity">L {formatBucket(buckets.liquidity)}%</span>
        <span title="Pricing">P {formatBucket(buckets.pricing)}%</span>
        <span title="Structure">S {formatBucket(buckets.structure)}%</span>
        <span title="Risk">R {formatBucket(buckets.risk)}%</span>
        <span title="Stability">T {formatBucket(buckets.stability)}%</span>
      </div>
      
      {/* Flags */}
      {flags.length > 0 && (
        <div className="text-[10px] text-amber-600 space-y-1">
          {flags.map((flag, index) => (
            <div key={index} className="flex items-center gap-1">
              <span>⚠️</span>
              <span>{flag}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Tooltip variant for detailed hover info
export function QualityTooltip({ quality, children }) {
  if (!quality) return children;
  
  return (
    <div className="relative group">
      {children}
      <div className="absolute z-50 invisible group-hover:visible bg-black text-white text-xs rounded-lg p-3 -top-2 left-full ml-2 whitespace-nowrap">
        <div className="font-semibold mb-2">Quality Breakdown (Score: {quality.score})</div>
        <div className="space-y-1">
          <div>Liquidity: {Math.round((quality.buckets?.liquidity || 0) * 100)}% - OI, Volume, Spreads</div>
          <div>Pricing: {Math.round((quality.buckets?.pricing || 0) * 100)}% - Edge vs Theoretical</div>
          <div>Structure: {Math.round((quality.buckets?.structure || 0) * 100)}% - Delta, DTE, Breakevens</div>
          <div>Risk: {Math.round((quality.buckets?.risk || 0) * 100)}% - Risk/Reward, Assignment</div>
          <div>Stability: {Math.round((quality.buckets?.stability || 0) * 100)}% - Greeks sensitivity</div>
        </div>
        {quality.flags && quality.flags.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-600">
            <div className="font-semibold">Warnings:</div>
            {quality.flags.map((flag, i) => (
              <div key={i} className="text-amber-300">• {flag}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}