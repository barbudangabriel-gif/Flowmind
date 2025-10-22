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
 id:'long-call-butterfly', name:'Long Call Butterfly', level:'Intermediate', stance:'neutral',
 tags:['debit','defined-risk','butterfly'],
 bullets:['Profit la middle strike','Risc limitat','Time decay favorabil','Range strâns'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'long_call_butterfly',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM-10',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM',qty:2},
 {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
 ], dteHint:30 })
 },
 {
 id:'long-put-butterfly', name:'Long Put Butterfly', level:'Intermediate', stance:'neutral',
 tags:['debit','defined-risk','butterfly'],
 bullets:['Profit la middle strike','Risc limitat PUT variant','Time decay favorabil','Range strâns'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'long_put_butterfly',
 legs:[
 {side:'BUY', kind:'PUT',strike:'ATM+10',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM',qty:2},
 {side:'BUY', kind:'PUT',strike:'ATM-10',qty:1},
 ], dteHint:30 })
 },
 {
 id:'short-call-butterfly', name:'Short Call Butterfly', level:'Intermediate', stance:'neutral',
 tags:['credit','volatility','butterfly'],
 bullets:['Credit upfront','Profit dacă mișcare mare','Time decay defavorabil','Inverse butterfly'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'short_call_butterfly',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM-10',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM',qty:2},
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
 ], dteHint:30 })
 },
 {
 id:'short-put-butterfly', name:'Short Put Butterfly', level:'Intermediate', stance:'neutral',
 tags:['credit','volatility','butterfly'],
 bullets:['Credit upfront PUT variant','Profit dacă mișcare mare','Time decay defavorabil','Inverse butterfly'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'short_put_butterfly',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM+10',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM',qty:2},
 {side:'SELL',kind:'PUT',strike:'ATM-10',qty:1},
 ], dteHint:30 })
 },
 {
 id:'inverse-iron-butterfly', name:'Inverse Iron Butterfly', level:'Intermediate', stance:'neutral',
 tags:['debit','volatility','iron'],
 bullets:['Reverse iron butterfly','Profit pe mișcare mare','Risc definit','Volatility play'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'inverse_iron_butterfly',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-10',qty:1},
 ], dteHint:28 })
 },
 {
 id:'inverse-iron-condor', name:'Inverse Iron Condor', level:'Intermediate', stance:'neutral',
 tags:['debit','volatility','iron'],
 bullets:['Reverse iron condor','Profit pe breakout','Risc definit','Volatility expansion'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'inverse_iron_condor',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+20',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-10',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-20',qty:1},
 ], dteHint:28 })
 },
 {
 id:'calendar-call-spread', name:'Calendar Call Spread', level:'Intermediate', stance:'neutral',
 tags:['time-decay','horizontal','call'],
 bullets:['Time decay CALL variant','Near-term vs far-term','IV expansion favorabil','Management activ'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'calendar_call_spread',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM',qty:1,dte:20},
 {side:'BUY', kind:'CALL',strike:'ATM',qty:1,dte:50},
 ], dteHint:35 })
 },
 {
 id:'calendar-put-spread', name:'Calendar Put Spread', level:'Intermediate', stance:'neutral',
 tags:['time-decay','horizontal','put'],
 bullets:['Time decay PUT variant','Near-term vs far-term','IV expansion favorabil','Bearish bias'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'calendar_put_spread',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM',qty:1,dte:20},
 {side:'BUY', kind:'PUT',strike:'ATM',qty:1,dte:50},
 ], dteHint:35 })
 },
 {
 id:'diagonal-call-spread', name:'Diagonal Call Spread', level:'Intermediate', stance:'bullish',
 tags:['time-decay','diagonal','call'],
 bullets:['Time + price directional CALL','Strike-uri diferite','Bullish bias','IV sensitive'],
 preview:'up',
 buildParams:(s)=>({ strategyId:'diagonal_call_spread',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1,dte:20},
 {side:'BUY', kind:'CALL',strike:'ATM',qty:1,dte:50},
 ], dteHint:35 })
 },
 {
 id:'diagonal-put-spread', name:'Diagonal Put Spread', level:'Intermediate', stance:'bearish',
 tags:['time-decay','diagonal','put'],
 bullets:['Time + price directional PUT','Strike-uri diferite','Bearish bias','IV sensitive'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'diagonal_put_spread',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM-5',qty:1,dte:20},
 {side:'BUY', kind:'PUT',strike:'ATM',qty:1,dte:50},
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
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:2},
 ], dteHint:35 })
 },
 {
 id:'long-call-condor', name:'Long Call Condor', level:'Advanced', stance:'neutral',
 tags:['debit','defined-risk','condor','wide-range'],
 bullets:['Range mai larg CALL variant','4 strike-uri','Profit în range','Risc limitat'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'long_call_condor',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM-15',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM-5',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM+15',qty:1},
 ], dteHint:30 })
 },
 {
 id:'long-put-condor', name:'Long Put Condor', level:'Advanced', stance:'neutral',
 tags:['debit','defined-risk','condor','wide-range'],
 bullets:['Range mai larg PUT variant','4 strike-uri','Profit în range','Risc limitat'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'long_put_condor',
 legs:[
 {side:'BUY', kind:'PUT',strike:'ATM+15',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM+5',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-5',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-15',qty:1},
 ], dteHint:30 })
 },
 {
 id:'short-call-condor', name:'Short Call Condor', level:'Advanced', stance:'neutral',
 tags:['credit','volatility','condor'],
 bullets:['Credit condor CALL','Profit pe breakout','Wide range risc','Volatility play'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'short_call_condor',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM-15',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM-5',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM+5',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+15',qty:1},
 ], dteHint:30 })
 },
 {
 id:'short-put-condor', name:'Short Put Condor', level:'Advanced', stance:'neutral',
 tags:['credit','volatility','condor'],
 bullets:['Credit condor PUT','Profit pe breakout','Wide range risc','Volatility play'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'short_put_condor',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM+15',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM+5',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-5',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-15',qty:1},
 ], dteHint:30 })
 },
 {
 id:'put-ratio-backspread', name:'Put Ratio Backspread', level:'Advanced', stance:'bearish',
 tags:['ratio','convexity','debit/credit'],
 bullets:['Expunere convexă pe downside','Poate fi debit/credit','Risc sus controlat','Bearish bias'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'put_ratio_backspread',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM-5',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-10',qty:2},
 ], dteHint:35 })
 },
 {
 id:'call-broken-wing', name:'Call Broken Wing Butterfly', level:'Advanced', stance:'bullish',
 tags:['asymmetric','debit','directional-bias'],
 bullets:['Butterfly asimetric CALL','Bias bullish','Risk/reward asimetric','Profit pe sus'],
 preview:'skew',
 buildParams:(s)=>({ strategyId:'call_broken_wing',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM-5',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+5',qty:2},
 {side:'BUY', kind:'CALL',strike:'ATM+20',qty:1},
 ], dteHint:30 })
 },
 {
 id:'put-broken-wing', name:'Put Broken Wing Butterfly', level:'Advanced', stance:'bearish',
 tags:['asymmetric','debit','directional-bias'],
 bullets:['Butterfly asimetric PUT','Bias bearish','Risk/reward asimetric','Profit pe jos'],
 preview:'skew',
 buildParams:(s)=>({ strategyId:'put_broken_wing',
 legs:[
 {side:'BUY', kind:'PUT',strike:'ATM+5',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-5',qty:2},
 {side:'BUY', kind:'PUT',strike:'ATM-20',qty:1},
 ], dteHint:30 })
 },
 {
 id:'inverse-call-broken-wing', name:'Inverse Call Broken Wing', level:'Advanced', stance:'directional',
 tags:['asymmetric','credit','volatility'],
 bullets:['Reverse broken wing CALL','Credit strategy','Profit pe mișcare','Asimetric'],
 preview:'skew',
 buildParams:(s)=>({ strategyId:'inverse_call_broken_wing',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM-5',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM+5',qty:2},
 {side:'SELL',kind:'CALL',strike:'ATM+20',qty:1},
 ], dteHint:30 })
 },
 {
 id:'inverse-put-broken-wing', name:'Inverse Put Broken Wing', level:'Advanced', stance:'directional',
 tags:['asymmetric','credit','volatility'],
 bullets:['Reverse broken wing PUT','Credit strategy','Profit pe mișcare','Asimetric'],
 preview:'skew',
 buildParams:(s)=>({ strategyId:'inverse_put_broken_wing',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM+5',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-5',qty:2},
 {side:'SELL',kind:'PUT',strike:'ATM-20',qty:1},
 ], dteHint:30 })
 },
 {
 id:'covered-short-straddle', name:'Covered Short Straddle', level:'Advanced', stance:'neutral',
 tags:['income','stock-required','credit'],
 bullets:['Short straddle + long stock','Income mare','Risc pe jos limitat','Stock assignment'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'covered_short_straddle',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM',qty:1},
 ], dteHint:20, notes:'Necesită 100 acțiuni/contract' })
 },
 {
 id:'covered-short-strangle', name:'Covered Short Strangle', level:'Advanced', stance:'neutral',
 tags:['income','stock-required','credit'],
 bullets:['Short strangle + long stock','Income moderat','Range mai larg','Stock assignment'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'covered_short_strangle',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-10',qty:1},
 ], dteHint:20, notes:'Necesită 100 acțiuni/contract' })
 },
 {
 id:'bull-call-ladder', name:'Bull Call Ladder', level:'Advanced', stance:'bullish',
 tags:['ratio','ladder','credit/debit'],
 bullets:['3-leg ladder CALL','Bullish cu risc limitat','Profit treptat','Management complex'],
 preview:'up',
 buildParams:(s)=>({ strategyId:'bull_call_ladder',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
 {side:'SELL',kind:'CALL',strike:'ATM+20',qty:1},
 ], dteHint:35 })
 },
 {
 id:'bear-call-ladder', name:'Bear Call Ladder', level:'Advanced', stance:'bearish',
 tags:['ratio','ladder','credit'],
 bullets:['3-leg ladder CALL bearish','Credit strategy','Profit treptat jos','Risc pe sus'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'bear_call_ladder',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM+10',qty:1},
 {side:'BUY', kind:'CALL',strike:'ATM+20',qty:1},
 ], dteHint:35 })
 },
 {
 id:'bull-put-ladder', name:'Bull Put Ladder', level:'Advanced', stance:'bullish',
 tags:['ratio','ladder','credit'],
 bullets:['3-leg ladder PUT bullish','Credit strategy','Profit treptat sus','Risc pe jos'],
 preview:'up',
 buildParams:(s)=>({ strategyId:'bull_put_ladder',
 legs:[
 {side:'SELL',kind:'PUT',strike:'ATM',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-10',qty:1},
 {side:'BUY', kind:'PUT',strike:'ATM-20',qty:1},
 ], dteHint:35 })
 },
 {
 id:'bear-put-ladder', name:'Bear Put Ladder', level:'Advanced', stance:'bearish',
 tags:['ratio','ladder','debit'],
 bullets:['3-leg ladder PUT bearish','Bearish cu profit limitat','Profit treptat jos','Management complex'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'bear_put_ladder',
 legs:[
 {side:'BUY', kind:'PUT',strike:'ATM',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-10',qty:1},
 {side:'SELL',kind:'PUT',strike:'ATM-20',qty:1},
 ], dteHint:35 })
 },
 {
 id:'reverse-jade-lizard', name:'Reverse Jade Lizard', level:'Advanced', stance:'bearish',
 tags:['credit','no-downside-risk'],
 bullets:['Jade lizard inversat','Fără risc jos dacă credit mare','Risc pe sus','Big Lizard alias'],
 preview:'skew',
 buildParams:(s)=>({ strategyId:'reverse_jade_lizard',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM+5',qty:1},
 {side:'SELL',kind:'PUT', strike:'ATM-5',qty:1},
 {side:'BUY', kind:'PUT', strike:'ATM-10',qty:1},
 ], dteHint:30 })
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
 {side:'BUY',kind:'PUT', strike:'ATM',qty:1},
 ], dteHint:20 })
 },
 {
 id:'long-synthetic-future', name:'Long Synthetic Future', level:'Expert', stance:'bullish',
 tags:['synthetic','directional','future'],
 bullets:['Replică long future','Long CALL + Short PUT','Delta ~1.0','Capital redus vs stock'],
 preview:'up',
 buildParams:(s)=>({ strategyId:'long_synthetic_future',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM',qty:1},
 {side:'SELL',kind:'PUT', strike:'ATM',qty:1},
 ], dteHint:45 })
 },
 {
 id:'short-synthetic-future', name:'Short Synthetic Future', level:'Expert', stance:'bearish',
 tags:['synthetic','directional','future'],
 bullets:['Replică short future','Short CALL + Long PUT','Delta ~-1.0','Risc nelimitat'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'short_synthetic_future',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM',qty:1},
 {side:'BUY', kind:'PUT', strike:'ATM',qty:1},
 ], dteHint:45 })
 },
 {
 id:'synthetic-put', name:'Synthetic Put', level:'Expert', stance:'bearish',
 tags:['synthetic','hedge'],
 bullets:['Replică long put','Short stock + Long CALL','Hedge sintetic','Management activ'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'synthetic_put',
 legs:[
 {side:'BUY',kind:'CALL',strike:'ATM',qty:1},
 ], dteHint:45, notes:'Necesită short stock position' })
 },
 {
 id:'long-combo', name:'Long Combo', level:'Expert', stance:'bullish',
 tags:['synthetic','directional','arbitrage'],
 bullets:['Long CALL ITM + Short PUT OTM','Bullish sintetic','Cost redus','Assignment risk'],
 preview:'up',
 buildParams:(s)=>({ strategyId:'long_combo',
 legs:[
 {side:'BUY', kind:'CALL',strike:'ATM-10',qty:1},
 {side:'SELL',kind:'PUT', strike:'ATM+10',qty:1},
 ], dteHint:45 })
 },
 {
 id:'short-combo', name:'Short Combo', level:'Expert', stance:'bearish',
 tags:['synthetic','directional','arbitrage'],
 bullets:['Short CALL OTM + Long PUT ITM','Bearish sintetic','Cost redus','Risk management'],
 preview:'down',
 buildParams:(s)=>({ strategyId:'short_combo',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1},
 {side:'BUY', kind:'PUT', strike:'ATM-10',qty:1},
 ], dteHint:45 })
 },
 {
 id:'guts', name:'Guts (Long)', level:'Expert', stance:'neutral',
 tags:['debit','volatility','ITM'],
 bullets:['Long ITM CALL + Long ITM PUT','Debit mare','Profit pe mișcare mare','Similar straddle ITM'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'guts',
 legs:[
 {side:'BUY',kind:'CALL',strike:'ATM-10',qty:1},
 {side:'BUY',kind:'PUT', strike:'ATM+10',qty:1},
 ], dteHint:20 })
 },
 {
 id:'short-guts', name:'Short Guts', level:'Expert', stance:'neutral',
 tags:['credit','time-decay','ITM'],
 bullets:['Short ITM CALL + Short ITM PUT','Credit mare','Profit în range strâns','Risc mare assignment'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'short_guts',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM-10',qty:1},
 {side:'SELL',kind:'PUT', strike:'ATM+10',qty:1},
 ], dteHint:20 })
 },
 {
 id:'double-diagonal', name:'Double Diagonal', level:'Expert', stance:'neutral',
 tags:['time-decay','diagonal','complex'],
 bullets:['Diagonal CALL + Diagonal PUT','Time decay profit','IV management complex','Multi-expiration'],
 preview:'range',
 buildParams:(s)=>({ strategyId:'double_diagonal',
 legs:[
 {side:'SELL',kind:'CALL',strike:'ATM+10',qty:1,dte:20},
 {side:'BUY', kind:'CALL',strike:'ATM+5', qty:1,dte:50},
 {side:'SELL',kind:'PUT', strike:'ATM-10',qty:1,dte:20},
 {side:'BUY', kind:'PUT', strike:'ATM-5', qty:1,dte:50},
 ], dteHint:35 })
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