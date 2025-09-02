export default function BuilderTable({ 
  pricing, 
  builder, 
  variant = "table" 
}) {
  if (!pricing?.chart?.series?.[0]?.xy) {
    return (
      <div className="bg-slate-900/30 rounded-lg border border-slate-800 p-8 text-center">
        <div className="text-slate-400">No data available for table view</div>
      </div>
    );
  }
  
  const data = pricing.chart.series[0].xy;
  const formatValue = (price, pnl) => {
    switch (variant) {
      case 'pl$':
        return `$${pnl.toFixed(2)}`;
      case 'pl%':
        const pctReturn = pricing.net_debit ? (pnl / Math.abs(pricing.net_debit)) * 100 : 0;
        return `${pctReturn.toFixed(1)}%`;
      case 'contract':
        return `$${(pnl + (pricing.net_debit || 0)).toFixed(2)}`;
      case '%risk':
        const maxRisk = Math.abs(pricing.max_loss || 1);
        const riskPct = (Math.abs(pnl) / maxRisk) * 100;
        return `${riskPct.toFixed(1)}%`;
      default:
        return `$${pnl.toFixed(2)}`;
    }
  };

  const getHeaderLabel = () => {
    switch (variant) {
      case 'pl$': return 'Profit/Loss ($)';
      case 'pl%': return 'Return (%)';
      case 'contract': return 'Contract Value ($)';
      case '%risk': return '% of Max Risk';
      default: return 'P&L at Expiration';
    }
  };

  // Sample first 10 and last 10 points for table view
  const sampleData = [
    ...data.slice(0, 10),
    ...(data.length > 20 ? [null] : []), // separator
    ...data.slice(-10)
  ];

  return (
    <div className="bg-slate-900/30 rounded-lg border border-slate-800 overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 bg-slate-900/50">
        <h3 className="text-sm font-medium text-slate-200">{getHeaderLabel()}</h3>
        <div className="text-xs text-slate-400 mt-1">
          Showing {sampleData.filter(Boolean).length} key price levels (at expiration)
        </div>
      </div>
      
      <div className="max-h-80 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-900/70 sticky top-0">
            <tr>
              <th className="text-left px-4 py-2 text-xs text-slate-400 uppercase tracking-wide">
                Underlying Price
              </th>
              <th className="text-right px-4 py-2 text-xs text-slate-400 uppercase tracking-wide">
                {getHeaderLabel()}
              </th>
            </tr>
          </thead>
          <tbody>
            {sampleData.map((point, i) => {
              if (!point) {
                return (
                  <tr key={`sep-${i}`}>
                    <td colSpan={2} className="px-4 py-2 text-center text-xs text-slate-500">
                      ⋯ ({data.length - 20} intermediate points) ⋯
                    </td>
                  </tr>
                );
              }
              
              const [price, pnl] = point;
              const isProfit = pnl > 0;
              const isBreakeven = Math.abs(pnl) < 0.01;
              
              return (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="px-4 py-2 text-slate-300">
                    ${price.toFixed(2)}
                  </td>
                  <td className={`px-4 py-2 text-right font-mono ${
                    isBreakeven ? 'text-slate-300' :
                    isProfit ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {formatValue(price, pnl)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}