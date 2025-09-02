// ---------- NOVICE ----------
const NOVICE = [
  {
    id:'long-call', name:'Long Call', level:'Novice', stance:'bullish',
    tags:['debit','defined-risk'],
    bullets:['Bullish direcțional','Profit nelimitat','Risc limitat la debit','Sensibil la IV și timp (θ−)'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'long_call', legs:[{side:'BUY',kind:'CALL',strike:'ATM',qty:1}], dteHint:30 })
  },
  {
    id:'long-put', name:'Long Put', level:'Novice', stance:'bearish',
    tags:['debit','defined-risk'],
    bullets:['Bearish direcțional','Hedge la downside','Risc limitat la debit','θ−, Vega+'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'long_put', legs:[{side:'BUY',kind:'PUT',strike:'ATM',qty:1}], dteHint:30 })
  },
  {
    id:'covered-call', name:'Covered Call', level:'Novice', stance:'neutral',
    tags:['income','covered','credit'],
    bullets:['Income din primă','Necesită acțiuni long','Cap profit limitat','Risc pe acțiuni'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'covered_call', legs:[{side:'SELL',kind:'CALL',strike:'ATM+5',qty:1}], dteHint:30, notes:'Necesită 100 acțiuni/contract' })
  },
  {
    id:'cash-secured-put', name:'Cash-Secured Put', level:'Novice', stance:'bullish',
    tags:['income','credit'],
    bullets:['Bullish moderat','Prime upfront','Obligație la assignment','Colateral cash'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'cash_secured_put', legs:[{side:'SELL',kind:'PUT',strike:'ATM-5',qty:1}], dteHint:30 })
  },
  {
    id:'protective-put', name:'Protective Put', level:'Novice', stance:'bearish',
    tags:['hedge','debit','defined-risk'],
    bullets:['Hedge pentru acțiuni long','Limitează downside','Cost: debit','Vega+'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'protective_put', legs:[{side:'BUY',kind:'PUT',strike:'ATM',qty:1}], dteHint:30, notes:'Se aplică peste poziție long stock' })
  },
  {
    id:'wheel_strategy', name:'Wheel Strategy', level:'Novice', stance:'neutral',
    tags:['income','assignment','systematic'],
    bullets:['CSP + Covered Call cicluri','Income consistent','Assignment management','Capital intensiv'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'wheel_strategy', legs:[{side:'SELL',kind:'PUT',strike:'ATM-10',qty:1}], dteHint:30 })
  },
  {
    id:'covered_put', name:'Covered Put', level:'Novice', stance:'bearish',
    tags:['income','short-stock'],
    bullets:['Short stock + Short PUT','Income din primă','Risk pe upside','Assignment management'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'covered_put', legs:[{side:'SELL',kind:'PUT',strike:'ATM-5',qty:1}], dteHint:30 })
  },
];

