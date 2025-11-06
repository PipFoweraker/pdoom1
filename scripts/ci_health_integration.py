# !/usr/bin/env python3
"""
CI/CD Health Integration - GitHub Actions Integration

Integrates project health monitoring with GitHub Actions pipeline.
Provides automated health gates, issue creation, and dev blog updates.

Features:
- Health gates for pull requests and releases
- Automated issue creation for critical problems
- Dev blog automation with health trends
- Performance regression detection
- Health milestone celebrations

Usage (CI/CD):
    python scripts/ci_health_integration.py --gate-check
    python scripts/ci_health_integration.py --post-merge-health
    python scripts/ci_health_integration.py --release-readiness
    python scripts/ci_health_integration.py --health-reporting
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.project_health import ProjectHealthDashboard
from scripts.health_tracker import HealthHistoryTracker
from scripts.health_automation import HealthAutomationSuite

class CIHealthIntegration:
    """CI/CD integration for automated health monitoring."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.dashboard = ProjectHealthDashboard()
        self.tracker = HealthHistoryTracker()
        self.automation = HealthAutomationSuite()
        self.is_ci = os.getenv('CI', 'false').lower() == 'true'
        self.github_actions = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
        
    def health_gate_check(self, min_score: int = 60) -> bool:
        """Health gate check for CI/CD pipeline."""
        print("[GATE] HEALTH GATE CHECK")
        print("=" * 40)
        
        # Quick health check for speed
        health_data = self.dashboard.quick_check()
        score = health_data.get('quick_score', 0)
        
        print(f"[DATA] Current Health Score: {score}/100")
        print(f"[TARGET] Required Minimum: {min_score}/100")
        
        if score >= min_score:
            print("[OK] HEALTH GATE: PASSED")
            self._set_github_output('health_gate_status', 'passed')
            self._set_github_output('health_score', str(score))
            return True
        else:
            print("[FAIL] HEALTH GATE: FAILED")
            print(f"[IDEA] Improvement needed: {min_score - score} points")
            
            # Generate immediate action recommendations
            critical_issues = self._identify_gate_blockers(health_data)
            print(f"\n[URGENT] GATE BLOCKERS ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"   - {issue}")
            
            self._set_github_output('health_gate_status', 'failed')
            self._set_github_output('health_score', str(score))
            self._set_github_output('gate_blockers', json.dumps(critical_issues))
            
            return False
    
    def post_merge_health_tracking(self):
        """Track health changes after merge to main."""
        print("[UP] POST-MERGE HEALTH TRACKING")
        print("=" * 40)
        
        # Record health snapshot
        commit_hash = os.getenv('GITHUB_SHA', 'unknown')[:8]
        notes = f"Post-merge health tracking - {commit_hash}"
        
        snapshot = self.tracker.record_health_snapshot(notes=notes)
        health_data = snapshot['health_data']
        
        # Check for regressions
        regressions = self._detect_health_regressions(health_data)
        
        if regressions:
            print(f"[WARNING] HEALTH REGRESSIONS DETECTED ({len(regressions)}):")
            for regression in regressions:
                print(f"   [DOWN] {regression}")
        else:
            print("[OK] No health regressions detected")
        
        # Check for improvements
        improvements = self._detect_health_improvements(health_data)
        
        if improvements:
            print(f"[CELEBRATE] HEALTH IMPROVEMENTS DETECTED ({len(improvements)}):")
            for improvement in improvements:
                print(f"   [UP] {improvement}")
        
        # Generate dev blog entry if significant changes
        if regressions or improvements:
            blog_file = self.tracker.generate_dev_blog_entry(title_suffix="post-merge")
            print(f"[WRITE] Dev blog entry created: {Path(blog_file).name}")
        
        # Set GitHub outputs
        self._set_github_output('health_regressions', json.dumps(regressions))
        self._set_github_output('health_improvements', json.dumps(improvements))
        self._set_github_output('overall_score', str(health_data.get('overall_score', 0)))
        
        return {
            'snapshot': snapshot,
            'regressions': regressions,
            'improvements': improvements
        }
    
    def release_readiness_check(self, target_score: int = 80) -> bool:
        """Comprehensive release readiness assessment."""
        print("[LAUNCH] RELEASE READINESS CHECK")
        print("=" * 40)
        
        health_data = self.dashboard.generate_full_report()
        overall_score = health_data.get('overall_score', 0)
        
        print(f"[DATA] Overall Health Score: {overall_score}/100")
        print(f"[TARGET] Release Target: {target_score}/100")
        
        # Detailed readiness assessment
        readiness_checks = self._perform_release_readiness_checks(health_data)
        
        passed_checks = sum(1 for check in readiness_checks if check['passed'])
        total_checks = len(readiness_checks)
        
        print(f"\n[OK] READINESS CHECKS: {passed_checks}/{total_checks} passed")
        
        for check in readiness_checks:
            status = "[OK]" if check['passed'] else "[FAIL]"
            print(f"   {status} {check['name']}: {check['description']}")
        
        # Overall readiness determination
        is_ready = overall_score >= target_score and passed_checks == total_checks
        
        if is_ready:
            print(f"\n[CELEBRATE] RELEASE READY! All checks passed.")
        else:
            print(f"\n[WARNING] RELEASE NOT READY - {total_checks - passed_checks} checks failed")
            
            # Generate release blockers report
            blockers = [check for check in readiness_checks if not check['passed']]
            print(f"\n[BLOCK] RELEASE BLOCKERS ({len(blockers)}):")
            for blocker in blockers:
                print(f"   [BLOCK] {blocker['name']}: {blocker['blocker_reason']}")
        
        # Set GitHub outputs
        self._set_github_output('release_ready', 'true' if is_ready else 'false')
        self._set_github_output('readiness_score', f"{passed_checks}/{total_checks}")
        self._set_github_output('health_score', str(overall_score))
        
        return is_ready
    
    def automated_health_reporting(self):
        """Generate automated health reports for stakeholders."""
        print("[DATA] AUTOMATED HEALTH REPORTING")
        print("=" * 40)
        
        # Generate comprehensive report
        health_data = self.dashboard.generate_full_report()
        
        # Create stakeholder report
        report = self._generate_stakeholder_report(health_data)
        
        # Save report
        report_file = self.project_root / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"[FILE] Health report saved: {report_file.name}")
        
        # Generate dev blog entry
        blog_file = self.tracker.generate_dev_blog_entry(title_suffix="automated-report")
        print(f"[WRITE] Dev blog entry: {Path(blog_file).name}")
        
        # Set GitHub outputs
        self._set_github_output('report_file', str(report_file))
        self._set_github_output('blog_file', blog_file)
        
        return report
    
    def _identify_gate_blockers(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify specific issues blocking health gate."""
        blockers = []
        
        linting_issues = health_data.get('linting_issues', 0)
        if linting_issues > 100:
            blockers.append(f"Excessive linting issues: {linting_issues}")
        
        total_issues = health_data.get('total_issues', 0)
        if total_issues > 50:
            blockers.append(f"Too many open issues: {total_issues}")
        
        test_count = health_data.get('test_count', 0)
        if test_count < 20:
            blockers.append(f"Insufficient test coverage: {test_count} test files")
        
        if not health_data.get('working_tree_clean', True):
            blockers.append("Dirty working tree - uncommitted changes")
        
        return blockers
    
    def _detect_health_regressions(self, current_health: Dict[str, Any]) -> List[str]:
        """Detect health regressions compared to previous measurements."""
        # Get recent history
        history = self.tracker.get_health_history(days=7)
        
        if len(history) < 2:
            return []  # Need previous data for comparison
        
        regressions = []
        previous = history[1]  # Second most recent (first is current)
        
        # Check overall score regression
        current_score = current_health.get('overall_score', 0)
        previous_score = previous['overall_score']
        
        if current_score < previous_score - 10:  # 10+ point drop
            regressions.append(f"Overall health dropped from {previous_score} to {current_score}")
        
        # Check specific metrics
        current_linting = current_health.get('code_quality', {}).get('linting_issues', 0)
        previous_linting = previous['linting_issues']
        
        if current_linting > previous_linting + 50:  # 50+ new linting issues
            regressions.append(f"Linting issues increased from {previous_linting} to {current_linting}")
        
        return regressions
    
    def _detect_health_improvements(self, current_health: Dict[str, Any]) -> List[str]:
        """Detect health improvements compared to previous measurements."""
        history = self.tracker.get_health_history(days=7)
        
        if len(history) < 2:
            return []
        
        improvements = []
        previous = history[1]
        
        # Check overall score improvement
        current_score = current_health.get('overall_score', 0)
        previous_score = previous['overall_score']
        
        if current_score > previous_score + 10:  # 10+ point improvement
            improvements.append(f"Overall health improved from {previous_score} to {current_score}")
        
        # Check linting improvements
        current_linting = current_health.get('code_quality', {}).get('linting_issues', 0)
        previous_linting = previous['linting_issues']
        
        if current_linting < previous_linting - 50:  # 50+ fewer linting issues
            improvements.append(f"Linting issues reduced from {previous_linting} to {current_linting}")
        
        # Check type coverage improvements
        current_types = current_health.get('code_quality', {}).get('type_coverage', 0)
        previous_types = previous['type_coverage']
        
        if current_types > previous_types + 5:  # 5%+ type coverage improvement
            improvements.append(f"Type coverage improved from {previous_types}% to {current_types}%")
        
        return improvements
    
    def _perform_release_readiness_checks(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform comprehensive release readiness checks."""
        checks = []
        
        # Health score check
        overall_score = health_data.get('overall_score', 0)
        checks.append({
            'name': 'Overall Health Score',
            'passed': overall_score >= 80,
            'description': f'Score: {overall_score}/100',
            'blocker_reason': f'Health score {overall_score} below release minimum of 80'
        })
        
        # Critical issues check
        high_priority = health_data.get('issue_tracking', {}).get('priority_breakdown', {}).get('high', 0)
        checks.append({
            'name': 'Critical Issues',
            'passed': high_priority <= 3,
            'description': f'High-priority issues: {high_priority}',
            'blocker_reason': f'{high_priority} high-priority issues exceed release limit of 3'
        })
        
        # Test coverage check
        test_count = health_data.get('test_metrics', {}).get('total_tests', 0)
        checks.append({
            'name': 'Test Coverage',
            'passed': test_count >= 100,
            'description': f'Total tests: {test_count}',
            'blocker_reason': f'Test count {test_count} below release minimum of 100'
        })
        
        # Working tree check
        clean_tree = health_data.get('branch_health', {}).get('clean_working_tree', False)
        checks.append({
            'name': 'Clean Working Tree',
            'passed': clean_tree,
            'description': 'No uncommitted changes' if clean_tree else 'Uncommitted changes detected',
            'blocker_reason': 'Release requires clean working tree'
        })
        
        # Documentation check
        doc_score = health_data.get('documentation', {}).get('score', 0)
        checks.append({
            'name': 'Documentation Quality',
            'passed': doc_score >= 80,
            'description': f'Documentation score: {doc_score}/100',
            'blocker_reason': f'Documentation score {doc_score} below release minimum of 80'
        })
        
        return checks
    
    def _generate_stakeholder_report(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stakeholder-friendly health report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'overall_health': health_data.get('overall_score', 0),
                'health_status': self._get_health_status_text(health_data.get('overall_score', 0)),
                'total_tests': health_data.get('test_metrics', {}).get('total_tests', 0),
                'open_issues': health_data.get('issue_tracking', {}).get('total_local_issues', 0),
                'critical_issues': health_data.get('issue_tracking', {}).get('priority_breakdown', {}).get('high', 0)
            },
            'metrics': {
                'code_quality': health_data.get('code_quality', {}).get('score', 0),
                'test_coverage': health_data.get('test_metrics', {}).get('score', 0),
                'documentation': health_data.get('documentation', {}).get('score', 0),
                'automation': health_data.get('automation', {}).get('score', 0)
            },
            'trends': self.tracker.get_trend_analysis(),
            'recommendations': health_data.get('recommendations', []),
            'milestones': self.tracker.get_recent_milestones(days=7)
        }
    
    def _get_health_status_text(self, score: int) -> str:
        """Convert health score to status text."""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 80:
            return "GOOD"
        elif score >= 60:
            return "FAIR"
        else:
            return "NEEDS_ATTENTION"
    
    def _set_github_output(self, name: str, value: str):
        """Set GitHub Actions output variable."""
        if self.github_actions:
            # GitHub Actions output format
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                with open(github_output, 'a') as f:
                    f.write(f"{name}={value}\n")
        else:
            # Local testing - just print
            print(f"[REMOVED] OUTPUT: {name}={value}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD Health Integration')
    parser.add_argument('--gate-check', action='store_true',
                       help='Health gate check for CI/CD')
    parser.add_argument('--post-merge-health', action='store_true',
                       help='Post-merge health tracking')
    parser.add_argument('--release-readiness', action='store_true',
                       help='Release readiness assessment')
    parser.add_argument('--health-reporting', action='store_true',
                       help='Automated health reporting')
    parser.add_argument('--min-score', type=int, default=60,
                       help='Minimum health score for gates')
    parser.add_argument('--target-score', type=int, default=80,
                       help='Target health score for releases')
    
    args = parser.parse_args()
    
    integration = CIHealthIntegration()
    
    if args.gate_check:
        success = integration.health_gate_check(min_score=args.min_score)
        sys.exit(0 if success else 1)
    elif args.post_merge_health:
        integration.post_merge_health_tracking()
    elif args.release_readiness:
        ready = integration.release_readiness_check(target_score=args.target_score)
        sys.exit(0 if ready else 1)
    elif args.health_reporting:
        integration.automated_health_reporting()
    else:
        # Default: health gate check
        success = integration.health_gate_check(min_score=args.min_score)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()