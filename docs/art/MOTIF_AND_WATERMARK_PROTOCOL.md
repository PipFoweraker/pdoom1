# Motif, lineage and watermark protocol -- DRAFT for ruling

> Status: **DRAFT, not adopted.** Written 2026-08-15 as a design card for Pip, and as the
> cross-repo proposal for `pdoom1-website` (consumer) and `pdoom-data` (schema judge).
> Nothing here is implemented. No code has been changed.

## What this is for

Three things Pip asked for, which turn out to be one object seen from three angles:

1. **Persistent motifs** -- a small recurring detail (the X in the corner of the office) that
   only a keen viewer notices, deliberately placed rather than accidental.
2. **Generational art** -- an asset family that visibly evolves across many iterations, so the
   set carries its own history.
3. **A watermark / metadata protocol** other repos can rely on.

## Scope split -- two tiers with different purposes (Pip, 2026-08-15)

These are NOT the same job and must not share a mechanism:

| | **Tier W -- website hero / poster art** | **Tier G -- in-game assets** |
|---|---|---|
| purpose | **disclosure.** Be upfront that a piece is AI-generated. | delight. The keen viewer notices a recurring detail. |
| threat model | none. Pip: "I don't mind people stealing it". Not anti-theft. | none. |
| mark style | **legible.** A mark you must hunt for is a bad disclosure. | grime-scale, deliberately easy to miss. |
| enters the `.pck`? | no -- so Godot import durability is irrelevant here | yes -- so the sidecar rules |
| metadata channel | `iTXt` + IPTC, fully durable on web-served PNG | sidecar manifest |
| status | **the near-term ask** | the longer game |

Pip's strategic claim, recorded because it drives the design: *the way to beat slop-dislike is
being upfront about it*, and then over time deliberately aiming for a mix of human, AI and
hybrid work as art direction. Disclosure is therefore not a compliance chore bolted on -- it is
the thing that makes a MIXED set legible, and a mixed set is the stated destination.

The object is a **lineage record**. The motif is what changes between generations; the
watermark is that record made visible; the metadata is that record made machine-readable.
One ledger backs all three, so the "keen viewer notices" experience is a CONSEQUENCE of
keeping the ledger, not a per-asset art-direction chore.

## What already exists (do not rebuild it)

| thing | where | what it already proves |
|---|---|---|
| deterministic sub-pixel stamping | `tools/art_review/butt_dot_stamp.py` | generation cannot hit 1-2px reliably; a PIL post-process can, and can be made to never halo |
| a vocabulary for recurring elements | `element:<thing>` harvest tags, `docs/art/NOMENCLATURE.md` | the SPEC exists. **The data does not** -- see "Measured, 2026-08-15" below. |
| 333 free-text review notes | `note` field in `review_log.jsonl` | the reusable reasons ARE being captured, in prose rather than in tags |
| an append-only decision ledger | `tools/art_review/review_log.jsonl` | lineage has somewhere to live that cannot silently overwrite itself |
| a per-asset origin guard | `tools/assets/check_provenance.py` | there is already a live trigger waiting for exactly this metadata channel (see "Manifund interaction") |
| a public export route | `tools/assets/build_share_set.py` | the website already has a supply line; lineage rides it rather than needing a new one |

## Measured, 2026-08-15 -- the harvest axis has never been used

An earlier draft of this doc claimed the motif catalogue was already being collected. That was
read off the SPEC (`NOMENCLATURE.md`) rather than off the DATA, and it is false. Counted over
`tools/art_review/review_log.jsonl`:

```
events: 506
verdicts: {'keep': 204, 'discard': 275, 'remix': 13, 'shelf': 3}
harvest tags: 0        # the `tags` list is empty in every single event
`element:` occurrences in review_log.jsonl and review_state.json: 0
events carrying a free-text note: 333  (274 of them discards)
```

Reproduce by parsing the `next.tags` and `next.note` fields of each JSONL line.

**What this changes.** A tag-counting motif report would return nothing, so it is not the next
step. The reusable material exists as PROSE -- notes like "too dark, brighten, decrease grain
slightly" and "Brighten, increase contrast, consider lighting some of the windows gently". A
meaningful fraction is boilerplate ("not chosen -- set winner: X") and must be filtered out.

