# Media retention policy -- recordings, transcripts and frames

Companion to `docs/art/ART_MASTERS_POLICY.md`, which does the same job for art
masters. Same principle: **big binaries live outside the repo, derived artifacts
live inside it.**

- **Status:** DRAFT for Pip's ruling, written 2026-07-30
- **Prompted by:** recorded playtests and design sessions becoming a routine
  part of the workflow, and the OBS output folder reaching **4.2 GB**

---

## 0. The one fact that drives everything

**Value and size are inversely correlated.** Measured on real 2026-07-29/30
sessions:

| Artifact | Size per hour | What it is |
|---|---|---|
| Transcript (`.md` + `.txt`) | ~50 KB | **the actual product** -- searchable, quotable, durable |
| Extracted marker frames | ~5 MB | the evidence for each finding |
| Flight-recorder capture (F6) | ~3 MB | screenshot + full game state + typed note |
| Stripped audio (16 kHz mono mp3) | ~20 MB | re-transcribable source |
| Video, 1080p30 | ~170 MB | motion, mouse path, timing |
| Video, 4K60 | **~1.2 GB** | the same thing, 7x bigger |

A 34-minute conversation was 218 MB of file for 12 MB of speech and 32 KB of
transcript. **The transcript is 0.015% of the bytes and roughly all of the
value.**

The corollary: **the cheapest storage decision is made at record time, not at
archive time.** Dropping OBS from 4K60 to 1080p30 gave an 8x reduction for
free, and it beats any disk purchase.

---

## 1. Tiers

### Tier 0 -- KEEP FOREVER, tracked in git
Transcripts, extracted findings, flight-recorder notes, and any issue or doc
they produced. Kilobytes. These are the reason the recording existed.

Location: `docs/`, or the issue tracker. **Never** the raw media.

### Tier 1 -- KEEP FOREVER, outside git
Flight-recorder captures (screenshot + `state.json` + note) and marker frames
that a live issue references. Megabytes. Small enough to keep indefinitely,
specific enough to be worth it.

### Tier 2 -- KEEP MONTHS, outside git
The stripped 16 kHz mono audio. ~20 MB/hour. Cheap insurance: if a transcript
needs re-running on a better model, this is the input, and it is 6% of the
video's size.

### Tier 3 -- KEEP WEEKS, outside git
The raw video. Delete once its transcript and frames exist and the findings are
filed. Retain longer only for a specific reason (an unresolved bug that needs
the motion, footage earmarked for a devblog or trailer).

---

## 2. Where things live

```
G:\012 OBS Outputs\              OBS writes here. Source of truth until ingested.
G:\pdoom1-media\                 PROPOSED: the media store, OUTSIDE the repo
    raw\YYYY-MM-DD\              Tier 3
    audio\                       Tier 2
    captures\                    Tier 1
<repo>\art_generated\audiodump\  working set only -- gitignored, prunable
<repo>\docs\                     Tier 0 -- transcripts and findings, tracked
```

**Raw video must not live inside the repo tree, even gitignored.** Three
reasons, in order: it makes the working folder enormous; it slows every tool
that walks the tree; and one mistaken `git add -A` is unrecoverable in a public
repo. The `.import`/`.uid` staging trap in CLAUDE.md is the same hazard class.

Today's practice puts the working set in `art_generated/audiodump/`, which is
gitignored and therefore safe, but it is a working set and should be pruned --
not an archive.

---

## 3. The workflow

```
python tools/ingest_recordings.py            # today's recordings, copy across
python tools/playtest_report.py <file>       # transcript + marker frames + review page
```

`ingest_recordings.py` copies rather than moves by default, so OBS keeps the
original until a retention decision is made deliberately. Once this policy is
ratified, `--move` becomes the normal call and OBS stops being an archive.

**Say BUG or NOTE out loud while recording** (`tools/runsheet/playtest_card.html`).
It is what makes the transcript mechanically convertible into Tier 0.

---

## 4. If streaming happens, this changes

Streaming makes the platform the cold storage. YouTube or Twitch keeps the raw
indefinitely at no local cost, which means:

- Tier 3 local retention drops to **days**, not weeks.
- A large local disk becomes a **working scratch**, not an archive -- so buy
  for throughput and convenience, not capacity.
- A new tier appears: **published** media, which is public, permanent, and
  outside your control to delete. That has its own review requirement, because
  a stream captures whatever is on screen.

**Privacy, learned the hard way (2026-07-29):** a recorded session contained a
mobile phone number spoken aloud in passing. It was harmless only because
`art_generated/` is gitignored. Anything moving toward a public surface --
a tracked path, a devblog, a stream VOD -- must be reviewed first. A recording
captures what was said, not what was intended.

---

## 5. Open questions for Pip

1. Ratify `G:\pdoom1-media\` as the store, or pick another location?
2. Tier 3 at weeks -- too long, too short?
3. Should `ingest_recordings.py` default to `--move` once this is ratified?
4. Is a scheduled prune wanted, or is deleting by hand fine at this volume?
   (At 1080p30 and a session a day, Tier 3 grows ~1 GB/week. Manual is fine
   for a long time.)
5. Streaming: platform-as-archive, or keep local masters regardless?
