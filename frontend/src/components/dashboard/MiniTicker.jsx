import React from "react";

export default function MiniTicker({ symbol, price, changePct, sparklineData }) {
  const isNegative = changePct < 0;
  const changeColor = isNegative ? "text-red-400" : "text-green-400";
  const changeSign = isNegative ? "" : "+";
  
  // Sparkline utils (simplified from StatCard)
  const getMinMax = (arr) => {
    let min = Infinity, max = -Infinity;
    for (const v of arr) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
    if (min === max) { min -= 1; max += 1; }
    return { min, max };
  };
  
  const toPoints = (data, w, h, padX = 1, padY = 1) => {
    const { min, max } = getMinMax(data);
    const len = data.length;
    const dx = (w - padX * 2) / Math.max(1, len - 1);
    const mapY = (v) => padY + (h - padY * 2) * (1 - (v - min) / (max - min));
    return data.map((v, i) => ({ x: padX + i * dx, y: mapY(v), v }));
  };
  
  const pathFromPoints = (points, smoothing = 0.1) => {
    if (points.length === 0) return "";
    const lerp = (a, b, t) => a + (b - a) * t;
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
  
  // Generate sparkline if data provided
  let sparklineSvg = null;
  if (sparklineData && sparklineData.length > 0) {
    const w = 100;
    const h = 24;
    const points = toPoints(sparklineData, w, h);
    const { min, max } = getMinMax(sparklineData);
    const midValue = (min + max) / 2;
    const mapY = (v) => 2 + (h - 4) * (1 - (v - min) / (max - min));
    const yAxisMid = mapY(midValue);
    
    const aboveAxis = [];
    const belowAxis = [];
    const gapThreshold = 2; // pixels around axis where we add gap
    
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1];
      const b = points[i];
      const aAbove = a.y < yAxisMid;
      const bAbove = b.y < yAxisMid;
      const aNearAxis = Math.abs(a.y - yAxisMid) < gapThreshold;
      const bNearAxis = Math.abs(b.y - yAxisMid) < gapThreshold;
      
      // Skip segment if both points are very close to axis (create visual gap)
      if (aNearAxis && bNearAxis) {
        continue;
      }
      
      if (aAbove && bAbove) {
        if (aboveAxis.length === 0) {
          aboveAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
        } else {
          const lastSeg = aboveAxis[aboveAxis.length - 1];
          const lastPoint = lastSeg[lastSeg.length - 1];
          if (lastPoint.x === a.x) {
            lastSeg.push({ x: b.x, y: b.y });
          } else {
            aboveAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
          }
        }
      } else if (!aAbove && !bAbove) {
        if (belowAxis.length === 0) {
          belowAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
        } else {
          const lastSeg = belowAxis[belowAxis.length - 1];
          const lastPoint = lastSeg[lastSeg.length - 1];
          if (lastPoint.x === a.x) {
            lastSeg.push({ x: b.x, y: b.y });
          } else {
            belowAxis.push([{ x: a.x, y: a.y }, { x: b.x, y: b.y }]);
          }
        }
      } else {
        // Crossing axis - add gap by starting new segment
        const t = (yAxisMid - a.y) / (b.y - a.y);
        const intersectX = a.x + t * (b.x - a.x);
        
        if (aAbove) {
          aboveAxis.push([{ x: a.x, y: a.y }, { x: intersectX - 1, y: yAxisMid }]);
          belowAxis.push([{ x: intersectX + 1, y: yAxisMid }, { x: b.x, y: b.y }]);
        } else {
          belowAxis.push([{ x: a.x, y: a.y }, { x: intersectX - 1, y: yAxisMid }]);
          aboveAxis.push([{ x: intersectX + 1, y: yAxisMid }, { x: b.x, y: b.y }]);
        }
      }
    }
    
    sparklineSvg = (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        <line x1="0" y1={yAxisMid} x2={w} y2={yAxisMid} stroke="#9CA3AF" strokeWidth="0.6" opacity="0.7" />
        {aboveAxis.map((seg, i) => (
          <path 
            key={`a${i}`} 
            d={pathFromPoints(seg, 0.1)} 
            stroke="#10B981" 
            strokeWidth="1.1" 
            strokeDasharray="0.6 0.4"
            fill="none" 
            strokeLinecap="round" 
            opacity="0.9" 
          />
        ))}
        {belowAxis.map((seg, i) => (
          <path 
            key={`b${i}`} 
            d={pathFromPoints(seg, 0.1)} 
            stroke="#EF4444" 
            strokeWidth="1.1" 
            strokeDasharray="0.6 0.4"
            fill="none" 
            strokeLinecap="round" 
            opacity="0.9" 
          />
        ))}
      </svg>
    );
  }
  
  return (
    <div className="flex flex-col gap-0.5">
      <div className="text-[17px] font-semibold text-white tracking-wide">{symbol}</div>
      <div className="flex items-center gap-2">
        <span className={`text-[16px] ${changeColor}`}>
          {price.toFixed(2)}
        </span>
        <span className={`text-[16px] ${changeColor}`}>
          {changeSign}{changePct.toFixed(2)}%
        </span>
      </div>
      <div className="flex items-center mt-1">
        <div className="text-[15px] text-zinc-500">Volume:</div>
        <div className="flex-1 flex justify-center">
          {sparklineSvg}
        </div>
      </div>
    </div>
  );
}
