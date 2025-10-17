#!/usr/bin/env python3
"""
Reduce ALL font sizes in ALL dashboard components to 9px/14.4px/font-medium
"""
import re
import os

# Font size mappings - reduce ALL to 9px
FONT_REPLACEMENTS = [
    (r'text-xs\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-sm\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-base\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-lg\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-2xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-3xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-4xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-5xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-6xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-7xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-8xl\b', 'text-[9px] leading-[14.4px] font-medium'),
    (r'text-9xl\b', 'text-[9px] leading-[14.4px] font-medium'),
]

def reduce_fonts_in_file(filepath):
    """Reduce all font sizes to 9px in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = 0
        
        for pattern, replacement in FONT_REPLACEMENTS:
            content, count = re.subn(pattern, replacement, content)
            changes += count
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filepath}: {changes} replacements")
            return changes
        return 0
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return 0

def main():
    dashboard_components = [
        'frontend/src/pages/Dashboard.jsx',
        'frontend/src/components/dashboard/StatCard.jsx',
        'frontend/src/components/dashboard/TopMindfolios.jsx',
        'frontend/src/components/dashboard/QuickActionButton.jsx',
        'frontend/src/components/dashboard/SignalCard.jsx',
        'frontend/src/components/dashboard/ActiveStrategies.jsx',
        'frontend/src/components/dashboard/FlowSummaryWidget.jsx',
        'frontend/src/components/dashboard/DarkPoolWidget.jsx',
        'frontend/src/components/dashboard/NewsTickerWidget.jsx',
        'frontend/src/components/dashboard/TopScoredStocks.jsx',
        'frontend/src/components/dashboard/SystemHealthWidget.jsx',
        'frontend/src/components/dashboard/AlertsWidget.jsx',
    ]
    
    total_changes = 0
    for component in dashboard_components:
        filepath = os.path.join('/workspaces/Flowmind', component)
        if os.path.exists(filepath):
            changes = reduce_fonts_in_file(filepath)
            total_changes += changes
        else:
            print(f"⚠️  Not found: {component}")
    
    print(f"\n🎯 TOTAL: {total_changes} font size reductions across all dashboard components")

if __name__ == '__main__':
    main()
