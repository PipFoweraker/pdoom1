# Old-Issue Triage -- decisions FOR PIP

**Status:** RECOMMENDATIONS ONLY (2026-07-25). Nothing here has been closed,
tagged, or mutated -- this is a review sheet for Pip to eyeball before any issue
is touched. Triaged the 22 oldest open issues (all vintage `#186..#520`, created
2025-08 through 2026-02, none milestoned into the live First-Contact work). Each
is scored against the CURRENT game: Godot 4.5.1 pure GDScript, survival/high-score
spine (ADR-0002), the WS-1/WS-2 ADRs (0001..0017), and the monthly-Theme release
model (`docs/RELEASE_NOMENCLATURE.md`).

The unlock this pass is looking for: **old ideas that were impossible or unclear
before the engine existed and are tractable now.** Those are marked GOLD.

Inferences I could not confirm from the issue text are marked `[INFERRED]`.

## Counts

| Classification | Count | Issues |
|---|---|---|
| REVIVE-FOR-WS3 | 7 | #476, #473, #514, #467, #475, #471, #236 |
| BUILD-LANE | 3 | #500, #506, #508 |
| FUTURE-EPOCH / ROADMAP | 5 | #186, #187, #188, #437, #433 |
| STALE-CLOSE | 7 | #470, #511, #516, #517, #518, #519, #520 |

---

## 1. REVIVE-FOR-WS3 (most-valuable first)

These read *better* now the engine exists. The top of this list is the gold: the
ledger, the effort/AP economy, the office-sim, the doom oracle and the WS-3
early-game-decisions agenda are all real now, so ideas that assumed them are
suddenly buildable instead of hand-wavy.

| # | Age | What it is | Feeds (theme / ADR) | Recommended tag/milestone | Note |
|---|---|---|---|---|---|
| **#476** GOLD | ~8mo | Progressive finance/software tiers: pen-and-paper -> spreadsheet -> QuickBooks -> ERP; each tier trades money for AP saved on ledger/payroll chores | Office economy / effort economy (ADR-0011) + liability ledger (ADR-0003) | WS-3 candidate; label `ws3:office-economy` `[INFERRED]` | The keystone revival. "Software tier reduces the AP cost of accounting" only makes sense now the ledger (ADR-0003, #601) and the effort economy (ADR-0011, #613 L2) both exist. Playtest #574 explicitly wants "accounting-software introduces the ledger" -- this issue IS that mechanic, written up 8 months early. De-scope the 6-tier table to 3 tiers for a first cut. |
| **#473** GOLD | ~8mo | Character-creation point-buy over starting conditions (location, capital, reputation, network, compute, institutional support) + presets + a "just start" default | Early-game decisions (WS-3 agenda item 1) | WS-3 candidate; label `ws3:early-game`; **consolidate with #514** | WS-3's headline agenda is literally "early-game decisions: offices choose 1 of 3, funding modes, scouting." #473 is the point-buy framing of exactly that. Near-duplicate of #514 -- merge into one design ticket for the workshop. |
| **#514** GOLD | ~7mo | Character creation with Insight domains (Political/Financial/Academic/Organizational visibility) + starting staff/resources + default class | Early-game decisions + legibility (ADR-0001 spending-buys-sight) | WS-3 candidate; label `ws3:early-game`; **consolidate with #473** | The insight-domain half maps cleanly onto ADR-0001 (spending buys sight): starting insight = pre-paid visibility. This is the legibility-flavoured version of #473. Keep #514's insight framing, fold in #473's location/capital dials, kill the duplicate. |
| **#467** GOLD | ~8mo | Employee living + office outfitting affecting morale/productivity/retention (desks, kitchen, gym; housing quality) | Office economy | WS-3 candidate; label `ws3:office-economy` | Was un-buildable before the office-sim; now #707/#791/#793 are rendering an actual office, so "outfit it for morale" has a surface to attach to. Pairs with #471 and #475 into one office-economy design block. |
| #475 | ~8mo | Comprehensive upgrades overhaul: upgrades reorganised into Office/Equipment/Software/Research with upfront + ongoing cost and a real gameplay benefit | Office economy / balance surface (ADR-0011; L9 #621) | WS-3 candidate; label `ws3:office-economy` | Broadest / least-crisp of the office-economy cluster ("comprehensive overhaul"). Best treated as the umbrella that #467/#471/#476 slot under, not its own build. Apply the WS-3 "crisp parts, brutal decisions" cut hard here. |
| #471 | ~8mo | Office cosmetic shopping (plants, coffee machine, foosball) -- small AP/budget sink, morale/culture benefit, shows up in the office view | Office economy | WS-3 candidate (lower prio); label `ws3:office-economy` | Explicitly depends on the office view (#470), which now exists. Lightweight depth-on-top; sequence AFTER #467. Pairs into the office-economy block. |
| **#236** GOLD | ~10mo | Schema for end-game states driven by real Manifold prediction-market outcomes; framed as "solve the pdoom mechanic for depth" | Meta-integrity / doom oracle (ADR-0015 no-printed-doom-deltas) | WS-3 candidate; label `ws3:meta-integrity` `[INFERRED]` | Now tractable because pdoom-data exists and the doom system is mature (ADR-0015, the WS-3 cat doom-oracle). **Determinism blocker:** a live external feed cannot drive a *scored/replayable* board (breaks the `(seed, ladder)` determinism contract). Land it as a non-scored "world doom" backdrop or in the discoverable **experimental league** (WS-3 agenda item 4), never the stable league. Flag for Pip. |

