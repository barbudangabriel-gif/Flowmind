#!/usr/bin/env python3
"""
Standardize typography across all pages to: text-[13px] leading-[20.8px] font-medium
Preserves large display values (text-3xl, text-4xl, text-5xl, text-6xl)
"""

import re
import os
from pathlib import Path

# Files to process (excluding sidebar components)
FILES_TO_UPDATE = [
 "frontend/src/pages/MindfolioList.jsx",
 "frontend/src/pages/PortfoliosList.jsx",
 "frontend/src/pages/PortfolioDetail.jsx",
 "frontend/src/pages/FlowPage.jsx",
 "frontend/src/pages/LiveFlowPage.jsx",
 "frontend/src/pages/LiveLitTradesFeed.jsx",
 "frontend/src/pages/LiveOffLitTradesFeed.jsx",
 "frontend/src/pages/InstitutionalPage.jsx",
]

# Standard typography
STANDARD = "text-[13px] leading-[20.8px] font-medium"

def update_typography(content):
 """Update text-sm, text-base, text-lg, text-xl, text-2xl to standard"""
 
 # Pattern: text-(sm|base|lg|xl|2xl) but preserve spacing/other classes
 # Also add font-medium if font-normal present
 
 replacements = [
 # text-xl -> text-[13px] leading-[20.8px] font-medium
 (r'\btext-xl\b', 'text-[13px] leading-[20.8px] font-medium'),
 
 # text-lg -> text-[13px] leading-[20.8px] font-medium
 (r'\btext-lg\b', 'text-[13px] leading-[20.8px] font-medium'),
 
 # text-base -> text-[13px] leading-[20.8px] font-medium
 (r'\btext-base\b', 'text-[13px] leading-[20.8px] font-medium'),
 
 # text-sm -> text-[13px] leading-[20.8px] font-medium
 (r'\btext-sm\b', 'text-[13px] leading-[20.8px] font-medium'),
 
 # text-2xl -> text-[13px] leading-[20.8px] font-medium (unless used for headers)
 (r'\btext-2xl\b(?!.*\b(font-normal|text-\[rgb))', 'text-[13px] leading-[20.8px] font-medium'),
 ]
 
 modified = content
 changes_made = 0
 
 for pattern, replacement in replacements:
 new_content, count = re.subn(pattern, replacement, modified)
 if count > 0:
 modified = new_content
 changes_made += count
 
 # Remove redundant font-normal after font-medium
 modified = re.sub(r'font-medium\s+font-normal', 'font-medium', modified)
 modified = re.sub(r'font-normal\s+font-medium', 'font-medium', modified)
 
 # Clean up duplicate font-medium
 modified = re.sub(r'font-medium\s+font-medium', 'font-medium', modified)
 
 return modified, changes_made

def main():
 root = Path("/workspaces/Flowmind")
 total_changes = 0
 
 print(" Standardizing Typography to 13px/20.8px/font-medium\n")
 print("=" * 60)
 
 for file_path in FILES_TO_UPDATE:
 full_path = root / file_path
 
 if not full_path.exists():
 print(f" SKIP: {file_path} (not found)")
 continue
 
 with open(full_path, 'r', encoding='utf-8') as f:
 original = f.read()
 
 updated, changes = update_typography(original)
 
 if changes > 0:
 with open(full_path, 'w', encoding='utf-8') as f:
 f.write(updated)
 print(f" {file_path:50s} → {changes:3d} changes")
 total_changes += changes
 else:
 print(f"⏭️ {file_path:50s} → no changes")
 
 print("=" * 60)
 print(f"\n Total changes: {total_changes}")
 print(f" Files processed: {len(FILES_TO_UPDATE)}")
 print("\n Standard applied: text-[13px] leading-[20.8px] font-medium")
 print(" Preserved: text-3xl, text-4xl, text-5xl, text-6xl (display values)")

if __name__ == "__main__":
 main()
