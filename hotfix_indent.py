#!/usr/bin/env python3
import io, os, re, sys

# --- CONFIG: fișier -> linii sau intervale (inclusive) ---
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
    """Normalizează lista de linii/intervale în set de indici (1-based)."""
    s = set()
    for x in spec:
        if isinstance(x, int):
            s.add(x)
        elif isinstance(x, tuple):
            a, b = x
            s.update(range(a, b+1))
        else:
            raise ValueError(f"linie/interval invalid: {x}")
    return s

def leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip(" "))

def hotfix_file(path: str) -> bool:
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"SKIP (absent): {path}")
        return False

    targets = to_set(TARGETS[path])
    changed = False
    in_triple = False

    # utilitar: găsește indentul și dacă linia anterioară deschide bloc
    prev_code_indent = 0
    prev_ends_colon = False

    for i in range(len(lines)):
        line = lines[i]

        # toggle triple-quoted state pe linia curentă
        for _ in TRIPLE.finditer(line):
            in_triple = not in_triple

        stripped = line.strip()
        if stripped and not in_triple and not stripped.startswith("#"):
            # actualizează pentru linia curentă, DAR folosim valorile anterioare pentru țintă
            pass

        if (i+1) in targets and not in_triple:
            cur_indent = leading_spaces(line.replace("\t", "    "))
            # regulă: dacă linia anterioară are ':' la final → +4; altfel, minim indentul anterior
            desired = prev_code_indent + (4 if prev_ends_colon else 0)
            if cur_indent < desired:
                new_line = (" " * desired) + line.lstrip(" \t")
                if new_line != line:
                    lines[i] = new_line
                    changed = True

        # update prev_* pe baza liniei curente (după aplicarea potențială)
        cur_line = lines[i]
        cur_stripped = cur_line.strip()
        if cur_stripped and not in_triple and not cur_stripped.startswith("#"):
            prev_code_indent = leading_spaces(cur_line.replace("\t", "    "))
            prev_ends_colon = cur_stripped.endswith(":")

    if changed:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        print(f"FIXED  {path}")
    else:
        print(f"OK     {path}")
    return changed

def main():
    any_change = False
    for path in TARGETS:
        any_change |= hotfix_file(path)
    if not any_change:
        print("Nicio modificare aplicată (poate erau deja corecte).")

if __name__ == "__main__":
    main()
