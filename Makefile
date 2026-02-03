# P(Doom) Development Makefile
# Run 'make help' for available targets

GODOT := godot
PYTHON := python

.PHONY: help run test lint validate clean

help: ## Show this help message
	@echo "P(Doom) Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Prerequisites: Godot 4.5.1, Python 3.9+"

run: ## Run the game
	$(GODOT) --path godot

test: ## Run GUT unit tests
	$(PYTHON) scripts/run_godot_tests.py --quick

test-ci: ## Run tests in CI mode (exits with status)
	$(PYTHON) scripts/run_godot_tests.py --quick --ci-mode

lint: ## Check GDScript syntax
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
