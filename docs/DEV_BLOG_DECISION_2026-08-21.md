# Dev blog -- the decision Pip has to make, and why the CI failure is a red herring

Written 2026-08-21 for Pip. **One decision is needed; everything else follows
from it.** Measured, not remembered -- every number below has a command.

---

## The thing that looks like the problem, and is not

`Sync Dev Blog to Website` has been failing. It failed 8 hours ago, 29 days ago,
and four times 10 months ago.

**It is not a regression. It has never passed.** The validator rejects 16 entries:

    2025-09-17-rng-deterministic-migration.md: Title exceeds 60 character limit
    2025-09-14-action-rules-type-annotation.md: Title exceeds 60 character limit
    ... 13 more of the same ...
    project-health-update-2025-10-09.md: Filename must follow YYYY-MM-DD-title.md
    project-health-update-2025-10-09.md: Missing required frontmatter: title, date, tags, summary
    2026-07-22-three-days-of-first-contact.md: Missing required frontmatter field: summary

Fixing those 16 would turn CI green and would not give Pip a blog he wants to
write in. That is why this sheet exists.

---

## What is actually in `dev-blog/entries/`

    ls dev-blog/entries | wc -l                                  -> 50
    ls dev-blog/entries | grep -oE '^[0-9]{4}-[0-9]{2}' | sort | uniq -c

| Month | Entries |
|---|---|
| 2025-09 | **45** |
| 2025-10 | 2 |
| 2026-07 | **1** |
| non-conforming filenames | 2 |

**47 of 50 entries are from the pygame era.** Titles like *"Type Annotation
Campaign Phase 2: Complete Core System Coverage"* and *"Employee Blob Manager
Extraction"*. They are machine-written progress reports about a codebase that no
longer exists -- the game is Godot now.

`dev-blog/config.json` still describes the project as:

    "description": "Development progress updates for the P(Doom) pygame strategy game"

**Exactly one entry is from 2026**: `2026-07-22-three-days-of-first-contact.md`,
title *"Three days of first contact: a Claude's-eye view"*. It is the only entry
a reader should land on, and its ONLY validation failure is a missing `summary:`
field -- a one-line fix.

---

## THE DECISION

> **Do the 47 pygame-era auto-generated posts stay, or get archived?**

Nothing else can be settled first. In particular the navigation Pip wants
depends on it.

### Option A -- Archive the 47, start the column at the 2026-07-22 post

- Move them to `dev-blog/archive/` (or delete; they are in git history either way).
- Add `summary:` to the 2026-07-22 entry. **CI goes green with that one line.**
- The blog becomes: one real essay, and whatever Pip writes next.
- Cost: the archive is a judgement that they have no readers. They almost
  certainly have none -- they were never published, because the sync has never
  once succeeded.

### Option B -- Keep all 50, retitle 15 to pass the 60-char limit

- CI goes green.
- The blog's front page is 47 type-annotation reports about a dead codebase,
  then one essay.
- Cost: retitling published-looking posts to satisfy a linter is dressing a
  graveyard, and the sequential navigation below becomes actively hostile.

### Option C -- Raise `max_title_length` and keep everything

- Cheapest. CI green in one config edit.
- Same front page as B. Declines the editorial question rather than answering it.

**Recommendation: A.** The validator has never passed, so nothing was ever
published; there is no audience to disappoint. And the 47 are not writing Pip
did -- they are agent output from a retired engine.

---

## Why the decision blocks the navigation Pip asked for

Pip, 2026-08-21:

> "I want the dev blog pages to have their own unique URLs and then navigation
> breadcrumbs in sequence, like MaRo's old blog on dailymtg.com. I can write
> those more than I can write infinite scroll page things, which I realise now I
> mostly hate. Maybe they're ok for patch notes."

That is a **serial column**, not a feed: each entry is a destination with its own
URL, and prev/next walks the sequence.

