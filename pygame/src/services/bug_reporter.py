'''
Bug reporting system for P(Doom) - Privacy-focused feedback collection.

This module provides functionality for players to report bugs, suggest features,
or provide feedback while maintaining privacy and offering flexible submission options.
'''

import json
import os
import datetime
import platform
import sys


class BugReporter:
    '''
    Privacy-focused bug reporting system.
    
    Collects minimal necessary information for debugging while protecting user privacy.
    Offers options for GitHub submission or local save with optional attribution.
    '''
    
    def __init__(self):
        self.reports_dir = 'bug_reports'
        self.ensure_reports_directory()
    
    def ensure_reports_directory(self):
        '''Create bug reports directory if it doesn't exist.'''
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def collect_system_info(self):
        '''
        Collect minimal system information for debugging.
        
        Only collects essential technical details, no personal information.
        '''
        return {
            'os_type': platform.system(),  # Linux/Windows/Darwin only
            'python_version': f'{sys.version_info.major}.{sys.version_info.minor}',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    
    def create_bug_report(self, report_type, title, description, 
                         steps_to_reproduce='', expected_behavior='', 
                         actual_behavior='', include_attribution=False, 
                         attribution_name='', contact_info=''):
        '''
        Create a structured bug report.
        
        Args:
            report_type: 'bug', 'feature_request', 'feedback'
            title: Brief summary of the issue
            description: Detailed description
            steps_to_reproduce: How to reproduce the issue
            expected_behavior: What should happen
            actual_behavior: What actually happens
            include_attribution: Whether to include user's name in report
            attribution_name: Name for attribution (if requested)
            contact_info: Optional contact information
        
        Returns:
            dict: Structured bug report ready for submission or saving
        '''
        system_info = self.collect_system_info()
        
        report = {
            'report_type': report_type,
            'title': title,
            'description': description,
            'system_info': system_info,
            'created_at': system_info['timestamp']
        }
        
        # Optional fields
        if steps_to_reproduce:
            report['steps_to_reproduce'] = steps_to_reproduce
        if expected_behavior:
            report['expected_behavior'] = expected_behavior
        if actual_behavior:
            report['actual_behavior'] = actual_behavior
        
        # Attribution (optional)
        if include_attribution and attribution_name:
            report['attribution'] = {
                'name': attribution_name,
                'contact': contact_info if contact_info else None
            }
        else:
            report['attribution'] = None
        
        return report
    
    def save_report_locally(self, report):
        '''
        Save bug report to local file system.
        
        Args:
            report: Bug report dictionary
            
        Returns:
            str: Path to saved report file
        '''
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f'bug_report_{timestamp}.json'
        filepath = os.path.join(self.reports_dir, filename)
        
        # Handle filename collisions by adding a counter
        counter = 1
        while os.path.exists(filepath):
            filename = f'bug_report_{timestamp}_{counter:02d}.json'
            filepath = os.path.join(self.reports_dir, filename)
            counter += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def format_for_github(self, report):
        '''
        Format bug report for GitHub issue submission.
        
        Args:
            report: Bug report dictionary
            
        Returns:
            dict: Title and body formatted for GitHub
        '''
        # Create GitHub issue title
        issue_type = report['report_type'].replace('_', ' ').title()
        title = f'[{issue_type}] {report['title']}'
        
        # Create GitHub issue body
        body_parts = []
        
        # Header
        body_parts.append(f'**Type:** {report['report_type'].replace('_', ' ').title()}')
        body_parts.append('')
        
        # Description
        body_parts.append('**Description:**')
        body_parts.append(report['description'])
        body_parts.append('')
        
        # Optional sections
        if 'steps_to_reproduce' in report and report['steps_to_reproduce']:
            body_parts.append('**Steps to Reproduce:**')
            body_parts.append(report['steps_to_reproduce'])
            body_parts.append('')
        
        if 'expected_behavior' in report and report['expected_behavior']:
            body_parts.append('**Expected Behavior:**')
            body_parts.append(report['expected_behavior'])
            body_parts.append('')
        
        if 'actual_behavior' in report and report['actual_behavior']:
            body_parts.append('**Actual Behavior:**')
            body_parts.append(report['actual_behavior'])
            body_parts.append('')
        
        # System information
        body_parts.append('**System Information:**')
        system_info = report['system_info']
        body_parts.append(f'- OS: {system_info['os_type']}')
        body_parts.append(f'- Python: {system_info['python_version']}')
        body_parts.append(f'- Reported: {system_info['timestamp']}')
        body_parts.append('')
        
        # Attribution
        if report.get('attribution') and report['attribution']:
            attribution = report['attribution']
            body_parts.append(f'**Reported by:** {attribution['name']}')
            if attribution.get('contact'):
                body_parts.append(f'**Contact:** {attribution['contact']}')
        else:
            body_parts.append('**Reported by:** Anonymous')
        
        return {
            'title': title,
            'body': '\n'.join(body_parts)
        }
    
    def get_recent_reports(self, limit=10):
        '''
        Get list of recent bug reports from local storage.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            list: List of recent report filenames
        '''
        if not os.path.exists(self.reports_dir):
            return []
        
        report_files = []
        for filename in os.listdir(self.reports_dir):
            if filename.startswith('bug_report_') and filename.endswith('.json'):
                filepath = os.path.join(self.reports_dir, filename)
                report_files.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by modification time (newest first)
        report_files.sort(key=lambda x: x[1], reverse=True)
        
        return [filepath for filepath, _ in report_files[:limit]]


def create_sample_report():
    '''Create a sample bug report for testing purposes.'''
    reporter = BugReporter()
    
    sample_report = reporter.create_bug_report(
        report_type='bug',
        title='Game crashes when clicking upgrade button',
        description='The game crashes with a Python error when I try to buy the Computer System upgrade.',
        steps_to_reproduce='1. Start new game\n2. Get enough money (>100)\n3. Click 'Computer System' upgrade\n4. Game crashes',
        expected_behavior='Upgrade should be purchased and game should continue',
        actual_behavior='Game crashes with IndexError',
        include_attribution=True,
        attribution_name='Test Player',
        contact_info='testplayer@example.com'
    )
    
    return sample_report


if __name__ == '__main__':
    # Demo usage
    reporter = BugReporter()
    sample = create_sample_report()
    
    print('Sample Bug Report:')
    print(json.dumps(sample, indent=2))
    
    print('\nGitHub Format:')
    github_format = reporter.format_for_github(sample)
    print(f'Title: {github_format['title']}')
    print(f'Body:\n{github_format['body']}')
    
    # Save locally
    filepath = reporter.save_report_locally(sample)
    print(f'\nSaved to: {filepath}')