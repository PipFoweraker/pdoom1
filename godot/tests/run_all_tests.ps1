# Run all Godot unit and integration tests via GUT
# Usage: .\run_all_tests.ps1

$GODOT_BIN = if ($env:GODOT_BIN) { $env:GODOT_BIN } else { "C:\Program Files\Godot\Godot_v4.5.1-stable_win64.exe" }
$PROJECT_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "Running Godot Unit Tests with GUT..." -ForegroundColor Cyan
Write-Host "Project: $PROJECT_DIR"
Write-Host "Godot binary: $GODOT_BIN"
Write-Host ""

# Run GUT tests in headless mode
& $GODOT_BIN --headless --path "$PROJECT_DIR\godot" --script "res://addons/gut/gut_cmdln.gd" `
  -gdir=res://tests/unit/ `
  -gdir=res://tests/integration/ `
  -gexit

$EXIT_CODE = $LASTEXITCODE

if ($EXIT_CODE -eq 0) {
  Write-Host ""
  Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
  Write-Host ""
  Write-Host "❌ Tests failed with exit code: $EXIT_CODE" -ForegroundColor Red
}

exit $EXIT_CODE
