# !/usr/bin/env python3
'''
GitHub Issue Sync Tool for P(Doom)
Prevents information loss by ensuring all local markdown issues are tracked in GitHub.
'''

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

class GitHubIssueSync:
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path)
        self.issues_dir = self.repo_path / 'issues'
        
    def get_local_issues(self) -> List[Dict]:
        '''Get all local markdown issues with metadata.'''
        issues = []
        for file_path in self.issues_dir.glob('*.md'):
            if file_path.name == 'README.md':
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract basic metadata
            issue = {
                'filename': file_path.name,
                'slug': file_path.stem,
                'content': content,
                'title': self._extract_title(content),
                'labels': self._extract_labels(content),
                'priority': self._extract_priority(content),
                'body': self._extract_body(content)
            }
            issues.append(issue)
            
        return issues
    
    def get_github_issues(self) -> List[Dict]:
        '''Get all GitHub issues via CLI.'''
        try:
            result = subprocess.run([
                'gh', 'issue', 'list', 
                '--state', 'all', 
                '--limit', '500',
                '--json', 'number,title,body,labels,state'
            ], capture_output=True, text=True, encoding='utf-8', cwd=self.repo_path)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f'Error fetching GitHub issues: {result.stderr}')
                return []
        except Exception as e:
            print(f'Error: {e}')
            return []
    
    def find_matching_github_issue(self, local_issue: Dict, github_issues: List[Dict]) -> Optional[Dict]:
        '''Find matching GitHub issue for local issue.'''
        local_title = local_issue['title'].lower()
        local_slug = local_issue['slug'].lower()
        
        for gh_issue in github_issues:
            gh_title = gh_issue['title'].lower()
            
            # Direct title match
            if local_title in gh_title or gh_title in local_title:
                return gh_issue
                
            # Slug-based matching
            slug_words = local_slug.replace('-', ' ').split()
            if len(slug_words) >= 2:
                if all(word in gh_title for word in slug_words if len(word) > 3):
                    return gh_issue
        
        return None
    
    def create_github_issue(self, local_issue: Dict) -> bool:
        '''Create a new GitHub issue from local markdown.'''
        title = local_issue['title']
        body = self._format_issue_body(local_issue)
        labels = local_issue.get('labels', [])
        
        cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]
        
        if labels:
            cmd.extend(['--label', ','.join(labels)])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='replace', cwd=self.repo_path)
            if result.returncode == 0:
                print(f'SUCCESS Created GitHub issue: {title}')
                return True
            else:
                print(f'ERROR Failed to create issue: {result.stderr}')
                return False
        except Exception as e:
            print(f'ERROR Error creating issue: {e}')
            return False
    
    def sync_issues(self, dry_run: bool = True) -> Dict:
        '''Sync all local issues to GitHub.'''
        local_issues = self.get_local_issues()
        github_issues = self.get_github_issues()
        
        results = {
            'total_local': len(local_issues),
            'total_github': len(github_issues),
            'matched': 0,
            'missing': [],
            'created': 0
        }
        
        print(f'[SEARCH] Analyzing {len(local_issues)} local vs {len(github_issues)} GitHub issues...')
        
        for local_issue in local_issues:
            match = self.find_matching_github_issue(local_issue, github_issues)
            
            if match:
                results['matched'] += 1
                print(f'[EMOJI] Found match: {local_issue['title']} -> #{match['number']}')
            else:
                results['missing'].append(local_issue)
                print(f'[EMOJI] Missing: {local_issue['title']} ({local_issue['filename']})')
                
                if not dry_run:
                    if self.create_github_issue(local_issue):
                        results['created'] += 1
        
        return results
    
    def _extract_title(self, content: str) -> str:
        '''Extract title from markdown content.'''
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback: use first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()
        
        return 'Untitled Issue'
    
    def _extract_labels(self, content: str) -> List[str]:
        '''Extract labels from content.'''
        labels = []
        
        # Look for common patterns
        if 'bug' in content.lower():
            labels.append('bug')
        if 'enhancement' in content.lower():
            labels.append('enhancement')
        if 'ui' in content.lower():
            labels.append('ui-ux')
        if 'critical' in content.lower():
            labels.append('priority-high')
        if 'documentation' in content.lower():
            labels.append('documentation')
            
        return labels
    
    def _extract_priority(self, content: str) -> str:
        '''Extract priority from content.'''
        content_lower = content.lower()
        if 'critical' in content_lower:
            return 'high'
        elif 'high' in content_lower:
            return 'high'
        elif 'medium' in content_lower:
            return 'medium'
        else:
            return 'low'
    
    def _extract_body(self, content: str) -> str:
        '''Extract body content, removing title.'''
        lines = content.split('\n')
        body_lines = []
        skip_first_header = True
        
        for line in lines:
            if skip_first_header and line.startswith('# '):
                skip_first_header = False
                continue
            body_lines.append(line)
        
        return '\n'.join(body_lines).strip()
    
    def _format_issue_body(self, local_issue: Dict) -> str:
        '''Format issue body for GitHub.'''
        body = local_issue['body']
        
        # Add metadata
        metadata = f'''
<!-- Auto-synced from local issues/{local_issue['filename']} -->

{body}

---
**Source:** `issues/{local_issue['filename']}`  
**Auto-synced:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
'''
        return metadata.strip()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync local markdown issues to GitHub')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without actually creating')
    parser.add_argument('--create', action='store_true', help='Actually create missing GitHub issues')
    
    args = parser.parse_args()
    
    syncer = GitHubIssueSync()
    
    if args.create:
        print('[ROCKET] CREATING MISSING GITHUB ISSUES')
        results = syncer.sync_issues(dry_run=False)
    else:
        print('[SEARCH] DRY RUN - Showing what would be created')
        results = syncer.sync_issues(dry_run=True)
    
    print(f'\n[CHART] SUMMARY:')
    print(f'Local issues: {results['total_local']}')
    print(f'GitHub issues: {results['total_github']}')
    print(f'Matched: {results['matched']}')
    print(f'Missing: {len(results['missing'])}')
    print(f'Created: {results['created']}')
    
    if results['missing'] and not args.create:
        print(f'\n[IDEA] Run with --create to actually create {len(results['missing'])} missing issues')

if __name__ == '__main__':
    main()
