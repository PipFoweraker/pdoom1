# Player-Facing Documentation Audit -- 2026-07-16 (ship hygiene)

**Scope:** every doc a player / tester / store-page reader would hit. Internal dev docs, ADRs,
and backlog are out of scope.
**Two verdict types:**

- **FIXED** -- factual error / staleness, corrected directly in this PR (safe, unambiguous).
- **TEARDOWN** -- voice / pitch / framing. **Not** rewritten here. Pip writes his own voice; each
  gets a skeleton below with section headers + bullet prompts for him to fill.

**Ground truth used** (so no new inaccuracies were introduced): `docs/ARCHITECTURE.md` (the merged
L1 dev map), `docs/adr/0002-win-condition-survival-spine.md`, `godot/autoload/game_config.gd`
(`CURRENT_VERSION = "0.11.0"`), `godot/project.godot`.

## The one truth every player doc must get right (per code + ADR-0002 / DQ-1)

**The game is unwinnable, by design.** `game_state.gd check_win_lose()` (lines 518-523) sets
`game_over = true; victory = false` on `doom >= 100` **or** `reputation <= 0`, and **`victory` is
never set `true` anywhere in the codebase** -- there is no `doom <= 0` branch. This is exactly what
ADR-0002 / DQ-1 (victory-removal, RESOLVED) and `DESIGN_PHILOSOPHY.md` ("On losing") intend.

> **You cannot win -- you can only buy time.** Survival duration is the score. Doom trends upward by
> design, so **every run ends in loss**. A "good" result is surviving *longer* -- beating your own
> previous baseline -- **never** driving doom to 0. There is **no turn limit** and **no victory
> condition** of any kind.

Any doc that advertises "**Survive 100 turns with P(Doom) at 0%**", a "victory", or a doom->0 win is
factually wrong.

> WARNING **Correction (supersedes the first version of this audit).** An earlier draft of these fixes
> described doom->0 as a "rare apex victory," following stale prose in the ADR-0002 *document*. The
> shipping **code has no victory path** (verified above); that framing was wrong and has been **purged
> from every fix**. Note the ADR-0002 doc text is itself stale on this point -- it claims a `doom <= 0`
> code victory that does not exist -- and should be reconciled to DQ-1. **Flagged, not edited** (ADRs
> are out of player-facing scope).

Other current-state facts a player doc must not contradict (from `ARCHITECTURE.md`):

- **Pure Godot 4 / GDScript.** The Python/Pygame prototype is fully retired -- no Python runtime ships.
- **Month-based planning, day-tick resolution** (ADR-0009): the turn is a *month* decision cadence;
  the sim still resolves day by day. "The turn is a week / here's your 3 Action Points this turn" is
  the retired pygame framing.
