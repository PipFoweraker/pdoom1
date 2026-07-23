#!/usr/bin/env python3
"""Commit wrapper that absorbs the "hook reformatted a file then aborted" dance.

Problem this solves (two known failure modes of plain `git commit` here):

1. Reformat-abort: pre-commit fixer hooks (trailing-whitespace,
   end-of-file-fixer, mixed-line-ending, black, isort, ruff --fix) MODIFY
   files and then FAIL the commit with "files were modified by this hook".
   The fix is always the same: re-`git add` the same paths and commit again.
   This wrapper does that retry automatically (once).

2. Settings-trap: `.claude/settings.local.json` is tracked but rewritten by
   the Claude session harness whenever tools run. If it changes while
   pre-commit has it stashed, pre-commit reports "Stashed changes conflicted
   with hook auto-fixes... Rolling back" and the rollback can DISCARD
   working-tree edits. This wrapper sets
   `git update-index --skip-worktree .claude/settings.local.json`
   (idempotent) before every commit so git ignores local churn in that file.

Usage:
    python tools/commit.py -m "feat: message" path/to/a.py path/to/b.md
    python tools/commit.py -m "feat: message" -u        # all tracked changes

Notes:
- Staging is explicit-paths only (or -u for tracked files). Never `add -A`.
- `.claude/settings.local.json` is refused as a path argument on purpose.
- Exactly ONE retry: if the second attempt still fails, a real (non-fixer)
  hook rejected the commit -- read its output and fix the underlying issue.
"""

import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_TRAP = ".claude/settings.local.json"
HOOK_MODIFIED_MARKER = "files were modified by this hook"


def run(cmd, capture=False):
    """Run a git command from the repo root. Returns CompletedProcess."""
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=capture,
        text=capture,
    )


def ensure_skip_worktree():
    """Idempotently mark the settings trap file skip-worktree.

    Safe to call every time: setting the flag twice is a no-op, and if the
    file is untracked or missing, git errors are swallowed (nothing to trap).
    """
    result = run(["git", "ls-files", "-v", "--", SETTINGS_TRAP], capture=True)
    lines = (result.stdout or "").splitlines()
    if lines and lines[0][:1] == "S":
        return  # already skip-worktree
    run(["git", "update-index", "--skip-worktree", SETTINGS_TRAP], capture=True)


def stage(paths, update_tracked):
    if update_tracked:
        return run(["git", "add", "-u"])
    return run(["git", "add", "--"] + paths)


def commit(message):
    """Run git commit in the foreground, teeing output so we can inspect it."""
    proc = subprocess.Popen(
        ["git", "commit", "-m", message],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    captured = []
    for line in proc.stdout:
        sys.stdout.write(line)
        captured.append(line)
    proc.wait()
    return proc.returncode, "".join(captured)


def main():
    parser = argparse.ArgumentParser(
        prog="commit.py",
        description=(
            "Hook-friendly git commit: stages the given paths, commits, and if "
            "a pre-commit fixer hook reformatted files and aborted the commit "
            "('files were modified by this hook'), re-adds the same paths and "
            "retries once. Also sets skip-worktree on "
            ".claude/settings.local.json so harness churn there cannot break "
            "the hooks' stash/unstash."
        ),
        epilog=(
            "Examples:\n"
            '  python tools/commit.py -m "fix(ui): message" godot/scripts/ui/x.gd\n'
            '  python tools/commit.py -m "docs: message" -u\n'
            '  make commit m="fix: message" f="path1 path2"'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-m", "--message", required=True, help="commit message")
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="stage ALL modified tracked files (git add -u) instead of named paths",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="paths to stage and commit (omit only when using -u)",
    )
    args = parser.parse_args()

    if not args.update and not args.paths:
        parser.error("give one or more paths, or -u for all tracked changes")
    if args.update and args.paths:
        parser.error("use either explicit paths or -u, not both")

    banned = [p for p in args.paths if p.replace("\\", "/").endswith(SETTINGS_TRAP)]
    if banned:
        parser.error(f"{SETTINGS_TRAP} is local-only and must never be committed")

    ensure_skip_worktree()

    staged = stage(args.paths, args.update)
    if staged.returncode != 0:
        print("commit.py: git add failed; aborting before commit", file=sys.stderr)
        return staged.returncode

    code, output = commit(args.message)
    if code == 0:
        return 0

    if HOOK_MODIFIED_MARKER not in output:
        print(
            "\ncommit.py: commit failed for a reason other than hook auto-fixes; "
            "not retrying. Read the hook output above.",
            file=sys.stderr,
        )
        return code

    print(
        "\ncommit.py: hooks reformatted files -- re-adding the same paths and " "retrying once...",
        file=sys.stderr,
    )
    staged = stage(args.paths, args.update)
    if staged.returncode != 0:
        print("commit.py: re-add failed; aborting", file=sys.stderr)
        return staged.returncode

    code, _ = commit(args.message)
    if code == 0:
        print("commit.py: retry succeeded (hook fixes are included).", file=sys.stderr)
    else:
        print(
            "commit.py: retry ALSO failed -- a real hook rejection, not just "
            "reformatting. Fix the reported issue, then rerun.",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
