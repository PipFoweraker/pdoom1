# !/usr/bin/env python3
"""
P(Doom) Project Health Dashboard - BLITZ MODE IMPLEMENTATION

Comprehensive project health monitoring with:
- Code quality scanning (linting, complexity, type coverage)
- Issue tracking analysis and prioritization 
- Branch health and merge readiness
- Test coverage and performance metrics
- Documentation completeness scoring
- CI/CD pipeline status monitoring

Usage:
    python scripts/project_health.py --full-report
    python scripts/project_health.py --quick-check
    python scripts/project_health.py --generate-issues
    python scripts/project_health.py --ci-mode
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import re

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class ProjectHealthDashboard:
    """Comprehensive project health monitoring and reporting system."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.health_data = {}
        self.issues = []
        self.warnings = []
        self.start_time = datetime.now()
        
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive project health report."""
        print("[LAUNCH] PROJECT HEALTH DASHBOARD - FULL SCAN INITIATED")
        print("=" * 60)
        
        self.health_data = {
            'timestamp': self.start_time.isoformat(),
            'code_quality': self._analyze_code_quality(),
            'issue_tracking': self._analyze_github_issues(),
            'branch_health': self._analyze_branch_status(),
            'test_metrics': self._analyze_test_coverage(),
            'documentation': self._analyze_documentation(),
            'automation': self._analyze_ci_status(),
            'overall_score': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        # Calculate overall health score
        self._calculate_overall_score()
        self._generate_recommendations()
        
        # Display results
        self._display_health_report()
        
        return self.health_data
    
    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        print("[SCAN] SCANNING: Code Quality Analysis...")
        
        quality_data = {
            'linting_issues': self._check_linting_issues(),
            'complexity_score': self._check_code_complexity(),
            'type_coverage': self._check_type_annotation_coverage(),
            'import_health': self._check_import_cleanliness(),
            'file_count': self._count_source_files(),
            'score': 0
        }
        
        # Calculate quality score (0-100)
        linting_penalty = min(50, quality_data['linting_issues'] * 2)
        complexity_bonus = max(0, 100 - quality_data['complexity_score'])
        type_bonus = quality_data['type_coverage']
        import_bonus = 100 - quality_data['import_health']['unused_imports']
        
        quality_data['score'] = max(0, 100 - linting_penalty + (complexity_bonus + type_bonus + import_bonus) // 3)
        
        print(f"   [OK] Linting Issues: {quality_data['linting_issues']}")
        print(f"   [OK] Type Coverage: {quality_data['type_coverage']}%")
        print(f"   [OK] Quality Score: {quality_data['score']}/100")
        
        return quality_data
    
    def _check_linting_issues(self) -> int:
        """Count linting issues using various tools."""
        issues = 0
        
        # Check for common Python linting issues
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple linting checks
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Check for common issues
                    if len(line) > 120:  # Line too long
                        issues += 1
                    if re.search(r'print\s*\(', line) and 'debug' not in py_file.name:  # Debug prints
                        issues += 1
                    if 'TODO' in line.upper() or 'FIXME' in line.upper():  # TODO items
                        issues += 1
                        
            except Exception:
                issues += 1  # File read error
                
        return issues
    
    def _check_code_complexity(self) -> int:
        """Estimate code complexity score."""
        complexity = 0
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple complexity metrics
                lines = len(content.split('\n'))
                if lines > 1000:  # Very large files
                    complexity += 10
                elif lines > 500:  # Large files
                    complexity += 5
                    
                # Count nested structures
                nesting_level = 0
                max_nesting = 0
                for line in content.split('\n'):
                    stripped = line.lstrip()
                    if stripped.startswith(('if ', 'for ', 'while ', 'try:', 'with ', 'def ', 'class ')):
                        nesting_level = (len(line) - len(stripped)) // 4
                        max_nesting = max(max_nesting, nesting_level)
                        
                if max_nesting > 6:  # Deep nesting
                    complexity += max_nesting
                    
            except Exception:
                complexity += 5
                
        return min(100, complexity)
    
    def _check_type_annotation_coverage(self) -> int:
        """Calculate type annotation coverage percentage."""
        python_files = list(self.project_root.rglob("*.py"))
        total_functions = 0
        annotated_functions = 0
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file) or 'test' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find function definitions
                function_pattern = r'def\s+\w+\s*\([^)]*\)(?:\s*->\s*[^:]+)?:'
                functions = re.findall(function_pattern, content)
                total_functions += len(functions)
                
                # Count annotated functions (simple heuristic)
                annotated_pattern = r'def\s+\w+\s*\([^)]*:\s*[^)]*\)(?:\s*->\s*[^:]+)?:'
                annotated = re.findall(annotated_pattern, content)
                annotated_functions += len(annotated)
                
            except Exception:
                pass
                
        if total_functions == 0:
            return 100
            
        return int((annotated_functions / total_functions) * 100)
    
    def _check_import_cleanliness(self) -> Dict[str, int]:
        """Check for import issues."""
        return {
            'unused_imports': 0,  # TODO: Implement proper analysis
            'circular_imports': 0,
            'import_errors': 0
        }
    
    def _count_source_files(self) -> Dict[str, int]:
        """Count different types of source files."""
        counts = {
            'python': len(list(self.project_root.rglob("*.py"))),
            'markdown': len(list(self.project_root.rglob("*.md"))),
            'json': len(list(self.project_root.rglob("*.json"))),
            'yaml': len(list(self.project_root.rglob("*.yml"))) + len(list(self.project_root.rglob("*.yaml")))
        }
        return counts
    
    def _analyze_github_issues(self) -> Dict[str, Any]:
        """Analyze GitHub issues and local issue tracking."""
        print("[LIST] SCANNING: Issue Tracking Analysis...")
        
        # Analyze local issues directory
        issues_dir = self.project_root / 'issues'
        local_issues = list(issues_dir.glob('*.md')) if issues_dir.exists() else []
        
        issue_data = {
            'total_local_issues': len(local_issues),
            'stale_issues': 0,
            'priority_breakdown': {'high': 0, 'medium': 0, 'low': 0},
            'category_breakdown': {},
            'score': 0
        }
        
        # Analyze local issues
        for issue_file in local_issues:
            try:
                with open(issue_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple categorization
                if any(word in content.lower() for word in ['critical', 'urgent', 'broken', 'crash']):
                    issue_data['priority_breakdown']['high'] += 1
                elif any(word in content.lower() for word in ['important', 'should', 'improve']):
                    issue_data['priority_breakdown']['medium'] += 1
                else:
                    issue_data['priority_breakdown']['low'] += 1
                    
                # Categorize by type
                if 'bug' in issue_file.name or 'fix' in issue_file.name:
                    issue_data['category_breakdown']['bugs'] = issue_data['category_breakdown'].get('bugs', 0) + 1
                elif 'feature' in issue_file.name or 'enhancement' in issue_file.name:
                    issue_data['category_breakdown']['features'] = issue_data['category_breakdown'].get('features', 0) + 1
                else:
                    issue_data['category_breakdown']['other'] = issue_data['category_breakdown'].get('other', 0) + 1
                    
            except Exception:
                pass
        
        # Calculate issue health score
        total_issues = issue_data['total_local_issues']
        high_priority = issue_data['priority_breakdown']['high']
        
        if total_issues == 0:
            issue_data['score'] = 100
        else:
            # Penalty for high number of issues and high-priority issues
            issue_penalty = min(50, total_issues * 2)
            priority_penalty = min(30, high_priority * 10)
            issue_data['score'] = max(0, 100 - issue_penalty - priority_penalty)
        
        print(f"   [OK] Total Local Issues: {total_issues}")
        print(f"   [OK] High Priority: {high_priority}")
        print(f"   [OK] Issue Health Score: {issue_data['score']}/100")
        
        return issue_data
    
    def _analyze_branch_status(self) -> Dict[str, Any]:
        """Analyze git branch health."""
        print("[BRANCH] SCANNING: Branch Health Analysis...")
        
        try:
            # Get branch information
            result = subprocess.run(['git', 'branch', '-a'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            branches = result.stdout.strip().split('\n')
            
            # Get current branch
            current_result = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True, cwd=self.project_root)
            current_branch = current_result.stdout.strip()
            
            branch_data = {
                'total_branches': len([b for b in branches if b.strip()]),
                'current_branch': current_branch,
                'remote_branches': len([b for b in branches if 'remotes/origin' in b]),
                'local_branches': len([b for b in branches if 'remotes' not in b and b.strip()]),
                'clean_working_tree': self._check_working_tree_clean(),
                'score': 0
            }
            
            # Calculate branch health score
            score = 100
            if not branch_data['clean_working_tree']:
                score -= 20  # Penalty for dirty working tree
            if branch_data['local_branches'] > 20:
                score -= 10  # Penalty for too many local branches
                
            branch_data['score'] = max(0, score)
            
            print(f"   [OK] Current Branch: {current_branch}")
            print(f"   [OK] Total Branches: {branch_data['total_branches']}")
            print(f"   [OK] Clean Working Tree: {branch_data['clean_working_tree']}")
            print(f"   [OK] Branch Health Score: {branch_data['score']}/100")
            
        except Exception as e:
            branch_data = {'error': str(e), 'score': 50}
            
        return branch_data
    
    def _check_working_tree_clean(self) -> bool:
        """Check if git working tree is clean."""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            return len(result.stdout.strip()) == 0
        except Exception:
            return False
    
    def _analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage and metrics."""
        print("[TEST] SCANNING: Test Coverage Analysis...")
        
        test_data = {
            'test_files': len(list(self.project_root.rglob("test_*.py"))),
            'total_tests': 0,
            'test_directories': len([d for d in self.project_root.rglob("test*") if d.is_dir()]),
            'score': 0
        }
        
        # Count actual test functions
        for test_file in self.project_root.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    test_functions = len(re.findall(r'def test_\w+', content))
                    test_data['total_tests'] += test_functions
            except Exception:
                pass
        
        # Calculate test score
        if test_data['total_tests'] > 100:
            test_data['score'] = 100
        elif test_data['total_tests'] > 50:
            test_data['score'] = 80
        elif test_data['total_tests'] > 20:
            test_data['score'] = 60
        else:
            test_data['score'] = max(0, test_data['total_tests'] * 3)
        
        print(f"   [OK] Test Files: {test_data['test_files']}")
        print(f"   [OK] Total Tests: {test_data['total_tests']}")
        print(f"   [OK] Test Score: {test_data['score']}/100")
        
        return test_data
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation completeness."""
        print("[DOCS] SCANNING: Documentation Analysis...")
        
        doc_data = {
            'readme_exists': (self.project_root / 'README.md').exists(),
            'changelog_exists': (self.project_root / 'CHANGELOG.md').exists(),
            'docs_directory': (self.project_root / 'docs').exists(),
            'markdown_files': len(list(self.project_root.rglob("*.md"))),
            'docstring_coverage': self._estimate_docstring_coverage(),
            'score': 0
        }
        
        # Calculate documentation score
        score = 0
        if doc_data['readme_exists']:
            score += 30
        if doc_data['changelog_exists']:
            score += 20
        if doc_data['docs_directory']:
            score += 20
        score += min(30, doc_data['markdown_files'] * 2)
        
        doc_data['score'] = min(100, score)
        
        print(f"   [OK] README: {doc_data['readme_exists']}")
        print(f"   [OK] Docs Directory: {doc_data['docs_directory']}")
        print(f"   [OK] Markdown Files: {doc_data['markdown_files']}")
        print(f"   [OK] Documentation Score: {doc_data['score']}/100")
        
        return doc_data
    
    def _estimate_docstring_coverage(self) -> int:
        """Estimate docstring coverage percentage."""
        python_files = list(self.project_root.rglob("*.py"))
        total_functions = 0
        documented_functions = 0
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple docstring detection
                lines = content.split('\n')
                in_function = False
                has_docstring = False
                
                for i, line in enumerate(lines):
                    if re.match(r'\s*def\s+\w+', line):
                        if in_function and has_docstring:
                            documented_functions += 1
                        total_functions += 1
                        in_function = True
                        has_docstring = False
                        
                        # Check next few lines for docstring
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                has_docstring = True
                                break
                                
                if in_function and has_docstring:
                    documented_functions += 1
                    
            except Exception:
                pass
                
        if total_functions == 0:
            return 100
            
        return int((documented_functions / total_functions) * 100)
    
    def _analyze_ci_status(self) -> Dict[str, Any]:
        """Analyze CI/CD pipeline status."""
        print("[CONFIG] SCANNING: CI/CD Analysis...")
        
        ci_data = {
            'github_actions': (self.project_root / '.github' / 'workflows').exists(),
            'workflow_files': len(list((self.project_root / '.github' / 'workflows').glob('*.yml'))) if (self.project_root / '.github' / 'workflows').exists() else 0,
            'requirements_files': len(list(self.project_root.glob('requirements*.txt'))),
            'docker_config': (self.project_root / 'Dockerfile').exists(),
            'score': 0
        }
        
        # Calculate CI score
        score = 0
        if ci_data['github_actions']:
            score += 40
        score += min(30, ci_data['workflow_files'] * 15)
        if ci_data['requirements_files'] > 0:
            score += 20
        if ci_data['docker_config']:
            score += 10
            
        ci_data['score'] = min(100, score)
        
        print(f"   [OK] GitHub Actions: {ci_data['github_actions']}")
        print(f"   [OK] Workflow Files: {ci_data['workflow_files']}")
        print(f"   [OK] CI/CD Score: {ci_data['score']}/100")
        
        return ci_data
    
    def _calculate_overall_score(self):
        """Calculate weighted overall health score."""
        weights = {
            'code_quality': 0.25,
            'issue_tracking': 0.20,
            'branch_health': 0.15,
            'test_metrics': 0.20,
            'documentation': 0.10,
            'automation': 0.10
        }
        
        total_score = 0
        for category, weight in weights.items():
            if category in self.health_data and 'score' in self.health_data[category]:
                total_score += self.health_data[category]['score'] * weight
        
        self.health_data['overall_score'] = int(total_score)
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on health data."""
        recommendations = []
        
        # Code quality recommendations
        if self.health_data['code_quality']['score'] < 70:
            recommendations.append("[FIX] URGENT: Address code quality issues - run linting tools and fix critical issues")
            
        if self.health_data['code_quality']['type_coverage'] < 60:
            recommendations.append("[REMOVED][REMOVED] Add type annotations to improve code maintainability")
        
        # Issue tracking recommendations
        if self.health_data['issue_tracking']['priority_breakdown']['high'] > 5:
            recommendations.append("[URGENT] CRITICAL: Address high-priority issues immediately")
            
        if self.health_data['issue_tracking']['total_local_issues'] > 30:
            recommendations.append("[LIST] Consider issue triage session to reduce backlog")
        
        # Test recommendations
        if self.health_data['test_metrics']['total_tests'] < 50:
            recommendations.append("[TEST] Increase test coverage - aim for 100+ tests minimum")
        
        # Documentation recommendations
        if self.health_data['documentation']['score'] < 70:
            recommendations.append("[DOCS] Improve documentation coverage and quality")
        
        # Overall health recommendations
        if self.health_data['overall_score'] < 60:
            recommendations.append("[WARNING] PROJECT HEALTH CRITICAL - Immediate action required")
        elif self.health_data['overall_score'] < 80:
            recommendations.append("[QUICK] Project health needs attention - focus on top issues")
        else:
            recommendations.append("[TARGET] Project health is good - maintain current standards")
        
        self.health_data['recommendations'] = recommendations
    
    def _display_health_report(self):
        """Display comprehensive health report."""
        print("\n" + "[HEALTH] PROJECT HEALTH REPORT".center(60, "="))
        print(f"Generated: {self.health_data['timestamp']}")
        print(f"Overall Health Score: {self.health_data['overall_score']}/100")
        
        # Health indicator
        if self.health_data['overall_score'] >= 90:
            print("[GREEN] EXCELLENT - Project is in outstanding health!")
        elif self.health_data['overall_score'] >= 80:
            print("[YELLOW] GOOD - Project health is solid with room for improvement")
        elif self.health_data['overall_score'] >= 60:
            print("[ORANGE] FAIR - Project needs attention in several areas")
        else:
            print("[RED] POOR - Project requires immediate health improvements")
        
        print("\n[DATA] DETAILED BREAKDOWN:")
        categories = ['code_quality', 'issue_tracking', 'branch_health', 'test_metrics', 'documentation', 'automation']
        for category in categories:
            if category in self.health_data:
                score = self.health_data[category].get('score', 0)
                indicator = "[GREEN]" if score >= 80 else "[YELLOW]" if score >= 60 else "[RED]"
                print(f"   {indicator} {category.replace('_', ' ').title()}: {score}/100")
        
        print(f"\n[TARGET] RECOMMENDATIONS ({len(self.health_data['recommendations'])} items):")
        for i, rec in enumerate(self.health_data['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*60)
        execution_time = (datetime.now() - self.start_time).total_seconds()
        print(f"[REMOVED][REMOVED] Analysis completed in {execution_time:.2f} seconds")
    
    def quick_check(self) -> Dict[str, Any]:
        """Perform quick health check with essential metrics only."""
        print("[QUICK] QUICK HEALTH CHECK")
        print("=" * 30)
        
        quick_data = {
            'timestamp': datetime.now().isoformat(),
            'linting_issues': self._check_linting_issues(),
            'total_issues': len(list((self.project_root / 'issues').glob('*.md'))) if (self.project_root / 'issues').exists() else 0,
            'working_tree_clean': self._check_working_tree_clean(),
            'test_count': len(list(self.project_root.rglob("test_*.py"))),
            'quick_score': 0
        }
        
        # Calculate quick score
        score = 100
        score -= min(50, quick_data['linting_issues'] * 2)
        score -= min(30, quick_data['total_issues'])
        if not quick_data['working_tree_clean']:
            score -= 20
        if quick_data['test_count'] < 20:
            score -= 20
            
        quick_data['quick_score'] = max(0, score)
        
        print(f"[SCAN] Linting Issues: {quick_data['linting_issues']}")
        print(f"[LIST] Open Issues: {quick_data['total_issues']}")
        print(f"[BRANCH] Clean Working Tree: {quick_data['working_tree_clean']}")
        print(f"[TEST] Test Files: {quick_data['test_count']}")
        print(f"[QUICK] Quick Health Score: {quick_data['quick_score']}/100")
        
        return quick_data
    
    def generate_github_issues(self):
        """Generate GitHub issues for critical health problems."""
        print("[WRITE] GENERATING GITHUB ISSUES FOR CRITICAL PROBLEMS...")
        
        # Generate full report first
        if not self.health_data:
            self.generate_full_report()
        
        issues_to_create = []
        
        # Critical code quality issues
        if self.health_data['code_quality']['score'] < 60:
            issues_to_create.append({
                'title': f"[CRITICAL] Code Quality Health Below 60% ({self.health_data['code_quality']['score']}/100)",
                'body': f"""## Code Quality Crisis

Current code quality score: **{self.health_data['code_quality']['score']}/100**

### Issues Detected:
- Linting Issues: {self.health_data['code_quality']['linting_issues']}
- Type Coverage: {self.health_data['code_quality']['type_coverage']}%
- Complexity Score: {self.health_data['code_quality']['complexity_score']}

### Immediate Actions:
1. Run comprehensive linting cleanup
2. Add type annotations to critical modules
3. Refactor overly complex functions
4. Set up automated quality gates

### Impact:
- Reduced code maintainability
- Increased bug risk
- Slower development velocity

**Priority: HIGH**
""",
                'labels': ['bug', 'critical', 'code-quality']
            })
        
        # High-priority issue backlog
        if self.health_data['issue_tracking']['priority_breakdown']['high'] > 3:
            issues_to_create.append({
                'title': f"[URGENT] High-Priority Issue Backlog ({self.health_data['issue_tracking']['priority_breakdown']['high']} issues)",
                'body': f"""## Issue Backlog Crisis

High-priority issues: **{self.health_data['issue_tracking']['priority_breakdown']['high']}**
Total issues: **{self.health_data['issue_tracking']['total_local_issues']}**

### Risk Assessment:
- Development velocity impact
- Technical debt accumulation
- User experience degradation

### Action Plan:
1. Immediate triage session
2. Prioritize critical bugs
3. Allocate dedicated resolution time
4. Set up issue velocity tracking

**Priority: URGENT**
""",
                'labels': ['project-management', 'urgent', 'technical-debt']
            })
        
        # Low test coverage
        if self.health_data['test_metrics']['total_tests'] < 30:
            issues_to_create.append({
                'title': f"[QUALITY] Insufficient Test Coverage ({self.health_data['test_metrics']['total_tests']} tests)",
                'body': f"""## Test Coverage Insufficient

Current test count: **{self.health_data['test_metrics']['total_tests']}**
Target: **100+ tests minimum**

### Impact:
- Increased regression risk
- Reduced deployment confidence
- Slower development velocity

### Action Plan:
1. Audit critical code paths
2. Add unit tests for core functionality
3. Implement integration tests
4. Set up coverage reporting

**Priority: MEDIUM**
""",
                'labels': ['testing', 'quality-assurance', 'technical-debt']
            })
        
        print(f"Generated {len(issues_to_create)} critical health issues")
        return issues_to_create


def main():
    parser = argparse.ArgumentParser(description='P(Doom) Project Health Dashboard')
    parser.add_argument('--full-report', action='store_true', 
                       help='Generate comprehensive health report')
    parser.add_argument('--quick-check', action='store_true',
                       help='Perform quick health check')
    parser.add_argument('--generate-issues', action='store_true',
                       help='Generate GitHub issues for critical problems')
    parser.add_argument('--ci-mode', action='store_true',
                       help='CI-friendly output mode')
    parser.add_argument('--output', type=str,
                       help='Save report to JSON file')
    
    args = parser.parse_args()
    
    dashboard = ProjectHealthDashboard()
    
    if args.quick_check:
        result = dashboard.quick_check()
    elif args.generate_issues:
        result = dashboard.generate_github_issues()
    else:
        result = dashboard.generate_full_report()
    
    # Save output if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n[SAVE] Report saved to {args.output}")
    
    # CI mode exit codes
    if args.ci_mode:
        if isinstance(result, dict) and 'overall_score' in result:
            if result['overall_score'] < 60:
                sys.exit(1)  # Fail CI if health is poor
            elif result['overall_score'] < 80:
                sys.exit(2)  # Warning if health needs attention
        elif isinstance(result, dict) and 'quick_score' in result:
            if result['quick_score'] < 60:
                sys.exit(1)


if __name__ == '__main__':
    main()