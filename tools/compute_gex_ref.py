# python tools/compute_gex_ref.py fixtures/tsla_2025-11-21_raw.json > fixtures/tsla_2025-11-21.json
import json, sys
from math import isnan

def main(p):
    raw = json.load(open(p))
    spot = float(raw["spot"])
    gex_items = []
    for it in raw["chain"]:
        g = float(it.get("gamma",0.0))
        oi = float(it.get("oi",0.0))
        gex = g * oi * 100.0 * (spot ** 2)
        if isnan(gex):
            gex = 0.0
        gex_items.append({"strike": it["strike"], "gex": gex})
    # net & walls
    net = sum(x["gex"] for x in gex_items)
    call_wall = max(gex_items, key=lambda x: x["gex"]) if gex_items else None
    put_wall = min(gex_items, key=lambda x: x["gex"]) if gex_items else None
    out = {
        "symbol": raw["symbol"],
        "expiry": raw["expiry"],
        "spot": spot,
        "strikes": [x["strike"] for x in gex_items],
        "gex_ref": [x["gex"] for x in gex_items],
        "netGex_ref": net,
        "walls_ref": {
            "call": call_wall["strike"] if call_wall else None,
            "put": put_wall["strike"] if put_wall else None,
        }
    }
    print(json.dumps(out, separators=(",",":")))

if __name__ == "__main__":
    main(sys.argv[1])
