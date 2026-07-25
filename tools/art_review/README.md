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

    tools/art_review/gen_contact_sheet.py
    tools/art_review/gen_hero_gallery.py
    tools/art_review/hero_gallery_template.html
    tools/art_review/analyze_verdicts.py
    tools/art_review/README.md
    art_source/pixellab_verdicts.json      (sprite triage decisions)
    art_source/hero_verdicts.json          (hero triage decisions)

REGENERABLE, so gitignored (rebuilt any time from source + inventory):

    art_source/pixellab_contact_sheet.html
    art_generated/hero_gallery.html
    art_source/promote_list.txt
    art_source/favour_list.txt
    art_source/disfavour_dislike_list.txt
    art_source/hero_promote_list.txt
    art_source/hero_favour_list.txt
    art_source/hero_disfavour_dislike_list.txt

The rule: verdicts JSONs and the tooling are versioned; every HTML sheet and
every `*_list.txt` is a derived output and stays out of git.
