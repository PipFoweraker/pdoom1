# [Gate 5: SEED BLESSING]

**When:** Friday ~1645. The doom-wand moment. Legacy: G4.

The league seed is drawn, spoken aloud, and stamped. This is the ceremony's
heart: determinism is the game's honesty, so the seed is blessed in public.

---

## The defect this sheet was written to fix

Playbook v0's incantation contains *"The board-key forks clean."*

**That clause cannot be verified by the person saying it.** Whether a board
key "forks clean" depends on the website publishing a matching board -- a
different repository, a different deploy, owned by the website side. This
week that side was broken until hours before the ceremony (a live XSS on
the leaderboard, plus orphaned boards nobody would re-stamp: *"Do not
resolve this by re-stamping a version. That fabricates history."*).

A line that cannot be checked by the person saying it is a **defect in the
ritual, not in the person**. And this one sits on the not-allowed-to-slip
list, which makes it worse: the ceremony's most-protected clause was its
least checkable.

The fix below splits it into the part that is provable from this repository
and the part that is somebody else's, said as an attestation with a name
attached rather than as a fact.

The second thing this sheet fixes: the seed the client POSTS to is a
pinned const, `GameConfig.FEATURED_SEED_OVERRIDE`. Blessing a seed without
editing it makes the blessed and posted boards diverge -- silently, and in
a way that looks completely fine from both ends. That was open at midnight
2026-07-30 (const read `weekly-2026-w30`; it now reads `weekly-2026-w31`).
**Changing it is a code change, not a ceremony action** -- so it must be
done, merged and re-cut BEFORE this gate, not during it.

---

## Entry criteria

- [Gate 4: PROVEN BUILD] PASSED on the cut that is actually going out, with
  its cut number recorded.
- The seed rotation, if any, is already merged and inside that cut. If the
  const changed after the cut, you do not have a proven build.
- The Commissioner is present with the wand. The wand can be a pencil.

## Mechanical checks

```
cat ladder_version.txt
grep -n "FEATURED_SEED_OVERRIDE" godot/autoload/game_config.gd
grep -n "func get_board_version" -A2 godot/autoload/game_config.gd
python tools/sync_version.py --check
git log -1 --format=%H                       # the blessed commit
gh release view v<X.Y.Z> --json tagName,assets 2>/dev/null || echo "no tag yet"
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | `ladder_version.txt` value, read aloud | mechanical | yes |
| 2 | `FEATURED_SEED_OVERRIDE` literal matches the seed about to be spoken | mechanical (grep) | yes |
| 3 | That const value is the one inside the blessed cut, not just on main | mechanical (cut SHA vs const's commit) | yes |
| 4 | Board key derives from `get_board_version()`, i.e. `L<N>` not the build string | mechanical (grep the callsites) | yes |
| 5 | `sync_version.py --check` exits 0 | mechanical | yes |
| 6 | Tag pushed, release workflows green | mechanical | yes, if done here |
| 7 | The website serves a board for `(seed, L<N>)` and it is empty | mechanical but **NOT from this repo** | no -- see below |
| 8 | **No non-Standard configuration can reach this board** | mechanical (grep) | yes |

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

Check 3 is the one that catches the divergence class. Check 2 alone proves
what main says; check 3 proves what players will run. Same distinction as
[Gate 4]'s "the thing we ship, not the thing we meant."

Check 4 exists because the failure it guards has already happened once:
rebuilding the key from `CURRENT_VERSION` at any callsite re-couples the
board to the build string and re-introduces the bug the version split
fixed -- a music-only patch once forked every board.

## The incantation

> *"The ladder stands at L<N>. The seed is drawn: <SEED>. The seed the
> client posts is the seed I speak, and it is inside the build we cut. The
> board key is (<SEED>, L<N>) and it is keyed on the ladder, not the
> binary. **And no non-Standard configuration can reach this board.** The
> board itself is attested by <NAME> at <TIME>. The seed is spoken. The
> wand is waved."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "The ladder stands at L<N>" | check 1 | mechanical |
| "The seed is drawn: <SEED>" | the draw itself | speech act |
| "the client posts is the seed I speak" | check 2 -- the const literal | mechanical |
| "and it is inside the build we cut" | check 3 -- const commit vs cut SHA | mechanical |
| "keyed on the ladder, not the binary" | check 4 -- `get_board_version()` | mechanical |
| "no non-Standard configuration can reach this board" | check 8 -- locked or `is_ranked_run()`-gated | mechanical |
| "attested by <NAME> at <TIME>" | check 7 -- somebody else's observation, named | **attestation, not verification** |
| "The seed is spoken. The wand is waved." | nothing -- these ARE the acts | speech act |

Changed: *"The board-key forks clean"* is gone, replaced by three clauses
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
  change the const, re-merge, **re-cut** ([Gate 4] from check 1), and bless
  late. Option (b) costs an hour; option (a) costs nothing and is usually
  right. What is never legal is speaking a seed the client will not post
  to -- that opens a board nobody's runs can reach.
- **The const changed after the cut.** You do not have a proven build.
  Re-cut. No exceptions; this is the exact "two builds, same epoch,
  different play" lie that nothing downstream can detect.
- **A board-key callsite rebuilds from `CURRENT_VERSION`.** Hard stop. That
  is a fork bug, it scatters players across incompatible boards, and it is
  a code fix plus a re-cut.
- **The website has no board, or a dirty one.** NOT a stop for the seed
  blessing, which is about this repository. It IS a stop for
  [Gate 6: BOARD OPENS]. Bless the seed, record the website state honestly,
  and hold the opening. Note that a live board cannot be tidied after the
  fact -- *"filtering standings is editing them"* -- so an already-dirty
  board is a decision for the Commissioner, not a cleanup task.
- **Release workflow red.** Bless the seed; do not announce. The seed and
  the announcement are separable and this gate owns only the seed.
- **A player-reachable control is neither locked nor gated (check 8).** Hard
  stop, and it is a code fix plus a re-cut. Do not open the board intending to
  filter the incomparable runs off it afterwards -- *"filtering standings is
  editing them"*. The cheap legal fix is the one used twice on 2026-07-31:
  either force the control to one value (#1058) or route its runs through
  `is_ranked_run()` and TELL the player at the moment they choose (#1060).
  Silently dropping their score is not an option; that is the failure mode this
  whole week was about.

## Not verifiable from here

- **That the website publishes a board for `(SEED, L<N>)`, that it is
  empty, and that it accepts posts.** Owner: the website side. Required
  form: a named person, a timestamp, and what they actually looked at --
  not "it's fine". The incantation carries the name because an unattributed
  attestation is indistinguishable from an assumption.
- **That no scores already sit on the blessed board.** Same owner. This is
  not hypothetical: rolling the seed late leaves runs already scored on the
  board the league is about to open on.
- **Council note (not a ruling):** the not-allowed-to-slip list currently
  protects "[Gate 5]'s board-key check". Under this sheet that check is
  three mechanical clauses plus one external attestation. The list should
  be read as protecting the three; the attestation cannot be protected by a
  list, only by an owner.
