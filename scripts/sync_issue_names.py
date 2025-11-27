# !/usr/bin/env python3
"""
Sync local issue filenames with GitHub issue numbers.

This script reads .sync_metadata.json and renames local issue files
to include their GitHub issue numbers for easier reference.

Format: {github_id}-{slug}.md
Example: ui-navigation-keyboard-shortcuts.md  ->  422-ui-navigation-keyboard-shortcuts.md
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
ISSUES_DIR = PROJECT_ROOT / "issues"
METADATA_FILE = ISSUES_DIR / ".sync_metadata.json"

def load_metadata() -> Dict:
    """Load sync metadata from file."""
    if not METADATA_FILE.exists():
        print(f"ERROR Metadata file not found: {METADATA_FILE}")
        return {}

    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def get_issue_number_from_filename(filename: str) -> Optional[int]:
    """Extract issue number from filename if it exists."""
    parts = filename.split('-')
    if parts and parts[0].isdigit():
        return int(parts[0])
    return None

def rename_issue_file(old_name: str, github_id: int, dry_run: bool = True) -> bool:
    """Rename an issue file to include GitHub issue number."""
    old_path = ISSUES_DIR / old_name

    if not old_path.exists():
        print(f"  WARNING  File not found: {old_name}")
        return False

    # Check if already has number
    existing_num = get_issue_number_from_filename(old_name)
    if existing_num == github_id:
        print(f"  CHECKED Already has correct number: {old_name}")
        return True

    # Create new filename
    if existing_num:
        # Replace existing number
        parts = old_name.split('-', 1)
        new_name = f"{github_id}-{parts[1]}" if len(parts) > 1 else f"{github_id}-{old_name}"
    else:
        # Add number prefix
        new_name = f"{github_id}-{old_name}"

    new_path = ISSUES_DIR / new_name

    if new_path.exists():
        print(f"  WARNING  Target file already exists: {new_name}")
        return False

    if dry_run:
        print(f"   ->  Would rename: {old_name}  ->  {new_name}")
    else:
        shutil.move(str(old_path), str(new_path))
        print(f"  SUCCESS Renamed: {old_name}  ->  {new_name}")

    return True

def update_metadata(metadata: Dict, dry_run: bool = True) -> None:
    """Update metadata file with new filenames."""
    if dry_run:
        print("\nMEMO Metadata update would be performed (dry run)")
        return

    # Create new metadata with updated keys
    new_metadata = {}
    for old_name, data in metadata.items():
        github_id = data.get("github_id")
        if github_id:
            existing_num = get_issue_number_from_filename(old_name)
            if existing_num == github_id:
                new_metadata[old_name] = data
            else:
                if existing_num:
                    parts = old_name.split('-', 1)
                    new_name = f"{github_id}-{parts[1]}" if len(parts) > 1 else f"{github_id}-{old_name}"
                else:
                    new_name = f"{github_id}-{old_name}"
                new_metadata[new_name] = data
        else:
            new_metadata[old_name] = data

    # Save updated metadata
    with open(METADATA_FILE, 'w') as f:
        json.dump(new_metadata, f, indent=2)

    print("\nSUCCESS Metadata file updated")

def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync local issue filenames with GitHub issue numbers")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--apply", action="store_true", help="Actually perform the renames")
    args = parser.parse_args()

    dry_run = not args.apply

    print("Issue Filename Sync Tool")
    print("=" * 60)
    print()

    if dry_run:
        print("SEARCH DRY RUN MODE - No changes will be made")
    else:
        print("WARNING  APPLY MODE - Files will be renamed!")
    print()

    # Load metadata
    metadata = load_metadata()
    if not metadata:
        return

    print(f"Found {len(metadata)} issues in metadata")
    print()

    # Process each issue
    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for filename, data in metadata.items():
        github_id = data.get("github_id")
        if not github_id:
            print(f"WARNING  No GitHub ID for: {filename}")
            skipped_count += 1
            continue

        print(f"Issue #{github_id}: {filename}")
        result = rename_issue_file(filename, github_id, dry_run)
        if result:
            renamed_count += 1
        else:
            error_count += 1

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Renamed: {renamed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print()

    if not dry_run and renamed_count > 0:
        # Update metadata file
        update_metadata(metadata, dry_run)

    if dry_run:
        print("To apply changes, run with: --apply")

if __name__ == "__main__":
    main()
