#!/usr/bin/env python3
"""
Generalized batch image generator for pdoom1 art assets.

Loads YAML prompt definitions and generates images using OpenAI's gpt-image-1 model.
Supports filtering, dry-run mode, cost tracking, and version management.
"""

import argparse
import base64
import hashlib
import logging
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import yaml
from openai import OpenAI
from PIL import Image

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cost per image for gpt-image-1 at 1024x1024
COST_PER_IMAGE_USD = 0.08

# Initialize client lazily to avoid errors in dry-run mode
_client = None

# Logging setup
_logger = None
_log_file = None


def setup_logging(output_dir, yaml_name):
    """Setup file and console logging for the generation run."""
    global _logger, _log_file

    # Create logs directory
    log_dir = Path("art_generated") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _log_file = log_dir / f"generation_{yaml_name}_{timestamp}.log"

    # Configure logger
    _logger = logging.getLogger("asset_generator")
    _logger.setLevel(logging.DEBUG)
    _logger.handlers.clear()

    # File handler - detailed logging
    file_handler = logging.FileHandler(_log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)

    # Console handler - info level only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    _logger.addHandler(console_handler)

    return _log_file


def log(message, level="info"):
    """Log a message to both file and console."""
    if _logger:
        if level == "debug":
            _logger.debug(message)
        elif level == "warning":
            _logger.warning(message)
        elif level == "error":
            _logger.error(message)
        else:
            _logger.info(message)
    else:
        print(message)


def get_client():
    """Lazy initialization of OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def load_prompts(yaml_path):
    """Load and parse YAML prompt file."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_prompts(yaml_path, data):
    """Save updated YAML with generation metadata."""
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def build_full_prompt(data, asset):
    """Build complete prompt from global style + theme + asset prompt_tail."""
    styles = data.get("styles", {})
    themes = data.get("themes", {})

    # Get theme for this asset (or default)
    theme_name = asset.get("theme", "base_corporate")
    theme = themes.get(theme_name, {})

    # Build style components
    style_parts = []

    # Use theme's style_overrides if present, otherwise use global_icon_base
    style_refs = theme.get("style_overrides", ["global_icon_base"])
    for ref in style_refs:
        if ref in styles:
            style_parts.append(styles[ref])

    # Add color bias if present
    if "color_bias" in theme:
        style_parts.append(theme["color_bias"])

    # Combine with asset's prompt_tail
    global_style = ", ".join(style_parts)
    prompt_tail = asset.get("prompt_tail", "").strip()

    full_prompt = f"{global_style}, {prompt_tail}" if prompt_tail else global_style
    return full_prompt


