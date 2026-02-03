# Event Integration Plan: Consuming 1,194 pdoom-data Events

**Goal**: Integrate the full 1,194 historical AI safety events from pdoom-data into the game while maintaining clean separation between data and game mechanics per ADR-001.

**Related Issues**: #505 (Override System), #442 (API Fetching), #432/#433 (pdoom-data)

---

## Current State

### What Exists

| Component | Location | Status |
|-----------|----------|--------|
| EventService | `godot/autoload/event_service.gd` | Fetches/caches, transforms to game format |
| Bundled fallback | `godot/data/historical_events.json` | 20 events, OLD format |
| Detailed timeline | `godot/data/historical_timeline/2017.json` | 5 events with options |
| GameEvents | `godot/scripts/core/events.gd` | Hardcoded random events |

### pdoom-data (Source)

| Dataset | Count | Format |
|---------|-------|--------|
| Manual curated | 28 | Full schema with impacts, rarity, reactions |
| Enriched alignment research | 1,166 | Same schema, auto-generated |
| **Total** | **1,194** | JSON with `impacts[]`, `rarity`, `safety_researcher_reaction` |

---

## Implementation Phases

### Phase 1: Directory Structure & Schemas

Create the override system infrastructure:

```
godot/data/events/
  overrides/
    README.md           # How to use overrides
    example.json        # Template override
    ftx_collapse.json   # Example: tune FTX event impacts
  extensions/
    event_chains.json   # A triggers B after N turns
    triggers.json       # Conditional appearance rules
    scenarios.json      # Difficulty mode assignments
  balancing/
    rarity_curves.json  # Probability by rarity tier
    difficulty.json     # Difficulty multipliers
    variable_mapping.json # pdoom-data vars -> game vars
```

**Override Schema** (only include fields to change):
```json
{
  "ftx_future_fund_collapse_2022": {
    "impacts": [
      {"variable": "money", "change": -50000}
    ],
    "rarity": "legendary",
    "pdoom_impact": 10
  }
}
```

**Variable Mapping** (pdoom-data -> game):
```json
{
  "cash": "money",
  "stress": "doom",
  "vibey_doom": "doom",
  "reputation": "reputation",
  "research": "research",
  "papers": "research",
  "burnout_risk": "doom"
}
```

---

### Phase 2: Update EventService for pdoom-data Format

Current EventService expects old format:
```json
{"id": "...", "title": "...", "date": "...", "significance": 8}
```

pdoom-data provides:
```json
{
  "id": "ftx_future_fund_collapse_2022",
  "title": "FTX Future Fund Collapse",
  "year": 2022,
  "category": "funding_catastrophe",
  "description": "...",
  "impacts": [{"variable": "cash", "change": -80}, ...],
  "rarity": "rare",
  "safety_researcher_reaction": "Devastating blow...",
  "media_reaction": "Crypto collapse..."
}
```

**Changes to EventService**:

1. **`_transform_event()`** - Update to:
   - Map `impacts[]` array to game effects
   - Use `rarity` for trigger probability
   - Include `safety_researcher_reaction` and `media_reaction` in event display
   - Generate options based on category + impacts

2. **Add `_apply_overrides()`** - New method to:
   - Load override files from `godot/data/events/overrides/`
   - Deep merge override values onto base event
   - Only override specified fields

3. **Add `_load_variable_mapping()`** - New method to:
   - Load `balancing/variable_mapping.json`
   - Translate pdoom-data variables to game variables

---

### Phase 3: Rarity-Based Trigger System

pdoom-data events have `rarity`: common, rare, legendary

**Rarity Curves** (`balancing/rarity_curves.json`):
```json
{
  "common": {
    "base_probability": 0.15,
    "min_turn": 5,
    "cooldown_turns": 10
  },
  "rare": {
    "base_probability": 0.08,
    "min_turn": 10,
    "cooldown_turns": 25
  },
  "legendary": {
    "base_probability": 0.03,
    "min_turn": 20,
    "cooldown_turns": 50
  }
}
```

**Integration with GameEvents**:
- Historical events get trigger parameters from rarity curves
- Events with specific years trigger around their historical date
- Legendary events are major narrative moments

