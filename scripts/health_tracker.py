#!/usr/bin/env python3
"""
Project Health History Tracker & Dev Blog Integration

Tracks project health metrics over time and automatically generates
dev blog entries with health insights and trends.

Features:
- Historical health data storage
- Trend analysis and insights
- Automated dev blog entry generation
- Health milestone detection
- Performance regression alerts

Usage:
    python scripts/health_tracker.py --record-health
    python scripts/health_tracker.py --generate-blog-entry
    python scripts/health_tracker.py --show-trends
    python scripts/health_tracker.py --health-history
"""

import sys
import json
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import our health dashboard
from scripts.project_health import ProjectHealthDashboard

class HealthHistoryTracker:
    """Tracks project health metrics over time with dev blog integration."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.db_path = self.project_root / 'project_health_history.db'
        self.dev_blog_dir = self.project_root / 'dev-blog' / 'entries'
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for health history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create health_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                overall_score INTEGER NOT NULL,
                code_quality_score INTEGER,
                issue_tracking_score INTEGER,
                branch_health_score INTEGER,
                test_metrics_score INTEGER,
                documentation_score INTEGER,
                automation_score INTEGER,
                linting_issues INTEGER,
                total_issues INTEGER,
                high_priority_issues INTEGER,
                test_count INTEGER,
                type_coverage REAL,
                file_count INTEGER,
                working_tree_clean BOOLEAN,
                raw_data TEXT,
                notes TEXT
            )
        ''')
        
        # Create milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                milestone_type TEXT NOT NULL,
                description TEXT NOT NULL,
                health_score INTEGER,
                details TEXT
            )
        ''')
        
        # Create trends table for quick analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_trends (
                metric_name TEXT PRIMARY KEY,
                current_value REAL,
                previous_value REAL,
                trend_direction TEXT,
                trend_percentage REAL,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def record_health_snapshot(self, notes: Optional[str] = None) -> Dict[str, Any]:
        """Record current project health to database."""
        print("[DATA] RECORDING HEALTH SNAPSHOT...")
        
        # Get current health data
        dashboard = ProjectHealthDashboard()
        health_data = dashboard.generate_full_report()
        
        # Extract key metrics
        timestamp = datetime.now().isoformat()
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_records (
                timestamp, overall_score, code_quality_score, issue_tracking_score,
                branch_health_score, test_metrics_score, documentation_score,
                automation_score, linting_issues, total_issues, high_priority_issues,
                test_count, type_coverage, file_count, working_tree_clean,
                raw_data, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            health_data.get('overall_score', 0),
            health_data.get('code_quality', {}).get('score', 0),
            health_data.get('issue_tracking', {}).get('score', 0),
            health_data.get('branch_health', {}).get('score', 0),
            health_data.get('test_metrics', {}).get('score', 0),
            health_data.get('documentation', {}).get('score', 0),
            health_data.get('automation', {}).get('score', 0),
            health_data.get('code_quality', {}).get('linting_issues', 0),
            health_data.get('issue_tracking', {}).get('total_local_issues', 0),
            health_data.get('issue_tracking', {}).get('priority_breakdown', {}).get('high', 0),
            health_data.get('test_metrics', {}).get('total_tests', 0),
            health_data.get('code_quality', {}).get('type_coverage', 0),
            health_data.get('code_quality', {}).get('file_count', {}).get('python', 0),
            health_data.get('branch_health', {}).get('clean_working_tree', False),
            json.dumps(health_data, default=str),
            notes
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        
        # Check for milestones
        self._check_milestones(health_data, cursor)
        
        # Update trends
        self._update_trends(cursor)
        
        conn.close()
        
        print(f"[OK] Health snapshot recorded (ID: {record_id})")
        print(f"[UP] Overall Score: {health_data.get('overall_score', 0)}/100")
        
        return {
            'record_id': record_id,
            'timestamp': timestamp,
            'health_data': health_data
        }
    
    def _check_milestones(self, health_data: Dict[str, Any], cursor):
        """Check for and record health milestones."""
        overall_score = health_data.get('overall_score', 0)
        timestamp = datetime.now().isoformat()
        
        milestones = []
        
        # Score milestones
        if overall_score >= 90:
            milestones.append(("EXCELLENT_HEALTH", "Project health reached EXCELLENT level (90+)", overall_score))
        elif overall_score >= 80:
            milestones.append(("GOOD_HEALTH", "Project health reached GOOD level (80+)", overall_score))
        elif overall_score >= 60:
            milestones.append(("FAIR_HEALTH", "Project health reached FAIR level (60+)", overall_score))
        
        # Specific metric milestones
        code_quality = health_data.get('code_quality', {}).get('score', 0)
        if code_quality >= 90:
            milestones.append(("CODE_QUALITY_EXCELLENT", "Code quality reached excellent level", code_quality))
        
        test_count = health_data.get('test_metrics', {}).get('total_tests', 0)
        if test_count >= 100:
            milestones.append(("TEST_CENTURY", "Test count reached 100+ tests", test_count))
        elif test_count >= 500:
            milestones.append(("TEST_MASSIVE", "Test count reached 500+ tests", test_count))
        
        type_coverage = health_data.get('code_quality', {}).get('type_coverage', 0)
        if type_coverage >= 80:
            milestones.append(("TYPE_COVERAGE_HIGH", "Type annotation coverage reached 80%+", type_coverage))
        
        linting_issues = health_data.get('code_quality', {}).get('linting_issues', 0)
        if linting_issues == 0:
            milestones.append(("ZERO_LINTING_ISSUES", "Achieved zero linting issues!", 0))
        elif linting_issues < 100:
            milestones.append(("LINTING_UNDER_100", "Linting issues reduced below 100", linting_issues))
        
        # Record milestones
        for milestone_type, description, value in milestones:
            # Check if milestone already recorded recently (avoid duplicates)
            cursor.execute('''
                SELECT COUNT(*) FROM health_milestones 
                WHERE milestone_type = ? AND timestamp > ?
            ''', (milestone_type, (datetime.now() - timedelta(days=7)).isoformat()))
            
            if cursor.fetchone()[0] == 0:  # Not recorded recently
                cursor.execute('''
                    INSERT INTO health_milestones (timestamp, milestone_type, description, health_score, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, milestone_type, description, overall_score, json.dumps({'value': value})))
                print(f"[TARGET] MILESTONE: {description}")
    
    def _update_trends(self, cursor):
        """Update trend analysis data."""
        # Get last two records to calculate trends
        cursor.execute('''
            SELECT overall_score, code_quality_score, test_count, linting_issues, type_coverage
            FROM health_records 
            ORDER BY timestamp DESC 
            LIMIT 2
        ''')
        
        records = cursor.fetchall()
        if len(records) < 2:
            return  # Need at least 2 records for trends
        
        current, previous = records[0], records[1]
        timestamp = datetime.now().isoformat()
        
        # Calculate trends for key metrics
        metrics = [
            ('overall_score', current[0], previous[0]),
            ('code_quality_score', current[1], previous[1]),
            ('test_count', current[2], previous[2]),
            ('linting_issues', current[3], previous[3]),
            ('type_coverage', current[4], previous[4])
        ]
        
        for metric_name, curr_val, prev_val in metrics:
            if prev_val == 0:
                continue  # Avoid division by zero
                
            trend_percentage = ((curr_val - prev_val) / prev_val) * 100
            
            if trend_percentage > 5:
                direction = "IMPROVING"
            elif trend_percentage < -5:
                direction = "DECLINING"
            else:
                direction = "STABLE"
            
            # Linting issues trend is inverted (fewer is better)
            if metric_name == 'linting_issues':
                if trend_percentage > 5:
                    direction = "DECLINING"
                elif trend_percentage < -5:
                    direction = "IMPROVING"
            
            cursor.execute('''
                INSERT OR REPLACE INTO health_trends 
                (metric_name, current_value, previous_value, trend_direction, trend_percentage, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric_name, curr_val, prev_val, direction, trend_percentage, timestamp))
    
    def generate_comprehensive_health_trend_analysis_for_cicd_integration(self, analysis_period_days: int = 30, output_format: str = 'human') -> Dict[str, Any]:
        """Generate comprehensive health trend analysis optimized for CI/CD pipeline integration.
        
        This method provides detailed trend analysis across all health metrics with multiple
        output formats suitable for human consumption, automated reporting, and CI/CD gates.
        
        Args:
            analysis_period_days: Number of historical days to analyze for trend calculation
            output_format: Output presentation format ('human', 'json', 'csv', 'summary', 'ci')
            
        Returns:
            Dictionary containing comprehensive trend analysis data with metrics, directions, and percentages
        """
        database_connection = sqlite3.connect(self.db_path)
        database_cursor = database_connection.cursor()
        
        historical_cutoff_timestamp = (datetime.now() - timedelta(days=analysis_period_days)).isoformat()
        database_cursor.execute('''
            SELECT timestamp, overall_score, code_quality_score, issue_tracking_score,
                   branch_health_score, test_metrics_score, documentation_score, automation_score
            FROM health_records 
            WHERE timestamp >= ? 
            ORDER BY timestamp ASC
        ''', (historical_cutoff_timestamp,))
        
        historical_health_records = database_cursor.fetchall()
        database_connection.close()
        
        if len(historical_health_records) < 2:
            insufficient_data_response = {
                'error_message': f'Insufficient historical data for trend analysis (need 2+ records, have {len(historical_health_records)})',
                'analysis_period_days': analysis_period_days,
                'available_records_count': len(historical_health_records)
            }
            if output_format in ['human', 'summary']:
                print(f"[UP] HEALTH TRENDS: Insufficient data ({len(historical_health_records)} records)")
            elif output_format == 'json':
                print(json.dumps(insufficient_data_response, indent=2))
            return insufficient_data_response
        
        # Calculate comprehensive trend analysis for each health metric
        health_metric_names_list = ['overall_score', 'code_quality', 'issue_tracking', 
                                  'branch_health', 'test_metrics', 'documentation', 'automation']
        
        comprehensive_trend_analysis_data = {
            'analysis_period_days': analysis_period_days,
            'available_records_count': len(historical_health_records),
            'trend_analysis_timestamp': datetime.now().isoformat(),
            'individual_metric_trends': {}
        }
        
        for metric_index, health_metric_name in enumerate(health_metric_names_list, 1):
            metric_historical_values = [record[metric_index] for record in historical_health_records]
            if metric_historical_values:
                earliest_metric_value = metric_historical_values[0]
                most_recent_metric_value = metric_historical_values[-1]
                absolute_metric_change = most_recent_metric_value - earliest_metric_value
                percentage_metric_change = (absolute_metric_change / earliest_metric_value * 100) if earliest_metric_value != 0 else 0
                
                comprehensive_trend_analysis_data['individual_metric_trends'][health_metric_name] = {
                    'current_value': most_recent_metric_value,
                    'historical_starting_value': earliest_metric_value,
                    'absolute_change': absolute_metric_change,
                    'percentage_change': round(percentage_metric_change, 1),
                    'trend_direction_indicator': 'improving' if absolute_metric_change > 0 else 'declining' if absolute_metric_change < 0 else 'stable',
                    'average_value_over_period': round(statistics.mean(metric_historical_values), 1),
                    'peak_value_in_period': max(metric_historical_values),
                    'lowest_value_in_period': min(metric_historical_values)
                }
        
        # Generate appropriate output based on requested format
        if output_format == 'json':
            print(json.dumps(comprehensive_trend_analysis_data, indent=2))
        elif output_format == 'csv':
            print("metric_name,current_value,starting_value,absolute_change,percentage_change,trend_direction,average_value,peak_value,lowest_value")
            for metric_name, metric_data in comprehensive_trend_analysis_data['individual_metric_trends'].items():
                print(f"{metric_name},{metric_data['current_value']},{metric_data['historical_starting_value']},{metric_data['absolute_change']},{metric_data['percentage_change']},{metric_data['trend_direction_indicator']},{metric_data['average_value_over_period']},{metric_data['peak_value_in_period']},{metric_data['lowest_value_in_period']}")
        elif output_format == 'summary':
            overall_health_metric_data = comprehensive_trend_analysis_data['individual_metric_trends'].get('overall_score', {})
            print(f"HEALTH_TREND_SUMMARY: {overall_health_metric_data.get('current_value', 0)}/100 ({overall_health_metric_data.get('percentage_change', 0):+.1f}% over {analysis_period_days}d)")
        elif output_format == 'ci':
            # Machine-readable format optimized for CI/CD pipeline consumption
            overall_health_metric_data = comprehensive_trend_analysis_data['individual_metric_trends'].get('overall_score', {})
            print(f"CICD_HEALTH_SCORE={overall_health_metric_data.get('current_value', 0)}")
            print(f"CICD_HEALTH_TREND_PERCENTAGE={overall_health_metric_data.get('percentage_change', 0)}")
            print(f"CICD_HEALTH_STATUS={overall_health_metric_data.get('trend_direction_indicator', 'unknown')}")
        elif output_format == 'human':
            print(f"[UP] COMPREHENSIVE HEALTH TRENDS ({analysis_period_days} days, {len(historical_health_records)} snapshots):")
            for metric_name, metric_data in comprehensive_trend_analysis_data['individual_metric_trends'].items():
                trend_direction_emoji = "[UP]" if metric_data['trend_direction_indicator'] == 'improving' else "[DOWN]" if metric_data['trend_direction_indicator'] == 'declining' else "[STABLE]"
                human_readable_metric_name = metric_name.replace('_', ' ').title()
                print(f"   {trend_direction_emoji} {human_readable_metric_name}: {metric_data['current_value']}/100 ({metric_data['percentage_change']:+.1f}%)")
        
        return comprehensive_trend_analysis_data
        """Get health history for specified number of days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, overall_score, code_quality_score, issue_tracking_score,
                   test_count, linting_issues, type_coverage, notes
            FROM health_records 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since_date,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'timestamp': row[0],
                'overall_score': row[1],
                'code_quality_score': row[2],
                'issue_tracking_score': row[3],
                'test_count': row[4],
                'linting_issues': row[5],
                'type_coverage': row[6],
                'notes': row[7]
            })
        
        conn.close()
        return records
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """Get current trend analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM health_trends')
        trends = {}
        
        for row in cursor.fetchall():
            trends[row[0]] = {
                'current_value': row[1],
                'previous_value': row[2],
                'trend_direction': row[3],
                'trend_percentage': row[4],
                'last_updated': row[5]
            }
        
        conn.close()
        return trends
    
    def get_recent_milestones(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent milestones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, milestone_type, description, health_score
            FROM health_milestones 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since_date,))
        
        milestones = []
        for row in cursor.fetchall():
            milestones.append({
                'timestamp': row[0],
                'type': row[1],
                'description': row[2],
                'health_score': row[3]
            })
        
        conn.close()
        return milestones
    
    def generate_dev_blog_entry(self, title_suffix: Optional[str] = None) -> str:
        """Generate automated dev blog entry with health insights."""
        print("[WRITE] GENERATING DEV BLOG ENTRY...")
        
        # Get current health data
        dashboard = ProjectHealthDashboard()
        current_health = dashboard.quick_check()
        
        # Get historical data
        history = self.get_health_history(days=7)
        trends = self.get_trend_analysis()
        milestones = self.get_recent_milestones(days=7)
        
        # Generate content
        date_str = datetime.now().strftime('%Y-%m-%d')
        title = f"project-health-update-{date_str}"
        if title_suffix:
            title += f"-{title_suffix}"
        
        content = self._generate_blog_content(current_health, history, trends, milestones)
        
        # Save to dev blog
        blog_file = self.dev_blog_dir / f"{title}.md"
        self.dev_blog_dir.mkdir(parents=True, exist_ok=True)
        
        with open(blog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Dev blog entry created: {blog_file}")
        return str(blog_file)
    
    def _generate_blog_content(self, current_health: Dict[str, Any], 
                             history: List[Dict[str, Any]], 
                             trends: Dict[str, Any],
                             milestones: List[Dict[str, Any]]) -> str:
        """Generate dev blog content from health data."""
        
        date_str = datetime.now().strftime('%B %d, %Y')
        
        content = f"""# Project Health Update - {date_str}

