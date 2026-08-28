# Release notes guard

`scripts/check_release_notes.py`, issue #1165.

## Why this exists

v0.13.2's published release body announced the Research Quality System as
delivered. `#500` was open then and is open now. The same body announced the
scenario/mod hook system 7.5 months after that work closed. pdoom1.com's
`/game-changelog/` renders release bodies live from the GitHub releases API, so
a false sentence reached readers with no human in between. Found by the
`pdoom1-website` seat on 2026-08-07 (`coordination#35`).

Two mechanisms produced it, both verified:

1. `CHANGELOG.md` carried **six** `## [Unreleased]` headings, three of them
   dated 2025-09. At least five past releases failed to clear the accumulator
   and nobody noticed, because the failure is silent and the output is
   plausible.
2. Misfiled sections. The `[0.13.2]` section carried `#500`/`#483` content that
   merged in `v0.11.0..v0.12.0` (`30f3c6d5`, `6eb20174`). Relocated to a
   reconstructed `[0.12.0]` on 2026-08-08.

## The propagation path -- established, not assumed

The path is narrower than it looks. Two extractors exist and only one of them
builds the thing players read:

| Where | Code | What it feeds |
| --- | --- | --- |
| `.github/workflows/enhanced-release.yml`, `create-github-release` job, step "Extract changelog" | `sed -n "/\[$VERSION_NUM\]/,/^## /p" CHANGELOG.md \| head -n -1 > release_notes.txt` | `release_notes.txt` -> `softprops/action-gh-release` `body_path` -> **the published release body** -> releases API -> `pdoom1.com/game-changelog/` |
| `scripts/generate_release_metadata.py`, `extract_changelog_for_version()` | anchors on `## [<version>]`, breaks at the next `## ` | `public/releases/*.json` feed, `scripts/generate_release_manifest.py` `highlights` field |

Consequences worth stating plainly:

- **A pre-commit hook on `CHANGELOG.md` could not have caught v0.13.2.** The
  body is assembled at release time from whatever the file says then.
- `extract_changelog_for_version()` matches only `## [<version>]` and breaks at
  the next `## `, so a misfiled `[0.13.2]` section could **not** leak into a
  `0.14.1` manifest. Cross-version leakage through the manifest was a decoy.
- The workflow's `sed`, by contrast, has a start pattern that is **not anchored
  to a heading**: `/\[0.13.2\]/` matches the string anywhere, including in
  prose. The guard sidesteps this entirely by checking `release_notes.txt`
  itself rather than re-deriving the section -- it checks the bytes that get
  published, whatever produced them.

## Where the checks run

| Gate | Runs | Checks | Blocking |
| --- | --- | --- | --- |
| pre-commit `changelog-structure-check` | on `CHANGELOG.md` commits | RN001, RN002. Offline. | yes (RN001) |
| `quality-checks.yml` | on every PR to main, and on push to main | RN001, RN002 + RN003/RN005 on the `version.txt` section | yes |
| `pre-release-checks.yml` | on `v*.*.*` tag push | RN001, RN002 + RN003/RN004 on the CHANGELOG section | yes |
| `enhanced-release.yml`, before `action-gh-release` | on `v*.*.*` tag push | RN003, RN004 on `release_notes.txt` | **yes -- this is the one that stops a bad body being published** |

### The PR-time row was added on 2026-08-29, and here is what it cost to learn

v0.14.4 was tagged on 2026-08-28 and then sat unpublished. RN003 failed on the
tag, in both release workflows, because the `[0.14.4]` bullet cited `#1071`
while `#1071` was open. The gate was right. What was wrong was **when it could
first speak**:

- pre-commit runs `--changelog-structure`, which is RN001/RN002 **only**;
- RN003 has to ask GitHub for issue state, and pre-commit is offline by design
  (`--offline` exists precisely to skip RN003/RN004);
- both workflows that did run RN003 triggered on `push: tags: v*.*.*`.

So between writing the bullet and cutting the tag there was **no moment at
which this repo could tell you the citation was wrong**. The first feedback
arrived after the tag existed, which means every mistake of this class
necessarily cost a tag rewrite. That is a gap in the *schedule* of the checks,
not a lapse by whoever wrote the bullet.

Both halves are demonstrable on the pre-fix text, and the pair is the point:

```
$ git show 9f7a3c78:CHANGELOG.md > OLD.md
$ sed -n "/\[0.14.4\]/,/^## /p" OLD.md | head -n -1 > old_body.txt

$ python scripts/check_release_notes.py --body old_body.txt --offline
[OK] release notes check passed (0 warning(s))          <-- the pre-commit shape

$ python scripts/check_release_notes.py --body old_body.txt
[FAIL] RN003: cites #1071 but that issue is OPEN        <-- the same text, online
```

