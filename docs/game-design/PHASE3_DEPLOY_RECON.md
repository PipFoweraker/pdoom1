# Phase 3 deploy recon -- "both-channel" epoch kickover (v0.13 build + backend rotation)

Read-only recon, 2026-07-23, for the Friday deployment plan. Sources: code reads,
live-API probes (GET only), gh queries. NOTE: several files (game_config.gd,
ladder_version.txt, sync_version.py targets) were mid-edit by other agents during
this recon -- treat line numbers as gist, re-verify at cutover.

## 1. League / seed rotation -- how it works TODAY

**Rotation is client-side only, and currently broken-frozen, not scheduled.**

- The board seed comes from `GameConfig.get_weekly_seed()`
  (`godot/autoload/game_config.gd`, ~line 361): `"weekly-%d-w%d" % [year, week % 52]`
  -- but `week` is computed from `Time.get_ticks_msec()` (milliseconds since
  ENGINE START, not epoch time). Result: week is always 0. The live seed is
  frozen at **`weekly-2026-w0`** and will not change until the year rolls over.
- Confirmed empirically: `GET api.pdoom1.com/score_api.php?seed=weekly-2026-w0&version=v0.12.0`
  returns the live friends-and-family board (real entries, top score 287);
  `weekly-2026-w29` (the correct ISO-ish week) is empty.
- `godot/scripts/core/seed_schedule.gd` is NOT the rotation mechanism. It is the
  ADR-0005 per-run cause schedule (inputs-only invariant: rival funding waves,
  aggression shifts, injected events). Rotation-relevant only in that a future
  league seed carries a schedule.
- ADR-0016 (league metabolism, `docs/game-design/decisions/ADR-0016-league-metabolism.md`):
  MONTHLY league cadence ruled; each month = world-update pack + new baseline
  seed + league notes. **None of that pipeline is implemented.** There is no
  code path today to designate "this league's seed" other than the broken
  weekly generator or the player typing a custom seed.

**What a kickover actually changes:** the seed string clients play/submit with,
and the version half of the board key. Both are CLIENT-side values shipped in
the build (`game_over_screen.gd` submits `GameConfig.get_display_seed()` +
`"v" + GameConfig.CURRENT_VERSION`). The SERVER needs no change to open a new
board -- `score_api.php` auto-creates a board file for whatever
`(seed, version)` pair a client sends. Server-side work is only needed for
aliasing/archiving OLD boards and for what the website displays.

## 2. Build / release mechanics

`tools/build_release.py` end-to-end:

1. `rm -rf godot/.godot` (defeats the stale-export-cache trap; ~12 cycles burned
   in v0.11.0 without this).
2. Writes a uniquely-named freshness marker `.gd` file into the project.
3. Runs `tools/write_build_stamp.py` (commit/date/branch -> `godot/build_stamp.txt`;
   FATAL if it fails) and `tools/sync_version.py --check` (WARN-only here;
   the fatal gate is CI/pre-commit).
4. `godot --headless --path godot --import` (non-zero tolerated; cold-cache noise).
5. `godot --headless --path godot --export-release "Windows Desktop" builds/windows_desktop/PDoom.exe`.
6. VERIFIES the marker token bytes are present in the emitted `.pck` (or exe) --
   exits non-zero if the pack is stale. Marker deleted afterward.
7. Prints PASS + reminder: the human release-build playtest
   (play -> lose -> leaderboard) is the final ship gate.

**Exact v0.13 cut + publish steps (Pip local, from a clean main):**

