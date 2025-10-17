#!/usr/bin/env python3
"""
Reduce font sizes from 13px to 9px in pages (NOT sidebar)
Preserves sidebar at 13px font-medium
"""

import os
import re

# Pages to update (NOT sidebar components)
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
 "frontend/src/App.js",
]

# Patterns to replace
REPLACEMENTS = [
 # With leading and font-medium
 (r'text-\[13px\] leading-\[20\.8px\] font-medium', 'text-[9px] leading-[14.4px] font-medium'),
 # With leading only
 (r'text-\[13px\] leading-\[20\.8px\]', 'text-[9px] leading-[14.4px]'),
 # Just text size with font-medium
 (r'text-\[13px\] font-medium', 'text-[9px] font-medium'),
]

def update_file(filepath):
 """Update a single file"""
 if not os.path.exists(filepath):
 print(f" File not found: {filepath}")
 return False
 
 with open(filepath, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 changes = 0
 
 for pattern, replacement in REPLACEMENTS:
 matches = re.findall(pattern, content)
 if matches:
 content = re.sub(pattern, replacement, content)
 changes += len(matches)
 
 if content != original_content:
 with open(filepath, 'w', encoding='utf-8') as f:
 f.write(content)
 print(f" {filepath}: {changes} replacements")
 return True
 else:
 print(f"⚪ {filepath}: no changes needed")
 return False

def main():
 print("🔧 Reducing font sizes from 13px → 9px in pages (sidebar stays 13px)\n")
 
 updated_files = 0
 for page in PAGES_TO_UPDATE:
 if update_file(page):
 updated_files += 1
 
 print(f"\n Updated {updated_files}/{len(PAGES_TO_UPDATE)} files")
 print(f"📏 New standard: text-[9px] leading-[14.4px] font-medium")
 print(f" Sidebar remains: text-[13px] leading-[20.8px] font-medium")

if __name__ == "__main__":
 main()
