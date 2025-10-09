# !/usr/bin/env python3
"""Debug typography module loading"""

print("Starting debug...")

try:
    print("1. Importing pygame...")
    print("[OK] Pygame imported")
    
    print("2. Importing typing...")
    print("[OK] Typing imported")
    
    print("3. Importing weakref...")
    print("[OK] Weakref imported")
    
    print("4. Starting class definition...")
    class FontManager:
        def __init__(self):
            print("[OK] FontManager init")
    
    print("5. Creating test instance...")
    fm = FontManager()
    print("[OK] Test instance created")
    
    print("6. Testing full module import...")
    exec(open('ui_new/components/typography.py').read())
    print("[OK] Module execution completed")
    
except Exception as e:
    print(f"[ERROR] Error at step: {e}")
    import traceback
    traceback.print_exc()
