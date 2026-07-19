"""Turn raw strudel captures into game-ready looping ogg stems.

For each tier take: find the musical start (librosa onset), cut an exact
bar-boundary loop (duration computed from the patch bpm -- the WebAudio
clock is sample-accurate so N bars is N*4*60/bpm seconds exactly), bake
the reverb spill of the loop tail into the loop head (1 s equal-power
crossfade -- the file boundary IS the loop point, per the drop-in kit),
then two-pass ffmpeg loudnorm to -16 LUFS and encode ogg vorbis 44.1k.

Loose takes (defeat/trailer/archive -- not hard-looped by the engine) just
get silence-trimmed, faded, normalized, encoded.

Usage:
  python tools/music/process_captures.py           # process everything found
  python tools/music/process_captures.py m0 m4     # just named takes

Outputs to tools/music/captures/game/<slot>.ogg + a report to stdout.
"""

import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "captures"
OUT = CAP / "game"
SR = 44100
XFADE_S = 1.0

# take stem -> (bpm, bars, out name). ML/AI-safety pun register per kit.
LOOP_TAKES = {
    "capture_2026-07-18_jukebox_m0": (104, 32, "unit_tests_passing"),
    "capture_2026-07-18_jukebox_m0s": (92, 32, "unit_tests_passing_first_light"),
    "capture_2026-07-18_jukebox_m1": (104, 16, "distribution_shift"),
    "capture_2026-07-18_jukebox_m2": (104, 32, "proxy_gaming"),
    "capture_2026-07-18_jukebox_m3": (96, 16, "mesa_optimizer"),
    "capture_2026-07-18_jukebox_m4": (96, 16, "treacherous_turn"),
    "capture_2026-07-18_jukebox_m4t": (96, 16, "treacherous_turn_train"),
    "capture_2026-07-18_jukebox_win": (66, 16, "the_off_switch_worked"),
    "capture_2026-07-18_jukebox_menu": (60, 16, "checkpoint_saved"),
}
# m4r: four 4-bar rounds at 96 bpm sped 1/1.06/1.13/1.21 -- computed below.
M4R_STEM = "capture_2026-07-18_jukebox_m4r"
M4R_LEN = sum(10.0 / s for s in (1.0, 1.06, 1.13, 1.21))

LOOSE_TAKES = {
    "capture_2026-07-18_trudge_welcome_v0_1": "out_of_distribution_trudge",
    "capture_2026-07-18_trailer_v0_4": "trailer_trudge_v0_4",
    "capture_2026-07-18_zen_standoff_v0_1": "zen_standoff",
    "capture_2026-07-18_drifting_seven_v0_1": "drifting_seven",
    "capture_2026-07-18_dirge_variations_v0_1": "dirge_variations",
}


def musical_start(y):
    on = librosa.onset.onset_detect(y=librosa.to_mono(y), sr=SR, units="samples", backtrack=True)
    if len(on) == 0:
        # fall back to first sample above -40 dBFS
        idx = np.argmax(np.abs(librosa.to_mono(y)) > 0.01)
        return int(idx)
    return max(0, int(on[0]) - SR // 100)  # 10 ms pad


def bake_loop(y, start, loop_len_s):
    n = int(round(loop_len_s * SR))
    x = int(XFADE_S * SR)
    if start + n + x > y.shape[-1]:
        raise ValueError(f"capture too short: need {start + n + x} samples, " f"have {y.shape[-1]}")
    loop = np.copy(y[..., start : start + n])
    tail = y[..., start + n : start + n + x]
    t = np.linspace(0, np.pi / 2, x)
    fade_in, fade_out = np.sin(t) ** 2, np.cos(t) ** 2
    loop[..., :x] = loop[..., :x] * fade_in + tail * fade_out
    return loop


def loudnorm_ogg(wav_path, ogg_path):
    p1 = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(wav_path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    err = p1.stderr
    stats = json.loads(err[err.rindex("{") : err.rindex("}") + 1])
    ln = (
        "loudnorm=I=-16:TP=-1.5:LRA=11:linear=true"
        f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
        f":measured_LRA={stats['input_lra']}"
        f":measured_thresh={stats['input_thresh']}"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(wav_path),
            "-af",
            ln,
            "-ar",
            "44100",
            "-c:a",
            "libvorbis",
            "-q:a",
            "6",
            str(ogg_path),
        ],
        check=True,
    )
    return stats["input_i"]


def process_loop(stem, bpm, bars, name):
    src = CAP / f"{stem}.wav"
    if not src.exists():
        print(f"[skip] {stem} (no wav yet)")
        return
    y, _ = librosa.load(src, sr=SR, mono=False)
    if y.ndim == 1:
        y = y[np.newaxis, :]
    loop_len = bars * 4 * 60.0 / bpm if bpm else bars  # bars==seconds if bpm None
    start = musical_start(y)
    loop = bake_loop(y, start, loop_len)
    tmp = OUT / f"{name}.wav"
    sf.write(tmp, loop.T, SR)
    lufs = loudnorm_ogg(tmp, OUT / f"{name}.ogg")
    tmp.unlink()
    print(
        f"[loop] {name}.ogg  {loop_len:.3f}s ({bars} bars @ {bpm})"
        f"  start={start / SR:.3f}s  measured {lufs} LUFS -> -16"
    )


def process_m4r():
    src = CAP / f"{M4R_STEM}.wav"
    if not src.exists():
        print(f"[skip] {M4R_STEM} (no wav yet)")
        return
    y, _ = librosa.load(src, sr=SR, mono=False)
    if y.ndim == 1:
        y = y[np.newaxis, :]
    start = musical_start(y)
    loop = bake_loop(y, start, M4R_LEN)
    tmp = OUT / "treacherous_turn_another_round.wav"
    sf.write(tmp, loop.T, SR)
    lufs = loudnorm_ogg(tmp, OUT / "treacherous_turn_another_round.ogg")
    tmp.unlink()
    print(
        f"[loop] treacherous_turn_another_round.ogg  {M4R_LEN:.3f}s"
        f"  start={start / SR:.3f}s  measured {lufs} LUFS -> -16"
    )


def process_loose(stem, name):
    src = CAP / f"{stem}.wav"
    if not src.exists():
        print(f"[skip] {stem} (no wav yet)")
        return
    y, _ = librosa.load(src, sr=SR, mono=False)
    if y.ndim == 1:
        y = y[np.newaxis, :]
    start = musical_start(y)
    trimmed = np.copy(y[..., start:])
    fade = int(0.01 * SR)
    trimmed[..., :fade] *= np.linspace(0, 1, fade)
    trimmed[..., -SR:] *= np.linspace(1, 0, SR)  # 1 s fade-out at hard end
    tmp = OUT / f"{name}.wav"
    sf.write(tmp, trimmed.T, SR)
    lufs = loudnorm_ogg(tmp, OUT / f"{name}.ogg")
    tmp.unlink()
    print(f"[full] {name}.ogg  {trimmed.shape[-1] / SR:.1f}s" f"  measured {lufs} LUFS -> -16")


def main():
    only = set(sys.argv[1:])

    def want(stem):
        return not only or any(k in stem for k in only)

    OUT.mkdir(parents=True, exist_ok=True)
    for stem, (bpm, bars, name) in LOOP_TAKES.items():
        if want(stem):
            process_loop(stem, bpm, bars, name)
    if want(M4R_STEM):
        process_m4r()
    for stem, name in LOOSE_TAKES.items():
        if want(stem):
            process_loose(stem, name)


if __name__ == "__main__":
    main()