**A prev/next chain is only worth walking if the sequence is worth walking.**
Under option B or C, "Previous article" from the one good essay lands the reader
on *"Deterministic Event Manager Extraction"*, 2025-09-24. The navigation would
work perfectly and be a trap. Under option A the chain is short and every link
is something Pip wrote on purpose.

The infinite-scroll instinct is also worth recording: Pip's read is that scroll
feeds suit **patch notes** (undifferentiated, skimmed, chronological) and not
**columns** (each a destination). That distinction is a design rule, not a
preference, and it should be written into whatever the website does.

---

## Where the work lands (NOT this repo)

The rendering lives in `pdoom1-website`:

    scripts/build-blog-index.py
    scripts/test-blog-render.js
    public/blog/
    public/data/blog.json

This repo owns the CONTENT (`dev-blog/entries/`) and the sync workflow
(`.github/workflows/sync-dev-blog.yml`, path-filtered on `dev-blog/index.json`).
The per-post URLs and the prev/next breadcrumbs are a website-side change.

So the sequence is: **Pip decides A/B/C -> content fixed here -> CI goes green ->
navigation built in the website repo.** Step 4 is the interesting one and it is
third in line.

---

## What is true regardless of the decision

- `docs/MUSIC_SYSTEM.md` is not the only stale doc; `dev-blog/config.json`
  calling this a pygame game is the same class and is one line.
- The 2026-07-22 post needs `summary:` no matter which option wins.
- Nothing here is a v0.14.2 blocker. The dev blog has been broken for ten months
  and can be broken for one more day.

---

## Questions only Pip can answer

1. **A, B or C?**
2. If A: archive in-tree (`dev-blog/archive/`) or delete and rely on git history?
3. Does the column want a name? MaRo's had one; "dev blog" is a category, not a
   masthead, and a named column is easier to keep writing.

---

## DECIDED, 2026-08-21

Pip ruled **option A**: archive the pygame-era entries, keep the 2026-07-22 post.

Executed the same day: 49 entries moved to `dev-blog/archive/` with `git mv`
(history preserved), `summary:` added to the kept entry, and
`dev-blog/config.json` corrected -- it still described this as "the P(Doom)
pygame strategy game".

**`python dev-blog/generate_index.py` now exits 0.** That workflow had never
passed once in ten months.

**Correction to the count above:** this document said 47 pygame-era entries. It
is **49**. 47 files are NAMED `2025-*`; two more carry non-conforming filenames
(`project-health-update-2025-10-09.md`,
`type-annotation-phase-2-completion-2025-09-29.md`) and are also 2025-era. The
"47" was the count of well-named files, quoted as though it were the count of
old entries. Left visible rather than edited away -- it is the same hand-typed
integer failure `docs/CLAIM_AUDIT_2026-08-21.md` measured that morning, made by
the same author, hours later.

COMMITMENT: 2026-12-19 -- Read the 49 archived pygame-era dev-blog entries end to end and write the retrospective post: what the pygame era actually cost, what survived the port to Godot, and what the agent-written progress reports got wrong about their own importance -- owner: pip -- kind: review -- note: archived 2026-08-21 per Pip's ask; the value is in reading them as one sequence, which nobody has ever done.

Declared here rather than in `dev-blog/archive/README.md` because the calendar
scanner's `SCAN_GLOBS` does not cover `dev-blog/`. Worth knowing generally:
CLAUDE.md says writing a dated promise ANYWHERE means writing the declaration
line, and that is not literally true -- outside `docs/`, `tools/`, `scripts/`
and root `*.md`, a declaration is silently invisible.

## Still open after this

Navigation is now unblocked and is website-side work: per-post URLs plus
sequential prev/next breadcrumbs, in `pdoom1-website`
(`scripts/build-blog-index.py`, `public/blog/`, `public/data/blog.json`).
With one entry there is no sequence to walk yet -- the chain becomes real on the
second post.

The two open questions from the sheet remain unanswered: whether the column
wants a NAME, and the design rule that scroll feeds suit patch notes while
columns need destinations.
