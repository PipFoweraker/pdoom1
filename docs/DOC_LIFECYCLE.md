# Doc lifecycle policy

Status: LIVE

**Purpose:** turn doc-sprawl reconciliation from a periodic heroic sweep into a
continuous, self-declaring, ride-the-release-train ritual. A doc should announce
its own mortality; archiving should happen the day a doc is consumed, not months
later when someone notices the rot.

This policy is the generalization of a sweep we keep re-running by hand (see
`docs/archive/README.md` and `SALVAGE_REPORT.md` for the last big one). The goal
is to never need that heroic sweep again.

## 1. Self-declaring status header

Every working doc under `docs/` carries a one-line `Status:` value near the top:

- `LIVE` -- current canon; trust it.
- `SEED` -- an early idea capture; expected to grow up or die.
- `PROPOSAL` -- a design/plan doc awaiting a decision; home is temporary (see 2).
- `SUPERSEDED-BY <path>` -- kept for history; read the named doc instead.
- `ARCHIVED` -- lives under `docs/archive/`; provenance only, not current.
- `ONE-OFF` -- a session handoff / recon / kickoff; ship-and-retire.

A `SEED` or `ONE-OFF` header telegraphs its own mortality, so a future reader (or
a staleness scan) knows it was never meant to be permanent. This is ADR-0004's
self-describing-data principle (`docs/adr/0004-self-describing-data.md`) applied
to prose: the doc carries the metadata that tells you how to treat it, instead of
relying on external memory.

## 2. Archive-on-consumption

A `PROPOSAL`'s home is temporary by contract. When its decisions land in an ADR
or a build brief, `git mv` it into `docs/archive/<date>-<slug>/` in the SAME pass,
and add a one-line note at the top: `Consumed by <ADR / brief / PR>`.

Example: a design proposal retires the day its workshop ends -- the workshop
kickoff transcripts and pre-workshop analyses were archived exactly this way
(`docs/archive/game-design-pre-workshop1/`). Never delete; `git mv` preserves
`git log --follow`.

## 3. Cadence rides the train

Do NOT schedule a separate "doc cleanup day". Fold an epoch-hygiene step into the
monthly Epoch cut (first Friday; see `docs/ROADMAP.md` and
`docs/RELEASE_NOMENCLATURE.md`). At each cut:

- archive `PROPOSAL`s that were consumed since the last epoch,
- flip stale `Status:` lines (LIVE that is now superseded, etc.),
- regenerate generated indexes (`DQ_INDEX` and friends -- see 5),
- bump any "Current Version" lines to match `version.txt`.

Riding the release train means hygiene happens ~12x/year in small bites instead
of once/year as a painful archaeology dig.

## 4. Automate detection (PROPOSED -- not yet built)

Propose a `scripts/check_doc_staleness.py` run in CI as WARN-only (never blocks a
merge; it produces a signal, not a gate). It greps changed docs for tells:

- retired terms: `quarterly`, `Python bridge`, `pygame`, old codenames,
- version numbers older than `version.txt`,
- dead relative links (a link whose target path no longer exists -- e.g. a link
  to a doc that was just `git mv`'d to `docs/archive/`).

Output is a report on the PR, so staleness becomes a CI signal an author can act
on, not a human-memory task. Status of this item: PROPOSED / not-yet-built.

## 5. Precedent: generated indexes never rot

The proven anti-rot pattern here is generation, not discipline: `DQ_INDEX.md` is
GENERATED from `WORKSHOP_2_BACKLOG.md` by `scripts/generate_dq_index.py` and is
never hand-edited (a `--check` mode gates pre-commit against a stale index). The
failure mode it replaced -- the hand-maintained `decisions/README.md` index that
silently went stale -- is exactly what this policy exists to prevent. Where an
index can be generated from source, generate it; where it must be prose, make the
prose self-declaring (rule 1) so a scan can catch it (rule 4).

---

This doc is itself `Status: LIVE`. When it is superseded, flip the header and
`git mv` it per its own rules.
