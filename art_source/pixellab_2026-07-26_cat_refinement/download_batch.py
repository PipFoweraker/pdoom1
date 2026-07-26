"""Download + selectively extract the 2026-07-26 cat refinement batch.

Pulls each character's zip from the PixelLab download endpoint and lands the
zip-native layout ({char}/rotations/*.png, {char}/animations/{group}/{dir}/
frame_*.png, {char}/metadata.json) into this folder.

For the EXISTING sweep characters only the NEW refinement groups are kept
(the old sweep clips already live in ../pixellab_2026-07-26_cat_sweep/); the
three new roster cats land in full. cat_purple is RETIRED (Pip 2026-07-26)
and is not downloaded.

Usage: python art_source/pixellab_2026-07-26_cat_refinement/download_batch.py
"""

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DL = "https://api.pixellab.ai/mcp/characters/{cid}/download"

# char folder -> (character id, keep-animation-folder names or None for ALL)
PLAN = {
    # existing characters: keep only the refinement groups
    "cat_b2_tabby_lowtd_heft": (
        "3bd14ec5-56d2-417e-ba15-293cec950089",
        [
            "walk_ew_cleanfix",
            "walk_north_tailfix",
            "walk_south_calmtall",
            "sitting_v2",
            "licking_v2",
            "butt_flash_dotted",
        ],
    ),
    "cat_black": (
        "28157d2a-7126-4db4-b726-2b6770ac0d4a",
        ["walk_diag_cleanfix", "sitting_v2", "licking_v2"],
    ),
    "cat_eldritch_r2": (
        "d13a61ca-67d9-4606-acd5-00f36bb28858",
        ["walk_ew_cleanfix", "walk_east_cleanfix2", "sitting_v2", "licking_v2"],
    ),
    "cat_sweep_black_side_heft": (
        "55bf4986-ac8e-4419-bce6-aeb6892e0c56",
        ["walk_west_cleanfix"],
    ),
    # new roster: keep everything
    "cat_ref_stripey_side_heft": ("e27412ed-fbed-43ed-a86b-2bbc0fef1d55", None),
    "cat_ref_stripey_lowtd": ("c17642a3-552e-4e0c-9f38-7fe6dc57dd77", None),
    "cat_ref_kambu_placeholder_side_heft": ("5cc3c3a8-17e5-409d-bb51-42557d56d6c5", None),
    "cat_ref_kambu_placeholder_lowtd": ("dfe42fba-11e6-4910-9ba1-e6035b5c6fba", None),
    "cat_ref_marmalade_side_heft": ("a4b9d8ae-df72-42c6-af58-00e96dddc4f9", None),
    "cat_ref_marmalade_lowtd": ("9eb8ed03-a8db-43eb-9c57-f6870b432907", None),
}


def main() -> int:
    failures = 0
    for folder, (cid, keep) in PLAN.items():
        dest = HERE / folder
        print(f"== {folder} ({cid})")
        try:
            with urllib.request.urlopen(DL.format(cid=cid), timeout=300) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            # 423 Locked = jobs still running on this character; re-run later
            print(f"   SKIPPED: HTTP {e.code} ({e.reason})")
            failures += 1
            continue
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
        # zips are rooted at "<charname>/..." -- normalize to our folder name
        roots = {n.split("/", 1)[0] for n in names if "/" in n}
        root = roots.pop() if len(roots) == 1 else None
        kept = 0
        for n in names:
            if n.endswith("/"):
                continue
            rel = n.split("/", 1)[1] if root and n.startswith(root + "/") else n
            parts = rel.split("/")
            if parts[0] == "animations" and keep is not None:
                if len(parts) < 2 or parts[1] not in keep:
                    continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(n))
            kept += 1
        print(f"   kept {kept} files")
    if failures:
        print(f"{failures} character(s) skipped -- re-run once their jobs finish")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
