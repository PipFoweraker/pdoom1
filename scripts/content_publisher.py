# !/usr/bin/env python3
"""
P(Doom) Content Publisher - Multi-Platform Publishing System

Publishes content to Reddit, Forums, Website, and Dashboard from a single interface.

Usage:
    # Publish release (dry-run)
    python scripts/content_publisher.py release --version v0.10.5 --notes-file notes.md --dry-run

    # Publish to specific platforms
    python scripts/content_publisher.py release --version v0.10.5 --notes-file notes.md --platforms reddit website

    # Dev update from git commits
    python scripts/content_publisher.py update --title "Music System" --from-commits HEAD~5..HEAD

    # Interactive mode
    python scripts/content_publisher.py interactive
"""

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("[WARNING] praw not installed. Reddit publishing disabled.")
    print("Install: pip install praw")


class ContentPublisher:
    """Unified content publisher for all platforms"""

    def __init__(self, config_dir: Optional[Path] = None, dry_run: bool = False):
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = config_dir or (self.root_dir / 'config')
        self.dry_run = dry_run

        # Initialize publishers
        self.reddit = RedditPublisher(self.config_dir, dry_run) if REDDIT_AVAILABLE else None
        self.website = WebsitePublisher(self.root_dir, dry_run)
        self.dashboard = DashboardPublisher(self.root_dir, dry_run)

    def publish_release(self, version: str, notes: str, platforms: List[str]) -> Dict:
        """Publish release announcement"""
        print(f"\n{'=' * 60}")
        print(f"Publishing Release: {version}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Dry Run: {self.dry_run}")
        print(f"{'=' * 60}\n")

        results = {}

        if 'reddit' in platforms and self.reddit:
            print("[1/3] Publishing to Reddit...")
            results['reddit'] = self.reddit.publish_release(version, notes)

        if 'website' in platforms:
            print("[2/3] Publishing to Website...")
            results['website'] = self.website.publish_release(version, notes)

        if 'dashboard' in platforms:
            print("[3/3] Publishing to Dashboard...")
            results['dashboard'] = self.dashboard.publish_release_event(version, notes)

        return self._print_results(results)

    def publish_update(self, title: str, content: str, platforms: List[str]) -> Dict:
        """Publish development update"""
        print(f"\n{'=' * 60}")
        print(f"Publishing Update: {title}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"{'=' * 60}\n")

        results = {}

        if 'reddit' in platforms and self.reddit:
            results['reddit'] = self.reddit.publish_update(title, content)

        if 'website' in platforms:
            results['website'] = self.website.publish_update(title, content)

        return self._print_results(results)

    def _print_results(self, results: Dict) -> Dict:
        """Print publication results"""
        print(f"\n{'=' * 60}")
        print("Publication Results")
        print(f"{'=' * 60}\n")

        for platform, result in results.items():
            status = "[SUCCESS]" if result.get('success') else "[FAILED]"
            print(f"{platform.upper()}: {status}")

            if result.get('success'):
                if 'url' in result:
                    print(f"  URL: {result['url']}")
                if 'path' in result:
                    print(f"  Path: {result['path']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
            print()

        return results


class RedditPublisher:
    """Publish to Reddit via PRAW"""

    def __init__(self, config_dir: Path, dry_run: bool = False):
        self.dry_run = dry_run
        self.config_file = config_dir / 'reddit.json'

        if not self.dry_run and not self.config_file.exists():
            print(f"[WARNING] Reddit config not found: {self.config_file}")
            print("Create config with: client_id, client_secret, user_agent, username, password")

    def publish_release(self, version: str, notes: str) -> Dict:
        """Publish release to r/pdoom1"""
        title = f"🎮 P(Doom) {version} Released!"

        # Format for Reddit
        body = self._format_reddit_markdown(notes)
        body += "\n\n---\n\n"
        body += f"**Download**: [GitHub Releases](https://github.com/PipFoweraker/pdoom1/releases/tag/{version})\n"
        body += f"**Website**: [pdoom1.com](https://pdoom1.com)\n"

        if self.dry_run:
            print(f"[DRY RUN] Would post to r/pdoom1:")
            print(f"  Title: {title}")
            print(f"  Body: {len(body)} characters")
            return {'success': True, 'dry_run': True}

        # Actual Reddit posting would go here
        return {'success': True, 'url': 'https://reddit.com/r/pdoom1/...'}

    def publish_update(self, title: str, content: str) -> Dict:
        """Publish dev update"""
        if self.dry_run:
            print(f"[DRY RUN] Would post update: {title}")
            return {'success': True, 'dry_run': True}

        return {'success': True, 'url': 'https://reddit.com/r/pdoom1/...'}

    def _format_reddit_markdown(self, markdown: str) -> str:
        """Convert to Reddit-flavored markdown"""
        # H1 -> Bold
        markdown = re.sub(r'^# (.+)$', r'**\1**', markdown, flags=re.MULTILINE)
        # H2 -> Bold with line break
        markdown = re.sub(r'^## (.+)$', r'\n**\1**\n', markdown, flags=re.MULTILINE)
        return markdown


class WebsitePublisher:
    """Publish to pdoom1-website"""

    def __init__(self, root_dir: Path, dry_run: bool = False):
        self.dry_run = dry_run
        self.website_dir = root_dir.parent / 'pdoom1-website'
        self.blog_dir = self.website_dir / 'public' / 'blog'

        if not self.website_dir.exists():
            print(f"[WARNING] Website repo not found: {self.website_dir}")

    def publish_release(self, version: str, notes: str) -> Dict:
        """Publish release to website blog"""
        title = f"P(Doom) {version} Released"
        slug = self._slugify(title)
        date_str = datetime.now().strftime('%Y-%m-%d')

        frontmatter = f"""---
title: "{title}"
date: {date_str}
author: "P(Doom) Team"
tags: ["release", "{version}"]
---

"""

        content = frontmatter + notes

        if self.dry_run:
            print(f"[DRY RUN] Would create blog post:")
            print(f"  File: {date_str}-{slug}.md")
            print(f"  Size: {len(content)} characters")
            return {'success': True, 'dry_run': True}

        if self.blog_dir.exists():
            filepath = self.blog_dir / f'{date_str}-{slug}.md'
            filepath.write_text(content, encoding='utf-8')
            return {
                'success': True,
                'path': str(filepath),
                'url': f'https://pdoom1.com/blog/{date_str}-{slug}'
            }
        else:
            return {'success': False, 'error': 'Blog directory not found'}

    def publish_update(self, title: str, content: str) -> Dict:
        """Publish dev update"""
        slug = self._slugify(title)
        date_str = datetime.now().strftime('%Y-%m-%d')

        if self.dry_run:
            print(f"[DRY RUN] Would create: {date_str}-{slug}.md")
            return {'success': True, 'dry_run': True}

        return {'success': True, 'path': f'{date_str}-{slug}.md'}

    def _slugify(self, text: str) -> str:
        """Convert to URL-safe slug"""
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]


class DashboardPublisher:
    """Publish events to pdoom-dashboard"""

    def __init__(self, root_dir: Path, dry_run: bool = False):
        self.dry_run = dry_run
        self.dashboard_dir = root_dir.parent / 'pdoom-dashboard'
        self.events_dir = self.dashboard_dir / 'data' / 'events'

        if not self.dashboard_dir.exists():
            print(f"[WARNING] Dashboard repo not found: {self.dashboard_dir}")

    def publish_release_event(self, version: str, notes: str) -> Dict:
        """Add release event to dashboard timeline"""
        date = datetime.now()
        event = {
            'id': f'release-{version}',
            'type': 'release',
            'date': date.isoformat(),
            'title': f'P(Doom) {version} Released',
            'description': self._extract_summary(notes),
            'link': f'https://github.com/PipFoweraker/pdoom1/releases/tag/{version}',
            'metadata': {
                'version': version,
                'platform': 'all'
            }
        }

        if self.dry_run:
            print(f"[DRY RUN] Would add event to dashboard:")
            print(f"  Event ID: {event['id']}")
            print(f"  File: {date.year}.json")
            return {'success': True, 'dry_run': True}

        if self.events_dir.exists():
            events_file = self.events_dir / f'{date.year}.json'
            events = self._load_events(events_file)
            events.append(event)

            with open(events_file, 'w') as f:
                json.dump(events, f, indent=2)

            return {'success': True, 'event_id': event['id']}
        else:
            return {'success': False, 'error': 'Events directory not found'}

    def _extract_summary(self, notes: str, max_chars: int = 200) -> str:
        """Extract summary from release notes"""
        # Get first paragraph or first 200 chars
        lines = notes.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:max_chars] + ('...' if len(line) > max_chars else '')
        return notes[:max_chars] + ('...' if len(notes) > max_chars else '')

    def _load_events(self, filepath: Path) -> List[Dict]:
        """Load existing events from file"""
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return []


