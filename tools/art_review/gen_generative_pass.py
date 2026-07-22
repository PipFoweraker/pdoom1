#!/usr/bin/env python3
"""
Generative (gpt-image) pass for the P(Doom)1 app-icon + settings-bg fast pass.

Companion to gen_icon_candidates.py / gen_settings_grounds.py (the procedural,
no-API set). This runs the concepts through the real OpenAI Images API for
higher fidelity, writing gen_*.png ALONGSIDE the procedural files so Pip can
compare both in one contact sheet.

Requires OPENAI_API_KEY in the environment (load the key file out-of-band;
never print or commit it). Uses the same request shape as
tools/assets/generate_images.py (model / prompt / size, b64_json response).

Usage:
  set -a; source <key.env>; set +a
  python tools/art_review/gen_generative_pass.py --test           # verify model id
  python tools/art_review/gen_generative_pass.py --which all --model gpt-image-1.5
"""

import argparse
import base64
from io import BytesIO
from pathlib import Path

from openai import OpenAI
from PIL import Image

ICON_DIR = Path("art_source/iconset_2026-07-21")
BG_DIR = Path("art_source/settings_bg_2026-07-21")
ICON_SIZES = [512, 256, 128, 64, 48, 32]

# Shared style preamble -- encodes the locked palette + cozy-grimdark + the
# SWEEP_REVIEW ruling (deadpan, NO skull/death-metal grim) + small-size clarity.
STYLE_ICON = (
    "A clean app icon, 1024x1024, single centered subject, bold and simple "
    "enough to stay legible at 32x32. Cozy-grimdark mood: a warm, lived-in feel "
    "under quiet dread, deadpan and a little bureaucratic -- NOT horror, no "
    "skulls, no gore, no death-metal edginess, friendly and charming. Deep "
    "aubergine-to-warm-brown background (from #170A1C to #2B221A) with ONE soft "
    "amber glow (#F6A800) as the only saturated accent. Flat poster-like limited "
    "palette, clean confident shapes, gentle vignette, subtle film grain, "
    "rounded-square icon framing, high contrast, uncluttered. "
)
STYLE_BG = (
    "A seamless worn wall-panel texture that fills the whole square frame, flat "
    "even lighting, no central subject, no text, no logo. Old peeling painted "
    "sheet-metal panel with an undercoat showing through the flaked paint, light "
    "rust streaks, a few flat-head screws near the corners and edge midpoints, "
    "fine grain, slightly grimy and lived-in. Warm register, cozy, NOT green. "
)

ICONS = {
    # (1) office cat -- highest priority for a generative model
    "gen_cat_face": STYLE_ICON
    + (
        "Subject: a charming simple house-cat face looking straight at the "
        "viewer, amber silhouette with warm highlights, big calm round eyes, "
        "small triangle ears. The friendly office mascot cat."
    ),
    "gen_cat_doom": STYLE_ICON
    + (
        "Subject: a nervous house cat crouching low with ears back, hiding, "
        "still cute and rounded (not scary). The single glow behind it sours "
        "from amber toward an uneasy red (#E24A3B) -- the cat as a doom "
        "barometer sensing trouble."
    ),
    "gen_cat_sitting": STYLE_ICON
    + (
        "Subject: a cozy tabby cat sitting upright next to a steaming coffee "
        "mug, warm amber desk-lamp light, content and relaxed."
    ),
    "gen_cat_loaf": STYLE_ICON
    + (
        "Subject: a sleepy cat curled into a neat loaf shape, eyes closed, warm "
        "amber glow, extremely cozy and calm."
    ),
    # (2) bureaucratic seal / stamp
    "gen_seal_star": STYLE_ICON
    + (
        "Subject: a round bureaucratic rubber-stamp seal, two concentric rings "
        "with curved uppercase text 'P(DOOM) LABORATORY', a bold five-point star "
        "in the middle, amber ink on the dark ground, slightly worn and inky. "
        "Deadpan officialdom."
    ),
    "gen_seal_hourglass": STYLE_ICON
    + (
        "Subject: a round official department stamp, a simple hourglass glyph in "
        "the center, curved uppercase text 'PAPERWORK THAT MIGHT SAVE THE "
        "WORLD', amber ink, worn rubber-stamp edges."
    ),
    "gen_seal_check": STYLE_ICON
    + (
        "Subject: a scalloped official approval seal with a bold check-mark in "
        "the center, curved text 'DOOM DEPT - APPROVED', teal-green ink "
        "(#1EC3B3) on the dark ground, rubber-stamp texture."
    ),
    "gen_seal_paper": STYLE_ICON
    + (
        "Subject: a tidy round department emblem built from a stack of paper / "
        "filed documents with a paperclip, amber on dark, curved ring text, a "
        "calm bureaucratic badge -- paperwork as heroism."
    ),
    # (3) doom dial / gauge
    "gen_dial_clock": STYLE_ICON
    + (
        "Subject: a doomsday-clock instrument -- a circular dial with tick "
        "marks and a needle sitting just before midnight, the top arc coloured "
        "amber-to-red, dark instrument face, one amber glow. Early-2000s "
        "command-center gauge."
    ),
    "gen_dial_half": STYLE_ICON
    + (
        "Subject: a half-circle speedometer-style risk gauge, an amber-to-red "
        "arc across the top, a single needle pointing up-right, minimal, dark "
        "background."
    ),
}

