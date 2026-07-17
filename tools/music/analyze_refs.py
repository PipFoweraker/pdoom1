#!/usr/bin/env python3
"""Reference-track analyzer for P(Doom)1 adaptive-music composition.

Turns a personal reference MP3 (Pip's aesthetic north stars -- see
docs/audio/REFERENCE_TRACKS.md) into a NUMERIC profile a language model can
compose Strudel / SuperCollider patterns against: tempo + beat grid, estimated
key/mode, section boundaries, a rhythmic-intensity envelope (RMS + onset
density over time), a coarse loudness arc, and a chroma/tonal summary.

The audio files are personal / copyrighted and MUST stay local (gitignored --
put them in tools/music/ref_local/). Only the emitted NUMBERS are safe to
keep; they carry no rights baggage. See tools/music/README.md.

Usage:
    python tools/music/analyze_refs.py path/to/track.mp3 [more.mp3 ...]

Output:
    tools/music/profiles/<trackname>.json  (one per input track)

Dependency: librosa (heavy; intentionally NOT in requirements-dev.txt to keep
CI light). If it is missing this script prints the install line and exits
non-zero rather than crashing with a raw traceback.
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

# Krumhansl-Schmuckler key profiles (major / minor). Correlating the mean
# chroma against all 12 rotations of each picks the most likely tonal center.
# These are a de-facto standard; they name a TONAL CENTER, not a functional key
# (drone/modal material has no leading-tone cadence to disambiguate) -- treat
# the estimate as direction, matching the caveat in REFERENCE_TRACKS.md.
_KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
_PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# JSON schema version -- bump if the emitted structure changes so downstream
# (Fable / Strudel) consumers can detect stale profiles.
SCHEMA_VERSION = 1


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="analyze_refs.py",
        description=(
            "Analyze reference audio tracks into JSON compositional seeds "
            "(tempo, key, sections, intensity envelope, chroma) for the "
            "P(Doom)1 adaptive-music lab. See tools/music/README.md."
        ),
        epilog=(
            "Input MP3s are personal/copyrighted -- keep them in the "
            "gitignored tools/music/ref_local/ dir. Only the JSON profiles "
            "(numbers) are committed/shared."
        ),
    )
    parser.add_argument(
        "tracks",
        nargs="+",
        metavar="TRACK",
        help="one or more audio files (mp3/wav/flac/ogg) to analyze",
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles"),
        help="directory for the emitted <trackname>.json files " "(default: tools/music/profiles/)",
    )
    parser.add_argument(
        "--sr",
        type=int,
        default=22050,
        help="analysis sample rate in Hz (default: 22050; librosa default, "
        "plenty for tempo/chroma/structure)",
    )
    parser.add_argument(
        "--segments",
        type=int,
        default=8,
        help="target number of structural sections to detect (default: 8)",
    )
    parser.add_argument(
        "--env-buckets",
        type=int,
        default=32,
        help="number of time buckets for the intensity envelope arrays "
        "(default: 32; keeps JSON compact)",
    )
    return parser.parse_args(argv)


def _require_librosa():
    """Import librosa lazily so --help works without it. Exit cleanly if absent."""
    try:
        import librosa  # noqa: F401
        import numpy  # noqa: F401
    except ImportError as exc:
        sys.stderr.write(
            "\n[analyze_refs] Missing dependency: this tool needs 'librosa' "
            "(which pulls in numpy/scipy/numba/soundfile).\n"
            "  Install it into your local/dev Python (it is intentionally NOT "
            "in requirements-dev.txt to keep CI light):\n\n"
            "      pip install librosa\n\n"
            "  On Windows you may also need a working ffmpeg on PATH for MP3 "
            "decoding (audioread/soundfile backend).\n"
            "  Underlying import error: %s\n" % exc
        )
        sys.exit(2)


def _estimate_key(chroma_mean):
    """Krumhansl-Schmuckler: return (tonic, mode, correlation, ranked list)."""
    import numpy as np

    vec = np.asarray(chroma_mean, dtype=float)
    if vec.sum() <= 0:
        return {"tonic": None, "mode": None, "correlation": 0.0, "candidates": []}
    vec = vec - vec.mean()
    major = np.asarray(_KS_MAJOR) - np.mean(_KS_MAJOR)
    minor = np.asarray(_KS_MINOR) - np.mean(_KS_MINOR)

    def _corr(a, b):
        denom = math.sqrt(float(np.dot(a, a)) * float(np.dot(b, b)))
        return float(np.dot(a, b) / denom) if denom > 0 else 0.0

    scored = []
    for i in range(12):
        rot = np.roll(vec, -i)
        scored.append((_PITCH_CLASSES[i], "major", _corr(rot, major)))
        scored.append((_PITCH_CLASSES[i], "minor", _corr(rot, minor)))
    scored.sort(key=lambda t: t[2], reverse=True)
    best = scored[0]
    candidates = [{"tonic": t, "mode": m, "correlation": round(c, 4)} for (t, m, c) in scored[:4]]
    return {
        "tonic": best[0],
        "mode": best[1],
        "correlation": round(best[2], 4),
        "candidates": candidates,
    }


def _bucket(values, n_buckets):
    """Down-sample a 1-D array to n_buckets means (compact envelope for JSON)."""
    import numpy as np

    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return []
    if values.size <= n_buckets:
        return [round(float(v), 5) for v in values]
    edges = np.linspace(0, values.size, n_buckets + 1, dtype=int)
    out = []
    for i in range(n_buckets):
        seg = values[edges[i] : edges[i + 1]]
        out.append(round(float(seg.mean()) if seg.size else 0.0, 5))
    return out


def _analyze(path, args):
    """Compute the full numeric profile for one track. Returns a dict."""
    import librosa
    import numpy as np

    y, sr = librosa.load(path, sr=args.sr, mono=True)
    duration = float(librosa.get_duration(y=y, sr=sr))
    hop = 512

    # --- Tempo + beat grid ---
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop).tolist()

    # --- Onset events (rhythmic density) ---
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop)
    onset_density = float(len(onset_times) / duration) if duration > 0 else 0.0

    # --- RMS + onset-strength envelopes over time (bucketed) ---
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    rms_db = librosa.amplitude_to_db(rms + 1e-10, ref=np.max(rms) + 1e-10)
    # onset events per env bucket (rhythmic-intensity, not just amplitude)
    n_frames = onset_env.shape[0]
    onset_hist = np.zeros(n_frames)
    for f in onset_frames:
        if 0 <= f < n_frames:
            onset_hist[f] = 1.0

    # --- Chroma / tonal summary ---
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    chroma_mean = chroma.mean(axis=1)
    chroma_norm = (
        (chroma_mean / chroma_mean.sum()).tolist()
        if chroma_mean.sum() > 0
        else chroma_mean.tolist()
    )
    top_idx = list(np.argsort(chroma_mean)[::-1][:3])
    top_pitches = [_PITCH_CLASSES[int(i)] for i in top_idx]
    key = _estimate_key(chroma_mean)

    # --- Spectral brightness (centroid), for the "unsettling tilt" budget ---
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]

    # --- Section boundaries (structural segmentation) ---
    # Agglomerative clustering over stacked chroma + MFCC gives robust,
    # tempo-agnostic section edges (novelty-style) without hand-tuning.
    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13)
        stack = np.vstack(
            [librosa.util.normalize(chroma, axis=1), librosa.util.normalize(mfcc, axis=1)]
        )
        k = max(2, min(int(args.segments), stack.shape[1] - 1))
        bound_frames = librosa.segment.agglomerative(stack, k)
        bound_times = librosa.frames_to_time(bound_frames, sr=sr, hop_length=hop).tolist()
        # ensure the final boundary reaches the end of the track
        if not bound_times or bound_times[-1] < duration - 1.0:
            bound_times.append(round(duration, 3))
        bound_times = [round(float(t), 3) for t in bound_times]
    except Exception as exc:  # segmentation is best-effort, never fatal
        bound_times = [0.0, round(duration, 3)]
        sys.stderr.write(
            "[analyze_refs] segmentation fell back for %s: %s\n" % (os.path.basename(path), exc)
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "source_basename": os.path.basename(path),
        "analyzed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "analysis_sr": sr,
        "duration_sec": round(duration, 3),
        "tempo": {
            "bpm": round(tempo, 2),
            "bpm_half": round(tempo / 2.0, 2),
            "bpm_double": round(tempo * 2.0, 2),
            "beat_count": len(beat_times),
            "beat_times_sec": [round(float(t), 3) for t in beat_times],
            "note": (
                "BPM is a dominant-periodicity estimate; it can alias to "
                "2x/4x of the felt tempo. bpm_half/bpm_double given for the "
                "'ritual heartbeat' vs 'pattern' lanes (see REFERENCE_TRACKS.md)."
            ),
        },
        "key": key,
        "tonal": {
            "chroma_mean_normalized": [round(float(c), 5) for c in chroma_norm],
            "pitch_class_order": _PITCH_CLASSES,
            "top_pitch_classes": top_pitches,
            "note": (
                "Tonal CENTER, not a functional key. Modal/drone material "
                "(C/D center, fifth + flat-7) is the target home per "
                "REFERENCE_TRACKS.md."
            ),
        },
        "rhythm": {
            "onset_count": int(len(onset_times)),
            "onset_density_per_sec": round(onset_density, 3),
            "onset_times_sec": [round(float(t), 3) for t in onset_times.tolist()],
        },
        "intensity_envelope": {
            "buckets": int(args.env_buckets),
            "rms": _bucket(rms, args.env_buckets),
            "rms_db_rel_peak": _bucket(rms_db, args.env_buckets),
            "onset_strength": _bucket(onset_env, args.env_buckets),
            "onset_density": _bucket(onset_hist, args.env_buckets),
            "spectral_centroid_hz": _bucket(centroid, args.env_buckets),
            "note": (
                "Arrays are time-ordered, evenly spaced across the whole "
                "track (bucket count above). rms_db_rel_peak is the loudness "
                "ARC (dB relative to peak) used to spot ritual build-release."
            ),
        },
        "sections": {
            "boundary_times_sec": bound_times,
            "count": max(0, len(bound_times) - 1),
            "note": "Agglomerative segmentation over chroma+MFCC (novelty-style).",
        },
        "spectral": {
            "centroid_hz_mean": round(float(np.mean(centroid)), 1),
            "low_energy_lt150hz_note": "not computed; use centroid as brightness proxy",
        },
    }


def main(argv=None):
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    _require_librosa()  # after arg parse so --help never needs librosa

    os.makedirs(args.out_dir, exist_ok=True)
    failures = 0
    written = []

    for path in args.tracks:
        if not os.path.isfile(path):
            sys.stderr.write("[analyze_refs] SKIP (not a file): %s\n" % path)
            failures += 1
            continue
        stem = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(args.out_dir, stem + ".json")
        try:
            print("[analyze_refs] analyzing: %s" % path)
            profile = _analyze(path, args)
            with open(out_path, "w", encoding="ascii") as fh:
                json.dump(profile, fh, indent=2, ensure_ascii=True)
                fh.write("\n")
            written.append(out_path)
            print(
                "[analyze_refs]   -> %s  (bpm=%.1f key=%s %s, %d sections)"
                % (
                    out_path,
                    profile["tempo"]["bpm"],
                    profile["key"]["tonic"],
                    profile["key"]["mode"],
                    profile["sections"]["count"],
                )
            )
        except Exception as exc:  # one bad file must not abort the batch
            sys.stderr.write("[analyze_refs] FAILED on %s: %s\n" % (path, exc))
            failures += 1

    print("[analyze_refs] done: %d profile(s) written, %d failure(s)." % (len(written), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
