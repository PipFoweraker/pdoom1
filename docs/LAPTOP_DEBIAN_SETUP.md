# Debian laptop -- what to set up, and what deliberately not to

**Status:** written 2026-08-10, before the machine arrived. The Linux isolation
incantation in section 4 is **reasoned, not executed** -- see the confirmation
step there.

## Why this doc is short

Pip named the use case honestly: *"laptop is really for dev work and builds"* --
then, *"and voice memos / and travelling / if i have to be honest / shiny new
thing excitement lol"*. Take the second version. The requirement is **elsewhere**
-- cafe, train, someone's kitchen -- and the uses are capture, light travel work,
and enjoying a new machine. A machine that is pleasant to open gets opened; that
is a real requirement, not a confession.

The failure mode this doc is written against is provisioning a perfect second
workstation that ends up used for voice notes on a train. So: two things on day
one, and a list of what is one command away when he wants it.

## 1. Day one -- the Syncthing folder (this is the actual job)

**Where memos land today, measured 2026-08-10, not assumed:**

| Stage | Where | Owner |
|---|---|---|
| Recorded | phone (F-Droid recorder) | -- |
| Transported | Syncthing, LAN-only, no cloud | `coordination/PHONE_TRANSPORT_v0.1_2026-08-02.md` |
| Lands on `Bort` | `G:\Documents\Organising_Life\phone-inbox` | 76 raw `.m4a` as of 2026-08-06 |
| Ingested | `G:\Documents\Organising_Life\capture` (`media/`, `meta/`, `derived/`, `manifest.jsonl`) | `coordination/tools/capture/capture_ingest.py`, env `CAPTURE_ARCHIVE` |
| Transcribed | locally, `faster-whisper`, nothing uploaded | `coordination/tools/capture/capture_transcribe.py` |
| Extracted into this repo | `docs/SPOKEN_*.md` | a human re-reads before it is acted on |

The laptop is **node three**. `coordination/CHECKLIST_2026-08-10_three-node-transport.md`
already has it as step 4, deliberately after `NEW-BORT` is enrolled -- one new
variable at a time:

```
sudo apt install syncthing
systemctl --user enable --now syncthing
# http://127.0.0.1:8384 -- pair with BOTH other machines, share the ONE capture folder
```

Then the only test that counts: record ten seconds on Bort, watch it arrive,
transcribe it on the laptop, **read the transcript**. Two dead links in series
look exactly like one working pipeline.

Sync **only** the capture folder. Not through git -- the archive is audio, and it
mixes repo routing with personal and financial material. Bidirectional, megabytes.

**The laptop's job is CAPTURE, not processing.** Transcription happens wherever
is convenient; it does not have to be here.

## 2. Day one -- a git clone

```
git clone <this repo>
```

Free, and it means the machine is ready if he wants it. Everything dev work
touches is in the repo -- including `tools/art_review/review_state.json`, the
human art verdicts, which are the irreplaceable part of the corpus and already
replicate through git. Measured on 2026-08-10: **2,713 entries, 2,704 carrying a
verdict** (`python -c "import json;print(len(json.load(open('tools/art_review/review_state.json'))))"`).
The "5,794 verdicts" figure in `docs/POSTMORTEM_2026-08-07_CAPTURE.md` does not
match the file today; the commit that tracked it (`f239af06`) says 2,713.

## 3. Not day one, and each is one command away

Deferring costs nothing. Listed so nobody sits in a cafe wishing they had
installed something.

| Deferred | Why | When wanted |
|---|---|---|
| `art_generated/` (~6.8 GB) | art review is a big-screen job -- Pip said so | rsync the directory; it is gitignored, so it never arrives with the clone |
| Godot 4.5.1 | nothing on the laptop needs the engine to read code | download the Linux binary, put it on `PATH`, then `godot --headless --path godot --import` once |
| Export templates | only builds need them | Godot editor: Editor > Manage Export Templates, matching 4.5.1-stable |
| Builds | see section 5 | `python tools/build_release.py --preset "Linux/X11" --output builds/linux` |

## 4. The section that matters -- Linux containment

**`CLAUDE.md`'s isolation rule is Windows-specific and following it on Linux
gives you NO isolation at all.** It says isolate via `APPDATA` and that
`XDG_DATA_HOME` does not work. Both true on Windows. **Both false on Linux**,
where `APPDATA` is meaningless and `XDG_DATA_HOME` is exactly the lever.

