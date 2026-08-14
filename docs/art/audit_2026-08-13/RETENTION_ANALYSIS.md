# art_generated/ retention analysis -- 2026-08-13

Status: **read-only measurement**. Nothing was deleted, moved, or renamed.
`art_generated/` is under MIGRATION-HOLD (`coordination/ESTATE_2026-08-12_repo-register.md`).
This document supplies numbers for a decision Pip makes; it recommends no deletion.

Every number below is reproduced by one command, run from the repo root:

```
python docs/art/audit_2026-08-13/retention_census.py
```

That script (in this directory) is read-only: it opens files, walks directories, and
prints. It writes nothing. Section numbers in its output map to section numbers here.

---

## 0. Parsing guard -- what counts as a resolution variant

The known trap: a 292 MB `.mp4` whose stem ends in `38` parses as "resolution 38", and
a naive parse silently books a video into the image tiers. Guard applied, both
conditions required:

- (a) extension in `{.png, .webp, .jpg, .jpeg}`
- (b) filename stem matches `^(.*)_(\d+)$` **and** that integer is in
  `{1536, 1024, 768, 512, 256, 128, 64}`

Anything failing either test is **excluded from every tier and every rule** and reported
here separately. It is never bucketed.

| Class | Files | Bytes | MB |
|---|---:|---:|---:|
| Parseable resolution variants (in 2,099 families) | 8,722 | 8,227,990,421 | 7,846.8 |
| Images failing guard (b) -- excluded | 618 | 60,521,531 | 57.7 |
| Non-image files failing guard (a) -- excluded | 1,236 | 1,336,883,208 | 1,275.0 |
| **Total** | **10,576** | **9,625,395,160** | **9,179.5** |

Partition check printed by the script: `8227990421 + 60521531 + 1336883208 = 9625395160` -> `OK`.

**618 images excluded, and why:**

| Block | Files | Bytes | Reason |
|---|---:|---:|---|
| `audiodump/frames_2026-07-30` | 526 | 54,003,558 | video keyframes named `t001.jpg`, `spot_289s.jpg` -- the numeric tail is a frame index or a timestamp, not a resolution |
| `iconset_round2` | 64 | 195,690 | stems end `_32` / `_48`, real sizes but outside the declared resolution set |
| `scene_art_wave2` | 28 | 6,322,283 | `.webp` named `event_board_v1.webp` -- no numeric tail at all |

The `_32` / `_48` case is the interesting one: those are almost certainly genuine
resolution variants under a different tier ladder. They are excluded here because the
brief fixed the resolution set, not because they are junk. 0.2 MB, so it does not move
any total.

**1,236 non-image files excluded** (this is where the `.mp4` trap lives):

| Ext | Files | Bytes | MB |
|---|---:|---:|---:|
| `.mp4` | 16 | 1,222,977,929 | 1,166.3 |
| `.mp3` | 31 | 82,282,738 | 78.5 |
| `.html` | 26 | 19,105,455 | 18.2 |
| `.json` | 1,104 | 9,846,283 | 9.4 |
| `.log` | 24 | 1,918,272 | 1.8 |
| `.md` / `.txt` / `.jsonl` | 35 | 752,531 | 0.7 |

The 16 `.mp4` files hold **1.17 GB -- 12.7% of the whole tree** and no retention rule in
this brief touches them. Flagged, not actioned.

---

## 1. Family census

Family key = `<block>/<vdir>/<basename-with-resolution-suffix-stripped>`.

- **2,099 families**
- **2,093 exist at more than one resolution** (2,099 minus the 6 single-tier families)

This matches the brief's stated ~2,099 / ~2,093 exactly, which is the strongest available
check that this parse agrees with whoever counted before.

| Tiers per family | Families |
|---:|---:|
| 1 | 6 |
| 2 | 59 |
| 3 | 152 |
| 4 | 1,268 |
| 5 | 614 |

The tier ladders are not arbitrary -- eight distinct ladders account for everything:

