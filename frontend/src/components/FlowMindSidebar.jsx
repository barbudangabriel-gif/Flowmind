// FlowMind — Sidebar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
import { buildNav } from '../lib/nav';
import {
 Tooltip,
 TooltipContent,
 TooltipProvider,
 TooltipTrigger,
} from './ui/tooltip';

// Badge component
function Badge({ text, tone = "default" }) {
 const toneClasses = {
 default: "bg-gray-100 text-gray-800 border-gray-300",
 success: "bg-green-100 text-green-800 border-green-300", 
 warn: "bg-yellow-100 text-yellow-800 border-yellow-300",
 danger: "bg-red-100 text-red-800 border-red-300",
 beta: "bg-purple-100 text-purple-800 border-purple-300",
 live: "bg-emerald-100 text-emerald-800 border-emerald-300 animate-pulse",
 verified: "bg-blue-100 text-blue-800 border-blue-300"
 };

 return (
 <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${toneClasses[tone]}`}>
 {text}
 </span>
 );
}

// Icon component with Lucide fallback
function Icon({ name }) {
 if (!name) return null;
 
 const IconComponent = LucideIcons[name];
 if (!IconComponent) {
 console.warn(`Icon '${name}' not found in lucide-react`);
 return <LucideIcons.Circle className="w-4 h-4" />;
 }
 
 return <IconComponent className="w-4 h-4" />;
}

// Row renderer (recursive for children)
function Row({ item, ctx, depth = 0 }) {
 // Check visibility
 if (item.visible && !item.visible(ctx)) {
 return null;
 }

 // Check disabled state
 const disabled = item.disabled?.(ctx) ?? false;
 const reason = disabled ? item.disabledReason?.(ctx) : undefined;

 // Resolve badge (function or object)
 const badge = typeof item.badge === 'function' ? item.badge(ctx) : item.badge;

 // Base styling
 const baseClasses = `
 flex items-center gap-2 px-2 py-1.5 rounded-md text-xl transition-colors
 ${depth > 0 ? 'ml-4' : ''}
 `;

 const activeClasses = disabled 
 ? "opacity-50 pointer-events-none text-muted-foreground"
 : "text-foreground hover:bg-accent hover:text-accent-foreground cursor-pointer";

 const content = (
 <div className={`${baseClasses} ${activeClasses}`}>
 <Icon name={item.icon} />
 <span className="flex-1">{item.label}</span>
 {badge && <Badge text={badge.text} tone={badge.tone} />}
 </div>
 );

 // Render logic based on disabled/to states
 if (disabled || !item.to) {
 return reason ? (
 <TooltipProvider delayDuration={0}>
 <Tooltip>
 <TooltipTrigger asChild>
 <div>{content}</div>
 </TooltipTrigger>
 <TooltipContent side="right" className="max-w-[220px] text-lg">
 {reason}
 </TooltipContent>
 </Tooltip>
 </TooltipProvider>
 ) : (
 <div>{content}</div>
 );
 }
 
 return (
 <Link to={item.to} className="block">
 {content}
 </Link>
 );
}

// Section renderer
function Section({ sec, ctx }) {
 return (
 <div className="px-2 py-3">
 <div className="px-1 mb-2 text-[11px] uppercase tracking-wide text-muted-foreground">
 {sec.title}
 </div>
 <div className="space-y-1">
 {sec.items.map((it, idx) => (
 <div key={`${sec.title}-${idx}`}>
 <Row item={it} ctx={ctx} />
 {/* children (nested) */}
 {it.children && it.children.length > 0 && (
 <div className="mt-1 ml-2 space-y-1">
 {it.children.map((ch, cidx) => (
 <Row key={`${sec.title}-${idx}-ch-${cidx}`} item={ch} ctx={ctx} depth={1} />
 ))}
 </div>
 )}
 </div>
 ))}
 </div>
 </div>
 );
}

export default function FlowMindSidebar({ ctx }) {
 const nav = React.useMemo(() => buildNav(ctx), [ctx]);
 
 return (
 <aside className="w-64 border-r bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 h-screen overflow-y-auto" style={{fontFamily: "'Arial Black', 'Impact', sans-serif", fontSize: '13px', fontWeight: 'bold'}}>
 {/* Brand */}
 <div className="px-3 py-3 border-b">
 <div className="text-3xl font-medium">FlowMind</div>
 <div className="text-[11px] text-muted-foreground">Where Data Flows, Intelligence Grows</div>
 </div>
 
 {/* Sections */}
 {nav.map((sec, i) => (
 <Section key={`sec-${i}`} sec={sec} ctx={ctx} />
 ))}
 
 {/* Footer */}
 <div className="mt-auto p-3 text-[10px] text-muted-foreground border-t">
 v{import.meta.env.VITE_APP_VERSION ?? "2.1.0"}
 </div>
 </aside>
 );
}