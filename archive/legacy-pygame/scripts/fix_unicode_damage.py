#!/usr/bin/env python3
"""
Game State Unicode Repair Script

This script fixes specific Unicode damage caused by the nuclear Unicode killer
in the game_state.py file, restoring proper string formatting.
"""

import re
from pathlib import Path

def fix_game_state_unicode():
    """Fix Unicode damage in game_state.py"""
    file_path = Path('src/core/game_state.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix broken possessive quotes
    content = re.sub(r'\?\? ([^}]+)\}\'s', r'\1}\'s', content)
    
    # Fix broken contractions and quotes in f-strings and regular strings  
    content = content.replace("'You're", "'You're")
    content = content.replace("'s ", "'s ")
    content = content.replace("'t ", "'t ")
    content = content.replace("'ll ", "'ll ")
    content = content.replace("'ve ", "'ve ")
    content = content.replace("'re ", "'re ")
    content = content.replace("'d ", "'d ")
    
    # Fix specific known broken patterns
    fixes = [
        (r"f'Action '\{action\['name'\]\}' not available'", r"f'Action {action[\"name\"]} not available'"),
        (r"'Consider using 'Scout Opponents' for detailed intelligence gathering.'", 
         r'"Consider using \'Scout Opponents\' for detailed intelligence gathering."'),
        (r"'Use 'Intelligence' action to gather more intelligence on their capabilities.'",
         r'"Use \'Intelligence\' action to gather more intelligence on their capabilities."'),
        (r"Cannot afford \{researcher\.name\}'s salary", r"Cannot afford {researcher.name}'s salary"),
        (r"Ranked #\{rank\} for seed '\{self\.seed\}'", r"Ranked #{rank} for seed '{self.seed}'"),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed Unicode damage in game_state.py")

if __name__ == '__main__':
    fix_game_state_unicode()