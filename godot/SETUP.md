# Godot Setup Guide

This guide helps you get Godot 4.5 running for P(Doom) development.

---

## Option 1: Use Project-Local Godot (Recommended)

The project includes a `tools/godot/` directory where you can download Godot locally.

### Quick Setup Script

Run this from the project root:

```bash
# Create tools directory
mkdir -p tools/godot
cd tools/godot

# Download Godot 4.5 stable (Windows 64-bit)
curl -L -o Godot_v4.5-stable_win64.exe.zip \
  "https://github.com/godotengine/godot/releases/download/4.5-stable/Godot_v4.5-stable_win64.exe.zip"

# Extract
powershell -Command "Expand-Archive -Path 'Godot_v4.5-stable_win64.exe.zip' -DestinationPath '.' -Force"

# Test it
./Godot_v4.5-stable_win64.exe --version
```

You should see: `4.5.stable.official.876b29033`

### Run the Game

```bash
cd godot
../tools/godot/Godot_v4.5-stable_win64.exe project.godot
```

---

## Option 2: System-Wide Install (WinGet)

If you prefer a system-wide install:

```bash
# Install via WinGet
winget install GodotEngine.GodotEngine

# Verify (may need to restart terminal)
godot --version
```

Then run:

```bash
cd godot
godot project.godot
```

---

## Option 3: Manual Download

1. Go to: https://godotengine.org/download/windows
2. Download **Godot Engine - .NET** version 4.5 (Standard)
3. Extract the .zip file
4. Move `Godot_v4.5-stable_win64.exe` to `tools/godot/`
5. Run as shown in Option 1

---

## Verifying Your Setup

### 1. Check Python

```bash
python --version
# Should output: Python 3.13.x or higher
```

### 2. Check Godot

```bash
# If using project-local
./tools/godot/Godot_v4.5-stable_win64.exe --version

# If using system install
godot --version
```

### 3. Test Python Bridge

```bash
cd shared_bridge
echo '{"action": "init_game", "seed": "test"}' | python bridge_server.py
```

You should see JSON output with `"success": true`.

### 4. Test Godot Scene

```bash
cd godot
../tools/godot/Godot_v4.5-stable_win64.exe --headless --script-check scripts/game_manager.gd
```

You should see `[GameManager] Starting...` without errors.

---

## Troubleshooting

### Godot won't run - "VCRUNTIME140.dll missing"

Install Microsoft Visual C++ Redistributable:
- https://aka.ms/vs/17/release/vc_redist.x64.exe

### Python not found

Ensure Python is in your PATH:

```bash
# Windows - add to PATH if needed
where python

# Should show something like:
# C:\Users\YourName\AppData\Local\Programs\Python\Python313\python.exe
```

### Bridge server errors

Check that `shared/` directory has no syntax errors:

```bash
cd shared
python -m py_compile core/game_logic.py
```

### Godot editor crashes on startup

Try the console version for debug output:

```bash
cd godot
../tools/godot/Godot_v4.5-stable_win64_console.exe project.godot
```

---

## Platform-Specific Notes

### Windows
- Use `Godot_v4.5-stable_win64.exe`
- Bridge uses PowerShell for piping (built-in)
- Tested on Windows 11

### Linux (Future)
- Download: `Godot_v4.5-stable_linux.x86_64`
- Bridge should work with bash piping
- May need to mark executable: `chmod +x Godot_*`

### macOS (Future)
- Download: `Godot_v4.5-stable_macos.universal.zip`
- Bridge should work with zsh/bash piping
- May need to allow unsigned app in Security settings

---

## Next Steps

Once Godot is set up:

1. Read [README.md](README.md) for game architecture
2. Open `godot/project.godot` in Godot editor
3. Press F5 to run the game
4. Test the minimal UI (Init Game  ->  Hire Researcher  ->  End Turn)
5. Check the console output for bridge communication logs

---

## Development Setup

### Recommended VS Code Extensions
- **Python** (ms-python.python)
- **GDScript** (geequlim.godot-tools)
- **Godot** (geequlim.godot-tools) - For scene editing

### Godot Editor Settings

Once in the editor, consider:
- **Editor  ->  Editor Settings  ->  Text Editor  ->  Font Size** - Increase if needed
- **Editor  ->  Editor Settings  ->  Run  ->  Window Placement** - Set to "Separate Windows"
- **Editor  ->  Editor Settings  ->  Debugger  ->  Verbose** - Enable for bridge debugging

---

**Last Updated**: 2025-10-17
**Godot Version**: 4.5 stable
**Tested On**: Windows 11, Python 3.13.7
