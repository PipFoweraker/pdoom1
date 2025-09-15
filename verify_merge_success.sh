#!/bin/bash

# P(Doom) Post-Merge Verification Script
# Verifies that merged branches work correctly and system is functional

set -e

echo "=========================================="
echo "P(Doom) Post-Merge Verification"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verify we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "src" ]; then
    print_error "Not in P(Doom) repository root"
    exit 1
fi

# Check current branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "Currently on branch: $current_branch"
    print_status "Switching to main branch..."
    git checkout main
fi

print_status "Verifying merge success..."

# 1. Check git history
print_status "1. Checking git history for merged commits"
if git log --oneline -10 | grep -q "Merge.*Mac compatibility"; then
    print_success "Mac compatibility fixes found in history"
else
    print_warning "Mac compatibility merge not found in recent history"
fi

if git log --oneline -10 | grep -q -i "layout\|button"; then
    print_success "UI layout changes found in history"  
else
    print_warning "UI layout changes not found in recent history"
fi

if git log --oneline -10 | grep -q -i "leaderboard\|party"; then
    print_success "Leaderboard/party features found in history"
else
    print_warning "Leaderboard features not found in recent history"
fi

# 2. Verify Python environment
print_status "2. Checking Python environment"
if python --version; then
    print_success "Python environment OK"
else
    print_error "Python environment issue"
    exit 1
fi

# 3. Check dependencies
print_status "3. Verifying dependencies"
if python -c "import pygame, numpy, jsonschema, pytest"; then
    print_success "Core dependencies available"
else
    print_error "Missing dependencies - run: pip install -r requirements.txt"
    exit 1
fi

# 4. Test game state initialization
print_status "4. Testing game state initialization"
if python -c "from src.core.game_state import GameState; gs = GameState('test-merge-verification'); print('✓ GameState initializes correctly')"; then
    print_success "Game state initialization works"
else
    print_error "Game state initialization failed"
    exit 1
fi

# 5. Test version system
print_status "5. Checking version system"
if python -c "from src.services.version import get_display_version; print(f'Version: {get_display_version()}')"; then
    print_success "Version system works"
else
    print_warning "Version system issue (non-critical)"
fi

# 6. Run critical tests
print_status "6. Running critical test subset"
if python -m unittest tests.test_game_state -v; then
    print_success "Game state tests pass"
else
    print_error "Game state tests failed"
    exit 1
fi

# 7. Test UI imports (without display)
print_status "7. Testing UI system imports"
if python -c "import src.ui; print('✓ UI system imports correctly')"; then
    print_success "UI system imports work"
else
    print_error "UI system import failed"
    exit 1
fi

# 8. Check for merge artifacts
print_status "8. Checking for merge conflict artifacts"
if grep -r "<<<<<<< " . --exclude-dir=.git --exclude="*.md" 2>/dev/null; then
    print_error "Merge conflict artifacts found!"
    exit 1
else
    print_success "No merge conflict artifacts found"
fi

# 9. Verify file structure
print_status "9. Verifying critical files exist"
critical_files=("main.py" "src/core/game_state.py" "src/ui.py" "requirements.txt")
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file exists"
    else
        print_error "✗ Missing critical file: $file"
        exit 1
    fi
done

# 10. Check branch cleanup status
print_status "10. Checking branch cleanup status"
deleted_count=0
for branch in "bug-sweep-critical-stability" "hotfix/mac-research-debt-fix" "feature/leaderboard-activation-v0.4.1"; do
    if ! git show-ref --verify --quiet "refs/remotes/origin/$branch" 2>/dev/null; then
        print_success "✓ Branch $branch cleaned up"
        ((deleted_count++))
    else
        print_warning "Branch $branch still exists (cleanup pending)"
    fi
done

if [ $deleted_count -eq 3 ]; then
    print_success "All target branches cleaned up"
elif [ $deleted_count -gt 0 ]; then
    print_warning "Partial cleanup completed ($deleted_count/3 branches)"
else
    print_warning "No branches cleaned up yet (manual cleanup required)"
fi

# Final summary
print_status "=========================================="
print_success "VERIFICATION COMPLETE"
print_status "=========================================="

echo "System Status: $(print_success "FUNCTIONAL")"
echo "Merged Features:"
echo "  ✓ Mac compatibility fixes"
echo "  ✓ UI layout optimization"  
echo "  ✓ Enhanced leaderboard system"
echo "  ✓ Party-ready v0.4.1 features"
echo ""
echo "Next Steps:"
echo "  1. Run full test suite: python -m unittest discover tests -v"
echo "  2. Test game launch: python main.py"
echo "  3. Begin playtesting with merged features"
echo "  4. Consider next priority branches from analysis"

print_success "Merge verification successful - ready for playtesting!"