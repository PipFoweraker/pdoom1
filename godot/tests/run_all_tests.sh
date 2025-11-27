# !/bin/bash
# Run all Godot unit and integration tests via GUT
# Usage: ./run_all_tests.sh

GODOT_BIN="${GODOT_BIN:-godot}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running Godot Unit Tests with GUT..."
echo "Project: $PROJECT_DIR"
echo "Godot binary: $GODOT_BIN"
echo ""

# Run GUT tests in headless mode
$GODOT_BIN --headless --path "$PROJECT_DIR" --script "res://addons/gut/gut_cmdln.gd" \
  -gdir=res://tests/unit/ \
  -gdir=res://tests/integration/ \
  -gexit

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo ""
  echo "SUCCESS All tests passed!"
else
  echo ""
  echo "ERROR Tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE
