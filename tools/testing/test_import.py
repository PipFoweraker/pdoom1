# !/usr/bin/env python3
'''Simple test script to validate dialog system imports'''

try:
    from src.ui.dialog_system import draw_fundraising_dialog
    print('v Successfully imported draw_fundraising_dialog')
    
    from src.ui.dialog_system import draw_research_dialog
    print('v Successfully imported draw_research_dialog')
    
    from src.ui.dialog_system import draw_hiring_dialog
    print('v Successfully imported draw_hiring_dialog')
    
    from src.ui.dialog_system import draw_researcher_pool_dialog
    print('v Successfully imported draw_researcher_pool_dialog')
    
    print('\n[PARTY] All dialog system imports successful! Ready to activate in ui.py')
    
except ImportError as e:
    print(f'[EMOJI] Import error: {e}')
except Exception as e:
    print(f'[EMOJI] Unexpected error: {e}')