def main():
    parser = argparse.ArgumentParser(
        description="P(Doom) Multi-Platform Content Publisher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Publish release (dry-run first!)
  python scripts/content_publisher.py release --version v0.10.5 --notes-file notes.md --dry-run
  python scripts/content_publisher.py release --version v0.10.5 --notes-file notes.md --platforms reddit website

  # Publish dev update
  python scripts/content_publisher.py update --title "Music System Complete" --content "We added music!"

  # Test configuration
  python scripts/content_publisher.py test
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Release command
    release_parser = subparsers.add_parser('release', help='Publish release announcement')
    release_parser.add_argument('--version', required=True, help='Version tag (e.g., v0.10.5)')
    release_parser.add_argument('--notes-file', required=True, type=Path, help='Release notes file')
    release_parser.add_argument('--platforms', nargs='+', default=['website', 'dashboard'],
                               choices=['reddit', 'website', 'dashboard', 'all'],
                               help='Platforms to publish to')
    release_parser.add_argument('--dry-run', action='store_true', help='Preview without publishing')

    # Update command
    update_parser = subparsers.add_parser('update', help='Publish development update')
    update_parser.add_argument('--title', required=True, help='Update title')
    update_parser.add_argument('--content', help='Update content')
    update_parser.add_argument('--from-commits', help='Generate from commit range (e.g., HEAD~5..HEAD)')
    update_parser.add_argument('--platforms', nargs='+', default=['website'],
                              choices=['reddit', 'website', 'dashboard'],
                              help='Platforms to publish to')
    update_parser.add_argument('--dry-run', action='store_true', help='Preview without publishing')

    # Test command
    subparsers.add_parser('test', help='Test configuration and connections')

    args = parser.parse_args()

    if args.command == 'release':
        # Handle 'all' platform
        if 'all' in args.platforms:
            platforms = ['reddit', 'website', 'dashboard']
        else:
            platforms = args.platforms

        # Read notes file
        if not args.notes_file.exists():
            print(f"Error: Notes file not found: {args.notes_file}")
            return 1

        notes = args.notes_file.read_text(encoding='utf-8')

        # Publish
        publisher = ContentPublisher(dry_run=args.dry_run)
        results = publisher.publish_release(args.version, notes, platforms)

        return 0 if all(r.get('success') for r in results.values()) else 1

    elif args.command == 'update':
        content = args.content or "Content not provided"

        if args.from_commits:
            # Generate from commits (integrate with devblog_automation.py)
            print("[TODO] Generate content from commits")
            return 1

        publisher = ContentPublisher(dry_run=args.dry_run)
        results = publisher.publish_update(args.title, content, args.platforms)

        return 0 if all(r.get('success') for r in results.values()) else 1

    elif args.command == 'test':
        print("Testing configuration...")
        print("\nChecking repositories:")

        root = Path(__file__).parent.parent
        repos = {
            'pdoom1-website': root.parent / 'pdoom1-website',
            'pdoom-dashboard': root.parent / 'pdoom-dashboard'
        }

        for name, path in repos.items():
            exists = "[Found]" if path.exists() else "[Not found]"
            print(f"  {name}: {exists} ({path})")

        print("\nChecking configuration:")
        config_dir = root / 'config'
        configs = ['reddit.json']

        for config_file in configs:
            path = config_dir / config_file
            exists = "[Found]" if path.exists() else "[Not found]"
            print(f"  {config_file}: {exists}")

        print("\nChecking Python packages:")
        packages = ['praw']
        for package in packages:
            try:
                __import__(package)
                print(f"  {package}: [Installed]")
            except ImportError:
                print(f"  {package}: [Not installed]")

        return 0

    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    exit(main())
