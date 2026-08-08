# Saturday postmortem -- items logged live, awaiting Pip's context

Logged as they happen so the context is not reconstructed later. Pip supplies the
"why" on Saturday; this file supplies the "what", timestamped and evidenced.

---

## ITEM 1 -- Truncated lab names on the public leaderboard

**Logged 2026-08-08 ~01:05 AEST, at Pip's request.** His words:

> "Ahhhh truncated lab things eh? this is ironic. Please note it in the logs and
> I'll saturday postmortem the context as to why."

**PIP TO SUPPLY: why this is ironic.** He has context this seat does not, and he
has asked to provide it himself rather than have it guessed at. Do not fill this
in speculatively -- the whole point of logging it now is that the reason is his.

### The measured facts, so the context has something to attach to

The leaderboard's `player_name` column is populated from
`GameConfig.lab_name`, not `player_name` -- `game_over_screen.gd:280-282`:

```gdscript
var entry = Leaderboard.ScoreEntry.new(
    final_turns,
    GameConfig.lab_name,     # lands in the field named player_name
```

`GameConfig.player_name` exists (`DEFAULT_PLAYER_NAME := "Researcher"`, line 10),
is persisted (line 246), is loaded (line 309) and is settable (line 396). **PR
#1133 built an identity prompt and a lab-name generator, and the leaderboard reads
neither.**

The API then truncates with `substr` at approximately 40 characters. Pip's entry
is on the live `(weekly-2026-w32, L4)` board right now, reading:

```
GRIM (Global Risk Intervention Mechanism
```

Cut mid-word, closing bracket lost. The lab-name generator produces expanded
bacronyms precisely BECAUSE the expansion is the joke, and the expansion is the
part the truncation removes.

### Why it is on the Saturday list rather than fixed tonight

Pip: *"I'm not asking for it now it just feels silly."* He named the absurdity
rather than setting a deadline. The ruling he DID make is recorded below and is
being implemented within safe limits tonight.

### Ruled by Pip, 2026-08-08 ~01:00

> "can we submit both? I feel like this has been mentioned a lot this week.
> players will collide on lab names and player names are also cool because then a
> player can have different labs?"

**BOTH -- player name and lab name as separate values.** Reasoning: lab names
collide (a good generator makes names two people both pick), and **one player with
many labs is a supported thing the board should be able to express.** A single
conflated field destroys that permanently.

Constraints this creates, being worked now: the ~40-char server limit will not
hold two names, so either the client fits deliberately or the API changes -- and
an API change is `pdoom1-website` territory, routed through coordination, not
solved in this repo. The live board also already holds rows whose `player_name`
is a lab name, so adding a field is a migration, not an edit.

### The generalisation worth testing on Saturday

Three defects tonight share one shape: **a field whose name and contents
disagree.** `player_name` holding a lab name; `duration_seconds` reading 2.8-10s
for 147-turn runs because `game_start_time` is never set on the live path; and
`[Unreleased]` in `CHANGELOG.md` accumulating across five releases. In each case
every check passed, because a check compares a value to itself and none of them
compares a value to its own label.

Related, from the `pdoom1-website` seat the same night: the version sync writes
`data/current-game-version.json` while the site serves `public/data/version.json`
-- **a producer and a consumer with no overlapping filename.** That one never
worked at all, not once, and nothing on either side ever went red.

---

## ITEM 2 -- Dev tools for memory and performance demands

**Requested by Pip, 2026-08-08 ~03:00.** His words:

> "I want to dive into dev tools around memory and performance demands, I think
> I talked about architecting it a few days or weeks back and maybe we did a
> little poke at it, if not it's probably in an issue somewhere."

**Searched and did not find it.** Checked: all pdoom1 issue titles open and closed
(400) for profil / perform / memory / FPS / benchmark; `docs/` for "profil" and
"performance budget". The only hits are in `docs/archive/2026-07-25-reconcile/`,
which is archived reconciliation material rather than a design. **No open issue
proposes a profiling or memory instrument.**

So either the conversation happened outside this repo (orchestrator, a voice memo,
or a sibling seat), or it was talked about and never filed. Worth Pip checking his
own memos before Saturday, because a design that exists is much cheaper than one
re-derived.

**Live evidence that this is now load-bearing, not speculative:** the slow
simulation tier timed out locally at the runner's hardcoded 900s cap with zero
tests collected, while CI ran the identical tree green in 9m07s. Three candidate
causes and no instrument to distinguish them:

1. Windows dev box versus Ubuntu CI -- but Pip believes sims have run locally
   before, which weakens this
2. `#1137`'s event-deck retiming genuinely lengthened runs -- a BALANCE finding
   wearing a tooling costume, and the most interesting possibility
