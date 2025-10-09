# !/usr/bin/env python3
"""
Monitor the cross-repository documentation sync status
"""
import subprocess
import time
import sys

def check_workflow_status():
    """Check the status of recent workflow runs"""
    try:
        # Note: This requires GitHub CLI, but we'll provide manual instructions
        print("[EMOJI] Checking Cross-Repository Documentation Sync Status")
        print("=" * 60)
        
        print("[CHART] Manual Monitoring Instructions:")
        print("1. GitHub Actions: https://github.com/PipFoweraker/pdoom1/actions")
        print("2. Look for 'Sync Documentation Across Repositories' workflow")
        print("3. Recent run should show your commit: 'docs: test cross-repository sync functionality'")
        
        print("\n[EMOJI] Success Indicators to Look For:")
        print("- Workflow status: [EMOJI] (green checkmark)")
        print("- All jobs completed successfully")
        print("- No red [EMOJI] error indicators")
        
        print("\n[CHECKLIST] Results to Check After Workflow Completes:")
        print("1. pdoom1-website repository:")
        print("   https://github.com/PipFoweraker/pdoom1-website/tree/main/docs")
        print("   -> Should contain ECOSYSTEM_OVERVIEW.md with sync header")
        
        print("2. pdoom-data repository:")
        print("   https://github.com/PipFoweraker/pdoom-data/tree/main/docs")  
        print("   -> Should contain ECOSYSTEM_OVERVIEW.md with sync header")
        
        print("\n[EMOJI] If Workflow Fails:")
        print("- Check workflow logs for error messages")
        print("- Verify CROSS_REPO_TOKEN has correct permissions")
        print("- Ensure token has 'repo' and 'workflow' scopes")
        
        print("\n[TARGET] Quick Status Check Commands:")
        print("Run these to verify sync worked:")
        print("curl -s https://api.github.com/repos/PipFoweraker/pdoom1-website/contents/docs/ECOSYSTEM_OVERVIEW.md")
        print("curl -s https://api.github.com/repos/PipFoweraker/pdoom-data/contents/docs/ECOSYSTEM_OVERVIEW.md")
        
        return True
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return False

def main():
    print("[EMOJI] P(Doom) Cross-Repository Sync Monitor")
    print(f"Triggered at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print()
    
    success = check_workflow_status()
    
    if success:
        print("\n" + "=" * 60)
        print("[IDEA] The sync should complete within 2-3 minutes.")
        print("[IDEA] Check the GitHub Actions page for real-time progress!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
