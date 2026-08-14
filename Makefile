# P(Doom) Development Makefile
# Run 'make help' for available targets

GODOT := godot
PYTHON := python

.PHONY: help run test lint validate clean commit class-cache

help: ## Show this help message
	@echo "P(Doom) Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Prerequisites: Godot 4.5.1, Python 3.9+"

# Pre-flight for anything that LAUNCHES the game (2026-08-13, cost a playtest).
# godot/.godot/global_script_class_cache.cfg is GENERATED, GITIGNORED and PER-CHECKOUT, so a
# long-lived working copy can hold a cache that predates a pulled `class_name`. The game then
# starts, draws, and does nothing -- no crash, no dialog, just a screen that looks like it is
# still loading. CI cannot catch this (it always clones fresh). ~30ms when clean; only pays
# for a Godot --import when it is actually stale. See tools/check_class_cache.py.
class-cache: ## Verify + repair the Godot class cache (stale cache = silently broken game)
	$(PYTHON) tools/check_class_cache.py --repair

run: class-cache ## Run the game
	$(GODOT) --path godot

test: ## Run GUT unit tests
	$(PYTHON) scripts/run_godot_tests.py --quick

test-ci: ## Run tests in CI mode (exits with status)
	$(PYTHON) scripts/run_godot_tests.py --quick --ci-mode

# `--quit` alone is NOT a syntax check on a stale cache: measured 2026-08-13, it emitted 30
# `Identifier "Capacity" not declared` parse errors plus 17 depended-script compile failures
# and still EXITED 0. The class-cache prerequisite is what makes this target honest.
lint: class-cache ## Check GDScript syntax
	$(GODOT) --headless --path godot --quit

validate: ## Validate historical data files
	$(PYTHON) scripts/validate_historical_data.py

health: ## Run project health check
	$(PYTHON) scripts/project_health.py

clean: ## Clean Python cache files and Godot temp files
	$(PYTHON) scripts/cleanup_project.py --clean-pyc --clean-cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

install: ## Install Python dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

commit: ## Hook-safe commit: make commit m="msg" f="path1 path2" (or f="-u" for all tracked). See tools/README_commit.md
	@if [ -z "$(m)" ] || [ -z "$(f)" ]; then \
		echo 'usage: make commit m="commit message" f="path1 path2"   (or f="-u" for all tracked changes)'; \
		exit 1; \
	fi
	$(PYTHON) tools/commit.py -m "$(m)" $(f)
