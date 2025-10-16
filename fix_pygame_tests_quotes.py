#!/usr/bin/env python3
"""
Fix quote escaping errors in pygame/tests/ directory only
Handles f-string nested quote issues from ASCII compliance fixer
"""

import re
from pathlib import Path

def fix_fstring_quotes(line):
    """Fix f-strings with nested quotes by swapping outer quotes"""
    # Pattern: f'text 'word' text' -> f"text 'word' text"
    # Only fix if there are nested single quotes
    if line.count("f'") > 0 and line.count("'") > 2:
        # Find f-strings with single outer quotes
        pattern = r"f'([^']*'[^']*')'"
        matches = list(re.finditer(pattern, line))

        # Process matches in reverse to maintain positions
        for match in reversed(matches):
            inner = match.group(1)
            # Only swap if inner has single quotes and no double quotes
            if "'" in inner and '"' not in inner:
                replacement = f'f"{inner}"'
                line = line[:match.start()] + replacement + line[match.end():]

    return line

def fix_file(filepath):
    """Fix quote errors in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        new_lines = []

        for i, line in enumerate(lines, 1):
            original = line

            # Fix f-string quote issues
            line = fix_fstring_quotes(line)

            # Additional specific patterns found in errors
            # Pattern: self.assertEqual(..., f'Missing 'word' ...')
            if 'assertIn' in line or 'assertEqual' in line or 'assert' in line.lower():
                # Fix nested quotes in assertion messages
                if "f'" in line and line.count("'") > 2:
                    line = fix_fstring_quotes(line)

            # Pattern: f.write('{...}') - unescaped braces
            if '.write(' in line and '{' in line:
                # This is trickier - check if it's an actual formatting issue
                # For now, flag it but don't auto-fix
                pass

            if line != original:
                modified = True

            new_lines.append(line)

        if modified:
            # Validate by trying to compile
            try:
                compile(''.join(new_lines), filepath, 'exec')
                # Success! Write the fixed file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return True, "Fixed"
            except SyntaxError as e:
                # Still broken, revert
                return False, f"Still has SyntaxError at line {e.lineno}: {e.msg}"
        else:
            return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix all test files in pygame/tests/"""
    test_dir = Path('pygame/tests')

    if not test_dir.exists():
        print(f"ERROR: {test_dir} not found!")
        return

    fixed_count = 0
    error_count = 0
    unchanged_count = 0

    test_files = sorted(test_dir.glob('test_*.py'))

    print(f"Processing {len(test_files)} test files in pygame/tests/\n")

    for test_file in test_files:
        success, message = fix_file(test_file)

        if success:
            fixed_count += 1
            print(f"[FIXED] {test_file.name}")
        elif "SyntaxError" in message:
            error_count += 1
            print(f"[ERROR] {test_file.name}: {message}")
        else:
            unchanged_count += 1
            # Don't print unchanged files to reduce noise

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Still have errors: {error_count}")
    print(f"  No changes needed: {unchanged_count}")
    print(f"{'='*60}")

    if error_count > 0:
        print("\nFiles still with errors need manual inspection")

    return error_count == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
