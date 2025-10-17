#!/usr/bin/env python3
"""
Reduce all font sizes by one Tailwind level (ONE TIME ONLY)
9px stays unchanged!
"""

import os
import re

# Pages to update
PAGES_TO_UPDATE = [
 "frontend/src/pages/AccountBalancePage.jsx",
 "frontend/src/pages/PortfolioDetail.jsx",
 "frontend/src/pages/BuilderPage.jsx",
 "frontend/src/pages/LiveFlowPage.jsx",
 "frontend/src/pages/LiveLitTradesFeed.jsx",
 "frontend/src/pages/LiveOffLitTradesFeed.jsx",
 "frontend/src/pages/InstitutionalPage.jsx",
 "frontend/src/pages/MindfolioList.jsx",
 "frontend/src/pages/PortfoliosList.jsx",
 "frontend/src/pages/PortfolioCreate.jsx",
 "frontend/src/pages/StreamingDashboard.jsx",
 "frontend/src/pages/HomePage.jsx",
 "frontend/src/App.js",
]

def update_file(filepath):
 """Update a single file - replace sizes in ONE PASS"""
 if not os.path.exists(filepath):
 print(f" File not found: {filepath}")
 return False
 
 with open(filepath, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 changes_by_size = {}
 
 # Create unique temporary markers to prevent cascade
 markers = {
 'text-6xl': '___TEMP_5XL___',
 'text-5xl': '___TEMP_4XL___',
 'text-4xl': '___TEMP_3XL___',
 'text-3xl': '___TEMP_2XL___',
 'text-2xl': '___TEMP_XL___',
 'text-xl': '___TEMP_LG___',
 'text-lg': '___TEMP_BASE___',
 'text-base': '___TEMP_SM___',
 }
 
 # Step 1: Replace with temporary markers
 for old_size, marker in markers.items():
 pattern = r'\b' + re.escape(old_size) + r'\b'
 matches = re.findall(pattern, content)
 if matches:
 changes_by_size[old_size] = len(matches)
 content = re.sub(pattern, marker, content)
 
 # Step 2: Replace markers with final values
 final_replacements = {
 '___TEMP_5XL___': 'text-5xl',
 '___TEMP_4XL___': 'text-4xl',
 '___TEMP_3XL___': 'text-3xl',
 '___TEMP_2XL___': 'text-2xl',
 '___TEMP_XL___': 'text-xl',
 '___TEMP_LG___': 'text-lg',
 '___TEMP_BASE___': 'text-base',
 '___TEMP_SM___': 'text-sm',
 }
 
 for marker, final_size in final_replacements.items():
 content = content.replace(marker, final_size)
 
 if content != original_content:
 with open(filepath, 'w', encoding='utf-8') as f:
 f.write(content)
 
 total_changes = sum(changes_by_size.values())
 changes_str = ', '.join([f"{k}→{v}x" for k, v in sorted(changes_by_size.items(), reverse=True)])
 print(f" {filepath}: {total_changes} changes ({changes_str})")
 return True
 else:
 print(f"⚪ {filepath}: no changes needed")
 return False

def main():
 print("🔧 Reducing all font sizes by ONE Tailwind level (no cascade)\n")
 print("📏 Mappings:")
 print(" text-6xl (60px) → text-5xl (48px)")
 print(" text-5xl (48px) → text-4xl (36px)")
 print(" text-4xl (36px) → text-3xl (30px)")
 print(" text-3xl (30px) → text-2xl (24px)")
 print(" text-2xl (24px) → text-xl (20px)")
 print(" text-xl (20px) → text-lg (18px)")
 print(" text-lg (18px) → text-base (16px)")
 print(" text-base (16px) → text-sm (14px)")
 print(f"\n text-[9px] stays unchanged!\n")
 
 updated_files = 0
 
 for page in PAGES_TO_UPDATE:
 if update_file(page):
 updated_files += 1
 
 print(f"\n Updated {updated_files}/{len(PAGES_TO_UPDATE)} files")
 print(f"📏 All sizes reduced by exactly one level")
 print(f" 9px labels remain unchanged")

if __name__ == "__main__":
 main()
