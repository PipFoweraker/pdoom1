#!/usr/bin/env python3
"""
Generalized batch image generator for pdoom1 art assets.

Loads YAML prompt definitions and generates images via a configurable backend.
Supports filtering, dry-run mode, cost tracking, and version management.

Backends:
  - openai (default): OpenAI Images API, model gpt-image-1.5.
  - gemini (dormant/opt-in): Google Gemini "Nano Banana Pro"
    (gemini-3-pro-image), for reference-image-consistent generation.
    google-genai is imported lazily, so the pipeline runs without it installed.
"""

import argparse
import base64
import hashlib
import logging
import sys
from datetime import datetime, timezone
from io import BytesIO
from math import gcd
from pathlib import Path

import yaml
from PIL import Image

# NOTE: openai/google-genai are imported lazily inside their backend helpers so
# that --dry-run (and the non-active backend) work without those SDKs installed.

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Default OpenAI model. gpt-image-1 retires 2026-10-23, so gpt-image-1.5 is the
# active default. It keeps the same request shape (model/prompt/size, alpha via
# background=transparent) and caps landscape at 1536x1024.
# TODO: confirm exact id vs live docs (snapshot: gpt-image-1.5-2025-12-16).
DEFAULT_OPENAI_MODEL = "gpt-image-1.5"

# Google "Nano Banana Pro" (Gemini API). Dormant until --backend gemini.
# TODO: confirm exact id vs live docs.
DEFAULT_GEMINI_MODEL = "gemini-3-pro-image"

DEFAULT_BACKEND = "openai"

# Rough per-image cost (USD) for the dry-run/confirmation estimate only.
# gpt-image-1 at 1024x1024 was $0.08; gpt-image-1.5 is ~20% cheaper and larger
# canvases cost more. These are estimates -- confirm vs live pricing pages.
COST_PER_IMAGE_USD = 0.08  # kept for backwards compat / default fallback


def estimate_cost_per_image(size_str, backend=DEFAULT_BACKEND):
    """Best-effort per-image cost estimate for dry-run reporting only."""
    if backend == "gemini":
        return 0.13  # Nano Banana Pro approx; confirm vs Gemini pricing
    # OpenAI gpt-image-1.5 (medium quality), rough per-size estimates.
    table = {"1024x1024": 0.06, "1536x1024": 0.09, "1024x1536": 0.09}
    return table.get(str(size_str).lower(), COST_PER_IMAGE_USD)


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
    """Lazy initialization of the OpenAI client (import kept local)."""
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI()
    return _client


def _parse_size(size_str):
    """Parse 'WxH' -> (width, height) ints, falling back to 1024x1024."""
    try:
        w, h = str(size_str).lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        return 1024, 1024


def _aspect_ratio(width, height):
    """Reduce WxH to a 'W:H' aspect-ratio string (e.g. 1536x1024 -> '3:2')."""
    g = gcd(width, height) or 1
    return f"{width // g}:{height // g}"


def _openai_generate_bytes(model, prompt, size_str, background="transparent"):
    """Call the OpenAI Images API and return raw image bytes.

    gpt-image-1.5 keeps gpt-image-1's request shape (model/prompt/size, and
    optional background for alpha control). Confirm the exact model id and
    param surface vs live docs before a real run.

    background='transparent' is requested by default so icons come back with a
    real alpha channel instead of a baked-in background (the icon prompts ask for
    transparency but the API otherwise fills the canvas). Full-bleed art (hero
    banners, backgrounds, textures) must pass background='opaque' via the
    manifest's top-level ``background`` key, otherwise flat regions (skies, dark
    grounds) get alpha-cut out of the scene. Accepts 'transparent', 'opaque' or
    'auto'. PNG (the gpt-image default) is alpha-capable, so no output_format
    override is needed.
    """
    result = get_client().images.generate(
        model=model, prompt=prompt, size=size_str, background=background
    )
    return base64.b64decode(result.data[0].b64_json)