| Tier set | Families | Reading |
|---|---:|---|
| (1536, 1024, 768, 512) | 1,210 | the "big art" ladder -- scenes, heroes, anchors |
| (1024, 512, 256, 128, 64) | 614 | the "icon" ladder |
| (1024, 512, 256) | 124 | truncated icon ladder |
| (512, 256, 128, 64) | 58 | small icon ladder |
| (1024, 512) | 47 | pair only |
| (1024, 768, 512) | 28 | |
| (1536, 768) | 12 | |
| (768,) | 6 | `round3_rerolls_banners/v1/*` -- the only single-tier families |

The 6 single-tier families cannot be shrunk by any keep-largest rule; they already are
their largest file.

---

## 2. Bytes by resolution tier, whole tree

| Tier | Files | Bytes | MB | Share of family bytes |
|---:|---:|---:|---:|---:|
| 1536 | 1,222 | 3,508,633,395 | 3,346.1 | 42.6% |
| 1024 | 2,023 | 2,976,992,500 | 2,839.1 | 36.2% |
| 768 | 1,256 | 947,879,903 | 904.0 | 11.5% |
| 512 | 2,081 | 709,092,102 | 676.2 | 8.6% |
| 256 | 796 | 66,381,558 | 63.3 | 0.8% |
| 128 | 672 | 14,699,277 | 14.0 | 0.2% |
| 64 | 672 | 4,311,686 | 4.1 | 0.05% |
| **Total** | **8,722** | **8,227,990,421** | **7,846.8** | 100% |

The shape that matters: **1536 and 1024 together are 78.8% of all family bytes** (6,485,625,895)
while being 37.2% of the files. The 256/128/64 tiers together are 2,140 files but only
**85,392,521 bytes -- 1.0%**. Deleting small downscales recovers almost nothing; the
decision is entirely about the top two tiers.

---

## 3. REJECTED rule: `discard` families keep the highest resolution only

Verdicts read from `tools/art_review/review_state.json`, `gen:<block>:<family>:<variant>`
keys. Legacy `iterate` / `maybe` / `reroll` mapped to `remix` as instructed.

Raw verdict values present in the file today (the rename has **not** been written back --
the file still stores the legacy names):

| Stored value | Keys |
|---|---:|
| `keep` | 4,644 |
| `discard` | 809 |
| `maybe` | 130 |
| `iterate` | 126 |
| `reroll` | 84 |
| `` (empty) | 1 |

No key stores `shelf` or `remix`. See section 8 for why the key totals here are far
larger than the family counts below.

**Rule applied to the 248 `discard` families:**

| Quantity | Bytes | MB |
|---|---:|---:|
| Currently held by discard families | 810,630,741 | 773.1 |
| Retained (largest file of each family) | 522,485,585 | 498.3 |
| **Freed** | **288,145,156** | **274.8** |

Freed = **3.0% of the whole tree**, **3.5% of family bytes**.

For contrast, and *not* the rule asked for: dropping discard families entirely would free
810,630,741 bytes (773.1 MB). The keep-largest rule therefore recovers 35.5% of what a
full drop would.

---

## 4. ACCEPTED rule: what does the game actually render?

**Partially answerable. The per-family byte figure is NOT computable, and I am stating
that rather than guessing.**

What the grep does establish (script section 7 -- scans `godot/` excluding `.godot/` and
`addons/` for `res://` and `uid://`):

- 353 distinct `res://` image references; 351 exist on disk
- 31 distinct `uid://` references, **0 of which resolve to an image** -- every `uid://`
  in game source points at a scene or script, so the `res://` set is the whole picture
- Total bytes of referenced images: **25,198,273 (24.0 MB)**

Pixel dimensions of the 351 referenced images:

