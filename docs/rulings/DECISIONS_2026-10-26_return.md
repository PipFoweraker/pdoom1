# Decisions, 2026-10-26 -- Pip's return batch

Pip answered the 25-item "Needs a Pip ruling" list from
`docs/TRIAGE_2026-09-07_backlog.md` section 5 in one sitting, in a Claude Code
session on 2026-10-26, his first day back after ~2 months away ill. Answers are
recorded here as written, with a machine-readable declaration where the answer
is a ruling or a dated promise. Items he asked to have explained first are
marked PENDING, not guessed.

Standing priority order he set the same day: (1) remove what stops friends
playing -- the macOS build first; (2) a coordinated release campaign into
November 2026; (3) everything else. A web export (#1014) is wanted but ranked
below (1).

---

## Ladder for v0.14.5

RULING: 2026-10-26 -- v0.14.5 ships on ladder epoch L6 (no bump); the fresh L7 board is cut at the start of the November 2026 release campaign, which also pays #1280's declared-but-unpaid bump -- flavour: ladder-epochs -- mechanism: tools/check_ladder_bump.py --owed

Why: every v0.14.5 game change is score-neutral (the pause fix acts only while
paused, #1344 declared none; Steam was never called), and #1280 shipped in both
L6 releases, so no L6 board mixes builds with and without it. The November
campaign gets a clean board as a launch moment instead of two resets in a month.

## Release and process

1. **#1061 IP / trademark.** Not yet spoken to the Australian lawyers. Pip asked
   for paste-ready email copy (supplied in session).
2. **#1343 pause-semantics sweep.**
   COMMITMENT: 2026-10-31 -- #1343 pause-semantics sweep: state what 'paused' means and bring the 9 timers, 18 tweens and 47 input surfaces under it -- owner: pdoom1-seat -- kind: deadline -- note: ruled by Pip 2026-10-26, replacing the missed 2026-09-04 date
3. **#1269 release branches.**
   RULING: 2026-10-26 -- adopt the release-branch model in RELEASING.md for real (release/v0.X cut per epoch, tags only from release branches), enforced by mechanical guards rather than prose -- flavour: release-cadence -- mechanism: guards to be built under #1269
4. **#1290 tag protection.**
   RULING: 2026-10-26 -- only Pip creates release tags -- flavour: releases -- mechanism: GitHub ruleset 21258734 (refs/tags/v*, creation/deletion/non-fast-forward, bypass: Admin role, Pip the only admin)
   The ruleset already existed (created 2026-08-24) and was verified active on
   2026-10-26 with `gh api repos/PipFoweraker/pdoom1/rulesets/21258734`.
   Caveat: an agent using Pip's own `gh` token *is* Pip to GitHub, so the
   ruleset cannot tell the two apart. Agents must never push a `v*` tag.
5. **#1299 pre-release checks.**
   RULING: 2026-10-26 -- pre-release checks become a blocking gate on the release workflow; a red check stops the publish -- flavour: ci-gates -- mechanism: to be built under #1299
6. **#1025 gate order.** Pip asked for the explanation to go into the
   developer guide with diagrams (`docs/dev/RELEASE_GATES.md`, PR #1351), plus a
   lightweight plan for putting dev notes and tools on the website. Having read
   the three proposed orders, he chose Idea A ("decide, lock, prove, open").
   RULING: 2026-10-26 -- gates reorder to decide, lock, prove, open: Last Pour, Pack Blessed, Seed Blessing, then The Freeze (= the release-branch cut, plus a windowed check that a run actually starts), then Proven Build, then Board Opens; gate names stay, numbers follow the new order -- flavour: league-gates -- mechanism: docs/rituals gate sheets + docs/dev/RELEASE_GATES.md, amended under #1025 (replaces the gate numbering in the undeclared 2026-07-29 naming ruling, docs/GLOSSARY.md)
   Wanted later, not yet scheduled: a playtest window for testers other than Pip
   between the release-branch cut and the tag (a release candidate that friends
   play for some days). Pip aims to run at least one week ahead in his dev cycle
   as the game gains momentum. Tracked in #1355.
7. **#1266 / #1267 league-cycle handbook.**
   RULING: 2026-10-26 -- pdoom1 owns the league-cycle handbook; the website receives published versions according to protocol and never holds the master copy -- flavour: estate-process -- mechanism: to be built under #1266
   Create a pdoom1 handbook if the website's (`pdoom1-website/docs/LEAGUE_CYCLE_HANDBOOK.md`,
   last touched 2026-07-31, describing the L3 era) does not cut the mustard.

## Design calls

8. **#961 candidate pool cap.**
   RULING: 2026-10-26 -- the hiring candidate-pool cap scales with reputation instead of the fixed MAX_CANDIDATES=6 -- flavour: hiring -- mechanism: #961
   COMMITMENT: 2026-11-30 -- Revisit hiring and midgame mechanics (candidate-pool scaling first) as midgame calibration starts -- owner: pip -- kind: review -- note: ruled 2026-10-26 with #961; window is November-December
9. **#1090 Research Quality.**
   RULING: 2026-10-26 -- Research Quality (Rushed/Standard/Thorough) moves off the Plan screen to research-project level -- flavour: research -- mechanism: #1090
10. **#903 perks.**
    RULING: 2026-10-26 -- keep both the 15-perk catalogue and quirks-as-perks for now, and ask QA testers which reads better during November -- flavour: staff-surfaces -- mechanism: #903
11. **#958 lab names.**
    RULING: 2026-10-26 -- the lab-name field is randomised by default, not opt-in -- flavour: lab-names -- mechanism: #958
    Plus a wanted, low-priority expansion of the generator in the spirit of
    Robert Anton Wilson's band-name lists and Neal Stephenson's digressions
    (#1135 is the existing content issue).
12. **#788 / #1012 dev-assisted runs.**
    RULING: 2026-10-26 -- dev-assisted runs are MARKED on submitted scores, never excluded -- flavour: league-integrity -- mechanism: #1012
13. **#822 overbooking.**
    RULING: 2026-10-26 -- overbooking Attention gets teeth (forced cancel-or-pay) instead of a flat reject -- flavour: attention-economy -- mechanism: #822
14. **#823 leagues.**
    RULING: 2026-10-26 -- leagues use a hard cutover, not layered overlapping lifespans -- flavour: league-seeds -- mechanism: #823
15. **#1193 event density.** PENDING -- explanation requested.
16. **#1004 parked upgrade mechanics.**
    RULING: 2026-10-26 -- next epoch is now for the three parked upgrade mechanics (chairs attrition, board oversight/payroll UI, ethicist headcount) -- flavour: upgrades -- mechanism: #1004
17. **#1015 visual designer.** Pip is hiring a visual designer, starting
    2026-10-26.
    RULING: 2026-10-26 -- yes to pairing with a human visual designer in response to the AI-art concern; Pip is hiring one -- flavour: art-provenance -- mechanism: #1015
18. **#1014 browser demo vs code-signing.** PENDING -- explanation of code
    signing requested. (The triage cited #683 for code-signing; #683 is an
    unrelated music PR. Code-signing context lives in #917, #1038 and #1071.)
19. **#1142 Chinese localisation.**
    RULING: 2026-10-26 -- Chinese localisation before the end of 2026 remains a goal -- flavour: localisation -- mechanism: #1142
    COMMITMENT: 2026-12-31 -- Chinese localisation of the game -- owner: pip -- kind: deadline -- note: #1142, reaffirmed 2026-10-26; scope still undecided
20. **#1257 authored art.**
    RULING: 2026-10-26 -- add a sixth provenance origin value, authored_art, for human-made art from contributing artists -- flavour: art-provenance -- mechanism: #1257
21. **#1258 worktree rule.**
    RULING: 2026-10-26 -- the P6 worktree rule gets a mechanical check rather than being deleted -- flavour: guard-doctrine -- mechanism: #1258
22. **#529 CRT / terminal aesthetic.**
    RULING: 2026-10-26 -- the CRT/terminal aesthetic is unparked -- flavour: visual-direction -- mechanism: #529
23. **#786 credits.** PENDING -- Pip asked what decision is being asked.
24. **#889, #984, #1210 workshops.** Put on the calendar. Dates PENDING Pip's
    confirmation of the proposed slots.
25. **#950 creative harvest.**
    RULING: 2026-10-26 -- approve creative-harvest items 1-3 and 5-12 of #950; item 4 (the 2026-07-30 anniversary beat) expired unbuilt -- flavour: creative-harvest -- mechanism: #950
