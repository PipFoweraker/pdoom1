# !/usr/bin/env python3
'''
Pre-Version Bump Quality Checks for P(Doom)

Runs comprehensive quality checks before version increments to ensure
the codebase meets professional standards. Integrates with version
management workflow.

Usage:
    python scripts/pre_version_bump.py --target-version v0.10.1
    python scripts/pre_version_bump.py --auto-fix
    python scripts/pre_version_bump.py --check-only
'''

import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class PreVersionBumpChecker:
    '''Comprehensive quality checks for version increments.'''
    
    def __init__(self, auto_fix: bool = False):
        self.auto_fix = auto_fix
        self.project_root = PROJECT_ROOT
        self.issues_found = []
        self.fixes_applied = []
        
    def run_all_checks(self, target_version: Optional[str] = None) -> bool:
        '''Run all pre-version-bump checks.'''
        print('=' * 60)
        print('P(DOOM) PRE-VERSION BUMP QUALITY CHECKS')
        print('=' * 60)
        
        if target_version:
            print(f'Target Version: {target_version}')
        print(f'Auto-fix Mode: {'ENABLED' if self.auto_fix else 'DISABLED'}')
        print(f'Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
        print()
        
        success = True
        
        # 1. ASCII Compliance Check
        success &= self._check_ascii_compliance()
        
        # 2. Development Standards Check
        success &= self._check_development_standards()
        
        # 3. Test Suite Validation
        success &= self._check_test_suite()
        
        # 4. Documentation Consistency
        success &= self._check_documentation()
        
        # 5. Version Consistency Check
        if target_version:
            success &= self._check_version_consistency(target_version)
        
        # Print summary
        self._print_summary(success)
        
        return success
    
    def _check_ascii_compliance(self) -> bool:
        '''Check and optionally fix ASCII compliance.'''
        print('STEP 1: ASCII Compliance Check')
        print('-' * 30)
        
        try:
            converter_path = self.project_root / 'scripts' / 'intelligent_ascii_converter.py'
            
            # Run dry-run first
            result = subprocess.run([
                sys.executable, str(converter_path), '--dry-run'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                if 'All files are ASCII compliant' in result.stdout:
                    print('SUCCESS All files are ASCII compliant')
                    return True
                else:
                    print('WARNING Unicode characters found')
                    self.issues_found.append('Unicode characters detected')
                    
                    if self.auto_fix:
                        print('INFO Applying automatic ASCII fixes...')
                        fix_result = subprocess.run([
                            sys.executable, str(converter_path)
                        ], capture_output=True, text=True, cwd=self.project_root)
                        
                        if fix_result.returncode == 0:
                            print('SUCCESS ASCII fixes applied successfully')
                            self.fixes_applied.append('ASCII compliance auto-fixed')
                            return True
                        else:
                            print(f'ERROR ASCII fix failed: {fix_result.stderr}')
                            return False
                    else:
                        print('ACTION Run: python scripts/intelligent_ascii_converter.py')
                        return False
            else:
                print(f'ERROR ASCII check failed: {result.stderr}')
                return False
                
        except Exception as e:
            print(f'ERROR ASCII compliance check failed: {e}')
            return False
    
    def _check_development_standards(self) -> bool:
        '''Check development standards compliance.'''
        print('\nSTEP 2: Development Standards Check')
        print('-' * 35)
        
        try:
            standards_path = self.project_root / 'scripts' / 'enforce_standards.py'
            
            result = subprocess.run([
                sys.executable, str(standards_path), '--check-all'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print('SUCCESS All development standards met')
                return True
            else:
                print('WARNING Standards violations detected')
                print('Details:')
                print(result.stdout)
                self.issues_found.append('Development standards violations')
                return False
                
        except Exception as e:
            print(f'ERROR Standards check failed: {e}')
            return False
    
    def _check_test_suite(self) -> bool:
        '''Validate test suite execution.'''
        print('\nSTEP 3: Test Suite Validation')
        print('-' * 26)
        
        try:
            # Run a quick test to ensure test suite is functional
            result = subprocess.run([
                sys.executable, '-m', 'unittest', 'discover', 'tests', '-v', '--failfast'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=120)
            
            if result.returncode == 0:
                print('SUCCESS Test suite passed')
                return True
            else:
                print('ERROR Test suite failures detected')
                print('Details:')
                print(result.stdout[-1000:])  # Last 1000 chars
                self.issues_found.append('Test suite failures')
                return False
                
        except subprocess.TimeoutExpired:
            print('WARNING Test suite timeout (>120s)')
            self.issues_found.append('Test suite performance issue')
            return False
        except Exception as e:
            print(f'ERROR Test suite check failed: {e}')
            return False
    
    def _check_documentation(self) -> bool:
        '''Check documentation consistency.'''
        print('\nSTEP 4: Documentation Consistency')
        print('-' * 30)
        
        # Basic checks for key documentation files
        required_docs = [
            'README.md',
            'docs/DEVELOPERGUIDE.md', 
            'docs/PLAYERGUIDE.md',
            'CHANGELOG.md'
        ]
        
        missing_docs = []
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)
        
        if missing_docs:
            print(f'ERROR Missing documentation: {', '.join(missing_docs)}')
            self.issues_found.append(f'Missing docs: {missing_docs}')
            return False
        
        print('SUCCESS Core documentation files present')
        return True
    
    def _check_version_consistency(self, target_version: str) -> bool:
        '''Check version consistency across files.'''
        print(f'\nSTEP 5: Version Consistency Check')
        print('-' * 29)
        
        try:
            # Check current version
            from scripts.lib.services.version import get_display_version
            current_version = get_display_version()
            
            print(f'Current Version: {current_version}')
            print(f'Target Version:  {target_version}')
            
            # Basic validation that target version is different
            if current_version == target_version:
                print('WARNING Target version same as current version')
                self.issues_found.append('Version not incremented')
                return False
            
            print('SUCCESS Version increment planned')
            return True
            
        except Exception as e:
            print(f'ERROR Version check failed: {e}')
            return False
    
    def _print_summary(self, success: bool) -> None:
        '''Print final summary.'''
        print('\n' + '=' * 60)
        print('QUALITY CHECK SUMMARY')
        print('=' * 60)
        
        if success:
            print('SUCCESS All quality checks passed')
            if self.fixes_applied:
                print('\nFixes Applied:')
                for fix in self.fixes_applied:
                    print(f'  - {fix}')
            print('\nREADY for version increment')
        else:
            print('ERROR Quality checks failed')
            if self.issues_found:
                print('\nIssues Found:')
                for issue in self.issues_found:
                    print(f'  - {issue}')
            print('\nNOT READY for version increment')
        
        print(f'\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')


def main():
    parser = argparse.ArgumentParser(
        description='Pre-version bump quality checks for P(Doom)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--target-version', 
                       help='Target version for increment (e.g., v0.10.1)')
    parser.add_argument('--auto-fix', action='store_true',
                       help='Automatically fix issues where possible')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check, never fix (overrides --auto-fix)')
    
    args = parser.parse_args()
    
    # Override auto-fix if check-only is specified
    auto_fix = args.auto_fix and not args.check_only
    
    checker = PreVersionBumpChecker(auto_fix=auto_fix)
    success = checker.run_all_checks(args.target_version)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())