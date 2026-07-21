#!/usr/bin/env python3
"""
Interactive asset selection tool for pdoom1.

Provides a conversational CLI for reviewing generated assets and selecting
which variants to promote to the game.

The HTML gallery (``--gallery`` / ``--gallery-batch``) is a single self-contained
page with TWO orthogonal review controls:

  1. Winner-picking per asset group -- click a variant's star to mark it the
     winner; the ``id:vN`` ``--select`` commands are emitted for copy-back.
  2. Verdict UX lifted from tools/art_review/build.py -- keyboard K/M/R
     (keep/maybe/re-roll), per-cell notes, status filter (All/Pending/Keep/
     Maybe/Re-roll), hide-on-verdict (a decided cell leaves the Pending view),
     localStorage persistence keyed by asset id, and a markdown export of every
     verdict + note.

Keyboard: arrows move the focus ring; K/M/R stamp a verdict on the focused cell;
N/Enter edit its note; W picks it as the group winner; click an image to enlarge;
Esc closes the enlarge / drops focus.

Images are referenced by RELATIVE path (from the HTML file) so the page is
portable. Verdicts persist to a single localStorage store, so the file:// origin
does not fragment them.
"""

import argparse
import glob
import json
import os
import re
import sys
import webbrowser
from pathlib import Path

