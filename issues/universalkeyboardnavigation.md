# Universal Keyboard Navigation\n\n# Universal Keyboard Navigation: Every Button Has a Key

## Summary
**ACCESSIBILITY PRIORITY**: Implement the design rule "every button in the UI has one default key assignment" to enable complete keyboard-only gameplay and terminal-like accessibility.

## Design Philosophy
Create a game that can be played entirely through keyboard shortcuts, enabling:
- Complete accessibility for users who cannot use a mouse
- Terminal-style gameplay (entering strings of numbers/keys)
- Speed gameplay for advanced users
- Better accessibility compliance
- Alternative input methods

## Core Design Rule
**"Every interactive element must have a dedicated keyboard shortcut"**

## Current State Analysis
The game currently has some keyboard shortcuts but lacks comprehensive coverage:
- Some actions have shortcuts (likely in `keyboard_shortcuts.py`)
- Many UI elements require mouse interaction
- Inconsistent shortcut assignments
- No systematic keyboard navigation

## Implementation Strategy

### Phase 1: Audit and Mapping
- [ ] Audit all interactive UI elements
- [ ] Map existing keyboard shortcuts
- [ ] Identify gaps in keyboard coverage
- [ ] Design consistent shortcut scheme

### Phase 2: Core Navigation
- [ ] Arrow key navigation for all menus
- [ ] Tab/Shift+Tab for element cycling
- [ ] Enter/Space for activation
- [ ] Escape for cancel/back operations

### Phase 3: Action Shortcuts
- [ ] Number keys (1-9) for primary actions
- [ ] Function keys (F1-F12) for secondary functions
- [ ] Letter keys for specific actions (Q=quit, H=help, etc.)
- [ ] Modifier combinations (Ctrl+, Alt+, Shift+)

### Phase 4: Context-Sensitive Help
- [ ] F1 or ? key shows available shortcuts in current context
- [ ] Visual indicators for keyboard shortcuts on buttons
- [ ] Contextual shortcut hints

## Shortcut Design Principles

### 1. Consistency
- Similar actions use similar keys across contexts
- Logical groupings (numbers for actions, F-keys for meta)
- Standard conventions (Ctrl+S save, Ctrl+Q quit)

### 2. Discoverability
- Visual shortcut indicators on UI elements
- Help system showing all shortcuts
- Tooltips displaying shortcut keys

### 3. Efficiency
- Most common actions get single-key shortcuts
- Logical progression (1,2,3 for top actions)
- No excessive modifier key combinations

### 4. Accessibility
- All functionality available via keyboard
- No mouse-only interactions
- Clear visual focus indicators

## Proposed Shortcut Scheme

### Main Game Actions
```
1-9     Action buttons (left panel)
Q       End Turn / Quit context
E       Espionage
R       Research
T       Tutorial/Help
H       Help/Shortcuts
M       Menu
S       Save (when applicable)
```

### Navigation
```
↑↓←→    Navigate UI elements
Tab     Next element
Shift+Tab Previous element
Enter   Activate/Select
Space   Activate/Select (alternative)
Esc     Cancel/Back/Menu
```

### Function Keys
```
F1      Help/Shortcuts
F2      Save
F3      Load
F4      Settings
F5      Refresh/Reset view
F11     Fullscreen toggle
F12     Screenshot
```

### Number Pad (Alternative)
```
Numpad 1-9  Same as main numbers
Numpad +    Zoom in (if applicable)
Numpad -    Zoom out (if applicable)
Numpad *    Toggle view mode
```

## Technical Implementation

### Files to Modify
- `src/services/keyboard_shortcuts.py` - Central shortcut management
- `ui.py` - Add keyboard handling to all UI elements
- Event handling system - Comprehensive key event processing
- Menu systems - Full keyboard navigation
- Button rendering - Visual shortcut indicators

### Architecture Changes
```python
class KeyboardNavigationManager:
    def __init__(self):
        self.shortcut_map = {}
        self.context_stack = []
        self.focus_element = None
    
    def register_shortcut(self, key, action, context=None):
        """Register a keyboard shortcut for an action"""
        
    def handle_key_event(self, event):
        """Process keyboard events and execute actions"""
        
    def show_help(self):
        """Display context-sensitive keyboard help"""
```

### Visual Indicators
- Button labels include shortcut in parentheses: "End Turn (Q)"
- Underlined letters for Alt+ shortcuts
- Help overlay showing all current shortcuts
- Focus highlighting for keyboard navigation

## Accessibility Benefits

### Primary Benefits
- **Complete mouse independence**: Game fully playable without mouse
- **Speed gameplay**: Expert players can use rapid key sequences
- **Accessibility compliance**: Supports users with motor disabilities
- **Alternative inputs**: Supports adaptive hardware and assistive devices

### Advanced Features
- **Macro support**: Sequences of keys for complex actions
- **Terminal mode**: Text-based command interface
- **Voice control ready**: Shortcuts work with speech-to-text
- **Screen reader friendly**: All actions have keyboard equivalents

## Testing Strategy

### Core Tests
- [ ] Complete game playthrough using only keyboard
- [ ] All UI elements accessible via keyboard
- [ ] Consistent shortcut behavior across contexts
- [ ] Help system accuracy and completeness

### Accessibility Tests
- [ ] Screen reader compatibility
- [ ] High contrast mode functionality
- [ ] Various keyboard layouts (QWERTY, DVORAK, etc.)
- [ ] Assistive device compatibility

## Priority Justification
**HIGH PRIORITY** because:
- Fundamental accessibility requirement
- Relatively straightforward to implement
- Massive improvement to user experience
- Future-proofs the game for accessibility compliance
- Enables advanced gameplay styles

## Labels
- enhancement
- accessibility
- keyboard-navigation
- user-experience
- priority-high

## Acceptance Criteria
- [ ] Every interactive UI element has a keyboard shortcut
- [ ] Complete game playable without mouse
- [ ] Visual shortcut indicators on all buttons
- [ ] Context-sensitive help system (F1)
- [ ] Consistent shortcut scheme across all screens
- [ ] No functionality requires mouse interaction
- [ ] Clear focus indicators for keyboard navigation
- [ ] Help documentation for all shortcuts

## Future Enhancements
- Command palette (Ctrl+P) for action search
- Customizable keyboard shortcuts
- Voice command integration
- Mobile/touch accessibility
- Gamepad support using same shortcut system

## Assignee
@PipFoweraker

---
*Accessibility enhancement - making P(Doom) fully keyboard accessible*
\n\n<!-- GitHub Issue #262 -->