# Session status + RESUME -- 2026-07-18 (pre-reboot handoff)

> Pip is rebooting Windows (memory/Explorer glitch). This is the durable handoff so a
> fresh Claude session resumes the v0.11.0 release with zero lost momentum. Everything
> below is already on origin/main unless marked otherwise.

## Release target (TODAY)
Friends & family DIRECT-DOWNLOAD Windows build of P(Doom)1 **v0.11.0** + a **live
leaderboard loop** (a friend's name showing on the board = the payoff). Music =
placeholder (deliberately out). Steam later; web port later. No release-and-patch
same day -- get the loop right once.

## State: GREEN and assembled
- origin/main tip `6a61f71` = full release codebase: alpha(#664) + P0(#691) +
  hotpatch(#694) + sync-client(#680) + anti-hollow-tests(#687) + metadata(#695) +
  palette(#693) + music-kit(#692) + overlay-tool(#696).
- Fast gate: **482 tests / 0 failures**. Exports clean at 0.11.0.
- Version single-source: `version.txt` = 0.11.0; run `python tools/sync_version.py`
  after any bump (stamps export_presets.cfg + project.godot; `--check` gates drift).

## TWO pending inputs = the ONLY blockers
1. **OpenAI key** -> `G:\tmp\pdoom-openai.env` containing `OPENAI_API_KEY=sk-...`.
   Personal account (burn the $40). NOT Beacon (no nonprofit/personal commingling).
   Verify org first (image-model KYC).
2. **Dreamhost `base_url`** -- after SFTP + token + writable DATA_DIR.

## RESUME RUNBOOK
### A. Score loop (release-critical)
1. Pip: SFTP `server/leaderboard/score_api.php` to a Dreamhost web dir -> that dir's
   URL = `base_url`. Set the token in score_api.php (or `.htaccess SetEnv
   PDOOM_SCORE_TOKEN`). Create a PHP-writable DATA_DIR outside web root.
   (See `docs/deployment/LEADERBOARD_SERVER_SETUP.md`.)
2. Claude: edit `godot/data/leaderboard_config.json` -> base_url, token (below),
   `enabled=true`. Commit to main.
3. Claude: export final Windows build at 0.11.0 (Godot headless
   `--export-release "Windows Desktop"`), config now baked in.
4. Claude: TEST round-trip -- curl POST a score with `X-PDoom-Token`, GET it back,
   confirm it stored.
5. Claude: zip (PDoom.exe + PDoom.pck + *.dll), tag `v0.11.0`, cut a GitHub Release,
   upload the zip.
6. Claude: post the download URL + base_url into website issue #140.
### B. Icons (art, NOT release-blocking)
1. Claude: patch `tools/assets/generate_images.py` `_openai_generate_bytes` to pass
   `background="transparent"` (glue gap #2 from ASSET_PIPELINE.md).
2. Claude: `set -a; . /g/tmp/pdoom-openai.env; set +a; python tools/assets/generate_images.py
   --file tools/assets/manifests/icons_v1.json` (default backend openai, model
   gpt-image-1.5, ~$0.06/img).
3. Review outputs (needs art_generated->review-viewer bridge, glue gap #1); promote keeps.

## Leaderboard shared token (goes in BOTH server + game config)
`SXeZs3NOV37AH5_uv6Nc_R41yq3ZfzzHPuUMYCHzPPujNMBj`
(Low-value shared secret; ships inside the public build; rotate if the board is abused.)

## Cross-repo issues filed (they own the work; do not touch their files)
- pdoom1-website #139 (version single-source), #140 (launch: download link + live board)
- pdoom-data #26 (expose A/B/C/D event tiers for feed salience)

## Open PRs pending Pip review (NOT release-critical)
- #690 art sweep review + tabbed viewer (winner-radio dropped; re-add is Pip's call)
- #649 visual asset options, #650 player-facing audit, #663 officefloor walks
- #682 adaptive-music (placeholder audio -- hold for real stems from the Fable lane)

## Deprioritized for the release (authorized, not fired)
- Pixellab tile/texture library (floors/walls/odd tiles) -- palette ready, not run.
- Doom colour system: hero palette covers only the purple/eldritch end; green + amber/fire
  zones need hand-authoring (see `tools/art_review/doom_overlay_preview.html`).

## Dev tools / assets
- Doom overlay preview: `tools/art_review/doom_overlay_preview.html` (on main, #696).
- Art review viewer: `tools/art_review/build.py` -> style_review.html (tabbed, verdicts baked).
- Palette: `docs/art/palette.json` (24 colours from hero); icon manifest
  `tools/assets/manifests/icons_v1.json` (6 icons incl robot-skull doom, GPU compute).
- Release notes DRAFT: `docs/releases/v0.11.0.md` (Pip to voice-pass; becomes Release body).

## Music (SEPARATE Fable window/session -- DIES ON REBOOT)
Before rebooting: have the Fable window SAVE its work-in-progress patches to disk + a
short "where we are" note (the conversation context is lost on reboot; disk survives).
Profiles: `tools/music/profiles/*.json`. Refs: `tools/music/ref_local/` (gitignored).
Drop-in kit + tier map: `docs/audio/MUSIC_DROPIN_KIT.md` (5 tiers cosy/uneasy/spooky/
eldritch/terminal; .ogg; 4s crossfades; files -> godot/assets/audio/music/).

## Local artifacts (regenerable; on disk, survive reboot)
- Test export at 0.11.0 (enabled=false):
  `.claude/worktrees/release-build/builds/windows/test-0.11.0/` -- re-export the FINAL
  build after the live config is wired.

## How to resume after reboot
Start a fresh Claude in the repo; point it at THIS doc. Do the two pending inputs
(OpenAI key file + Dreamhost base_url), then run Runbook A (release) and B (icons).
Nothing of Claude's was mid-flight -- all agents completed and merged, so the reboot
interrupts no in-progress work.
