#!/usr/bin/env python3
"""
Script pentru schimbarea fontului în SidebarNav demo
"""

import os
import re

def change_sidebar_font():
 """Schimbă fontul în sidebar-ul din demo"""
 demo_file = "/workspaces/Flowmind/sidebar-nav-demo.html"
 
 if not os.path.exists(demo_file):
 print(f" Fișierul {demo_file} nu există!")
 return
 
 # Citește conținutul fișierului
 with open(demo_file, 'r', encoding='utf-8') as f:
 content = f.read()
 
 print(" Schimb fontul în sidebar...")
 
 # Înlocuiește fontul în .sidebar
 old_pattern = r'(\.sidebar\s*{[^}]*font-family:\s*)[^;]+;'
 new_font = r"\1'Arial Black', 'Impact', sans-serif;"
 
 content = re.sub(old_pattern, new_font, content, flags=re.DOTALL)
 
 # Adaugă și font-size mai mare pentru sidebar
 sidebar_pattern = r'(\.sidebar\s*{[^}]*)(})'
 def add_font_size(match):
 existing = match.group(1)
 if 'font-size:' not in existing:
 return existing + '\n font-size: 16px;\n }'
 return match.group(0)
 
 content = re.sub(sidebar_pattern, add_font_size, content, flags=re.DOTALL)
 
 # Schimbă și fontul pentru nav-item-uri să fie și mai vizibil
 nav_item_pattern = r'(\.nav-item\s*{[^}]*font-size:\s*)\d+px;'
 content = re.sub(nav_item_pattern, r'\g<1>15px;', content)
 
 # Scrie fișierul modificat
 with open(demo_file, 'w', encoding='utf-8') as f:
 f.write(content)
 
 print(" Fontul a fost schimbat în sidebar!")
 print("📄 Fișier actualizat:", demo_file)
 print(" Font nou: Arial Black, Impact (bold și mare)")
 print("📏 Font size: 16px pentru sidebar, 15px pentru nav items")

if __name__ == "__main__":
 change_sidebar_font()