# !/usr/bin/env python3
"""
Historical Data Validation Script

Validates all historical timeline data before builds/releases.
Ensures data integrity and game compatibility.

Usage:
    python scripts/validate_historical_data.py
    python scripts/validate_historical_data.py --verbose
    python scripts/validate_historical_data.py --fix

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse
try:
    import jsonschema
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# Cache for loaded schemas
_SCHEMA_CACHE: Dict[str, Dict] = {}


def load_schema(schema_name: str) -> Optional[Dict]:
    """Load and cache a JSON Schema file"""
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]

    schema_path = Path("shared/schemas") / f"{schema_name}.schema.json"
    if not schema_path.exists():
        return None

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        _SCHEMA_CACHE[schema_name] = schema
        return schema
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Failed to load schema {schema_name}: {e}{Colors.RESET}")
        return None


def validate_with_schema(data: Dict, schema_name: str, file_path: Path) -> List[str]:
    """Validate data against a JSON Schema"""
    errors = []

    if not HAS_JSONSCHEMA:
        errors.append(f"{file_path.name}: jsonschema library not installed, skipping schema validation")
        return errors

    schema = load_schema(schema_name)
    if not schema:
        errors.append(f"{file_path.name}: Schema {schema_name} not found")
        return errors

    try:
        validator = Draft7Validator(schema)
        validation_errors = list(validator.iter_errors(data))

        for error in validation_errors:
            # Build path to the error
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(
                f"{file_path.name}/{path}: {error.message}"
            )
    except Exception as e:
        errors.append(f"{file_path.name}: Schema validation failed: {e}")

    return errors


def validate_json_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate that a file contains valid JSON"""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, []
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        return False, errors


def validate_timeline_event(event: Dict, year_file: Path) -> List[str]:
    """Validate a single timeline event"""
    errors = []
    event_id = event.get('event_id', 'unknown')

    # Required fields
    required_fields = [
        'event_id', 'trigger_date', 'type', 'name', 'description',
        'game_effect', 'historical_fact', 'source'
    ]

    for field in required_fields:
        if field not in event:
            errors.append(
                f"{year_file.name}/{event_id}: Missing required field '{field}'"
            )

    # Validate date format
    if 'trigger_date' in event:
        try:
            datetime.fromisoformat(event['trigger_date'])
        except ValueError:
            errors.append(
                f"{year_file.name}/{event_id}: Invalid date format "
                f"'{event['trigger_date']}' (expected YYYY-MM-DD)"
            )

    # Validate event type
    valid_types = [
        'paper_publication', 'conference', 'org_founding',
        'funding', 'capability', 'governance'
    ]
    if event.get('type') not in valid_types:
        errors.append(
            f"{year_file.name}/{event_id}: Invalid type '{event.get('type')}' "
            f"(must be one of {valid_types})"
        )

    # Validate game_effect structure
    if 'game_effect' in event:
        effect = event['game_effect']
        if not isinstance(effect, dict):
            errors.append(
                f"{year_file.name}/{event_id}: 'game_effect' must be a dictionary"
            )

    # Validate source URL
    if 'source' in event and not event['source'].startswith('http'):
        errors.append(
            f"{year_file.name}/{event_id}: 'source' must be a valid URL"
        )

    return errors


def validate_timeline_file(file_path: Path) -> List[str]:
    """Validate a timeline year file"""
    errors = []

    # First check if it's valid JSON
    valid_json, json_errors = validate_json_file(file_path)
    if not valid_json:
        return json_errors

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate top-level structure
    if 'year' not in data:
        errors.append(f"{file_path.name}: Missing 'year' field")

    if 'default_timeline_events' not in data:
        errors.append(f"{file_path.name}: Missing 'default_timeline_events'")

    # Validate year matches filename
    if 'year' in data:
        expected_year = int(file_path.stem)
        if data['year'] != expected_year:
            errors.append(
                f"{file_path.name}: Year mismatch "
                f"(file: {expected_year}, data: {data['year']})"
            )

    # Validate each event
    for event in data.get('default_timeline_events', []):
        errors.extend(validate_timeline_event(event, file_path))

    # Validate background events if present
    if 'background_events' in data:
        for event in data['background_events']:
            if 'event_id' not in event or 'date' not in event:
                errors.append(
                    f"{file_path.name}: Background event missing id or date"
                )

    return errors


def validate_researcher_file(file_path: Path) -> List[str]:
    """Validate researcher profile file"""
    errors = []

    # First check if it's valid JSON
    valid_json, json_errors = validate_json_file(file_path)
    if not valid_json:
        return json_errors

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Use JSON Schema validation if available
    schema_errors = validate_with_schema(data, 'researcher', file_path)
    if schema_errors:
        errors.extend(schema_errors)
        # If schema validation passed, skip legacy checks
        if not any("not found" in e or "not installed" in e for e in schema_errors):
            return errors

    # Legacy validation (fallback if schema unavailable)
    if 'researchers' not in data:
        errors.append(f"{file_path.name}: Missing 'researchers' array")
        return errors

    for researcher in data.get('researchers', []):
        researcher_id = researcher.get('id', 'unknown')

        # Required fields
        required = ['id', 'name', 'specialization']
        for field in required:
            if field not in researcher:
                errors.append(
                    f"{file_path.name}/{researcher_id}: Missing required field '{field}'"
                )

        # Validate specialization
        valid_specs = ['safety', 'capabilities', 'interpretability', 'alignment', 'governance', 'policy', 'theory']
        if researcher.get('specialization') not in valid_specs:
            errors.append(
                f"{file_path.name}/{researcher_id}: Invalid specialization "
                f"(must be one of {valid_specs})"
            )

    return errors


