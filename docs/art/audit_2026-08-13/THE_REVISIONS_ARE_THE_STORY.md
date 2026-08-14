# The revisions are the story

**Draft for Pip, 2026-08-14, by `seat:pdoom`.** Raw material for a blog post and
for `pdoom1-website#308`. Not published anywhere. Every number is re-derivable
from `tools/art_review/review_log.jsonl`, which is committed.

---

## The argument, in one line

Austin Chen's second objection to the Manifund campaign was that the visuals read
as **"AI-generated and/or chaotic"**, and his recommendation was to work with a
professional graphic designer.

**The honest answer is not "we hired a designer". It is: the chaos was never the
generation, it was the absence of curation -- and here is the curation, with
receipts.**

## What happened on 2026-08-14

**470 assets judged in 23.1 minutes. 20.3 decisions a minute, one every 2.9
seconds.**

| | |
|---|---|
| `discard` | **274** |
| `keep` | 198 |
| `remix` | 13 |
| `shelf` | 2 |

**Discard outnumbered keep 1.4 to 1.** That ratio is the whole point. A gallery
that keeps everything is a dump; this was a cull.

And 62 of those judgements carried **written direction**, at 2.9 seconds each:

> *"one red team one blue team, combat, not chess, can be engineers facing each other off"*
> *"this si danerously close to a mtg symbol"*
> *"silhouette too boviously male, too obviously signalling Operator"*
> *"we ssem toh ave massively overindexed on the bankers lamp as an art object"*
> *"the approved needs to be the right way up, players can read up side down"*

## The part almost nobody publishes

**Fifteen assets were judged, then judged differently.** The tool records every
step rather than the final answer, so the changes of mind survive:

| asset | the sequence |
|---|---|
| `game_icons:action_strategic_lobby_government:v2` | `remix -> remix -> remix -> remix -> remix -> keep` |
| `an0807_l3_hero_land:s11_r06_p06:v3` | `-> -> -> keep` (three passes before a verdict stuck) |
| `screen_backgrounds:bg_welcome_lab:v1` | `remix -> shelf -> remix` |
| `ui_icons:indicator_risk_minimal:v1` | `shelf -> keep` |
| `game_icons:action_funding_grant_proposal:v3` | `keep -> discard` |
| `an0807_l0_anchors:s01_r01_p07:v1` and `:v2` | `remix -> discard` / `remix -> keep` -- siblings split |
| `an0807_l3_hero_land:s09_r06_p06:v2` | `remix -> discard`, note: *"bad composion"* |

**Five rounds of "not yet" before a keep is not indecision. It is a standard
being held.** The interesting artefact is not the final image; it is that the
same person looked at the same picture six times and only accepted it once it
changed.

### Why this record exists at all, and only just

`review_state.json` stores the CURRENT verdict per asset. It overwrites. Every
one of those sequences above would have been destroyed by the next click, leaving
only the last answer.

The append-only log (`review_log.jsonl`) landed on the morning of **2026-08-13**
and the session ran on **2026-08-14**. **It was about four hours old when it first
mattered.** Had the session run a day earlier, this document could not be written
-- the evidence would exist as a single row saying `keep`.

That is worth saying plainly in any published version: **we can show our working
because we changed the tool to keep it, and we nearly did not.**

## The claim this supports, and the claim it does not

**Supports:** *"Every asset in this game has been looked at by a human, judged,
and the judgement is on the record -- including the ones we changed our minds
about."*

Measured coverage as at 2026-08-14: **1,391 of 2,099 families decided (66.3%)**.
Not all of them. Say 66%, not "every".

**Does NOT support:** *"here is how it was made, you could remake it."* `seed` is
`null` in all 1,098 sidecars because the OpenAI Images API exposes no seed
parameter. **The record attests; it cannot reproduce.** Any published wording that
implies reproducibility is false.

## Ten candidates for the `#308` provenance publish

Selection rule: `keep` verdict, an0807 (so a full `.meta.json` sidecar exists),
**zero OCR text detections**, ranked by how much evidence the asset carries.

| # | asset | why it earns the slot |
|---|---|---|
| 1 | `an0807_l3_hero_land:s11_r06_p06:v3` | **4 log events** before the verdict stuck. Note: *"good"*. The strongest single demonstration of the record |
| 2 | `an0807_l3_hero_land:s10_r07_p03:v2` | 3 events. Note: *"i like the off-camera-ness of the pending weirdness"* -- taste stated in his own words |
| 3 | `an0807_l3_hero_land:s06_r06_p06:v2` | 2 events. Note: *"Tricolour with the cup rings is amazing"* -- names the specific thing that worked |
| 4 | `an0807_l3_hero_land:s03_r01_p01:v2` | clean keep; `s03` also has `r02_p02` and `r04_p07` kept, so the subject shows range |
| 5 | `an0807_l3_hero_land:s08_r01_p03:v2` | `s08` kept across three renderings -- good for showing rendering-vs-subject |
| 6 | `an0807_l3_hero_land:s01_r03_p09:v2` | the `p09` palette, distinct from the dominant green |
| 7 | `an0807_l3_hero_land:s04_r10_p08:v4` | `r10` rendering appears once in the whole kept set -- the outlier that survived |
| 8 | `an0807_l3_hero_land:s05_r06_p06:v4` | `r06_p06` recurs across `s05/s06/s09/s10/s11` -- the combination he kept most |
| 9 | `an0807_l3_hero_land:s02_r05_p04:v3` | v3 chosen over three siblings; a clean set-winner story |
| 10 | `an0807_l3_hero_land:s09_r06_p06:v1` | its sibling `:v2` was discarded with *"bad composion"* -- **publish the pair** and the judgement becomes visible |

**Number 10 is the one to lead with if only one ships.** A kept image beside its
rejected sibling and the four words that separated them is the entire argument in
one panel, and it needs no explanation.

## What each published asset can carry today

| field | present? |
|---|---|
| prompt + `prompt_sha256` | yes |
| model, size, quality, cost | yes (cost is a **tariff estimate**, `cost_is_billed_truth: false`) |
| taste-profile + queue-spec hashes | yes |
| **review state, verdict, notes, revision history** | **yes, as of 2026-08-14** |
| where-used | no -- absent from the sidecar schema |
| licence / usage rights | no -- absent |
| `seed` | **null, always** |
| content hash (`master_sha256`) | no -- only `master_bytes`, a length check |

## Before any of this goes near Manifund

`coordination/DRAFT_manifund_comment_2026-08-06.md` holds a standing constraint
and it still applies:

> **Why this should not go out until Mac has a true sentence.** The comment is
> much stronger opening by closing his actual blocker. Leading with art fixes
> while he still cannot launch the game reads as answering the easier question.
> **Fill the Mac line with something true, or cut it and accept a weaker comment
> -- do not soften it.**

Austin's objection 1 was that he could not play it on Mac (`PDOOM-9`). **That is
still the conversion blocker.** This document strengthens the art half; it does
not touch the half that matters more.

A blog post is a different surface from a Manifund comment and is not bound by
that constraint -- but if the post is going to be pointed at Austin, the same
logic applies.
