import QualityBadge from "../common/QualityBadge";
import { chipClassByStance, stanceLabel, tradeColorByStance } from "../../utils/stance";

export default function StrategyCard({
  strategy,          // { id,name,stance,tags,level,brief, score_ev, chance, liq, sqm }
  onOpenBuilder,     // () => void
  onOpenDetails,     // optional
}) {
  const stance = strategy.stance || "neutral";
  const tags = strategy.tags || [];
  const ev = strategy.score_ev ?? 0;
  const ch = strategy.chance ?? 0;
  const lq = strategy.liq ?? 0;
  const sqm = strategy.sqm; // dacă ai hook, îl treci din părinte

  return (
    <div className="fm-card">
      <div className="fm-card-head">
        <div className="flex items-center gap-2">
          <span className={chipClassByStance(stance)}>{stanceLabel(stance)}</span>
          <h3 className="text-slate-100 font-semibold">{strategy.name}</h3>
          {strategy.level && (
            <span className="text-[11px] text-slate-400">• {strategy.level}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <QualityBadge value={sqm} mode={strategy.sqmMode || "idle"} />
        </div>
      </div>

      <div className="fm-card-body space-y-3">
        {strategy.brief && <p className="text-slate-300 text-sm">{strategy.brief}</p>}

        {tags?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {tags.slice(0, 6).map((t) => (
              <span key={t} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {t}
              </span>
            ))}
          </div>
        )}

        <div className="grid grid-cols-3 gap-2">
          <Metric label="EV" value={ev} fmt="pct" />
          <Metric label="Chance" value={ch} fmt="pct" />
          <Metric label="Liquidity" value={lq} fmt="pct" />
        </div>

        <div className="flex items-center justify-end gap-2 pt-1">
          {onOpenDetails && (
            <button
              onClick={onOpenDetails}
              className="px-3 py-1.5 rounded bg-slate-800 text-slate-200 hover:bg-slate-700"
            >
              Details
            </button>
          )}
          <button
            onClick={onOpenBuilder}
            className={`px-3 py-1.5 rounded ${tradeColorByStance(stance)}`}
          >
            Open in Builder
          </button>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, fmt = "pct" }) {
  const v = Number(value) || 0;
  const txt = fmt === "pct" ? `${Math.round(v * 100)}%` : `${v}`;
  const c =
    v >= 0.75 ? "text-emerald-300" :
    v >= 0.5  ? "text-amber-300" :
                "text-slate-300";
  return (
    <div className="rounded-lg bg-slate-900/50 p-3 border border-slate-800">
      <div className="text-[11px] text-slate-400">{label}</div>
      <div className={`text-sm font-semibold ${c}`}>{txt}</div>
    </div>
  );
}