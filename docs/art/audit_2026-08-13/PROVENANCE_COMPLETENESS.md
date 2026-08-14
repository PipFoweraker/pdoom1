# Provenance completeness -- art_night_2026-08-07 sidecars

Audit date 2026-08-13. Scope: the 1,098 `.meta.json` sidecars under
`art_generated/**/` and the 1,214-record run ledger at
`art_generated/art_night_2026-08-07/ledger.jsonl`.

**Read-only audit. Nothing under `art_generated/` was created, moved, edited or
deleted.** `art_generated/` is under MIGRATION-HOLD.

Every number below comes from one script, committed next to this file:

    python docs/art/audit_2026-08-13/provenance_census.py

Run from the repo root. Individual sections:
`--section 0` inventory, `1` field coverage, `2` cost, `3` mix, `4` prompt
clustering, `5` lineage, `6` PII, `7` publishability, `8` integrity,
`9` ledger reconciliation. Each claim below names the section that prints it.
Where a claim is my inference rather than a printed number, it is labelled
INFERRED.

---

## The headline: these records ATTEST, they do not REPRODUCE

**`seed` is `null` in all 1,098 of 1,098 sidecars (100.00%), because the OpenAI
Images API exposes no seed parameter.** The pipeline recorded the field as
explicitly `null` rather than omitting it, so a consumer can tell "no seed was
available" from "we forgot to record one". The sidecar carries a `seed_note`
saying exactly this, identically in all 1,098 files:

> The OpenAI Images API exposes no seed parameter, so this image is not
> reproducible from its record. Recorded as null rather than omitted so a
> consumer can tell the difference.

Consequence, stated plainly so no downstream wording drifts: **re-running the
recorded prompt against the recorded model with the recorded size, quality and
background will NOT return the recorded image.** These records establish what
was asked for, by which tool, against which model, at what time, and what came
back (byte count, token usage, API timestamp). They are an attestation chain.
They are not a reproduction recipe, and no publishable wording derived from them
may say "reproducible", "regenerate the same image", "deterministic", or
anything that implies a reader could re-derive the asset.

Verify:

    python docs/art/audit_2026-08-13/provenance_census.py --section 1
    # look for: -- always-null fields: ['revised_prompt', 'seed']

---

## 0. Inventory (section 0)

| Quantity | Value |
| --- | --- |
| Sidecar files found | 1,098 |
| Sidecars that failed to parse as JSON | 0 |
| Distinct `run_id` values | 1 (`art_night_2026-08-07`) |
| Distinct `level` values | 4 (L0, L1, L2, L3) |
| Distinct `block` values | 15 |
| Directories containing sidecars | 15 (`art_generated/an0807_*/v1/`) |

Every sidecar in the repo belongs to this one run. There is no second run mixed
into the scan. Other directories under `art_generated/` (`audiodump/`,
`iconset_round2/`, `ceremony_2026-07-31/`, ...) contain **no** `.meta.json`
sidecars at all -- which is itself a finding: provenance sidecars exist only for
this one night's output.

    find art_generated -name "*.meta.json" | wc -l          # 1098
    find art_generated -name "*.meta.json" | cut -d/ -f2 | sort -u   # an0807_* only

Per block:

| Block | Level | Images |
| --- | --- | --- |
| l0_anchors | L0 | 54 |
| l0_sheets | L0 | 18 |
| l1_family | L1 | 264 |
| l1_grid | L1 | 220 |
| l1_palette | L1 | 90 |
| l1_probe | L1 | 6 |
| l2_a_decay | L2 | 42 |
| l2_a_distance | L2 | 42 |
| l2_a_pitch | L2 | 48 |
| l2_a_quiet | L2 | 42 |
| l2_a_style_tween | L2 | 42 |
| l2_a_title_space | L2 | 42 |
| l2_a_yaw | L2 | 48 |
| l3_hero_land | L3 | 112 |
| l3_hero_port | L3 | 28 |
| **Total** | | **1,098** |

---

## 1. Field coverage (section 1)

