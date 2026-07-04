# ADR-0006 — The replay string is the canonical run artifact; backend wiring order

- **Status:** ACCEPTED
- **Date:** 2026-07-04
- **Session:** Fable workshop #1 (repo archaeology: this repo + pdoom1-website + pdoom1-webclient)

## Context (what archaeology found)

The backend is ~80% built, not aspirational. Survived the Godot migration: seeded
deterministic RNG through `godot/scripts/core/game_state.gd`; a fully implemented
cumulative SHA-256 hash chain in `godot/autoload/verification_tracker.gd` (partially
wired — `record_rng_outcome` live, `record_action` tests-only, final hash printed at
game-over "for future leaderboard integration"); local per-seed JSON leaderboard
(`godot/scripts/leaderboard.gd`); headless `baseline_simulator.gd`. In `pdoom1-website`:
`api-server-v2.py` with `POST /api/scores/submit`, per-seed boards, JWT, Postgres
migrations incl. verification-hash schema, plausibility checks — with static per-seed
JSON boards on Netlify as the actually-deployed artifact. `pdoom1-webclient` has a
TypeScript port of the tracker and an empty `src/api/`.

**The correction:** the "run any input string through a verifier" memory describes the
full input-string replay design (`docs/REPLAY_VERIFICATION_SYSTEM.md`) — the one
component never built in either era. A hash chain proves the client computed a
self-consistent transcript; it does **not** prove the transcript describes a legal game.
Only re-simulation from inputs verifies.

## Decision

**The input-string replay is the canonical run artifact — anti-cheat, share format, and
bug-repro format in one object.** Rationale beyond anti-cheat: the community philosophy
(*"only the vastness of the design space will be what stops a determined player just
brute-forcing their way to a high score… although I would laud the initiative!"*) makes
verification the only law — coherent only if runs are replayable. And the "best loss"
(inventing an opening the ladder adopts) requires openings to be **shareable to be
adoptable**: the replay string is chess PGN — paste-able, forum-postable, verifiable
text. The pygame-era compact command-string format (`docs/technical/
COMMAND_STRING_CONTROLLER.md`) is the starting point for serialization.

**Two-tier verification:** hash chain stays as the cheap fingerprint for casual
submission; headless re-simulation (Godot, as `baseline_simulator.gd` proves viable)
backs disputed and top scores. For the ~30-nerd community, static-JSON boards plus a
submit path are sufficient; **the Postgres apparatus stays parked.**

## Wiring order (implementation lane)

1. Wire `record_action` into the live action pipeline (currently tests-only).
2. Serialize runs to the command-string format (seed + version + action string).
3. Import-and-replay path (load a string, re-simulate, compare final hash/score).
4. Submission to the static JSON boards (Netlify path already deployed).
5. (Parked) Postgres API server; revisit only if community scale demands it.

## Consequences

- Scores keyed `(seed, game_version)` (ADR-0002) are exactly what replay needs: a replay
  is only valid against its version's engine.
- Bots and brute-forcers are players, not cheaters, provided their runs verify. Tool-
  assisted play is welcomed culture, not a threat model.
- `pdoom1-ui` (empty directory) is deletion-candidate debris; `pdoom1-webclient`
  integration is out of scope until the Godot path is wired.