def _gemini_generate_bytes(model, prompt, size_str, reference_images=None):
    """Call Google Gemini (Nano Banana Pro) and return raw image bytes.

    DORMANT backend: only reached via --backend gemini. google-genai is imported
    lazily here so the rest of the pipeline runs without it installed. Reads
    GEMINI_API_KEY from the environment. Reference-image paths are passed as
    extra content for style/subject consistency across a set.
    """
    import os

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - dormant backend
        raise RuntimeError(
            "google-genai is not installed. Run 'pip install google-genai' "
            "to use --backend gemini."
        ) from exc

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

    client = genai.Client(api_key=api_key)

    # Multimodal contents: prompt text followed by any reference images.
    contents = [prompt]
    for ref in reference_images or []:
        contents.append(Image.open(ref))

    width, height = _parse_size(size_str)

    # TODO: confirm image_config / aspect_ratio surface vs live google-genai docs.
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=_aspect_ratio(width, height)),
    )
    response = client.models.generate_content(model=model, contents=contents, config=config)

    for part in response.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and getattr(inline, "data", None):
            return inline.data
    raise RuntimeError("Gemini response contained no image data.")


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


def generate_image(
    asset_id,
    full_prompt,
    output_dir,
    sizes,
    size_str="1024x1024",
    unit_cost=COST_PER_IMAGE_USD,
    model=DEFAULT_OPENAI_MODEL,
    backend=DEFAULT_BACKEND,
    force=False,
    variant_num=None,
    reference_images=None,
    background="transparent",
):
    """
    Generate an image (via the chosen backend) and downscaled versions.

    Args:
        size_str: Master canvas size 'WxH' (e.g. '1536x1024'). Passed to the API
            and used to name/scale the master.
        sizes: List of target WIDTHS. Each downscale preserves the master aspect
            ratio, so square masters behave exactly as before and landscape
            banners downscale to landscape.
        variant_num: If provided, generates variant with suffix _vN
            (e.g., asset_v2_1536.png).

    Returns: (success: bool, cost: float, file_path: str)
    """
    master_w, master_h = _parse_size(size_str)

    # Build filename with optional variant suffix
    if variant_num is not None:
        base_name = f"{asset_id}_v{variant_num}"
    else:
        base_name = asset_id

    master_path = output_dir / f"{base_name}_{master_w}.png"

    # Skip if exists unless force
    if master_path.exists() and not force:
        log(f"  ⏭️  Skipping {base_name} (already exists, use --force to regenerate)")
        log(f"SKIP: {base_name} - file exists", "debug")
        return False, 0.0, str(master_path)

    log(f"  🎨 Generating {base_name} ({size_str}, {backend})...")
    log(f"GENERATE: {base_name}", "debug")
    log(f"PROMPT: {full_prompt}", "debug")

    try:
        if backend == "gemini":
            img_bytes = _gemini_generate_bytes(model, full_prompt, size_str, reference_images)
        else:
            img_bytes = _openai_generate_bytes(model, full_prompt, size_str, background)
    except Exception as e:
        log(f"  ❌ ERROR generating {base_name}: {e}", "error")
        log(f"ERROR: {base_name} - {str(e)}", "error")
        return False, 0.0, None

    # Decode and save master
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    img.save(master_path)

    # Downscale to requested widths, preserving the master aspect ratio.
    for width in sizes:
        if width >= master_w:
            continue
        height = max(1, round(master_h * width / master_w))
        resized = img.resize((width, height), Image.LANCZOS)
        resized.save(output_dir / f"{base_name}_{width}.png")

    downscaled = len([w for w in sizes if w < master_w])
    log(f"  ✅ Saved: {master_path.name} (+ {downscaled} downscaled versions)")
    log(f"SUCCESS: {base_name} -> {master_path}", "debug")

    return True, unit_cost, str(master_path)


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

  # Generate landscape hero banners (uses default_size from the YAML)
  python tools/generate_images.py --file art_prompts/hero_banners.yaml --status pending --variants 3 --yes --update-yaml

  # Opt into the Google Gemini "Nano Banana Pro" backend (needs GEMINI_API_KEY)
  python tools/generate_images.py --file art_prompts/hero_banners.yaml --backend gemini \\
      --reference-images ref_a.png ref_b.png --status pending --yes
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
    parser.add_argument(
        "--backend",
        choices=["openai", "gemini"],
        default=DEFAULT_BACKEND,
        help="Image backend: 'openai' (gpt-image-1.5, default) or 'gemini' "
        "(Nano Banana Pro / gemini-3-pro-image, needs GEMINI_API_KEY).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the model id. Defaults to gpt-image-1.5 (openai) or "
        "gemini-3-pro-image (gemini).",
    )
    parser.add_argument(
        "--reference-images",
        nargs="+",
        help="Reference image paths for style/subject consistency "
        "(gemini backend). Applied to every asset in this run.",
    )

    args = parser.parse_args()

    # Resolve the active model from backend + optional override.
    if args.model:
        model = args.model
    elif args.backend == "gemini":
        model = DEFAULT_GEMINI_MODEL
    else:
        model = DEFAULT_OPENAI_MODEL

    # Load YAML
    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"❌ File not found: {yaml_path}")
        return 1

    data = load_prompts(yaml_path)

    # Extract config
    asset_type = data.get("asset_type", "unknown")
    output_sizes = data.get("output_sizes", [1024, 512, 256, 128, 64])
    size_str = str(data.get("default_size", "1024x1024"))
    unit_cost = estimate_cost_per_image(size_str, args.backend)
    # Alpha control for the OpenAI backend: 'transparent' (default, icons),
    # 'opaque' (full-bleed hero banners / backgrounds), or 'auto'.
    background = str(data.get("background", "transparent"))
    assets = data.get("assets", [])

    # Reference images: CLI applies to the whole run (gemini backend).
    cli_reference_images = args.reference_images or []

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
    print(f"🧩 Backend: {args.backend}")
    print(f"🤖 Model: {model}")
    print(f"📐 Size: {size_str}")
    print(f"🖼️  Background: {background} (openai backend)")
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
            estimated_cost = len(filtered) * unit_cost
            total_images = len(filtered)
            print(
                f"\n💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: 1 new variant per asset @ ~${unit_cost:.2f} each, est.)"
            )
        else:
            estimated_cost = len(filtered) * args.variants * unit_cost
            total_images = len(filtered) * args.variants
            print(
                f"\n💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: {len(filtered)} assets × {args.variants} variants @ ~${unit_cost:.2f} each, est.)"
            )
        return 0

    # Confirm before generating
    if args.add_variant:
        estimated_cost = len(filtered) * unit_cost
        total_images = len(filtered)
        print(
            f"💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: 1 new variant per asset)\n"
        )
    elif args.variants > 1:
        estimated_cost = len(filtered) * args.variants * unit_cost
        total_images = len(filtered) * args.variants
        print(
            f"💰 Estimated cost: ${estimated_cost:.2f} ({total_images} images: {len(filtered)} assets × {args.variants} variants)\n"
        )
    else:
        estimated_cost = len(filtered) * unit_cost
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

        # Per-asset reference images (YAML) plus any CLI-wide ones (gemini).
        reference_images = list(asset.get("reference_images", [])) + cli_reference_images

        variant_successes = 0

        for variant_num in range(start_variant, end_variant):
            # Use variant suffix if adding variant or multiple variants requested
            if args.add_variant or args.variants > 1:
                v_num = variant_num
            else:
                v_num = None

            success, cost, file_path = generate_image(
                asset_id,
                full_prompt,
                output_dir,
                output_sizes,
                size_str=size_str,
                unit_cost=unit_cost,
                model=model,
                backend=args.backend,
                force=args.force,
                variant_num=v_num,
                reference_images=reference_images,
                background=background,
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
                            "model": model,
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
