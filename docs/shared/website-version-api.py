'''
Website Version Tracking API
==========================

API endpoints for tracking game versions, website versions, and data batch integration.
Designed for the pdoom1-website to consume and display version information.
'''

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class VersionStatus(Enum):
    '''Version support status levels.'''
    CURRENT = 'current'
    SUPPORTED = 'supported' 
    DEPRECATED = 'deprecated'
    END_OF_LIFE = 'end_of_life'


class SupportLevel(Enum):
    '''Level of support for a version.'''
    FULL = 'full'
    SECURITY_ONLY = 'security_only'
    NONE = 'none'


class ReleaseType(Enum):
    '''Type of release following semantic versioning.'''
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
    HOTFIX = 'hotfix'


@dataclass
class GameVersion:
    '''Represents a game version with metadata.'''
    version: str
    display_version: str
    release_date: date
    status: VersionStatus
    support_level: SupportLevel
    end_of_life: Optional[date] = None
    changelog_url: Optional[str] = None
    download_url: Optional[str] = None
    size_mb: Optional[int] = None
    requirements: Optional[Dict[str, Any]] = None


@dataclass
class WebsiteVersion:
    '''Represents website version information.'''
    version: str
    name: str
    release_date: datetime
    description: str
    changelog_url: str
    build_info: Dict[str, str]


@dataclass
class DataBatch:
    '''Represents a data batch from pdoom-data integration.'''
    batch_type: str  # leaderboards, analytics, challenges
    version: str
    batch_date: date
    record_count: int
    schema_version: str
    compatible_game_versions: List[str]
    status: str = 'active'


