# Leaderboard Website Integration

> # [!] SUPERSEDED -- the CLI this document is built around no longer exists.
>
> **Audited 2026-08-04.** Every `python scripts/export_leaderboards.py ...`
> command below is dead. That script was DELETED on 2026-08-04: it began
> `from scripts.lib.scores.enhanced_leaderboard import leaderboard_manager` and
> `scripts/lib/` was removed with the Python game, so the script raised
> ImportError on the first line of real work. It had no caller in the Makefile,
> pre-commit or any CI workflow.
>
> Also gone the same day: `tools/web_export/` (its `__init__.py` imported two
> modules, `export_leaderboards` and `privacy_filter`, that were not in the
> package -- so `import tools.web_export` always raised) and
> `tools/integration_test_v0_10_0.py` (imported both).
>
> The LIVE leaderboard path is in-game GDScript: the `LeaderboardSync` autoload
> plus `godot/scripts/ui/leaderboard_screen.gd`, publishing to the website's own
> API. `src/scores/enhanced_leaderboard.py` referenced below is also gone (`src/`
> was the retired Python game).
>
> Kept for the integration contract discussion, not as runnable instructions.

**Date**: 2025-10-30
**Status**: SUPERSEDED 2026-08-04 (was: "Export functionality implemented" -- the export CLI could not import)
**Purpose**: Integrate P(Doom)1 game leaderboards with pdoom1-website

---

## Overview

This document describes the integration between the P(Doom)1 game's leaderboard system and the pdoom1-website public leaderboard display.

### Architecture

```
[P(Doom)1 Game]
      |
      | Plays game, records scores
      |
      v
[Enhanced Leaderboard Manager]
      |
      | Stores local JSON files
      |
      v
[leaderboards/*.json files]
      |
      | Export via export_for_website()
      |
      v
[web_export/*.json files]
      |
      | Copy to website
      |
      v
[pdoom1-website/public/leaderboard/data/*.json]
      |
      | Website displays
      |
      v
[Public Leaderboard Page]
```

---

## Implementation Complete

### 1. Export Function ([src/scores/enhanced_leaderboard.py:376-487](../src/scores/enhanced_leaderboard.py))

Added `export_for_website()` method to `EnhancedLeaderboardManager`:

```python
def export_for_website(self, output_dir: Optional[Path] = None,
                      seed_filter: Optional[str] = None) -> Dict[str, Any]
```

**Features**:
- Converts game leaderboard format to website-compatible JSON
- Supports seed filtering for specific exports
- Includes comprehensive metadata (doom, money, staff, etc.)
- Generates export summary with statistics
- Creates files matching website's expected format

### 2. CLI Export Script ([scripts/export_leaderboards.py](../scripts/export_leaderboards.py))

Command-line tool for easy exports:

```bash
# Export to default directory (./web_export)
python scripts/export_leaderboards.py

# Export specific seed only
python scripts/export_leaderboards.py --seed my-custom-seed

# Export directly to website repository
python scripts/export_leaderboards.py --copy-to-website

# Show detailed export information
python scripts/export_leaderboards.py --verbose
```

---

## Data Format

### Website-Compatible Export Format

