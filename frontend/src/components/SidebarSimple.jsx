// =============================================
// FlowMind — Sidebar (Safe Minimal)
// =============================================
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
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
function Row({ item, ctx, depth = 0, expandedItems, toggleItem }) {
 const location = useLocation();
 
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

 // Check if this route is active
 const isActive = item.to && location.pathname === item.to;

 const baseClasses = `flex items-center gap-2 px-2 py-1.5 rounded-md text-[13px] font-medium transition-all duration-200 ${depth > 0 ? 'ml-4' : ''}`;
 const stateClasses = disabled 
 ? "opacity-50 pointer-events-none text-slate-500"
 : isActive
 ? "bg-emerald-900/40 text-emerald-400 border-l-2 border-emerald-400 shadow-sm"
 : "text-slate-300 hover:bg-slate-800 hover:text-[rgb(252,251,255)] cursor-pointer";

 const hasChildren = item.children && item.children.length > 0;
 const isExpanded = expandedItems[item.label];
 
 const content = (
 <div className={`${baseClasses} ${stateClasses}`}>
 <span className="flex items-center gap-2 flex-1">
 {hasChildren && (
 <LucideIcons.ChevronRight className={`w-4 h-4 text-slate-400 opacity-60 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`} />
 )}
 <IconByName name={item.icon} className={`w-4 h-4 shrink-0 ${isActive ? 'text-emerald-400' : 'opacity-80'}`} />
 <span className="text-[13px] font-medium truncate">{item.label}</span>
 </span>
 {badge && <Badge b={badge} />}
 </div>
 );
 
 if (hasChildren) {
 // If has children, make it clickable to toggle with smooth animation
 return (
 <>
 <div onClick={() => toggleItem(item.label)} className="cursor-pointer">{content}</div>
 <div 
 className={`overflow-hidden transition-all duration-300 ease-in-out ${
 isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
 }`}
 >
 <div className="mt-1 ml-2 space-y-1">
 {item.children.map((ch, cidx) => (
 <Row key={cidx} item={ch} ctx={ctx} depth={depth + 1} expandedItems={expandedItems} toggleItem={toggleItem} />
 ))}
 </div>
 </div>
 </>
 );
 }
 
 return item.to ? (
 <Link to={item.to} className="block">{content}</Link>
 ) : (
 <div>{content}</div>
 );
}

