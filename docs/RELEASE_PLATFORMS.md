# RELEASE PLATFORMS -- what we can build, and what we have proven

**Status:** written 2026-07-31, from facts re-verified on Pip's Windows machine
that day. Companion to `docs/rituals/gate_4_proven_build.md` (the cut) and
`docs/rituals/gate_6_board_opens.md` (the doors). This sheet owns the question
those two do not: *which platforms, from which machine, and who proved it runs.*

---

## The two failures that earned this sheet

Both happened on league night, 2026-07-31, roughly forty minutes before the
board was to open.

**Failure 1 -- `latest` was a lie nobody could see.** The build was cut and
blessed as v0.13.2. There was no `v0.13.2` git tag and no GitHub Release object.
`git tag --list "v0.13*"` returns exactly `v0.13.0` and `v0.13.1` (verified
2026-07-31). The website's Download button points at
`https://github.com/PipFoweraker/pdoom1/releases/latest/download/PDoom-Windows.zip`,
so `latest` still resolved to **v0.13.1** -- which ships ladder **L2** and
featured seed **weekly-2026-w30**, while the blessed league board was
**(weekly-2026-w31, L3)**. Both were corrected for that cut:
`ladder_version.txt` read `3` and `godot/autoload/game_config.gd` read
`const FEATURED_SEED_OVERRIDE: String = "weekly-2026-w31"`.

(Those two values are the LIVE state of the repo, not of this page: v0.14.0 cut
epoch **L4** on seed **weekly-2026-w32**. Read `ladder_version.txt` and the const
itself -- a dated sheet quoting them will always be a release behind.)

Had the league opened, every downloader would have posted to a different board
on **both** axes, the blessed board would have sat empty all night, and nothing
anywhere would have raised an error. This is the house failure mode exactly:
every component behaves correctly and the state is wrong.

**Failure 2 -- an assumption presented as a constraint.** The orchestrator then
told Pip that Mac and Linux builds were not possible that night, and offered a
false trilemma: Windows-only, carry the old macOS/Linux assets forward, or
Windows-only-with-a-note. That was never checked. Everything needed was already
on the machine and in the repo -- three configured presets, all export templates
installed, GodotSteam binaries committed for every platform, and a builder that
already takes `--preset`. Pip's ruling: *"this would be silly if we didn't have
good internal documents next time this happened to prevent this collision."*

The generalisable lesson: **"I could not verify X" and "X is impossible" are
different sentences**, and only the first one is ever honest without a command
having been run. This whole sheet is the check that turns the first into the
second, or into a build.

---

## 1. The platform matrix

Everything below was verified by reading files and listing directories on the
Windows dev machine on 2026-07-31. No build was run to produce this table.

| Platform | Preset name | Export path in preset | Architecture | Buildable from Windows | Playable on Windows |
|---|---|---|---|---|---|
| Windows | `Windows Desktop` | `../builds/windows/v0.13.2/PDoom.exe` | `x86_64` | yes | **yes** |
| Linux | `Linux/X11` | `../builds/linux/v0.13.2/PDoom.x86_64` | `x86_64` | yes | no |
| macOS | `macOS` | `../builds/mac/v0.13.2/PDoom.app.zip` | `universal` | yes | no |

Source: `godot/export_presets.cfg`, presets 0, 1 and 2. All three carry
`runnable=true`, the same `include_filter="build_stamp.txt"` and the same
`exclude_filter` (tests, gut, tools, docs, `*.md`, `*.py`, `*.bat`, `*.ps1`,
`*.sh`, `*.xml`). Windows and Linux set `binary_format/embed_pck=false`, so each
produces an executable **plus a sibling `.pck`**; macOS produces a single
`.app.zip` (preset 2 sets `export/distribution_type=1`).

### What each platform needs, and the state of it