**There are no sparse fields. All 33 top-level keys appear in all 1,098
sidecars (100.00%), and all 9 nested `api_usage` keys likewise.** The schema was
emitted by a single code path with no optional branches, and it shows.

Top-level keys, all at 1098/1098:

    api_created            api_usage             backend
    background             block                 cell
    cost_is_billed_truth   cost_source           cost_usd_tariff
    generated_at_utc       job_id                level
    master_bytes           master_path           model
    origin                 promotion_note        promotion_state
    prompt                 prompt_sha256         quality
    queue_spec_sha256      revised_prompt        run_id
    seed                   seed_note             size
    taste_profile_path     taste_profile_sha256  taste_profile_source
    tool                   variant

Nested, all at 1098/1098:

    api_usage.input_tokens
    api_usage.input_tokens_details.image_tokens
    api_usage.input_tokens_details.text_tokens
    api_usage.output_tokens
    api_usage.output_tokens_details.image_tokens
    api_usage.output_tokens_details.text_tokens
    api_usage.total_tokens

**Fields present but always null (2 of 33):**

| Field | Null count | Why |
| --- | --- | --- |
| `seed` | 1098/1098 | OpenAI Images API exposes no seed parameter. See the headline section. |
| `revised_prompt` | 1098/1098 | The API returned no revised prompt for any of the 1,098 calls. The field is a placeholder for a value the backend never supplied. |

`revised_prompt` being universally null is worth a second look: on DALL-E-3 the
Images API rewrote prompts and returned the rewrite, and a null there would mean
the record is silently missing the prompt the model actually saw. On
`gpt-image-1.5` / `gpt-image-2` I did **not** verify whether the API returns this
field at all. **I could not measure whether the recorded prompt is the prompt the
model actually received.** If it is not, the attestation is weaker than it looks.
Flagged in "what I could not measure".

Zero fields are present-but-empty-string, present-but-empty-list, or
present-but-empty-dict.

---

## 2. Cost (section 2)

**Every dollar figure in this section is a TARIFF ESTIMATE, not billed truth.**
All 1,098 sidecars carry `"cost_is_billed_truth": false`. The figures are
computed by the pipeline from a published per-image price table, not read back
from an OpenAI invoice or usage export. No reconciliation against a bill has been
performed, and this audit did not attempt one.

    python docs/art/audit_2026-08-13/provenance_census.py --section 2
    # cost_is_billed_truth values: {'False': 1098}

| Level | Images | Tariff estimate (USD) | Unit |
| --- | --- | --- | --- |
| L0 | 72 | 2.4480 | 0.0340 |
| L1 | 580 | 29.0000 | 0.0500 |
| L2 | 306 | 15.3000 | 0.0500 |
| L3 | 140 | 28.0000 | 0.2000 |
| **Total** | **1,098** | **74.7480** | |

Per block, tariff estimate (USD):

| Block | Images | Tariff estimate | Unit |
| --- | --- | --- | --- |
| l0_anchors | 54 | 1.8360 | 0.0340 |
| l0_sheets | 18 | 0.6120 | 0.0340 |
| l1_family | 264 | 13.2000 | 0.0500 |
| l1_grid | 220 | 11.0000 | 0.0500 |
| l1_palette | 90 | 4.5000 | 0.0500 |
| l1_probe | 6 | 0.3000 | 0.0500 |
| l2_a_decay | 42 | 2.1000 | 0.0500 |
| l2_a_distance | 42 | 2.1000 | 0.0500 |
| l2_a_pitch | 48 | 2.4000 | 0.0500 |
| l2_a_quiet | 42 | 2.1000 | 0.0500 |
| l2_a_style_tween | 42 | 2.1000 | 0.0500 |
| l2_a_title_space | 42 | 2.1000 | 0.0500 |
| l2_a_yaw | 48 | 2.4000 | 0.0500 |
| l3_hero_land | 112 | 22.4000 | 0.2000 |
| l3_hero_port | 28 | 5.6000 | 0.2000 |

