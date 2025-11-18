# StarCraft 2 UI Reference for P(Doom)

## Key Concepts to Adopt

### 1. Command Card Layout (Bottom Right)
- Grid of action icons in fixed positions
- Icons are square, consistent size
- Subtle keyboard hints in corner of each icon
- Clear visual hierarchy with selected item highlighted

### 2. Submenu Expansion
- When selecting a building/unit, relevant actions appear in command card
- Actions "open out" into the working space
- Context-sensitive - shows only relevant options

### 3. Keyboard Shortcut Display
- Small letter in corner of each icon (Q, W, E, R, etc.)
- Uses home row and surrounding keys for quick access
- Subtle but visible - doesn't clutter the icon

### 4. Information Panel (Center Bottom)
- Shows selected unit/building details
- Displays progress bars, health, etc.
- Clean separation from command card

## Implementation Plan for P(Doom)

### Phase 1: Current Work
- [x] Icon-based action buttons
- [x] Vertical stack layout on left
- [ ] Subtle keyboard hint overlay on icons (number in corner)
- [ ] Fix icon sizing to fill button properly

### Phase 2: Submenu Expansion
- [ ] When clicking "Hire Staff", expand into middle zone with hiring options
- [ ] Use animation to slide options out
- [ ] Keep parent action visible/highlighted
- [ ] ESC or click outside to collapse

### Phase 3: Polish
- [ ] Hover states with subtle glow/highlight
- [ ] Selection feedback (border highlight)
- [ ] Consistent icon art style
- [ ] Sound effects for selection/hover

## Visual Reference
The SC2 command card shows:
- 3x3 grid of action icons
- Dark background with subtle borders
- Green/cyan accent colors for Protoss
- Numbers 2,3,4,5 visible for queued units

## Adaptation Notes
- P(Doom) uses categories (hiring, research, funding) vs SC2's unit-specific
- We can use submenu expansion for category -> specific action flow
- Info bar at bottom serves similar purpose to SC2's unit info panel