---

### Phase 4: Event Chains & Triggers

**Event Chains** (`extensions/event_chains.json`):
```json
{
  "chains": [
    {
      "trigger_event": "ftx_future_fund_collapse_2022",
      "unlocks": ["cais_ftx_clawback_2023"],
      "delay_turns": 12,
      "probability": 0.8
    },
    {
      "trigger_event": "openai_founded",
      "unlocks": ["openai_gpt3_released", "openai_safety_team_formed"],
      "delay_turns": 50
    }
  ]
}
```

**Trigger Conditions** (`extensions/triggers.json`):
```json
{
  "triggers": {
    "major_alignment_breakthrough": {
      "min_turn": 50,
      "requires": {"research": 100, "safety_researchers": 3},
      "probability": 0.1
    },
    "regulatory_crackdown": {
      "min_turn": 30,
      "requires": {"doom": 70},
      "probability": 0.2
    }
  }
}
```

---

### Phase 5: Update Bundled Data

Replace `godot/data/historical_events.json` (20 events) with full pdoom-data export:

**Option A**: Bundle `all_events.json` (28 manual + 1,166 enriched)
- Pros: Complete dataset, works offline
- Cons: Large file (~5MB), stale data

**Option B**: Bundle manual events only, fetch enriched on demand
- Pros: Smaller bundle, fresh data
- Cons: Requires network for full experience

**Recommended**: Option A with periodic refresh
- Ship with full 1,194 events bundled
- EventService fetches updates when online
- Cache invalidation based on version in MANIFEST.json

---

### Phase 6: Option Generation for Historical Events

pdoom-data events don't have player options - we generate them.

**Strategy by Category**:

| Category | Options Template |
|----------|-----------------|
| `funding_catastrophe` | Diversify funding, Emergency fundraise, Accept losses |
| `technical_research_breakthrough` | Build upon, Safety analysis, Acknowledge |
| `policy_event` | Support publicly, Offer critique, Stay neutral |
| `organization_founding` | Seek partnership, Monitor, Compete |
| `capability_advance` | Respond publicly, Internal review, Note concerns |

**Using Reactions for Flavor**:
```gdscript
func _generate_options(event: Dictionary) -> Array:
    var options = _get_category_template(event.category)

    # Add flavor from reactions
    if event.has("safety_researcher_reaction"):
        options[0]["flavor"] = event.safety_researcher_reaction
    if event.has("media_reaction"):
        options[1]["flavor"] = event.media_reaction

    return options
```

---

## Implementation Order

1. **Create directory structure** (30 min)
   - `godot/data/events/overrides/`, `extensions/`, `balancing/`
   - README and example files

2. **Add variable mapping** (30 min)
   - `balancing/variable_mapping.json`
   - `balancing/rarity_curves.json`

3. **Update EventService transform** (2 hours)
   - Handle new pdoom-data schema
   - Implement variable mapping
   - Implement rarity-based triggers

4. **Implement override loader** (1 hour)
   - Load override files
   - Deep merge onto base events

5. **Implement event chains** (1.5 hours)
   - Load chain definitions
   - Track triggered events
   - Queue unlocked events

6. **Update bundled data** (30 min)
   - Download full pdoom-data export
   - Replace `historical_events.json`

7. **Create example overrides** (30 min)
   - Tune 3-5 key events
   - Document rationale

8. **Documentation** (30 min)
   - `docs/EVENT_OVERRIDE_SYSTEM.md`
   - Update `CLAUDE.md`

---

## Success Criteria

- [ ] 1,194 events loadable from bundled data
- [ ] Override system allows balance tuning without data changes
- [ ] Event chains create narrative sequences
- [ ] Rarity system controls event frequency
- [ ] Variable mapping translates pdoom-data -> game
- [ ] EventService fetches updates when online
- [ ] Documentation complete

---

## Notes

- **No game logic in pdoom-data**: Chains, triggers, scenarios all live in pdoom1
- **Sensible defaults**: pdoom-data impacts are usable as-is, overrides for tuning
- **ASCII only**: pdoom-data enforces ASCII, no encoding issues
- **Community modding**: Override files are moddable by players
