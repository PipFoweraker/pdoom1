# !/usr/bin/env python3
"""
P(Doom) Ecosystem Repository Status Dashboard

This script provides a quick overview of all repositories in the P(Doom) ecosystem,
including their status, recent activity, and synchronization state.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

class Colors:
    """Terminal colors for better output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def run_command(cmd, cwd=None, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_github_repo(repo_name):
    """Check if a GitHub repository exists and get basic info"""
    success, output, error = run_command(f'curl -s https://api.github.com/repos/{repo_name}')
    
    if success:
        try:
            data = json.loads(output)
            if 'message' in data and data['message'] == 'Not Found':
                return False, "Repository not found"
            
            return True, {
                'name': data.get('name', ''),
                'description': data.get('description', 'No description'),
                'updated_at': data.get('updated_at', ''),
                'open_issues': data.get('open_issues_count', 0),
                'language': data.get('language', 'Unknown'),
                'private': data.get('private', False)
            }
        except json.JSONDecodeError:
            return False, "Invalid response from GitHub API"
    
    return False, error

def check_local_repo(repo_path):
    """Check local repository status"""
    if not repo_path.exists():
        return False, "Directory not found"
    
    if not (repo_path / '.git').exists():
        return False, "Not a git repository"
    
    # Get current branch
    success, branch, _ = run_command('git branch --show-current', cwd=repo_path)
    if not success:
        branch = "unknown"
    
    # Get status
    success, status_output, _ = run_command('git status --porcelain', cwd=repo_path)
    uncommitted_files = len(status_output.split('\n')) if success and status_output else 0
    
    # Get last commit
    success, last_commit, _ = run_command(
        'git log -1 --pretty=format:"%h %s (%cr)"', 
        cwd=repo_path
    )
    if not success:
        last_commit = "No commits"
    
    # Check if ahead/behind remote
    success, ahead_behind, _ = run_command(
        f'git rev-list --left-right --count origin/{branch}...HEAD 2>/dev/null || echo "0	0"',
        cwd=repo_path
    )
    
    behind, ahead = 0, 0
    if success and ahead_behind:
        try:
            behind, ahead = map(int, ahead_behind.split('\t'))
        except ValueError:
            pass
    
    return True, {
        'branch': branch,
        'uncommitted_files': uncommitted_files,
        'last_commit': last_commit,
        'ahead': ahead,
        'behind': behind
    }

def print_header():
    """Print the dashboard header"""
    print(f"{Colors.BOLD}{Colors.CYAN}[EMOJI] P(Doom) Ecosystem Status Dashboard{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def print_repo_status(name, emoji, github_repo, local_path=None):
    """Print status for a single repository"""
    print(f"{Colors.BOLD}{emoji} {name}{Colors.END}")
    print("-" * 40)
    
    # Check GitHub status
    github_success, github_data = check_github_repo(github_repo)
    
    if github_success:
        print(f"  {Colors.GREEN}[EMOJI] GitHub: Active{Colors.END}")
        print(f"     Language: {github_data['language']}")
        print(f"     Open Issues: {github_data['open_issues']}")
        print(f"     Last Updated: {github_data['updated_at'][:10]}")
        if github_data['description']:
            print(f"     Description: {github_data['description']}")
    else:
        print(f"  {Colors.RED}[EMOJI] GitHub: {github_data}{Colors.END}")
    
    # Check local status if path provided
    if local_path:
        local_success, local_data = check_local_repo(Path(local_path))
        
        if local_success:
            print(f"  {Colors.GREEN}[EMOJI] Local: Available{Colors.END}")
            print(f"     Branch: {local_data['branch']}")
            print(f"     Uncommitted: {local_data['uncommitted_files']} files")
            print(f"     Last Commit: {local_data['last_commit']}")
            
            if local_data['ahead'] > 0:
                print(f"     {Colors.YELLOW}[UP_ARROW][EMOJI]  {local_data['ahead']} commits ahead{Colors.END}")
            if local_data['behind'] > 0:
                print(f"     {Colors.YELLOW}[DOWN_ARROW][EMOJI]  {local_data['behind']} commits behind{Colors.END}")
        else:
            print(f"  {Colors.RED}[EMOJI] Local: {local_data}{Colors.END}")
    
    print()

def check_sync_status():
    """Check GitHub Actions sync status"""
    print(f"{Colors.BOLD}[EMOJI] Sync Status{Colors.END}")
    print("-" * 40)
    
    # Check recent workflow runs
    success, output, _ = run_command('gh run list --limit 5 --json status,conclusion,name,createdAt')
    
    if success:
        try:
            runs = json.loads(output)
            for run in runs:
                status = run.get('status', 'unknown')
                conclusion = run.get('conclusion', 'unknown')
                name = run.get('name', 'Unknown workflow')
                created = run.get('createdAt', '')[:10]
                
                if conclusion == 'success':
                    status_icon = f"{Colors.GREEN}[EMOJI]{Colors.END}"
                elif conclusion == 'failure':
                    status_icon = f"{Colors.RED}[EMOJI]{Colors.END}"
                elif status == 'in_progress':
                    status_icon = f"{Colors.YELLOW}[EMOJI]{Colors.END}"
                else:
                    status_icon = f"{Colors.YELLOW}[U+23F8][EMOJI]{Colors.END}"
                
                print(f"  {status_icon} {name} ({created})")
        except json.JSONDecodeError:
            print(f"  {Colors.RED}[EMOJI] Failed to parse workflow data{Colors.END}")
    else:
        print(f"  {Colors.RED}[EMOJI] Could not fetch workflow status{Colors.END}")
    
    print()

def print_quick_actions():
    """Print available quick actions"""
    print(f"{Colors.BOLD}[LIGHTNING] Quick Actions{Colors.END}")
    print("-" * 40)
    print("  Clone website repository:")
    print(f"    {Colors.CYAN}git clone https://github.com/PipFoweraker/pdoom1-website.git{Colors.END}")
    print()
    print("  Create data repository:")
    print(f"    {Colors.CYAN}gh repo create PipFoweraker/pdoom-data --public{Colors.END}")
    print()
    print("  Trigger dev blog sync:")
    print(f"    {Colors.CYAN}gh workflow run sync-dev-blog.yml{Colors.END}")
    print()

def main():
    """Main dashboard function"""
    print_header()
    
    # Define repositories
    repositories = [
        {
            'name': 'Game Repository',
            'emoji': '[EMOJI]',
            'github': 'PipFoweraker/pdoom1',
            'local': '.'
        },
        {
            'name': 'Website Repository', 
            'emoji': '[EMOJI]',
            'github': 'PipFoweraker/pdoom1-website',
            'local': '../pdoom1-website'
        },
        {
            'name': 'Data Service Repository',
            'emoji': '[EMOJI][EMOJI]',
            'github': 'PipFoweraker/pdoom-data',
            'local': '../pdoom-data'
        }
    ]
    
    # Check each repository
    for repo in repositories:
        print_repo_status(
            repo['name'], 
            repo['emoji'], 
            repo['github'],
            repo.get('local')
        )
    
    # Check sync status
    check_sync_status()
    
    # Print quick actions
    print_quick_actions()

if __name__ == "__main__":
    main()
