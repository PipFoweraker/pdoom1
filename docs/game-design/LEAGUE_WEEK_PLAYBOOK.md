# LEAGUE WEEK PLAYBOOK -- v0

Written Tuesday 2026-07-28 evening, three days ahead of its first full run
(league close Friday 2026-07-31). Deliberately built a little ahead of how we
actually run: v0 is the proposal, Friday is the first execution, and the retro
slot at the bottom turns v0 into v1. The evergreen ceremony lives HERE; the
volatile dates live in the runsheet (`RUNSHEET_2026-07-27_to_29.md` is SSOT for
Wednesday's workshop detail). Anti-rot rule: this doc never copies what the
runsheet owns, it links.

Register note: the ceremony language below is deadpan-bureaucratic on purpose --
the game is a bureaucracy simulator and the league is its liturgy. Every ritual
line maps to a mechanical check. The incantation is a checklist you can say out
loud; the checklist is an incantation you can verify. Neither is decoration.

---

## The shipping cycle (the week shape, per Monday's audacity ruling)

- Mon-Wed: daily patches. 3-4 ladder-version breaks priced in and accepted.
- Wed: slow down. Morning = review + creative session (Fable). PM = THE FREEZE.
- Thu: no mechanics. Cleanup, playtest THE RELEASE ARTIFACT (not the editor),
  anniversary beat (one year since issue #1, 2026-07-30).
- Fri: league day. Pack final, build proven, seed blessed, board opens.
- Sat AM: hotpatch watch window (ship:hotpatch-48h discipline).
- A parked lane at any hard stop is an agenda line, not a failure.

## Roles

- **The Commissioner** (Pip): the only one who blesses. Rules on packs, waves
  the doom wand, speaks the seed. Hard stops apply to the Commissioner and are
  themselves part of the discipline.
- **Clerk of the League** (Fable): prepares packs, tables, verification
  evidence, and the gate paperwork. The Clerk may declare a gate READY, never
  PASSED.
- **The Bureau** (agent lanes): builds. Never blesses. Push-per-step so nothing
  the Bureau does can be lost by stopping it.

---

## Stage gates

Each gate: entry criteria -> mechanical checks -> incantation. A gate is PASSED
when the Commissioner says its incantation with every line true. Saying a line
you have not verified is the cardinal sin of the ceremony (and of the game).

### G0 -- LAST POUR (Wed ~1200)
Last mechanics merge of the week enters review. Anything not in review by the
pour does not ship this league.
- Checks: open-PR list snapshotted; W0 merge/park table complete.
- Incantation: *"What is poured is poured. The month is what it is."*

### G1 -- THE FREEZE (Wed PM, after the workshop blocks)
Main freezes for mechanics. After the freeze only: pack content, art, docs,
and bugfixes labeled league-critical.
- Checks: freeze announced in the day-log; ladder_version.txt final for the
  league; no mechanics PR may merge past this line.
- Incantation: *"No new law crosses this line. What is merged is the month.
  What is parked is the next."*

### G2 -- THE PACK IS BLESSED (Wed EOD, target; Thu AM at latest)
The 0016 league pack is authored, schema-valid, and born clean of printed doom.
- Checks: pack schema validation passes; ADR-0015 grep proves zero printed doom
  deltas in pack content; Commissioner has read every card in the pack.
- Incantation: *"The pack is clean of printed doom. The schema holds. Every
  card has been read by the one who blesses it."*

### G3 -- THE PROVEN BUILD (Thu)
The release artifact exists and is proven, and a human has played it.
- Checks: `python tools/build_release.py` (never raw export -- the freshness
  marker must be PROVEN in the .pck); `sync_version.py --check` green;
  changelog heading carries the literal version; playtest pass on the built
  artifact incl. soft-lock sweep; release URL verification green (the #998
  fail-loud check: every advertised door answers 200).
- Incantation: *"The build is fresh and proves it. The version speaks with one
  voice. A human has played the thing we ship, not the thing we meant."*

### G4 -- THE SEED BLESSING (Fri PM) -- the doom wand moment
The league seed is drawn, spoken aloud, and stamped. This is the ceremony's
heart: determinism is the game's honesty, so the seed is blessed in public.
- Checks: seed generated and recorded; ladder_version stamped; board-key fork
  verified clean; tag pushed; release workflows green.
- Incantation: *"The ladder stands at N. The board-key forks clean. The seed
  is drawn: <SEED>. The seed is spoken. The wand is waved."*

### G5 -- THE BOARD OPENS (Fri evening)
- Checks: league live; announce posted (site news stub was pre-staged
  Wednesday); first runs observed; hotpatch window armed.
- Incantation: *"The board is open. Doom is patient. Play."*

---

## This week's dated instantiation (proposal -- Commissioner tunes the clock)

| When | What |
|---|---|
| Wed 07-29 AM | W-3b workshop per runsheet (W0 review of Tuesday's builds first). Creative session w/ Fable. |
| Wed ~1200 | **G0 LAST POUR** |
| Wed PM | W-blocks continue; **G1 THE FREEZE**; pack authoring; anniversary-eve devblog beat 1515-1545; **G2 target EOD** |
| Thu 07-30 | ANNIVERSARY (1yr since issue #1). Cleanup + release-artifact playtest. **G3 THE PROVEN BUILD.** Invite the playtester friend. |
| Fri 07-31 ~1500 | Final build cut if Thu found anything; otherwise re-verify G3 |
| Fri ~1645 | **G4 THE SEED BLESSING** (doom wand, seed spoken) |
| Fri ~1700 | **G5 THE BOARD OPENS**; announce |
| Sat 08-01 AM | Hotpatch watch window; league retro notes -> playbook v1 |

## Ceremony prep

- Props: Commissioner builds props Wednesday (his declaration, 2026-07-28).
  OPEN QUESTION for Pip: pixel props (the rebase triage set), physical
  doom-wand props for the ceremony/stream, or both?
- The incantations above are v0 text -- Wednesday's creative session may tune
  the voice. The mechanical checks under them are not tunable by vibe; they
  are the point.
- No Jira this week (ruled 2026-07-28). The playbook and runsheet are the
  tracking surface; gates are the stage-gate system.

## What can slip (league-week sacrificial list)

1. Any mechanics lane not through G0 -- next month's league, by construction.
2. Devblog length/polish -- a short honest post beats a late shiny one.
3. Ceremony production value -- the checks matter; the wand can be a pencil.
4. NOT allowed to slip: G2's clean-of-printed-doom, G3's proven build, G4's
   board-key check. These three are why players can trust the league.

## Retro slot (fill Sat/Mon -> becomes v1)

- Which gate was theatre, which caught something real?
- Timing misses vs the table above?
- Incantation lines that felt wrong in the mouth?
