# ADR-0019 -- Pull-from-demand asset pipeline: the pack is a function of declared demand

- **Status:** ACCEPTED
- **Date:** 2026-08-03
- **Summary:** The pack becomes a function of DECLARED DEMAND rather than an accumulation of past approvals: Library admission is taste-gated, but only a demand manifest pulls a size-declared derivative into godot/assets, making "packed but undemanded" unrepresentable rather than merely rejected.
- **Session:** asset-pipeline ruling, 2026-08-03 (post-mortem of the same-day promote incident)

## Context

### The failure that earned this decision (measured 2026-08-03)

Running `tools/art_review/apply_review.py promote` today copied 202 files into
`godot/assets/`, adding 228 MB and taking the directory from 46 MB to 275 MB --
a ~5x pack increase, reverted before commit. What it copied were MASTERS:
`tex_bakelite_cracked_1024.png`, `crt_frame_bezel_heavy_1536.png`. A 1024px
master backing a 64px icon is 256x the pixels the game ever draws. The promote
would also have violated `docs/art/ART_MASTERS_POLICY.md` (art over 1MB never
goes in git) roughly 200 times in one commit.

This is not a new failure; it is issue #787 recurring: ~488MB of unreferenced
hi-res icon variants once bloated the build the same way. The generator of both
incidents is the same two facts:

1. `godot/export_presets.cfg` sets `export_filter="all_resources"` in all three
   presets -- Godot packs the ENTIRE `godot/` tree. Nothing is excluded by
   reference. Whatever lands under `godot/` ships.
2. The pipeline is push-and-copy: approval upstream (a review verdict, a
   category map) directly produces files under `godot/`, with no step that asks
   whether the game will ever draw them.

Measured today: `godot/assets` is 47 MB of a 59 MB pack -- assets are ~80% of
the player's download. And the review-verdict store held 1,021 verdicts
(807 keep / 214 iterate) of which only 202 could actually move, because the
hand-maintained category->destination map had fallen behind and pixellab paths
did not resolve. The tool reported a confident keep=807 while 75% of it could
not move -- the same silent-wrongness shape as the hollow CI gate (ADR-0017):
a confident signal uncorrelated with reality.

### The four states

Three states are intended:

| State | Where | Admitted by |
|---|---|---|
| Generated | `art_generated/` (gitignored) | the pipeline ran |
| Library | `art_source/` (<=1MB, in git) + masters archive per ART_MASTERS_POLICY | **Pip's taste.** No justification needed |
| Packed | `godot/assets/` | **declared demand** |

The fourth state was discovered by measurement today: **packed-but-undemanded**
-- bytes in the pack that no game mechanic will ever instantiate. The current
architecture admits this state freely (both #787 and today's promote landed the
tree in it), and every guard we have is downstream of it already existing.

A second distinction rides on the table: **Library holds MASTERS; Packed holds
GAME-READY DERIVATIVES.** A master crossing into `godot/` unchanged is itself a
defect, independent of whether it is demanded.

### The ruling

Pip, 2026-08-03 (verbatim): *"no asset can get generated and promoted INTO the
game's library by a mechanism which won't allow receipt of an asset into the
game's library without something like a mechanically verified reason for it to
be instantiated in the game at least once... 'Pip wants an image' might arrive
in his brain, or I might come up with things spontaneously that are cool, and
say 'yes promote these to Library status' and they can be like that. But then to
get them INSIDE A SPACE IN THE GAME there has to be a GAME MECHANICS element
that says 'at this point I want to instantiate e.g. [pot plant] and therefore I
need [pot plant large 1] and [pot plant large 2]', the game registers a LACK of
[pot plant large 2], and then there is a mechanism by which it is selected from
Library and pulled into where it is meant to be for the build."*

## Decision

**The pack is a FUNCTION of declared demand, not an accumulation of past
approvals.** Assets flow pull-from-demand:

1. **Library admission stays taste-gated.** Anything Pip likes enters the
   Library with no justification. The Library may grow without bound; it is
   outside `godot/` and (above 1MB) outside git, so its growth costs nothing
   in the pack.

2. **Pack admission is demand-gated, structurally.** A DEMAND MANIFEST declares
   what the game instantiates. The only path into `godot/assets/` is the pull
   step, which reads the manifest, selects from the Library, and renders a
   derivative into place. "Packed but undemanded" is thereby UNREPRESENTABLE,
   not merely rejected -- there is no promote-without-demand path to misuse.
   This is the same shape as `GameConfig.is_ranked_run()`
   (`godot/autoload/game_config.gd:597`) and the #1058 difficulty lock: the
   rule lives in the only path that exists, not in a checker bolted alongside.
   (That function's own comment names the failure mode of the alternative: a
   second write site "that forgets this check silently reopens the hole.")