3. Something hangs rather than runs slow -- the process was alive at 530MB, which
   does not distinguish the two

**A memory-and-performance instrument is exactly what would tell these apart.**
The cheap distinguishing experiment, if no instrument exists by then: run the sim
tier on a quiet machine with the cap raised, against the pre-`#1137` tree and the
current one. If quiet-Windows still exceeds 900s it is the platform; if only
post-`#1137` does, runs got materially longer this week and the first thing to
notice was a timeout.

Related friction filed by the release lane: `run_godot_tests.py` hardcodes the
900s sim cap with no flag, prints no per-test progress (so "slow" and "hung" are
indistinguishable), and reports a timeout as `0 tests, 0 fail (FAIL)` -- the same
shape as the hollow-CI failure this repo already fixed once.

---

## ITEM 3 -- The test-pollution bug was already filed, and sat for a week

**Not requested. Found while searching for Item 2, and it is the sharpest thing
in this file.**

Tonight the test suite wrote **1,330 files** into Pip's live player profile,
**destroyed his 2026-07-31 league board** (50 entries -> 0), mutated `config.cfg`,
`keybinds.cfg` and `theme.cfg`, and injected 23 synthetic rows into the live
`(weekly-2026-w32, L4)` board during a release playtest. Hours went into
diagnosing it, and it briefly corrupted the evidence used to diagnose a separate
ship blocker.

**`pdoom1#1070` filed this on 2026-07-31. Seven days earlier.** It names the exact
file and line -- `godot/tests/unit/test_leaderboard_properties.gd:31` -- as
constructing a real `Leaderboard` that persists to `user://`, plus
`test_leaderboard_view_bounded.gd:91,130`. It was split out of `#1066` as, in its
own words, *"the underlying cause rather than the symptom"*.

So the analysis was correct, precise, actionable, and a week old. **Nobody
disarmed it and it went off.**

This is the strongest instance yet of the pattern the 08-07 chronicle measured:
**noticing was never the bottleneck.** The chronicle's headline gap was 241 days
between a defect being written down and being fixed. This one is 7 days between a
correct diagnosis and real data loss on a release night.

**The Saturday question is not "how do we find these" -- we found it. It is what
makes a filed, correctly-diagnosed defect get acted on before it costs something.**
Any answer that ends in "file an issue" has missed the point.

---

## ITEM 4 -- The estate DID have a guard for this. It was pointed at a decoy.

**Found 2026-08-08 by the release-sync lane, after two wrong answers about the
same file -- including one of mine.**

`data/current-game-version.json` lives at the root of `pdoom1-website`, is written
by **pdoom1's** `sync-game-version.yml`, and sits **outside the rsync source**, so
it cannot change what a visitor sees.

The story about it changed three times, and the sequence is the finding:

1. **"Producer and consumer share no filename."** Partly wrong -- the site's real
   `version.json` IS written by the website's own script to `public/data/`.
2. **"Zero consumers."** Wrong, and wrong in a specific way: the search was scoped
   to `pdoom1-website` and never asked whether *pdoom1* reads it.
3. **The truth: it has exactly ONE reader -- `release-sync-monitor.yml`, ours,
   running daily, whose entire purpose is to notice when the site has fallen behind
   a release.**

**So the estate had a check for exactly this failure, and the check read the decoy
file.** It would have reported green throughout the outage it appears to guard
against. Not a missing guard, not a broken guard -- a guard aimed one directory to
the left of the thing it was built to watch.

This is a distinct mechanism from the four in `POSTMORTEM_2026-08-07_CAPTURE.md`
and sharper than any of them, because every prior instance was something nobody was
watching. Here somebody built the watcher, wired it up, and ran it daily.

**Practical consequence, before anyone tidies:** do NOT delete
`data/current-game-version.json` as dead weight. It would break the monitor. The
real fix is repointing the monitor at what the site actually serves, which is what
`pdoom1#1182` does.

**The Saturday question this raises**, and it is harder than "add a check":
`#1182` adds a freshness check with an eight-hour tolerance, argued from the
website's six-hourly cron so it cannot cry wolf on every release. Its comparison
logic was proven red before being proposed. But **its alarm path -- issue creation
and de-duplication -- has never executed once.** So the new guard is in the same
state the old one was in: reasoned, wired, and unobserved. Watching it fire costs
one dispatch with `tolerance_minutes: 0` after a release.

Unrelated, found in passing: a pre-commit gate forced `docs/TOOLS.md` to
regenerate, which **deleted six entries pointing at `scripts/lib/scores/` and
`scripts/lib/services/` -- directories that do not exist and that git has no record
of ever containing.** The generated index has been advertising tooling that was
never in the repo.
