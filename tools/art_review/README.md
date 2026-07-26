# art_review -- art triage pipeline (v2)

Status: LIVE

Local-first, browser-based triage for the game's two art libraries, plus a
stdlib analyzer that turns triage decisions into actionable promote / favour /
prune lists and an "untriaged" oversight-gap report. Pure Python 3.11 + self-
contained HTML; ASCII only; no external services at review time.

Two libraries, one workflow:

  * sprites -- the pixellab pixel-art library under `art_source/pixellab_*`
    (characters, cats, props, tilesets, cosmetics).
  * hero    -- the gpt-image-1 hero / banner / icon library under
    `art_generated/` (game_icons, ui_icons, hero_banners, ...).

Each library: a generator builds a self-contained review HTML, you triage in
the browser (tag + bulk-select), you "export JSON" to a tracked verdicts file,
then the analyzer reads the verdicts against the on-disk inventory.


## Shared house style -- review_style.py (CONVENTION)

ALL new internal review/dev HTML tools build on `review_style.py` instead of
hand-rolling CSS. It is the one place for the "warm cozy-grim CRT" look (dark
warm ground, subtle scanlines + vignette, amber/green accents, ASCII chrome)
extracted from the contact sheet / hero gallery, and it provides:

  * the shared vocabulary: PALETTE, VERDICTS, VERDICT_COLORS, CAT_PALETTE;
  * `page(...)` -- standard document wrapper: header block (tool name, date,
    count badges), intro note, footer;
  * `section(...)` / `image_cell(...)` -- collapsible sections and the standard
    image cell (checkerboard-under-alpha thumb, size-variant row, blurb,
    expandable prompt, verdict-chip slot);
  * verdict machinery -- per-cell chips, filter-by-verdict, export/import JSON
    in the flat `{rel: [tags]}` schema `analyze_verdicts.py` reads;
  * the completeness pass (`COMPLETENESS_JS` / `COMPLETENESS_CSS` /
    `completeness_controls()`), shared by ALL three sheets: sections render
    COLLAPSED by default (expand state persists per-section in localStorage;
    expand-all / collapse-all in the header); every section header carries a
    live "unreviewed N / M" rollup where parent headers aggregate their
    sub-sections; and a three-state show control -- ALL / HIDE DECIDED / ONLY
    UNREVIEWED (any verdict tag = decided). ONLY UNREVIEWED is the completeness
    pass: sections with 0 unreviewed disappear and the rest force-open, so the
    queue is exactly the items judgment has not reached. The rollup logic has a
    pure-Python mirror: `python tools/art_review/review_style.py --selftest`.

