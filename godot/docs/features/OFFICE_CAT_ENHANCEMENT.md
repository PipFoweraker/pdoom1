# 🐱 Enhanced Office Cat Feature - Godot Port Specification

**Status**: Ready for Implementation  
**Priority**: High (Key feature)  
**Estimated Effort**: 4-6 hours  
**Related**: Existing cat event in Godot main branch

## Overview

This document specifies an enhanced office cat feature to be implemented in the Godot version of P(Doom). The Python prototype implemented a comprehensive office cat system with multiple interactions, visual doom progression, economic integration, and dramatic end-game effects.

## Current State (Godot Main Branch)

The Godot version has a basic cat adoption event (see `godot/CAT_EVENT_COMPLETE.md`):
- One-time event on turn 7
- Three adoption choices (Adopt $500, Feed $100, Shoo $0)
- Static cat emoji (🐱) display
- Basic doom effects (-1 for adoption, +1 for shooing)

## Enhanced Features to Add

### 1. Progressive Adoption System

**Trigger Conditions:**
- Requires 5+ staff for 5+ consecutive turns
- Minimum $89 in funds (basic care package)
- Only triggers once per game

**Adoption Options:**
```
1. Full Care Package: $666
   - Health insurance, deworming, premium setup
   - Best morale benefits
   
2. Basic Care Package: $89
   - Immunizations only
   - Standard morale benefits
   
3. Decline Adoption: $0
   - Cat wanders away
   - No benefits, no costs
```

**Event Message:**
```
🐱 SPECIAL EVENT: A mysterious feline visitor has arrived!
A small, dark cat has wandered into your office and seems quite at home.
Your staff suggest adopting the office cat for morale benefits.
```

### 2. Interactive Cat Petting System

**Mechanics:**
- Cat is clickable (64x64 pixel interaction area)
- Shows floating heart emoji animation when petted (💖)
- Heart floats upward over 2 seconds, fading out
- 30% chance of immediate -1 doom reduction when petted
- Tracks total pets count for statistics

**State Tracking:**
```gdscript
var office_cat_adopted: bool = false
var office_cat_position: Vector2 = Vector2(400, 500)
var office_cat_last_petted: int = 0  # Turn number
var office_cat_love_emoji_timer: float = 0.0
var office_cat_love_emoji_pos: Vector2 = Vector2.ZERO
var office_cat_total_pets: int = 0
```

**Pet Interaction Logic:**
```gdscript
func pet_office_cat(mouse_pos: Vector2) -> bool:
    if not office_cat_adopted:
        return false
    
    # Check if click is within 32 pixels of cat
    if mouse_pos.distance_to(office_cat_position) <= 32:
        office_cat_total_pets += 1
        office_cat_last_petted = current_turn
        
        # Show heart animation
        office_cat_love_emoji_timer = 2.0  # 2 seconds
        office_cat_love_emoji_pos = office_cat_position + Vector2(16, -20)
        
        # 30% chance for doom reduction
        if randf() < 0.3:
            modify_doom(-1, "💖 Petting the cat provides immediate stress relief!")
        
        # Play sound effect
        SoundManager.play_sound("pet_cat")
        return true
    
    return false
```

### 3. Visual Doom Progression (5 Stages)

The cat's appearance changes based on current doom percentage:

**Stage 0: Happy Cat (0-20% doom)**
- Normal appearance
- Peaceful, content

**Stage 1: Concerned Cat (20-40% doom)**
- Slightly darker tint (20% darkening)
- Alert posture

**Stage 2: Alert Cat (40-60% doom)**
- Medium darkening (40%)
- Eyes start to glow faintly

**Stage 3: Ominous Cat (60-80% doom)**
- Heavy darkening (60%)
- Eyes glow red with pulsing effect
- Red tint overlay

**Stage 4: Apocalyptic Cat (80-100% doom)**
- Maximum darkening (80%)
- Bright red glowing eyes
- **LASER EYES** shooting from eyes across the screen
- Flickering laser beams
- Triggers dramatic screen effects

**Implementation:**
```gdscript
func get_cat_doom_stage() -> int:
    if not office_cat_adopted:
        return 0
    
    var doom_percentage = float(current_doom) / float(max_doom)
    
    if doom_percentage < 0.2:
        return 0  # Happy
    elif doom_percentage < 0.4:
        return 1  # Concerned
    elif doom_percentage < 0.6:
        return 2  # Alert
    elif doom_percentage < 0.8:
        return 3  # Ominous
    else:
        return 4  # Apocalyptic
```

### 4. Dramatic End-Game Effects (Doom >= 85%)

When cat reaches stage 4 AND doom >= 85%, add these visual effects:

