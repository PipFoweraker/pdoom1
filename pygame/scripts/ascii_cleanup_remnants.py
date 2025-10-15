# !/usr/bin/env python3
"""
Intelligent ASCII Documentation Artifact Recovery Tool for P(Doom)

This specialized tool performs intelligent cleanup of leftover formatting artifacts 
from previous ASCII compliance operations, including orphaned [EMOJI] tags, malformed 
Unicode remnants, and other formatting detritus that may compromise documentation 
readability and professional presentation.

Key Features:
- Context-aware artifact identification and removal
- Intelligent [EMOJI] tag cleanup with semantic preservation
- Pattern-based artifact detection with regex optimization
- Comprehensive remnant scanning across project documentation
- Surgical cleanup operations that preserve intended meaning
- Separation of concerns from primary ASCII compliance tooling

This tool complements the main ASCII compliance fixer by handling edge cases
and cleanup scenarios that require specialized pattern matching and replacement logic.
"""

import os
import re
import argparse
from typing import Dict, List, Tuple, Union, Callable

class ASCIICleanupRemnants:
    def __init__(self):
        # Cleanup patterns for common remnants
        self.cleanup_patterns: Dict[str, str] = {
            # [EMOJI] cleanup patterns - context-aware replacements
            r'\[EMOJI\]\s*COMPLETE': 'COMPLETE',
            r'\[EMOJI\]\s*SUCCESS': 'SUCCESS', 
            r'\[EMOJI\]\s*READY': 'READY',
            r'\[EMOJI\]\s*EXCELLENT': 'EXCELLENT',
            r'\[EMOJI\]\s*YES': 'YES',
            r'\[EMOJI\]\s*GOOD': 'GOOD',
            r'\[EMOJI\]\s*DONE': 'DONE',
            r'\[EMOJI\]\s*FIXED': 'FIXED',
            r'\[EMOJI\]\s*RESOLVED': 'RESOLVED',
            
            # Status indicators - convert to simple text
            r'Status:\s*\[EMOJI\]\s*': 'Status: ',
            r'Ready for Merge:\s*\[EMOJI\]\s*': 'Ready for Merge: ',
            r'Issue Resolution:\s*\[EMOJI\]\s*': 'Issue Resolution: ',
            r'Quality Grade:\s*\[EMOJI\]\s*': 'Quality Grade: ',
            
            # List items with emoji remnants
            r'^\s*-\s*\[EMOJI\]\s*': '- ',
            r'^\s*\*\s*\[EMOJI\]\s*': '* ',
            
            # Common leftover patterns
            r'\[EMOJI\]\s*\[EMOJI\]': '',  # Double emoji artifacts
            r'\[EMOJI\]\s+': '',           # Standalone emoji with space
            r'\s+\[EMOJI\]': '',           # Trailing emoji
            r'\[EMOJI\]': '',              # Any remaining standalone emoji
            
            # Other common Unicode remnants that might slip through
            r'\[U\+2705\]': 'COMPLETE',    # Specific checkmark Unicode
            r'\[U\+2713\]': 'v',           # Check mark
            r'\[U\+2714\]': 'V',           # Heavy check mark
            r'\[U\+2192\]': '->',          # Right arrow
            r'\[U\+[0-9A-F]{4}\]': '',     # Any other Unicode remnants
        }
        
        # Context-aware replacements for better readability
        self.context_replacements = {
            # Quality assessment cleanup
            (r'### Code Quality: EXCELLENT - COMPLETE', '### Code Quality: EXCELLENT'),
            (r'### Documentation: COMPREHENSIVE - COMPLETE', '### Documentation: COMPREHENSIVE'),
            (r'### Process Adherence: EXEMPLARY - COMPLETE', '### Process Adherence: EXEMPLARY'),
            (r'### Deliverables: COMPLETE - COMPLETE', '### Deliverables: COMPLETE'),
            
            # Status cleanup
            (r'COMPLETE & READY FOR MERGE', 'COMPLETE AND READY FOR MERGE'),
            (r'SUCCESSFULLY COMPLETED', 'SUCCESSFULLY COMPLETED'),
        }

    def clean_file(self, file_path: str, dry_run: bool = False) -> Tuple[bool, int]:
        """
        Clean a single file of ASCII compliance remnants.
        
        Args:
            file_path: Path to the file to clean
            dry_run: If True, don't actually modify the file
            
        Returns:
            Tuple of (success, number_of_replacements)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            total_replacements = 0
            
            # Apply pattern-based cleanups
            for pattern, replacement in self.cleanup_patterns.items():
                # Regular string replacements
                before_count = len(re.findall(pattern, content, re.MULTILINE))
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                total_replacements += before_count
            
            # Apply context-aware replacements
            for old_text, new_text in self.context_replacements:
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    total_replacements += 1
            
            # Only write if we made changes and not in dry run mode
            if content != original_content and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, total_replacements
            elif content != original_content and dry_run:
                return True, total_replacements
            else:
                return True, 0
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, 0

    def find_remnants(self, file_path: str) -> List[str]:
        """Find remnant patterns in a file without fixing them."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            remnants = []
            
            # Check for emoji remnants
            emoji_matches = re.findall(r'\[EMOJI\][^a-zA-Z]*[A-Z]+', content)
            remnants.extend(emoji_matches)
            
            # Check for Unicode remnants
            unicode_matches = re.findall(r'\[U\+[0-9A-F]{4}\]', content)
            remnants.extend(unicode_matches)
            
            # Check for double artifacts
            double_matches = re.findall(r'\[EMOJI\]\s*\[EMOJI\]', content)
            remnants.extend(double_matches)
            
            return list(set(remnants))  # Remove duplicates
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []

    def scan_directory(self, directory: str = ".") -> Dict[str, List[str]]:
        """Scan directory for files with remnants."""
        results = {}
        
        # File patterns to check
        patterns = [
            "*.md", "*.txt", "*.rst", "*.py", "*.json", "*.yaml", "*.yml"
        ]
        
        for pattern in patterns:
            import glob
            for file_path in glob.glob(os.path.join(directory, "**", pattern), recursive=True):
                if os.path.isfile(file_path):
                    remnants = self.find_remnants(file_path)
                    if remnants:
                        results[file_path] = remnants
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Clean up ASCII compliance remnants")
    parser.add_argument("--file", help="Specific file to clean")
    parser.add_argument("--directory", default=".", help="Directory to scan/clean")
    parser.add_argument("--scan", action="store_true", help="Scan for remnants without fixing")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    
    args = parser.parse_args()
    
    cleaner = ASCIICleanupRemnants()
    
    if args.scan:
        print("Scanning for ASCII compliance remnants...")
        results = cleaner.scan_directory(args.directory)
        
        if not results:
            print("No remnants found!")
        else:
            print(f"Found remnants in {len(results)} files:")
            for file_path, remnants in results.items():
                print(f"\n{file_path}:")
                for remnant in remnants:
                    print(f"  - {repr(remnant)}")
    
    elif args.file:
        print(f"Cleaning file: {args.file}")
        success, count = cleaner.clean_file(args.file, dry_run=args.dry_run)
        
        if success:
            action = "Would fix" if args.dry_run else "Fixed"
            print(f"{action} {count} remnants in {args.file}")
        else:
            print(f"Failed to process {args.file}")
    
    else:
        # Clean all files in directory
        print(f"Cleaning directory: {args.directory}")
        results = cleaner.scan_directory(args.directory)
        
        total_files = 0
        total_replacements = 0
        
        for file_path in results.keys():
            success, count = cleaner.clean_file(file_path, dry_run=args.dry_run)
            if success and count > 0:
                total_files += 1
                total_replacements += count
                action = "Would fix" if args.dry_run else "Fixed"
                print(f"{action} {count} remnants in {file_path}")
        
        action = "Would clean" if args.dry_run else "Cleaned"
        print(f"\n{action} {total_replacements} remnants across {total_files} files")

if __name__ == "__main__":
    main()