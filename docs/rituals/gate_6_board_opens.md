# [Gate 6: BOARD OPENS]

**When:** Friday evening. Legacy: G5. Number unchanged by the 2026-10-26
reorder (#1025); its entry gate is now [Gate 5: PROVEN BUILD].

The league is live, the announcement is posted, and the hotpatch window is
armed.

---

## Entry criteria

- [Gate 5: PROVEN BUILD] PASSED on the cut that is actually going out, with
  its cut number recorded. the seed and ladder blessed at
  [Gate 3: SEED BLESSING] are inside it ([Gate 5] check 9).
- Pip has pushed the tag from `release/v0.X` and the release assets are
  uploaded. This is the first
  moment in the week when that is true, which is why this gate now owns the
  release-URL check.
- The site news stub was pre-staged (Wednesday) and only needs the numbers.

## Mechanical checks

```
gh release view v<X.Y.Z> --json tagName,assets,url
python scripts/generate_release_metadata.py --version v<X.Y.Z> --verify
python scripts/verify_release_urls.py --file public/releases/v<X.Y.Z>.json
python scripts/verify_release_urls.py --sweep public/releases/releases.json
gh run list --workflow enhanced-release.yml --limit 3   # the tag's release run
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | Every advertised download URL answers 200 | mechanical (`--file`, blocking) | yes |
| 2 | The release feed's "latest" is actually this release | mechanical (`--sweep`) | yes |
| 3 | The release body does not teach a dead keybind | judgement over a grep | yes |
| 4 | A real run reaches the live board | mechanical, end to end | yes |
| 5 | Announcement posted, carrying seed and ladder | mechanical | yes |
| 6 | Hotpatch watch window armed (Sat AM) | declaration | yes |
| 7 | The website serves a board for `(seed, L<N>)` and it is empty (before check 4's run) | mechanical but **NOT from this repo** | attestation -- see below |
| 8 | Tag pushed, release workflow green (preflight, build, publish) | mechanical | yes |

Checks 7 and 8 moved here from [Gate 3: SEED BLESSING] on 2026-10-26 (they
were its checks 7 and 6). Once the seed is blessed before the freeze, neither
is runnable there: no tag or workflow exists, and "the board is empty" is a
claim about the moment it opens -- the [Gate 5] proving playtest now runs on
the league seed and can land on it in between. Take check 7 BEFORE check 4,
which puts a run on the board on purpose.

Check 1 is the #998 fail-loud check, moved here from [Gate 5: PROVEN BUILD]
(numbered Gate 4 then) because at that gate the tag does not exist and the
check can only be run against the previous release -- proving nothing while
looking green. `--file` is
blocking and exits non-zero on any non-200.

Check 2 exists because the release feed called v0.9.0 "latest" from
November onward (#1008): a one-line string sort, `"v0.9.0" > "v0.13.1"`
because `9 > 1`. Nobody looked, because it was valid-looking JSON. The
`--sweep` mode checks the Releases API rather than the tag page on purpose
-- a bare git tag with no Release object still 200s its tag page, which is
exactly how that rot went unnoticed.

Check 3 is this week's specific scar and generalises: the v0.13.1 release
body still says F8 for bug reports, and the website republishes it
verbatim. #1039 fixed the settings menu and the HOW-TO-RUN files, not the
published body. **Anywhere a string is republished by someone else is a
place a fix does not reach.** Grep the body for keybind claims and check
them against `keybind_manager.gd`, which is the authority.

Check 4 is the only check in the ceremony that exercises the whole chain --
client, board key, network, backend, board. Nothing else does. One run,
short, submitted deliberately; then look for it on the board.

## The incantation

> *"Every advertised door answers. The feed names this build and no other.
> The board was attested empty by <NAME> at <TIME>. One run has travelled the
> whole way and arrived. The board is open. Doom
> is patient. Play."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "Every advertised door answers" | check 1 -- `verify_release_urls.py --file` | mechanical |
| "The feed names this build and no other" | check 2 -- `--sweep` | mechanical |
| "The board was attested empty by <NAME> at <TIME>" | check 7 -- somebody else's observation, named | **attestation, not verification** |
| "One run has travelled the whole way and arrived" | check 4 | mechanical, end to end |
| "The board is open." | the act of opening | speech act |
| "Doom is patient. Play." | nothing, and correctly nothing | the payload |

Changed 2026-10-26: the attestation clause moved here from
[Gate 3: SEED BLESSING] with its check (it read *"The board itself is
attested by <NAME> at <TIME>"* there).

Changed 2026-07-31: three verifiable clauses added in front. Playbook v0's
[Gate 6] had checks with no corresponding words -- the announcement and the
URL sweep were listed but never spoken -- which is the inverse of
[Gate 3: SEED BLESSING]'s problem and just as bad: a check nobody says is a
check nobody misses when it is skipped.

Left alone, and it must stay exactly this: *"The board is open. Doom is
patient. Play."* It is the only line in the ceremony aimed at players
rather than at the Commissioner, and its brevity is the whole effect.
Nothing verifiable belongs in it.

The house register applies to the added lines: "Every advertised door
answers" is deadpan-bureaucratic and maps to one exact command. That is the
target -- ceremonial surface, mechanical spine.

## When a line is FALSE

- **A download URL 404s.** Do not open. This is the failure the check was
  built for (#963): README once advertised a URL that never existed, and it
  looked like a working link. Fix the asset or the generated JSON, re-run
  `--file`, then open. Opening a league whose download is a 404 wastes
  every player who tries.
- **The feed names the wrong build.** Not a stop for the board, but fix it
  before announcing -- the announcement points at the feed. Regenerate with
  `generate_release_metadata.py --version v<X.Y.Z> --verify`; do not
  hand-edit the JSON. The generated-not-hand-maintained pattern is the
  actual lesson of #1008.
- **The release body teaches a dead key.** Edit the release body. It is
  editable after the fact and it is republished verbatim by the website, so
  leaving it is a choice to keep misinforming every downloader.
- **The test run does not reach the board.** Hard stop. Something between
  the client and the backend is broken and no player run will land either.
  This is the check most likely to fail on an evening where the website
  side has been in flux, and the one whose failure is most invisible
  without it: an empty board on league night looks like nobody played.
  Related and worth knowing: until #1051, a player who stopped playing had
  no exit but alt-F4, submitted nothing, and left no trace -- *"I as dev
  don't see the player quitting, just the ones that finish the game."*
- **The website has no board, or a dirty one (check 7).** Hold the opening.
  A live board cannot be tidied after the fact -- *"filtering standings is
  editing them"* -- so an already-dirty board is a decision for the
  Commissioner, not a cleanup task. If proving runs from [Gate 5] are what
  dirtied it, that is the cost the reorder carries; record it.
- **Release workflow red (check 8).** Do not announce. The preflight is a
  blocking gate (`RELEASING.md`): red means nothing published, so check 1
  will fail too. Fix the cause and let Pip re-tag; never hand-upload around
  it.
- **Announcement blocked** (site down, no time). The board can be open
  without an announcement; say so, and post when able. Do not delay the
  board for prose. Devblog length and polish are on the sacrificial list;
  a short honest post beats a late shiny one.

## After the gate

- Arm the Saturday-morning hotpatch window (`ship:hotpatch-48h`
  discipline). A forking change is not a hotpatch no matter how urgent --
  urgency and forking are independent axes.
- **Fire the freshness drill, once per release cycle.** Dispatch
  `Live site release freshness` with `force_alarm: true`
  (`gh workflow run live-site-release-freshness.yml -f force_alarm=true`),
  confirm a `[DRILL]` issue appears, then close it. The run goes RED on
  purpose -- red is how the alarm reaches anyone, so a drill that stayed
  green would be exercising a different path. A green drill run means
  pdoom1.com was unreachable and the drill proved nothing; re-run it.
  **A drill that has never been run is the same as a guard that has never
  failed.** That workflow's comparison was proven red before it shipped
  (#1182); its issue-filing half had never executed once, which is a
  distinction nothing in the Actions list makes visible.
- Watch the probe cadence. Six hours is too slow for a live league evening
  (noted 2026-07-30); if a board or a door dies at 1900 you want to know by
  1930, not by breakfast.
- Fill the retro slot Saturday or Monday: which gate was theatre, which
  caught something real, and which lines felt wrong in the mouth. Amendments
  go to the Council per #1025.

## Not verifiable from here

- **That the website publishes a board for `(SEED, L<N>)`, that it is
  empty, and that it accepts posts (check 7).** Owner: the website side.
  Required form: a named person, a timestamp, and what they actually looked
  at -- not "it's fine". The incantation carries the name because an
  unattributed attestation is indistinguishable from an assumption.
- **Board rendering, sorting and de-duplication on the website.** Owner:
  the website side. Check 4 proves a run arrives; it does not prove the
  board displays it correctly.
- **That the board stays healthy after the gate.** Nothing in the ceremony
  covers the live window. That is the probe's job, and the probe is
  currently too slow.
- **Player-side download and launch on machines that are not the
  Commissioner's** -- notably macOS, where Sequoia removed
  right-click-to-Open and every guide on the internet still gives that
  instruction. Owner: the platform notes, and whoever answers the first
  confused message.
