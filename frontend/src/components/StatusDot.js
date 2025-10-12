import React from "react";

export default function StatusDot({ score=0, size=8 }) {
  const v = Math.max(0, Math.min(100, score));
  const color = v >= 60 ? "#16a34a" : v >= 40 ? "#f59e0b" : "#ef4444";
  return (
    <span style={{
      display:"inline-block", width:size, height:size, borderRadius:"50%",
      background: color, boxShadow:`0 0 0 2px #fff inset, 0 0 0 1px ${color}33`
    }} />
  );
}
