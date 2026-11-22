# The causality violation -- doom 0, pinned, and the run that would not end

- **Status:** DESIGN CAPTURED (Pip, dictated 2026-08-15 07:15). Structured here,
  not redesigned. Needs rulings on the asks in Section 0 before build.
- **Source:** Pip's dictated answer to "an exploit drove doom to 0 and pinned it
  there for 100 turns; the game did not end. Is that a win, a bug, an ending, or
  something the game should officially have happen?" Quotations below are his,
  lightly cleaned of speech-recognition noise; anything marked **[PROPOSAL]** is
  an agent addition and is his to keep or kill.
- **Consumes:** `decisions/ADR-0002-scoring-turns-survived.md` (the live scoring
  ADR and the mortality guarantee), `WORKSHOP_2_BACKLOG.md` DQ-1 / DQ-27,
  `WORLD_AND_LORE.md` (time-loop framing, event-horizon guardrail),
  `COLD_OPEN_SEQUENCE.md` (the Editor, the Mysterious Helpful Stranger),
  `EASTER_EGGS_BRAINSTORM.md` (fourth-wall register), `UI_ESCAPE_CONTRACT.md`.
- **Touches open issues:** `pdoom1#800` (F8 reporter does not transmit),
  `pdoom1#809` (vestigial victory plumbing / reconcile `docs/adr/0002`).

---

## 0. The asks

One line each, answerable yes or no. Everything below is the reasoning.

| # | Ask | Rec |
|---|---|---|
| A1 | Ratify: doom 0 is not a win, not a bug, but an **authored ending** -- the run is confiscated, not rewarded. | yes |
| A2 | The halting entity is **not** called "time guardians". Pick a name from the Section 7 shortlist, or rule your own. | see 7 |
| A3 | The leaderboard mark is a **mark only** -- an icon and a label, zero score effect. | yes |
| A4 | The marked run sits on the **main board** beside ordinary runs, despite your 2026-07-31 unranked-runs ruling. | needs you |
| A5 | Build the exploit-submission path on **LeaderboardSync's transport**, not on the F8 reporter's. | yes |
| A6 | Robin Hanson appears **only** as an out-of-game email from you, never as an in-game character. | yes |

---

## 1. What the player did, and what it actually means

A player drove P(Doom) to 0 and held it there for a hundred turns. Nothing
happened. The run continued.

**The first thing to say is that this is not a bug.** It is the shipped,
deliberate, test-pinned behaviour of the game. `game_state.gd:775`
`check_win_lose()` ends the run on `doom >= 100` or `reputation <= 0` and on
nothing else; there is no doom-0 branch, `victory` is initialised false and is
never assigned true anywhere in the engine. A test exists specifically to hold
that line -- `test_game_state.gd:128 test_check_win_lose_doom_zero_no_victory`,
whose own comment reads *"DQ-1 / ADR-0002: there is NO victory condition.
doom<=0 must NOT end the game."* DQ-1 removed the victory branch on purpose. The
menu already tells the player the thesis: you can't win, you can only buy time.

So the player did not find a hole in the win condition. There is no win
condition to hole. **What they found is the mortality guarantee failing**, and
that is a different and much more interesting animal.

The live ADR-0002 names the requirement precisely and, having named it, leaves
the mechanism open:

> "With no victory condition, nothing formally ends a stabilized game, and
> lexicographic turns-scoring with immortal runs is a broken leaderboard. **Some
> pressure must grow without bound** so every run ends and turn counts stay
> finite and meaningful... The mechanism is open; the requirement is not."

DQ-1's justification for deleting the victory branch was that this requirement
was already satisfied: *"Proven safe by the exploit sweep: with rival labs
contributing scaling doom (#562), a clean safety run is now finite (dies of
doom, no immortal runs), so removing the win no longer creates an immortal-run
exploit."*

The player has just produced an immortal run. **The claim that justified DQ-1 is
now falsified by observation.** DQ-27 -- "mortality guarantee: where is it
ratified?" -- was resolved on the argument that the guarantee is pinned
executably in the exploit sweep rather than in prose. Two things are worth
noticing about that. The sweep is a bot policy search inside the same engine it
is checking, so it can only find exploits its own policy space can express; and
the bound it enforces (`MAX_TURNS = 10000`) lives in
`baseline_simulator.gd:33` and `replay_simulator.gd:16` -- **the headless
simulators only.** The live interactive game has no turn cap at all;
`turn_manager.gd` reads `state.game_over` and nothing else. A human player is
therefore running unbounded in a way no sweep run ever can.

