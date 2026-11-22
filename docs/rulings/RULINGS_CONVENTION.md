# The RULING convention -- how a decision stops evaporating

> Hand-written SSOT. The index (`RULINGS.md`) and the machine artifact
> (`rulings.json`) are GENERATED from the declarations this file describes.
> Regenerate with `python scripts/generate_rulings.py`.

## This is an INDEX, not the only store (consolidated 2026-08-21)

An audit on 2026-08-21 found five places rulings were being recorded, four of
them older than this convention. Pip's instruction was to consolidate. What that
meant in practice was **one index over five sources**, not one file:

| kind | n | what it is | where it lives |
|---|---:|---|---|
| `declaration` | 10 | a `RULING:` line written next to what it governs | anywhere |
| `adr` | 19 | a full architecture argument, summarised here | `docs/game-design/decisions/` |
| `session` | 3 | a transcript or workshop ruling set, pointed at | `docs/SPOKEN_*`, `*RULINGS*` |
| `card` | 3 | the input a ruling was made FROM | `docs/decision-cards/` |

**Why the files were not merged.** They are genres, not rivals, and each carries
something a one-line summary would delete:

- An **ADR** is an argument. Context, Decision, Consequences, several pages. The
  reasoning is what makes it re-checkable in a year; flattening it destroys the
  only part that ages well. The index carries its `Status` and `Summary`
  verbatim and points at the rest.
- **`SPOKEN_RULINGS_*`** are **transcripts** -- evidence of what was said, one of
  them explicitly stamped *"not yet re-read by him"*. Rewriting evidence into a
  summary is the same error `check_provenance.py` refuses to make about asset
  origins: asserting after the fact something the record never said.
- A **decision card** is the input a ruling was made from. Indexing it as a
  ruling would confuse the question with the answer.

So: nothing was moved, nothing was rewritten, and every ruling in the estate is
findable in one place for the first time. `--flavour architecture` now returns
all 19 ADRs.

**If you add a sixth kind of ruling document**, add it to `RULING_DOC_GLOBS` in
`scripts/generate_rulings.py` rather than starting a sixth store.

## The problem this solves

Rulings in this estate are already being captured -- measured 2026-08-15, more
than forty `ruled by Pip` / `Pip ruled` / `ruled 2026-..` lines exist across
`.py` docstrings, `.gd` comments, `.json` data files, docs and tests. Each was
written at the point where the ruling bites, which is the right place for it.

Three things are missing, and none of them is capture:

1. **A home for a ruling with no code yet.** "The epoch counter starts at 1"
   has nowhere to live until an epoch exists.
2. **Recall by flavour.** Pip, 2026-08-15: *"these will show up again in
   similar flavours."* Nothing today can answer "what have I already ruled
   about this kind of question?"
3. **Supersession.** Nothing marks which of two conflicting rulings is current.

## The convention

One line. Writable in ANY tracked text file -- a docstring, a `.gd` comment, a
markdown paragraph, an issue body. This is deliberate and copied wholesale from
the `COMMITMENT` convention (`docs/calendar/COMMITMENTS.md`), which solved the
same shape for dates: the declaration goes where the thing lives, and a
generator does the gathering.

(Note the missing colon above and below. Writing that token followed by a colon
in prose makes the commitment calendar's scanner read this documentation as two
malformed declarations -- the same "examples must not become data" trap the
rulings generator hits with its own convention doc.)

```
RULING: <YYYY-MM-DD> -- <the ruling, one sentence> -- flavour: <slug>
```

Optional trailing fields, any order, each introduced by ` -- `:

| field | meaning |
|---|---|
| `mechanism: <what>` | the guard, gate or trigger that will RE-ASK this. See "Teeth" below. |
| `supersedes: <id>` | this ruling replaces an earlier one; the earlier one is marked superseded in the index rather than deleted. |
| `by: <who>` | defaults to `Pip`. Present for the rare ruling made by someone else. |

Examples, all real shapes:

```
RULING: 2026-08-15 -- the epoch counter starts at 1, no backfill over past waves -- flavour: art-lineage
RULING: 2026-08-15 -- masters are written verbatim, never re-encoded -- flavour: art-provenance -- mechanism: tools/assets/check_credentials.py
RULING: 2026-08-11 -- keep unattributable assets and record them as unknown -- flavour: art-provenance -- mechanism: tools/assets/check_provenance.py
```

### Where to write one

- **It has a home** -- put the line next to the code, data or doc it governs.
  This is the preferred case: the ruling is visible to whoever next touches the
  thing it constrains.
