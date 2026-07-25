# Tech-debt burndown -- ranked (2026-07-25)

> Companion to `TECH_DEBT_REGISTER.md` (the 2026-07-12 workshop-2 audit) and
> `docs/game-design/WS3_FINISH_OR_DROP.md` (the unbuilt-ADR decision prep).
> Purpose: one ranked list of the STANDING debt with an action class per item,
> so the safe-now slices can land without a workshop and the rest is queued
> behind the WS-3 (Wed 2026-07-29) ratify block.
>
> Every code claim below is a file:line fact re-checked against this branch's
> tree on 2026-07-25 (grep of `godot/scripts`, `godot/autoload`, `godot/data`),
> or inherited verbatim from WS3_FINISH_OR_DROP.md where noted. Sizing (S/M/L)
> and "safe vs needs-decision" judgements are the analyst's calls.

## Action-class legend

- **SAFE MECHANICAL** -- behavior-preserving; landable now without ratification.
  No play-loop number changes; a green fast gate is sufficient proof.
- **NEEDS WS-3 DECISION** -- carries a design call (what to re-author onto, when
  a currency dies, keep-or-hide). Stripping without ratification would either
  change behavior or pre-empt a WS-3 question.
- **BUILD LANE (not a tidy)** -- listed for completeness; it is feature
  completion of an accepted-but-unbuilt ADR, not debt removal. Owned by the
  WS-3 lanes (#613/#614/#615), not by this burndown.

## The ranked table

| # | Item | Risk if untouched | Effort | Action class |
|---|------|-------------------|--------|--------------|
| 1 | ADR-0015 doom-clobber has no guard test | HIGH (silent) -- any refactor that drops the `resource_accessor.gd` clobber resurrects printed doom with ZERO test failures | S | SAFE MECHANICAL (add the property test now) |
| 2 | #809 vestigial victory plumbing | HIGH (latent) -- any path that sets `victory = true` shows a "VICTORY!" screen the design forbids; live runtime ADR-0002 still documents a retired win condition | S doc / M code | SAFE MECHANICAL (already milestoned) |
| 3 | ADR-0015 ~66 inert literal doom fields + "-N doom" fiction strings | MED -- compounds: the ADR-0016 pack format inherits `2017.json`'s schema and any L4 event lane copies existing events as templates | S | NEEDS WS-3 DECISION (re-author vs delete = Decision 2B) |
| 4 | Legacy `action_points` pool coexisting with Attention economy | MED -- two currencies mid-migration; the fungible scalar IS the diagnosed constant-policy exploit | L | NEEDS WS-3 DECISION (name the AP->Attention endpoint) |
| 5 | Visible `is_stub` / "[Coming Soon]" actions | MED -- fiction/mechanic gap (#801 class): player sees actions that do nothing | S | NEEDS WS-3 DECISION (keep-visible vs hide) |
| 6 | ADR-0010 adoption contradiction (private absorption offsets rival frontier) | HIGH (design) -- the rejected status-quo shape persists inside the stream engine; degenerate dominant line available by construction | M downscoped / L full | BUILD LANE (#614) |
| 7 | ADR-0011 workstream substrate missing; research->paper chain is fiction | HIGH (design) -- biggest single drag; appetite/promise loop has nothing directable to feed | L | BUILD LANE (#613) |
| 8 | TODO/FIXME residue (9 sites) | LOW -- localized, non-blocking | S each | SAFE MECHANICAL (opportunistic) |
| 9 | DEPRECATED save/load code (quicksave hidden) | LOW -- intentional deferral, documented with re-add checklist | -- | TRACKED (not debt to strip) |

## Top-5 detail

### 1. ADR-0015 doom-clobber has no guard test (S, SAFE MECHANICAL)

The clobber that makes ~66 literal `"doom": N` content fields inert is explicit
and commented -- `resource_accessor.gd:73-77` ("event-content doom sink.
Clobbered by doom resolution in the real loop (inert no-op)") and
`game_state.gd:381-382`. No test asserts the clobber holds. This is the
cheapest, safest, highest-leverage item: one property/regression test that
feeds a content dict carrying `"doom": N` through the resolve path and asserts
doom is unmoved. It converts item 3's "latent" risk into "fails CI if
resurrected," which de-risks BOTH the ADR-0016 pack pipeline and any L4 event
lane. Landable now, no design call required. Recommend pairing with a matching
guard for item 2 (assert no play-loop path sets `victory = true`).

### 2. #809 vestigial victory plumbing (S doc / M code, SAFE MECHANICAL)

`game_state.gd:525-534` `check_win_lose()` awards NO victory -- only
`doom >= 100` / `reputation <= 0`, both `victory = false`; grep of the play loop
finds ONLY `victory = false`. Safe to strip because victory is never awarded
today. But the flag is READ in ~10 sites across layers:
`turn_manager.gd:715-716` ("VICTORY! p(doom) reached 0!"),
`game_over_screen.gd:136-137` + flavor `:224-226`, `main_ui.gd:1018-1020`,
`debug_overlay.gd:212-213`, `death_attribution.gd:40`,
`baseline_simulator.gd:275`, `game_manager.gd:507`, plus the flag + save/load
(`game_state.gd:113,274,978,1058`). Two slices:
- **doc reconcile (S, do first):** the runtime `docs/adr/ADR-0002` still
  declares "Victory: doom <= 0 ... a real but rare apex victory" -- contradicts
  the game-design ADR-0002, the code, AND `DESIGN_PHILOSOPHY.md`. Mark retired /
  add superseding note. Pure doc, zero code risk.
- **code strip (M):** remove or gate-behind-a-never-set-flag the victory
  branches. Mechanical but multi-file and touches save/load -- add the item-1
  guard test alongside so "no victory" is enforced by absence + test, not by a
  flag nothing sets. Already sits in the "Technical Debt Cleanup" milestone.

### 3. ADR-0015 ~66 inert literal doom fields + fiction strings (S, NEEDS WS-3)

Verified counts (grep this tree): `core_events.json` 40, `risk_events.json` 20,
`2017.json` 4, `crisis.json` 2 effect fields (its 3rd `doom` is start-config,
fine). Plus `variable_mapping.json` maps external pdoom-data variables onto the
doom sink, and two player-facing "-N doom" fiction strings survive
(`risk_events.json:14`; `actions.gd:847` prints "-N doom" while actually writing
`global_alarm`). The strip itself is content-only and S-sized, but WS-3
Decision 2B explicitly wants it RATIFIED, not silently done -- the design call
is "re-author onto intermediaries vs delete," and whether it rides the L4
content lane or goes standalone. Do the item-1 guard test now; hold the strip
for the ratify block.

### 4. Legacy action_points pool vs Attention economy (L, NEEDS WS-3)

165 `action_points` refs across engine + `data/actions/*.json` costs. ADR-0011
decided "delete the global AP pool"; the Attention currency (evaporating
reserve) is built as ADR-0009's L1 layer (`month_plan.gd`), but the legacy AP
pool STILL EXISTS and is what actions actually spend (`game_state.gd:41-42`,
`:694` comment "legacy action_points field survives only as a low-level
resource primitive"). NOT safe to strip -- actions depend on it; the two
currencies coexist mid-migration. WS-3 must name the AP->Attention endpoint
(Decision under ADR-0011): leaving two currencies indefinitely is the same
mid-migration rot the WS3 doc targets. This is the biggest single drag but its
resolution is scheduling + build, not a mechanical tidy.

### 5. Visible is_stub / "[Coming Soon]" actions (S, NEEDS WS-3)

`travel.json:15-31` ships attend-conference + send-delegation as
`is_stub: true` "[Coming Soon]"; `travel_panel_controller.gd:108,139` renders
them; `actions.gd:462` returns "[Issue #411] Delegation system coming soon!";
`main_ui.gd:122` targeted-role hiring "COMING SOON" suffix;
`staff_perks_panel.gd:456` perk interaction stub. These are the #801-class
fiction gap. WS-3 (ADR-0014 row) explicitly asks whether the stubbed travel UI
stays visible in v0.13 or hides until the lane lands -- so keep-vs-hide is a
ratify-block question, not an analyst call. Once decided, execution is S.

## Notes / what is already retired

- **enforce-standards whole-tree churn (#773)** -- RETIRED via PR #849; this PR
  fixes the stale references to it in `CLAUDE.md` and `TECH_DEBT_REGISTER.md`.
- **Earlier dead-code kill-list** (`game_controller.gd`, `end_game_screen.gd` +
  `.tscn`) -- grep finds no such files; already deleted in L0. The
  `TECH_DEBT_REGISTER.md` "Dead code (delete in L0)" list is largely retired.
- **Doom-band desync (L6, #617)** and the 2026-07-20..22 palette/emoji/icon
  sweeps -- retired per the register's own change log.

## Recommended near-term sequence (analyst suggestion, not ratified)

1. This PR: stale enforce-standards refs (done).
2. Land the item-1 + item-2 guard tests (SAFE MECHANICAL, one small PR) -- turns
   two "latent, silent" risks into CI-enforced invariants.
3. #809 doc reconcile of runtime ADR-0002 (SAFE MECHANICAL, doc-only).
4. WS-3 ratify block resolves items 3, 4, 5 and unblocks build lanes 6, 7.