class VersionTrackingAPI:
    '''
    Main API class for version tracking functionality.
    
    This would be implemented in the website backend to serve
    version information to the frontend and external consumers.
    '''
    
    def __init__(self):
        self.current_game_version = '0.6.0'
        self.website_version = '1.0.0'
        self.data_integration_enabled = False
    
    # === Game Version Endpoints ===
    
    def get_current_game_version(self) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/game/current
        
        Returns current game version information.
        '''
        return {
            'version': self.current_game_version,
            'display_version': f'v{self.current_game_version}',
            'status': 'stable',
            'release_date': '2025-09-14',
            'download_url': f'https://github.com/PipFoweraker/pdoom1/releases/tag/v{self.current_game_version}',
            'changelog_url': f'/game/releases/v{self.current_game_version}',
            'requirements': {
                'python': '3.9+',
                'os': ['Windows 10+', 'Linux', 'macOS'],
                'memory': '512MB',
                'storage': '100MB'
            }
        }
    
    def get_game_version_history(self, limit: int = 10) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/game/history?limit=10
        
        Returns historical game version information.
        '''
        return {
            'versions': [
                {
                    'version': '0.6.0',
                    'release_date': '2025-09-14',
                    'type': 'minor',
                    'highlights': ['Development transparency', 'Automated blog pipeline']
                },
                {
                    'version': '0.5.0', 
                    'release_date': '2025-09-14',
                    'type': 'minor',
                    'highlights': ['PyInstaller distribution', 'Windows executable']
                },
                {
                    'version': '0.4.1',
                    'release_date': '2025-09-13', 
                    'type': 'patch',
                    'highlights': ['Enhanced leaderboards', 'Performance improvements']
                }
            ],
            'pagination': {
                'total': 15,
                'limit': limit,
                'has_more': True
            }
        }
    
    def get_supported_versions(self) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/game/supported
        
        Returns currently supported game versions.
        '''
        return {
            'supported_versions': [
                {
                    'version': '0.6.0',
                    'status': 'current',
                    'support_level': 'full',
                    'end_of_life': None
                },
                {
                    'version': '0.5.0',
                    'status': 'supported', 
                    'support_level': 'security_only',
                    'end_of_life': '2025-12-15'
                }
            ],
            'deprecated_versions': [
                {
                    'version': '0.4.1',
                    'status': 'deprecated',
                    'support_level': 'none', 
                    'end_of_life': '2025-10-15'
                }
            ]
        }
    
    # === Website Version Endpoints ===
    
    def get_website_version(self) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/website
        
        Returns current website version information.
        '''
        return {
            'version': self.website_version,
            'name': 'P(Doom) Community Hub',
            'release_date': '2025-09-15T00:00:00Z',
            'description': 'Official website for P(Doom): Bureaucracy Strategy Game',
            'build_info': {
                'environment': 'production',
                'framework': 'Next.js',
                'node_version': '18.x'
            },
            'features': [
                'Game version tracking',
                'Development blog integration', 
                'Community features',
                'Download management'
            ]
        }
    
    # === Data Integration Endpoints (Placeholders) ===
    
    def get_data_status(self) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/data/current
        
        Returns current data integration status.
        '''
        if not self.data_integration_enabled:
            return {
                'enabled': False,
                'status': 'placeholder',
                'message': 'Data integration not yet implemented',
                'target_date': '2025-11-01',
                'features': {
                    'leaderboards': 'planned',
                    'analytics': 'planned', 
                    'challenges': 'planned'
                }
            }
        
        # Future implementation when pdoom-data is ready
        return {
            'enabled': True,
            'status': 'active',
            'last_sync': '2025-09-15T12:00:00Z',
            'data_batches': {
                'leaderboards': {
                    'version': '1.0.0',
                    'batch_date': '2025-09-15',
                    'records': 15420
                },
                'analytics': {
                    'version': '1.0.0', 
                    'batch_date': '2025-09-15',
                    'metrics': 8940
                }
            }
        }
    
    def get_compatibility_matrix(self) -> Dict[str, Any]:
        '''
        GET /api/v1/versions/compatibility
        
        Returns version compatibility information.
        '''
        return {
            'website_version': self.website_version,
            'supported_game_versions': ['0.6.0', '0.5.0'],
            'compatibility': {
                '0.6.0': {
                    'website_features': 'full',
                    'data_integration': 'ready',
                    'api_version': '1.0.0'
                },
                '0.5.0': {
                    'website_features': 'full', 
                    'data_integration': 'limited',
                    'api_version': '1.0.0'
                },
                '0.4.1': {
                    'website_features': 'basic',
                    'data_integration': 'none', 
                    'api_version': '0.9.0'
                }
            },
            'deprecated_after': '2025-12-31'
        }
    
    # === Webhook Endpoints ===
    
    def sync_game_version(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        '''
        POST /api/v1/versions/sync
        
        Webhook endpoint for GitHub releases to sync game versions.
        '''
        # Extract version from GitHub webhook
        tag_name = webhook_data.get('release', {}).get('tag_name', '')
        version = tag_name.lstrip('v')
        
        # Update current version tracking
        self.current_game_version = version
        
        # Trigger content updates
        self._update_version_content(version, webhook_data)
        
        return {
            'status': 'success',
            'updated_version': version,
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [
                'Updated current version tracking',
                'Generated changelog content',
                'Invalidated version cache',
                'Triggered content rebuild'
            ]
        }
    
    def _update_version_content(self, version: str, webhook_data: Dict[str, Any]):
        '''Internal method to update version-related content.'''
        # This would trigger:
        # 1. Content generation from changelog
        # 2. Cache invalidation
        # 3. Static site rebuild
        # 4. CDN cache purge


# === Data Batch Integration Stubs ===

class DataBatchAPI:
    '''
    Placeholder API for future pdoom-data integration.
    
    This will be implemented when pdoom-data repository is ready
    and authentication/privacy systems are in place.
    '''
    
    def __init__(self):
        self.integration_ready = False
        self.mock_data = True
    
    def get_leaderboard_batch(self, batch_date: Optional[str] = None) -> Dict[str, Any]:
        '''
        GET /api/v1/data/leaderboards?batch_date=2025-09-15
        
        Future endpoint for leaderboard data batches.
        '''
        if not self.integration_ready:
            return {
                'status': 'not_implemented',
                'message': 'Leaderboard integration pending pdoom-data completion',
                'mock_data': {
                    'batch_date': '2025-09-15',
                    'version': '0.0.0',
                    'records': [],
                    'schema': 'placeholder'
                }
            }
    
    def get_analytics_batch(self, batch_date: Optional[str] = None) -> Dict[str, Any]:
        '''
        GET /api/v1/data/analytics?batch_date=2025-09-15
        
        Future endpoint for analytics data batches.
        '''
        if not self.integration_ready:
            return {
                'status': 'not_implemented', 
                'message': 'Analytics integration pending pdoom-data completion',
                'mock_data': {
                    'batch_date': '2025-09-15',
                    'version': '0.0.0',
                    'metrics': {},
                    'schema': 'placeholder'
                }
            }
    
    def get_challenges_batch(self, batch_date: Optional[str] = None) -> Dict[str, Any]:
        '''
        GET /api/v1/data/challenges?batch_date=2025-09-15
        
        Future endpoint for challenge data batches.
        '''
        if not self.integration_ready:
            return {
                'status': 'not_implemented',
                'message': 'Challenges integration pending pdoom-data completion', 
                'mock_data': {
                    'batch_date': '2025-09-15',
                    'version': '0.0.0',
                    'challenges': [],
                    'schema': 'placeholder'
                }
            }


# === Usage Examples ===

def example_usage():
    '''Example of how the website would use these APIs.'''
    
    # Initialize API
    version_api = VersionTrackingAPI()
    DataBatchAPI()
    
    # Get current game version for header display
    current_version = version_api.get_current_game_version()
    print(f'Current Game Version: {current_version['display_version']}')
    
    # Get version history for releases page
    history = version_api.get_game_version_history(limit=5)
    print(f'Recent Releases: {len(history['versions'])} versions')
    
    # Check data integration status
    data_status = version_api.get_data_status()
    print(f'Data Integration: {data_status['status']}')
    
    # Get compatibility info for support pages
    compatibility = version_api.get_compatibility_matrix()
    print(f'Supported Versions: {compatibility['supported_game_versions']}')


if __name__ == '__main__':
    example_usage()
