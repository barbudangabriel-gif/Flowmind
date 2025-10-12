import React from "react";
import Tooltip from "./Tooltip";
import StatusDot from "./StatusDot";

export default function FISBadge({ score, factors={}, size="sm", title="FIS" }) {
  const v = Math.max(0, Math.min(100, score ?? 0));
  const bg = v >= 60 ? "#DCFCE7" : v >= 40 ? "#FEF3C7" : "#FEE2E2";
  const fg = v >= 60 ? "#166534" : v >= 40 ? "#92400E" : "#991B1B";
  const pad = size === "sm" ? "2px 8px" : "4px 10px";
  const fs  = size === "sm" ? 12 : 14;

  const content = (
    <div style={{display:"grid", gap:6}}>
      <div style={{opacity:.8}}>Breakdown</div>
      <Row k="Tech" v={factors.tech}/>
      <Row k="Vol"  v={factors.vol_surface ?? factors.vol}/>
      <Row k="Flow" v={factors.flow}/>
    </div>
  );

  return (
    <Tooltip content={content} delay={150}>
      <span style={{
        display:"inline-flex", alignItems:"center", gap:8,
        background:bg, color:fg, padding:pad, borderRadius:999, fontWeight:600, fontSize:fs
      }}>
        <StatusDot score={v} />
        <span>{title}</span>
        <span style={{
          background:"#fff", color:fg, padding:"1px 6px", borderRadius:999,
          border:`1px solid ${fg}20`, minWidth:28, textAlign:"center"
        }}>{v}</span>
      </span>
    </Tooltip>
  );
}

function Row({k, v=0}){
  const val = Math.max(0, Math.min(100, v));
  return (
    <div>
      <div style={{display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4}}>
        <span>{k}</span><span>{val}</span>
      </div>
      <div style={{background:"#374151", height:6, borderRadius:4}}>
        <div style={{width:`${val}%`, height:6, borderRadius:4, background:"#60A5FA"}} />
      </div>
    </div>
  );
}