**What this strengthens.** Rule 3 below is now evidence-backed rather than aspirational: 274
discard notes are 274 recorded questions a future generation could be made to answer.

**Implication for the review UI:** if motifs are wanted, the harvest-tag control needs to become
something a reviewer actually reaches for during a 470-asset session. Being present in the
vocabulary was not enough. Worth treating as its own small design question, not an assumption.

## Rule 1 -- the payload does not live in the pixels

Steganographic payloads (epoch or hash in low-order bits) are REJECTED for this estate.

Boundary conditions that destroy such a payload, all of which this pipeline does routinely:
nearest-neighbour downscale, palette quantisation, PNG re-optimisation, and Godot's texture
import re-encode. Each fails silently, and silent wrongness is the documented failure mode
here.

Channels, split by what survives:

| channel | carries | durability |
|---|---|---|
| visible stamped mark | an epoch number a HUMAN can count. Nothing machine-readable. | total -- a human reading it tolerates a resample |
| PNG `iTXt` chunk | the full lineage record | file copies, web, share set. Assume DROPPED by Godot import until measured. |
| sidecar manifest (`tools/assets/manifests/`) | the full lineage record | total, including in-game |

**Authority order:** sidecar manifest > `iTXt` > pixels. The pixels are an invitation to look
it up, never the record itself.

**Open measurement (do before adopting):** confirm whether `iTXt` survives
`godot --headless --path godot --import`. Expected answer is no, because the imported artifact
is `.ctex`, not PNG. Record the result here either way.

## Tier W -- do not invent an origin vocabulary, one exists

The three-way art direction Pip wants (some human, some AI, some hybrid) is ALREADY a
controlled vocabulary: **IPTC Digital Source Type NewsCodes**, the same field Adobe, Google
Images and most stock libraries read. Verified against `cv.iptc.org/newscodes/digitalsourcetype`
on 2026-08-15; the AI terms were added in the 2024 Q3 release.

Mapping, exact identifier strings:

| our category | IPTC term | IPTC definition |
|---|---|---|
| AI-generated | `trainedAlgorithmicMedia` | "Digital media created algorithmically using an Artificial Intelligence model trained on captured content" |
| human | `digitalCreation` | "Media created by a human using non-generative tools" |
| **hybrid A** -- human piece, AI touch-up | `compositeWithTrainedAlgorithmicMedia` | "Augmentation, correction or enhancement using a Generative AI model, such as with inpainting or outpainting operations" |
| **hybrid B** -- collage of human + AI elements | `compositeSynthetic` | "Mix or composite of several elements, at least one of which is Generative AI" |
| human retouch of an AI base | `humanEdits` | "Augmentation, correction or enhancement by one or more humans using non-generative tools" |

**The standard splits "hybrid" in two, and the split is worth adopting deliberately.** "A human
painted it and AI fixed the hands" (hybrid A) and "an AI background with a hand-painted subject"
(hybrid B) are different artistic positions and will read differently to an audience that cares.
Choosing which hybrids the project does is an art-direction decision, not a metadata one.

Full URI form for embedding: `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia`.

Two consequences:

1. `origin` in the record shape below should CARRY the IPTC term rather than a homegrown
   string. Homegrown wins nothing and loses interoperability. Keep the model name
   (`gpt-image-1.5`) as a separate field -- it is a different fact.
2. **MEASURED 2026-08-15, both halves. The API sends a signed credential and we destroy it.**

   Probe: one `gpt-image-1` generation, raw API bytes dumped BEFORE any decode, chunks walked,
   then the exact round-trip from `generate_images.py:338` applied and chunks walked again.

   ```
   RAW FROM API      chunks: IHDR(13), caBX(29030), IDAT(1070835), IEND(0)
                     markers: caBX, jumb, c2pa
   AFTER PIL SAVE    chunks: IHDR, IDAT x18, IEND
                     markers: NONE
   ```

   A **29,030-byte C2PA manifest** arrives on every image. Decoded, it asserts:

   ```
   digitalSourceType : http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia
   action            : c2pa.created   softwareAgent: gpt-image (pre-2.0)
   claim generator   : "OpenAI Media Service API"
   cert chain        : SSL.com C2PA ICA R1 -> "OpenAI OpCo, LLC" / "OpenAI Media Service"
   timestamp         : RFC3161 token, OpenAI TSA Issuing CA
   embedded icon     : the Content Credentials SVG badge
   spec              : c2pa 2.2.0
   ```

   **The IPTC term this document proposed writing by hand is already in there, signed.** Our
   disclosure problem was solved upstream and the pipeline has been deleting the solution since
   the first art night. A self-authored credit line is strictly weaker than a CA-signed one.

   **Tier W is therefore mostly a SUBTRACTION.** See "Tier W, revised" below.

   (Superseded finding, kept for the record: the earlier note below observed the strip on
   already-saved masters. That was correct but incomplete -- it could not tell whether anything
   was arriving. It was.)