export default function SidebarSimple({ ctx, collapsed = false }) {
 const location = useLocation();
 
 // State for collapsed sections
 const [collapsedSections, setCollapsedSections] = useState({});
 // State for expanded items with children
 const [expandedItems, setExpandedItems] = useState({});
 // State for showing popover submenu (simple - no complex handlers needed with hover)
 const [activePopover, setActivePopover] = useState(null);
 
 const toggleSection = (sectionTitle) => {
 setCollapsedSections(prev => ({
 ...prev,
 [sectionTitle]: !prev[sectionTitle]
 }));
 };
 
 const toggleItem = (itemLabel) => {
 setExpandedItems(prev => ({
 ...prev,
 [itemLabel]: !prev[itemLabel]
 }));
 };
 
 // Provide safe defaults
 const safeCtx = {
 role: ctx?.role || "user",
 flags: ctx?.flags || {},
 metrics: ctx?.metrics || {},
 portfolios: Array.isArray(ctx?.portfolios) ? ctx.portfolios : [],
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
 <aside className={`border-r border-[#1e293b] bg-gradient-to-b from-[#0f1419] to-[#0a0e1a] h-screen overflow-y-auto transition-all duration-300 ${collapsed ? 'w-16' : 'w-[226px]'} scrollbar-hide`} style={{ borderRightWidth: '1px', fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial', fontSize: '13px', lineHeight: '20.8px', fontWeight: '400' }}>
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
 className={`w-full flex items-center gap-2 px-1 mb-2 text-[13px] uppercase tracking-wide font-semibold ${sec.isComplete ? 'text-cyan-400' : 'text-[#94a3b8]'} hover:text-[rgb(252, 251, 255)] transition-all duration-200`}
 >
 <LucideIcons.ChevronRight 
 className={`w-4 h-4 text-slate-400 transition-transform duration-300 ease-in-out ${isCollapsed ? '' : 'rotate-90'}`}
 />
 <span>{sec.title}</span>
 </button>
 )}
 
 {/* Section items - full view when expanded with smooth animation */}
 {!collapsed && (
 <div 
 className={`overflow-hidden transition-all duration-300 ease-in-out ${
 isCollapsed ? 'max-h-0 opacity-0' : 'max-h-[2000px] opacity-100'
 }`}
 >
 <div className="space-y-1">
 {(sec.items || []).map((it, idx) => (
 <Row key={`${sec.title}-${idx}`} item={it} ctx={safeCtx} expandedItems={expandedItems} toggleItem={toggleItem} />
 ))}
 </div>
 </div>
 )}
 
 {/* Show only icons when sidebar collapsed - no arrows */}
 {collapsed && (
 <div className="space-y-2">
 {(sec.items || []).map((it, idx) => {
 const itemKey = `${sec.title}-${idx}`;
 const hasChildren = it.children && it.children.length > 0;
 const isActive = activePopover === itemKey;
 const isItemActive = it.to && location.pathname === it.to;
 const isChildActive = hasChildren && it.children.some(ch => ch.to && location.pathname === ch.to);
 
 // Regular item without children - just show icon with link
 if (!hasChildren) {
 return (
 <Link
 key={itemKey}
 to={it.to || '#'}
 className={`flex items-center justify-center p-2 rounded transition-all duration-200 ${
 isItemActive 
 ? 'bg-emerald-900/40 text-emerald-400 ring-2 ring-emerald-400/50'
 : 'text-slate-300 hover:bg-slate-800'
 }`}
 title={it.label}
 >
 <IconByName name={it.icon} className="w-4 h-4" />
 </Link>
 );
 }
 
 // Item with children - show popover on hover
 return (
 <div 
 key={itemKey} 
 className="relative"
 onMouseEnter={() => setActivePopover(itemKey)}
 onMouseLeave={() => setActivePopover(null)}
 >
 {/* Icon button */}
 <div
 className={`flex items-center justify-center p-2 rounded transition-all duration-200 relative cursor-pointer ${
 isActive 
 ? 'bg-slate-800 text-emerald-400' 
 : isChildActive
 ? 'bg-emerald-900/40 text-emerald-400 ring-2 ring-emerald-400/50'
 : 'text-slate-300 hover:bg-slate-800'
 }`}
 title={it.label}
 >
 <IconByName name={it.icon} className="w-4 h-4" />
 {/* Green dot indicator when has active children */}
 {isChildActive && (
 <span className="absolute bottom-1 right-1 w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
 )}
 </div>
 
 {/* Popover menu with smooth fade-in animation */}
 {isActive && (
 <div 
 className="absolute left-full top-0 ml-2 z-[100] min-w-[200px] animate-in fade-in slide-in-from-left-2 duration-200"
 style={{ backgroundColor: '#1e293b' }}
 >
 <div className="bg-[#1e293b] border border-[#334155] rounded-lg shadow-2xl py-2 backdrop-blur-sm">
 {/* Header */}
 <div className="px-3 py-2 text-[13px] font-medium text-slate-400 uppercase border-b border-[#334155] flex items-center gap-2">
 <IconByName name={it.icon} className="w-3.5 h-3.5" />
 {it.label}
 </div>
 {/* Children items */}
 {it.children.map((ch, cidx) => {
 const isChildActive = ch.to && location.pathname === ch.to;
 return (
 <Link
 key={cidx}
 to={ch.to || '#'}
 className={`flex items-center gap-2 px-3 py-2.5 text-[13px] font-medium transition-all duration-200 ${
 isChildActive
 ? 'bg-emerald-900/40 text-emerald-400 border-l-2 border-emerald-400'
 : 'text-slate-300 hover:bg-slate-700/50 hover:text-[rgb(252,251,255)]'
 }`}
 >
 <IconByName name={ch.icon} className={`w-4 h-4 ${isChildActive ? 'text-emerald-400' : ''}`} />
 <span>{ch.label}</span>
 </Link>
 );
 })}
 </div>
 </div>
 )}
 </div>
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