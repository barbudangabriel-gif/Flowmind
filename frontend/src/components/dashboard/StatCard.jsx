import React from "react";

export default function StatCard({ title, value, change, percentage, subtitle, icon, gradient, sparklineData, isNeutralMetric }) {
  // Utils
  const lerp = (a, b, t) => a + (b - a) * t;
  
  const getMinMax = (arr) => {
    let min = Infinity, max = -Infinity;
    for (const v of arr) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
    if (min === max) { min -= 1; max += 1; }
    return { min, max };
  };
  
  const toPoints = (data, w, h, padX = 2, padY = 2) => {
    const { min, max } = getMinMax(data);
    const len = data.length;
    const dx = (w - padX * 2) / Math.max(1, len - 1);
    const mapY = (v) => padY + (h - padY * 2) * (1 - (v - min) / (max - min));
    return data.map((v, i) => ({ x: padX + i * dx, y: mapY(v), v }));
  };
  
  const pathFromPoints = (points, smoothing = 0.15) => {
    if (points.length === 0) return "";
    if (smoothing <= 0) {
      return points.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(" ");
    }
    const d = [];
    d.push(`M${points[0].x.toFixed(2)},${points[0].y.toFixed(2)}`);
    for (let i = 1; i < points.length; i++) {
      const p0 = points[i - 1];
      const p1 = points[i];
      const cx = lerp(p0.x, p1.x, 0.5);
      const c0x = lerp(p0.x, cx, smoothing);
      const c1x = lerp(p1.x, cx, smoothing);
      d.push(`C${c0x.toFixed(2)},${p0.y.toFixed(2)} ${c1x.toFixed(2)},${p1.y.toFixed(2)} ${p1.x.toFixed(2)},${p1.y.toFixed(2)}`);
    }
    return d.join(" ");
  };
  
  const splitSegments = (points) => {
    const up = [];
    const down = [];
    let curr = [];
    let mode = null;
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1];
      const b = points[i];
      const dir = b.v >= a.v ? 'up' : 'down';
      if (mode !== dir) {
        if (curr.length > 0) {
          (mode === 'up' ? up : down).push(curr);
        }
        curr = [{ x: a.x, y: a.y }, { x: b.x, y: b.y }];
        mode = dir;
      } else {
        curr.push({ x: b.x, y: b.y });
      }
    }
    if (curr.length > 0 && mode) (mode === 'up' ? up : down).push(curr);
    return { up, down };
  };
  
  return (
    <div className={`bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3 hover:border-[#1a1f26] transition-colors shadow-lg ${gradient ? `bg-gradient-to-br ${gradient}` : ''} relative`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{icon}</span>
        <div className="text-xs text-[rgb(252, 251, 255)]">{title}</div>
      </div>
      <div className="text-[18px] text-green-400">{value?.toLocaleString?.() ?? value}</div>
      {subtitle && <div className="text-xs text-gray-400 mt-1">{subtitle}</div>}
      {(change || percentage) && (
        <div className="text-xs mt-2">
          {change && <span className={change >= 0 ? "text-green-400" : "text-red-400"}>{change >= 0 ? "+" : ""}{change.toLocaleString?.() ?? change}</span>}
          {percentage && <span className="ml-2 text-gray-400">({percentage > 0 ? "+" : ""}{percentage}%)</span>}
        </div>
      )}
      
      {/* Sparkline */}
      {sparklineData && sparklineData.length > 0 && (() => {
        const w = 100;
        const h = 20;
        const points = toPoints(sparklineData, w, h);
        
        // Calculate axes positions (middle of range)
        const { min, max } = getMinMax(sparklineData);
        const midValue = (min + max) / 2;
        const mapY = (v) => 2 + (h - 4) * (1 - (v - min) / (max - min));
        const yAxisMid = mapY(midValue);
        
        // Split segments based on position relative to horizontal axis
        const aboveAxis = [];
        const belowAxis = [];
        
        for (let i = 1; i < points.length; i++) {
          const a = points[i - 1];
          const b = points[i];
          const aAbove = a.y < yAxisMid;
          const bAbove = b.y < yAxisMid;
          
          if (aAbove && bAbove) {
            // Both above axis - add to green
            if (aboveAxis.length === 0 || aboveAxis[aboveAxis.length - 1].length === 0) {
              aboveAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
            } else {
              const lastSeg = aboveAxis[aboveAxis.length - 1];
              const lastPoint = lastSeg[lastSeg.length - 1];
              if (lastPoint.x === a.x && lastPoint.y === a.y) {
                lastSeg.push({ x: b.x, y: b.y });
              } else {
                aboveAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
              }
            }
          } else if (!aAbove && !bAbove) {
            // Both below axis - add to red
            if (belowAxis.length === 0 || belowAxis[belowAxis.length - 1].length === 0) {
              belowAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
            } else {
              const lastSeg = belowAxis[belowAxis.length - 1];
              const lastPoint = lastSeg[lastSeg.length - 1];
              if (lastPoint.x === a.x && lastPoint.y === a.y) {
                lastSeg.push({ x: b.x, y: b.y });
              } else {
                belowAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
              }
            }
          } else {
            // Crosses axis - calculate intersection
            const t = (yAxisMid - a.y) / (b.y - a.y);
            const intersectX = a.x + t * (b.x - a.x);
            const intersectPoint = { x: intersectX, y: yAxisMid };
            
            if (aAbove) {
              // a above, b below
              if (aboveAxis.length === 0) {
                aboveAxis.push([{ x: a.x, y: a.y }, intersectPoint]);
              } else {
                const lastSeg = aboveAxis[aboveAxis.length - 1];
                const lastPoint = lastSeg[lastSeg.length - 1];
                if (lastPoint.x === a.x && lastPoint.y === a.y) {
                  lastSeg.push(intersectPoint);
                } else {
                  aboveAxis.push([{ x: a.x, y: a.y }, intersectPoint]);
                }
              }
              belowAxis.push([intersectPoint, { x: b.x, y: b.y }]);
            } else {
              // a below, b above
              if (belowAxis.length === 0) {
                belowAxis.push([{ x: a.x, y: a.y }, intersectPoint]);
              } else {
                const lastSeg = belowAxis[belowAxis.length - 1];
                const lastPoint = lastSeg[lastSeg.length - 1];
                if (lastPoint.x === a.x && lastPoint.y === a.y) {
                  lastSeg.push(intersectPoint);
                } else {
                  belowAxis.push([{ x: a.x, y: a.y }, intersectPoint]);
                }
              }
              aboveAxis.push([intersectPoint, { x: b.x, y: b.y }]);
            }
          }
        }
        
        return (
          <div className="absolute right-4 top-1/2 -translate-y-1/2 h-12 w-1/3">
            <svg width="100%" height="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
              {/* Horizontal axis (baseline) */}
              <line 
                x1="0" 
                y1={yAxisMid} 
                x2={w} 
                y2={yAxisMid} 
                stroke="#6B7280" 
                strokeWidth="0.4" 
                opacity="0.5" 
              />
              
              {/* Above axis segments (green) */}
              {aboveAxis.map((seg, i) => (
                <path
                  key={`above${i}`}
                  d={pathFromPoints(seg, 0.15)}
                  stroke="#10B981"
                  strokeWidth="0.6"
                  strokeDasharray="1 0.8"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.75"
                />
              ))}
              
              {/* Below axis segments (red) */}
              {belowAxis.map((seg, i) => (
                <path
                  key={`below${i}`}
                  d={pathFromPoints(seg, 0.15)}
                  stroke="#EF4444"
                  strokeWidth="0.6"
                  strokeDasharray="1 0.8"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.75"
                />
              ))}
            </svg>
          </div>
        );
      })()}
    </div>
  );
}