3. **The pipeline strips every ancillary chunk (the earlier, partial measurement).** A raw PNG chunk walk over
   six generated masters in `art_source/iconset_2026-07-21/` returns `IHDR, IDAT..., IEND` and
   nothing else -- no `tEXt`, no `iTXt`, no `caBX` (the chunk C2PA / Content Credentials uses),
   no XMP.

   Cause is a PIL round-trip: `tools/assets/generate_images.py:338` and
   `tools/assets/run_art_night.py:735` both do
   `Image.open(BytesIO(img_bytes)).convert("RGBA")` and re-save. PIL does not carry unknown
   ancillary chunks across a decode/encode, so anything the API attached is discarded at that
   line.

   **What this does NOT prove:** that OpenAI attached a credential in the first place. The strip
   point is identified; the upstream presence is not. Settle it by hashing/dumping `img_bytes`
   to disk BEFORE the `Image.open` call on the next run and walking its chunks -- a few lines,
   one generation, definitive.

   If a credential IS arriving, preserving it is cheaper and far more credible than any mark
   this document proposes, and should be done first.

## Tier W, revised -- stop deleting it, then say what we changed

Ordered by value per unit of work. Step 1 is worth more than everything else in this document
combined, and is the smallest change in it.

### Step 1 -- masters keep their original bytes (the whole fix)

The credential covers the exact pixels it was signed over, so it can only be preserved on an
UNMODIFIED master. Write the API bytes straight to disk; keep the PIL decode only for
downscales.

In `tools/assets/generate_images.py`, replace:

```python
    # Decode and save master
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    img.save(master_path)
```

with:

```python
    # Master is written VERBATIM: the OpenAI response carries a signed C2PA
    # credential in a `caBX` chunk, and PIL drops unknown ancillary chunks on
    # re-encode. Measured 2026-08-15: 29,030 bytes of signed provenance,
    # asserting IPTC digitalSourceType=trainedAlgorithmicMedia. A re-save is a
    # silent deletion. Derivatives below are decoded copies and legitimately
    # carry no credential -- their pixels are not the signed pixels.
    master_path.write_bytes(img_bytes)
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
```

`tools/assets/run_art_night.py:735` has the same round-trip and needs the same treatment.

**Two things to check when applying, not to assume:**
- the master's pixel mode is now whatever the API returned rather than a guaranteed RGBA. If
  anything downstream assumes RGBA masters, it must convert on read.
- the probe used `background="opaque"`. Whether `background="transparent"` responses also carry
  `caBX` is UNVERIFIED -- re-run the probe once with transparent before trusting it for icons.

### Step 2 -- a verifier, so the guard is real

A credential nobody checks is a credential that quietly stops arriving. Proposed:
`tools/assets/check_credentials.py`, read-only, walks masters and reports how many carry a
`caBX` chunk. Fails when a master that HAD one loses it. Same ratchet doctrine as
`check_provenance.py`.

This also makes the honest claim available for the website: not "we say it is AI", but "here is
a signed credential you can verify yourself".

### Step 3 -- derivatives, which are ours and cannot be signed

Downscales, crops and composites break the signature by construction -- correctly, that is the
point of it. For those we make our OWN statement, in the sidecar and in `iTXt`, using the same
IPTC vocabulary, and pointing at the master that does carry the signed credential.

A derivative of an AI master that a human then paints over is `humanEdits` over
`trainedAlgorithmicMedia`, and this is exactly where the mixed-set art direction becomes
expressible rather than hand-waved.

### The visible Tier W mark

**Demoted by the C2PA finding.** A self-authored line is weaker evidence than a CA-signed
credential, so this is now a HUMAN-FACING courtesy for people who will never open a metadata
inspector -- not the disclosure mechanism. Optional, and safe to defer past steps 1-3.

