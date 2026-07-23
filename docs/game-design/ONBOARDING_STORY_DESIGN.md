# Onboarding & Story System -- Structural Design

Implements GitHub issue #801. Status: DESIGN (structure only).

> SCOPE GUARD: This document designs the CONTAINER, not the CONTENTS. Every
> place narrative/story text belongs is marked `[STORY COPY -- WORKSHOP WITH
> PIP]`. Pip is workshopping the actual copy separately. Do NOT fill prose in
> here; if you are implementing, wire the plumbing and leave the placeholders
> as data-driven slots so the copy can be dropped in later without code edits.

This is a presentation/UX system. See the Non-score guarantee section: it
touches no game logic, scoring, or seed, so it is safe for the hotpatch lane.

---

## Core purpose: LEVER legibility (action -> effect)

Stated FIRST, above generic orientation, because a later playtest refinement
narrowed the diagnosis. The player already understands the GOAL: he knows he
must drive doom / risk toward 0%. What he does NOT know is which LEVERS move
that needle -- which actions actually change doom, in what direction, and roughly
how much. The onboarding's primary job is therefore to teach the mapping
`action -> effect`, NOT to re-explain the objective.

Concretely: every direction the onboarding gives must NAME a specific lever AND
its effect -- e.g. "hire a researcher -> lowers doom" -- never a generic "do
something" or "you can take actions here." This purpose is the lens for
Components 2 and 3 below: they are lever-teaching devices first, orientation
second.

---

## The two gaps (from #801)

The first external playtester said: "a lot of information happening immediately
and not a lot of direction... trial and error just to find out what I'm meant
to do. I love the concept though just hard to navigate."

That single complaint is actually TWO distinct, separable failures:

1. **Cold-open overload / no narrative context.** The player is dropped into a
   dense strategy UI with no framing of who they are, what the lab is, or why
   doom matters. There is no story on-ramp -- the fiction that makes the numbers
   legible is missing. This is a ONE-TIME, session-start problem.

2. **No LEVER legibility.** Even once framed -- and even KNOWING the goal is
   "doom to 0%" -- the player does not know which action moves that needle. Which
   button lowers doom, and by how much? This is the "trial and error just to
   find out what I'm meant to do" phrase: not confusion about the objective, but
   about the `action -> effect` mapping (see Core purpose above). It is a
   PER-TURN (specifically first-turn) problem.

Why the intro alone does NOT fix gap 2: a narrative cold-open answers "what is
this world," but it does not answer "which lever lowers doom right now." A
player can read a beautiful crawl and STILL stare at the plan screen unsure
which button moves the needle.
Issue #720 already shipped a first-launch welcome overlay (-> Player Guide,
`godot/scripts/ui/player_guide.gd`) PLUS a `getting_started_hint` shown on turns
< 3 -- and the tester was still lost. Conclusion: a dismissible popup covers gap
1 weakly and a generic always-the-same hint covers gap 2 not at all. The two
gaps need two targeted mechanisms, not one bigger popup.

---

## Design: reuse what exists

Anti-rot rule: build ON #720's machinery. Do not invent a parallel
"has the player seen the intro" flag when the repo already has a proven
show-once-per-version gate.

The existing, proven gate (in `godot/autoload/game_config.gd`):

- `var games_played: int` (line ~43) -- persisted counter; `false`-cost
  first-launch detector is simply `games_played == 0`. Incremented by
  `increment_games_played()` (line ~313), called from
  `config_confirmation.gd` (`GameConfig.increment_games_played()`) at game
  start.
- `var last_seen_version: String` (line ~52) with:
  - `const CURRENT_VERSION` (line ~61, stamped from `version.txt` by
    `tools/sync_version.py`).
  - `has_unseen_patch_notes() -> bool` (line ~369): true if
    `last_seen_version.is_empty()` OR `last_seen_version != CURRENT_VERSION`.
  - `mark_patch_notes_seen() -> void` (line ~375): sets
    `last_seen_version = CURRENT_VERSION` and `save_config()`.

