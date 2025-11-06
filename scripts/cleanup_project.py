#!/usr/bin/env python3
"""
Project Cleanup Automation Script

Automates routine cleanup tasks for the P(Doom) project.
Keeps the repository clean and organized.

Usage:
    python scripts/cleanup_project.py --dry-run          # See what would be cleaned
    python scripts/cleanup_project.py --clean-pyc        # Remove .pyc files
    python scripts/cleanup_project.py --archive-old      # Archive old session notes
    python scripts/cleanup_project.py --all              # Run all cleanup tasks
"""

import argparse
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import hashlib
import json

class ProjectCleaner:
    """Automated project cleanup utility"""

    def __init__(self, root_dir: Path, dry_run: bool = False):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.stats = {
            'pyc_files_removed': 0,
            'pycache_dirs_removed': 0,
            'sessions_archived': 0,
            'bytes_freed': 0
        }

    def log(self, message: str, level: str = "INFO"):
        """Print formatted log message"""
        prefix = "[DRY-RUN]" if self.dry_run else "[CLEANUP]"
        print(f"{prefix} [{level}] {message}")

    def get_file_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0

    def clean_pyc_files(self):
        """Remove all .pyc files and __pycache__ directories"""
        self.log("Cleaning Python cache files...")

        # Find all .pyc files
        pyc_files = list(self.root_dir.rglob('*.pyc'))
        for pyc_file in pyc_files:
            size = self.get_file_size(pyc_file)
            self.log(f"Removing {pyc_file.relative_to(self.root_dir)}", "DEBUG")
            if not self.dry_run:
                pyc_file.unlink()
            self.stats['pyc_files_removed'] += 1
            self.stats['bytes_freed'] += size

        # Find all __pycache__ directories
        pycache_dirs = [d for d in self.root_dir.rglob('__pycache__') if d.is_dir()]
        for pycache_dir in pycache_dirs:
            size = self.get_file_size(pycache_dir)
            self.log(f"Removing {pycache_dir.relative_to(self.root_dir)}", "DEBUG")
            if not self.dry_run:
                shutil.rmtree(pycache_dir)
            self.stats['pycache_dirs_removed'] += 1
            self.stats['bytes_freed'] += size

        self.log(f"Removed {self.stats['pyc_files_removed']} .pyc files and "
                f"{self.stats['pycache_dirs_removed']} __pycache__ directories")

    def clean_cache_dirs(self):
        """Remove Python cache directories"""
        self.log("Cleaning cache directories...")

        cache_patterns = ['.mypy_cache', '.ruff_cache', '.pytest_cache', '.hypothesis']
        for pattern in cache_patterns:
            cache_dirs = [d for d in self.root_dir.rglob(pattern) if d.is_dir()]
            for cache_dir in cache_dirs:
                size = self.get_file_size(cache_dir)
                self.log(f"Removing {cache_dir.relative_to(self.root_dir)}")
                if not self.dry_run:
                    shutil.rmtree(cache_dir)
                self.stats['bytes_freed'] += size

    def archive_old_sessions(self, age_days: int = 180):
        """Archive session notes older than specified days"""
        self.log(f"Archiving session notes older than {age_days} days...")

        sessions_dir = self.root_dir / 'docs' / 'sessions' / '2024-2025'
        if not sessions_dir.exists():
            self.log("Sessions directory not found", "WARNING")
            return

        archive_dir = self.root_dir / 'docs' / 'sessions' / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)

        cutoff_date = datetime.now() - timedelta(days=age_days)

        for session_file in sessions_dir.glob('SESSION_*.md'):
            file_date = datetime.fromtimestamp(session_file.stat().st_mtime)
            if file_date < cutoff_date:
                dest = archive_dir / session_file.name
                self.log(f"Archiving {session_file.name} (age: {(datetime.now() - file_date).days} days)")
                if not self.dry_run:
                    shutil.move(str(session_file), str(dest))
                self.stats['sessions_archived'] += 1

    def find_orphaned_files(self) -> List[Path]:
        """Find potentially orphaned files in root directory"""
        self.log("Scanning for orphaned files...")

        # Files that should definitely be in root
        expected_root_files = {
            'README.md', 'CHANGELOG.md', 'LICENSE', '.gitignore',
            'requirements.txt', 'requirements-dev.txt', 'pyproject.toml',
            'main.py', 'ui.py', 'setup.py', 'GODOT_README.md', 'GODOT_QUICKSTART.md'
        }

        orphaned = []
        for item in self.root_dir.iterdir():
            if item.is_file() and item.name not in expected_root_files:
                # Check if it looks like a temp/test file
                if any(pattern in item.name.lower() for pattern in
                      ['test_', 'temp', 'tmp', 'debug', '.backup', '.old']):
                    orphaned.append(item)
                    self.log(f"Found orphaned file: {item.name}", "WARNING")

        return orphaned

    def detect_duplicates(self) -> List[Tuple[Path, Path]]:
        """Find duplicate files by content hash"""
        self.log("Scanning for duplicate files...")

        hashes = {}
        duplicates = []

        # Only scan specific directories to avoid noise
        scan_dirs = ['src', 'godot/scripts', 'shared', 'tools', 'scripts']

        for scan_dir in scan_dirs:
            dir_path = self.root_dir / scan_dir
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob('*.py'):
                if file_path.stat().st_size < 100:  # Skip tiny files
                    continue

                # Compute hash
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                if file_hash in hashes:
                    duplicates.append((hashes[file_hash], file_path))
                    self.log(f"Duplicate found: {file_path.relative_to(self.root_dir)} == "
                            f"{hashes[file_hash].relative_to(self.root_dir)}", "WARNING")
                else:
                    hashes[file_hash] = file_path

        return duplicates

    def generate_report(self):
        """Generate cleanup report"""
        print("\n" + "="*60)
        print("CLEANUP REPORT")
        print("="*60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL'}")
        print(f"\nStatistics:")
        print(f"  .pyc files removed: {self.stats['pyc_files_removed']}")
        print(f"  __pycache__ dirs removed: {self.stats['pycache_dirs_removed']}")
        print(f"  Session notes archived: {self.stats['sessions_archived']}")
        print(f"  Space freed: {self.stats['bytes_freed'] / 1024 / 1024:.2f} MB")
        print("="*60 + "\n")

    def run_all(self):
        """Run all cleanup tasks"""
        self.log("Running all cleanup tasks...")
        self.clean_pyc_files()
        self.clean_cache_dirs()
        self.find_orphaned_files()
        self.detect_duplicates()
        self.generate_report()

def main():
    parser = argparse.ArgumentParser(description="Project cleanup automation")
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned without making changes')
    parser.add_argument('--clean-pyc', action='store_true',
                       help='Remove .pyc files and __pycache__ directories')
    parser.add_argument('--clean-cache', action='store_true',
                       help='Remove cache directories (.mypy_cache, etc.)')
    parser.add_argument('--archive-old', action='store_true',
                       help='Archive old session notes (>180 days)')
    parser.add_argument('--find-orphans', action='store_true',
                       help='Find orphaned files in root directory')
    parser.add_argument('--find-duplicates', action='store_true',
                       help='Find duplicate files by content')
    parser.add_argument('--all', action='store_true',
                       help='Run all cleanup tasks')

    args = parser.parse_args()

    # Get project root (assuming script is in scripts/ directory)
    root_dir = Path(__file__).parent.parent

    cleaner = ProjectCleaner(root_dir, dry_run=args.dry_run)

    # Run requested tasks
    if args.all:
        cleaner.run_all()
    else:
        if args.clean_pyc:
            cleaner.clean_pyc_files()
        if args.clean_cache:
            cleaner.clean_cache_dirs()
        if args.archive_old:
            cleaner.archive_old_sessions()
        if args.find_orphans:
            cleaner.find_orphaned_files()
        if args.find_duplicates:
            cleaner.detect_duplicates()

        if not any([args.clean_pyc, args.clean_cache, args.archive_old,
                   args.find_orphans, args.find_duplicates]):
            parser.print_help()
        else:
            cleaner.generate_report()

if __name__ == '__main__':
    main()
