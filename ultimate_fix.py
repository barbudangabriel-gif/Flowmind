#!/usr/bin/env python3
import subprocess
import sys
import re

def check_file(filepath):
    result = subprocess.run(['python', '-m', 'py_compile', filepath], capture_output=True, text=True)
    if result.returncode == 0:
        return None
    match = re.search(r'line (\d+)', result.stderr)
    if match:
        return {'line': int(match.group(1)), 'error': result.stderr}
    return {'line': None, 'error': result.stderr}

def fix_at_line(filepath, target_line):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    if target_line > len(lines) or target_line < 1:
        return False
    
    idx = target_line - 1
    parent_idx = idx - 1
    
    while parent_idx >= 0:
        line = lines[parent_idx]
        if line.strip() and line.rstrip().endswith(':'):
            parent_indent = len(line) - len(line.lstrip(' '))
            fixed = False
            
            for i in range(parent_idx + 1, len(lines)):
                next_line = lines[i]
                if not next_line.strip():
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip(' '))
                if next_indent <= parent_indent:
                    lines[i] = ' ' * (parent_indent + 4) + next_line.lstrip()
                    fixed = True
                else:
                    break
            
            if fixed:
                with open(filepath, 'w') as f:
                    f.writelines(lines)
                return True
            break
        parent_idx -= 1
    
    if idx < len(lines):
        line = lines[idx]
        if line.strip():
            leading = len(line) - len(line.lstrip(' '))
            if 1 <= leading <= 3:
                lines[idx] = ' ' * (leading * 4) + line[leading:]
                with open(filepath, 'w') as f:
                    f.writelines(lines)
                return True
    
    return False

def fix_file(filepath, max_iter=50):
    print(f"\n🔧 {filepath}...")
    for iteration in range(max_iter):
        error_info = check_file(filepath)
        if error_info is None:
            print(f"   ✅ SUCCESS after {iteration + 1} iterations")
            return True
        if error_info['line'] is None:
            print(f"   ❌ Cannot parse error")
            return False
        if not fix_at_line(filepath, error_info['line']):
            print(f"   ❌ Could not fix line {error_info['line']}")
            return False
        print(f"   🔄 Iteration {iteration + 1}: Fixed line {error_info['line']}")
    print(f"   ⚠️  Max iterations reached")
    return False

if __name__ == "__main__":
    files = sys.argv[1:]
    results = {f: fix_file(f) for f in files}
    print("\n" + "="*70)
    success = sum(1 for v in results.values() if v)
    print(f"Total: {success}/{len(results)} files fixed")
    for f, s in results.items():
        print(f"{'✅' if s else '❌'} {f}")
