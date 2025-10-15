# !/usr/bin/env python3
'''
ASCII Compliance Fixer - Remove all Unicode characters from project files
'''

import re
from pathlib import Path

def fix_unicode_in_file(filepath: str) -> bool:
    '''Remove Unicode characters from a file, return True if changes made'''
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # File might have mixed encodings, try binary mode
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
    
    original_content = content
    
    # Common Unicode replacements
    # Type ignore because this list intentionally contains Unicode for replacement
    replacements = [  # type: ignore
        ('PASS', 'PASS'),
        ('FAIL', 'FAIL'),
        ('OK', 'OK'),
        ('ERROR', 'ERROR'),
        ('WARNING', 'WARNING'),
        ('NOTE', 'NOTE'),
        ('LAUNCH', 'LAUNCH'),
        ('TOOL', 'TOOL'),
        ('TARGET', 'TARGET'),
        ('IDEA', 'IDEA'),
        ('BUG', 'BUG'),
        ('STAR', 'STAR'),
        ('TROPHY', 'TROPHY'),
        ('CHART', 'CHART'),
        ('SEARCH', 'SEARCH'),
        ('FAST', 'FAST'),
        ('GAME', 'GAME'),
        ('CODE', 'CODE'),
        ('LIST', 'LIST'),
        ('PARTY', 'PARTY'),
        ('HOT', 'HOT'),
        ('100%', '100%'),
        ('STAR', 'STAR'),
        ('CONSTRUCTION', 'CONSTRUCTION'),
        ('GROWTH', 'GROWTH'),
        ('DESIGN', 'DESIGN'),
        ('TOOLS', 'TOOLS'),
        ('PACKAGE', 'PACKAGE'),
        ('REFRESH', 'REFRESH'),
        ('SETTINGS', 'SETTINGS'),
        ('PIN', 'PIN'),
        ('CIRCUS', 'CIRCUS'),
        ('SHINE', 'SHINE'),
        # Unicode dashes and quotes
        ('-', '-'),
        ('-', '-'),
        (''', '''),
        (''', '''),
        (''', '''),
        # Unicode bullets and arrows  
        ('*', '*'),
        ('->', '->'),
        ('<-', '<-'),
        ('^', '^'),
        ('v', 'v'),
        # Other special characters
        ('...', '...'),
        ('(c)', '(c)'),
        ('(R)', '(R)'),
        ('(TM)', '(TM)'),
    ]
    
    # Apply replacements
    # Type ignore because we're intentionally processing Unicode characters
    for unicode_char, replacement in replacements:  # type: ignore
        content = content.replace(unicode_char, replacement)  # type: ignore
    
    # Remove any remaining non-ASCII characters
    content = re.sub(r'[^\x00-\x7F]+', '?', content)
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='ascii', errors='replace') as f:
            f.write(content)
        return True
    
    return False

def main():
    '''Fix ASCII compliance across the entire project'''
    project_root = Path('.')
    
    # File patterns to check
    patterns = [
        '**/*.py',
        '**/*.md',
        '**/*.txt',
        '**/*.json',
        '**/*.yaml',
        '**/*.yml'
    ]
    
    files_changed = 0
    
    for pattern in patterns:
        for filepath in project_root.glob(pattern):
            if filepath.is_file() and not any(part.startswith('.') for part in filepath.parts):
                try:
                    if fix_unicode_in_file(str(filepath)):
                        print(f'Fixed: {filepath}')
                        files_changed += 1
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')
    
    print(f'\nFixed {files_changed} files for ASCII compliance')

if __name__ == '__main__':
    main()