#!/usr/bin/env python3
"""
Fix incorrect 'from backend.' imports in backend code.
When running from /app in Docker, 'backend.' prefix should be removed.
"""
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path):
    """Fix backend imports in a single file"""
    try:
        content = file_path.read_text()
        original = content
        
        # Pattern 1: from backend.agents -> from agents
        content = re.sub(
            r'^from backend\.agents\.',
            'from agents.',
            content,
            flags=re.MULTILINE
        )
        
        # Pattern 2: from backend.redis_fallback -> from redis_fallback
        content = re.sub(
            r'^from backend\.redis_fallback',
            'from redis_fallback',
            content,
            flags=re.MULTILINE
        )
        
        # Pattern 3: from backend.geopolitical_news_agent -> from geopolitical_news_agent
        content = re.sub(
            r'^from backend\.geopolitical_news_agent',
            'from geopolitical_news_agent',
            content,
            flags=re.MULTILINE
        )
        
        # Pattern 4: from backend. (catch-all for any other backend imports)
        content = re.sub(
            r'^from backend\.',
            'from ',
            content,
            flags=re.MULTILINE
        )
        
        if content != original:
            file_path.write_text(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    backend_dir = Path(__file__).parent / "backend"
    
    # Find all Python files in backend/agents
    python_files = list(backend_dir.rglob("*.py"))
    
    fixed_count = 0
    for py_file in python_files:
        if fix_imports_in_file(py_file):
            print(f"✅ Fixed: {py_file.relative_to(backend_dir)}")
            fixed_count += 1
    
    print(f"\n📊 Summary: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
