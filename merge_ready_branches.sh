#!/bin/bash

# P(Doom) Branch Merge Script
# Merges the 3 production-ready branches identified in repository analysis
# REQUIRES: Admin access and git push permissions to main branch

set -e  # Exit on any error

echo "=========================================="
echo "P(Doom) Branch Merge Execution Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verify we're in the right repository
if [ ! -f "main.py" ] || [ ! -d "src" ]; then
    print_error "Not in P(Doom) repository root directory"
    exit 1
fi

print_status "Starting branch merge process..."

# Phase 1: Pre-merge validation
print_status "Phase 1: Pre-merge validation"

# Ensure we're on main and up to date
git checkout main
git pull origin main

print_status "Current main branch state:"
git log --oneline -3

# Verify target branches exist
BRANCHES=("hotfix/mac-research-debt-fix" "bug-sweep-critical-stability" "feature/leaderboard-activation-v0.4.1")

for branch in "${BRANCHES[@]}"; do
    if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        print_success "Branch $branch exists"
    else
        print_error "Branch $branch not found"
        exit 1
    fi
done

# Phase 2: Run tests on current main
print_status "Phase 2: Running tests on current main branch"
if python -m unittest discover tests -v; then
    print_success "Main branch tests pass"
else
    print_error "Tests fail on main branch - aborting merge"
    exit 1
fi

# Phase 3: Merge branches in priority order
print_status "Phase 3: Merging production-ready branches"

# Merge 1: Critical Mac fixes (highest priority)
print_status "Merging hotfix/mac-research-debt-fix (CRITICAL)"
git merge --no-ff origin/hotfix/mac-research-debt-fix -m "Merge critical Mac compatibility fixes

- Fix Mac TypeError with verbose naming pattern
- Add GameClock array bounds protection  
- Verify hiring dialog ESC functionality
- 24 new test scenarios (15 type safety + 9 integration)
- Resolves blocking issues for Mac users"

print_success "Mac compatibility fixes merged"

# Merge 2: UI layout optimization  
print_status "Merging bug-sweep-critical-stability (UI improvements)"
git merge --no-ff origin/bug-sweep-critical-stability -m "Merge UI layout optimization hotfix

- Reduce button width from 30% to 25% (17% smaller)
- Reduce button height from 5.5% to 4.5% (18% smaller)
- Reduce button spacing from 1.5% to 0.8% (47% smaller)
- Better space utilization and professional layout
- No logic changes, UI improvements only"

print_success "UI layout optimization merged"

# Merge 3: Complete v0.4.1 release
print_status "Merging feature/leaderboard-activation-v0.4.1 (Party release)"
git merge --no-ff origin/feature/leaderboard-activation-v0.4.1 -m "Merge complete v0.4.1 party-ready release

- Enhanced leaderboard system with seed-specific competition
- Spectacular game over screen with celebration effects
- Mini leaderboard preview with rank highlighting  
- Context-aware button text and natural flow progression
- Complete party demo functionality"

print_success "Party-ready v0.4.1 release merged"

# Phase 4: Post-merge validation
print_status "Phase 4: Post-merge validation"

print_status "Running full test suite on merged code..."
if python -m unittest discover tests -v; then
    print_success "All tests pass after merge"
else
    print_error "Tests fail after merge - manual review required"
    print_warning "Main branch has been modified but not pushed"
    exit 1
fi

# Verify game initialization
print_status "Verifying game initialization..."
if python -c "from src.core.game_state import GameState; gs = GameState('test'); print('Game initializes correctly')"; then
    print_success "Game initialization successful"
else
    print_error "Game initialization failed - manual review required"
    exit 1
fi

# Phase 5: Push to remote (ADMIN OPERATION)
print_status "Phase 5: Pushing merged main to remote"
print_warning "About to push merged changes to origin/main"
read -p "Continue with push? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    print_success "Merged changes pushed to main"
else
    print_warning "Push cancelled - merged changes remain local only"
    print_status "To push later: git push origin main"
    exit 0
fi

# Phase 6: Branch cleanup
print_status "Phase 6: Branch cleanup"

print_warning "About to delete remote branches (IRREVERSIBLE)"
read -p "Delete remote branches? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for branch in "${BRANCHES[@]}"; do
        print_status "Deleting remote branch: $branch"
        git push origin --delete "$branch"
        print_success "Deleted remote branch: $branch"
    done
else
    print_warning "Remote branch cleanup skipped"
    print_status "To delete later: git push origin --delete <branch_name>"
fi

# Final status report
print_status "=========================================="
print_success "MERGE PROCESS COMPLETE"
print_status "=========================================="

echo "Summary of changes:"
git log --oneline -10

print_success "All 3 production-ready branches successfully merged"
print_success "Tests passing, game functional"
print_success "Repository environment cleaned up"

print_status "Next recommended actions:"
echo "1. Close PR #300 (should close automatically)"
echo "2. Close analysis PR #304"
echo "3. Consider next priority branches from analysis"
echo "4. Update CHANGELOG.md with new features"

print_success "Development environment is now clean and ready for playtesting!"