The offline mode reports **OK on the exact text that stopped the release**. It
is not broken -- it is answering a smaller question, correctly -- but it is why
"the hook passed" was never evidence here.

The tag-time gates stay. They check the exact bytes about to be published,
which is a different and stronger question than checking the file. The PR-time
row is the same question asked early enough to be fixed without moving a tag.

## What is checked mechanically

| ID | Rule | Severity |
| --- | --- | --- |
| RN001 | more than one `## [Unreleased]` heading | fatal |
| RN002 | the same version heading appearing twice | warn |
| RN003 | a cited issue/PR whose state is OPEN | fatal |
| RN004 | a cited issue/PR that no commit in `<prev tag>..<tag>` mentions | fatal |
| RN005 | a bullet saying `#N is still OPEN` about an issue that has CLOSED | fatal |

RN005 is the disclosure escape checked in the other direction, added 2026-08-09
and taken from the non-overlapping half of #1187, whose author identified it.
Without it the escape rots into decoration: a marker written truthfully in
August is a false claim to a player in September, in the same file and on the
same page, and RN003 -- the only reason the wording exists -- would never look
at it. It became load-bearing immediately, because the `[0.14.0]` correction
added fourteen such markers in one edit.

RN002 is a warning because `CHANGELOG.md` carries a genuine historical
duplicate (`[0.7.4]`, twice on 2025-09-16) that predates the guard. Making it
fatal would have meant rewriting history to land the guard.

RN003 resolves state through one batched `gh api graphql` call per 50 numbers,
using `issueOrPullRequest` rather than `gh issue view`, because the changelog
mixes issue and PR references and `gh issue view` on a PR number is a
coincidence, not a lookup. An unresolvable number is reported as a warning --
never silently treated as a pass.

## What is NOT checked -- still a human's job

Be clear about this, because "every bullet ties to a merged commit" was enforced
by hand on 2026-08-08, twice, at real cost, and the guard replaces only part of
that labour.

- **Prose accuracy.** `#1173` being closed and in range says the work happened.
  It says nothing about whether "it opens on global now" is true. Only running
  the build settles that.
- **Uncited bullets.** RN003 and RN004 bind to `#N`. A bullet that cites nothing
  passes silently. The mitigation is a convention, not a check: cite the issue.
- **Correct version filing.** RN004 is a **lower bound, not a proof**. Run
  against v0.13.2 it caught the misfiled `#500` and did **not** catch the
  misfiled `#483`, because an unrelated commit in that range
  (`fix(league): scenario runs are UNRANKED ... (#1060)`) happened to mention
  `#483` in its body. A coincidental mention satisfies the tie.
- **Scope creep inside a bullet.** A bullet may cite a closed, in-range issue
  and then describe more than that issue delivered.

## The disclosure escape

Describing shipped code that belongs to an unfinished feature is legitimate.
Announcing that feature as delivered is not. So RN003 permits a citation of an
OPEN issue when the same bullet says so in exactly these words:

```
#500 is still OPEN
```

Markdown emphasis is stripped and whitespace collapsed before matching (the
existing disclosure in `[0.12.0]` is bold and line-wrapped), but the wording
itself must be exact. The escape is scoped to the bullet making the claim, so
one disclosed bullet cannot launder its neighbours.

## Proving it fails

A guard that has never been shown to fail is not evidence.

```
$ python scripts/check_release_notes.py --release v0.13.2
[FAIL] RN003: published release v0.13.2: cites #791 but that issue is OPEN
[FAIL] RN003: published release v0.13.2: cites #811 but that issue is OPEN
[FAIL] RN003: published release v0.13.2: cites #500 but that issue is OPEN
[FAIL] RN003: published release v0.13.2: cites #500 but that issue is OPEN
[FAIL] RN004: published release v0.13.2: cites #500, which no commit in v0.13.1..v0.13.2 mentions
...
RELEASE NOTES CHECK FAILED: 8 fatal, 0 warning

$ python scripts/check_release_notes.py --release v0.14.1
[OK] release notes check passed (0 warning(s))
```

`tests/test_release_notes_guard.py` pins both directions offline, with issue
states stubbed to their real values.

## Outstanding

The **published v0.13.2 release body is still wrong** and is still being served
by `pdoom1.com/game-changelog/`. Correcting a published body is Pip's call;
`pdoom1-website` has asked him. This guard prevents the next one, it does not
repair that one.