The proven consumer (in `godot/scripts/ui/whats_new_modal.gd` +
`godot/scripts/ui/welcome_screen.gd`):

- `welcome_screen.gd::_setup_whats_new_modal()` (line ~184) instantiates the
  modal and, IF `GameConfig.has_unseen_patch_notes()`, shows it once and marks
  it seen -- the exact "show once per version, re-show on version bump" pattern
  we want.
- `whats_new_modal.gd::show_modal(mark_as_seen: bool = true)` (line ~68) shows
  the modal and calls `GameConfig.mark_patch_notes_seen()` when
  `mark_as_seen`. Its `_input()` (line ~33) closes on ESC / ENTER / SPACE and
  calls `get_viewport().set_input_as_handled()` -- the skip/dismiss idiom to
  copy.

### The onboarding gate

Add a SEPARATE persisted marker so the intro's show-once is independent of
patch notes (a player may have seen v0.11 notes but never the intro, or we may
want to force a re-intro on a major narrative revision without re-showing patch
notes). Mirror the existing pattern exactly -- new field + two helpers in
`game_config.gd`, saved/loaded alongside the others in `save_config()` /
`load_config()`:

```
# game_config.gd  (new, mirrors last_seen_version)
var last_seen_intro_version: String = ""   # "" = never seen the cold-open

func should_show_intro() -> bool:
    # First launch OR intro re-versioned since last seen.
    return games_played == 0 or last_seen_intro_version != INTRO_VERSION

func mark_intro_seen() -> void:
    last_seen_intro_version = INTRO_VERSION
    save_config()
```

`INTRO_VERSION` is a small independent const (e.g. `"1"`) bumped ONLY when the
cold-open content changes enough to warrant a re-show -- decoupled from
`CURRENT_VERSION` so ordinary patch releases do not re-trigger the intro. Persist
`last_seen_intro_version` in the `"game"` section of the ConfigFile next to
`last_seen_version` (same two lines in `save_config`/`load_config`).

Do not reuse `mark_patch_notes_seen()` for this -- keep the two show-once tracks
orthogonal.

---

## Component 1 -- Narrative cold-open (Civ II / old-RPG style)

Mechanism only. A short sequence of BEATS played before the player reaches the
main game UI. Each beat = one full-bleed art frame + a few lines of text that
fade in, hold, and fade out. Fully skippable. Shown once via `should_show_intro()`.

### Sequence data shape

Data-driven so copy drops in without code changes. Ship as
`res://data/intro_sequence.json` (mirrors how `whats_new_modal.gd` loads
`res://data/patch_notes.json` via `FileAccess` + `JSON.new().parse()`):

```
{
  "intro_version": "1",
  "beats": [
    {
      "art_ref": "res://assets/<hero_or_beat_art>.webp",
      "text": "[STORY COPY -- WORKSHOP WITH PIP]",
      "duration": 4.0
    },
    {
      "art_ref": "res://assets/<beat_2_art>.webp",
      "text": "[STORY COPY -- WORKSHOP WITH PIP]",
      "duration": 4.0
    }
  ]
}
```

Per-beat fields:

- `art_ref` (String): `res://` path to an existing texture. Reuse art already in
  the repo -- e.g. the hero background at
  `godot/assets/dump_october_31_2025/hero-bg-2400w.webp` (relocate into a
  packed `assets/` path first; the `dump_*` folder is a staging area). No new art
  is REQUIRED to ship the structure; placeholder art is fine.
- `text` (String): a beat's line(s). ALWAYS a placeholder here.
- `duration` (float, seconds): auto-advance hold time. Skippable overrides it.

Optional later fields (leave unused for v1): `text_align`, `sfx_ref`,
`music_cue`.

### Fade approach in Godot

Standard `Tween` on `modulate:a` of the text `Label`/`RichTextLabel` (and
optionally the art `TextureRect`). Per beat:

