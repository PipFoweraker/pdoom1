# Visual Asset Options Menu + Pipeline Inventory

**Date:** 2026-07-16
**Purpose:** A menu of dials for Pip to pick from, so visuals can iterate rapidly in parallel with playtesting. This is a **decision doc, not generated art** — nothing here has been generated or committed. Pick, then one command generates.
**Register (canonical, from `DESIGN_PHILOSOPHY.md` §"flavor and theme" + `WORLD_AND_LORE.md`):** Papers, Please deadpan around enormous stakes. Dark comedy in flat CRT type over raw grief ("HypNOTised: 2.1B", not casualty counters). Desaturated teal/olive Tarkov surfaces, warm amber CRT glow as the only saturated accent. Researcher archetypes are **flavors, never portraits of real people** — so archetype portraits are lore-safe.

---

## 0. TL;DR — what to do today

1. **Generate the 3 hero banners that are already scoped and on-register** (`art_prompts/hero_banners.yaml`, status `pending`). Zero new prompt authoring. `~$0.81` for 3 variants each. Fastest visible payoff: title screen + doom-spike event art + board-grant fanfare.
2. **Kill the 8 magenta/cyan placeholder icons** still showing in-game (IconLoader renders a checkerboard for unmapped actions). `~$0.96`. Matches existing icon style exactly.
3. **Pilot 6 researcher archetype portraits** — the single biggest lever for the XCOM/attachment feeling, and the one net-new art class. Do a small pilot to lock the look before scaling. `~$1.08`.

**Total first batch ≈ $2.85, ~51 images.** Cost is a rounding error; the real cost is your curation time in the HTML gallery.

---

## 1. Pipeline inventory — does it run today?

**Yes, it runs today.** Verified in this repo on 2026-07-16:
- `openai 2.8.0`, `Pillow 12.0.0`, `pyyaml` all importable in the local env.
- `python tools/assets/generate_images.py --file art_prompts/hero_banners.yaml --status pending --dry-run` succeeds and prints a `$0.27` estimate.
- **Only missing piece for a real run: `OPENAI_API_KEY` is not set.** Set it and generation proceeds (`export OPENAI_API_KEY="sk-..."`). No key needed for `--dry-run`.

### The three tools (`tools/assets/`)
| Tool | Role |
|------|------|
| `generate_images.py` | YAML → images via OpenAI (default) or Gemini (dormant). Cost estimate + confirmation, `--dry-run`, `--variants N`, `--force`, `--update-yaml`. |
| `select_assets.py` | Interactive CLI + **HTML gallery** (`--gallery generated` opens a browser, click winners, copy the `--select` command). |
| `promote_assets.py` | Copies selected variants into `godot/assets/`, `--mark-promoted`. |

### YAML-as-source-of-truth + composable style
Full prompt = `{styles} + {color_bias} + {prompt_tail}`. You write only a per-asset `prompt_tail`; the shared `styles`/`themes` block enforces visual consistency. Status flows `pending → generated → selected → promoted`. History (model, cost, prompt hash) is written back into the YAML. This is why 91 icons stayed coherent for ~$12.

### Backends / models
- **`openai` (default):** `DEFAULT_OPENAI_MODEL = "gpt-image-1.5"`. Same request shape as gpt-image-1 (model/prompt/size, `background=transparent` for alpha), caps landscape at 1536×1024.
- **`gemini` "Nano Banana Pro" (`gemini-3-pro-image`) — DORMANT.** Imported lazily; only via `--backend gemini` + `GEMINI_API_KEY`. **Key feature: `--reference-images` for style/subject consistency across a set.** This is the right tool if you want a *matched* portrait cast or a family of event-window art that shares a face/style — gpt-image-1.5 can't hold subject identity across images the way reference-conditioned Gemini can.

