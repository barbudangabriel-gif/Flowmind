#!/usr/bin/env python3
"""Smart indentation fixer that respects Python block structure"""
import re
import sys

def fix_indentation(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # Skip empty lines and comments at start of line
        if not line.strip() or line.lstrip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Get leading whitespace
        leading = len(line) - len(line.lstrip())
        
        # Fix if not a multiple of 4
        if leading > 0 and leading % 4 != 0:
            # Round down to nearest 4-multiple (conservative approach)
            new_leading = (leading // 4) * 4
            if new_leading == 0 and leading > 0:
                new_leading = 4  # At least one indent level
            line = ' ' * new_leading + line.lstrip()
        
        fixed_lines.append(line)
    
    with open(filename, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed {filename}")

if __name__ == '__main__':
    fix_indentation('backend/server.py')
