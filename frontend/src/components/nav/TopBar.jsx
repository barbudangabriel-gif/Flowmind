import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import BuildHoverMegaMenu from "./BuildHoverMegaMenu";

export default function TopBar() {
  const [megaMenuOpen, setMegaMenuOpen] = useState(false);
  const areaRef = useRef(null);
  
  // Auto-open for demo/test (still available)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('catalog') === '1') {
      setMegaMenuOpen(true);
    }
  }, []);

  return (
    <div className="relative z-[1000]">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
        {/* Left - Logo */}
        <div className="flex items-center gap-6">
          <Link to="/" className="text-xl font-bold text-white">
            FlowMind
          </Link>
          
          {/* Navigation */}
          <nav className="flex items-center gap-4">
            <Link to="/optimize" className="px-3 py-2 hover:text-emerald-400 text-slate-200 transition-colors">
              Optimize
            </Link>
            
            <Link to="/flow" className="px-3 py-2 hover:text-emerald-400 text-slate-200 transition-colors">
              Flow
            </Link>
            
            {/* Build Hover Mega Menu */}
            <div
              ref={areaRef}
              className="relative"
              onMouseEnter={() => setMegaMenuOpen(true)}
              onMouseLeave={() => setMegaMenuOpen(false)}
            >
              <button
                className="px-3 py-2 hover:text-emerald-400 text-slate-200 transition-colors"
                onClick={() => setMegaMenuOpen(v => !v)}
                aria-haspopup="menu"
                aria-expanded={megaMenuOpen}
                data-testid="build-hover-button"
              >
                Build ▾
              </button>
              {megaMenuOpen && (
                <BuildHoverMegaMenu
                  symbol="TSLA"
                  onClose={() => setMegaMenuOpen(false)}
                />
              )}
            </div>
            
            <Link to="/portfolios" className="px-3 py-2 hover:text-emerald-400 text-slate-200 transition-colors">
              Portfolios
            </Link>
          </nav>
        </div>
        
        {/* Right - User menu placeholder */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-slate-700 rounded-full"></div>
        </div>
      </div>
    </div>
  );
}