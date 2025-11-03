# !/usr/bin/env python3
'''
Web Export Script for P(Doom)1 Leaderboards

This script exports leaderboard data in a format compatible with the pdoom1-website
repository. It bridges the gap between local game leaderboards and global web display.

Usage:
    python export_leaderboards.py
    python export_leaderboards.py --format web --output ./web_export/
    python export_leaderboards.py --seed specific-seed --privacy-filter
'''

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
from src.services.leaderboard import get_leaderboard_manager, is_leaderboard_available
from src.services.version import get_display_version
from tools.web_export.api_format import WebAPIFormatter
from tools.web_export.privacy_filter import PrivacyFilter


class LeaderboardWebExporter:
    '''Export leaderboard data for web consumption.'''
    
    def __init__(self):
        self.enhanced_manager = EnhancedLeaderboardManager()
        self.api_formatter = WebAPIFormatter()
        self.privacy_filter = PrivacyFilter()
        
    def export_all_leaderboards(self, output_dir: Path, privacy_mode: bool = True) -> Dict[str, Any]:
        '''Export all leaderboards in web-compatible format.'''
        output_dir.mkdir(parents=True, exist_ok=True)
        
        export_metadata = {
            'export_timestamp': datetime.now().isoformat(),
            'game_version': get_display_version(),
            'export_tool_version': '1.0.0',
            'privacy_filtered': privacy_mode,
            'exported_leaderboards': []
        }
        
        # Get all available leaderboards
        all_leaderboards = self.enhanced_manager.get_all_leaderboards()
        
        print(f'Found {len(all_leaderboards)} leaderboard(s) to export')
        
        for seed, leaderboard_info in all_leaderboards.items():
            try:
                # Load the specific leaderboard file directly
                from src.scores.local_store import LocalLeaderboard
                from pathlib import Path
                
                leaderboard_file = Path(leaderboard_info['file_path'])
                leaderboard = LocalLeaderboard(leaderboard_file=leaderboard_file)
                
                # Convert to web format
                web_format = self.api_formatter.format_leaderboard_for_web(
                    leaderboard, seed, leaderboard_info['config_hash']
                )
                
                # Apply privacy filtering if requested
                if privacy_mode:
                    web_format = self.privacy_filter.filter_leaderboard_data(web_format)
                
                # Save individual leaderboard file
                seed_filename = f'leaderboard_{seed.replace('/', '_').replace('\\', '_')}.json'
                seed_file = output_dir / seed_filename
                
                with open(seed_file, 'w', encoding='utf-8') as f:
                    json.dump(web_format, f, indent=2, ensure_ascii=False)
                
                export_metadata['exported_leaderboards'].append({
                    'seed': seed,
                    'filename': seed_filename,
                    'entry_count': len(web_format.get('entries', [])),
                    'top_score': web_format.get('entries', [{}])[0].get('score', 0) if web_format.get('entries') else 0
                })
                
                print(f'Exported leaderboard for seed '{seed}': {len(web_format.get('entries', []))} entries')
                
            except Exception as e:
                print(f'Warning: Failed to export leaderboard for seed '{seed}': {e}')
        
        # Create combined leaderboard file (for general website use)
        if export_metadata['exported_leaderboards']:
            combined_data = self._create_combined_leaderboard(all_leaderboards, privacy_mode)
            combined_file = output_dir / 'leaderboard.json'
            
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
                
            print(f'Created combined leaderboard file: leaderboard.json')
        
        # Save export metadata
        metadata_file = output_dir / 'export_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(export_metadata, f, indent=2, ensure_ascii=False)
        
        return export_metadata
    
    def export_specific_seed(self, seed: str, output_file: Path, privacy_mode: bool = True) -> Dict[str, Any]:
        '''Export a specific seed's leaderboard.'''
        try:
            # Get config hash from existing leaderboards
            all_leaderboards = self.enhanced_manager.get_all_leaderboards()
            
            if seed not in all_leaderboards:
                return {
                    'success': False,
                    'seed': seed,
                    'error': f'Seed '{seed}' not found in available leaderboards'
                }
            
            leaderboard_info = all_leaderboards[seed]
            
            # Load the leaderboard file directly
            from src.scores.local_store import LocalLeaderboard
            from pathlib import Path
            
            leaderboard_file = Path(leaderboard_info['file_path'])
            leaderboard = LocalLeaderboard(leaderboard_file=leaderboard_file)
            
            # Convert to web format
            web_format = self.api_formatter.format_leaderboard_for_web(
                leaderboard, seed, leaderboard_info['config_hash']
            )
            
            # Apply privacy filtering if requested
            if privacy_mode:
                web_format = self.privacy_filter.filter_leaderboard_data(web_format)
            
            # Save to file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(web_format, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'seed': seed,
                'entry_count': len(web_format.get('entries', [])),
                'output_file': str(output_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'seed': seed,
                'error': str(e)
            }
    
    def _create_combined_leaderboard(self, all_leaderboards: Dict[str, Dict[str, Any]], privacy_mode: bool) -> Dict[str, Any]:
        '''Create a combined leaderboard from multiple seeds for general display.'''
        # For now, use the leaderboard with the most entries as the primary one
        best_seed = max(all_leaderboards.items(), key=lambda x: x[1]['entry_count'])[0]
        
        leaderboard = self.enhanced_manager.get_leaderboard_for_seed(best_seed)
        config_hash = all_leaderboards[best_seed]['config_hash']
        
        # Convert to web format
        web_format = self.api_formatter.format_leaderboard_for_web(
            leaderboard, best_seed, config_hash
        )
        
        # Apply privacy filtering if requested
        if privacy_mode:
            web_format = self.privacy_filter.filter_leaderboard_data(web_format)
        
        # Add metadata about combined nature
        web_format['meta']['note'] = f'Combined leaderboard (primary seed: {best_seed})'
        web_format['meta']['total_seeds'] = len(all_leaderboards)
        
        return web_format


