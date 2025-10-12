import React, { useMemo, useState } from "react";
import { fetchGexSummary, GexSummaryResponse } from "../../lib/api/gexClient";


type Props = {
  symbol: string;
  expiries: string[];             // ex: ["2025-11-21","2025-12-19"]
  dealer?: string;                // "mm_short" | "mm_long"
  normalize?: string;             // "none" | "spot" | "iv"
  source?: "real" | "mock";
};


export default function GexSummaryPanel({
  symbol,
  expiries,
  dealer = "mm_short",
  normalize = "none",
  source = "real",
}: Props) {
  const [data, setData] = useState<GexSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [err, setErr] = useState<string | null>(null);

  const onFetch = async (): Promise<void> => {
    if (!symbol || expiries.length === 0) return;
    setLoading(true); setErr(null);
    try {
      const res = await fetchGexSummary({ symbol, expiries, dealer, normalize, source });
      setData(res);
    } catch (e: any) {
      setErr(e?.message || "Summary fetch failed");
    } finally {
      setLoading(false);
    }
  };

  const badgeSource = useMemo(() => {
    if (!data?.items?.length) return "n/a";
    const uniq = new Set(data.items.map((i: any) => i.source || "n/a"));
    return uniq.size === 1 ? [...uniq][0] : "mixed";
  }, [data]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <button
          onClick={onFetch}
          disabled={loading || expiries.length === 0}
          className="px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-50"
        >
          {loading ? "Fetching…" : "Fetch Summary"}
        </button>

        <span className="text-xs px-2 py-1 rounded bg-zinc-800">
          source: {badgeSource}
        </span>
        {data?.meta?.p95_ms !== undefined && (
          <span className="text-xs px-2 py-1 rounded bg-zinc-800">
            p95 ~ {data.meta.p95_ms}ms
          </span>
        )}
        {data?.meta && (
          <span className="text-xs px-2 py-1 rounded bg-zinc-800">
            cache: HIT x{data.meta.cacheHits ?? 0} · MISS x{data.meta.misses ?? 0}
          </span>
        )}
      </div>

      {err && <div className="text-red-400 text-sm">{err}</div>}

      {data?.items?.length ? (
        <div className="overflow-auto border border-zinc-800 rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left px-3 py-2">Expiry</th>
                <th className="text-right px-3 py-2">Net GEX</th>
                <th className="text-right px-3 py-2">Call Wall</th>
                <th className="text-right px-3 py-2">Put Wall</th>
                <th className="text-left px-3 py-2">Source</th>
                <th className="text-left px-3 py-2">TS</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((it: any) => (
                <tr key={it.expiry} className="border-t border-zinc-800">
                  <td className="px-3 py-2">{it.expiry}</td>
                  <td className="px-3 py-2 text-right">
                    {Math.round(it.net_gex).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-right">{it.walls?.call ?? "–"}</td>
                  <td className="px-3 py-2 text-right">{it.walls?.put ?? "–"}</td>
                  <td className="px-3 py-2">{it.source ?? "n/a"}</td>
                  <td className="px-3 py-2">{it.ts ?? "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-sm opacity-70">
          Selectează 1+ expirări și apasă <b>Fetch Summary</b>.
        </div>
      )}
    </div>
  );
}