| Dimensions | Count | Note |
|---|---:|---|
| 64 x 64 | 146 | icons and sprite frames |
| 92 x 92 | 120 | office-floor worker sprites |
| 180 x 180 | 50 | `artloop_char` |
| 512 x 512 | 20 | all `godot/assets/textures/` surfaces and terminals |
| 1536 x 1024 | 3 | `office_scene.png`, `computer_1.png`, `computer_2.png` |
| 1928 x 1808 | 1 | `office_cat.png` |
| 1024 x 1024 | 1 | `cat_closeup.png` |
| 256 / 128 / other | 5 | `logo.png` at 256, misc |
| (unreadable header) | 5 | `.webp`/`.jpg` -- dimension not parsed, see section 9 |

Read as a rule: **the game renders at 512 or below for everything except five background
plates.** The maximum icon size in use is 512; the only assets above 1024 are one cat and
three scene backgrounds.

**Why this does not convert into a byte figure for `art_generated`:**

The two trees do not share filenames. Of 2,003 distinct family basenames in
`art_generated`, only **7** appear as a shipped basename (`compute`, `doom`, `logo`,
`money`, `paper`, `reputation`, `research`), rising to 8 after stripping `_vN`
(`intro_bus_strangers_help`). And even those 7 do not match by size: `art_generated/core_resource_icons/v1/compute_*`
exists at 1024/512/256/128/64, while the shipped `godot/assets/icons/compute.png` is
**64 x 64, 9,300 bytes** -- it was exported and hand-processed, not copied.

So `art_generated` is a **generation staging tree, not a source tree the build reads
from**. 751 families carry a `keep` verdict; at most 8 of them have a shipped
counterpart. "Keep only what the game renders" cannot be evaluated per family, because
for ~99% of `keep` families the game renders nothing at all yet -- they are approved art
awaiting a shipping decision, not shipped art with surplus tiers.

What I can offer instead is the scenario table: **if** the ACCEPTED rule is later defined
as "cap keep families at tier T", these are the numbers. Current `keep`-family holdings:
751 families, 2,301,585,669 bytes (2,195.0 MB).

| Cap T | Retained bytes | Freed bytes | Freed MB |
|---:|---:|---:|---:|
| 1536 (= keep largest only) | 1,501,162,343 | 800,423,326 | 763.3 |
| 1024 | 1,104,629,156 | 1,196,956,513 | 1,141.5 |
| 768 | 361,933,257 | 1,939,652,412 | 1,849.8 |
| 512 | 258,291,300 | 2,043,294,369 | 1,948.6 |
| 256 | 139,989,532 | 2,161,596,137 | 2,061.5 |
| 128 | 115,708,632 | 2,185,877,037 | 2,084.6 |
| 64 | 109,368,439 | 2,192,217,230 | 2,090.7 |

(Cap semantics: each family keeps its largest tier at or below T; a family with no tier
at or below T keeps its smallest.)

The evidence-backed cap suggested by section 7's dimension histogram would be **512**,
which frees 2,043,294,369 bytes (1,948.6 MB) from `keep` families. I am flagging that as
an *inference from what currently ships*, not a measurement of what these families are
for -- several `keep` blocks are hero/banner art whose intended use may legitimately be
1536. That call is Pip's.

---

## 5. The undecided majority

**858 families have no verdict of any kind, holding 4,411,056,137 bytes (4,206.7 MB).**

That is **45.8% of the whole tree** and **53.6% of all family bytes** -- more than the
keep, remix, and discard buckets combined (3,816,934,284 bytes).

Their tier profile is top-heavy even by this tree's standards:

| Tier | Undecided bytes | MB |
|---:|---:|---:|
| 1536 | 2,264,343,856 | 2,159.7 |
| 1024 | 1,219,546,431 | 1,163.1 |
| 768 | 624,796,924 | 595.8 |
| 512 | 296,372,882 | 282.6 |
| 256 | 5,996,044 | 5.7 |
| 128 / 64 | 0 | 0.0 |

1536 alone is 51.3% of undecided bytes. The undecided set holds **64.5% of every 1536px
byte in the tree** -- the biggest files are precisely the ones nobody has ruled on.

By block:

