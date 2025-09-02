// =============================================
// FlowMind — Sidebar (Safe Minimal)
// =============================================
import React from 'react';
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

  const baseClasses = `flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors ${depth > 0 ? 'ml-4' : ''}`;
  const stateClasses = disabled 
    ? "opacity-50 pointer-events-none text-gray-400"
    : "text-gray-700 hover:bg-gray-100 cursor-pointer";

  const content = (
    <div className={`${baseClasses} ${stateClasses}`}>
      <span className="flex items-center gap-2 flex-1">
        <IconByName name={item.icon} className="w-4 h-4 shrink-0 opacity-80" />
        <span className="text-sm truncate">{item.label}</span>
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

export default function SidebarSimple({ ctx }) {
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
    <aside className="w-64 border-r bg-white h-screen overflow-y-auto">
      <div className="px-3 py-3 border-b">
        <div className="text-lg font-semibold text-gray-900">FlowMind</div>
        <div className="text-[11px] text-gray-500">Sidebar (Safe Minimal)</div>
      </div>
      
      {nav.map((sec, i) => (
        <div key={`sec-${i}`} className="px-2 py-3">
          <div className="px-1 mb-2 text-[11px] uppercase tracking-wide text-gray-400">
            {sec.title}
          </div>
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
        </div>
      ))}
      
      <div className="mt-auto p-3 text-[10px] text-gray-400 border-t">
        v2.1.0-minimal
      </div>
    </aside>
  );
}