```
# 1. bump SSOT (on main, freshly fetched -- see caveat below)
#    edit version.txt -> 0.13.0
python tools/sync_version.py          # stamps game_config.gd, project.godot,
                                      # export_presets.cfg, welcome.tscn
#    (epoch cut: also bump ladder_version.txt -> 2, IF the ladder split has landed)
#    commit both + the stamped files; pre-commit runs sync_version --check

# 2. build (nukes .godot, stamps, exports, proves freshness)
python tools/build_release.py
#    -> builds/windows_desktop/PDoom.exe + PDoom.pck

# 3. package -- MANUAL, no current tool (v0.10.1-era scripts are archived).
#    Zip: PDoom.exe, PDoom.pck, the 2 Steam dlls, HOW-TO-RUN.txt
#    -> PDoom-v0.13.0-windows.zip (v0.12.0 asset was named PDoom-v0.12.0-windows.zip)

# 4. publish
gh release create v0.13.0 PDoom-v0.13.0-windows.zip \
  --title "P(Doom)1 v0.13.0 -- <name>" --notes-file <notes.md>

# 5. FINAL GATE: extract the zip to a clean dir, play -> lose -> verify the score
#    lands on the NEW board:
curl "https://api.pdoom1.com/score_api.php?seed=<new-seed>&version=<new-key>&limit=5"
```

CAVEAT: this worktree's `version.txt` reads `0.11.0` but **main reads `0.12.0`**
(verified via gh) -- the Friday bump must be cut from freshly-fetched main, not
this branch. `.github/RELEASE_CHECKLIST.md` is stale (references archived
`package_release.sh` / `create_github_release.sh`) and is mid-edit.

## 3. Backend / leaderboard server

