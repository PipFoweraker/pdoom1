@echo off
REM P(Doom) PyInstaller Build Script for Windows
REM Creates single-file executable for alpha/beta distribution

echo ================================================
echo P(Doom) PyInstaller Build Script
echo ================================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

if not exist "pdoom.spec" (
    echo ERROR: pdoom.spec not found. Please ensure PyInstaller configuration exists.
    pause
    exit /b 1
)

echo Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Building P(Doom) executable...
echo This may take 2-5 minutes depending on your system.
echo.

REM Run PyInstaller with our spec file
pyinstaller --clean pdoom.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check the output above for specific error messages.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build completed successfully!
echo ================================================

REM Check if the executable was created
if exist "dist\PDoom-v0.4.1-alpha.exe" (
    echo Executable created: dist\PDoom-v0.4.1-alpha.exe
    
    REM Get file size
    for %%I in ("dist\PDoom-v0.4.1-alpha.exe") do (
        echo File size: %%~zI bytes (approximately %%~zI:~0,-6% MB)
    )
    
    echo.
    echo The executable is ready for distribution!
    echo Location: %CD%\dist\PDoom-v0.4.1-alpha.exe
    echo.
    echo You can now test the executable by running:
    echo   dist\PDoom-v0.4.1-alpha.exe
    echo.
) else (
    echo ERROR: Executable not found in expected location!
    echo Check the dist\ directory for output files.
)

echo Build log saved in build.log (if any errors occurred)
echo.
pause