**[PROPOSAL -- analysis, not design]** This is the "a check must take an input
from outside the system it is checking" rule doing its work, and the player is
the outside input. The sweep derived what to look for from the engine's own
policy space; the exploit lived outside it. That is worth one line in DQ-27
whatever else gets built.

### Why it must not be suppressed

Pip's ruling, and the whole point of the memo: **this should not be patched into
non-existence.** The player did something extraordinary and difficult. Silently
closing the hole spends that moment on nothing. His design instead pays the
player for it, takes the exploit off the board, and harvests the bug report --
all in one beat, in fiction, in the game's own voice.

There is also a hard mechanical reason the run cannot simply be left running.
Score is lexicographic with turns strictly dominant (ADR-0002). An unending run
accrues turns forever. One immortal run does not just top the board, it makes
the board meaningless for that seed permanently. **Something has to end the
run.** Pip's answer is that the ending should be authored rather than
mechanical -- the game notices, and objects.

---

## 2. The flow

Pip's sequence, in order, with the seams named.

**Step 1 -- Detection.** The engine notices a sustained doom-0 state. Not the
instant of touching zero (doom is a float and a one-tick dip is not an exploit),
but a hold: doom at or below the floor across a threshold of consecutive turns.
The player in question held it for a hundred. The threshold is a dial and is an
open question (Section 6, Q3).

**Step 2 -- The halt.** A masked figure appears -- *"the in-game representation
of me"* -- and stops the run. The framing is a warp screen. Pip's copy, which is
close to shippable as dictated:

> "Halt. You have found the boundaries of the simulation and violated the time
> code. We're sending this run to time jail."

> "We're fixing this with interdimensional gaffer tape and returning you to
> correct timelines. Please stand by."

**Step 3 -- The achievement and the unlock.** The run earns **Causality
Violator**: an achievement, plus a permanent profile-level unlock recording that
the player drove doom to zero. Pip's phrase for what they did: they were
*"preheating reality"*.

**Step 4 -- The invitation.** The player is taken to a submission surface:

> "We would like to submit this run to the administrator, as he needs to patch
> the universe so that this can't happen again."

> "Please use the thing to describe the process that you used to drive doom to
> zero, so that we can make sure this never happens again. If you would like this
> exploit noted as yours so that we can credit our records and any patch notes
> will capture this -- fantastic."

Credit is opt-in, exactly as the existing contributor path already offers
("optionally include your name for attribution", `CONTRIBUTOR_REWARDS.md`).

**Step 5 -- The board.** The run lands on the leaderboard carrying a
distinguishing icon and a label to the effect that this run violated the rules of
causality and that the violation is being patched. Pip: *"run gets to the
leaderboard when it hits zero with a bonus marker and an icon, it gets patched."*
And: *"if this reaches the leaderboard, the administrator will be notified, and
they're going to look into it."*

### The seam that matters

The halt **is** the ending. It is not a victory screen and not a defeat screen;
it is a third outcome, and it must not touch `GameState.victory`, which #809 is
in the process of deleting. The run terminates, the score persists through the
ordinary `_persist_and_submit_score()` path, and the outcome is recorded as
`halted_causality` alongside the existing death-cause attribution.

**[PROPOSAL]** Order matters and the existing code already knows why. The
death screen's isolation contract is SCORE FIRST -- the local save happens before
anything that can hang, so *"a later hang / force-quit / error cannot lose it"*
(`game_over_screen.gd:325`). The halt sequence is a cutscene with a text box in
it, which is exactly the sort of thing that can hang or be alt-F4'd. **Persist
the score before the warp screen plays, not after.** The player who quits out of
the cutscene still keeps their run.

---

## 3. Diegetic versus chrome

The line to hold: the fiction may lie about causality, but it must never lie
about whether the game received the player's data.