Only three distinct unit tariffs appear across the run: 0.034 (x72), 0.05 (x886),
0.2 (x140). The tariff is a pure function of (size, quality), not of prompt
length or token usage -- **INFERRED** from the fact that unit cost is constant
within each (size, quality) combination while `api_usage.input_tokens` varies
per image.

**Finding -- a tariff applied to the wrong model.** All 1,098 sidecars carry an
identical `cost_source` string that names one model:

> OpenAI first-party model page for gpt-image-1.5, read 2026-08-06. Per-image
> output price by size and quality. [...] not billed truth -- see the plan.

But 6 of the 1,098 images were generated with **`gpt-image-2`**, and were priced
at the `gpt-image-1.5` tariff of 0.05 anyway (all 6 in `l1_probe`). The
attribution is honest -- the record says which model ran and says which model the
price came from, so the mismatch is visible rather than hidden -- but USD 0.30 of
the 74.7480 total is a price read from the wrong model's page. **I could not
verify what gpt-image-2 actually costs at 1536x1024 medium**; the error could be
in either direction.

    python docs/art/audit_2026-08-13/provenance_census.py --section 2
    # sidecars whose model is NOT the model named in cost_source: 6

**Failed calls cost nothing in this accounting.** The ledger's 116 failed rows
all carry `cost_usd: 0.0`, so the 74.7480 total covers only delivered images
(section 9). Whether the 348 underlying attempts (116 x 3) incurred any billed
charge is not measurable from these records.

---

## 3. Model / size / quality / background mix (section 3)

| Field | Value | Count | Share |
| --- | --- | --- | --- |
| backend | openai | 1,098 | 100.00% |
| model | gpt-image-1.5 | 1,092 | 99.45% |
| model | gpt-image-2 | 6 | 0.55% |
| size | 1536x1024 | 998 | 90.89% |
| size | 1024x1024 | 72 | 6.56% |
| size | 1024x1536 | 28 | 2.55% |
| quality | medium | 958 | 87.25% |
| quality | high | 140 | 12.75% |
| background | opaque | 1,098 | 100.00% |
| origin | generated | 1,098 | 100.00% |
| promotion_state | library | 1,098 | 100.00% |
| tool | tools/assets/run_art_night.py | 1,098 | 100.00% |
| taste_profile_source | brief-heading | 1,098 | 100.00% |

Full cross-tab -- only five combinations occur:

| model | size | quality | background | Count |
| --- | --- | --- | --- | --- |
| gpt-image-1.5 | 1536x1024 | medium | opaque | 880 |
| gpt-image-1.5 | 1536x1024 | high | opaque | 112 |
| gpt-image-1.5 | 1024x1024 | medium | opaque | 72 |
| gpt-image-1.5 | 1024x1536 | high | opaque | 28 |
| gpt-image-2 | 1536x1024 | medium | opaque | 6 |

Variant index: v1 x978, v2 x64, v3 x28, v4 x28.

Note the shape: `high` quality was spent exclusively on the 140 L3 hero images
(112 landscape + 28 portrait), and `background: opaque` is universal -- no
transparent-background asset was produced in this run at all. **INFERRED** from
the block/level cross-tab that quality tracks level, not subject.

---

## 4. Prompt clustering -- and why the obvious number is misleading (section 4)

The literal answer:

| Measure | Value |
| --- | --- |
| Images | 1,098 |
| Distinct `prompt_sha256` | 1,057 |
| Mean images per distinct prompt | 1.0388 |
| Largest cluster | 4 images |
| Prompts producing exactly 1 image | 1,021 (covering 1,021 images) |
| Prompts producing 2 images | 32 (64 images) |
| Prompts producing 3 images | 3 (9 images) |
| Prompts producing 4 images | 1 (4 images) |
| `prompt_sha256` that is not `sha256(utf8(prompt))` | 0 |

The hash field is trustworthy: all 1,057 hashes recompute exactly from the stored
prompt text, so a third party can verify the prompt was not edited after the
fact.

