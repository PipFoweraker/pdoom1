# !/usr/bin/env python3
"""
Nuclear Unicode Killer - Simple, aggressive Unicode elimination

This script finds and eliminates ALL Unicode characters from the entire project.
No fancy conversion, no preservation - just pure ASCII enforcement.
"""

import os
import sys
from pathlib import Path

def is_ascii_only(text):
    """Check if text contains only ASCII characters."""
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def kill_unicode_in_file(file_path):
    """Remove all non-ASCII characters from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        if is_ascii_only(content):
            return False, 0  # No changes needed
        
        # Nuclear approach: replace any non-ASCII with [REMOVED]
        ascii_content = ''
        removed_count = 0
        
        for char in content:
            if ord(char) <= 127:
                ascii_content += char
            else:
                # Replace with descriptive ASCII
                if char.isspace():
                    ascii_content += ' '  # Replace Unicode spaces with regular space
                else:
                    ascii_content += '[REMOVED]'
                    removed_count += 1
        
        # Write back
        with open(file_path, 'w', encoding='ascii', errors='replace') as f:
            f.write(ascii_content)
        
        return True, removed_count
    
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False, 0

def scan_project():
    """Scan entire project for Unicode violations."""
    project_root = Path(__file__).parent.parent
    violations = []
    
    # File extensions to check
    text_extensions = {'.py', '.md', '.txt', '.yml', '.yaml', '.json', '.cfg', '.ini'}
    
    for root, dirs, files in os.walk(project_root):
        # Skip common directories that shouldn't be processed
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
        
        for file in files:
            file_path = Path(root) / file
            
            # Only check text files
            if file_path.suffix.lower() in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    if not is_ascii_only(content):
                        violations.append(file_path)
                
                except Exception:
                    continue  # Skip files we can't read
    
    return violations

def main():
    """Main execution."""
    print("NUCLEAR UNICODE KILLER - Starting scan...")
    print("=" * 50)
    
    violations = scan_project()
    
    if not violations:
        print("SUCCESS: No Unicode violations found!")
        return 0
    
    print(f"FOUND: {len(violations)} files with Unicode characters")
    print()
    
    # Show first 10 violations
    print("FILES TO PROCESS:")
    for i, file_path in enumerate(violations[:10]):
        print(f"  {i+1}. {file_path}")
    
    if len(violations) > 10:
        print(f"  ... and {len(violations) - 10} more files")
    
    print()
    confirm = input("NUCLEAR OPTION: Remove ALL Unicode characters? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("ABORTED: User cancelled operation")
        return 1
    
    print()
    print("EXECUTING NUCLEAR UNICODE ELIMINATION...")
    print("-" * 50)
    
    total_removed = 0
    processed = 0
    
    for file_path in violations:
        changed, count = kill_unicode_in_file(file_path)
        if changed:
            print(f"NUKED: {file_path} ({count} characters removed)")
            total_removed += count
            processed += 1
        else:
            print(f"CLEAN: {file_path}")
    
    print("-" * 50)
    print(f"COMPLETE: Processed {processed} files")
    print(f"REMOVED: {total_removed} Unicode characters")
    print("PROJECT IS NOW ASCII-ONLY!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())