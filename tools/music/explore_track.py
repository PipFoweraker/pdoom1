"""One-command track exploration: drop in any song, get a full analysis report.

The library builder for Pip's growing collection of explored referents.

Usage:
    python tools/music/explore_track.py "path/to/track.mp3" [--skip-demucs] [--whisper]

What it does:
    1. Profiles the full mix (tempo, key, meter hint, structure, dynamics)
       using analyze_refs_meter.py.
    2. Splits the track into drums/bass/vocals/other stems with Demucs
       (skipped with --skip-demucs, or if stems already exist). Stems land in
       tools/music/ref_local/stems/htdemucs/<track>/ -- gitignored, audio
       stays local.
    3. Re-profiles the ISOLATED DRUM stem and folds its onset energy into an
       averaged accent bar at the winning meter -- the rhythm skeleton.
    4. Optionally (--whisper) transcribes/translates the vocal stem.
    5. Writes a human-readable report + machine JSON to
       tools/music/library/<slug>/ (numbers only -- committable), and updates
       tools/music/library/INDEX.md.

Needs: pip install librosa demucs  (and openai-whisper for --whisper).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from analyze_refs_meter import analyze  # noqa: E402

STEMS_ROOT = HERE / "ref_local" / "stems"
LIBRARY = HERE / "library"
SPARK = " .:-=+*#%@"


def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def sparkline(values: list[float]) -> str:
    vmax = max(values) + 1e-9
    return "".join(SPARK[min(9, int(v / vmax * 9))] for v in values)


def run_demucs(track: Path) -> Path | None:
    out_dir = STEMS_ROOT / "htdemucs" / track.stem
    if (out_dir / "drums.wav").exists():
        print(f"stems already exist: {out_dir}")
        return out_dir
    print("running demucs (several minutes on CPU)...")
    res = subprocess.run(
        [sys.executable, "-m", "demucs", str(track), "-o", str(STEMS_ROOT)],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print("demucs failed:")
        print(res.stderr[-2000:])
        return None
    return out_dir if (out_dir / "drums.wav").exists() else None


def fold_accents(drums_wav: Path, bpm: float, beats_per_bar: int) -> list[float]:
    """Average the drum onset energy into one bar at the given meter (8th grid)."""
    import librosa

    y, sr = librosa.load(drums_wav, sr=22050, mono=True)
    env = librosa.onset.onset_strength(y=y, sr=sr)
    fps = sr / 512
    cyc = beats_per_bar * 60.0 / bpm
    slots = beats_per_bar * 2
    times = np.arange(len(env)) / fps
    best = None
    for ph in np.arange(0, cyc, cyc / (slots * 4)):
        pos = (((times - ph) % cyc) / cyc * slots).astype(int) % slots
        prof = np.zeros(slots)
        cnt = np.zeros(slots) + 1e-9
        np.add.at(prof, pos, env)
        np.add.at(cnt, pos, 1)
        prof /= cnt
        if best is None or prof.std() > best[0]:
            best = (prof.std(), prof)
    prof = best[1]
    return list(prof / (prof.max() + 1e-9))


def strudel_seed(accents: list[float], bpm: float, beats_per_bar: int) -> str:
    def voice(a: float) -> str:
        if a >= 0.9:
            return "lt"
        if a >= 0.65:
            return "mt"
        if a >= 0.45:
            return "hh"
        return "~"

    pat = " ".join(voice(a) for a in accents)
    return f"setcpm({bpm:.1f}/{beats_per_bar})\n" f's("{pat}").bank("RolandTR808")'


def run_whisper(vocals_wav: Path, out_dir: Path) -> str | None:
    print("running whisper on vocal stem...")
    res = subprocess.run(
        [
            "whisper",
            str(vocals_wav),
            "--task",
            "translate",
            "--model",
            "small",
            "--output_dir",
            str(out_dir),
            "--output_format",
            "txt",
            "--verbose",
            "False",
        ],
        capture_output=True,
        text=True,
    )
    txt = out_dir / (vocals_wav.stem + ".txt")
    if res.returncode == 0 and txt.exists():
        return txt.read_text(encoding="utf-8", errors="replace").strip()
    print("whisper failed or produced nothing")
    return None


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 1
    track = Path(args[0])
    if not track.exists():
        print(f"not found: {track}")
        return 1

    slug = slugify(track.stem)
    out = LIBRARY / slug
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] profiling full mix: {track.name}")
    mix = analyze(track)
    (out / "mix_profile.json").write_text(json.dumps(mix, indent=2) + "\n", encoding="utf-8")

    stems_dir = None
    if "--skip-demucs" not in flags:
        print("[2/4] separating stems")
        stems_dir = run_demucs(track)

    drum = None
    accents: list[float] = []
    meter = None
    if stems_dir:
        print("[3/4] profiling isolated drums + folding accent bar")
        drum = analyze(stems_dir / "drums.wav")
        (out / "drums_profile.json").write_text(json.dumps(drum, indent=2) + "\n", encoding="utf-8")
        meter = drum["meter_hint"].get("likely_beats_per_bar")
        if meter:
            accents = fold_accents(stems_dir / "drums.wav", drum["tempo_bpm"], meter)

    lyrics = None
    if "--whisper" in flags and stems_dir:
        lyrics = run_whisper(stems_dir / "vocals.wav", out)

    print("[4/4] writing report")
    lines = [
        f"# {track.stem}",
        "",
        f"Source file: `{track}` (audio stays local; this report is numbers only)",
        "",
        f"- Duration: {mix['duration_sec']}s",
        f"- Tempo (full mix): {mix['tempo_bpm']} bpm",
        f"- Key: {mix['key']['best']} (conf {mix['key']['confidence']}, "
        f"2nd: {mix['key']['second']})",
        f"- Loudness arc: `{sparkline(mix['rms_arc_16bins'])}`",
        f"- Segment boundaries (s): {mix['segment_boundaries_sec']}",
        "",
    ]
    if drum:
        lines += [
            "## Rhythm (from isolated drum stem)",
            "",
            f"- Drum-stem tempo: {drum['tempo_bpm']} bpm",
            f"- Likely meter: {meter} beats/bar "
            f"(contrasts: {drum['meter_hint'].get('contrast_by_group')})",
            "",
        ]
        if accents:
            lines += ["Accent bar (8th grid, folded over full track):", "```"]
            labels = []
            for b in range(meter):
                labels += [str(b + 1), "&"]
            for lab, a in zip(labels, accents):
                lines.append(f"  {lab:>2} {a:5.2f} {'#' * int(a * 40)}")
            lines += [
                "```",
                "",
                "Strudel seed:",
                "```",
                strudel_seed(accents, drum["tempo_bpm"], meter),
                "```",
                "",
            ]
    if lyrics is not None:
        lines += [
            "## Whisper on vocal stem (hallucination-prone -- verify!)",
            "",
            "```",
            lyrics[:4000],
            "```",
            "",
        ]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # index line
    LIBRARY.mkdir(exist_ok=True)
    index = LIBRARY / "INDEX.md"
    header = "# Explored-track library\n\n"
    entry = (
        f"- [{track.stem}]({slug}/report.md) -- {mix['tempo_bpm']} bpm, "
        f"{mix['key']['best']}" + (f", {meter}-beat bar" if meter else "") + "\n"
    )
    if index.exists():
        text = index.read_text(encoding="utf-8")
        text = "\n".join(row for row in text.splitlines() if f"]({slug}/" not in row) + "\n"
    else:
        text = header
    index.write_text(text.rstrip("\n") + "\n" + entry, encoding="utf-8")
    print(f"done -> {out / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