**But "1,057 distinct prompts" badly overstates how many distinct briefs this
was.** Every prompt in the run has the same structure: a long shared style
preamble, then the literal marker `SUBJECT:`, then the actual brief. Splitting
on that marker:

| Measure | Value |
| --- | --- |
| Distinct SUBJECT clauses across all 1,098 images | **23** |
| Distinct SUBJECT clauses among prompts that have one | 22 |
| Distinct pre-SUBJECT style preambles | 438 |
| Distinct prompts with no `SUBJECT:` marker | 9 |
| Largest SUBJECT cluster | **98 images** |

SUBJECT cluster sizes, largest first: 98, 65, 64, 61, 61, 58, 58, 56, 56, 55,
54, 54, 49, 48, 46, 44, 43, 22, 22, 22, 22, 22, 18.

So: **1,098 images came from roughly 22 distinct briefs, rendered through 438
distinct style preambles.** Mean 47.7 images per brief. This was overwhelmingly a
style-variation sweep, not a breadth-of-subject sweep -- which matches the block
names (`l2_a_pitch`, `l2_a_yaw`, `l2_a_decay`, `l1_palette`, `l1_grid` are axis
sweeps by construction). The prompt text that actually varies between two images
in the same cluster is a palette line, a composition line, or a camera line.

    python docs/art/audit_2026-08-13/provenance_census.py --section 4
    # -- brief vs variation --

Per-block ratio of images to distinct prompts is 1.00 everywhere except
`l0_sheets` (2.00: 18 images from 9 prompts, i.e. deliberate duplicate rolls) and
`l0_anchors` (1.10: 54 images from 49 prompts).

---

## 5. Brief lineage (section 5)

**One taste profile, three queue specs.**

`taste_profile_path` is a single value across all 1,098 sidecars:
`docs/design/TASTE_PROFILE_2026-08-06.md`, with a single
`taste_profile_sha256` of
`e6c7cdf700a0e64b7cf2ee83dd34a7b1f98950c3c23d99db24d714a2ad66c417`.

**That hash still matches the file on disk today (measured 2026-08-13).** The
taste profile has not drifted since the run. This is the strongest link in the
chain -- a reader can hash the file themselves and confirm.

    python -c "import hashlib;print(hashlib.sha256(open('docs/design/TASTE_PROFILE_2026-08-06.md','rb').read()).hexdigest())"
    # e6c7cdf700a0e64b7cf2ee83dd34a7b1f98950c3c23d99db24d714a2ad66c417

`queue_spec_sha256` has three values, and they partition the run cleanly by
level -- the queue manifest was edited between waves:

| queue_spec_sha256 | Images | Blocks |
| --- | --- | --- |
| `d4287c06daac339ee98606d27fd3953e01f379bed0bbbf8cff59dae245c38c20` | 652 | l0_anchors, l0_sheets, l1_family, l1_grid, l1_palette, l1_probe |
| `a74cfc26733e278ca7a516ef1e35d294167c8f27da0a7af0518ce719efe1a3db` | 306 | l2_a_decay, l2_a_distance, l2_a_pitch, l2_a_quiet, l2_a_style_tween, l2_a_title_space, l2_a_yaw |
| `8c2a2a8d6f72f444283dca4a1a9dc066287f267a1de37a0cd8ff8a431d61d108` | 140 | l3_hero_land, l3_hero_port |

No block mixes two queue specs. All 15 blocks map to exactly one.

**All three queue specs are recoverable**, which was not obvious -- only one of
them is the current working-tree file. The manifest at
`tools/assets/manifests/art_night_2026-08-07.json` was rewritten in place across
two commits, so the earlier two states survive only as git blobs:

| queue_spec_sha256 | Where it lives now |
| --- | --- |
| `d4287c06...` (L0+L1) | git blob `1fec3e0ca412` |
| `a74cfc26...` (L2) | git blob `cb475fdd1aba` |
| `8c2a2a8d...` (L3) | git blob `ce94bbe434ec` **and** the current working tree |

    git cat-file -p 1fec3e0ca412 | sha256sum   # d4287c06daac...
    git cat-file -p cb475fdd1aba | sha256sum   # a74cfc26733e...
    git cat-file -p ce94bbe434ec | sha256sum   # 8c2a2a8d6f72...

