#!/usr/bin/env python3
"""
Project Health Automation Suite - BLITZ MODE

Complete project health management integration that:
- Records health snapshots automatically
- Generates GitHub issues for critical problems
- Creates dev blog entries with trends
- Integrates with CI/CD pipeline
- Provides actionable insights and automation

BLITZ MODE FEATURES:
- One-command health improvement workflows
- Automated issue triage and prioritization
- Smart milestone tracking and celebration
- Integration with existing P(Doom) infrastructure

Usage:
    python scripts/health_automation.py --daily-health-check
    python scripts/health_automation.py --emergency-triage
    python scripts/health_automation.py --improvement-blitz
    python scripts/health_automation.py --celebration-mode
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.project_health import ProjectHealthDashboard
from scripts.health_tracker import HealthHistoryTracker

class HealthAutomationSuite:
    """Complete automation suite for project health management."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.dashboard = ProjectHealthDashboard()
        self.tracker = HealthHistoryTracker()
        
    def daily_health_check(self):
        """Automated daily health check with full reporting."""
        print("🌅 DAILY HEALTH CHECK INITIATED")
        print("=" * 50)
        
        # 1. Record health snapshot
        print("\n📊 STEP 1: Recording health snapshot...")
        snapshot = self.tracker.record_health_snapshot(
            notes=f"Daily automated health check - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        # 2. Generate dev blog entry
        print("\n📝 STEP 2: Generating dev blog entry...")
        blog_file = self.tracker.generate_dev_blog_entry()
        
        # 3. Check for critical issues
        print("\n🚨 STEP 3: Checking for critical issues...")
        health_data = snapshot['health_data']
        critical_issues = self._identify_critical_issues(health_data)
        
        if critical_issues:
            print(f"🚨 FOUND {len(critical_issues)} CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   - {issue}")
        else:
            print("✅ No critical issues detected!")
        
        # 4. Generate summary
        print("\n📋 STEP 4: Daily summary...")
        self._print_daily_summary(health_data, blog_file, critical_issues)
        
        return {
            'snapshot': snapshot,
            'blog_file': blog_file,
            'critical_issues': critical_issues
        }
    
    def emergency_triage(self):
        """Emergency triage mode for critical health issues."""
        print("🚨 EMERGENCY TRIAGE MODE ACTIVATED")
        print("=" * 50)
        
        # Get current health
        health_data = self.dashboard.generate_full_report()
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(health_data)
        
        if not critical_issues:
            print("✅ No emergency issues detected!")
            return
        
        print(f"\n🚨 EMERGENCY ISSUES DETECTED ({len(critical_issues)}):")
        
        # Prioritize issues
        prioritized_issues = self._prioritize_emergency_issues(critical_issues, health_data)
        
        for i, (priority, issue, action) in enumerate(prioritized_issues, 1):
            print(f"\n{i}. {priority}: {issue}")
            print(f"   ACTION: {action}")
        
        # Generate emergency action plan
        self._generate_emergency_action_plan(prioritized_issues)
        
        return prioritized_issues
    
    def improvement_blitz(self):
        """Rapid improvement mode targeting biggest wins."""
        print("⚡ IMPROVEMENT BLITZ MODE")
        print("=" * 50)
        
        health_data = self.dashboard.generate_full_report()
        
        # Identify biggest wins
        improvements = self._identify_biggest_wins(health_data)
        
        print(f"\n🎯 BIGGEST IMPROVEMENT OPPORTUNITIES ({len(improvements)}):")
        
        for i, (impact, effort, improvement, action) in enumerate(improvements, 1):
            impact_emoji = "🎯" if impact == "HIGH" else "📈" if impact == "MEDIUM" else "⚡"
            effort_emoji = "🟢" if effort == "LOW" else "🟡" if effort == "MEDIUM" else "🔴"
            
            print(f"\n{i}. {impact_emoji} {improvement} (Impact: {impact}, Effort: {effort_emoji} {effort})")
            print(f"   🔧 ACTION: {action}")
        
        return improvements
    
    def celebration_mode(self):
        """Celebrate recent achievements and milestones."""
        print("🎉 CELEBRATION MODE - ACKNOWLEDGING WINS!")
        print("=" * 50)
        
        # Get recent milestones
        milestones = self.tracker.get_recent_milestones(days=7)
        trends = self.tracker.get_trend_analysis()
        
        celebrations = []
        
        # Celebrate milestones
        if milestones:
            print(f"\n🏆 RECENT MILESTONES ({len(milestones)}):")
            for milestone in milestones:
                print(f"   🎯 {milestone['description']}")
                celebrations.append(f"Milestone: {milestone['description']}")
        
        # Celebrate positive trends
        positive_trends = [
            (metric, data) for metric, data in trends.items() 
            if data['trend_direction'] == 'IMPROVING'
        ]
        
        if positive_trends:
            print(f"\n📈 POSITIVE TRENDS ({len(positive_trends)}):")
            for metric, data in positive_trends:
                print(f"   📈 {metric.replace('_', ' ').title()}: +{data['trend_percentage']:.1f}%")
                celebrations.append(f"Improved {metric}: +{data['trend_percentage']:.1f}%")
        
        # Celebrate big numbers
        health_data = self.dashboard.generate_full_report()
        big_wins = self._identify_celebration_worthy_metrics(health_data)
        
        if big_wins:
            print(f"\n🌟 IMPRESSIVE METRICS:")
            for metric, value, description in big_wins:
                print(f"   🌟 {description}: {value}")
                celebrations.append(f"{description}: {value}")
        
        if not celebrations:
            print("🔧 Keep working - your next celebration is coming!")
        else:
            print(f"\n🎊 TOTAL CELEBRATIONS: {len(celebrations)}")
            
        return celebrations
    
    def _identify_critical_issues(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify issues requiring immediate attention."""
        critical_issues = []
        
        # Overall health crisis
        overall_score = health_data.get('overall_score', 0)
        if overall_score < 30:
            critical_issues.append(f"HEALTH CRISIS: Overall score critically low ({overall_score}/100)")
        
        # Code quality crisis
        code_quality = health_data.get('code_quality', {})
        linting_issues = code_quality.get('linting_issues', 0)
        if linting_issues > 1000:
            critical_issues.append(f"LINTING CRISIS: {linting_issues} linting issues detected")
        
        # Issue backlog crisis
        issue_tracking = health_data.get('issue_tracking', {})
        high_priority = issue_tracking.get('priority_breakdown', {}).get('high', 0)
        if high_priority > 10:
            critical_issues.append(f"ISSUE BACKLOG CRISIS: {high_priority} high-priority issues")
        
        # Test failure crisis
        test_metrics = health_data.get('test_metrics', {})
        if test_metrics.get('score', 0) < 30:
            critical_issues.append("TEST CRISIS: Test coverage critically low")
        
        # Working tree chaos
        branch_health = health_data.get('branch_health', {})
        if not branch_health.get('clean_working_tree', True):
            critical_issues.append("WORKING TREE CHAOS: Uncommitted changes detected")
        
        return critical_issues
    
    def _prioritize_emergency_issues(self, critical_issues: List[str], health_data: Dict[str, Any]) -> List[tuple]:
        """Prioritize emergency issues by severity and impact."""
        prioritized = []
        
        for issue in critical_issues:
            if "HEALTH CRISIS" in issue:
                prioritized.append(("🔴 CRITICAL", issue, "Run full health improvement blitz"))
            elif "LINTING CRISIS" in issue:
                prioritized.append(("🟠 HIGH", issue, "Run automated linting fixes"))
            elif "ISSUE BACKLOG CRISIS" in issue:
                prioritized.append(("🟡 MEDIUM", issue, "Emergency issue triage session"))
            elif "TEST CRISIS" in issue:
                prioritized.append(("🟠 HIGH", issue, "Immediate test coverage review"))
            elif "WORKING TREE CHAOS" in issue:
                prioritized.append(("🟢 LOW", issue, "Commit or stash changes"))
            else:
                prioritized.append(("❓ UNKNOWN", issue, "Manual investigation required"))
        
        # Sort by priority (CRITICAL > HIGH > MEDIUM > LOW)
        priority_order = {"🔴 CRITICAL": 0, "🟠 HIGH": 1, "🟡 MEDIUM": 2, "🟢 LOW": 3, "❓ UNKNOWN": 4}
        prioritized.sort(key=lambda x: priority_order.get(x[0], 5))
        
        return prioritized
    
    def _identify_biggest_wins(self, health_data: Dict[str, Any]) -> List[tuple]:
        """Identify biggest improvement opportunities by impact vs effort."""
        opportunities = []
        
        # Linting cleanup - high impact, medium effort
        linting_issues = health_data.get('code_quality', {}).get('linting_issues', 0)
        if linting_issues > 100:
            opportunities.append((
                "HIGH", "MEDIUM", 
                f"Fix {linting_issues} linting issues", 
                "Run automated linting tools (autoflake, black, isort)"
            ))
        
        # Type annotation improvement - high impact, low effort  
        type_coverage = health_data.get('code_quality', {}).get('type_coverage', 0)
        if type_coverage < 70:
            opportunities.append((
                "HIGH", "LOW",
                f"Improve type coverage from {type_coverage}%",
                "Add type hints to high-traffic functions"
            ))
        
        # Issue triage - medium impact, low effort
        total_issues = health_data.get('issue_tracking', {}).get('total_local_issues', 0)
        if total_issues > 30:
            opportunities.append((
                "MEDIUM", "LOW",
                f"Reduce {total_issues} issue backlog",
                "Close obsolete issues and prioritize active ones"
            ))
        
        # Documentation improvements - medium impact, low effort
        doc_score = health_data.get('documentation', {}).get('score', 0)
        if doc_score < 80:
            opportunities.append((
                "MEDIUM", "LOW",
                f"Improve documentation score from {doc_score}%",
                "Add docstrings to key functions"
            ))
        
        # Working tree cleanup - low impact, very low effort
        if not health_data.get('branch_health', {}).get('clean_working_tree', True):
            opportunities.append((
                "LOW", "LOW",
                "Clean working tree",
                "Commit or stash uncommitted changes"
            ))
        
        # Sort by impact (HIGH > MEDIUM > LOW) then by effort (LOW > MEDIUM > HIGH)
        impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        effort_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        
        opportunities.sort(key=lambda x: (impact_order.get(x[0], 3), effort_order.get(x[1], 3)))
        
        return opportunities
    
    def _identify_celebration_worthy_metrics(self, health_data: Dict[str, Any]) -> List[tuple]:
        """Identify metrics worth celebrating."""
        celebrations = []
        
        # Test count celebrations
        test_count = health_data.get('test_metrics', {}).get('total_tests', 0)
        if test_count > 5000:
            celebrations.append(('test_count', test_count, f"Massive test suite with {test_count:,} tests"))
        elif test_count > 1000:
            celebrations.append(('test_count', test_count, f"Strong test coverage with {test_count:,} tests"))
        
        # Documentation celebrations
        md_files = health_data.get('documentation', {}).get('markdown_files', 0)
        if md_files > 200:
            celebrations.append(('documentation', md_files, f"Comprehensive documentation with {md_files} markdown files"))
        
        # Automation celebrations
        automation_score = health_data.get('automation', {}).get('score', 0)
        if automation_score > 80:
            celebrations.append(('automation', automation_score, f"Excellent automation infrastructure ({automation_score}/100)"))
        
        # File count celebrations
        python_files = health_data.get('code_quality', {}).get('file_count', {}).get('python', 0)
        if python_files > 200:
            celebrations.append(('codebase', python_files, f"Large codebase with {python_files} Python files"))
        
        return celebrations
    
    def _generate_emergency_action_plan(self, prioritized_issues: List[tuple]):
        """Generate actionable emergency plan."""
        print(f"\n⚡ EMERGENCY ACTION PLAN:")
        print(f"   1. Focus on {prioritized_issues[0][1] if prioritized_issues else 'general improvements'}")
        print(f"   2. Execute: {prioritized_issues[0][2] if prioritized_issues else 'run health check'}")
        print(f"   3. Re-run health check to verify improvement")
        print(f"   4. Move to next priority issue")
    
    def _print_daily_summary(self, health_data: Dict[str, Any], blog_file: str, critical_issues: List[str]):
        """Print daily summary report."""
        overall_score = health_data.get('overall_score', 0)
        
        print(f"\n📊 DAILY HEALTH SUMMARY:")
        print(f"   🏥 Overall Health: {overall_score}/100")
        print(f"   📝 Blog Entry: {Path(blog_file).name}")
        print(f"   🚨 Critical Issues: {len(critical_issues)}")
        
        if overall_score >= 80:
            print(f"   🎉 STATUS: Project health is EXCELLENT!")
        elif overall_score >= 60:
            print(f"   📈 STATUS: Project health is GOOD - keep improving!")
        else:
            print(f"   ⚠️ STATUS: Project needs attention")
        
        print(f"\n⚡ NEXT ACTIONS:")
        if critical_issues:
            print(f"   - Run: python scripts/health_automation.py --emergency-triage")
        else:
            print(f"   - Run: python scripts/health_automation.py --improvement-blitz")
        print(f"   - Run: python scripts/health_automation.py --celebration-mode")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Health Automation Suite')
    parser.add_argument('--daily-health-check', action='store_true',
                       help='Run automated daily health check')
    parser.add_argument('--emergency-triage', action='store_true',
                       help='Emergency triage for critical issues')
    parser.add_argument('--improvement-blitz', action='store_true',
                       help='Rapid improvement targeting biggest wins')
    parser.add_argument('--celebration-mode', action='store_true',
                       help='Celebrate recent achievements')
    parser.add_argument('--full-automation', action='store_true',
                       help='Run complete automation suite')
    
    args = parser.parse_args()
    
    suite = HealthAutomationSuite()
    
    if args.daily_health_check:
        suite.daily_health_check()
    elif args.emergency_triage:
        suite.emergency_triage()
    elif args.improvement_blitz:
        suite.improvement_blitz()
    elif args.celebration_mode:
        suite.celebration_mode()
    elif args.full_automation:
        print("🚀 FULL AUTOMATION SUITE")
        print("=" * 50)
        suite.daily_health_check()
        print("\n" + "="*50)
        suite.emergency_triage()
        print("\n" + "="*50)
        suite.improvement_blitz()
        print("\n" + "="*50)
        suite.celebration_mode()
    else:
        # Default: daily health check
        suite.daily_health_check()


if __name__ == '__main__':
    main()