def compute_prompt_hash(prompt):
    """Compute SHA256 hash of prompt for tracking."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]


def generate_image(asset_id, full_prompt, output_dir, sizes, force=False, variant_num=None):
    """
    Generate image and downscaled versions.

    Args:
        variant_num: If provided, generates variant with suffix _vN (e.g., asset_v2_1024.png)

    Returns: (success: bool, cost: float, file_path: str)
    """
    # Build filename with optional variant suffix
    if variant_num is not None:
        base_name = f"{asset_id}_v{variant_num}"
    else:
        base_name = asset_id

    master_path = output_dir / f"{base_name}_1024.png"

    # Skip if exists unless force
    if master_path.exists() and not force:
        log(f"  ⏭️  Skipping {base_name} (already exists, use --force to regenerate)")
        log(f"SKIP: {base_name} - file exists", "debug")
        return False, 0.0, str(master_path)

    log(f"  🎨 Generating {base_name}...")
    log(f"GENERATE: {base_name}", "debug")
    log(f"PROMPT: {full_prompt}", "debug")

    try:
        result = get_client().images.generate(
            model="gpt-image-1", prompt=full_prompt, size="1024x1024"
        )
    except Exception as e:
        log(f"  ❌ ERROR generating {base_name}: {e}", "error")
        log(f"ERROR: {base_name} - {str(e)}", "error")
        return False, 0.0, None

    # Decode and save master
    img_bytes = base64.b64decode(result.data[0].b64_json)
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    img.save(master_path)

    # Downscale to requested sizes
    for size in sizes:
        if size == 1024:
            continue
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(output_dir / f"{base_name}_{size}.png")

    log(
        f"  ✅ Saved: {master_path.name} (+ {len([s for s in sizes if s != 1024])} downscaled versions)"
    )
    log(f"SUCCESS: {base_name} -> {master_path}", "debug")

    return True, COST_PER_IMAGE_USD, str(master_path)


def filter_assets(assets, category=None, status=None, ids=None):
    """Filter assets based on criteria."""
    filtered = assets

    if category:
        filtered = [a for a in filtered if a.get("category") == category]

    if status:
        filtered = [a for a in filtered if a.get("status") == status]

    if ids:
        id_set = set(ids)
        filtered = [a for a in filtered if a.get("id") in id_set]

    return filtered


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from YAML prompt definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all pending icons
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --status pending

  # Dry-run to see what would be generated
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --dry-run

  # Generate specific icons by ID
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --ids ui_home_hq ui_alerts

  # Generate max 10 icons from a category
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --category buttons --limit 10

  # Force regenerate all icons (ignores existing files)
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --force

  # Generate 3 variants of each icon for comparison
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --status pending --variants 3 --yes

  # Add second variant to single-variant assets
  python tools/generate_images.py --file art_prompts/ui_icons.yaml --status generated --add-variant --yes
        """,
    )

    parser.add_argument("--file", required=True, help="Path to YAML prompt file")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--status", help="Filter by status (e.g., pending, needs_review)")
    parser.add_argument(
        "--add-variant", action="store_true", help="Add one more variant to existing assets"
    )
    parser.add_argument("--ids", nargs="+", help="Generate only specific IDs")
    parser.add_argument("--limit", type=int, help="Maximum number of images to generate")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be generated without calling API"
    )
    parser.add_argument("--force", action="store_true", help="Regenerate even if files exist")
    parser.add_argument(
        "--update-yaml", action="store_true", help="Write generation metadata back to YAML"
    )
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    parser.add_argument(
        "--variants",
        type=int,
        default=1,
        help="Number of variants to generate per asset (default: 1)",
    )

    args = parser.parse_args()

    # Load YAML
    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"❌ File not found: {yaml_path}")
        return 1

    data = load_prompts(yaml_path)

    # Extract config
    asset_type = data.get("asset_type", "unknown")
    output_sizes = data.get("output_sizes", [1024, 512, 256, 128, 64])
    assets = data.get("assets", [])

    # Determine output directory
    output_dir = Path("art_generated") / asset_type / "v1"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging (not for dry-run)
    if not args.dry_run:
        yaml_name = yaml_path.stem
        log_file = setup_logging(output_dir, yaml_name)
        log(f"Generation started for {yaml_path}")
        log(f"Log file: {log_file}", "debug")

    # Filter assets
    filtered = filter_assets(assets, args.category, args.status, args.ids)

    if args.limit:
        filtered = filtered[: args.limit]

    if not filtered:
        print("ℹ️  No assets match the specified filters.")
        return 0

    # Summary
    print(f"\n{'='*60}")
    print(f"📋 Asset Type: {asset_type}")
    print(f"📁 Output Dir: {output_dir}")
    print(f"🎯 Assets to generate: {len(filtered)}")
    if args.category:
        print(f"   Category filter: {args.category}")
    if args.status:
        print(f"   Status filter: {args.status}")
    if args.limit:
        print(f"   Limit: {args.limit}")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("🔍 DRY RUN MODE - showing prompts without generating:\n")
        for asset in filtered:
            asset_id = asset.get("id", "unknown")
            full_prompt = build_full_prompt(data, asset)
            prompt_hash = compute_prompt_hash(full_prompt)
            print(f"[{asset_id}]")
            print(f"  Hash: {prompt_hash}")
            print(f"  Category: {asset.get('category', 'none')}")
            print(f"  Status: {asset.get('status', 'unknown')}")
            print(f"  Prompt: {full_prompt[:150]}...")
            print()

        if args.add_variant:
            estimated_cost = len(filtered) * COST_PER_IMAGE_USD
            total_images = len(filtered)
            print(
                f"\n💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: 1 new variant per asset @ ${COST_PER_IMAGE_USD} each)"
            )
        else:
            estimated_cost = len(filtered) * args.variants * COST_PER_IMAGE_USD
            total_images = len(filtered) * args.variants
            print(
                f"\n💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: {len(filtered)} assets × {args.variants} variants @ ${COST_PER_IMAGE_USD} each)"
            )
        return 0

    # Confirm before generating
    if args.add_variant:
        estimated_cost = len(filtered) * COST_PER_IMAGE_USD
        total_images = len(filtered)
        print(
            f"💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: 1 new variant per asset)\n"
        )
    elif args.variants > 1:
        estimated_cost = len(filtered) * args.variants * COST_PER_IMAGE_USD
        total_images = len(filtered) * args.variants
        print(
            f"💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: {len(filtered)} assets × {args.variants} variants)\n"
        )
    else:
        estimated_cost = len(filtered) * COST_PER_IMAGE_USD
        total_images = len(filtered)
        print(f"💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images)\n")

    if not args.yes:
        response = input("Proceed with generation? [y/N]: ")
        if response.lower() != "y":
            print("Cancelled.")
            return 0

    # Generate images
    log("\n🚀 Starting generation...\n")
    log(f"Starting batch: {len(filtered)} assets, {args.variants} variants each", "debug")

    total_cost = 0.0
    success_count = 0
    skip_count = 0

    for i, asset in enumerate(filtered, 1):
        asset_id = asset.get("id", f"unknown_{i}")

        # Determine variant range
        if args.add_variant:
            # Add one variant after existing ones
            existing_count = len(asset.get("generation_history", []))
            start_variant = existing_count + 1
            end_variant = start_variant + 1
            log(f"[{i}/{len(filtered)}] {asset_id} (adding v{start_variant})")
        else:
            # Generate multiple variants if requested
            num_variants = args.variants
            start_variant = 1
            end_variant = num_variants + 1
            if num_variants > 1:
                log(f"[{i}/{len(filtered)}] {asset_id} ({num_variants} variants)")
            else:
                log(f"[{i}/{len(filtered)}] {asset_id}")

        full_prompt = build_full_prompt(data, asset)
        prompt_hash = compute_prompt_hash(full_prompt)

        variant_successes = 0

        for variant_num in range(start_variant, end_variant):
            # Use variant suffix if adding variant or multiple variants requested
            if args.add_variant or args.variants > 1:
                v_num = variant_num
            else:
                v_num = None

            success, cost, file_path = generate_image(
                asset_id, full_prompt, output_dir, output_sizes, args.force, variant_num=v_num
            )

            if success:
                variant_successes += 1
                total_cost += cost

                # Update asset metadata if requested
                if args.update_yaml:
                    if "generation_history" not in asset:
                        asset["generation_history"] = []

                    asset["generation_history"].append(
                        {
                            "version": (
                                f"v{variant_num}"
                                if (args.add_variant or args.variants > 1)
                                else "v1"
                            ),
                            "generated_at": datetime.now(timezone.utc).isoformat(),
                            "model": "gpt-image-1",
                            "full_prompt_hash": prompt_hash,
                            "file_path": file_path,
                            "cost_usd": cost,
                        }
                    )
            else:
                if cost == 0.0:  # Skipped, not error
                    skip_count += 1

        # Update status after all variants are generated
        if variant_successes > 0:
            success_count += 1
            if args.update_yaml and asset.get("status") == "pending":
                asset["status"] = "generated"

        log("")

    # Save updated YAML
    if args.update_yaml and success_count > 0:
        save_prompts(yaml_path, data)
        log(f"💾 Updated {yaml_path} with generation metadata\n")

    # Summary
    failed_count = len(filtered) - success_count - skip_count
    log(f"\n{'='*60}")
    log("✨ Generation Complete!")
    log(f"   Success: {success_count}")
    log(f"   Skipped: {skip_count}")
    log(f"   Failed: {failed_count}")
    log(f"   Total cost: ${total_cost:.2f}")
    if _log_file:
        log(f"   Log file: {_log_file}")
    log(f"{'='*60}\n")

    # Log final summary to file
    log(
        f"SUMMARY: success={success_count}, skipped={skip_count}, failed={failed_count}, cost=${total_cost:.2f}",
        "debug",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
