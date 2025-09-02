import React, { useState, useRef, useEffect } from "react";
import { strategiesByLevel, deepLinkFromStrategy } from "../../data/strategies-helpers";
import HoverDiagram from "../build/HoverDiagram";

export default function BuildMegaMenu({ symbol = "TSLA" }) {
  const [open, setOpen] = useState(false);
  const [preview, setPreview] = useState(null);
  const [isMobile, setIsMobile] = useState(false);
  const wrapRef = useRef(null);
  let hoverTimer = useRef(null);
  let previewTimer = useRef(null);

  const levels = ["novice", "intermediate", "advanced", "expert"];
  const titles = {
    novice: "Novice",
    intermediate: "Intermediate", 
    advanced: "Advanced",
    expert: "Expert"
  };

  const levelColors = {
    novice: "text-blue-400",
    intermediate: "text-yellow-400",
    advanced: "text-orange-400", 
    expert: "text-red-400"
  };

  // Mobile detection & keyboard handling
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 1024);
    const handleKeydown = (e) => {
      if (e.key === 'Escape' && open) {
        setOpen(false);
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    document.addEventListener('keydown', handleKeydown);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('keydown', handleKeydown);
    };
  }, [open]);

  // Hover intent with safe timing
  const onEnter = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    hoverTimer.current = setTimeout(() => setOpen(true), 80);
  };

  const onLeave = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    setOpen(false);
    setPreview(null);
  };

  // Strategy preview on hover
  const onStrategyEnter = (strategy) => {
    if (isMobile) return;
    if (previewTimer.current) clearTimeout(previewTimer.current);
    
    previewTimer.current = setTimeout(() => {
      // Prefetch Builder route
      try {
        import('react-router-dom').then(({ preloadRoute }) => {
          if (preloadRoute) preloadRoute('/build/:id');
        });
      } catch (e) { /* Fallback gracefully */ }
      
      // Set preview data
      setPreview({
        legs: strategy.legs || [],
        spot: 250, // Default TSLA spot
        strikes: [240, 250, 260]
      });
    }, 100);
  };

  const onStrategyLeave = () => {
    if (previewTimer.current) clearTimeout(previewTimer.current);
    setPreview(null);
  };

  const handleStrategyClick = (strategy, event) => {
    // Check if Shift key is pressed for new tab
    if (event.shiftKey || event.ctrlKey || event.metaKey) {
      event.preventDefault();
      const url = deepLinkFromStrategy(strategy, { symbol });
      window.open(url, '_blank', 'rel=noopener');
    }
    // Otherwise let the default link behavior happen
    setOpen(false);
    setPreview(null);
  };

  return (
    <div
      className="relative"
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      ref={wrapRef}
    >
      <button 
        className="px-3 py-2 hover:text-emerald-400 transition-colors text-slate-200"
        onClick={() => setOpen(!open)}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        Build ▾
      </button>

      {open && (
        // Desktop mega menu
        <div className="hidden lg:block absolute left-0 top-full z-50 mt-2 w-[880px] rounded-xl bg-slate-900/95 shadow-2xl ring-1 ring-white/10 backdrop-blur border border-slate-800">
          <div className="grid grid-cols-4 gap-6 p-6">
            {levels.map(level => (
              <div key={level}>
                <h4 className={`mb-3 text-sm font-semibold ${levelColors[level]} flex items-center gap-2`}>
                  {titles[level]}
                  <span className="text-xs px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {(strategiesByLevel[level] || []).reduce((count, group) => count + group.items.length, 0)}
                  </span>
                </h4>

                <div className="space-y-4">
                  {(strategiesByLevel[level] || []).map(group => (
                    <div key={group.title}>
                      <div className="text-[11px] uppercase tracking-wide text-slate-400 mb-2 font-medium">
                        {group.title}
                      </div>
                      <ul className="space-y-1.5">
                        {group.items.map(strategy => (
                          <li
                            key={strategy.id}
                            onMouseEnter={() => onStrategyEnter(strategy)}
                            onMouseLeave={onStrategyLeave}
                            className="relative group"
                          >
                            <a
                              href={deepLinkFromStrategy(strategy, { symbol })}
                              onClick={(e) => handleStrategyClick(strategy, e)}
                              className="block text-sm text-sky-300 hover:text-emerald-300 hover:underline transition-colors py-0.5 px-1 -mx-1 rounded hover:bg-slate-800/50"
                              title={`${strategy.name} - ${strategy.stance} strategy`}
                            >
                              {strategy.name}
                            </a>

                            {/* Preview diagram on hover */}
                            {preview && (
                              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-3 z-50 pointer-events-none">
                                <HoverDiagram
                                  symbol={symbol}
                                  legs={preview.legs}
                                  spot={preview.spot}
                                  width={220}
                                  height={88}
                                />
                              </div>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer with hints */}
          <div className="border-t border-white/10 px-6 py-3 bg-slate-900/50">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-4">
                <span>Symbol: <span className="text-slate-300 font-mono">{symbol}</span></span>
                <span>Total: <span className="text-slate-300">{
                  levels.reduce((total, level) => 
                    total + (strategiesByLevel[level] || []).reduce((count, group) => 
                      count + group.items.length, 0), 0)
                } strategies</span></span>
              </div>
              <div>
                Hint: Hold <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">Shift</kbd> to open in new tab
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mobile drawer */}
      {open && (
        <div className="lg:hidden fixed inset-0 z-50 overflow-hidden">
          <div 
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-0 h-full w-80 max-w-[90vw] bg-slate-900 shadow-2xl border-l border-slate-800 overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
              <h3 className="text-lg font-semibold text-white">Build Strategy</h3>
              <button
                onClick={() => setOpen(false)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <span className="sr-only">Close</span>
                <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-slate-800">
              <input
                type="text"
                placeholder="Search strategies..."
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Strategy list - single column */}
            <div className="p-4">
              {levels.map(level => (
                <div key={level} className="mb-6">
                  <h4 className={`mb-3 text-sm font-semibold ${levelColors[level]} flex items-center gap-2`}>
                    {titles[level]}
                    <span className="text-xs px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {(strategiesByLevel[level] || []).reduce((count, group) => count + group.items.length, 0)}
                    </span>
                  </h4>

                  <div className="space-y-4">
                    {(strategiesByLevel[level] || []).map(group => (
                      <div key={group.title}>
                        <div className="text-[11px] uppercase tracking-wide text-slate-400 mb-2 font-medium">
                          {group.title}
                        </div>
                        <ul className="space-y-2">
                          {group.items.map(strategy => (
                            <li key={strategy.id}>
                              <a
                                href={deepLinkFromStrategy(strategy, { symbol })}
                                onClick={(e) => handleStrategyClick(strategy, e)}
                                className="block text-sm text-sky-300 hover:text-emerald-300 hover:underline transition-colors py-2 px-3 -mx-3 rounded-lg hover:bg-slate-800/50"
                                title={`${strategy.name} - ${strategy.stance} strategy`}
                              >
                                {strategy.name}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}