// ---------- INTERMEDIATE ----------
const INTERMEDIATE = [
  {
    id:'bull-call-spread', name:'Bull Call Spread', level:'Intermediate', stance:'bullish',
    tags:['debit','defined-risk','vertical'],
    bullets:['Bullish controlat','Debit redus vs long call','Profit limitat','Risc definit'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'bull_call_spread',
      legs:[
        {side:'BUY',kind:'CALL',strike:'ATM',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
      ], dteHint:35 })
  },
  {
    id:'bear-put-spread', name:'Bear Put Spread', level:'Intermediate', stance:'bearish',
    tags:['debit','defined-risk','vertical'],
    bullets:['Bearish controlat','Debit redus','Profit limitat','Risc definit'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'bear_put_spread',
      legs:[
        {side:'BUY',kind:'PUT',strike:'ATM',qty:1},
        {side:'SELL',kind:'PUT',strike:'ATM-10',qty:1},
      ], dteHint:35 })
  },
  {
    id:'bull-put-spread', name:'Bull Put Spread (Credit)', level:'Intermediate', stance:'bullish',
    tags:['credit','defined-risk','vertical','income'],
    bullets:['Bullish moderat','Credit inițial','Risc limitat','Profit max = credit'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'bull_put_spread',
      legs:[
        {side:'SELL',kind:'PUT',strike:'ATM-5',qty:1},
        {side:'BUY', kind:'PUT',strike:'ATM-15',qty:1},
      ], dteHint:30 })
  },
  {
    id:'bear-call-spread', name:'Bear Call Spread (Credit)', level:'Intermediate', stance:'bearish',
    tags:['credit','defined-risk','vertical','income'],
    bullets:['Bearish moderat','Credit inițial','Risc limitat','Profit max = credit'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'bear_call_spread',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+15',qty:1},
      ], dteHint:30 })
  },
  {
    id:'iron-condor', name:'Iron Condor', level:'Intermediate', stance:'neutral',
    tags:['credit','defined-risk','iron','neutral'],
    bullets:['Neutral / range','Credit inițial','Risc definit','Sensibil la IV'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'iron_condor',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+20',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM-10',qty:1},
        {side:'BUY', kind:'PUT', strike:'ATM-20',qty:1},
      ], dteHint:28 })
  },
  {
    id:'iron-butterfly', name:'Iron Butterfly', level:'Intermediate', stance:'neutral',
    tags:['credit','defined-risk','iron','butterfly','neutral'],
    bullets:['Neutral strâns','Credit mai mare','Risc definit','Profit max la strike central'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'iron_butterfly',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM',qty:1},
        {side:'BUY', kind:'PUT', strike:'ATM-10',qty:1},
      ], dteHint:28 })
  },
  {
    id:'long-straddle', name:'Long Straddle', level:'Intermediate', stance:'neutral',
    tags:['debit','volatility','event'],
    bullets:['Pariezi pe mișcare mare','Debit mare','Profit simetric','IV important'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'long_straddle',
      legs:[
        {side:'BUY',kind:'CALL',strike:'ATM',qty:1},
        {side:'BUY',kind:'PUT', strike:'ATM',qty:1},
      ], dteHint:20 })
  },
  {
    id:'long-strangle', name:'Long Strangle', level:'Intermediate', stance:'neutral',
    tags:['debit','volatility','event'],
    bullets:['Mișcare mare, debit mai mic','Strike-uri OTM','Profit simetric','IV important'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'long_strangle',
      legs:[
        {side:'BUY',kind:'CALL',strike:'ATM+10',qty:1},
        {side:'BUY',kind:'PUT', strike:'ATM-10',qty:1},
      ], dteHint:20 })
  },
  {
    id:'short_straddle', name:'Short Straddle', level:'Intermediate', stance:'neutral',
    tags:['credit','volatility','time-decay'],
    bullets:['Credit upfront','Profit din time decay','Risc la mișcări mari','IV scăzut favorabil'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'short_straddle',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM',qty:1},
      ], dteHint:20 })
  },
  {
    id:'short_strangle', name:'Short Strangle', level:'Intermediate', stance:'neutral',
    tags:['credit','volatility','time-decay'],
    bullets:['Credit mai mic, strike-uri OTM','Profit range mai larg','Time decay profit','IV management'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'short_strangle',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM-10',qty:1},
      ], dteHint:20 })
  },
  {
    id:'calendar_spread', name:'Calendar Spread', level:'Intermediate', stance:'neutral',
    tags:['time-decay','horizontal'],
    bullets:['Profită din time decay diferențial','Range play','IV expansion favorabil','Management complex'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'calendar_spread',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM',qty:1,dte:20},
        {side:'BUY', kind:'CALL',strike:'ATM',qty:1,dte:50},
      ], dteHint:35 })
  },
  {
    id:'diagonal_spread', name:'Diagonal Spread', level:'Intermediate', stance:'neutral',
    tags:['time-decay','diagonal'],
    bullets:['Time + price directional','Strike-uri diferite','Time decay advantage','IV sensitive'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'diagonal_spread',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1,dte:20},
        {side:'BUY', kind:'CALL',strike:'ATM',qty:1,dte:50},
      ], dteHint:35 })
  },
  {
    id:'collar', name:'Collar', level:'Intermediate', stance:'neutral',
    tags:['hedge','stock-protection'],
    bullets:['Stock protection cu income','Long stock + Short CALL + Long PUT','Cost redus/zero','Range definit'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'collar',
      legs:[
        {side:'BUY', kind:'PUT', strike:'ATM-10',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
      ], dteHint:45 })
  },
  {
    id:'risk_reversal', name:'Risk Reversal', level:'Intermediate', stance:'directional',
    tags:['directional','synthetic'],
    bullets:['Long CALL + Short PUT','Zero-cost sau credit','Directional bet','Assignment risk'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'risk_reversal',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM+5',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM-5',qty:1},
      ], dteHint:35 })
  },
];

