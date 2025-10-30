#!/usr/bin/env python3
"""Fix smart quotes in pygame/main.py"""

import sys
from pathlib import Path

# Smart quote replacements
REPLACEMENTS = {
    '\u2018': "'",  # '
    '\u2019': "'",  # '
    '\u201c': '"',  # "
    '\u201d': '"',  # "
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for smart, regular in REPLACEMENTS.items():
        content = content.replace(smart, regular)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

if __name__ == '__main__':
    filepath = Path('pygame/main.py')
    if fix_file(filepath):
        print(f'[FIXED] Replaced smart quotes in {filepath}')
    else:
        print(f'[OK] No smart quotes in {filepath}')
