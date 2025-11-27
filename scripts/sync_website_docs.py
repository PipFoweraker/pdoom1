# !/usr/bin/env python3
"""
Sync documentation from pdoom1 repo to website export format.

Usage:
    python scripts/sync_website_docs.py [--output DIR]

Exports markdown docs to _website_export/ with website-specific transformations.
"""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class WebsiteDocSyncer:
    """Sync game documentation to website export format."""

    def __init__(self, output_dir: Path = Path("_website_export")):
        self.repo_root = Path(__file__).parent.parent
        self.output_dir = self.repo_root / output_dir
        self.docs_output = self.output_dir / "docs"

    def sync_all(self):
        """Sync all documentation to website format."""
        print("=== P(Doom) Website Documentation Sync ===")
        print(f"Output: {self.output_dir}")
        print()

        # Clean output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.docs_output.mkdir(parents=True, exist_ok=True)

        # Sync different doc types
        self.sync_readme()
        self.sync_user_docs()
        self.sync_developer_docs()
        self.sync_privacy()
        self.sync_changelog()

        # Generate manifest
        self.generate_manifest()

        print()
        print(f"CHECKED Export complete: {self.output_dir}")
        print(f"  Docs: {len(list(self.docs_output.rglob('*.md')))} files")

    def sync_readme(self):
        """Export README as index page."""
        print("Syncing README...")

        source = self.repo_root / "README.md"
        output = self.docs_output / "index.md"

        content = source.read_text(encoding="utf-8")

        # Add front-matter
        front_matter = self._create_front_matter(
            title="P(Doom): AI Safety Strategy Game",
            slug="index",
            category="overview",
            description="A satirical strategy game about managing an AI safety lab"
        )

        # Transform content
        content = self._transform_links(content)
        content = self._transform_images(content)

        output.write_text(front_matter + content, encoding="utf-8")
        print(f"  CHECKED {output.relative_to(self.output_dir)}")

    def sync_user_docs(self):
        """Export user-facing documentation."""
        print("Syncing user guides...")

        user_docs = self.repo_root / "docs" / "user-guide"
        if not user_docs.exists():
            print("  WARNING docs/user-guide/ not found, skipping")
            return

        output_dir = self.docs_output / "guides"
        output_dir.mkdir(exist_ok=True)

        for md_file in user_docs.glob("*.md"):
            self._export_doc(md_file, output_dir, category="guides")

    def sync_developer_docs(self):
        """Export developer documentation."""
        print("Syncing developer docs...")

        dev_docs = self.repo_root / "docs" / "developer"
        if not dev_docs.exists():
            print("  WARNING docs/developer/ not found, skipping")
            return

        output_dir = self.docs_output / "dev"
        output_dir.mkdir(exist_ok=True)

        for md_file in dev_docs.glob("*.md"):
            self._export_doc(md_file, output_dir, category="developer")

    def sync_privacy(self):
        """Export privacy documentation."""
        print("Syncing privacy docs...")

        privacy = self.repo_root / "docs" / "PRIVACY.md"
        if not privacy.exists():
            print("  WARNING docs/PRIVACY.md not found, skipping")
            return

        output = self.docs_output / "privacy.md"
        self._export_doc(privacy, self.docs_output, category="legal", slug="privacy")

    def sync_changelog(self):
        """Export changelog."""
        print("Syncing changelog...")

        changelog = self.repo_root / "CHANGELOG.md"
        if not changelog.exists():
            print("  WARNING CHANGELOG.md not found, skipping")
            return

        output = self.docs_output / "releases.md"
        self._export_doc(changelog, self.docs_output, category="releases", slug="releases")

    def _export_doc(self, source: Path, output_dir: Path, category: str, slug: str = None):
        """Export a single document with transformations."""
        if slug is None:
            slug = source.stem.lower().replace("_", "-")

        output = output_dir / f"{slug}.md"

        content = source.read_text(encoding="utf-8")

        # Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else source.stem.replace("_", " ").title()

        # Add front-matter
        front_matter = self._create_front_matter(
            title=title,
            slug=slug,
            category=category
        )

        # Transform content
        content = self._transform_links(content)
        content = self._transform_images(content)

        output.write_text(front_matter + content, encoding="utf-8")
        print(f"  CHECKED {output.relative_to(self.output_dir)}")

    def _create_front_matter(self, title: str, slug: str, category: str, description: str = None) -> str:
        """Create YAML front-matter for static site generators."""
        fm = [
            "---",
            f"title: \"{title}\"",
            f"slug: \"{slug}\"",
            f"category: \"{category}\"",
            f"updated: \"{datetime.now().strftime('%Y-%m-%d')}\"",
        ]

        if description:
            fm.append(f"description: \"{description}\"")

        fm.append("---")
        fm.append("")

        return "\n".join(fm)

    def _transform_links(self, content: str) -> str:
        """Transform GitHub-relative links to website links."""
        # docs/foo/BAR.md -> /game/foo/bar
        def replace_doc_link(match):
            path = match.group(1)
            # Remove .md extension
            path = path.replace(".md", "")
            # Convert to lowercase
            path = path.lower()
            # Replace underscores with hyphens
            path = path.replace("_", "-")
            # Prepend /game/
            return f"(/game/{path})"

        content = re.sub(r'\(docs/([^)]+)\.md\)', replace_doc_link, content)

        return content

    def _transform_images(self, content: str) -> str:
        """Transform image paths for website."""
        # screenshots/foo.png -> /images/screenshots/foo.png
        def replace_image(match):
            path = match.group(1)
            return f"(/images/{path})"

        content = re.sub(r'\(screenshots/([^)]+)\)', replace_image, content)

        return content

    def generate_manifest(self):
        """Generate manifest of exported docs."""
        print("Generating manifest...")

        manifest = {
            "version": "1.0",
            "updated": datetime.now().isoformat(),
            "files": []
        }

        for md_file in self.docs_output.rglob("*.md"):
            relative = md_file.relative_to(self.docs_output)
            manifest["files"].append(str(relative).replace("\\", "/"))

        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        print(f"  CHECKED {manifest_path.relative_to(self.output_dir)}")


def main():
    parser = argparse.ArgumentParser(description="Sync docs to website export format")
    parser.add_argument("--output", default="_website_export", help="Output directory")

    args = parser.parse_args()

    syncer = WebsiteDocSyncer(output_dir=Path(args.output))
    syncer.sync_all()


if __name__ == "__main__":
    main()
