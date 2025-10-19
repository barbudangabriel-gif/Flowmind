#!/usr/bin/env python3
import argparse, os, re, sys

TRIPLE = re.compile(r"(?<!\\)(?:'''|\"\"\")")

def collect_indents(lines):
    indents = []
    in_triple = False
    for line in lines:
        # detect entering/leaving triple-quoted strings (very robust for common cases)
        for m in TRIPLE.finditer(line):
            in_triple = not in_triple
        if in_triple:
            continue  # don't consider indentation inside multiline string content
        if not line.strip(): 
            continue
        # count leading spaces only; normalize tabs to 4 spaces first
        raw = line.replace('\t', '    ')
        i = len(raw) - len(raw.lstrip(' '))
        if i > 0:
            indents.append(i)
    # base indent = smallest > 0 (fallback 1)
    return min(indents) if indents else 1

def reindent_text(text, target=4):
    lines = text.splitlines(keepends=True)
    base = collect_indents(lines)
    if base <= 0:
        base = 1

    out = []
    in_triple = False
    for line in lines:
        # toggle triple-quoted state
        for _ in TRIPLE.finditer(line):
            in_triple = not in_triple

        if in_triple or not line.strip():
            out.append(line)
            continue

        # normalize tabs first
        s = line.replace('\t', '    ')
        leading = len(s) - len(s.lstrip(' '))

        if leading == 0:
            out.append(s)
            continue

        # if indentation isn't multiple of base, keep it (likely alignment)
        if leading % base != 0:
            out.append(s)
            continue

        levels = leading // base
        new_leading = ' ' * (levels * target)
        out.append(new_leading + s.lstrip(' '))

    return ''.join(out)

def process_file(path, write=False):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
    except Exception as e:
        print(f"SKIP {path}: {e}", file=sys.stderr)
        return False

    dst = reindent_text(src, target=4)
    changed = (dst != src)

    if changed:
        if write:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(dst)
        print(("FIXED " if write else "WOULD FIX ") + path)
    return changed

def walk(root, write=False):
    pyfiles = []
    if os.path.isfile(root) and root.endswith('.py'):
        pyfiles = [root]
    else:
        for dirpath, _, filenames in os.walk(root):
            # skip common build dirs
            skip = {'.git', 'venv', '.venv', 'node_modules', 'dist', 'build', '__pycache__'}
            if any(part in skip for part in dirpath.split(os.sep)):
                continue
            for fn in filenames:
                if fn.endswith('.py'):
                    pyfiles.append(os.path.join(dirpath, fn))
    changed = 0
    for p in pyfiles:
        if process_file(p, write=write):
            changed += 1
    print(f"{'Changed' if write else 'Would change'} {changed} file(s).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Reindent FlowMind style (1-space units) to 4-space units safely.")
    ap.add_argument("path", help="File or directory")
    ap.add_argument("-w", "--write", action="store_true", help="Write changes (otherwise dry-run)")
    args = ap.parse_args()
    walk(args.path, write=args.write)
