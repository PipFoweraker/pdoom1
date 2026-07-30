#!/usr/bin/env python3
"""Turn a recorded playtest into an evidenced bug list.

One command: recording in, review page out. It transcribes the dictation, finds
every spoken BUG / NOTE marker, grabs the screen frame at that exact moment, and
pairs each finding with what was actually on screen when it was said.

Why markers: a 9-minute playtest produces ~30 spoken observations, and finding
the frame for each one by hand does not happen. Saying "BUG" out loud costs
nothing and makes the whole thing mechanical. See tools/runsheet/playtest_card.html.

It also checks the audio BEFORE spending money on transcription. On 2026-07-30 a
whole session was recorded with the mic never added as an OBS source; Whisper
duly hallucinated "You You You You" across the silence and it nearly got read as
content. This refuses to do that quietly.

Usage:
    python tools/playtest_report.py art_generated/audiodump/RECORDING.mp4
    python tools/playtest_report.py RECORDING.mp4 --markers BUG,NOTE,TODO
    python tools/playtest_report.py RECORDING.mp4 --all       # every segment, not just markers
"""

import argparse
import html
import re
import subprocess
import sys
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRANSCRIBER = REPO / "tools" / "transcribe_recording.py"

# A finding is usually described over a few consecutive segments. Merge segments
# that start within this many seconds of the previous one into a single item.
MERGE_WINDOW_S = 22.0
# Grab the frame slightly AFTER the marker word: people say "BUG" and then look at
# the thing, so a couple of seconds later is usually a better picture of it.
FRAME_OFFSET_S = 2.0
QUIET_MAX_DB = -12.0  # peaks below this suggest no close-mic speech


