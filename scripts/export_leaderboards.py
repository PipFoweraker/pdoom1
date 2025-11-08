#!/usr/bin/env python3
"""
Export P(Doom)1 Leaderboards for Website Integration

This script exports game leaderboard data to a format compatible with the
pdoom1-website repository.

Usage:
    python scripts/export_leaderboards.py
    python scripts/export_leaderboards.py --seed specific-seed
    python scripts/export_leaderboards.py --output ../pdoom1-website/public/leaderboard/data
    python scripts/export_leaderboards.py --copy-to-website
"""

import argparse
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.scores.enhanced_leaderboard import leaderboard_manager


def main():
    parser = argparse.ArgumentParser(
        description="Export P(Doom)1 leaderboards for website integration"
    )
    parser.add_argument(
        "--output", type=str, help="Output directory for exported files (default: ./web_export)"
    )
    parser.add_argument("--seed", type=str, help="Export only specific seed")
    parser.add_argument(
        "--copy-to-website",
        action="store_true",
        help="Automatically copy exports to ../pdoom1-website/public/leaderboard/data",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed export information")

    args = parser.parse_args()

    # Determine output directory
    if args.copy_to_website:
        website_dir = Path(__file__).parent.parent.parent / "pdoom1-website"
        if not website_dir.exists():
            print(f"ERROR: Website directory not found at {website_dir}")
            print("Clone pdoom1-website repository or specify --output manually")
            sys.exit(1)
        output_dir = website_dir / "public" / "leaderboard" / "data"
    elif args.output:
        output_dir = Path(args.output)
    else:
        output_dir = None  # Use default

    try:
        print("Exporting P(Doom)1 leaderboards...")
        if args.seed:
            print(f"Seed filter: {args.seed}")
        if output_dir:
            print(f"Output directory: {output_dir}")

        # Export leaderboards
        summary = leaderboard_manager.export_for_website(
            output_dir=output_dir, seed_filter=args.seed
        )

        # Display results
        print("\nExport complete!")
        print(f"Seeds exported: {summary['seeds_exported']}")
        print(f"Total entries: {summary['total_entries']}")
        print(f"Generated: {summary['generated']}")
        print(f"Game version: {summary['game_version']}")

        if args.verbose:
            print("\nExported files:")
            for file_info in summary["files"]:
                print(f"   - {file_info['filename']}")
                print(f"     Seed: {file_info['seed']}")
                print(f"     Entries: {file_info['entries_count']}")
                print(f"     Top score: {file_info['top_score']} turns")

        # Show next steps
        print("\nNext steps:")
        if args.copy_to_website:
            print("   1. cd ../pdoom1-website")
            print("   2. View leaderboards: npm run dev (then visit /leaderboard)")
            print("   3. Commit and deploy when ready")
        else:
            output_path = output_dir or Path.cwd() / "web_export"
            print(f"   1. Copy files from {output_path} to pdoom1-website/public/leaderboard/data")
            print("   2. Test in website: npm run dev")
            print("   3. Deploy when ready")

        sys.exit(0)

    except Exception as e:
        print(f"\nERROR: Export failed: {e}")
        import traceback

        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
