# Archived dev-blog entries -- the pygame era

**49 entries, 2025-09-10 to 2025-10-09.** Moved here from `dev-blog/entries/` on
2026-08-21 by Pip's decision.

## Why they were archived

They are agent-written progress reports about a codebase that no longer exists.
P(Doom)1 was a pygame project when these were written; it is Godot 4.5.1 now, and
the Python bridge is gone. Titles like *"Type Annotation Campaign Phase 2:
Complete Core System Coverage"* and *"Employee Blob Manager Extraction"* describe
files that are not in the tree.

**None of them were ever published.** The `Sync Dev Blog to Website` workflow has
never once passed -- it failed on 2026-08-20, on 2026-07-23, and four times in
2025 -- because 16 of these entries fail the validator in
`dev-blog/config.json` (15 on the 60-character title limit, plus two
non-conforming filenames and missing frontmatter). So there is no audience being
deprived of them and no incoming link to break.

The one entry that stayed in `entries/` is
`2026-07-22-three-days-of-first-contact.md`, which is the only entry written
about the game as it now exists.

## Why they were kept rather than deleted

They are a record of how the project was actually built, including the parts that
were later thrown away. That is the raw material for a retrospective, and it is
worth more read all at once than it ever was drip-fed as a feed.

**Pip asked for a note to revisit these by the end of the year for a proper
retrospective post.** That is declared as a dated commitment -- but NOT here.
`scripts/generate_commitment_calendar.py` scans `docs/**/*.md`,
`tools/**/*.py`, `scripts/**/*.py` and root `*.md` only, so `dev-blog/` is
outside its reach and a declaration written in this file would never reach the
calendar. It lives in `docs/DEV_BLOG_DECISION_2026-08-21.md` instead, dated
**2026-12-19** -- before the end of the year, on a working day rather than on
New Year's Eve.

## Etiquette for this directory

- **Do not edit these files.** They are a record of what was written at the time,
  including the claims that turned out to be wrong. Correcting them retroactively
  would destroy the only thing they are good for.
  - **One exception, already used once, and it is not editorial:** encoding
    normalisation forced by the repo-wide ASCII rule (issue #744), recorded here
    rather than done quietly. On 2026-08-21,
    `2025-10-10-programmatic-control-implementation.md` carried 11 non-ASCII
    characters -- one U+1F680 rocket and ten U+2705 check marks. The check marks
    became `[OK]`, the house ASCII chrome; the rocket was decorative and was
    dropped. No wording changed.
  - **How it survived until now is the more interesting part.** The `no-emoji`
    gate covers `godot/**` only, and `enforce-standards` runs `--incremental`
    over the files a commit touches. This file had not been touched since it was
    written, so no gate had ever read it. It has been in the repository since
    2025-10-10 and the first thing to notice was `git mv`. Anything else never
    edited since is equally unscanned.
- **Do not move them back into `entries/`** to "fix" the blog. If something here
  deserves publishing, it deserves rewriting as a new post that says so.
- `dev-blog/generate_index.py` globs `entries/*.md` non-recursively, so nothing
  in this directory is indexed, validated or synced. That is intentional.