def run(cmd: list, capture: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        sys.exit(f"[!] failed: {' '.join(str(c) for c in cmd[:4])}\n{result.stderr[-1200:]}")
    return result


def audio_levels(video: Path) -> tuple:
    """(mean_db, max_db) over the first few minutes. Cheap sanity check."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-t",
            "180",
            "-i",
            str(video),
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    mean = re.search(r"mean_volume:\s*(-?[\d.]+) dB", proc.stderr)
    peak = re.search(r"max_volume:\s*(-?[\d.]+) dB", proc.stderr)
    return (float(mean.group(1)) if mean else None, float(peak.group(1)) if peak else None)


def looks_hallucinated(text: str) -> bool:
    """Whisper on silence emits a tiny vocabulary repeated forever."""
    words = text.split()
    if len(words) < 40:
        return False
    return len(set(w.lower().strip(".,!?") for w in words)) <= 4


def ensure_transcript(video: Path) -> Path:
    md = video.with_suffix(".transcript.md")
    if md.exists():
        print(f"[1/4] reusing {md.name}")
        return md
    print("[1/4] transcribing (strip -> chunk -> whisper)...")
    run([sys.executable, str(TRANSCRIBER), str(video), "--keep-audio"], capture=False)
    if not md.exists():
        sys.exit("[!] transcription produced no timestamped transcript")
    return md


def parse_segments(md: Path) -> list:
    """[(seconds, text)] from the '**[m:ss]** text' lines."""
    out = []
    for line in md.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\*\*\[(?:(\d+):)?(\d+):(\d{2})\]\*\*\s*(.*)", line.strip())
        if not m:
            continue
        hours, minutes, secs, text = m.groups()
        total = int(minutes) * 60 + int(secs) + (int(hours) * 3600 if hours else 0)
        if text.strip():
            out.append((float(total), text.strip()))
    return out


def find_markers(segments: list, markers: list, take_all: bool) -> list:
    """Group segments into findings, anchored on marker words."""
    pattern = re.compile(r"\b(" + "|".join(re.escape(m) for m in markers) + r")\b", re.I)
    if take_all:
        # --all is the review-everything fallback, so each segment stands alone.
        # Merging here swallowed a whole 91-segment session into ONE finding.
        return [{"start": s, "last": s, "parts": [t], "marker": "NOTE"} for s, t in segments]
    findings, current = [], None
    for start, text in segments:
        hit = bool(pattern.search(text))
        if hit and (current is None or start - current["last"] > MERGE_WINDOW_S):
            current = {
                "start": start,
                "last": start,
                "parts": [text],
                "marker": (
                    pattern.search(text).group(1).upper() if pattern.search(text) else "NOTE"
                ),
            }
            findings.append(current)
        elif current is not None and start - current["last"] <= MERGE_WINDOW_S:
            current["parts"].append(text)
            current["last"] = start
    return findings


def stamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def extract_frames(video: Path, findings: list, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for index, finding in enumerate(findings, start=1):
        at = max(0.0, finding["start"] + FRAME_OFFSET_S)
        name = f"f{index:03d}_{int(at)}s.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                f"{at:.2f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-vf",
                "scale=1600:-1",
                "-q:v",
                "3",
                str(out_dir / name),
            ]
        )
        finding["frame"] = name
        finding["at"] = at


def build_html(video: Path, findings: list, frames_rel: str, levels: tuple, warn: str) -> str:
    cards = []
    for index, finding in enumerate(findings, start=1):
        quote = html.escape(" ".join(finding["parts"]))
        cards.append(
            f"""
<section class="card" id="f{index}">
  <div class="hd"><span class="tag {finding['marker'].lower()}">{finding['marker']}</span>
    <span class="t">{stamp(finding['at'])}</span>
    <span class="n">#{index}</span></div>
  <div class="body">
    <a href="{frames_rel}/{finding['frame']}" target="_blank">
      <img loading="lazy" src="{frames_rel}/{finding['frame']}" alt="frame at {stamp(finding['at'])}"></a>
    <div class="side">
      <p class="quote">{quote}</p>
      <div class="btns">
        <button class="v" data-k="{index}" data-v="critical">League-critical</button>
        <button class="v" data-k="{index}" data-v="hotpatch">Hotpatch</button>
        <button class="v" data-k="{index}" data-v="backlog">Backlog</button>
        <button class="v" data-k="{index}" data-v="wontfix">Not a bug</button>
      </div>
      <textarea class="note" data-k="{index}" rows="2" placeholder="triage note / issue number"></textarea>
    </div>
  </div>
</section>"""
        )

    banner = f'<div class="warn">{html.escape(warn)}</div>' if warn else ""
    mean, peak = levels
    lv = f"audio mean {mean} dB, peak {peak} dB" if peak is not None else "audio level unknown"
    return (
        TEMPLATE.replace("__CARDS__", "\n".join(cards))
        .replace("__TITLE__", html.escape(video.name))
        .replace("__COUNT__", str(len(findings)))
        .replace("__LEVELS__", html.escape(lv))
        .replace("__WARN__", banner)
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("recording", type=Path)
    ap.add_argument(
        "--markers", default="BUG,NOTE", help="comma-separated marker words (default BUG,NOTE)"
    )
    ap.add_argument(
        "--all", action="store_true", help="treat every segment as a finding, not just marked ones"
    )
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    video = args.recording
    if not video.exists():
        sys.exit(f"[!] not found: {video}")

    mean, peak = audio_levels(video)
    warn = ""
    print(f"[0/4] audio: mean {mean} dB, peak {peak} dB")
    if peak is not None and peak < QUIET_MAX_DB:
        warn = (
            f"AUDIO IS QUIET (peak {peak} dB). That is typical of a recording where the "
            f"microphone was never added as a source and only desktop audio was captured. "
            f"Any transcript below may be invented. Check the OBS mic source before trusting it."
        )
        print(f"[!] {warn}")

    md = ensure_transcript(video)
    segments = parse_segments(md)
    if not segments:
        sys.exit("[!] no timestamped segments parsed from the transcript")

    full = " ".join(t for _, t in segments)
    if looks_hallucinated(full):
        print("[!] TRANSCRIPT LOOKS HALLUCINATED -- a handful of words repeated over the whole")
        print("    file is what Whisper emits for silence. Treat this session as having no")
        print("    usable narration; the video frames are still fine.")
        warn = warn or "Transcript appears to be hallucinated silence. Do not read it as content."

    markers = [m.strip() for m in args.markers.split(",") if m.strip()]
    findings = find_markers(segments, markers, args.all)
    print(
        f"[2/4] {len(segments)} segments -> {len(findings)} findings"
        f" ({'all segments' if args.all else ', '.join(markers)})"
    )
    if not findings:
        print("    No marker words found. Re-run with --all to review every segment,")
        print("    and say BUG or NOTE out loud next session (see the playtest card).")
        return 0

    frames_dir = video.parent / f"frames_{video.stem}"
    print(f"[3/4] extracting {len(findings)} frames...")
    extract_frames(video, findings, frames_dir)

    out = video.with_suffix(".playtest.html")
    out.write_text(
        build_html(video, findings, frames_dir.name, (mean, peak), warn),
        encoding="utf-8",
        newline="\n",
    )
    print(f"[4/4] {out}")
    if args.open:
        webbrowser.open(out.as_uri())
    return 0


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Playtest report -- __TITLE__</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;
        --no:#e2807c;--warn:#d9bd6a;--acc:#d9955c;--ok:#7fc08d}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--no:#9c2b2b;--warn:#8a6a10;--acc:#7a3b12;--ok:#2f6b3a}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:16px 18px 110px;
       font:14px/1.5 ui-monospace,Consolas,monospace}
  header{border-bottom:1px solid var(--line);padding-bottom:9px;margin-bottom:14px}
  h1{font-size:15px;margin:0 0 3px}
  .meta{color:var(--dim);font-size:12px}
  .warn{border:1px solid var(--no);color:var(--no);padding:9px 12px;border-radius:4px;
        margin:10px 0;font-size:12.5px;line-height:1.5}
  .card{border:1px solid var(--line);background:var(--card);border-radius:5px;
        margin:0 0 14px;overflow:hidden}
  .hd{display:flex;gap:10px;align-items:center;padding:8px 12px;border-bottom:1px solid var(--line)}
  .tag{font-size:10px;font-weight:700;letter-spacing:.7px;padding:2px 7px;border-radius:3px;
       border:1px solid var(--acc);color:var(--acc)}
  .tag.bug{border-color:var(--no);color:var(--no)}
  .t{color:var(--dim);font-size:12px}
  .n{margin-left:auto;color:var(--dim);font-size:11px}
  .body{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:12px;padding:12px}
  @media(max-width:1000px){.body{grid-template-columns:1fr}}
  img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:3px}
  .quote{margin:0 0 9px;font-size:13px}
  .btns{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:7px}
  button.v{padding:6px 9px;font:600 11px ui-monospace,monospace;cursor:pointer;
           background:transparent;color:var(--dim);border:1px solid var(--line);border-radius:3px}
  button.v:hover{color:var(--fg)}
  .card[data-v="critical"] button.v[data-v="critical"]{background:var(--no);color:#fff;border-color:var(--no)}
  .card[data-v="hotpatch"] button.v[data-v="hotpatch"]{background:var(--warn);color:#120e02;border-color:var(--warn)}
  .card[data-v="backlog"] button.v[data-v="backlog"]{background:var(--acc);color:#120a04;border-color:var(--acc)}
  .card[data-v="wontfix"] button.v[data-v="wontfix"]{background:var(--ok);color:#08120a;border-color:var(--ok)}
  textarea.note{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--line);
                border-radius:3px;padding:6px;font:12px ui-monospace,monospace;resize:vertical}
  #bar{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);
       padding:9px 16px;display:flex;gap:12px;align-items:center;font-size:12px;flex-wrap:wrap}
  #bar button{padding:7px 13px;font:600 12px ui-monospace,monospace;cursor:pointer;
              background:var(--acc);color:#120a04;border:0;border-radius:3px}
  #out{width:100%;height:140px;display:none;margin-top:8px;background:var(--bg);color:var(--fg);
       border:1px solid var(--line);font:11px ui-monospace,monospace}
</style>

<header>
  <h1>Playtest report -- __TITLE__</h1>
  <div class="meta">__COUNT__ findings &middot; __LEVELS__ &middot; frame captured ~2s after each marker</div>
  __WARN__
</header>

__CARDS__

<div id="bar">
  <button id="exp">Export JSON</button>
  <span id="prog" class="meta"></span>
  <textarea id="out" readonly></textarea>
</div>

<script>
const KEY = "playtest_" + document.title.replace(/\\W/g,"_");
let state = JSON.parse(localStorage.getItem(KEY) || '{"v":{},"n":{}}');
function paint(){
  document.querySelectorAll(".card").forEach(c=>{
    const id = c.id.slice(1); const v = state.v[id];
    if(v) c.setAttribute("data-v", v); else c.removeAttribute("data-v");
  });
  document.querySelectorAll("textarea.note").forEach(t=>{
    if(state.n[t.dataset.k] !== undefined && t.value === "") t.value = state.n[t.dataset.k];
  });
  const done = Object.keys(state.v).length;
  const crit = Object.values(state.v).filter(x=>x==="critical").length;
  document.getElementById("prog").textContent =
    done + " / " + document.querySelectorAll(".card").length + " triaged, " + crit + " league-critical";
}
function save(){ localStorage.setItem(KEY, JSON.stringify(state)); paint(); }
document.querySelectorAll("button.v").forEach(b=>b.addEventListener("click",()=>{
  const k=b.dataset.k;
  if(state.v[k]===b.dataset.v) delete state.v[k]; else state.v[k]=b.dataset.v;
  save();
}));
document.querySelectorAll("textarea.note").forEach(t=>t.addEventListener("input",()=>{
  if(t.value.trim()) state.n[t.dataset.k]=t.value.trim(); else delete state.n[t.dataset.k];
  localStorage.setItem(KEY, JSON.stringify(state));
}));
document.getElementById("exp").addEventListener("click",()=>{
  const rows=[];
  document.querySelectorAll(".card").forEach(c=>{
    const id=c.id.slice(1);
    rows.push({n:+id, at:c.querySelector(".t").textContent,
               marker:c.querySelector(".tag").textContent,
               quote:c.querySelector(".quote").textContent.trim(),
               frame:c.querySelector("img").getAttribute("src"),
               triage:state.v[id]||null, note:state.n[id]||null});
  });
  const o=document.getElementById("out");
  o.style.display="block"; o.value=JSON.stringify(rows,null,1); o.select();
  try{navigator.clipboard.writeText(o.value);}catch(e){}
});
paint();
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main())