**Export templates.** `%APPDATA%\Godot\export_templates\` contains exactly one
version directory, `4.5.1.stable`, matching the engine in `CLAUDE.md`. Listed
and confirmed present: `windows_release_x86_64.exe` (+ console variant),
`linux_release.x86_64` (plus arm32/arm64/x86_32 release and debug variants), and
`macos.zip`. Nothing needed to be downloaded on the night; the "we can't build
Mac" claim was false at the moment it was made.

**GodotSteam native libraries.** `godot/addons/godotsteam/godotsteam.gdextension`
declares libraries per platform, and every declared binary is committed in the
repo (directory listing, 2026-07-31):

| Declared entry | File on disk |
|---|---|
| `macos.release` | `osx/libgodotsteam.macos.template_release.framework/Versions/Current/libgodotsteam.macos.template_release` (5.6 MB) |
| `macos.debug` | `osx/libgodotsteam.macos.template_debug.framework/Versions/.../libgodotsteam.macos.template_debug` (6.1 MB) |
| `linux.release.x86_64` | `linux64/libgodotsteam.linux.template_release.x86_64.so` (4.4 MB) |
| `linux.release.x86_32` | `linux32/libgodotsteam.linux.template_release.x86_32.so` (4.8 MB) |
| `windows.release.x86_64` | `win64/libgodotsteam.windows.template_release.x86_64.dll` (3.7 MB) |
| `windows.release.x86_32` | `win32/libgodotsteam.windows.template_release.x86_32.dll` (4.6 MB) |

Dependencies (the Steam runtime libs) are likewise all present:
`osx/libsteam_api.dylib`, `linux64/libsteam_api.so`, `linux32/libsteam_api.so`,
`win64/steam_api64.dll`, `win32/steam_api.dll`.

Two things worth knowing rather than assuming:

- The macOS preset asks for a **universal** binary. The two macOS Mach-O files
  were byte-checked: both start `ca fe ba be 00 00 00 02`, i.e. a fat binary
  with two slices. That is consistent with x86_64 + arm64 universal, which is
  what the preset requires. The slice CPU types themselves were not decoded here
  -- `lipo -info` needs a Mac.
- There is **no arm64 Linux** GodotSteam library, only x86_32/x86_64. So a Linux
  arm64 export is not available to us even though the engine template is, and
  the `Linux/X11` preset correctly asks for `x86_64`.

---

## 2. Cutting all three platforms -- the exact commands

`tools/build_release.py` takes `--preset`. Verified usage (`--help`,
2026-07-31):

```
usage: build_release.py [-h] [--godot-path GODOT_PATH] [--preset PRESET]
                        [--mode {release,debug}] [--output OUTPUT]
                        [--project PROJECT] [--no-clean] [--keep-marker]
```

Defaults: `--preset "Windows Desktop"`, `--mode release`, output
`builds/<preset-slug>` where the slug is the preset name lowercased with spaces
replaced by underscores.

### These MUST run one at a time. Never concurrently.

Step 1 of the tool is `shutil.rmtree(godot/.godot)` -- an unconditional
`rm -rf` of the engine cache before every export (`tools/build_release.py`, the
block commented "the anti-stale-cache core"). Two builds running at once means
one of them deletes the cache the other is mid-way through populating. The
outcomes range from a hard failure to something far worse: an export that
reports success while packing a half-imported tree. The freshness marker check
would not necessarily catch that, because the marker only proves *the marker
file* made it into the pack, not that every other resource did.

The same rule applies to anything else touching the tree. `[Gate 4]` already
states it for agents; it applies to a second build with equal force.

```
# 0. Preconditions, once, before any of the three.
python tools/sync_version.py --check
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
git rev-parse HEAD                      # RECORD THIS. It is the cut's base SHA.

# 1. Windows. Sequential. Wait for [BUILD-VERIFY][PASS].
python tools/build_release.py --preset "Windows Desktop" --output builds/windows

# 2. Linux. Only after step 1 has fully exited.
python tools/build_release.py --preset "Linux/X11" --output builds/linux

