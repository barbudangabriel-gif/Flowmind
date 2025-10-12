import React, { useMemo } from "react";
import { useFIS } from "../hooks/useFIS";
import FISBadge from "./FISBadge";
import TrendBadge from "./TrendBadge";
import Tooltip from "./Tooltip";

export default function TickerRow({ symbol, name, trendWindow = 7 }) {
  const { data: fis, loading, history } = useFIS(symbol);

  // % schimbare pe ultimele trendWindow puncte de istoric (default 7)
  const arr = useMemo(() => history.slice(-trendWindow), [history, trendWindow]);
  const changePct = useMemo(() => {
    if (!arr.length || arr.length < 2) return 0;
    const first = arr[0].score || 0;
    const last  = arr[arr.length - 1].score || 0;
    if (first === 0) return 0;
    return ((last - first) / first) * 100;
  }, [arr]);

  return (
    <div style={{
      display:"grid",
      gridTemplateColumns:"110px 1fr 220px",
      gap:12, padding:"8px 12px",
      borderBottom:"1px solid #eee", alignItems:"center"
    }}>
      <div style={{fontWeight:700}}>{symbol}</div>
      <div style={{opacity:.75}}>{name}</div>
      <div style={{justifySelf:"end", display:"flex", gap:8, alignItems:"center"}}>
        {loading ? <span style={{opacity:.6}}>FIS…</span> :
          <>
            <FISBadge score={fis?.score} factors={fis?.factors} />
            {arr.length < 2 ? (
              <span style={{fontSize:12,opacity:.7}}>Insufficient data</span>
            ) : (
              <Tooltip content={<span>Trend {trendWindow}d: {changePct.toFixed(1)}%</span>}>
                <TrendBadge changePct={changePct} title={`Trend ${trendWindow}d: ${changePct.toFixed(1)}%`} />
              </Tooltip>
            )}
          </>
        }
      </div>
    </div>
  );
}
