## [0.14.0] - 2026-08-07

Ladder epoch **L3 -> L4** -- this is a FORKING release. The historical event deck
was retimed to one-turn-one-month and the ruled promotions were applied (#1137),
which changes which events fire on a given seed, so scores are not comparable
with L3 boards. L3 entries stay valid and visible under L3; new runs land on L4.
Featured league seed rolls to `weekly-2026-w32`.

Every entry below is tied to a commit merged between `v0.13.2` and this release.

**Corrected 2026-08-09.** As first published, this section named 14 issues in
wording that read as "we delivered this", and all 14 were -- and still are --
open. The code behind each one is real and merged in this range; the issue it
belongs to is not finished. Every such citation now says so in the same
sentence, so you can tell what shipped from what only moved. Nothing about the
build changed, and no entry was deleted.

### Added
- **Pick the music from the pause menu** (#802, #1146) -- track selection while
  you play, not only in Settings. The wider music controller is not done:
  **#802 is still OPEN** for mute/skip and the doom-triggered rotation.
- **A credits screen you can actually reach** (#1161).
- **Month review shows what CHANGED**, and SPACE opens it (#1100).
- **Settings rebuilt as a front card plus an operations board** (#1096, #1103).
- **One-time "claim a name" prompt before your first upload**, plus a lab-name
  generator (#957, #1063, #1133) -- a public board of identical
  "Researcher -- AI Safety Lab" rows is one nobody can find themselves on. The
  prompt appears at upload, not on the first screen (**#1063 is still OPEN**),
  and your own row is not yet highlighted on the board (**#957 is still OPEN**).
- **Epoch-aware update check** reads `release_manifest.json`; the manifest now
  carries the ladder epoch and sha256 anchors (#1110).

### Changed
- **Historical event deck retimed to one turn = one month**, with a timing dial
  and the ruled promotions applied (#1137), against Pip's rulings of 2026-08-04.
  *This is the change that forks the ladder.* The ruling records stay open
  because deferred items remain in them (**#1111 is still OPEN**,
  **#1125 is still OPEN**); the retime itself shipped.
- **Difficulty lock enforced where the value is CONSUMED**, not on one screen,
  and Alpha Tools now set a sticky unranked flag (#1058, #1060, #1084, #1104).
- **One table for choice keys, one door per panel** -- keyboard and navigation
  unified (#565, #567, #575, #602, #1120).
- **The last player-facing "AP" is gone**, and one number format is ruled across
  the UI (#1073, #1087, #1116).
- **Copy stops teaching a different game** -- the guide, the win condition and
  the cold open now describe what the game actually does (#1136).
- **Turn-1 hand fits above the fold; Fundraising is tile 1** (#1130).
- **The debug event-trigger is deleted, not guarded** (#1134, #1143).
- **A third-party endpoint and its unreachable fetch path were removed** (#1101,
  #1105).
- **Contact addresses redacted from the bundled historical events** (#1106).
- **The pause menu grows into its text, not into padding** (#1155).

### Fixed
- **The achievement toast rendered as a giant purple rectangle** in v0.13.2
  (#1083).
- **The office cat was a magenta checkerboard in every shipped build** -- not one
  flaky JPG (#796, #1080).
- **The server rack painted over the feed and the staff were oversized**
  (#793, #1081). Every staff member still renders as the same character, so
  **#793 is still OPEN**.
- **The public build wore a stale, clipped "DEV BUILD" banner** (#1067, #1079).
  The banner is fixed; CI still does not run `write_build_stamp.py`, so
  **#1067 is still OPEN**.
- **A failed global leaderboard fetch is now VISIBLE**, and players are warned
  about SmartScreen (#1127). The toggle's own un-press behaviour is unverified
  in a shipped build, so **#1126 is still OPEN**.
- **Music was too loud and the wrong track; Graphics Settings was an empty
  header** (#1095).
- **Percent tie direction pinned**, so doom reads the same on every platform.
- **Release export filename derives from the preset**, and the Linux alias is
  published (#1099). Neither the site's Linux download button
  (**#1068 is still OPEN**) nor the hardcoded-output-name issue
  (**#1072 is still OPEN**) has been confirmed closed against a shipped build.
- **The backslash dev key returns in release builds** (dev gates split) (#1129).

### Dev / tooling (no player-visible change)
- CI exports now route through `build_release.py`'s freshness proof (#1069,
  #1114); the GDScript syntax gate COMPILES every `.gd` rather than only what
  boot reaches (#1082, #1119).
- New instruments: `find_dead_code.py` (#1124), an action-taxonomy checker
  (#1139), a generated `docs/TOOLS.md` (#1123), a generated
  `decisions/README.md` (#1108). These are instruments, not fixes: the dead-path
  sweep they serve is unfinished (**#1117 is still OPEN**) and the taxonomy
  checker reports the action grouping it was built to measure
  (**#798 is still OPEN**).
- Dead paths retired; what remains is LOUD (#1118). The pdoom-data re-sync
  capability was deleted rather than replaced, so **#1115 is still OPEN**.
- Art pipeline: promotion map unblocks 605 then all 327 remaining approved assets
  (#1107, #1122); 2,713 human verdicts made durable; the 2026-08-07 art
  night fired 652 images (#1158); art-review gallery keyboard repaired (#1162).
  The review backlog those assets came from is not cleared, so
  **#1093 is still OPEN**.
- Issue triage across all 201 open issues plus a 7-fix drive-by batch (#1144),
  and a pre-close mining pass (#1153).
- ADR-0019 (the pack is a function of declared demand), a phase-critical state
  audit (#1145), and a claims audit of the project's own output (#1160).

## Before you download: your OS will warn you, and that is expected

These builds are **unsigned**. Signing means buying a code-signing certificate
(Windows) or an Apple Developer identity plus notarization (macOS). P(Doom) is
an alpha made by one person and has not bought either yet, so every operating
system reports that it cannot verify who made the program. The warnings mean
"we cannot check the publisher", not "this is malware".

### Windows -- SmartScreen

You will see a blue **"Windows protected your PC"** box, often naming an
**unknown / untrusted publisher**. To run the game:

1. Click **More info** (the small link under the message).
2. Click **Run anyway**.

Also: extract the whole zip to a folder before running `PDoom.exe`. Running it
from inside the zip viewer hides `PDoom.pck` from it, and the game will not
start. That is the single most common problem people hit.

### macOS -- Gatekeeper

First launch is blocked. On macOS 15 (Sequoia) and later, double-click the app
once, dismiss the warning, then go to **System Settings -> Privacy & Security**
and click **Open Anyway**. On macOS 14 and earlier you can right-click (or
Control-click) the app and choose **Open**. Full steps are in `HOW-TO-RUN.txt`
inside the zip.

### Linux

You may need to set the executable bit: `chmod +x PDoom.x86_64`.

### Checking you have the real file

Because the OS cannot vouch for the publisher, verify the source instead:

- **This release page is the only trusted download.** Do not run a P(Doom)
  binary that reached you any other way.
- `release_manifest.json`, attached to this release, lists the exact size and
  **sha256** of every zip. Compare it against your download:
  - Windows (PowerShell): `Get-FileHash -Algorithm SHA256 .\PDoom-Windows.zip`
  - macOS / Linux: `shasum -a 256 PDoom-Linux.zip`

A matching hash means the file is byte-for-byte what was published here.

## Build Information

- **Commit:** `7368e2373393badc16f9189209c199732cb4fcec`
- **Data Hash:** `4b2b31dab682e25ea2338e52fd6e47a55048208a10e3346a751a3a4e869442dc`
- **Manifest Hash:** `47ef38eb1d5c02d53e17bc95d2d79e5bd605ba197fa21e8f0ae6c867f0f0db93`
- **Engine:** Godot 4.5.1