| Block | Families | Bytes | MB |
|---|---:|---:|---:|
| `an0807_l1_grid` | 220 | 1,144,035,611 | 1,091.0 |
| `an0807_l3_hero_land` | 112 | 642,091,845 | 612.3 |
| `an0807_l1_family` | 116 | 621,826,439 | 593.0 |
| `an0807_l2_a_pitch` | 48 | 252,158,420 | 240.5 |
| `an0807_l2_a_distance` | 42 | 247,717,481 | 236.2 |
| `an0807_l2_a_yaw` | 48 | 235,121,184 | 224.2 |
| `an0807_l2_a_style_tween` | 42 | 226,337,766 | 215.9 |
| `an0807_l2_a_quiet` | 42 | 225,642,369 | 215.2 |
| `an0807_l2_a_title_space` | 42 | 202,559,109 | 193.2 |
| `an0807_l2_a_decay` | 42 | 194,110,800 | 185.1 |
| `an0807_l3_hero_port` | 28 | 169,706,420 | 161.8 |
| `an0807_l0_anchors` | 54 | 129,126,561 | 123.1 |
| `endgame_concepts_gen2` | 21 | 114,396,300 | 109.1 |
| `wanasai_calls` | 1 | 6,225,832 | 5.9 |
| **Total** | **858** | **4,411,056,137** | **4,206.7** |

The concentration is the actionable fact: the **12 `an0807_*` blocks (the 2026-08-07 art
night) hold 4,290,434,005 of the 4,411,056,137 undecided bytes -- 97.3%**. Add
`endgame_concepts_gen2` and 13 blocks cover 4,404,830,305, or **99.86%**. This is not 858
scattered judgement calls; it is essentially one unreviewed generation run, and a single
review session over `an0807_*` converts 97.3% of the undecided mass into rule-eligible
bytes.

For reference, if a keep-largest rule were ever applied to undecided families it would
free 1,955,029,552 bytes (1,864.5 MB) -- but no rule in this brief touches them, which is
the point of this section.

---

## 6. Combined table

All figures in bytes, against a tree total of 9,625,395,160.

| Segment | Families | Current bytes | Rule | Freed by rule | Untouched |
|---|---:|---:|---|---:|---:|
| `discard` | 248 | 810,630,741 | REJECTED: keep largest | **288,145,156** | 522,485,585 |
| `keep` | 751 | 2,301,585,669 | ACCEPTED: undetermined (sec. 4) | **not computable** | 2,301,585,669 |
| `remix` (was iterate/maybe/reroll) | 242 | 704,717,874 | none defined | 0 | 704,717,874 |
| `shelf` | 0 | 0 | none | 0 | 0 |
| **undecided** | **858** | **4,411,056,137** | **none -- no verdict** | **0** | **4,411,056,137** |
| unparseable images | -- | 60,521,531 | excluded by guard | 0 | 60,521,531 |
| non-image (incl. 1.17 GB mp4) | -- | 1,336,883,208 | excluded by guard | 0 | 1,336,883,208 |
| **Total** | **2,099** | **9,625,395,160** | | **288,145,156** | **9,337,250,004** |

Headline arithmetic:

- Freed under the only fully-specified rule (REJECTED): **288,145,156 bytes = 274.8 MB = 3.0% of the tree**
- Bytes no rule touches because the family is undecided: **4,411,056,137 = 45.8% of the tree**
- Bytes no rule touches for any reason (undecided + remix + shelf + unparseable + non-image):
  **6,513,178,750 = 67.7% of the tree**
- Bytes awaiting the ACCEPTED rule's definition: **2,301,585,669 = 23.9%**

Check: 6,513,178,750 + 2,301,585,669 + 810,630,741 = 9,625,395,160. Balances.

If the ACCEPTED rule is later set to cap `keep` at 512, the two rules together free
288,145,156 + 2,043,294,369 = **2,331,439,525 bytes (2,223.4 MB, 24.2% of the tree)**,
and 4,411,056,137 bytes still sit outside both rules pending review.

---

## 7. Sanity check against `du`

