export default function QualityBadge({ value, mode = "idle" }) {
 const v = Number.isFinite(value) ? value : null;
 const color =
 v == null ? "border-slate-700 text-slate-300"
 : v >= 75 ? "border-emerald-700 text-emerald-300"
 : v >= 50 ? "border-amber-700 text-amber-300"
 : "border-rose-700 text-rose-300";

 const hint =
 mode === "degraded" ? "degraded" :
 mode === "loading" ? "loading…" : "";

 return (
 <span
 className={`text-lg rounded px-2 py-1 border ${color}`}
 title={hint ? `SQM ${v ?? "n/a"} (${hint})` : `SQM ${v ?? "n/a"}`}
 data-testid="quality-badge"
 >
 SQM: {v ?? "—"}{hint ? ` (${hint})` : ""}
 </span>
 );
}