# Dev Blog to Website Pipeline - Implementation Guide

## Quick Setup (5 minutes)

This guide will get the automated dev blog sync pipeline operational.

### Step 1: GitHub Repository Setup

1. **Create Personal Access Token** (if not exists):
   - Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Click 'Generate new token (classic)'
   - Select scopes: `repo` (full repository access)
   - Copy the token (you won't see it again)

2. **Add Secret to pdoom1 Repository**:
   - Go to pdoom1 repository Settings > Secrets and variables > Actions
   - Click 'New repository secret'
   - Name: `WEBSITE_SYNC_TOKEN`
   - Value: [paste your token]

### Step 2: Test the Pipeline

The workflow is already created at `.github/workflows/sync-dev-blog.yml`. To test:

1. **Manual Trigger** (recommended first test):
   - Go to Actions tab in pdoom1 repository
   - Select 'Sync Dev Blog to Website' workflow
   - Click 'Run workflow'
   - Select 'Force sync all entries' checkbox
   - Click 'Run workflow'

2. **Automatic Trigger Test**:
   - Create or edit any file in `dev-blog/entries/`
   - Commit and push to main branch
   - Workflow will automatically trigger

### Step 3: Verify Results

After the workflow runs:

1. **Check GitHub Actions**:
   - Ensure the workflow completed successfully (green checkmark)
   - Review logs for any errors

2. **Check Website Repository**:
   - Visit pdoom1-website repository
   - Verify `public/blog/` directory contains your entries
   - Check commit history for sync bot commits

3. **Check Live Website** (if deployed):
   - Visit the live website
   - Navigate to blog section
   - Verify new content appears

## Current Status

### [EMOJI] Ready Components
- **Dev Blog System**: 16 entries validated and ready
- **Website Structure**: Empty `public/blog/` directory ready for content
- **GitHub Workflow**: Complete sync pipeline created
- **Content Validation**: ASCII compliance and title length checks

### [EMOJI] Setup Required
- **GitHub Token**: Personal access token with repo access
- **Repository Secret**: WEBSITE_SYNC_TOKEN configuration
- **Initial Test**: Manual workflow trigger to verify setup

### [CHECKLIST] Next Steps
1. Configure WEBSITE_SYNC_TOKEN secret
2. Run manual workflow test
3. Create new dev blog entry to test automatic sync
4. Enhance website to display blog content (HTML templates)
5. Add RSS feed generation
6. Implement comment system integration

## Workflow Features

### [EMOJI] Smart Sync
- **Incremental**: Only syncs changed entries (detects git diff)
- **Force Sync**: Manual option to sync all entries
- **Validation**: Runs blog validation before sync (prevents broken content)

### [EMOJI][EMOJI] Safety Features
- **Repository Check**: Only runs on official pdoom1 repository
- **Validation**: Prevents sync of invalid blog entries
- **Meaningful Commits**: Clear commit messages with context
- **No-op Detection**: Skips commit if no actual changes

### [CHART] Monitoring
- **Detailed Logs**: Step-by-step progress reporting
- **Change Detection**: Shows exactly which entries were synced
- **Success Notifications**: Clear success/failure indicators

## Troubleshooting

### Common Issues

1. **Token Permissions Error**:
   - Ensure token has `repo` scope
   - Verify token isn't expired
   - Check secret name is exactly `WEBSITE_SYNC_TOKEN`

2. **Validation Failures**:
   - Run `python dev-blog/generate_index.py` locally
   - Fix any title length or ASCII character issues
   - Re-run workflow after fixes

3. **No Changes Detected**:
   - Workflow only syncs changed entries
   - Use 'Force sync' option for full sync
   - Check that changes are in `dev-blog/entries/` directory

### Debug Commands

```bash
# Test blog validation locally
cd pdoom1
python dev-blog/generate_index.py

# Check what files would be synced
git diff --name-only HEAD~1 HEAD | grep '^dev-blog/entries/.*\.md$'

# Verify blog entry format
cat dev-blog/entries/your-entry.md
```

## Success Criteria

After successful setup, you should see:

1. [EMOJI] GitHub Actions workflow runs without errors
2. [EMOJI] Blog entries appear in website repository
3. [EMOJI] Automatic sync triggers on new blog entries
4. [EMOJI] Manual force sync works for bulk updates
5. [EMOJI] Clear logs showing sync progress and results

## What's Next?

This pipeline creates the foundation for automated development-to-community content flow. Future enhancements:

- **Website Templates**: HTML rendering of blog entries
- **RSS Feeds**: Automatic feed generation for subscribers
- **Social Integration**: Auto-post to Discord/Twitter
- **Release Notes**: Automatic version release documentation
- **Community Challenges**: Weekly seed challenge posting

The infrastructure is now ready - time to start building the community bridge! [ROCKET]
