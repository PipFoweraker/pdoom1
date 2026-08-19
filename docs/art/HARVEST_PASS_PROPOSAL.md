# Harvest as a second pass -- decision card

> **Status: BUILT 2026-08-17** (ruled and built; this card is kept as the argument
> and the evidence trail). Written 2026-08-15 as a proposal. Self-contained:
> assumes no session context.
>
> **What shipped:** a harvest mode in `tools/art_review/serve_review.py` --
> press `H` or the `[H] harvest pass` chip. You pick a QUESTION first; the filter
> and the tag palette follow from it. Tags apply to the whole selection, ADD
> rather than replace, and never touch the verdict. Palette is seeded from the
> mined notes below and grows by use. Tests: `tests/test_harvest_pass.py` (24).
>
> **Not built, still open:** `check:in-game` for the 268 "needs a manual eyeball"
> notes (proposed, unruled), and the note-field keystroke logging described at the
> bottom of this card.

## The ask in one line

Make harvesting a **separate sweep over already-decided assets**, instead of a
field on the decision, and seed its vocabulary from the notes Pip has already
written.

## Context -- why this is on the queue

The review vocabulary has two axes (`docs/art/NOMENCLATURE.md`):

- a **verdict** is an asset's fate -- exactly one, exclusive
- a **harvest tag** is what *survives* that fate -- any number, still applies to a
  discard. "No, but I like the corner" is a discard plus `element:corner`.

The harvest axis has effectively never been used.

```
assets with a verdict        7,944
assets with a harvest tag        2      (0.03%)
```

Measured over `tools/art_review/review_state.json`, 2026-08-15 11:17 AEST.

The batch-selection UI (b1287e8b, 2026-08-15 00:33) was built partly to fix this
-- its own commit message says the first mass review used "ZERO harvest tags,
because there is no room to type in that lane". The room now exists. The
behaviour did not follow.

## Pip said this out loud DURING the sweep, two days before describing it

Added 2026-08-17, after the session audio was transcribed
(`tools/transcribe.py`, local whisper, offline). The recording of the
2026-08-14 sweep contains the multi-pass workflow being invented in real time:

```
12:33  I don't know what to do with these ones, so I'm just going to scroll past them.
12:43  I'll come back and judge these later if we want.
16:33  Interesting. Okay, I'm going to do another pass for winners, and then I'm
       going to just export and try and figure out what the next process is.
16:40  This has been kind of cool, though. I suppose I can just click and give
       more opinions on...
16:44  No, actually, let me do another pass, because I think without instructions,
       I'm not sure where my limited attention is going to be best spent.
```

Two things this changes:

1. **The need is evidenced, not inferred.** The proposal below was written from
   a 0.03% tag rate and one remark. It is now backed by the reviewer narrating
   the same conclusion mid-sweep, unprompted, before anyone analysed anything.

