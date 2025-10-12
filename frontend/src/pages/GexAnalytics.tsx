import React, { useState } from "react";
import GexSummaryPanel from "@/components/gex/GexSummaryPanel";

export default function GexAnalytics() {
  // Example state for symbol, dealer, normalize, source
  const [symbol, setSymbol] = useState("SPY");
  const [dealer, setDealer] = useState("mm_short");
  const [normalize, setNormalize] = useState("none");
  const [source, setSource] = useState("real");
  const [activeTab, setActiveTab] = useState("gex");
  const [expiries, setExpiries] = useState(["2025-11-21"]);

  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-screen">
      {/* Tabs */}
      <div className="flex gap-2 mb-3">
        <button
          className={`px-3 py-1 rounded ${activeTab === "gex" ? "bg-blue-600 text-white" : "bg-zinc-800"}`}
          onClick={() => setActiveTab("gex")}
        >
          GEX
        </button>
        <button
          className={`px-3 py-1 rounded ${activeTab === "summary" ? "bg-blue-600 text-white" : "bg-zinc-800"}`}
          onClick={() => setActiveTab("summary")}
        >
          Summary
        </button>
      </div>

      {/* Expiries input */}
      <label className="text-xs opacity-70">Expiries (CSV)</label>
      <input
        className="w-full bg-zinc-900 border border-zinc-800 rounded px-2 py-1"
        value={expiries.join(",")}
        onChange={e => {
          const v = e.target.value.split(",").map(s => s.trim()).filter(Boolean);
          setExpiries(v);
        }}
        placeholder="2025-11-21,2025-12-19"
      />

      {/* Mount summary panel only on summary tab */}
      {activeTab === "summary" && (
        <GexSummaryPanel
          symbol={symbol}
          expiries={expiries}
          dealer={dealer}
          normalize={normalize}
          source={source}
        />
      )}

      {/* GEX tab content placeholder */}
      {activeTab === "gex" && (
        <div className="text-slate-400">GEX tab content (existing logic remains here)</div>
      )}
    </div>
  );
}
