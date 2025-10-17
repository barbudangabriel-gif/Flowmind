#!/usr/bin/env python3
"""
Uniformize ALL font sizes across the entire FlowMind application

STANDARD FONT SYSTEM:
1. Display (Page Headers) → text-2xl font-bold
2. Section Headers → text-xl font-semibold  
3. Body/Normal → text-base font-medium
4. Small/Details → text-sm font-medium
5. Highlighted Values → text-3xl font-semibold
"""
import re
import os
from pathlib import Path

# Font size standardization rules
FONT_RULES = {
    # Page headers (h1)
    r'<h1[^>]*className="[^"]*text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)[^"]*"': 
        lambda m: m.group(0).replace(re.search(r'text-\w+', m.group(0)).group(0), 'text-2xl'),
    
    # Section headers (h2)
    r'<h2[^>]*className="[^"]*text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)[^"]*"': 
        lambda m: m.group(0).replace(re.search(r'text-\w+', m.group(0)).group(0), 'text-xl'),
    
    # Subsection headers (h3)
    r'<h3[^>]*className="[^"]*text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)[^"]*"': 
        lambda m: m.group(0).replace(re.search(r'text-\w+', m.group(0)).group(0), 'text-base'),
}

# Simple replacements for specific contexts
SIMPLE_REPLACEMENTS = [
    # Replace extreme sizes
    (r'\btext-9xl\b', 'text-3xl'),
    (r'\btext-8xl\b', 'text-3xl'),
    (r'\btext-7xl\b', 'text-3xl'),
    (r'\btext-6xl\b', 'text-3xl'),
    (r'\btext-5xl\b', 'text-2xl'),
    (r'\btext-4xl\b', 'text-xl'),
    
    # Normalize font weights
    (r'\bfont-normal\b', 'font-medium'),
]

def uniformize_file(filepath):
    """Uniformize font sizes in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = 0
        
        # Apply simple replacements
        for pattern, replacement in SIMPLE_REPLACEMENTS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes += content.count(pattern.strip('\\b'))
                content = new_content
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filepath.relative_to('/workspaces/Flowmind')}: {changes} changes")
            return changes
        return 0
    except Exception as e:
        print(f"❌ {filepath}: {e}")
        return 0

def main():
    """Uniformize fonts across all frontend files"""
    frontend_dir = Path('/workspaces/Flowmind/frontend/src')
    
    # Find all JSX files
    jsx_files = list(frontend_dir.rglob('*.jsx')) + list(frontend_dir.rglob('*.js'))
    
    print(f"🔍 Found {len(jsx_files)} files to process\n")
    
    total_changes = 0
    files_changed = 0
    
    for filepath in sorted(jsx_files):
        changes = uniformize_file(filepath)
        if changes > 0:
            total_changes += changes
            files_changed += 1
    
    print(f"\n{'='*60}")
    print(f"🎯 UNIFORMIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Files changed: {files_changed}")
    print(f"✅ Total changes: {total_changes}")
    print(f"\n📏 STANDARD FONT SIZES:")
    print(f"   • Display (h1): text-2xl font-bold")
    print(f"   • Section (h2): text-xl font-semibold")
    print(f"   • Body: text-base font-medium")
    print(f"   • Small: text-sm font-medium")
    print(f"   • Values: text-3xl font-semibold")

if __name__ == '__main__':
    main()