- **Score API** (PR #680, merged): single-file PHP, source in THIS repo at
  `server/leaderboard/score_api.php`, deployed on DreamCompute (nginx + php-fpm)
  at `https://api.pdoom1.com/score_api.php` (client config:
  `godot/data/leaderboard_config.json`, endpoint = base_url + `/score_api.php`).
  Deploys are MANUAL uploads -- no CI from this repo touches the box.
- **Board keying (server):** flat JSON file per board:
  `DATA_DIR/board_<safe(seed)>__<safe(version)>.json`. Both key halves come from
  the CLIENT (query params on GET, body fields on POST). Top-100, ADR-0002 sort
  (score DESC, doom_integral DESC), idempotent on entry_uuid, POST gated by the
  shared `X-PDoom-Token`, GET public. Boards are auto-created on first POST.
- **Live board:** `board_weekly-2026-w0__v0.12.0.json` (confirmed via GET).

**Ladder/epoch state (BUILD_VS_LADDER_VERSION_SPLIT.md, draft ADR-0018):**
board key should move from `"v"+CURRENT_VERSION` to `GameConfig.get_board_version()`
returning `"L"+LADDER_VERSION`. As of this recon: `ladder_version.txt` (value `1`)
and the `LADDER_VERSION` const + accessor exist LOCALLY (another agent, mid-flight,
NOT on main), but the six board-key call sites (`game_over_screen.gd:260,280`,
`leaderboard_screen.gd:89,106,153`, local `Leaderboard.new`) still use
`"v" + GameConfig.CURRENT_VERSION`, and `sync_version.py` does not stamp/check
the ladder file yet.

**What a server-side rotation requires:**

- New board for the new epoch: NOTHING (auto-created when the first v0.13
  client posts).
- **L1 alias of the live v0.12.0 board:** the PHP has NO alias/redirect concept;
  "alias" = ssh to the DreamCompute box and COPY the file:
  `cp board_weekly-2026-w0__v0.12.0.json board_<L1-seed>__L1.json`
  (the seed half of the L1 key must be decided -- keeping `weekly-2026-w0` is the
  honest choice). This is a snapshot, not a redirect: **v0.12.0 clients keep
  POSTing to the old `(weekly-2026-w0, v0.12.0)` key afterward**, so the L1 copy
  and the old board diverge unless Pip either re-copies at a "close of epoch"
  moment or rotates the POST token to fence off old builds (which silently
  strands their scores in the client outbox -- retried forever, never landing).
- DATA_DIR path and ssh access exist only on the box / in Pip's head -- not
  discoverable from this repo.

**pdoom1-website / score-API repo coordination (outside this repo):**

- `PipFoweraker/pdoom1-website` has a `sync-leaderboards.yml` workflow and
  leaderboard display -- it must be told the NEW featured board key
  `(<new-seed>, L2)` (and optionally the legacy L1 key for an archive view).
- `version_manifest.json` on api.pdoom1.com does NOT exist (probed: empty), and
  the in-game update notice (#799, the L2 rung of DISTRIBUTION_AND_PATCHING.md)
  is OPEN/unbuilt -- so v0.12.0 testers get NO in-game prompt; the v0.13
  download announcement is manual (Discord/email).
- API deployment docs live in pdoom1-website `docs/02-deployment/API_DEPLOYMENT_GUIDE.md`.

## 4. The BOTH-channel kickover -- deploy sequence for Friday

Pre-Friday, in THIS repo (agents/Pip, must MERGE TO MAIN first):

1. **Land the ladder split** (in flight now): call-site rewiring to
   `get_board_version()`, `sync_version.py` stamps/checks `LADDER_VERSION`,
   the fast test guarding the accessor. Without this, v0.13 keys boards
   `(seed, v0.13.0)` and the epoch concept never materializes.
2. **Implement the league-seed mechanism** (BLOCKER -- no code path exists):
   decide the new league's seed string and how the client gets it. Cheapest
   Friday-shaped fix: replace `get_weekly_seed()`'s broken ticks math with an
   explicit league seed constant/data value (ADR-0016 monthly cadence; a
   date-correct weekly generator contradicts the ruled MONTHLY cadence anyway).
3. Bump `ladder_version.txt` 1 -> 2 and `version.txt` -> 0.13.0 (from
   freshly-fetched main -- main is at 0.12.0, this branch's copy is stale);
   `python tools/sync_version.py`; commit; merge.

Friday, Pip local:

4. `python tools/build_release.py` -- verified-fresh exe+pck.
5. Manual zip (exe, pck, 2 Steam dlls, HOW-TO-RUN.txt).
6. Release-build smoke test from a clean extract: play -> lose -> confirm the
   score lands on `(<new-seed>, L2)` via curl GET.
7. `gh release create v0.13.0 PDoom-v0.13.0-windows.zip --title ... --notes ...`.

Friday, server (Pip, ssh to DreamCompute -- NOT doable from this repo):

8. Alias the live board to epoch L1: copy
   `board_weekly-2026-w0__v0.12.0.json` -> `board_weekly-2026-w0__L1.json`
   in DATA_DIR. No score_api.php change is required for the rotation itself.
9. (Optional, if #799 ships) create + serve `version_manifest.json` with
   `latest_build`/`ladder_version`/`download_url`.

Friday, pdoom1-website repo (Pip coordinates there):

10. Point the featured leaderboard / sync-leaderboards workflow at
    `(<new-seed>, L2)`; optionally surface the L1 board as "legacy epoch".

Announce (manual channel):

11. Tell testers to download v0.13 -- there is NO in-game update notice in
    v0.12.0 (#799 open). Old clients keep playing/posting to the old board;
    decide whether that is accepted drift or fenced via token rotation.

## Top unknowns / blockers for Friday

1. **No league-seed mechanism exists.** `get_weekly_seed()` is frozen at
   `weekly-2026-w0` (ticks-since-boot bug); nothing implements ADR-0016's
   monthly baseline seed. Pip must rule: the new seed string, where it lives
   (const vs data file), and whether the broken weekly generator is replaced or
   bypassed. Without this, the "new seed" half of the kickover has no carrier.
2. **Ladder split is unmerged and half-done.** `LADDER_VERSION`/accessor exist
   only in a local worktree; board-key call sites still use the build version;
   `sync_version.py` has no ladder support; nothing is on main. The L1->L2
   migration story depends on this landing (and on deciding the seed half of
   the L1 alias key).
3. **Server + website steps are outside this repo and undocumented here.**
   L1 "alias" = manual file copy over ssh (DATA_DIR path/access not in this
   repo); old v0.12.0 clients keep writing to the old key (divergence vs token
   fencing tradeoff, token rotation silently strands outboxed scores); the
   website's sync-leaderboards/featured-board config and any
   `version_manifest.json` live in `PipFoweraker/pdoom1-website`.

Secondary gaps: no packaging tool (zip is hand-rolled; archived v0.10.1 scripts
only), `.github/RELEASE_CHECKLIST.md` stale, this worktree's `version.txt`
(0.11.0) trails main (0.12.0), and #799 (update notice) is open so tester
migration is announcement-driven.
