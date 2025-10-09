"""
Web Export Module for P(Doom)1 Leaderboards

This module provides functionality to export leaderboard data in formats
compatible with the pdoom1-website repository, enabling global leaderboards
and web-based competition features.

Components:
- export_leaderboards.py: Main export script and CLI interface
- api_format.py: Convert internal format to web API format
- privacy_filter.py: Apply privacy controls and anonymization

Usage:
    from tools.web_export import export_leaderboards
    
    # Export all leaderboards
    python -m tools.web_export.export_leaderboards --output ./web_data/
    
    # Export specific seed with privacy filtering
    python -m tools.web_export.export_leaderboards --seed test-seed --privacy-filter
"""

from .export_leaderboards import LeaderboardWebExporter
from .api_format import WebAPIFormatter
from .privacy_filter import PrivacyFilter

__version__ = "1.0.0"
__all__ = ["LeaderboardWebExporter", "WebAPIFormatter", "PrivacyFilter"]