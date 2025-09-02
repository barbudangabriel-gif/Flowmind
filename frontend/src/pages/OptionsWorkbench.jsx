import React, { useState, lazy, Suspense } from "react";
import { useNavigate } from "react-router-dom";

const BuildHoverMegaMenu = lazy(() => import("../components/nav/BuildHoverMegaMenu"));

function FlowScroller() {
  const navigate = useNavigate();
  const items = [
    { key:"summary",    label:"Summary",    desc:"Top net premium by symbol", to:"/flow/summary" },
    { key:"live",       label:"Live",       desc:"Tape tranzacții mari",     to:"/flow/live?symbol=TSLA" },
    { key:"historical", label:"Historical", desc:"Flux istoric",             to:"/flow/historical" },
    { key:"news",       label:"News",       desc:"Știri & sentiment",        to:"/flow/news" },
    { key:"congress",   label:"Congress",   desc:"Tranzacții congres",       to:"/flow/congress" },
    { key:"insiders",   label:"Insiders",   desc:"Tranzacții insiders",      to:"/flow/insiders" },
  ];
  return (
    <div className="mt-4 overflow-x-auto">
      <div className="flex gap-3 min-w-max">
        {items.map(it => (
          <button key={it.key}
            onClick={()=>navigate(it.to)}
            className="w-56 shrink-0 text-left p-4 rounded-2xl bg-slate-900/70 border border-slate-800 hover:bg-slate-900">
            <div className="text-sm font-semibold text-slate-100">{it.label}</div>
            <div className="text-xs text-slate-400 mt-1">{it.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function OptionsWorkbench() {
  const [showBuild, setShowBuild] = useState(false);
  const [hovered, setHovered] = useState(null);
  const symbol = "TSLA";

  return (
    <div className="px-4 py-4">
      <div className="flex items-center gap-2">
        <div
          className="relative"
          onMouseEnter={()=>setShowBuild(true)}
          onMouseLeave={()=>setShowBuild(false)}
        >
          <button className="px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors">Build ▾</button>
          {showBuild && (
            <Suspense fallback={<div className="absolute left-0 top-full mt-1 px-3 py-2 text-xs bg-slate-900/90 border border-slate-800 rounded">Loading…</div>}>
              <BuildHoverMegaMenu
                symbol={symbol}
                onClose={()=>setShowBuild(false)}
                onItemHover={setHovered}  // păstrăm hook-ul pt. preview ulterior
              />
            </Suspense>
          )}
        </div>

        <a className="px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors" href="/optimize">Optimize</a>
        <a className="px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors" href="/flow/summary">Flow</a>
      </div>

      {/* Preview tray îl lăsăm oprit acum (lightweight). Îl activăm când vrei. */}
      {/* <div className="mt-3 rounded-2xl border border-slate-800 bg-slate-900/70 p-3 min-h-[120px]">…</div> */}

      <FlowScroller />
    </div>
  );
}