#!/usr/bin/env python3
"""
Remove ALL emojis from pages - STRICT POLICY ENFORCEMENT
NO icons unless explicitly requested by user
"""

import os
import re

# Pages to clean
PAGES_TO_CLEAN = [
 "frontend/src/pages/AccountBalancePage.jsx",
 "frontend/src/pages/PortfolioDetail.jsx",
 "frontend/src/pages/MindfolioList.jsx",
 "frontend/src/pages/PortfoliosList.jsx",
 "frontend/src/pages/InstitutionalPage.jsx",
 "frontend/src/pages/FlowPage.jsx",
 "frontend/src/pages/PortfolioCreate.jsx",
]

# Specific emoji patterns to remove (with their containers)
EMOJI_REMOVALS = [
 # Icon spans in stat cards
 (r'<span className="[^"]*text-[^"]*">[🔌]</span>\s*', ''),
 
 # Standalone emoji divs
 (r'<div className="[^"]*">[🔌]</div>\s*', ''),
 
 # Emoji in text content
 (r'[🔌]\s*', ''),
 
 # Tab icons in arrays
 (r"icon:\s*'[🔌]'", "icon: ''"),
 
 # Option text with emoji
 (r'[🔌]\s+([A-Z][a-z\s]+)', r'\1'),
]

def remove_emojis_from_file(filepath):
 """Remove all emojis from a file"""
 if not os.path.exists(filepath):
 print(f" File not found: {filepath}")
 return False
 
 with open(filepath, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 emoji_count = 0
 
 # Count emojis before removal
 emoji_chars = '🔌'
 for char in emoji_chars:
 emoji_count += content.count(char)
 
 if emoji_count == 0:
 print(f"⚪ {filepath}: no emojis found")
 return False
 
 # Apply all removal patterns
 for pattern, replacement in EMOJI_REMOVALS:
 content = re.sub(pattern, replacement, content)
 
 # Final cleanup: remove any remaining emoji characters
 for char in emoji_chars:
 content = content.replace(char, '')
 
 # Clean up any double spaces or empty lines created
 content = re.sub(r' {2,}', ' ', content)
 content = re.sub(r'\n{3,}', '\n\n', content)
 
 if content != original_content:
 with open(filepath, 'w', encoding='utf-8') as f:
 f.write(content)
 print(f" {filepath}: {emoji_count} emojis removed")
 return True
 else:
 print(f"⚪ {filepath}: no changes after processing")
 return False

def main():
 print("🚫 STRICT POLICY ENFORCEMENT: Removing ALL emojis\n")
 print("📜 Policy: NO icons/emojis unless explicitly requested\n")
 
 cleaned_files = 0
 total_emojis = 0
 
 for page in PAGES_TO_CLEAN:
 if remove_emojis_from_file(page):
 cleaned_files += 1
 
 print(f"\n Cleaned {cleaned_files}/{len(PAGES_TO_CLEAN)} files")
 print(f"🚫 All emojis removed - strict compliance achieved")

if __name__ == "__main__":
 main()
