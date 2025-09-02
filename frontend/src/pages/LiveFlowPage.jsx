import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import TradeDrawer from "../components/flow/TradeDrawer";

async function fetchJSON(url, { timeoutMs = 3200, signal } = {}) {
  const t = new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), timeoutMs));
  const r = await Promise.race([fetch(url, { signal }), t]);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export default function LiveFlowPage() {
  const [params] = useSearchParams();
  const symbol = (params.get("symbol") || "").toUpperCase();

  const [rows, setRows] = useState([]);
  const [mode, setMode] = useState("UW_DEGRADED");   // default, ca să avem badge de la început
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeRow, setActiveRow] = useState(null);

  useEffect(() => {
    let alive = true;
    const ctrl = new AbortController();

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const q = new URLSearchParams();
        if (symbol) q.set("symbol", symbol);
        const j = await fetchJSON(`/api/flow/live?${q.toString()}`, { timeoutMs: 3200, signal: ctrl.signal });
        if (!alive) return;
        setRows(Array.isArray(j?.items) ? j.items : []);
        setMode(j?.mode || "UW_LIVE");
      } catch (e) {
        if (!alive) return;
        // NU blocăm UI: punem fallback minimal, dar păstrăm adevărul în badge (DEGRADED)
        setRows([]);
        setMode("UW_DEGRADED");
        setError(e);
      } finally {
        if (alive) setLoading(false); // important: nu lăsăm loading agățat
      }
    })();

    return () => { alive = false; ctrl.abort(); };
  }, [symbol]);

  return (
    <div data-testid="live-flow-page">
      <header className="flex items-center gap-2 mb-3">
        <span className={`text-xs rounded px-2 py-1 border ${
          mode === "UW_LIVE" ? "border-emerald-700 text-emerald-300" :
          mode === "DEMO" ? "border-amber-700 text-amber-300" :
          "border-slate-700 text-slate-300"
        }`}>
          {mode === "UW_LIVE" ? "UW LIVE" : mode === "DEMO" ? "DEMO DATA" : "UW DEGRADED"}
        </span>
        {symbol && <span className="text-xs text-slate-400">Symbol: {symbol}</span>}
        {loading && <span className="text-xs text-sky-300">loading…</span>}
        {error && <span className="text-xs text-amber-400">degraded: {String(error.message || error)}</span>}
      </header>

      {rows.length > 0 ? (
        <div className="overflow-auto rounded-xl border border-slate-800">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900/50 text-slate-300">
              <tr>
                <th className="px-3 py-2 text-left">Time</th>
                <th className="px-3 py-2">Side</th>
                <th className="px-3 py-2">Kind</th>
                <th className="px-3 py-2 text-right">Strike</th>
                <th className="px-3 py-2">Expiry</th>
                <th className="px-3 py-2 text-right">Qty</th>
                <th className="px-3 py-2 text-right">Price</th>
                <th className="px-3 py-2 text-right">Premium</th>
                <th className="px-3 py-2">Flags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {rows.map((r, i) => (
                <tr
                  key={i}
                  className="hover:bg-slate-900/50 cursor-pointer"
                  onClick={() => { setActiveRow(r); setDrawerOpen(true); }}
                >
                  <td className="px-3 py-2">{r.t}</td>
                  <td className="px-3 py-2 text-center">{r.side}</td>
                  <td className="px-3 py-2 text-center">{r.kind}</td>
                  <td className="px-3 py-2 text-right">{Number(r.strike).toFixed(2)}</td>
                  <td className="px-3 py-2">{r.expiry}</td>
                  <td className="px-3 py-2 text-right">{r.qty}</td>
                  <td className="px-3 py-2 text-right">{Number(r.price).toFixed(2)}</td>
                  <td className="px-3 py-2 text-right">${Number(r.premium).toLocaleString()}</td>
                  <td className="px-3 py-2">{(r.flags && r.flags.join(", ")) || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-slate-500 text-sm">
          {loading ? "Loading…" : "No live flow (check UW filters / min premium)."}
        </div>
      )}

      <TradeDrawer
        row={drawerOpen ? {
          symbol: (activeRow?.symbol || symbol || "").toUpperCase(),
          side: activeRow?.side || "B",
          kind: activeRow?.kind || "C",
          strike: Number(activeRow?.strike || 0),
          expiry: String(activeRow?.expiry || ""),
          qty: Number(activeRow?.qty || 100),
          price: Number(activeRow?.price || 0),
          premium: Number(activeRow?.premium || 0),
          flags: activeRow?.flags || [],
          iv: activeRow?.iv ?? null,
        } : null}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}