# The backlog is the teacher -- why P(Doom)1 hands you more than you can do

> **Status: design thesis, captured. Not an ADR, nothing ruled.** Dictated by
> Pip on the morning of 2026-08-15 and written up the same day. It is the
> *rationale* under mechanics that already exist -- ADR-0011's workstream
> backlog and typed Attention, ADR-0012's event-response taxonomy, ADR-0003's
> Liability Ledger -- rather than a proposal to build anything new. Its value is
> that it says what those mechanics are FOR, which none of them currently state.
>
> **Provenance.** Pip's phrasing is preserved verbatim in quotes and is the
> load-bearing part. Everything marked **Proposal** is this seat's addition and
> carries no ruling. The raw recording is not in this repo.
>
> **Downstream of** `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md`
> and `docs/adr/0002-win-condition-survival-spine.md`. It must not, and does not,
> contradict either. See section 5.

## Read this first: "backlog" is three things

The word is overloaded in this repo, and this document is about the *idea* that
spans all three. Where a section constrains a specific mechanic, it names it.

| Sense | The thing | Where it lives |
|---|---|---|
| **Workstream backlog** | The standing list of directed work you can commit people to. `backlog.json`, 8 entries. "There's always a backlog" -- the file that makes idle staff impossible. | ADR-0011 s3; `godot/data/workstreams/backlog.json` |
| **The diegetic to-do list** | Deferred liabilities, standing offers and unhandled windows, accumulating past what the UI foregrounds. There is no single object; **deferred events ARE Ledger entries.** | ADR-0012; `ledger.gd`, `window_resolver.gd` |
| **The action queue** | The un-committed month plan on the PLAN screen. Cleared with `C`, undone with `Z`, and flushed every turn. **This one is supposed to be clearable.** | `docs/CONTROLS.md`; `plan_controller.gd` |

**Nothing in section 4 forbids the `C` key.** The action queue is a scratchpad
for one month's intent; clearing it costs the player nothing and teaches nothing.
The unclearable thing is the mountain behind it.

