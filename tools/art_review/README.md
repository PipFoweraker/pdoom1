# Art review pipeline

Status: LIVE

The end-to-end loop for triaging generated pixel-sprite art and turning an
owner's opinions into an actionable generation queue. Everything here is local
review tooling -- it never runs in CI or in the game. Python 3.11, stdlib only,
ASCII only.

Home for the tools is `tools/art_review/`; the data they read/write lives under
`art_source/` (kept in git for art <= 1MB, per `docs/art/ART_MASTERS_POLICY.md`).

## The 5-step flow

```
(1) generate contact sheet  ->  (2) triage in browser  ->  (3) export JSON
        gen_contact_sheet.py         pixellab_contact_sheet.html      save to
                                                                 pixellab_verdicts.json
                                                                       |
(5) generate toward the GAPS  <-  (4) analyze verdicts  <---------------+
    (office sandbox / next round)     analyze_verdicts.py
                                      -> promote/favour/prune lists
```

### 1. Generate the contact sheet

```
python tools/art_review/gen_contact_sheet.py
```

Scans `art_source/pixellab_*/` for images and writes a single self-contained
`art_source/pixellab_contact_sheet.html` (all CSS/JS inline; thumbnails are
`<img>` refs to the sprite files, so keep the HTML sitting inside `art_source/`
so the relative paths resolve). Also prints a category/run breakdown to stdout.

- Input:  `art_source/pixellab_*/**/*.{png,jpg,jpeg,gif,webp}`
- Output: `art_source/pixellab_contact_sheet.html` (regenerable, gitignored)
- Optional arg: a path to a different `art_source` dir
  (`python tools/art_review/gen_contact_sheet.py /some/other/art_source`).
  With no arg it resolves `art_source/` two levels up from the script, so it
  works from any cwd.

### 2. Triage in the browser

Open `art_source/pixellab_contact_sheet.html` in a browser. Per sprite you can
apply any of **5 verdict tags**:

| verdict     | meaning                                             |
|-------------|-----------------------------------------------------|
| `like`      | good enough to keep                                 |
| `dislike`   | bad; a prune candidate                              |
| `favour`    | shortlist -- prefer this within its subtype         |
| `disfavour` | de-prioritise; a prune candidate                    |
| `promote`   | pull into the game / next generation round          |

Selection + bulk tooling: per-tile checkbox, shift-click for ranges,
"select group" / "select" (per run / per category), "select all visible", then a
bulk apply/remove bar to stamp a verdict across the whole selection. Filter by
filename/category/folder and by verdict. Click a thumbnail to enlarge (Esc
closes). Verdicts persist to the browser's `localStorage`; if that is off a
warning shows and you must Export to keep them.

### 3. Export the JSON

Click **export JSON** in the sheet. It downloads `pixellab_verdicts.json`.
**Save it to `art_source/pixellab_verdicts.json`** (overwriting the tracked
copy). This file is the valuable, non-regenerable human decision data -- it is
tracked in git.

Export JSON schema -- a flat object mapping a sprite's `art_source`-relative,
POSIX-slash path to its list of tags:

```json
{
  "pixellab_2026-07-16/08-V8-fullcolor-chibi_east.png": ["like", "promote"],
  "pixellab_2026-07-17/reroll/objects/desk_decent_1.png": ["favour"]
}
```

(There is also an "export CSV" and per-verdict "copy PROMOTE / copy FAVOUR"
clipboard buttons for quick ad-hoc use; the analyzer below only reads the JSON.)

### 4. Analyze the verdicts

```
python tools/art_review/analyze_verdicts.py
```

Reads `art_source/pixellab_verdicts.json`, re-scans the on-disk inventory (same
classification logic as the contact sheet, so categories match exactly), and
prints an imbalance + coverage-gap report:

- verdict totals, and PROMOTE/FAVOUR broken down by category and finer subtype
  (so `props/coat_rack 40` vs `props/bin 2` is obvious);
- over-represented promoted subtypes per category, and under-/zero-promote
  subtypes that DO exist in inventory (the gaps to generate toward);
- STALE verdict paths (tagged but no longer on disk) and never-triaged counts.

It also writes three actionable path lists, each grouped by `# category/subtype`:

- Input:  `art_source/pixellab_verdicts.json` (+ the `art_source/pixellab_*/`
  inventory)
- Outputs (all regenerable, gitignored):
  - `art_source/promote_list.txt`            -- office sandbox + generation queue
  - `art_source/favour_list.txt`             -- shortlist
  - `art_source/disfavour_dislike_list.txt`  -- prune / ignore
- Optional arg: a path to a different `art_source` dir (same as the generator).
- `--selftest` runs a synthetic self-check of the classification/aggregation
  logic (no disk scan; used as a cheap sanity gate).

### 5. Feed the gaps into the next round

Take `art_source/promote_list.txt` into the office sandbox / next pixellab
generation round, and generate toward the GAPS the analyzer surfaces (the
under-/zero-promote subtypes), not just more of what is already over-represented.

## Sibling: hero gallery

`art_generated/hero_gallery.html` (if present) is a separate promoted-hero
gallery view. `art_generated/` is gitignored wholesale, so that HTML is a
regenerable artifact, not tracked source. (Its generator currently lives outside
this dir; home it here if it earns a permanent place.)

## What is tracked vs regenerable

Tracked source (commit these):

- `tools/art_review/gen_contact_sheet.py`  -- contact-sheet generator
- `tools/art_review/analyze_verdicts.py`   -- verdict analyzer
- `art_source/pixellab_verdicts.json`      -- the owner's triage opinions (data)
- this `README.md`

Regenerable artifacts (gitignored -- never commit; re-run the tools):

- `art_source/pixellab_contact_sheet.html`
- `art_source/promote_list.txt`
- `art_source/favour_list.txt`
- `art_source/disfavour_dislike_list.txt`
- `art_generated/hero_gallery.html`

Note: this dir also contains an OLDER, separate review app (`serve_review.py`,
`build.py`, `apply_review.py`, `verdicts.json`, and the various `*.html`) from a
prior icon/style pass. That is a different pipeline; the contact-sheet flow
documented here is the current one for pixellab sprite triage.