- **Attention** is the founder currency (per month; evaporating reserve). WARNING **Caveat:** the legacy
  **Action Points (AP)** pool *still co-exists in the shipped build* -- the AP->Attention migration
  (L2, #613) is **not built yet**. So docs that say "AP" are not strictly *wrong today*; they are
  **transitional** and should be updated when #613 lands. This is why AP wording was **flagged, not
  rewritten** below.
- **Doom is readable, not random:** nine named streams, attributable death ("which stream killed you").
- **Ledger / cost-of-debt** is the mortality engine under the hood -- but it is **not player-facing
  yet** (no ledger UI/action; ARCHITECTURE Section Liability Ledger, blocker BL-1). Don't pitch it as a
  visible feature.

---

## Verdict table

| Doc | Passage | Verdict | Note |
|---|---|---|---|
| `README.md` | "Survive 100 turns with P(Doom) at 0%" (gameplay bullet) | **FIXED** | Replaced with "you can't win, only buy time; score = how long you last; every run ends in loss" + ADR-0002 link. **The most embarrassing line on the old README.** |
| `README.md` | "Your choices determine whether P(Doom) reaches 0% or humanity faces extinction" (About para) | **FIXED** | Same win-lie in prose. Purged to buy-time framing (minimal factual correction; full pitch rewrite still Pip's). |
| `README.md` | footer `[Contributors](docs/CONTRIBUTORS.md)` | **FIXED** | Dead link (file absent). Repointed to existing `docs/CONTRIBUTOR_REWARDS.md`. |
| `README.md` | "About the Game" para + "Gameplay:" bullet list | **TEARDOWN** | LLM feature-list voice; highlights trait names (`team_player`, `leak_prone`) over actual play. Skeleton below. |
| `README.md` | screenshot `pdoom_screenshot_20250918_104357.png` | **TEARDOWN** | Pip flagged the image; it predates the month-engine UI. Needs a fresh capture (asset task, not a text fix). |
| `docs/STEAM_INTEGRATION_ROADMAP.md` | "Current Version: v0.10.5" (x2, header + status table) | **FIXED** | -> v0.11.0. |
| `docs/STEAM_INTEGRATION_ROADMAP.md` | store copy: short-description "...whether P(Doom) reaches 0% or humanity faces extinction" (L380) + bullet "Surviving 100 turns with P(Doom) at 0%" (L389) | **FIXED** | Both purged to "you can't win, only buy time" framing. |
| `docs/STEAM_INTEGRATION_ROADMAP.md` | achievement table (L280-289): "First Victory -- Win your first game", "Zero Doom -- Reduce P(Doom) to 0%", "Safety Champion -- Win with 0% doom", "Speedrunner -- Win in <50 turns" | **TEARDOWN (flag -- hard blocker for store)** | **Win-based achievements in an unwinnable game.** Must be redesigned around survival milestones (turns held / baseline beats) by the achievements lane -- NOT rewritten here (speculative internal mapping that also references deleted `legacy/.../achievements_endgame.py`). Do not ship these to Steam as-is. |
| `docs/STEAM_INTEGRATION_ROADMAP.md` | "feature-complete", "Achievement System -- Implemented" | **TEARDOWN** | Overclaim: achievements are an observer-only skeleton (L8); ledger/finance not player-facing. Store copy block needs Pip's voice. |
| `docs/PLAYERGUIDE.md` | "The Python/Pygame version is for development only" | **HANDED TO #719** | Factually stale (pure GDScript now), but PLAYERGUIDE.md is owned by the #719 truth-pass lane -- not carried in this PR to avoid double-editing. Flagged for that lane. |
| `docs/PLAYERGUIDE.md` | dead `[CONFIG_SYSTEM.md]` link | **HANDED TO #719** | Dead link (file absent); fix belongs to the #719 PLAYERGUIDE lane, not this PR. |
| `docs/PLAYERGUIDE.md` | **entire mechanics body** (Action Points as core, weekly cash, "Turns 1-13", `[EMOJI]`/`[TARGET]` tokens, no month engine / Attention / doom-streams / finance) | **TEARDOWN** | This doc describes the *pygame-era game*. Surgical fixes would falsely signal the rest is current. Full rewrite. Skeleton below. |
| `docs/DEMO_GUIDE.md` | whole file: `python main.py`, `src/services`, "built in Python", hardcoded path `c:\Users\gday\...`, v0.2.5, `[DEMO]/[AWESOME]` tokens | **TEARDOWN** | Describes a game that no longer exists. **Recommend archive or ground-up rewrite** -- do not ship as-is. |
| `docs/QUICK_REFERENCE.md` | "P(Doom) v0.4.1" | **FIXED** | -> v0.11.0. |
| `docs/QUICK_REFERENCE.md` | pervasive `[EMOJI]/[LIGHTNING]/[TARGET]` tokens; "Party-ready demonstrations", "Spectacular celebration"; AP references | **TEARDOWN** | Broken emoji rendering + party-demo boilerplate; AP flagged (see caveat). Rewrite. |
| `docs/PRIVACY.md` | "Current Status (v0.2.5)"; `[EMOJI][EMOJI]` bullet markers | **TEARDOWN (flag)** | Version + broken tokens. **Not auto-fixed:** privacy *content* accuracy needs Pip/eng to confirm what actually changed since v0.2.5 before relabeling. |
| `docs/README.md` (docs index) | `CLIPBOARD Summaries` / `MICROSCOPE Analysis` sections -- 8 dead links + literal emoji-replacement text | **FIXED** | Removed the two all-dead sections and the dead `../DEV_TOOLS_PORTING_ANALYSIS.md` link. |
| `CONTRIBUTING.md` | `[CONTRIBUTORS.md](docs/CONTRIBUTORS.md)` | **FIXED** | Dead link removed (kept the live Contributor Rewards line). |
| `CONTRIBUTING.md` | bug-reporter keybind: `~` (L88) vs `\` (L213) vs CONTROLS.md `F8`/`]`/`\` | **TEARDOWN (flag)** | Cross-doc keybind mismatch; needs a ground-truth pass against the actual input map before editing. |
| `docs/CONTROLS.md` | "Reserve AP" (L17, L116) | **TEARDOWN (flag)** | Should become "Attention" *after* #613; AP still live today, so left as-is deliberately. Otherwise current (v0.11.0 history, correct framing). |
| `docs/SCENARIOS.md` | `action_points` starting-resource schema | **no change** | Accurate today (AP still a real resource); "lose at 100%" framing is correct. |
| `docs/KEYBOARD_REFERENCE.md` | -- | **no change** | Clean. |
| `docs/CONTRIBUTOR_REWARDS.md` | closing "more engaging, polished, and meaningful" line | **TEARDOWN (low pri)** | Minor boilerplate; otherwise fine. |
| `CHANGELOG.md` | `[Unreleased]` stops at #500/#527-era | **TEARDOWN (flag)** | Omits the entire L1 wave (month engine #636, nine-stream doom #643, finance #641, calibration #638). Release-notes job for Pip -- not fabricated here. Also title says "Bureaucracy Strategy Game" vs README's "AI Safety Strategy Game". |

**Factual fixes applied: 10.** All are safe to merge. (Two PLAYERGUIDE.md fixes originally counted here were **handed to the #719 truth-pass lane** during reconciliation -- PLAYERGUIDE.md is that lane's file, not this PR's.) Everything marked TEARDOWN / flag is Pip's worklist.

## Findings for other lanes (NOT fixed here -- not player-facing docs / game code)

- **In-game HUD center string** `"Win: P(Doom) = 0% or beat baseline | Lose: P(Doom) = 100%"` -- the
  **same stale win-lie, live in the running game.** There is no win; it must read as survival-only
  (e.g. "Lose: P(Doom) = 100% -- no win; last as long as you can"). Owned by the HUD/code lane, not
  this docs PR.
- **ADR-0002 document prose is itself stale** -- it describes a `doom <= 0` code victory and a "rare
  apex victory" that the shipping code does not implement (verified: `check_win_lose` never sets
  `victory = true`). Reconcile the ADR text to DQ-1 (victory-removal, RESOLVED). ADR, not player-facing.

---

## Docs needing Pip's voice rewrite (worklist, priority order)

1. **`README.md`** -- the pitch (below). Highest visibility.
2. **`docs/PLAYERGUIDE.md`** -- full rewrite against the month engine (below).
3. **`docs/DEMO_GUIDE.md`** -- archive or rewrite; currently describes the pygame build.
4. **`docs/QUICK_REFERENCE.md`** -- de-token + de-boilerplate + AP->Attention (post-#613).
5. **`docs/STEAM_INTEGRATION_ROADMAP.md`** -- the store-copy block + drop the overclaims.
6. **`docs/PRIVACY.md`** -- version + tokens, once content delta confirmed.
7. **`CHANGELOG.md`** -- add the L1 wave entries.

---

# VOICE TEARDOWNS (skeletons for Pip -- not filled)

## README.md

**Off-voice passage 1 -- the logline + About para:**
> "Manage an AI safety lab racing to solve alignment before it's too late." ... "Your choices determine
> whether P(Doom) reaches 0% or humanity faces extinction."

Why it misses: it sells a **binary win/lose to 0%** -- but **there is no win**. It hides the actual
experience -- you're **buying time** you can *read* running out. "racing to solve alignment"
is generic AI-safety-flyer language, not what the player does minute to minute (scout, plan a month,
watch a doom stream climb, take a loan you'll regret).

**Off-voice passage 2 -- the "Gameplay:" bullet list:**
> "Balance researcher traits (team_player, media_savvy, leak_prone) for optimal productivity" ...
> "Manage teams of up to 8 researchers per manager"

Why it misses: this is the **LLM-highlights-dev-features** problem Pip named -- internal trait
identifiers and org-chart limits, not gameplay experience. A player doesn't care about `leak_prone`
as a headline; they care that a leak can spike doom.

**What the pitch should actually convey** (the real hooks, for Pip to voice):
- You **can't win, you buy time** -- and the game is honest about it: the score is how long you held on.
- The **month loop**: plan a month, watch it play out day by day, react when something forces a decision.
- **Doom you can read**: it's not a random number; named pressures push it and the game tells you which
  one is about to kill you (lead-time, not surprise).
- **The debt tension**: every mitigation is borrowed against the future (note: engine-real, but *not a
  visible UI yet* -- pitch the *feeling*, not a feature screen).
- **Scouting / situational awareness** early: spending buys sight.

**Skeleton to fill (Pip's voice):**
```
# P(Doom): <one-line hook -- what the player feels, not "manage a lab">

<2-3 sentence About: you run the lab; you can't win, you hold the line; the game tells you how you're losing>

## What a run feels like
- <the month loop, in your words>
- <reading doom / the moment you realise which stream is killing you>
- <the debt / desperation-lever tension>
- <scouting rivals early>

## Download & Play
<keep as-is -- factually current>
```
**Also:** replace `screenshots/pdoom_screenshot_20250918_104357.png` with a current month-engine capture.

## docs/PLAYERGUIDE.md

This is not a voice problem so much as a **wrong-game** problem: the entire body documents the retired
pygame build. Representative stale passages:
> "Base AP: You start with 3 Action Points per turn" - "First Employee: $600/week" -
> "Late Game (Turns 10-13)" - "80's techno-green context window" - pervasive `[EMOJI]` / `[TARGET]` tokens -
> "Your score is how many turns you survived" (this instinct is **correct and complete** -- survival *is*
> the game; do not add any win/victory to it).
> Also purge L826 "Every turn you survive is a victory" of the word "victory" to avoid any win read
> (the sentiment -- survival is the point -- is right).

It contradicts `ARCHITECTURE.md` on: currency (AP-as-core vs **Attention**), turn grain (week vs
**month plan / day tick**), and omits nine-stream doom, the ledger, finance offers, death attribution.

**Skeleton to fill (rewrite against the current engine):**
```
# P(Doom) -- Player Guide

## The goal (read this first)
<you can't win, only buy time; survival duration is the score; every run ends in loss; a good run beats your own baseline; NO doom->0 victory -- ADR-0002 / DQ-1>

## The month loop
<Plan phase: spend Attention on strategic actions with durations>
<Day-tick playback: the month plays out; some events pause you for a decision (window)>
<Month review -> next plan>
(Note: AP still appears in the build until #613 -- decide how much to explain the dual currency.)

## Reading doom
<nine named streams; how to see which one is rising; lead-time before death>

## Money, debt, and offers
<funding offers; the cost-of-debt tension; note ledger UI isn't surfaced yet>

## Rivals & scouting
<situational awareness; spending buys sight>

## Papers & conferences
<attendance + yields; keep it honest about what's built -- DQ-16>

## Game over & scoring
<turns survived + doom-integral tiebreak; concede gracefully>
```

## docs/DEMO_GUIDE.md

Every command and claim is pygame-era (`python main.py`, `src/services/version`, "built in Python",
a hardcoded personal path, v0.2.5, `[AWESOME]` tokens). Recommend **archive** (to
`archive/legacy-pygame/` alongside the other debris) unless a live "how to demo the build" doc is
wanted -- in which case it's a from-scratch rewrite, not an edit.

## docs/QUICK_REFERENCE.md

Beyond the version fix: strip the `[EMOJI]/[LIGHTNING]/[TARGET]` tokens and the "Party-ready
demonstrations / Spectacular celebration for achievements" boilerplate; migrate AP->Attention after
#613. Keep the one-page format -- it's a good format, wrong content.

## docs/STEAM_INTEGRATION_ROADMAP.md

The **store-copy block** (short description + "About This Game" + Key Features) is Pip-voice work --
reuse the README pitch once written. Also correct the **overclaims** before this becomes store copy:
"feature-complete", "Achievement System -- Implemented" (it's an observer-only skeleton), and the
achievement table referencing deleted `legacy/.../achievements_endgame.py`.

## docs/PRIVACY.md

Update "Current Status (v0.2.5)" -> current version and fix the `[EMOJI]` bullet markers -- **but** confirm
the privacy *implementation* hasn't changed since v0.2.5 before relabeling (don't assert current
behavior you haven't verified).

## CHANGELOG.md

Add the L1 wave to `[Unreleased]` (month engine #636, nine-stream doom #643, cost-of-debt finance #641,
calibration #638, honest CI #640). Reconcile the H1 subtitle ("Bureaucracy Strategy Game") with the
README title ("AI Safety Strategy Game").
