# !/usr/bin/env python3
"""
Quick GitHub Token Setup Guide for P(Doom) Cross-Repository Sync

This script provides step-by-step instructions without hanging or external dependencies.
"""

def main():
    print("[EMOJI] GitHub Token Setup for Cross-Repository Documentation Sync")
    print("=" * 60)
    
    print("\n[CHECKLIST] STEP 1: Create Personal Access Token")
    print("1. Open: https://github.com/settings/tokens/new")
    print("2. Token name: 'P(Doom) Cross-Repository Sync'")
    print("3. Expiration: 1 year (or your preference)")
    print("4. Select these scopes:")
    print("   [EMOJI] repo (Full control of private repositories)")
    print("   [EMOJI] workflow (Update GitHub Action workflows)")
    print("5. Click 'Generate token' and COPY the token")
    
    print("\n[CHECKLIST] STEP 2: Add Token as Repository Secret")
    print("1. Open: https://github.com/PipFoweraker/pdoom1/settings/secrets/actions")
    print("2. Click 'New repository secret'")
    print("3. Name: CROSS_REPO_TOKEN")
    print("4. Secret: Paste your token")
    print("5. Click 'Add secret'")
    
    print("\n[CHECKLIST] STEP 3: Test the Setup")
    print("Method 1 - Manual trigger:")
    print("1. Go to: https://github.com/PipFoweraker/pdoom1/actions")
    print("2. Find 'Sync Documentation Across Repositories'")
    print("3. Click 'Run workflow' -> 'Run workflow'")
    
    print("\nMethod 2 - Make a documentation change:")
    print("1. Edit any file in docs/shared/")
    print("2. Commit and push the change")
    print("3. Check GitHub Actions for automatic sync")
    
    print("\n[EMOJI] SUCCESS INDICATORS:")
    print("- Workflow runs without errors")
    print("- Documentation appears in pdoom1-website/docs/")
    print("- Documentation appears in pdoom-data/docs/")
    print("- Files have sync headers with timestamps")
    
    print("\n[EMOJI] Quick Links:")
    print("Token creation: https://github.com/settings/tokens/new")
    print("Repository secrets: https://github.com/PipFoweraker/pdoom1/settings/secrets/actions")
    print("Actions page: https://github.com/PipFoweraker/pdoom1/actions")
    
    print("\n" + "=" * 60)
    print("[IDEA] Tip: The VS Code GitHub extension can also help with authentication!")

if __name__ == "__main__":
    main()
