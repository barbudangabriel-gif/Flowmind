function fmt4(val) {
  if (val == null) return '—';
  return val.toFixed(4);
}

function fmt6(val) {
  if (val == null) return '—';
  return val.toFixed(6);
}

export default function GreeksStrip({ greeks }) {
  if (!greeks) return null;

  const greekItems = [
    { label: 'Δ', value: fmt4(greeks.delta), tooltip: 'Delta - Price sensitivity' },
    { label: 'Θ', value: fmt4(greeks.theta), tooltip: 'Theta - Time decay' },
    { label: 'Γ', value: fmt6(greeks.gamma), tooltip: 'Gamma - Delta sensitivity' },
    { label: 'Vega', value: fmt4(greeks.vega), tooltip: 'Vega - IV sensitivity' },
    { label: 'ρ', value: fmt4(greeks.rho), tooltip: 'Rho - Interest rate sensitivity' }
  ];

  return (
    <div className="mt-2 flex gap-6 text-xs text-slate-400 border-t border-slate-800 pt-2">
      <span className="text-slate-500 uppercase tracking-wide">Greeks:</span>
      {greekItems.map(({ label, value, tooltip }) => (
        <span 
          key={label} 
          className="hover:text-slate-300 transition-colors cursor-help"
          title={tooltip}
        >
          <span className="font-medium">{label}</span> {value}
        </span>
      ))}
    </div>
  );
}