# Hook-safe commits: `tools/commit.py` / `make commit`

## Why this exists

Two recurring commit failures on this repo:

1. **Reformat-abort dance.** Several pre-commit hooks are *fixers*
   (trailing-whitespace, end-of-file-fixer, mixed-line-ending, black, isort,
   ruff --fix): they modify the file AND fail the commit with
   `files were modified by this hook`. The fix is always mechanical --
   re-`git add` the same paths and commit again -- so the wrapper does that
   retry for you (exactly once; a second failure means a real hook rejection).

2. **Settings-trap.** `.claude/settings.local.json` is tracked but rewritten
   by the Claude session harness whenever tools run. If it changes while
   pre-commit has it stashed, the hook run aborts with "Stashed changes
   conflicted with hook auto-fixes... Rolling back" -- and the rollback can
   discard working-tree edits. The wrapper marks the file
   `git update-index --skip-worktree` (idempotent, runs every invocation)
   so git ignores local churn there.

## Usage

```
python tools/commit.py -m "fix(ui): message" path/one.gd path/two.md
python tools/commit.py -m "docs: message" -u       # all tracked changes
```

Or via make:

```
make commit m="fix(ui): message" f="path/one.gd path/two.md"
make commit m="docs: message" f="-u"
```

Notes:

- Explicit paths only (or `-u` for tracked files). It never does `git add -A`,
  and it refuses `.claude/settings.local.json` as a path.
- If the retry also fails, that is a genuine hook rejection (ASCII violation,
  stale DQ index, scene-nav violation, version drift...). Read the hook
  output and fix the underlying issue; the wrapper deliberately does not
  loop.

## The real root fix: format on save

`.vscode/settings.json` mirrors the fixer hooks (trim trailing whitespace,
final newline, LF line endings, black/isort/ruff on save for Python), so
files are already clean by commit time and the hooks find nothing to fix.
Note `.vscode/` is currently gitignored, so that config is machine-local;
committing it would need a `!.vscode/settings.json` exception in
`.gitignore` (Pip's call).

## Deferred upgrade (do not do mid-crunch)

Converting the fixer hooks to check-only (so hooks never modify files and
never need the retry) is deliberately deferred -- changing
`.pre-commit-config.yaml` behaviour is a later, careful change.
