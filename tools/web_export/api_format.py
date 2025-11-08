# !/usr/bin/env python3
'''
API Format Converter for P(Doom)1 Web Integration

Converts internal leaderboard format to website-compatible JSON format
matching the structure expected by the pdoom1-website repository.

Based on the API specification from:
https://github.com/PipFoweraker/pdoom1-website/blob/main/docs/03-integrations/leaderboard-integration-spec.md
'''

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.lib.services.version import get_display_version


class WebAPIFormatter:
    '''Format leaderboard data for web API consumption.'''
    
    def __init__(self):
        self.api_version = '1.0.0'
        
    def format_leaderboard_for_web(self, 
                                  leaderboard, 
                                  seed: str, 
                                  config_hash: str) -> Dict[str, Any]:
        '''
        Convert internal leaderboard to web API format.
        
        Output format matches the specification from pdoom1-website:
        {
            'meta': { ... },
            'seed': '...',
            'economic_model': 'Bootstrap_v0.4.1',
            'entries': [ ... ]
        }
        '''
        
        # Convert entries to web format
        web_entries = []
        for entry in leaderboard.entries:
            web_entry = self._convert_entry_to_web_format(entry)
            web_entries.append(web_entry)
        
        # Create metadata
        metadata = {
            'generated': datetime.now().isoformat() + 'Z',
            'game_version': get_display_version(),
            'total_seeds': 1,  # This will be updated by caller if needed
            'total_players': len(set(entry.player_name for entry in leaderboard.entries)),
            'export_source': 'game-repository',
            'api_version': self.api_version,
            'config_hash': config_hash,
            'note': 'Exported from actual game leaderboard data'
        }
        
        # Determine economic model from entries
        economic_model = 'Bootstrap_v0.4.1'  # Default
        if web_entries and 'game_mode' in web_entries[0]:
            economic_model = web_entries[0]['game_mode']
        
        return {
            'meta': metadata,
            'seed': seed,
            'economic_model': economic_model,
            'entries': web_entries
        }
    
    def _convert_entry_to_web_format(self, entry) -> Dict[str, Any]:
        '''
        Convert a single leaderboard entry to web format.
        
        Maps internal ScoreEntry format to the format expected by pdoom1-website.
        '''
        
        # Handle date formatting - ensure it's always a string
        date_str = datetime.now().isoformat()
        if hasattr(entry, 'date'):
            if isinstance(entry.date, str):
                date_str = entry.date
            elif hasattr(entry.date, 'isoformat'):  # datetime object
                date_str = entry.date.isoformat()
        
        # Base entry data (guaranteed fields)
        web_entry = {
            'score': entry.score,
            'player_name': entry.player_name,
            'date': date_str,
            'level_reached': entry.score,  # In our game, score == turns survived
            'game_mode': getattr(entry, 'game_mode', 'Bootstrap_v0.4.1'),
            'duration_seconds': getattr(entry, 'duration_seconds', 0.0),
            'entry_uuid': str(getattr(entry, 'entry_uuid', ''))
        }
        
        # Add additional metrics if available
        if hasattr(entry, 'final_money'):
            web_entry['final_money'] = entry.final_money
        else:
            web_entry['final_money'] = 100000  # Default starting amount
            
        if hasattr(entry, 'final_staff'):
            web_entry['final_staff'] = entry.final_staff
        else:
            web_entry['final_staff'] = 5  # Default starting staff
            
        if hasattr(entry, 'final_reputation'):
            web_entry['final_reputation'] = entry.final_reputation
        else:
            web_entry['final_reputation'] = 50.0  # Default starting reputation
            
        if hasattr(entry, 'final_doom'):
            web_entry['final_doom'] = entry.final_doom
        else:
            web_entry['final_doom'] = 25.0  # Default doom level
            
        if hasattr(entry, 'final_compute'):
            web_entry['final_compute'] = entry.final_compute
        else:
            web_entry['final_compute'] = 10000  # Default compute
            
        # Additional metrics that might be available
        optional_fields = [
            'research_papers_published',
            'technical_debt_accumulated',
            'total_research_spending',
            'total_fundraising_gained',
            'milestone_progress',
            'safety_measures_implemented'
        ]
        
        for field in optional_fields:
            if hasattr(entry, field):
                web_entry[field] = getattr(entry, field)
            else:
                # Provide sensible defaults
                if field == 'research_papers_published':
                    web_entry[field] = 0
                elif field == 'technical_debt_accumulated':
                    web_entry[field] = 0
        
        return web_entry
    
    def format_combined_leaderboards(self, leaderboards_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        '''
        Format multiple leaderboards into a combined structure.
        
        This creates the format suitable for global leaderboard display
        across multiple seeds/game modes.
        '''
        
        all_entries = []
        total_players = set()
        all_seeds = set()
        
        for leaderboard in leaderboards_data:
            entries = leaderboard.get('entries', [])
            all_entries.extend(entries)
            
            # Track unique players and seeds
            for entry in entries:
                total_players.add(entry.get('player_name', ''))
            all_seeds.add(leaderboard.get('seed', ''))
        
        # Sort by score (highest first)
        all_entries.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Create combined metadata
        metadata = {
            'generated': datetime.now().isoformat() + 'Z',
            'game_version': get_display_version(),
            'total_seeds': len(all_seeds),
            'total_players': len(total_players),
            'export_source': 'game-repository-combined',
            'api_version': self.api_version,
            'note': 'Combined leaderboard from multiple seeds'
        }
        
        return {
            'meta': metadata,
            'seed': 'combined',
            'economic_model': 'Bootstrap_v0.4.1',
            'entries': all_entries,
            'source_seeds': list(all_seeds)
        }
    
    def create_api_status_response(self, leaderboards_count: int) -> Dict[str, Any]:
        '''Create an API status response for health checks.'''
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat() + 'Z',
            'data': {
                'export_system': 'operational',
                'available_leaderboards': leaderboards_count,
                'game_version': get_display_version(),
                'api_version': self.api_version,
                'export_features': [
                    'individual_seed_export',
                    'combined_leaderboard_export', 
                    'privacy_filtering',
                    'web_api_format'
                ]
            }
        }
    
    def validate_web_format(self, web_data: Dict[str, Any]) -> Dict[str, bool]:
        '''
        Validate that exported data matches expected web format.
        
        Returns validation results for debugging export issues.
        '''
        validation = {
            'has_meta': 'meta' in web_data,
            'has_entries': 'entries' in web_data,
            'has_seed': 'seed' in web_data,
            'has_economic_model': 'economic_model' in web_data,
            'meta_has_required_fields': False,
            'entries_have_required_fields': False
        }
        
        # Check meta fields
        if validation['has_meta']:
            meta = web_data['meta']
            required_meta_fields = ['generated', 'game_version', 'total_players']
            validation['meta_has_required_fields'] = all(
                field in meta for field in required_meta_fields
            )
        
        # Check entry format
        if validation['has_entries'] and web_data['entries']:
            first_entry = web_data['entries'][0]
            required_entry_fields = ['score', 'player_name', 'date', 'level_reached']
            validation['entries_have_required_fields'] = all(
                field in first_entry for field in required_entry_fields
            )
        
        return validation


def test_web_format():
    '''Test the web format conversion with sample data.'''
    print('Testing Web API Format Converter...')
    
    # This would normally come from actual leaderboard data
    class MockEntry:
        def __init__(self):
            self.score = 42
            self.player_name = 'Test Lab'
            self.date = '2025-10-09T12:00:00'
            self.game_mode = 'Bootstrap_v0.4.1'
            self.duration_seconds = 120.5
            self.entry_uuid = 'test-uuid-123'
            self.final_money = 150000
            self.final_staff = 8
            self.final_reputation = 75.0
            self.final_doom = 30.0
            self.final_compute = 15000
    
    class MockLeaderboard:
        def __init__(self):
            self.entries = [MockEntry()]
    
    formatter = WebAPIFormatter()
    mock_leaderboard = MockLeaderboard()
    
    result = formatter.format_leaderboard_for_web(
        mock_leaderboard, 'test-seed', 'abc123'
    )
    
    print('Formatted result:')
    print(json.dumps(result, indent=2))
    
    validation = formatter.validate_web_format(result)
    print('\nValidation results:')
    for check, passed in validation.items():
        status = 'PASS' if passed else 'FAIL'
        print(f'  {check}: {status}')


if __name__ == '__main__':
    test_web_format()