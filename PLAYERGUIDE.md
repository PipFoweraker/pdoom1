# P(Doom) Player Guide

Welcome to **P(Doom): Bureaucracy Strategy Prototype**!  
This guide will help you get started, understand the interface, and make effective decisions.

---

## What is P(Doom)?

P(Doom) is a satirical strategy game about managing an AI safety lab. Your goals are to manage resources, handle events, and survive longer than the reckless "frontier" labs racing to dangerous AI.

---

## How to Start

1. **Install requirements:**  
   - Python 3.8+  
   - pygame (`pip install pygame`)

2. **Run the game:**  
   ```
   python main.py
   ```

3. **Navigate the main menu:**
   - Use mouse clicks or arrow keys (Up/Down) to navigate
   - Press Enter or click to select an option
   - Choose from:
     * **Launch with Weekly Seed**: Start with this week's challenge
     * **Launch with Custom Seed**: Enter your own seed for repeatable games
     * **Options**: Future settings (currently inactive)
     * **Player Guide**: View this guide in-game
     * **README**: View technical documentation

4. **Start playing:** Select a game mode and begin managing your AI safety lab!

---

## Game Loop Overview

- **Select actions** (left panel) by clicking their buttons. Each costs money and has effects (see tooltips).
- **Buy upgrades** (right panel) by clicking available upgrade buttons. Purchased upgrades shrink to icons at the top right.
- **End your turn** by clicking the "END TURN" button (bottom center) or pressing `Space`.
  - **Event Log Reset:** When you end your turn, the activity log is automatically cleared
  - This ensures you only see events from the current turn, keeping information fresh and relevant
- **View resource changes** and random events in the activity log (bottom left).
- **Repeat:** Take actions, buy upgrades, end turn, and react to events.
- **Game ends** if:
  - p(Doom) reaches 100 (catastrophe).
  - All your staff leave.
  - The opponent lab reaches 100 progress.

---

## Controls

| Action             | How to Use          |
|--------------------|-------------------|
| **Main Menu Navigation** | Arrow keys or mouse |
| **Select Menu Item** | Enter or mouse click |
| **Exit Menu/Overlay** | Escape key |
| **Scroll in Overlays** | Up/Down arrow keys |
| Select Action      | Click action button (left) |
| Buy Upgrade        | Click upgrade button (right) |
| End Turn           | Click "END TURN" or press `Space` |
| Toggle Sound       | Click mute button (♪/🔇) in bottom right |
| Tooltips           | Hover mouse over upgrades for more info |
| **Scroll Event Log** | Up/Down arrows or mouse wheel (when unlocked) |
| Quit Game          | Press `Esc` (from main menu or game) |
| Restart (after loss)| Click anywhere on scoreboard |

**Note:** The main menu provides easy access to documentation and different game modes. During gameplay, there is no direct character movement - all interaction is via UI clicks and keyboard shortcuts.

---

## UI Layout

- **Top Bar:** Money, Staff, Reputation, p(Doom), Opponent Progress, Turn, Seed.
- **Second Resource Bar:** Compute, Research Progress, Papers Published.
- **Left Column:** Actions you can take this turn.
- **Right Column:** Upgrades (buttons if available, icons if purchased).
- **Bottom Center:** "END TURN" button.
- **Bottom Right:** Mute button (♪/🔇) to toggle sound effects.
- **Bottom Left:** **Activity Log** (recent events, outcomes)
  - **Important:** The activity log is automatically cleared at the start of each turn
  - Only shows events from the current turn - previous turn events are removed
  - This ensures you see only fresh, relevant information for decision-making
  - Examples of messages: action confirmations, event outcomes, resource changes
  - **Scrollable Event Log Upgrade:** After turn 5, you may unlock an enhanced event log system:
    * **Visual Enhancement:** The event log gains a blue border and "Scrollable" indicator
    * **Full History:** Access to complete activity history from all previous turns
    * **Navigation:** Use arrow keys (↑↓) or mouse wheel to scroll through past events
    * **Turn Organization:** History is organized by turn headers (e.g., "=== Turn 3 ===")
    * **Backward Compatibility:** Current turn events still appear normally for immediate reference
- **Lower Middle:** **Employee Blobs** - animated visualizations of your staff
  - Round blobs representing each employee
  - New hires animate in from the left side
  - Productive employees (with compute access) display glowing halos
  - Positioned in a cluster pattern, no overlapping
