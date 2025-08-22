"""
Data loaders pentru Sell Puts Toolkit.
Permite citirea de poziții din CSV sau JSON și transformarea lor în Position.
"""
from __future__ import annotations
from typing import List
import json
import pandas as pd
from sell_puts_engine import Position

CSV_COLUMNS = [
    "ticker","price","strike","delta","dte","premium","iv_rank","vix",
    "selected","assigned","status","contracts","notes"
]

def _coerce_bool(x):
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    return s in ("1","true","yes","y")

def positions_from_dataframe(df: pd.DataFrame) -> List[Position]:
    rows: List[Position] = []
    for _, r in df.iterrows():
        rows.append(Position(
            ticker=str(r.get("ticker",""))).upper(),
            price=float(r.get("price",0) or 0),
            strike=float(r.get("strike",0) or 0),
            delta=float(r.get("delta",0) or 0),
            dte=int(r.get("dte",0) or 0),
            premium=float(r.get("premium",0) or 0),
            iv_rank=float(r.get("iv_rank",0) or 0),
            vix=float(r.get("vix",0) or 0),
            selected=_coerce_bool(r.get("selected", True)),
            assigned=_coerce_bool(r.get("assigned", False)),
            status=str(r.get("status","Active")) or "Active",
            contracts=int(r.get("contracts",0) or 0),
            notes=str(r.get("notes",""))
        ))
    return rows

def load_positions_from_csv(path: str) -> List[Position]:
    df = pd.read_csv(path)
    for c in CSV_COLUMNS:
        if c not in df.columns:
            df[c] = None if c not in ("selected","assigned") else False
    return positions_from_dataframe(df)

def load_positions_from_json(path: str) -> List[Position]:
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("positions", data)
    df = pd.DataFrame(items)
    for c in CSV_COLUMNS:
        if c not in df.columns:
            df[c] = None if c not in ("selected","assigned") else False
    return positions_from_dataframe(df)