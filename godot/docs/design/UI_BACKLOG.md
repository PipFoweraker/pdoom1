# UI / Player-Experience — backlog (pending work for a future UI push)

> Durable home for UI work raised but not completed in the 2026-06-30 session, so it survives
> the lane pause. Pairs with `UI_DECISIONS.md` (the *why* of decisions already made) and the
> round-1 feedback record in `screenshots/dev-blog/ui-player-experience/`.

## Next UI push — concrete, mostly decided
- **Horseshoe / speedometer doom gauge** *(Pip's idea — paused, not abandoned)*. Replace the full
  circle in `doom_meter.gd` with a `<360°` arc (e.g. 270°) that fills like a petrol/gas gauge:
  empty on the left prong → halfway vertical → descending right prong at max. Map 0–100% onto the
  partial arc. Prototype beside the current circle for comparison.
- **Doom-cluster reposition downward** (screen1). Move the doom number / gauge / sparkline cluster
  lower in the middle column. Pip wants this reviewed *coupled* with the gauge redesign + bar size,
  so do it in the same pass as the horseshoe.
- **Expand panel polish**: axis labels, gridlines, and time-series marks/notes on the full-history
  doom panel (feedback line 67).
- **Submenu close-hint formatting**: further readability passes welcome (Pip was "open to
  suggestions"). Current state = styled `✕` top-right + `[ESC] close` bottom-right.
- **Ramp tuning**: now that TERMINAL is saturated dark purple (not black), revisit stop values in
  `ThemeManager.DOOM_STOPS` after seeing it in play — Pip wanted to lean darker overall.

## Future / bigger features
- **Full "Doom Screen"** — a dedicated, richer view the player unlocks via situational awareness:
  - **Event / impact markers** on the doom timeline, Spotify-comments style — inspectable points of
    impact showing what moved doom that turn.
  - **Animation-over-time** playback of the doom trend (Pip liked the background-color-changing
    effect and wants it preserved as a playable animation here).
  - More situational-awareness info surfaced as insight is gained.
- **Sparkline horizontal extent**: the always-on widget is constrained by the middle-column width;
  true wide time-series lives in the expand panel / Doom Screen above.
- **Discoverability**: surface the "click sparkline to expand" + hover tooltips in the tutorial /
  intro (feedback line 62).

## Held pending QA triage / design pass (from PRIMER)
- **#529** CRT/terminal textures — the other parked target; not started this session.
- **#511** highlight newly-available actions — overlaps QA/UX findings; hold until QA triage.
- **#528** Lab Ledger (insight-gated redacted risk page) — wants a design pass with Pip first.

## Reserved-judgment / verify later
- Colorblind mode labels + numeric/resource-bar recolor on the new ramp — Pip reserved judgment.
- Save/load persistence of `doom_history` — built + serialized, but not yet playtested (line 70).

## Dev tooling note
- **Debug doom keys** `PageUp`/`PageDown` (±10, debug-build-gated, in `main_ui._debug_nudge_doom`).
  Release-safe as gated, but remove if undesired before a release build.