## Current Health Status

**Overall Health Score: {current_health.get('quick_score', 0)}/100**

### Quick Metrics:
- [SCAN] Linting Issues: {current_health.get('linting_issues', 0)}
- [LIST] Open Issues: {current_health.get('total_issues', 0)}
- [TEST] Test Files: {current_health.get('test_count', 0)}
- [BRANCH] Clean Working Tree: {'[OK]' if current_health.get('working_tree_clean') else '[FAIL]'}

## Health Trends (Last 7 Days)

"""
        
        # Add trend analysis
        if trends:
            content += "### Trend Analysis:\n"
            for metric, trend_data in trends.items():
                direction_emoji = {
                    'IMPROVING': '[UP]',
                    'DECLINING': '[DOWN]',
                    'STABLE': '[STABLE]'
                }.get(trend_data['trend_direction'], '[UNKNOWN]')
                
                content += f"- **{metric.replace('_', ' ').title()}**: {direction_emoji} {trend_data['trend_direction']} "
                content += f"({trend_data['trend_percentage']:+.1f}%)\n"
        
        # Add milestones
        if milestones:
            content += "\n## Recent Milestones [TARGET]\n\n"
            for milestone in milestones:
                milestone_date = datetime.fromisoformat(milestone['timestamp']).strftime('%m/%d')
                content += f"- **{milestone_date}**: {milestone['description']}\n"
        
        # Add historical context
        if len(history) > 1:
            content += "\n## Historical Context\n\n"
            scores = [h['overall_score'] for h in history if h['overall_score']]
            if scores:
                avg_score = statistics.mean(scores)
                content += f"- Average health score (7 days): {avg_score:.1f}/100\n"
                content += f"- Health score range: {min(scores)} - {max(scores)}\n"
        
        # Add action items based on current health
        content += "\n## Action Items\n\n"
        
        if current_health.get('linting_issues', 0) > 100:
            content += "- [URGENT] **URGENT**: Address linting issues (current: {})\n".format(
                current_health.get('linting_issues', 0))
        
        if current_health.get('total_issues', 0) > 30:
            content += "- [LIST] **HIGH**: Reduce issue backlog (current: {})\n".format(
                current_health.get('total_issues', 0))
        
        if current_health.get('test_count', 0) < 50:
            content += "- [TEST] **MEDIUM**: Increase test coverage (current: {} files)\n".format(
                current_health.get('test_count', 0))
        
        if not current_health.get('working_tree_clean', True):
            content += "- [BRANCH] **LOW**: Clean up working tree\n"
        
        # Add automation note
        content += f"\n---\n*Generated automatically by Project Health Tracker at {datetime.now().strftime('%H:%M')}*\n"
        
        return content
    
    def show_health_dashboard(self):
        """Display interactive health dashboard."""
        print("[HEALTH] PROJECT HEALTH DASHBOARD")
        print("=" * 50)
        
        # Current status
        dashboard = ProjectHealthDashboard()
        current = dashboard.quick_check()
        
        print(f"\n[DATA] CURRENT STATUS:")
        print(f"   Health Score: {current.get('quick_score', 0)}/100")
        
        # Recent trends
        trends = self.get_trend_analysis()
        if trends:
            print(f"\n[UP] TRENDS:")
            for metric, data in trends.items():
                emoji = {'IMPROVING': '[UP]', 'DECLINING': '[DOWN]', 'STABLE': '[STABLE]'}
                direction_emoji = emoji.get(data['trend_direction'], '[UNKNOWN]')
                print(f"   {direction_emoji} {metric.replace('_', ' ').title()}: {data['trend_direction']}")
        
        # Recent milestones
        milestones = self.get_recent_milestones()
        if milestones:
            print(f"\n[TARGET] RECENT MILESTONES:")
            for milestone in milestones[:3]:  # Show top 3
                date = datetime.fromisoformat(milestone['timestamp']).strftime('%m/%d')
                print(f"   {date}: {milestone['description']}")
        
        # Quick actions
        print(f"\n[QUICK] QUICK ACTIONS:")
        print(f"   Record health: python scripts/health_tracker.py --record-health")
        print(f"   Generate blog: python scripts/health_tracker.py --generate-blog-entry")
        print(f"   View history: python scripts/health_tracker.py --health-history")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Health History Tracker & CI/CD Integration')
    parser.add_argument('--record-health', action='store_true',
                       help='Record current health snapshot')
    parser.add_argument('--generate-blog-entry', action='store_true',
                       help='Generate dev blog entry')
    parser.add_argument('--show-trends', action='store_true',
                       help='Show health trends')
    parser.add_argument('--health-history', action='store_true',
                       help='Show health history')
    parser.add_argument('--dashboard', action='store_true',
                       help='Show interactive dashboard')
    parser.add_argument('--notes', type=str,
                       help='Add notes to health record')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days for history')
    parser.add_argument('--format', type=str, default='human',
                       choices=['human', 'json', 'csv', 'summary', 'ci'],
                       help='Output format for CI/CD integration')
    parser.add_argument('--export', type=str,
                       help='Export data to file')
    parser.add_argument('--ci-mode', action='store_true',
                       help='CI/CD mode: machine-readable output')
    
    args = parser.parse_args()
    
    tracker = HealthHistoryTracker()
    
    # CI mode overrides format
    if args.ci_mode:
        args.format = 'ci'
    
    if args.record_health:
        result = tracker.record_health_snapshot(notes=args.notes)
        if args.format in ['json', 'ci']:
            print(json.dumps({'health_recorded': True, 'timestamp': result.get('timestamp', '')}))
    elif args.generate_blog_entry:
        blog_path = tracker.generate_dev_blog_entry()
        if args.format in ['json', 'ci']:
            print(json.dumps({'blog_generated': str(blog_path)}))
    elif args.show_trends:
        comprehensive_trend_analysis_results = tracker.generate_comprehensive_health_trend_analysis_for_cicd_integration(analysis_period_days=args.days, output_format=args.format)
        if args.export:
            with open(args.export, 'w') as export_file_handle:
                if args.format == 'json':
                    json.dump(comprehensive_trend_analysis_results, export_file_handle, indent=2)
                else:
                    export_file_handle.write(str(comprehensive_trend_analysis_results))
    elif args.health_history:
        history = tracker.get_health_history(days=args.days)
        if args.format == 'json':
            print(json.dumps(history, indent=2))
        elif args.format == 'csv':
            print("timestamp,overall_score,code_quality,issue_tracking,branch_health,test_metrics,documentation,automation")
            for record in history:
                print(f"{record['timestamp']},{record['overall_score']},{record['code_quality']},{record['issue_tracking']},{record['branch_health']},{record['test_metrics']},{record['documentation']},{record['automation']}")
        else:
            print(f"[DATA] HEALTH HISTORY (Last {args.days} days):")
            for record in history:
                date = datetime.fromisoformat(record['timestamp']).strftime('%m/%d %H:%M')
                print(f"   {date}: Score {record['overall_score']}/100")
    elif args.dashboard:
        tracker.show_health_dashboard()
    else:
        # Default: show dashboard
        tracker.show_health_dashboard()


if __name__ == '__main__':
    main()