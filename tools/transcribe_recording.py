#!/usr/bin/env python3
"""Turn a recording into a transcript.

Layer: OBSERVE
Invoked by: human

Written 2026-07-29 for a 34-minute conversation that was recorded as an mp4 with
a blank 4K video track -- 218 MB of file for about 12 MB of speech.

THE IDEA, in three steps:

  1. STRIP. ffmpeg throws away the video and downmixes the audio to 16 kHz mono.
     Not just to save space: speech-recognition models are trained on 16 kHz
     mono, so 48 kHz stereo is detail the model discards anyway. ~218 MB -> ~12 MB.

  2. CHECK. The transcription API rejects uploads over 25 MB. We measure before
     we send, and say so plainly rather than letting the upload fail.

  3. TRANSCRIBE. One API call, then write the result twice -- a plain .txt for
     reading, and a timestamped .md for finding the moment someone said the
     thing worth keeping.

Model choice: whisper-1, because it is the model that returns per-segment
TIMESTAMPS (`verbose_json`). gpt-4o-transcribe is more accurate but returns
plain text only, and for a long two-person conversation being able to jump to
14:02 is worth more than a slightly lower error rate. Pass --model
gpt-4o-transcribe to swap; you get a .txt and no timestamps.

WHAT THIS CANNOT DO: it does not separate speakers. The OpenAI transcription
API has no diarization, so a two-person conversation comes back as one voice.
Timestamps plus your own memory of who talks when is the practical substitute.

Cost: whisper-1 bills about US$0.006/minute, so ~$0.20 for 34 minutes.

Usage:
    python tools/transcribe_recording.py art_generated/audiodump/RECORDING.mp4
    python tools/transcribe_recording.py RECORDING.mp4 --keep-audio
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

MAX_UPLOAD_MB = 25

# Whisper accepts a `prompt` that biases spelling and vocabulary. Without it,
# real 2026-07-29/30 sessions produced "pdumedata" for pdoom-data, "0.3.2" for
# 0.13.2, and "S6" for F6. A short vocabulary list fixes most of that class.
# Kept as a plain file so it can be edited without touching this script, and so
# other projects can point --vocab somewhere else entirely.
DEFAULT_VOCAB = [
    "P(Doom)1",
    "pdoom1",
    "pdoom-data",
    "pdoom1-website",
    "Godot",
    "GDScript",
    "ladder epoch",
    "seed roll",
    "leaderboard",
    "board key",
    "doom",
    "Attention",
    "founder hours",
    "Manifund",
    "Wanasai",
    "Pip",
]
CHUNK_SECONDS = 600  # 10 min: short enough that a 500 costs one chunk, not the run


def run(cmd: list) -> subprocess.CompletedProcess:
    """Run a command, and fail loudly with its stderr rather than silently."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"[!] command failed: {' '.join(cmd[:3])}...\n{result.stderr[-1500:]}")
    return result


def probe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def extract_audio(source: Path, dest: Path) -> None:
    """Video out, mono 16 kHz in. -vn drops the video stream entirely."""
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",  # no video
            "-ac",
            "1",  # mono
            "-ar",
            "16000",  # 16 kHz -- what ASR models actually consume
            "-b:a",
            "48k",  # plenty for speech
            str(dest),
        ]
    )


def split_audio(audio: Path, seconds: int) -> list:
    """Cut the audio into fixed-length pieces.

    Long single uploads to the transcription endpoint fail with server-side 500s
    often enough to be a real problem. Chunking also means a failure costs one
    piece rather than the whole 34 minutes, and each piece can be retried alone.
    """
    out_dir = audio.parent / (audio.stem + "_chunks")
    out_dir.mkdir(exist_ok=True)
    for stale in out_dir.glob("part_*.mp3"):
        stale.unlink()
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio),
            "-f",
            "segment",
            "-segment_time",
            str(seconds),
            "-c",
            "copy",
            str(out_dir / "part_%03d.mp3"),
        ]
    )
    return sorted(out_dir.glob("part_*.mp3"))


def load_vocab(path, disabled: bool) -> str:
    """Build the Whisper `prompt` string that biases spelling.

    Accepts a JSON array or a plain one-term-per-line file. Returns "" when
    disabled, so a caller transcribing something unrelated is not nudged toward
    this project's jargon.
    """
    if disabled:
        return ""
    terms = DEFAULT_VOCAB
    if path is not None:
        raw = Path(path).read_text(encoding="utf-8").strip()
        try:
            loaded = json.loads(raw)
            terms = [str(t) for t in loaded] if isinstance(loaded, list) else DEFAULT_VOCAB
        except json.JSONDecodeError:
            terms = [ln.strip() for ln in raw.splitlines() if ln.strip() and not ln.startswith("#")]
    # A prompt is a hint, not a glossary: Whisper reads it as prior context, so
    # a comma list of proper nouns works better than instructions.
    return "Terms that may appear: " + ", ".join(terms) + "."


