import { useEffect, useRef, useState } from "react";
import { withRetry } from "../../utils/withRetry";

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "";

async function fetchPayoffData({ symbol, legs, dte = 30, spot, ivMult = 1.0, rangePct = 0.15 }) {
  try {
    const payload = {
      symbol,
      expiry: new Date(Date.now() + dte * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      dte,
      legs: legs || [],
      qty: 1,
      iv_mult: ivMult,
      range_pct: rangePct,
      mode: 'pl_usd',
      strategyId: 'custom'
    };

    const response = await withRetry(() => 
      fetch(`${API}/api/builder/price`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.json();
      })
    );

    return response?.chart?.series?.[0]?.xy || [];
  } catch (error) {
    console.warn('HoverDiagram fetch failed:', error);
    return [];
  }
}

export default function HoverDiagram({ 
  symbol, 
  legs, 
  dte = 30, 
  spot, 
  width = 220, 
  height = 88 
}) {
  const [data, setData] = useState(null);
  const mounted = useRef(true);

  useEffect(() => { 
    mounted.current = true; 
    return () => { mounted.current = false; }; 
  }, []);

  useEffect(() => {
    if (!legs || legs.length === 0 || !spot) return;
    
    let alive = true;
    
    (async () => {
      try {
        const series = await fetchPayoffData({ symbol, legs, dte, spot });
        if (!alive || !mounted.current) return;
        setData(series);
      } catch (error) {
        if (!alive || !mounted.current) return;
        console.warn('HoverDiagram error:', error);
        setData([]);
      }
    })();

    return () => { alive = false; };
  }, [symbol, JSON.stringify(legs), dte, spot]);

  if (!data) {
    return (
      <div 
        className="rounded-lg bg-slate-900/60 flex items-center justify-center"
        style={{ width, height }}
      >
        <div className="text-xs text-slate-500">Loading...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div 
        className="rounded-lg bg-slate-900/60 flex items-center justify-center"
        style={{ width, height }}
      >
        <div className="text-xs text-slate-500">No data</div>
      </div>
    );
  }

  // Mini SVG payoff chart with unified P&L palette
  const xs = data.map(p => p[0]);
  const ys = data.map(p => p[1]);
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  
  const sx = v => ((v - xMin) / (xMax - xMin || 1)) * width;
  const sy = v => height - ((v - yMin) / (yMax - yMin || 1)) * height;
  
  // Create profit and loss fill paths
  const createFillPaths = () => {
    const zeroY = sy(0);
    const profitPoints = [];
    const lossPoints = [];
    
    // Start both paths at zero line
    profitPoints.push(`M0,${zeroY}`);
    lossPoints.push(`M0,${zeroY}`);
    
    data.forEach((p, i) => {
      const x = sx(p[0]);
      const y = sy(p[1]);
      
      if (p[1] >= 0) {
        profitPoints.push(`${i === 0 ? 'M' : 'L'}${x},${y}`);
      } else {
        lossPoints.push(`${i === 0 ? 'M' : 'L'}${x},${y}`);
      }
    });
    
    // Close to zero line
    profitPoints.push(`L${width},${zeroY}Z`);
    lossPoints.push(`L${width},${zeroY}Z`);
    
    return {
      profitPath: profitPoints.join(' '),
      lossPath: lossPoints.join(' ')
    };
  };
  
  const { profitPath, lossPath } = createFillPaths();
  const mainPath = data.map((p, i) => 
    (i ? "L" : "M") + sx(p[0]) + "," + sy(p[1])
  ).join(" ");

  return (
    <svg 
      width={width} 
      height={height} 
      className="rounded-lg bg-slate-900/60"
    >
      {/* Loss region fill (red translucent) */}
      {yMin < 0 && (
        <path 
          d={lossPath}
          fill="var(--pl-loss-fill)"
          opacity="0.7"
        />
      )}
      
      {/* Profit region fill (green translucent) */}
      {yMax > 0 && (
        <path 
          d={profitPath}
          fill="var(--pl-profit-fill)"
          opacity="0.7"
        />
      )}
      
      {/* Zero line with accent */}
      {0 >= yMin && 0 <= yMax && (
        <line 
          x1={0} 
          y1={sy(0)} 
          x2={width} 
          y2={sy(0)} 
          stroke="var(--pl-zero-axis)"
          strokeDasharray="3 3"
          strokeWidth="1"
        />
      )}
      
      {/* P&L payoff line */}
      <path 
        d={mainPath} 
        fill="none" 
        stroke="var(--pl-profit-line)"
        strokeWidth="1.5" 
      />
    </svg>
  );
}