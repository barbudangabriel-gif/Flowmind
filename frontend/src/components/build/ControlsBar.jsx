import { useState, useEffect } from 'react';

export default function ControlsBar({ 
  builder, 
  onParams, 
  mode, 
  setMode, 
  pricing,
  showProbability,
  setShowProbability,
  highContrast,
  setHighContrast
}) {
  const [moreOpen, setMoreOpen] = useState(false);
  
  // Toggle high contrast theme on body
  useEffect(() => {
    if (highContrast) {
      document.body.classList.add('theme-contrast');
    } else {
      document.body.classList.remove('theme-contrast');
    }
    
    return () => {
      document.body.classList.remove('theme-contrast');
    };
  }, [highContrast]);
  const modes = [
    { key: 'graph', label: 'Graph' },
    { key: 'table', label: 'Table' },
    { key: 'pl$', label: 'Profit / Loss $' },
    { key: 'pl%', label: 'Profit / Loss %' },
    { key: 'contract', label: 'Contract Value' },
    { key: '%risk', label: '% of Max Risk' }
  ];

  const expiryLabel = pricing?.expiry_label || 
    (builder.expiry ? new Date(builder.expiry).toLocaleDateString() : 'No expiry selected');

  const ivAtm = pricing?.iv_atm || 0.25; // Default 25% IV

  return (
    <div className="space-y-4 py-3" data-testid="controls-bar">
      {/* Date Display */}
      <div className="text-xs text-slate-400 uppercase tracking-wide">
        Date: {expiryLabel}
      </div>

      {/* Range & IV Controls */}
      <div className="grid grid-cols-2 gap-6">
        {/* Range Control */}
        <div>
          <label className="block text-xs text-slate-400 uppercase tracking-wide mb-2">
            Range: ±{Math.round(builder.params.range_pct * 100)}%
          </label>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">5%</span>
            <input 
              type="range" 
              min="0.05" 
              max="0.30" 
              step="0.01"
              value={builder.params.range_pct}
              onChange={e => onParams({ range_pct: +e.target.value })}
              className="flex-1 accent-emerald-500"
              data-testid="range-slider"
            />
            <span className="text-xs text-slate-500">30%</span>
          </div>
        </div>

        {/* IV Control */}
        <div>
          <label className="block text-xs text-slate-400 uppercase tracking-wide mb-2">
            Implied Volatility: {(ivAtm * builder.params.iv_mult * 100).toFixed(1)}% 
            <span className="text-slate-500">({builder.params.iv_mult.toFixed(2)}x)</span>
          </label>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">0.5x</span>
            <input 
              type="range" 
              min="0.5" 
              max="3" 
              step="0.05"
              value={builder.params.iv_mult}
              onChange={e => onParams({ iv_mult: +e.target.value })}
              className="flex-1 accent-emerald-500"
              data-testid="iv-slider"
            />
            <span className="text-xs text-slate-500">3.0x</span>
          </div>
        </div>
      </div>

      {/* Mode Tabs */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          {modes.map(m => (
            <button 
              key={m.key} 
              className={`px-3 py-1.5 rounded text-xs transition-colors ${
                mode === m.key 
                  ? 'bg-emerald-600 text-white' 
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
              onClick={() => setMode(m.key)}
              data-tab={m.key}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* More Options Dropdown */}
        <div className="relative">
          <button 
            className="px-3 py-1.5 rounded text-xs bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
            onClick={() => setMoreOpen(!moreOpen)}
          >
            More ▾
          </button>
          
          {moreOpen && (
            <>
              {/* Backdrop to close dropdown */}
              <div 
                className="fixed inset-0 z-40" 
                onClick={() => setMoreOpen(false)}
              />
              
              {/* Dropdown Menu */}
              <div className="absolute right-0 top-full mt-2 w-56 bg-slate-800 rounded-lg shadow-xl border border-slate-700 z-50">
                <div className="p-3">
                  <div className="text-xs uppercase tracking-wide text-slate-400 mb-3">
                    Chart Options
                  </div>
                  
                  {/* High Contrast Toggle */}
                  <label className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-700/50 rounded px-2 -mx-2">
                    <div>
                      <div className="text-sm text-slate-200">High Contrast</div>
                      <div className="text-xs text-slate-400">Color-blind safe palette</div>
                    </div>
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={highContrast}
                        onChange={(e) => setHighContrast(e.target.checked)}
                        className="sr-only"
                      />
                      <div className={`w-11 h-6 rounded-full transition-colors ${
                        highContrast ? 'bg-emerald-600' : 'bg-slate-600'
                      }`}>
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform mt-0.5 ${
                          highContrast ? 'translate-x-5 ml-0.5' : 'translate-x-0 ml-0.5'
                        }`} />
                      </div>
                    </div>
                  </label>
                  
                  {/* Show Probability Toggle */}
                  <label className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-700/50 rounded px-2 -mx-2">
                    <div>
                      <div className="text-sm text-slate-200">Show Probability</div>
                      <div className="text-xs text-slate-400">Display probability bands</div>
                    </div>
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={showProbability}
                        onChange={(e) => setShowProbability(e.target.checked)}
                        className="sr-only"
                      />
                      <div className={`w-11 h-6 rounded-full transition-colors ${
                        showProbability ? 'bg-emerald-600' : 'bg-slate-600'
                      }`}>
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform mt-0.5 ${
                          showProbability ? 'translate-x-5 ml-0.5' : 'translate-x-0 ml-0.5'
                        }`} />
                      </div>
                    </div>
                  </label>
                  
                  <div className="border-t border-slate-700 mt-3 pt-3">
                    <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                      Greeks
                    </div>
                    <div className="text-xs text-slate-500">
                      Greeks are displayed below the chart when available
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}