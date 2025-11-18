#!/usr/bin/env python3
"""
Asset promotion tool for pdoom1.

Copies approved assets from art_generated/ to godot/assets/ui/ for use in the game.
Tracks which assets have been promoted and maintains a clean asset structure.
"""

import argparse
import sys
import yaml
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_prompts(yaml_path):
    """Load YAML prompt file."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_prompts(yaml_path, data):
    """Save updated YAML."""
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def promote_asset(asset, source_dir, dest_base_dir, sizes, dry_run=False):
    """
    Copy asset files from generated dir to game assets dir.

    If asset has a selected_variant, copies that variant's files.
    Renames variant files to remove variant suffix for clean game paths.

    Returns: (success: bool, files_copied: int)
    """
    asset_id = asset.get('id')
    category = asset.get('category', 'uncategorized')
    selected_variant = asset.get('selected_variant', '')

    # Create category subdirectory
    dest_dir = dest_base_dir / category

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    files_copied = 0

    for size in sizes:
        # Build source filename - with variant if selected
        if selected_variant:
            # Try with variant suffix first, fall back to without for original v1 files
            source_name_with_variant = f"{asset_id}_{selected_variant}_{size}.png"
            source_name_without_variant = f"{asset_id}_{size}.png"

            # Check if file with variant suffix exists, otherwise try without
            if (source_dir / source_name_with_variant).exists():
                source_name = source_name_with_variant
            else:
                source_name = source_name_without_variant
        else:
            source_name = f"{asset_id}_{size}.png"

        source_file = source_dir / source_name

        # Destination always uses clean name (no variant suffix)
        dest_file = dest_dir / f"{asset_id}_{size}.png"

        if not source_file.exists():
            print(f"  ⚠️  Warning: {source_file.name} not found")
            continue

        if dry_run:
            if selected_variant:
                print(f"  📋 Would copy: {source_file.name} → {dest_file.name}")
            else:
                print(f"  📋 Would copy: {source_file.name} → {dest_file.relative_to(dest_base_dir.parent)}")
        else:
            shutil.copy2(source_file, dest_file)
            if selected_variant:
                print(f"  ✅ Copied: {source_file.name} → {dest_file.name}")
            else:
                print(f"  ✅ Copied: {source_file.name} → {dest_file.relative_to(dest_base_dir.parent)}")

        files_copied += 1

    return files_copied > 0, files_copied


def main():
    parser = argparse.ArgumentParser(
        description="Promote selected assets to game directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to see what would be promoted
  python tools/promote_assets.py --file art_prompts/ui_icons.yaml --dry-run

  # Promote all selected assets (default)
  python tools/promote_assets.py --file art_prompts/ui_icons.yaml

  # Promote specific assets by ID
  python tools/promote_assets.py --file art_prompts/ui_icons.yaml --ids ui_home_hq ui_alerts

  # Promote from a specific category
  python tools/promote_assets.py --file art_prompts/ui_icons.yaml --category main_navigation

Workflow:
  1. Generate assets: python tools/generate_images.py ...
  2. Select variants: python tools/select_assets.py --file art_prompts/ui_icons.yaml
  3. Promote to game: python tools/promote_assets.py --file art_prompts/ui_icons.yaml
        """
    )

    parser.add_argument('--file', required=True, help='Path to YAML prompt file')
    parser.add_argument('--status', default='selected', help='Only promote assets with this status (default: selected)')
    parser.add_argument('--category', help='Only promote assets from this category')
    parser.add_argument('--ids', nargs='+', help='Promote only specific IDs')
    parser.add_argument('--dest', default='godot/assets/icons', help='Destination directory (default: godot/assets/icons)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without copying files')
    parser.add_argument('--mark-promoted', action='store_true', help='Update YAML to mark assets as promoted')

    args = parser.parse_args()

    # Load YAML
    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"❌ File not found: {yaml_path}")
        return 1

    data = load_prompts(yaml_path)

    asset_type = data.get('asset_type', 'unknown')
    output_sizes = data.get('output_sizes', [1024, 512, 256, 128, 64])
    assets = data.get('assets', [])

    # Source directory
    source_dir = Path('art_generated') / asset_type / 'v1'
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Destination directory
    dest_dir = Path(args.dest)

    # Filter assets
    filtered = []
    for asset in assets:
        # Status filter
        if args.status and asset.get('status') != args.status:
            continue

        # Category filter
        if args.category and asset.get('category') != args.category:
            continue

        # ID filter
        if args.ids and asset.get('id') not in args.ids:
            continue

        filtered.append(asset)

    if not filtered:
        print(f"ℹ️  No assets match the specified filters (status={args.status})")
        print(f"   Try using --status generated to see recently generated assets")
        return 0

    # Summary
    print(f"\n{'='*60}")
    print(f"📦 Asset Type: {asset_type}")
    print(f"📂 Source Dir: {source_dir}")
    print(f"🎯 Dest Dir: {dest_dir}")
    print(f"📊 Assets to promote: {len(filtered)}")
    if args.status:
        print(f"   Status filter: {args.status}")
    if args.category:
        print(f"   Category filter: {args.category}")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("🔍 DRY RUN MODE\n")

    # Promote assets
    total_files = 0
    success_count = 0

    for i, asset in enumerate(filtered, 1):
        asset_id = asset.get('id', f'unknown_{i}')
        category = asset.get('category', 'uncategorized')

        print(f"[{i}/{len(filtered)}] {asset_id} ({category})")

        success, files = promote_asset(
            asset,
            source_dir,
            dest_dir,
            output_sizes,
            args.dry_run
        )

        if success:
            success_count += 1
            total_files += files

            # Mark as promoted if requested
            if args.mark_promoted and not args.dry_run:
                asset['status'] = 'promoted'

        print()

    # Save updated YAML
    if args.mark_promoted and success_count > 0 and not args.dry_run:
        save_prompts(yaml_path, data)
        print(f"💾 Updated {yaml_path} - marked {success_count} assets as 'promoted'\n")

    # Summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"📋 DRY RUN COMPLETE")
        print(f"   Would promote: {success_count} assets ({total_files} files)")
    else:
        print(f"✨ PROMOTION COMPLETE!")
        print(f"   Promoted: {success_count} assets")
        print(f"   Files copied: {total_files}")
        print(f"   Destination: {dest_dir}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
