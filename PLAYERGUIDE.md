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
3. **Enter a seed** when prompted, or leave blank for the weekly challenge seed.

---

## Game Loop Overview

- **Select actions** (left panel) by clicking their buttons. Each costs money and has effects (see tooltips).
- **Buy upgrades** (right panel) by clicking available upgrade buttons. Purchased upgrades shrink to icons at the top right.
- **End your turn** by clicking the "END TURN" button (bottom center) or pressing `Space`.
- **View resource changes** and random events in the activity log (bottom left).
- **Repeat:** Take actions, buy upgrades, end turn, and react to events.
- **Game ends** if:
  - p(Doom) reaches 100 (catastrophe).
  - All your staff leave.
  - The opponent lab reaches 100 progress.

---

## Controls

| Action             | How to Use          |
|--------------------|--------------------|
| Select Action      | Click action button (left) |
| Buy Upgrade        | Click upgrade button (right) |
| End Turn           | Click "END TURN" or press `Space` |
| Tooltips           | Hover mouse over upgrades for more info |
| Quit Game          | Press `Esc`         |
| Restart (after loss)| Click anywhere on scoreboard |

**Note:** There is no direct character movement. All gameplay is via UI clicks and the keyboard shortcuts above.

---

## UI Layout

- **Top Bar:** Money, Staff, Reputation, p(Doom), Opponent Progress, Turn, Seed.
- **Left Column:** Actions you can take this turn.
- **Right Column:** Upgrades (buttons if available, icons if purchased).
- **Bottom Center:** "END TURN" button.
- **Bottom Left:** Activity log (recent events, outcomes).
- **Scoreboard:** Appears when game ends (game over summary, high score).

---

## Actions

Here are the actions you can take each turn (subject to funds):

- **Grow Community:** +Reputation, possible new staff. Costs money.
- **Fundraise:** Gain money (scaled by reputation), possible small reputation loss.
- **Safety Research:** Reduce p(Doom), +Reputation. Costly.
- **Governance Research:** Reduce p(Doom), +Reputation. Costly.
- **Hire Staff:** Gain staff, costs money.
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

## Troubleshooting

- If the game window is too small or crowded, resize it.
- If you encounter bugs, restart the game or check the README for troubleshooting tips.

---

## For More Information

- See the README for modding, expanding content, and technical details.

---

Happy surviving!