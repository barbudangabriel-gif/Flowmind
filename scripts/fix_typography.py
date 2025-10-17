#!/usr/bin/env python3
"""
Script pentru standardizarea tipografiei în FlowMind
Aplică fontul Inter pe toate fișierele CSS, JS, JSX, TSX
"""

import os
import re
from pathlib import Path

# Configurație
INTER_FONT_STACK = 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial'
BASE_TEXT_COLOR = 'rgb(252, 251, 255)' # #FCFBFF
MENU_TYPOGRAPHY = {
 'font_size': '13px',
 'line_height': '20.8px', 
 'font_weight': '400'
}

# Extensii de fișiere de procesat
FILE_EXTENSIONS = ['.css', '.scss', '.js', '.jsx', '.ts', '.tsx', '.html']

def find_files_to_process(root_dir):
 """Găsește toate fișierele care trebuie procesate"""
 files = []
 for ext in FILE_EXTENSIONS:
 files.extend(Path(root_dir).rglob(f'*{ext}'))
 
 # Exclude node_modules, build, dist, .git
 exclude_dirs = {'node_modules', 'build', 'dist', '.git', '__pycache__', '.pytest_cache'}
 filtered_files = []
 
 for file_path in files:
 if not any(part in exclude_dirs for part in file_path.parts):
 filtered_files.append(file_path)
 
 return filtered_files

def fix_font_family_css(content):
 """Înlocuiește font-family în CSS"""
 patterns = [
 # font-family: Arial, sans-serif;
 r'font-family\s*:\s*[^;]+;',
 # fontFamily: 'Arial'
 r'fontFamily\s*:\s*["\'][^"\']+["\']',
 # font: 400 14px Arial
 r'font\s*:\s*(\d+(?:px)?(?:\s+\w+)?)\s+[^;,}]+([;,}])',
 ]
 
 new_content = content
 
 # Înlocuiește font-family declarații
 new_content = re.sub(
 r'font-family\s*:\s*[^;]+;',
 f'font-family: {INTER_FONT_STACK};',
 new_content
 )
 
 # Înlocuiește fontFamily în JS/JSX
 new_content = re.sub(
 r'fontFamily\s*:\s*["\'][^"\']+["\']',
 f'fontFamily: "{INTER_FONT_STACK}"',
 new_content
 )
 
 return new_content

def fix_menu_typography_css(content):
 """Aplică tipografia standard pentru menu items"""
 # Caută clase care par să fie pentru menu
 menu_selectors = [
 r'\.menu-item\s*{[^}]*}',
 r'\.nav-item\s*{[^}]*}',
 r'\.sidebar.*item\s*{[^}]*}',
 r'\[class\*="menu"\]\s*{[^}]*}',
 r'\[class\*="nav"\]\s*{[^}]*}'
 ]
 
 new_content = content
 
 # Adaugă CSS global pentru menu typography dacă nu există
 if 'menu-typography-standard' not in content:
 standard_css = f"""
/* FlowMind Menu Typography Standard */
.menu-typography-standard {{
 font-family: {INTER_FONT_STACK};
 font-size: {MENU_TYPOGRAPHY['font_size']};
 line-height: {MENU_TYPOGRAPHY['line_height']};
 font-weight: {MENU_TYPOGRAPHY['font_weight']};
 color: {BASE_TEXT_COLOR};
 display: flex;
 align-items: center;
 white-space: nowrap;
}}
"""
 new_content = standard_css + new_content
 
 return new_content

def fix_tailwind_classes(content):
 """Înlocuiește clasele Tailwind cu fontul standard"""
 # font-sans -> font-inter (presupunând că avem font-inter configurat)
 new_content = re.sub(r'\bfont-sans\b', 'font-inter', content)
 
 # text-white -> text-[rgb(252,251,255)]
 new_content = re.sub(r'\btext-white\b', f'text-[{BASE_TEXT_COLOR}]', new_content)
 
 return new_content

def process_file(file_path):
 """Procesează un singur fișier"""
 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 
 # Aplică fix-urile
 content = fix_font_family_css(content)
 
 if file_path.suffix in ['.css', '.scss']:
 content = fix_menu_typography_css(content)
 
 if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
 content = fix_tailwind_classes(content)
 
 # Scrie fișierul doar dacă s-a schimbat
 if content != original_content:
 with open(file_path, 'w', encoding='utf-8') as f:
 f.write(content)
 return True
 
 return False
 
 except Exception as e:
 print(f"Eroare la procesarea {file_path}: {e}")
 return False

def main():
 """Funcția principală"""
 print(" FlowMind Typography Standardization")
 print("=" * 50)
 
 # Găsește directorul root
 root_dir = Path(__file__).parent.parent
 print(f"📂 Procesez directorul: {root_dir}")
 
 # Găsește fișierele
 files = find_files_to_process(root_dir)
 print(f"📄 Găsite {len(files)} fișiere pentru procesare")
 
 # Procesează fișierele
 processed_count = 0
 for file_path in files:
 if process_file(file_path):
 print(f" {file_path.relative_to(root_dir)}")
 processed_count += 1
 else:
 print(f"⏭️ {file_path.relative_to(root_dir)} (fără modificări)")
 
 print("\n" + "=" * 50)
 print(f"✨ Procesare completă: {processed_count}/{len(files)} fișiere modificate")
 
 # Afișează rezumatul
 print(f"\n Standard aplicat:")
 print(f" Font: {INTER_FONT_STACK}")
 print(f" Menu: {MENU_TYPOGRAPHY['font_size']}/{MENU_TYPOGRAPHY['line_height']}/{MENU_TYPOGRAPHY['font_weight']}")
 print(f" Color: {BASE_TEXT_COLOR}")

if __name__ == "__main__":
 main()