// ---------- ADVANCED ----------
const ADVANCED = [
  {
    id:'short-put', name:'Short Put (Naked)', level:'Advanced', stance:'bullish',
    tags:['credit','naked','income'],
    bullets:['Bullish/income','Risc mare la downside','Colateral mare','Simplu și lichid'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'short_put', legs:[{side:'SELL',kind:'PUT',strike:'ATM-5',qty:1}], dteHint:25 })
  },
  {
    id:'short-call', name:'Short Call (Naked)', level:'Advanced', stance:'bearish',
    tags:['credit','naked'],
    bullets:['Bearish/income','Risc nelimitat upside','Necesită margine','Atenție la IV'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'short_call', legs:[{side:'SELL',kind:'CALL',strike:'ATM+5',qty:1}], dteHint:25 })
  },
  {
    id:'jade-lizard', name:'Jade Lizard', level:'Advanced', stance:'bullish',
    tags:['credit','no-upside-risk'],
    bullets:['Fără risc pe upside dacă credit ≥ spread','Risc pe downside','Credit net','Management atent'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'jade_lizard',
      legs:[
        {side:'SELL',kind:'PUT', strike:'ATM-5',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
      ], dteHint:30 })
  },
  {
    id:'call-ratio-backspread', name:'Call Ratio Backspread', level:'Advanced', stance:'directional',
    tags:['ratio','convexity','debit/credit'],
    bullets:['Expunere convexă pe upside','Poate fi debit/credit','Risc jos controlat','Vega+'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'call_ratio_backspread',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+10',qty:2},
      ], dteHint:35 })
  },
  {
    id:'butterfly_spread', name:'Butterfly Spread', level:'Advanced', stance:'neutral',
    tags:['debit','defined-risk','neutral'],
    bullets:['Debit strategy','Profit maxim la middle strike','Risc limitat','Time decay profit'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'butterfly_spread',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM-10',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM',qty:2},
        {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
      ], dteHint:30 })
  },
  {
    id:'condor_spread', name:'Condor Spread', level:'Advanced', stance:'neutral',
    tags:['debit','defined-risk','wide-range'],
    bullets:['Range mai larg decât butterfly','4 strike-uri','Profit constant în range','Management complex'],
    preview:'range',
    buildParams:(s)=>({ strategyId:'condor_spread',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM-15',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM-5',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
        {side:'BUY', kind:'CALL',strike:'ATM+15',qty:1},
      ], dteHint:30 })
  },
  {
    id:'ratio_call_spread', name:'Ratio Call Spread', level:'Advanced', stance:'bullish',
    tags:['ratio','credit/debit'],
    bullets:['1:2 sau 1:3 ratio','Upside exposure','Risk pe breakout','Adjustment complex'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'ratio_call_spread',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+10',qty:2},
      ], dteHint:35 })
  },
  {
    id:'ratio_put_spread', name:'Ratio Put Spread', level:'Advanced', stance:'bearish',
    tags:['ratio','credit/debit'],
    bullets:['1:2 sau 1:3 ratio PUT','Downside exposure','Risk pe breakdown','Volatility sensitive'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'ratio_put_spread',
      legs:[
        {side:'BUY', kind:'PUT',strike:'ATM',qty:1},
        {side:'SELL',kind:'PUT',strike:'ATM-10',qty:2},
      ], dteHint:35 })
  },
  {
    id:'big_lizard', name:'Big Lizard', level:'Advanced', stance:'bearish',
    tags:['credit','no-downside-risk'],
    bullets:['Reverse jade lizard','Fără risc pe downside dacă credit ≥ spread','Risc pe upside','Management atent'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'big_lizard',
      legs:[
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM-5',qty:1},
        {side:'BUY', kind:'PUT', strike:'ATM-10',qty:1},
      ], dteHint:30 })
  },
  {
    id:'broken_wing_butterfly', name:'Broken Wing Butterfly', level:'Advanced', stance:'directional',
    tags:['asymmetric','debit','directional-bias'],
    bullets:['Butterfly asimetric','Bias directional','Risk/reward asimetric','Management complex'],
    preview:'skew',
    buildParams:(s)=>({ strategyId:'broken_wing_butterfly',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM-5',qty:1},
        {side:'SELL',kind:'CALL',strike:'ATM+5',qty:2},
        {side:'BUY', kind:'CALL',strike:'ATM+20',qty:1},
      ], dteHint:30 })
  },
];

