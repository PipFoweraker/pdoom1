# Tension Audit -- 2026-07-23 (overnight)

> **What this is.** An emergent-tension sweep across the durable design philosophy
> (DESIGN_PHILOSOPHY.md + ADRs), the recent decisions (2026-07-20..23: version
> split, cold-open, distribution, #789, cat/cosmetics, WS-3 prep, AP baseline),
> and the live build lanes (issues + metabolic labels). Goal: surface where recent
> commitments pull against older ones or against each other, so future-us is not
> surprised. Requested by Pip 2026-07-23 ("I'm particularly interested in any
> emergent tensions").
>
> **Method.** Three parallel doc-readers (philosophy/ADRs; recent decisions;
> build lanes/backlog) + a first-person read of DESIGN_PHILOSOPHY.md and the
> version-split spec + code verification of the flagged victory contradiction.
> Quotes are exact where they sharpen the point.
>
> **Status.** ANALYSIS ONLY. Nothing here is ruled. No GitHub labels were changed
> (the metabolic tiers are Pip's taxonomy; this recommends, does not mutate). No
> code changed. Written off the merge commit; lives clear of PR #806.
>
> **Severity key.** T1-class = structural-integrity or Friday-critical; T2-class =
> design coherence / latent landmine; T3-class = known / philosophy-internal /
> watch. Probabilities are my calibrated guesses, not measured.

---

## Section 0 -- FRIDAY-CRITICAL (read before the v0.13 epoch cut)

These three could bite the 2026-07-24 epoch cut specifically. Everything else can
wait for a workshop.

### F1. The L1 -> L2 ladder bump MUST ride in the SAME build as the #789 gameplay, or v0.13 scores land on the v0.12 board. (deploy-sequence hazard)

- The live v0.12.0 build friends are playing keys boards the OLD way (`v0.12.0`);
  it has no ladder split. PHASE3_DEPLOY_RECON aliases that live board to L1:
  *"copy `board_weekly-2026-w0__v0.12.0.json` -> `board_weekly-2026-w0__L1.json`."*
- PR #806 ships `game_config.gd` with `LADDER_VERSION = "1"` (L1). If the Friday
  v0.13 build (which contains #789 -- an Attention-economy gameplay change) is cut
  while `ladder_version.txt` still reads `1`, it keys boards `L1` and **mixes new
  gameplay scores into the aliased old-gameplay board.** That is exactly the lie
  ADR-0002 #5 forbids.
- PHASE3 already knows this -- *"epoch cut: also bump `ladder_version.txt` -> 2, IF
  the ladder split has landed."* The hazard is the ordering dependency: **#806 must
  merge (establishing L1 = the legacy board), THEN the v0.13 release commit bumps
  ladder -> 2 in the same build as the #789 gameplay.** If those two steps separate,
  boards contaminate silently (no error, wrong board).
- **Severity: HIGH / p(happens if not pinned) ~ 35%.** It is a two-step sequence
  with no gate enforcing the order.
- **Resolution:** make the L1->L2 bump part of the v0.13 *release commit* checklist,
  not a separate step; the `check_ladder_bump.py` heuristic should hard-flag "gameplay
  files changed (#789 touched core/) but ladder still 1". Confirm the numbering
  reconciliation in F2 first.

### F2. Epoch numbering: is the Friday cut L1 or L2? Two docs say different things.

- Version-split spec sec 5.2: *"recommend seeding it so the first ladder epoch is a
  ROUND, memorable number (e.g. `L1`)"* and treat pre-split boards as "legacy /
  epoch 0."
- PHASE3_DEPLOY_RECON: aliases the *legacy v0.12 board* to **L1** and cuts the new
  v0.13 epoch as **L2**.
- These reconcile IF you read it as: **L1 = the current v0.12 live board (retroactively
  named), L2 = Friday's v0.13 epoch.** That is coherent and is what PHASE3 assumes.
  But the split spec's words ("first epoch = L1") read as if L1 should be the *new*
  epoch. Pin it explicitly before Friday or the alias/bump could be off by one.
- **Severity: MEDIUM but Friday-blocking-adjacent.** One-line decision.
- **Resolution (recommended):** ratify "L1 = legacy v0.12 board (aliased, read-only),
  L2 = v0.13 gameplay epoch (#789)." Update the split spec sec 5.2 example from L1 to
  match so the docs stop disagreeing.

### F3. #789 routes the accept-prompt through the RESPONSE-WINDOW pipeline -- the exact channel the AP baseline says is scarcest (budget ~3/mo). (shipping Friday)

- BUILD_BRIEF_789 sec 3 recommends *"Option A for the pause-and-pay beat"* -- reusing
  the response-window pipeline.
- EARLY_AP_ECONOMY_BASELINE sec 6 warns the opposite: *"Prefer routing new
  hiring/mentoring/conference steps through PLANNED Attention spend, not windows"*
  because *"if any #789/#803 step surfaces as a response WINDOW ... it competes against
  this budget of 3 ... the overwhelm threshold arrives far sooner."*
- Philosophy names this channel the scarce one: *"The scarce channel is
  acknowledgment, not information ... decision demands are what flood."* Response
  windows ARE the acknowledgment channel.
- So #789's implementation choice loads the flood-prone channel the same week we are
  trying to fix Rick's "not enough direction / overwhelm" onboarding feedback. #789
  is replay-safe (sec 8.3, no new RNG draws) -- the concern is feel, not determinism.
- **Severity: MEDIUM-HIGH / p(opening feels spammy) ~ 40%.** It is the Friday build.
- **Resolution:** review #789 before the cut -- can the accept-prompt be a PLANNED-
  Attention beat (spend at the month boundary) rather than an interrupt window? If it
  must ship as a window for time reasons, cap it to ONE window per hire and watch the
  first playtest for overwhelm.

---

## Section 1 -- TIER-1 TENSIONS (structural / process)

### T1. The metabolic dev cycle has a mechanism but no written tier rule -- and the labels are already leaking.

**The two poles.**
- Philosophy wants stable boards on a slow, legible cadence: league metabolism is
  MONTHLY (ADR-0016 sec 3: *"World-updates are monthly, light ... Balance patches are
  slower and legible-event-grade"*); the patch is *"the community's heartbeat --
  legible events people argue about"*, explicitly *not frequent*; and the whole
  point is *"this can't take up more than 1 day a week of effort"* (ADR-0016 sec 5).
- The version-split gives a crisp BUMP rule (sec 3: bump iff same inputs could diverge
  in score/trajectory/RNG). Good. But **there is no canonical document defining the
  `league:v0.13 / patch:ui / league:next` tiers** -- the recent-decisions sweep
  confirmed "no literal metabolic dev cycle string exists in the repo." The tiers
  Pip applied this session are ad-hoc labels not derived from the bump rule.

**Why they conflict / the evidence it is leaking.** Without a written tier rule,
the labels drift. Already observed:
- **#789** is tagged BOTH `league:v0.13` (forking) AND `ship:hotpatch-48h`
  (non-forking mid-week). A forking mechanics change cannot also be a non-forking
  hotpatch. Direct contradiction.
- **#788** (leaderboard dev-mode badge -- a scoring-INTEGRITY surface) is tagged
  `patch:ui` (cosmetic).
- **#799** (install-ping + update infra) and **#805** (mac/Linux builds) are tagged
  `patch:ui` -- neither is UI.
- **#735** (enable remote board), **#700** (add_score dedupe), **#648** (uncapped-
  stacking exploit fix) are scoring-critical or forking, yet carry NO metabolic tier.

The metabolic proof-of-concept is the thing Pip is deliberately building; if the
tiers are hand-applied without a rule, they will keep misclassifying, and a forking
change will eventually ride a mid-week lane and fork the board off-schedule --
defeating the board-stability the split exists to protect.

- **Severity: HIGH / p(a mislabel forks a board within 2 epochs) ~ 30%.**
- **Resolution:** write the tier rule ONCE, derived mechanically from the split's
  bump checklist (sec 3.3), and home it in #775 (release-branching model). The rule is
  basically: tier = f(does it bump the ladder?). `league:*` iff any bump-checklist
  answer is yes; `patch:*` iff all no; infra/build/telemetry get their own non-UI
  label. Then relabel the six issues above (see Section 4). Consider a CI check that
  a `league:*` issue's PR touches `ladder_version.txt` and a `patch:*` PR does not.

### T2. "Numbers patch freely" (light, frequent) vs "any outcome-altering change forks the ladder" (heavy, board-rotating).

**The two poles.**
- Philosophy: *"Structure is never-patch; numbers patch freely"* -- and the lighter-
  check intent: *"pure number changes ... shift balance but mint no new mechanical
  surface, so they ride a lighter check."*
- The version-split bump rule (sec 3.1) makes ANY outcome-altering number change (action
  costs, doom deltas, event probabilities, finance numbers) BUMP the ladder -- i.e.
  rotate every board, scatter scores, start a new epoch.

**Why they conflict.** "Patch numbers freely" and "every number-patch forks the
board" cannot both be true operationally. If you tune balance often (which the game
needs during alpha), you either fork boards often (fragmentation) or you batch tuning
into rare epochs (numbers do NOT patch freely -- they patch monthly). The split doc's
own DECISION C recommendation ("batch into one v0.13 epoch ... testers accumulate
scores against a stable ruleset for LONGER") quietly resolves this toward batching --
which means the honest statement is **"numbers patch freely WITHIN an epoch's dev
window, and land in batches AT epoch boundaries,"** not "numbers patch freely."

This is the same root as T1: the cadence/queue discipline is the real design object,
and it is unwritten. Every queued gameplay/balance item (hiring, cat, rivals #804,
WS-3 mechanics, #648 exploit, #791 economy) wants an epoch; the design wants few.

- **Severity: HIGH (it is the load-bearing tension of the whole liveops model) /
  p ~ n/a (it is a definitional gap, not an event).**
- **Resolution:** state the epoch-train rule explicitly: balance/gameplay changes
  QUEUE for the next scheduled monthly epoch; they do not ship on merge. The Friday
  v0.13 cut is epoch N; the next epoch is ~a month out, not next week. Write this
  where the lanes can see it (ROADMAP or #775), because two forces (queue pressure +
  the every-number-forks rule) push toward more-frequent forking, and the philosophy's
  "1 day/week, small durable community, legible heartbeat" all degrade if cadence
  creeps weekly.

---

## Section 2 -- TIER-2 TENSIONS (coherence / latent landmines)

### T3. "No victory, only time bought" (never-patch structure) is HALF-implemented: vestigial victory scaffolding + a stale runtime ADR remain.

**Verified in code (not just docs).**
- Philosophy + game-design ADR-0002: *"you cannot win, only buy time"* / "There is
  no victory condition."
- Current `check_win_lose()` (`game_state.gd:525-530`) HONORS this: it only ends the
  run on `doom >= 100` or `reputation <= 0`, both setting `victory = false`. **No code
  path in the play loop sets `victory = true`** (grep of `godot/scripts` finds only
  `victory = false` assignments).
- BUT vestigial victory plumbing survives, wired to a flag nothing sets:
  `turn_manager.gd:716` still emits *"VICTORY! p(doom) reached 0!"*;
  `game_over_screen.gd:137` sets `"VICTORY!"`; `main_ui.gd:991` logs
  *"VICTORY! You survived!"*; `death_attribution.gd:40` and `baseline_simulator`
  branch on `state.victory`.
- AND the RUNTIME `docs/adr/ADR-0002` still declares *"Victory: doom <= 0 ... a real
  but rare apex victory for mastery play"* -- contradicting BOTH the game-design ADR
  AND the actual code, and contradicting the philosophy's *"ASI won't be survivable."*

**Why it matters.** Two failure modes. (1) Latent landmine: if any refactor,
save-load path, or debug toggle ever sets `victory = true`, the game shows a
"VICTORY!" screen the design says must not exist. (2) Doc drift: a live ADR documents
a win condition as canonical that the code has already removed -- a future
contributor could "restore" it in good faith.

- **Severity: MEDIUM (latent, not live) / p(a code path resurrects victory) ~ 15%.**
- **Resolution:** finish the removal -- strip the vestigial victory branches (or
  gate them behind an explicit, never-set feature flag with a comment), and reconcile
  runtime ADR-0002 with game-design ADR-0002 (mark the win condition retired, or add
  a superseding note). Non-forking (no play-loop behavior changes). Good `patch:ui`
  or tech-debt item.

### T4. The metabolic cycle promises mid-week non-forking hotpatches -- but the DELIVERY mechanism for direct-download users (L3 pck-patcher) is unbuilt AND maybe-cancelled.

**The two poles.**
- The whole point of the version split + metabolic cycle is that cosmetic/UI fixes
  ship mid-week without forking the board. That implies a way to DELIVER a mid-week
  patch to players.
- DISTRIBUTION_AND_PATCHING self-contradicts on whether that mechanism gets built:
  D3/TIMING commit to L3 (*"SIGN WITH L3"*, *"L3 next version increment"*), but the
  Steam section says *"L3 (custom pck-patcher): probably do NOT build it. Steam
  depots delta-patch natively."*

**Why they conflict.** If L3 is skipped (betting on Steam), then between now and
Steam there is **no delivery path for the mid-week cosmetic hotpatches the metabolic
cycle promises** -- direct-download users would have to re-download a full build for
a font fix. So "we'll UI-patch mid-week" (T1's `patch:ui` lane) has no wire to the
direct channel yet. The cycle's forking side (epoch = new full build) works; the
non-forking side (mid-week small patch) has no delivery.

- **Severity: MEDIUM / p(mid-week patch has no delivery path when first needed) ~ 50%.**
- **Resolution:** decide the direct-channel patch story explicitly. Options: (a)
  build a minimal L3 pck-swap for direct users pre-Steam; (b) accept "direct users
  re-download full builds; only Steam gets delta-patches" and tell testers that; (c)
  keep the friend cohort small enough that full re-download mid-week is fine (it is
  ~5 people now -- (c) may be the honest cheapest answer for this month). Pin which.

### T5. The balance instrument that would validate #789/#803 pacing cannot see the Attention economy it is changing.

- EARLY_AP_ECONOMY_BASELINE sec 7.1: *"the instrument we reach for ... literally cannot
  see Attention. It would green-light pacing it never tested."* And sec 5/sec 8.2: *"passive
  is immortal in this harness ... no non-ledger mortality floor."*
- Philosophy expects the opposite of passive-immortal in the long run (*"the
  background of Doom is nearly always going to be trending up"*) -- so a harness where
  passive never dies is either mis-measuring or exposing a difficulty-floor gap; and
  either way it is blind to Attention, the currency #789 loads.

**Why it matters.** We are shipping #789 (an Attention-economy change) Friday and
plan #803/#804 next, validated by a sweep instrument that does not model Attention.
Any "balance looks fine" signal from it about the new economy is uninformed.

- **Severity: MEDIUM / p(we ship a pacing regression the sweep couldn't catch) ~ 30%.**
- **Resolution:** before leaning on the sweep to sign off #789/#803 pacing, give it
  an Attention-aware policy (even a crude "spend all planned Attention greedily"
  baseline). Until then, treat #789 pacing as human-playtest-validated only, not
  sweep-validated -- and say so in the release notes.

### T6. The cat wants to be two different design objects: a doom-sight INSTRUMENT (aligned) and a mechanical-BONUS holder (fights minmax + instrument purity).

- The cat-as-higher-resolution-doom-oracle (CAT sec 1) is BEAUTIFULLY aligned with the
  philosophy and worth calling out as a POSITIVE resonance: *"instrumentation as
  progression"*, *"what's earned is resolution"*, *"no printed doom deltas"*, *"SA is
  channels with provenance, personified."* A diegetic, observation-rewarding doom
  sensor is on-thesis.
- The cat-adoption-vs-rival-steal giving *"2 STACKING modifiers"* (CAT sec 2) is the
  part in tension -- Pip already self-flagged it against *"don't force minmaxers,
  leave room for nonoptimal fun."* Sharpening: a modifier-holding cat also converts an
  INSTRUMENT into a RESOURCE, cutting against *"SA buys lead time, not power"* and
  *"progression lives in the org, not the hero."*

**Why it matters.** Bundling the two roles means the beloved doom-oracle drags a
minmax-y adopt-or-lose-a-swing decision along with it. Splitting them lets the oracle
ship clean.

- **Severity: LOW (explicitly next-epoch) / p ~ n/a.**
- **Resolution (WS-3 / DQ-22):** keep the cat's doom-oracle role as the primary,
  on-thesis design; make any mechanical bonus MODEST (per Pip's own sec 2 rec) or drop
  it, so the oracle is not hostage to the modifier. Decide as part of the rivals
  workshop where the rival-cat lives.

### T7. ADR-0015 "no printed doom deltas" is enforced only by a resolve-clobber; the literal delta data still exists and can be resurrected by a refactor.

- WS-3 prep sec 2 Decision 2B: *"ADR-0015's data strip is unfinished -- the fiction still
  says '-3 doom' and 40 literal fields survive as inert no-ops. Any refactor that
  drops the resolve-clobber silently resurrects printed doom."*
- ADR-0015 is a structural claim (*"only world state touches doom"*). It is currently
  true only because something clobbers the literal deltas at resolve time; the deltas
  are still in the data.

- **Severity: MEDIUM (latent landmine on a structural claim) / p(a refactor trips it)
  ~ 20%.**
- **Resolution:** finish the ADR-0015 data strip (delete the 40 inert delta fields)
  so the invariant is enforced by absence, not by a clobber. Non-forking cleanup.

### T8. The cold-open onboarding trains a "watch narrative" posture before the "actively scout" posture the early game depends on.

**Largely resolved, residual flagged.** The onboarding design already dodges the
obvious version of this: ONBOARDING_STORY_DESIGN rejects a forced tutorial (*"a
POINTER to a LEVER, not a LEASH"*), teaches lever-legibility not goal-narrative, is
skippable (`play_intros` + `INTRO_VERSION` decoupled from `CURRENT_VERSION`), and is
non-score. So it does not violate *"the quiet opening is intended"* for veterans.

The residual: the cold-open still delivers a scripted linear sequence
(phone->passcode->apps->Stranger) on first play, and the early-game's replayability
engine is *scouting* -- *"re-gathering information about this seed"*, active, opt-in.
Does the onboarding END by handing the player a scouting CHOICE ("go read / go to
meetups / who do you look into first?"), or does it end on a narrative beat? If the
first thing the game teaches is "narrative arrives at you," it mis-primes the
"you must go look" core loop.

- **Severity: LOW-MEDIUM / p(onboarding mis-primes scouting posture) ~ 25%.**
- **Resolution (WS-3):** ensure the cold-open's final beat hands the player an active
  scouting decision, not a narrative conclusion -- the handoff from scripted intro to
  opt-in scouting is the pedagogically load-bearing seam.

---

## Section 3 -- TIER-3 (known / philosophy-internal / watch)

These are already logged by Pip or are internal to the philosophy; listed for
completeness, not action.

- **T9. Doom floor: negative-legal vs sustained-fall-is-a-bug.** *"Doom rate may
  legally go negative"* vs *"persistently achievable downward trends probably mean
  I've failed to make the game hard enough."* The boundary between "impressive dip"
  and "difficulty failure" is asserted but not operationally drawn. Home: the
  exploit-sweep invariant (no bot policy sustains an N-month decline) -- pick N.
- **T10. Founding-location weight vs fast replays.** Pip's own logged open tension:
  *"the early game must carry strategic commitment AND be quick to re-play ... Civ
  never solved this; we have to."* Owned by the pacing question (ADR-0008).
- **Launcher vs Steam (DISTRIBUTION).** The separate-launcher decision (D2) partly
  fights the eventual Steam channel (*"Steam DISCOURAGES third-party launchers"*).
  Resolved only by "right-size it." Watch when Steam gets real.
- **Save-scum identity fork (WS-3 prep sec 3d).** *"Orb-of-Regret branch mechanic vs
  one-run discipline is a genuine fork with leaderboard-integrity consequences; not
  yet chosen."* WS-3 material.

---

## Section 4 -- BUILD-LANE MISLABELS (recommended relabels -- Pip's call, not actioned)

Surfaced by the backlog sweep. NOT changed on GitHub; some may be intentional. Each
is "current tier -> suggested tier, because."

**Tier contradictions / misfits:**
- **#789** `league:v0.13` + `ship:hotpatch-48h` -> pick ONE. It forks (AP economy),
  so `league:v0.13` is right; drop `ship:hotpatch-48h` (a forking change is not a
  non-forking hotpatch). If the intent was "forking but urgent," that needs a distinct
  label, not the hotpatch one.
- **#788** dev-mode badge, `patch:ui` -> a `league:*` tier. It alters leaderboard
  legitimacy display = scoring-integrity, not cosmetic.
- **#799** install-ping + update infra, `patch:ui` -> an infra/telemetry label. Zero
  UI.
- **#805** mac/Linux builds, `patch:ui` -> a build/packaging label. Zero UI.

**Scoring-critical work sitting UNTIERED:**
- **#735** enable remote board (`ship:tonight`, no tier) -> `league:*`. Most
  scoring-critical open item.
- **#700** add_score dedupe (`ship:hotpatch-48h`, no tier) -> leaderboard correctness;
  tier it.
- **#648** uncapped-stacking exploit fix (`ship:next-release`, no tier) -> exploit
  fixes are forking by definition; `league:next` at least.

**Clusters worth consolidating (four onboarding issues across three tiers):**
- Onboarding: **#801** + **#789** + **#721** + **#722** all touch onboarding/tutorial
  across `league:v0.13` and `ship:next-release`. One lane, one owner.
- Bug reporter: **#800** + **#603** are the same broken reporter, split across tiers.
- PLAN action-grouping: **#795** + **#798** + **#794** are one PLAN-screen pass split
  across `patch:ui` and `ship:next-release`.
- Cross-repo sync: **#545** + **#723** + **#724** (#724 "folds into #545") -- collapse.

**Sequencing hazard (not a mislabel):** several `ship:next-release` UI issues
(**#707, #601, #578, #577**) target screens that L2 (**#613**) will restructure. The
backlog's own rule is "hold UI polish until L2 restructures these screens." Building
them now risks polishing soon-to-be-deleted layouts. #622 (main_ui decomposition)
likely precedes them.

---

## Section 5 -- Feed into Workshop 3

WS-3's scoping is itself unresolved (prep sec 5: *"Which milestone does WS-3 serve --
v0.12 or v0.13? Everything else falls out of this"*). This audit suggests an agenda
ordered by what is load-bearing:

1. **Cadence + epoch-train discipline (T1, T2).** The single highest-leverage ruling:
   write the tier rule and pin the monthly epoch cadence. Everything about board
   stability and the "1 day/week" liveops promise depends on it. Not a mechanics
   question -- a process ruling, could be settled before WS-3 even convenes.
2. **The mid-week delivery gap (T4).** Decide the direct-channel patch story so the
   `patch:ui` lane is real, not aspirational.
3. **Onboarding -> scouting handoff (T8)** and **cat oracle-vs-modifier split (T6)**
   -- both fold naturally into the DQ-22 rivals / early-game workshop material.
4. **Instrument blindness (T5)** and **ADR-0015 data strip (T7)** -- tooling/tech-debt
   prerequisites; do them before trusting sweep sign-off or refactoring doom.
5. Carry the known Tier-3 items (T9 doom-floor N, T10 founding-vs-replay, save-scum
   fork) as standing agenda, per Pip's "finish-or-drop, don't stack" WS-3 rule.

The "crisp parts, brutal decisions" WS-3 thesis is consistent with everything here:
most of these tensions are about keeping the ENGINE crisp (one tier rule, one epoch
train, one delivery path, no vestigial victory, no latent doom-deltas) so the
DIFFICULTY can live in the decisions, not in the plumbing.

---

## Method notes & caveats

- Three background doc-readers + first-person reads of DESIGN_PHILOSOPHY.md and
  BUILD_VS_LADDER_VERSION_SPLIT.md + a code check of `check_win_lose()` and the
  victory plumbing. The victory finding was DOWNGRADED after reading code (grep alone
  implied a live win-against-thesis; the code showed vestigial scaffolding + doc drift
  instead) -- a reminder to verify before ranking.
- Probabilities are calibrated guesses, unmeasured. Severities are mine.
- No "metabolic dev cycle" doc exists in the repo; the tier taxonomy is carried
  implicitly by the version-split bump rule + issue labels. That absence IS T1.
- Not exhaustive. High-confidence coverage of philosophy, recent decisions, and open
  issues; lighter on the older balance docs (DOOM_STREAMS, DESPERATION_SOLVER,
  OPENING_BOOK -- 2026-07-13/14, pre-window) which may hide further number-level
  tensions.
