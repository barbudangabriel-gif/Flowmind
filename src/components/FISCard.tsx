import React, { useEffect, useState } from "react";
import { getFISScore, getIVX, getGEX, getFlow } from "../lib/api";

declare global {
  interface ImportMeta {
    env: Record<string, string | undefined>;
  }
}

const SYMBOL = import.meta.env.VITE_FIS_DEFAULT_SYMBOL || "TSLA";

function badge(n: number|null) {
  if (n==null) return "—";
  if (n<40) return "🔴";
  if (n<60) return "🟡";
  if (n<80) return "🟢";
  return "🟩";
}

export default function FISCard() {
  const [score, setScore] = useState<number|null>(null);
  const [ivx, setIVX] = useState<{ivx:string; rank:string} | null>(null);
  const [walls, setWalls] = useState<{call:number; put:number}|null>(null);
  const [flow, setFlow] = useState<{bias:string; sweeps:number; blocks:number}|null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string|null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [s, i, g, f] = await Promise.all([
          getFISScore(SYMBOL), getIVX(SYMBOL), getGEX(SYMBOL), getFlow(SYMBOL)
        ]);
        if (!alive) return;
        setScore(typeof s.score === "number" ? s.score : null);
        setIVX({ ivx: i.ivx, rank: i.rank });
        setWalls(g.walls);
        setFlow({ bias: f.bias, sweeps: f.sweeps, blocks: f.blocks });
        setErr(null);
      } catch (e:any) {
        setErr(e?.message || "network");
      } finally {
        setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  return (
    <div style={styles.wrap}>
      <h1 style={styles.h1}>Flowmind Investment Score (FIS)</h1>
      <div style={styles.row}>
        <div style={styles.scoreCard}>
          <div style={styles.scoreLabel}>Score</div>
          <div style={styles.scoreValue}>
            {loading ? "…" : (score ?? "—")} <span>{badge(score)}</span>
          </div>
          <div style={styles.symbol}>Symbol: <b>{SYMBOL}</b></div>
          {err && <div style={styles.err}>❌ {err}</div>}
          {!err && !loading && <div style={styles.ok}>✅ API OK</div>}
        </div>

        <div style={styles.grid}>
          <div style={styles.tile}>
            <div style={styles.tileTitle}>Volatility State</div>
            {ivx ? (
              <div>IVX: <b>{ivx.ivx}</b> · Rank: <b>{ivx.rank}</b></div>
            ) : loading ? "…" : "—"}
          </div>
          <div style={styles.tile}>
            <div style={styles.tileTitle}>Dealer Positioning</div>
            {walls ? (
              <div>Call wall: <b>{walls.call}</b> · Put wall: <b>{walls.put}</b></div>
            ) : loading ? "…" : "—"}
          </div>
          <div style={styles.tile}>
            <div style={styles.tileTitle}>Flow Bias</div>
            {flow ? (
              <div>Bias: <b>{flow.bias}</b> · Sweeps: <b>{flow.sweeps}</b> · Blocks: <b>{flow.blocks}</b></div>
            ) : loading ? "…" : "—"}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrap: { fontFamily: "ui-sans-serif, system-ui, -apple-system", padding: 16, maxWidth: 980, margin: "0 auto" },
  h1: { fontSize: 24, marginBottom: 12 },
  row: { display: "flex", gap: 16, alignItems: "stretch", flexWrap: "wrap" },
  scoreCard: { flex: "0 0 260px", border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, boxShadow: "0 1px 4px rgba(0,0,0,.05)" },
  scoreLabel: { fontSize: 12, color: "#6b7280", textTransform: "uppercase", letterSpacing: 0.6 },
  scoreValue: { fontSize: 36, fontWeight: 700, margin: "6px 0 8px" },
  symbol: { fontSize: 13, color: "#374151" },
  err: { marginTop: 8, color: "#b91c1c", fontSize: 13 },
  ok: { marginTop: 8, color: "#065f46", fontSize: 13 },
  grid: { display: "grid", gridTemplateColumns: "repeat(2, minmax(220px, 1fr))", gap: 16, flex: "1 1 480px" },
  tile: { border: "1px solid #e5e7eb", borderRadius: 12, padding: 14, minHeight: 84, boxShadow: "0 1px 4px rgba(0,0,0,.05)" },
  tileTitle: { fontSize: 13, color: "#6b7280", marginBottom: 6, textTransform: "uppercase", letterSpacing: 0.6 }
};
