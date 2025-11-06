#!/usr/bin/env python3
"""
Fix systematic quote escaping errors in test files
Addresses syntax errors from f-string quote nesting issues
"""

import re
from pathlib import Path
import ast

def fix_quote_errors_in_file(filepath):
    """Fix quote escaping errors in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Pattern 1: f'string with 'nested' quotes' -> f"string with 'nested' quotes"
        # Find f-strings with single quotes that contain single quotes inside
        pattern1 = r"f'([^']*'[^']*')(?!')"

        def replace_outer_quotes(match):
            inner = match.group(1)
            # If the inner content has single quotes, change outer to double
            if "'" in inner and '"' not in inner:
                return f'f"{inner}"'
            return match.group(0)

        content = re.sub(pattern1, replace_outer_quotes, content)

        # Pattern 2: f.write('{') or similar - unescaped braces in strings
        # Find strings with unmatched braces
        pattern2 = r"(['\"])(\{[^}]*|[^{]*\})(\1)"

        def escape_braces(match):
            quote = match.group(1)
            inner = match.group(2)
            # If it's just a brace without proper formatting, it might be an issue
            # This is complex, let's handle specific cases
            return match.group(0)

        # Pattern 3: Common specific patterns found in errors
        # self.assertEqual(..., f'text 'word' more')
        fixes = [
            (r"f'([^']*)'([^']+)'([^']*)'", lambda m: f'f"{m.group(1)}\'{m.group(2)}\'{m.group(3)}"'),
            (r'f"([^"]*)"([^"]+)"([^"]*)"', lambda m: f'f\'{m.group(1)}"{m.group(2)}"{m.group(3)}\''),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        # Try to parse to see if we fixed it
        try:
            ast.parse(content)
            # Successfully parses!
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, "Fixed"
            return False, "No changes needed"
        except SyntaxError as e:
            # Still has errors, try manual specific patterns
            # Get the line with error
            lines = content.split('\n')
            if e.lineno and e.lineno <= len(lines):
                error_line = lines[e.lineno - 1]

                # Common pattern: f'text 'word' text' -> f"text 'word' text"
                if error_line.strip().startswith('f\'') or error_line.strip().startswith('self.assert'):
                    # Try swapping quotes on this line
                    if "f'" in error_line and error_line.count("'") > 2:
                        # Find the f-string
                        fixed_line = re.sub(
                            r"f'([^']*'[^']*)'",
                            lambda m: f'f"{m.group(1)}"',
                            error_line
                        )
                        lines[e.lineno - 1] = fixed_line
                        content = '\n'.join(lines)

                        try:
                            ast.parse(content)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)
                            return True, f"Fixed line {e.lineno}"
                        except:
                            pass

            return False, f"Still has SyntaxError at line {e.lineno}: {e.msg}"

    except Exception as e:
        return False, f"Error processing: {e}"

def main():
    """Fix all test files with quote errors"""
    test_dirs = [
        Path('pygame/tests'),
        Path('tests'),
        Path('tools/testing'),
    ]

    fixed_count = 0
    error_count = 0
    results = []

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.glob('test_*.py'):
            success, message = fix_quote_errors_in_file(test_file)
            results.append((test_file, success, message))

            if success:
                fixed_count += 1
                print(f"[FIXED] {test_file}: {message}")
            elif "SyntaxError" in message:
                error_count += 1
                print(f"[ERROR] {test_file}: {message}")
            else:
                print(f"[OK] {test_file}: {message}")

    print(f"\n{'='*60}")
    print(f"Summary: {fixed_count} fixed, {error_count} still have errors")
    print(f"{'='*60}")

    if error_count > 0:
        print("\nFiles still with errors:")
        for filepath, success, message in results:
            if not success and "SyntaxError" in message:
                print(f"  - {filepath}")

if __name__ == '__main__':
    main()