BGS = {
    "gen_bg_warm_ochre": STYLE_BG
    + (
        "Warm ochre / mustard-gold topcoat flaking to a pale cream undercoat, "
        "gentle warm rust. Cozy amber-leaning."
    ),
    "gen_bg_warm_terracotta": STYLE_BG
    + (
        "Warm terracotta / rust-red topcoat flaking to a warm tan undercoat, "
        "rusty streaks. The warmest, reddest option."
    ),
    "gen_bg_warm_bakelite": STYLE_BG
    + (
        "Deep warm chocolate-brown bakelite-like panel, worn with subtle hairline "
        "cracks, minimal flaking, very cozy dark brown."
    ),
}


def gen_bytes(client, model, prompt, size):
    r = client.images.generate(model=model, prompt=prompt, size=size)
    return base64.b64decode(r.data[0].b64_json)


def save_icon(raw, icon_id):
    # gpt-image 1024px PNGs are 1.3-2.3 MB and exceed the repo's 1000 KB
    # add-large-file hook, so the committed master tops out at 512.
    img = Image.open(BytesIO(raw)).convert("RGBA")
    for s in ICON_SIZES:
        img.resize((s, s), Image.LANCZOS).save(ICON_DIR / f"{icon_id}_{s}.png")


def save_bg(raw, bg_id):
    img = Image.open(BytesIO(raw)).convert("RGB")
    img.resize((512, 512), Image.LANCZOS).save(BG_DIR / f"{bg_id}_512.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-image-1.5")
    ap.add_argument("--which", choices=["icons", "bg", "all"], default="all")
    ap.add_argument("--only", nargs="+", help="generate only these ids")
    ap.add_argument(
        "--test", action="store_true", help="one throwaway generation to verify the model id"
    )
    args = ap.parse_args()

    client = OpenAI()

    if args.test:
        try:
            gen_bytes(
                client,
                args.model,
                "a plain solid amber (#F6A800) square, flat color, no " "text, test swatch",
                "1024x1024",
            )
            print(f"MODEL_OK {args.model}")
        except Exception as e:  # noqa: BLE001
            print(f"MODEL_FAIL {args.model} :: {type(e).__name__}: {e}")
        return

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    BG_DIR.mkdir(parents=True, exist_ok=True)

    jobs = []
    if args.which in ("icons", "all"):
        jobs += [("icon", k, v) for k, v in ICONS.items()]
    if args.which in ("bg", "all"):
        jobs += [("bg", k, v) for k, v in BGS.items()]
    if args.only:
        jobs = [j for j in jobs if j[1] in set(args.only)]

    done, failed = 0, []
    for kind, jid, prompt in jobs:
        try:
            raw = gen_bytes(client, args.model, prompt, "1024x1024")
            if kind == "icon":
                save_icon(raw, jid)
            else:
                save_bg(raw, jid)
            done += 1
            print(f"  ok {jid}")
        except Exception as e:  # noqa: BLE001
            failed.append(jid)
            print(f"  FAIL {jid} :: {type(e).__name__}: {e}")

    print(f"Done: {done} generated, {len(failed)} failed. model={args.model}")
    if failed:
        print("Failed ids:", ", ".join(failed))


if __name__ == "__main__":
    main()
