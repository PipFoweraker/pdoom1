#!/usr/bin/env python3
"""
Phase 0: Pygame→Godot Migration - Directory Structure Setup

Creates parallel development environment without disrupting existing pygame codebase.
Run from project root: python tools/setup_godot_migration.py
"""

import os
import shutil
from pathlib import Path

def create_migration_structure():
    """Create parallel directory structure for Godot migration."""
    
    project_root = Path.cwd()
    
    # Backup check
    if not (project_root / "main.py").exists():
        raise RuntimeError("Run from pdoom1 project root (main.py not found)")
    
    print("🚀 Phase 0: Setting up Godot migration structure...")
    
    # Create pygame/ directory and move existing code
    pygame_dir = project_root / "pygame"
    if not pygame_dir.exists():
        print("\n📦 Creating pygame/ directory structure...")
        pygame_dir.mkdir()
        
        # Files to move to pygame/
        files_to_move = [
            "main.py",
            "requirements.txt",
        ]
        
        dirs_to_move = [
            "src",
            "tests", 
            "assets",
            "scripts",
            "tools",
        ]
        
        # Move files
        for filename in files_to_move:
            src = project_root / filename
            if src.exists():
                shutil.copy2(src, pygame_dir / filename)
                print(f"  ✓ Copied {filename}")
        
        # Move directories
        for dirname in dirs_to_move:
            src = project_root / dirname
            if src.exists():
                shutil.copytree(src, pygame_dir / dirname, dirs_exist_ok=True)
                print(f"  ✓ Copied {dirname}/")
    else:
        print("  ⚠ pygame/ already exists, skipping copy")
    
    # Create shared/ directory for engine-agnostic logic
    shared_dir = project_root / "shared"
    shared_dir.mkdir(exist_ok=True)
    print("\n🔧 Creating shared/ directory structure...")
    
    subdirs = [
        "core",
        "features", 
        "data",
        "utils",
    ]
    
    for subdir in subdirs:
        (shared_dir / subdir).mkdir(exist_ok=True)
        (shared_dir / subdir / "__init__.py").touch()
        print(f"  ✓ Created shared/{subdir}/")
    
    # Create godot/ project structure
    godot_dir = project_root / "godot"
    godot_dir.mkdir(exist_ok=True)
    print("\n🎮 Creating godot/ directory structure...")
    
    godot_subdirs = [
        "scenes",
        "scripts",
        "scripts/ui",
        "scripts/adapters",
        "scripts/features",
        "assets",
        "assets/fonts",
        "assets/sounds",
        "assets/textures",
        "tests",
    ]
    
    for subdir in godot_subdirs:
        (godot_dir / subdir).mkdir(exist_ok=True)
        print(f"  ✓ Created godot/{subdir}/")
    
    # Create project.godot file
    project_godot = godot_dir / "project.godot"
    if not project_godot.exists():
        project_godot.write_text("""[application]
config/name="P(Doom)"
config/description="Privacy-First Bureaucracy Strategy Game"
run/main_scene="res://scenes/main.tscn"

[display]
window/size/width=1024
window/size/height=768
window/size/resizable=true

[rendering]
environment/default_environment="res://default_env.tres"
""")
        print("  ✓ Created project.godot")
    
    # Create migration tests directory
    tests_dir = project_root / "tests"
    migration_tests = tests_dir / "test_migration"
    migration_tests.mkdir(exist_ok=True)
    (migration_tests / "__init__.py").touch()
    print("\n🧪 Created migration test directory")
    
    # Create tools/migration/ for validation scripts
    migration_tools = project_root / "tools" / "migration"
    migration_tools.mkdir(exist_ok=True)
    print("  ✓ Created tools/migration/")
    
    # Create README files
    create_readme_files(project_root, pygame_dir, shared_dir, godot_dir)
    
    print("\n✅ Phase 0 directory structure complete!")
    print("\nNext steps:")
    print("  1. Review created structure")
    print("  2. Run: python tools/migration/create_engine_interface.py")
    print("  3. Begin logic extraction from pygame/src/core/game_state.py")

def create_readme_files(root, pygame_dir, shared_dir, godot_dir):
    """Create README files explaining each directory."""
    
    # pygame README
    (pygame_dir / "README.md").write_text("""# Pygame Codebase

**Status:** Active development continues here

This directory contains the original pygame implementation.
Development work continues normally while Godot migration proceeds.

## Structure
- `main.py` - Game entry point
- `src/` - Core game code
- `tests/` - Test suite

## Running
```bash
cd pygame/
python main.py
```
""")
    
    # shared README
    (shared_dir / "README.md").write_text("""# Shared Game Logic

**Status:** Engine-agnostic game mechanics

This directory contains pure game logic with NO pygame or Godot dependencies.
Both pygame and Godot implementations use this shared code.

## Structure
- `core/` - Core game state, actions, events
- `features/` - Economic cycles, technical failures, etc.
- `data/` - JSON definitions for actions, events, upgrades
- `utils/` - Helper functions

## Testing
All shared logic is tested independently:
```bash
python -m pytest tests/test_shared_logic/ -v
```
""")
    
    # godot README  
    (godot_dir / "README.md").write_text("""# Godot Implementation

**Status:** In development

This directory contains the Godot port of P(Doom).

## Structure
- `scenes/` - Godot scene files (.tscn)
- `scripts/` - GDScript code
- `assets/` - Game assets (fonts, sounds, textures)

## Running
Open in Godot Engine 4.x and press F5
""")
    
    # Migration tools README
    (root / "tools" / "migration" / "README.md").write_text("""# Migration Tools

Utilities for validating the pygame→Godot migration.

## Scripts
- `validate_parity.py` - Ensures Godot matches pygame behavior
- `extract_logic.py` - Helps extract pure logic from pygame code
- `run_dual_tests.py` - Runs same scenario in both engines
""")
    
    print("  ✓ Created README files")

if __name__ == "__main__":
    create_migration_structure()
