'''
Privacy-Respecting Leaderboard Foundation for P(Doom)

Provides infrastructure for competitive leaderboards while maintaining user privacy.
Uses pseudonymous identifiers and opt-in submission system.
'''

import json
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SubmissionStatus(Enum):
    '''Status of leaderboard submission.'''
    PENDING = 'pending'
    SUBMITTED = 'submitted'
    VERIFIED = 'verified'
    REJECTED = 'rejected'


@dataclass
class LeaderboardEntry:
    '''Privacy-respecting leaderboard entry.'''
    pseudonym: str                    # Player-chosen pseudonym
    seed: str                        # Weekly/challenge seed
    score: int                       # Turns survived
    game_checksum: str              # Verification checksum
    submission_time: str            # When submitted
    game_metadata: Dict[str, Any]   # Version, config, etc.
    verification_data: Dict[str, Any]  # For anti-cheat verification
    status: SubmissionStatus = SubmissionStatus.PENDING
    
    
@dataclass
class WeeklyChallenge:
    '''Weekly challenge configuration.'''
    week_id: str                    # e.g., '2025-W36'
    seed: str                       # Challenge seed
    config_name: str               # Game configuration to use
    start_date: str                # Challenge start
    end_date: str                  # Challenge end
    description: str               # Challenge description
    special_rules: Dict[str, Any]  # Any special modifiers
    

