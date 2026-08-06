# Issue mining, 2026-08-06 -- reading the ~50 closeable issues before they close

Companion to `docs/ISSUE_TRIAGE_2026-08-06.md` (PR #1144). That document decided
WHICH issues are closeable. This one reads them, and answers Pip's constraint:

> "It would be good to thoroughly review the issues and their subsequent
> implementation to avoid losing any interesting ideas, tidbits, or drive-by
> opportunities etc."

**Method.** All 50 issues in the four closeable buckets were pulled with full
body and comment thread (`gh issue view N --comments`), read in full, and checked
against `origin/main` at the time of writing -- greps and file reads, not
inference from PR titles. Where an issue claimed a fix landed somewhere, the
somewhere was opened.

**Do NOT close anything on the strength of this document.** Closing is Pip's or
the orchestrator's action. This document tells them what is safe to close and
what is not.

---

## Headline

| Verdict | Count |
|---|---|
| CLOSE CLEAN -- read in full, yielded nothing worth saving | **32** |
| CLOSE WITH EXTRACTION -- something is lost unless it is carried out first | **7** |
| DO NOT CLOSE -- the implementation covered only part of the issue | **11** |
| **Total reviewed** | **50** |

**32 of 50 yielded nothing.** That is the number to calibrate on. Two thirds of
these issues are exactly what their titles say, were fixed, and contain no
surviving thinking. That is a healthy result, not a disappointing one -- it means
the repo's habit of writing rich issue bodies is paying into the FIX, not being
stranded in the issue.

**The more valuable output of this lane was not the extractions -- it was the 11
DO-NOT-CLOSE corrections.** Five of them are cases where the triage document
asserted an issue was absorbed by a newer document, and the newer document does
not contain it. Those five would have closed silently and stayed closed.

New issues filed: **6**. The bar is argued at the bottom.

---

## Part 1 -- triage corrections (read this part if you read nothing else)

### 1.1 The UI architecture doc does not absorb what the triage says it absorbs

The triage retires six issues on the grounds that
`docs/design/UI_ARCHITECTURE_2026-08-06.md` covers them. Measured against the
file on `main`:

| Issue | Triage claim | What the doc actually contains |
|---|---|---|
| **#622** | "superseded by the same doc's phased plan (Phase 1 IS this, with a current map)" | The doc contains **zero** occurrences of `#622`, "monolith", "decompose", or "LET-DIE". Its Phases 0-4 are an ACTION TAXONOMY plan (hiring fold, digit grammar, Research door), not a `main_ui.gd` decomposition. **The claim is wrong.** |
| **#577** | "UI arch Phase 1 owns the componentized fix" | The doc's **Part F -- what this does NOT solve** names mouse-over jiggle explicitly (line 335). It is on the out-of-scope list, not the owned list. |
| **#936** | "UI arch Phase 1 geometry contract owns this" | The doc's only "geometry" reference (line 276) assigns geometry to `test_action_visibility.gd` from #1130 -- an above-the-fold check at 1080p. It says nothing about attention-item pressure compacting the action menu. |
| **#828 / #830 / #954** | "absorbed into UI arch Phase 2's candidate-card pipeline" | Phase 2 is "merges + digit grammar". The candidate-card pipeline is named once, at line 294-295, as something the hiring panel **already has** -- an assumption, not a plan. |

**Action:** #622 and #577 must not close. #936, #828, #830 and #954 may still be
fine to close, but on the strength of a check that the described UX exists in the
game, not on the strength of this doc.

### 1.2 #802 (music) -- the wrong music player shipped

PR #1129 shipped a **dev-tools** music player: a MUSIC section inside the
backslash Alpha Tools overlay with a track dropdown, "Play selected" and
"Release -> AUTO". Its own PR body sources it to a different request from Pip
("a little music player in the dev tools function would be good ... particularly
now I have a muso who likes the game").

#802 is the playtester's request, and it is a different one: *"In-game /
pause-menu music controller -- at minimum a MUTE toggle + a SKIP/NEXT-track
button"*, plus more track variety, plus rotation decoupled from doom. Checked on
main: `settings_menu.gd` and `pause_menu.gd` carry master/SFX/music **volume
sliders** (pre-existing), and there is no skip, no next, no mute toggle, no
player-facing rotation control anywhere in `godot/scripts` or `godot/scenes`.

**#802 is not done.** Keep it open; the dev player does not answer it.

### 1.3 #1018 -- do not close until the collision matrix moves

The triage folds #1018 into #1049. #1049 was read in full: it is a real and
broader ADR-honesty issue raised from the website side (framing text, an
`Implemented:` field, the publication pipeline). It does **not** contain #1018's
two irreplaceable artefacts:

1. The **collision matrix** -- six named, evidence-carrying contradictions found
   in a single day. One of them is still live: `docs/ROADMAP.md:47` and
   `docs/RELEASE_NOMENCLATURE.md:89` both map `v0.14 -> L3`, but L3 was spent
   mid-month by #982 and the shipped build is already L3. Every row from v0.14
   down is off by one. (Verified on main today. The one collision that HAS been
   fixed is the stale `game_config.gd:159-160` runtime comment -- it is gone.)
2. The **proposed frontmatter schema** (`supersedes` / `superseded-by` /
   `canonical-authority`) plus the generate-the-index-like-`DQ_INDEX.md` cure.

Transplant both into #1049, then close #1018. Do not close it first.

### 1.4 Four issues where the fix addressed the headline and not the body

- **#1126** -- PR #1127 fixed the toggle. The issue's second half is untouched:
  the same external player got a local score and no global one, did not
  understand why, and the issue asks to confirm whether the consent prompt
  appeared and whether its wording explains the consequence of declining. That is
  a legibility defect in the same family, still open in fact.
- **#1063** -- the ask is *"let people update that on the FIRST screen"*. What
  shipped (#1133) is a one-time default-name prompt at upload; the editable
  fields still live in `pregame_setup.gd:12-13`. Also unresolved: the playtest's
  [6:28] report that a name field could not be clicked, which the issue flags as
  "the more urgent half".
- **#1064** -- PR #1144 renamed the button from "Play Again" to "New Run" with a
  tooltip. That is a good fix for the label. The issue also asks to audit the
  post-run route and make `GameManager.start_new_game`'s `force=true` refusal
  legible instead of a silent dead button. Unaddressed, and no other issue owns
  it.
- **#600** -- #1134 and PR #1144 handled event injection; #1028 owns the
  pause/`process_mode` root cause; #877 (modal stacking) is closed; the Alpha
  Tools sticky UNRANKED flag satisfies the "dev pokes must not corrupt the
  verification log" design guard. **Two sub-items remain unverified and
  unhoused:** whether the DEV MODE resource +/- nudge buttons actually change
  state, and whether backslash CLOSES the overlay as well as opening it.

### 1.5 #929 -- the thing that shipped is not the thing that was asked for

Commit `f239af06` un-gitignored `tools/art_review/review_state.json` and put
2,713 verdicts into version control. That was important and it is why the triage
found it. But #929 asked for something else: an **append-only, timestamped event
log** (`art_source/verdict_log.jsonl`, one line per verdict change with
`tags_before`/`tags_after`/`session_id`/`source`) sitting alongside the snapshot,
with an explicit anti-goal that the canonical snapshot must NOT become a log.
`git ls-tree` finds no `.jsonl` verdict log on main. The reason it was wanted --
value progressions over time, and killing the +/-2x uncertainty in
`SEED_ART_COST_MODEL`'s triage-rate estimate for want of timestamps -- is
unaddressed. Keep open.

### 1.6 #1132 -- consumed, but three items landed nowhere

Confirmed homed: item 1 (jiggle) named in the UI arch doc's Part F, item 5's
action log assigned there to #1043's workshop, the button cap and submenu ruling
absorbed into the doc's Phase 1, month review shipped in #1100, the dev-tool
phase-guard failure fixed as #1134. **Not homed:** item 3 (F3 overlay's Controls
tab is off-screen -- `debug_overlay.gd:5-7` wires only Game State / Errors /
Performance), item 4 (Operations and Office share one glyph), and Pip's own
unanswered open question about what the Office submenu group is for.

---

## Part 2 -- per-issue verdicts

### CLOSE CLEAN (32) -- read in full, nothing worth carrying out

`#959` `#1030` `#1037` `#1072` `#1068` `#1023` `#957` `#958` `#793` `#791`
`#811` `#900` `#925` `#789` `#798` `#763` `#794` `#828` `#830` `#954` `#936`
`#186` `#187` `#188` `#437` `#500` `#805` `#1062` `#1035` `#1029` `#700` `#882`

Notes only where the "nothing lost" verdict depends on a check someone might
otherwise want to redo:

- **#1030** -- the `+=`-does-not-establish-ownership rule and the rejected
  ownership-analysis design (Design B) are preserved in
  `docs/UI_PLACEHOLDER_AUDIT_2026-07-30.md` (exists on main) and actioned by
  #1031. Part (b) folds to #1031 as the triage says.
- **#1037** -- bucket 3 ("historical, DO NOT SWEEP") is not just prose, it is
  encoded in the blocking `test_no_stale_ap_vocabulary.gd` guard. Bucket 2's
  identifier/node rename (`APLabel`, `ReserveAPButton`) was explicitly filed by
  its own author as "separate post-league PR, or not at all"; declining to do it
  is a decision already made, not a loss.
- **#1035** -- verified: `main.tscn` and `player_guide.tscn` are ASCII-clean on
  main today, so the PR's "last two strings" claim holds. The transferable
  constraint (Godot rewrites `.tscn` on save and drops comments, so a `.tscn`
  allowlist must be an external checked-in file) is already cited by #1031.
- **#1072** -- the macOS "adjacent, worth fixing in the same pass" item WAS
  fixed, and its reasoning ("never weakened to compensate: skipping ... ") is
  written into `tools/build_release.py:23-41` where the next person will read it.
  Best-case outcome for an extraction: the reasoning moved into the code.
- **#1068** -- the drive-by observation (a "Verify Release Download URLs" job
  that passed while the URL was dead) is preserved as a comment at
  `.github/workflows/enhanced-release.yml:409` and the job now asserts all three
  unversioned aliases.
- **#789** -- all six rulings, the FIFO click-order-equals-execution-order
  sequencing philosophy, the provisional Attention values table and the
  deterministic response-latency note live in the TRACKED
  `docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md`. Surviving build intent is
  in #1091.
- **#805** -- the GodotSteam `.dylib`/`.so` blocker (the issue's own "risk to
  check first") is carried in both #917 and #1071.
- **#186 / #187 / #188** -- three-line feature stubs from August 2025 against the
  pygame build. There is genuinely nothing in them.
- **#925** -- the seven decision-agnostic pre-builds were a bet on W3 not yet
  having ruled. W3 ruled. Any survivor is now ordinary work with a known spec,
  not a hedge.

### CLOSE WITH EXTRACTION (7) -- carry the item out, then close

| Issue | What must survive | Where it goes |
|---|---|---|
| **#1067** | The behavioural build-identity check (below, E1). Absent from `.github/RELEASE_CHECKLIST.md` -- grep for "NOT RANKED"/"identity" returns nothing. | new issue |
| **#1102** | Four concrete defects buried in a memo-shaped issue (E5). The memo `docs/memos/MEMO_2026-08-04_1106-and-1102.html` carries the headline numbers (1,194 / nineteen / rarity / significance) but not the boundary case, not `salience_tier`, and not the doc/code disagreement. | new issue |
| **#803** | The content guardrail (E4). Grep across `docs/` finds it nowhere -- it exists only in a GitHub comment. | new issue |
| **#1032** | "the shape is the bug, not the file" -- other `_input` shortcut handlers alongside focused controls (E3). | new issue |
| **#1134** | The deeper version: `pending_events` is a queue any caller can push to with no validation (E2). | new issue |
| **#801** | The lever-legibility reframe (below, in Observations). Design reasoning, no action pending. | this doc |
| **#619** | Its own deferral condition has now been met (below). | this doc |

### DO NOT CLOSE (11)

`#622` `#577` `#802` `#929` `#1018` `#1126` `#1063` `#1064` `#600` `#1132`
-- reasons in Part 1. Plus:

- **#1026** -- keep open, and the triage agrees (close-when-consumed). Recorded
  here because it is worth knowing that the audit inside it lost nothing: all
  three of its route-audit drive-bys were filed (ENTER double-fire -> #1032, now
  fixed; `is_transitioning` -> #1033, open; fade/pause deadlock -> #1034, open).
  What lives ONLY in #1026 is the clerk's counter-argument to Pip's own WHY 4 and
  WHY 5 -- the case that the diagnosis is architecture (test and product do not
  share a boot path) rather than thoroughness, and that under-prioritising QA
  architecture during explosive growth was the CORRECT call. That is the whole
  point of the container and it should be weighed, not inherited.

---

## Part 3 -- extracted material, by category

### Unimplemented ideas

- **E1 -- behavioural build identity beats a printed stamp** (#1067). Build
  identity was confirmed in fifteen seconds by opening the scenario dropdown and
  seeing an amber `[!] NOT RANKED` warning that only existed in code merged that
  afternoon. *"A feature that cannot exist in the previous version is a stronger
  identity check than any string the build prints about itself."* Not in any
  checklist.
- **E2 -- guard the queue, not the caller** (#1134). *"`pending_events` is a
  queue any caller can push to with no validation. This is the first caller found
  doing it wrongly; it is unlikely to be the last. A single guarded entry point
  would make the class impossible rather than this instance."* PR #1144 fixed the
  instance.
- **E3 -- the shape is the bug, not the file** (#1032). A hand-rolled `_input`
  keyboard shortcut alongside a focused Control double-fires unless the handler
  marks the event handled. Fixed in `config_confirmation.gd`; the same shape
  exists elsewhere in `godot/scripts/ui/`.
- **E6 -- verdict progression log** (#929, still open). `verdict_log.jsonl`,
  append-only, one line per verdict change; the snapshot stays derived and small.
  Anti-goal recorded with it: do NOT make the canonical snapshot a log.
- **#619 residue** -- "Fastest X this season" was deferred *"until leaderboards
  (EE-4)"*. Leaderboards shipped and ran a league. The deferral condition is met.
  Not filed: the candidate register is `WORKSHOP_2_BACKLOG` DQ-17 and that is
  where it belongs.
- **#437 residue** -- ADR-0016 names "league-notes format" as an explicit open
  consequence, and #437 was retargeted onto it in July. #1009 (the
  draft-generator ruling) covers blog automation but not league notes. If #437
  closes, confirm league-notes authoring has an owner.

### Design reasoning and rejected alternatives

- **E4 -- the conference/travel content guardrail** (#803, Pip 2026-07-22). The
  highest-value extraction in this lane, and it exists in exactly one place: a
  GitHub comment.

  > NEVER imply wrongdoing by a single real human, or realistic institutional
  > negligence by a real named entity, in any period between sim-start and modern
  > day. Historical contributions to AI capabilities are NOT morally judged --
  > only PLAYER and RIVAL actions carry moral weight.

  With the differential test and its worked examples: OK -- ninjas rappel through
  the ceiling and steal a briefcase; OK -- the return flight is delayed by a
  doomstorm; NOT OK -- a conference volunteer pickpockets an attendee (implies
  the real event had thieving staff); NOT OK -- the venue roof leaks from poor
  maintenance (implies real venue negligence). Plus Claude's accepted pushback
  under Pip's own rule: keep the vignette, drop the real name -- naming a real
  recent person, even one with real convictions, even as a joke, reintroduces the
  exact risk the rule forbids.

  This is a reputational and arguably legal guardrail on content that the game
  intends to generate a lot of. It should be a doc, not a comment on an issue
  about to be closed.

- **The ADR supersession diagnosis** (#1018). *"Each ADR is a correct snapshot of
  a decision at a moment. Nothing carries the edges between decisions. So the set
  accumulates truth-at-a-time and presents it as truth-now."* Plus the reusable
  technique that surfaced it: **writing a glossary forces one meaning per term
  across documents, which is what makes disagreements legible.** Plus the
  post-mortem that motivated the filing: the ADR-0016 pack pipeline was recorded
  as owed in the ADR's own status line and in the runsheet, but was never given
  an issue number, so no lane picked it up. **"Documenting debt is not scheduling
  debt."**

- **Pip's monolith-decomposition deferral** (#622, 2026-07-22). *"Monolith
  decomposition is DEFERRED until the game is out ... do not slow time-sensitive
  development for it, and do not launch decomposition lanes pre-release."* This
  is a standing ruling that any future "let's refactor main_ui" proposal collides
  with, and it currently lives only in an issue comment on an issue the triage
  wants closed. The issue also carries a line-precise LET-DIE map naming what
  must NOT be extracted or polished because the L1/L2 plan screen replaces it.

- **The "cap the button count" design rule** (#1132). Absorbed into the UI arch
  doc, but worth restating because of what kind of rule it is: *"the total
  unlockable set is bounded by the bar, not the other way round"* -- a constraint
  on GAME design imposed by UI width. If a new action would be the eleventh,
  something else becomes a submenu or the action does not ship.

- **Why pdoom-data will not encode pdoom1's vocabulary** (#1102). If pdoom-data
  encodes `frontier_capability` and pdoom1 later renames or splits it, every
  exported pack already in the wild silently means the wrong thing -- no error,
  no failed parse, just numbers attached to a concept that no longer exists. An
  external taxonomy plus a mapping table keeps the vocabulary revisable. Recorded
  because it is a rejected alternative that will look like an obvious improvement
  to whoever next reads the mapping table and wonders why it exists.

### Drive-by opportunities

- **Ladder columns are off by one, today** (#1018). `docs/ROADMAP.md:47` and
  `docs/RELEASE_NOMENCLATURE.md:89` map `v0.14 -> L3`; L3 is already spent. Every
  row below is wrong. Verified on main 2026-08-06.
- **F3's Controls tab is unreachable** (#1132 item 3) -- `debug_overlay.gd:5-7`
  wires three tabs; the fourth needs the panel to be wider or to pop out left.
- **Operations and Office share one icon** (#1132 item 4).
- **`main.tscn:376`'s tooltip still says "advance to next turn ... unused AP" on
  a button labelled `COMMIT THE MONTH >`** (#1037) -- worth a re-check; the AP
  sweep may have taken it, but the turn-vs-month half of that sentence drifted
  separately from AP and is a distinct wrong.

### Observations about feel and player experience

Scarce material, and Pip is mid-UX-push, so these are recorded verbatim rather
than paraphrased.

- **It is lever legibility, not goal legibility** (#801, playtester Rick M). *"I
  get what I need to get the risk to 0% just hard to know what are the things
  that help with that."* The goal lands. The gap is which actions move the
  needle. Onboarding's real job is teaching causal levers (action -> effect), not
  explaining the objective -- so a nudge must NAME the effect ("hire a researcher
  -> lowers doom"), not merely say "do something". The tester independently
  described the fix Pip was already prototyping, which is the strongest kind of
  signal available.
- **Music: fatigue, not dislike** (#802). *"i'm actually digging the music lol"*
  and *"Music is start to break my mind a little now haha"* -- same session.
  Repetition over a long sitting. The design smell underneath: the score rotates
  only on doom thresholds, so a stable-doom stretch loops one track, and the only
  way to force a change is to dev-mode doom upward.
- **A failure found in under an hour by the first external player, having
  survived every internal playtest** (#1126) -- *"because everyone internal has a
  working network and a populated board."* The general form is worth keeping:
  internal testers share an environment, and shared environments hide whole
  classes of defect.
- **Money disappears with no trace** (#1132, raised twice in one session). *"The
  money seems to disappear immediately. I'm noticing maybe we need an action
  log."* Instantaneous actions leave nothing behind.
- **The permalock was fun** (#1132) -- Pip bricked his own run via the control
  overlay and called it *"kind of cool"*, then correctly ruled it out of scope
  because he caused it with a dev tool. Worth noting as a data point about what
  he finds tolerable versus what he finds broken.

### Contradictions

- **The UI architecture doc versus #622's deferral ruling.** The doc plans phased
  UI work; Pip ruled decomposition deferred until the game is out. These are
  probably compatible (taxonomy work is not decomposition) but nobody has said so
  in writing, and the triage read them as the same thing -- which is evidence
  that the next reader will too.
- **Three documents describe an active code path as inert** (#1102).
  `WS3_FINISH_OR_DROP.md:280-282`, `TECH_DEBT_BURNDOWN.md:78-79` and
  `resource_accessor.gd:73-76` all describe the literal-`doom` impact path as a
  dead sink. `events.gd:290-310` intercepts it and reroutes into
  `doom_system.add_stream_input("panic", ...)`. One of those is wrong.
- **ADR-0015 versus what pdoom-data actually supplies** (#1102). `vibey_doom`,
  `stress` and `burnout_risk` map onto `doom` via `variable_mapping.json`, which
  is precisely what ADR-0015 outlaws; it survives only because of the reroute
  above. Separately, #500's spec (`+1 doom per turn`) was already flagged as
  ADR-0015-violating in its own comment thread -- worth carrying that flag onto
  #1090, which inherits the feature.
- **#1129 versus #1134, on what "safe to ship" means** (#1134). #1129 un-gates
  the backslash overlay for release builds because Alpha Tools protects the
  leaderboard. That reasoning covers score integrity and does not cover run
  integrity: Alpha Tools stops a tampered run reaching the board; it does nothing
  to stop the run becoming unplayable. The two questions look similar and are
  not.

---

## Part 4 -- new issues filed, and the bar

**The bar.** An extraction earns an issue only if all four hold:

1. It is **not recorded** in any tracked file -- doc, ADR, code comment, or other
   open issue. (This killed the most candidates. #789's rulings are in a tracked
   build brief; #1068's lesson is a comment in the workflow that broke; #1072's
   reasoning is in the tool's docstring. Reasoning that reached a tracked file is
   not at risk and does not need a ticket.)
2. It names an **action a person could take**, not a sentiment.
3. Reconstructing it later would be **hard** -- it depends on a measurement, a
   ruling, or a session that will not recur.
4. It is **genuinely different work** from the source issue. Where the source
   issue still describes unshipped work, the correct move is DO NOT CLOSE, not
   close-and-refile. Refiling loses the thread and inflates the count -- which is
   the disease, not the cure. Ten of the eleven DO-NOT-CLOSE verdicts would each
   have become a new issue under a sloppier bar.

Six issues met it. They are cross-linked to their sources.

| New | Source | Why it cleared the bar |
|---|---|---|
| **#1147** behavioural build-identity check in the release checklist | #1067 | Different artefact (a checklist, not the stamp fix); verified absent |
| **#1148** single guarded entry point for `pending_events` | #1134 | Class fix versus instance fix; #1134's own "deeper version, worth considering separately" |
| **#1149** sweep `_input`-shortcut-plus-focused-control sites | #1032 | #1032 explicitly declined to scope the sweep |
| **#1150** conference/travel content guardrail as a tracked doc | #803 | Exists in exactly one GitHub comment; reputational risk; #803 is closing |
| **#1151** event-pipeline defects measured in the pdoom-data audit | #1102 | Four code-level defects inside a memo-shaped issue; the memo does not carry them |
| **#1152** ladder column off-by-one in ROADMAP + RELEASE_NOMENCLATURE | #1018 | Live wrongness in two published docs; #1018 is closing and #1049 does not carry it |

Candidates deliberately NOT filed: the #619 "fastest X this season" unblock (its
register is DQ-17); the #437 league-notes residue (raise it when ADR-0016 is next
touched); the #1037 identifier rename (its author already ruled "separate PR, or
not at all"); the #1132 icon collision and F3 tab width (drive-bys, cheaper to do
than to track -- listed above for whoever next opens that file); the #500
ADR-0015 flag (a cross-link comment on #1090, not an issue).

---

*Generated 2026-08-06. Evidence checked against `origin/main`. Companion to
`docs/ISSUE_TRIAGE_2026-08-06.md`; where the two disagree, the corrections in
Part 1 above were measured against the files and this document wins.*
