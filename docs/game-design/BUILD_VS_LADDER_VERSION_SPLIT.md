# Build vs Ladder Version Split

Design/implementation spec for splitting the single game version number into two
independent concepts so cosmetic patches stop forking the leaderboard.

- **Status:** DRAFT (for Pip review; recommend promoting to ADR-0018 once ruled)
- **Drafted:** 2026-07-18 (Fable session)
- **Blocks:** the first gameplay hotpatch, and #789 hiring-stitch (which changes
  gameplay and legitimately SHOULD fork the ladder)
- **Related:** `docs/game-design/DISTRIBUTION_AND_PATCHING.md` (L3 pck patcher,
  which forces this split), `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md`
  (item #5: "Boards are keyed by `(seed, game_version)`"),
  `docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md`
  (seed schedules -- the RNG surface a ladder bump must protect)

---

## 0. TL;DR

Today one number -- the full build version string (`GameConfig.CURRENT_VERSION`,
stamped from `version.txt`) -- is glued into the leaderboard board key. So a
music-only or UI-only patch bump forks every board and scatters scores.

Split it:

- **build_version** -- the existing `version.txt` SSOT. Bumps every release/patch.
  Identifies the binary/pck. Keeps doing everything it does today EXCEPT feeding
  the board key.
- **ladder_version** (a.k.a. ruleset/epoch version) -- a new, separate,
  slow-moving integer. Bumps ONLY when gameplay/scoring/seed-affecting rules
  change. This is what the leaderboard board key uses.

Cosmetic patches keep everyone on one board; gameplay changes start a new epoch.

---

## 1. Current state -- how version binds into the board key today

### 1.1 The SSOT and its propagation

- `version.txt` (repo root) holds the single canonical string. Current value:
  `0.11.0` (`version.txt:1`).
- `tools/sync_version.py` stamps that string into every file that cannot read
  `version.txt` at runtime: `game_config.gd` `const CURRENT_VERSION`,
  `project.godot` `config/version`, `export_presets.cfg` (export paths + Windows
  metadata quad), and `welcome.tscn` label fallback (`tools/sync_version.py:13-22`,
  `TARGETS` list at `tools/sync_version.py:140-145`).
- `sync_version.py --check` writes nothing and exits 1 on any drift; it gates
  pre-commit + CI (`tools/sync_version.py:28-31`, `179-187`). The docstring is
  explicit about WHY: "the leaderboard board-key derives from the version, so a
  silent drift would fork score boards" (`tools/sync_version.py:30-31`). CLAUDE.md
  echoes this: a silent version drift "forks the leaderboard board-key -- fatal".
- Runtime copy: `const CURRENT_VERSION: String = "0.11.0"`
  (`godot/autoload/game_config.gd:61`). The comment at
  `game_config.gd:53-60` explains it is a compiled-in const (not a runtime
  `version.txt` read) precisely because "the leaderboard board-key derives from
  this value, so it must resolve identically in exported builds".

### 1.2 The exact binding (this is the thing the spec changes)

The version enters the board key at exactly one VALUE source --
`GameConfig.CURRENT_VERSION`, prefixed with `"v"` -- consumed at these call sites:

**Local board file (per-seed, per-version JSON file):**

- `godot/scripts/leaderboard.gd:80` -- field `game_version` with the comment
  "ADR-0002 #5: boards are keyed by (seed, game_version)".
- `godot/scripts/leaderboard.gd:84-93` -- `_init(p_seed, p_version)` builds the
  filename:
  ```
  file_path = "%s/leaderboard_%s__%s.json" % [leaderboard_dir, game_seed, game_version]
  ```
  (`leaderboard.gd:91`). The `__` delimiter and the "version-scope the board so
  balance patches rotate the meta" rationale are at `leaderboard.gd:87-89`.
- Constructed from `game_over_screen.gd:260`:
  `Leaderboard.new(game_seed, "v" + GameConfig.CURRENT_VERSION)`.
- The board file also serializes `"game_version": game_version` into its JSON
  payload (`leaderboard.gd:169`).

**Remote board (PHP score API, PR #680):**

- `godot/autoload/leaderboard_sync.gd:107-111` -- `build_post_body` stamps
  `body["version"] = version` into the POST.
- `godot/autoload/leaderboard_sync.gd:114-121` -- `build_get_url` puts
  `version=...` into the GET query string. So the SERVER board key is
  `(seed, version)` too.
- Submit call site: `game_over_screen.gd:280` --
  `LeaderboardSync.submit_score(entry, game_seed, "v" + GameConfig.CURRENT_VERSION)`.
- Fetch call site: `leaderboard_screen.gd:89-91` --
  `var version = "v" + GameConfig.CURRENT_VERSION` then
  `LeaderboardSync.fetch_board(board_seed, version, 100, ...)`.

**View / dropdown key (which board the screen shows):**

- `godot/scripts/ui/leaderboard_screen.gd:111-113` -- `_board_key(lb_seed, lb_version)`.
- `leaderboard_screen.gd:153` -- the "current" board to auto-select:
  `_board_key(GameConfig.get_display_seed(), "v" + GameConfig.CURRENT_VERSION)`.
- Subtitle label: `leaderboard_screen.gd:106` --
  `"Global board: %s (v%s)" % [GameConfig.get_display_seed(), GameConfig.CURRENT_VERSION]`.

**Replay/verification artifact (adjacent, carries version but is NOT the board key):**

- `godot/scripts/game_manager.gd:72,78` and `:731` --
  `VerificationTracker.start_tracking(seed, GameConfig.CURRENT_VERSION, ...)`.
- `godot/autoload/verification_tracker.gd:40,73,273,305,365,384` -- stores/emits
  `game_version`. This tags the replay with the build it was produced on; it is
  provenance, not the board scope. See Section 5.3 for the "which one goes here"
  ruling.

### 1.3 Why every patch forks the board

Because all six board-key call sites above read `CURRENT_VERSION`, and
`CURRENT_VERSION` is stamped from `version.txt`, ANY `version.txt` bump -- even a
music-only patch like the recent `aaccc6a feat(music): Fable music session 1` --
changes the `"v" + CURRENT_VERSION` component and therefore:

- writes scores to a NEW local file `leaderboard_<seed>__v0.11.1.json` while old
  scores sit in `leaderboard_<seed>__v0.11.0.json`, and
- posts/fetches a NEW remote board `(seed, v0.11.1)`.

Result: a cosmetic bump scatters testers across incompatible ladders. This is the
exact failure `DISTRIBUTION_AND_PATCHING.md:112-130` flags as blocking the first
gameplay hotpatch.

Note the design INTENT behind the current coupling (ADR-0002 #5,
`ADR-0002...md:34-36`): "Balance patches naturally rotate the meta; old scores
never lie about the current game. Score-formula changes are patch content." That
intent is CORRECT -- gameplay changes should rotate the board. The bug is only
that the trigger is "any build bump" instead of "any gameplay-rules bump". This
spec preserves the intent and narrows the trigger.

---

## 2. Proposed model -- where ladder_version lives and the binding change

### 2.1 The new value

Introduce `ladder_version`: a small monotonic integer (recommended) or a short
string, that is INDEPENDENT of `build_version`. It bumps only on
gameplay/scoring/seed rule changes (Section 3).

Integer vs semver-string tradeoff:

- **Integer (recommended, e.g. `"3"`).** Matches the manifest example already in
  `DISTRIBUTION_AND_PATCHING.md:84` (`"ladder_version": "3"`). An epoch is an
  opaque bucket; there is no meaningful "minor vs major" distinction between
  epochs -- either scores are comparable or they are not. An integer says exactly
  that and nothing more. Simplest to compare, hardest to mis-format.
- **Semver-ish string (`"2.0"`).** Tempting for human readability but invites a
  false "0.x compatible" ordering that does not exist for ladders. Rejected.

Recommendation: **integer**, rendered in keys/labels as `"L<n>"` (e.g. `"L3"`) to
be unambiguous next to the `"v0.11.0"` build string.

### 2.2 Where it is stored -- three options

**Option A -- a second line/field in `version.txt`.** e.g.
```
0.11.0
ladder=3
```
or a small JSON. Pro: one SSOT file. Con: `version.txt` is currently a bare
semver read by a strict regex (`sync_version.py:50,53-60`, `_SEMVER_RE` matches
the whole trimmed file); adding a second line forces parser changes and risks the
Windows-metadata quad logic. Medium blast radius.

**Option B -- a dedicated `ladder_version.txt` at repo root (RECOMMENDED).**
A one-line integer file, sibling to `version.txt`. Pro: zero risk to the existing
version pipeline; orthogonal file for an orthogonal concept (mirrors the doc's
framing that the ladder is "ORTHOGONAL to the two files",
`DISTRIBUTION_AND_PATCHING.md:36-39`); trivially diffable ("did this PR touch the
ladder file?" is a one-line git check that reviewers and CI can both use). Con: a
second SSOT file to remember -- mitigated by Enforcement (Section 4).

**Option C -- a GDScript const only (`game_config.gd`), no root file.** Pro:
fewest files. Con: breaks the established "root text file is SSOT, `sync_version.py`
stamps the const" pattern; the const would be hand-edited, which is exactly the
drift hazard `sync_version.py --check` exists to kill. Rejected.

Recommendation: **Option B** -- `ladder_version.txt` (root) as SSOT, stamped by an
extended `sync_version.py` into a new `game_config.gd` const `LADDER_VERSION`,
exactly mirroring how `CURRENT_VERSION` is stamped today.

### 2.3 The binding change -- route board keys through one accessor

Do NOT sprinkle `LADDER_VERSION` across the six call sites. Add ONE accessor and
point the board-key sites at it, so there is a single binding point forever:

```gdscript
# game_config.gd
const LADDER_VERSION: String = "L3"   # stamped from ladder_version.txt by sync_version.py

## The value that scopes leaderboard boards (ADR-0002 #5). This is the LADDER
## epoch, NOT the build version -- cosmetic build bumps must not fork the board.
func get_board_version() -> String:
    return LADDER_VERSION
```

Then the change is mechanical -- replace `"v" + GameConfig.CURRENT_VERSION` with
`GameConfig.get_board_version()` at exactly the board-key sites:

- `game_over_screen.gd:260` (local file) and `:280` (remote submit)
- `leaderboard_screen.gd:89` (remote fetch) and `:153` (current-board select)
- `leaderboard_screen.gd:106` subtitle: show BOTH -- board epoch AND build (see
  Section 5.4 labelling).

Leave `game_over_screen.gd:252`/`444` (share line) and the verification tracker
(`game_manager.gd:72,78,731`) on `CURRENT_VERSION` -- those want the build string
for provenance/repro, not the board scope (Section 5.3).

"The one-line change" in the strict sense: the board scope is now sourced from
`get_board_version()` returning `LADDER_VERSION` instead of `CURRENT_VERSION`.
Everything else is call-site rewiring to that accessor.

### 2.4 Server-side note

The PHP score API keys boards on the `version` query/body param
(`leaderboard_sync.gd:114-121`). Once the client sends `L3` instead of `v0.11.0`,
the server transparently buckets by the ladder value -- no server schema change
required, the `version` column just now holds `L3`. (A cosmetic column rename to
`ladder` is optional cleanup, not required for correctness.)

---

## 3. The bump rule -- when ladder_version bumps (and when it must NOT)

Principle: **the ladder version bumps if and only if two identical inputs (same
seed, same player choices) could produce a different score, a different world
trajectory, or a different RNG stream than the previous epoch.** If a patch cannot
change any score or any simulation outcome, it MUST NOT bump the ladder.

### 3.1 BUMP the ladder (gameplay/scoring/seed/RNG surface changed)

- Scoring rule changes -- anything touching ADR-0002 scoring: turn accrual, the
  `100 - doom` doom-integral tiebreak, `GameState.compare_score`, victory/loss
  thresholds.
- Balance changes that alter outcomes -- action costs/effects, doom deltas, event
  probabilities, finance/economy numbers in `godot/data/*.json`, effort economy
  (ADR-0011), cost-of-debt (ADR-0013).
- Seed schedule / wave changes -- ADR-0005 emergent waves + seed schedules;
  `seed_schedule.gd`; anything that changes which events fire on a given seed.
- RNG-affecting changes -- reordering RNG draws, changing the RNG seeding, adding
  or removing a `randi()`/`randf()` call in the sim path, changing turn order.
  (Even a "no balance change" refactor that shifts the RNG stream forks replays
  and must bump.)
- New content that changes the reachable game -- new actions/events/scenarios that
  can occur on existing seeds.
- Mortality-guarantee mechanism changes (ADR-0002 "Requirement created").

### 3.2 Do NOT bump the ladder (cosmetic / non-behavioral)

- UI layout, panels, `main_ui.gd` presentation, colors, fonts.
- Music, SFX, audio mix (e.g. the music session commits).
- Art, icons, sprites, banners.
- Copy/text, patch notes, onboarding/tutorial wording, feed-channel labels.
- Bugfixes with NO behavior change (crash fix, null guard, a fix that does not
  alter any score or trajectory on any seed).
- Tooling/CI/build/docs.

### 3.3 Author decision checklist (run per patch, before merge)

Answer these; ANY "yes" means bump `ladder_version.txt`:

1. Could this change the score of an otherwise-identical run? (score formula,
   tiebreak, thresholds)
2. Could this change what happens in the sim on a fixed seed? (balance numbers,
   event/action effects, probabilities)
3. Does this touch the seed schedule, wave generation, or event scheduling?
4. Does this add/remove/reorder any RNG draw or change turn order? (would a saved
   replay from last epoch still verify?)
5. Does this add content reachable in an existing seed's run?

If all five are "no", it is a cosmetic patch: bump `version.txt` only, leave
`ladder_version.txt` untouched, everyone stays on the same board.

Tie-break guidance for the unsure author: if a saved replay artifact from the
previous epoch would FAIL to reproduce under this patch, that is definitional
proof the ladder must bump (replays are epoch-scoped by construction).

---

## 4. Enforcement -- preventing silent drift

Mirror the existing `sync_version.py --check` discipline. Three layers:

### 4.1 Stamp + check parity (extend `sync_version.py`)

- Add `ladder_version.txt` as a new SSOT read (alongside `read_version()`).
- Add a `game_config.gd` stamper target for `const LADDER_VERSION`
  (new entry in `TARGETS`, `sync_version.py:140-145`; new regex stamper mirroring
  `_stamp_game_config`, `sync_version.py:73-78`).
- `--check` now also fails if `LADDER_VERSION` has drifted from
  `ladder_version.txt`. This reuses the existing CI/pre-commit gate wording and
  exit-1 behavior (`sync_version.py:179-187`) so the ladder gets the same
  "fatal drift" protection the build version already has.

### 4.2 A "did you mean to (not) bump the ladder?" guard (recommended)

The dangerous silent failure is not drift between two files -- it is a HUMAN
forgetting to bump the ladder on a gameplay PR, or bumping it on a cosmetic one.
A pure `--check` cannot catch that. Options, cheapest first:

- **Manifest field + reviewer checkbox (cheapest).** Every patch manifest (Section
  6) carries an explicit `ladder_forks: true|false`. PR template gets the Section
  3.3 checklist. Cheap, but trust-based.
- **CI heuristic gate (recommended).** A `tools/check_ladder_bump.py` that, on a
  PR diff, flags "gameplay-surface files changed but `ladder_version.txt` did NOT"
  as a WARNING requiring an explicit ack, and "cosmetic-only diff but
  `ladder_version.txt` DID change" as a second warning. Gameplay surface = a
  path allowlist: `godot/scripts/core/**` (game logic), `godot/data/**` (balance),
  `seed_schedule.gd`, scoring files. This is a smell detector, not a proof --
  false positives are acked, not blocked -- but it makes the omission loud.
- **Determinism test as backstop (strongest signal, already partly exists).** The
  simulation tier already has determinism/replay tests. Add one asserting that a
  checked-in "golden replay" for the CURRENT epoch still verifies; if a PR breaks
  it WITHOUT bumping `ladder_version.txt`, fail. This catches RNG-stream changes
  (checklist Q4) that a file-path heuristic would miss. Runs in the slow tier
  (non-blocking per CLAUDE.md), so treat as a nightly/pre-release gate, not the
  fast gate.

Recommendation: ship 4.1 + the CI heuristic (4.2 middle) before the first
gameplay hotpatch; add the golden-replay backstop when replay verification is
wired to CI.

### 4.3 One-time test for the split itself

Add a fast unit test asserting `GameConfig.get_board_version()` returns
`LADDER_VERSION` (not `CURRENT_VERSION`), so a future refactor cannot silently
re-couple the board key to the build string. Pair with a test that a simulated
cosmetic build bump (change `CURRENT_VERSION`, hold `LADDER_VERSION`) produces the
SAME board key.

---

## 5. Migration / epochs

### 5.1 Existing boards at introduction

Today's local files are named `leaderboard_<seed>__v0.11.0.json` and remote boards
are keyed `(seed, v0.11.0)` (or `v0.12.0` on the launch build the distribution doc
references; the `version.txt` SSOT currently reads `0.11.0`, so confirm the live
value at cutover). When `ladder_version` is introduced, new boards key on `L<n>`.
The old `v...`-keyed boards do NOT vanish -- the discovery code lists ALL board
files and shows each by its stored identity (`leaderboard_screen.gd:115-149`,
`_parse_board_identity` reads seed+version from the filename). So legacy boards
remain readable; they just stop receiving new scores.

### 5.2 Epoch boundary semantics (define once)

- An **epoch** = one value of `ladder_version`. All scores with the same
  `(seed, ladder_version)` are directly comparable; scores across different
  `ladder_version` values are NOT comparable (different rules produced them).
- Introducing the split IS itself epoch boundary 1 -> the first `L<n>`. Pick the
  starting integer deliberately: recommend seeding it so the first ladder epoch is
  a ROUND, memorable number (e.g. `L1`), and treat all pre-split `v...` boards as
  "legacy / pre-ladder epoch 0", archived read-only.
- Crossing a boundary is a one-way rotation: scores never migrate forward
  automatically (that would be a lie about the rules they were earned under).

### 5.3 Which version tags which artifact (avoid the double-binding trap)

- **Board key** -> `ladder_version` (the scope of comparison).
- **Replay/verification artifact** -> KEEP `build_version` (`CURRENT_VERSION`) via
  the verification tracker (`verification_tracker.gd:40,273,305`), AND add
  `ladder_version` alongside it. Rationale: a replay must reproduce on the EXACT
  build that made it (build string = repro identity), but it belongs to a LADDER
  epoch for ranking. Store both; they answer different questions.
- **Share line / bug report** -> `build_version` (what binary the player ran;
  `game_over_screen.gd:444`, `bug_reporter.gd:47`). Optionally append the epoch.

### 5.4 UI labelling (which epoch a score belongs to)

- The board subtitle (`leaderboard_screen.gd:106`) should read the epoch it is
  scoping by, e.g. `"Global board: <seed> (epoch L3)"`, and MAY footnote the build
  the viewer is running (`"you are on build v0.11.1"`) so a player on a cosmetic
  patch understands they are correctly on the same board as `v0.11.0` players.
- Legacy pre-split boards render with a `"legacy (pre-ladder)"` tag so nobody
  reads an old `v0.11.0` board as current.
- The dropdown `_board_key` (`leaderboard_screen.gd:111-113`) formats the epoch,
  not the build, for post-split boards.

---

## 6. Connection to patch delivery (pck manifest)

`DISTRIBUTION_AND_PATCHING.md` already anticipates this split and already put
`"ladder_version": "3"` in the L2 manifest example
(`DISTRIBUTION_AND_PATCHING.md:80-88`) and states the requirement
(`:112-130`): "A UI/art/text pck MUST NOT fork the ladder. A balance/scoring pck
MUST fork the ladder."

Wiring:

- The version manifest served from `api.pdoom1.com` carries BOTH `latest_build`
  and `ladder_version` (as already drafted). A client that mounts a downloaded
  gameplay patch pck adopts the pck's `ladder_version`; a cosmetic pck leaves it
  unchanged.
- Concretely, the patch pck should ship its OWN `ladder_version.txt` (or a small
  `patch_manifest.json` field) so that when
  `ProjectSettings.load_resource_pack("patch.pck")` overrides files
  (`DISTRIBUTION_AND_PATCHING.md:45-52`), the ladder value the game reads at
  runtime comes from the mounted patch -- a gameplay patch thus automatically
  moves the player to the new epoch, a cosmetic patch does not.
- This is why storing `ladder_version` as a file the pck can override (Section
  2.2 Option B) is better than a hardcoded server assumption: the mounted pck is
  self-describing about which epoch it belongs to.
- Keep the manifest's `ladder_forks` boolean (Section 4.2) as the authored,
  reviewed intent; the `ladder_version` value is the derived consequence. CI can
  assert they agree (a `ladder_forks: true` patch must carry a higher
  `ladder_version` than the base it patches).

---

## 7. OPEN DECISIONS (Pip to resolve)

### DECISION A -- manual bump vs derived-from-a-flag

How does `ladder_version` actually increment?

- **A1 (recommended): manual bump of `ladder_version.txt`, guarded by the CI
  heuristic (Section 4.2).** The author edits one integer when the checklist says
  so; CI warns on suspected omissions. Simple, explicit, matches the existing
  `version.txt` mental model. Risk: human forgets -> mitigated by the gameplay-
  surface heuristic + golden-replay backstop.
- **A2: derived from a per-patch `ladder_forks` flag.** The manifest declares the
  intent and a tool auto-increments the epoch. Less to remember, but adds
  machinery and a source of "the tool bumped when I didn't mean it".
- **Tradeoff:** A1 puts the human in the loop with a safety net; A2 removes a
  manual step but hides the decision inside tooling. Recommendation: **A1 now**,
  keep the manifest `ladder_forks` field so A2 can be layered later without
  rework.

### DECISION B -- in-flight / historical scores at an epoch boundary

When the ladder bumps, what happens to the previous epoch's scores?

- **B1 (recommended): show-both, archive read-only.** Old epoch boards stay
  visible, clearly tagged "legacy / epoch L<n-1>", read-only; new scores land on
  the new epoch. Zero data loss, honest about non-comparability. The current
  discovery code already lists all boards, so this is the low-effort path.
- **B2: archive/hide.** Old boards move out of the default view (still on disk).
  Cleaner UI, but hides history testers may want ("what did the pre-hiring-stitch
  board look like?").
- **B3: merge/carry-forward.** Reject -- merging scores earned under different
  rules is precisely the lie ADR-0002 #5 and Section 5.2 forbid.
- **Tradeoff:** B1 favors transparency and minimal code; B2 favors a tidy default.
  Recommendation: **B1** (show-both with a legacy tag), revisit if the dropdown
  gets cluttered.

### DECISION C -- does #789 hiring-stitch get its own epoch, or ride a batched v0.13 gameplay epoch?

#789 changes gameplay, so it MUST bump the ladder (checklist Q2/Q5). The question
is granularity:

- **C1: its own epoch bump on merge.** Cleanest attribution ("epoch L3 = hiring
  stitch"), but if several gameplay changes land in quick succession pre-launch,
  you get many short-lived epochs and fragmented boards during active development.
- **C2 (recommended): batch into one v0.13 gameplay epoch.** Hold the ladder bump
  and land #789 plus any other queued gameplay changes under a single new epoch
  cut at the v0.13 gameplay release. Fewer, more meaningful boards; testers
  accumulate scores against a stable ruleset for longer. Cosmetic patches between
  now and that cut stay on the CURRENT epoch (which is the whole point of this
  spec).
- **Tradeoff:** C1 = precise provenance, more board churn; C2 = stable boards,
  coarser attribution. During active pre-launch balancing, board stability for
  testers usually beats per-PR attribution.
- **Recommendation: C2** -- batch #789 into a single v0.13 gameplay epoch, unless
  #789 ships alone with a meaningful tester cohort already scoring, in which case
  C1 is fine. Either way, the ladder bumps for #789; the only question is whether
  it shares the bump with siblings.

---

## Appendix -- files this spec touches (implementation checklist)

- NEW `ladder_version.txt` (root) -- SSOT integer.
- `tools/sync_version.py` -- read ladder file, stamp `LADDER_VERSION`, extend
  `--check`.
- `godot/autoload/game_config.gd` -- add `const LADDER_VERSION` +
  `get_board_version()`.
- `godot/scripts/ui/game_over_screen.gd:260,280` -- board key -> `get_board_version()`.
- `godot/scripts/ui/leaderboard_screen.gd:89,106,153` -- board key/labels ->
  `get_board_version()` (subtitle shows epoch + build).
- `godot/scripts/leaderboard.gd` -- no logic change (it receives whatever version
  string the caller passes); comment update from "(seed, game_version)" to note
  the value is now the ladder epoch.
- NEW `tools/check_ladder_bump.py` (CI heuristic) + PR-template checklist.
- NEW fast test: `get_board_version()` returns ladder, and cosmetic build bump
  keeps the board key stable.
- Leave `CURRENT_VERSION` binding intact for verification tracker, share line, bug
  report (build provenance).
