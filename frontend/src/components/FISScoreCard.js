import React, { useMemo, useRef, useState } from "react";
import { ResponsiveContainer, LineChart, Line, Tooltip as RTooltip } from "recharts";

// Debounce util
function useDebounced(fn, ms = 250) {
  const t = useRef();
  return (...args) => {
    if (t.current) clearTimeout(t.current);
    t.current = setTimeout(() => fn(...args), ms);
  };
}

// Exponential moving average
function ema(data, alpha) {
  if (!data?.length) return [];
  let res = [data[0]];
  for (let i = 1; i < data.length; ++i) {
    res.push({
      ...data[i],
      score: alpha * data[i].score + (1 - alpha) * res[i - 1].score
    });
  }
  return res;
}

export default function FISScoreCard({ rawData, factors, ts, symbol, lineColor = "#2563eb" }) {
  const [days, setDays] = useState(7);
  const [useSmoothing, setUseSmoothing] = useState(false);
  const [alpha, setAlpha] = useState(0.3);
  const data = useMemo(() => useSmoothing ? ema(rawData, alpha) : rawData, [rawData, useSmoothing, alpha]);

  return (
    <div style={{ padding: 18, background: "#fff", borderRadius: 12, boxShadow: "0 1px 4px #0001", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontSize: 12, opacity: .7 }}>Trend ({days}d)</div>
          <Seg active={days === 7} onClick={() => setDays(7)}>7d</Seg>
          <Seg active={days === 30} onClick={() => setDays(30)}>30d</Seg>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <label
            style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, opacity: .95, cursor: "pointer" }}
            aria-label="Toggle smoothing"
            title="Toggle smoothing"
          >
            <input
              type="checkbox"
              checked={useSmoothing}
              onChange={e => setUseSmoothing(e.target.checked)}
            />
            Smoothed
          </label>
          {useSmoothing && (
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12 }}>
              α:
              <select
                aria-label="Smoothing alpha"
                value={alpha}
                onChange={e => setAlpha(parseFloat(e.target.value))}
                style={{ padding: "2px 6px", border: "1px solid #ddd", borderRadius: 6 }}
              >
                <option value={0.2}>0.2</option>
                <option value={0.3}>0.3</option>
                <option value={0.5}>0.5</option>
              </select>
            </span>
          )}
        </div>
      </div>
      <div style={{ height: 64, marginTop: 4 }}>
        {!data?.length ? (
          <div style={{
            height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 12, color: "#6b7280", border: "1px dashed #e5e7eb", borderRadius: 8
          }}>
            No history yet. Use Refresh.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <Line type="monotone" dataKey="score" stroke={lineColor} strokeWidth={2} dot={false} />
              <RTooltip
                formatter={v => [`Score: ${v}`, '']}
                labelFormatter={v => new Date(v * 1000).toLocaleDateString()}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
      <div style={{ height: 12 }} />
      <Bar label="Tech" value={factors.tech} />
      <Bar label="Vol Surface" value={factors.vol_surface ?? factors.vol} />
      <Bar label="Flow" value={factors.flow} />
      <div style={{ marginTop: 10, fontSize: 12, opacity: .7 }}>
        <div>Updated: {ts}</div>
        <div>Endpoint: <code>/investment-scoring/advanced/{symbol}</code></div>
      </div>
    </div>
  );
}

function Seg({ active, children, onClick }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      style={{
        border: "1px solid #ddd",
        background: active ? "#111827" : "#fff",
        color: active ? "#fff" : "#111",
        borderRadius: 6, padding: "2px 8px", fontSize: 12, cursor: "pointer",
        outline: "none", boxShadow: "none"
      }}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      onFocus={e => { e.currentTarget.style.boxShadow = "0 0 0 2px #2563eb"; }}
      onBlur={e => { e.currentTarget.style.boxShadow = "none"; }}
    >
      {children}
    </button>
  );
}

function Seg({active, children, onClick}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      style={{
        border:"1px solid #ddd",
        background: active ? "#111827" : "#fff",
        color: active ? "#fff" : "#111",
        borderRadius:6, padding:"2px 8px", fontSize:12, cursor:"pointer",
        outline:"none", boxShadow: "none"
      }}
      onKeyDown={e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); onClick(); } }}
      onFocus={e=>{ e.currentTarget.style.boxShadow="0 0 0 2px #2563eb"; }}
      onBlur={e=>{ e.currentTarget.style.boxShadow="none"; }}
    >
      {children}
    </button>
  );
}