An agent obeying our own documented rule on that laptop runs **unisolated** and
writes straight into the real player profile -- the same defect that destroyed a
50-entry league board on 2026-08-08, arriving through the opposite door.

**The Linux incantation:**

```
XDG_DATA_HOME=/tmp/pdoom1-godot-iso-<lane> HOME=/tmp/pdoom1-godot-iso-<lane> \
  godot --headless --path godot ...
```

Set **both**. Reasoning, stated so it can be checked rather than trusted: Godot 4
resolves `user://` to `<data path>/godot/app_userdata/<config/name>`; on Linux the
data path is `$XDG_DATA_HOME` when set to an absolute path, and `$HOME/.local/share`
otherwise. `XDG_DATA_HOME` alone should suffice; `HOME` is the belt to its braces,
and covers the case where the var is ignored (Godot ignores a **relative**
`XDG_DATA_HOME` with a warning -- use an absolute path).

Better: **do not hand-roll it.** `scripts/run_godot_tests.py` already sets all
three vars (`APPDATA`, `XDG_DATA_HOME`, `HOME`) to a per-checkout sandbox, so the
supported entry point is already correct on Linux.

**What is verified.** Verified: `.github/workflows/godot-tests.yml` runs
`run_godot_tests.py` on `ubuntu-latest`, and
`godot/tests/unit/test_userdata_isolation.gd::test_runner_supplied_a_sandbox`
asserts `user://` resolves *inside* the declared sandbox.

**Now also verified ON THIS MACHINE (2026-08-17), which is what this section
asked for.** Godot 4.5.1 at `/home/pip/.local/bin/godot`; the fast gate ran
`1360 tests, 0 failures` in ~16s and `test_runner_supplied_a_sandbox` reported a
**pass, not the skip branch**:

```
the runner declared a sandbox at /tmp/pdoom1-godot-userdata/efc8e9b003e0
but user:// resolved to /tmp/pdoom1-godot-userdata/efc8e9b003e0/godot/app_userdata/P(Doom)
```

**And the open question is closed: `XDG_DATA_HOME` is the variable that does it.**
This doc previously recorded that as unverifiable because the runner sets both
together. Pointing the two at DIFFERENT sandboxes separates them, which is safe
in both outcomes because neither is the real profile:

```
XDG_DATA_HOME=/tmp/pdoom1-probe-xdg HOME=/tmp/pdoom1-probe-home \
  godot --headless --path godot --script res://<a script printing OS.get_user_data_dir()>

  -> /tmp/pdoom1-probe-xdg/godot/app_userdata/P(Doom)
```

`XDG_DATA_HOME` wins outright. `HOME` is genuinely only the belt to its braces --
still set both, because the reasoning above (Godot ignores a *relative*
`XDG_DATA_HOME`) is unchanged and costs nothing.

**Still confirm on any new machine, before trusting the above** -- run the fast
gate and check that `test_runner_supplied_a_sandbox` passes rather than skips:

```
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
```

If it skips, the sandbox var did not reach the engine, and the isolation is not
real. **Correct this doc from the machine.** An unverified isolation instruction
is worse than none, because it will be trusted.

Also, unchanged from Windows: do NOT set `use_custom_user_dir` in
`project.godot` -- that ships to players.

## 5. The Linux build capability -- a thing to do once, deliberately, later

We ship Linux zips that CI builds, and `docs/RELEASE_PLATFORMS.md` states plainly
that **no human on this project has ever launched one**. It is reported that an
external player did, by accident, on 2026-08-10 (`Kaur, Chen & Lindqvist`, score
44, 1546s) -- **I could not find that record in this checkout**, so treat the
name and figures as needing confirmation against the live board.

This laptop could make us a Linux build-and-test machine, which is what `#917`
(cross-OS releases) wants. Do it as one deliberate afternoon: install Godot and
export templates, build the Linux preset, launch the binary, note that
`docs/RELEASE_PLATFORMS.md:361` can finally change.

**That is not a reason to provision the laptop as a dev box on day one.** The
capability is worth naming precisely so it does not get smuggled into a travel
machine's setup as urgency.
