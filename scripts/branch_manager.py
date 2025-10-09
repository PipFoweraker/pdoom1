# !/usr/bin/env python3
"""
Automated Branch Management System for P(Doom)

This script provides intelligent branch lifecycle management, including:
- Stale branch detection and cleanup
- Automated develop branch reset ("nuke from orbit")
- Feature branch creation from issues
- PR status tracking and auto-merge

Usage:
    python scripts/branch_manager.py --detect-stale
    python scripts/branch_manager.py --nuke-develop --confirm
    python scripts/branch_manager.py --cleanup-all --dry-run
    python scripts/branch_manager.py --auto-merge-ready
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class BranchInfo:
    """Information about a git branch."""
    
    def __init__(self, name: str, last_commit_date: datetime, 
                 last_commit_hash: str, author: str, is_merged: bool = False):
        self.name = name
        self.last_commit_date = last_commit_date
        self.last_commit_hash = last_commit_hash
        self.author = author
        self.is_merged = is_merged
        self.age_days = (datetime.now() - last_commit_date).days
    
    def __repr__(self):
        return f"BranchInfo(name='{self.name}', age_days={self.age_days}, author='{self.author}')"

class GitRepository:
    """Interface to git repository operations."""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or PROJECT_ROOT
        self.verify_git_repo()
    
    def verify_git_repo(self) -> None:
        """Verify we're in a git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise RuntimeError(f"Not a git repository: {self.repo_path}")
    
    def run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and return the result."""
        cmd = ['git'] + args
        try:
            return subprocess.run(cmd, cwd=self.repo_path, capture_output=True, 
                                text=True, check=check)
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            raise
    
    def get_all_branches(self, include_remote: bool = True) -> List[BranchInfo]:
        """Get information about all branches."""
        branches = []
        
        # Get local branches
        cmd_args = ['for-each-ref', '--format=%(refname:short)|%(committerdate:iso)|%(objectname:short)|%(authorname)', 'refs/heads']
        result = self.run_git_command(cmd_args)
        
        for line in result.stdout.strip().split('\\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) == 4:
                name, date_str, commit_hash, author = parts
                commit_date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                
                # Check if branch is merged
                is_merged = self.is_branch_merged(name)
                
                branches.append(BranchInfo(name, commit_date, commit_hash, author, is_merged))
        
        # Get remote branches if requested
        if include_remote:
            cmd_args = ['for-each-ref', '--format=%(refname:short)|%(committerdate:iso)|%(objectname:short)|%(authorname)', 'refs/remotes/origin']
            result = self.run_git_command(cmd_args)
            
            for line in result.stdout.strip().split('\\n'):
                if not line or 'origin/HEAD' in line:
                    continue
                parts = line.split('|')
                if len(parts) == 4:
                    name, date_str, commit_hash, author = parts
                    # Remove origin/ prefix
                    local_name = name.replace('origin/', '')
                    
                    # Skip if we already have the local version
                    if any(b.name == local_name for b in branches):
                        continue
                    
                    commit_date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                    branches.append(BranchInfo(name, commit_date, commit_hash, author, False))
        
        return branches
    
    def is_branch_merged(self, branch_name: str, target_branch: str = 'main') -> bool:
        """Check if a branch has been merged into target branch."""
        try:
            result = self.run_git_command(['merge-base', '--is-ancestor', branch_name, target_branch], check=False)
            return result.returncode == 0
        except:
            return False
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return result.stdout.strip()
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Delete a local branch."""
        flag = '-D' if force else '-d'
        try:
            self.run_git_command(['branch', flag, branch_name])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def delete_remote_branch(self, branch_name: str) -> bool:
        """Delete a remote branch."""
        try:
            self.run_git_command(['push', 'origin', '--delete', branch_name])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_branch(self, branch_name: str, start_point: str = 'main') -> bool:
        """Create a new branch from start_point."""
        try:
            self.run_git_command(['checkout', '-b', branch_name, start_point])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def reset_branch_to_main(self, branch_name: str, force: bool = False) -> bool:
        """Reset a branch to match main branch."""
        try:
            # Fetch latest
            self.run_git_command(['fetch', 'origin'])
            
            # Checkout the branch
            self.run_git_command(['checkout', branch_name])
            
            # Reset to main
            reset_flag = '--hard' if force else '--mixed'
            self.run_git_command(['reset', reset_flag, 'origin/main'])
            
            # Force push if requested
            if force:
                self.run_git_command(['push', 'origin', branch_name, '--force-with-lease'])
            
            return True
        except subprocess.CalledProcessError:
            return False

