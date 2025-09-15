#!/usr/bin/env python3
"""Simple test script to validate dialog system imports"""

try:
    from src.ui.dialog_system import draw_fundraising_dialog
    print("✓ Successfully imported draw_fundraising_dialog")
    
    from src.ui.dialog_system import draw_research_dialog
    print("✓ Successfully imported draw_research_dialog")
    
    from src.ui.dialog_system import draw_hiring_dialog
    print("✓ Successfully imported draw_hiring_dialog")
    
    from src.ui.dialog_system import draw_researcher_pool_dialog
    print("✓ Successfully imported draw_researcher_pool_dialog")
    
    print("\n🎉 All dialog system imports successful! Ready to activate in ui.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
