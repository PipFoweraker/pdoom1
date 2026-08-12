# Art review nomenclature -- P(Doom)1

**GENERATED FILE -- do not hand-edit.** Regenerate with:

```
python tools/art_review/serve_review.py --emit-nomenclature
```

The source of truth is `VERDICTS_DOC` / `HARVEST_DOC` in
`tools/art_review/serve_review.py`. This file exists so `pdoom1-website`,
`pdoom-data` and `coordination` can quote the vocabulary without reading the
app, and cannot end up quoting a version the app no longer uses.

## Two axes, not one

A **verdict** is an asset's **fate** -- exactly one per asset, exclusive.
A **harvest tag** is something that **survives** that fate -- any number, and
still applies when the image is discarded. "No, but I like the corner" is not
a verdict; it is a discard plus a harvest tag.

## Verdicts (exactly one per asset)

| verdict | key | meaning | detail |
|---|---|---|---|
| `keep` | `K` | Ship it. | This asset is good as it stands. Decided -- moves to the archive. Does NOT mean promoted: promotion is a separate gate. |
| `remix` | `R` | Regenerate and compare. | On-brief but not final. Spends generation budget: a remix is a request for a fresh variant. Stays LIVE -- it expects a new image to judge. Was called `iterate` in v2 and migrates automatically. |
| `shelf` | `S` | Right, but not now. | Correct work with no current home -- the wrong brief, the wrong season, or a scene not yet written. Spends nothing. REQUIRES a return condition (a trigger, not a date). Without one it is an abandonment with better manners, so the server rejects it. NAMED `shelf`, NOT `hold`, DELIBERATELY: apply_review.py uses `held` for a PROMOTION state -- a keep the pipeline withholds from godot/assets with a rule reason -- and pdoom1-website#249 has already been told the promotion vocabulary is promotable/contested/held/blocked. Reviewer-defers and pipeline-withholds are different layers and must not be one letter apart. Ruled by Pip 2026-08-13. Key is S; H still works as an alias for the hour this was called `hold`. |
| `discard` | `D` | Off-brief. | Wrong direction. NOT regenerated -- a discard says the BRIEF needs a rethink, not a re-roll. Decided -- moves to the archive. Prompts for a note, because the reason is the reusable part. |

`keep` and `discard` are **decided**. `remix` and `hold` stay **live**.

**`keep` is not `promoted`.** Promotion to the game or to a public surface is
a separate gate, ruled distinct by Pip on 2026-08-06.

## Harvest tags (zero or more, independent of the verdict)

| pattern | example | meaning |
|---|---|---|
| `element:<thing>` | `element:corner, element:lamp` | A component worth keeping when the image is not. Survives a discard. |
| `composition` | `composition` | The arrangement works even if the render does not. |
| `palette` | `palette` | The colour relationship is the keeper. |
| `seed:<idea>` | `seed:new-scene` | An idea this image PRODUCED, which outlives it. Feeds the next batch's queue spec rather than describing this asset at all. |

## Storage contract

| file | role |
|---|---|
| `tools/art_review/review_log.jsonl` | **append-only, source of truth.** One event per change: `{ts, asset, prev, next, cleared}` |
| `tools/art_review/review_state.json` | **projection** -- last write per asset. Rebuildable via `--replay-log` |

Events predate the log only for decisions made before **2026-08-13**; a replay
over the partial log is reported as a SUBSET and never silently overwrites.

Asset ids: `gen:<batch>:<family>:<variant>`, `px:<relpath>`, `file:<relpath>`.
**Resolution is never part of the id**, so a verdict applies to a family and
cannot orphan its own downscales.

## Legacy verdicts

`iterate` (v2), `maybe` and `reroll` (v1) all migrate to `remix` on load.
Migration is in-memory and lossless; files are rewritten opportunistically.
