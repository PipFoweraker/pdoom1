# !/usr/bin/env python3
'''
Privacy Filter for P(Doom)1 Web Export

Applies privacy controls and filtering to leaderboard data before web export.
Ensures compliance with user privacy settings and data protection principles.

Features:
- Anonymous/pseudonymous player names
- Optional data field filtering
- Compliance with privacy manager settings
- Configurable anonymization levels
'''

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PrivacyFilter:
    '''Filter and anonymize leaderboard data for web export.'''
    
    def __init__(self):
        self.anonymization_level = 'standard'  # 'none', 'standard', 'strict'
        self.preserved_fields = {
            'score', 'date', 'level_reached', 'game_mode', 'duration_seconds'
        }
        self.sensitive_fields = {
            'final_money', 'final_staff', 'final_reputation', 'final_compute',
            'research_papers_published', 'technical_debt_accumulated'
        }
        
        # Lab name pools for anonymization
        self.lab_name_pool = [
            'Apex Intelligence', 'Quantum Leap', 'Neural Dynamics', 'Zenith Dynamics',
            'Infinitas Research', 'Synergy Labs', 'Vanguard AI', 'Prometheus Research',
            'Atlas Computing', 'Nexus Intelligence', 'Catalyst Labs', 'Meridian AI',
            'Phoenix Research', 'Orion Labs', 'Titan Intelligence', 'Vector Dynamics',
            'Echo Labs', 'Pulse Research', 'Nova Intelligence', 'Prime Dynamics'
        ]
    
    def filter_leaderboard_data(self, leaderboard_data: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Apply privacy filtering to complete leaderboard data.
        
        Args:
            leaderboard_data: Raw leaderboard data in web format
            
        Returns:
            Privacy-filtered leaderboard data
        '''
        filtered_data = leaderboard_data.copy()
        
        # Filter entries
        if 'entries' in filtered_data:
            filtered_entries = []
            for entry in filtered_data['entries']:
                filtered_entry = self._filter_entry(entry)
                if filtered_entry:  # None means entry was filtered out completely
                    filtered_entries.append(filtered_entry)
            
            filtered_data['entries'] = filtered_entries
        
        # Add privacy notice to metadata
        if 'meta' in filtered_data:
            filtered_data['meta']['privacy_filtered'] = True
            filtered_data['meta']['anonymization_level'] = self.anonymization_level
            filtered_data['meta']['privacy_notice'] = (
                'Player names have been anonymized to protect user privacy. '
                'Scores and game metrics are preserved for competitive integrity.'
            )
        
        return filtered_data
    
    def _filter_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        '''
        Filter a single leaderboard entry.
        
        Args:
            entry: Single leaderboard entry
            
        Returns:
            Filtered entry or None if entry should be excluded
        '''
        if self.anonymization_level == 'none':
            return entry
        
        filtered_entry = {}
        
        # Always preserve core competitive data
        for field in self.preserved_fields:
            if field in entry:
                filtered_entry[field] = entry[field]
        
        # Handle player name anonymization
        if 'player_name' in entry:
            filtered_entry['player_name'] = self._anonymize_player_name(
                entry['player_name'], entry.get('entry_uuid', '')
            )
        
        # Handle sensitive fields based on anonymization level
        if self.anonymization_level == 'standard':
            # Include aggregated/rounded sensitive data
            for field in self.sensitive_fields:
                if field in entry:
                    filtered_entry[field] = self._anonymize_sensitive_value(
                        field, entry[field]
                    )
        elif self.anonymization_level == 'strict':
            # Exclude all sensitive fields
            pass
        
        # Always include entry UUID for deduplication (but possibly hashed)
        if 'entry_uuid' in entry:
            if self.anonymization_level == 'strict':
                # Hash the UUID to prevent tracking while preserving uniqueness
                filtered_entry['entry_uuid'] = self._hash_uuid(entry['entry_uuid'])
            else:
                filtered_entry['entry_uuid'] = entry['entry_uuid']
        
        return filtered_entry
    
    def _anonymize_player_name(self, original_name: str, entry_uuid: str) -> str:
        '''
        Generate a consistent anonymous name for a player.
        
        Uses deterministic generation based on entry UUID to ensure
        the same player gets the same anonymous name across exports.
        '''
        if self.anonymization_level == 'none':
            return original_name
        
        # Use entry UUID to deterministically select lab name
        if entry_uuid:
            hash_obj = hashlib.md5(entry_uuid.encode())
            name_index = int.from_bytes(hash_obj.digest()[:4], 'big') % len(self.lab_name_pool)
        else:
            # Fallback to hash of original name
            hash_obj = hashlib.md5(original_name.encode())
            name_index = int.from_bytes(hash_obj.digest()[:4], 'big') % len(self.lab_name_pool)
        
        return self.lab_name_pool[name_index]
    
    def _anonymize_sensitive_value(self, field_name: str, value: Any) -> Any:
        '''
        Anonymize sensitive numerical values while preserving competitive utility.
        
        Different fields get different anonymization strategies.
        '''
        if not isinstance(value, (int, float)):
            return value
        
        if field_name in {'final_money', 'final_compute'}:
            # Round large values to nearest 1000
            return round(value / 1000) * 1000
        elif field_name in {'final_staff'}:
            # Round staff to nearest 5
            return round(value / 5) * 5
        elif field_name in {'final_reputation', 'final_doom'}:
            # Round percentages to nearest 5%
            return round(value / 5) * 5
        elif field_name in {'research_papers_published', 'technical_debt_accumulated'}:
            # Keep exact counts for these competitive metrics
            return value
        else:
            # Default: round to nearest 10
            return round(value / 10) * 10
    
    def _hash_uuid(self, uuid_str: str) -> str:
        '''Generate a privacy-preserving hash of a UUID.'''
        return hashlib.sha256(uuid_str.encode()).hexdigest()[:16]
    
    def set_anonymization_level(self, level: str) -> bool:
        '''
        Set the anonymization level.
        
        Args:
            level: 'none', 'standard', or 'strict'
            
        Returns:
            True if level was valid and set, False otherwise
        '''
        valid_levels = {'none', 'standard', 'strict'}
        if level in valid_levels:
            self.anonymization_level = level
            return True
        return False
    
    def get_privacy_summary(self) -> Dict[str, Any]:
        '''Get a summary of current privacy settings.'''
        return {
            'anonymization_level': self.anonymization_level,
            'preserved_fields': list(self.preserved_fields),
            'sensitive_fields': list(self.sensitive_fields),
            'anonymization_features': {
                'player_name_anonymization': self.anonymization_level != 'none',
                'sensitive_data_rounding': self.anonymization_level == 'standard',
                'sensitive_data_exclusion': self.anonymization_level == 'strict',
                'uuid_hashing': self.anonymization_level == 'strict'
            }
        }
    
    def create_privacy_manifest(self, output_file: Path) -> None:
        '''Create a privacy manifest file explaining what data was filtered.'''
        manifest = {
            'privacy_manifest_version': '1.0.0',
            'created': datetime.now().isoformat(),
            'privacy_policy': {
                'data_minimization': 'Only competitive game metrics are exported',
                'anonymization': 'Player names are replaced with anonymous lab names',
                'data_retention': 'No personal identifying information is retained',
                'purpose_limitation': 'Data is used only for competitive leaderboards'
            },
            'technical_details': self.get_privacy_summary(),
            'contact_info': {
                'privacy_questions': 'See game privacy settings for user controls',
                'data_subject_rights': 'Users can disable leaderboard participation entirely'
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)


def test_privacy_filter():
    '''Test the privacy filter with sample data.'''
    print('Testing Privacy Filter...')
    
    # Sample leaderboard data
    sample_data = {
        'meta': {
            'generated': '2025-10-09T12:00:00Z',
            'game_version': 'v0.9.1',
            'total_players': 1
        },
        'seed': 'test-seed',
        'economic_model': 'Bootstrap_v0.4.1',
        'entries': [
            {
                'score': 42,
                'player_name': 'RealPlayerName',
                'date': '2025-10-09T12:00:00',
                'level_reached': 42,
                'game_mode': 'Bootstrap_v0.4.1',
                'duration_seconds': 120.5,
                'entry_uuid': '12345678-1234-1234-1234-123456789012',
                'final_money': 156789,
                'final_staff': 13,
                'final_reputation': 73.2,
                'final_doom': 28.7,
                'final_compute': 18432,
                'research_papers_published': 3
            }
        ]
    }
    
    filter_obj = PrivacyFilter()
    
    # Test different anonymization levels
    for level in ['none', 'standard', 'strict']:
        print(f'\n--- Testing {level} anonymization ---')
        filter_obj.set_anonymization_level(level)
        filtered = filter_obj.filter_leaderboard_data(sample_data)
        
        entry = filtered['entries'][0]
        print(f'Player name: {entry.get('player_name', 'N/A')}')
        print(f'Final money: {entry.get('final_money', 'N/A')}')
        print(f'Entry UUID: {entry.get('entry_uuid', 'N/A')}')
        print(f'Fields count: {len(entry)}')
    
    # Test privacy summary
    print(f'\n--- Privacy Summary ---')
    summary = filter_obj.get_privacy_summary()
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    test_privacy_filter()