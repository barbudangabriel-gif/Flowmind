// components/StatusBadges.jsx
import React from 'react';

export function SQMBadge({ score, degraded }) {
  const scoreValue = score ?? 50;
  const color = scoreValue >= 75 ? 'text-emerald-300' : scoreValue >= 50 ? 'text-amber-300' : 'text-rose-300';
  
  return (
    <span 
      title={degraded ? 'Quality service timed out at 3.5s' : `Quality Score: ${scoreValue}`}
      className={`text-xs px-2 py-0.5 rounded bg-zinc-800 ${color} font-mono`}
    >
      SQM: {scoreValue}{degraded ? ' (degraded)' : ''}
    </span>
  );
}

export function ModeBadge({ mode }) {
  const cls = mode === 'LIVE' 
    ? 'bg-emerald-500/20 text-emerald-300' 
    : 'bg-amber-500/20 text-amber-200';
  
  return (
    <span className={`text-[10px] px-2 py-0.5 rounded ${cls} font-medium`}>
      {mode === 'LIVE' ? 'LIVE FEED' : 'DEMO DATA'}
    </span>
  );
}

export function PerfBadge({ duration, threshold = 1200 }) {
  if (!duration || duration < threshold) return null;
  
  return (
    <span className="text-[10px] px-1 py-0.5 rounded bg-orange-500/20 text-orange-300">
      slow {Math.round(duration)}ms
    </span>
  );
}