```
# pseudocode inside the cold-open controller
func _play_beat(beat: Dictionary) -> void:
    art.texture = load(beat.art_ref)
    label.text = beat.text          # placeholder copy from JSON
    label.modulate.a = 0.0
    var tw := create_tween()
    tw.tween_property(label, "modulate:a", 1.0, 0.6)          # fade in
    tw.tween_interval(beat.duration)                          # hold
    tw.tween_property(label, "modulate:a", 0.0, 0.6)          # fade out
    tw.finished.connect(_advance_beat)
```

Skip handling copies `whats_new_modal.gd::_input()`: on ESC or click (or
ENTER/SPACE), kill the running tween, and either advance to the next beat (single
tap = skip THIS beat) or exit the whole sequence (hold ESC / a dedicated Skip
button = skip ALL). Recommend: click/ENTER = next beat, ESC = skip entire intro.
Always `get_viewport().set_input_as_handled()` so the tap does not leak into the
game UI underneath.

### Where it hooks into scene flow

MUST route through the `SceneTransition` autoload -- never
`change_scene_to_file()` directly (the v0.11.0 leaderboard segfault rule; see
CLAUDE.md and `docs/LEADERBOARD_CRASH_DIAGNOSIS.md`). The whole codebase already
uses `SceneTransition.go_to("res://scenes/X.tscn")` (e.g. `welcome_screen.gd`,
`config_confirmation.gd`).

Two viable placements:

- **(Recommended) Its own scene `res://scenes/intro_sequence.tscn`**, inserted
  between config confirmation and `main.tscn`. Today
  `config_confirmation.gd` does `GameConfig.increment_games_played()` then
  `SceneTransition.go_to("res://scenes/main.tscn")`. Change to: if
  `GameConfig.should_show_intro()`, `go_to("res://scenes/intro_sequence.tscn")`
  instead; the intro scene, on finish or skip, calls `mark_intro_seen()` then
  `SceneTransition.go_to("res://scenes/main.tscn")`. Note the ordering subtlety:
  `increment_games_played()` currently runs BEFORE we would read
  `games_played == 0`. Read `should_show_intro()` (or capture the first-launch
  boolean) BEFORE the increment, or gate purely on `last_seen_intro_version`
  which is immune to the ordering issue. Prefer the `last_seen_intro_version`
  gate for exactly this reason.
- **(Alternative) An overlay CanvasLayer on `main.tscn`** shown on `_ready`
  before enabling input. Cheaper wiring but muddies `main_ui.gd` (already a
  3k-line monolith); the separate-scene option keeps the monolith clean.

Recommendation: separate scene, gated on `last_seen_intro_version`, transition
via `SceneTransition`.

---

## Component 2 -- First-turn LEVER pointer (fixes the trial-and-error)

This is the part that teaches `action -> effect` (Core purpose). It does NOT
restate the goal (the player already knows: doom to 0%); it names ONE lever and
its effect and points at the button that pulls it. The current mechanism is
`getting_started_hint`:

- `main_ui.gd:31` -- `@onready var getting_started_hint =
  plan_screen.getting_started_hint`.
- `main_ui.gd:866-867` -- visibility gate:
  `getting_started_hint.visible = state.get("turn", 0) < 3`.
- `plan_screen.gd:9` -- `@onready var getting_started_hint: Label =
  $GettingStartedHint` (a plain `Label` in the plan screen).

So today it is a static `Label` that is simply shown/hidden by turn number. It
does not point at anything.

### Options and tradeoffs

**(a) Upgrade `getting_started_hint` from generic to a LEVER pointer.**
Change the hint text (or make it data-driven per turn/state) from a generic
"you can take actions here" to a specific line that names a lever AND its
effect: "[STORY COPY -- WORKSHOP WITH PIP]" carrying the shape "hire a
researcher -> lowers doom." The point is the arrow (`action -> effect`), not
just "do X."
Cost: trivial -- it is already a `Label` with a visibility gate; only the text
source changes. Risk: text-only, easy to overlook in a dense screen.

