# Playtest notes -- v0.13.1

> Pip's v0.13.1 dev-build play-through, 2026-07-25. [PIP] = verbatim-ish; [CLAUDE] = triage note.

Lossless capture of the play-through. Every observation is recorded; each gap/bug
carries a [CLAUDE] triage line mapping it to existing issues or design docs. The
consolidated proposal (for Pip's ok before anything is filed) is at the bottom.

## Positives (kept for regression tracking)

- [PIP] No cold-open intro fired. Pip suspects local settings -- he has
  `last_seen_intro_version` set from prior play. NOT a bug.
  [CLAUDE] Not a defect; corroborates the value of a "replay intro" reset (a way to
  clear/force the show-once gate). Note against #801 / the onboarding cold-open work.
- [PIP] Hiring felt "much much better"; candidate pictures being present helped.
  [CLAUDE] Positive regression marker for the hiring rework -- candidate portraits landed.
- [PIP] Onboarding popups were "great".
  [CLAUDE] Positive regression marker for the onboarding popup pass.
- [PIP] Fundraising submenu: good; showing costs was liked.
  [CLAUDE] Positive marker -- this is the reference the financing submenu should match
  (see the financing gap below).

## Gaps / polish

- [PIP] Hiring: no follow-on where an INTERVIEW takes place and then extra candidate
  info is REVEALED. "Check for gaps."
  [CLAUDE] Relates to #789 hiring-stitch (interview = schedule -> happen; fire a
  pop-up/notification when the interview happens) and the RESEARCH_IDEA_PAPER doc.
  Interview -> reveal is a real gap; #789 already frames the schedule->happen half but
  does not explicitly cover the "extra candidate info revealed" payoff.
- [PIP] Onboarding popups want a COLOURED BACKGROUND per advisor "voice" -- like Civ
  advisors (military yellow / social purple) so you know WHO is yammering. Subtle
  identity indicators.
  [CLAUDE] Advisor-persona affordance; relates to ONBOARDING_STORY_DESIGN advisor
  persona and #801 (whose open design decision #1 is "narrator/advisor persona vs plain
  text crawl"). A per-voice colour is a concrete affordance for that persona.
- [PIP] Financing submenu looks WEIRD vs fundraising: just text options, NO icons, costs
  DON'T show. Both submenus should match.
  [CLAUDE] Consistency bug. Post-CARVE-2 the SubmenuController is data-driven, so this is
  a data/config gap (financing submenu entries missing icon + cost fields that fundraising
  has), not a code-path divergence. No existing issue owns this -- candidate NEW.
- [PIP] Submit-paper submenu needs work; likely superseded by WS-3 soon, but should get
  interim better UI + reuse existing icons.
  [CLAUDE] Interim polish only (WS-3 will replace it). Reuse existing icons; no existing
  issue owns the interim look -- candidate NEW, scoped as interim.
- [PIP] Bug-report auto-close after Submit felt abrupt -- Pip wants a visible "closing in
  5...4...3...2...1" countdown so it's not a surprise.
  [CLAUDE] Same post-submit bug-report "thanks" state that #603 already addresses (#603:
  after submit the Submit button stays clickable -- disable/hide it). The countdown is
  adjacent polish on that same state -- AUGMENT #603 (or a NEW if Pip wants it tracked
  separately).

## Bugs

- [PIP] Liability Ledger won't close: ESC and L don't dismiss it; it was opened while the
  Bug Report dialog was already up (two modals stacked); pressing L toggles the background
  instead.
  [CLAUDE] Overlaps #601 "Ledger UX ... L-to-close". A separate agent is diagnosing root
  cause -- augment #601 with the modal-stacking specifics (ledger opened on top of an
  already-open bug-report modal; L routes to the background layer, not the top modal;
  ESC also fails to dismiss the top modal).
- [PIP] Deferrals are UI-INVISIBLE -- Pip wants a deferred item to either lurk as a card
  OR be reflected as a visible ledger update, so DEFER isn't silent.
  [CLAUDE] Design item. Relates to ADR-0012 (DEFER-mints-ledger) -- the ledger should
  visibly reflect deferrals (a card, or a ledger row), so the action has feedback. SEED
  into the design docs; no code issue filed yet.
- [PIP] Dev tools + F3 blocked while a modal is up.
  [CLAUDE] Dev-build-only (players lack dev tools), so not player-facing. Overlaps #600
  (dev overlays can't read live state; backslash should toggle/close) and the input-routing
  family (#575). Best home is #600 as the dev-overlay owner -- augment with "dev overlays
  (backslash / F3) are blocked/unreachable while a modal is open".

## Proposed triage -- for Pip's ok before filing

Nothing below has been filed or commented. Each existing-issue mapping was verified with
`gh issue view <n>` (state OPEN unless noted).

| # | Item | Proposal | Rationale |
|---|------|----------|-----------|
| 1 | Hiring interview -> reveal extra candidate info | AUGMENT #789 | #789 owns the hiring stitch incl. interview schedule->happen + notification; add the "extra candidate info revealed after the interview" payoff as an explicit sub-point. |
| 2 | Advisor coloured backgrounds per voice (Civ-style) | SEED (-> ONBOARDING_STORY_DESIGN; connects to #801) | Task steer: advisor-colours are design, not a filing yet. #801 open-decision #1 (persona vs text crawl) is the natural home if/when it becomes an issue. |
| 3 | Financing submenu inconsistent (no icons, costs hidden) vs fundraising | NEW ISSUE | No existing issue covers it. Title: "Financing submenu missing icons + costs -- match fundraising submenu (data-driven SubmenuController config gap)". |
| 4 | Submit-paper submenu interim UI | NEW ISSUE | No existing issue; interim-only (WS-3 supersedes). Title: "Submit-paper submenu: interim UI polish + reuse existing icons (pre-WS-3)". |
| 5 | Bug-report auto-close countdown ("closing in 5...4...3...2...1") | AUGMENT #603 (or NEW if Pip prefers) | #603 already owns the bug-report post-submit "thanks" state; the countdown is adjacent polish on that same state. Prefer AUGMENT per conservatism; genuinely could be a standalone NEW. |
| 6 | Liability Ledger won't close (modal stacking; L/ESC fail) | AUGMENT #601 | #601 already lists "L should close the ledger". Add the modal-stacking specifics (opened over an already-open bug-report modal; L/ESC route to background). Separate agent already diagnosing root cause. |
| 7 | Deferrals are UI-invisible | SEED (-> ADR-0012 DEFER-mints-ledger) | Design: the ledger should visibly reflect deferrals (card or ledger row). Task steer: likely SEED. |
| 8 | Dev tools + F3 blocked while a modal is up | AUGMENT #600 (related #575) | Dev-build-only. #600 owns the dev overlays (backslash/F3) not reading live state / toggle behaviour; add "blocked while a modal is open". Input-routing sibling is #575. |

### Positives (no action -- regression markers only)

- Cold-open intro correctly suppressed by local `last_seen_intro_version` -- feeds the
  "replay intro" reset idea (note against #801), not a bug.
- Hiring "much much better" + candidate portraits present -- keep.
- Onboarding popups "great" -- keep.
- Fundraising submenu (costs shown) liked -- the reference target for item 3.

### Summary counts

- AUGMENT: 4 (#789, #603, #601, #600)
- NEW ISSUE: 2 clear (financing submenu, paper submenu) + 1 conditional (bug-report
  countdown, if not folded into #603)
- SEED / design: 2 (advisor colours, deferral visibility)
