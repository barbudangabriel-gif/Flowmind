import React from 'react';
import { BUILD_STRATEGIES, toSlug } from '../../lib/buildStrategies';
import { useNavigate } from 'react-router-dom';

export default function BuildHoverMegaMenu({ symbol = "TSLA", onItemHover, onClose }) {
 const nav = useNavigate();
 
 return (
 <div 
 className="absolute top-full left-0 mt-2 bg-white rounded-2xl border border-gray-200 shadow-xl z-50 p-6"
 style={{ width: "min(95vw, 1100px)" }}
 >
 {/* Content grid - 4 coloane: Novice/Intermediate/Advanced/Expert */}
 <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
 {BUILD_STRATEGIES.map(section => (
 <div key={section.level}>
 <div className="text-xl font-medium mb-2 text-gray-700">{section.level}</div>
 <div className="grid grid-cols-1 gap-4">
 {section.groups.map(group => (
 <div key={group.title}>
 <div className="text-[11px] font-medium uppercase tracking-wide text-gray-500 mb-1">
 {group.title}
 </div>
 <div className="flex flex-col">
 {group.items.map(name => (
 <button
 key={name}
 className="text-left py-1 text-xl text-gray-700 hover:text-blue-600 hover:underline"
 onMouseEnter={() => onItemHover?.({ name, level: section.level, category: group.title })}
 onClick={(e) => {
 const slug = toSlug(name);
 const builderUrl = `/build/${slug}`;
 
 if (e.shiftKey || e.ctrlKey || e.metaKey) {
 // Open in new tab
 window.open(builderUrl, '_blank');
 } else {
 // Navigate in current tab
 nav(builderUrl);
 }
 onClose?.();
 }}
 >
 {name}
 </button>
 ))}
 </div>
 </div>
 ))}
 </div>
 </div>
 ))}
 </div>

 {/* Footer */}
 <div className="mt-6 pt-4 border-t border-gray-100">
 <div className="flex justify-between items-center text-lg text-gray-500">
 <div>Symbol: {symbol}</div>
 <div>Total: {BUILD_STRATEGIES.reduce((sum, sec) => sum + sec.groups.reduce((gSum, g) => gSum + g.items.length, 0), 0)} strategies</div>
 <div>Shift+Click to open in new tab</div>
 </div>
 </div>
 </div>
 );
}