# [Gate 3: SEED BLESSING]

**When:** after [Gate 2: PACK BLESSED], before [Gate 4: THE FREEZE]. The
doom-wand moment. Legacy: G4. Numbered Gate 5 (Friday ~1645, after the build)
before the 2026-10-26 reorder (#1025).

The league seed is drawn, spoken aloud, and committed. This is the ceremony's
heart: determinism is the game's honesty, so the seed is blessed in public.

---

## Why this gate moved in front of the build

Ruled 2026-10-26 (#1025, `docs/rulings/DECISIONS_2026-10-26_return.md` item 6):
the gates run *decide, lock, prove, open*. The seed is a decision, so it is
blessed before anything is locked or built.

The seed the client POSTS to is a pinned const,
`GameConfig.FEATURED_SEED_OVERRIDE`. **Changing it is a code change, not a
ceremony action.** Under the old order the seed was blessed AFTER the proven
build, so blessing a different seed than the const named meant change the
const, re-merge, **re-cut**, re-play. That happened: on 2026-07-30 the const
read `weekly-2026-w30`; it was corrected to `weekly-2026-w31` before that cut,
and rolled again to `weekly-2026-w32` for v0.14.0 -- read the const, never this
sentence.

At this position there is no cut yet. A wrong const costs a one-line PR, not a
re-cut, and [Gate 4: THE FREEZE] then cuts the release branch WITH the blessed
seed in it. What this gate can no longer claim is that the seed is "inside the
build we cut" -- no build exists. That clause and its check moved to
[Gate 5: PROVEN BUILD] (check 9), and the Freeze repeats the branch-level
version of it (its check 6).

## The defect this sheet was written to fix (2026-07-31, still in force)

Playbook v0's incantation contains *"The board-key forks clean."*

**That clause cannot be verified by the person saying it.** Whether a board
key "forks clean" depends on the website publishing a matching board -- a
different repository, a different deploy, owned by the website side. That
week the website side was broken until hours before the ceremony (a live XSS
on the leaderboard, plus orphaned boards nobody would re-stamp: *"Do not
resolve this by re-stamping a version. That fabricates history."*).

A line that cannot be checked by the person saying it is a **defect in the
ritual, not in the person**. The fix split it into the part that is provable
from this repository (checks 1-4 and 8 below) and the part that is somebody
else's, said as an attestation with a name attached rather than as a fact.
Since the 2026-10-26 reorder that attestation is spoken at
[Gate 6: BOARD OPENS] (its check 7), because "the board is empty" is a claim
about the moment the board opens, and the proving playtest at [Gate 5] now
runs on the blessed seed.

---

## Entry criteria

- [Gate 2: PACK BLESSED] spoken on one of its two branches. The pack is part
  of seed identity, so it is decided first.
- The seed rotation, if any, is **merged** on the line [Gate 4: THE FREEZE]
  will cut from: `origin/main` at the epoch commit for a new epoch, or the
  existing `release/v0.X` for a point release on a live line (see
  `RELEASING.md`). An open PR or a local edit is not merged.
- The Commissioner is present with the wand. The wand can be a pencil.

## Mechanical checks

```
git fetch origin
cat ladder_version.txt
git grep -n "FEATURED_SEED_OVERRIDE: String" origin/main -- godot/autoload/game_config.gd
#   (point release on a live line: origin/release/v0.X in place of origin/main)
grep -n "func get_board_version" -A2 godot/autoload/game_config.gd
python tools/sync_version.py --check
git rev-parse origin/main                   # the blessed commit -- record it
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | `ladder_version.txt` value, read aloud | mechanical | yes |
| 2 | `FEATURED_SEED_OVERRIDE` literal matches the seed about to be spoken | mechanical (grep) | yes |
| 3 | That literal is merged on the line the Freeze will cut from, not only in a local tree or an open PR | mechanical (`git grep` against the remote ref) | yes |
| 4 | Board key derives from `get_board_version()`, i.e. `L<N>` not the build string | mechanical (grep the callsites) | yes |
| 5 | `sync_version.py --check` exits 0 | mechanical | yes |
| 8 | **No non-Standard configuration can reach this board** | mechanical (grep) | yes |

Numbers 6 and 7 are deliberately left unused so that checks keep the numbers
they had in records written before 2026-10-26. Where they went:

- **Old check 3, "that const value is the one inside the blessed cut"** --
  not runnable here, there is no cut. Replaced by the branch-level check 3
  above; the cut-level check moved to [Gate 5: PROVEN BUILD] check 9, and
  [Gate 4: THE FREEZE] check 6 confirms the const on the cut release branch.
- **Old check 6, "tag pushed, release workflows green"** -- not runnable
  here, no release branch or build exists. Moved to [Gate 6: BOARD OPENS]
  check 8.
- **Old check 7, "the website serves a board for `(seed, L<N>)` and it is
  empty"** -- moved to [Gate 6: BOARD OPENS] check 7. Spoken here it would be
  true and then made stale by the [Gate 5] proving playtest, which now runs on
  this seed.

Check 8 was added on 2026-07-31 and it was earned twice in four hours.

At 11:14 #1058 locked difficulty to Standard: difficulty existed, was persisted,
and appeared nowhere in the board key, so Easy and Hard runs were landing on one
board silently incomparable. At 16:15 #1060 closed the identical hole for the
**scenario** dropdown sitting three rows above it on the same screen -- Sandbox
Mode opens with $10,000,000 and posted to that same board.

The gap this exposes is precise, and checks 1-4 do not cover it: **"the board key
has not forked" and "everything landing on this board is comparable" are different
claims.** A board key can be perfectly stable while two runs on it were played
under rules that share nothing. The first is about identity, the second is about
meaning, and a league is a claim about meaning.

```
grep -n "func is_ranked_run" -A3 godot/autoload/game_config.gd
grep -rn "is_ranked_run" godot/scripts/          # every board-write site
grep -n "GameConfig.difficulty = 1" godot/scripts/ui/pregame_setup.gd
```

What check 8 asserts: every input that changes the starting position or the rules
is either (a) locked to one value, or (b) routed through `is_ranked_run()` so runs
under it never touch the board. Anything a player can change from a menu that is
neither locked nor gated is a check-8 failure.

Check 3 is the one that catches the divergence class at this position. Check 2
alone proves what a working tree says; check 3 proves what the Freeze will cut.
The final form of the same question -- what players will actually run -- is
[Gate 5]'s check 9, the same distinction as its "the thing we ship, not the
thing we meant."

Check 4 exists because the failure it guards has already happened once:
rebuilding the key from `CURRENT_VERSION` at any callsite re-couples the
board to the build string and re-introduces the bug the version split
fixed -- a music-only patch once forked every board.

On check 1: the ladder is read here but declared FINAL only at
[Gate 4: THE FREEZE]. A poured mechanics PR may still merge between this gate
and the Freeze, so the Freeze re-reads the ladder against the `L<N>` spoken
here (its check 4). If they differ, the board key spoken here is wrong: re-bless.

## The incantation

> *"The ladder stands at L<N>. The seed is drawn: <SEED>. The seed the
> client posts is the seed I speak, and it is committed to the line we will
> cut. The board key is (<SEED>, L<N>) and it is keyed on the ladder, not the
> binary. **And no non-Standard configuration can reach this board.** The
> seed is spoken. The wand is waved."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "The ladder stands at L<N>" | check 1 | mechanical (declared final later, at [Gate 4]) |
| "The seed is drawn: <SEED>" | the draw itself | speech act |
| "the client posts is the seed I speak" | check 2 -- the const literal | mechanical |
| "and it is committed to the line we will cut" | check 3 -- `git grep` on the remote ref | mechanical |
| "keyed on the ladder, not the binary" | check 4 -- `get_board_version()` | mechanical |
| "no non-Standard configuration can reach this board" | check 8 -- locked or `is_ranked_run()`-gated | mechanical |
| "The seed is spoken. The wand is waved." | nothing -- these ARE the acts | speech act |

Changed 2026-10-26: *"and it is inside the build we cut"* became *"and it is
committed to the line we will cut"* (no build exists at this position; the
original clause now lives in [Gate 5]'s incantation). *"The board itself is
attested by <NAME> at <TIME>"* moved to [Gate 6]'s incantation with its check.

Changed 2026-07-31: *"The board-key forks clean"* is gone, replaced by clauses
that are separately checkable plus one that is honestly labelled as
hearsay-with-a-name. Nothing was lost in meaning; what was lost was the
pretence that one person could verify all of it.

Left alone: *"The ladder stands at N"* (unchanged except for rendering the
`L` prefix, per the glossary -- `L3` next to `v0.13.2` is unambiguous,
a bare `3` is not), and the closing pair *"The seed is spoken. The wand is
waved."* Those two are speech acts and are perfect as they are. This is the
one moment in the week where ceremony is the point, and the sheet does not
touch it.

The build-order gibberish is kept and is meant to be kept: *"keyed on the
ladder, not the binary"* is funny out loud AND names the exact bug class it
prevents. That is the register to aim for -- if a line is funny and vague,
rewrite it; if it is funny and precise, keep it.

## When a line is FALSE

- **The const does not match the seed you meant to speak.** Do not bless a
  different seed to make the line true. Two legal exits: (a) bless the seed
  the const actually names, and record that the rotation slipped, or (b)
  change the const, merge it, and bless once check 3 passes. At this
  position (b) costs a one-line PR and no re-cut, so it is usually right
  now. What is never legal is speaking a seed the client will not post to --
  that opens a board nobody's runs can reach.
- **The const is changed after this gate.** If before [Gate 4: THE FREEZE]:
  re-bless. If after: it is a code change on a cut release branch -- re-bless,
  then re-run [Gate 4] and [Gate 5] from scratch. This is the exact "two
  builds, same epoch, different play" lie that nothing downstream can detect.
- **A board-key callsite rebuilds from `CURRENT_VERSION`.** Hard stop. That
  is a fork bug, it scatters players across incompatible boards, and it is
  a code fix merged before the Freeze.
- **A player-reachable control is neither locked nor gated (check 8).** Hard
  stop, and it is a code fix merged before the Freeze. Do not open the board
  intending to filter the incomparable runs off it afterwards -- *"filtering
  standings is editing them"*. The cheap legal fix is the one used twice on
  2026-07-31: either force the control to one value (#1058) or route its runs
  through `is_ranked_run()` and TELL the player at the moment they choose
  (#1060). Silently dropping their score is not an option; that is the failure
  mode that whole week was about.

The website-board and release-workflow failure paths moved to
[Gate 6: BOARD OPENS] with their checks.

## Not verifiable from here

- **Anything about the build.** None exists yet. Whether the cut carries this
  seed is [Gate 5]'s check 9.
- **The website board for `(SEED, L<N>)`.** Owner: the website side; spoken
  as a named attestation at [Gate 6].
- **Council note (not a ruling):** the not-allowed-to-slip list protects
  "[Gate 3: SEED BLESSING]'s board-key check" (G4's in the playbook). Under
  this sheet that check is the mechanical clauses here plus one external
  attestation now spoken at [Gate 6]. The list should be read as protecting
  the mechanical clauses; the attestation cannot be protected by a list, only
  by an owner.
