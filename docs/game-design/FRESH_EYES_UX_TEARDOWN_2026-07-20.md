# Fresh-eyes UX teardown -- 2026-07-20 (v0.11.0 build)

> A simulated completely-fresh player, traced through actual code paths.
> Severity: would-quit = likely loses the player; would-struggle = survivable
> confusion; cosmetic = unpolished, not fatal.

## A. Timeline (double-click to minute 30)

- T+0s: exe is unsigned, default Godot icon, empty publisher/description
  (export_presets.cfg:28,35,40,42) -> Windows SmartScreen "unknown publisher".
  A fraction of non-technical players never see frame one.
- T+3s: welcome.tscn boots. Subtitle "Bureaucracy Strategy Prototype"
  (welcome.tscn:111) -- "Prototype" grants permission not to take it seriously.
- T+5s: menu wall of 11 buttons; none says Play/New Game; player must infer
  "Launch Lab" = start (welcome.tscn:120-248). Emoji baked into two labels.
- T+8s: Launch Lab does NOT start a game -- it routes to config_confirmation
  (welcome_screen.gd:136) with jargon (Experimental Seed weekly-2025-w45,
  Research Intensity, ">> INITIALIZE LAB"). A form before play.
- T+12s: main.tscn. Resource bar's Attention readout tooltip still explains the
  RETIRED AP system (main.tscn:152-153 vs main_ui.gd:796-798 relabel). Doom
  instrument jargon undefined outside hover tooltips. Bottom bar exposes a debug
  "Init" button, disabled "Hire SR"/"Reserve AP", and TWO commit buttons
  (main.tscn:328-373). Only onboarding: a 10px hint that self-hides after turn 3
  (plan_screen.tscn:13; main_ui.gd:831-833). No tutorial system exists (verified
  by search).
- T+30s-2min: pressing the big COMMIT THE MONTH with an empty queue hard-errors:
  "ERROR: No actions queued! Press C to clear queue or select actions."
  (main_ui.gd:613-614). The advance-anyway path is a small unrelated "Do
  Nothing" button (plan_screen.tscn:53-56). This is the historical "needs a
  human to explain how to take a turn" failure, still present mechanically.
- Month review dialog is dense and auto-jumps back to PLAN without letting the
  player look around (game_manager.gd:608-625; UI_PASS_NOTES_2026-07-20.md:32).
- First loss: honest cause-specific defeat title exists (game_over_screen.gd:
  262-276) BUT the rich DeathAttribution.classify()/chain_summary() causal trail
  (death_attribution.gd:51-114) is never called by the game-over screen -- it
  only reads ledger.death_attribution. The best "why did I lose" hook is dark.
  Momentum shown as "up (Spiral)/down (Flywheel)" jargon unexplained (:161-165).

## B. Ranked friction list

| # | Severity | Problem | Evidence | Smallest fix |
|---|---|---|---|---|
| 1 | would-quit | Unsigned exe, default icon, empty publisher -> SmartScreen wall | export_presets.cfg:28,35,40,42 | Set icon/company_name/file_description/product_name; ship a "More info -> Run anyway" note. Signing later |
| 2 | would-quit | COMMIT THE MONTH errors on empty queue; advance path hidden | main_ui.gd:613-614; plan_screen.tscn:53-56 | Empty queue -> COMMIT auto-queues the pass action |
| 3 | would-quit | Zero onboarding beyond a self-deleting 10px hint | plan_screen.tscn:13; main_ui.gd:831-833 | One-time 4-sentence first-run modal (goal, Attention, commit, lose condition) |
| 4 | would-struggle | Debug buttons player-visible: Init, disabled Hire SR / Reserve AP, duplicate commit buttons | main.tscn:328-373 | Hide behind dev overlay; collapse to one commit button |
| 5 | would-struggle | Undefined vocabulary in view: P(Doom), Attention, reserve, league baseline, ledger, feed, Spiral/Flywheel | main.tscn:152,245; game_over_screen.gd:161-165 | 1-line on-screen definitions; rename Spiral/Flywheel to plain words |
| 6 | would-struggle | Stale AP tooltip teaches the wrong model on the core resource | main.tscn:152-153 vs main_ui.gd:796 | Rewrite tooltip for Attention |
| 7 | would-struggle | Mandatory config-confirmation form before any game | welcome_screen.gd:136; config_confirmation.tscn:110-221 | Launch Lab starts immediately; config only behind Custom Seed |
| 8 | would-struggle | Death-attribution chain computed but never rendered | death_attribution.gd:51-114; game_over_screen.gd:298-314 | Call chain_summary(); render top 3 causes above the fold |
| 9 | would-struggle | Month review modal auto-jumps to PLAN, no inspection | game_manager.gd:608-625; UI_PASS_NOTES:32 | Dismissible/scrollable review; no auto-jump |
| 10 | would-struggle | 11-button menu, no "Play"; "Prototype" subtitle | welcome.tscn:111,120-248 | Play / Continue / Settings / More; drop "Prototype" |
| 11 | cosmetic+ | Screen density; zones hard to read (dev's own UI notes agree) | main.tscn:55-388; UI_PASS_NOTES:9-51 | Zone background tints; left-align action list |
| 12 | cosmetic | Placeholder values flash pre-state-load ("58.5%", "$0") | main.tscn:91,152,216 | Init labels from state before first paint |

## C. First stuck point with zero coaching

1. Before launch: SmartScreen (item 1). 2. In game: the COMMIT rejection loop
(item 2) on a screen full of undefined terms. If only two fixes land: #2 + #3.

## D. Tell-a-friend loop: currently a dead end

- Shipped leaderboard config is disabled with placeholder URL/token
  (data/leaderboard_config.json: enabled=false, api.example.invalid,
  CHANGE_ME token) -> should_submit() always false; no shared board exists.
- No seed-share / challenge affordance despite deterministic runs; seed field
  only in the pregame form a new player never opens (pregame_setup.tscn:193-198).
- No share/result-card/screenshot button on game over (ScreenshotManager
  autoload exists, unused there); only outbound link is aisafety.info.
- Minimum viable loop: real leaderboard endpoint ON + one "Copy result + seed"
  button producing a single line of shareable text. Retention fixes come first.
