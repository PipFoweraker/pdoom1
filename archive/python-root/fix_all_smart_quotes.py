#!/usr/bin/env python3
"""
Fix ALL smart quotes in pygame/tests/ directory
Converts Unicode smart quotes to regular ASCII quotes
"""

from pathlib import Path

SMART_QUOTE_REPLACEMENTS = {
    '\u2018': "'",  # ' (left single quote)
    '\u2019': "'",  # ' (right single quote)
    '\u201c': '"',  # " (left double quote)
    '\u201d': '"',  # " (right double quote)
    '\u201a': ',',  # ‚ (single low quote)
    '\u201e': '"',  # „ (double low quote)
    '\u2032': "'",  # ′ (prime)
    '\u2033': '"',  # ″ (double prime)
}

def fix_smart_quotes(content):
    """Replace all smart quotes with regular quotes"""
    for smart, regular in SMART_QUOTE_REPLACEMENTS.items():
        content = content.replace(smart, regular)
    return content

def fix_file(filepath):
    """Fix smart quotes in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        fixed = fix_smart_quotes(original)

        if fixed != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True, "Fixed smart quotes"
        else:
            return False, "No smart quotes found"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix all test files in pygame/tests/"""
    test_dir = Path('pygame/tests')

    if not test_dir.exists():
        print(f"ERROR: {test_dir} not found!")
        return

    fixed_count = 0
    test_files = sorted(test_dir.glob('test_*.py'))

    print(f"Scanning {len(test_files)} test files for smart quotes...\n")

    for test_file in test_files:
        success, message = fix_file(test_file)
        if success:
            fixed_count += 1
            print(f"[FIXED] {test_file.name}: {message}")

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} files with smart quotes")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
