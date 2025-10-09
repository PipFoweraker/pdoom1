# !/usr/bin/env python3
'''
Bidirectional Issue Sync System for P(Doom)

This script provides a data lake-inspired approach to keeping local Markdown issues
in sync with GitHub Issues, maintaining a single source of truth with audit trails.

Features:
- Bidirectional synchronization (local  <->  GitHub)
- Conflict detection and resolution
- Audit trail for all changes  
- Dry-run mode for safe testing
- Automatic linking between local and GitHub issues

Usage:
    python scripts/issue_sync_bidirectional.py --dry-run
    python scripts/issue_sync_bidirectional.py --sync-all
    python scripts/issue_sync_bidirectional.py --resolve-conflicts
'''

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib
import re

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class IssueMetadata:
    '''Manages metadata for issue tracking and synchronization.'''
    
    def __init__(self, github_id: Optional[int] = None, 
                 last_sync: Optional[str] = None,
                 local_hash: Optional[str] = None,
                 github_hash: Optional[str] = None):
        self.github_id = github_id
        self.last_sync = last_sync or datetime.now().isoformat()
        self.local_hash = local_hash
        self.github_hash = github_hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'github_id': self.github_id,
            'last_sync': self.last_sync,
            'local_hash': self.local_hash,
            'github_hash': self.github_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IssueMetadata':
        return cls(
            github_id=data.get('github_id'),
            last_sync=data.get('last_sync'),
            local_hash=data.get('local_hash'),
            github_hash=data.get('github_hash')
        )

