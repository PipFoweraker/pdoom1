#!/usr/bin/env python3
"""Debug typography module loading"""

print("Starting debug...")

try:
    print("1. Importing pygame...")
    import pygame
    print("✓ Pygame imported")
    
    print("2. Importing typing...")
    from typing import Tuple, Optional, Dict, Any
    print("✓ Typing imported")
    
    print("3. Importing weakref...")
    import weakref
    print("✓ Weakref imported")
    
    print("4. Starting class definition...")
    class FontManager:
        def __init__(self):
            print("✓ FontManager init")
    
    print("5. Creating test instance...")
    fm = FontManager()
    print("✓ Test instance created")
    
    print("6. Testing full module import...")
    exec(open('ui_new/components/typography.py').read())
    print("✓ Module execution completed")
    
except Exception as e:
    print(f"✗ Error at step: {e}")
    import traceback
    traceback.print_exc()
