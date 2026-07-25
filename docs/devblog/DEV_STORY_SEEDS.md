# Dev-Story Seeds

> Raw material for future Pip-written devblog / dev-story posts. NOT posts themselves --
> quotes, moments, and lessons captured while fresh so the assembly is cheap later.
> Pip writes the actual posts; this is the quote-and-moment lumberyard.

## The backlog as a time-capsule (2026-07-25, WS-3 triage)

**The moment:** a triage of the oldest open issues (#186-#520, some written ~8
months ago) surfaced a cluster of ideas that were *correct but premature* --
articulated long before the engine existed to hold them. The standout: **#476,
"accounting software reduces the AP cost of ledger chores,"** written months
before the ledger (ADR-0003) and the effort/Attention economy (ADR-0011) existed
to give it any meaning -- and it turns out to be almost exactly the mechanic the
first external playtest (#574) later asked for, unprompted.

**Why it's a story:** the satisfying inversion of "tech debt." A backlog isn't
only a pile of unpaid obligations; it's a time-capsule of ideas you had before
you could build them. The pleasure of building the engine is watching long-parked
back-of-mind niggles quietly become tractable -- the substrate catching up to the
intuition. Blog angle: *"the ideas were right; the engine wasn't ready yet"* -- on
parking ideas without guilt and letting the platform mature into them.

## The repatching / fallback-divergence lesson (2026-07-16, issue #646)

**The moment:** the overnight architecture-map lane, drafting `ARCHITECTURE.md`, ran a
coherence check and found that the nine-stream doom code (`doom_system.gd`) carried
*hardcoded fallback* coefficients ~66x off from the calibrated `defaults.json` shipped
alongside it. Normal play loads the JSON so it never bites -- but `Balance.gd` promises
"a missing/broken file degrades to exactly the shipped behavior," and that promise had
quietly become a lie for the new keys.

**Why it's a story, not just a bug:** it's a clean example of a *repatching hazard* that
appears whenever balance lives in data but ships with code defaults -- the two drift, and
the drift is invisible until the data path fails. It pairs with the session's
exploit-vs-strategy ruling: an exploit is engine misbehaviour, and a silent 66x fallback
is exactly the buglike behaviour a dev must get ahead of. The fix is trivial (match the
numbers); the *lesson* is the interesting part -- "data-driven balance needs a test that
the code fallbacks equal the shipped data," which is a generalizable discipline.

**Blog angle:** "The bug that only exists when the config file is missing" -- on why
data-driven design needs its degrade-path tested, not just its happy path.

## Other seeds from the L1 build wave (2026-07-13..16)

- **"I watched as I lost."** Pip's first playtest of the day-tick month playback -- the
  resolution spectacle delivered ADR-0004's *tragedy* loss-feeling for free, unplanned.
  The engine change that was about pacing turned out to be about emotion.
- **Attention = the founder currency, named in 2017 -- the year of "Attention Is All You
  Need."** The joke that is also the thesis.
- **The 50x calibration.** Pre-calibration, every bot died before the first month
  boundary (rival doom billed per day-tick, ~23x over). One re-denomination pass and
  baseline runs lasted ~50x longer. The game's whole feel was gated behind an accounting
  artifact nobody had looked at.
- **The CI that was green while running zero tests.** #629 -- the fresh-checkout import
  gap meant GUT quit(0) before collecting a single test, and the runner trusted the
  exit code. The repo's most dangerous lie, live for who-knows-how-long.
- **Doom became nine streams.** The thesis moment: doom stopped being a number things
  bump and became a computed rate over named world-state, so "what makes doom go up" is
  finally a single inspectable, arguable function -- the game's executable argument about
  AI risk.
- **The desperation lever is a trap that reads as help.** The solver proved it:
  pulling it is monotonically worse, and it silently converts doom deaths into ledger
  deaths -- ADR-0003's "every mitigation is a loan" proving itself in the sweep data.

## 2026-07-25 -- session seeds

- **"The bug only a human mashing keys could find."** A modal soft-lock -- open
  the ledger while an event fires, and the ledger ends up orphaned and
  un-closeable -- sailed through EVERY automated unit test. The tests asked "does
  `close()` work?" and never "can we reach a state where `close()` is
  unreachable?". A human playtester found it by flailing. The response, an
  adversarial FUZZ harness, then caught a SECOND shipping soft-lock plus the whole
  antipattern class. Thematic resonance: a game *about* the gap between
  verification and reality, whose own testing just re-taught that exact lesson --
  passing tests are not the same as a safe system.

- **"One missing queue_free()."** Both soft-locks were the same root shape: modal
  state lived in TWO places -- a tracked slot and the visible scene tree -- kept in
  sync BY HAND across a dozen handlers, and one handler forgot. Not a bug so much
  as a bug-factory: an architecture that makes correctness a thing you must
  remember N times instead of a thing that can't be gotten wrong. The fix was 3
  lines; the lesson is invariants-over-conventions.

- **"Curation before generation."** Built browser triage tools for ~1,668
  generated art assets and formed 650+ opinions in an evening -- then the analyzer
  showed the truth: 72 cat-walks promoted, and ZERO windows or floor tiles. You
  cannot build an office out of things you never chose. The discipline: review and
  surface the GAPS before generating more, not after.

- **"Hero hardcore, game cozy."** An art-direction thesis that crystallized
  mid-session: push the hero images to a hardcore high-fidelity ceiling,
  deliberately downscale the in-game art toward cozy, and let the CONTRAST between
  the two carry both the humour and the dread. Downscaling as a choice, not a
  compromise.
