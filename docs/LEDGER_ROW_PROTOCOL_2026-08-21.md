# Ledger row: protocol, etiquette, procedure -- as at 2026-08-21

For Pip, on L5 night. **You were right that it has versioned up:** the base
procedure is three steps, and there are now three amendments layered on it, each
written after something went wrong. They are listed in force order below.

**Authority chain.** `docs/RELEASE_NOMENCLATURE.md` (pdoom1) is CANONICAL on
epochs, seeds, ladders and board keys. `docs/LEAGUE_SEED_LEDGER.md`
(pdoom1-website) is the RECORD. `docs/LEAGUE_CYCLE_HANDBOOK.md` (same repo) is
the WHY. `docs/rituals/gate_5_seed_blessing.md` (pdoom1) is the CEREMONY. Where
a ritual sheet disagrees with nomenclature, the sheet is wrong.

---

## The base procedure (LEAGUE_SEED_LEDGER.md, "How to add a row")

1. Read the seed the **shipped client** sends, from the game's protocol docs.
2. Get **Pip's explicit blessing** on that value.
3. Add the row with the **real UTC date**.

That is all it says. The amendments are where the substance is.

---

## Amendment 1 -- ROLL, NOT BLESS-IN-PLACE (ruled 2026-07-31)

**The league opens on a NEW seed; Gate 4 proving runs do not carry over.**

Reasoning, which is the part worth keeping: the website **does not filter a live
board**. Removing entries is editing standings, and a board that can be edited is
not a record. So the only honest way to exclude the Thursday proving runs is to
open on a *different board key*.

Corollary you must accept knowingly: **the board opens EMPTY and stays empty
until a real player finishes a run. That is correct, not a fault.**

**Does it bind tonight? NO.** Tonight the *epoch* moved (L4 -> L5), which forks
the key on its own. The seed is deliberately HELD at `weekly-2026-w33`. Amendment
1 exists for when the rules did NOT change and the seed is the only half that can
move. Tonight the other half moved.

## Amendment 2 -- VERIFY FROM THE ARTIFACT (same ruling, "the verification wrinkle")

This is the most important one tonight.

- **DO** read the seed and ladder out of the **built artifact**. It is the source
  of truth for what the client will send, needs no submission, and is *stronger*
  evidence than a round trip.
- **DO NOT** verify by POST. That puts a run on the opening board -- the exact
  thing being ruled out.
- **DO NOT** verify by `GET` returning `ok:true`. **Every wrong key returns
  `ok:true` too.** A positive check means entries you can count, not a 200.

**Consequence tonight, and it is good news: `api.pdoom1.com` being down does NOT
block the L5 blessing.** The ledger's own discipline never wanted a round trip.
It DOES block Gate 6 check 4 ("a real run reaches the live board") -- that is a
separate gate and a separate decision.

## Amendment 3 -- A FORK GETS RECORDED EVEN IF NOBODY BLESSED IT (2026-08-08)

*"A ledger silent about a fork is worse than one with a gap in it."* When the
ladder moves and no ceremony happened, you still write a section recording the
fact, clearly marked **NOT a blessing**. That is why L4 has a factual record and
no row.

---

## Etiquette (the things that are rude, not just wrong)

1. **Never edit a past row's seed.** A corrected seed is a NEW EPOCH, not a
   rewrite of history.
2. **Never pre-populate a seed before the ceremony that draws it.** An
   unconfirmed guess published on the site is a claim the site cannot support.
3. **Never re-stamp closed-epoch entries onto a new epoch.** They were played
   under different rules. That merge is the specific lie the ladder split exists
   to prevent.
4. **The anomaly archive is immutable.**
   `public/leaderboard/data/preserved/`. Never edit, never re-stamp -- it is the
   only surviving copy; the boards it came from have been rewritten since.
5. **Every published value carries a `source`.** *"A value with no source is a
   hardcoded literal wearing a costume."*
6. **Filtering standings is editing them.** If a board is already dirty, that is
   a Commissioner's decision, not a cleanup task.
7. **The Clerk may declare a gate READY, never PASSED. The Bureau builds and
   never blesses.** Only the Commissioner blesses.

---

## THE STATE TONIGHT -- three rows are owed, not one

