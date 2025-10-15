# !/usr/bin/env python3
'''
GitHub Token Setup Helper for VS Code Users
Helps set up cross-repository token through VS Code's GitHub integration
'''

import webbrowser
import json
import os
from pathlib import Path

def main():
    print('[ROCKET] GitHub Token Setup for P(Doom) Cross-Repository Sync')
    print('=' * 60)
    
    print('\n[CHECKLIST] Steps to set up the token:')
    print('1. Create Personal Access Token')
    print('2. Add token as repository secret')
    print('3. Test the documentation sync')
    
    choice = input('\n[EMOJI] Choose setup method:\n1. Open GitHub web interface\n2. VS Code Command Palette instructions\n3. Manual token creation guide\n\nEnter choice (1-3): ')
    
    if choice == '1':
        setup_web_interface()
    elif choice == '2':
        setup_vscode_integration()
    elif choice == '3':
        setup_manual_guide()
    else:
        print('Invalid choice. Please run the script again.')

def setup_web_interface():
    print('\n[EMOJI] Opening GitHub web interface...')
    
    # Token creation URL with pre-filled settings
    token_url = 'https://github.com/settings/tokens/new?' + \
                'scopes=repo,workflow,write:packages,read:packages&' + \
                'description=P(Doom) Cross-Repository Documentation Sync'
    
    secrets_url = 'https://github.com/PipFoweraker/pdoom1/settings/secrets/actions'
    
    print(f'[NOTE] Step 1: Create token')
    print(f'   Opening: {token_url}')
    webbrowser.open(token_url)
    
    input('\n[U+23F8][EMOJI]  Press Enter after creating and copying the token...')
    
    print(f'[EMOJI] Step 2: Add repository secret')
    print(f'   Opening: {secrets_url}')
    webbrowser.open(secrets_url)
    
    print('\n[CHECKLIST] Instructions:')
    print('   * Click 'New repository secret'')
    print('   * Name: CROSS_REPO_TOKEN')
    print('   * Secret: Paste the token you copied')
    print('   * Click 'Add secret'')
    
    input('\n[U+23F8][EMOJI]  Press Enter after adding the secret...')
    
    test_sync()

def setup_vscode_integration():
    print('\n[EMOJI] VS Code Integration Setup:')
    print('=' * 40)
    
    print('1. [CHECKLIST] Open VS Code Command Palette:')
    print('   * Press Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac)')
    print('   * Type: 'GitHub: Create Token'')
    print('   * Or type: 'Git: Clone' and authenticate when prompted')
    
    print('\n2. [EMOJI] If prompted for GitHub authentication:')
    print('   * Choose 'Sign in with browser'')
    print('   * Grant necessary permissions')
    print('   * VS Code will handle token creation')
    
    print('\n3. [EMOJI][EMOJI] Manual token creation (if VS Code doesn't handle it):')
    print('   * Use Ctrl+Shift+P -> 'Simple Browser: Show'')
    print('   * Navigate to: https://github.com/settings/tokens/new')
    print('   * Create token with repo, workflow, packages permissions')
    
    print('\n4. [NOTE] Add to repository secrets:')
    print('   * In VS Code, use Ctrl+Shift+P -> 'Simple Browser: Show'')
    print('   * Navigate to: https://github.com/PipFoweraker/pdoom1/settings/secrets/actions')
    print('   * Add secret named: CROSS_REPO_TOKEN')
    
    if input('\n[EMOJI] Complete setup using VS Code? (y/n): ').lower() == 'y':
        test_sync()

def setup_manual_guide():
    print('\n[EMOJI] Manual Setup Guide:')
    print('=' * 30)
    
    print('[EMOJI] Token Requirements:')
    print('   [EMOJI] repo (Full control of repositories)')
    print('   [EMOJI] workflow (Update GitHub Action workflows)')
    print('   [EMOJI] write:packages (Upload packages)')
    print('   [EMOJI] read:packages (Download packages)')
    
    print('\n[EMOJI] URLs you'll need:')
    print('   * Token creation: https://github.com/settings/tokens/new')
    print('   * Repository secrets: https://github.com/PipFoweraker/pdoom1/settings/secrets/actions')
    
    print('\n[CHECKLIST] Checklist:')
    print('   [EMOJI] Create Personal Access Token with required scopes')
    print('   [EMOJI] Copy token (you won't see it again!)')
    print('   [EMOJI] Add as repository secret named 'CROSS_REPO_TOKEN'')
    print('   [EMOJI] Test the documentation sync')
    
    if input('\n[EMOJI] Ready to test sync? (y/n): ').lower() == 'y':
        test_sync()

def test_sync():
    print('\n[U+1F9EA] Testing Documentation Sync:')
    print('=' * 35)
    
    print('1. [EMOJI] Manual workflow trigger:')
    print('   * Go to: https://github.com/PipFoweraker/pdoom1/actions')
    print('   * Find 'Sync Documentation Across Repositories'')
    print('   * Click 'Run workflow' -> 'Run workflow'')
    
    print('\n2. [NOTE] Or make a test change:')
    print('   * Edit a file in docs/shared/')
    print('   * Commit and push changes')
    print('   * Workflow will trigger automatically')
    
    print('\n3. [EMOJI] Verify sync worked:')
    print('   * Check https://github.com/PipFoweraker/pdoom1-website/tree/main/docs')
    print('   * Check https://github.com/PipFoweraker/pdoom-data/tree/main/docs')
    print('   * Look for files with sync headers')
    
    actions_url = 'https://github.com/PipFoweraker/pdoom1/actions'
    print(f'\n[TARGET] Opening Actions page: {actions_url}')
    webbrowser.open(actions_url)
    
    print('\n[PARTY] Setup complete! Your documentation will now sync automatically.')

if __name__ == '__main__':
    main()
