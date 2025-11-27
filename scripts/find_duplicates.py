# !/usr/bin/env python3
"""
Duplicate File Detector

Finds duplicate files across the codebase using content hashing.

Usage:
    python scripts/find_duplicates.py --scan
    python scripts/find_duplicates.py --report
    python scripts/find_duplicates.py --ignore-list duplicates_ignore.txt
"""

import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json

class DuplicateDetector:
    """Detect duplicate files by content"""

    def __init__(self, root_dir: Path, min_size: int = 1024):
        self.root_dir = root_dir
        self.min_size = min_size  # Minimum file size to check (bytes)
        self.ignore_patterns = {'__pycache__', '.git', '.godot', '.import', 'node_modules',
                               'venv', 'env', '.mypy_cache', '.pytest_cache'}
        self.ignore_list: Set[str] = set()  # Known intentional duplicates
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)

    def load_ignore_list(self, ignore_file: Path):
        """Load list of files to ignore (intentional duplicates)"""
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                self.ignore_list = {line.strip() for line in f if line.strip()}
            print(f"Loaded {len(self.ignore_list)} files from ignore list")

    def should_scan(self, filepath: Path) -> bool:
        """Check if file should be scanned"""
        # Skip ignored patterns
        if any(pattern in str(filepath) for pattern in self.ignore_patterns):
            return False

        # Skip if in ignore list
        rel_path = str(filepath.relative_to(self.root_dir))
        if rel_path in self.ignore_list:
            return False

        # Skip if too small
        if filepath.stat().st_size < self.min_size:
            return False

        return True

    def compute_hash(self, filepath: Path) -> str:
        """Compute MD5 hash of file content"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def scan_directory(self):
        """Scan directory for duplicate files"""
        print(f"Scanning {self.root_dir} for duplicates...")

        scanned = 0
        for filepath in self.root_dir.rglob('*'):
            if not filepath.is_file():
                continue

            if not self.should_scan(filepath):
                continue

            try:
                file_hash = self.compute_hash(filepath)
                self.file_hashes[file_hash].append(filepath)
                scanned += 1

                if scanned % 100 == 0:
                    print(f"  Scanned {scanned} files...")

            except (PermissionError, OSError) as e:
                print(f"  Warning: Could not read {filepath}: {e}")

        print(f"Scanned {scanned} files")

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Return dictionary of duplicate groups"""
        duplicates = {}
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                duplicates[file_hash] = files
        return duplicates

    def generate_report(self):
        """Generate duplicate files report"""
        duplicates = self.find_duplicates()

        if not duplicates:
            print("\nNo duplicates found!")
            return

        print("\n" + "="*80)
        print("DUPLICATE FILES REPORT")
        print("="*80)

        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        total_wasted_space = 0

        print(f"\nFound {len(duplicates)} groups of duplicates")
        print(f"Total duplicate files: {total_duplicates}")

        print("\n" + "-"*80)
        print("DUPLICATE GROUPS")
        print("-"*80)

        for i, (file_hash, files) in enumerate(sorted(duplicates.items(),
                                                      key=lambda x: x[1][0].stat().st_size,
                                                      reverse=True), 1):
            file_size = files[0].stat().st_size
            wasted = file_size * (len(files) - 1)
            total_wasted_space += wasted

            print(f"\nGroup {i}: {len(files)} copies ({file_size:,} bytes each, "
                  f"{wasted:,} bytes wasted)")
            print(f"  Hash: {file_hash[:16]}...")

            for filepath in sorted(files):
                rel_path = filepath.relative_to(self.root_dir)
                print(f"    - {rel_path}")

        print("\n" + "="*80)
        print(f"Total wasted space: {total_wasted_space:,} bytes "
              f"({total_wasted_space / 1024 / 1024:.2f} MB)")
        print("="*80 + "\n")

    def export_json(self, output_file: Path):
        """Export duplicates as JSON"""
        duplicates = self.find_duplicates()

        data = {
            'root_dir': str(self.root_dir),
            'total_groups': len(duplicates),
            'duplicates': {}
        }

        for file_hash, files in duplicates.items():
            data['duplicates'][file_hash] = [str(f.relative_to(self.root_dir)) for f in files]

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported duplicate report to {output_file}")

    def suggest_consolidation(self):
        """Suggest how to consolidate duplicates"""
        duplicates = self.find_duplicates()

        if not duplicates:
            return

        print("\n" + "-"*80)
        print("CONSOLIDATION SUGGESTIONS")
        print("-"*80)

        for file_hash, files in duplicates.items():
            # Group by directory
            by_dir = defaultdict(list)
            for f in files:
                by_dir[f.parent].append(f)

            # If all in same directory, might be intentional
            if len(by_dir) == 1:
                print(f"\n[SKIP] All copies in same directory:")
                print(f"  {list(by_dir.keys())[0]}")
                continue

            # Suggest keeping the one in the most "canonical" location
            canonical_dirs = ['src', 'godot/scripts', 'shared']
            canonical_file = None

            for dir_name in canonical_dirs:
                for f in files:
                    if dir_name in str(f):
                        canonical_file = f
                        break
                if canonical_file:
                    break

            if not canonical_file:
                canonical_file = files[0]

            print(f"\n[ACTION] Keep: {canonical_file.relative_to(self.root_dir)}")
            print(f"  Remove:")
            for f in files:
                if f != canonical_file:
                    print(f"    - {f.relative_to(self.root_dir)}")

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files")
    parser.add_argument('--scan', action='store_true',
                       help='Scan for duplicates')
    parser.add_argument('--report', action='store_true',
                       help='Generate duplicate report')
    parser.add_argument('--suggest', action='store_true',
                       help='Suggest consolidation actions')
    parser.add_argument('--export-json', metavar='FILE',
                       help='Export as JSON')
    parser.add_argument('--ignore-list', metavar='FILE',
                       help='File containing paths to ignore')
    parser.add_argument('--min-size', type=int, default=1024,
                       help='Minimum file size to check (bytes)')

    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    detector = DuplicateDetector(root_dir, min_size=args.min_size)

    if args.ignore_list:
        detector.load_ignore_list(Path(args.ignore_list))

    if args.scan or args.report or args.suggest:
        detector.scan_directory()

    if args.report:
        detector.generate_report()

    if args.suggest:
        detector.suggest_consolidation()

    if args.export_json:
        detector.scan_directory()
        detector.export_json(Path(args.export_json))

    if not any([args.scan, args.report, args.suggest, args.export_json]):
        parser.print_help()

if __name__ == '__main__':
    main()
