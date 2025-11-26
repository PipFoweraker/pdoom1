#!/usr/bin/env python3
"""
Generate mechanics documentation from game code.

Extracts game values, constants, and mechanics from GDScript files and generates
up-to-date markdown documentation for the website.

Usage:
    python scripts/generate_mechanics_docs.py [--check] [--output docs/mechanics/]
"""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class GameConstant:
    """A game constant or default value."""

    name: str
    value: Any
    type: str
    source_file: str
    line_number: int
    comment: Optional[str] = None


@dataclass
class MechanicData:
    """Data for a game mechanic."""

    name: str
    constants: Dict[str, GameConstant]
    description: str
    related_files: List[str]
    last_updated: str


class GameDataExtractor:
    """Extract game data from GDScript files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.godot_root = repo_root / "godot"

    def extract_game_state_defaults(self) -> Dict[str, GameConstant]:
        """Extract default resource values from game_state.gd"""
        game_state_file = self.godot_root / "scripts" / "core" / "game_state.gd"
        constants = {}

        if not game_state_file.exists():
            return constants

        content = game_state_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Parse resource definitions
        resource_pattern = re.compile(r"^var\s+(\w+):\s*(\w+)\s*=\s*([^#]+)(?:#\s*(.+))?")

        for line_num, line in enumerate(lines, 1):
            match = resource_pattern.match(line.strip())
            if match:
                var_name, var_type, value, comment = match.groups()

                # Clean up value
                value = value.strip()

                # Parse numeric values
                parsed_value = value
                try:
                    if "." in value:
                        parsed_value = float(value)
                    elif value.isdigit():
                        parsed_value = int(value)
                except ValueError:
                    pass

                constants[var_name] = GameConstant(
                    name=var_name,
                    value=parsed_value,
                    type=var_type,
                    source_file="godot/scripts/core/game_state.gd",
                    line_number=line_num,
                    comment=comment.strip() if comment else None,
                )

        return constants

    def extract_action_costs(self) -> Dict[str, Dict[str, Any]]:
        """Extract action costs and effects from actions.gd"""
        actions_file = self.godot_root / "scripts" / "core" / "actions.gd"

        if not actions_file.exists():
            return {}

        # TODO: Parse action definitions
        # For now, return empty dict - will implement full parser
        return {}

    def extract_constants(self, file_path: Path, pattern: str) -> Dict[str, GameConstant]:
        """Extract constants matching a pattern from a GDScript file."""
        constants = {}

        if not file_path.exists():
            return constants

        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        const_pattern = re.compile(r"^const\s+(\w+):\s*(\w+)?\s*=\s*([^#]+)(?:#\s*(.+))?")

        for line_num, line in enumerate(lines, 1):
            match = const_pattern.match(line.strip())
            if match:
                const_name, const_type, value, comment = match.groups()

                if pattern and not re.search(pattern, const_name):
                    continue

                # Clean up value
                value = value.strip()

                # Parse numeric values
                parsed_value = value
                try:
                    if "." in value:
                        parsed_value = float(value)
                    elif value.isdigit():
                        parsed_value = int(value)
                except ValueError:
                    pass

                relative_path = file_path.relative_to(self.repo_root)
                constants[const_name] = GameConstant(
                    name=const_name,
                    value=parsed_value,
                    type=const_type or "unknown",
                    source_file=str(relative_path).replace("\\", "/"),
                    line_number=line_num,
                    comment=comment.strip() if comment else None,
                )

        return constants


class MechanicsDocGenerator:
    """Generate mechanics documentation with embedded game data."""

    def __init__(self, repo_root: Path, output_dir: Path):
        self.repo_root = repo_root
        self.output_dir = output_dir
        self.extractor = GameDataExtractor(repo_root)
        self.data_cache_file = output_dir / ".mechanics_data.json"

    def extract_all_data(self) -> Dict[str, MechanicData]:
        """Extract all game data for mechanics."""
        game_state_constants = self.extractor.extract_game_state_defaults()

        # Build mechanic data
        mechanics = {
            "reputation": MechanicData(
                name="reputation",
                constants={k: v for k, v in game_state_constants.items() if k == "reputation"},
                description="Reputation & Public Opinion System",
                related_files=[
                    "godot/scripts/core/game_state.gd",
                    "godot/scripts/core/events.gd",
                    "godot/scripts/core/actions.gd",
                ],
                last_updated=datetime.now().isoformat(),
            ),
            "resources": MechanicData(
                name="resources",
                constants={
                    k: v
                    for k, v in game_state_constants.items()
                    if k
                    in [
                        "money",
                        "compute",
                        "research",
                        "papers",
                        "doom",
                        "action_points",
                        "stationery",
                    ]
                },
                description="Core Game Resources",
                related_files=[
                    "godot/scripts/core/game_state.gd",
                    "godot/scripts/core/turn_manager.gd",
                ],
                last_updated=datetime.now().isoformat(),
            ),
            "personnel": MechanicData(
                name="personnel",
                constants={
                    k: v
                    for k, v in game_state_constants.items()
                    if k
                    in [
                        "safety_researchers",
                        "capability_researchers",
                        "compute_engineers",
                        "managers",
                    ]
                },
                description="Personnel & Hiring System",
                related_files=[
                    "godot/scripts/core/game_state.gd",
                    "godot/scripts/core/researcher.gd",
                ],
                last_updated=datetime.now().isoformat(),
            ),
        }

        return mechanics

    def save_data_cache(self, mechanics: Dict[str, MechanicData]):
        """Save extracted data to JSON cache."""
        data = {
            name: {
                "name": mech.name,
                "description": mech.description,
                "constants": {k: asdict(v) for k, v in mech.constants.items()},
                "related_files": mech.related_files,
                "last_updated": mech.last_updated,
            }
            for name, mech in mechanics.items()
        }

        self.data_cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_data_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached mechanic data."""
        if not self.data_cache_file.exists():
            return None

        return json.loads(self.data_cache_file.read_text(encoding="utf-8"))

    def generate_data_table(self, constants: Dict[str, GameConstant]) -> str:
        """Generate markdown table from constants."""
        if not constants:
            return "*No game data extracted yet.*\n"

        lines = [
            "| Variable | Default Value | Type | Source |",
            "|----------|---------------|------|--------|",
        ]

        for const in constants.values():
            source_link = f"[{const.source_file}:{const.line_number}](../../{const.source_file}#L{const.line_number})"
            value_str = f"`{const.value}`"
            lines.append(f"| `{const.name}` | {value_str} | {const.type} | {source_link} |")

        return "\n".join(lines) + "\n"

    def update_reputation_doc(self, mechanic_data: MechanicData):
        """Update reputation.md with current game data."""
        doc_file = self.output_dir / "reputation.md"

        if not doc_file.exists():
            print(f"Warning: {doc_file} not found, skipping update")
            return

        content = doc_file.read_text(encoding="utf-8")

        # Generate data table
        data_table = self.generate_data_table(mechanic_data.constants)

        # Replace or insert game data section
        game_data_section = f"""## Game Data (Auto-Generated)

> **Note**: This section is automatically generated from the game code. Do not edit manually.
> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{data_table}

*These values are extracted from the game source code and updated automatically.*

---

"""

        # Insert after "Current Mechanics" section
        current_mechanics_pattern = r"(## Current Mechanics.*?\n\n)"

        if re.search(current_mechanics_pattern, content, re.DOTALL):
            # Replace existing game data section if present
            content = re.sub(
                r"## Game Data \(Auto-Generated\).*?---\n\n", "", content, flags=re.DOTALL
            )
            # Insert new section
            content = re.sub(
                current_mechanics_pattern, r"\1" + game_data_section, content, flags=re.DOTALL
            )

        doc_file.write_text(content, encoding="utf-8")
        print(f"[OK] Updated {doc_file.relative_to(self.repo_root)}")

    def generate_all(self):
        """Generate all mechanics documentation."""
        print("=== Mechanics Documentation Generator ===")
        print(f"Repository: {self.repo_root}")
        print(f"Output: {self.output_dir}")
        print()

        # Extract game data
        print("Extracting game data...")
        mechanics = self.extract_all_data()

        # Save cache
        self.save_data_cache(mechanics)
        print(f"[OK] Saved data cache: {self.data_cache_file.relative_to(self.repo_root)}")

        # Update documentation
        print("\nUpdating documentation files...")
        self.update_reputation_doc(mechanics["reputation"])

        print("\n[OK] Generation complete")

    def check_sync(self) -> bool:
        """Check if docs are in sync with game code."""
        print("Checking documentation sync status...")

        # Extract current data
        current_mechanics = self.extract_all_data()

        # Load cached data
        cached_data = self.load_data_cache()

        if not cached_data:
            print("[WARN] No cache found - run without --check to generate")
            return False

        # Compare
        out_of_sync = []
        for name, current in current_mechanics.items():
            if name not in cached_data:
                out_of_sync.append(f"{name}: Not in cache")
                continue

            cached = cached_data[name]

            # Compare constants
            for const_name, const in current.constants.items():
                if const_name not in cached["constants"]:
                    out_of_sync.append(f"{name}.{const_name}: New constant")
                elif cached["constants"][const_name]["value"] != const.value:
                    old_val = cached["constants"][const_name]["value"]
                    out_of_sync.append(
                        f"{name}.{const_name}: Value changed ({old_val} → {const.value})"
                    )

        if out_of_sync:
            print("\n[WARN] Documentation is OUT OF SYNC:")
            for issue in out_of_sync:
                print(f"  - {issue}")
            print("\nRun without --check to update documentation.")
            return False

        print("[OK] Documentation is in sync with game code")
        return True


def main():
    parser = argparse.ArgumentParser(description="Generate mechanics documentation from game code")
    parser.add_argument(
        "--check", action="store_true", help="Check if docs are in sync (don't update)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/mechanics"),
        help="Output directory for mechanics docs",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / args.output

    generator = MechanicsDocGenerator(repo_root, output_dir)

    if args.check:
        in_sync = generator.check_sync()
        exit(0 if in_sync else 1)
    else:
        generator.generate_all()


if __name__ == "__main__":
    main()