**Screen Flash Effect:**
```gdscript
# Pulsing red overlay
var flash_intensity = 50.0 * (1.0 + sin(current_turn * 0.8))
# Create red flash surface with varying alpha
```

**Laser Eyes:**
```gdscript
# Draw flickering laser beams from cat's eyes
var laser_alpha = 200 + 55 * sin(current_turn * 1.2)
var laser_width = 2 + 2 * sin(current_turn * 0.8)
# Draw lines from cat eyes to edge of screen
```

**Vignette Effect:**
```gdscript
# Dark edges closing in
# Radial gradient from center (transparent) to edges (dark red/black)
# Intensity increases with doom
```

### 5. Economic Integration

**Weekly Upkeep:**
- $14 per turn when cat is adopted
- Deducted automatically during end_turn()
- Displays in activity log: "🐱 Cat upkeep: $14 (total: $XXX)"
- Tracks cumulative food costs

**Morale Benefits:**
- 30% chance per turn to reduce doom by 1
- Message: "🐱 The office cat provides stress relief for the team!"
- Petting provides additional morale opportunities

**Economic State:**
```gdscript
var office_cat_total_food_cost: int = 0

func process_cat_upkeep():
    if not office_cat_adopted:
        return
    
    const CAT_FOOD_COST = 14
    modify_money(-CAT_FOOD_COST, "🐱 Cat upkeep")
    office_cat_total_food_cost += CAT_FOOD_COST
    
    # 30% chance for morale boost
    if randf() < 0.3:
        modify_doom(-1, "🐱 The office cat provides stress relief for the team!")
```

### 6. Statistics Tracking

Track these statistics for end-game scoreboard:

```gdscript
var office_cat_adopted: bool = false
var office_cat_total_food_cost: int = 0  # Total spent on cat food
var office_cat_total_pets: int = 0       # Times player petted the cat
var office_cat_doom_reductions: int = 0  # Times cat reduced doom
var office_cat_turns_owned: int = 0      # Turns with cat
```

**Scoreboard Display:**
```
Office Cat Statistics:
- Adopted: Yes/No
- Turns with Cat: 45
- Total Food Cost: $630
- Times Petted: 23
- Doom Reductions: 8
- Final Doom Stage: Stage 2 (Alert Cat)
```

### 7. Asset Requirements

**Base Cat Sprite:**
- 32x32 or 48x48 pixel PNG
- Transparent background
- Black cat recommended (works with tinting)
- File: `godot/assets/images/office_cat_base.png`

**Visual Effects:**
- Shader or code-based tinting (no additional sprites needed)
- Eye glow can be drawn programmatically
- Laser beams drawn with line/polygon drawing
- Heart emoji can be drawn or use existing emoji sprites

## Technical Implementation Guide

### Files to Modify

1. **godot/scripts/core/game_state.gd**
   - Add cat state variables
   - Add `get_cat_doom_stage()` method
   - Add `pet_office_cat()` method
   - Add cat upkeep in `process_turn()` or equivalent

2. **godot/scripts/core/events.gd**
   - Modify existing cat event trigger (turn 7  ->  progressive conditions)
   - Add staff tracking logic
   - Add adoption cost options

3. **godot/scripts/ui/main_ui.gd**
   - Add cat sprite rendering
   - Add doom-based visual effects
   - Add petting interaction
   - Add heart animation
   - Add dramatic effects for high doom

4. **godot/scenes/main.tscn**
   - Add cat sprite node (or render via script)
   - Position near bottom-right or configurable position

5. **godot/scripts/ui/end_game_screen.gd** (or scoreboard)
   - Add cat statistics display

### Event Definition Update

Replace or enhance existing cat event:

```gdscript
{
    "id": "office_cat_adoption",
    "name": "🐱 Mysterious Office Visitor",
    "description": "A small, dark cat has wandered into your office and seems quite at home.\nYour staff suggest adopting the office cat for morale benefits.",
    "type": "popup",
    "trigger_type": "custom",
    "trigger": func(state): 
        return (state.staff >= 5 and 
                state.office_cat_turns_with_5_staff >= 5 and 
                state.money >= 89 and 
                not state.office_cat_adoption_offered),
    "repeatable": false,
    "options": [
        {
            "text": "💰 Full Care Package ($666)",
            "cost": 666,
            "effects": {
                "office_cat_adopted": true,
                "doom": -2,
                "office_cat_package": "full"
            },
            "message": "HOME You've adopted the office cat with full care! Premium benefits unlocked."
        },
        {
            "text": "💰 Basic Care Package ($89)",
            "cost": 89,
            "effects": {
                "office_cat_adopted": true,
                "doom": -1,
                "office_cat_package": "basic"
            },
            "message": "HOME You've adopted the office cat! Welcome to the team, little one."
        },
        {
            "text": "💔 Decline Adoption",
            "cost": 0,
            "effects": {},
            "message": "💔 The cat wanders away, disappointed. Maybe another time..."
        }
    ]
}
```

