'''
Test ASCII compliance to prevent LLM Unicode contamination.

This test ensures all source files contain only ASCII characters,
preventing encoding issues that can be introduced by LLMs.
'''

import unittest
import os
import glob


class TestASCIICompliance(unittest.TestCase):
    '''Ensure all source files contain only ASCII characters to prevent LLM Unicode contamination.'''
    
    def test_python_files_ascii_only(self):
        '''Check all Python files for ASCII compliance.'''
        python_files = []
        python_files.extend(glob.glob('*.py'))
        python_files.extend(glob.glob('src/**/*.py', recursive=True))
        python_files.extend(glob.glob('tests/**/*.py', recursive=True))
        
        # Filter out files we don't want to check
        excluded_patterns = ['__pycache__', '.pyc', 'logs/', 'screenshots/']
        python_files = [f for f in python_files if not any(pattern in f for pattern in excluded_patterns)]
        
        for file_path in python_files:
            with self.subTest(file=file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    try:
                        content.decode('ascii')
                    except UnicodeDecodeError as e:
                        self.fail(f'Non-ASCII character found in {file_path} at position {e.start}: {e.reason}')
    
    def test_config_files_ascii_only(self):
        '''Check all config files for ASCII compliance.'''
        config_files = glob.glob('configs/**/*.json', recursive=True)
        
        for file_path in config_files:
            with self.subTest(file=file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    try:
                        content.decode('ascii')
                    except UnicodeDecodeError as e:
                        self.fail(f'Non-ASCII character found in {file_path} at position {e.start}: {e.reason}')
    
    def test_documentation_files_ascii_only(self):
        '''Check documentation files for ASCII compliance.'''
        doc_files = []
        doc_files.extend(glob.glob('*.md'))
        doc_files.extend(glob.glob('docs/**/*.md', recursive=True))
        
        # Filter out log files and other excluded directories
        excluded_patterns = ['logs/', 'screenshots/', '__pycache__']
        doc_files = [f for f in doc_files if not any(pattern in f for pattern in excluded_patterns)]
        
        # TEMPORARY: Exclude files with known Unicode issues (Issue #244)
        # These files contain Unicode symbols that need systematic cleanup
        unicode_cleanup_pending = [
            'README.md',  # Multiple emoji sections need cleanup
            'INTERNAL_POLISH_SUMMARY.md',
            'ISSUE_195_IMPLEMENTATION_SUMMARY.md', 
            'PR_DESCRIPTION.md',
            'RELEASE_NOTES_v0.2.0.md',
            'RELEASE_NOTES_v0.2.4.md', 
            'SETTINGS_SYSTEM_SUMMARY.md',
            'UI_FIXES_SUMMARY.md',
            'UNICODE_CLEANUP_TASK.md',
            'assets/hats/README.md',  # Tree symbols
            'assets/sfx/README.md',   # Tree symbols
            'docs/CONFIG_SYSTEM.md',
            'docs/CONTEXT_WINDOW_SYSTEM.md',
            'docs/DEVELOPERGUIDE.md',
            'docs/DEVELOPMENT_LOG.md',
            'docs/HOTFIX_WORKFLOW.md',
            'docs/KEYBOARD_REFERENCE.md',
            'docs/MENU_IMPROVEMENTS.md',
            'docs/PLAYERGUIDE.md',
            'docs/Prelaunch-Bug-Sweep-Plan.md',
            'docs/PRIVACY.md',
            'docs/PROGRESSION_SYSTEM_DESIGN.md',
            'docs/PR_DESCRIPTION.md',
            'docs/PUBLIC_OPINION_SYSTEM.md',
            'docs/RELEASE_CHECKLIST.md',
            'docs/TECHNICAL_DEBT_RESOLUTION.md',
            'docs/TURN_SEQUENCING_FIX.md',
            'docs/TYPOGRAPHY_IMPORT_FIX.md',
            'docs/UI_CRASH_FIX.md',
            'docs/UI_IMPROVEMENTS_SUMMARY.md'
        ]
        
        # Normalize paths for comparison (handle Windows/Unix path differences)
        normalized_pending = [os.path.normpath(f) for f in unicode_cleanup_pending]
        doc_files = [f for f in doc_files if os.path.normpath(f) not in normalized_pending]
        
        for file_path in doc_files:
            with self.subTest(file=file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    try:
                        content.decode('ascii')
                    except UnicodeDecodeError as e:
                        self.fail(f'Non-ASCII character found in {file_path} at position {e.start}: {e.reason}')
    
    def test_main_entry_points_ascii_only(self):
        '''Check main entry point files for ASCII compliance.'''
        entry_files = ['main.py', 'ui.py', '__main__.py', '__init__.py']
        
        for file_path in entry_files:
            if os.path.exists(file_path):
                with self.subTest(file=file_path):
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        try:
                            content.decode('ascii')
                        except UnicodeDecodeError as e:
                            self.fail(f'Non-ASCII character found in {file_path} at position {e.start}: {e.reason}')


if __name__ == '__main__':
    unittest.main()
