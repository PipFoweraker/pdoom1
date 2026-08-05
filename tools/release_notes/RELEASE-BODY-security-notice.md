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
