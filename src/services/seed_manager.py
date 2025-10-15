'''
Seed Management for P(Doom)

This module centralizes seed generation and management for reproducible gameplay.
It supports weekly challenge seeds, custom seeds, and seed validation.
'''

import datetime
import hashlib
import re


def get_weekly_seed() -> str:
    '''
    Get the current weekly challenge seed.
    
    Returns:
        String seed based on current year and ISO week number
    '''
    now = datetime.datetime.now(datetime.timezone.utc)
    return f'{now.year}{now.isocalendar()[1]}'


def get_daily_seed() -> str:
    '''
    Get a daily seed for daily challenges.
    
    Returns:
        String seed based on current date
    '''
    now = datetime.datetime.now(datetime.timezone.utc)
    return f'{now.year}{now.month:02d}{now.day:02d}'


def validate_custom_seed(seed: str) -> bool:
    '''
    Validate a custom seed for acceptability.
    
    Args:
        seed: Custom seed string to validate
        
    Returns:
        True if seed is valid, False otherwise
    '''
    if not seed or not isinstance(seed, str):
        return False
    
    # Remove whitespace
    seed = seed.strip()
    
    # Check length (reasonable limits)
    if len(seed) < 1 or len(seed) > 50:
        return False
    
    # Check for valid characters (alphanumeric, spaces, basic punctuation)
    if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', seed):
        return False
    
    return True


def normalize_seed(seed: str) -> str:
    '''
    Normalize a seed string for consistent usage.
    
    Args:
        seed: Raw seed string
        
    Returns:
        Normalized seed string
    '''
    if not seed:
        return get_weekly_seed()
    
    # Strip whitespace and convert to consistent case
    normalized = seed.strip()
    
    # If empty after stripping, use weekly seed
    if not normalized:
        return get_weekly_seed()
    
    return normalized


def generate_seed_hash(seed: str) -> str:
    '''
    Generate a hash from a seed for consistent randomization.
    
    Args:
        seed: Seed string to hash
        
    Returns:
        Hexadecimal hash string
    '''
    normalized = normalize_seed(seed)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def create_community_seed(description: str, difficulty: str = 'standard') -> str:
    '''
    Create a themed seed for community challenges.
    
    Args:
        description: Description of the challenge
        difficulty: Difficulty level
        
    Returns:
        Generated seed string
    '''
    # Create a seed based on description and current date
    now = datetime.datetime.now(datetime.timezone.utc)
    base = f'{description}_{difficulty}_{now.year}_{now.month:02d}_{now.day:02d}'
    
    # Generate hash and take first 8 characters for readability
    seed_hash = hashlib.md5(base.encode('utf-8')).hexdigest()[:8]
    
    return f'{difficulty}_{seed_hash}'


def parse_seed_info(seed: str) -> dict:
    '''
    Parse seed string to extract information about it.
    
    Args:
        seed: Seed string to parse
        
    Returns:
        Dictionary with seed information
    '''
    info = {
        'seed': seed,
        'type': 'custom',
        'is_weekly': False,
        'is_daily': False,
        'is_generated': False,
        'description': 'Custom seed'
    }
    
    if not seed:
        return info
    
    # Check if it's a weekly seed (YYYYWW format)
    if re.match(r'^\d{6}$', seed):
        try:
            year = int(seed[:4])
            week = int(seed[4:])
            if 2020 <= year <= 2050 and 1 <= week <= 53:
                info['type'] = 'weekly'
                info['is_weekly'] = True
                info['description'] = f'Weekly challenge for {year}, week {week}'
        except ValueError:
            pass
    
    # Check if it's a daily seed (YYYYMMDD format)
    elif re.match(r'^\d{8}$', seed):
        try:
            year = int(seed[:4])
            month = int(seed[4:6])
            day = int(seed[6:])
            if 2020 <= year <= 2050 and 1 <= month <= 12 and 1 <= day <= 31:
                info['type'] = 'daily'
                info['is_daily'] = True
                info['description'] = f'Daily challenge for {year}-{month:02d}-{day:02d}'
        except ValueError:
            pass
    
    # Check if it's a generated community seed
    elif '_' in seed:
        parts = seed.split('_')
        if len(parts) >= 2 and parts[0] in ['standard', 'hardcore', 'sandbox', 'speedrun']:
            info['type'] = 'community'
            info['is_generated'] = True
            info['description'] = f'Community {parts[0]} challenge'
    
    return info


def get_seed_display_name(seed: str) -> str:
    '''
    Get a human-readable display name for a seed.
    
    Args:
        seed: Seed string
        
    Returns:
        Display-friendly name
    '''
    info = parse_seed_info(seed)
    
    if info['is_weekly']:
        return f'Weekly Challenge ({seed})'
    elif info['is_daily']:
        return f'Daily Challenge ({seed})'
    elif info['is_generated']:
        return f'Community Challenge ({seed})'
    else:
        return f'Custom Seed ({seed})'
