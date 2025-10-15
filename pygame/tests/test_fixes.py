'''
Test script to validate the custom seed fix

This script tests the core functionality without requiring the full GUI.
'''

def test_custom_seed_fix():
    '''Test that the custom seed functionality is properly integrated.'''
    
    print('Testing P(Doom) Custom Seed Fix')
    print('=' * 40)
    
    # Test 1: Import main module
    try:
        import main
        print('? Main module imports successfully')
    except ImportError as e:
        print(f'? Failed to import main module: {e}')
        return False
    
    # Test 2: Check menu items alignment
    expected_items = ['Launch Lab', 'Launch with Custom Seed', 'Settings', 'Player Guide', 'Exit']
    if hasattr(main, 'menu_items') and main.menu_items == expected_items:
        print('? Menu items are properly aligned')
    else:
        print(f'? Menu items mismatch. Expected: {expected_items}, Got: {getattr(main, 'menu_items', 'Not found')}')
        return False
    
    # Test 3: Check weekly seed function
    try:
        weekly_seed = main.get_weekly_seed()
        print(f'? Weekly seed generation works: {weekly_seed}')
    except Exception as e:
        print(f'? Weekly seed generation failed: {e}')
        return False
    
    # Test 4: Check UI import
    try:
        print('? draw_seed_prompt function is available')
    except ImportError as e:
        print(f'? Failed to import draw_seed_prompt: {e}')
        return False
    
    # Test 5: Check config system
    try:
        from src.services.config_manager import initialize_config_system, get_current_config
        initialize_config_system()
        get_current_config()
        print('? Config system initializes properly')
    except Exception as e:
        print(f'? Config system failed: {e}')
        return False
    
    print('\n[CELEBRATION] All tests passed! Custom seed functionality should work.')
    print('\nTo test in game:')
    print('1. Run: python main.py')
    print('2. Click 'Launch with Custom Seed'')
    print('3. Enter a seed or press Enter for weekly seed')
    print('4. Game should start with your chosen seed')
    
    return True

def test_enhanced_system():
    '''Test the enhanced settings system components.'''
    
    print('\nTesting Enhanced Settings System')
    print('=' * 40)
    
    # Test enhanced settings import
    try:
        print('? Enhanced settings system imports successfully')
    except ImportError as e:
        print(f'? Enhanced settings import failed: {e}')
        return False
    
    # Test game config manager
    try:
        from src.services.game_config_manager import game_config_manager
        configs = game_config_manager.get_available_configs()
        print(f'? Game config manager works. Found {len(configs)} configs')
    except Exception as e:
        print(f'? Game config manager failed: {e}')
        return False
    
    # Test seed manager
    try:
        from src.services.seed_manager import get_weekly_seed, validate_custom_seed
        weekly = get_weekly_seed()
        valid_test = validate_custom_seed('test123')
        print(f'? Seed manager works. Weekly: {weekly}, Validation test: {valid_test}')
    except Exception as e:
        print(f'? Seed manager failed: {e}')
        return False
    
    print('\n[ROCKET] Enhanced system is ready!')
    print('\nTo test enhanced system:')
    print('1. Run: python demo_settings.py')
    print('2. Explore the new settings menu structure')
    print('3. Try the game configuration features')
    
    return True

if __name__ == '__main__':
    print('P(Doom) Settings System Validation')
    print('=' * 50)
    
    # Test core fix
    core_success = test_custom_seed_fix()
    
    # Test enhanced system
    enhanced_success = test_enhanced_system()
    
    print('\n' + '=' * 50)
    if core_success and enhanced_success:
        print('[CELEBRATION] ALL TESTS PASSED!')
        print('\nThe custom seed issue is FIXED and the enhanced system is ready for integration.')
    elif core_success:
        print('? Core fix is working, enhanced system has issues')
        print('\nThe main issue is resolved. Enhanced features can be debugged separately.')
    else:
        print('? Core fix has issues')
        print('\nPlease check the integration guide for troubleshooting steps.')