---

## 2. BUILD-LANE (concrete enough to schedule)

| # | Age | What it is | Lane / theme | Recommended tag/milestone | Note |
|---|---|---|---|---|---|
| #500 | ~7mo | Research Quality toggle: Rushed (2x speed, +debt, +doom) / Standard / Thorough (0.5x, -doom). Ships with GDScript const table + file list | Hiring-research; hooks tech-debt (ADR-0013) + doom | v0.14 "Per-tick & People" candidate `[INFERRED]`; small build | Most ratified of the whole vintage -- concrete numbers, named files, ~1-2h estimate, and both systems it touches (tech-debt, doom) already exist. **ADR-0015 tension:** the spec prints "-1 doom per turn," which violates no-printed-doom-deltas. Reframe the payoff as an *un-printed* modifier surfaced only through the doom oracle before building. Otherwise near-ready. |
| #506 | ~7mo | Clean up GDScript warnings (integer division, unused locals/params, ternary type mismatch, `seed` iterator shadowing) | Tech debt | milestone `Technical Debt Cleanup` | Pure chore against the current engine; still valid. Warning list may be partly stale after 7 months of churn `[INFERRED]` -- re-run the debugger and refresh the list before assigning. Good first-timer / low-risk lane filler. |
| #508 | ~7mo | Optional hero-art/icon field on event-popup choice buttons | Legibility / UI polish | First Contact polish; sequence after #755 | Additive, not superseded. Depends on the event-popup theming already in flight (#755) and the fanfare/backdrop work (#603/#578) -- do it as a follow-on to those, not standalone. (Issue body's pizza emoji is illustrative only; real assets would be images, and the no-emoji rule still applies to shipped strings.) |

---

## 3. FUTURE-EPOCH / ROADMAP (good, not now -- gives ROADMAP meat)