# 3. macOS. Only after step 2 has fully exited.
python tools/build_release.py --preset "macOS" --output builds/mac
```

Separate `--output` directories per platform are still the recommended habit,
but they are no longer load-bearing. **Both hazards this section used to warn
about are FIXED (issue #1072).**

### What changed, and what it means for the three cut commands

- **The output filename now comes from the preset**, read out of that preset's
  own `export_path` in `godot/export_presets.cfg`
  (`output_name_for_preset()` in `tools/build_release.py`). Windows lands as
  `PDoom.exe`, Linux as `PDoom.x86_64`, macOS as `PDoom.app.zip` -- the same
  names a manual editor export produces, because it is the same source of truth.
  No rename step, and three presets sharing one output directory can no longer
  silently overwrite each other. Unit-covered in
  `tests/test_build_release_paths.py`, including a check against the real
  `export_presets.cfg` so the derivation cannot drift.
- **The freshness check now descends into zip containers** (`find_marker()`).
  The old raw-byte scan could not see the marker's filename inside a macOS
  `.app.zip`, because it lives in a *compressed* `.pck` entry rather than in the
  zip's plaintext central directory -- a false FAILURE waiting to happen. The
  check now searches zip entry names and then entry contents. It was NOT
  weakened: a zip genuinely lacking the marker still fails, and `--no-clean` is
  still the wrong answer to a `[BUILD-VERIFY]` failure.

Still true, still unproven, still a job for a human on the relevant machine:

- **Linux:** Godot resolves the pack from the executable's basename with its
  extension stripped, so `PDoom.x86_64` pairs with `PDoom.pck`. Set the
  executable bit -- a Windows filesystem carries no mode bits, so a zip built on
  Windows can ship a Linux binary that will not execute.
- **macOS:** no macOS build has ever been verified to RUN (issue #1071). That
  needs a person with a Mac, not code.

### CI parity (issue #1069)

The release workflow (`.github/workflows/enhanced-release.yml` ->
`scripts/build_all_platforms.py`) used to run a raw `godot --export-release`
per platform: no cache nuke, no freshness marker, no proof -- the release path
routed around the tool built after the v0.11.0 stale-cache disaster. Since
issue #1069, `build_all_platforms.py` delegates every export to
`tools/build_release.py` (sequentially, for the same never-concurrently reason
as above), so CI artifacts carry the same `[BUILD-VERIFY]` marker proof in the
workflow log that a local cut prints. Failure policy, ruled there: Windows or
Linux failing fails the job and publishes nothing; macOS is best-effort
(issue #1071) -- its failure drops the macOS assets and the
`verify-release-urls` alias check turns the run red AFTER Windows/Linux
publish. Loud, not blocking.

---

## 3. THE RELEASE CHECKLIST

This is the checklist that would have caught the near-miss. Run it in order.
Each line is written so that it is false-able -- if you cannot state the evidence
in the same breath, the line is not passed.

```
# the commands, in order
git rev-parse HEAD                                  # the SHA you BUILT from
git tag --list "v<X.Y.Z>"                           # does the tag exist at all?
git rev-list -n 1 v<X.Y.Z>                          # what does the tag point AT?
gh release view v<X.Y.Z> --json tagName,assets,url,targetCommitish
gh release list --limit 3                           # which one is flagged Latest?
python scripts/generate_release_metadata.py --version v<X.Y.Z> --verify
python scripts/verify_release_urls.py --file public/releases/v<X.Y.Z>.json
python scripts/verify_release_urls.py --sweep public/releases/releases.json
```

| # | Check | How it fails silently if skipped |
|---|---|---|
| 1 | **The tag exists.** `git tag --list` names it. | This is the exact 2026-07-31 miss. No tag, no error, `latest` quietly means the previous release. |
| 2 | **The tag points at the commit the artifact was BUILT from** -- compare `git rev-list -n 1 v<X.Y.Z>` against the SHA recorded at cut time, NOT against current `HEAD`. | Tagging HEAD after a few more merges tags a tree nobody built or played. Same class as `[Gate 5]`'s "the const changed after the cut": the version string agrees with itself and describes different bits. |
| 3 | **The Release object is published**, not draft, and `gh release list` shows it as `Latest`. | A bare git tag 200s its own tag page while `releases/latest/download/...` still serves the old release. `[Gate 6]` check 2 exists for precisely this: `--sweep` queries the Releases API rather than the tag page on purpose. |
| 4 | **Assets are named so `releases/latest/download/<name>` keeps resolving** -- see section 5. | The button is a fixed string. Ship only versioned names and the button 404s or serves nothing new. |
| 5 | **Every advertised URL answers 200**: `verify_release_urls.py --file` (blocking). | #963: the README once advertised a URL that had never existed and looked like a working link. |
| 6 | **CLICK THE ACTUAL DOWNLOAD BUTTON ON pdoom1.com**, in a browser, and confirm the version served. | See below. This is the irreducible one. |
| 7 | **Ladder and seed match the board you blessed.** Launch what the button gave you and read them off the running game. | The 2026-07-31 miss was visible only here: v0.13.1 ships (weekly-2026-w30, L2) and reports no error while doing so. |

### On check 6, which is the point of this sheet

**Check what the button serves. Not what the API says, and not what main says.**

Those three can disagree, and on 2026-07-31 all three did. `main` said 0.13.2
(`version.txt` reads `0.13.2`, and it is the version SSOT). The GitHub API said
v0.13.1 was Latest, which was *correct* -- and reading it as "fine, a release
exists" is how the miss survived. The button served a v0.13.1 zip that plays a
different ladder on a different seed. Each layer was internally consistent and
the chain was broken.

The button is also the only artefact on the list a player actually touches.
Everything above it is a proxy for it. Download the file the button gives you,
unzip it, run it, and read the version off the screen. If that takes four
minutes, it takes four minutes.

---

## 4. Limitations -- "we built it" and "a human proved it runs" are different claims

State which one you are making. They are not interchangeable and the ceremony
depends on the difference.

**A Windows machine can EXPORT macOS and Linux. It cannot PLAY them.** Godot
cross-exports fine; the artifact is not runnable on the machine that made it. So
for any release cut solely on Pip's Windows box:

| Platform | "We built it" | "A human proved it runs" |
|---|---|---|
| Windows | yes -- `build_release.py` exits 0 having proven its marker in the pack | yes, if `[Gate 4]` check 5 was performed (the human playtest of the built artifact) |
| Linux | yes | **no.** Nobody has launched it. Say so. |
| macOS | yes | **no.** Nobody has launched it, and see Gatekeeper below. |

The build tool says this about itself, and it is worth repeating rather than
paraphrasing -- from its own docstring: *"A clean, verified pack proves the RIGHT
BITS shipped. It does NOT prove the game runs on a real GPU."* The marker check
is a supply-chain proof, not a render proof. On the platforms we cannot launch,
there is no render proof at all.

`[Gate 6]` already carries the honest form of this under "Not verifiable from
here": *"Player-side download and launch on machines that are not the
Commissioner's."* This sheet just names the platforms.

### Windows: unsigned, so SmartScreen warns about an untrusted publisher

Read from `godot/export_presets.cfg` preset 0: `codesign/enable=false`,
`codesign/description=""`. Nothing signs the Windows executable, and no
code-signing certificate has been bought.

The consequence, reported by Pip on 2026-08-05 after a friend downloaded the
build: **"The game came up with an untrusted publisher warning."** Windows
Defender SmartScreen shows a blue "Windows protected your PC" panel naming an
unrecognised app / unknown publisher, and the Run button is hidden behind a
**More info** link. A player who does not know the link is there simply cannot
start the game -- the dialog offers only "Don't run".

The click path, which every player-facing surface must state in these words:
**"More info" -> "Run anyway"**.

Two things make this worse than macOS Gatekeeper rather than better. First, the
button is HIDDEN, not merely scary. Second, SmartScreen is partly reputation-
based, so it can warn on some machines and not others for the same file, which
makes second-hand troubleshooting ("it works for me") useless.

Because Windows cannot vouch for the publisher, the honest substitute is
provenance: the GitHub release page is the only trusted download, and
`release_manifest.json` (PR #1110) carries a per-asset **sha256** so a player
can verify their copy with `Get-FileHash -Algorithm SHA256 .\PDoom-Windows.zip`.
Say that alongside the warning -- the warning is the moment a cautious player
wants a way to check, and this is the only one we can give them.

Where the text lives (keep these three in step; the wording is deliberately
close to identical):

| Surface | File | Seen when |
|---|---|---|
| Zip contents | `tools/release_notes/HOW-TO-RUN-windows.txt` -> ships as `HOW-TO-RUN.txt` (`_zip_native_build` in `scripts/build_all_platforms.py`, which FAILS the package if the template is missing) | after extracting, if they look |
| GitHub release body | `tools/release_notes/RELEASE-BODY-security-notice.md`, appended by `.github/workflows/enhanced-release.yml` | before downloading |
| Website download page | pdoom1.com (separate repo -- must be copied there by hand) | before downloading |

Note the ordering problem: the zip note is the LAST of the three a player
reaches, because SmartScreen fires at the moment they run the exe, which is
after extraction but likely before they open a text file. The release body and
the website are the surfaces that actually prevent the alarm; the zip note is
the one that rescues someone already staring at the dialog.

The real fix is a code-signing certificate (an OV certificate is roughly
100-400 USD/year and still accrues SmartScreen reputation slowly; an EV
certificate is more expensive and gets reputation immediately). Not a tonight
problem, and deliberately not attempted here.

### macOS: unsigned and un-notarized, so Gatekeeper will block it

Read from `godot/export_presets.cfg` preset 2: `codesign/apple_team_id=""`,
`codesign/identity=""`, `notarization/notarization=0`. There is no signing
identity and notarization is off -- and notarization cannot be done from Windows
regardless, since it requires Apple's toolchain and an Apple Developer account.
Bundle identifier is `net.pdoom.game`, minimum macOS 10.13.

So every macOS download is quarantined by the OS and refused on first launch.
The user-visible symptom is a dialog saying the app is damaged or cannot be
opened because the developer cannot be verified. **It is not damaged.** Ship a
platform note that says so, in these words or close to them, because a user who
believes the download is corrupt will re-download rather than work around it.

Workarounds, in the order they should be offered:

1. **System Settings -> Privacy & Security**, scroll to the blocked-app message,
   click **Open Anyway**. This is the current path and the one to lead with.
2. **Right-click (or Control-click) the app -> Open**, then confirm. This is the
   instruction every guide on the internet still gives. Note carefully:
   `[Gate 6]` records that **Sequoia removed this path**, so it works on older
   macOS and fails on new machines. Offering it first is how you generate a
   confused message.
3. **Terminal:** `xattr -dr com.apple.quarantine /path/to/PDoom.app` -- strips
   the quarantine attribute recursively, after which the app opens normally.
   Reliable across versions, and correspondingly the one that scares
   non-technical players. Offer it last, with the path spelled out.

The real fix is a signed and notarized build, which needs a Mac (or a macOS CI
runner) plus an Apple Developer account. Until then, every macOS release ships
with a friction step and that should be stated in the release body rather than
discovered.

### Linux: no launch proof, and one remaining mechanical trap

The wrong-filename trap is closed (issue #1072 -- the binary now lands as
`PDoom.x86_64`, from the preset). What remains is the **missing executable
bit**: a Windows filesystem carries no mode bits, so a zip packaged on Windows
can ship a Linux binary that will not execute. That is the kind of thing that is
obvious to whoever launches it and invisible to whoever built it on Windows.
No Linux build has ever been verified to run.

---

## 5. Asset naming -- what the website actually depends on

Verified with `gh release view v0.13.1 --json assets` on 2026-07-31. What that
release actually shipped:

| Asset | Size | Notes |
|---|---|---|
| `PDoom-Windows-v0.13.1.zip` | 95,084,454 | versioned Windows build |
| `PDoom-Windows.zip` | 95,084,454 | **unversioned**, identical sha256 (`3a83ff90...`), uploaded ~1h15m AFTER the release was published |
| `PDoom-Linux-v0.13.1.zip` | 87,837,672 | versioned only -- there is **no** unversioned Linux asset |
| `PDoom-macOS-v0.13.1.zip` | 124,733,808 | versioned macOS build |
| `PDoom.app.zip` | 124,733,808 | unversioned macOS, identical sha256 (`1265fd31...`) |
| `release_manifest.json`, `releases.json`, `releases.rss`, `v0.13.1.json`, `v0.9.0.json` | small | feed metadata, published as release assets |

Two facts follow, and the first one is the load-bearing one.

**`PDoom-Windows.zip` is a stable-name alias, and the Download button depends on
it.** The button's URL is
`https://github.com/PipFoweraker/pdoom1/releases/latest/download/PDoom-Windows.zip`.
That URL resolves only if the release GitHub currently flags as Latest carries an
asset with **exactly** that name. Note the timestamps: on v0.13.1 the alias was
uploaded 75 minutes after the release went out, i.e. it was an afterthought, and
an afterthought is the kind of step that gets skipped. **Every release must
upload the unversioned alias, and the checklist's step 6 is what proves it.**