def validate_organization_file(file_path: Path) -> List[str]:
    """Validate organization file"""
    errors = []

    # First check if it's valid JSON
    valid_json, json_errors = validate_json_file(file_path)
    if not valid_json:
        return json_errors

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Use JSON Schema validation if available
    schema_errors = validate_with_schema(data, 'organization', file_path)
    if schema_errors:
        errors.extend(schema_errors)
        # If schema validation passed, skip legacy checks
        if not any("not found" in e or "not installed" in e for e in schema_errors):
            return errors

    # Legacy validation (fallback if schema unavailable)
    if 'organizations' not in data:
        errors.append(f"{file_path.name}: Missing 'organizations' array")
        return errors

    for org in data.get('organizations', []):
        org_id = org.get('id', 'unknown')

        # Required fields
        required = ['id', 'name', 'type', 'description']
        for field in required:
            if field not in org:
                errors.append(
                    f"{file_path.name}/{org_id}: Missing required field '{field}'"
                )

        # Validate type
        valid_types = ['safety', 'frontier', 'governance', 'academic', 'nonprofit']
        if org.get('type') not in valid_types:
            errors.append(
                f"{file_path.name}/{org_id}: Invalid type "
                f"(must be one of {valid_types})"
            )

    return errors


def run_validation(verbose: bool = False) -> Tuple[int, int, List[str]]:
    """
    Run all validation checks

    Returns:
        (total_files, files_with_errors, all_errors)
    """
    all_errors = []
    total_files = 0
    files_with_errors = 0

    # Validate timeline events
    print(f"{Colors.BLUE}Validating timeline events...{Colors.RESET}")
    timeline_dirs = [
        Path("shared/data/historical_timeline"),
        Path("godot/data/historical_timeline")
    ]

    for timeline_dir in timeline_dirs:
        if not timeline_dir.exists():
            if verbose:
                print(f"  {Colors.YELLOW}Skipping {timeline_dir} (not found){Colors.RESET}")
            continue

        for year_file in sorted(timeline_dir.glob("*.json")):
            total_files += 1
            errors = validate_timeline_file(year_file)
            if errors:
                files_with_errors += 1
                all_errors.extend(errors)
                if verbose:
                    print(f"  {Colors.RED}[X] {year_file.name}: {len(errors)} error(s){Colors.RESET}")
            else:
                if verbose:
                    print(f"  {Colors.GREEN}[OK] {year_file.name}{Colors.RESET}")

    # Validate researchers
    print(f"{Colors.BLUE}Validating researcher profiles...{Colors.RESET}")
    researcher_dirs = [
        Path("shared/data/researchers"),
        Path("godot/data/researchers")
    ]

    for researcher_dir in researcher_dirs:
        if not researcher_dir.exists():
            if verbose:
                print(f"  {Colors.YELLOW}Skipping {researcher_dir} (not found){Colors.RESET}")
            continue

        for file in sorted(researcher_dir.glob("*.json")):
            total_files += 1
            errors = validate_researcher_file(file)
            if errors:
                files_with_errors += 1
                all_errors.extend(errors)
                if verbose:
                    print(f"  {Colors.RED}[X] {file.name}: {len(errors)} error(s){Colors.RESET}")
            else:
                if verbose:
                    print(f"  {Colors.GREEN}[OK] {file.name}{Colors.RESET}")

    # Validate organizations
    print(f"{Colors.BLUE}Validating organizations...{Colors.RESET}")
    org_dirs = [
        Path("shared/data/organizations"),
        Path("godot/data/organizations")
    ]

    for org_dir in org_dirs:
        if not org_dir.exists():
            if verbose:
                print(f"  {Colors.YELLOW}Skipping {org_dir} (not found){Colors.RESET}")
            continue

        for file in sorted(org_dir.glob("*.json")):
            total_files += 1
            errors = validate_organization_file(file)
            if errors:
                files_with_errors += 1
                all_errors.extend(errors)
                if verbose:
                    print(f"  {Colors.RED}[X] {file.name}: {len(errors)} error(s){Colors.RESET}")
            else:
                if verbose:
                    print(f"  {Colors.GREEN}[OK] {file.name}{Colors.RESET}")

    return total_files, files_with_errors, all_errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate historical data for P(Doom) game'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed validation output'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix common issues (future feature)'
    )
    args = parser.parse_args()

    print(f"{Colors.BOLD}=== P(Doom) Historical Data Validation ==={Colors.RESET}\n")

    # Check schema validation availability
    if HAS_JSONSCHEMA:
        print(f"{Colors.GREEN}JSON Schema validation: ENABLED{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}JSON Schema validation: DISABLED (install jsonschema: pip install jsonschema){Colors.RESET}")
    print()

    total_files, files_with_errors, all_errors = run_validation(args.verbose)

    print()

    if not all_errors:
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] All historical data validated successfully{Colors.RESET}")
        print(f"   Files checked: {total_files}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}[FAILED] VALIDATION FAILED{Colors.RESET}")
        print(f"   Files checked: {total_files}")
        print(f"   Files with errors: {files_with_errors}")
        print(f"   Total errors: {len(all_errors)}\n")

        print(f"{Colors.RED}Errors:{Colors.RESET}")
        for error in all_errors:
            print(f"  - {error}")

        print()
        print(f"{Colors.YELLOW}Please fix these errors before building/releasing.{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
