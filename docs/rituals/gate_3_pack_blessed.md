# [Gate 3: PACK BLESSED]

**When:** Wednesday EOD (target), Thursday AM at the latest. Legacy: G2.

The ADR-0016 league pack is authored, schema-valid, and born clean of
printed doom.

---

## READ THIS FIRST: the gate dissolved on its first run

On 2026-07-29 this gate was attempted and there was nothing to bless.
ADR-0005 seed schedules are **inert in real play** (#1020):
`GameState._init(game_seed, schedule)` accepts a schedule and treats it as
part of seed identity, but the live-play callsite is

```gdscript
# godot/scripts/game_manager.gd:80
state = GameState.new(game_seed)
```

with no schedule argument. `event_schedule` is `[]` for every real run, and
`SeedSchedule.apply_due_causes()` has never fired a cause for any player.
The only callers that pass a schedule are `baseline_simulator.gd`,
`replay_simulator.gd` and `save_load.gd` (which restores an empty array).

There is no `godot/data/packs/` directory. The missing piece was never a
schema -- `seed_schedule.gd` has always defined the cause shape -- it is a
**loader**. That is scoped for v0.14 (Aug 7), not for a league week.

So the league shipped **pack-free**, which cost nothing it was ever
getting: an empty schedule is what every previous league ran on too.

**A gate that can evaporate on inspection must say what it does when its
subject does not exist.** Playbook v0 did not, and the gate was simply
skipped in silence -- which is the same shape as every other failure this
week: an absence that looks like a pass.

Hence this sheet has two branches. Take exactly one, out loud.

---

## Branch A: THERE IS NO PACK (the null-pack path)

Use when no pack file was authored for this league, for any reason --
including "the loader does not exist yet".

### Entry criteria
- [Gate 2: THE FREEZE] PASSED.
- The Commissioner has decided, explicitly, that this league ships
  pack-free. A pack absent by accident is a FALSE line, not a null pack.

### Mechanical checks

```
ls godot/data/packs 2>/dev/null || echo "no pack directory"
grep -n "GameState.new(" godot/scripts/game_manager.gd
gh issue view 1020 --json state,title
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | No pack content is staged for this league | mechanical | yes |
| 2 | The live callsite passes no schedule (so nothing can load silently) | mechanical | yes |
| 3 | The reason is recorded against an open issue (#1020) | mechanical | yes |
| 4 | The Commissioner rules pack-free acceptable for this league | judgement | yes |

Check 2 is the one that makes the null branch honest rather than lazy: it
proves the emptiness is structural, not just unpopulated. If that line ever
gains a schedule argument, this branch stops being available.

### The incantation (null pack)

> *"There is no pack. The schedule is empty, and the emptiness is proven,
> not assumed. Nothing unread ships. The month is carried by the ruleset
> alone."*

### Provenance

| Clause | Backed by | Kind |
|---|---|---|
| "There is no pack" | check 1 | mechanical |
| "the emptiness is proven, not assumed" | check 2 -- `game_manager.gd:80` passes no schedule | mechanical |
| "Nothing unread ships" | checks 1+2 together: no content exists to be unread | mechanical |
| "carried by the ruleset alone" | check 4 | declared judgement |

---

## Branch B: THERE IS A PACK

Use once the #1020 loader lands (candidate epoch v0.14).

### Entry criteria
- A pack file exists at its agreed path and is under version control.
- The loader passes it to `GameState.new()` and the schedule reaches
  `VerificationTracker`, so replays still verify.
- The ladder consequence has been faced: **every pack change forks the
  ladder** (pack content is part of seed identity), so this branch implies
  a ladder bump, which implies [Gate 2] declared that value.

### Mechanical checks

```
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
python tools/check_ladder_bump.py --base <last-league-tag>
# plus, once they exist: the pack loader's own validation, run in reject
# mode -- unknown cause types must fail loudly at LOAD, not push_warning
# at fire time.
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | Pack parses and every cause type is one of the three permitted | mechanical (loader validation) | yes, once built |
| 2 | Zero printed-doom deltas in pack content | mechanical, and structurally guaranteed -- see below | yes |
| 3 | Ladder bumped for the pack change | mechanical (`ladder_version.txt` diff) | yes |
| 4 | The Commissioner has read every card | judgement, irreducibly human | yes |

On check 2, an honest downgrade of playbook v0's claim: the ADR-0005 cause
types (`rival_funding_wave`, `rival_aggression_shift`, `inject_event`) can
touch sim INPUTS only. **The format cannot express printed doom.** So the
grep is a belt over a structural guarantee, not the guarantee itself
(#1020). Keep the belt -- it catches a future cause type that breaks the
invariant -- but do not describe it as the thing keeping doom unprinted.
ADR-0015 and its guard tests in the fast gate do that.

Check 4 has no mechanical substitute and should not acquire one. It is the
only check in the whole ceremony that is purely an act of attention.

### The incantation (pack present)

> *"The pack is clean of printed doom -- by grep, and by a format that
> cannot say it. The schema holds. The ladder moved, because content is
> seed. Every card has been read by the one who blesses it."*

### Provenance

| Clause | Backed by | Kind |
|---|---|---|
| "clean of printed doom -- by grep" | check 2, the grep | mechanical |
| "and by a format that cannot say it" | ADR-0005 input-only cause types (#1020) | structural |
| "The schema holds" | check 1, loader validation | mechanical |
| "The ladder moved, because content is seed" | check 3 | mechanical |
| "Every card has been read by the one who blesses it" | check 4 | human judgement, no substitute |

---

## When a line is FALSE

- **A pack was intended but is not finished.** Fall to Branch A and say so.
  Shipping pack-free is a legal league; shipping a half-read pack is not.
  This week's lesson underneath it (`SESSION_CAPTURE_2026-07-30.md`):
  *"An unticketed commitment does not happen."* The ADR-0016 pack pipeline
  was owed in the ADR and in the runsheet prose, never given an issue
  number, so no lane picked it up. **Documenting debt is not scheduling
  debt.** If Branch A is taken, file or update the issue before speaking.
- **A card has not been read.** Not a stop for the league; a stop for the
  pack. Cut the unread card, re-run check 1, then bless the smaller pack.
  A pack is a list -- it shrinks cleanly.
- **Grep finds a printed-doom delta.** Hard stop, and it is on the
  not-allowed-to-slip list. It also means a cause type escaped the
  input-only invariant, which is an ADR-0015 bug well above pack scope.
  Stop the pack, file it, ship pack-free (Branch A).
- **Pack changed but the ladder did not.** Bump the ladder, which sends you
  back through [Gate 2]'s check 4 and invalidates any existing build.

## Not verifiable from here

- Nothing external. Both branches close entirely inside this repository --
  which is why the null branch could be made honest at all.
- Note for the Council: because Branch A is fully mechanical and cheap,
  there is no reason for this gate ever to be *skipped* again rather than
  *spoken null*. A skipped gate leaves no record; a null gate does.