def main():
    '''CLI interface for leaderboard web export.'''
    parser = argparse.ArgumentParser(description='Export P(Doom)1 leaderboards for web consumption')
    parser.add_argument('--format', default='web', choices=['web', 'json'], 
                       help='Export format (default: web)')
    parser.add_argument('--output', type=Path, default='./web_export',
                       help='Output directory (default: ./web_export)')
    parser.add_argument('--seed', type=str,
                       help='Export specific seed only')
    parser.add_argument('--privacy-filter', action='store_true', default=True,
                       help='Apply privacy filtering (default: True)')
    parser.add_argument('--no-privacy-filter', action='store_false', dest='privacy_filter',
                       help='Disable privacy filtering')
    parser.add_argument('--status', action='store_true',
                       help='Show export status and available leaderboards')
    
    args = parser.parse_args()
    
    # Initialize exporter
    try:
        exporter = LeaderboardWebExporter()
    except Exception as e:
        print(f'Error: Failed to initialize leaderboard exporter: {e}')
        return 1
    
    if args.status:
        # Show status information
        all_leaderboards = exporter.enhanced_manager.get_all_leaderboards()
        
        print('P(Doom)1 Leaderboard Export Status')
        print('=' * 40)
        print(f'Game Version: {get_display_version()}')
        print(f'Available Leaderboards: {len(all_leaderboards)}')
        print(f'Leaderboard System Available: {is_leaderboard_available()}')
        print()
        
        if all_leaderboards:
            print('Available Seeds:')
            for seed, info in all_leaderboards.items():
                print(f'  - {seed}: {info['entry_count']} entries (top score: {info['top_score']})')
        else:
            print('No leaderboards found. Play some games to generate leaderboard data.')
        
        return 0
    
    # Perform export
    try:
        if args.seed:
            # Export specific seed
            output_file = args.output / f'leaderboard_{args.seed.replace('/', '_').replace('\\', '_')}.json'
            result = exporter.export_specific_seed(args.seed, output_file, args.privacy_filter)
            
            if result['success']:
                print(f'Successfully exported seed '{args.seed}' to {result['output_file']}')
                print(f'Exported {result['entry_count']} entries')
            else:
                print(f'Failed to export seed '{args.seed}': {result['error']}')
                return 1
        else:
            # Export all leaderboards
            metadata = exporter.export_all_leaderboards(args.output, args.privacy_filter)
            
            print(f'Export completed successfully!')
            print(f'Output directory: {args.output}')
            print(f'Exported {len(metadata['exported_leaderboards'])} leaderboard(s)')
            print(f'Privacy filtering: {'Enabled' if args.privacy_filter else 'Disabled'}')
            
            if metadata['exported_leaderboards']:
                total_entries = sum(lb['entry_count'] for lb in metadata['exported_leaderboards'])
                print(f'Total entries exported: {total_entries}')
        
        return 0
        
    except Exception as e:
        print(f'Export failed: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())