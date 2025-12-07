# !/usr/bin/env python3
"""
Dev Blog Automation System with Metadata

Automatically generates development blog entries from git commits
with structured metadata for categorization and searching.

Usage:
    python scripts/devblog_automation.py --from-commits HEAD~5..HEAD
    python scripts/devblog_automation.py --add-entry
    python scripts/devblog_automation.py --weekly-summary
    python scripts/devblog_automation.py --export
"""

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import sys

class DevBlogEntry:
    """Represents a single dev blog entry with metadata"""

    def __init__(self, title: str, date: datetime, categories: List[str],
                 issues: List[int], contributors: List[str], content: str):
        self.title = title
        self.date = date
        self.categories = categories
        self.issues = issues
        self.contributors = contributors
        self.content = content

    def to_markdown(self) -> str:
        """Convert to markdown format with YAML frontmatter"""
        frontmatter = f"""---
title: {self.title}
date: {self.date.strftime('%Y-%m-%d')}
categories: {json.dumps(self.categories)}
issues: {json.dumps(self.issues)}
contributors: {json.dumps(self.contributors)}
---

"""
        return frontmatter + self.content

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            'title': self.title,
            'date': self.date.isoformat(),
            'categories': self.categories,
            'issues': self.issues,
            'contributors': self.contributors,
            'content': self.content
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DevBlogEntry':
        """Create from dictionary"""
        return cls(
            title=data['title'],
            date=datetime.fromisoformat(data['date']),
            categories=data['categories'],
            issues=data['issues'],
            contributors=data['contributors'],
            content=data['content']
        )

