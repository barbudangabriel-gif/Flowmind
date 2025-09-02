import { useEffect } from "react";
import HoverDiagram from "./HoverDiagram";
import { chipClassByStance, stanceLabel, tradeColorByStance } from "../../utils/stance";

export default function StrategyDetailsModal({
  open,
  strategy,            // { id,name,stance,level,tags,brief,bullets,templateLegs }
  previewSymbol = "TSLA",
  previewSpot = 250,
  onClose,
  onOpenBuilder,       // (strategy) => void
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose?.(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !strategy) return null;
  const tags = strategy.tags || [];
  const bullets = strategy.bullets || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" onClick={onClose}>
      <div className="w-full max-w-3xl rounded-2xl border border-slate-800 bg-slate-950"
           onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        {/* header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={chipClassByStance(strategy.stance)}>{stanceLabel(strategy.stance)}</span>
            <h2 className="text-slate-100 font-semibold">{strategy.name}</h2>
            {strategy.level && <span className="text-[11px] text-slate-400">• {strategy.level}</span>}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">Close</button>
        </div>

        {/* body */}
        <div className="p-4 grid md:grid-cols-2 gap-4">
          <div className="space-y-3">
            {strategy.brief && <p className="text-slate-300 text-sm">{strategy.brief}</p>}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {tags.slice(0, 8).map((t) => (
                  <span key={t} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {t}
                  </span>
                ))}
              </div>
            )}
            {bullets.length > 0 && (
              <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
                {bullets.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
            )}
          </div>

          {/* preview payoff mai mare */}
          <div className="flex flex-col items-center gap-3">
            <HoverDiagram
              symbol={previewSymbol}
              spot={previewSpot}
              legs={strategy.templateLegs}
              width={360}
              height={160}
            />
            <div className="text-[11px] text-slate-500">
              Preview payoff · P&L la expirare (linia albă = 0)
            </div>
          </div>
        </div>

        {/* footer */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-end gap-2">
          <button onClick={onClose} className="px-3 py-1.5 rounded bg-slate-800 text-slate-200 hover:bg-slate-700">
            Close
          </button>
          <button
            onClick={() => onOpenBuilder?.(strategy)}
            className={`px-3 py-1.5 rounded ${tradeColorByStance(strategy.stance)}`}
          >
            Open in Builder
          </button>
        </div>
      </div>
    </div>
  );
}