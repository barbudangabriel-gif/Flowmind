import React, { useState, useEffect } from 'react';
import { Monitor, Save, RotateCcw } from 'lucide-react';

export default function ScreensaverSettings() {
  const [timeout, setTimeout] = useState(() => {
    // Load from localStorage or default to 5 minutes
    const saved = localStorage.getItem('screensaverTimeout');
    return saved ? parseInt(saved) : 5;
  });
  
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('screensaverTimeout', timeout.toString());
    setSaved(true);
    
    // Trigger a custom event to update the App component
    window.dispatchEvent(new CustomEvent('screensaverSettingsChanged', { 
      detail: { timeout: timeout * 60 * 1000 } 
    }));
    
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    setTimeout(5);
    localStorage.setItem('screensaverTimeout', '5');
    setSaved(true);
    
    window.dispatchEvent(new CustomEvent('screensaverSettingsChanged', { 
      detail: { timeout: 5 * 60 * 1000 } 
    }));
    
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-8 bg-gradient-to-r from-[#0a0e1a] via-[#0b0f1b] to-[#0a0e1a] min-h-screen">
      <div className="max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Monitor className="w-6 h-6 text-cyan-400" />
            <h1 className="text-[20px] text-[rgb(252, 251, 255)]">Screensaver Settings</h1>
          </div>
          <p className="text-[13px] text-slate-400">
            Configure automatic return to homepage after inactivity
          </p>
        </div>

        {/* Settings Card */}
        <div className="bg-[#0a0e1a] border border-[#1e2530] rounded-lg p-4">
          <div className="mb-6">
            <label className="block text-[13px] text-[rgb(252, 251, 255)] mb-3">
              Inactivity Timeout (minutes)
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                min="0"
                max="60"
                value={timeout}
                onChange={(e) => setTimeout(Math.max(0, Math.min(60, parseInt(e.target.value) || 0)))}
                className="w-32 px-3 py-2 bg-[#0f1419] border border-[#1e2530] rounded text-[13px] text-white focus:outline-none focus:border-cyan-400 transition-colors"
              />
              <span className="text-[13px] text-slate-400">minutes</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              {timeout === 0 
                ? 'Screensaver is disabled' 
                : `After ${timeout} ${timeout === 1 ? 'minute' : 'minutes'} of no activity, you'll return to the homepage`
              }
            </p>
          </div>

          {/* Quick presets */}
          <div className="mb-6">
            <label className="block text-[13px] text-[rgb(252, 251, 255)] mb-3">
              Quick Presets
            </label>
            <div className="flex flex-wrap gap-2">
              {[1, 3, 5, 10, 15, 30, 60].map(minutes => (
                <button
                  key={minutes}
                  onClick={() => setTimeout(minutes)}
                  className={`px-3 py-1.5 rounded text-[11px] transition-colors ${
                    timeout === minutes
                      ? 'bg-cyan-400 text-black'
                      : 'bg-[#0f1419] text-slate-300 hover:bg-slate-700 border border-[#1e2530]'
                  }`}
                >
                  {minutes === 60 ? '1h' : `${minutes}m`}
                </button>
              ))}
              <button
                onClick={() => setTimeout(0)}
                className={`px-3 py-1.5 rounded text-[11px] transition-colors ${
                  timeout === 0
                    ? 'bg-cyan-400 text-black'
                    : 'bg-[#0f1419] text-slate-300 hover:bg-slate-700 border border-[#1e2530]'
                }`}
              >
                Never
              </button>
            </div>
          </div>

          {/* Info box */}
          <div className="bg-slate-900/30 border border-slate-800/50 rounded p-3 mb-6">
            <p className="text-[11px] text-slate-400 leading-relaxed">
              <span className="text-cyan-400 font-medium">How it works:</span> The screensaver monitors 
              mouse movement, keyboard input, scrolling, and touch events. If no activity is detected 
              for the specified duration, you'll automatically return to the homepage.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black rounded text-[13px] hover:bg-cyan-300 transition-colors"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 bg-[#0f1419] text-slate-300 border border-[#1e2530] rounded text-[13px] hover:bg-slate-700 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset to Default
            </button>
          </div>

          {/* Success message */}
          {saved && (
            <div className="mt-4 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded text-[13px] text-emerald-400">
              Settings saved successfully!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
