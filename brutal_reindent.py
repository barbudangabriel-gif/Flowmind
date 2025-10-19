#!/usr/bin/env python3
import os, re

def brutal_fix(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    fixed = []
    for line in lines:
        # Calculează numărul de spații leading
        stripped = line.lstrip(' ')
        if line == stripped:  # Nu are spații la început
            fixed.append(line)
            continue
        
        leading_spaces = len(line) - len(stripped)
        # Multiplică cu 4
        new_indent = ' ' * (leading_spaces * 4)
        fixed.append(new_indent + stripped)
    
    with open(path, 'w') as f:
        f.writelines(fixed)
    print(f"FIXED {path}")

def main():
    for root, dirs, files in os.walk('backend/services'):
        if '__pycache__' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                brutal_fix(path)

if __name__ == '__main__':
    main()