### ⚠ Setup gap to check before a paid batch
`generate_images.py` line ~41 carries a `TODO: confirm exact id vs live docs (snapshot: gpt-image-1.5-2025-12-16)`. The default model id is **unverified against the live API**. Two consequences:
- First real run may error on an unknown model id → confirm the current id (or fall back to `--model gpt-image-1`, which retires 2026-10-23).
- The cost table (`estimate_cost_per_image`) is **estimate-only** (`1024² ≈ $0.06`, `1536×1024 ≈ $0.09`, gemini `≈ $0.13`). Confirm against the live pricing page before assuming batch totals. Do a **single 1-image real generation first** to confirm id + true cost, then fire the batch.

### pixellab.ai
**Not integrated in-repo.** No pipeline, no references (only an aspirational "sprite sheet" line in `.github/ISSUE_MISSING_FEATURES.md` for animated cats). Pixel-sprite / office-sim work would be a *new* external workflow, not a dial you can pull today. All working generation today is the gpt-image-1.5 pipeline.

---

## 2. Current asset coverage (what exists)

| Class | State | Location |
|-------|-------|----------|
| **Action/role/resource icons** | Strong. ~200 icon instances, each at 64/128/256/512/1024. 36 mapped, 55 generated-but-unmapped, **8 still missing (show as placeholder)**. Style = desaturated teal/olive Tarkov single-symbol. | `godot/assets/icons/` (30 subfolders), routed via `autoload/icon_loader.gd` + `data/icon_mapping.json` |
| **Material surface textures** | Complete set, 10 tiles, 512px. bakelite/concrete/CRT-burnin/circuit/graphpaper/perforated-metal/linoleum/copper/painted-metal/plywood. | `godot/assets/textures/surfaces/` |
| **Terminal/CRT screen fills** | Complete set, 10 tiles, 512px. amber/blue-DOS/cyan-ISPF/gray-dither/green-phosphor, scanlines + noise variants. | `godot/assets/textures/terminal/` |
| **Menu backgrounds** | Present. Welcome/settings/pregame/leaderboard use circuit-trace bg + green scanline overlay. | `welcome.tscn` etc. |
| **Cats (running gag)** | Covered. 5 SVG doom-expression states + 8 web JPG photos (live, random-selected in game). Cat is currently `visible=false` in `main.tscn`. | `godot/assets/cats/{default,simple,incoming}/` |
| **Music** | 7 tracks. | `godot/assets/audio/music/` |
| **Hero / scene illustration** | **NONE promoted.** 3 banners scoped but still `pending`. | `art_prompts/hero_banners.yaml` |
| **Researcher/staff portraits** | **NONE.** Entire staff display is text + emoji + color-coded panels. | `employee_screen.gd`, `staff_perks_panel.gd`, `researcher.gd` |
| **Event/dialog window art** | **NONE.** Code-drawn green `StyleBoxFlat` panel. | `event_dialog.gd` |
| **Office/HQ background** | **NONE.** Main gameplay screen (`main.tscn`) has no background TextureRect at all. Unused concept art sits in the dump folder. | `godot/assets/dump_october_31_2025/` |
| **Fonts, SFX** | Empty (`.gitkeep`). | `godot/assets/fonts/`, `audio/sfx/` |

---

## 3. Existing scoped ideas found (this is a REFRESH, not a reinvention)

Three prior scoping artefacts exist. Reuse status matters:

1. **`art_prompts/hero_banners.yaml` — 3 SCENE banners, fully prompt-authored, `status: pending`, and already in the *current* canonical register** (Papers-Please / Tarkov / amber-CRT, 1536×1024). **This is the "scene generation we scoped" you remembered.** Ready to generate verbatim:
   - `banner_title_hero` — dim night AI-safety lab/open-plan office, CRT + amber glow, lone empty chair, whiteboard equations, server racks, cold city skyline. (Title screen.)
   - `banner_doom_rising` — same room, dread escalating: amber soured to red, warning strobes, a wall monitor showing one red curve climbing off-chart. (Doom-spike event.)
   - `fanfare_strategic_moves` — shadowed boardroom, a governing board granting the player authority; also doubles as first event-fanfare art. (Ties to `fanfare_popup.tscn`.)

