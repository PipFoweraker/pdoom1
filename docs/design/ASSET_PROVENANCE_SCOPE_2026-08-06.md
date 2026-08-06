# Asset provenance -- scoping pass for `coordination#32`

- **Date:** 2026-08-06
- **Answers:** `coordination#32` (blocking party `pdoom1`, return date 2026-08-13)
- **Status:** SCOPING ONLY. Nothing built. Output is a decision for Pip.
- **Related:** ADR-0019 (pull-from-demand asset pipeline), `pdoom1#900`,
  `docs/art/ART_MASTERS_POLICY.md`, `tools/assets/demand/slot_picks.json`

## The one question

`coordination#32` promised, by 2026-08-13, an answer to: **can provenance be
captured retroactively for already-generated assets, or only prospectively?**

**Answer: retroactively, for the large majority -- but the evidence for a third
of the pack lives on ONE gitignored directory on ONE machine, and a backfill has
to run before that evidence is the thing that decides the number.**

Measured coverage: **491 of 510 packed art/audio files (96.3%) can have an origin
CLASS established today with named evidence. 6 files (1.2%) are genuinely
unattributable.** The rest of this document is how that number was produced, what
it does NOT cover, and where prospective capture should live.

## 1. Confirming the finding first

`coordination#32` was filed from an agent report. This pass checked it against
the code rather than relying on it. **The finding holds.**

- `docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md`
  (259 lines, read in full): defines Generated / Library / Packed and the
  packed-but-undemanded fourth state. **No `origin` field. The word
  "provenance" does not appear in it at all.**
- `godot/assets/`: no manifest of any kind. 536 files, of which 26 are non-art
  (README.md, .tres, shaders, .gitkeep) and **510 are art or audio**. Not one
  carries an origin marker.
- PNG metadata: checked with PIL on the oldest untraceable images. Info keys are
  `srgb`/`gamma`/`dpi` or empty -- no `tEXt` generation chunks, no EXIF. Nothing
  a generator wrote survived.
- `pdoom1#900` body, verbatim: *"Prereq before spending: confirm the
  gpt-image/pixellab pipeline logs prompt+params (provenance) so round-2 is
  queryable."* Still open, still a prereq.

One partial correction to `#32`'s characterisation, offered because it changes
the size of the job: batch metadata is **not only prose**. Two machine-readable
sources exist that `#32` did not name.

