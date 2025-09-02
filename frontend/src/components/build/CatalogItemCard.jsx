import { memo, useState } from "react";
import HoverDiagram from "./HoverDiagram";
import { chipClassByStance, stanceLabel, tradeColorByStance } from "../../utils/stance";

/**
 * @param {object} props
 * @param {object} props.strategy - { id,name,stance,level,brief,tags,templateLegs }
 * @param {string} [props.previewSymbol] - simbolul curent (ex: din search)
 * @param {number} [props.previewSpot] - spot price pentru preview (din quotes)
 * @param {function} props.onOpenBuilder - handler "Open in Builder"
 * @param {function} [props.onOpenDetails] - (opțional) deschide detalii
 */
function CatalogItemCardBase({
  strategy,
  previewSymbol = "TSLA",
  previewSpot = 250,
  onOpenBuilder,
  onOpenDetails,
}) {
  const [hover, setHover] = useState(false);
  const stance = strategy.stance || "neutral";
  const tags = strategy.tags || [];

  return (
    <div
      className="fm-card"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
      tabIndex={0}
    >
      <div className="fm-card-head">
        <div className="flex items-center gap-2">
          <span className={chipClassByStance(stance)}>{stanceLabel(stance)}</span>
          <h3 className="text-slate-100 font-semibold">{strategy.name}</h3>
          {strategy.level && (
            <span className="text-[11px] text-slate-400">• {strategy.level}</span>
          )}
        </div>
        {/* poți adăuga un badge mic aici dacă vrei (ex: "Defined risk") */}
      </div>

      <div className="fm-card-body flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0 space-y-2">
          {strategy.brief && (
            <p className="text-slate-300 text-sm">{strategy.brief}</p>
          )}

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {tags.slice(0, 6).map((t) => (
                <span
                  key={t}
                  className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700"
                >
                  {t}
                </span>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2 pt-1">
            {onOpenDetails && (
              <button
                onClick={() => onOpenDetails(strategy)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-200 hover:bg-slate-700"
              >
                Details
              </button>
            )}
            <button
              onClick={() => onOpenBuilder(strategy)}
              className={`px-3 py-1.5 rounded ${tradeColorByStance(stance)}`}
            >
              Open in Builder
            </button>
          </div>
        </div>

        {/* Preview doar la hover/focus */}
        {hover ? (
          <HoverDiagram
            symbol={previewSymbol}
            spot={previewSpot}
            legs={strategy.templateLegs}
            width={220}
            height={88}
          />
        ) : (
          <div className="h-[88px] w-[220px] rounded-lg bg-slate-900/60" />
        )}
      </div>
    </div>
  );
}

const CatalogItemCard = memo(CatalogItemCardBase);
export default CatalogItemCard;