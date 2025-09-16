# P(Doom) Distribution Guide

## PyInstaller Windows Executable Distribution

This guide covers building and distributing P(Doom) as a single-file Windows executable for alpha/beta testing.

### Overview

- **Target Audience**: 90% low-skill Windows users requiring download-and-run experience
- **File Size**: ~19MB single executable file
- **Requirements**: Windows 10/11 (no Python installation required)
- **Security**: Users may need to bypass Windows Defender warnings (documented below)

### Build Process

#### Prerequisites

1. **Development Environment**: Python 3.9+ with dependencies installed
2. **PyInstaller**: Included in `requirements-dev.txt`
3. **Project Structure**: Complete P(Doom) source code with all assets

#### Quick Build Commands

**Windows (Recommended)**:
```batch
# Using build script
build.bat

# Or manual command
pyinstaller --clean pdoom.spec
```

**Unix/macOS**:
```bash
# Using build script
./build.sh

# Or manual command
pyinstaller --clean pdoom.spec
```

#### Build Configuration

The build is configured via `pdoom.spec` with the following key settings:

- **Single-file executable**: All dependencies bundled into one `.exe`
- **Windowed mode**: No console window (GUI-only)
- **Asset bundling**: Complete `assets/` directory included
- **Module inclusion**: Both root-level `ui.py` and `src/` structure
- **Compression**: UPX compression enabled for smaller file size

### Distribution

#### File Output

- **Location**: `dist/PDoom-v0.4.1-alpha.exe`
- **Size**: Approximately 19MB
- **Dependencies**: None (fully self-contained)

#### User Instructions

1. **Download**: Provide the single `.exe` file to users
2. **Run**: Double-click to start (no installation required)
3. **Save Data**: Automatically stored in user's AppData directory
4. **Updates**: Replace `.exe` file with newer version

### Windows Defender Handling

#### Expected Behavior

Windows Defender will likely flag the executable as potentially unwanted software because:
- It's an unsigned executable
- PyInstaller executables often trigger false positives
- The file is relatively large and self-extracting

#### User Workaround Instructions

**For Windows Defender SmartScreen**:
1. When Windows shows "Windows protected your PC", click "More info"
2. Click "Run anyway" at the bottom
3. The game will start normally

**For Windows Defender Antivirus**:
1. If the file is quarantined, open Windows Security
2. Go to "Virus & threat protection" > "Protection history"
3. Find the P(Doom) detection and click "Actions" > "Allow"
4. Re-download or restore the file if needed

**For Corporate/Managed Systems**:
- IT administrators may need to add exceptions for PyInstaller executables
- Alternative: Provide Python source code installation instructions as fallback

### Technical Details

#### Resource Management

The executable uses `src/services/resource_manager.py` to handle assets:
- **Development mode**: Assets loaded from project directory
- **Bundled mode**: Assets extracted to temporary directory via `sys._MEIPASS`
- **User data**: Configs, saves, and logs stored in `%APPDATA%/PDoom/`

#### Build Artifacts

```
build/               # Temporary build files (can be deleted)
[EMOJI][EMOJI][EMOJI] pdoom/
[EMOJI]   [EMOJI][EMOJI][EMOJI] Analysis-00.toc
[EMOJI]   [EMOJI][EMOJI][EMOJI] PYZ-00.pyz
[EMOJI]   [EMOJI][EMOJI][EMOJI] ...

dist/                # Distribution output
[EMOJI][EMOJI][EMOJI] PDoom-v0.4.1-alpha.exe    # Final executable
```

#### Performance Considerations

- **Startup time**: 2-5 seconds (PyInstaller extraction overhead)
- **Memory usage**: ~50-100MB (Python runtime + game)
- **Disk space**: 19MB for executable + ~5MB extracted assets

### Troubleshooting

#### Common Issues

**"Failed to execute script 'main'"**:
- Usually indicates missing dependencies or import errors
- Check `build/pdoom/warn-pdoom.txt` for warnings
- Verify all modules are included in `pdoom.spec`

**"No module named 'ui'"**:
- Root-level modules must be explicitly included
- Check that `ui.py` is in the `datas` section of `pdoom.spec`

**Assets not loading**:
- Verify `assets/` directory is included in build
- Check `resource_manager.py` is handling bundled paths correctly

**Game crashes on startup**:
- Test with `python main.py` first to ensure source works
- Check for missing hiddenimports in `pdoom.spec`

#### Validation Steps

1. **Build success**: PyInstaller completes without errors
2. **File creation**: `PDoom-v0.4.1-alpha.exe` exists in `dist/`
3. **Startup test**: Executable launches and shows main menu
4. **Asset loading**: Game graphics and sounds work correctly
5. **Save functionality**: Game can create and load save files
6. **Clean exit**: Game closes properly without errors

### Development Workflow

#### Building for Release

1. **Update version**: Modify `src/services/version.py`
2. **Update spec**: Change executable name in `pdoom.spec` if needed
3. **Clean build**: Use `--clean` flag to ensure fresh build
4. **Test thoroughly**: Validate on clean Windows system if possible
5. **Document changes**: Update this guide for any process changes

#### Automated Building

Consider integrating PyInstaller into CI/CD:
```yaml
# Example GitHub Actions step
- name: Build Windows Executable
  run: |
    pip install pyinstaller
    pyinstaller --clean pdoom.spec
    
- name: Upload Artifact
  uses: actions/upload-artifact@v3
  with:
    name: PDoom-Windows-Executable
    path: dist/PDoom-v0.4.1-alpha.exe
```

### Future Improvements

#### Potential Enhancements

- **Code signing**: Eliminate Windows Defender warnings
- **Custom icon**: Add game icon to executable
- **Auto-updater**: Built-in update mechanism
- **Installer**: Optional MSI/NSIS installer for enterprise deployment
- **Cross-platform**: macOS and Linux builds using same PyInstaller approach

#### Size Optimization

Current 19MB is acceptable for alpha/beta, but could be reduced via:
- Excluding unused libraries (current `excludes` list)
- Custom PyInstaller hooks for pygame
- Alternative packaging solutions (cx_Freeze, Nuitka)

---

## Quick Reference

### Essential Commands
```batch
# Install PyInstaller
pip install pyinstaller

# Build executable  
pyinstaller --clean pdoom.spec

# Check output
dir dist\PDoom-v0.4.1-alpha.exe

# Test run (brief)
timeout 10 dist\PDoom-v0.4.1-alpha.exe
```

### Key Files
- `pdoom.spec` - PyInstaller configuration
- `build.bat` / `build.sh` - Build automation scripts  
- `src/services/resource_manager.py` - Asset loading for bundled environment
- `dist/PDoom-v0.4.1-alpha.exe` - Final distributable executable

---

*For technical questions or build issues, refer to the main developer documentation or create an issue in the project repository.*