Or all three at once via `--section 5`, which walks the git history itself.

**Fragility worth naming:** the sidecar records a queue-spec *hash* but not the
queue-spec *path*, unlike the taste profile, which records both. Today the hash
resolves because someone (me, in this audit) hunted the git object graph. If that
manifest file is ever deleted and its history rewritten or the blobs GC'd, the
652- and 306-image waves lose their brief lineage with no recorded pointer to
what was lost. Adding `queue_spec_path` to future sidecars would cost one line.

---

## 6. PII / third-party risk (section 6)

**Clean.** No person's name, email address, real brand, or real organisation was
found in any prompt string or any filename in this run.

This matters because pdoom1-website#246 found third parties' names embedded in
publicly-fetchable filenames on production. That failure mode does not appear
here, and the reason it does not is structural rather than lucky: filenames in
this run are machine-generated coordinate tokens, and prompts are assembled from
a fixed clause library rather than typed freehand.

### What was searched -- prompts

Corpus: all **1,057 distinct prompt strings**, **7,123,519 characters** total.

| Check | Regex | Hits |
| --- | --- | --- |
| Email address | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | **0** |
| URL | `(?:https?://\|www\.)\S+` | **0** |
| Bare domain | `\b[a-z0-9-]+\.(?:com\|org\|net\|io\|ai\|co\|uk\|gov\|edu)\b` | **0** |
| Honorific + name | `\b(?:Mr\|Mrs\|Ms\|Dr\|Prof\|Sir\|Lady)\.?\s+[A-Z][a-z]+` | **0** |
| Two capitalised words in a row (the "Firstname Lastname" shape) | `\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b` | **0** |
| Non-ASCII codepoint | `[^\x00-\x7f]` | **0** |

Rather than only testing a blocklist, I enumerated the entire capitalised
vocabulary of the corpus, which is what would catch a name I had not thought to
look for:

- **Distinct mid-sentence capitalised tokens: 1.** The complete list is
  `['Tuesday']`, appearing 22 times, in the clause "an inspection carried out at
  4pm on a Tuesday by somebody who does not work here". A weekday, not a person.
- **Distinct ALLCAPS tokens: 99.** The complete list is printed by `--section 6`.
  Every one is either an instruction keyword (`ABSOLUTELY`, `NEVER`, `SUBJECT`,
  `PALETTE`, `RENDERING`, ...) or a generic technical acronym: `AI`, `UI`, `CRT`,
  `KVM`, `LTO`, `ARM`. None is a proper noun for a person or a company.

Two acronyms deserve an explicit clearing, since a naive brand scan would flag
them:

- **`ARM`** occurs in "WARM GRIME (CONTROL ARM, the incumbent house style)" --
  experimental-arm terminology, not Arm Holdings. 4 distinct contexts, all the
  same construction.
- **`CRT`, `LTO`, `KVM`** are generic hardware categories (cathode-ray tube,
  Linear Tape-Open, keyboard-video-mouse switch), used as prop nouns in an
  object-vocabulary list. None is a company name.

A word-boundary sweep for 25 specific brand and identity tokens (`openai`,
`anthropic`, `deepmind`, `google`, `microsoft`, `nvidia`, `intel`, `cisco`,
`oracle`, `amazon`, `tesla`, `sony`, `samsung`, `xerox`, `sharpie`, `post-it`,
`thinkpad`, `macbook`, `iphone`, `beacon`, `certes`, `pdoom`, `godot`, `github`,
`pip`) returned exactly one non-zero hit:

- **`beacon`, 1,048 occurrences, in exactly 1 distinct context:**
  "...a screen, an indicator lamp, an emergency beacon, a corona arc or the
  impossible thing itself..." -- the common noun, inside the shared lighting
  clause, hence the high count. Not Beacon the organisation. Verified by printing
  the surrounding 40 characters of every occurrence; all 1,048 are the same
  sentence.

