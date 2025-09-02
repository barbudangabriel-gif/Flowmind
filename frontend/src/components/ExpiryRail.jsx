// components/ExpiryRail.jsx
import React, { useEffect, useMemo, useRef } from "react";
import { isMonthlyOpexNY } from '../utils/date';

export default function ExpiryRail({ 
  expirations, 
  value, 
  onChange, 
  variant = 'optimize',
  showOpexMarker = false 
}) {
  const ref = useRef(null);
  const idx = useMemo(() => Math.max(0, expirations.indexOf(value)), [expirations, value]);
  const wrap = variant === 'builder';

  // group by month for builder variant
  const groups = useMemo(() => {
    if (!wrap) return null;
    const map = new Map();
    expirations.forEach(iso => {
      const d = new Date(iso + "T00:00:00Z");
      const key = d.toLocaleString(undefined, { month: 'short', year: '2-digit' });
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(iso);
    });
    return [...map.entries()];
  }, [expirations, wrap]);

  // drag to scroll (only for optimize variant)
  useEffect(() => {
    if (wrap) return; // no drag for builder variant
    
    const el = ref.current; 
    if (!el) return;
    
    let sx = 0, sl = 0, dragging = false;
    const md = (e) => { dragging = true; sx = e.pageX; sl = el.scrollLeft; };
    const mm = (e) => { if (dragging) { el.scrollLeft = sl - (e.pageX - sx); } };
    const mu = () => dragging = false;
    
    el.addEventListener('mousedown', md);
    window.addEventListener('mousemove', mm);
    window.addEventListener('mouseup', mu);
    
    return () => { 
      el.removeEventListener('mousedown', md); 
      window.removeEventListener('mousemove', mm); 
      window.removeEventListener('mouseup', mu); 
    };
  }, [wrap]);

  // wheel horizontal (only for optimize variant)
  useEffect(() => {
    if (wrap) return;
    
    const el = ref.current; 
    if (!el) return;
    
    const onWheel = (e) => { 
      e.preventDefault();
      el.scrollLeft += (e.deltaY || e.deltaX); 
    };
    
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, [wrap]);

  // keyboard nav: [ and ]
  useEffect(() => {
    const h = (e) => {
      if (e.key === '[') onChange(expirations[Math.max(0, idx - 1)]);
      if (e.key === ']') onChange(expirations[Math.min(expirations.length - 1, idx + 1)]);
    };
    
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [idx, expirations, onChange]);

  return (
    <div className="w-full select-none">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>Expirations</span>
        <span>{value}</span>
      </div>

      {!wrap ? (
        // OPTIMIZE: rail horizontal with scroll
        <div ref={ref} className="flex gap-2 overflow-x-auto pb-1 cursor-grab active:cursor-grabbing">
          {expirations.map(iso => (
            <ExpiryBtn 
              key={iso} 
              iso={iso} 
              active={iso === value} 
              onClick={onChange}
              showOpexMarker={showOpexMarker}
            />
          ))}
        </div>
      ) : (
        // BUILDER: all expirations wrapped, grouped by month
        <div className="flex flex-wrap gap-4">
          {groups.map(([month, days]) => (
            <div key={month} className="min-w-[200px]">
              <div className="text-xs text-slate-400 mb-2 font-medium">{month}</div>
              <div className="flex flex-wrap gap-2">
                {days.map(iso => (
                  <ExpiryBtn 
                    key={iso} 
                    iso={iso} 
                    active={iso === value} 
                    onClick={onChange}
                    showOpexMarker={showOpexMarker}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ExpiryBtn({ iso, active, onClick, showOpexMarker }) {
  const d = new Date(iso + "T00:00:00Z");
  const opex = showOpexMarker && isMonthlyOpexNY(iso);
  const day = d.getDate();
  
  // Enhanced tooltip for OPEX
  const getTooltip = () => {
    if (opex) {
      return `${iso} · Monthly OPEX (3rd Friday)`;
    }
    return iso;
  };

  return (
    <button
      onClick={() => onClick(iso)}
      className={[
        "relative px-3 py-1 rounded-md text-sm transition",
        active ? "bg-sky-500 text-white" : "bg-slate-700/60 hover:bg-slate-600 text-slate-200"
      ].join(" ")}
      title={getTooltip()}
      aria-label={getTooltip()}
    >
      {day}
      {opex && (
        <span 
          className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-amber-400" 
          aria-hidden 
          title="Monthly OPEX (3rd Friday)"
        />
      )}
    </button>
  );
}