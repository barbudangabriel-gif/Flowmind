import React from "react";

function encodeBuilderPayload(row) {
  const stance =
    row.side === "B"
      ? (row.kind === "C" ? "bullish" : "bearish")
      : (row.kind === "C" ? "bearish" : "bullish");

  const payload = {
    symbol: row.symbol,
    expiry: row.expiry,
    dte: null,
    legs: [{
      side: row.side === "B" ? "BUY" : "SELL",
      kind: row.kind === "C" ? "CALL" : "PUT",
      strike: row.strike,
      qty: 1,
    }],
    qty: Math.max(1, Math.round((row.qty || 100) / 100)),
    params: { iv_hint: row.iv ?? null, fromFlow: true },
    meta: { stance, from: "LiveFlow" },
  };

  const s = btoa(unescape(encodeURIComponent(JSON.stringify(payload))))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/,"");

  return `/build/custom?s=${s}`;
}

export default function TradeDrawer({ row, open, onClose }) {
  if (!open || !row) return null;
  const builderLink = encodeBuilderPayload(row);

  const stanceColor =
    (row.side === "B" && row.kind === "C") || (row.side === "S" && row.kind === "P")
      ? "bg-emerald-600"
      : (row.side === "B" && row.kind === "P") || (row.side === "S" && row.kind === "C")
      ? "bg-rose-600"
      : "bg-slate-600";

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/40" onClick={onClose}/>
      <aside className="absolute right-0 top-0 h-full w-[420px] bg-slate-950 border-l border-slate-800 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="text-slate-200 font-semibold">{row.symbol} — Trade</div>
          <button className="text-slate-400 hover:text-slate-200" onClick={onClose}>✕</button>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div><span className="text-slate-400">Side</span><div className="font-medium">{row.side}</div></div>
          <div><span className="text-slate-400">Kind</span><div className="font-medium">{row.kind}</div></div>
          <div><span className="text-slate-400">Strike</span><div className="font-medium">{Number(row.strike).toFixed(2)}</div></div>
          <div><span className="text-slate-400">Expiry</span><div className="font-medium">{row.expiry}</div></div>
          <div><span className="text-slate-400">Qty</span><div className="font-medium">{row.qty}</div></div>
          <div><span className="text-slate-400">Price</span><div className="font-medium">{Number(row.price).toFixed(2)}</div></div>
          <div><span className="text-slate-400">Premium</span><div className="font-medium">${Number(row.premium).toLocaleString()}</div></div>
          <div><span className="text-slate-400">Flags</span><div className="font-medium">{(row.flags && row.flags.join(", ")) || "-"}</div></div>
        </div>

        <div className="mt-4 space-y-2">
          <a
            href={builderLink}
            className="w-full inline-flex items-center justify-center rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2"
          >
            Open in Builder
          </a>

          <button
            className={`w-full inline-flex items-center justify-center rounded-lg ${stanceColor} text-white px-3 py-2`}
            title="Trade via TS (stub)"
          >
            Trade (TS)
          </button>

          <button
            onClick={() => {
              const name = `${row.symbol}_${row.kind}${row.strike}_${row.expiry}.json`.replace(/[^\w\.-]+/g,'_');
              const data = new Blob([JSON.stringify(row, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(data);
              const a = document.createElement('a'); a.href = url; a.download = name; a.click();
              setTimeout(() => URL.revokeObjectURL(url), 500);
            }}
            className="w-full inline-flex items-center justify-center rounded-lg border border-slate-700 text-slate-200 px-3 py-2 hover:bg-slate-900"
          >
            Save JSON
          </button>
        </div>
      </aside>
    </div>
  );
}