Because the purpose is disclosure, the mark states rather than hides. Proposal: a single thin
line in the bottom margin, in the existing palette's muted slate, of the form

```
P(Doom)1 -- AI-generated -- epoch 4
```

ASCII only (issue #744). It is a credit line, not a watermark in the anti-theft sense, and
should look like a credit line. If a piece is later reworked by a human it gets the honest
version of the same line rather than losing it.

## Rule 2 -- two marks, on two clocks

### The chrome mark (automatic)

A tiny deterministic glyph in a fixed corner, stamped post-generation by the pipeline.

- Increments **per epoch**, not per asset. Every asset in a wave carries the same epoch mark.
- Zero art-direction cost. This is what makes the whole scheme survive contact with an art
  night -- if the mark needed a decision it would quietly stop happening by wave 3.
- Effect: two builds side by side, and the corner has ticked. Set-wide, free.
- Encoding proposal: N dark pixels in an L-shaped run, reading as grime at a glance and as a
  count when looked for. **ASCII-only constraint applies to any code/doc rendering of it**
  (issue #744); the glyph itself is pixels, not a character, so no gate risk.
- Epoch source: an `art_epoch.txt` SSOT at repo root, in the style of `ladder_version.txt`.

### The diegetic motif (opt-in, hand-placed)

A recurring in-world detail: the same chipped mug, a scratch on the same wall panel, a cat
that is present in exactly one more scene each epoch.

- Increments **per family**, decided by Pip.
- Sourced from harvested `element:<thing>` tags -- the motif candidates are already recorded;
  the missing piece is a report that ranks them by recurrence.
- Default for any new family is **no motif**. Motifs are earned by a tag showing up repeatedly,
  not assigned at birth.

## Rule 3 -- a generation is a reply, not a re-roll

Twenty undirected re-rolls is drift with a version number. The review system already emits the
questions: `remix` means "regenerate and compare", and `discard` prompts for a note because
"the reason is the reusable part" (`docs/art/NOMENCLATURE.md`).

**Proposed constraint:** a generation record MUST cite the review event it answers. A generation
that cites nothing is a variant, not a generation, and gets no epoch bump.

Consequence worth having: the 20-generation retrospective becomes a narrative with a spine, and
the dev-blog post is generated from the ledger rather than reconstructed from memory.

## Rule 4 -- lineage is a THIRD axis

`NOMENCLATURE.md` already separates two axes: a **verdict** is an asset's fate (exclusive), a
**harvest tag** is what survives that fate (any number). Lineage is neither:

| axis | question | cardinality |
|---|---|---|
| verdict | what happens to this asset? | exactly one |
| harvest tag | what outlives it? | zero or more |
| **lineage** | **what did it descend from?** | **exactly one parent, or none** |

Asset ids stay `gen:<batch>:<family>:<variant>` unchanged. Generation is NOT added to the id --
same reasoning that keeps resolution out of it: a verdict must not orphan its own relatives.

## Proposed record shape (v0.1 -- for pdoom-data to judge)

```json
{
  "schema": "pdoom1.art.lineage/0.1",
  "asset": "gen:art_night_2026-08-07:office:v3",
  "family": "office",
  "generation": 7,
  "parent": "gen:art_night_2026-07-27:office:v1",
  "epoch": 4,
  "answers": {"log_ts": "2026-08-13T09:14:22Z", "note": "corner reads flat"},
  "motifs": ["corner-x"],
  "digital_source_type": "trainedAlgorithmicMedia",
  "generator": "gpt-image-1.5",
  "mark": {"kind": "chrome", "epoch": 4, "corner": "br"}
}
```

`digital_source_type` is deliberately the same concept `check_provenance.py` tracks, expressed
in IPTC's vocabulary rather than a homegrown one. It is the field that makes this protocol worth
more than a novelty (below).

## Manifund interaction -- the real reason to build this

`tools/assets/check_provenance.py` records a live trigger: the application's blanket statement
that current assets are AI-generated IS the attribution, and that statement is true **only
while the set is homogeneous**. The moment one human-made asset ships, the set is mixed, the
blanket claim goes false, and per-asset origin becomes load-bearing for the first time.

Nothing currently supplies per-asset origin. This protocol does. Adopting it BEFORE the first
human-made asset lands converts an anticipated scramble into a field that was already there.
That is the strongest argument for this mission being more than decoration.

## Cross-repo asks

**Unverified, worth knowing about:** OpenAI's help-centre page on provenance signals states they
are also incorporating Google DeepMind's **SynthID**, a pixel-level watermark, into images from
ChatGPT/Codex/the API. If present, it survives our re-encode and every downscale -- meaning the
AI-generated fact may ALREADY be durably marked in the pixels of every derivative we ship. No
public detector was used here, so this is a claim read off a vendor page and NOT measured. Do
not repeat it as fact.

**`pdoom1-website`** -- consumer, and the ask GREW with the C2PA finding. Once masters keep their
credential, the site can offer verification rather than assertion: a hero image whose Content
Credential any visitor can check against SSL.com's chain is a much stronger answer to
slop-dislike than a caption we wrote. Concrete ask: serve masters with the `caBX` chunk intact
(confirm the CDN / image optimiser does not strip it -- most DO by default, and that is the
likeliest place this fix silently dies), and link the Content Credentials verifier.

Second ask, the original one -- a gallery surface: "this is generation 7 of the
office; here are 1 through 6, and here is the note each one answered." Supply route is the
existing share set (`tools/assets/build_share_set.py`), extended with a `lineage` block. No new
transport. Nothing to build until the schema is ruled.

**`pdoom-data`** -- schema judge and veto. The ask is narrow: does `pdoom1.art.lineage/0.1`
collide with, or duplicate, an existing provenance vocabulary? The failure mode to prevent is
two repos inventing two origin fields that disagree. Not a build request.

## Risk register

| risk | probability | mitigation |
|---|---|---|
| motif selection becomes a per-asset chore and the scheme dies by wave 3 | high (~70%) without mitigation | chrome mark is fully automatic; diegetic motif defaults to none |
| `iTXt` silently dropped and treated as authoritative anyway | high (~80%) if unmeasured | sidecar is authoritative by rule; measurement is a listed pre-adoption step |
| stamped mark haloes or lands on transparency | moderate | reuse the `butt_dot_stamp.py` algorithm: draw only over already-opaque pixels |
| watermark reads as DRM / distrust signalling to players | low (~15%) | mark is grime-scale and unbranded; it counts, it does not claim |
| epoch bumped without a real wave, numbers become noise | moderate | epoch is an SSOT file with the same discipline as `ladder_version.txt` |

## Decisions needed from Pip

0. **Tier W first?** Tier W (website disclosure) is smaller, has a named near-term purpose, and
   needs no Godot involvement at all. Recommendation: ship Tier W standalone, leave Tier G as a
   ruled-but-unbuilt design. They share a record shape and nothing else.
0b. **Which hybrids does the project actually want to make** -- hybrid A (human piece, AI
   touch-up), hybrid B (human/AI collage), or both? This is art direction, and the metadata
   follows it rather than leading it.
0c. **ANSWERED, both halves, measured 2026-08-15.** A 29 KB CA-signed C2PA credential arrives on
   every image and `generate_images.py:338` deletes it. Step 1 of "Tier W, revised" is now the
   top-priority item in this document and is ~2 lines. Ruling needed only on whether to apply it
   to the two call sites now or fold it into a wider art-pipeline change.

1. **Chrome mark: adopt per-epoch auto-stamping, or motifs only?** (Recommendation: adopt --
   it is the part that survives busy weeks.)
2. **Where does the chrome mark go on assets with no safe corner** (sprites, transparent props)?
   Options: skip them entirely (recommended -- backgrounds and banners carry the mark, sprites
   do not), or stamp into the sidecar only.
3. **First diegetic motif and its family.** The `element:` tag report should propose candidates
   rather than this doc inventing one.
4. **Does the epoch counter start at 1 now, or backfill over the existing waves?** (Recommendation:
   start at 1 now. A backfilled epoch is a claim about images nobody stamped.)

## Not yet built

Everything above. The next concrete step is a read-only report --
`tools/art_review/motif_candidates.py` -- that ranks `element:<thing>` tags in
`review_log.jsonl` by recurrence, so decision 3 is made from evidence rather than invention.
It changes no assets and can run before any of this is ruled on.
