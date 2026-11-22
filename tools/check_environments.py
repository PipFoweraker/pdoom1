#!/usr/bin/env python3
"""Flag GitHub environments that no workflow references -- and say which are LIES.

Layer: PROVE

THE DEFECT CLASS (found 2026-08-24 across two repos in this estate)
-------------------------------------------------------------------
pdoom1-website has an environment named `production-approval`, created 2025-10-09, with
an EMPTY protection_rules array, referenced by NO workflow. Its NAME asserts an approval
gate. It has no rules and it gates nothing. Anyone auditing that repo by listing
environments reads "production-approval" and concludes deploys are approved.

That is manufactured confidence implemented in a NAME rather than in code -- one layer
below where anybody looks for it. No file contains the false claim; the repository
settings do.

pdoom1 has the same shape, milder: environment `copilot`, protection_rules=0, created
2025-07-31, and no workflow here references any environment at all. `copilot` asserts
nothing about safety, so it misleads nobody.

THE RULE
    AN ENVIRONMENT THAT NO WORKFLOW REFERENCES IS EITHER CLUTTER OR A LIE, AND WHICH
    ONE DEPENDS ENTIRELY ON WHAT IT IS CALLED.

So the classifier is a vocabulary check on the name: approval / review / gate /
protected / prod / production / sign-off mean the name is making a safety claim, and an
unreferenced environment making a safety claim is a FINDING. Everything else is clutter,
reported and not gated.

WHY IT REPORTS ONLY
    Environments are repository settings and settings are Pip's. This never deletes or
    edits one. It also does NOT judge protection_rules on a REFERENCED environment --
    an empty rule set on an environment a workflow actually deploys through is a
    different question with a different answer.

EXIT CODES -- THREE, NOT TWO
    0  measured: no unreferenced environment makes a safety claim. (Clutter may exist
       and is listed.)
    1  measured FINDING: an unreferenced environment whose name asserts a gate.
    2  UNKNOWN: the GitHub API could not be reached, or a workflow names an environment
       through an expression this cannot resolve. **NOT a pass.** A guard that reports
       "no findings" because it could not call GitHub has implemented the exact defect
       it exists to detect -- two seats in this estate wrote that bug into the tools
       built to prevent it on 2026-08-24 alone.

USAGE
    python tools/check_environments.py                    # audit this repo
    python tools/check_environments.py --repo owner/name  # audit another
    python tools/check_environments.py --self-test        # prove BOTH answers, no network

RULING: 2026-08-24 -- an environment no workflow references is either clutter or a lie, and which one depends entirely on what it is called; a safety-vocabulary name with no reference is a finding, any other name is reported and not gated -- flavour: guard-doctrine -- mechanism: tools/check_environments.py in .github/workflows/guards.yml
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover -- pyyaml is in requirements.txt
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"

# A name is making a safety claim if any of its tokens STARTS WITH one of these. Prefix
# matching, not substring: "production" must match "prod" while "reproduction" must not.
SAFETY_STEMS = ("approv", "review", "gate", "protect", "prod", "signoff")
EXPRESSION_RE = re.compile(r"\$\{\{")


def classify(name: str) -> str:
    """ "finding" if the name asserts a gate, else "clutter"."""
    flat = name.lower().replace("-", " ").replace("_", " ").replace(".", " ").replace("/", " ")
    if "sign off" in flat:
        return "finding"
    for token in flat.split():
        if any(token.startswith(stem) for stem in SAFETY_STEMS):
            return "finding"
    return "clutter"


def referenced_environments(directory: Path):
    """({names}, [unresolvable expressions]) named by any job in any workflow."""
    names, unresolved = set(), []
    for path in sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            unresolved.append("%s (will not parse)" % path.name)
            continue
        if not isinstance(doc, dict):
            continue
        for job in (doc.get("jobs") or {}).values():
            if not isinstance(job, dict):
                continue
            env = job.get("environment")
            if env is None:
                continue
            value = env.get("name") if isinstance(env, dict) else env
            if not isinstance(value, str):
                unresolved.append("%s (environment: is not a name)" % path.name)
            elif EXPRESSION_RE.search(value):
                # Cannot tell WHICH environment this is, so cannot tell which are
                # unreferenced. Say UNKNOWN rather than guess.
                unresolved.append("%s (environment: %s)" % (path.name, value))
            else:
                names.add(value)
    return names, unresolved


def fetch_environments(repo: str):
    """([environment dicts], error_message or None). Never raises."""
    cmd = ["gh", "api", "repos/%s/environments" % repo, "--paginate"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return None, "gh is not installed, so the environments list could not be read"
    except subprocess.TimeoutExpired:
        return None, "gh api timed out after 60s"
    if proc.returncode != 0:
        return None, "gh api exited %d: %s" % (proc.returncode, proc.stderr.strip()[:400])
    try:
        # --paginate concatenates JSON objects when the response is an object, so parse
        # each and merge rather than assuming one.
        envs = []
        decoder = json.JSONDecoder()
        text, idx = proc.stdout.strip(), 0
        while idx < len(text):
            obj, end = decoder.raw_decode(text, idx)
            envs.extend(obj.get("environments") or [])
            idx = end
            while idx < len(text) and text[idx] in " \r\n\t":
                idx += 1
    except ValueError as exc:
        return None, "gh api returned unparseable JSON: %s" % exc
    return envs, None


def resolve_repo(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    try:
        url = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?$", url)
    return "%s/%s" % (m.group(1), m.group(2)) if m else None


# --- self-test -------------------------------------------------------------


def self_test() -> int:
    """Prove the classifier separates the two real instances, with NO network call.

    Deliberately synthetic: live environment state changes, and a self-test that reads
    it is not a test, it is a second copy of the thing being tested.
    """
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        if cond:
            print("  [ok] %s" % label)
        else:
            ok = False
            print("SELF-TEST FAIL: %s %s" % (label, detail))

    # The two real instances, by name.
    check(
        "pdoom1-website's `production-approval` classifies as a FINDING",
        classify("production-approval") == "finding",
    )
    check(
        "pdoom1's `copilot` classifies as CLUTTER -- it asserts nothing, so it lies to nobody",
        classify("copilot") == "clutter",
    )

    # The whole declared vocabulary, or the rule has holes where nobody looks.
    vocab = [
        "production-approval",
        "manual-approval",
        "code-review",
        "release-gate",
        "protected-main",
        "prod",
        "production",
        "sign-off",
        "sign_off",
        "signoff",
    ]
    missed = [n for n in vocab if classify(n) != "finding"]
    check("every safety word in the rule is caught", not missed, repr(missed))

    # The other answer, and the false positive worth pinning: prefix matching, not
    # substring, so a legitimate name containing a safety word inside another word
    # is not reported.
    benign = ["copilot", "dependabot", "reproduction-tests", "sandbox", "docs-preview"]
    wrong = [n for n in benign if classify(n) != "clutter"]
    check(
        "benign names are clutter, and `reproduction-tests` does NOT match `prod`",
        not wrong,
        repr(wrong),
    )

    # Referencing is what separates a lie from a configured gate.
    envs = [{"name": "production-approval"}, {"name": "copilot"}]
    referenced = {"production-approval"}
    unref = [e["name"] for e in envs if e["name"] not in referenced]
    check(
        "an environment a workflow DOES reference is not reported at all",
        unref == ["copilot"],
        repr(unref),
    )
    check(
        "and the same name unreferenced is a finding",
        [n for n in [e["name"] for e in envs] if classify(n) == "finding"]
        == ["production-approval"],
    )

    # UNKNOWN must be reachable. A guard whose only failure mode is "pass" is the
    # defect this file exists to detect.
    envs2, err = fetch_environments("this-owner-does-not-exist/nor-does-this-repo-xyzzy")
    check(
        "an API call that cannot succeed returns an error, never an empty pass",
        envs2 is None and err,
        repr(err),
    )

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--repo",
        help="owner/name (default: GITHUB_REPOSITORY, then origin). NOTE: the REFERENCED "
        "set is always read from THIS checkout's .github/workflows/, so pointing --repo "
        "at another repository compares its environments against this repo's workflows. "
        "Useful for a quick look; run it inside that repo for a verdict.",
    )
    ap.add_argument("--self-test", action="store_true", help="prove BOTH answers, no network")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if yaml is None:
        print("[environments] UNKNOWN: pyyaml not installed", file=sys.stderr)
        return 2
    if not WORKFLOW_DIR.is_dir():
        print("[environments] UNKNOWN: %s missing" % WORKFLOW_DIR, file=sys.stderr)
        return 2

    repo = resolve_repo(args.repo)
    if not repo:
        print("[environments] UNKNOWN: could not determine owner/repo", file=sys.stderr)
        return 2

    envs, err = fetch_environments(repo)
    if envs is None:
        print("[environments] UNKNOWN: %s" % err, file=sys.stderr)
        print(
            "  This is NOT a pass. An environments audit that reports 'no findings'\n"
            "  because it could not reach GitHub has implemented the very defect it\n"
            "  exists to detect.",
            file=sys.stderr,
        )
        return 2

    local = resolve_repo(None)
    if local and repo != local:
        print(
            "[environments] NOTE: --repo %s, but the referenced set comes from THIS\n"
            "  checkout (%s). Treat the verdict as indicative only." % (repo, local)
        )

    referenced, unresolved = referenced_environments(WORKFLOW_DIR)
    if unresolved:
        print("[environments] UNKNOWN: a workflow names an environment this cannot resolve:")
        for u in unresolved:
            print("    %s" % u)
        print("  Which environments are unreferenced is therefore not knowable here.")
        return 2

    print(
        "[environments] %s -- %d environment(s), %d referenced by a workflow"
        % (repo, len(envs), len(referenced))
    )
    findings, clutter = [], []
    for env in sorted(envs, key=lambda e: e.get("name", "")):
        name = env.get("name", "")
        rules = len(env.get("protection_rules") or [])
        if name in referenced:
            print("  referenced  %-28s protection_rules=%d" % (name, rules))
            continue
        (findings if classify(name) == "finding" else clutter).append((name, rules, env))

    for name, rules, env in clutter:
        print(
            "  CLUTTER     %-28s protection_rules=%d  created %s"
            % (name, rules, env.get("created_at", "?"))
        )
    for name, rules, env in findings:
        print(
            "  FINDING     %-28s protection_rules=%d  created %s"
            % (name, rules, env.get("created_at", "?"))
        )

    print()
    if findings:
        print(
            "[environments] FAIL: %d unreferenced environment(s) whose NAME asserts a"
            % len(findings)
        )
        print("  gate. No workflow deploys through them, so the claim is made to anyone")
        print("  listing environments and honoured by nothing:")
        for name, rules, _ in findings:
            print("    %s (protection_rules=%d)" % (name, rules))
        print("  Fix by renaming it, deleting it, or referencing it from the workflow it")
        print("  claims to gate. This tool reports only -- settings are Pip's.")
        return 1

    if clutter:
        print(
            "[environments] OK: %d unreferenced environment(s), none asserting a gate."
            % len(clutter)
        )
        print("  Clutter, not a lie -- reported so it does not accumulate, not gated.")
    else:
        print("[environments] OK: every environment is referenced by a workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