The website's own repository is not in this checkout, so the exact button markup
was not read here -- the URL above is as reported on 2026-07-31, corroborated by
the existence of a duplicate-content `PDoom-Windows.zip` asset that has no other
reason to exist. Confirm it against the website repo when convenient, and fix
this line if it is wrong.

**The generated feeds use versioned URLs.** `public/releases/v0.13.1.json` and
`public/releases/releases.json` both point at
`.../download/v0.13.1/PDoom-<Platform>-v0.13.1.zip`. So the site has two
independent download paths -- the fixed-string button on the `latest` alias, and
the feed on versioned URLs -- and they can rot independently. `verify_release_urls.py`
covers the feed side only; **only clicking the button covers the button.**

Recommended asset set per release, so both paths stay alive:

```
PDoom-Windows-v<X.Y.Z>.zip      PDoom-Windows.zip       (alias -- the button)
PDoom-Linux-v<X.Y.Z>.zip        PDoom-Linux.zip         (alias -- ADDED, issue #1068)
PDoom-macOS-v<X.Y.Z>.zip        PDoom.app.zip           (alias, existing name -- keep it)
```

**`PDoom-Linux.zip` is now produced automatically** by
`scripts/build_all_platforms.py` (same `shutil.copy2` alias step Windows already
had), and the release workflow's `verify-release-urls` job asserts all three
alias assets exist on the tag before the run goes green. The website's Linux
button pointed at `PDoom.x86_64`, which was never an asset -- the game repo
publishes `PDoom-Linux.zip`, and the website repo repoints the button at that.
A bare `PDoom.x86_64` would be the wrong thing to publish anyway: without the
sibling `PDoom.pck` and the GodotSteam `.so` libraries it cannot run, which is
exactly why the other two platforms ship zips.

