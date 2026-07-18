"""Programmatic Strudel capture -- no OBS, no system audio.

Drives strudel.cc in an automated Edge window (moved offscreen, --mute-audio)
and records the WebAudio graph digitally: every node connect() to the
context destination is also routed into a MediaStreamAudioDestinationNode,
which feeds a MediaRecorder (opus 256k). The speakers stay silent and
nothing from the rest of the system (e.g. a voice call) can leak in --
the capture IS the synthesized signal.

Per take: load patch -> play a warmup pass (creates the audio context,
caches gm_* soundfonts + drum samples) -> stop -> attach recorder ->
play again -> record N seconds -> save webm -> ffmpeg to 44.1k wav.

Usage:
  python tools/music/capture_takes.py --test        # one short take + level check
  python tools/music/capture_takes.py --all         # full priority take list
  python tools/music/capture_takes.py --take m4 60  # one named take, N seconds

Outputs to tools/music/captures/raw/ (webm) and tools/music/captures/ (wav).
Requires: pip install playwright  (uses the installed Edge, channel=msedge).
"""

import argparse
import base64
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
JUKEBOX = ROOT / "jukebox.html"
RAW = ROOT / "captures" / "raw"
WAV = ROOT / "captures"

# (take name, source, seconds). source: jukebox track id, or patches/*.js file.
PRIORITY_TAKES = [
    ("capture_2026-07-18_jukebox_m0", "m0", 78),
    ("capture_2026-07-18_jukebox_m0s", "m0s", 88),
    ("capture_2026-07-18_jukebox_m1", "m1", 78),
    ("capture_2026-07-18_jukebox_m2", "m2", 78),
    ("capture_2026-07-18_jukebox_m3", "m3", 84),
    ("capture_2026-07-18_jukebox_m4", "m4", 84),
    ("capture_2026-07-18_jukebox_m4t", "m4t", 84),
    ("capture_2026-07-18_jukebox_m4r", "m4r", 77),
    ("capture_2026-07-18_jukebox_win", "win_b", 120),
    ("capture_2026-07-18_jukebox_menu", "menu", 100),
    ("capture_2026-07-18_trudge_welcome_v0_1", "patches/trudge_welcome_v0_1.js", 130),
]

ARCHIVE_TAKES = [
    ("capture_2026-07-18_trailer_v0_4", "patches/trailer_trudge_sketch_v0_4.js", 180),
    ("capture_2026-07-18_zen_standoff_v0_1", "patches/zen_standoff_sketch_v0_1.js", 70),
    ("capture_2026-07-18_drifting_seven_v0_1", "patches/drifting_seven_v0_1.js", 60),
    ("capture_2026-07-18_dirge_variations_v0_1", "patches/dirge_variations_v0_1.js", 145),
]

# Injected before any page script: every connect() into the destination is
# duplicated into a per-context MediaStreamAudioDestinationNode (the tap).
INIT_JS = """
(() => {
  const origConnect = AudioNode.prototype.connect;
  window.__taps = new Map();
  AudioNode.prototype.connect = function(target, ...rest) {
    try {
      if (target && target instanceof AudioDestinationNode) {
        const ctx = target.context;
        if (!window.__taps.has(ctx)) {
          window.__taps.set(ctx, ctx.createMediaStreamDestination());
        }
        origConnect.call(this, window.__taps.get(ctx));
      }
    } catch (e) {}
    return origConnect.call(this, target, ...rest);
  };
})();
"""

START_REC_JS = """
() => {
  const taps = [...window.__taps.values()];
  if (!taps.length) return false;
  window.__chunks = [];
  window.__rec = new MediaRecorder(taps[0].stream,
    { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 256000 });
  window.__rec.ondataavailable = e => window.__chunks.push(e.data);
  window.__rec.start(1000);
  return true;
}
"""

