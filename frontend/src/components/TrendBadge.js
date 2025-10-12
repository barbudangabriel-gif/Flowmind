// ▲ / ▼ / ▬ + culoare dupa trend (%)
export default function TrendBadge({ changePct=0, title }) {
  const up   = changePct > 0.5;
  const down = changePct < -0.5;
  const color = up ? "#16a34a" : down ? "#ef4444" : "#6b7280";
  const bg    = up ? "#DCFCE7" : down ? "#FEE2E2" : "#F3F4F6";
  const sign  = up ? "▲" : down ? "▼" : "▬";
  const pct   = (changePct).toFixed(1);
  const label = title || `Trend ${changePct >= 0 ? '+' : ''}${pct}%`;

  return (
    <span
      role="status"
      aria-live="polite"
      aria-label={label}
      title={label}
      style={{
        display:"inline-flex",alignItems:"center",gap:6,
        background:bg,color, padding:"2px 8px", borderRadius:999,
        fontWeight:600, fontSize:12
      }}
    >
      <span aria-hidden="true">{sign}</span>
      <span>{pct}%</span>
    </span>
  );
}
