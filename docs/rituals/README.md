# Ritual sheets -- the league-week gates

Internal. One sheet per gate, six gates, in ceremony order. These are the
working papers the Commissioner reads FROM at the gate; the evergreen
narrative of the ceremony still lives in
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md`.

| Sheet | Gate | When |
|---|---|---|
| `gate_1_last_pour.md` | [Gate 1: LAST POUR] | Wed ~1200 |
| `gate_2_the_freeze.md` | [Gate 2: THE FREEZE] | Wed PM |
| `gate_3_pack_blessed.md` | [Gate 3: PACK BLESSED] | Wed EOD / Thu AM |
| `gate_4_proven_build.md` | [Gate 4: PROVEN BUILD] | Thu (re-cut Fri) |
| `gate_5_seed_blessing.md` | [Gate 5: SEED BLESSING] | Fri ~1645 |
| `gate_6_board_opens.md` | [Gate 6: BOARD OPENS] | Fri ~1700 |

Legacy mapping, stated once: the playbook's zero-indexed G0-G5 are
Gate 1 = G0, 2 = G1, 3 = G2, 4 = G3, 5 = G4, 6 = G5. Gates are written
name-first with the sequence number (`[Gate 4: PROVEN BUILD]`) per Pip's
2026-07-29 ruling, because a bare "Gate 1" is ambiguous between the first
gate and the old G1.

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
  release-URL verification moved off [Gate 4] (the tag does not exist yet)
  onto [Gate 5]/[Gate 6].
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

Provisional or one-off deviations get written down on the day, in the
day-log, with the reason -- a deviation that is not recorded is
indistinguishable next week from the ceremony itself.

## Status

Drafted 2026-07-31, on league day, from the first full run of the ceremony
(2026-07-29 to 2026-07-31). Evidence base: the playbook v0,
`docs/SESSION_CAPTURE_2026-07-30.md`, and issues #1020, #1023, #1025,
#1039, #1044, #1051. Where the ceremony was wrong this week, the sheet
says so on the sheet rather than in a retro nobody re-reads.
