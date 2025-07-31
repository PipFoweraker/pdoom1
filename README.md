# P(Doom): Bureaucracy Strategy Game Prototype

A satirical meta-strategy game about AI Safety, inspired by *Papers, Please*, *Pandemic*, and clicker games.

## Getting Started

### Requirements

- Python 3.8+
- [pygame](https://www.pygame.org/) (`pip install pygame`)

### How to Run

```sh
pip install pygame
python main.py
```

### Main Menu

When you launch the game, you'll see a main menu with the following options:

- **Launch with Weekly Seed**: Start immediately with the current week's challenge seed
- **Launch with Custom Seed**: Enter your own seed for repeatable games  
- **Options**: Placeholder for future settings (currently inactive)
- **Player Guide**: View the complete player guide with controls and strategies
- **README**: View this documentation file

**Navigation:**
- Use mouse clicks or arrow keys to navigate
- Press Enter or click to select an option
- Press Escape to quit from the main menu

### Gameplay

- The game now starts with a **main menu** where you can choose your game mode.
- Select "Launch with Weekly Seed" for the current week's challenge, or "Launch with Custom Seed" to enter your own.
- Enter a seed at startup (or leave blank for weekly challenge seed).
- Select actions (left column) by clicking buttons. Buy upgrades (right) by clicking. Purchased upgrades shrink to icons at the top right.
- Take as many actions as you want, then click "End Turn" (or press Space) to process choices and see results.
- Manage Money, Staff, Reputation, and p(Doom) (AI risk). Pay staff each turn.
- Watch out for random events and opponent progress!
- **Game Over**: p(Doom) reaches 100, all staff leave, or the opponent finishes their AGI.
- At game end, see your turn survived and local high score (per seed).

---

## Adaptive UI

- The window is 80% of your screen by default and resizable.
- UI elements adapt to fit; if crowded, elements may overlap (intentional for "bureaucratic clutter" vibe).
- Upgrades, when purchased, shrink to icons at the top right with tooltips on mouseover.

---

## Expanding the Game

### 1. **Adding/Editing Actions**

- Actions are in `actions.py` as a list of dicts.
- Each dict has: `name`, `desc`, `cost`, `upside`, `downside`, and `rules`.
- Example:
    ```python
    {
        "name": "Lobby Politicians",
        "desc": "+Reputation, possible doom reduction; costly.",
        "cost": 70,
        "upside": lambda gs: (gs._add('reputation', 3), gs._add('doom', -2)),
        "downside": lambda gs: gs._add('money', -10 if random.random() < 0.2 else 0),
        "rules": None
    }
    ```
- Add new actions by adding new dicts to `ACTIONS` in `actions.py`.

### 2. **Adding Upgrades**

- Upgrades are in `upgrades.py` as a list of dicts.
- Each dict: `name`, `desc`, `cost`, `effect_key`.
- Effects are handled in `game_state.py` and referenced in action logic.
- Add new upgrades by adding dicts to `UPGRADES` in `upgrades.py`.

### 3. **Adding/Editing Events**

- Events are in `events.py`.
- Each dict: `name`, `desc`, `trigger` (lambda returning bool), `effect` (lambda for effect).
- Example:
    ```python
    {
        "name": "Media Scandal",
        "desc": "Negative press coverage! Lose reputation.",
        "trigger": lambda gs: gs.reputation > 10 and random.random() < 0.1,
        "effect": lambda gs: gs._add('reputation', -random.randint(2, 4))
    }
    ```
- Add new events by adding dicts to `EVENTS` in `events.py`.

### 4. **Seeded Challenges & Weekly Modes**

- The game prompts for a seed at startup.
- Use the same seed for repeatable scenarios (e.g., weekly challenge, competitions).
- The weekly seed is year+ISO week (e.g., `202531` for 2025 week 31).
- High scores are stored locally for each seed in `local_highscore.json`.

---

## Tips & Modular Structure

- All game content (actions, upgrades, events) is in its own file for easy patching.
- Add new features by editing the relevant file and referencing new upgrades in action/event logic.
- "Cluttered" UI and tooltips for purchased upgrades are intentional for future expansion (e.g., paperwork, news, etc.).
- The code is ready for further modularization and scenario/patch expansion!

---

**Not affiliated with any AI org. For fun, education, and satire only.**