3. **Demand is declared as POOLS, not file lists.** The dynamic loaders read
   directories and construct paths at runtime -- `portrait_library.gd:40`
   builds `"%s%s_%d.png" % [PORTRAIT_DIR, stem, PORTRAIT_SIZE]`;
   `worker_variant_pool.gd:89` loads whatever variants its data names. A
   file-list manifest would re-invent exactly the blindness that makes static
   scanning unusable (see Rejected alternatives). A demand entry therefore
   reads like: "office props: >=2 large pot plants at 96px" or ">=6 researcher
   portraits at 128px" -- a pool, a floor, a size.

4. **Demand declares the SIZE the game instantiates at.** The pull step renders
   a game-ready derivative (resize/compress/format) from the Library master.
   Promotion is a TRANSFORM, never a copy. The master never enters `godot/`,
   so the 1024px-master-behind-a-64px-icon failure and the ART_MASTERS_POLICY
   violation are both impossible by construction, not by vigilance.

5. **Unmet demand is a GENERATION REQUEST, surfaced loudly and forward --
   never a placeholder texture.** When the manifest demands what the Library
   cannot supply, the gap is reported where it is actionable (the audit output,
   the build log, a filed request for the generation pipeline), not papered
   over in the render. Issue #796 (the magenta cat) is the anti-pattern: a
   deliberate placeholder that shipped because absence was represented as a
   texture instead of as work. This clause also closes issue #1092 (events
   name physical things the office never shows -- install a security system,
   no cameras appear) by construction: the event's demand entry for cameras is
   unmet, and the gap is on a list someone reads, rather than waiting for a
   player to notice.

6. **A two-direction audit backstops the structure.** It reports BOTH
   packed-but-undemanded (bytes in `godot/assets/` no manifest entry accounts
   for) and demanded-but-missing (manifest entries the pack does not satisfy),
   and FAILS the build when unaccounted bytes exceed a budget. It NEVER
   deletes. The audit is a drift detector for the transition period and for
   anything that bypasses the pull path (hand-added files, merge accidents);
   the pull path itself is the enforcement.

### What is NOT decided here

- The manifest's file format and location (it must be diffable and reviewable;
  whether it lives under `godot/data/` so the game itself can read pool floors
  at runtime, or build-side only, is open).
- The unaccounted-bytes budget number for the audit gate.
- The derivative-rendering toolchain (what performs resize/compress/format).
- Whether the audit runs pre-commit, CI, or both.
- Whether the Library grows a curated store beyond `art_source/` + the masters
  archive, and what its index looks like.
- The concrete surfacing mechanism for generation requests (audit section,
  auto-filed issue, or runsheet line).

## Beacons served / violated

- **Rams #6 (honest):** the pack stops lying about what the game uses. Today a
  59 MB download asserts, implicitly, that the game needs 59 MB; measurement
  says a large fraction is undemanded. Under this ADR the pack's contents ARE
  the demand declaration, and the audit reports both directions instead of a
  confident keep-count 75% of which cannot move.
