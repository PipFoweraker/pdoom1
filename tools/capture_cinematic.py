#!/usr/bin/env python3
"""Cinematic capture harness for P(Doom)1 -- deterministic scene footage -> mp4/gif.

Records a Godot scene with Godot's built-in MOVIE MAKER mode (an AVI, with audio),
then post-processes it with ffmpeg into a social-ready MP4 (h264/yuv420p/faststart)
and an optimized GIF (two-pass palettegen/paletteuse). Same seed + same scene ->
identical footage, so a trailer can be re-shot each patch and diffed frame-for-frame.

    python tools/capture_cinematic.py portal          # capture the named 'portal'
    python tools/capture_cinematic.py --dry-run portal # print the commands, run nothing
    python tools/capture_cinematic.py res://scenes/dev/captures/portal_capture.tscn

GPU REQUIRED. Movie Maker renders through the real GPU/display pipeline; it does NOT
work headless (no framebuffer -> no frames). Run this on a machine with a GPU/display
(Pip's Windows box), not in CI. See tools/README_capture.md.

Standard library + subprocess only. Godot 4.5.1, pure-GDScript project.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Repo layout: this file is tools/capture_cinematic.py; the Godot project is godot/;
# capture output lands in repo-root captures/ (OUTSIDE godot/ so it is never packed
# into the shipped .pck -- build-hygiene rule from CLAUDE.md).
REPO_ROOT = Path(__file__).resolve().parent.parent
GODOT_PROJECT_DIR = REPO_ROOT / "godot"
CAPTURES_DIR = REPO_ROOT / "captures"

# Default Godot binary (Pip's machine, per CLAUDE.md). Override with --godot or the
# GODOT_BIN env var.
DEFAULT_GODOT = r"C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"


# ---------------------------------------------------------------------------
# NAMED-CAPTURE REGISTRY
# ---------------------------------------------------------------------------
# Each entry is a self-contained recipe. Add new cinematics here (see the commented
# cold_open / doom_scroll stubs) rather than memorizing CLI flags. Fields:
#   scene       res:// path to the scene to record (must exist under godot/).
#   fps         Movie Maker fixed framerate (--fixed-fps) AND the mp4 framerate.
#   resolution  (width, height) render resolution. Keep BOTH even for h264/yuv420p.
#   duration    seconds of footage. frames captured = round(fps * duration), passed
#               to Godot as --quit-after so the run bounds itself with no input.
#   gif_fps     (optional) GIF framerate (lower = smaller file). Default 24.
#   gif_width   (optional) GIF width in px, height auto (keeps aspect). Default 540.
CAPTURES: dict[str, dict] = {
    "portal": {
        "scene": "res://scenes/dev/captures/portal_capture.tscn",
        "fps": 60,
        "resolution": (1080, 1080),  # square -- the portal disc is round
        "duration": 8.0,  # 8s * 60fps = 480 frames
        "gif_fps": 24,
        "gif_width": 540,
    },
    # ---- Add more captures like this (uncomment + point at the real scene) -----
    #
    # The COLD-OPEN is show-once gated (GameConfig.should_show_intro ->
    # last_seen_intro_version / play_intros). Point the runner STRAIGHT at the scene
    # to bypass the gate for capture; see tools/README_capture.md "Capturing the
    # cold-open" for resetting the gate if you want the real entry flow instead.
    #
    # "cold_open": {
    #     "scene": "res://scenes/cold_open_sequence.tscn",
    #     "fps": 60,
    #     "resolution": (1920, 1080),
    #     "duration": 30.0,          # the cold-open is interactive (phone passcode);
    #     "gif_fps": 20,             # for an unattended capture make a dedicated
    #     "gif_width": 640,          # auto-playing variant, as portal_capture.tscn is.
    # },
    #
    # A future doom-scroll trailer: a scene that auto-drives the doom feed.
    # "doom_scroll": {
    #     "scene": "res://scenes/dev/captures/doom_scroll_capture.tscn",
    #     "fps": 30,
    #     "resolution": (1080, 1920),  # vertical / social
    #     "duration": 15.0,
    #     "gif_fps": 20,
    #     "gif_width": 480,
    # },
}


class PreflightError(Exception):
    """A capture prerequisite is missing; message is user-facing + actionable."""


def _res_to_fs_path(res_path: str) -> Path:
    """Map a res:// scene path to its file on disk under godot/."""
    rel = res_path[len("res://") :] if res_path.startswith("res://") else res_path
    return (GODOT_PROJECT_DIR / rel).resolve()


