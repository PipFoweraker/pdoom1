# !/usr/bin/env python3
'''
Cleanup script for duplicate GitHub issues created by sync tool failure.
Target: Issues #313-#359 created on 2025-09-16 between 07:05-07:06Z
'''

import subprocess
import json
import sys

def get_duplicate_issues():
    '''Get all issues created during the sync failure window.'''
    cmd = [
        'gh', 'issue', 'list', 
        '--state', 'all', 
        '--limit', '1000',
        '--json', 'number,title,createdAt'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f'Error fetching issues: {result.stderr}')
            return []
            
        issues = json.loads(result.stdout)
        
        # Filter to sync failure window: 2025-09-16T07:05-07:06
        duplicates = []
        for issue in issues:
            created = issue['createdAt']
            if created.startswith('2025-09-16T07:05') or created.startswith('2025-09-16T07:06'):
                duplicates.append(issue)
                
        return sorted(duplicates, key=lambda x: x['number'])
        
    except Exception as e:
        print(f'Error: {e}')
        return []

def delete_issues(issues, dry_run=True):
    '''Delete the duplicate issues.'''
    print(f'{'[SEARCH] DRY RUN' if dry_run else '[EMOJI][EMOJI] DELETING'} - Found {len(issues)} duplicate issues:')
    
    for issue in issues:
        print(f'  #{issue['number']}: {issue['title']}')
        
        if not dry_run:
            cmd = ['gh', 'issue', 'delete', str(issue['number']), '--yes']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    print(f'    [EMOJI] Deleted #{issue['number']}')
                else:
                    print(f'    [EMOJI] Failed to delete #{issue['number']}: {result.stderr}')
            except Exception as e:
                print(f'    [EMOJI] Error deleting #{issue['number']}: {e}')

def main():
    dry_run = '--execute' not in sys.argv
    
    print('GitHub Issue Duplicate Cleanup')
    print('=' * 40)
    
    duplicates = get_duplicate_issues()
    
    if not duplicates:
        print('No duplicate issues found.')
        return
        
    delete_issues(duplicates, dry_run)
    
    if dry_run:
        print('\n[SEARCH] This was a dry run. Use --execute to actually delete issues.')
        print('[WARNING][EMOJI]  WARNING: This will permanently delete these GitHub issues!')
    else:
        print(f'\n[EMOJI] Cleanup complete. Deleted {len(duplicates)} duplicate issues.')

if __name__ == '__main__':
    main()
