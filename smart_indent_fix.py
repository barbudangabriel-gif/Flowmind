#!/usr/bin/env python3
"""
Smart Python Indent Fixer
Fixes mixed 1-space/4-space indentation by analyzing context
"""
import sys
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    fixed = []
    
    for i, line in enumerate(lines):
        # Empty line or no leading spaces
        if not line.strip() or line[0] != ' ':
            fixed.append(line)
            continue
        
        # Count leading spaces
        leading = len(line) - len(line.lstrip(' '))
        
        # If 1, 2, or 3 spaces, it's clearly wrong - multiply by 4
        if leading in [1, 2, 3]:
            new_line = ' ' * (leading * 4) + line[leading:]
            fixed.append(new_line)
        # If 4-7 spaces, check context
        elif 4 <= leading <= 7:
            # Look at previous non-empty line
            prev_i = i - 1
            while prev_i >= 0 and not lines[prev_i].strip():
                prev_i -= 1
            
            if prev_i >= 0:
                prev_line = lines[prev_i]
                prev_leading = len(prev_line) - len(prev_line.lstrip(' '))
                
                # If previous line ends with `:`, this should be indented more
                if prev_line.rstrip().endswith(':'):
                    if leading <= prev_leading:
                        # Same or less indent after `:` - add 4 spaces
                        new_line = ' ' * (prev_leading + 4) + line.lstrip()
                        fixed.append(new_line)
                    else:
                        # Already more indented
                        fixed.append(line)
                else:
                    fixed.append(line)
            else:
                fixed.append(line)
        else:
            # 8+ spaces, assume correct
            fixed.append(line)
    
    with open(filepath, 'w') as f:
        f.writelines(fixed)
    
    print(f"✅ Fixed {filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_indent_fix.py <file1.py> [file2.py ...]")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        fix_file(filepath)