Substring scans (as opposed to word-boundary) do produce false positives that a
careless auditor would report as findings, and I want them on record as
dismissed: `meta` matches 0 times at a word boundary but appears inside `metal`
(101 word-boundary occurrences of "metal"); `windows` matches 1,092 times but
every one is an architectural window in a room description, not the operating
system. **Neither is a brand hit.**

### What was searched -- filenames

Corpus: all **5,169 file and directory basenames** under
`art_generated/an0807_*/` and `art_generated/art_night_2026-08-07/` (that is the
1,098 sidecars plus 4,080 PNGs at multiple downscales, plus `ledger.jsonl` and
`l1_run.log`, plus the 16 directory names).

Rather than pattern-match for names, I extracted **every alphabetic run of 3 or
more letters across all 5,169 names**. The complete vocabulary is 27 tokens:

    anchors  art     decay   distance  family  grid    hero
    json     jsonl   land    ledger    log     meta    night
    palette  pitch   png     port      probe   quiet   run
    sheets   space   style   title     tween   yaw

**All 27 are pipeline vocabulary. Zero tokens fall outside it.** Everything else
in every filename is a coordinate (`s01_r01_p01_v1_1536`) or a pixel dimension.
There is no room in this naming scheme for a person's name to appear.

    python docs/art/audit_2026-08-13/provenance_census.py --section 6
    # tokens OUTSIDE the pipeline vocabulary: []

### What was searched -- path leakage

- `master_path` values that are absolute (would leak a local user directory):
  **0 of 1,098**.
- `master_path` values containing `Users`: **0 of 1,098**.

All paths are repo-relative, e.g. `art_generated\an0807_l0_anchors\v1\...`.
They use Windows backslash separators, which is a portability wart but not a
disclosure one.

### One caveat, stated rather than buried

The scan covers **prompt text and filenames**. It does **not** cover **image
pixels**. Nothing here rules out a face, a legible sign, a trademark, or a
readable name having been *rendered into* an image despite the prompts
instructing against it -- the prompts contain explicit "no text, no lettering, no
logo, no watermark, no identifiable real people" clauses precisely because the
model does not always obey them. `tools/art_review/text_leak_scan.py` and
`tools/art_review/text_scan_ALL_2026-08-13.json` exist and appear to address
exactly this, but I did not run or evaluate them, and this audit makes **no
claim** about pixel content.

---

## 7. Publishability gap (section 7)

A public provenance record needs four things. The sidecar carries two of them.

| Requirement | In the sidecar? | Detail |
| --- | --- | --- |
| **Prompt** | **YES, complete** | `prompt` (full text, 1098/1098) plus `prompt_sha256`, verified to recompute exactly. Publishable as-is. |
| **Tools** | **YES, complete** | `tool` (`tools/assets/run_art_night.py`), `backend` (`openai`), `model`, `size`, `quality`, `background`, `api_created`, `api_usage`, `generated_at_utc`. All 1098/1098. Plus the lineage hashes of section 5. |
| **Review state** | **NO -- absent from the sidecar entirely** | No `review_state`, `verdict`, `reviewed_at`, or equivalent key exists in any sidecar. `promotion_state` is present but is `library` for all 1,098 -- a constant carries no information about any individual image. |
| **Where-used** | **NO -- absent from the sidecar entirely** | No `where_used`, `used_in`, `consumers`, or `slot` key exists in any sidecar. |

Also absent from every sidecar, and needed before anything is published:
`license` and `usage_rights`. Neither key appears in any of the 1,098 files. The
record does not state under what terms the images may be used or redistributed.

### The two missing halves exist -- but not in the sidecar, and not completely

Review state and where-used are not nowhere. They live in separate files with a
different key scheme (`gen:<block_dir>:<cell>:v<n>`, derivable from the sidecar's
`master_path` + `cell` + `variant` but **not stored in the sidecar**). Their
coverage is partial:

