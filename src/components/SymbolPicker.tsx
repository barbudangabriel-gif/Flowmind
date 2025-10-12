import React, { useEffect, useState } from "react";

type Props = { value: string; onChange: (s: string) => void; };

const PRESETS = ["TSLA","AAPL","NVDA","MSFT","AMD"];

export default function SymbolPicker({ value, onChange }: Props) {
  const [sym, setSym] = useState(value || "TSLA");

  useEffect(() => setSym(value), [value]);
  useEffect(() => {
    localStorage.setItem("fis_symbol", sym);
  }, [sym]);

  return (
    <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
      <div>Symbol:</div>
      {PRESETS.map(p => (
        <button key={p}
          onClick={() => { setSym(p); onChange(p); }}
          style={{
            padding:"6px 10px",
            borderRadius:8,
            border: sym===p ? "2px solid #111827" : "1px solid #d1d5db",
            background: sym===p ? "#eef2ff" : "#fff",
            cursor:"pointer"
          }}>
          {p}
        </button>
      ))}
      <input
        value={sym}
        onChange={e => setSym(e.target.value.toUpperCase())}
        onBlur={() => onChange(sym)}
        placeholder="CUSIP/Ticker"
        style={{ padding:"6px 10px", border:"1px solid #d1d5db", borderRadius:8, width:120 }}
      />
    </div>
  );
}