Compare-mode hook (issue #745): every `image_cell` carries `data-rel`, the
stable handle a compare-and-contrast mode needs. The planned shape: a "compare"
pin per cell collecting pinned cells into a fixed side-by-side tray (same
lightbox stage the hero gallery uses). Build it INSIDE review_style so every
sheet gets it at once.

Sheets on the shared style:

    python tools/art_review/gen_quirk_icon_sheet.py
        -> art_generated/quirk_icons_sheet.html
        Quirk icon set (#903/#909): shipped 64px icons grouped by valence with
        the theme_manager colour language, 64/32/16 readability rows, resolved
        prompts, verdict chips (exports quirk_verdicts.json, repo-relative
        godot/assets/... paths).

    python tools/art_review/build_cat_angle_ab_sheet.py [--source-root DIR]
        -> art_generated/cat_angle_ab.html
        Cat angle A/B vanguard (#900): old low-top-down vs new side-view on a
        floor-tiled strip, animated walk players. --source-root points at the
        checkout holding the A/B frames when they live in another worktree.

### Migration status

| tool | on review_style? | notes |
|---|---|---|
| gen_quirk_icon_sheet.py | YES | born on it (replaces the #909 inline one-off) |
| build_cat_angle_ab_sheet.py | YES | ported 2026-07-26 (layout CSS stays sheet-local) |
| gen_contact_sheet.py | PARTIAL | imports VERDICTS/VERDICT_COLORS + COMPLETENESS_JS/CSS + completeness_controls() from review_style; page CSS still inline -- it IS the style source |
| gen_hero_gallery.py + hero_gallery_template.html | PARTIAL | template keeps its own style/verdict colours, but the completeness engine is injected from review_style (`__RS_COMPLETENESS_JS__` / `__RS_COMPLETENESS_CSS__` placeholders) -- full style migration still a follow-up |
| serve_review.py | NO (follow-up) | different verdict model (keep/iterate/discard, server-persisted); adopt BASE_CSS only |

Follow-up rule: migrate a legacy tool only when its output can be verified
against a pre-migration render (the gen_contact_sheet.py byte-diff pattern).


## Pipeline -- sprites

    python tools/art_review/gen_contact_sheet.py
        -> writes art_source/pixellab_contact_sheet.html   (regenerable artifact)

    open art_source/pixellab_contact_sheet.html in a browser
        - filter by category / folder / filename; per-sprite verdict tags;
          checkbox + shift-click range select; bulk apply/remove bar;
          thumbnail = lightbox. Verdicts persist to that browser's
          localStorage.
        - click "export JSON" and SAVE the download over:
              art_source/pixellab_verdicts.json                (TRACKED source)

    python tools/art_review/analyze_verdicts.py --library sprites
        -> report to stdout + writes:
              art_source/promote_list.txt                      (regenerable)
              art_source/favour_list.txt                       (regenerable)
              art_source/disfavour_dislike_list.txt            (regenerable)


## Pipeline -- hero

    python tools/art_review/gen_hero_gallery.py
        -> writes art_generated/hero_gallery.html          (regenerable artifact)
        (pulls prompt/provenance from art_prompts/*.yaml|json + art_generated/logs;
         needs PyYAML. multi-size exports of one asset -- foo_v2_64/128/.../1024.png
         -- are deduped to one entry per (run-subdir, id, version).)

    open art_generated/hero_gallery.html in a browser
        - full-size lightbox + per-asset provenance (prompt, model, cost, hash);
          same tag + bulk-select controls as the contact sheet.
        - click "export JSON" and SAVE the download over:
              art_source/hero_verdicts.json                    (TRACKED source)

    python tools/art_review/analyze_verdicts.py --library hero
        -> report to stdout + writes:
              art_source/hero_promote_list.txt                 (regenerable)
              art_source/hero_favour_list.txt                  (regenerable)
              art_source/hero_disfavour_dislike_list.txt       (regenerable)


## analyze_verdicts.py

    python tools/art_review/analyze_verdicts.py                # both libraries (default)
    python tools/art_review/analyze_verdicts.py --library hero
    python tools/art_review/analyze_verdicts.py --library sprites
    python tools/art_review/analyze_verdicts.py --selftest     # synthetic checks

For each library it prints:

  1. Verdict summary   -- inventory total, tagged count, per-tag counts;
     PROMOTE + FAVOUR broken down by category and finer subtype.
  2. Imbalance + gaps  -- over-represented promoted subtypes vs zero/under-
     promoted subtypes that DO exist in inventory.
  3. UNTRIAGED report (the headline) -- inventory assets with NO verdict at
     all, by category/subtype and as a % of that category, most-first: the
     oversight gap, i.e. where judgment has not yet reached.
  4. Stale verdict paths -- tagged but no longer on disk.

and writes the per-library promote / favour / disfavour+dislike list files
(grouped by `# category/subtype`) named above. A missing verdicts JSON is
handled gracefully: it prints where to paste the export and skips that library;
the other still runs. stdlib only.

Paths are repo-relative (derived from the script's own location), so the tools
run from any working directory. `gen_contact_sheet.py` also accepts an
alternate art_source dir as `argv[1]`.


## Verdict JSON schema

Both `pixellab_verdicts.json` and `hero_verdicts.json` are a flat object
mapping a POSIX-style relative path to a list of verdict tags:

    {
      "pixellab_2026-07-19/objects/desk_decent_1.png": ["like", "promote"],
      "pixellab_2026-07-17/reroll/cats/cat_black_1_east.png": ["favour"],
      "game_icons/grant_proposal_v2_1024.png": ["promote"]
    }

  * sprite paths are relative to `art_source/`.
  * hero paths are relative to `art_generated/`; a verdict on ANY size variant
    of a deduped asset resolves to that asset's single entry.
  * a bare string value ("promote") is accepted and treated as ["promote"].
  * unknown tags are ignored; empty tag lists drop the key.

### the 5 verdict tags

    like        general approval / keep
    dislike     general rejection
    favour      shortlist -- a preferred candidate within its group
    disfavour   deprioritize (soft prune)
    promote     graduate into the game -- office sandbox + generation queue

`analyze_verdicts.py` acts on `promote` (promote list), `favour` (favour list),
and merges `disfavour` + `dislike` into the prune list. `like` is informational.


## Tracked source vs regenerable artifact

TRACKED (the durable human decisions + the tools):

    tools/art_review/review_style.py           (shared house style -- see above)
    tools/art_review/gen_contact_sheet.py
    tools/art_review/gen_hero_gallery.py
    tools/art_review/hero_gallery_template.html
    tools/art_review/gen_quirk_icon_sheet.py
    tools/art_review/build_cat_angle_ab_sheet.py
    tools/art_review/analyze_verdicts.py
    tools/art_review/README.md
    art_source/pixellab_verdicts.json      (sprite triage decisions)
    art_source/hero_verdicts.json          (hero triage decisions)

REGENERABLE, so gitignored (rebuilt any time from source + inventory):

    art_source/pixellab_contact_sheet.html
    art_generated/hero_gallery.html
    art_generated/quirk_icons_sheet.html
    art_generated/cat_angle_ab.html
    art_source/promote_list.txt
    art_source/favour_list.txt
    art_source/disfavour_dislike_list.txt
    art_source/hero_promote_list.txt
    art_source/hero_favour_list.txt
    art_source/hero_disfavour_dislike_list.txt

The rule: verdicts JSONs and the tooling are versioned; every HTML sheet and
every `*_list.txt` is a derived output and stays out of git.
