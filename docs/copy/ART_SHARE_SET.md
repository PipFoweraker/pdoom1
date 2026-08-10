# Art share set -- what it is, what it is not, and how to consume it

**Status: ACTIVE (2026-08-07).** Part of the voice seam. `pdoom1` publishes it;
`pdoom1-website` pulls it. Direction is one-way, per `docs/copy/README.md`.

- Manifest: `docs/copy/art_share_set.json`
- Prompt bodies: `docs/copy/art_share_set_prompts.json` (keyed by `prompt_sha256`)
- Builder: `python tools/assets/build_share_set.py` (`--check` gates staleness)
- Text-leak evidence: `tools/art_review/text_scan_art_night_2026-08-07.json`

---

## The gap this closes

ADR-0019 routes art that a GAME SLOT demands: Generated -> Library -> Packed,
where the only path into `godot/assets/` is a mechanically verified demand entry.
It says nothing about public surfaces, because it was never about them.

The consequence nobody had written down: **an asset Pip likes that no game slot
needs had no route to any public surface at all.** It is never packed, so there
is nothing for the website to pull. On the 2026-08-07 run that is most of what he
kept -- 143 assets judged good, zero of them demanded by a slot.

The share set is that missing route. It is a declaration, derived from verdicts
already applied, of which Library assets `pdoom1` will hand over.

## What it is NOT

**It is not a publication decision.** `coordination#31` ruled A2 bit 3: the
`publishable` gate belongs to `pdoom1-website`. The asymmetry in the minute is the
reason -- "a wrong `promotable` puts a weak sprite in a build -- internal,
recoverable. A wrong `publishable` puts a public claim on a cached, indexed
surface that deleting a file does not retract." `pdoom1` did not want that gate
and is not quietly taking it here. Every entry is a CANDIDATE.

**`keep` is not clearance.** `tools/art_review/serve_review.py` defines `keep` as
"accept it" -- taste, and only taste. ADR-0019 agrees from the other side:
"Verdicts still gate Library admission (taste)... none of them implies packing."
So `keep` is treated as necessary and not sufficient. The builder adds what a
taste verdict cannot express: provenance that survives to a consumer, and a
text-leak check.

## What qualifies, and the arguments

**`keep` only.** 143 of the 262 judged.

**`iterate` is excluded -- 56 assets.** Not on a rule, on his own words. Every
note Pip left on an `iterate` in this run is a complaint: *"slightly too washed
out, composition feels odd"*, *"this composition feels weird"*, *"slightyl too
crisp"*, *"a bit too warm/ soft?"*. The verdict is defined as "on-brief but not
final; regenerate to compare/hone -- the DEFAULT 'slight reject'". Publishing one
would publish an image he has already said is wrong. The honest response to
"the website wants more material" is a better generation run, not a looser gate.

**`discard` is excluded -- 63 assets.** Off-brief by his verdict.

**Unjudged is excluded -- 390 of the run's 652 images**, including the whole
`l1_grid` (220) and `l0_anchors` (54) blocks. Unjudged is not a quiet yes. Worth
noting because the one text leak found by eye before this pass
(`s17_f01`, "DESICCANT") sits in the unjudged remainder -- absence of a verdict is
absence of information, in both directions.

**Older Library assets are excluded, structurally.** The builder cannot emit an
entry without a run-ledger line and a per-file `.meta.json` sidecar, so an asset
whose origin cannot be established cannot enter -- it is a mechanism, not a policy
someone has to remember. This matters because
`docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md` measured the older material:
96.3% attributable by class, but 31.6% of packed assets have their only origin
evidence in a gitignored single-copy directory, and 6 are unattributable outright.
Evidence that weak cannot back a public claim. Widening the share set to cover
them needs the `coordination#32` backfill first, not a judgement call here.

## Tiers -- because the consumer wants images to LOOK at

A `keep` on a 1024x1024 colour swatch sheet and a `keep` on a 1536x1024 lit
interior are the same verdict and completely different publication candidates.
Handing over 143 undifferentiated paths would pass that sorting problem to the
website seat.

| tier | n | what it is |
|---|---:|---|
| `hero` | 5 | `keep` AND Pip typed an approving note. The strongest signal in the store. |
| `feature` | 121 | `keep`, text-clean scene, no note either way. |
| `reference` | 8 | `keep`, but a design-reference colour swatch sheet. **Not a publication candidate.** Interesting to us, meaningless to a reader. |
| `quarantine_text` | 9 | `keep`, but OCR found lettering. Excluded, with every detection listed. |

**126 publication candidates** (`publishable_candidate == true`).

The `hero` rule is worth stating plainly because it is doing a lot of work on a
small number: on this run, **every note on a `keep` is praise and every note on an
`iterate` is a reservation.** That is a measured property of these 262 verdicts,
not a general law -- the note text ships in each entry so a reader can check it
rather than take it. The five: *"love this"*, *"love this one"*, *"touch of green
is nice"*, *"nice and warm"*, *"Nice altar, good stylishness"*.

