import React, { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import SymbolPicker from "./SymbolPicker";

type S = "idle" | "loading" | "ready" | "error";

export default function FISCard() {
  const initial = useMemo(() => localStorage.getItem("fis_symbol") || "TSLA", []);
  const [symbol, setSymbol] = useState(initial);
  const [state, setState] = useState<S>("idle");
  const [score, setScore] = useState<number|null>(null);
  const [ivx, setIVX] = useState<{ivx:string; rank:string} | null>(null);
  const [walls, setWalls] = useState<{call:number; put:number}|null>(null);
  const [flow, setFlow] = useState<{bias:string; sweeps:number; blocks:number}|null>(null);
  const [err, setErr] = useState<string|null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      setState("loading"); setErr(null);
      try {
        const [s, i, g, f] = await Promise.all([
          api.score(symbol), api.ivx(symbol), api.gex(symbol), api.flow(symbol)
        ]);
        if (!alive) return;
        setScore(typeof s.score === "number" ? s.score : null);
        setIVX({ ivx: i.ivx, rank: i.rank });
        setWalls(g.walls);
        setFlow({ bias: f.bias, sweeps: f.sweeps, blocks: f.blocks });
        setState("ready");
      } catch (e:any) {
        if (!alive) return;
        setErr(e?.message || "network");
        setState("error");
      }
    })();
    return () => { alive = false; };
  }, [symbol]);

  return (
    <div style={styles.wrap}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12}}>
        <h1 style={styles.h1}>Flowmind Investment Score</h1>
        <SymbolPicker value={symbol} onChange={setSymbol}/>
      </div>

      <div style={styles.row}>
        <div style={styles.scoreCard}>
          <div style={styles.scoreLabel}>Score</div>
          <div style={styles.scoreValue}>
            {state==="loading" ? "…" : (score ?? "—")} <span>{badge(score)}</span>
          </div>
          <div style={styles.symbol}>Symbol: <b>{symbol}</b></div>
          {state==="error" && <div style={styles.err}>❌ {err}</div>}
          {state==="ready" && <div style={styles.ok}>✅ API OK</div>}
        </div>

        <div style={styles.grid}>
          <Tile title="Volatility State">
            {state==="loading" ? "…" : ivx ? <>IVX: <b>{ivx.ivx}</b> · Rank: <b>{ivx.rank}</b></> : "—"}
          </Tile>
          <Tile title="Dealer Positioning">
            {state==="loading" ? "…" : walls ? <>Call wall: <b>{walls.call}</b> · Put wall: <b>{walls.put}</b></> : "—"}
          </Tile>
          <Tile title="Flow Bias">
            {state==="loading" ? "…" : flow ? <>Bias: <b>{flow.bias}</b> · Sweeps: <b>{flow.sweeps}</b> · Blocks: <b>{flow.blocks}</b></> : "—"}
          </Tile>
        </div>
      </div>
    </div>
  );
}

function Tile({ title, children }:{title:string; children:React.ReactNode}) {
  return (
    <div style={styles.tile}>
      <div style={styles.tileTitle}>{title}</div>
      <div>{children}</div>
    </div>
  );
}

function badge(n: number|null) {
  if (n==null) return "—";
  if (n<40) return "🔴";
  if (n<60) return "🟡";
  if (n<80) return "🟢";
  return "🟩";
}

const styles: Record<string, React.CSSProperties> = {
  wrap: { fontFamily: "ui-sans-serif, system-ui, -apple-system", padding: 16, maxWidth: 980, margin: "0 auto" },
  h1: { fontSize: 20, margin: 0 },
  row: { display: "flex", gap: 16, alignItems: "stretch", flexWrap: "wrap", marginTop: 8 },
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