STOP_REC_JS = """
() => new Promise(res => {
  window.__rec.onstop = () => {
    const blob = new Blob(window.__chunks, { type: 'audio/webm' });
    const r = new FileReader();
    r.onload = () => res(r.result.split(',')[1]);
    r.readAsDataURL(blob);
  };
  window.__rec.stop();
})
"""


def jukebox_tracks():
    html = JUKEBOX.read_text(encoding="utf-8")
    return dict(re.findall(r'id:"(\w+)"[^`]*code:`([^`]*)`', html))


def get_code(source):
    if source.endswith(".js"):
        return (ROOT / source).read_text(encoding="utf-8")
    tracks = jukebox_tracks()
    if source not in tracks:
        raise SystemExit(
            f"track id {source!r} not found in jukebox.html " f"(have: {', '.join(tracks)})"
        )
    return tracks[source]


def play(page):
    page.locator(".cm-content").first.click(timeout=10000)
    page.keyboard.press("Control+Enter")


def stop(page):
    page.keyboard.press("Control+.")


def capture(page, code, seconds, warmup=12):
    b64 = base64.b64encode(code.encode()).decode()
    # goto about:blank first: a URL differing only in #hash is a
    # same-document navigation and strudel would keep playing the OLD code
    # (this silently recorded 11 copies of m0 on the first run).
    page.goto("about:blank")
    page.goto("https://strudel.cc/#" + b64)
    page.wait_for_timeout(5000)
    # verify the editor really holds THIS patch (first distinctive line)
    sig = next(ln for ln in code.splitlines() if ln.strip())[:40]
    got = page.locator(".cm-content").first.inner_text(timeout=10000)
    if sig not in got:
        raise RuntimeError(f"editor content mismatch: expected {sig!r}")
    play(page)  # warmup pass: builds ctx, loads samples
    page.wait_for_timeout(warmup * 1000)
    stop(page)
    page.wait_for_timeout(1000)
    if not page.evaluate(START_REC_JS):
        raise RuntimeError("no audio tap -- graph never connected to destination")
    play(page)  # the real take
    page.wait_for_timeout(seconds * 1000)
    stop(page)
    page.wait_for_timeout(500)
    return base64.b64decode(page.evaluate(STOP_REC_JS))


def to_wav(webm_path, wav_path):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(webm_path),
            "-ar",
            "44100",
            "-ac",
            "2",
            str(wav_path),
        ],
        check=True,
    )


def level_report(path):
    out = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    for line in out.stderr.splitlines():
        if "mean_volume" in line or "max_volume" in line:
            print("   ", line.split("]")[-1].strip())


def run_takes(takes, warmup=12):
    RAW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
            args=[
                "--mute-audio",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--window-position=-32000,-32000",
                "--window-size=1280,900",
                "--no-first-run",
            ],
        )
        page = browser.new_page()
        page.add_init_script(INIT_JS)
        for name, source, seconds in takes:
            print(f"[take] {name} ({seconds}s from {source})")
            try:
                data = capture(page, get_code(source), seconds, warmup)
            except Exception as e:
                print(f"   FAILED: {e}")
                continue
            webm = RAW / f"{name}.webm"
            webm.write_bytes(data)
            wav = WAV / f"{name}.wav"
            to_wav(webm, wav)
            print(f"   ok -> {wav.name} ({wav.stat().st_size // 1024} KB)")
            level_report(wav)
        browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="single 20s m4 take + level check")
    ap.add_argument("--all", action="store_true", help="priority take list")
    ap.add_argument("--archive", action="store_true", help="archive take list")
    ap.add_argument(
        "--take",
        nargs=2,
        metavar=("SOURCE", "SECONDS"),
        help="one take: jukebox id or patches/*.js, length in s",
    )
    args = ap.parse_args()
    if args.test:
        run_takes([("capture_test_m4", "m4", 20)])
    elif args.all:
        run_takes(PRIORITY_TAKES)
    elif args.archive:
        run_takes(ARCHIVE_TAKES)
    elif args.take:
        src, secs = args.take
        run_takes([(f"capture_2026-07-18_{Path(src).stem}", src, int(secs))])
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
