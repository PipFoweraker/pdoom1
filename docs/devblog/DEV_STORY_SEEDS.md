# Dev-Story Seeds

> Raw material for future Pip-written devblog / dev-story posts. NOT posts themselves —
> quotes, moments, and lessons captured while fresh so the assembly is cheap later.
> Pip writes the actual posts; this is the quote-and-moment lumberyard.

## The repatching / fallback-divergence lesson (2026-07-16, issue #646)

**The moment:** the overnight architecture-map lane, drafting `ARCHITECTURE.md`, ran a
coherence check and found that the nine-stream doom code (`doom_system.gd`) carried
*hardcoded fallback* coefficients ~66× off from the calibrated `defaults.json` shipped
alongside it. Normal play loads the JSON so it never bites — but `Balance.gd` promises
"a missing/broken file degrades to exactly the shipped behavior," and that promise had
quietly become a lie for the new keys.

**Why it's a story, not just a bug:** it's a clean example of a *repatching hazard* that
appears whenever balance lives in data but ships with code defaults — the two drift, and
the drift is invisible until the data path fails. It pairs with the session's
exploit-vs-strategy ruling: an exploit is engine misbehaviour, and a silent 66× fallback
is exactly the buglike behaviour a dev must get ahead of. The fix is trivial (match the
numbers); the *lesson* is the interesting part — "data-driven balance needs a test that
the code fallbacks equal the shipped data," which is a generalizable discipline.

**Blog angle:** "The bug that only exists when the config file is missing" — on why
data-driven design needs its degrade-path tested, not just its happy path.

## Other seeds from the L1 build wave (2026-07-13..16)

- **"I watched as I lost."** Pip's first playtest of the day-tick month playback — the
  resolution spectacle delivered ADR-0004's *tragedy* loss-feeling for free, unplanned.
  The engine change that was about pacing turned out to be about emotion.
- **Attention = the founder currency, named in 2017 — the year of "Attention Is All You
  Need."** The joke that is also the thesis.
- **The 50× calibration.** Pre-calibration, every bot died before the first month
  boundary (rival doom billed per day-tick, ~23× over). One re-denomination pass and
  baseline runs lasted ~50× longer. The game's whole feel was gated behind an accounting
  artifact nobody had looked at.
- **The CI that was green while running zero tests.** #629 — the fresh-checkout import
  gap meant GUT quit(0) before collecting a single test, and the runner trusted the
  exit code. The repo's most dangerous lie, live for who-knows-how-long.
- **Doom became nine streams.** The thesis moment: doom stopped being a number things
  bump and became a computed rate over named world-state, so "what makes doom go up" is
  finally a single inspectable, arguable function — the game's executable argument about
  AI risk.
- **The desperation lever is a trap that reads as help.** The solver proved it:
  pulling it is monotonically worse, and it silently converts doom deaths into ledger
  deaths — ADR-0003's "every mitigation is a loan" proving itself in the sweep data.
