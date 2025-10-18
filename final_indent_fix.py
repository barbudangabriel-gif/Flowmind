#!/usr/bin/env python3
"""
FINAL FIX: Convertește corect 1-space indent → 4-space indent.
Strategia: Pentru fiecare linie, dacă are leading spaces, înlocuiește cu 4x.
"""
import os, re

def fix_indent_1_to_4(path):
    """Convert 1-space indent to 4-space indent."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if not line or line[0] not in ' \t':
            # Nu are indent
            fixed_lines.append(line)
            continue
        
        # Calculează indent original (numai spații, nu tabs)
        original = line
        stripped = line.lstrip(' ')
        
        if line == stripped:
            # Nu avea spații (poate avea tabs)
            fixed_lines.append(line)
            continue
        
        spaces = len(line) - len(stripped)
        
        # Multiplică cu 4
        new_indent = ' ' * (spaces * 4)
        fixed_lines.append(new_indent + stripped)
    
    # Scrie înapoi
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    return True

def main():
    count = 0
    for root, dirs, files in os.walk('backend/services'):
        # Skip __pycache__
        if '__pycache__' in root:
            continue
        
        for fname in files:
            if fname.endswith('.py'):
                path = os.path.join(root, fname)
                fix_indent_1_to_4(path)
                count += 1
                print(f"✓ {path}")
    
    print(f"\n✅ Processed {count} files")

if __name__ == '__main__':
    main()
