# Deliberately untagged versions

`version.txt` is the version SSOT. Every value it has ever held is expected to
have a matching git tag -- because a tag push is what arms
`.github/workflows/enhanced-release.yml`, which builds all three platforms and
publishes the GitHub release with assets. **A bump with no tag is a release that
was prepared and never delivered, and until 2026-08-24 nothing in this repo
could see that state.**

Sometimes a bump legitimately does not get a tag: an internal playtest cut, a
version claimed and then superseded before it shipped, a number burned by
mistake. Those are fine. What is not fine is leaving the machine unable to tell
that case apart from a forgotten release.

So: declare it here, one line, in the same shape as the ruling and commitment
declaration conventions used elsewhere in this tree (see
`docs/rulings/RULINGS_CONVENTION.md` and `docs/calendar/COMMITMENTS.md` -- the
markers are not spelled out here, because writing one in prose is itself a
malformed declaration to the scanners that read for them).

    UNTAGGED: <version> -- <reason>

`tools/check_release_ledger.py` parses those lines and stops failing on that
version. The prose around a declaration is free -- only the line is parsed.

## Declarations

<!-- Add UNTAGGED: lines below. None yet. -->

## Currently undeclared and untagged

As of 2026-08-24 this is `0.14.3`, and it is **not** being declared here,
because it is not a deliberate skip -- it is the defect that caused this file
to exist. It is a real playtest cut with a proven build on disk, a blessed
seed and a fresh ladder epoch, waiting on a decision about whether it ships
publicly. See `docs/releases/RELEASE_LEDGER.md`.

The two honest exits, and they are the only two:

1. **Push the tag.** `enhanced-release.yml` takes it from there -- validate,
   build Windows/macOS/Linux, feeds, manifest, GitHub release with assets,
   then verify every advertised download URL answers 200. This is an
   outward-facing, hard-to-reverse act: it publishes a public release.
2. **Declare it here** with the reason it stays internal, and let the next
   public version be the one that ships.

What is not an exit is leaving it undecided, which is the state that produced
this file.
