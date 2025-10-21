// =============================================
// FlowMind — Sidebar (Safe Minimal)
// =============================================
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
import { buildNav } from '../lib/nav.simple';

// Safe icon component
function IconByName({ name, className = "w-4 h-4" }) {
 if (!name) return <LucideIcons.Circle className={className} />;
 
 const IconComponent = LucideIcons[name];
 if (!IconComponent) {
 console.warn(`Icon '${name}' not found`);
 return <LucideIcons.Circle className={className} />;
 }
 
 return <IconComponent className={className} />;
}

// Simple badge component
function Badge({ b }) {
 if (!b) return null;
 
 const toneClasses = {
 default: "bg-gray-100 text-gray-800",
 success: "bg-green-100 text-green-800", 
 warn: "bg-yellow-100 text-yellow-800",
 danger: "bg-red-100 text-red-800",
 beta: "bg-purple-100 text-purple-800",
 live: "bg-emerald-100 text-emerald-800 animate-pulse",
 verified: "bg-blue-100 text-blue-800"
 };

 const classes = toneClasses[b.tone] || toneClasses.default;
 
 return (
 <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${classes}`}>
 {b.text}
 </span>
 );
}

// Safe row renderer
function Row({ item, ctx, depth = 0 }) {
 // Safety checks
 if (!item || !item.label) return null;
 
 // Check visibility
 try {
 if (item.visible && !item.visible(ctx)) return null;
 } catch (e) {
 console.warn('Visibility check failed:', e);
 }

 // Check disabled state 
 let disabled = false;
 try {
 disabled = item.disabled ? item.disabled(ctx) : false;
 } catch (e) {
 console.warn('Disabled check failed:', e);
 }

 // Resolve badge safely
 let badge = null;
 try {
 if (typeof item.badge === 'function') {
 badge = item.badge(ctx);
 } else if (item.badge) {
 badge = item.badge;
 }
 } catch (e) {
 console.warn('Badge resolution failed:', e);
 }

 const baseClasses = `flex items-center gap-2 px-2 py-1.5 rounded-md text-xl transition-colors ${depth > 0 ? 'ml-4' : ''}`;
 const stateClasses = disabled 
 ? "opacity-50 pointer-events-none text-slate-500"
 : "text-slate-300 hover:bg-slate-800 cursor-pointer";

 const content = (
 <div className={`${baseClasses} ${stateClasses}`}>
 <span className="flex items-center gap-2 flex-1">
 <IconByName name={item.icon} className="w-4 h-4 shrink-0 opacity-80" />
 <span className="text-xl truncate">{item.label}</span>
 </span>
 <Badge b={badge} />
 </div>
 );
 
 return item.to ? (
 <Link to={item.to} className="block">{content}</Link>
 ) : (
 <div>{content}</div>
 );
}

export default function SidebarSimple({ ctx, collapsed = false }) {
 // State for collapsed sections
 const [collapsedSections, setCollapsedSections] = useState({});
 // State for showing popover submenu
 const [activePopover, setActivePopover] = useState(null);
 
 const toggleSection = (sectionTitle) => {
 setCollapsedSections(prev => ({
 ...prev,
 [sectionTitle]: !prev[sectionTitle]
 }));
 };
 
 // Close popover when clicking outside
 React.useEffect(() => {
 if (!activePopover) return;
 
 const handleClickOutside = (e) => {
 // Don't close if clicking on the popover itself or the button
 const clickedOnSidebar = e.target.closest('aside');
 const clickedOnPopover = e.target.closest('[data-popover]');
 
 console.log('🖱️ Click outside check:', { 
 clickedOnSidebar: !!clickedOnSidebar, 
 clickedOnPopover: !!clickedOnPopover,
 activePopover 
 });
 
 if (!clickedOnSidebar && !clickedOnPopover) {
 console.log(' Closing popover');
 setActivePopover(null);
 }
 };
 
 // Use setTimeout to avoid closing immediately after opening
 const timer = setTimeout(() => {
 console.log(' Click outside handler attached for:', activePopover);
 document.addEventListener('click', handleClickOutside);
 }, 100);
 
 return () => {
 clearTimeout(timer);
 document.removeEventListener('click', handleClickOutside);
 };
 }, [activePopover]);
 
 // Provide safe defaults
 const safeCtx = {
 role: ctx?.role || "user",
 flags: ctx?.flags || {},
 metrics: ctx?.metrics || {},
 mindfolios: Array.isArray(ctx?.mindfolios) ? ctx.mindfolios : [],
 };
 
 const nav = React.useMemo(() => {
 try {
 return buildNav(safeCtx);
 } catch (e) {
 console.error('buildNav failed:', e);
 return [];
 }
 }, [JSON.stringify(safeCtx)]);
 
 return (
 <aside className={`border-r border-[#1e293b] bg-gradient-to-b from-[#0f1419] to-[#0a0e1a] h-screen overflow-y-auto transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}`} style={{ borderRightWidth: '1px' }}>
 {/* Space for hamburger button */}
 <div className="h-16"></div>
 
 {nav.map((sec, i) => {
 const isCollapsed = collapsedSections[sec.title];
 
 return (
 <div key={`sec-${i}`} className="px-2 py-3">
 {/* Section header with toggle arrow - only when NOT collapsed */}
 {!collapsed && (
 <button
 onClick={() => toggleSection(sec.title)}
 className="w-full flex items-center gap-2 px-1 mb-2 text-[11px] uppercase tracking-wide text-[#94a3b8] hover:text-[rgb(252, 251, 255)] transition-colors"
 >
 <LucideIcons.ChevronRight 
 className={`w-4 h-4 text-slate-400 transition-transform ${isCollapsed ? '' : 'rotate-90'}`}
 />
 <span>{sec.title}</span>
 </button>
 )}
 
 {/* Section items - full view when expanded */}
 {!isCollapsed && !collapsed && (
 <div className="space-y-1">
 {(sec.items || []).map((it, idx) => (
 <div key={`${sec.title}-${idx}`}>
 <Row item={it} ctx={safeCtx} />
 {it.children && it.children.length > 0 && (
 <div className="mt-1 ml-2 space-y-1">
 {it.children.map((ch, cidx) => (
 <Row key={`${sec.title}-${idx}-ch-${cidx}`} item={ch} ctx={safeCtx} depth={1} />
 ))}
 </div>
 )}
 </div>
 ))}
 </div>
 )}
 
 {/* Show only icons when sidebar collapsed - no arrows */}
 {collapsed && (
 <div className="space-y-2">
 {(sec.items || []).map((it, idx) => {
 const itemKey = `${sec.title}-${idx}`;
 const hasChildren = it.children && it.children.length > 0;
 
 // If item has children, show a popover menu on click
 if (hasChildren) {
 const isActive = activePopover === itemKey;
 
 return (
 <div key={`${itemKey}-icon`} className="relative">
 <button
 onClick={(e) => {
 e.stopPropagation();
 console.log('🔘 Popover toggle:', it.label, 'Current:', activePopover, 'New:', isActive ? null : itemKey);
 setActivePopover(isActive ? null : itemKey);
 }}
 className={`w-full flex items-center justify-center p-2 rounded transition-all relative ${
 isActive 
 ? 'bg-slate-800 text-emerald-400' 
 : 'text-slate-300 hover:bg-slate-800'
 }`}
 title={it.label}
 >
 <IconByName name={it.icon} className="w-5 h-5" />
 {/* Indicator that item has submenu */}
 <span className="absolute bottom-1 right-1 w-1.5 h-1.5 bg-emerald-400 rounded-full"></span>
 </button>
 
 {/* Popover menu */}
 {activePopover === itemKey && (
 <div 
 data-popover="true"
 className="absolute left-full top-0 ml-2 z-50 min-w-[200px] animate-in fade-in-0 slide-in-from-left-2 duration-200"
 onClick={(e) => e.stopPropagation()}
 >
 <div className="bg-[#1e293b] border border-[#334155] rounded-lg shadow-2xl py-2 backdrop-blur-sm">
 {/* Header */}
 <div className="px-3 py-2 text-lg font-medium text-slate-400 uppercase border-b border-[#334155] flex items-center gap-2">
 <IconByName name={it.icon} className="w-3.5 h-3.5" />
 {it.label}
 </div>
 {/* Children items */}
 {it.children.map((ch, cidx) => (
 <Link
 key={cidx}
 to={ch.to || '#'}
 onClick={() => setActivePopover(null)}
 className="flex items-center gap-2 px-3 py-2.5 text-xl text-slate-300 hover:bg-slate-700/50 hover:text-[rgb(252, 251, 255)] transition-all group"
 >
 <IconByName name={ch.icon} className="w-4 h-4 group-hover:text-emerald-400 transition-colors" />
 <span>{ch.label}</span>
 </Link>
 ))}
 </div>
 </div>
 )}
 </div>
 );
 }
 
 // Regular item without children
 return (
 <Link
 key={`${itemKey}-icon`}
 to={it.to || '#'}
 className="flex items-center justify-center p-2 text-slate-300 hover:bg-slate-800 rounded transition-colors"
 title={it.label}
 >
 <IconByName name={it.icon} className="w-5 h-5" />
 </Link>
 );
 })}
 </div>
 )}
 </div>
 );
 })}
 
 {!collapsed && (
 <div className="mt-auto p-3 text-[10px] text-[#94a3b8] border-t border-[#1e293b]">
 v2.1.0-uw-dark
 </div>
 )}
 </aside>
 );
}