# !/usr/bin/env python3
"""
Archive Completed Issues Script

Moves completed/resolved local issue files from issues/ to docs/issues/archive/
to prepare for clean issue sync with GitHub.

This prevents creating duplicate GitHub issues for work that's already done.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def archive_completed_issues():
    """Archive issues that have been confirmed as completed."""
    
    # Issues confirmed as completed based on commit history analysis
    completed_issues = [
        'action-points-counting-bug.md',           # Fixed in commit 045acf8
        'action-points-system-validation.md',     # Fixed in multiple commits  
        'fundraising-mechanics-bug.md',           # Fixed in commit 045acf8
        'ascii-compliance-cleanup.md',            # Multiple ASCII cleanup commits
        'uiinteractionissuesbuttonclicksandspacebarnotworkingconsistently.md', # Fixed
        'critical-game-state-syntax-errors.md',   # Fixed in Unicode commits
        'sound-system-default-configuration.md',  # Audio system completed
        'live-session-activity-log-repositioning.md', # Activity log fixes done
        'live-session-verbose-activity-logging.md',   # Activity log fixes done
        'programmatic-game-control-system.md',    # Recently implemented (#384)
        'investigatecriticalgameplaybugs.md',     # Issue #382 was closed
    ]
    
    issues_dir = Path('issues')
    archive_dir = Path('docs/issues/archive')
    
    # Ensure archive directory exists
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Load sync metadata to update it
    metadata_file = issues_dir / '.sync_metadata.json'
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    archived_count = 0
    
    print("Archiving Completed Issues")
    print("=" * 40)
    
    for issue_file in completed_issues:
        source_path = issues_dir / issue_file
        dest_path = archive_dir / issue_file
        
        if source_path.exists():
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            print(f"CHECKED Archived: {issue_file}")
            
            # Remove from sync metadata
            if issue_file in metadata:
                del metadata[issue_file]
                print(f"  `-- Removed from sync metadata")
            
            archived_count += 1
        else:
            print(f"WARNING Not found: {issue_file}")
    
    # Update sync metadata
    if metadata_file.exists():
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"\nCHECKED Updated sync metadata")
    
    # Create archive index
    archive_index = archive_dir / 'README.md'
    with open(archive_index, 'w') as f:
        f.write(f"""# Archived Issues

This directory contains issues that have been completed/resolved and archived on {datetime.now().strftime('%Y-%m-%d')}.

These issues were moved here to prevent duplicate GitHub issue creation during issue sync.

## Archived Issues ({archived_count} files)

""")
        for issue_file in completed_issues:
            if (archive_dir / issue_file).exists():
                f.write(f"- [{issue_file}](./{issue_file})\n")
    
    print(f"\nCELEBRATION Archive Complete!")
    print(f"   Archived: {archived_count} issues")
    print(f"   Location: {archive_dir}")
    print(f"   Index: {archive_index}")
    
    return archived_count

if __name__ == '__main__':
    archive_completed_issues()