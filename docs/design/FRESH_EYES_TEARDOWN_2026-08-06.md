# Fresh-eyes teardown -- 2026-08-06 (today's main, post-#1130)

> A simulated completely-fresh player, reconstructed from code on main as of
> 2026-08-06. Method: static read of the scenes/scripts a player meets, in the
> order they meet them. NOT a live playthrough -- everything here is what the
> code says it will show; anything that depends on real rendering, timing, or
> feel is flagged as unverified and pushed to Part D.
>
> Prior art: docs/game-design/FRESH_EYES_UX_TEARDOWN_2026-07-20.md (17 days
> old, predates the cold open, the PLAN/WATCH split, the month review rework,
> the action-bar refit #1130, and the identity prompt). Treated as history;
> where an old finding is still live it is marked [SURVIVES 07-20 #N].
>
> Convention: OBSERVATION = what the code/scene literally contains, with
> file:line. INFERENCE = what I predict a first-time player experiences.
> Confidence is stated per finding.

---

## Part A -- the minute-by-minute walkthrough

### T+0s: the menu

OBSERVATION: welcome.tscn boots. Title "P(Doom)", subtitle "You can't win.
You can only buy time." (godot/scenes/welcome.tscn:58,65). Ten visible
buttons: Launch Lab, Launch with Custom Seed, Settings, Player Guide,
Keybindings, Leaderboard, What's New, AI Safety Info, Exit (Load Game exists
but is hidden, welcome_screen.gd:82). Version bottom-right.

INFERENCE: the subtitle is now doing real work -- it states the core premise
in nine words before anything else happens. Big improvement over 07-20's
"Bureaucracy Strategy Prototype". But the start verb is still "Launch Lab"
[SURVIVES 07-20 #10]: no button says Play or New Game, and "Launch with
Custom Seed" sits directly under it using the word "Seed" before the player
knows the game has seeds.

OBSERVATION: on a genuine first launch, a welcome overlay auto-shows once
(welcome_screen.gd:228-235): "You run an AI safety lab racing to keep
P(Doom) -- the probability of catastrophe -- from hitting 100%." with a
">> Open Player Guide" button (godot/scenes/ui/welcome_overlay.tscn:92-115).

INFERENCE: this is a good 15-second orientation. Its one risk is that it
routes the curious player to the Player Guide -- which teaches the wrong
game (Part B, finding 1).

### T+15s: Launch Lab -> a configuration form

OBSERVATION: Launch Lab does not start the game; it routes to
config_confirmation.tscn (welcome_screen.gd:161-167): "LABORATORY
CONFIGURATION", rows for Player Name ("Researcher"), Lab Name ("AI Safety
Lab"), "Experimental Seed: weekly-YYYY-wNN (Weekly Challenge)" greyed,
"Research Intensity: Standard (Regulatory)" greyed, "Starting Funding:
$245,000" greyed, note "Greyed options are locked for this configuration."
(config_confirmation.tscn:60-176).

INFERENCE [SURVIVES 07-20 #7, softened]: a form before play. It is at least
read-only now, and one click through. But it asks the player to confirm
five values of which a first-timer can meaningfully evaluate zero:
"Experimental Seed" and "Research Intensity" are unexplained jargon
("Research Intensity" is difficulty wearing a costume -- the pregame screen
calls the same value "Difficulty"), and nothing says WHY the seed is locked
or what a Weekly Challenge is. The names default to "Researcher"/"AI Safety
Lab" and nothing here invites editing them (that costs a trip through
"Customize") -- which is exactly how default-identity scores end up on the
board (#1063, and the game-over identity prompt exists to mop this up).

OBSERVATION: ENTER on this screen fires launch, and #1032 (open) records
that ENTER double-fires increment_games_played.

### T+30s: the cold open (first launch only)

OBSERVATION: cold_open_sequence.gd plays once: fade-up lines "Doom is
coming." / "But... when am I? What can I do? What *day* is it?" / "*checks
pockets* -- a primitive phone!", then an interactive phone: tap to wake,
4-digit keypad where any code unlocks ("Oh! how lucky!"), a home screen with
a BANK app showing $245,000 and a MESSAGES app (cold_open_sequence.gd:30-60).

OBSERVATION: the one message a new player is guaranteed to read, from
"Mysterious Helpful Stranger", is: "Hello past me! I am expository filler
(for now). You know nothing yet -- go and find out. Read, show up somewhere,
or be loud online. Scouting. -- MHS" (cold_open_sequence.gd:56). The code
comment says "Copy still Pip's to finalize" -- but it ships.

INFERENCE: the structure is genuinely good (a diegetic on-ramp, a single
active handoff: "go scout"). The copy self-identifying as "expository
filler" is the game telling a first-time player, in its one scripted
narrative beat, that its writing is unfinished. See Part B finding 4.

OBSERVATION: on finish or skip, the sequence sets a first-lever nudge
pointing at action id "scouting" with hint text "Advisor: you do not know
anything yet. Go and find out -- scouting (the glowing button)."
(cold_open_sequence.gd:59-60, 594-598).

### T+2min: main.tscn -- the critical screen

What is on screen at turn 1, top to bottom (main.tscn + runtime mounts in
main_ui.gd _ready):

TOP BAR (8 readouts, one line): title "P(Doom)"; "Turn N - Wed 5 Jul 2017"
(runtime format, main_ui.gd:1908-1922); Money; Compute; Research; Papers;
Rep; "Attention: 20" plus colored asterisk glyphs per staff member
(main_ui.gd:1114-1152). Every readout has a hover tooltip, now generated
from Balance so numbers cannot drift (main_ui.gd:739-750).

- Does a new player know what each means? Money yes. Compute/Research/
  Papers/Rep: the tooltips are good ("100 research = 1 auto-published
  paper") but only exist on hover -- nothing invites hovering.
- Attention: the FACE shows one number; the real mechanic is a two-way
  split (planning hours vs operating hours) that surfaces ONLY in the
  tooltip, which itself admits the problem: "'I have Attention left but the
  button is dead' is otherwise an unexplainable UI state"
  (main_ui.gd:1153-1160). See Part B finding 5.
- The staff glyphs (green/red/blue "*") beside Attention are explained
  nowhere on this screen; the only text explaining the color code is in the
  stale Player Guide (player_guide.tscn:154-156).
- OBSERVATION: before first state paint, the scene's authored placeholders
  are visible: doom "58.5%", "Money: $0", and a turn label reading "Week 1 |
  Mon Jul 3, 2017 | Day 1/5" -- a Week/Day time model the game no longer
  has (main.tscn:96,114,239). Filed as #1031; the stale time-model
  placeholder is worth singling out because for however many frames it
  lives, it teaches a wrong calendar.

MODE BANNER (runtime): "## PLAN - strategy - lay out the month, then COMMIT
THE MONTH >" with a "WATCH >" toggle button (screen_mode.gd:187-200).
INFERENCE: this is the single best orientation device on the screen -- it
names the current mode AND the next verb.

LEFT COLUMN, PLAN screen: "ATTENTION" pip gauge (plan_screen.gd:64-107);
a 10px hint line (the cold-open advisor text); then the HAND: ~15 icon
tiles in a wrapping grid (post-#1130), 70x70px, icon-only, number badges
1-9 on the first nine, category-color tinted, greyed when unaffordable
(action_bar_renderer.gd:184-296). Funding renders first ("FUNDING LEADS",
action_bar_renderer.gd:150). Below: "Upgrades:" list with prices. Bottom:
"Command" zone with a "Do Nothing" button.

- The turn-1 hand (core.json minus locked/hidden): Fundraising, Hire Staff,
  Advertise a Role [SOON, disabled], Work Your Connections, Onboard New
  Hires, Purchase Compute, Safety Research, Capability Research, Publish
  Safety Paper, Travel & Conferences, Operations, Office, Publicity,
  Financing, Scouting. Locked and hidden: Team Building, Safety Audit,
  Strategic, Interview/Make-Offer.
- INFERENCE: tiles carry NO names on their face; the name appears only in
  the tooltip and the hover info bar. A fresh player must hover 15
  unlabeled icons to learn the game's verb set (Part B finding 6; adjacent
  to filed #1132/#1043).
- INFERENCE: at turn 1 most research actions are dead (Safety Research
  costs research:10; the player has 0), so several tiles render greyed with
  the reason visible only on hover. Greyed-without-visible-reason is the
  default first impression of a third of the hand.
- The scouting tile -- the cold-open's "glowing button" -- pulses alpha
  0.4..1.0 (main_ui.gd:1496-1498). Unverified visually whether an alpha
  pulse reads as "glowing" or as "flickering/disabled" (Part D).

MIDDLE COLUMN, instruments: "P(DOOM)" title, numeric doom (starts 20.0%),
doom meter, the line "Buy time [middle-dot] survival is the score | Lose:
P(Doom) = 100%" (main.tscn:269, contains non-ASCII middle-dot -- #1035
family), doom trend sparkline, per-source doom breakdown, a Liability
Ledger summary button, "Employees -- roster & morale" button, Staff Roster,
Action Queue panel.

- OBSERVATION: the doom explanation tooltip reads "Win by solving alignment
  (0%) or finishing below the league baseline. Lose if doom reaches 100% or
  you finish above baseline." (main.tscn:273-275).
- INFERENCE: this is the main screen contradicting the main menu. The
  subtitle said "You can't win"; the doom instrument says "Win by solving
  alignment"; and it prices the win in a term ("league baseline") no new
  player can parse. Part B finding 2.
- "Liability Ledger" as a label at turn 1: unexplained jargon; the ledger
  is empty and nothing says what it will become [SURVIVES 07-20 #5 in
  part; #1037's glossary gap].

RIGHT COLUMN, WATCH screen: hidden in PLAN mode. It holds the feed
("Feed -- the month as it happens:"), two filter toggles ("Hide arxiv
flood", "Hide rival intel"), and the office-floor sprite strip
(watch_screen.gd:36-82).

- INFERENCE: a brand-new player in PLAN mode sees filter toggles for two
  channels ("arxiv flood", "rival intel") they have never seen produce a
  single line. Also: everything main_ui logs via log_message during
  planning -- queue confirmations, several rejection messages -- goes into
  a feed that is INVISIBLE in PLAN mode (Part B finding 7).

BOTTOM BAR: "Reserve Attention" (disabled), "Undo (Z)", "Clear (C)",
"COMMIT THE MONTH >" (teal, runtime relabel of END TURN, main_ui.gd:413),
"Plan (Enter)" (main.tscn:381-386), phase label "SELECT ACTIONS - Click
actions or press 1-9", "Bug Report (N)".

- OBSERVATION: two commit buttons persist. The big teal one commits with
  warnings; "Plan (Enter)"'s tooltip says "Execute queued actions
  immediately without warnings", and its handler ALSO silently reserves all
  remaining Attention (main_ui.gd:1006-1030) -- a semantic difference no
  surface explains.
- INFERENCE: the small button is labeled "Plan" on a screen whose banner
  says "## PLAN". A button named after the mode you are already in, which
  EXITS that mode, is a verb collision a fresh player cannot untangle.
  Part B finding 3 [SURVIVES 07-20 #4, sharpened].

### T+4min: the first decision loop

What tells the player what to do next, in order of strength: the mode
banner ("lay out the month, then COMMIT THE MONTH >"), the phase label
("SELECT ACTIONS - Click actions or press 1-9"), the pulsing scouting tile
plus 10px advisor line, and the disabled-until-queued state of the commit
button. INFERENCE: this is a real improvement over 07-20 (where the answer
was "a 10px hint"). The loop teaches itself IF the player queues something.
The empty-queue hard-error is gone: committing with nothing queued now
auto-passes ("Nothing planned -- the month proceeds.", main_ui.gd:942-952,
fix #733). 07-20 finding #2 is DEAD -- good.

OBSERVATION: after commit, the screen flips to WATCH: green banner, feed,
playback strip "> PLAYBACK || 1x 2x 4x ... day N -- reserve N"
(screen_mode.gd:82-137). The pause button is a visible disabled stub.
INFERENCE: a first month with no reserved Attention and default filters
plays out in ~4-5 seconds of feed lines, then the month review appears.
Whether the WATCH phase reads as "my plan executing" or as "a wall of green
text I did not ask for" is a Part D question.

### T+5min: the first surprise

OBSERVATION: the month review (reworked #1100) is a popup: "August 2017
begins. / Attention: 20 fresh decisions this month (last month's unspent
reserve evaporated -- no banking). / Last month's movement: Funds ... Staff
... Doom band ..." plus, when any rival is visible, "Rivals this month:
<name> (<focus>) -- <drift>" (game_manager.gd:789-826, 908-926). One
teal door-button "Begin planning August 2017 [SPACE]"; the whole review is
also mirrored into the feed so dismissing it costs nothing.

- OBSERVATION: two of three rival labs start at visibility KNOWN
  (rivals.gd:159-166), so the FIRST month review names rival labs with a
  capability-drift label -- and no surface has ever said the game has
  rivals, what "focus" means, or why I should care. FILED as #1088, still
  open; confirmed live in code.
- INFERENCE: mid-month response windows (event dialogs) can also fire
  before any of this is explained; the dialog itself is decent (lettered
  choices, inline costs, "(Free)" marked, rejection shows a reason and
  keeps the dialog open -- event_dialog.gd:65-250).

### Death and the board

OBSERVATION: game_over_screen.gd is now rich: cause-specific defeat title,
a rendered CAUSE OF DEATH attribution chain (EE-8 -- 07-20 finding #8 is
DEAD), score + baseline comparison, "Copy result" share line, the
default-identity prompt before a default-named score uploads (#1133), and
a consent dialog before any remote submit. Leaderboard screen explains
what a board is (#1048) and makes global-fetch failure visible (#1126).

- OBSERVATION: momentum still prints as "^ 1.2 (Spiral)" / "v (Flywheel)"
  (game_over_screen.gd:181) [SURVIVES 07-20 #5, narrow residue].
- OBSERVATION: a victory branch exists: "VICTORY! / Humanity Survived the
  AI Revolution" (game_over_screen.gd:137-140) -- the third surface to
  disagree about whether winning exists.
- OBSERVATION: "Accept Your Fate (end run)" in the pause menu resigns with
  NO confirmation -- one click, ESC-menu adjacency, immediately drives doom
  to the lose threshold (pause_menu.gd:68-79, game_manager.gd:480-500).
  A resigned run therefore also gets the doom-death headline "The AI
  Destroyed Humanity", which is not what the player did. Part B finding 8.
- INFERENCE: no in-run path back to the Player Guide exists -- the pause
  menu has Resume / Accept Fate / Main Menu / Quit only. A player who gets
  lost at turn 6 (after the hint self-hides at turn 3, main_ui.gd:1203)
  has no help surface short of abandoning to the main menu. Part B
  finding 9.

---

## Part B -- ranked findings

Ranked by (players who hit it) x (damage). FILED = an open issue already
covers substantially this; NEW = not found in the open issue list
(#1031-#1135 titles reviewed 2026-08-06).

### 1. NEW -- The Player Guide teaches a different, wrong game
- Player experience: the one surface every confused player is DIRECTED to
  (the first-launch overlay's ">> Open Player Guide" button) says: "Your
  goal is to reduce P(Doom) to 0% before running out of money or turns"
  and "P(Doom): The probability of AI catastrophe - REDUCE TO ZERO TO
  WIN!" (player_guide.tscn:95-97,158). It also teaches retired controls:
  "Space/Enter: End turn and execute queued actions" (no PLAN/WATCH, no
  COMMIT THE MONTH, no month playback, no Attention split; :118-127), and
  carries the pygame-era subtitle "How to Navigate P(Doom): Bureaucracy
  Strategy" (:63) plus non-ASCII bullets/dots (:125,154-156, #1035 family).
- Mechanism: player_guide.tscn is static scene text, apparently untouched
  through the ADR-0002 no-victory ruling, the attention migration (#996),
  and the PLAN/WATCH split. Nothing regenerates or checks it (the DQ_INDEX
  anti-rot pattern does not cover player-facing help).
- Damage: a diligent new player -- exactly the kind who reads guides --
  builds the wrong model of the objective ("push doom to 0 or lose") and
  the wrong model of the controls, then finds neither works. The players
  who skip the guide are better off than the ones who do the intended
  thing. This inverts the value of the whole onboarding chain.
- Confidence: HIGH (text is unambiguous; the overlay routing to it is
  unambiguous). Impact estimate: hits ~100% of guide-readers; guide-reader
  fraction unknown (Part D).

### 2. NEW -- Three surfaces disagree about whether you can win
- Player experience: menu subtitle "You can't win. You can only buy time."
  (welcome.tscn:65). Doom instrument tooltip: "Win by solving alignment
  (0%) or finishing below the league baseline." (main.tscn:273-275).
  Player Guide: "REDUCE TO ZERO TO WIN!". Game over: "VICTORY! Humanity
  Survived the AI Revolution" (game_over_screen.gd:137-140). Resign
  tooltip: "There is no way to win P(Doom)" (pause_menu.tscn:172).
- Mechanism: the no-victory ruling (ADR-0002, DESIGN_PHILOSOPHY "no
  victory, only time bought") landed in the subtitle and resign tooltip
  but was never swept through main.tscn's doom tooltip, the guide, or the
  game-over victory branch. "League baseline" additionally prices the
  claimed win in a term no first-run surface defines.
- Damage: the core emotional contract of the game -- the thing the design
  philosophy calls load-bearing and never-patch -- is stated three
  different ways. Players argue with the score instead of the world.
- Confidence: HIGH on the texts; MEDIUM on whether a victory state is
  actually reachable in current balance (unverified -- if it is not, the
  victory branch is dead code that still cost the tooltip its honesty).

### 3. PARTIALLY FILED (#1041/#1043 adjacent; core is old 07-20 #4) --
###    "Plan (Enter)" is a second commit button named after the mode it exits
- Player experience: bottom bar shows the teal "COMMIT THE MONTH >" and a
  small "Plan (Enter)". The screen banner says "## PLAN". Pressing the
  button named "Plan" ends planning, with no warnings, and silently
  reserves all remaining Attention (main_ui.gd:1006-1030) -- a different
  outcome from the big button, explained only across two tooltips.
- Mechanism: END TURN was relabeled at runtime for the PLAN/WATCH model
  (main_ui.gd:413) but CommitPlanButton kept its scene-authored label and
  its distinct reserve-all semantics (main.tscn:381-386).
- Damage: every player faces this pair every single turn. Best case they
  never notice the small button; worst case they commit months early with
  everything reserved and cannot say why the two buttons differ.
- Confidence: HIGH on mechanism; MEDIUM on frequency of harm (the small
  button may be visually recessive enough to be ignored -- Part D).

### 4. NEW -- The cold open ends on copy that calls itself placeholder
- Player experience: the single scripted narrative moment of the game
  hands over: "I am expository filler (for now)." (cold_open_sequence.gd:56).
- Mechanism: TODO copy shipped behind a "Pip's to finalize" comment; the
  show-once gate means every new player sees it exactly once -- at maximum
  first-impression leverage.
- Damage: reads as either a bug or a shrug. It undercuts the (genuinely
  strong) diegetic on-ramp at its climax. One string fix; listed this high
  because 100% of new players see it at minute two.
- Confidence: HIGH.

### 5. NEW -- The Attention hour-split produces dead buttons the HUD cannot explain
- Player experience: the HUD face says "Attention: 20"; an action tile or
  submenu option is dead anyway, because the real budget is split into
  planning vs operating hours and hour_type-tagged actions draw from one
  side only (main_ui.gd:1620-1629; tooltip text :1156-1160 -- which itself
  names the failure: "'I have Attention left but the button is dead' is
  otherwise an unexplainable UI state").
- Mechanism: the split exists in month_plan (ADR-0011); the only surface
  is a hover tooltip on the Attention readout. Neither the pip gauge, the
  action tiles, nor rejection feedback name which hour type an action
  wants (and see finding 7 for where the rejection text goes).
- Damage: mid-run confusion for anyone who plans a full month; it looks
  like the fundraise-invisibility class -- a systemic rule invisible at
  the point of failure.
- Confidence: HIGH that the surface is tooltip-only; MEDIUM on how often a
  turn-1..5 player actually collides with the split (depends on balance
  numbers not audited here -- Part D).

### 6. PARTIALLY FILED (#1132 "cap the top bar at 10 buttons", #1043) --
###    Fifteen unlabeled icon tiles are still the whole verb set
- Player experience: the hand is icon-only 70px tiles; names exist only on
  hover (tooltip = bare name; info bar = name/desc/costs). To learn what
  the game lets you DO, you hover 15 icons one at a time. About a third
  are greyed at turn 1 with the reason (missing research/staff) visible
  only in the hover info bar.
- Mechanism: action_bar_renderer.gd:219-296 (_build_action_tile: icon +
  number badge, no name label). #1130 fixed position/wrap (fundraise is
  now tile 1, all above the fold) but not labeling.
- Damage: the fundraise incident generalizes: any action whose ICON does
  not communicate is invisible-in-plain-sight. The grouped P9 layout (rows
  WITH names) already exists behind the "proposed" layout flag
  (_render_grouped, :301-358) -- the fix is built but not default.
- Confidence: HIGH on structure; icon comprehensibility itself is
  unverifiable by reading (Part D).

### 7. NEW -- In PLAN mode, several rejection/feedback messages go to a hidden feed
- Player experience: some clicks do nothing visible. Example path: an
  action passes the tile-level cost check but fails the hour-type check;
  the handler logs "[color=red]Not enough Attention: need N ..." via
  log_message -- into the WATCH feed, which is invisible in PLAN mode --
  and returns (main_ui.gd:1620-1633). The PLAN error toast exists but only
  receives engine error_occurred signals (EventResultPresenter), not these
  early-return logs. Same for "Cannot afford action" (:1632) and the
  queue/pass confirmations.
- Mechanism: log_message writes only to watch_screen.message_log
  (main_ui.gd:1407-1433); ScreenModeController hides the whole watch
  subtree in PLAN (screen_mode.gd:154-162). The 2026-07-24 toast fix
  covered the signal path, not the direct-log path.
- Damage: silent-click is the single most trust-destroying UI behavior;
  the project's own #1126 write-up ("a failed request and a broken button
  must never look the same") states the principle this violates.
- Confidence: MEDIUM -- the reachable set of these paths depends on
  tile-disable coverage I could not exhaustively verify; the mechanism
  (log-to-hidden-surface) is certain.

### 8. NEW -- "Accept Your Fate" is one unconfirmed click, and mislabels the death
- Player experience: ESC (a reflex key) opens the pause menu; the second
  button ends the run permanently with no confirmation
  (pause_menu.gd:68-79). The implementation drives doom to the lose
  threshold (game_manager.gd:480-500), so the defeat screen then headlines
  "The AI Destroyed Humanity" for a player who resigned.
- Mechanism: deliberate cheap-form design (#959) reusing the proven loss
  route; the tooltip does explain the consequence, but tooltips are not
  guards. There is no save/load for players (both hidden), so the loss is
  total.
- Damage: low frequency, maximal severity per hit (a misclick erases a
  run; the death headline then gaslights). Note untracked
  test_resign_destructive.gd.uid in the worktree suggests someone is
  already circling this; no open issue found.
- Confidence: HIGH on code path; the misclick frequency is a guess.

### 9. NEW -- After turn 3, there is no help surface inside a run
- Player experience: the getting-started hint self-hides at turn 3
  (main_ui.gd:1203); the first-lever pulse retires by turn 3 (:1207); the
  welcome overlay and cold open are show-once. From turn 3 on, a lost
  player's only help is the Player Guide -- reachable ONLY from the main
  menu (pause menu has no guide entry, pause_menu.tscn:153-193), and
  currently wrong (finding 1).
- Damage: combined with finding 1 this closes the loop on "the game
  assumes knowledge it never gave": the window in which knowledge is
  offered is three turns wide and never reopens.
- Confidence: HIGH.

### 10. FILED, confirmed live -- Rivals debut unintroduced (#1088)
- Confirmed mechanism: two of three rivals start visibility=KNOWN
  (rivals.gd:159-166), so the first month review prints "Rivals this
  month: <name> (<focus>) -- <drift>" (game_manager.gd:908-926) with zero
  prior introduction; the feed's "Hide rival intel" toggle is visible from
  turn 1 for a channel that has produced nothing. RIVALS_INTRODUCTION.md
  exists in docs/design but nothing in the scenes implements an intro.

### 11. FILED, confirmed live -- assorted, briefly
- #1031: authored placeholders paint as real state pre-boot ("58.5%",
  "$0", and the retired "Week 1 ... Day 1/5" time model, main.tscn:96-239).
- #1032: ENTER double-fires launch on config confirmation.
- #1035: non-ASCII survives in player-facing .tscn text (the middle-dot in
  the doom line main.tscn:269; guide bullets player_guide.tscn:125,154).
- #1037: stale "AP" vocabulary -- the scene still has ReserveAPButton /
  "Reserve Attention" naming mix; glossary missing (the "league baseline"
  and "Liability Ledger" definitions have nowhere to live).
- #1086: onboard window tooltip omits Attention cost, raw "money: 3000.0".
- #1089: Strategic unlock fanfare is bare text on black -- the game's
  biggest mid-run milestone beat.
- #1063: identity is only editable via Customize pregame; default path
  never asks until the post-death prompt.
- #1062 / #1064: leaderboard Duration column; Play Again edge cases.
- #1044: actions resolve instantly -> early game lacks rhythm; interacts
  with finding 6 (a hand of instant verbs reads as a menu, not a plan).

### Fixed since 07-20 (verified in code, worth knowing the class is closable)
- Empty-queue commit hard-error -> auto-pass (#733). Old #2 dead.
- Death attribution chain now rendered (EE-8). Old #8 dead.
- AP tooltip rewritten for Attention; balance-sourced tooltips. Old #6 dead.
- Debug Init button removed (#715); duplicate commit REMAINS (finding 3).
- Month review: movement-only stats, feed mirror, SPACE door (#1100).
  Old #9 largely dead (still a modal; A5 structural fix explicitly
  deferred, game_manager.gd:897-898).
- Leaderboard: real board, explanation header, visible fetch failure,
  consent + identity flow (#1048/#1126/#1133). Old section D largely dead.

---

## Part C -- what is GOOD (must survive an architecture pass)

1. The mode banner + phase label pair. "## PLAN - strategy - lay out the
   month, then COMMIT THE MONTH >" (screen_mode.gd:196) is the sentence
   that makes the loop self-teaching. Any refactor that keeps everything
   else but loses this line makes the game harder to learn.
2. The subtitle. "You can't win. You can only buy time." is the design
   philosophy in nine words, shown first. Findings 1-2 are about the OTHER
   surfaces failing to keep its promise -- the fix direction is to make
   everything agree with IT, not to soften it.
3. The cold-open STRUCTURE and the first-lever handoff seam. Show-once,
   pure presentation, hold-to-skip with auto-flip preference, ends on an
   active choice, and re-pointing the handoff is a one-string change
   (GameConfig.first_lever_action_id). Keep the machinery; fix the copy.
4. The commit path is unlosable. Auto-pass on empty queue, warnings on
   danger, tile-only-on-backend-accept (#821), rejection toast on the
   signal path. The turn can no longer hard-refuse to advance.
5. Balance-sourced tooltips (main_ui.gd:739-750) and the #1087/#1116
   number-format policy. Numbers on screen now share one format and cannot
   silently drift from mechanics. This is an anti-rot pattern that should
   be EXTENDED to help text (finding 1 is exactly the un-extended case).
6. Cost honesty at the point of choice: costs on submenu button faces, "
   (Free)" explicitly marked, event dialogs that stay open and say WHY a
   rejected choice failed (event_dialog.gd:65-83, 210-221), the NOT RANKED
   warning at scenario selection (pregame_setup.gd:99-117), the difficulty
   lock reflected with its reason (pregame_setup.gd:51-56).
7. The month review's information discipline: movement not levels, band
   not number for doom, mirrored to the feed so dismissal is free
   (game_manager.gd:799-826). The review is the best-written surface in
   the game right now.
8. Failure-is-visible on the leaderboard (#1126) and score-first ordering
   on death (game_over_screen.gd:66-124). The end-of-run pipeline is the
   most defensively engineered part of the UI; do not let a UI refactor
   re-order it.
9. The feed filters defaulting flavour-spam off, with the full stream
   recorded and recoverable (main_ui.gd:1435-1456) -- channel discipline
   already half-built.

---

## Part D -- what only a real fresh player can answer

Brief for the next observed playtest. Watch, do not coach; note timestamps.

1. THE GUIDE PATH. Do they open the Player Guide from the welcome overlay?
   If yes: what do they say the objective is afterwards? (Prediction from
   finding 1: "get doom to zero". If they say "survive as long as
   possible", the guide is being skimmed, and finding 1 drops a rank.)
2. THE TWO BUTTONS. First three commits: which of "COMMIT THE MONTH >" vs
   "Plan (Enter)" do they press, and can they explain the difference at
   turn 5? Do they ever notice the reserve-all side effect?
3. THE PULSE. During the cold-open handoff, watch their cursor: do they go
   to the pulsing scouting tile, the tile labeled "1" (Fundraising), or
   hover-scan the whole wall? Does the alpha pulse read as "glowing" (the
   hint's word) or as "broken/disabled"? I could not judge this from code.
4. ICON LITERACY. Ask at turn 2 (screen visible, no hovering): "what can
   you do in this game?" Count how many of the 15 verbs they can name.
   This measures whether icon-only tiles communicate at all.
5. WATCH MODE COMPREHENSION. After the first commit, do they understand
   the green screen is their plan executing? Do they try to click things?
   Does the ~5s playback feel like an event or a loading screen? (#1044's
   rhythm question, observed.)
6. THE FIRST MONTH REVIEW. Read-aloud test: what do they make of "Rivals
   this month: ... steady climb"? (#1088 severity calibration -- is it
   confusion, or does the deadpan land as intended worldbuilding?)
7. THE DEAD BUTTON. Note the first time any click produces no visible
   response, and what they conclude (finding 7's real-world frequency; I
   could only prove the mechanism, not the rate).
8. ATTENTION SPLIT COLLISION. Does any turn 1-6 action get refused for
   hour-type while the HUD shows Attention remaining? (Finding 5's
   frequency -- needs live balance, not code reading.)
9. TOOLTIP DISCOVERY. Do they EVER hover the top-bar readouts unprompted?
   The entire resource-explanation layer is tooltip-gated; if the answer
   is no, that layer effectively does not exist.
10. ESC BEHAVIOR. When they first want to "get out" of something, what do
    they press, and if they reach the pause menu, does "Accept Your Fate"
    read as dangerous? (Finding 8: does anyone hover long enough to see
    the tooltip before clicking?)
11. UNVERIFIABLE BY READING, for the record: actual layout/fold behavior
    at non-1080p resolutions; whether the backdrop/scrim/terminal styling
    reads as intentional or unfinished; audio mix on first launch; whether
    the office-floor sprite strip draws attention away from the feed;
    SmartScreen behavior of the current build (07-20 #1 -- outside the
    repo's scenes, not re-verified here).