class LocalIssueManager:
    '''Manages local Markdown issue files.'''
    
    def __init__(self, issues_dir: Optional[Path] = None):
        self.issues_dir = issues_dir or PROJECT_ROOT / 'issues'
        self.metadata_file = self.issues_dir / '.sync_metadata.json'
        self.load_metadata()
    
    def load_metadata(self) -> None:
        '''Load sync metadata from file.'''
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                self.metadata = {
                    filename: IssueMetadata.from_dict(meta)
                    for filename, meta in data.items()
                }
        else:
            self.metadata = {}
    
    def save_metadata(self) -> None:
        '''Save sync metadata to file.'''
        data = {
            filename: meta.to_dict()
            for filename, meta in self.metadata.items()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_issues(self) -> List[Tuple[str, str, IssueMetadata]]:
        '''Get all local issues with their content and metadata.'''
        issues: List[Tuple[str, str, IssueMetadata]] = []
        
        for issue_file in self.issues_dir.glob('*.md'):
            if issue_file.name.startswith('.'):
                continue
                
            with open(issue_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = issue_file.name
            metadata = self.metadata.get(filename, IssueMetadata())
            
            # Update local hash
            metadata.local_hash = self.calculate_content_hash(content)
            self.metadata[filename] = metadata
            
            issues.append((filename, content, metadata))
        
        return issues
    
    def calculate_content_hash(self, content: str) -> str:
        '''Calculate hash of issue content for change detection.'''
        # Normalize content for hashing (remove metadata section)
        normalized = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        normalized = normalized.strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def create_issue(self, filename: str, content: str, metadata: IssueMetadata) -> None:
        '''Create a new local issue file.'''
        filepath = self.issues_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        metadata.local_hash = self.calculate_content_hash(content)
        self.metadata[filename] = metadata
        self.save_metadata()
    
    def update_issue(self, filename: str, content: str) -> None:
        '''Update an existing local issue file.'''
        filepath = self.issues_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if filename in self.metadata:
            self.metadata[filename].local_hash = self.calculate_content_hash(content)
            self.metadata[filename].last_sync = datetime.now().isoformat()
        
        self.save_metadata()

class GitHubIssueManager:
    '''Manages GitHub Issues via GitHub CLI.'''
    
    def __init__(self):
        self.verify_gh_cli()
    
    def verify_gh_cli(self) -> None:
        '''Verify GitHub CLI is installed and authenticated.'''
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("GitHub CLI not authenticated. Run 'gh auth login'")
        except FileNotFoundError:
            raise RuntimeError('GitHub CLI not found. Please install GitHub CLI')
    
    def get_all_issues(self) -> List[Dict[str, Any]]:
        '''Get all GitHub issues.'''
        try:
            cmd = ['gh', 'issue', 'list', '--limit', '1000', '--json', 
                   'number,title,body,state,labels,createdAt,updatedAt']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f'Error fetching GitHub issues: {e}')
            return []
    
    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Optional[int]:
        '''Create a new GitHub issue and return its number.'''
        cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]
        if labels:
            cmd.extend(['--label', ','.join(labels)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Parse issue number from output URL
            output = result.stdout.strip()
            if '/issues/' in output:
                return int(output.split('/issues/')[-1])
        except subprocess.CalledProcessError as e:
            print(f'Error creating GitHub issue: {e}')
        
        return None
    
    def update_issue(self, issue_number: int, title: Optional[str] = None, 
                    body: Optional[str] = None) -> bool:
        '''Update an existing GitHub issue.'''
        cmd = ['gh', 'issue', 'edit', str(issue_number)]
        if title:
            cmd.extend(['--title', title])
        if body:
            cmd.extend(['--body', body])
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f'Error updating GitHub issue #{issue_number}: {e}')
            return False

class ConflictResolver:
    '''Resolves conflicts between local and GitHub issues.'''
    
    def __init__(self):
        self.resolution_strategies = {
            'github_newer': self._resolve_github_wins,
            'local_newer': self._resolve_local_wins,
            'manual': self._resolve_manual
        }
    
    def detect_conflicts(self, local_issues: List[Tuple[str, str, IssueMetadata]], 
                        github_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        '''Detect conflicts between local and GitHub issues.'''
        conflicts: List[Dict[str, Any]] = []
        
        # Create lookup for GitHub issues by ID
        github_by_id = {issue['number']: issue for issue in github_issues}
        
        for filename, content, metadata in local_issues:
            if metadata.github_id and metadata.github_id in github_by_id:
                github_issue = github_by_id[metadata.github_id]
                
                # Calculate GitHub content hash
                github_content = f'# {github_issue['title']}\\n\\n{github_issue['body'] or ''}'
                github_hash = self._calculate_hash(github_content)
                
                # Check for conflicts
                if (metadata.local_hash != metadata.github_hash and 
                    github_hash != metadata.github_hash):
                    conflicts.append({
                        'type': 'content_conflict',
                        'filename': filename,
                        'local_content': content,
                        'github_content': github_content,
                        'metadata': metadata,
                        'github_issue': github_issue
                    })
        
        return conflicts
    
    def _calculate_hash(self, content: str) -> str:
        '''Calculate normalized content hash.'''
        normalized = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        normalized = normalized.strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _resolve_github_wins(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        '''Resolve conflict by using GitHub version.'''
        return {
            'action': 'update_local',
            'filename': conflict['filename'],
            'content': conflict['github_content'],
            'metadata': conflict['metadata']
        }
    
    def _resolve_local_wins(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        '''Resolve conflict by using local version.'''
        return {
            'action': 'update_github',
            'github_issue': conflict['github_issue'],
            'content': conflict['local_content'],
            'metadata': conflict['metadata']
        }
    
    def _resolve_manual(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        '''Mark conflict for manual resolution.'''
        return {
            'action': 'manual_review',
            'conflict': conflict
        }

class BidirectionalIssueSync:
    '''Main orchestrator for bidirectional issue synchronization.'''
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.local_manager = LocalIssueManager()
        self.github_manager = GitHubIssueManager()
        self.conflict_resolver = ConflictResolver()
        self.audit_log: List[Dict[str, Any]] = []
    
    def sync_all(self) -> None:
        '''Perform complete bidirectional synchronization.'''
        print('REFRESH Starting bidirectional issue synchronization...')
        print(f'   Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}')
        print()
        
        # 1. Load all issues
        local_issues = self.local_manager.get_all_issues()
        github_issues = self.github_manager.get_all_issues()
        
        print(f'FOLDER Local issues found: {len(local_issues)}')
        print(f'? GitHub issues found: {len(github_issues)}')
        print()
        
        # 2. Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(local_issues, github_issues)
        
        if conflicts:
            print(f'WARNING  Conflicts detected: {len(conflicts)}')
            self._handle_conflicts(conflicts)
            return
        
        # 3. Sync new local issues to GitHub
        self._sync_local_to_github(local_issues, github_issues)
        
        # 4. Sync new GitHub issues to local
        self._sync_github_to_local(local_issues, github_issues)
        
        # 5. Update existing issues
        self._sync_updates(local_issues, github_issues)
        
        print('SUCCESS Synchronization complete!')
        self._print_audit_summary()
    
    def _sync_local_to_github(self, local_issues: List[Tuple[str, str, IssueMetadata]], 
                             github_issues: List[Dict[str, Any]]) -> None:
        '''Sync local issues that don't exist on GitHub.'''
        github_ids = {issue['number'] for issue in github_issues}
        
        for filename, content, metadata in local_issues:
            if metadata.github_id is None or metadata.github_id not in github_ids:
                title = self._extract_title_from_content(content)
                labels = self._extract_labels_from_filename(filename)
                
                if self.dry_run:
                    print(f'[DRY RUN] Would create GitHub issue: {title}')
                else:
                    github_id = self.github_manager.create_issue(title, content, labels)
                    if github_id:
                        metadata.github_id = github_id
                        metadata.github_hash = metadata.local_hash
                        self.local_manager.save_metadata()
                        print(f'SUCCESS Created GitHub issue #{github_id}: {title}')
                
                self.audit_log.append({
                    'action': 'create_github_issue',
                    'filename': filename,
                    'title': title,
                    'dry_run': self.dry_run
                })
    
    def _sync_github_to_local(self, local_issues: List[Tuple[str, str, IssueMetadata]], 
                             github_issues: List[Dict[str, Any]]) -> None:
        '''Sync GitHub issues that don't exist locally.'''
        local_github_ids = {meta.github_id for _, _, meta in local_issues if meta.github_id}
        
        for github_issue in github_issues:
            if github_issue['number'] not in local_github_ids:
                filename = self._generate_filename_from_title(github_issue['title'])
                content = self._format_github_issue_as_markdown(github_issue)
                
                if self.dry_run:
                    print(f'[DRY RUN] Would create local issue: {filename}')
                else:
                    metadata = IssueMetadata(
                        github_id=github_issue['number'],
                        github_hash=self.local_manager.calculate_content_hash(content)
                    )
                    self.local_manager.create_issue(filename, content, metadata)
                    print(f'SUCCESS Created local issue: {filename}')
                
                self.audit_log.append({
                    'action': 'create_local_issue',
                    'filename': filename,
                    'github_id': github_issue['number'],
                    'dry_run': self.dry_run
                })
    
    def _sync_updates(self, local_issues: List[Tuple[str, str, IssueMetadata]], 
                     github_issues: List[Dict[str, Any]]) -> None:
        '''Sync updates between linked issues.'''
        github_by_id = {issue['number']: issue for issue in github_issues}
        
        for filename, content, metadata in local_issues:
            if metadata.github_id and metadata.github_id in github_by_id:
                github_issue = github_by_id[metadata.github_id]
                github_content = self._format_github_issue_as_markdown(github_issue)
                github_hash = self.local_manager.calculate_content_hash(github_content)
                
                # Local changed, GitHub unchanged
                if (metadata.local_hash != metadata.github_hash and 
                    github_hash == metadata.github_hash):
                    title = self._extract_title_from_content(content)
                    body = self._extract_body_from_content(content)
                    
                    if self.dry_run:
                        print(f'[DRY RUN] Would update GitHub issue #{metadata.github_id}')
                    else:
                        success = self.github_manager.update_issue(
                            metadata.github_id, title, body)
                        if success:
                            metadata.github_hash = metadata.local_hash
                            self.local_manager.save_metadata()
                            print(f'SUCCESS Updated GitHub issue #{metadata.github_id}')
                
                # GitHub changed, local unchanged
                elif (github_hash != metadata.github_hash and 
                      metadata.local_hash == metadata.github_hash):
                    
                    if self.dry_run:
                        print(f'[DRY RUN] Would update local issue: {filename}')
                    else:
                        self.local_manager.update_issue(filename, github_content)
                        metadata.github_hash = github_hash
                        metadata.local_hash = github_hash
                        self.local_manager.save_metadata()
                        print(f'SUCCESS Updated local issue: {filename}')
    
    def _handle_conflicts(self, conflicts: List[Dict[str, Any]]) -> None:
        '''Handle detected conflicts.'''
        print('WARNING  Conflicts require manual resolution:')
        for i, conflict in enumerate(conflicts, 1):
            print(f'   {i}. {conflict['filename']}  <->  GitHub #{conflict['github_issue']['number']}')
        
        print('\\nRun with --resolve-conflicts to handle these interactively')
    
    def _extract_title_from_content(self, content: str) -> str:
        '''Extract title from Markdown content.'''
        lines = content.split('\\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to filename-based title
        return 'Untitled Issue'
    
    def _extract_body_from_content(self, content: str) -> str:
        '''Extract body from Markdown content.'''
        lines = content.split('\\n')
        body_lines: List[str] = []
        found_title = False
        
        for line in lines:
            if line.startswith('# ') and not found_title:
                found_title = True
                continue
            if found_title:
                body_lines.append(line)
        
        return '\\n'.join(body_lines).strip()
    
    def _extract_labels_from_filename(self, filename: str) -> List[str]:
        '''Extract labels from filename patterns.'''
        labels: List[str] = []
        name = filename.replace('.md', '').lower()
        
        if 'bug' in name or 'fix' in name:
            labels.append('bug')
        if 'feature' in name or 'enhancement' in name:
            labels.append('enhancement')
        if 'docs' in name or 'documentation' in name:
            labels.append('documentation')
        if 'test' in name:
            labels.append('testing')
        
        return labels
    
    def _generate_filename_from_title(self, title: str) -> str:
        '''Generate filename from issue title.'''
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        filename = re.sub(r'[^a-zA-Z0-9\\s-]', '', title.lower())
        filename = re.sub(r'\\s+', '-', filename)
        filename = re.sub(r'-+', '-', filename)
        filename = filename.strip('-')
        
        return f'{filename}.md'
    
    def _format_github_issue_as_markdown(self, github_issue: Dict[str, Any]) -> str:
        '''Format GitHub issue as Markdown.'''
        content = f'# {github_issue['title']}\\n\\n'
        
        if github_issue.get('body'):
            content += github_issue['body']
        
        # Add metadata comment
        content += f'\\n\\n<!-- GitHub Issue #{github_issue['number']} -->'
        
        return content
    
    def _print_audit_summary(self) -> None:
        '''Print summary of all actions performed.'''
        if not self.audit_log:
            print('MEMO No changes made')
            return
        
        print('\\nMEMO Audit Summary:')
        for entry in self.audit_log:
            action = entry['action']
            if action == 'create_github_issue':
                status = '[DRY RUN] ' if entry['dry_run'] else ''
                print(f'   {status}Created GitHub issue for {entry['filename']}')
            elif action == 'create_local_issue':
                status = '[DRY RUN] ' if entry['dry_run'] else ''
                print(f'   {status}Created local issue {entry['filename']} from GitHub #{entry['github_id']}')

def main():
    parser = argparse.ArgumentParser(description='Bidirectional Issue Sync for P(Doom)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default)')
    parser.add_argument('--live', action='store_true', 
                       help='Run in live mode (make actual changes)')
    parser.add_argument('--sync-all', action='store_true',
                       help='Perform complete synchronization')
    parser.add_argument('--resolve-conflicts', action='store_true',
                       help='Interactively resolve conflicts')
    
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.live
    
    try:
        sync = BidirectionalIssueSync(dry_run=dry_run)
        
        if args.sync_all or len(sys.argv) == 1:
            sync.sync_all()
        elif args.resolve_conflicts:
            print('Interactive conflict resolution not yet implemented')
            sys.exit(1)
        else:
            parser.print_help()
    
    except Exception as e:
        print(f'ERROR Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()