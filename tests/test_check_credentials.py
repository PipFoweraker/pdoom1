#!/usr/bin/env python3
"""Unit tests for the C2PA content-credential guard and the pipeline fix it protects.

WHAT IS BEING PROTECTED, AND WHY IT NEEDS A TEST RATHER THAN A COMMENT

The OpenAI Images API returns a signed C2PA manifest in a `caBX` PNG chunk.
PIL drops unknown ancillary chunks on re-encode, so `Image.open(b).save(p)`
deletes it and leaves a perfectly good-looking image behind. That is how
roughly 1,600 masters lost their provenance before 2026-08-15, silently, with
no failing test and no visible symptom.

The fix is two lines (`write_bytes` instead of a re-encode) in each of
`tools/assets/generate_images.py` and `tools/assets/run_art_night.py`. Two-line
fixes of this shape are exactly what a later tidy-up reverts, because the
re-encode version looks more idiomatic. These tests exist so that revert fails
out loud.

THE NEGATIVE CONTROL IS THE POINT

Every preservation test here is paired with a control that runs the OLD code
path over the SAME bytes and asserts it LOSES the credential. Without that, a
green suite is consistent with "the detector is broken and sees credentials
everywhere". A published command must be shown capable of returning the other
answer (docs/CLAIM_AUDIT_2026-08-06.md).

FIXTURES ARE SYNTHETIC ON PURPOSE

A real credential is ~29-65 KB of signed CBOR. Committing one as a fixture
would put a binary blob in git to test a chunk-copying property that a 200-byte
synthetic PNG demonstrates exactly as well. Nothing here needs a valid
signature -- the failure being guarded is chunk survival, not cryptography.
"""

import struct
import sys
import tempfile
import unittest
import zlib
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "assets"))

import check_credentials as cc  # noqa: E402

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + ctype
        + payload
        + struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF)
    )