| Epoch | Seed | Status in the ledger |
|---|---|---|
| L2 | `weekly-2026-w30` | Blessed 2026-07-25 by Pip. **The last completed blessing.** |
| L3 | `weekly-2026-w31` | Row reads **NOT YET BLESSED**. 6 real entries, board closed and preserved. |
| L4 | `weekly-2026-w32` | **No row at all.** Factual record only (Amendment 3). 9-11 real entries. |
| L5 | `weekly-2026-w33` | Forked today by v0.14.2. **No row yet.** |

**Four weeks, three epochs, zero completed ceremonies.** If tonight ends without
a row, L5 makes it four.

---

## PROCEDURE FOR TONIGHT, step by step

### Step 0 -- decide the scope (2 minutes, Pip only)

Bless **L5 only**, or also regularise **L3 and L4** retrospectively?

Retrospective rows are legitimate: the evidence exists (git tag messages,
`release_manifest.json`, preserved board captures) and Amendment 2 says an
artifact is stronger evidence than a round trip. Doing all three closes the gap
permanently. Doing only L5 leaves two holes that will be harder to fill later,
not easier.

**Recommendation: all three.** The evidence will never be fresher.

### Step 1 -- read the seed out of the ARTIFACT, not out of main

```
gh release view v0.14.2 --json assets
gh release download v0.14.2 --pattern "PDoom-Windows-v0.14.2.zip"
```

then read `release_manifest.json` from the release assets and confirm:

```
"ladder_version": "5"
"league_seed":    "weekly-2026-w33"
```

That is the artifact check. It is the whole of Amendment 2.

Cross-check against the tag message, which states the key in words:

```
git tag -n99 v0.14.2 | head -20
```

### Step 2 -- say the words (Gate 5 incantation, ~1645)

> *"The ladder stands at L5. The seed is drawn: weekly-2026-w33. The seed the
> client posts is the seed I speak, and it is inside the build we cut. The board
> key is (weekly-2026-w33, L5) and it is keyed on the ladder, not the binary. And
> no non-Standard configuration can reach this board. The board itself is
> attested by <NAME> at <TIME>. The seed is spoken. The wand is waved."*

**Tonight the attestation clause cannot be satisfied** -- there is no reachable
board to attest. The sheet's own instruction for that case: *bless the seed,
record the website state honestly, and hold the opening.* Say the attestation
line as what it is -- unavailable, host down -- rather than skipping it silently.

### Step 3 -- write the rows (pdoom1-website)

File: `D:\Local_Code\pdoom1-website\docs\LEAGUE_SEED_LEDGER.md`

Add to the table, real UTC date, one row per epoch, `by` = Pip. For L3 and L4
mark them plainly as **regularised retrospectively from artifacts on
2026-08-21**, and name the artifact for each. Do not backdate the `blessed`
column to the epoch date -- the blessing happened tonight; the epoch did not.

### Step 4 -- the machine-readable side

1. `public/data/ladder-epochs.json` -- set the L5 entry, `seed_status: "blessed"`,
   and fill `regularised_from` / `seed_status` for L3 and L4.
2. `public/leaderboard/data/board-probe-targets.json` -- `current_ladder_epoch`
   to **L5**, with a `source` line naming the v0.14.2 tag and manifest.

Until `seed_provenance.blessed: true` exists, `public/leaderboard/index.html`
**refuses to offer a seed to a player**. That is why this is not paperwork.

### Step 5 -- what you cannot do tonight

Gate 6 check 4, *"a real run reaches the live board"*, requires
`api.pdoom1.com`. Diagnosed 2026-08-21: DNS resolves to `208.113.200.215`, but
ICMP, `:22`, `:80` and `:443` **all time out** -- timeout, not refused, so the
HOST is unreachable, not the web server. Not a token: a token error requires a
server to read the token and say no.

**Hold Gate 6. Bless at Gate 5 anyway.** They are separable and the sheet says so.

---

## One thing that has gone stale and is worth 10 minutes later

`LEAGUE_CYCLE_HANDBOOK.md` section 5 says the current ladder epoch reaches the
website by *"a person reading a GitHub comment and typing a value"*, because
*"pdoom1 publishes no machine-readable epoch artifact yet"*. **That is no longer
true.** v0.14.1 (#1175) added `ladder_version` and `league_seed` to
`release_manifest.json`, and v0.14.2 carries them. `board-probe-targets.json`
names a `supersede_when` condition for retiring the human channel -- **that
condition is now met.** Retiring it removes the one step in this whole rail that
nothing can check.