```
du -sm art_generated                  ->  9205
du -sm --apparent-size art_generated  ->  9180
du -sb art_generated                  ->  9625395160
find art_generated -type f | wc -l    ->  10576
```

Script total: **9,625,395,160 bytes across 10,576 files**.

- Versus `du -sb`: **byte-exact, zero discrepancy.**
- Versus `du -sm --apparent-size` (9,180 MB): script says 9,179.5 MB. Difference is `du`
  rounding to whole MB. Not a discrepancy.
- Versus plain `du -sm` (9,205 MB): **+25.5 MB, 0.28% higher than the script.** This is
  real and expected -- plain `du` reports *allocated disk blocks*, so 10,576 files each
  round up to a cluster boundary. At NTFS's 4 KB default that is up to ~41 MB of slack,
  and 25.5 MB observed sits inside that. Recovering files does recover the allocated
  size, not the apparent size, so **every "freed" figure in this document is a slight
  underestimate of disk actually reclaimed** -- by roughly 0.3%, or ~0.8 MB on the
  274.8 MB REJECTED figure. I have not adjusted for it.

---

## 8. Verdict-join method, and its one real weakness

`review_state.json` holds 5,794 keys across three namespaces. **They do not all address
this tree**, and conflating them would badly overstate review coverage:

| Namespace | Keys | Points at |
|---|---:|---|
| `px:` | 4,466 | `art_source/` -- pixellab output. Probe: the first path segment of 200/200 sampled `px:` keys exists as a directory under `art_source/`, and **0/200** under `art_generated/`. **Zero apply to this tree.** |
| `gen:` | 1,236 | `art_generated/` -- the namespace this analysis uses (1,235 carry a non-empty verdict) |
| `file:` | 92 | concrete paths, all under `art_generated/iconset_round2/` -- files whose stems end `_32`/`_48` and which the resolution guard already excludes, so they contribute nothing |

So the raw "4,644 keep verdicts" is misleading: only 1,235 verdicts address
`art_generated` at all, and they resolve to 1,241 families out of 2,099.

**The join rule** is `gen:<block>:<family>:<variant>` matched against
`<block>/<vdir>/<family>_<variant>`. A first pass matched only 1,128 families and left
107 `gen:` keys orphaned. Cause found: some blocks (`core_resource_icons`, `crt_frame_overlay`,
`ui_icons`) name files without an explicit `_vN` -- `compute_1024.png`, not
`compute_v1_1024.png` -- while the verdict key still says `:v1`. A documented fallback
(bare basename -> implicit `v1`) recovered all 107. **Final state: 1,235 of 1,235 `gen:`
verdict keys matched a family on disk; 0 orphans.** This is the check that would have
caught a silent 8.7% undercount of reviewed families, and it is worth re-running after
any future rename.

**Known weakness, disclosed:** 6 `gen:` keys match **two** families each, all in
`game_icons/v1/`, where both `icon_compute` and `icon_compute_v1` exist side by side
(also `icon_doom`, `icon_governance`, `icon_money`, `icon_papers`, `icon_reputation`).
The single verdict is applied to both. If those pairs are genuinely different images
rather than duplicates, up to 6 families carry a verdict that was not cast on them. All
6 are small icons; the maximum possible byte error is well under 20 MB and cannot move
any headline. Flagged rather than resolved -- resolving it means opening the images,
which is a review action, not a measurement.

---

## 8b. Git tracking -- what "freed" actually means

`art_generated/` is **not** gitignored, so this needed checking before any freed-byte
figure could be read as reclaimed disk.

```
git check-ignore -q art_generated ; echo $?     -> 1  (not ignored)
git ls-files art_generated | wc -l              -> 534
```

**534 of 10,576 files are tracked, holding 93,795,744 bytes (89.5 MB) -- 1.0% of the tree.**
All 534 are images (506 `.png`, 28 `.webp`); no `.mp4`, `.mp3`, `.json` or log is tracked.
The other 10,042 files (9,531,599,416 bytes, 99.0%) are **untracked working-copy only**.

