# Player docs: current state, SSOT pipeline, roadmap -- 2026-07-20

> Investigation across pdoom1 (game) and pdoom1-website (static site).
> Filed as GitHub issues; this doc is the underlying map.

## Current state

In-game help is THIN and docs oversell it:
- welcome menu has Guide/WhatsNew/Keybindings buttons; player_guide.tscn is a
  static-text stub (content hardcoded in the tscn, no data source).
- whats_new_modal.gd + GameConfig.last_seen_version is a WORKING show-once
  precedent.
- The ONLY in-play onboarding: getting_started_hint in main_ui.gd (visible
  turn < 3) + queue_hint.
- NO tutorial system exists in godot/ (verified: zero hits for tutorial/
  onboard/TutorialManager/hints_enabled). docs/PLAYERGUIDE.md's "comprehensive
  tutorial system and Factorio-style hint system ... press H" claims are stale
  pygame-era aspirational copy -- BUT its four named triggers (first hire,
  first upgrade, out of AP, high doom) are a ready-made Phase 2 spec.
- game_config.gd (user://config.cfg) already has games_played (free first-
  launch detector) and last_seen_version (show-once gate) -- the two
  primitives onboarding needs.

Markdown docs: docs/PLAYERGUIDE.md (827 lines, current to v0.11.0, best SSOT
candidate, needs the false-claims correction); CONTROLS.md,
KEYBOARD_REFERENCE.md, QUICK_REFERENCE.md, DEMO_GUIDE.md. The pre-Godot
archive holds NO reusable onboarding content (checked docs/archive and the
sibling ARchive dir -- unrelated). Onboarding is recreate-from-scratch;
PLAYERGUIDE.md is the one strong reusable asset.

Website: fully static (netlify.toml publish=public; pages hand-authored under
public/). public/docs/ is developer/integration-facing; NO player how-to-play
page exists; nothing renders PLAYERGUIDE.md. Existing sync paths from the game
repo: sync-dev-blog.yml pushes dev-blog entries into website public/blog/ via
WEBSITE_SYNC_TOKEN (the PROVEN push-to-public model); sync-documentation.yml
pushes docs/shared/** into siblings' docs/ (dev-visible, not public) and
carries dead no-op mappings that issue #545 will remove. The leaderboard PHP
channel (score_api.php) is unrelated to docs -- do not model doc sync on it.

## Pipeline decision

Single source of truth: the pdoom1 repo (consistent with #545, source_wins).
Two consumers, two formats, one authored source:
1. Narrative layer: docs/PLAYERGUIDE.md (promote/declare as SSOT) -> rendered
   to website public/docs/how-to-play via a CI push modeled on
   sync-dev-blog.yml, folded into the #545 rewrite rather than a parallel
   workflow.
2. Structured layer: godot/data/help/hints.json ({id, title, body, trigger,
   guide_anchor}) consumed by an in-game HintManager; guide_anchor links each
   hint to a PLAYERGUIDE section so a unit test can flag drift.
The in-game static player_guide.tscn becomes a thin "see full guide" pointer
(do not hand-maintain long text in a tscn).

## Phased roadmap (each shippable)

- Phase 0 (S): SSOT hygiene -- correct PLAYERGUIDE's false tutorial claims;
  declare it SSOT. No code.
- Phase 1 (S): first-launch skeleton -- GameConfig show_hints flag + settings
  toggle; one dismissible first-launch overlay (games_played == 0), reusing
  the show-once pattern.
- Phase 2 (M): data-driven contextual hints -- hints.json + HintManager
  autoload firing show-once popups on the four PLAYERGUIDE triggers. Highest
  gameplay ROI.
- Phase 3 (M/L): opt-in Tutorial Mode -- TutorialManager step overlay,
  relaunchable from the welcome menu, tutorial_completed persisted.
- Phase 4 (S/M): website how-to-play page + CI sync (fold into #545).

Filed as six GitHub issues (SSOT correction; first-launch skeleton; contextual
hints; tutorial mode; website publish + sync; #545 mapping fold-in).