class DevBlogAutomation:
    """Automated dev blog management"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.entries_dir = root_dir / 'docs' / 'devblog' / 'entries'
        self.index_file = root_dir / 'docs' / 'devblog' / 'index.json'

        # Ensure directories exist
        self.entries_dir.mkdir(parents=True, exist_ok=True)

    def extract_issue_numbers(self, text: str) -> List[int]:
        """Extract issue numbers from text (e.g., #123, #456)"""
        matches = re.findall(r'#(\d+)', text)
        return [int(m) for m in matches]

    def categorize_commit(self, message: str, files_changed: List[str]) -> List[str]:
        """Auto-categorize commit based on message and files"""
        categories = []

        # Check commit message
        message_lower = message.lower()

        if any(word in message_lower for word in ['feat', 'feature', 'add', 'implement']):
            categories.append('feature')
        if any(word in message_lower for word in ['fix', 'bug', 'resolve']):
            categories.append('bugfix')
        if any(word in message_lower for word in ['refactor', 'cleanup', 'restructure']):
            categories.append('refactor')
        if any(word in message_lower for word in ['docs', 'documentation']):
            categories.append('docs')
        if any(word in message_lower for word in ['test', 'testing']):
            categories.append('test')
        if any(word in message_lower for word in ['ui', 'ux', 'interface']):
            categories.append('ui-ux')
        if any(word in message_lower for word in ['chore', 'maintenance']):
            categories.append('chore')

        # Check files changed
        for file in files_changed:
            if 'test' in file:
                if 'test' not in categories:
                    categories.append('test')
            if 'docs/' in file or '.md' in file:
                if 'docs' not in categories:
                    categories.append('docs')
            if 'godot/' in file:
                if 'godot' not in categories:
                    categories.append('godot')

        return categories if categories else ['other']

    def get_git_commits(self, commit_range: str) -> List[Dict]:
        """Get commits from git with details"""
        try:
            # Get commit info
            result = subprocess.run(
                ['git', 'log', commit_range, '--format=%H|%an|%ae|%s|%b', '--name-only'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            current_commit = None

            for line in result.stdout.split('\n'):
                if '|' in line and len(line.split('|')) == 5:
                    # Commit header line
                    if current_commit:
                        commits.append(current_commit)

                    hash, author, email, subject, body = line.split('|')
                    current_commit = {
                        'hash': hash,
                        'author': author,
                        'email': email,
                        'subject': subject,
                        'body': body,
                        'files': []
                    }
                elif line.strip() and current_commit:
                    # File changed
                    current_commit['files'].append(line.strip())

            if current_commit:
                commits.append(current_commit)

            return commits

        except subprocess.CalledProcessError as e:
            print(f"Error getting git commits: {e}")
            return []

    def generate_entry_from_commits(self, commit_range: str) -> Optional[DevBlogEntry]:
        """Generate dev blog entry from git commits"""
        commits = self.get_git_commits(commit_range)
        if not commits:
            print("No commits found in range")
            return None

        # Aggregate data
        all_categories = set()
        all_issues = set()
        all_contributors = set()
        content_sections = {}

        for commit in commits:
            # Extract metadata
            categories = self.categorize_commit(commit['subject'] + ' ' + commit['body'],
                                              commit['files'])
            issues = self.extract_issue_numbers(commit['subject'] + ' ' + commit['body'])

            all_categories.update(categories)
            all_issues.update(issues)
            all_contributors.add(commit['author'])

            # Group by category
            for category in categories:
                if category not in content_sections:
                    content_sections[category] = []
                content_sections[category].append(f"- {commit['subject']}")

        # Build content
        content = ""
        category_names = {
            'feature': '## Features',
            'bugfix': '## Bug Fixes',
            'refactor': '## Refactoring',
            'ui-ux': '## UI/UX Improvements',
            'docs': '## Documentation',
            'test': '## Testing',
            'godot': '## Godot Port',
            'chore': '## Maintenance',
            'other': '## Other'
        }

        for category in sorted(content_sections.keys()):
            content += f"\n{category_names.get(category, f'## {category.title()}')}\n\n"
            content += '\n'.join(content_sections[category])
            content += "\n"

        # Create entry
        title = f"Development Update - {datetime.now().strftime('%B %d, %Y')}"
        entry = DevBlogEntry(
            title=title,
            date=datetime.now(),
            categories=sorted(list(all_categories)),
            issues=sorted(list(all_issues)),
            contributors=sorted(list(all_contributors)),
            content=content.strip()
        )

        return entry

    def save_entry(self, entry: DevBlogEntry):
        """Save entry to file and update index"""
        # Generate filename
        date_str = entry.date.strftime('%Y-%m-%d')
        title_slug = re.sub(r'[^\w\s-]', '', entry.title.lower())
        title_slug = re.sub(r'[-\s]+', '-', title_slug)[:50]
        filename = f"{date_str}-{title_slug}.md"

        # Save markdown file
        filepath = self.entries_dir / filename
        filepath.write_text(entry.to_markdown())
        print(f"Saved entry: {filename}")

        # Update index
        self.update_index(entry, filename)

    def update_index(self, entry: DevBlogEntry, filename: str):
        """Update the index.json file"""
        # Load existing index
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {'entries': []}

        # Add new entry
        entry_data = entry.to_dict()
        entry_data['filename'] = filename
        index['entries'].insert(0, entry_data)  # Newest first

        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"Updated index: {len(index['entries'])} total entries")

    def generate_weekly_summary(self):
        """Generate summary of past week's entries"""
        print("Generating weekly summary...")

        week_ago = datetime.now() - timedelta(days=7)

        if not self.index_file.exists():
            print("No index file found")
            return

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        recent_entries = []
        for entry_data in index['entries']:
            entry_date = datetime.fromisoformat(entry_data['date'])
            if entry_date >= week_ago:
                recent_entries.append(entry_data)

        if not recent_entries:
            print("No entries in past week")
            return

        print(f"\nWeek in Review ({week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}):")
        print("=" * 60)

        all_categories = set()
        all_issues = set()
        all_contributors = set()

        for entry in recent_entries:
            print(f"\n{entry['title']} ({entry['date']})")
            all_categories.update(entry['categories'])
            all_issues.update(entry['issues'])
            all_contributors.update(entry['contributors'])

        print(f"\nSummary:")
        print(f"  Entries: {len(recent_entries)}")
        print(f"  Categories: {', '.join(sorted(all_categories))}")
        print(f"  Issues addressed: {len(all_issues)}")
        print(f"  Contributors: {', '.join(sorted(all_contributors))}")

    def export_for_publishing(self, output_file: Optional[Path] = None):
        """Export entries in publishable format"""
        if output_file is None:
            output_file = self.root_dir / 'docs' / 'devblog' / 'BLOG.md'

        if not self.index_file.exists():
            print("No index file found")
            return

        with open(self.index_file, 'r') as f:
            index = json.load(f)

        # Build combined blog
        content = "# P(Doom) Development Blog\n\n"
        content += "Automated development updates and progress tracking.\n\n"
        content += "---\n\n"

        for entry_data in index['entries']:
            entry_file = self.entries_dir / entry_data['filename']
            if entry_file.exists():
                content += entry_file.read_text() + "\n\n---\n\n"

        output_file.write_text(content)
        print(f"Exported blog to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Dev blog automation")
    parser.add_argument('--from-commits', metavar='RANGE',
                       help='Generate entry from commit range (e.g., HEAD~5..HEAD)')
    parser.add_argument('--add-entry', action='store_true',
                       help='Manually add entry (opens editor)')
    parser.add_argument('--weekly-summary', action='store_true',
                       help='Generate weekly summary')
    parser.add_argument('--export', action='store_true',
                       help='Export all entries for publishing')

    args = parser.parse_args()

    # Get project root
    root_dir = Path(__file__).parent.parent
    automation = DevBlogAutomation(root_dir)

    if args.from_commits:
        entry = automation.generate_entry_from_commits(args.from_commits)
        if entry:
            automation.save_entry(entry)
            print("\nGenerated entry:")
            print(entry.to_markdown())
    elif args.weekly_summary:
        automation.generate_weekly_summary()
    elif args.export:
        automation.export_for_publishing()
    elif args.add_entry:
        print("Manual entry creation not yet implemented")
        print("Use --from-commits to generate from git commits")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