Tracked bytes by verdict bucket:

| Bucket | Tracked files | Tracked bytes | MB |
|---|---:|---:|---:|
| `keep` | 253 | 47,232,047 | 45.0 |
| `remix` | 187 | 38,733,015 | 36.9 |
| `discard` | **2** | **1,343,172** | **1.3** |
| guard-excluded (`iconset_round2` `_32`/`_48`) | 92 | 6,487,510 | 6.2 |
| undecided | 0 | 0 | 0.0 |

Two consequences that change how the rest of this document reads:

1. **The REJECTED rule is almost entirely an untracked-file operation.** Of the
   288,145,156 bytes it frees, at most 1,343,172 sit in git history -- and only some of
   that, since those 2 tracked files may be the largest-of-family the rule *retains*.
   Deleting under this rule reclaims real disk and leaves history essentially untouched.
2. **The undecided 4.2 GB has zero git coverage.** Nothing in `an0807_*` is committed.
   If that working copy is lost, the art is gone -- there is no repository backstop. That
   is a preservation question sitting underneath the retention question, and it points
   the opposite way from deletion.

---

## 9. What I could not measure

1. **The ACCEPTED rule's byte figure.** Stated in full in section 4. `art_generated`
   is not a source tree the build reads from (7-8 basename overlaps out of 2,003; the
   shipped `compute.png` is 64x64 while the generated one starts at 1024). Any per-family
   "what the game renders" number would be invented. The scenario table is offered
   instead, explicitly as scenarios.

2. **Whether a `keep` family is *intended* to ship at 1536.** The dimension histogram
   describes assets that shipped, which is a biased sample -- nothing hero-sized has
   shipped yet, so it cannot tell us whether the 112 `an0807_l3_hero_land` families need
   1536. This is a design question with no measurable answer in the repo.

3. **Pixel dimensions of 5 referenced images** (`.webp` and `.jpg`). The dimension reader
   parses the PNG IHDR header only; it reports `None` for other formats rather than
   guessing. 5 of 351 referenced images, all small.

4. **Whether the 618 guard-excluded images are recoverable.** The 64 `_32`/`_48`
   `iconset_round2` files are near-certainly real resolution variants under a different
   ladder, and the 526 `audiodump` frames are near-certainly derived from the 16 `.mp4`
   files and thus regenerable. Both are conjecture from filenames; I did not open the
   files or diff frames against video.

5. *(Originally listed as unmeasured; measured instead -- see section 8b.)*

6. **Duplicate content across families.** Byte-identical images generated twice under
   different family names would be double-counted here. No content hashing was performed
   (~9 GB of hashing was out of scope for this pass). If the `an0807_l2_a_*` sweep blocks
   share unchanged frames, real recoverable bytes could exceed these figures.

7. **The 1.17 GB of `.mp4`.** Excluded by the guard, correctly. No rule in this brief
   covers video, so its retention is entirely undecided and it is the single largest
   non-family object in the tree.

---

## 10. Options, with numbers, no recommendation

| Option | Freed bytes | Freed MB | % of tree | Preconditions |
|---|---:|---:|---:|---|
| A. REJECTED rule only (as specified) | 288,145,156 | 274.8 | 3.0% | none -- fully specified today |
| B. A + drop discard families entirely | 810,630,741 | 773.1 | 8.4% | a stronger rule than the brief states |
| C. A + cap `keep` at 512 | 2,331,439,525 | 2,223.4 | 24.2% | ACCEPTED rule must first be defined |
| D. C + review the `an0807_*` blocks, then apply both rules to the outcome | up to ~4.3 GB | -- | up to ~45% | 858 families need verdicts |
| E. Decide the 16 `.mp4` files separately | 1,222,977,929 | 1,166.3 | 12.7% | outside both rules entirely |

Option A -- the only rule specified precisely enough to execute -- recovers 3.0%. The
mass is in D and E, and both are blocked on a decision rather than on a measurement.