- **It has no home yet** -- append it to `docs/rulings/LEDGER.md`, which exists
  for exactly this. `python tools/rule.py` does that for you in one command.

## Teeth -- the mechanism field is optional, and its absence is reported

Pip's doctrine, ruled 2026-08-11 and embodied in `check_provenance.py`: *what
forces a question to be resolved later is a MECHANISM, not a document.*

Requiring a mechanism on every ruling was considered and rejected on
2026-08-15: it taxes every capture, and the predictable result is rulings that
never get written down at all. So `mechanism:` is optional, and the generated
index carries a **"nothing will re-ask these"** section listing every ruling
without one.

Report, never block -- the same posture `check_provenance.py` takes toward the
third audit direction. You see the rot without paying for it per ruling.

## Never drop -- the UNDECLARED scan

The generator also does a PROSE SCAN for the informal patterns already in the
tree (`ruled by Pip`, `Pip ruled`, `ruled 2026-..`). Anything that reads like a
ruling but carries no `RULING:` declaration is emitted as
**`UNDECLARED -- needs a RULING: line`**, in both outputs.

This is the `COMMITMENT` doctrine restated: *"A calendar that silently omits is
worse than no calendar, because it looks complete."* An index of rulings that
quietly ignores forty existing ones would be actively misleading.

The scan is a heuristic and WILL produce false positives (a sentence that merely
mentions a ruling). That is the correct trade: a false positive costs one glance,
a false negative loses a decision.

## Determinism

Output is a pure function of tracked files. Nothing reads the clock -- a
clock-reading generator goes stale overnight and trains people to ignore the
gate. This is what makes `--check` safe in pre-commit.

Ruling ids are `<repo>:<date>:<hash8>` where `hash8` is the first 8 hex chars of
the sha256 of the ruling text. Deliberately NOT a sequence number: inserting a
ruling must not renumber every later one, or ids in `supersedes:` fields rot.

## Cross-repo -- federated, not centralised

Ruled by Pip 2026-08-15: the road is cross-repo from day one.

There is no shared database and no server. Each repo scans ITSELF and emits
`docs/rulings/rulings.json`. That is the same doctrine `docs/art/NOMENCLATURE.md`
already states for vocabulary:

> "This file exists so `pdoom1-website`, `pdoom-data` and `coordination` can
>  quote the vocabulary without reading the app, and cannot end up quoting a
>  version the app no longer uses."

An aggregator -- `coordination` is the natural home -- reads each repo's emitted
`rulings.json` and produces the estate-wide view. It never writes back: a repo's
rulings are authored in that repo, full stop. That keeps the merge story empty,
which is the only reason a federated design of this kind survives.

### The consumer contract (`rulings.json`, schema `pdoom.rulings/0.1`)

```json
{
  "schema": "pdoom.rulings/0.1",
  "repo": "pdoom1",
  "generated_from": "tracked files at HEAD",
  "count": 3,
  "rulings": [
    {
      "id": "pdoom1:2026-08-15:1a2b3c4d",
      "date": "2026-08-15",
      "ruling": "the epoch counter starts at 1, no backfill over past waves",
      "flavour": "art-lineage",
      "by": "Pip",
      "mechanism": null,
      "supersedes": null,
      "superseded_by": null,
      "source": "docs/rulings/LEDGER.md:12"
    }
  ],
  "undeclared": [
    {"source": "tools/assets/check_provenance.py:4", "text": "Ruled by Pip 2026-08-11: the six unattributable assets are KEPT ..."}
  ]
}
```

Rules for consumers:

- `id` is stable across regenerations. Reference rulings by `id`, never by index.
- A ruling with `superseded_by` set is HISTORY. Do not quote it as current.
- `undeclared` is a work list, not data. Never present it as a ruling.
- The schema version changes if any field's meaning changes. Pin it.

### What each repo needs to join

1. `scripts/generate_rulings.py` (copy it; it has no pdoom1-specific logic
   beyond the repo name, which it derives from the git remote).
2. `docs/rulings/LEDGER.md` with a header line.
3. A pre-commit `--check` hook.

## Usage

```
python tools/rule.py "the epoch counter starts at 1" --flavour art-lineage
python tools/rule.py "..." --flavour art-lineage --mechanism tools/x.py
python tools/rule.py --flavour art-lineage --list      # precedent: what did I already rule here?

python scripts/generate_rulings.py           # (re)write RULINGS.md + rulings.json
python scripts/generate_rulings.py --check   # exit 1 if stale (pre-commit)
python scripts/generate_rulings.py --report  # stdout summary, never fails
```
