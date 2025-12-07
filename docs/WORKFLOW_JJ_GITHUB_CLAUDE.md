# Workflow Guide: JJ + GitHub CLI + Claude Code

**Purpose**: Establish efficient patterns for issue-driven development with jj version control and GitHub integration.

---

## Daily Workflow

### Morning Routine
```bash
# 1. Check repository state
jj status                    # View working copy
jj log --limit 5             # Recent commits
jj git fetch                 # Get latest from origin

# 2. Review priorities
gh issue list --milestone "v1.0 Beta Ready" --state open
gh issue list --label player-blocking

# 3. Check what main branch is at
jj log -r main
```

### Starting Work on an Issue

```bash
# 1. Review the issue
gh issue view 390

# 2. Create a new working copy from main
jj new main

# 3. Describe your work
jj describe -m "fix: #390 employee red crosses not displaying

Working on UI rendering bug affecting employee status visualization.

Related to #390"

# 4. Create a feature bookmark (optional but recommended)
jj bookmark create fix-390

# 5. Start coding
cd pygame
# ... make changes ...
```

### During Development

```bash
# Check what you've changed
jj diff

# Check status frequently
jj status

# If you need to context-switch, jj auto-saves your work
jj new main          # Start new work
jj edit fix-390      # Return to previous work
```

### Committing and Pushing

```bash
# JJ automatically creates commits as you work
# If you want to explicitly commit with a message:
jj describe -m "fix: #390 fixed employee rendering

- Updated sprite positioning logic
- Fixed status change triggers
- Added tests for employee display

Fixes #390"

# Push your work
jj git push --bookmark fix-390

# Or push current commit
jj git push -c @
```

### Creating a Pull Request

```bash
# After pushing, create PR
gh pr create --fill --base main

# Or with specific details
gh pr create \
  --title "Fix: Employee red crosses not displaying (#390)" \
  --body "Fixes #390

## Changes
- Fixed sprite rendering logic
- Updated status triggers
- Added tests

## Testing
- Manual playtest verified
- All tests passing" \
  --base main
```

---

## Working with Multiple Developers

### Your Workflow
```bash
# Create your feature branch
jj bookmark create dev/pip/feature-name
jj new main -m "feat: implement feature"

# Regular commits as you work
jj describe -m "progress: feature mostly working"

# Push when ready for review
jj git push --bookmark dev/pip/feature-name
gh pr create --fill
```

### Friend's Workflow (on their machine)
```bash
# They create their feature branch
jj bookmark create dev/friend/feature-name
jj new main -m "feat: their feature"

# They push when ready
jj git push --bookmark dev/friend/feature-name
```

### Integration
```bash
# Fetch latest changes
jj git fetch

# See all branches
jj bookmark list

# Review what's coming
jj log -r 'remote_bookmarks()'

# Integrate friend's work
jj new main
jj rebase -d dev/friend/feature-name@origin  # Rebase onto their work
# ... test integration ...
jj bookmark move main --to @
jj git push -b main
```

---

## JJ Commands Cheat Sheet

### Basic Operations
```bash
jj status                    # Show working copy state
jj log                       # Show commit history
jj log --limit 5             # Recent 5 commits
jj diff                      # Show uncommitted changes
jj show                      # Show current commit details
```

### Creating Commits
```bash
jj new main                  # New commit based on main
jj new @-                    # New commit on parent
jj describe -m "message"     # Add/update commit message
jj commit                    # Explicitly create commit (usually auto)
```

### Bookmarks (Branches)
```bash
jj bookmark list             # List all bookmarks
jj bookmark create name      # Create bookmark at current commit
jj bookmark move name --to @ # Move bookmark to current commit
jj bookmark delete name      # Delete bookmark
```

### Navigation
```bash
jj edit <commit>             # Move to existing commit
jj new <commit>              # Create new commit based on commit
```

### Remote Operations
```bash
jj git fetch                 # Fetch from origin
jj git push -c @             # Push current commit
jj git push -b main          # Push main bookmark
jj git push --bookmark name  # Push specific bookmark
```

### Revsets (Queries)
```bash
jj log -r main               # Show main branch
jj log -r @                  # Show current commit
jj log -r @-                 # Show parent
jj log -r 'main..@'          # Commits from main to current
jj log -r 'remote_bookmarks()'  # All remote branches
```

---

## GitHub CLI Commands

### Issues
```bash
# List issues
gh issue list
gh issue list --label bug
gh issue list --milestone "v1.0"
gh issue list --assignee @me
gh issue list --state open --limit 20

# View issue
gh issue view 390
gh issue view 390 --web  # Open in browser

# Create issue
gh issue create --title "Bug: ..." --body "Description"

# Update issue
gh issue edit 390 --add-label "priority-high"
gh issue close 390
```

### Pull Requests
```bash
# List PRs
gh pr list
gh pr list --state open

# View PR
gh pr view 123
gh pr view 123 --web

# Create PR
gh pr create --fill                    # Interactive
gh pr create --title "..." --body "..."  # Non-interactive

# Review PR
gh pr checkout 123                     # Check out PR locally
gh pr review 123 --approve
gh pr merge 123
```

### Repositories
```bash
gh repo view                           # View current repo
gh repo view --web                     # Open in browser
```

---

## Claude Code Session Patterns

### Starting a Session
1. **Review handoff doc**: Read previous session's handoff
2. **Check jj status**: Understand current state
3. **Review issues**: Pick work from GitHub issues
4. **Set session goal**: Clear, focused objective

