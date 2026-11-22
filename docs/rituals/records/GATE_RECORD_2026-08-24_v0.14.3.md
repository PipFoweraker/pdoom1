# Gate record -- v0.14.3, ladder epoch L6

**Board key: `(weekly-2026-w35, L6)`**

---

## [Gate 5: SEED BLESSING] -- PASSED

| Check | Kind | Result |
|---|---|---|
| 1. `ladder_version.txt` value | mechanical | `6` |
| 2. `FEATURED_SEED_OVERRIDE` matches the spoken seed | mechanical | `weekly-2026-w35` |
| 3. That const is inside the cut, not just on main | mechanical | PASS -- read from the build stamp in the `.pck`, not a filename |
| 4. Board key derives from `get_board_version()` | mechanical | PASS -- no callsite rebuilds from `CURRENT_VERSION` |
| 5. `sync_version.py --check` | mechanical | exit 0 |
| 6. Tag pushed, release workflows green | mechanical | tag `v0.14.3`, release published 2026-08-24T04:37Z |
| 8. No non-Standard configuration can reach this board | mechanical | PASS -- difficulty hard-locked (`LEAGUE_DIFFICULTY_LOCK := true`); scenario reachable but gated by `is_ranked_run()` |

**The seed was rolled before blessing.** The const read `weekly-2026-w34` on the
morning of 2026-08-24, during ISO week 35. Pip ruled that the seed names the ISO
week the league OPENS in, so it was rolled to `weekly-2026-w35` and the build
re-cut. The 2026-07-30 precedent in `gate_5_seed_blessing.md` -- `w30` corrected
to `w31` before that cut -- is the authority.

**`weekly-2026-w34` was never published and no board was ever opened on it.** It
is skipped, not reused.

---

## [Gate 6: BOARD OPENS] -- PASSED 2026-08-24, time DISPUTED (see below)

| # | Check | Result |
|---|---|---|
| 1 | Every advertised download URL answers 200 | **PASS** |
| 2 | The release feed's "latest" is actually this release | **PASS** -- `latest_version: v0.14.3` |
| 3 | The release body does not teach a dead keybind | **PASS** -- only `(N)`, confirmed against `keybind_manager.gd:55` |
| 4 | A real run reaches the live board | **PASS -- and by a person, not a test** |
| 5 | Announcement posted, carrying seed and ladder | Pip's, at the gate |
| 6 | Hotpatch watch window armed | Pip's, at the gate |

**Check 1, stated precisely because macOS did not ship.** Windows, Linux and both
source archives answer 200. **macOS is not advertised**: `platform_status.mac`
reads `status: not_built`, names the expected asset, and carries **no `url`**.
Nothing points at a door that does not open. The macOS export failed on an
icon regression (#1282 set an `.ico` on the macOS preset; Godot has no `.ico`
decoder), the cause is fixed in #1305, and #1309 tracks it publicly.

**Check 4 was satisfied by a real player before the gate was performed.** Rue
played the published v0.14.3 build and submitted a score at 18:04:47 AEST, which
arrived on `(weekly-2026-w35, L6)` -- the first score on a live board since
2026-08-14. The one check in the ceremony that exercises the whole chain --
client, board key, network, backend, board -- was met by the chain being used,
not by a test run submitted to satisfy it.

Board state at the moment of opening: **1 entry.**

## The incantation, as spoken

> *"Every advertised door answers. The feed names this build and no other. One
> run has travelled the whole way and arrived. The board is open. Doom is
> patient. Play."*

Spoken by **Pip Foweraker**. The words reached this seat at 2026-08-24
20:59:06 AEST; a second first-hand record puts the opening 83 minutes
earlier. See the dispute section above before citing either time.

## AN UNRESOLVED DISPUTE ABOUT WHEN THIS HAPPENED -- READ BEFORE CITING A TIME

**Two first-hand records disagree by 83 minutes, and this one may be the wrong
half.** Recorded here rather than quietly reconciled, because a ceremony record
that hides a dispute about its own timestamp is worse than one that has none.

| Record | Says | Written by |
|---|---|---|
| this file | Pip spoke the Gate 6 words at **20:59 AEST** (10:59Z) | pdoom1 seat, from the words arriving in its session |
| `pdoom1-website` `ladder-epochs.json` | `board_opened_utc: 2026-08-24T09:36:00Z` (**19:36 AEST**) | website seat, from Pip sending "1936" |

**And the site PUBLISHED the open board at 10:39Z -- twenty minutes before the
ceremony this file describes.**

**What each seat actually saw.** In this session, the incantation arrived as
text and `date` returned `2026-08-24 20:59:06 AUSEST` when it did. In the
website seat's session, Pip said "let's bless it", then sent "1936" and "note";
that seat recorded Gate 5 **and** Gate 6 at 19:36, and has since said plainly
that *"in the same breath" was its inference, not his words.*

**Two readings, and only Pip can settle it:**

1. **19:36 was Gate 5 (the seed), 20:59 was Gate 6 (the board).** Both records
   are then right about different gates, and the website's error is narrow --
   the timestamp on Gate 6, not the fact of it.
2. **19:36 was both**, and the 20:59 utterance was the ceremony being spoken
   aloud after the fact. This file's time is then the wrong one.

**Neither seat is correcting its own record on the other's word.** That would be
the same error pointed the other way. The website seat has put the question to
Pip directly.

**The structural finding, which stands whichever way it goes:** two artefacts in
two repositories now record the same ceremony at different times, each written
first-hand. `check-blessing-consistency.py` cannot see it -- it compares four
artefacts *within* the website repo. **A cross-repo blessing record has no guard
at all**, and the ceremony is performed on this side.

---

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "Every advertised door answers" | check 1, re-verified after the feed was corrected | mechanical |
| "The feed names this build and no other" | check 2 | mechanical |
| "One run has travelled the whole way and arrived" | check 4 -- Rue, 18:04:47 | mechanical, end to end |
| "The board is open." | the act of opening | speech act |
| "Doom is patient. Play." | nothing, and correctly nothing | the payload |

---

## Still owed after this gate

- [ ] Announcement, carrying seed `weekly-2026-w35` and ladder `L6`
- [ ] Saturday hotpatch window declared (`ship:hotpatch-48h` discipline)
- [ ] **The freshness drill, once per release cycle.** `gh workflow run
      live-site-release-freshness.yml -f force_alarm=true`, confirm a `[DRILL]`
      issue appears, then close it. **The run goes RED on purpose.** A green
      drill means pdoom1.com was unreachable and proves nothing. That
      workflow's issue-filing half has never executed once.
- [ ] Retro slot: which gate was theatre, which caught something real, which
      lines felt wrong in the mouth.

## What this gate caught that a ceremony is supposed to catch

The 07:48 note that day said the gates were *"two minutes, and the only thing
standing between a finished build and a scoreable one."* That was wrong.
Blessing the seed would not have made the build scoreable, because
`FEATURED_SEED_OVERRIDE` is a compiled-in const and no published build had ever
carried the rolled seed -- the league had been dark since 2026-08-14 for that
reason and no other. Gate 5's own rule names the move that would have been made:
*"speaking a seed the client will not post to -- that opens a board nobody's
runs can reach."*

The ceremony worked. It is the only thing that day that asked whether the build
players actually have could reach the board being blessed.