Note the shape of how #1068 hid: `verify_release_urls.py` only checks URLs the
generated FEED lists, and the feed lists versioned zips only. So the "Verify
Release Download URLs" job passed green on every release while the site's Linux
button 404'd. The proxy ("the checked downloads work") had detached from the
thing ("all the downloads people actually click work"). The new alias step is
the missing half.

Do not rename an existing alias to something tidier. The alias names are a
contract with a fixed string in someone else's repository, and `[Gate 6]` check 3
already records the general form of that hazard: **anywhere a string is
republished by someone else is a place a fix does not reach.**

Never regenerate the feeds by hand: `python scripts/generate_release_metadata.py
--version v<X.Y.Z> --verify` writes them and HEADs every URL, and `--check` gates
pre-commit and CI by comparing the tracked index against the git tags. That
generated-not-hand-maintained pattern is the actual lesson of #1008, where a
one-line string sort called v0.9.0 "latest" from November onward because
`"v0.9.0" > "v0.13.1"` when `9 > 1`.

---

## What this sheet does not cover

- **Any claim about a macOS or Linux build actually running.** No such proof
  exists as of 2026-07-31. Owner: whoever gets access to those machines. Until
  then the release body should say "untested on this platform" rather than
  nothing.
- **The website repository.** The Download button URL, the news stub and the
  board rendering all live elsewhere. This sheet records what this repository
  publishes and what the button is reported to consume.
