# Distribution and Patching

Architecture for shipping P(Doom)1 (Godot 4.5.1, pure GDScript, Windows
builds) and patching it after the fact. Workshopped 2026-07-22 during the
v0.12.0 friends-and-family launch.

## The problem

v0.12.0 ships as one ~92MB zip:

- `PDoom.exe` (~94MB)
- `PDoom.pck` (~60MB)
- 2 Steam dlls
- `HOW-TO-RUN.txt`

Two pains observed in the wild:

1. A non-technical tester ran `PDoom.exe` from INSIDE the Windows zip viewer
   without extracting first, so the `.pck` was not next to the exe --
   `"Couldn't load project data... Is the .pck file missing?"`. The
   run-from-inside-zip trap.
2. Every future update currently means a full re-download of the whole ~92MB
   blob, even for a one-line balance tweak.

## The generator: three things change at different rates

A shipped Godot build bundles three components with very different change
frequencies. Bundling them together is exactly what makes patching awkward --
a change to the smallest, most frequently-changing part forces re-shipping the
largest, rarest part.

- **Engine exe + native dlls (~94MB)** -- changes only on Godot version bumps,
  export-template changes, or native-library swaps. RARE.
- **Game pck (~60MB)** -- ALL gdscript + data + art. Changes every single
  patch. OFTEN.
- **Ladder ruleset (logical, not a file)** -- the scoring rules that fork the
  leaderboard board key. ORTHOGONAL to the two files above; a patch can change
  the pck without changing the ladder, or (rarely) change scoring rules that
  matter to the ladder.

Key consequence: **patch the PCK, not the whole blob.** Roughly 95% of patches
(UI, balance, art, icons, text) are pck-only; the exe does not move. Shipping a
new exe for a balance number is pure waste.

## Godot superpower: additive patch pcks

`ProjectSettings.load_resource_pack("patch.pck")` mounts a SECOND pck whose
files OVERRIDE the files in the base pck. A patch that touches 3 files becomes a
few-KB pck containing only those 3 files.

Boot flow with patching:

1. On boot, read a manifest.
2. Download any missing patch pcks named in the manifest.
3. Mount them in order (later mounts override earlier ones).

CAVEAT (security): mounting a downloaded pck runs its gdscript. That is a
remote-code-execution path by construction. Require a verified content hash and
a trusted backend before mounting anything downloaded. Never mount an
unverified pck.

## The options ladder (cheapest first)

- **L0: raw zip + manual extract (TODAY).** Trips non-technical users -- the
  run-from-inside-zip trap above.
- **L1: Inno Setup installer.** Nothing to extract; a Start Menu shortcut and a
  known, fixed install directory that every future updater needs to exist
  anyway.
- **L2: in-game update NOTICE.** On launch, GET a version manifest from
  `api.pdoom1.com`; if a newer build exists, show a non-blocking
  `"vX available -> Download"` banner that opens the release URL. This is the
  core of issue #799.
- **L3: in-game auto pck-swap patcher.** Download + hash-verify + mount/swap +
  relaunch, all in-game. Rare exe/engine updates fall back to re-running the
  installer, surfaced via the same L2 banner.

Pseudocode for the L2 manifest check:

```
# version_manifest.json served from api.pdoom1.com:
# {
#   "latest_build":   "0.13.0+build.412",
#   "ladder_version": "3",
#   "min_supported":  "0.12.0",
#   "download_url":   "https://pdoom1.com/releases/0.13.0",
#   "pck_patch_url":  "https://cdn.pdoom1.com/patches/0.13.0.pck",
#   "pck_sha256":     "ab12...ef"
# }

func check_for_update() -> void:
    var manifest = http_get_json("https://api.pdoom1.com/version_manifest.json")
    if manifest == null:
        return  # offline / backend down -- stay silent, never block play
    if version_gt(manifest.latest_build, CURRENT_BUILD):
        show_update_banner(manifest.latest_build, manifest.download_url)
        # L3 later: if manifest.pck_patch_url and hash trusted -> offer in-game swap
```

Design note: the check must be non-blocking and fail silent. A tester offline or
a backend hiccup must never stop the game from starting.

## Recommendation

Do **L1 + L2 EARLY (this week).** Both are cheap, and both are hard to retrofit:
the cost of adding an updater grows with the install base and with how much
testers have been trained on the manual zip flow. Every tester who learns
"extract, then double-click the exe" is a habit to later un-teach. Design the
code toward L3 from the start (manifest schema, build-vs-ladder split below) even
if L3 does not ship this week.

## Dependency: the build-vs-ladder version split

L3 forces a version split that is already on the backlog. Today the leaderboard
board key is `(seed, full game_version)`, so EVERY patch forks the leaderboard --
a UI-only pck that changes nothing about scoring still splits the board and
scatters testers across incompatible ladders.

