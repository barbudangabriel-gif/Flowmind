#!/usr/bin/env python3
"""
Display formatted task list from PROJECT_TASKS.md
Used at the start of every Copilot session
"""

import re
from pathlib import Path


def parse_project_tasks():
    """Parse PROJECT_TASKS.md and extract active/backlog tasks"""
    tasks_file = Path(__file__).parent.parent / "PROJECT_TASKS.md"
    
    if not tasks_file.exists():
        print("❌ PROJECT_TASKS.md not found!")
        return
    
    content = tasks_file.read_text()
    
    # Priority emojis mapping
    priority_map = {
        "CRITICAL": "🔴",
        "HIGH": "🟡",
        "MEDIUM": "🟢",
        "LOW": "⚪"
    }
    
    status_map = {
        "Active": "🚀",
        "Backlog": "📋",
        "Completed": "✅",
        "Blocked": "🚫"
    }
    
    # Extract Active Tasks section
    active_match = re.search(
        r'## 🚀 Active Tasks \(In Progress\)\s*\n(.*?)(?=\n## |\Z)',
        content,
        re.DOTALL
    )
    
    # Extract Backlog section
    backlog_match = re.search(
        r'## 📦 Backlog \(Planned\)\s*\n(.*?)(?=\n## |\Z)',
        content,
        re.DOTALL
    )
    
    print("\n" + "="*70)
    print("📋 AVAILABLE TASKS (from PROJECT_TASKS.md)")
    print("="*70 + "\n")
    
    # Parse Active Tasks
    if active_match:
        print("🚀 ACTIVE TASKS (In Progress):")
        print("-" * 70)
        parse_section(active_match.group(1), "Active")
        print()
    
    # Parse Backlog
    if backlog_match:
        print("📋 BACKLOG (Planned):")
        print("-" * 70)
        parse_section(backlog_match.group(1), "Backlog")
        print()
    
    print("="*70)
    print("❓ Which task would you like to work on?")
    print("   Reply with task number or task name")
    print("="*70 + "\n")


def parse_section(section_text, section_type):
    """Parse individual section and extract tasks"""
    # Match task headers like "### 1. 🏦 Task Name (PRIORITY)" or "### 1. Task Name"
    # Emoji are multi-byte UTF-8, so we match any non-ASCII or non-word chars
    task_pattern = r'###\s+(\d+)\.\s+(.+?)\s*(?:\(([A-Z\s]+PRIORITY)\))?\s*$'
    tasks = re.finditer(task_pattern, section_text, re.MULTILINE)
    
    task_list = list(tasks)
    if not task_list:
        print(f"   No tasks found in {section_type}")
        return
    
    for i, task_match in enumerate(task_list):
        task_num = task_match.group(1)
        task_name = task_match.group(2).strip()
        priority_hint = task_match.group(3) if task_match.group(3) else None
        
        # Extract task details (text between this header and next header)
        task_start = task_match.end()
        if i + 1 < len(task_list):
            task_end = task_list[i + 1].start()
        else:
            # Find next section or end
            next_section = re.search(r'\n##\s+', section_text[task_start:])
            task_end = task_start + next_section.start() if next_section else len(section_text)
        
        task_body = section_text[task_start:task_end]
        
        # Extract priority from hint or status line
        priority = "MEDIUM"
        if priority_hint and "CRITICAL" in priority_hint:
            priority = "CRITICAL"
        elif priority_hint and "HIGH" in priority_hint:
            priority = "HIGH"
        else:
            # Check status line for priority
            status_line = re.search(r'\*\*Status:\*\*\s+[^-\n]+-?\s*([^\n]+)', task_body)
            if status_line:
                status_text = status_line.group(1).upper()
                if "CRITICAL" in status_text:
                    priority = "CRITICAL"
                elif "HIGH" in status_text:
                    priority = "HIGH"
        
        priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🟢", "LOW": "⚪"}.get(priority, "⚪")
        
        # Extract time estimate
        due_match = re.search(r'\*\*Due:\*\*\s+([^\n]+)', task_body)
        time_estimate = due_match.group(1).strip() if due_match else "Not specified"
        
        # Extract task file reference
        file_match = re.search(r'\*\*Task File:\*\*\s+`([^`]+)`', task_body)
        task_file = file_match.group(1) if file_match else None
        
        # Extract progress (checkbox count)
        checkboxes = re.findall(r'- \[([ xX])\]', task_body)
        total = len(checkboxes)
        completed = sum(1 for c in checkboxes if c.lower() == 'x')
        progress = f"{completed}/{total} subtasks" if total > 0 else "No subtasks"
        
        # Display task
        print(f"\n{priority_emoji} {priority} - Task #{task_num}")
        print(f"   📌 {task_name}")
        print(f"   ⏱️  Time: {time_estimate}")
        if task_file:
            print(f"   📄 File: {task_file}")
        print(f"   📊 Progress: {progress}")
        
        # Show first few objectives
        objectives = re.findall(r'- \[([ xX])\]\s+\*?\*?([^\n]+?)\*?\*?$', task_body, re.MULTILINE)
        if objectives:
            print(f"   🎯 Next actions:")
            for idx, (status, objective) in enumerate(objectives[:3], 1):
                check = "✅" if status.lower() == "x" else "⬜"
                obj_clean = objective.strip()
                print(f"      {check} {obj_clean[:60]}{'...' if len(obj_clean) > 60 else ''}")
            if len(objectives) > 3:
                print(f"      ... and {len(objectives) - 3} more")


if __name__ == "__main__":
    parse_project_tasks()
