import React from 'react';

export function SpreadQualityMeter({ score = 0, slippageUsd = 0 }) {
  // Quality bands: 80-100 Excellent, 60-79 Good, 40-59 Fair, 25-39 Poor, <25 Bad
  const getQualityInfo = (score) => {
    if (score >= 80) return { label: 'Excellent', color: 'bg-emerald-500', textColor: 'text-emerald-700' };
    if (score >= 60) return { label: 'Good', color: 'bg-green-500', textColor: 'text-green-700' };
    if (score >= 40) return { label: 'Fair', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (score >= 25) return { label: 'Poor', color: 'bg-orange-500', textColor: 'text-orange-700' };
    return { label: 'Bad', color: 'bg-red-500', textColor: 'text-red-700' };
  };

  const quality = getQualityInfo(score);
  const widthPercentage = Math.min(100, Math.max(0, score));

  return (
    <div className="space-y-2">
      {/* Quality bar */}
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${quality.color}`}
            style={{ width: `${widthPercentage}%` }}
          />
        </div>
        <span className={`text-xs font-medium ${quality.textColor}`}>
          {score}%
        </span>
      </div>

      {/* Quality label and slippage */}
      <div className="flex items-center justify-between text-xs">
        <span className={`font-medium ${quality.textColor}`}>
          {quality.label}
        </span>
        {slippageUsd > 0 && (
          <span className="text-slate-500">
            Est. Slippage: ${slippageUsd.toFixed(2)}
          </span>
        )}
      </div>
    </div>
  );
}

export default SpreadQualityMeter;