| Source | Coverage of the 1,098 |
| --- | --- |
| `tools/art_review/review_state.json` | **262 of 1,098 (23.86%)** carry a verdict |
| `tools/assets/demand/slot_picks.json` | **0 slots, 0 frame_roles** -- the file's `slots` object is empty |
| `docs/copy/art_share_set.json` | names **143 of 1,098** masters |
| `tools/art_review/picks_l2_an0807_iterate.json` | 51 entries, all 51 resolve to run assets (4.6%) |
| `tools/art_review/picks_l3_an0807_keep.json` | 28 entries, all 28 resolve (2.6%) |

Verdict mix over the 262 reviewed: **143 keep, 63 discard, 56 iterate.**

Review coverage is wildly uneven by block -- five blocks are fully reviewed and
nine have not been touched at all:

| Block | Reviewed / total |
| --- | --- |
| l0_sheets | 18 / 18 |
| l1_palette | 90 / 90 |
| l1_probe | 6 / 6 |
| l1_family | 148 / 264 |
| l0_anchors | 0 / 54 |
| l1_grid | 0 / 220 |
| l2_a_* (all seven) | 0 / 306 |
| l3_hero_land | 0 / 112 |
| l3_hero_port | 0 / 28 |

**836 of 1,098 images (76.14%) have no recorded human verdict anywhere.**

### The gap, summarised

To publish a provenance record today you would have to join three files with two
different key schemes, and for 76% of images the review column would be blank and
the where-used column would be blank for all but 143. The sidecar is a strong
*generation* record and not yet a *publication* record. The cheapest closes,
**INFERRED** from the above and offered as options rather than recommendations:

1. Add `queue_spec_path` alongside `queue_spec_sha256` (section 5 fragility).
2. Add the canonical `gen:` asset id to the sidecar so the three files join on a
   stored key rather than a reconstructed one.
3. Add `license` / `usage_rights`, which no current file supplies at all.
4. Decide whether review state belongs *in* the sidecar (denormalised, goes
   stale) or stays external with a recorded pointer. **This is a design call, not
   an audit finding.**

---

## 8. Integrity checks (section 8)

These were not asked for, but they are cheap and they are what makes the
attestation worth anything.

| Check | Result |
| --- | --- |
| Masters referenced by a sidecar but absent from disk | **0 of 1,098** |
| Masters whose on-disk byte count differs from `master_bytes` | **0 of 1,098** |
| `sum(master_bytes)` | 3,117,291,134 bytes (2.90 GiB) |
| `sum(api_usage.input_tokens)` | 1,543,937 |
| `sum(api_usage.output_tokens)` | 2,827,354 |
| `sum(api_usage.total_tokens)` | 4,371,291 |
| `generated_at_utc` range | 2026-08-06T12:42:30.653445+00:00 -> 2026-08-07T13:24:27.900883+00:00 |

Every sidecar points at a file that exists and is the size the record says it is.
Note the limit: `master_bytes` is a **length** check, not a content hash. A file
could be swapped for a different image of identical byte length and this check
would pass. There is no content digest of the image anywhere in the sidecar.
**Adding `master_sha256` would turn a length assertion into a real one** --
flagged, not fixed, since this is a read-only audit.

The run spanned 24h 42m wall clock.

---

## 9. Ledger reconciliation (section 9)

The 1,214-record ledger and the 1,098 sidecars agree exactly.

| Measure | Value |
| --- | --- |
| Ledger records | 1,214 |
| `status: ok` | 1,098 |
| `status: failed` | 116 |
| 1,098 + 116 | 1,214 |
| Ledger `cost_usd` total (tariff estimate) | 74.7480 |
| Sidecar `cost_usd_tariff` total (tariff estimate) | 74.7480 |
| Ledger cost attributed to failed rows | 0.0000 |
| `ok` ledger rows with no matching sidecar | **0** |
| Sidecars with no matching `ok` ledger row | **0** |
| Cost disagreements, sidecar vs ledger, per `job_id` | **0** |
| `prompt_sha256` disagreements, sidecar vs ledger, per `job_id` | **0** |

