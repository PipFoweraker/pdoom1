"""
ASCII compliance fixer for P(Doom) codebase.

Automatically detects and fixes non-ASCII characters in Python files,
replacing them with ASCII-compatible alternatives.

Part of internal polish phase to improve code quality and compliance.
"""

import os
import re
from typing import Dict, List, Tuple


class ASCIIComplianceFixer:
    """Fixes non-ASCII characters in Python source files."""
    
    # Mapping of common non-ASCII characters to ASCII alternatives
    ASCII_REPLACEMENTS = {
        # Common Unicode quotes
        '"': '"',  # Left double quotation mark  
        '"': '"',  # Right double quotation mark
        ''''''': "'",  # Right single quotation mark
        
        # Common Unicode dashes
        '-': '-',  # En dash
        '--': '--', # Em dash
        
        # Common Unicode symbols
        '...': '...',  # Horizontal ellipsis
        'x': 'x',    # Multiplication sign
        '/': '/',    # Division sign
        
        # Common emoji that might appear in comments
        '[OK]': '[OK]',      # Check mark
        '[FAIL]': '[FAIL]',    # Cross mark
        '[WARNING]': '[WARNING]', # Warning sign
        '[TARGET]': '[TARGET]', # Direct hit
        '[LIST]': '[LIST]',   # Clipboard
        '[ORB]': '[ORB]',    # Crystal ball
        '[ALERT]': '[ALERT]',  # Rotating light
        '[SKULL]': '[SKULL]',  # Skull
        '[RADIATION]': '[RADIATION]', # Radioactive
        '[FIRE]': '[FIRE]',   # Fire
        '[EXPLOSION]': '[EXPLOSION]', # Explosion
        '[CELEBRATION]': '[CELEBRATION]', # Party popper
        '[NEWS]': '[NEWS]',   # Newspaper
        '[LIGHTNING]': '[LIGHTNING]', # Lightning bolt
        '[TOOLS]': '[TOOLS]',  # Hammer and wrench
        '[CONSTRUCTION]': '[CONSTRUCTION]', # Building construction
        '[LINK]': '[LINK]',   # Link symbol
        '[TEST]': '[TEST]',   # Test tube
        '[CHART]': '[CHART]',  # Bar chart
        '[TROPHY]': '[TROPHY]', # Trophy
        '[GAME]': '[GAME]',   # Video game controller
        '[SHIELD]': '[SHIELD]', # Shield
        '[TARGET]': '[TARGET]', # Direct hit (alternative)
        '[CYCLE]': '[CYCLE]',  # Counterclockwise arrows
        '[ROCKET]': '[ROCKET]', # Rocket
        '[PACKAGE]': '[PACKAGE]', # Package
        '[CONFETTI]': '[CONFETTI]', # Confetti ball
        '[STAR]': '[STAR]',   # Star
        '[IDEA]': '[IDEA]',   # Light bulb
        '[LOCK]': '[LOCK]',   # Lock
        
        # Math symbols
        '<=': '<=',
        '>=': '>=',
        '!=': '!=',
        '+/-': '+/-',
        
        # Currency symbols
        'EUR': 'EUR',
        'GBP': 'GBP',
        'YEN': 'YEN',
        'cents': 'cents',
        
        # Superscript/subscript numbers
        '^2': '^2',
        '^3': '^3',
        '^1': '^1',
        '_0': '_0',
        '_1': '_1',
        '_2': '_2',
        
        # Degree symbol
        'deg': 'deg',
        
        # Common accented characters (if they appear in variable names or comments)
        'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a',
        'e': 'e', 'e': 'e', 'e': 'e', 'e': 'e',
        'i': 'i', 'i': 'i', 'i': 'i', 'i': 'i',
        'o': 'o', 'o': 'o', 'o': 'o', 'o': 'o', 'o': 'o',
        'u': 'u', 'u': 'u', 'u': 'u', 'u': 'u',
        'y': 'y', 'y': 'y',
        'n': 'n', 'c': 'c',
    }
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the ASCII compliance fixer.
        
        Args:
            dry_run: If True, only report issues without fixing them
        """
        self.dry_run = dry_run
        self.issues_found = []
        self.fixes_applied = []
    
    def find_non_ascii_chars(self, content: str, filename: str) -> List[Tuple[int, str, str]]:
        """
        Find all non-ASCII characters in content.
        
        Args:
            content: File content to check
            filename: Name of file being checked
            
        Returns:
            List of (position, character, context) tuples
        """
        issues = []
        
        for i, char in enumerate(content):
            if ord(char) >= 128:  # Non-ASCII character
                # Get some context around the character
                start = max(0, i - 20)
                end = min(len(content), i + 20)
                context = content[start:end].replace('\n', '\\n')
                
                issues.append((i, char, context))
        
        return issues
    
    def fix_content(self, content: str, filename: str) -> str:
        """
        Fix non-ASCII characters in content.
        
        Args:
            content: Original content
            filename: Name of file being fixed
            
        Returns:
            Fixed content with ASCII-compatible characters
        """
        fixed_content = content
        fixes_made = []
        
        for char, replacement in self.ASCII_REPLACEMENTS.items():
            if char in fixed_content:
                count = fixed_content.count(char)
                fixed_content = fixed_content.replace(char, replacement)
                fixes_made.append((char, replacement, count))
        
        # Handle any remaining non-ASCII characters with generic replacements
        result = []
        for char in fixed_content:
            if ord(char) >= 128:
                # For any remaining non-ASCII, try to find a reasonable replacement
                if char.isalpha():
                    result.append('?')  # Unknown letter
                elif char.isdigit():
                    result.append('#')  # Unknown digit
                else:
                    result.append('?')  # Unknown symbol
                self.issues_found.append(f"{filename}: Replaced unknown character '{char}' (ord {ord(char)}) with placeholder")
            else:
                result.append(char)
        
        final_content = ''.join(result)
        
        if fixes_made:
            self.fixes_applied.extend([
                f"{filename}: Replaced '{char}' with '{replacement}' ({count} times)"
                for char, replacement, count in fixes_made
            ])
        
        return final_content
    
    def fix_file(self, filepath: str) -> bool:
        """
        Fix a single Python file.
        
        Args:
            filepath: Path to the file to fix
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            self.issues_found.append(f"Error reading {filepath}: {e}")
            return False
        
        # Check if file has non-ASCII characters
        issues = self.find_non_ascii_chars(original_content, filepath)
        
        if not issues:
            return False  # No issues found
        
        # Fix the content
        fixed_content = self.fix_content(original_content, filepath)
        
        if self.dry_run:
            self.issues_found.extend([
                f"{filepath}:{pos}: Non-ASCII character '{char}' in context: {context}"
                for pos, char, context in issues
            ])
            return False
        
        # Write the fixed content back
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        except Exception as e:
            self.issues_found.append(f"Error writing {filepath}: {e}")
            return False
    
    def fix_directory(self, directory: str) -> Dict[str, int]:
        """
        Fix all Python files in a directory and its subdirectories.
        
        Args:
            directory: Root directory to scan
            
        Returns:
            Dictionary with statistics about fixes applied
        """
        stats = {
            'files_scanned': 0,
            'files_with_issues': 0,
            'files_fixed': 0,
            'total_issues': 0
        }
        
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__, .git, and virtual environment directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', '.venv', 'venv', '.env']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    stats['files_scanned'] += 1
                    
                    issues = self.find_non_ascii_chars(
                        open(filepath, 'r', encoding='utf-8').read(),
                        filepath
                    )
                    
                    if issues:
                        stats['files_with_issues'] += 1
                        stats['total_issues'] += len(issues)
                        
                        if self.fix_file(filepath):
                            stats['files_fixed'] += 1
        
        return stats
    
    def get_report(self) -> str:
        """Generate a report of issues found and fixes applied."""
        report = []
        
        if self.issues_found:
            report.append("Issues Found:")
            for issue in self.issues_found:
                report.append(f"  - {issue}")
        
        if self.fixes_applied:
            report.append("\nFixes Applied:")
            for fix in self.fixes_applied:
                report.append(f"  - {fix}")
        
        return '\n'.join(report) if report else "No issues found."


def main():
    """Main function to run ASCII compliance fixes."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix ASCII compliance issues in Python files')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--dry-run', action='store_true', help='Only report issues without fixing')
    
    args = parser.parse_args()
    
    fixer = ASCIIComplianceFixer(dry_run=args.dry_run)
    stats = fixer.fix_directory(args.directory)
    
    print(f"ASCII Compliance Report")
    print(f"=" * 40)
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Files with issues: {stats['files_with_issues']}")
    print(f"Files fixed: {stats['files_fixed']}")
    print(f"Total issues: {stats['total_issues']}")
    print()
    print(fixer.get_report())


if __name__ == '__main__':
    main()
