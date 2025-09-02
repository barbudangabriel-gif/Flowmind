// ==============================================
// Builder — Strike Rail PRO (BSR1)
// • Strike rail cu OI/Volume/IV tooltips + snap-to-chain
// • Multi-leg highlight (buy/sell, call/put) și markers pentru strikes alese
// • Rulare orizontală smooth, zoom pe rotiță (opțional), taste A/D
// • Fără dependențe; Tailwind only
// ==============================================
import React from 'react'

export function StrikeRailPro({
  chain = [],               // datele de lanț (sorted asc) - default to empty array
  legs = [],                // legs curente ale strategiei - default to empty array  
  onPick = () => {},        // când utilizatorul dă click pe un strike -> returnează strike
  snap = true,              // încadrăm strikes la cele din chain
  show = { oi: true, vol: true, iv: true },
  loading = false,          // SR-1/3: loading state
  error = undefined         // SR-1/3: error message
}) {
  // SR-1/3: Early returns for loading/error states
  if (loading) {
    return (
      <div className="w-full h-[120px] flex items-center justify-center text-slate-500 bg-[#0b1c33] border border-[#12233f] rounded-xl">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
          Loading chain data...
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="w-full h-[120px] flex items-center justify-center text-rose-400 bg-[#0b1c33] border border-[#12233f] rounded-xl">
        <div className="text-center">
          <div className="text-rose-500 mb-1">⚠️ Chain Error</div>
          <div className="text-sm opacity-70">{error}</div>
        </div>
      </div>
    );
  }
  
  if (!Array.isArray(chain) || !chain.length) {
    return (
      <div className="w-full h-[120px] flex items-center justify-center text-slate-400 bg-[#0b1c33] border border-[#12233f] rounded-xl">
        <div className="text-center">
          <div className="text-slate-500 mb-1">📊 No Chain Data</div>
          <div className="text-sm opacity-70">No options chain available</div>
        </div>
      </div>
    );
  }

  const ref = React.useRef(null)
  const [hover, setHover] = React.useState(null)

  const maxOI = Math.max(1, ...chain.map(c=> c.oi||0))
  const maxVol = Math.max(1, ...chain.map(c=> c.vol||0))
  const minIv = Math.min(...chain.map(c=> c.iv ?? Infinity))
  const maxIv = Math.max(...chain.map(c=> c.iv ?? 0))

  // taste A/D pentru scroll
  React.useEffect(()=>{
    const onKey=(e)=>{
      if(!ref.current) return
      if(e.key==='a' || e.key==='A') ref.current.scrollBy({left:-120,behavior:'smooth'})
      if(e.key==='d' || e.key==='D') ref.current.scrollBy({left:120,behavior:'smooth'})
    }
    window.addEventListener('keydown', onKey)
    return ()=> window.removeEventListener('keydown', onKey)
  },[])

  // util: formatare + SR-1/3 enhancements
  const fmt = {
    usd:(x)=> x==null?'-': '$'+x.toFixed(2),
    pct:(x)=> x==null?'-': (x*100).toFixed(1)+'%',
    spread:(bid, ask, mid) => {
      if (!bid || !ask || !mid) return { spread: '-', color: 'text-slate-400', pct: 0 };
      const spread = ask - bid;
      const pct = spread / mid;
      const color = pct <= 0.05 ? 'text-emerald-400' : pct <= 0.10 ? 'text-yellow-400' : 'text-red-400';
      return { spread: `±$${spread.toFixed(2)}`, color, pct };
    }
  }

  // Calculate total OI for percentage
  const totalOI = chain.reduce((sum, c) => sum + (c.oi || 0), 0);

  // highlight pentru strike-urile din legs
  const legMap = new Map()
  if (Array.isArray(legs)) {
    for(const l of legs){
      const k = snap ? nearestStrike(chain, l.strike) : l.strike
      const list = legMap.get(k) || []
      list.push(l); legMap.set(k, list)
    }
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2 text-xs text-slate-300">
        <div className="flex gap-3">
          <Toggle label="OI"   active={!!show.oi }  color="emerald" />
          <Toggle label="Vol"  active={!!show.vol} color="sky" />
          <Toggle label="IV"   active={!!show.iv } color="indigo" />
        </div>
        <div className="opacity-70">Scroll: ⟵⟶ · Taste: A/D · Snap-to-chain: {snap? 'On':'Off'}</div>
      </div>

      <div ref={ref} className="overflow-x-auto border border-[#12233f] rounded-xl bg-[#0b1c33] p-2">
        <div className="grid gap-2" style={{gridTemplateColumns:`repeat(${chain.length}, minmax(64px, 1fr))`}}>
          {chain.map((c,idx)=>{
            const legsHere = legMap.get(c.strike)
            const active = !!legsHere
            const mid = c.mid ?? (c.bid != null && c.ask != null ? (c.bid+c.ask)/2 : undefined)
            const oiH = (c.oi||0)/maxOI
            const volH = (c.vol||0)/maxVol
            const ivT = normalize(c.iv, minIv, maxIv)

            return (
              <button key={idx}
                onMouseEnter={()=> setHover(c)}
                onMouseLeave={()=> setHover(h=> h?.strike===c.strike? null:h)}
                onClick={()=> onPick(c.strike)}
                className={"relative rounded-lg px-2 py-2 text-xs text-slate-200 bg-white/5 hover:bg-white/10 transition border "+(active?"border-emerald-400 shadow-[0_0_0_2px_rgba(16,185,129,0.2)]":"border-transparent")}
              >
                {/* header strike */}
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold">{c.strike.toFixed(0)}</div>
                  <div className="text-[10px] opacity-70">{fmt.usd(mid)}</div>
                </div>

                {/* OI/Vol bars */}
                <div className="space-y-1">
                  <Bar label="OI"  frac={oiH}  color="#10b981" />
                  <Bar label="Vol" frac={volH} color="#38bdf8" />
                </div>

                {/* IV dot */}
                <div className="mt-2 h-6 relative">
                  <span className="text-[10px] opacity-70 absolute left-0">IV</span>
                  <div className="absolute inset-x-0 top-1/2 h-px bg-white/10"/>
                  <div className="absolute top-1/2 -mt-1 h-2 w-2 rounded-full" style={{left:`${ivT*100}%`, background:'#6366f1'}}/>
                </div>

                {/* leg badges */}
                {active && (
                  <div className="absolute -top-1 -right-1 flex gap-1">
                    {legsHere.map((l,i)=> (
                      <span key={i} className={"px-1.5 py-0.5 rounded text-[10px] font-semibold "+badgeCls(l)}>{l.side==='BUY'?'B':'S'}{l.type==='CALL'?'C':'P'}</span>
                    ))}
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tooltip flotant - SR-1/3 Enhanced */}
      {hover && (
        <div className="mt-2 text-xs rounded-lg border border-[#12233f] bg-[#0b1c33] p-3 shadow-xl">
          <div className="flex gap-6">
            <div>
              <div className="text-slate-400">Strike</div>
              <div className="font-semibold">{hover.strike.toFixed(0)}</div>
            </div>
            <div>
              <div className="text-slate-400">Bid / Ask</div>
              <div>{fmt.usd(hover.bid)} <span className="opacity-60">/</span> {fmt.usd(hover.ask)}</div>
              <div className="text-slate-400 mt-0.5">Mid</div>
              <div className="flex items-center gap-2">
                <span>{fmt.usd(hover.mid)}</span>
                <span className={fmt.spread(hover.bid, hover.ask, hover.mid).color}>
                  {fmt.spread(hover.bid, hover.ask, hover.mid).spread}
                </span>
              </div>
            </div>
            <div>
              <div className="text-slate-400">IV</div>
              <div>{fmt.pct(hover.iv)}</div>
            </div>
            <div>
              <div className="text-slate-400">OI / Vol</div>
              <div>{(hover.oi||0).toLocaleString()} / {(hover.vol||0).toLocaleString()}</div>
              {totalOI > 0 && (
                <div className="text-slate-400 text-[10px] mt-0.5">
                  OI: {((hover.oi||0) / totalOI * 100).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Toggle({label, active, color}){
  const map = { emerald:'text-emerald-400', sky:'text-sky-400', indigo:'text-indigo-400' }
  return <span className={'px-2 py-0.5 rounded-lg bg-white/5 '+map[color]}>{label}</span>
}

function Bar({label, frac, color}){
  return (
    <div className="h-3 relative">
      <span className="absolute left-0 top-0 text-[10px] opacity-70">{label}</span>
      <div className="absolute left-6 right-0 top-1/2 -translate-y-1/2 h-1 bg-white/10 rounded"/>
      <div className="absolute left-6 top-1/2 -translate-y-1/2 h-1 rounded" style={{width:`${Math.max(2, frac*100)}%`, background:color}}/>
    </div>
  )
}

function badgeCls(l){
  const base = 'shadow text-white'
  if(l.side==='BUY' && l.type==='CALL') return base+' bg-emerald-600'
  if(l.side==='SELL'&& l.type==='CALL') return base+' bg-red-600'
  if(l.side==='BUY' && l.type==='PUT' ) return base+' bg-sky-600'
  if(l.side==='SELL'&& l.type==='PUT' ) return base+' bg-yellow-600 text-black'
  return base+' bg-slate-600'
}

function normalize(v, a, b){
  if(v==null || !isFinite(v)) return 0.5
  if(a===b) return 0.5
  return (v-a)/(b-a)
}

function nearestStrike(chain, x){
  let best=chain[0]?.strike||x, d=Infinity
  for(const c of chain){ const dd=Math.abs(c.strike-x); if(dd<d){d=dd; best=c.strike} }
  return best
}

export default StrikeRailPro;