### Staff Tracking Logic

Add to turn processing:

```gdscript
func process_turn_end():
    # ... existing turn processing ...
    
    # Track consecutive turns with 5+ staff for cat adoption
    if staff >= 5:
        office_cat_turns_with_5_staff += 1
    else:
        office_cat_turns_with_5_staff = 0
    
    # Process cat upkeep if adopted
    if office_cat_adopted:
        process_cat_upkeep()
        office_cat_turns_owned += 1
```

## Testing Checklist

- [ ] Cat adoption event triggers after 5+ staff for 5+ turns
- [ ] Insufficient funds prevent adoption
- [ ] Basic package costs $89, full package costs $666
- [ ] Cat sprite displays after adoption
- [ ] Cat is clickable and responds to petting
- [ ] Heart animation displays when cat is petted
- [ ] 30% doom reduction chance works when petting
- [ ] Cat appearance changes through 5 doom stages
- [ ] Stage 4 triggers dramatic effects (flash, laser, vignette)
- [ ] Weekly upkeep deducts $14 per turn
- [ ] Statistics track correctly (food cost, pets, doom reductions)
- [ ] End-game scoreboard displays cat statistics
- [ ] Cat state persists through save/load

## Balance Considerations

**Costs:**
- Full Package $666: Expensive early-game investment
- Basic Package $89: Affordable for established lab
- Weekly $14: Ongoing commitment (similar to 1 staff upkeep)

**Benefits:**
- 30% chance per turn for -1 doom = ~0.3 doom/turn average
- Additional petting opportunities
- Offsets upkeep cost with morale value
- Fun factor and player engagement

**Net Impact:**
- $14/turn cost vs ~$40+ value of -0.3 doom reduction
- Positive ROI if player engages with the cat
- Becomes more valuable at high doom levels

## Future Enhancements (Out of Scope)

These features were mentioned but not implemented in Python version:

1. **Cat Personality System**: Different cat behaviors based on adoption package
2. **Multiple Cat Stages**: Baby  ->  Adult  ->  Elder with different costs/benefits
3. **Cat Upgrades**: Premium food, toys, cat tree for enhanced effects
4. **Photo Upload**: Players upload their real cat photos (mentioned in Godot docs)
5. **Cat Minigames**: Simple interaction games for bonus morale
6. **Office Cat Museum**: Collection of all cats adopted across saves

## Why This Feature Matters

From the original developer notes:

> **"I also really fucking want to get that cat into the game ASAP, it's our only drawcard"**

This isn't just a cute feature:
- **Memorable**: Players will remember and talk about the doom-tracking cat
- **Shareable**: "There's a game where your office cat gets laser eyes at high doom"
- **Emotional**: Creates attachment to the game beyond mechanics
- **Unique**: No other AI safety game has progressive apocalypse cats
- **Extensible**: Opens possibilities for pet-based mechanics

## References

**Python Implementation:**
- `src/core/game_state.py` - Lines 284-293, 1724-1725, 2248-2410 (cat state and logic)
- `src/core/events.py` - `trigger_office_cat_adoption()` function
- `ui.py` - Cat rendering with doom effects and animations
- `tests/test_office_cat.py` - Comprehensive test suite (11 tests)
- `assets/images/office_cat_base.png` - 251-byte placeholder sprite

**Godot Existing Implementation:**
- `godot/CAT_EVENT_COMPLETE.md` - Basic cat event documentation
- `godot/scripts/core/events.gd` - Event system
- `godot/scripts/core/game_state.gd` - State management
- `godot/scripts/ui/main_ui.gd` - UI rendering

## Implementation Priority

**Phase 1 (Core - 2-3 hours):**
1. Update event trigger conditions (staff tracking)
2. Add adoption cost options
3. Implement basic cat sprite rendering
4. Add petting interaction
5. Add weekly upkeep

**Phase 2 (Visual - 1-2 hours):**
6. Implement 5-stage doom progression
7. Add eye glow effects
8. Add heart animation

**Phase 3 (Polish - 1 hour):**
9. Add dramatic end-game effects (laser, flash, vignette)
10. Add statistics tracking
11. Update end-game scoreboard

**Phase 4 (Testing - 30 min):**
12. Test all interactions
13. Verify save/load persistence
14. Balance check

---

**The enhanced office cat is ready to port. Humanity's doom will be slightly lower, and significantly more entertaining. 🐱SPARKLES**

*Document created 2025-11-03 for Godot port planning*
