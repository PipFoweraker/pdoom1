# !/bin/bash
# P(Doom) Branch Cleanup Script
# This script helps identify and clean up old branches safely

echo "=== P(Doom) Branch Cleanup Tool ==="
echo ""

# Function to check if branch exists
branch_exists() {
    git branch -r | grep -q "origin/$1"
}

# Function to check if branch is merged
is_merged() {
    git branch -r --merged main | grep -q "origin/$1"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "Analyzing repository branches..."
echo ""

# Count branches
TOTAL_BRANCHES=$(git branch -r | grep -v "HEAD" | wc -l)
MERGED_BRANCHES=$(git branch -r --merged main | grep -v "HEAD" | wc -l)
UNMERGED_BRANCHES=$((TOTAL_BRANCHES - MERGED_BRANCHES))

echo -e "${BLUE}METRICS Branch Statistics:${NC}"
echo "  Total remote branches: $TOTAL_BRANCHES"
echo "  Merged into main: $MERGED_BRANCHES"
echo "  Unmerged: $UNMERGED_BRANCHES"
echo ""

# Analyze merged branches that can be safely deleted
echo -e "${GREEN}SUCCESS SAFE TO DELETE (Already merged into main):${NC}"
echo ""

echo "Copilot fix branches:"
git branch -r --merged main | grep "origin/copilot/fix-" | head -10 | while read branch; do
    branch_name=${branch#origin/}
    echo "  - $branch_name"
done
COPILOT_COUNT=$(git branch -r --merged main | grep "origin/copilot/fix-" | wc -l)
echo "  ... and $((COPILOT_COUNT - 10)) more copilot fix branches"
echo ""

echo "Feature branches:"
git branch -r --merged main | grep "origin/feature/" | while read branch; do
    branch_name=${branch#origin/}
    echo "  - $branch_name"
done
echo ""

echo "Issue branches:"
git branch -r --merged main | grep -E "origin/[0-9]+-" | while read branch; do
    branch_name=${branch#origin/}
    echo "  - $branch_name"
done
echo ""

# Analyze unmerged branches that need review
echo -e "${YELLOW}SEARCH NEEDS REVIEW (Contains unmerged work):${NC}"
echo ""

git branch -r --no-merged main | grep -v "HEAD" | while read branch; do
    branch_name=${branch#origin/}
    commit_count=$(git rev-list --count main..$branch 2>/dev/null || echo "0")
    last_commit=$(git log -1 --format="%cr" $branch 2>/dev/null || echo "unknown")
    echo "  - $branch_name ($commit_count commits ahead, last: $last_commit)"
done
echo ""

# New strategy branches
echo -e "${BLUE}HOME NEW STRATEGY BRANCHES (Keep these):${NC}"
for branch in "develop" "release/staging" "experimental/playground" "hotfix/ui-button-shrink"; do
    if branch_exists "$branch"; then
        echo "  CHECKED $branch"
    else
        echo "  FAILED $branch (missing)"
    fi
done
echo ""

# Generate cleanup commands
echo -e "${RED}TRASH  CLEANUP COMMANDS:${NC}"
echo ""
echo "# Delete merged copilot fix branches (run these one by one to be safe):"
git branch -r --merged main | grep "origin/copilot/fix-" | head -5 | while read branch; do
    branch_name=${branch#origin/}
    echo "git push origin --delete $branch_name"
done
echo "# ... continue with remaining copilot branches"
echo ""

echo "# Delete merged feature branches:"
git branch -r --merged main | grep "origin/feature/" | while read branch; do
    branch_name=${branch#origin/}
    echo "git push origin --delete $branch_name"
done
echo ""

echo "# Delete merged issue branches:"
git branch -r --merged main | grep -E "origin/[0-9]+-" | while read branch; do
    branch_name=${branch#origin/}
    echo "git push origin --delete $branch_name"
done
echo ""

echo -e "${YELLOW}WARNING  MANUAL REVIEW REQUIRED:${NC}"
echo "Before deleting any branches, review unmerged content:"
git branch -r --no-merged main | grep -v "HEAD" | while read branch; do
    branch_name=${branch#origin/}
    echo "git log --oneline main..$branch  # Review $branch_name"
done
echo ""

echo -e "${GREEN}SPARKLES RECOMMENDATIONS:${NC}"
echo "1. Review unmerged branches for valuable content"
echo "2. Merge useful fixes to 'develop' branch"
echo "3. Move experimental features to 'experimental/playground'"
echo "4. Delete merged branches in small batches"
echo "5. Set up branch protection rules in GitHub"
echo ""

echo "Run this script periodically to maintain a clean repository!"