- **Steam distribution.** GodotSteam is present and its libraries ship, but
  nothing here covers depots, app IDs or the Steam upload path.
- **Signing on Windows.** Preset 0 has `codesign/enable=false`, so Windows
  builds are unsigned too and SmartScreen will warn on a fresh reputation.
  Different mechanism from Gatekeeper, and not blocking in the same way, but it
  is the same class of first-run friction.

---

## Addendum 2026-08-24 -- the first release that shipped no macOS asset

v0.14.3 published `PDoom-Windows-v0.14.3.zip` and `PDoom-Linux-v0.14.3.zip` and
**no macOS asset at all**. Every release from v0.13.1 through v0.14.2 carried
`PDoom-macOS-v<version>.zip`; this was the first that did not.

### The cause, from the log

Run `32690368004`, job **Build Godot Game (All Platforms)**, step *Build all
platforms*:

```
[   0% ] export | Started Exporting for macOS (3 steps)
[   0% ] export | Creating app bundle
ERROR: Project export for preset "macOS" failed.
   at: _fs_changed (editor/editor_node.cpp:1275)
```

That is the entire diagnostic Godot emitted. 1.4 seconds after the bundle step
began, before a single `Storing File:` line -- so the export died while
assembling the bundle from the template, not while packing the game.

The only change to the macOS preset between the two tags, other than the routine
version strings and a new copyright line, was **one line added by #1282**:

