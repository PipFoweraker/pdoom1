# P(Doom)1 Self-Updater -- Design

- **Status:** DESIGN + first increment BUILT (branch `feat/self-updater`)
- **Drafted:** 2026-08-04 (Fable session, parallel workstream)
- **Ruling that opened this lane (Pip, 2026-08-04):** "I think I want a good
  updater first and independently, that feels more correct to me and lets
  e.g. LLMs and so on play it without needing to do Steam based things."
  Steam becomes an ADDITIONAL distribution channel later, not the patching
  mechanism. This partially supersedes the 2026-07-23 Steam note in
  `docs/game-design/DISTRIBUTION_AND_PATCHING.md:196-199` ("likely SKIP L3");
  L3's build-or-not is re-opened as an open decision below.
- **Second driver:** the project's own diagnosis (#1027, #1075) is checks
  that report green about nothing. The updater must be inspectable end to
  end and must fail loudly. Handing patching to a content system nobody here
  can instrument would repeat the failure mode.
- **Prior art this design honours:**
  `docs/game-design/DISTRIBUTION_AND_PATCHING.md` (the L0-L3 ladder, the
  pck-swap model, the exe/pck/ladder 3-rate split, the run-from-inside-zip
  trap, the 2026-07-23 rulings),
  `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md` (build vs board epoch),
  `docs/RELEASE_PLATFORMS.md` (asset naming, the 2026-07-31 "latest was a
  lie" near-miss), `docs/PRIVACY_POSTURE.md` (two-tier consent, ruled
  2026-07-26).

---

## 1. What exists today, precisely

### 1.1 The in-game check (L2) -- `godot/autoload/update_check.gd`

