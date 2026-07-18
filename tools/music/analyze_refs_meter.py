"""Profile reference tracks into compositional seeds.

Usage:
    python tools/music/analyze_refs.py tools/music/ref_local/<file> [more files]

Writes one JSON per input to tools/music/profiles/<stem>.json with:
    - duration, tempo (beat-tracked) and inter-beat stats
    - key estimate (Krumhansl-Schmuckler correlation on mean chroma)
    - meter hint: contrast score for grouping beats in 2..9 (higher = likelier
      downbeat period), plus the beat-position accent profile for the winner
    - structure: segment boundary timestamps (agglomerative on chroma+mfcc)
    - dynamics: coarse RMS arc (16 bins over the track)

Needs: pip install librosa  (ffmpeg on PATH for mp3/wma decode).
Profiles are seeds for composing, not ground truth -- trust ears first.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROFILE_DIR = Path(__file__).parent / "profiles"

# Krumhansl-Kessler key profiles (major, minor)
KS_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_key(chroma_mean: np.ndarray) -> dict:
    scores = []
    for shift in range(12):
        rolled = np.roll(chroma_mean, -shift)
        scores.append((float(np.corrcoef(rolled, KS_MAJOR)[0, 1]), shift, "major"))
        scores.append((float(np.corrcoef(rolled, KS_MINOR)[0, 1]), shift, "minor"))
    scores.sort(reverse=True)
    best, second = scores[0], scores[1]
    return {
        "best": f"{PITCH_NAMES[best[1]]} {best[2]}",
        "confidence": round(best[0], 3),
        "second": f"{PITCH_NAMES[second[1]]} {second[2]}",
        "second_confidence": round(second[0], 3),
    }


def meter_hint(onset_env: np.ndarray, beat_frames: np.ndarray) -> dict:
    """Fold per-beat onset strength into candidate group sizes.

    A real downbeat period shows high contrast between strong and weak beat
    positions; report contrast per candidate and the winner's accent profile.
    """
    if len(beat_frames) < 24:
        return {"note": "too few beats for a meter hint"}
    beat_strength = onset_env[np.clip(beat_frames, 0, len(onset_env) - 1)]
    beat_strength = beat_strength / (beat_strength.max() + 1e-9)
    contrasts = {}
    profiles = {}
    for group in range(2, 10):
        usable = (len(beat_strength) // group) * group
        folded = beat_strength[:usable].reshape(-1, group)
        positions = folded.mean(axis=0)
        contrasts[group] = round(float(positions.std()), 4)
        profiles[group] = [round(float(p), 3) for p in positions]
    winner = max(contrasts, key=contrasts.get)
    return {
        "contrast_by_group": contrasts,
        "likely_beats_per_bar": winner,
        "winner_accent_profile": profiles[winner],
    }


def analyze(path: Path) -> dict:
    import librosa

    y, sr = librosa.load(path, sr=22050, mono=True)
    duration = float(len(y) / sr)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    ibis = np.diff(beat_times)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key = estimate_key(chroma.mean(axis=1))

    # structure: beat-synced features, agglomerative segmentation
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    n_feat_frames = min(chroma.shape[1], mfcc.shape[1])
    sync_frames = np.clip(beat_frames, 0, n_feat_frames - 1)
    feats = np.vstack(
        [
            librosa.util.sync(chroma[:, :n_feat_frames], sync_frames),
            librosa.util.sync(mfcc[:, :n_feat_frames], sync_frames),
        ]
    )
    n_segments = max(4, min(16, int(duration // 25)))
    seg_bounds = []
    if feats.shape[1] > n_segments * 2:
        bound_beats = librosa.segment.agglomerative(feats, n_segments)
        bound_beats = np.clip(bound_beats, 0, len(beat_times) - 1)
        seg_bounds = [round(float(beat_times[b]), 2) for b in bound_beats]

    # dynamics arc: 16 coarse RMS bins
    rms = librosa.feature.rms(y=y)[0]
    bins = np.array_split(rms, 16)
    arc = [round(float(b.mean()), 4) for b in bins]

    return {
        "file": path.name,
        "duration_sec": round(duration, 1),
        "tempo_bpm": round(tempo, 1),
        "inter_beat_sec": {
            "median": round(float(np.median(ibis)), 3) if len(ibis) else None,
            "std": round(float(np.std(ibis)), 3) if len(ibis) else None,
        },
        "key": key,
        "meter_hint": meter_hint(onset_env, beat_frames),
        "segment_boundaries_sec": seg_bounds,
        "rms_arc_16bins": arc,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    PROFILE_DIR.mkdir(exist_ok=True)
    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        print(f"analyzing: {path.name} ...", flush=True)
        try:
            profile = analyze(path)
        except Exception as exc:  # decode failures on odd codecs etc.
            print(f"  FAILED: {exc}")
            continue
        out = PROFILE_DIR / (path.stem + ".json")
        out.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        print(f"  -> {out}")
        print(
            f"  tempo ~{profile['tempo_bpm']} bpm, key {profile['key']['best']}, "
            f"meter hint {profile['meter_hint'].get('likely_beats_per_bar')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