def resolve_target(name_or_scene: str, args: argparse.Namespace) -> dict:
    """Build a fully-resolved capture recipe from a registry name OR a raw scene path.

    Returns a dict: {name, scene, fps, resolution:(w,h), duration, frames, out,
    gif_fps, gif_width}. CLI overrides win over the registry defaults.
    """
    if name_or_scene in CAPTURES:
        spec = dict(CAPTURES[name_or_scene])
        name = name_or_scene
    elif name_or_scene.startswith("res://") or name_or_scene.endswith(".tscn"):
        # Ad-hoc: a scene path with no registry entry. Bare defaults; override via CLI.
        scene = name_or_scene
        if not scene.startswith("res://"):
            scene = "res://" + scene.replace("\\", "/").lstrip("/")
        spec = {"scene": scene, "fps": 60, "resolution": (1920, 1080), "duration": 8.0}
        name = Path(scene).stem
    else:
        known = ", ".join(sorted(CAPTURES)) or "(none)"
        raise PreflightError(
            "Unknown capture '%s'. Use a registry name (%s) or a res:// scene path "
            "(e.g. res://scenes/dev/captures/portal_capture.tscn)." % (name_or_scene, known)
        )

    # ---- Apply CLI overrides ----
    if args.fps is not None:
        spec["fps"] = args.fps
    if args.duration is not None:
        spec["duration"] = args.duration
    if args.resolution is not None:
        spec["resolution"] = args.resolution  # already parsed to (w, h)

    fps = int(spec["fps"])
    width, height = spec["resolution"]
    width, height = int(width), int(height)

    # Frame bound: explicit --frames wins, else round(fps * duration).
    if args.frames is not None:
        frames = int(args.frames)
    else:
        frames = int(round(fps * float(spec["duration"])))

    out = args.out or name

    return {
        "name": name,
        "scene": spec["scene"],
        "fps": fps,
        "resolution": (width, height),
        "duration": float(spec["duration"]),
        "frames": frames,
        "out": out,
        "gif_fps": int(spec.get("gif_fps", 24)),
        "gif_width": int(spec.get("gif_width", 540)),
    }


def preflight(target: dict, godot_bin: Path, need_ffmpeg: bool) -> list[str]:
    """Collect blocking problems. Empty list = good to go."""
    problems: list[str] = []

    if not godot_bin.exists():
        problems.append(
            "Godot binary not found: %s\n"
            "  Fix: pass --godot <path> or set GODOT_BIN. On Pip's machine it is\n"
            "  '%s'." % (godot_bin, DEFAULT_GODOT)
        )

    scene_fs = _res_to_fs_path(target["scene"])
    if not scene_fs.exists():
        problems.append(
            "Scene not found: %s\n  (resolved from %s under %s)"
            % (scene_fs, target["scene"], GODOT_PROJECT_DIR)
        )

    if not (GODOT_PROJECT_DIR / "project.godot").exists():
        problems.append("Godot project.godot not found under %s" % GODOT_PROJECT_DIR)

    if need_ffmpeg and shutil.which("ffmpeg") is None:
        problems.append(
            "ffmpeg not found on PATH (needed for mp4/gif post-processing).\n"
            "  Install: winget install Gyan.FFmpeg  (Windows)  |  apt install ffmpeg  (Linux)\n"
            "  |  brew install ffmpeg  (macOS). Or run with --no-mp4 --no-gif to keep only the AVI."
        )

    return problems


def build_godot_cmd(target: dict, godot_bin: Path, avi_path: Path) -> list[str]:
    """The Godot Movie Maker invocation.

    --write-movie enables Movie Maker mode and writes an AVI (with audio) to an
    ABSOLUTE path outside godot/ (so it never lands in the packed project).
    --fixed-fps sets the deterministic fixed timestep AND the movie framerate.
    --windowed + --resolution set the EXACT capture size: without --windowed the
    project's window/size/mode=2 (maximized) overrides --resolution and you capture
    at the monitor size instead of the requested WxH (verified 2026-07-23: a request
    for 1080x1080 recorded 1080x2160 until --windowed was added). --quit-after bounds
    the run to N frames with no input (the scene also self-quits as a standalone backstop).
    """
    width, height = target["resolution"]
    return [
        str(godot_bin),
        "--path",
        str(GODOT_PROJECT_DIR),
        "--write-movie",
        str(avi_path),
        "--fixed-fps",
        str(target["fps"]),
        "--windowed",
        "--resolution",
        "%dx%d" % (width, height),
        "--quit-after",
        str(target["frames"]),
        target["scene"],
    ]


