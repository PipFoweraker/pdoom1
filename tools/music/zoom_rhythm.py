"""Zoom into a time window of a track and extract its rhythm as notation.

Built for decoding the Drifting Houses leitmotif ("dun-dundun-dun-DUN...")
once Pip supplies a timestamp -- turns complex humming into a grid.

Usage:
    python tools/music/zoom_rhythm.py "<audio file>" <start_sec> <end_sec> [subdiv]

    subdiv = grid steps per beat (default 4 = sixteenth grid; use 3 for triplets)

Output: local tempo in the window, onset times, an ASCII grid per beat, and a
suggested Strudel mini-notation string ("x" = onset, "~" = rest) you can paste
into a drum pattern. Accents (loud onsets) shown as "X".

Needs: pip install librosa
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__)
        return 1
    path = Path(argv[1])
    start, end = float(argv[2]), float(argv[3])
    subdiv = int(argv[4]) if len(argv) > 4 else 4

    import librosa

    y, sr = librosa.load(path, sr=22050, mono=True, offset=start, duration=end - start)
    if not len(y):
        print("empty window")
        return 1

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    strengths = onset_env[np.clip(onset_frames, 0, len(onset_env) - 1)]
    strengths = strengths / (strengths.max() + 1e-9)

    print(f"window {start:.2f}-{end:.2f}s of {path.name}")
    print(f"local tempo ~{tempo:.1f} bpm, {len(beat_times)} beats, " f"{len(onset_times)} onsets")
    print()
    print("onsets (sec into window, strength 0-9):")
    for t, s_ in zip(onset_times, strengths):
        print(f"  {t + start:7.2f}  ({t:5.2f} local)  {'#' * max(1, int(s_ * 9))}")

    if len(beat_times) < 2:
        print("too few beats for a grid")
        return 0

    # quantize onsets to a subdiv grid between consecutive beats
    print()
    print(f"grid ({subdiv} per beat; x=onset, X=strong, .=rest, | = beat):")
    rows = []
    strudel_cells = []
    for bi in range(len(beat_times) - 1):
        b0, b1 = beat_times[bi], beat_times[bi + 1]
        cell = ["."] * subdiv
        strudel = ["~"] * subdiv
        for t, s_ in zip(onset_times, strengths):
            if b0 <= t < b1:
                slot = min(subdiv - 1, int((t - b0) / (b1 - b0) * subdiv))
                cell[slot] = "X" if s_ > 0.6 else "x"
                strudel[slot] = "x"
        rows.append("".join(cell))
        strudel_cells.append(" ".join(strudel))
    for i in range(0, len(rows), 4):
        print("  |" + "|".join(rows[i : i + 4]) + "|")
    print()
    print("suggested Strudel skeleton (replace x with a drum sample name):")
    print('  s("' + " . ".join("[" + c + "]" for c in strudel_cells[:8]) + '")')
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
