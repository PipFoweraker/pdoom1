# P(Doom) Content Distribution System

**Status**: Design Phase
**Created**: 2025-11-25
**Purpose**: Automated content publishing to Reddit, Forums, Dashboard, and Website

---

## Overview

A unified system for managing and distributing P(Doom) content across multiple platforms with minimal manual effort. Builds on existing `devblog_automation.py` foundation.

---

## Architecture

### Repository Structure

```
pdoom1/                    # Main game repository
|--- scripts/
|   |--- devblog_automation.py      # Existing (base for expansion)
|   `--- content_publisher.py       # NEW: Multi-platform publisher
|
|--- content/
|   |--- templates/                  # Content templates
|   |   |--- release_announcement.md
|   |   |--- dev_update.md
|   |   |--- weekly_summary.md
|   |   `--- patch_notes.md
|   |
|   |--- scheduled/                  # Content queue
|   |   |--- 2025-11-25_v0.10.5_release.json
|   |   `--- 2025-11-30_weekly_update.json
|   |
|   `--- published/                  # Archive
|       `--- 2025-11_published.json
|
`--- tools/
    `--- content_manager/            # NEW: GUI for content management
        |--- main.py
        |--- preview.py
        `--- scheduler.py

pdoom1-website/            # Website repository
|--- public/
|   |--- blog/                       # Auto-published posts
|   `--- releases/                   # Release feeds
|
`--- scripts/
    `--- sync_content.py             # Pull from main repo

pdoom-dashboard/           # Dashboard repository
|--- data/
|   |--- events/                     # Game events
|   `--- releases/                   # Release data
|
`--- components/
    `--- NewsSection.tsx             # Displays content

content-hub/              # NEW: Central content repo
|--- config/
|   |--- platforms.yaml              # Platform credentials
|   `--- rules.yaml                  # Publishing rules
|
|--- pipelines/
|   |--- reddit_pipeline.py
|   |--- forum_pipeline.py
|   `--- dashboard_pipeline.py
|
`--- ui/
    |--- dashboard.html              # Management UI
    `--- scheduler.html              # Content calendar
```

---

## Platform Integration

### 1. Reddit Integration

**Target**: r/pdoom1, r/gamedev (for major releases)

```python
# scripts/content_publisher.py - Reddit Module

import praw
from datetime import datetime

class RedditPublisher:
    """Publish to Reddit with rate limiting and validation"""

    def __init__(self, credentials_file='config/reddit.json'):
        with open(credentials_file) as f:
            creds = json.load(f)

        self.reddit = praw.Reddit(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            user_agent=creds['user_agent'],
            username=creds['username'],
            password=creds['password']
        )

    def publish_release(self, version: str, notes: str,
                       subreddit='pdoom1', flair='Release'):
        """Publish release announcement to Reddit"""

        # Format title
        title = f"🎮 P(Doom) {version} Released!"

        # Format body with Reddit markdown
        body = self._format_reddit_post(notes)
        body += "\n\n---\n\n"
        body += f"**Download**: [GitHub Releases](https://github.com/PipFoweraker/pdoom1/releases/tag/{version})\n"
        body += f"**Website**: [pdoom1.com](https://pdoom1.com)\n"
        body += f"**Discord**: [Join our community](https://discord.gg/pdoom1)\n"

        # Submit post
        submission = self.reddit.subreddit(subreddit).submit(
            title=title,
            selftext=body,
            flair_text=flair
        )

        return {
            'success': True,
            'url': submission.url,
            'id': submission.id
        }

    def publish_dev_update(self, title: str, content: str):
        """Publish development update"""
        pass

    def _format_reddit_post(self, markdown: str) -> str:
        """Convert standard markdown to Reddit-flavored markdown"""
        # H1 headers -> Bold
        markdown = re.sub(r'^# (.+)$', r'**\1**', markdown, flags=re.MULTILINE)
        # H2 headers -> Bold with line break
        markdown = re.sub(r'^## (.+)$', r'\n**\1**\n', markdown, flags=re.MULTILINE)
        return markdown
```

**Configuration**: `config/reddit.json`
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "user_agent": "PDoom Publisher v1.0",
  "username": "PDoomBot",
  "password": "STORED_IN_ENV"
}
```

---

### 2. Forum Integration

**Target**: LessWrong, EA Forum (for major announcements)

```python
# scripts/content_publisher.py - Forum Module

