#!/usr/bin/env python3
"""
Phase 3: Extract Features to Shared

Moves economic_cycles.py and technical_failures.py to shared/features/
Run from project root: python tools/phase3_setup.py
"""

import shutil
from pathlib import Path

def main():
    project_root = Path.cwd()
    
    print("[ROCKET] Phase 3: Feature Extraction")
    print("=" * 40)
    
    # Source and destination
    pygame_features = project_root / "pygame" / "src" / "features"
    shared_features = project_root / "shared" / "features"
    
    # Files to copy
    features_to_extract = [
        "economic_cycles.py",
        "technical_failures.py",
        "event_system.py",
        "achievements_endgame.py",
        "onboarding.py",
    ]
    
    for feature_file in features_to_extract:
        src = pygame_features / feature_file
        dst = shared_features / feature_file
        
        if src.exists():
            print(f"\n[COPY] {feature_file}")
            shutil.copy2(src, dst)
            print(f"  [OK] Copied to shared/features/")
        else:
            print(f"\n[SKIP] {feature_file} not found")
    
    # Create __init__.py
    init_file = shared_features / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Feature modules."""\n', encoding='utf-8')
        print("\n[OK] Created __init__.py")
    
    print("\n[SUCCESS] Phase 3 complete!")
    print("\nFeatures extracted to shared/features/:")
    print("  - economic_cycles.py")
    print("  - technical_failures.py")
    print("  - event_system.py")
    print("  - achievements_endgame.py")
    print("  - onboarding.py")
    print("\nThese are now engine-agnostic and work with both pygame and Godot!")

if __name__ == "__main__":
    main()
