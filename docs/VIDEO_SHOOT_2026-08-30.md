# Video shoot -- 2 to 3 minutes, tonight

Prepared 2026-08-30 while Pip was at the conference, for a same-night shoot.
Two audiences, one cut: funders who asked, and YouTube generally.

Everything factual below was measured today, and every claim carries the command
that proves it. This repo has already sent funders a document with twelve false
claims in it (`docs/archive/2026-08-23-architecture-funders/`), and a video is
harder to correct than a page.

---

## 0. READ THIS FIRST -- the way this shoot fails

**Do not record from a source run without the pre-flight.**

Issue **#1023 is still open**: *"game does not initialise on launch -- full UI,
Phase: Not Started, no action buttons"*. The chrome renders perfectly, the office
and the cat and the doom readout all appear, and the game is simply not there.
It reads on camera as a game that does not work. CLAUDE.md describes the same
symptom under the stale class cache, which is what cost a playtest in front of a
first-time playtester on 2026-08-13.

> **CORRECTION, added the same afternoon.** The paragraph above was written
> before this issue was actually investigated, and it overstates the risk. Two
> checks, both cheap, both run today:
>
> 1. **#1023's own leading hypothesis is falsified.** It proposes that
>    `start_new_game()` was refused for want of `force=true`. That `force=true`
>    landed on **2026-07-27** in #983 (`d36cff9d`), and
>    `git merge-base --is-ancestor d36cff9d 3f408038` confirms it was already
>    present in the exact commit the failure was observed on. Every fresh-boot
>    path in `main_ui._boot_game()` passes it today -- resume, load and new game.
> 2. **The symptom is covered by a passing regression test.**
>    `godot/tests/unit/test_game_start_actionable.gd` (from #664) boots the REAL
>    `main.tscn` through `_boot_game` and asserts the game either presents an
>    initial event dialog or emits a non-empty action list with the buttons
>    enabled -- which is precisely "no action buttons". In today's gate:
>    `tests="1" failures="0" skipped="0"`.
>
> So #1023 is probably stale, and what remains is the third candidate its own
> author listed and said to rule out FIRST: an artefact of running from source
> with a warm `.godot`, which nobody has done in the month since.
>
> **What this means for tonight:** recording from source is very likely fine, as
> long as you run the pre-flight. The shipped build is still the better choice,
> but for the ordinary reason -- it is what a funder downloads -- rather than
> because the source path is dangerous.
>
> **The limit of this evidence:** the regression test drives the boot path
> in-engine under GUT. It is not a human clicking welcome -> config -> main on an
> exported binary. Strong evidence, not proof. The decisive test is still the one
> #1023 asks for and nobody has run: launch a built artifact and look.

Two ways to be safe, in order of preference:

**A. Record the SHIPPED v0.14.4 build.** No class cache is involved in an
exported build, so the whole failure class is gone. It is also literally what a
funder would download. Windows/Linux/macOS assets are on the v0.14.4 release.

    https://github.com/PipFoweraker/pdoom1/releases/tag/v0.14.4

**B. If you record from source**, run the pre-flight FIRST, every time:

    python tools/check_class_cache.py --repair
    godot --path godot

Never a bare `godot --path godot`. It takes about 30ms and it is the difference
between a demo and a diagnosis.

**Sanity check before you hit record, whichever you chose:** start a run and
confirm you can see action buttons in the left column and a phase that is not
"Not Started". If the left column is empty, stop and fix it -- do not narrate
around it.

**macOS caveat, if anyone asks on camera:** v0.14.4 restored the macOS *export*.
No macOS build from this pipeline has been launched on a Mac and watched to work
(#1071 is still open). Say "we ship a Mac build" only if you are willing to add
"and I have not personally verified it runs".

---

## 1. The beat sheet -- 2:30 target

Timings are a budget, not a metronome. The whole thing is roughly 380-420 spoken
words; at 2:30 you have room for about 400. Anything you cannot say in that
budget belongs in a second video.

| # | Time | On screen | What it is doing |
|---|---|---|---|
| 1 | 0:00-0:12 | Cold open / title | Premise in one sentence, before anything is explained |
| 2 | 0:12-0:30 | Main screen, office + doom meter | Orient the eye: this is a desk, that number is the stake |
| 3 | 0:30-1:05 | Queue actions `1`-`9`, `Enter` to commit | The core loop, and the only mechanic that must land |
| 4 | 1:05-1:25 | `V` to WATCH, the turn resolves | Consequence -- the game answering back |
| 5 | 1:25-1:45 | An event fires; `Q`/`W`/`E` to choose | It is a game about decisions under pressure |
| 6 | 1:45-2:05 | `T` Travel & Conferences, or `H` Hiring | Depth: there is a real org underneath |
| 7 | 2:05-2:20 | Game over screen, score | Runs end, and they end with a number |
| 8 | 2:20-2:30 | Leaderboard, then where to get it | The ask, or the link |

### Beat notes

**1. Cold open.** `godot/scenes/cold_open_sequence.tscn` exists and runs at
launch. Let it play; do not talk over the first four seconds. Your one sentence
should say what the game *is*, not what it is about -- "you run an AI safety lab
and try not to end the world" beats any amount of framing.

**2. Orient.** The doom meter is the thing a stranger's eye goes to. Name it once
and move on. The office cat (Mando) is on screen; it is charming and it is free,
do not explain it.

**3. The loop -- this is the beat that earns the video.** Number keys queue
actions into the action bar, `Z` undoes, `C` clears, `Enter` commits the plan and
reserves the rest of your Attention. Do it slowly enough that a viewer sees
cause and effect once. If only one beat survives the edit, it is this one.

**4. `V` flips PLAN to WATCH.** This is the reveal that it is a simulation and not
a menu. Worth the eight seconds.

**5. Events.** `Q` `W` `E` `R` `A` pick options. You have 35 core events; you do
not need a specific one, you need the viewer to see a choice with a cost.

**6. Depth, pick ONE.** `T` (Travel & Conferences) is the topical one and you are
literally at a conference tonight -- that is a good line if you want it. `H`
(Hiring) is the more legible one for a funder because it shows an org growing.
Do not open both; there is no time and it dilutes.

**7-8. End and ask.** A run ends with a score. The board is live and real -- see
the verified numbers below for exactly how real, and please use that number
rather than a vibe.

---

## 2. What NOT to put on camera

All open issues, all confirmed today. None of these is a secret; they are simply
places where the shipped build will contradict you or look broken.

| Avoid | Why | Issue |
|---|---|---|
| **Alt-tabbing / minimising mid-take** | minimising does not minimise; window left in a wrong state until re-maximised | #1085 |
| **The Local/Global leaderboard toggle** | silently un-presses itself on a fetch failure -- indistinguishable from a dead button, on camera | #1126 |
| **Lingering on the Attention header next to the Action Queue** | the two contradict each other in one frame, three widgets from three data sources | #1223 |
| **Close-ups of hotkey badges** | badges lose to modulate, and the "press 1-9" hint is wrong once there are 13 tiles | #1224 |
| **The Send Feedback / bug reporter (`N`)** | reports die on the player's disk; the website intake exists and the game never calls it | #1057 |
| **The Financing submenu** | inconsistent with Fundraising: no icons, costs not shown | #880 |
| **The Liability Ledger (`L`) as a hero shot** | layout is cramped and wrong; fine in passing, not as a feature | #601 |
| **Firing an employee** | the screen exists but the player never reaches it | #1226 |
| **Fanfare popups over events** | no dimming backdrop, so events leak under the popup | #603 |
| **Claiming a tutorial or new-player help** | `docs/PLAYERGUIDE.md` marks the interactive tutorial and first-time help triggers as **planned, not implemented** | -- |

**The last row is the important one.** It is the easiest sentence to say by
accident to a funder ("there's onboarding") and it is not true yet.

---

## 3. Verified claims sheet

Say these. Each one has a command that returns it, run today, 2026-08-30.

| Claim | Value | Proof |
|---|---|---|
| Version shipping | **0.14.4** | `cat version.txt` |
| Ladder epoch / featured seed | **L6**, `weekly-2026-w35` | `cat ladder_version.txt` |
| GDScript, excluding addons | **77,924 lines across 304 files** | `find godot -name '*.gd' -not -path '*/addons/*' -exec cat {} + \| wc -l` |
| Godot test functions written | **1,691** | `grep -rhoE '^\s*func test_' godot/tests --include=*.gd \| wc -l` |
| Godot tests that actually run in the fast gate | **1,518 across 147 files, 18s** | `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300` |
| Python automation tests | **482 passing** | `python -m pytest tests/ -q --ignore=tests/test_ascii_compliance.py` |
| Platforms with a shipped build | **Windows, Linux, macOS** | v0.14.4 release assets |
| Engine | **Godot 4.5.1, pure GDScript** | `godot/project.godot` |
| Content in the shipped data | **20 core actions, 35 core events, 3 researcher personas** | `godot/data/` |

### The leaderboard, stated precisely

The board is **live and has real submissions**. I queried it today:

    curl -s "https://api.pdoom1.com/score_api.php?action=list&seed=weekly-2026-w35&version=L6&limit=10"

It returns **one entry**: a player who is not Pip, score 21, level 21, a run of
285 seconds, submitted 2026-08-24 from v0.14.3.

So the true sentence is *"there is a live global leaderboard and real players are
submitting to it."* The false sentence is anything implying a community. One real
stranger's run is a genuinely good thing to have at this stage and it does not
need inflating.

### Things NOT to claim

- **No web build.** There is no web export preset and never has been. If a funder
  asks for "try it in the browser", the answer is no, not yet.
- **No mobile build.** No iOS or Android preset exists.
- **Not open-source.** The licence is **interim source-available**. `docs/copy/budget.json`
  constrains all copy against the word, deliberately.
- **Not finished.** Same file: no copy may frame this as a launch, a 1.0, or a
  completed thing.
- **No tutorial** (see the table above).

Those five are exactly the claims the archived funder document got wrong.

---

## 4. Free polish, if you have twenty spare minutes

**There is already a cinematic capture harness** and it is better than screen
recording for anything you want to look deliberate:

    python tools/capture_cinematic.py portal

`tools/capture_cinematic.py` records a scene through Godot's Movie Maker mode and
post-processes to a social-ready MP4 (h264/yuv420p/faststart) plus an optimised
GIF. It is deterministic: same seed and scene gives identical footage, so a beat
can be re-shot next patch and diffed frame-for-frame. Needs a GPU/display, so it
runs on your machine and not in CI. Read `tools/README_capture.md` first --
there is a known quirk where capture height comes out 2x on your dev box.

**What is registered today:** exactly one capture, `portal` -- 1080x1080, 8
seconds, 60fps. That is ready-made B-roll for a title card or a cutaway.

**Untested idea, offer not a promise:** the tool also accepts a raw scene path,
so `python tools/capture_cinematic.py res://scenes/cold_open_sequence.tscn` may
give you a clean cold open with no cursor and no window chrome. I could not test
it here -- no GPU capture on this laptop -- so treat it as a two-minute
experiment, not a plan.

**Audio:** there is music and sfx (8 files, `music_manager` autoload). The
conductor bug from v0.14.3 is fixed. Decide before you record whether you are
narrating over game audio or muting it; switching mid-take is the usual reason a
cut sounds amateur.

**`[` takes a screenshot** in-game, if you want stills for a thumbnail.

---

## 5. Suggested running order for tonight

1. Pick source or shipped build. Prefer shipped.
2. Run the sanity check in section 0. Confirm action buttons exist.
3. Start a run and play three or four turns WITHOUT recording, to find a state
   that looks alive. Turn one is a bad opening shot; a run with staff, some doom
   movement and a pending event is a good one.
4. Record beats 3 through 6 first, while you are warm and the state is good.
5. Record the cold open and the closing ask last, when you know what you actually
   said in the middle.
6. Keep every take. `python tools/ingest_recordings.py` pulls today's OBS output
   into the repo working area, copying rather than moving.

---

## Open question only you can answer

**What is the ask at the end?** The Manifund campaign closes **2026-09-09**, nine
days out, $14,500 minimum and $48,000 goal. If this video is partly for the
funders who have just expressed interest, the close should probably point there
rather than at a generic "wishlist it". `docs/copy/budget.json` is the money SSOT
and it carries the constraints that copy must respect.