class PrivacyManager:
    '''Manages user privacy settings and pseudonym generation.'''
    
    def __init__(self):
        self.privacy_file = 'user_privacy.json'
        self.settings = self._load_privacy_settings()
    
    def _load_privacy_settings(self) -> Dict[str, Any]:
        '''Load user privacy settings.'''
        try:
            if os.path.exists(self.privacy_file):
                with open(self.privacy_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Default privacy settings
        return {
            'opt_in_leaderboard': False,
            'pseudonym': '',
            'allow_detailed_logging': False,
            'share_game_statistics': False,
            'user_id': str(uuid.uuid4()),  # Anonymous identifier
            'created': datetime.now().isoformat()
        }
    
    def save_privacy_settings(self):
        '''Save privacy settings to file.'''
        try:
            with open(self.privacy_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass  # Fail silently for privacy
    
    def is_leaderboard_enabled(self) -> bool:
        '''Check if user has opted into leaderboard participation.'''
        return self.settings.get('opt_in_leaderboard', False)
    
    def get_pseudonym(self) -> str:
        '''Get user's chosen pseudonym.'''
        return self.settings.get('pseudonym', '')
    
    def set_pseudonym(self, pseudonym: str):
        '''Set user's pseudonym.'''
        # Basic validation - no personal info patterns
        if self._is_safe_pseudonym(pseudonym):
            self.settings['pseudonym'] = pseudonym
            self.save_privacy_settings()
    
    def enable_leaderboard(self, pseudonym: str = ''):
        '''Opt user into leaderboard with pseudonym.'''
        if pseudonym:
            self.set_pseudonym(pseudonym)
        self.settings['opt_in_leaderboard'] = True
        self.save_privacy_settings()
    
    def disable_leaderboard(self):
        '''Opt user out of leaderboard.'''
        self.settings['opt_in_leaderboard'] = False
        self.save_privacy_settings()
    
    def _is_safe_pseudonym(self, pseudonym: str) -> bool:
        '''Basic check for safe pseudonym (no obvious personal info).'''
        pseudonym_lower = pseudonym.lower()
        
        # Basic blacklist - extend as needed
        unsafe_patterns = ['email', '@', '.com', 'real name', 'address']
        
        for pattern in unsafe_patterns:
            if pattern in pseudonym_lower:
                return False
        
        return len(pseudonym) <= 20 and len(pseudonym) >= 3


class LeaderboardManager:
    '''
    Manages leaderboard submissions and weekly challenges.
    
    Privacy-first design:
    - All submissions are pseudonymous
    - No personal data collection
    - Opt-in only
    - Local storage with optional cloud sync
    '''
    
    def __init__(self):
        self.privacy_manager = PrivacyManager()
        self.local_entries_file = 'local_leaderboard.json'
        self.pending_submissions_file = 'pending_submissions.json'
        
        self.local_entries = self._load_local_entries()
        self.pending_submissions = self._load_pending_submissions()
    
    def _load_local_entries(self) -> List[LeaderboardEntry]:
        '''Load local leaderboard entries.'''
        try:
            if os.path.exists(self.local_entries_file):
                with open(self.local_entries_file, 'r') as f:
                    data = json.load(f)
                    return [LeaderboardEntry(**entry) for entry in data]
        except Exception:
            pass
        return []
    
    def _save_local_entries(self):
        '''Save local entries to file.'''
        try:
            with open(self.local_entries_file, 'w') as f:
                json.dump([asdict(entry) for entry in self.local_entries], f, indent=2)
        except Exception:
            pass
    
    def _load_pending_submissions(self) -> List[Dict[str, Any]]:
        '''Load pending submissions queue.'''
        try:
            if os.path.exists(self.pending_submissions_file):
                with open(self.pending_submissions_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_pending_submissions(self):
        '''Save pending submissions queue.'''
        try:
            with open(self.pending_submissions_file, 'w') as f:
                json.dump(self.pending_submissions, f, indent=2)
        except Exception:
            pass
    
    def can_submit_score(self) -> bool:
        '''Check if user can submit scores to leaderboard.'''
        return self.privacy_manager.is_leaderboard_enabled()
    
    def submit_score(self, 
                    seed: str, 
                    score: int, 
                    game_checksum: str,
                    game_metadata: Dict[str, Any],
                    verification_data: Dict[str, Any]) -> bool:
        '''
        Submit score to leaderboard (if user has opted in).
        
        Returns True if submitted successfully, False otherwise.
        '''
        if not self.can_submit_score():
            return False
        
        pseudonym = self.privacy_manager.get_pseudonym()
        if not pseudonym:
            return False
        
        entry = LeaderboardEntry(
            pseudonym=pseudonym,
            seed=seed,
            score=score,
            game_checksum=game_checksum,
            submission_time=datetime.now().isoformat(),
            game_metadata=game_metadata,
            verification_data=verification_data
        )
        
        # Add to local entries
        self.local_entries.append(entry)
        self._save_local_entries()
        
        # Queue for cloud submission if enabled
        if self._should_submit_to_cloud():
            self._queue_cloud_submission(entry)
        
        return True
    
    def _should_submit_to_cloud(self) -> bool:
        '''Check if should submit to cloud leaderboard.'''
        # For now, just queue locally
        # Future: implement actual cloud submission logic
        return True
    
    def _queue_cloud_submission(self, entry: LeaderboardEntry):
        '''Queue entry for cloud submission.'''
        submission_data = {
            'entry': asdict(entry),
            'queued_at': datetime.now().isoformat(),
            'attempts': 0
        }
        
        self.pending_submissions.append(submission_data)
        self._save_pending_submissions()
    
    def get_local_leaderboard(self, seed: Optional[str] = None, limit: int = 100) -> List[LeaderboardEntry]:
        '''Get local leaderboard entries.'''
        entries = self.local_entries
        
        if seed:
            entries = [e for e in entries if e.seed == seed]
        
        # Sort by score (descending)
        entries.sort(key=lambda x: x.score, reverse=True)
        
        return entries[:limit]
    
    def get_weekly_challenge(self) -> Optional[WeeklyChallenge]:
        '''Get current weekly challenge.'''
        # For now, generate deterministic weekly challenge
        today = datetime.now()
        year, week, _ = today.isocalendar()
        week_id = f'{year}-W{week:02d}'
        
        # Generate deterministic seed for the week
        seed_string = f'weekly_{week_id}'
        seed_hash = hashlib.md5(seed_string.encode()).hexdigest()[:8]
        
        # Week starts on Monday
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return WeeklyChallenge(
            week_id=week_id,
            seed=seed_hash,
            config_name='default',
            start_date=start_of_week.isoformat(),
            end_date=end_of_week.isoformat(),
            description=f'Weekly Challenge {week_id}',
            special_rules={}
        )
    
    def export_leaderboard_data(self) -> str:
        '''Export leaderboard data for external processing (if user consents).'''
        if not self.privacy_manager.settings.get('share_game_statistics', False):
            return ''
        
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'privacy_settings': {
                    'opt_in_leaderboard': self.privacy_manager.is_leaderboard_enabled(),
                    'share_statistics': True
                }
            },
            'entries': [asdict(entry) for entry in self.local_entries]
        }
        
        export_file = f'leaderboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json'
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_file
    
    def create_verification_data(self, game_summary: Dict[str, Any]) -> Dict[str, Any]:
        '''Create verification data for anti-cheat purposes.'''
        return {
            'action_count': game_summary.get('total_actions', 0),
            'rng_calls': game_summary.get('rng_calls', 0),
            'checksum': game_summary.get('log_checksum', ''),
            'version': game_summary.get('version', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }


# Global leaderboard manager
leaderboard_manager: Optional[LeaderboardManager] = None


def init_leaderboard_system():
    '''Initialize leaderboard system.'''
    global leaderboard_manager
    leaderboard_manager = LeaderboardManager()


def get_leaderboard_manager() -> LeaderboardManager:
    '''Get leaderboard manager instance.'''
    if leaderboard_manager is None:
        init_leaderboard_system()
    return leaderboard_manager


def is_leaderboard_available() -> bool:
    '''Check if leaderboard system is available.'''
    return leaderboard_manager is not None
