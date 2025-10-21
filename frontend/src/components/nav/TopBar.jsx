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
 <div className="flex items-center justify-between px-6 py-3 bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] border-b border-[#1e293b]/50 backdrop-blur-sm">
 {/* Left - Logo */}
 <div className="flex items-center gap-8">
 <Link to="/" className="text-xl font-medium bg-gradient-to-r from-[#3b82f6] to-[#60a5fa] bg-clip-text text-transparent">
 FlowMind
 </Link>
 
 {/* Navigation */}
 <nav className="flex items-center gap-2">
 <Link to="/optimize" className="px-4 py-2 rounded-lg hover:bg-[#1e2430] text-[#cbd5e1] hover:text-[rgb(252, 251, 255)] transition-all duration-150">
 Optimize
 </Link>
 
 <Link to="/flow" className="px-4 py-2 rounded-lg hover:bg-[#1e2430] text-[#cbd5e1] hover:text-[rgb(252, 251, 255)] transition-all duration-150">
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
 className="px-4 py-2 rounded-lg hover:bg-[#1e2430] text-[#cbd5e1] hover:text-[rgb(252, 251, 255)] transition-all duration-150 flex items-center gap-1"
 onClick={() => setMegaMenuOpen(v => !v)}
 aria-haspopup="menu"
 aria-expanded={megaMenuOpen}
 data-testid="build-hover-button"
 >
 <span>Build</span>
 <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
 </svg>
 </button>
 {megaMenuOpen && (
 <BuildHoverMegaMenu
 symbol="TSLA"
 onClose={() => setMegaMenuOpen(false)}
 />
 )}
 </div>
 
 <Link to="/mindfolios" className="px-4 py-2 rounded-lg hover:bg-[#1e2430] text-[#cbd5e1] hover:text-[rgb(252, 251, 255)] transition-all duration-150">
 Mindfolios
 </Link>
 </nav>
 </div>
 
 {/* Right - User menu placeholder */}
 <div className="flex items-center gap-3">
 <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
 <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
 <span className="text-lg font-medium text-emerald-400">LIVE</span>
 </div>
 <div className="w-9 h-9 bg-gradient-to-br from-[#3b82f6] to-[#2563eb] rounded-lg flex items-center justify-center">
 <span className="text-[rgb(252, 251, 255)] text-xl font-medium">GB</span>
 </div>
 </div>
 </div>
 </div>
 );
}