Pre-increment behaviour (issues #799/#942, "one request, two jobs"):

- Once per session at boot, fire-and-forget, 3s hard timeout, never blocks
  startup, silent no-op on every failure (one `push_warning` max/session).
- Job 1: GET the website's static feed `https://pdoom1.com/data/version.json`,
  parse `latest_release.version`, compare NUMERICALLY (never strings -- the
  `"0.9.0" > "0.11.0"` trap) to `GameConfig.CURRENT_VERSION`. If newer and
  not previously dismissed, emit `update_available`; the welcome screen
  (`godot/scripts/ui/welcome_screen.gd:276-315`) shows a dismissible
  `vX available >> [U]pdate page` button opening
  `github.com/PipFoweraker/pdoom1/releases/latest`. **It can NOTIFY only** --
  no download, no install, no knowledge of what changed or whether the update
  forks the player's board.
- Job 2: anonymous install ping (Plausible, random UUIDv4 in `user://`,
  nothing machine-derived), gated by its own default-ON settings toggle per
  the 2026-07-26 two-tier privacy ruling. Unchanged by this workstream.

Post-increment behaviour is section 3.

### 1.2 The distribution ladder and its rulings

`DISTRIBUTION_AND_PATCHING.md:62-84`: **L0** raw zip (the run-from-inside-zip
trap), **L1** Inno Setup installer (ruled yes 2026-07-23, not yet shipped),
**L2** in-game update notice (SHIPPED as update_check.gd), **L3** in-game
auto pck-swap patcher (unbuilt). Ruled 2026-07-23: hash-in-manifest over
HTTPS now, cryptographic signatures land WITH L3 ("auto-execution is when the
RCE risk bites"); a separate launcher exe for the direct channel; code-signing
cert at wide release.

The 3-rate split (`DISTRIBUTION_AND_PATCHING.md:25-43`): engine exe ~94MB
changes RARELY; game pck (~59MB today, ~165MB projected, #1109) changes every
patch; the ladder ruleset changes ORTHOGONALLY. ~95% of patches are pck-only.
Godot mounts additive patch pcks via
`ProjectSettings.load_resource_pack()` -- a few-KB pck can override 3 files.

### 1.3 The board-epoch split (LANDED)

`BUILD_VS_LADDER_VERSION_SPLIT.md` shipped: `ladder_version.txt` (root, reads
`3`) is the epoch SSOT, stamped into
`godot/autoload/game_config.gd:202` (`const LADDER_VERSION: String = "3"`);
`get_board_version()` (`game_config.gd:622`) returns `"L3"` and is the ONLY
board-key version source. **The board key is `(seed, ladder_epoch)`. An
update that changes the epoch forks every board.** The 2026-07-31 league
near-miss (`RELEASE_PLATFORMS.md`, "Failure 1") was exactly a player-visible
epoch/seed mismatch that no component reported.

### 1.4 Release production

- `tools/build_release.py` -- local cuts: nukes `godot/.godot`, stamps the
  build, exports, and PROVES a unique freshness marker landed inside the
  `.pck`/zip before emitting (`[BUILD-VERIFY]`).
- `.github/workflows/enhanced-release.yml` -- CI releases on `v*.*.*` tags:
  builds all three platforms via `scripts/build_all_platforms.py` (**NOT**
  `build_release.py` -- issue #1069: CI artifacts bypass the freshness
  proof), generates feeds, creates `release_manifest.json`, publishes the
  GitHub Release, then verifies every advertised URL and the three
  unversioned alias assets (`PDoom-Windows.zip`, `PDoom-Linux.zip`,
  `PDoom.app.zip` -- #1068) answer 200.
- `release_manifest.json` is published as an asset on every tag, so
  `releases/latest/download/release_manifest.json` is a stable URL that
  always describes EXACTLY the release the download button serves. Before
  this increment it carried version/commit/engine/platforms/provenance; it
  now also carries `ladder_version`, `highlights`, `download_page`, and
  per-asset `sha256` (section 4).

---

## 2. The update ladder -- rungs, and what decides the rung

Four client-side rungs, mapped onto the existing L-scheme. The DECIDER is
three comparisons the manifest already supports:

1. **build delta** -- `manifest.version` vs `GameConfig.CURRENT_VERSION`
   (numeric semver triple).
2. **epoch delta** -- `manifest.ladder_version` vs `GameConfig.LADDER_VERSION`
   (opaque integers; equal or not, no ordering semantics).
3. **engine delta** -- `manifest.engine.version` vs the running engine
   (`Engine.get_version_info()`). Engine change means the exe must move:
   pck-swap is impossible.

| Rung | Name | When | Player experience |
|---|---|---|---|
| R0 | up to date | no build delta | nothing. Silence is correct here. |
| R1 | **notify** (= L2, SHIPPED) | build delta, any kind | dismissible one-line notice; epoch-forking updates say "(new board epoch)" in the same line; tooltip shows changelog highlights; button opens the release tag page. |
| R2 | **fetch pck** (= L3 narrow, UNBUILT) | build delta, NO engine delta | offer in-game download of the new `.pck` only (~59MB now, vs ~95MB zip; the gap widens as #1109 grows the pack). Hash-verified before swap, A/B rollback (section 5). Epoch-forking pck REQUIRES an explicit confirmation screen naming the fork; cosmetic pck is one click. |
| R3 | **fetch full / must-reinstall** (UNBUILT) | engine delta, or hash/verify machinery unavailable | notice escalates to "this update replaces the whole install"; link to installer/zip. Never auto. SmartScreen will warn on the unsigned exe -- noted, explicitly not solved here (cert at wide-release per 2026-07-23 ruling). |

Epoch rule, restated as a hard invariant: **the updater never moves a player
across ladder epochs without saying so before the player acts, and never
automatically.** A cosmetic update may eventually background-download; an
epoch-forking update may not even do that without the fork being on screen.
(Rationale: the board key is `(seed, ladder_epoch)`; a silent epoch move
mid-league is the 2026-07-31 failure, automated.)

A future `min_supported` manifest field (already sketched in
`DISTRIBUTION_AND_PATCHING.md:88-96`) upgrades R1's wording to "this build
can no longer submit to boards" -- but never blocks offline play.

## 3. The check protocol (post-increment)

- **What is fetched:** GET
  `https://github.com/PipFoweraker/pdoom1/releases/latest/download/release_manifest.json`
  (`update_check.gd:52`), once per session at boot, 3s timeout, redirects
  followed. On ANY failure (unreachable, non-200, malformed) -- exactly one
  fallback GET of the old website feed (`update_check.gd:388-398`), so the
  check is never worse than pre-manifest. Both paths fail silent to the
  player, loud in logs.
- **Why the manifest and not the website feed:** the manifest is published
  atomically WITH the assets by the same workflow run. The website feed is a
  cross-repo sync hop (`enhanced-release.yml` `sync-website-version`, which
  needed a loop-prevention workaround already) -- an extra place for state to
  rot. And only the manifest knows the epoch and the hashes.
- **What is sent:** a GET with `User-Agent: pdoom1/<version> (<OS>)` and
  nothing else. No identifiers, no widening of data collection. **One posture
  change to state honestly:** the check endpoint moves from pdoom1.com to
  github.com, so GitHub now sees a boot-time request (IP + UA) from players.
  GitHub already saw every download; this adds launch-time visibility to the
  same party. The anonymous install ping (Tier 2, own toggle, 2026-07-26
  ruling) is UNCHANGED and remains the only thing that persists an id.
- **Frequency:** boot only. No polling, no retries beyond the single
  fallback.

## 4. Integrity -- non-negotiable

A downloaded pck executes its GDScript when mounted; an updater that installs
an unverified blob is an RCE path into every player machine
(`DISTRIBUTION_AND_PATCHING.md:57-60` says this too).

- **Published anchors (BUILT):** `scripts/generate_release_manifest.py` runs
  in CI with the actual build artifacts and writes
  `assets: [{name, size, sha256}]` into the manifest. Unit-tested
  (`tests/test_generate_release_manifest.py`) including that hashes are real
  digests of the bytes. Every release from here on is verifiable; players
  can check a manual download today (`sha256sum` vs the manifest).
- **Verification rule (for R2, when built):** download to a temp file ->
  check size -> stream sha256 -> compare against the manifest fetched fresh
  over HTTPS in the same session -> ONLY then swap. Mismatch = delete the
  blob, keep the current install, tell the player. No hash in the manifest =
  no auto-anything (the client treats absent hashes as "R1 only").
- **Trust chain today** is rung 2 of the 2026-07-23 ruling: HTTPS to
  github.com plus control of the repo. Rung 3 (detached signature over the
  manifest, public key baked into the client) lands WITH R2 auto-apply,
  before any auto-execution ships.
- **Client-side gate already live:** manifest `download_page` reaches
  `OS.shell_open`, so it is prefix-locked to
  `https://github.com/PipFoweraker/pdoom1/` (`update_check.gd:56-62,219`);
  anything else is dropped and the generic releases page is used. A tampered
  manifest cannot launch arbitrary URLs or local files.
- **Honest limitation (#1069):** manifest hashes prove "what CI uploaded is
  what you received", NOT "CI packed the right bits" -- CI builds bypass
  `build_release.py`'s freshness proof. Fixing #1069 (make CI use the proven
  builder) is a prerequisite for R2, tracked separately.

## 5. Failure modes -- what the player sees

Invariant: **the updater must never leave the game unlaunchable.** The
current install is never modified until a verified replacement exists.

| Failure | Player sees | Mechanism |
|---|---|---|
| Offline / GitHub down | nothing; game identical to offline play | both check requests fail silent (`update_check.gd:360-366`, warn-once in logs) |
| Manifest 404/malformed | nothing, unless the website feed answers (then the plain notice) | single fallback, fail-closed parsing (`parse_release_manifest` returns `{}` -> fallback) |
| Both endpoints lie/garbled | nothing; worst case is a MISSING notice, never a wrong one | every parse fails closed; `is_remote_newer` returns false on malformed input |
| Partial download (R2) | "Download incomplete -- nothing was changed. Try again or download manually." | temp-file download; size+hash checked before any swap; blob deleted |
| Corrupt/tampered pck (R2) | "Update failed verification -- nothing was changed." + manual link | sha256 mismatch aborts before mount/swap, blob deleted |
| Disk full (R2) | "Not enough disk space for the update (needs ~N MB). Nothing was changed." | preflight free-space check against manifest `size`; download is to temp, never over the live pck |
| No write permission to install dir | "Can't update in place (folder is read-only) -- download manually." | preflight write-probe BEFORE downloading; relevant once L1 installs under Program Files |
| Hash-valid patch that bricks the game | next launch auto-restores the previous version; notice "Update rolled back after a failed start." | A/B swap: new pck lands as `PDoom.pck.new`, old kept as `PDoom.pck.prev`, atomic rename; a boot marker file is cleared only after the main menu loads; marker present at next boot = crash -> restore `.prev`. `.prev` is deleted only after one clean boot of the new build |
| Epoch change mid-league | the fork is named in the notice before any action; R2 additionally requires an explicit confirm screen | `is_epoch_change` + `build_notice_label` (`update_check.gd:241-256`); never automatic |

## 6. Explicitly OUT of scope for v1

- Auto-download and auto-apply (R2/R3 execution) -- design above, build later.
- Signature verification (rung 3) -- lands with R2, not before, per ruling.
- The separate launcher exe (2026-07-23 DECISION 2) -- right-size it when R2
  is real; the in-game notice does not depend on it.
- Code signing / SmartScreen -- noted at R3; cert at wide-release.
- Additive multi-pck deltas (patch.pck stacking) -- full pck swap first;
  few-KB deltas are a later optimization.
- Steam depots -- additional channel later; nothing here assumes it.
- Server-side `min_supported` enforcement on the score API.
- macOS/Linux updater mechanics (no launch proof exists for those builds at
  all -- `RELEASE_PLATFORMS.md` section 4).

## 7. What the first increment shipped (this branch)

1. **Manifest generation became code, not YAML** --
   `scripts/generate_release_manifest.py` replaces the heredoc in
   `enhanced-release.yml`; same fields (add-only contract, tested), plus
   `ladder_version` (from `ladder_version.txt`, loud failure if absent),
   `highlights` (ASCII CHANGELOG excerpt, capped), `download_page` (tag
   page), and per-asset `sha256` computed from the real CI artifacts.
   Fails the release non-zero on any malformed input.
2. **The client check reads the manifest** (`update_check.gd`): primary GET
   of `release_manifest.json`, website feed demoted to one-shot fallback;
   epoch comparison against `GameConfig.LADDER_VERSION` with fail-closed
   normalization; notice label announces board forks; tooltip carries
   highlights; update button opens the prefix-validated tag page.
3. **Tests:** 23 new GDScript tests (parser contract, the shell_open
   prefix gate, epoch fail-closed semantics, handler + fallback decision,
   dismissal state) and 14 new Python tests (field contract vs the GDScript
   parser, real-digest hashing, loud-failure paths). Both suites were
   sabotaged (wrong manifest field name; hashing the filename instead of the
   bytes) and went red -- 7 GDScript failures, 1 Python failure -- then
   restored to green. The guards can fail.

## 8. Needs Pip's ruling

1. **Check endpoint = GitHub.** Accept that GitHub sees a boot-time request
   from every online player (it already serves every download)? Alternative:
   mirror the manifest to pdoom1.com and check there (keeps GitHub
   download-only, adds back a sync hop that can rot). Recommendation: GitHub,
   it is the atomic truth; revisit if a non-GitHub mirror ever matters.
2. **R2 shape for the direct channel:** pck-swap (smaller: pck-only vs full
   zip, and the gap grows with #1109) vs full-zip auto-download (simpler, no
   A/B pck logic). The 2026-07-23 "likely SKIP L3" note leaned on Steam
   patching; the 2026-08-04 updater-first ruling reopens it.
   Recommendation: pck-swap, engine moves rarely.
3. **#1069 as an R2 prerequisite:** agree that CI must adopt the
   `build_release.py` freshness proof BEFORE any auto-apply ships, so the
   hashes anchor a proven artifact.
4. **Epoch-change wording** on the notice: currently
   `"vX available (new board epoch) >> [U]pdate page"`. Louder variant
   ("updating starts a new leaderboard") costs screen space; ruling is
   cosmetic and can wait.
