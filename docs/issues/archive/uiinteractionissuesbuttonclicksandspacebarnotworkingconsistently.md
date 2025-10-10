# UI Interaction Issues: Button clicks and spacebar not working consistently\n\n## Issue Description

Users are reporting issues with button clicks not having consistent effects and spacebar (end turn) stopping working after certain actions or game state changes.

## Symptoms
- Button clicks not registering consistently
- Windows/popups interfering with each other (layering issues)
- Spacebar stops working after some actions between turns 3-10
- Game flow interruption affecting user experience

## Investigation Priority Areas
1. Event handling priority/blocking in main.py event loop
2. Overlay/popup modal behavior interference
3. Keyboard input state management
4. UI element layering and collision detection
5. Tutorial/onboarding state interference

## Potential Root Causes
- Multiple overlay systems competing for event handling
- Modal dialog behavior blocking input
- Tutorial overlay state not properly cleared
- Event handling order in main game loop
- Window manager/overlay manager conflicts

## Branch
Created fix-ui-interaction-issues branch for investigation and fixes\n\n<!-- GitHub Issue #240 -->