class PullRequestManager:
    """Manages GitHub Pull Requests via GitHub CLI."""
    
    def __init__(self):
        self.verify_gh_cli()
    
    def verify_gh_cli(self) -> None:
        """Verify GitHub CLI is available and authenticated."""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True)
            if result.returncode != 0:
                raise RuntimeError("GitHub CLI not authenticated")
        except FileNotFoundError:
            raise RuntimeError("GitHub CLI not found")
    
    def get_all_prs(self) -> List[Dict[str, Any]]:
        """Get all pull requests."""
        try:
            cmd = ['gh', 'pr', 'list', '--limit', '100', '--json', 
                   'number,title,headRefName,baseRefName,state,mergeable,checks']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return []
    
    def get_ready_to_merge_prs(self) -> List[Dict[str, Any]]:
        """Get PRs that are ready to be auto-merged."""
        all_prs = self.get_all_prs()
        ready_prs = []
        
        for pr in all_prs:
            if (pr['state'] == 'OPEN' and 
                pr.get('mergeable') == 'MERGEABLE' and
                self._all_checks_passed(pr.get('checks', []))):
                ready_prs.append(pr)
        
        return ready_prs
    
    def _all_checks_passed(self, checks: List[Dict[str, Any]]) -> bool:
        """Check if all PR checks have passed."""
        if not checks:
            return False
        
        for check in checks:
            if check.get('conclusion') != 'SUCCESS':
                return False
        
        return True
    
    def auto_merge_pr(self, pr_number: int) -> bool:
        """Auto-merge a PR with squash."""
        try:
            cmd = ['gh', 'pr', 'merge', str(pr_number), '--squash', '--auto']
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

