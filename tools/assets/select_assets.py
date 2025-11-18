#!/usr/bin/env python3
"""
Interactive asset selection tool for pdoom1.

Provides a conversational CLI for reviewing generated assets and selecting
which variants to promote to the game.
"""

import argparse
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


def generate_gallery_html(data, assets, output_path):
    """Generate an HTML gallery for viewing and selecting variants."""
    asset_type = data.get("asset_type", "ui_icons")

    # Build source directory path - resolve to absolute for browser compatibility
    source_dir = Path("art_generated") / asset_type / "v1"

    # If default path doesn't exist, try common alternatives
    if not source_dir.exists():
        # Try game_icons as common fallback
        alt_dir = Path("art_generated") / "game_icons" / "v1"
        if alt_dir.exists():
            source_dir = alt_dir
            print(f"📁 Using fallback directory: {source_dir}")

    # Resolve to absolute path for file:// URLs
    source_dir = source_dir.resolve()

    # Count files in source directory for debug info
    png_count = len(list(source_dir.glob("*.png"))) if source_dir.exists() else 0
    print(f"📁 Source directory: {source_dir}")
    print(f"   Found {png_count} PNG files")

    # Build HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Asset Selection Gallery - {asset_type}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
            margin: 0;
        }}
        h1 {{ color: #fff; margin-bottom: 10px; }}
        .stats {{ color: #888; margin-bottom: 20px; }}
        .asset {{
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #3a3a3a;
        }}
        .asset-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .asset-id {{ font-weight: bold; font-size: 1.1em; }}
        .asset-meta {{ color: #888; font-size: 0.9em; }}
        .variants {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .variant {{
            text-align: center;
            background: #333;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
        }}
        .variant:hover {{
            background: #404040;
            border-color: #666;
        }}
        .variant.selected {{
            border-color: #4CAF50;
            background: #2a3a2a;
        }}
        .variant img {{
            width: 128px;
            height: 128px;
            border-radius: 4px;
            image-rendering: pixelated;
        }}
        .variant-label {{
            margin-top: 8px;
            font-size: 0.9em;
        }}
        .selection-output {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #2a2a2a;
            border-top: 2px solid #4CAF50;
            padding: 15px 20px;
        }}
        .selection-output h3 {{ margin: 0 0 10px 0; font-size: 1em; }}
        .selection-commands {{
            font-family: monospace;
            background: #1a1a1a;
            padding: 10px;
            border-radius: 4px;
            white-space: pre-wrap;
            max-height: 100px;
            overflow-y: auto;
        }}
        .copy-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }}
        .copy-btn:hover {{ background: #45a049; }}
        .category-header {{
            background: #333;
            padding: 10px 15px;
            margin: 20px 0 10px 0;
            border-radius: 4px;
            font-weight: bold;
        }}
        main {{ padding-bottom: 180px; }}
    </style>
</head>
<body>
    <h1>Asset Selection Gallery</h1>
    <div class="stats">
        {len(assets)} assets to review | Click variants to select | Copy commands at bottom
        <br><small>Source: {source_dir} ({png_count} PNGs)</small>
    </div>
    <main>
"""

    # Group by category
    by_category = {}
    for asset in assets:
        cat = asset.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(asset)

    # Generate asset cards
    for category, cat_assets in sorted(by_category.items()):
        html += f'<div class="category-header">{category} ({len(cat_assets)} assets)</div>\n'

        for asset in cat_assets:
            asset_id = asset.get("id", "unknown")
            display_name = asset.get("display_name", asset_id)
            status = asset.get("status", "unknown")
            selected = asset.get("selected_variant", "")
            variants = get_asset_variants(asset, source_dir)

            html += f"""<div class="asset" data-id="{asset_id}">
    <div class="asset-header">
        <span class="asset-id">{asset_id}</span>
        <span class="asset-meta">{display_name} | {status}</span>
    </div>
    <div class="variants">
"""

            for variant in variants:
                # Build image path - check for variant suffix first, fall back to no suffix
                img_name_with_variant = f"{asset_id}_{variant}_128.png"
                img_name_without_variant = f"{asset_id}_128.png"

                # Use variant suffix if file exists, otherwise try without
                if (source_dir / img_name_with_variant).exists():
                    img_name = img_name_with_variant
                else:
                    img_name = img_name_without_variant

                img_path = source_dir / img_name

                # Use absolute file:// URL for browser compatibility
                # On Windows, need to format as file:///C:/path/to/file
                abs_path = img_path.resolve()
                if sys.platform == "win32":
                    # Convert Windows path to file:// URL format
                    file_url = "file:///" + str(abs_path).replace("\\", "/")
                else:
                    file_url = "file://" + str(abs_path)

                selected_class = "selected" if variant == selected else ""

                html += f"""        <div class="variant {selected_class}" data-variant="{variant}" onclick="selectVariant('{asset_id}', '{variant}')">
            <img src="{file_url}" alt="{asset_id} {variant}" onerror="this.style.border='2px solid red'; this.alt='Not found: {img_name}'">
            <div class="variant-label">{variant}</div>
        </div>
"""

            html += """    </div>
</div>
"""

    html += """    </main>

    <div class="selection-output">
        <h3>Selection Commands (for select_assets.py --select)</h3>
        <div class="selection-commands" id="commands">Click variants above to generate selection commands...</div>
        <button class="copy-btn" onclick="copyCommands()">Copy to Clipboard</button>
    </div>

    <script>
        const selections = {};

        function selectVariant(assetId, variant) {
            // Update visual selection
            const asset = document.querySelector(`[data-id="${assetId}"]`);
            asset.querySelectorAll('.variant').forEach(v => v.classList.remove('selected'));
            asset.querySelector(`[data-variant="${variant}"]`).classList.add('selected');

            // Track selection
            selections[assetId] = variant;

            // Update command output
            updateCommands();
        }

        function updateCommands() {
            const cmds = Object.entries(selections)
                .map(([id, v]) => `${id}:${v}`)
                .join(' ');

            document.getElementById('commands').textContent = cmds || 'No selections made yet...';
        }

        function copyCommands() {
            const cmds = document.getElementById('commands').textContent;
            navigator.clipboard.writeText(cmds).then(() => {
                alert('Copied to clipboard!\\n\\nRun:\\npython tools/select_assets.py --file art_prompts/ui_icons.yaml --select ' + cmds);
            });
        }
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


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
    print("🎨 ASSET SELECTION - Interactive Mode")
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

            print(f"\n📋 Assets with status '{status_filter}': {len(filtered)}\n")
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
            print(f"📦 {asset['id']}")
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
            print(f"✅ Selected {asset_id} → {variant}")

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
                    print(f"  ⚠️  Invalid format: {line} (use asset_id:variant)")
                    continue

                asset_id, variant = line.split(":", 1)
                variant = variant.strip().lower()
                if not variant.startswith("v"):
                    variant = f"v{variant}"

                asset = next((a for a in assets if a["id"] == asset_id.strip()), None)
                if not asset:
                    print(f"  ⚠️  Asset not found: {asset_id}")
                    continue

                available = get_asset_variants(asset)
                if variant not in available:
                    print(f"  ⚠️  Variant '{variant}' not available for {asset_id}")
                    continue

                asset["selected_variant"] = variant
                asset["status"] = "selected"
                batch_count += 1
                print(f"  ✅ {asset_id} → {variant}")

            if batch_count > 0:
                modified = True
                print(f"\n✅ Batch selected {batch_count} assets\n")

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
            generate_gallery_html(data, filtered, gallery_path)

            # Open in browser
            abs_path = gallery_path.resolve()
            webbrowser.open(f"file://{abs_path}")
            print(f"\n🌐 Opened gallery with {len(filtered)} assets in browser")
            print(f"   File: {gallery_path}")
            print("\n   Click variants to select, then copy commands at bottom.\n")

        # STATUS command
        elif action == "status":
            pending = len(get_assets_by_status(assets, "pending"))
            generated = len(get_assets_by_status(assets, "generated"))
            selected = len(get_assets_by_status(assets, "selected"))
            promoted = len(get_assets_by_status(assets, "promoted"))

            print("\n📊 Selection Progress:")
            print(f"   Pending:   {pending}")
            print(f"   Generated: {generated} (need review)")
            print(f"   Selected:  {selected} (ready to promote)")
            print(f"   Promoted:  {promoted}")
            print(f"   Total:     {len(assets)}")

            if modified:
                print("\n   ⚠️  Unsaved changes!")
            print()

        # SAVE command
        elif action == "save":
            save_prompts(yaml_path, data)
            modified = False
            print(f"💾 Saved to {yaml_path}\n")

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
                    print(f"💾 Saved to {yaml_path}")
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
            print(f"⚠️  Invalid format: {selection} (use asset_id:variant)")
            continue

        asset_id, variant = selection.split(":", 1)
        variant = variant.strip().lower()
        if not variant.startswith("v"):
            variant = f"v{variant}"

        asset = next((a for a in assets if a["id"] == asset_id.strip()), None)
        if not asset:
            print(f"⚠️  Asset not found: {asset_id}")
            continue

        # Use disk scanning for variant discovery
        available = get_asset_variants(asset, source_dir)
        if variant not in available:
            print(f"⚠️  Variant '{variant}' not available for {asset_id}")
            print(f"   Available: {', '.join(available)}")
            continue

        asset["selected_variant"] = variant
        asset["status"] = "selected"
        print(f"✅ {asset_id} → {variant}")

    save_prompts(yaml_path, data)
    print(f"\n💾 Saved to {yaml_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive asset selection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python tools/select_assets.py --file art_prompts/ui_icons.yaml

  # Quick select specific variants
  python tools/select_assets.py --file art_prompts/ui_icons.yaml --select ui_home_hq:v2 ui_alerts_incidents:v1

  # List assets needing review
  python tools/select_assets.py --file art_prompts/ui_icons.yaml --list generated

  # Open HTML gallery for visual selection
  python tools/select_assets.py --file art_prompts/ui_icons.yaml --gallery generated
        """,
    )

    parser.add_argument("--file", required=True, help="Path to YAML prompt file")
    parser.add_argument(
        "--select", nargs="+", help="Quick select variants (format: asset_id:variant)"
    )
    parser.add_argument("--list", dest="list_status", help="List assets with specified status")
    parser.add_argument(
        "--gallery", dest="gallery_status", help="Open HTML gallery with assets of specified status"
    )

    args = parser.parse_args()

    # Load YAML
    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"❌ File not found: {yaml_path}")
        return 1

    data = load_prompts(yaml_path)
    assets = data.get("assets", [])

    # List mode
    if args.list_status:
        filtered = get_assets_by_status(assets, args.list_status)
        if not filtered:
            print(f"No assets with status '{args.list_status}'")
            return 0

        print(f"\n📋 Assets with status '{args.list_status}': {len(filtered)}\n")
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

        gallery_path = Path("asset_gallery.html")
        generate_gallery_html(data, filtered, gallery_path)

        abs_path = gallery_path.resolve()
        webbrowser.open(f"file://{abs_path}")
        print(f"\n🌐 Opened gallery with {len(filtered)} assets in browser")
        print(f"   File: {gallery_path}")
        print("\n   Click variants to select, then copy commands at bottom.")
        print(
            f"   Apply with: python tools/select_assets.py --file {args.file} --select <copied commands>\n"
        )
        return 0

    # Quick select mode
    if args.select:
        quick_select(yaml_path, data, args.select)
        return 0

    # Interactive mode (default)
    interactive_mode(yaml_path, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
