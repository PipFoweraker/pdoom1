@echo off
REM Run GUT tests for Godot P(Doom) project
REM Usage: run_tests.bat

echo ========================================
echo Running Godot Unit Tests (GUT)
echo ========================================
echo.

REM Check if godot is in PATH
where godot >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Godot not found in PATH
    echo Please add Godot to your PATH or run from Godot editor
    echo.
    echo Alternative: Run from Godot editor:
    echo   1. Open Godot Editor
    echo   2. Go to Project -^> Tools -^> Run GUT
    echo   3. Or use bottom panel GUT tab
    exit /b 1
)

REM Run tests headless
godot --headless --script addons/gut/gut_cmdln.gd -gdir=res://tests/unit -gexit

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ALL TESTS PASSED
    echo ========================================
) else (
    echo.
    echo ========================================
    echo TESTS FAILED - Fix errors before pushing
    echo ========================================
    exit /b 1
)
