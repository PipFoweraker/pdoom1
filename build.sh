#!/bin/bash
# P(Doom) PyInstaller Build Script for Unix/macOS
# Creates single-file executable for alpha/beta distribution

echo "================================================"
echo "P(Doom) PyInstaller Build Script"
echo "================================================"
echo

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found. Please run this script from the project root directory."
    exit 1
fi

if [ ! -f "pdoom.spec" ]; then
    echo "ERROR: pdoom.spec not found. Please ensure PyInstaller configuration exists."
    exit 1
fi

echo "Cleaning previous build artifacts..."
rm -rf build/ dist/

echo
echo "Building P(Doom) executable..."
echo "This may take 2-5 minutes depending on your system."
echo

# Run PyInstaller with our spec file
pyinstaller --clean pdoom.spec

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: PyInstaller build failed!"
    echo "Check the output above for specific error messages."
    exit 1
fi

echo
echo "================================================"
echo "Build completed successfully!"
echo "================================================"

# Check if the executable was created
if [ -f "dist/PDoom-v0.4.1-alpha" ]; then
    echo "Executable created: dist/PDoom-v0.4.1-alpha"
    
    # Get file size
    size=$(du -h "dist/PDoom-v0.4.1-alpha" | cut -f1)
    echo "File size: $size"
    
    echo
    echo "The executable is ready for distribution!"
    echo "Location: $(pwd)/dist/PDoom-v0.4.1-alpha"
    echo
    echo "You can now test the executable by running:"
    echo "  ./dist/PDoom-v0.4.1-alpha"
    echo
else
    echo "ERROR: Executable not found in expected location!"
    echo "Check the dist/ directory for output files."
    exit 1
fi

echo "Build log saved in build.log (if any errors occurred)"
echo