- **Scoreboard:** Appears when game ends (game over summary, high score).

---

## Actions

Here are the actions you can take each turn (subject to funds):

- **Grow Community:** +Reputation, possible new staff. Costs money.
- **Fundraise:** Gain money (scaled by reputation), possible small reputation loss.
- **Safety Research:** Reduce p(Doom), +Reputation. Costly.
- **Governance Research:** Reduce p(Doom), +Reputation. Costly.
- **Buy Compute:** Purchase compute resources. $100 per 10 flops. Essential for employee productivity.
- **Hire Staff:** Gain staff, costs money. New employees appear as animated blobs.
- **Espionage:** Chance to learn opponent progress (risky).

Action details and costs are displayed on each button.

---

## Upgrades

Upgrades give ongoing benefits and can be purchased if you have enough money:

- **Upgrade Computer System:** Boosts research effectiveness.
- **Buy Comfy Office Chairs:** Staff less likely to leave if unpaid.
- **Secure Cloud Provider:** Reduces severity of doom spikes from breakthroughs.

Purchased upgrades are shown as icons at the top right; hover for tooltips.

---

## Events

Random events may occur after each turn. Pay attention to the log for effects such as:

- Lab breakthroughs (increase p(Doom))
- Funding crises (lose money)
- Staff burnout (lose staff)
- Special purchases (e.g., accounting software: unlocks balance change display)

---

## High Score

At game over, your survived turns are shown and stored per seed.  
Compete for the best streak!

---

## Compute Resources & Employee Productivity

### Compute System
- **Compute Resource:** Essential for employee productivity, starts at 0
- **Purchase:** Use "Buy Compute" action - $100 per 10 flops
- **Weekly Consumption:** Each employee attempts to use 1 compute per turn (week)
- **Starting Funding:** $100,000 to support expanded compute infrastructure

### Employee Productivity
- **With Compute:** Employees who get compute show glowing halos and contribute to research
- **Without Compute:** Employees without compute incur doom penalties for the organization
- **Research Progress:** Productive employees have a 30% chance each turn to advance research
- **Research Papers:** When progress reaches 100, a paper is published (+5 reputation per paper)

### Employee Blobs
- **Visualization:** Each staff member appears as a round blob in the lower middle area
- **Animation:** New hires animate in from the left side when recruited
- **Clustering:** Blobs automatically position in a non-overlapping cluster pattern
- **Halos:** Productive employees (with compute) display a glowing green halo effect
- **Sound Effects:** New employee blobs make a soft "bloop" sound when hired

### Weekly Cycle
- Each turn represents one week in the organization
- During end turn, employees automatically attempt to consume compute
- Research progress accumulates from productive employees
- Papers are published automatically when thresholds are reached

---

## Advanced Features

### Scrollable Event Log

The **Scrollable Event Log** is an advanced feature that becomes available as your organization grows. This feature enhances your ability to track and review historical activity.

#### How to Unlock

- **Automatic Trigger:** The event log upgrade becomes available after **Turn 5**
- **Event:** "Event Log System Upgrade" - Your organization upgrades its event tracking system
- **No Cost:** This upgrade is provided automatically when conditions are met

#### Features

**Enhanced Visual Design:**
- Blue border around the activity log area
- "Activity Log (Scrollable)" title with scroll instructions
- Visual scroll indicators (▲▼) when more content is available

**Complete History Access:**
- View all events from previous turns, not just current turn
- Turn headers organize events by turn (e.g., "=== Turn 3 ===")
- Events include: actions taken, random events, resource changes, upgrade purchases

**Navigation Controls:**
- **Arrow Keys:** Use ↑ and ↓ to scroll up and down through history
- **Mouse Wheel:** Scroll up and down through the event log
- **Smooth Scrolling:** Navigate through multiple turns of activity seamlessly

**Smart Display:**
- Current turn events remain visible for immediate reference
- History is preserved indefinitely while the feature is active
- Turn headers help you quickly locate specific periods of activity

#### Usage Tips

1. **Strategic Review:** Use the history to review what strategies worked in previous turns
2. **Event Tracking:** Keep track of random events and their timing
3. **Resource Management:** Review past resource changes to identify spending patterns
4. **Decision Making:** Reference past actions when planning future strategies

#### Technical Details

