#!/usr/bin/env python3
"""
P(Doom)1 Leaderboard Module Entry Point

This provides the command-line interface requested by the pdoom1-website repository:
    python -m pdoom1.leaderboard export --format web --output ./web_export/

This is a wrapper around the tools.web_export functionality to provide
the exact CLI interface expected by the website integration.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.web_export.export_leaderboards import LeaderboardWebExporter


def main():
    """Main entry point for pdoom1.leaderboard module."""
    parser = argparse.ArgumentParser(description="P(Doom)1 Leaderboard Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export leaderboard data')
    export_parser.add_argument('--format', default='web', choices=['web', 'json'],
                              help='Export format (default: web)')
    export_parser.add_argument('--output', type=Path, default='./web_export/',
                              help='Output directory (default: ./web_export/)')
    export_parser.add_argument('--seed', type=str,
                              help='Export specific seed only')
    export_parser.add_argument('--privacy-filter', action='store_true', default=True,
                              help='Apply privacy filtering (default: True)')
    export_parser.add_argument('--no-privacy-filter', action='store_false', 
                              dest='privacy_filter',
                              help='Disable privacy filtering')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show leaderboard status')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available leaderboards')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'export':
            return handle_export_command(args)
        elif args.command == 'status':
            return handle_status_command(args)
        elif args.command == 'list':
            return handle_list_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1


def handle_export_command(args):
    """Handle the export command."""
    exporter = LeaderboardWebExporter()
    
    if args.seed:
        # Export specific seed
        output_file = args.output / f"leaderboard_{args.seed.replace('/', '_').replace('\\', '_')}.json"
        result = exporter.export_specific_seed(args.seed, output_file, args.privacy_filter)
        
        if result["success"]:
            print(f"Successfully exported seed '{args.seed}' to {result['output_file']}")
            print(f"Exported {result['entry_count']} entries")
            return 0
        else:
            print(f"Failed to export seed '{args.seed}': {result['error']}")
            return 1
    else:
        # Export all leaderboards
        metadata = exporter.export_all_leaderboards(args.output, args.privacy_filter)
        
        print(f"Export completed successfully!")
        print(f"Output directory: {args.output}")
        print(f"Exported {len(metadata['exported_leaderboards'])} leaderboard(s)")
        print(f"Privacy filtering: {'Enabled' if args.privacy_filter else 'Disabled'}")
        
        if metadata["exported_leaderboards"]:
            total_entries = sum(lb["entry_count"] for lb in metadata["exported_leaderboards"])
            print(f"Total entries exported: {total_entries}")
        
        return 0


def handle_status_command(args):
    """Handle the status command."""
    from src.services.leaderboard import is_leaderboard_available
    from src.services.version import get_display_version
    
    exporter = LeaderboardWebExporter()
    all_leaderboards = exporter.enhanced_manager.get_all_leaderboards()
    
    print("P(Doom)1 Leaderboard System Status")
    print("=" * 40)
    print(f"Game Version: {get_display_version()}")
    print(f"Available Leaderboards: {len(all_leaderboards)}")
    print(f"Leaderboard System Available: {is_leaderboard_available()}")
    print(f"Web Export Ready: True")
    
    return 0


def handle_list_command(args):
    """Handle the list command."""
    exporter = LeaderboardWebExporter()
    all_leaderboards = exporter.enhanced_manager.get_all_leaderboards()
    
    print("Available Leaderboards:")
    print("=" * 30)
    
    if all_leaderboards:
        for seed, info in all_leaderboards.items():
            print(f"Seed: {seed}")
            print(f"  Entries: {info['entry_count']}")
            print(f"  Top Score: {info['top_score']}")
            print(f"  Config Hash: {info['config_hash']}")
            print()
    else:
        print("No leaderboards found.")
        print("Play some games to generate leaderboard data.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())