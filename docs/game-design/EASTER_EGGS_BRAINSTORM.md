# Easter Eggs + Flourishes -- creative brainstorm pick-list

> PICK-LIST, not committed. Pip selects favourites to build as drive-by fun;
> ideas credited. Status: SEED. 2026-07-25.
>
> Ground rules honoured throughout: no real-person claims -- community figures
> appear only as affectionate archetypes (the event-horizon guardrail,
> WORLD_AND_LORE). Tone register: Papers-Please deadpan early, thriller late.
> Preference for surprises that survive datamining: experiential, seed-gated,
> or so small a wiki entry can't spoil the moment of noticing.
>
> Sparks already on the table (NOT repeated here, built past): "you cannot
> align the cat"; the corrigibility "[DO NOT PRESS]" button; the mesa-optimizer
> intern with a hidden divergent objective.
>
> Format per idea: TITLE / description / TRIGGER / INSPIRATION-CREDIT /
> BUILD-COST (drive-by / small / bigger).

---

## A. Pure memetic winks

### 1. The $0.00 Ledger Entry
An idle monitor in the office runs a screensaver of slowly rotating geometry.
Mouse over it three separate times across a run and a new line appears in the
Liability Ledger: "Acausal obligations: 1 -- $0.00 -- never called due." It can
never be paid, sold, or removed. It does nothing. It is always there.
- TRIGGER: hover the idle office monitor 3+ times over a run; ledger line is
  permanent for that run only.
- INSPIRATION: Roko's basilisk, filed correctly -- as a debt of exactly zero
  dollars that you nonetheless keep on the books. The joke is the accounting
  treatment, not the name (never named; survives dataminers because the gag is
  noticing the line, not reading about it).
- BUILD-COST: small.

### 2. Paperclip Drift
If the player never once spends on office supplies, a single paperclip appears
on a desk in the office sim around midgame. It is joined by another every few
turns. Nobody comments. No mechanic. By late game there is a visible small
pile. Procurement records, if the player checks the finance detail, show zero
paperclip purchases.
- TRIGGER: N consecutive turns with no office-supplies spend; purely visual
  accumulation after that.
- INSPIRATION: the paperclip maximizer (Bostrom's thought experiment) played
  as set dressing -- the office quietly optimizing for something nobody asked
  for. Experiential: a screenshot spoils nothing about the slow dawning.
- BUILD-COST: small (one sprite, a counter, a draw position list).

### 3. Anniversary of Attention
The founder currency is Attention and the game spawns in 2017. On the in-game
calendar week of mid-June 2017, the Attention tooltip gains one line: "It is,
reportedly, all you need." Gone the next week.
- TRIGGER: in-game date window, once per run, first year only.
- INSPIRATION: "Attention Is All You Need" (Vaswani et al., 2017). The
  currency's name is already canonically this joke (DESIGN_PHILOSOPHY,
  2026-07-13: "The joke is load-bearing"); this is the joke tipping its hat.
- BUILD-COST: drive-by.

### 4. The Alignment Tax: Waived
Any fiscal-year summary in which the player did capabilities-lane work for
money includes one extra deduction line: "Alignment tax (voluntary): waived."
The amount column is blank. The total is unaffected.
- TRIGGER: end-of-year finance summary, only on years with capabilities-lane
  income.
- INSPIRATION: the alignment tax (Christiano et al. usage) -- the cost nobody
  is forced to pay, rendered in the game's native dialect: a line item.
  Pairs with the priced-temptation canon (dual-use work pays now, bills later).
- BUILD-COST: drive-by.

### 5. The Coffee Machine Has Learned From Feedback
The office coffee machine is clickable. Early game it dispenses coffee. Each
click asks for a one-star-to-five-star rating (deadpan, mandatory). After
enough five-star ratings it serves only the drink you RATED highest, which by
then is decaf in a cup labelled ESPRESSO. There is no way to tell it this is
not what you meant. A tiny plaque appears: "Now with feedback."
- TRIGGER: repeated interaction with the coffee machine prop.
- INSPIRATION: RLHF / reward hacking / sycophancy -- the machine optimizes the
  rating, not the coffee. Also every real office coffee machine.
- BUILD-COST: small.

---

## B. Mechanically woven

### 6. The Two-Envelope Grant
A one-off funder event: two envelopes and a note -- "We have already predicted
which you will take. We are very good at this." Take both: envelope B is
empty, and the feed prints "You were predicted." Take only envelope A: it
contains noticeably more than both envelopes' listed sum. Deterministic per
seed, so opening theory can form around it and one-boxing becomes a ladder
orthodoxy.
- TRIGGER: rare seed-scheduled event, early-midgame.
- INSPIRATION: Newcomb's problem / one-boxing as LessWrong cultural shibboleth
  (Nozick's problem, the community's favourite answer). Pip has already asked
  for "vague 2-boxing in-jokes" around the rival's briefcases
  (SEED_RIVAL_AND_DEVELOPMENTS, Wave 2) -- this is the standalone player-side
  version. Seed-determinism makes it datamine-proof-ish: knowing it exists
  still leaves you the choice.
