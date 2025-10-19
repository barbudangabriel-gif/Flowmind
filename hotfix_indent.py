#!/usr/bin/env python3
import io, re

# Liniile cu probleme (1-based). Interval = (a,b) inclusiv.
TARGETS = {
    "backend/services/bs.py": [(17,18)],
    "backend/services/builder_engine.py": [(28,29)],
    "backend/services/cache_decorators.py": [37],
    "backend/services/calendar_backtest.py": [(36,37)],
    "backend/services/historical_engine.py": [18],
    "backend/services/optimize_engine.py": [(13,14)],
    "backend/services/options_gex.py": [(19,20)],
    "backend/services/options_provider.py": [(9,10)],
    "backend/services/quality.py": [(8,9)],
    "backend/services/ts_oauth.py": [(24,26)],
    "backend/services/uw_flow.py": [(25,26)],
    "backend/services/warmup.py": [40],
    "backend/services/ws_connection_manager.py": [(39,40)],
    "backend/services/providers/__init__.py": [(10,11)],
    "backend/services/providers/ts_provider.py": [(10,11)],
    "backend/services/providers/uw_provider.py": [(9,10)],
}

TRIPLE = re.compile(r"(?<!\\)(?:'''|\"\"\")")

def to_set(spec):
    s=set()
    for x in spec:
        if isinstance(x,int): s.add(x)
        else: a,b=x; s.update(range(a,b+1))
    return s

def leading_spaces(s): return len(s)-len(s.lstrip(" "))

def fix_file(path):
    try:
        with io.open(path,"r",encoding="utf-8") as f: lines=f.readlines()
    except FileNotFoundError:
        print(f"SKIP  {path} (absent)"); return False

    targets=to_set(TARGETS[path]); changed=False; in_triple=False
    prev_indent=0; prev_colon=False

    for i in range(len(lines)):
        line=lines[i]
        for _ in TRIPLE.finditer(line): in_triple=not in_triple

        if (i+1) in targets and not in_triple:
            cur=leading_spaces(line.replace("\t","    "))
            desired=prev_indent+(4 if prev_colon else 0)
            if cur<desired:
                lines[i]=(" "*desired)+line.lstrip(" \t"); changed=True

        cur_line=lines[i]; stripped=cur_line.strip()
        if stripped and not in_triple and not stripped.startswith("#"):
            prev_indent=leading_spaces(cur_line.replace("\t","    "))
            prev_colon=stripped.endswith(":")

    if changed:
        with io.open(path,"w",encoding="utf-8",newline="") as f: f.writelines(lines)
        print(f"FIXED {path}")
    else:
        print(f"OK    {path}")
    return changed

def main():
    any_change=False
    for p in TARGETS: any_change|=fix_file(p)
    if not any_change: print("Nicio modificare aplicată.")
if __name__=="__main__": main()
