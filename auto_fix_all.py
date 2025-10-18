#!/usr/bin/env python3
import subprocess, re, io

TRIPLE = re.compile(r"(?<!\\)(?:'''|\"\"\")")
OPENERS = ("try","if","for","while","with","def","class")
DEDIT = ("except","finally","elif","else")

def leading_spaces(s): return len(s) - len(s.lstrip(" "))

def find_opener_indent(lines, start_idx):
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

def fix_one_line(path, line_no):
    """Fix single line in file"""
    with io.open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if line_no < 1 or line_no > len(lines):
        return False
    
    i = line_no - 1
    line = lines[i]
    stripped = line.strip()
    cur = leading_spaces(line.replace("\t", "    "))
    
    # Find prev indent
    prev_indent = 0
    prev_colon = False
    in_triple = False
    
    for j in range(i):
        l = lines[j]
        for _ in TRIPLE.finditer(l): in_triple = not in_triple
        s = l.strip()
        if s and not in_triple and not s.startswith("#"):
            prev_indent = leading_spaces(l.replace("\t", "    "))
            prev_colon = s.endswith(":")
    
    # Determine desired indent
    starts = stripped.split(":", 1)[0].split()
    if starts and starts[0] in DEDIT:
        desired = find_opener_indent(lines, i - 1)
    else:
        desired = prev_indent + (4 if prev_colon else 0)
    
    if cur < desired:
        lines[i] = (" " * desired) + line.lstrip(" \t")
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        return True
    return False

def get_errors():
    """Run compileall and extract errors"""
    result = subprocess.run(
        ["python", "-m", "compileall", "-q", "backend/services"],
        capture_output=True, text=True
    )
    
    errors = []
    combined = result.stdout + result.stderr
    lines = combined.split("\n")
    
    current_file = None
    for line in lines:
        # Match file: *** Error compiling 'backend/services/file.py'...
        m1 = re.search(r"'(backend/services/[^']+)'", line)
        if m1:
            current_file = m1.group(1)
            continue
        
        # Match line number: Sorry: IndentationError: ... on line 35
        if current_file:
            m2 = re.search(r"line (\d+)", line)
            if m2:
                errors.append((current_file, int(m2.group(1))))
                current_file = None
    
    return errors

def main():
    max_iterations = 100
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        errors = get_errors()
        
        if not errors:
            print(f"\n🎉 SUCCESS dopo {iteration} iterazioni!")
            return True
        
        print(f"\nIterazione {iteration}: {len(errors)} errori da correggere")
        
        fixed = 0
        for path, line_no in errors[:5]:  # Fix 5 at a time
            if fix_one_line(path, line_no):
                print(f"  ✓ {path}:{line_no}")
                fixed += 1
        
        if fixed == 0:
            print("\n⚠️ Nessun progresso - errori rimasti:")
            for path, line_no in errors[:10]:
                print(f"  - {path}:{line_no}")
            return False
    
    print(f"\n⚠️ Timeout dopo {max_iterations} iterazioni")
    return False

if __name__ == "__main__":
    main()