class BranchManager:
    """Main branch management orchestrator."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.git = GitRepository()
        self.pr_manager = PullRequestManager()
        self.actions_log = []
    
    def detect_stale_branches(self, stale_days: int = 30, 
                            exclude_branches: List[str] = None) -> List[BranchInfo]:
        """Detect branches that haven't been updated in stale_days."""
        if exclude_branches is None:
            exclude_branches = ['main', 'develop', 'master']
        
        all_branches = self.git.get_all_branches()
        stale_branches = []
        
        for branch in all_branches:
            if (branch.name not in exclude_branches and 
                branch.age_days > stale_days and
                not branch.is_merged):
                stale_branches.append(branch)
        
        return stale_branches
    
    def cleanup_stale_branches(self, stale_days: int = 30, 
                              auto_delete_merged: bool = True) -> None:
        """Clean up stale branches."""
        print(f"SEARCH Detecting stale branches (older than {stale_days} days)...")
        
        stale_branches = self.detect_stale_branches(stale_days)
        merged_branches = [b for b in stale_branches if b.is_merged]
        unmerged_branches = [b for b in stale_branches if not b.is_merged]
        
        print(f"METRICS Found {len(stale_branches)} stale branches:")
        print(f"   - {len(merged_branches)} merged (safe to delete)")
        print(f"   - {len(unmerged_branches)} unmerged (require review)")
        print()
        
        # Auto-delete merged branches
        if auto_delete_merged and merged_branches:
            print("TRASH  Auto-deleting merged branches:")
            for branch in merged_branches:
                self._delete_branch_safely(branch)
        
        # Report unmerged branches for manual review
        if unmerged_branches:
            print("WARNING  Unmerged stale branches requiring manual review:")
            for branch in unmerged_branches:
                print(f"   - {branch.name} (age: {branch.age_days} days, author: {branch.author})")
                # TODO: Create GitHub issue for manual review
    
    def nuke_develop_branch(self, confirm: bool = False) -> None:
        """Reset develop branch to match main (nuclear option)."""
        if not confirm:
            print("ERROR --confirm flag required for develop branch reset")
            print("   This is a destructive operation that will:")
            print("   1. Delete the current develop branch")
            print("   2. Create a new develop branch from main")
            print("   3. Force push to origin/develop")
            print()
            print("   Run with --confirm flag if you're sure")
            return
        
        print("💥 NUCLEAR OPTION: Resetting develop branch to match main")
        print("   This will permanently destroy the current develop branch!")
        
        current_branch = self.git.get_current_branch()
        
        try:
            # Step 1: Switch to main
            if self.dry_run:
                print("[DRY RUN] Would checkout main branch")
            else:
                self.git.run_git_command(['checkout', 'main'])
                print("SUCCESS Switched to main branch")
            
            # Step 2: Fetch latest changes
            if self.dry_run:
                print("[DRY RUN] Would fetch latest changes")
            else:
                self.git.run_git_command(['fetch', 'origin'])
                print("SUCCESS Fetched latest changes")
            
            # Step 3: Delete local develop branch
            if self.dry_run:
                print("[DRY RUN] Would delete local develop branch")
            else:
                success = self.git.delete_branch('develop', force=True)
                if success:
                    print("SUCCESS Deleted local develop branch")
                else:
                    print("WARNING  Local develop branch not found or already deleted")
            
            # Step 4: Create new develop branch from main
            if self.dry_run:
                print("[DRY RUN] Would create new develop branch from main")
            else:
                success = self.git.create_branch('develop', 'main')
                if success:
                    print("SUCCESS Created new develop branch from main")
                else:
                    raise RuntimeError("Failed to create new develop branch")
            
            # Step 5: Force push to origin
            if self.dry_run:
                print("[DRY RUN] Would force push to origin/develop")
            else:
                self.git.run_git_command(['push', 'origin', 'develop', '--force-with-lease'])
                print("SUCCESS Force pushed new develop branch to origin")
            
            # Step 6: Return to original branch if it still exists
            if current_branch != 'develop':
                if self.dry_run:
                    print(f"[DRY RUN] Would return to {current_branch} branch")
                else:
                    try:
                        self.git.run_git_command(['checkout', current_branch])
                        print(f"SUCCESS Returned to {current_branch} branch")
                    except:
                        print(f"WARNING  Could not return to {current_branch}, staying on develop")
            
            print()
            print("TARGET Develop branch reset complete!")
            print("   - develop branch now matches main exactly")
            print("   - All previous develop commits are lost")
            print("   - Remote develop branch has been updated")
            
            self.actions_log.append({
                'action': 'nuke_develop',
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'success': True
            })
            
        except Exception as e:
            print(f"ERROR Error during develop branch reset: {e}")
            self.actions_log.append({
                'action': 'nuke_develop',
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'success': False,
                'error': str(e)
            })
            raise
    
    def auto_merge_ready_prs(self) -> None:
        """Automatically merge PRs that are ready."""
        print("SEARCH Checking for PRs ready to auto-merge...")
        
        ready_prs = self.pr_manager.get_ready_to_merge_prs()
        
        if not ready_prs:
            print("SUCCESS No PRs ready for auto-merge")
            return
        
        print(f"LAUNCH Found {len(ready_prs)} PRs ready for auto-merge:")
        
        for pr in ready_prs:
            pr_number = pr['number']
            title = pr['title']
            branch = pr['headRefName']
            
            if self.dry_run:
                print(f"[DRY RUN] Would auto-merge PR #{pr_number}: {title}")
            else:
                success = self.pr_manager.auto_merge_pr(pr_number)
                if success:
                    print(f"SUCCESS Auto-merged PR #{pr_number}: {title}")
                    
                    # Schedule branch cleanup
                    self._schedule_branch_cleanup(branch)
                else:
                    print(f"ERROR Failed to auto-merge PR #{pr_number}: {title}")
            
            self.actions_log.append({
                'action': 'auto_merge_pr',
                'pr_number': pr_number,
                'title': title,
                'branch': branch,
                'dry_run': self.dry_run
            })
    
    def _delete_branch_safely(self, branch: BranchInfo) -> None:
        """Safely delete a branch (local and remote)."""
        branch_name = branch.name.replace('origin/', '')
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete branch: {branch_name}")
            return
        
        # Delete local branch
        local_success = self.git.delete_branch(branch_name, force=True)
        
        # Delete remote branch if it exists
        remote_success = True
        if branch.name.startswith('origin/'):
            remote_success = self.git.delete_remote_branch(branch_name)
        
        if local_success or remote_success:
            print(f"SUCCESS Deleted branch: {branch_name}")
        else:
            print(f"WARNING  Failed to delete branch: {branch_name}")
        
        self.actions_log.append({
            'action': 'delete_branch',
            'branch_name': branch_name,
            'age_days': branch.age_days,
            'author': branch.author,
            'dry_run': self.dry_run,
            'success': local_success or remote_success
        })
    
    def _schedule_branch_cleanup(self, branch_name: str) -> None:
        """Schedule a branch for cleanup after PR merge."""
        # Wait a bit for GitHub to process the merge
        import time
        time.sleep(2)
        
        if self.dry_run:
            print(f"[DRY RUN] Would schedule cleanup for branch: {branch_name}")
        else:
            success = self.git.delete_branch(branch_name, force=False)
            if success:
                print(f"🧹 Cleaned up merged branch: {branch_name}")
    
    def generate_branch_report(self) -> None:
        """Generate a comprehensive branch status report."""
        print("METRICS Branch Status Report")
        print("=" * 50)
        
        all_branches = self.git.get_all_branches()
        current_branch = self.git.get_current_branch()
        
        # Categorize branches
        active_branches = [b for b in all_branches if b.age_days <= 7]
        recent_branches = [b for b in all_branches if 7 < b.age_days <= 30]
        stale_branches = [b for b in all_branches if b.age_days > 30]
        merged_branches = [b for b in all_branches if b.is_merged]
        
        print(f"Current branch: {current_branch}")
        print(f"Total branches: {len(all_branches)}")
        print()
        
        print("GROWTH Branch Categories:")
        print(f"   Active (<=7 days):     {len(active_branches)}")
        print(f"   Recent (8-30 days):   {len(recent_branches)}")
        print(f"   Stale (>30 days):     {len(stale_branches)}")
        print(f"   Merged:               {len(merged_branches)}")
        print()
        
        if stale_branches:
            print("WARNING  Stale Branches (>30 days old):")
            for branch in sorted(stale_branches, key=lambda x: x.age_days, reverse=True):
                status = "merged" if branch.is_merged else "unmerged"
                print(f"   - {branch.name} ({branch.age_days} days, {status}, {branch.author})")
            print()
        
        # Check for PRs
        try:
            ready_prs = self.pr_manager.get_ready_to_merge_prs()
            if ready_prs:
                print(f"LAUNCH PRs Ready for Auto-merge: {len(ready_prs)}")
                for pr in ready_prs:
                    print(f"   - #{pr['number']}: {pr['title']}")
                print()
        except:
            print("WARNING  Could not fetch PR information (GitHub CLI issue)")
    
    def print_actions_summary(self) -> None:
        """Print summary of all actions performed."""
        if not self.actions_log:
            print("MEMO No actions performed")
            return
        
        print("\\nMEMO Actions Summary:")
        for entry in self.actions_log:
            action = entry['action']
            dry_run_prefix = "[DRY RUN] " if entry.get('dry_run') else ""
            
            if action == 'delete_branch':
                print(f"   {dry_run_prefix}Deleted branch: {entry['branch_name']} (age: {entry['age_days']} days)")
            elif action == 'auto_merge_pr':
                print(f"   {dry_run_prefix}Auto-merged PR #{entry['pr_number']}: {entry['title']}")
            elif action == 'nuke_develop':
                status = "SUCCESS" if entry['success'] else "FAILED"
                print(f"   {dry_run_prefix}Develop branch reset: {status}")

