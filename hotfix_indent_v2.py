#!/usr/bin/env python3
import io, re

# ---- Liniile țintă (1-based), unite cu cele din primul pas + noile tale ----
TARGETS = {
    "backend/services/bs.py":            [(17,18), (25,26)],
    "backend/services/builder_engine.py":[(28,29), (30,31)],
    "backend/services/cache_decorators.py":[37],
    "backend/services/calendar_backtest.py":[(36,37)],
    "backend/services/historical_engine.py":[18],
    "backend/services/optimize_engine.py":[(13,15)],            # 13-15
    "backend/services/options_gex.py":   [(19,22)],              # 19-22
    "backend/services/options_provider.py":[(9,10), (14,19)],    # 9-10 + 14-19
    "backend/services/quality.py":       [(8,9), (11,12)],       # 8-9 + 11-12
    "backend/services/ts_oauth.py":      [(24,27)],              # 24-27
    "backend/services/uw_flow.py":       [27],                   # except/finally
    "backend/services/warmup.py":        [40],
    "backend/services/ws_connection_manager.py":[(39,40), (53,54)],
    "backend/services/providers/__init__.py":[(10,13)],          # 10-13
    "backend/services/providers/ts_provider.py":[(10,11), (13,14)],
    "backend/services/providers/uw_provider.py":[(9,10), (14,15)],
}

TRIPLE = re.compile(r"(?<!\\)(?:'''|\"\"\")")
OPENERS = ("try","if","for","while","with","def","class")
DEDIT = ("except","finally","elif","else")

def to_set(spec):
    s=set()
    for x in spec:
        if isinstance(x,int): s.add(x)
        else: a,b=x; s.update(range(a,b+1))
    return s

def leading_spaces(s): return len(s) - len(s.lstrip(" "))

def find_opener_indent(lines, start_idx):
    """Caută în sus indentul unui opener (try/if/for/...) pentru except/elif/else/finally."""
    in_triple=False
    for j in range(start_idx, -1, -1):
        line = lines[j]
        for _ in TRIPLE.finditer(line): in_triple = not in_triple
        if in_triple: continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"): continue
        if stripped.endswith(":"):
            head = stripped.split(":",1)[0].split()
            if head and head[0] in OPENERS:
                return leading_spaces(line.replace("\t","    "))
    return 0

def fix_file(path):
    try:
        with io.open(path,"r",encoding="utf-8") as f: lines=f.readlines()
    except FileNotFoundError:
        print(f"SKIP  {path} (absent)"); return False

    targets = to_set(TARGETS[path])
    changed=False; in_triple=False

    # păstrăm ultimele info de flux
    prev_indent=0; prev_colon=False

    for i in range(len(lines)):
        line = lines[i]
        # toggle triple quotes
        for _ in TRIPLE.finditer(line): in_triple = not in_triple

        if (i+1) in targets and not in_triple:
            stripped = line.strip()
            cur = leading_spaces(line.replace("\t","    "))

            # caz: dedent keywords (except/finally/elif/else)
            starts = stripped.split(":",1)[0].split()
            if starts and starts[0] in DEDIT:
                desired = find_opener_indent(lines, i-1)
            else:
                # regulă default: dacă linia anterioară se termină cu ":", +4
                desired = prev_indent + (4 if prev_colon else 0)

            if cur < desired:
                lines[i] = (" " * desired) + line.lstrip(" \t")
                changed=True

        # update „prev" pe baza liniei curente
        cur_line = lines[i]
        s = cur_line.strip()
        if s and not in_triple and not s.startswith("#"):
            prev_indent = leading_spaces(cur_line.replace("\t","    "))
            prev_colon  = s.endswith(":")

    if changed:
        with io.open(path,"w",encoding="utf-8",newline="") as f: f.writelines(lines)
        print(f"FIXED {path}")
    else:
        print(f"OK    {path}")
    return changed

def main():
    any_change=False
    for p in TARGETS: any_change |= fix_file(p)
    if not any_change: print("Nicio modificare aplicată.")
if __name__=="__main__": main()
