export function drawdown(series: { equity: number }[]) {
 let peak = -Infinity, curDD = 0, maxDD = 0;
 for (const p of series) {
 peak = Math.max(peak, p.equity);
 const dd = peak > 0 ? (p.equity - peak) / peak : 0;
 curDD = dd;
 maxDD = Math.min(maxDD, dd);
 }
 return { current: curDD, max: maxDD }; // valori negative
}

export function utilization(equity: number, start: number) {
 if (!start || start === 0) return 0;
 return (equity - start) / start; // 0.20 = +20% față de buget
}

export const fmtPct = (x: number) => (x * 100).toFixed(1) + '%';
export const last = <T,>(arr: T[]) => arr.length ? arr[arr.length - 1] : undefined;