```json
{
  "meta": {
    "generated": "2025-10-30T14:26:22.786582Z",
    "game_version": "v0.10.1",
    "total_seeds": 1,
    "total_players": 5,
    "export_source": "game-repository",
    "source_file": "leaderboard_my-seed_abc12345.json",
    "note": "Exported from actual game leaderboard data"
  },
  "seed": "my-custom-seed",
  "economic_model": "Bootstrap_v0.4.1",
  "entries": [
    {
      "score": 85,
      "player_name": "Anthropic Safety Labs",
      "date": "2025-10-30T12:00:00",
      "level_reached": 85,
      "game_mode": "Bootstrap_v0.4.1",
      "duration_seconds": 1245.5,
      "entry_uuid": "uuid-here",
      "final_doom": 15.5,
      "final_money": 2500000,
      "final_staff": 45,
      "final_reputation": 85.0,
      "final_compute": 150000,
      "research_papers_published": 8,
      "technical_debt_accumulated": 12
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `score` | int | Turns survived (primary ranking metric) |
| `player_name` | string | **Misnamed: this carries the LAB name, and since 2026-08-10 the operator too, composed as `Lab -- Operator`.** Max 324 BYTES, derived from the input-field caps (see below) -- large enough that a name typed in the game is never cut at all. |
| `date` | ISO datetime | When score was achieved |
| `level_reached` | int | Final turn number (same as score) |
| `game_mode` | string | Economic model version |
| `duration_seconds` | float | Real-time duration of game session |
| `entry_uuid` | string | Unique identifier for entry |
| `final_doom` | float | P(Doom) risk level at game end |
| `final_money` | int | Money remaining |
| `final_staff` | int | Staff count |
| `final_reputation` | float | Reputation score |
| `final_compute` | int | Compute resources |
| `research_papers_published` | int | Papers published during game |
| `technical_debt_accumulated` | int | Technical debt accrued |

### Name budget: 324 bytes, DERIVED (was 40, and 40 was arbitrary)

**The rule: a name is never silently altered between the field the player types
it into and the public board.** Either it fits, or the field does not accept the
keystroke.

#### What 40 was, and why it was wrong

The old limit was measured off the deployed API and recorded as an external
constraint. On 2026-08-08 the live `(weekly-2026-w32, L4)` board held:

```
"GRIM (Global Risk Intervention Mechanism"    <- 40 bytes, as stored
"GRIM (Global Risk Intervention Mechanism)"   <- 41 bytes, as submitted
```

Measuring it was right. Concluding it was **immovable** was not.
`godot/scripts/leaderboard.gd` stated in terms that `score_api.php` "lives on the
server and is in no repo here". **That was false** -- it is
`server/leaderboard/score_api.php`, in this repository, and the 40 was our own
`substr($s, 0, 40)`. Believing the number external, the client divided it between
the two names instead of raising it, and the live `weekly-2026-w33` board
published:

```
"Bureau of Catastrophe... -- Pip"
```

The literal `...` was **stored data**. A player learned his lab's public name by
reading the board.

Nothing ever needed 40:

- **Storage** is flat JSON -- `MAX_BODY` 8192 per POST, `MAX_ENTRIES` 100 per
  board. A few hundred bytes of name is noise.
- **Display** already coped: the in-game board Label sets
  `OVERRUN_TRIM_ELLIPSIS` (`leaderboard_screen.gd:678`), so it ellipsises at any
  length. Display needing short *rendering* never meant storage needing short
  *data*.
- **No website consumer** in this repo states a column width.
- And 40 **contradicted our own product**: `LabNameGenerator` ships curated lab
  names up to 50 characters -- including the very
  `GRIM (Global Risk Intervention Mechanism)` (41 bytes) the investigation was
  named after.

#### What the budget is now

Not chosen -- **derived**, so that "the player is never edited" is arithmetic
rather than intention:

```
BOARD_NAME_MAX_BYTES = (LAB_NAME_MAX_CHARS + OPERATOR_NAME_MAX_CHARS)
                       * MAX_UTF8_BYTES_PER_CHAR
                       + BOARD_NAME_SEPARATOR_BYTES
                     = (50 + 30) * 4 + 4
                     = 324
