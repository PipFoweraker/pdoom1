#!/usr/bin/env python3
"""Transcribe a recording to timestamped text, offline, and optionally join it to the review log.

Layer: OBSERVE

WHY THIS EXISTS
---------------
On 2026-08-15 this seat wrote that 33 minutes of narrated art-review recording
was "the densest unread source available" and that "no tool in the estate
currently can" read it. Pip's reply, 2026-08-17:

    "can't we convert the audio out of the file using some extraction tool and
     just run that with timestamps?"

Yes. The claim was wrong -- it was made about LOCAL tooling without checking
what was installed, and `whisper` was already on this machine. Recorded here
because the failure mode (asserting a capability gap from memory instead of a
command) is the one this estate keeps paying for.

OFFLINE BY DEFAULT, DELIBERATELY
--------------------------------
Transcription runs through local `openai-whisper`. No audio leaves the machine.
That is not incidental: these recordings are screen captures of a working
session, and the 2026-08-14 one drifts into unrelated personal browsing after
about minute 22. A tool that uploaded whole recordings by default would be the
wrong shape regardless of cost. Use `--window` to transcribe only the part you
mean.

CROSS-MACHINE (Pip's newpc + the Debian laptop)
-----------------------------------------------
ffmpeg is located via PATH first, then a short list of known install locations
per platform, so this runs on both without editing. Whisper model files download
once to ~/.cache/whisper and are reused.

MEASURED 2026-08-17 on Pip's desktop (CPU-only torch 2.13, no CUDA):
21m10s of 16 kHz mono audio, model `small.en` -> 4m03s wall, i.e. **~5x
realtime**, plus a one-off 461 MB model download. An earlier estimate in this
docstring said 0.5-1.5x realtime; that was a guess and it was wrong by about
4x in the pessimistic direction. Drop to `base.en` on the laptop only if it is
actually slow there -- measure before assuming.

DO NOT REACH FOR A BIGGER MODEL WHEN A TRANSCRIPT READS BADLY
--------------------------------------------------------------
This tool has NO voice-activity detection, and the estate has already measured
what that costs. `coordination/PROTOCOL_UPDATE_2026-08-10_transcription-vad.md`,
on a real memo with a 58-second verified-silent stretch:

    with `large-v3 --beam 5` and no VAD, the instruction "merge PR295"
    transcribed as "merge PR 219. 5" -- not dropped, REWRITTEN into a plausible,
    differently-numbered, still-actionable instruction. `small.en` got it right.

    "a stronger language model fills dead air more convincingly. Model size is
     not monotonic in trustworthiness."

So `small.en` is the default here deliberately, and an earlier version of this
seat's advice -- "switch to medium.en if the room track reads rough" -- was
backwards and is withdrawn.

For anything with real silence in it (room mics, long pauses), prefer
`coordination/tools/capture/capture_transcribe.py`, which runs faster-whisper
with VAD on by default. See
`coordination/PROTOCOL_UPDATE_2026-08-21_two-transcription-tools.md` for the
open question of whether this tool should keep transcribing at all.

THE JOIN IS THE POINT
---------------------
Audio alone is a transcript. Audio plus `--align-log` is a record of what was
SAID while a specific asset was being judged: each transcript segment is mapped
to wall-clock and matched against `tools/art_review/review_log.jsonl`. The
2026-08-14 recording covers 495 of 506 logged decisions, so nearly every
judgement that night has narration attached to it.

Usage:
  # transcribe a window of a screen recording
  python tools/transcribe.py "G:/012 OBS Outputs/2026-08-14_22-03-05.mp4" \\
      --window 0:50-22:00 --model small.en --out-dir "G:/012 OBS Outputs/pdoom1-media-library"

  # same, and join every segment to the review decisions it overlaps
  python tools/transcribe.py <file> --window 0:50-22:00 \\
      --align-log --recording-start "2026-08-14T22:03:05" --utc-offset 10

  # already have a wav
  python tools/transcribe.py audio.wav --model base.en
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART_REVIEW = REPO / "tools" / "art_review"


def review_log_for(reviewer: str | None) -> Path:
    """Whose decisions to align against.

    The default reviewer keeps the historical unsuffixed filename; anyone else
    has their own. Hardcoding the default would silently align a GUEST's speech
    against the OWNER's decisions -- every segment would find a match, the output
    would look complete, and every attribution in it would be wrong. That is the
    failure this whole estate keeps paying for, so the reviewer is explicit.
    """
    if not reviewer or reviewer.lower() == "pip":
        return ART_REVIEW / "review_log.jsonl"
    safe = re.sub(r"[^a-z0-9_-]+", "-", reviewer.lower()).strip("-")
    return ART_REVIEW / f"review_log.{safe}.jsonl"


AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus"}

# Checked in order after PATH. Kept short and explicit rather than globbing the
# filesystem: a wrong ffmpeg found by a wide search is worse than a clear error.
FFMPEG_CANDIDATES = [
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "ffmpeg-8.1.2-full_build/bin/ffmpeg.exe",
    Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
    Path("/usr/bin/ffmpeg"),
    Path("/usr/local/bin/ffmpeg"),
    Path("/opt/homebrew/bin/ffmpeg"),
]


def find_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for cand in FFMPEG_CANDIDATES:
        try:
            if cand.is_file():
                return str(cand)
        except OSError:
            continue
    sys.exit(
        "ffmpeg not found. Install it (Debian: apt install ffmpeg; "
        "Windows: winget install Gyan.FFmpeg) or put it on PATH."
    )


def parse_clock(text: str) -> float:
    """'93', '1:33' or '1:02:03' -> seconds."""
    parts = text.strip().split(":")
    if not all(p.replace(".", "", 1).isdigit() for p in parts):
        raise ValueError(f"not a timestamp: {text!r}")
    total = 0.0
    for part in parts:
        total = total * 60 + float(part)
    return total


def parse_window(spec: str) -> tuple[float, float]:
    if "-" not in spec:
        raise ValueError("window must look like START-END, e.g. 0:50-22:00")
    a, b = spec.split("-", 1)
    start, end = parse_clock(a), parse_clock(b)
    if end <= start:
        raise ValueError(f"window end ({end}s) must be after start ({start}s)")
    return start, end


def hhmmss(seconds: float) -> str:
    s = int(seconds)
    return (
        f"{s // 3600:d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        if s >= 3600
        else f"{s // 60:d}:{s % 60:02d}"
    )


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def extract_audio(src: Path, dest: Path, window: tuple[float, float] | None) -> Path:
    """16 kHz mono PCM -- what whisper resamples to anyway, so no quality is lost."""
    ffmpeg = find_ffmpeg()
    cmd = [ffmpeg, "-y", "-v", "error"]
    if window:
        # -ss before -i seeks by keyframe and is far faster on a long file.
        cmd += ["-ss", str(window[0]), "-to", str(window[1])]
    cmd += ["-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dest)]
    print(f"extracting audio -> {dest.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not dest.exists():
        sys.exit(f"ffmpeg failed:\n{result.stderr[:1500]}")
    mb = dest.stat().st_size / 1e6
    print(f"  {mb:.1f} MB")
    return dest


def transcribe(audio: Path, model_name: str) -> dict:
    try:
        import whisper
    except ImportError:
        sys.exit(
            "openai-whisper not installed.\n"
            "  pip install -U openai-whisper\n"
            "It needs ffmpeg too, which this tool has already located."
        )
    print(f"loading model {model_name} (first run downloads to ~/.cache/whisper) ...")
    model = whisper.load_model(model_name)
    # Measured, not guessed: small.en did 21m10s of audio in 4m03s on this CPU.
    # The figure printed here was 0.5-1.5x realtime until 2026-08-17, which was a
    # guess and wrong by ~4x in the discouraging direction -- the kind of number
    # that makes someone not bother running the tool.
    print(f"transcribing with {model_name} -- CPU runs ~5x realtime, so this is minutes ...")
    return model.transcribe(str(audio), verbose=False, word_timestamps=False)


def recording_epoch(recording_start: str, utc_offset_hours: float, window_start: float) -> float:
    """Epoch seconds of the first sample in the extracted window.

    Every datetime here is made TIMEZONE-AWARE before any arithmetic. Naive
    `.timestamp()` silently interprets its input as the MACHINE's local time,
    so the obvious version of this function is correct on Pip's AEST desktop
    and wrong by hours on the Debian laptop -- with no error, just an alignment
    that quietly points at the wrong decisions.
    """
    tz = dt.timezone(dt.timedelta(hours=utc_offset_hours))
    start = dt.datetime.fromisoformat(recording_start)
    if start.tzinfo is None:
        start = start.replace(tzinfo=tz)
    return start.timestamp() + window_start


def load_review_events(base_epoch: float, log_path: Path) -> list[tuple[float, dict]]:
    """Review-log events as (seconds-into-the-window, event).

    Log timestamps are ISO with an explicit UTC offset; where one is missing,
    UTC is assumed, because that is what the review server writes.
    """
    if not log_path.exists():
        print(f"  NOTE: {log_path} absent -- no alignment")
        return []
    out = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("ts")
        if not ts:
            continue
        when = dt.datetime.fromisoformat(ts)
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt.timezone.utc)
        out.append((when.timestamp() - base_epoch, e))
    return out


def write_outputs(result: dict, stem: Path, aligned: list | None) -> list[Path]:
    segments = result.get("segments", [])
    written = []

    js = stem.with_suffix(".json")
    js.write_text(
        json.dumps(
            {
                "text": result.get("text", ""),
                "language": result.get("language"),
                "segments": [
                    {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                    for s in segments
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="",
    )
    written.append(js)

    srt = stem.with_suffix(".srt")
    lines = []
    for i, s in enumerate(segments, 1):
        lines += [str(i), f"{srt_time(s['start'])} --> {srt_time(s['end'])}", s["text"].strip(), ""]
    srt.write_text("\n".join(lines), encoding="utf-8", newline="")
    written.append(srt)

    md = stem.with_suffix(".md")
    body = [
        f"# Transcript -- {stem.name}",
        "",
        "> GENERATED by `tools/transcribe.py` (local whisper, offline).",
        "> Timestamps are offsets into the extracted window, not the source file.",
        "",
    ]
    for s in segments:
        body.append(f"**{hhmmss(s['start'])}**  {s['text'].strip()}")
    md.write_text("\n".join(body) + "\n", encoding="utf-8", newline="")
    written.append(md)

    if aligned is not None:
        al = stem.parent / (stem.name + "_aligned.md")
        rows = [
            f"# Transcript joined to review decisions -- {stem.name}",
            "",
            "> GENERATED by `tools/transcribe.py --align-log`. Each block is what was",
            "> being SAID while those assets were being judged. Alignment is by",
            "> wall-clock arithmetic, not by content -- verify before quoting.",
            "",
        ]
        for seg, events in aligned:
            if not events:
                continue
            rows.append(f"### {hhmmss(seg['start'])}  {seg['text'].strip()}")
            rows.append("")
            for e in events:
                nx = e.get("next") or {}
                note = (nx.get("note") or "").strip()
                rows.append(
                    f"- `{nx.get('verdict')}` {e.get('asset','')}" + (f" -- {note}" if note else "")
                )
            rows.append("")
        al.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="")
        written.append(al)

    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="video or audio file")
    ap.add_argument("--window", help="START-END within the source, e.g. 0:50-22:00")
    ap.add_argument("--model", default="small.en", help="whisper model (default: small.en)")
    ap.add_argument("--out-dir", type=Path, help="default: alongside the source")
    ap.add_argument("--keep-audio", action="store_true", help="keep the extracted wav")
    ap.add_argument("--align-log", action="store_true", help="join to a reviewer's decision log")
    ap.add_argument(
        "--reviewer",
        help=(
            "WHOSE decisions to align against (default: pip). Get this wrong and every "
            "segment still finds a match -- the output looks complete and is wrong."
        ),
    )
    ap.add_argument(
        "--recording-start", help="local start of the SOURCE, ISO e.g. 2026-08-14T22:03:05"
    )
    ap.add_argument(
        "--utc-offset", type=float, default=10.0, help="hours ahead of UTC (default 10, AEST)"
    )
    args = ap.parse_args()

    if not args.source.exists():
        sys.exit(f"no such file: {args.source}")
    out_dir = args.out_dir or args.source.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    window = parse_window(args.window) if args.window else None
    stem_name = args.source.stem + (f"_{int(window[0])}-{int(window[1])}" if window else "")
    stem = out_dir / stem_name

    if args.source.suffix.lower() in AUDIO_SUFFIXES and not window:
        audio, temp = args.source, False
    else:
        audio = extract_audio(args.source, stem.with_suffix(".wav"), window)
        temp = not args.keep_audio

    result = transcribe(audio, args.model)
    segments = result.get("segments", [])
    print(f"  {len(segments)} segment(s)")

    aligned = None
    if args.align_log:
        if not args.recording_start:
            sys.exit("--align-log needs --recording-start (local ISO time of the SOURCE file)")
        base = recording_epoch(args.recording_start, args.utc_offset, window[0] if window else 0.0)
        log_path = review_log_for(args.reviewer)
        print(f"  aligning against {log_path.name}")
        events = load_review_events(base, log_path)
        aligned = []
        for s in segments:
            hits = [e for rel, e in events if s["start"] <= rel <= s["end"]]
            aligned.append((s, hits))
        matched = sum(1 for _s, h in aligned if h)
        print(f"  {matched} of {len(segments)} segment(s) overlap a logged decision")

    written = write_outputs(result, stem, aligned)
    if temp and audio.exists() and audio != args.source:
        audio.unlink()
    print("\nwrote:")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