**New vocabulary warning.** "Eisenhower matrix" and "Peter principle" have zero
prior hits in this repo. They arrive with this document. Neither renames an
existing mechanic: the player's verbs remain HANDLE / DEFER / IGNORE (ADR-0009)
across the four event classes (ADR-0012). Note also that **"technical debt" is
already taken** -- a legacy 0-100 scalar on `game_state.gd` (issue #416) that no
ADR blesses. This document says "debt" only in Pip's sense of the Ledger.

---

## 1. The claim

The design starts from the Peter principle and pushes one step past it.

> "the Peter principle says an operator is gonna get either better at, like an
> operator is either gonna get more effective at their work or they're gonna get
> promoted and then be given more tasks, right? So kind of like a corollary to
> that is at some point an operator will get promoted into a role where there
> are more tasks than can be done."

That is the corollary the game is built on: **overload is not a failure state,
it is the terminal state of a working career.** Everyone competent arrives
there. What happens next is the subject.

> "And if that operator is diligent, they might just like try to get it all
> themselves, right? But there's a point where you're like, the unfair or
> impossible to meet amount of demands placed on me are too great. And
> eventually you learn to like communicate that fact. And if you're in a
> workplace that is at all responsive, then like your workload will be regulated
> to some extent, right? Either, or like you'll be, or you'll be regulated."

Note the sting in the tail. The responsive workplace regulates your load; the
unresponsive one regulates *you*. Both are outcomes the simulation should be
able to produce.

And the behaviour that precedes learning any of this:

> "before someone learns effective delegation or like how to correctly triage
> and then abandon tasks in those environments, your backlog will grow, right?
> You're like, oh, I'll get to this later, something more urgent has come up.
> Oh, I'll get this to this later, something more urgent has come up."

Three named competencies, in ascending difficulty: **delegation, triage,
abandonment.** Abandonment is last and hardest, and it is the one the game is
actually trying to teach.

The claim in one sentence: **the growth of your backlog is a measurement of a
skill you have not learned yet, and the game exists to let you learn it by
paying for it.**

This is the same instinct that produced ADR-0011, from the other side. Pip's
originating quote there was *"I have never been around unassigned workers
before, because there's always been a backlog"* -- which is why idle staff do
not exist. This thesis says the founder is in that condition too, permanently,
and that the condition is the curriculum.

## 2. The mechanism

The mechanism is a deliberately laid trap, offered as often as possible.

> "Every time a player thinks I will do this later, something more urgent has
> come up, then they're falling into an Eisenhower matrix trap. We wanna give
> them as many of those options as possible."

An Eisenhower-matrix trap, as Pip is using the term: the player defers on
**urgency** while telling themselves they are deferring on **importance**. The
sentence "something more urgent has come up" is true and is also the whole
error. Urgency is legible, arrives with a deadline attached, and is supplied by
other people. Importance is illegible, silent, and supplied only by you. A game
that presents plenty of urgent things will harvest that confusion reliably.

So the design does not *guard* against the trap. It stocks the shelves with it.

The exit condition is not "stop deferring". It is **deferring for the right
reason**:

> "when players gain the strategic capability to not fall into Eisenhower matrix
> traps by saying to themselves, I'll do it later, something more important has
> come up because they're recognizing the trade-offs, then we will have
> emergently taught them how to get out of Eisenhower trapping themselves out of
> like the strategic outcomes they need"

The two sentences are one word apart -- *urgent* becomes *important* -- and that
one word is the entire lesson. This has a hard implementation consequence:
**the surface behaviour of a novice and an expert is identical.** Both press
DEFER. The game therefore cannot detect mastery from the action, only from what
the run does forty turns later. Which is exactly why the scoring works the way
it does.

> "the strategic measurements we have for that are do you survive longer than
> anyone else many turns down the track"

**Teaching is emergent, not instructional.** Pip's word is "emergently". Nothing
here licenses a tutorial explaining the Eisenhower matrix, a "your backlog is
growing" nag, or an advisor who tells the player to triage. Being told is not
the same skill as having paid.

### The trap is already encoded in the effort economy

The strongest existing support for this thesis is a rule that was ruled for
other reasons. ADR-0011 amendment (e) types every Attention spend as **PLANNING**
(queueing strategic work, direction, approvals) or **OPERATING** (response
windows, hiring, travel, interviews), and makes **overflow asymmetric**:

> operating may eat planning; planning may never eat operating.

That is the Eisenhower trap expressed as an economy. The urgent lane can consume
the important lane and never the reverse -- which means a player who simply
responds to what arrives will find their planning hours quietly gone, without
ever making a decision they could point to. **No new mechanism is needed to
deliver the thesis's core loop; it is shipped.** What is missing is the
rationale, which is this document, and the measurement, which is section 6.

### The infrastructure case is the same shape, on a longer fuse

Pip extends the argument from tasks to capital, and the extension is what makes
it a design thesis rather than a mood:

> "you start to see the impact of not investing in infrastructure when the comp,
> like not when infrastructure is cheap, not when we're in zero interest rate
> environments and things are flowing, but when actually we're like, oh, hold
> on."

The reckoning is displaced in time from the decision, and the displacement is
the point. Deferring investment is *correct-looking* for as long as conditions
are loose, and the bill arrives when they are not.

> "some of these bills will fall due in ways where we simply will not be able to
> metabolize up and down the economic chains and the ripples from those. Going
> to give you competition pressures at times when it is not convenient for you
> because your peers with the same level of insight as you are already acting as
> well and there are more of them than there are of you."

Two mechanisms are named there and they should be kept separate:

- **Correlated timing.** Bills do not fall due at random. They fall due when
  conditions tighten -- which is when everyone else's fall due, which is why you
  cannot metabolise them. In Ledger terms (ADR-0003) this is a claim about
  **fuse correlation**, not about interest rates.
- **Correlated rivals.** Your peers share your insight. Acting on a good idea
  buys no edge if the idea is legible to everyone, and *there are more of them
  than there are of you*. The inconvenient moment is structural, not a dice roll.

This lands cleanly on ADR-0005 (author causes, never outcomes): inconvenient
timing is what correlation produces, not what a schedule specifies.

**Caution, and it cuts against the passage above.** ADR-0003 warns that if
liabilities are insufficiently heterogeneous the game degenerates into an
**"inevitability queue"**, and requires a lean-ledger / clean-hands path to
survive at the cost of tempo. Correlating fuses pushes directly toward the
failure mode ADR-0003 names. Correlation is the honest model; heterogeneity is
the playable one, and the tension between them is unresolved here.

**Note also: there is no infrastructure mechanic.** "Infrastructure" currently
exists only as an upgrade-category string and a proposed staff bucket. This
section is a claim about how such a thing should behave if built, not a
description of anything shipped.

### The framing line

> "At some point we might have to figure out a way to let the player delete
> their backlog, but in some ways what's going to happen is the game is going to
> be a triaging of action against a mountain of debts, some of which are imposed
> on you externally and none of which are fair. Because I'm not representing a
> fair game here, I am simulating an actual challenge."

**"I am not representing a fair game here, I am simulating an actual
challenge"** is the sentence to keep. It is the acceptance test for every
balance argument that opens "but that isn't fair to the player". Unfairness is
not a tuning defect here; it is the modelled quantity. The design owes the
player **legibility** and **a real chance** -- a different debt from fairness,
and one the Ledger cascade already pays (ADR-0012's register: tragedy, "I saw it
coming").

"A triaging of action against a mountain of debts" is also, almost exactly,
ADR-0003's phrase for where skill lives: **"Triage-in-time"**, skill expression
as debt portfolio selection and sequencing. The thesis and the flagship system
were reaching for the same sentence a month apart.

Note the source split: *"some of which are imposed on you externally"*. The
mountain is not all self-inflicted. A backlog you built by over-committing and a
backlog handed to you by the world should both be present, and the player should
not always be able to tell which is which at the time.

## 3. What this implies for the plan screen and the queues

Constraints on anything touching the PLAN screen, the response windows, or the
workstream backlog.

1. **Volume of offers is a feature, to be tuned upward.** *"We wanna give them
   as many of those options as possible"* is a design instruction. A plan screen
   the player can comfortably clear is failing to present the trap. This already
   agrees with the ruled card-hand principle that the hand must show **more than
   you can afford to play**.
2. **DEFER must stay cheap at the moment of choice and expensive later.** It
   already does -- ADR-0012 mints a Ledger entry, ADR-0013 prices the carrying
   cost through the single shared engine -- and this thesis is why it must stay
   that way. The player must be able to make the mistake.
3. **But deferral must not be invisible.** Pip has already flagged this in
   playtest: *"Deferrals are UI-INVISIBLE"* (`PLAYTEST_v0.13.1_NOTES.md`), with
   a want for a deferred item to lurk as a card or show as a visible Ledger row.
   These pull against each other and the resolution is a *timing* one: the cost
   should be **discoverable on the Ledger**, not **quoted at the point of the
   click**. Visible accumulation teaches; a price tag on the button instructs.
4. **The four-class taxonomy is load-bearing and must survive.** Un-snoozable,
   deferrable, standing offer, no-action-correct (ADR-0012). Abandonment is only
   learnable if **no-action-correct** genuinely exists and is genuinely not
   punished. If every ignored item eventually bites, "abandon" is not a strategy
   but a slower loss, and the third competency cannot be taught.
5. **Items must be allowed to fall out of view.** Already ruled diegetic --
   *"Doom Arrives With Your To-Do List Being Infinitely Long Still is a real
   possibility that I'm not shy of playing into."* This thesis supplies the
   justification: a backlog you can fully see is one you can fully plan against,
   and planning against it is the novice behaviour the trap depends on.
6. **Externally-imposed load needs its own source.** Some of the mountain must
   arrive unbidden. If everything traces to a player choice, the game teaches
   "be careful what you start" -- a smaller and less true lesson.
7. **Infrastructure-style decisions need a fuse long enough to be forgotten.**
   For the deferred-investment lesson to land, the gap between skipping and
   paying must exceed the player's memory of the choice. A two-turn consequence
   teaches cause and effect; a twenty-turn one teaches what this is about.
8. **The asymmetric overflow rule is thesis-critical and should not be softened
   for comfort.** If a future quality-of-life change lets planning hours be
   protected from operating overflow by default, the trap stops being reachable.

## 4. What the game must NOT do

Stated as prohibitions because each would quietly delete the lesson while
looking like a quality-of-life improvement.

- **Never make the diegetic backlog fully clearable in a state the player can
  reach and hold.** The moment a diligent player can reach zero and stay there,
  the game has confirmed the novice hypothesis -- that enough diligence beats
  the load -- and has taught the opposite of the thesis. Inbox zero must be
  *unreachable*, not merely hard. (Again: this is not about the `C` key.)
- **Never let clearing the backlog become a scoring path.** ADR-0002 already
  forbids stocks at death; this adds that "items completed", "queue length" or
  "ledger cleared" must not become score terms, tiebreaks or achievements.
  Rewarding throughput rewards the trap.
- **Never let a Ledger entry be discarded without being paid.** No write-off
  verb, no amnesty. Compounding Ledger interest is the standing candidate for
  ADR-0002's **mortality guarantee**; a free clear-the-ledger action would
  contradict it directly.
- **Never explain the trap in-game.** No triage tutorial, no backlog-growth
  warning, no advisor telling the player to delegate.
- **Never make the correct choice legible at the point of choice.** If the UI
  can distinguish urgent from important for the player, the player never learns
  to.
- **Never punish no-action uniformly.** ADR-0012 says some events deserve
  nothing. If that class shrinks in practice, abandonment stops being teachable.
- **Never price the mountain as fair.** No mechanic whose stated purpose is to
  make load proportionate to capacity. *"I am not representing a fair game
  here."*
- **Do not cull the load to reduce anxiety.** Items may fall out of view because
  that is what real backlogs do; they may not be deleted because a designer
  worried the screen looked stressful.
- **Do not introduce a "workload" resource to model any of this.** ADR-0003's
  no-parallel-economy rule stands: the thesis is delivered through Attention,
  the Ledger and existing resources or not at all.

**Proposal (this seat, not ruled).** The cleanest way to hold all of this is a
single invariant the sim can check: *the expected arrival rate of actionable
items exceeds the founder's maximum achievable throughput at every tier of
capability.* Ops staff reduce the founder-price of routine actions and
automation removes whole classes over time (ADR-0011 s6); both may raise
throughput a great deal, and neither may raise it past arrival. That converts
"the backlog must not be clearable" from a thing we remember into a thing a test
can fail on -- the difference this ecosystem keeps learning matters. Whether it
is worth building is Pip's call.

*(Correction to an obvious-looking version of that worry: managers are **not** a
throughput risk here. ADR-0011 explicitly rejected managers as output
multipliers -- they are interrupt shields whose value is founder-attention
arbitrage. The clearing risk runs through ops and automation, not management.)*

## 5. Connection to the survival spine

The thesis and the spine meet at one joint: **the lesson is unobservable in the
moment and measurable only in duration.**

- `ADR-0002-scoring-turns-survived.md` makes **turns survived strictly
  dominant**, with a doom-integral tiebreak, flows only, no stocks at death,
  post-mortem reveal only. Pip's *"do you survive longer than anyone else many
  turns down the track"* is that rule restated in plain language, and this thesis
  supplies its rationale: turns-survived is the only measurement that can tell a
  wise deferral from a lazy one, because the two are identical when made.
- **No live score ticker** matters more under this thesis than it did when it was
  ruled. A running score would give the player exactly the point-of-choice
  feedback section 4 forbids.
- `docs/adr/0002-win-condition-survival-spine.md` frames the game as primarily
  survival / high-score, with doom-to-zero a **rare apex victory** and
  **graceful concession** an owed, unbuilt mechanic. This thesis needs neither
  the apex victory's existence nor its absence; it needs only that the ordinary
  outcome is measured in duration, which both ADRs assert.
- **The known collision, stated so nobody re-derives it.** The two ADR series
  give opposite answers on whether a victory condition exists (pdoom1#809; see
  the index note in `docs/game-design/decisions/README.md`). **This document
  takes no position** and is compatible with either resolution, because it uses
  only the claim both share: runs are ranked by how long they last.
- **Graceful concession is this thesis's natural endgame.** Conceding is
  abandonment applied to the whole run -- the third and hardest competency,
  performed at the top level. If it is built, it should read as the mature move
  it is and never as a forfeit.

## 6. What would falsify this in playtesting

The thesis makes empirical claims. **Proposal: this seat's falsifiers, offered
for Pip to accept, cut or replace.**

- **The lesson does not transfer.** If experienced players' deferral *patterns*
  do not change with play count -- same items deferred, same ordering, merely
  faster -- nothing is being taught and their longer runs are explained by
  something else. This is the central falsifier, and it needs logging of *which*
  items are deferred, not how many.
- **Turn count does not separate the behaviours.** If runs that abandon
  aggressively and runs that grind everything survive equally long, the scoring
  spine is not measuring the skill this thesis claims it measures, and section 5
  fails.
- **A dominant clearing strategy exists.** If some build -- enough ops staff,
  enough automation -- holds the queue near empty and wins, the backlog is not a
  teacher but a phase the player exits.
- **The mountain is homogeneous.** If liabilities are similar enough that
  sequencing them stops being a real decision, ADR-0003's **inevitability queue**
  has arrived: the player is watching a countdown, not triaging. Symptom to
  watch for is playtesters describing the Ledger as a schedule rather than a
  portfolio.
- **The trap is not tempting.** If testers never report the "I'll get to this
  later" feeling -- if deferral feels obviously right or obviously wrong rather
  than *seductive* -- the traps are mis-costed and the design is not producing
  the confusion it depends on.
- **Overload reads as noise, not pressure.** If players call the queue cluttered,
  buggy or unfinished rather than oppressive, the mountain is failing to
  communicate as a mountain, and the fix is presentation, not volume.
- **Players quit at overload rather than through it.** Some attrition is
  intended; Pip's own gloss is that a player may stop *"because they recognize at
  least partially that their mind has been caught by one of the labyrinths that
  the world sets for them and this is the one that I built."* But if the modal
  new player abandons at first overload and never returns, the lesson has no one
  left to teach and the on-ramp needs work even though the thesis is intact.
  Distinguish **quit-in-recognition** from **quit-in-bewilderment**; only the
  second is a design failure.
- **The infrastructure fuse is too short.** If testers can name the decision that
  caused a late-run bill, the displacement is not working. Not being able to name
  it is the intended experience -- though it sits in tension with ADR-0003's
  **death attributability** goal ("this is the bill for turn 2"), and which of
  those two wins is an open call this document does not make.

A note on method. Several of these need **an input from outside the system being
checked**: self-reported "I learned to triage" is a proxy, the deferral log is
the state. And where a falsifier can be settled by asking a playtester, ask them
-- an inference about a person's behaviour drawn only from their click counts has
been wrong in this ecosystem before.

## 7. The open question: is deletion ever offered?

Pip left this open, explicitly:

> "At some point we might have to figure out a way to let the player delete
> their backlog."

The tension is real and unresolved. Section 4 forbids a clearable backlog and
forbids discarding a Ledger entry unpaid; Pip anticipates needing a deletion
affordance anyway. Both can be true if deletion is a **priced strategic act**
rather than a **hygiene button** -- but that is a hypothesis, not a ruling.

What the thesis settles, and so constrains any answer:

- Deletion must not be free and must not be silent. Abandonment that costs
  nothing is not the skill being taught.
- Deletion must not be *complete*. A gesture that empties the mountain restores
  the clearable state section 4 forbids.
- Consequences must land later than the gesture, or it teaches nothing about
  displacement.
- It must not become a new currency or a second pricing path (ADR-0003, ADR-0013).

**Proposal -- three shapes, none endorsed:**

1. **Declared abandonment.** The player names what they are dropping and takes a
   consequence per item (reputation, a rival's gain, a soured counterparty). This
   is triage made explicit and paid for, and it is the closest fit to the
   existing IGNORE verb -- arguably it is IGNORE, applied retroactively and at a
   worse price. Risk: making the choice explicit makes it legible, which section 4
   warns against.
2. **Discharge with a scar.** A single whole-Ledger discharge, once per run, that
   clears the mountain and leaves a permanent penalty. Fits Pip's debt framing
   and the existing desperation-lever design (priced as desperation, never
   rubber-banding). Risk: a once-per-run button is a resource to optimise, not a
   skill to learn -- and it collides hardest with the mortality guarantee.
3. **No deletion; only decay and consequence.** Standing offers already evaporate
   (ADR-0012), minting nothing. On this reading the want is not for a mechanic at
   all but for the UI to stop showing what the player has already decided against.
   Cheapest by far. **But note it points the opposite way from Pip's own
   standing playtest note that deferrals are UI-INVISIBLE and should be made more
   visible** -- so if this is the answer, the two wants need reconciling in one
   pass rather than satisfied separately.

**Worth establishing first:** whether the felt need is for a *mechanic* or for a
*view* -- a way to file something as decided-against without it vanishing from
the record. Those have very different costs and only one touches the simulation.
Ask before building.

## Related

- `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md` -- turns survived dominant; flows only; the mortality guarantee
- `docs/adr/0002-win-condition-survival-spine.md` -- survival spine, rare apex victory, graceful concession (engineering ADR series)
- `docs/game-design/decisions/ADR-0003-liability-ledger.md` -- every mitigation is a loan; "Triage-in-time"; the inevitability-queue failure mode; no parallel economy
- `docs/game-design/decisions/ADR-0009-plan-months-two-speeds.md` -- HANDLE / DEFER / IGNORE; reserve; no banking
- `docs/game-design/decisions/ADR-0011-effort-economy.md` -- typed Attention (PLANNING / OPERATING), asymmetric overflow, workstream backlog, managers as interrupt shields
- `docs/game-design/decisions/ADR-0012-event-response-taxonomy.md` -- the four event classes; "the infinite to-do list is diegetic"
- `docs/game-design/decisions/ADR-0013-cost-of-debt-engine.md` -- one pricing engine for loans and defers
- `docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md` -- author causes, never outcomes
- `docs/game-design/PLAYTEST_v0.13.1_NOTES.md` -- "Deferrals are UI-INVISIBLE"
- `docs/game-design/DESIGN_2026-08-15_causality-violation.md` -- captured the same morning; the mortality guarantee from the other end (doom pinned at 0 and a run that would not end). Read alongside section 4's ban on discharging a Ledger entry unpaid.
- `docs/game-design/DESIGN_PHILOSOPHY.md` -- the interview-extracted principle set this feeds
- `docs/art/NOTE_2026-08-15_colour-as-identity.md` -- the other subject from the same recording
