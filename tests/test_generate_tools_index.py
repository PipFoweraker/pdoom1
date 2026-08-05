#!/usr/bin/env python3
"""Unit tests for scripts/generate_tools_index.py (the dev-tools index generator).

What these lock down:

- Docstring parsing: purpose extraction, tolerant Layer:/Invoked by: declaration
  parsing, unrecognised layers recorded rather than fatal, usage-hint detection.
- Caller discovery: pre-commit / Makefile / workflow / test / sibling-tool
  matching, and the docstring-stripping defense (a tool that merely NAMES a
  sibling in prose must not fabricate a caller for it).
- UNKNOWN classification: no declaration + no usage hint + no caller, and
  nothing else, lands a tool there.
- The guard can actually fail: --check goes red when a tool appears that the
  committed index does not know about, and green again when it is removed.
  Two guards shipped this week that could not fail; this asserts ours can.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_tools_index as gti  # noqa: E402


def make_fixture(root: Path) -> None:
    """A tiny fake repo exercising every discovery path."""
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "archive").mkdir()
    (root / "tools").mkdir()
    (root / "tests").mkdir()
    (root / "docs").mkdir()
    (root / ".github" / "workflows").mkdir(parents=True)

    (root / "scripts" / "alpha.py").write_text(
        '"""Alpha checks a thing and fails loudly.\n'
        "\n"
        "Layer: PROVE -- trailing comment must be tolerated\n"
        "\n"
        "Wired into pre-commit.\n"
        "\n"
        "Usage:\n"
        "    python scripts/alpha.py\n"
        '"""\n',
        encoding="utf-8",
    )
    (root / "scripts" / "beta.py").write_text("x = 1\n", encoding="utf-8")  # no docstring
    (root / "tools" / "gamma.py").write_text(
        '"""Gamma reports on things.\n\nInvoked by: human\n"""\n', encoding="utf-8"
    )
    (root / "tools" / "delta.py").write_text(
        '"""Delta does something, but nothing says how it is run."""\n', encoding="utf-8"
    )
    # eps CALLS gamma in code, but only MENTIONS delta in its docstring -- the
    # docstring must be stripped before caller discovery, so delta stays orphaned.
    (root / "tools" / "eps.py").write_text(
        '"""Eps drives things. Unlike delta.py, eps has a caller story.\n'
        "\n"
        "Layer: WIBBLE\n"
        '"""\n'
        'import subprocess\n\nsubprocess.run(["python", "gamma.py"])\n',
        encoding="utf-8",
    )
    (root / "tools" / "zeta.py").write_text(
        '"""Zeta claims to be the CI gate for everything."""\n', encoding="utf-8"
    )
    (root / "scripts" / "archive" / "old.py").write_text(
        '"""Old archived thing."""\n', encoding="utf-8"
    )

    (root / ".pre-commit-config.yaml").write_text(
        "hooks:\n  - entry: python scripts/alpha.py\n", encoding="utf-8"
    )
    (root / "Makefile").write_text("report:\n\tpython tools/gamma.py\n", encoding="utf-8")
    (root / ".github" / "workflows" / "x.yml").write_text(
        "run: python scripts/beta.py\n", encoding="utf-8"
    )
    (root / "tests" / "test_alpha.py").write_text("from alpha import main\n", encoding="utf-8")


class ToolsIndexFixtureTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        make_fixture(self.root)
        self.records, self.archived = gti.collect(self.root)
        self.by_rel = {r["rel"]: r for r in self.records}

    def tearDown(self):
        self._tmp.cleanup()

    def rec(self, rel):
        return self.by_rel[rel]

    def test_collects_active_and_archived_separately(self):
        self.assertIn("scripts/alpha.py", self.by_rel)
        self.assertNotIn("scripts/archive/old.py", self.by_rel)
        self.assertEqual(
            [p.name for p in self.archived], ["old.py"], "archive/ must be split out, not dropped"
        )

    def test_parses_declarations_tolerantly(self):
        alpha = self.rec("scripts/alpha.py")
        self.assertEqual(alpha["layer"], "PROVE")
        self.assertEqual(alpha["purpose"], "Alpha checks a thing and fails loudly.")
        self.assertTrue(alpha["usage_hint"])
        self.assertIn("pre-commit", alpha["claims"])
        gamma = self.rec("tools/gamma.py")
        self.assertEqual(gamma["declared_invokers"], "human")
        # An unrecognised layer is RECORDED, never fatal.
        eps = self.rec("tools/eps.py")
        self.assertIsNone(eps["layer"])
        self.assertEqual(eps["layer_raw"], "WIBBLE")

    def test_missing_docstring_is_reported_not_fatal(self):
        beta = self.rec("scripts/beta.py")
        self.assertEqual(beta["purpose"], "")
        self.assertFalse(beta["parse_error"])

    def test_discovers_every_caller_category(self):
        self.assertIn("pre-commit", self.rec("scripts/alpha.py")["callers"])
        self.assertIn("test:test_alpha.py", self.rec("scripts/alpha.py")["callers"])
        self.assertIn("ci:x.yml", self.rec("scripts/beta.py")["callers"])
        gamma = self.rec("tools/gamma.py")["callers"]
        self.assertIn("make", gamma)
        self.assertIn("tool:eps.py", gamma)

    def test_docstring_mention_does_not_fabricate_a_caller(self):
        # eps.py's DOCSTRING names delta.py; that must not count as a caller.
        self.assertEqual(self.rec("tools/delta.py")["callers"], [])

    def test_unknown_is_exactly_the_undeclared_uncalled_set(self):
        unknown = {r["rel"] for r in self.records if gti.is_unknown(r)}
        self.assertIn("tools/delta.py", unknown)
        self.assertNotIn("scripts/alpha.py", unknown)  # has callers + declaration
        self.assertNotIn("tools/gamma.py", unknown)  # declared Invoked by: human
        self.assertNotIn("tools/eps.py", unknown)  # declares a layer, even a bad one

    def test_claim_gaps_flag_uncorroborated_ci_claims(self):
        gaps = dict(gti.claim_gaps(self.records))
        self.assertIn("tools/zeta.py", gaps, "claims CI, nothing calls it -> the finding")
        self.assertNotIn(
            "scripts/alpha.py", gaps, "claims pre-commit AND pre-commit calls it -> no gap"
        )

    def test_render_is_ascii_and_deterministic(self):
        out = gti.render(self.root)
        out.encode("ascii")  # raises if not
        self.assertEqual(out, gti.render(self.root))
        self.assertIn("`tools/delta.py`", out)
        self.assertIn("UNKNOWN", out)
        self.assertIn("WIBBLE (unrecognised)", out)
        self.assertIn("scripts/archive/old.py", out)

    def test_check_goes_red_on_a_new_tool_and_green_again(self):
        """PROVE THE GUARD FAILS -- per #640's lesson applied to its successors."""
        with mock.patch.object(gti, "ROOT", self.root):
            with mock.patch.object(sys, "argv", ["generate_tools_index.py"]):
                self.assertEqual(gti.main(), 0)  # write the index
            with mock.patch.object(sys, "argv", ["generate_tools_index.py", "--check"]):
                self.assertEqual(gti.main(), 0, "freshly written index must be green")
                probe = self.root / "tools" / "zz_probe.py"
                probe.write_text('"""Probe."""\n', encoding="utf-8")
                self.assertEqual(gti.main(), 1, "a new tool MUST turn --check red")
                probe.unlink()
                self.assertEqual(gti.main(), 0, "removing it must turn --check green")


class RealRepoSmokeTest(unittest.TestCase):
    def test_real_tree_renders_and_indexes_itself(self):
        out = gti.render(REPO_ROOT)
        out.encode("ascii")
        self.assertIn("generate_tools_index.py", out)
        self.assertIn("run_godot_tests.py", out)


if __name__ == "__main__":
    unittest.main()
