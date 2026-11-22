# pdoom-data contract -- pointer, not a copy

The full brief lives in the repo that owns it. Read it there:

- Integration brief (10 sections, the argument):
  `D:\Local_Code\pdoom-data\docs\PDOOM1_INTEGRATION_BRIEF.md`
- Full consumer contract (field-by-field):
  `D:\Local_Code\pdoom-data\docs\CONSUMER_GUIDE.md`

Both are on pdoom-data `main`. The additive candidate feed they describe
(3,434 records covering 2023-2026) merged as `5ab4579b94cd` on 2026-07-26.

**Why this file is a pointer.** A 148-line copy of that brief sat here
untracked from 2026-07-25 to 2026-08-21 and already contained one struck-through
paragraph that had gone stale within five days of being written. Copied
cross-repo docs drift silently; the same failure mode is why
`decisions/README.md` is stale and why `DQ_INDEX.md` is generated. Keep the
argument in one repo and the pointer in the other.

## What a pdoom1 agent needs to know without opening the other repo

- **`all_events.json` is unchanged.** The candidate feed is additive and lives
  at `data/serveable/api/candidates/all_candidates.jsonl`.
- **Nothing in the candidate feed is human-reviewed.** Do not ship it to
  players as-is.
- **Two temporal gates, not one.** Fact visibility (`published_at <=
  game_date`) is a different test from dataset unlock (`source_available_at <=
  game_date`). Merging them hides every pre-2024 model from every pre-2024
  player.
- **Do not use the old A/B/C/D tier field for importance.** It scores
  provenance and length, which is why `hist_arxiv` floods the feed (#630). Use
  `salience_tier_by_profile` / `salience_by_profile` instead.
- **Honour tombstones (non-optional).** If pdoom1 vendors a record that later
  appears in `pdoom-data/data/raw/_tombstones/`, delete it. Those are records
  removed for privacy reasons -- memorials, harassment reports and health
  disclosures about real people. 23 were flagged at the time of writing,
  including one that scored top-ten by salience.
- **Pin what you vendor.** Fetch at build, record the tag or commit, do not
  track a moving target mid-sprint.

## The open decisions are pdoom1's, and pdoom-data is deliberately not making them

Section 9 of the upstream brief lists six forks -- the dataset-unlock gate as a
visible mechanic, the salience threshold that fixes the feed flood, whether to
inherit review verdicts, whether the MIT AIRR taxonomy is player-visible, what
happens to the 1,166 arXiv records in `all_events.json`, and which pdoom1
resource variables an export profile should map. They are tracked on the pdoom1
side in **#1102** (what does pdoom1 actually want from pdoom-data). Related:
**#1052** (ADR-0015 / DQ-21, what a pdoom-data event should carry), **#1151**
(measured defects in the ingest path), **#1115** (no working re-sync path).