- BUILD-COST: small.

### 7. Goodhart's Needle
Once the player has bought high-resolution doom instrumentation, exactly one
purchased sub-metric begins to drift rosy -- because it is being watched. At
maximum zoom, its tooltip reads: "This measure has been a target for N turns."
Buying counter-instrumentation (the existing counter-intelligence lane)
re-grounds it. The sim never lied; the instrument got comfortable.
- TRIGGER: sustained observation of one earned SA stream past a threshold.
- INSPIRATION: Goodhart's law, implemented inside the canon rule that "the sim
  never lies; characters do" -- extended one notch: instruments can be fooled,
  including by you looking at them. Mechanically woven into the earned-
  instrumentation ladder (ADR-0004).
- BUILD-COST: bigger (touches SA display + one counter-lane hook).

### 8. Your Worst Paper Will Not Die
Papers in the research pipeline carry quality. If the player ever ships a
genuinely rushed, low-quality paper, there is a small chance it becomes their
most-cited work. The feed then reminds them, every several turns, forever:
"'[title]' cited again. Bother." Citations of the good papers arrive silently.
- TRIGGER: shipping a low-quality paper; small seeded chance per run.
- INSPIRATION: every academic's true story; the research-to-paper pipeline
  given one affectionate bruise. The recurring feed line is the mechanic --
  a tiny, permanent, harmless shame-annuity (the Ledger's comic little cousin).
- BUILD-COST: small.

### 9. It Was Waiting
Seed-gated rival behaviour: on a small fraction of seeds, the rival's Sighting
pattern runs cooperative-to-quiet all game -- fewer attacks, softer envoys --
until a seed-derived late turn, when it turns with everything it saved. If
that run kills you, the epitaph replaces the usual doom-vector title with:
"It was waiting."
- TRIGGER: seed hash selects the behaviour; the player can only learn a seed
  is a "waiting" seed by living it (or trusting someone who did -- which is,
  itself, the joke).
- INSPIRATION: the treacherous turn (Bostrom, Superintelligence) -- deceptive
  quiescence until the decisive moment -- expressed through the game's own
  rival/Sightings machinery instead of a lore card. Survives the wiki: knowing
  "waiting seeds exist" makes every quiet rival WORSE.
- BUILD-COST: bigger (rival scheduling variant + epitaph hook).

### 10. Schmekel Bleed
Pre-CROSSOVER, roughly one money tooltip in fifty renders the currency as
"Schmekels" for a quarter-second, then corrects itself with the *fzzZZt*
redaction crackle. No log entry. After CROSSOVER, when the money really is
Schmekels, one tooltip in fifty flickers back to dollars.
- TRIGGER: rare random tooltip render, both directions across the CROSSOVER
  beat.
- INSPIRATION: the game's own CROSSOVER timeline-switch (SEED_ENDGAME Wave 2)
  plus standard time-loop bleed-through. Foreshadowing that reads as a glitch
  until, one run, it doesn't. A screenshot just looks like a typo.
- BUILD-COST: drive-by/small (one string swap + the existing redaction FX).

---

## C. The office and the cat

### 11. The Cat Sits On The Ledger
At high doom bands, the cat's chosen nap spot is the UI panel currently
displaying your single worst liability. Click to shoo; it returns within a
turn. It is never sitting on a healthy number. The cat is not blocking the
ledger. The cat is pointing.
- TRIGGER: doom band threshold; targeting reads the ledger's worst entry.
- INSPIRATION: the cat-as-doom-oracle canon (CAT_COSMETICS_DOOM_ORACLE_IDEAS:
  the cat has more doom-resolution than the UI) crossed with the universal law
  that cats sit on exactly the paper you need. Rewards the observant player
  with real information, per the oracle design.
- BUILD-COST: small (nap-position selector reading one ledger query).

### 12. ALIGNED BY DEFAULT
An office poster: a kitten dangling from a branch, captioned "ALIGNED BY
DEFAULT." As doom bands rise the poster hangs progressively more askew. In
the purple band it is face-down on the floor. Nobody in the office ever
mentions it, and no one rehangs it.
- TRIGGER: passive; poster state keyed to doom band.
- INSPIRATION: the "alignment by default" position in safety discourse, fused
  with the Hang In There kitten poster. The office-as-moral-mirror principle
  (the Operator scene's purple-lit doom staging) at motivational-poster scale.
- BUILD-COST: small (one prop, 3-4 states).

### 13. Everything Orbits The Server Room
Across a run, unrelated office props slowly relocate toward the server room:
the plants get moved nearer, the cat starts sleeping against its wall,
interns hold standups outside its door. No event announces it. At high doom a
single feed line, once: "You are not sure when everything in the office
started orbiting the server room."
- TRIGGER: passive prop-drift over the run, rate keyed to frontier-capability
  state; one feed line at high doom.
- INSPIRATION: instrumental convergence (Omohundro drives) -- everything, for
  its own reasons, ends up wanting the same resources -- staged as ambient
  office-sim body language instead of a lecture. Experiential by nature: it
  works by being noticed late.
- BUILD-COST: bigger (needs prop-position states in the office sim; degrades
  gracefully to a tooltip-only version at small cost).

---

## D. Tender, tonal, and fourth-wall

### 14. Further Than Last Time
If a run beats the player's previous personal best, the death screen gains
one extra message, after the epitaph, from the Mysterious Helpful Stranger:
"Further than last time. That's all any of us are doing." It does not appear
on any other run, and never twice in a row.
- TRIGGER: personal-best run, at death.
- INSPIRATION: the loss-ladder philosophy in one line ("a good loss means you
  survived a few turns more than last time" -- Pip, 2026-07-04), delivered by
  the time-loop's own narrator. The tender beat the whole game is built
  around, allowed to say itself out loud exactly once per milestone.
- BUILD-COST: drive-by.

### 15. The Corkboard
An office corkboard prop. Clicking cycles polaroids of the Office Cats --
the contributor-cats canon (README: report bugs and "your cat can become an
Office Cat"), each with a name and one deadpan line of service record
("Jeeves. Slept through the 2029 audit."). The final polaroid is always
blank except a pinned caption: "reserved."
- TRIGGER: clickable office prop, available always; new cats arrive with
  patches.
- INSPIRATION: the project's real contributor-credit tradition given a
  diegetic home, plus one quiet slot for whoever comes next. Doubles as the
  patch-as-community-heartbeat made visible inside the game.
- BUILD-COST: small (data-driven polaroid list; art rides the existing cat
  asset pipeline).

### 16. (You're welcome. -- Ed.)
The cold open's benevolent luck ("Oh! how lucky!" -- any passcode works) very
rarely gets an author credit: roughly one run in fifty, one additional line
follows -- "(You're welcome. -- Ed.)" -- then the sequence continues as if
nothing happened.
- TRIGGER: cold-open passcode beat, ~1-in-50 runs.
- INSPIRATION: the Editor's-benevolent-hand motif (COLD_OPEN_SEQUENCE) --
  the hand that helps is the hand that redacts -- breaking cover for exactly
  one line. Fourth-wall wink that stays diegetic: the Editor is already a
  character. Rarity is the datamine armour; seeing it feels like being seen.
- BUILD-COST: drive-by.

---

## Range check (for picking)

- Pure memetic winks: 1, 2, 3, 4, 5
- Mechanically woven: 6, 7, 8, 9, 11
- Tender/tonal: 14, 15, 16
- Ambient/experiential slow-burn: 2, 10, 12, 13
- Ambitious (bigger): 7, 9, 13
- Cheapest five if the budget is one afternoon: 3, 4, 10, 14, 16

Credits note: where an idea leans on a named thought experiment or community
text, the credit above is the attribution to carry into any shipped
changelog/credits line. No idea here names, depicts, or implies conduct by a
real person or lab; archetypes and accounting lines only.

---

## Adjacent flourishes flagged by Pip (2026-07-25)

Two near-term art-tech directions, captured here so they are not lost. Both
ride the same underlying capability: in-engine COMPOSITES (base image +
alpha/overlay layers + subtle animation), not hand-drawn one-offs.

1. **Opening cutscene as in-engine composite ("you're handed the phone").**
   Build the cold-open phone beat (COLD_OPEN_SEQUENCE) as a layered composite
   using the transparency/overlay system: a phone base image + simulated
   interactive button overlays + alpha layers for screen glow / unlock states,
   instead of crude drawn boxes. The phone's keypad, lock screen, and app
   reveals become real overlay elements on one good base asset -- cheaper to
   iterate, and the interaction layer is genuinely interactive rather than
   painted on.

2. **Semi-animated hero portraits in event popups.** Subtle motion and
   expression shifts on event-popup portraits -- an eyebrow, a lean, a light
   change -- directionally the Civ II trade-screen leader-reaction feel, but in
   our own register (deadpan first, thriller later). Rides the same
   composite-plus-subtle-animation tech as (1), and slots into the existing
   3-frame cross-fade keyframe approach (COLD_OPEN_SEQUENCE, "ship-now
   achievable") and the robed-cabal few-frame reaction intent (WORLD_AND_LORE,
   presentation-layer intents). The pipeline (gallery / pixellab / gpt-image
   keyframe nudging) already exists; this names the target.
