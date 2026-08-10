# [Gate 6: BOARD OPENS]

**When:** Friday evening. Legacy: G5.

The league is live, the announcement is posted, and the hotpatch window is
armed.

---

## Entry criteria

- [Gate 5: SEED BLESSING] PASSED, seed spoken, ladder stamped.
- The tag is pushed and the release assets are uploaded. This is the first
  moment in the week when that is true, which is why this gate now owns the
  release-URL check.
- The site news stub was pre-staged (Wednesday) and only needs the numbers.

## Mechanical checks

```
gh release view v<X.Y.Z> --json tagName,assets,url
python scripts/generate_release_metadata.py --version v<X.Y.Z> --verify
python scripts/verify_release_urls.py --file public/releases/v<X.Y.Z>.json
python scripts/verify_release_urls.py --sweep public/releases/releases.json
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | Every advertised download URL answers 200 | mechanical (`--file`, blocking) | yes |
| 2 | The release feed's "latest" is actually this release | mechanical (`--sweep`) | yes |
| 3 | The release body does not teach a dead keybind | judgement over a grep | yes |
| 4 | A real run reaches the live board | mechanical, end to end | yes |
| 5 | Announcement posted, carrying seed and ladder | mechanical | yes |
| 6 | Hotpatch watch window armed (Sat AM) | declaration | yes |

Check 1 is the #998 fail-loud check, moved here from [Gate 4] because at
[Gate 4] time the tag does not exist and the check can only be run against
the previous release -- proving nothing while looking green. `--file` is
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
> One run has travelled the whole way and arrived. The board is open. Doom
> is patient. Play."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "Every advertised door answers" | check 1 -- `verify_release_urls.py --file` | mechanical |
| "The feed names this build and no other" | check 2 -- `--sweep` | mechanical |
| "One run has travelled the whole way and arrived" | check 4 | mechanical, end to end |
| "The board is open." | the act of opening | speech act |
| "Doom is patient. Play." | nothing, and correctly nothing | the payload |

Changed: three verifiable clauses added in front. Playbook v0's [Gate 6]
had checks with no corresponding words -- the announcement and the URL
sweep were listed but never spoken -- which is the inverse of [Gate 5]'s
problem and just as bad: a check nobody says is a check nobody misses when
it is skipped.

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