Required split:

- **Build version** bumps every patch (it identifies the binary/pck content).
- A **SEPARATE ladder version** bumps ONLY on gameplay/scoring changes.

The patch manifest must declare, per patch, whether it forks the ladder:

- A UI/art/text pck MUST NOT fork the ladder.
- A balance/scoring pck MUST fork the ladder.

This split must land BEFORE the first gameplay hotpatch, otherwise the first
pck-only balance fix either wrongly preserves an outdated ladder or wrongly
forks a cosmetic one.

## Signing / SmartScreen

Unsigned builds show `"Windows protected your PC"` (SmartScreen). Testers get
past it with `More info -> Run anyway`. A signed installer softens this warning.
A code-signing certificate (~$100-400/yr) is a LATER money lever, not an alpha
concern -- friends-and-family testers can be walked through the click-through.

## RULINGS (2026-07-23, Pip)

- **DECISION 1 -- Installer: INNO SETUP.** Move the direct-download build to an Inno Setup
  installer (L1). Nothing to extract (kills the run-from-inside-zip trap); Start Menu shortcut
  + fixed install dir.
- **DECISION 2 -- Updater reach: SEPARATE LAUNCHER.** A small launcher exe that can update
  everything (incl. engine) before starting the game. Rationale beyond updates: a persistent
  owned surface for community news / showcases / tournaments. (See the Steam caveat -- keep the
  community features channel-agnostic / in-game.)
- **DECISION 3 -- Trust model: HASH NOW, SIGN WITH L3.** Alpha ships hash-in-manifest over
  HTTPS (rung 2). Cryptographic signature verification (baked-in public key, rung 3) lands WITH
  L3 auto-patching -- auto-execution is when the RCE risk bites. Verification is 100% LOCAL
  (sends nothing about the player); only outbound is an ANONYMOUS version-check. Privacy stance
  from day one: anonymous checks, no accounts, any install-ping aggregate-not-identified;
  publish a one-line "what the updater sends" (tie to pdoom1.com/privacy).
- **TIMING -- L1 + L2 early; L3 next version increment.** L3 is itself a delivery change, so
  defer it to when we increment anyway.
- **CODE-SIGNING CERT -- buy at wide-release / L3.** Pip will pay then. Dual-use: removes the
  SmartScreen warning AND is the signing key for rung-3 pck verification. Reassess scope once
  Steam is in play (below).

## Steam as an eventual second channel

Pip's plan: eventually distribute via Steam (far larger market / discovery). Groundwork is
already partly done -- the GodotSteam native dlls (`libgodotsteam...dll`, `steam_api64.dll`)
already ship in the build, and `achievements.gd` exists. Steam is a "when more polished" move
($100 Steamworks fee/app, store review, wants a wishlist + store-page campaign first), NOT now
-- but it RE-PRIORITIZES the ladder above:

- Steam is a SECOND channel, not a replacement -- direct download (itch/GitHub) stays for alpha,
  non-Steam, DRM-free users. So L1/L2 are NOT wasted; they serve the persistent direct channel.
- Steam provides NATIVELY: installer, delta auto-updates (Steampipe depots), a trusted-source
  signal (no SmartScreen for Steam-launched games), and a community surface (hub, news, rich
  presence). This partly OBVIATES three things above:
  - **L3 (custom pck-patcher): probably do NOT build it.** Steam depots delta-patch natively and
    better on the Steam channel; the direct channel can survive on L2 (notice -> download new
    build). Steam potentially removes the single most complex work item.
  - **Launcher (Decision 2): right-size it.** Steam DISCOURAGES third-party launchers and its hub
    duplicates the news/showcase vision. Build the launcher for DIRECT-channel delivery, but put
    community features IN-GAME (channel-agnostic) so they are not stranded or fighting Steam UX.
  - **Cert: mainly for the direct channel.** Steam-delivered builds bypass SmartScreen, so if
    Steam becomes primary the cert's value shrinks to direct downloaders (still needed for rung-3
    signing). Reassess at wide-release.
- Steam auto-updates REINFORCE the build-vs-ladder split: Steam patches players automatically, so
  a gameplay patch could move Steam users to a new epoch silently -- the split makes that safe.
- Steam also offers leaderboards/achievements/cloud-saves/workshop. The custom leaderboard
  (api.pdoom1.com) is still needed for cross-platform / non-Steam players; plan to run both or
  bridge them rather than migrate.

---

Rulings recorded 2026-07-23. Steam re-prioritization: keep L1/L2, likely SKIP L3 (Steam
patches), right-size the launcher, community features in-game, cert at wide-release.