2. **`docs/assets/ASSET_GENERATION_BATCH.md` — a 126-asset, 14-batch master list.** ⚠ **Stale palette.** It's written in the *old* "cyan/blue sci-fi, dark laboratory" register that predates the canonical desaturated-teal/olive + amber-CRT direction. **Do not generate it verbatim** — the colour-bias language fights the current look. Still-relevant chunks worth refreshing: Batch 1 (the 8 missing action icons), Batch 11 (doom-meter visuals), Batch 12 (event/dialog icons). The rest (leaderboard medals, scrollbars, settings icons) is low-value polish.

3. **`docs/assets/ICON_MAPPING_AUDIT.md` — the concrete "8 icons still needing generation" list:** `team_building`, `network`, `acquire_startup`, `sabotage_competitor`, `lobby_government`, `open_source_release`, `take_loan`, `grant_proposal`. These are the ones IconLoader currently renders as a magenta/cyan checkerboard placeholder in-game.

**Lesson from the rejected batch:** in `batch_3_backgrounds.yaml`, every *scene-as-background* attempt was rejected ("generated a scene layout instead of a tileable texture"). gpt-image-1 is bad at "seamless tileable texture" but **fine at full illustrative scenes** (that's exactly what the hero banners want). So: use it for scenes and single-symbol icons, not for tileable fills — the tileable surfaces you already have are enough.

---

## 4. Gaps ranked by player-visible impact (game is now playable)

| # | Gap | Why it matters now | New art? | Pipeline |
|---|-----|--------------------|----------|----------|
| **1** | **Researcher / staff portraits** | Personnel is the core loop (AP = the founder's own week; "costly humans who come with their own problems, bother"). The staff screen is pure text/emoji — nothing to attach to. Faces are the XCOM-recruit hook. Lore-safe as archetypes. | **Yes (net-new class)** | gpt-image-1.5, or Gemini if you want a matched cast |
| **2** | **Event / response-window hero art** | Events are the main narrative surface and the Papers-Please gravity lives here; currently a flat green box. Hero art per event *genre* (crisis / opportunity / board / blackmail) transforms the moment. | Partly scoped (`banner_doom_rising`, `fanfare_strategic_moves` cover 2 genres) | gpt-image-1.5 |
| **3** | **Title/menu hero + coherent CRT frame** | The game opens on text-on-texture. `banner_title_hero` is the single highest-visibility image in the product. A CRT bezel/frame overlay would unify every screen. | Title: scoped. Frame: net-new | gpt-image-1.5 |
| **4** | **8 missing action icons (placeholder killers)** | These literally render as a broken-looking magenta checkerboard during play. Cheapest possible credibility win; matches existing icon set exactly. | Refresh (prompts exist, palette needs updating) | gpt-image-1.5 |
| **5** | **Doom meter / doom-stream face** | `doom_meter.tscn` is procedurally drawn; a full `doom_meter` icon set (frame, safe/warning/danger/critical backgrounds, glow) **already exists in `assets/icons/doom_meter/` but is unused.** Mostly an *integration* job, minimal generation. | Mostly no (wire up existing) | — |
| **6** | **Office/HQ background** | `main.tscn` has no backdrop; unused concept art ("main office doom chair scene.png") sits in the dump folder. Could be wired or regenerated on-register. | Maybe (source exists) | gpt-image-1.5 |
| **7** | **Ledger / finance-offer chrome** | Ledger + the unbuilt ADR-0012 standing-offer selection UI are text/`StyleBoxFlat`. **Deprioritise generation** — Papers-Please deadpan *is* flat type on a leather panel; a letterhead/seal motif is the most this wants, and the offer-card UI needs building before it needs art. | Optional | gpt-image-1.5 |
| **8** | **Month-review / L1 plan-phase screen** | No UI surface exists yet (logic-only layer). Art is premature until the screen is designed. | Blocked on UI | — |

---

## 5. Per-asset-class dials (pick your settings)

For each candidate class: the tunable parameters, heavy-vs-light where it's a taste call, rough per-batch cost, and which pipeline fits. All costs are **estimate-only** pending the pricing confirmation in §1.

### A. Researcher archetype portraits ⭐ (gap #1)
The taste-defining batch. Pilot a small set first.

**Dials:**
- **Medium:** painterly bust *(heavy — matte-painting faces, XCOM soldier-card feel)* vs. flat CRT-ID-photo *(light — desaturated "personnel dossier" mugshot, dot-matrix printed, most on-register with Papers-Please)* vs. pixel portrait *(would need pixellab — not available today)*.
- **Framing:** head-and-shoulders vs. ID-badge with role stripe + fake employee number.
- **Palette:** strict desaturated teal/olive (matches icons) vs. warm-amber CRT tint (matches terminal).
- **Border/frame:** none / thin dossier frame / full laminated-badge treatment with corner wear.
- **Resolution:** 1024×1024 master (portraits read at 256 in-panel).
- **Variety axis:** one archetype per hireable role (safety_specialist, capability researcher, engineer, manager, ethicist, auditor) — matches the existing `employee_roles` icon taxonomy, and each wants 2–3 face variants so repeat hires don't clone.

**Recommendation:** flat CRT-dossier style, desaturated + amber tint, thin frame. It's the most on-tone AND the most forgiving of AI face weirdness (a slightly-off dot-matrix mugshot reads as *intended* grime; a slightly-off painterly face reads as broken).
**Pipeline:** if you want each role to look like a *consistent cast*, use **Gemini `--reference-images`** with one locked reference; otherwise gpt-image-1.5 is fine for independent archetypes.
**Cost:** 6 roles × 3 variants @ ~$0.06 ≈ **$1.08** (pilot). Full cast with variants later ≈ $3–5.

### B. Event / response-window hero art (gap #2)
**Dials:**
- **Scope:** full-scene banner *(heavy — like the scoped hero banners, one per genre)* vs. single-symbol vignette icon *(light — a 512px genre glyph in the dialog corner)*.
- **Coverage:** per-genre (crisis / opportunity / board / blackmail / discovery) vs. one generic "incoming transmission" frame reused with text.
- **Treatment:** painterly scene vs. "CRT broadcast still" (scanlines + amber, as if the event is coming in over a terminal).
- **Resolution:** 1536×1024 for banners, 512 for glyphs.

**Recommendation:** start with the 2 already-scoped banners (`banner_doom_rising`, `fanfare_strategic_moves`) — they cover crisis + board for free — then decide if per-genre banners are worth it after seeing them in the dialog.
**Pipeline:** gpt-image-1.5. **Cost:** covered by the hero-banner batch (§C); additional per-genre banners ~$0.09 × variants each.

### C. Title / menu hero banners (gap #3) — ALREADY SCOPED
**Dials (already set in `hero_banners.yaml`, but tunable):**
- **Aspect:** 1536×1024 landscape (fixed by the model's landscape cap).
- **Variants:** 1 (cheap, gamble) vs. 3 (recommended — image gen is stochastic; you want to pick).
- **Mood dial** (already in YAML as `mood_cozy_dread`): could push warmer/cosier or colder/more ominous.
- **Title negative space:** prompt already reserves upper-left for a title overlay — keep, so the title text/logo sits cleanly.

**Recommendation:** generate all 3 at **3 variants** as-is. No editing needed.
**Pipeline:** gpt-image-1.5. **Cost:** 3 × 3 @ ~$0.09 ≈ **$0.81**.

### D. The 8 placeholder-killer icons (gap #4)
**Dials:**
- **Palette:** must match the existing promoted icons → reuse `ui_icons.yaml`'s `base_corporate` theme (desaturated teal/olive, `surface_tarkov`). **Do not** copy the stale cyan/blue prompt_tails from `ASSET_GENERATION_BATCH.md` verbatim — keep the *subject* descriptions, swap the colour language.
- **Variants:** 2 each (these are small, single-symbol, low-risk).
- **Resolution:** 1024 master → auto-downscales to 64/128/256/512.

**Subjects (from ICON_MAPPING_AUDIT):** team_building (group/raised arms), network (handshake), acquire_startup (small building absorbed by larger), sabotage_competitor (hooded figure, red accent), lobby_government (capitol dome + briefcase), open_source_release (open book + branching arrows), take_loan (money bag + chain), grant_proposal (document + seal).
**Pipeline:** gpt-image-1.5. **Cost:** 8 × 2 @ ~$0.06 ≈ **$0.96**.

### E. CRT frame / bezel overlay (gap #3, optional unifier)
**Dials:** heavy chunky CRT bezel with screw holes + corner wear *(frames the whole game as a monitor)* vs. subtle vignette + scanline edge *(light, non-intrusive)*. Single 9-slice-able PNG or a full-screen overlay. **Taste call — mock both at 1 variant (~$0.12) before committing.**

### F. Doom meter (gap #5) — mostly integration, defer generation
The `doom_meter` icon set already exists unused. This is a "wire up what you have" task, not a generation task. Only generate if, after wiring, the existing frames don't fit the procedural gauge.

---

## 6. Recommended FIRST batch (today) — exact params

Two flavours depending on appetite. Both assume you've done the §1 single-image id/cost confirmation first.

### Light (fastest wow, ~$0.81, zero authoring): hero banners only
```bash
export OPENAI_API_KEY="sk-..."
# Confirm model id + true cost with ONE image first:
python tools/assets/generate_images.py --file art_prompts/hero_banners.yaml \
  --ids banner_title_hero --variants 1 --yes --update-yaml
# Then the rest:
python tools/assets/generate_images.py --file art_prompts/hero_banners.yaml \
  --status pending --variants 3 --yes --update-yaml
# Review + select:
python tools/assets/select_assets.py --file art_prompts/hero_banners.yaml --gallery generated
```
Delivers: title-screen hero, doom-spike event art, board-grant fanfare. ~9 images, ~$0.81.

### Recommended (full first-day payoff, ~$2.85, ~51 images)
Same hero-banner command above **plus** two new small YAMLs (to be authored — subjects listed in §5-D and §5-A; not created here because this is the options doc):
- `art_prompts/missing_action_icons.yaml` — 8 icons, `base_corporate` theme reused from `ui_icons.yaml`, 2 variants → ~$0.96.
- `art_prompts/researcher_portraits.yaml` — 6 role archetypes, flat CRT-dossier style (desaturated + amber, thin frame), 3 variants → ~$1.08. **Pilot — lock the look before scaling to the full cast.**

**Why this three-part batch:** (1) heroes = immediate visible transformation with zero authoring risk; (2) placeholder icons = removes the one actively *broken-looking* thing during playtests; (3) portrait pilot = de-risks the highest-value but highest-taste-uncertainty new class before you spend real curation time on it.

---

## 7. Open decisions for Pip (blockers)

1. **Portrait style:** flat CRT-dossier (recommended) vs. painterly XCOM-card vs. wait-for-pixellab. Pick one before the portrait YAML is authored.
2. **Portrait consistency:** independent archetypes (gpt-image-1.5) vs. matched cast (Gemini + reference image, needs `GEMINI_API_KEY`)?
3. **Confirm the model id / live cost** (§1 ⚠) — one throwaway image settles it.
4. **Per-genre event banners** — commit now, or decide after seeing the 2 scoped ones in the dialog?
5. **CRT frame** — worth mocking, or does the existing scanline treatment already carry it?
