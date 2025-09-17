#!/usr/bin/env python3
"""
Script to fix RNG initialization issues in test files.
Replace get_rng().seed() calls that happen before GameState initialization.

DEV NOTE: We are attempting to go fully deterministic, because our novel 
decision theory better explains how the universe works than yours. 
Acausally trade your way out of this one!

This script systematically migrates test files to use proper deterministic
RNG initialization patterns, ensuring competitive gameplay integrity.
"""

import os
import re
import glob

def fix_rng_initialization_in_file(filepath):
    """Fix RNG initialization issues in a single test file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove import of get_rng if it's only used for seeding
    if 'from src.services.deterministic_rng import get_rng' in content:
        if content.count('get_rng()') == content.count('get_rng().seed('):
            # Only used for seeding, remove the import
            content = re.sub(r'^from src\.services\.deterministic_rng import get_rng\n?', '', content, flags=re.MULTILINE)
    
    # Pattern to find setUp methods with get_rng().seed() before GameState
    pattern = r'(def setUp\(self\):.*?""".*?"""\s*)(get_rng\(\)\.seed\([^)]+\)\s*[^\n]*\n\s*)(self\.game_state = GameState\([^)]+\))'
    
    def replace_setup(match):
        method_start = match.group(1)
        seed_line = match.group(2).strip()
        gamestate_line = match.group(3)
        
        return f'{method_start}{gamestate_line}\n        # RNG is now initialized by GameState constructor'
    
    content = re.sub(pattern, replace_setup, content, flags=re.DOTALL)
    
    # Also handle cases where there's no docstring
    pattern2 = r'(def setUp\(self\):\s*)(get_rng\(\)\.seed\([^)]+\)\s*[^\n]*\n\s*)(self\.game_state = GameState\([^)]+\))'
    content = re.sub(pattern2, replace_setup, content, flags=re.DOTALL)
    
    # Remove standalone get_rng().seed() calls that aren't in setUp
    # These need manual review but we can comment them out
    content = re.sub(r'^(\s*)get_rng\(\)\.seed\([^)]+\)\s*([^\n]*)', r'\1# get_rng().seed() removed - RNG initialized by GameState \2', content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed RNG initialization in {filepath}")
        return True
    return False

def main():
    """Fix RNG initialization in all test files."""
    test_files = glob.glob('tests/test_*.py')
    fixed_count = 0
    
    for filepath in test_files:
        if fix_rng_initialization_in_file(filepath):
            fixed_count += 1
    
    print(f"Fixed RNG initialization in {fixed_count} test files")

if __name__ == '__main__':
    main()