def main():
    parser = argparse.ArgumentParser(description='Automated Branch Management for P(Doom)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default)')
    parser.add_argument('--live', action='store_true',
                       help='Run in live mode (make actual changes)')
    
    # Action arguments
    parser.add_argument('--detect-stale', action='store_true',
                       help='Detect and report stale branches')
    parser.add_argument('--cleanup-all', action='store_true',
                       help='Clean up stale and merged branches')
    parser.add_argument('--nuke-develop', action='store_true',
                       help='Reset develop branch to match main (destructive!)')
    parser.add_argument('--confirm', action='store_true',
                       help='Confirm destructive operations')
    parser.add_argument('--auto-merge-ready', action='store_true',
                       help='Auto-merge ready PRs')
    parser.add_argument('--report', action='store_true',
                       help='Generate branch status report')
    
    # Configuration arguments
    parser.add_argument('--stale-days', type=int, default=30,
                       help='Days after which a branch is considered stale')
    
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.live
    
    try:
        manager = BranchManager(dry_run=dry_run)
        
        if args.report or len(sys.argv) == 1:
            manager.generate_branch_report()
        
        if args.detect_stale:
            stale_branches = manager.detect_stale_branches(args.stale_days)
            print(f"Found {len(stale_branches)} stale branches")
            for branch in stale_branches:
                print(f"  - {branch}")
        
        if args.cleanup_all:
            manager.cleanup_stale_branches(args.stale_days)
        
        if args.nuke_develop:
            manager.nuke_develop_branch(args.confirm)
        
        if args.auto_merge_ready:
            manager.auto_merge_ready_prs()
        
        manager.print_actions_summary()
    
    except Exception as e:
        print(f"ERROR Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()