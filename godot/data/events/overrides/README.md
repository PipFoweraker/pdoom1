# Event Overrides

> **[!] EVERY `.json` IN THIS DIRECTORY IS LOADED AND APPLIED AT STARTUP.**
> There is no "examples are ignored" rule. `event_service.gd::_load_overrides()`
> iterates the whole directory and merges every non-`_`-prefixed key. That
> includes `example.json`, whose FTX override is live in shipped builds.
> Do not park drafts or experiments here.
>
> **Overrides fail SILENTLY on a bad id.** `_apply_overrides()` only fires on an
> exact `id` match against `godot/data/historical_events.json`; a typo or a
> retired id is simply skipped, with no warning. `example.json` shipped two such
> dead keys (`openai_founded`, `chatgpt_released`) until 2026-08-04 -- the file
> teaching the format was wrong in 2 of its 3 examples and nothing said so.
> **Grep `historical_events.json` for your id before trusting an override.**
> Since 2026-08-06 `tests/unit/test_event_retime.gd` asserts every key in every
> file here exists in the corpus -- a dead key is now a red test, not a silence.
>
> **Same key in two files = whole-entry replacement, in directory-listing order**
> (`_load_override_file` assigns, it does not merge across files). If you must
> repeat a key (see `ftx_future_fund_collapse_2022` in both `example.json` and
> `promotion_pass_2026_08.json`), make the entries semantically identical so load
> order cannot matter.

This directory contains game-balance overrides for pdoom-data events.

## Principle

**pdoom-data owns facts and defaults; pdoom1 owns balance tuning via overrides.**

Never modify pdoom-data for game balance. Instead, create override files here that deep-merge onto base events.

## How Overrides Work

1. EventService loads base events from `data/historical_events.json` (pdoom-data export)
2. Override files in this directory are loaded and merged onto matching events
3. Only specified fields are overridden; unspecified fields keep their base values

## File Format

Each override file is a JSON object mapping event IDs to override values:

```json
{
  "event_id_here": {
    "impacts": [
      {"variable": "money", "change": -50000}
    ],
    "rarity": "legendary",
    "pdoom_impact": 10
  }
}
```

## Available Override Fields

- `impacts` - Array of `{variable, change}` pairs (replaces base impacts)
- `rarity` - Override rarity tier: "common", "rare", or "legendary".
  NOTE: `docs/decision-cards/2026-08-02_pdoom-data-contract.md` proposes RETIRING
  rarity from the contract. Do not build new tuning on it.
- ~~`pdoom_impact`~~ - **DEAD FIELD. Setting it does nothing.** It is copied onto
  the game event and then read by NOTHING (zero consumers in `godot/scripts`,
  verified 2026-08-04). It also contradicts ADR-0015, which makes DoomSystem the
  single authority on the doom level. Write a world-state intermediary via
  `impacts` instead.
- `category` - Override event category. This picks the generated decision
  template (incident, policy_event, organization, alignment_research,
  funding_catastrophe...) -- and it is how a record escapes the
  `technical_research_breakthrough` flavour demotion.
- `id` - Rename the event (keyed by the ORIGINAL id; the new id applies before
  the flavour gate runs). Required to promote `arxiv_*` records, whose id prefix
  alone demotes them to the feed. See `promotion_pass_2026_08.json`.
- `year` - Override the historical year (drives the firing turn; see
  `balancing/rarity_curves.json` `timescales` for the turns-per-year dial).
- `significance` - 1-10, scales generated option magnitudes.
- `title` - Override display title
- `description` - Override description text

## Creating an Override

1. Find the event ID in `data/historical_events.json`
2. Create a JSON file (any name) in this directory
3. Add the event ID as a key with your override values
4. Restart the game to apply changes

## Example

See `example.json` for a working example of tuning the FTX collapse event.

## Variable Mapping

pdoom-data uses different variable names. See `balancing/variable_mapping.json` for the full mapping:

| pdoom-data | Game Variable |
|------------|---------------|
| cash       | money         |
| stress     | doom          |
| vibey_doom | doom          |
| reputation | reputation    |
| papers     | papers        |

## Tips

- Start with small adjustments and playtest
- Use `rarity` to control how often major events appear
- Negative money changes should account for early-game economy
- Doom impacts above 10 are very significant
