#!/usr/bin/env python3
"""
TODO/FIXME/HACK Tracker

Scans codebase for TODO/FIXME/HACK comments and organizes them by priority.

Usage:
    python scripts/todo_tracker.py --scan
    python scripts/todo_tracker.py --report
    python scripts/todo_tracker.py --create-issues
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class TodoItem:
    """Represents a TODO/FIXME/HACK comment"""
    type: str  # TODO, FIXME, HACK, NOTE
    file: Path
    line: int
    text: str
    context: str  # Function/class name if available
    priority: str  # high, medium, low

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'file': str(self.file),
            'line': self.line,
            'text': self.text,
            'context': self.context,
            'priority': self.priority
        }

class TodoTracker:
    """TODO comment scanner and tracker"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.todos: List[TodoItem] = []

        # Priority keywords
        self.high_priority_keywords = ['critical', 'urgent', 'asap', 'security', 'bug']
        self.low_priority_keywords = ['nice', 'maybe', 'consider', 'optional']

    def determine_priority(self, text: str) -> str:
        """Determine priority from TODO text"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in self.high_priority_keywords):
            return 'high'
        elif any(keyword in text_lower for keyword in self.low_priority_keywords):
            return 'low'
        else:
            return 'medium'

    def scan_file(self, filepath: Path):
        """Scan a single file for TODO comments"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_context = "global"

            for i, line in enumerate(lines, 1):
                # Track context (function/class)
                if re.match(r'^(class|def|func)\s+(\w+)', line):
                    match = re.match(r'^(class|def|func)\s+(\w+)', line)
                    if match:
                        current_context = match.group(2)

                # Find TODO-style comments
                todo_pattern = r'#\s*(TODO|FIXME|HACK|NOTE|XXX|BUG)[:,\s]+(.*)'
                match = re.search(todo_pattern, line, re.IGNORECASE)

                if match:
                    todo_type = match.group(1).upper()
                    todo_text = match.group(2).strip()

                    priority = self.determine_priority(todo_text)

                    todo = TodoItem(
                        type=todo_type,
                        file=filepath.relative_to(self.root_dir),
                        line=i,
                        text=todo_text,
                        context=current_context,
                        priority=priority
                    )
                    self.todos.append(todo)

        except (UnicodeDecodeError, PermissionError):
            # Skip files that can't be read
            pass

    def scan_directory(self, extensions: List[str] = None):
        """Scan entire directory for TODOs"""
        if extensions is None:
            extensions = ['.py', '.gd', '.gdscript', '.md']

        print(f"Scanning {self.root_dir} for TODO comments...")

        # Scan Python files
        for ext in extensions:
            for filepath in self.root_dir.rglob(f'*{ext}'):
                # Skip virtual environments and build directories
                if any(skip in str(filepath) for skip in ['venv', 'env', '__pycache__',
                                                          '.git', 'node_modules']):
                    continue
                self.scan_file(filepath)

        print(f"Found {len(self.todos)} TODO items")

    def generate_report(self):
        """Generate formatted report of TODOs"""
        if not self.todos:
            print("No TODOs found")
            return

        # Group by priority
        by_priority = defaultdict(list)
        for todo in self.todos:
            by_priority[todo.priority].append(todo)

        # Group by type
        by_type = defaultdict(list)
        for todo in self.todos:
            by_type[todo.type].append(todo)

        print("\n" + "="*80)
        print("TODO TRACKER REPORT")
        print("="*80)

        print(f"\nTotal: {len(self.todos)} items")
        print(f"  High Priority: {len(by_priority['high'])}")
        print(f"  Medium Priority: {len(by_priority['medium'])}")
        print(f"  Low Priority: {len(by_priority['low'])}")

        print(f"\nBy Type:")
        for todo_type, items in sorted(by_type.items()):
            print(f"  {todo_type}: {len(items)}")

        # Show high priority items
        print("\n" + "-"*80)
        print("HIGH PRIORITY ITEMS")
        print("-"*80)

        for todo in sorted(by_priority['high'], key=lambda x: str(x.file)):
            print(f"\n[{todo.type}] {todo.file}:{todo.line}")
            print(f"  Context: {todo.context}")
            print(f"  {todo.text[:100]}...")

        # Show files with most TODOs
        print("\n" + "-"*80)
        print("FILES WITH MOST TODOs")
        print("-"*80)

        file_counts = defaultdict(int)
        for todo in self.todos:
            file_counts[todo.file] += 1

        for file, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {count:3d} - {file}")

        print("\n" + "="*80 + "\n")

    def export_json(self, output_file: Path):
        """Export TODOs as JSON"""
        data = {
            'generated': str(Path.cwd()),
            'total_todos': len(self.todos),
            'todos': [todo.to_dict() for todo in self.todos]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported {len(self.todos)} TODOs to {output_file}")

    def export_markdown(self, output_file: Path):
        """Export TODOs as Markdown"""
        if not self.todos:
            return

        # Group by priority
        by_priority = defaultdict(list)
        for todo in self.todos:
            by_priority[todo.priority].append(todo)

        content = "# TODO Tracker Report\n\n"
        content += f"Generated: {Path.cwd()}\n\n"
        content += f"Total: {len(self.todos)} items\n\n"

        for priority in ['high', 'medium', 'low']:
            items = by_priority[priority]
            if not items:
                continue

            content += f"## {priority.upper()} Priority ({len(items)} items)\n\n"

            for todo in sorted(items, key=lambda x: str(x.file)):
                content += f"### [{todo.type}] `{todo.file}:{todo.line}`\n\n"
                content += f"**Context:** `{todo.context}`\n\n"
                content += f"{todo.text}\n\n"
                content += "---\n\n"

        output_file.write_text(content)
        print(f"Exported markdown report to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="TODO/FIXME tracker")
    parser.add_argument('--scan', action='store_true',
                       help='Scan codebase for TODOs')
    parser.add_argument('--report', action='store_true',
                       help='Generate TODO report')
    parser.add_argument('--export-json', metavar='FILE',
                       help='Export TODOs as JSON')
    parser.add_argument('--export-md', metavar='FILE',
                       help='Export TODOs as Markdown')

    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    tracker = TodoTracker(root_dir)

    if args.scan or args.report:
        tracker.scan_directory()

    if args.report:
        tracker.generate_report()

    if args.export_json:
        tracker.scan_directory()
        tracker.export_json(Path(args.export_json))

    if args.export_md:
        tracker.scan_directory()
        tracker.export_markdown(Path(args.export_md))

    if not any([args.scan, args.report, args.export_json, args.export_md]):
        parser.print_help()

if __name__ == '__main__':
    main()
