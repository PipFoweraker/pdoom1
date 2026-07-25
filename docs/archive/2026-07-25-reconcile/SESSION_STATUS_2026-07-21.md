# Session status + RESUME -- 2026-07-21 (compaction handoff)

> v0.11.0 friends-and-family alpha. Core loop works; blocked on ONE leaderboard segfault.
> Read this first; it is the map to finish + ship.

## THE BLOCKER: leaderboard segfault (game-over -> leaderboard), RELEASE-ONLY
- Crash happens LOADING the leaderboard scene, BEFORE its `_ready` runs (confirmed: trace prints never fired). Main-menu transition from game-over works fine, so it is leaderboard-scene-specific, not teardown.
- Suspect: the two bg textures `tex_cyan_ispf_512` / `tex_oxidized_copper_512`. #728 replaced them with ColorRects IN THE SCENE. BUT `theme_manager.gd` (autoload) still lists them as string paths, so they are still PACKED into every export (not necessarily loaded).

### THE TIME-SINK (do not repeat): STALE EXPORT CACHE
`.claude/worktrees/release-build/godot/.godot/exported/` served a STALE converted scene -- every export from that worktree packed the OLD textured leaderboard scene, so #728 (and diagnostic traces) were NEVER in any build Pip tested. `--import` and deleting `.godot/exported/` did NOT clear it. ~12 test cycles wasted re-running the original bug.
- **Discipline:** export from a FRESH `git worktree` (or nuke the whole `.godot/`), and VERIFY the fix is packed by grepping the `.pck` for a unique SCRIPT string you added (e.g. an added `printerr` tag). Do NOT grep for a texture NAME to check scene freshness -- `theme_manager` pulls textures into the pack regardless (always ~4; useless metric).

### IMMEDIATE NEXT STEP
Fresh build (brand-new worktree off origin/main @ 8373332 with #728, from-scratch import) at:
`.claude/worktrees/ship-fresh/builds/PDoom.exe`  -- first genuinely-fresh build with #728.
Pip TESTS it (play -> lose -> leaderboard):
- **Reaches board** -> #728 was right; the release-build worktree was serving stale. Do a clean export from a fresh worktree, then tag v0.11.0.
- **Still crashes** -> the texture is loaded via `theme_manager`'s inclusion, OR the crash is elsewhere. Then: (a) also remove `tex_cyan_ispf`/`tex_oxidized_copper` from `theme_manager.gd` (nothing else uses them), rebuild FRESH, verify, test; and/or (b) add `printerr("[LBTRACE] N ...")` probes to leaderboard_screen.gd `_ready` in a FRESH worktree, build, and read the last trace before the crash.

## DONE + on main (8373332)
Score API LIVE + round-trip verified (`api.pdoom1.com`, nginx+php-fpm on DreamCompute; frozen ADR-0002). Merged: promise-currency early-loss fix, P0 batch, endgame freeze + durable outbox (#705), leaderboard memory leak (#713), load-perf + Clear-Local-Scores (#716), ledger dead-end + auto-discovering no-dead-end test (#711), texture->ColorRect swap (#728), anti-hollow + property tests (ADR-0017), version single-source (sync_version.py), palette/pipeline, music-kit, review app (`serve_review.py`), `apply_review.py`, music session merge (#710).

## Open PRs HELD for Pip's review (Phase 2 -- NOT merged; UI/copy are his calls)
- #715 text-trap fixes (papers tooltip "-3 doom" was FALSE; dev buttons "Hire SR"/"Init" removed; ">> INITIALIZE LAB" -> "Launch Lab"; economy tooltips data-driven)
- #717 menu-consistency (off-black #170A1C, palette, blue->amber, added Menu Chrome Tokens to UI_STYLE_GUIDE.md)
- #712 vision doc; #730 postmortem/lessons doc; #690 art tabbed review viewer; #663 walk cycles; #649/#650 docs; #682 adaptive music (placeholder audio)

## Phase 2 UI backlog (Pip playthrough: docs/game-design/UI_PASS_NOTES_2026-07-20.md + agent reports)
1. Zone-with-color + kill default black (menu agent #717 covers much). 2. FONTS + LICENSING (main-screen white text, button fonts) -- research + offer a pick-menu. 3. PLAN-screen restructure -- Pip's `ABBBCCC` nested-menu idea, hiring buttons out of the vertical stack, planned-action icons a la Civ build queue -- WORKSHOP with Pip, do not agent-guess. 4. Month-review flow -- do not auto-dump to Plan; let player review/scroll/click back. 5. Small: watch-screen purpose text fade after first play; popup color not-green.

### ICONS INTO GAME (Pip's explicit ask, high visual bang)
Resources render EMOJI now (`money_label.text = "money-emoji ..."`, reputation "star ..."). Replace with the generated icons. Steps: Pip marks icon keeps in serve_review.py -> `python tools/art_review/apply_review.py promote` -> `godot --headless --path godot --import` -> an agent wires the top-bar to `[icon][value]` + action-button icons pointing at the promoted keeps.

## Art pile (review via `python tools/art_review/serve_review.py --art-root=<main checkout>`)
gpt icons/heroes/environment (~$18 spent of $40) in `art_generated/`; pixellab office props/characters/tilesets (subscription, $0) in `art_source/pixellab_2026-07-19/`. `apply_review.py`: keeps -> promote to `godot/assets/`, rerolls + notes -> next generation wave.

## Vision (#712, held)
Run telemetry as the game's self-building substrate: VerificationTracker hash + `replay_log` already travel in `export_for_submission()`. Named-discoverer credit graph (attribution). HARD PRINCIPLE: light-touch on the sim -- telemetry/attribution live in the meta layer, never a game lever.

## Facts
- Leaderboard shared token (ships in build, low-value): `SXeZs3NOV37AH5_uv6Nc_R41yq3ZfzzHPuUMYCHzPPujNMBj`
- Distribution: friends-and-family direct download via GitHub Release, linked from website (issue #140). Steam later; web port later. Website = read-only consumer of the score API.
- Pip's main checkout sits on branch `fable/music-session-1`; he self-syncs it. Never auto-pull it.