| # | Age | What it is | Future theme / epoch | Recommended tag/milestone | Note |
|---|---|---|---|---|---|
| #186 | ~11mo | Public opinion + media system: dynamic sentiment, media cycles, PR campaigns, scandals; reputation feeds funding/recruitment/regulatory pressure | Big Milestone **"Rivals & News"** (target Dec 30) | milestone `Rivals & News` `[INFERRED]` | Too large for a single Theme and there is already a dedicated "News" milestone -- park it there as the anchor design for that milestone rather than a WS-3 revive. |
| #187 | ~11mo | Regulatory/government mechanics: lobbying, compliance cost, regulatory capture; regulations cap rivals or unlock research paths | Future meta/regulation Theme (post First-Contact) | ROADMAP backlog `[INFERRED]` | Live idea, not obsolete (rivals already carry "regulatory influence"). Slots naturally next to #186 in the Rivals & News / geopolitics arc. Adds meat to a Q4+ Theme. |
| #188 | ~11mo | International/geopolitical layer: per-country AI policy, export restrictions, brain drain, labs relocating to permissive jurisdictions | Far-future Theme (post-Rivals) | ROADMAP backlog (far) `[INFERRED]` | Largest scope of the vintage; genuinely later. Keep as a ROADMAP horizon marker so the geopolitics direction is on record, not lost. |
| #437 | ~9mo | Automated blog publishing from data-lake events + commits (cross-repo pdoom1 <-> pdoom-data pipeline) | Tooling/infra (not gameplay) | ROADMAP infra backlog; overlaps #545 | Over-scoped "world-best pipeline" write-up. A dev-blog + screenshot flow (#777) now exists via a simpler path, so this should be **slimmed, not built as specified** `[INFERRED]`. Fold into the #545 cross-repo cleanup rather than run standalone. |
| #433 | ~9mo | Extract 2018-2019 AI-safety timeline from the Alignment Research Dataset (25-35 events/year) to feed historical events | Content pipeline (feeds events/meta) | **Belongs in pdoom-data repo** -- consider transfer | The timeline-as-events idea is alive, but this is a pdoom-data content task ("requires pdoom-data repository first"), misfiled in pdoom1. Recommend transfer to pdoom-data or close-here-track-there. Not stale, just wrong repo `[INFERRED]`. |

---

## 4. STALE-CLOSE (superseded / obsolete / already in flight)

| # | Age | What it is | Why close | Superseded by |
|---|---|---|---|---|
| #470 | ~8mo | Visual office representation on screen (top-down/isometric office view) | The design ask is being realised right now by the office-sim lane -- a standalone "please draw the office" ticket is redundant | #707 (office-sim visual pass), #793 (office floor), #796 (cat), #791 (office economy) |
| #511 | ~7mo | Visual highlight/glow for newly available actions until seen | Direct duplicate, re-filed 7 months later with the same "until mouseover" behaviour | #790 "Newness-glow: glow-until-mouseover" (First Contact, open) |
| #516 | ~6mo | QA: test Core Gameplay Flow section of QA_CHECKLIST.md | One-off Feb-2026 coordinated QA push; overtaken by WS-2 + v0.11-v0.13 playtest cycles that tested the same flows live `[INFERRED]` | Later playtest issues (#578/#579/#703 et al.) |
| #517 | ~6mo | QA: test Debug & Developer Tools section | Same Feb-2026 QA batch; dev overlays were separately audited since | #600 (dev overlays audit) |
| #518 | ~6mo | QA: test Events System section | Same Feb-2026 QA batch; events reworked in WS-2 (ADR-0012) after this was filed | #603/#615 (event taxonomy/intake) |
| #519 | ~6mo | QA: test Accessibility Features section | Same Feb-2026 QA batch, superseded by later UI/theme work `[INFERRED]` | theme lane (#743/#755) |
| #520 | ~6mo | QA: test Doom System & Victory Conditions | Same Feb-2026 QA batch; doom + victory reworked post-filing (ADR-0002 survival spine, ADR-0015) | ADR-0002 / ADR-0015 work |

**Note on the #516-520 QA cluster:** these aren't *bad* -- they're a stale
snapshot of a "run the checklist" process. If Pip still wants a standing release
QA gate, the right move is to **reframe one fresh checklist issue** tied to the
monthly Epoch cut, not revive five 6-month-old section-tasks. Recommend
close-with-a-pointer rather than silent close.

---

## Questions for Pip / blockers

1. **#473 + #514 consolidation:** OK to merge these two character-creation
   tickets into a single WS-3 early-game design ticket? They overlap ~80%.
2. **#236 Manifold + determinism:** confirm the routing -- world-doom backdrop
   vs experimental league only. A live external feed must NOT touch the stable
   scored board. Which surface do you want it on (if any)?
3. **#500 vs ADR-0015:** the spec prints doom deltas, which the no-printed-deltas
   rule forbids. Approve reframing the payoff as an oracle-only (un-printed)
   modifier before this is built?
4. **#433 repo home:** transfer to pdoom-data, or keep a tracking stub in pdoom1?
5. **#516-520:** close-with-pointer and open one fresh monthly-Epoch QA gate, or
   keep them as-is?

*(This doc is advisory. No issue has been closed, relabelled, or milestoned.)*