Two independent records of the same run, written by the same tool, that do not
contradict each other on a single field. This is the part of the provenance story
that is genuinely solid.

**The 116 failures are one event, not scattered noise.** All 116 are in L3
(`l3_hero_land` 92, `l3_hero_port` 24), all have `attempts: 3`, all cost 0.0, and
all carry a byte-identical error:

> RateLimitError: Error code: 429 - {'error': {'message': 'You have no credits
> remaining. Add credits to continue using the API at
> https://platform.openai.com/settings/organization/billing/.', 'type':
> 'insufficient_quota', 'param': None, 'code': 'credit_balance_exhausted'}}

The run did not fail on content policy, rate shaping, or a bug. **It ran out of
credit partway through the L3 hero wave and stopped.** The L3 blocks were
therefore planned at 204 landscape + 52 portrait and delivered 112 + 28 -- L3 is
**54.7% complete** (140 of 256 planned). Nothing in the *sidecars* records this;
a consumer reading only the sidecars would see 140 L3 images and no indication
that 116 more were intended. The ledger is the only place the truncation is
visible, which is an argument for treating the ledger as part of the provenance
record rather than as a log.

That error string is also the only URL-shaped text anywhere in the run's records.
It is an OpenAI billing URL in a machine-generated error message, not
user-supplied content, and it lives in the ledger rather than in any sidecar
(section 6 measured zero URLs across all 1,057 prompts).

---

## What I could not measure

Stated explicitly rather than estimated. Each of these is a real gap in this
audit, not a formality.

1. **Whether the recorded prompt is the prompt the model received.**
   `revised_prompt` is null in all 1,098 records. I did not verify whether
   `gpt-image-1.5` / `gpt-image-2` return a revised prompt at all. If they do and
   the pipeline discarded it, the attestation is materially weaker than it
   appears -- the record would name a prompt the model never saw verbatim. I have
   no evidence either way.

2. **Billed truth.** Every dollar figure here is a tariff estimate. I did not
   access any OpenAI invoice, usage export, or billing API. The real spend for
   this run is unknown to this audit. The 74.7480 USD figure could be wrong in
   either direction, and the 6 `gpt-image-2` images (USD 0.30) are priced off a
   different model's page outright.

3. **What the failed 348 attempts cost.** 116 failed jobs x 3 attempts each are
   recorded at 0.0. Whether any of those attempts were billed is not derivable
   from these files.

4. **Image content.** No pixels were examined. No claim is made about whether any
   image contains a face, legible text, a logo, a trademark, or an identifiable
   real person, regardless of what the prompts instructed. `tools/art_review/`
   contains text-leak scanners that appear to target this; they were not run or
   evaluated here.

5. **Whether the masters are the images the API returned.** `master_bytes`
   matches on disk for all 1,098, but that is a length check. No content hash
   exists in any sidecar, so undetected substitution or corruption of an image at
   identical byte length is not ruled out.

6. **Provenance for the rest of `art_generated/`.** Only this one run has
   sidecars. `audiodump/`, `iconset_round2/`, `ceremony_2026-07-31/`,
   `action_icons_missing/` and the other directories have zero `.meta.json`
   files. I did not count those assets or assess what provenance, if any, exists
   for them elsewhere. **The 100% field-coverage result in section 1 describes
   the 1,098 files that HAVE sidecars, and says nothing about how many generated
   assets in this repo have no sidecar at all.**

7. **Whether the taste profile that hashes correctly is semantically the brief
   that was followed.** The hash proves the file has not changed. It does not
   prove the pipeline read it, or read all of it. `taste_profile_source` is
   `brief-heading` for all 1,098, which suggests only a heading was extracted,
   but I did not read `run_art_night.py` to confirm what it actually consumes.

8. **Copyright and licensing status of the outputs.** No sidecar carries a
   `license` or `usage_rights` field, and this audit does not opine on what terms
   apply. That is a legal question, not a measurement.