import requests

class ForumPublisher:
    """Publish to LessWrong/EA Forum via API"""

    def __init__(self, credentials_file='config/forum.json'):
        with open(credentials_file) as f:
            creds = json.load(f)

        self.api_key = creds['api_key']
        self.base_url = creds['base_url']
        self.author_id = creds['author_id']

    def publish_post(self, title: str, content: str,
                    tags: List[str], draft=False):
        """Publish post to LessWrong/EA Forum"""

        payload = {
            'title': title,
            'contents': {
                'originalContents': {
                    'type': 'markdown',
                    'data': content
                }
            },
            'tags': tags,
            'draft': draft,
            'authorId': self.author_id
        }

        response = requests.post(
            f'{self.base_url}/posts',
            json=payload,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )

        if response.status_code == 200:
            post_data = response.json()
            return {
                'success': True,
                'url': post_data['pageUrl'],
                'id': post_data['_id']
            }
        else:
            return {
                'success': False,
                'error': response.text
            }
```

---

### 3. Dashboard Integration

**Target**: pdoom-dashboard (live event feed)

```python
# scripts/content_publisher.py - Dashboard Module

class DashboardPublisher:
    """Publish events to pdoom-dashboard"""

    def __init__(self, dashboard_repo='../pdoom-dashboard'):
        self.repo_path = Path(dashboard_repo)
        self.events_dir = self.repo_path / 'data' / 'events'

    def publish_release_event(self, version: str, date: datetime,
                             changelog: str):
        """Add release event to dashboard timeline"""

        event = {
            'id': f'release-{version}',
            'type': 'release',
            'date': date.isoformat(),
            'title': f'P(Doom) {version} Released',
            'description': self._extract_summary(changelog),
            'link': f'https://github.com/PipFoweraker/pdoom1/releases/tag/{version}',
            'metadata': {
                'version': version,
                'platform': 'all'
            }
        }

        # Save to events file
        events_file = self.events_dir / f'{date.year}.json'
        events = self._load_events(events_file)
        events.append(event)

        with open(events_file, 'w') as f:
            json.dump(events, f, indent=2)

        return {'success': True, 'event_id': event['id']}

    def publish_dev_milestone(self, title: str, description: str):
        """Add development milestone to timeline"""
        pass
```

---

### 4. Website Integration

**Target**: pdoom1-website (blog + news)

```python
# scripts/content_publisher.py - Website Module

class WebsitePublisher:
    """Publish content to pdoom1-website"""

    def __init__(self, website_repo='../pdoom1-website'):
        self.repo_path = Path(website_repo)
        self.blog_dir = self.repo_path / 'public' / 'blog'

    def publish_blog_post(self, title: str, content: str,
                         metadata: Dict):
        """Publish blog post to website"""

        # Generate slug from title
        slug = self._slugify(title)
        date_str = datetime.now().strftime('%Y-%m-%d')

        # Create frontmatter
        frontmatter = f"""---
title: "{title}"
date: {date_str}
author: {metadata.get('author', 'P(Doom) Team')}
tags: {json.dumps(metadata.get('tags', []))}
---

"""

        # Save markdown file
        filepath = self.blog_dir / f'{date_str}-{slug}.md'
        filepath.write_text(frontmatter + content)

        return {
            'success': True,
            'path': str(filepath),
            'url': f'https://pdoom1.com/blog/{date_str}-{slug}'
        }

    def _slugify(self, text: str) -> str:
        """Convert title to URL-safe slug"""
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]
```

---

## Content Manager UI

### GUI Tool for Content Management

```python
# tools/content_manager/main.py

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from pathlib import Path
from datetime import datetime