- **Rams #10 (as little design as possible):** the pack becomes derived state
  with a single generator, replacing an accumulation that needs periodic
  archaeology (#787 was a dig; today would have been another). Nothing is
  designed twice: the demand entry is written once and drives selection,
  sizing, and audit.
- Cost: friction, on purpose. "I generated something cool" no longer puts
  anything in the game -- Library, yes; pack, no. Every in-game appearance now
  requires a demand entry first, which is one more step on the happy path of
  shipping art, and the transform step needs real tooling before the manual
  copy workflow can be retired.

## Interaction contract

- **Reads:** `godot/export_presets.cfg` (`export_filter="all_resources"`, the
  fact that makes packing unconditional); the eight runtime-constructed-path
  load sites (`scripts/ui/action_bar_renderer.gd:334`,
  `scripts/ui/fanfare_popup.gd:133`, `scripts/ui/office_cat.gd:75`,
  `scripts/ui/office_floor/office_floor.gd:700`,
  `scripts/ui/office_floor/worker_variant_pool.gd:89`,
  `scripts/ui/portrait_library.gd:40`, `scripts/ui/resource_bar.gd:33`,
  `scripts/ui/office_floor/office_sandbox.gd:1691` -- the evidence that demand
  must be pools); `docs/art/ART_MASTERS_POLICY.md`;
  `tools/art_review/apply_review.py` and its verdict store; ADR-0017 (the
  silent-wrongness precedent); ADR-0018 (the office render surface where #1092
  demand originates).
- **Writes:** constrains all future writes to `godot/assets/**` (pull step
  only), retires `apply_review.py promote`'s copy-into-godot behavior in favor
  of the transform, and adds two new artifacts: the demand manifest and the
  two-direction audit tool. No engine code changes in this ADR.

## Rejected alternatives

- **Stage-outside-godot alone.** Rejected because it is ALREADY the
  architecture -- `art_source/` sits outside `godot/`, the masters archive sits
  outside git -- and it did not prevent today's incident. Staging guards
  against UNREVIEWED assets entering the tree; it says nothing about
  UNREFERENCED ones. #787 and today both happened with staging in place,
  because the promote step is a doorway through the wall, and the doorway had
  no demand check.
- **Strip-at-build (auto-remove unreferenced assets, driven by static
  analysis).** Rejected on measured evidence: eight sites load assets by
  runtime-constructed path (list above). Static analysis cannot see those
  references, so an auto-stripper would delete assets the game loads
  dynamically -- and the failure would appear on a PLAYER'S machine as a
  missing texture, in a build that passed every check. That is issue #796's
  magenta cat shipped deliberately, as policy. Auto-stripping is ruled OUT,
  permanently, not deferred; the audit may report, never delete.
- **A file-list manifest (enumerate exact paths instead of pools).** Rejected:
  the loaders that defeat static scanning read directories and construct
  filenames (`portrait_library.gd` bakes the size into the name it builds). A
  file list is a static scan written by hand -- same blindness, more toil.
  Pools-with-floors-and-sizes match what the code actually consumes.
- **A lint/checker that rejects undemanded files at commit time, keeping the
  copy-based promote.** Rejected: a checker alongside the path is the pattern
  `is_ranked_run()`'s comment warns about -- a second site that forgets the
  check silently reopens the hole. The 1,021-verdict/202-movable gap shows
  hand-maintained side-maps rot quietly. The rule must live IN the only path;
  the audit exists as a backstop, not as the mechanism.
- **Placeholder textures for unmet demand.** Rejected: #796 demonstrated that a
  placeholder converts a loud, actionable gap into shipped visual debt. Absence
  must be represented as work-to-do where it is actionable, not as a texture.
- **Accept the bloat / raise the size cap.** Rejected by arithmetic: assets are
  already ~80% of a 59 MB download, today's single promote would have made the
  pack ~275 MB, and the Library is designed to keep growing. Any cap becomes a
  fight the Library wins.

## Consequences / open questions

- **Migration path -- first increment is deliberately small.** Hand-write the
  demand manifest for what the game loads today, and build the two-direction
  audit against it. NO file moves in this increment. It is independently
  valuable on day one: it yields the MB number (how much of the 47 MB is
  undemanded) and the gap list (what #1092-class demand is unmet) immediately,
  before any tooling risk is taken. Transform-based promotion and retiring the
  copy path come after the manifest has proven its shape.
- **The category->destination map dies.** Under pull-from-demand, destination
  is derived from the demand entry (pool -> directory, size -> filename), so
  the hand-maintained map that silently stranded 75% of verdicts has no
  successor to rot.
- **The review pipeline upstream is untouched.** Verdicts still gate Library
  admission (taste); this ADR only severs the verdict -> pack link. The 807
  keeps remain Library candidates; none of them implies packing.
- **Existing packed assets are grandfathered until audited, not purged.**
  RULED by Pip, 2026-08-03, when this was raised as the one assumption the ADR
  had made without a ruling: "Yes things are grandfathered". The audit's
  packed-but-undemanded report is the worklist; removal happens as deliberate,
  reviewed deletions (the #787 precedent: archaeology, then intentional
  removal), never automatically.

  This matters more than it reads. It decides whether the audit's FIRST RUN is
  a report or a crisis. `godot/assets` is 47 MB today and predates any manifest,
  so on day one essentially all of it will be undemanded -- not because it is
  unused, but because nothing has declared it yet. Without grandfathering, the
  audit would open by failing the build over the entire existing pack, and the
  rational response would be to raise the budget until it passed, which is how
  a gate becomes decoration. Grandfathered, the same number is a backlog with a
  size attached.
- **Risk, stated with odds:** the manifest itself can rot like any
  hand-maintained index (the stale `decisions/README.md` failure mode). Two
  mitigations are structural -- the audit fails the build when manifest and
  pack disagree in either direction, and pools (not file lists) mean routine
  asset additions inside an existing pool need no manifest edit. Residual
  probability that manifest rot still causes at least one shipped gap in the
  first six months: ~20%; without the two-direction audit it would be
  near-certain, which is why the audit ships in increment one.
- Open: whether pool floors ever become runtime-readable (the game itself
  asserting "this pool is under floor" at boot, extending ADR-0017's
  nothing-hollow-at-load-time smoke into asset space). Attractive, undecided.
- Open: interaction with the export presets -- once the pull path is the only
  writer of `godot/assets/`, `export_filter="all_resources"` becomes harmless
  for assets, but the broader Godot-packs-everything trap (CLAUDE.md) still
  governs non-asset files under `godot/`; this ADR does not touch that.
