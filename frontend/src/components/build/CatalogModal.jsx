import React, { useMemo, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { STRATEGIES } from "../../data/strategies";
import CatalogItemCard from "./CatalogItemCard";
import StrategyDetailsModal from "./StrategyDetailsModal";

const chip = (t)=>(
  <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-800 text-zinc-200">{t}</span>
);

function Preview({type}){
  // mini SVG schematic (foarte light)
  const path = {
    up: "M2,28 L18,28 L28,6", down: "M2,6 L12,20 L28,28",
    range:"M2,20 L12,20 L18,8 L28,8", skew:"M2,24 L18,18 L28,10"
  }[type];
  return (
    <svg viewBox="0 0 30 30" className="w-16 h-10">
      <path d={path} stroke="currentColor" fill="none" strokeWidth="2" className="text-emerald-400"/>
    </svg>
  );
}

// Removem StrategyCard function din această fișă - nu mai e necesară
// Folosim CatalogItemCard acum

export default function CatalogModal({ open, onOpenChange, symbol }) {
  const [stance, setStance] = useState("all");
  const [level, setLevel] = useState("all");
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState(null);

  // For preview diagrams - you can get these from props or use defaults
  const previewSymbol = symbol || 'TSLA';
  const previewSpot = 250; // Default spot price for preview

  const allStrategies = useMemo(() => {
    return Object.values(STRATEGIES).flat();
  }, []);

  const filteredStrategies = useMemo(() => {
    return allStrategies.filter(s => {
      const stanceOk = stance === "all" || s.stance === stance;
      const levelOk = level === "all" || s.level === level;
      const text = (s.name + " " + (s.tags || []).join(" ") + " " + s.bullets.join(" ")).toLowerCase();
      const qok = !q || text.includes(q.toLowerCase());
      return stanceOk && levelOk && qok;
    });
  }, [stance, level, q, allStrategies]);

  const encodeStrategyParams = (symbol, params) => {
    // Simple base64 encoding for strategy parameters
    const payload = {
      symbol,
      ...params
    };
    try {
      const jsonStr = JSON.stringify(payload);
      return btoa(jsonStr);
    } catch {
      return "";
    }
  };

  const handleStrategySelect = (strategy) => {
    const params = strategy.buildParams(symbol);
    const url = "/build/" + params.strategyId + "?s=" + encodeStrategyParams(symbol, params);
    window.location.assign(url);
    onOpenChange(false);
  };

  const strategiesByLevel = useMemo(() => {
    const grouped = {};
    Object.entries(STRATEGIES).forEach(([levelName, strategies]) => {
      const filtered = strategies.filter(s => filteredStrategies.includes(s));
      if (filtered.length > 0) {
        grouped[levelName] = filtered;
      }
    });
    return grouped;
  }, [filteredStrategies]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle className="text-xl font-bold">Strategy Catalog • {symbol}</DialogTitle>
          <div className="text-sm text-zinc-400">
            {filteredStrategies.length} strategies available
          </div>
        </DialogHeader>

        {/* Filters */}
        <div className="flex-shrink-0 space-y-3 border-b border-zinc-800 pb-4">
          <input
            placeholder="Search strategies, tags, keywords…"
            value={q} 
            onChange={e => setQ(e.target.value)}
            className="w-full rounded-xl bg-zinc-900/50 border border-zinc-700 px-4 py-2 text-white placeholder-zinc-400 focus:border-zinc-600 focus:outline-none"
          />
          
          <div className="flex flex-wrap gap-2">
            <div className="flex gap-1">
              <span className="text-xs text-zinc-400 py-2">Stance:</span>
              {["all","bullish","bearish","neutral","directional"].map(k => (
                <button key={k}
                  onClick={() => setStance(k)}
                  className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                    stance === k 
                      ? "bg-indigo-500 text-white" 
                      : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                  }`}>
                  {k}
                </button>
              ))}
            </div>
            
            <div className="flex gap-1">
              <span className="text-xs text-zinc-400 py-2">Level:</span>
              {["all","Novice","Intermediate","Advanced","Expert"].map(k => (
                <button key={k}
                  onClick={() => setLevel(k)}
                  className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                    level === k 
                      ? "bg-indigo-500 text-white" 
                      : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                  }`}>
                  {k}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Strategy Grid */}
        <div className="flex-1 overflow-y-auto">
          <div className="space-y-6 py-4">
            {Object.entries(strategiesByLevel).map(([levelName, strategies]) => (
              <div key={levelName}>
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="text-lg font-semibold text-white">{levelName}</h3>
                  <span className="text-xs text-zinc-400">({strategies.length} strategies)</span>
                </div>
                
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {strategies.map(strategy => (
                    <CatalogItemCard
                      key={strategy.id} 
                      strategy={strategy} 
                      previewSymbol={previewSymbol}
                      previewSpot={previewSpot}
                      onOpenBuilder={handleStrategySelect}
                      onOpenDetails={(st) => setSelected(st)}
                    />
                  ))}
                </div>
              </div>
            ))}
            
            {Object.keys(strategiesByLevel).length === 0 && (
              <div className="text-center py-12">
                <div className="text-zinc-400 mb-2">No strategies found</div>
                <div className="text-xs text-zinc-500">Try adjusting your filters or search terms</div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>

      {/* Strategy Details Modal */}
      <StrategyDetailsModal
        open={!!selected}
        strategy={selected}
        onClose={() => setSelected(null)}
        onOpenBuilder={(st) => { 
          setSelected(null); 
          handleStrategySelect(st); 
        }}
        previewSymbol={previewSymbol}
        previewSpot={previewSpot}
      />
    </Dialog>
  );
}