def make_png(width: int = 4, height: int = 4, credential: bytes | None = None) -> bytes:
    """A minimal valid RGBA PNG, optionally carrying a `caBX` credential chunk."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x40\x40\x40\xff" * width for _ in range(height))
    parts = [PNG_MAGIC, _chunk(b"IHDR", ihdr)]
    if credential is not None:
        parts.append(_chunk(b"caBX", credential))
    parts.append(_chunk(b"IDAT", zlib.compress(raw)))
    parts.append(_chunk(b"IEND", b""))
    return b"".join(parts)


FAKE_CREDENTIAL = (
    b"jumbc2pa"
    + b"cv.iptc.org/newscodes/digitalsourcetype/"
    + b"trainedAlgorithmicMedia"
    + b"\x00" * 64
)


class TestDetector(unittest.TestCase):
    """The detector must be able to return both answers, and refuse decoys."""

    def test_plain_png_has_no_credential(self):
        self.assertIsNone(cc.read_c2pa_box(make_png()))

    def test_credentialed_png_yields_exact_payload(self):
        box = cc.read_c2pa_box(make_png(credential=FAKE_CREDENTIAL))
        self.assertEqual(box, FAKE_CREDENTIAL)

    def test_cabx_bytes_inside_image_data_are_not_a_credential(self):
        """A `caBX` run in compressed pixel data must not register as a chunk.

        This is why the detector walks the chunk table instead of searching for
        the marker. A substring search would pass every other test here and
        still be wrong.
        """
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
        # Compression level 0 = stored, so the literal bytes survive into the
        # file. With default compression they do NOT, and this test would pass
        # while containing no decoy at all -- which is why the fixture is
        # asserted below rather than assumed.
        idat = zlib.compress(b"\x00" + b"caBX", 0)
        data = PNG_MAGIC + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
        self.assertIn(b"caBX", data, "fixture must actually contain the decoy bytes")
        self.assertIsNone(cc.read_c2pa_box(data))

    def test_non_png_is_handled_not_crashed(self):
        self.assertIsNone(cc.read_c2pa_box(b"GIF89a and then some nonsense"))
        self.assertIsNone(cc.read_c2pa_box(b""))

    def test_truncated_png_does_not_hang_or_raise(self):
        truncated = make_png(credential=FAKE_CREDENTIAL)[:40]
        self.assertIsNone(cc.read_c2pa_box(truncated))


class TestStreamingReaderMatchesInMemory(unittest.TestCase):
    """The fast path must give the same answer as the tested slow one.

    `credential_of` uses a seeking reader (O(chunks), not O(file size)) because
    the naive version read ~4 GB across art_source and blew a 120s timeout. Two
    implementations of the same predicate is exactly how a fast path silently
    drifts, so they are compared directly on every fixture shape.
    """

    def _both(self, data: bytes):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.png"
            p.write_bytes(data)
            return cc.read_c2pa_box(data), cc.read_c2pa_box_streaming(p)

    def test_agree_on_credentialed(self):
        mem, stream = self._both(make_png(32, 32, credential=FAKE_CREDENTIAL))
        self.assertEqual(mem, FAKE_CREDENTIAL)
        self.assertEqual(mem, stream)

    def test_agree_on_plain(self):
        mem, stream = self._both(make_png(32, 32))
        self.assertIsNone(mem)
        self.assertIsNone(stream)

    def test_agree_on_non_png(self):
        mem, stream = self._both(b"not a png at all")
        self.assertIsNone(mem)
        self.assertIsNone(stream)

    def test_agree_on_truncated(self):
        mem, stream = self._both(make_png(32, 32, credential=FAKE_CREDENTIAL)[:30])
        self.assertEqual(mem, stream)

    def test_streaming_handles_missing_file(self):
        self.assertIsNone(cc.read_c2pa_box_streaming(Path("no/such/file.png")))


class TestIptcTermExtraction(unittest.TestCase):
    """The reported source type is quoted as disclosure, so it must not be guessed."""

    def _source_type(self, term: bytes) -> str:
        payload = b"cv.iptc.org/newscodes/digitalsourcetype/" + term + b"\xff\xffnextkey"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.png"
            p.write_bytes(make_png(credential=payload))
            return cc.credential_of(p)["digital_source_type"]

    def test_ai_generated_term(self):
        self.assertEqual(self._source_type(b"trainedAlgorithmicMedia"), "trainedAlgorithmicMedia")

    def test_longest_match_wins_over_prefix(self):
        """`composite` prefixes three other terms; the specific one must win."""
        self.assertEqual(
            self._source_type(b"compositeWithTrainedAlgorithmicMedia"),
            "compositeWithTrainedAlgorithmicMedia",
        )
        self.assertEqual(self._source_type(b"compositeSynthetic"), "compositeSynthetic")
        self.assertEqual(self._source_type(b"composite"), "composite")

    def test_human_authored_term(self):
        self.assertEqual(self._source_type(b"digitalCreation"), "digitalCreation")

    def test_unknown_term_is_reported_as_unrecognised_not_invented(self):
        self.assertEqual(self._source_type(b"someFutureIptcTerm"), "UNRECOGNISED")


class TestSelfTest(unittest.TestCase):
    def test_guard_self_test_passes(self):
        self.assertEqual(cc.self_test(), 0)


class TestPipelinePreservesCredentials(unittest.TestCase):
    """The two call sites must write masters verbatim. Each with its control."""

    def test_generate_images_preserves_and_old_path_would_not(self):
        import generate_images as gi

        signed = make_png(64, 64, credential=FAKE_CREDENTIAL)
        original = gi._openai_generate_bytes
        gi._openai_generate_bytes = lambda *a, **k: signed
        try:
            with tempfile.TemporaryDirectory() as td:
                out = Path(td)
                ok, _cost, master = gi.generate_image(
                    asset_id="cred_test",
                    full_prompt="(patched, no network)",
                    output_dir=out,
                    sizes=[64, 32],
                    size_str="64x64",
                    backend="openai",
                    background="opaque",
                )
                self.assertTrue(ok)
                master = Path(master)

                self.assertEqual(
                    master.read_bytes(),
                    signed,
                    "master must be byte-identical to the API response",
                )
                self.assertIsNotNone(cc.read_c2pa_box(master.read_bytes()))

                derived = sorted(p for p in out.glob("*.png") if p != master)
                self.assertEqual(len(derived), 1, "the 32px downscale must still be produced")
                self.assertIsNone(
                    cc.read_c2pa_box(derived[0].read_bytes()),
                    "a downscale must NOT claim a signature covering pixels it changed",
                )
        finally:
            gi._openai_generate_bytes = original

        self._assert_control_loses_it(signed)

    def test_run_art_night_preserves_through_master_and_staging(self):
        import run_art_night as ran

        signed = make_png(64, 64, credential=FAKE_CREDENTIAL)
        # write_outputs computes master.relative_to(REPO), so the sandbox must
        # live inside the repo rather than in the system temp dir.
        sandbox = Path(tempfile.mkdtemp(prefix=".credtest_", dir=REPO_ROOT))
        try:
            out_dir = sandbox / "out"
            stage = sandbox / "stage"
            out_dir.mkdir(parents=True)
            job = {
                "out_dir": str(out_dir),
                "master_path": str(out_dir / "t_v1_64.png"),
                "base_name": "t_v1",
                "size": "64x64",
                "job_id": "t-1",
                "level": "L0",
                "block": "t",
                "cell": "s01_r01_p01",
                "variant": 1,
                "prompt": "(offline)",
                "prompt_sha256": "0" * 64,
                "model": "gpt-image-1",
                "quality": "low",
                "background": "opaque",
                "cost_usd": 0.0,
            }
            run_meta = dict.fromkeys(
                [
                    "cost_source",
                    "taste_profile_path",
                    "taste_profile_sha256",
                    "taste_profile_source",
                    "queue_spec_sha256",
                ],
                "n/a",
            )
            run_meta.update({"run_id": "credtest", "backend": "openai"})
            api_meta = {"revised_prompt": None, "api_created": None, "api_usage": None}

            sidecar = ran.write_outputs(job, signed, api_meta, run_meta, staging_dir=str(stage))

            master = Path(job["master_path"])
            self.assertEqual(master.read_bytes(), signed)
            self.assertIsNotNone(cc.read_c2pa_box(master.read_bytes()))
            self.assertEqual(
                sidecar["master_bytes"],
                len(signed),
                "the sidecar's recorded size must describe the file actually written",
            )
            staged = stage / master.name
            self.assertIsNotNone(
                cc.read_c2pa_box(staged.read_bytes()),
                "staging feeds the website; a strip here defeats the whole point",
            )
        finally:
            import shutil

            shutil.rmtree(sandbox, ignore_errors=True)

        self._assert_control_loses_it(signed)

    def _assert_control_loses_it(self, signed: bytes) -> None:
        """The old code path over the same bytes MUST destroy the credential.

        If this ever stops failing, the tests above prove nothing: they would be
        green on a pipeline that could not lose a credential in the first place.
        """
        from PIL import Image

        buf = BytesIO()
        Image.open(BytesIO(signed)).convert("RGBA").save(buf, format="PNG")
        self.assertIsNone(
            cc.read_c2pa_box(buf.getvalue()),
            "negative control did not reproduce the loss -- these tests prove nothing",
        )


class TestRatchet(unittest.TestCase):
    """Both drift directions must be detected, against real files on disk."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.shipped = root / "assets"
        self.shipped.mkdir()
        self._orig = (cc.REPO, cc.SHIPPED, cc.WORKING, cc.PIN)
        cc.REPO = root
        cc.SHIPPED = self.shipped
        cc.WORKING = root / "working"
        cc.PIN = root / "pin.json"

    def tearDown(self):
        cc.REPO, cc.SHIPPED, cc.WORKING, cc.PIN = self._orig
        self.tmp.cleanup()

    def _write(self, name, credential=None):
        (self.shipped / name).write_bytes(make_png(credential=credential))

    def test_steady_state_is_green_and_means_something(self):
        self._write("a.png", FAKE_CREDENTIAL)
        self._write("plain.png")
        cc.write_pin(cc.scan(self.shipped))
        self.assertEqual(cc.audit(), 0)

    def test_losing_a_credential_fails(self):
        self._write("a.png", FAKE_CREDENTIAL)
        cc.write_pin(cc.scan(self.shipped))
        self._write("a.png")  # re-encoded without the chunk
        self.assertEqual(cc.audit(), 1)

    def test_gaining_a_credential_fails_as_a_stale_pin(self):
        self._write("a.png", FAKE_CREDENTIAL)
        cc.write_pin(cc.scan(self.shipped))
        self._write("b.png", FAKE_CREDENTIAL)
        self.assertEqual(cc.audit(), 1)

    def test_replacing_a_credential_fails(self):
        self._write("a.png", FAKE_CREDENTIAL)
        cc.write_pin(cc.scan(self.shipped))
        self._write("a.png", FAKE_CREDENTIAL + b"different manifest bytes")
        self.assertEqual(cc.audit(), 1)

    def test_absent_pin_fails_rather_than_passing_vacuously(self):
        self._write("a.png", FAKE_CREDENTIAL)
        self.assertEqual(cc.audit(), 1)

    def test_deleting_an_uncredentialed_file_is_not_drift(self):
        """Only credentialed images are pinned, so ordinary churn must stay quiet."""
        self._write("a.png", FAKE_CREDENTIAL)
        self._write("noise.png")
        cc.write_pin(cc.scan(self.shipped))
        (self.shipped / "noise.png").unlink()
        self.assertEqual(cc.audit(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