| Element | Register | Note |
|---|---|---|
| The masked figure, the halt, the time-jail framing | **Diegetic** | It is a character, in-world, in the game's voice. |
| "Interdimensional gaffer tape", "please stand by" | **Diegetic** | Keep the phrasing. See Section 7 -- it is doing more work than it looks. |
| Warp / CRT-glitch treatment of the halt screen | **Diegetic** | The redaction motif and CRT-glitch look already exist (`COLD_OPEN_SEQUENCE.md`); reuse, do not invent. |
| The **Causality Violator** achievement + permanent unlock | **Chrome** | Profile furniture. Real, out-of-fiction, persists across runs. |
| The exploit-description text box | **Chrome, honestly labelled** | The *invitation* is in character. The box is a bug report and must look like one. |
| **Transmission status** ("sent" / "queued" / "failed") | **Chrome. Never diegetic.** | See Section 4. This is the one place the joke must stop. |
| Opt-in credit / name field | **Chrome** | Same consent surface the leaderboard already uses. |
| Leaderboard icon + label | **Chrome, diegetic copy** | The icon is board furniture; the sentence on it can be in-world. |

The masked figure is *"the in-game representation of me"* and that is fine -- Pip
is the game's author and may appear in it. It is worth noting that this is the
only real-person representation the guardrails permit: `WORLD_AND_LORE.md`'s
event-horizon guardrail states that researcher and staff archetypes are
*"flavors, never portraits of real people"*. The author breaking cover to halt
his own simulation is a different act from putting a recognisable third party in
the fiction. That distinction is what Section 6 Q6 turns on.

**Naming hazard, flagged.** Pip said "a masked Uber operator". **"The Operator"
is already taken, twice** -- it is one of the three player archetypes
(`WORLD_AND_LORE.md:51`) and it is the name of the game's central visual
framing, the Operator scene shot from behind at the desk
(`WORLD_AND_LORE.md:204-225`). It is also, as of Pip's 2026-08-08 ruling, the
player-identity field on the leaderboard. The halting entity cannot be called
the Operator without collision. See Section 7.

---

## 4. The submission path, and the mistake it must not repeat

**This is the part with a live landmine in it, so it is stated flatly.**

`pdoom1#800` records that the in-game bug reporter does not transmit. That is
still true in the code as it stands today, and the shape of it is worse than
"does not transmit":

- `godot/scripts/core/bug_reporter.gd` has exactly one persistence path,
  `save_report_locally()` (line 124), which writes
  `user://bug_reports/bug_report_<timestamp>.json` and emits `report_saved`.
- The same file has `format_for_github()` (line 178), which assembles a
  complete, correct, well-documented GitHub issue title and body -- whose text
  even ends *"Submitted via in-game bug reporter"* -- and which **has zero
  callers anywhere in the tree, not even a test.** The game builds the issue and
  drops it on the floor.
- There is no `HTTPRequest` in that file or anywhere near it. The only two files
  in the shipping Godot tree that hold one are
  `godot/autoload/leaderboard_sync.gd` and `godot/autoload/update_check.gd`.

**Correction to the brief this doc was written from: the reporter is bound to N,
not F8.** `keybind_manager.gd:55` reads
`"bug_reporter": {"key": KEY_N, ... "Open Bug Reporter"}`, and there is no
`KEY_F8` anywhere in `godot/`. F8 survives only as a stale docstring at
`bug_report_panel.gd:7`. Worth a one-line fix in the same lane, because
`docs/KEYBOARD_REFERENCE.md` lists neither.

**What #800 already got was honesty, not transmission**, and the distinction is
the whole lesson. `bug_report_panel.gd:182` now says:

> "Thanks! Saved locally to: `<path>`. This build does not send reports
> automatically yet -- please email that file to team@pdoom1.com so it reaches
> us."

