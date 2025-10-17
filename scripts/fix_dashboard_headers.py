#!/usr/bin/env python3
"""
Fix ALL section headers (h2) in Dashboard to be text-xl font-semibold
"""
import re

dashboard_file = '/workspaces/Flowmind/frontend/src/pages/Dashboard.jsx'

with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all h2 section headers to use text-xl font-semibold
# Pattern: <h2 className="text-[any size]...">
pattern = r'(<h2 className=")text-\[9px\] leading-\[14\.4px\] font-semibold([^"]*")'
replacement = r'\1text-xl font-semibold\2'

new_content = re.sub(pattern, replacement, content)

changes = content.count('text-[9px] leading-[14.4px] font-semibold')

with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Fixed {changes} section headers in Dashboard.jsx")
print(f"   All h2 headers now use: text-xl font-semibold")
