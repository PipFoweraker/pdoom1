# The first mass review -- 23 minutes, 470 assets, 150 families unlocked

**Recorded by `seat:pdoom`, 2026-08-14.** Every number below is re-derivable from
`tools/art_review/review_log.jsonl` and `docs/art/audit_2026-08-13/retention_census.py`.

This is the first review session ever run through the v3 tooling, and the first
time anything in `art_generated/` was judged at scale.

## The session

| | |
|---|---|
| Span | **12:01:55 -> 12:25:00, 23.1 minutes** |
| Events written | **496** (plus 4 seat probes, excluded throughout) |
| Distinct assets judged | **470** |
| Rate | **20.3 assets/minute** -- one decision every 2.9 seconds |
| Blocks touched | **21** |

### Verdicts

| verdict | events |
|---|---|
| `discard` | 274 |
| `keep` | 198 |
| `remix` | 13 |
| `shelf` | 2 |
| cleared | 9 |

**Discard outnumbered keep 1.4 to 1.** A review that mostly keeps is not a review;
this one was doing real work.

### What he wrote while doing it

- **62 notes in his own words** -- design direction, not bookkeeping.
- 246 auto-notes from the set-winner button (`not chosen -- set winner: X`).
- **15 assets were revised mid-session** -- a verdict changed after first
  judgement. One went `remix -> remix -> remix -> remix -> remix -> keep`;
  another `shelf -> keep`; another `keep -> discard`.

**Those 15 are the append-only log earning its keep on day one.** Under the old
state file every one of those earlier judgements would have been overwritten and
unrecoverable. The revision history exists because the log landed hours earlier.

### A sample of the direction, verbatim

> *"silhouette too boviously male, too obviously signalling Operator"* (x4)
> *"one red team one blue team, combat, not chess, can be engineers facing each other off"*
> *"this si danerously close to a mtg symbol"*
> *"Tricolour with the cup rings is amazing"*
> *"we ssem toh ave massively overindexed on the bankers lamp as an art object"*
> *"Avoid cockleg problems, this is very funny though"*
> *"i like the off-camera-ness of the pending weirdness"*

## What it unlocked

| | before | after | delta |
|---|---|---|---|
| Families decided | 1,241 | **1,391 of 2,099 (66.3%)** | **+150** |
| Families undecided | 858 | **708** | **-150** |
| Discard families | 248 | **518** | **+270** |
| Freeable under the REJECTED rule | 274.8 MB | **594.3 MB** | **+319.5 MB** |

**Friday's hero exists.** 73 hero candidates judged, **19 kept**, 54 discarded.
Before this session the heroes had zero verdicts and the Friday push had no
image.

## The finding that matters for the next build

**Harvest tags used: 0. Shelf verdicts surviving: 0** (2 were set, both later
changed to something else).

The two-axis model -- the thing designed that morning on the strength of *"no but
I like the corner"* -- **went unused in its first real outing.** What he actually
used was **set-winner plus keep/discard**, almost exclusively.

That is not a failure of the idea; it is a measurement of the workflow. At 2.9
seconds per asset there is no room to type a tag. Harvest is a slow-lane feature
being offered in a fast lane. `AP11` should be answered from this, not from the
design intent: **the batch workflow is the real one, and the tooling should be
built for it.**

## Highest-leverage remaining work, by measured unlock

| block | families | bytes | note |
|---|---|---|---|
| `an0807_l1_grid` | **220** | **1,091.0 MB** | biggest single block left |
| the seven `l2_a_*` sweeps | **306** | **1,510.3 MB** | **parameter sweeps -- one winner per axis, so ~7 real decisions** |
| `an0807_l1_family` | 115 | 588.1 MB | partially reviewed already |
| `an0807_l3_hero_port` | 28 | 161.8 MB | zero portrait heroes chosen yet |
| `an0807_l3_hero_land` | 39 | 211.1 MB | remainder after this session |
| **TOTAL** | **708** | **3,562.3 MB** | |

**The sweeps are the standout.** 306 families and 1.5 GB gated behind roughly
seven judgements, because each sweep varies one parameter and needs one winner.
Nothing else on the board has that ratio.

## Standing constraints, unchanged by this session

- **Nothing has been deleted and nothing will be** without Pip's word.
  `art_generated/` remains under `MIGRATION-HOLD`
  (`coordination/ESTATE_2026-08-12_repo-register.md:92`).
- The freeable figures are **options with numbers attached**, not a plan.
- The undecided remainder still has **zero git coverage** -- it exists on one
  disk. That argues for backup before deletion, in that order.