**(b) Highlight / pulse the button for that named lever.**
Add a visual pull to the SAME action the hint names (not just "a first action"):
a looping `Tween` on `modulate` or a glow/outline on that button, cleared once
the player takes any action (or after turn N). This binds the WORD ("hire a
researcher -> lowers doom") to the WHERE (the glowing hire button), so the
player learns the lever, not just clicks it. Cost: low -- one tween on an
existing button, plus a "which lever are we teaching" lookup (a static
first-lever id for v1; no logic change). Risk: needs a rule for which button;
keep it a constant, and keep it the SAME lever the hint names.

**(c) A guided first turn (forced tutorial).**
Gate the UI so only the intended first action is enabled, walk the player
through a scripted sequence. Cost: HIGH -- intrusive UI gating, state machine,
easy to desync with real game logic, and it removes agency. Risk: exactly the
"leash" the tester did not ask for.

### Recommendation

Do **(a) + (b): a lightweight nudge** -- a concrete pointer line PLUS a pulse on
the suggested first-action button -- and NOT (c).

Why: the tester said "trial and error just to find out what I'm meant to do...
just hard to navigate," and "I love the concept." They needed a POINTER to a
LEVER, not a LEASH. They understood the goal and the genre; they lacked the
`action -> effect` mapping. A nudge (a) names the lever and its effect, (b)
glows the button that pulls it, both are cheap, both are pure presentation, and
both preserve the player's agency to ignore the suggestion and explore. A forced
tutorial (c) is expensive, brittle, and risks smothering the "I love the
concept" spark that survived even the bad first session.

Implementation note: (a) and (b) live entirely in the plan screen /
`main_ui.gd` visibility+tween layer already used by the `turn < 3` gate. Clear
the pulse when the player takes their first action or crosses the same turn
threshold that already hides the hint.

---

## Component 3 (unifying idea) -- Advisor / narrator persona

A Civ II-style advisor voice is the device that can deliver BOTH the cold-open
context (Component 1) AND the first-turn lever pointer (Component 2) through ONE
diegetic channel, so the game speaks to the player in a consistent voice instead
of via disconnected popups and labels.

CONFIRMED BY THE PLAYTESTER: the advisor + button-glow device is explicitly
liked -- the intended shape is an advisor line like "[STORY COPY -- WORKSHOP
WITH PIP]" carrying "Looks like doom is rising. Better hire a researcher..."
delivered WHILE the hire button glows (Component 2b). That co-timing -- advisor
names the lever and its effect, the button for that lever pulses in sync -- is
the core loved interaction, and it is exactly the `action -> effect` teaching
from Core purpose made diegetic. Treat this pairing as the design's spine, not
an optional flourish.

Design it as a REUSABLE text-delivery component, not a one-off:

- **Portrait slot**: a `TextureRect` (advisor face / persona art) + a name
  `Label`. `art_ref` is data-driven like the intro beats; a placeholder portrait
  is fine to ship.
- **Line queue**: a FIFO of lines the advisor speaks, each rendered with the
  same fade-in / hold / fade-out `Tween` on `modulate:a` as Component 1. Public
  API shape:

```
# advisor_panel.gd (reusable component -- pseudocode)
func set_persona(portrait_ref: String, name: String) -> void: ...
func queue_line(text: String) -> void: ...        # text = placeholder
func queue_lines(lines: Array) -> void: ...
func skip() -> void: ...                            # ESC/click, per Component 1
signal line_finished(index: int)
signal queue_emptied()
```

- The cold-open (Component 1) becomes: `set_persona(...)` then
  `queue_lines(beats.map(text))` -- the beat sequence IS an advisor monologue.
- The first-turn lever pointer (Component 2) becomes: on the first turn, the
  same advisor `queue_line("[STORY COPY -- WORKSHOP WITH PIP]")` (a lever+effect
  line, e.g. the "doom is rising -> hire a researcher" shape), and the button
  pulse for that named lever fires WHEN that line shows (drive the glow off the
  `line_finished` / line-shown signal so word and glow are co-timed).
