#!/usr/bin/env python3
"""Comprehensively fix all quote issues in ui.py"""

import re

def fix_all_quotes():
    with open('ui.py.backup', 'r', encoding='utf-8') as f:
        content = f.read()

    # List of all problematic patterns we need to fix
    fixes = [
        # Line 391: Pip Foweraker's
        (r"'Pip Foweraker's'", r'"Pip Foweraker\'s"'),

        # Line 4443: You'll
        (r"'You'll be assigned", r'"You\'ll be assigned'),

        # Line 3052: Click 'Got it!'
        (r"'Click 'Got it!' or press", r'"Click \'Got it!\' or press'),

        # Line 4646: Seed with nested quotes in f-string
        (r"f'Seed: '{seed}' \|", r'f"Seed: {seed} |'),

        # Any other instances of contractions in single quotes
        (r"'([^']*)'s ", r'"\1\'s "'),
        (r"'([^']*)You'll", r'"\1You\'ll'),
        (r"'([^']*)won't", r'"\1won\'t'),
        (r"'([^']*)can't", r'"\1can\'t'),
        (r"'([^']*)don't", r'"\1don\'t'),
        (r"'([^']*)doesn't", r'"\1doesn\'t"),
        (r"'([^']*)it's", r'"\1it\'s'),
        (r"'([^']*)that's", r'"\1that\'s'),
    ]

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)

    with open('ui.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Applied all fixes")

if __name__ == '__main__':
    fix_all_quotes()