def stamp(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:d}:{secs:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("recording", type=Path, help="the video/audio file to transcribe")
    parser.add_argument(
        "--model", default="whisper-1", help="whisper-1 (timestamps) or gpt-4o-transcribe"
    )
    parser.add_argument("--language", default="en")
    parser.add_argument(
        "--vocab",
        type=Path,
        help="file of domain terms (one per line, or a JSON array) to bias spelling. "
        "Defaults to the built-in P(Doom)1 list; pass a different file for other projects.",
    )
    parser.add_argument("--no-vocab", action="store_true", help="send no vocabulary hint at all")
    parser.add_argument(
        "--out",
        type=Path,
        help="directory for the transcripts (default: alongside the recording). "
        "Lets this be used on files outside any repo.",
    )
    parser.add_argument(
        "--keep-audio", action="store_true", help="do not delete the stripped audio"
    )
    parser.add_argument(
        "--reuse-audio",
        action="store_true",
        help="skip the ffmpeg step if the stripped audio is already on disk (retry-friendly)",
    )
    args = parser.parse_args()

    source = args.recording
    if not source.exists():
        sys.exit(f"[!] not found: {source}")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("[!] OPENAI_API_KEY is not set in this shell")

    duration = probe_duration(source)
    src_mb = source.stat().st_size / 1_048_576
    print(f"[1/3] source: {source.name}  {src_mb:.0f} MB  {stamp(duration)}")

    audio = source.with_suffix(".audio.mp3")
    if audio.exists() and args.reuse_audio:
        print("[2/3] reusing the audio already stripped earlier")
    else:
        print("[2/3] stripping video, downmixing to 16 kHz mono...")
        extract_audio(source, audio)
    out_mb = audio.stat().st_size / 1_048_576
    print(f"      {src_mb:.0f} MB -> {out_mb:.1f} MB  ({out_mb / src_mb:.1%} of the original)")

    if out_mb > MAX_UPLOAD_MB:
        sys.exit(
            f"[!] {out_mb:.1f} MB is over the {MAX_UPLOAD_MB} MB upload limit.\n"
            f"    Lower -b:a (try 24k), or split the file with ffmpeg -f segment."
        )

    vocab_prompt = load_vocab(args.vocab, args.no_vocab)
    if vocab_prompt:
        print(f"[*] vocabulary hint: {len(vocab_prompt.split(','))} terms")

    print(f"[3/3] transcribing with {args.model}...")
    from openai import OpenAI

    # A 12 MB multipart upload over a domestic connection drops sometimes. The
    # default client gives up quickly, which is how the first run of this script
    # died with APIConnectionError while the network was perfectly healthy.
    client = OpenAI(timeout=1800.0, max_retries=4)
    wants_timestamps = args.model == "whisper-1"

    chunks = split_audio(audio, CHUNK_SECONDS)
    print(f"      split into {len(chunks)} chunks of <= {CHUNK_SECONDS // 60} min")

    pieces, segments, offset = [], [], 0.0
    for index, chunk in enumerate(chunks, start=1):
        size_mb = chunk.stat().st_size / 1_048_576
        print(f"      [{index}/{len(chunks)}] {chunk.name} ({size_mb:.1f} MB)...", flush=True)
        with chunk.open("rb") as handle:
            create_kwargs = {
                "model": args.model,
                "file": handle,
                "language": args.language,
                "response_format": "verbose_json" if wants_timestamps else "text",
            }
            if vocab_prompt:
                create_kwargs["prompt"] = vocab_prompt
            piece = client.audio.transcriptions.create(**create_kwargs)
        piece_text = piece.text if wants_timestamps else str(piece)
        pieces.append(piece_text.strip())
        if wants_timestamps:
            for segment in getattr(piece, "segments", []) or []:
                segments.append((offset + segment.start, segment.text))
            offset += float(getattr(piece, "duration", CHUNK_SECONDS) or CHUNK_SECONDS)

    text = chr(10).join(pieces)  # blank line between chunk transcripts
    out_dir = Path(args.out) if args.out else source.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / (source.stem + ".transcript.txt")
    txt_path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[+] {txt_path.name}  ({len(text.split()):,} words)")

    if wants_timestamps and segments:
        lines = [
            f"# Transcript -- {source.name}",
            "",
            f"Duration {stamp(duration)}. Model `{args.model}`.",
            "",
            "> No speaker separation: the API does not diarize, so both voices",
            "> appear as one. Timestamps are there so you can find a moment fast.",
            "",
        ]
        for start, seg_text in segments:
            lines.append(f"**[{stamp(start)}]** {seg_text.strip()}")
            lines.append("")
        md_path = out_dir / (source.stem + ".transcript.md")
        md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print(f"[+] {md_path.name}  ({len(segments):,} timestamped segments)")

    if not args.keep_audio:
        audio.unlink()
        print("[*] removed the stripped audio (pass --keep-audio to keep it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
