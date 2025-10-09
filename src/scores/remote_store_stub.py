'''
Remote score storage stub for PDoom1.

Placeholder implementation for future HTTPS JSON score uploads.
Provides interface for when online leaderboards are implemented.
'''

from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from src.scores.local_store import ScoreEntry

if TYPE_CHECKING:
    from src.scores.local_store import LocalLeaderboard


class RemoteLeaderboard:
    '''
    Stub implementation for remote leaderboard functionality.
    
    This is a placeholder for future implementation of online leaderboards.
    Currently returns mock data and logs intended operations.
    '''
    
    def __init__(self, 
                 api_endpoint: str = 'https://api.pdoom1.com/scores',
                 api_key: Optional[str] = None):
        '''
        Initialize remote leaderboard stub.
        
        Args:
            api_endpoint: API endpoint URL (not used in stub)
            api_key: API authentication key (not used in stub)
        '''
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.is_enabled = False  # Stub is never actually enabled
        
        print(f'RemoteLeaderboard initialized as stub (endpoint: {api_endpoint})')
    
    def is_available(self) -> bool:
        '''
        Check if remote leaderboard service is available.
        
        Returns:
            False (stub always returns False)
        '''
        return False
    
    def submit_score(self, score_entry: ScoreEntry) -> Dict[str, Any]:
        '''
        Submit a score to the remote leaderboard.
        
        Args:
            score_entry: ScoreEntry to submit
            
        Returns:
            Mock response dictionary
        '''
        print(f'STUB: Would submit score: {score_entry}')
        
        # Return mock response
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'rank': None,
            'submitted_at': datetime.now().isoformat(),
            'entry_id': None
        }
    
    def get_global_leaderboard(self, 
                              count: int = 100, 
                              game_mode: Optional[str] = None) -> Dict[str, Any]:
        '''
        Get global leaderboard from remote service.
        
        Args:
            count: Number of entries to retrieve
            game_mode: Filter by game mode
            
        Returns:
            Mock response with empty leaderboard
        '''
        print(f'STUB: Would fetch global leaderboard (count={count}, mode={game_mode})')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'entries': [],
            'total_count': 0,
            'fetched_at': datetime.now().isoformat()
        }
    
    def get_player_rank(self, player_name: str, game_mode: Optional[str] = None) -> Dict[str, Any]:
        '''
        Get a player's rank from the remote leaderboard.
        
        Args:
            player_name: Player to look up
            game_mode: Filter by game mode
            
        Returns:
            Mock response with no rank found
        '''
        print(f'STUB: Would fetch rank for player '{player_name}' (mode={game_mode})')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'player_name': player_name,
            'rank': None,
            'score': None,
            'fetched_at': datetime.now().isoformat()
        }
    
    def sync_with_local(self, local_leaderboard: 'LocalLeaderboard') -> Dict[str, Any]:
        '''
        Sync local leaderboard with remote service.
        
        Args:
            local_leaderboard: Local leaderboard to sync
            
        Returns:
            Mock response indicating no sync occurred
        '''
        print(f'STUB: Would sync {len(local_leaderboard.entries)} local entries with remote')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'uploaded_count': 0,
            'downloaded_count': 0,
            'synced_at': datetime.now().isoformat()
        }
    
    def validate_connection(self) -> Dict[str, Any]:
        '''
        Validate connection to remote service.
        
        Returns:
            Mock response indicating connection failed
        '''
        print('STUB: Would validate connection to remote service')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'endpoint': self.api_endpoint,
            'authenticated': False,
            'latency_ms': None,
            'checked_at': datetime.now().isoformat()
        }
    
    def get_daily_challenge_scores(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        '''
        Get daily challenge leaderboard.
        
        Args:
            date: Date for daily challenge (defaults to today)
            
        Returns:
            Mock response with empty daily challenge
        '''
        date = date or datetime.now()
        print(f'STUB: Would fetch daily challenge scores for {date.date()}')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'date': date.date().isoformat(),
            'entries': [],
            'challenge_id': None,
            'fetched_at': datetime.now().isoformat()
        }
    
    def submit_daily_challenge_score(self, 
                                   score_entry: ScoreEntry,
                                   challenge_id: str) -> Dict[str, Any]:
        '''
        Submit score for daily challenge.
        
        Args:
            score_entry: ScoreEntry to submit
            challenge_id: Daily challenge identifier
            
        Returns:
            Mock response indicating submission failed
        '''
        print(f'STUB: Would submit daily challenge score: {score_entry} (challenge: {challenge_id})')
        
        return {
            'success': False,
            'message': 'Remote leaderboard not implemented',
            'challenge_id': challenge_id,
            'rank': None,
            'submitted_at': datetime.now().isoformat()
        }


class RemoteStoreManager:
    '''
    Manager for remote store operations with graceful fallbacks.
    
    Coordinates between local and remote storage, handling cases where
    remote service is unavailable.
    '''
    
    def __init__(self, 
                 local_leaderboard: 'LocalLeaderboard',
                 remote_leaderboard: Optional[RemoteLeaderboard] = None):
        '''
        Initialize remote store manager.
        
        Args:
            local_leaderboard: Local leaderboard instance
            remote_leaderboard: Remote leaderboard instance (creates stub if None)
        '''
        self.local = local_leaderboard
        self.remote = remote_leaderboard or RemoteLeaderboard()
        
    def submit_score(self, score_entry: ScoreEntry) -> Dict[str, Any]:
        '''
        Submit score to both local and remote stores.
        
        Args:
            score_entry: ScoreEntry to submit
            
        Returns:
            Combined result from local and remote submissions
        '''
        # Always save locally first
        local_success, local_rank = self.local.add_score(score_entry)
        
        # Attempt remote submission if available
        remote_result = {'success': False, 'message': 'Remote not available'}
        if self.remote.is_available():
            remote_result = self.remote.submit_score(score_entry)
        
        return {
            'local': {
                'success': local_success,
                'rank': local_rank
            },
            'remote': remote_result,
            'submitted_at': datetime.now().isoformat()
        }
    
    def get_combined_leaderboard(self, 
                               count: int = 10,
                               game_mode: Optional[str] = None) -> Dict[str, Any]:
        '''
        Get leaderboard combining local and remote scores.
        
        Args:
            count: Number of entries to return
            game_mode: Filter by game mode
            
        Returns:
            Combined leaderboard data
        '''
        # Get local scores
        local_scores = self.local.get_top_scores(count, game_mode)
        
        # Try to get remote scores
        remote_result = {'success': False, 'entries': []}
        if self.remote.is_available():
            remote_result = self.remote.get_global_leaderboard(count, game_mode)
        
        return {
            'local_scores': [entry.to_dict() for entry in local_scores],
            'remote_scores': remote_result.get('entries', []),
            'remote_available': self.remote.is_available(),
            'fetched_at': datetime.now().isoformat()
        }
    
    def sync_scores(self) -> Dict[str, Any]:
        '''
        Synchronize local and remote leaderboards.
        
        Returns:
            Sync result information
        '''
        if not self.remote.is_available():
            return {
                'success': False,
                'message': 'Remote service not available',
                'synced_at': datetime.now().isoformat()
            }
        
        return self.remote.sync_with_local(self.local)