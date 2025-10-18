#!/usr/bin/env python3
import ast, os, sys

def smart_fix_file(path):
    """
    Fix indentation by detecting expected indent level from AST errors.
    """
    with open(path, 'r') as f:
        lines = f.readlines()
    
    max_attempts = 50
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        code = ''.join(lines)
        
        try:
            ast.parse(code, filename=path)
            # Success!
            with open(path, 'w') as f:
                f.writelines(lines)
            print(f"✅ FIXED {path} (after {attempt} iterations)")
            return True
        except IndentationError as e:
            line_no = e.lineno - 1  # 0-indexed
            if line_no < 0 or line_no >= len(lines):
                break
            
            # Găsește linia anterioară cu cod (nu comment/blank)
            prev_indent = 0
            for i in range(line_no - 1, -1, -1):
                stripped = lines[i].strip()
                if stripped and not stripped.startswith('#'):
                    prev_indent = len(lines[i]) - len(lines[i].lstrip(' '))
                    break
            
            # Dacă linia anterioară se termină cu ':', adaugă +4
            if lines[line_no - 1].rstrip().endswith(':'):
                desired_indent = prev_indent + 4
            else:
                desired_indent = prev_indent
            
            # Aplică indent-ul
            current_line = lines[line_no]
            current_indent = len(current_line) - len(current_line.lstrip(' '))
            
            if current_indent < desired_indent:
                # Adaugă indent
                lines[line_no] = ' ' * desired_indent + current_line.lstrip(' ')
            elif current_indent > desired_indent:
                # Reduce indent
                lines[line_no] = ' ' * desired_indent + current_line.lstrip(' ')
        
        except SyntaxError as e:
            # Try same fix
            line_no = e.lineno - 1
            if line_no < 0 or line_no >= len(lines):
                break
            
            # Adaugă 4 spații
            current_line = lines[line_no]
            current_indent = len(current_line) - len(current_line.lstrip(' '))
            lines[line_no] = ' ' * (current_indent + 4) + current_line.lstrip(' ')
        
        except Exception as e:
            print(f"❌ FAILED {path}: {e}")
            return False
    
    print(f"❌ TIMEOUT {path} (exceeded {max_attempts} attempts)")
    return False

def main():
    failed = []
    for root, dirs, files in os.walk('backend/services'):
        if '__pycache__' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                if not smart_fix_file(path):
                    failed.append(path)
    
    if failed:
        print(f"\n⚠️  Failed to fix {len(failed)} files:")
        for p in failed:
            print(f"  - {p}")
    else:
        print("\n🎉 All files fixed successfully!")

if __name__ == '__main__':
    main()
