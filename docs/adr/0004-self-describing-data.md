# ADR-0004: Self-describing data files (schema declared by the file, not inferred from location)

**Status:** Accepted (2026-07-25, Pip)
**Deciders:** Pip
**Context tags:** tooling, data-architecture, anti-rot, futureproofing

## Context

The data-validation CI (`scripts/validate_historical_data.py`) globs a directory
(`godot/data/researchers/*.json`) and validates **every** file in it against ONE
schema (`researcher.schema.json`, which requires a top-level `researchers`
array). When a second file *shape* -- `quirks.json`, a quirk catalogue with a
top-level `quirks` key -- landed in that folder, validation hard-failed
(`quirks.json/root: 'researchers' is a required property`) and reddened CI on
every PR (issue #807).

**Root cause is structural, not a typo:** the validator assumes
`directory == schema type`. One folder, one shape. That assumption breaks
silently the moment a folder holds two shapes, and it does not scale.

This matters beyond one file. The game is deliberately **data-driven** (events,
actions, scenarios, researchers, quirks, balance -- all JSON) and Pip is steering
toward **scale**: `pdoom-data` treated as a data lake, good metadata, downstream
ingestion, then balance-shaping inside this repo, targeting **hundreds-to-
thousands of events managed with minimal drift, wrongness, and operator
insanity**. Directory-inferred schema is a landmine that detonates more often as
the data grows.

## Decision

**Data files declare their own type; tooling dispatches on the declaration.**

1. Each validated JSON data file carries an explicit type discriminator -- a
   native `"$schema"` reference (path or id) or a `"schema_type": "<name>"`
   field -- naming the schema it must satisfy.
2. Validation tooling reads the declaration and selects the schema from a
   registry. It NEVER infers schema from directory or filename.
3. A file with no declaration is either (a) skipped with a logged notice, or
   (b) failed as "undeclared" -- chosen per tool, but never mis-validated
   against a wrong schema.
4. **Migration is incremental, not a big bang.** New data files self-declare
   from now on. Existing files are migrated folder-by-folder during tidy lanes,
   not under release pressure.
5. **Immediate unblock (v0.13.1, non-forking, tooling-only):** make the current
   researcher loop skip files lacking a `researchers` key (or explicitly skip
   `quirks.json`) so CI goes green now. This is the stopgap; the self-declaration
   migration is the real fix (tracked as a follow-up tech-debt issue).

## Consequences

**Positive**
- Adding a new data file-type never again requires editing the validator or
  dodging a glob assumption -- the file says what it is.
- Consistent with the repo's existing **anti-rot principle**: `DQ_INDEX` is
  *generated from source, not hand-maintained*; version is *one SSOT, synced*
  (`sync_version.py`). Self-declaration extends "the source describes itself;
  tooling reads the description" to all game data. It cannot drift from its
  validator the way a central manifest can (the stale `decisions/README.md` is
  that drift failure mode).
- Scales toward the data-lake vision: thousands of events, each self-typed,
  ingestible downstream by `pdoom-data` on a stable declared contract.

**Negative / cost**
- Every data file gains one metadata field (small, one-time).
- A schema registry must exist and be kept complete (but it is small, central,
  and additive -- far less drift-prone than per-directory glob assumptions).
- Migration touches many files over time (done incrementally, low-risk).

**Non-forking:** this is tooling + data-metadata only. No gameplay/RNG/scoring
change. Ladder unaffected.

## Related
- Issue #807 (the quirks.json CI failure that triggered this).
- `CLAUDE.md` anti-rot pattern (generated indexes; version SSOT).
- Cross-repo: `pdoom-data` data-lake direction (metadata + downstream ingestion),
  balance-shaping consumed back into this repo.
- Follow-up: file a tech-debt issue for the `data/**` self-declaration migration.
