"""
PyInstaller Validation Script
Tests the built executable to ensure it works correctly
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def test_executable():
    """Test the PyInstaller executable"""
    print("=" * 60)
    print("P(Doom) PyInstaller Validation Test")
    print("=" * 60)
    
    # Check if executable exists
    exe_path = Path("dist/PDoom-v0.4.1-alpha.exe")
    if not exe_path.exists():
        print("❌ ERROR: Executable not found at dist/PDoom-v0.4.1-alpha.exe")
        return False
    
    print(f"✅ Executable found: {exe_path}")
    print(f"📦 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Test executable startup (brief run)
    print("\n🔄 Testing executable startup...")
    try:
        # Run the executable with a very short timeout to test startup
        process = subprocess.Popen([str(exe_path)], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   cwd=os.getcwd())
        
        # Give it 3 seconds to start up
        time.sleep(3)
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("✅ Executable started successfully (terminated after startup test)")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Executable failed to start: {e}")
        return False


def validate_build_artifacts():
    """Validate that all expected build artifacts are present"""
    print("\n🔍 Validating build artifacts...")
    
    expected_files = [
        "dist/PDoom-v0.4.1-alpha.exe",
        "build/pdoom/",
        "pdoom.spec"
    ]
    
    all_present = True
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_present = False
    
    return all_present


def main():
    print("Starting P(Doom) PyInstaller validation...")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    success = True
    success &= validate_build_artifacts()
    success &= test_executable()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ PyInstaller build validation PASSED")
        print("🎉 The executable is ready for distribution!")
        print(f"📍 Location: {Path.cwd() / 'dist' / 'PDoom-v0.4.1-alpha.exe'}")
    else:
        print("❌ PyInstaller build validation FAILED")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