- `tools/assets/manifests/*.json` -- 11 generation manifests **tracked in git**,
  carrying prompts, palette anchors, sizes, `asset_type`, and the model
  (`generate_images.py:38-39`: default `gpt-image-1.5`, "gpt-image-1 retires
  2026-10-23"). These are the INPUT to generation, so they establish the origin
  class of everything a run produced.
- `art_generated/logs/*.log` -- 23 timestamped per-run logs written by
  `generate_images.py:73-104`. **In `art_generated/`, which `.gitignore:133`
  excludes.** Local-only.

So the pipeline DOES log prompt+params. What it does not do is carry any of it
across the promote step. `#32`'s core claim -- **stripped before a file reaches
the pack** -- is exactly right, and is the whole problem.

## 2. Retroactive coverage: the number and how it was measured

### Method

A scan hashed (SHA-256) every file under `godot/assets/` and every image/audio
file under `art_source/` (4,562 files) and `art_generated/` (5,183 files),
9,515 library files hashed in total. Each packed file was then matched by:

1. **content hash** to a library file (exact, no false positives);
2. failing that, **the git commit that first added it** (`git log
   --diff-filter=A --follow`), whose subject or body was searched for a named
   generator (`pixellab`, `gpt-image`, "AI-powered asset generation pipeline");
3. failing that, **hand inspection** of the file and any co-located INVENTORY /
   MANIFEST / README.

Every packed file resolved to an add-commit (0 files with no git history), so
tier 2 is available everywhere tier 1 is not.

### Result -- 510 art/audio files

| Evidence tier | Files | % | What it establishes |
|---|---:|---:|---|
| A. Content hash -> `art_source/` batch WITH a `MANIFEST.md` | 124 | 24.3% | Tool, mode, size, settings, and per-character pixellab UUIDs |
| B. Content hash -> `art_source/` without a manifest | 8 | 1.6% | The 8 contributor cat PHOTOS, staged with `art_source/cats_incoming/INVENTORY.md` |
| C. Git commit message names the generator | 198 | 38.8% | Origin class + tool, batch granularity |
| D. Content hash -> `art_generated/` only (GITIGNORED) | 161 | 31.6% | Origin class from batch dir + run logs -- **local-only** |
| E. Resolved by hand inspection | 13 | 2.5% | 8 music `.ogg` + 5 cat `.svg` (see below) |
| F. **Unattributable** | **6** | **1.2%** | Pre-2026 images, no record anywhere |

**Attributable: 504 of 510 = 98.8%** if tier E's hand-inspection cases are
accepted. Stated conservatively -- counting only tiers A-D, i.e. only where a
machine could rebuild the record without a human reading a file -- **491 of 510
= 96.3%**.

Tier E, resolved by inspection during this pass:

- **8 `.ogg` in `godot/assets/audio/music/`** are NOT model-generated audio. They
  are digital captures of hand-authored WebAudio patches: 13 `.js` patch files
  tracked in `tools/music/patches/`, rendered by `tools/music/capture_takes.py`
  per `tools/music/CAPTURE_RUNBOOK.md` ("records the WebAudio graph digitally").
  `tools/music/DIRECTION_NOTES.md:14`: *"godot/assets/audio/music/ now holds the
  8 composed oggs only."* Origin = procedural render of authored code.
- **5 `.svg` in `godot/assets/cats/default/`** are hand-written SVG, self-labelled
  in a comment: `<!-- Happy cat placeholder (0-20% doom) -->`. Origin = authored
  markup, not an image model.

### The 6 genuinely unattributable files

| File | First commit | Note |
|---|---|---|
| `godot/assets/images/office_cat.png` | 2025-09-04 "Master base cat image" | 1928x1808, 3.9 MB |
| `godot/assets/images/backgrounds/office_scene.png` | 2025-10-31 "Big update on theme + UI + glow button assets" | 1536x1024, 2.5 MB |
| `godot/assets/images/misc/cat_closeup.png` | same commit | 1024x1024, 1.8 MB |
| `godot/assets/images/misc/computer_1.png` | same commit | 1536x1024, 1.9 MB |
| `godot/assets/images/misc/computer_2.png` | same commit | 1536x1024, 2.6 MB |
| `godot/assets/ui/buttons/glowcat/cat_icon.svg` | same commit | Bundle copy in `art_source/dump_october_31_2025/` whose `README.txt` documents USE, never origin |

**These must be recorded as `unknown`, not inferred.** The temptation to infer is
concrete and should be named so it can be refused: 1536x1024 and 1024x1024 are
exactly OpenAI image-model output sizes, which makes "these are gpt-image output"
a very plausible guess. It is still a guess, and `coordination#32` already ruled
on this class of answer -- *"a worse answer than the alternative and still much
better than an inferred one."* An `unknown` that is honest is compliant; a
`generated` that is guessed is the failure the obligation exists to prevent.

Two of these six are also 1MB+ raster in git, which `docs/art/ART_MASTERS_POLICY.md`
forbids, and none is plausibly demanded under ADR-0019. Provenance backfill and
the ADR-0019 audit will hand Pip the same six files from opposite directions.

### The finding that should change the schedule

**Tier D is 161 files whose only evidence is `art_generated/` -- gitignored
(`.gitignore:133`), on one machine, not backed up by git.**

| Local-only batch | Files |
|---|---:|
| `art_generated/game_icons/v1` | 134 |
| `art_generated/screen_backgrounds/v1` | 10 |
| `art_generated/terminal_textures/v1` | 10 |
| `art_generated/core_resource_icons/v1` | 7 |

Of these, `game_icons` is partly rescued by `tools/assets/manifests/icons_v1.json`
+ `icons_v2.json` (both tracked, both `asset_type: game_icons`, 30 asset entries
between them at multiple output sizes) -- enough to establish the class in-repo,
not enough to map every one of the 134 files.

So there are two coverage numbers and they must not be conflated:

- **96.3% (491/510)** -- what can be established TODAY, on Pip's machine.
- **~64.7% (330/510)**, rising to ~91% if the `icons_v1`/`icons_v2` manifests are
  accepted as batch-level proof for `game_icons` -- what could be established
  from a **fresh clone**, if `art_generated/` were lost tonight.

The gap between those numbers is a single directory on a single disk. It closes
permanently the moment a backfill writes the record into git, and it is the
reason to do the backfill in the next week rather than after the pull step is
built. Estimated probability that `art_generated/` is lost or materially
disturbed before a backfill lands, absent urgency: low, maybe 5-10% over a
quarter -- but the loss is irreversible and the mitigation is a day of work.

## 3. Does `slot_picks.json` help?

Yes, materially, and it is the strongest argument for where capture belongs.

`tools/assets/demand/slot_picks.json` (written 2026-08-06, 136 slots + 15 frame
roles, generated by `tools/art_review/apply_slot_picks.py` from 2,713 verdicts)
already carries per-slot fields that are precisely provenance:

```
"godot/assets/icons/generated/action_policy_whistleblower": {
  "status": "chosen",
  "source_file": "art_generated/ui_icons/v1/action_policy_whistleblower_512.png",
  "source_asset": "gen:ui_icons:action_policy_whistleblower:v1",
  "destination": "godot/assets/icons/generated",
  "draw_px": 70,
  "draw_why": "action_bar_renderer.gd:227 custom_minimum_size 70x70"
}
```

`source_asset` is already namespaced with a `gen:` prefix -- a de facto origin
marker that nobody named as one. `source_file` points at the exact library file.

Two caveats that stop this being the answer on its own:

- It is **prospective only**: 136 slots not yet pulled, against 510 files already
  packed. It does nothing for the existing set.
- Its own `_comment` says *"the SELECTION authority the demand manifest
  (ADR-0019) consumes"* -- it is an input to the pull step, not an output that
  ships. It lives under `tools/`, outside `godot/`, so it never reaches the pack.

What it proves is the important part: **at the instant something enters
`godot/assets/`, the writing process already knows the source file and a source
identifier.** Provenance is not missing information. It is discarded information.

## 4. Prospective capture -- where should `origin` live?

### Constraint set

- Godot packs the **entire** `godot/` tree (`export_filter="all_resources"` in
  all three presets). Anything under `godot/` ships; anything outside does not.
- ADR-0019 clause 3 rejects file-list manifests: demand is declared as **pools**,
  because eight load sites construct paths at runtime.
- ADR-0019's enforcement doctrine: *"the rule lives in the only path that exists,
  not in a checker bolted alongside"* -- and its warning that a second write site
  "silently reopens the hole."
- `docs/art/ART_MASTERS_POLICY.md`: nothing over 1MB in git.

### Option A -- one tracked manifest under `godot/`, written only by the pull step

`godot/data/asset_provenance.json`, keyed by packed path, with content hash.

- **Ships to the pack for free** (Godot packs `godot/`), so the record travels
  with the build. The website can read it from the repo; a future in-game credits
  screen or `--dump-provenance` flag can read it at runtime.
- Diffable and reviewable: a provenance change shows up in PR review as text.
- Backfillable: the tiers above write straight into it, `unknown` included.
- Batch facts (model, prompt, tool version) are stated once and referenced by
  many files, so it does not force per-file prompt duplication.
- **Misses:** a file hand-copied into `godot/assets/` gets no entry. Detection,
  not prevention -- it needs ADR-0019's two-direction audit extended to a third
  direction (packed-but-unprovenanced) to catch drift. It is also a second write
  site unless the pull step is the ONLY writer, which is exactly the failure mode
  `is_ranked_run()`'s comment warns about; the mitigation is that the pull step
  emits it as a by-product of the write it is already doing, never as a separate
  step someone can forget.

### Option B -- per-file sidecars (`foo.png.prov.json`)

- **Misses:** nothing per-file -- but it roughly doubles the file count of
  `godot/assets/` (510 art files -> 1,020+ tracked files) alongside the existing
  `.import`/`.uid` pairs, which is the staging trap in CLAUDE.md made worse.
  Batch facts get repeated 134 times, so a correction to one model string is 134
  edits and rots the moment one is missed. And sidecars do not survive a file
  move any better than a manifest does -- worse, because the manifest's content
  hash can re-find a moved file and a sidecar just gets orphaned.

### Option C -- a field in the demand manifest (ADR-0019)

- **Misses the fundamental thing:** origin is a property of a FILE; the demand
  manifest declares POOLS ("at least 6 researcher portraits at 128px"). A pool
  cannot carry the origin of its members without becoming the file list ADR-0019
  explicitly rejected. Adding `origin` here either re-opens that rejected design
  or degrades to "this pool is mostly generated", which cannot answer "was THIS
  image generated?" -- the actual question.

### Recommendation

**Option A, with capture at the pull step and a three-value-plus-detail schema.**

- Location: `godot/data/asset_provenance.json` (under `godot/`, so it ships;
  under `data/`, alongside the other JSON the game already reads).
- Sole writer: the ADR-0019 pull step, which already holds `source_file` and
  `source_asset` from `slot_picks.json` at write time. Provenance becomes a
  by-product of the transform, not an extra chore -- structurally the same move
  ADR-0019 made for demand.
- Backstop: extend the two-direction audit to report packed-but-unprovenanced.
  Report, never delete -- same doctrine.

**The vocabulary needs to be wider than `generated` / `human` / `photo`.** This
scan turned up four distinguishable origins and one absence, and a schema that
cannot express them will force a lie at backfill time:

| `origin` | Example in the current pack | Count |
|---|---|---:|
| `generated_model` | pixellab characters, gpt-image icons | 483 |
| `authored_code` | 5 cat `.svg`, hand-written markup | 5 |
| `procedural_render` | 8 music `.ogg`, WebAudio patch captures | 8 |
| `photo` | 8 contributor cats, `godot/assets/cats/simple/` | 8 |
| `unknown` | the 6 pre-2026 images | 6 |

Alongside `origin`, carry `origin_detail` (tool + model + batch id),
`evidence` (which tier above established it), and `confidence`. The `evidence`
field is what makes the record auditable rather than merely asserted -- and it is
what lets a later pass upgrade a `git-commit-message` entry to a `manifest` entry
without re-litigating the whole file.

**On the `photo` bucket.** The 8 contributor cat photographs were contributed
with their owners' explicit permission (confirmed by Pip, 2026-08-06). Their
origin value is `photo`. There is no outstanding question here.

Two mechanical notes for whoever writes the backfill, because both are easy to
get wrong by sweeping on directory name:

- The `photo` bucket is exactly **8 shipped files**, all in
  `godot/assets/cats/simple/` (`web-arwen`, `web-arwen-chuck`, `web-chucky`,
  `web-doom-cat`, `web-luna`, `web-mando`, `web-missy`, `web-nigel`), and all 8
  are live -- `office_cat.gd:40-48` picks one at random, so every one reaches
  players. The `art_source/cats_incoming/` copies are byte-identical staging
  duplicates outside `godot/` and are NOT packed; a writer keying on both
  directories would double-count these 8.
- `godot/assets/cats/default/*.svg` (5 files) are `authored_code`, NOT `photo`.
  They sit under a `cats/` path and will be swept into the cat bucket by any
  rule that keys on the directory.

Separately, and independent of provenance: **the game has no in-game credits
surface.** `CREDITS.md` sits at the repo root and its own header states it "is
not bundled into the shipped build", and `office_cat.tscn`'s `ContributorLabel`
displays the CAT's name, not a person's (`office_cat.gd:48`). There is currently
nowhere in the product to credit anyone. Recorded as an observation; no fix
designed here.

## 5. What pdoom1 can and cannot promise the website by 2026-08-13

**Can promise:**

1. The retroactive/prospective answer itself -- **retroactive capture is
   feasible**, at origin-class granularity, for 96.3% of packed art/audio, with
   named evidence per file and a machine-reproducible method.
2. A specific, small unattributable set: **6 files**, enumerated above. The
   website can state "6 of 510 packed assets predate our records and are recorded
   as origin unknown" and that sentence is true and checkable.
3. The capture-point decision, argued, ready for Pip to accept or reject.

**Cannot promise by 2026-08-13:**

1. **A shipped mechanism.** The ADR-0019 pull step does not exist yet;
   `slot_picks.json` is only its selection input. Until the pull step exists,
   any provenance manifest is hand-written and can rot -- the exact risk ADR-0019
   already prices at ~20% for the demand manifest.
2. **Per-file generation parameters for the whole set.** Prompt/model/params at
   per-file depth exist for roughly the 132 hash-matched-to-`art_source` files
   plus the manifest-covered `game_icons`. For the rest, the honest depth is
   batch-level: "this file came from the 2026-07-26 pixellab worker re-base,
   `create_character` standard mode, size 64" -- not "this file's exact prompt
   string was X".
3. **Any answer for `pdoom-data`.** Unverified by this seat, as `#32` already
   flagged.
4. **An in-game credits surface.** None exists (see section 4). Nothing in the
   Manifund obligation requires one, but if the website's wording implies the
   game credits contributors, it does not.

**The dependency the website should know about:** the 96.3% figure is contingent
on a gitignored directory on one machine. Until a backfill commits the record to
git, a fresh clone supports roughly 65-91%. The website should not publish the
96.3% number before the backfill lands.

## Decision requested from Pip

1. Accept **Option A** (single tracked manifest at `godot/data/asset_provenance.json`,
   written by the ADR-0019 pull step) as the capture point? Or prefer B or C.
2. Accept the **five-value origin vocabulary** (`generated_model`,
   `authored_code`, `procedural_render`, `photo`, `unknown`) over the three
   values the workshop agenda assumed?
3. Authorise the **backfill to run before the pull step exists**, accepting a
   hand-written manifest as an interim, on the grounds that 161 files' evidence
   is currently single-copy and gitignored?
4. Rule on whether the **6 unattributable files** are recorded as `unknown` and
   kept, or removed (5 of them are 1MB+ and probably undemanded, so the
   ADR-0019 audit will ask the same question independently).
