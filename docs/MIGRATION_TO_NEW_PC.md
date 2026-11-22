# Migrating pdoom1 to a new PC

> Measured 2026-08-20 on the current machine. Sizes and file counts are real
> counts, not estimates. Update them if they drift materially.

## The one-line version

`git clone` gets you **almost nothing that matters**. Roughly **17 GB of
load-bearing data lives outside git**, and the worst failure is silent: a fresh
clone runs the provenance backfill happily and records ~150 attributable assets
as `unknown`.

## What git does NOT have

| Store | Files | Size | Why it matters |
|---|---:|---:|---|
| `art_generated/` | 10,576 | **9.6 GB** | Only **534 are tracked.** Provenance **evidence tier D** resolves asset origin by hashing into this tree. Without it the backfill silently downgrades ~150 assets to `unknown`. |
| `G:/012 OBS Outputs/` | 150 | **5.5 GB** | Session recordings, the media library, transcripts. Irreplaceable -- these are records of work, not outputs of it. |
| `G:/tmp/pdoom1-art-masters/` | 1,119 | **1.9 GB** | The masters archive. `docs/art/ART_MASTERS_POLICY.md` says art over 1MB lives here and NEVER in git. The `tmp` in the path is a lie: this is permanent. |
| Godot player profile | 4,336 | **141 MB** | `C:/Users/Pip/AppData/Roaming/Godot/app_userdata/P(Doom)/` -- **the league boards.** A 50-entry board was destroyed here once already (#1070) and recovered only from a backup. |

**Carry all four.** Total ~17 GB.

## What re-downloads, so do not bother copying

| Thing | Size | How it comes back |
|---|---:|---|
| Godot export templates | 2.1 GB | Godot editor, matching the engine version. Needed by `tools/build_release.py`; its absence makes the build die with a bare `exited 1`. |
| Whisper model cache | 1.1 GB | First `tools/transcribe.py` run re-downloads to `~/.cache/whisper`. |

## Software the tooling assumes

Discovered by reading the tools, not by guessing:

| Needed by | What | Note |
|---|---|---|
| `tools/transcribe.py` | **ffmpeg** | Found via PATH, then per-platform fallbacks. Debian: `apt install ffmpeg`. Windows: `winget install Gyan.FFmpeg`. |
| `tools/transcribe.py` | **openai-whisper** | `pip install -U openai-whisper`. CPU-only is fine: ~5x realtime measured. |
| `tools/print_doc.py` | **SumatraPDF** (strongly preferred) | The ONLY silent print path. Without it the tool falls back to Acrobat (steals focus) and then to the Windows shell verb, which is **measured to exit 0 and print nothing** (2026-08-20). Install Sumatra early. |
| `tools/print_doc.py` | Edge or Chrome | HTML -> PDF rendering. |
| art generation | `OPENAI_API_KEY` | Environment variable. |
| everything | Python 3.11+ | The automation floor, enforced by a syntax gate. |

## The trap that will actually bite

**Godot writes to the REAL player profile from any headless run.** The user data
dir derives from `config/name` in `project.godot`, NOT from the worktree, so every
checkout shares one profile.

- **Windows:** isolate with `APPDATA=<temp dir>`. `XDG_DATA_HOME` does **nothing**.
- **Linux:** exactly backwards -- `XDG_DATA_HOME` is the lever, `APPDATA` means
  nothing. See `docs/LAPTOP_DEBIAN_SETUP.md` section 4.

Get this wrong on the new machine and the first headless test run writes into the
live boards. That is not hypothetical; it has happened.

## Order of operations

1. Clone the repo. Confirm `python --version` >= 3.11.
2. **Copy the four stores above before running any tool that reads them.** In
   particular do not run `tools/assets/backfill_provenance.py --write` until
   `art_generated/` is present, or it will write a manifest that validates
   cleanly and is wrong.
3. Install ffmpeg, SumatraPDF, whisper. Set `OPENAI_API_KEY`.
4. Install Godot and its export templates.
5. `pre-commit install --hook-type post-merge --hook-type post-checkout` -- the
   class-cache guard is inert until this runs.
6. `python tools/check_class_cache.py --repair`, then `make test`.
7. Verify isolation once: print `OS.get_user_data_dir()` under your isolation
   env and confirm it is NOT under `AppData/Roaming`.

## Paths that assume this machine

`G:/` appears in 44 tracked files. Most are prose in docs and are harmless. The
executable ones to check on a machine without a `G:` drive:

- `tools/validate_assets.py`
- `tools/transcribe.py` (has PATH-first fallbacks; verify anyway)
- `tools/print_doc.py` (has fallbacks)
- `docs/art/ART_MASTERS_POLICY.md` -- the masters staging path is policy, so
  moving it means changing the policy, not just the path.

If the new machine has no `G:` drive, decide the new masters root FIRST and
update the policy doc, rather than letting each tool guess.

## What is safe to abandon

- The session scratchpad (`AppData/Local/Temp/claude/...`) -- ephemeral by design.
- `godot/.godot/` -- generated, per-checkout, gitignored, and a STALE copy is
  actively dangerous. Never carry it.
- `.claude/settings.local.json` -- local, and never staged.
