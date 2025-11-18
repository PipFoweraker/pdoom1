#!/usr/bin/env python3
"""
Icon Asset Audit Tool

Scans the godot/assets/icons directory and compares against icon_mapping.json
to identify:
- Used icons (referenced in mapping)
- Unused icons (generated but not mapped)
- Missing icons (referenced but don't exist)

Usage:
    python tools/assets/audit_icons.py [--format json|markdown|summary]
"""

import json
from collections import defaultdict
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
GODOT_ROOT = PROJECT_ROOT / "godot"
ICONS_DIR = GODOT_ROOT / "assets" / "icons"
MAPPING_FILE = GODOT_ROOT / "data" / "icon_mapping.json"


def scan_icon_files() -> dict[str, list[str]]:
    """Scan all icon files organized by category/folder."""
    icons = defaultdict(list)

    for png_file in ICONS_DIR.rglob("*_64.png"):
        # Only count 64px versions as canonical
        rel_path = png_file.relative_to(ICONS_DIR)
        category = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
        icons[category].append(png_file.name)

    return dict(icons)


def load_icon_mapping() -> dict:
    """Load the icon_mapping.json file."""
    with open(MAPPING_FILE, "r") as f:
        return json.load(f)


def extract_used_icons(mapping: dict) -> set[str]:
    """Extract all icon paths that are referenced in the mapping."""
    used = set()

    def extract_from_value(value):
        if isinstance(value, str):
            if value.startswith("res://assets/icons/") and value.endswith(".png"):
                # Extract just the filename
                filename = value.split("/")[-1]
                used.add(filename)
        elif isinstance(value, dict):
            for k, v in value.items():
                if k == "icon" and isinstance(v, str) and v != "PLACEHOLDER":
                    if v.startswith("res://assets/icons/"):
                        filename = v.split("/")[-1]
                        used.add(filename)
                else:
                    extract_from_value(v)
        elif isinstance(value, list):
            for item in value:
                extract_from_value(item)

    for section, content in mapping.items():
        if section == "_meta":
            continue
        extract_from_value(content)

    return used


def get_placeholder_actions(mapping: dict) -> list[dict]:
    """Get all actions that still have PLACEHOLDER icons."""
    placeholders = []

    def find_placeholders(data, path=""):
        if isinstance(data, dict):
            if data.get("icon") == "PLACEHOLDER":
                placeholders.append(
                    {
                        "id": path.split(".")[-1],
                        "path": path,
                        "suggested_prompt": data.get("suggested_prompt", "No prompt provided"),
                    }
                )
            else:
                for key, value in data.items():
                    new_path = f"{path}.{key}" if path else key
                    find_placeholders(value, new_path)

    for section, content in mapping.items():
        if section == "_meta":
            continue
        find_placeholders(content, section)

    return placeholders


def audit_icons() -> dict:
    """Perform full audit and return results."""
    # Scan files
    icons_by_category = scan_icon_files()
    all_icon_files = set()
    for icons in icons_by_category.values():
        all_icon_files.update(icons)

    # Load mapping
    mapping = load_icon_mapping()
    used_icons = extract_used_icons(mapping)
    placeholders = get_placeholder_actions(mapping)

    # Calculate unused
    unused_icons = all_icon_files - used_icons

    # Organize unused by category
    unused_by_category = defaultdict(list)
    for category, icons in icons_by_category.items():
        for icon in icons:
            if icon in unused_icons:
                unused_by_category[category].append(icon)

    # Check for missing (referenced but not existing)
    missing = set()
    for icon in used_icons:
        found = False
        for png_file in ICONS_DIR.rglob(icon):
            found = True
            break
        if not found:
            missing.add(icon)

    return {
        "total_files": len(all_icon_files),
        "used_count": len(used_icons),
        "unused_count": len(unused_icons),
        "missing_count": len(missing),
        "placeholder_count": len(placeholders),
        "used_icons": sorted(used_icons),
        "unused_icons": sorted(unused_icons),
        "unused_by_category": {k: sorted(v) for k, v in unused_by_category.items()},
        "missing_icons": sorted(missing),
        "placeholders": placeholders,
        "icons_by_category": {k: sorted(v) for k, v in icons_by_category.items()},
    }


def format_summary(results: dict) -> str:
    """Format results as a brief summary."""
    lines = [
        "=" * 50,
        "ICON ASSET AUDIT SUMMARY",
        "=" * 50,
        "",
        f"Total 64px icons:     {results['total_files']}",
        f"Used in mapping:      {results['used_count']}",
        f"Unused (available):   {results['unused_count']}",
        f"Missing (broken ref): {results['missing_count']}",
        f"Placeholders needed:  {results['placeholder_count']}",
        "",
        "UNUSED BY CATEGORY:",
        "-" * 50,
    ]

    for category, icons in sorted(results["unused_by_category"].items()):
        if icons:
            lines.append(f"\n{category}/ ({len(icons)} icons)")
            for icon in icons:
                lines.append(f"  - {icon}")

    if results["placeholders"]:
        lines.append("\n" + "=" * 50)
        lines.append("ICONS NEEDING GENERATION:")
        lines.append("-" * 50)
        for p in results["placeholders"]:
            lines.append(f"\n{p['id']}:")
            lines.append(f"  Prompt: {p['suggested_prompt']}")

    if results["missing_icons"]:
        lines.append("\n" + "=" * 50)
        lines.append("MISSING ICONS (broken references):")
        lines.append("-" * 50)
        for icon in results["missing_icons"]:
            lines.append(f"  - {icon}")

    return "\n".join(lines)


def format_markdown(results: dict) -> str:
    """Format results as markdown for documentation."""
    lines = [
        "# Icon Asset Audit Report",
        "",
        "## Summary",
        "",
        f"- **Total 64px Icons**: {results['total_files']}",
        f"- **Used in Mapping**: {results['used_count']}",
        f"- **Unused (Available)**: {results['unused_count']}",
        f"- **Missing (Broken Refs)**: {results['missing_count']}",
        f"- **Placeholders Needed**: {results['placeholder_count']}",
        "",
        "## Used Icons",
        "",
    ]

    for icon in results["used_icons"]:
        lines.append(f"- `{icon}`")

    lines.extend(
        [
            "",
            "## Unused Icons by Category",
            "",
        ]
    )

    for category, icons in sorted(results["unused_by_category"].items()):
        if icons:
            lines.append(f"### {category}/ ({len(icons)} icons)")
            lines.append("")
            for icon in icons:
                lines.append(f"- `{icon}`")
            lines.append("")

    if results["placeholders"]:
        lines.extend(
            [
                "## Icons Needing Generation",
                "",
                "| Action ID | Suggested Prompt |",
                "|-----------|------------------|",
            ]
        )
        for p in results["placeholders"]:
            prompt = (
                p["suggested_prompt"][:60] + "..."
                if len(p["suggested_prompt"]) > 60
                else p["suggested_prompt"]
            )
            lines.append(f"| `{p['id']}` | {prompt} |")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Audit icon assets vs usage")
    parser.add_argument(
        "--format", choices=["json", "markdown", "summary"], default="summary", help="Output format"
    )
    args = parser.parse_args()

    results = audit_icons()

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "markdown":
        print(format_markdown(results))
    else:
        print(format_summary(results))


if __name__ == "__main__":
    main()