import yaml

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def load_prompts(yaml_path):
    """Load YAML prompt file."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_prompts(yaml_path, data):
    """Save updated YAML."""
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def get_asset_variants(asset, source_dir=None):
    """Get list of variant versions for an asset.

    First checks generation_history in YAML, then falls back to
    scanning disk for actual variant files.
    """
    # Try YAML history first
    history = asset.get("generation_history", [])
    if history:
        return [h.get("version", "v1") for h in history]

    # Fall back to disk scanning if no history
    if source_dir:
        asset_id = asset.get("id", "")
        variants = []

        # Scan for v1, v2, v3 patterns
        for version in ["v1", "v2", "v3", "v4", "v5"]:
            # Check for files matching asset_id_v1_*.png pattern
            pattern = f"{asset_id}_{version}_*.png"
            matches = list(source_dir.glob(pattern))
            if matches:
                variants.append(version)

        if variants:
            return variants

    # Default to v1 if nothing found
    return ["v1"]


def get_assets_by_status(assets, status):
    """Filter assets by status."""
    return [a for a in assets if a.get("status") == status]


# ---------------------------------------------------------------------------
# Gallery generation (winner-pick + verdict UX)
# ---------------------------------------------------------------------------

# Preferred preview sizes, first hit wins. Covers square icons/portraits (256/512)
# AND wide banners / CRT frames whose smallest render is 768.
_SIZE_PREVIEW_ORDER = [256, 512, 768, 1024, 1536, 128, 64]


def resolve_source_dir(asset_type):
    """art_generated/<asset_type>/v1 with a game_icons fallback (legacy)."""
    source_dir = Path("art_generated") / asset_type / "v1"
    if not source_dir.exists():
        alt_dir = Path("art_generated") / "game_icons" / "v1"
        if alt_dir.exists():
            return alt_dir
    return source_dir


def _relpath_posix(path, out_dir):
    """Relative POSIX path from the HTML file's dir to an image.

    Falls back to an absolute file:// URL when a relative path is impossible
    (e.g. output and images on different Windows drives)."""
    abs_img = str(Path(path).resolve())
    try:
        return os.path.relpath(abs_img, str(Path(out_dir).resolve())).replace("\\", "/")
    except ValueError:
        return "file:///" + abs_img.replace("\\", "/")


def _variant_sort_key(v):
    m = re.match(r"v(\d+)$", v)
    return (0, int(m.group(1))) if m else (1, v)


def discover_variant_images(asset_id, source_dir, default_variant="v1"):
    """Scan disk for an asset's variant images.

    Handles both naming schemes seen in the batch:
      * ``<id>_v<N>_<size>.png``  (icons, portraits, banners -- v1..vN)
      * ``<id>_<size>.png``       (single-variant CRT frames -> default_variant)

    Returns an ordered list of {"variant", "preview": Path, "full": Path}.
    """
    if not source_dir or not source_dir.exists():
        return []
    var_re = re.compile(r"^" + re.escape(asset_id) + r"_v(\d+)_(\d+)\.png$")
    single_re = re.compile(r"^" + re.escape(asset_id) + r"_(\d+)\.png$")
    buckets = {}  # variant -> {size: Path}
    for p in source_dir.glob(asset_id + "_*.png"):
        m = var_re.match(p.name)
        if m:
            v = "v" + m.group(1)
            buckets.setdefault(v, {})[int(m.group(2))] = p
            continue
        m2 = single_re.match(p.name)
        if m2:
            buckets.setdefault(default_variant, {})[int(m2.group(1))] = p
    out = []
    for v in sorted(buckets, key=_variant_sort_key):
        sizes = buckets[v]
        preview = None
        for s in _SIZE_PREVIEW_ORDER:
            if s in sizes:
                preview = sizes[s]
                break
        if preview is None:
            preview = sizes[min(sizes)]
        out.append({"variant": v, "preview": preview, "full": sizes[max(sizes)]})
    return out


def _default_variant_for(asset):
    hist = asset.get("generation_history") or []
    if hist and hist[0].get("version"):
        return hist[0]["version"]
    return "v1"


def build_gallery_cells(sources, out_dir):
    """Turn a list of sources into flat cell records + tab list + type->yaml map.

    Each source: {"asset_type", "yaml_file", "assets": [...]}.
    Only assets with at least one image on disk contribute cells.
    """
    cells = []
    tabs = []
    type_file = {}
    for src in sources:
        atype = src["asset_type"]
        yaml_file = src.get("yaml_file", "")
        # An explicit source_dir lets callers point the gallery at a flat image
        # folder (e.g. art_source/<batch>/) instead of art_generated/<type>/v1.
        sdir = Path(src["source_dir"]) if src.get("source_dir") else resolve_source_dir(atype)
        has_any = False
        for asset in src.get("assets", []):
            aid = asset.get("id", "unknown")
            variants = discover_variant_images(aid, sdir, _default_variant_for(asset))
            if not variants:
                continue
            has_any = True
            display = asset.get("display_name", aid)
            cat = asset.get("category", "")
            for vi in variants:
                cells.append(
                    {
                        "id": f"{atype}:{aid}:{vi['variant']}",
                        "tab": atype,
                        "group": f"{atype}:{aid}",
                        "row": display,
                        "sub": (cat + " / " if cat else "") + atype,
                        "variant": vi["variant"],
                        "cap": vi["variant"],
                        "img": _relpath_posix(vi["preview"], out_dir),
                        "full": _relpath_posix(vi["full"], out_dir),
                        "winnerKey": f"{atype}:{aid}",
                    }
                )
        if has_any:
            tabs.append(atype)
            type_file[atype] = yaml_file.replace("\\", "/") if yaml_file else ""
    return cells, tabs, type_file


def write_gallery(sources, output_path, title="Asset Selection Gallery", store_key=None):
    """Write the self-contained gallery HTML. Returns (path, cells, tabs).

    store_key, when given, namespaces this gallery's localStorage so distinct
    galleries opened from the shared file:// origin do not share verdicts/tallies.
    """
    output_path = Path(output_path)
    out_dir = output_path.resolve().parent
    cells, tabs, type_file = build_gallery_cells(sources, out_dir)
    data = {"cells": cells, "tabs": tabs, "typeFile": type_file, "title": title}
    if store_key:
        data["storeKey"] = store_key
    html = GALLERY_TEMPLATE.replace("{{TITLE}}", _esc(title)).replace(
        "{{DATA}}", json.dumps(data, separators=(",", ":"))
    )
    # newline="\n" so the generated HTML is LF on Windows too (Path.write_text
    # otherwise translates to CRLF and trips the mixed-line-ending commit hook).
    output_path.write_text(html, encoding="utf-8", newline="\n")
    return output_path, cells, tabs


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_gallery_html(data, assets, output_path, yaml_file=""):
    """Back-compat single-source wrapper (interactive mode + single --file mode)."""
    atype = data.get("asset_type", "ui_icons")
    src = {"asset_type": atype, "yaml_file": yaml_file, "assets": assets}
    path, cells, tabs = write_gallery(
        [src], output_path, title=f"Asset Selection Gallery - {atype}"
    )
    print(f"Wrote {path} ({len(cells)} cells across {len(tabs)} batch tab(s))")
    return output_path


def collect_batch_sources(status, prompts_dir="art_prompts"):
    """Scan <prompts_dir>/*.yaml|yml for assets with the given status that have
    images on disk. Returns (sources, total_assets_kept)."""
    sources = []
    kept = 0
    yfiles = sorted(glob.glob(os.path.join(prompts_dir, "*.yaml"))) + sorted(
        glob.glob(os.path.join(prompts_dir, "*.yml"))
    )
    for yf in yfiles:
        try:
            d = load_prompts(yf)
        except Exception as e:  # malformed yaml -- skip, keep going
            print(f"skip {yf}: {e}")
            continue
        if not isinstance(d, dict):
            continue
        atype = d.get("asset_type", "")
        assets = d.get("assets", []) or []
        filtered = [a for a in assets if a.get("status") == status]
        if not filtered:
            continue
        sdir = resolve_source_dir(atype)
        keep = [
            a
            for a in filtered
            if discover_variant_images(a.get("id", ""), sdir, _default_variant_for(a))
        ]
        if keep:
            sources.append({"asset_type": atype, "yaml_file": yf, "assets": keep})
            kept += len(keep)
    return sources, kept


def print_asset_summary(asset, index=None):
    """Print a summary of an asset."""
    prefix = f"[{index}] " if index is not None else ""
    variants = get_asset_variants(asset)
    variant_str = ", ".join(variants) if len(variants) > 1 else "single"

    status = asset.get("status", "unknown")
    selected = asset.get("selected_variant", "")

    if selected:
        print(f"{prefix}{asset['id']} ({asset.get('display_name', '')})")
        print(f"    Status: {status} | Selected: {selected} | Variants: {variant_str}")
    else:
        print(f"{prefix}{asset['id']} ({asset.get('display_name', '')})")
        print(f"    Status: {status} | Variants: {variant_str}")


def interactive_mode(yaml_path, data):
    """Run interactive selection mode."""
    assets = data.get("assets", [])

    print("\n" + "=" * 60)
    print("ASSET SELECTION - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  list [status]     - List assets (default: generated)")
    print("  show <id>         - Show asset details and file paths")
    print("  select <id> <v#>  - Select variant (e.g., select ui_home_hq v2)")
    print("  batch             - Batch select from prompted input")
    print("  gallery [status]  - Open HTML gallery in browser (default: generated)")
    print("  status            - Show selection progress")
    print("  save              - Save changes to YAML")
    print("  help              - Show this help")
    print("  quit              - Exit (prompts to save)")
    print()

    modified = False

    while True:
        try:
            cmd = input("select> ").strip()
        except (EOFError, KeyboardInterrupt):
            cmd = "quit"

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        # LIST command
        if action == "list":
            status_filter = parts[1] if len(parts) > 1 else "generated"
            filtered = get_assets_by_status(assets, status_filter)

            if not filtered:
                print(f"\nNo assets with status '{status_filter}'")
                print("Try: list generated, list selected, list pending\n")
                continue

            print(f"\nAssets with status '{status_filter}': {len(filtered)}\n")
            for i, asset in enumerate(filtered, 1):
                print_asset_summary(asset, i)
            print()

        # SHOW command
        elif action == "show":
            if len(parts) < 2:
                print("Usage: show <asset_id>")
                continue

            asset_id = parts[1]
            asset = next((a for a in assets if a["id"] == asset_id), None)

            if not asset:
                print(f"Asset '{asset_id}' not found")
                continue

            print(f"\n{'='*60}")
            print(f"{asset['id']}")
            print(f"   Display Name: {asset.get('display_name', 'N/A')}")
            print(f"   Category: {asset.get('category', 'N/A')}")
            print(f"   Status: {asset.get('status', 'unknown')}")
            if asset.get("selected_variant"):
                print(f"   Selected: {asset['selected_variant']}")
            print("\n   Variants:")

            for h in asset.get("generation_history", []):
                version = h.get("version", "v1")
                file_path = h.get("file_path", "unknown")
                print(f"   - {version}: {file_path}")

            print(f"{'='*60}\n")

        # SELECT command
        elif action == "select":
            if len(parts) < 3:
                print("Usage: select <asset_id> <variant>")
                print("Example: select ui_home_hq v2")
                continue

            asset_id = parts[1]
            variant = parts[2].lower()

            # Normalize variant format
            if not variant.startswith("v"):
                variant = f"v{variant}"

            asset = next((a for a in assets if a["id"] == asset_id), None)

            if not asset:
                print(f"Asset '{asset_id}' not found")
                continue

            available = get_asset_variants(asset)
            if variant not in available:
                print(f"Variant '{variant}' not available for {asset_id}")
                print(f"Available: {', '.join(available)}")
                continue

            asset["selected_variant"] = variant
            asset["status"] = "selected"
            modified = True
            print(f"Selected {asset_id} -> {variant}")

        # BATCH command
        elif action == "batch":
            print("\nEnter selections (one per line, format: asset_id:variant)")
            print("Example: ui_home_hq:v2")
            print("Enter empty line when done:\n")

            batch_count = 0
            while True:
                try:
                    line = input("  ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not line:
                    break

                if ":" not in line:
                    print(f"  Invalid format: {line} (use asset_id:variant)")
                    continue

                asset_id, variant = line.split(":", 1)
                variant = variant.strip().lower()
                if not variant.startswith("v"):
                    variant = f"v{variant}"

                asset = next((a for a in assets if a["id"] == asset_id.strip()), None)
                if not asset:
                    print(f"  Asset not found: {asset_id}")
                    continue

                available = get_asset_variants(asset)
                if variant not in available:
                    print(f"  Variant '{variant}' not available for {asset_id}")
                    continue

                asset["selected_variant"] = variant
                asset["status"] = "selected"
                batch_count += 1
                print(f"  {asset_id} -> {variant}")

            if batch_count > 0:
                modified = True
                print(f"\nBatch selected {batch_count} assets\n")

        # GALLERY command
        elif action == "gallery":
            status_filter = parts[1] if len(parts) > 1 else "generated"
            filtered = get_assets_by_status(assets, status_filter)

            if not filtered:
                print(f"\nNo assets with status '{status_filter}'")
                print("Try: gallery generated, gallery selected\n")
                continue

            # Generate HTML to project root
            gallery_path = Path("asset_gallery.html")
            generate_gallery_html(data, filtered, gallery_path, yaml_file=str(yaml_path))

            # Open in browser
            abs_path = gallery_path.resolve()
            webbrowser.open(f"file://{abs_path}")
            print(f"\nOpened gallery with {len(filtered)} assets in browser")
            print(f"   File: {gallery_path}")
            print("\n   Star a variant to pick a winner; K/M/R to verdict; Export at bottom.\n")

        # STATUS command
        elif action == "status":
            pending = len(get_assets_by_status(assets, "pending"))
            generated = len(get_assets_by_status(assets, "generated"))
            selected = len(get_assets_by_status(assets, "selected"))
            promoted = len(get_assets_by_status(assets, "promoted"))

            print("\nSelection Progress:")
            print(f"   Pending:   {pending}")
            print(f"   Generated: {generated} (need review)")
            print(f"   Selected:  {selected} (ready to promote)")
            print(f"   Promoted:  {promoted}")
            print(f"   Total:     {len(assets)}")

            if modified:
                print("\n   Unsaved changes!")
            print()

        # SAVE command
        elif action == "save":
            save_prompts(yaml_path, data)
            modified = False
            print(f"Saved to {yaml_path}\n")

        # HELP command
        elif action == "help":
            print("\nCommands:")
            print("  list [status]     - List assets by status")
            print("  show <id>         - Show asset details")
            print("  select <id> <v#>  - Select a variant")
            print("  batch             - Batch select from input")
            print("  gallery [status]  - Open HTML gallery in browser")
            print("  status            - Show progress summary")
            print("  save              - Save changes")
            print("  quit              - Exit\n")

        # QUIT command
        elif action in ["quit", "exit", "q"]:
            if modified:
                response = input("Unsaved changes. Save before quitting? [Y/n]: ").strip().lower()
                if response != "n":
                    save_prompts(yaml_path, data)
                    print(f"Saved to {yaml_path}")
            print("Goodbye!")
            break

        else:
            print(f"Unknown command: {action}")
            print("Type 'help' for available commands")


def quick_select(yaml_path, data, selections):
    """Process quick selections from command line."""
    assets = data.get("assets", [])
    asset_type = data.get("asset_type", "ui_icons")

    # Build source directory for disk scanning (same logic as gallery)
    source_dir = Path("art_generated") / asset_type / "v1"
    if not source_dir.exists():
        alt_dir = Path("art_generated") / "game_icons" / "v1"
        if alt_dir.exists():
            source_dir = alt_dir
    source_dir = source_dir.resolve()

    for selection in selections:
        if ":" not in selection:
            print(f"Invalid format: {selection} (use asset_id:variant)")
            continue

        asset_id, variant = selection.split(":", 1)
        variant = variant.strip().lower()
        if not variant.startswith("v"):
            variant = f"v{variant}"

        asset = next((a for a in assets if a["id"] == asset_id.strip()), None)
        if not asset:
            print(f"Asset not found: {asset_id}")
            continue

        # Use disk scanning for variant discovery
        available = get_asset_variants(asset, source_dir)
        if variant not in available:
            print(f"Variant '{variant}' not available for {asset_id}")
            print(f"   Available: {', '.join(available)}")
            continue

        asset["selected_variant"] = variant
        asset["status"] = "selected"
        print(f"{asset_id} -> {variant}")

    save_prompts(yaml_path, data)
    print(f"\nSaved to {yaml_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive asset selection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml

  # Quick select specific variants
  python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --select ui_home_hq:v2

  # List assets needing review
  python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --list generated

  # Single-manifest HTML gallery (winner-pick + K/M/R verdict UX)
  python tools/assets/select_assets.py --file art_prompts/hero_banners.yaml --gallery generated

  # Merged gallery across EVERY art_prompts/*.yaml with images on disk
  python tools/assets/select_assets.py --gallery-batch generated
        """,
    )

    parser.add_argument(
        "--file", help="Path to YAML prompt file (required except for --gallery-batch)"
    )
    parser.add_argument(
        "--select", nargs="+", help="Quick select variants (format: asset_id:variant)"
    )
    parser.add_argument("--list", dest="list_status", help="List assets with specified status")
    parser.add_argument(
        "--gallery", dest="gallery_status", help="Open HTML gallery with assets of specified status"
    )
    parser.add_argument(
        "--gallery-batch",
        dest="gallery_batch",
        help="Scan art_prompts/*.yaml and build ONE merged gallery of all assets "
        "with the given status that have images on disk",
    )
    parser.add_argument(
        "--out",
        default="asset_gallery.html",
        help="Gallery output path (default: asset_gallery.html)",
    )
    parser.add_argument(
        "--no-open", action="store_true", help="Do not open the gallery in a browser"
    )

    args = parser.parse_args()

    # Batch gallery mode (no --file needed)
    if args.gallery_batch:
        sources, kept = collect_batch_sources(args.gallery_batch)
        if not sources:
            print(f"No assets with status '{args.gallery_batch}' have images on disk.")
            return 0
        title = f"Asset Selection Gallery -- batch review ({kept} renders)"
        path, cells, tabs = write_gallery(sources, args.out, title=title)
        print(f"Wrote {path.resolve()}")
        print(f"  {len(cells)} cells across {len(tabs)} batch tab(s): {', '.join(tabs)}")
        if not args.no_open:
            webbrowser.open(f"file://{path.resolve()}")
        return 0

    # Every other mode needs --file
    if not args.file:
        parser.error("--file is required (except with --gallery-batch)")

    # Load YAML
    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"File not found: {yaml_path}")
        return 1

    data = load_prompts(yaml_path)
    assets = data.get("assets", [])

    # List mode
    if args.list_status:
        filtered = get_assets_by_status(assets, args.list_status)
        if not filtered:
            print(f"No assets with status '{args.list_status}'")
            return 0

        print(f"\nAssets with status '{args.list_status}': {len(filtered)}\n")
        for i, asset in enumerate(filtered, 1):
            print_asset_summary(asset, i)
        print()
        return 0

    # Gallery mode
    if args.gallery_status:
        filtered = get_assets_by_status(assets, args.gallery_status)
        if not filtered:
            print(f"No assets with status '{args.gallery_status}'")
            return 0

        gallery_path = Path(args.out)
        generate_gallery_html(data, filtered, gallery_path, yaml_file=str(yaml_path))

        abs_path = gallery_path.resolve()
        if not args.no_open:
            webbrowser.open(f"file://{abs_path}")
        print(f"\nGallery: {abs_path}")
        print("   Star a variant to pick a winner; K/M/R to verdict; Export at bottom.")
        print(
            f"   Apply picks with: python tools/assets/select_assets.py --file {args.file} "
            "--select <copied commands>\n"
        )
        return 0

    # Quick select mode
    if args.select:
        quick_select(yaml_path, data, args.select)
        return 0

    # Interactive mode (default)
    interactive_mode(yaml_path, data)
    return 0


# ---------------------------------------------------------------------------
# Self-contained gallery template. CSS/JS lifted from tools/art_review/build.py
# (dark cozy-grim palette, K/M/R verdicts, notes, status filter, hide-on-verdict,
# markdown export) + winner-pick and click-to-enlarge from the asset gallery.
# {{TITLE}} and {{DATA}} are substituted by write_gallery(); no .format() so the
# CSS/JS braces are left untouched.
# ---------------------------------------------------------------------------
GALLERY_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
  :root{
    --ground:#17120e;--panel:#211a14;--panel-2:#2b221a;--ink:#ece0cf;--ink-dim:#a9977f;--ink-faint:#6f6250;
    --amber:#e8a33d;--amber-deep:#c07a1f;--win:#6fae86;--line:#3a2e22;--checker-a:#201811;--checker-b:#180f09;
    --field:#120d09;--shadow:rgba(0,0,0,.45);
  }
  @media (prefers-color-scheme:light){:root{
    --ground:#efe6d6;--panel:#f7efe0;--panel-2:#fbf5e9;--ink:#2b2116;--ink-dim:#6b5b45;--ink-faint:#9a876c;
    --amber:#b9741a;--amber-deep:#8f5710;--win:#3f8a5c;--line:#ddccb0;--checker-a:#e6dac4;--checker-b:#ded1b8;
    --field:#fffaf0;--shadow:rgba(80,55,20,.18);}}
  :root{--keep:var(--win);--maybe:var(--amber);--reroll:#d8695a}
  @media (prefers-color-scheme:light){:root{--reroll:#c14a3a}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--ground);color:var(--ink);font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
  img{max-width:100%;height:auto;display:block}
  .wrap{max-width:1180px;margin:0 auto;padding:2.4rem 1.4rem 6rem}
  .eyebrow{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--amber);margin:0 0 .8rem}
  h1{font-family:ui-monospace,"Cascadia Code",Consolas,monospace;font-weight:700;font-size:clamp(1.6rem,4vw,2.4rem);line-height:1.05;margin:0 0 .5rem;text-wrap:balance}
  .lede{max-width:74ch;color:var(--ink-dim);font-size:.98rem;margin:0}
  .deck{position:sticky;top:0;z-index:40;margin:1.5rem 0 1.4rem;padding:.8rem 0 .5rem;background:color-mix(in srgb,var(--ground) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
  .deck-row{display:flex;align-items:center;gap:.9rem;flex-wrap:wrap;margin-bottom:.6rem}
  .seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .seg button{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;padding:.34rem .7rem;border:0;background:var(--field);color:var(--ink-dim);cursor:pointer}
  .seg button+button{border-left:1px solid var(--line)}
  .seg button.on{background:var(--amber);color:#20140a;font-weight:700}
  .seg button:focus-visible{outline:2px solid var(--amber);outline-offset:-2px}
  .deck-label{font-family:ui-monospace,Consolas,monospace;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-faint)}
  .tabbar{display:flex;gap:.35rem;overflow-x:auto;padding-bottom:.3rem;scrollbar-width:thin}
  .tab{white-space:nowrap;font-family:ui-monospace,Consolas,monospace;font-size:.76rem;padding:.4rem .75rem;border-radius:8px 8px 0 0;border:1px solid var(--line);border-bottom:0;background:var(--panel);color:var(--ink-dim);cursor:pointer}
  .tab .cnt{font-size:.62rem;color:var(--ink-faint);margin-left:.35rem}
  .tab.on{background:var(--panel-2);color:var(--ink);box-shadow:inset 0 -3px 0 var(--amber)}
  .tab:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  #board{min-height:40vh}
  .empty{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.85rem;padding:2rem 0}
  .board-rows{display:flex;flex-direction:column;gap:1rem}
  .row{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.9rem;display:grid;grid-template-columns:180px 1fr;gap:.9rem;align-items:start}
  .rowhead h4{margin:0 0 .25rem;font-size:.9rem;font-family:ui-monospace,Consolas,monospace;word-break:break-word}
  .rowhead p{margin:0;font-size:.72rem;color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;word-break:break-word}
  .rowhead .winner-of{margin-top:.4rem;font-size:.66rem;color:var(--win)}
  .rolls{display:grid;grid-template-columns:repeat(var(--cols),minmax(140px,1fr));gap:.7rem}
  .cell{position:relative;display:flex;flex-direction:column;gap:.4rem;background:var(--panel-2);border:1px solid var(--line);padding:.6rem;border-radius:8px;scroll-margin:120px}
  .cell.v-keep{box-shadow:0 0 0 2px var(--keep)}
  .cell.v-maybe{box-shadow:0 0 0 2px var(--maybe)}
  .cell.v-reroll{box-shadow:0 0 0 2px var(--reroll)}
  .cell.winner{border-color:var(--win);background:color-mix(in srgb,var(--win) 14%,var(--panel-2))}
  .cell.focused{outline:2px solid var(--amber);outline-offset:2px}
  .caprow{display:flex;align-items:center;justify-content:space-between;gap:.4rem}
  .cap{font-family:ui-monospace,Consolas,monospace;font-size:.66rem;color:var(--amber);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .winbtn{flex:none;font-size:.8rem;line-height:1;padding:.15rem .4rem;border-radius:5px;border:1px solid var(--line);background:var(--field);color:var(--ink-faint);cursor:pointer}
  .winbtn:hover{color:var(--amber);border-color:var(--ink-faint)}
  .winbtn.on{background:var(--win);border-color:var(--win);color:#12251a}
  .winbtn:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .stage{background-color:var(--checker-a);background-image:linear-gradient(45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(-45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker-b) 75%),linear-gradient(-45deg,transparent 75%,var(--checker-b) 75%);background-size:14px 14px;background-position:0 0,0 7px,7px -7px,-7px 0;border:1px solid var(--line);border-radius:8px;padding:.4rem;display:grid;place-items:center;min-height:130px;cursor:zoom-in}
  .stage img{width:auto;max-height:160px}
  .stage.pending{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.7rem;text-align:center;cursor:default}
  .note{width:100%;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.35rem .5rem;font-size:.76rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .note:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .verdict{display:flex;gap:.25rem}
  .vbtn{flex:1;font-family:ui-monospace,Consolas,monospace;font-size:.62rem;text-transform:uppercase;letter-spacing:.03em;padding:.28rem .1rem;border-radius:5px;border:1px solid var(--line);background:var(--field);color:var(--ink-dim);cursor:pointer;transition:.1s}
  .vbtn:hover{color:var(--ink);border-color:var(--ink-faint)}
  .vbtn:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .vbtn.on[data-v="keep"]{background:var(--keep);border-color:var(--keep);color:#12251a}
  .vbtn.on[data-v="maybe"]{background:var(--maybe);border-color:var(--maybe);color:#2a1e08}
  .vbtn.on[data-v="reroll"]{background:var(--reroll);border-color:var(--reroll);color:#2a1210}
  .kbd-legend{position:fixed;top:10px;right:10px;z-index:50;display:flex;flex-direction:column;gap:.28rem;background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:9px;padding:.55rem .65rem;font-family:ui-monospace,Consolas,monospace;font-size:.66rem;color:var(--ink-dim);pointer-events:none;box-shadow:0 2px 12px var(--shadow);backdrop-filter:blur(4px)}
  .kbd-legend b{color:var(--amber);font-weight:400}
  .kbd-legend kbd{display:inline-block;min-width:1.1em;text-align:center;padding:.05rem .32rem;margin-right:.12rem;border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;background:var(--field);color:var(--ink);font-size:.62rem}
  .exportbar{position:sticky;bottom:0;margin:2.5rem -1.4rem -6rem;padding:1rem 1.4rem;background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(8px);border-top:1px solid var(--line);display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
  .tally{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;color:var(--ink-dim)}
  .tally b{color:var(--win)}
  .spacer{flex:1}
  .btn{font-family:ui-monospace,Consolas,monospace;font-size:.8rem;padding:.5rem .9rem;border-radius:7px;border:1px solid var(--amber);background:var(--amber);color:#20140a;font-weight:700;cursor:pointer}
  .btn:hover{background:var(--amber-deep);border-color:var(--amber-deep)}
  .btn:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
  .btn.ghost{background:transparent;color:var(--ink-dim);border-color:var(--line);font-weight:400}
  .btn.ghost:hover{color:var(--ink);border-color:var(--ink-faint)}
  dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:0;max-width:min(760px,92vw);width:100%}
  dialog::backdrop{background:rgba(0,0,0,.55)}
  .modal-head{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.2rem;border-bottom:1px solid var(--line)}
  .modal-head h3{margin:0;font-size:1rem;font-family:ui-monospace,Consolas,monospace}
  .modal-body{padding:1.1rem 1.2rem}
  .modal-body p{margin:0 0 .7rem;color:var(--ink-dim);font-size:.85rem}
  #exporttext,#cmdtext{width:100%;min-height:320px;resize:vertical;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.8rem;font-family:ui-monospace,Consolas,monospace;font-size:.76rem;line-height:1.5;white-space:pre}
  #cmdtext{min-height:120px}
  dialog.lightbox{max-width:96vw;width:auto;background:transparent;border:0}
  dialog.lightbox::backdrop{background:rgba(0,0,0,.82)}
  dialog.lightbox img{max-width:96vw;max-height:92vh;border-radius:8px;box-shadow:0 8px 40px rgba(0,0,0,.6);cursor:zoom-out}
  footer{margin-top:3rem;padding-top:1.4rem;border-top:1px solid var(--line);color:var(--ink-faint);font-size:.78rem;font-family:ui-monospace,Consolas,monospace}
  @media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
  @media (max-width:760px){.row{grid-template-columns:1fr}.rolls{--cols:2!important}}
  @media (max-width:640px){.kbd-legend{display:none}}
</style>
</head>
<body>
<div class="kbd-legend" aria-hidden="true">
  <span><kbd>&larr;</kbd><kbd>&rarr;</kbd> move focus</span>
  <span><b>K</b> keep &middot; <b>M</b> maybe &middot; <b>R</b> re-roll</span>
  <span><b>W</b> winner &middot; <kbd>N</kbd>/<kbd>&crarr;</kbd> note</span>
  <span>click image = enlarge &middot; <kbd>Esc</kbd> back</span>
</div>

<div class="wrap">
  <p class="eyebrow">P(Doom)1 &middot; asset gallery &middot; repo tool</p>
  <h1>{{TITLE}}</h1>
  <p class="lede" id="lede"></p>

  <div class="deck">
    <div class="deck-row">
      <span class="deck-label">status</span>
      <div class="seg" id="filterseg" role="group" aria-label="Status filter">
        <button type="button" data-f="all">All</button>
        <button type="button" data-f="pending">Pending</button>
        <button type="button" data-f="keep">Keep</button>
        <button type="button" data-f="maybe">Maybe</button>
        <button type="button" data-f="reroll">Re-roll</button>
      </div>
    </div>
    <div class="tabbar" id="tabbar" role="tablist"></div>
  </div>

  <div id="board"></div>

  <div class="exportbar">
    <div class="tally" id="tally"></div>
    <div class="tally" id="vct"></div>
    <div class="spacer"></div>
    <button type="button" class="btn ghost" id="clearbtn">reset</button>
    <button type="button" class="btn ghost" id="cmdbtn">Copy --select &rarr;</button>
    <button type="button" class="btn" id="exportbtn">Export verdicts &rarr;</button>
  </div>
  <footer>Verdicts + winner picks saved in your browser (localStorage). Star a variant to pick the group winner; K/M/R to verdict. Export hands both back for the next round.</footer>
</div>

<dialog id="exportdlg">
  <div class="modal-head"><h3>// verdicts + picks</h3><button type="button" class="btn ghost" id="copybtn">copy</button></div>
  <div class="modal-body"><p>Copy and paste this back into the chat.</p><textarea id="exporttext" readonly></textarea></div>
</dialog>

<dialog id="cmddlg">
  <div class="modal-head"><h3>// --select commands</h3><button type="button" class="btn ghost" id="cmdcopybtn">copy</button></div>
  <div class="modal-body"><p>Run these to write your winner picks back into the manifests.</p><textarea id="cmdtext" readonly></textarea></div>
</dialog>

<dialog id="lightbox" class="lightbox"><img id="lightimg" alt="enlarged asset"></dialog>

<script>
(function(){
  "use strict";
  var DATA={{DATA}};
  var KEY=(DATA.storeKey||"pdoom_asset_gallery_v1"),UKEY=KEY+"_ui";
  var CELLDATA=DATA.cells;
  var TYPEFILE=DATA.typeFile||{};
  var LABELS={};CELLDATA.forEach(function(c){LABELS[c.id]=c.row+" / "+c.variant;});
  var TABS=["All"].concat(DATA.tabs||[]);

  var st={picks:{},verdicts:{},notes:{}};
  try{var ls=JSON.parse(localStorage.getItem(KEY)||"{}");
    if(ls.picks)st.picks=ls.picks;
    if(ls.verdicts)st.verdicts=ls.verdicts;
    if(ls.notes)st.notes=ls.notes;
  }catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
  function reduceMotion(){return window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches;}
  function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

  var ui={tab:"All",filter:"all"};
  try{var us=JSON.parse(localStorage.getItem(UKEY)||"{}");
    if(us.tab&&TABS.indexOf(us.tab)>=0)ui.tab=us.tab;
    if(us.filter)ui.filter=us.filter;
  }catch(e){}
  function saveUI(){try{localStorage.setItem(UKEY,JSON.stringify(ui));}catch(e){}}

  var board=document.getElementById('board');
  var tabbar=document.getElementById('tabbar');
  document.getElementById('lede').textContent=
    CELLDATA.length+" renders across "+(DATA.tabs||[]).length+" batch(es). "+
    "Star a variant to pick a group winner; K/M/R to verdict; click an image to enlarge.";

  function inTab(c){return ui.tab==="All"||c.tab===ui.tab;}
  function passesFilter(c){
    if(ui.filter==="all")return true;
    var v=st.verdicts[c.id]||null;
    if(ui.filter==="pending")return !v;
    return v===ui.filter;
  }
  function activeCells(){return CELLDATA.filter(function(c){return inTab(c)&&passesFilter(c);});}

  // ---- verdicts ----
  function applyVerdict(c,v){
    c.classList.remove('v-keep','v-maybe','v-reroll');
    if(v)c.classList.add('v-'+v);
    c.querySelectorAll('.vbtn').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v')===v);});
  }
  function setVerdict(c,v){
    var id=c.getAttribute('data-id');
    if(st.verdicts[id]===v){delete st.verdicts[id];v=null;}
    else{st.verdicts[id]=v;}
    applyVerdict(c,v);save();tally();
    if(ui.filter!=="all")render();
  }

  // ---- winner picks ----
  function setWinner(c){
    var wk=c.getAttribute('data-wk'),variant=c.getAttribute('data-variant');
    if(st.picks[wk]===variant)delete st.picks[wk];else st.picks[wk]=variant;
    save();render();tally();
  }

  // ---- keyboard focus ----
  var CELLS=[],cur=-1;
  function setFocus(i,scroll){
    if(i<0||i>=CELLS.length)return;
    if(cur>=0&&CELLS[cur])CELLS[cur].classList.remove('focused');
    cur=i;var c=CELLS[cur];c.classList.add('focused');
    if(scroll)c.scrollIntoView({behavior:reduceMotion()?'auto':'smooth',block:'nearest',inline:'nearest'});
  }
  function move(d){var i=cur<0?0:cur+d;if(i<0)i=0;if(i>=CELLS.length)i=CELLS.length-1;setFocus(i,true);}
  function focusNote(){
    if(cur<0)setFocus(0,true);
    var c=CELLS[cur],n=c&&c.querySelector('.note');
    if(n){n.focus();if(n.select)n.select();}
  }

  // ---- lightbox ----
  var lb=document.getElementById('lightbox'),lbimg=document.getElementById('lightimg');
  function enlarge(full,label){
    lbimg.src=full;lbimg.alt=label||"enlarged asset";
    if(typeof lb.showModal==='function')lb.showModal();
  }
  lb.addEventListener('click',function(){lb.close();});

  // ---- rendering ----
  function cellHTML(c){
    var won=st.picks[c.winnerKey]===c.variant;
    var stg=c.img
      ? '<div class="stage" data-full="'+esc(c.full)+'" title="click to enlarge"><img loading="lazy" src="'+esc(c.img)+'" alt="'+esc(c.row)+' '+esc(c.variant)+'"></div>'
      : '<div class="stage pending"><span>missing<br>regenerate</span></div>';
    return '<div class="cell'+(won?' winner':'')+'" data-id="'+esc(c.id)+'" data-wk="'+esc(c.winnerKey)+'" data-variant="'+esc(c.variant)+'">'
      +'<div class="caprow"><span class="cap" title="'+esc(c.variant)+'">'+esc(c.cap)+'</span>'
      +'<button type="button" class="winbtn'+(won?' on':'')+'" title="Pick winner (W)" aria-label="Pick winner">&#9733;</button></div>'
      +stg
      +'<div class="verdict" role="group" aria-label="Verdict for '+esc(c.row)+' '+esc(c.variant)+'">'
      +'<button type="button" class="vbtn" data-v="keep" title="Keep (K)">keep</button>'
      +'<button type="button" class="vbtn" data-v="maybe" title="Maybe (M)">maybe</button>'
      +'<button type="button" class="vbtn" data-v="reroll" title="Re-roll (R)">re-roll</button></div>'
      +'<input type="text" class="note" placeholder="note..." aria-label="Note for '+esc(c.row)+' '+esc(c.variant)+'">'
      +'</div>';
  }
  function buildTabs(){
    var totals={};CELLDATA.forEach(function(c){totals[c.tab]=(totals[c.tab]||0)+1;});
    totals["All"]=CELLDATA.length;
    tabbar.innerHTML=TABS.map(function(t){
      var on=t===ui.tab?' on':'';
      return '<button type="button" class="tab'+on+'" role="tab" data-tab="'+esc(t)+'" aria-selected="'+(t===ui.tab)+'">'
        +esc(t)+'<span class="cnt">'+(totals[t]||0)+'</span></button>';
    }).join('');
    tabbar.querySelectorAll('.tab').forEach(function(btn){
      btn.addEventListener('click',function(){ui.tab=btn.getAttribute('data-tab');saveUI();render();});
    });
  }
  function render(){
    buildTabs();
    var cells=activeCells();
    var order=[],groups={};
    cells.forEach(function(c){if(!groups[c.group]){groups[c.group]=[];order.push(c.group);}groups[c.group].push(c);});
    var html;
    if(!order.length){
      html='<p class="empty">no cells match this tab + filter.</p>';
    }else{
      html='<div class="board-rows">'+order.map(function(g){
        var rows=groups[g],first=rows[0];
        var wk=first.winnerKey,winv=st.picks[wk];
        var wtag=winv?'<p class="winner-of">winner: '+esc(winv)+'</p>':'';
        return '<div class="row"><div class="rowhead"><h4>'+esc(first.row)+'</h4>'
          +'<p>'+esc(first.sub||"")+'</p>'+wtag+'</div>'
          +'<div class="rolls" style="--cols:'+Math.max(rows.length,1)+'">'
          +rows.map(cellHTML).join('')+'</div></div>';
      }).join('')+'</div>';
    }
    board.innerHTML=html;
    wireCells();
  }
  function wireCells(){
    CELLS=[].slice.call(board.querySelectorAll('.cell'));cur=-1;
    CELLS.forEach(function(c,idx){
      var id=c.getAttribute('data-id');
      var inp=c.querySelector('.note');
      if(inp){
        if(st.notes[id])inp.value=st.notes[id];
        inp.addEventListener('input',function(e){st.notes[id]=e.target.value;if(!e.target.value)delete st.notes[id];save();});
      }
      applyVerdict(c,st.verdicts[id]||null);
      c.querySelectorAll('.vbtn').forEach(function(btn){
        btn.addEventListener('click',function(){setFocus(idx,false);setVerdict(c,btn.getAttribute('data-v'));});
      });
      var win=c.querySelector('.winbtn');
      if(win)win.addEventListener('click',function(){setFocus(idx,false);setWinner(c);});
      var stg=c.querySelector('.stage');
      if(stg&&stg.getAttribute('data-full')){
        stg.addEventListener('click',function(){setFocus(idx,false);enlarge(stg.getAttribute('data-full'),LABELS[id]);});
      }
      c.addEventListener('mousedown',function(e){if(e.target.tagName!=='INPUT')setFocus(idx,false);});
    });
  }

  document.querySelectorAll('#filterseg button').forEach(function(btn){
    btn.classList.toggle('on',btn.getAttribute('data-f')===ui.filter);
    btn.addEventListener('click',function(){
      ui.filter=btn.getAttribute('data-f');
      document.querySelectorAll('#filterseg button').forEach(function(b){b.classList.toggle('on',b===btn);});
      saveUI();render();
    });
  });

  document.addEventListener('keydown',function(e){
    var t=e.target,tag=(t.tagName||'').toLowerCase();
    var typing=tag==='input'||tag==='textarea'||t.isContentEditable;
    if(typing){if(e.key==='Escape'){t.blur();e.preventDefault();}return;}
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    var k=e.key;
    if(k==='ArrowRight'||k==='ArrowDown'){move(1);e.preventDefault();}
    else if(k==='ArrowLeft'||k==='ArrowUp'){move(-1);e.preventDefault();}
    else if(k==='k'||k==='K'){if(cur>=0){setVerdict(CELLS[cur],'keep');e.preventDefault();}}
    else if(k==='m'||k==='M'){if(cur>=0){setVerdict(CELLS[cur],'maybe');e.preventDefault();}}
    else if(k==='r'||k==='R'){if(cur>=0){setVerdict(CELLS[cur],'reroll');e.preventDefault();}}
    else if(k==='w'||k==='W'){if(cur>=0){setWinner(CELLS[cur]);e.preventDefault();}}
    else if(k==='n'||k==='N'||k==='Enter'){focusNote();e.preventDefault();}
    else if(k==='Escape'){if(lb.open){lb.close();}else if(cur>=0){CELLS[cur].classList.remove('focused');cur=-1;}}
  });

  function tally(){
    var np=Object.keys(st.picks).length;
    document.getElementById('tally').innerHTML='winners picked: <b>'+np+'</b>';
    var k=0,m=0,r=0;
    for(var id in st.verdicts){var v=st.verdicts[id];if(v==='keep')k++;else if(v==='maybe')m++;else if(v==='reroll')r++;}
    document.getElementById('vct').innerHTML='keep <b>'+k+'</b> / maybe <b>'+m+'</b> / re-roll <b>'+r+'</b>';
  }

  // ---- --select command output (grouped by asset_type -> manifest) ----
  function buildCommands(){
    var byType={};
    Object.keys(st.picks).forEach(function(wk){
      var i=wk.indexOf(":");var atype=wk.slice(0,i),aid=wk.slice(i+1);
      (byType[atype]=byType[atype]||[]).push(aid+":"+st.picks[wk]);
    });
    var lines=[];
    Object.keys(byType).forEach(function(atype){
      var f=TYPEFILE[atype]||("art_prompts/"+atype+".yaml");
      lines.push("python tools/assets/select_assets.py --file "+f+" --select "+byType[atype].join(" "));
    });
    return lines.length?lines.join("\n"):"(no winners picked yet -- star a variant)";
  }

  function labelFor(id){return LABELS[id]||id;}
  function buildExport(){
    var L=["# P(Doom)1 asset gallery -- Pip's picks",""];
    L.push("## Winners (--select)");
    var cmd=buildCommands();
    L.push(cmd.indexOf("no winners")>=0?"_(none picked)_":("```\n"+cmd+"\n```"));
    L.push("");
    var groups={keep:[],maybe:[],reroll:[]};
    Object.keys(st.verdicts).forEach(function(id){
      var v=st.verdicts[id];if(!groups[v])return;
      var note=st.notes[id]?(" -- "+st.notes[id]):"";
      groups[v].push("- "+labelFor(id)+" ("+id+")"+note);
    });
    var titles={keep:"Keep",maybe:"Maybe",reroll:"Re-roll"};
    ["keep","maybe","reroll"].forEach(function(g){
      if(groups[g].length){L.push("## "+titles[g],groups[g].join("\n"),"");}
    });
    var extra=Object.keys(st.notes).filter(function(id){return !st.verdicts[id];});
    if(extra.length){L.push("## Other notes");
      extra.forEach(function(id){L.push("- "+labelFor(id)+" ("+id+"): "+st.notes[id]);});
      L.push("");
    }
    return L.join("\n");
  }

  function copyText(el,btn){
    el.select();var ok=false;try{ok=document.execCommand('copy');}catch(e){}
    if(navigator.clipboard)navigator.clipboard.writeText(el.value).catch(function(){});
    var old=btn.textContent;btn.textContent=ok?"copied":"select+copy";
    setTimeout(function(){btn.textContent=old;},1500);
  }

  var dlg=document.getElementById('exportdlg'),txt=document.getElementById('exporttext');
  document.getElementById('exportbtn').addEventListener('click',function(){
    txt.value=buildExport();
    if(typeof dlg.showModal==='function')dlg.showModal();else alert(txt.value);
    txt.focus();txt.select();
  });
  document.getElementById('copybtn').addEventListener('click',function(){copyText(txt,this);});

  var cdlg=document.getElementById('cmddlg'),cmdtxt=document.getElementById('cmdtext');
  document.getElementById('cmdbtn').addEventListener('click',function(){
    cmdtxt.value=buildCommands();
    if(typeof cdlg.showModal==='function')cdlg.showModal();else alert(cmdtxt.value);
    cmdtxt.focus();cmdtxt.select();
  });
  document.getElementById('cmdcopybtn').addEventListener('click',function(){copyText(cmdtxt,this);});

  document.getElementById('clearbtn').addEventListener('click',function(){
    if(!confirm("Clear all winner picks, verdicts and notes?"))return;
    st={picks:{},verdicts:{},notes:{}};save();render();tally();
  });

  render();
  tally();
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