class ContentManagerUI:
    """Simple GUI for managing content distribution"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("P(Doom) Content Manager")
        self.root.geometry("1200x800")

        self.setup_ui()

    def setup_ui(self):
        """Create UI layout"""

        # Top: Content Type Selector
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill='x')

        ttk.Label(top_frame, text="Content Type:").pack(side='left')
        self.content_type = ttk.Combobox(top_frame, values=[
            'Release Announcement',
            'Dev Update',
            'Weekly Summary',
            'Patch Notes',
            'Community Update'
        ])
        self.content_type.pack(side='left', padx=10)
        self.content_type.bind('<<ComboboxSelected>>', self.load_template)

        # Middle: Content Editor
        editor_frame = ttk.Frame(self.root, padding=10)
        editor_frame.pack(fill='both', expand=True)

        ttk.Label(editor_frame, text="Title:").pack(anchor='w')
        self.title_entry = ttk.Entry(editor_frame, width=80)
        self.title_entry.pack(fill='x', pady=5)

        ttk.Label(editor_frame, text="Content:").pack(anchor='w')
        self.content_text = scrolledtext.ScrolledText(
            editor_frame,
            height=20,
            font=('Consolas', 10)
        )
        self.content_text.pack(fill='both', expand=True, pady=5)

        # Right Sidebar: Platform Checklist
        platform_frame = ttk.LabelFrame(self.root, text="Publish To", padding=10)
        platform_frame.pack(side='right', fill='y', padx=10)

        self.platforms = {
            'reddit': tk.BooleanVar(value=True),
            'forum': tk.BooleanVar(value=False),
            'website': tk.BooleanVar(value=True),
            'dashboard': tk.BooleanVar(value=True),
            'discord': tk.BooleanVar(value=False)
        }

        for platform, var in self.platforms.items():
            ttk.Checkbutton(
                platform_frame,
                text=platform.title(),
                variable=var
            ).pack(anchor='w', pady=2)

        # Bottom: Actions
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill='x')

        ttk.Button(
            action_frame,
            text="Preview",
            command=self.preview_content
        ).pack(side='left', padx=5)

        ttk.Button(
            action_frame,
            text="Schedule",
            command=self.schedule_content
        ).pack(side='left', padx=5)

        ttk.Button(
            action_frame,
            text="Publish Now",
            command=self.publish_content
        ).pack(side='left', padx=5)

        ttk.Button(
            action_frame,
            text="Save Draft",
            command=self.save_draft
        ).pack(side='left', padx=5)

    def load_template(self, event=None):
        """Load template for selected content type"""
        content_type = self.content_type.get()
        template_file = Path(f'content/templates/{content_type.lower().replace(" ", "_")}.md')

        if template_file.exists():
            template = template_file.read_text()
            self.content_text.delete('1.0', 'end')
            self.content_text.insert('1.0', template)

    def preview_content(self):
        """Preview content in all platform formats"""
        # Open preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Content Preview")
        preview_window.geometry("1000x700")

        notebook = ttk.Notebook(preview_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Get content
        title = self.title_entry.get()
        content = self.content_text.get('1.0', 'end')

        # Preview for each platform
        for platform in ['reddit', 'forum', 'website']:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=platform.title())

            preview_text = scrolledtext.ScrolledText(frame, wrap='word')
            preview_text.pack(fill='both', expand=True)

            formatted = self._format_for_platform(title, content, platform)
            preview_text.insert('1.0', formatted)
            preview_text.config(state='disabled')

    def schedule_content(self):
        """Schedule content for future publication"""
        # Open scheduling dialog
        pass

    def publish_content(self):
        """Publish content to selected platforms"""
        title = self.title_entry.get()
        content = self.content_text.get('1.0', 'end')

        # Get selected platforms
        selected = [p for p, var in self.platforms.items() if var.get()]

        # Publish to each platform
        from content_publisher import ContentPublisher
        publisher = ContentPublisher()

        results = publisher.publish_multi(
            title=title,
            content=content,
            platforms=selected
        )

        # Show results
        self._show_results(results)

    def save_draft(self):
        """Save content as draft"""
        pass

    def _format_for_platform(self, title: str, content: str,
                            platform: str) -> str:
        """Format content for specific platform"""
        # Platform-specific formatting logic
        pass

    def run(self):
        """Start the UI"""
        self.root.mainloop()

if __name__ == '__main__':
    app = ContentManagerUI()
    app.run()
```

---

## Unified Publisher

```python
# scripts/content_publisher.py - Main Module

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

class ContentPublisher:
    """Unified publisher for all platforms"""

    def __init__(self, config_dir='config'):
        self.config_dir = Path(config_dir)
        self.reddit = RedditPublisher()
        self.forum = ForumPublisher()
        self.website = WebsitePublisher()
        self.dashboard = DashboardPublisher()

    def publish_release(self, version: str, notes: str,
                       platforms: List[str] = ['all']):
        """Publish release announcement to multiple platforms"""

        if 'all' in platforms:
            platforms = ['reddit', 'website', 'dashboard']

        results = {}

        if 'reddit' in platforms:
            results['reddit'] = self.reddit.publish_release(version, notes)

        if 'website' in platforms:
            results['website'] = self.website.publish_blog_post(
                title=f"P(Doom) {version} Released",
                content=notes,
                metadata={'tags': ['release', version]}
            )

        if 'dashboard' in platforms:
            results['dashboard'] = self.dashboard.publish_release_event(
                version=version,
                date=datetime.now(),
                changelog=notes
            )

        # Log publication
        self._log_publication(version, platforms, results)

        return results

    def publish_multi(self, title: str, content: str,
                     platforms: List[str]) -> Dict:
        """Publish generic content to multiple platforms"""

        results = {}

        for platform in platforms:
            try:
                if platform == 'reddit':
                    results[platform] = self.reddit.publish_dev_update(
                        title, content
                    )
                elif platform == 'forum':
                    results[platform] = self.forum.publish_post(
                        title, content, tags=['pdoom', 'gamedev']
                    )
                elif platform == 'website':
                    results[platform] = self.website.publish_blog_post(
                        title, content, metadata={}
                    )
                elif platform == 'dashboard':
                    results[platform] = self.dashboard.publish_dev_milestone(
                        title, content
                    )

                results[platform]['success'] = True

            except Exception as e:
                results[platform] = {
                    'success': False,
                    'error': str(e)
                }

        return results

    def _log_publication(self, identifier: str, platforms: List[str],
                        results: Dict):
        """Log publication to history"""
        log_file = Path('content/published') / f'{datetime.now().strftime("%Y-%m")}_published.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'identifier': identifier,
            'platforms': platforms,
            'results': results
        }

        if log_file.exists():
            with open(log_file) as f:
                history = json.load(f)
        else:
            history = []

        history.append(log_entry)

        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)
```

---

## Command-Line Interface

```bash
# Publish release announcement
python scripts/content_publisher.py release \
    --version v0.10.5 \
    --notes-file /tmp/release_notes_v0.10.5.md \
    --platforms reddit website dashboard

# Publish dev update
python scripts/content_publisher.py update \
    --title "Music System Complete" \
    --from-commits HEAD~10..HEAD \
    --platforms reddit website

# Schedule weekly summary
python scripts/content_publisher.py schedule \
    --type weekly_summary \
    --date 2025-12-01 \
    --platforms all

# Open GUI
python tools/content_manager/main.py
```

---

## GitHub Actions Integration

```yaml
# .github/workflows/publish-release.yml

name: Publish Release

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Publish to platforms
        env:
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
        run: |
          python scripts/content_publisher.py release \
            --version ${{ github.event.release.tag_name }} \
            --notes-file <(gh release view ${{ github.event.release.tag_name }} --json body -q .body) \
            --platforms reddit website dashboard
```

---

## Repository Decisions

### Option A: Monorepo (Recommended for MVP)
Keep everything in `pdoom1` for now:
- SUCCESS Faster iteration
- SUCCESS Easier to maintain
- SUCCESS Single source of truth
- ERROR Grows large over time

### Option B: Separate Content Hub
Create `pdoom-content-hub` repository:
- SUCCESS Clean separation
- SUCCESS Easier permissions management
- SUCCESS Independent deployment
- ERROR More repos to manage

### Recommendation: Start with Option A, migrate to Option B when:
- You have >5 active publishing pipelines
- Multiple team members need access
- You want platform-specific deployment controls

---

## Next Steps

1. **Week 1: Foundation**
   - Create content publisher CLI
   - Set up Reddit integration
   - Test with v0.10.5 release

2. **Week 2: Multi-Platform**
   - Add website integration
   - Add dashboard integration
   - Create content templates

3. **Week 3: GUI**
   - Build content manager UI
   - Add preview functionality
   - Create scheduling system

4. **Week 4: Automation**
   - GitHub Actions integration
   - Scheduled weekly summaries
   - Analytics dashboard

---

**Status**: Ready for Implementation
**Priority**: High (post-v0.10.5)
**Estimated Effort**: 3-4 weeks
