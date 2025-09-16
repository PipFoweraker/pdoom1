# Setting Up Cross-Repository Token for Documentation Sync

## Overview
To enable automated documentation synchronization across your P(Doom) repositories, we need to create a Personal Access Token (PAT) and configure it as a repository secret.

## Step 1: Create Personal Access Token

### Via GitHub Web Interface:

1. **Navigate to GitHub Settings**:
   - Go to https://github.com/settings/tokens
   - Or: GitHub -> Profile -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)

2. **Generate New Token**:
   - Click "Generate new token" -> "Generate new token (classic)"
   - **Token name**: `P(Doom) Cross-Repository Documentation Sync`
   - **Expiration**: Choose appropriate duration (recommend 1 year)

3. **Select Required Scopes**:
   ```
   [EMOJI] repo (Full control of private repositories)
     [EMOJI] repo:status (Access commit status)
     [EMOJI] repo_deployment (Access deployment status)
     [EMOJI] public_repo (Access public repositories)
     [EMOJI] repo:invite (Access repository invitations)
     [EMOJI] security_events (Read and write security events)
   
   [EMOJI] workflow (Update GitHub Action workflows)
   
   [EMOJI] write:packages (Upload packages to GitHub Package Registry)
   [EMOJI] read:packages (Download packages from GitHub Package Registry)
   ```

4. **Generate Token**:
   - Click "Generate token"
   - **[WARNING][EMOJI] IMPORTANT**: Copy the token immediately - you won't see it again!

## Step 2: Add Token as Repository Secret

### Via GitHub Web Interface:

1. **Navigate to Repository Settings**:
   - Go to https://github.com/PipFoweraker/pdoom1/settings/secrets/actions
   - Or: pdoom1 repository -> Settings -> Secrets and variables -> Actions

2. **Create New Secret**:
   - Click "New repository secret"
   - **Name**: `CROSS_REPO_TOKEN`
   - **Secret**: Paste the token you copied in Step 1
   - Click "Add secret"

## Step 3: Verify Token Setup

### Test Token Permissions:
You can test the token using curl (replace `YOUR_TOKEN` with the actual token):

```bash
# Test repository access
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/PipFoweraker/pdoom1-website

# Test write permissions (this should return repository info)
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/PipFoweraker/pdoom-data
```

### Verify Secret in Repository:
1. Go to https://github.com/PipFoweraker/pdoom1/settings/secrets/actions
2. You should see `CROSS_REPO_TOKEN` listed
3. The secret value will be hidden (shows as `***`)

## Step 4: Test Documentation Sync

### Trigger the Workflow:

1. **Manual Trigger** (recommended for first test):
   - Go to https://github.com/PipFoweraker/pdoom1/actions
   - Find "Sync Documentation Across Repositories" workflow
   - Click "Run workflow" -> Select "main branch" -> "Run workflow"

2. **Automatic Trigger** (make a documentation change):
   ```bash
   # Make a small change to trigger sync
   echo "<!-- Test sync $(date) -->" >> docs/shared/ECOSYSTEM_OVERVIEW.md
   git add docs/shared/ECOSYSTEM_OVERVIEW.md
   git commit -m "docs: test cross-repository sync"
   git push
   ```

3. **Monitor Workflow Execution**:
   - Watch the workflow run at https://github.com/PipFoweraker/pdoom1/actions
   - Check for successful completion and any error messages

### Verify Sync Results:
After the workflow completes, check the target repositories:

1. **pdoom1-website**: https://github.com/PipFoweraker/pdoom1-website/tree/main/docs
2. **pdoom-data**: https://github.com/PipFoweraker/pdoom-data/tree/main/docs

You should see the documentation files with sync headers added.

## Alternative: GitHub CLI Method (if available)

If you prefer using GitHub CLI, you can set up the token programmatically:

```bash
# Install GitHub CLI (if not available)
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: See https://cli.github.com/manual/installation

# Authenticate with GitHub
gh auth login

# Create the repository secret
gh secret set CROSS_REPO_TOKEN --repo PipFoweraker/pdoom1 --body "your_token_here"

# Verify the secret was created
gh secret list --repo PipFoweraker/pdoom1
```

## Security Best Practices

### Token Security:
- **Never commit tokens to repositories**
- **Use repository secrets, not environment variables in code**
- **Set appropriate expiration dates**
- **Regularly rotate tokens**
- **Use minimal required permissions**

### Monitoring:
- **Monitor token usage** in GitHub Settings -> Personal access tokens
- **Set up notifications** for unusual repository activity
- **Regular security audits** of repository access

## Troubleshooting

### Common Issues:

1. **"Bad credentials" error**:
   - Token may be expired or incorrect
   - Verify token is copied correctly without extra spaces
   - Check token permissions include `repo` scope

2. **"Resource not accessible by integration" error**:
   - Token missing required permissions
   - Add `workflow` scope to token
   - Ensure token has access to target repositories

3. **Workflow doesn't trigger**:
   - Check file paths in workflow trigger conditions
   - Verify documentation files are in the correct paths
   - Check workflow syntax for errors

### Debug Commands:
```bash
# Check repository access with token
curl -H "Authorization: token YOUR_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/PipFoweraker/pdoom1-website

# Check repository permissions
curl -H "Authorization: token YOUR_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/PipFoweraker/pdoom-data/collaborators/PipFoweraker/permission
```

## Expected Results

After successful setup, you should see:

1. **Automated Sync**: Documentation changes in `pdoom1/docs/shared/` automatically appear in other repositories
2. **Sync Headers**: Files in target repositories include sync metadata headers
3. **Commit History**: Target repositories show commits from "Documentation Sync Bot"
4. **Workflow Success**: GitHub Actions show successful runs for documentation sync

## Next Steps

Once the token is configured:
1. **Test the sync** with a small documentation change
2. **Monitor workflow execution** for any issues
3. **Set up local multi-repository workspace** using the provided workspace file
4. **Begin documenting your integration architecture** knowing it will automatically sync

The cross-repository documentation system will then be fully operational! [ROCKET]