- Later milestone beats (below) reuse the SAME component: same portrait slot,
  same queue, same skip idiom.

All spoken lines are `[STORY COPY -- WORKSHOP WITH PIP]`. This section designs
the mouth, not the words.

Reuse boundary: keep `advisor_panel` UI-only and stateless about game rules --
callers decide WHEN to queue lines and WHAT to say; the component only renders
and fades. This keeps it safe for the hotpatch lane and prevents it from
accreting game logic.

---

## Later: milestone story beats

A trigger-driven beat framework that fires short narrative moments at gameplay
milestones (e.g. "first paper published", "doom crosses 50%", "first hire",
"first rival overtakes you"). These reuse the Component 3 advisor queue for
delivery. Dual purpose: each beat is also short-form MARKETING content
(screenshot / clip of an in-fiction moment).

Design the TRIGGER HOOK shape only (not the copy, not the trigger logic wiring
into every system yet):

```
# res://data/story_beats.json  (data-driven; copy is placeholders)
{
  "beats": [
    {
      "id": "first_paper",
      "trigger": { "event": "paper_published", "count_eq": 1 },
      "lines": ["[STORY COPY -- WORKSHOP WITH PIP]"],
      "once": true
    },
    {
      "id": "doom_50",
      "trigger": { "event": "doom_crossed", "threshold": 50, "dir": "up" },
      "lines": ["[STORY COPY -- WORKSHOP WITH PIP]"],
      "once": true
    }
  ]
}
```

Hook mechanism: a lightweight listener (an autoload or a node subscribing to the
existing turn/event pipeline -- e.g. `event_service` / the turn manager) checks
fired game events against `trigger` predicates each turn. On a match with
`once: true` and not-yet-fired, it calls the advisor component
`queue_lines(beat.lines)` and records the beat id as fired (persist per-run, not
per-install -- these should replay in a new game). The framework only READS game
events; it never mutates them (see Non-score guarantee).

Keep the predicate vocabulary small for v1 (`event` name + one of
`count_eq` / `threshold`+`dir`). Do not build a general rules engine.

---

## Non-score guarantee

All of the above is presentation / UX ONLY:

- No change to game logic, action resolution, economy, or the doom system.
- No change to scoring or the leaderboard score computation.
- No change to the seed or any RNG draw -- the intro, hints, advisor, and beats
  READ state and events; they never mutate them or consume randomness.

Therefore this does NOT fork the leaderboard ladder / board-key. It is safe to
ship in the hotpatch lane. Guard this invariant in review: if any part of this
system ever writes to game state, the RNG, or the score, it has left its lane.

---

## Open decisions for Pip

From #801, two calls -- both now effectively RESOLVED by the playtester
refinement, but recorded here for Pip to ratify:

1. **Narrator persona vs plain crawl** for the cold-open (Component 1).
   - Recommendation: **persona** (Component 3). CONFIRMED loved by the tester
     (advisor line + synced button glow). One diegetic voice unifies the context
     AND the first-turn lever pointer AND later milestone beats, and the advisor
     component pays for itself across all three uses. A plain crawl is cheaper
     for v1 but throws away the reuse, the marketing-clip value, and the exact
     interaction the tester liked.

2. **Guided first turn vs stronger static hint** for direction (Component 2).
   - Recommendation: **lightweight lever nudge** (a lever+effect line -- "hire a
     researcher -> lowers doom" -- plus a synced glow on that button), NOT a
     guided/forced first turn. The tester needed a pointer to a LEVER, not a
     leash; the nudge is cheap, preserves agency, and lives in the existing
     `getting_started_hint` visibility layer.

Both recommendations converge on the confirmed spine: an advisor persona that
speaks the cold-open and then delivers a first-turn `action -> effect` line
while the named lever's button glows -- the minimum-parts design that closes
both gaps, teaches lever legibility, and stays pure presentation (hotpatch
lane). Remaining for Pip: the actual copy, the chosen first lever to teach, and
the advisor's persona/portrait.