The confirmation text used to imply an auto-filed GitHub issue; that lie was
fixed. The missing transport was not. (`docs/CONTRIBUTOR_REWARDS.md` still
carries the old promise -- *"saved locally and will be processed into a GitHub
issue"* -- and should be corrected too.)

**An exploit-submission flow built on `BugReporter` inherits all of that**, and
it would fail in the worst possible place: this design's entire harvest value is
the player's description of how they broke the game, given once, in a moment
they will not repeat. Asking them to find a JSON file and email it is not a
harvest.

### What to build on instead

The game already contains a working, consent-gated, failure-tolerant outbound
path, and it is the leaderboard's: the `LeaderboardSync` autoload, invoked from
`game_over_screen.gd:_maybe_submit_remote()`. It is live -- a league ran on the
real board on 2026-07-31. Its properties are exactly the ones this flow needs,
and every one of them was paid for by a previous incident:

- **Local save is authoritative and never gated.** The score exists on disk
  before any network call; the remote POST is fire-and-forget and *"internally
  bulletproof against network failure, so nothing here can crash or freeze the
  end-game"*. The doctrine line in `leaderboard_sync.gd` is the one to inherit
  verbatim: *"the local score save is NEVER gated by any of this -- consent
  covers only the remote upload."*
- **A durable outbox, not a retry timer.** `user://pending_scores.json` is
  written *before* the POST and cleared only on server ack, flushed at next
  launch; the server dedups on `entry_uuid`. Its header records why: a
  force-quit at the defeat freeze killed the in-flight POST and the score
  reached the server on **zero** occasions.
- **`PROCESS_MODE_ALWAYS`** so an in-flight request survives a paused tree, with
  an 8-second timeout.
- **Consent is explicit and stateful**, via the pure, unit-tested
  `consent_flow_state()` helper (`submit` / `ask` / `remind` / `silent`) and the
  privacy ruling of 2026-07-26.
- **Silence when unconfigured.** Missing or malformed config leaves it disabled
  and never errors -- dev builds and forks do not nag.

**[PROPOSAL] The rule for this flow, in one line: the exploit report rides the
score submission.** It is generated at the same moment, by the same screen, for
the same run, under the same consent flow, through the same outbox. Building a
second transport is how the first one ended up not existing.

**The receiving end already exists too**, which removes the biggest unknown:
`pdoom1-website` ships a live bug intake at `netlify/functions/report-bug.js`
(`POST /api/report-bug`, forwards to GitHub via `repository_dispatch`) and a
PHP fallback at `public/bug-submit.php` (emails team@pdoom1.com, with honeypot,
throttle and size limits). Its own documentation says the endpoint is
*"shared by Web and Game"*. **The game-side client is the only missing piece.**
That is also why `pdoom1#1057` is tracked as a duplicate of #800.

Four consequences follow, and they are the build contract:

1. **Consent must be re-taken, not inherited.** The existing consent covers a
   name, a lab name and two integers. This flow uploads **free text the player
   wrote**, which is a materially different disclosure. Precedent is already
   set: the launch ping honours `send_launch_ping` rather than
   `submit_scores_global` specifically because it carries no identity. This
   needs its **own named consent key** in `game_config.gd`, defaulting false.
2. **Pin the payload with a whitelist test.** `test_update_check.gd` already
   does exactly this for telemetry. It is the only mechanism that stops a
   future field quietly widening what leaves the player's machine.
3. **Keep it off the deterministic path (ADR-0006).** `LeaderboardSync` is
   called only from the game-over and leaderboard screens, never from sim, RNG
   or replay. The halt fires from the sim's turn loop, so the submission must be
   raised as a signal and actioned by the screen -- not called where it is
   detected.
4. **The player must be told the truth about transmission.** If it queued, say
   queued. If it failed, say failed and say where the file is. The fiction may
   be sending the run to time jail; the status line underneath says
   `[QUEUED] report will send when online`. **This is the one element of the
   whole design that is not allowed to be funny**, because #800 is precisely a
   case of a reporting surface that looked like it worked.

**[PROPOSAL]** Fixing #800 is not a dependency -- riding LeaderboardSync routes
around it. But once the exploit flow visibly transmits, a bug reporter that
visibly does not becomes a much more embarrassing object, and by then the client
is written. **Do #800 with it, not after it**: same transport, same consent
pattern, same endpoint. The prior estimate for #800 alone was 3-5 days
cross-repo; most of that cost is shared with this work.

**Unrelated but found on the way, and someone should decide about it:**
`godot/data/leaderboard_config.json` is committed and not gitignored, and it
carries the API token that ships inside every public build. Its own comment
calls it *"a low-value shared secret... acceptable for alpha; rotate if the
board is abused."* An exploit-submission endpoint using the same pattern
inherits that posture. Fine for alpha, worth a deliberate ruling before any
wider release.

---

## 5. Where this sits against the ADRs

It contradicts nothing, and that is worth demonstrating rather than asserting.

**ADR-0002 (live, `decisions/ADR-0002-scoring-turns-survived.md`): there is no
victory condition.** Honoured. The halt is not a win. The player is not
congratulated for solving alignment; they are stopped, tidied up, and returned
to the correct timeline. Nothing sets `victory = true`, and the
`doom<=0 must not end the game` test remains true in spirit -- doom 0 still does
not end the game. **A sustained doom-0 hold ends the run, and it ends it by
authored intervention rather than by win check.** That is a new, third
termination route and it should be spelled that way in code so nobody
reintroduces the victory branch by the back door.

**Note on the stale copy.** `docs/adr/0002-win-condition-survival-spine.md` still
says *"Victory: doom <= 0"* and calls it *"a real but rare apex victory"*. That
file is **wrong and known to be wrong**: it was never marked Superseded, the
2026-08-03 ADR/DQ audit flags it, and #809 is open to fix it. Anyone reading only
`docs/adr/` inherits a dead win condition. This design must not be read as
reviving it. **[PROPOSAL]** Landing this work is a natural moment to close #809,
since it forces the question anyway.

**ADR-0002's scoring rules: flows only, never stocks; no new blended terms.**
This is why ask A3 matters. Pip said "bonus marker", which is ambiguous between a
visual mark and a score bonus. A score bonus is barred twice: once by ADR-0002
("any end-state stock term is an anti-sink... rejected on sight") and again by
the achievements contract, which is explicit that achievements are *"RECOGNITION,
never in-run reward"* and that *"a proposed achievement with an in-run effect is
rejected on sight"* (`godot/autoload/achievements.gd`). **Recommendation: the
mark is an icon and a label, and the score is the ordinary turns/doom-integral
tuple.** The distinction costs the player nothing -- the icon is rarer and more
interesting than any number would have been.

**ADR-0004 (self-describing data).** The halt copy, the achievement definition
and the leaderboard marker are all content, and content is JSON here. Any new
data file carries its own `schema_type` declaration; nothing infers schema from
the directory. The achievement itself needs no new file -- it is one more entry
in `DEFINITIONS` in `achievements.gd`, which is where the existing nine live.

**The achievements system fits as-is.** It is observer-only, listens to
`game_state_updated` snapshots, persists per-profile to
`user://achievements.json`, records first-unlock date, and unlocks are permanent.
Pip asked for "an achievement plus a permanent unlock in your thing". That is
what this node already does, with no new machinery.

**[PROPOSAL] Flavour text, in the established register** (bureaucratic deadpan;
compare *"Doom passed 90. You filed the paperwork anyway."*):

> **Causality Violator** -- "You held it at zero for a hundred turns. Somebody
> had to come and get you."

**`UI_ESCAPE_CONTRACT.md`.** The halt screen is an overlay panel and inherits the
no-dead-ends contract: it must provide its own intrinsic exit, and
`test_ui_no_dead_ends.gd` auto-discovers it if the scene is named with a `_panel`
or `_modal` suffix or the script exposes `build_screen()`. **Esc must not
cancel the halt** -- the run is over either way -- **it must advance to the
leaderboard**, and it must not silently discard an unsent description. Name it
`causality_halt_panel.tscn` and the guard picks it up for free.

---

## 6. Open questions

**Q1 -- What is the halting entity called?** Pip: *"I don't think I want to use
actual time guardians. We can probably use something that's in-universe and a bit
more meta."* This is the largest open question because the name sets the register
for every line of copy. Shortlist in Section 7. **Blocking on copy, not on
build.**

**Q2 -- Does the marked run go on the main board?** Pip's dictation says yes,
with an icon. **His own earlier ruling says no.** On 2026-07-31 he ruled that
unranked runs never touch the board, including the local one, because a run
played under different rules is *"silently incomparable with every Standard score
sitting beside it"* -- the reason scenario and alpha-tools runs are excluded at
`game_over_screen.gd:340`. A causality-violating run is the strongest case of
incomparability the game has produced. The counter-argument is that the icon
makes it *loudly* comparable rather than silently incomparable, which is exactly
what the earlier ruling was protecting against, and that hiding the best story
the game has ever generated is a poor trade. **Three options: main board with
icon; a separate Violations board; main board but sorted outside the ranked
positions (shown, not ranked). Pip rules.**

**Q3 -- What is the detection threshold?** How many consecutive turns at doom 0
before the halt fires, and is it doom exactly 0 or doom below some epsilon? Too
tight and a lucky mid-game dip triggers a cutscene; too loose and a player sits
in a solved game for an hour. The observed run held for 100. **[PROPOSAL]** Well
under 100 -- the player has demonstrably solved it long before then, and the beat
lands better while it still feels like an achievement rather than a chore.
Suggest something in the 10-25 range, tuned once by watching one real run.

**Q4 -- Does the halt fire once per profile, or every time?** The first
encounter is a genuine surprise; the fifth is an obstacle between a player and
the leaderboard, and a player who has learned the exploit can now farm it.
**[PROPOSAL]** Full cutscene on first violation per profile, abbreviated
acknowledgement thereafter -- but the achievement is already permanent and
first-unlock-dated, so the second violation has nothing left to give. This may
argue for the halt being unskippable exactly once and skippable forever after.

**Q5 -- What happens to the seed?** Pip's fiction says the exploit gets patched
so *"this can't happen again"*, and seeds are timelines in this game's canon. Is
that purely flavour, or does the violated seed acquire real state -- a note on
the board, a changed opening, a refusal to serve that seed again? The fiction is
making a promise here that the mechanics can either keep or quietly not keep.
**Not urgent, but it should be answered before the copy ships**, because
"returning you to correct timelines" reads as a mechanical claim to an attentive
player.

**Q6 -- Robin Hanson.** Pip raised, half-seriously, a decision-theory joke and
emailing Robin Hanson: an administrator who *"traded off too many sacred
values"* and, rather than deal with it, shunts you into a timeline where you
cannot do this again. (The transcript is rough here; the shape is clear, the
wording is not.) **Two separable things, and they have different answers.** The
*decision-theory joke* is squarely on-brand -- the easter-eggs doc already files
Roko's basilisk as a $0.00 ledger entry and calls the accounting treatment the
joke. **A named real person as an in-game character is barred** by the
event-horizon guardrail: archetypes are *"flavors, never portraits of real
people"*. **Recommendation: keep the decision-theory register, do not name him in
the game, and email him as yourself if you want to** -- that is a delightful
thing to do and costs the fiction nothing. His closing thought is worth keeping
in the file either way, because it is the design's own thesis stated as a joke:

> "The problem of trying to fight people with the ability of time travel and
> narrative causal selection on their side is that... well, the troubles become
> evident."

**Q7 -- Does the halt need to close the exploit?** It does not, and that is a
feature: the fiction absorbs the exploit while the fix is pending, so a shipped
build is never embarrassed by a hole it has not patched yet. But it also means
**the mortality guarantee is now backstopped by a cutscene**, which is a real
architectural statement and should be made deliberately. DQ-27 deferred writing
the ratifying ADR until mid/late game felt designed rather than accidental. **A
player just found the edge of the map. That may be the trigger DQ-27 was waiting
for.**

---

## 7. Naming the halting entity -- shortlist [PROPOSAL]

Pip asked for options and rejected "time guardians" as too literal. The house
convention for bodies is a dry formal name plus the flat nickname people
actually use (`SEED_GOVERNANCE_NAMES_YESAND.md`: "the Panel has questions",
"nobody says DOOM aloud").

**The observation that should drive this: "interdimensional gaffer tape" is a
film-production metaphor, and it is the best line in the memo.** A gaffer is a
crew member. So is an editor -- and **the Editor already exists in this game's
canon** as the benevolent-and-withholding hand of `COLD_OPEN_SEQUENCE.md`, the
one who rigs the passcode and redacts the lore, explicitly because *"future-you
can't tell past-you too much without breaking the timeline"*. **The Editor is
already the timeline-integrity authority.** He is in-universe, he is meta, he is
established, and he has never once been called a guardian.

That gives a coherent register: the simulation has a production crew, they are
in blacks, they are masked because crew are not supposed to be in shot, and they
have come on set to fix continuity with tape.

| Formal | Nickname | Notes |
|---|---|---|
| **The Editor** (existing canon) | "the Editor" | Cheapest and strongest. No new lore, and it pays off the cold open. The hand that helps and redacts now also intervenes. |
| Office of Continuity | **"Continuity"** | "Continuity would like a word." Doubles as film-crew continuity and timeline continuity; deadpan, meta, not literal. Pairs with gaffer tape and the Editor. |
| Bureau of Narrative Causal Selection | "the Bureau" | Lifts Pip's own phrase from the closing line. Most decision-theory-flavoured option. |
| Standing Panel on Temporal Integrity | "the Panel" | Maximum house-style bureaucratic deadpan -- but "the Panel" is already spoken for in the governance roster. |
| The Second Shift | "the Second Shift" | The crew who come in after hours to fix what the day shift broke. Most mysterious, least explanatory. |

**Recommendation: the masked figure is the Editor, and "Continuity" is the desk
he works for.** It reuses canon instead of adding to it, it makes the gaffer-tape
line load-bearing rather than decorative, and it keeps the metaphor consistent
from the cold open to the halt.

---

## 8. Cost, and what it buys

Sized in the register of the easter-eggs doc (drive-by / small / bigger).

| Piece | Cost | Why |
|---|---|---|
| Detection + third termination route | **small** | A counter on the doom-0 hold, a `halted_causality` outcome, one new branch out of `check_win_lose()`. The hard part is not code, it is Q3's threshold and making sure it cannot be confused with the deleted victory branch. |
| Achievement + permanent unlock | **drive-by** | One entry in `DEFINITIONS` in `achievements.gd`. The persistence, the first-unlock date and the profile scope already exist and already have tests. |
| The halt screen (copy + warp treatment) | **small** | The copy is written -- it is in Section 2. The CRT-glitch and redaction motifs already exist as visual language. Rises to **bigger** only if the masked figure needs new art rather than a silhouette. |
| Exploit-submission client | **small-to-bigger** | One text field, one payload field, one consent key, one whitelist test -- *if* it rides `LeaderboardSync`'s shape. It becomes **bigger** the moment anyone proposes a separate transport. The honest framing: this is the #800 client, which was costed at 3-5 days cross-repo, and this design is the reason to finally write it. |
| Server-side receipt + administrator notification | **already built** | `pdoom1-website` `/api/report-bug` forwards to GitHub via `repository_dispatch`, with a PHP email fallback; its docs say it is shared by Web and Game. Marking the payload as a causality violation so it can be routed or labelled is a small addition, not a new service. |
| Leaderboard icon + label | **small** | Board furniture plus a marker field on the entry. Gated on Q2. |

### What it buys

**One:** the mortality guarantee acquires a backstop that does not depend on
balance tuning holding forever. Every future exploit that stabilises the game
lands in the same net, whether or not anyone anticipated it -- which is the
opposite of the position DQ-1 left the game in, where the guarantee rested on a
sweep that could not see this class of failure.

**Two:** a bug-intake path with the best conversion rate the project will ever
get. The player is asked to describe an exploit at the exact moment they are
proudest of it, by a game that just staged a cutscene in their honour, with
opt-in credit in the patch notes. Compare the current alternative, which is
hoping they file a GitHub issue.

**Three:** it is funny, it is in-universe, and it is the kind of thing players
screenshot. Pip's own summary of why it works, and it is the right summary:

> "It fits inside the game diegetically, it keeps the humorous tone, and it's a
> great way to increase engagement."

**And one thing it costs, stated plainly:** the game will now formally recognise
an ending that is neither victory nor defeat, in a project that has spent
considerable effort establishing that there is no victory. The halt must
therefore never be dressed as a win. The player is not congratulated for saving
the world. **They are congratulated for breaking the game, and then the game
takes the run away from them and tapes the hole shut.** That is the joke, and it
is also, precisely, the ruling.

---

*Captured 2026-08-15 from Pip's dictation. Structure and marked proposals: agent.
The design, the sequence and the good lines are his.*