- History storage begins when the feature is unlocked (not retroactive to earlier turns)
- Current turn events function exactly as before - the feature is additive
- Scroll position resets when starting a new game
- The feature remains active for the duration of the game once unlocked

---

## Sound & Settings

### Sound System
- **Default State:** Sound effects are enabled by default
- **Mute Button:** Click the sound icon (♪/🔇) in the bottom-right corner during gameplay
- **Sound Effects:** Includes "blobby" sound when new employees are hired
- **Settings Menu:** Access full settings from the main menu

### Settings Menu
- Available from the main menu by selecting "Settings"
- Provides information about sound controls and gameplay features
- Explains all UI elements and game mechanics
- Press Escape to return to the main menu

### Audio Features
- **Employee Hiring:** Soft "bloop" sound effect when new staff join
- **Mute Toggle:** Instantly enables/disables all sound effects
- **Visual Feedback:** Mute button changes color and icon based on sound state
- **Graceful Fallback:** Game automatically disables sound if no audio device available

---

## Troubleshooting

- If the game window is too small or crowded, resize it.
- If you encounter bugs, restart the game or check the README for troubleshooting tips.

---

## Testing

If you're interested in contributing to P(Doom) or want to verify the game works correctly on your system, you can run the automated tests.

### Running Tests

1. **Install testing dependencies** (if not already installed):
   ```
   pip install pytest
   ```
   Or install all dependencies:
   ```
   pip install -r requirements.txt
   ```

2. **Run all tests:**
   ```
   pytest
   ```

3. **Run tests with verbose output:**
   ```
   pytest -v
   ```

### Sample Test Output

**When tests pass:**
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/runner/work/pdoom1/pdoom1
collecting ... collected 1 item

tests/test_game_state.py::TestGameStateInitialization::test_game_state_default_values PASSED [100%]

============================== 1 passed in 0.01s ===============================
```

**When tests fail:**
```
=================================== FAILURES ===================================
_______________________ TestFailure.test_this_will_fail ________________________

    def test_this_will_fail(self):
        game_state = GameState("test")
>       self.assertEqual(game_state.money, 999, "Expected 999, got 300")
E       AssertionError: 300 != 999 : Expected 999, got 300

temp_failing_test.py:12: AssertionError
=========================== short test summary info ============================
FAILED temp_failing_test.py::TestFailure::test_this_will_fail - AssertionError: 300 != 999
============================== 1 failed in 0.02s ===============================
```

### Troubleshooting

**"No module named pytest"**
- Install pytest: `pip install pytest` or `pip install -r requirements.txt`

**"Import errors"**
- Make sure you're running tests from the project root directory
- Try: `python -m pytest` instead of just `pytest`

**"Permission denied" or file access errors**
- Check that you have read/write permissions in the project directory
- On some systems, use `python3` instead of `python`

### Test Coverage

This project maintains automated tests to ensure game stability and functionality. Current test coverage includes:

- **GameState (`tests/test_game_state.py`)**: 
  - GameState initialization and default values
  - Core resource setup (money, staff, reputation, doom)
  - Game state collections and properties

- **Upgrades (`tests/test_upgrades.py`)**:
  - Upgrade purchasing with sufficient money
  - Upgrade purchase failure with insufficient money  
  - Prevention of duplicate purchases
  - Upgrade effect activation and management
  - Success and failure message generation
  - Upgrade initialization and structure validation

- **Compute & Sound Systems (`tests/test_compute_and_sound.py`)**:
  - Compute resource initialization and management
  - Buy Compute action functionality and costs
  - Employee productivity with and without compute
  - Research progress and papers published tracking
  - Sound system functionality and toggle controls
  - Employee blob system creation and management
  - Sound effect playback (graceful failure handling)

**Contributors:** Please keep this Test Coverage section current when adding new test files or expanding test coverage. This helps other contributors understand what is already tested and what areas might need additional testing.

### For Contributors

See the README.md for detailed information about adding new tests, test structure, and contributor guidelines. When contributing:

1. **Always add or update tests** for your changes
2. **Run the full test suite** before submitting: `pytest`
3. **Update the Test Coverage section** in both README.md and PLAYERGUIDE.md when adding new tests
4. **Ensure all tests pass** - don't break existing functionality

---

## For More Information

- See the README for modding, expanding content, and technical details.

---

Happy surviving!