2. **It adds a design constraint nobody had.** 16:44 gives the REASON: *"without
   instructions, I'm not sure where my limited attention is going to be best
   spent."* A pass is not just a filter -- **a pass needs a stated purpose**, or
   the reviewer cannot tell what to look at. So the harvest pass should open by
   declaring its own instruction ("you are looking for what to keep from these
   discards"), not merely present a filtered grid. 12:33 is the same problem
   with no pass available: scrolling past rather than deciding.

Also captured, and not otherwise recorded anywhere:

```
0:05   Marking that as a keep is opposite of picking it as a winner.
```

That is friction in the verdict model itself -- `keep` and "winner of a set" are
being conflated at the point of use. It appears in no note, no issue and no
verdict. It is exactly the kind of thing that only exists in audio.

## The diagnosis (Pip, 2026-08-15)

> "I want to harvest things after I've decided what I liked or disliked about
> them. Negative sweep passes with commentary en masse felt good."

**The tool asks for the tag at the wrong moment.** Verdict and harvest are
presented as one form, so harvesting competes with sweeping for the same
seconds. It loses, every time, because fate is urgent and harvest is not.

This is a TIMING problem, not a discipline problem. The relevant precedent is
already in this estate: a field nobody is asked about at the moment the answer
exists does not get filled in.

## The evidence that makes this cheap: the vocabulary already exists

Pip's batch notes ARE a tag vocabulary written in prose. From
`review_log.jsonl`, notes by verdict, excluding the `not chosen -- set winner`
boilerplate:

### Discards -- these are flaws, stated and counted

| times applied | note | reads as |
|---:|---|---|
| 92 | regretful retire spookycat for now | subject retirement, not a flaw |
| 69 | this is cool and i like the glowing eyes, but ... | a LIKE inside a discard -- exactly what harvest is for |
| 60 | these all seem way too small | `flaw:scale` |
| 56 | unsure | a deferral, not a flaw |
| 32 | these feel blurry? check process and report back? | `flaw:blurry` |
| 16 | these seem too blurry? | `flaw:blurry` -- **same concept, second phrasing** |
| 8 | I think the shininess / refractivity here is unpleasant? | `flaw:shiny` |
| 8 | dislike | unlabelled |
| 7 | no thanks | unlabelled |

42 distinct discard notes across 404 applications.

### Keeps -- mostly assent, some real signal

| times applied | note |
|---:|---|
| 587 | ok |
| 211 | all orange cat files, all seem fine |
| 148 | this seems like a pleasing representation of Kambu for now, approved |
| 148 | This little chonker needs a manual eyeball but he survives the cull for now |
| 148 | keep |
| 120 | cat sprites seem fine, want to check in-game |

53 distinct keep notes across 1,680 applications. Note the recurring
**"needs a manual eyeball" / "want to check in-game"** -- that is a follow-up
state the vocabulary has no word for, applied 268 times.

### The fragmentation this fixes

`blurry` was written two ways and counted separately: 32 + 16. In prose those
are two facts; as `flaw:blurry` they are one fact worth 48. **The whole value of
a tag over a note is that it is countable and groupable.** Prose cannot answer
"how often did small-scale kill an asset?"

## Proposal

### 1. A harvest pass, run after a verdict sweep

- Filter the gallery to already-decided assets -- **discards first**, since a
  discard is where harvest matters most (the image dies, the lesson should not).
- Batch-select exactly as now (shift-click over the filtered set).
- Apply a tag from a **palette of buttons**, not a text field. One click.
- The existing batch note stays available for the prose that does not fit a tag.

The interaction Pip already likes -- select many, apply one commentary -- is
unchanged. Only the *pass* is new.

### 2. Seed the palette from the mined notes

Do not ask for a vocabulary to be invented. Derive the starting palette from the
table above, present it, and let it grow by use. A first-use types a new tag; a
second use clicks it.

### 3. Vocabulary question -- NEEDS A RULING

`element:<thing>` is defined as "a component worth keeping when the image is
not". It has no negative counterpart, and Pip's sweeps are mostly negative.

| option | shape | trade |
|---|---|---|
| **A. add `flaw:<thing>`** (recommended) | `flaw:blurry`, `flaw:scale`, `flaw:shiny` | Countable dislikes, symmetric with `element:`. One new namespace to publish to other repos. |
| B. reuse `element:` for both | `element:blurry` | No new vocabulary, but loses polarity -- cannot tell "keep this bit" from "this bit killed it". |
| C. leave dislikes in prose | status quo | Zero work, and the fragmentation above persists. |

A fourth term may be warranted for the 268 "needs a manual eyeball" notes --
something like `check:in-game`. That is a follow-up marker, not a like or a
dislike, and it is currently invisible to every downstream tool.

## Also found, and worth its own decision

**The note field logs every keystroke pause as a separate event.** One note was
saved six times in eleven seconds on the same asset:

```
12:04:56.475  'at leats 2 c'
12:04:57.985  'at leats 2 colour '
12:05:00.126  'at leats 2 colour tones please'
12:05:03.113  'at lea 2 colour tones please'
12:05:03.546  'at least 2 colour tones please'
12:05:07.800  'at least 2 colour tones please'
```

Impact is small but real: **1.4% of Friday's events and 1.7% of Saturday's are
keystroke re-saves.** It pollutes any attempt to mine the vocabulary, because
partial words become distinct "notes". Correcting for it moves Saturday's
throughput from 33.7 to **35.2 assets per decision** -- the number gets better,
not worse.

Suggested fix: save on blur/commit rather than on keystroke, or collapse
consecutive same-asset same-verdict writes at projection time. The log stays
append-only either way.

## Precise ask

**For Pip:** rule on the vocabulary question (A / B / C above), and on whether a
follow-up marker like `check:in-game` joins the taxonomy.

**For `pdoom1-website` and `pdoom-data`:** `docs/art/NOMENCLATURE.md` is the
generated vocabulary you quote. Adding `flaw:` and possibly `check:` extends it.
Does either collide with, or duplicate, anything you already consume? This is a
veto request, not a build request.

## Sources

- `tools/art_review/review_state.json`, `tools/art_review/review_log.jsonl`
- `docs/art/NOMENCLATURE.md` -- the two-axis vocabulary (GENERATED)
- commit `b1287e8b` -- batch selection, and the measurement that motivated it
- `docs/rulings/RULINGS_CONVENTION.md` -- where the resulting ruling should land
