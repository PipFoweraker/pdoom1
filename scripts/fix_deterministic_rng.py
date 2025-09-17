#!/usr/bin/env python3
"""
Fix deterministic RNG compliance in P(Doom) codebase.
Replaces 'import random' with proper deterministic RNG imports.
"""

import os
import re
import sys
from pathlib import Path

class DeterministicRNGFixer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.files_fixed = 0
        self.fixes_made = 0
        
    def should_skip_file(self, file_path):
        """Skip certain files that should keep random imports"""
        skip_patterns = [
            'tests/',
            '.venv/',
            '__pycache__/',
            'tools/dev/demo_technical_failures.py',  # Demo file - intentional
            'src/services/deterministic_rng.py',      # Core RNG module
        ]
        
        relative_path = str(file_path.relative_to(self.root_path))
        for pattern in skip_patterns:
            if pattern in relative_path:
                return True
        return False
    
    def fix_file(self, file_path):
        """Fix deterministic RNG imports in a single file"""
        if self.should_skip_file(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_in_file = 0
            
            # Pattern 1: Replace standalone 'import random'
            if re.search(r'^import random$', content, re.MULTILINE):
                content = re.sub(
                    r'^import random$',
                    'from src.services.deterministic_rng import get_rng',
                    content,
                    flags=re.MULTILINE
                )
                fixes_in_file += 1
            
            # Pattern 2: Replace 'random.' calls with 'get_rng().'
            # This is more complex - need to be careful about context
            if 'random.' in content:
                # Add get_rng call at the start of functions that use random
                content = re.sub(
                    r'(\b\w+\s*=\s*)?random\.(\w+)',
                    r'\1get_rng().\2',
                    content
                )
                fixes_in_file += 1
                
            if fixes_in_file > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Fixed {fixes_in_file} issues in {file_path}")
                self.files_fixed += 1
                self.fixes_made += fixes_in_file
                return True
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
        return False
    
    def fix_all_files(self):
        """Fix all Python files in the codebase"""
        print("Fixing deterministic RNG compliance...")
        print("=" * 50)
        
        for py_file in self.root_path.rglob('*.py'):
            self.fix_file(py_file)
            
        print("=" * 50)
        print(f"Summary: Fixed {self.fixes_made} issues in {self.files_fixed} files")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("DRY RUN - No changes will be made")
        return
        
    root_path = Path(__file__).parent.parent
    fixer = DeterministicRNGFixer(root_path)
    fixer.fix_all_files()

if __name__ == '__main__':
    main()