```

- **50** is `LabNameGenerator`'s own longest curated output, not a preference.
  A pool entry that outgrows it fails
  `test_the_generator_never_rolls_a_name_the_lab_field_cannot_hold`, at the pool,
  rather than silently on someone's board row.
- **4** is the most bytes one UTF-8 codepoint can occupy, so a field cap counted
  in CHARACTERS can never overflow a budget counted in BYTES, in any script.

Consequently `Leaderboard.fit_board_name()` **cannot fire on anything the UI can
produce**. It remains as a backstop for values that never came from a field (an
edited save, a corrupt local row), and its word-boundary-plus-`...` contract is
still tested as such.

The caps are applied where the names are typed -- `pregame_setup.gd:_ready()`
and the game-over identity prompt -- from these same constants, so the field
stops accepting characters visibly rather than editing the name later.

`tools/check_board_name_budget.py` (pre-commit) fails the commit if
`$MAX_NAME_BYTES` in the PHP and `BOARD_NAME_MAX_BYTES` in the GDScript ever
drift apart, or if the budget is re-frozen into a literal. The two numbers
disagreeing, with nothing comparing them, is the whole defect class.

### A split codepoint DESTROYED THE BOARD (measured 2026-08-10; fixed at source)

This is the severe one, and it was found by probing rather than reading.

A submission whose byte-wise cut at 40 splits a UTF-8 codepoint **empties the
entire board file**. Measured on a throwaway board: 7 rows went to 0 rows while
the server answered

```
HTTP 200  {"ok":true,"added":true,"rank":7}
```

Mechanism, visible in `server/leaderboard/score_api.php`: `substr($s, 0, 40)`
can leave malformed UTF-8; PHP `json_encode()` returns `false` on malformed
UTF-8; the handler then does `ftruncate($fp, 0)` and writes that `false` as an
empty string. Every row is gone and the response still says success.

The trigger is **precisely the split**, not merely being non-ASCII: an over-40
multi-byte name whose cut lands ON a codepoint boundary (21 x 2-byte = 42 bytes)
was stored normally in the same probe run.

**Both halves of this are now fixed in `score_api.php`, in this repo:**

1. `fit_name_bytes()` replaces `substr()` -- it walks back off any partial
   codepoint, so a cut can never emit malformed UTF-8. (No `mbstring`
   dependency; Dreamhost shared PHP is not guaranteed to have it.)
2. The writer **encodes before it truncates**. If `json_encode()` ever returns
   `false`, the board file on disk is left untouched and the caller gets a 500
   instead of a cheerful `{"ok":true}` over an emptied league.

Either guard alone would have prevented the measured wipe; a public board is
worth both.

**DEPLOY GATE:** `score_api.php` is uploaded by hand
(`server/leaderboard/README.md`). Until the new file is on `api.pdoom1.com` the
deployed server is still the old 40-byte byte-wise one, so the upload must land
**before** a game build that sends longer names. Verify with
`curl "https://api.pdoom1.com/score_api.php?seed=...&version=..."` against a
throwaway board, never the live one.

### Two identity values, one wire field (shipped 2026-08-10)

Pip ruled on 2026-08-08 that the board should carry **both** an Operator (the
human) and a Lab (the org), because generated lab names collide and one player
may run several labs over time. He restated it on 2026-08-10 after a second real
external player landed on the live board: *"It'll be good to bump the board to
include player name or we're going to get a LOT of colliding labs."*

**Measured, so no longer a guess:** an unknown extra key on a POST is *accepted*
(HTTP 200) and then **silently dropped** by the `$ALLOWED_FIELDS` whitelist --
absent on read-back. Tested with `operator_name` and with a nonsense control key;
both behaved identically. So the feared rejection does **not** happen, but a
second key delivers nothing either.

Since a second key is a no-op, both names now travel **composed inside the one
frozen `player_name` field**, via `Leaderboard.compose_board_name()`:

```
GRIM -- Pip
GRIM (Global Risk... -- Pip
Kaur, Chen & Lindqvist -- Priya
AI Safety Lab                      <- no operator: byte-identical to before
```

Format rules, each forced by a real constraint:

- **Lab first.** The rows already on the board hold a bare lab in this column;
  leading with the operator would change what the column means halfway down.
- **`--`, not parentheses.** The one real lab name we have,
  `GRIM (Global Risk Intervention Mechanism)`, already contains brackets, so
  `LAB (OPERATOR)` would nest them.
- **Neither half may erase the other, and neither pays for the other.** Each
  name gets its OWN allowance, sized at its own field cap, so adding a
  maximum-length operator cannot shorten the lab by a single character. The
  earlier rule -- operator gets half, lab takes the remainder -- read as fair and
  was not: with the budget too small for either, the lab was simply the half
  that lost, which is how `Bureau of Catastrophe... -- Pip` reached the public
  board.
- **No operator -> unchanged output.** Legacy rows and anonymous players submit
  exactly as they did before: no separator, no empty parenthetical, and no
  back-filled identity on read (`from_dict` defaults `operator_name` to `""`).

`to_wire_dict()` still omits an `operator_name` **key**, now for a measured
reason rather than a cautious one: it is dropped, so sending it would put the
operator on the wire twice and desync the day the server whitelists it.

### Coordination ask (pdoom1-website / API)

The first framing of this list assumed none of it was reachable from here. Two
of the three were: `server/leaderboard/score_api.php` is in this repo and is the
file that gets uploaded.

**Done in this repo, pending a manual upload:**

1. ~~**Fix the board-wipe.**~~ Done both ways -- `fit_name_bytes()` never emits a
   split codepoint, and the writer encodes before truncating so a failed
   `json_encode()` cannot blank a league.
2. ~~**Raise the 40-byte limit.**~~ Done: `$MAX_NAME_BYTES = 324`, derived from
   the client's input-field caps and drift-gated by
   `tools/check_board_name_budget.py`.

**Still genuinely a coordination ask:**

3. **Whitelist `operator_name`** in `$ALLOWED_FIELDS` and render it as a second
   column. Composition inside `player_name` is a workaround for a single-field
   schema, not the right shape: two names in one string cannot be sorted,
   filtered or de-duplicated separately, and any lab name containing ` -- ` has
   to be mangled on the way out (`_collapse_separator`). Structured is better
   whenever the website is ready for a second column.
4. **Return the stored value** in the POST response, so the client can show the
   player what actually landed rather than inferring it. With the budget derived
   this should now always equal what was sent -- which makes it a cheap
   end-to-end assertion rather than a display feature.

---

## Usage Workflows

### Workflow 1: Manual Export for Testing

```bash
# 1. Play games to generate leaderboard data
python main.py

# 2. Export leaderboards
python scripts/export_leaderboards.py --verbose

# 3. Copy files to website
cp web_export/*.json ../pdoom1-website/public/leaderboard/data/

# 4. Test in website
cd ../pdoom1-website
npm run dev
# Visit http://localhost:5173/leaderboard
```

### Workflow 2: Direct Export to Website

```bash
# Export directly to website (if repos are side-by-side)
python scripts/export_leaderboards.py --copy-to-website --verbose
```

### Workflow 3: Weekly League Integration

```bash
# Export specific weekly seed
python scripts/export_leaderboards.py --seed weekly-2025-W44 --copy-to-website

# Website automatically displays new leaderboard
```

---

## Integration Status

### Completed

- SUCCESS Export function in `enhanced_leaderboard.py`
- SUCCESS CLI export script with full options
- SUCCESS Website-compatible JSON format
- SUCCESS Metadata tracking (doom, money, staff, etc.)
- SUCCESS Seed filtering support
- SUCCESS Export summary generation
- SUCCESS Documentation

### Ready for Use

The export functionality is **fully implemented and ready**. To use:

1. **Generate game data**: Play games using Pygame or Godot version
2. **Run export**: Use `scripts/export_leaderboards.py`
3. **Deploy to website**: Copy files to pdoom1-website repository
4. **Website displays**: Public leaderboards update automatically

### Current Limitation

The existing leaderboard JSON files in `leaderboards/` directory have invalid JSON format (single quotes instead of double quotes). These were regenerated as empty files during export testing.

**Solution**: Generate fresh leaderboard data by playing games, which will create properly formatted JSON files.

---

## File Locations

### Game Repository (pdoom1)

```
pdoom1/
|--- src/scores/
|   `--- enhanced_leaderboard.py    # Export function
|--- scripts/
|   `--- export_leaderboards.py     # CLI export tool
|--- leaderboards/                  # Local game leaderboards
|   |--- leaderboard_*.json         # Seed-specific boards
|   `--- sessions/                  # Game session metadata
|--- web_export/                    # Export output (default)
|   |--- seed_leaderboard_*.json    # Website-compatible exports
|   `--- export_summary.json        # Export statistics
`--- docs/
    `--- LEADERBOARD_WEBSITE_INTEGRATION.md  # This file
```

### Website Repository (pdoom1-website)

```
pdoom1-website/
|--- public/leaderboard/data/
|   `--- seed_leaderboard_*.json       # Leaderboards displayed on site
|--- public/leaderboard/
|   `--- index.html                    # Leaderboard page
|--- scripts/
|   `--- export-leaderboard-bridge.py  # Website's bridge script
`--- docs/03-integrations/
    |--- leaderboard-integration-spec.md
    `--- leaderboard-development.md
```

---

## Next Steps

### For Godot Integration

1. **Implement leaderboard in Godot**: Add session tracking to Godot game manager
2. **Connect to Python bridge**: Use existing `EnhancedLeaderboardManager`
3. **Test Godot leaderboards**: Play games and verify data collection
4. **Export and deploy**: Use export script to push to website

### For Website Features

1. **Weekly leagues**: Export weekly seed leaderboards
2. **Live updates**: Automate export on game completion
3. **Player profiles**: Link multiple sessions by player UUID
4. **Statistics dashboard**: Aggregate statistics from export summaries

### For Automation

1. **Git hooks**: Auto-export on game session completion
2. **CI/CD**: Automated deployment to website
3. **API endpoint**: Direct game-to-website score submission
4. **Validation**: Score verification and anti-cheat measures

---

## Technical Notes

### Export Performance

- Processes all leaderboard files in `leaderboards/` directory
- Filters empty leaderboards automatically
- Typical export time: < 1 second for ~50 leaderboards
- Memory efficient: Processes files one at a time

### Data Integrity

- Export preserves all original metadata
- UUID tracking ensures no duplicate entries
- ISO datetime format for cross-platform compatibility
- UTF-8 encoding for international character support

### Compatibility

- **Python**: 3.9+ (uses `Path`, type hints, dataclasses)
- **JSON**: Standard JSON (double quotes, proper escaping)
- **Website**: Compatible with existing leaderboard display code
- **Format version**: Can add version field for future migration

---

## Troubleshooting

### Issue: "No leaderboards exported"

**Cause**: Empty or invalid leaderboard files
**Solution**: Play games to generate fresh leaderboard data

### Issue: "Website directory not found"

**Cause**: pdoom1-website not cloned side-by-side
**Solution**: Use `--output` to specify custom directory or clone website repo

### Issue: "Invalid JSON format"

**Cause**: Legacy leaderboard files with single quotes
**Solution**: Delete old files and generate new ones through gameplay

---

## References

- **Game Leaderboard Code**: [src/scores/enhanced_leaderboard.py](../src/scores/enhanced_leaderboard.py)
- **Website Integration Spec**: [pdoom1-website/docs/03-integrations/leaderboard-integration-spec.md](https://github.com/PipFoweraker/pdoom1-website/blob/main/docs/03-integrations/leaderboard-integration-spec.md)
- **Issue #291**: [Enable Leaderboard System for Alpha Testing](https://github.com/PipFoweraker/pdoom1/issues/291)
- **Website Repository**: [github.com/PipFoweraker/pdoom1-website](https://github.com/PipFoweraker/pdoom1-website)

---

**Implementation Complete**: 2025-10-30
**Ready for Production Use**: Pending fresh game data generation
**Documentation Status**: Complete