def build_ffmpeg_mp4_cmd(avi_path: Path, mp4_path: Path, fps: int) -> list[str]:
    """AVI -> h264 mp4, yuv420p, +faststart (web/social friendly). Even dims enforced."""
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(avi_path),
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-preset",
        "slow",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(mp4_path),
    ]


def build_ffmpeg_gif_cmds(
    avi_path: Path, gif_path: Path, palette_path: Path, gif_fps: int, gif_width: int
) -> tuple[list[str], list[str]]:
    """Two-pass GIF: palettegen then paletteuse (clean colours, small file)."""
    vf = "fps=%d,scale=%d:-1:flags=lanczos" % (gif_fps, gif_width)
    palettegen = [
        "ffmpeg",
        "-y",
        "-i",
        str(avi_path),
        "-vf",
        vf + ",palettegen=stats_mode=diff",
        str(palette_path),
    ]
    paletteuse = [
        "ffmpeg",
        "-y",
        "-i",
        str(avi_path),
        "-i",
        str(palette_path),
        "-filter_complex",
        "%s[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" % vf,
        str(gif_path),
    ]
    return palettegen, paletteuse


# Chars that make an arg unsafe to paste bare into a shell (spaces + ffmpeg filter
# punctuation the shell would otherwise interpret: subshells, globs, separators).
_SHELL_SPECIAL = set(" ()[]{};,*&|<>?!$`\"'")


def _fmt(cmd: list[str]) -> str:
    """Render a command list as a copy-paste-safe line (double-quote risky args).

    The script itself runs commands via subprocess WITHOUT a shell, so quoting here
    is purely so the printed dry-run line survives a copy-paste into bash/PowerShell
    (ffmpeg filter strings contain ( ) [ ] ; , which a shell would otherwise mangle).
    """
    parts = []
    for a in cmd:
        if a == "" or any(c in _SHELL_SPECIAL for c in a):
            parts.append('"%s"' % a)
        else:
            parts.append(a)
    return " ".join(parts)