```
-application/icon=""
+application/icon="res://assets/images/pdoom1.ico"
```

Godot has no `.ico` decoder. Measured on the same Godot 4.5.1 build CI runs, on
this machine:

```
[probe] Image.load err=15 (OK=0) empty=true      # res://assets/images/pdoom1.ico
[probe] control png err=0 size=(256, 256)        # res://assets/images/logo.png
```

Error 15 is `ERR_FILE_UNRECOGNIZED`. Godot's own property hints say the same
thing (`get_export_options`, Godot 4.5-stable): macOS accepts
`*.icns,*.png,*.webp,*.svg`, Windows accepts `*.ico,*.png,*.webp,*.svg`. The
Windows exporter consumes `.ico` natively, which is why the Windows build was
fine and only macOS died.

**Why the message was empty.** In `platform/macos/export/export_plugin.cpp` the
icon load writes into the same `err` the export-template unzip loop tests:

```
Ref<Image> icon = _load_icon_or_splash_image(icon_path, &err);
...
while (ret == UNZ_OK && err == OK)
```

A failed icon load therefore ends the loop with no message of its own, and the
export returns that error. The binary entry (`Contents/MacOS/...`) sorts before
`Contents/Resources/icon.icns`, so `found_binary` was already true and even the
missing-binary message never fired. Nothing anywhere named the icon.

### This is a regression, not #1071 finally firing

Different failure, opposite shape. #1071 is the GodotSteam `.framework` losing
its `Versions/Current` symlink on a non-mac checkout; on v0.14.2 it produced
`ERROR: LipO`, `ERROR: CodeSign: Invalid binary format` and
`WARNING: Project export for preset "macOS" completed with warnings` -- and then
**shipped a 119.5 MB zip anyway**. Those warnings are non-fatal and the asset
published. In v0.14.3 the export never reached the frameworks at all. #1071
remains exactly as open and as unverified as it was.

What is genuinely latent here is the measurement gap, and it is the reason a
one-line preset edit reached a tag:

```
$ grep -rl "export-release" .github/workflows/
.github/workflows/enhanced-release.yml
```

**One file.** No PR check, no nightly, nothing but the release workflow itself
ever runs a macOS export. The first measurement of a preset change is the
release. `tools/check_export_icons.py` (pre-commit hook `export-icon-check`,
~10ms, no Godot launch) closes the specific hole: it fails on the v0.14.3 tree
and passes on the v0.14.2 tree and on the fix.

### Whether v0.14.3 can be given its macOS asset without re-tagging

`enhanced-release.yml`'s `workflow_dispatch` takes a `version` input and every
job resolves `${{ github.event.inputs.version || github.ref_name }}`, so a
dispatch naming `v0.14.3` would build, name and upload as v0.14.3.
`softprops/action-gh-release@v1` with an existing `tag_name` updates the
existing release rather than creating a tag, so the ruleset restricting `v*`
tag creation to admins is not in the path.

It still does not help, for a reason that has nothing to do with permissions:
**no `actions/checkout` step in that workflow sets `ref:`**, so a dispatch
builds whatever ref it was dispatched from.

- Dispatch from the tag `v0.14.3` -- builds the tag's tree, which contains the
  broken icon line, so the macOS export fails again, identically.
- Dispatch from a fixed branch -- builds a tree that is not v0.14.3, and
  publishes the result under the v0.14.3 name. That is exactly the class of
  claim the freshness proof in `tools/build_release.py` exists to prevent.

So: not retriable in place. The honest routes are (a) cut the next version with
the fix in it, or (b) leave v0.14.3 without a macOS asset and say so in the
release body. Note that `verify-release-urls` is currently red on v0.14.3 for
this reason, which is the loud signal working as designed.
