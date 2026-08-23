# Silent failure register -- first alert, 2026-08-23

**A named defect class, its confirmed sightings, and why watching harder does not work.**

Pip named it, 2026-08-23, on being shown the smell-pass finding: *"these are
evidence of actions of one of my deadliest enemies... allowing failures to
accumulate like dust subtly just beneath the threshold of individual
perception."*

The register exists because the class was independently rediscovered **at least
fifteen times in this estate** and never written down as one thing. Each
instance was fixed on its own terms and none of the fixes generalised.

---

## The signature

A silent failure is not a crash. It is **a failure mode whose output is a
plausible-looking value.**

Three properties, all required:

1. **The failure is representable in the success type.** `Balance.num` returns a
   float; "this key does not exist" is also a float. Wherever the error case
   fits inside the return type, silence is the default outcome and no author
   chose it.
2. **The output is individually unremarkable.** Not wrong-looking. A `5.0` where
   a tuned value should be. A green check. An empty directory. Nothing about any
   single instance invites a second look.
3. **It accumulates.** One is invisible. The population is not.

**"Sensible default" and "unfalsifiable output" describe the same construct from
opposite ends.** That the first phrase sounds like good engineering is most of
the problem.

---

## Confirmed sightings

Fifteen, all from this estate, all verified rather than recalled. Ordered by
how loudly the fix had to shout.

| # | sighting | what it returned instead of failing |
|---|---|---|
| 1 | `Balance.num(key, fallback)` -- the mechanism itself | the fallback, for any key that does not exist |
| 2 | `doom.streams.upgrade_cat_alarm` read, never defined | a hardcoded `5.0`; the cat's effect is untunable and invisible in `defaults.json` |
| 3 | 13 of 273 balance keys defined and never read | nothing -- including a `doom.legacy_*` model anyone tuning would assume is live |
| 4 | Two invented Balance keys survived review (#1276) | plausible numbers; the feature "worked" |
| 5 | In-game bug reports saved to `user://`, never sent | a success dialog. **Zero reports filed, ever, across a fortnight of playtesting** |
| 6 | Desperation lever (#967) | a printed doom figure it never applied |
| 7 | Ad campaign, zero-yield month (#1225 item 3) | silence, indistinguishable from the campaign having ended |
| 8 | `Documentation Sync` workflow | **green on `main` for a month** -- the failing step is skipped where there is no PR |
| 9 | `Ladder-Impact: bump` before `--owed` | mechanically identical to `none`; both green, both silent |
| 10 | A `RULING:` written in a commit message | nothing. The generator scans the tree, not `git log`. Index stayed at 35 |
| 11 | CI reporting green while running **zero tests** (#640) | a passing gate |
| 12 | VAD in the capture pipeline | a shorter transcript, with no marker of where speech was dropped |
| 13 | Seed named `weekly-2026-w33` during ISO week 34 | a name that had stopped being true -- the same failure expressed in language |
| 14 | `$?` after a pipe, checking a Godot import | `tail`'s exit code. Reported `IMPORT_EXIT=0` while the import had failed |
| 15 | Netlify function + Bug Report Intake workflow | nothing, for **327 days**. 3 runs ever, all failures, and a doc describing it as the live path |

Two observations about the table rather than its rows:

- **Six of fifteen are green signals.** The most common form in this estate is
  not a wrong number, it is a **passing check that checked nothing**.
- **Four were found only because something else was being investigated.** None
  of those four had a finder looking for them. That ratio is the argument for
  census over vigilance.

---

## Why vigilance is the wrong counter

Pip is trained for swords, smoke and reduced visibility -- adversaries that are
**present**. Fast, hostile, and above all there to be perceived.

**This class attacks the complement of that.** No event, no moment to react in,
nothing arriving. It does not evade attention by being fast; it evades attention
by never generating a thing to attend to. *"Heighten our vigilance"* is
precisely the response the technique is designed to defeat, because vigilance
operates per-event and there is no event.

If each failure is individually sub-threshold, **per-instance detection cannot
work by construction.** Not "works poorly" -- cannot work.

---

## The three counters that do work

None of them involve looking harder.

**CENSUS -- enumerate the surface and diff both directions.** Not "is this value
right" but "what is defined, what is read, and where do those sets disagree".
This caught sightings 2 and 3 in under a minute after a weekend of nobody
noticing them. It is the cheapest counter and the estate has exactly one
instance of it (`--owed`).

**AGGREGATE -- count what is individually invisible.** One fallback resolution
is nothing; the *number* of Balance lookups resolving to fallback in a session
is a signal. Dust is invisible per mote and obvious per drift.

**DIFFERENTIAL -- run the same input twice with one variable moved.** Divergence
shows even when neither run looks wrong on its own. The determinism the
simulation already guarantees makes this nearly free here and it is entirely
unused.

The estate's existing antibodies are all instances of these, arrived at
separately: **"UNKNOWN, never zero"** (census), the **min-test floor**
(aggregate), `--self-test` **against real history** (differential). None of them
was written as an instance of a class, which is why the fourth, fifth and
fifteenth sightings still happened.

---

## Declaration

RULING: 2026-08-23 -- silent failures are a named defect class and the counter is instrumentation, never vigilance; a failure representable in its own success type must be made countable rather than watched for -- flavour: silent-failure -- mechanism: this register, and the census/aggregate/differential counters it names

**Status: first alert. The register is open and expected to grow.**

A sighting belongs here when it meets all three signature properties. Add the
row when it is confirmed, not when it is suspected -- an unverified sighting in
a register of verified ones is itself a silent failure.

**The next census to run, and the reason it is next:** the balance surface has
no gate in either direction, and it is the one surface where every existing
guard is pointed elsewhere. Roughly forty lines would have caught sightings 2,
3 and 4 before review.