def _run(cmd: list[str], label: str) -> None:
    print("[capture] %s:\n  %s" % (label, _fmt(cmd)))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise PreflightError("%s failed (exit %d)." % (label, result.returncode))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="capture_cinematic.py",
        description="Deterministic Godot scene capture -> mp4/gif via Movie Maker + ffmpeg. "
        "GPU required (does not run headless).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Named captures: " + (", ".join(sorted(CAPTURES)) or "(none)"),
    )
    parser.add_argument(
        "target",
        help="A named capture (e.g. 'portal') OR a res:// scene path to record.",
    )
    parser.add_argument("--fps", type=int, help="Override framerate.")
    parser.add_argument(
        "--resolution",
        type=parse_resolution,
        metavar="WxH",
        help="Override render resolution, e.g. 1920x1080.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        metavar="SECONDS",
        help="Override duration in seconds (frames = fps * duration).",
    )
    parser.add_argument(
        "--frames", type=int, help="Override the frame bound directly (wins over --duration)."
    )
    parser.add_argument(
        "--out",
        metavar="NAME",
        help="Output basename (default = capture name). Writes captures/<NAME>.*",
    )
    parser.add_argument(
        "--godot",
        default=os.environ.get("GODOT_BIN", DEFAULT_GODOT),
        help="Path to the Godot 4.5 binary (or set GODOT_BIN).",
    )
    parser.add_argument("--no-mp4", action="store_true", help="Skip the mp4 pass.")
    parser.add_argument("--no-gif", action="store_true", help="Skip the gif pass.")
    parser.add_argument(
        "--skip-godot",
        action="store_true",
        help="Skip recording; only post-process an existing captures/<out>.avi.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the exact Godot + ffmpeg commands and exit (no rendering).",
    )
    args = parser.parse_args(argv)

    godot_bin = Path(args.godot)

    try:
        target = resolve_target(args.target, args)
    except PreflightError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    avi_path = (CAPTURES_DIR / (target["out"] + ".avi")).resolve()
    mp4_path = (CAPTURES_DIR / (target["out"] + ".mp4")).resolve()
    gif_path = (CAPTURES_DIR / (target["out"] + ".gif")).resolve()
    palette_path = (CAPTURES_DIR / (target["out"] + ".palette.png")).resolve()

    want_mp4 = not args.no_mp4
    want_gif = not args.no_gif
    need_ffmpeg = want_mp4 or want_gif

    godot_cmd = build_godot_cmd(target, godot_bin, avi_path)
    mp4_cmd = build_ffmpeg_mp4_cmd(avi_path, mp4_path, target["fps"]) if want_mp4 else None
    gif_cmds = (
        build_ffmpeg_gif_cmds(
            avi_path, gif_path, palette_path, target["gif_fps"], target["gif_width"]
        )
        if want_gif
        else None
    )

    # ---- Summary banner ----
    w, h = target["resolution"]
    print("=" * 70)
    print("CAPTURE: %s" % target["name"])
    print("  scene      %s" % target["scene"])
    print("  fps        %d" % target["fps"])
    print("  resolution %dx%d" % (w, h))
    print(
        "  duration   %.2fs  (%d frames via --quit-after)" % (target["duration"], target["frames"])
    )
    print(
        "  outputs    %s%s%s"
        % (
            avi_path.name,
            (", " + mp4_path.name) if want_mp4 else "",
            (", " + gif_path.name) if want_gif else "",
        )
    )
    print("  dir        %s" % CAPTURES_DIR)
    print("=" * 70)

    if args.dry_run:
        print("\n-- DRY RUN (no commands executed) --\n")
        if not args.skip_godot:
            print("# 1. Record with Godot Movie Maker (writes the AVI + audio):")
            print(_fmt(godot_cmd) + "\n")
        if want_mp4:
            print("# 2. Post-process AVI -> mp4 (h264 / yuv420p / faststart):")
            print(_fmt(mp4_cmd) + "\n")
        if want_gif:
            print("# 3. Post-process AVI -> gif (two-pass palettegen / paletteuse):")
            print(_fmt(gif_cmds[0]))
            print(_fmt(gif_cmds[1]) + "\n")
        print(
            "Preflight would check: Godot binary exists, scene exists"
            + (", ffmpeg on PATH." if need_ffmpeg else ".")
        )
        return 0

    # ---- Real run: preflight, then execute in order ----
    problems = preflight(target, godot_bin, need_ffmpeg)
    if args.skip_godot:
        # Not recording -> Godot binary irrelevant; the AVI must already exist instead.
        problems = [p for p in problems if "Godot binary" not in p and "project.godot" not in p]
        if not avi_path.exists():
            problems.append("--skip-godot set but %s does not exist to post-process." % avi_path)
    if problems:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 2

    try:
        if not args.skip_godot:
            _run(godot_cmd, "Recording (Godot Movie Maker)")
            if not avi_path.exists():
                raise PreflightError(
                    "Godot exited but %s was not written. Movie Maker needs a real "
                    "GPU/display -- are you running headless?" % avi_path
                )
        if want_mp4:
            _run(mp4_cmd, "Encoding mp4")
        if want_gif:
            _run(gif_cmds[0], "GIF pass 1 (palettegen)")
            _run(gif_cmds[1], "GIF pass 2 (paletteuse)")
            if palette_path.exists():
                palette_path.unlink()  # intermediate; not worth keeping
    except PreflightError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    print("\nDONE. Wrote to %s :" % CAPTURES_DIR)
    for p in (avi_path, mp4_path if want_mp4 else None, gif_path if want_gif else None):
        if p is not None and p.exists():
            print("  %s  (%.1f MB)" % (p.name, p.stat().st_size / 1e6))
    return 0


def parse_resolution(value: str) -> tuple[int, int]:
    """Parse 'WxH' (e.g. 1920x1080) into an (int, int) tuple for argparse."""
    sep = "x" if "x" in value.lower() else ("," if "," in value else None)
    if sep is None:
        raise argparse.ArgumentTypeError("resolution must be WxH, e.g. 1920x1080")
    try:
        w, h = value.lower().split("x") if sep == "x" else value.split(",")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError("resolution must be WxH, e.g. 1920x1080")


if __name__ == "__main__":
    raise SystemExit(main())
