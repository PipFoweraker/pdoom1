# !/usr/bin/env python3
'''
P(Doom) Development Standards Enforcement Script

Automated checks for coding standards, documentation requirements,
and deployment readiness. Integrates with dev blog system and 
enforces project quality gates.

Usage:
    python scripts/enforce_standards.py --check-all
    python scripts/enforce_standards.py --pre-commit
    python scripts/enforce_standards.py --pre-deploy
'''

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class StandardsEnforcer:
    '''Enforces P(Doom) development standards and quality gates.'''
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = PROJECT_ROOT
        
    def check_all(self) -> bool:
        '''Run all standard checks.'''
        print('[SEARCH] P(Doom) Standards Enforcement - Full Check')
        print('=' * 50)
        
        success = True
        success &= self.check_code_quality()
        success &= self.check_documentation()
        success &= self.check_dev_blog_compliance()
        success &= self.check_ascii_compliance()
        success &= self.check_import_patterns()
        success &= self.check_test_coverage()
        
        self.print_summary()
        return success
    
    def check_code_quality(self) -> bool:
        '''Check code quality standards.'''
        print('\n[CHECKLIST] Code Quality Checks')
        print('-' * 25)
        
        success = True
        
        # Check for deterministic RNG usage
        print('[CHECK] Checking deterministic RNG usage...')
        random_imports = self._find_files_with_pattern('import random', exclude_dirs=['tests', '.venv', 'scripts'])
        # Filter out the deterministic_rng.py file which legitimately uses random
        random_imports = [r for r in random_imports if 'deterministic_rng.py' not in r[0]]
        if random_imports:
            self.errors.append('Non-deterministic random imports found:')
            for file_path, line_num, line in random_imports:
                self.errors.append(f'  {file_path}:{line_num} - {line.strip()}')
            success = False
        else:
            print('[CHECK] No problematic random imports found')
        
        # Check for hardcoded magic numbers
        print('[CHECK] Checking for magic numbers...')
        magic_numbers = self._find_magic_numbers()
        if magic_numbers:
            self.warnings.extend([f'Potential magic number: {mn}' for mn in magic_numbers[:5]])
            if len(magic_numbers) > 5:
                self.warnings.append(f'... and {len(magic_numbers) - 5} more')
        
        # Check for TODO/FIXME comments
        print('[NOTE] Checking for TODO/FIXME comments...')
        todos = self._find_files_with_pattern(r'TODO|FIXME|HACK', is_regex=True)
        if todos:
            self.warnings.append(f'Found {len(todos)} TODO/FIXME comments')
            for file_path, line_num, line in todos[:3]:
                self.warnings.append(f'  {file_path}:{line_num} - {line.strip()}')
        
        return success
    
    def check_documentation(self) -> bool:
        '''Check documentation standards.'''
        print('\n[CHECK] Documentation Checks')
        print('-' * 23)
        
        success = True
        
        # Check for CHANGELOG.md updates
        if not self._check_changelog_recent():
            self.warnings.append('CHANGELOG.md may need updates for recent changes')
        
        # Check for broken internal links
        broken_links = self._check_internal_links()
        if broken_links:
            self.warnings.extend([f'Broken internal link: {link}' for link in broken_links])
        
        # Check for outdated import examples - skip checking our own documentation
        outdated_imports = self._find_files_with_pattern('from game_state import', exclude_dirs=['.git', 'scripts'])
        if outdated_imports:
            self.errors.append('Outdated import patterns in documentation:')
            for file_path, line_num, line in outdated_imports:
                self.errors.append(f'  {file_path}:{line_num} - {line.strip()}')
            success = False
        
        return success
    
    def check_dev_blog_compliance(self) -> bool:
        '''Check dev blog system compliance.'''
        print('\n[CHECK] Dev Blog Compliance')
        print('-' * 21)
        
        success = True
        
        # Check if recent work has dev blog entry
        recent_commits = self._get_recent_commits(days=7)
        if len(recent_commits) > 5:  # Significant work without blog entry
            latest_blog = self._get_latest_blog_entry()
            if not latest_blog or not self._is_recent_blog_entry(latest_blog):
                self.warnings.append('Consider creating dev blog entry for recent work')
        
        # Check blog entry format compliance
        blog_errors = self._validate_blog_entries()
        if blog_errors:
            self.warnings.extend(blog_errors)
        
        return success
    
    def check_ascii_compliance(self) -> bool:
        '''Check ASCII-only compliance and optionally fix issues.'''
        print('\n[ASCII] ASCII Compliance Check')
        print('-' * 24)
        
        success = True
        
        # First, check for Unicode content
        unicode_files = self._find_unicode_content()
        if unicode_files:
            print(f'[WARNING] Found {len(unicode_files)} files with Unicode content')
            
            # Try to auto-fix using intelligent ASCII converter
            try:
                converter_path = self.project_root / 'scripts' / 'intelligent_ascii_converter.py'
                if converter_path.exists():
                    print('[INFO] Attempting auto-fix with intelligent ASCII converter...')
                    
                    # Run the intelligent converter
                    import subprocess
                    result = subprocess.run([
                        sys.executable, str(converter_path), '--dry-run'
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if result.returncode == 0:
                        if 'All files are ASCII compliant' in result.stdout:
                            print('[SUCCESS] All files are already ASCII compliant')
                        else:
                            print('[ACTION] Unicode characters found. Run the following to fix:')
                            print(f'  python {converter_path}')
                            self.warnings.append('Unicode content can be auto-fixed with intelligent ASCII converter')
                            success = False
                    else:
                        print(f'[ERROR] ASCII converter failed: {result.stderr}')
                        self.errors.append('ASCII compliance check failed')
                        success = False
                else:
                    # Fallback to old behavior
                    self.errors.append('Non-ASCII content found:')
                    for file_path, line_num, char in unicode_files:
                        self.errors.append(f'  {file_path}:{line_num} - Non-ASCII character: {repr(char)}')
                    success = False
                    
            except Exception as e:
                print(f'[ERROR] ASCII compliance check failed: {e}')
                self.errors.append(f'ASCII compliance check error: {e}')
                success = False
        else:
            print('[SUCCESS] All content is ASCII-compliant')
        
        return success
    
    def check_import_patterns(self) -> bool:
        '''Check import pattern consistency.'''
        print('\n[CHECK] Import Pattern Check')
        print('-' * 22)
        
        success = True
        
        # Check for consistent src.core imports
        inconsistent_imports = []
        
        # Look for old-style imports that should use src.core (skip our own documentation)
        old_patterns = [
            'from game_state import',
            'from actions import', 
            'from events import'
        ]
        
        for pattern in old_patterns:
            matches = self._find_files_with_pattern(pattern, exclude_dirs=['docs', '.git', 'scripts'])
            inconsistent_imports.extend(matches)
        
        if inconsistent_imports:
            self.errors.append('Inconsistent import patterns found:')
            for file_path, line_num, line in inconsistent_imports:
                self.errors.append(f'  {file_path}:{line_num} - {line.strip()}')
            success = False
        
        return success
    
    def check_test_coverage(self) -> bool:
        '''Check test coverage standards.'''
        print('\n[CHECK] Test Coverage Check')
        print('-' * 21)
        
        # This would integrate with pytest coverage
        print('[INFO]  Test coverage check - placeholder (integrate with pytest-cov)')
        return True
    
    def pre_commit_check(self) -> bool:
        '''Quick checks before commit.'''
        print('[ROCKET] Pre-commit Standards Check')
        print('=' * 29)
        
        success = True
        success &= self.check_ascii_compliance()
        success &= self.check_import_patterns()
        
        # Quick syntax check
        print('\n[CHECK] Python Syntax Check')
        if not self._check_python_syntax():
            success = False
        
        self.print_summary()
        return success
    
    def pre_deploy_check(self) -> bool:
        '''Comprehensive checks before deployment.'''
        print('[CHECK] Pre-deployment Standards Check')
        print('=' * 33)
        
        success = self.check_all()
        
        # Additional deployment-specific checks
        print('\n[CHECK] Deployment Readiness')
        print('-' * 20)
        
        # Check version consistency
        if not self._check_version_consistency():
            self.errors.append('Version inconsistency detected')
            success = False
        
        # Check for debug code
        debug_code = self._find_debug_code()
        if debug_code:
            self.warnings.extend([f'Debug code found: {dc}' for dc in debug_code])
        
        self.print_summary()
        return success
    
    # Helper methods
    def _find_files_with_pattern(self, pattern: str, exclude_dirs: List[str] = None, is_regex: bool = False) -> List[Tuple[str, int, str]]:
        '''Find files containing a specific pattern.'''
        import re
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', '.venv', 'node_modules']
        
        matches = []
        pattern_re = re.compile(pattern) if is_regex else None
        
        for py_file in self.project_root.rglob('*.py'):
            if any(exclude_dir in str(py_file) for exclude_dir in exclude_dirs):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if is_regex:
                            if pattern_re.search(line):
                                matches.append((str(py_file.relative_to(self.project_root)), line_num, line))
                        else:
                            if pattern in line:
                                matches.append((str(py_file.relative_to(self.project_root)), line_num, line))
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return matches
    
    def _find_magic_numbers(self) -> List[str]:
        '''Find potential magic numbers (hardcoded values).'''
        # Simplified implementation - would need more sophisticated parsing
        return []
    
    def _check_changelog_recent(self) -> bool:
        '''Check if CHANGELOG.md has recent updates.'''
        changelog_path = self.project_root / 'CHANGELOG.md'
        if not changelog_path.exists():
            return False
        
        # Check if modified in last 7 days
        import time
        mod_time = changelog_path.stat().st_mtime
        return (time.time() - mod_time) < (7 * 24 * 3600)
    
    def _check_internal_links(self) -> List[str]:
        '''Check for broken internal documentation links.'''
        # Placeholder - would parse markdown files for internal links
        return []
    
    def _get_recent_commits(self, days: int = 7) -> List[str]:
        '''Get recent git commits.'''
        try:
            result = subprocess.run(
                ['git', 'log', f'--since={days} days ago', '--oneline'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.SubprocessError:
            return []
    
    def _get_latest_blog_entry(self) -> Optional[str]:
        '''Get latest dev blog entry.'''
        blog_dir = self.project_root / 'dev-blog' / 'entries'
        if not blog_dir.exists():
            return None
        
        blog_files = sorted(blog_dir.glob('*.md'), reverse=True)
        return str(blog_files[0]) if blog_files else None
    
    def _is_recent_blog_entry(self, blog_file: str) -> bool:
        '''Check if blog entry is recent.'''
        # Parse date from filename or file content
        return True  # Placeholder
    
    def _validate_blog_entries(self) -> List[str]:
        '''Validate blog entry format compliance.'''
        return []  # Placeholder
    
    def _find_unicode_content(self) -> List[Tuple[str, int, str]]:
        '''Find non-ASCII content in files.'''
        unicode_issues = []
        
        # File patterns to check
        patterns = ['*.py', '*.md', '*.txt', '*.json', '*.yaml', '*.yml', '*.toml', '*.cfg', '*.sh']
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}
        
        for pattern in patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip files in excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            for char in line:
                                if ord(char) > 127:  # Non-ASCII
                                    unicode_issues.append((
                                        str(file_path.relative_to(self.project_root)), 
                                        line_num, 
                                        char
                                    ))
                                    break  # One per line is enough
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return unicode_issues
    
    def _check_python_syntax(self) -> bool:
        '''Check Python syntax for all .py files.'''
        import ast
        
        syntax_errors = []
        for py_file in self.project_root.rglob('*.py'):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read(), filename=str(py_file))
            except SyntaxError as e:
                syntax_errors.append(f'{py_file.relative_to(self.project_root)}:{e.lineno} - {e.msg}')
        
        if syntax_errors:
            self.errors.extend(syntax_errors)
            return False
        
        print('[CHECK] All Python files have valid syntax')
        return True
    
    def _check_version_consistency(self) -> bool:
        '''Check version consistency across files.'''
        # Would check version.py, pyproject.toml, etc.
        return True  # Placeholder
    
    def _find_debug_code(self) -> List[str]:
        '''Find debug code that shouldn't be in production.'''
        debug_patterns = ['print(', 'console.log', 'debugger', 'pdb.set_trace']
        debug_code = []
        
        for pattern in debug_patterns:
            matches = self._find_files_with_pattern(pattern, exclude_dirs=['tests', 'debug', 'dev-blog'])
            debug_code.extend([f'{m[0]}:{m[1]}' for m in matches])
        
        return debug_code
    
    def print_summary(self):
        '''Print check summary.'''
        print('\n' + '=' * 50)
        print('[CHART] STANDARDS CHECK SUMMARY')
        print('=' * 50)
        
        if self.errors:
            print(f'[ERROR] ERRORS ({len(self.errors)}):')
            for error in self.errors:
                print(f'   {error}')
        
        if self.warnings:
            print(f'\n[WARNING] WARNINGS ({len(self.warnings)}):')
            for warning in self.warnings:
                print(f'   {warning}')
        
        if not self.errors and not self.warnings:
            print('[SUCCESS] All checks passed!')
        
        print(f'\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings')


def main():
    parser = argparse.ArgumentParser(description='P(Doom) Development Standards Enforcement')
    parser.add_argument('--check-all', action='store_true', help='Run all standard checks')
    parser.add_argument('--pre-commit', action='store_true', help='Run pre-commit checks')
    parser.add_argument('--pre-deploy', action='store_true', help='Run pre-deployment checks')
    
    args = parser.parse_args()
    
    enforcer = StandardsEnforcer()
    
    if args.pre_commit:
        success = enforcer.pre_commit_check()
    elif args.pre_deploy:
        success = enforcer.pre_deploy_check()
    else:  # Default to check-all
        success = enforcer.check_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
