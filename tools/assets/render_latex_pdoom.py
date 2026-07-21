#!/usr/bin/env python3
"""
Local LaTeX-style typeset renders of the P(doom) logo studies.

Uses matplotlib's mathtext with the Computer Modern font set (the LaTeX look),
so it needs NO system LaTeX install and costs NO API credits. Renders a couple
of Bayesian-notation P(doom) marks in the house palette (amber on aubergine) for
typography comparison against the generative logo studies in iconset_round2.yaml.

Output filenames match the asset ids in the YAML so select_assets.py's gallery
finds them: art_generated/iconset_round2/v1/<id>_<size>.png
"""

from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

# House palette (docs/art/PALETTE_AND_DOOM_INTENSITY.md)
AUBERGINE = "#170A1C"
AMBER = "#E8A33D"

OUT_DIR = Path("art_generated") / "iconset_round2" / "v1"
SIZES = [512, 256, 128, 64, 48, 32]  # downscale widths (matches YAML output_sizes)

# LaTeX / Computer Modern look via mathtext -- no external TeX needed.
matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["font.family"] = "serif"

RENDERS = {
    # id -> (mathtext string, fontsize, figure width inches)
    "render_latex_pdoom_inaction": (
        r"$P(\mathrm{doom}\;|\;\mathrm{inaction})$",
        44,
        8.0,
    ),
    "render_latex_pdoom_bayes": (
        r"$P(\mathrm{doom}\,|\,E)=\dfrac{P(E\,|\,\mathrm{doom})\,P(\mathrm{doom})}{P(E)}$",
        34,
        8.0,
    ),
}


def render(asset_id, mathtext, fontsize, width_in):
    fig = plt.figure(figsize=(width_in, width_in * 0.5), dpi=200)
    fig.patch.set_facecolor(AUBERGINE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(AUBERGINE)
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        mathtext,
        color=AMBER,
        fontsize=fontsize,
        ha="center",
        va="center",
        transform=ax.transAxes,
    )
    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=AUBERGINE)
    plt.close(fig)
    buf.seek(0)
    master = Image.open(buf).convert("RGBA")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mw = master.width
    # Save a 1024-wide "master" (unstaged, like the gpt masters) + downscales.
    master.save(OUT_DIR / f"{asset_id}_{mw}.png")
    for w in SIZES:
        if w >= mw:
            continue
        h = max(1, round(master.height * w / mw))
        master.resize((w, h), Image.LANCZOS).save(OUT_DIR / f"{asset_id}_{w}.png")
    print(f"  rendered {asset_id} (master {mw}px + {len([w for w in SIZES if w < mw])} downscales)")


def main():
    print("Rendering local LaTeX-style P(doom) typeset marks...")
    for asset_id, (mt, fs, w) in RENDERS.items():
        render(asset_id, mt, fs, w)
    print(f"Done -> {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
