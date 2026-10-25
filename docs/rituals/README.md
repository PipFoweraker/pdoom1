# Ritual sheets -- the league-week gates

Internal. One sheet per gate, six gates, in ceremony order. These are the
working papers the Commissioner reads FROM at the gate; the evergreen
narrative of the ceremony still lives in
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md`.

The order is *decide, lock, prove, open* (ruled 2026-10-26, #1025;
`docs/rulings/DECISIONS_2026-10-26_return.md` item 6):

| Sheet | Gate | Phase | When |
|---|---|---|---|
| `gate_1_last_pour.md` | [Gate 1: LAST POUR] | decide | Wed ~1200 |
| `gate_2_pack_blessed.md` | [Gate 2: PACK BLESSED] | decide | Wed EOD / Thu AM |
| `gate_3_seed_blessing.md` | [Gate 3: SEED BLESSING] | decide | after Gate 2 |
| `gate_4_the_freeze.md` | [Gate 4: THE FREEZE] | lock -- cut `release/v0.X`, and a run starts | after Gate 3 |
| `gate_5_proven_build.md` | [Gate 5: PROVEN BUILD] | prove | after Gate 4 (re-cut as needed) |
| `gate_6_board_opens.md` | [Gate 6: BOARD OPENS] | open | Fri ~1700 |

The weekday slots for Gates 3-5 were not re-ruled with the reorder; read them
as an ordering, not a calendar.

Gates are written name-first with the sequence number
(`[Gate 5: PROVEN BUILD]`) per Pip's 2026-07-29 ruling, because a bare
number is ambiguous -- and since 2026-10-26 it is ambiguous twice over. The
names never changed; only the numbers did.

**Records and documents dated before 2026-10-26 use the old numbering.** They
are left as written, because they describe what happened under it. Mapping:

| Name | Now (from 2026-10-26) | 2026-07-29 .. 2026-10-25 | Playbook v0 |
|---|---|---|---|
| LAST POUR | Gate 1 | Gate 1 | G0 |
| PACK BLESSED | Gate 2 | Gate 3 | G2 |
| SEED BLESSING | Gate 3 | Gate 5 | G4 |
| THE FREEZE | Gate 4 | Gate 2 | G1 |
| PROVEN BUILD | Gate 5 | Gate 4 | G3 |
| BOARD OPENS | Gate 6 | Gate 6 | G5 |

Old file names, for links in old records: `gate_2_the_freeze.md` is now
`gate_4_the_freeze.md`, `gate_3_pack_blessed.md` is `gate_2_pack_blessed.md`,
`gate_4_proven_build.md` is `gate_5_proven_build.md`, and
`gate_5_seed_blessing.md` is `gate_3_seed_blessing.md`.

## What a sheet is for

The cardinal sin of the ceremony is *saying a line you have not verified*.
A sheet exists so that no line can be said without a check next to it. Each
sheet carries, in this order: entry criteria, the mechanical checks as
literal commands, the incantation, per-line provenance (which check backs
which clause), the abort path when a line is FALSE, and the items that
cannot be verified from this repository at all.

Three properties are load-bearing:

- **Every clause maps to a check.** If a clause has no check, it is either
  cut or demoted to a stated judgement, marked as such.
- **A check must be runnable at the moment the line is spoken.** A check
  that can only run later belongs to a later gate. This is why the
  release-URL verification moved off [Gate 5: PROVEN BUILD] (the tag does
  not exist yet) onto [Gate 6: BOARD OPENS], and why the 2026-10-26 reorder
  moved "the seed is inside the cut" from [Gate 3: SEED BLESSING] to
  [Gate 5] -- there is no cut when the seed is blessed.
- **A FALSE line has a named next step.** The playbook says only that the
  gate is not PASSED. That was not enough this week.

## Authority

`docs/RELEASE_NOMENCLATURE.md` is CANONICAL on epochs, seeds, ladders,
board keys and forking. If a sheet disagrees with it, the sheet is wrong;
fix the sheet. `docs/GLOSSARY.md` defines the terms. These sheets define
only the ceremony.

Roles are unchanged: the **Commissioner** (Pip) is the only one who
blesses; the **Clerk** (Fable) may declare a gate READY, never PASSED; the
**Bureau** (agent lanes) builds and never blesses.

## Amendment

Wording, checks and ordering are amended by a **Council of Elders vote**,
per issue **#1025**. An open vote is recorded on the affected sheet in a
PENDING VOTE box and is NOT in force until it carries. The Clerk may draft
an amendment; the Clerk may not adopt one.

Carried so far: the reorder and the Freeze's boot check, ruled 2026-10-26
(#1025). A playtest window for testers other than Pip, between the
release-branch cut and the tag, is wanted but not scheduled (#1355).

Provisional or one-off deviations get written down on the day, in the
day-log, with the reason -- a deviation that is not recorded is
indistinguishable next week from the ceremony itself.

## Status

Drafted 2026-07-31, on league day, from the first full run of the ceremony
(2026-07-29 to 2026-07-31). Evidence base: the playbook v0,
`docs/SESSION_CAPTURE_2026-07-30.md`, and issues #1020, #1023, #1025,
#1039, #1044, #1051. Where the ceremony was wrong this week, the sheet
says so on the sheet rather than in a retro nobody re-reads.

Reordered and renumbered 2026-10-26 (#1025). Each moved sheet says, on the
sheet, which checks moved with it and why.