### During Session
1. **Use Grep/Glob first**: Search before reading large files
2. **Read with line ranges**: For files > 100 lines
3. **Parallel operations**: Multiple tool calls when possible
4. **Commit early, commit often**: Push work incrementally

### Ending Session
1. **Commit all work**: Ensure everything is saved
2. **Push to remote**: Make work available to others
3. **Create handoff doc**: Document what's done and what's next
4. **Update issues**: Comment on progress, close if fixed

---

## Issue-Driven Development

### Labels for Prioritization
```bash
# Suggested label scheme
player-blocking     # Must fix before release
critical            # High impact bugs
nice-to-have        # Quality of life improvements
wontfix            # Closed, not addressing
good-first-issue   # For new contributors
```

### Using Issues for Planning
```bash
# Morning: Review what to work on
gh issue list --label player-blocking --state open

# Pick an issue
gh issue view 390

# Start work (link to issue in commit)
jj new main
jj describe -m "fix: #390 description

Fixes #390"

# Update issue as you go
gh issue comment 390 --body "Working on fix, testing sprite rendering"

# Close issue when done (commit message with "Fixes #390" closes automatically)
```

---

## Common Scenarios

### Scenario: Fix a Bug
```bash
gh issue view 390                      # Review bug
jj new main                            # Start from main
jj describe -m "fix: #390 employee red crosses"
jj bookmark create fix-390
cd pygame
# ... make changes ...
python -m pytest tests/test_ui.py      # Test
jj diff                                # Review changes
jj git push --bookmark fix-390
gh pr create --fill
```

### Scenario: Start a Feature
```bash
gh issue create --title "Feature: Add sound settings"  # Create issue
jj new main
jj describe -m "feat: #425 sound settings menu"
jj bookmark create feature-sound-settings
# ... implement ...
```

### Scenario: Context Switch
```bash
# Currently working on fix-390
jj status                              # Save current state

# Urgent bug comes in
jj new main                            # Start new work
jj describe -m "fix: urgent crash on startup"
# ... fix urgent bug ...
jj git push -c @

# Return to previous work
jj edit fix-390                        # Resume where you left off
```

### Scenario: Review Friend's PR
```bash
gh pr list                             # See open PRs
gh pr view 45                          # Review details
gh pr checkout 45                      # Test locally
cd pygame
python -m pytest tests/                # Run tests
gh pr review 45 --approve              # Approve
gh pr merge 45                         # Merge
```

---

## Best Practices

### Commit Messages
```bash
# Good format:
<type>: <short summary> (#issue)

<detailed description>

Fixes #123

# Types: feat, fix, docs, test, refactor, chore
```

**Examples:**
```bash
fix: #390 employee red crosses not displaying

Updated sprite rendering logic to properly show employee status indicators.

Fixes #390

---

feat: #425 add sound settings menu

Implemented configurable sound settings with:
- Master volume control
- Individual sound toggles
- Save/load preferences

Related to #425
```

### Bookmarks (Branch Names)
```bash
# Good names:
fix-390                    # Issue-specific
feature-sound-settings     # Feature-specific
dev/pip/experimental       # Personal experimental work
hotfix-crash-on-startup    # Urgent fixes

# Avoid:
test                       # Too generic
fix                        # Not descriptive
my-branch                  # Not informative
```

### When to Push
- SUCCESS **Push early, push often** - Share work with team
- SUCCESS **Before context switch** - Ensure work is backed up
- SUCCESS **After significant progress** - Natural breakpoints
- SUCCESS **End of session** - Always push before stopping
- ERROR **Don't wait for perfection** - Iterate with team

### When to Create PR
- SUCCESS **Feature complete** - Ready for review
- SUCCESS **Tests passing** - Verified locally
- SUCCESS **Self-review done** - Check your own diff
- SUCCESS **Draft PR** - For early feedback (use `--draft` flag)

---

## Troubleshooting

### JJ Issues

**Problem**: "Working copy has uncommitted changes"
```bash
jj status                              # See what changed
jj diff                                # Review changes
jj describe -m "work in progress"      # Describe and commit
```

**Problem**: "Bookmark not found"
```bash
jj bookmark list                       # See all bookmarks
jj bookmark create name                # Create if missing
```

**Problem**: "Conflicts after rebase"
```bash
jj status                              # See conflicted files
# Edit files to resolve conflicts
jj resolve                             # Mark as resolved
```

### GitHub CLI Issues

**Problem**: "Not authenticated"
```bash
gh auth status                         # Check status
gh auth login                          # Re-authenticate
```

**Problem**: "Rate limit exceeded"
```bash
# Wait or use authentication (authenticated = higher limit)
gh auth login
```

---

## Quick Reference Card

```bash
# Daily Start
jj status && gh issue list --label player-blocking

# Start Work
jj new main && jj describe -m "fix: #NUM description"

# Review Changes
jj diff

# Push Work
jj git push -c @

# Create PR
gh pr create --fill

# Daily End
jj git push -c @ && gh issue list --assignee @me --state open
```

---

**Pro Tip**: Create shell aliases for common commands:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias jst='jj status'
alias jl='jj log --limit 10'
alias jn='jj new main'
alias jp='jj git push -c @'
alias gil='gh issue list'
alias giv='gh issue view'
```

---

*Last Updated: 2025-10-16*
*For P(Doom) Development Team*
