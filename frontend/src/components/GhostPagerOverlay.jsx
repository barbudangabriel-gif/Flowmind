import React from 'react';

const clsx = (...xs) => xs.filter(Boolean).join(' ');

export function GhostPagerOverlay({
 currentPage = "Greeks", // "Greeks" | "Strategy Info"
 onPageChange,
 className = ""
}) {
 const pages = ["Greeks", "Strategy Info"];
 const currentIndex = pages.indexOf(currentPage);

 return (
 <div className={clsx("absolute inset-0 pointer-events-none", className)}>
 {/* Left chevron */}
 <button
 className={clsx(
 "absolute left-2 top-1/2 -translate-y-1/2 pointer-events-auto",
 "w-8 h-8 rounded-full bg-black/10 hover:bg-black/20 transition-colors",
 "flex items-center justify-center text-slate-700 hover:text-slate-900",
 currentIndex <= 0 && "opacity-30 cursor-not-allowed"
 )}
 onClick={() => currentIndex > 0 && onPageChange(pages[currentIndex - 1])}
 disabled={currentIndex <= 0}
 title="Previous page"
 >
 <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
 <path d="M10 12L6 8l4-4v8z"/>
 </svg>
 </button>

 {/* Right chevron */}
 <button
 className={clsx(
 "absolute right-2 top-1/2 -translate-y-1/2 pointer-events-auto",
 "w-8 h-8 rounded-full bg-black/10 hover:bg-black/20 transition-colors",
 "flex items-center justify-center text-slate-700 hover:text-slate-900",
 currentIndex >= pages.length - 1 && "opacity-30 cursor-not-allowed"
 )}
 onClick={() => currentIndex < pages.length - 1 && onPageChange(pages[currentIndex + 1])}
 disabled={currentIndex >= pages.length - 1}
 title="Next page"
 >
 <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
 <path d="M6 4l4 4-4 4V4z"/>
 </svg>
 </button>

 {/* Page indicators at bottom */}
 <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-auto">
 <div className="flex gap-2">
 {pages.map((page, index) => (
 <button
 key={page}
 className={clsx(
 "w-2 h-2 rounded-full transition-colors",
 index === currentIndex 
 ? "bg-slate-700" 
 : "bg-slate-300 hover:bg-slate-500"
 )}
 onClick={() => onPageChange(page)}
 title={page}
 />
 ))}
 </div>
 </div>
 </div>
 );
}

export default GhostPagerOverlay;