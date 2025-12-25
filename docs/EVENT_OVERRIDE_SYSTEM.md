# Event Override System

**Status:** Implemented (Phases 1-4) | **Issue:** #505

---

## Overview

The Event Override System integrates 1,194 historical AI safety events from the [pdoom-data](https://github.com/PipFoweraker/pdoom-data) repository into the game while maintaining clean separation between source data and game balance tuning.

**Key Principle:** pdoom-data owns facts and defaults; pdoom1 owns balance tuning via overrides.

---

## Architecture

```
pdoom-data (external)          pdoom1 (this repo)
       |                              |
       v                              v
 all_events.json  -->  historical_events.json (bundled fallback)
                              |
                              v
                        EventService
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
    variable_mapping   rarity_curves      overrides/
            |                 |                 |
            +-----------------+-----------------+
                              |
                              v
                     Transformed Events
                              |
                              v
                      GameEvents System
```

---

## Data Flow

1. **Startup:** EventService loads bundled `historical_events.json` (1,194 events)
2. **Config Loading:** Loads variable mapping, rarity curves, and override files
3. **Override Application:** Deep-merges overrides onto matching events
4. **Transformation:** Converts pdoom-data format to game event format
5. **Runtime:** GameEvents checks historical events each turn for triggering

---

## Directory Structure

```
godot/data/events/
    balancing/
        variable_mapping.json   # pdoom-data vars -> game vars
        rarity_curves.json      # Trigger probability/timing by rarity
        difficulty.json         # Difficulty multipliers (future)
    extensions/
        event_chains.json       # Event A triggers Event B (Phase 5)
        triggers.json           # Conditional trigger rules
        scenarios.json          # Scenario-specific settings
    overrides/
        README.md               # How to create overrides
        example.json            # Example override file
        [your_overrides].json   # Custom balance tuning
```

---

## Event Formats

### pdoom-data Format (Input)

```json
{
  "id": "ftx_future_fund_collapse_2022",
  "title": "FTX Future Fund Collapse",
  "year": 2022,
  "category": "funding_catastrophe",
  "description": "$32M+ in AI safety grants vanished overnight...",
  "impacts": [
    {"variable": "cash", "change": -80},
    {"variable": "stress", "change": 50},
    {"variable": "vibey_doom", "change": 25}
  ],
  "rarity": "rare",
  "safety_researcher_reaction": "Devastating blow to AI safety funding",
  "media_reaction": "Crypto collapse takes down AI safety research"
}
```

### Game Event Format (Output)

```json
{
  "id": "hist_ftx_future_fund_collapse_2022",
  "name": "FTX Future Fund Collapse",
  "description": "...",
  "type": "popup",
  "trigger_type": "random",
  "trigger_turn": 287,
  "eligibility_start": 274,
  "eligibility_end": 300,
  "year": 2022,
  "category": "funding_catastrophe",
  "rarity": "rare",
  "trigger_mode": "probabilistic_window",
  "probability": 0.06,
  "options": [...],
  "safety_researcher_reaction": "...",
  "media_reaction": "..."
}
```

---

## Trigger Modes

Events trigger differently based on their rarity:

| Rarity | Count | Trigger Mode | Behavior |
|--------|-------|--------------|----------|
| **Legendary** | 41 | `deterministic` | Always fires at exact turn (100% probability) |
| **Rare** | 1,076 | `probabilistic_window` | 6% chance each turn within 26-turn window |
| **Common** | 77 | `random_after_eligible` | 12% chance each turn after min_turn |

### Turn Calculation

- **Base:** 52 turns per year (weekly turns)
- **Start:** Game begins July 2017 (turn 1)
- **Formula:** `trigger_turn = (year - 2017) * 52 + offset`

**Examples:**
| Year | Event | Rarity | Trigger Turn |
|------|-------|--------|--------------|
| 2017 | Asilomar Principles | Legendary | ~27 |
| 2020 | GPT-3 Released | Legendary | ~183 |
| 2022 | ChatGPT Released | Legendary | ~287 |
| 2022 | FTX Collapse | Rare | ~274-300 (window) |

---

## Variable Mapping

pdoom-data uses different variable names than the game. The mapping is defined in `balancing/variable_mapping.json`:

| pdoom-data Variable | Game Variable | Scale Factor |
|---------------------|---------------|--------------|
| `cash` | `money` | 1000x |
| `money` | `money` | 1000x |
| `stress` | `doom` | 1x |
| `vibey_doom` | `doom` | 1x |
| `burnout_risk` | `doom` | 1x |
| `reputation` | `reputation` | 1x |
| `research` | `research` | 2x |
| `papers` | `papers` | 1x |
| `compute` | `compute` | 10x |

**Example:** pdoom-data `{"variable": "cash", "change": -80}` becomes game effect `{"money": -80000}`

---

## Creating Overrides

### Step 1: Find the Event ID

Look in `godot/data/historical_events.json` for the event you want to tune:

```json
"chatgpt_released_2022": {
  "id": "chatgpt_released_2022",
  "title": "ChatGPT Released",
  "rarity": "rare",
  ...
}
```

### Step 2: Create Override File

Create a JSON file in `godot/data/events/overrides/` (any filename ending in `.json`):

```json
{
  "chatgpt_released_2022": {
    "_reason": "ChatGPT was a watershed moment - make it legendary",
    "rarity": "legendary",
    "impacts": [
      {"variable": "doom", "change": 15},
      {"variable": "reputation", "change": 10}
    ]
  }
}
```

### Step 3: Test

Restart the game. The override will be applied automatically.

### Override Fields

You can override any field from the base event:

| Field | Description |
|-------|-------------|
| `rarity` | Change trigger behavior (`common`, `rare`, `legendary`) |
| `impacts` | Replace the impacts array entirely |
| `pdoom_impact` | Direct doom impact value |
| `category` | Change event category (affects option generation) |
| `title` | Override display title |
| `description` | Override description text |

Fields starting with `_` (like `_reason`) are ignored and can be used for comments.

---

## Rarity Curves Configuration

`balancing/rarity_curves.json` controls trigger behavior:

```json
{
  "legendary": {
    "base_probability": 1.0,
    "min_turn": 1,
    "cooldown_turns": 0,
    "trigger_mode": "deterministic"
  },
  "rare": {
    "base_probability": 0.06,
    "min_turn": 20,
    "cooldown_turns": 15,
    "eligibility_window_turns": 26,
    "trigger_mode": "probabilistic_window"
  },
  "common": {
    "base_probability": 0.12,
    "min_turn": 10,
    "cooldown_turns": 8,
    "trigger_mode": "random_after_eligible"
  },
  "year_trigger": {
    "turns_per_year": 52,
    "base_year": 2017,
    "legendary_month_offset": 26,
    "rare_spread_turns": 13
  }
}
```

---

## EventService API

### Public Methods

```gdscript
# Get all transformed historical events
EventService.get_historical_events() -> Array[Dictionary]

# Get events for a specific year
EventService.get_events_for_year(year: int) -> Array[Dictionary]

# Get events by category
EventService.get_events_by_category(category: String) -> Array[Dictionary]

# Check if events are loaded
EventService.is_ready() -> bool

# Get event count
EventService.get_event_count() -> int

# Force refresh from API/cache
EventService.refresh_events(force: bool = false)

# Reload config files and re-transform
EventService.reload_config()

# Get cache status
EventService.get_cache_info() -> Dictionary
```

### Signals

```gdscript
signal events_loaded(event_count: int)
signal events_fetch_failed(error: String)
signal events_transformed(event_count: int)
```

---

## Category-Based Options

Options are generated based on event category:

| Category | Options |
|----------|---------|
| `organization`, `organization_founding` | Collaborate, Compete, Observe |
| `research`, `paper`, `technical_research_breakthrough` | Build Upon, Safety Analysis, Acknowledge |
| `policy`, `regulation`, `policy_event` | Support, Critique, Stay Neutral |
| `incident`, `capability`, `capability_advance` | Respond Publicly, Internal Review, Note Concerns |
| `funding_catastrophe` | Emergency Fundraise, Diversify Funding, Accept Losses |
| Other | Engage, Acknowledge |

---

## Debugging

### Check Event Cache Status

In-game, press F3 to open debug overlay. Look for:
```
Historical Events: Loaded 1194 events (3 overrides)
```

### Console Commands

```gdscript
# In Godot debugger or console
print(EventService.get_cache_info())
# Output: {cached_count: 1194, transformed_count: 1194, overrides_count: 3, ...}

# Check a specific event
var events = EventService.get_events_for_year(2022)
for e in events:
    print("%s (%s) - turn %d" % [e.name, e.rarity, e.trigger_turn])
```

### Reload Without Restart

```gdscript
EventService.reload_config()
```

---

## Future Work (Phase 5)

- **Event Chains:** One event triggering another after a delay
- **Conditional Triggers:** Events that require specific game state
- **Scenario Assignments:** Different event pools per scenario

See `extensions/event_chains.json` for the planned structure.

---

## Files Reference

| File | Purpose |
|------|---------|
| `godot/autoload/event_service.gd` | Main EventService autoload |
| `godot/data/historical_events.json` | Bundled pdoom-data export (1,194 events) |
| `godot/data/events/balancing/variable_mapping.json` | Variable name mapping |
| `godot/data/events/balancing/rarity_curves.json` | Trigger probability settings |
| `godot/data/events/overrides/*.json` | Balance tuning overrides |
| `godot/scripts/core/events.gd` | GameEvents integration point |

---

## Related Issues

- #442 - API Event Fetching
- #505 - Event Override System
- #432, #433, #437 - pdoom-data repository

---

## Changelog

- **2025-12-25:** Initial implementation (Phases 1-4)
  - 1,194 events from pdoom-data
  - Variable mapping and rarity curves
  - Override system with deep merge
  - Correct 52 turns/year timing
  - Deterministic legendary events