// ---------- EXPERT ----------
const EXPERT = [
  {
    id:'synthetic-long-future', name:'Synthetic Long (Call+Short Put)', level:'Expert', stance:'bullish',
    tags:['synthetic','directional'],
    bullets:['Replică long stock cu opțiuni','Cost de capital redus','Risc ca stocul','Greeks ca delta≈1'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'synthetic_long',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM',qty:1},
      ], dteHint:45 })
  },
  {
    id:'risk-reversal-bull', name:'Risk Reversal (Bullish)', level:'Expert', stance:'bullish',
    tags:['directional','credit/debit'],
    bullets:['Long CALL + Short PUT','Direcțional bullish','Poate fi zero-cost','Risc assignment pe PUT'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'risk_reversal_bull',
      legs:[
        {side:'BUY', kind:'CALL',strike:'ATM+5',qty:1},
        {side:'SELL',kind:'PUT', strike:'ATM-5',qty:1},
      ], dteHint:35 })
  },
  {
    id:'strip', name:'Strip (2P+1C)', level:'Expert', stance:'bearish',
    tags:['debit','volatility'],
    bullets:['Bias bearish pe straddle','Profit mai mare pe jos','Debit ridicat','IV critic'],
    preview:'down',
    buildParams:(s)=>({ strategyId:'strip',
      legs:[
        {side:'BUY',kind:'PUT', strike:'ATM',qty:2},
        {side:'BUY',kind:'CALL',strike:'ATM',qty:1},
      ], dteHint:20 })
  },
  {
    id:'strap', name:'Strap (2C+1P)', level:'Expert', stance:'bullish',
    tags:['debit','volatility'],
    bullets:['Bias bullish pe straddle','Profit mai mare pe sus','Debit ridicat','IV critic'],
    preview:'up',
    buildParams:(s)=>({ strategyId:'strap',
      legs:[
        {side:'BUY',kind:'CALL',strike:'ATM',qty:2},
        {side:'BUY',kind:'PUT', strike:'ATM',qty:1},
      ], dteHint:20 })
  },
];

// ---------- EXPORT AGREGAT ----------
export const STRATEGIES = {
  Novice: NOVICE,
  Intermediate: INTERMEDIATE,
  Advanced: ADVANCED,
  Expert: EXPERT,
};

export const ALL_STRATEGIES = [
  ...NOVICE, ...INTERMEDIATE, ...ADVANCED, ...EXPERT
];