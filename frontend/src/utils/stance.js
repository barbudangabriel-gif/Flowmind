export const stanceLabel = (s) => ({
 bullish: "Bullish",
 bearish: "Bearish",
 neutral: "Neutral", 
 directional: "Directional",
}[s] || "Neutral");

export const chipClassByStance = (s) => ({
 bullish: "fm-chip fm-chip-bullish",
 bearish: "fm-chip fm-chip-bearish",
 neutral: "fm-chip fm-chip-neutral",
 directional: "fm-chip fm-chip-directional",
}[s] || "fm-chip fm-chip-neutral");

export const tradeColorByStance = (s) => ({
 bullish: "bg-emerald-600 hover:bg-emerald-700 text-[rgb(252, 251, 255)]",
 bearish: "bg-rose-600 hover:bg-rose-700 text-[rgb(252, 251, 255)]",
 neutral: "bg-slate-600 hover:bg-slate-700 text-[rgb(252, 251, 255)]",
 directional: "bg-fuchsia-600 hover:bg-fuchsia-700 text-[rgb(252, 251, 255)]",
}[s] || "bg-slate-600 hover:bg-slate-700 text-[rgb(252, 251, 255)]");

export function stanceFromDelta(deltaSum = 0) {
 if (deltaSum > 0.10) return "bullish";
 if (deltaSum < -0.10) return "bearish"; 
 return "neutral";
}