## The text leak, measured

The run put a global no-text instruction in every prompt
(`docs/design/ART_RUN_2026-08-07.md`: "Text, lettering or logos. Banned in every
prompt."). It leaked.

RapidOCR over all 262 judged masters: **17 images carry a detection, 14 of them at
confidence >= 0.60. Among the 143 keeps, 9 -- a 6.3% leak rate.** The worst are
not garbled at all, which is the point: `'Plan A'` / `'Plan B'` / `'Final
Decision'` at 0.85 on a whiteboard, and `'PENDING'` / `'APPROVED'` / `'REJECTED'`
at 0.83-0.88 on a status board. Some are garbled, which is worse for a public
surface: `'PENDOVED'`, `'PPROVED'`, `'Nex+ Steps'`, `'De Bg aat'`.

Ten of the seventeen are subject `s07`, one recurring status-board scene -- the
leak is concentrated in prompts that describe a surface a real room would letter,
not sprayed at random. That is actionable: fix the subject, not the pipeline.

**Any detection quarantines, not just a confident one.** The costs are
asymmetric -- a false quarantine loses one image out of ~130, a false pass puts a
garbled half-word on an image chosen precisely because it is prominent.

**Honest limit: the number is a LOWER BOUND.** OCR misses small, low-contrast,
stylised and partially occluded lettering. A clean scan is evidence of absence,
not proof of it. Re-run with `python tools/art_review/scan_text_leak.py`.

## Surfaces -- what these files actually support

Recorded per entry in `surfaces`, derived from pixel size rather than asserted.

- **Web and social: yes**, at any normal display size. 1536x1024 and 1024x1024 are
  comfortable for OG cards, post images, headers and lightboxes.
- **Print at poster size: no, for every entry.** 1536px long edge is about 5.1
  inches at 300dpi and this pipeline has no upscale path. `ART_RUN_2026-08-07.md`
  says it directly: "L3 produces print-ready *sources*, not printable posters...
  Do not claim upscaling happened." A poster needs a regenerated source, not a
  resample.

## Provenance -- mandatory, and its honest limit

Every entry carries `provenance`: `origin: generated_model`, the model, backend,
`run_id`, `job_id`, `prompt_sha256`, UTC generation timestamp, quality, and the
tariff cost. The full prompt text lives in `art_share_set_prompts.json` keyed by
`prompt_sha256`, **in git**, so a public claim ("machine-generated, this model,
this prompt") is substantiable from a fresh clone. It is a separate file only so
the manifest stays diffable -- 900KB of near-identical prompt bodies would drown
the review signal in `art_share_set.json`.

That design choice is deliberate given what the provenance scoping pass found: the
older material's weakness is precisely that its evidence lives in a gitignored
directory on one machine. Repeating that here would have been building the known
failure a second time.

**The limit, recorded rather than papered over: there is no seed.** The OpenAI
Images API exposes no seed parameter, so `seed` is `null` with a note in every
entry. The record establishes **what was asked for**. It does not make the exact
output reproducible. Any public copy should say "generated with this model from
this prompt", never "reproducible from this record".

Cost figures are tariff arithmetic (`cost_is_billed_truth: false`), not billed truth.

## Getting the actual pixels

**The manifest carries paths, not bytes, and that is not an oversight.**

The 126 candidates total roughly 350MB of PNG. `docs/art/ART_MASTERS_POLICY.md`
forbids art over 1MB in git and the masters archive bucket is deliberately
non-public and auth-only -- "Keep the bucket NON-public (auth-only, not a web
path)". So there is no existing surface from which the website can just fetch
these.

Bridging that is a deliberate handover and a decision for Pip, not something a
build script should do silently. The builder stages the candidates for it:

    python tools/assets/build_share_set.py --stage G:/tmp/pdoom1-art-masters/share_set_2026-08-07

That copies each candidate master plus its `.meta.json` sidecar, tier-prefixed in
the filename, alongside a copy of both manifests -- one directory, off git, ready
to be handed over by whatever route he chooses.

## Looking at it

    python tools/assets/build_share_set.py --html

writes `art_generated/share_set.html` -- a contact sheet grouped by tier, with
Pip's notes and the text detections shown on the cards. Derived output, gitignored,
regenerate rather than commit.

## What a share set cannot offer today

Every candidate here is an **L1** image: `medium` quality, one variant per cell,
generated in an unattended wave to cast a wide net. The run's L2 (controlled
single-axis variation on chosen winners) and L3 (few, large, `high` quality
heroes) are **unrun** -- they require a picks file and about USD 35 of the funded
budget is still unspent.

So the honest statement of what this delivers: 126 competent wide-net images that
Pip liked, suitable for web and social, none of them made to be a hero. If the
announcement run wants a genuinely striking lead image, the route to it is
spending the L2/L3 headroom on his chosen directions -- not lowering this bar.
That is his call to make, and this document exists so he can make it knowing what
the alternative already contains.
